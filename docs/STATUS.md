# Research status

Snapshot date: 2026-08-20

OpenMaxFire separates evidence into four levels:

- **Vendor-documented** - stated in recovered Bixby documentation.
- **Statically confirmed** - visible in a preserved executable or firmware image.
- **Owner-reported** - observed or reported by the stove owner but not yet independently measured.
- **Unverified hypothesis** - plausible and useful for planning, but requires a bench or stove test.

## Established facts

| Area | Finding | Evidence |
| --- | --- | --- |
| Stove | Serial number 5215 | Nameplate photograph |
| Stove | Model identified as MaxFire 115 | Owner report |
| Controller | Main PCB reported as 9067-0604, manufactured December 2005, assembly marked `12/15` | Owner report |
| BixCheck 5.0.21 | Monitor, calibration, telemetry, logging, Checkout, and Downloader are documented | Vendor manual/release package |
| BixCheck 5.5.00 | Paired with stove software 2.70 and database 07 | Preserved executable strings |
| BixCheck 5.5.01 | Paired with stove software 2.71 and database 07 | Preserved executable strings |
| Firmware 2.06 | Downloader and PICkit images preserved; PICkit adds bootloader/service code and EEPROM defaults | Vendor package and static comparison |
| Firmware 2.70 | Embedded HEX extracted and verified; 7,681 PIC16F877A program words | Preserved package and deterministic extraction |
| Firmware 2.71 | Embedded HEX re-extraction matches prior recovery; 7,755 PIC16F877A program words | Preserved package and two independent disassembly paths |
| Firmware identity | CR0B/CR0C constants encode 2.06, 2.70, and 2.71 | Cross-version firmware disassembly |
| Normal protocol | `CRXX` reads and `CWXXYY` writes ASCII hexadecimal bytes | BixCheck and firmware disassembly |
| Responses | ASCII hexadecimal output terminates with LF (`0x0A`) | Firmware disassembly |
| UART generation change | SPBRG changes from `0x40` in 2.06 to `0x20` in 2.70/2.71; TXSTA/RCSTA stay `0x26`/`0x90` | Cross-version firmware disassembly |
| Remote buttons | OFF=`CW0E11`, ON=`CW0E12`, UP=`CW0E14`, DOWN=`CW0E18` | BixCheck 5.5.01 static analysis |
| J3 location | Black four-pin connector behind the fan/feed trim-control tab | Vendor 2.06 release notes |
| Cable | Factory custom computer cable is Bixby P/N 2013324 | Vendor manual |

## Important unresolved items

| Question | Current position | Next evidence |
| --- | --- | --- |
| J3 pinout/levels | Unknown; do not assume TTL or standard RS-232 | Unpowered continuity plus protected voltage/polarity measurements |
| Baud rate | Divisors imply nominal 19,200 for 2.06 and 38,400 for 2.70/2.71 if the oscillator is 20 MHz | Confirm oscillator, then passively capture the matching BixCheck generation |
| Command terminator | Firmware consumes fixed command fields; only response LF is confirmed | Capture BixCheck traffic |
| Ack/response frame | Not decoded | Trace `CollectResponse()` and capture live traffic |
| Door input | Candidates are CR02 bits 4-7 and CR06 bit 2 | Poll while operating each switch |
| Telemetry mapping | Vendor field list is known; underlying register/stream mapping is not | Correlate BixCheck tables with captures and firmware |
| EEPROM/config map | Capability is known; address map is not | Trace BixCheck readback/write functions |
| Checkout commands | Function inventory is known; command map is not | Static analysis only until a protected test fixture exists |
| Firmware downloader | The PICkit reset/bootloader region and Downloader/PICkit image delta are mapped; wire protocol is not decoded | Trace the PICkit-only serial routine, then capture on sacrificial/bench hardware |

## Current blocker

The correct physical cable/interface has not arrived. All findings in the repository are therefore static; no J3 command has been validated against serial 5215 yet.
