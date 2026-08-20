# Reverse-engineering log

## 2026-08-18

- Reviewed BixCheck service documentation for MaxFire 110/115.
- Established preservation goal and Linux BixCheck feature-parity scope.
- Confirmed factory software supports monitoring, calibration/readback, telemetry, flue monitoring, logging, checkout testing, and firmware downloading.

## 2026-08-20 — HEX analysis

- Analyzed `Bixby_0271_080315.hex` as Intel HEX.
- Identified target as PIC16F877A.
- Preserved original HEX and generated address maps, dumps, hashes, and binary-derived analysis files.

## 2026-08-20 — disassembly

- Disassembled with `gpdasm` for PIC16F877A.
- Generated readable, reassemblable, memory-dump, and HEX-info outputs.
- Annotated reset vector, interrupt path, UART setup, protocol parser, and register-read mapping.

## 2026-08-20 — protocol discoveries

- Confirmed `CRxx` / `CWxxYY` ASCII protocol in firmware.
- Mapped `CR00` through `CR0E` static handlers.
- Identified `CR02` as a packed physical/multiplexed input byte.
- Identified `CR06.2` as RB4.
- Established live differential polling as the fastest method to identify door/hopper inputs.

## Blocked / waiting

Live J3 testing is waiting on the ordered USB-UART cable and connector hardware.
