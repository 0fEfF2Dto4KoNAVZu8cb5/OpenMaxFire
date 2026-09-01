import { readFile, writeFile } from "node:fs/promises"
import {
  convertDsnSessionToCircuitJson,
  parseDsnToDsnJson,
} from "dsn-converter"
import type { AnyCircuitElement, PcbTrace, PcbVia } from "circuit-json"

const [, , circuitJsonPath, baseDsnPath, sessionPath, outputPath] = process.argv

if (!circuitJsonPath || !baseDsnPath || !sessionPath || !outputPath) {
  console.error(
    "usage: bun scripts/import-freerouting-session.ts " +
      "<circuit.json> <base.dsn> <routed.ses> <routed.circuit.json>",
  )
  process.exit(2)
}

const specctraLayerToCircuitJson = (layer: string): string => {
  if (layer === "F.Cu") return "top"
  if (layer === "B.Cu") return "bottom"
  const inner = layer.match(/^In(\d+)\.Cu$/)
  if (inner) return `inner${inner[1]}`
  throw new Error(`unsupported Specctra copper layer: ${layer}`)
}

const coordinateKey = (x: number, y: number): string =>
  `${Number(x.toFixed(4))},${Number(y.toFixed(4))}`

const original = JSON.parse(
  await readFile(circuitJsonPath, "utf8"),
) as AnyCircuitElement[]
const baseDsn = parseDsnToDsnJson(await readFile(baseDsnPath, "utf8"))
const session = parseDsnToDsnJson(await readFile(sessionPath, "utf8"))

if (!baseDsn.is_dsn_pcb) throw new Error("base input is not a Specctra PCB")
if (!session.is_dsn_session) throw new Error("route input is not a Specctra session")

/*
 * dsn-converter 0.0.92 recognizes vias only when the two-layer default
 * padstack name is present. Freerouting correctly emits a four-layer
 * Via[0-3] padstack for this board. Add a parser-only alias so the converter
 * emits the vias, then restore their actual layer semantics below.
 */
const sessionPadstacks = session.routes.library_out?.padstacks
const fourLayerVia = sessionPadstacks?.find((padstack) =>
  padstack.name.startsWith("Via[0-3]_")
)
if (
  fourLayerVia &&
  !sessionPadstacks?.some(
    (padstack) => padstack.name === "Via[0-1]_600:300_um",
  )
) {
  sessionPadstacks?.push({
    ...fourLayerVia,
    name: "Via[0-1]_600:300_um",
  })
}

const converted = convertDsnSessionToCircuitJson(baseDsn, session, original)
const routedTraces = converted.filter(
  (element): element is PcbTrace => element.type === "pcb_trace",
)
const routedVias = converted.filter(
  (element): element is PcbVia => element.type === "pcb_via",
)

const traceById = new Map(routedTraces.map((trace) => [trace.pcb_trace_id, trace]))
const netByTraceId = new Map<string, string>()
const touchingLayersByVia = new Map<string, Set<string>>()

for (const net of session.routes.network_out.nets) {
  net.wires.forEach((wire, wireIndex) => {
    if (!wire.path) return
    const traceId = `pcb_trace_${net.name}_${wireIndex}`
    const trace = traceById.get(traceId)
    if (!trace) {
      throw new Error(`session wire did not produce ${traceId}`)
    }

    const layer = specctraLayerToCircuitJson(wire.path.layer)
    netByTraceId.set(traceId, net.name)
    for (const point of trace.route) {
      if (point.route_type === "wire") point.layer = layer as typeof point.layer
    }

    for (let index = 0; index < wire.path.coordinates.length; index += 2) {
      const x = wire.path.coordinates[index]
      const y = wire.path.coordinates[index + 1]
      if (x === undefined || y === undefined) continue
      const key = `${net.name}|${coordinateKey(x / 1e4, y / 1e4)}`
      const layers = touchingLayersByVia.get(key) ?? new Set<string>()
      layers.add(layer)
      touchingLayersByVia.set(key, layers)
    }
  })
}

type ViaInfo = {
  netName: string
  layers: string[]
}

const viaInfoByCoordinate = new Map<string, ViaInfo>()
for (const net of session.routes.network_out.nets) {
  for (const via of net.vias ?? []) {
    const key = coordinateKey(via.x / 1e4, via.y / 1e4)
    const existing = viaInfoByCoordinate.get(key)
    if (existing && existing.netName !== net.name) {
      throw new Error(
        `different nets share via coordinate ${key}: ${existing.netName}, ${net.name}`,
      )
    }
    const layers = [
      ...(touchingLayersByVia.get(`${net.name}|${key}`) ?? new Set<string>()),
    ]
    viaInfoByCoordinate.set(key, { netName: net.name, layers })
  }
}

for (const trace of routedTraces) {
  const netName = netByTraceId.get(trace.pcb_trace_id)
  if (!netName) throw new Error(`missing net lookup for ${trace.pcb_trace_id}`)
  // Session wires are already split at each via. Keep the standalone pcb_via
  // below and remove the converter's duplicate inline marker.
  trace.route = trace.route.filter((point) => point.route_type !== "via")
}

for (const via of routedVias) {
  const key = coordinateKey(via.x, via.y)
  const info = viaInfoByCoordinate.get(key)
  if (!info) throw new Error(`converted via is not present in session: ${key}`)

  const owningTrace = routedTraces.find(
    (trace) =>
      netByTraceId.get(trace.pcb_trace_id) === info.netName &&
      trace.route.some(
        (point) =>
          point.route_type === "wire" &&
          coordinateKey(point.x, point.y) === key,
      ),
  )
  if (!owningTrace) throw new Error(`no routed trace owns via ${key}`)

  via.layers = ["top", "bottom"]
  via.from_layer = "top"
  via.to_layer = "bottom"
  via.pcb_trace_id = owningTrace.pcb_trace_id
}

if (routedVias.length !== viaInfoByCoordinate.size) {
  throw new Error(
    `via count mismatch: converted=${routedVias.length}, session=${viaInfoByCoordinate.size}`,
  )
}

const sourceTraceIds = new Set(
  original
    .filter((element) => element.type === "source_trace")
    .map((trace) => trace.source_trace_id),
)
const unknownSourceTraceIds = [
  ...new Set(
    routedTraces
      .map((trace) => trace.source_trace_id)
      .filter((id): id is string => id !== undefined)
      .filter((id) => !sourceTraceIds.has(id)),
  ),
]
if (unknownSourceTraceIds.length > 0) {
  throw new Error(
    `routes reference unknown source traces: ${unknownSourceTraceIds.join(", ")}`,
  )
}

const replaceableRoutingTypes = new Set([
  "pcb_trace",
  "pcb_via",
  "pcb_trace_error",
  "pcb_trace_missing_error",
  "pcb_autorouting_error",
])
const merged: AnyCircuitElement[] = [
  ...original.filter((element) => !replaceableRoutingTypes.has(element.type)),
  ...routedTraces,
  ...routedVias,
]

await writeFile(outputPath, `${JSON.stringify(merged, null, 2)}\n`)

const layerCounts = routedTraces.reduce<Record<string, number>>((counts, trace) => {
  const layer = trace.route.find((point) => point.route_type === "wire")?.layer
  if (layer) counts[layer] = (counts[layer] ?? 0) + 1
  return counts
}, {})

console.log(
  JSON.stringify(
    {
      output: outputPath,
      routed_traces: routedTraces.length,
      routed_vias: routedVias.length,
      layers: layerCounts,
      unknown_source_trace_ids: unknownSourceTraceIds.length,
    },
    null,
    2,
  ),
)
