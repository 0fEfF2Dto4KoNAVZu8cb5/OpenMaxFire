"""Deterministic construction of complete PICkit images from J3 updates.

This module performs no hardware I/O.  It applies the reconstructed resident-
loader address rules to a complete PICkit base image and emits a complete,
derived Intel HEX image representing the immediate post-download state.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Sequence

from .firmware import (
    FirmwareImage,
    FirmwareImageError,
    FirmwareVariant,
    loader_effective_word_address,
)


DERIVED_PICKIT_SCHEMA = "openmaxfire.derived-pickit.v1"
PIC16F877A_PROGRAM_WORDS = 0x2000
PIC16F877A_EEPROM_BYTES = 0x100
RESET_TRAMPOLINE_ADDRESSES = frozenset(range(0x1E84, 0x1E88))


def _intel_hex_record(address: int, record_type: int, payload: bytes = b"") -> str:
    body = bytes(
        (
            len(payload),
            (address >> 8) & 0xFF,
            address & 0xFF,
            record_type,
        )
    ) + payload
    checksum = (-sum(body)) & 0xFF
    return ":" + (body + bytes((checksum,))).hex().upper()


def serialize_intel_hex(
    memory: Mapping[int, int],
    *,
    record_size: int = 16,
    start_segment: int | None = None,
    start_linear: int | None = None,
) -> str:
    """Serialize sparse byte-addressed memory as deterministic Intel HEX."""

    if (
        isinstance(record_size, bool)
        or not isinstance(record_size, int)
        or not 1 <= record_size <= 0xFF
    ):
        raise ValueError("record_size must be between 1 and 255")
    normalized: dict[int, int] = {}
    for address, value in memory.items():
        if (
            isinstance(address, bool)
            or not isinstance(address, int)
            or not 0 <= address <= 0xFFFFFFFF
        ):
            raise ValueError("Intel HEX addresses must be 32-bit unsigned integers")
        if (
            isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= 0xFF
        ):
            raise ValueError("Intel HEX memory values must be bytes")
        normalized[address] = value

    lines: list[str] = []
    addresses = sorted(normalized)
    current_upper: int | None = None
    index = 0
    while index < len(addresses):
        first = addresses[index]
        upper = first >> 16
        if upper != current_upper:
            lines.append(_intel_hex_record(0, 0x04, upper.to_bytes(2, "big")))
            current_upper = upper
        selected = [first]
        index += 1
        while (
            index < len(addresses)
            and len(selected) < record_size
            and addresses[index] == selected[-1] + 1
            and addresses[index] >> 16 == upper
        ):
            selected.append(addresses[index])
            index += 1
        payload = bytes(normalized[address] for address in selected)
        lines.append(_intel_hex_record(first & 0xFFFF, 0x00, payload))

    if start_segment is not None:
        if not 0 <= start_segment <= 0xFFFFFFFF:
            raise ValueError("start_segment must be a 32-bit unsigned integer")
        lines.append(_intel_hex_record(0, 0x03, start_segment.to_bytes(4, "big")))
    if start_linear is not None:
        if not 0 <= start_linear <= 0xFFFFFFFF:
            raise ValueError("start_linear must be a 32-bit unsigned integer")
        lines.append(_intel_hex_record(0, 0x05, start_linear.to_bytes(4, "big")))
    lines.append(_intel_hex_record(0, 0x01))
    return "\n".join(lines) + "\n"


def _words_sha256(words: Mapping[int, int], addresses: Sequence[int]) -> str:
    payload = bytearray()
    for address in addresses:
        value = words[address]
        payload.extend((value & 0xFF, (value >> 8) & 0xFF))
    return hashlib.sha256(payload).hexdigest()


@dataclass(frozen=True, slots=True)
class PickitOverlayStep:
    """One Downloader image applied through resident-loader semantics."""

    filename: str
    sha256: str
    firmware_version: str
    source_program_words: int
    applied_words: int
    changed_words: int
    unchanged_words: int
    relocated_words: int
    protected_skipped_words: int
    ignored_user_id_words: int
    ignored_configuration_word: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "sha256": self.sha256,
            "firmware_version": self.firmware_version,
            "source_program_words": self.source_program_words,
            "applied_words": self.applied_words,
            "changed_words": self.changed_words,
            "unchanged_words": self.unchanged_words,
            "relocated_words": self.relocated_words,
            "protected_skipped_words": self.protected_skipped_words,
            "ignored_user_id_words": self.ignored_user_id_words,
            "ignored_configuration_word": self.ignored_configuration_word,
        }


@dataclass(frozen=True, slots=True)
class DerivedPickitImage:
    """Complete predicted post-J3/pre-calibration PIC memory image."""

    base: FirmwareImage
    downloaders: tuple[FirmwareImage, ...]
    memory: Mapping[int, int]
    steps: tuple[PickitOverlayStep, ...]

    @property
    def firmware_version(self) -> str:
        version = self.downloaders[-1].firmware_version
        assert version is not None
        return version

    def to_intel_hex(self) -> str:
        return serialize_intel_hex(
            self.memory,
            start_segment=self.base.intel_hex.start_segment,
            start_linear=self.base.intel_hex.start_linear,
        )

    def to_firmware_image(self, *, filename: str) -> FirmwareImage:
        return FirmwareImage.parse(
            self.to_intel_hex(),
            filename=filename,
            firmware_version=self.firmware_version,
            variant=FirmwareVariant.PICKIT,
        )

    def to_manifest(self, *, output_filename: str) -> dict[str, object]:
        payload = self.to_intel_hex().encode("ascii")
        final = self.to_firmware_image(filename=output_filename)
        base_program = self.base.program_words
        final_program = final.program_words
        immutable_loader = tuple(
            address
            for address in range(0x1E80, 0x2000)
            if address not in RESET_TRAMPOLINE_ADDRESSES
        )
        return {
            "schema": DERIVED_PICKIT_SCHEMA,
            "classification": "derived_expected_post_j3_pre_calibration_pickit",
            "vendor_supplied": False,
            "output": {
                "filename": output_filename,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "size": len(payload),
                "firmware_version": self.firmware_version,
                "program_words": len(final.program_words),
                "configuration_word": f"0x{final.configuration_word:04X}",
                "user_id_words": {
                    f"0x{address:04X}": f"0x{value:04X}"
                    for address, value in final.user_id_words.items()
                },
                "eeprom_bytes": len(final.eeprom_words),
            },
            "base": {
                "filename": self.base.filename,
                "sha256": self.base.sha256,
                "firmware_version": self.base.firmware_version,
            },
            "loader_sequence": [step.to_dict() for step in self.steps],
            "verification": {
                "complete_program_space": set(final.program_words)
                == set(range(PIC16F877A_PROGRAM_WORDS)),
                "physical_reset_vector_preserved": all(
                    final_program[address] == base_program[address]
                    for address in range(4)
                ),
                "resident_loader_excluding_trampoline_preserved": all(
                    final_program[address] == base_program[address]
                    for address in immutable_loader
                ),
                "user_ids_preserved": final.user_id_words
                == self.base.user_id_words,
                "configuration_preserved": final.configuration_word
                == self.base.configuration_word,
                "eeprom_preserved": final.eeprom_words == self.base.eeprom_words,
                "program_words_changed_from_base": sum(
                    final_program[address] != base_program[address]
                    for address in range(PIC16F877A_PROGRAM_WORDS)
                ),
                "resident_loader_sha256_excluding_trampoline": _words_sha256(
                    final_program, immutable_loader
                ),
                "eeprom_sha256": hashlib.sha256(
                    bytes(final.eeprom_words[address] for address in range(0x100))
                ).hexdigest(),
            },
            "calibration_required": self.firmware_version
            != self.base.firmware_version,
            "limitations": [
                "Derived by deterministic loader simulation; not a vendor-supplied PICkit image.",
                "Represents immediate post-download state before Individualize, Format, or calibration changes EEPROM.",
                "Must be validated on a spare PIC/controller and compared with a physical post-J3 PICkit read before production use.",
            ],
        }


def _validate_complete_pickit_base(base: FirmwareImage) -> None:
    if base.variant is not FirmwareVariant.PICKIT:
        raise FirmwareImageError("base image must be identified as a PICkit image")
    if set(base.program_words) != set(range(PIC16F877A_PROGRAM_WORDS)):
        raise FirmwareImageError(
            "base PICkit image must contain all 8,192 program words"
        )
    if set(base.user_id_words) != set(range(0x2000, 0x2004)):
        raise FirmwareImageError("base PICkit image must contain all four User IDs")
    if base.configuration_word is None:
        raise FirmwareImageError("base PICkit image has no configuration word")
    if set(base.eeprom_words) != set(range(PIC16F877A_EEPROM_BYTES)):
        raise FirmwareImageError(
            "base PICkit image must contain all 256 data-EEPROM bytes"
        )


def compose_pickit_image(
    base: FirmwareImage,
    downloaders: Sequence[FirmwareImage],
) -> DerivedPickitImage:
    """Apply known J3 Downloader images over one complete PICkit base.

    The Downloader's configuration and User-ID records are intentionally
    ignored because the resident loader does not apply them.  Images carrying
    EEPROM data are rejected until that separate loader path is modeled and
    qualified.
    """

    _validate_complete_pickit_base(base)
    if not downloaders:
        raise FirmwareImageError("at least one Downloader image is required")

    memory = dict(base.intel_hex.memory)
    current_words = dict(base.program_words)
    steps: list[PickitOverlayStep] = []
    accepted: list[FirmwareImage] = []
    for image in downloaders:
        if image.variant not in (FirmwareVariant.DOWNLOADER, FirmwareVariant.EMBEDDED):
            raise FirmwareImageError(
                f"{image.filename} is not a J3 Downloader/embedded image"
            )
        if image.firmware_version is None:
            raise FirmwareImageError(
                f"{image.filename} has no recognized firmware version"
            )
        if not image.program_words:
            raise FirmwareImageError(f"{image.filename} has no program words")
        if image.eeprom_words:
            raise FirmwareImageError(
                f"{image.filename} contains EEPROM records; composition is blocked"
            )

        applied = 0
        changed = 0
        relocated = 0
        skipped = 0
        for source_address, value in sorted(image.program_words.items()):
            target_address = loader_effective_word_address(source_address)
            if target_address is None:
                skipped += 1
                continue
            applied += 1
            relocated += target_address != source_address
            changed += current_words[target_address] != value
            current_words[target_address] = value
            byte_address = target_address * 2
            memory[byte_address] = value & 0xFF
            memory[byte_address + 1] = (value >> 8) & 0xFF

        steps.append(
            PickitOverlayStep(
                filename=image.filename,
                sha256=image.sha256,
                firmware_version=image.firmware_version,
                source_program_words=len(image.program_words),
                applied_words=applied,
                changed_words=changed,
                unchanged_words=applied - changed,
                relocated_words=relocated,
                protected_skipped_words=skipped,
                ignored_user_id_words=len(image.user_id_words),
                ignored_configuration_word=image.configuration_word is not None,
            )
        )
        accepted.append(image)

    result = DerivedPickitImage(
        base=base,
        downloaders=tuple(accepted),
        memory=MappingProxyType(memory),
        steps=tuple(steps),
    )
    final = result.to_firmware_image(filename="Derived_PICkit.hex")
    if any(final.program_words[address] != base.program_words[address] for address in range(4)):
        raise FirmwareImageError("composition changed the physical reset vector")
    if final.user_id_words != base.user_id_words:
        raise FirmwareImageError("composition changed base User IDs")
    if final.configuration_word != base.configuration_word:
        raise FirmwareImageError("composition changed base configuration word")
    if final.eeprom_words != base.eeprom_words:
        raise FirmwareImageError("composition changed base EEPROM")
    return result
