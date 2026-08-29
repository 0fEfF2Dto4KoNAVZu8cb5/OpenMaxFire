# Safety policy

This project interacts with a mains-powered solid-fuel appliance containing hot surfaces, moving mechanisms, igniters, fans, and combustion-safety logic. Reverse-engineering evidence is not a substitute for appliance-service training or the factory manual. The preserved [MaxFire Model 115 owner manual](preservation/original/manuals/7346103.pdf) remains the primary source for factory installation, operation, maintenance, clearances, and venting instructions.

## Non-negotiable boundaries

- Disconnect mains power and allow the stove to cool before opening, cleaning, or servicing it. Never operate it with the side panel removed.
- Operate only with the hopper door closed and the firebox door and ash drawer fully latched. The factory manual says a firebox door left open for about one minute or an ash drawer left open for about 20 minutes causes shutdown; opening the drawer also disables the ash dump and blocks startup.
- On the validated 9067-0604 controller, J3-1 is stove RX, J3-2 is stove TX, and J3-4 is ground. Leave unresolved J3-3 and adapter VCC disconnected. Do not generalize this pinout to another board revision without tracing it.
- Do not connect standard RS-232 voltage levels directly to J3. The validated bench interface used an FTDI TTL-232R-5V-WE with black/GND on J3-4, orange/adapter-TX on J3-1, yellow/adapter-RX on J3-2, and no VCC connection. The preserved photograph marked incorrect shows orange and yellow reversed; do not copy it.
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
- The original firmware-2.02 PIC is preservation media. One complete read is
  preserved; collect the remaining independent reads before clone work. Never
  Program or Erase the original, and stop if any later read reports CP/CPD as
  enabled or unknown. Clearing PIC16F877A protection requires a destructive
  chip erase. Follow the [PICkit 3 read-only procedure](docs/guides/pickit3-firmware-preservation.md).

## Firmware-flashing boundary

The experimental guarded J3 executor does not make physical flashing proven.
Before its live gate can be satisfied, PICkit recovery must have been programmed,
read back, authenticated, and exercised on a spare PIC/controller. Do not assert
that merely owning a PICkit, spare chip, or known-good file proves recovery.

For any J3 firmware session, the stove must be cold and OFF and both igniters
must be physically unplugged. Use only the validated 5 V TTL ground/TX/RX
wiring; keep J3-3 and adapter VCC disconnected. Entry is by manual AC power
cycle. Keep AC, J3, and the host stable until the tool finishes. The flasher
must first preserve an authenticated exact-image rescue bundle and pass a
non-writing `EA/EB`, `ED/E4` rehearsal with no `E3` frames. It retains one
exclusive serial handle and must acquire the platform sleep inhibitor before
the destructive window.

Once any `E3` may have been sent, a failure is a recovery event, not permission
to operate the stove or choose another image. Preserve the failed session and
replay its authenticated image from block zero. One `E5` receives one bounded
identical retry and triggers a hardware-inspection gate even if programming
finishes; a second `E5` anywhere aborts. The durable recovery marker is removed
only after repeated target identity and byte-identical EEPROM verification.
Recovery is one-way: a newer self-contained recovery session atomically takes
responsibility from its source, and an older or completed session cannot be
replayed as a shortcut around compatibility rules.

The resident loader always uses 9,600 baud. A target 2.70/2.71 application uses
19,200 only after handoff. Do not reconnect igniters or operate the stove after
a data-format migration until the vendor calibration/Format procedure is
complete. See the [guarded flashing guide](docs/guides/safe-j3-firmware-flashing.md)
and the mandatory
[sacrificial-hardware qualification plan](docs/guides/j3-flasher-qualification.md).

## Fail-out-of-the-way requirement

A disconnected, crashed, unpowered, or removed OpenMaxFire device must not
prevent normal factory operation. Home Assistant, Wi-Fi, Ethernet, MQTT, the
ESP32, and the cross-platform service tool are optional supervisory layers,
never required safety controllers.

Factory Checkout functions that directly drive the feed mechanism, burn/ash plates, air pump, igniters, or fans remain isolated from the normal user API.
