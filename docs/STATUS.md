# Research status

Snapshot date: 2026-08-21

OpenMaxFire separates evidence into four levels:

- **Vendor-documented**: stated in recovered Bixby documentation.
- **Direct photographic**: visibly established in a preserved photograph of
  serial 5215 or its installed hardware.
- **Statically confirmed**: visible in a preserved executable or firmware image.
- **Emulator-confirmed**: executed from preserved firmware under an explicitly
  incomplete synthetic hardware model.
- **Owner-reported**: reported by the stove owner but not independently measured.

## Established facts

| Area | Finding | Evidence |
| --- | --- | --- |
| Stove | Serial 5215; owner identifies model as MaxFire 115 | Nameplate photo / owner report |
| Controller | Installed PCB suffix `-0604` corroborates owner-reported 9067-0604; December 2005 manufacture and assembly `12/15` remain owner-reported | Direct photograph / owner report |
| BixCheck pairing | 5.0.21→2.06/format 05; 5.5.00→2.70/07; 5.5.01→2.71/07 | Vendor package / EXE tables |
| BixCheck internals | EXEs retain 640/655 COFF function symbols, source-unit names, and fixed tables | Reproducible PE/COFF analysis |
| PC serial | 5.0.21 uses 9,600; 5.5.x selects 9,600 or 19,200; all use 8N1 | `async.cpp` methods in all EXEs |
| Firmware | Four images target PIC16F877A and validate as Intel HEX | Deterministic firmware pipeline |
| Firmware identity | CR0B/CR0C constants encode 2.06, 2.70, and 2.71 | Cross-version disassembly |
| Requests | Reads are exactly 4 bytes, writes 6, uppercase, with no terminator | `regio()` in every EXE |
| Responses | Addressed replies are six characters; physical firmware telemetry is one-byte `Txxvv`; CR/LF terminates | BixCheck receiver plus all firmware TX paths |
| UART generation | SPBRG changes `0x40`→`0x20`; exact intended PC rates imply a 10 MHz oscillator | Firmware plus BixCheck DCB setup |
| Remote buttons | OFF=`CW0E11`, ON=`CW0E12`, UP=`CW0E14`, DOWN=`CW0E18` | All BixCheck tables/action paths |
| Telemetry | All 91 periodic producer slots mapped/executed; logical 16-bit fields use adjacent big-endian T slots; 2.71 adds periodic T1E and event T20 | Decoded tables, firmware producers, emulator sender traces |
| Telemetry conversions | T00 C/F, pot trim, RPM, phase µs, 1/120-second feed values, timer units, and exact T09 display rules recovered | BixCheck update assembly and vendor manual |
| Operating state | T09 is RAM 0x4C; reset/cooldown/off/startup/operating/ramping/ash-dump handlers and structural transitions mapped in all generations | Firmware dispatcher/transition sites plus BixCheck display decoder |
| C writes | All CW00-CW0F handlers mapped in every generation; synthetic sweep reaches 48/48 handlers and 42 normal exits; CW05/CW0A are bounded model nonreturns | Firmware dispatch plus disposable-clone emulation |
| BixCheck workflows | Generic write lifecycle, logging schema/names, configuration reports, QuickCal/debug/flue/fuel UI construction recovered | Retained symbols, call graph, focused assembly |
| Configuration | Record layout, A-unit ranges, lean-burn transforms, and checksum decoded | All BixCheck EXEs |
| Checkout | 45 reachable tests; identical dormant 46th plate-motor record | Tables plus UI/dispatcher flow |
| Downloader | `CW0FC4` reset; `EA`/`EB` identify; `E3` blocks; `ED` completion | All EXEs / emulator identify probe |
| Emulator | 45 CR reads, 48 safe C writes, 91 periodic telemetry slots, and 768 A-unit EEPROM reads execute expected bounded paths through real 2.06/2.70/2.71 code; PICkit emits `EB` for `EA` | Experimental PIC14 harness |
| Offline inputs | Door=CR02.5/RD1; drawer=CR02.6/RD4; thermostat=CR06.2/RB4; fan pot=CR09/AN3; feed pot=CR0A/AN4 | BixCheck masks plus firmware GPIO/ADC traces |
| J10 exhaust sensor | RA4/T0CKI falling-edge count is sampled into RAM 0x34 and returned as CR05 | Identical 2.06/2.70/2.71 producer signatures plus BixCheck exhaust predicates and board diagram |
| J9 feeder sensor | RD0 high-then-low wheel cycle is timed while RB1 is active; CR02.4 is current state and CR07 is the scaled interval | Identical 2.06/2.70/2.71 producer signatures plus BixCheck feed predicate and board diagram |
| A-unit storage | Firmware reads A00-AFF through PIC16F877A internal data EEPROM registers | Emulator events and bank-aware handler trace |
| J3/cable | Black four-contact main-board connector and location; factory cable P/N 2013324 | Installed-board photographs plus vendor notes/manual |
| Board diagram | Online-found MaxFire pinout labels J3 and board subsystems; pictured PCB is 9067-0404 | Preserved image plus visible silkscreen; related-family evidence |
| Input mux | CR01 button mux recovered; burn-drive switch=CR02.0; fuel selector=CR02.2 (`1`=Fuel A/corn, `0`=Fuel B/wood) | Identical 2.06/2.70/2.71 scanner, configuration-bank flow, BixCheck predicates, diagram labels |

## Important unresolved items

| Question | Current position | Next evidence |
| --- | --- | --- |
| J3 pinout/levels | Unknown; do not assume TTL or RS-232 | Continuity and protected voltage/polarity measurements |
| Oscillator | 10 MHz is strongly inferred, not physically checked | Read marking/frequency |
| Live framing | Software/emulator grammar is established; no electrical capture | Passive capture, then `CR00` only |
| M/I families | Outer dispatch known; CW0D emits `I` plus LF, but general payload semantics remain unresolved | Deeper data-flow analysis or controlled capture |
| Board routing | Diagram depicts 9067-0404; serial 5215's `-0604` suffix corroborates the owner-reported 9067-0604, but the prefix and solder side are obstructed | Unobstructed full silkscreen, solder-side photographs, and continuity tracing around J3 |
| Input wiring | Offline assignments are strong; serial 5215 wiring and physical polarity remain untested; CR02.1 and CR02.7 are unnamed | Cold/off polling while toggling one switch; observe J9 only without energizing its motor |
| Telemetry conversions | Core formulas and T08/T09 display decoders are mapped; BixCheck itself leaves T12/T13 raw and only derives T14's mode number | Safe live correlation plus firmware bitfield tracing |
| Table-only telemetry | BixCheck 5.5.01 names TFD-TFF, but no producer is recovered in periodic 2.71 firmware; T20 is a separate event path | Passive capture or newly identified conditional producer |
| EEPROM semantics | Internal storage, addresses/types/checksum, read path, and CW01 checksum writes mapped; many calibration meanings rely on labels | Read-only live backup, then field correlation |
| Checkout thresholds | Buttons, pots, doors, thermostat, exhaust CR05, feeder CR07, and igniter result bits are mapped; several engineering units/state meanings remain unresolved | Trace remaining manual/no-op cases and conversions |
| Downloader | Framing/identify mapped; erase/program acknowledgements and recovery unproven | Isolated emulation, then sacrificial bench controller only |

## Current blocker

The J3 electrical interface has not been characterized. No command has been
validated against serial 5215. Findings are vendor-documented, static, or
explicitly labeled experimental emulation.
