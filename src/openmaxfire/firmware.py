"""Firmware-image validation and binary loader block construction.

The image and framing APIs are offline only.  The separate loader module can
exercise the reconstructed exchange against a strict simulator, but no live
loader transport or erase/program entry path is exposed.
"""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from types import MappingProxyType
from typing import Mapping

from .profiles import ControllerProfile


class FirmwareImageError(ValueError):
    pass


class FirmwareVariant(str, Enum):
    DOWNLOADER = "downloader"
    PICKIT = "pickit"
    EMBEDDED = "embedded"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class IntelHexImage:
    memory: Mapping[int, int]
    record_counts: Mapping[int, int]
    comments: tuple[str, ...]
    start_segment: int | None = None
    start_linear: int | None = None

    @property
    def words(self) -> Mapping[int, int]:
        words: dict[int, int] = {}
        for address in sorted(self.memory):
            if address & 1:
                continue
            if address + 1 not in self.memory:
                raise FirmwareImageError(
                    f"orphan firmware byte at 0x{address:08X}"
                )
            words[address // 2] = self.memory[address] | (self.memory[address + 1] << 8)
        return MappingProxyType(words)


def parse_intel_hex(text: str | bytes) -> IntelHexImage:
    """Parse Intel HEX with checksums, extended addresses, and overlap checks."""

    if isinstance(text, bytes):
        try:
            source = text.decode("ascii")
        except UnicodeDecodeError as exc:
            raise FirmwareImageError("Intel HEX must be ASCII") from exc
    elif isinstance(text, str):
        source = text
    else:
        raise TypeError("Intel HEX input must be str or bytes")

    memory: dict[int, int] = {}
    counts: Counter[int] = Counter()
    comments: list[str] = []
    base = 0
    eof = False
    start_segment = None
    start_linear = None
    for line_number, original in enumerate(source.splitlines(), 1):
        line = original.strip()
        if not line:
            continue
        if line.startswith((";", "#")):
            comments.append(line[1:].strip())
            continue
        if eof:
            raise FirmwareImageError(f"data appears after EOF on line {line_number}")
        if not line.startswith(":"):
            comments.append(line)
            continue
        try:
            record = bytes.fromhex(line[1:])
        except ValueError as exc:
            raise FirmwareImageError(f"invalid hexadecimal on line {line_number}") from exc
        if len(record) < 5:
            raise FirmwareImageError(f"short Intel HEX record on line {line_number}")
        count = record[0]
        if len(record) != count + 5:
            raise FirmwareImageError(f"record length mismatch on line {line_number}")
        if sum(record) & 0xFF:
            raise FirmwareImageError(f"checksum mismatch on line {line_number}")
        offset = (record[1] << 8) | record[2]
        record_type = record[3]
        payload = record[4 : 4 + count]
        counts[record_type] += 1
        if record_type == 0x00:
            absolute = base + offset
            for index, value in enumerate(payload):
                address = absolute + index
                if address in memory and memory[address] != value:
                    raise FirmwareImageError(
                        f"conflicting byte at 0x{address:08X} on line {line_number}"
                    )
                memory[address] = value
        elif record_type == 0x01:
            if count != 0 or offset != 0:
                raise FirmwareImageError(f"invalid EOF record on line {line_number}")
            eof = True
        elif record_type == 0x02:
            if count != 2:
                raise FirmwareImageError(
                    f"invalid extended-segment record on line {line_number}"
                )
            base = int.from_bytes(payload, "big") << 4
        elif record_type == 0x03:
            if count != 4:
                raise FirmwareImageError(
                    f"invalid start-segment record on line {line_number}"
                )
            start_segment = int.from_bytes(payload, "big")
        elif record_type == 0x04:
            if count != 2:
                raise FirmwareImageError(
                    f"invalid extended-linear record on line {line_number}"
                )
            base = int.from_bytes(payload, "big") << 16
        elif record_type == 0x05:
            if count != 4:
                raise FirmwareImageError(
                    f"invalid start-linear record on line {line_number}"
                )
            start_linear = int.from_bytes(payload, "big")
        else:
            raise FirmwareImageError(
                f"unsupported Intel HEX record type 0x{record_type:02X}"
            )
    if not eof:
        raise FirmwareImageError("Intel HEX image has no EOF record")
    return IntelHexImage(
        memory=MappingProxyType(memory),
        record_counts=MappingProxyType(dict(counts)),
        comments=tuple(comments),
        start_segment=start_segment,
        start_linear=start_linear,
    )


def _metadata_from_name(filename: str) -> tuple[str | None, FirmwareVariant]:
    normalized = filename.casefold()
    version = None
    # Embedded filenames also carry a build date (for example,
    # Bixby_0270_070206.hex). Check the explicit firmware tokens before the
    # shorter 0206 token so a 2007-02-06 date is not misidentified as v2.06.
    for pattern, value in (("0271", "2.71"), ("0270", "2.70"), ("0206", "2.06")):
        if pattern in normalized:
            version = value
            break
    if "pickit" in normalized:
        variant = FirmwareVariant.PICKIT
    elif "downloader" in normalized:
        variant = FirmwareVariant.DOWNLOADER
    elif version is not None:
        variant = FirmwareVariant.EMBEDDED
    else:
        variant = FirmwareVariant.UNKNOWN
    return version, variant


@dataclass(frozen=True, slots=True)
class FirmwareImage:
    filename: str
    sha256: str
    firmware_version: str | None
    variant: FirmwareVariant
    target: str
    intel_hex: IntelHexImage
    program_words: Mapping[int, int]
    user_id_words: Mapping[int, int]
    device_id_word: int | None
    configuration_word: int | None
    eeprom_words: Mapping[int, int]

    @classmethod
    def parse(
        cls,
        text: str | bytes,
        *,
        filename: str = "firmware.hex",
        firmware_version: str | None = None,
        variant: FirmwareVariant | str | None = None,
    ) -> "FirmwareImage":
        raw = text.encode("ascii") if isinstance(text, str) else bytes(text)
        parsed = parse_intel_hex(raw)
        inferred_version, inferred_variant = _metadata_from_name(filename)
        selected_variant = inferred_variant if variant is None else FirmwareVariant(variant)
        words = parsed.words
        program = {address: value for address, value in words.items() if address < 0x2000}
        user_ids = {
            address: words[address] for address in range(0x2000, 0x2004) if address in words
        }
        device_id_word = words.get(0x2006)
        configuration_word = words.get(0x2007)
        eeprom = {
            address - 0x2100: value & 0xFF
            for address, value in words.items()
            if 0x2100 <= address <= 0x21FF
        }
        for address, word in program.items():
            if word > 0x3FFF:
                raise FirmwareImageError(
                    f"program word 0x{address:04X} exceeds PIC14 width"
                )
        return cls(
            filename=filename,
            sha256=hashlib.sha256(raw).hexdigest(),
            firmware_version=firmware_version or inferred_version,
            variant=selected_variant,
            target="PIC16F877A",
            intel_hex=parsed,
            program_words=MappingProxyType(program),
            user_id_words=MappingProxyType(user_ids),
            device_id_word=device_id_word,
            configuration_word=configuration_word,
            eeprom_words=MappingProxyType(eeprom),
        )

    @classmethod
    def load(cls, path: str | Path, **metadata: object) -> "FirmwareImage":
        source = Path(path)
        return cls.parse(source.read_bytes(), filename=source.name, **metadata)

    def to_dict(self) -> dict[str, object]:
        addresses = tuple(self.program_words)
        return {
            "filename": self.filename,
            "sha256": self.sha256,
            "firmware_version": self.firmware_version,
            "variant": self.variant.value,
            "target": self.target,
            "program_words": len(self.program_words),
            "program_word_min": min(addresses) if addresses else None,
            "program_word_max": max(addresses) if addresses else None,
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
            "user_id_words": {
                f"0x{address:04X}": f"0x{value:04X}"
                for address, value in self.user_id_words.items()
            },
            "eeprom_words": len(self.eeprom_words),
        }


@dataclass(frozen=True, slots=True)
class ProgramBlock:
    word_address: int
    data: bytes

    @property
    def checksum(self) -> int:
        return sum(self.data) & 0xFF

    @property
    def frame(self) -> bytes:
        if len(self.data) > 32 or len(self.data) % 2:
            raise FirmwareImageError("loader block data must contain 1-16 PIC words")
        return bytes(
            (
                0xE3,
                (self.word_address >> 8) & 0xFF,
                self.word_address & 0xFF,
                len(self.data),
                self.checksum,
            )
        ) + self.data

    def to_dict(self) -> dict[str, object]:
        return {
            "word_address": f"0x{self.word_address:04X}",
            "byte_count": len(self.data),
            "checksum": f"{self.checksum:02X}",
            "frame_hex": self.frame.hex(" ").upper(),
        }


def build_program_blocks(
    image: FirmwareImage,
    *,
    max_words: int = 16,
) -> tuple[ProgramBlock, ...]:
    """Group consecutive program words into reconstructed E3 loader frames."""

    if not isinstance(max_words, int) or not 1 <= max_words <= 16:
        raise ValueError("max_words must be between 1 and 16")
    blocks: list[ProgramBlock] = []
    addresses = sorted(image.program_words)
    index = 0
    while index < len(addresses):
        first = addresses[index]
        selected = [first]
        index += 1
        while (
            index < len(addresses)
            and len(selected) < max_words
            and addresses[index] == selected[-1] + 1
        ):
            selected.append(addresses[index])
            index += 1
        data = bytearray()
        for address in selected:
            word = image.program_words[address]
            data.extend((word & 0xFF, (word >> 8) & 0xFF))
        blocks.append(ProgramBlock(first, bytes(data)))
    return tuple(blocks)


EXPECTED_FORMAT_BY_VERSION: Mapping[str, int] = MappingProxyType(
    {"2.06": 0x05, "2.70": 0x07, "2.71": 0x07}
)


@dataclass(frozen=True, slots=True)
class FirmwareCompatibility:
    target_matches: bool
    j3_layout_eligible: bool
    expected_data_format: int | None
    data_format_migration_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    live_programming_supported: bool = False

    @property
    def valid_for_offline_planning(self) -> bool:
        return not self.blockers

    def to_dict(self) -> dict[str, object]:
        return {
            "target_matches": self.target_matches,
            "j3_layout_eligible": self.j3_layout_eligible,
            "expected_data_format": (
                f"{self.expected_data_format:02X}"
                if self.expected_data_format is not None
                else None
            ),
            "data_format_migration_required": self.data_format_migration_required,
            "valid_for_offline_planning": self.valid_for_offline_planning,
            "live_programming_supported": self.live_programming_supported,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def assess_firmware_compatibility(
    image: FirmwareImage,
    profile: ControllerProfile,
) -> FirmwareCompatibility:
    blockers: list[str] = []
    warnings: list[str] = []
    target_matches = image.target == "PIC16F877A"
    if not target_matches:
        blockers.append("firmware does not target PIC16F877A")
    j3_eligible = image.variant in (
        FirmwareVariant.DOWNLOADER,
        FirmwareVariant.EMBEDDED,
    )
    if not j3_eligible:
        blockers.append("PICkit/unknown images are not J3 downloader layouts")
    if not image.program_words:
        blockers.append("firmware contains no program words")
    expected_format = (
        EXPECTED_FORMAT_BY_VERSION.get(image.firmware_version)
        if image.firmware_version
        else None
    )
    migration = expected_format is not None and expected_format != profile.data_format
    if migration:
        warnings.append(
            f"firmware expects format {expected_format:02X}; controller uses "
            f"{profile.data_format:02X}; calibration migration is required"
        )
    warnings.append(
        "loader acknowledgements, erase behavior, and interruption recovery are not live-validated"
    )
    return FirmwareCompatibility(
        target_matches=target_matches,
        j3_layout_eligible=j3_eligible,
        expected_data_format=expected_format,
        data_format_migration_required=migration,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
    )


LOADER_IDENTIFY_REQUEST = b"\xEA"
LOADER_IDENTIFY_RESPONSE = b"\xEB"
LOADER_CHECKSUM_ACCEPTED_RESPONSE = b"\xE7"
LOADER_CHECKSUM_REJECTED_RESPONSE = b"\xE8"
LOADER_WRITE_VERIFIED_RESPONSE = b"\xE4"
LOADER_WRITE_FAILED_RESPONSE = b"\xE5"
LOADER_BLOCK_ACKNOWLEDGEMENTS = (b"\xE7", b"\xE4")
LOADER_COMPLETE_REQUEST = b"\xED"
LOADER_COMPLETE_RESPONSE = b"\xE4"

LOADER_FLASH_ROW_WORDS = 4
LOADER_PROTECTED_START = 0x1E80
LOADER_RESET_SOURCE_START = 0x0000
LOADER_RESET_SOURCE_END = 0x0003
LOADER_RESET_RELOCATION_START = 0x1E84


def loader_effective_word_address(word_address: int) -> int | None:
    """Map one J3 Downloader source address to its effective Flash target.

    The resident loader relocates the application's first four words into its
    protected reset trampoline.  Other direct targets in the protected loader
    range are skipped and acknowledged without being written.
    """

    if isinstance(word_address, bool) or not isinstance(word_address, int):
        raise TypeError("word_address must be an integer")
    if not 0 <= word_address <= 0xFFFF:
        raise ValueError("word_address must be between 0x0000 and 0xFFFF")
    if LOADER_RESET_SOURCE_START <= word_address <= LOADER_RESET_SOURCE_END:
        return LOADER_RESET_RELOCATION_START + word_address
    if word_address >= LOADER_PROTECTED_START:
        return None
    return word_address


def loader_state_machine_supported() -> bool:
    """Remain explicit until a recoverable physical loader path is validated."""

    return False
