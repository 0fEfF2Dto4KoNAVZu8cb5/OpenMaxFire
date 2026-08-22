# Serial 5215 live evidence: firmware 2.02 / format 04

This directory preserves the read-only live evidence acquired on 2026-08-22
UTC from the cold, non-firing MaxFire 115 controller associated with appliance
serial 5215.

See the interpreted report:
[`docs/reverse-engineering/live-fw202-format04.md`](../../../docs/reverse-engineering/live-fw202-format04.md).

## Evidence policy

- Capture files are byte-identical to the uploaded artifacts.
- The duplicate upload `maxfire-fw202-format04-eeprom(1).json` was not stored a
  second time; it was byte-identical to the retained file.
- JSONL timestamps and the original lowercase response bytes are retained.
- No `CW`, `AW`, loader, remote-ON, or actuator request appears in this set.
- `SHA256SUMS.txt` covers every retained artifact in this directory.

## Top-level artifacts

| Path | Purpose |
| --- | --- |
| `maxfire-adapter-identification.json` | Serial-port inventory proving the FTDI `TTL-232R-5V-WE`, USB `0403:6001`, serial `ABBAUPPN` |
| `maxfire-fw202-format04-eeprom.json` | Lossless A00-AFF backup with identity, checksum, decoded individualization, and `raw_hex` |
| `cold-register-results.txt` | Human-readable first CR00-CR0E cold sweep; CR0B's first partial-frame failure is represented by its separate raw log |
| `captures/` | Exact JSONL sessions and byte-direction traffic events |

## Capture groups

| Files | Meaning |
| --- | --- |
| `first-cr00.jsonl`, `first-identify.jsonl` | First successful 9,600-baud request and identity sequence |
| `CR00.jsonl` through `CR0E.jsonl` | Individual cold register reads |
| `fw202-backup-2.jsonl`, `fw202-backup-3.jsonl` | Two complete independent identity + A00-AFF read sessions with interleaved telemetry |
| `fw202-powerup-rx-only*.jsonl`, `fw202-idle-after-reads.jsonl` | Receive-only port-opening experiments; each contains only `00 0A`, not a unique power-up signature |
| `fw202-identify-slow.jsonl` | Slow baseline identity used to expose a telemetry cycle |
| `fw202-identify-door-open.jsonl`, `fw202-identify-door-closed-control.jsonl` | First firebox-door comparison |
| `fw202-identify-ash-drawer-open*.jsonl`, `fw202-identify-all-closed-long.jsonl` | Ash-drawer open/closed comparison and LED-flash sampling |
| `fw202-identify-firebox-door-open-long.jsonl` | Longer firebox-door capture including `T06` and flashing `T08` states |
| `fw202-identify-thermostat-open-long.jsonl`, `fw202-identify-thermostat-restored-long.jsonl` | Thermostat A-B-A comparison confirming `T0C & 0x08` |
| `fw202-identify-fuel-corn-long.jsonl` | Corn/Fuel-A telemetry correlation attempt |

The first failed long firebox-door attempt was overwritten locally before a
successful capture, so it is not represented as a file. Its observed error,
`no matching CR08 response within 16 frames`, is recorded in the interpreted
report and motivated the parser regression test.
