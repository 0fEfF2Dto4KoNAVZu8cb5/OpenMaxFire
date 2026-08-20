# Architecture

OpenMaxFire has two related products with deliberately different scopes.

## Linux service tool

The Linux CLI/application is the eventual BixCheck replacement. Its long-term scope includes serial communication, stove identification, telemetry, remote control, fuel/hardware configuration, calibration, blocked-flue and lean-burn monitoring, thermostat/auto-restart settings, trim-pot modes, configuration readback/write/format, logging, factory Checkout, debug tools, firmware identification, bootloader communication, firmware flashing, and post-flash calibration.

Dangerous service functions must remain visibly separated from normal monitoring and control.

## Permanent ESP32/ESPHome controller

The permanent appliance-adjacent controller gets only the reliable everyday subset:

- read-only telemetry and faults
- current and target heat level
- start, stop, up, and down
- command acknowledgement and state verification
- Home Assistant entities

It does not replace BixCheck's calibration, Checkout, raw-write, memory-format, or firmware-flash functions.

## Failure model

The factory stove controller owns combustion and appliance safety. OpenMaxFire observes and requests actions.

- Loss of Home Assistant must not disable the stove.
- Loss of Wi-Fi, MQTT, or Ethernet must not disable the stove.
- Loss or removal of the ESP32 must not disable the front panel or factory thermostat.
- A stale or ambiguous connection must block new remote commands.
- A transmitted command is not successful until the resulting stove state is read back.
- Firmware/configuration writes are never part of ordinary automation.

For whole-house coordination, the pellet stove and backup heat source retain independent thermostat behavior. If automation disappears, both may temporarily call for heat, but neither is made dependent on the other for basic operation.
