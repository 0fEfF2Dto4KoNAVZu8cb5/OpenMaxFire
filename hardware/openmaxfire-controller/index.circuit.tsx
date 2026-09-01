import { PermanentPower } from "./src/power"
import { Processor } from "./src/processor"
import { UsbDevicePort } from "./src/usb"
import { ModeAndService } from "./src/mode-service"
import { SafetyAndThermostat } from "./src/safety"
import { TargetService } from "./src/target-service"
import { Expansion } from "./src/expansion"
import { TestPoints } from "./src/testpoints"

/**
 * OpenMaxFire full controller, Rev A.
 *
 * The board is intentionally split into a permanently powered controller side
 * and a stove-target side. GND_CTRL and GND_TGT must never be joined on the
 * PCB: all J3 traffic crosses the reinforced digital isolator in the target
 * service block.
 */
export default () => (
  <board
    title="OpenMaxFire Full Controller Rev A"
    width="140mm"
    height="100mm"
    layers={4}
    thickness="1.6mm"
    borderRadius="2mm"
    solderMaskColor="green"
    silkscreenColor="white"
    routingDisabled
    nominalTraceWidth="0.25mm"
    defaultTraceWidth="0.25mm"
    minTraceWidth="0.20mm"
    minTraceToPadEdgeClearance="0.20mm"
    minPadEdgeToPadEdgeClearance="0.20mm"
    minViaEdgeToPadEdgeClearance="0.20mm"
    minViaHoleEdgeToViaHoleEdgeClearance="0.20mm"
    minPlatedHoleDrillEdgeToDrillEdgeClearance="0.25mm"
    minBoardEdgeClearance="0.30mm"
    minViaHoleDiameter="0.30mm"
    minViaPadDiameter="0.60mm"
    allowBlindAndBuriedVias={false}
    isViaInPadAllowed={false}
  >
    <schematicsection name="Power" displayName="Protected 12 V Input and Main Rails" />
    <schematicsection name="Processor" displayName="ESP32-S3 Supervisory Controller" />
    <schematicsection name="USB" displayName="Native USB-C Device Port" />
    <schematicsection name="ModeControl" displayName="Fail-safe Operating Mode Selection" />
    <schematicsection name="J3Service" displayName="Isolated J3 and FTDI Service Interface" />
    <schematicsection name="Safety" displayName="Hardware Dead-man and Thermostat Transfer" />
    <schematicsection name="Expansion" displayName="Protected Sensors and Future I/O" />
    <schematicsection name="TestPoints" displayName="Production and Service Test Points" />

    {/* Permanently powered controller domain. */}
    <net name="GND_CTRL" isGroundNet nominalTraceWidth="0.40mm" />
    <net name="VIN_FUSED_RAW" isPowerNet nominalTraceWidth="1.00mm" />
    <net name="VIN_FUSED" isPowerNet nominalTraceWidth="1.00mm" />
    <net name="VIN_PROTECTED" isPowerNet nominalTraceWidth="1.00mm" />
    <net name="V5_MAIN" isPowerNet nominalTraceWidth="0.80mm" />
    <net name="V3V3_MAIN" isPowerNet nominalTraceWidth="0.50mm" />
    <net name="EXP_3V3" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="EXP_IO_OE_N" />
    <net name="EXP_RAIL_GOOD" />
    <net name="EXP_IO_GATE_MID" />
    <net name="EXP_IO_GATE_ENABLE" />
    <net name="INPUT_FAULT_N" />
    <net name="V3V3_POWER_GOOD" />

    {/* ESP32 signals. Strap pins are deliberately not used by safety logic. */}
    <net name="ESP_UART_TX" />
    <net name="ESP_UART_RX" />
    <net name="HEARTBEAT" />
    <net name="HEARTBEAT_ARM_CLK" />
    <net name="RELAY_REQUEST" />
    <net name="IOX_INTERRUPT_N" />
    <net name="EXPANSION_ENABLE" />
    <net name="EXPANSION_FAULT_N" />
    <net name="ONEWIRE_DATA" />
    <net name="USB_DN_MCU" />
    <net name="USB_DP_MCU" />
    <net name="USB_VBUS_GATE" />
    <net name="USB_VBUS_PRESENT_N" />
    <net name="I2C_SDA" />
    <net name="I2C_SCL" />
    <net name="AUX_ADC" />
    <net name="AUX_GPIO1" />
    <net name="AUX_GPIO2" />
    <net name="HOPPER_SWITCH" />
    <net name="MODE_NORMAL_SENSE" />
    <net name="MODE_FTDI_SENSE" />
    <net name="ESP_MCLR_ASSERT" />

    {/* Hardware-derived mode and safety state. */}
    <net name="RUN_RAW" />
    <net name="FTDI_RAW" />
    <net name="MODE_SOURCE_OK" />
    <net name="RUN_PRE" />
    <net name="FTDI_PRE" />
    <net name="RUN_INHIBIT_N" />
    <net name="FTDI_INHIBIT_N" />
    <net name="UART_CONNECT" />
    <net name="RUN_MODE" />
    <net name="FTDI_VALID" />
    <net name="HB_OK" />
    <net name="WD_CLEAR_N" />
    <net name="HB_CLEAR_N" />
    <net name="KTH_COIL_5V" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="FORCE_BACKUP_RETURN" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="RELAY_COIL_LOW" />
    <net name="RELAY_DRIVER_MID" />

    {/* Floating thermostat dry-contact domain. Never tie these to a ground. */}
    <net name="STOVE_TH_A" />
    <net name="STOVE_TH_B" />
    <net name="BACKUP_TH_A" />
    <net name="BACKUP_TH_B" />
    <net name="TH_CALL_SHORT" />

    {/* FTDI/service power stays current limited and cannot power the ESP. */}
    <net name="FTDI_VCC_CABLE" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="FTDI_5V_RAW" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="FTDI_5V_LIMITED" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="FTDI_5V_MODE" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="FTDI_POWER_FAULT_N" />
    <net name="SERVICE_5V" isPowerNet nominalTraceWidth="0.40mm" />
    <net name="SERVICE_3V3" isPowerNet nominalTraceWidth="0.30mm" />
    <net name="SERVICE_TX_SELECTED" />
    <net name="SERVICE_RX_ISOLATED" />
    <net name="FTDI_TX" />
    <net name="FTDI_RX" />
    <net name="FTDI_RTS_N" />

    {/* Stove target domain: powered only from verified J5 VDD/VSS. */}
    <net name="GND_TGT" isGroundNet nominalTraceWidth="0.30mm" />
    <net name="VTGT_RAW" isPowerNet nominalTraceWidth="0.30mm" />
    <net name="VTGT_PROTECTED" isPowerNet nominalTraceWidth="0.30mm" />
    <net name="VTGT_GOOD" />
    <net name="J3_STOVE_RX" />
    <net name="J3_STOVE_TX" />
    <net name="J5_MCLR_VPP" />
    <net name="J5_PGD" />
    <net name="J5_PGC" />

    {/*
     * Split internal planes preserve the reinforced isolation barrier. The
     * polygons stop at the keepout edges; the solver additionally applies the
     * explicit 0.30 mm margins below.
     */}
    <copperpour
      name="INNER1_CONTROLLER_GND"
      layer="inner1"
      connectsTo="net.GND_CTRL"
      outline={[{ x: -19, y: -47.5 }, { x: 69.5, y: -47.5 }, { x: 69.5, y: 47.5 }, { x: -19, y: 47.5 }, { x: -19, y: -47.5 }]}
      clearance="0.20mm"
      padMargin="0.20mm"
      traceMargin="0.20mm"
      boardEdgeMargin="0.30mm"
      cutoutMargin="0.30mm"
      unbroken
      useThermalReliefs
    />
    <copperpour
      name="INNER1_TARGET_GND"
      layer="inner1"
      connectsTo="net.GND_TGT"
      outline={[{ x: -69.5, y: -47.5 }, { x: -27, y: -47.5 }, { x: -27, y: 47.5 }, { x: -69.5, y: 47.5 }, { x: -69.5, y: -47.5 }]}
      clearance="0.20mm"
      padMargin="0.20mm"
      traceMargin="0.20mm"
      boardEdgeMargin="0.30mm"
      cutoutMargin="0.30mm"
      unbroken
      useThermalReliefs
    />
    <copperpour
      name="INNER2_CONTROLLER_3V3"
      layer="inner2"
      connectsTo="net.V3V3_MAIN"
      outline={[{ x: -19, y: -47.5 }, { x: 69.5, y: -47.5 }, { x: 69.5, y: 47.5 }, { x: -19, y: 47.5 }, { x: -19, y: -47.5 }]}
      clearance="0.20mm"
      padMargin="0.20mm"
      traceMargin="0.20mm"
      boardEdgeMargin="0.30mm"
      cutoutMargin="0.30mm"
      unbroken
      useThermalReliefs
    />
    <copperpour
      name="INNER2_TARGET_POWER"
      layer="inner2"
      connectsTo="net.VTGT_PROTECTED"
      outline={[{ x: -69.5, y: -47.5 }, { x: -27, y: -47.5 }, { x: -27, y: 47.5 }, { x: -69.5, y: 47.5 }, { x: -69.5, y: -47.5 }]}
      clearance="0.20mm"
      padMargin="0.20mm"
      traceMargin="0.20mm"
      boardEdgeMargin="0.30mm"
      cutoutMargin="0.30mm"
      unbroken
      useThermalReliefs
    />

    {/*
     * Schematic-only offsets keep the eight functional sheets readable while
     * preserving every explicitly assigned PCB coordinate.
     */}
    <group pcbX={0} pcbY={0} schX={0} schY={0}><PermanentPower /></group>
    <group pcbX={0} pcbY={0} schX={24} schY={0}><Processor /></group>
    <group pcbX={0} pcbY={0} schX={25} schY={0}><UsbDevicePort /></group>
    <group pcbX={0} pcbY={0} schX={2} schY={-16}><ModeAndService /></group>
    <group pcbX={0} pcbY={0} schX={51} schY={-16}><SafetyAndThermostat /></group>
    <group pcbX={0} pcbY={0} schX={-3} schY={-52}><TargetService /></group>
    <group pcbX={0} pcbY={0} schX={33} schY={-36}><Expansion /></group>
    <group pcbX={0} pcbY={0} schX={65} schY={-36}><TestPoints /></group>

    {/* M3 mounting holes are kept outside all functional domains. */}
    <hole name="H1" diameter="3.2mm" pcbX={-65} pcbY={-45} />
    <hole name="H2" diameter="3.2mm" pcbX={65} pcbY={-45} />
    <hole name="H3" diameter="3.2mm" pcbX={-65} pcbY={45} />
    <hole name="H4" diameter="3.2mm" pcbX={65} pcbY={45} />
  </board>
)
