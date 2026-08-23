# Fault-state API

The reusable API exposes raw, decoded, temporal, and evidence information in
`StoveSnapshot.alarms`. It does not require a CLI, GUI, or Home Assistant
consumer to duplicate firmware-specific fault logic.

## Typed snapshot contract

`AlarmState` contains:

| Field | Meaning |
| --- | --- |
| `raw` / `raw_source` | Later-format raw alarm value and its wire source (`T13`) |
| `indicator_source` | Format-04 flashing-indicator source (`T08`) |
| `indicator_instantaneous_raw` | Latest `T08` sample, which may be zero during a dark flash phase |
| `indicator_active_mask` | Bits retained across the configured observation window |
| `indicator_hold_seconds` | Retention interval used by the monitor |
| `indicator_lights` | One-based physical light numbers represented by the active mask |
| `fault_code` / `fault_label` | Stable machine code and human description for a recognized exact pattern |
| `fault_evidence` | Live-confirmed, factory-documented/inferred, or unknown-pattern boundary |
| `firebox_door_warning` | Convenience boolean for format-04 light 4 |
| `ash_drawer_warning` | Convenience boolean for format-04 light 5 |
| `feeder_wheel_warning` | Convenience boolean for format-04 light 8 |

Example:

```python
from openmaxfire import ControllerSession

with ControllerSession.connect(
    "/dev/ttyUSB0",
    baudrate=9600,
    format04_indicator_hold=8.0,
) as stove:
    snapshot = stove.poll_snapshot(request_delay=1.0)
    alarm = snapshot.alarms
    if snapshot.fresh and alarm.fault_code:
        print(alarm.fault_code, alarm.indicator_lights, alarm.fault_evidence)
```

For a format-04 feeder-wheel fault sampled during the lamp's dark phase, the
important distinction is:

```python
alarm.indicator_instantaneous_raw == 0x00
alarm.indicator_active_mask == 0x80
alarm.indicator_lights == (8,)
alarm.fault_code == "feeder_wheel_failure"
```

## Decoder API

Consumers that already have an accumulated mask may call:

```python
from openmaxfire import decode_format04_indicator_mask

fault = decode_format04_indicator_mask(0x06)
assert fault.lights == (2, 3)
assert fault.code == "empty_hopper_or_possible_blocked_flue"
```

`FORMAT04_FAULT_PATTERNS` exposes the immutable known-pattern table, while
`indicator_lights(mask)` provides lossless bit-to-light conversion for an
unknown combination.

## Temporal behavior

`MonitorState`, `ControllerSession`, and `replay_capture` default
`format04_indicator_hold` to eight seconds. A bit is
active while its most recent nonzero observation is within that interval of
the latest received `T08` sample. Sustained zero samples clear it. If serial
traffic stops, `StoveSnapshot.fresh` becomes false; clients must never treat a
stale snapshot as proof that an alarm cleared.

The legacy dictionary snapshot also exposes:

```json
{
  "fault_indicators": {
    "source": "T08",
    "instantaneous_raw": "00",
    "active_mask": "80",
    "hold_seconds": 8.0,
    "lights": [8],
    "fault_code": "feeder_wheel_failure",
    "fault_label": "Feeder-wheel failure",
    "recognized": true
  }
}
```

Later format-05/07 snapshots instead preserve BixCheck's `T13` alarm byte as
raw data. The API does not reuse the format-04 indicator decoder across that
profile boundary.

## Safety boundary

Fault decoding is observational. OpenMaxFire does not suppress, acknowledge,
bypass, or replace the controller's factory shutdown and interlock behavior.
Dangerous faults do not need to be deliberately induced to populate the
factory-documented table; unobserved serial mappings retain their inferred
evidence label.
