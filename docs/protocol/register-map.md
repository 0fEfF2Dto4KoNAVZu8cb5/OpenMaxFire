# Firmware CR register map

The detailed map below combines bank-aware handler traces from all three real
firmware images with BixCheck's Checkout masks. It is emulator-confirmed, not
live-stove-confirmed. The same CR00-CR0E structure exists in 2.06, 2.70, and
2.71.

## Cross-version constants

| Read | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: |
| `CR00` | `0x00` | `0x00` | `0x00` |
| `CR08` | `0x05` | `0x07` | `0x07` |
| `CR0B` | `0x02` | `0x02` | `0x02` |
| `CR0C` | `0x06` | `0x70` | `0x71` |
| `CR0D` | `0x00` | `0x00` | `0x00` |
| `CR0E` | `0x21` | `0x02` | `0x00` |

CR0B/CR0C are identified as the two-byte stove software version. Every
BixCheck Individualization table labels C08 `Stove data format`, so CR08's name
is now statically confirmed rather than inferred. CR0E read behavior changes
even though BixCheck uses writes to 0x0E for remote-button actions. See the
[full firmware comparison](../reverse-engineering/firmware-comparison.md).

## 2.71 detailed handlers

| Request | Traced return/source | Interpretation |
| --- | --- | --- |
| `CR00` | Constant `0x00` | Emulator-confirmed first read-only probe |
| `CR01` | Bank-1 RAM byte 0x53 | Front-panel button code from RD3/RD2/RD6:RD5 mux scanner |
| `CR02` | Packed input byte | See bit table below |
| `CR03` | Packed status/output byte | See bit table below |
| `CR04` | Bank-1 RAM byte 0x0A2 | Thermometer value used by Checkout; conversion unresolved |
| `CR05` | RAM byte 0x34 | Unknown |
| `CR06` | Packed flags | See bit table below |
| `CR07` | Derived/scaled from RAM 0x44/0x45 | Unknown engineering value |
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
| 4 | RD0 | Direct digital input |
| 5 | RD1 | Firebox door: open=1, closed=0 |
| 6 | RD4 | Ash drawer: open=1, closed=0 |
| 7 | RE1 | Direct digital input |

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

## Buttons and potentiometers

`AnalyzeInteractiveResult()` supplies exact service-test encodings:

- CR01 front-panel buttons: none `0x00`, ON `0x02`, OFF `0x01`, UP `0x04`,
  DOWN `0x08`. RD2 selects the active-low button bank, RD6:RD5 select
  OFF/ON/UP/DOWN, RD3 supplies the shared return, and the debounced result is
  stored in RAM 0x53.
- CR09 fan potentiometer: low `<=0x03`, detent `0x79-0x86`, high `>0xFB`.
- CR0A feed potentiometer: the same low/detent/high thresholds.

Reset-time synthetic ADC sweeps identify AN3→CR09 and AN4→CR0A in all three
firmware generations. The reported byte is the high eight bits of the modeled
10-bit sample.

## Physical-validation boundary

The offline cross-reference now assigns the front-panel multiplexer,
burn-drive limit switch, fuel selector, door, drawer, thermostat, and trim-pot
paths. `CR02.1` remains unnamed. Static code establishes the fuel polarity by
following the `0x30` configuration-bank offset: clear selects Fuel B (`A70...`)
and set leaves Fuel A (`A40...`).

This still cannot prove the PCB wiring or electrical polarity on serial 5215.
The preserved diagram shows board `9067-0404`, while the installed board is
owner-reported as `9067-0604`. Safe validation remains a cold/off CR01/CR02/CR06
baseline with one physical input changed at a time.

Machine-readable traces and stimulus results are documented in the
[exhaustive emulator pass](../reverse-engineering/emulator-deep-pass.md).
