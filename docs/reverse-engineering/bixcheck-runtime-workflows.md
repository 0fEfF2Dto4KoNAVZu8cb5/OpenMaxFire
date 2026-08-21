# BixCheck runtime workflows

Status: static reconstruction from retained function symbols, call graphs,
tables, strings, and focused assembly in BixCheck 5.0.21, 5.5.00, and 5.5.01.
The executables were not run.

This pass extends the protocol/table work into the application workflows that
a useful replacement tool must reproduce: writes, logging, report files,
QuickCal, debug, and the blocked-flue/fuel-monitor windows.

## Configuration-write lifecycle

The 5.5.01 four-argument `BixbyWriteRegister()` is at VA `00414780`. Its
observable sequence is:

1. optionally collect/drain a prior response;
2. call `bixby110io::writereg()` for the selected unit/address/value;
3. delay 50 ms;
4. collect responses and route returned data through
   `Bixby110UpdateData()` so the application's caches and controls refresh.

That is stronger than a blind transmit, but it is not a proven read-after-write
comparison. A replacement must issue an explicit read and compare the expected
stored representation before it reports a durable configuration change.

Six lean-burn addresses receive a host-side inverse display transform before
the generic writer is called:

| Role | Fuel A | Fuel B | Host display → stored value |
| --- | ---: | ---: | --- |
| threshold | A6B | A9B | percentage to 0-128-style multiply parameter |
| fan offset | A6C | A9C | signed percentage around stored center `0x80` |
| feed offset | A6D | A9D | reversed signed percentage around `0x80` |

The exact rounding and inverse functions are implemented and tested in
`src/openmaxfire/protocol.py`. `Bixby110TuneAdjustments()`, initialization,
QuickCal/debug setup, report generation/loading, and five main-dialog call
sites feed the common writer rather than implementing separate wire grammars.

The controller C-unit actions are mapped independently in
[controller-writes.md](../protocol/controller-writes.md). A-unit configuration
writes still require field-specific ranges, a complete backup, data-format
validation, checksum handling, and verify-after-write before OpenMaxFire should
expose them live.

## Telemetry logging

BixCheck's log path is a selected set of telemetry/display records, not a raw
serial transcript. The workflow has three internal states: Off, On, and Hold.
It also has a percentage setting that decides which completed telemetry sweeps
are written.

Once a log file has been selected/opened, the active path is retained for that
logging session. New files use:

```text
BixLog_<serial>_<01..99>.txt
```

The application searches the two-digit suffix range for an available `.txt`
name. `WriteDataLogDescription()` writes the selected-field description/schema;
`WriteDataLogTimeDate()`, `DataLogLineAssemblePayload()`, and
`WriteDataLogLine()` assemble comma-separated time/data rows. The functions use
`GetLocalTime`, the local `FormatTime()` helper, and Win32 `WriteFile`.

This distinction matters for replacement design:

- a compatibility export should preserve selected columns, ordering, labels,
  local timestamps, and sweep-percentage behavior;
- a research capture should separately retain exact raw bytes and arrival
  times, because the BixCheck log has already decoded and filtered the stream;
- Hold must stop appending without discarding the active selection/path;
- partial two-byte fields must not be logged as a new 16-bit value until both
  adjacent physical T slots have arrived.

## Configuration/service reports

The control application generates text reports named:

```text
Bixby_115_<serial>_<number>.txt
```

`GenerateReport(char*)` serializes identification and groups of configuration
records. `LoadReport(char*)` opens and parses the corresponding text fields
back into the application's data/UI model. Loading a report is therefore not
itself proof that any value was written to the controller.

Checkout has a separate `bixby110checkout::GenerateReport()` path for factory
test results. OpenMaxFire should keep configuration snapshots, live write
transactions, and Checkout reports as visibly different artifact types.

## QuickCal and debug surfaces

The setup functions expose the shape and ownership of the utility workflows
even where button-specific semantics need further message-handler tracing.

| Surface | 5.5.01 setup VA | Recovered controls | Confirmed role |
| --- | ---: | --- | --- |
| QuickCal | `00416600` | 5 radio buttons, 3 pushbuttons | selects a compact calibration mode/action workflow |
| Debug | `00416AB0` | 4 edit fields, 2 pushbuttons | raw/debug communication window |
| Flue monitor | `00416DF0` | 4 edit fields, 6 static labels | blocked-flue measurements/status display |
| Fuel monitor | `004171D0` | 2 tri-state checkboxes, 5 pushbuttons, 5 edit fields plus labels | fuel/lean-burn monitoring and operator actions |

These are dynamically constructed child controls inside the main monitor
object, not independent protocols. Their values are updated by the same
telemetry/configuration caches used elsewhere. The fuel monitor's tri-state
checkboxes must not be simplified to booleans until all three states are
semantically named.

## Generated evidence

`tools/analyze_bixcheck.py` now emits these focused excerpts for every release:

| File | Functions grouped |
| --- | --- |
| `telemetry-core.asm` | scan/update/conversion and telemetry display paths |
| `write-ui-core.asm` | generic writes, tuning, initialization, QuickCal, debug |
| `logging-core.asm` | data-log assembly, report generation, report loading |
| `monitor-core.asm` | flue-monitor and fuel-monitor construction/workflow |

They accompany the existing `protocol-core.asm`, `checkout-core.asm`, and
`downloader-core.asm`. Exact function extents and direct callers remain in
`functions.csv` and `call-graph.csv`, so the conclusions can be regenerated
without executing vendor code.

## Remaining static work

The useful remaining targets are narrower now:

- assign semantic names to every QuickCal/debug/monitor button message;
- recover the exact report grammar as a versioned parser fixture;
- decode the I/M status payloads used by service workflows;
- map every A-unit configuration field to validation range and UI ownership;
- distinguish response collection from actual persistence verification at
  each write call site.

None of those tasks requires a stove. Electrical characterization is still the
blocker for confirming any reconstructed behavior on serial 5215.
