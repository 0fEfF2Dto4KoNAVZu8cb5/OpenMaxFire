# Firmware 2.02 original-controller read

`Bixby_0202_260827_PICkit.hex` is the first complete PICkit read supplied from
the original PIC16F877A removed from serial 5215's `9067-0604` controller. The
owner supplied the file to OpenMaxFire on 2026-08-28; the received filename is
retained unchanged. The HEX file itself is preserved byte-for-byte and must
never be edited in place.

## Identity and integrity

| Property | Value |
| --- | --- |
| Bytes | 46,536 |
| SHA-256 | `272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab` |
| Target | PIC16F877A |
| Program memory | 8,192 words, complete `0x0000`-`0x1FFF` |
| Data EEPROM | 256 bytes, complete |
| User IDs | four words, all `0x3FFF` |
| Configuration word | `0x3F32` |
| Device ID | absent from this export |
| Program code protection | disabled |
| Data EEPROM code protection | disabled |

Every Intel HEX record checksum and the EOF record validate. The normalized
EEPROM content is byte-identical to the independent A00-AFF J3 backup captured
from the same controller on 2026-08-22, when it identified itself as firmware
2.02/data format 04. The complete protected loader range `0x1E80`-`0x1FFF` is
also word-for-word identical to the preserved 2.06 PICkit image. These are
strong provenance checks, but they do not replace repeat programmer reads.

## Authentication status

This is one complete, internally valid read. The owner reports that its hash
was checked. Additional independently saved exports and programmer logs remain
pending. When supplied, they should be added as separate immutable originals
and compared with `openmaxfire firmware-preserve compare-reads` before the
image is described as repeat-read authenticated.

The original PIC remains preservation media: never erase or program it. Clone
work must use a spare PIC, followed by a fresh readback comparison and a
controlled board-boot test.
