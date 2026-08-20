# OpenMaxFire

OpenMaxFire is a preservation and reverse-engineering project for the discontinued Bixby MaxFire 110/115 biomass stove ecosystem. It archives the factory BixCheck service software and firmware, documents the J3 computer interface, and is building a modern Linux service tool plus a deliberately limited ESP32/Home Assistant controller.

## Current status

The repository contains the recovered vendor packages, BixCheck 5.x manual, all
preserved 2.06/2.70/2.71 firmware images, portable and annotated disassemblies,
a deep three-EXE comparison, decoded application tables, an experimental PIC
emulator, a virtual serial lab, photographs, provenance records, and the first
protocol library.

Confirmed by static evidence:

- All four preserved firmware images target a PIC16F877A and pass Intel HEX checksum validation.
- The controller recognizes ASCII register commands `CRXX` and `CWXXYY`.
- Requests are fixed at four/six bytes and have no terminator.
- Addressed responses are six ASCII characters; telemetry frames carry one or
  two bytes; BixCheck accepts CR or LF termination.
- BixCheck maps remote OFF/ON/UP/DOWN to `CW0E11`, `CW0E12`, `CW0E14`, and `CW0E18`.
- CR0B/CR0C expose firmware `2.06`, `2.70`, or `2.71` as constant bytes.
- BixCheck 5.0.21 selects 9,600 baud; 5.5.x selects 9,600/19,200, all at 8N1.
- The configuration/telemetry/Checkout tables, lean-burn transforms, and
  configuration checksum are now machine-readable.
- The experimental emulator runs the actual firmware: all application images
  answer `CR00` with `CR0000`+LF, and the PICkit loader answers `EA` with `EB`.
- The recovered stove is serial 5215; its owner identifies it as a MaxFire 115.

Not yet confirmed on physical hardware:

- J3 pinout and electrical levels.
- Physical oscillator marking/frequency. The exact BixCheck rates and firmware
  divisors strongly imply 10 MHz, but the board has not been checked.
- Live electrical/timing validation of the reconstructed response grammar.
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

Run the read-only virtual endpoint without hardware:

```bash
python tools/virtual_serial_lab.py --demo
```

Regenerate the three-EXE analysis and offline firmware probes:

```bash
python tools/analyze_bixcheck.py --repo-root .
python tools/pic14_emulator.py project --repo-root .
```

## Repository map

- `preservation/original/` - recovered files as received, plus provenance and hashes
- `reverse-engineering/` - EXE tables/call graphs, firmware, disassembly,
  comparisons, and emulation traces
- `docs/` - hardware, protocol, BixCheck, automation, status, history, and roadmap
- `src/openmaxfire/` - modern Python protocol/transport foundation
- `tools/` - reproducible Debian analysis helpers
- `tests/` - offline protocol tests

Start with [the research status](docs/STATUS.md),
[the BixCheck comparison](docs/reverse-engineering/bixcheck-comparison.md),
[the J3 protocol](docs/protocol/j3-protocol.md),
[the firmware comparison](docs/reverse-engineering/firmware-comparison.md), and
[the preservation manifest](preservation/MANIFEST.md).

## Licensing

OpenMaxFire-authored code and documentation are released under the MIT License. Recovered Bixby vendor artifacts and user photographs retain their respective original rights and are not relicensed by this project. See [preservation/README.md](preservation/README.md).
