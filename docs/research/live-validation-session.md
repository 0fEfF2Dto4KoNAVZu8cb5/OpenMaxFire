# Guided live-validation session

`tools/live_validation_session.py` is the evidence-gathering harness for a
supervised physical controller session. It exercises the public Python API and
keeps research-only operator prompts out of the API, CLI, future GUI, and Home
Assistant layers.

## Default scope

The default workflow is read-only and performs:

1. an interactive electrical and appliance safety checklist;
2. read-only baud/profile detection and three repeated identities;
3. three complete CR00-CR0E snapshots with interleaved telemetry retained;
4. one complete A00-AFF backup with checksum and raw SHA-256;
5. repeated one-at-a-time correlations for front-panel OFF/UP/DOWN, firebox
   door, ash drawer, thermostat, fuel selector, and fan/feed trim pots;
6. exact-byte audit JSONL, individual snapshots, a structured summary, and a
   concise Markdown report.

The physical ON button is not part of the read-only input phase because it can
start the stove. Every CR02 sample retains the unresolved bits so changes can
be discovered without assigning them a meaning prematurely.

Run from an editable checkout with its virtual environment active:

```bash
python tools/live_validation_session.py \
  --port /dev/ttyUSB0 \
  --baud auto
```

The default artifact directory is `live-validation/<UTC timestamp>/` and is
ignored as an uncurated working copy. Review it for private information before
copying selected evidence into a dated directory under `research/live/`.

For a short connection/API check that skips the physical manipulations:

```bash
python tools/live_validation_session.py \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --skip-interactive-inputs
```

The harness refuses a non-empty output directory and updates `summary.json`
even after a safe abort, interruption, or connection failure.

## Optional normal-control evidence

The read-only safety checklist requires the controller to begin cold/off. In
that state, an OFF no-op cannot prove acceptance and UP/DOWN have no active
heat level to change. `--include-control` by itself therefore records those
tests as skipped and transmits no remote-control command.

A meaningful normal-control test is a separately gated, state-aware
ON → UP → DOWN → OFF sequence:

```bash
python tools/live_validation_session.py \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --include-control \
  --include-start-test
```

This requires a phase-wide phrase, a second safety checklist, and a distinct
authorization phrase for ON, UP, and DOWN. UP is sent only after the operator
positively observes startup, then DOWN restores the selected level. OFF recovery
is sent in a `finally` block. A transmitted command is never called accepted
without the corresponding operator observation.

Interactive prompts can accumulate periodic telemetry in the host receive
buffer. Before each state-changing transmission the harness ingests queued
frames through the audited transport until the serial line is idle. Operator
observations are recorded before the post-command snapshot, so a snapshot
timeout cannot erase valid physical evidence.

Use that phase only when the stove is fully assembled, correctly vented, safe
to run, continuously supervised, and the physical OFF control is immediately
available. The harness sends an OFF recovery command in a `finally` block after
an ON transmission, but this is not a substitute for the physical control or
normal stove shutdown procedure.

## Deliberately excluded

This harness contains no configuration writes, arbitrary raw traffic, factory
Checkout actuator commands, loader entry, erase, programming, or reset path.
Those require separate evidence and, for firmware work, a sacrificial and
externally recoverable controller.
