# Firmware analysis — Bixby 2.71 / 080315

## Preserved artifact

`firmware/original/Bixby_0271_080315.hex`

SHA-256:

`dc4dcf7aeb83c95525053018e010194c55498796b0b65c0ff26a11eb695e556b`

## Architecture

Microchip PIC16F877A.

## Important landmarks

- reset vector at `0x0000`
- interrupt vector at `0x0004`
- reset transfers to startup at program address `0x1825`
- interrupt handler checks UART RX (`RCIF`) and Timer2 sources
- serial parser confirms the `CR` / `CW` ASCII-hex protocol

## UART

Startup at `0x1825` configures `SPBRG=0x20`, `TXSTA=0x26`, `RCSTA=0x90`. At 20 MHz this corresponds closely to 38.4 kbaud, 8N1 async.

## Important disassembler caveat

`gpdasm` register-name annotations are not always bank-aware. Always inspect `STATUS.RP0/RP1` before trusting a displayed SFR name. A concrete example found during analysis: a banked write shown as `TXREG` is actually `SPBRG` when RP0 is set.

## Current highest-value findings

1. Serial command grammar is independently confirmed by firmware.
2. Read registers `CR02` and `CR06` expose physical-input-related bits.
3. A live differential-input test can likely identify the door/hopper states without a firmware patch.
