import { CathodePin1Diode } from "./cathode-pin1-diode"

/**
 * TI RPW0010A recommended HotRod land pattern (drawing 4225183/A).
 *
 * The four corner terminals are true L-shaped lands; each is constructed from
 * two same-pin rounded rectangles. Pins 5 and 6 are the long power lands. The
 * smaller same-pin pads are fully contained paste carriers implementing TI's
 * 0.100 mm-stencil apertures without changing the copper outline.
 */
const TiRpw0010aFootprint = () => (
  <footprint>
    {/* Pin 1: upper-left L land plus 93%-area paste carriers. */}
    <smtpad portHints={["pin1"]} pcbX={-0.9} pcbY={0.7} width={0.6} height={0.3} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin1"]} pcbX={-0.725} pcbY={0.875} width={0.25} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin1"]} pcbX={-0.9} pcbY={0.6875} width={0.6} height={0.275} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin1"]} pcbX={-0.7125} pcbY={0.875} width={0.225} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />

    <smtpad portHints={["pin2"]} pcbX={-0.9} pcbY={0.225} width={0.6} height={0.25} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={0} />
    <smtpad portHints={["pin3"]} pcbX={-0.9} pcbY={-0.225} width={0.6} height={0.25} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={0} />

    {/* Pin 4: lower-left L land. */}
    <smtpad portHints={["pin4"]} pcbX={-0.9} pcbY={-0.7} width={0.6} height={0.3} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin4"]} pcbX={-0.725} pcbY={-0.875} width={0.25} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin4"]} pcbX={-0.9} pcbY={-0.6875} width={0.6} height={0.275} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin4"]} pcbX={-0.7125} pcbY={-0.875} width={0.225} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />

    {/* Long IN/OUT lands with two TI stencil apertures per pin. */}
    <smtpad portHints={["pin5"]} pcbX={-0.25} pcbY={0} width={0.3} height={2.4} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin5"]} pcbX={-0.25} pcbY={0.63} width={0.28} height={1.06} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin5"]} pcbX={-0.25} pcbY={-0.63} width={0.28} height={1.06} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin6"]} pcbX={0.25} pcbY={0} width={0.3} height={2.4} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin6"]} pcbX={0.25} pcbY={0.63} width={0.28} height={1.06} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin6"]} pcbX={0.25} pcbY={-0.63} width={0.28} height={1.06} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />

    {/* Pin 7: lower-right L land. */}
    <smtpad portHints={["pin7"]} pcbX={0.9} pcbY={-0.7} width={0.6} height={0.3} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin7"]} pcbX={0.725} pcbY={-0.875} width={0.25} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin7"]} pcbX={0.9} pcbY={-0.6875} width={0.6} height={0.275} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin7"]} pcbX={0.7125} pcbY={-0.875} width={0.225} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />

    <smtpad portHints={["pin8"]} pcbX={0.9} pcbY={-0.225} width={0.6} height={0.25} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={0} />
    <smtpad portHints={["pin9"]} pcbX={0.9} pcbY={0.225} width={0.6} height={0.25} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={0} />

    {/* Pin 10: upper-right L land. */}
    <smtpad portHints={["pin10"]} pcbX={0.9} pcbY={0.7} width={0.6} height={0.3} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin10"]} pcbX={0.725} pcbY={0.875} width={0.25} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0.05} solderPasteMargin={-2} />
    <smtpad portHints={["pin10"]} pcbX={0.9} pcbY={0.6875} width={0.6} height={0.275} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />
    <smtpad portHints={["pin10"]} pcbX={0.7125} pcbY={0.875} width={0.225} height={0.65} shape="rect" cornerRadius={0.05} solderMaskMargin={0} solderPasteMargin={0} />

    <silkscreencircle pcbX={-1.75} pcbY={0.7} radius={0.125} isFilled />
    <courtyardrect pcbX={0} pcbY={0} width={3} height={3} strokeWidth={0.1} />
  </footprint>
)

export const PermanentPower = () => (
  <>
    <connector
      name="J1"
      manufacturerPartNumber="B2P-VH-B(LF)(SN)"
      footprint="kicad:Connector_JST/JST_VH_B2P-VH-B_1x02_P3.96mm_Vertical"
      pinLabels={{ pin1: "VIN_12V", pin2: "GND" }}
      pcbX={67.5}
      pcbY={-39}
      pcbRotation={90}
      schX={0}
      schY={0}
      schSectionName="Power"
    />
    <fuse
      name="F1"
      manufacturerPartNumber="1812L150/24DR"
      datasheetUrl="https://www.littelfuse.com/assetdocs/littelfuse-ptc-1812l-datasheet?assetguid=1bc63281-b1f6-44c9-9626-f96bdc8d7c2f"
      currentRating="1.5A"
      voltageRating="24V"
      footprint="1812"
      pcbX={60}
      pcbY={-37}
      schX={1.5}
      schY={0}
      schSectionName="Power"
    />
    <CathodePin1Diode
      name="D3"
      manufacturerPartNumber="PMEG6030EP,115"
      datasheetUrl="https://assets.nexperia.com/documents/data-sheet/PMEG6030EP.pdf"
      footprint="sod128"
      variant="schottky"
      pcbX={55}
      pcbY={-43}
      schX={2.75}
      schY={0}
      schSectionName="Power"
    />
    <CathodePin1Diode
      name="D1"
      manufacturerPartNumber="SMBJ15A-13-F"
      datasheetUrl="https://www.diodes.com/assets/Datasheets/SMBJ5.0A-SMBJ170A.pdf"
      footprint="smb"
      variant="tvs"
      pcbX={44}
      pcbY={-45.5}
      schX={3}
      schY={-2}
      schSectionName="Power"
    />
    <capacitor
      name="C1"
      manufacturerPartNumber="EEE-FK1V470P"
      datasheetUrl="https://industrial.panasonic.com/cdbs/www-data/pdf/RDE0000/ABA0000C1215.pdf"
      capacitance="47uF"
      maxVoltageRating="35V"
      polarized
      footprint="kicad:Capacitor_SMD/CP_Elec_6.3x5.8"
      pcbX={61}
      pcbY={-27}
      schX={3}
      schY={1.8}
      schSectionName="Power"
    />
    {/* Local eFuse bypass; 35 V is greater than twice the nominal 12 V rail. */}
    <capacitor
      name="C10"
      manufacturerPartNumber="CGA3E1X7R1V105K080AC"
      datasheetUrl="https://product.tdk.com/en/search/capacitor/ceramic/mlcc/info?part_no=CGA3E1X7R1V105K080AC"
      capacitance="1uF"
      maxVoltageRating="35V"
      footprint="0603"
      pcbX={48}
      pcbY={-34}
      pcbRotation={180}
      schX={4.5}
      schY={1.3}
      schSectionName="Power"
    />

    <chip
      name="U2"
      manufacturerPartNumber="TPS259470LRPWR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tps25947.pdf"
      footprint={<TiRpw0010aFootprint />}
      pinLabels={{
        pin1: "EN_UVLO",
        pin2: "OVLO",
        pin3: "AUXOFF",
        pin4: "FAULT_N",
        pin5: "IN",
        pin6: "OUT",
        pin7: "DVDT",
        pin8: "GND",
        pin9: "ILM",
        pin10: "ITIMER",
      }}
      noConnect={["AUXOFF"]}
      pcbX={49}
      pcbY={-37}
      schX={5}
      schY={0}
      schSectionName="Power"
    />
    <resistor name="R1" resistance="649k" tolerance="1%" footprint="0603" pcbX={47.5} pcbY={-32} schX={4} schY={2.5} schSectionName="Power" />
    <resistor name="R2" resistance="100k" tolerance="1%" footprint="0603" pcbX={44} pcbY={-32} schX={5} schY={2.5} schSectionName="Power" />
    <resistor name="R3" resistance="1.15M" tolerance="1%" footprint="0603" pcbX={51} pcbY={-32} schX={6} schY={2.5} schSectionName="Power" />
    <resistor name="R4" resistance="100k" tolerance="1%" footprint="0603" pcbX={54.5} pcbY={-32} schX={7} schY={2.5} schSectionName="Power" />
    <resistor name="R5" resistance="2.21k" tolerance="1%" footprint="0603" pcbX={45} pcbY={-40} schX={5} schY={-2.5} schSectionName="Power" />
    <capacitor
      name="C2"
      manufacturerPartNumber="GRM1885C1H332JA01D"
      datasheetUrl="https://www.murata.com/en-us/products/productdetail?partno=GRM1885C1H332JA01%23"
      capacitance="3.3nF"
      maxVoltageRating="50V"
      footprint="0603"
      pcbX={47.5}
      pcbY={-41.5}
      schX={6}
      schY={-2.5}
      schSectionName="Power"
    />
    <capacitor name="C3" capacitance="10nF" maxVoltageRating="16V" footprint="0603" pcbX={52.5} pcbY={-39.5} schX={7} schY={-2.5} schSectionName="Power" />
    <resistor name="R6" resistance="47k" footprint="0603" pcbX={44} pcbY={-35} schX={8} schY={-2.5} schSectionName="Power" />

    <chip
      name="U3"
      manufacturerPartNumber="LMR51430XDDCR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/lmr51430.pdf"
      footprint="sot23_6"
      pinLabels={{ pin1: "GND", pin2: "SW", pin3: "VIN", pin4: "FB", pin5: "EN", pin6: "CB" }}
      pcbX={38}
      pcbY={-37}
      schX={10}
      schY={0}
      schSectionName="Power"
    />
    <capacitor name="C4" manufacturerPartNumber="GRM21BR71H475KA73L" capacitance="4.7uF" maxVoltageRating="50V" footprint="0805" pcbX={42.5} pcbY={-38} schX={9} schY={2.5} schSectionName="Power" />
    <capacitor name="C5" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={38} pcbY={-33} schX={10} schY={-2.5} schSectionName="Power" />
    <inductor name="L1" manufacturerPartNumber="XAL7030-682ME" inductance="6.8uH" maxCurrentRating="4A" footprint="kicad:Inductor_SMD/L_Coilcraft_XAL7030-682" pcbX={31} pcbY={-37} schX={12} schY={0} schSectionName="Power" />
    <resistor name="R7" resistance="73.2k" tolerance="1%" footprint="0603" pcbX={32.5} pcbY={-32} schX={12} schY={2.5} schSectionName="Power" />
    <resistor name="R8" resistance="10k" tolerance="1%" footprint="0603" pcbX={29} pcbY={-32} schX={13} schY={2.5} schSectionName="Power" />
    <capacitor name="C6" manufacturerPartNumber="GRM21BR61A226ME44L" capacitance="22uF" maxVoltageRating="10V" footprint="0805" pcbX={25} pcbY={-35} schX={14} schY={-1.5} schSectionName="Power" />
    <capacitor name="C7" manufacturerPartNumber="GRM21BR61A226ME44L" capacitance="22uF" maxVoltageRating="10V" footprint="0805" pcbX={25} pcbY={-39} schX={15} schY={-1.5} schSectionName="Power" />

    <chip
      name="U4"
      manufacturerPartNumber="TPS62162DSGR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tps62162.pdf"
      footprint="kicad:Package_SON/Texas_DSG0008A_WSON-8-1EP_2x2mm_P0.5mm_EP0.9x1.6mm_ThermalVias"
      pinLabels={{ pin1: "PGND", pin2: "VIN", pin3: "EN", pin4: "AGND", pin5: "FB", pin6: "VOS", pin7: "SW", pin8: "PG", pin9: "EP" }}
      pcbX={17}
      pcbY={-37}
      schX={18}
      schY={0}
      schSectionName="Power"
    />
    <capacitor name="C8" manufacturerPartNumber="GRM21BR61A106KE19L" capacitance="10uF" maxVoltageRating="10V" footprint="0805" pcbX={21} pcbY={-37} schX={17} schY={2.5} schSectionName="Power" />
    <inductor name="L2" manufacturerPartNumber="SRN4018-2R2M" inductance="2.2uH" maxCurrentRating="1.5A" footprint="kicad:Inductor_SMD/L_Bourns-SRN4018" pcbX={11} pcbY={-37} schX={20} schY={0} schSectionName="Power" />
    <capacitor name="C9" manufacturerPartNumber="GRM21BR61A226ME44L" capacitance="22uF" maxVoltageRating="10V" footprint="0805" pcbX={5} pcbY={-37} schX={22} schY={-1.5} schSectionName="Power" />
    <resistor name="R9" resistance="100k" footprint="0603" pcbX={15} pcbY={-33} schX={20} schY={2.5} schSectionName="Power" />
    <resistor name="R10" resistance="1k" footprint="0603" pcbX={6} pcbY={-33} schX={22} schY={2.5} schSectionName="Power" />
    <led name="D2" color="green" footprint="0603" pcbX={2.5} pcbY={-33} schX={23} schY={2.5} schSectionName="Power" />

    <trace from=".J1 > .pin1" to=".F1 > .pin1" />
    <trace from=".J1 > .pin2" to="net.GND_CTRL" />
    <trace from=".F1 > .pin2" to="net.VIN_FUSED_RAW" />
    <trace from="net.VIN_FUSED_RAW" to=".D3 > .A" />
    <trace from=".D3 > .K" to="net.VIN_FUSED" />
    <trace from=".D1 > .K" to="net.VIN_FUSED" />
    <trace from=".D1 > .A" to="net.GND_CTRL" />
    <trace from=".C1 > .pin1" to="net.VIN_FUSED" />
    <trace from=".C1 > .pin2" to="net.GND_CTRL" />
    <trace from=".C10 > .pin1" to="net.VIN_FUSED" />
    <trace from=".C10 > .pin2" to="net.GND_CTRL" />
    <trace from=".U2 > .pin5" to="net.VIN_FUSED" />
    <trace from=".U2 > .pin6" to="net.VIN_PROTECTED" />
    <trace from=".U2 > .pin8" to="net.GND_CTRL" />
    <trace from=".R1 > .pin1" to="net.VIN_FUSED" />
    <trace from=".R1 > .pin2" to=".U2 > .pin1" />
    <trace from=".R2 > .pin1" to=".U2 > .pin1" />
    <trace from=".R2 > .pin2" to="net.GND_CTRL" />
    <trace from=".R3 > .pin1" to="net.VIN_FUSED" />
    <trace from=".R3 > .pin2" to=".U2 > .pin2" />
    <trace from=".R4 > .pin1" to=".U2 > .pin2" />
    <trace from=".R4 > .pin2" to="net.GND_CTRL" />
    <trace from=".R5 > .pin1" to=".U2 > .pin9" />
    <trace from=".R5 > .pin2" to="net.GND_CTRL" />
    <trace from=".C2 > .pin1" to=".U2 > .pin7" />
    <trace from=".C2 > .pin2" to="net.GND_CTRL" />
    <trace from=".C3 > .pin1" to=".U2 > .pin10" />
    <trace from=".C3 > .pin2" to="net.GND_CTRL" />
    <trace from=".R6 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R6 > .pin2" to=".U2 > .pin4" />
    <trace from=".U2 > .pin4" to="net.INPUT_FAULT_N" />

    <trace from=".U3 > .pin1" to="net.GND_CTRL" />
    <trace from=".U3 > .pin3" to="net.VIN_PROTECTED" />
    <trace from=".U3 > .pin5" to="net.VIN_PROTECTED" />
    <trace from=".C4 > .pin1" to="net.VIN_PROTECTED" />
    <trace from=".C4 > .pin2" to="net.GND_CTRL" />
    <trace from=".C5 > .pin1" to=".U3 > .pin6" />
    <trace from=".C5 > .pin2" to=".U3 > .pin2" />
    <trace from=".U3 > .pin2" to=".L1 > .pin1" />
    <trace from=".L1 > .pin2" to="net.V5_MAIN" />
    <trace from=".R7 > .pin1" to="net.V5_MAIN" />
    <trace from=".R7 > .pin2" to=".U3 > .pin4" />
    <trace from=".R8 > .pin1" to=".U3 > .pin4" />
    <trace from=".R8 > .pin2" to="net.GND_CTRL" />
    <trace from=".C6 > .pin1" to="net.V5_MAIN" />
    <trace from=".C6 > .pin2" to="net.GND_CTRL" />
    <trace from=".C7 > .pin1" to="net.V5_MAIN" />
    <trace from=".C7 > .pin2" to="net.GND_CTRL" />

    <trace from=".U4 > .pin1" to="net.GND_CTRL" />
    <trace from=".U4 > .pin2" to="net.V5_MAIN" />
    <trace from=".U4 > .pin3" to="net.V5_MAIN" />
    <trace from=".U4 > .pin4" to="net.GND_CTRL" />
    <trace from=".U4 > .pin5" to="net.GND_CTRL" />
    <trace from=".U4 > .pin6" to="net.V3V3_MAIN" />
    <trace from=".U4 > .pin7" to=".L2 > .pin1" />
    <trace from=".U4 > .pin9" to="net.GND_CTRL" />
    <trace from=".L2 > .pin2" to="net.V3V3_MAIN" />
    <trace from=".C8 > .pin1" to="net.V5_MAIN" />
    <trace from=".C8 > .pin2" to="net.GND_CTRL" />
    <trace from=".C9 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C9 > .pin2" to="net.GND_CTRL" />
    <trace from=".R9 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R9 > .pin2" to=".U4 > .pin8" />
    <trace from=".U4 > .pin8" to="net.V3V3_POWER_GOOD" />
    <trace from=".R10 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R10 > .pin2" to=".D2 > .pin1" />
    <trace from=".D2 > .pin2" to="net.GND_CTRL" />
  </>
)
