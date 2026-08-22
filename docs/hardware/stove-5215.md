# Recovered stove: serial 5215

## Identity

| Field | Value | Confidence |
| --- | --- | --- |
| Product family | Bixby MaxFire room heater | Nameplate |
| Model | MaxFire 115 | Owner report |
| Serial number | 5215 | Nameplate photograph |
| Manufacture year | 2005 | Nameplate photograph |
| Manufacture month | December | Owner report |
| Main PCB | 9067-0604 | Directly legible in bare-board photograph |
| Internal assembly mark | `12/15` | Owner report |

An earlier box/card number of 5232 was mentioned during inventory. The appliance nameplate is authoritative for this project and clearly shows 5215.

## Photographs

- [Nameplate and serial number](../../preservation/original/photos/nameplate-serial-5215.png)
- [Safety labels and side-panel warning](../../preservation/original/photos/safety-labels.png)
- [Front control panel](../../preservation/original/photos/front-control-panel.jpg)
- [Installed controller and stove-interior photograph set](installed-controller-photographs.md)
- [Bare controller, J3, PIC, and solder-side photograph set](bare-controller-photographs.md)

The nameplate identifies a 115 V, 60 Hz appliance rated 10 A at startup and 2 A while running. The safety label warns against operating with the side panel removed and requires power disconnection before servicing.

The later bare-board set makes the complete main-PCB `9067-0604` marking,
PIC16F877A, and `10.000` oscillator legible and directly exposes both sides of
J3. Manufacture month and the `12/15` assembly interpretation retain an
owner-report component.

The controller's live EEPROM contains serial string `2060` and production-date
string `01102007`, while the appliance nameplate says serial 5215 and December
2005. Both identities are preserved without assigning a cause to the mismatch;
see [the firmware-2.02 live report](../reverse-engineering/live-fw202-format04.md).
