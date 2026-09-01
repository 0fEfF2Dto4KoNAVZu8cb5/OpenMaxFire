/**
 * Production and field-service probe access.
 *
 * These are exposed copper pads only: they do not add LEDs, dividers, clamps,
 * or other loading to the signals under test.  Controller-domain and target-
 * domain probes are physically separated by the isolation keepout.
 */

type Probe = {
  name: string
  net: string
  label: string
  pcbX: number
  pcbY: number
  schX: number
  schY: number
}

const controllerProbes: Probe[] = [
  { name: "TP101", net: "VIN_FUSED", label: "VFUS", pcbX: 0, pcbY: 13, schX: 0, schY: 0 },
  { name: "TP102", net: "VIN_PROTECTED", label: "VPRO", pcbX: 4, pcbY: 13, schX: 2, schY: 0 },
  { name: "TP103", net: "V5_MAIN", label: "5V", pcbX: 8, pcbY: 13, schX: 4, schY: 0 },
  { name: "TP104", net: "V3V3_MAIN", label: "3V3", pcbX: 12, pcbY: 13, schX: 6, schY: 0 },
  { name: "TP105", net: "SERVICE_5V", label: "S5", pcbX: 16, pcbY: 13, schX: 8, schY: 0 },
  { name: "TP106", net: "SERVICE_3V3", label: "S3", pcbX: 20, pcbY: 13, schX: 10, schY: 0 },
  { name: "TP107", net: "FTDI_5V_LIMITED", label: "F5", pcbX: 24, pcbY: 13, schX: 12, schY: 0 },
  { name: "TP108", net: "EXP_3V3", label: "EX3", pcbX: 28, pcbY: 13, schX: 14, schY: 0 },

  { name: "TP109", net: "ESP_UART_TX", label: "ETX", pcbX: 0, pcbY: 8, schX: 0, schY: -4 },
  { name: "TP110", net: "ESP_UART_RX", label: "ERX", pcbX: 4, pcbY: 8, schX: 2, schY: -4 },
  { name: "TP111", net: "SERVICE_TX_SELECTED", label: "STX", pcbX: 8, pcbY: 8, schX: 4, schY: -4 },
  { name: "TP112", net: "SERVICE_RX_ISOLATED", label: "SRX", pcbX: 12, pcbY: 8, schX: 6, schY: -4 },
  { name: "TP113", net: "RUN_MODE", label: "RUN", pcbX: 16, pcbY: 8, schX: 8, schY: -4 },
  { name: "TP114", net: "FTDI_VALID", label: "FTD", pcbX: 20, pcbY: 8, schX: 10, schY: -4 },
  { name: "TP115", net: "HEARTBEAT", label: "HB", pcbX: 24, pcbY: 8, schX: 12, schY: -4 },
  { name: "TP116", net: "WD_CLEAR_N", label: "WDC", pcbX: 28, pcbY: 8, schX: 14, schY: -4 },

  { name: "TP117", net: "HB_OK", label: "HBO", pcbX: 0, pcbY: 3, schX: 0, schY: -8 },
  { name: "TP118", net: "RELAY_REQUEST", label: "REQ", pcbX: 4, pcbY: 3, schX: 2, schY: -8 },
  { name: "TP119", net: "KTH_COIL_5V", label: "K5", pcbX: 8, pcbY: 3, schX: 4, schY: -8 },
  { name: "TP120", net: "RELAY_COIL_LOW", label: "KLO", pcbX: 12, pcbY: 3, schX: 6, schY: -8 },
  { name: "TP121", net: "INPUT_FAULT_N", label: "IFL", pcbX: 16, pcbY: 3, schX: 8, schY: -8 },
  { name: "TP122", net: "EXPANSION_FAULT_N", label: "EFL", pcbX: 20, pcbY: 3, schX: 10, schY: -8 },
  { name: "TP123", net: "USB_VBUS_PRESENT_N", label: "USB", pcbX: 24, pcbY: 3, schX: 12, schY: -8 },
  { name: "TP124", net: "GND_CTRL", label: "GND", pcbX: 28, pcbY: 3, schX: 14, schY: -8 },
]

const targetProbes: Probe[] = [
  { name: "TP201", net: "GND_TGT", label: "TG", pcbX: -62, pcbY: -5, schX: 0, schY: -12 },
  { name: "TP202", net: "VTGT_RAW", label: "VR", pcbX: -58, pcbY: -5, schX: 2, schY: -12 },
  { name: "TP203", net: "VTGT_PROTECTED", label: "VP", pcbX: -54, pcbY: -5, schX: 4, schY: -12 },
  { name: "TP204", net: "VTGT_GOOD", label: "VG", pcbX: -50, pcbY: -5, schX: 6, schY: -12 },
  { name: "TP205", net: "J3_STOVE_RX", label: "RX", pcbX: -46, pcbY: -5, schX: 8, schY: -12 },
  { name: "TP206", net: "J3_STOVE_TX", label: "TX", pcbX: -42, pcbY: -5, schX: 10, schY: -12 },
  { name: "TP207", net: "J5_MCLR_VPP", label: "VPP", pcbX: -38, pcbY: -5, schX: 12, schY: -12 },
  { name: "TP208", net: "J5_PGD", label: "PGD", pcbX: -34, pcbY: -5, schX: 14, schY: -12 },
  { name: "TP209", net: "J5_PGC", label: "PGC", pcbX: -30, pcbY: -5, schX: 16, schY: -12 },
]

const ProbePad = ({ name, net, label, pcbX, pcbY, schX, schY }: Probe) => (
  <>
    <testpoint
      name={name}
      footprintVariant="pad"
      padShape="circle"
      padDiameter="1.6mm"
      connections={{ pin1: `net.${net}` }}
      pcbX={pcbX}
      pcbY={pcbY}
      schX={schX}
      schY={schY}
      schSectionName="TestPoints"
    />
    <silkscreentext
      text={label}
      pcbX={pcbX}
      pcbY={pcbY + 1.55}
      fontSize="0.55mm"
      anchorAlignment="center"
      layer="top"
    />
  </>
)

export const TestPoints = () => (
  <>
    {controllerProbes.map((probe) => <ProbePad key={probe.name} {...probe} />)}
    {targetProbes.map((probe) => <ProbePad key={probe.name} {...probe} />)}
  </>
)
