# External interfaces

Connector reference designators and exact families are controlled by the
schematic/BOM. This file defines electrical meaning independent of connector
brand.

## Permanent power

| Pin | Signal | Notes |
| --- | --- | --- |
| 1 | `VIN_12V` | nominal 12 V DC from a certified isolated supply; 10.8-13.2 V normal, 15 V qualification maximum |
| 2 | `GND_CTRL` | controller-side return |

No stove line-voltage or unverified auxiliary supply may be connected here.

## Stove J3 harness

Validated only on controller 9067-0604, serial 5215:

| J3 pin | Stove function | Controller signal |
| --- | --- | --- |
| 1 | stove RX / PIC RC7 pin 26 | `J3_STOVE_RX` (output from adapter) |
| 2 | stove TX / PIC RC6 pin 25 | `J3_STOVE_TX` (input to adapter) |
| 3 | probable VDD through about 100 ohms | NC/test-only; insulated lead if present |
| 4 | signal ground | `GND_TGT` |

The board-side harness must be keyed. A harness label shall state the stove
board revision for which it was traced. Do not use RS-232 electrical levels.

J3 pin 1 is the actively driven output and must become high impedance whenever
the target interface is unqualified. J3 pin 2 is an input, not a second
tri-state output: after R406, R411 provides a 47 kohm UART-idle bias only from
the target-derived `VTGT_PROTECTED` rail. It must never be moved to a controller
rail, and its target loading, rail-collapse behavior, and target-off leakage are
release tests.

## Main-board J5 / PICkit

Strong provisional mapping for the 9067-0604 main controller only:

| Main-board J5 | PICkit | Signal |
| --- | --- | --- |
| 1, square pad | 1 | MCLR/VPP |
| 2 | 2 | VDD/VTGT sense |
| 3 | 3 | VSS/target ground |
| 4 | 4 | PGD/RB7 |
| 5 | 5 | PGC/RB6 |
| no target pin | 6 | AUX/PGM; NC |

This mapping is not released until the second continuity pass. The auxiliary
igniter board also has a connector labeled J5; factory drawings associate that
other J5 with 120 V AC. Never probe or cable it as ICSP.

The controller provides two J5-related connections:

- a keyed target harness to the provisionally mapped five-pin main-board J5;
- a standard six-pin PICkit header in Microchip order, with pin 6 unconnected.

PGD, PGC, and MCLR/VPP are direct in the PICkit path. Do not fit status LEDs,
TVS clamps, level translators, or default series resistors on those nets.

PICkit use is offline service only. Verify the full `9067-0604` main-board
identity, cable pin 1, and connector location immediately before insertion;
leave J404 AUTO RESET ARM open and disconnect J3, FTDI, USB, and other service
tools. Configure exactly one target-VDD source: never allow the stove and
PICkit to source VDD together. Begin read-only on a spare controller. The
complete procedure and the two-J5 hazard are in
[`TARGET_SERVICE_DESIGN.md`](./TARGET_SERVICE_DESIGN.md#9-installer-and-service-rules).

## External FTDI service

The six positions follow the TTL-232R cable convention so either a connectorized
cable or a TTL-232R-5V-WE pigtail adapter can be used:

| Position | FTDI wire | Function |
| --- | --- | --- |
| 1 | black | `GND_CTRL` |
| 2 | brown | CTS, no-connect/reserved |
| 3 | red | `FTDI_VCC`, service-front-end power only |
| 4 | orange | FTDI TXD to stove RX path |
| 5 | yellow | FTDI RXD from stove TX path |
| 6 | green | RTS#, input to the separately armed isolated MCLR fixture |

The expected cable is 5 V TTL, non-inverted. R300 is an 82 ohm, 1% series power
resistor upstream of every board load. Even with 5.5 V at the cable and a hard
short downstream, its minimum resistance limits the VCC-wire current to less
than 68 mA. U301 (`TPS2553`) then provides a secondary active current limit,
disconnect, reverse blocking, and `FTDI_POWER_FAULT_N`; its 50-100 mA fixed-
limit spread is not the sole cable-budget guarantee. First-article testing must
also prove adequate service-rail voltage and UART margin after R300 at maximum
legitimate load.

FTDI VCC must never feed the ESP32, relay, permanent 5 V rail, or target VDD.
RTS# cannot reach MCLR unless the physical reset-arm link is fitted; the direct
PICkit MCLR/VPP path remains untouched.

## Thermostat transfer

| Pin | Function |
| --- | --- |
| 1 | stove thermostat terminal A |
| 2 | stove thermostat terminal B |
| 3 | physical backup thermostat terminal A |
| 4 | physical backup thermostat terminal B |

These are dry-contact circuits. Neither side is intentionally tied to a logic
rail or ground. The keyed four-wire harness permits a passive bypass accessory
that joins pins 1-3 and 2-4 with the PCB absent. Keep that bypass with the
installed controller.

The separate two-pin `FORCE BACKUP` connector is normally fitted with a closed
shunt. Removing the shunt, unplugging its cable, or opening an attached normally-
closed service contact removes relay-coil power and returns to the wall
thermostat without firmware cooperation.

## Native ESP USB-C

USB-C is for ESP32 programming, logging, and USB-JTAG. It is not the stove J3
service connection. VBUS is sensing-only and neither powers nor receives power
from the permanent board in Rev A. VBUS reaches Q201's insulated gate through
100 kohm; Q201 pulls `USB_VBUS_PRESENT_N` low when VBUS is present. The ESP GPIO
is pulled high from `V3V3_MAIN`, so it is meaningful only while the permanent
3.3 V rail is valid:

| `USB_VBUS_PRESENT_N` | Meaning while `V3V3_MAIN` is valid |
| ---: | --- |
| 0 | USB VBUS/cable present |
| 1 | USB VBUS absent |

## Low-speed expansion

All expansion connectors are controller-side SELV 3.3 V only. They are not 5 V,
12 V, target-domain, thermostat, or mains tolerant. `EXP_3V3` is shared by all
three connectors, defaults off, and is nominally limited to about 200 mA by a
TPS2553. ESP GPIO11 (`EXPANSION_ENABLE`) explicitly enables the rail; R605 holds
it off during reset. TCA9535 P14-P17 are unused and do not control power.
Firmware must treat `EXPANSION_FAULT_N` as active low.

The sixteen data conductors, but not power or ground, pass through U607/U608
powered-off-isolating bus switches. Their common active-low OE is released only
when GPIO11 requests power, U609 (`TLV809EA29DBZR`) has qualified `EXP_3V3` for
approximately 200 ms, and `EXPANSION_FAULT_N` is high. Q601-Q603 implement the
three-condition hardware gate. Startup, disable, undervoltage, or a current
fault therefore disconnects every connector signal without firmware timing
assumptions.

There is no external I2C connector. GPIO9/GPIO10 form an on-board bus to the
TCA9535 at address `0x20`.

### J601 — 12-channel expansion

J601 is a keyed JST PH 16-position header. The two power/ground pairs serve the
two six-GPIO cable banks but share the same board nets.

| Pin | Function | Pin | Function |
| ---: | --- | ---: | --- |
| 1 | `GND_CTRL` | 9 | `GND_CTRL` |
| 2 | `EXP_3V3` | 10 | `EXP_3V3` |
| 3 | TCA9535 P00 | 11 | TCA9535 P06 |
| 4 | TCA9535 P01 | 12 | TCA9535 P07 |
| 5 | TCA9535 P02 | 13 | TCA9535 P10 |
| 6 | TCA9535 P03 | 14 | TCA9535 P11 |
| 7 | TCA9535 P04 | 15 | TCA9535 P12 |
| 8 | TCA9535 P05 | 16 | TCA9535 P13 |

Each exposed channel has 1 kohm series resistance, a 100 kohm pulldown, and a
connector-side ground-only ESD array. All twelve channels pass through U607 or
U608. TCA9535 ports power up as inputs; firmware must keep them inputs until
accessory identity, rail state, and safe direction are known.

### J602 — 1-Wire temperature sensor

| Pin | Function |
| ---: | --- |
| 1 | `GND_CTRL` |
| 2 | switched `EXP_3V3` |
| 3 | protected `ONEWIRE_DATA` |

The data path includes U608, 100 ohm controller-side series damping, a 4.7 kohm
pull-up to `EXP_3V3` on the connector side of U608, a connector-side weak
discharge path, and ground-only ESD protection. Connector-side placement keeps
an ESP GPIO high from feeding a disabled accessory rail through the pull-up.

### J603 — auxiliary and hopper inputs

| Pin | Function | Electrical contract |
| ---: | --- | --- |
| 1 | `GND_CTRL` | controller return |
| 2 | switched `EXP_3V3` | shared current-limited accessory rail |
| 3 | `AUX_ADC` | 0-3.3 V only; U608 then 20 kohm/100 kohm divider (5:6) and 100 nF filter to GPIO1/ADC1 |
| 4 | `AUX_GPIO1` | U608 then bidirectional GPIO12 through 1 kohm |
| 5 | `HOPPER_SWITCH` | U608 then active-low GPIO14 dry-contact input through 4.7 kohm and RC filtering |

At 3.3 V on J603 pin 3, the nominal ESP ADC-node voltage is 2.75 V. Firmware
must apply ADC calibration and multiply the measured node voltage by 6/5 to
recover connector voltage. All three J603 signals remain disconnected while the
expansion signal gate is not qualified.

ESP32 strapping pins are not exposed. No expansion pin is authorized to drive a
stove actuator.

## Labeled test points

The board has two physically separated probe banks. TP101-TP124 are referenced
to `GND_CTRL`; TP201-TP209 are referenced to `GND_TGT`. A grounded oscilloscope
or programmer can defeat that separation, so test equipment connections remain
part of the safety procedure.

| Controller TP | Net | Controller TP | Net |
| --- | --- | --- | --- |
| TP101 | `VIN_FUSED` | TP113 | `RUN_MODE` |
| TP102 | `VIN_PROTECTED` | TP114 | `FTDI_VALID` |
| TP103 | `V5_MAIN` | TP115 | `HEARTBEAT` |
| TP104 | `V3V3_MAIN` | TP116 | `WD_CLEAR_N` |
| TP105 | `SERVICE_5V` | TP117 | `HB_OK` |
| TP106 | `SERVICE_3V3` | TP118 | `RELAY_REQUEST` |
| TP107 | `FTDI_5V_LIMITED` | TP119 | `KTH_COIL_5V` |
| TP108 | `EXP_3V3` | TP120 | `RELAY_COIL_LOW` |
| TP109 | `ESP_UART_TX` | TP121 | `INPUT_FAULT_N` |
| TP110 | `ESP_UART_RX` | TP122 | `EXPANSION_FAULT_N` |
| TP111 | `SERVICE_TX_SELECTED` | TP123 | `USB_VBUS_PRESENT_N` |
| TP112 | `SERVICE_RX_ISOLATED` | TP124 | `GND_CTRL` |

| Target TP | Net | Target TP | Net |
| --- | --- | --- | --- |
| TP201 | `GND_TGT` | TP206 | `J3_STOVE_TX` |
| TP202 | `VTGT_RAW` | TP207 | `J5_MCLR_VPP` |
| TP203 | `VTGT_PROTECTED` | TP208 | `J5_PGD` |
| TP204 | `VTGT_GOOD` | TP209 | `J5_PGC` |
| TP205 | `J3_STOVE_RX` |  |  |
