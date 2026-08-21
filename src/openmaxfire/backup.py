"""Read-only configuration-backup artifacts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping

from . import __version__
from .client import StoveIdentity
from .protocol import calculate_configuration_checksum


BACKUP_SCHEMA = "openmaxfire.eeprom-backup.v1"


def _fixed_ascii(values: Mapping[int, int], first: int, length: int) -> str:
    raw = bytes(values[address] for address in range(first, first + length))
    return raw.decode("ascii", errors="backslashreplace").rstrip("\0\xff ")


def build_eeprom_backup(
    identity: StoveIdentity,
    values: Mapping[int, int],
    *,
    port: str,
    baudrate: int,
    created_utc: str | None = None,
) -> dict[str, object]:
    """Build a complete, lossless A00-AFF backup with checksum diagnostics."""

    missing = [address for address in range(0x100) if address not in values]
    if missing:
        raise ValueError(f"EEPROM backup is missing A{missing[0]:02X}")
    normalized: dict[int, int] = {}
    for address in range(0x100):
        value = values[address]
        if not isinstance(value, int) or not 0 <= value <= 0xFF:
            raise ValueError(f"EEPROM A{address:02X} is not a byte")
        normalized[address] = value

    stored_checksum = (normalized[0x00] << 8) | normalized[0x01]
    eeprom_format = normalized[0x02]
    try:
        calculated_checksum = calculate_configuration_checksum(eeprom_format, normalized)
    except ValueError:
        calculated_checksum = None

    return {
        "schema": BACKUP_SCHEMA,
        "created_utc": created_utc or datetime.now(timezone.utc).isoformat(),
        "openmaxfire_version": __version__,
        "connection": {"port": port, "baudrate": baudrate},
        "controller_identity": identity.to_dict(),
        "individualization": {
            "data_format": f"{eeprom_format:02X}",
            "controller_and_eeprom_format_match": eeprom_format == identity.data_format,
            "serial_number": _fixed_ascii(normalized, 0x03, 8),
            "production_date": _fixed_ascii(normalized, 0x0B, 8),
            "model_name": _fixed_ascii(normalized, 0x13, 16),
        },
        "checksum": {
            "stored": f"{stored_checksum:04X}",
            "calculated": (
                f"{calculated_checksum:04X}" if calculated_checksum is not None else None
            ),
            "matches": (
                stored_checksum == calculated_checksum
                if calculated_checksum is not None
                else None
            ),
        },
        "eeprom": {f"A{address:02X}": f"{normalized[address]:02X}" for address in range(0x100)},
        "raw_hex": bytes(normalized[address] for address in range(0x100)).hex().upper(),
        "evidence_boundary": (
            "Read-only artifact from statically reconstructed protocol; physical J3 behavior "
            "and this controller's values require live validation."
        ),
    }


def save_json_document(
    document: Mapping[str, object],
    path: str | Path,
    *,
    overwrite: bool = False,
) -> Path:
    """Write a JSON artifact without silently replacing an existing backup."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open(
        "w" if overwrite else "x", encoding="utf-8", newline="\n"
    ) as stream:
        json.dump(dict(document), stream, indent=2, sort_keys=True)
        stream.write("\n")
    return destination
