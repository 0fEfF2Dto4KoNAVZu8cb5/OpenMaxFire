# MaxFire motherboard pinout diagram cross-reference

## Evidence identity

The owner supplied an online-found image titled `MaxFire Mother Board Pin Out`
on 2026-08-20. The repository preserves the received bytes at
[`maxfire-mother-board-pinout.jpg`](../../preservation/original/diagrams/maxfire-mother-board-pinout.jpg).

| Property | Value |
| --- | --- |
| Received name | `1000000387.jpg` |
| Dimensions | 1187 x 1536 pixels |
| SHA-256 | `22dad1271b3780b5867a4be6bf9875495aa4fe39b218352a9121097920145975` |
| Visible board marking | `PCB Part Number 9067-0404` |
| Publicly indexed match | [`115 110 Mother Board Pin Out`](https://www.scribd.com/document/3144205/115-110-Mother-Board-Pin-Out) |

The public match helps identify the appliance family, but the original author,
date, and vendor-publication status are unverified.

## Cross-check against stove serial 5215

The nameplate photograph establishes appliance serial **5215**, and the owner
identifies the stove as a MaxFire 115. Its installed controller is
owner-reported as `9067-0604`, manufactured in December 2005 with assembly mark
`12/15`.

The diagram therefore does **not** show the exact reported PCB revision:

| Evidence | Board/revision | Conclusion |
| --- | --- | --- |
| Supplied diagram silkscreen | `9067-0404` | Directly visible in the image |
| Serial 5215 installed board | `9067-0604` | Owner-reported; board photograph still needed |
| Family relationship | Common `9067-xx04` numbering and matching MaxFire functions | Closely related-family evidence, not proof of identical routing |

Connector names and system roles that agree with software/firmware evidence can
be used as corroboration. Individual cavities, wire positions, PCB nets, and
electrical levels must remain unconfirmed until the `9067-0604` board is
photographed or measured.

## Diagram inventory

The image separates blue low-voltage circuits from red 120 V AC circuits. Its
low-voltage labels include:

- `J3 - Computer Port`;
- `J2` communication cable between the motherboard and front panel;
- `J6` thermostat connection;
- `J9` feeder-wheel sensor and `J10` exhaust-fan sensor;
- burn-drive motor, fire-door, fuel, and ash-bin-door switches;
- `J18` thermocouple; and
- front-panel ON/OFF/UP/DOWN buttons and LEDs.

Its mains section labels igniters, burn/feeder motors, hopper snap switch, air
compressor, exhaust fan, convection fan/capacitor, fuses, and 120 V input.
Those red circuits are documentation only and are outside the read-only J3
work. Power must be disconnected before opening or servicing the stove.

## Static firmware and BixCheck correlation

The diagram materially strengthens several mappings recovered independently
from all three firmware generations and all three BixCheck executables:

| Diagram label | Firmware path | J3 protocol result | Confidence and boundary |
| --- | --- | --- | --- |
| ON/OFF/UP/DOWN panel buttons | RD2 selects the button bank; RD6:RD5 selects one of four buttons; RD3 is the active-low return; result is debounced into RAM `0x53` | `CR01`: none `00`, ON `02`, OFF `01`, UP `04`, DOWN `08` | High static confidence; no live check on serial 5215 |
| Burn Drive Motor Switch | External-input mux slot 0: RD7=1, RD6:RD5=`00`, RD3 active-high return | `CR02.0`; BixCheck plate-motor-off test also inspects `CR03.1` | High static signal assignment; physical polarity unverified |
| Fuel Switch | External-input mux slot 2: RD7=1, RD6:RD5=`10`, RD3 active-high return | `CR02.2`; `1` selects Fuel A/corn and `0` selects Fuel B/wood | High static mapping and polarity; no live check |
| J9 Feeder Wheel Sensor | RD0 edge input; RB1 feed-motor state gates a 16-bit RB0-tick counter; a high-then-low RD0 cycle latches RAM `0x45:0x44` | Current RD0 level is `CR02.4`; `CR07` is the low byte of the latched interval shifted right four | High static signal path in 2.06/2.70/2.71; polarity, time unit, and revision routing unverified |
| J10 Exhaust Fan Sensor | RA4/T0CKI high-to-low pulses increment unprescaled TMR0; every 30 RB0 external-interrupt ticks the count is latched into RAM `0x34` | `CR05` raw pulse-count byte; overflow is `FF` | High static signal path in 2.06/2.70/2.71; conversion to RPM and revision routing unverified |
| Fire Door Safety Switch | Direct RD1 input | `CR02.5`; open `1`, closed `0` | High offline mapping; revision routing not measured |
| Ash Bin Door Switch | Direct RD4 input | `CR02.6`; open `1`, closed `0` | High offline mapping; revision routing not measured |
| Thermostat connection J6 | Direct RB4 input | `CR06.2`; opposite open/closed states | High bit/pin mapping; physical polarity unverified |
| Front-panel trim controls | ADC paths AN3 and AN4 | Fan pot `CR09`; feed pot `CR0A` | High offline mapping |

The fuel polarity is not inferred from the picture. In 2.70/2.71 firmware, a
clear mux bit adds `0x30` to the configuration address, moving from the Fuel A
bank (`A40...`) to Fuel B (`A70...`). The corresponding 2.06 paths and dormant
BixCheck predicates agree. The picture then independently supplies the physical
name `Fuel Switch` for that muxed input.

The sensor names are cross-referenced in the other direction. BixCheck reads
`CR05` for all three exhaust-fan service tests and `CR07` for the automatic
feed-motor/sensor test. Firmware then traces `CR05` back to the TMR0/RA4 path
and `CR07` back to an RD0 wheel transition. The diagram independently names
those related-board connectors J10 and J9, respectively.

Factory Checkout's raw acceptance ranges are:

| Service condition | Accepted value |
| --- | ---: |
| J10 exhaust, full power | `CR05 >= 0x78` (120) |
| J10 exhaust, half power | `CR05 = 0x38`-`0x48` (56-72) |
| J10 exhaust, off | `CR05 = 0x00` in BixCheck 5.5.x; `0x00`-`0x03` in 5.0.21 |
| J9 feed motor/sensor | `CR07 = 0x10`-`0x68` (16-104) |

These are application thresholds, not documented engineering units. In
particular, `CR05` must not be labeled RPM without a physical correlation.

`CR02.1`, external-input mux slot 1, remains physically unassigned.

## What the diagram does not establish

The diagram identifies J3 as the computer port and shows its board location,
which independently corroborates the BixCheck release notes. It does not label
J3's four individual pins, TX, RX, ground, a supply, signaling voltage, or
polarity. It therefore does not make a generic TTL or RS-232 adapter safe to
connect.

The remaining revision-specific checks are:

1. photograph serial 5215's `9067-0604` silkscreen and both sides around J3;
2. compare connector designators and harness positions against this `9067-0404`
   image;
3. identify ground and idle voltages through a protected, power-limited setup;
4. validate the read-only register mappings with the stove cold and off.
