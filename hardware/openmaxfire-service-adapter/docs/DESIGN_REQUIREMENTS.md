# Portable service adapter design requirements

Status: design-input requirements; no released schematic or PCB

## 1. Product purpose

The adapter shall provide a small, inexpensive, portable service interface for a supported Bixby MaxFire main controller. It shall support:

1. isolated UART communication through main-board J3 using an external FTDI TTL cable; and
2. direct Microchip ICSP access through the five-contact main-board J5 using an external PICkit.

The first revision is a technician tool, not a permanently installed controller and not an appliance safety device.

## 2. Supported hardware boundary

- The initial supported target is the photographed large main controller marked `PCB Part Number 9067-0604` and fitted with a PIC16F877A.
- J3 behavior is based on live evidence from stove serial 5215.
- Main-board J5 remains provisionally mapped until a second independent continuity pass is archived.
- The auxiliary igniter-board connector also called J5 is expressly unsupported and hazardous.
- A different PCB number, PIC, contact count, connector location, or continuity result shall be treated as incompatible until separately qualified.

## 3. Functional requirements

### FR-1: J3 UART

The adapter shall:

- carry FTDI TX to stove J3 pin 1 and stove J3 pin 2 to FTDI RX;
- preserve non-inverted UART operation at 9600 baud, 8 data bits, no parity, and one stop bit;
- be electrically capable of higher test rates up to 115200 baud without making those rates a stove-compatibility claim;
- leave J3 pin 3 completely unconnected in the PCB and cable;
- reference the stove-side UART only to J3/J5 target ground;
- isolate FTDI/computer ground from target ground;
- prevent a powered FTDI from driving or back-powering an unpowered stove UART input;
- default the FTDI receive output to UART idle high when the target side is absent; and
- permit all currently implemented `maxfirectl` read-only and normal-control transactions after qualification.

### FR-2: deterministic J3 reset provision

The adapter shall provide an optional FTDI RTS# controlled, optically isolated, open-collector pull-down to main-board J5 MCLR.

The reset path shall:

- only pull MCLR low;
- never source MCLR or programming voltage;
- remain physically disconnected in its normal PARK position;
- require a deliberate shunt change to ARM;
- include no component in series with the direct PICkit MCLR/VPP path; and
- return to PARK immediately after an attended reset/loader-entry operation.

### FR-3: J5 ICSP

The adapter shall map:

| PICkit | Function | `9067-0604` main-board J5 |
| ---: | --- | ---: |
| 1 | MCLR/VPP | 1 |
| 2 | VDD target sense/source | 2 |
| 3 | VSS | 3 |
| 4 | PGD/ICSPDAT | 4 |
| 5 | PGC/ICSPCLK | 5 |
| 6 | AUX/PGM | no connection |

Pins 1-5 shall be short, direct, one-to-one connections. No LED, diode, clamp, capacitor, RC filter, translator, isolator, or unqualified series impedance may be placed in those paths.

### FR-4: physical mode separation

The product shall have a hardware target-interface power selector with two unambiguous states:

- `UART`: target VDD may power the isolated UART secondary and target buffer;
- `ICSP/PARK`: target UART electronics are physically disconnected from target VDD.

ICSP does not require switching MCLR, VDD, VSS, PGD, or PGC. The unplugged PICkit header is passive during UART use. Operational instructions shall still require the unused host tool and unused target harness to be disconnected.

### FR-5: power behavior

- The adapter shall have no battery, wall supply, onboard USB supply, isolated converter, or external target-power injection input.
- The FTDI cable may power only the host side of the isolator and the reset optocoupler LED.
- Main-board J5 VDD may power only the target-side UART electronics while the mode jumper is in UART.
- PICkit pin 2 shall remain directly connected to target VDD for sensing or qualified PICkit-powered operation.
- Exactly one target VDD source is permitted during ICSP.
- No adapter state may join host VCC to target VDD or host ground to target ground.

### FR-6: target-good gating

The adapter shall hold both target-facing UART buffer outputs disabled:

- while target-interface power is disconnected;
- during startup delay;
- below the selected target undervoltage threshold;
- during brownout and rail collapse; and
- whenever the supervisor output is indeterminate.

The target buffer shall have specified powered-off protection on its signal pins.

### FR-7: protection

- Host and target auxiliary interface supplies shall each include a resettable overcurrent device or an independently reviewed equivalent.
- UART signal paths shall include modest edge/fault series resistance adjacent to the target connector or buffer.
- Any optional ESD footprint shall be unpopulated until its leakage, capacitance, clamp voltage, and target reference are reviewed.
- Protection shall not compromise PICkit bidirectional signaling or VPP.

## 4. Safety requirements

### SR-1: positive target identification

The enclosure and J5 harness shall state:

`9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5`

J3 and J5 target tails shall use different contact counts and shall not cross-mate at the adapter. Pin 1 shall be marked at the adapter, harness, and target connector.

### SR-2: domain isolation

- `GND_HOST` and `GND_TGT` shall have no intentional conductive connection.
- Only the digital isolator and reset optocoupler may cross the PCB isolation corridor.
- PICkit service intentionally references the target domain and is permitted only on a removed, de-harnessed controller under the offline procedure.

### SR-3: fail-open defaults

Removing either configuration shunt, placing it incorrectly, losing target power, losing host power, or leaving a jumper between positions shall not create an actively driven J3 output or an automatic MCLR assertion.

### SR-4: no energized ICSP

The released procedure shall prohibit PICkit connection while the controller is installed in an energized appliance, while appliance mains or actuator harnesses are attached, or while J3/FTDI is connected.

### SR-5: first-operation boundary

The first successful J5 operations shall be device identification and repeated complete reads. Erase or program operations require a separately approved expendable-target procedure and authenticated firmware image.

## 5. Mechanical requirements

- Two-layer, 1.6 mm FR-4 and 1 oz copper are preferred.
- Target size is at most 60 mm x 40 mm; 65 mm x 45 mm is the hard first-revision maximum.
- All external connectors shall be accessible from board edges.
- The FTDI, J3, and J5 adapter-side connectors shall be polarized/shrouded.
- Configuration shunts shall be accessible without removing strain relief and shall have visible parked/active legends.
- The isolation corridor shall be visible on both silkscreen sides and preserved through copper, vias, test pads, mounting hardware, and enclosure features.
- Cable exits shall have independent strain relief so force is not transferred to board headers.

## 6. Cost and manufacturing requirements

- The adapter PCB assembly shall target USD 8-12 in small quantities, excluding external tools, PCB, enclosure, and target-end connectors.
- The design shall use commonly stocked active parts and 0603/0805 passives where practical.
- Isolation packages and edge connectors may use larger footprints where required for hand inspection and reliability.
- Through-hole connectors and jumpers are preferred; SMD active parts and passives are acceptable.
- There shall be no BGA, QFN, fine-pitch leadless package, blind/buried via, via-in-pad, controlled impedance, or four-layer requirement.

## 7. Documentation and production requirements

Before fabrication release, the project shall provide:

- reviewed schematic and netlist;
- exact manufacturer part numbers and approved alternates;
- symbol/footprint/polarity verification records;
- adapter and target harness drawings;
- enclosure and label drawing;
- serialized cable continuity test;
- complete ERC/DRC and fabrication-output review;
- staged first-article test record; and
- explicit supported-board and unsupported-board list.

## 8. Non-goals for Rev A

The adapter shall not include:

- ESP32, Wi-Fi, Ethernet, Bluetooth, or Home Assistant logic;
- permanent stove control;
- thermostat transfer or dry-contact circuitry;
- onboard USB-UART or USB composite device;
- onboard PIC programming algorithm or VPP generator;
- target power supply or battery;
- display, buttons, logging storage, or firmware;
- expansion GPIO or external sensor interfaces;
- direct control of igniters, fans, feed motors, ash mechanisms, or line-voltage circuits; or
- compatibility claims for an unverified main-board revision.

A feature that violates these non-goals belongs in a later product, not in the first service adapter.
