# Controller write register map

Status: complete static dispatcher map for application firmware 2.06, 2.70,
and 2.71; offline emulator coverage only. Nothing in this document is a live
authorization to drive a stove.

The controller accepts the six-byte, unterminated form `CWxxyy`. All three
application generations have exactly sixteen computed-dispatch entries,
`CW00` through `CW0F`. The dispatcher destinations are asserted by the
firmware pipeline and every handler is reached by the disposable-clone
emulator.

| Write | Recovered role | How the value is used | 2.06 PC | 2.70 PC | 2.71 PC |
| --- | --- | --- | ---: | ---: | ---: |
| `CW00` | Service/telemetry countdown reset | Handler clears the bank-1 countdown; the supplied byte is not the new countdown | `1030` | `113A` | `1110` |
| `CW01` | Persist configuration checksum | Recomputes the configuration checksum and programs PIC data EEPROM A00/A01; request value is not the checksum | `1036` | `1140` | `1116` |
| `CW02` | Suppress periodic telemetry | Sets RAM `0x51.3` and loads countdown `0x78` | `107B` | `1185` | `115B` |
| `CW03` | Resume periodic telemetry | Clears RAM `0x51.3` and parser scratch | `1080` | `118A` | `1160` |
| `CW04` | Front-panel LEDs | Passes the byte to the LED output routine; Checkout uses `FF` and `00` | `1085` | `118F` | `1165` |
| `CW05` | Burn-drive/plate motor | Enters the motor routine; Checkout uses `00` | `108E` | `1198` | `116E` |
| `CW06` | Air compressor on | Calls the compressor-on routine; Checkout uses `00` | `1095` | `119B` | `1171` |
| `CW07` | Air compressor off | Calls the compressor-off routine; Checkout uses `00` | `109A` | `11A0` | `1176` |
| `CW08` | Convection fan target | Copies the byte into the fan target path | `10A1` | `11A7` | `117D` |
| `CW09` | Exhaust fan phase/power | Scales the byte through the phase-control routine | `10A7` | `11AD` | `1183` |
| `CW0A` | Igniter follow-up | Enters the second igniter follow-up routine; Checkout uses `00` | `10C5` | `11CB` | `11A1` |
| `CW0B` | Feed motor/sensor test | Swaps the byte and retains its high nibble as the drive parameter; Checkout uses `20` | `10D1` | `11D3` | `11A9` |
| `CW0C` | Controller service | Calls a service routine and rewrites RAM `0x43` mode bits; exact purpose remains unresolved | `10DF` | `11E1` | `11B7` |
| `CW0D` | Igniter workflow | Enters the workflow, loads countdown `0x82`, and emits `I` plus LF | `10ED` | `11ED` | `11C3` |
| `CW0E` | Remote front-panel button | Stores the byte as a synthetic panel-button code | `1104` | `11FE` | `11D8` |
| `CW0F` | Reset/loader request | Only value `C4` enters the reset/bootloader path; other values return normally | `110B` | `1205` | `11DF` |

## Known service values

The retained BixCheck tables and action paths establish these values:

| Function | Request/value |
| --- | --- |
| Remote OFF / ON / UP / DOWN | `CW0E11` / `CW0E12` / `CW0E14` / `CW0E18` |
| Convection levels 1-4, data format 5 | `CW0801` through `CW0804` |
| Convection levels 1-4, data format 7 | `CW0819`, `CW0832`, `CW084B`, `CW0864` |
| Convection off | `CW0800` |
| Exhaust full / half / off | `CW0980`, `CW0940`, `CW0900` |
| LEDs on / off | `CW04FF`, `CW0400` |
| Feed test | `CW0B20` |
| Reset into firmware servicing | `CW0FC4` |

`CW0FC4` is intentionally absent from the emulator sweep. The sweep sends only
`CW0F00`, which reaches the handler and returns without taking the keyed reset
branch.

## Offline execution result

All 48 version/register combinations reach their statically identified handler.
Forty-two reach the shared silent-write exit. The remaining six are `CW05` and
`CW0A` in each generation: both enter long actuator/timer paths and exceed the
50,000-instruction bound of the incomplete peripheral model. That is a model
limitation, not evidence of a firmware hang.

`CW01` produces exactly two modeled PIC EEPROM program events per generation,
at A00 and A01. Because the synthetic fixture already has a valid checksum,
the programmed bytes equal the existing bytes. `CW0D` is the only swept write
that returns serial data (`I\n`); the others are silent.

Machine-readable evidence is in:

- `reverse-engineering/firmware/comparison/cw00-cw0f-handlers.csv`
- `reverse-engineering/firmware/emulation/deep/cw-write-matrix.csv`
- `reverse-engineering/firmware/emulation/deep/cw-handler-access-summary.csv`
- `reverse-engineering/firmware/emulation/deep/cw-handler-change-summary.csv`
- `reverse-engineering/firmware/emulation/deep/cw-handler-net-changes.csv`
- `reverse-engineering/firmware/emulation/deep/cw-eeprom-events.csv`

The experiments alter only cloned RAM and synthetic EEPROM. They do not write
a preserved HEX file or communicate with physical hardware.
