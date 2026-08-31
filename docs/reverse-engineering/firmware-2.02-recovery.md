# Firmware 2.02 recovery report

## Result

OpenMaxFire now preserves one complete PICkit export from the original
PIC16F877A removed from serial 5215's controller. It is the first recovered
program image for the controller that previously identified itself over J3 as
firmware `2.02`, data format `04`.

The immutable source is
`preservation/original/firmware/2.02/Bixby_0202_260827_PICkit.hex`, SHA-256
`272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab`.

## Evidence chain

1. The physical controller reported CR0B=`02`, CR0C=`02`, and CR08=`04` in the
   preserved August 2026 J3 sessions.
2. Three independent J3 reads produced the same 256-byte A00-AFF EEPROM image.
3. The newly supplied PICkit export contains a complete 256-byte data EEPROM
   that is byte-for-byte identical to that earlier live backup.
4. The export contains the same reset redirection and resident loader as the
   independently preserved factory 2.06 PICkit image.
5. The 2.02 application region differs from 2.06 in 7,478 of 7,808 same-address
   words. The file is therefore not merely a relabeled copy of the 2.06 image.

The EEPROM match ties the export to the previously observed controller much
more strongly than a filename alone. The live identification and program
structure together support cataloguing it as the serial-5215 firmware 2.02
read. It is the sole pre-write export: the original was
subsequently programmed during emergency recovery, so later reads cannot serve
as independent captures of that earlier state.

## Structural inspection

| Property | Recovered value |
| --- | --- |
| File size | 46,536 bytes |
| Intel HEX records | 1,058 data, 1 extended-linear-address, 1 EOF |
| Program words | all 8,192 words, `0x0000`-`0x1FFF` |
| Erased program words | 14 words containing `0x3FFF` |
| Data EEPROM | all 256 bytes |
| User ID words | four, all `0x3FFF` |
| Configuration word | `0x3F32` |
| Undecoded PIC14 words | 0 |
| Code protection | program and EEPROM protection disabled |

The Device ID location is absent. That omission is permitted in programmer
exports and is recorded rather than synthesized.

## Relationship to 2.06 PICkit

| Region | Words | Identical | Different |
| --- | ---: | ---: | ---: |
| Complete program | 8,192 | 714 | 7,478 |
| Application delivery range `0x0000`-`0x1E7F` | 7,808 | 330 | 7,478 |
| Protected loader range `0x1E80`-`0x1FFF` | 384 | 384 | 0 |
| Reset vector `0x0000`-`0x0003` | 4 | 4 | 0 |
| Resident loader body `0x1E88`-`0x1FFF` | 376 | 376 | 0 |

The experimental PIC14 emulator executes the recovered reset/loader path and
returns `EB` for the `EA` identification probe in 43 steps. This confirms a
software path under the documented synthetic model; it does not prove live
electrical timing or safe flashing.

## Produced research artifacts

The deterministic pipeline emits a byte-identical analysis copy, sparse-memory
map, program binary, EEPROM CSV, decoded program-word table, portable and
annotated disassemblies, pairwise comparisons, and the loader emulator trace
under `reverse-engineering/firmware/2.02/` and
`reverse-engineering/firmware/emulation/`.

## Remaining gates

1. Preserve immutable copies and hashes of the sole pre-write original export;
   do not represent later reads as independent pre-write captures.
2. Keep the original safely stored and do not program it again absent an
   explicit recovery need.
3. Program a spare PIC, verify it, read it back, and authenticate that
   readback against the original image.
4. Install the verified clone in the socket and confirm board boot, 2.02/04
   identification, EEPROM identity, and normal read-only J3 behavior.
5. Use the recovered 2.02 application to decode format-04 state and telemetry,
   then validate those meanings against new live captures.
6. Test configuration and J3-loader behavior only on externally recoverable
   spare hardware.

No physical firmware-write path is enabled by this recovery.
