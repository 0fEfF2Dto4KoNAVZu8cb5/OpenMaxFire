# OpenMaxFire hardware

OpenMaxFire currently has two separate hardware tracks.

## Active priority: portable service adapter

The [portable service adapter](openmaxfire-service-adapter/README.md) is now the first hardware proof platform. It is intentionally small and low cost, using an external genuine FTDI cable for isolated J3 UART service and an external PICkit for direct main-board J5 ICSP.

Its preparation package includes:

- frozen Rev A scope and non-goals;
- schematic-ready electrical connections;
- J3, J5, FTDI, PICkit, and jumper pin maps;
- harness and enclosure requirements;
- preliminary BOM and cost target;
- operating/safety boundaries; and
- staged UART, reset, target-power, and ICSP validation.

No PCB design or fabrication release exists yet.

## Preserved reference: full controller

The [full OpenMaxFire controller](openmaxfire-controller/CURRENT_STATUS.md) remains a documented reference design for a future permanent supervisor with an ESP32, thermostat fail-back, permanent power, and expansion. Its existing Rev A routing is not fabrication-ready.

The portable adapter is a separate product, not a depopulated version of the full-controller PCB. Evidence from the adapter should be used to simplify and qualify the full controller's future J3/J5 section.

## Current sequence

1. close the adapter's J5 mapping, connector-identification, and target-power measurements;
2. independently review and capture its schematic;
3. verify exact footprints and draw the small two-layer PCB;
4. build controlled first articles and qualify UART read-only operation;
5. qualify isolated reset and J5 read-only ICSP on expendable hardware;
6. qualify recovery/write behavior only after repeated readback succeeds; and
7. return to the permanent controller using the measured, proven service interface.
