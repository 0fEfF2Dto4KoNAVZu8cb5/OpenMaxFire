# Exhaustive firmware-emulator pass

Status: offline, experimental emulation against disposable CPU/RAM/EEPROM
clones. No stove or serial adapter is involved, and no preserved image is
modified.

## Scope and result

`tools/pic14_emulator.py project --repo-root .` now performs these offline
investigations for the 2.02, 2.06, 2.70, and 2.71 application images:

1. execute every real CR handler (CR00-CR0C in 2.02 and CR00-CR0E later);
2. trace every file-register and port read/write from handler entry to the
   shared response formatter;
3. record instruction-level watchpoint changes and whole-handler RAM diffs;
4. execute every real C-write handler with safe synthetic values: CW00-CW0E
   in 2.02 and CW00-CW0F later, explicitly substituting `CW0F00` for the
   later reset/loader key;
5. trace every periodic T slot through its producer and real UART sender;
6. replay every configured GPIO input and all eight ten-bit ADC channels; and
7. run all 256 A-unit reads against checksum-valid synthetic PIC data EEPROM.

All 58 CR handlers reached their expected entry and response-formatter PCs
without error. All 63 C-write probes reached their expected handler; 55
returned through the shared silent exit and the eight bounded nonreturns are
the long `CW05`/`CW0A` actuator paths. All 113 periodic telemetry slots reached
the real sender. All 1,024 A-unit reads returned the injected byte. The fixture is
deliberately labeled `EMU00001` / `OPENMAXFIRE-LAB`; it is not data from serial
5215 and is never written back to an image or device.

## New dynamic findings

The full firmware-generated CR baseline is:

| Read | 2.02 | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: | ---: |
| `CR00` | `00` | `00` | `00` | `00` |
| `CR01` | `00` | `00` | `00` | `00` |
| `CR02` | `00` | `00` | `00` | `00` |
| `CR03` | `00` | `08` | `08` | `08` |
| `CR04` | `41` | `41` | `41` | `41` |
| `CR05` | `00` | `00` | `00` | `00` |
| `CR06` | `03` | `03` | `03` | `03` |
| `CR07` | `2D` | `51` | `51` | `51` |
| `CR08` | `04` | `05` | `07` | `07` |
| `CR09` | `00` | `00` | `00` | `00` |
| `CR0A` | `00` | `00` | `00` | `00` |
| `CR0B` | `02` | `02` | `02` | `02` |
| `CR0C` | `02` | `06` | `70` | `71` |
| `CR0D` | generic `00` | `00` | `00` | `00` |
| `CR0E` | generic `00` | `21` | `02` | `00` |

The baseline is a deterministic synthetic-hardware state, not a claim about a
real idle stove. The cross-version constants are nevertheless executed facts.

The real formatter emits lowercase hexadecimal letters. For example, an
uppercase `CR0A` request receives `CR0a00` plus LF, and a value of `0x4F` is
rendered as `4f`. BixCheck and OpenMaxFire already accept either case on input;
replacement clients should continue sending uppercase requests.

Bank-aware tracing also corrects the CR04 source from the earlier provisional
RAM `0x22` label to bank-1 address `0x0A2`. The complete source sets and exact
read PCs are in `cr-handler-dependencies.csv`.

## Synthetic C-write coverage

The new pass reaches every real dispatch entry: CW00-CW0E in 2.02 and
CW00-CW0F in each later generation.
Writes run only against a cloned post-boot CPU with synthetic RAM and PIC data
EEPROM. `CW0FC4` is never generated: the reset register is probed with value
`00`, which exercises its non-key branch and returns normally.

Fifty-five of 63 probes reach the normal silent exit. `CW05` (burn-drive motor)
and `CW0A` (igniter follow-up) in all four versions enter long timer/actuator
paths and exceed the 50,000-instruction bound. That is expected under the
incomplete peripheral model and is not classified as an error. `CW0D` emits
`I` plus LF; all other completed probes are silent.

The EEPROM model now implements the PIC write-enable/write-complete sequence.
`CW01` produces exactly two program events in each version, at A00 and A01,
after running the firmware checksum routine. The checksum-valid fixture means
the final bytes equal the starting bytes, while the write events themselves
remain observable.

The complete register meanings, exact handler PCs, known service values, and
safety boundary are in [controller-writes.md](../protocol/controller-writes.md).

## Telemetry producer coverage

The harness directly selects each periodic slot after synthetic boot, then
allows the real firmware producer and UART sender to run. It completes 22 slots
for 2.02, 30 for 2.06, 30 for 2.70, and 31 for 2.71 with no error. This establishes the
physical `Txxvv` one-byte lines, optional preceding `DWxxyy` auxiliary lines,
producer dependencies, and per-version end indexes.

Direct entry is intentionally not a scheduler model. Periodic cadence,
suppression gates, and real-time sensor evolution cannot be inferred from the
step counts. TMR0 also advances synthetically per modeled instruction, so
those counts establish control flow only.

The field/source map, big-endian adjacent-slot assembly, BixCheck conversion
math, and exact T09 decoder are in
[telemetry-fields.md](../protocol/telemetry-fields.md).

## Signal map recovered offline

The GPIO differentials agree across all four generations. Cross-referencing
them with BixCheck's `AnalyzeInteractiveResult()` masks produces:

| Physical/service signal | Protocol representation | PIC source | Offline confidence |
| --- | --- | --- | --- |
| Front-panel buttons | `CR01`: none `00`, ON `02`, OFF `01`, UP `04`, DOWN `08` | RD2 button-bank select, RD6:RD5 address, active-low RD3 return; final value RAM `0x52` in 2.02 and bank-1 `0x53` later | Static map; OFF/UP/DOWN/none later live-validated |
| Burn-drive limit switch | `CR02` bit 0 | RD3 external-input mux slot 0 | High static mapping; physical polarity unverified |
| Unassigned mux input | `CR02` bit 1 | RD3 external-input mux slot 1 | Transport mapped; physical function unresolved |
| Firebox door | `CR02` bit 5; open `1`, closed `0` | RD1 | Later live-validated |
| Ash drawer | `CR02` bit 6; open `1`, closed `0` | RD4 | Later live-validated |
| Thermostat | `CR06` bit 2; open `1`, closed `0` | RB4 | Later live-validated |
| Fuel select | `CR02` bit 2; `1`=Fuel A/corn, `0`=Fuel B/wood | RD3 external-input mux slot 2 | Later live-validated |
| Exhaust-fan sensor J10 | `CR05` raw pulse-count byte | RA4/T0CKI → TMR0 → RAM `0x34`; sampled every 30 RB0 external-interrupt ticks | Live 2.02 blower correlation; count-to-RPM conversion unresolved |
| Feeder-wheel sensor J9 | Current state in `CR02.4`; scaled cycle interval in `CR07` | RD0 high-then-low cycle; RB1-gated RAM `0x47:0x46` counter latched to `0x45:0x44`; 2.02 pre-shifts once, then all versions shift four times in CR07 | Partial live 2.02 correlation; polarity and time unit unresolved |
| Fan potentiometer | `CR09`; low `00`, center about `80`, high `FF` | AN3 | High offline mapping |
| Feed potentiometer | `CR0A`; low `00`, center about `80`, high `FF` | AN4 | High offline mapping |

RD0→CR02 bit 4 is now assigned to the J9 feeder-wheel sensor by following its
motor-gated transition detector; RE1→bit 7 remains physically unnamed. The
original GPIO replay held RD3 at one synthetic level and therefore set all three external-mux
slots together. Static scanner reconstruction now separates the selectors:
RD7 chooses the external-input bank, RD6:RD5 choose slots 0-2, and RD3 is the
active-high return. The related-board 9067-0404 diagram labels the corresponding
physical signals as the burn-drive motor switch and fuel switch; slot 1 remains
unassigned.

Fuel polarity is independently fixed by controller behavior. When CR02.2 is
clear, 2.70/2.71 add `0x30` to move configuration reads from Fuel A (`A40...`)
to Fuel B (`A70...`); 2.02/2.06 have equivalent paths, and retained BixCheck
result predicates test the same opposite states. The reachable 5.5 fuel-test
rows still fail to machine-check the operator state, which is a BixCheck
application defect rather than evidence against the firmware mapping.

The producer trace also resolves the previously unnamed CR05 and CR07 values.
All four applications contain the same six functional stages, now asserted by
`tests/test_firmware_pipeline.py` and exported to
`reverse-engineering/firmware/comparison/sensor-signal-paths.csv`. The 2.02
J9 latch adds one right shift that later versions omit. BixCheck
accepts CR05 `>=0x78` at full exhaust, `0x38`-`0x48` at half exhaust, and zero
when off in 5.5.x (5.0.21 tolerates `0x00`-`0x03`). Its feed test accepts CR07
`0x10`-`0x68`. Those ranges do not establish engineering units.

The ADC replay starts each image from reset. Each generation samples AN1-AN4
during startup. Sweeping AN3 changes CR09 linearly through the high eight bits
of the ten-bit sample; sweeping AN4 does the same for CR0A. No other ADC
channel changed those two pot registers.

## EEPROM correction and model

The A-unit configuration reads are implemented by the firmware through
PIC16F877A `EEADR`, `EEDATA`, and `EECON1`. This is the PIC's internal 256-byte
data EEPROM, not an external I²C EEPROM. The I²C peripheral remains a separate
synthetic device in this emulator.

Three fixtures are generated:

| Stove data format | Checksum coverage | Stored checksum |
| ---: | ---: | ---: |
| `04` | A02-A69 | `0x59B5` |
| `05` | A02-A9A | `0x643D` |
| `07` | A02-AFF | `0x9AF4` |

The checksum is the reconstructed BixCheck add-then-rotate-left-16 algorithm,
stored big-endian at A00-A01. Every `AR00`-`ARFF` request is sent to every
firmware generation. The firmware's real UART/parser/EEPROM/formatter path
returns every expected fixture byte.

## Generated evidence

All files below are under `reverse-engineering/firmware/emulation/deep/`:

| File | Contents |
| --- | --- |
| `cr-read-matrix.csv` | 58 requests, responses, handler/formatter reachability, and trace counts |
| `cr-handler-accesses.csv` | Every traced direct/indirect read and write in execution order |
| `cr-handler-dependencies.csv` | Unique read dependencies, values, and exact PCs |
| `cr-handler-watchpoints.csv` | Every instrumented value change with before/after bits |
| `cr-handler-net-changes.csv` | Complete RAM/SFR entry-versus-exit differences |
| `cw-write-matrix.csv` | All 63 synthetic C writes, reachability, serial output, and event counts |
| `cw-handler-access-summary.csv` | Per-write unique file-register reads/writes and PCs |
| `cw-handler-change-summary.csv` | Per-write watchpoint changes grouped by address |
| `cw-handler-net-changes.csv` | Complete C-write RAM/SFR entry-versus-exit differences |
| `cw-eeprom-events.csv` | The eight A00/A01 checksum-program events produced by CW01 |
| `telemetry-slot-matrix.csv` | All 113 forced slots, exact T/D lines, scratch writes, and reachability |
| `telemetry-producer-access-summary.csv` | Per-slot producer dependency sets and exact PCs |
| `gpio-input-matrix.csv` | TRIS-derived input/output direction for every port bit |
| `gpio-scenarios.csv`, `gpio-effects.csv` | Per-input replay and only the changed CR results |
| `adc-scenarios.csv`, `adc-effects.csv` | Per-channel/value reset replay and changed pot results |
| `controller-eeprom-fixtures.csv` | All three synthetic 256-byte fixtures with field roles |
| `a-unit-eeprom-reads.csv` | All 1,024 expected/actual A-unit reads and EEPROM events |
| `signal-map.csv` | BixCheck/firmware/emulator signal cross-reference |
| `summary.json` | Counts, fixture metadata, mappings, and limitations |

## Boundaries

- Synthetic logic levels do not model voltage, polarity, pull-ups, switch
  bounce, isolation, or a real cable.
- C writes alter only disposable synthetic state. No A-unit write is executed,
  and the keyed `CW0FC4` reset/loader request is explicitly excluded.
- The modeled completion of a write handler is not physical acknowledgement,
  actuator validation, persistence verification, or evidence that a request is
  safe to send live.
- `CW05` and `CW0A` do not return within the bounded timer/peripheral model;
  their eight records are expected modeled nonreturns, not firmware failures.
- The 2.02 fixture stops at the first state dispatch and seeds the live-observed
  `0x20` Off state because synchronous CCP1 actuator initialization is not yet
  advanced by the lightweight peripheral model.
- Telemetry slots are forced directly through real producer/sender code;
  scheduler cadence and gating remain unmodeled.
- Firmware control flow can identify a PIC pin and protocol bit, but only a
  cold/off physical correlation can validate the `9067-0604` board wiring on
  serial 5215. The diagram used for signal names depicts `9067-0404`.
- This work does not make ignition, actuator, downloader, configuration, or
  ordinary control writes safe.
