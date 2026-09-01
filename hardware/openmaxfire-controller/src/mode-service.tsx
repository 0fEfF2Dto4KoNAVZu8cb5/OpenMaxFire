import { CathodePin1Diode } from "./cathode-pin1-diode"
import { TiDcu0008aFootprint } from "./ti-dcu0008a-footprint"

/**
 * Service power, fail-safe mode selection, and UART ownership.
 *
 * SW301 is a physical, break-before-make 4P3T selector.  Its four poles:
 *   A - select NORMAL or FTDI logical ownership
 *   B - qualify that the selected source is actually present
 *   C - physically supply the thermostat relay coil only in NORMAL
 *   D - physically admit FTDI VCC only in FTDI SERVICE
 *
 * No stove-target signal crosses this switch.  J3/J5 remain on the isolated
 * target side and are enabled through a separate optocoupler.
 */

const ModeSwitchFootprint = () => (
  <footprint insertionDirection="from_above" cutoutApertureDirection="from_above">
    {/*
     * Littelfuse/C&K SS-43D28-G 6 NS recommended piercing plan:
     * 20 x 0.8 mm terminal holes on a 2.0 mm by 2.5 mm grid plus two
     * 1.55 mm mechanical holes on 24 mm centers.  Each pole has duplicated
     * common terminals: C-1-2-3-C.  Position numbering must receive a second
     * continuity check on incoming parts before assembly release.
     */}
    <platedhole portHints={["pin1"]} pcbX={-9} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin2"]} pcbX={-7} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin3"]} pcbX={-5} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin4"]} pcbX={-3} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin5"]} pcbX={-1} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin6"]} pcbX={1} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin7"]} pcbX={3} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin8"]} pcbX={5} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin9"]} pcbX={7} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin10"]} pcbX={9} pcbY={1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin11"]} pcbX={-9} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin12"]} pcbX={-7} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin13"]} pcbX={-5} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin14"]} pcbX={-3} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin15"]} pcbX={-1} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin16"]} pcbX={1} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin17"]} pcbX={3} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin18"]} pcbX={5} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin19"]} pcbX={7} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <platedhole portHints={["pin20"]} pcbX={9} pcbY={-1.25} shape="circle" holeDiameter={0.8} outerDiameter={1.4} />
    <hole name="MH1" pcbX={-12} pcbY={0} diameter={1.55} />
    <hole name="MH2" pcbX={12} pcbY={0} diameter={1.55} />
    <silkscreenrect pcbX={0} pcbY={0} width={24.5} height={7} strokeWidth={0.2} />
    <courtyardrect pcbX={0} pcbY={0} width={25.5} height={8} strokeWidth={0.1} />
  </footprint>
)

const Buffer126 = ({
  name,
  pcbX,
  pcbY,
  schX,
  schY,
}: {
  name: string
  pcbX: number
  pcbY: number
  schX: number
  schY: number
}) => (
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
    schSectionName="ModeControl"
  />
)

export const ModeAndService = () => (
  <>
    <connector
      name="J301"
      manufacturerPartNumber="B6B-XH-A(LF)(SN)"
      footprint="kicad:Connector_JST/JST_XH_B6B-XH-A_1x06_P2.50mm_Vertical"
      pinLabels={{
        pin1: "BLACK_GND",
        pin2: "BROWN_CTS_N",
        pin3: "RED_VCC_5V",
        pin4: "ORANGE_TXD",
        pin5: "YELLOW_RXD",
        pin6: "GREEN_RTS_N",
      }}
      noConnect={["BROWN_CTS_N"]}
      pcbX={30}
      pcbY={45}
      pcbRotation={180}
      schX={0}
      schY={0}
      schSectionName="ModeControl"
    />

    {/**
     * R300 is the unconditional cable-current ceiling. Even with a downstream
     * hard short and 5.5 V at the cable, its 82 ohm +/-1% minimum value limits
     * VCC-wire current below 68 mA. U301 adds controlled disconnect and a
     * fault indication; every board load is downstream of R300.
     */}
    <resistor
      name="R300"
      manufacturerPartNumber="RC2512FK-0782RL"
      datasheetUrl="https://www.yageo.com/upload/media/product/productsearch/datasheet/rchip/PYu-RC_Group_51_RoHS_L_16.pdf"
      resistance="82ohm"
      tolerance="1%"
      footprint="2512"
      pcbX={34}
      pcbY={37.5}
      schX={1.5}
      schY={-3.5}
      schSectionName="ModeControl"
    />

    {/**
     * TPS2553 provides a second active limit, disconnect, and fault output.
     * TI explicitly permits ILIM tied directly to IN for its special
     * 50/75/100 mA min/typ/max setting. R300, not this tolerance-heavy active
     * limit, is the unconditional less-than-68 mA cable-current ceiling.
     */}
    <chip
      name="U301"
      manufacturerPartNumber="TPS2553DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tps2553.pdf"
      footprint="sot23_6"
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "FAULT_N", pin5: "ILIM", pin6: "OUT" }}
      pcbX={25}
      pcbY={39}
      schX={3}
      schY={0}
      schSectionName="ModeControl"
    />
    <capacitor name="C301" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={29} pcbY={40.4} schX={2} schY={2} schSectionName="ModeControl" />
    <capacitor name="C302" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={28.6} pcbY={37} schX={3.5} schY={2} schSectionName="ModeControl" />
    <capacitor name="C303" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={21} pcbY={40} schX={5} schY={2} schSectionName="ModeControl" />
    <resistor name="R301" resistance="47k" footprint="0603" pcbX={24} pcbY={35} schX={5} schY={-2} schSectionName="ModeControl" />
    <resistor name="R302" resistance="2.2k" footprint="0603" pcbX={20.5} pcbY={35} schX={6.5} schY={-2} schSectionName="ModeControl" />
    <led name="D303" color="red" footprint="0603" pcbX={17} pcbY={35} schX={8} schY={-2} schSectionName="ModeControl" />

    {/* Schottky OR: neither source can back-power the other. */}
    <CathodePin1Diode name="D301" manufacturerPartNumber="PMEG2010AEH,115" datasheetUrl="https://assets.nexperia.com/documents/data-sheet/PMEG2010AEH.pdf" footprint="sod123f" variant="schottky" pcbX={12} pcbY={39} schX={7} schY={1} schSectionName="ModeControl" />
    <CathodePin1Diode name="D302" manufacturerPartNumber="PMEG2010AEH,115" datasheetUrl="https://assets.nexperia.com/documents/data-sheet/PMEG2010AEH.pdf" footprint="sod123f" variant="schottky" pcbX={12} pcbY={36} schX={7} schY={-1} schSectionName="ModeControl" />

    <chip
      name="U302"
      manufacturerPartNumber="TLV75533PDBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tlv755p.pdf"
      footprint="sot23_5"
      pinLabels={{ pin1: "IN", pin2: "GND", pin3: "EN", pin4: "NC", pin5: "OUT" }}
      noConnect={["NC"]}
      pcbX={6}
      pcbY={38}
      schX={10}
      schY={0}
      schSectionName="ModeControl"
    />
    <capacitor name="C304" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={8.5} pcbY={34} schX={9} schY={2} schSectionName="ModeControl" />
    <capacitor name="C305" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={4.5} pcbY={34} schX={11} schY={2} schSectionName="ModeControl" />
    <capacitor name="C306" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={0.5} pcbY={34} schX={12.5} schY={2} schSectionName="ModeControl" />
    <resistor name="R303" resistance="10k" footprint="0603" pcbX={-3} pcbY={36} schX={12} schY={-2} schSectionName="ModeControl" />

    <chip
      name="SW301"
      manufacturerPartNumber="SS-43D28-G 6 NS"
      datasheetUrl="https://www.littelfuse.com/assetdocs/littelfuse-ck-slide-ss-series-datasheet?assetguid=1964a539-29dd-40e2-bbda-ce2cdfa9dede"
      footprint={<ModeSwitchFootprint />}
      pinLabels={{
        pin1: "A_COM1", pin2: "A_POS1_NORMAL", pin3: "A_POS2_FTDI", pin4: "A_POS3_OFFLINE", pin5: "A_COM2",
        pin6: "B_COM1", pin7: "B_POS1_NORMAL", pin8: "B_POS2_FTDI", pin9: "B_POS3_OFFLINE", pin10: "B_COM2",
        pin11: "C_COM1", pin12: "C_POS1_NORMAL", pin13: "C_POS2_FTDI", pin14: "C_POS3_OFFLINE", pin15: "C_COM2",
        pin16: "D_COM1", pin17: "D_POS1_NORMAL", pin18: "D_POS2_FTDI", pin19: "D_POS3_OFFLINE", pin20: "D_COM2",
      }}
      noConnect={[
        "A_POS3_OFFLINE",
        "B_POS3_OFFLINE",
        "C_POS2_FTDI",
        "C_POS3_OFFLINE",
        "D_POS1_NORMAL",
        "D_POS3_OFFLINE",
      ]}
      pcbX={0}
      pcbY={45}
      schX={15}
      schY={0}
      schSectionName="ModeControl"
    />
    <resistor name="R304" resistance="10k" footprint="0603" pcbX={-9} pcbY={40} schX={14} schY={3} schSectionName="ModeControl" />
    <resistor name="R305" resistance="10k" footprint="0603" pcbX={-5.5} pcbY={40} schX={16} schY={3} schSectionName="ModeControl" />
    <resistor name="R306" resistance="100k" footprint="0603" pcbX={-2} pcbY={40} schX={18} schY={3} schSectionName="ModeControl" />

    <chip
      name="U304"
      manufacturerPartNumber="SN74LVC2G08DCUR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf"
      footprint={<TiDcu0008aFootprint />}
      pinLabels={{ pin1: "A1", pin2: "B1", pin3: "Y2", pin4: "GND", pin5: "A2", pin6: "B2", pin7: "Y1", pin8: "VCC" }}
      pcbX={0}
      pcbY={30}
      schX={23}
      schY={0}
      schSectionName="ModeControl"
    />
    <capacitor name="C308" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={5.5} pcbY={30} schX={24} schY={2} schSectionName="ModeControl" />

    {/**
     * Explicit cross-inhibit treats the impossible-but-fault-injected N=F
     * state as OFFLINE. U304 first qualifies each throw against the selected
     * source; U307/U308 then require the opposite throw to be low.
     */}
    <chip
      name="U307"
      manufacturerPartNumber="SN74LVC2G04DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc2g04.pdf"
      footprint="sot23_6"
      pinLabels={{ pin1: "A1", pin2: "GND", pin3: "A2", pin4: "Y2", pin5: "VCC", pin6: "Y1" }}
      pcbX={-11}
      pcbY={24}
      schX={26}
      schY={-3}
      schSectionName="ModeControl"
    />
    <capacitor name="C311" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={-7} pcbY={24} schX={27} schY={-1} schSectionName="ModeControl" />
    <chip
      name="U308"
      manufacturerPartNumber="SN74LVC2G08DCUR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc2g08.pdf"
      footprint={<TiDcu0008aFootprint />}
      pinLabels={{ pin1: "A1", pin2: "B1", pin3: "Y2", pin4: "GND", pin5: "A2", pin6: "B2", pin7: "Y1", pin8: "VCC" }}
      pcbX={-2}
      pcbY={24}
      schX={29}
      schY={-3}
      schSectionName="ModeControl"
    />
    <capacitor name="C312" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={3.8} pcbY={24} schX={30} schY={-1} schSectionName="ModeControl" />

    {/* Diode OR makes interface enable true for either qualified owner. */}
    <chip
      name="D304"
      manufacturerPartNumber="BAT54C,215"
      footprint="sot23"
      pinLabels={{ pin1: "A1", pin2: "A2", pin3: "K" }}
      pcbX={-7}
      pcbY={30}
      schX={26}
      schY={0}
      schSectionName="ModeControl"
    />
    <resistor name="R307" resistance="10k" footprint="0603" pcbX={-11} pcbY={30} schX={27} schY={2} schSectionName="ModeControl" />

    <Buffer126 name="U305" pcbX={8} pcbY={27} schX={30} schY={0} />
    <Buffer126 name="U306" pcbX={15} pcbY={27} schX={34} schY={0} />
    <capacitor name="C309" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={8} pcbY={23} schX={31} schY={2} schSectionName="ModeControl" />
    <capacitor name="C310" capacitance="100nF" maxVoltageRating="10V" footprint="0603" pcbX={15} pcbY={23} schX={35} schY={2} schSectionName="ModeControl" />
    <resistor name="R308" resistance="1k" footprint="0603" pcbX={5} pcbY={32.5} schX={29} schY={2} schSectionName="ModeControl" />
    <resistor name="R309" resistance="1k" footprint="0603" pcbX={3.5} pcbY={21} schX={29} schY={-2} schSectionName="ModeControl" />
    <resistor name="R310" resistance="47k" footprint="0603" pcbX={11.5} pcbY={23} schX={32} schY={3} schSectionName="ModeControl" />

    {/* Open-drain-style mode sensing prevents service power from backfeeding an unpowered ESP. */}
    <chip
      name="Q301"
      manufacturerPartNumber="BSS138BK,215"
      footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
      pcbX={23}
      pcbY={27}
      schX={40.815}
      schY={0}
      schSectionName="ModeControl"
    />
    <chip
      name="Q302"
      manufacturerPartNumber="BSS138BK,215"
      footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
      pcbX={28}
      pcbY={27}
      schX={41}
      schY={0}
      schSectionName="ModeControl"
    />
    <resistor name="R311" resistance="100k" footprint="0603" pcbX={23} pcbY={23} schX={37} schY={2} schSectionName="ModeControl" />
    <resistor name="R312" resistance="100k" footprint="0603" pcbX={28} pcbY={23} schX={40} schY={2} schSectionName="ModeControl" />
    <resistor name="R313" resistance="100k" footprint="0603" pcbX={23} pcbY={31} schX={39} schY={2} schSectionName="ModeControl" />
    <resistor name="R314" resistance="100k" footprint="0603" pcbX={28} pcbY={31} schX={42} schY={2} schSectionName="ModeControl" />
    <resistor name="R315" resistance="100k" footprint="0603" pcbX={18} pcbY={30.5} schX={35} schY={4} schSectionName="ModeControl" />

    {/* FTDI connector and protected power. */}
    <trace from=".J301 > .pin1" to="net.GND_CTRL" />
    <trace from=".J301 > .pin3" to="net.FTDI_VCC_CABLE" />
    <trace from="net.FTDI_VCC_CABLE" to=".R300 > .pin1" />
    <trace from=".R300 > .pin2" to="net.FTDI_5V_RAW" />
    <trace from=".J301 > .pin4" to="net.FTDI_TX" />
    <trace from=".J301 > .pin5" to="net.FTDI_RX" />
    <trace from=".J301 > .pin6" to="net.FTDI_RTS_N" />
    <trace from=".U301 > .pin1" to="net.FTDI_5V_RAW" />
    <trace from=".U301 > .pin2" to="net.GND_CTRL" />
    <trace from=".U301 > .pin3" to="net.FTDI_5V_RAW" />
    <trace from=".U301 > .pin5" to="net.FTDI_5V_RAW" />
    <trace from=".U301 > .pin6" to="net.FTDI_5V_LIMITED" />
    <trace from=".U301 > .pin4" to="net.FTDI_POWER_FAULT_N" />
    <trace from=".C301 > .pin1" to="net.FTDI_5V_RAW" />
    <trace from=".C301 > .pin2" to="net.GND_CTRL" />
    <trace from=".C302 > .pin1" to="net.FTDI_5V_RAW" />
    <trace from=".C302 > .pin2" to="net.GND_CTRL" />
    <trace from=".C303 > .pin1" to="net.FTDI_5V_LIMITED" />
    <trace from=".C303 > .pin2" to="net.GND_CTRL" />
    <trace from=".R301 > .pin1" to="net.FTDI_5V_RAW" />
    <trace from=".R301 > .pin2" to="net.FTDI_POWER_FAULT_N" />
    <trace from=".R302 > .pin1" to="net.FTDI_5V_RAW" />
    <trace from=".R302 > .pin2" to=".D303 > .pin1" />
    <trace from=".D303 > .pin2" to="net.FTDI_POWER_FAULT_N" />

    {/* Main/FTDI service supply OR and 3.3 V LDO. */}
    <trace from=".D301 > .A" to="net.V5_MAIN" />
    <trace from=".D301 > .K" to="net.SERVICE_5V" />
    <trace from=".D302 > .A" to="net.FTDI_5V_MODE" />
    <trace from=".D302 > .K" to="net.SERVICE_5V" />
    <trace from=".U302 > .pin1" to="net.SERVICE_5V" />
    <trace from=".U302 > .pin2" to="net.GND_CTRL" />
    <trace from=".U302 > .pin3" to="net.SERVICE_5V" />
    <trace from=".U302 > .pin5" to="net.SERVICE_3V3" />
    <trace from=".C304 > .pin1" to="net.SERVICE_5V" />
    <trace from=".C304 > .pin2" to="net.GND_CTRL" />
    <trace from=".C305 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C305 > .pin2" to="net.GND_CTRL" />
    <trace from=".C306 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C306 > .pin2" to="net.GND_CTRL" />
    <trace from=".R303 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".R303 > .pin2" to="net.GND_CTRL" />

    {/* Physical selector pole wiring. Position 1=NORMAL, 2=FTDI, 3=OFFLINE. */}
    <trace from=".SW301 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".SW301 > .pin5" to="net.SERVICE_3V3" />
    <trace from=".SW301 > .pin2" to="net.RUN_RAW" />
    <trace from=".SW301 > .pin3" to="net.FTDI_RAW" />
    <trace from=".SW301 > .pin6" to="net.MODE_SOURCE_OK" />
    <trace from=".SW301 > .pin10" to="net.MODE_SOURCE_OK" />
    <trace from=".SW301 > .pin7" to="net.WD_CLEAR_N" />
    <trace from=".SW301 > .pin8" to="net.FTDI_5V_LIMITED" />
    <trace from=".SW301 > .pin11" to="net.V5_MAIN" />
    <trace from=".SW301 > .pin15" to="net.V5_MAIN" />
    <trace from=".SW301 > .pin12" to="net.KTH_COIL_5V" />
    <trace from=".SW301 > .pin16" to="net.FTDI_5V_LIMITED" />
    <trace from=".SW301 > .pin20" to="net.FTDI_5V_LIMITED" />
    <trace from=".SW301 > .pin18" to="net.FTDI_5V_MODE" />
    <trace from=".R304 > .pin1" to="net.RUN_RAW" />
    <trace from=".R304 > .pin2" to="net.GND_CTRL" />
    <trace from=".R305 > .pin1" to="net.FTDI_RAW" />
    <trace from=".R305 > .pin2" to="net.GND_CTRL" />
    <trace from=".R306 > .pin1" to="net.MODE_SOURCE_OK" />
    <trace from=".R306 > .pin2" to="net.GND_CTRL" />

    {/* First qualify each physical throw against the source selected by pole B. */}
    <trace from=".U304 > .pin1" to="net.RUN_RAW" />
    <trace from=".U304 > .pin2" to="net.MODE_SOURCE_OK" />
    <trace from=".U304 > .pin7" to="net.RUN_PRE" />
    <trace from=".U304 > .pin5" to="net.FTDI_RAW" />
    <trace from=".U304 > .pin6" to="net.MODE_SOURCE_OK" />
    <trace from=".U304 > .pin3" to="net.FTDI_PRE" />
    <trace from=".U304 > .pin4" to="net.GND_CTRL" />
    <trace from=".U304 > .pin8" to="net.SERVICE_3V3" />
    <trace from=".C308 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C308 > .pin2" to="net.GND_CTRL" />

    {/* RUN_MODE=RUN_PRE & !FTDI_RAW; FTDI_VALID=FTDI_PRE & !RUN_RAW. */}
    <trace from=".U307 > .pin1" to="net.FTDI_RAW" />
    <trace from=".U307 > .pin6" to="net.FTDI_INHIBIT_N" />
    <trace from=".U307 > .pin3" to="net.RUN_RAW" />
    <trace from=".U307 > .pin4" to="net.RUN_INHIBIT_N" />
    <trace from=".U307 > .pin2" to="net.GND_CTRL" />
    <trace from=".U307 > .pin5" to="net.SERVICE_3V3" />
    <trace from=".C311 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C311 > .pin2" to="net.GND_CTRL" />

    <trace from=".U308 > .pin1" to="net.RUN_PRE" />
    <trace from=".U308 > .pin2" to="net.FTDI_INHIBIT_N" />
    <trace from=".U308 > .pin7" to="net.RUN_MODE" />
    <trace from=".U308 > .pin5" to="net.FTDI_PRE" />
    <trace from=".U308 > .pin6" to="net.RUN_INHIBIT_N" />
    <trace from=".U308 > .pin3" to="net.FTDI_VALID" />
    <trace from=".U308 > .pin4" to="net.GND_CTRL" />
    <trace from=".U308 > .pin8" to="net.SERVICE_3V3" />
    <trace from=".C312 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C312 > .pin2" to="net.GND_CTRL" />

    <trace from=".D304 > .pin1" to="net.RUN_MODE" />
    <trace from=".D304 > .pin2" to="net.FTDI_VALID" />
    <trace from=".D304 > .pin3" to="net.UART_CONNECT" />
    <trace from=".R307 > .pin1" to="net.UART_CONNECT" />
    <trace from=".R307 > .pin2" to="net.GND_CTRL" />

    {/* Only one transmit buffer can drive the shared service bus. */}
    <trace from=".U305 > .pin1" to="net.RUN_MODE" />
    <trace from=".U305 > .pin2" to="net.ESP_UART_TX" />
    <trace from=".U305 > .pin6" to=".R308 > .pin1" />
    <trace from=".R308 > .pin2" to="net.SERVICE_TX_SELECTED" />
    <trace from=".U305 > .pin7" to="net.FTDI_VALID" />
    <trace from=".U305 > .pin5" to="net.FTDI_TX" />
    <trace from=".R315 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".R315 > .pin2" to="net.FTDI_TX" />
    <trace from=".U305 > .pin3" to=".R309 > .pin1" />
    <trace from=".R309 > .pin2" to="net.SERVICE_TX_SELECTED" />
    <trace from=".U305 > .pin4" to="net.GND_CTRL" />
    <trace from=".U305 > .pin8" to="net.SERVICE_3V3" />
    <trace from=".R310 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".R310 > .pin2" to="net.SERVICE_TX_SELECTED" />
    <trace from=".C309 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C309 > .pin2" to="net.GND_CTRL" />

    {/* Receive fanout is likewise enabled only for the qualified owner. */}
    <trace from=".U306 > .pin1" to="net.RUN_MODE" />
    <trace from=".U306 > .pin2" to="net.SERVICE_RX_ISOLATED" />
    <trace from=".U306 > .pin6" to="net.ESP_UART_RX" />
    <trace from=".U306 > .pin7" to="net.FTDI_VALID" />
    <trace from=".U306 > .pin5" to="net.SERVICE_RX_ISOLATED" />
    <trace from=".U306 > .pin3" to="net.FTDI_RX" />
    <trace from=".U306 > .pin4" to="net.GND_CTRL" />
    <trace from=".U306 > .pin8" to="net.SERVICE_3V3" />
    <trace from=".C310 > .pin1" to="net.SERVICE_3V3" />
    <trace from=".C310 > .pin2" to="net.GND_CTRL" />

    {/* ESP sees active-low mode indications in its own power domain. */}
    <trace from=".Q301 > .pin1" to="net.RUN_MODE" />
    <trace from=".Q301 > .pin2" to="net.GND_CTRL" />
    <trace from=".Q301 > .pin3" to="net.MODE_NORMAL_SENSE" />
    <trace from=".Q302 > .pin1" to="net.FTDI_VALID" />
    <trace from=".Q302 > .pin2" to="net.GND_CTRL" />
    <trace from=".Q302 > .pin3" to="net.MODE_FTDI_SENSE" />
    <trace from=".R311 > .pin1" to="net.RUN_MODE" />
    <trace from=".R311 > .pin2" to="net.GND_CTRL" />
    <trace from=".R312 > .pin1" to="net.FTDI_VALID" />
    <trace from=".R312 > .pin2" to="net.GND_CTRL" />
    <trace from=".R313 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R313 > .pin2" to="net.MODE_NORMAL_SENSE" />
    <trace from=".R314 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R314 > .pin2" to="net.MODE_FTDI_SENSE" />
  </>
)
