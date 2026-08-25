# Bare controller photographs: serial 5215

## Evidence identity

The stove owner supplied a second controller-board photograph set on
2026-08-22 after removing the board far enough to expose both sides, followed
by a photograph of the successful J3 connection. OpenMaxFire preserves eight
unique JPEG byte streams under
[`preservation/original/photos/serial-5215-bare-controller/`](../../preservation/original/photos/serial-5215-bare-controller/).

Two received `PXL` filename pairs were byte-identical duplicates. One copy of
each unique byte stream is retained under a descriptive name; the original
upload names and hashes are recorded in the preservation manifest.

| Preserved file | Dimensions | Directly useful view |
| --- | ---: | --- |
| [`component-side-full.jpg`](../../preservation/original/photos/serial-5215-bare-controller/component-side-full.jpg) | 1157 x 1536 | Full populated side; complete `9067-0604` marking, connectors, PIC, oscillator, and power/output sections |
| [`component-side-alternate.jpg`](../../preservation/original/photos/serial-5215-bare-controller/component-side-alternate.jpg) | 1157 x 1536 | Alternate full populated-side exposure and legible designators |
| [`solder-side-full.jpg`](../../preservation/original/photos/serial-5215-bare-controller/solder-side-full.jpg) | 1157 x 1536 | Full solder side and copper routing |
| [`j3-pic-component-side.jpg`](../../preservation/original/photos/serial-5215-bare-controller/j3-pic-component-side.jpg) | 1536 x 1157 | PIC16F877A, `10.000` oscillator, J3, and adjacent passive network |
| [`j3-component-side-closeup.jpg`](../../preservation/original/photos/serial-5215-bare-controller/j3-component-side-closeup.jpg) | 1157 x 1536 | J3, resistor/capacitor network, PIC, and nearby logic |
| [`pic-solder-side-routing.jpg`](../../preservation/original/photos/serial-5215-bare-controller/pic-solder-side-routing.jpg) | 1157 x 1536 | Solder-side PIC/J3-area routing |
| [`j3-ftdi-correct-wiring-solder-side.jpg`](../../preservation/original/photos/serial-5215-bare-controller/j3-ftdi-correct-wiring-solder-side.jpg) | 1542 x 2048 | **Authoritative correct/live-validated FTDI attachment:** orange J3-1, yellow J3-2, J3-3 unused, black J3-4 |
| [`j3-ftdi-incorrect-wiring-solder-side.jpg`](../../preservation/original/photos/serial-5215-bare-controller/j3-ftdi-incorrect-wiring-solder-side.jpg) | 1152 x 1536 | **Incorrect/reversed FTDI attachment retained as evidence; do not copy** |

The separately supplied `1000000393.jpg` completes the earlier installed-board
sequence and is retained with that set.

## Direct observations

- The complete silkscreen reads `PCB Part Number 9067-0604`, removing the
  earlier need to rely on an owner-reported prefix plus photographed suffix.
- U3 is visibly a `PIC16F877A-I/P` in a 40-pin DIP package.
- X1 is visibly marked `10.000`, physically confirming the 10 MHz frequency
  previously inferred from BixCheck baud settings and firmware divisors.
- The J3 square pad establishes pin 1; in the documented upright board view it
  is the bottom J3 pad, while the confirmed ground is the top round pad/pin 4.
- J3's two UART contacts enter passive networks before the PIC area rather than
  a visible MAX232, USB PHY, or RS-485 transceiver.
- Corrected owner continuity and wiring identification maps J3-1 toward PIC
  physical pin 26/RC7-RX, J3-2 toward pin 25/RC6-TX, and J3-4 to board ground.
- `j3-ftdi-correct-wiring-solder-side.jpg` is the authoritative positive
  reference: black on J3-4, J3-3 unused, yellow on J3-2, and orange on J3-1.
  Only those three conductors terminate on J3; the visible loose green conductor
  is not connected. This connection exchanged valid 9,600-baud application
  traffic.
- The older archived FTDI photograph shows black on J3-4, J3-3 unused, orange
  on J3-2, and yellow on J3-1. **That orange/yellow placement is reversed and
  must not be copied.**

Continuity measurements are owner-performed physical evidence rather than a
value derivable solely from pixels. The corrected live exchange independently
validates the functional TX/RX crossing.

## Supplied video

The owner also supplied `1000000401.mp4`, a 31.564-second, 1920x1080 HEVC/AAC
clip (78,737,900 bytes) with SHA-256
`185338b444ab517d1ded2ec43f37af73c68f1720acef4b209e6673e2fde64434`.
It is recorded here and in the preservation manifest but is not committed to
Git because of its size; it remains a candidate for the external preservation
archive.

## Limits

- J3-3 remains electrically unresolved and was not used for live communication.
- A successful 5 V TTL cable establishes compatibility for the tested board;
  it does not authorize attaching adapter VCC or applying the mapping to an
  unverified controller revision.
- The photographs do not replace safe unpowered continuity measurements.
- The board carries exposed mains circuitry during operation.
