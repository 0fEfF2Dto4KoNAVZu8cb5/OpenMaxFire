# BixCheck feature-parity target

The Linux OpenMaxFire application is intended to replace essentially all documented and discovered BixCheck behavior. The permanent ESP32 controller has a much smaller scope; see [architecture](../ARCHITECTURE.md).

## Connection and identity

- Enumerate and open PC serial ports.
- Select the stove family/version and validate communications.
- Read stove software version, database/data-format version, internal checksum, serial number, production date, and model name.
- Provide raw request/response capture and replay for research.
- Recover cleanly from stale or partial frames.

## Monitor and normal control

- Live current/target heat level and operating state.
- Remote OFF, ON, UP, and DOWN with read-after-write verification.
- Ambient/control-board temperature and exhaust thermocouple value.
- Exhaust-fan measured/target values and phase control value.
- Convection-fan level, igniter state/current, panel LEDs, alarms, flags, IIC status, feed timing, ash values, and door/drawer timers.
- Blocked-flue warning/detected/shutdown state and history.
- Lean-burn/low-temperature indicators where exposed.
- Thermostat, fuel-selection switch, front-panel switches, and trim-pot modes/readings.

## Configuration and calibration

- Complete configuration/EEPROM readback.
- Save, compare, restore, and print durable backups.
- Read and write individual calibration values.
- Fuel A and Fuel B calculations for model, altitude, fuel, fan curve, and feed-wheel selections.
- Fan, feed, ash, startup, igniter, ash-dump, and convection-fan calibration.
- Serial-number, production-date, model-name, checksum, and data-format handling.
- Full configuration format/individualization workflow with version guards and verification.
- Calibration wizard and post-firmware-update recalibration.

## Logging and diagnosis

- Selectable telemetry fields.
- Start, hold, resume, and stop logs.
- Stable CSV and JSON formats with timestamps, identity, units, and raw values.
- Long-term logging and graphs without requiring proprietary software.
- Capture files suitable for offline parser tests.

## Factory Checkout

- All 45 documented interactive/automatic tests.
- Operator identity, test timing, pass/fail/not-performed result, diagnostic hints, and complete report.
- Direct tests for front panel, LEDs, door and ash-drawer switches, plate drive, air pump, convection and exhaust fans, igniters, feed motor/sensor, thermocouple, thermometer, thermostat, fuel switch, and trim pots.
- Safety isolation between Checkout actuator control and the ordinary API.

## Firmware servicing

- Identify installed firmware and expected database format.
- Load embedded or external firmware.
- Communicate with the stove downloader/bootloader.
- Flash firmware with progress, retry/recovery, and compatibility checks.
- Support the distinction between `_Downloader.hex` and PICkit-programmer images.
- Verify the result and guide post-flash calibration.

## Help and preservation

- Contextual help for every service operation.
- Versioned protocol/register documentation.
- Preserve original vendor files, hashes, provenance, disassembly, derived work, and modified firmware separately.
