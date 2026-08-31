# BixCheck telemetry map

Status: BixCheck display records and the complete periodic firmware producer
have been statically reconstructed; every periodic slot has also executed
through the real producer and UART sender in offline emulation. A read-only
physical 2.06 session has now validated the Cooldown/Off state transition,
fan command/target/feedback fields, and flashing-light event described below;
other later-format values remain unvalidated on a physical stove.

> **Format boundary:** serial 5215's original controller identified as firmware
> 2.02/data format 04. Its shorter `T00`-`T15` stream does not match this later
> format-05/07 logical table position-for-position. A separately programmed
> controller was subsequently live-validated as 2.06/format 05. Original-chip
> format-04 correlations are documented separately in
> [the firmware-2.02 report](../reverse-engineering/live-fw202-format04.md).
> Its profile-specific flashing-light and fault behavior is documented in
> [fault and flashing-indicator protocol](faults.md).

The preserved 2.02 control capture proves that format-04 `T09=07` is not the
later operating-state field. Exact recovered code resolves the format boundary:
2.02 T0C reads state RAM 0x4C, while its T09 reads unrelated RAM 0x2D and T15
has no state assignment. OpenMaxFire applies the shared family decoder to T0C
for format 04 and to T09 for later formats. Live `T0C=20`/Off and
`T0C=30`/Prefill match those exact paths.

## Wire framing

All four recovered application generations send exactly one telemetry byte per
physical line:

```text
T<index:02x><value:02x>\n
```

For example, the 16-bit value `0x1234` beginning at T0A is transmitted as two
lines, not one seven-character line:

```text
T0a12\n
T0b34\n
```

BixCheck stores the first byte, shifts it left eight bits, and adds the next
slot. OpenMaxFire still accepts the previously documented `T0A1234` host form
for capture compatibility, but no such physical sender path exists in the
preserved application firmware.

Some producer slots first emit an addressed diagnostic line of the form
`DW<address><value>\n`, followed by the T line. BixCheck stores D and T in
separate 256-byte arrays. These D values are auxiliary flags/measurements; they
are not the high byte of the T value. The exact version/slot combinations and
addresses are preserved in `telemetry-slot-matrix.csv`.

| Firmware | Periodic producer | Index RAM | Value RAM | Aux RAM | Sender | Last periodic T slot |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2.02 | `0DA3` | `0A0` | `0CA` | `0CB` | `0D8A` | `15` |
| 2.06 | `0CF2` | `0A1` | `0CA` | `0CB` | `0783` | `1D` |
| 2.70 | `0DBD` | `0A0` | `0C8` | `0C9` | `0771` | `1D` |
| 2.71 | `0DA6` | `0A0` | `0C8` | `0C9` | `0771` | `1E` |

The normal scheduler calls these producers at `0ECC`, `0E5D`, `0F4F`, and
`0F1A`, respectively. The emulator enters each slot directly so it can prove producer
and UART behavior without claiming to reproduce the scheduler's real cadence
or gates.

## Logical fields

`C` and `V` rows below are BixCheck-computed/display records, not additional
T frames. A two-byte row names both physical T slots.

| Wire slot(s) | Logical bytes | Field | Statically recovered display interpretation |
| --- | ---: | --- | --- |
| T00 | 1 | Control-board temperature | signed °C; °F = trunc(`C * 9 / 5`) + 32 |
| T01 | 1 | Thermocouple | uncalibrated `TC Points` |
| T02 | 1 | Fan potentiometer | raw byte; format 05/07 trim = `raw * 60 / 255 - 30` percent |
| T03 | 1 | Feed potentiometer | raw byte; format 05/07 trim = `raw * 60 / 255 - 30` percent |
| T04 | 1 | Exhaust fan speed | raw count; displayed RPM = `raw * 24` |
| T05 | 1 | Exhaust fan phase | raw count; displayed µs = `8.0 - raw * 0.0264` |
| T06 | 1 | Convection fan level | raw percent |
| T07 | 1 | Display LED | decoded LED display |
| T08 | 1 | Igniter state | exact low-three-bit decoder below |
| C00 | computed | Current heat level | derived from state/display data |
| C00 | computed | Target heat level | derived from state/display data |
| T09 | 1 | Operating state | exact family/substate decoder below |
| T0A + T0B | 2 | Ash level | unsigned big-endian 16-bit value |
| T0C + T0D | 2 | Ash target | unsigned big-endian 16-bit value |
| T0E + T0F | 2 | Feed on time | unsigned big-endian ticks; seconds = ticks / 120 |
| T10 + T11 | 2 | Feed off time | unsigned big-endian ticks; seconds = ticks / 120 |
| C00 | computed | Feed cycle time | `(feed_on + feed_off) / 120` seconds |
| T12 | 1 | IIC status | raw status byte; no named decode in preserved BixCheck |
| T13 | 1 | Alarm status | raw status byte; no named decode in preserved BixCheck |
| T14 | 1 | Flag status | raw byte; BixCheck `Flag mode` = `(raw & 7) + 1` |
| T15 | 1 | Igniter current | raw byte/state display |
| T16 | 1 | Fire-door timer | raw ticks; BixCheck manual defines 1/3-second units; owner manual says about one minute open causes shutdown |
| T17 | 1 | Ash-drawer timer | raw ticks; BixCheck manual defines 5 1/3-second units; owner manual says open blocks startup and about 20 minutes causes shutdown |
| T18 | 1 | Exhaust fan target | raw count; displayed RPM = `raw * 24` |
| T19 | 1 | Drop limit / BF drop limit | raw thermocouple-point threshold |
| T1A + T1B | 2 | Feed cycle table | unsigned big-endian ticks; seconds = ticks / 120 |
| T1C + T1D | 2 | Feed cycle calibration | unsigned big-endian ticks; seconds = ticks / 120 |
| T1E | 1 | LB drop limit (2.71) | raw thermocouple-point threshold |
| V1B / V1C | computed | Time to ash dump | hours:minutes; V1B in 5.0.21/5.5.00, V1C in 5.5.01 |
| C00 | computed | Telemetry mode | UI state |
| C20 | computed | LED no-log/event path | UI state; related 2.06/2.70/2.71 event T20 described below |

The RPM and phase formulas above reproduce BixCheck's display math; they do
not make those values calibrated measurements. The vendor manual explicitly
describes the thermocouple as uncalibrated points and the exhaust phase as an
internal time. T00 is ambient/control-board temperature, not fire temperature.

Older data formats (`CR08 <= 2`) contain a dormant potentiometer formula of
`raw * 40 / 255 - 20`; every preserved 2.06/2.70/2.71 pairing reports format
05 or 07 and therefore uses the ±30-percent formula.

## Exact T08 igniter decoder

All three BixCheck generations mask the T08 byte with `0x07`. The following
labels are literal strings reconstructed from the vendor update routine; `L`
and `R` denote its left/right igniter wording.

| `T08 & 0x07` | BixCheck display |
| ---: | --- |
| `0` | `L R failed` |
| `1` | `R failed` |
| `2` | `L failed` |
| `7` | `L R good` |
| `3`-`6` | `Error` |

The preserved application does not contain an equivalent named bit decoder
for T12 IIC status or T13 alarm status. It formats those bytes as hexadecimal.
For T14 it retains the raw byte and separately displays the low-three-bit mode
as one through eight. Semantic names for those controller bits therefore
remain a firmware/live-correlation question rather than a BixCheck feature.

This later-format T13 behavior is deliberately separate from the live
format-04 controller. On firmware 2.02, T13 remained `BA` in both cold/off and
feeder-wheel-fault captures, while T08 alternated `00`/`80` with physical light
8. OpenMaxFire does not apply either profile's slot meaning to the other.

## 2.71 producer sources

This table follows the 2.71 producer from each slot to the byte copied into its
T-value scratch register. `B0` and `B1` denote PIC file-register banks, not
protocol unit spaces.

| Slot | Firmware source | Slot | Firmware source |
| --- | --- | --- | --- |
| T00 | B1 `A2` | T10 | B0 `3E` |
| T01 | B0 `57` | T11 | B0 `3D` |
| T02 | B0 `2E` | T12 | B0 `7E` |
| T03 | B0 `2F` | T13 | B0 `4F` |
| T04 | B0 `34` | T14 | B0 `5D` |
| T05 | B0 `37` | T15 | B0 `58` |
| T06 | B0 `29` | T16 | B0 `5F` |
| T07 | B0 `48` | T17 | B0 `5E` |
| T08 | B0 `2D` | T18 | B0 `33` |
| T09 | B0 `4C` | T19 | computed by routine `01D1` |
| T0A | B0 `3A` | T1A | B1 `C7` |
| T0B | B0 `39` | T1B | B1 `C6` |
| T0C | computed high byte from routine `0113` (`79`) | T1C | B0 `40` |
| T0D | computed low byte from routine `0113` (`78`) | T1D | B0 `3F` |
| T0E | B0 `45` | T1E | computed/scaled 2.71 path |
| T0F | B0 `44` |  |  |

All 113 version/slot combinations (22 + 30 + 30 + 31) reach their real firmware
sender in the synthetic harness. The table immediately above is the later
layout; format-04 source rows remain in the generated matrices. The complete
access dependency sets and exact
write PCs are generated as `telemetry-producer-access-summary.csv` and
`telemetry-slot-matrix.csv` under
`reverse-engineering/firmware/emulation/deep/`.

## Exact state-family decoder (later T09; 2.02 T0C)

BixCheck 5.5.01 masks T09 with `0x7F` before decoding, and the firmware
dispatchers independently mask the shared state byte with `0x70`. Firmware
2.02 emits that byte at T0C; later versions emit it at T09. Bit 7 therefore
does not create a new operating family. The low three bits carry a startup
substate or zero-based heat level; bit 3 is the thermostat flag in operating
family 4.

| Normalized pattern | BixCheck display |
| --- | --- |
| `1x` | `Cooldown` |
| `2x` | `Off` |
| `30` | `Prefill` |
| `31` | `Started` |
| `32` | `Starting` |
| `33` | `Ignited` |
| `34`-`37` | `Error` |
| `40`-`47` | `Level 1` through `Level 8` |
| `48`-`4F` | `TSTAT L 1` through `TSTAT L 8` |
| `5x` | `Ramping` (low three bits still encode target level) |
| `6x` | `Ash dump` |
| other | `Undefined: %02X` |

For example, raw `C3` normalizes to `43` and displays `Level 4`. The exact
firmware state topology and transition sites are documented in
[operating-state-machine.md](../reverse-engineering/operating-state-machine.md).

## Non-periodic and table-only indexes

Firmware 2.06, 2.70, and 2.71 contain a separate event path that sends T20.
The 2.06 path begins at `086A`; the later pair begins at `07E2`. T20 is not a
member of the periodic telemetry walk. During the first live 2.06 session,
T20 alternated `02` and `00` in step with the operator-observed flashing second
panel light. Periodic T07 sampled the same alternating `02`/`00` display state,
while alarm T13 remained `02`. Both display paths continued after T09 changed
to Off and the fan command/target fell to zero, showing that the light-2 fault
was latched independently of active cooldown. BixCheck has a related C20
`LED no-log` computed record.

BixCheck 5.5.01's data table also names TFD `Low temp count`, TFE `Sample
maximum`, and TFF `Recent sample`. No literal periodic slot or recovered
firmware sender path produces those indexes in the preserved 2.71 application
image. They remain valid vendor table entries, but OpenMaxFire must not claim
that they are periodic 2.71 wire frames without a capture or a newly recovered
producer.

## Blocked-flue monitor

The vendor algorithm watches for a rapid thermocouple-point drop consistent
with reduced exhaust flow. A warning can clear if temperature recovers;
otherwise the factory controller shuts down. Fuel exhaustion or an overly lean
fire can produce similar indications.

OpenMaxFire should expose BF/LB measurements and factory alarms without
reimplementing or bypassing the controller's shutdown logic. The complete raw
BixCheck records are in each release's `data-elements.csv`.
