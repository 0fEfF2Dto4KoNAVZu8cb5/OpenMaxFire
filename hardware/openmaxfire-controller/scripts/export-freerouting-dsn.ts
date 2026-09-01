import { readFile, writeFile } from "node:fs/promises"
import {
  convertCircuitJsonToDsnString,
  parseDsnToDsnJson,
} from "dsn-converter"
import type { AnyCircuitElement } from "circuit-json"

const [, , circuitJsonPath, outputPath] = process.argv

if (!circuitJsonPath || !outputPath) {
  console.error(
    "usage: bun scripts/export-freerouting-dsn.ts <circuit.json> <output.dsn>",
  )
  process.exit(2)
}

const original = JSON.parse(
  await readFile(circuitJsonPath, "utf8"),
) as AnyCircuitElement[]
const exportCircuit = structuredClone(original)

/*
 * dsn-converter 0.0.92 groups equal-size components into one Specctra image,
 * but derives that image from the first component's already-rotated absolute
 * pads and emits placement rotation modulo 90 degrees. A 180-degree first
 * instance therefore reverses every other instance's physical pins.
 *
 * Give every physical component its own image and bake its current pad
 * coordinates into that image with a zero-degree placement. This preserves
 * exact Circuit JSON geometry for every rotation without changing the source
 * design or the fabrication Circuit JSON.
 */
for (const element of exportCircuit) {
  if (element.type === "source_component") {
    const mutableSourceComponent = element as unknown as { ftype: string }
    mutableSourceComponent.ftype = `${element.ftype}__${element.source_component_id}`
  } else if (element.type === "pcb_component") {
    element.rotation = 0
  }
}

let dsn = convertCircuitJsonToDsnString(exportCircuit, {
  traceClearance: 150,
})

// dsn-converter currently omits pcb_keepout elements. Preserve the board's
// 8 mm reinforced-isolation strip explicitly and extend it 1 mm past both
// board edges so no routed copper can go around an endpoint.
const viaDeclaration = '    (via "Via[0-3]_600:300_um")'
const isolationKeepout =
  '    (keepout "isolation-strip" ' +
  "(polygon signal 0 -27000 -51000 -19000 -51000 -19000 51000 " +
  "-27000 51000 -27000 -51000))"
if (!dsn.includes(viaDeclaration)) {
  throw new Error("could not locate four-layer via declaration for keepout insertion")
}
dsn = dsn.replace(viaDeclaration, `${isolationKeepout}\n${viaDeclaration}`)

const parsed = parseDsnToDsnJson(dsn)
if (!parsed.is_dsn_pcb) throw new Error("export did not produce a Specctra PCB")

type Coordinate = { x: number; y: number }
const expectedPins = new Map<string, Coordinate[]>()
const actualPins = new Map<string, Coordinate[]>()

const sourceComponents = new Map(
  original
    .filter((element) => element.type === "source_component")
    .map((component) => [component.source_component_id, component]),
)
const pcbComponents = new Map(
  original
    .filter((element) => element.type === "pcb_component")
    .map((component) => [component.pcb_component_id, component]),
)
const pcbPorts = new Map(
  original
    .filter((element) => element.type === "pcb_port")
    .map((port) => [port.pcb_port_id, port]),
)
const sourcePorts = new Map(
  original
    .filter((element) => element.type === "source_port")
    .map((port) => [port.source_port_id, port]),
)

const addCoordinate = (
  map: Map<string, Coordinate[]>,
  key: string,
  coordinate: Coordinate,
) => {
  const coordinates = map.get(key) ?? []
  coordinates.push(coordinate)
  map.set(key, coordinates)
}

const polygonCenter = (points: Array<{ x: number; y: number }>): Coordinate => {
  let signedArea = 0
  let centroidX = 0
  let centroidY = 0
  for (let index = 0; index < points.length; index++) {
    const current = points[index]
    const next = points[(index + 1) % points.length]
    const cross = current.x * next.y - next.x * current.y
    signedArea += cross
    centroidX += (current.x + next.x) * cross
    centroidY += (current.y + next.y) * cross
  }
  if (signedArea !== 0) {
    return {
      x: centroidX / (signedArea * 3),
      y: centroidY / (signedArea * 3),
    }
  }
  const xs = points.map((point) => point.x)
  const ys = points.map((point) => point.y)
  return {
    x: (Math.min(...xs) + Math.max(...xs)) / 2,
    y: (Math.min(...ys) + Math.max(...ys)) / 2,
  }
}

for (const element of original) {
  if (element.type !== "pcb_smtpad" && element.type !== "pcb_plated_hole") {
    continue
  }
  if (!element.pcb_port_id) continue
  if (!element.pcb_component_id) continue
  const pcbComponent = pcbComponents.get(element.pcb_component_id)
  const sourceComponent = pcbComponent
    ? sourceComponents.get(pcbComponent.source_component_id ?? "")
    : undefined
  const pcbPort = pcbPorts.get(element.pcb_port_id)
  const sourcePort = pcbPort
    ? sourcePorts.get(pcbPort.source_port_id)
    : undefined
  if (!sourceComponent || !sourcePort || !pcbPort) continue
  const key = `${sourceComponent.name}_${sourceComponent.source_component_id}-${sourcePort.pin_number}`
  const coordinate =
    "x" in element && "y" in element
      ? { x: element.x, y: element.y }
      : polygonCenter(element.points)
  addCoordinate(expectedPins, key, coordinate)
}

for (const component of parsed.placement.components) {
  const image = parsed.library.images.find(
    (candidate) => candidate.name === component.name,
  )
  if (!image) throw new Error(`missing Specctra image: ${component.name}`)
  for (const place of component.places) {
    if (place.rotation !== 0 || place.side !== "front") {
      throw new Error(`unexpected transformed placement: ${place.refdes}`)
    }
    for (const pin of image.pins) {
      const key = `${place.refdes}-${pin.pin_number}`
      addCoordinate(actualPins, key, {
        x: (place.x + pin.x) / 1000,
        y: (place.y + pin.y) / 1000,
      })
    }
  }
}

const sortCoordinates = (coordinates: Coordinate[]) =>
  [...coordinates].sort((a, b) => a.x - b.x || a.y - b.y)
const toleranceMm = 0.0002
const pinErrors: string[] = []

for (const [key, expected] of expectedPins) {
  const actual = actualPins.get(key) ?? []
  const expectedSorted = sortCoordinates(expected)
  const actualSorted = sortCoordinates(actual)
  if (expectedSorted.length !== actualSorted.length) {
    pinErrors.push(
      `${key}: expected ${expectedSorted.length} physical pads, got ${actualSorted.length}`,
    )
    continue
  }
  expectedSorted.forEach((coordinate, index) => {
    const candidate = actualSorted[index]
    if (
      !candidate ||
      Math.abs(coordinate.x - candidate.x) > toleranceMm ||
      Math.abs(coordinate.y - candidate.y) > toleranceMm
    ) {
      pinErrors.push(
        `${key}: expected (${coordinate.x}, ${coordinate.y}), got ` +
          `(${candidate?.x}, ${candidate?.y})`,
      )
    }
  })
}

const expectedExplicitNets = new Map<string, Set<string>>()
const sourceNets = new Map(
  original
    .filter((element) => element.type === "source_net")
    .map((net) => [net.source_net_id, net]),
)

for (const trace of original.filter(
  (element) => element.type === "source_trace",
)) {
  for (const netId of trace.connected_source_net_ids ?? []) {
    const net = sourceNets.get(netId)
    if (!net) continue
    const netName = `${net.name}_${net.source_net_id}`
    const pins = expectedExplicitNets.get(netName) ?? new Set<string>()
    for (const portId of trace.connected_source_port_ids) {
      const sourcePort = sourcePorts.get(portId)
      const sourceComponent = sourcePort
        ? sourceComponents.get(sourcePort.source_component_id ?? "")
        : undefined
      if (!sourcePort || !sourceComponent) continue
      pins.add(
        `${sourceComponent.name}_${sourceComponent.source_component_id}-${sourcePort.pin_number}`,
      )
    }
    expectedExplicitNets.set(netName, pins)
  }
}

const networkErrors: string[] = []
for (const [netName, expected] of expectedExplicitNets) {
  const actual = new Set(
    parsed.network.nets.find((net) => net.name === netName)?.pins ?? [],
  )
  const missing = [...expected].filter((pin) => !actual.has(pin))
  const extra = [...actual].filter((pin) => !expected.has(pin))
  if (missing.length > 0 || extra.length > 0) {
    networkErrors.push(
      `${netName}: missing=[${missing.join(", ")}], extra=[${extra.join(", ")}]`,
    )
  }
}

if (pinErrors.length > 0 || networkErrors.length > 0) {
  throw new Error(
    [
      `Specctra export verification failed`,
      ...pinErrors.slice(0, 25),
      ...networkErrors.slice(0, 25),
    ].join("\n"),
  )
}

await writeFile(outputPath, dsn)
console.log(
  JSON.stringify(
    {
      output: outputPath,
      verified_physical_pins: [...expectedPins.values()].reduce(
        (sum, coordinates) => sum + coordinates.length,
        0,
      ),
      verified_explicit_nets: expectedExplicitNets.size,
      component_images: parsed.library.images.length,
      isolation_keepout: "x=-27..-19 mm, all copper layers",
      pin_coordinate_errors: pinErrors.length,
      network_membership_errors: networkErrors.length,
    },
    null,
    2,
  ),
)
