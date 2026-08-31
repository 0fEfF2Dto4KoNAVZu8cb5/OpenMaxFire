# BixCheck configuration model

This map combines vendor documentation with decoded tables and methods from all
three BixCheck executables. Addresses are statically established. Complete
format-04 and format-05 configurations have since been read from serial 5215
under documented read-only sessions. A checksum-only `CW0100` repair that
changed A00/A01 and survived a true cold boot is live-validated on firmware
2.06; arbitrary configuration writes and formatting remain unqualified.

## Data-element record layout

BixCheck stores UI/configuration definitions in fixed 0x58-byte records:

| Offset | Size | Field |
| ---: | ---: | --- |
| `0x00` | 1 | data type |
| `0x01` | 32 | label |
| `0x21` | 32 | units/secondary description |
| `0x44` | 4 | signed value/default |
| `0x48` | 1 | unit/tag (`A`, `C`, `T`, `V`, or empty) |
| `0x49` | 1 | address/index |
| `0x4C` | 4 | signed maximum |
| `0x50` | 4 | signed minimum |
| `0x54` | 2 | byte/string length or bit mask |
| `0x56` | 2 | display/edit mode |

Recovered type behavior:

| Type | Interpretation |
| ---: | --- |
| 0 | no value |
| 1, 5 | unsigned 8-bit |
| 2 | signed 8-bit |
| 3, 4, 6 | big-endian 16-bit |
| 7, 8 | fixed-length string |
| 10 | bit field |

## Individualization map

| Address/source | Length | Field |
| --- | ---: | --- |
| C0B | 2 | stove software version (C0B/C0C) |
| A00 | 2 | stove-stored checksum |
| computed | 2 | BixCheck-calculated checksum |
| C08 | 1 | stove data format |
| A02 | 1 | EEPROM data format expected by BixCheck |
| A03 | 8 | serial number |
| A0B | 8 | production date |
| A13 | 16 | model name |
| A23 | 13 | spare/reserved range |

The stove uses calibration data only when checksum and data-format values
match. Firmware-emulator events confirm that A-unit reads traverse the
PIC16F877A's internal 256-byte data EEPROM registers, not an external I²C
EEPROM. All 256 addresses execute normally in each application generation
against a synthetic fixture. Identity strings and calibration must be backed
up before any write.

## Fuel-table map

Both generations expose Fuel A and Fuel B banks. The repeated eight-level
ranges are:

| Fuel A | Fuel B | Meaning |
| --- | --- | --- |
| A40-A47 | A70-A77 | fan adjustments, levels 1-8 |
| A48-A4F | A78-A7F | feed adjustments, levels 1-8 |
| A50-A57 | A80-A87 | ash-counter increments, levels 1-8 |
| A58 | A88 | startup fan |
| A59 | A89 | startup feed |
| A5A | A8A | startup time |
| A5B | A8B | igniter time |
| A60-A64 | A90-A94 | ash-dump settings |
| A68-A69 | A98-A99 | convection-fan thermocouple points |
| A6A | A9A | thermostat heat level (A6A added in 5.5) |

5.0.21/data format 05 stops at A9A and has 71 displayed adjustment records.
5.5.x/data format 07 adds:

| Fuel A | Fuel B | Type/range |
| --- | --- | --- |
| A6B | A9B | LB threshold, unsigned 0-100% |
| A6C | A9C | LB fan adjustment, signed -30..30 |
| A6D | A9D | LB feed adjustment, signed -30..30 |
| A6E bit 1 | A9E bit 1 | ratio/ash trimpot mode |
| A6E bit 2 | A9E bit 2 | disable automatic restart |

The two bit records share each physical A6E/A9E byte. A replacement editor must
merge bits rather than writing either record as an independent whole byte.

## Lean-burn display conversions

BixCheck 5.5 does not display the A6B-A6D/A9B-A9D wire bytes directly. Its exact
forward transforms are:

- threshold: `(raw × 100 + 100) >> 7`;
- fan: signed, truncating `(raw - 128) × 100 / 128` toward zero;
- feed: signed, truncating `(128 - raw) × 100 / 128` toward zero.

The reverse path truncates `percentage × 128 / 100` and uses explicit
center-away corrections for fan/feed. Tested byte-exact implementations are in
`src/openmaxfire/protocol.py`; the original instructions are preserved in each
5.5 `protocol-core.asm`.

## Checksum

For every logical byte from A02 through the format-specific endpoint:

1. add the byte to a 16-bit accumulator;
2. rotate the 16-bit accumulator left by one bit.

| Data format | Last included address |
| ---: | --- |
| 0/1 | A4B |
| 2/3 | A4C |
| 4 | A69 |
| 5 | A9A |
| 7 | AFF |

Format 06 was not present in the reconstructed switch and remains unsupported.
For format 07, BixCheck converts displayed A6B-A6D/A9B-A9D values back to wire
encoding before checksum calculation.

## Safe implementation rules

- Read and save the complete original configuration before any edit.
- Preserve the exact software/data-format pairing.
- Reject missing, out-of-range, or nonnumeric values.
- Show a field-level and raw-byte diff before sending.
- Merge shared bit fields and serialize all writes.
- Read every value back and verify both checksum and data format.
- Keep format/individualization/downloader functions outside normal control
  APIs and behind an expert recovery workflow.

Every decoded field, including 5.0.21/5.5 bounds, is available in the generated
`data-elements.csv` files.
