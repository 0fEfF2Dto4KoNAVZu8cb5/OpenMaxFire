# OpenMaxFire portable service adapter

Status: **PCB-design input package; not fabrication-ready or approved for use on a stove**

Snapshot: 2026-09-01

The OpenMaxFire portable service adapter is a small, low-cost technician interface for the Bixby MaxFire main controller. It combines two independent service paths in one inline adapter:

- isolated 5 V TTL UART access to the main-board J3 computer port using the existing FTDI `TTL-232R-5V-WE`; and
- a short, direct PICkit ICSP pass-through to the five-contact J5 on the `9067-0604` main controller.

The external FTDI cable remains the USB-to-UART device. The external PICkit remains the programmer. The adapter does not recreate either tool. Rev A is intentionally specified for only one service path at a time, using physical UART-power and reset-arm jumpers plus a mandatory cable-disconnection procedure rather than an expensive multi-pole interlock.

> [!DANGER]
> A separate connector also called **J5** exists on the auxiliary igniter board and is associated with 120 VAC in the preserved factory-family drawing. This adapter is intended only for the five-contact **`9067-0604 MAIN-BOARD J5 ICSP`** beside the PIC16F877A. The PCB number, controller identity, contact count, pin 1, and continuity map must all be verified before connection.

## Why this product comes first

The full OpenMaxFire controller remains a useful reference design, but it combines permanent power, an ESP32, thermostat transfer, safety logic, expansion, and two service interfaces. This adapter isolates the two service problems that must work first:

1. reliable, target-safe J3 serial communication; and
2. repeatable PICkit identification, reading, backup, and recovery through main-board J5.

Successful qualification of this adapter will provide reusable evidence and a proven service circuit for a later permanent controller.

## Deliberately small architecture

```text
 FTDI TTL-232R-5V-WE                         PICkit 3/4/5
 black/red/orange/yellow/green                    pins 1-6
            |                                        |
       HOST DOMAIN                              TARGET DOMAIN
            |                                        |
       resettable fuse                               +-- direct MCLR/VPP
            |                                        +-- direct VDD sense/source
     ISO7721 1-forward/1-reverse                     +-- direct VSS
       digital isolator                              +-- direct PGD
            ||                                       +-- direct PGC
            || 8 mm no-copper barrier                +-- pin 6 NC
            ||                                        |
      target-side buffer <--- physically selected J5 VDD
            |                                        |
         J3 TX/RX                                  main-board J5

 FTDI RTS# -> VOL618A isolated open-collector reset -> guarded MCLR arm
```

The preliminary circuit uses only four active devices:

- `ISO7721DWVR` reinforced, default-high bidirectional UART isolator;
- `SN74LVC2G126DCUR` dual tri-state target buffer with powered-off protection;
- `TLV803EA42RDBZR` 4.2 V, delayed, open-drain target power-good supervisor; and
- `VOL618A-3X001T` optocoupler for an optional FTDI RTS# to MCLR pull-down.

A physical three-pin target-power jumper replaces the full controller's active load switch. In UART position it powers only the target-side UART electronics from J5 VDD. In ICSP/PARK position it disconnects that load so a PICkit does not have to power the UART circuitry. A separate three-pin RESET ARM jumper physically removes the automatic reset sink from MCLR unless deliberately armed.

## Capabilities

### J3 UART

- live-validated physical mapping for controller `9067-0604`, serial 5215;
- non-inverted 5 V TTL UART, currently validated at 9600 8N1;
- an electrical path for `maxfirectl` identify, capture, monitor, backup, separately qualified normal control, and future qualified loader traffic;
- galvanic separation between FTDI/computer ground and the stove target domain;
- target-derived secondary power and target-power-good output gating;
- no electrical connection to J3 pin 3; and
- optional, physically armed MCLR reset through J5 for deterministic bootloader entry.

### J5 ICSP

- PICkit pins 1-5 map directly one-to-one to main-board J5;
- PICkit pin 6/AUX remains deliberately unconnected;
- no isolator, diode, LED, filter, ordinary clamp, or series resistance in MCLR, PGD, or PGC;
- target-side UART power is physically disconnected in ICSP mode; and
- the adapter provides no target power of its own, preventing a hidden competing VDD source.

## Operating modes

| Mode | Target-power jumper | Reset-arm jumper | FTDI | PICkit | Target harnesses |
| --- | --- | --- | --- | --- | --- |
| Storage / safe | `ICSP/PARK` | `PARK` | disconnected | disconnected | disconnected |
| J3 monitor/control | `UART` | `PARK` | connected | disconnected | J3 and main-board J5 connected |
| Attended J3 reset/loader entry | `UART` | `ARM` only during reset | connected | disconnected | J3 and main-board J5 connected |
| J5 ICSP | `ICSP/PARK` | `PARK` | disconnected | connected | J5 only; J3 disconnected |

The adapter is not designed for hot-plugging, simultaneous FTDI/PICkit use, energized open-stove probing, or attachment to an installed controller while mains or actuator harnesses are present during ICSP work.

## Cost and size targets

- two-layer, 1.6 mm FR-4;
- target outline no larger than 60 mm x 40 mm, hard maximum 65 mm x 45 mm;
- one small inline enclosure;
- through-hole edge connectors and jumpers, SMD protection and logic;
- preliminary assembled-electronics target of **USD 8-12 in small quantity**, excluding PCB, enclosure, FTDI cable, PICkit, and stove-end mating connectors; and
- no onboard USB bridge, microcontroller, isolated DC/DC converter, display, relay, or expansion connector.

## Current evidence boundary

J3 TX, RX, and ground are live-validated on the documented board. The J5 mapping is strong provisional evidence but remains blocked on an independent second continuity pass, exact mating-connector identification, target-power measurements, and repeatable read-only PICkit operation through the finished adapter.

No board should be ordered until the electrical connection list, exact footprints, connector orientations, component availability, mechanical arrangement, and validation gates in this directory have been independently reviewed.

## Design package

| Topic | Document |
| --- | --- |
| Current preparation status | [CURRENT_STATUS.md](CURRENT_STATUS.md) |
| Functional and safety requirements | [Design requirements](docs/DESIGN_REQUIREMENTS.md) |
| Schematic-ready circuit definition | [Electrical design](docs/ELECTRICAL_DESIGN.md) |
| Connector maps and harness requirements | [Interfaces and harnesses](docs/INTERFACES_AND_HARNESSES.md) |
| Modes and service procedure boundaries | [Operating and safety rules](docs/OPERATING_AND_SAFETY.md) |
| Size, partitioning, and enclosure constraints | [PCB and mechanical requirements](docs/PCB_AND_MECHANICAL_REQUIREMENTS.md) |
| Bench and first-article qualification | [Validation plan](docs/VALIDATION_PLAN.md) |
| Design choices and rejected alternatives | [Decision record](docs/DECISIONS.md) |
| Preliminary purchasing list | [BOM notes](bom/BOM_NOTES.md) and [CSV](bom/preliminary-bom.csv) |

Existing evidence remains authoritative:

- [J3 hardware interface](../../docs/hardware/j3-interface.md)
- [9067-0604 main-board J5 ICSP interface](../../docs/hardware/j5-icsp-interface.md)
- [J5 service safety](../../docs/guides/j5-service-safety.md)
- [PICkit preservation procedure](../../docs/guides/pickit3-firmware-preservation.md)
- [Project safety policy](../../SAFETY.md)
