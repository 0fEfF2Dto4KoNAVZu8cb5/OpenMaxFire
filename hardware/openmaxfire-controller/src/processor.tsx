export const Processor = () => (
  <>
    <chip
      name="U1"
      manufacturerPartNumber="ESP32-S3-WROOM-1U-N16R2"
      datasheetUrl="https://documentation.espressif.com/esp32-s3-wroom-1_wroom-1u_datasheet_en.pdf"
      footprint="kicad:RF_Module/ESP32-S3-WROOM-1U"
      pinLabels={{
        pin1: "GND1",
        pin2: "3V3",
        pin3: "EN",
        pin4: "IO4_ESP_TX",
        pin5: "IO5_ESP_RX",
        pin6: "IO6_HEARTBEAT",
        pin7: "IO7_RELAY_REQ",
        pin8: "IO15_RESERVED",
        pin9: "IO16_RESERVED",
        pin10: "IO17_IOX_INT",
        pin11: "IO18_EXT_FAULT",
        pin12: "IO8_ONEWIRE",
        pin13: "IO19_USB_DN",
        pin14: "IO20_USB_DP",
        pin15: "IO3_STRAP",
        pin16: "IO46_STRAP",
        pin17: "IO9_I2C_SDA",
        pin18: "IO10_I2C_SCL",
        pin19: "IO11_EXP_ENABLE",
        pin20: "IO12_AUX_GPIO1",
        pin21: "IO13_MCLR_ASSERT",
        pin22: "IO14_HOPPER_SW",
        pin23: "IO21_USB_VBUS_N",
        pin24: "IO47_MODE_NORMAL",
        pin25: "IO48_MODE_FTDI",
        pin26: "IO45_STRAP",
        pin27: "IO0_BOOT",
        pin28: "IO35",
        pin29: "IO36",
        pin30: "IO37",
        pin31: "IO38",
        pin32: "IO39",
        pin33: "IO40",
        pin34: "IO41",
        pin35: "IO42",
        pin36: "IO44_RXD0",
        pin37: "IO43_TXD0",
        pin38: "IO2_STATUS",
        pin39: "IO1_AUX_ADC",
        pin40: "GND2",
        pin41: "GND_EP",
      }}
      noConnect={[
        "IO3_STRAP",
        "IO46_STRAP",
        "IO45_STRAP",
        "IO15_RESERVED",
        "IO16_RESERVED",
        "IO35",
        "IO36",
        "IO37",
        "IO38",
        "IO39",
        "IO40",
        "IO41",
        "IO42",
        "IO44_RXD0",
        "IO43_TXD0",
      ]}
      pcbX={44}
      pcbY={25}
      pcbRotation={180}
      schX={12}
      schY={0}
      schSectionName="Processor"
    />

    <resistor name="R101" resistance="10k" footprint="0603" pcbX={56} pcbY={19} schX={8.5} schY={-1.5} schSectionName="Processor" />
    <capacitor name="C101" capacitance="1uF" maxVoltageRating="10V" footprint="0603" pcbX={56} pcbY={22} schX={10} schY={-2.5} schSectionName="Processor" />
    <pushbutton
      name="SW101"
      manufacturerPartNumber="B3U-1000P"
      datasheetUrl="https://components.omron.com/sites/default/files/datasheet_pdf/A205-E1.pdf"
      footprint="kicad:Button_Switch_SMD/SW_SPST_B3U-1000P"
      pcbX={63}
      pcbY={20}
      schX={11.5}
      schY={-3.25}
      schSectionName="Processor"
    />
    <resistor name="R102" resistance="10k" footprint="0603" pcbX={59} pcbY={27} schX={14.5} schY={-1.5} schSectionName="Processor" />
    <pushbutton
      name="SW102"
      manufacturerPartNumber="B3U-1000P"
      datasheetUrl="https://components.omron.com/sites/default/files/datasheet_pdf/A205-E1.pdf"
      footprint="kicad:Button_Switch_SMD/SW_SPST_B3U-1000P"
      pcbX={64}
      pcbY={27}
      schX={14.5}
      schY={-2.5}
      schSectionName="Processor"
    />
    <capacitor name="C102" capacitance="10uF" maxVoltageRating="10V" footprint="0805" pcbX={57} pcbY={14} schX={11} schY={3} schSectionName="Processor" />
    <capacitor name="C103" capacitance="100nF" maxVoltageRating="16V" footprint="0603" pcbX={53.5} pcbY={14} schX={13} schY={3} schSectionName="Processor" />
    <resistor name="R103" resistance="1k" footprint="0603" pcbX={27.5} pcbY={17} schX={15} schY={0.8} schSectionName="Processor" />
    <led name="D101" color="green" footprint="0603" pcbX={24} pcbY={17} schX={16} schY={0.8} schSectionName="Processor" />
    {/* Hold UART TX at the idle-high state while the ESP32 boots. */}
    <resistor name="R104" resistance="100k" footprint="0603" pcbX={31} pcbY={21.5} schX={15} schY={2.2} schSectionName="Processor" />

    <trace from=".U1 > .pin1" to="net.GND_CTRL" />
    <trace from=".U1 > .pin40" to="net.GND_CTRL" />
    <trace from=".U1 > .pin41" to="net.GND_CTRL" />
    <trace from=".U1 > .pin2" to="net.V3V3_MAIN" />
    <trace from=".C102 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C102 > .pin2" to="net.GND_CTRL" />
    <trace from=".C103 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".C103 > .pin2" to="net.GND_CTRL" />

    <trace from=".R101 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R101 > .pin2" to=".U1 > .pin3" />
    <trace from=".C101 > .pin1" to=".U1 > .pin3" />
    <trace from=".C101 > .pin2" to="net.GND_CTRL" />
    <trace from=".SW101 > .pin1" to=".U1 > .pin3" />
    <trace from=".SW101 > .pin2" to="net.GND_CTRL" />

    <trace from=".R102 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R102 > .pin2" to=".U1 > .pin27" />
    <trace from=".SW102 > .pin1" to=".U1 > .pin27" />
    <trace from=".SW102 > .pin2" to="net.GND_CTRL" />

    <trace from=".U1 > .pin4" to="net.ESP_UART_TX" />
    <trace from=".U1 > .pin5" to="net.ESP_UART_RX" />
    <trace from=".U1 > .pin6" to="net.HEARTBEAT" />
    <trace from=".U1 > .pin7" to="net.RELAY_REQUEST" />
    <trace from=".U1 > .pin10" to="net.IOX_INTERRUPT_N" />
    <trace from=".U1 > .pin11" to="net.EXPANSION_FAULT_N" />
    <trace from=".U1 > .pin12" to="net.ONEWIRE_DATA" />
    <trace from=".U1 > .pin13" to="net.USB_DN_MCU" />
    <trace from=".U1 > .pin14" to="net.USB_DP_MCU" />
    <trace from=".U1 > .pin17" to="net.I2C_SDA" />
    <trace from=".U1 > .pin18" to="net.I2C_SCL" />
    <trace from=".U1 > .pin19" to="net.EXPANSION_ENABLE" />
    <trace from=".U1 > .pin20" to="net.AUX_GPIO1" />
    <trace from=".U1 > .pin21" to="net.ESP_MCLR_ASSERT" />
    <trace from=".U1 > .pin22" to="net.HOPPER_SWITCH" />
    <trace from=".U1 > .pin23" to="net.USB_VBUS_PRESENT_N" />
    <trace from=".U1 > .pin24" to="net.MODE_NORMAL_SENSE" />
    <trace from=".U1 > .pin25" to="net.MODE_FTDI_SENSE" />
    <trace from=".U1 > .pin39" to="net.AUX_ADC" />

    <trace from=".R104 > .pin1" to="net.V3V3_MAIN" />
    <trace from=".R104 > .pin2" to="net.ESP_UART_TX" />

    <trace from=".U1 > .pin38" to=".R103 > .pin1" />
    <trace from=".R103 > .pin2" to=".D101 > .pin1" />
    <trace from=".D101 > .pin2" to="net.GND_CTRL" />
  </>
)
