# Serial 5215 live control and fault evidence

This directory preserves the 2026-08-23 UTC live evidence from the firmware
2.02/data-format-04 controller associated with appliance serial 5215. It
extends the earlier read-only corpus with normal front-panel command traffic
and a steady feeder-wheel fault capture.

See the interpreted reports:

- [`docs/reverse-engineering/live-fw202-format04.md`](../../../docs/reverse-engineering/live-fw202-format04.md)
- [`docs/protocol/faults.md`](../../../docs/protocol/faults.md)

## Evidence policy

- Copied JSON/JSONL/Markdown artifacts are byte-identical to the uploaded
  files; only their repository filenames were normalized.
- Raw traffic is retained without editing or reconstructed timestamps.
- Interpretation and later operator observations are recorded here rather
  than inserted into the original session artifacts.
- `SHA256SUMS.txt` covers every retained file except itself.

## Control-validation session

The `validation/` directory contains one `openmaxfire.live-validation.v1`
session and its exact serial audit log. The session transmitted the recovered
front-panel commands:

| Action | Wire command | Result |
| --- | --- | --- |
| ON | `CW0E12` | Startup physically observed |
| UP | `CW0E14` | Physical response observed |
| DOWN | `CW0E18` | Physical response observed |
| OFF | `CW0E11` | Shutdown subsequently confirmed by the operator |

The generated `RESULTS.md` conservatively labels the combined ON/OFF step
indeterminate because its automated snapshot evidence could not independently
prove both state transitions. The later operator confirmation is not retrofitted
into that immutable report.

## Feeder-wheel fault capture

The stove was already displaying a single flashing rightmost heat-level light
when `captures/fw202-fault8-traffic.jsonl` began. Consequently this is a steady
fault-state capture, not a record of the transition that latched the fault.
The operator identified the physical lamp as light 8.

The exact traffic establishes:

- firmware `2.02`, data format `04`, 9,600 baud;
- 17 observed `T08` samples in about 30 seconds;
- `T08` alternated between `00` and `80` while light 8 visibly flashed;
- seven samples contained `T08=80`;
- the maximum interval between `T08=80` samples was about 6.14 seconds;
- the cold/off control capture held `T08=00`; and
- `T13=BA` appeared unchanged in cold/off and fault evidence.

This live-correlates format-04 `T08.7`/`0x80` with flashing light 8 and the
factory-documented feeder-wheel failure indication. It also demonstrates why a
latest-value snapshot can miss a flashing fault: both generated snapshots
ended during a `T08=00` phase even though the raw traffic retained the nonzero
samples.

The empty hopper present during this experiment is context, not a proven cause
of fault 8. The factory table assigns an empty-hopper/possible-blocked-flue
indication to lights 2 and 3, while light 8 means feeder-wheel movement was not
detected.

## Artifact inventory

| Path | Purpose |
| --- | --- |
| `validation/RESULTS.md` | Original generated validation report |
| `validation/summary.json` | Structured validation outcome and audit digest |
| `validation/traffic.jsonl` | Exact ON/OFF/UP/DOWN validation traffic |
| `validation/cold-baseline-01.json` | Typed cold/off snapshot from the session |
| `captures/fw202-fault8-traffic.jsonl` | Exact byte traffic during physical flashing light 8 |
| `captures/fw202-fault8-snapshots.jsonl` | Two generated monitor snapshots from the same capture |
