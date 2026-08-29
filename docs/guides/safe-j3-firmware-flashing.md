# Guarded J3 firmware flashing

Status: release-candidate host implementation, exhaustively fault-injected
offline. Physical zero-write sessions have now observed `EA/EB` and `ED/E4`,
but loader-entry electrical/reset behavior, Flash programming, and recovery are
**not qualified on sacrificial hardware**. Do not use a production controller
until the qualification matrix has passed and complete PICkit recovery has been
programmed, read back, authenticated, and exercised on a spare PIC/controller.
The command refuses to proceed without an explicit confirmation of that
recovery test.

This is the dedicated replacement for BixCheck Downloader. Loader traffic is
not exposed through generic raw mode, and this workflow never sends the
application's `CW0FC4` software-reset command. Loader entry uses a manual stove
AC power cycle only.

## The unavoidable boundary

The PIC16F877A has one application program-memory space, not two switchable
application banks. A J3 update is therefore in-place. Software cannot guarantee
that the application remains runnable during every interruption.

The recoverable design boundary is stronger and narrower:

- Downloader images cannot directly replace the resident loader at
  `0x1E80`-`0x1FFF`;
- application reset words `0x0000`-`0x0003` are redirected to the protected
  trampoline at `0x1E84`-`0x1E87`;
- the vendor manual says an interrupted update can be attempted again because
  the update software is not damaged;
- every session preserves the exact authenticated HEX required to replay the
  image from block zero;
- a conspicuous recovery marker exists before the first possible `E3` frame
  and remains until post-flash application and EEPROM verification pass.

J3 cannot recover a physically failing PIC, unstable controller supply,
damaged socket, or loader/reset region erased by external programming. Those
conditions require the proven external-programmer path.

The vendor interruption warning and retry statement are on page 24 of the
[preserved BixCheck service manual](../../preservation/original/manuals/1394047.pdf).

## What the tool proves

Before a write, OpenMaxFire requires all of the following:

- three identical controller-identity reads selecting an exact preserved
  profile;
- two byte-identical complete `A00`-`AFF` reads;
- a valid stored EEPROM checksum and matching controller/EEPROM data format;
- one of three exact authenticated J3 images, matched by SHA-256, filename,
  delivery variant, program-word count, configuration word, block count, and
  the SHA-256 of the complete on-wire frame sequence;
- a successful whole-image run through the strict loader simulator;
- a self-contained recovery bundle containing the exact HEX, preparation, and
  EEPROM backup with a hash manifest;
- a non-writing physical rehearsal: `EA/EB`, then `ED/E4`, with **zero `E3`
  frames**;
- after `ED/E4`, a transmit-silent wait for unsolicited `T` or periodic `DW`
  application telemetry before the first `CR00`;
- three unchanged application identities and two unchanged EEPROM reads.

During and after a write, it requires:

- fixed 9,600-baud loader transport;
- an `E7` payload acceptance followed by `E4` PIC-side write/readback evidence
  for every block;
- bounded outcome-specific retry decisions;
- target application identity repeated three times at the target baud;
- two identical complete post-flash EEPROM reads;
- byte-for-byte equality with the pre-flash EEPROM.

`E4` is the resident loader's local readback result. J3 has no independent
whole-program-memory read command. A PICkit readback on expendable hardware is
the independent whole-chip verification method.

## Firmware and MCU evidence

The byte-identical 2.02/2.06 resident loader sets `SPBRG=0x40` with the board's
10.000 MHz oscillator. That is the 9,600-baud setting. Firmware 2.70 and 2.71
use 19,200 only after application handoff.

At reset, the loader permits approximately three Timer1 overflow periods for
its first byte. The recovered instructions and 10 MHz oscillator put this
window near 78 ms. OpenMaxFire uses a 20 ms read timeout for rapid `EA` probes,
then changes to a 500 ms block-response timeout.

The recovered PIC machine code has also been emulated with `EA ED` queued at
reset. It consumes both bytes, returns exactly `EB E4`, and enters the original
application path without an `E3` transfer. Physical zero-write sessions 003,
004, and 006 reproduced those identify and completion acknowledgements on
serial 5215. Those sessions did not qualify Flash programming or the electrical
loader-entry path.

Those same sessions exposed an application-handoff defect in host version 0.9:
the first `CR00` was sent about 0.76-0.78 seconds after final `E4`, while
firmware 2.02 could have its USART receiver enabled before its receive interrupt
was ready. Four request bytes can overrun the PIC16F877A's two-byte receive
FIFO; Microchip documents that `OERR` then blocks further receive activity until
`CREN` is reset. Version 0.9.1 therefore treats unsolicited periodic telemetry,
not elapsed time, as application readiness. It sends no application bytes until
a valid `T` or `DW` frame is received.

Microchip specifies edge-aligned four-word Flash erase/write blocks, loading
untouched neighbors when only part of a row changes, and a typical 4 ms halt on
the final erase/write operation. It also documents `WRERR` when a write is
interrupted by reset. See the official [PIC16F87XA data
sheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/39582C.pdf),
sections 3.1 and 3.6.

## Mandatory physical prerequisites

Every live or recovery command requires confirmation that:

1. The stove is cold and OFF.
2. Both igniters are physically unplugged.
3. The exact traced 9067-0604 5 V TTL wiring is used: adapter TX/orange to
   J3-1, adapter RX/yellow to J3-2, and ground/black to J3-4.
4. J3 pin 3 is disconnected.
5. Adapter VCC is disconnected. Do not inject USB 5 V into J3.
6. Complete PICkit recovery has been proven on a spare PIC/controller, not
   merely planned or assumed.
7. The computer is on stable power and its lid will remain open.
8. Stove AC will remain stable for the complete programming window.
9. The target-version calibration procedure is ready.

The flasher also acquires a host sleep inhibitor during the destructive window:
Windows `SetThreadExecutionState`, macOS `caffeinate`, or Linux
`systemd-inhibit`. It fails before programming if that inhibitor cannot be
established. These mechanisms cannot prevent mains loss, forced shutdown,
SIGKILL, or every lid-close policy. See the platform documentation for
[Windows execution state](https://learn.microsoft.com/windows/win32/api/winbase/nf-winbase-setthreadexecutionstate),
[Apple power assertions](https://developer.apple.com/documentation/iokit/1557134-iopmassertioncreatewithname),
and [systemd inhibitor locks](https://www.freedesktop.org/software/systemd/man/latest/systemd-inhibit.html).

The helper is checked again after the operator's power-off phrase, immediately
before any possible `E3`, and at progress checkpoints. If it disappears before
programming, the tool stops. If it disappears after a block may be partial, the
tool records the failure and finishes the exact image rather than deliberately
abandoning it.

The tool opens one serial handle and retains it across preflight, rehearsal,
programming, and post-verification. On POSIX it requests pySerial exclusive
mode; Windows serial handles are natively exclusive. Baud and timeout are
changed on that open handle. This removes the phase-to-phase port race and
avoids additional DTR/RTS transitions. pySerial's [native-port
API](https://pyserial.readthedocs.io/en/latest/pyserial_api.html) documents
exclusive mode and warns that opening a port can glitch DTR/RTS.

Do not connect RS-232 voltage levels to J3. Do not reconnect the igniters just
because programming completed.

## Authenticate the plan offline

For a 2.06 controller being upgraded to 2.70:

```bash
maxfirectl flash \
  reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex \
  --plan-only \
  --current-profile fw206-format05
```

This opens no serial port. The report should name target
`fw270-format07`, loader baud 9,600, application baud 19,200, 481
authenticated blocks, a data-format migration, and no software reset.

Unknown, modified, renamed, PICkit, and firmware 2.73 images are blocked.
For 2.73, contact [contact@openmaxfire.com](mailto:contact@openmaxfire.com) and
provide the original image to the
[OpenMaxFire project](https://github.com/OpenMaxFire/OpenMaxFire) for
preservation and analysis.

Same-version rewrites and J3 downgrades are also blocked. Sparse downgrades can
leave stale newer program words. Session-bound recovery is the only exact-image
replay path.

## Run only the non-writing rehearsal

This exercises the real adapter, wiring, reset window, resident loader, handoff,
original application, and EEPROM without transmitting an `E3` block:

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --timeout 0.50 \
  flash reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex \
  --rehearsal-only \
  --session-dir flash-sessions/rehearsal-001 \
  --confirm-stove-cold-and-off \
  --confirm-igniters-unplugged \
  --confirm-correct-5v-ttl-wiring \
  --confirm-j3-pin3-disconnected \
  --confirm-adapter-vcc-disconnected \
  --confirm-pickit-recovery-tested-on-spare \
  --confirm-computer-power-stable \
  --confirm-stove-power-stable \
  --confirm-calibration-plan
```

The tool requires the exact phrase `POWER OFF FOR REHEARSAL` after AC is
physically disconnected. A successful rehearsal result explicitly reports
`program_blocks_sent=0` and `flash_write_commands_sent=0`. After `ED/E4`, it
waits up to 30 seconds for unsolicited `T` or `DW` telemetry while transmitting
nothing. If telemetry never arrives, it fails without sending `CR00`. The
timeout can be changed with `--application-ready-timeout`, but increasing it
does not repair an electrical reset or backfeed problem.

## Live update

Use the controller's **current application baud** in the global `--baud`
option. The tool switches the retained handle to 9,600 for each loader entry
and to the known target application baud after handoff.

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --timeout 0.50 \
  flash reverse-engineering/firmware/2.06/extracted/Bixby_02060021_Downloader.hex \
  --session-dir flash-sessions/fw202-to-fw206-001 \
  --confirm-stove-cold-and-off \
  --confirm-igniters-unplugged \
  --confirm-correct-5v-ttl-wiring \
  --confirm-j3-pin3-disconnected \
  --confirm-adapter-vcc-disconnected \
  --confirm-pickit-recovery-tested-on-spare \
  --confirm-computer-power-stable \
  --confirm-stove-power-stable \
  --confirm-calibration-plan
```

The session directory must not exist. The command performs the complete
preflight and first prompts for `POWER OFF FOR REHEARSAL`. After that cycle
returns to the unchanged original application, it acquires the sleep inhibitor
and prompts for the separate phrase `POWER OFF FOR FLASH`.

Before the tool asks the operator to restore AC for programming, it writes
`RECOVERY_REQUIRED.txt` and a durable `state.json`. Keep AC, USB, J3, and the
computer stable until the final result appears.

Ordinary Ctrl+C, SIGTERM, and Windows SIGBREAK are deferred from the moment
programming is armed until the critical loader call ends. The request is
recorded by a minimal signal handler, then reported and journaled after the
critical exchange; it does not intentionally abandon a partial image.
Power loss, forced process kill, kernel failure, or unplugged hardware cannot be
deferred.

## Retry policy

Every retry sends the same authenticated block. No arbitrary resume address is
accepted, and the BixCheck terminal transmission whose response is never read
is not reproduced.

| Outcome | Host action |
| --- | --- |
| `E8` before programming | Up to two retries; `E8` proves the payload was rejected before a write. |
| Timeout before `E7` | Up to two cautious retries. The missing reply is ambiguous; it does not prove the PIC failed to write. |
| Timeout after `E7` | One identical retry because the prior write may have completed. |
| First `E5` in the session | One identical retry. The PIC has already exhausted its two internal row-write attempts. |
| Second `E5`, on the same or a later block | Immediate abort and exact-image recovery requirement. |
| Unexpected byte sequence | Immediate abort; framing may be lost. |
| Serial write/read error | Immediate abort; reconnecting blindly cannot establish what reached the PIC. |

No block can be transmitted more than four times even if different failure
classes occur. A delayed `E4` is accepted only after that same attempt already
consumed `E7`; a delayed `E7 E4` pair is accepted only after neither byte was
seen. Other late byte sequences abort, so a stray `E4` after `E5` or `E8`
cannot forge success.

If one `E5` retries successfully, the transfer continues because finishing the
application is safer than intentionally leaving a mixed image. The final result
records the anomaly and requires qualified socket/contact and controller-VDD
inspection before operation. A second `E5` is treated as systemic.

Progress is printed every 25 blocks and at the first/final block. Every failed
attempt is printed immediately with its address, attempt number, classified
outcome, retry/abort decision, and reason. Journal, byte-traffic, and console
failures are recorded when possible but are not allowed to interrupt an image
once programming may be partial. If a post-write traffic recorder cannot open
or fails mid-read, repeated target identity and EEPROM verification continue on
the already-open handle; the final result reports incomplete diagnostics.

## Automatic exact-image recovery

If `RECOVERY_REQUIRED.txt` remains, do not operate the stove, reconnect the
igniters, edit the failed session, choose another image, or guess a checkpoint.
Start a new output directory and point at the failed session:

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --timeout 0.50 \
  flash \
  --session-dir flash-sessions/fw202-to-fw206-recovery-002 \
  --recover-from-session flash-sessions/fw202-to-fw206-001 \
  --confirm-stove-cold-and-off \
  --confirm-igniters-unplugged \
  --confirm-correct-5v-ttl-wiring \
  --confirm-j3-pin3-disconnected \
  --confirm-adapter-vcc-disconnected \
  --confirm-pickit-recovery-tested-on-spare \
  --confirm-computer-power-stable \
  --confirm-stove-power-stable \
  --confirm-calibration-plan \
  --confirm-recovery-target-matches-backup
```

No image argument is needed. The source must still contain both a durable state
with `recovery_required=true` and `RECOVERY_REQUIRED.txt`; a completed session
cannot be reused to bypass the same-version/no-downgrade rules. Recovery loads
the exact HEX from the failed session's `rescue/` directory, verifies its
allowlist hash, file size, manifest, preparation, profile, identity, and EEPROM
cross-links, reparses all 256 raw/addressed EEPROM bytes, rebuilds the canonical
wire sequence, reruns whole-image simulation, and replays from block zero.

Before the power-cycle prompt, the new session creates its own marker and exact
rescue bundle, then atomically takes recovery responsibility from the old
session. The old session receives `RECOVERY_DELEGATED_TO.json` and loses its
active marker. If this recovery fails or is aborted, continue from the **new**
session named in that delegation record. This prevents accidental replay of an
old recovery bundle after a later attempt has changed the PIC again.

Recovery skips the non-writing rehearsal because the old application may
already be incomplete. Loader mode cannot report application identity, so the
operator must confirm that the physical target is the controller represented
by the backup.

| Evidence at failure | Meaning and next action |
| --- | --- |
| No `EB`, no `E3` in a normal session | This attempt did not start programming. Fix the loader-entry condition and rerun normally. |
| Any `E3` may have been sent without final `E4` | `RECOVERY_REQUIRED`; replay the exact session image from block zero. |
| Every block has `E4`, final `ED/E4` missing | The tool first tries the target application. If that fails, it probes the still-open handle at 9,600 and sends one more `ED` only after `EB`. |
| Target identity and unchanged EEPROM verify | The recovery marker is removed; calibration or E5 inspection can still block operation. |
| Neither target application nor resident loader answers | Remove stove AC and use the proven PICkit/spare recovery path. |

## Session artifacts and states

Every live session attempts to preserve:

- `state.json`, atomically replaced for each major state;
- `RECOVERY_REQUIRED.txt` whenever exact replay is required;
- `RECOVERY_DELEGATED_TO.json` in a recovery source after a newer self-contained
  session assumes responsibility;
- `preflight-traffic.jsonl` for a normal session;
- `eeprom-before.json` and `preparation.json`;
- `offline-qualification.json`;
- `rescue/<exact-vendor-filename>.hex` and
  `rescue/recovery-manifest.json`;
- `rehearsal-traffic.jsonl`, `rehearsal-loader-result.json`,
  `rehearsal-app-traffic.jsonl`, `rehearsal-application-readiness.json`,
  `rehearsal-verification.json`, and `rehearsal-eeprom.json` for a normal
  session;
- `journal.jsonl`, flushed and `fsync`'d after each state event while the
  diagnostic sink remains healthy;
- `loader-traffic.jsonl`, flushed and `fsync`'d for every non-empty TX/RX
  event while the diagnostic sink remains healthy;
- `loader-result.json`;
- `postflash-readiness-<attempt>.json`, post-flash traffic,
  `eeprom-after.json`, and `result.json`.

The high-level states distinguish `failed_before_programming` from
`recovery_required`, `programming_verified_calibration_required`, and
`complete_verified`. A failed session directory is evidence and the recovery
source. Do not edit it.

CLI exit codes relevant to flashing are:

| Code | Meaning |
| --- | --- |
| `0` | Requested rehearsal or programming verification completed. Check `ready_for_operation`. |
| `2` | Invalid command arguments. |
| `3` | Operator phrase/gate abort before this session's program traffic. |
| `4` | Pre-programming validation, file, serial-open, or sleep-inhibitor error. |
| `5` | Loader/rehearsal failure with no new partial image from this normal session. |
| `6` | Recovery is required or remains required, including a failed or aborted recovery command. |
| `130` | Interrupt occurred before the protected programming section. |

## Calibration after an update

The factory Downloader images contain no EEPROM records, so J3 leaves the old
calibration bytes in place. The 2.06 release notes require Monitor model
selection, **Individualize**, **Calculate Fuel A/B**, and **Format** after the
firmware/data-format update. BixCheck 5.5.01 also emphasizes calibration.

Every supported normal transition changes firmware version, so OpenMaxFire
reports `ready_for_operation=false` after programming. Keep both igniters
disconnected and do not operate the stove until the target-version procedure is
complete. A recovered `E5` adds a qualified hardware-inspection requirement.
Back up the newly calibrated EEPROM separately.

## Release qualification

Passing software tests does not convert emulator evidence into physical
evidence. The stable-release gate and forced-interruption matrix are in the
[J3 flasher qualification plan](j3-flasher-qualification.md). Until that matrix
passes, treat the live executor as a recoverable bench instrument, not a
consumer updater.
