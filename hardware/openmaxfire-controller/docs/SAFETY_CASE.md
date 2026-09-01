# Preliminary safety case

This file states the claims the hardware must eventually justify. A claim is not
accepted merely because it appears in the schematic.

## Claim 1: controller failure does not strand the thermostat path

Mechanisms:

- K501 is non-latching and its NC contact is the physical-thermostat path.
- The coil is low-side driven and its gate has a hardware pulldown.
- `NORMAL_MODE`, `HEARTBEAT_OK`, and `RELAY_REQUEST` are independently required.
- U501 services on a heartbeat falling edge, while Schmitt inverter U504 turns
  that same edge into U503's rising arm clock. A static level cannot arm and
  service the chain using two different events.
- A 100 kohm heartbeat pulldown defines the reset/processor-absent state, and
  U503 is cleared outside NORMAL mode or on either watchdog/supervisor fault.
- The specified 22 nF C0G timing capacitor gives a 1.758 s nominal watchdog
  interval and an estimated 1.51-2.02 s tolerance range; measured release time
  remains a production gate.
- SW301 uses U501's `WD_CLEAR_N` output as its NORMAL source qualifier. The
  TPS3851 H33 supervisor, with a 3.069 V nominal falling threshold, therefore
  removes both J3 ownership and relay health during main-rail startup/brownout
  or a watchdog fault; there is no second main-rail supervisor.
- R501 pulls `WD_CLEAR_N` up only from `V3V3_MAIN`, while R306 pulls
  `MODE_SOURCE_OK` down; the NORMAL qualifier is therefore defined low when the
  main rail is absent.
- A passive bypass plug restores the original thermostat wiring after a board or
  relay mechanical failure.

Evidence still required: schematic review, component failure analysis, relay
contact characterization, timeout measurement across temperature, stuck-GPIO
tests, connector-removal tests, and live stove-state tests.

## Claim 2: service modes cannot leave OpenMaxFire in control

Mechanisms:

- Mode selection is hardware, not an ESP software setting.
- Only the NORMAL contact asserts `NORMAL_MODE`.
- Open/invalid switch states disable every UART source and the relay gate.
- FTDI and ESP outputs use powered-off protection and mutually exclusive output
  enables.
- PICkit mode has no enabled UART source.

Evidence still required: truth-table test of all intended, transition, open-
contact, shorted-contact, and partial-power states.

## Claim 3: an unpowered stove controller is not back-powered

Mechanisms:

- The isolator target side and final J3-output gate use target-derived power.
- The final output device has specified powered-off high impedance (`Ioff`).
- J3-3 is no-connect and cannot source the adapter.
- J5 VDD is current limited and used only after its source capability is proven.
- Target VDD is monitored rather than driven in ordinary operation.

Evidence still required: microamp-level leakage measurements with each domain
powered alone, ramp tests through UVLO, and target startup/reset observation.

## Claim 4: service power sources cannot energize the installed controller

Mechanisms:

- USB VBUS reaches only a high-impedance MOSFET gate. The controller-side
  `USB_VBUS_PRESENT_N` signal is active low and powered from `V3V3_MAIN`.
- Every FTDI-powered board load is downstream of an 82 ohm, 1% resistor that
  limits a 5.5 V hard short to less than 68 mA; TPS2553 adds active limiting,
  disconnect, and fault indication.
- PICkit VDD remains in the target domain and has no DC path to controller rails.
- The relay coil is powered only from permanent protected input power.
- U607/U608 place every expansion data conductor behind powered-off-isolating
  switches. Their OE requires `EXPANSION_ENABLE`, U609 rail-good delay, and an
  inactive expansion fault through Q601-Q603. The J602 pull-up is connector-side,
  so controller GPIO cannot feed a disabled `EXP_3V3` rail through it.

Evidence still required: resistance/diode-mode audit, resistor fault-temperature
test, USB sense truth-table test, TPS2553 behavior, expansion off-domain leakage
and fault/enable sequencing, and all single-source power tests before installing
a harness.

## Claim 5: OpenMaxFire cannot directly override factory combustion safety

Mechanisms:

- The board connects only to documented low-voltage service, ICSP, thermostat,
  local sensor, and expansion interfaces.
- There are no outputs to igniters, fans, motors, valves, ash/burn mechanisms,
  or line-voltage circuits.
- Normal firmware exposes bounded J3 commands and treats transmitted commands
  as pending until state readback confirms them.

Evidence still required: connector/harness inspection and firmware API review.

## Known limits

- A physical thermostat on firmware 2.02 does not independently start a stopped
  stove; it only changes an already-running stove between selected level and
  level 1.
- A mechanical relay can fail welded or open. The passive bypass addresses loss
  of continuity but not every possible contact fault.
- Galvanic isolation is for signal-domain separation; final creepage category
  depends on proving J3/J5 are SELV. It is not authorization to work on an
  energized open stove.
- Neither this controller nor Home Assistant is the final freeze-protection
  system.
- The current PCB and documentation are engineering artifacts, not a released
  fabrication package. Open CAD, footprint, stove-interface, thermostat,
  watchdog, EMC, enclosure, and production-test gates remain listed in the
  validation and bring-up documents.
