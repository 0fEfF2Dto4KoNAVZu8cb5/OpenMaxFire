# System design

## Linux service application

The Linux OpenMaxFire application is the comprehensive service/engineering tool. It may expose diagnostics, calibration, factory checkout, raw protocol access, and firmware service functions with appropriate safeguards.

## ESP32 / ESPHome controller

The permanent controller is deliberately narrower:

- telemetry
- faults/status
- start/stop
- heat-level control
- command verification
- Home Assistant entities

It should avoid exposing arbitrary write registers and firmware-service operations as everyday Home Assistant controls.

## Home Assistant integration philosophy

Home Assistant coordinates comfort and fuel-source logic, but the stove retains its own thermostat/safety behavior. Loss of Home Assistant should not make heating impossible. Smart control should fail toward independent local operation, not toward dependence on the network.
