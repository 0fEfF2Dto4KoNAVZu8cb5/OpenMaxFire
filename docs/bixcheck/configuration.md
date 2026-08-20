# BixCheck configuration model

This inventory is extracted from the 2007 BixCheck How-To Guide. It describes capabilities and ranges, not yet protocol addresses.

## Individualization fields

| Field | Format | Purpose |
| --- | --- | --- |
| Software version | Four hexadecimal characters | Installed stove software |
| Internal checksum | Four hexadecimal characters | Configuration checksum calculated by stove |
| Calculated checksum | Four hexadecimal characters | Local BixCheck calculation |
| Internal data format | Two hexadecimal characters | Database format used by stove |
| Calculated data format | Two hexadecimal characters | Format expected by BixCheck |
| Serial number | Eight text characters | Stove identity |
| Production date | `mmddyyyy` | Production identity |
| Model name | Sixteen text characters | Machine description |

The stove uses calibration data only when checksum and data-format values match.

## Fuel A and Fuel B tables

Each fuel bank contains eight fan adjustments, eight feed adjustments, and eight ash-counter increments. Fan/feed adjustment fields use 0-255 percentage-like values; ash fields add 0-255 counts per feed cycle.

Each bank also contains:

| Field | Documented range |
| --- | ---: |
| Startup fan | 0-255 |
| Startup feed | 0-255 |
| Startup time percent | 0-255 |
| Igniter time percent | 0-255 |
| Ash-dump fan | 0-255 |
| Ash-dump feed | 0-255 |
| Ash-dump time percent | 0-255 |
| Ash-dump heat level | 0-8 |
| Ash-dump target percent | 0-100 |
| Thermocouple value for 25% convection fan | 0-510 |
| Thermocouple value for 100% convection fan | 0-510 |

## Safe implementation rules

- Read and save the complete original configuration before any edit.
- Preserve the exact software/data-format pairing.
- Reject out-of-range or nonnumeric values.
- Allow individual edits without forcing a full memory format.
- Show a field-level diff and require confirmation before sending.
- Serialize writes so readback, calculate, initialize, format, and individual writes cannot overlap.
- Read every value back and verify the checksum/data format.
- Keep full format/individualization behind an expert workflow because it overwrites factory calibration.
