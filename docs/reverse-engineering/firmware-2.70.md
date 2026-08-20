# Stove firmware 2.70 reverse engineering

Source: `BixCheck_080206.zip` / `BixCheck_080206.exe`. The executable contains an 84,672-character ASCII hexadecimal block immediately before the string `Bixby_0270_070206.hex`. Decoding that block produces a valid 42,336-byte Intel HEX file whose every record checksum passes.

SHA-256: `c6decc8173cadd13f59743df416d783c6de22e55cc9636f5f79dd22dec3e7bca`

## Image summary

- Target: PIC16F877A
- Mapped program words: 7,681
- Program word range: `0x0000-0x1E3E`, with normal compiler/linker gaps
- User-ID words: `0x0004`, `0x0003`, `0x0000`, `0x0002`
- Configuration word: `0x3F72`
- EEPROM data: absent
- Intel HEX records: 964 data records and one EOF record
- Unknown/undecoded program opcodes: zero

## Confirmed code locations

| Word address | Finding |
| ---: | --- |
| `0x00AE` | UART receive interrupt routine |
| `0x0F63` | Receive-buffer character reader |
| `0x0F95` | Uppercase ASCII-hex nibble decoder |
| `0x0FB1` | Two-character hex-byte parser |
| `0x1112` | `C` command check |
| `0x111E` | `W` command check |
| `0x1234` | `R` command check |
| `0x1391` | CR00-CR0E dispatch table |
| `0x1352` | ASCII response formatter |
| `0x1800` | Startup/peripheral initialization |
| `0x1804` | UART initialization; nearby code loads `SPBRG=0x20` |

CR0B and CR0C return `0x02` and `0x70`, directly exposing the 2.70 identity. CR08 returns `0x07`. The handler-by-handler comparison is preserved in `reverse-engineering/firmware/comparison/cr00-cr0e-handlers.csv`.

## Confidence

Extraction offsets, checksums, hashes, opcodes, and constants are statically confirmed. Descriptive function names are annotations inferred from control flow and close structural matches to 2.71. This work did not execute the Windows application or communicate with a stove.
