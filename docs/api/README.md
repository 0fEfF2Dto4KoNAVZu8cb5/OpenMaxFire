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
| Serial transport | Foundation complete | Cross-platform port listing, bounded I/O, timing, JSONL traffic recording | Add connection probing without unsafe writes |
| Protocol framing | Foundation complete | Strict A/C/D requests, addressed replies, telemetry/status parsing | Extend only when new valid frame families are established |
| Register access | Foundation complete | Generic A/C/D read/write, exact response matching, optional fresh readback | Resolve D-space semantics and classify controller writes |
| Raw exchange | Foundation complete | Exact-byte exchange with known loader markers blocked | Keep loader traffic outside this API |
| Transactions | Foundation complete | Validated ordered read/write/delay plans, authorization, fail-fast readback | Add typed cleanup/finally behavior and richer failure receipts |
| Identification | Partial | Read-only controller identity sequence | Safe baud probing, profile selection, capability negotiation, unsupported-profile result |
| EEPROM backup | Read path complete | Lossless A00-AFF read, identity metadata, checksum diagnostics | Stable import/validation model shared by restore |
| Monitor | Partial | Latest-value state, staleness, raw fields, selected decoding, replay | Complete named fields, flags, calibration, alarms, M/I payloads, and format-specific decoding |
| Normal control | Primitive only | Reconstructed remote-button requests and generic writes | Verified OFF/ON/UP/DOWN operations, resulting-state checks, idempotence, rate limits, lockouts, and recovery |
| Configuration | Read-only foundation | Full EEPROM backup and checksum calculation | Typed field schema, ranges, diff, compatibility checks, ordered apply, checksum write, full verification, restore, and formatting/individualization workflows |
| Checkout | Not implemented | Static knowledge of the 45 factory tests and low-level transaction primitives | Typed test catalog, prerequisites, input evaluation, bounded actuator tests, interlocks, mandatory cleanup, and structured reports |
| Firmware images | Research only | Recovered Downloader/PICkit layouts and static framing knowledge | Validated image objects, metadata, target compatibility, address bounds, and calibration-preservation policy |
| Firmware loader | Not implemented | Loader traffic isolated from generic raw/register paths | Loader identify, enter, erase, program, acknowledgements, retries, verification, interruption recovery, reset, and post-flash result |
| Error/result model | Partial | Receipts and transaction results | Stable exception/result taxonomy across discovery, monitor, control, configuration, Checkout, and loader services |
| Simulation | Experimental | Standalone virtual serial lab and firmware emulator | Public API-compatible simulated transport/controller with deterministic scenarios and fault injection |

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

## Implementation order

1. Add safe discovery, controller profiles, and capability negotiation.
2. Complete the typed monitor/state model.
3. Implement and live-validate verified normal control.
4. Build configuration diff/apply/restore with whole-image verification.
5. Build the Checkout catalog and bounded execution engine.
6. Build the isolated firmware-image and loader state machines.
7. Promote the virtual lab into an API-compatible simulation/fault backend.

Physical validation remains an evidence gate for declaring an API operation
supported, but CLI design, GUI design, and Home Assistant entity design are not
part of this roadmap.
