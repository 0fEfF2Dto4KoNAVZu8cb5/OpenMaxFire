# Experimental J3 flasher

Status: **experimental, destructive, bench-only**.

This tool exists separately from `maxfirectl` so physical firmware loading is
not accidentally exposed through the normal OpenMaxFire API/CLI. Use only on a
controller/PIC that is externally recoverable with a PICkit and a verified full
image.

## What it implements

- Fast `EA` -> `EB` reset-window loader identification.
- Exact `E3` frames: word address, byte count, additive payload checksum, data.
- `E7` checksum-accepted handling.
- `E8` checksum-rejected handling with a small explicit retry limit.
- **Immediate abort on `E5`** write/readback verification failure.
- `E4` block success handling.
- `ED` -> `E4` completion.
- Required structured JSONL event logging with monotonic timestamps and exact TX/RX bytes.
- Strict rejection of full PICkit images on the J3 path.
- Acceptance only of the preserved 2.06, 2.70, and 2.71 J3 image families.
- Optional post-flash read-only controller identity verification at an explicitly
  selected baud.
- Required `--i-understand-this-can-brick` acknowledgement for every physical
  loader operation.

Unlike BixCheck, this tool does not broadly retry an `E5` failure. A PIC-side
write/readback verification failure stops the transfer immediately so the
failed row and exact wire exchange can be preserved for diagnosis.

## Loader-window timing

A first physical capture showed that using the normal 250 ms serial timeout for
loader identification produced `EA` probes roughly every 271 ms, which is too
slow for a short reset-time bootloader window.

The flasher now temporarily changes the serial timeout to **10 ms** during
loader identification and targets an `EA` transmission every **15 ms**. As soon
as `EB` is received, or if identification fails, the original normal serial
timeout is restored before any `E3` programming transaction can occur.

Defaults:

- `--identify-read-timeout 0.010`
- `--identify-interval 0.015`
- `--identify-attempts 1500`

`--identify-delay` remains accepted as an alias for `--identify-interval`.

## Commands

Run from an editable/installable checkout so `openmaxfire` is importable.

### Offline image plan

```bash
python tools/experimental_j3_flasher.py dry-run \
  reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex
```

No serial port is opened.

### Loader probe only

This sends only repeated `EA` bytes while the loader window is available and
requires `EB`. It does not send an `E3` frame.

```bash
python tools/experimental_j3_flasher.py probe \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --event-log captures/loader-probe.jsonl \
  --i-understand-this-can-brick
```

The normal vendor workflow power-cycles the stove/controller while the host is
probing for the reset-time loader window.

### Protected-range framing test

This is the first physical test to perform. It identifies the loader, sends one
normal `E3` block beginning at `0x1E80`, requires `E7` then `E4`, and sends
`ED`/requires final `E4`.

The reconstructed 2.06 resident loader treats direct targets at and above
`0x1E80` as protected and skips the Flash write. The test therefore exercises
physical framing/checksum/acknowledgement timing without intentionally changing
an application Flash word.

```bash
python tools/experimental_j3_flasher.py protected-test \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --event-log captures/protected-test-002.jsonl \
  --i-understand-this-can-brick
```

A successful result must show loader identification, `E7`, `E4`, and final
`ED`/`E4`. Preserve the JSONL file.

### Full J3 image transfer

Do not run this until the probe and protected test are repeatedly successful on
externally recoverable hardware.

Example 2.70 transfer from a 2.06 resident loader:

```bash
python tools/experimental_j3_flasher.py flash \
  reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex \
  --port /dev/ttyUSB0 \
  --baud 9600 \
  --post-baud 19200 \
  --event-log captures/fw206-to-fw270-001.jsonl \
  --i-understand-this-can-brick
```

`--post-baud` is optional because the correct application baud must be selected
from the actual controller/firmware behavior being tested. If supplied, the
loader transport is closed after `ED/E4`, the tool waits, reopens the port, and
runs the existing read-only `CR00`, `CR08`, `CR0B`-`CR0E` identity sequence.

## Required recovery preparation

Before any full physical transfer:

1. Preserve a verified full PICkit image of the exact starting chip.
2. Verify that the spare PIC can be restored externally.
3. Preserve current EEPROM/calibration separately.
4. Disconnect heating loads/igniters as required by the vendor servicing
   procedure.
5. Record the complete serial event log for every experiment.
6. If a transfer fails, stop and PICkit-read the chip before attempting another
   J3 transfer so the exact failed state is preserved.

## Failure behavior

- No `EB`: stop; no programming block is sent.
- `E8`: retry only up to the explicit small checksum retry limit.
- Timeout: retry only up to the explicit small timeout retry limit.
- Unexpected response: default is **zero retries**.
- `E5`: **always abort immediately**.
- Missing final `E4` after `ED`: report failure; do not send another programming
  block.

The event log is intended to make each failure attributable to an exact frame,
word address, checksum, response byte, and time.
