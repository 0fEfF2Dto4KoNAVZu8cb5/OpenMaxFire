"""Read-only controller discovery and profile selection.

Discovery sends only the established identity reads.  Opening a serial port may
still transition DTR/RTS, so this API is read-only at the protocol level rather
than electrically passive.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Iterable

from .client import MaxFireClient, StoveIdentity
from .profiles import ControllerProfile, select_profile
from .transport import (
    SerialPortInfo,
    SerialSettings,
    SerialTransport,
    Transport,
    list_serial_ports,
)


TransportFactory = Callable[[SerialSettings], Transport]


class DetectionStatus(str, Enum):
    DETECTED = "detected"
    UNSUPPORTED = "unsupported"
    NO_RESPONSE = "no_response"


@dataclass(frozen=True, slots=True)
class ProbeAttempt:
    port: str
    baudrate: int
    responded: bool
    error_type: str | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "port": self.port,
            "baudrate": self.baudrate,
            "responded": self.responded,
            "error_type": self.error_type,
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class DetectionResult:
    status: DetectionStatus
    port: str
    baudrate: int | None
    identity: StoveIdentity | None
    profile: ControllerProfile | None
    attempts: tuple[ProbeAttempt, ...]

    @property
    def detected(self) -> bool:
        return self.status is DetectionStatus.DETECTED

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status.value,
            "port": self.port,
            "baudrate": self.baudrate,
            "identity": self.identity.to_dict() if self.identity else None,
            "profile": self.profile.to_dict() if self.profile else None,
            "attempts": [attempt.to_dict() for attempt in self.attempts],
        }


@dataclass(frozen=True, slots=True)
class DiscoveryReport:
    results: tuple[DetectionResult, ...]

    @property
    def detected(self) -> tuple[DetectionResult, ...]:
        return tuple(result for result in self.results if result.detected)

    def to_dict(self) -> dict[str, object]:
        return {"results": [result.to_dict() for result in self.results]}


def _validated_baudrates(values: Iterable[int]) -> tuple[int, ...]:
    result: list[int] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError("baudrates must contain positive integers")
        if value not in result:
            result.append(value)
    if not result:
        raise ValueError("at least one baudrate is required")
    return tuple(result)


def detect_controller(
    port: str,
    *,
    baudrates: Iterable[int] = (9600, 19200),
    timeout: float = 0.35,
    request_delay: float = 0.10,
    transport_factory: TransportFactory = SerialTransport,
) -> DetectionResult:
    """Probe one port with read-only identity requests and select a profile."""

    if not isinstance(port, str) or not port.strip():
        raise ValueError("port must be a non-empty serial device name")
    if not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("timeout must be a finite positive number")
    if (
        not isinstance(request_delay, (int, float))
        or not math.isfinite(request_delay)
        or request_delay < 0
    ):
        raise ValueError("request_delay must be finite and nonnegative")

    attempts: list[ProbeAttempt] = []
    for baudrate in _validated_baudrates(baudrates):
        client: MaxFireClient | None = None
        try:
            transport = transport_factory(
                SerialSettings(port=port, baudrate=baudrate, timeout=float(timeout))
            )
            client = MaxFireClient(transport)
            identity = client.identify(request_delay=float(request_delay))
        except Exception as exc:
            attempts.append(
                ProbeAttempt(
                    port=port,
                    baudrate=baudrate,
                    responded=False,
                    error_type=type(exc).__name__,
                    error=str(exc),
                )
            )
            continue
        finally:
            if client is not None:
                client.close()

        attempts.append(ProbeAttempt(port=port, baudrate=baudrate, responded=True))
        profile = select_profile(identity)
        return DetectionResult(
            status=(DetectionStatus.DETECTED if profile else DetectionStatus.UNSUPPORTED),
            port=port,
            baudrate=baudrate,
            identity=identity,
            profile=profile,
            attempts=tuple(attempts),
        )

    return DetectionResult(
        status=DetectionStatus.NO_RESPONSE,
        port=port,
        baudrate=None,
        identity=None,
        profile=None,
        attempts=tuple(attempts),
    )


def detect_controllers(
    ports: Iterable[str | SerialPortInfo] | None = None,
    **probe_options: object,
) -> DiscoveryReport:
    """Probe explicit ports, or every enumerated port, without issuing writes."""

    candidates = list_serial_ports() if ports is None else list(ports)
    names = [item.device if isinstance(item, SerialPortInfo) else item for item in candidates]
    return DiscoveryReport(
        tuple(detect_controller(name, **probe_options) for name in names)
    )
