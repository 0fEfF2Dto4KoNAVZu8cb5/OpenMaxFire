# J3 protocol working specification

Status: statically reconstructed from all three BixCheck executables and all
three preserved application-firmware generations, then live-validated
read-only on serial 5215's older firmware 2.02/data-format 04 controller on
2026-08-22. Physical loader experiments on 2026-08-29/30 recorded 12
incorrectly low-byte-first `E3` attempts before their underlying transport
writes; three subsequent `E7` replies prove at least three complete frames
reached the controller, and PICkit readback proved three changed reset-vector
words. The corrected high-byte-first frame has never been attempted physically,
and all physical loader traffic is now locked in the CLI and public executors.

## Physical interface

Vendor release notes describe J3 as a black four-pin connector just behind the
tab holding the exhaust-fan and feed-rate adjustment knobs. The BixCheck manual
says the PC interface requires custom Bixby cable P/N 2013324 and supports PC
serial ports or USB-to-serial converters on the computer side.

The [installed-controller photographs](../hardware/installed-controller-photographs.md)
locate the black, single-row, four-contact J3. The later
[bare-controller photographs](../hardware/bare-controller-photographs.md)
directly show both PCB sides, complete `9067-0604` marking, PIC16F877A, and
`10.000` MHz oscillator. Owner continuity tracing plus successful live traffic
establish J3-1=stove RX, J3-2=stove TX, J3-4=ground. J3-3 remains unresolved
and disconnected. The preserved pre-validation FTDI photograph has the two
signal wires reversed and is explicitly marked incorrect. See
[the hardware pinout](../hardware/j3-interface.md).

The working adapter is an FTDI `TTL-232R-5V-WE`; adapter VCC was not connected.
This validates non-inverted TTL UART compatibility for the tested board. It
does not make a generic DB9/bipolar RS-232 adapter safe on J3.

## PC serial settings

Direct reconstruction of BixCheck's Win32 DCB setup establishes 8 data bits, no
parity, and one stop bit. DTR and RTS are enabled; hardware/software flow
control is disabled.

| BixCheck | Intended firmware | Selectable baud |
| --- | --- | --- |
| 5.0.21 | 2.06 | 9,600 only |
| 5.5.00 | 2.70 | 9,600 or 19,200 |
| 5.5.01 | 2.71 | 9,600 or 19,200 |

The live controller identified itself as firmware 2.02/data format 04 and
responded at 9,600 baud. A 19,200-baud `CR00` attempt timed out.

The firmware uses `TXSTA=0x26`, `RCSTA=0x90`, and these divisors:

| Firmware | SPBRG | At 10 MHz | Matching intended PC rate |
| --- | ---: | ---: | ---: |
| 2.06 | `0x40` | 9,615 | 9,600 |
| 2.70 | `0x20` | 18,939 | 19,200 |
| 2.71 | `0x20` | 18,939 | 19,200 |

For the PIC16F877A high-speed asynchronous UART,
`baud = Fosc / (16 × (SPBRG + 1))`. The exact host settings make a 10 MHz
controller oscillator the strong compatibility inference. The bare-board
photographs now physically confirm the installed oscillator's `10.000` marking.

## Requests

`bixby110io::regio()` in every EXE builds fixed-length uppercase ASCII requests:

| Operation | Grammar | Length | Example |
| --- | --- | ---: | --- |
| Read | `<unit>R<address:02X>` | 4 | `CR02` |
| Write | `<unit>W<address:02X><value:02X>` | 6 | `CW0E14` |

There is no CR, LF, NUL, or other request terminator. BixCheck uses A, C, and D
unit spaces internally; C is the controller/command space. The stove firmware's
ASCII nibble decoder handles digits and uppercase A-F. Replacement tools should
therefore send uppercase only.

## Responses

BixCheck's `scanio()` removes CR and LF and then dispatches:

| Family | Grammar | Meaning established |
| --- | --- | --- |
| A/C/D | `<unit><operation><address:02X><value:02X>` | Addressed one-byte result |
| T | `T<index:02X><value:02X>` | One telemetry byte |
| M | `M...` | Status/control family; payload unresolved |
| I | `I...` | Status/control family; payload unresolved |

Incoming hex accepts upper- or lowercase. Leading control bytes `01`, `02`, or
`03` are stripped and the remainder is re-dispatched. `async::read_string()`
accepts either CR or LF as the line terminator. Firmware transmit paths
explicitly emit LF. The real firmware formatter emits lowercase letters for
hexadecimal nibbles A-F: for example, uppercase request `CR0A` returns
`CR0a00` plus LF in the synthetic baseline. Clients must parse response hex
case-insensitively.

All preserved firmware telemetry senders emit the five-character T form only.
Logical 16-bit fields arrive as adjacent lines—for example, T0A high then T0B
low—and BixCheck combines them big-endian. The OpenMaxFire parser continues to
accept the older seven-character host/capture representation for compatibility,
but it is not a recovered physical firmware frame. Some periodic slots first
send an addressed `DWxxyy` auxiliary/diagnostic line; D and T are stored in
separate BixCheck arrays. See [the telemetry map](telemetry-fields.md).

For an addressed response, BixCheck stores bytes 4-5 as the value at the
address in bytes 2-3. It does not meaningfully validate byte 1; OpenMaxFire
retains it as the operation field and applies stricter length/character checks.

`CollectResponse()` makes no more than 16 scan attempts and skips `T` frames
while waiting for a non-telemetry result. This proves that telemetry can be
interleaved with request/response traffic. The live format-04 controller can
place a valid addressed response after more than 16 complete `T`/`DW` frames,
so OpenMaxFire no longer copies that fixed limit by default; it matches until
the configured serial timeout.

The experimental emulator executes the real 2.02, 2.06, 2.70, and 2.71 code.
All 58 real CR handlers reach their shared formatter; all 1,024 A-unit reads
return the injected internal-EEPROM fixture byte; all 63 safe synthetic C-write
probes reach their handler; and all 113 periodic slots reach the real telemetry
sender. The 2.02 boot fixture has an explicit synthetic CCP1/startup boundary.
This confirms software paths offline; it does not establish electrical
compatibility or make writes safe.

## Remote front-panel actions

All three BixCheck builds encode these writes to controller register 0x0E:

| Action | Value | Request |
| --- | ---: | --- |
| OFF | `0x11` | `CW0E11` |
| ON | `0x12` | `CW0E12` |
| UP | `0x14` | `CW0E14` |
| DOWN | `0x18` | `CW0E18` |

All four were successfully sent to and physically observed on the live
firmware-2.02 controller. This validates the command bytes, but a serial write
receipt alone still does not prove a requested transition completed.

The complete `CW00`-`CW0F` dispatcher, including actuator/service registers and
the excluded loader key, is in [controller-writes.md](controller-writes.md).

## Downloader is a different protocol

Firmware servicing uses raw binary control bytes and program blocks after a
hardware or application-requested reset. Firmware 2.06/2.70/2.71 implement the
state-changing `CW0FC4` reset request; the exact original 2.02 image does not
have a `CW0F` table entry or keyed reset handler, so its first update requires a
hardware reset. The binary protocol is not an extension of the ASCII register
grammar and is intentionally excluded from normal OpenMaxFire APIs. See
[the downloader analysis](../reverse-engineering/bixcheck-downloader-protocol.md).

## Completed first live read-only sequence

The 2026-08-22 session completed the intended first-live sequence without any
write:

1. traced J3 ground/TX/RX and left J3-3 disconnected;
2. confirmed the physical 10 MHz oscillator marking;
3. inventoried and wired the official 5 V TTL FTDI adapter without VCC;
4. observed no spontaneous passive traffic;
5. rejected 19,200 and established 9,600 8N1;
6. captured exact `CR00`/`CR0000` bytes and LF termination;
7. identified firmware 2.02/data format 04;
8. completed three identical A00-AFF EEPROM reads; and
9. live-validated door, drawer, thermostat, fuel, button, and trim-pot inputs
   while cold/off.

See [the complete live report](../reverse-engineering/live-fw202-format04.md).
Future live sessions remain read-only unless a separate, reviewed plan
explicitly authorizes a known command. No `CW` request was sent in this session.
