# ESP32-S3 firmware pin map

Status: Rev A hardware/firmware contract. This map follows
[`src/processor.tsx`](../src/processor.tsx) and the connected functional blocks.
It is not evidence that the board is released for fabrication or stove use.

The module is `ESP32-S3-WROOM-1U-N16R2`. GPIO numbers below are ESP32 GPIO
numbers, not module land numbers.

## Connected GPIO

| GPIO | Hardware net/function | Direction | Active state and firmware rule |
| ---: | --- | --- | --- |
| 0 | BOOT pushbutton | strap/input | 10 kohm pull-up; button pulls low. Do not repurpose. |
| 1 | `AUX_ADC` / ADC1_CH0 | analog input | J603 pin 3 is 0-3.3 V only. A 20 kohm/100 kohm divider produces 5/6 of connector voltage and C606 provides 100 nF filtering. Recover connector voltage by multiplying the calibrated ADC-node voltage by 6/5. |
| 2 | green status LED | output | High lights D101. Keep diagnostic only; never use as a safety indication. |
| 4 | `ESP_UART_TX` | output | 5 V-target service UART transmit before guarded source select. A 100 kohm pull-up holds idle high through boot. 9600-8-N-1 baseline. |
| 5 | `ESP_UART_RX` | input | Isolated service UART receive, enabled for the ESP only in qualified NORMAL mode. |
| 6 | `HEARTBEAT` | output | 100 kohm pulldown. A high-to-low edge services U501 and, through U504, clocks U503. Do not use a static level as proof of health. |
| 7 | `RELAY_REQUEST` | output | Active high; 100 kohm pulldown. Assert only with valid local temperature, fresh J3 state, qualified NORMAL mode, and an intentional automated call. |
| 8 | `ONEWIRE_DATA` | bidirectional | J602 temperature data through protection and U608. Access only after `EXP_3V3` and the expansion signal gate are qualified; the 4.7 kohm pull-up is connector-side. |
| 9 | `I2C_SDA` | bidirectional/open-drain | On-board TCA9535 bus; not exposed on a connector. |
| 10 | `I2C_SCL` | bidirectional/open-drain | On-board TCA9535 bus; not exposed on a connector. |
| 11 | `EXPANSION_ENABLE` | output | Active high enables U602 and is also a hardware term in U607/U608 OE qualification. R605 holds it low through reset. Drive low before changing expansion ownership or recovering from a fault. |
| 12 | `AUX_GPIO1` | bidirectional | J603 pin 4 through 1 kohm and ESD protection. Default to input. |
| 13 | `ESP_MCLR_ASSERT` | output | Active high request. Effective only in NORMAL and only when the normally-open J404 AUTO RESET ARM shunt is deliberately fitted. Default low; attended service only. |
| 14 | `HOPPER_SWITCH` | input | Active low; J603 pin 5 is a filtered dry-contact input. Debounce in firmware. |
| 17 | `IOX_INTERRUPT_N` | input | Active-low, open-drain interrupt from TCA9535; 10 kohm pull-up. |
| 18 | `EXPANSION_FAULT_N` | input | Active-low fault from the expansion-rail TPS2553. Drive GPIO11 low and place controller-side expansion signals in their safe states on fault. Hardware also disconnects U607/U608 without waiting for firmware. |
| 19 | `USB_DN_MCU` | USB | Native USB D- through 22 ohm and connector-side ESD protection. |
| 20 | `USB_DP_MCU` | USB | Native USB D+ through 22 ohm and connector-side ESD protection. |
| 21 | `USB_VBUS_PRESENT_N` | input | Active low while `V3V3_MAIN` is valid. VBUS is sensing-only and cannot power the ESP. |
| 47 | `MODE_NORMAL_SENSE` | input | Active low means hardware-qualified NORMAL. High means not NORMAL. |
| 48 | `MODE_FTDI_SENSE` | input | Active low means hardware-qualified FTDI SERVICE. High means not FTDI. |

GPIO15 and GPIO16 are explicit reserved no-connects. GPIO3, GPIO45, and GPIO46
are strapping pins and are deliberately not used. GPIO35-GPIO44 are also
unrouted/no-connect in this revision. Do not infer availability from the module
alone; change the hardware source and this contract together.

`INPUT_FAULT_N` is available at TP121 but is not connected to an ESP GPIO in Rev
A. It must not be listed as firmware-observable.

## Mode decode

The two firmware indications are active low and are generated through MOSFETs
in the permanent ESP power domain.

| GPIO47 NORMAL_N | GPIO48 FTDI_N | Firmware interpretation |
| ---: | ---: | --- |
| 0 | 1 | qualified NORMAL |
| 1 | 0 | qualified FTDI SERVICE |
| 1 | 1 | PICkit/OFFLINE, switch transition, cable absent, or unqualified source |
| 0 | 0 | hardware fault/contradiction; force all requests safe and log a fault |

The physical mode logic, not firmware, selects the UART owner and NORMAL-only
relay-coil feed. Firmware must still debounce mode transitions and immediately
clear `RELAY_REQUEST` whenever NORMAL is not continuously observed.

## TCA9535 and expansion power

U601 is at 7-bit I2C address `0x20` (`A2:A0 = 000`). P00-P07 and P10-P13 appear
on J601. P14-P17 are unused and have hardware pulldowns. GPIO11 directly
controls U602; no TCA9535 port controls expansion power:

- GPIO11 low or high impedance: U602 off and the signal switches disabled;
- GPIO11 high: accessory rail requested, but signal connection still waits for
  U609 (`TLV809EA29DBZR`) rail-good and `EXPANSION_FAULT_N` high; and
- `EXPANSION_FAULT_N` low: hardware disconnects every external data conductor;
  firmware must drive GPIO11 low and require an explicit recovery policy.

U607/U608 carry all twelve J601 channels plus J602 1-Wire and all three J603
signals. Q601-Q603 pull their common active-low OE low only when
`EXPANSION_ENABLE`, U609's delayed rail-good output, and
`EXPANSION_FAULT_N` are all high. U609 keeps the switches disconnected below
the valid `EXP_3V3` range and for approximately 200 ms after recovery. U607/U608
also specify powered-off isolation at 0 V supply.

At reset all TCA9535 ports are inputs and R605 holds GPIO11 low. Keep all
controller-side expansion signals benign until the accessory is identified and
the rail is stable. The approximately 200 mA limit is nominal; firmware must not
use it as a measured load budget.

## Safety-critical startup sequence

1. Before initializing peripherals, establish intended safe output values:
   `RELAY_REQUEST=0`, `ESP_MCLR_ASSERT=0`, `HEARTBEAT=0`, and
   `EXPANSION_ENABLE=0`.
2. Read both active-low mode inputs. Treat every state except unambiguous NORMAL
   as non-automated and leave the relay request low.
3. Drive GPIO11 low, initialize I2C, verify U601, leave P00-P13 as inputs, and
   clear any latched accessory-fault policy. Set intended controller-side GPIO
   states before requesting expansion power. If power is requested, wait for
   the U609 release interval and confirm `EXPANSION_FAULT_N=1` before use.
4. Validate the local temperature path and acquire fresh, coherent J3 telemetry
   before allowing an automated thermostat call.
5. Generate a deliberate heartbeat high-to-low transition. The falling edge is
   the common watchdog-service/latch-arm event. A first rising edge alone does
   not qualify health.
6. Continue edges only from the independently monitored control task and within
   the bench-qualified watchdog window. The 22 nF C0G network is 1.758 s nominal
   and approximately 1.51-2.02 s across stated tolerances; do not set the
   firmware cadence from the nominal number without margin and measurement.
7. Assert `RELAY_REQUEST` only after all local policy conditions are valid.
   Clear it before deliberately stopping heartbeat and on stale J3, invalid
   temperature, mode loss, expansion fault affecting required sensing, reset,
   or shutdown.

Home Assistant and network availability are not heartbeat qualifications. A
network outage may leave local control running only if all local safety and data
freshness conditions remain valid.
