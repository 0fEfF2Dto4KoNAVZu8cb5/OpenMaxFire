# Full-controller hardware checkpoint

- Snapshot: 2026-09-01
- Revision: Rev A engineering design
- Source format: tscircuit, with generated Specctra/Freerouting and KiCad handoff

> [!WARNING]
> **NOT FABRICATION READY. DO NOT ORDER, ASSEMBLE, INSTALL, OR CONNECT THIS
> BOARD TO A STOVE.** The last saved routing checkpoint had two unrouted
> connections and is now obsolete after safety fixes. The current source has
> no accepted route, has not passed the final native KiCad DRC and zone-refill
> cycle, and has open electrical, footprint, mechanical, firmware, and
> first-article safety gates. A board-view screenshot is not a fabrication
> release.

This page is the concise, GitHub-facing record of where the new OpenMaxFire
hardware stands. It describes an engineering checkpoint, not a completed
product or an installation procedure. Detailed requirements and safety gates
remain authoritative and are linked below.

## Product split

OpenMaxFire is intentionally becoming two related hardware builds. Work is
currently focused only on the full controller.

| Build | Purpose | Included | Status |
| --- | --- | --- | --- |
| **Full OpenMaxFire controller** | Permanently installed supervisor and complete service interface | Full J3 and main-board J5/PICkit service capability, ESP32-S3, fail-back thermostat relay, permanent power, native USB, protected expansion, and service test points | Rev A design and routing in progress |
| **Portable service cable** | Small, inexpensive maintenance tool for stove owners and technicians | The reusable J3 and main-board J5 service functions, without the ESP32, thermostat transfer, permanent power, or expansion hardware | Deferred until the full controller's service interface is electrically qualified |

The portable service cable is not an optional ESP32 variant of this PCB. It
will be a separate, smaller, cost-focused product. The full controller must
nevertheless provide every service function planned for that cable.

## Intended full-controller capability

The current Rev A source implements these functional blocks:

- an ESP32-S3-WROOM-1U supervisor with external antenna support, native USB,
  local operation, telemetry, and a future Home Assistant integration;
- a complete J3 path for normal ESP control and independently selected FTDI
  service, including a deliberately armed, isolated reset path for repeatable
  loader entry;
- a short, direct main-board J5-to-PICkit path for offline preservation and
  recovery work, with PICkit AUX/PGM deliberately left unconnected;
- target-powered stove-side UART circuitry and an isolation boundary between
  controller ground and target ground;
- a break-before-make thermostat transfer relay whose released state returns
  control to the physical thermostat;
- hardware watchdog, health latch, mode qualification, and series relay-drive
  controls intended to make loss of power, firmware, heartbeat, or valid mode
  release the relay without software cooperation;
- protected permanent power, FTDI-only service power, USB-presence sensing,
  protected expansion GPIO, a 1-Wire sensor connection, auxiliary inputs, and
  separated controller/target test-point banks; and
- a 140 mm x 100 mm, four-layer first-revision engineering outline with four
  mounting holes and an 8 mm all-copper-layer isolation corridor.

These are design intentions and source-level implementations. They are not
claims of physical qualification. The factory controller remains authoritative
for combustion, interlocks, actuators, and shutdown; OpenMaxFire does not
directly drive stove actuators.

See the [system architecture](docs/SYSTEM_ARCHITECTURE.md),
[interface definitions](docs/INTERFACES.md), and
[design requirements](docs/DESIGN_REQUIREMENTS.md) for the detailed design.

## Current CAD and routing result

The last saved corrected Freerouting checkpoint, before the final expansion
safety edits, reports:

| Check | Result | Interpretation |
| --- | ---: | --- |
| Initial unrouted connections | 592 | Starting point after corrected export and net normalization |
| Unrouted connections in saved checkpoint | **2** | Major routing progress, but not complete |
| Pins assigned to more than one normalized net | **0** | The corrected routing input no longer has multi-net physical pins |
| Cross-net clearance reports | **0** | Freerouting's checkpoint audit found no reported overlap between different nets |
| Same-net clearance reports | 44 | All 44 are also same-component reports from overlapping primitives in compound pads; they still require an explicit final disposition |

The numbers above are a tool-specific checkpoint, not a KiCad manufacturing
DRC result. In particular, `0` cross-net reports does not prove that the board
is electrically correct, completely routed, manufacturable, or safe.

After that checkpoint was saved, the source was corrected so the connector-side
1-Wire pull-up cannot back-power a disabled expansion rail and the expansion
bus switches require `EXPANSION_ENABLE` as well as rail-good and fault
qualification. Those changes are source-verified but make the two-airwire
checkpoint obsolete. The final route must start from a newly exported design.

## Why the route was restarted

An earlier route reached zero airwires, but review found two export defects and
that result was rejected:

1. The general DSN conversion path reused a footprint image derived from an
   already rotated component. On some shared footprints this could reverse the
   physical pin mapping of another rotated instance while still producing a
   visually plausible route.
2. The general converter did not carry the PCB isolation keepout into the DSN,
   allowing the router to cross the intended isolation corridor.

That earlier zero-airwire route is **not valid fabrication evidence**. The
saved corrected two-airwire checkpoint was produced only after correcting both
paths.

## Corrected export and verification pipeline

The repository now contains a reviewable handoff pipeline under
[`scripts/`](scripts/):

1. tscircuit generates the source Circuit JSON.
2. [`export-freerouting-dsn.ts`](scripts/export-freerouting-dsn.ts) gives every
   physical component its own DSN image, bakes its current geometry into a
   zero-degree placement, and checks the exported physical pin coordinates and
   explicit net membership before writing the file.
3. The same exporter inserts the isolation corridor directly into the
   Specctra design because the upstream converter currently omits PCB keepouts.
4. [`FreeroutingAudit.java`](scripts/FreeroutingAudit.java) normalizes only net
   aliases that meet at the same physical pin, then reports multi-net pins,
   airwires, and same-net versus cross-net clearance findings.
5. [`import-freerouting-session.ts`](scripts/import-freerouting-session.ts)
   imports all four routed copper layers, checks source-trace ownership, and
   converts each routed via into one through-via instead of retaining duplicate
   inline markers.
6. [`export-routed-kicad.ts`](scripts/export-routed-kicad.ts) creates the derived
   KiCad board and restores the all-layer isolation keepout that the general
   KiCad converter also omits.
7. A native KiCad zone refill and DRC must pass before any manufacturing files
   are generated. This final stage has **not** passed yet.

For the current post-safety-fix input, the DSN export verification checked 792
physical pad shapes, 77 explicit source nets, and 250 unique component images
with zero coordinate or network-membership errors. Those checks guard the
conversion boundary; they do not replace schematic review, package
verification, KiCad DRC, or physical test.

## Isolation boundary

The Rev A source defines an 8 mm corridor centered at `x=-23 mm`, spanning
`x=-27..-19 mm` and extending 1 mm beyond both edges of the 100 mm-tall board.
The corrected DSN export applies that keepout on all four copper layers, and
the KiCad exporter recreates the same all-layer rule zone.

Only the specifically selected isolation components are intended to bridge
the controller and stove-target domains. This CAD rule is a routing constraint,
not certification of creepage, clearance, insulation grade, transient
withstand, or suitability for energized in-appliance service. Those questions
remain part of the safety and first-article validation program.

## What is verified at this checkpoint

- The current TypeScript design compiles, and the latest source netlist and
  placement checks completed without reported source/placement errors.
- The current post-fix DSN boundary independently validates all 792 physical
  pad shapes and 77 explicit nets before routing.
- The normalized corrected routing input has zero multi-net pins.
- The saved corrected route reduced 592 airwires to two and its audit reports
  zero cross-net clearance findings.
- The isolation corridor is explicitly represented in both the corrected DSN
  handoff and the custom KiCad export path.
- The full controller and later service cable have separate, documented scopes.
- J3 has a live-validated board-specific UART mapping; the main-board J5 ICSP
  mapping remains strong but provisional evidence.

Every statement above is limited to its stated evidence level. None is a
fabrication release or a substitute for the open gates below.

## What remains before a board order

At minimum:

1. complete a fresh route from the post-safety-fix input and repeat every
   routing audit on the resulting checkpoint;
2. repeat the route again if any electrical-review correction changes the
   source;
3. import the final session, verify four-layer traces and through-vias, and
   inspect the isolation corridor for any crossing;
4. generate the native KiCad project, refill zones, and close KiCad DRC with
   zero unexplained violations;
5. independently verify every exact symbol, footprint, pin number, drill,
   polarity, connector orientation, and controlled BOM entry against the
   manufacturer drawing;
6. inspect every copper, mask, paste, silkscreen, drill, and outline output;
7. finish the enclosure, harness, strain-relief, antenna, access, labeling,
   environmental, and production review;
8. close the J3, provisional J5, target-power, FTDI, thermostat, watchdog,
   partial-power, EMC, and firmware gates; and
9. build and test first articles in the staged, current-limited, offline order
   defined by the validation documents before any installed-stove evaluation.

Gerbers, drills, and a release archive should be generated only after those CAD
checks pass. Passing CAD is itself only permission to begin controlled
first-article validation, not permission for unattended stove installation or
production use.

## Reading guide

| Topic | Document |
| --- | --- |
| Controller entry point | [Full-controller README](README.md) |
| Required behavior and release gates | [Design requirements](docs/DESIGN_REQUIREMENTS.md) |
| Functional partitioning and signal ownership | [System architecture](docs/SYSTEM_ARCHITECTURE.md) |
| Connector pinouts, service modes, and test points | [Interfaces](docs/INTERFACES.md) |
| J3/J5 isolation and service-circuit implementation | [Target service design](docs/TARGET_SERVICE_DESIGN.md) |
| Hazard analysis and fail-safe claims to prove | [Safety case](docs/SAFETY_CASE.md) |
| Verification matrix | [Validation plan](docs/VALIDATION_PLAN.md) |
| First-article sequence and open gates | [Bring-up checklist](docs/BRINGUP_CHECKLIST.md) |
| Live-validated J3 evidence | [J3 hardware interface](../../docs/hardware/j3-interface.md) |
| Provisional 9067-0604 main-board J5 mapping | [J5 ICSP interface](../../docs/hardware/j5-icsp-interface.md) |
| Plain-language J5 hazard boundary | [J5 service safety](../../docs/guides/j5-service-safety.md) |
| J3 wire protocol | [J3 protocol](../../docs/protocol/j3-protocol.md) |
| Project-wide safety policy | [Safety policy](../../SAFETY.md) |
