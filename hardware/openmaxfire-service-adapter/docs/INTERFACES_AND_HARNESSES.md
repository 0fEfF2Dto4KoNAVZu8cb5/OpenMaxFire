# Portable service adapter interfaces and harnesses

Status: preliminary controlled-interface definition; stove-end connector families remain open gates

## 1. Interface inventory

| Ref. | Adapter-side connector | Purpose | Mating item |
| --- | --- | --- | --- |
| J101 | JST XH six-position, side-entry preferred | genuine FTDI cable | `XHP-6` with qualified SXH contacts |
| J201 | JST XH four-position, side-entry preferred | stove J3 harness | `XHP-4`; target-end connector TBD |
| J202 | JST XH five-position, side-entry preferred | `9067-0604` main-board J5 harness | `XHP-5`; target-end connector TBD |
| J203 | 1x6, 2.54 mm straight through-hole header | PICkit | standard PICkit female lead/tool |
| JP201 | 1x3, 2.54 mm header plus shunt | UART power / ICSP park | controlled shorting shunt |
| JP301 | 1x3, 2.54 mm header plus shunt | reset arm / park | controlled shorting shunt |

JST XH is selected only for the adapter side because it is inexpensive, polarized, readily available, and large enough for hand inspection. This choice does not assert that the stove connectors are JST XH.

## 2. J101 FTDI input

The released FTDI harness shall be made for the genuine `TTL-232R-5V-WE` cable already validated in the project.

| J101 pin | FTDI conductor | Function | Board net |
| ---: | --- | --- | --- |
| 1 | black | ground | `GND_HOST` |
| 2 | red | +5 V cable output | `VHOST_RAW` |
| 3 | orange | TXD | `FTDI_TXD` |
| 4 | yellow | RXD | `FTDI_RXD` |
| 5 | green | RTS# | `FTDI_RTS_N` |
| 6 | brown | CTS# | no connection |

Construction requirements:

- Verify every conductor by continuity and the FTDI manufacturer's current cable drawing before crimping.
- Do not infer conductor function from color on a generic cable.
- Insulate and strain-relieve the cable jacket before the individual conductors reach the housing.
- The CTS# contact may be omitted from the housing; if installed, J101 pin 6 shall have no PCB copper beyond its pad.
- The harness label shall include FTDI model, cable serial number, adapter revision, and pin-1 orientation.

## 3. J201 stove J3 harness

### 3.1 Adapter-side map

| J201 pin | Stove J3 pin | Function | Suggested wire color |
| ---: | ---: | --- | --- |
| 1 | 1, square pad | adapter TX to stove RX | orange |
| 2 | 2 | stove TX to adapter RX | yellow |
| 3 | 3 | deliberate no-contact/no-conductor | none |
| 4 | 4 | target signal ground | black |

The empty third cavity is a required safety and compatibility feature. J3 pin 3 has been passively traced toward PIC VDD but has not been qualified as a supply. Neither the adapter PCB nor the harness may contact it.

### 3.2 Target-end requirements

The target-end connector is not yet identified by manufacturer or family. Before release:

- measure pitch, housing dimensions, latch/key geometry, contact dimensions, and wire range;
- compare against manufacturer drawings rather than online appearance;
- obtain the exact housing and crimp contact from an authorized source;
- verify mating insertion force and retention on a spare controller;
- photograph cable-face and board-face pin numbering;
- prove cavity 3 is empty and insulated; and
- use a housing that cannot fit main-board J5 or an igniter connector.

The target label shall read `9067-0604 MAIN BOARD — J3 COMPUTER PORT`.

## 4. J202 main-board J5 harness

### 4.1 Adapter-side map

| J202 pin | Main-board J5 | Function | Suggested wire color |
| ---: | ---: | --- | --- |
| 1 | 1, square pad | MCLR/VPP | violet or white |
| 2 | 2 | VDD/target sense | red |
| 3 | 3 | VSS/target ground | black |
| 4 | 4 | PGD/ICSPDAT | blue |
| 5 | 5 | PGC/ICSPCLK | green |

Suggested colors are subordinate to the numbered drawing and serialized continuity record.

### 4.2 Mandatory identity label

Both ends of the J5 harness and the enclosure shall state:

`9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5`

No shortened `J5`-only label is acceptable.

### 4.3 Target-end requirements

The exact mating connector remains unknown. Release requires:

- independent confirmation that the same PCB is marked `9067-0604` and carries the PIC16F877A;
- exact five-contact housing and contact identification;
- square-pad pin-1 documentation;
- second-person continuity from each connector contact to PIC MCLR, VDD, VSS, RB7, and RB6;
- adjacent-contact and housing-key inspection;
- strain relief that prevents a cable pull from reaching the controller header; and
- a mechanical/color strategy that makes the J5 tail unmistakable from J3 and all igniter wiring.

## 5. J203 PICkit header

| J203 pin | PICkit signal | J202 pin |
| ---: | --- | ---: |
| 1 | VPP/MCLR | 1 |
| 2 | VDD target sense/source | 2 |
| 3 | VSS | 3 |
| 4 | PGD/ICSPDAT | 4 |
| 5 | PGC/ICSPCLK | 5 |
| 6 | AUX/PGM | no connection |

Requirements:

- use the conventional PICkit order without mirroring;
- place a permanent triangle and `1` at pin 1 on copper/silkscreen;
- make orientation visible after enclosure assembly;
- prefer a keyed adapter lead or enclosure recess even if the PCB header is unshrouded;
- leave pin 6 without trace, via, test point, or plane connection; and
- keep pins 1-5 direct to J202.

## 6. Configuration jumpers

### JP201 — target UART power

```text
[1 UART SOURCE] [2 VTGT_AUX] [3 PARK/NC]
```

- Shunt 1-2: UART target electronics powered from protected J5 VDD.
- Shunt 2-3: ICSP/PARK; UART target electronics disconnected.
- Shunt absent: safe/off.

Silkscreen shall show `UART 1-2` and `ICSP/PARK 2-3` on both sides where possible.

### JP301 — automatic reset

```text
[1 RESET SINK] [2 MCLR] [3 PARK/NC]
```

- Shunt 1-2: reset armed for an attended J3 loader-entry operation.
- Shunt 2-3: PARK; optocoupler disconnected from MCLR.
- Shunt absent: reset sink disconnected.

Silkscreen shall show `ARM 1-2` and `PARK 2-3`. The normal storage and operating position is PARK.

The two headers should use different shunt colors or prominent legends. A shunt shall never be stored loose inside the enclosure.

## 7. Harness lengths

Preliminary limits, subject to waveform testing:

| Harness | Initial prototype target | Release maximum without retest |
| --- | ---: | ---: |
| FTDI loose-wire section to adapter | 150 mm | 300 mm |
| Adapter to J3 | 300 mm | 500 mm |
| Adapter to main-board J5 | 200 mm | 300 mm |
| PICkit header lead | shortest practical | 150 mm preferred |

The PICkit path is the most length-sensitive. If the adapter and J5 harness exceed the preferred length, PGC/PGD and VPP waveforms must be requalified at the actual length.

## 8. Wire and crimp requirements

- Use stranded copper wire within the selected contact's qualified gauge and insulation-diameter range.
- Initial target is 26-28 AWG for signal harnesses, subject to contact availability and voltage-drop review.
- Use manufacturer-approved or independently validated crimp tooling.
- Record pull-test acceptance for the released crimp process.
- No solder-tinned conductor may be inserted into a crimp barrel intended for bare stranded wire.
- Splices, loose Dupont ends, alligator clips, and unlabeled ribbon cable are prohibited in a released harness.
- Bundle J3 and J5 separately; do not use one split target housing that could shift by one cavity.

## 9. Serialized end-to-end cable test

Every completed harness shall receive a serial number and pass:

1. connector identity and part-number inspection;
2. cable-face versus board-face pin-number verification;
3. end-to-end resistance for every populated conductor;
4. open-circuit confirmation for every omitted/NC position;
5. adjacent-pin and all-pin-to-shield isolation;
6. target-housing key and retention inspection;
7. controlled pull/strain-relief inspection;
8. color and label verification; and
9. photograph of both connector faces with the serial number visible.

Suggested acceptance limits before target-specific refinement:

- each ordinary conductor: less than 1 ohm end-to-end;
- direct PICkit conductor set: resistance consistent within 0.2 ohm of one another;
- NC and adjacent conductors: greater than 20 megohms at the test voltage;
- no intermittent continuity during gentle flex and strain-relief test.

## 10. Enclosure labels

At minimum, the enclosure shall permanently show:

- `OPENMAXFIRE SERVICE ADAPTER`;
- hardware revision and serial number;
- `J3 UART` at J201;
- `9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5` at J202;
- PICkit pin 1 at J203;
- `UART 1-2 / ICSP PARK 2-3` at JP201;
- `RESET ARM 1-2 / PARK 2-3` at JP301;
- `NEVER CONNECT FTDI AND PICKIT TOGETHER`;
- `ICSP: CONTROLLER REMOVED, MAINS/HARNESSES DISCONNECTED`; and
- a link or QR code to the exact revision's operating procedure.

Labels must remain readable with every cable attached.
