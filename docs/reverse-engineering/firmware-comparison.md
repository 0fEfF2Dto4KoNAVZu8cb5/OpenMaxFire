# Firmware 2.06 / 2.70 / 2.71 comparison

This report compares the three preserved generations at PIC16F877A word level. Raw tables live in `reverse-engineering/firmware/comparison/`.

## Major findings

1. The `CRXX` / `CWXXYY` ASCII command skeleton exists in all three generations. The nibble decoder, byte parser, CR dispatcher, and ASCII response formatter can be followed across relocated code.
2. Firmware identity is exposed through reads: CR0B returns the major byte `0x02`; CR0C returns `0x06`, `0x70`, or `0x71` by generation.
3. CR08 changes from `0x05` in 2.06 to `0x07` in 2.70 and 2.71. All three
   BixCheck Individualization tables identify C08 as `Stove data format`.
4. UART setup changes at the 2.06-to-2.70 boundary: `SPBRG` is `0x40` in 2.06 and `0x20` in 2.70/2.71. `TXSTA=0x26` and `RCSTA=0x90` remain stable.
5. BixCheck 5.0.21 selects exactly 9,600 baud and 5.5.x selects 9,600 or 19,200.
   Paired with the firmware divisors, this strongly implies a 10 MHz controller
   oscillator and intended rates of 9,600 for 2.06 and 19,200 for 2.70/2.71.
   The physical oscillator must still be measured.
6. The 2.06 PICkit image is a superset-style complete programming image: it redirects reset to a serial bootloader/service region and includes 256 EEPROM defaults. The 2.06 Downloader image is the main application payload.
7. The experimental PIC emulator executes every CR00-CR0E receive, dispatch,
   handler, and formatter path: all 45 complete without error. Its formatter
   emits lowercase A-F nibbles in responses.
8. Bank-aware dynamic dependencies are structurally stable across releases.
   GPIO/ADC differentials identify RD1 as door, RD4 as ash drawer, RB4 as
   thermostat, AN3 as fan pot, and AN4 as feed pot after cross-referencing
   BixCheck Checkout masks.
9. A-unit reads use the PIC16F877A internal data EEPROM. All 768 AR00-ARFF
   cross-version probes match checksum-valid synthetic format-05/07 fixtures.
10. All three generations contain the same input-multiplexer design. RD2 and
    RD6:RD5 scan the active-low front-panel buttons into CR01; RD7 and RD6:RD5
    scan three active-high RD3 external inputs into CR02.0-2.
11. Static configuration-bank selection fixes CR02.2 as the fuel selector:
    `1`=Fuel A/corn and `0`=Fuel B/wood. BixCheck and the related-board diagram
    corroborate the name; CR02.0 is the burn-drive limit switch and CR02.1
    remains unassigned.

## Protocol-anchor matrix

| Function | 2.06 | 2.70 | 2.71 |
| --- | ---: | ---: | ---: |
| UART RX interrupt | `0x00C6`* | `0x00AE` | `0x00AE` |
| Receive-buffer byte | `0x0E71` | `0x0F63` | `0x0F2E` |
| ASCII-hex nibble | `0x0EA4` | `0x0F95` | `0x0F60` |
| ASCII-hex byte | `0x0EC0` | `0x0FB1` | `0x0F7C` |
| Check command `C` | `0x1008` | `0x1112` | `0x10E8` |
| Check command `W` | `0x1014` | `0x111E` | `0x10F4` |
| Check command `R` | `0x113F` | `0x1234` | `0x120E` |
| CR00-CR0E table | `0x12A7` | `0x1391` | `0x136E` |
| Response formatter | `0x1265` | `0x1352` | `0x132F` |
| Application startup | `0x1800` | `0x1800` | `0x1825` |

`*` The 2.06 UART ISR location is a close instruction-signature match and is therefore medium confidence; the other listed anchors are high confidence.

## Constant CR responses

| Read | 2.06 | 2.70 | 2.71 | Working interpretation |
| --- | ---: | ---: | ---: | --- |
| CR00 | `0x00` | `0x00` | `0x00` | Constant/status baseline |
| CR08 | `0x05` | `0x07` | `0x07` | Stove data format |
| CR0B | `0x02` | `0x02` | `0x02` | Firmware major byte |
| CR0C | `0x06` | `0x70` | `0x71` | Firmware minor/revision byte |
| CR0D | `0x00` | `0x00` | `0x00` | Reserved/unknown |
| CR0E | `0x21` | `0x02` | `0x00` | Read semantics changed; writes carry remote buttons in 2.71 BixCheck |

## Comparison caveat

Compiled routines move between releases, so a word at the same numerical address is not necessarily the same logical function. `pairwise-summary.json` records exact same-address counts for reproducibility, but semantic conclusions above are based on instruction sequences, dispatch tables, literal checks, and surrounding control flow—not percentage similarity alone.

## Useful next work

- Resolve remaining erase/program acknowledgement semantics in the PICkit-only
  bootloader region; `EA`/`EB`, block framing, and completion are mapped.
- Assign the remaining CR02.1 external-multiplexer slot and verify all muxed
  inputs against the installed `9067-0604` board.
- Continue assigning CR04-CR07 engineering semantics from their traced RAM
  producers, not just their read handlers.
- Match write-register handler paths across all versions before considering any live write.
