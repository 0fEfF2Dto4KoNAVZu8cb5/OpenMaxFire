# Fault and flashing-indicator protocol

OpenMaxFire treats fault reporting as profile-specific. The live firmware
2.02/data-format-04 controller and the preserved BixCheck 5.x generations do
not use the same telemetry slots for the same meanings.

## Firmware 2.02 / data format 04

On controller serial 5215, `T08` is an instantaneous bitmap of the eight
flashing heat-level/problem indicators. Bit zero corresponds to light 1 and bit
seven corresponds to light 8.

This is not a stable fault register. During a visible flash, the wire value
alternates between the active mask and zero. The captured feeder-wheel fault,
for example, contained:

```text
T0800
T0880
T0800
T0880
```

A consumer must therefore observe a time window rather than inspect only the
latest `T08` byte. `MonitorState` retains bits for eight seconds of observed
`T08` stream time. The live fault-8 evidence had a maximum interval of about
6.14 seconds between `T08=80` samples. The retention clock advances only when
another `T08` sample arrives; loss of serial traffic makes the snapshot stale
instead of falsely clearing a previously observed alarm.

### Indicator patterns

| Mask | Lights | Factory meaning | Serial evidence |
| ---: | --- | --- | --- |
| `01` | 1 | Power interruption during operation | Light mapping inferred |
| `02` | 2 | Operating temperature not reached | Light mapping inferred |
| `04` | 3 | Exhaust system or hopper area overheating | Light mapping inferred |
| `06` | 2 + 3 | Empty hopper or possible blocked flue | Light mapping inferred |
| `08` | 4 | Firebox door open | Live-confirmed |
| `10` | 5 | Ash drawer open | Live-confirmed |
| `20` | 6 | Exhaust-fan failure | Light mapping inferred |
| `40` | 7 | Fire-pot mechanical malfunction | Light mapping inferred |
| `41` | 7 + 1 | Left igniter failure | Light mapping inferred |
| `42` | 7 + 2 | Right igniter failure | Light mapping inferred |
| `43` | 7 + 1 + 2 | Both igniters failed | Light mapping inferred |
| `47` | 7 + 1 through 3 | Internal or possible igniter electrical fault | Light mapping inferred |
| `80` | 8 | Feeder-wheel failure | Live-confirmed |

“Light mapping inferred” means the fault description and light combination are
factory-documented, while the corresponding serial bits follow the
live-confirmed one-bit-per-light layout. Those patterns have not been induced
on the physical stove. Unknown combinations remain raw masks and light-number
lists; OpenMaxFire does not invent a name.

The stable physical input should be used when one exists:

- firebox door: `CR02 & 0x20`;
- ash drawer: `CR02 & 0x40`;
- feeder-wheel sensor current state: `CR02 & 0x10`; and
- feeder-wheel interval: `CR07`.

Those inputs help diagnose a condition but are not substitutes for the
controller's latched/flashing problem indication.

## Preserved BixCheck formats 05 and 07

BixCheck 5.0.21, 5.5.00, and 5.5.01 use the later telemetry layout:

| Slot | BixCheck field | Recovered behavior |
| --- | --- | --- |
| `T07` | Display LED | Retained/displayed as the panel LED value |
| `T08` | Igniter state | Low three bits decoded as left/right igniter good/failure state |
| `T09` | State control | Decoded into cooldown, off, startup, error, operating, ramping, and ash-dump families |
| `T13` | Alarm status | Displayed as raw hexadecimal “Alarm mode” |

No named `T13` bit decoder was recovered from BixCheck. OpenMaxFire therefore
preserves later-format `T13` as `AlarmState.raw`, reports its source, and does
not apply the format-04 `T08` light table to it. Later-format fault semantics
remain a firmware-analysis and live-validation task.

## Evidence files

- Initial format-04 door/drawer correlations:
  [`research/live/2026-08-22-fw202-format04/`](../../research/live/2026-08-22-fw202-format04/)
- Live control and feeder-wheel fault:
  [`research/live/2026-08-23-fw202-control-faults/`](../../research/live/2026-08-23-fw202-control-faults/)
- Static BixCheck field reconstruction:
  [telemetry fields](telemetry-fields.md)
