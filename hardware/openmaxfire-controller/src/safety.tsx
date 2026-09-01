import { CathodePin1Diode } from "./cathode-pin1-diode"
import { TiDcu0008aFootprint } from "./ti-dcu0008a-footprint"

/**
 * Independent dead-man and fail-back thermostat transfer.
 *
 * K501 is deliberately energized only for the healthy automated state.  Its
 * de-energized (NC) contacts reconnect the original wall thermostat.  Three
 * independent conditions are in the coil path:
 *
 *   1. SW301 physically supplies KTH_COIL_5V only in NORMAL mode.
 *   2. Q501 requires an explicit ESP32 RELAY_REQUEST.
 *   3. Q502 requires HB_OK from the hardware watchdog/latch.
 *
 * J502 is shipped with a fitted normally-closed shunt.  Removing that shunt,
 * opening a remote force-backup contact, loss of power, reset, service mode,
 * or stale heartbeat all release K501 without firmware cooperation.
 *
 * The K501 contacts and J501 thermostat wiring are a floating dry-contact
 * domain.  Never connect them to GND_CTRL or GND_TGT.
 */

const Tq2RelayFootprint = () => (
  <footprint insertionDirection="from_above" cutoutApertureDirection="from_above">
    {/**
     * Panasonic TQ2 through-hole, bottom-view land pattern.
     * Two rows are 7.62 mm apart; pin columns are on 2.54 mm pitch.
     *
     * PRODUCTION GATE: compare pin numbering, bottom-view orientation, hole
     * size, and body courtyard against the current Panasonic TQ datasheet and
     * a received TQ2-5V before releasing fabrication outputs.
     */}
    <platedhole portHints={["pin1"]} pcbX={-5.08} pcbY={3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin2"]} pcbX={-2.54} pcbY={3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin3"]} pcbX={0} pcbY={3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin4"]} pcbX={2.54} pcbY={3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin5"]} pcbX={5.08} pcbY={3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin10"]} pcbX={-5.08} pcbY={-3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin9"]} pcbX={-2.54} pcbY={-3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin8"]} pcbX={0} pcbY={-3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin7"]} pcbX={2.54} pcbY={-3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <platedhole portHints={["pin6"]} pcbX={5.08} pcbY={-3.81} shape="circle" holeDiameter={1} outerDiameter={1.8} />
    <silkscreencircle pcbX={-5.08} pcbY={3.81} radius={1.35} strokeWidth={0.2} />
    <silkscreenrect pcbX={0} pcbY={0} width={14} height={9} strokeWidth={0.2} />
    <courtyardrect pcbX={0} pcbY={0} width={15} height={10} strokeWidth={0.1} />
  </footprint>
)

const TiDrb0008aFootprint = () => (
  <footprint>
    {/**
     * TI DRB0008A example board layout, package drawing 4218875/A:
     * 0.65 mm pitch, 2.8 mm opposing-row center distance, eight
     * 0.60 x 0.31 mm lands, and a 1.50 x 1.75 mm exposed-pad land.
     */}
    <smtpad portHints={["pin1"]} pcbX={-1.4} pcbY={0.975} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin2"]} pcbX={-1.4} pcbY={0.325} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin3"]} pcbX={-1.4} pcbY={-0.325} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin4"]} pcbX={-1.4} pcbY={-0.975} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin5"]} pcbX={1.4} pcbY={-0.975} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin6"]} pcbX={1.4} pcbY={-0.325} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin7"]} pcbX={1.4} pcbY={0.325} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin8"]} pcbX={1.4} pcbY={0.975} width={0.6} height={0.31} shape="rect" />
    <smtpad portHints={["pin9"]} pcbX={0} pcbY={0} width={1.5} height={1.75} shape="rect" />
    <silkscreenrect pcbX={0} pcbY={0} width={3.2} height={3.2} strokeWidth={0.15} />
    <courtyardrect pcbX={0} pcbY={0} width={4} height={4} strokeWidth={0.1} />
  </footprint>
)

export const SafetyAndThermostat = () => (
  <>
    {/*
     * 3.069 V supervisor plus extended window watchdog. C501 is a specified
     * 22 nF +/-5% C0G part, giving 1.758 s nominal and approximately
     * 1.51-2.02 s including capacitor and TPS3851 timing tolerances. SET1
     * selects watchdog operation; /MR is held inactive.
     */}
    <chip
      name="U501"
      manufacturerPartNumber="TPS3851H33EDRBR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/tps3851.pdf"
      footprint={<TiDrb0008aFootprint />}
      pinLabels={{
        pin1: "VDD",
        pin2: "CWD",
        pin3: "MR_N",
        pin4: "GND",
        pin5: "SET1",
        pin6: "WDI",
        pin7: "WDO_N",
        pin8: "RESET_N",
        pin9: "EP",
      }}
      pcbX={30}
      pcbY={-8}
      schX={3}
      schY={0}
      schSectionName="Safety"
    />
    <capacitor
      name="C501"
      manufacturerPartNumber="C0805C223J5GACTU"
      datasheetUrl="https://yageogroup.com/download/specsheet/C0805C223J5GACTU"
      capacitance="22nF"
      maxVoltageRating="50V"
      footprint="0805"
      pcbX={28}
      pcbY={-12}
      schX={1}
      schY={2}
      schSectionName="Safety"
    />
    <capacitor
      name="C502"
      capacitance="100nF"
      maxVoltageRating="16V"
      footprint="0603"
      pcbX={26}
      pcbY={-8}
      schX={4}
      schY={2}
      schSectionName="Safety"
    />
    <resistor name="R501" resistance="10k" footprint="0603" pcbX={28} pcbY={-4.5} schX={5} schY={2} schSectionName="Safety" />

    {/* Open-drain RESET and WDO share WD_CLEAR_N.  Either can clear the latch. */}
    <chip
      name="U502"
      manufacturerPartNumber="SN74LVC1G08DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc1g08.pdf"
      footprint="sot23_5"
      pinLabels={{ pin1: "A", pin2: "B", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      pcbX={35}
      pcbY={-7}
      schX={8}
      schY={0}
      schSectionName="Safety"
    />
    <capacitor name="C503" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={39} pcbY={-7} schX={8} schY={2} schSectionName="Safety" />

    {/**
     * U503 captures the watchdog's short active-low fault pulse.  /CLR is also
     * held low whenever RUN_MODE is false, so entering service or OFFLINE
     * immediately drops HB_OK.  A fresh heartbeat edge is required after
     * returning to NORMAL; a stale high level cannot re-arm the relay.
     */}
    <chip
      name="U503"
      manufacturerPartNumber="SN74LVC1G74DCUR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf"
      footprint={<TiDcu0008aFootprint />}
      pinLabels={{
        pin1: "CLK",
        pin2: "D",
        pin3: "Q_N",
        pin4: "GND",
        pin5: "Q",
        pin6: "CLR_N",
        pin7: "PRE_N",
        pin8: "VCC",
      }}
      noConnect={["Q_N"]}
      pcbX={34.5}
      pcbY={-13}
      schX={12}
      schY={0}
      schSectionName="Safety"
    />
    <capacitor name="C504" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={34.5} pcbY={-16.5} schX={12} schY={2} schSectionName="Safety" />
    {/**
     * U504 inverts the heartbeat with a Schmitt input. The watchdog and latch
     * are therefore both qualified by the same ESP falling edge: falling WDI
     * services U501 while the resulting rising HEARTBEAT_ARM_CLK arms U503.
     * R504 holds WDI low through reset or an absent processor.
     */}
    <chip
      name="U504"
      manufacturerPartNumber="SN74LVC1G14DBVR"
      datasheetUrl="https://www.ti.com/lit/ds/symlink/sn74lvc1g14.pdf"
      footprint="sot23_5"
      pinLabels={{ pin1: "NC", pin2: "A", pin3: "GND", pin4: "Y", pin5: "VCC" }}
      noConnect={["NC"]}
      pcbX={22}
      pcbY={-15}
      schX={12}
      schY={-4}
      schSectionName="Safety"
    />
    <capacitor name="C505" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={18} pcbY={-15} schX={14} schY={-5} schSectionName="Safety" />
    <resistor name="R504" resistance="100k" footprint="0603" pcbX={22} pcbY={-11} schX={9} schY={-4} schSectionName="Safety" />
    <resistor name="R502" resistance="100k" footprint="0603" pcbX={45.5} pcbY={-16} schX={15} schY={2} schSectionName="Safety" />
    <resistor name="R503" resistance="100k" footprint="0603" pcbX={40.5} pcbY={-16} schX={17} schY={2} schSectionName="Safety" />

    {/*
     * Open-fail force-backup loop. Populate a shorting plug for normal use, or
     * replace it with a normally-closed dry contact. Opening the loop removes
     * relay-coil power regardless of watchdog, GPIO, or MOSFET failure.
     */}
    <connector
      name="J502"
      manufacturerPartNumber="B2B-XH-A(LF)(SN)"
      footprint="kicad:Connector_JST/JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical"
      pinLabels={{ pin1: "NORMAL_FEED", pin2: "FORCE_BACKUP_RETURN" }}
      pcbX={32}
      pcbY={-22}
      pcbRotation={0}
      schX={19}
      schY={3}
      schSectionName="Safety"
    />

    {/* Panasonic TQ2-5V (legacy order code ATQ209), non-latching DPDT. */}
    <chip
      name="K501"
      manufacturerPartNumber="TQ2-5V"
      datasheetUrl="https://industry.panasonic.com/global/en/products/control/relay/signal/tq"
      footprint={<Tq2RelayFootprint />}
      pinLabels={{
        pin1: "COIL_POS",
        pin2: "NC_A",
        pin3: "COM_A",
        pin4: "NO_A",
        pin5: "UNUSED_5",
        pin6: "UNUSED_6",
        pin7: "NO_B",
        pin8: "COM_B",
        pin9: "NC_B",
        pin10: "COIL_NEG",
      }}
      noConnect={["UNUSED_5", "UNUSED_6"]}
      pcbX={55}
      pcbY={-9}
      schX={24}
      schY={0}
      schSectionName="Safety"
    />
    <CathodePin1Diode
      name="D501"
      manufacturerPartNumber="1N4148W-7-F"
      datasheetUrl="https://www.diodes.com/assets/Datasheets/ds30086.pdf"
      footprint="sod123"
      pcbX={55}
      pcbY={-16}
      schX={23}
      schY={-3}
      schSectionName="Safety"
    />

    {/* Two series low-side MOSFETs implement RELAY_REQUEST AND HB_OK. */}
    <chip
      name="Q501"
      manufacturerPartNumber="BSS138BK,215"
      footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
      pcbX={45}
      pcbY={-11}
      schX={29}
      schY={-1}
      schSectionName="Safety"
    />
    <chip
      name="Q502"
      manufacturerPartNumber="BSS138BK,215"
      footprint="sot23"
      pinLabels={{ pin1: "G", pin2: "S", pin3: "D" }}
      pcbX={40.5}
      pcbY={-11}
      schX={33}
      schY={-1}
      schSectionName="Safety"
    />
    {/**
     * One keyed four-wire harness contains both stove-input and backup-
     * thermostat pairs.  The passive bypass accessory joins 1-3 and 2-4,
     * restoring the original thermostat path with the PCB entirely absent.
     */}
    <connector
      name="J501"
      manufacturerPartNumber="B4P-VH-B(LF)(SN)"
      footprint="kicad:Connector_JST/JST_VH_B4P-VH-B_1x04_P3.96mm_Vertical"
      pinLabels={{
        pin1: "STOVE_TH_A",
        pin2: "STOVE_TH_B",
        pin3: "BACKUP_TH_A",
        pin4: "BACKUP_TH_B",
      }}
      pcbX={68}
      pcbY={-8}
      pcbRotation={90}
      schX={39}
      schY={0}
      schSectionName="Safety"
    />

    {/* TPS3851 power, timing, watchdog input, and wired-OR fault output. */}
    <trace from=".U501 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".U501 > .pin2" to=".C501 > .pin1" />
    <trace from=".C501 > .pin2" to="net.GND_CTRL" />
    <trace from=".U501 > .pin3" to="net.V3V3_MAIN" />
    <trace from=".U501 > .pin4" to="net.GND_CTRL" />
    <trace from=".U501 > .pin5" to="net.V3V3_MAIN" />
    <trace from=".U501 > .pin6" to="net.HEARTBEAT" />
    <trace from=".U501 > .pin7" to="net.WD_CLEAR_N" />
    <trace from=".U501 > .pin8" to="net.WD_CLEAR_N" />
    <trace from=".U501 > .pin9" to="net.GND_CTRL" />
    <trace from=".C502 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C502 > .pin2" to="net.GND_CTRL" />
    <trace from=".R501 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R501 > .pin2" to="net.WD_CLEAR_N" />
    <trace from=".R504 > .pin1" to="net.HEARTBEAT" />
    <trace from=".R504 > .pin2" to="net.GND_CTRL" />
    <trace from=".U504 > .pin2" to="net.HEARTBEAT" />
    <trace from=".U504 > .pin3" to="net.GND_CTRL" />
    <trace from=".U504 > .pin4" to="net.HEARTBEAT_ARM_CLK" />
    <trace from=".U504 > .pin5" to="net.V3V3_MAIN" />
    <trace from=".C505 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C505 > .pin2" to="net.GND_CTRL" />

    {/* HB_CLEAR_N = WD_CLEAR_N AND RUN_MODE. */}
    <trace from=".U502 > .pin1" to="net.WD_CLEAR_N" />
    <trace from=".U502 > .pin2" to="net.RUN_MODE" />
    <trace from=".U502 > .pin3" to="net.GND_CTRL" />
    <trace from=".U502 > .pin4" to="net.HB_CLEAR_N" />
    <trace from=".U502 > .pin5" to="net.V3V3_MAIN" />
    <trace from=".C503 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C503 > .pin2" to="net.GND_CTRL" />

    {/* Sticky healthy latch: the first watchdog-valid falling edge sets Q. */}
    <trace from=".U503 > .pin1" to="net.HEARTBEAT_ARM_CLK" />
    <trace from=".U503 > .pin2" to="net.V3V3_MAIN" />
    <trace from=".U503 > .pin4" to="net.GND_CTRL" />
    <trace from=".U503 > .pin5" to="net.HB_OK" />
    <trace from=".U503 > .pin6" to="net.HB_CLEAR_N" />
    <trace from=".U503 > .pin7" to="net.V3V3_MAIN" />
    <trace from=".U503 > .pin8" to="net.V3V3_MAIN" />
    <trace from=".C504 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C504 > .pin2" to="net.GND_CTRL" />

    {/* Gate pulldowns make both MOSFETs default-off during reset or removal. */}
    <trace from=".R502 > .pin1" to="net.RELAY_REQUEST" />
    <trace from=".R502 > .pin2" to="net.GND_CTRL" />
    <trace from=".R503 > .pin1" to="net.HB_OK" />
    <trace from=".R503 > .pin2" to="net.GND_CTRL" />
    <trace from=".Q501 > .pin1" to="net.RELAY_REQUEST" />
    <trace from=".Q501 > .pin3" to="net.RELAY_COIL_LOW" />
    <trace from=".Q501 > .pin2" to="net.RELAY_DRIVER_MID" />
    <trace from=".Q502 > .pin1" to="net.HB_OK" />
    <trace from=".Q502 > .pin3" to="net.RELAY_DRIVER_MID" />
    <trace from=".Q502 > .pin2" to="net.GND_CTRL" />

    {/* Physical mode feed, force-backup loop, coil, and flyback clamp. */}
    <trace from="net.KTH_COIL_5V" to=".J502 > .pin1" />
    <trace from=".J502 > .pin2" to="net.FORCE_BACKUP_RETURN" />
    <trace from="net.FORCE_BACKUP_RETURN" to=".K501 > .pin1" />
    <trace from=".K501 > .pin10" to="net.RELAY_COIL_LOW" />
    <trace from=".D501 > .K" to="net.FORCE_BACKUP_RETURN" />
    <trace from=".D501 > .A" to="net.RELAY_COIL_LOW" />

    {/*
     * Released: COM_A-NC_A and COM_B-NC_B reconnect the wall thermostat.
     * Energized: both COMs meet through the two NO contacts at TH_CALL_SHORT.
     */}
    <trace from=".K501 > .pin3" to="net.STOVE_TH_A" />
    <trace from=".K501 > .pin2" to="net.BACKUP_TH_A" />
    <trace from=".K501 > .pin4" to="net.TH_CALL_SHORT" />
    <trace from=".K501 > .pin8" to="net.STOVE_TH_B" />
    <trace from=".K501 > .pin9" to="net.BACKUP_TH_B" />
    <trace from=".K501 > .pin7" to="net.TH_CALL_SHORT" />
    <trace from=".J501 > .pin1" to="net.STOVE_TH_A" />
    <trace from=".J501 > .pin2" to="net.STOVE_TH_B" />
    <trace from=".J501 > .pin3" to="net.BACKUP_TH_A" />
    <trace from=".J501 > .pin4" to="net.BACKUP_TH_B" />
  </>
)
