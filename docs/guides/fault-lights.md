# Bixby MaxFire 110/115 fault-light guide

This page is a plain-language reference for the eight numbered lights on the Bixby MaxFire control panel. It is based primarily on the factory MaxFire Model 115 owner manual, with added notes from OpenMaxFire's firmware analysis and live controller testing.

## Before doing anything

- Write down the **exact light or combination of lights** before resetting the stove.
- If smoke is entering the room, the stove or hopper is unusually hot, you smell overheated wiring, or a mechanism is repeatedly jamming, press **Off** if it is safe to do so, ventilate the room, and stop using the stove until the cause is found.
- Let the stove finish its shutdown and cool completely. Unplug it before opening panels, clearing a jam, touching wiring, or removing a cover.
- Never bypass the door switch, ash-drawer switch, hopper-temperature switch, or another safety device.
- Do not repeatedly restart a failed ignition while unburned fuel is accumulating in the pot.

## Quick fault-light chart

| Flashing light(s) | Factory meaning | Safe first checks |
| --- | --- | --- |
| **1** | Power interruption during operation | Press **Off**, then **On** to restart. If it keeps returning, investigate the outlet, plug, cord, breaker, and unstable power. |
| **2** | Operating temperature was not reached | Check the hopper and fuel delivery, clean the burn pot, confirm ignition and the air pump, and inspect the exhaust thermocouple connection. |
| **3** | Exhaust system or hopper area overheating | Reduce the feed rate only if the stove is otherwise operating safely. Inspect for overfiring, restricted airflow, ash buildup, and blocked venting. Stop using the stove if overheating continues. |
| **2 and 3** | Empty hopper or possible blocked flue | Check for fuel and fuel bridging. If fuel is present, clean the stove's exhaust path and attached venting before another run. |
| **4** | Firebox door open | Close and latch the door tightly. If the light remains, inspect the latch, switch engagement, connector, and wiring. The stove shuts down after the door has been open for about one minute. |
| **5** | Ash drawer open | Fully insert and latch the drawer. If the light remains, inspect the latch, switch engagement, connector, and wiring. The stove will not start with the drawer open and shuts down if it remains open for about 20 minutes. |
| **6** | Exhaust-fan failure | Do not assume the fan is okay merely because it is spinning. Check the fan, its speed-feedback sensor and J10 connection, wiring, sensor position, and exhaust obstruction. See the detailed note below. |
| **7** | Fire-pot mechanical malfunction | After the stove is cool and unplugged, inspect the burn pot, lower paddle, drive, linkage, and limit-switch area for ash, clinker, misalignment, or a jam. |
| **7 and 1** | Left igniter failed | The stove may continue to operate but can take longer to light from cold. Inspect the igniter circuit only with the stove unplugged. |
| **7 and 2** | Right igniter failed | Same checks as the left igniter. |
| **7, 1, and 2** | Both igniters failed | Automatic starting is unavailable. Repair the ignition system before relying on normal startup. |
| **7, 1, 2, and 3** | Internal fault, possibly igniter electrical | Unplug the stove and have the electrical fault diagnosed before further operation. |
| **8** | Feeder-wheel failure | Once cool and unplugged, inspect the hopper/feed-wheel area for foreign material, compacted fines, bridging, or a jam. Check the J9 feeder sensor and wiring if the wheel moves but the fault remains. |

## Light 6 when the exhaust fan is visibly spinning

Light 6 does not necessarily mean that the fan motor is completely stopped. The controller also expects feedback pulses from the exhaust-fan speed sensor.

OpenMaxFire has confirmed in firmware **2.02, 2.06, 2.70, and 2.71** that the controller counts exhaust-sensor pulses associated with **J10**. If the count remains too low, the firmware can report an exhaust-fan failure even while the impeller appears to turn.

With the stove cool and unplugged, check:

1. The J10 exhaust-sensor plug is seated correctly.
2. The sensor wires, including the black lead mentioned in older service discussions, are intact and firmly terminated.
3. The sensor is positioned close enough to detect the rotating target but does not touch the blades.
4. The impeller is clean and rotates freely.
5. The exhaust path and vent are not restricted.
6. The fan reaches normal speed rather than merely turning slowly.

Possible causes include the fan itself, the speed sensor, its target or alignment, a connector, damaged wiring, or the board's sensor-input circuit. There is no known BixCheck setting that safely disables or adjusts this protection. A software change is not the normal fix for a missing feedback signal.

The exact J10 firmware path is now statically verified in 2.02, but physical J10 pulse testing on the installed controller remains outstanding.

## Light 8 when the feeder wheel is visibly moving

The controller also watches feeder-wheel feedback. The factory wiring identifies the feeder sensor at **J9**, and OpenMaxFire has traced that input in firmware 2.02, 2.06, 2.70, and 2.71. Firmware 2.02 scales its raw interval differently, but the diagnostic role is the same.

If the wheel moves but light 8 appears, check for intermittent movement, debris, a loose or damaged sensor connection, sensor alignment, motor-mount movement, and wiring back to J9. Never put a hand or tool into the feeder mechanism while the stove is connected to power.

## Lights 2 and 3 are not the same fault

- **Light 2 alone** means the controller did not see the expected operating temperature. The fire may have failed to light, fuel may not be feeding, the exhaust thermocouple may be disconnected, or the stove may be losing the fire.
- **Lights 2 and 3 together** mean empty hopper or possible blocked flue. Fuel in the hopper does not rule out bridging or a blocked feed tube. If fuel delivery looks normal, treat the exhaust path and vent as the next priority.
- **Light 3 alone** is an overheating warning and should not be treated as a simple failed-start code.

## Normal blinking that can be mistaken for a fault

On the Rev. A MaxFire thermostat arrangement, the heat-level lights blink when the thermostat is not calling for heat and the stove drops to level 1. That is normal thermostat behavior, not automatically a fault. A useful forum report should identify exactly which numbered lights flash and when they begin flashing.

It is also normal for the convection blower and exhaust fan to continue running
during cooldown. The manual gives a general figure of roughly 30 minutes; exact
firmware 2.06 code and a matching live capture establish about 14 minutes 38
seconds for its power-up cooldown.

## What to include when asking for help

- MaxFire 110 or 115, if known
- Stove serial number
- Firmware version and BixCheck version, if known
- Exact flashing light or combination
- Whether it happens during startup, normal running, ash dump, or shutdown
- Whether the fan, feeder, igniters, air pump, and burn-pot drive actually move or operate
- Fuel type and whether the stove was recently cleaned or repaired
- Clear photographs of any connector or part that was disturbed

## Sources and confidence

The fault meanings and basic remedies above are **factory documented** in the preserved [MaxFire Model 115 owner manual](../../preservation/original/manuals/7346103.pdf). The J9/J10 signal explanations are **project supported** by the factory wiring diagram and static analysis of firmware 2.02, 2.06, 2.70, and 2.71. A bounded firmware-2.02 start physically correlated the running blower with J10's CR05 path and produced partial J9 changes; J9 polarity, timing units, and a complete wheel-cycle test remain outstanding.

For the detailed technical evidence, see:

- [Fault and flashing-indicator protocol](../protocol/faults.md)
- [BixCheck checkout tests and raw sensor thresholds](../bixcheck/checkout-tests.md)
- [MaxFire owner-manual analysis](../manuals/maxfire-owner-manual-2020866-rev-a.md)

OpenMaxFire is preserving the remaining Bixby software, firmware, manuals, and repair knowledge at [OpenMaxFire.com](https://openmaxfire.com). We are still looking for a surviving copy of **firmware 2.73** and any unlisted Bixby service material.
