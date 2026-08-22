# Cross-platform service tool

Status: the portable read-only foundation is implemented, tested offline, and
live-validated for read-only use on serial 5215's firmware 2.02/data-format 04
controller at 9,600 baud. Writes remain unvalidated and excluded from the
documented workflow.

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

Host-originated D requests are excluded from the live read command because
their semantics remain unresolved.

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

## Writes remain isolated

The existing `button` command remains gated and unvalidated. Configuration
writes, Checkout actuator commands, raw A-space writes, `CW0FC4`, and the binary
loader are not added to these read-only workflows. The first physical session
must contain no `CW`, `AW`, or loader bytes.

## Cross-platform verification

GitHub Actions runs the offline suite on Windows, Ubuntu, and macOS with Python
3.11 and 3.13. The suite covers request/response parsing, interleaved telemetry,
identity ordering, A-space reads, backup integrity, port normalization, traffic
recording, real-firmware emulation, and loader separation. Live-derived
regressions cover a partial first line and 32 interleaved telemetry frames.
Archive integrity is verified separately on Linux.
