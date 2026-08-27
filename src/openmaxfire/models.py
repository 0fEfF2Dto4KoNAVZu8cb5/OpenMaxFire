"""Typed controller state returned by the reusable Python API."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Mapping

from .faults import decode_format04_indicator_mask
from .profiles import ControllerProfile, TelemetryLayout
from .protocol import (
    IgniterState,
    OperatingState,
    combine_telemetry_word,
    decode_igniter_state,
    decode_operating_state,
)


def _signed_byte(value: int) -> int:
    return value - 0x100 if value & 0x80 else value


def _word(values: Mapping[int, int], high: int) -> int | None:
    if high not in values or high + 1 not in values:
        return None
    return combine_telemetry_word(values[high], values[high + 1])


def _seconds(ticks: int | None) -> float | None:
    return round(ticks / 120.0, 6) if ticks is not None else None


@dataclass(frozen=True, slots=True)
class PanelButtons:
    raw: int
    off: bool
    on: bool
    up: bool
    down: bool


@dataclass(frozen=True, slots=True)
class PhysicalInputs:
    raw: int
    burn_drive_limit: bool
    bit_1_unresolved: bool
    fuel_a_corn: bool
    feeder_wheel_sensor: bool
    firebox_door_open: bool
    ash_drawer_open: bool
    bit_7_unresolved: bool


@dataclass(frozen=True, slots=True)
class AlarmState:
    # ``raw`` remains the later-format BixCheck T13 Alarm status byte.  Format
    # 04 uses the explicit indicator fields below because its live T13 value
    # did not change between cold/off and the feeder-wheel fault.
    raw: int | None = None
    raw_source: str | None = None
    indicator_source: str | None = None
    indicator_instantaneous_raw: int | None = None
    indicator_active_mask: int | None = None
    indicator_hold_seconds: float | None = None
    indicator_lights: tuple[int, ...] = ()
    fault_code: str | None = None
    fault_label: str | None = None
    fault_evidence: str | None = None
    firebox_door_warning: bool | None = None
    ash_drawer_warning: bool | None = None
    feeder_wheel_warning: bool | None = None


@dataclass(frozen=True, slots=True)
class TelemetryMeasurements:
    board_temperature_raw: int | None = None
    board_temperature_c: int | None = None
    board_temperature_f: int | None = None
    thermocouple_points: int | None = None
    fan_pot_raw: int | None = None
    fan_trim_percent: int | None = None
    feed_pot_raw: int | None = None
    feed_trim_percent: int | None = None
    exhaust_fan_count: int | None = None
    exhaust_fan_rpm: int | None = None
    exhaust_phase_count: int | None = None
    exhaust_phase_microseconds: float | None = None
    convection_percent: int | None = None
    display_led_raw: int | None = None
    ash_level: int | None = None
    ash_target: int | None = None
    feed_on_ticks: int | None = None
    feed_on_seconds: float | None = None
    feed_off_ticks: int | None = None
    feed_off_seconds: float | None = None
    feed_cycle_seconds: float | None = None
    iic_status_raw: int | None = None
    flag_status_raw: int | None = None
    flag_mode: int | None = None
    igniter_current_raw: int | None = None
    fire_door_timer_raw: int | None = None
    ash_drawer_timer_raw: int | None = None
    exhaust_target_count: int | None = None
    exhaust_target_rpm: int | None = None
    blocked_flue_drop_limit: int | None = None
    feed_cycle_table_ticks: int | None = None
    feed_cycle_table_seconds: float | None = None
    feed_cycle_calibration_ticks: int | None = None
    feed_cycle_calibration_seconds: float | None = None
    lean_burn_drop_limit: int | None = None
    format04_firebox_related_raw: int | None = None
    format04_state_unresolved_raw: int | None = None


@dataclass(frozen=True, slots=True)
class Format04StateCandidate:
    """Evidence-labeled composite observation, never a control verifier."""

    code: str
    label: str
    t09_raw: int | None
    t0c_raw: int | None
    t15_raw: int | None
    t09_discriminating: bool | None
    control_verification_eligible: bool
    evidence: str


def decode_format04_state_candidate(
    telemetry: Mapping[int, int],
) -> Format04StateCandidate | None:
    """Classify only the two composite patterns present in live evidence.

    The 2026-08-23 capture proves that T09=07 is not state-discriminating: it
    remained constant before ON, during physically observed UP/DOWN startup
    activity, and after OFF.  T0C/T15 composites are therefore exposed as
    provisional observations, not :class:`OperatingState` values.
    """

    t09 = telemetry.get(0x09)
    t0c = telemetry.get(0x0C)
    t15 = telemetry.get(0x15)
    if t09 is None and t0c is None and t15 is None:
        return None
    t09_discriminating = False if t09 == 0x07 else None
    # T0C.3 is the independently validated thermostat-open bit. Ignore it for
    # this composite so opening the thermostat cannot change the candidate.
    t0c_without_thermostat = t0c & ~0x08 if t0c is not None else None
    if t0c_without_thermostat == 0x20 and t15 == 0x0F:
        code = "cold_off_candidate"
        label = "Cold/off candidate"
        evidence = (
            "T0C base 20 and T15=0F were observed in the cold/off baseline "
            "and again after physical OFF on serial 5215"
        )
    elif t0c_without_thermostat == 0x30 and t15 == 0x08:
        code = "startup_or_control_active_candidate"
        label = "Startup/control-active candidate"
        evidence = (
            "T0C base 30 and T15=08 were observed after physically confirmed "
            "UP/DOWN responses during startup on serial 5215"
        )
    else:
        code = "unclassified"
        label = "Unclassified format-04 state"
        evidence = "No live-correlated composite pattern matches these raw values"
    return Format04StateCandidate(
        code=code,
        label=label,
        t09_raw=t09,
        t0c_raw=t0c,
        t15_raw=t15,
        t09_discriminating=t09_discriminating,
        control_verification_eligible=False,
        evidence=evidence,
    )


@dataclass(frozen=True, slots=True)
class StoveSnapshot:
    profile_key: str | None
    firmware_version: str | None
    data_format: int | None
    fresh: bool
    age_seconds: float | None
    observed_utc: str | None
    panel_buttons: PanelButtons | None
    physical_inputs: PhysicalInputs | None
    thermostat_open: bool | None
    alarms: AlarmState
    operating_state: OperatingState | None
    format04_state_candidate: Format04StateCandidate | None
    igniter_state: IgniterState | None
    current_heat_level: int | None
    target_heat_level: int | None
    telemetry: TelemetryMeasurements
    controller_registers: Mapping[int, int]
    telemetry_bytes: Mapping[int, int]
    status_payloads: Mapping[str, bytes]
    evidence: str

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_key": self.profile_key,
            "firmware_version": self.firmware_version,
            "data_format": (
                f"{self.data_format:02X}" if self.data_format is not None else None
            ),
            "fresh": self.fresh,
            "age_seconds": self.age_seconds,
            "observed_utc": self.observed_utc,
            "panel_buttons": asdict(self.panel_buttons) if self.panel_buttons else None,
            "physical_inputs": asdict(self.physical_inputs) if self.physical_inputs else None,
            "thermostat_open": self.thermostat_open,
            "alarms": asdict(self.alarms),
            "operating_state": (
                asdict(self.operating_state) if self.operating_state else None
            ),
            "format04_state_candidate": (
                asdict(self.format04_state_candidate)
                if self.format04_state_candidate
                else None
            ),
            "igniter_state": asdict(self.igniter_state) if self.igniter_state else None,
            "current_heat_level": self.current_heat_level,
            "target_heat_level": self.target_heat_level,
            "telemetry": asdict(self.telemetry),
            "controller_registers": {
                f"CR{address:02X}": f"{value:02X}"
                for address, value in sorted(self.controller_registers.items())
            },
            "telemetry_bytes": {
                f"T{address:02X}": f"{value:02X}"
                for address, value in sorted(self.telemetry_bytes.items())
            },
            "status_payloads": {
                kind: payload.decode("ascii", errors="backslashreplace")
                for kind, payload in sorted(self.status_payloads.items())
            },
            "evidence": self.evidence,
        }


def decode_stove_snapshot(
    profile: ControllerProfile | None,
    controller: Mapping[int, int],
    telemetry: Mapping[int, int],
    status: Mapping[str, bytes],
    *,
    fresh: bool,
    age_seconds: float | None,
    observed_utc: str | None,
    format04_indicator_mask: int | None = None,
    format04_indicator_hold_seconds: float | None = None,
) -> StoveSnapshot:
    """Decode raw latest values under one explicit controller profile."""

    buttons = None
    if (raw := controller.get(0x01)) is not None:
        buttons = PanelButtons(
            raw=raw,
            off=bool(raw & 0x01),
            on=bool(raw & 0x02),
            up=bool(raw & 0x04),
            down=bool(raw & 0x08),
        )

    inputs = None
    if (raw := controller.get(0x02)) is not None:
        inputs = PhysicalInputs(
            raw=raw,
            burn_drive_limit=bool(raw & 0x01),
            bit_1_unresolved=bool(raw & 0x02),
            fuel_a_corn=bool(raw & 0x04),
            feeder_wheel_sensor=bool(raw & 0x10),
            firebox_door_open=bool(raw & 0x20),
            ash_drawer_open=bool(raw & 0x40),
            bit_7_unresolved=bool(raw & 0x80),
        )

    thermostat_open = (
        bool(controller[0x06] & 0x04) if 0x06 in controller else None
    )
    data_format = profile.data_format if profile else controller.get(0x08)
    later_layout = bool(profile and profile.telemetry_layout is TelemetryLayout.BIXCHECK_5)

    operating_state = None
    format04_state_candidate = None
    igniter_state = None
    current_level = None
    target_level = None
    alarm_raw = None
    alarm_raw_source = None
    indicator_source = None
    indicator_instantaneous_raw = None
    indicator_active_mask = None
    indicator_lights: tuple[int, ...] = ()
    fault_code = None
    fault_label = None
    fault_evidence = None
    firebox_warning = None
    ash_warning = None
    feeder_warning = None
    values: dict[str, object] = {}

    if later_layout:
        if 0x08 in telemetry:
            igniter_state = decode_igniter_state(telemetry[0x08])
        if 0x09 in telemetry:
            operating_state = decode_operating_state(telemetry[0x09])
            if operating_state.phase == "operating":
                current_level = operating_state.level
                target_level = operating_state.level
            elif operating_state.phase == "ramping":
                target_level = operating_state.level

        if 0x00 in telemetry:
            raw_temp = telemetry[0x00]
            celsius = _signed_byte(raw_temp)
            values.update(
                board_temperature_raw=raw_temp,
                board_temperature_c=celsius,
                board_temperature_f=int(celsius * 9 / 5) + 32,
            )
        if 0x01 in telemetry:
            values["thermocouple_points"] = telemetry[0x01]
        for index, prefix in ((0x02, "fan"), (0x03, "feed")):
            if index in telemetry:
                raw_pot = telemetry[index]
                values[f"{prefix}_pot_raw"] = raw_pot
                values[f"{prefix}_trim_percent"] = (raw_pot * 60 // 255) - 30
        if 0x04 in telemetry:
            values["exhaust_fan_count"] = telemetry[0x04]
            values["exhaust_fan_rpm"] = telemetry[0x04] * 24
        if 0x05 in telemetry:
            values["exhaust_phase_count"] = telemetry[0x05]
            values["exhaust_phase_microseconds"] = round(
                8.0 - telemetry[0x05] * 0.0264, 4
            )
        scalar_fields = {
            0x06: "convection_percent",
            0x07: "display_led_raw",
            0x12: "iic_status_raw",
            0x14: "flag_status_raw",
            0x15: "igniter_current_raw",
            0x16: "fire_door_timer_raw",
            0x17: "ash_drawer_timer_raw",
            0x19: "blocked_flue_drop_limit",
            0x1E: "lean_burn_drop_limit",
        }
        for index, name in scalar_fields.items():
            if index in telemetry:
                values[name] = telemetry[index]
        if 0x13 in telemetry:
            alarm_raw = telemetry[0x13]
            alarm_raw_source = "T13"
        if 0x14 in telemetry:
            values["flag_mode"] = (telemetry[0x14] & 0x07) + 1
        if 0x18 in telemetry:
            values["exhaust_target_count"] = telemetry[0x18]
            values["exhaust_target_rpm"] = telemetry[0x18] * 24

        pairs = {
            0x0A: ("ash_level", None),
            0x0C: ("ash_target", None),
            0x0E: ("feed_on_ticks", "feed_on_seconds"),
            0x10: ("feed_off_ticks", "feed_off_seconds"),
            0x1A: ("feed_cycle_table_ticks", "feed_cycle_table_seconds"),
            0x1C: (
                "feed_cycle_calibration_ticks",
                "feed_cycle_calibration_seconds",
            ),
        }
        for high, (raw_name, seconds_name) in pairs.items():
            if (combined := _word(telemetry, high)) is not None:
                values[raw_name] = combined
                if seconds_name:
                    values[seconds_name] = _seconds(combined)
        feed_on = values.get("feed_on_ticks")
        feed_off = values.get("feed_off_ticks")
        if isinstance(feed_on, int) and isinstance(feed_off, int):
            values["feed_cycle_seconds"] = _seconds(feed_on + feed_off)
        evidence = profile.evidence
    elif data_format == 0x04:
        format04_state_candidate = decode_format04_state_candidate(telemetry)
        if 0x03 in telemetry:
            values["fan_pot_raw"] = telemetry[0x03]
        if 0x04 in telemetry:
            values["feed_pot_raw"] = telemetry[0x04]
        if 0x06 in telemetry:
            values["format04_firebox_related_raw"] = telemetry[0x06]
        if 0x08 in telemetry:
            indicator_source = "T08"
            indicator_instantaneous_raw = telemetry[0x08]
            indicator_active_mask = (
                telemetry[0x08]
                if format04_indicator_mask is None
                else format04_indicator_mask
            )
            indication = decode_format04_indicator_mask(indicator_active_mask)
            indicator_lights = indication.lights
            fault_code = indication.code
            fault_label = indication.label
            fault_evidence = indication.evidence
            firebox_warning = bool(indicator_active_mask & 0x08)
            ash_warning = bool(indicator_active_mask & 0x10)
            feeder_warning = bool(indicator_active_mask & 0x80)
        if 0x09 in telemetry:
            values["format04_state_unresolved_raw"] = telemetry[0x09]
        if 0x0C in telemetry:
            thermostat_open = bool(telemetry[0x0C] & 0x08)
        if 0x09 in controller:
            values["fan_pot_raw"] = controller[0x09]
        if 0x0A in controller:
            values["feed_pot_raw"] = controller[0x0A]
        evidence = (
            profile.evidence
            if profile
            else "unknown profile; only common controller inputs were decoded"
        )
    else:
        evidence = "unknown profile; only common controller inputs were decoded"

    return StoveSnapshot(
        profile_key=profile.key if profile else None,
        firmware_version=profile.firmware_version if profile else None,
        data_format=data_format,
        fresh=fresh,
        age_seconds=age_seconds,
        observed_utc=observed_utc,
        panel_buttons=buttons,
        physical_inputs=inputs,
        thermostat_open=thermostat_open,
        alarms=AlarmState(
            raw=alarm_raw,
            raw_source=alarm_raw_source,
            indicator_source=indicator_source,
            indicator_instantaneous_raw=indicator_instantaneous_raw,
            indicator_active_mask=indicator_active_mask,
            indicator_hold_seconds=(
                format04_indicator_hold_seconds
                if indicator_source is not None
                else None
            ),
            indicator_lights=indicator_lights,
            fault_code=fault_code,
            fault_label=fault_label,
            fault_evidence=fault_evidence,
            firebox_door_warning=firebox_warning,
            ash_drawer_warning=ash_warning,
            feeder_wheel_warning=feeder_warning,
        ),
        operating_state=operating_state,
        format04_state_candidate=format04_state_candidate,
        igniter_state=igniter_state,
        current_heat_level=current_level,
        target_heat_level=target_level,
        telemetry=TelemetryMeasurements(**values),
        controller_registers=dict(controller),
        telemetry_bytes=dict(telemetry),
        status_payloads=dict(status),
        evidence=evidence,
    )
