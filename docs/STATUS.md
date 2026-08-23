# Research status

Snapshot date: 2026-08-23

OpenMaxFire separates evidence into five levels:

- **Vendor-documented**: stated in recovered Bixby documentation.
- **Direct photographic**: visibly established in a preserved photograph of
  serial 5215 or its installed hardware.
- **Statically confirmed**: visible in a preserved executable or firmware image.
- **Emulator-confirmed**: executed from preserved firmware under an explicitly
  incomplete synthetic hardware model.
- **Live-validated**: observed through preserved raw traffic on serial 5215's
  physical controller while cold/off.
- **Owner-reported**: reported by the stove owner but not independently measured.

## Established facts

| Area | Finding | Evidence |
| --- | --- | --- |
| Stove | Serial 5215; owner identifies model as MaxFire 115 | Nameplate photo / owner report |
| Owner manual | Factory installation, operating, and maintenance instructions, document `2020866 REV A`; embedded title identifies Model 115 | Vendor-documented / PDF metadata |
| Thermostat | Rev. A manual: unpowered on/off 24 V thermostat does not start the stove; while running, a call selects the chosen level and no call falls back to level 1 | Vendor-documented; later format-07 behavior still needs live validation |
| Safety interlocks | Door open about one minute causes shutdown; drawer open blocks startup/ash dump and about 20 minutes causes shutdown | Vendor-documented |
| Hopper sensing | Factory wiring diagram shows the hopper over-temperature switch but no hopper-level or hopper-lid sensor | Vendor-documented wiring diagram |
| Controller | Bare-board photographs directly show PCB `9067-0604`, PIC16F877A-I/P, and `10.000` MHz oscillator; December 2005 manufacture and assembly `12/15` remain owner-reported | Direct photograph / owner report |
| BixCheck pairing | 5.0.21→2.06/format 05; 5.5.00→2.70/07; 5.5.01→2.71/07 | Vendor package / EXE tables |
| Installed firmware | Serial 5215's controller reports firmware 2.02/data format 04 at 9,600 baud; this older pairing was absent from the preserved packages | Live-validated JSONL traffic |
| BixCheck internals | EXEs retain 640/655 COFF function symbols, source-unit names, and fixed tables | Reproducible PE/COFF analysis |
| PC serial | 5.0.21 uses 9,600; 5.5.x selects 9,600 or 19,200; all use 8N1; live 2.02 responds at 9,600 and not 19,200 | `async.cpp` methods plus live capture |
| Firmware | Four images target PIC16F877A and validate as Intel HEX | Deterministic firmware pipeline |
| Firmware identity | CR0B/CR0C constants encode 2.06, 2.70, and 2.71 | Cross-version disassembly |
| Requests | Reads are exactly 4 bytes, uppercase, with no terminator; live `CR00` was `43 52 30 30` | `regio()` plus live traffic |
| Responses | Addressed replies are six characters plus LF; firmware emits lowercase hex; live format-04 telemetry uses one-byte `Txxvv` and auxiliary `DWxxyy` lines | BixCheck/firmware paths plus live traffic |
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
| Physical inputs | Door=CR02.5 (1=open); drawer=CR02.6 (1=open); thermostat=CR06.2 (1=open); fuel=CR02.2 (1=corn); OFF/UP/DOWN=CR01 01/04/08; fan=CR09; feed=CR0A | Static/emulator mapping plus live one-at-a-time cold/off validation |
| J10 exhaust sensor | RA4/T0CKI falling-edge count is sampled into RAM 0x34 and returned as CR05 | Identical 2.06/2.70/2.71 producer signatures plus BixCheck exhaust predicates and board diagram |
| J9 feeder sensor | RD0 high-then-low wheel cycle is timed while RB1 is active; CR02.4 is current state and CR07 is the scaled interval | Identical 2.06/2.70/2.71 producer signatures plus BixCheck feed predicate and board diagram |
| A-unit storage | Firmware reads A00-AFF through PIC16F877A internal data EEPROM registers | Emulator events and bank-aware handler trace |
| J3/cable | J3-1=stove TX/PIC25, J3-2=stove RX/PIC26, J3-4=ground, J3-3 unresolved; FTDI TTL-232R-5V-WE wired without VCC exchanged valid traffic | Bare-board photographs, owner continuity, adapter inventory, live traffic |
| Board diagram | Online-found MaxFire pinout labels J3 and board subsystems; pictured PCB is 9067-0404 | Preserved image plus visible silkscreen; related-family evidence |
| Factory wiring | Owner-manual page 31 independently labels J3 and the major switches/sensors but gives no J3 pin functions or electrical levels | Vendor-documented; not a J3 electrical pinout |
| Input mux | CR01 button mux recovered; burn-drive switch=CR02.0; fuel selector=CR02.2 (`1`=Fuel A/corn, `0`=Fuel B/wood) | Identical 2.06/2.70/2.71 scanner, configuration-bank flow, BixCheck predicates, diagram labels |
| Python API | Version 0.6 adds an owned detected session, typed polling/iteration, configuration backup access, automated read-only Checkout, and simulator-only configuration/control/Checkout executors with authorization, full verification, interlocks, and cleanup; physical state-changing paths remain blocked | 116 portable offline tests, preserved serial 5215 replay fixtures, virtual endpoint, static analysis, and live read-only sessions |
| EEPROM | Three independent A00-AFF reads agree; checksum EFCE matches; format 04, model `Bixby Model 115`, stored serial `2060`, date string `01102007` | Live-validated backup and two raw traffic logs |
| Format-04 telemetry | ~3.58 s burst cycle; T03 fan trim, T04 feed trim, T06 firebox-related dynamic value, T08 flashing door/drawer warning bits, T0C bit 08 thermostat-open | Live A/B and A-B-A cold/off captures |

## Important unresolved items

| Question | Current position | Next evidence |
| --- | --- | --- |
| J3 pin 3 | Ground/TX/RX are live-validated; pin 3 remains unused/unresolved | Protected measurement and revision-specific tracing; do not connect |
| M/I families | Outer dispatch known; CW0D emits `I` plus LF, but general payload semantics remain unresolved | Deeper data-flow analysis or controlled capture |
| Board routing | Full 9067-0604 marking and both PCB sides are photographed; J3 continuity is owner-measured, but pin 3 and some under-component routing remain unresolved | Additional protected net tracing only as needed |
| Input wiring | Door/drawer/thermostat/fuel/buttons/pots are live-validated; CR02.1/CR02.7 and live J9/J10 behavior remain unnamed/unvalidated | Cold/off correlation or passive observation without actuator writes |
| Telemetry conversions | Later format-05/07 map is statically decoded; live format 04 differs and only several fields are correlated | Additional cold/off correlation, then operating capture under a separate safe plan |
| Table-only telemetry | BixCheck 5.5.01 names TFD-TFF, but no producer is recovered in periodic 2.71 firmware; T20 is a separate event path | Passive capture or newly identified conditional producer |
| EEPROM semantics | Live format-04 backup/checksum/identity are preserved; stored serial/date differ from the appliance nameplate and many calibration meanings rely on labels | Compare another format-04 unit or recovered 2.02 BixCheck/firmware |
| Checkout thresholds | Buttons, pots, doors, thermostat, exhaust CR05, feeder CR07, and igniter result bits are mapped; several engineering units/state meanings remain unresolved | Trace remaining manual/no-op cases and conversions |
| Downloader | Framing/identify mapped; erase/program acknowledgements and recovery unproven | Isolated emulation, then sacrificial bench controller only |

## Current boundary

Read-only J3 access is now established for serial 5215. The next safety boundary
is any state-changing command or operating-stove test: neither is authorized by
the cold/off session. Firmware 2.02 program memory remains unpreserved, J3-3 is
unresolved, and no recovery path has been proven on sacrificial hardware. The
version-0.6 API can own a detected session, run read-only Checkout, and execute
configuration/control/Checkout workflows against simulation, but known loader
markers and every physical state-changing service remain blocked. A matching
readback verifies a byte only, not physical actuator behavior or overall
controller safety.
