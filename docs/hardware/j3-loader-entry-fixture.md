# Deterministic J3 loader-entry fixture

Status: design requirements only. No schematic is construction-ready, J3-3 is
unresolved, and MCLR access on controller 9067-0604 has not been electrically
mapped.

## Objective

Enter the resident PIC16F877A loader on firmware 2.02 without relying on a
human-timed AC restoration and without allowing either UART endpoint to
partially power the other. The fixture must fail to an ordinary, released UART
and must never assert a reset accidentally when software, USB, or fixture power
is lost.

## Architecture choices

| Choice | Deterministic reset | Prevents UART backpower | Galvanic isolation | Assessment |
| --- | --- | --- | --- | --- |
| Bare FTDI + manual AC/BREAK | No | No | No | Retire for writes |
| FTDI all-input bit-bang + manual AC | No power-edge sense; mode switch unqualified | Reduces TX injection but leaves ~200 kOhm pull-up | No | Retired; bench characterization only after separate review |
| USB isolator before FTDI | No | No | Yes to host only | Insufficient |
| Always-powered isolated UART secondary | No | No | Yes | Insufficient without target-controlled output gate |
| Dual-supply fixed-direction translator + shared ground | With qualified MCLR channel | Conditional on exact-part/ramp qualification | No | Good bench/service candidate after reference-safety review |
| Target-powered UART isolator + isolated reset channel | With qualified reset channel | Conditional on exact-part/ramp qualification | Conditional on complete barrier construction | Preferred robust candidate |

## Option A: target-powered isolated fixture

Functional requirements:

```text
USB/host domain                    isolation            stove domain

FTDI TX  -> non-inverting channel  || -> stove RX/J3-1
FTDI RX  <- non-inverting channel  || <- stove TX/J3-2
RESET_EN -> isolated open-drain    || -> PIC MCLR pull-low only
USB GND                           ||    J3 ground
USB power                          ||    verified stove VDD
```

- The UART device needs one forward and one reverse channel and must be
  non-inverting at idle.
- The stove side must be powered from a verified stove supply that disappears
  with target VDD. Do not use an always-on isolated DC/DC output to drive J3-1
  unless a separate target-VDD gate guarantees high impedance.
- Choose the normal/default-high UART variant only after reviewing its
  power-off behavior. “Default high” while powered is not a substitute for
  high impedance while target VDD is absent.
- Require a specified stove-side output state and leakage limit at `VDD2=0`
  and throughout secondary undervoltage, power-up, and power-down while the
  primary remains powered. Also prove worst-case input/output logic margins in
  both directions; an isolator family name or nominal voltage is insufficient.
- With stove-side power present but FTDI/primary power absent or ramping, the
  stove-facing output toward PIC RX must remain valid UART idle-high or
  high-impedance with a verified target-domain pull-up. It must not pulse low,
  hold BREAK, or emit a malformed first byte as the primary rail crosses
  undervoltage thresholds.
- The reset channel must only sink MCLR. It must not source MCLR or expose a
  programming voltage.
- Until documented circuit/source construction, insulation coordination, and
  fault-condition assessment establish the J3 reference as SELV, treat this
  barrier as hazardous-voltage insulation. Spot voltage measurements alone
  cannot establish SELV. Select the exact isolator, reset component, PCB
  stackup, connectors, and enclosure for the assessed continuous working
  voltage, expected transients/overvoltage category, required basic or
  reinforced insulation, creepage/clearance, and applicable safety approvals.
  A component-family isolation rating does not qualify a hobby breakout or its
  board layout for an appliance boundary.

A basic ADuM1201-class breakout can be useful only on the safely bench-powered
spare, if both domains are supplied correctly and its exact channel
directions/defaults are known. Do not connect such a hobby breakout to the
installed controller before the interface safety classification and complete
barrier construction are established. Its mere presence does not provide
isolated secondary power, deterministic reset, or a mains-safe insulation
system.

## Option B: shared-ground, partial-power-down fixture

Use a dual-supply translator with one fixed channel in each direction, or two
separately powered `Ioff`-rated three-state buffers:

```text
FTDI TX -> [host input | target output] -> J3-1 / PIC RX
J3-2    -> [target input | host output] -> FTDI RX
```

The `TXU0202` is a promising single-device candidate: it has one non-inverting
A-to-B channel and one B-to-A channel, accepts 1.1-5.5 V supplies, specifies
`Ioff` and floating-supply leakage, and disables both outputs if either supply
is disconnected or below 100 mV. Assign B to verified stove VDD. Do not simply
run A at the FTDI's nominal 5 V: select a lower regulated host-side rail only
after proving that its worst-case input threshold accepts the FTDI cable's
guaranteed `VOH` and that its output meets the FTDI receiver's guaranteed
`VIH`. Pull OE to its disabled state and enable it only after both rails are
valid. The region between an absent rail and the minimum operating voltage,
including asymmetric ramps, still requires measurement and may require an
external power-valid gate.

Candidate-only logical routing is FTDI TX -> `A1`, `B1Y` -> J3-1/PIC RX,
J3-2/PIC TX -> `B2`, and `A2Y` -> FTDI RX. This names the fixed channel
directions; it is not a wiring authorization or complete schematic.

If discrete buffers are used instead, the receiving domain powers each one so
its output disappears with its receiver. Do not select a part from `Ioff`
alone. For example, the
`SN74LVC1G125` specifies partial-power-down/back-drive protection and an OE
power-transition circuit, but it is not qualified for the 5 V FTDI-to-stove
direction: its guaranteed high-input threshold is `0.7 * VCC` at a 4.5-5.5 V
supply, while the `TTL-232R-5V-WE` guarantees only 3.2 V minimum high output.
The worst-case limits have no valid high-level margin. Select each direction's
device only after its `VOH`/`VIH`, `VOL`/`VIL`, `Ioff`, output-off leakage, and
ramp behavior all overlap. Any active-low OE must default high relative to its
own supply during power-up/down, and a deliberate arm signal may enable it only
after both supplies are valid without creating a new cross-power path.

This design retains a common ground. It is useful only after a documented
circuit/source, insulation, fault-condition, and common-mode assessment—not a
spot measurement—establishes J3 ground as safe for the exact attached host and
instrumentation environment.

## MCLR control requirements

The MCLR stage is independent of the UART isolation choice:

MCLR makes loader entry deterministic but does not solve UART-line backfeed.
Every qualified write fixture must combine it with either Option A's
target-powered isolation or Option B's dual-supply partial-power protection;
bare FTDI plus MCLR is not, by itself, a qualified architecture.

- Develop it first on the spare controller using an electrically safe logic
  supply with no appliance loads attached. Testing an installed controller
  requires a cold stove, physically disconnected igniters and actuator loads,
  and a separately reviewed mains-safety procedure; reset may tri-state or
  reinitialize MCU outputs.
- Trace PIC pin 1 through every pull-up, capacitor, resistor, ICSP connector,
  and board test point before attachment.
- Use open-drain/open-collector pull-low control. Never actively drive MCLR
  high and never connect FTDI RTS directly.
- Hardware must default to released if USB is unplugged, the serial process
  exits, a GPIO floats, or fixture power disappears.
- Provide a physical arm mechanism so ordinary monitoring cannot assert reset.
- Do not attach the PICkit and reset fixture simultaneously.
- Preserve the board's normal MCLR pull-up and startup behavior. Microchip's
  reference network calls for pull-up R1 below 40 kΩ and series R2 between the
  RC node and MCLR above 1 kΩ; the actual board network remains authoritative.

Proposed host sequence after electrical qualification:

1. Open and configure UART at 9,600 8N1 with receive buffers drained.
2. Arm the fixture and pull MCLR low for a characterized interval.
3. Arm the bounded identify operation with TX held at a valid idle state, but
   transmit no byte while MCLR is low.
4. Release MCLR on a controlled event, wait the scope-qualified
   release-to-start interval, and transmit the first complete `EA` frame;
   repeat complete `EA` probes only after that first frame.
5. Require exactly `EB`; for qualification, send only `ED` and require `E4`.
6. Disarm the reset channel and confirm the application identity.

The exact hold and release-to-`EA` timing must come from scope captures, not an
untested constant.

## J3-3 measurement decision tree

Leave J3-3 disconnected until all of these are recorded:

1. Unpowered resistance/continuity to PIC VDD pins 11/32, PIC VSS pins 12/31,
   J3-4, R10, and C5.
2. Powered high-impedance voltage relative to J3-4 during off, boot, normal
   idle, and loader operation.
3. Source impedance/current-limited response using an electrically reviewed
   method appropriate to the measured voltage.

If J3-3 tracks PIC VDD and can safely supply the characterized isolator load,
it is a candidate stove-side supply. If not, locate a separately protected
target-domain supply. Do not infer function from the historical cable's red
wire.

## Instrumentation and acceptance

Use appropriately rated isolated or differential instrumentation until the
stove signal reference is established safe by circuit and fault-condition
assessment. Battery power alone does not establish adequate input insulation,
working-voltage, or measurement-category rating. An earth-grounded oscilloscope
clip must not be connected to an unproven appliance reference.

Before testing, the signed electrical acceptance record must define numeric
pass/fail limits and instrument bandwidth for off-rail voltage/current,
power-off leakage, UART `VIH`/`VIL` and `VOH`/`VOL` margins, maximum permitted
glitch width, and VDD/MCLR ramp and reset timing. Derive those limits from the
exact PIC, interface, supply, and reset-network specifications; qualitative
labels such as “not lifted,” “harmless,” or “valid idle” do not pass a trace.

Before any program frame, the completed fixture must pass this pre-`E3`
electrical and loader-entry gate:

- target VDD is not lifted when only the host side is powered;
- host/FTDI supply is not lifted when only the target side is powered;
- the fixture output toward PIC RX/J3-1 is high-impedance when target VDD is
  zero;
- with target VDD present and host power absent or ramping, PIC RX/J3-1 remains
  idle-high or high-impedance with a verified target pull-up, with no low pulse,
  BREAK condition, or false start bit;
- the fixture output toward FTDI RX is high-impedance when host/FTDI power is
  zero, so powered PIC TX/J3-2 cannot lift the host rail;
- isolator or buffer output leakage remains within its specified harmless limit
  through target-supply undervoltage, power-down, and power-up ramps;
- worst-case `VOH`/`VIH` and `VOL`/`VIL` limits overlap in both UART directions;
- non-inverted 5 V UART idle and transitions, with no first-byte framing error;
- reset control always defaults released;
- 100 consecutive `EA/EB`, `ED/E4` reset cycles on the spare 2.02 target;
- captured VDD/MCLR/RX/TX waveforms for representative cycles, with measured
  values compared against every recorded numeric limit.

Only after the complete pre-`E3` gate passes may the fixture enter qualification
with one complete expendable spare-target update followed by exact PICkit
whole-chip readback. That next-stage readback must show target-correct relocated
reset words at `0x1E84`-`0x1E87` and an unchanged remainder of the resident
loader, EEPROM, configuration, and User IDs. This is qualification admission,
not itself production authorization.

See the [physical-session forensic report](../reverse-engineering/physical-flash-session-forensics.md)
for the evidence behind these requirements.
