"""Experimental physical J3 firmware flasher.

This module is intentionally separate from the normal OpenMaxFire API. It
implements the reconstructed Bixby resident-loader protocol for controlled
bench testing on externally recoverable PIC16F877A hardware.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path

from .firmware import (
    FirmwareImage,
    FirmwareImageError,
    FirmwareVariant,
    LOADER_CHECKSUM_ACCEPTED_RESPONSE,
    LOADER_CHECKSUM_REJECTED_RESPONSE,
    LOADER_COMPLETE_REQUEST,
    LOADER_COMPLETE_RESPONSE,
    LOADER_IDENTIFY_REQUEST,
    LOADER_IDENTIFY_RESPONSE,
    LOADER_PROTECTED_START,
    LOADER_WRITE_FAILED_RESPONSE,
    LOADER_WRITE_VERIFIED_RESPONSE,
    ProgramBlock,
    build_program_blocks,
)
from .transport import Transport


class ExperimentalFlasherError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class PhysicalFlasherPolicy:
    identify_attempts: int = 1500
    identify_interval: float = 0.015
    identify_read_timeout: float = 0.010
    timeout_retries: int = 2
    checksum_retries: int = 2
    unexpected_retries: int = 0

    def __post_init__(self) -> None:
        if self.identify_attempts < 1:
            raise ValueError("identify_attempts must be positive")
        if self.identify_interval < 0:
            raise ValueError("identify_interval must be nonnegative")
        if self.identify_read_timeout <= 0:
            raise ValueError("identify_read_timeout must be greater than zero")
        for value in (self.timeout_retries, self.checksum_retries, self.unexpected_retries):
            if value < 0:
                raise ValueError("retry counts must be nonnegative")


@dataclass(frozen=True, slots=True)
class ExchangeEvent:
    event: str
    monotonic_ns: int
    fields: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict[str, object]:
        return {"event": self.event, "monotonic_ns": self.monotonic_ns, **self.fields}


class FlasherEventRecorder:
    def __init__(self, path: str | Path | None):
        self.path = Path(path) if path is not None else None
        self.events: list[ExchangeEvent] = []
        self._stream = None
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._stream = self.path.open("x", encoding="utf-8", newline="\n")

    def record(self, event: str, **fields: object) -> None:
        item = ExchangeEvent(event, time.monotonic_ns(), dict(fields))
        self.events.append(item)
        if self._stream is not None:
            self._stream.write(json.dumps(item.to_dict(), sort_keys=True) + "\n")
            self._stream.flush()

    def close(self) -> None:
        if self._stream is not None and not self._stream.closed:
            self._stream.close()


def validate_j3_image(image: FirmwareImage) -> None:
    if image.variant is FirmwareVariant.PICKIT:
        raise FirmwareImageError("full PICkit images are forbidden on the J3 loader path")
    if image.variant not in (FirmwareVariant.DOWNLOADER, FirmwareVariant.EMBEDDED):
        raise FirmwareImageError("image is not recognized as a J3 Downloader layout")
    if image.target != "PIC16F877A":
        raise FirmwareImageError("firmware target is not PIC16F877A")
    if image.firmware_version not in {"2.06", "2.70", "2.71"}:
        raise FirmwareImageError("only preserved 2.06, 2.70, and 2.71 J3 images are allowed")
    if not image.program_words:
        raise FirmwareImageError("firmware image contains no program words")


def protected_test_block() -> ProgramBlock:
    # Direct targets at/above 0x1E80 are parsed/checksummed but skipped by the
    # resident loader. Two words are used so the frame is structurally normal.
    return ProgramBlock(LOADER_PROTECTED_START, b"\x55\x15\x2A\x2A")


class ExperimentalJ3Flasher:
    def __init__(
        self,
        transport: Transport,
        *,
        policy: PhysicalFlasherPolicy | None = None,
        recorder: FlasherEventRecorder | None = None,
    ):
        self.transport = transport
        self.policy = policy or PhysicalFlasherPolicy()
        self.recorder = recorder or FlasherEventRecorder(None)

    def _tx(self, data: bytes, *, phase: str, **fields: object) -> None:
        self.recorder.record(
            "tx", phase=phase, data_hex=data.hex(" ").upper(), byte_count=len(data), **fields
        )
        self.transport.write(data)

    def _rx(self, *, phase: str, **fields: object) -> bytes:
        data = self.transport.read(1)
        self.recorder.record(
            "rx", phase=phase, data_hex=data.hex(" ").upper(), byte_count=len(data), **fields
        )
        return data

    def _temporary_identify_timeout(self) -> tuple[object | None, float | None]:
        """Apply the short loader-probe timeout when the transport supports it."""

        setter = getattr(self.transport, "set_timeout", None)
        original = getattr(self.transport, "timeout", None)
        if not callable(setter) or not isinstance(original, (int, float)):
            self.recorder.record(
                "identify_timeout_unavailable",
                requested_timeout=self.policy.identify_read_timeout,
            )
            return None, None
        setter(self.policy.identify_read_timeout)
        self.recorder.record(
            "identify_timeout_set",
            previous_timeout=float(original),
            probe_timeout=self.policy.identify_read_timeout,
        )
        return setter, float(original)

    def identify(self) -> int:
        setter, original_timeout = self._temporary_identify_timeout()
        try:
            for attempt in range(1, self.policy.identify_attempts + 1):
                started = time.monotonic()
                self._tx(LOADER_IDENTIFY_REQUEST, phase="identify", attempt=attempt)
                response = self._rx(phase="identify", attempt=attempt)
                if response == LOADER_IDENTIFY_RESPONSE:
                    self.recorder.record("loader_identified", attempt=attempt)
                    return attempt
                elapsed = time.monotonic() - started
                remaining = self.policy.identify_interval - elapsed
                if remaining > 0:
                    time.sleep(remaining)
        finally:
            if setter is not None and original_timeout is not None:
                setter(original_timeout)
                self.recorder.record(
                    "identify_timeout_restored",
                    restored_timeout=original_timeout,
                )
        raise ExperimentalFlasherError("loader did not answer EA with EB")

    def _program_block(self, block: ProgramBlock, *, block_index: int) -> int:
        timeout_count = 0
        checksum_count = 0
        unexpected_count = 0
        attempt = 0
        while True:
            attempt += 1
            self._tx(
                block.frame,
                phase="block",
                block_index=block_index,
                attempt=attempt,
                word_address=f"0x{block.word_address:04X}",
                checksum=f"0x{block.checksum:02X}",
            )
            first = self._rx(
                phase="block_ack1",
                block_index=block_index,
                attempt=attempt,
                word_address=f"0x{block.word_address:04X}",
            )
            if first == LOADER_CHECKSUM_REJECTED_RESPONSE:
                checksum_count += 1
                self.recorder.record(
                    "block_retry",
                    reason="E8_checksum_rejected",
                    block_index=block_index,
                    attempt=attempt,
                    word_address=f"0x{block.word_address:04X}",
                )
                if checksum_count > self.policy.checksum_retries:
                    raise ExperimentalFlasherError(
                        f"block 0x{block.word_address:04X} exceeded E8 retry limit"
                    )
                continue
            if not first:
                timeout_count += 1
                if timeout_count > self.policy.timeout_retries:
                    raise ExperimentalFlasherError(
                        f"block 0x{block.word_address:04X} timed out waiting for E7"
                    )
                continue
            if first != LOADER_CHECKSUM_ACCEPTED_RESPONSE:
                unexpected_count += 1
                if unexpected_count > self.policy.unexpected_retries:
                    raise ExperimentalFlasherError(
                        f"block 0x{block.word_address:04X} unexpected first reply {first.hex().upper()}"
                    )
                continue

            second = self._rx(
                phase="block_ack2",
                block_index=block_index,
                attempt=attempt,
                word_address=f"0x{block.word_address:04X}",
            )
            if second == LOADER_WRITE_VERIFIED_RESPONSE:
                self.recorder.record(
                    "block_complete",
                    block_index=block_index,
                    attempt=attempt,
                    word_address=f"0x{block.word_address:04X}",
                )
                return attempt
            if second == LOADER_WRITE_FAILED_RESPONSE:
                # Deliberately do not imitate BixCheck's broad retry behavior.
                raise ExperimentalFlasherError(
                    f"block 0x{block.word_address:04X} returned E5 write/readback failure; aborting immediately"
                )
            if not second:
                timeout_count += 1
                if timeout_count > self.policy.timeout_retries:
                    raise ExperimentalFlasherError(
                        f"block 0x{block.word_address:04X} timed out waiting for E4/E5"
                    )
                continue
            unexpected_count += 1
            if unexpected_count > self.policy.unexpected_retries:
                raise ExperimentalFlasherError(
                    f"block 0x{block.word_address:04X} unexpected second reply {second.hex().upper()}"
                )

    def complete(self) -> None:
        self._tx(LOADER_COMPLETE_REQUEST, phase="complete")
        response = self._rx(phase="complete")
        if response != LOADER_COMPLETE_RESPONSE:
            raise ExperimentalFlasherError(
                f"loader completion expected E4, received {response.hex().upper() or 'timeout'}"
            )
        self.recorder.record("loader_complete")

    def run_protected_test(self) -> dict[str, object]:
        self.identify()
        block = protected_test_block()
        attempts = self._program_block(block, block_index=0)
        self.complete()
        return {
            "mode": "protected-test",
            "word_address": f"0x{block.word_address:04X}",
            "attempts": attempts,
            "success": True,
            "note": "target is in the resident loader protected skip range; no application Flash word is intentionally changed",
        }

    def flash(self, image: FirmwareImage) -> dict[str, object]:
        validate_j3_image(image)
        blocks = build_program_blocks(image)
        self.recorder.record(
            "flash_start",
            filename=image.filename,
            sha256=image.sha256,
            firmware_version=image.firmware_version,
            block_count=len(blocks),
        )
        self.identify()
        attempts: list[int] = []
        for index, block in enumerate(blocks):
            attempts.append(self._program_block(block, block_index=index))
        self.complete()
        result = {
            "mode": "flash",
            "filename": image.filename,
            "sha256": image.sha256,
            "firmware_version": image.firmware_version,
            "blocks_total": len(blocks),
            "blocks_completed": len(blocks),
            "retries": sum(max(0, value - 1) for value in attempts),
            "success": True,
        }
        self.recorder.record("flash_complete", **result)
        return result


def dry_run_image(image: FirmwareImage) -> dict[str, object]:
    validate_j3_image(image)
    blocks = build_program_blocks(image)
    return {
        "mode": "dry-run",
        "filename": image.filename,
        "sha256": image.sha256,
        "firmware_version": image.firmware_version,
        "variant": image.variant.value,
        "block_count": len(blocks),
        "program_words": sum(len(block.data) // 2 for block in blocks),
        "first_block": blocks[0].to_dict() if blocks else None,
        "last_block": blocks[-1].to_dict() if blocks else None,
    }


__all__ = [
    "ExperimentalFlasherError",
    "ExperimentalJ3Flasher",
    "FlasherEventRecorder",
    "PhysicalFlasherPolicy",
    "dry_run_image",
    "protected_test_block",
    "validate_j3_image",
]
