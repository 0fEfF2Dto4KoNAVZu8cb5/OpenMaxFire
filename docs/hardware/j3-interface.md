# J3 serial interface

## Current understanding

BixCheck documentation describes a custom Bixby cable, P/N 2013324, used between the stove and a PC. It states that standard PC serial ports and USB-to-RS-232 converters work on the PC side of that custom cable.

Firmware analysis confirms that the PIC hardware UART is used internally. The original custom cable therefore should not be assumed to be a passive DB9 adapter.

For OpenMaxFire development, the planned interface is a **5 V TTL USB-UART adapter** connected to the J3-side UART, with a Molex-SL-compatible 4-pin connector.

## Initial hookup policy

Until J3 is measured/verified on the actual board:

- Identify J3 ground first.
- Identify stove TX and RX before connection.
- Connect UART ground, TX, and RX only.
- **Do not connect USB-UART VCC/+5 V to J3.**
- Cross TX/RX: adapter TX -> stove RX, adapter RX -> stove TX.

## Expected serial configuration

Firmware startup writes:

- `SPBRG = 0x20`
- `TXSTA = 0x26`
- `RCSTA = 0x90`

With a 20 MHz oscillator, this is approximately **38400 baud, 8N1, asynchronous**. Oscillator frequency still needs hardware confirmation, so 38400 should be treated as strongly supported rather than physically measured.
