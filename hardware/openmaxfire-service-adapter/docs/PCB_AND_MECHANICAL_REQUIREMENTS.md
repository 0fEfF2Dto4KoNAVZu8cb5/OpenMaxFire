# Portable service adapter PCB and mechanical requirements

Status: constraints for a future PCB design; this file is not a layout

## 1. Board target

The first adapter shall be deliberately simple:

- two copper layers;
- 1.6 mm FR-4;
- 1 oz finished copper;
- ordinary through vias only;
- no controlled impedance;
- no blind/buried vias or via-in-pad;
- target outline no larger than 60 mm x 40 mm;
- hard maximum 65 mm x 45 mm without a documented exception; and
- one small inline enclosure rather than a permanently mounted appliance assembly.

The board should be rectangular unless connector access or the isolation corridor clearly benefits from a small notch. Rounded corners are preferred for an inline cable pod.

## 2. Functional partition

Use a left-to-right or top-to-bottom partition that is immediately understandable under inspection:

```text
 HOST / FTDI EDGE       ISOLATION CORRIDOR       TARGET / STOVE EDGE

 J101, F101,            U101 digital isolator    U102, U103,
 host test pads,        U104 optocoupler          JP201, JP301,
 R101/R102                                         J201 J3,
                                                    J202 J5,
                                                    J203 PICkit,
                                                    target test pads
```

J203 belongs entirely to the target domain even though it connects to an external USB tool. Its copper, labels, and access must not imply that it is protected by the UART isolation barrier.

## 3. Isolation corridor

- Provide a continuous all-copper-layer no-copper corridor at least 8 mm wide between host and target domains.
- The corridor shall extend to the board edges or to verified isolation slots so a copper path cannot go around it.
- Only U101 and U104 may bridge the corridor.
- No copper pour, trace, via, thermal spoke, test point, fiducial, mounting pad, metal fastener, shield, or exposed conductive label may cross or narrow it.
- Keep host and target silkscreen legends visually distinct and mark the corridor on both sides.
- Solder mask is not counted as the sole insulation distance.
- Actual creepage and clearance must be measured from finished fabrication outputs and the selected packages, not inferred from a nominal rectangle.

The 8 mm target is a conservative project layout rule. It is not a regulatory classification or evidence that all appliance conditions are touch-safe.

## 4. Connector placement

### J101 FTDI

- Place on the host edge.
- Prefer side-entry JST XH so the FTDI pigtail exits parallel to the PCB.
- Keep pin 1 and the black/red/orange/yellow/green order visible after enclosure assembly.
- Provide strain-relief anchor space independent of the connector solder joints.

### J201 and J202 target harnesses

- Place on the target edge.
- Use different contact counts and large `J3` / `MAIN J5` legends.
- Orient latches consistently but prevent a user from visually treating the two connectors as interchangeable.
- J201 pin 3 shall have a pad only as required by the connector; it shall have no trace, via, pour connection, or test point.
- J202 pin 1 shall have a prominent square pad/triangle matching the harness and controller square-pad convention.

### J203 PICkit

- Place close to J202 so MCLR, VDD, VSS, PGD, and PGC are short and direct.
- Keep the header outside the isolation corridor and entirely within the target region.
- Pin 1 must remain visible with a cable attached.
- Consider an enclosure key, recess, or keyed short adapter lead because a bare 1x6 header is reversible.
- Pin 6 shall be isolated from all copper except its own unconnected pad.

### JP201 and JP301

- Place both near the target edge and outside the isolation corridor.
- Provide enough finger/tool access to move a shunt without pulling a target cable.
- Orient both so pins 2-3 PARK is the same physical direction if that does not create ambiguity.
- Print the active and park positions rather than only the reference designator.
- Use different shunt colors in the assembly specification.

## 5. Component placement

- Put F101 and host decoupling immediately after J101 VCC.
- Put U101 across the isolation corridor, with host and target decoupling on their respective sides.
- Put U102 adjacent to J201; keep the two 330 ohm J3 series resistors between U102 and the connector.
- Put U103 and its pull-up/pulldown close to U102 output-enable pins.
- Put F201 and JP201 between J202 VDD and the target UART rail.
- Put U104 across the isolation corridor and R302/JP301 near J202 MCLR.
- Keep the direct J202-to-J203 ICSP bundle away from FTDI TX/RX and from the optocoupler LED current loop.
- Avoid routing PGC parallel to PGD for long distances; provide target-ground adjacency where practical.
- Keep all decoupling loops short and free of isolation-corridor detours.

## 6. Routing requirements

- Route the five direct ICSP signals first.
- Prefer no vias in MCLR/VPP, PGD, or PGC. If unavoidable, use one ordinary through via and document it.
- Keep J202-to-J203 direct-path copper short, with no test-point stub except the defined target pads placed close to the main route.
- Do not route an ICSP signal under U101/U104 or across the host region.
- Route host and target UART paths separately with local ground references on their own domains.
- Use solid host and target ground pours only if they cannot narrow the isolation corridor.
- Keep target UART output series resistors at the J201 edge.
- Keep reset optocoupler collector routing away from PGC/PGD and park-jumper stubs short.
- Provide adequate copper width for VDD/VSS even though the adapter does not intentionally power the whole board; PICkit pin 2 and pin 3 may carry target current.
- Apply conservative edge clearance around all exposed connectors and enclosure openings.

Preliminary trace targets, subject to review:

| Net class | Width |
| --- | ---: |
| ordinary UART/logic | 0.20-0.25 mm |
| target VDD/VSS and host 5 V | 0.40-0.60 mm |
| PICkit VDD/VSS direct path | at least 0.60 mm |
| isolation crossing | only package leads/pads; no free trace crossing |

## 7. Test access

Use exposed test pads, not fitted headers, to save cost and size. Host and target banks must be separated and clearly labeled.

- Test pads should accept ordinary spring probes or fine meter probes.
- Avoid placing a host test pad where a slipped probe can touch a target pad.
- Include ground pads at both ends of each bank.
- MCLR/VPP, PGC, and PGD pads must not add long stubs.
- The enclosure may require a removable service cover for test-pad access; production use should not require exposed copper.

## 8. Optional/DNP footprints

The PCB may reserve compact DNP footprints for:

- host power LED and resistor;
- target-ready LED and resistor;
- a reviewed two-line low-capacitance J3 ESD device;
- zero-ohm links replacing R101/R102 for waveform comparison; and
- one 0603 capacitor pad pair on each rail only if it does not encourage an unreviewed MCLR/PGD/PGC capacitor.

DNP footprints must not enlarge the board significantly, complicate isolation, or appear in the fitted-cost target.

## 9. Silkscreen and copper marking

Required visible text:

- `OPENMAXFIRE SERVICE ADAPTER REV A`;
- board serial or blank serialized-label field;
- `HOST` and `TARGET` domain names;
- `ISOLATION — NO COPPER` along the corridor;
- J101 wire/function abbreviations;
- `J3: 1 RX, 2 TX, 3 NC, 4 GND` from the stove's perspective;
- `9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5`;
- PICkit pins `1 VPP 2 VDD 3 VSS 4 PGD 5 PGC 6 NC`;
- JP201 `UART 1-2 / ICSP PARK 2-3`;
- JP301 `RESET ARM 1-2 / PARK 2-3`;
- pin-1 triangles for J101, J201, J202, J203, JP201, and JP301; and
- `NO FTDI + PICKIT TOGETHER`.

Critical pin-1 and NC markings should also exist in copper or mask artwork so they survive silkscreen omission or abrasion.

## 10. Enclosure concept

The preferred first enclosure is a small nonconductive two-piece clamshell or printed engineering enclosure:

- cables exit from opposing host and target ends;
- the PICkit header and two jumpers are accessible under a labeled service cover;
- normal UART use does not expose target-domain copper;
- strain relief clamps cable jackets, not individual conductors;
- no metal fastener bridges the isolation corridor;
- the enclosure prevents the PICkit plug from being shifted by one pin where practical;
- labels remain visible with cables installed; and
- ventilation is unnecessary if measured temperature rise remains negligible.

Heat-shrink-only encapsulation may be used for an early UART prototype, but not for a released dual-interface adapter because the jumpers, PICkit orientation, inspection, and replacement labels must remain accessible.

## 11. Fabrication review checklist

Before ordering any PCB:

- schematic/ERC passes with no unexplained errors;
- netlist is independently compared against `ELECTRICAL_DESIGN.md`;
- all exact footprints and pin numbers are compared with current manufacturer drawings;
- J101/J201/J202 latch direction and cable-face numbering are reviewed;
- J203 pin order is checked against the actual PICkit lead;
- all isolation distances are measured in copper, mask, drill, and outline outputs;
- J201 pin 3 and J203 pin 6 are verified completely unconnected;
- ICSP paths contain no unintended inline or shunt component;
- both shunts fail safe when absent or parked;
- Gerber, drill, solder-mask, paste, silkscreen, and board-outline files are visually inspected; and
- enclosure and harness CAD is checked against a printed 1:1 board drawing.
