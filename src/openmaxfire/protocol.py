"""Low-level MaxFire 110/115 J3 protocol primitives.

The framing and transformations here were reconstructed from all three
preserved BixCheck executables. Register reads and the remote front-panel
OFF/ON/UP/DOWN writes have also been live-validated on firmware 2.02/data
format 04. Other writes retain their narrower static or emulator evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import Mapping, TypeAlias


CONTROLLER_PREFIX = "C"
READ_OPCODE = "R"
WRITE_OPCODE = "W"
ADDRESSED_UNITS = frozenset("ACD")
CONTROL_PREFIXES = frozenset((0x01, 0x02, 0x03))

# Reconstructed from BixCheck 5.5.01 and live-validated on firmware 2.02:
# remote front-panel actions are writes to controller register 0x0E.
REMOTE_BUTTON_REGISTER = 0x0E


class RemoteButton(IntEnum):
    """Values stored in BixCheck's Bixby110RCButtonData table."""

    OFF = 0x11
    ON = 0x12
    UP = 0x14
    DOWN = 0x18


class ProtocolError(ValueError):
    """A serial frame does not match the statically reconstructed grammar."""


@dataclass(frozen=True, slots=True)
class RegisterRequest:
    unit: str
    opcode: str
    address: int
    value: int | None = None


@dataclass(frozen=True, slots=True)
class AddressedResponse:
    """Six-character A/C/D response: unit, operation, address, and value."""

    unit: str
    opcode: str
    address: int
    value: int
    raw: bytes


@dataclass(frozen=True, slots=True)
class TelemetryResponse:
    """A T response carrying one byte, or a legacy two-byte host form.

    The recovered 2.06/2.70/2.71 firmware sender emits one byte per physical
    ``Txxvv`` line.  The seven-character form remains accepted because the
    BixCheck receive path can represent two adjacent bytes that way and older
    OpenMaxFire documentation exposed it as a compatibility grammar.
    """

    index: int
    values: tuple[int, ...]
    raw: bytes


@dataclass(frozen=True, slots=True)
class StatusResponse:
    """An M/I response whose inner payload is not yet semantically decoded."""

    kind: str
    payload: bytes
    raw: bytes


@dataclass(frozen=True, slots=True)
class OperatingState:
    """Decoded BixCheck display meaning for telemetry byte T09."""

    raw: int
    normalized: int
    family: int
    phase: str
    label: str
    level: int | None = None
    thermostat: bool = False


@dataclass(frozen=True, slots=True)
class IgniterState:
    """Decoded BixCheck display meaning for telemetry byte T08."""

    raw: int
    code: int
    label: str


ResponseFrame: TypeAlias = AddressedResponse | TelemetryResponse | StatusResponse


# The firmware transmits both halves as separate five-character frames.  The
# BixCheck update routine stores the first byte, shifts it left eight bits, and
# adds the following byte when the second index arrives.
TELEMETRY_WORD_PAIRS: Mapping[int, str] = {
    0x0A: "ash level",
    0x0C: "ash target",
    0x0E: "feed on time",
    0x10: "feed off time",
    0x1A: "feed cycle table",
    0x1C: "feed cycle calibration",
}


def _byte(value: int, name: str) -> int:
    if not isinstance(value, int) or not 0 <= value <= 0xFF:
        raise ValueError(f"{name} must be an integer from 0x00 to 0xFF")
    return value


def _unit(value: str) -> str:
    if value not in ADDRESSED_UNITS:
        raise ValueError(f"unit must be one of {''.join(sorted(ADDRESSED_UNITS))}")
    return value


def encode_read_register(address: int, *, unit: str = CONTROLLER_PREFIX) -> bytes:
    """Encode a register read as four ASCII bytes with no terminator.

    Example: register 0x0E -> b"CR0E".
    """

    address = _byte(address, "address")
    unit = _unit(unit)
    return f"{unit}{READ_OPCODE}{address:02X}".encode("ascii")


def encode_write_register(
    address: int, value: int, *, unit: str = CONTROLLER_PREFIX
) -> bytes:
    """Encode a register write as six ASCII bytes with no terminator.

    Example: write 0x14 to register 0x0E -> b"CW0E14".
    """

    address = _byte(address, "address")
    value = _byte(value, "value")
    unit = _unit(unit)
    return f"{unit}{WRITE_OPCODE}{address:02X}{value:02X}".encode("ascii")


def encode_remote_button(button: RemoteButton) -> bytes:
    """Encode a reconstructed and firmware-2.02-validated remote-button write."""

    try:
        button = RemoteButton(button)
    except ValueError as exc:
        raise ValueError(f"unknown remote button value: {button!r}") from exc
    return encode_write_register(REMOTE_BUTTON_REGISTER, int(button))


def _uppercase_hex_byte(value: bytes, field: str) -> int:
    if len(value) != 2 or any(item not in b"0123456789ABCDEF" for item in value):
        raise ProtocolError(f"{field} must be two uppercase hexadecimal digits")
    return int(value, 16)


def _incoming_hex_byte(value: bytes, field: str) -> int:
    if len(value) != 2 or any(item not in b"0123456789ABCDEFabcdef" for item in value):
        raise ProtocolError(f"{field} must be two hexadecimal digits")
    return int(value, 16)


def decode_register_request(data: bytes | bytearray | memoryview) -> RegisterRequest:
    """Decode BixCheck's exact four/six-byte, unterminated request grammar."""

    raw = bytes(data)
    if len(raw) not in (4, 6):
        raise ProtocolError("register request must contain exactly 4 or 6 bytes")
    try:
        unit = chr(raw[0])
        opcode = chr(raw[1])
    except (IndexError, ValueError) as exc:
        raise ProtocolError("invalid request header") from exc
    if unit not in ADDRESSED_UNITS:
        raise ProtocolError(f"unsupported request unit: {unit!r}")
    if opcode not in (READ_OPCODE, WRITE_OPCODE):
        raise ProtocolError(f"unsupported request opcode: {opcode!r}")
    expected = 4 if opcode == READ_OPCODE else 6
    if len(raw) != expected:
        raise ProtocolError(f"{opcode} request must contain exactly {expected} bytes")
    address = _uppercase_hex_byte(raw[2:4], "address")
    value = _uppercase_hex_byte(raw[4:6], "value") if opcode == WRITE_OPCODE else None
    return RegisterRequest(unit=unit, opcode=opcode, address=address, value=value)


def parse_response_line(data: bytes | bytearray | memoryview | str) -> ResponseFrame:
    """Parse one CR/LF-delimited BixCheck response line.

    ``scanio`` in the 5.5 executables accepts lower- or uppercase incoming hex,
    strips CR/LF, and re-dispatches leading control bytes 0x01 through 0x03.
    This parser mirrors that grammar while adding length and character checks
    missing from the vendor implementation.
    """

    if isinstance(data, str):
        try:
            raw = data.encode("ascii")
        except UnicodeEncodeError as exc:
            raise ProtocolError("response is not ASCII") from exc
    else:
        raw = bytes(data)
    raw = raw.strip(b"\r\n")
    while raw and raw[0] in CONTROL_PREFIXES:
        raw = raw[1:]
    if not raw:
        raise ProtocolError("empty response")
    if b"\r" in raw or b"\n" in raw:
        raise ProtocolError("response contains an embedded line terminator")

    prefix = chr(raw[0])
    if prefix in ADDRESSED_UNITS:
        if len(raw) != 6:
            raise ProtocolError("addressed response must contain exactly 6 bytes")
        opcode = chr(raw[1])
        if not ("A" <= opcode <= "Z"):
            raise ProtocolError("addressed response opcode must be an uppercase letter")
        return AddressedResponse(
            unit=prefix,
            opcode=opcode,
            address=_incoming_hex_byte(raw[2:4], "address"),
            value=_incoming_hex_byte(raw[4:6], "value"),
            raw=raw,
        )
    if prefix == "T":
        if len(raw) not in (5, 7):
            raise ProtocolError("telemetry response must contain 5 or 7 bytes")
        values = [_incoming_hex_byte(raw[3:5], "telemetry value")]
        if len(raw) == 7:
            values.append(_incoming_hex_byte(raw[5:7], "second telemetry value"))
        return TelemetryResponse(
            index=_incoming_hex_byte(raw[1:3], "telemetry index"),
            values=tuple(values),
            raw=raw,
        )
    if prefix in ("M", "I"):
        if any(item < 0x20 or item > 0x7E for item in raw[1:]):
            raise ProtocolError("status response contains non-printable bytes")
        return StatusResponse(kind=prefix, payload=raw[1:], raw=raw)
    raise ProtocolError(f"unsupported response prefix: {prefix!r}")


def combine_telemetry_word(high: int, low: int) -> int:
    """Combine adjacent firmware telemetry bytes using BixCheck's byte order."""

    return (_byte(high, "high telemetry byte") << 8) | _byte(
        low, "low telemetry byte"
    )


def decode_igniter_state(raw: int) -> IgniterState:
    """Decode BixCheck's exact low-three-bit T08 display rules.

    The labels preserve the vendor application's literal ``L``/``R`` wording.
    High bits do not affect the displayed result.
    """

    raw = _byte(raw, "igniter state")
    code = raw & 0x07
    label = {
        0: "L R failed",
        1: "R failed",
        2: "L failed",
        7: "L R good",
    }.get(code, "Error")
    return IgniterState(raw=raw, code=code, label=label)


def decode_operating_state(raw: int) -> OperatingState:
    """Decode the exact BixCheck 5.5 display rules for the T09 state byte.

    ``family`` is the high nibble.  ``level`` retains the low-three-bit target
    encoded by the controller even where BixCheck displays only ``Ramping``.
    Values outside the six known families deliberately remain explicit rather
    than being assigned invented controller semantics.
    """

    raw = _byte(raw, "state")
    normalized = raw & 0x7F
    family = (normalized & 0x70) >> 4
    low = normalized & 0x0F
    if family == 1:
        return OperatingState(raw, normalized, family, "cooldown", "Cooldown")
    if family == 2:
        return OperatingState(raw, normalized, family, "off", "Off")
    if family == 3:
        startup = {
            0: ("prefill", "Prefill"),
            1: ("started", "Started"),
            2: ("starting", "Starting"),
            3: ("ignited", "Ignited"),
        }
        phase, label = startup.get(low & 0x07, ("startup_error", "Error"))
        return OperatingState(raw, normalized, family, phase, label)
    if family == 4:
        level = (low & 0x07) + 1
        thermostat = bool(low & 0x08)
        label = f"TSTAT L {level}" if thermostat else f"Level {level}"
        return OperatingState(
            raw, normalized, family, "operating", label,
            level=level, thermostat=thermostat
        )
    if family == 5:
        return OperatingState(
            raw, normalized, family, "ramping", "Ramping",
            level=(low & 0x07) + 1
        )
    if family == 6:
        return OperatingState(raw, normalized, family, "ash_dump", "Ash dump")
    return OperatingState(
        raw, normalized, family, "undefined", f"Undefined: {normalized:02X}"
    )


class ResponseLineParser:
    """Incremental CR/LF response splitter with a bounded receive buffer."""

    def __init__(self, max_line_length: int = 255):
        if max_line_length < 7:
            raise ValueError("max_line_length must be at least 7")
        self.max_line_length = max_line_length
        self._buffer = bytearray()

    def feed(self, data: bytes | bytearray | memoryview) -> list[ResponseFrame]:
        self._buffer.extend(data)
        frames: list[ResponseFrame] = []
        while True:
            positions = [
                position
                for marker in (b"\r", b"\n")
                if (position := self._buffer.find(marker)) >= 0
            ]
            if not positions:
                break
            end = min(positions)
            line = bytes(self._buffer[:end])
            del self._buffer[: end + 1]
            while self._buffer[:1] in (b"\r", b"\n"):
                del self._buffer[:1]
            if line:
                frames.append(parse_response_line(line))
        if len(self._buffer) > self.max_line_length:
            self._buffer.clear()
            raise ProtocolError("unterminated response exceeds receive limit")
        return frames

    @property
    def pending(self) -> bytes:
        return bytes(self._buffer)


def _signed_byte(value: int) -> int:
    value = _byte(value, "value")
    return value - 0x100 if value & 0x80 else value


def _trunc_div(numerator: int, denominator: int) -> int:
    if denominator <= 0:
        raise ValueError("denominator must be positive")
    magnitude = abs(numerator) // denominator
    return -magnitude if numerator < 0 else magnitude


def stove_multiply_parameter_to_percentage(raw_value: int, address: int) -> int:
    """Reproduce BixCheck 5.5's displayed lean-burn conversion.

    The second argument in the EXE is the EEPROM address, not a generic mode:
    0x6B/0x9B are thresholds, 0x6C/0x9C fan offsets, and 0x6D/0x9D
    feed offsets.  The return value is normalized to a signed Python integer.
    """

    raw_value = _byte(raw_value, "raw_value")
    address = _byte(address, "address")
    if address in (0x6B, 0x9B):
        return (raw_value * 100 + 100) >> 7
    if address in (0x6C, 0x9C):
        return _trunc_div((raw_value - 128) * 100, 128)
    if address in (0x6D, 0x9D):
        return _trunc_div((128 - raw_value) * 100, 128)
    raise ValueError(f"address 0x{address:02X} is not a lean-burn multiply parameter")


def _bixcheck_center_round(value: int) -> int:
    """Reproduce the two SBB-based byte corrections in the original EXE."""

    value &= 0xFF
    carry = value < 0x80
    value = (value - int(carry)) & 0xFF
    carry = value < 0x81
    return (value - 0xFF - int(carry)) & 0xFF


def percentage_to_stove_multiply_parameter(percentage: int, address: int) -> int:
    """Reproduce BixCheck 5.5's percentage-to-EEPROM conversion exactly."""

    if not isinstance(percentage, int) or not -128 <= percentage <= 127:
        raise ValueError("percentage must fit in a signed byte")
    address = _byte(address, "address")
    scaled = _trunc_div(percentage * 128, 100)
    if address in (0x6B, 0x9B):
        return scaled & 0xFF
    if address in (0x6C, 0x9C):
        return _bixcheck_center_round(128 + scaled)
    if address in (0x6D, 0x9D):
        return _bixcheck_center_round(128 - scaled)
    raise ValueError(f"address 0x{address:02X} is not a lean-burn multiply parameter")


CHECKSUM_END_BY_FORMAT = {
    0: 0x4B,
    1: 0x4B,
    2: 0x4C,
    3: 0x4C,
    4: 0x69,
    5: 0x9A,
    7: 0xFF,
}


def calculate_configuration_checksum(
    data_format: int,
    eeprom: Mapping[int, int] | bytes | bytearray | memoryview,
    *,
    displayed_lean_burn_values: bool = False,
) -> int:
    """Calculate the 16-bit BixCheck EEPROM checksum.

    Coverage begins at A02 and is selected by data format.  A byte is added to
    the accumulator and the 16-bit result is rotated left once for every
    address.  If ``displayed_lean_burn_values`` is true, values at A6B-A6D and
    A9B-A9D are converted back to their on-stove representation first, matching
    BixCheck 5.5's checksum path.
    """

    try:
        end = CHECKSUM_END_BY_FORMAT[data_format]
    except KeyError as exc:
        raise ValueError(f"unsupported or unconfirmed data format: {data_format}") from exc
    if isinstance(eeprom, Mapping):
        missing = [address for address in range(0x02, end + 1) if address not in eeprom]
        if missing:
            raise ValueError(f"EEPROM map is missing address 0x{missing[0]:02X}")
        values = {address: eeprom[address] for address in range(0x02, end + 1)}
    else:
        sequence = bytes(eeprom)
        required = end - 0x02 + 1
        if len(sequence) < required:
            raise ValueError(f"EEPROM sequence requires at least {required} bytes")
        values = {
            address: sequence[address - 0x02] for address in range(0x02, end + 1)
        }

    checksum = 0
    lean_burn = frozenset((0x6B, 0x6C, 0x6D, 0x9B, 0x9C, 0x9D))
    for address in range(0x02, end + 1):
        value = values[address]
        if displayed_lean_burn_values and address in lean_burn:
            value = percentage_to_stove_multiply_parameter(value, address)
        value = _byte(value, f"EEPROM A{address:02X}")
        checksum = (checksum + value) & 0xFFFF
        checksum = ((checksum << 1) | (checksum >> 15)) & 0xFFFF
    return checksum
