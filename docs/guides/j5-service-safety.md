# J5 service safety

Status: **conservative identification guide; main-board J5 ICSP use is not yet
released**.

This guide helps owners and technicians avoid confusing two unrelated
connectors named J5. It deliberately contains no erase, program, recovery,
target-power, fuse-setting, or safety-lock-bypass procedure.

## The one fact to remember

“J5” is only a reference designator local to one circuit board.

- The **9067-0604 main-board J5** is a five-contact, provisionally mapped PIC
  programming connection on the large controller board.
- The **auxiliary igniter-board J5** is shown in a preserved related-family
  diagram as the **120 V AC left-igniter connection**.

Connecting service electronics to the wrong one can place mains voltage on a
PICkit, USB adapter, ESP board, computer, or person. Do not proceed from the
letters `J5` alone.

## Owner boundary

Owners do not need J5 for normal operation, cleaning, routine maintenance,
fault-code review, or J3 serial monitoring. If the task does not specifically
require PIC firmware preservation or qualified recovery, leave J5 alone.

Before any appliance service, follow the factory manual: shut the stove down,
disconnect mains power, allow it to cool completely, and do not operate it with
the side panel removed. The project [safety policy](../../SAFETY.md) summarizes
additional non-negotiable boundaries.

If you cannot positively distinguish the main controller from the auxiliary
power/igniter board, stop and use a qualified appliance technician. A photo in
a forum post, connector color, or wire color is not sufficient identification.

## Current technician boundary

At the present evidence level, work at main-board J5 is limited to:

- visual identification and photography on a completely unpowered appliance;
- removal and labeling of the controller under the applicable factory service
  procedure; and
- unpowered continuity verification by a qualified person after the
  controller is removed and every harness and external source is disconnected.

Do not attach a programmer to the installed stove. Do not energize either J5.
Do not use the provisional pinout to perform a firmware operation. The
[technical interface reference](../hardware/j5-icsp-interface.md) lists the
evidence still required before use can be released.

## Safe identification checklist

With mains unplugged, the appliance cool, and no board energized:

1. Identify the **large main controller PCB**, not the separate auxiliary
   igniter/power board.
2. Read the full main-board marking: `PCB Part Number 9067-0604`.
3. Confirm that the same PCB carries the large 40-pin `PIC16F877A-I/P` at U3.
4. Locate the small white five-contact J5 on that PCB near U3 and the red
   indicator LED.
5. Identify pin 1 only by the square PCB pad. Do not infer it from viewing
   direction; the solder side is mirrored.
6. Confirm that the cable label names the board and function in full:
   `9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5`.

Every item must agree. If the PCB revision, PIC, contact count, location, or
pin-1 evidence differs, treat the connector as unknown and stop.

The auxiliary igniter-board J5 can be recognized by the fact that it is on a
different PCB associated with igniter power wiring and fuses. That description
is a warning sign, not a field pinout: do not probe or attach test equipment to
it merely to confirm its voltage.

## Actions that remain prohibited

Until the project publishes a dated release record for this interface:

- no PICkit connection through main-board J5;
- no Program, Erase, Blank Check, “preserve memory,” or firmware-file load
  with the controller attached;
- no programmer-supplied target power and no external recovery supply;
- no simultaneous connection to appliance mains, actuator harnesses, J3,
  USB/FTDI, ESP32, or another target supply;
- no improvised Dupont leads, loose clips, reversed ribbon cables, or cables
  built from wire color alone;
- no assumption that another Bixby model or PCB revision shares this mapping;
- no in-place experiment on the only working controller; and
- no attempt to bypass OpenMaxFire's physical interlocks or software safety
  locks.

A successful bare-chip PICkit operation does not waive these restrictions.
The serial-5215 recovery was performed with the PIC removed and placed in a
verified socket adapter, not through main-board J5.

## If firmware preservation is the goal

Stop before connecting anything and review the
[PICkit read-only preservation boundary](pickit3-firmware-preservation.md).
That procedure currently describes a removed PIC in a verified socket. It does
not authorize substituting the provisional in-circuit J5 path.

For any untouched original, the first programmer session is read/export only.
If code protection is reported or uncertain, stop: clearing protection is
destructive. This J5 guide does not authorize firmware writing or emergency
recovery.

## What a qualified J5 release must contain

Do not rely on a future cable or controller merely because it fits. Look for a
release record that includes all of the following:

- dated independent continuity evidence for the exact 9067-0604 mapping;
- connector and crimp part numbers, pin-1 photographs, and serialized cable
  test results;
- read-only PICkit identification/read evidence on expendable, de-harnessed
  hardware;
- measured target current, backfeed, VPP, and PGD/PGC signal integrity;
- proof that J3, ESP32, automated reset, and recovery power are physically
  isolated or disabled in ICSP mode;
- enclosure, labeling, strain-relief, and electrical-safety review; and
- explicit supported controller revisions and operating limits.

Absence of a known failure is not a release. Until the record exists, regard
the interface as engineering evidence only.

## Stop conditions and incident record

Stop immediately if any identity is uncertain, continuity disagrees, a target
rail is unexpectedly present, the programmer reports an unexpected device or
protection state, any component warms, an actuator moves, or there is odor,
noise, discoloration, or visible damage.

Disconnect power without changing more of the setup than safety requires.
Record the controller part number and serial, connector and cable photographs,
pin-1 orientation, every attached source, instrument, switch position, and the
exact message or measurement. Preserve that evidence before attempting a
different setup.
