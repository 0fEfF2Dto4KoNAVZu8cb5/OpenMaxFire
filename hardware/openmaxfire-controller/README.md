# OpenMaxFire full controller hardware

> [!WARNING]
> **REV A IS NOT FABRICATION READY.** The saved two-airwire routing checkpoint
> is obsolete after safety fixes; the corrected source has not yet completed a
> final route or passed native KiCad DRC, footprint review, or first-article
> validation. Do not order, assemble,
> install, or connect this board to a stove. See the dated
> [hardware checkpoint](CURRENT_STATUS.md) for exact progress and remaining
> gates.

This directory is the fresh source of truth for the full OpenMaxFire controller.
It does not import or depend on the earlier KiCad service-adapter design.

The controller combines three deliberately separated roles:

1. a permanent ESP32-S3 supervisor for local temperature control, telemetry,
   verified J3 commands, and Home Assistant integration;
2. the complete target-safe J3 service interface, including deterministic
   loader reset and an independent external FTDI connection;
3. a short, direct J5/PICkit recovery path for offline service.

The future portable service cable will be derived from the reusable J3 and J5
sections after this reference controller is electrically qualified. It will omit
the ESP32, thermostat relay, permanent supply, and expansion circuitry.

Rev A is currently a 140 mm x 100 mm, four-layer engineering layout. That size
is a working envelope for safe separation, accessible test points, and first-
article serviceability; it is not yet a released enclosure outline.

## Safety status

This is an engineering reference design, not yet a construction or installation
instruction. The PCB is not released until every gate in
[`docs/VALIDATION_PLAN.md`](docs/VALIDATION_PLAN.md) has passed on spare hardware.
In particular, the main-board J5 mapping still needs a second independent
continuity pass, J5 target-power loading must be measured, the thermostat
contact voltage/current must be characterized, every exact footprint must be
independently checked, and all placement/routing/short checks must close with
zero unexplained errors. See the current open-gate table in
[`docs/BRINGUP_CHECKLIST.md`](docs/BRINGUP_CHECKLIST.md).

The factory Bixby controller remains responsible for combustion safety,
interlocks, actuators, and shutdown. OpenMaxFire never drives the igniters,
feed motor, fans, burn plate, or ash mechanism directly.

## Source and generated artifacts

- `index.circuit.tsx` is the tscircuit entry point.
- `src/` contains reusable functional blocks.
- [`CURRENT_STATUS.md`](CURRENT_STATUS.md) is the dated GitHub-facing routing,
  export-pipeline, and release-readiness checkpoint.
- `docs/` records requirements, architecture, interfaces, safety analysis, and
  validation.
- [`docs/FIRMWARE_PIN_MAP.md`](docs/FIRMWARE_PIN_MAP.md) is the hardware/firmware
  GPIO contract.
- [`docs/BRINGUP_CHECKLIST.md`](docs/BRINGUP_CHECKLIST.md) is the staged first-
  article checklist and current release-gate status.
- `bom/parts.csv` is the controlled engineering BOM.
- `dist/` is generated and intentionally ignored.

Install the pinned toolchain and run the source-level gates with:

```sh
bun install --frozen-lockfile
bun run check
bun run export:verified-dsn
```

The generic `build:preview` task is useful only for local schematic/PCB review.
Source-level autorouting is deliberately disabled, so it shows placement and
unrouted connectivity rather than manufacturing traces. Follow the
[routing and fabrication handoff](docs/ROUTING_AND_FABRICATION.md) for the
verified DSN export, Freerouting audit, routed-session import, KiCad keepout,
zone refill, and native DRC gates. Do not hand-edit generated files; change the
tscircuit source or the checked-in conversion scripts instead.

## Design principles

- Loss of controller power, firmware health, valid local temperature, or fresh
  J3 communication releases the relay and reconnects the physical thermostat.
- Only NORMAL mode can energize the thermostat-transfer relay.
- FTDI SERVICE and PICkit/OFFLINE modes force thermostat backup in hardware.
- No powered output may backfeed an unpowered stove controller.
- FTDI VCC may power only the small service front end, never the ESP32 or relay.
- An 82 ohm, 1% series power resistor gives the FTDI VCC wire an unconditional
  sub-68 mA short-circuit ceiling at 5.5 V; TPS2553 adds active limiting and
  disconnect downstream.
- USB VBUS is sensing-only. Firmware sees `USB_VBUS_PRESENT_N`, which is low
  when a USB source is present and valid only while the main 3.3 V rail is up.
- J3-3 remains no-connect/test-only. The target-side interface is provisionally
  powered from verified J5 VDD through a protected, current-limited path.
- Main-board J5 ICSP and the auxiliary igniter-board mains-voltage J5 are never
  treated as the same connector.
