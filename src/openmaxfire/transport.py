"""Serial transport for the MaxFire J3 research interface."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Transport(Protocol):
    def write(self, data: bytes) -> None: ...
    def read(self, size: int = 1) -> bytes: ...
    def close(self) -> None: ...


@dataclass(slots=True)
class SerialSettings:
    port: str
    baudrate: int
    timeout: float = 0.25


class SerialTransport:
    """Thin pyserial wrapper for controlled bench research.

    The firmware configures a UART consistent with approximately 38,400 baud
    if the controller oscillator is 20 MHz. Earlier project notes assumed
    19,200 baud. Until a live capture resolves this conflict, callers must
    choose the baud rate explicitly.
    """

    def __init__(self, settings: SerialSettings):
        import serial

        self._serial = serial.Serial(
            port=settings.port,
            baudrate=settings.baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=settings.timeout,
            write_timeout=settings.timeout,
        )

    def write(self, data: bytes) -> None:
        self._serial.write(data)
        self._serial.flush()

    def read(self, size: int = 1) -> bytes:
        return self._serial.read(size)

    def close(self) -> None:
        self._serial.close()
