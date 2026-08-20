# Project overview

## Why OpenMaxFire exists

Bixby MaxFire stoves have unusually capable controller electronics and service software, but the original ecosystem is aging and difficult to obtain. OpenMaxFire aims to preserve that knowledge and make the stoves maintainable with modern, open tooling.

## Workstreams

### 1. Preservation

Archive original firmware, BixCheck executables/packages, manuals, service documentation, cable/interface information, and checksums. Keep untouched copies distinct from derived artifacts.

### 2. Linux BixCheck replacement

The Linux application should ultimately aim for functional parity with the useful BixCheck service workflows: serial communication, stove identification, telemetry, control, calibration, configuration read/write, checkout testing, debugging, firmware identification/loading/flashing, post-flash calibration, logging, and documentation.

### 3. Permanent smart-home controller

The ESP32/ESPHome side should intentionally remain smaller and safer than the service tool. Its everyday scope is telemetry, faults, start/stop, heat-level control, command verification, and Home Assistant exposure. It should not casually expose dangerous factory/service functions.

### 4. Reverse engineering

Firmware and software analysis is used to discover protocol semantics, register meanings, undocumented sensors, safety interlocks, and firmware-update behavior.

## Architectural principle

The stove must remain capable of operating independently of Home Assistant. Smart-home automation should layer on top of the stove's own control and safety mechanisms rather than replacing them.
