# 9067-0604 main-board J5 ICSP interface

Status: **provisional, board-specific mapping; not released for in-circuit
programmer use**.

This page records what OpenMaxFire currently knows about the five-contact J5
on the Bixby `9067-0604` main controller. It is an interface reference for the
controller and future service hardware, not permission to read, erase, or
program a controller through J5.

> **The main-board J5 described here is not the igniter-board J5.** A related
> appliance diagram uses `J5` for a 120 V AC left-igniter connection on a
> separate board. A reference designator has meaning only on its own PCB.

See the [J5 service-safety guide](../guides/j5-service-safety.md) before using
this information around physical hardware.

## Scope and naming

Use the complete name **9067-0604 main-board J5 ICSP** in drawings, labels,
test records, and conversation. Do not shorten it to “J5” where it could be
confused with another PCB.

This mapping applies only to the photographed controller from stove serial
5215:

- the large main control PCB is marked `PCB Part Number 9067-0604`;
- U3 is a 40-pin `PIC16F877A-I/P`;
- the main-board J5 is a small white five-contact connector on that same PCB,
  near U3 and the red indicator LED; and
- pin 1 is identified by the square PCB pad.

The [bare-controller photograph record](bare-controller-photographs.md)
documents the exact board, both PCB sides, the part number, and the PIC. Never
infer pin order from “left,” “right,” “top,” or “bottom”: board orientation can
change, and a solder-side view is mirrored.

## Current main-board mapping

The mapping below comes from owner-performed tracing and continuity work on the
exact `9067-0604` controller. It agrees with the PIC16F877A programming pins
documented in the project's
[PICkit preservation guide](../guides/pickit3-firmware-preservation.md).

It remains **strong provisional evidence**, rather than a released field
pinout, until a second independent continuity pass and its photographs and
measurements are archived.

| Main-board J5 | Reported function | PIC16F877A programming endpoint |
| ---: | --- | --- |
| 1, square pad | MCLR/VPP | U3 pin 1, MCLR/VPP |
| 2 | VDD / target-voltage sense | U3 VDD rail, pins 11 and 32 |
| 3 | VSS / target ground | U3 VSS rail, pins 12 and 31 |
| 4 | PGD / ICSPDAT | U3 pin 40, RB7/PGD |
| 5 | PGC / ICSPCLK | U3 pin 39, RB6/PGC |

Signal meanings matter:

- `MCLR/VPP` is both reset and the programming-voltage input. It is not an
  ordinary 5 V GPIO.
- `VDD` on a PICkit cable is also the programmer's target-voltage sense line.
  Depending on programmer configuration, that pin may sense a separately
  powered target or source target power. This project has not qualified either
  mode through the installed controller.
- `VSS` is the target reference. The appliance-side reference has not been
  established as SELV by a documented circuit and fault-condition review.
- `PGD` and `PGC` are the in-circuit programming data and clock lines.

## PICkit six-pin correspondence

A conventional PICkit ICSP header has six positions. A future OpenMaxFire
controller or service adapter must preserve this order and must not invent a
sixth connection at the stove board:

| PICkit pin | PICkit signal | 9067-0604 main-board J5 |
| ---: | --- | ---: |
| 1 | VPP/MCLR | 1 |
| 2 | VDD target / VTGT sense | 2 |
| 3 | VSS / target ground | 3 |
| 4 | PGD/ICSPDAT | 4 |
| 5 | PGC/ICSPCLK | 5 |
| 6 | AUX/PGM | No connection |

PICkit pin 6 has no corresponding contact on main-board J5. It must remain no
connect in the OpenMaxFire pass-through. The programmer's pin-1 triangle, the
adapter's pin-1 mark, and the main board's square pad are three separate
orientation references; all three must agree.

This table defines correspondence only. It does not approve a cable, a target
power arrangement, or a programmer operation.

## Why the other J5 is hazardous

The preserved related-family
[MaxFire mother-board pinout diagram](../../preservation/original/diagrams/maxfire-mother-board-pinout.jpg)
shows two separate PCBs. On its auxiliary power/igniter board, the connector
labeled `J5 Left Igniter` is colored as a **120 V AC** circuit. The diagram's
authorship is unverified and its photographed main board is revision
`9067-0404`, not the serial-5215 `9067-0604`; those provenance limits are
recorded beside the [preserved diagram](../../preservation/original/diagrams/README.md).

Those limits do not make the warning less important. They show that the same
designator is reused for unrelated functions within this appliance family:

| Identity | Board | Contacts/function | Treatment |
| --- | --- | --- | --- |
| **Main-board J5 ICSP** | Large `9067-0604` controller with PIC16F877A | Five low-voltage programming signals | Provisional mapping; offline validation only |
| **Auxiliary igniter J5** | Separate igniter/power board | Left igniter, shown as 120 V AC | Hazardous mains connection; never attach service electronics |

Never identify a connector from `J5` silkscreen alone. A USB cable, PICkit,
logic analyzer, ESP board, or OpenMaxFire product connected to the wrong J5
could expose the user and connected computer equipment to mains voltage.

## Positive identification

Positive identification requires all of the following, with the appliance
unplugged and the controller removed from every power and actuator connection:

1. Read the complete `PCB Part Number 9067-0604` marking on the same PCB.
2. Confirm the same PCB carries U3, the 40-pin PIC16F877A.
3. Locate the five-contact connector marked J5 on that main PCB near U3 and
   the red indicator LED.
4. Establish pin 1 from its square copper pad, not from a photograph or wire
   color.
5. On first use of each controller and cable, have a qualified person repeat
   and record unpowered continuity to MCLR, VDD, VSS, RB7, and RB6.

Stop if the board marking is missing or different, if the contact count or
location differs, if the connector is on the auxiliary board, or if any
continuity result disagrees. Similar appearance is not evidence of
compatibility.

## OpenMaxFire hardware requirements

Any OpenMaxFire controller that exposes this interface must meet these design
requirements before it can claim full J5 capability:

- use a short, direct one-to-one path for MCLR/VPP, VTGT sense, VSS, PGD, and
  PGC;
- leave PICkit AUX/PGM disconnected;
- mark pin 1 at both ends and use a keyed, labeled pigtail that cannot mate
  with the J3 UART tail or an igniter connector;
- add no indicator LED, ordinary clamp, RC filter, or unqualified series
  impedance to MCLR/VPP, PGD, or PGC;
- physically disconnect the ESP32, J3 UART drivers, and automated reset sink
  from the target while in ICSP mode;
- prevent recovery power in every non-ICSP mode and prevent competing target
  power sources;
- retain PICkit pin 2 for target-voltage sensing even when a separately
  qualified target supply is used;
- require a deliberate physical service-mode selection; firmware alone must
  not be able to enter ICSP mode or apply target power; and
- label the enclosure and target cable `9067-0604 MAIN-BOARD J5 ICSP — NOT
  IGNITER J5`.

These are requirements, not claims that the new controller has passed them.

## Known limitations

As of 2026-08-31, the evidence does **not** establish any of the following:

- compatibility with a controller revision other than the tested
  `9067-0604`;
- a second independently witnessed and photographed J5 continuity map;
- the exact mating-housing manufacturer, series, pitch, key, or crimp part;
- safe programmer-supplied target power or safe external recovery power for a
  populated controller;
- controller inrush, steady current, or backfeed behavior through J5;
- VPP margin or PGD/PGC waveform integrity through a finished cable and
  OpenMaxFire board;
- successful PICkit identification or a repeatable whole-device read through
  main-board J5;
- safe hot-plugging, installed-appliance use, or operation with any mains or
  actuator harness attached; or
- safety classification of the target reference, finished isolation system,
  cable, or enclosure.

The project's recorded PICkit recovery used a PIC removed from the controller
and a verified socket adapter. It is not evidence that in-circuit use through
main-board J5 works or is safe.

## Validation gates

The mapping may be promoted from provisional only when all applicable records
below are dated, reviewed, and archived:

1. **Identity gate:** clear photographs show the complete board number, U3,
   J5, square-pad pin 1, both connector faces, and both PCB sides.
2. **Independent mapping gate:** a second operator records unpowered
   point-to-point continuity for all five contacts and adjacent-pin isolation;
   the result must agree exactly with the table above.
3. **Cable gate:** the exact mating family is identified; every serialized
   cable passes end-to-end resistance, adjacent-short, orientation,
   strain-relief, and mis-mating inspection.
4. **Safety gate:** a qualified review covers target-reference classification,
   isolation, enclosure, touch protection, power-source conflicts, and all
   credible misconnection cases.
5. **Expendable-target electrical gate:** with a spare controller removed from
   the appliance and every mains/actuator harness absent, record target inrush,
   steady current, reverse current, MCLR/VPP levels, PGD/PGC waveforms, target
   sensing, and power-removal behavior under a separately reviewed test plan.
6. **Read-only ICSP gate:** correct device identification and repeatable,
   independently compared whole-device reads succeed before any write is even
   considered.
7. **Product interlock gate:** verify by fault injection that ESP32 reset,
   firmware crash, power loss, switch transitions, and cable insertion cannot
   assert MCLR, drive PGD/PGC, enable recovery power, or energize an appliance
   load in ICSP mode.
8. **Write qualification gate:** any future write testing requires a separate,
   explicit procedure, expendable hardware, authenticated images, independent
   whole-chip readback, interruption testing, and project approval. This page
   does not provide that authorization.

Until those gates pass, public use is limited to non-energized identification,
documentation, and qualified continuity verification. The repository's
[safety policy](../../SAFETY.md) and all firmware safety locks remain in force.
