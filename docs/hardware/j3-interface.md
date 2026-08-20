# J3 hardware interface

## Vendor evidence

The BixCheck manual calls for custom Bixby PC cable P/N 2013324. The 2.06 release notes identify J3 as a black four-pin connector behind the exhaust-fan/feed-rate trim-control tab. Standard PC serial ports or USB-to-RS-232 converters connect on the PC side of the custom cable.

The custom cable should not be assumed to be passive, and the J3 side should not be assumed to use standard RS-232 voltages.

The preserved [MaxFire motherboard diagram](maxfire-motherboard-pinout.md)
independently labels J3 as `Computer Port` and places it along the upper-left
edge of a `9067-0404` motherboard. It does not label the four cavities or any
voltage level. Serial 5215's board is owner-reported as `9067-0604`, so even the
illustrated physical placement remains revision-family evidence rather than an
exact pinout.

## Earlier project hardware proposal

Prior research proposed a 5 V TTL USB-UART adapter and a Molex-SL-compatible four-pin connector for the J3 side. This was a procurement/interface hypothesis, not a measured pinout. The ordered cable/connector hardware had not arrived by 2026-08-20.

Until measurement proves that proposal:

- identify ground first;
- identify stove TX and RX from protected measurements;
- do not connect adapter VCC/+5 V to J3;
- do not assume wire colors or connector position;
- cross TX/RX only after polarity and voltage compatibility are known;
- prefer isolation and current limiting.

The firmware-derived baud candidates and first live-test order are documented in [the J3 protocol specification](../protocol/j3-protocol.md).
