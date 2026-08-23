"""Read-only live monitoring and capture replay.

The monitor deliberately sends only controller ``CR`` reads.  It preserves raw
values alongside conservative interpretations so format-specific observations
cannot be mistaken for universal controller semantics.
"""

from __future__ import annotations

import json
import math
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Mapping, TextIO

from .client import StoveIdentity
from .faults import (
    FORMAT04_INDICATOR_HOLD_SECONDS,
    decode_format04_indicator_mask,
)
from .models import StoveSnapshot, decode_stove_snapshot
from .profiles import (
    ControllerProfile,
    TelemetryLayout,
    profile_for_data_format,
    select_profile,
)
from .protocol import (
    TELEMETRY_WORD_PAIRS,
    AddressedResponse,
    ResponseFrame,
    StatusResponse,
    TelemetryResponse,
    combine_telemetry_word,
    decode_igniter_state,
    decode_operating_state,
    parse_response_line,
)


MONITOR_SNAPSHOT_SCHEMA = "openmaxfire.monitor-snapshot.v1"
MONITOR_LOG_SCHEMA = "openmaxfire.monitor-log.v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hex_map(prefix: str, values: Mapping[int, int]) -> dict[str, str]:
    return {f"{prefix}{address:02X}": f"{value:02X}" for address, value in sorted(values.items())}


@dataclass(frozen=True, slots=True)
class ReplayResult:
    """Summary returned after replaying one serial-capture JSONL file."""

    state: "MonitorState"
    session_metadata: Mapping[str, object]
    traffic_events: int
    rx_chunks: int
    rx_bytes: int
    parsed_frames: int
    malformed_lines: int
    trailing_bytes: bytes
    last_monotonic_ns: int | None


class MonitorState:
    """Latest-value state assembled from addressed and telemetry responses."""

    def __init__(
        self,
        *,
        stale_after: float = 10.0,
        format04_indicator_hold: float = FORMAT04_INDICATOR_HOLD_SECONDS,
        profile: ControllerProfile | None = None,
    ):
        if not isinstance(stale_after, (int, float)) or not math.isfinite(stale_after):
            raise ValueError("stale_after must be a finite number")
        if stale_after <= 0:
            raise ValueError("stale_after must be greater than zero")
        if (
            isinstance(format04_indicator_hold, bool)
            or not isinstance(format04_indicator_hold, (int, float))
            or not math.isfinite(format04_indicator_hold)
        ):
            raise ValueError("format04_indicator_hold must be a finite number")
        if format04_indicator_hold <= 0:
            raise ValueError("format04_indicator_hold must be greater than zero")
        self.stale_after = float(stale_after)
        self.format04_indicator_hold = float(format04_indicator_hold)
        self.profile = profile
        self.controller: dict[int, int] = {}
        self.telemetry: dict[int, int] = {}
        self.status: dict[str, bytes] = {}
        self.frame_count = 0
        self.addressed_frame_count = 0
        self.telemetry_frame_count = 0
        self.status_frame_count = 0
        self.last_monotonic_ns: int | None = None
        self.last_observed_utc: str | None = None
        self._t08_latest_sample_ns: int | None = None
        self._t08_bit_last_on_ns: list[int | None] = [None] * 8

    def observe(
        self,
        frame: ResponseFrame,
        *,
        monotonic_ns: int | None = None,
        created_utc: str | None = None,
    ) -> None:
        """Apply one parsed frame without discarding its raw byte values."""

        observed_ns = time.monotonic_ns() if monotonic_ns is None else monotonic_ns
        if not isinstance(observed_ns, int) or observed_ns < 0:
            raise ValueError("monotonic_ns must be a nonnegative integer")
        self.last_monotonic_ns = observed_ns
        self.last_observed_utc = created_utc or _utc_now()
        self.frame_count += 1

        if isinstance(frame, AddressedResponse):
            self.addressed_frame_count += 1
            if frame.unit == "C" and frame.opcode == "R":
                self.controller[frame.address] = frame.value
            return
        if isinstance(frame, TelemetryResponse):
            self.telemetry_frame_count += 1
            for offset, value in enumerate(frame.values):
                address = frame.index + offset
                if address <= 0xFF:
                    self.telemetry[address] = value
                    if address == 0x08:
                        self._t08_latest_sample_ns = observed_ns
                        for bit in range(8):
                            if value & (1 << bit):
                                self._t08_bit_last_on_ns[bit] = observed_ns
            return
        if isinstance(frame, StatusResponse):
            self.status_frame_count += 1
            self.status[frame.kind] = frame.payload
            return
        raise TypeError(f"unsupported monitor frame: {type(frame).__name__}")

    def _effective_profile(self) -> ControllerProfile | None:
        if self.profile is not None:
            return self.profile
        required = (0x00, 0x08, 0x0B, 0x0C, 0x0D, 0x0E)
        if all(address in self.controller for address in required):
            identity = StoveIdentity(
                probe=self.controller[0x00],
                data_format=self.controller[0x08],
                firmware_major=self.controller[0x0B],
                firmware_minor=self.controller[0x0C],
                reserved=self.controller[0x0D],
                version_readback=self.controller[0x0E],
            )
            if (profile := select_profile(identity)) is not None:
                return profile
        if (data_format := self.controller.get(0x08)) is not None:
            return profile_for_data_format(data_format)
        return None

    def _freshness(self, now_monotonic_ns: int) -> tuple[float | None, bool]:
        if self.last_monotonic_ns is None:
            return None, True
        age = max(
            0.0,
            (now_monotonic_ns - self.last_monotonic_ns) / 1_000_000_000,
        )
        return age, age >= self.stale_after

    def _format04_indicator_mask(self) -> int | None:
        """Return T08 bits observed recently enough to span a dark flash phase.

        The age calculation uses the latest *observed T08 sample*, not wall
        time.  If serial traffic stops, the overall snapshot becomes stale but
        a previously observed alarm is not falsely reported as cleared.
        """

        if self._t08_latest_sample_ns is None:
            return None
        hold_ns = int(self.format04_indicator_hold * 1_000_000_000)
        mask = 0
        for bit, last_on_ns in enumerate(self._t08_bit_last_on_ns):
            if (
                last_on_ns is not None
                and self._t08_latest_sample_ns - last_on_ns <= hold_ns
            ):
                mask |= 1 << bit
        return mask

    def typed_snapshot(
        self,
        *,
        now_monotonic_ns: int | None = None,
    ) -> StoveSnapshot:
        """Return the profile-driven typed API view of the latest raw state."""

        now_ns = time.monotonic_ns() if now_monotonic_ns is None else now_monotonic_ns
        if not isinstance(now_ns, int) or now_ns < 0:
            raise ValueError("now_monotonic_ns must be a nonnegative integer")
        age_seconds, stale = self._freshness(now_ns)
        return decode_stove_snapshot(
            self._effective_profile(),
            self.controller,
            self.telemetry,
            self.status,
            fresh=not stale,
            age_seconds=(
                round(age_seconds, 6) if age_seconds is not None else None
            ),
            observed_utc=self.last_observed_utc,
            format04_indicator_mask=self._format04_indicator_mask(),
            format04_indicator_hold_seconds=self.format04_indicator_hold,
        )

    def _decoded_inputs(self) -> dict[str, object]:
        decoded: dict[str, object] = {}
        if (value := self.controller.get(0x01)) is not None:
            decoded["panel_buttons"] = {
                "off": bool(value & 0x01),
                "on": bool(value & 0x02),
                "up": bool(value & 0x04),
                "down": bool(value & 0x08),
                "raw": f"{value:02X}",
            }
        if (value := self.controller.get(0x02)) is not None:
            decoded["physical_inputs"] = {
                "burn_drive_limit": bool(value & 0x01),
                "bit_1_unresolved": bool(value & 0x02),
                "fuel_a_corn": bool(value & 0x04),
                "feeder_wheel_sensor": bool(value & 0x10),
                "firebox_door_open": bool(value & 0x20),
                "ash_drawer_open": bool(value & 0x40),
                "bit_7_unresolved": bool(value & 0x80),
                "raw": f"{value:02X}",
            }
        if (value := self.controller.get(0x06)) is not None:
            decoded["thermostat_open"] = bool(value & 0x04)
            decoded["thermostat_register_raw"] = f"{value:02X}"
        return decoded

    def _decoded_telemetry(self) -> dict[str, object]:
        decoded: dict[str, object] = {}
        data_format = self.controller.get(0x08)
        profile = self._effective_profile()
        later_layout = bool(
            profile and profile.telemetry_layout is TelemetryLayout.BIXCHECK_5
        )
        if (value := self.telemetry.get(0x08)) is not None:
            if data_format == 0x04:
                active_mask = self._format04_indicator_mask()
                active_mask = value if active_mask is None else active_mask
                indication = decode_format04_indicator_mask(active_mask)
                decoded["fault_indicators"] = {
                    "source": "T08",
                    "instantaneous_raw": f"{value:02X}",
                    "active_mask": f"{active_mask:02X}",
                    "hold_seconds": self.format04_indicator_hold,
                    "lights": list(indication.lights),
                    "fault_code": indication.code,
                    "fault_label": indication.label,
                    "evidence": indication.evidence,
                    "recognized": indication.recognized,
                }
                decoded["warning_flash_bits"] = {
                    "firebox_door": bool(active_mask & 0x08),
                    "ash_drawer": bool(active_mask & 0x10),
                    "feeder_wheel": bool(active_mask & 0x80),
                }
            if later_layout:
                decoded["bixcheck_55_igniter_display"] = asdict(
                    decode_igniter_state(value)
                )
        if (value := self.telemetry.get(0x09)) is not None and later_layout:
            decoded["operating_state"] = asdict(decode_operating_state(value))
        if (value := self.telemetry.get(0x13)) is not None and later_layout:
            decoded["alarm_status"] = {
                "source": "T13",
                "raw": f"{value:02X}",
                "decoded": False,
                "evidence": "BixCheck displays Alarm mode as raw hexadecimal",
            }

        # These fields were correlated on serial 5215's format-04 controller.
        # They remain explicitly nested under a format-specific key.
        if data_format == 0x04:
            format04: dict[str, object] = {}
            names = {
                0x03: "fan_trim_raw",
                0x04: "feed_trim_raw",
                0x06: "firebox_related_raw",
            }
            for index, name in names.items():
                if index in self.telemetry:
                    format04[name] = self.telemetry[index]
            if 0x0C in self.telemetry:
                format04["thermostat_open"] = bool(self.telemetry[0x0C] & 0x08)
                format04["thermostat_telemetry_raw"] = f"{self.telemetry[0x0C]:02X}"
            if 0x09 in self.telemetry:
                format04["t09_meaning_unresolved_raw"] = self.telemetry[0x09]
            if 0x09 in self.controller:
                format04["fan_pot_raw"] = self.controller[0x09]
            if 0x0A in self.controller:
                format04["feed_pot_raw"] = self.controller[0x0A]
            if format04:
                decoded["format04_live_correlations"] = format04
        return decoded

    def snapshot(
        self,
        *,
        now_monotonic_ns: int | None = None,
        generated_utc: str | None = None,
        source: str = "live",
    ) -> dict[str, object]:
        """Return a lossless latest-value snapshot with freshness diagnostics."""

        now_ns = time.monotonic_ns() if now_monotonic_ns is None else now_monotonic_ns
        if not isinstance(now_ns, int) or now_ns < 0:
            raise ValueError("now_monotonic_ns must be a nonnegative integer")
        age_seconds, stale = self._freshness(now_ns)

        words: dict[str, object] = {}
        data_format = self.controller.get(0x08)
        for high_index, label in TELEMETRY_WORD_PAIRS.items():
            if high_index in self.telemetry and high_index + 1 in self.telemetry:
                value = combine_telemetry_word(
                    self.telemetry[high_index], self.telemetry[high_index + 1]
                )
                word: dict[str, object] = {
                    "value": value,
                    "hex": f"{value:04X}",
                }
                if data_format in (0x05, 0x07):
                    word["label"] = label
                else:
                    word["candidate_label_from_later_formats"] = label
                words[f"T{high_index:02X}/T{high_index + 1:02X}"] = word

        decoded = self._decoded_inputs()
        decoded.update(self._decoded_telemetry())
        profile = self._effective_profile()
        return {
            "schema": MONITOR_SNAPSHOT_SCHEMA,
            "source": source,
            "generated_utc": generated_utc or _utc_now(),
            "last_observed_utc": self.last_observed_utc,
            "fresh": not stale,
            "stale": stale,
            "age_seconds": round(age_seconds, 6) if age_seconds is not None else None,
            "stale_after_seconds": self.stale_after,
            "profile": profile.to_dict() if profile else None,
            "frame_counts": {
                "total": self.frame_count,
                "addressed": self.addressed_frame_count,
                "telemetry": self.telemetry_frame_count,
                "status": self.status_frame_count,
            },
            "controller_registers": _hex_map("CR", self.controller),
            "telemetry_bytes": _hex_map("T", self.telemetry),
            "telemetry_words": words,
            "status_payloads": {
                kind: payload.decode("ascii", errors="backslashreplace")
                for kind, payload in sorted(self.status.items())
            },
            "decoded": decoded,
            "evidence_boundary": (
                "Raw values are preserved. Named format-04 telemetry fields are limited to "
                "live correlations from serial 5215. Fault lights 4, 5, and 8 are "
                "live-confirmed; other named fault patterns come from the factory manual "
                "with serial bit positions inferred from the confirmed bitmap."
            ),
        }


class JsonlMonitorRecorder:
    """Write durable monitor snapshots without silently replacing a session."""

    def __init__(
        self,
        path: str | Path,
        *,
        metadata: Mapping[str, object] | None = None,
        overwrite: bool = False,
    ):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._stream: TextIO = self.path.open(
            "w" if overwrite else "x", encoding="utf-8", newline="\n"
        )
        self._sequence = 0
        self._write(
            {
                "schema": MONITOR_LOG_SCHEMA,
                "event": "session",
                "created_utc": _utc_now(),
                "metadata": dict(metadata or {}),
            }
        )

    def _write(self, event: Mapping[str, object]) -> None:
        self._stream.write(json.dumps(dict(event), sort_keys=True) + "\n")
        self._stream.flush()

    def record(self, snapshot: Mapping[str, object]) -> None:
        self._sequence += 1
        self._write(
            {
                "schema": MONITOR_LOG_SCHEMA,
                "event": "snapshot",
                "sequence": self._sequence,
                "snapshot": dict(snapshot),
            }
        )

    def close(self) -> None:
        if not self._stream.closed:
            self._stream.close()


def format_monitor_summary(snapshot: Mapping[str, object]) -> str:
    """Return a compact human-readable status line for one snapshot."""

    decoded = snapshot.get("decoded")
    decoded = decoded if isinstance(decoded, Mapping) else {}
    physical = decoded.get("physical_inputs")
    physical = physical if isinstance(physical, Mapping) else {}
    format04 = decoded.get("format04_live_correlations")
    format04 = format04 if isinstance(format04, Mapping) else {}
    operating = decoded.get("operating_state")
    operating = operating if isinstance(operating, Mapping) else {}
    warnings = decoded.get("warning_flash_bits")
    warnings = warnings if isinstance(warnings, Mapping) else {}
    fault = decoded.get("fault_indicators")
    fault = fault if isinstance(fault, Mapping) else {}

    freshness = "STALE" if snapshot.get("stale") else "fresh"
    age = snapshot.get("age_seconds")
    age_text = "unknown" if age is None else f"{float(age):.2f}s"
    parts = [
        str(snapshot.get("last_observed_utc") or snapshot.get("generated_utc") or "unknown-time"),
        freshness,
        f"age={age_text}",
    ]
    if operating.get("label"):
        parts.append(f"state={operating['label']}")
    if physical:
        parts.extend(
            (
                "door=" + ("open" if physical.get("firebox_door_open") else "closed"),
                "drawer=" + ("open" if physical.get("ash_drawer_open") else "closed"),
                "fuel=" + ("corn" if physical.get("fuel_a_corn") else "wood"),
            )
        )
    if "thermostat_open" in decoded:
        parts.append("thermostat=" + ("open" if decoded["thermostat_open"] else "closed"))
    elif "thermostat_open" in format04:
        parts.append(
            "thermostat=" + ("open" if format04["thermostat_open"] else "closed")
        )
    if warnings.get("firebox_door"):
        parts.append("door-warning=on")
    if warnings.get("ash_drawer"):
        parts.append("drawer-warning=on")
    if warnings.get("feeder_wheel"):
        parts.append("feeder-warning=on")
    if fault.get("fault_code"):
        parts.append(f"fault={fault['fault_code']}")
    elif fault.get("lights"):
        lights = ",".join(str(item) for item in fault["lights"])
        parts.append(f"fault-lights={lights}")
    if "fan_pot_raw" in format04:
        parts.append(f"fan-pot={format04['fan_pot_raw']}")
    elif "fan_trim_raw" in format04:
        parts.append(f"fan-trim={format04['fan_trim_raw']}")
    if "feed_pot_raw" in format04:
        parts.append(f"feed-pot={format04['feed_pot_raw']}")
    elif "feed_trim_raw" in format04:
        parts.append(f"feed-trim={format04['feed_trim_raw']}")
    counts = snapshot.get("frame_counts")
    if isinstance(counts, Mapping):
        parts.append(f"frames={counts.get('total', 0)}")
    return " ".join(parts)


def replay_capture(
    path: str | Path,
    *,
    stale_after: float = 10.0,
    format04_indicator_hold: float = FORMAT04_INDICATOR_HOLD_SECONDS,
) -> ReplayResult:
    """Replay exact RX chunks from an ``openmaxfire.serial-capture.v1`` log."""

    source = Path(path)
    state = MonitorState(
        stale_after=stale_after,
        format04_indicator_hold=format04_indicator_hold,
    )
    session_metadata: Mapping[str, object] = {}
    traffic_events = 0
    rx_chunks = 0
    rx_bytes = 0
    parsed_frames = 0
    malformed_lines = 0
    buffer = bytearray()
    last_monotonic_ns: int | None = None

    with source.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSON on line {line_number}") from exc
            if event.get("event") == "session":
                metadata = event.get("metadata")
                if isinstance(metadata, Mapping):
                    session_metadata = dict(metadata)
                continue
            if event.get("event") != "traffic":
                continue
            traffic_events += 1
            if event.get("direction") != "rx":
                continue
            try:
                data = bytes.fromhex(str(event["data_hex"]))
            except (KeyError, ValueError) as exc:
                raise ValueError(f"invalid RX data_hex on line {line_number}") from exc
            rx_chunks += 1
            rx_bytes += len(data)
            buffer.extend(data)
            value = event.get("monotonic_ns")
            event_ns = value if isinstance(value, int) and value >= 0 else None
            if event_ns is not None:
                last_monotonic_ns = event_ns
            created_utc = event.get("created_utc")
            created_text = created_utc if isinstance(created_utc, str) else None

            while True:
                delimiters = [
                    position
                    for marker in (b"\r", b"\n")
                    if (position := buffer.find(marker)) >= 0
                ]
                if not delimiters:
                    break
                end = min(delimiters)
                raw = bytes(buffer[:end])
                del buffer[: end + 1]
                while buffer[:1] in (b"\r", b"\n"):
                    del buffer[:1]
                if not raw:
                    continue
                try:
                    frame = parse_response_line(raw)
                except ValueError:
                    malformed_lines += 1
                    continue
                state.observe(frame, monotonic_ns=event_ns, created_utc=created_text)
                parsed_frames += 1

    return ReplayResult(
        state=state,
        session_metadata=session_metadata,
        traffic_events=traffic_events,
        rx_chunks=rx_chunks,
        rx_bytes=rx_bytes,
        parsed_frames=parsed_frames,
        malformed_lines=malformed_lines,
        trailing_bytes=bytes(buffer),
        last_monotonic_ns=last_monotonic_ns,
    )
