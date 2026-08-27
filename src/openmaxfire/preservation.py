"""Read-only PIC16F877A dump inspection and comparison.

This module parses programmer-exported Intel HEX files. It never communicates
with a PICkit and contains no erase or program operation.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Sequence

from .firmware import FirmwareImage


PIC16F877A_PROGRAM_WORDS = 0x2000
PIC16F877A_EEPROM_BYTES = 0x100
PIC16F877A_DEVICE_ID_MASK = 0x3FF0
PIC16F877A_DEVICE_ID_VALUE = 0x0E20


class ProtectionState(str, Enum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    UNKNOWN = "unknown"


def _hash_words(values: dict[int, int], count: int, erased: int) -> str:
    digest = hashlib.sha256()
    for address in range(count):
        digest.update(values.get(address, erased).to_bytes(2, "little"))
    return digest.hexdigest()


def _hash_bytes(values: dict[int, int], count: int, erased: int) -> str:
    digest = hashlib.sha256()
    digest.update(bytes(values.get(address, erased) for address in range(count)))
    return digest.hexdigest()


def _protection_state(configuration_word: int | None, mask: int) -> ProtectionState:
    if configuration_word is None:
        return ProtectionState.UNKNOWN
    return ProtectionState.DISABLED if configuration_word & mask else ProtectionState.ENABLED


@dataclass(frozen=True, slots=True)
class Pic16f877aDumpInspection:
    filename: str
    file_sha256: str
    program_sha256: str
    eeprom_sha256: str
    user_ids_sha256: str
    configuration_sha256: str
    preservation_sha256: str
    program_words_present: int
    eeprom_bytes_present: int
    user_id_words_present: int
    configuration_word: int | None
    device_id_word: int | None
    device_id_matches: bool | None
    program_code_protection: ProtectionState
    eeprom_code_protection: ProtectionState
    blockers: tuple[str, ...]

    @property
    def safe_read(self) -> bool:
        return not self.blockers

    def to_dict(self) -> dict[str, object]:
        return {
            "filename": self.filename,
            "file_sha256": self.file_sha256,
            "normalized_sections": {
                "program_sha256": self.program_sha256,
                "eeprom_sha256": self.eeprom_sha256,
                "user_ids_sha256": self.user_ids_sha256,
                "configuration_sha256": self.configuration_sha256,
                "preservation_sha256": self.preservation_sha256,
            },
            "coverage": {
                "program_words_present": self.program_words_present,
                "program_words_total": PIC16F877A_PROGRAM_WORDS,
                "eeprom_bytes_present": self.eeprom_bytes_present,
                "eeprom_bytes_total": PIC16F877A_EEPROM_BYTES,
                "user_id_words_present": self.user_id_words_present,
                "user_id_words_total": 4,
            },
            "configuration_word": (
                f"0x{self.configuration_word:04X}"
                if self.configuration_word is not None
                else None
            ),
            "device_id_word": (
                f"0x{self.device_id_word:04X}"
                if self.device_id_word is not None
                else None
            ),
            "device_id_matches_pic16f877a": self.device_id_matches,
            "program_code_protection": self.program_code_protection.value,
            "eeprom_code_protection": self.eeprom_code_protection.value,
            "safe_read": self.safe_read,
            "blockers": list(self.blockers),
        }


def inspect_pic16f877a_dump(
    source: FirmwareImage | str | Path,
) -> Pic16f877aDumpInspection:
    """Inspect one exported dump and fail closed on protection uncertainty."""

    image = source if isinstance(source, FirmwareImage) else FirmwareImage.load(source)
    program = dict(image.program_words)
    eeprom = dict(image.eeprom_words)
    user_ids = dict(image.user_id_words)
    program_hash = _hash_words(program, PIC16F877A_PROGRAM_WORDS, 0x3FFF)
    eeprom_hash = _hash_bytes(eeprom, PIC16F877A_EEPROM_BYTES, 0xFF)
    normalized_user_ids = {
        address - 0x2000: value for address, value in user_ids.items()
    }
    user_hash = _hash_words(normalized_user_ids, 4, 0x3FFF)
    configuration_payload = (
        b"missing"
        if image.configuration_word is None
        else image.configuration_word.to_bytes(2, "little")
    )
    configuration_hash = hashlib.sha256(configuration_payload).hexdigest()
    preservation_hash = hashlib.sha256(
        bytes.fromhex(program_hash)
        + bytes.fromhex(eeprom_hash)
        + bytes.fromhex(user_hash)
        + bytes.fromhex(configuration_hash)
    ).hexdigest()

    program_protection = _protection_state(image.configuration_word, 0x2000)
    eeprom_protection = _protection_state(image.configuration_word, 0x0100)
    device_matches = (
        None
        if image.device_id_word is None
        else (image.device_id_word & PIC16F877A_DEVICE_ID_MASK)
        == PIC16F877A_DEVICE_ID_VALUE
    )
    blockers: list[str] = []
    if image.configuration_word is None:
        blockers.append(
            "configuration word is missing; code-protection state cannot be established"
        )
    if program_protection is ProtectionState.ENABLED:
        blockers.append(
            "program-memory code protection is enabled; protected reads are not a backup"
        )
    if eeprom_protection is ProtectionState.ENABLED:
        blockers.append(
            "data-EEPROM code protection is enabled; protected reads are not a backup"
        )
    if not program:
        blockers.append("dump contains no program-memory words")
    if not eeprom:
        blockers.append("dump contains no data-EEPROM bytes")
    if device_matches is False:
        blockers.append("device ID does not identify a PIC16F877A")

    return Pic16f877aDumpInspection(
        filename=image.filename,
        file_sha256=image.sha256,
        program_sha256=program_hash,
        eeprom_sha256=eeprom_hash,
        user_ids_sha256=user_hash,
        configuration_sha256=configuration_hash,
        preservation_sha256=preservation_hash,
        program_words_present=len(program),
        eeprom_bytes_present=len(eeprom),
        user_id_words_present=len(user_ids),
        configuration_word=image.configuration_word,
        device_id_word=image.device_id_word,
        device_id_matches=device_matches,
        program_code_protection=program_protection,
        eeprom_code_protection=eeprom_protection,
        blockers=tuple(blockers),
    )


@dataclass(frozen=True, slots=True)
class Pic16f877aDumpSetReport:
    purpose: str
    inspections: tuple[Pic16f877aDumpInspection, ...]
    program_matches: bool
    eeprom_matches: bool
    user_ids_match: bool
    configuration_matches: bool
    preservation_matches: bool
    raw_files_identical: bool
    blockers: tuple[str, ...]

    @property
    def authenticated(self) -> bool:
        return len(self.inspections) >= 2 and self.preservation_matches and not self.blockers

    @property
    def safe_to_continue(self) -> bool:
        return self.authenticated

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.pickit-preservation.v1",
            "purpose": self.purpose,
            "dump_count": len(self.inspections),
            "sections_match": {
                "program": self.program_matches,
                "eeprom": self.eeprom_matches,
                "user_ids": self.user_ids_match,
                "configuration": self.configuration_matches,
                "complete_preservation_set": self.preservation_matches,
                "raw_files_identical": self.raw_files_identical,
            },
            "authenticated": self.authenticated,
            "safe_to_continue": self.safe_to_continue,
            "blockers": list(self.blockers),
            "dumps": [inspection.to_dict() for inspection in self.inspections],
            "safety_boundary": (
                "offline HEX inspection only; this report cannot read, erase, or program a device"
            ),
        }


def compare_pic16f877a_dumps(
    sources: Sequence[FirmwareImage | str | Path],
    *,
    purpose: str = "repeated-dump",
) -> Pic16f877aDumpSetReport:
    """Compare two or more reads by normalized memory section and raw hash."""

    if len(sources) < 2:
        raise ValueError("at least two independently exported dumps are required")
    if purpose not in ("repeated-dump", "clone-compare"):
        raise ValueError("purpose must be repeated-dump or clone-compare")
    inspections = tuple(inspect_pic16f877a_dump(source) for source in sources)

    def matches(attribute: str) -> bool:
        return len({getattr(item, attribute) for item in inspections}) == 1

    program_matches = matches("program_sha256")
    eeprom_matches = matches("eeprom_sha256")
    user_ids_match = matches("user_ids_sha256")
    configuration_matches = matches("configuration_sha256")
    preservation_matches = matches("preservation_sha256")
    raw_files_identical = matches("file_sha256")
    blockers = [
        f"{item.filename}: {blocker}"
        for item in inspections
        for blocker in item.blockers
    ]
    for matches_section, name in (
        (program_matches, "program memory"),
        (eeprom_matches, "data EEPROM"),
        (user_ids_match, "User IDs"),
        (configuration_matches, "configuration word"),
    ):
        if not matches_section:
            blockers.append(f"{name} differs between dumps")
    return Pic16f877aDumpSetReport(
        purpose=purpose,
        inspections=inspections,
        program_matches=program_matches,
        eeprom_matches=eeprom_matches,
        user_ids_match=user_ids_match,
        configuration_matches=configuration_matches,
        preservation_matches=preservation_matches,
        raw_files_identical=raw_files_identical,
        blockers=tuple(blockers),
    )


__all__ = [
    "PIC16F877A_DEVICE_ID_MASK",
    "PIC16F877A_DEVICE_ID_VALUE",
    "PIC16F877A_EEPROM_BYTES",
    "PIC16F877A_PROGRAM_WORDS",
    "Pic16f877aDumpInspection",
    "Pic16f877aDumpSetReport",
    "ProtectionState",
    "compare_pic16f877a_dumps",
    "inspect_pic16f877a_dump",
]
