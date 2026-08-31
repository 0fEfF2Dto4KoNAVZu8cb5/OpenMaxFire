# Firmware 2.02 / 2.06 / 2.70 / 2.71 comparison

This report compares the four preserved generations at PIC16F877A word level.
The semantic tables and executable PIC14 probes now cover 2.02, 2.06, 2.70,
and 2.71. Raw tables live in
`reverse-engineering/firmware/comparison/`.

## Major findings

The recovered 2.02 PICkit image is complete. Its 256-byte EEPROM exactly
matches the independently preserved live backup from serial 5215. Its reset
vector and all 384 protected-loader words are identical to 2.06 PICkit; the
loader returns `EB` for `EA` in the experimental emulator. The 2.02 application
is not a renamed 2.06 build: 7,478 of 7,808 words in the application delivery
range differ at the same addresses. Its CR, CW, telemetry, and state-family
paths are now mapped and exercised through the recovered instructions.

1. The `CRXX` / `CWXXYY` ASCII command skeleton exists in all four generations. The nibble decoder, byte parser, CR dispatcher, and ASCII response formatter can be followed across relocated code.
2. Firmware identity is exposed through reads: CR0B returns the major byte `0x02`; CR0C returns `0x02`, `0x06`, `0x70`, or `0x71` by generation.
3. CR08 is `0x04` in 2.02, `0x05` in 2.06, and `0x07` in 2.70/2.71. The
   BixCheck Individualization tables identify C08 as `Stove data format`.
4. UART setup changes at the 2.06-to-2.70 boundary: `SPBRG` is `0x40` in
   2.02/2.06 and `0x20` in 2.70/2.71. `TXSTA=0x26` and `RCSTA=0x90` remain stable.
5. BixCheck 5.0.21 selects exactly 9,600 baud and 5.5.x selects 9,600 or 19,200.
   Paired with the firmware divisors, this strongly implies a 10 MHz controller
   oscillator and intended rates of 9,600 for 2.02/2.06 and 19,200 for 2.70/2.71.
   The physical oscillator must still be measured.
6. The 2.06 PICkit image is a complete external-programmer image: it redirects reset through the resident loader at `0x1E88`, maps all 8,192 program words, and includes 256 EEPROM bytes. The 2.06 Downloader image is an application-update payload; the J3 loader protects direct targets at and above `0x1E80`, redirects application reset words `0x0000`-`0x0003` to `0x1E84`-`0x1E87`, and leaves EEPROM unchanged because the recovered Downloader images contain no EEPROM records.
7. The experimental PIC emulator executes all 58 real CR handlers across the
   four applications without error. Firmware 2.02 has handlers only for
   CR00-CR0C; CR0D/CR0E take its generic zero-response path. The formatters
   emit lowercase A-F nibbles in responses.
8. Bank-aware dynamic dependencies are structurally stable across releases.
   GPIO/ADC differentials identify RD1 as door, RD4 as ash drawer, RB4 as
   thermostat, AN3 as fan pot, and AN4 as feed pot after cross-referencing
   BixCheck Checkout masks.
9. A-unit reads use the PIC16F877A internal data EEPROM. All 1,024 AR00-ARFF
   cross-version probes match checksum-valid synthetic format-04/05/07 fixtures.
10. All four generations contain the same input-multiplexer design. RD2 and
    RD6:RD5 scan the active-low front-panel buttons into CR01; RD7 and RD6:RD5
    scan three active-high RD3 external inputs into CR02.0-2.
11. Static configuration-bank selection fixes CR02.2 as the fuel selector:
    `1`=Fuel A/corn and `0`=Fuel B/wood. BixCheck and the related-board diagram
    corroborate the name; CR02.0 is the burn-drive limit switch and CR02.1
    remains unassigned.
12. The J10 exhaust-sensor path is identical in all generations. `OPTION_REG`
    is loaded with `0xBF`, so unprescaled high-to-low RA4/T0CKI transitions
    increment TMR0. Every 30 RB0 external-interrupt ticks, the count is latched
    into RAM 0x34; CR05 returns it directly.
13. The J9 feeder-wheel path is also stable. While RB1 is active, RB0 external
    interrupts increment RAM 0x47:0x46. An RD0 high-then-low cycle latches the
    interval into 0x45:0x44, and CR07 returns the scaled low byte. Firmware
    2.02 shifts the interval once while latching and four more times in CR07;
    later versions latch directly and shift four times in CR07. RD0's
    instantaneous state is also CR02.4.
14. The mature 2.06/2.70/2.71 generations each have sixteen C-write entries,
    CW00-CW0F. All 48 synthetic probes reach the recovered handler; CW01
    programs checksum bytes A00/A01, and the keyed CW0FC4 loader branch is
    deliberately not executed. Authenticated original 2.02 instead has only 15
    GOTOs through CW0E; CW0F lands on NOPs and has no keyed reset handler.
15. The complete periodic producer emits one physical T byte per line. Forced
    producer execution reaches 113/113 requested slots: T00-T15 in 2.02,
    T00-T1D in 2.06/2.70, and T00-T1E in 2.71, including optional addressed
    D-unit auxiliary lines.
16. The shared state-family RAM byte 0x4C is emitted as T0C in 2.02 and T09 in
    later firmware. The 2.02 T09 comes from unrelated RAM 0x2D, while T15 has
    no state assignment. All four applications dispatch cooldown, off,
    startup, operating/ramping, ash-dump, and fallback families from RAM 0x4C.

## Protocol-anchor matrix

| Function | 2.02 | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: | ---: |
| UART RX interrupt | `0x00FA` | `0x00C6`* | `0x00AE` | `0x00AE` |
| Receive-buffer byte | `0x0EDA` | `0x0E71` | `0x0F63` | `0x0F2E` |
| ASCII-hex nibble | `0x0F13` | `0x0EA4` | `0x0F95` | `0x0F60` |
| ASCII-hex byte | `0x0F2F` | `0x0EC0` | `0x0FB1` | `0x0F7C` |
| Check command `C` | `0x1073` | `0x1008` | `0x1112` | `0x10E8` |
| Check command `W` | `0x107F` | `0x1014` | `0x111E` | `0x10F4` |
| CW table | `0x12E5` (00-0E) | `0x1293` (00-0F) | `0x137D` (00-0F) | `0x135A` (00-0F) |
| Check command `R` | `0x115F` | `0x113F` | `0x1234` | `0x120E` |
| CR table | `0x12FB` (00-0C) | `0x12A7` (00-0E) | `0x1391` (00-0E) | `0x136E` (00-0E) |
| Response formatter | `0x12B7` | `0x1265` | `0x1352` | `0x132F` |
| Telemetry producer | `0x0DA3` | `0x0CF2` | `0x0DBD` | `0x0DA6` |
| Telemetry sender | `0x0D8A` | `0x0783` | `0x0771` | `0x0771` |
| Application startup | `0x1800` | `0x1800` | `0x1800` | `0x1825` |
| State-family dispatcher | `0x191F` | `0x18DB` | `0x18D4` | `0x18F9` |

`*` The 2.06 UART ISR location is a close instruction-signature match and is therefore medium confidence; the other listed anchors are high confidence.

## Constant CR responses

| Read | 2.02 | 2.06 | 2.70 | 2.71 | Working interpretation |
| --- | ---: | ---: | ---: | ---: | --- |
| CR00 | `0x00` | `0x00` | `0x00` | `0x00` | Constant/status baseline |
| CR08 | `0x04` | `0x05` | `0x07` | `0x07` | Stove data format |
| CR0B | `0x02` | `0x02` | `0x02` | `0x02` | Firmware major byte |
| CR0C | `0x02` | `0x06` | `0x70` | `0x71` | Firmware minor/revision byte |
| CR0D | generic `0x00` | `0x00` | `0x00` | `0x00` | Reserved/unknown |
| CR0E | generic `0x00` | `0x21` | `0x02` | `0x00` | Read semantics changed; writes carry remote buttons |

## Comparison caveat

Compiled routines move between releases, so a word at the same numerical address is not necessarily the same logical function. `pairwise-summary.json` records exact same-address counts for reproducibility, but semantic conclusions above are based on instruction sequences, dispatch tables, literal checks, and surrounding control flow—not percentage similarity alone.

## Useful next work

- Live-qualify format-04 level changes and bound the startup UART-silent
  interval before enabling verified physical normal-control execution.
- Validate the decoded loader behavior on expendable hardware: `E5` write or
  readback failure, `E8` payload-checksum failure, four-word row preservation,
  the `0x1E80` protection boundary, retry limits, interruption, and recovery.
- Assign the remaining CR02.1 external-multiplexer slot and verify all muxed
  inputs against the installed `9067-0604` board.
- Resolve CR05/CR07 physical engineering units and the roles of AN1, AN2, and
  RE1 from their traced producers.
- Assign semantic names to every condition feeding the recovered state-family
  transition writes and decode the remaining alarm/flag bits.
- Resolve M/I service payloads and conditional/table-only telemetry paths.
