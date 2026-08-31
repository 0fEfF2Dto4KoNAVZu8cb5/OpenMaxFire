# MaxFire serial command and register cheat sheet

This is the short, operator-friendly reference for the reconstructed MaxFire
110/115 J3 protocol. It combines the controller reads, controller writes,
configuration bytes, telemetry fields, and loader controls in one place.

> **Current proof level:** the commands below come from three BixCheck releases,
> three preserved application-firmware generations, offline execution of the
> real PIC code, and a read-only live session on serial 5215's firmware
> 2.02/data-format 04 controller. That board's J3 ground/TX/RX and 5 V TTL cable
> are validated; J3-3 remains unresolved. Do not connect a generic USB serial
> adapter or generalize this pinout to another board revision.

## Safety legend

| Label | Meaning |
| --- | --- |
| **READ ONLY** | Does not intentionally change controller state. Use only after the J3 electrical interface has been proved. |
| **STATE WRITE** | Changes RAM, telemetry, LEDs, configuration, or operating state. Not for the first live session. |
| **ACTUATOR WRITE** | Can operate a motor, fan, compressor, feed system, or igniter. Bench/service use only. |
| **DO NOT SEND** | Can enter the bootloader or alter firmware/configuration. Keep out of ordinary tools. |

No command is electrically safe until J3 ground, level, polarity, and pinout
are measured. In particular, **READ ONLY describes the command's software
effect, not the cable**.

## 60-second protocol basics

| Item | Rule |
| --- | --- |
| Serial format | 8 data bits, no parity, 1 stop bit (`8N1`) |
| Live firmware 2.02 / format 04 | 9,600 baud |
| Firmware 2.06 | 9,600 baud |
| Firmware 2.70/2.71 | 19,200 baud intended; BixCheck also offered 9,600 |
| Host control lines | BixCheck enables DTR and RTS; no hardware/software flow control |
| Request text | Uppercase ASCII only |
| Read request | Four bytes: `<unit>R<address>` |
| Write request | Six bytes: `<unit>W<address><value>` |
| Request ending | **None**: do not append Enter, CR, LF, or NUL |
| Address/value format | Exactly two hexadecimal digits, `00` through `FF` |
| Stove response ending | LF (`0A`); clients may accept CR or LF |
| Response hex | Parse case-insensitively; real firmware can return lowercase `a`-`f` |
| Background traffic | `T...` telemetry can appear between a request and its response |

The smallest read-only exchange should be:

```text
Host sends exactly:  CR00
Stove should return: CR0000\n
```

Here `\n` means one LF byte returned by the stove. It is not part of the host
request.

## Command families

| Family | Example | Direction | Meaning | Safety |
| --- | --- | --- | --- | --- |
| `CRxx` | `CR02` | Host to stove | Read controller register `xx` | **READ ONLY** |
| `CWxxyy` | `CW0E14` | Host to stove | Write value `yy` to controller register `xx` | **STATE/ACTUATOR WRITE** |
| `ARxx` | `AR03` | Host to stove | Read one internal EEPROM/configuration byte | **READ ONLY** |
| `AWxxyy` | `AW6B40` | Host to stove | Generic A-space write grammar used by BixCheck | **DO NOT SEND** |
| `DRxx` / `DWxxyy` | `DW1234` | Both/host-generic | D-space is retained by BixCheck; firmware also emits `DWxxyy` diagnostic lines | **UNRESOLVED** |
| `Txxvv` | `T0913` | Stove to host | Unsolicited telemetry slot `xx`, value `vv` | Receive only |
| `M...` / `I...` | `I` | Stove to host | Status/control family; inner payload unresolved | Receive only |
| raw loader bytes | `EA`, `E3`, `ED` | Both | Separate binary firmware-loader protocol | **DO NOT SEND** |

The generic BixCheck request builder accepts A, C, and D unit letters. `CR`,
all `CW00`-`CW0F` handlers, and every `AR00`-`ARFF` read are corroborated by
offline firmware execution. No A-space write has been run in the emulator, and
D-request semantics remain unresolved. Treat `AW` and host-originated `D`
requests as unsupported even though they fit the generic frame grammar.

## Recommended first read-only sequence

Send one request, wait for its matching addressed response, and log every raw
byte and timestamp.

| Order | Request | Why |
| ---: | --- | --- |
| 1 | `CR00` | Lowest-risk known probe; expected value `00` |
| 2 | `CR08` | Data format: live 2.02=`04`, 2.06=`05`, 2.70/2.71=`07` |
| 3 | `CR0B` | Firmware major byte; expected `02` |
| 4 | `CR0C` | Firmware minor byte: live `02`, or preserved `06`, `70`, `71` |
| 5 | `CR0D` | Reserved constant; expected `00` |
| 6 | `CR0E` | Version-dependent read constant |
| 7 | `CR01`-`CR0A` | Inputs and live measurements, one at a time |
| 8 | `AR00`-`ARFF` | Full EEPROM backup, only after stable controller reads |

Version identification:

| CR0B | CR0C | Firmware | CR08 format | Intended baud |
| ---: | ---: | --- | ---: | ---: |
| `02` | `02` | 2.02 (live-observed) | `04` | 9,600 |
| `02` | `06` | 2.06 | `05` | 9,600 |
| `02` | `70` | 2.70 | `07` | 19,200 |
| `02` | `71` | 2.71 | `07` | 19,200 |

Do not send a `CW`, `AW`, or raw loader byte during this sequence.

## Controller read registers: CR00-CR0E

| Request | Returned value/field | Plain meaning | Notes |
| --- | --- | --- | --- |
| `CR00` | constant `00` | Presence/basic communication probe | Live 2.02 and preserved 2.06/2.70/2.71 |
| `CR01` | button byte | Physical front-panel button | Values in the button table below |
| `CR02` | bit field | Switches, doors, fuel, feeder sensor | Bits below; two inputs still unnamed |
| `CR03` | bit field | Internal/output status | Physical names remain partly unresolved |
| `CR04` | signed byte | Control-board ambient temperature in °C | Same source as T00; not fire temperature |
| `CR05` | raw byte | J10 exhaust-fan sensor pulse count | Raw counter, not proved RPM |
| `CR06` | bit field | Controller flags and thermostat | Thermostat is bit 2 |
| `CR07` | raw byte | J9 feeder-wheel cycle interval | Raw interval-like value; unit unproved |
| `CR08` | constant | Stove data format | Live 2.02=`04`; 2.06=`05`; 2.70/2.71=`07` |
| `CR09` | raw byte | Fan adjustment potentiometer | AN3; checkout thresholds below |
| `CR0A` | raw byte | Feed adjustment potentiometer | AN4; checkout thresholds below |
| `CR0B` | constant | Firmware major byte | `02` on all preserved versions |
| `CR0C` | constant | Firmware minor byte | Live `02`; preserved `06`, `70`, or `71` |
| `CR0D` | constant `00` | Reserved/unknown | Same in all preserved versions |
| `CR0E` | constant on read | Version-dependent/reserved readback | 2.06=`21`, 2.70=`02`, 2.71=`00`; writes are remote buttons |

### CR01 front-panel button values

| CR01 value | Meaning |
| ---: | --- |
| `00` | No button |
| `01` | OFF |
| `02` | ON |
| `04` | UP |
| `08` | DOWN |

These are physical-panel read values. The synthetic remote-button write values
at `CW0E` are different.

### CR02 input bits

| Bit/mask | Meaning | Known polarity |
| --- | --- | --- |
| 0 / `01` | Burn-drive motor limit switch | Unverified |
| 1 / `02` | External mux input | Physical function unresolved |
| 2 / `04` | Fuel selector | 1=Fuel A/corn; 0=Fuel B/wood |
| 3 / `08` | Internal/multiplexer state | Unresolved |
| 4 / `10` | J9 feeder-wheel sensor current state | Unverified |
| 5 / `20` | Firebox door | 1=open; 0=closed |
| 6 / `40` | Ash drawer | 1=open; 0=closed |
| 7 / `80` | RE1 digital input | Physical function unresolved |

To test a bit, use `value & mask`. Example: `(CR02 & 0x20) != 0` means the
firebox door reports open.

### CR03 status/output bits

| Bit/mask | Static source | Meaning status |
| --- | --- | --- |
| 0 / `01` | RB1 output | Physical role not yet named with confidence |
| 1 / `02` | RB5 output | Physical role not yet named with confidence |
| 2 / `04` | RAM `0x56`, bit 5 | Internal status |
| 3 / `08` | RAM `0x56`, bit 7 | Internal status |
| 4-7 / `F0` | Zero in recovered handler | Reserved in observed firmware |

### CR06 flag bits

| Bit/mask | Static source | Meaning status |
| --- | --- | --- |
| 0 / `01` | RAM `0x2D`, bit 0 | Internal flag; unnamed |
| 1 / `02` | RAM `0x2D`, bit 1 | Internal flag; unnamed |
| 2 / `04` | RB4 | Thermostat input; live 2.02 polarity is 1=open, 0=closed |
| 3-7 / `F8` | Zero in recovered handler | Reserved in observed firmware |

### Raw checkout ranges

| Register | Condition | Expected raw value |
| --- | --- | ---: |
| `CR09` / `CR0A` | Potentiometer low | `00`-`03` |
| `CR09` / `CR0A` | Center detent | `79`-`86` |
| `CR09` / `CR0A` | Potentiometer high | `FC`-`FF` |
| `CR05` | Exhaust full-power test | `78` or higher |
| `CR05` | Exhaust half-power test | `38`-`48` |
| `CR05` | Exhaust off, BixCheck 5.5.x | `00` |
| `CR05` | Exhaust off, BixCheck 5.0.21 | `00`-`03` |
| `CR07` | Feed motor/sensor checkout | `10`-`68` |

These are vendor checkout predicates on raw bytes. Do not label CR05 as RPM or
CR07 as seconds until live correlation establishes physical units.
The live format-04 fan control's physical center read `0x78`, one count below
the later BixCheck detent predicate; the feed control's center read `0x79`.

## Controller write registers: CW00-CW0F

Every command in this section changes state or enters an actuator/service path.
The examples document BixCheck; they are **not** a recommendation to transmit.
The table describes 2.06/2.70/2.71. Original 2.02 has only `CW00`-`CW0E` table
entries; `CW0F` falls into NOPs and does not implement `CW0FC4`.

| Register | Recovered role | Value behavior / known example | Risk |
| --- | --- | --- | --- |
| `CW00yy` | Reset service/telemetry countdown | `yy` is ignored | **STATE WRITE** |
| `CW01yy` | Recompute/persist configuration checksum | Programs EEPROM A00/A01; `yy` is ignored; one backed-up `CW0100` repair is live-validated on 2.06 | **EEPROM WRITE / EXPERT WORKFLOW** |
| `CW02yy` | Suppress periodic telemetry | Sets suppression flag/countdown; `yy` not used as countdown | **STATE WRITE** |
| `CW03yy` | Resume periodic telemetry | Clears suppression/parser state | **STATE WRITE** |
| `CW04yy` | Front-panel LEDs | `FF` on, `00` off | **STATE WRITE** |
| `CW05yy` | Burn-drive/plate motor | Checkout uses `00` | **ACTUATOR WRITE** |
| `CW06yy` | Air compressor on | Checkout uses `00` | **ACTUATOR WRITE** |
| `CW07yy` | Air compressor off | Checkout uses `00` | **ACTUATOR WRITE** |
| `CW08yy` | Convection fan target | Values below | **ACTUATOR WRITE** |
| `CW09yy` | Exhaust fan phase/power | `80` full, `40` half, `00` off | **ACTUATOR WRITE** |
| `CW0Ayy` | Igniter follow-up routine | Checkout uses `00` | **ACTUATOR WRITE** |
| `CW0Byy` | Feed motor/sensor test | Checkout uses `20` | **ACTUATOR WRITE** |
| `CW0Cyy` | Controller service/mode routine | Exact purpose unresolved | **DO NOT SEND** |
| `CW0Dyy` | Igniter workflow | Uses countdown and returns `I\n`; Checkout uses `00` | **ACTUATOR WRITE** |
| `CW0Eyy` | Synthetic front-panel button | OFF/ON/UP/DOWN values below | **STATE/OPERATING WRITE** |
| `CW0Fyy` | Reset/loader request | Only `yy=C4` takes loader branch | **DO NOT SEND** |

### Known CW values

| Function | Exact request |
| --- | --- |
| LEDs on / off | `CW04FF` / `CW0400` |
| Convection off | `CW0800` |
| Convection levels 1-4, data format 05 | `CW0801`, `CW0802`, `CW0803`, `CW0804` |
| Convection levels 1-4, data format 07 | `CW0819`, `CW0832`, `CW084B`, `CW0864` |
| Exhaust full / half / off | `CW0980` / `CW0940` / `CW0900` |
| Feed motor/sensor test | `CW0B20` |
| Remote OFF | `CW0E11` |
| Remote ON | `CW0E12` |
| Remote UP | `CW0E14` |
| Remote DOWN | `CW0E18` |
| Enter firmware servicing on 2.06+ | `CW0FC4` — **DO NOT SEND** |

Most C writes are silent. `CW0D` is the only write in the safe synthetic
emulator sweep that returned serial data (`I\n`). Silence is not proof that a
write failed.

## A-space EEPROM/configuration map

Read one byte with `ARxx`; for example, `AR03` reads the first serial-number
byte. Read and save all `AR00` through `ARFF` before considering any future
configuration work. Strings occupy consecutive bytes.

| Address/range | Length | Meaning |
| --- | ---: | --- |
| `A00-A01` | 2 | Stored configuration checksum, big-endian |
| `A02` | 1 | EEPROM/data format expected by the stove |
| `A03-A0A` | 8 | Serial number string |
| `A0B-A12` | 8 | Production date string |
| `A13-A22` | 16 | Model name string |
| `A23-A3F` | 29 | Spare/reserved/not catalogued |
| `A40-A47` | 8 | Fuel A fan adjustments, heat levels 1-8 |
| `A48-A4F` | 8 | Fuel A feed adjustments, heat levels 1-8 |
| `A50-A57` | 8 | Fuel A ash-counter increments, levels 1-8 |
| `A58` | 1 | Fuel A startup fan |
| `A59` | 1 | Fuel A startup feed |
| `A5A` | 1 | Fuel A startup time percentage |
| `A5B` | 1 | Fuel A igniter time percentage |
| `A5C-A5F` | 4 | Reserved/gap |
| `A60` | 1 | Fuel A ash-dump fan |
| `A61` | 1 | Fuel A ash-dump feed |
| `A62` | 1 | Fuel A ash-dump time percentage |
| `A63` | 1 | Fuel A ash-dump heat level, 0-8 |
| `A64` | 1 | Fuel A ash-dump target percentage |
| `A65-A67` | 3 | Reserved |
| `A68` | 1 | Fuel A thermocouple point for 25% convection fan |
| `A69` | 1 | Fuel A thermocouple point for 100% convection fan |
| `A6A` | 1 | Fuel A thermostat heat level, 0-8; format 07 era |
| `A6B` | 1 | Fuel A lean-burn threshold, displayed 0-100% |
| `A6C` | 1 | Fuel A lean-burn fan adjustment, displayed -30..30 |
| `A6D` | 1 | Fuel A lean-burn feed adjustment, displayed -30..30 |
| `A6E` | 1 | Fuel A shared flags: bit 1 ratio/ash trim mode; bit 2 disable auto-restart |
| `A6F` | 1 | Reserved |
| `A70-A77` | 8 | Fuel B fan adjustments, heat levels 1-8 |
| `A78-A7F` | 8 | Fuel B feed adjustments, heat levels 1-8 |
| `A80-A87` | 8 | Fuel B ash-counter increments, levels 1-8 |
| `A88` | 1 | Fuel B startup fan |
| `A89` | 1 | Fuel B startup feed |
| `A8A` | 1 | Fuel B startup time percentage |
| `A8B` | 1 | Fuel B igniter time percentage |
| `A8C-A8F` | 4 | Reserved/gap |
| `A90` | 1 | Fuel B ash-dump fan |
| `A91` | 1 | Fuel B ash-dump feed |
| `A92` | 1 | Fuel B ash-dump time percentage |
| `A93` | 1 | Fuel B ash-dump heat level, 0-8 |
| `A94` | 1 | Fuel B ash-dump target percentage |
| `A95-A97` | 3 | Reserved |
| `A98` | 1 | Fuel B thermocouple point for 25% convection fan |
| `A99` | 1 | Fuel B thermocouple point for 100% convection fan |
| `A9A` | 1 | Fuel B thermostat heat level, 0-8; format 07 era |
| `A9B` | 1 | Fuel B lean-burn threshold, displayed 0-100% |
| `A9C` | 1 | Fuel B lean-burn fan adjustment, displayed -30..30 |
| `A9D` | 1 | Fuel B lean-burn feed adjustment, displayed -30..30 |
| `A9E` | 1 | Fuel B shared flags: bit 1 ratio/ash trim mode; bit 2 disable auto-restart |
| `A9F-AFF` | 97 | Reserved/unknown in format 07, but included in its checksum |

Format 05 (firmware 2.06) checksums A02-A9A. Format 07 (firmware 2.70/2.71)
checksums A02-AFF. The checksum adds each logical byte to a 16-bit accumulator,
then rotates the accumulator left one bit after each byte.

Lean-burn A6B-A6D/A9B-A9D bytes use vendor display conversions and are not
simple percentages on the wire. A6E/A9E contain multiple settings in one byte.
This is why `AW` must remain disabled until there is a verified full backup,
field-level diff, shared-bit merge, checksum update, readback, and a recovery
path.

## Unsolicited telemetry: T00-T1E

The stove emits one byte per line:

```text
T<index><value>\n
```

Example: a big-endian 16-bit value `0x1234` at T0A/T0B arrives as two physical
lines, `T0a12\n` then `T0b34\n`. It does **not** arrive as `T0A1234` from the
preserved firmware.

The field table below is the later format-05/07 BixCheck layout. Firmware
2.02/format 04 ends at T15 and is positionally different: its exact operating
state source is T0C, not T09. See the
[format-04 live report](../reverse-engineering/live-fw202-format04.md).

| Slot(s) | Meaning | Conversion/notes |
| --- | --- | --- |
| `T00` | Control-board ambient temperature | Signed °C; °F = trunc(`C * 9 / 5`) + 32 |
| `T01` | Thermocouple | Uncalibrated `TC Points`, not °C/°F |
| `T02` | Fan potentiometer | Trim % = `raw * 60 / 255 - 30` for formats 05/07 |
| `T03` | Feed potentiometer | Same trim conversion as T02 |
| `T04` | Exhaust fan speed | Raw; BixCheck display RPM = `raw * 24`, not live calibrated |
| `T05` | Exhaust fan phase | Raw; BixCheck display µs = `8.0 - raw * 0.0264` |
| `T06` | Convection fan level | Raw percent |
| `T07` | Display LEDs | Raw/decoded display byte |
| `T08` | Igniter state | Low-three-bit decoder below |
| `T09` | Operating state | Family/substate decoder below |
| `T0A-T0B` | Ash level | Unsigned big-endian 16-bit |
| `T0C-T0D` | Ash target | Unsigned big-endian 16-bit |
| `T0E-T0F` | Feed on time | Big-endian ticks; seconds = value / 120 |
| `T10-T11` | Feed off time | Big-endian ticks; seconds = value / 120 |
| `T12` | IIC status | Raw byte; named bit decode not recovered |
| `T13` | Alarm status | Raw byte; named bit decode not recovered |
| `T14` | Flag status | Raw; displayed mode = `(raw & 7) + 1` |
| `T15` | Igniter current | Raw byte/state display |
| `T16` | Fire-door timer | Raw ticks; vendor says 1/3-second units |
| `T17` | Ash-drawer timer | Raw ticks; vendor says 5 1/3-second units |
| `T18` | Exhaust fan target | Raw; BixCheck display RPM = `raw * 24` |
| `T19` | Drop/BF drop limit | Raw thermocouple-point threshold |
| `T1A-T1B` | Feed cycle table | Big-endian ticks; seconds = value / 120 |
| `T1C-T1D` | Feed cycle calibration | Big-endian ticks; seconds = value / 120 |
| `T1E` | Lean-burn drop limit | 2.71 only; raw thermocouple-point threshold |

Additional non-periodic/table-only slots:

| Slot | Meaning/status |
| --- | --- |
| `T20` | 2.06/2.70/2.71 event-only display path related to BixCheck `LED no-log`; live 2.06 `02`/`00` alternation matched flashing light 2 |
| `TFD` | Vendor table name `Low temp count`; no recovered periodic producer |
| `TFE` | Vendor table name `Sample maximum`; no recovered periodic producer |
| `TFF` | Vendor table name `Recent sample`; no recovered periodic producer |

### T08 igniter state

Decode `T08 & 0x07`:

| Value | BixCheck display |
| ---: | --- |
| `0` | Left and right failed |
| `1` | Right failed |
| `2` | Left failed |
| `3`-`6` | Error |
| `7` | Left and right good |

### Operating state family (later T09; firmware 2.02 T0C)

First ignore bit 7. Use `state = T09 & 0x7F` on later formats and
`state = T0C & 0x7F` on firmware 2.02/format 04.

| Pattern | Meaning |
| --- | --- |
| `1x` | Cooldown |
| `2x` | Off |
| `30` | Prefill |
| `31` | Started |
| `32` | Starting |
| `33` | Ignited |
| `34`-`37` | Error |
| `40`-`47` | Heat Level 1-8 |
| `48`-`4F` | Thermostat Level 1-8 |
| `5x` | Ramping; low three bits encode target level |
| `6x` | Ash dump |
| other | Undefined |

For two-slot words, combine `high` and `low` as `(high << 8) | low`.

## Responses and parsing

| Response | Meaning |
| --- | --- |
| `CR0200\n` | Controller read response: C address 02 has value 00 |
| `AR034D\n` | A-space read response: A address 03 has value 4D |
| `T0913\n` | Telemetry slot 09 has value 13 (Cooldown family) |
| `DW1234\n` | Auxiliary D-space line: address 12, value 34; exact semantics unresolved |
| `I\n` | Status response emitted by the `CW0D` workflow |

Addressed A/C/D responses are six characters before the line ending:
`<unit><operation><address><value>`. BixCheck does not rely heavily on the
operation character in responses; a replacement client should still require a
valid six-character frame and match unit/address to the outstanding request.

While waiting for a response:

1. split incoming data on CR or LF;
2. accept lowercase response hex;
3. record and dispatch any `T` telemetry separately;
4. continue waiting for the addressed A/C/D response;
5. stop after a bounded timeout/line count instead of waiting forever.

## Binary bootloader controls — do not send

This protocol is separate from ASCII register traffic and can erase/program the
controller. It is included only so captures can be recognized.

| Direction | Byte/frame | Reconstructed role |
| --- | --- | --- |
| Host to stove | `CW0FC4` | On 2.06+, leave the application and request firmware servicing; absent from original 2.02 |
| Host to stove | raw `EA` | Loader identity probe |
| Stove to host | raw `EB` | Loader identified |
| Host to stove | raw `E3` | Begin program block |
| Host to stove | address high, address low | PIC word address |
| Host to stove | byte count | Payload size; up to 32 data bytes in BixCheck |
| Host to stove | checksum | Sum of block data bytes modulo 256 |
| Host to stove | raw data bytes | High/low PIC program-word bytes (opposite Intel HEX storage order) |
| Stove to host | raw `E7`, then `E4` | Two-stage block acknowledgement |
| Host to stove | raw `ED` | Download complete |
| Stove to host | raw `E4` | Completion acknowledgement |

Never place these bytes in a monitor, Home Assistant integration, normal CLI,
or automatic retry loop.

## New-board live-session checklist

- Stove cold, off, and not responsible for heating.
- Identify J3 ground, pin order, idle level, polarity, and whether isolation is
  required using protected high-impedance measurements.
- Confirm the oscillator marking/frequency and use a level-correct,
  current-limited, isolated interface.
- Start with adapter transmit disabled and capture idle traffic.
- Enable transmit only after the receive side and voltage levels are proved.
- Send exactly `CR00`, with no line ending, and save raw bytes/timing.
- Continue only if the reply is the expected addressed frame.
- Read identity/version registers next; then observe cold/off inputs one at a
  time.
- Send no `CW`, `AW`, or loader byte in the first session.

Serial 5215 completed this checklist read-only on 2026-08-22. Its exact pinout,
cable wiring, captures, EEPROM, and format-04 field correlations are in the
[live firmware-2.02 report](../reverse-engineering/live-fw202-format04.md).

For derivation details and machine-readable evidence, see the
[J3 working specification](j3-protocol.md),
[controller read map](register-map.md),
[controller write map](controller-writes.md),
[telemetry map](telemetry-fields.md),
[configuration map](../bixcheck/configuration.md), and
[downloader reconstruction](../reverse-engineering/bixcheck-downloader-protocol.md).
