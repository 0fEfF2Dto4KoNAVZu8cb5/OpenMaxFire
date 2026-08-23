"""Controller profiles and machine-readable capability negotiation.

Profiles centralize firmware/data-format differences so callers do not scatter
version comparisons or register literals throughout their own code.  A profile
describes both what the controller is known to provide and the present evidence
boundary of the OpenMaxFire API.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType
from typing import Mapping, Protocol


class IdentityLike(Protocol):
    probe: int
    data_format: int
    firmware_major: int
    firmware_minor: int
    reserved: int
    version_readback: int


class Capability(str, Enum):
    MONITOR = "monitor"
    NORMAL_CONTROL = "normal_control"
    CONFIGURATION_READ = "configuration_read"
    CONFIGURATION_WRITE = "configuration_write"
    CHECKOUT_PASSIVE = "checkout_passive"
    CHECKOUT_ACTUATOR = "checkout_actuator"
    FIRMWARE_LOADER = "firmware_loader"
    D_SPACE = "d_space"
    PROGRAM_MEMORY_DUMP = "program_memory_dump"


class CapabilityState(str, Enum):
    """Current API support/evidence state for one controller capability."""

    AVAILABLE = "available"
    EXPERIMENTAL = "experimental"
    PLANNED = "planned"
    UNSUPPORTED = "unsupported"


class TelemetryLayout(str, Enum):
    FORMAT_04 = "format04-live-partial"
    BIXCHECK_5 = "bixcheck5-static"


@dataclass(frozen=True, slots=True)
class ControllerRegisterDefinition:
    address: int
    name: str
    evidence: str


@dataclass(frozen=True, slots=True)
class ControllerWriteDefinition:
    address: int
    name: str
    state_changing: bool
    same_address_readback_meaningful: bool
    evidence: str


@dataclass(frozen=True, slots=True)
class ControllerCapabilities:
    states: Mapping[Capability, CapabilityState]

    def state(self, capability: Capability | str) -> CapabilityState:
        return self.states[Capability(capability)]

    def available(self, capability: Capability | str) -> bool:
        return self.state(capability) is CapabilityState.AVAILABLE

    def to_dict(self) -> dict[str, str]:
        return {capability.value: self.states[capability].value for capability in Capability}


@dataclass(frozen=True, slots=True)
class ControllerProfile:
    key: str
    firmware_major: int
    firmware_minor: int
    data_format: int
    reserved: int
    version_readback: int
    baudrates: tuple[int, ...]
    telemetry_layout: TelemetryLayout
    telemetry_last_periodic: int
    evidence: str
    capabilities: ControllerCapabilities
    controller_registers: Mapping[int, ControllerRegisterDefinition]
    controller_writes: Mapping[int, ControllerWriteDefinition]

    @property
    def firmware_version(self) -> str:
        return f"{self.firmware_major:X}.{self.firmware_minor:02X}"

    def matches(self, identity: IdentityLike) -> bool:
        return (
            identity.probe == 0
            and identity.data_format == self.data_format
            and identity.firmware_major == self.firmware_major
            and identity.firmware_minor == self.firmware_minor
            and identity.reserved == self.reserved
            and identity.version_readback == self.version_readback
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "key": self.key,
            "firmware_version": self.firmware_version,
            "data_format": f"{self.data_format:02X}",
            "baudrates": list(self.baudrates),
            "telemetry_layout": self.telemetry_layout.value,
            "telemetry_last_periodic": f"T{self.telemetry_last_periodic:02X}",
            "evidence": self.evidence,
            "capabilities": self.capabilities.to_dict(),
        }


def _frozen_map(values: Mapping) -> Mapping:
    return MappingProxyType(dict(values))


COMMON_CONTROLLER_REGISTERS = _frozen_map(
    {
        0x00: ControllerRegisterDefinition(0x00, "communication_probe", "live/static"),
        0x01: ControllerRegisterDefinition(0x01, "front_panel_buttons", "live/static"),
        0x02: ControllerRegisterDefinition(0x02, "physical_inputs", "live/static"),
        0x03: ControllerRegisterDefinition(0x03, "controller_status_03", "static/partial"),
        0x04: ControllerRegisterDefinition(0x04, "board_temperature", "static"),
        0x05: ControllerRegisterDefinition(0x05, "exhaust_sensor_count", "static"),
        0x06: ControllerRegisterDefinition(0x06, "thermostat_and_status", "live/static"),
        0x07: ControllerRegisterDefinition(0x07, "feeder_sensor_interval", "static"),
        0x08: ControllerRegisterDefinition(0x08, "data_format", "live/static"),
        0x09: ControllerRegisterDefinition(0x09, "fan_potentiometer", "live/static"),
        0x0A: ControllerRegisterDefinition(0x0A, "feed_potentiometer", "live/static"),
        0x0B: ControllerRegisterDefinition(0x0B, "firmware_major", "live/static"),
        0x0C: ControllerRegisterDefinition(0x0C, "firmware_minor", "live/static"),
        0x0D: ControllerRegisterDefinition(0x0D, "firmware_reserved", "live/static"),
        0x0E: ControllerRegisterDefinition(0x0E, "version_readback", "live/static"),
    }
)


COMMON_CONTROLLER_WRITES = _frozen_map(
    {
        0x00: ControllerWriteDefinition(0x00, "service_countdown", True, False, "static"),
        0x01: ControllerWriteDefinition(0x01, "persist_configuration_checksum", True, False, "static/emulator"),
        0x02: ControllerWriteDefinition(0x02, "telemetry_suppression_enable", True, False, "static"),
        0x03: ControllerWriteDefinition(0x03, "telemetry_suppression_disable", True, False, "static"),
        0x04: ControllerWriteDefinition(0x04, "front_panel_leds", True, False, "static"),
        0x05: ControllerWriteDefinition(0x05, "burn_drive_motor", True, False, "static"),
        0x06: ControllerWriteDefinition(0x06, "air_compressor_on", True, False, "static"),
        0x07: ControllerWriteDefinition(0x07, "air_compressor_off", True, False, "static"),
        0x08: ControllerWriteDefinition(0x08, "convection_fan", True, False, "static"),
        0x09: ControllerWriteDefinition(0x09, "exhaust_fan", True, False, "static"),
        0x0A: ControllerWriteDefinition(0x0A, "igniter_followup", True, False, "static"),
        0x0B: ControllerWriteDefinition(0x0B, "feed_motor_sensor_test", True, False, "static"),
        0x0C: ControllerWriteDefinition(0x0C, "controller_service_unresolved", True, False, "static/partial"),
        0x0D: ControllerWriteDefinition(0x0D, "igniter_workflow", True, False, "static"),
        0x0E: ControllerWriteDefinition(
            0x0E,
            "remote_front_panel",
            True,
            False,
            "static; live on firmware 2.02",
        ),
        0x0F: ControllerWriteDefinition(0x0F, "reset_or_loader", True, False, "static"),
    }
)


def _capabilities(*, live_read: bool) -> ControllerCapabilities:
    read_state = CapabilityState.AVAILABLE if live_read else CapabilityState.EXPERIMENTAL
    return ControllerCapabilities(
        _frozen_map(
            {
                Capability.MONITOR: read_state,
                Capability.NORMAL_CONTROL: CapabilityState.EXPERIMENTAL,
                Capability.CONFIGURATION_READ: read_state,
                Capability.CONFIGURATION_WRITE: CapabilityState.PLANNED,
                Capability.CHECKOUT_PASSIVE: CapabilityState.EXPERIMENTAL,
                Capability.CHECKOUT_ACTUATOR: CapabilityState.PLANNED,
                Capability.FIRMWARE_LOADER: CapabilityState.PLANNED,
                Capability.D_SPACE: CapabilityState.EXPERIMENTAL,
                Capability.PROGRAM_MEMORY_DUMP: CapabilityState.UNSUPPORTED,
            }
        )
    )


PROFILES: tuple[ControllerProfile, ...] = (
    ControllerProfile(
        key="fw202-format04",
        firmware_major=0x02,
        firmware_minor=0x02,
        data_format=0x04,
        reserved=0x00,
        version_readback=0x00,
        baudrates=(9600,),
        telemetry_layout=TelemetryLayout.FORMAT_04,
        telemetry_last_periodic=0x15,
        evidence="live-validated read/control/fault behavior on controller serial 5215",
        capabilities=_capabilities(live_read=True),
        controller_registers=COMMON_CONTROLLER_REGISTERS,
        controller_writes=COMMON_CONTROLLER_WRITES,
    ),
    ControllerProfile(
        key="fw206-format05",
        firmware_major=0x02,
        firmware_minor=0x06,
        data_format=0x05,
        reserved=0x00,
        version_readback=0x21,
        baudrates=(9600,),
        telemetry_layout=TelemetryLayout.BIXCHECK_5,
        telemetry_last_periodic=0x1D,
        evidence="vendor package, static analysis, and offline emulation",
        capabilities=_capabilities(live_read=False),
        controller_registers=COMMON_CONTROLLER_REGISTERS,
        controller_writes=COMMON_CONTROLLER_WRITES,
    ),
    ControllerProfile(
        key="fw270-format07",
        firmware_major=0x02,
        firmware_minor=0x70,
        data_format=0x07,
        reserved=0x00,
        version_readback=0x02,
        baudrates=(19200,),
        telemetry_layout=TelemetryLayout.BIXCHECK_5,
        telemetry_last_periodic=0x1D,
        evidence="embedded vendor image, static analysis, and offline emulation",
        capabilities=_capabilities(live_read=False),
        controller_registers=COMMON_CONTROLLER_REGISTERS,
        controller_writes=COMMON_CONTROLLER_WRITES,
    ),
    ControllerProfile(
        key="fw271-format07",
        firmware_major=0x02,
        firmware_minor=0x71,
        data_format=0x07,
        reserved=0x00,
        version_readback=0x00,
        baudrates=(19200,),
        telemetry_layout=TelemetryLayout.BIXCHECK_5,
        telemetry_last_periodic=0x1E,
        evidence="embedded vendor image, static analysis, and offline emulation",
        capabilities=_capabilities(live_read=False),
        controller_registers=COMMON_CONTROLLER_REGISTERS,
        controller_writes=COMMON_CONTROLLER_WRITES,
    ),
)

PROFILES_BY_KEY: Mapping[str, ControllerProfile] = _frozen_map(
    {profile.key: profile for profile in PROFILES}
)


def select_profile(identity: IdentityLike) -> ControllerProfile | None:
    """Return the exact known profile for an identity, or ``None``."""

    return next((profile for profile in PROFILES if profile.matches(identity)), None)


def profile_for_data_format(data_format: int) -> ControllerProfile | None:
    """Return a layout representative when only CR08 has been observed.

    Format 07 has two known firmware versions with the same BixCheck telemetry
    layout.  The newest profile is returned for decoding only; callers must not
    use this fallback for capability or write decisions.
    """

    matches = [profile for profile in PROFILES if profile.data_format == data_format]
    return matches[-1] if matches else None
