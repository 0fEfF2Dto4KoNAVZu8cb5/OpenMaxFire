# Design requirements

Status: Rev A design input. Requirements marked `GATE` block release until they
are physically verified.

## Product scope

The full controller shall provide every electrical service function planned for
the later portable cable, while also providing permanent ESP32 operation,
fail-safe thermostat transfer, local sensing, and protected expansion.

The board shall:

- communicate with the factory controller through J3 at validated 5 V TTL,
  non-inverted, 9,600 baud, 8N1 for firmware 2.02 and the resident loader;
- expose an independent FTDI TTL-232R-compatible service connection;
- provide deterministic, isolated open-collector MCLR assertion for J3 loader
  entry, guarded by a physical arm control;
- expose direct PICkit-compatible J5 pins 1 through 5 and leave PICkit AUX/PGM
  unconnected;
- include an ESP32-S3 with native USB and an external-antenna connector;
- transfer the stove thermostat input between OpenMaxFire control and the
  original physical thermostat using a non-latching break-before-make relay;
- include a hardware liveness/dead-man gate independent of ESP software;
- retain useful local control when Home Assistant and all networks are absent;
- expose protected, non-strapping GPIO for future sensors and accessories;
- fit a serviceable enclosure and use keyed connectors for field wiring; and
- use a 140 mm x 100 mm, four-layer Rev A engineering outline, subject to final
  enclosure and fabrication review.

## Non-negotiable safety behavior

The factory stove controller owns all combustion and appliance safety. The
OpenMaxFire controller is supervisory.

`COIL_ENABLE` shall be true only when all of the following are true:

```text
NORMAL_MODE AND HEARTBEAT_OK AND RELAY_REQUEST
```

Loss of any term shall de-energize the relay without software intervention.
The de-energized relay state shall reconnect the physical thermostat.

The watchdog and healthy latch shall recognize the same qualified heartbeat
event. In Rev A, an ESP heartbeat falling edge services U501 while U504 turns
that same edge into the rising clock that arms U503. A 100 kohm hardware pull-
down defines the reset/processor-absent state. The specified 22 nF, +/-5% C0G
timing capacitor yields a 1.758 s nominal watchdog interval and an estimated
1.51-2.02 s worst-case interval including capacitor and TPS3851 tolerances;
assembled hardware must establish the released limits.

The relay shall remain de-energized during boot, reset, brownout, missing
heartbeat, stale J3 data, invalid local temperature, FTDI service, PICkit
service, and controller power loss. Returning the mode selector to NORMAL shall
not energize it until a new heartbeat qualification and relay request occur.

No J3 or J5 output may raise target VDD when the target is unpowered. The J3 RX
drive into the stove shall be high impedance whenever target VDD is absent.

Service features shall not rely on the ESP32 being installed, bootable, or
programmed. PICkit access shall remain a short direct path without LEDs, clamps,
or default series resistors on MCLR/VPP, PGD, or PGC.

## Required physical modes

| Mode | J3 owner | J3 reset | Thermostat | J5/PICkit |
| --- | --- | --- | --- | --- |
| NORMAL | ESP32 | disarmed | eligible after health qualification | no programmer attached |
| FTDI SERVICE | external FTDI | separately armed | physical backup | disconnected from active drive |
| PICkit/OFFLINE | none; UART physically/electronically high-Z | service fixture only | physical backup | direct pins 1-5 |

An invalid, open, or unpowered selector state shall behave as PICkit/OFFLINE,
not NORMAL.

## Power and grounding

- Permanent board power shall enter through a fuse, a non-sacrificial series
  reverse-polarity barrier, and a transient-protected nominal 12 V input
  intended for a certified external
  supply. Normal operation is specified over 10.8-13.2 V; qualification extends
  to 15 V. This is not a general-purpose 18 V input.
- The design shall provide at least 1 A peak at 3.3 V for ESP32 radio bursts and
  at least 100 mA at 5 V beyond the relay coil and housekeeping load.
- USB VBUS shall not be paralleled with the permanent 5 V rail in Rev A.
- USB VBUS shall reach only a high-impedance MOSFET gate monitor. The ESP input
  is `USB_VBUS_PRESENT_N`: low means present, high means absent, and the signal
  is meaningful only while `V3V3_MAIN` is valid.
- FTDI VCC shall feed only a current-limited service rail. An 82 ohm, 1% series
  resistor shall limit cable-wire current below 68 mA even for a downstream
  short at 5.5 V; a TPS2553 shall provide secondary active limiting,
  disconnect, and fault indication.
- Controller ground and stove-side J3/J5 ground shall remain separated across
  the UART isolation barrier.
- Thermostat contacts shall remain dry and shall not connect to either logic
  ground.

## Environmental and serviceability goals

- Use industrial-temperature components where the cost delta is reasonable.
- Prefer 0603 passives and hand-inspectable leaded IC packages for Rev A.
- Use four PCB layers: signal/power, solid controller ground, power/quiet
  routing, signal/power. Keep the stove-side isolated island free of controller
  copper.
- Put external connectors on board edges and provide permanent pin/function
  labels on both sides where practical.
- Provide labeled test points for all rails, both grounds, UART directions,
  mode signals, heartbeat, relay request, watchdog output, and MCLR.
- Provide mounting holes outside the isolation and antenna keepouts.
- Provide physically separated controller-domain TP101-TP124 and target-domain
  TP201-TP209 probe banks; no target probe may bridge the isolation keepout.

## Release gates

- `GATE-J3`: repeat and record direction, levels, idle state, target-off
  leakage, and target supply behavior.
- `GATE-J5`: independently re-prove the main-board J5 mapping and its physical
  pin-1 orientation.
- `GATE-VTGT`: measure J5 VDD available current and prove the interface does not
  disturb reset/startup.
- `GATE-THERM`: measure thermostat open-circuit voltage, closed current, and
  behavior in all stove states.
- `GATE-MODE`: fault-inject every switch state, missing shunt/contact, and
  partial-power combination.
- `GATE-WDT`: prove relay release on stopped heartbeat, hung CPU, brownout,
  boot loop, and GPIO stuck in both states.
- `GATE-SVC`: prove zero-write J3 loader entry and read-only PICkit access on
  sacrificial hardware before any production target.
- `GATE-EMC`: review ESD, cable transients, creepage/clearance, antenna placement,
  and enclosure grounding before installation.
- `GATE-CAD`: close type, netlist, pin, schematic-placement, PCB-placement,
  routing-difficulty, build, and short checks with zero unexplained errors;
  inspect every generated manufacturing layer.
- `GATE-FP`: independently verify every exact symbol and footprint, especially
  the TPS25947 RPW package, TQ2 relay pin view/drills, four-pole mode switch,
  isolation packages, and all remotely fetched connector footprints.
- `GATE-FTDI`: measure the FTDI short-circuit ceiling, resistor temperature,
  TPS2553 behavior, service-rail startup, and UART operation over cable-voltage
  and temperature limits.
