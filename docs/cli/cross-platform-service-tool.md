# Cross-platform service tool

Status: the portable foundation is implemented, tested offline, and
live-validated on serial 5215's firmware 2.02/data-format 04 controller at
9,600 baud. Remote OFF/ON/UP/DOWN bytes are live-validated; unrelated writes
remain unvalidated and excluded from the documented workflow. Version 0.9.1
also contains a separate authenticated J3 flasher. Its physical zero-write
identify/completion handshake has been observed, but electrical reset behavior,
Flash programming, and recovery remain gated on proven PICkit recovery and the
sacrificial-hardware qualification matrix. After loader handoff, it passively
waits for unsolicited application telemetry before transmitting `CR00`.

Firmware work is not part of the generic live-I/O gate below. Read the
[guarded J3 firmware-flashing guide](../guides/safe-j3-firmware-flashing.md);
the dedicated `flash` command has stricter image, wiring, igniter, recovery,
manual-power-cycle, backup, and post-flash verification requirements.

`maxfirectl` uses one Python codebase on Windows, Linux, and macOS. The protocol,
identity, backup, and safety logic does not contain OS-specific port assumptions.
Only the serial-device name changes:

| Platform | Typical port | Intended support |
| --- | --- | --- |
| Windows | `COM3` | First-class |
| Linux | `/dev/ttyUSB0` or `/dev/ttyACM0` | First-class |
| macOS | `/dev/cu.usbserial-*` or `/dev/cu.usbmodem-*` | First-class after hardware validation |

The Unix pseudo-terminal virtual lab remains a Linux/macOS development aid. Its
protocol model and tests are importable on Windows, but Windows does not provide
the PTY endpoint used by that optional tool.

## Install from source

Python 3.11 or newer is required.

Linux/macOS:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
```

Future releases should add signed or checksummed standalone Windows, Linux, and
macOS packages so stove owners do not need Python or Git.

## Cable-only discovery

`ports` enumerates serial devices without opening them and does not require the
live-I/O acknowledgement:

```bash
maxfirectl ports
maxfirectl ports --json
```

Run it before and after attaching only the computer end of the received cable.
The output retains available USB VID/PID, serial number, manufacturer, product,
hardware ID, and physical location. Save both results with photographs of every
cable marking.

## Safety gate

Every command that opens a serial port requires all three of:

- an explicit port;
- an explicit baud rate;
- `--i-understand-unverified-io` after the subcommand.

This is deliberate. Opening a serial device can transition DTR/RTS even when
the program never transmits a payload. The `capture` command is receive-only,
but it is **not** an electrically passive substitute for a protected meter or
logic analyzer.

Do not use the commands below until the received cable and J3 electrical
interface have been inspected and proven suitable.

## Timestamped traffic capture

This opens the selected serial device, transmits nothing, reads for ten seconds,
and records exact received chunks with UTC and monotonic timestamps:

Windows:

```powershell
maxfirectl --port COM3 --baud 19200 capture `
  --duration 10 --output cable-idle.jsonl `
  --i-understand-unverified-io
```

Linux/macOS:

```bash
maxfirectl --port /dev/ttyUSB0 --baud 19200 capture \
  --duration 10 --output cable-idle.jsonl \
  --i-understand-unverified-io
```

Capture files use schema `openmaxfire.serial-capture.v1`. The first JSON Lines
record contains the OS, Python version, port, baud, timeout, and serial format.
Each following record contains direction, exact hex, printable representation,
byte count, UTC time, and monotonic nanoseconds. Existing files are not replaced
unless `--overwrite` is supplied.

## Read-only identification

`identify` sends only `CR00`, `CR08`, and `CR0B` through `CR0E`, in that order.
It waits 100 ms between requests by default and ignores interleaved telemetry
while waiting for the matching addressed reply. Matching continues until the
transport timeout by default and resynchronizes after a partial opening line;
the live format-04 controller can emit more than 16 frames before a valid reply.

```bash
maxfirectl --port COM3 --baud 19200 \
  --traffic-log identify-traffic.jsonl \
  identify --json --i-understand-unverified-io
```

The known static pairings are:

| Firmware | CR08 | CR0B | CR0C | CR0D | CR0E | Intended baud |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 2.02 (live-observed) | `04` | `02` | `02` | `00` | `00` | 9,600 |
| 2.06 | `05` | `02` | `06` | `00` | `21` | 9,600 |
| 2.70 | `07` | `02` | `70` | `00` | `02` | 19,200 |
| 2.71 | `07` | `02` | `71` | `00` | `00` | 19,200 |

An unrecognized combination is reported as unrecognized rather than forced
into one of these versions.

## One-byte reads

Controller byte:

```bash
maxfirectl --port COM3 --baud 19200 read 0x02 \
  --unit C --i-understand-unverified-io
```

EEPROM byte:

```bash
maxfirectl --port COM3 --baud 19200 read 0x03 \
  --unit A --i-understand-unverified-io
```

Version 0.4 permits `--unit D` for low-level research while retaining an
explicit warning that host-originated D-space semantics remain unresolved.

## Complete EEPROM backup

The backup workflow first runs the read-only identity sequence, then reads every
byte from `AR00` through `ARFF` with the configured inter-request delay:

```bash
maxfirectl --port COM3 --baud 19200 \
  --traffic-log backup-traffic.jsonl \
  backup --output serial-5215-eeprom.json \
  --i-understand-unverified-io
```

The backup uses schema `openmaxfire.eeprom-backup.v1` and contains:

- all 256 bytes individually and as one lossless hex string;
- controller identity and data format;
- decoded serial-number, production-date, and model fields;
- stored and independently calculated BixCheck checksums;
- an explicit controller/EEPROM format comparison;
- connection metadata and the static/live evidence boundary.

Existing backup and traffic files are never silently replaced. `--overwrite`
and `--overwrite-traffic-log` must be supplied separately when replacement is
intentional.

## Continuous read-only monitor

Version 0.3 adds a first-class monitor that cycles through CR00-CR0E and retains
every valid interleaved telemetry/status frame observed while it waits for each
matching reply. It never sends `CW`, `AW`, `DW`, or loader bytes. The software
path is covered by unit tests and preserved firmware-2.02 captures; the
continuous polling loop still needs one cold/off live validation.

For serial 5215, a bounded first run is:

```bash
maxfirectl \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --timeout 1.0 \
  --request-delay 0.50 \
  --traffic-log fw202-monitor-raw.jsonl \
  monitor \
  --cycles 1 \
  --output fw202-monitor-snapshots.jsonl \
  --i-understand-unverified-io
```

After that bounded cycle is reviewed, replace `--cycles 1` with `--duration 60`
for a one-minute run. Omitting both limits runs until Ctrl-C. `--json` emits the
same machine-readable snapshot objects to standard output; otherwise the CLI
prints compact human-readable status lines.

Snapshots preserve all latest CR and T bytes, adjacent telemetry words,
per-frame counts, last-observed time, age, and a configurable stale threshold.
Format-04 names are limited to the correlations established on serial 5215.
In particular, format-04 `T09=07` is retained as unresolved raw data rather than
being passed through the later BixCheck 5.5 state decoder.

Format-04 fault indicators are temporal. The monitor accumulates nonzero T08
bits across an eight-second observed-stream window so a snapshot taken while a
physical fault lamp is dark still reports the active light and recognized
factory pattern. Later formats retain BixCheck's T13 Alarm status as raw data;
they do not use the format-04 T08 decoder.

## Offline capture replay

`replay` never opens a serial port and does not require the live-I/O acknowledgement:

```bash
maxfirectl replay \
  research/live/2026-08-22-fw202-format04/captures/\
fw202-identify-ash-drawer-open-long.jsonl \
  --json
```

The replay engine reconstructs frames across arbitrary RX chunk boundaries,
ignores TX events, resynchronizes after malformed/partial opening lines, and
reports parsed-frame, malformed-line, received-byte, and trailing-byte counts.
Use `--output final-snapshot.json` to save the final decoded state without
altering the original capture.

## Most low-level writes remain unvalidated

Version 0.4 adds generic A/C/D writes, optional fresh readback, exact-byte raw
exchange, and validated register transaction plans. They require a second
state-change acknowledgement. Remote front-panel writes are now live-validated
on firmware 2.02; other write addresses remain offline-tested only. The read-only
monitor, backup, identify, capture, and replay workflows still never emit a
write. Known `CW0FC4`, `EA`, `E3`, and `ED` loader traffic is blocked from raw
and transaction mode. See [Low-level service layer](low-level-service-layer.md).

## Cross-platform verification

GitHub Actions runs the offline suite on Windows, Ubuntu, and macOS with Python
3.11 and 3.13. The suite covers request/response parsing, interleaved telemetry,
identity ordering, A-space reads, backup integrity, port normalization, traffic
recording, real-firmware emulation, and loader separation. Live-derived
regressions cover a partial first line, 32 interleaved telemetry frames, and
four preserved format-04 door/drawer/thermostat replay cases. A preserved
flashing-light-8 capture additionally verifies temporal fault retention when
the final instantaneous `T08` sample is zero. Archive integrity is verified
separately on Linux.
