# Exhaustive firmware-emulator pass

Status: offline, read-only, experimental emulation. No stove or serial adapter
is involved.

## Scope and result

`tools/pic14_emulator.py project --repo-root .` now performs all five offline
investigations requested for the 2.06, 2.70, and 2.71 application images:

1. execute every `CR00` through `CR0E` request;
2. trace every file-register and port read/write from handler entry to the
   shared response formatter;
3. record instruction-level watchpoint changes and whole-handler RAM diffs;
4. replay every configured GPIO input and all eight ten-bit ADC channels; and
5. run all 256 A-unit reads against checksum-valid synthetic PIC data EEPROM.

All 45 CR handlers reached their expected entry and response-formatter PCs
without error. All 768 A-unit reads returned the injected byte. The fixture is
deliberately labeled `EMU00001` / `OPENMAXFIRE-LAB`; it is not data from serial
5215 and is never written back to an image or device.

## New dynamic findings

The full firmware-generated CR baseline is:

| Read | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: |
| `CR00` | `00` | `00` | `00` |
| `CR01` | `00` | `00` | `00` |
| `CR02` | `00` | `00` | `00` |
| `CR03` | `08` | `08` | `08` |
| `CR04` | `41` | `41` | `41` |
| `CR05` | `00` | `00` | `00` |
| `CR06` | `03` | `03` | `03` |
| `CR07` | `51` | `51` | `51` |
| `CR08` | `05` | `07` | `07` |
| `CR09` | `00` | `00` | `00` |
| `CR0A` | `00` | `00` | `00` |
| `CR0B` | `02` | `02` | `02` |
| `CR0C` | `06` | `70` | `71` |
| `CR0D` | `00` | `00` | `00` |
| `CR0E` | `21` | `02` | `00` |

The baseline is a deterministic synthetic-hardware state, not a claim about a
real idle stove. The cross-version constants are nevertheless executed facts.

The real formatter emits lowercase hexadecimal letters. For example, an
uppercase `CR0A` request receives `CR0a00` plus LF, and a value of `0x4F` is
rendered as `4f`. BixCheck and OpenMaxFire already accept either case on input;
replacement clients should continue sending uppercase requests.

Bank-aware tracing also corrects the CR04 source from the earlier provisional
RAM `0x22` label to bank-1 address `0x0A2`. The complete source sets and exact
read PCs are in `cr-handler-dependencies.csv`.

## Signal map recovered offline

The GPIO differentials agree across all three generations. Cross-referencing
them with BixCheck's `AnalyzeInteractiveResult()` masks produces:

| Physical/service signal | Protocol representation | PIC source | Offline confidence |
| --- | --- | --- | --- |
| Front-panel buttons | `CR01`: none `00`, ON `02`, OFF `01`, UP `04`, DOWN `08` | RAM `0x53`; transport into the PIC remains unresolved | High encoding confidence |
| Firebox door | `CR02` bit 5; open `1`, closed `0` | RD1 | High; not live-validated |
| Ash drawer | `CR02` bit 6; open `1`, closed `0` | RD4 | High; not live-validated |
| Thermostat | `CR06` bit 2 | RB4 | High pin/bit confidence; verify polarity live |
| Fuel select | Candidate `CR02` bit 2 | RD3 external-multiplexer sample slot | Provisional |
| Fan potentiometer | `CR09`; low `00`, center about `80`, high `FF` | AN3 | High offline mapping |
| Feed potentiometer | `CR0A`; low `00`, center about `80`, high `FF` | AN4 | High offline mapping |

Additional direct CR02 mappings are RD0→bit 4 and RE1→bit 7. Holding the
synthetic RD3 mux-return line high sets CR02 bits 0-2 because the firmware
samples it under three selector states. A future selection-aware external-mux
model or a live cold/off correlation is required to assign each slot. The
fuel-switch association is therefore kept provisional: the current BixCheck
table presents the two fuel tests, but its reachable 5.5 result paths do not
machine-check them; two retained, unreachable handlers test opposite states of
CR02 bit 2.

The ADC replay starts each image from reset. Each generation samples AN1-AN4
during startup. Sweeping AN3 changes CR09 linearly through the high eight bits
of the ten-bit sample; sweeping AN4 does the same for CR0A. No other ADC
channel changed those two pot registers.

## EEPROM correction and model

The A-unit configuration reads are implemented by the firmware through
PIC16F877A `EEADR`, `EEDATA`, and `EECON1`. This is the PIC's internal 256-byte
data EEPROM, not an external I²C EEPROM. The I²C peripheral remains a separate
synthetic device in this emulator.

Two fixtures are generated:

| Stove data format | Checksum coverage | Stored checksum |
| ---: | ---: | ---: |
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
| `cr-read-matrix.csv` | 45 requests, responses, handler/formatter reachability, and trace counts |
| `cr-handler-accesses.csv` | Every traced direct/indirect read and write in execution order |
| `cr-handler-dependencies.csv` | Unique read dependencies, values, and exact PCs |
| `cr-handler-watchpoints.csv` | Every instrumented value change with before/after bits |
| `cr-handler-net-changes.csv` | Complete RAM/SFR entry-versus-exit differences |
| `gpio-input-matrix.csv` | TRIS-derived input/output direction for every port bit |
| `gpio-scenarios.csv`, `gpio-effects.csv` | Per-input replay and only the changed CR results |
| `adc-scenarios.csv`, `adc-effects.csv` | Per-channel/value reset replay and changed pot results |
| `controller-eeprom-fixtures.csv` | Both synthetic 256-byte fixtures with field roles |
| `a-unit-eeprom-reads.csv` | All 768 expected/actual A-unit reads and EEPROM events |
| `signal-map.csv` | BixCheck/firmware/emulator signal cross-reference |
| `summary.json` | Counts, fixture metadata, mappings, and limitations |

## Boundaries

- Synthetic logic levels do not model voltage, polarity, pull-ups, switch
  bounce, isolation, or a real cable.
- The emulator executes no `CW` or `AW` request in this pass.
- Firmware control flow can identify a PIC pin and protocol bit, but only a
  cold/off physical correlation can validate the board wiring on serial 5215.
- This work does not make ignition, actuator, downloader, or write commands
  safe.
