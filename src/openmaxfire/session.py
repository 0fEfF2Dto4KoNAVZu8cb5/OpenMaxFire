"""Unified, presentation-neutral controller session.

The session owns one transport, exact identity/profile negotiation, accumulated
monitor state, and read-only service primitives.  CLI, GUI, and automation
clients can share this layer without reproducing connection or register logic.
"""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Iterator

from .audit import AuditTrail
from .client import MaxFireClient, StoveIdentity
from .configuration import ConfigurationImage
from .discovery import DetectionStatus, TransportFactory, detect_controller
from .errors import OpenMaxFireError, UnsupportedControllerError
from .models import StoveSnapshot
from .monitor import MonitorState
from .profiles import ControllerCapabilities, ControllerProfile, select_profile
from .transport import RecordingTransport, SerialSettings, SerialTransport, Transport


@dataclass(frozen=True, slots=True)
class ConnectionInfo:
    port: str
    baudrate: int
    timeout: float
    simulated: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "timeout": self.timeout,
            "simulated": self.simulated,
        }


class ControllerSession:
    """One identified controller connection and its accumulated typed state."""

    def __init__(
        self,
        client: MaxFireClient,
        identity: StoveIdentity,
        profile: ControllerProfile,
        connection: ConnectionInfo,
        *,
        stale_after: float = 10.0,
        audit: AuditTrail | None = None,
    ):
        if select_profile(identity) != profile:
            raise ValueError("identity does not exactly match the supplied profile")
        self.client = client
        self.identity = identity
        self.profile = profile
        self.connection = connection
        self.monitor = MonitorState(stale_after=stale_after, profile=profile)
        self.audit = audit
        self._closed = False
        self._last_control_monotonic: float | None = None

    @classmethod
    def from_client(
        cls,
        client: MaxFireClient,
        *,
        port: str,
        baudrate: int,
        timeout: float = 0.35,
        request_delay: float = 0.0,
        stale_after: float = 10.0,
        audit: AuditTrail | None = None,
    ) -> "ControllerSession":
        """Identify an already-open client and take ownership of it."""

        if audit is not None:
            client.transport = RecordingTransport(client.transport, audit)
        try:
            identity = client.identify(request_delay=request_delay)
        except Exception:
            client.close()
            raise
        profile = select_profile(identity)
        if profile is None:
            client.close()
            raise UnsupportedControllerError(
                f"unsupported controller {identity.firmware_version}/"
                f"format {identity.data_format:02X}"
            )
        connection = ConnectionInfo(
            port=port,
            baudrate=baudrate,
            timeout=float(timeout),
            simulated=_is_simulated_transport(client.transport),
        )
        return cls(
            client,
            identity,
            profile,
            connection,
            stale_after=stale_after,
            audit=audit,
        )

    @classmethod
    def connect(
        cls,
        port: str,
        *,
        baudrate: int | None = None,
        baudrates: tuple[int, ...] = (9600, 19200),
        timeout: float = 0.35,
        request_delay: float = 0.10,
        stale_after: float = 10.0,
        transport_factory: TransportFactory = SerialTransport,
        audit: AuditTrail | None = None,
    ) -> "ControllerSession":
        """Open an exact baud or safely detect it using identity reads only."""

        selected_baud = baudrate
        if selected_baud is None:
            detection = detect_controller(
                port,
                baudrates=baudrates,
                timeout=timeout,
                request_delay=request_delay,
                transport_factory=transport_factory,
            )
            if detection.status is DetectionStatus.NO_RESPONSE:
                raise OpenMaxFireError(f"no supported controller responded on {port}")
            if detection.status is DetectionStatus.UNSUPPORTED:
                assert detection.identity is not None
                raise UnsupportedControllerError(
                    f"unsupported controller {detection.identity.firmware_version}/"
                    f"format {detection.identity.data_format:02X} on {port}"
                )
            assert detection.baudrate is not None
            selected_baud = detection.baudrate
        settings = SerialSettings(
            port=port,
            baudrate=selected_baud,
            timeout=float(timeout),
        )
        client = MaxFireClient(transport_factory(settings))
        return cls.from_client(
            client,
            port=port,
            baudrate=selected_baud,
            timeout=timeout,
            request_delay=request_delay,
            stale_after=stale_after,
            audit=audit,
        )

    @classmethod
    def simulated(
        cls,
        profile: ControllerProfile | str = "fw271-format07",
        *,
        allow_writes: bool = False,
        stale_after: float = 10.0,
        controller: object | None = None,
        audit: AuditTrail | None = None,
    ) -> "ControllerSession":
        """Create a session over the public in-memory simulator."""

        from .simulator import SimulatedController, SimulatedTransport

        if controller is None:
            simulated = SimulatedController(profile, allow_writes=allow_writes)
        elif isinstance(controller, SimulatedController):
            simulated = controller
        else:
            raise TypeError("controller must be a SimulatedController")
        selected = simulated.profile
        return cls.from_client(
            MaxFireClient(SimulatedTransport(simulated)),
            port="SIM0",
            baudrate=selected.baudrates[0],
            timeout=0.01,
            stale_after=stale_after,
            audit=audit,
        )

    @property
    def capabilities(self) -> ControllerCapabilities:
        return self.profile.capabilities

    @property
    def simulated_backend(self) -> bool:
        return self.connection.simulated

    @property
    def closed(self) -> bool:
        return self._closed

    def _ensure_open(self) -> None:
        if self._closed:
            raise RuntimeError("controller session is closed")

    def refresh_identity(self, *, request_delay: float = 0.0) -> StoveIdentity:
        self._ensure_open()
        identity = self.client.identify(request_delay=request_delay)
        if select_profile(identity) != self.profile:
            raise UnsupportedControllerError(
                "controller identity changed or no longer matches the active profile"
            )
        self.identity = identity
        return identity

    def read_register(self, address: int, *, unit: str = "C") -> int:
        self._ensure_open()
        return self.client.query_register(address, unit=unit).value

    def poll_snapshot(
        self,
        *,
        request_delay: float = 0.0,
        first: int = 0x00,
        last: int = 0x0E,
    ) -> StoveSnapshot:
        """Poll C-space while ingesting every interleaved telemetry frame."""

        self._ensure_open()
        if not 0 <= first <= last <= 0x0E:
            raise ValueError("controller poll range must be within CR00-CR0E")
        if not math.isfinite(request_delay) or request_delay < 0:
            raise ValueError("request_delay must be finite and nonnegative")
        for address in range(first, last + 1):
            self.client.query_register(address, on_frame=self.monitor.observe)
            if request_delay and address < last:
                time.sleep(request_delay)
        return self.monitor.typed_snapshot()

    def iter_snapshots(
        self,
        *,
        interval: float = 1.0,
        cycles: int | None = None,
        request_delay: float = 0.0,
    ) -> Iterator[StoveSnapshot]:
        """Yield typed snapshots for presentation-neutral subscriptions."""

        if not math.isfinite(interval) or interval < 0:
            raise ValueError("interval must be finite and nonnegative")
        if cycles is not None and (
            isinstance(cycles, bool) or not isinstance(cycles, int) or cycles < 1
        ):
            raise ValueError("cycles must be a positive integer or None")
        completed = 0
        while cycles is None or completed < cycles:
            yield self.poll_snapshot(request_delay=request_delay)
            completed += 1
            if interval and (cycles is None or completed < cycles):
                time.sleep(interval)

    def read_configuration_image(self, *, request_delay: float = 0.0) -> ConfigurationImage:
        self._ensure_open()
        values = self.client.read_eeprom(request_delay=request_delay)
        return ConfigurationImage.from_mapping(values)

    def configuration_backup_document(
        self,
        *,
        request_delay: float = 0.0,
    ) -> dict[str, object]:
        """Return a complete read-only backup document without writing a file."""

        from .backup import build_eeprom_backup

        self._ensure_open()
        values = self.client.read_eeprom(request_delay=request_delay)
        return build_eeprom_backup(
            self.identity,
            values,
            port=self.connection.port,
            baudrate=self.connection.baudrate,
        )

    def claim_control_window(self, minimum_interval: float) -> None:
        """Enforce an in-session lower bound between normal-control writes."""

        if not math.isfinite(minimum_interval) or minimum_interval < 0:
            raise ValueError("minimum_interval must be finite and nonnegative")
        now = time.monotonic()
        if (
            self._last_control_monotonic is not None
            and now - self._last_control_monotonic < minimum_interval
        ):
            from .errors import SafetyInterlockError

            raise SafetyInterlockError("normal-control rate limit has not elapsed")
        self._last_control_monotonic = now

    def close(self) -> None:
        if not self._closed:
            self.client.close()
            self._closed = True

    def __enter__(self) -> "ControllerSession":
        self._ensure_open()
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


def _is_simulated_transport(transport: Transport) -> bool:
    from .simulator import SimulatedTransport

    current: object = transport
    while isinstance(current, RecordingTransport):
        current = current.transport
    return isinstance(current, SimulatedTransport)
