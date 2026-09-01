/**
 * Two-terminal SMD diodes used on this board number the cathode as physical
 * pin 1 and the anode as physical pin 2.  tscircuit's generic diode defaults
 * to the opposite convention, so keep the package numbering explicit here.
 *
 * The `cathodepin1` footprint modifier also places the polarity artwork on
 * the correct pad.  Connect these parts by `.K` and `.A`, never by an assumed
 * generic diode pin order. A labeled two-pin box is intentional: tscircuit's
 * stock diode symbol binds its anode graphic to pin 1, so that symbol would
 * be visually misleading for these cathode-pin-1 production parts.
 */
type CathodePin1DiodeProps = {
  name: string
  manufacturerPartNumber: string
  datasheetUrl: string
  footprint: "sod123" | "sod123f" | "sod128" | "sod323" | "smb"
  variant?: "standard" | "schottky" | "zener" | "avalanche" | "photo" | "tvs"
  pcbX: number
  pcbY: number
  pcbRotation?: number
  schX: number
  schY: number
  schSectionName: string
}

export const CathodePin1Diode = ({
  name,
  manufacturerPartNumber,
  datasheetUrl,
  footprint,
  variant: _variant = "standard",
  pcbX,
  pcbY,
  pcbRotation,
  schX,
  schY,
  schSectionName,
}: CathodePin1DiodeProps) => (
  <chip
    name={name}
    manufacturerPartNumber={manufacturerPartNumber}
    datasheetUrl={datasheetUrl}
    footprint={`${footprint}_cathodepin1`}
    pinLabels={{
      pin1: ["K", "cathode", "neg"],
      pin2: ["A", "anode", "pos"],
    }}
    schPinArrangement={{
      leftSide: { direction: "top-to-bottom", pins: ["A"] },
      rightSide: { direction: "top-to-bottom", pins: ["K"] },
    }}
    schWidth={1.2}
    schHeight={0.6}
    pcbX={pcbX}
    pcbY={pcbY}
    pcbRotation={pcbRotation}
    schX={schX}
    schY={schY}
    schSectionName={schSectionName}
  />
)
