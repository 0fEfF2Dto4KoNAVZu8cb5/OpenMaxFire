# J3 flasher qualification plan

Status: required physical release gate; **not yet executed**.

The guarded host is not a consumer updater until every mandatory item in this
plan passes on expendable, externally recoverable hardware. Unit tests,
firmware emulation, and a successful non-writing rehearsal are necessary but
do not prove the PIC's electrical erase/write behavior, the stove power rail,
the adapter, or recovery after interruption.

Never run destructive qualification on a stove responsible for heating. Use a
cold bench controller with both igniters and all other hazardous loads
physically disconnected. Mains wiring and controller repair must be performed
only by a person qualified for that work.

## Release decision

The release gate stays closed until one signed qualification record shows:

- complete original and recovery images authenticated before testing;
- at least one spare PIC programmed, read back, authenticated, and booted in a
  representative expendable controller before any J3 interruption test;
- the complete supported upgrade sequence and every forced-interruption case
  below passing;
- no program-memory change outside the planned application words, including
  no change to `0x1E80`-`0x1FFF`, configuration, User IDs, or EEPROM;
- every interrupted session leaving an accurate recovery marker and every
  exact-image replay recovering from block zero;
- every successful run producing the expected identity, unchanged EEPROM, and
  complete evidence artifacts;
- the matrix repeated on all supported host operating systems and representative
  USB-TTL adapter chipsets; and
- zero unexplained `E5`, unexpected-byte, serial, state, manifest, or readback
  anomalies.

Any failure closes the gate. Preserve the failed session and programmer reads,
identify the cause, add a regression test, correct the host or procedure, and
restart the affected matrix rather than waiving it.

## Required equipment and specimens

Use five or more independently labeled spare PIC16F877A/controller specimens
where practical. Do not treat repeated tests on one known-good PIC as evidence
of unit-to-unit tolerance.

Required equipment:

- a PICkit 3 or equivalent programmer with verified device support;
- immutable, hash-checked original and recovery images;
- a representative expendable 9067-0604 controller or electrically faithful
  fixture with a 10.000 MHz clock;
- current-limited, instrumented controller power under a qualified operator's
  control;
- a logic analyzer or oscilloscope on controller VDD and J3 TX/RX;
- at least two reputable 5 V TTL USB adapters using different bridge chipsets;
- Windows, Linux, and macOS hosts on stable power;
- a controlled USB-disconnect method and a controlled controller-power cut;
- a dedicated evidence directory with synchronized UTC time; and
- both igniters and every hazardous or heating load physically disconnected.

J3 wiring for every test is adapter TX to J3-1, adapter RX to J3-2, and ground
to J3-4. J3-3 and adapter VCC remain disconnected. Do not power the controller
from USB.

## Stage 1: external recovery proof

For each specimen:

1. Label and photograph the PIC, controller, adapter, wiring, and programmer.
2. Read program memory, EEPROM, User IDs, configuration, and Device ID three
   times without changing programmer settings.
3. Authenticate the repeated reads with the OpenMaxFire preservation tools.
4. Program only a spare PIC with the intended complete recovery image.
5. Read the programmed spare three times and authenticate every normalized
   section against the source.
6. Boot it in the expendable controller and confirm application identity and
   complete EEPROM access.
7. Deliberately replace the application on that spare with a known recoverable
   test state, restore it with the programmer, read it back again, and repeat
   the boot/identity check.

Owning a programmer or obtaining one successful write is not enough. The
restore must work on the actual spare PIC/controller combination used for the
J3 tests.

## Stage 2: non-writing path

Run `--rehearsal-only` at least ten times for each host/adapter/controller
combination selected for the matrix. Capture J3 and VDD on the analyzer.

Each run must prove:

- exactly one retained serial handle from preflight through final verification;
- application identity read three times and EEPROM read twice before loader
  entry;
- `EA/EB`, then `ED/E4`, with no `E3` byte at any point;
- unchanged application identity read three times after handoff;
- two identical post-rehearsal EEPROM reads equal to the preflight bytes;
- no unexpected reset, DTR/RTS-induced entry, or host sleep; and
- complete, parseable rehearsal artifacts and a correct terminal state.

Also prove that every missing safety confirmation, wrong operator phrase,
unknown image, renamed image, modified image, PICkit image, same-version image,
downgrade, incompatible current profile, invalid EEPROM checksum, mismatched
data format, corrupt rescue manifest, pre-existing session directory, and
unavailable sleep inhibitor fails before the first `E3` frame.

Prove that recovery refuses a completed session and any source already carrying
`RECOVERY_DELEGATED_TO.json`. Abort one recovery before `E3`, confirm the old
source points to the new self-contained session, and successfully continue only
from that new session.

## Stage 3: successful programming sequence

On each representative specimen, use only exact preserved Downloader images
and execute the supported sequence:

| Current profile | Target image | Expected target | Blocks | Loader baud |
| --- | --- | --- | ---: | ---: |
| `fw202-format04` | `Bixby_02060021_Downloader.hex` | `fw206-format05` | 476 | 9,600 |
| `fw206-format05` | `Bixby_0270_070206.hex` | `fw270-format07` | 481 | 9,600 |
| `fw270-format07` | `Bixby_0271_080315.hex` | `fw271-format07` | 486 | 9,600 |

For every transition:

1. Save the PICkit before-state and complete J3 EEPROM backup.
2. Run the mandatory non-writing rehearsal.
3. Run the live transfer and retain all session artifacts.
4. Confirm three target identities and two identical EEPROM reads through J3.
5. Read the entire PIC with the PICkit before any calibration change.
6. Compare program memory against the exact expected result, including sparse
   untouched words and reset-vector relocation.
7. Prove the loader range, EEPROM, User IDs, and configuration are unchanged.
8. Complete the target-version calibration/Format procedure, then save a new
   independent EEPROM backup.

No “it boots” shortcut is acceptable; booting does not independently verify
the whole program image or protected loader.

## Stage 4: forced-interruption and fault matrix

Begin each case from a PICkit-authenticated baseline. Use a distinct new
session directory for the attempt and another for recovery. Never reuse or edit
the failed session.

| Injection point or fault | Required host result | Required recovery proof |
| --- | --- | --- |
| Before loader `EB` | No program traffic; `failed_before_programming` | Normal rerun succeeds; no recovery marker remains |
| Before first `E3` | No application write | Normal rerun succeeds |
| During first block header | `recovery_required` if any `E3` may have left the host | Exact saved image replayed from block zero |
| During first block payload | `recovery_required` | Exact saved image replayed from block zero |
| At 25%, 50%, and 75% of blocks | `recovery_required` | Exact saved image replayed from block zero |
| During final block | `recovery_required` | Exact saved image replayed from block zero |
| After block `E7`, before `E4` reaches host | At most one identical ambiguous-write retry | Successful verification or exact replay |
| After final block `E4`, before `ED` | Conservative completion recovery | Target app first; otherwise `EA/EB` then one `ED` |
| After `ED`, before its `E4` reaches host | No block retransmission | Target app or one identified-loader completion retry |
| Controller AC loss | No blind reconnect/resume | Restore stable AC; exact replay from block zero |
| USB disconnect or adapter reset | Immediate transport abort | Reopen only through explicit recovery command |
| Host process termination request | SIGINT/SIGTERM/SIGBREAK deferred in critical section | Result records request; complete or explicit recovery |
| Forced process kill | Marker survives process loss | New-process exact replay succeeds |
| Host suspend request | Sleep inhibitor prevents suspend or tool fails before `E3` | No unexplained partial session |
| Traffic/journal disk-write failure | Program loop continues once partial write is possible | Diagnostic failure recorded; final state conservative |
| First loader `E5` | One identical retry only | Finish with inspection gate, or exact replay on failure |
| Second `E5` anywhere | Immediate abort | Inspect VDD/socket/PIC, then exact replay |
| `E8` checksum reject | At most two identical retries | No PIC write before accepted payload |
| Timeout before `E7` | At most two identical retries; treat the lost reply as ambiguous | Exact row replay is idempotent; verify/recover without assuming no write occurred |
| Unexpected response byte | Immediate abort, no retry | Inspect framing, then exact replay |

Power cuts and serial faults must be injected at repeatable measured points,
not by guessing from the progress display. Repeat each boundary case at least
three times and rotate specimens. Repeat the ambiguous post-`E7` and final-`ED`
cases at least ten times because those paths decide whether to resend a row or
handoff command.

If safe instrumentation cannot provoke a real `E5`, do not damage a production
controller to obtain one. Retain the exhaustive simulated `E5` coverage and
mark the physical case unresolved; the consumer release gate remains closed
until the risk is otherwise bounded with credible hardware evidence.

## Stage 5: platform and adapter matrix

At minimum, qualify the current supported Python build on:

| Host | Power/sleep check | Serial check |
| --- | --- | --- |
| Windows | `SetThreadExecutionState` active; lid/open-power policy verified | Native exclusive handle, no reopen between phases |
| macOS | `caffeinate` assertion active | One retained device handle and target-baud handoff |
| Linux | `systemd-inhibit` lock active | pySerial exclusive lock and one retained handle |

For every host, exercise two adapter chipsets, USB reconnect behavior, port-name
changes, permission denial, another process holding the port, and diagnostic
filesystem exhaustion. Record OS, kernel/build, Python, pySerial, adapter VID,
PID, serial number, driver, cable length, and measured controller VDD.

## Evidence package

The qualification record must include:

- hardware inventory, photographs, wiring, and instrument setup;
- command line and OpenMaxFire commit hash for every run;
- SHA-256 of every firmware image, PICkit export, EEPROM backup, and session
  artifact tree;
- raw logic-analyzer traces for reset entry and each injected boundary;
- `state.json`, recovery marker disposition, journal, traffic logs, loader
  result, and final result from every attempt;
- full before/after/recovered PICkit comparisons;
- calibration records; and
- a pass/fail table signed and dated by the operators who performed and
  independently reviewed the tests.

Publish failures with the successes. A missing artifact is a failed case, not
an assumed pass.

## Consumer-release requirements

Even after this matrix passes, a consumer build should keep the same fixed
allowlist, no-downgrade rule, rehearsal, power/sleep checks, exact rescue
bundle, attempt logging, recovery marker, and post-verification. It should also
ship with a clear unsupported-controller message, a tested installer/driver
path, a digitally signed release, and an operator-facing recovery document
available offline.

The underlying single-bank limitation remains: an unexpected power loss can
make the application temporarily nonfunctional. The safety claim is therefore
“detect partial/uncertain programming and recover using the protected loader or
proven external programmer,” never “a J3 update cannot be interrupted.”
