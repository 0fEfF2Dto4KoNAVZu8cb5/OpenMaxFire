"""High-level OpenMaxFire client.

Version 0.1 deliberately keeps the high-level surface small.  Raw register
writes are available to research tooling, while ordinary users get only the
known front-panel abstraction.  Factory checkout commands are intentionally
not exposed here yet.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass

from .protocol import (
    AddressedResponse,
    ResponseFrame,
    RemoteButton,
    encode_read_register,
    encode_remote_button,
    encode_write_register,
    parse_response_line,
)
from .transport import Transport


@dataclass(frozen=True, slots=True)
class CommandReceipt:
    request: bytes
    response: bytes | None = None
    verified: bool = False


@dataclass(frozen=True, slots=True)
class StoveIdentity:
    """Read-only identity values returned by the controller C-space."""

    probe: int
    data_format: int
    firmware_major: int
    firmware_minor: int
    reserved: int
    version_readback: int

    @property
    def firmware_version(self) -> str:
        return f"{self.firmware_major:X}.{self.firmware_minor:02X}"

    @property
    def recognized(self) -> bool:
        expected = {
            (0x05, 0x02, 0x06, 0x00, 0x21),
            (0x07, 0x02, 0x70, 0x00, 0x02),
            (0x07, 0x02, 0x71, 0x00, 0x00),
        }
        return (
            self.data_format,
            self.firmware_major,
            self.firmware_minor,
            self.reserved,
            self.version_readback,
        ) in expected

    def to_dict(self) -> dict[str, object]:
        values = {
            "CR00": f"{self.probe:02X}",
            "CR08": f"{self.data_format:02X}",
            "CR0B": f"{self.firmware_major:02X}",
            "CR0C": f"{self.firmware_minor:02X}",
            "CR0D": f"{self.reserved:02X}",
            "CR0E": f"{self.version_readback:02X}",
        }
        return {
            "firmware_version": self.firmware_version,
            "data_format": f"{self.data_format:02X}",
            "probe_ok": self.probe == 0,
            "recognized_static_pairing": self.recognized,
            "registers": values,
        }


class MaxFireClient:
    def __init__(self, transport: Transport):
        self.transport = transport

    def send_raw(self, command: bytes) -> CommandReceipt:
        self.transport.write(command)
        return CommandReceipt(request=command)

    def read_register(self, address: int) -> CommandReceipt:
        """Send a register-read request without waiting for a response."""

        return self.send_raw(encode_read_register(address))

    def query_register(
        self,
        address: int,
        *,
        unit: str = "C",
        max_frames: int = 16,
    ) -> AddressedResponse:
        """Read one A/C/D register and ignore interleaved unsolicited frames."""

        if max_frames < 1:
            raise ValueError("max_frames must be at least one")
        self.send_raw(encode_read_register(address, unit=unit))
        for _ in range(max_frames):
            frame = self.receive_response()
            if (
                isinstance(frame, AddressedResponse)
                and frame.unit == unit
                and frame.address == address
            ):
                return frame
        raise TimeoutError(
            f"no matching {unit}R{address:02X} response within {max_frames} frames"
        )

    def identify(self, *, request_delay: float = 0.0) -> StoveIdentity:
        """Run BixCheck's read-only controller identity sequence."""

        if not math.isfinite(request_delay) or request_delay < 0:
            raise ValueError("request_delay must be finite and nonnegative")
        addresses = (0x00, 0x08, 0x0B, 0x0C, 0x0D, 0x0E)
        values: dict[int, int] = {}
        for index, address in enumerate(addresses):
            values[address] = self.query_register(address).value
            if request_delay and index + 1 < len(addresses):
                time.sleep(request_delay)
        return StoveIdentity(
            probe=values[0x00],
            data_format=values[0x08],
            firmware_major=values[0x0B],
            firmware_minor=values[0x0C],
            reserved=values[0x0D],
            version_readback=values[0x0E],
        )

    def read_eeprom(
        self,
        *,
        first: int = 0x00,
        last: int = 0xFF,
        request_delay: float = 0.0,
    ) -> dict[int, int]:
        """Read a contiguous A-space range without issuing any write."""

        if not 0 <= first <= last <= 0xFF:
            raise ValueError("EEPROM range must satisfy 0x00 <= first <= last <= 0xFF")
        if not math.isfinite(request_delay) or request_delay < 0:
            raise ValueError("request_delay must be finite and nonnegative")
        values: dict[int, int] = {}
        for address in range(first, last + 1):
            values[address] = self.query_register(address, unit="A").value
            if request_delay and address < last:
                time.sleep(request_delay)
        return values

    def capture_receive_only(self, duration: float, *, chunk_size: int = 256) -> bytes:
        """Read without transmitting for a bounded duration.

        Opening the underlying serial device can still transition DTR/RTS; see
        :class:`openmaxfire.transport.SerialTransport`.
        """

        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("duration must be greater than zero")
        if chunk_size < 1:
            raise ValueError("chunk_size must be at least one")
        deadline = time.monotonic() + duration
        captured = bytearray()
        while time.monotonic() < deadline:
            captured.extend(self.transport.read(chunk_size))
        return bytes(captured)

    def receive_response(self, max_bytes: int = 255) -> ResponseFrame:
        """Read and strictly parse one CR/LF-terminated response line."""

        line = bytearray()
        while len(line) <= max_bytes:
            value = self.transport.read(1)
            if not value:
                raise TimeoutError("serial response timed out")
            if value in (b"\r", b"\n"):
                if line:
                    return parse_response_line(line)
                continue
            line.extend(value)
        raise ValueError("serial response exceeded receive limit")

    def write_register(self, address: int, value: int) -> CommandReceipt:
        """Research-level raw register write. Use only with a documented map."""

        return self.send_raw(encode_write_register(address, value))

    def remote_button(self, button: RemoteButton) -> CommandReceipt:
        """Send a reconstructed BixCheck front-panel remote-control action.

        WARNING: statically confirmed in BixCheck 5.5.01, but not yet live-tested.
        """

        return self.send_raw(encode_remote_button(button))

    def close(self) -> None:
        self.transport.close()
