# J3 protocol working specification

Status: statically reconstructed from all three BixCheck executables and all
three application-firmware generations; every `CR00`-`CR0E` exchange, every
`AR00`-`ARFF` read, every C-write handler, and every periodic telemetry slot is
corroborated in offline PIC emulation. Nothing has yet been validated on serial
5215's J3 port.

## Physical interface

Vendor release notes describe J3 as a black four-pin connector just behind the
tab holding the exhaust-fan and feed-rate adjustment knobs. The BixCheck manual
says the PC interface requires custom Bixby cable P/N 2013324 and supports PC
serial ports or USB-to-serial converters on the computer side.

The [installed-controller photographs](../hardware/installed-controller-photographs.md)
directly confirm a black, single-row, four-contact J3 on serial 5215's main
board. Its legible `-0604` suffix corroborates the owner-reported `9067-0604`.
The images confirm connector identity and placement only; the solder side and
individual nets are not visible.

That does not establish that J3 itself carries standard RS-232 voltages. Pin
order, ground, power, polarity, logic levels, and isolation remain unknown. Do
not attach a generic serial adapter directly.

## PC serial settings

Direct reconstruction of BixCheck's Win32 DCB setup establishes 8 data bits, no
parity, and one stop bit. DTR and RTS are enabled; hardware/software flow
control is disabled.

| BixCheck | Intended firmware | Selectable baud |
| --- | --- | --- |
| 5.0.21 | 2.06 | 9,600 only |
| 5.5.00 | 2.70 | 9,600 or 19,200 |
| 5.5.01 | 2.71 | 9,600 or 19,200 |

The firmware uses `TXSTA=0x26`, `RCSTA=0x90`, and these divisors:

| Firmware | SPBRG | At 10 MHz | Matching intended PC rate |
| --- | ---: | ---: | ---: |
| 2.06 | `0x40` | 9,615 | 9,600 |
| 2.70 | `0x20` | 18,939 | 19,200 |
| 2.71 | `0x20` | 18,939 | 19,200 |

For the PIC16F877A high-speed asynchronous UART,
`baud = Fosc / (16 × (SPBRG + 1))`. The exact host settings make a 10 MHz
controller oscillator the strong compatibility inference. The marking/frequency
must still be physically confirmed before a live connection.

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
while waiting for a non-telemetry result. This proves that unsolicited telemetry
can be interleaved with request/response traffic.

The experimental emulator executes the real 2.06, 2.70, and 2.71 code from
reset. All 45 CR reads reach their expected handler and shared formatter; all
768 A-unit reads return the injected internal-EEPROM fixture byte; all 48 safe
synthetic C-write probes reach their handler; and all 91 periodic slots reach
the real telemetry sender. This confirms software paths offline; it does not
establish electrical compatibility or make writes safe.

## Remote front-panel actions

All three BixCheck builds encode these writes to controller register 0x0E:

| Action | Value | Request |
| --- | ---: | --- |
| OFF | `0x11` | `CW0E11` |
| ON | `0x12` | `CW0E12` |
| UP | `0x14` | `CW0E14` |
| DOWN | `0x18` | `CW0E18` |

They are software-confirmed but have not been sent to a stove.

The complete `CW00`-`CW0F` dispatcher, including actuator/service registers and
the excluded loader key, is in [controller-writes.md](controller-writes.md).

## Downloader is a different protocol

Firmware servicing begins with the state-changing `CW0FC4` reset request, then
uses raw binary control bytes and program blocks. It is not an extension of the
ASCII register grammar and is intentionally excluded from normal OpenMaxFire
APIs. See [the downloader analysis](../reverse-engineering/bixcheck-downloader-protocol.md).

## First live read-only sequence

1. Confirm J3 ground, pinout, idle voltage, and polarity using protected
   high-impedance measurements.
2. Confirm the board oscillator marking/frequency.
3. Use an isolated, current-limited, level-correct interface with transmit held
   disabled initially.
4. Passively observe idle and any controller traffic with the stove not firing.
5. Match 9,600 to 2.06 or 19,200 to 2.70/2.71 based on a read-only version probe;
   do not guess with writes.
6. Send only `CR00`, capture exact bytes/timing, and require `CR0000` plus CR/LF.
7. Read CR08 and CR0B-CR0E to identify data format and firmware.
8. Only after stable read-only behavior, validate the offline mappings
   (door=CR02.5/RD1, drawer=CR02.6/RD4, thermostat=CR06.2/RB4) by toggling one
   safe switch at a time while the appliance is cold and off.

No `CW` request belongs in the first live session.
