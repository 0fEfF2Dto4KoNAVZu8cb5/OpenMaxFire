# Design decisions

## D-001: separate full controller and portable cable

The full controller is the reference design. The later portable service cable is
a reduced derivative of its proven J3/J5 blocks rather than a depopulated ESP
option on the same board. This keeps the field cable small and inexpensive while
letting the permanent controller prioritize robustness and serviceability.

## D-002: ESP32-S3 module with external antenna

Use an ESP32-S3-WROOM-1U module rather than a bare RF design. Native USB reduces
programming parts, and the U.FL antenna connection lets the antenna be mounted
outside a metal stove/controller enclosure. The final module ordering code is
controlled by the BOM.

## D-003: no onboard Ethernet or PoE in Rev A

Rev A uses Wi-Fi plus an external antenna and reserves protected expansion for a
future wired-network daughterboard. Integrating PoE and an Ethernet PHY would
materially increase cost, layout/compliance risk, and board area without
improving the stove-facing safety boundary. The controller remains autonomous
without a network.

## D-004: dedicated permanent input power

Use a certified external 12 V supply. The board is specified for 10.8-13.2 V
normal operation and qualified to 15 V; the eFuse overvoltage threshold is
intentionally near that ceiling. Do not advertise or use it as a generic 18 V
input. A series Schottky after the replaceable input fuse blocks reversed input
without intentionally blowing the fuse; the TVS and eFuse then handle positive
transients, ramp, current limit, and overvoltage cutoff. Do not draw operating
power from unqualified J3/J5 pins. USB VBUS is not tied to the main rail. This
makes all service and partial-power states explicit.

## D-005: target side follows provisionally mapped J5 VDD

J3-3 remains disconnected. The isolated target-side UART provisionally follows
J5 VDD/VSS through protection and current limiting, because J5 is the target's
defined programming-power reference. This decision remains blocked by
`GATE-J5` and `GATE-VTGT`.

## D-006: mechanical fail-safe thermostat transfer

Use a non-latching DPDT signal relay. A dry mechanical contact has an
unambiguous de-energized state without semiconductor off-state leakage or
polarity assumptions. Both poles transfer the two fully floating thermostat
conductors: released, each stove lead is connected to its corresponding backup-
thermostat lead; energized, the two stove leads are joined through the two NO
contacts. Supply a passive bypass for PCB/relay mechanical failure.

## D-007: physical service selection

NORMAL, FTDI SERVICE, and PICkit/OFFLINE are selected by a break-before-make
four-pole, three-position mechanical switch. Separate poles select UART owner,
qualify the selected power source, physically admit FTDI VCC only in FTDI mode,
and physically supply relay-coil power only in NORMAL. Software cannot turn a
service mode into NORMAL. An open or invalid selection is safe/offline.

## D-008: 140 mm x 100 mm four-layer controller; two-layer cable later

Rev A uses a 140 mm x 100 mm engineering outline and four layers for return-
path integrity, power distribution, RF/USB layout, accessible first-article
test points, and clear domain separation. The final enclosure review may reduce
the outline only after routing and isolation margins are proven. The later low-
cost service cable may use two layers once the isolated interface is frozen.

## D-009: independent FTDI cable-current ceiling

Place an 82 ohm, 1% power resistor ahead of every load on the FTDI VCC wire.
Its minimum resistance limits a 5.5 V downstream short below 68 mA, independent
of semiconductor tolerances. Retain the TPS2553 downstream for active limiting,
disconnect, reverse blocking, and fault indication. Voltage margin, resistor
temperature, and cable operation remain first-article qualification items.

## D-010: one heartbeat edge for service and arming

Use the ESP heartbeat falling edge as the TPS3851 service event. A Schmitt
inverter converts the same falling edge into the rising clock for the healthy
latch. Add a hardware pulldown so an absent or resetting processor has a defined
state. This prevents a prior rising edge from arming the relay before any valid
watchdog-service edge has occurred. Use the same TPS3851 `WD_CLEAR_N` node as
SW301's NORMAL source qualifier, so startup, brownout, or a watchdog fault also
removes ESP ownership of J3 without a separate main-rail supervisor.

## D-011: switched expander-centered accessory interface

Keep ESP strapping pins off external connectors. Use a local TCA9535 for twelve
protected J601 channels, plus dedicated J602 1-Wire and J603 auxiliary/hopper
ports. All share a firmware-enabled, current-limited `EXP_3V3` rail that defaults
off. GPIO11, not a TCA9535 port, controls the rail; P14-P17 remain unused.

Place all sixteen external data conductors behind two powered-off-isolating bus
switches. Permit their OE only when the GPIO11 enable request, delayed U609
rail-good indication, and inactive-low TPS2553 fault are all valid through a
three-FET hardware chain. Keep the J602 1-Wire pull-up on the connector side of
that barrier. Route J603 analog input to GPIO1/ADC1 through a 20 kohm/100 kohm
five-sixths divider. The internal I2C bus is not exposed as a cable interface in
Rev A.

## D-012: sensing-only USB VBUS

Rev A remains self-powered. USB VBUS drives only a protected MOSFET-gate monitor
and cannot feed a powered-down ESP GPIO or any board rail. Firmware receives the
controller-powered, active-low `USB_VBUS_PRESENT_N` indication.
