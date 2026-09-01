import { mkdir, readFile, writeFile } from "node:fs/promises"
import { dirname } from "node:path"
import {
  CircuitJsonToKicadPcbConverter,
  CircuitJsonToKicadProConverter,
} from "circuit-json-to-kicad"
import type { CircuitJson } from "circuit-json"

const [, , circuitJsonPath, pcbOutputPath, projectOutputPath] = process.argv

if (!circuitJsonPath || !pcbOutputPath) {
  console.error(
    "usage: bun scripts/export-routed-kicad.ts " +
      "<routed.circuit.json> <output.kicad_pcb> [output.kicad_pro]",
  )
  process.exit(2)
}

const circuitJson = JSON.parse(
  await readFile(circuitJsonPath, "utf8"),
) as CircuitJson

const inlineVias = circuitJson
  .filter((element) => element.type === "pcb_trace")
  .flatMap((trace) => trace.route)
  .filter((point) => point.route_type === "via")
if (inlineVias.length > 0) {
  throw new Error(
    `routed Circuit JSON contains ${inlineVias.length} duplicate inline vias`,
  )
}

const pcbConverter = new CircuitJsonToKicadPcbConverter(circuitJson, {
  projectName: "openmaxfire-controller-rev-a",
})
for (const stage of pcbConverter.pipeline) stage.MAX_ITERATIONS = 10_000
pcbConverter.runUntilFinished()
let pcb = pcbConverter.getOutputString()

/*
 * circuit-json-to-kicad currently omits pcb_keepout. Recreate the same
 * all-copper-layer isolation strip enforced during Freerouting. The converter
 * maps Circuit JSON (x, y) to KiCad (100 + x, 100 - y).
 */
const isolationKeepout = `  (zone
    (net 0)
    (net_name "")
    (layers "F.Cu" "In1.Cu" "In2.Cu" "B.Cu")
    (uuid 00000000-0000-4000-8000-00000000a001)
    (hatch edge 0.5)
    (keepout
      (tracks not_allowed)
      (vias not_allowed)
      (pads allowed)
      (copperpour not_allowed)
      (footprints allowed)
    )
    (connect_pads
      (clearance 0)
    )
    (min_thickness 0.25)
    (filled_areas_thickness no)
    (polygon
      (pts
        (xy 73 49)
        (xy 81 49)
        (xy 81 151)
        (xy 73 151)
      )
    )
  )`

const firstFootprint = "  (footprint"
if (!pcb.includes(firstFootprint)) {
  throw new Error("could not locate KiCad footprint insertion point")
}
pcb = pcb.replace(firstFootprint, `${isolationKeepout}\n${firstFootprint}`)

await mkdir(dirname(pcbOutputPath), { recursive: true })
await writeFile(pcbOutputPath, pcb)

if (projectOutputPath) {
  const projectName = "openmaxfire-controller-rev-a"
  const proConverter = new CircuitJsonToKicadProConverter(circuitJson, {
    projectName,
    pcbFilename: `${projectName}.kicad_pcb`,
    schematicFilename: `${projectName}.kicad_sch`,
  })
  proConverter.runUntilFinished()
  await mkdir(dirname(projectOutputPath), { recursive: true })
  await writeFile(projectOutputPath, proConverter.getOutputString())
}

const count = (pattern: RegExp): number => pcb.match(pattern)?.length ?? 0
const summary = {
  output: pcbOutputPath,
  segments: count(/^  \(segment$/gm),
  vias: count(/^  \(via$/gm),
  copper_zones: count(/^  \(zone$/gm) - 1,
  isolation_keepout_zones: count(/00000000-0000-4000-8000-00000000a001/g),
  inline_circuit_json_vias: inlineVias.length,
}

if (summary.isolation_keepout_zones !== 1) {
  throw new Error("KiCad isolation keepout injection failed")
}

console.log(JSON.stringify(summary, null, 2))
