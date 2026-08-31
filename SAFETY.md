# Safety policy

This project interacts with a mains-powered solid-fuel appliance containing hot surfaces, moving mechanisms, igniters, fans, and combustion-safety logic. Reverse-engineering evidence is not a substitute for appliance-service training or the factory manual. The preserved [MaxFire Model 115 owner manual](preservation/original/manuals/7346103.pdf) remains the primary source for factory installation, operation, maintenance, clearances, and venting instructions.

## Non-negotiable boundaries

- Disconnect mains power and allow the stove to cool before opening, cleaning, or servicing it. Never operate it with the side panel removed.
- Operate only with the hopper door closed and the firebox door and ash drawer fully latched. The factory manual says a firebox door left open for about one minute or an ash drawer left open for about 20 minutes causes shutdown; opening the drawer also disables the ash dump and blocks startup.
- On the validated 9067-0604 controller, J3-1 is stove RX, J3-2 is stove TX,
  and J3-4 is ground. Owner-reported unpowered tracing places J3-3 on the PIC
  VDD/logic-supply net through approximately 100 ohms, supporting nominal +5 V,
  but the powered voltage and available current remain unverified. Leave J3-3
  and adapter VCC disconnected. Any attached identification lead must have its
  free end individually insulated. Do not generalize this pinout to another
  board revision without tracing it.
- Do not connect standard RS-232 voltage levels directly to J3. Historical
  functional UART tests used an FTDI TTL-232R-5V-WE with black/GND on J3-4,
  orange/adapter-TX on J3-1, yellow/adapter-RX on J3-2, and no VCC connection.
  That establishes pin direction, logic family, and baud behavior when
  communication succeeds; it does not establish a safe electrical reference,
  isolation, or partial-power behavior. The preserved photograph marked
  incorrect shows orange and yellow reversed; do not copy it.
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
- The original firmware-2.02 PIC is preservation media. Its sole pre-write
  complete read is preserved; the chip was subsequently programmed once during
  the 2026-08-30 emergency restore, so later reads cannot retroactively become
  independent pre-write captures. Do not Program or Erase it again absent
  an explicit recovery need, and stop if any read reports CP/CPD as enabled or
  unknown. Clearing PIC16F877A protection requires a destructive chip erase.
  Follow the [PICkit 3 preservation boundary](docs/guides/pickit3-firmware-preservation.md).

## Firmware-flashing boundary

All physical J3 loader traffic is unavailable in the current release. The CLI
allows only offline `flash --plan-only`; public rehearsal, programming, and
recovery executors reject physical transports before the first loader byte.
The generic raw/register paths also reject known loader bytes and the `CW0FC4`
entry request. There is no confirmation flag or session-replay option that
bypasses these locks.

The bare-FTDI/manual-AC/BREAK method is retired for writes because loader entry
was nondeterministic at the power boundary, and it is now retired for physical
rehearsal as well because the shared electrical reference and partial-power
behavior remain unqualified. Historical zero-write sessions remain useful
protocol evidence, but the current software provides no physical loader path.
Future zero-write qualification must use a reviewed fixture on safely powered
spare hardware.

If a historical session may have sent an `E3`, preserve it and keep the stove
out of operation until the whole chip is verified or restored through the
[external-programmer recovery procedure](docs/guides/pickit3-emergency-recovery.md).
Historical
`RECOVERY_REQUIRED.txt` instructions that mention `--recover-from-session` are
preserved evidence but are superseded; the current J3 replay path is locked.
The 2026-08-30 original-controller restore produced a normal boot and matching
J3 identity/EEPROM, but it lacked a saved post-program whole-chip readback and
was not exercised on a spare; it is an observed one-time recovery, not a
qualified process. Do not assert that merely owning a PICkit, spare chip, or
known-good file proves recovery: authenticate the image, program it, read the
whole chip back, and exercise it on a spare PIC/controller first.

Any future physical executor requires a target-power-safe UART interface and
deterministic hardware-reset fixture, followed by the complete multi-specimen,
cross-host, forced-interruption qualification plan. Preliminary 100/100
zero-write entries and one spare-target update admit a fixture only to that
qualification; they do not authorize a production-stove write.

The resident loader always uses 9,600 baud. A target 2.70/2.71 application uses
19,200 only after handoff. Do not reconnect igniters or operate the stove after
a data-format migration until the vendor calibration/Format procedure is
complete. See the [guarded flashing guide](docs/guides/safe-j3-firmware-flashing.md),
the [fixture requirements](docs/hardware/j3-loader-entry-fixture.md), and the mandatory
[sacrificial-hardware qualification plan](docs/guides/j3-flasher-qualification.md).

## Fail-out-of-the-way requirement

A disconnected, crashed, unpowered, or removed OpenMaxFire device must not
prevent normal factory operation. Home Assistant, Wi-Fi, Ethernet, MQTT, the
ESP32, and the cross-platform service tool are optional supervisory layers,
never required safety controllers.

Factory Checkout functions that directly drive the feed mechanism, burn/ash plates, air pump, igniters, or fans remain isolated from the normal user API.
