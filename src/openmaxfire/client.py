"""High-level and research-level OpenMaxFire client primitives.

The public methods deliberately distinguish transmission from verification.
Writing bytes to J3 is never treated as proof that the controller accepted or
acted on them.  Callers that need a verified register value must request a
fresh readback explicitly.
"""

from __future__ import annotations

import math
import threading
import time
from dataclasses import dataclass
from typing import Callable

from .errors import SafetyInterlockError
from .profiles import ControllerProfile, select_profile
from .protocol import (
    AddressedResponse,
    ProtocolError,
    READ_OPCODE,
    ResponseFrame,
    RemoteButton,
    decode_register_request,
    encode_read_register,
    encode_remote_button,
    encode_write_register,
    parse_response_line,
)
from .transport import Transport


_BINARY_LOADER_MARKERS = frozenset(
    (0xE3, 0xE4, 0xE5, 0xE7, 0xE8, 0xEA, 0xEB, 0xED)
)
_SOFTWARE_LOADER_ENTRY = b"CW0FC4"
_SOFTWARE_LOADER_REGISTER_STEM = b"CW0F"
_SOFTWARE_LOADER_SPLIT_SUFFIXES = (b"W0FC4", b"0FC4", b"FC4")


class _RawGuardState:
    """Per-transport fail-closed state for generic outgoing byte streams."""

    def __init__(self) -> None:
        self.tail = b""
        self.indeterminate_after_write_error = False
        self.lock = threading.Lock()


def contains_loader_traffic(
    payload: bytes | bytearray | memoryview,
    *,
    stream_prefix: bytes = b"",
) -> bool:
    """Return whether bytes can participate in the known loader protocol.

    The loader opcodes are binary single bytes, not the ASCII strings ``EA``
    or ``E3``.  ``stream_prefix`` lets a caller reject the keyed ASCII reset
    even when it is split across multiple raw writes.
    """

    value = bytes(payload)
    return (
        any(byte in _BINARY_LOADER_MARKERS for byte in value)
        or _SOFTWARE_LOADER_REGISTER_STEM in value
        or value.startswith(_SOFTWARE_LOADER_SPLIT_SUFFIXES)
        or _SOFTWARE_LOADER_ENTRY in stream_prefix + value
    )


def validate_generic_raw_payload(
    payload: bytes | bytearray | memoryview,
    *,
    stream_prefix: bytes = b"",
) -> bytes:
    """Validate one complete non-loader A/C/D request for generic transmission.

    Constraining each call to the recovered fixed-length request grammar keeps
    separate clients or CLI processes from assembling an unterminated loader
    entry request across transport reopen boundaries.
    """

    value = bytes(payload)
    if not value:
        raise ValueError("raw command must contain at least one byte")
    if contains_loader_traffic(value, stream_prefix=stream_prefix):
        raise SafetyInterlockError(
            "known firmware-loader traffic is isolated and forbidden through generic "
            "raw/register I/O"
        )
    try:
        decode_register_request(value)
    except ProtocolError as exc:
        raise SafetyInterlockError(
            "generic raw transmission accepts exactly one complete A/C/D register "
            "request; arbitrary or fragmented byte streams are disabled"
        ) from exc
    return value


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
        return select_profile(self) is not None

    @property
    def profile(self) -> ControllerProfile | None:
        return select_profile(self)

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
            "profile_key": self.profile.key if self.profile else None,
            "registers": values,
        }


class MaxFireClient:
    def __init__(self, transport: Transport):
        self.transport = transport
        state = getattr(transport, "_openmaxfire_raw_guard_state", None)
        if not isinstance(state, _RawGuardState):
            state = _RawGuardState()
            try:
                setattr(transport, "_openmaxfire_raw_guard_state", state)
            except (AttributeError, TypeError):
                # Built-in transports permit the shared marker. A minimal
                # slots-only research transport still receives a per-client
                # fail-closed guard.
                pass
        self._raw_guard_state = state

    def send_raw(self, command: bytes | bytearray | memoryview) -> CommandReceipt:
        """Transmit exact bytes without appending a line terminator.

        This is a send-only request primitive, not a success claim. It accepts
        exactly one recovered A/C/D register request; arbitrary and fragmented
        byte streams are disabled. Known binary loader markers, the entire
        ``CW0F`` reset-register family, boundary fragments, and the keyed
        ``CW0FC4`` reset are isolated from this generic API. Dedicated rehearsal
        code accepts only exact simulator transports. Direct Transport access
        is outside this API safety boundary.
        """

        payload = bytes(command)
        state = self._raw_guard_state
        with state.lock:
            if state.indeterminate_after_write_error:
                raise SafetyInterlockError(
                    "generic raw output is locked after an indeterminate transport write; "
                    "close this transport rather than continuing a byte stream"
                )
            validate_generic_raw_payload(payload, stream_prefix=state.tail)
            combined = state.tail + payload
            # Advance before the I/O. If write/flush fails after putting bytes
            # on the wire, a caller cannot discard the dangerous prefix state.
            state.tail = combined[-(len(_SOFTWARE_LOADER_ENTRY) - 1):]
            try:
                self.transport.write(payload)
            except BaseException:
                state.indeterminate_after_write_error = True
                raise
        return CommandReceipt(request=payload)

    def exchange_raw(
        self,
        command: bytes | bytearray | memoryview,
        *,
        receive_duration: float = 1.0,
    ) -> CommandReceipt:
        """Transmit one exact A/C/D request and retain an uninterpreted reply window.

        No response grammar, acknowledgement, or success semantics are
        inferred. The outgoing bytes must pass the complete-request guard;
        this keeps register and loader state machines separate.
        """

        if not math.isfinite(receive_duration) or receive_duration < 0:
            raise ValueError("receive_duration must be finite and nonnegative")
        receipt = self.send_raw(command)
        response = (
            self.capture_receive_only(receive_duration)
            if receive_duration > 0
            else b""
        )
        return CommandReceipt(request=receipt.request, response=response)

    def read_register(self, address: int, *, unit: str = "C") -> CommandReceipt:
        """Send a register-read request without waiting for a response."""

        return self.send_raw(encode_read_register(address, unit=unit))

    def query_register(
        self,
        address: int,
        *,
        unit: str = "C",
        max_frames: int | None = None,
        on_frame: Callable[[ResponseFrame], None] | None = None,
    ) -> AddressedResponse:
        """Read one A/C/D register and ignore interleaved unsolicited frames.

        By default, matching continues until the transport's configured read
        timeout expires.  ``max_frames`` remains available to callers that need
        an additional explicit bound.
        """

        if max_frames is not None and max_frames < 1:
            raise ValueError("max_frames must be at least one")
        self.send_raw(encode_read_register(address, unit=unit))
        frames_seen = 0
        while max_frames is None or frames_seen < max_frames:
            try:
                frame = self.receive_response()
            except TimeoutError as exc:
                raise TimeoutError(
                    f"no matching {unit}R{address:02X} response before serial "
                    f"timeout after {frames_seen} frame(s)"
                ) from exc
            except ValueError:
                # A port can open in the middle of a periodic telemetry line.
                # Discard that bounded malformed fragment and resynchronize at
                # the next CR/LF delimiter while the traffic logger retains the
                # original bytes for diagnosis.
                frames_seen += 1
                continue
            frames_seen += 1
            if on_frame is not None:
                on_frame(frame)
            if (
                isinstance(frame, AddressedResponse)
                and frame.unit == unit
                and frame.opcode == READ_OPCODE
                and frame.address == address
            ):
                return frame
        assert max_frames is not None
        raise TimeoutError(
            f"no matching {unit}R{address:02X} response within {max_frames} frames"
        )

    def _query_read_only_with_retries(
        self,
        address: int,
        *,
        unit: str = "C",
        attempts: int = 1,
    ) -> AddressedResponse:
        if isinstance(attempts, bool) or not isinstance(attempts, int):
            raise TypeError("attempts must be an integer")
        if not 1 <= attempts <= 5:
            raise ValueError("attempts must be between 1 and 5")
        for attempt in range(1, attempts + 1):
            try:
                return self.query_register(address, unit=unit)
            except TimeoutError:
                if attempt == attempts:
                    raise
        raise AssertionError("read-only retry loop did not return or raise")

    def identify(
        self,
        *,
        request_delay: float = 0.0,
        read_attempts: int = 1,
    ) -> StoveIdentity:
        """Run BixCheck's read-only controller identity sequence."""

        if not math.isfinite(request_delay) or request_delay < 0:
            raise ValueError("request_delay must be finite and nonnegative")
        addresses = (0x00, 0x08, 0x0B, 0x0C, 0x0D, 0x0E)
        values: dict[int, int] = {}
        for index, address in enumerate(addresses):
            values[address] = self._query_read_only_with_retries(
                address,
                attempts=read_attempts,
            ).value
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

    def identify_profile(
        self,
        *,
        request_delay: float = 0.0,
        read_attempts: int = 1,
    ) -> tuple[StoveIdentity, ControllerProfile | None]:
        """Read identity and return its exact known profile, if any."""

        identity = self.identify(
            request_delay=request_delay,
            read_attempts=read_attempts,
        )
        return identity, select_profile(identity)

    def read_eeprom(
        self,
        *,
        first: int = 0x00,
        last: int = 0xFF,
        request_delay: float = 0.0,
        read_attempts: int = 1,
    ) -> dict[int, int]:
        """Read a contiguous A-space range without issuing any write."""

        if not 0 <= first <= last <= 0xFF:
            raise ValueError("EEPROM range must satisfy 0x00 <= first <= last <= 0xFF")
        if not math.isfinite(request_delay) or request_delay < 0:
            raise ValueError("request_delay must be finite and nonnegative")
        values: dict[int, int] = {}
        for address in range(first, last + 1):
            values[address] = self._query_read_only_with_retries(
                address,
                unit="A",
                attempts=read_attempts,
            ).value
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

    def write_register(
        self,
        address: int,
        value: int,
        *,
        unit: str = "C",
    ) -> CommandReceipt:
        """Transmit one A/C/D write without claiming controller acceptance."""

        return self.send_raw(encode_write_register(address, value, unit=unit))

    def write_register_verified(
        self,
        address: int,
        value: int,
        *,
        unit: str = "C",
        settle_delay: float = 0.0,
        max_frames: int | None = None,
        on_frame: Callable[[ResponseFrame], None] | None = None,
    ) -> CommandReceipt:
        """Write a register, read it afresh, and compare the returned byte.

        A matching readback verifies only the addressed byte.  It does not
        prove that an actuator moved or that a command-style C register had its
        intended physical effect.
        """

        if not math.isfinite(settle_delay) or settle_delay < 0:
            raise ValueError("settle_delay must be finite and nonnegative")
        receipt = self.write_register(address, value, unit=unit)
        if settle_delay:
            time.sleep(settle_delay)
        response = self.query_register(
            address,
            unit=unit,
            max_frames=max_frames,
            on_frame=on_frame,
        )
        return CommandReceipt(
            request=receipt.request,
            response=response.raw,
            verified=response.value == value,
        )

    def remote_button(self, button: RemoteButton) -> CommandReceipt:
        """Send a reconstructed BixCheck front-panel remote-control action.

        The bytes are live-validated on firmware 2.02. A write receipt confirms
        transmission only; it is not proof that the controller accepted or
        completed the requested state transition.
        """

        return self.send_raw(encode_remote_button(button))

    def close(self) -> None:
        self.transport.close()
