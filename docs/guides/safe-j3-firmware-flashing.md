# Guarded J3 firmware flashing

Status: **physical J3 programming is not qualified**. The first `E3` attempt on
2026-08-29 exposed a host/simulator word-byte-order defect: the loader accepted
the order-insensitive checksum (`E7`), but PICkit readback showed three
byte-swapped relocated reset-vector words. The adverse readback physically
anchors the diagnosis of the old encoding; BixCheck assembly and the strict
simulator anchor the corrected encoding. The corrected frame itself has not
been physically tested. After an operator-reported external restore from the
sole pre-write 2.02 image, the controller showed a normal 2.02 boot and matching
J3 identity/EEPROM; no post-program whole-chip readback was retained.

The offline host is exhaustively fault-injected, and historical physical
zero-write sessions observed `EA/EB` and `ED/E4`. Neither result qualifies the
loader-entry electrical/reset boundary, Flash programming, or recovery on
sacrificial hardware.

The corrected `E3` frame has never been transmitted physically. Later runs
missed loader entry, and corpus-wide analysis found a 255 ms gap between saved
host probe timestamps plus a nondeterministic bare-FTDI power boundary. The gap
is not wire-time or causal proof because AC-on was not timestamped. **Do not use the manual-AC/
BREAK workflow for another write.** First qualify a target-power-safe UART and
deterministic hardware-reset fixture on the spare target. See the
[physical-session forensic report](../reverse-engineering/physical-flash-session-forensics.md)
and [fixture requirements](../hardware/j3-loader-entry-fixture.md).

This is the offline design and evidence base for a future dedicated BixCheck
Downloader replacement. Loader traffic is not exposed through generic raw
mode. The manual stove-AC/BREAK implementation is retained in source only as
historical research code and is not reachable for physical traffic. The CLI
permits only `--plan-only`; every rehearsal, programming, or recovery run is
rejected before image/bundle access, session creation, serial open, or an
operator power-cycle prompt. The rehearsal and complete write executors accept
only the package's exact in-process simulator types and reject physical
transports and simulator subclasses before the first loader byte.

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
conditions require the conservative external-programmer procedure, which is
not yet a qualified repeatable process.

The vendor interruption warning and retry statement are on page 24 of the
[preserved BixCheck service manual](../../preservation/original/manuals/1394047.pdf).

## What the reachable tool proves

The offline plan authenticates an exact preserved J3 image by SHA-256,
filename, delivery variant, program-word count, configuration word, block
count, and the SHA-256 of the complete on-wire frame sequence. It constructs
and validates a strict-simulator-executable frame plan; `--plan-only` does not
execute that simulator or claim a memory result.

The exact-type simulation-only rehearsal tests `EA/EB`, then `ED/E4`, with zero
`E3` frames. The simulation-only write executor tests fixed 9,600-baud loader
transport, per-block `E7`/`E4` handling, bounded retries, application identity,
and unchanged EEPROM verification. Those software checks are not evidence that
the present physical reset/power boundary is safe or deterministic.
After `ED/E4`, the retained handoff gate waits transmit-silent for unsolicited
`T` or periodic `DW` application telemetry before the first `CR00`; timeout
cannot be treated as permission to transmit.

`E4` is the resident loader's local readback result; J3 has no independent
whole-program-memory read command. A PICkit readback on expendable hardware is
the independent whole-chip verification method.

The physical failure also proves that `E7` alone authenticates only the sum of
payload bytes, not their order. BixCheck sends each PIC word high byte first;
Intel HEX stores it low byte first. OpenMaxFire now performs that conversion
explicitly, and the strict simulator independently decodes the wire order.

## Firmware and MCU evidence

The byte-identical 2.02/2.06 resident loader sets `SPBRG=0x40` with the board's
10.000 MHz oscillator. That is the 9,600-baud setting. Firmware 2.70 and 2.71
use 19,200 only after application handoff.

At reset, the loader initializes a three-count timeout loop, but a pre-set
Timer1 flag consumes its first decrement immediately. The two remaining real
overflows and the 10 MHz oscillator put the first-byte window near 200 ms.
OpenMaxFire defaults to a 20 ms read timeout and no extra delay between missed
`EA` probes; `--loader-identify-retry-delay` can add a bounded 0-50 ms pacing
delay independently of program-block retries. After loader identification,
the tool changes to a 500 ms block-response timeout.

The recovered PIC machine code has also been emulated with `EA ED` queued at
reset. It consumes both bytes, returns exactly `EB E4`, and enters the original
application path without an `E3` transfer.

Ten physical rehearsals on the original firmware-2.02 controller confirmed
`EA/EB` and `ED/E4` with zero `E3` frames. Other otherwise equivalent entries
failed. With the direct `TTL-232R-5V-WE`, UART BREAK holding orange/TX low during
power removal improved entry but did not make it deterministic. Application J3
traffic also sometimes required a cold boot with both stove AC and FTDI USB
power removed. All 24 saved EEPROM images are byte-identical. These results
prove functional loader-protocol and UART logic-level behavior when entry
occurs; they do not establish a safe electrical reference, partial-power
compatibility, firmware programming, or the power-transition method.

The sessions also exposed an application-handoff defect in host version 0.9:
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

## Physical loader boundary

There is no current physical rehearsal path. Zero-write does not resolve the
unclassified shared electrical reference, cross-power possibility, or reset-
time nondeterminism, so the manual AC/BREAK workflow and its operator prompts
are retired. Do not copy a historical command from a saved session. Future
zero-write work starts only with the reviewed fixture on a safely powered spare
described in the qualification plan.

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
authenticated blocks, a data-format migration, and
`physical_e3_enabled: false`.

Unknown, modified, renamed, PICkit, and firmware 2.73 images are blocked.
For 2.73, contact [contact@openmaxfire.com](mailto:contact@openmaxfire.com) and
provide the original image to the
[OpenMaxFire project](https://github.com/OpenMaxFire/OpenMaxFire) for
preservation and analysis.

Same-version rewrites and J3 downgrades are also rejected by the offline plan.
Sparse downgrades can leave stale newer program words. The dormant
session-bound replay design is retained for simulation, but physical recovery
currently requires the conservative, not-yet-qualified PICkit procedure.

## All physical loader traffic is locked

There is currently no supported physical rehearsal, live-update, or J3 recovery
command. A `flash` invocation without `--plan-only` exits before loading the
image or recovery bundle, creating a session, opening the serial port, or
showing any power-cycle prompt. Adding `--rehearsal-only`,
`--hold-tx-break-during-power-off`, confirmation flags, or
`--recover-from-session` does not bypass this lock.

The implementation below that lock is retained so the complete plan, retry,
recovery, and post-write verification behavior can be called directly by the
simulation/qualification tests. There is no command-line override, including
for a simulated transport. Adding a fixture-specific physical executor for
qualification requires all of the following in a separate reviewed change:

1. A target-power-safe UART interface and deterministic hardware-reset entry.
2. The spare-target electrical and 100/100 zero-write qualification gates in
   the [fixture requirements](../hardware/j3-loader-entry-fixture.md).
3. One complete spare-target flash with independent PICkit whole-chip
   readback.
4. A new CLI path tied specifically to that qualified fixture, with tests that
   prove the retired AC/BREAK entry still cannot reach `E3`.

The historical tool required an exact power-off phrase and, after `ED/E4`,
waited up to 30 seconds for unsolicited `T` or `DW` telemetry while
transmitting nothing. If telemetry never arrived, it failed without sending
`CR00`. Increasing that timeout does not repair an electrical reset or
backfeed problem.

That development path must remain unavailable for a production controller
until the complete multi-specimen, forced-interruption, and cross-platform
[release qualification plan](j3-flasher-qualification.md) passes and produces
a signed release record.

If an older session contains `RECOVERY_REQUIRED.txt`, preserve the directory,
keep the stove out of operation, and follow the
[external-programmer recovery procedure](pickit3-emergency-recovery.md). The
2026-08-30 original-controller restore booted normally and retained the
expected J3 EEPROM, but no saved post-program whole-chip readback or spare-
controller proof exists; do not call that process fully qualified. The dormant
`--recover-from-session` J3 replay path is also blocked by both public physical
gates; do not treat it as an available recovery command.
Any preserved 2026-08-29/30 marker text that instructs
`--recover-from-session` is historical evidence and is superseded by this
boundary; do not edit the saved marker.

## Historical session artifacts and current exit behavior

`--plan-only` writes no session and opens no serial port. Historical physical
`--rehearsal-only` sessions attempted to preserve:

- `state.json`, atomically replaced for each major state;
- `preflight-traffic.jsonl`;
- `eeprom-before.json` and `preparation.json`;
- `offline-qualification.json`;
- `rescue/<exact-vendor-filename>.hex` and
  `rescue/recovery-manifest.json`;
- `rehearsal-traffic.jsonl`, `rehearsal-loader-result.json`,
  `rehearsal-app-traffic.jsonl`, `rehearsal-application-readiness.json`,
  `rehearsal-verification.json`, and `rehearsal-eeprom.json` for a normal
  session;
- `journal.jsonl`, normally flushed and `fsync`'d after each state event;
  identify probe misses are bounded and aggregated until the timing window
  ends;
- `loader-traffic.jsonl`, flushed and `fsync`'d for every non-empty TX/RX
  event while the diagnostic sink remains healthy;
- `loader-result.json`;
- `postflash-readiness-<attempt>.json`, post-flash traffic,
  `eeprom-after.json`, and `result.json`.

Older programming-session directories remain evidence. Do not edit or delete
them even though their physical J3 recovery command is now locked.

CLI exit codes relevant to flashing are:

| Code | Meaning |
| --- | --- |
| `0` | Offline plan completed. |
| `2` | Invalid command arguments. |
| `3` | Historical/dead-code operator abort state; not reachable from the current physical CLI. |
| `4` | Validation failure or any physical loader workflow blocked by the early CLI safety lock. |
| `5` | Historical/dead-code loader failure state; not reachable from the current physical CLI. |
| `6` | Historical unresolved recovery state; current physical J3 replay is locked. |
| `130` | The process was interrupted. |

## Calibration after an update

The factory Downloader images contain no EEPROM records, so J3 leaves the old
calibration bytes in place. The 2.06 release notes require Monitor model
selection, **Individualize**, **Calculate Fuel A/B**, and **Format** after the
firmware/data-format update. BixCheck 5.5.01 also emphasizes calibration.

This procedure remains a requirement for any future physical updater. The
current CLI cannot perform that update.

## Release qualification

Passing software tests does not convert emulator evidence into physical
evidence. The stable-release gate and forced-interruption matrix are in the
[J3 flasher qualification plan](j3-flasher-qualification.md). Until that matrix
and the replacement fixture gates pass, every physical loader byte remains
unreachable from both the CLI and the public executors.
