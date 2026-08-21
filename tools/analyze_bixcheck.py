#!/usr/bin/env python3
"""Reproducible static-analysis pipeline for the three preserved BixCheck EXEs.

The executable files retain MinGW COFF symbols even though conventional debug
information was removed.  This script combines those symbols, PE section data,
and GNU objdump disassembly to produce reviewable CSV/JSON inventories and
focused assembly excerpts.  It intentionally does not execute vendor code.

Requirements: Python 3.11+ and GNU objdump (binutils).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import struct
import subprocess
import tempfile
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Iterator, Sequence


RECORD_SIZE = 0x58
CHECKOUT_RECORD_SIZE = 0x122


@dataclass(frozen=True)
class VersionSpec:
    version: str
    archive: str
    member: str
    sha256: str
    application_version: str
    downloader_version: str
    stove_software: str
    database_format: int
    adjustment_count: int
    telemetry_count: int
    supported_baudrates: tuple[int, ...]


VERSIONS = (
    VersionSpec(
        version="5.0.21",
        archive="Bixby110_115_02060021_and_manual.zip",
        member="BixCheck_5021.exe",
        sha256="0f51f1b9ffe12011928c7821ecc07db92b2bf98a1d82e5fcf605d464316d52d4",
        application_version="5.0.21",
        downloader_version="1.4",
        stove_software="02.06",
        database_format=5,
        adjustment_count=71,
        telemetry_count=30,
        supported_baudrates=(9600,),
    ),
    VersionSpec(
        version="5.5.00",
        archive="BixCheck_080206.zip",
        member="BixCheck_080206.exe",
        sha256="12dd738a10f72f18a672aeec6ec5e1456ff478103ca84fc154c4f73594aac3d6",
        application_version="5.5.00",
        downloader_version="2.70",
        stove_software="02.70",
        database_format=7,
        adjustment_count=82,
        telemetry_count=30,
        supported_baudrates=(9600, 19200),
    ),
    VersionSpec(
        version="5.5.01",
        archive="BixCheck_080315.zip",
        member="BixCheck_080315.exe",
        sha256="b681f79d284bc5da6d087ce052f916853402144430d4adbceaa2ed2e911c2792",
        application_version="5.5.01",
        downloader_version="2.71",
        stove_software="02.71",
        database_format=7,
        adjustment_count=82,
        telemetry_count=34,
        supported_baudrates=(9600, 19200),
    ),
)


DATA_TABLES = (
    ("utility", "Bixby110UtilityWindowData", 4),
    ("remote_buttons", "Bixby110RCButtonData", 4),
    ("feedwheel_settings", "Bixby110FeedwheelSettingData", 2),
    ("fan_curve_settings", "Bixby110FancurveSettingData", 2),
    ("fuel_settings", "Bixby110FueltypeSettingData", 10),
    ("altitude_settings", "Bixby110AltitudeSettingData", 3),
    ("model_settings", "Bixby110ModelSettingData", 2),
    ("test_settings", "Bixby110TestData", 3),
    ("individualization", "Bixby110IndividualizationData", 9),
    ("adjustment_descriptions", "Bixby110AdjustmentDescriptions", 9),
)


COMBUSTION_TABLES = (
    ("feedwheel", "Bixby110FeedwheelCombustionAdjustments", 0x40),
    ("fan_curve", "Bixby110FancurveCombustionAdjustments", 0x40),
    ("fuel_type", "Bixby110FueltypeCombustionAdjustments", 0x80),
    ("altitude", "Bixby110AltitudeCombustionAdjustments", 0x60),
)


PROTOCOL_FUNCTIONS = (
    "async::set_timeout(long)",
    "async::async(int, long, long, int, int)",
    "async::write(char*, int)",
    "async::read_char(char*)",
    "async::read_string(char*)",
    "bixby110io::getrs232port(unsigned char)",
    "bixby110io::getrs232port(unsigned char, unsigned char)",
    "bixby110io::sendcommand(char*)",
    "bixby110io::scanio(unsigned char*)",
    "bixby110io::regio(unsigned char, unsigned char, unsigned char, unsigned char)",
    "bixby110io::writereg(unsigned char, unsigned char, unsigned char)",
    "bixby110io::readreg(unsigned char, unsigned char)",
    "bixby110io::CollectResponse(unsigned char*)",
    "bixby110io::CollectResponse()",
    "bixby110io::CalculateChecksum(unsigned char)",
    "StoveMultiplyParameterToPercentage(unsigned char, unsigned char)",
    "PercentageToStoveMultiplyParameter(unsigned char, unsigned char)",
)


CHECKOUT_FUNCTIONS = (
    "bixby110checkout::SendInteractiveAction(int)",
    "bixby110checkout::ReadInteractiveResult(int)",
    "bixby110checkout::AnalyzeInteractiveResult(int)",
    "bixby110checkout::SendAutomaticAction(int)",
    "bixby110checkout::ReadAutomaticResult(int)",
    "bixby110checkout::AnalyzeAutomaticResult(int)",
    "bixby110checkout::Bixby110SetupCheckoutInteractiveTests(int, int, int, int)",
    "bixby110checkout::Bixby110SetupCheckoutAutomaticTests(int, int, int, int)",
)


DOWNLOADER_FUNCTIONS = (
    "bixby110downloader::GetStoveVersion()",
    "bixby110downloader::AttemptStoveReset()",
    "bixby110downloader::SendDone()",
    "bixby110downloader::LoadHex(char*)",
    "bixby110downloader::DownLoad()",
    "bixby110downloader::Identify()",
)


TELEMETRY_FUNCTIONS = (
    "bixby110io::scanio(unsigned char*)",
    "bixby110control::Bixby110UpdateData(char, unsigned char)",
    "bixby110control::Bixby110DialogSetupTelemetry(int, int, int, int)",
)


WRITE_UI_FUNCTIONS = (
    "bixby110control::BixbyWriteRegister(unsigned char, unsigned char, unsigned char, unsigned char)",
    "bixby110control::BixbyWriteRegister(unsigned char, unsigned char, unsigned char)",
    "bixby110control::Bixby110TuneAdjustments(unsigned char)",
    "bixby110control::Bixby110Initialize(unsigned char, unsigned char)",
    "bixby110control::Bixby110DialogSetupIndividualization(int, int, int, int)",
    "bixby110control::Bixby110DialogSetupQuickCal(int, int, int, int)",
    "bixby110control::Bixby110DialogSetupDebug(int, int, int, int)",
)


LOGGING_FUNCTIONS = (
    "bixby110control::AppendDataLogLine(char*, unsigned char)",
    "bixby110control::AppendDataLogLine(char*)",
    "bixby110control::WriteDataLogTimeDate()",
    "bixby110control::DataLogLineAssemblePayload()",
    "bixby110control::WriteDataLogLine()",
    "bixby110control::WriteDataLogDescription()",
    "bixby110control::GenerateReport(char*)",
    "bixby110control::LoadReport(char*)",
)


MONITOR_FUNCTIONS = (
    "bixby110control::Bixby110DialogSetupFlueMonitor(int, int, int, int)",
    "bixby110control::Bixby110DialogSetupFuelMonitor(HWND__*, int, int, int, int, int)",
    "bixby110control::Bixby110DialogSetupUtilityWindows()",
    "bixby110control::Bixby110DialogSetupUtilityWindowButtons(int, int, int, int)",
)


SELECTED_STRING_TERMS = (
    "bixcheck",
    "downloader",
    "stove software",
    "data format",
    "checksum",
    "telemetry",
    "lean burn",
    "wheat",
    "biomass",
    "corn",
    "wood",
    "checkout",
    "serial",
    "plate motor",
    "igniter",
    "exhaust fan",
)


@dataclass(frozen=True)
class Section:
    index: int
    name: str
    virtual_size: int
    virtual_address: int
    raw_size: int
    raw_pointer: int
    characteristics: int


class PEImage:
    """Small dependency-free PE32 reader, sufficient for preserved EXEs."""

    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        if self.data[:2] != b"MZ":
            raise ValueError(f"{path}: not an MZ executable")
        pe_offset = struct.unpack_from("<I", self.data, 0x3C)[0]
        if self.data[pe_offset : pe_offset + 4] != b"PE\0\0":
            raise ValueError(f"{path}: no PE signature")
        coff = pe_offset + 4
        (
            self.machine,
            section_count,
            self.timestamp,
            _symbol_table,
            _symbol_count,
            optional_size,
            self.characteristics,
        ) = struct.unpack_from("<HHIIIHH", self.data, coff)
        optional = coff + 20
        magic = struct.unpack_from("<H", self.data, optional)[0]
        if magic != 0x10B:
            raise ValueError(f"{path}: expected PE32, found magic 0x{magic:04X}")
        self.entry_rva = struct.unpack_from("<I", self.data, optional + 16)[0]
        self.image_base = struct.unpack_from("<I", self.data, optional + 28)[0]
        self.subsystem = struct.unpack_from("<H", self.data, optional + 68)[0]
        section_table = optional + optional_size
        sections: list[Section] = []
        for index in range(section_count):
            offset = section_table + index * 40
            name = self.data[offset : offset + 8].split(b"\0", 1)[0].decode("ascii")
            virtual_size, virtual_address, raw_size, raw_pointer = struct.unpack_from(
                "<IIII", self.data, offset + 8
            )
            characteristics = struct.unpack_from("<I", self.data, offset + 36)[0]
            sections.append(
                Section(
                    index=index + 1,
                    name=name,
                    virtual_size=virtual_size,
                    virtual_address=virtual_address,
                    raw_size=raw_size,
                    raw_pointer=raw_pointer,
                    characteristics=characteristics,
                )
            )
        self.sections = tuple(sections)

    def section(self, identifier: int | str) -> Section:
        for section in self.sections:
            if identifier == section.index or identifier == section.name:
                return section
        raise KeyError(identifier)

    def section_data(self, section: int | str, offset: int, size: int) -> bytes:
        item = self.section(section)
        if offset < 0 or offset + size > item.raw_size:
            raise ValueError(
                f"read outside {item.name}: offset=0x{offset:X}, size=0x{size:X}"
            )
        start = item.raw_pointer + offset
        return self.data[start : start + size]

    def va_for(self, section_number: int, section_offset: int) -> int:
        return self.image_base + self.section(section_number).virtual_address + section_offset

    def metadata(self) -> dict[str, object]:
        return {
            "path": self.path.name,
            "size_bytes": len(self.data),
            "sha256": hashlib.sha256(self.data).hexdigest(),
            "machine": f"0x{self.machine:04X}",
            "timestamp_unix": self.timestamp,
            "timestamp_utc": datetime.fromtimestamp(
                self.timestamp, tz=timezone.utc
            ).isoformat(),
            "image_base": f"0x{self.image_base:08X}",
            "entry_rva": f"0x{self.entry_rva:08X}",
            "entry_va": f"0x{self.image_base + self.entry_rva:08X}",
            "subsystem": self.subsystem,
            "characteristics": f"0x{self.characteristics:04X}",
            "sections": [asdict(item) for item in self.sections],
        }


SYMBOL_RE = re.compile(
    r"^\[\s*\d+\]\(sec\s+(-?\d+)\).*?"
    r"\(ty\s+([0-9A-Fa-f]+)\).*?\(scl\s+(\d+)\).*?"
    r"0x([0-9A-Fa-f]+)\s+(.+)$"
)


@dataclass
class Symbol:
    section: int
    symbol_type: int
    storage_class: int
    offset: int
    name: str
    source: str


@dataclass
class Instruction:
    address: int
    raw: bytes
    assembly: str
    rendered: str


@dataclass
class Function:
    source: str
    name: str
    occurrence: int
    section: int
    section_offset: int
    rva: int
    va: int
    size: int
    instruction_count: int
    raw_sha256: str
    normalized_sha256: str

    @property
    def key(self) -> tuple[str, int]:
        return self.name, self.occurrence


def run_objdump(executable: Path, *args: str) -> str:
    completed = subprocess.run(
        ["objdump", *args, str(executable)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        errors="replace",
    )
    return completed.stdout


def parse_symbols(text: str) -> list[Symbol]:
    symbols: list[Symbol] = []
    source = "<linker/global>"
    seen: set[tuple[int, int, str]] = set()
    for line in text.splitlines():
        match = SYMBOL_RE.match(line)
        if not match:
            continue
        section, symbol_type, storage_class, offset, name = match.groups()
        section_number = int(section)
        storage = int(storage_class)
        if section_number == -2 and storage == 103:
            source = name
            continue
        symbol = Symbol(
            section=section_number,
            symbol_type=int(symbol_type, 16),
            storage_class=storage,
            offset=int(offset, 16),
            name=name.strip(),
            source=source,
        )
        key = (symbol.section, symbol.offset, symbol.name)
        if key not in seen:
            seen.add(key)
            symbols.append(symbol)
    return symbols


INSTRUCTION_RE = re.compile(
    r"^\s*([0-9A-Fa-f]+):\s+((?:[0-9A-Fa-f]{2}(?:\s+|$))+)(.*)$"
)


def parse_disassembly(text: str) -> dict[int, Instruction]:
    instructions: dict[int, Instruction] = {}
    for line in text.splitlines():
        match = INSTRUCTION_RE.match(line)
        if not match:
            continue
        address_text, raw_text, assembly = match.groups()
        raw_hex = "".join(raw_text.split())
        if not raw_hex or len(raw_hex) % 2:
            continue
        address = int(address_text, 16)
        instructions[address] = Instruction(
            address=address,
            raw=bytes.fromhex(raw_hex),
            assembly=assembly.strip(),
            rendered=line.rstrip(),
        )
    return instructions


SYMBOL_TARGET_RE = re.compile(r"\b[0-9A-Fa-f]+\s+<([^>]+)>")
ABSOLUTE_RE = re.compile(r"(?<![A-Za-z0-9_])0x[0-9A-Fa-f]{6,}")


def normalize_instruction(assembly: str, function_name: str) -> str:
    own_base = function_name.split("(", 1)[0]

    def target(match: re.Match[str]) -> str:
        symbol = match.group(1)
        base = symbol.split("+0x", 1)[0].split("-0x", 1)[0]
        if base.split("(", 1)[0] == own_base:
            return "<LOCAL>"
        return f"<SYM:{base}>"

    normalized = SYMBOL_TARGET_RE.sub(target, assembly)
    normalized = ABSOLUTE_RE.sub("ADDR", normalized)
    return " ".join(normalized.split())


def build_functions(
    pe: PEImage,
    symbols: Sequence[Symbol],
    instructions: dict[int, Instruction],
) -> list[Function]:
    candidates = [item for item in symbols if item.section == 1 and item.symbol_type == 0x20]
    addresses = sorted({item.offset for item in candidates})
    text_section = pe.section(1)
    next_offset: dict[int, int] = {}
    for index, start in enumerate(addresses):
        next_offset[start] = (
            addresses[index + 1] if index + 1 < len(addresses) else text_section.virtual_size
        )
    occurrences: Counter[str] = Counter()
    functions: list[Function] = []
    for symbol in candidates:
        occurrence = occurrences[symbol.name]
        occurrences[symbol.name] += 1
        end = next_offset[symbol.offset]
        size = max(0, end - symbol.offset)
        raw = pe.section_data(1, symbol.offset, min(size, text_section.raw_size - symbol.offset))
        va = pe.va_for(1, symbol.offset)
        function_instructions = [
            item for address, item in sorted(instructions.items()) if va <= address < va + size
        ]
        normalized = "\n".join(
            normalize_instruction(item.assembly, symbol.name) for item in function_instructions
        ).encode("utf-8")
        functions.append(
            Function(
                source=symbol.source,
                name=symbol.name,
                occurrence=occurrence,
                section=1,
                section_offset=symbol.offset,
                rva=text_section.virtual_address + symbol.offset,
                va=va,
                size=size,
                instruction_count=len(function_instructions),
                raw_sha256=hashlib.sha256(raw).hexdigest(),
                normalized_sha256=hashlib.sha256(normalized).hexdigest(),
            )
        )
    return functions


def c_string(field: bytes) -> str:
    return field.split(b"\0", 1)[0].decode("cp1252", errors="replace").strip()


def data_symbol_map(symbols: Sequence[Symbol]) -> dict[str, Symbol]:
    return {item.name: item for item in symbols if item.section == 2}


def decode_data_element(record: bytes) -> dict[str, object]:
    if len(record) != RECORD_SIZE:
        raise ValueError("invalid data-element record length")
    return {
        "type": record[0],
        "label": c_string(record[0x01:0x21]),
        "units_or_description": c_string(record[0x21:0x41]),
        "value_or_default": struct.unpack_from("<i", record, 0x44)[0],
        "unit": chr(record[0x48]) if record[0x48] else "",
        "address": record[0x49],
        "address_hex": f"0x{record[0x49]:02X}",
        "maximum": struct.unpack_from("<i", record, 0x4C)[0],
        "minimum": struct.unpack_from("<i", record, 0x50)[0],
        "length_or_mask": struct.unpack_from("<H", record, 0x54)[0],
        "display_mode": struct.unpack_from("<H", record, 0x56)[0],
    }


def extract_data_elements(
    pe: PEImage, symbols: Sequence[Symbol], spec: VersionSpec
) -> list[dict[str, object]]:
    symbol_map = data_symbol_map(symbols)
    tables = list(DATA_TABLES) + [
        ("adjustments", "Bixby110AdjustmentData", spec.adjustment_count),
        ("telemetry", "Bixby110TelemetryData", spec.telemetry_count),
    ]
    rows: list[dict[str, object]] = []
    for table_name, symbol_name, count in tables:
        symbol = symbol_map.get(symbol_name)
        if symbol is None:
            continue
        for index in range(count):
            record = pe.section_data(2, symbol.offset + index * RECORD_SIZE, RECORD_SIZE)
            decoded = decode_data_element(record)
            rows.append(
                {
                    "version": spec.version,
                    "table": table_name,
                    "index": index,
                    "symbol": symbol_name,
                    "section_offset": f"0x{symbol.offset + index * RECORD_SIZE:04X}",
                    **decoded,
                }
            )
    return rows


def decode_checkout_record(record: bytes) -> dict[str, object]:
    if len(record) != CHECKOUT_RECORD_SIZE:
        raise ValueError("invalid checkout record length")
    return {
        "type": record[0],
        "label": c_string(record[0x01:0x21]),
        "instruction": c_string(record[0x21:0xA1]),
        "failure_hint": c_string(record[0xA1:0x121]),
    }


def extract_checkout(
    pe: PEImage, symbols: Sequence[Symbol], spec: VersionSpec
) -> list[dict[str, object]]:
    symbol_map = data_symbol_map(symbols)
    groups = (
        ("automatic", "Bixby110AutomaticCheckoutTests", 9),
        ("interactive", "Bixby110InteractiveCheckoutTests", 34),
        ("iic_verification", "Bixby110IICVerificationTests", 3),
    )
    rows: list[dict[str, object]] = []
    for group, symbol_name, count in groups:
        symbol = symbol_map.get(symbol_name)
        if symbol is None:
            continue
        for index in range(count):
            record = pe.section_data(
                2, symbol.offset + index * CHECKOUT_RECORD_SIZE, CHECKOUT_RECORD_SIZE
            )
            decoded = decode_checkout_record(record)
            reachable = not (group == "automatic" and index == 8)
            rows.append(
                {
                    "version": spec.version,
                    "group": group,
                    "index": index,
                    "display_number": (
                        index + 1
                        if group == "interactive"
                        else index + 35
                        if group == "iic_verification"
                        else index + 38
                    ),
                    "ui_reachable": reachable,
                    "symbol": symbol_name,
                    "section_offset": f"0x{symbol.offset + index * CHECKOUT_RECORD_SIZE:04X}",
                    **decoded,
                }
            )
    return rows


def extract_combustion(
    pe: PEImage, symbols: Sequence[Symbol], spec: VersionSpec
) -> list[dict[str, object]]:
    symbol_map = data_symbol_map(symbols)
    rows: list[dict[str, object]] = []
    for table, symbol_name, size in COMBUSTION_TABLES:
        symbol = symbol_map.get(symbol_name)
        if symbol is None:
            continue
        data = pe.section_data(2, symbol.offset, size)
        for index, value in enumerate(data):
            rows.append(
                {
                    "version": spec.version,
                    "table": table,
                    "index": index,
                    "value": value,
                    "value_hex": f"0x{value:02X}",
                    "symbol": symbol_name,
                    "section_offset": f"0x{symbol.offset + index:04X}",
                }
            )
    return rows


def ascii_strings(data: bytes, minimum: int = 5) -> Iterator[tuple[int, str]]:
    start: int | None = None
    for index, value in enumerate(data + b"\0"):
        if 0x20 <= value <= 0x7E or value in (0x09,):
            if start is None:
                start = index
        elif start is not None:
            if index - start >= minimum:
                yield start, data[start:index].decode("ascii", errors="replace")
            start = None


def selected_strings(pe: PEImage, spec: VersionSpec) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for offset, value in ascii_strings(pe.data):
        lowered = value.lower()
        terms = [term for term in SELECTED_STRING_TERMS if term in lowered]
        if terms:
            rows.append(
                {
                    "version": spec.version,
                    "file_offset": f"0x{offset:08X}",
                    "matched_terms": ";".join(terms),
                    "string": value,
                }
            )
    return rows


def function_instruction_rows(
    function: Function, instructions: dict[int, Instruction]
) -> list[Instruction]:
    return [
        item
        for address, item in sorted(instructions.items())
        if function.va <= address < function.va + function.size
    ]


def extract_calls(
    functions: Sequence[Function], instructions: dict[int, Instruction], version: str
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    call_re = re.compile(r"\bcall\s+(?:0x)?([0-9A-Fa-f]+)\s+<([^>]+)>")
    for function in functions:
        counts: Counter[tuple[int, str]] = Counter()
        for instruction in function_instruction_rows(function, instructions):
            match = call_re.search(instruction.assembly)
            if match:
                counts[(int(match.group(1), 16), match.group(2))] += 1
        for (target_va, target_name), count in sorted(counts.items()):
            rows.append(
                {
                    "version": version,
                    "source": function.source,
                    "caller": function.name,
                    "caller_occurrence": function.occurrence,
                    "caller_va": f"0x{function.va:08X}",
                    "callee": target_name,
                    "callee_va": f"0x{target_va:08X}",
                    "call_sites": count,
                }
            )
    return rows


def find_functions(functions: Sequence[Function], names: Sequence[str]) -> list[Function]:
    wanted = set(names)
    selected = [item for item in functions if item.name in wanted]
    return sorted(selected, key=lambda item: (item.va, item.occurrence))


def write_assembly_excerpt(
    path: Path,
    title: str,
    version: str,
    functions: Sequence[Function],
    instructions: dict[int, Instruction],
) -> None:
    lines = [
        f"# {title}",
        f"# BixCheck {version}; generated by tools/analyze_bixcheck.py",
        "# Exact GNU objdump Intel-syntax excerpts; addresses are build-specific.",
        "",
    ]
    for function in functions:
        lines.extend(
            [
                f"# source={function.source}",
                f"# va=0x{function.va:08X} size=0x{function.size:X}",
                f"0x{function.va:08X} <{function.name}>:",
            ]
        )
        rows = function_instruction_rows(function, instructions)
        lines.extend(item.rendered for item in rows)
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_csv(path: Path, rows: Sequence[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def function_rows(functions: Sequence[Function], version: str) -> list[dict[str, object]]:
    return [
        {
            "version": version,
            "source": item.source,
            "name": item.name,
            "occurrence": item.occurrence,
            "section": item.section,
            "section_offset": f"0x{item.section_offset:08X}",
            "rva": f"0x{item.rva:08X}",
            "va": f"0x{item.va:08X}",
            "size": item.size,
            "instruction_count": item.instruction_count,
            "raw_sha256": item.raw_sha256,
            "normalized_sha256": item.normalized_sha256,
        }
        for item in functions
    ]


def project_function(function: Function) -> bool:
    source = function.source.lower()
    return source == "async.cpp" or source == "main.cpp" or source.startswith("bixby110")


def compare_functions(
    older: VersionSpec,
    newer: VersionSpec,
    analyses: dict[str, dict[str, object]],
) -> list[dict[str, object]]:
    old_functions = {
        item.key: item
        for item in analyses[older.version]["functions"]  # type: ignore[index]
        if project_function(item)
    }
    new_functions = {
        item.key: item
        for item in analyses[newer.version]["functions"]  # type: ignore[index]
        if project_function(item)
    }
    rows: list[dict[str, object]] = []
    for key in sorted(set(old_functions) | set(new_functions)):
        old = old_functions.get(key)
        new = new_functions.get(key)
        if old is None:
            status = "added"
        elif new is None:
            status = "removed"
        elif old.normalized_sha256 == new.normalized_sha256:
            status = "same_normalized"
        elif old.raw_sha256 == new.raw_sha256:
            status = "same_raw"
        else:
            status = "changed"
        representative = new or old
        assert representative is not None
        rows.append(
            {
                "comparison": f"{older.version}_to_{newer.version}",
                "source_old": old.source if old else "",
                "source_new": new.source if new else "",
                "name": representative.name,
                "occurrence": representative.occurrence,
                "status": status,
                "old_va": f"0x{old.va:08X}" if old else "",
                "new_va": f"0x{new.va:08X}" if new else "",
                "old_size": old.size if old else "",
                "new_size": new.size if new else "",
                "old_normalized_sha256": old.normalized_sha256 if old else "",
                "new_normalized_sha256": new.normalized_sha256 if new else "",
            }
        )
    return rows


def compare_keyed_rows(
    older: VersionSpec,
    newer: VersionSpec,
    analyses: dict[str, dict[str, object]],
    collection: str,
    key_fields: Sequence[str],
    value_fields: Sequence[str],
) -> list[dict[str, object]]:
    old_rows = analyses[older.version][collection]  # type: ignore[index]
    new_rows = analyses[newer.version][collection]  # type: ignore[index]
    old_map = {tuple(item[field] for field in key_fields): item for item in old_rows}
    new_map = {tuple(item[field] for field in key_fields): item for item in new_rows}
    output: list[dict[str, object]] = []
    for key in sorted(set(old_map) | set(new_map)):
        old = old_map.get(key)
        new = new_map.get(key)
        if old is None:
            status = "added"
        elif new is None:
            status = "removed"
        else:
            status = (
                "same"
                if all(old[field] == new[field] for field in value_fields)
                else "changed"
            )
        row: dict[str, object] = {
            "comparison": f"{older.version}_to_{newer.version}",
            **{field: value for field, value in zip(key_fields, key)},
            "status": status,
        }
        for field in value_fields:
            row[f"old_{field}"] = old[field] if old else ""
            row[f"new_{field}"] = new[field] if new else ""
        output.append(row)
    return output


def analyze_one(executable: Path, spec: VersionSpec, output_root: Path) -> dict[str, object]:
    pe = PEImage(executable)
    actual_sha = hashlib.sha256(pe.data).hexdigest()
    if actual_sha != spec.sha256:
        raise ValueError(
            f"{spec.version}: SHA-256 mismatch: expected {spec.sha256}, got {actual_sha}"
        )
    symbol_text = run_objdump(executable, "-t", "-C")
    disassembly_text = run_objdump(executable, "-d", "-C", "-Mintel")
    symbols = parse_symbols(symbol_text)
    instructions = parse_disassembly(disassembly_text)
    functions = build_functions(pe, symbols, instructions)
    data_elements = extract_data_elements(pe, symbols, spec)
    checkout = extract_checkout(pe, symbols, spec)
    combustion = extract_combustion(pe, symbols, spec)
    strings = selected_strings(pe, spec)
    calls = extract_calls(functions, instructions, spec.version)

    destination = output_root / spec.version
    destination.mkdir(parents=True, exist_ok=True)
    write_csv(destination / "functions.csv", function_rows(functions, spec.version))
    write_csv(destination / "call-graph.csv", calls)
    write_csv(destination / "data-elements.csv", data_elements)
    write_csv(destination / "checkout-tests.csv", checkout)
    write_csv(destination / "combustion-adjustments.csv", combustion)
    write_csv(destination / "selected-strings.csv", strings)
    write_assembly_excerpt(
        destination / "protocol-core.asm",
        "Normal serial protocol and checksum core",
        spec.version,
        find_functions(functions, PROTOCOL_FUNCTIONS),
        instructions,
    )
    write_assembly_excerpt(
        destination / "checkout-core.asm",
        "Factory checkout core",
        spec.version,
        find_functions(functions, CHECKOUT_FUNCTIONS),
        instructions,
    )
    write_assembly_excerpt(
        destination / "downloader-core.asm",
        "Firmware downloader core (unsafe binary protocol)",
        spec.version,
        find_functions(functions, DOWNLOADER_FUNCTIONS),
        instructions,
    )
    focused_groups = (
        (
            "telemetry-core.asm",
            "Telemetry receive, decode, conversion, and UI update core",
            TELEMETRY_FUNCTIONS,
        ),
        (
            "write-ui-core.asm",
            "Configuration writes, initialization, QuickCal, and debug UI core",
            WRITE_UI_FUNCTIONS,
        ),
        (
            "logging-core.asm",
            "Data logging and report workflow core",
            LOGGING_FUNCTIONS,
        ),
        (
            "monitor-core.asm",
            "Flue, fuel, and utility monitor UI core",
            MONITOR_FUNCTIONS,
        ),
    )
    focused_counts: dict[str, int] = {}
    for filename, title, names in focused_groups:
        selected = find_functions(functions, names)
        write_assembly_excerpt(
            destination / filename,
            title,
            spec.version,
            selected,
            instructions,
        )
        focused_counts[filename] = len(selected)

    source_files = sorted({item.source for item in functions})
    summary = {
        "schema": 1,
        "generated_by": "tools/analyze_bixcheck.py",
        "analysis_type": "static-only; executable was not run",
        "version": asdict(spec),
        "pe": pe.metadata(),
        "retained_coff": {
            "symbol_count": len(symbols),
            "function_count": len(functions),
            "unique_function_offsets": len({item.section_offset for item in functions}),
            "source_files": source_files,
        },
        "extracted": {
            "data_elements": len(data_elements),
            "checkout_records": len(checkout),
            "checkout_ui_reachable": sum(bool(item["ui_reachable"]) for item in checkout),
            "combustion_adjustment_bytes": len(combustion),
            "selected_strings": len(strings),
            "call_edges": len(calls),
            "focused_assembly_functions": focused_counts,
        },
        "serial": {
            "baudrates_selected_by_pc_software": list(spec.supported_baudrates),
            "framing": "8N1",
            "request_terminator": None,
            "response_terminators_accepted": ["CR", "LF"],
            "normal_protocol": "ASCII CRxx/CWxxyy family",
            "downloader_protocol": "separate binary bootloader framing",
        },
    }
    (destination / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return {
        "spec": spec,
        "pe": pe,
        "symbols": symbols,
        "functions": functions,
        "data_elements": data_elements,
        "checkout": checkout,
        "combustion": combustion,
        "strings": strings,
        "calls": calls,
        "summary": summary,
    }


def write_comparisons(
    output_root: Path, analyses: dict[str, dict[str, object]]
) -> dict[str, object]:
    pairs = ((VERSIONS[0], VERSIONS[1]), (VERSIONS[1], VERSIONS[2]))
    function_changes: list[dict[str, object]] = []
    data_changes: list[dict[str, object]] = []
    checkout_changes: list[dict[str, object]] = []
    combustion_changes: list[dict[str, object]] = []
    for older, newer in pairs:
        function_changes.extend(compare_functions(older, newer, analyses))
        data_changes.extend(
            compare_keyed_rows(
                older,
                newer,
                analyses,
                "data_elements",
                ("table", "index"),
                (
                    "type",
                    "label",
                    "units_or_description",
                    "value_or_default",
                    "unit",
                    "address_hex",
                    "maximum",
                    "minimum",
                    "length_or_mask",
                    "display_mode",
                ),
            )
        )
        checkout_changes.extend(
            compare_keyed_rows(
                older,
                newer,
                analyses,
                "checkout",
                ("group", "index"),
                ("type", "label", "instruction", "failure_hint", "ui_reachable"),
            )
        )
        combustion_changes.extend(
            compare_keyed_rows(
                older,
                newer,
                analyses,
                "combustion",
                ("table", "index"),
                ("value", "value_hex"),
            )
        )
    comparison_dir = output_root / "comparison"
    write_csv(comparison_dir / "function-changes.csv", function_changes)
    write_csv(comparison_dir / "data-element-changes.csv", data_changes)
    write_csv(comparison_dir / "checkout-changes.csv", checkout_changes)
    write_csv(comparison_dir / "combustion-adjustment-changes.csv", combustion_changes)

    summaries: dict[str, object] = {}
    for older, newer in pairs:
        pair_name = f"{older.version}_to_{newer.version}"
        selected_functions = [
            item for item in function_changes if item["comparison"] == pair_name
        ]
        selected_data = [item for item in data_changes if item["comparison"] == pair_name]
        selected_checkout = [
            item for item in checkout_changes if item["comparison"] == pair_name
        ]
        selected_combustion = [
            item for item in combustion_changes if item["comparison"] == pair_name
        ]
        summaries[pair_name] = {
            "functions": dict(Counter(item["status"] for item in selected_functions)),
            "data_elements": dict(Counter(item["status"] for item in selected_data)),
            "checkout_records": dict(Counter(item["status"] for item in selected_checkout)),
            "combustion_bytes": dict(
                Counter(item["status"] for item in selected_combustion)
            ),
        }
    summary = {
        "schema": 1,
        "generated_by": "tools/analyze_bixcheck.py",
        "normalization_note": (
            "Function normalization removes build-specific absolute addresses and "
            "symbolic branch destinations; changed hashes still require human review."
        ),
        "comparisons": summaries,
    }
    comparison_dir.mkdir(parents=True, exist_ok=True)
    (comparison_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def extract_executable(archive: Path, member: str, destination: Path) -> Path:
    with zipfile.ZipFile(archive) as source:
        try:
            data = source.read(member)
        except KeyError as exc:
            raise ValueError(f"{archive}: missing {member}") from exc
    destination.write_bytes(data)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="OpenMaxFire repository root",
    )
    parser.add_argument(
        "--version",
        choices=[item.version for item in VERSIONS] + ["all"],
        default="all",
        help="analyze one version or the complete matrix",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if shutil.which("objdump") is None:
        raise SystemExit("GNU objdump is required")
    repo_root = args.repo_root.resolve()
    archive_root = repo_root / "preservation" / "original" / "vendor-packages"
    output_root = repo_root / "reverse-engineering" / "bixcheck"
    specs = VERSIONS if args.version == "all" else tuple(
        item for item in VERSIONS if item.version == args.version
    )
    analyses: dict[str, dict[str, object]] = {}
    with tempfile.TemporaryDirectory(prefix="openmaxfire-bixcheck-") as temp_name:
        temp_root = Path(temp_name)
        for spec in specs:
            archive = archive_root / spec.archive
            if not archive.is_file():
                raise SystemExit(f"missing preserved archive: {archive}")
            executable = extract_executable(archive, spec.member, temp_root / spec.member)
            analyses[spec.version] = analyze_one(executable, spec, output_root)
            print(f"analyzed BixCheck {spec.version}")
    if len(specs) == len(VERSIONS):
        comparison = write_comparisons(output_root, analyses)
        print(json.dumps(comparison["comparisons"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
