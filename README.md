# OpenMaxFire

OpenMaxFire is a preservation and reverse-engineering project for the discontinued Bixby MaxFire 110/115 biomass stove ecosystem. It archives the factory BixCheck service software and firmware, documents the J3 computer interface, and is building a modern cross-platform Windows/Linux/macOS service tool plus a deliberately limited ESP32/Home Assistant controller.

## Current status

The repository contains the recovered vendor packages, BixCheck 5.x manual, all
preserved 2.06/2.70/2.71 firmware images, portable and annotated disassemblies,
a deep three-EXE comparison, decoded application tables, an experimental PIC
emulator, a virtual serial lab, photographs, provenance records, and the first
cross-platform read-only service-tool foundation.

Confirmed by static evidence:

- All four preserved firmware images target a PIC16F877A and pass Intel HEX checksum validation.
- The controller recognizes ASCII register commands `CRXX` and `CWXXYY`.
- Requests are fixed at four/six bytes and have no terminator.
- Addressed responses are six ASCII characters. Firmware telemetry lines are
  `Txxvv` one-byte frames; logical 16-bit fields use adjacent high/low slots.
  BixCheck accepts CR or LF termination.
- BixCheck maps remote OFF/ON/UP/DOWN to `CW0E11`, `CW0E12`, `CW0E14`, and `CW0E18`.
- CR0B/CR0C expose firmware `2.06`, `2.70`, or `2.71` as constant bytes.
- BixCheck 5.0.21 selects 9,600 baud; 5.5.x selects 9,600/19,200, all at 8N1.
- The configuration/telemetry/Checkout tables, lean-burn transforms, and
  configuration checksum are now machine-readable.
- The experimental emulator runs the actual firmware: all 45 `CR00`-`CR0E`
  handlers, all 48 safe synthetic `CW00`-`CW0F` handler probes, all 91 periodic
  telemetry slots, and all 768 `AR00`-`ARFF` internal-EEPROM reads complete
  their expected bounded paths, while the PICkit loader answers `EA` with
  `EB`. The keyed `CW0FC4` loader reset is excluded.
- T09 is RAM `0x4C`; its six operating families, startup substates, thermostat
  flag, heat levels, and cross-version handler dispatch are reconstructed.
  Both firmware and BixCheck ignore state bit 7.
- BixCheck masks plus firmware GPIO/ADC traces map door to CR02.5/RD1, ash
  drawer to CR02.6/RD4, thermostat to CR06.2/RB4, fan pot to CR09/AN3, and feed
  pot to CR0A/AN4. These are offline mappings, not live wiring validation.
- The common input scanner maps front-panel buttons into CR01, the burn-drive
  limit switch to CR02.0, and the fuel selector to CR02.2 (`1`=Fuel A/corn,
  `0`=Fuel B/wood). A preserved 9067-0404 board diagram independently
  corroborates those physical labels.
- The same three firmware generations map the diagram's J10 exhaust sensor
  through RA4/T0CKI and TMR0 to CR05, and J9 feeder-wheel sensor through RD0
  and a motor-gated interval counter to CR02.4/CR07. BixCheck's exact raw
  Checkout thresholds are documented; their engineering units are not.
- Installed photographs expose a `-0604` main-PCB suffix consistent with the
  owner-reported `9067-0604` and directly show its black four-contact J3
  housing; individual pin functions and electrical levels remain unknown.
- The recovered stove is serial 5215; its owner identifies it as a MaxFire 115.

Not yet confirmed on physical hardware:

- J3 pinout and electrical levels.
- Physical oscillator marking/frequency. The exact BixCheck rates and firmware
  divisors strongly imply 10 MHz, but the board has not been checked.
- Live electrical/timing validation of the reconstructed response grammar.
- Physical validation of the offline button/switch/door/drawer/thermostat/pot
  and J9/J10 sensor mappings on serial 5215's owner-reported,
  photo-corroborated 9067-0604 board.
  The preserved diagram depicts 9067-0404, and CR02.1/CR02.7 remain physically
  unassigned.
- Any remote command on the actual stove.

No live connection should be attempted until [SAFETY.md](SAFETY.md) and the [J3 working specification](docs/protocol/j3-protocol.md) have been reviewed.

## Project goals

1. Preserve original Bixby software, firmware, manuals, release notes, photographs, and hardware documentation without modifying the originals.
2. Fully document the MaxFire 110/115 J3 protocol and controller register space.
3. Replace essentially all BixCheck functions with a cross-platform Windows,
   Linux, and macOS CLI/application.
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

maxfirectl ports
# Lists COM ports on Windows and /dev devices on Linux/macOS without opening them
```

The portable read-only foundation now includes serial-port discovery, exact
timestamped JSONL traffic capture, bounded register queries, stove identity,
and complete `AR00`-`ARFF` JSON backups with checksum diagnostics. Live I/O is
intentionally gated and requires an explicit port, baud rate, and
acknowledgement flag. Do not open a stove-connected port until the cable and J3
electrical interface have been characterized; opening a port can transition
DTR/RTS even when no payload is transmitted.

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
[the cross-platform service-tool guide](docs/cli/cross-platform-service-tool.md),
[the serial command cheat sheet](docs/protocol/serial-command-cheat-sheet.md),
[the BixCheck comparison](docs/reverse-engineering/bixcheck-comparison.md),
[the BixCheck runtime workflows](docs/reverse-engineering/bixcheck-runtime-workflows.md),
[the J3 protocol](docs/protocol/j3-protocol.md),
[the controller-write map](docs/protocol/controller-writes.md),
[the telemetry map](docs/protocol/telemetry-fields.md),
[the operating-state machine](docs/reverse-engineering/operating-state-machine.md),
[the firmware comparison](docs/reverse-engineering/firmware-comparison.md),
[the exhaustive emulator pass](docs/reverse-engineering/emulator-deep-pass.md), and
[the preservation manifest](preservation/MANIFEST.md).

## Licensing

OpenMaxFire-authored code and documentation are released under the MIT License. Recovered Bixby vendor artifacts and user photographs retain their respective original rights and are not relicensed by this project. See [preservation/README.md](preservation/README.md).
