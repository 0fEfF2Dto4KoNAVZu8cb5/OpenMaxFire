# Bixby MaxFire 110/115 common problems and first checks

This is a symptom-based troubleshooting guide for Bixby MaxFire owners. It combines the factory Model 115 owner manual with findings that OpenMaxFire has verified in the controller firmware and on a live stove.

It is meant to help an owner gather useful information and perform conservative first checks. It is not permission to bypass a safety device or work on an energized mains-voltage board.

## Start here

1. **Record the symptoms before resetting anything.** Photograph the control panel and note the exact flashing lights.
2. **Stop for unsafe conditions.** If smoke is entering the room, the hopper or stove is overheating, an electrical smell is present, or fire is outside the normal burn area, press **Off** if safe, ventilate, and discontinue use.
3. **Let it cool and unplug it** before opening panels, touching connectors, clearing fuel, cleaning the fan, or working around a motor.
4. **Clean before adjusting.** Many apparent control problems are caused by ash, fines, a dirty burn pot, a restricted exhaust path, or blocked venting.
5. **Change one thing at a time.** If a trim adjustment is actually called for, move only one setting by one notch and observe before changing it again.

For the meaning of a numbered warning, use the [fault-light guide](fault-lights.md).

## The stove has no response when plugged in

- Confirm the outlet has proper power and the breaker has not tripped.
- Use the grounded power cord directly as specified by the factory manual, not an extension cord.
- Inspect the cord and plug for damage.
- With the stove unplugged, a qualified person can check the circuit-board fuse and related connections. Do not replace a fuse with a larger value or bypass it.
- If the replacement fuse immediately opens again, stop. A short circuit must be found before further use.

## No fuel reaches the burn pot

- Confirm there is usable fuel in the hopper.
- Look for bridging, compacted fines, or a blockage in the feeder tube.
- Observe whether the feeder wheel turns, without putting hands or tools near the mechanism.
- Check for flashing light 8.
- If the feeder wheel is jammed, let the stove cool, unplug it, and clear the obstruction from the access area described in the factory manual.
- If the wheel moves but light 8 remains, inspect the feeder-feedback sensor and wiring at J9.

## Fuel arrives, but the fire does not start

The factory manual says fuel should cover the bottom of the burn pot to roughly 1/2 inch during a start attempt.

Check:

- Built-up ash or deposits at the bottom of the burn pot
- Blocked burn-pot and lower-paddle air holes
- Flashing light 6, indicating an exhaust-fan or feedback problem
- Igniter fault lights and the igniter fuses
- Air-pump operation during startup; the pump should produce noticeable vibration
- Whether the stove and venting need cleaning

A very cold stove can sometimes require a second start, according to the factory manual. However, do **not** keep restarting if raw fuel is accumulating. Shut down, allow the stove to cool, and remove the excess fuel safely before another attempt.

## The fire starts, then shuts down after about 12 minutes

This commonly points toward the controller not seeing enough heat or losing fuel delivery.

- Check that fuel continues down the feeder chute.
- Check for light 2.
- Inspect the two-wire exhaust thermocouple connection at **J18**, on the upper-right area of the main board. The factory manual specifically calls out a disconnected thermocouple for this symptom.
- Inspect the thermocouple lead for damage and make sure its connector has not been loosened during service.
- Clean the burn pot, exhaust path, heat exchanger, and venting.
- If fuel delivery stops at nearly the same time on every attempt, the feeder control or electronics may need diagnosis.

Do not replace the thermocouple solely because someone on a forum had a similar symptom. Confirm the connector, wiring, and signal first.

## Light 6 appears even though the exhaust fan spins

The controller is not satisfied merely by visible fan motion. Firmware 2.02,
2.06, 2.70, and 2.71 count speed-sensor pulses associated with **J10**. A
spinning fan can still produce light 6 if the sensor signal is absent or too
slow.

With the stove cool and unplugged, inspect:

- J10 and the exhaust-sensor wiring
- Sensor placement and alignment near the rotating target
- A dirty impeller or fan that turns slowly
- Damaged wires or loose terminals
- Exhaust and vent restrictions
- The sensor and the board's feedback-input circuit

BixCheck can help observe the raw feedback value, but there is no known safe software option that turns this protection off. See the [fault-light guide](fault-lights.md) and [BixCheck checkout tests](../bixcheck/checkout-tests.md).

## Light 4 or 5 will not clear

- Light 4 is the firebox-door input.
- Light 5 is the ash-drawer input.

Close and latch the affected part firmly. If the light stays on, inspect mechanical alignment, switch engagement, the connector, and wiring. OpenMaxFire has physically confirmed these two input mappings on a firmware-2.02 controller.

Do not jumper the switch to make the light disappear. The door and drawer inputs alter safety behavior, ash-dump operation, and shutdown timing.

## Dark yellow or lazy flame, slow startup, or excessive smoke

Clean first:

- Burn pot and its air holes
- Lower-paddle holes
- Heat-exchanger passages
- Exhaust manifold and fan impeller
- Attached venting and outside termination
- Rear room-air filter

Also check that the heat-exchanger cover plates and burn-pot parts are installed and aligned correctly.

If the stove is clean and mechanically correct, the factory chart suggests increasing exhaust-fan trim or reducing fuel trim by **one notch**, then observing. Avoid making several changes at once; the original settings are otherwise difficult to recover.

If smoke from the louvers or hopper is excessive immediately, or does not clear within about 15 minutes of startup, shut the stove down and ventilate the area.

## Flame repeatedly grows and shrinks

- Confirm the front door and ash drawer are fully latched.
- Check for interrupted fuel delivery, bridging, or excessive fines.
- If the stove is clean and fuel delivery is consistent, the factory manual suggests the feed rate may be low. Increase fuel trim by one notch and observe.
- Do not use trim settings to hide a dirty vent, failing sensor, air leak, or mechanical fault.

## Burn pot fills with fuel, glass soils rapidly, or ash volume is excessive

- Clean the burn pot, exhaust system, heat exchanger, and venting.
- Confirm the stove is level.
- Check burn-pot alignment and heat-exchanger cover-plate installation.
- Watch whether fuel is arriving faster than it burns.
- Once cleaning and mechanical checks are complete, the factory chart suggests increasing fan trim or reducing fuel trim by one notch and observing.

Repeated overfilling is not a reason to keep restarting. Accumulated fuel can ignite all at once.

## Ash dump or burn-pot mechanism jams

- Let the stove cool and unplug it.
- Remove clinker, hardened deposits, and loose material obstructing the burn-pot or lower-paddle movement.
- Clean the lower-paddle holes.
- Inspect alignment, linkage, the burner drive, and limit-switch area.
- Confirm the ash drawer is fully inserted and latched; opening it disables the dump process.
- Do not force the mechanism while it is powered.

Light 7 is the factory fire-pot mechanical-malfunction indication.

## Fans continue running after Off

This is usually normal. The factory manual says the convection blower and exhaust fan continue to run for approximately **30 minutes** while the stove cools. The exhaust fan may also run for roughly 30 minutes when the stove is first plugged in to clear possible combustion gases after a power interruption.

Firmware 2.06 is now measured more precisely: its exact CCP1/Timer1 setup and
cooldown threshold produce about **14 minutes 38 seconds** at the controller's
10 MHz clock. A live power-up capture matched that interval and showed the fan
command, target, and measured speed all return to zero as the state changed to
Off. The manual's 30-minute statement should still be treated as the general
cross-version/operator expectation.

Investigate if the fans never stop, run abnormally, or are accompanied by a fault light or overheating.

## Thermostat behavior seems wrong

On the Rev. A MaxFire arrangement documented by the factory:

- The thermostat does not start a stove that is fully off.
- When calling for heat, the stove operates at the selected level.
- When not calling for heat, it drops to level 1 and the level lights blink.

Later software and configuration options may behave differently, so include the firmware version when asking for help.

## A new fault appeared immediately after cleaning or repair

Start with whatever was touched. Recheck connectors, pinched wires, and mechanical alignment before buying parts. Especially note:

- **J9:** feeder-wheel sensor
- **J10:** exhaust-fan speed sensor
- **J18:** exhaust thermocouple
- Firebox-door and ash-drawer switches
- Burn-pot parts, lower paddle, and heat-exchanger cover plates

Photographs taken before disconnecting anything are often more useful than wire colors alone.

## BixCheck will not connect

Do not connect USB-adapter VCC to the stove. Use the verified J3 signal wiring and a proper mating connector. The [J3 working specification](../protocol/j3-protocol.md) documents the pinout, adapter requirements, and connection precautions.

A communications problem and a stove fault are separate diagnoses. Do not update firmware merely because BixCheck cannot connect.

## Before ordering a substitute part

Old forum posts provide valuable leads, but a similar-looking part is not automatically compatible. Verify the original part number and all relevant electrical and mechanical details, including voltage, current, speed, rotation, capacitor, sensor, mounting, temperature rating, and connector pinout.

OpenMaxFire records community repair claims as leads until they are supported by a factory document, part marking, measurement, firmware evidence, or a repeatable test.

## A good forum help request

Include:

- Model and serial number
- Firmware and BixCheck version, if known
- Exact flashing lights
- Startup, running, ash-dump, or shutdown phase
- Fuel type and recent fuel change
- What moves, spins, feeds, heats, or vibrates
- Cleaning already performed
- Recent repairs or connectors disturbed
- Clear photos and any BixCheck readings

Avoid saying only that the stove “doesn't work.” The exact sequence usually narrows the problem much faster.

## Sources and further reading

- [Factory MaxFire Model 115 owner manual](../../preservation/original/manuals/7346103.pdf)
- [Fault-light guide](fault-lights.md)
- [MaxFire owner-manual analysis](../manuals/maxfire-owner-manual-2020866-rev-a.md)
- [Fault and flashing-indicator protocol](../protocol/faults.md)
- [BixCheck checkout tests](../bixcheck/checkout-tests.md)
- [J3 working specification](../protocol/j3-protocol.md)

OpenMaxFire is preserving the remaining Bixby software, firmware, manuals, and repair knowledge at [OpenMaxFire.com](https://openmaxfire.com). If you have **firmware 2.73**, an old BixCheck package, a service CD, or documentation that is not already archived, please contact the project.
