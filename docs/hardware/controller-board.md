# Controller board notes

## Confirmed MCU

Firmware metadata/layout and disassembly identify the stove controller as a **Microchip PIC16F877A**.

## Startup I/O observations

Static analysis of the TRIS configuration shows the following pins configured as inputs during startup:

- RA0..RA5
- RB0, RB4, RB6, RB7
- RD0, RD1, RD3, RD4
- RE0, RE1

RB1 and RB5 are configured as outputs even though their states are packed into a readable status byte.

These observations are firmware-level facts; they do not yet identify every physical sensor/switch connected to each pin.
