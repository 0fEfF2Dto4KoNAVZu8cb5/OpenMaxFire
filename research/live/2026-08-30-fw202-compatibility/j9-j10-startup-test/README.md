# Bounded J9/J10 startup incident

Date: 2026-08-30  
Controller: firmware 2.02, data format 04  
Conditions: no fuel; igniters unplugged; operator present for the active
portion; side panel not installed; no loader or configuration traffic

This was intended as a 60-second startup correlation for J9 and J10. It did
not complete as designed. The recorder called `to_dict()` on an
`OperatingState` immediately after its first register batch, raised
`AttributeError`, and entered its `finally` recovery path. The resulting
failure and shutdown evidence are retained rather than represented as a clean
test.

## Exact sequence

- Baseline at `22:00:24.211613Z` was T0C `20`/Off, `CR02=02`, `CR03=08`,
  `CR05=00`, and `CR07=1E`.
- ON (`CW0E12`) was transmitted at `22:00:24.646829Z`.
- The first byte received after ON did not arrive until
  `22:00:51.796216Z`, 27.149 seconds later. During that silent interval the
  recovery loop transmitted 26 OFF requests; transmission alone does not prove
  that any was accepted.
- The first returned post-start register set included `CR02=92`, `CR03=09`,
  `CR05=0C`, and `CR07=1E`. T08 was `01`. The operator independently reported
  the first physical light on and the blower running and said the stove still
  appeared on.
- The recovery code incorrectly reported Off at `22:00:53.587235Z`. That claim
  is retracted: its T0C `20` had last arrived at `22:00:23.763994Z`, before ON.
  New addressed responses made the overall snapshot fresh while its retained
  state byte was stale.
- A separate remote OFF (`CW0E11`) was transmitted at
  `22:01:36.948989Z`. The operator then reported that the stove returned Off
  without pressing the physical control.
- The following read-only capture observed T08 `00` at
  `22:01:57.004280Z` and a genuinely post-command T0C `20` at
  `22:01:58.986887Z`. Its two complete no-timeout cycles had `CR05=00`,
  `CR07=1F`, `CR02=12`, and `CR03=08`.
- A later 20-cycle read-only stability capture ran from
  `22:09:54.761866Z` through `22:10:29.158722Z` with zero timeouts. Every
  cycle retained `CR02=12`, `CR03=08`, `CR05=00`, `CR07=1F`, and T08 `00`;
  all 19 snapshots that had received T0C reported `20`/Off.

## What this establishes

- J10 has a live physical correlation on this controller: `CR05` moved
  `00`→`0C` while the operator observed the blower running, then returned to
  `00` after OFF. This confirms a pulse-count role, not a count-to-RPM formula.
- The J9 path received partial live support: `CR02.4` changed from 0 to 1 and
  `CR07` changed from `1E` to `1F` across the start/stop interval, then both
  remained stable through 20 read-only Off cycles. This supports a parked
  sensor level plus latched interval rather than transient noise. Static writer
  enumeration makes the cycle evidence stronger: the bank-0 boot initializer
  would report `CR07=2D`, and the range clamp would report `16`; the observed
  `1F` therefore came through the runtime latch at `0x0CD0`, which requires RB1
  active and the recorded RD0 high-to-low sequence. No operator observation of
  feeder-wheel motion or running interval was captured, so electrical
  polarity, physical movement per edge, and timing units remain unresolved.
- T08 `01` is now live-correlated with the operator-observed first physical
  light. The factory-manual meaning remains a separate semantic layer.
- A typed snapshot's global `fresh` flag cannot validate a retained telemetry
  field. OFF recovery must prove that the exact T09/T0C state sample arrived
  after the command.

## Software correction

`MonitorState` now timestamps each telemetry index separately. The recovery
loop records the first transmitted OFF time and requires two distinct state
samples newer than that transmission to report Off or Cooldown. Focused tests
cover the exact stale-precommand-state failure.

No second active test was attempted. After the operator left, work was limited
to read-only monitoring and offline analysis.

## Artifacts

| Artifact | Purpose |
| --- | --- |
| `traffic.jsonl` | Exact baseline, ON, failed recorder, repeated cleanup, and first returned traffic |
| `summary.json` | Original generated summary; its `verified=true` result is explicitly retracted above |
| `sensor-samples.jsonl` | Empty because the recorder failed before committing its first sample |
| `manual-recovery-off-traffic.jsonl` | Separate remote OFF transmission |
| `post-manual-recovery-traffic.jsonl` | Exact read-only recovery verification traffic |
| `post-manual-recovery-snapshots.jsonl` | Decoded post-recovery snapshots |
| `unattended-final-traffic.jsonl` | Final read-only traffic after the operator left |
| `unattended-final-snapshots.jsonl` | Three zero-timeout snapshots ending at `22:08:17.991041Z`, each with T08 `00`; the final two contain post-open T0C `20`/Off |
| `postrun-stability-traffic.jsonl` | Exact traffic for 20 unattended read-only Off cycles |
| `postrun-stability-snapshots.jsonl` | Stable J9/J10 values and zero timeouts over 34.4 seconds |
