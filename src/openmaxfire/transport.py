"""Cross-platform serial transport for the MaxFire J3 research interface."""

from __future__ import annotations

import json
import math
import platform
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Protocol, TextIO


class Transport(Protocol):
    def write(self, data: bytes) -> None: ...
    def read(self, size: int = 1) -> bytes: ...
    def close(self) -> None: ...


class TrafficRecorder(Protocol):
    """Minimal sink accepted by :class:`RecordingTransport`."""

    def record(self, direction: str, data: bytes) -> None: ...
    def close(self) -> None: ...


@dataclass(frozen=True, slots=True)
class SerialPortInfo:
    """Portable subset of pyserial's platform-specific port metadata."""

    device: str
    description: str | None = None
    hardware_id: str | None = None
    vid: int | None = None
    pid: int | None = None
    serial_number: str | None = None
    manufacturer: str | None = None
    product: str | None = None
    location: str | None = None

    @property
    def usb_id(self) -> str | None:
        if self.vid is None or self.pid is None:
            return None
        return f"{self.vid:04X}:{self.pid:04X}"

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["usb_id"] = self.usb_id
        return result


def _clean_port_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _serial_port_info(port: object) -> SerialPortInfo:
    return SerialPortInfo(
        device=str(getattr(port, "device")),
        description=_clean_port_text(getattr(port, "description", None)),
        hardware_id=_clean_port_text(getattr(port, "hwid", None)),
        vid=getattr(port, "vid", None),
        pid=getattr(port, "pid", None),
        serial_number=_clean_port_text(getattr(port, "serial_number", None)),
        manufacturer=_clean_port_text(getattr(port, "manufacturer", None)),
        product=_clean_port_text(getattr(port, "product", None)),
        location=_clean_port_text(getattr(port, "location", None)),
    )


def list_serial_ports() -> list[SerialPortInfo]:
    """Return serial ports using the same API on Windows, Linux, and macOS."""

    from serial.tools import list_ports

    return sorted(
        (_serial_port_info(port) for port in list_ports.comports()),
        key=lambda item: item.device.casefold(),
    )


@dataclass(frozen=True, slots=True)
class SerialSettings:
    port: str
    baudrate: int
    timeout: float = 0.25

    def __post_init__(self) -> None:
        if not isinstance(self.port, str) or not self.port.strip():
            raise ValueError("port must be a non-empty serial device name")
        if not isinstance(self.baudrate, int) or self.baudrate <= 0:
            raise ValueError("baudrate must be a positive integer")
        if (
            not isinstance(self.timeout, (int, float))
            or not math.isfinite(self.timeout)
            or self.timeout <= 0
        ):
            raise ValueError("timeout must be greater than zero")


class SerialTransport:
    """Thin pyserial wrapper for controlled cross-platform bench research.

    BixCheck uses 8N1, enables DTR/RTS, and disables hardware and software flow
    control. BixCheck 5.0.21 selects 9,600 baud; 5.5.00/5.5.01 select either
    9,600 or 19,200 baud. Firmware 2.02 and the J3 TTL-UART path have been
    live-validated at 9,600 baud; callers still choose the rate explicitly
    because preserved later firmware generations have not been live-tested.

    Opening a serial device can transition DTR/RTS even when no payload is
    transmitted. A receive-only capture is therefore not an electrically
    passive measurement.
    """

    def __init__(self, settings: SerialSettings):
        import serial

        self.settings = settings
        self._serial = serial.Serial(
            port=settings.port,
            baudrate=settings.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=settings.timeout,
            write_timeout=settings.timeout,
            xonxoff=False,
            rtscts=False,
            dsrdtr=False,
        )

    def write(self, data: bytes) -> None:
        self._serial.write(data)
        self._serial.flush()

    def read(self, size: int = 1) -> bytes:
        return self._serial.read(size)

    def close(self) -> None:
        self._serial.close()


def _display_bytes(data: bytes) -> str:
    return "".join(
        chr(value) if 0x20 <= value <= 0x7E else f"\\x{value:02X}"
        for value in data
    )


class JsonlTrafficRecorder:
    """Durable per-read/per-write serial transcript with monotonic timing."""

    SCHEMA = "openmaxfire.serial-capture.v1"

    def __init__(
        self,
        path: str | Path,
        *,
        metadata: Mapping[str, object] | None = None,
        overwrite: bool = False,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream: TextIO = self.path.open(
            "w" if overwrite else "x", encoding="utf-8", newline="\n"
        )
        self._sequence = 0
        self._write(
            {
                "schema": self.SCHEMA,
                "event": "session",
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "platform": platform.platform(),
                "python": sys.version.split()[0],
                "metadata": dict(metadata or {}),
            }
        )

    def _write(self, event: Mapping[str, object]) -> None:
        self._stream.write(json.dumps(dict(event), sort_keys=True) + "\n")
        self._stream.flush()

    def record(self, direction: str, data: bytes) -> None:
        if direction not in ("tx", "rx"):
            raise ValueError("direction must be 'tx' or 'rx'")
        if not data:
            return
        self._sequence += 1
        self._write(
            {
                "schema": self.SCHEMA,
                "event": "traffic",
                "sequence": self._sequence,
                "created_utc": datetime.now(timezone.utc).isoformat(),
                "monotonic_ns": time.monotonic_ns(),
                "direction": direction,
                "byte_count": len(data),
                "data_hex": data.hex(" ").upper(),
                "data_ascii": _display_bytes(data),
            }
        )

    def close(self) -> None:
        if not self._stream.closed:
            self._stream.close()


class RecordingTransport:
    """Transport decorator that records exact TX/RX chunks without altering them."""

    def __init__(self, transport: Transport, recorder: TrafficRecorder):
        self.transport = transport
        self.recorder = recorder

    def write(self, data: bytes) -> None:
        self.recorder.record("tx", data)
        self.transport.write(data)

    def read(self, size: int = 1) -> bytes:
        data = self.transport.read(size)
        self.recorder.record("rx", data)
        return data

    def close(self) -> None:
        try:
            self.transport.close()
        finally:
            self.recorder.close()
