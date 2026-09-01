import { CathodePin1Diode } from "./cathode-pin1-diode"
import { TiDcu0008aFootprint } from "./ti-dcu0008a-footprint"

/**
 * Reinforced-isolated stove target service interface.
 *
 * Active-high equations implemented here:
 *   VTGT_INTERFACE_ON = UART_CONNECT && VTGT_RAW_PRESENT
 *   J3_OE             = VTGT_GOOD
 *   ESP_MCLR_LOW      = RUN_MODE && ESP_MCLR_ASSERT && AUTO_RESET_ARMED
 *   FTDI_MCLR_LOW     = FTDI_5V_MODE_PRESENT && !FTDI_RTS_N && AUTO_RESET_ARMED
 *
 * The mechanical mode switch is entirely in the controller/service domain.
 * No J3 or J5 signal, GND_TGT, VTGT_RAW, or VTGT_PROTECTED traverses it.
 * U401/U404/U406/U407 are the only components allowed to cross the physical
 * isolation keepout below.
 */

type Placement = {
  name: string
  pcbX: number
  pcbY: number
  schX: number
  schY: number
}

const Vol618aLsop4Footprint = () => (
  <footprint>
    {/**
     * Vishay VOL618A LSOP-4 recommended land pattern, datasheet figure 22533:
     * 10.80 mm land-span, 8.20 mm inner-land gap, 0.90 mm land height, and
     * 2.54 mm pin pitch. Each land is therefore 1.30 x 0.90 mm with its
     * center 4.75 mm from the package centerline.
     *
     * The two separate silkscreen strokes deliberately do not cross the
     * isolation barrier. The filled circle identifies pin 1.
     */}
    <smtpad portHints={["pin1"]} pcbX={-4.75} pcbY={1.27} width={1.3} height={0.9} shape="rect" solderMaskMargin={0} />
    <smtpad portHints={["pin2"]} pcbX={-4.75} pcbY={-1.27} width={1.3} height={0.9} shape="rect" solderMaskMargin={0} />
    <smtpad portHints={["pin3"]} pcbX={4.75} pcbY={-1.27} width={1.3} height={0.9} shape="rect" solderMaskMargin={0} />
    <smtpad portHints={["pin4"]} pcbX={4.75} pcbY={1.27} width={1.3} height={0.9} shape="rect" solderMaskMargin={0} />
    <silkscreenpath
      route={[
        { x: -3.75, y: -1.9 },
        { x: -3.75, y: 1.9 },
      ]}
      strokeWidth={0.15}
    />
    <silkscreenpath
      route={[
        { x: 3.75, y: -1.9 },
        { x: 3.75, y: 1.9 },
      ]}
      strokeWidth={0.15}
    />
    <silkscreencircle pcbX={-3.45} pcbY={1.55} radius={0.2} isFilled />
    <courtyardrect pcbX={0} pcbY={0} width={11.3} height={4.6} strokeWidth={0.1} />
  </footprint>
)

/**
 * VOL618A LSOP-4: pin 1 anode, pin 2 cathode, pin 3 emitter, pin 4 collector.
 * Rotation places LED pins 1/2 on the controller (right) side and transistor
 * pins 3/4 on the target (left) side of the isolation barrier.
 */
const ReinforcedOptocoupler = ({ name, pcbX, pcbY, schX, schY }: Placement) => (
  <chip
    name={name}
    manufacturerPartNumber="VOL618A-3X001T"
    datasheetUrl="https://www.vishay.com/docs/82405/vol618a.pdf"
    footprint={<Vol618aLsop4Footprint />}
    pinLabels={{
      pin1: "LED_ANODE",
      pin2: "LED_CATHODE",
      pin3: "EMITTER",
      pin4: "COLLECTOR",
    }}
    pcbX={pcbX}
    pcbY={pcbY}
    pcbRotation={180}
    schX={schX}
    schY={schY}
    schSectionName="J3Service"
  />
)

/** TI DCU/VSSOP-8 physical pin map, including the crossed Y pin numbering. */
const TargetBuffer126 = ({ name, pcbX, pcbY, schX, schY }: Placement) => (
  <chip
    name={name}
    manufacturerPartNumber="SN74LVC2G126DCUR"
    datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc2g126.pdf"
    footprint={<TiDcu0008aFootprint />}
    pinLabels={{
      pin1: "OE1",
      pin2: "A1",
      pin3: "Y2",
      pin4: "GND",
      pin5: "A2",
      pin6: "Y1",
      pin7: "OE2",
      pin8: "VCC",
    }}
    pcbX={pcbX}
    pcbY={pcbY}
    schX={schX}
    schY={schY}
    schSectionName="J3Service"
  />
)

/**
 * Würth 61300611121 vertical 1x6 header on 2.54 mm pitch. The cable/tool is
 * inserted from above, not through the board edge. Pin 1 is the footprint
 * origin so its board coordinate stays explicit and reviewable.
 */
const PicKitHeaderFootprint = () => (
  <footprint insertionDirection="from_above" cutoutApertureDirection="from_above">
    <platedhole portHints={["pin1"]} pcbX={0} pcbY={0} shape="circle" holeDiameter={1} outerDiameter={1.7} />
    <platedhole portHints={["pin2"]} pcbX={0} pcbY={-2.54} shape="circle" holeDiameter={1} outerDiameter={1.7} />
    <platedhole portHints={["pin3"]} pcbX={0} pcbY={-5.08} shape="circle" holeDiameter={1} outerDiameter={1.7} />
    <platedhole portHints={["pin4"]} pcbX={0} pcbY={-7.62} shape="circle" holeDiameter={1} outerDiameter={1.7} />
    <platedhole portHints={["pin5"]} pcbX={0} pcbY={-10.16} shape="circle" holeDiameter={1} outerDiameter={1.7} />
    <platedhole portHints={["pin6"]} pcbX={0} pcbY={-12.7} shape="circle" holeDiameter={1} outerDiameter={1.7} />
    <silkscreenrect pcbX={0} pcbY={-6.35} width={2.54} height={15.24} strokeWidth={0.15} />
    <courtyardrect pcbX={0} pcbY={-6.35} width={3.54} height={16.24} strokeWidth={0.1} />
  </footprint>
)

export const TargetService = () => (
  <>
    {/*
     * Eight-millimetre no-copper strip through every board layer. Only the
     * four reinforced isolation packages may bridge it. Their target pads
     * face left and controller pads face right.
     *
     * PRODUCTION GATE: preserve this keepout in exported KiCad/Gerbers and
     * verify >= 8 mm creepage/clearance after copper pours, vias, silkscreen,
     * solder-mask openings, mounting hardware, and enclosure are finalized.
     */}
    <keepout
      shape="rect"
      pcbX={-23}
      pcbY={0}
      width="8mm"
      height="102mm"
      layers={["top", "inner1", "inner2", "bottom"]}
      excludeRefs={[".U401", ".U404", ".U406", ".U407"]}
    />
    <silkscreentext
      text="ISOLATION BARRIER - NO COPPER"
      pcbX={-23}
      pcbY={46.5}
      fontSize="0.8mm"
      anchorAlignment="center"
      layer="top"
    />

    {/*
     * Keyed stove harness. Pin 3 is deliberately absent from the circuit:
     * no power, test pad, pull-up, or ESD rail connection is permitted.
     */}
    <connector
      name="J401"
      manufacturerPartNumber="B4B-XH-A(LF)(SN)"
      footprint="kicad:Connector_JST/JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical"
      pinLabels={{
        pin1: "STOVE_RX",
        pin2: "STOVE_TX",
        pin3: "DELIBERATE_NC",
        pin4: "TARGET_GND",
      }}
      noConnect={["DELIBERATE_NC"]}
      pcbX={-65}
      pcbY={28}
      pcbRotation={270}
      schX={24}
      schY={0}
      schSectionName="J3Service"
    />
    <silkscreentext
      text="J3: 1 RX  2 TX  3 NC  4 GND"
      pcbX={-54}
      pcbY={37}
      fontSize="0.8mm"
      anchorAlignment="center"
      layer="top"
    />
    <silkscreentext
      text="1"
      pcbX={-62.5}
      pcbY={28}
      fontSize="1mm"
      anchorAlignment="center"
      layer="top"
    />

    {/*
     * PROVISIONAL J5 stove mapping; production is blocked until a second
     * independent continuity pass confirms 1=MCLR, 2=VDD, 3=VSS, 4=PGD,
     * 5=PGC on the actual stove controller and mating harness.
     */}
    <connector
      name="J402"
      manufacturerPartNumber="B5B-XH-A(LF)(SN)"
      footprint="kicad:Connector_JST/JST_XH_B5B-XH-A_1x05_P2.50mm_Vertical"
      pinLabels={{
        pin1: "MCLR_VPP",
        pin2: "VDD_VTGT",
        pin3: "VSS_TARGET",
        pin4: "PGD_RB7",
        pin5: "PGC_RB6",
      }}
      pcbX={-65}
      pcbY={11}
      pcbRotation={270}
      schX={24}
      schY={8}
      schSectionName="J3Service"
    />
    <silkscreentext
      text="MAIN J5 ICSP - PROVISIONAL"
      pcbX={-54}
      pcbY={15.5}
      fontSize="0.65mm"
      anchorAlignment="center"
      layer="top"
    />
    <silkscreentext
      text="1"
      pcbX={-62.5}
      pcbY={11}
      fontSize="1mm"
      anchorAlignment="center"
      layer="top"
    />

    {/**
     * Direct standard PICkit ICSP header. Pins 1-5 have no series parts.
     * The vertical header is inserted from above. Its pin-1 footprint origin
     * preserves the explicit (-65, -15.35) board coordinate below.
     */}
    <connector
      name="J403"
      manufacturerPartNumber="61300611121"
      datasheetUrl="https://www.we-online.com/components/products/datasheet/61300611121.pdf"
      footprint={<PicKitHeaderFootprint />}
      pinLabels={{
        pin1: "MCLR_VPP",
        pin2: "VDD_VTGT",
        pin3: "VSS_TARGET",
        pin4: "PGD_ICSPDAT",
        pin5: "PGC_ICSPCLK",
        pin6: "AUX_NC",
      }}
      noConnect={["AUX_NC"]}
      pcbX={-65}
      pcbY={-15.35}
      pcbRotation={0}
      schX={24}
      schY={14}
      schSectionName="J3Service"
    />
    <silkscreentext
      text="PICkit: 1 VPP 2 VDD 3 VSS 4 PGD 5 PGC 6 NC"
      pcbX={-53}
      pcbY={-19}
      fontSize="0.75mm"
      anchorAlignment="center"
      layer="top"
    />
    <silkscreentext
      text="1"
      pcbX={-62.5}
      pcbY={-15.35}
      fontSize="1mm"
      anchorAlignment="center"
      layer="top"
    />

    {/* UART_CONNECT optically enables the target-powered interface rail. */}
    <ReinforcedOptocoupler name="U401" pcbX={-23} pcbY={28} schX={8} schY={0} />
    <resistor
      name="R401"
      resistance="820ohm"
      footprint="0603"
      pcbX={-13}
      pcbY={28}
      schX={5}
      schY={0}
      schSectionName="J3Service"
    />
    <resistor
      name="R402"
      resistance="100kohm"
      footprint="0603"
      pcbX={-34}
      pcbY={30}
      schX={11}
      schY={2}
      schSectionName="J3Service"
    />

    <chip
      name="U402"
      manufacturerPartNumber="TPS22948DCKR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tps22948.pdf"
      footprint="kicad:Package_TO_SOT_SMD/SOT-363_SC-70-6"
      pinLabels={{
        pin1: "IN",
        pin2: "GND",
        pin3: "ON",
        pin4: "NC",
        pin5: "FLT_N",
        pin6: "OUT",
      }}
      noConnect={["NC", "FLT_N"]}
      pcbX={-40}
      pcbY={27}
      schX={14}
      schY={0}
      schSectionName="J3Service"
    />
    <capacitor name="C401" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={-43} pcbY={30} schX={13} schY={2} schSectionName="J3Service" />
    <capacitor name="C402" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={-43} pcbY={26} schX={16} schY={2} schSectionName="J3Service" />
    <capacitor name="C403" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={-40} pcbY={23.5} schX={17.5} schY={2} schSectionName="J3Service" />
    <resistor name="R403" resistance="47kohm" footprint="0603" pcbX={-36.5} pcbY={24} schX={16} schY={-2} schSectionName="J3Service" />

    {/*
     * R-pinout order is exact for TLV803EA42RDBZR:
     * pin 1 RESET_N, pin 2 GND, pin 3 VDD. RESET_N is open drain.
     */}
    <chip
      name="U403"
      manufacturerPartNumber="TLV803EA42RDBZR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tlv803e.pdf"
      footprint="sot23_3"
      pinLabels={{ pin1: "RESET_N", pin2: "GND", pin3: "VDD" }}
      pcbX={-39}
      pcbY={19}
      schX={18}
      schY={0}
      schSectionName="J3Service"
    />
    <resistor name="R404" resistance="10kohm" footprint="0603" pcbX={-35} pcbY={19} schX={19} schY={2} schSectionName="J3Service" />
    <capacitor name="C404" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={-43} pcbY={19} schX={20.5} schY={3.5} schSectionName="J3Service" />

    {/*
     * Non-F ISO7721 defaults both powered outputs HIGH if the corresponding
     * input side is absent. That is UART idle, never an unintended BREAK.
     * Pin map: 1 VCC1, 2 OUTA, 3 INB, 4 GND1, 5 GND2, 6 OUTB,
     * 7 INA, 8 VCC2.
     *
     * PRODUCTION GATE: verify the KiCad SOIC-8 wide-body land pattern against
     * TI DWV0008A and preserve its reinforced creepage geometry.
     */}
    <chip
      name="U404"
      manufacturerPartNumber="ISO7721DWVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/iso7721.pdf"
      footprint="kicad:Package_SO/SOIC-8_7.5x5.85mm_P1.27mm"
      pinLabels={{
        pin1: "VCC1",
        pin2: "OUTA",
        pin3: "INB",
        pin4: "GND1",
        pin5: "GND2",
        pin6: "OUTB",
        pin7: "INA",
        pin8: "VCC2",
      }}
      pcbX={-23}
      pcbY={8}
      pcbRotation={180}
      schX={10}
      schY={8}
      schSectionName="J3Service"
    />
    <capacitor name="C405" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={-13} pcbY={8} schX={7} schY={10} schSectionName="J3Service" />
    <capacitor name="C406" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={-13} pcbY={5.5} schX={8} schY={10} schSectionName="J3Service" />
    <capacitor name="C407" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={-33} pcbY={8} schX={13} schY={10} schSectionName="J3Service" />
    <capacitor name="C408" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={-33} pcbY={5.5} schX={14} schY={10} schSectionName="J3Service" />

    {/* Both active-high OEs use the supervised target-interface rail. */}
    <TargetBuffer126 name="U405" pcbX={-39} pcbY={8} schX={17} schY={8} />
    <capacitor name="C409" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={-39} pcbY={4.5} schX={18} schY={10} schSectionName="J3Service" />
    <resistor name="R405" resistance="330ohm" footprint="0603" pcbX={-45} pcbY={9} schX={20} schY={7} schSectionName="J3Service" />
    <resistor name="R406" resistance="330ohm" footprint="0603" pcbX={-45} pcbY={6.5} schX={20} schY={9} schSectionName="J3Service" />
    {/* UART idle is high even with the stove-side J3 TX conductor open. */}
    <resistor name="R411" resistance="47kohm" footprint="0603" pcbX={-46} pcbY={4} schX={20} schY={11} schSectionName="J3Service" />

    {/* NORMAL-only ESP MCLR pull-down. A low RUN_MODE removes LED current. */}
    <ReinforcedOptocoupler name="U406" pcbX={-23} pcbY={18} schX={8} schY={16} />
    <resistor name="R407" resistance="1kohm" footprint="0603" pcbX={-13} pcbY={18} schX={5} schY={16} schSectionName="J3Service" />
    <chip
      name="Q401"
      manufacturerPartNumber="BSS138BK,215"
      footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
      pcbX={-13}
      pcbY={14}
      schX={6}
      schY={19}
      schSectionName="J3Service"
    />
    <resistor name="R408" resistance="100kohm" footprint="0603" pcbX={-9} pcbY={14} schX={4} schY={19} schSectionName="J3Service" />

    {/**
     * FTDI RTS# is active low. D402 admits current only from the selected
     * FTDI rail, blocking an unpowered FTDI_5V_MODE node from being back-fed
     * through R409. D401 remains anti-parallel across the optocoupler LED.
     */}
    <ReinforcedOptocoupler name="U407" pcbX={-23} pcbY={40} schX={8} schY={23} />
    <resistor name="R409" resistance="1.5kohm" footprint="0603" pcbX={-13} pcbY={40} schX={5} schY={23} schSectionName="J3Service" />
    <CathodePin1Diode
      name="D402"
      manufacturerPartNumber="PMEG2010AEH,115"
      datasheetUrl="https://assets.nexperia.com/documents/data-sheet/PMEG2010AEH.pdf"
      footprint="sod123f"
      variant="schottky"
      pcbX={-15.5}
      pcbY={44}
      schX={3}
      schY={23}
      schSectionName="J3Service"
    />
    <CathodePin1Diode
      name="D401"
      manufacturerPartNumber="1N4148W-7-F"
      datasheetUrl="https://www.diodes.com/assets/Datasheets/ds30086.pdf"
      footprint="sod123"
      pcbX={-13}
      pcbY={36}
      schX={8}
      schY={26}
      schSectionName="J3Service"
    />

    {/*
     * Removable 2.54 mm shunt is deliberately NOT fitted by default.
     * R410 exists only in the automatic open-collector branch. The direct
     * J402/J403 MCLR/VPP path remains zero-ohm and VPP capable.
     */}
    <resistor name="R410" resistance="100ohm" footprint="0603" pcbX={-34} pcbY={-18} schX={13} schY={20} schSectionName="J3Service" />
    <connector
      name="J404"
      manufacturerPartNumber="M20-9990245"
      footprint="kicad:Connector_PinHeader_2.54mm/PinHeader_1x02_P2.54mm_Vertical"
      pinLabels={{ pin1: "AUTO_RESET_OD", pin2: "MCLR_ARMED" }}
      pcbX={-40}
      pcbY={-18}
      schX={16}
      schY={20}
      schSectionName="J3Service"
    />
    <silkscreentext
      text="AUTO RESET ARM - SHUNT NOT FITTED"
      pcbX={-45}
      pcbY={-25}
      fontSize="0.75mm"
      anchorAlignment="center"
      layer="top"
    />

    {/* J3/J5 edge harnesses and direct PICkit mapping. */}
    <trace from=".J401 > .pin1" to="net.J3_STOVE_RX" />
    <trace from=".J401 > .pin2" to="net.J3_STOVE_TX" />
    <trace from=".J401 > .pin4" to="net.GND_TGT" />

    <trace from=".J402 > .pin1" to="net.J5_MCLR_VPP" />
    <trace from=".J402 > .pin2" to="net.VTGT_RAW" />
    <trace from=".J402 > .pin3" to="net.GND_TGT" />
    <trace from=".J402 > .pin4" to="net.J5_PGD" />
    <trace from=".J402 > .pin5" to="net.J5_PGC" />

    <trace from=".J403 > .pin1" to="net.J5_MCLR_VPP" />
    <trace from=".J403 > .pin2" to="net.VTGT_RAW" />
    <trace from=".J403 > .pin3" to="net.GND_TGT" />
    <trace from=".J403 > .pin4" to="net.J5_PGD" />
    <trace from=".J403 > .pin5" to="net.J5_PGC" />

    {/* Optically controlled, target-derived interface supply. */}
    <trace from="net.UART_CONNECT" to=".R401 > .pin1" />
    <trace from=".R401 > .pin2" to=".U401 > .pin1" />
    <trace from=".U401 > .pin2" to="net.GND_CTRL" />
    <trace from=".U401 > .pin4" to="net.VTGT_RAW" />
    <trace from=".U401 > .pin3" to=".U402 > .pin3" />
    <trace from=".U401 > .pin3" to=".R402 > .pin1" />
    <trace from=".R402 > .pin2" to="net.GND_TGT" />

    <trace from=".U402 > .pin1" to="net.VTGT_RAW" />
    <trace from=".U402 > .pin2" to="net.GND_TGT" />
    <trace from=".U402 > .pin6" to="net.VTGT_PROTECTED" />
    <trace from=".C401 > .pin1" to="net.VTGT_RAW" />
    <trace from=".C401 > .pin2" to="net.GND_TGT" />
    <trace from=".C402 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".C402 > .pin2" to="net.GND_TGT" />
    <trace from=".C403 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".C403 > .pin2" to="net.GND_TGT" />
    <trace from=".R403 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".R403 > .pin2" to="net.GND_TGT" />

    {/* 4.2 V threshold plus 200 ms release delay qualifies both buffer OEs. */}
    <trace from=".U403 > .pin1" to="net.VTGT_GOOD" />
    <trace from=".U403 > .pin2" to="net.GND_TGT" />
    <trace from=".U403 > .pin3" to="net.VTGT_PROTECTED" />
    <trace from=".R404 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".R404 > .pin2" to="net.VTGT_GOOD" />
    <trace from=".C404 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".C404 > .pin2" to="net.GND_TGT" />

    {/* Controller side of ISO7721. */}
    <trace from=".U404 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".U404 > .pin2" to="net.SERVICE_RX_ISOLATED" />
    <trace from=".U404 > .pin3" to="net.SERVICE_TX_SELECTED" />
    <trace from=".U404 > .pin4" to="net.GND_CTRL" />
    <trace from=".C405 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C405 > .pin2" to="net.GND_CTRL" />
    <trace from=".C406 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C406 > .pin2" to="net.GND_CTRL" />

    {/* Target side of ISO7721 and its local rail decoupling. */}
    <trace from=".U404 > .pin5" to="net.GND_TGT" />
    <trace from=".U404 > .pin8" to="net.VTGT_PROTECTED" />
    <trace from=".C407 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".C407 > .pin2" to="net.GND_TGT" />
    <trace from=".C408 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".C408 > .pin2" to="net.GND_TGT" />

    {/* Host-to-stove: OUTB -> tri-state buffer -> 330 R -> J3 pin 1. */}
    <trace from=".U404 > .pin6" to=".U405 > .pin2" />
    <trace from=".U405 > .pin6" to=".R405 > .pin1" />
    <trace from=".R405 > .pin2" to="net.J3_STOVE_RX" />

    {/* Stove-to-host: J3 pin 2 -> 330 R -> tri-state buffer -> INA. */}
    <trace from="net.J3_STOVE_TX" to=".R406 > .pin1" />
    <trace from=".R406 > .pin2" to=".U405 > .pin5" />
    <trace from="net.VTGT_PROTECTED" to=".R411 > .pin1" />
    <trace from=".R411 > .pin2" to=".U405 > .pin5" />
    <trace from=".U405 > .pin3" to=".U404 > .pin7" />

    <trace from=".U405 > .pin1" to="net.VTGT_GOOD" />
    <trace from=".U405 > .pin7" to="net.VTGT_GOOD" />
    <trace from=".U405 > .pin4" to="net.GND_TGT" />
    <trace from=".U405 > .pin8" to="net.VTGT_PROTECTED" />
    <trace from=".C409 > .pin1" to="net.VTGT_PROTECTED" />
    <trace from=".C409 > .pin2" to="net.GND_TGT" />

    {/* NORMAL/ESP automatic MCLR open-collector path. */}
    <trace from="net.RUN_MODE" to=".R407 > .pin1" />
    <trace from=".R407 > .pin2" to=".U406 > .pin1" />
    <trace from=".U406 > .pin2" to=".Q401 > .pin3" />
    <trace from=".Q401 > .pin1" to="net.ESP_MCLR_ASSERT" />
    <trace from=".Q401 > .pin2" to="net.GND_CTRL" />
    <trace from=".R408 > .pin1" to="net.ESP_MCLR_ASSERT" />
    <trace from=".R408 > .pin2" to="net.GND_CTRL" />

    {/* FTDI automatic MCLR path; D401 is anti-parallel to U407's LED. */}
    <trace from="net.FTDI_5V_MODE" to=".D402 > .A" />
    <trace from=".D402 > .K" to=".R409 > .pin1" />
    <trace from=".R409 > .pin2" to=".U407 > .pin1" />
    <trace from=".U407 > .pin2" to="net.FTDI_RTS_N" />
    <trace from=".D401 > .A" to=".U407 > .pin2" />
    <trace from=".D401 > .K" to=".U407 > .pin1" />

    {/* Target-side opto outputs share only the removable automatic branch. */}
    <trace from=".U406 > .pin3" to="net.GND_TGT" />
    <trace from=".U407 > .pin3" to="net.GND_TGT" />
    <trace from=".U406 > .pin4" to=".R410 > .pin1" />
    <trace from=".U407 > .pin4" to=".R410 > .pin1" />
    <trace from=".R410 > .pin2" to=".J404 > .pin1" />
    <trace from=".J404 > .pin2" to="net.J5_MCLR_VPP" />
  </>
)
