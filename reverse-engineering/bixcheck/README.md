# BixCheck static-analysis archive

This tree is generated from the three original vendor ZIP packages by
`tools/analyze_bixcheck.py`. The script never executes an EXE and validates each
member against its expected SHA-256 before analysis.

## Versions

| Directory | Package member | SHA-256 |
| --- | --- | --- |
| `5.0.21/` | `BixCheck_5021.exe` | `0f51f1b9ffe12011928c7821ecc07db92b2bf98a1d82e5fcf605d464316d52d4` |
| `5.5.00/` | `BixCheck_080206.exe` | `12dd738a10f72f18a672aeec6ec5e1456ff478103ca84fc154c4f73594aac3d6` |
| `5.5.01/` | `BixCheck_080315.exe` | `b681f79d284bc5da6d087ce052f916853402144430d4adbceaa2ed2e911c2792` |

> **Have an unlisted BixCheck version?** If you have BixCheck software from a
> version not listed above, please contact me or open a pull request so it can
> be preserved and reverse-engineered.

## Per-version outputs

- `summary.json`: PE metadata, symbol/table counts, and serial settings;
- `functions.csv`: source unit, demangled name, VA/RVA, extent, and raw/normalized hashes;
- `call-graph.csv`: statically visible direct call edges;
- `data-elements.csv`: decoded 0x58-byte configuration/telemetry/UI records;
- `checkout-tests.csv`: decoded 0x122-byte tests and UI reachability;
- `combustion-adjustments.csv`: byte-exact adjustment arrays;
- `selected-strings.csv`: evidence-relevant ASCII strings with file offsets;
- `protocol-core.asm`, `checkout-core.asm`, `downloader-core.asm`: focused exact
  GNU objdump excerpts for framing, factory tests, and firmware servicing;
- `telemetry-core.asm`: receive/update, state decode, and display conversions;
- `write-ui-core.asm`: generic register writes, initialization, tuning,
  QuickCal, and debug construction;
- `logging-core.asm`: data-log assembly plus report generation/loading;
- `monitor-core.asm`: blocked-flue and fuel-monitor window construction.

Full multi-megabyte disassemblies are intentionally not checked in because the
focused excerpts and reproducible script preserve the useful evidence with less
review noise.

`comparison/` contains function, record, Checkout, and raw adjustment deltas
for 5.0.21→5.5.00 and 5.5.00→5.5.01.

## Regenerate

```bash
python tools/analyze_bixcheck.py --repo-root .
```

GNU `objdump` with Intel syntax is the only non-Python requirement.
