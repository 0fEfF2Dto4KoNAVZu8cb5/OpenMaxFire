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

## Door-state result

The firmware confirms several direct input bits are exposed through CR02 and CR06, but it does not yet prove which one represents the firebox door. Live correlation is still required; see the register map.
