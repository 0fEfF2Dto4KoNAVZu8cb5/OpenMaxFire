# BixCheck 5.0.21 reverse engineering

## Artifact identity

| Field | Value |
| --- | --- |
| Package | `Bixby110_115_02060021_and_manual.zip` |
| Executable | `BixCheck_5021.exe` |
| Size | 441,552 bytes |
| SHA-256 | `0f51f1b9ffe12011928c7821ecc07db92b2bf98a1d82e5fcf605d464316d52d4` |
| PE linker timestamp | 2007-04-26 14:38:38 UTC |
| Application | BixCheck Control/Monitor/Checkout 5.0.21 |
| Downloader | 1.4 |
| Intended stove software | 02.06 |
| Data format | 05 |

## What the deep pass recovered

The executable retains 640 COFF function symbols at 639 unique offsets and the
same original source-unit structure seen in the later builds. The normal serial
request builder, Checkout action senders, and downloader state machine are
semantically equivalent across all three versions.

This generation opens the PC serial port at exactly 9,600 baud and configures
8N1. It uses 20,480-byte Win32 input/output queues. Requests are the same
unterminated four-byte reads and six-byte writes used later; CR/LF-terminated
responses use the same addressed and telemetry grammar.

The matching firmware 2.06 loads `SPBRG=0x40`, while later firmware loads
`0x20`. The exact 9,600-baud host setting strongly supports a 10 MHz controller
oscillator for 2.06, although that oscillator has not yet been physically
checked on serial 5215.

## Configuration generation

5.0.21 has 71 adjustment records. It contains the two eight-level fuel tables,
startup and ash-dump settings, but not the later lean-burn fields A6B-A6E and
A9B-A9E. It exposes the thermostat heat-level field only at A9A; the 5.5
generation contains corresponding A6A and A9A records.

Most numeric records in this build leave the explicit UI maximum/minimum fields
zero. BixCheck 5.5 adds populated bounds and stronger range-check helpers.

The checksum algorithm is the same add-then-rotate-left-16 core. This build
supports data formats through 05 and does not apply lean-burn display-to-wire
transforms because those fields do not exist.

## Monitor and Checkout

The telemetry table contains 30 records. Its addresses and labels match 5.5.00,
including `T19 Drop limit`, `V1B Time to ash dump`, and the two computed heat
level entries.

Checkout data and command actions are byte-for-byte/semantically identical to
the later applications, except convection-fan actions use legacy values
`CW0801` through `CW0804`; newer data formats use percentage-like values
`CW0819`, `CW0832`, `CW084B`, and `CW0864`.

The EXE contains the same dormant ninth automatic `Plate motor cycle test`
record. Only eight automatic records are reachable, so the operational total is
45 tests.

## Downloader

Downloader 1.4 implements the same binary framing as the later builds; its
paired payload is firmware 02.06. The package separately includes a PICkit
image containing the protected/reset-time service region. In the experimental
PIC14 emulator, the Downloader firmware answers `CR00` with `CR0000` plus LF,
and the PICkit image answers bootloader identify `EA` with `EB`.

See `reverse-engineering/bixcheck/5.0.21/` for the generated inventory, decoded
tables, focused assembly, and call graph.
