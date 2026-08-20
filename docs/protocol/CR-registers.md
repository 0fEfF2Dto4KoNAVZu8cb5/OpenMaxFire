# CR register map

This table records handlers identified in firmware 2.71. Meanings are separated from raw implementation so uncertain interpretations remain explicit.

| Register | Firmware result | Interpretation / status |
|---|---|---|
| CR00 | constant `0x00` | confirmed implementation |
| CR01 | bank1 RAM `0x53` | state byte; semantic meaning unknown |
| CR02 | packed input byte | high-interest physical/multiplexed input status |
| CR03 | packed status byte | includes RB1/RB5 output states + internal flags |
| CR04 | RAM `0x22` | meaning unknown |
| CR05 | RAM `0x34` | meaning unknown |
| CR06 | packed flags | includes RB4 physical input |
| CR07 | derived/scaled from RAM `0x44/0x45` | meaning unknown |
| CR08 | constant `0x07` | confirmed implementation |
| CR09 | RAM `0x2E` | meaning unknown |
| CR0A | RAM `0x2F` | meaning unknown |
| CR0B | constant `0x02` | likely version/identity component; not yet proven |
| CR0C | constant `0x71` | likely version/identity component; not yet proven |
| CR0D | constant `0x00` | confirmed implementation |
| CR0E | constant `0x00` | confirmed implementation |

## CR02 bit layout

| Bit | Source | Current meaning |
|---:|---|---|
| 0 | multiplexed reading sampled through RD3 | unknown |
| 1 | multiplexed reading sampled through RD3 | unknown |
| 2 | multiplexed reading sampled through RD3 | unknown |
| 3 | internal/mux state | unknown |
| 4 | RD0 | physical input, function unknown |
| 5 | RD1 | physical input, function unknown |
| 6 | RD4 | physical input, function unknown |
| 7 | RE1 | physical input, function unknown |

## CR03 bit layout

- bit 0: RB1 state
- bit 1: RB5 state
- bit 2: RAM `0x56` bit 5
- bit 3: RAM `0x56` bit 7

## CR06 bit layout

- bit 0: RAM `0x2D` bit 0
- bit 1: RAM `0x2D` bit 1
- bit 2: RB4 physical input

## Door/hopper investigation

Best current candidates for a direct digital door/switch signal are `CR02` bits 4-7 and `CR06` bit 2. Static analysis has **not** yet proven which is the firebox door, hopper switch, fuel switch, or another interlock.

Next experiment: continuously poll read registers and perform one physical action at a time (open/close door, operate hopper-related switch, etc.), recording bit transitions.
