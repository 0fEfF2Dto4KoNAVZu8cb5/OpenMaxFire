# Firmware CR register map

The detailed map below combines bank-aware handler traces from all four
preserved application generations with BixCheck's Checkout masks. Common
physical inputs were subsequently live-validated read-only on the firmware
2.02/data-format 04 controller. Firmware 2.02 has real handlers for CR00-CR0C;
CR0D/CR0E use its generic zero-response path. Later versions have CR00-CR0E
handlers.

## Cross-version constants

| Read | Live 2.02 | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: | ---: |
| `CR00` | `0x00` | `0x00` | `0x00` | `0x00` |
| `CR08` | `0x04` | `0x05` | `0x07` | `0x07` |
| `CR0B` | `0x02` | `0x02` | `0x02` | `0x02` |
| `CR0C` | `0x02` | `0x06` | `0x70` | `0x71` |
| `CR0D` | `0x00` | `0x00` | `0x00` | `0x00` |
| `CR0E` | `0x00` | `0x21` | `0x02` | `0x00` |

CR0B/CR0C are identified as the two-byte stove software version. Every
BixCheck Individualization table labels C08 `Stove data format`, so CR08's name
is now statically confirmed rather than inferred. CR0E read behavior changes
even though BixCheck uses writes to 0x0E for remote-button actions. See the
[full firmware comparison](../reverse-engineering/firmware-comparison.md).

The 2.02 column is both exact recovered-code behavior and live observation.
The complete live capture is in
[the format-04 live report](../reverse-engineering/live-fw202-format04.md).

## 2.71 detailed handlers

| Request | Traced return/source | Interpretation |
| --- | --- | --- |
| `CR00` | Constant `0x00` | Emulator-confirmed first read-only probe |
| `CR01` | Bank-1 RAM byte 0x53 | Front-panel button code from RD3/RD2/RD6:RD5 mux scanner |
| `CR02` | Packed input byte | See bit table below |
| `CR03` | Packed status/output byte | See bit table below |
| `CR04` | Bank-1 RAM byte 0x0A2 | Control-board ambient temperature; the same T00 source is displayed as signed °C |
| `CR05` | RAM byte 0x34, latched from TMR0 | J10 exhaust-fan sensor pulse count |
| `CR06` | Packed flags | See bit table below |
| `CR07` | Low byte of `(RAM 0x45:0x44) >> 4` | J9 feeder-wheel sensor cycle interval |
| `CR08` | Constant `0x07` | Stove data format 07 |
| `CR09` | RAM byte 0x2E | Fan potentiometer, sampled from AN3 |
| `CR0A` | RAM byte 0x2F | Feed potentiometer, sampled from AN4 |
| `CR0B` | Constant `0x02` | Firmware major byte |
| `CR0C` | Constant `0x71` | Firmware minor byte; together 2.71 |
| `CR0D` | Constant `0x00` | Unknown/reserved |
| `CR0E` | Constant `0x00` on read | Writes to 0x0E carry remote buttons in BixCheck |

## CR02

| Bit | Firmware source | Cross-referenced meaning |
| ---: | --- | --- |
| 0 | RD3 external-input mux slot 0 | Burn-drive motor limit switch; polarity unverified |
| 1 | RD3 external-input mux slot 1 | Physical function unresolved |
| 2 | RD3 external-input mux slot 2 | Fuel selector: 1=Fuel A/corn, 0=Fuel B/wood |
| 3 | Internal/multiplexer state | Unknown |
| 4 | RD0 | J9 feeder-wheel sensor current state; polarity unverified |
| 5 | RD1 | Firebox door: open=1, closed=0 |
| 6 | RD4 | Ash drawer: open=1, closed=0 |
| 7 | RE1 | Direct digital input |

On serial 5215, the cold/off baseline was `0x12`. One-at-a-time physical tests
returned `0x32` with the firebox door open, `0x52` with the ash drawer open,
and `0x16` in corn/Fuel-A position, then returned to `0x12`. This live-validates
bits 5, 6, and 2 and their documented polarity on the 9067-0604 controller.

## CR03

| Bit | Static source |
| ---: | --- |
| 0 | RB1 output state |
| 1 | RB5 output state |
| 2 | RAM 0x56 bit 5 |
| 3 | RAM 0x56 bit 7 |
| 4-7 | Zero in the observed handler |

## CR06

| Bit | Static source |
| ---: | --- |
| 0 | RAM 0x2D bit 0 |
| 1 | RAM 0x2D bit 1 |
| 2 | RB4 thermostat input |
| 3-7 | Zero in the observed handler |

The live thermostat baseline was `CR06=0x03` with its jumper installed/contacts
closed and `0x07` with the jumper removed/contacts open. Bit 2 is therefore
live-validated as 1=open on this controller.

## Buttons and potentiometers

`AnalyzeInteractiveResult()` supplies exact service-test encodings:

- CR01 front-panel buttons: none `0x00`, ON `0x02`, OFF `0x01`, UP `0x04`,
  DOWN `0x08`. RD2 selects the active-low button bank, RD6:RD5 select
  OFF/ON/UP/DOWN, RD3 supplies the shared return, and the debounced result is
  stored in RAM `0x52` on 2.02 and bank-1 RAM `0x53` in later firmware.
- CR09 fan potentiometer: low `<=0x03`, detent `0x79-0x86`, high `>0xFB`.
- CR0A feed potentiometer: the same low/detent/high thresholds.

Reset-time synthetic ADC sweeps identify AN3→CR09 and AN4→CR0A in all four
firmware versions. The reported byte is the high eight bits of the modeled
10-bit sample.

Live cold/off testing returned OFF=`0x01`, UP=`0x04`, DOWN=`0x08`, and none=
`0x00`; ON was intentionally not pressed. Both potentiometers covered
`0x00`-`0xFF`; physical center was fan `0x78` and feed `0x79`. The session ended
with fan `0x78` and the owner's original feed setting `0x49`.

## J9 and J10 sensor counters

The preserved board diagram supplies the connector names; firmware and
BixCheck independently establish the data paths. Equivalent paths occur in
2.02, 2.06, 2.70, and 2.71.

### CR05 / J10 exhaust-fan sensor

Firmware writes `0xBF` to `OPTION_REG`. On a PIC16F877A this selects the
external RA4/T0CKI source, high-to-low transitions, and no TMR0 prescaler.
Every 30 RB0 external-interrupt ticks, the ISR copies TMR0 to RAM `0x34`, uses
`0xFF` if the counter overflowed, and clears TMR0. `CR05` returns that byte
without another conversion.

BixCheck applies these service-test predicates:

| Test | Accepted CR05 value |
| --- | ---: |
| Exhaust full power | `>= 0x78` (120) |
| Exhaust half power | `0x38`-`0x48` (56-72) |
| Exhaust off, BixCheck 5.5.x | `0x00` |
| Exhaust off, BixCheck 5.0.21 | `0x00`-`0x03` |

These are raw count thresholds, not RPM. The RB0 interrupt also restarts the
phase-control timing path, which is strongly consistent with an AC
zero-crossing timebase, but that physical interpretation and the exact sample
duration have not been measured on serial 5215.

### CR02.4 and CR07 / J9 feeder-wheel sensor

RD0 is both exposed directly as `CR02.4` and used as the wheel-sensor input.
While the RB1 feed-motor output is active, each RB0 external interrupt
increments the 16-bit RAM counter `0x47:0x46`. The control loop remembers an
RD0-high state, recognizes the following RD0-low transition, and then latches
the elapsed count into `0x45:0x44`. Firmware 2.02 shifts the value right once
during that latch; later versions copy it directly. Every version then shifts
the latched value right four more places in `CR07` and returns the low byte.
Thus 2.02's effective raw scale contains one extra factor of two and `CR07`
values should not be compared across firmware versions as identical units.

All three BixCheck executables accept `CR07` values `0x10`-`0x68` (16-104)
during the automatic feed-motor/sensor test. The value is therefore an
interval-like wheel-sensor measurement; its engineering unit, polarity, and
out-of-range/fault behavior remain unresolved.

Exact per-generation PCs and every stage are regenerated into
`reverse-engineering/firmware/comparison/sensor-signal-paths.csv`.

## Physical-validation boundary

The offline cross-reference now assigns the front-panel multiplexer,
burn-drive limit switch, fuel selector, feeder-wheel sensor, exhaust-fan
sensor, door, drawer, thermostat, and trim-pot paths. `CR02.1` and `CR02.7`
remain unnamed. Static code establishes the fuel polarity by
following the `0x30` configuration-bank offset: clear selects Fuel B (`A70...`)
and set leaves Fuel A (`A40...`).

The cold/off CR01/CR02/CR06 and potentiometer mappings above are now physically
validated on serial 5215's directly photographed `9067-0604` board. CR02.1 and
CR02.7 remain unnamed. A bounded no-fuel start with the igniters disconnected
live-correlated the operator-observed blower with CR05 `00`→`0C` and its
post-OFF return to `00`. Across that interval CR02.4 changed 0→1 and CR07
changed `1E`→`1F`; both post-run values then remained stable through 20
read-only Off cycles. The other bank-0 writers would produce CR07 `2D` at boot
or `16` at the range clamp, so the observed `1F` proves that the RB1-gated
runtime latch executed after an RD0 high-to-low sequence. This does not
establish electrical polarity, physical movement per edge, or engineering
units.

Machine-readable traces and stimulus results are documented in the
[exhaustive emulator pass](../reverse-engineering/emulator-deep-pass.md).
