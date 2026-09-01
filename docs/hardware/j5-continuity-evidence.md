# 9067-0604 main-board J5 continuity evidence

Status: **documented engineering evidence; requires repeat measurement before release**

Snapshot: 2026-09-01

## Purpose

This document records the physical continuity investigation of the five-contact
J5 connector on the Bixby MaxFire `9067-0604` main controller board.

The purpose of this record is to separate two different questions:

1. **What does J5 connect to?**
2. **Can an ICSP programmer safely and reliably operate through J5 on a populated controller?**

The first question has been investigated through continuity tracing. The second
question remains a separate electrical qualification task.

## Board identity boundary

This mapping applies only to:

- Bixby MaxFire main controller PCB `9067-0604`;
- controller containing the 40-pin `PIC16F877A-I/P` MCU;
- the small five-contact J5 connector located near the PIC and red indicator LED.

This is **not** the auxiliary igniter-board connector that also uses the
reference designator J5 in related documentation.

## Physical pin mapping

Pin 1 is identified by the square PCB pad.

| J5 pin | Function | PIC16F877A destination |
|---|---|---|
| 1 | MCLR / VPP | PIC pin 1 (MCLR/VPP) |
| 2 | VDD / target voltage | PIC VDD pins 11 and 32 |
| 3 | VSS / ground | PIC VSS pins 12 and 31 |
| 4 | ICSPDAT / PGD | PIC RB7 / pin 40 |
| 5 | ICSPCLK / PGC | PIC RB6 / pin 39 |

## Evidence basis

The mapping was established by:

- tracing J5 pads from the physical controller board;
- comparing traced endpoints against the PIC16F877A ICSP pin assignments;
- correlating the discovered connections with the project's PICkit preservation work.

The mapping is considered strong evidence for the photographed `9067-0604`
controller, but should be repeated and photographed as an independent validation
step before a released service cable is used.

## PICkit correspondence

A standard PICkit ICSP header maps as follows:

| PICkit pin | Signal | J5 pin |
|---|---|---|
| 1 | MCLR/VPP | 1 |
| 2 | VDD/VDD sense | 2 |
| 3 | VSS | 3 |
| 4 | PGD/ICSPDAT | 4 |
| 5 | PGC/ICSPCLK | 5 |
| 6 | AUX/PGM | No connection |

PICkit pin 6 must remain unconnected.

## Important distinction

The continuity map proves the signal destinations. It does **not** prove:

- PICkit-powered operation of the complete controller board;
- safe in-circuit programming through J5;
- target current requirements;
- VPP margin through a harness;
- PGD/PGC signal integrity;
- compatibility with other Bixby controller revisions.

Those require separate testing.

## Remaining validation

Before J5 is considered qualified for the OpenMaxFire service adapter:

- repeat the continuity mapping independently;
- photograph both connector sides and pin 1 orientation;
- verify the exact connector family and harness orientation;
- measure J5 VDD behavior on the powered controller;
- perform read-only PICkit identification and repeated reads through J5 on expendable hardware.

No write, erase, or recovery operation should be considered validated until the
read-only path has been proven first.
