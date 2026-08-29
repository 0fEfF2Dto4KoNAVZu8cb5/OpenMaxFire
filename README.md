# OpenMaxFire

OpenMaxFire is a preservation and reverse-engineering project for the discontinued Bixby MaxFire 110/115 biomass stove ecosystem. It archives the factory BixCheck service software and firmware, documents the J3 computer interface, and is building a modern cross-platform Windows/Linux/macOS service tool plus a deliberately limited ESP32/Home Assistant controller.

## Current status

The repository contains the recovered vendor packages, the BixCheck service
manual and MaxFire Model 115 owner manual, all
preserved 2.02/2.06/2.70/2.71 firmware images, portable and annotated disassemblies,
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
and digestable workflow receipts, authenticates the then-complete four-image
firmware corpus, and implements the reconstructed binary loader as a strict
simulator-only state machine with retries, progress, corruption/disconnect
faults, and final memory comparison. It still contains no physical flashing
path, bootloader-entry write, or erase command.
Version 0.8 completes the currently evidence-backed offline loader model:
classified `E8`/`E5`, four-word partial rows, protected-address handling,
reset-vector relocation, the exact BixCheck retry edge, and simulated
handoff/reconnect. It also corrects format-04 `T09` as non-discriminating and
adds a fail-closed PIC16F877A repeated-read/clone authentication toolkit plus a
PICkit 3 preservation procedure. Physical flashing remains absent.
Version 0.9 adds a separate guarded experimental J3 flasher. It authenticates
the three exact factory Downloader images and their complete wire-frame
sequences, fixes the loader rate at 9,600 baud, rapidly probes the roughly
78 ms reset window, creates an authenticated exact-image rescue bundle, and
requires a zero-write loader/handoff rehearsal. It then keeps one exclusive
serial handle, inhibits host sleep, classifies and bounds every block outcome,
defers ordinary termination during programming, writes crash-resistant state
and byte evidence, verifies the target application at its own baud, and
requires byte-identical EEPROM afterward. Delayed replies must match the exact
prior phase, and unresolved recovery ownership advances to one self-contained
session at a time. It never sends `CW0FC4`. Physical
programming and recovery still require the published sacrificial-hardware
qualification matrix before production use.

Version 0.9.1 corrects the application-handoff check discovered during the
first physical zero-write rehearsals. After the loader acknowledges `ED` with
`E4`, the host remains transmit-silent until it receives unsolicited `T` or
`DW` application telemetry; only then may it send `CR00`. This prevents an
early four-byte request from overrunning firmware 2.02's two-byte USART receive
FIFO during startup. The change addresses the persistent post-handoff `CR00`
failure; it does not qualify the direct USB-TTL electrical interface or live
Flash programming.

Version 0.10 adds an offline complete-PICkit image composer and five derived,
hash-manifested post-J3/pre-calibration predictions for the factory-2.06 and
serial-5215 lineages. It reproduces the loader's reset-word relocation and
sparse-write behavior while preserving the base loader, EEPROM, configuration,
and User IDs. The known factory 2.06 Downloader/PICkit pair is an exact mapped-
memory golden check, and every derived image boots and answers `CR00` in the
PIC14 emulator. Physical whole-chip comparison on expendable hardware remains
required before these are treated as verified recovery images.

On 2026-08-28 the first complete PICkit export from serial 5215's original
firmware-2.02 PIC was preserved. It contains all program memory, EEPROM, User
IDs, and configuration; its EEPROM exactly matches the earlier live J3 backup,
and its resident loader exactly matches the factory 2.06 PICkit loader. The
owner reports checking the file hash. Additional independent exports remain
pending before the read set is called repeat-authenticated.

Live work on 2026-08-23 physically validated the normal OFF/ON/UP/DOWN command
bytes on firmware 2.02 and captured flashing fault light 8. The API now retains
format-04 `T08` fault bits across the lamp's dark phase and keeps that profile
separate from BixCheck's later raw `T13` alarm field. The verified high-level
physical control executor remains blocked until format-04 state readback is
decoded well enough to prove command outcomes automatically.

> **Have an unlisted version?** If you have any BixCheck software, MaxFire
> firmware, manual, hardware documentation, or related material from a version
> not listed in this repository, please contact me at [contact@openmaxfire.com](mailto:contact@openmaxfire.com) or open a pull request so it
> can be preserved and reverse-engineered.

Confirmed by static, photographic, emulator, and live evidence:

- All five preserved firmware images target a PIC16F877A and pass Intel HEX checksum validation.
- The recovered 2.02 original-controller image is complete: all 8,192 program
  words, 256 EEPROM bytes, four User ID words, and configuration word `0x3F32`.
  CP/CPD are disabled and its SHA-256 is
  `272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab`.
- The controller recognizes ASCII register commands `CRXX` and `CWXXYY`.
- Requests are fixed at four/six bytes and have no terminator.
- Addressed responses are six ASCII characters. Firmware telemetry lines are
  `Txxvv` one-byte frames; logical 16-bit fields use adjacent high/low slots.
  BixCheck accepts CR or LF termination.
- BixCheck maps remote OFF/ON/UP/DOWN to `CW0E11`, `CW0E12`, `CW0E14`, and `CW0E18`.
- Those four normal-control bytes produced the expected physical responses on
  the live firmware-2.02 controller; exact traffic and operator observations
  are preserved.
- CR0B/CR0C expose firmware identity bytes; the live controller reports `2.02`
  and `CR08=04`, older than the preserved 2.06/format-05 release.
- BixCheck 5.0.21 selects 9,600 baud; 5.5.x applications select
  9,600/19,200, all at 8N1. The Downloader itself hard-codes 9,600, matching
  the resident loader's `SPBRG=0x40` at 10 MHz.
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
- Corrected continuity and live-wiring evidence establish J3-1=stove RX,
  J3-2=stove TX, J3-4=ground; J3-3 is unresolved and disconnected. An official FTDI
  `TTL-232R-5V-WE`, used without VCC, exchanged valid 9,600-baud traffic.
- Three independent live A00-AFF reads agree byte-for-byte and have a matching
  `EFCE` EEPROM checksum. The stored controller serial/date strings differ from
  the appliance nameplate and are preserved without an assumed explanation.
- The recovered stove is serial 5215; its owner identifies it as a MaxFire 115.
- Format-04 `T08` is a flashing-indicator bitmap: lights 4, 5, and 8 are
  live-correlated to `0x08`, `0x10`, and `0x80`. The monitor uses temporal
  retention so a snapshot taken during the dark phase does not lose the fault.
- Format-04 `T09=07` stayed constant before ON, during physically observed
  UP/DOWN startup activity, and after OFF. It is not a usable state readback;
  provisional T0C/T15 candidates remain explicitly ineligible for control
  verification.
- The offline PIC16F877A preservation checker authenticates repeated programmer
  exports and original/clone readbacks by program memory, EEPROM, User IDs,
  configuration, Device ID, code-protection state, and SHA-256. It has no
  programmer-control capability.

Not yet confirmed on physical hardware:

- J3-3 function, exact idle/noise-margin measurements, and behavior under
  operating electrical loads.
- Physical J9/J10 sensor correlation, CR02.1/CR02.7 functions, and most
  format-04 telemetry meanings.
- Automatic format-04 state/level verification and high-level physical-control
  execution, despite the low-level normal-control bytes now being live-proven.
- Independent repeat-read authentication of the preserved complete 2.02
  image, followed by spare-chip readback and controlled board recovery.
- Physical firmware-loader erase/program timing, acknowledgement behavior,
  and interrupted-transfer recovery on expendable hardware. Only the guarded
  host's zero-write `EA/EB` and `ED/E4` path has been observed physically.

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
6. Preserve enough firmware and hardware knowledge to keep failed controllers
   repairable and make a compatible replacement motherboard possible if the
   original hardware can no longer be sourced.

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

maxfirectl flash \
  reverse-engineering/firmware/2.70/extracted/Bixby_0270_070206.hex \
  --plan-only --current-profile fw206-format05
# Authenticates and prints the complete J3 plan without opening a port
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
second state-change acknowledgement. The firmware-2.02 remote OFF/ON/UP/DOWN
bytes have been exercised successfully; other write paths remain offline-only
unless their evidence says otherwise. See the
[low-level service layer](docs/cli/low-level-service-layer.md).

The Python API builds profile-aware service models above that
low-level layer without adding presentation-specific behavior. See the
[API architecture](docs/api/README.md) and
[v0.8 offline preservation milestone](docs/api/v0.8-offline-preservation.md).
The experimental live path is documented separately in the
[guarded J3 flashing guide](docs/guides/safe-j3-firmware-flashing.md).

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

Start with [the fault-light guide](docs/guides/fault-lights.md),
[common problems and first checks](docs/guides/common-problems.md),
[the PICkit 3 read-only preservation guide](docs/guides/pickit3-firmware-preservation.md),
[the guarded J3 firmware-flashing guide](docs/guides/safe-j3-firmware-flashing.md),
[the J3 flasher qualification plan](docs/guides/j3-flasher-qualification.md),
[the research status](docs/STATUS.md),
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
