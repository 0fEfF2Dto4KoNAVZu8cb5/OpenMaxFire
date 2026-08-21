# Safety policy

This project interacts with a mains-powered solid-fuel appliance containing hot surfaces, moving mechanisms, igniters, fans, and combustion-safety logic. Reverse-engineering evidence is not a substitute for appliance-service training or the factory manual.

## Non-negotiable boundaries

- Disconnect mains power before opening or servicing the stove. Never operate it with the side panel removed.
- Do not connect a USB UART, ESP32, logic analyzer, or standard RS-232 adapter directly to J3 until pinout, ground reference, voltage levels, and signal polarity have been measured.
- Do not describe a software receive-only capture as electrically passive.
  Opening a PC serial device can transition DTR/RTS before any payload byte is
  sent; characterize the cable and interface with protected instrumentation
  first.
- Use current limiting, protection, and preferably galvanic isolation during initial electrical characterization.
- Do not issue undocumented writes, Checkout actuator commands, or firmware updates on a running production stove.
- Keep factory combustion control, interlocks, shutdown behavior, front-panel control, and thermostat operation intact.
- Back up all readable configuration and calibration data before any write or firmware operation.
- Treat remote ON as safety-sensitive. It must require verified stove state, fresh telemetry, command acknowledgement, and appropriate physical conditions.
- Firmware flashing can temporarily leave the stove non-functional if interrupted. Preserve a known-good image and recovery method first.

## Fail-out-of-the-way requirement

A disconnected, crashed, unpowered, or removed OpenMaxFire device must not
prevent normal factory operation. Home Assistant, Wi-Fi, Ethernet, MQTT, the
ESP32, and the cross-platform service tool are optional supervisory layers,
never required safety controllers.

Factory Checkout functions that directly drive the feed mechanism, burn/ash plates, air pump, igniters, or fans remain isolated from the normal user API.
