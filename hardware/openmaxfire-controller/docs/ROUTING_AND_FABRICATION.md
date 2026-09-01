# Routing and fabrication handoff

Status: **engineering workflow only — no Rev A fabrication package has been
released**

This document records the reproducible path from the tscircuit source to a
reviewable KiCad board. Generated DSN, SES, Circuit JSON, KiCad, DRC, and Gerber
files belong under `dist/` and are intentionally not committed. A generated
file is never the source of truth.

The board sets `routingDisabled` in its tscircuit source. This is intentional:
Circuit JSON exports contain authoritative placement and net geometry without
spending time on, or accidentally trusting, the generic autorouter. All
manufacturing-route work begins with the verified Specctra export below.

## Current checkpoint

The last corrected routing experiment on 2026-08-31 established that the
140 mm x 100 mm, four-layer placement is routable without crossing the
reinforced-isolation strip:

| Check | Result |
| --- | ---: |
| Physical pad shapes coordinate-checked during DSN export | 789 |
| Explicit source nets membership-checked during DSN export | 76 |
| Unique component images in the corrected DSN | 249 |
| Initial Freerouting airwires after shared-pin normalization | 592 |
| Airwires after five routing passes | 2 |
| Multi-net physical pins in the saved checkpoint | 0 |
| Cross-net clearance violations in the saved checkpoint | 0 |
| Same-net, same-component composite-pad overlaps reported as violations | 44 |

The checkpoint is useful evidence, but it is **obsolete as a fabrication
route**. The expansion-interface audit that followed requires moving the R651
1-Wire pull-up to the connector-side domain and adding hardware
`EXPANSION_ENABLE` qualification to the bus-switch output-enable chain. A new
Circuit JSON, DSN, route, KiCad conversion, and DRC are required after those
source changes.

Those two source corrections are now complete. The 2026-09-01 post-fix export
contains 250 unique component images and independently verifies 792 physical
pad shapes plus 77 explicit net memberships with zero coordinate or membership
errors. It is the new routing input; no routed checkpoint has yet been accepted
from it.

An earlier route reached zero airwires but was rejected. The generic DSN
converter had reused a rotated component image and reversed physical pin
locations on some shared footprints. It had also omitted the isolation
keepout, allowing eight tracks and two vias through the protected strip. None
of that route may be reused.

## Why the custom handoff exists

The current third-party conversion path has three behaviors that the project
must compensate for explicitly:

1. equal-size component images can inherit already-rotated absolute pads;
2. Circuit JSON keepouts can be omitted from Specctra and KiCad output; and
3. four-layer Freerouting vias can be misread as two-layer aliases or duplicated
   both inline and as standalone vias.

The checked-in scripts make those transformations explicit and fail closed:

- `scripts/export-freerouting-dsn.ts` gives every physical component a unique
  zero-rotation image, verifies every pad coordinate and explicit net member,
  and injects the all-copper-layer isolation keepout.
- `scripts/FreeroutingAudit.java` normalizes only nets that meet on the same
  physical pin, reports remaining airwires and classified clearances, and
  creates a session handoff from a routed checkpoint.
- `scripts/import-freerouting-session.ts` maps all four copper layers, converts
  every route via to one top-to-bottom standalone via, removes duplicate inline
  via markers, and rejects unknown source-trace mappings.
- `scripts/export-routed-kicad.ts` converts the routed Circuit JSON with bounded
  high iteration limits, rejects inline vias, and injects the same four-layer
  KiCad isolation keepout.

These scripts reduce known conversion risks. They do not replace independent
schematic review, native KiCad DRC, fabrication review, or first-article test.

## Reproducible workflow

Run commands from `hardware/openmaxfire-controller`. Use the dependency
versions in `bun.lock` and do not silently upgrade the conversion packages
during a release candidate.

```sh
bun install --frozen-lockfile
bunx tsc --noEmit
mkdir -p dist/index
bunx tsci export index.circuit.tsx \
  --format circuit-json \
  --output dist/index/circuit.json
bun scripts/export-freerouting-dsn.ts \
  dist/index/circuit.json \
  dist/index/openmaxfire-controller-rev-a-pinverified.dsn
```

Compile the audit helper against the exact Freerouting installation used for
the run. `OPENMAXFIRE_FREEROUTING_JAR` below is an operator-selected path, not
a repository default:

```sh
mkdir -p dist/tools/freerouting-audit
javac \
  -cp "$OPENMAXFIRE_FREEROUTING_JAR" \
  -d dist/tools/freerouting-audit \
  scripts/FreeroutingAudit.java
java -cp "dist/tools/freerouting-audit:$OPENMAXFIRE_FREEROUTING_JAR" \
  FreeroutingAudit \
  dist/index/openmaxfire-controller-rev-a-pinverified.dsn \
  --normalize-output \
  dist/index/openmaxfire-controller-rev-a-pinverified-normalized.dsn
```

Route only the normalized DSN. Use single-threaded optimization; Freerouting
2.3.0 warns that multithreaded optimization can create clearance violations.
Never judge success from the visible ratsnest alone. Save a DSN checkpoint and
audit it:

```sh
java -cp "dist/tools/freerouting-audit:$OPENMAXFIRE_FREEROUTING_JAR" \
  FreeroutingAudit \
  dist/index/openmaxfire-controller-rev-a-routed.dsn
```

The required audit result is:

- `MULTI_NET_PINS` equals zero;
- `UNROUTED` equals zero;
- cross-net clearance violations equal zero; and
- every remaining same-net report is individually explained and recorded.

Create a Specctra session against the normalized base design, then merge the
route back into the original Circuit JSON:

```sh
java -cp "dist/tools/freerouting-audit:$OPENMAXFIRE_FREEROUTING_JAR" \
  FreeroutingAudit \
  dist/index/openmaxfire-controller-rev-a-routed.dsn \
  --ses-output dist/index/openmaxfire-controller-rev-a-routed.ses \
  --base-design openmaxfire-controller-rev-a-pinverified-normalized.dsn
bun scripts/import-freerouting-session.ts \
  dist/index/circuit.json \
  dist/index/openmaxfire-controller-rev-a-pinverified-normalized.dsn \
  dist/index/openmaxfire-controller-rev-a-routed.ses \
  dist/index/openmaxfire-controller-rev-a-routed.circuit.json
bun scripts/export-routed-kicad.ts \
  dist/index/openmaxfire-controller-rev-a-routed.circuit.json \
  dist/index/fabrication/openmaxfire-controller-rev-a.kicad_pcb \
  dist/index/fabrication/openmaxfire-controller-rev-a.kicad_pro
```

The `--base-design` value stored inside the SES is a design name, not a path
lookup performed by the Java helper. Keep it identical to the normalized DSN
filename so later reviews can identify the exact base.

## Native KiCad release gate

Open the generated board in the pinned KiCad major version and inspect all
four copper layers, net assignments, component orientation, board outline,
mounting holes, antenna clearance, isolation bridges, and keepout geometry.
Refill zones in KiCad and run native DRC with violation exit status enabled.

Gerbers and drill files may be generated only after a saved, refilled board
passes native KiCad DRC with no unexplained error or warning. The release
record must include:

- tool and dependency versions;
- hashes of tscircuit source, normalized DSN, routed DSN/SES, routed Circuit
  JSON, final KiCad board, and fabrication archive;
- DSN audit output and native KiCad DRC report;
- visual review images for every copper and mask layer;
- an isolation-strip geometry check showing that no trace, via, zone, pad,
  mounting feature, or silkscreen ambiguity defeats the domain boundary; and
- a BOM/reference reconciliation from the same source commit.

## Fabrication blockers beyond routing

Zero airwires is necessary but not sufficient. Rev A remains blocked until the
release gates in `VALIDATION_PLAN.md` and `BRINGUP_CHECKLIST.md` close,
including exact-part and footprint review, independent main-board J5 mapping,
target-power/backfeed tests, mode-switch and thermostat fail-back validation,
expansion partial-power tests, antenna/enclosure review, and first-article
inspection. No Git commit, rendered PCB image, or successful autorouter pass
changes that safety status by itself.
