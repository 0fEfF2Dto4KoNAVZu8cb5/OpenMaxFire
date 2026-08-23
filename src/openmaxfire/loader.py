"""Offline firmware-loader planning and simulator-only execution.

This module models the binary protocol reconstructed from the preserved
BixCheck clients.  It intentionally has no serial-port constructor and never
sends the normal-protocol ``CW0FC4`` bootloader-entry write.  The executor
accepts only :class:`SimulatedLoaderTransport`, keeping physical flashing
unreachable while retry, framing, progress, and failure behavior are tested.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .audit import AuditSpan, AuditTrail
from .errors import CapabilityUnavailableError
from .firmware import (
    LOADER_BLOCK_ACKNOWLEDGEMENTS,
    LOADER_COMPLETE_REQUEST,
    LOADER_COMPLETE_RESPONSE,
    LOADER_IDENTIFY_REQUEST,
    LOADER_IDENTIFY_RESPONSE,
    FirmwareCompatibility,
    FirmwareImage,
    ProgramBlock,
    assess_firmware_compatibility,
    build_program_blocks,
)
from .profiles import ControllerProfile
from .transport import Transport


class LoaderState(str, Enum):
    PLANNED = "planned"
    IDENTIFYING = "identifying"
    PROGRAMMING = "programming"
    COMPLETING = "completing"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True, slots=True)
class LoaderPolicy:
    max_retries: int = 30

    def __post_init__(self) -> None:
        if (
            isinstance(self.max_retries, bool)
            or not isinstance(self.max_retries, int)
            or not 0 <= self.max_retries <= 1000
        ):
            raise ValueError("max_retries must be an integer between 0 and 1000")


@dataclass(frozen=True, slots=True)
class LoaderPlan:
    profile_key: str
    image_filename: str
    image_sha256: str
    firmware_version: str | None
    compatibility: FirmwareCompatibility
    blocks: tuple[ProgramBlock, ...]
    live_executable: bool = False

    @property
    def simulator_executable(self) -> bool:
        return self.compatibility.valid_for_offline_planning and bool(self.blocks)

    @property
    def program_word_count(self) -> int:
        return sum(len(block.data) // 2 for block in self.blocks)

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.loader-plan.v1",
            "profile_key": self.profile_key,
            "image_filename": self.image_filename,
            "image_sha256": self.image_sha256,
            "firmware_version": self.firmware_version,
            "block_count": len(self.blocks),
            "program_word_count": self.program_word_count,
            "simulator_executable": self.simulator_executable,
            "live_executable": self.live_executable,
            "compatibility": self.compatibility.to_dict(),
            "blocks": [block.to_dict() for block in self.blocks],
            "safety_boundary": (
                "offline plan only; bootloader entry and physical serial execution are absent"
            ),
        }


@dataclass(frozen=True, slots=True)
class LoaderBlockReceipt:
    word_address: int
    byte_count: int
    attempts: int
    acknowledged: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "word_address": f"0x{self.word_address:04X}",
            "byte_count": self.byte_count,
            "attempts": self.attempts,
            "acknowledged": self.acknowledged,
        }


@dataclass(frozen=True, slots=True)
class LoaderResult:
    state: LoaderState
    image_sha256: str
    blocks_total: int
    blocks_completed: int
    retries: int
    memory_verified: bool
    block_receipts: tuple[LoaderBlockReceipt, ...]
    message: str
    audit_span: AuditSpan | None = None

    @property
    def successful(self) -> bool:
        return self.state is LoaderState.COMPLETE and self.memory_verified

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.loader-result.v1",
            "state": self.state.value,
            "image_sha256": self.image_sha256,
            "blocks_total": self.blocks_total,
            "blocks_completed": self.blocks_completed,
            "retries": self.retries,
            "memory_verified": self.memory_verified,
            "successful": self.successful,
            "block_receipts": [item.to_dict() for item in self.block_receipts],
            "message": self.message,
            "audit_span": self.audit_span.to_dict() if self.audit_span else None,
            "evidence_boundary": "simulator execution only",
        }


def build_loader_plan(
    image: FirmwareImage,
    profile: ControllerProfile,
    *,
    max_words: int = 16,
) -> LoaderPlan:
    compatibility = assess_firmware_compatibility(image, profile)
    return LoaderPlan(
        profile_key=profile.key,
        image_filename=image.filename,
        image_sha256=image.sha256,
        firmware_version=image.firmware_version,
        compatibility=compatibility,
        blocks=build_program_blocks(image, max_words=max_words),
    )


def _exchange(
    transport: Transport,
    request: bytes,
    expected: tuple[bytes, ...],
    policy: LoaderPolicy,
    audit: AuditTrail | None,
) -> tuple[bool, int]:
    """Return ``(acknowledged, attempts)`` for one retry-bounded exchange."""

    for attempt in range(1, policy.max_retries + 2):
        if audit is not None:
            audit.record("tx", request)
        transport.write(request)
        received: list[bytes] = []
        for _ in expected:
            chunk = transport.read(1)
            if audit is not None:
                audit.record("rx", chunk)
            received.append(chunk)
        if tuple(received) == expected:
            return True, attempt
    return False, policy.max_retries + 1


def execute_loader_plan(
    transport: Transport,
    plan: LoaderPlan,
    *,
    authorize: bool = False,
    policy: LoaderPolicy | None = None,
    audit: AuditTrail | None = None,
) -> LoaderResult:
    """Execute a reconstructed loader plan against the simulator only.

    Passing a serial transport, wrapper, or duck-typed substitute is rejected.
    This hard type gate is intentional and keeps the unvalidated physical
    bootloader workflow outside the public executable surface.
    """

    from .simulator import SimulatedLoaderTransport

    if not authorize:
        raise PermissionError("simulated firmware programming was not authorized")
    if not isinstance(transport, SimulatedLoaderTransport):
        raise CapabilityUnavailableError(
            "physical firmware-loader execution is unvalidated and blocked"
        )
    selected_policy = policy or LoaderPolicy()
    checkpoint = audit.checkpoint() if audit is not None else 0
    if not plan.simulator_executable:
        return LoaderResult(
            LoaderState.BLOCKED,
            plan.image_sha256,
            len(plan.blocks),
            0,
            0,
            False,
            (),
            "; ".join(plan.compatibility.blockers) or "loader plan is not executable",
            audit.span(checkpoint) if audit is not None else None,
        )

    receipts: list[LoaderBlockReceipt] = []
    total_retries = 0
    completed = 0
    state = LoaderState.IDENTIFYING
    try:
        acknowledged, attempts = _exchange(
            transport,
            LOADER_IDENTIFY_REQUEST,
            (LOADER_IDENTIFY_RESPONSE,),
            selected_policy,
            audit,
        )
        total_retries += attempts - 1
        if not acknowledged:
            return _loader_failure(
                plan, completed, total_retries, receipts, "loader identify timed out", audit, checkpoint
            )

        state = LoaderState.PROGRAMMING
        for block in plan.blocks:
            acknowledged, attempts = _exchange(
                transport,
                block.frame,
                LOADER_BLOCK_ACKNOWLEDGEMENTS,
                selected_policy,
                audit,
            )
            total_retries += attempts - 1
            receipts.append(
                LoaderBlockReceipt(
                    block.word_address, len(block.data), attempts, acknowledged
                )
            )
            if not acknowledged:
                return _loader_failure(
                    plan,
                    completed,
                    total_retries,
                    receipts,
                    f"block 0x{block.word_address:04X} acknowledgement failed",
                    audit,
                    checkpoint,
                )
            completed += 1

        state = LoaderState.COMPLETING
        acknowledged, attempts = _exchange(
            transport,
            LOADER_COMPLETE_REQUEST,
            (LOADER_COMPLETE_RESPONSE,),
            selected_policy,
            audit,
        )
        total_retries += attempts - 1
        if not acknowledged:
            return _loader_failure(
                plan, completed, total_retries, receipts, "completion acknowledgement failed", audit, checkpoint
            )
        memory_verified = transport.programmed_words == _words_from_blocks(plan.blocks)
        state = LoaderState.COMPLETE if memory_verified else LoaderState.FAILED
        return LoaderResult(
            state,
            plan.image_sha256,
            len(plan.blocks),
            completed,
            total_retries,
            memory_verified,
            tuple(receipts),
            (
                "simulated loader completed and programmed memory matches the plan"
                if memory_verified
                else "simulated loader completed but programmed memory differs"
            ),
            audit.span(checkpoint) if audit is not None else None,
        )
    except Exception as exc:
        return _loader_failure(
            plan,
            completed,
            total_retries,
            receipts,
            f"{state.value} failed: {exc}",
            audit,
            checkpoint,
        )


def _words_from_blocks(blocks: tuple[ProgramBlock, ...]) -> dict[int, int]:
    words: dict[int, int] = {}
    for block in blocks:
        for offset in range(0, len(block.data), 2):
            words[block.word_address + offset // 2] = (
                block.data[offset] | (block.data[offset + 1] << 8)
            )
    return words


def _loader_failure(
    plan: LoaderPlan,
    completed: int,
    retries: int,
    receipts: list[LoaderBlockReceipt],
    message: str,
    audit: AuditTrail | None,
    checkpoint: int,
) -> LoaderResult:
    return LoaderResult(
        LoaderState.FAILED,
        plan.image_sha256,
        len(plan.blocks),
        completed,
        retries,
        False,
        tuple(receipts),
        message,
        audit.span(checkpoint) if audit is not None else None,
    )


def loader_simulation_supported() -> bool:
    return True


def live_loader_supported() -> bool:
    return False


__all__ = [
    "LoaderBlockReceipt",
    "LoaderPlan",
    "LoaderPolicy",
    "LoaderResult",
    "LoaderState",
    "build_loader_plan",
    "execute_loader_plan",
    "live_loader_supported",
    "loader_simulation_supported",
]
