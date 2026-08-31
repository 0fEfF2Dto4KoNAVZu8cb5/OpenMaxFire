#!/usr/bin/env python3
"""Deterministically summarize preserved J3 flash-session evidence.

This tool only opens evidence files for reading.  It has no serial, USB, or
programmer imports and offers no output-file option.  Its JSON report is meant
to make traffic counts, loader-frame byte order, EEPROM continuity, and probe
timing independently reproducible.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, Mapping, Sequence


SCHEMA = "openmaxfire.flash-session-forensics.v1"
TRAFFIC_FILENAMES = ("loader-traffic.jsonl", "rehearsal-traffic.jsonl")
PROTOCOL_DIRECTIONS = {
    "EA": "tx",
    "EB": "rx",
    "E3": "tx",
    "E7": "rx",
    "ED": "tx",
    "E4": "rx",
    "E5": "rx",
    "E8": "rx",
}
E3_CLASSIFICATIONS = (
    "high_byte_first",
    "low_byte_first",
    "ambiguous_equal_byte_pairs",
    "payload_mismatch",
    "no_reference_image",
    "malformed",
)
RESULT_FIELDS = (
    "schema",
    "state",
    "status",
    "successful",
    "ready_for_operation",
    "recovery_required",
    "loader_identified",
    "blocks_completed",
    "blocks_total",
    "completion_sent",
    "completion_acknowledged",
    "program_blocks_sent",
    "flash_write_commands_sent",
    "failure_outcome",
    "message",
)
JOURNAL_RESULT_FIELDS = (
    "event",
    "successful",
    "recovery_required",
    "loader_identified",
    "identify_attempts",
    "program_blocks_sent",
    "flash_write_commands_sent",
    "completion_sent",
    "completion_acknowledged",
    "failure_outcome",
    "message",
)


class EvidenceError(ValueError):
    """Preserved evidence is malformed or internally inconsistent."""


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> object:
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvidenceError(f"{path}: cannot read JSON: {exc}") from exc


def _load_jsonl(path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise EvidenceError(
                        f"{path}:{line_number}: cannot parse JSON: {exc}"
                    ) from exc
                if not isinstance(row, dict):
                    raise EvidenceError(
                        f"{path}:{line_number}: JSONL row is not an object"
                    )
                row = dict(row)
                row["_evidence_line"] = line_number
                rows.append(row)
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"{path}: cannot read JSONL: {exc}") from exc
    return rows


def _hex_bytes(value: object, *, location: str) -> bytes:
    if not isinstance(value, str):
        raise EvidenceError(f"{location}: data_hex is not a string")
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise EvidenceError(f"{location}: invalid data_hex: {exc}") from exc


def _walk_fields(value: object, pointer: str = "") -> Iterable[tuple[str, str, object]]:
    if isinstance(value, dict):
        for key in sorted(value):
            item = value[key]
            child = f"{pointer}/{key}"
            yield child, str(key), item
            yield from _walk_fields(item, child)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_fields(item, f"{pointer}/{index}")


def _hash_fields(value: object, field_name: str) -> set[str]:
    found: set[str] = set()
    for _, key, item in _walk_fields(value):
        if key == field_name and isinstance(item, str) and len(item) == 64:
            try:
                bytes.fromhex(item)
            except ValueError:
                continue
            found.add(item.lower())
    return found


def _firmware_hashes(value: object) -> set[str]:
    """Recover either live-result or recovery-manifest image hash spelling."""

    return _hash_fields(value, "image_sha256") | _hash_fields(
        value, "firmware_sha256"
    )


def _parse_ihex_program_words(raw: bytes, *, source: Path) -> dict[int, int]:
    """Parse enough Intel HEX to recover PIC program words for E3 comparison."""

    try:
        text = raw.decode("ascii")
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"{source}: Intel HEX is not ASCII") from exc
    memory: dict[int, int] = {}
    base = 0
    eof = False
    for line_number, original in enumerate(text.splitlines(), 1):
        line = original.strip()
        if not line or line.startswith((";", "#")):
            continue
        if not line.startswith(":"):
            continue
        try:
            record = bytes.fromhex(line[1:])
        except ValueError as exc:
            raise EvidenceError(
                f"{source}:{line_number}: invalid Intel HEX"
            ) from exc
        if len(record) < 5 or len(record) != record[0] + 5 or sum(record) & 0xFF:
            raise EvidenceError(f"{source}:{line_number}: malformed Intel HEX record")
        count = record[0]
        offset = int.from_bytes(record[1:3], "big")
        kind = record[3]
        payload = record[4 : 4 + count]
        if kind == 0x00:
            for index, byte in enumerate(payload):
                address = base + offset + index
                previous = memory.get(address)
                if previous is not None and previous != byte:
                    raise EvidenceError(
                        f"{source}:{line_number}: conflicting Intel HEX byte"
                    )
                memory[address] = byte
        elif kind == 0x01:
            eof = True
        elif kind == 0x02 and count == 2:
            base = int.from_bytes(payload, "big") << 4
        elif kind == 0x04 and count == 2:
            base = int.from_bytes(payload, "big") << 16
    if not eof:
        raise EvidenceError(f"{source}: Intel HEX has no EOF record")
    words: dict[int, int] = {}
    for byte_address in sorted(memory):
        if byte_address & 1 or byte_address >= 0x4000:
            continue
        if byte_address + 1 not in memory:
            raise EvidenceError(
                f"{source}: incomplete PIC word at byte address 0x{byte_address:04X}"
            )
        words[byte_address // 2] = (
            memory[byte_address] | (memory[byte_address + 1] << 8)
        )
    return words


def _discover_reference_images(
    repo_root: Path, wanted_hashes: set[str]
) -> tuple[dict[str, Mapping[int, int]], dict[str, str]]:
    references: dict[str, Mapping[int, int]] = {}
    paths: dict[str, str] = {}
    if not wanted_hashes:
        return references, paths
    for path in sorted(repo_root.rglob("*.hex"), key=lambda item: item.as_posix()):
        digest = _sha256(path)
        if digest not in wanted_hashes or digest in references:
            continue
        references[digest] = _parse_ihex_program_words(path.read_bytes(), source=path)
        paths[digest] = _display_path(path, repo_root)
    return references, paths


def _percentile(sorted_values: Sequence[float], fraction: float) -> float | None:
    if not sorted_values:
        return None
    index = (len(sorted_values) - 1) * fraction
    lower = math.floor(index)
    upper = math.ceil(index)
    if lower == upper:
        return sorted_values[lower]
    return sorted_values[lower] + (
        (sorted_values[upper] - sorted_values[lower]) * (index - lower)
    )


def _rounded(value: float | None) -> float | None:
    return None if value is None else round(value, 6)


def _cadence(ea_rows: Sequence[tuple[int, dict[str, object]]]) -> dict[str, object]:
    gaps = [
        (current[0] - previous[0]) / 1_000_000
        for previous, current in zip(ea_rows, ea_rows[1:])
    ]
    if any(gap < 0 for gap in gaps):
        raise EvidenceError("EA monotonic timestamps run backwards within a traffic log")
    ordered = sorted(gaps)
    maximum: dict[str, object] | None = None
    if gaps:
        index = max(range(len(gaps)), key=gaps.__getitem__)
        before = ea_rows[index][1]
        after = ea_rows[index + 1][1]
        maximum = {
            "milliseconds": _rounded(gaps[index]),
            "before_created_utc": before.get("created_utc"),
            "after_created_utc": after.get("created_utc"),
            "before_sequence": before.get("sequence"),
            "after_sequence": after.get("sequence"),
        }
    return {
        "ea_count": len(ea_rows),
        "gap_count": len(gaps),
        "duration_ms": (
            _rounded((ea_rows[-1][0] - ea_rows[0][0]) / 1_000_000)
            if len(ea_rows) >= 2
            else 0.0 if ea_rows else None
        ),
        "min_gap_ms": _rounded(min(gaps)) if gaps else None,
        "median_gap_ms": _rounded(statistics.median(gaps)) if gaps else None,
        "mean_gap_ms": _rounded(statistics.fmean(gaps)) if gaps else None,
        "p95_gap_ms": _rounded(_percentile(ordered, 0.95)),
        "p99_gap_ms": _rounded(_percentile(ordered, 0.99)),
        "max_gap_ms": _rounded(max(gaps)) if gaps else None,
        "gaps_over_ms": {
            str(threshold): sum(gap > threshold for gap in gaps)
            for threshold in (50, 78, 100, 200)
        },
        "max_gap_evidence": maximum,
    }


def _frame_shape(frame: bytes) -> tuple[bool, int | None, int | None, bytes]:
    if len(frame) < 5 or frame[0] != 0xE3:
        return False, None, None, b""
    address = int.from_bytes(frame[1:3], "big")
    byte_count = frame[3]
    payload = frame[5:]
    valid = (
        2 <= byte_count <= 32
        and byte_count % 2 == 0
        and len(frame) == 5 + byte_count
        and (sum(payload) & 0xFF) == frame[4]
    )
    return valid, address, byte_count, payload


def _classify_e3(
    frame: bytes,
    reference_hashes: Iterable[str],
    reference_words: Mapping[str, Mapping[int, int]],
) -> tuple[str, list[str], bool, int | None, int | None]:
    valid, address, byte_count, payload = _frame_shape(frame)
    if not valid or address is None or byte_count is None:
        return "malformed", [], False, address, byte_count
    matched_high: list[str] = []
    matched_low: list[str] = []
    usable_reference = False
    for digest in sorted(set(reference_hashes)):
        words = reference_words.get(digest)
        if words is None:
            continue
        expected_words = [words.get(address + index) for index in range(byte_count // 2)]
        if any(word is None for word in expected_words):
            continue
        usable_reference = True
        high = bytes(
            byte
            for word in expected_words
            for byte in ((int(word) >> 8) & 0xFF, int(word) & 0xFF)
        )
        low = bytes(
            byte
            for word in expected_words
            for byte in (int(word) & 0xFF, (int(word) >> 8) & 0xFF)
        )
        if payload == high:
            matched_high.append(digest)
        if payload == low:
            matched_low.append(digest)
    if matched_high and matched_low:
        return (
            "ambiguous_equal_byte_pairs",
            sorted(set(matched_high + matched_low)),
            True,
            address,
            byte_count,
        )
    if matched_high:
        return "high_byte_first", matched_high, True, address, byte_count
    if matched_low:
        return "low_byte_first", matched_low, True, address, byte_count
    if usable_reference:
        return "payload_mismatch", [], True, address, byte_count
    return "no_reference_image", [], True, address, byte_count


def _session_evidence(session: Path, repo_root: Path) -> dict[str, object]:
    journal_path = session / "journal.jsonl"
    image_hashes: set[str] = set()
    declared_eeprom: list[dict[str, str]] = []
    journal_summary: dict[str, object] | None = None
    if journal_path.is_file():
        rows = _load_jsonl(journal_path)
        event_counts = Counter(
            str(row.get("event")) for row in rows if row.get("event") is not None
        )
        outcomes: list[dict[str, object]] = []
        for row in rows:
            image_hashes.update(_firmware_hashes(row))
            for pointer, key, value in _walk_fields(row):
                if "eeprom" in key.casefold() and "sha256" in key.casefold() and isinstance(value, str):
                    declared_eeprom.append(
                        {
                            "path": _display_path(journal_path, repo_root),
                            "json_pointer": pointer,
                            "field": key,
                            "sha256": value.lower(),
                        }
                    )
            event = row.get("event")
            if isinstance(event, str) and (event.endswith("_result") or event == "result"):
                outcomes.append(
                    {key: row[key] for key in JOURNAL_RESULT_FIELDS if key in row}
                )
        journal_summary = {
            "path": _display_path(journal_path, repo_root),
            "event_counts": dict(sorted(event_counts.items())),
            "result_events": outcomes,
        }

    result_summaries: list[dict[str, object]] = []
    json_documents: list[tuple[Path, object]] = []
    for path in sorted(session.rglob("*.json"), key=lambda item: item.as_posix()):
        document = _load_json(path)
        json_documents.append((path, document))
        image_hashes.update(_firmware_hashes(document))
        for pointer, key, value in _walk_fields(document):
            if "eeprom" in key.casefold() and "sha256" in key.casefold() and isinstance(value, str):
                declared_eeprom.append(
                    {
                        "path": _display_path(path, repo_root),
                        "json_pointer": pointer,
                        "field": key,
                        "sha256": value.lower(),
                    }
                )
        if path.name.endswith("result.json") or path.name == "state.json":
            if isinstance(document, dict):
                summary = {"path": _display_path(path, repo_root)}
                summary.update(
                    {key: document[key] for key in RESULT_FIELDS if key in document}
                )
                result_summaries.append(summary)

    return {
        "session": session.name,
        "image_sha256": sorted(image_hashes),
        "journal": journal_summary,
        "results": result_summaries,
        "declared_eeprom_sha256": sorted(
            declared_eeprom,
            key=lambda item: (item["path"], item["json_pointer"], item["sha256"]),
        ),
        "_json_documents": json_documents,
    }


def _eeprom_artifacts(
    sessions: Sequence[Path],
    repo_root: Path,
    evidence_by_name: Mapping[str, dict[str, object]],
) -> list[dict[str, object]]:
    artifacts: list[dict[str, object]] = []
    for session in sessions:
        documents = evidence_by_name[session.name]["_json_documents"]
        assert isinstance(documents, list)
        for path, document in documents:
            if not isinstance(document, dict) or document.get("schema") != "openmaxfire.eeprom-backup.v1":
                continue
            raw_hex = document.get("raw_hex")
            if not isinstance(raw_hex, str):
                raise EvidenceError(f"{path}: EEPROM backup has no raw_hex")
            try:
                raw = bytes.fromhex(raw_hex)
            except ValueError as exc:
                raise EvidenceError(f"{path}: EEPROM raw_hex is invalid") from exc
            if len(raw) != 256:
                raise EvidenceError(
                    f"{path}: EEPROM raw_hex has {len(raw)} bytes, expected 256"
                )
            mapping = document.get("eeprom")
            if isinstance(mapping, dict):
                try:
                    mapped = bytes(int(str(mapping[f"A{address:02X}"]), 16) for address in range(256))
                except (KeyError, TypeError, ValueError) as exc:
                    raise EvidenceError(f"{path}: malformed EEPROM address map") from exc
                if mapped != raw:
                    raise EvidenceError(f"{path}: EEPROM address map disagrees with raw_hex")
            artifacts.append(
                {
                    "session": session.name,
                    "path": _display_path(path, repo_root),
                    "byte_count": len(raw),
                    "raw_sha256": hashlib.sha256(raw).hexdigest(),
                    "file_sha256": _sha256(path),
                }
            )
    return artifacts


def analyze(repo_root: Path, sessions_root: Path | None = None) -> dict[str, object]:
    repo_root = repo_root.resolve()
    sessions_root = (
        (repo_root / "flash-sessions") if sessions_root is None else sessions_root.resolve()
    )
    if not sessions_root.is_dir():
        raise EvidenceError(f"{sessions_root}: flash-session directory does not exist")
    sessions = sorted(
        (path for path in sessions_root.iterdir() if path.is_dir()),
        key=lambda item: item.name,
    )
    evidence = [_session_evidence(session, repo_root) for session in sessions]
    evidence_by_name = {str(item["session"]): item for item in evidence}
    wanted_hashes = {
        digest
        for item in evidence
        for digest in item["image_sha256"]
        if isinstance(digest, str)
    }
    reference_words, reference_paths = _discover_reference_images(
        repo_root, wanted_hashes
    )

    totals = Counter({opcode: 0 for opcode in PROTOCOL_DIRECTIONS})
    e3_totals = Counter({name: 0 for name in E3_CLASSIFICATIONS})
    logs: list[dict[str, object]] = []
    frames: list[dict[str, object]] = []
    for session in sessions:
        session_hashes = evidence_by_name[session.name]["image_sha256"]
        assert isinstance(session_hashes, list)
        paths = sorted(
            (path for name in TRAFFIC_FILENAMES if (path := session / name).is_file()),
            key=lambda item: item.as_posix(),
        )
        for path in paths:
            rows = _load_jsonl(path)
            counts = Counter({opcode: 0 for opcode in PROTOCOL_DIRECTIONS})
            ea_rows: list[tuple[int, dict[str, object]]] = []
            traffic_records = 0
            for row in rows:
                if row.get("event") != "traffic":
                    continue
                traffic_records += 1
                line_number = row.get("_evidence_line")
                location = f"{path}:{line_number}"
                data = _hex_bytes(row.get("data_hex"), location=location)
                direction = row.get("direction")
                opcode: str | None = None
                if direction == "tx" and data == b"\xEA":
                    opcode = "EA"
                    monotonic_ns = row.get("monotonic_ns")
                    if isinstance(monotonic_ns, bool) or not isinstance(monotonic_ns, int):
                        raise EvidenceError(f"{location}: EA has no integer monotonic_ns")
                    ea_rows.append((monotonic_ns, row))
                elif direction == "tx" and data == b"\xED":
                    opcode = "ED"
                elif direction == "tx" and data.startswith(b"\xE3"):
                    opcode = "E3"
                    classification, matched, valid, address, byte_count = _classify_e3(
                        data, session_hashes, reference_words
                    )
                    e3_totals[classification] += 1
                    frame = {
                        "session": session.name,
                        "path": _display_path(path, repo_root),
                        "line": line_number,
                        "sequence": row.get("sequence"),
                        "created_utc": row.get("created_utc"),
                        "frame_sha256": hashlib.sha256(data).hexdigest(),
                        "word_address": (
                            f"0x{address:04X}" if address is not None else None
                        ),
                        "byte_count": byte_count,
                        "structurally_valid": valid,
                        "byte_order": classification,
                        "matched_image_sha256": matched,
                    }
                    frames.append(frame)
                elif direction == "rx" and len(data) == 1:
                    candidate = f"{data[0]:02X}"
                    if candidate in ("EB", "E7", "E4", "E5", "E8"):
                        opcode = candidate
                if opcode is not None:
                    counts[opcode] += 1
                    totals[opcode] += 1
            logs.append(
                {
                    "session": session.name,
                    "path": _display_path(path, repo_root),
                    "traffic_records": traffic_records,
                    "protocol_counts": dict(counts),
                    "ea_cadence": _cadence(ea_rows),
                }
            )

    eeprom = _eeprom_artifacts(sessions, repo_root, evidence_by_name)
    eeprom_hash_counts = Counter(
        str(artifact["raw_sha256"]) for artifact in eeprom
    )
    public_evidence: list[dict[str, object]] = []
    for item in evidence:
        public_evidence.append(
            {key: value for key, value in item.items() if not key.startswith("_")}
        )
    return {
        "schema": SCHEMA,
        "scope": {
            "repo_root": repo_root.as_posix(),
            "sessions_root": _display_path(sessions_root, repo_root),
            "session_count": len(sessions),
            "traffic_log_count": len(logs),
            "traffic_patterns": [f"*/{name}" for name in TRAFFIC_FILENAMES],
            "read_only": True,
        },
        "totals": {
            "protocol_counts": dict(totals),
            "e3_byte_order": dict(e3_totals),
            "eeprom_backup_count": len(eeprom),
            "eeprom_raw_sha256_counts": dict(sorted(eeprom_hash_counts.items())),
        },
        "reference_images": [
            {"image_sha256": digest, "path": reference_paths[digest]}
            for digest in sorted(reference_paths)
        ],
        "logs": logs,
        "e3_frames": frames,
        "eeprom_backups": eeprom,
        "sessions": public_evidence,
        "counting_rule": (
            "Loader requests are counted only in their expected direction; EA and ED "
            "must be exact one-byte TX records, E3 must begin a TX record, and loader "
            "responses must be exact one-byte RX records. Payload and application bytes "
            "are therefore never miscounted as loader commands."
        ),
        "timing_rule": (
            "EA cadence is derived from consecutive monotonic_ns audit timestamps in "
            "each individual traffic log; percentiles use linear interpolation."
        ),
        "evidence_boundary": (
            "Audit timestamps establish host-side logging cadence, not exact UART wire "
            "arrival or the physical AC-on instant. Historical TX records were written "
            "before the underlying transport write, so E3 counts are host attempts, not "
            "proof of complete wire receipt; a subsequent controller reply is stronger "
            "receipt evidence. E3 byte order is classified only when a declared SHA-256 "
            "resolves to a byte-for-byte matching local image."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read preserved flash-session JSON/JSONL evidence and emit a deterministic "
            "JSON forensic summary. No hardware interfaces are opened."
        )
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="repository root used to find firmware references (default: current directory)",
    )
    parser.add_argument(
        "--sessions-root",
        type=Path,
        help="flash-sessions directory (default: REPO_ROOT/flash-sessions)",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = analyze(args.repo_root, args.sessions_root)
    except EvidenceError as exc:
        print(f"flash-session analysis failed: {exc}", file=sys.stderr)
        return 2
    json.dump(report, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
