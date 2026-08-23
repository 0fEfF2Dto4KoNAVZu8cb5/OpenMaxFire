# Python API architecture and completion roadmap

Snapshot date: 2026-08-23

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
| Serial transport | Foundation complete | Cross-platform port listing, bounded I/O, timing, JSONL traffic recording, and read-only connection probing | Live-validate automatic detection on additional host/controller combinations |
| Protocol framing | Foundation complete | Strict A/C/D requests, addressed replies, telemetry/status parsing | Extend only when new valid frame families are established |
| Register access | Foundation complete | Generic A/C/D read/write, exact response matching, optional fresh readback | Resolve D-space semantics and classify controller writes |
| Raw exchange | Foundation complete | Exact-byte exchange with known loader markers blocked | Keep loader traffic outside this API |
| Transactions | Foundation complete | Validated ordered read/write/delay plans, authorization, fail-fast readback | Add typed cleanup/finally behavior and richer failure receipts |
| Identification | Offline foundation complete | Read-only port/baud probing, exact profile selection, capability negotiation, explicit no-response and unsupported results | Live-validate automatic detection on additional controllers |
| Session facade | Foundation complete | Owned connection, identity/profile/capabilities, typed polling/iteration, configuration images, and backup documents | Add async subscriptions only when a client requires them |
| EEPROM backup | Read path complete | Lossless A00-AFF read, identity metadata, checksum diagnostics, and shared import/validation model | Additional live fixtures from other formats/controllers |
| Monitor | Typed foundation complete | Profile-aware immutable snapshots, raw preservation, freshness, format-04 conservative decoding, format-05/07 conversions, replay | Resolve remaining flags, physical calibration, M/I payloads, and live-validate later formats |
| Normal control | Simulator workflow complete; physical execution blocked | Typed plans plus authorization, idempotence, rate/door/drawer/profile/stale interlocks, simulated state transitions, fresh-state verification, structured outcomes | Live-validate OFF/ON/UP/DOWN and define physical recovery timing before enabling the executor |
| Configuration | Simulator workflow complete; physical execution blocked | Schemas/plans plus fresh pre-write comparison, backup hash, authorized apply, firmware checksum persistence, and complete A00-AFF verification in simulation | Live-validate write order/readback on recoverable hardware; reconstruct format-04 fields and expert formatting |
| Checkout | Read-only runner and simulated cleanup complete | All 45 tests as data; automated tests 1-8, 11-14, 16, 33-34, and 36-37; bounded polling; reports; simulator-only actuator executor with unconditional cleanup | Add remaining evidence-backed predicates and physically validate each actuator/cleanup pair |
| Firmware images | Offline foundation complete | Strict Intel HEX validation, PIC14 address mapping, delivery-layout classification, compatibility/migration reports, E3 block construction | Add calibration-preservation policy for actual programming and validate against every preserved image in CI |
| Firmware loader | Deliberately blocked | Constants, E3 frames, compatibility gates, and explicit unsupported state | Loader identify, enter, erase, ack/retry state machine, interruption recovery, verification, reset, and sacrificial-hardware validation |
| Error/result model | Foundation complete | Stable base exceptions plus domain-specific detection, control, Checkout, transaction, configuration, and firmware results | Use the common taxonomy in future live service executors |
| Simulation | Service workflow foundation complete | Public controller/transport/factory, telemetry/state transitions, firmware checksum behavior, writes-disabled default, and fault injection | Add richer timelines and loader models only as semantics are proven |

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
- Identify the controller/loader and reject incompatible images before erase.
- Implement loader entry as a dedicated state transition.
- Model erase, block programming, acknowledgements, retry limits, and progress.
- Recover or provide a deterministic recovery result after interrupted transfer.
- Verify programmed contents where the loader permits it, reset cleanly, and
  report post-flash calibration/restoration requirements.
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

## Remaining implementation order

1. Live-validate normal control before allowing the existing verified executor
   to operate on a physical session.
2. Validate the simulator-proven configuration workflow first on recoverable
   hardware before allowing physical apply/restore.
3. Live-validate each Checkout actuator/cleanup pair before physical execution.
4. Resolve the loader acknowledgements/recovery path in emulation and then on a
   sacrificial controller before enabling any erase/program operation.
5. Fill remaining telemetry/configuration semantics only as new evidence lands.

Physical validation remains an evidence gate for declaring an API operation
supported, but CLI design, GUI design, and Home Assistant entity design are not
part of this roadmap.
