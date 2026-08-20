# BixCheck telemetry map

The addresses below are decoded directly from BixCheck's 0x58-byte telemetry
records. `T` entries arrive from the serial telemetry stream; `C` and `V`
entries are computed/display records rather than additional T frames.

## Shared 5.0.21 / 5.5.00 table

| Source | Bytes | Field | BixCheck units/conversion label |
| --- | ---: | --- | --- |
| T00 | 1 | Temperature | Temp C, Temp F |
| T01 | 1 | Thermocouple | TC Points |
| T02 | 1 | Fan potentiometer | Fan units, Fan % |
| T03 | 1 | Feed potentiometer | Feed units, Feed % |
| T04 | 1 | Exhaust fan speed | count, RPM |
| T05 | 1 | Exhaust fan phase | count, microseconds |
| T06 | 1 | Convection fan level | percent |
| T07 | 1 | Display LED | LED display |
| T08 | 1 | Igniter state | code, state |
| C00 | computed | Current heat level | current level |
| C00 | computed | Target heat level | target level |
| T09 | 1 | State control | code, mode |
| T0A | 2 | Ash level | 16-bit |
| T0C | 2 | Ash target | 16-bit |
| T0E | 2 | Feed on time | 1/120 s, seconds |
| T10 | 2 | Feed off time | 1/120 s, seconds |
| C00 | computed | Feed cycle time | 1/120 s, seconds |
| T12 | 1 | IIC status | mode |
| T13 | 1 | Alarm status | mode |
| T14 | 1 | Flag status | mode |
| T15 | 1 | Igniter current | raw |
| T16 | 1 | Firedoor timer | raw units |
| T17 | 1 | Ash drawer timer | raw units |
| T18 | 1 | Exhaust fan target | count, RPM |
| T19 | 1 | Drop limit | TC drop limit |
| T1A | 2 | Feed cycle table | 1/120 s, seconds |
| T1C | 2 | Feed cycle calibration | 1/120 s, seconds |
| V1B | computed | Time to ash dump | hours:minutes display |
| C00 | computed | Telemetry mode | UI state |
| C20 | computed | LED no-log | UI state |

## 5.5.01 changes

The first 24 rows remain the same. The tail becomes:

| Source | Bytes | Field |
| --- | ---: | --- |
| T19 | 1 | BF drop limit |
| T1A | 2 | Feed cycle table |
| T1C | 2 | Feed cycle calibration |
| T1E | 1 | LB drop limit |
| V1C | computed | Time to ash dump |
| C00 | computed | Telemetry mode |
| C20 | computed | LED no-log |
| TFD | 1 | Low temp count |
| TFE | 1 | Sample maximum |
| TFF | 1 | Recent sample |

The `scanio()` code changes its virtual time-to-ash-dump index from 0x1B to
0x1C in the same release, corroborating the table move.

## State-control values

The vendor manual describes these patterns:

| Pattern | Vendor description |
| --- | --- |
| `1x` | Shutdown/cooling |
| `2x` | Shutdown/off |
| `30` | Startup; temperature rise not detected |
| `31` | Startup; temperature rise detected |
| `4x` | Operating at heat level x+1 |
| `5x` | Ramping to heat level x+1 |
| `6x` | Ramping in ash-dump mode; ash dump pending |

## Blocked-flue monitor

The vendor algorithm watches for a rapid thermocouple drop consistent with
reduced exhaust flow. A warning can clear if temperature recovers; otherwise
the factory controller shuts down. Fuel exhaustion or an overly lean fire can
produce similar indications.

OpenMaxFire should expose BF/LB measurements and factory alarms without
reimplementing or bypassing the controller's shutdown logic. Numeric unit
conversions beyond the labels above still require code-level reconstruction or
live correlation.

The complete raw records for each release are in that release's
`data-elements.csv`.
