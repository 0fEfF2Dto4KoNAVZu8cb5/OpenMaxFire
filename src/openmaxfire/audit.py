"""Presentation-neutral, exact-byte audit trails for API sessions.

The audit layer is deliberately transport-level: it records the bytes actually
offered to and returned by a transport, including malformed and unsolicited
traffic.  Higher layers can retain a whole session or a digestable span without
depending on a CLI log-file convention.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, TextIO


def _display_bytes(data: bytes) -> str:
    return "".join(
        chr(value) if 0x20 <= value <= 0x7E else f"\\x{value:02X}"
        for value in data
    )


@dataclass(frozen=True, slots=True)
class AuditEvent:
    sequence: int
    created_utc: str
    monotonic_ns: int
    direction: str
    data: bytes

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": AuditTrail.SCHEMA,
            "event": "traffic",
            "sequence": self.sequence,
            "created_utc": self.created_utc,
            "monotonic_ns": self.monotonic_ns,
            "direction": self.direction,
            "byte_count": len(self.data),
            "data_hex": self.data.hex(" ").upper(),
            "data_ascii": _display_bytes(self.data),
        }


@dataclass(frozen=True, slots=True)
class AuditSpan:
    first_sequence: int | None
    last_sequence: int | None
    event_count: int
    tx_bytes: int
    rx_bytes: int
    sha256: str

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": "openmaxfire.audit-span.v1",
            "first_sequence": self.first_sequence,
            "last_sequence": self.last_sequence,
            "event_count": self.event_count,
            "tx_bytes": self.tx_bytes,
            "rx_bytes": self.rx_bytes,
            "sha256": self.sha256,
        }


class AuditTrail:
    """In-memory audit trail with optional flush-on-event JSONL persistence."""

    SCHEMA = "openmaxfire.serial-audit.v1"

    def __init__(
        self,
        path: str | Path | None = None,
        *,
        metadata: Mapping[str, object] | None = None,
        overwrite: bool = False,
        session_id: str | None = None,
    ):
        self.path = Path(path) if path is not None else None
        self.metadata = dict(metadata or {})
        self.session_id = session_id or str(uuid.uuid4())
        self.created_utc = datetime.now(timezone.utc).isoformat()
        self._events: list[AuditEvent] = []
        self._stream: TextIO | None = None
        self._closed = False
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self._stream = self.path.open(
                "w" if overwrite else "x", encoding="utf-8", newline="\n"
            )
            self._write(self.session_document())

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    @property
    def closed(self) -> bool:
        return self._closed

    def session_document(self) -> dict[str, object]:
        return {
            "schema": self.SCHEMA,
            "event": "session",
            "session_id": self.session_id,
            "created_utc": self.created_utc,
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "metadata": dict(self.metadata),
        }

    def _write(self, event: Mapping[str, object]) -> None:
        if self._stream is not None:
            self._stream.write(json.dumps(dict(event), sort_keys=True) + "\n")
            self._stream.flush()

    def record(self, direction: str, data: bytes) -> None:
        if self._closed:
            raise RuntimeError("audit trail is closed")
        if direction not in ("tx", "rx"):
            raise ValueError("direction must be 'tx' or 'rx'")
        payload = bytes(data)
        if not payload:
            return
        event = AuditEvent(
            sequence=len(self._events) + 1,
            created_utc=datetime.now(timezone.utc).isoformat(),
            monotonic_ns=time.monotonic_ns(),
            direction=direction,
            data=payload,
        )
        self._events.append(event)
        self._write(event.to_dict())

    def checkpoint(self) -> int:
        """Return a stable marker suitable for a later :meth:`span` call."""

        return len(self._events)

    def span(self, checkpoint: int = 0) -> AuditSpan:
        if isinstance(checkpoint, bool) or not isinstance(checkpoint, int):
            raise TypeError("checkpoint must be an integer")
        if not 0 <= checkpoint <= len(self._events):
            raise ValueError("checkpoint is outside this audit trail")
        selected = self._events[checkpoint:]
        digest = hashlib.sha256()
        for event in selected:
            direction = b"T" if event.direction == "tx" else b"R"
            digest.update(direction)
            digest.update(len(event.data).to_bytes(8, "big"))
            digest.update(event.data)
        return AuditSpan(
            first_sequence=selected[0].sequence if selected else None,
            last_sequence=selected[-1].sequence if selected else None,
            event_count=len(selected),
            tx_bytes=sum(len(item.data) for item in selected if item.direction == "tx"),
            rx_bytes=sum(len(item.data) for item in selected if item.direction == "rx"),
            sha256=digest.hexdigest(),
        )

    def to_dict(self) -> dict[str, object]:
        return {
            **self.session_document(),
            "events": [event.to_dict() for event in self._events],
            "span": self.span().to_dict(),
            "closed": self._closed,
        }

    def write_jsonl(self, path: str | Path, *, overwrite: bool = False) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open(
            "w" if overwrite else "x", encoding="utf-8", newline="\n"
        ) as stream:
            stream.write(json.dumps(self.session_document(), sort_keys=True) + "\n")
            for event in self._events:
                stream.write(json.dumps(event.to_dict(), sort_keys=True) + "\n")
        return destination

    def close(self) -> None:
        if not self._closed:
            if self._stream is not None:
                self._stream.close()
            self._closed = True


__all__ = ["AuditEvent", "AuditSpan", "AuditTrail"]
