# J3 protocol working specification

Status: statically reverse-engineered, not yet validated on serial 5215.

## Physical interface

Vendor release notes describe J3 as a black four-pin connector just behind the tab holding the exhaust-fan and feed-rate adjustment knobs. The BixCheck manual says the PC interface requires custom Bixby cable P/N 2013324 and that both built-in serial ports and USB-to-RS-232 converters were used on the PC side.

That does **not** establish that J3 itself carries standard RS-232 voltage levels. Pin order, ground, power, polarity, and electrical levels remain unknown. Do not attach a generic serial adapter directly.

## Normal controller commands

BixCheck 5.5.01 and stove firmware 2.71 independently support uppercase ASCII hexadecimal commands.

| Operation | Format | Example |
| --- | --- | --- |
| Read controller byte/register | `CRXX` | `CR02` |
| Write controller command/register | `CWXXYY` | `CW0E14` |

`XX` and `YY` are two uppercase hexadecimal digits. Firmware code at program address 0x0F60 decodes ASCII `0`-`9` and `A`-`F`; the two-character byte parser begins at 0x0F7C. The controller-command parser checks for `C` at 0x10E8, `W` at 0x10F4, and `R` at 0x120E.

The transmit paths format response bytes as ASCII hexadecimal and send LF (`0x0A`) as a terminator. Exact response prefixes, lengths, and acknowledgement behavior still need decoding.

## Remote front-panel actions

BixCheck's `Bixby110RCButtonData` table and remote-button handlers produce writes to register 0x0E:

| Action | Value | Reconstructed request |
| --- | ---: | --- |
| OFF | `0x11` | `CW0E11` |
| ON | `0x12` | `CW0E12` |
| UP | `0x14` | `CW0E14` |
| DOWN | `0x18` | `CW0E18` |

These are statically confirmed for BixCheck 5.5.01. They have not been sent to a stove.

## UART configuration by firmware generation

All three generations use asynchronous transmit/receive settings `TXSTA=0x26` (`BRGH=1`) and `RCSTA=0x90`. The baud-rate generator changes:

| Firmware | SPBRG | At 20 MHz | At 10 MHz |
| --- | ---: | ---: | ---: |
| 2.06 | `0x40` | 19,231 baud | 9,615 baud |
| 2.70 | `0x20` | 37,879 baud | 18,939 baud |
| 2.71 | `0x20` | 37,879 baud | 18,939 baud |

For a PIC16F877A asynchronous high-speed UART:

`baud = Fosc / (16 * (SPBRG + 1))`

At 20 MHz these are the normal error-tolerant settings for 19,200 and 38,400 baud. At 10 MHz they correspond to 9,600 and 19,200. The actual oscillator must therefore be confirmed before treating any absolute rate as authoritative, and the PC software generation should be matched to the controller firmware during passive capture.

The original v0.1 prototype defaulted to 19,200 baud. Static evidence now shows that this is plausible for 2.06 at 20 MHz or 2.70/2.71 at 10 MHz, but it is not universal.

## First live-test sequence

1. Confirm pinout and voltage levels using protected measurements.
2. Confirm oscillator marking/frequency.
3. Passively capture BixCheck traffic if possible.
4. With the stove safely off, send only `CR00` at the rate supported by the confirmed oscillator and installed firmware generation.
5. Record every byte and timing detail.
6. Read CR00-CR0E and correlate physical inputs.
7. Do not issue `CW` requests until read-only behavior and response verification are stable.
