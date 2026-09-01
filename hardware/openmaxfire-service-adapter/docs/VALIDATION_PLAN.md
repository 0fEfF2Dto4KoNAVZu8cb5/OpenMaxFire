# Portable service adapter validation plan

Status: staged first-article plan; no step authorizes fabrication or stove connection until preceding gates close

Every test record shall include adapter serial/revision, controller PCB number and serial, harness serials, instrument identification, software/tool version, jumper state, attached sources, measured values, photographs where relevant, reviewer, and date.

## Gate 0 — evidence and design release

Before schematic or PCB release:

- [ ] Archive the second independent `9067-0604` main-board J5 continuity map.
- [ ] Identify and document exact stove-end J3 and J5 connector housings and contacts.
- [ ] Measure normal main-controller VDD at J5 pin 2 and confirm J5 pin 3 reference.
- [ ] Measure powered J3 pins 1-4, especially pin 3, without using pin 3 in the design.
- [ ] Verify exact active-part order codes, datasheet revisions, package pinouts, lifecycle, and distributor availability.
- [ ] Complete host and target worst-case current calculations.
- [ ] Independently review the connection list and direct ICSP path.
- [ ] Review schematic, ERC, footprints, PCB DRC, fabrication outputs, harness drawings, enclosure, and labels.

Failure or ambiguity blocks board ordering.

## Gate 1 — serialized harness qualification

Test each harness separately before attaching it to the adapter or controller.

### FTDI harness

- [ ] Verify genuine FTDI model and serial.
- [ ] Continuity-map black, red, orange, yellow, green, and brown to J101.
- [ ] Prove no adjacent shorts and no unintended shield/drain connection.
- [ ] Verify CTS# is absent or terminates only on the deliberate NC pad.
- [ ] Flex the cable and strain relief while monitoring continuity.

### J3 harness

- [ ] Verify adapter pins 1, 2, and 4 reach the correct target contacts.
- [ ] Prove adapter and target cavity 3 are empty/open.
- [ ] Verify housing key, retention, and pin-1 mark.
- [ ] Prove the harness cannot mate with J202 or the J5 target connector.

### J5 harness

- [ ] Verify one-to-one pins 1-5 and square-pad orientation.
- [ ] Measure all five conductor resistances and compare for anomalies.
- [ ] Prove adjacent and all non-matching pairs are open.
- [ ] Verify the full hazard label and controller revision tag.

Initial acceptance:

- ordinary conductor less than 1 ohm end-to-end;
- ICSP conductors mutually consistent within 0.2 ohm;
- NC/adjacent isolation greater than 20 megohms at the test voltage; and
- no intermittency during gentle flex.

## Gate 2 — unpowered assembled-adapter inspection

With no cables or sources attached:

- [ ] Microscope-inspect U101/U104 orientation across the isolation corridor.
- [ ] Verify U102/U103 pin 1, D301 polarity, fuses, resistors, and capacitors.
- [ ] Verify J101/J201/J202/J203 and both jumper orientations.
- [ ] Confirm J201 pin 3 has no copper connection.
- [ ] Confirm J203 pin 6 has no copper connection.
- [ ] Confirm J202-to-J203 pins 1-5 are direct and correctly ordered.
- [ ] Verify JP201 2-3 PARK physically disconnects `VTGT_AUX` from `VTGT_RAW`.
- [ ] Verify JP301 2-3 PARK physically disconnects U104 collector from MCLR.
- [ ] Measure resistance between `GND_HOST` and `GND_TGT`; acceptance greater than 20 megohms with expected instrument polarity behavior recorded.
- [ ] Measure resistance from each supply to its own ground and investigate unexpected low values.
- [ ] Continuity-check every named test point.
- [ ] Inspect the entire no-copper corridor under magnification and against Gerber plots.

## Gate 3 — host-only power

No target, PICkit, J3, or J5 harness attached. JP201 and JP301 parked.

Use a current-limited 5 V bench supply at J101 first, then repeat with the genuine FTDI VCC.

- [ ] Ramp 0-5.5 V and record input current and `VHOST`.
- [ ] Verify U101 host-side supply and decoupling.
- [ ] Confirm target-domain rails remain below 50 mV.
- [ ] Confirm no measurable current or voltage appears on J201/J202/J203 target pins except instrument noise/leakage.
- [ ] Drive FTDI TX high/low and verify only U101 host input changes.
- [ ] Verify U101 host receive output is default high with target side absent.
- [ ] Toggle RTS# and record U104 LED current.
- [ ] With JP301 parked, confirm no target pin changes.
- [ ] Short the protected host auxiliary output through an appropriate bounded fixture and characterize F101 trip/recovery without exceeding FTDI ratings.

Target acceptance goals, to be finalized from datasheets:

- host idle current less than 10 mA;
- host reset-active current less than 15 mA;
- no host-to-target backfeed above the measured leakage limit; and
- no component exceeds accepted temperature rise.

## Gate 4 — target-only auxiliary power

Use an isolated, current-limited 5 V bench source at J202 pin 2/3. No FTDI, PICkit, or controller attached.

### JP201 parked

- [ ] Ramp `VTGT_RAW` from 0-5.5 V.
- [ ] Confirm `VTGT_AUX` remains discharged and below 100 mV.
- [ ] Confirm U102 target outputs are high impedance.
- [ ] Confirm no host rail rises.

### JP201 UART

- [ ] Record F201 voltage drop and total target auxiliary current.
- [ ] Confirm `VTGT_AUX` follows the source within the accepted drop.
- [ ] Measure U103 falling threshold, rising threshold/hysteresis, and release delay.
- [ ] Verify `VTGT_GOOD` holds both U102 outputs disabled until release.
- [ ] Sweep slow ramps, fast ramps, brownout, short interruptions, and abrupt removal.
- [ ] Confirm J3 pin 1 stays high impedance below the accepted rail threshold.
- [ ] Confirm R201 discharges `VTGT_AUX` after JP201 is parked or source removed.
- [ ] Confirm no target-to-host power transfer.
- [ ] Characterize F201 trip/recovery with a bounded load fixture.

Target acceptance goals:

- normal target auxiliary current less than 10 mA, with 15 mA as a design-review stop threshold;
- UART output not enabled until the target rail is stable;
- rail discharge to below 0.5 V within a documented bounded time; and
- no host-domain rise above the leakage limit.

## Gate 5 — isolated UART bench loopback

Use independent isolated bench supplies for host and target domains. Do not use a stove controller yet.

- [ ] Verify DC isolation remains intact with both domains powered.
- [ ] Exercise both UART directions with pseudorandom and walking-bit data.
- [ ] Verify non-inversion and no missing/duplicate bytes at 9600 8N1.
- [ ] Repeat at 19200, 57600, and 115200 baud as electrical margin tests only.
- [ ] Measure propagation delay, rise/fall time, overshoot, ringing, idle levels, and noise margin at U101, U102, and J201.
- [ ] Repeat with minimum/maximum planned harness lengths.
- [ ] Disconnect and reconnect each power domain in every order while transmitting.
- [ ] Hold TX high, low, floating, and toggling during target startup and shutdown.
- [ ] Prove J201 pin 1 becomes high impedance whenever `VTGT_GOOD` is low.
- [ ] Verify an open J3 TX input is weakly biased to target-derived UART idle high.
- [ ] Inject bounded shorts from J3 TX/RX to target ground and target VDD and record series-resistor current.

Acceptance:

- zero byte errors over the defined long-duration test at 9600;
- no false low/BREAK pulse exceeding the agreed threshold during power transitions;
- no backfeed beyond the measured release limit; and
- target output high impedance in every unqualified state.

## Gate 6 — isolated reset bench test

No PICkit connected. Use a simulated target MCLR pull-up and then expendable controller hardware.

- [ ] Verify JP301 PARK prevents all RTS# influence on MCLR.
- [ ] Verify missing JP301 shunt also prevents reset.
- [ ] With JP301 ARM, toggle RTS# and measure MCLR low voltage, delay, pulse width, and release edge.
- [ ] Test minimum and maximum MCLR pull-up current expected from the controller.
- [ ] Verify U104 cannot source voltage into MCLR.
- [ ] Verify host loss, FTDI unplug, port open, port close, host reboot, and software crash behavior.
- [ ] Confirm D301 limits reverse LED stress under tested transient conditions.
- [ ] Return JP301 to PARK and apply simulated PICkit VPP; measure that the reset branch adds no significant load.

The first controller test is reset observation only. No loader programming traffic is permitted at this gate.

## Gate 7 — expendable `9067-0604` J3 qualification

Use a spare controller in the previously accepted safe test arrangement.

- [ ] Reconfirm board identity, J3 orientation, and main-board J5 orientation.
- [ ] Measure J5 VDD before connecting JP201 in UART.
- [ ] Connect J3 and J5 harnesses with PICkit absent and reset parked.
- [ ] Record added target VDD current caused by the adapter.
- [ ] Confirm PIC startup, front-panel behavior, and idle UART are unchanged.
- [ ] Execute at least 100 `CR00` reads with zero errors.
- [ ] Execute identity and complete EEPROM backup three times and compare results.
- [ ] Monitor telemetry through representative off/cold input changes.
- [ ] Repeat target power cycles and cable/host reconnects.
- [ ] Observe operation in the electrically noisy conditions later approved for testing, without bypassing stove safety or opening energized compartments.

Only after read-only success may specifically listed normal-control commands be tested with their existing command-verification procedure.

## Gate 8 — main-board J5 power characterization

Before connecting a PICkit through the adapter:

- [ ] Measure unpowered resistance from J5 VDD to VSS in both meter polarities.
- [ ] Power the removed controller from an isolated current-limited bench arrangement at the separately identified normal low-voltage input and record J5 VDD.
- [ ] Measure steady current and startup inrush of the complete board.
- [ ] Separately test PICkit-supplied VDD starting with a conservative current limit and record whether target voltage remains regulated.
- [ ] Stop PICkit-powered testing if target current approaches the tool limit, VDD sags, any component warms, or device identity is unstable.
- [ ] Confirm no normal appliance mains or actuator harness is required or attached.

The accepted release shall state either:

- `PICkit-powered target qualified` with a measured current envelope; or
- `external target power required` with the exact current-limited low-voltage method and PICkit output disabled.

## Gate 9 — direct ICSP signal-integrity test

Use a PIC simulator fixture or expendable PIC/controller before an original target.

- [ ] Verify J203/J202 pin 1 orientation and direct continuity immediately before connection.
- [ ] Confirm JP201 and JP301 are parked, FTDI absent, and J3 disconnected.
- [ ] Scope VDD, MCLR/VPP, PGC, and PGD at both adapter and target ends.
- [ ] Record VPP rise, high level, pulse shape, and fall.
- [ ] Record PGC/PGD rise/fall, ringing, contention, and logic margin.
- [ ] Repeat using the maximum released PICkit and J5 harness length.
- [ ] Confirm pin 6 remains electrically absent.
- [ ] Confirm target UART electronics remain unpowered.

No programming operation is necessary to pass basic electrical waveform testing.

## Gate 10 — read-only ICSP qualification

On expendable `9067-0604` hardware:

- [ ] Detect exactly `PIC16F877A`.
- [ ] Read and save program memory, EEPROM, User IDs, configuration, Device ID, and protection status.
- [ ] Disconnect all sources and repeat the entire setup/read two more times.
- [ ] Generate section hashes and prove all three reads are identical.
- [ ] Compare against an independently known-good bare-chip/socket read where available.
- [ ] Repeat target power removal in both supported source modes, if both modes are released.
- [ ] Verify no adapter or target heating and no unexplained current.

Only after this gate may the physical adapter be labeled `J5 READ-ONLY QUALIFIED`.

## Gate 11 — write/recovery qualification

This gate requires separate project authorization and spare hardware.

At minimum:

- [ ] authenticate the exact complete PICkit image;
- [ ] preserve the pre-write target three times;
- [ ] program, verify, disconnect, and independently read back;
- [ ] compare every memory region and configuration field;
- [ ] verify controller boot and J3 identity;
- [ ] perform controlled interruption at each material programming phase;
- [ ] demonstrate recovery without relying on the original working controller; and
- [ ] publish all evidence, hashes, tool versions, controller identities, and failures.

A single successful flash is insufficient for release.

## Gate 12 — enclosure and production acceptance

- [ ] Enclosure prevents accidental contact with target-domain copper.
- [ ] Cable strain reaches clamps, not connector solder joints.
- [ ] All legends remain visible with cables installed.
- [ ] PICkit pin 1 cannot be mistaken or shifted without defeating a clear physical/visual control.
- [ ] J3 and J5 tails cannot cross-mate.
- [ ] Both jumpers have retained park positions and controlled shunt colors.
- [ ] Thermal soak shows acceptable rise.
- [ ] Serialized production test repeats harness continuity, domain isolation, UART loopback, reset-park, and ICSP direct-path checks.
- [ ] Release archive contains immutable schematic, PCB, Gerbers, drill, BOM, assembly, harness, enclosure, test procedure, and source hashes.

## Release criteria

A fabrication candidate requires Gates 0-1 design evidence and completed CAD checks. An assembled engineering unit remains `UNPOWERED ONLY` until Gates 2-4 pass. Each later qualification label is granted only after its named gate and all preceding gates pass with reviewed records.
