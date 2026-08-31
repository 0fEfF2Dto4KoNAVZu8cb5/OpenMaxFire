"""Deterministic API-compatible controller and transport for offline tests."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .configuration import ConfigurationImage
from .firmware import (
    LOADER_CHECKSUM_ACCEPTED_RESPONSE,
    LOADER_CHECKSUM_REJECTED_RESPONSE,
    LOADER_COMPLETE_REQUEST,
    LOADER_COMPLETE_RESPONSE,
    LOADER_FLASH_ROW_WORDS,
    LOADER_IDENTIFY_REQUEST,
    LOADER_IDENTIFY_RESPONSE,
    LOADER_WRITE_FAILED_RESPONSE,
    LOADER_WRITE_VERIFIED_RESPONSE,
    loader_effective_word_address,
)
from .profiles import ControllerProfile, PROFILES_BY_KEY, TelemetryLayout
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
    disconnect_after_requests: int | None = None

    def __post_init__(self) -> None:
        if (
            self.disconnect_after_requests is not None
            and self.disconnect_after_requests < 0
        ):
            raise ValueError("disconnect_after_requests must be nonnegative or None")


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
        self.telemetry = (
            {0x08: 0x00, 0x09: 0x07, 0x0C: 0x20, 0x14: 0x0F, 0x15: 0x0F}
            if self.profile.telemetry_layout is TelemetryLayout.FORMAT_04
            else {0x08: 0x07, 0x09: 0x43}
        )
        if telemetry:
            self.telemetry.update(telemetry)
        self.faults = faults or SimulationFaults()
        self.requests: list[RegisterRequest] = []

    def handle(self, command: bytes) -> bytes:
        if (
            self.faults.disconnect_after_requests is not None
            and len(self.requests) >= self.faults.disconnect_after_requests
        ):
            raise OSError("simulated controller disconnected")
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
        state_index = (
            0x0C
            if self.profile.telemetry_layout is TelemetryLayout.FORMAT_04
            else 0x09
        )
        return f"{request.unit}W{request.address:02x}{request.value:02x}\n".encode(
            "ascii"
        ) + (
            f"T{state_index:02x}{self.telemetry[state_index]:02x}\n".encode("ascii")
            if request.unit == "C" and request.address == 0x0E
            else b""
        )

    def _apply_remote_button(self, value: int) -> None:
        state_index = (
            0x0C
            if self.profile.telemetry_layout is TelemetryLayout.FORMAT_04
            else 0x09
        )
        state = self.telemetry.get(state_index, 0x43) & 0x7F
        family = (state >> 4) & 0x07
        level = (state & 0x07) + 1 if family in (4, 5) else 4
        if value == 0x11:
            self.telemetry[state_index] = 0x20
        elif value == 0x12:
            if family in (0, 1, 2):
                self.telemetry[state_index] = 0x30
        elif value == 0x14:
            self.telemetry[state_index] = 0x40 | (min(8, level + 1) - 1)
        elif value == 0x18:
            self.telemetry[state_index] = 0x40 | (max(1, level - 1) - 1)


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


@dataclass(slots=True)
class SimulatedLoaderFaults:
    """Deterministic fault injection for the isolated loader simulator."""

    identify_failures: int = 0
    checksum_failures: dict[int, int] = field(default_factory=dict)
    write_failures: dict[int, int] = field(default_factory=dict)
    row_write_failures: dict[int, int] = field(default_factory=dict)
    # Backward-compatible generic unexpected-response injection.
    block_failures: dict[int, int] = field(default_factory=dict)
    completion_failures: int = 0
    reconnect_failures: int = 0
    disconnect_after_blocks: int | None = None
    # Deliberately models corruption after the loader's local readback so the
    # host-side final simulator comparison remains independently testable.
    corrupt_word_address: int | None = None

    def __post_init__(self) -> None:
        if (
            self.identify_failures < 0
            or self.completion_failures < 0
            or self.reconnect_failures < 0
        ):
            raise ValueError("loader failure counts must be nonnegative")
        fault_maps = (
            self.checksum_failures,
            self.write_failures,
            self.row_write_failures,
            self.block_failures,
        )
        if any(
            address < 0 or failures < 0
            for fault_map in fault_maps
            for address, failures in fault_map.items()
        ):
            raise ValueError("loader block/row fault values must be nonnegative")
        if self.disconnect_after_blocks is not None and self.disconnect_after_blocks < 0:
            raise ValueError("disconnect_after_blocks must be nonnegative or None")


class SimulatedLoaderTransport:
    """Strict binary-loader endpoint for offline state-machine validation.

    This simulator does not model ``CW0FC4`` or a boot window.  It starts in
    loader mode by construction and accepts only the reconstructed binary
    identify, program-block, and completion frames.
    """

    # Safety-sensitive callers use this explicit marker to distinguish the
    # deterministic in-process model from every physical transport.  Physical
    # transports must never set or inherit it.
    simulation_only = True

    def __init__(
        self,
        *,
        faults: SimulatedLoaderFaults | None = None,
        initial_program_words: Mapping[int, int] | None = None,
    ):
        self.faults = faults or SimulatedLoaderFaults()
        self.incoming = bytearray()
        self.writes: list[bytes] = []
        initial = dict(initial_program_words or {})
        if any(
            isinstance(address, bool)
            or not isinstance(address, int)
            or not 0 <= address < 0x2000
            or isinstance(value, bool)
            or not isinstance(value, int)
            or not 0 <= value <= 0x3FFF
            for address, value in initial.items()
        ):
            raise ValueError(
                "initial program words must map 0x0000-0x1FFF to PIC14 values"
            )
        self.initial_flash_words: dict[int, int] = initial.copy()
        self.flash_words: dict[int, int] = initial.copy()
        self.programmed_words: dict[int, int] = {}
        self.row_write_attempts: dict[int, int] = {}
        self.preserved_neighbors_verified = True
        self.blocks_accepted = 0
        self.identified = False
        self.completed = False
        self.application_running = False
        self.application_reconnected = False
        self.closed = False

    def write(self, data: bytes) -> None:
        if self.closed:
            raise OSError("simulated loader transport is closed")
        if (
            self.faults.disconnect_after_blocks is not None
            and self.blocks_accepted >= self.faults.disconnect_after_blocks
        ):
            raise OSError("simulated loader disconnected")
        payload = bytes(data)
        self.writes.append(payload)
        if payload == LOADER_IDENTIFY_REQUEST:
            if self.faults.identify_failures:
                self.faults.identify_failures -= 1
                self.incoming.extend(b"\x00")
            else:
                self.identified = True
                self.incoming.extend(LOADER_IDENTIFY_RESPONSE)
            return
        if payload == LOADER_COMPLETE_REQUEST:
            if not self.identified:
                self.incoming.extend(b"\x00")
            elif self.faults.completion_failures:
                self.faults.completion_failures -= 1
                self.incoming.extend(b"\x00")
            else:
                self.completed = True
                self.identified = False
                self.application_running = True
                self.incoming.extend(LOADER_COMPLETE_RESPONSE)
            return
        self._program_block(payload)

    def _program_block(self, frame: bytes) -> None:
        if not self.identified or len(frame) < 7 or frame[0] != 0xE3:
            self.incoming.extend(b"\x00")
            return
        word_address = (frame[1] << 8) | frame[2]
        byte_count = frame[3]
        checksum = frame[4]
        data = frame[5:]
        structurally_valid = (
            2 <= byte_count <= 32
            and byte_count % 2 == 0
            and len(data) == byte_count
            and word_address + byte_count // 2 <= 0x2000
        )
        if not structurally_valid:
            self.incoming.extend(b"\x00")
            return

        checksum_failures = self.faults.checksum_failures.get(word_address, 0)
        if sum(data) & 0xFF != checksum or checksum_failures:
            if checksum_failures:
                self.faults.checksum_failures[word_address] = checksum_failures - 1
            self.incoming.extend(LOADER_CHECKSUM_REJECTED_RESPONSE)
            return

        generic_failures = self.faults.block_failures.get(word_address, 0)
        if generic_failures:
            self.faults.block_failures[word_address] = generic_failures - 1
            self.incoming.extend(b"\x00")
            return

        self.incoming.extend(LOADER_CHECKSUM_ACCEPTED_RESPONSE)
        write_failures = self.faults.write_failures.get(word_address, 0)
        if write_failures:
            self.faults.write_failures[word_address] = write_failures - 1
            self.incoming.extend(LOADER_WRITE_FAILED_RESPONSE)
            return

        updates_by_row: dict[int, dict[int, int]] = {}
        for offset in range(0, byte_count, 2):
            source_address = word_address + offset // 2
            target_address = loader_effective_word_address(source_address)
            if target_address is None:
                continue
            # The preserved BixCheck downloader sends PIC14 words high byte
            # first.  Keeping this decode independent of Intel HEX byte order
            # prevents the simulator from blessing a byte-swapped host.
            value = (data[offset] << 8) | data[offset + 1]
            row_address = target_address - (target_address % LOADER_FLASH_ROW_WORDS)
            updates_by_row.setdefault(row_address, {})[target_address] = value

        for row_address, updates in sorted(updates_by_row.items()):
            if not self._write_flash_row(row_address, updates):
                self.incoming.extend(LOADER_WRITE_FAILED_RESPONSE)
                return

        current_targets: set[int] = set()
        for updates in updates_by_row.values():
            self.programmed_words.update(updates)
            current_targets.update(updates)
        corrupt_address = self.faults.corrupt_word_address
        if corrupt_address is not None and corrupt_address in current_targets:
            corrupted = self.programmed_words[corrupt_address] ^ 1
            self.programmed_words[corrupt_address] = corrupted
            self.flash_words[corrupt_address] = corrupted
        self.blocks_accepted += 1
        self.incoming.extend(LOADER_WRITE_VERIFIED_RESPONSE)

    def _write_flash_row(self, row_address: int, updates: Mapping[int, int]) -> bool:
        before = {
            address: self.flash_words.get(address, 0x3FFF)
            for address in range(row_address, row_address + LOADER_FLASH_ROW_WORDS)
        }
        intended = dict(before)
        intended.update(updates)
        for _ in range(2):
            self.row_write_attempts[row_address] = (
                self.row_write_attempts.get(row_address, 0) + 1
            )
            failures = self.faults.row_write_failures.get(row_address, 0)
            if failures:
                self.faults.row_write_failures[row_address] = failures - 1
                continue
            self.flash_words.update(intended)
            if all(self.flash_words.get(address, 0x3FFF) == value for address, value in intended.items()):
                for address, value in before.items():
                    if address not in updates and self.flash_words[address] != value:
                        self.preserved_neighbors_verified = False
                return True
        return False

    def reconnect_application(self) -> bool:
        """Model a close/reopen after the loader's application handoff."""

        if not self.application_running:
            return False
        if self.faults.reconnect_failures:
            self.faults.reconnect_failures -= 1
            return False
        self.application_reconnected = True
        return True

    def read(self, size: int = 1) -> bytes:
        if self.closed:
            raise OSError("simulated loader transport is closed")
        if size < 1:
            raise ValueError("read size must be positive")
        if not self.incoming:
            return b""
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk

    def read_available(self) -> bytes:
        data = bytes(self.incoming)
        self.incoming.clear()
        return data

    def close(self) -> None:
        self.closed = True


class SimulatedFlashSessionTransport:
    """One-handle application/rehearsal/programming/application lifecycle.

    This is a deterministic CLI test fixture, not an electrical or timing
    model.  The first loader entry is treated as a zero-block rehearsal; a
    later entry accepts the real plan and hands off to the target profile.
    """

    simulation_only = True

    def __init__(
        self,
        current_profile: ControllerProfile | str,
        target_profile: ControllerProfile | str,
        *,
        eeprom: bytes | bytearray | memoryview | None = None,
        rehearsal_faults: SimulatedLoaderFaults | None = None,
        programming_faults: SimulatedLoaderFaults | None = None,
        post_eeprom: bytes | bytearray | memoryview | None = None,
        skip_rehearsal: bool = False,
        emit_application_telemetry: bool = True,
        port: str = "SIM0",
        baudrate: int = 9600,
        timeout: float = 0.50,
    ):
        self.current_profile = (
            PROFILES_BY_KEY[current_profile]
            if isinstance(current_profile, str)
            else current_profile
        )
        self.target_profile = (
            PROFILES_BY_KEY[target_profile]
            if isinstance(target_profile, str)
            else target_profile
        )
        baseline = default_eeprom(self.current_profile) if eeprom is None else bytes(eeprom)
        self.before = SimulatedController(self.current_profile, eeprom=baseline)
        self.after = SimulatedController(
            self.target_profile,
            eeprom=baseline if post_eeprom is None else bytes(post_eeprom),
        )
        self.rehearsal_faults = rehearsal_faults or SimulatedLoaderFaults()
        self.programming_faults = programming_faults or SimulatedLoaderFaults()
        self.settings = SerialSettings(port, baudrate, timeout, exclusive=True)
        self.incoming = bytearray()
        self.writes: list[bytes] = []
        self.loader_entries = 1 if skip_rehearsal else 0
        self.emit_application_telemetry = emit_application_telemetry
        self.loader: SimulatedLoaderTransport | None = None
        self.mode = "application_before"
        self.closed = False
        self.break_active = False
        self.break_states: list[bool] = []

    def set_baudrate(self, baudrate: int) -> None:
        self.settings = SerialSettings(
            self.settings.port,
            baudrate,
            self.settings.timeout,
            self.settings.exclusive,
        )

    def set_timeout(self, timeout: float) -> None:
        self.settings = SerialSettings(
            self.settings.port,
            self.settings.baudrate,
            timeout,
            self.settings.exclusive,
        )

    def set_break(self, active: bool) -> None:
        if not isinstance(active, bool):
            raise TypeError("active must be a boolean")
        self.break_active = active
        self.break_states.append(active)

    def _enter_loader(self) -> None:
        self.loader_entries += 1
        faults = (
            self.rehearsal_faults
            if self.loader_entries == 1
            else self.programming_faults
        )
        self.loader = SimulatedLoaderTransport(faults=faults)
        self.mode = "loader"

    def write(self, data: bytes) -> None:
        if self.closed:
            raise OSError("simulated flash-session transport is closed")
        if self.break_active:
            raise OSError("cannot transmit while simulated UART BREAK is active")
        payload = bytes(data)
        self.writes.append(payload)
        if self.mode != "loader" and payload == LOADER_IDENTIFY_REQUEST:
            self._enter_loader()
        if self.mode == "loader":
            assert self.loader is not None
            self.loader.write(payload)
            self.incoming.extend(self.loader.read_available())
            if payload == LOADER_COMPLETE_REQUEST and self.loader.application_running:
                self.mode = (
                    "application_before"
                    if self.loader_entries == 1
                    else "application_after"
                )
                # Real controllers emit periodic application telemetry without
                # a host request.  The live flasher waits for this passive
                # readiness evidence before it is allowed to send CR00.
                if self.emit_application_telemetry:
                    self.incoming.extend(b"T0800\n")
            return
        controller = self.after if self.mode == "application_after" else self.before
        self.incoming.extend(controller.handle(payload))

    def read(self, size: int = 1) -> bytes:
        if self.closed:
            raise OSError("simulated flash-session transport is closed")
        if size < 1:
            raise ValueError("read size must be positive")
        if not self.incoming:
            return b""
        chunk = bytes(self.incoming[:size])
        del self.incoming[:size]
        return chunk

    def read_available(self) -> bytes:
        data = bytes(self.incoming)
        self.incoming.clear()
        return data

    def close(self) -> None:
        self.closed = True
