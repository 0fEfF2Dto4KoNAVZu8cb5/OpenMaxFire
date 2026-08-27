# Python API architecture and completion roadmap

Snapshot date: 2026-08-27

This document tracks the reusable Python API required to reproduce BixCheck's
machine-facing behavior. It deliberately excludes command-line syntax, GUI
screens, Home Assistant entities, packaging, and other presentation concerns.
Those are separate consumers of the API.

## Boundary

`src/openmaxfire/` is the authoritative implementation of controller behavior.
Every client must call this package instead of duplicating register addresses,
serial framing, safety rules, or firmware-loader logic.

| Layer | Responsibility | Must not contain |
| --- | --- | --- |
| Protocol | Frames, checksums, byte encodings, parsed response types | Serial-port or interface policy |
| Transport | Bounded byte I/O, timing, port discovery, traffic recording | Stove register meanings |
| Register client | A/C/D reads and writes, response matching, transactions | BixCheck screen concepts |
| Controller profile | Firmware/data-format capabilities, register and telemetry semantics | CLI flags or GUI widgets |
| Service APIs | Monitor, control, configuration, Checkout, and firmware workflows | Printing, prompts, or Home Assistant entities |
| Client applications | CLI, GUI, Home Assistant, research tools | Independent protocol implementations |

The dependency direction is one-way: clients may depend on the API; the API
must never depend on a CLI, GUI, or Home Assistant integration.

Human confirmation belongs to the calling application. Machine-enforceable
rules still belong in the API: compatibility checks, ranges, interlocks,
timeouts, cleanup, verification, and refusal of unsupported operations.

## Definition of API parity

The API reaches BixCheck parity when a Python caller can perform every Monitor,
configuration, Checkout, debug, and Downloader operation without constructing
raw controller bytes or knowing firmware-specific addresses. Each call must
return structured data and a definite outcome; transmission alone is never
reported as controller acceptance or physical success.

Raw register and byte access remains available for research, but it is an
escape hatch rather than the implementation of high-level parity.

## Current capability matrix

| API area | Status | Present foundation | Remaining API work |
| --- | --- | --- | --- |
| Serial transport | Foundation complete | Cross-platform port listing, bounded I/O, read-only probing, legacy JSONL capture, and API-native exact-byte `AuditTrail` sessions/spans | Live-validate automatic detection on additional host/controller combinations |
| Protocol framing | Foundation complete | Strict A/C/D requests, addressed replies, telemetry/status parsing | Extend only when new valid frame families are established |
| Register access | Foundation complete | Generic A/C/D read/write, exact response matching, optional fresh readback | Resolve D-space semantics and classify controller writes |
| Raw exchange | Foundation complete | Exact-byte exchange with known loader markers blocked | Keep loader traffic outside this API |
| Transactions | Foundation complete | Validated ordered read/write/delay plans, authorization, fail-fast readback, and transport-level audit evidence | Add cleanup only to domain workflows that require it; do not guess generic rollback semantics |
| Identification | Offline foundation complete | Read-only port/baud probing, exact profile selection, capability negotiation, explicit no-response and unsupported results | Live-validate automatic detection on additional controllers |
| Session facade | Foundation complete | Owned connection, identity/profile/capabilities, typed polling/iteration, configuration images, and backup documents | Add async subscriptions only when a client requires them |
| EEPROM backup | Read path complete | Lossless A00-AFF read, identity metadata, checksum diagnostics, and shared import/validation model | Additional live fixtures from other formats/controllers |
| Monitor | Typed foundation complete | Profile-aware immutable snapshots, raw preservation, freshness, temporal format-04 fault indicators, non-control format-04 composite state candidates, raw later-format alarm status, format-05/07 conversions, and replay | Resolve format-04 phase/level verification, remaining flags, physical calibration, M/I payloads, and live-validate later formats |
| Normal control | Low-level commands live-validated on 2.02; verified service execution blocked | Typed plans plus authorization, idempotence, rate/door/drawer/profile/stale interlocks, simulated state transitions, fresh-state verification, exact audit spans, interruption receipts, and preserved physical OFF/ON/UP/DOWN traffic | Resolve format-04 state/level verification and recovery timing before enabling the high-level physical executor |
| Configuration | Simulator workflow complete; physical execution blocked | Schemas/plans plus fresh pre-write comparison, backup hash, authorized apply, firmware checksum persistence, complete A00-AFF verification, audit spans, and interruption receipts | Live-validate write order/readback on recoverable hardware; reconstruct format-04 fields and expert formatting |
| Checkout | Read-only runner and simulated cleanup complete | All 45 tests as data; automated tests 1-8, 11-14, 16, 33-34, and 36-37; bounded polling; audit spans; reports; simulator-only actuator executor with unconditional cleanup | Add remaining evidence-backed predicates and physically validate each actuator/cleanup pair |
| Firmware images | Offline validation and preservation toolkit complete | Strict Intel HEX/PIC14 parsing, delivery-layout classification, compatibility/migration reports, E3 block construction, authenticated factory corpus, and read-export/clone section hashes with CP/CPD fail-closed checks | Read/authenticate original 2.02 three times; add calibration-preservation policy for any future physical programming |
| Firmware loader | Evidence-backed offline state machine complete; physical execution absent | `EA/EB`; classified `E8` and `E7`→`E5/E4`; four-word partial rows and two PIC attempts; `0x1E80` protection; reset relocation; exact 30 accepted/31st unread loop; one-shot `ED/E4`; simulated handoff/reconnect; audit and interruption faults | Validate physical timing, row behavior, completion, and recovery on sacrificial hardware before any serial executor |
| Error/result model | Foundation complete | Stable exceptions plus typed detection, control, Checkout, transaction, configuration, firmware, audit, and loader results; interrupted simulator workflows fail indeterminate/failed | Use the common taxonomy in future physically validated executors |
| Simulation | Broad offline workflow complete | Register and isolated loader transports, writes-disabled default, telemetry/state transitions, checksum behavior, retries, corruption, disconnects, and cleanup faults | Add only evidence-backed timing/peripheral behavior |

The register-level mechanics are close to complete. Most remaining work is the
controller-aware semantic and workflow layer that makes those mechanics safe,
version-aware, and sufficient for BixCheck parity.

## Required service APIs

### Discovery and capabilities

- Enumerate candidate serial ports without opening them.
- Probe supported baud rates using read-only identity requests.
- Return controller firmware, data format, pairing status, and evidence level.
- Select a matching controller profile or return an explicit unsupported result.
- Expose capabilities so callers never infer support from a version string.

### Monitoring

- Decode all stable controller and telemetry fields into typed snapshots.
- Preserve raw values alongside decoded values and their evidence/provenance.
- Represent state, heat level, alarms, temperatures, fans, feed, door/drawer,
  thermostat, ash, flue, lean-burn, timers, and freshness.
- Retain flashing indicators across their dark phase without treating stale
  serial traffic as proof that a fault cleared.
- Support polling, unsolicited-frame ingestion, subscriptions, and offline replay
  through the same state model.
- Never fabricate a semantic value for an unknown firmware/data-format field.

### Normal control

- Provide OFF, ON, UP, DOWN, and explicit target-level operations.
- Determine whether a requested operation is already satisfied.
- Enforce profile support, controller-state prerequisites, rate limits, and
  lockouts before transmission.
- Observe the resulting controller state and distinguish `sent`, `accepted`,
  `verified`, `rejected`, `timed_out`, and `indeterminate` outcomes.
- Define bounded recovery behavior after partial or ambiguous operations.

### Configuration and calibration

- Decode and encode every BixCheck field using a data-format-specific schema.
- Validate types, ranges, cross-field constraints, and controller compatibility.
- Produce a no-I/O diff and an ordered write plan.
- Take a mandatory pre-write backup before applying changes.
- Write data and checksum bytes in the proven order and verify the entire result.
- Restore from a compatible backup without silently changing identity fields.
- Isolate full formatting and controller individualization as expert operations.

### Factory Checkout

- Represent all 45 documented tests as data, not interface-specific code.
- Separate passive input tests from state-changing actuator tests.
- Encode prerequisites, expected observations, time limits, and abort criteria.
- Guarantee actuator-off cleanup on success, failure, cancellation, or exception.
- Preserve the pre-test calibration and return a structured, durable report.

### Firmware servicing

- Parse and validate both recovered firmware delivery layouts.
- Identify the controller and loader, then reject incompatible images before programming.
- Keep loader entry as a dedicated future live state transition; it is not in
  the normal register client or the current loader simulator.
- Model proven block programming, acknowledgements, retry limits, and progress.
  There is no host-side erase exchange; the PIC erases and writes each four-word
  Flash row inside its self-programming routine.
- Recover or provide a deterministic recovery result after interrupted transfer.
- Distinguish the PIC's per-block readback from a host-side whole-image
  verification, reset cleanly, and report post-flash calibration/restoration
  requirements.
- Keep PIC ICSP program-memory preservation separate from the J3 service API;
  no J3 program-memory dump command is currently known.

## Cross-cutting contracts

Every state-changing service API must:

1. Require explicit programmatic authorization from its caller.
2. Check the detected controller profile and current state first.
3. Apply bounded timeouts and retry limits.
4. Preserve exact traffic suitable for diagnosis.
5. Return a structured result with evidence for its conclusion.
6. Run mandatory cleanup where the operation can leave an actuator energized.
7. Fail closed when state, compatibility, or outcome is unknown.

The API does not print, prompt, render controls, choose Home Assistant entities,
or decide how an operator acknowledgement is displayed. Those responsibilities
belong to their respective client projects.

## Implemented v0.5 foundation

Version 0.5 implements the no-hardware portions of every service domain:

1. Read-only detection and exact profiles for 2.02/04, 2.06/05, 2.70/07,
   and 2.71/07.
2. A shared typed snapshot model with profile-driven conservative decoding.
3. Idempotence-aware normal-control plans whose transmission remains blocked.
4. Format-05/07 configuration schemas, edits, diffs, restore plans, firmware
   checksum persistence through `CW0100`, and full A00-AFF verification plans.
5. A machine-readable catalog and planner for all 45 Checkout tests.
6. Strict Intel HEX/PIC14 images, compatibility reports, and reconstructed E3
   loader blocks, without a live loader executor.
7. An API-compatible simulator/fault backend and a public error taxonomy.

See [v0.5 API reference and evidence boundary](v0.5-foundations.md) for the
public objects, examples, and precise execution limits.

## Implemented v0.6 service layer

Version 0.6 composes the v0.5 domains into presentation-neutral workflows:

1. `ControllerSession` owns one connection, exact identity/profile, accumulated
   monitor state, typed polling/iteration, and read-only configuration access.
2. `ReadOnlyCheckoutRunner` automates every currently machine-evaluable
   non-writing Checkout test and never fabricates manual or actuator success.
3. Configuration apply verifies its source is still current, records a backup
   hash, runs only with explicit authorization on the simulator, persists the
   firmware checksum, and compares every A00-AFF byte afterward.
4. Normal control adds authorization, idempotence, rate limiting, input
   interlocks, simulated state transitions, and fresh resulting-state checks.
5. The simulated Checkout executor guarantees cleanup in `finally`, including
   when its observation provider fails.

See [v0.6 unified sessions and safe workflows](v0.6-services.md).

## Implemented v0.7 audit and loader laboratory

Version 0.7 fills the largest remaining offline/API gaps:

1. `AuditTrail` records exact TX/RX chunks in memory and optionally flushes each
   event to JSONL. Stable checkpoints produce byte-counted, SHA-256 audit spans
   that are attached to control, configuration, Checkout, and loader results.
2. A typed loader planner and retry-bounded state machine implement only the
   statically established `EA`/`EB`, `E3`/`E7`/`E4`, and `ED`/`E4` exchanges.
3. The loader executor accepts only `SimulatedLoaderTransport`; it has no port
   constructor and no `CW0FC4` entry, erase, reset, or live-write path.
4. The loader simulator validates block length/checksum/address, reconstructs
   programmed PIC14 words, and injects identify/block/completion failures,
   disconnects, and silent corruption.
5. `FIRMWARE_CORPUS` authenticates the four preserved images by path, size,
   SHA-256, version, variant, program-word count, and configuration word.
6. Control and configuration workflows now return structured interrupted
   results with their exact audit evidence rather than allowing an ambiguous
   post-write transport failure to masquerade as success.

See [v0.7 audit, firmware corpus, and loader laboratory](v0.7-audit-loader-lab.md).

## Current main after v0.7

The live firmware-2.02 control/fault session adds two evidence-backed API
improvements without weakening the physical-write gates:

1. `AlarmState` separates format-04 `T08` flashing indicators from later
   BixCheck `T13` raw alarm status.
2. `MonitorState` retains format-04 indicator bits across the lamp's dark phase
   using observed telemetry time, with a configurable eight-second default.
3. All factory-documented light combinations have stable machine codes and
   evidence labels. Lights 4, 5, and 8 are live-confirmed; other bit positions
   remain explicitly inferred.
4. Exact physical OFF/ON/UP/DOWN and feeder-wheel-fault captures are preserved
   as replay fixtures. Low-level control is live-proven, but the high-level
   service remains blocked until format-04 state verification is reliable.

See the [fault-state API contract](fault-model.md).

## Remaining implementation order

1. Decode and live-validate format-04 operating state/target level so the
   already live-proven OFF/ON/UP/DOWN bytes can receive machine verification
   before the high-level executor operates on a physical session.
2. Validate the simulator-proven configuration workflow first on recoverable
   hardware before allowing physical apply/restore.
3. Live-validate each Checkout actuator/cleanup pair before physical execution.
4. Read the original 2.02 chip three times, authenticate program/EEPROM/config/
   User IDs, prove a spare clone and external recovery, then validate physical
   loader timing and interruption recovery on sacrificial hardware before
   creating a live loader transport.
5. Fill remaining telemetry/configuration semantics only as new evidence lands.

Physical validation remains an evidence gate for declaring an API operation
supported, but CLI design, GUI design, and Home Assistant entity design are not
part of this roadmap.

## Implemented v0.8 offline preservation milestone

Version 0.8 completes the currently evidence-backed loader simulator details,
corrects format-04 T09 interpretation from the preserved live control traffic,
and adds fail-closed PIC16F877A dump/clone comparison. See
[v0.8 offline loader fidelity and firmware preservation](v0.8-offline-preservation.md).
