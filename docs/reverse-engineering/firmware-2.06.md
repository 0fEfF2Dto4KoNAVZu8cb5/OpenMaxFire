# Stove firmware 2.06 reverse engineering

Source: `Bixby110_115_02060021_and_manual.zip`, released with BixCheck 5.0.21. The vendor package names the stove release `02.06.00.21` and supplies two programming images.

## The two images

The Downloader and PICkit files contain the same main stove application, but they are not interchangeable container variants:

- 7,599 program-word addresses are common; 7,595 words match and only the four reset-vector words differ.
- The Downloader reset vector directly enters the application. The PICkit reset vector redirects to `0x1E88`.
- The PICkit image adds 593 mapped program words, including code from `0x1E27` through `0x1FFF`, and supplies all 256 EEPROM bytes.
- The four user-ID words and configuration word also differ. Downloader config is `0x3F76`; PICkit config is `0x3F32`.
- Across all memory regions, nine common addresses differ and the PICkit image has 849 additional words.

This strongly supports the vendor distinction: the Downloader image is the application payload used by the factory updater, while the PICkit image is a complete programmer image with the resident serial service/bootloader path and EEPROM defaults. That final sentence is an inference from the code layout and release notes, not a live programming test.

## PICkit EEPROM image

The PICkit file maps `0x2100-0x21FF`. It includes the ASCII identification `Bixby Model 115` at EEPROM addresses `0x2114-0x2122`, followed by calibration/default tables and erased `0xFF` space. The complete byte-by-byte export is in `analysis/pickit/eeprom.csv`; meanings beyond the visible identification string remain unassigned.

## Protocol anchors

| Word address | Finding |
| ---: | --- |
| `0x0E71` | Receive-buffer character reader |
| `0x0EA4` | Uppercase ASCII-hex nibble decoder |
| `0x0EC0` | Two-character hex-byte parser |
| `0x1008` | `C` command check |
| `0x1014` | `W` command check |
| `0x113F` | `R` command check |
| `0x12A7` | CR00-CR0E dispatch table |
| `0x1265` | ASCII response formatter |
| `0x1800` | Application startup |
| `0x1804` | UART initialization; nearby code loads `SPBRG=0x40` |
| `0x1E88` | PICkit-only reset/serial bootloader entry |

The CR version handlers return `CR0B=0x02` and `CR0C=0x06`. CR08 returns
`0x05`. A read-only 2026-08-30 session subsequently confirmed that exact
firmware/data-format pairing on physical hardware.

## Confidence and safety

Intel HEX structure, hashes, opcodes, constants, and addresses are statically
confirmed. Function names are reverse-engineering annotations. This original
static analysis did not prove electrical levels, packet timing, or safe write
behavior. Later physical sessions sent only incorrectly byte-ordered first
blocks; the corrected 2.06 transfer remains physically untested. See the
[physical-session forensic report](physical-flash-session-forensics.md).

## 2026-08-30 live identification

A separate externally programmed controller was queried read-only through J3.
The exact identity was `CR00=00`, `CR08=05`, `CR0B=02`, `CR0C=06`, `CR0D=00`,
and `CR0E=21`: firmware 2.06, data format 05, build 21. This validates the
static version constants and BixCheck pairing, but it does not validate the J3
firmware-loader path used in the earlier failed update attempts.

The first response began with a NUL byte before the valid `CR0000` line. The
receive parser now discards only leading NUL/control resynchronization bytes;
an embedded NUL remains invalid. No transmitted framing changed.

Two independent complete A00-AFF reads produced the same 256 EEPROM bytes
(SHA-256 `c1b8da891e94357f1d3bb23004d44aa663943f1d28fb734bef56dfa3e5bd0cfd`).
They decode as format 05, model `Bixby Model 115`, serial `Unknown`, and date
`08282026`. The stored checksum is `D168`, while the checksum over the current
record is `576B`; therefore this is not a checksum-valid 2.06 configuration.

The stored `D168` value is exactly the checksum of the vendor record after
changing only serial `5015` to `Unknown`. After also changing the production
date from `04162007` to `08282026`, the correct value becomes `576B`. This
mathematically establishes that the date changed after the last checksum
persistence; it does not identify which software or operator workflow made
the edits.

Comparison with the complete vendor 2.06 PICkit EEPROM found differences only
in 13 identity/checksum bytes. The calibration and fuel-table bytes match the
vendor defaults exactly. Consequently, migrating 2.02 fan tables is not
indicated by this image; the invalid checksum must be resolved before treating
its runtime behavior as a clean 2.06 baseline.

Execution of the real Downloader application in the PIC emulator with the
captured EEPROM and with an otherwise identical checksum-corrected copy first
diverges in the checksum-validation routine around `0x0732`. The failing path
clears validation flags. This proves that the mismatch is visible to firmware,
but the incomplete emulator does not by itself establish the physical fallback
behavior.

The live controller reported `T09=10` (Cooldown), `T06=19` (25% convection
command), `T18=57` (exhaust target), and nonzero exhaust rotation/control
values while both fans were observed running. Thus the persistent fan was
software-commanded, not evidence of a stuck output. The owner-reported flashing
second light coincided with the later-firmware T20 display-event path alternating
between `02` and `00`; the same sender path exists statically in 2.06, 2.70, and
2.71.

The controller subsequently left Cooldown without any host command. T18 and
T06 fell to zero, T09 changed `10`→`20` (Off), and T04/CR05 tracked the exhaust
fan coasting to zero; the owner independently observed that the fan stopped.
A final monitor confirmed stable Off and zero fan command, target, phase, and
speed values with no timeouts. T20 continued alternating `02`/`00`, separating
the latched light-2 fault display from active cooldown.

The timing is exact in the 2.06 image. Startup loads CCPR1=`0xC674`,
CCP1CON=`0x0B`, and T1CON=`0x31`. With the photographed 10 MHz oscillator,
CCP1's Timer1 special event occurs every 0.1625728 seconds. The cooldown
handler changes state to `0x20` after the RAM `0x4B:0x4A` counter passes
`0x1517`, or at event 5,400: 877.893 seconds (about 14 minutes 38 seconds),
provided the adjacent thermocouple/input predicates permit it. The live
transition at `22:50:29Z` back-calculates power-up to approximately
`22:35:51Z`, matching the session start. This proves that the initially
persistent fan was normal 2.06 power-up cooldown behavior, not a migrated fan
table or stuck triac. It does not make the invalid EEPROM checksum acceptable;
that remains a separate configuration defect to repair before active testing.

## Checksum-valid live qualification

The same session later persisted the calculated `576B` checksum with one
audited `CW0100`. Only A00/A01 changed from `D1 68` to `57 6B`; two immediate
complete reads and one after a true AC-off/USB-out cold boot were byte-identical
and checksum-valid. Exact 2.06/05/21 identity and all calibration bytes were
retained.

On that repaired configuration, one-at-a-time physical actions independently
confirmed CR02.5 firebox-open, CR02.6 drawer-open, CR02.2 corn selection, and
CR06.2 thermostat-open. An accidental physical ON produced exact Prefill
T09=`30`, first-light T07=`01`, T06=`19`, T18=`5C`, and live exhaust feedback.
The first remote OFF was ignored while the controller remained in Prefill; one
retry entered repeated T09=`10` Cooldown.

A final unattended read-only capture followed that checksum-valid Cooldown to
Off. The first observed Cooldown was `23:26:58.294226Z`. Last nonzero command
evidence was T06=`19` at `23:41:34.543018Z`, and the first post-gap T09 response
was Off at `23:41:54.722898Z`. The exact 877.893-second firmware prediction is
`23:41:36.187Z`, inside the retained 20.18-second response gap. T18/T06 then
reported zero, T04 reached zero at `23:42:08.667186Z`, and CR05 reached zero at
`23:42:11.960806Z`. All later snapshots remained Off with T07/T13 clear. This
second transition establishes that the recovered Cooldown behavior also holds
with a checksum-valid record; no active command was sent during the capture.
