# Virtual serial lab

`tools/virtual_serial_lab.py` creates a local POSIX pseudo-terminal implementing the
reconstructed BixCheck register grammar. It allows the modern client—or
BixCheck on a compatible host connected through a PTY bridge—to be exercised
without a stove.

The PTY endpoint requires Linux or macOS. `--demo`, the protocol model, and the
offline tests remain importable on Windows; normal Windows serial hardware is
handled by the portable `openmaxfire.transport` layer.

## Safe default

The lab is read-only by default. It accepts exact, unterminated requests:

- `<A|C|D>R<address:02X>`;
- `<A|C|D>W<address:02X><value:02X>`.

Reads return deterministic synthetic six-character responses ending in LF.
Writes return `IWRITE-BLOCKED` and do not alter the model. Any raw bootloader
byte, including `EA`, is rejected; the lab intentionally cannot emulate or
forward firmware servicing.

## Run it

```bash
python tools/virtual_serial_lab.py
```

The command prints a PTY such as `/dev/pts/7`. Point the client under test at
that path. A PTY accepts either nominal baud setting because it does not model
bit timing.

For a finite parser demonstration:

```bash
python tools/virtual_serial_lab.py --demo
```

For a JSON Lines transcript:

```bash
python tools/virtual_serial_lab.py --jsonl-log lab-events.jsonl
```

Synthetic register overrides use `UNIT:XX=YY`:

```bash
python tools/virtual_serial_lab.py --register C:08=05 --register C:0C=06
```

`--allow-writes` changes only the in-memory synthetic model. It never connects
to real serial hardware, but it should still be enabled only for a test that
specifically needs write/echo behavior.

## Default identity

The model advertises data format 07 and software bytes 02/71. Its A-unit serial,
date, and model strings are conspicuously synthetic, and A00/A01 contain the
matching synthetic configuration checksum. Unknown registers read as zero.
These values are test fixtures, not a dump of serial 5215.

## What this validates

- request stream splitting without terminators, including arbitrary chunking;
- strict uppercase host encoding and length checks;
- response parsing across CR, LF, and CRLF chunks;
- client timeout/logging behavior;
- enforcement of read-only and downloader-separation boundaries.

It does not validate J3 electrical characteristics, real timing, unsolicited
telemetry cadence, or state-dependent controller semantics.
