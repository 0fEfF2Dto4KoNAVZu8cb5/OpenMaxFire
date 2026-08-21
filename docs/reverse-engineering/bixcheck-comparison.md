# BixCheck cross-version comparison

## Release matrix

| BixCheck | EXE size | Intended firmware | Data format | Host baud selection | Adjustments | Telemetry records |
| --- | ---: | --- | ---: | --- | ---: | ---: |
| 5.0.21 | 441,552 | 02.06 | 05 | 9,600 | 71 | 30 |
| 5.5.00 | 462,052 | 02.70 | 07 | 9,600 / 19,200 | 82 | 30 |
| 5.5.01 | 464,650 | 02.71 | 07 | 9,600 / 19,200 | 82 | 34 |

All three are 32-bit MinGW Windows GUI applications. Their COFF symbols retain
enough names and compilation-unit provenance for source-level comparison.

## Function-level change counts

The analyzer normalizes build-specific absolute addresses and symbolic branch
destinations before hashing instructions. This reduces relocation noise but
does not replace manual review.

| Transition | Same normalized | Changed | Added | Removed |
| --- | ---: | ---: | ---: | ---: |
| 5.0.21 → 5.5.00 | 85 | 46 | 16 | 4 |
| 5.5.00 → 5.5.01 | 109 | 38 | 0 | 0 |

The second transition's 38 changed hashes are dominated by object/table offsets
moving after four telemetry records are inserted. Direct semantic comparison
shows these cores unchanged in 5.5.00 and 5.5.01:

- `regio`, `writereg`, and `readreg` request construction;
- `CalculateChecksum`;
- `SendInteractiveAction` and `SendAutomaticAction`;
- Downloader `GetStoveVersion`, `AttemptStoveReset`, `SendDone`, `LoadHex`,
  `DownLoad`, and `Identify`.

`scanio` has one meaningful 5.5.01 table-index change, `0x1B` to `0x1C`, matching
the moved virtual time-to-ash-dump record.

## Stable wire behavior

Across all three builds:

- read requests are `<unit>R<address:02X>`;
- write requests are `<unit>W<address:02X><value:02X>`;
- outgoing hex is uppercase and requests carry no terminator;
- addressed responses are six characters; firmware telemetry is the
  five-character one-byte form, while the host parser retains a seven-character
  compatibility representation;
- CR and LF terminate responses;
- leading bytes 01-03 are stripped before dispatch;
- the binary firmware downloader is separate from the normal ASCII protocol.

The compatibility-breaking serial difference is outside the grammar: 5.0.21
only selects 9,600 baud, while 5.5.x can select 9,600 or 19,200.

## Configuration evolution

5.0.21 has no lean-burn records. 5.5.x adds the following to both fuel banks:

| Fuel A | Fuel B | Meaning |
| --- | --- | --- |
| A6B | A9B | Lean-burn threshold percent |
| A6C | A9C | Lean-burn fan adjustment |
| A6D | A9D | Lean-burn feed adjustment |
| A6E | A9E | Shared ratio/ash mode and auto-restart-disable bits |

5.5.x also adds A6A thermostat heat level and explicit field limits. Its format
07 checksum covers A02-AFF and transforms displayed lean-burn values back to
wire encoding before calculation. 5.0.21 format 05 stops at A9A.

## 5.5.01 fuel-profile change

The third selection in each fuel list changes from `2% ash Biomass` to `Wheat`.
Only 24 of the 352 raw combustion-adjustment bytes change, all in three
consecutive eight-level blocks of the fuel-type table:

| Raw indices | 5.5.00 | 5.5.01 |
| --- | --- | --- |
| 48-55 | `0x7D` × 8 | `0x73` × 8 |
| 56-63 | `0x55` × 8 | `0x78` × 8 |
| 64-71 | `0x3A` × 8 | `0x1E` × 8 |

Feedwheel, fan-curve, and altitude adjustment arrays are identical. The raw
blocks correlate with the relabeled third fuel profile, but their precise
fan/feed/ash semantic order should not be treated as live-calibration guidance
until independently validated.

## Telemetry evolution

5.0.21 and 5.5.00 have identical 30-record telemetry tables. 5.5.01:

- relabels T19 from `Drop limit` to `BF drop limit`;
- adds T1E `LB drop limit`;
- moves `Time to ash dump` from virtual V1B to V1C;
- adds TFD `Low temp count`, TFE `Sample maximum`, and TFF `Recent sample`.

The firmware pass independently finds periodic T00-T1E and a separate T20
event sender in 2.71. It does not find a periodic or literal TFD-TFF producer,
so those three remain BixCheck table entries rather than claimed periodic wire
frames.

The complete row-level differences are in
`reverse-engineering/bixcheck/comparison/data-element-changes.csv`.

## Checkout and Downloader stability

All 46 embedded Checkout records are byte-identical in every EXE, and the
action sender methods normalize identically. Only 45 records are reachable;
the dormant ninth automatic plate-motor record is excluded by the UI and
dispatcher.

The Downloader state machine also normalizes identically. Version labels and
firmware payloads change, not the host framing. That stability lets us analyze
one protocol implementation and verify it against all three builds, while still
requiring exact firmware/data-format matching for any future service operation.

Machine-readable evidence lives under
`reverse-engineering/bixcheck/comparison/`. Regenerate it with:

```bash
python tools/analyze_bixcheck.py --repo-root .
```

The recovered write, logging/report, QuickCal/debug, and flue/fuel-monitor
flows are summarized in
[bixcheck-runtime-workflows.md](bixcheck-runtime-workflows.md).
