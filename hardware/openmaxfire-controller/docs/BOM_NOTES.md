# Full-Controller BOM Notes — NOT FOR PURCHASING

> **NOT FOR PURCHASING, ASSEMBLY, OR PRODUCTION.** This is a reconciled
> engineering BOM, not a released AVL. Rows with exact source-selected MPNs
> still require the listed footprint, electrical, lifecycle, sourcing, and
> validation gates. Rows marked `TBD — production gate` are intentionally
> incomplete and must not be ordered by description alone.

Status: **engineering preliminary; source-reconciled 2026-09-01**

The PCB assembly BOM is [parts.csv](../bom/parts.csv). It is derived from every placed source component in `src/*.tsx` for the OpenMaxFire full controller. It intentionally does not include the PCB fabrication item, enclosure, fasteners, ESP32 antenna/cable, external FTDI or PICkit tools, stove-end connectors, cable assemblies, crimp tooling, or field sensors unless noted as a mating/accessory requirement.

## Reconciliation summary

The current source snapshot contains 250 source references and the CSV accounts for all of them exactly once. Thirty-three references are bare PCB test pads rather than purchased components, so the fitted/purchased component count is 217:

| Source component class | Count |
|---|---:|
| Capacitors | 48 |
| Resistors | 97 |
| Connectors | 12 |
| Chips, modules, MOSFETs, relay and mode switch | 43 |
| Discrete diodes | 9 |
| LEDs | 3 |
| Inductors | 2 |
| Pushbuttons | 2 |
| Fuse | 1 |
| Bare PCB test pads | 33 |
| **Total source references** | **250** |

The CSV has 87 line items, including one explicitly non-procured PCB-feature line for all test pads. Its `Qty` total is 250, its reference list contains 250 unique designators, and automated comparison with the current source snapshot found no missing, duplicate, or extra references. Every line's `Qty` equals the number of listed designators. All 79 references with a source-authored manufacturer part number match the BOM MPN exactly, and all 147 source-authored resistor, capacitor, and inductor values match their BOM rows.

This accounting completeness must not be confused with procurement completeness: 31 BOM lines covering 138 fitted references still have `TBD — production gate` in the MPN field. They are predominantly commodity passives and LEDs whose exact tolerance, dielectric/tempco, voltage or power rating, lifecycle, and approved supplier still need to be frozen.

Passives are combined only where the source-authored value, package, voltage/rating field, tolerance field, and exact-MPN status match. A missing tolerance is treated as unresolved, not as 1% or 5%. Thus R2/R4 and R654 (100 kΩ, explicit 1%) are separate from generic 100 kΩ resistors; R653 is correctly recorded as 20 kΩ/1%; and 100 nF/10 V capacitors remain separate from 100 nF/16 V capacitors. Exact source-selected capacitors such as C8 are not merged into unresolved rows of the same nominal value. Repeated active parts are combined only when MPN and footprint source match. U305/U306/U405 now share the same source-defined TI DCU0008A footprint and are intentionally combined.

The reconciliation removes obsolete U303, C307, and C605 entries and adds C10, C505, C608–C610, R104, R300, R315, R411, R504, R622, R659/R660, Q601–Q603, U504, U607/U608, and U609. It also corrects the earlier R306, connector-side R651, R653/R654, C2, C501, D301/D302/D402, K501, and U603–U606 descriptions. These are accounting corrections, not authorization to purchase.

Only supplier data explicitly authored in source is treated as authoritative. At present that is JLCPCB `C97502` for U201. Other JLCPCB candidates emitted by tscircuit's part search are deliberately excluded: they are search suggestions, not approved manufacturer parts, and their tolerance, dielectric, voltage, footprint and lifecycle have not been qualified.

## Meaning of a production gate

`TBD — production gate` means the row is adequate for circuit intent and reference accounting but may not be purchased or substituted until an exact orderable part and its requirements are frozen. `FIT` means the source currently intends to populate that reference; it does **not** mean purchasing release. Closing a gate requires a reviewed manufacturer datasheet, current lifecycle/stock check, footprint-to-package comparison, assembly capability check and—where relevant—bench or compliance evidence.

The most important open gates are:

1. **Every unresolved passive:** freeze manufacturer MPN, tolerance, voltage/power rating, dielectric or tempco, temperature range and derating. Qualify effective capacitance at operating DC bias where applicable. Exact source-selected parts still require lifecycle, land-pattern, derating, and availability review. C501 is now an exact 22 nF, 5%, C0G part; independently sign off the documented 1.51–2.02 s watchdog interval.
2. **Input protection:** F1 is now the exact `1812L150/24DR` resettable PTC, D1 is `SMBJ15A-13-F`, and D3 is `PMEG6030EP,115`. This closes the former part-number gaps but not the engineering gate: validate available fault current, PTC trip/hold behavior and temperature derating, TVS surge/clamp energy, D3 forward drop/thermal rise, and coordination with U2 absolute maxima.
3. **Controls and indicators:** SW101/SW102 are now exact `B3U-1000P` parts and footprints. D2, D101, and D303 remain generic LEDs; freeze polarity, Vf, intensity bin, temperature behavior, and drive-current pairing.
4. **Custom or generated footprints:** U2 now implements the source-defined TI RPW0010A recommended HotRod land pattern instead of the incompatible symmetric QFN placeholder. K501 now uses 1.0 mm drills. Neither change is self-certifying: compare generated copper/mask/paste and pin numbering against current package drawings and received parts. Also validate U201 (TI DRT/JLC C97502), J201, SW301, U501, U601, U607/U608, J403, U4, and all TI DCU footprints. U404's wide-body isolation footprint must preserve certified creepage geometry.
5. **Isolation:** retain the source-defined 8 mm no-copper strip through all copper layers. Recheck creepage and clearance after pours, vias, mask openings, silkscreen, mounting hardware and enclosure details are final. Only U401/U404/U406/U407 may bridge it.
6. **J5 mapping:** J402 remains blocked until a second independent continuity pass on an actual stove controller/harness confirms pins 1–5 as MCLR, VDD, VSS, PGD and PGC. J403 must be checked against that same mapping before connecting a PICkit.
7. **Thermostat fail-back:** K501's source footprint is corrected to 1.0 mm drills with 1.8 mm lands. Verify received-part fit, contact/coil ratings, NC/NO pinout, bottom-view transformation, relay order code, de-energized continuity, and contact life. Release controlled drawings and continuity tests for both the J501 passive bypass accessory and J502 normally closed force-backup loop.
8. **Mode selector:** continuity-test an incoming `SS-43D28-G 6 NS` in all three positions, verify break-before-make behavior and reconcile the 20 terminal numbers with the custom footprint before assembly.
9. **Accessory interfaces and power-off isolation:** freeze cable pinout drawings, wire gauges, strain relief and ESD test conditions. J603 is 0–3.3 V SELV only; it is not 12 V, mains or stove-target tolerant. The J601/J602/J603 rail is a shared, firmware-enabled, current-limited 3.3 V rail, not a safety supply. Validate U607/U608 Ioff behavior and channel mapping, U609 threshold/delay, the Q601–Q603 series OE interlock, and the TI ESDS304 ground-only protection topology under startup, shutdown, overload, disconnected-controller, and externally driven cable tests.
10. **RF and mechanics:** select the ESP32-S3 external antenna/cable, preserve its RF keepout and verify all connector insertion paths, enclosure openings and service access.
11. **Test access:** TP101–TP124 and TP201–TP209 are 1.6 mm exposed copper pads, not fitted components. Freeze mask opening and finish, verify fixture probe access/clearance and keep controller- and target-domain fixture wiring isolated.
12. **Current-limit and analog qualification:** U303 has been removed; U609's A29 threshold now qualifies only the switched expansion rail. U301's broad TPS2553 active-limit tolerance is backed by the exact 82 Ω/2512/1% R300 ceiling, intended to keep cable current below 68 mA; independently prove that limit and thermal behavior. Validate U602's 173.7–233.9 mA range and fault energy. Complete the R653/R654/C606 auxiliary-ADC divider, acquisition-time, leakage, clamp-current, and tolerance error budget.

## Connector mating and harness notes

Mating items below are harness/accessory parts and are not included in the PCB-assembly quantity. Contact options are wire-gauge alternatives within the same connector family, not blanket substitutes. The harness drawing must select exactly one contact, wire, insulation diameter and approved crimp process.

| PCB reference | Board header | Mating housing / accessory | Contact and key notes |
|---|---|---|---|
| J1 | JST `B2P-VH-B(LF)(SN)` | `VHR-2N` | `SVH-21T-P1.1` for #22–18 AWG or `SVH-41T-P1.1` for #20–16 AWG; choose after current and insulation review. |
| J501 | JST `B4P-VH-B(LF)(SN)` | `VHR-4N` | Same VH contact choices. A separately controlled passive bypass joins 1–3 and 2–4. |
| J301 | JST `B6B-XH-A(LF)(SN)` | `XHP-6` | `SXH-001T-P0.6` for #28–22 AWG or `SXH-002T-P0.6` for #30–26 AWG. Preserve the source cable colors; CTS_N is NC. |
| J401 | JST `B4B-XH-A(LF)(SN)` | `XHP-4` | Select an SXH contact for the actual gauge. Pin 3 is deliberately NC. Stove-end mate is still TBD. |
| J402 | JST `B5B-XH-A(LF)(SN)` | `XHP-5` | Select an SXH contact for the actual gauge. Do not build until the J5 mapping gate is closed; stove-end mate is still TBD. |
| J502 | JST `B2B-XH-A(LF)(SN)` | `XHP-2` closed-loop harness | Two SXH contacts and a controlled wire loop, or an approved XH-family assembly, must ship normally closed. This is not a standard 2.54 mm board jumper. |
| J601 | JST `B16B-PH-K-S(LF)(SN)` | `PHR-16` | `SPH-002T-P0.5S` for #30–24 AWG or `SPH-004T-P0.5S` for #32–28 AWG. Verify duplicated power/ground contact current sharing. |
| J602 | JST `B3B-PH-K-S(LF)(SN)` | `PHR-3` | Same PH contact choices; lock the sensor pinout in a harness drawing. |
| J603 | JST `B5B-PH-K-S(LF)(SN)` | `PHR-5` | Same PH contact choices; label the harness 0–3.3 V SELV only. |
| J201 | GCT `USB4105-GF-A` | Standards-compliant USB Type-C plug/cable | No proprietary crimp housing; verify shell/stake option and enclosure retention. |
| J403 | Würth `61300611121` | 1x6, 2.54 mm female PICkit lead/tool | Exact cable/socket assembly TBD. Pin 6 is NC. Validate pin 1 at both ends. |
| J404 | Harwin `M20-9990245` | Standard 2.54 mm shorting shunt, exact MPN TBD | Header is fitted; shunt is explicitly **not fitted by default** and must be controlled as an accessory. |

Primary connector-family references: [JST VH](https://www.jst-mfg.com/product/pdf/eng/eVH.pdf), [JST XH](https://www.jst-mfg.com/product/pdf/eng/eXH.pdf), [JST PH](https://www.jst-mfg.com/product/pdf/eng/ePH.pdf), [Würth 61300611121](https://www.we-online.com/components/products/datasheet/61300611121.pdf), and [Harwin M20-9990245](https://www.harwin.com/products/M20-9990245/).

## Alternate-part policy

No alternate silicon, connector family, relay, mode switch, fuse or safety/isolation component is presently approved. A lower-cost part is acceptable only after the BOM row's electrical behavior, pinout, package/land pattern, temperature/lifecycle and regulatory constraints are shown equal or better. Similar marketing descriptions or tscircuit/JLC search matches are insufficient.

For commodity passives, a second source may be approved after the exact baseline specification is frozen. The alternate must match package, value, voltage/power, tolerance, dielectric/tempco, temperature range and any function-specific properties such as DC-bias capacitance, ESR, pulse capability, leakage or high-frequency parasitics. TI tape-quantity suffix changes may be accepted only when TI's ordering information proves the device, package and finish are identical; that is a packaging change, not authorization for alternate silicon.

## Release checklist

- Replace every `TBD — production gate` with a manufacturer and complete orderable MPN.
- Record approved distributor/SKU, lifecycle state, MOQ/reel implications and current quotation without replacing the manufacturer MPN.
- Attach the selected datasheet revision and a footprint comparison for every package gate.
- Re-run schematic/ERC, placement/DRC, isolation and net-short checks on the exact release commit.
- Build the PCB, harness and accessory BOMs as separate controlled documents; add test-point, label, packaging and programming requirements as separate manufacturing artifacts.
- Perform incoming inspection and continuity fixtures for SW301, K501, J501 bypass, J502 loop, J3/J5 cables, PICkit header and auto-reset shunt policy.
- Execute the project validation plan before changing this document from preliminary to released.

## Source snapshot and audit evidence

The 2026-09-01 reconciliation used the complete controller entry point and every `src/*.tsx` file, including shared footprint/component helpers. SHA-256 values make later source drift visible:

| Source | SHA-256 |
|---|---|
| `index.circuit.tsx` | `bf90e9bd9e32f8216f59602fad77ec1bf02d3774f99cd04f957035624ce54825` |
| `src/cathode-pin1-diode.tsx` | `a7fd7c900da780ae6a8960993ca7af791a44650473083826af5176e5844ebdb3` |
| `src/expansion.tsx` | `5353ba6df0b75792c12a1e563ca87b7b17ef053bbf0af40b3132cee6072c082d` |
| `src/mode-service.tsx` | `ac80d04762799ab9a2dd3cb1a8576f75983821da331cf244d8921ecbf6a247e1` |
| `src/power.tsx` | `ecde6908596cd2bb50f58f118bab8028fb27d1ff71a0dc09c1b16755d35e7fe2` |
| `src/processor.tsx` | `fb32f8c74ab16f304119fe20ff1a727c048997840e468b21d7992a407df2039d` |
| `src/safety.tsx` | `0c20639cb5feb6d657b2d58f481d2a2713573259f2b8e833b506ca1ae298ed4e` |
| `src/target-service.tsx` | `67b7841ac8da663310b16af964130fca71082cf6dcbd58b55e34a3dadad040f4` |
| `src/testpoints.tsx` | `9eab91f224868f6bcc41b22cf0bb013ed69c3a356f92d229994d6bb94517229f` |
| `src/ti-dcu0008a-footprint.tsx` | `db747e63c6e4fce6af8cea4c2e1ca1d2b4d24bdd16eed0e2c5d1832edd57c2a5` |
| `src/usb.tsx` | `1f2b88eae19b6dc01139a2f3b98b05f32a6f5d576ed6a0c84cc1a31d3ec8e96c` |

The audit checks performed on this snapshot were:

- CSV syntax: 17 columns on all 87 data rows.
- Quantity integrity: every row's `Qty` equals its reference-list length; total 250.
- Reference integrity: 250 unique source designators; zero missing, extra, or duplicated references.
- Procurement count: 250 total minus 33 fabricated test pads equals 217 fitted/purchased references.
- Attribute integrity: zero mismatches across 79 source-authored MPN references and zero mismatches across 147 source-authored R/C/L values.
- Targeted package reconciliation: TI RPW0010A for U2; 1.0 mm relay drills for K501; SOD-123F for D301/D302/D402; SOT-23-5 for U603–U606; exact TI DCU0008A footprint grouping; and exact packages for U504, U607/U608, and U609.

Any source hash change invalidates these counts and requires rerunning the reconciliation before this BOM can advance toward release.
