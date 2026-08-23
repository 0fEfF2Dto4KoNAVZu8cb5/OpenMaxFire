# OpenMaxFire

OpenMaxFire is a preservation and reverse-engineering project for the discontinued Bixby MaxFire 110/115 biomass stove ecosystem. It archives the factory BixCheck service software and firmware, documents the J3 computer interface, and is building a modern cross-platform Windows/Linux/macOS service tool plus a deliberately limited ESP32/Home Assistant controller.

## Current status

The repository contains the recovered vendor packages, the BixCheck service
manual and MaxFire Model 115 owner manual, all
preserved 2.06/2.70/2.71 firmware images, portable and annotated disassemblies,
a deep three-EXE comparison, decoded application tables, an experimental PIC
emulator, a virtual serial lab, photographs, provenance records, and the first
cross-platform read-only service-tool foundation. A live cold/off session now
documents serial 5215's previously unpreserved firmware 2.02/data format 04,
working J3 pinout, 9,600-baud traffic, physical inputs, telemetry correlations,
and three identical EEPROM backups. Version 0.3 adds a first-class read-only
monitor, freshness/stale-data tracking, decoded JSONL snapshots, and offline
replay against the preserved byte-exact traffic corpus. Version 0.4 adds the
offline-tested low-level service foundation: generic A/C/D reads and writes,
fresh-readback verification, exact-byte raw exchange, and validated fail-fast
register transactions. Known loader traffic remains isolated and blocked.
Version 0.5 adds the reusable controller-aware API foundations: exact profiles
and read-only detection, typed state, format-05/07 configuration images and
diff/restore planning, all 45 Checkout definitions, firmware-image validation
and loader-block planning, idempotent control planning, and an API-compatible
simulator. Unvalidated state-changing execution remains deliberately blocked.
Version 0.6 adds an owned controller session, typed snapshot iteration, an
automated read-only Checkout runner, and simulator-only configuration,
normal-control, and actuator-cleanup workflows. Real state-changing execution
continues to fail closed. Version 0.7 adds API-native exact-byte audit trails
and digestable workflow receipts, authenticates the complete four-image
firmware corpus, and implements the reconstructed binary loader as a strict
simulator-only state machine with retries, progress, corruption/disconnect
faults, and final memory comparison. It still contains no physical flashing
path, bootloader-entry write, or erase command.

> **Have an unlisted version?** If you have any BixCheck software, MaxFire
> firmware, manual, hardware documentation, or related material from a version
> not listed in this repository, please contact me at [openmaxfire@mailbruh.com](mailto:openmaxfire@mailbruh.com) or open a pull request so it
> can be preserved and reverse-engineered.

Confirmed by static, photographic, emulator, and live evidence:

- All four preserved firmware images target a PIC16F877A and pass Intel HEX checksum validation.
- The controller recognizes ASCII register commands `CRXX` and `CWXXYY`.
- Requests are fixed at four/six bytes and have no terminator.
- Addressed responses are six ASCII characters. Firmware telemetry lines are
  `Txxvv` one-byte frames; logical 16-bit fields use adjacent high/low slots.
  BixCheck accepts CR or LF termination.
- BixCheck maps remote OFF/ON/UP/DOWN to `CW0E11`, `CW0E12`, `CW0E14`, and `CW0E18`.
- CR0B/CR0C expose firmware identity bytes; the live controller reports `2.02`
  and `CR08=04`, older than the preserved 2.06/format-05 release.
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
  pot to CR0A/AN4. One-at-a-time cold/off tests live-validated these mappings
  and their polarity on the physical 9067-0604 controller.
- The common input scanner maps front-panel buttons into CR01, the burn-drive
  limit switch to CR02.0, and the fuel selector to CR02.2 (`1`=Fuel A/corn,
  `0`=Fuel B/wood). A preserved 9067-0404 board diagram and the factory owner
  manual independently corroborate those physical labels.
- The factory MaxFire Model 115 owner manual documents thermostat behavior,
  safety-interlock timeouts, fault indicators, maintenance intervals, wiring,
  and service parts. It confirms that the Rev. A thermostat behavior does not
  start the stove and that no hopper-level/lid sensor appears in the wiring
  diagram.
- The same three firmware generations map the diagram's J10 exhaust sensor
  through RA4/T0CKI and TMR0 to CR05, and J9 feeder-wheel sensor through RD0
  and a motor-gated interval counter to CR02.4/CR07. BixCheck's exact raw
  Checkout thresholds are documented; their engineering units are not.
- Bare-board photographs directly expose the complete `9067-0604` marking,
  PIC16F877A, `10.000` MHz oscillator, both PCB sides, and J3 routing area.
- Continuity and live traffic establish J3-1=stove TX, J3-2=stove RX,
  J3-4=ground; J3-3 is unresolved and disconnected. An official FTDI
  `TTL-232R-5V-WE`, used without VCC, exchanged valid 9,600-baud traffic.
- Three independent live A00-AFF reads agree byte-for-byte and have a matching
  `EFCE` EEPROM checksum. The stored controller serial/date strings differ from
  the appliance nameplate and are preserved without an assumed explanation.
- The recovered stove is serial 5215; its owner identifies it as a MaxFire 115.

Not yet confirmed on physical hardware:

- J3-3 function, exact idle/noise-margin measurements, and behavior under
  operating electrical loads.
- Physical J9/J10 sensor correlation, CR02.1/CR02.7 functions, and most
  format-04 telemetry meanings.
- Any remote write, actuator/service command, or operating-stove control.
- A recoverable in-circuit method for preserving firmware-2.02 program memory.
- Firmware-loader erase/program acknowledgements or interrupted-transfer recovery.

No new board revision or state-changing live connection should be attempted
until [SAFETY.md](SAFETY.md), the
[J3 working specification](docs/protocol/j3-protocol.md), and the
[first-live report](docs/reverse-engineering/live-fw202-format04.md) have been
reviewed.

## Project goals

1. Preserve original Bixby software, firmware, manuals, release notes, photographs, and hardware documentation without modifying the originals.
2. Fully document the MaxFire 110/115 J3 protocol and controller register space.
3. Implement essentially all BixCheck machine-facing behavior in a reusable,
   cross-platform Python API, then expose it through separate CLI and GUI clients.
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

maxfirectl replay research/live/2026-08-22-fw202-format04/captures/\
fw202-identify-firebox-door-open-long.jsonl --json
# Reconstructs monitor state without opening a serial port

maxfirectl transaction plan.json --dry-run
# Validates and canonicalizes a register transaction without opening a port
```

The portable foundation now includes serial-port discovery, exact
timestamped JSONL traffic capture, timeout-bounded register queries, stove identity,
complete `AR00`-`ARFF` JSON backups with checksum diagnostics, continuous
read-only CR00-CR0E monitoring, stale-data detection, and capture replay. Live I/O is
intentionally gated and requires an explicit port, baud rate, and
acknowledgement flag. Addressed matching tolerates partial opening lines and
arbitrarily many valid telemetry frames until the configured serial timeout.
Opening a port can still transition DTR/RTS even when no payload is transmitted.
The low-level 0.4 layer also exposes generic A/C/D writes, optional fresh
readback verification, raw byte exchange, and JSON transaction plans behind a
second state-change acknowledgement. These new write paths are offline-tested
but have not been authorized or exercised on the physical stove. See the
[low-level service layer](docs/cli/low-level-service-layer.md).

The Python API builds profile-aware service models above that
low-level layer without adding presentation-specific behavior. See the
[API architecture](docs/api/README.md) and
[v0.7 audit/loader laboratory](docs/api/v0.7-audit-loader-lab.md).

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

- [`preservation/`](preservation/README.md) - recovered files as received, provenance, manifests, and hashes
- `reverse-engineering/` - EXE tables/call graphs, firmware, disassembly,
  comparisons, and emulation traces
- [`research/`](research/README.md) - byte-identical physical traffic, EEPROM, adapter, and
  checksum evidence
- [`docs/`](docs/README.md) - documentation index, research status, safety boundary, and roadmaps
- [`docs/api/`](docs/api/README.md) - reusable Python API boundary and completion roadmap
- [`docs/cli/`](docs/cli/cross-platform-service-tool.md) - command-line client behavior and usage
- [`protocol/`](protocol/README.md) - machine-readable evidence maps; runtime behavior lives in the Python API
- `src/openmaxfire/` - reusable Python protocol, transport, profile, service, audit, and simulation API
- [`tools/`](tools/README.md) - deterministic static-analysis, emulation, integrity, and virtual-lab helpers
- [`tests/`](tests/README.md) - portable API tests and deterministic analysis regression tests
- [`examples/`](examples/read-only-register-plan.json) - presentation-neutral example plans
- [`.github/workflows/`](.github/workflows/cross-platform-tests.yml) - cross-platform tests and archive-integrity verification

Contribution and preservation rules are in [CONTRIBUTING.md](CONTRIBUTING.md).

Start with [the research status](docs/STATUS.md),
[the Python API roadmap](docs/api/README.md),
[the firmware-2.02/data-format-04 live report](docs/reverse-engineering/live-fw202-format04.md),
[the bare-controller photographs](docs/hardware/bare-controller-photographs.md),
[the MaxFire owner-manual analysis](docs/manuals/maxfire-owner-manual-2020866-rev-a.md),
[the cross-platform service-tool guide](docs/cli/cross-platform-service-tool.md),
[the low-level service layer](docs/cli/low-level-service-layer.md),
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
