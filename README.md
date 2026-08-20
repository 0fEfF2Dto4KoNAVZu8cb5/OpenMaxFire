# OpenMaxFire

OpenMaxFire is a preservation and reverse-engineering project for the discontinued Bixby MaxFire 110/115 biomass stove ecosystem. It archives the factory BixCheck service software and firmware, documents the J3 computer interface, and is building a modern Linux service tool plus a deliberately limited ESP32/Home Assistant controller.

## Current status

The repository contains the recovered vendor packages, BixCheck 5.x manual, BixCheck 5.5.00/5.5.01 binaries, 2.06 and 2.71 firmware, the complete 2.71 disassembly, photographs, provenance records, and the first protocol library.

Confirmed by static evidence:

- Stove firmware 2.71 targets a PIC16F877A.
- The controller recognizes ASCII register commands `CRXX` and `CWXXYY`.
- Responses use ASCII hexadecimal and end with LF (`0x0A`).
- BixCheck maps remote OFF/ON/UP/DOWN to `CW0E11`, `CW0E12`, `CW0E14`, and `CW0E18`.
- The recovered stove is serial 5215; its owner identifies it as a MaxFire 115.

Not yet confirmed on physical hardware:

- J3 pinout and electrical levels.
- Baud rate. Firmware register values imply about 38.4 kbaud at a 20 MHz oscillator; an earlier prototype assumed 19.2 kbaud.
- Response framing beyond the LF terminator and acknowledgement semantics.
- Which exposed input bit is the firebox door switch.
- Any remote command on the actual stove.

No live connection should be attempted until [SAFETY.md](SAFETY.md) and the [J3 working specification](docs/protocol/j3-protocol.md) have been reviewed.

## Project goals

1. Preserve original Bixby software, firmware, manuals, release notes, photographs, and hardware documentation without modifying the originals.
2. Fully document the MaxFire 110/115 J3 protocol and controller register space.
3. Replace essentially all BixCheck functions with a cross-platform Linux CLI/application.
4. Build a fail-out-of-the-way ESP32/ESPHome interface for normal telemetry, faults, start/stop, heat level, command verification, and Home Assistant exposure.
5. Keep the factory controller, front panel, thermostat inputs, combustion logic, and safety behavior authoritative.

## Quick offline use

The encoder can be used without hardware:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -e .

maxfirectl encode read 0x0e
# CR0E

maxfirectl encode button up
# CW0E14
```

Live I/O is intentionally gated and requires an explicit port, baud rate, and acknowledgement flag.

## Repository map

- `preservation/original/` - recovered files as received, plus provenance and hashes
- `reverse-engineering/` - extracted firmware, disassembly, strings, and analysis outputs
- `docs/` - hardware, protocol, BixCheck, automation, status, history, and roadmap
- `src/openmaxfire/` - modern Python protocol/transport foundation
- `tools/` - reproducible Debian analysis helpers
- `tests/` - offline protocol tests

Start with [the research status](docs/STATUS.md), [the project roadmap](docs/ROADMAP.md), and [the preservation manifest](preservation/MANIFEST.md).

## Files pending direct upload

Five original artifacts are intentionally omitted from the automated import and will be uploaded directly to GitHub without any transformation. Their exact destination paths, sizes, and expected SHA-256 values are recorded in [preservation/PENDING_UPLOADS.md](preservation/PENDING_UPLOADS.md).

## Licensing

OpenMaxFire-authored code and documentation are released under the MIT License. Recovered Bixby vendor artifacts and user photographs retain their respective original rights and are not relicensed by this project. See [preservation/README.md](preservation/README.md).
