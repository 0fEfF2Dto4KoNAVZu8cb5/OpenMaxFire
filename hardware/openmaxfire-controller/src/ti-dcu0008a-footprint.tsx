/**
 * TI DCU0008A / VSSOP-8 land pattern.
 *
 * The generic tscircuit `vssop8_p0.5mm` shorthand currently emits 0.50 mm
 * wide pads on a 0.50 mm pitch, which makes adjacent pads touch.  This shared
 * footprint keeps the 0.50 mm pitch but uses 0.28 mm pad width, leaving
 * 0.22 mm copper clearance and satisfying this board's 0.20 mm rule.
 * Pin ordering matches TI's top-view DCU package drawing.
 */
export const TiDcu0008aFootprint = () => (
  <footprint>
    <smtpad portHints={["pin1"]} pcbX={-1.4} pcbY={0.75} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin2"]} pcbX={-1.4} pcbY={0.25} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin3"]} pcbX={-1.4} pcbY={-0.25} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin4"]} pcbX={-1.4} pcbY={-0.75} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin5"]} pcbX={1.4} pcbY={-0.75} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin6"]} pcbX={1.4} pcbY={-0.25} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin7"]} pcbX={1.4} pcbY={0.25} width={1.25} height={0.28} shape="rect" />
    <smtpad portHints={["pin8"]} pcbX={1.4} pcbY={0.75} width={1.25} height={0.28} shape="rect" />
    <silkscreenpath
      route={[
        { x: -1.15, y: -1.05 },
        { x: 1.15, y: -1.05 },
        { x: 1.15, y: 1.05 },
        { x: -1.15, y: 1.05 },
      ]}
      strokeWidth={0.15}
    />
    <silkscreencircle pcbX={-0.75} pcbY={0.65} radius={0.18} isFilled />
    <courtyardrect pcbX={0} pcbY={0} width={4.25} height={2.3} strokeWidth={0.1} />
  </footprint>
)
