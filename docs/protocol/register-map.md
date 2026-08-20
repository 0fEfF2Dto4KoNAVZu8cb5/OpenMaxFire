# Firmware CR register map

The detailed map below comes from the 2.71 PIC16F877A disassembly, not a live stove. The same CR00-CR0E dispatch structure exists in 2.06 and 2.70. RAM names remain provisional and banked register names must be checked against STATUS bank bits.

## Cross-version constants

| Read | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: |
| `CR00` | `0x00` | `0x00` | `0x00` |
| `CR08` | `0x05` | `0x07` | `0x07` |
| `CR0B` | `0x02` | `0x02` | `0x02` |
| `CR0C` | `0x06` | `0x70` | `0x71` |
| `CR0D` | `0x00` | `0x00` | `0x00` |
| `CR0E` | `0x21` | `0x02` | `0x00` |

CR0B/CR0C are strongly identified as firmware version bytes. CR08 is probably a data-format/database generation because it moves from 05 to 07 with the preserved software generations, but that name remains unconfirmed. CR0E read behavior changes even though BixCheck 5.5.01 uses writes to 0x0E for remote-button actions. See the [full firmware comparison](../reverse-engineering/firmware-comparison.md).

## 2.71 detailed handlers

| Request | Static return/source | Interpretation |
| --- | --- | --- |
| `CR00` | Constant `0x00` | Useful first read-only probe |
| `CR01` | Bank-1 RAM byte 0x53 | State byte; semantic mapping unresolved |
| `CR02` | Packed input byte | See bit table below |
| `CR03` | Packed status/output byte | See bit table below |
| `CR04` | RAM byte 0x22 | Unknown |
| `CR05` | RAM byte 0x34 | Unknown |
| `CR06` | Packed flags | See bit table below |
| `CR07` | Derived/scaled from RAM 0x44/0x45 | Unknown engineering value |
| `CR08` | Constant `0x07` | Likely data-format/database version 07 |
| `CR09` | RAM byte 0x2E | Unknown |
| `CR0A` | RAM byte 0x2F | Unknown |
| `CR0B` | Constant `0x02` | Likely firmware major byte |
| `CR0C` | Constant `0x71` | Likely firmware minor byte; together 2.71 |
| `CR0D` | Constant `0x00` | Unknown/reserved |
| `CR0E` | Constant `0x00` on read | Writes to 0x0E carry remote buttons in BixCheck |

## CR02

| Bit | Static source | Candidate meaning |
| ---: | --- | --- |
| 0-2 | Three multiplexed readings sampled through RD3 | Unknown switch/input bank |
| 3 | Internal/multiplexer state | Unknown |
| 4 | RD0 | Direct digital input |
| 5 | RD1 | Direct digital input |
| 6 | RD4 | Direct digital input |
| 7 | RE1 | Direct digital input |

## CR03

| Bit | Static source |
| ---: | --- |
| 0 | RB1 output state |
| 1 | RB5 output state |
| 2 | RAM 0x56 bit 5 |
| 3 | RAM 0x56 bit 7 |
| 4-7 | Zero in the observed handler |

## CR06

| Bit | Static source |
| ---: | --- |
| 0 | RAM 0x2D bit 0 |
| 1 | RAM 0x2D bit 1 |
| 2 | RB4 direct input |
| 3-7 | Zero in the observed handler |

## Door-state investigation

The BixCheck manual proves that Checkout can distinguish door-switch open/closed and ash-drawer-switch open/closed. Firmware startup configures RD0, RD1, RD3, RD4, RE0, RE1, RB0, RB4, RB6, RB7, and RA0-RA5 as inputs. The best directly exposed candidates are CR02 bits 4-7 and CR06 bit 2.

Static analysis has not assigned a physical switch to any one bit. The safe experiment is to record a CR02/CR06 baseline and toggle one physical switch at a time while the stove is not burning.
