# Firmware 2.06 J3 checksum repair

Date: 2026-08-30  
Controller: firmware 2.06 / data format 05 / build 21  
Command: one `CW0100` checksum-persistence request  
Result: successful and cold-boot persistent

## Pre-write gate

- Exact identity was re-read as CR08=`05`, CR0B/CR0C=`02`/`06`, and
  CR0E=`21`.
- A short monitor showed stable Off, closed firebox/ash drawer, and zero
  timeouts.
- A third complete A00-AFF backup was byte-identical to the two earlier reads,
  raw SHA-256
  `c1b8da891e94357f1d3bb23004d44aa663943f1d28fb734bef56dfa3e5bd0cfd`.
- The pre-write checksum was stored `D168`, calculated `576B`.

The first CLI invocation used bare `01 00` arguments and was rejected during
argument parsing because byte values require `0x` notation. It did not open the
port or create traffic. The corrected invocation transmitted exactly one frame;
the complete traffic record contains only:

```text
43 57 30 31 30 30    CW0100
```

## Immediate verification

Two independent complete A00-AFF backups both reported stored/calculated
`576B/576B` and were byte-identical. Comparison with the pre-write image found
exactly two changes:

| Address | Before | After |
| --- | --- | --- |
| A00 | `D1` | `57` |
| A01 | `68` | `6B` |

No identity, calibration, fuel-table, or unused EEPROM byte changed. The
repaired 256-byte EEPROM SHA-256 is
`5416b4acecd2e4b0f7dbc3d2bc76e6c4a846d96e55e7e404c94e7f0614d27ff2`.
A post-write monitor showed stable Off with zero timeouts.

## Cold-boot verification

The operator removed AC, unplugged USB to eliminate FTDI backpower, waited,
restored AC with USB absent, allowed a normal boot, and then reconnected USB.
Read-only identity remained exact 2.06/05/21. A complete post-cold-boot backup
was byte-identical to both repaired copies, retained checksum `576B/576B`, and
had the same SHA-256.

The final monitor showed the expected power-up Cooldown (`T09=10`), convection
command T06=`19`, exhaust target T18=`57`, live exhaust feedback T04/CR05=`8B`,
and zero timeouts. This is the already characterized approximately 14-minute
38-second 2.06 power-up cooldown.

No actuator, remote-button, reset, loader, program-memory, identity, calibration,
or fuel-table write was sent. PICkit recovery was not required.
