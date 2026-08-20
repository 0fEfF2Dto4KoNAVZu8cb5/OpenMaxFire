# Vendor-documented telemetry fields

The BixCheck 5.x manual documents the values visible to its Monitor. The protocol address or stream field for each value is not yet mapped.

## Runtime values

| Field | Vendor meaning |
| --- | --- |
| Temperature | Ambient air temperature measured on the control board |
| Thermocouple | Exhaust temperature; manual says no calibrated units |
| Fan potentiometer | Raw 0-255 reading used for roughly +/-30% exhaust-fan adjustment |
| Feed potentiometer | Raw 0-255 reading used for roughly +/-30% feed-rate adjustment |
| Exhaust fan speed | Measured fan speed, 0-3600 RPM |
| Exhaust fan phase | Internal fan-control parameter, 0-255 |
| Convection fan level | Commanded power, 0-100% |
| Display LED | Graphical front-panel LED state |
| Igniter state | Internal igniter status byte |
| Current heat level | Current level 1-8 |
| Target heat level | Front-panel target 1-8 |
| State control | Operating-state byte |
| Ash level | Current 16-bit ash counter |
| Ash target | 16-bit ash-dump threshold |
| Feed on/off/cycle time | 16-bit values in 1/120-second units |
| IIC status | Serial-memory status byte |
| Alarm status | Internal alarm byte |
| Flag status | Internal flag byte |
| Igniter current | Instantaneous raw current reading |
| Firedoor timer | Door-open time in 1/3-second units |
| Ash drawer timer | Drawer-open time in 5 1/3-second units |
| Exhaust fan target | Target fan speed, 0-3600 RPM |
| Drop limit | Allowed thermocouple drop before blocked-flue handling |
| Feed cycle table | Base 16-bit feed-cycle value |
| Feed cycle calibration | Adjusted 16-bit feed-cycle value |
| Time to ash dump | Approximate hours:minutes |

## State-control values

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

BixCheck exposes warning, detected, shutdown, warning count, overtemperature pullback, history index/maximum, sample timer, ramp/adjustment values, reset countdown, current/target level, low-temperature timer, and two eight-entry temperature-history tables.

The vendor algorithm watches for a rapid thermocouple drop consistent with reduced exhaust airflow. A warning can clear if temperature recovers; otherwise the stove performs a blocked-flue shutdown. Running out of fuel or an overly lean fire can produce similar #2/#3 indications.

OpenMaxFire must expose these values without reimplementing or bypassing the factory shutdown logic.
