# Firmware 2.02 compatibility session

Date: 2026-08-30  
Controller: appliance serial 5215, firmware 2.02, data format 04, 9,600 baud  
Interface: direct FTDI UART on `/dev/ttyUSB0`  
Operator conditions: no fuel; igniters physically unplugged; firebox door,
ash drawer, and hopper door closed; controller remained AC-powered.

This session was aimed at closing read-only format-04 compatibility gaps. It
did not attempt J3 loader entry, firmware programming, arbitrary writes, or
Checkout actuator commands.

## Preserved baseline

- `fw202-format04-baseline-backup.json` is a complete A00-AFF read. Its raw
  EEPROM bytes match the authenticated PICkit 2.02 image byte for byte.
- `cold-off-baseline-snapshots.jsonl` and its traffic capture contain eight
  bounded monitor cycles with no read timeout.
- The exact recovered 2.02 image and live telemetry agree that T0C is the
  state-family byte. Cold/off was `T0C=20`; T09 is not the state source.
- CR00-CR0C reach real 2.02 read handlers. CR0D and CR0E return the parser's
  generic zero response without handler entries. The 2.02 write table ends at
  CW0E; it has no CW0F or `CW0FC4` application-to-loader entry.

## Bounded state-transition observation

At `2026-08-30T21:16:03.899016Z`, the test transmitted remote ON (`CW0E12`).
The controller stopped producing serial replies during the immediate startup
transition. A fail-safe OFF (`CW0E11`) was transmitted 0.729 seconds later,
but the controller was still not servicing UART and did not act on it. The
saved summary therefore contains only the pre-command Off snapshot and records
the post-command timeout.

After serial replies resumed, three terminal snapshots reported `Prefill`.
This independently live-confirmed the T0C startup-family decode, but those
three console lines were not written to a capture file and are not elevated to
byte-level artifact evidence.

A second OFF was transmitted at `2026-08-30T21:17:33.322154Z`. Subsequent
read-only monitoring reported Off repeatedly. The durable two-cycle
post-recovery capture includes a fresh `T0C=20`/Off snapshot with zero poll
timeouts at `2026-08-30T21:19:06.986172Z`.

After the offline emulator and repository regressions completed, a final
read-only two-cycle capture ended at `2026-08-30T21:40:25.126282Z`. It again
reported firmware 2.02/format 04, `T0C=20`/Off, no active T08 fault indicators,
and zero poll timeouts. No control command was sent during this closeout check.

## Safety/software consequence

Transmission alone is not command acceptance on firmware 2.02. In particular,
a single cleanup OFF sent during the startup UART-silent interval is not a
cleanup guarantee. A later bounded sensor run exposed a second failure mode:
new addressed replies made a snapshot globally fresh even though its retained
T0C `20` predated ON. The live-validation harness now timestamps individual
telemetry fields and requires two distinct post-OFF T0C samples reporting Off
or Cooldown. High-level physical control remains blocked while this stronger
cleanup contract and format-04 level changes are not fully live-qualified.

## Artifacts

| Artifact | Purpose |
| --- | --- |
| `captures/baseline-backup-traffic.jsonl` | Exact complete EEPROM-read traffic |
| `fw202-format04-baseline-backup.json` | Decoded complete EEPROM backup |
| `captures/cold-off-baseline-traffic.jsonl` | Eight-cycle cold/off traffic |
| `cold-off-baseline-snapshots.jsonl` | Decoded cold/off snapshots |
| `captures/t0c-state-transition-traffic.jsonl` | ON, immediate failed cleanup OFF, and surrounding traffic |
| `t0c-state-transition-summary.json` | Conservative transition result and timeout |
| `captures/recovery-off-traffic.jsonl` | Retried OFF transmission after UART recovery |
| `captures/post-recovery-off-verification-traffic.jsonl` | Read-only final-state verification traffic |
| `post-recovery-off-verification-snapshots.jsonl` | Durable decoded final Off snapshots |
| `captures/closeout-readonly-traffic.jsonl` | Exact traffic from the post-regression read-only check |
| `closeout-readonly-snapshots.jsonl` | Two decoded closeout snapshots confirming Off |
| `captures/j9-j10-preflight-traffic.jsonl` | Read-only preflight before the bounded sensor run |
| `j9-j10-preflight-snapshots.jsonl` | Two decoded preflight Off snapshots |
| `j9-j10-startup-test/` | Aborted startup capture, stale-state incident, recovery, and forensic report |

No artifact is overwritten by the workflow, and no repository push was made.
