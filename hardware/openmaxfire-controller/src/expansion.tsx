import { CathodePin1Diode } from "./cathode-pin1-diode"

/**
 * Protected low-voltage expansion and sensor interfaces.
 *
 * U601 adds twelve externally available GPIOs while leaving four ports for
 * local housekeeping. Every external signal has series impedance or an input
 * network, connector-side ESD protection, and a bus-switch path powered from
 * EXP_3V3. U607/U608 therefore isolate all 16 signal conductors when accessory
 * power is disabled, starting, undervoltage, or reporting a current fault.
 *
 * EXP_3V3 is a single 200 mA nominal current-limited supply shared by all
 * expansion connectors. It defaults OFF: ESP32 GPIO11 is high-impedance at
 * power-up and R605 holds the TPS2553 enable low. Firmware must explicitly
 * drive EXPANSION_ENABLE high before powering accessories. Expansion power
 * and GPIO are convenience I/O only and are not part of any stove, thermostat,
 * or dead-man safety function.
 */

type GpioChannel = {
  chipPin: number
  connectorPin: number
  seriesName: string
  pullName: string
  switchName: "U607" | "U608"
  switchChannel: number
  pcbX: number
  schY: number
}

const gpioChannels: GpioChannel[] = [
  { chipPin: 4, connectorPin: 3, seriesName: "R610", pullName: "R630", switchName: "U607", switchChannel: 1, pcbX: 27.0, schY: 6.6 },
  { chipPin: 5, connectorPin: 4, seriesName: "R611", pullName: "R631", switchName: "U607", switchChannel: 2, pcbX: 29.2, schY: 5.4 },
  { chipPin: 6, connectorPin: 5, seriesName: "R612", pullName: "R632", switchName: "U607", switchChannel: 3, pcbX: 31.4, schY: 4.2 },
  { chipPin: 7, connectorPin: 6, seriesName: "R613", pullName: "R633", switchName: "U607", switchChannel: 4, pcbX: 33.6, schY: 3.0 },
  { chipPin: 8, connectorPin: 7, seriesName: "R614", pullName: "R634", switchName: "U607", switchChannel: 5, pcbX: 35.8, schY: 1.8 },
  { chipPin: 9, connectorPin: 8, seriesName: "R615", pullName: "R635", switchName: "U607", switchChannel: 6, pcbX: 38.0, schY: 0.6 },
  { chipPin: 10, connectorPin: 11, seriesName: "R616", pullName: "R636", switchName: "U607", switchChannel: 7, pcbX: 40.2, schY: -0.6 },
  { chipPin: 11, connectorPin: 12, seriesName: "R617", pullName: "R637", switchName: "U607", switchChannel: 8, pcbX: 42.4, schY: -1.8 },
  { chipPin: 13, connectorPin: 13, seriesName: "R618", pullName: "R638", switchName: "U608", switchChannel: 1, pcbX: 44.6, schY: -3.0 },
  { chipPin: 14, connectorPin: 14, seriesName: "R619", pullName: "R639", switchName: "U608", switchChannel: 2, pcbX: 46.8, schY: -4.2 },
  { chipPin: 15, connectorPin: 15, seriesName: "R620", pullName: "R640", switchName: "U608", switchChannel: 3, pcbX: 49.0, schY: -5.4 },
  { chipPin: 16, connectorPin: 16, seriesName: "R621", pullName: "R641", switchName: "U608", switchChannel: 4, pcbX: 51.2, schY: -6.6 },
]

const ExposedGpio = ({
  chipPin,
  connectorPin,
  seriesName,
  pullName,
  switchName,
  switchChannel,
  pcbX,
  schY,
}: GpioChannel) => (
  <>
    <resistor
      name={seriesName}
      resistance="330ohm"
      footprint="0603"
      pcbX={pcbX}
      pcbY={-13.5}
      pcbRotation={90}
      schX={seriesName === "R612" ? 11.95 : 12}
      schY={schY}
      schSectionName="Expansion"
    />
    <resistor
      name={pullName}
      resistance="100kohm"
      footprint="0603"
      pcbX={pcbX}
      pcbY={-10.5}
      pcbRotation={90}
      schX={8.5}
      schY={schY}
      schSectionName="Expansion"
    />
    <trace from={`.U601 > .pin${chipPin}`} to={`.${seriesName} > .pin1`} />
    <trace from={`.${seriesName} > .pin2`} to={`.${switchName} > .A${switchChannel}`} />
    <trace from={`.${switchName} > .B${switchChannel}`} to={`.J601 > .pin${connectorPin}`} />
    <trace from={`.U601 > .pin${chipPin}`} to={`.${pullName} > .pin1`} />
    <trace from={`.${pullName} > .pin2`} to="net.GND_CTRL" />
  </>
)

const QuadEsd = ({
  name,
  pcbX,
  schX = 17,
  connectorPins,
}: {
  name: string
  pcbX: number
  schX?: number
  connectorPins: [number, number, number, number]
}) => (
  <>
    <chip
      name={name}
      manufacturerPartNumber="ESDS304DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/esds304.pdf"
      footprint="sot23_5"
      pinLabels={{
        pin1: "IO1",
        pin2: "GND",
        pin3: "IO2",
        pin4: "IO3",
        pin5: "IO4",
      }}
      pcbX={pcbX}
      pcbY={-16.8}
      schX={schX}
      schY={(pcbX - 38) / 2}
      schSectionName="Expansion"
    />
    <trace from={`.${name} > .pin1`} to={`.J601 > .pin${connectorPins[0]}`} />
    <trace from={`.${name} > .pin3`} to={`.J601 > .pin${connectorPins[1]}`} />
    <trace from={`.${name} > .pin4`} to={`.J601 > .pin${connectorPins[2]}`} />
    <trace from={`.${name} > .pin5`} to={`.J601 > .pin${connectorPins[3]}`} />
    <trace from={`.${name} > .pin2`} to="net.GND_CTRL" />
  </>
)

/**
 * Eight bidirectional signal paths with guaranteed power-off isolation.
 * The A side faces the always-powered controller logic; the B side faces the
 * external connectors. OE_N is derived from the actual EXP_3V3 rail, so a
 * disabled, starting, or current-limited accessory rail cannot be back-powered
 * through any data pin.
 */
const ExpansionBusSwitch = ({
  name,
  capacitorName,
  pcbX,
  pcbY,
  schX,
  schY,
}: {
  name: "U607" | "U608"
  capacitorName: "C608" | "C609"
  pcbX: number
  pcbY: number
  schX: number
  schY: number
}) => (
  <>
    <chip
      name={name}
      manufacturerPartNumber="SN74CBTLV3245APWR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74cbtlv3245a.pdf"
      footprint="tssop20_p0.65mm_w4.4mm"
      pinLabels={{
        pin1: "NC",
        pin2: "A1", pin3: "A2", pin4: "A3", pin5: "A4",
        pin6: "A5", pin7: "A6", pin8: "A7", pin9: "A8",
        pin10: "GND",
        pin11: "B8", pin12: "B7", pin13: "B6", pin14: "B5",
        pin15: "B4", pin16: "B3", pin17: "B2", pin18: "B1",
        pin19: "OE_N",
        pin20: "VCC",
      }}
      noConnect={["NC"]}
      pcbX={pcbX}
      pcbY={pcbY}
      schX={schX}
      schY={schY}
      schSectionName="Expansion"
    />
    <capacitor
      name={capacitorName}
      capacitance="100nF"
      maxVoltageRating="10V"
      footprint="0603"
      pcbX={pcbX + 5.5}
      pcbY={pcbY}
      schX={schX - 1.5}
      schY={schY + 3}
      schSectionName="Expansion"
    />
    <trace from={`.${name} > .VCC`} to="net.EXP_3V3" />
    <trace from={`.${name} > .GND`} to="net.GND_CTRL" />
    <trace from={`.${name} > .OE_N`} to="net.EXP_IO_OE_N" />
    <trace from={`.${capacitorName} > .pin1`} to="net.EXP_3V3" />
    <trace from={`.${capacitorName} > .pin2`} to="net.GND_CTRL" />
  </>
)

export const Expansion = () => (
  <>
    {/*
     * Keep the dense expander/connector bank in the open controller-side
     * centre bay.  Local coordinates remain readable as a standalone block;
     * this group applies the board-level floorplan offset.
     */}
    <group pcbX={-37}>
    {/**
     * TI TCA9535, active production PW package.  Address straps select 0x20.
     * Its interrupt is open drain.  All P-port pins are inputs after power-on;
     * external channels additionally have explicit pull-downs below.
     *
     * PRODUCTION GATE: verify the generated 24-pin, 0.65 mm-pitch TSSOP land
     * pattern against TI package drawing PW before fabrication release.
     */}
    <chip
      name="U601"
      manufacturerPartNumber="TCA9535PWR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tca9535.pdf"
      footprint="tssop24_p0.65mm_w4.4mm"
      pinLabels={{
        pin1: "INT_N",
        pin2: "A1",
        pin3: "A2",
        pin4: "P00",
        pin5: "P01",
        pin6: "P02",
        pin7: "P03",
        pin8: "P04",
        pin9: "P05",
        pin10: "P06",
        pin11: "P07",
        pin12: "GND",
        pin13: "P10",
        pin14: "P11",
        pin15: "P12",
        pin16: "P13",
        pin17: "P14_UNUSED",
        pin18: "P15_UNUSED",
        pin19: "P16_UNUSED",
        pin20: "P17_UNUSED",
        pin21: "A0",
        pin22: "SCL",
        pin23: "SDA",
        pin24: "VCC",
      }}
      pcbX={33}
      pcbY={-4.5}
      schX={2.23}
      schY={0}
      schSectionName="Expansion"
    />
    <capacitor name="C601" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={40} pcbY={-0.5} schOrientation="vertical" schX={-1} schY={3.5} schSectionName="Expansion" />
    <resistor name="R601" resistance="4.7kohm" footprint="0603" pcbX={23} pcbY={-3.5} pcbRotation={90} schX={-2.11} schY={1.5} schSectionName="Expansion" />
    <resistor name="R602" resistance="4.7kohm" footprint="0603" pcbX={25.5} pcbY={-3.5} pcbRotation={90} schX={-2.11} schY={0} schSectionName="Expansion" />
    <resistor name="R603" resistance="10kohm" footprint="0603" pcbX={28} pcbY={-3.5} pcbRotation={90} schX={-2} schY={-1.5} schSectionName="Expansion" />

    {/* Unused expander ports are not left floating, per the TCA9535 data sheet. */}
    <resistor name="R607" resistance="10kohm" footprint="0603" pcbX={23} pcbY={-7} pcbRotation={90} schX={4.64} schY={-8.5} schSectionName="Expansion" />
    <resistor name="R608" resistance="10kohm" footprint="0603" pcbX={25.5} pcbY={-7} pcbRotation={90} schX={7.36} schY={-8.5} schSectionName="Expansion" />
    <resistor name="R609" resistance="10kohm" footprint="0603" pcbX={28} pcbY={-7} pcbRotation={90} schX={9} schY={-8.5} schSectionName="Expansion" />
    <resistor name="R622" resistance="10kohm" footprint="0603" pcbX={20.5} pcbY={-7} pcbRotation={90} schX={11} schY={-8.5} schSectionName="Expansion" />

    <trace from=".U601 > .pin24" to="net.V3V3_MAIN" />
    <trace from=".U601 > .pin12" to="net.GND_CTRL" />
    <trace from=".C601 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C601 > .pin2" to="net.GND_CTRL" />
    <trace from=".U601 > .pin21" to="net.GND_CTRL" />
    <trace from=".U601 > .pin2" to="net.GND_CTRL" />
    <trace from=".U601 > .pin3" to="net.GND_CTRL" />
    <trace from=".U601 > .pin23" to="net.I2C_SDA" />
    <trace from=".U601 > .pin22" to="net.I2C_SCL" />
    <trace from=".R601 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R601 > .pin2" to="net.I2C_SDA" />
    <trace from=".R602 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R602 > .pin2" to="net.I2C_SCL" />
    <trace from=".R603 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R603 > .pin2" to="net.IOX_INTERRUPT_N" />
    <trace from=".U601 > .pin1" to="net.IOX_INTERRUPT_N" />
    <trace from=".U601 > .pin17" to=".R607 > .pin1" />
    <trace from=".R607 > .pin2" to="net.GND_CTRL" />
    <trace from=".U601 > .pin18" to=".R608 > .pin1" />
    <trace from=".R608 > .pin2" to="net.GND_CTRL" />
    <trace from=".U601 > .pin20" to=".R609 > .pin1" />
    <trace from=".R609 > .pin2" to="net.GND_CTRL" />
    <trace from=".U601 > .pin19" to=".R622 > .pin1" />
    <trace from=".R622 > .pin2" to="net.GND_CTRL" />

    {/**
     * Shared accessory rail.  R604 sets approximately 200 mA nominal current
     * limit (TI table: 133 kohm gives 173.7 to 233.9 mA across tolerance).
     * TPS2553 provides reverse-voltage protection and an active-low fault.
     */}
    <chip
      name="U602"
      manufacturerPartNumber="TPS2553DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tps2553-1.pdf"
      footprint="sot23_6"
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "FAULT_N", pin5: "ILIM", pin6: "OUT" }}
      pcbX={43}
      pcbY={-4.5}
      schX={3.45}
      schY={-10.62}
      schSectionName="Expansion"
    />
    <capacitor name="C602" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={43} pcbY={-8} schOrientation="vertical" schX={-1.02} schY={-11} schSectionName="Expansion" />
    <capacitor name="C603" capacitance="10uF" maxVoltageRating="10V" footprint="0805" pcbX={47} pcbY={-2.3} schOrientation="vertical" schX={7.56} schY={-11} schSectionName="Expansion" />
    <capacitor name="C604" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={50.5} pcbY={-2.5} schOrientation="vertical" schX={9} schY={-11} schSectionName="Expansion" />
    <resistor name="R604" resistance="133kohm" tolerance="1%" footprint="0603" pcbX={48} pcbY={-6.5} schX={4} schY={-16} schSectionName="Expansion" />
    <resistor name="R605" resistance="100kohm" footprint="0603" pcbX={39} pcbY={-5.5} schX={0} schY={-15} schSectionName="Expansion" />
    <resistor name="R606" resistance="10kohm" footprint="0603" pcbX={52} pcbY={-5.5} schX={7.32} schY={-13} schSectionName="Expansion" />
    <CathodePin1Diode
      name="D601"
      manufacturerPartNumber="PESD3V3U1UA,115"
      datasheetUrl="https://assets.nexperia.com/documents/data-sheet/PESD3V3U1UA_UB_UL.pdf"
      footprint="sod323"
      variant="tvs"
      pcbX={54.5}
      pcbY={-13}
      schX={11.68}
      schY={-13}
      schSectionName="Expansion"
    />

    <trace from=".U602 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".U602 > .pin2" to="net.GND_CTRL" />
    <trace from=".U602 > .pin3" to="net.EXPANSION_ENABLE" />
    <trace from=".R605 > .pin1" to=".U602 > .pin3" />
    <trace from=".R605 > .pin2" to="net.GND_CTRL" />
    <trace from=".U602 > .pin4" to="net.EXPANSION_FAULT_N" />
    <trace from=".R606 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R606 > .pin2" to="net.EXPANSION_FAULT_N" />
    <trace from=".U602 > .pin5" to=".R604 > .pin1" />
    <trace from=".R604 > .pin2" to="net.GND_CTRL" />
    <trace from=".U602 > .pin6" to="net.EXP_3V3" />
    <trace from=".C602 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C602 > .pin2" to="net.GND_CTRL" />
    <trace from=".C603 > .pin1" to="net.EXP_3V3" />
    <trace from=".C603 > .pin2" to="net.GND_CTRL" />
    <trace from=".C604 > .pin1" to="net.EXP_3V3" />
    <trace from=".C604 > .pin2" to="net.GND_CTRL" />
    <trace from=".D601 > .K" to="net.EXP_3V3" />
    <trace from=".D601 > .A" to="net.GND_CTRL" />

    {/**
     * Keyed 16-way harness: each six-GPIO bank has its own 3.3 V and ground.
     * PH headers are top-entry and remain accessible without using a board
     * edge.  Firmware must enable EXP_3V3 before driving an attached device.
     *
     * PRODUCTION GATE: verify pin-1 marking and mating shell/cable keying
     * against the current JST PH drawing and selected harness supplier.
     */}
    <connector
      name="J601"
      manufacturerPartNumber="B16B-PH-K-S(LF)(SN)"
      footprint="kicad:Connector_JST/JST_PH_B16B-PH-K_1x16_P2.00mm_Vertical"
      pinLabels={{
        pin1: "GND_A",
        pin2: "EXP_3V3_A",
        pin3: "GPIO_P00",
        pin4: "GPIO_P01",
        pin5: "GPIO_P02",
        pin6: "GPIO_P03",
        pin7: "GPIO_P04",
        pin8: "GPIO_P05",
        pin9: "GND_B",
        pin10: "EXP_3V3_B",
        pin11: "GPIO_P06",
        pin12: "GPIO_P07",
        pin13: "GPIO_P10",
        pin14: "GPIO_P11",
        pin15: "GPIO_P12",
        pin16: "GPIO_P13",
      }}
      pcbX={23}
      pcbY={-20.9}
      schX={22.6}
      schY={0}
      schSectionName="Expansion"
    />
    <trace from=".J601 > .pin1" to="net.GND_CTRL" />
    <trace from=".J601 > .pin9" to="net.GND_CTRL" />
    <trace from=".J601 > .pin2" to="net.EXP_3V3" />
    <trace from=".J601 > .pin10" to="net.EXP_3V3" />

    {gpioChannels.map((channel) => (
      <ExposedGpio key={channel.seriesName} {...channel} />
    ))}

    {/* Ground-only snapback arrays cannot back-power V3V3_MAIN through clamps. */}
    <QuadEsd name="U603" pcbX={30} connectorPins={[3, 4, 5, 6]} />
    <QuadEsd name="U604" pcbX={38} schX={16.4} connectorPins={[7, 8, 11, 12]} />
    <QuadEsd name="U605" pcbX={46} schX={17.06} connectorPins={[13, 14, 15, 16]} />
    </group>

    {/*
     * The first switch carries eight J601 GPIOs. The second carries the
     * remaining four GPIOs and every dedicated sensor signal. Both devices
     * specify Ioff isolation when their EXP_3V3 supply is at 0 V.
     */}
    <ExpansionBusSwitch name="U607" capacitorName="C608" pcbX={42} pcbY={-22} schX={27} schY={2} />
    <ExpansionBusSwitch name="U608" capacitorName="C609" pcbX={53} pcbY={-22} schX={27} schY={-8} />

    {/*
     * TLV809 provides an active-high rail-good signal: its active-low RESET
     * stays low below 2.90 V and for 200 ms after EXP_3V3 exceeds 2.93 V.
     * Three series NMOS devices pull OE_N low only when rail-good, the eFuse
     * FAULT_N output, and the firmware EXPANSION_ENABLE command are all high.
     * R605 defaults EXPANSION_ENABLE low, so any reset, startup, undervoltage,
     * current fault, or explicit disable releases OE_N to R659 and disconnects
     * every signal path.
     * Standard DBZ pinout: 1=GND, 2=RESET_N, 3=VDD.
     */}
    <chip
      name="U609"
      manufacturerPartNumber="TLV809EA29DBZR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tlv803e.pdf"
      footprint="sot23_3"
      pinLabels={{ pin1: "GND", pin2: "RESET_N", pin3: "VDD" }}
      pcbX={20}
      pcbY={-26}
      schX={25}
      schY={-14}
      schSectionName="Expansion"
    />
    <resistor name="R659" resistance="100kohm" footprint="0603" pcbX={20} pcbY={-22.5} schX={27} schY={-12} schSectionName="Expansion" />
    <resistor name="R660" resistance="100kohm" footprint="0603" pcbX={24} pcbY={-22.5} schX={29} schY={-16} schSectionName="Expansion" />
    <capacitor name="C610" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={24} pcbY={-26} schX={27} schY={-16} schSectionName="Expansion" />
    <chip name="Q601" manufacturerPartNumber="BSS138BK,215" datasheetUrl="https://assets.nexperia.com/documents/data-sheet/BSS138BK.pdf" footprint="sot23" pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} pcbX={28} pcbY={-28.5} schX={30} schY={-13} schSectionName="Expansion" />
    <chip name="Q602" manufacturerPartNumber="BSS138BK,215" datasheetUrl="https://assets.nexperia.com/documents/data-sheet/BSS138BK.pdf" footprint="sot23" pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} pcbX={33} pcbY={-28.5} schX={33} schY={-13} schSectionName="Expansion" />
    <chip name="Q603" manufacturerPartNumber="BSS138BK,215" datasheetUrl="https://assets.nexperia.com/documents/data-sheet/BSS138BK.pdf" footprint="sot23" pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }} pcbX={38} pcbY={-28.5} schX={36} schY={-13} schSectionName="Expansion" />
    <trace from=".U609 > .GND" to="net.GND_CTRL" />
    <trace from=".U609 > .RESET_N" to="net.EXP_RAIL_GOOD" />
    <trace from=".U609 > .VDD" to="net.EXP_3V3" />
    <trace from=".R659 > .pin1" to="net.EXP_3V3" />
    <trace from=".R659 > .pin2" to="net.EXP_IO_OE_N" />
    <trace from=".R660 > .pin1" to="net.EXP_RAIL_GOOD" />
    <trace from=".R660 > .pin2" to="net.GND_CTRL" />
    <trace from=".C610 > .pin1" to="net.EXP_3V3" />
    <trace from=".C610 > .pin2" to="net.GND_CTRL" />
    <trace from=".Q601 > .G" to="net.EXP_RAIL_GOOD" />
    <trace from=".Q601 > .D" to="net.EXP_IO_OE_N" />
    <trace from=".Q601 > .S" to="net.EXP_IO_GATE_MID" />
    <trace from=".Q602 > .G" to="net.EXPANSION_FAULT_N" />
    <trace from=".Q602 > .D" to="net.EXP_IO_GATE_MID" />
    <trace from=".Q602 > .S" to="net.EXP_IO_GATE_ENABLE" />
    <trace from=".Q603 > .G" to="net.EXPANSION_ENABLE" />
    <trace from=".Q603 > .D" to="net.EXP_IO_GATE_ENABLE" />
    <trace from=".Q603 > .S" to="net.GND_CTRL" />

    {/**
     * Dedicated keyed temperature-sensor port.  Data uses an external 4.7 k
     * pull-up to the switched rail, 100 ohm series damping, a weak discharge
     * path for an unpowered cable, and connector-side ESD protection.
     */}
    <group pcbX={-8} pcbY={-7}>
    <connector
      name="J602"
      manufacturerPartNumber="B3B-PH-K-S(LF)(SN)"
      footprint="kicad:Connector_JST/JST_PH_B3B-PH-K_1x03_P2.00mm_Vertical"
      pinLabels={{ pin1: "GND", pin2: "EXP_3V3", pin3: "ONEWIRE" }}
      schHeight={0.4}
      pcbX={-7}
      pcbY={-36}
      schX={22}
      schY={-13}
      schSectionName="Expansion"
    />
    <resistor name="R650" resistance="100ohm" footprint="0603" pcbX={-6} pcbY={-33} schX={14} schY={-12} schSectionName="Expansion" />
    <resistor name="R651" resistance="4.7kohm" footprint="0603" pcbX={-6} pcbY={-26.5} schX={15} schY={-13} schSectionName="Expansion" />
    <resistor name="R652" resistance="470kohm" footprint="0603" pcbX={-3} pcbY={-26.5} schX={17} schY={-10} schSectionName="Expansion" />
    <trace from=".J602 > .pin1" to="net.GND_CTRL" />
    <trace from=".J602 > .pin2" to="net.EXP_3V3" />
    <trace from=".J602 > .pin3" to=".U608 > .B5" />
    <trace from=".U608 > .A5" to=".R650 > .pin1" />
    <trace from=".R650 > .pin2" to="net.ONEWIRE_DATA" />
    <trace from=".R651 > .pin1" to="net.EXP_3V3" />
    <trace from=".R651 > .pin2" to=".U608 > .B5" />
    <trace from=".R652 > .pin1" to=".J602 > .pin3" />
    <trace from=".R652 > .pin2" to="net.GND_CTRL" />

    {/**
     * Auxiliary low-voltage inputs:
     *   pin 3 - 0 to 3.3 V analog input, 5:6 divider and 100 nF low-pass
     *   pin 4 - bidirectional GPIO, 1 k series, weak pull-down
     *   pin 5 - active-low dry-contact hopper switch, 4.7 k series and RC
     *
     * These are SELV 3.3 V signals only; they are not tolerant of stove mains,
     * 12 V automotive-style signaling, or either isolated target domain.
     */}
    <connector
      name="J603"
      manufacturerPartNumber="B5B-PH-K-S(LF)(SN)"
      footprint="kicad:Connector_JST/JST_PH_B5B-PH-K_1x05_P2.00mm_Vertical"
      pinLabels={{
        pin1: "GND",
        pin2: "EXP_3V3",
        pin3: "AUX_ADC_0_3V3",
        pin4: "AUX_GPIO1",
        pin5: "HOPPER_SWITCH_N",
      }}
      schHeight={0.6}
      pcbX={2}
      pcbY={-36}
      schX={22}
      schY={-20}
      schSectionName="Expansion"
    />
    <resistor name="R653" resistance="20kohm" tolerance="1%" footprint="0603" pcbX={-3} pcbY={-33} schX={14} schY={-17} schSectionName="Expansion" />
    <resistor name="R654" resistance="100kohm" tolerance="1%" footprint="0603" pcbX={0} pcbY={-26.5} schX={17} schY={-16} schSectionName="Expansion" />
    {/* Group offset makes this absolute (31.5, 17), adjacent to ESP GPIO1. */}
    <capacitor name="C606" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={39.5} pcbY={24} schOrientation="vertical" schX={17} schY={-18} schSectionName="Expansion" />
    <resistor name="R655" resistance="1kohm" footprint="0603" pcbX={0} pcbY={-33} schX={14} schY={-20} schSectionName="Expansion" />
    <resistor name="R656" resistance="100kohm" footprint="0603" pcbX={-6} pcbY={-24} schX={17} schY={-20} schSectionName="Expansion" />
    <resistor name="R657" resistance="4.7kohm" footprint="0603" pcbX={3} pcbY={-33} schX={14} schY={-23} schSectionName="Expansion" />
    <resistor name="R658" resistance="47kohm" footprint="0603" pcbX={-3} pcbY={-24} schX={17} schY={-22} schSectionName="Expansion" />
    <capacitor name="C607" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={0} pcbY={-24} schOrientation="vertical" schX={17} schY={-24} schSectionName="Expansion" />

    <trace from=".J603 > .pin1" to="net.GND_CTRL" />
    <trace from=".J603 > .pin2" to="net.EXP_3V3" />
    <trace from=".J603 > .pin3" to=".U608 > .B6" />
    <trace from=".U608 > .A6" to=".R653 > .pin1" />
    <trace from=".R653 > .pin2" to="net.AUX_ADC" />
    <trace from=".R654 > .pin1" to="net.AUX_ADC" />
    <trace from=".R654 > .pin2" to="net.GND_CTRL" />
    <trace from=".C606 > .pin1" to="net.AUX_ADC" />
    <trace from=".C606 > .pin2" to="net.GND_CTRL" />
    <trace from=".J603 > .pin4" to=".U608 > .B7" />
    <trace from=".U608 > .A7" to=".R655 > .pin1" />
    <trace from=".R655 > .pin2" to="net.AUX_GPIO1" />
    <trace from=".R656 > .pin1" to="net.AUX_GPIO1" />
    <trace from=".R656 > .pin2" to="net.GND_CTRL" />
    <trace from=".J603 > .pin5" to=".U608 > .B8" />
    <trace from=".U608 > .A8" to=".R657 > .pin1" />
    <trace from=".R657 > .pin2" to="net.HOPPER_SWITCH" />
    <trace from=".R658 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R658 > .pin2" to="net.HOPPER_SWITCH" />
    <trace from=".C607 > .pin1" to="net.HOPPER_SWITCH" />
    <trace from=".C607 > .pin2" to="net.GND_CTRL" />

    {/* One active, orderable four-line protector covers all sensor inputs. */}
    <chip
      name="U606"
      manufacturerPartNumber="ESDS304DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/esds304.pdf"
      footprint="sot23_5"
      pinLabels={{ pin1: "IO1", pin2: "GND", pin3: "IO2", pin4: "IO3", pin5: "IO4" }}
      pcbX={-3}
      pcbY={-29.5}
      schX={19}
      schY={-17}
      schSectionName="Expansion"
    />
    <trace from=".U606 > .pin1" to=".J602 > .pin3" />
    <trace from=".U606 > .pin3" to=".J603 > .pin3" />
    <trace from=".U606 > .pin4" to=".J603 > .pin4" />
    <trace from=".U606 > .pin5" to=".J603 > .pin5" />
    <trace from=".U606 > .pin2" to="net.GND_CTRL" />
    </group>
  </>
)
