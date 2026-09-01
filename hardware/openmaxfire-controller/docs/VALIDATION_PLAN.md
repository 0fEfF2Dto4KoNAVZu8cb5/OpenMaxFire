# Validation and release plan

No production-stove write or unattended operation is authorized by completing
only a schematic or PCB build. Validation proceeds from passive inspection to
sacrificial hardware.

## 1. Design audit

- Independently check every IC pin number against the current manufacturer
  datasheet and every footprint against the recommended land pattern.
- Run tscircuit netlist, pin-specification, schematic-placement, PCB-placement,
  routing-difficulty, and short checks with zero unexplained errors.
- Inspect schematic, all four copper layers, both solder-mask/silkscreen sides,
  drill/cutout data, 3D render, fabrication outputs, and the generated KiCad
  project.
- Perform an independent schematic safety review and FMEA.
- Verify BOM lifecycle, temperature grade, and alternate parts.
- Verify the 140 mm x 100 mm outline, mounting-hole geometry, antenna clearance,
  connector access, and the full-height isolation keepout against the enclosure.
- Treat the TPS25947 RPW land pattern, TQ2 bottom-view pin numbering and drills,
  four-pole mode switch, isolation packages, and custom/library connector
  footprints as explicit independent-review gates.
- Verify the source's physical polarity convention against every exact package:
  D1/D3/D301/D302/D401/D402/D501/D601 use pin 1 cathode and pin 2 anode;
  D304 uses pins 1/2 as anodes and pin 3 as the common cathode. Do not release
  D2/D101/D303 until exact LED MPN polarity matches the PCB artwork and drive.

## 2. Unpowered bare-board tests

- AOI/microscope inspection; resistance to ground on every rail.
- Verify no continuity across the isolation keepout or into dry contacts.
- Verify direct PICkit pin order and AUX/PGM no-connect.
- Verify diode band/pad orientation and every polarized capacitor before power;
  verify the selected LEDs rather than assuming a generic 0603 pin convention.
- Verify mode-switch truth table with an ohmmeter before fitting active parts.
- Verify TP101-TP124 are controller-domain only and TP201-TP209 are target-
  domain only; check labels, continuity, and absence of barrier crossings.
- Hi-pot/insulation test only to a reviewed SELV-domain plan; do not improvise a
  mains isolation test.

## 3. Single-domain power tests

Power one source at a time: permanent input, USB VBUS, FTDI VCC, and target VDD.
For every case record all rail voltages and source currents.

Acceptance criteria:

- an absent rail remains below the agreed leakage threshold;
- J3 output is high impedance with target VDD absent or below valid range;
- USB and FTDI cannot energize K501 or the ESP main rail;
- `USB_VBUS_PRESENT_N` is low only with VBUS present while `V3V3_MAIN` is valid,
  and VBUS cannot lift any board rail;
- target VDD cannot lift controller power;
- relay is de-energized until NORMAL mode plus valid heartbeat plus request;
- the 82 ohm FTDI input resistor keeps worst-case cable current below 68 mA at
  5.5 V under a downstream short, without exceeding its thermal limits; and
- the downstream TPS2553 disconnects/limits as designed while the legitimate
  FTDI service load still receives enough voltage to communicate.

## 4. Power supply and thermal tests

- Sweep 10.8-13.2 V as the normal input range, then perform bounded 15 V
  qualification and verify overvoltage cutoff above the documented ceiling.
- Test reverse polarity, slow ramps, brownout, hot plug, and repeated cycling.
- Measure ripple and transient response during ESP32 Wi-Fi transmit bursts and
  relay switching.
- Run worst-case radio, UART, sensor, and relay load together.
- Record component/enclosure temperatures at minimum/nominal/maximum ambient.

## 5. Mode and dead-man fault injection

- Exercise NORMAL, FTDI SERVICE, PICkit/OFFLINE, switch transitions, open
  contacts, and each partial-power combination.
- Sweep `V3V3_MAIN` through U501's TPS3851 H33 3.069 V nominal falling threshold,
  hysteresis, and release timing. Prove `WD_CLEAR_N` prevents SW301 from
  qualifying NORMAL/J3 ownership during startup or brownout; there is no second
  main-rail qualifier. With `V3V3_MAIN` absent, verify R501 supplies no foreign
  pull-up and R306 holds `MODE_SOURCE_OK` low.
- Inject watchdog timeout and reset pulses on `WD_CLEAR_N`; prove each removes
  UART ownership and clears relay health before a fresh heartbeat can restore
  either qualification.
- Stop heartbeat at every phase and measure K501 release time.
- Hold heartbeat GPIO high, low, toggling too slowly, and toggling too fast.
- Scope U501 WDI and U503 `HEARTBEAT_ARM_CLK`; prove the same ESP falling edge
  both services the watchdog and becomes the latch's rising clock through U504.
- Measure the 22 nF C0G watchdog interval across voltage and temperature and
  confirm the released population lies within the justified 1.51-2.02 s range.
- Return from service/OFFLINE to NORMAL with heartbeat held high and low; prove
  neither stale level can assert `HB_OK` without a fresh high-to-low edge.
- Hold relay request high through reset and brownout.
- Induce ESP boot loop, task hang, watchdog reset, invalid temperature, stale J3,
  Wi-Fi loss, Home Assistant loss, and complete network loss.
- Confirm only network loss permits continued local operation, and only while
  the local loop remains healthy.

## 6. Target-interface qualification

On a spare 9067-0604 controller with actuators/igniters disconnected:

- repeat the J3 pin/level/source-impedance measurements;
- repeat J5 mapping with an independent continuity method;
- measure J5 VDD current margin and its behavior during reset/startup;
- verify J404 is open and exactly one target-VDD source is configured before
  every PICkit connection; positively distinguish the main-board J5 from the
  igniter-board 120 VAC J5;
- log target-off leakage across the full voltage ramp;
- characterize R411's 47 kohm target-derived idle bias on the J3 pin-2 receive
  path: open-conductor idle, target input loading, transition behavior, and
  target-off leakage. Do not record the stove-to-controller input as an ideal
  high-impedance conductor;
- run read-only J3 identity/telemetry in NORMAL and FTDI modes;
- qualify 100/100 deterministic zero-write loader entries before any write;
- use PICkit read-only first and follow the preservation boundary;
- test forced interruptions on sacrificial targets before any production use.

## 7. Expansion isolation and analog tests

- Begin with GPIO11 low and all expansion harnesses absent. Confirm U602 is off,
  `EXP_3V3` discharges, U607/U608 OE is inactive, and all sixteen data paths are
  disconnected.
- Exercise the complete hardware truth table. U607/U608 may connect only when
  `EXPANSION_ENABLE=1`, U609 (`TLV809EA29DBZR`) rail-good has completed its
  approximately 200 ms release delay, and `EXPANSION_FAULT_N=1`; loss of any one
  condition must disconnect every path without firmware action.
- Ramp and brown out `EXP_3V3` through U609's 2.9 V-class threshold, trip U602's
  current limit, hold GPIO11 high/low/open, and externally hold the rail charged.
  Record OE timing, rail decay, fault recovery, and absence of chatter.
- With `EXP_3V3=0`, drive each J601, J602, and J603 data pin separately to 0 V
  and 3.3 V within a current-limited fixture. Measure leakage into
  `V3V3_MAIN`, `EXP_3V3`, each controller GPIO, and every unrelated connector;
  repeat with controller power absent and accessory power present.
- Verify R651 is on U608's connector side. Hold ESP GPIO8 high while expansion
  is disabled and prove the 1-Wire pull-up cannot lift `EXP_3V3`; then qualify
  1-Wire rise time and cable length after the gate connects.
- Sweep J603 pin 3 from 0 to 3.3 V. Confirm the nominal ADC node is five-sixths
  of connector voltage (2.75 V at 3.3 V), verify 20 kohm/100 kohm tolerance and
  bus-switch error, and establish firmware attenuation/calibration limits.
- Exercise J601 direction changes, J603 GPIO and hopper contacts, cable opens,
  shorts, ESD fixtures, and hot plug only after the off-domain tests pass.

## 8. Thermostat tests

- Measure open voltage and closed current before connecting K501.
- Verify relay wiring and break-before-make behavior with a simulated load.
- On spare stove hardware, observe open/closed behavior in off, startup, run,
  ramp, shutdown, fault, and power-restoration states.
- Fault the PCB, relay drive, controller power, harness, and firmware and confirm
  passive thermostat restoration.
- Demonstrate and label the passive bypass plug.

## 9. Release artifacts

Release requires:

- signed schematic/PCB/BOM review checklist;
- source and generated-artifact hashes;
- assembly drawing and enclosure drawing;
- harness drawings with board-revision labels;
- factory test procedure and passing serial-numbered results;
- installation, normal-operation, service-mode, bypass, and recovery guides;
- explicit list of remaining limitations.

The execution order and current open-gate snapshot are maintained in
[`BRINGUP_CHECKLIST.md`](./BRINGUP_CHECKLIST.md). That checklist does not reduce
or replace any requirement in this plan.
