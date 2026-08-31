#!/usr/bin/env python3
"""Construct an unqualified hybrid image for offline forensic analysis only.

The output combines 2.06 program/configuration with a controller's preserved
2.02-format EEPROM and User IDs.  Firmware 2.06 expects format 05, while this
incident controller held format 04 data.  The resulting hybrid must not be
imported into a programmer, programmed, or operated.  This tool has no
programmer, USB, erase, or device-programming capability.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

from openmaxfire.firmware import FirmwareImage
from openmaxfire.preservation import (
    PIC16F877A_EEPROM_BYTES,
    PIC16F877A_PROGRAM_WORDS,
    inspect_pic16f877a_dump,
)


EXPECTED_DONOR_SHA256 = (
    "2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4"
)
EXPECTED_REFERENCE_SHA256 = (
    "272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab"
)
EXPECTED_INCIDENT_PROGRAM_DIFFS = {
    0x1E84: (0x3018, 0x1830),
    0x1E85: (0x008A, 0x0A00),
    0x1E86: (0x2800, 0x0028),
}


def _record(address: int, record_type: int, payload: bytes = b"") -> str:
    body = bytes(
        (len(payload), (address >> 8) & 0xFF, address & 0xFF, record_type)
    ) + payload
    return ":" + (body + bytes(((-sum(body)) & 0xFF,))).hex().upper()


def serialize_intel_hex(memory: Mapping[int, int]) -> bytes:
    """Serialize the PIC's sub-64-KiB sparse byte map deterministically."""

    if not memory:
        raise ValueError("cannot serialize an empty memory map")
    if any(not 0 <= address <= 0xFFFF for address in memory):
        raise ValueError("hybrid candidate contains an address outside linear base zero")
    lines = [_record(0, 0x04, b"\x00\x00")]
    addresses = sorted(memory)
    index = 0
    while index < len(addresses):
        start = addresses[index]
        selected = [start]
        index += 1
        while (
            index < len(addresses)
            and len(selected) < 16
            and addresses[index] == selected[-1] + 1
        ):
            selected.append(addresses[index])
            index += 1
        lines.append(
            _record(start, 0x00, bytes(memory[address] for address in selected))
        )
    lines.append(_record(0, 0x01))
    return ("\n".join(lines) + "\n").encode("ascii")


def _require_complete(image: FirmwareImage, label: str) -> None:
    checks = (
        (len(image.program_words) == PIC16F877A_PROGRAM_WORDS, "program memory"),
        (len(image.eeprom_words) == PIC16F877A_EEPROM_BYTES, "EEPROM"),
        (len(image.user_id_words) == 4, "User IDs"),
        (image.configuration_word is not None, "configuration word"),
    )
    missing = [name for valid, name in checks if not valid]
    if missing:
        raise ValueError(f"{label} is not complete: {', '.join(missing)}")


def build_unqualified_candidate(
    *,
    donor_path: Path,
    reference_path: Path,
    controller_path: Path,
    expected_controller_sha256: str,
) -> tuple[bytes, dict[str, object]]:
    donor = FirmwareImage.load(donor_path)
    reference = FirmwareImage.load(reference_path)
    controller = FirmwareImage.load(controller_path)
    if donor.sha256 != EXPECTED_DONOR_SHA256:
        raise ValueError("donor is not the hash-pinned full 2.06 PICkit image")
    if reference.sha256 != EXPECTED_REFERENCE_SHA256:
        raise ValueError("reference is not the sole hash-pinned pre-write 2.02 image")
    if controller.sha256 != expected_controller_sha256.lower():
        raise ValueError("controller dump SHA-256 does not match the operator-supplied gate")
    for image, label in (
        (donor, "2.06 donor"),
        (reference, "2.02 reference"),
        (controller, "controller dump"),
    ):
        _require_complete(image, label)
        inspection = inspect_pic16f877a_dump(image)
        if not inspection.safe_read:
            raise ValueError(f"{label} failed protection/coverage checks: {inspection.blockers}")

    if donor.configuration_word != 0x3F32:
        raise ValueError("2.06 donor configuration is not the expected 0x3F32")
    if controller.configuration_word != reference.configuration_word:
        raise ValueError("controller configuration no longer matches its 2.02 reference")
    if dict(controller.eeprom_words) != dict(reference.eeprom_words):
        raise ValueError("controller EEPROM no longer matches its preserved reference")
    if dict(controller.user_id_words) != dict(reference.user_id_words):
        raise ValueError("controller User IDs no longer match their preserved reference")

    program_diffs = {
        address: (reference.program_words[address], controller.program_words[address])
        for address in range(PIC16F877A_PROGRAM_WORDS)
        if reference.program_words[address] != controller.program_words[address]
    }
    if program_diffs != EXPECTED_INCIDENT_PROGRAM_DIFFS:
        raise ValueError(
            "controller program differences are not the three proven byte-swapped "
            "relocated reset-vector words"
        )

    output_memory = dict(donor.intel_hex.memory)
    preserved_byte_ranges = (
        range(0x4000, 0x4008),  # User ID words 0x2000-0x2003
        range(0x4200, 0x4400),  # data EEPROM words 0x2100-0x21FF
    )
    for byte_range in preserved_byte_ranges:
        for address in byte_range:
            if address not in controller.intel_hex.memory:
                raise ValueError(f"controller dump lacks byte 0x{address:04X}")
            output_memory[address] = controller.intel_hex.memory[address]

    output_bytes = serialize_intel_hex(output_memory)
    output = FirmwareImage.parse(
        output_bytes,
        filename="UNQUALIFIED_206_PROGRAM_WITH_202_FORMAT04_DATA_DO_NOT_PROGRAM.hex",
    )
    _require_complete(output, "generated hybrid candidate")
    output_inspection = inspect_pic16f877a_dump(output)
    donor_inspection = inspect_pic16f877a_dump(donor)
    controller_inspection = inspect_pic16f877a_dump(controller)
    section_checks = {
        "program_matches_authenticated_206_donor": (
            dict(output.program_words) == dict(donor.program_words)
        ),
        "configuration_matches_authenticated_206_donor": (
            output.configuration_word == donor.configuration_word
        ),
        "eeprom_matches_controller_dump": (
            dict(output.eeprom_words) == dict(controller.eeprom_words)
        ),
        "user_ids_match_controller_dump": (
            dict(output.user_id_words) == dict(controller.user_id_words)
        ),
        "mapped_byte_set_matches_full_donor": (
            set(output.intel_hex.memory) == set(donor.intel_hex.memory)
        ),
        "code_protection_checks_pass": output_inspection.safe_read,
    }
    if not all(section_checks.values()):
        raise ValueError(f"generated hybrid candidate failed section checks: {section_checks}")

    output_sha256 = hashlib.sha256(output_bytes).hexdigest()
    manifest: dict[str, object] = {
        "schema": "openmaxfire.unqualified-pickit-hybrid.v1",
        "target": "PIC16F877A",
        "operation": "offline Intel HEX construction only; no hardware was accessed",
        "status": "unqualified_experimental_candidate",
        "safe_to_import_in_ipe": False,
        "programming_authorized": False,
        "warnings": [
            "DO NOT import this hybrid into IPE or any programmer",
            "DO NOT program or operate a controller from this hybrid",
            "2.06 application code expects EEPROM format 05, but the preserved controller data is format 04",
            "serial 5215 recovery used the exact complete 2.02 image, not this constructed hybrid",
        ],
        "section_sources": {
            "program_memory": "hash-pinned full 2.06 PICkit donor",
            "configuration_word": "hash-pinned full 2.06 PICkit donor",
            "data_eeprom": "controller pre-recovery readback",
            "user_ids": "controller pre-recovery readback",
        },
        "inputs": {
            "donor": {"path": str(donor_path), "sha256": donor.sha256},
            "reference": {"path": str(reference_path), "sha256": reference.sha256},
            "controller_dump": {
                "path": str(controller_path),
                "sha256": controller.sha256,
            },
        },
        "incident_program_differences": [
            {
                "word_address": f"0x{address:04X}",
                "reference": f"0x{before:04X}",
                "readback": f"0x{after:04X}",
            }
            for address, (before, after) in sorted(program_diffs.items())
        ],
        "output": {
            "sha256": output_sha256,
            "program_sha256": output_inspection.program_sha256,
            "eeprom_sha256": output_inspection.eeprom_sha256,
            "user_ids_sha256": output_inspection.user_ids_sha256,
            "configuration_word": f"0x{output.configuration_word:04X}",
            "program_words": len(output.program_words),
            "eeprom_bytes": len(output.eeprom_words),
            "user_id_words": len(output.user_id_words),
        },
        "expected_section_hashes": {
            "program_from_donor": donor_inspection.program_sha256,
            "eeprom_from_controller": controller_inspection.eeprom_sha256,
            "user_ids_from_controller": controller_inspection.user_ids_sha256,
        },
        "verification": section_checks,
    }
    return output_bytes, manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor", required=True, type=Path)
    parser.add_argument("--reference", required=True, type=Path)
    parser.add_argument("--controller-dump", required=True, type=Path)
    parser.add_argument("--expected-controller-sha256", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument(
        "--acknowledge-unqualified-analysis-only",
        action="store_true",
        help=(
            "required to emit the hybrid; confirms it will not be imported, "
            "programmed, or operated"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if not args.acknowledge_unqualified_analysis_only:
            raise ValueError(
                "refusing to emit the unqualified format-04/2.06 hybrid without "
                "--acknowledge-unqualified-analysis-only"
            )
        if args.output.exists() or args.manifest.exists():
            raise ValueError("output and manifest paths must both be new")
        output_bytes, manifest = build_unqualified_candidate(
            donor_path=args.donor,
            reference_path=args.reference,
            controller_path=args.controller_dump,
            expected_controller_sha256=args.expected_controller_sha256,
        )
        manifest["output"]["path"] = str(args.output)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("xb") as stream:
            stream.write(output_bytes)
        with args.manifest.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(manifest, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except (OSError, ValueError) as exc:
        print(f"unqualified hybrid build failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
