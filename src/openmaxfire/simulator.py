"""Deterministic API-compatible controller and transport for offline tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .configuration import ConfigurationImage
from .profiles import ControllerProfile, PROFILES_BY_KEY
from .protocol import ProtocolError, RegisterRequest, decode_register_request
from .transport import SerialSettings


def default_eeprom(profile: ControllerProfile) -> bytes:
    raw = bytearray(0x100)
    raw[0x02] = profile.data_format
    raw[0x03:0x0B] = b"SIM00001"
    raw[0x0B:0x13] = b"20260823"
    raw[0x13:0x23] = b"SIMULATED MAXFIR"
    return ConfigurationImage(bytes(raw)).with_checksum().raw


def default_controller_registers(profile: ControllerProfile) -> dict[int, int]:
    return {
        0x00: 0x00,
        0x01: 0x00,
        0x02: 0x00,
        0x03: 0x00,
        0x04: 0x48,
        0x05: 0x00,
        0x06: 0x00,
        0x07: 0x00,
        0x08: profile.data_format,
        0x09: 0x78,
        0x0A: 0x78,
        0x0B: profile.firmware_major,
        0x0C: profile.firmware_minor,
        0x0D: profile.reserved,
        0x0E: profile.version_readback,
    }


@dataclass(slots=True)
class SimulationFaults:
    drop_reads: set[tuple[str, int]] = field(default_factory=set)
    read_overrides: dict[tuple[str, int], int] = field(default_factory=dict)
    malformed_prefix_once: bytes = b""


class SimulatedController:
    """In-memory A/C/D register endpoint with writes disabled by default."""

    def __init__(
        self,
        profile: ControllerProfile | str = "fw271-format07",
        *,
        allow_writes: bool = False,
        controller_registers: Mapping[int, int] | None = None,
        eeprom: bytes | bytearray | memoryview | None = None,
        d_space: Mapping[int, int] | None = None,
        telemetry: Mapping[int, int] | None = None,
        faults: SimulationFaults | None = None,
    ):
        self.profile = (
            PROFILES_BY_KEY[profile] if isinstance(profile, str) else profile
        )
        self.allow_writes = allow_writes
        self.registers: dict[tuple[str, int], int] = {}
        controller = default_controller_registers(self.profile)
        if controller_registers:
            controller.update(controller_registers)
        self.registers.update({("C", address): value for address, value in controller.items()})
        eeprom_raw = default_eeprom(self.profile) if eeprom is None else bytes(eeprom)
        if len(eeprom_raw) != 0x100:
            raise ValueError("simulated EEPROM must contain exactly 256 bytes")
        self.registers.update(
            {("A", address): value for address, value in enumerate(eeprom_raw)}
        )
        self.registers.update(
            {("D", address): value for address, value in (d_space or {}).items()}
        )
        self.telemetry = {0x08: 0x07, 0x09: 0x43}
        if telemetry:
            self.telemetry.update(telemetry)
        self.faults = faults or SimulationFaults()
        self.requests: list[RegisterRequest] = []

    def handle(self, command: bytes) -> bytes:
        try:
            request = decode_register_request(command)
        except ProtocolError:
            return b"ILOADER-BLOCKED\n"
        self.requests.append(request)
        key = (request.unit, request.address)
        if request.opcode == "R":
            if key in self.faults.drop_reads:
                return b""
            value = self.faults.read_overrides.get(key, self.registers.get(key, 0))
            prefix = self.faults.malformed_prefix_once
            self.faults.malformed_prefix_once = b""
            unsolicited = b""
            if request.unit == "C" and request.address == 0x00:
                unsolicited = b"".join(
                    f"T{index:02x}{item:02x}\n".encode("ascii")
                    for index, item in sorted(self.telemetry.items())
                )
            response = f"{request.unit}R{request.address:02x}{value:02x}\n".encode(
                "ascii"
            )
            return prefix + unsolicited + response
        assert request.value is not None
        if not self.allow_writes:
            return b"IWRITE-BLOCKED\n"
        self.registers[key] = request.value
        if request.unit == "C" and request.address == 0x01:
            raw = bytes(self.registers[("A", address)] for address in range(0x100))
            checksummed = ConfigurationImage(raw).with_checksum().raw
            self.registers[("A", 0x00)] = checksummed[0x00]
            self.registers[("A", 0x01)] = checksummed[0x01]
        if request.unit == "C" and request.address == 0x0E:
            self._apply_remote_button(request.value)
        return f"{request.unit}W{request.address:02x}{request.value:02x}\n".encode(
            "ascii"
        ) + (
            f"T09{self.telemetry[0x09]:02x}\n".encode("ascii")
            if request.unit == "C" and request.address == 0x0E
            else b""
        )

    def _apply_remote_button(self, value: int) -> None:
        state = self.telemetry.get(0x09, 0x43) & 0x7F
        family = (state >> 4) & 0x07
        level = (state & 0x07) + 1 if family in (4, 5) else 4
        if value == 0x11:
            self.telemetry[0x09] = 0x20
        elif value == 0x12:
            if family in (0, 1, 2):
                self.telemetry[0x09] = 0x30
        elif value == 0x14:
            self.telemetry[0x09] = 0x40 | (min(8, level + 1) - 1)
        elif value == 0x18:
            self.telemetry[0x09] = 0x40 | (max(1, level - 1) - 1)


class SimulatedTransport:
    """Implements :class:`openmaxfire.transport.Transport` in memory."""

    def __init__(self, controller: SimulatedController, *, responsive: bool = True):
        self.controller = controller
        self.responsive = responsive
        self.incoming = bytearray()
        self.writes: list[bytes] = []
        self.closed = False

    def write(self, data: bytes) -> None:
        if self.closed:
            raise OSError("simulated transport is closed")
        payload = bytes(data)
        self.writes.append(payload)
        if self.responsive:
            self.incoming.extend(self.controller.handle(payload))

    def read(self, size: int = 1) -> bytes:
        if self.closed:
            raise OSError("simulated transport is closed")
        if size < 1:
            raise ValueError("read size must be positive")
        if not self.incoming:
            return b""
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk

    def queue_incoming(self, data: bytes | bytearray | memoryview) -> None:
        self.incoming.extend(bytes(data))

    def close(self) -> None:
        self.closed = True


class SimulatedTransportFactory:
    """Transport factory suitable for exercising read-only discovery."""

    def __init__(
        self,
        profile: ControllerProfile | str = "fw271-format07",
        *,
        port: str = "SIM0",
    ):
        self.profile = PROFILES_BY_KEY[profile] if isinstance(profile, str) else profile
        self.port = port
        self.settings: list[SerialSettings] = []
        self.transports: list[SimulatedTransport] = []

    def __call__(self, settings: SerialSettings) -> SimulatedTransport:
        self.settings.append(settings)
        responsive = settings.port == self.port and settings.baudrate in self.profile.baudrates
        transport = SimulatedTransport(
            SimulatedController(self.profile), responsive=responsive
        )
        self.transports.append(transport)
        return transport
