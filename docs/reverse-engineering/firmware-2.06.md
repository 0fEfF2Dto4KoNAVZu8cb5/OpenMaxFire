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

The CR version handlers return `CR0B=0x02` and `CR0C=0x06`. CR08 returns `0x05`, which is consistent with the BixCheck 5.0-generation data-format identifier but still needs a live/protocol confirmation.

## Confidence and safety

Intel HEX structure, hashes, opcodes, constants, and addresses are statically confirmed. Function names are reverse-engineering annotations. Nothing here proves electrical levels, packet timing, or safe write behavior on physical hardware, and no firmware was sent to a device.
