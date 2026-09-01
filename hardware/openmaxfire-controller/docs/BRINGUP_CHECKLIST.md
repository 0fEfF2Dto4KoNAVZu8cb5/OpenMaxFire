# First-article bring-up and release checklist

Status: planning document only. The current design is **not approved for
fabrication, installation, energized-stove testing, or production use**. This
checklist sequences work after each preceding gate is signed; it does not
replace [`VALIDATION_PLAN.md`](./VALIDATION_PLAN.md) or authorize skipping any
test there.

## Current open gates

| Gate | Current disposition | Evidence required to close |
| --- | --- | --- |
| CAD and routing | OPEN | Zero unexplained type, netlist, pin, schematic-placement, PCB-placement, routing-difficulty, build, and short errors; visual inspection of every generated layer and 3D assembly. |
| Exact symbols/footprints | OPEN | Independent package/pin/land-pattern audit, especially TPS25947 RPW, TQ2 bottom-view numbering and 1.0 mm drills, four-pole selector, isolation parts, ESP module, and custom/library connector footprints. |
| Mechanics/enclosure | OPEN | Confirm 140 mm x 100 mm outline, mounting holes, connector access, switch labeling, external antenna path, isolation clearance, and service access in the intended enclosure. |
| J3/J5 target evidence | OPEN | Repeat J3 electrical measurements; second-person main-board J5 continuity/orientation proof; supported-board-revision record. |
| Target-derived power | OPEN | Measure J5 VDD source capability, target disturbance, U402 load margin, target-off leakage, and all partial-power states. |
| FTDI service power | OPEN | Prove R300 keeps a 5.5 V hard short below 68 mA, remains thermally safe, and leaves adequate service voltage; qualify TPS2553 limit/fault behavior. |
| Watchdog/fail-back | OPEN | Verify same-falling-edge U501/U504/U503 behavior, 1.51-2.02 s timing limits, brownout response, stuck GPIOs, and relay release time. |
| Thermostat circuit | OPEN | Measure stove thermostat voltage/current, independently verify TQ2 contact orientation, test bypass/force-backup behavior, and qualify contact ratings. |
| Firmware | OPEN | Implement and review [`FIRMWARE_PIN_MAP.md`](./FIRMWARE_PIN_MAP.md), bounded J3 behavior, local fallback, fault logging, and update/recovery design. |
| EMC/environment/production | OPEN | ESD/EFT, thermal, humidity, vibration, harness, antenna, serialized test, manufacturing, installer, and independent safety sign-off. |

No fabrication release exists while any row above is open.

## A. Design package before ordering boards

- [ ] Freeze an identified source revision without committing or publishing it
  as a release prematurely.
- [ ] Run the complete tscircuit workflow and archive logs: TypeScript/source,
  netlist, pin specification, schematic placement, PCB placement, routing
  difficulty, build, and shorts.
- [ ] Inspect schematic readability and all four copper layers, masks,
  silkscreens, keepouts, drills, cutouts, antenna clearance, and 3D model.
- [ ] Confirm the isolation keepout is 8 mm wide, 102 mm tall, centered at
  `x=-23 mm`, present on every copper layer, and crossed only by U401/U404/U406/
  U407.
- [ ] Independently compare every symbol pin and footprint pad to the exact MPN
  drawing. Record reviewer, drawing revision, and disposition.
- [ ] Record polarity explicitly: D1/D3/D301/D302/D401/D402/D501/D601 are
  physical pin 1 cathode and pin 2 anode; D304 has anodes on pins 1/2 and common
  cathode on pin 3. Select exact D2/D101/D303 LED MPNs and prove their package
  polarity matches the PCB artwork rather than assuming a generic 0603 order.
- [ ] Verify all connector pin-1 marks, cable-face versus board-face numbering,
  enclosure accessibility, and non-interchangeable harness strategy.
- [ ] Check the controlled BOM, lifecycle, ratings, alternates, assembly drawing,
  harness drawings, and source/generated-artifact hashes.

Stop here if any CAD error, generic/unverified land pattern, ambiguous connector,
or mechanical conflict remains.

## B. Unpowered assembled-board inspection

- [ ] Assign a serial number and record assembly lot, board revision, and test
  equipment calibration.
- [ ] Microscope-inspect soldering, each diode band against the recorded pad-1
  convention, polarized capacitors, LED polarity, IC/relay pin 1, switch and
  connector keys, mounting hardware, antenna region, and isolation corridor.
- [ ] Measure resistance to ground on all controller, service, and target rails.
- [ ] Prove no continuity between `GND_CTRL`, `GND_TGT`, and any thermostat dry
  contact.
- [ ] Continuity-check TP101-TP124 and TP201-TP209 to their documented nets and
  verify that probe-bank labels match [`INTERFACES.md`](./INTERFACES.md).
- [ ] Ohm out all switch positions and transitions. OFFLINE and between-detent
  states must not qualify UART ownership or relay-coil power.
- [ ] Verify J501 released-contact routing, J502 normally-closed shunt assembly,
  passive bypass harness, and direct PICkit pins 1-5 with pin 6 open.
- [ ] Confirm J404 AUTO RESET ARM is not fitted.

## C. Current-limited controller power

Use a current-limited bench supply first; do not connect a stove, thermostat,
USB host, FTDI cable, PICkit, or expansion harness.

- [ ] Start below the expected load with relay disabled, then ramp through the
  10.8-13.2 V operating range while recording current and every rail.
- [ ] Verify fuse/reverse-polarity/TVS/eFuse behavior, eFuse thresholds, 5 V and
  3.3 V regulation, ripple, startup, shutdown, slow ramp, and brownout.
- [ ] Sweep `V3V3_MAIN` through U501's TPS3851 H33 3.069 V nominal falling
  threshold, hysteresis, and release timing. Prove `WD_CLEAR_N` prevents SW301
  from qualifying NORMAL/J3 ownership during startup and brownout; there is no
  second main-rail qualifier. With `V3V3_MAIN` absent, verify R501 supplies no
  foreign pull-up and R306 holds `MODE_SOURCE_OK` low.
- [ ] Pulse `WD_CLEAR_N` with both TPS3851 reset and watchdog fault conditions.
  Confirm each pulse removes UART ownership and clears relay health.
- [ ] Confirm K501 remains released and J501 COM-NC continuity is preserved.
- [ ] Exercise reset and boot buttons; verify safe GPIO defaults before loading
  application firmware.

## D. Single-source and partial-power matrix

Apply only one source at a time before testing allowed combinations.

- [ ] USB only: confirm no controller rail rises. With controller power also
  valid, confirm `USB_VBUS_PRESENT_N` changes low on attach and high on removal.
- [ ] FTDI only through R300: confirm neither ESP nor relay powers. Measure
  legitimate load voltage/current, then use a bounded electronic load/short
  fixture to confirm the less-than-68 mA ceiling at 5.5 V and resistor
  temperature. Verify TPS2553 limiting, recovery, and fault indication.
- [ ] Target VDD only: confirm no controller/service rail rises. With
  `UART_CONNECT=0`, verify J3 pin 1 is high impedance and J3 pin 2 has no source
  other than its target-derived R411 weak bias through R406.
- [ ] PICkit power only, on a sacrificial target setup: confirm direct target-
  domain behavior and no controller backfeed.
- [ ] Expansion accessory power only, with controller power absent: drive
  current-limited 0 V/3.3 V test levels into each J601/J602/J603 data conductor
  and prove neither `V3V3_MAIN` nor unrelated signals rise.
- [ ] Controller power with GPIO11 low: confirm `EXP_3V3` is off and discharged,
  U607/U608 are disconnected, and externally driven connector pins cannot
  backfeed the rail or controller GPIOs. Hold the external rail charged and
  repeat to prove Q603 keeps OE disabled when `EXPANSION_ENABLE=0`.
- [ ] Repeat power application/removal in both orders, hot plug, slow ramp,
  brownout, and abrupt loss while probing for unintended UART BREAK or MCLR.

## E. Firmware and dead-man bench test

- [ ] Load a bench-only image implementing the safe startup sequence and pin
  directions in [`FIRMWARE_PIN_MAP.md`](./FIRMWARE_PIN_MAP.md).
- [ ] Confirm mode inputs decode as NORMAL `0/1`, FTDI `1/0`, OFFLINE `1/1`, and
  fault `0/0`; the latter two must force `RELAY_REQUEST=0`.
- [ ] With a scope, prove one ESP falling `HEARTBEAT` edge services U501 and the
  U504 output creates the same event's rising `HEARTBEAT_ARM_CLK` edge.
- [ ] Measure watchdog and relay release across supply and temperature. Confirm
  the justified 1.51-2.02 s watchdog range before freezing firmware cadence.
- [ ] Hold heartbeat and relay-request GPIOs high, low, open, slow, fast, and
  through resets/boot loops. Return through every mode and prove a stale level
  cannot re-arm `HB_OK`.
- [ ] Verify `EXP_3V3` defaults off, TCA9535 address `0x20`, P00-P13 boot as
  inputs, P14-P17 remain unused/pulled low, and GPIO11 explicitly controls U602.
- [ ] Exercise the U607/U608 OE truth table. All sixteen signal paths may connect
  only with GPIO11 high, U609 (`TLV809EA29DBZR`) rail-good released after
  approximately 200 ms, and `EXPANSION_FAULT_N` high. Loss of any term must
  disconnect them in hardware.
- [ ] Ramp/brown out `EXP_3V3`, trip U602 current limit, and hold the rail
  externally charged. Record U609 threshold/delay, OE timing, fault recovery,
  rail decay, and absence of signal backfeed or chatter.
- [ ] Verify R651 connects `EXP_3V3` to the J602/U608 connector side. Hold ESP
  GPIO8 high with expansion disabled and prove it cannot lift the rail; then
  qualify 1-Wire rise time with the signal gate enabled.
- [ ] Sweep J603 pin 3 from 0-3.3 V and confirm the 20 kohm/100 kohm divider gives
  five-sixths at GPIO1/ADC1, including 2.75 V nominal at the 3.3 V endpoint.
  Establish firmware ADC calibration and acceptance limits.

Use a simulated dry-contact load, not a stove thermostat, for these tests.

## F. Mode, relay, and thermostat simulation

- [ ] Mark the selector NORMAL / FTDI SERVICE / PICkit-OFFLINE and exercise all
  intended positions, between-position travel, contradictory fault injection,
  and missing contacts.
- [ ] Verify only NORMAL supplies `KTH_COIL_5V`; removing the J502 shunt must
  release the relay regardless of GPIO/watchdog state.
- [ ] Prove released K501 connects stove A/B to backup A/B and energized K501
  joins the two stove leads only through the floating NO contacts.
- [ ] Measure pickup/dropout time, flyback behavior, contact bounce, coil and
  driver temperature, and every power-loss transition.
- [ ] Demonstrate the passive bypass with the PCB completely removed.

Do not connect the real thermostat until its open voltage, closed current,
transients, and all stove-state behavior have been independently measured and
accepted against the relay/contact design.

## G. Sacrificial target qualification

- [ ] Use only a spare 9067-0604 controller with mains, actuators, and igniters
  disconnected.
- [ ] Independently re-prove J3 and main-board J5 pinout/orientation immediately
  before cable insertion. Positively distinguish the igniter-board 120 VAC J5.
- [ ] Measure J5 VDD source capability and prove U402/interface load cannot
  disturb startup, reset, or operation.
- [ ] Test NORMAL and FTDI UART paths read-only first, including target-off
  leakage, malformed data, cable faults, and all mode/power transitions.
- [ ] Qualify deterministic zero-write loader entry and verify J404 is fitted
  only for the attended reset test, then removed and accounted for.
- [ ] Begin PICkit work read-only with exactly one target VDD source and preserve
  flash, EEPROM, configuration, IDs, and calibration before any write test.
- [ ] With J3 pin 2 open, verify R411 produces UART idle high through its 47 kohm
  pull-up to `VTGT_PROTECTED`. Measure receive-path loading and target-off
  leakage; only the J3 pin-1 output is required to be actively high impedance.

Follow the complete offline and one-VDD-source procedure in
[`TARGET_SERVICE_DESIGN.md`](./TARGET_SERVICE_DESIGN.md#9-installer-and-service-rules);
the connector text `J5` alone is never sufficient identification.

## H. Release decision

- [ ] Complete thermostat, thermal, EMC/ESD/EFT, environment, enclosure,
  antenna, harness, field-recovery, and serialized production tests.
- [ ] Resolve every open item in this file and `VALIDATION_PLAN.md` with numeric,
  serial-numbered evidence.
- [ ] Obtain independent hardware, firmware, safety, manufacturing, and
  installer-documentation sign-off.
- [ ] Issue a distinct fabrication/installation release with immutable source
  and generated-artifact hashes. A successful prototype test is not itself a
  release.
