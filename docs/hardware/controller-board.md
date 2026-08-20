# Controller-board notes

## Confirmed from firmware

Firmware metadata and valid code disassembly identify the controller as a Microchip PIC16F877A.

Startup TRIS configuration makes these pins inputs:

- RA0-RA5
- RB0, RB4, RB6, and RB7
- RD0, RD1, RD3, and RD4
- RE0 and RE1

RB1 and RB5 are outputs even though CR03 reports their states.

These are firmware-level facts, not a complete physical schematic. Every pin-to-sensor assignment remains provisional until traced or correlated on the board.

## Owner inventory

The installed main PCB is reported as part/silkscreen 9067-0604, manufactured December 2005, with an internal assembly mark of `12/15`. Board photographs and oscillator markings are still needed.
