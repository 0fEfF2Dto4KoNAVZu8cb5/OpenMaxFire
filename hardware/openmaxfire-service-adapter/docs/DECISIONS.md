# Portable service adapter decision record

Status: Rev A preparation decisions, 2026-09-01

## D-001 — build the service adapter before the permanent controller

**Decision:** prioritize the small portable adapter as the first hardware proof platform.

**Reason:** it isolates the two highest-value unknowns—target-safe J3 UART and in-circuit J5/PICkit operation—without combining them with permanent power, ESP32 firmware, thermostat transfer, expansion, or an appliance enclosure.

The full-controller work remains preserved as a reference. Successful adapter qualification should feed its J3/J5 service block rather than the adapter inheriting all full-controller features.

## D-002 — retain external FTDI and PICkit tools

**Decision:** Rev A contains neither an onboard USB-UART bridge nor an onboard PIC programmer.

**Reason:** the genuine FTDI cable has already communicated successfully, and the PICkit already implements USB, device support, target-voltage sensing, VPP generation, programming algorithms, and verification. Reimplementing either increases cost, board size, firmware scope, driver risk, and recovery risk.

The adapter is the electrical boundary and harness system between those tools and the stove controller.

## D-003 — two independent service modes

**Decision:** FTDI/J3 and PICkit/J5 are never simultaneous modes.

**Reason:** UART operation may use J5 VDD/VSS and a reset tap while communicating through J3, but ICSP requires direct MCLR/VPP, VDD, VSS, PGD, and PGC without UART loading or an active reset sink.

Operational and physical configuration must make the unused interface inactive. A single-USB composite tool is deferred.

## D-004 — physical jumpers instead of a multi-pole selector

**Decision:** use two three-pin shunt headers:

- JP201: `UART POWER 1-2 / ICSP PARK 2-3`;
- JP301: `RESET ARM 1-2 / PARK 2-3`.

**Reason:** jumpers are smaller, cheaper, visually inspectable, easy to continuity-test, and have a defined retained park position. JP201 physically removes the target UART load from PICkit VDD. JP301 physically removes the automatic reset transistor from MCLR/VPP.

A future enclosure may replace one or both with equivalent keyed switches, but only if the electrical states remain fail-open.

## D-005 — remove the active target load switch

**Decision:** the portable adapter uses a physical power jumper and resettable fuse rather than the full controller's TPS22948 load switch and isolated enable circuitry.

**Reason:** the service adapter is attended and mode-selected by the technician. A physical open provides clearer ICSP separation, eliminates one active device, reduces board area/cost, and prevents PICkit VDD from powering the UART secondary.

The tradeoff is that the adapter relies on correct jumper procedure. Labels, shunt retention, and pre-use inspection are therefore required.

## D-006 — target-powered UART secondary

**Decision:** U101 side 2, U102, and U103 are powered from main-board J5 VDD through F201 and JP201 only in UART mode.

**Reason:** target-derived power disappears with the target and does not create an always-powered isolated secondary that can inject into an unpowered PIC input. It also provides the correct 5 V target logic reference.

J3 pin 3 remains disconnected even though it appears related to PIC VDD. Its live voltage and source behavior are not sufficiently qualified.

## D-007 — wide-body default-high digital isolator

**Decision:** baseline UART isolation is `ISO7721DWVR`.

**Reason:** it provides one channel in each direction, supports 5 V supplies, and the non-`F` device defaults high, matching UART idle. The wide-body package supports a clear physical isolation corridor.

A narrower or lower-cost isolator may be evaluated later, but not by weakening the established domain separation or default behavior.

## D-008 — separate target tri-state buffer and supervisor

**Decision:** place `SN74LVC2G126DCUR` between the isolator and J3, with both output enables controlled by `TLV803EA42RDBZR`.

**Reason:** galvanic isolation alone does not guarantee that the stove-facing conductor is benign during target power loss or brownout. The selected buffer has powered-off protection, and the supervisor delays connection until the target auxiliary rail is valid.

The two parts cost more than connecting the isolator directly, but this is the minimum retained target-off protection considered acceptable for a repeatable service tool.

## D-009 — optional reset is isolated and pull-down only

**Decision:** FTDI RTS# drives a `VOL618A-3X001T` LED on the host side; its target phototransistor may pull MCLR low only through R302 and JP301.

**Reason:** a deterministic hardware reset is needed to replace unreliable AC-cycle/manual-BREAK loader entry, but FTDI and target grounds must remain isolated. An open-collector sink cannot source VPP.

Because FTDI drivers may toggle RTS# during plug/open/close/reset, the MCLR connection is normally physically parked.

## D-010 — direct ICSP with no inline protection

**Decision:** PICkit pins 1-5 connect directly to J5 pins 1-5; pin 6 is NC.

**Reason:** MCLR must accept programming voltage, PGD is bidirectional, PGC requires clean edges, and PICkit pin 2 must sense target VDD. Ordinary protection components, LEDs, switches, or filters can break programming.

Safety is supplied by offline procedure, positive connector identification, physical UART/reset parking, one target power source, short harnesses, and staged read-only qualification—not by altering the ICSP waveforms.

## D-011 — no target power supply in the adapter

**Decision:** Rev A has no external target-power input, isolated converter, regulator, or battery.

**Reason:** adding target power creates source-conflict, reverse-current, current-limit, voltage-selection, connector, and user-error problems. The adapter shall first measure whether PICkit power can support the populated controller. If not, a separately qualified current-limited low-voltage supply must power the controller through its proper input while PICkit output is disabled.

A future power accessory must be a separate reviewed design, not an undocumented wire into J5 VDD.

## D-012 — adapter-side JST XH; stove-end connectors remain unknown

**Decision:** use 4-, 5-, and 6-position JST XH side-entry headers on the adapter side.

**Reason:** they are low-cost, polarized, visually distinct by contact count, and easy to obtain. The 4/5/6 split prevents adapter-side cross-mating.

This does not identify the stove-side connector family. Exact stove-end housings and contacts remain release blockers.

## D-013 — omit required LEDs

**Decision:** no status LED is required or populated in the baseline.

**Reason:** LEDs add current, especially to the target rail, while conveying less trustworthy information than measured test points and software state. DNP footprints may be reserved for development.

## D-014 — two-layer compact PCB

**Decision:** target a two-layer board no larger than 60 mm x 40 mm, with 65 mm x 45 mm as a hard first-revision ceiling.

**Reason:** the circuit is small enough for two layers when partitioned carefully. Two layers reduce cost and make isolation, direct ICSP routing, and visual inspection easier. The isolation corridor and edge connectors are allowed to determine size; artificial miniaturization shall not reduce clearance or serviceability.

## D-015 — engineering labels are part of the safety design

**Decision:** connector identity, board revision, pin 1, jumper states, and the distinction between main-board and igniter-board J5 are mandatory controlled artifacts.

**Reason:** the largest credible hazard is not component failure; it is attaching a valid cable to the wrong similarly named connector or using the correct connector in the wrong mode. A board that is electrically correct but ambiguously labeled is not complete.

## D-016 — read-only J5 qualification precedes all writing

**Decision:** require device identification and three complete matching reads through the assembled adapter before considering any erase or program test.

**Reason:** the project has bare-chip evidence but no qualified in-circuit J5 result. Repeated reads prove orientation, target power, VPP entry, PGC/PGD integrity, and stable memory access without immediately risking the target contents.

## Deferred alternatives

The following may be reconsidered only after Rev A evidence exists:

- onboard FTDI/CP210x USB-UART;
- single-USB composite UART/programmer;
- isolated DC/DC target-side power;
- active electronic mode switching;
- J3 pin 3 as target auxiliary power;
- onboard target power injection;
- automatic reset permanently connected to MCLR;
- LEDs, display, buttons, or logging;
- smaller/narrow-body isolation packages; and
- combined permanent-controller/service-adapter PCB.
