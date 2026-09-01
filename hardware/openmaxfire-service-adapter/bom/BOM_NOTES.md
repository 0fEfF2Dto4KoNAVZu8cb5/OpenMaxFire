# Portable service adapter preliminary BOM notes

> **NOT FOR PURCHASING OR FABRICATION.** This BOM supports schematic capture and cost review. It is not a released approved-vendor list. Every row marked `TBD - production gate` requires an exact manufacturer part number, ratings, footprint, lifecycle, and approved supplier before ordering.

The machine-readable list is [`preliminary-bom.csv`](preliminary-bom.csv).

## 1. Cost target

The fitted Rev A electronics are intentionally limited to four active devices, two resettable fuses, one diode, ordinary passives, three polarized edge connectors, one PICkit header, and two jumper headers.

Planning target:

| Cost group | Small-quantity target |
| --- | ---: |
| isolation and active logic | USD 4.5-6.0 |
| protection and passives | USD 1.5-2.5 |
| adapter-side connectors/jumpers | USD 1.0-2.0 |
| **estimated fitted PCB components** | **USD 8-12** |

Excluded:

- PCB fabrication and assembly;
- enclosure, labels, and fasteners;
- genuine FTDI cable and PICkit;
- stove-end J3/J5 housings and contacts, which are not yet identified;
- cable wire, sleeving, strain relief, and crimp labor;
- test fixtures and programming equipment; and
- shipping, minimum-order quantities, reels, taxes, and distributor fees.

The price range is a design target, not a quotation. Availability and pricing must be refreshed immediately before release.

## 2. Locked functional parts

The following exact parts are the current baseline because they reproduce the essential service behavior from the full-controller design with minimal circuitry.

### U101 — ISO7721DWVR

Required properties:

- one channel in each direction;
- operation with independent host and target supplies around 5 V;
- non-`F` default-high outputs suitable for UART idle;
- reinforced isolation in the wide-body `DWV0008A` package; and
- sufficient creepage/clearance for the project's 8 mm partition target.

Do not substitute a two-forward-channel ISO7720, a default-low `F` suffix, a narrow package without reviewing the barrier, or a part whose powered-off/default behavior differs.

### U102 — SN74LVC2G126DCUR

Required properties:

- two non-inverting buffers;
- independent active-high output enables that may be tied together;
- 5 V operation;
- 5.5 V tolerant inputs;
- specified `Ioff` powered-off protection; and
- DCU/VSSOP-8 crossed output pinout verified against the current drawing.

A generic `74xx126` is not automatically equivalent. Package pin order and powered-off behavior are release-critical.

### U103 — TLV803EA42RDBZR

Required properties:

- 4.2 V falling threshold;
- active-low open-drain output;
- delayed release, nominal 200 ms class and 130 ms minimum class;
- SOT-23-3 `R` pinout; and
- defined low-voltage behavior adequate for the U102 output-enable network.

The `A`, `42`, and `R` portions of the order code are functional. A same-family device with a different delay, threshold, output type, or SOT-23 pinout is not a drop-in substitute.

### U104 — VOL618A-3X001T

Required properties:

- phototransistor output;
- low input-current CTR grade suitable for a few-milliampere FTDI RTS# LED drive;
- 80 V collector-emitter class;
- option-1 long-creepage LSOP-4 package; and
- verified pins 1 anode, 2 cathode, 3 emitter, and 4 collector.

The actual reset-low margin must be calculated at minimum CTR, maximum MCLR pull-up current, minimum VHOST, and temperature. Do not approve the part solely from its isolation voltage.

## 3. Protection parts

### F101/F201 — 0805L005/30YR

The preliminary fuse is a 50 mA hold-class resettable PPTC in 0805. It is chosen to keep the tiny auxiliary circuits from presenting an unlimited board fault while avoiding a series diode drop.

Required review:

- cold and maximum resistance;
- hold/trip current across temperature;
- trip time at available source current;
- voltage rating;
- recovery behavior;
- effect on U103 threshold and FTDI supply margin; and
- coordination with the FTDI output and Bixby target rail.

A PPTC is not a precision or instantaneous current limiter. If the available target fault current cannot trip F201 safely, the schematic must add or substitute a reviewed hard current-limiting element.

### D301 — 1N4148W-7-F

D301 is anti-parallel across the optocoupler LED. Verify physical pin 1/cathode orientation in the chosen SOD-123 footprint. It is not connected to MCLR or any direct ICSP signal.

## 4. Passive requirements

All fitted resistors should initially be 1% unless a reviewed calculation permits otherwise. Minimum voltage/power and temperature range must be frozen even for apparently ordinary UART resistors.

Critical calculations:

- R202/R203 supervisor-output divider at all leakage and logic-threshold corners;
- R301 optocoupler LED current and FTDI RTS# sink margin;
- R302 reset low level and MCLR/VPP isolation when parked;
- R204/R205 target short/contention current and UART noise margin;
- R206 target-derived idle pull-up loading; and
- R201 target auxiliary rail discharge time.

Capacitors:

- use X7R or better for ordinary 100 nF decoupling;
- use a voltage rating with comfortable margin above 5.5 V, with 16 V preferred where size/cost permits;
- qualify effective capacitance under DC bias for the 1 uF rail capacitors; and
- never add capacitance to MCLR/VPP, PGC, or PGD.

C103 is optional and should remain DNP unless layout distance or measured transient behavior requires it.

## 5. Connectors

### Adapter side

The baseline uses side-entry JST XH headers:

- J101: `S6B-XH-A(LF)(SN)`;
- J201: `S4B-XH-A(LF)(SN)`;
- J202: `S5B-XH-A(LF)(SN)`.

The corresponding cable housings are `XHP-6`, `XHP-4`, and `XHP-5`. The exact SXH contact must be selected for the released wire gauge and insulation diameter.

These references are adapter-side parts only. Do not purchase them as assumed stove-end mates.

### PICkit header

J203 baseline is Würth `61300611121`, a straight 1x6, 2.54 mm through-hole header. A lower-cost equivalent may be approved after pitch, pin dimensions, plating, board retention, mating cycles, and pin-1 visibility are checked. Pin 6 remains unconnected regardless of supplier.

### Jumper headers and shunts

JP201 and JP301 should be low-profile 1x3, 2.54 mm through-hole headers. Freeze:

- header height and shroud/no-shroud choice;
- shunt contact resistance and retention;
- two visibly distinct shunt colors;
- enclosure clearance; and
- a storage method that leaves each shunt fitted in PARK rather than loose.

## 6. DNP options

The following are not populated in the baseline cost or power budget:

- D101/R103 host power LED;
- D201/R207 target-ready LED; and
- D202 two-line J3 ESD device.

Reasons:

- LEDs consume a material fraction of the tiny target interface current budget and are not necessary for function.
- A generic ESD part can add leakage/capacitance or clamp to an unqualified rail. The correct device depends on measured J3 levels and transient tests.

The PCB may reserve footprints, but a released BOM must explicitly say `DNP` unless qualification changes the baseline.

## 7. Harness and enclosure BOM separation

Do not mix the PCB assembly, harness, enclosure, and external tools into one purchasing row. Release four controlled lists:

1. PCB assembly BOM;
2. FTDI, J3, and J5 cable/harness BOM;
3. enclosure, labels, strain-relief, shunts, and packaging BOM; and
4. required service equipment list identifying compatible PICkit and FTDI models.

The target-end J3 and J5 connectors are release blockers until positively identified. No generic marketplace `JST-style` listing is an approved substitute.

## 8. Alternate-part policy

No alternate is approved merely because its description says:

- digital isolator;
- dual buffer;
- 4.2 V reset;
- optocoupler;
- JST XH compatible; or
- PICkit header.

An alternate must equal or improve every relevant property:

- electrical function and default state;
- pinout and package;
- supply range and logic thresholds;
- powered-off leakage/backfeed behavior;
- propagation delay and UART margin;
- isolation rating, creepage, clearance, and certifications;
- CTR and reset-low margin;
- temperature range and lifecycle;
- land pattern and assembly capability; and
- current stock from an authorized supplier.

Revalidate the affected partial-power, UART, reset, and ICSP tests after any active, protection, connector, or isolation substitution.

## 9. Purchasing release checklist

- Replace every `TBD - production gate` with an exact manufacturer and orderable part number.
- Record manufacturer datasheet revision and approved distributor SKU.
- Confirm active lifecycle status and realistic small-quantity stock.
- Compare every package drawing and recommended land pattern with the schematic/PCB footprint.
- Freeze resistor tolerance/power and capacitor dielectric/voltage/effective capacitance.
- Select wire, contacts, crimp tooling, pull-test limits, and strain relief.
- Identify the exact stove-end connector families from physical evidence.
- Generate separate prototype and production quantities.
- Recalculate fitted cost without DNP items and without silently excluding required shunts.
- Obtain independent BOM and polarity review before ordering.
