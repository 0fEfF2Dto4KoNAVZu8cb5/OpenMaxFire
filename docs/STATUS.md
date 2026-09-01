# Research status

Snapshot date: 2026-09-01

OpenMaxFire separates evidence into five levels:

- **Vendor-documented**: stated in recovered Bixby documentation.
- **Direct photographic**: visibly established in a preserved photograph of
  serial 5215 or its installed hardware.
- **Statically confirmed**: visible in a preserved executable or firmware image.
- **Emulator-confirmed**: executed from preserved firmware under an explicitly
  incomplete synthetic hardware model.
- **Live-validated**: observed through preserved raw traffic on serial 5215's
  physical controller under the documented test condition.
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
| Spare-chip 2.06 identity | A separately PICkit-programmed controller reports exact firmware 2.06/data format 05/build 21 (`CR0B/CR0C=02/06`, `CR08=05`, `CR0E=21`) | Live read-only J3 capture |
| BixCheck internals | EXEs retain 640/655 COFF function symbols, source-unit names, and fixed tables | Reproducible PE/COFF analysis |
| PC serial | 5.0.21 uses 9,600; 5.5.x selects 9,600 or 19,200; all use 8N1; live 2.02 responds at 9,600 and not 19,200 | `async.cpp` methods plus live capture |
| Firmware | Five images across 2.02/2.06/2.70/2.71 target PIC16F877A and validate as Intel HEX | Deterministic firmware pipeline |
| Recovered 2.02 image | First complete original-chip export: all 8,192 program words, all 256 EEPROM bytes, User IDs, and config `0x3F32`; CP/CPD disabled; additional independent exports pending | Exact owner-supplied HEX plus preservation inspector |
| 2.02 provenance | Dump EEPROM is byte-identical to the independent 2026-08-22 J3 backup; protected loader `0x1E80`-`0x1FFF` is byte-identical to 2.06 PICkit | Deterministic section comparison |
| Firmware identity | CR0B/CR0C constants encode 2.02, 2.06, 2.70, and 2.71 | Cross-version disassembly and live 2.02 reads |
| Requests | Reads are exactly 4 bytes, uppercase, with no terminator; live `CR00` was `43 52 30 30` | `regio()` plus live traffic |
| Responses | Addressed replies are six characters plus LF; firmware emits lowercase hex; live format-04 telemetry uses one-byte `Txxvv` and auxiliary `DWxxyy` lines | BixCheck/firmware paths plus live traffic |
| UART generation | SPBRG changes `0x40`→`0x20`; exact intended PC rates imply a 10 MHz oscillator | Firmware plus BixCheck DCB setup |
| Remote buttons | OFF=`CW0E11`, ON=`CW0E12`, UP=`CW0E14`, DOWN=`CW0E18`; all four produced the expected physical response on firmware 2.02 | BixCheck tables/action paths plus preserved live control traffic and operator observations |
| Telemetry | All 113 periodic producer slots across 2.02/2.06/2.70/2.71 mapped/executed; logical 16-bit fields use adjacent big-endian T slots; 2.71 adds periodic T1E, while 2.06/2.70/2.71 share event T20 | Decoded tables, firmware producers, emulator sender traces, and live 2.06 capture |
| Telemetry conversions | T00 C/F, pot trim, RPM, phase µs, 1/120-second feed values, timer units, and exact T09 display rules recovered | BixCheck update assembly and vendor manual |
| Operating state | Firmware 2.02 emits state RAM 0x4C at T0C; later firmware emits it at T09. Live T0C `20`=Off and `30`=Prefill match exact dispatch families. 2.02 T09 reads unrelated RAM 0x2D and T15 is not a state source | Exact four-version firmware paths plus bounded live Off/Prefill evidence |
| C writes | The synthetic sweep reaches all 63 real handlers and 55 normal exits: CW00-CW0E in 2.02 and CW00-CW0F in 2.06/2.70/2.71. Original 2.02 CW0F falls into NOPs and has no C4 reset handler | Authenticated firmware dispatch plus disposable-clone emulation and 2.02/2.06 regression |
| BixCheck workflows | Generic write lifecycle, logging schema/names, configuration reports, QuickCal/debug/flue/fuel UI construction recovered | Retained symbols, call graph, focused assembly |
| Configuration | Record layout, A-unit ranges, lean-burn transforms, and checksum decoded | All BixCheck EXEs |
| Checkout | 45 reachable tests; identical dormant 46th plate-motor record | Tables plus UI/dispatcher flow |
| Downloader | Fixed 9,600 baud; approximately 200 ms reset window; `EA`/`EB` identify; `E3` blocks; `ED` completion. `CW0FC4` exists in 2.06+ but not original 2.02. BixCheck sends each PIC word high byte first; physical readback exposed and proved the former inverse host assumption | All EXEs, hash-pinned 2.02/2.06 images, resident loader disassembly, oscillator, emulator identify probe, and 2026-08-29 PICkit readback |
| Emulator | 58 real CR handlers, 63 safe C writes, 113 periodic telemetry slots, and 1,024 A-unit EEPROM reads execute expected bounded paths through real 2.02/2.06/2.70/2.71 code; PICkit emits `EB` for `EA` | Experimental PIC14 harness |
| Physical inputs | Door=CR02.5 (1=open); drawer=CR02.6 (1=open); thermostat=CR06.2 (1=open); fuel=CR02.2 (1=corn); OFF/UP/DOWN=CR01 01/04/08; fan=CR09; feed=CR0A | Static/emulator mapping plus live one-at-a-time cold/off validation |
| 2.06 physical inputs | On checksum-valid 2.06, one-at-a-time door/drawer/corn/thermostat actions changed CR02 `12→32`/`12→52`/`12→16` and CR06 `03→07`, with independent fields stable and all return edges captured | Continuous decoded monitor and exact traffic |
| J10 exhaust sensor | RA4/T0CKI falling-edge count is sampled into RAM 0x34 and returned as CR05; live 2.02 moved `00`→`0C` with the operator-observed blower and returned to `00` after OFF | Equivalent four-version producer paths, bounded live 2.02 correlation, BixCheck predicates, and board diagram |
| J9 feeder sensor | RD0 high-then-low wheel cycle is timed while RB1 is active; CR02.4 is current state and CR07 is the scaled interval. 2.02 pre-shifts the latch once; a bounded start/stop changed CR02.4 0→1 and CR07 `1E`→`1F`, then both remained stable for 20 Off cycles. The observed `1F` excludes the `2D` boot initializer and `16` range clamp, proving runtime latch execution | Equivalent four-version paths plus live 2.02 cycle-latch evidence; physical edge polarity, movement per edge, and time unit remain unverified |
| A-unit storage | Firmware reads A00-AFF through PIC16F877A internal data EEPROM registers | Emulator events and bank-aware handler trace |
| J3/cable | J3-1=stove RX/PIC26 with FTDI orange/TX, J3-2=stove TX/PIC25 with FTDI yellow/RX, J3-4=ground; J3-3 measures approximately 100 ohms to PIC VDD pins 11/32 and is provisionally nominal +5 V, with powered voltage unverified; adapter VCC remains disconnected. Bare FTDI completed 10 zero-write loader handoffs but entry remained nondeterministic. Its powered idle-high TX can plausibly backfeed the unpowered PIC; the waveform is not yet captured | Corrected continuity/wiring, follow-up owner-reported unpowered tracing, application traffic, corpus-wide `EA/EB` and `ED/E4` evidence, PIC/FTDI electrical specifications |
| Board diagram | Online-found MaxFire pinout labels J3 and board subsystems; pictured PCB is 9067-0404 | Preserved image plus visible silkscreen; related-family evidence |
| Factory wiring | Owner-manual page 31 independently labels J3 and the major switches/sensors but gives no J3 pin functions or electrical levels | Vendor-documented; not a J3 electrical pinout |
| Input mux | CR01 button mux recovered; burn-drive switch=CR02.0; fuel selector=CR02.2 (`1`=Fuel A/corn, `0`=Fuel B/wood) | Equivalent 2.02/2.06/2.70/2.71 scanners with version-specific RAM staging, configuration-bank flow, BixCheck predicates, diagram labels |
| Python API | Version 0.10 retains passive post-handoff readiness and deterministic complete-PICkit composition. The first physical `E3` exposed a shared host/simulator byte-order defect after `E7`; the corrected encoding is anchored to BixCheck assembly and strict simulation but remains physically untested. The CLI allows offline planning only, and public executors hard-reject every physical loader byte until a deterministic fixture is separately implemented and qualified | Portable tests, BixCheck assembly, exact J3 audit, full-image loader emulation, factory 2.06 golden reconstruction, session analyzer, hashes, and safety-lock regressions |
| Full-controller hardware | A fresh four-layer tscircuit Rev A implements ESP32-S3, complete J3/FTDI and provisional main-board J5/PICkit service paths, hardware watchdog/latch, released-state thermostat fail-back, protected power, USB, and disconnected-when-off expansion I/O. The corrected post-fix export has 250 components, 792 verified physical pad shapes, 77 verified explicit nets, and an 8 mm all-layer isolation keepout, with zero export coordinate or membership errors. It is not fabrication-ready and has no accepted final route | Source/netlist/placement checks, custom DSN boundary audit, and dated engineering checkpoint; physical qualification remains open |
| EEPROM | Three independent A00-AFF reads agree; checksum EFCE matches; format 04, model `Bixby Model 115`, stored serial `2060`, date string `01102007` | Live-validated backup and two raw traffic logs |
| 2.06 EEPROM | Two independent A00-AFF reads agree; format 05 and all vendor calibration/fuel bytes match, but modified identity bytes (`Unknown`, `08282026`) leave stored checksum `D168` unequal to calculated `576B`. `D168` exactly matches the intermediate serial-only edit, proving the date changed after checksum persistence | Live backups, checksum variants, vendor-byte comparison, and real-firmware checksum-path emulation |
| 2.06 checksum repair | One audited `CW0100` changed only A00/A01 `D168`→`576B`; two immediate full reads and one after AC-off/USB-out cold boot were byte-identical and valid. Identity/calibration remained unchanged and monitors had zero timeouts | Exact TX capture, three complete post-write backups, raw-byte diff, and cold-boot validation |
| Format-04 telemetry | ~3.58 s burst cycle; T03 fan trim, T04 feed trim, T06 firebox-related dynamic value, T08 flashing-light bitmap with lights 1/4/5/8 live-correlated to `01`/`08`/`10`/`80`, and T0C exact state family plus thermostat bit 08 | Exact 2.02 firmware, live A/B and state captures, control replay, and fault/start captures |
| 2.06 power-up cooldown | T09 changed `10`→`20`, T06/T18 fell to zero, and T04/CR05 tracked the observed fan coast-down. The exact CCP1/Timer1 setup and `0x1518` event threshold yield 877.893 s (~14m38s), matching the live power-up/Off interval | Exact firmware path, raw traffic, decoded monitor, and owner observation |
| 2.06 bounded start/cleanup | Physical ON produced checksum-valid T09=`30` Prefill, T07=`01`, T06=`19`, T18=`5C`, and live exhaust feedback. A first remote OFF was ignored; one retry produced repeated T09=`10` Cooldown. Passive monitoring then captured autonomous Off and fan coast-down; the exact 877.893-second prediction falls inside the preserved transition gap, and later T04/T05/T06/T18/CR05 were all zero with T07/T13 clear | Exact command traffic, decoded before/after captures, raw passive-transition traffic, and owner observation |
| Firmware preservation | Original 2.02 plus the post-J3 full read are preserved. The latter retains EEPROM/User IDs/config and all but three program words. A historical tool constructed a 2.06-program/format-04-data hybrid, but it is explicitly quarantined as unqualified and must not be imported or programmed | Two complete PICkit exports, exact section hashes, J3 audit, and offline tooling |
| Derived PICkit images | Five complete post-J3/pre-calibration predictions are generated from authenticated bases and Downloader sequences; the factory 2.06 Downloader→PICkit relationship reproduces every mapped byte as a golden check | Deterministic loader overlay, Intel HEX round-trip, section invariants, and hashes; physical spare readback comparison pending |
| Fault reporting | Format-04 T08 is an instantaneous flashing-indicator bitmap; the API retains bits across an eight-second observed stream window. Later BixCheck instead exposes T07 display LED, T09 state, and raw T13 Alarm mode | Live 2.02 light-1/light-4/light-5/light-8 captures plus static BixCheck reconstruction |

## Important unresolved items

| Question | Current position | Next evidence |
| --- | --- | --- |
| J3 pin 3 | Passively traced through approximately 100 ohms to PIC VDD pins 11/32 and the broad logic-supply net; nominal +5 V is strongly supported, but the powered voltage and source/load limits are unverified | Protected powered voltage/source characterization; do not connect or load |
| M/I families | Outer dispatch known; CW0D emits `I` plus LF, but general payload semantics remain unresolved | Deeper data-flow analysis or controlled capture |
| Board routing | Full 9067-0604 marking and both PCB sides are photographed; J3 continuity is owner-measured, including the pin-3-to-VDD series path; some under-component routing remains unresolved | Additional protected net tracing only as needed |
| Input wiring | Door/drawer/thermostat/fuel/buttons/pots and the J10 blower correlation are live-validated; J9 has partial start/stop support; CR02.1/CR02.7, J9 polarity, and J9 timing remain unresolved | Passive observation or a separately supervised bounded sensor test |
| Telemetry conversions | Later format-05/07 map is statically decoded; live format 04 differs and only several fields, inputs, and fault indicators are correlated | Additional controlled operating captures and recovered 2.02 firmware/software |
| Table-only telemetry | BixCheck 5.5.01 names TFD-TFF, but no producer is recovered in periodic 2.71 firmware; T20 is a separate 2.06/2.70/2.71 display-event path and live 2.06 `02`/`00` matched flashing light 2 | Passive capture or newly identified conditional producer |
| EEPROM semantics | Live format-04 backup/checksum/identity are preserved; stored serial/date differ from the appliance nameplate and many calibration meanings rely on labels | Compare another format-04 unit or recovered 2.02 BixCheck/firmware |
| Checkout thresholds | Buttons, pots, doors, thermostat, exhaust CR05, feeder CR07, and igniter result bits are mapped; several engineering units/state meanings remain unresolved | Trace remaining manual/no-op cases and conversions |
| Downloader | First physical block returned `E7` then no `E4`; PICkit readback proved byte-swapped words. Original 2.02 has been restored and boots normally. The corrected frame has never been transmitted physically because later runs missed entry | Build a target-power-safe UART/hardware-reset fixture, prove 100/100 zero-write entries, then perform one corrected update and PICkit readback on expendable hardware |
| Full-controller Rev A | The last corrected route reached two airwires with zero multi-net pins and zero cross-net clearance findings, but it predates the connector-side 1-Wire pull-up and three-condition expansion-enable correction and is obsolete. Exact footprints, native KiCad DRC, J5 mapping, harnesses, enclosure, and first-article tests remain open | Route the post-fix 250-component input through the audited handoff, require zero airwires and clean native KiCad DRC, then execute the staged validation plan before any board order |

## Current boundary

Read-only J3 access and the four normal-control button bytes are now established
for serial 5215. Exact 2.02 code and bounded live evidence establish T0C state
readback, including Off and Prefill. The direct low-level button path remains
explicitly authorized; the high-level API executor still fails closed because
format-04 level changes and the post-ON UART recovery interval are not fully
qualified.
Firmware 2.02 program memory, EEPROM, User IDs, and configuration are preserved
from the original complete read. A second complete read after the failed J3
block proved EEPROM/User IDs/config intact and isolated corruption to three
relocated reset-vector words. The operator reported restoring the sole hash-
pinned pre-write 2.02 image with the external programmer; the controller then
showed a normal boot and matching J3 identity/EEPROM. No post-program whole-chip
readback or IPE log was retained.
J3-3 is passively traced through approximately 100 ohms to PIC VDD and is
provisionally nominal +5 V, but its powered behavior remains unverified. It
must stay disconnected regardless of the historical forum cable's red-wire
position. No J3 update/recovery path has been proven on sacrificial hardware.
Configuration and Checkout actuators remain simulator-only. The corrected
loader framing is not yet physically requalified. The current bare-FTDI/BREAK
entry workflow is retired for every physical loader exchange; loader-entry hardware must
first satisfy the documented no-backpower and repeatability gates. A matching
register readback verifies a byte only, not physical actuator behavior or
overall controller safety.

The new full-controller PCB is a source-level engineering checkpoint only. Its
[dated status](../hardware/openmaxfire-controller/CURRENT_STATUS.md) records the
verified CAD boundary, rejected route history, BOM reconciliation, and open
release gates. No current Gerber set is released, and nothing in the PCB source
authorizes an installed-stove connection or physical firmware operation.
