# Research status

Snapshot date: 2026-08-20

OpenMaxFire separates evidence into four levels:

- **Vendor-documented**: stated in recovered Bixby documentation.
- **Statically confirmed**: visible in a preserved executable or firmware image.
- **Emulator-confirmed**: executed from preserved firmware under an explicitly
  incomplete synthetic hardware model.
- **Owner-reported**: reported by the stove owner but not independently measured.

## Established facts

| Area | Finding | Evidence |
| --- | --- | --- |
| Stove | Serial 5215; owner identifies model as MaxFire 115 | Nameplate photo / owner report |
| Controller | PCB reported as 9067-0604, manufactured December 2005, assembly `12/15` | Owner report |
| BixCheck pairing | 5.0.21→2.06/format 05; 5.5.00→2.70/07; 5.5.01→2.71/07 | Vendor package / EXE tables |
| BixCheck internals | EXEs retain 640/655 COFF function symbols, source-unit names, and fixed tables | Reproducible PE/COFF analysis |
| PC serial | 5.0.21 uses 9,600; 5.5.x selects 9,600 or 19,200; all use 8N1 | `async.cpp` methods in all EXEs |
| Firmware | Four images target PIC16F877A and validate as Intel HEX | Deterministic firmware pipeline |
| Firmware identity | CR0B/CR0C constants encode 2.06, 2.70, and 2.71 | Cross-version disassembly |
| Requests | Reads are exactly 4 bytes, writes 6, uppercase, with no terminator | `regio()` in every EXE |
| Responses | Addressed replies are six characters; telemetry is five/seven; CR/LF terminates | BixCheck receiver and firmware TX paths |
| UART generation | SPBRG changes `0x40`→`0x20`; exact intended PC rates imply a 10 MHz oscillator | Firmware plus BixCheck DCB setup |
| Remote buttons | OFF=`CW0E11`, ON=`CW0E12`, UP=`CW0E14`, DOWN=`CW0E18` | All BixCheck tables/action paths |
| Telemetry | T00-T1C mapped; 5.5.01 adds T1E/TFD-TFF and moves virtual ash time to V1C | Decoded tables / `scanio()` |
| Configuration | Record layout, A-unit ranges, lean-burn transforms, and checksum decoded | All BixCheck EXEs |
| Checkout | 45 reachable tests; identical dormant 46th plate-motor record | Tables plus UI/dispatcher flow |
| Downloader | `CW0FC4` reset; `EA`/`EB` identify; `E3` blocks; `ED` completion | All EXEs / emulator identify probe |
| Emulator | All 45 CR reads and all 768 A-unit EEPROM reads complete through real 2.06/2.70/2.71 code; PICkit code emits `EB` for `EA` | Experimental PIC14 harness |
| Offline inputs | Door=CR02.5/RD1; drawer=CR02.6/RD4; thermostat=CR06.2/RB4; fan pot=CR09/AN3; feed pot=CR0A/AN4 | BixCheck masks plus firmware GPIO/ADC traces |
| A-unit storage | Firmware reads A00-AFF through PIC16F877A internal data EEPROM registers | Emulator events and bank-aware handler trace |
| J3/cable | Black four-pin connector location; factory cable P/N 2013324 | Vendor notes/manual |

## Important unresolved items

| Question | Current position | Next evidence |
| --- | --- | --- |
| J3 pinout/levels | Unknown; do not assume TTL or RS-232 | Continuity and protected voltage/polarity measurements |
| Oscillator | 10 MHz is strongly inferred, not physically checked | Read marking/frequency |
| Live framing | Software/emulator grammar is established; no electrical capture | Passive capture, then `CR00` only |
| M/I families | Outer dispatch known; payload semantics unresolved | Deeper data-flow analysis or controlled capture |
| Input wiring | Offline pin/bit assignments are strong; serial 5215 wiring and polarity remain untested | Cold/off polling while toggling one switch |
| Fuel select | CR02 bit 2 / RD3 mux slot is provisional; reachable 5.5 Checkout paths do not machine-check it | Selection-aware mux model or cold/off correlation |
| Telemetry conversions | Indexes/widths mapped; several numeric formulas unresolved | Trace display conversions, then correlate safely |
| EEPROM semantics | Internal storage, addresses/types/checksum, and read path mapped; many calibration meanings rely on labels | Read-only live backup, then field correlation |
| Checkout thresholds | Direct actions mapped; some result criteria/state bits unresolved | Continue `Analyze*Result()` reconstruction |
| Downloader | Framing/identify mapped; erase/program acknowledgements and recovery unproven | Isolated emulation, then sacrificial bench controller only |

## Current blocker

The J3 electrical interface has not been characterized. No command has been
validated against serial 5215. Findings are vendor-documented, static, or
explicitly labeled experimental emulation.
