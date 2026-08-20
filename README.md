# OpenMaxFire

OpenMaxFire is a preservation, reverse-engineering, diagnostics, and modern-control project for Bixby MaxFire 110/115 stoves.

The project has two complementary goals:

1. **Preserve the original platform** — factory software, firmware, documentation, protocol behavior, calibration knowledge, and service workflows.
2. **Build maintainable replacements** — a Linux-first BixCheck-compatible toolchain and a reliable ESP32/Home Assistant controller for day-to-day stove operation.

## Current state

As of 2026-08-20:

- Bixby firmware `2.71 / 080315` has been archived and disassembled.
- The controller MCU has been identified as a **Microchip PIC16F877A**.
- The firmware's UART initialization and command parser have been located.
- The protocol skeleton is confirmed in firmware: `CRxx` reads a byte/register and `CWxxYY` writes a byte/value, using ASCII hexadecimal.
- `CR02` and `CR06` expose several physical/input-related states that are candidates for door/hopper detection.
- Live J3 differential testing is the next hardware experiment once the serial cable is available.

## Repository map

- `docs/` — living technical documentation.
- `firmware/original/` — untouched factory firmware artifacts.
- `firmware/disassembly/` — derived assembly listings and annotations.
- `firmware/analysis/` — reproducible analysis outputs.
- `firmware/archives/` — preserved analysis bundles from reverse-engineering sessions.
- `protocol/` — machine-readable protocol/register knowledge.
- `tools/` — scripts for firmware and serial analysis.
- `research/` — provenance, research log, open questions, and archival status.
- `openmaxfire/` — future Linux CLI/application implementation.
- `esphome/` — future permanent ESP32/Home Assistant implementation.

## Safety and preservation rules

- Never modify the only copy of a factory artifact.
- Record hashes for original firmware and software.
- Treat unverified register meanings as hypotheses, not facts.
- Prefer read-only serial experiments before write commands.
- Do not connect USB 5 V/VCC to the stove merely for UART communication; the stove powers its own controller.
- The stove contains mains-powered circuitry. Hardware probing must account for ground/reference and isolation safety.

## Legal/provenance note

Factory binaries and documents are kept separate from original OpenMaxFire code and derived notes. Redistribution status should be reviewed before making the repository public. The repository is currently private while archival provenance is being established.
