# Live validation: firmware 2.02 / data format 04

Date: 2026-08-22 UTC

Status: live-validated on the cold, non-firing controller from appliance serial
5215. Only read requests were sent. No `CW`, `AW`, Downloader, bootloader,
remote-ON, or actuator command was used.

> **Later evidence:** A separately preserved 2026-08-23 session subsequently
> live-validated the normal OFF/ON/UP/DOWN command bytes and captured flashing
> fault light 8. The original read-only scope above describes the 2026-08-22
> corpus only. See [the addendum below](#2026-08-23-control-and-fault-addendum).

The byte-identical JSONL traffic logs, EEPROM artifact, adapter inventory, and
checksums are preserved under
[`research/live/2026-08-22-fw202-format04/`](../../research/live/2026-08-22-fw202-format04/).

## Major result

Serial 5215 contains an older, previously unpreserved controller application:

| Property | Live result |
| --- | --- |
| Firmware | `2.02` (`CR0B=02`, `CR0C=02`) |
| Data format | `04` (`CR08=04`) |
| UART | 9,600 baud, 8N1 |
| Request terminator | None |
| Response terminator | LF (`0A`) |
| Response hex case | Lowercase `a`-`f` is emitted |
| Static OpenMaxFire pairing | Not recognized before this capture |

The preserved factory releases begin at firmware 2.06/data format 05. Firmware
2.02 and format 04 must therefore be treated as a separate live-observed
generation. Later format-05/07 telemetry labels cannot be copied onto its
`T00`-`T15` slots without correlation.

## Board and J3 electrical path

The new bare-board photographs directly show:

- complete main-PCB marking `9067-0604`;
- `PIC16F877A-I/P` controller;
- oscillator marking `10.000 MHz`;
- component and solder sides of J3 and the PIC routing area; and
- the live FTDI wiring at the J3 solder pads.

Unpowered continuity tracing and the successful live exchange establish this
J3 mapping. Numbering follows the square pin-1 pad:

| J3 pin | Physical position in the documented upright board view | Function | Evidence |
| ---: | --- | --- | --- |
| 1 | Bottom, square pad | Stove RX, toward PIC pin 26 `RC7/RX/DT` | Corrected owner continuity/wiring identification plus successful transmit path |
| 2 | Third from top | Stove TX, toward PIC pin 25 `RC6/TX/CK` | Corrected owner continuity/wiring identification plus successful receive path |
| 3 | Second from top | Unresolved; left disconnected | No voltage/function conclusion; measured 0 V in an earlier standalone-board check |
| 4 | Top | Board ground | Direct continuity to board power-input ground |

The working cable is an FTDI `TTL-232R-5V-WE`, USB `0403:6001`, serial
`ABBAUPPN`. Its live wiring was:

| FTDI conductor | FTDI function | J3 connection |
| --- | --- | --- |
| Black | Ground | J3-4 |
| Orange | Adapter TX | J3-1 / stove RX |
| Yellow | Adapter RX | J3-2 / stove TX |
| Red, brown, green | Power/flow control | Disconnected |

The preserved solder-side FTDI photograph shows orange on J3-2 and yellow on
J3-1. That photographed placement was incorrect and does not represent the
successful live connection; the image is retained only as clearly labeled
historical evidence.

No adapter VCC conductor was connected. A generic bipolar RS-232 adapter or a
USB data cable is not equivalent. The continuity path to the PIC USART, lack of
an observed RS-232 transceiver in that path, and successful 5 V TTL adapter use
establish non-inverted TTL-level UART compatibility for this board.

## First communication and framing

At 19,200 baud, a ten-second receive-only capture and a `CR00` request produced
no valid response. At 9,600 baud, the same exact four-byte request succeeded:

```text
TX: 43 52 30 30             CR00
RX: 43 52 30 30 30 30 0A    CR0000\n
```

`identify` then returned:

```text
Firmware: 2.02
Data format: 04
CR00=00
CR08=04
CR0B=02
CR0C=02
CR0D=00
CR0E=00
Static pairing recognized: no
```

Receive-only captures returned zero bytes even while a local door/drawer LED
was flashing. Telemetry appeared only while read requests kept the serial path
active. Two port-opening experiments captured only `00 0A`; the same two bytes
also appeared without a power cycle, so they are not classified as a unique
power-up signature.

Telemetry is emitted in fast bursts separated by a repeating cycle of about
3.58 seconds. Addressed replies can be separated from their requests by more
than 16 complete interleaved `T`/`DW` frames. Opening a port in the middle of a
burst can also expose a partial first line such as `0f\n`.

## Cold CR register baseline

The first sequential cold/off read produced:

| Register | Value | Live interpretation |
| --- | ---: | --- |
| `CR00` | `00` | Read-only probe |
| `CR01` | `00` | No panel button pressed |
| `CR02` | `12` | Wood, both doors closed; other baseline bits remain unresolved |
| `CR03` | `08` | Unresolved packed status/output |
| `CR04` | `11` | 17 decimal; consistent with board ambient °C mapping |
| `CR05` | `00` | Exhaust-sensor count while off |
| `CR06` | `03` | Thermostat jumper/contacts closed |
| `CR07` | `2D` | Cold/off feeder interval-like value; engineering meaning unresolved |
| `CR08` | `04` | Stove data format |
| `CR09` | `00` initially | Fan trim at the then-current full-low position |
| `CR0A` | `49` | Owner's feed-trim setting |
| `CR0B` | `02` | Firmware major |
| `CR0C` | `02` | Firmware minor |
| `CR0D` | `00` | Unknown/reserved |
| `CR0E` | `00` | Version/readback value |

The first `CR0B` pass encountered a partial telemetry fragment and the CLI
reported `unsupported response prefix: '0'`; an immediate retry returned
`CR0B=02`. The raw evidence is retained rather than edited.

## Physically correlated inputs

Each input was changed alone while the controller was cold/off, then restored.

| Input | Normal/restored | Changed | Confirmed mask/polarity |
| --- | ---: | ---: | --- |
| Firebox door | `CR02=12` closed | `CR02=32` open | `CR02 & 0x20`; 1=open |
| Ash drawer | `CR02=12` closed | `CR02=52` open | `CR02 & 0x40`; 1=open |
| Fuel selector | `CR02=12` wood/Fuel B | `CR02=16` corn/Fuel A | `CR02 & 0x04`; 1=corn |
| Thermostat | `CR06=03` jumper installed/closed | `CR06=07` jumper removed/open | `CR06 & 0x04`; 1=open |
| OFF button | `CR01=00` released | `CR01=01` held | Value `0x01` |
| DOWN button | `CR01=00` released | `CR01=08` held | Value `0x08` |
| UP button | `CR01=00` released | `CR01=04` held | Value `0x04` |

The ON button was intentionally not tested. The input results live-validate the
previous static/emulator mappings on the physical 9067-0604 controller.

## Trim potentiometers

| Control | Full CCW | Physical center | Full CW | Restored final value |
| --- | ---: | ---: | ---: | ---: |
| Fan trim / `CR09` | `00` | `78` | `FF` | `78` |
| Feed trim / `CR0A` | `00` | `79` | `FF` | `49` |

The knobs were accidentally bumped during later thermostat handling. Direct
reads restored and verified `CR09=78` and `CR0A=49`. This also explained the
temporary `T03=CF` and `T04/T05=59` values in one capture; they are preserved
as real traffic but are not thermostat effects.

## Format-04 telemetry correlations

Format 04 repeatedly emitted `T00` through `T15`, with `T08` appearing twice
per cycle, plus addressed `DW` auxiliary lines. Two long EEPROM-read logs
contained about nine complete cycles each; median cycle period was about
3.583-3.585 seconds.

The following correlations are live-supported:

| Field | Observation | Current conclusion |
| --- | --- | --- |
| `T03` | Followed fan trim, including centered `78` and accidental `CF` | Format-04 fan-trim sample |
| `T04` | Followed feed trim near `49`; changed after knob bump | Format-04 feed-trim sample |
| `T05` | Closely followed `T04` in these captures | Related/filtered value; exact role unresolved |
| `T06` | Closed `00`; firebox open observed `89`, `85`, then `84` | Dynamic firebox-related value; timer/filter/scaling unresolved |
| `T08` | Both closed `00`; firebox LED flash sampled `08`; ash LED flash sampled `10`; off flash phases sampled `00` | Instantaneous warning/LED bit field, not a stable raw switch value |
| `T09` | Cold/off baseline `07` | Format-04 cold/off state candidate |
| `T0C` | Thermostat closed `20`; open `28`; restored `20` | Bit `0x08` indicates thermostat contacts open |
| `DW06` | `05` in controls; `06` with ash open and also with corn selected | Not uniquely an ash-drawer field; exact meaning unresolved |

The firebox-warning and ash-warning values match the visibly flashing panel
LEDs: a sample may read zero during the off phase. The stable door, drawer, and
fuel states should be read from `CR02`, and the thermostat input from `CR06`.

The corn capture contained one transient `T0F=43`, followed by `T0F=00` in the
same run; it is not accepted as a stable fuel field. No unique stable T-slot
fuel indication was established.

These observations prove that the later BixCheck format-05/07 logical field
table cannot be applied position-for-position to format 04. In particular,
later documentation naming `T06` as convection-fan level is not a valid label
for this live format-04 stream.

## EEPROM preservation

Three complete read-only A00-AFF acquisitions agreed byte-for-byte: the JSON
backup and two independent traffic-log backups each contain all 256 unique
addresses. The decoded 256-byte EEPROM SHA-256 is:

```text
5ceb73151c785a4561f37abe5f379bd1f94d3b6833fc83636453d82124174f0e
```

The uppercase 512-character `.raw_hex` text, when emitted by `jq -r` including
its final newline, has SHA-256:

```text
3dfb7aefbc8084f4dd353943d0cf7d60f2fb9ccef62bc8e52a11338133d8f2b9
```

Decoded individualization:

| Field | Value |
| --- | --- |
| Stored/calculated checksum | `EFCE` / `EFCE` (matches) |
| EEPROM data format | `04` |
| EEPROM serial string | `2060` |
| EEPROM production-date string | `01102007` |
| EEPROM model string | `Bixby Model 115` |

The appliance nameplate says serial 5215 and December 2005. The EEPROM says
serial string 2060 and production-date string `01102007`. Both are preserved;
the discrepancy is not assigned a cause. It may reflect controller replacement,
factory individualization history, or another meaning of the stored strings.

## End-of-session state

The owner restored every manipulated control and verified:

```text
CR01=0x00
CR02=0x12
CR06=0x03
CR09=0x78
CR0A=0x49
```

This corresponds to no button pressed, wood selected, both doors closed,
thermostat jumper installed, fan trim centered, and the original feed setting.

## 2026-08-23 control and fault addendum

The later session is preserved under
[`research/live/2026-08-23-fw202-control-faults/`](../../research/live/2026-08-23-fw202-control-faults/).
It extends—but does not rewrite—the original cold/off evidence boundary.

### Normal control

The controller received the recovered front-panel commands and the operator
observed the corresponding physical behavior:

| Action | Exact request |
| --- | --- |
| OFF | `CW0E11` |
| ON | `CW0E12` |
| UP | `CW0E14` |
| DOWN | `CW0E18` |

The generated validation report remains conservative where an automated
format-04 state snapshot could not independently verify the transition. The
low-level bytes are physically validated; the high-level API executor remains
blocked pending reliable format-04 state and level decoding.

### Flashing light 8

The fault capture began while the single rightmost/light-8 indicator was
already flashing. Seventeen `T08` samples were received in about 30 seconds:
ten were `00` and seven were `80`. The maximum interval between `80` samples
was approximately 6.14 seconds. The last raw value was zero, so both original
latest-value snapshots missed the fault despite the physical lamp continuing
to flash.

This establishes `T08.7`/`0x80` as format-04 flashing light 8, which the owner
manual names feeder-wheel failure. Together with the earlier live `0x08`
firebox/light-4 and `0x10` ash-drawer/light-5 cases, the evidence supports a
one-bit-per-light bitmap. Other factory patterns are decoded from that layout
but retain an inferred rather than live-confirmed serial evidence label.

`T13` remained `BA`, matching the cold/off evidence. This reinforces the
profile boundary: later BixCheck labels T13 Alarm status, but it is not the
validated fault source for this format-04 controller.

The API now retains a nonzero T08 bit for eight seconds of subsequent observed
T08 stream time. This interval exceeds the longest live gap with margin.
Serial loss marks the snapshot stale rather than advancing the clearing clock.

## Software consequences

The live stream exposed two parser assumptions that were acceptable in the
offline fixtures but not on this controller:

1. A matching addressed reply can occur after more than 16 interleaved frames.
2. Opening a port mid-burst can present a bounded partial first line.

`MaxFireClient.query_register()` now searches until the configured serial
timeout by default, retains an optional explicit frame bound, and discards a
malformed opening fragment while the raw traffic logger preserves every byte.
Regression tests cover 32 interleaved frames and `0f\n` resynchronization.

## Remaining boundaries

- No firmware program-memory image was extracted; only internal data EEPROM was
  read over the normal application protocol.
- No physical ON, actuator, igniter, fan, feed, ash-drive, or remote-write test
  was performed.
- J3-3 remains unresolved and must stay disconnected.
- `T06` scaling, `DW06`, the remaining format-04 slots, and behavior while the
  stove is operating remain unresolved.
- Firmware 2.02 itself is not among the preserved HEX images. A non-destructive
  in-circuit programming read remains future work and may be blocked by PIC
  code-protection configuration.
