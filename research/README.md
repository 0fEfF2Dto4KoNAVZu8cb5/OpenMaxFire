# Research evidence

`research/` holds physical-session evidence produced by real hardware. It is
separate from both immutable vendor originals and derived static-analysis
outputs.

## Live sessions

| Session | Contents |
| --- | --- |
| [2026-08-22 firmware 2.02 / format 04](live/2026-08-22-fw202-format04/README.md) | Exact J3 JSONL traffic, three EEPROM reads, adapter identity, cold register sweep, input correlations, and per-file checksums |

Raw captures must remain byte-identical. New interpretations belong in
`docs/reverse-engineering/` and should link back to the exact capture. Each
session directory should include a README, a checksum inventory, device and
connection identity, safety state, and an explicit list of any transmitted
state-changing bytes.
