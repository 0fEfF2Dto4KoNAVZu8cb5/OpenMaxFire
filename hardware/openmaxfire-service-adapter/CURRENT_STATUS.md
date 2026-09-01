# Portable service adapter checkpoint

Snapshot: 2026-09-01  
Revision: Rev A preparation  
Status: **requirements and electrical-design package prepared; no PCB design exists**

> [!WARNING]
> This directory is an engineering input package, not a released schematic, PCB, cable, or service procedure. Do not order parts by description alone, fabricate a board, attach a PICkit through main-board J5, or connect this design to a stove until its open gates are closed and a distinct first-article release is issued.

## Product definition

The portable adapter will use the owner's existing genuine FTDI `TTL-232R-5V-WE` for J3 UART service and a separate genuine PICkit for J5 ICSP. It will not contain an ESP32, onboard USB bridge, programmer implementation, permanent supply, isolated DC/DC converter, thermostat relay, watchdog, display, expansion interface, or appliance actuator connection.

The target product consists of:

- one small two-layer interface PCB;
- one six-conductor FTDI-to-adapter lead;
- one four-position adapter-to-J3 harness with cavity 3 omitted;
- one five-position adapter-to-`9067-0604` main-board J5 harness;
- one standard six-pin PICkit header;
- a UART/ICSP target-power selection jumper;
- a normally parked automatic-reset arm jumper; and
- an inline enclosure with permanent identity, pin-1, mode, and hazard labels.

## Preparation completed

- Product scope and explicit non-goals are frozen for the first revision.
- The J3 and J5 functional blocks have been separated from the permanent controller.
- A four-active-device UART/reset architecture is defined.
- The direct PICkit-to-J5 mapping is specified without inline components.
- Physical UART/ICSP and RESET ARM configuration is defined.
- Host and target power domains, allowed crossings, and partial-power behavior are specified.
- Adapter-side connector families and preliminary pin assignments are selected.
- A schematic-ready net/connection list is written.
- A preliminary BOM, cost target, harness plan, mechanical constraints, operating rules, and qualification matrix are recorded.

## Key design choices

| Question | Rev A choice | Reason |
| --- | --- | --- |
| USB-UART | External genuine FTDI cable | Already live-validated; avoids another USB design and driver problem |
| ICSP programmer | External PICkit | Keeps VPP generation and device support in a proven tool |
| UART isolation | `ISO7721DWVR` | One forward and one reverse channel, 5 V operation, default-high UART behavior |
| Target-off behavior | `SN74LVC2G126DCUR` plus supervisor | Outputs disabled during startup, brownout, and target-power loss; powered-off protection |
| Target interface power | J5 VDD through a fuse and physical jumper | No isolated converter and no hidden target-power source |
| Mode control | Two three-pin shunt headers | Smaller and cheaper than a multi-pole selector; each has a defined park position |
| Automatic reset | `VOL618A-3X001T`, pull-down only | RTS# can reset the PIC without joining FTDI and target grounds or sourcing VPP |
| ICSP path | Direct pins 1-5; pin 6 NC | Preserves PICkit signaling and target-voltage sensing |
| Board construction | Two layers, target <=60 x 40 mm | Low prototype cost and easy visual inspection |

## What is known

- J3 pin 1 is stove RX, pin 2 is stove TX, and pin 4 is target ground on the documented `9067-0604` controller.
- The direct FTDI wiring has successfully communicated at 9600 8N1.
- J3 pin 3 traces through approximately 100 ohms to PIC VDD but remains deliberately unused.
- The working main-board J5 map is pin 1 MCLR/VPP, pin 2 VDD, pin 3 VSS, pin 4 PGD, and pin 5 PGC.
- A removed PIC has been successfully preserved with a PICkit and socket fixture.

## Open release gates

### Interface evidence

- Repeat and photograph an independent five-pin J5 continuity map on an unpowered `9067-0604` board.
- Identify the exact manufacturer, family, pitch, mating housing, and contacts for the stove-side J3 and J5 connectors.
- Measure J5 VDD and J3 pin 3 on a normally powered controller, including source impedance and available current.
- Measure controller-board current when powered from PICkit VDD and determine whether it stays safely below the PICkit's supported target-current limit.
- Complete three repeatable whole-device read-only PICkit captures through main-board J5 on expendable hardware.

### Electrical review

- Independently verify each exact part number, symbol pinout, package, land pattern, polarity, and lifecycle state.
- Confirm the target supervisor suffix and release delay against the selected orderable part.
- Calculate the complete host and target current budgets at minimum/maximum rail voltage and temperature.
- Prove no backfeed in every single-source and plug-order condition.
- Scope UART idle, transition, reset, VPP, PGC, and PGD behavior through the complete harness lengths.

### PCB and mechanics

- Draw and review the schematic from the connection list.
- Place and route the two-layer board while preserving the all-layer isolation corridor.
- Run native ERC/DRC and inspect copper, mask, silkscreen, drill, and outline outputs.
- Verify enclosure fit, cable exit, strain relief, jumper access, pin-1 visibility, and non-interchangeable target harnesses.

### Qualification

- Build an unpowered continuity fixture and serialized cable test record.
- Execute the staged host-only, target-only, UART, reset, partial-power, and ICSP tests in the validation plan.
- Perform all write testing only on spare hardware after repeatable read-only operation is proven.

## Cost and size checkpoint

The preliminary fitted electronics and adapter-side connectors are intended to remain below approximately USD 12 at small-quantity distributor pricing. That estimate excludes the FTDI cable, PICkit, PCB fabrication, enclosure, crimp tooling, and still-unidentified stove-side mating connectors.

The placement target is no larger than 60 mm x 40 mm. The isolation corridor and through-hole edge connectors, rather than component count, will probably determine the final outline.

## Immediate next engineering task

The next task is **schematic capture and independent electrical review**, followed by footprint verification. PCB placement and routing should not begin until the J5 mapping, connector identity, and target-power measurements are either closed or explicitly retained as first-article-only gates.
