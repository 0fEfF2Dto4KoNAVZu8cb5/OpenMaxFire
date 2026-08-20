# Stove firmware 2.71 reverse engineering

Source: extracted embedded resource `Bixby_0271_080315.hex` from BixCheck 5.5.01.

SHA-256: `dc4dcf7aeb83c95525053018e010194c55498796b0b65c0ff26a11eb695e556b`

## Image summary

- Target comment: PIC16F877A
- Lowest Intel HEX data address: `0x0000`
- Highest address: `0x400F`
- Overall span: 16,400 bytes
- Parsed type-00 data records: 973
- End-of-file records: one type-01
- Program data reaches `0x3CBD`; configuration words are present at `0x4000-0x4007` and `0x400E-0x400F`
- Contiguous binary produced by the first analysis bundle: 16,400 bytes, SHA-256 `23c55678af7babfbc7bf46161dfea1b442f748676750b2ea6d8630dd7e0753da`
- Normalized mapped program words: 7,755 (`0x0000-0x1E5E`), plus four user-ID words and one configuration word (`0x3F72`)
- Portable decoder result: zero unknown opcodes

## Confirmed code locations

| Address | Finding |
| ---: | --- |
| `0x0000` | Reset vector loads PCLATH and jumps to `0x1825` |
| `0x0F60` | ASCII hexadecimal digit decoder |
| `0x0F7C` | Two-character hexadecimal byte parser |
| `0x10E8` | Checks first controller command byte for ASCII `C` |
| `0x10F4` | Checks second byte for ASCII `W` |
| `0x120E` | Checks second byte for ASCII `R` |
| `0x1221` | CR low-register dispatch |
| `0x1825` | Main startup/peripheral initialization |
| `0x1829` | Writes `SPBRG=0x20` in bank 1 |
| `0x182C` | Writes `TXSTA=0x26` in bank 1 |
| `0x182F` | Writes `RCSTA=0x90` in bank 0 |

## Tooling caveat

gpdasm's automatically printed register names are not always bank-aware. The annotated copy explicitly corrects the UART assignments based on STATUS.RP0. Treat other peripheral names cautiously until their bank context is checked.

The newer portable listing deliberately prints numeric file-register operands and low-11-bit CALL/GOTO targets instead of guessing bank/page state. It was compared against the original gpdasm listing and matches all 7,755 mapped program words and mnemonics. Both versions are retained as independent views.

For changes relative to 2.06 and 2.70, see [the comparative report](firmware-comparison.md).

## Input-state result

Bank-aware emulator traces plus BixCheck's Checkout masks assign firebox door
to CR02 bit 5 / RD1, ash drawer to CR02 bit 6 / RD4, and thermostat to CR06 bit
2 / RB4. Reset-time ADC replay assigns fan and feed potentiometers to AN3/CR09
and AN4/CR0A. These are strong offline mappings, not physical validation of
serial 5215; see the [register map](../protocol/register-map.md) and
[exhaustive emulator pass](emulator-deep-pass.md).
