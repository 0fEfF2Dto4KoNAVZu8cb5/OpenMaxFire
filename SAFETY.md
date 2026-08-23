# Safety policy

This project interacts with a mains-powered solid-fuel appliance containing hot surfaces, moving mechanisms, igniters, fans, and combustion-safety logic. Reverse-engineering evidence is not a substitute for appliance-service training or the factory manual. The preserved [MaxFire Model 115 owner manual](preservation/original/manuals/7346103.pdf) remains the primary source for factory installation, operation, maintenance, clearances, and venting instructions.

## Non-negotiable boundaries

- Disconnect mains power and allow the stove to cool before opening, cleaning, or servicing it. Never operate it with the side panel removed.
- Operate only with the hopper door closed and the firebox door and ash drawer fully latched. The factory manual says a firebox door left open for about one minute or an ash drawer left open for about 20 minutes causes shutdown; opening the drawer also disables the ash dump and blocks startup.
- J3-1/stove TX, J3-2/stove RX, and J3-4/ground are established only for the photographed 9067-0604 controller. Leave unresolved J3-3 and adapter VCC disconnected. Do not generalize this pinout to another board revision without tracing it.
- Do not connect standard RS-232 voltage levels directly to J3. The validated bench interface used an FTDI TTL-232R-5V-WE with black/orange/yellow for ground/adapter-TX/adapter-RX and no VCC connection.
- Do not describe a software receive-only capture as electrically passive.
  Opening a PC serial device can transition DTR/RTS before any payload byte is
  sent; characterize an unfamiliar cable and interface with protected
  instrumentation first.
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
