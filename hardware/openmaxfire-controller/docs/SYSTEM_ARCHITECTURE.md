# System architecture

## Safety ownership

The existing Bixby/PIC controller continues to own the stove state machine,
combustion safety, interlocks, faults, actuators, and orderly shutdown. The
OpenMaxFire board reads telemetry and makes the same bounded J3 requests a
service tool can make. It is not a replacement combustion controller.

The physical wall thermostat is the passive fallback. It is not complete freeze
protection on the validated firmware because it cannot start a stopped stove;
the independently controlled backup heating system remains the final minimum-
temperature protection.

## Functional blocks

```text
 certified 12 V supply
          |
  input protection -> 5 V buck -> 3.3 V regulator -> ESP32-S3 + sensors
          |                 |
          |                 +-> watchdog + mode logic + expansion
          +--------------------> fail-safe relay coil

 ESP UART ----\
               > guarded source select -> galvanic isolator -> target-off gate -> J3
 FTDI UART ---/                                      ^
                                                    |
                                    protected J5 VDD/VSS target supply

 ESP heartbeat -> watchdog -> Schmitt inverter -> sticky healthy latch --\
 ESP request ---------------------------------------- series FETs -> DPDT relay
 physical NORMAL-only coil feed --------------------/

 J5 target header <--------------------> direct PICkit header
 J5 MCLR <------ guarded isolated open-collector reset fixture

 thermostat terminals <------ dry contacts only ------> original thermostat
```

## Domain boundaries

| Domain | Rails/reference | Contents | May power another domain? |
| --- | --- | --- | --- |
| Permanent controller | `VIN_PROTECTED`, `V5_MAIN`, `V3V3_MAIN`, `GND_CTRL` | ESP32, USB, sensors, watchdog, expansion, relay coil | Only through designed regulators/isolators |
| FTDI/service front end | `FTDI_VCC_CABLE`, `FTDI_5V_RAW`, `FTDI_5V_LIMITED`, `SERVICE_3V3`, `GND_CTRL` | FTDI-side buffers and mode input | No ESP32 or relay power |
| Stove target | `VTGT_RAW`, `VTGT_PROTECTED`, `GND_TGT` | isolator target side, target-off output gate, MCLR sinks | Never feeds controller rails |
| Thermostat dry contact | no board supply/reference | relay contacts and terminal block | Never |

`GND_CTRL` and `GND_TGT` are separated by the digital isolator. The direct J5
PICkit header belongs entirely to the target domain. A programmer connection can
bridge its own computer to the target and is therefore allowed only in the
offline service procedure.

## Operating modes

### NORMAL

- A mechanical selector pole chooses the ESP path; a second pole qualifies that
  the main source is present.
- A third mechanical pole is the only source of relay-coil power.
- The isolated J3 data path is enabled only while the selected source remains
  valid.
- The MCLR/reset fixture is disarmed.
- `NORMAL_MODE` may participate in the relay safety AND gate.
- SW301 qualifies the NORMAL source with `WD_CLEAR_N`, the wired open-drain
  reset/watchdog output of U501 (`TPS3851H33E`, 3.069 V nominal falling
  threshold). U501 therefore removes NORMAL ownership during main-rail startup
  or brownout and on a watchdog fault; there is no second main-rail supervisor.
- R501 pulls `WD_CLEAR_N` up only from `V3V3_MAIN`; R306 pulls the selector's
  `MODE_SOURCE_OK` result down, so loss of the main rail cannot leave NORMAL
  qualification floating.
- Firmware still has to establish valid local temperature, fresh J3 telemetry,
  and a healthy local loop before asserting `RELAY_REQUEST` and heartbeat.

### FTDI SERVICE

- The ESP UART is isolated from the bus even if the ESP is powered.
- A fourth mechanical selector pole admits current-limited FTDI VCC only in this
  position; cable power cannot become a false NORMAL qualification.
- R300, 82 ohm +/-1%, is upstream of every board load and limits a 5.5 V cable
  to less than 68 mA under a downstream short. U301 (`TPS2553`) adds active
  current limiting, disconnect, and an active-low fault output; it is not the
  sole guarantee of the cable-current ceiling.
- The external FTDI cable owns J3 TX/RX through the same target-safe isolation
  and target-off gate used in NORMAL mode.
- The FTDI cable may power its small source-side buffer from FTDI VCC; it cannot
  power the ESP or relay.
- `NORMAL_MODE` is false, so the physical thermostat is connected.
- MCLR is usable only after the separate physical RESET ARM control is enabled.

### PICkit/OFFLINE

- Both ESP and FTDI UART sources are high impedance.
- `NORMAL_MODE` is false and the physical thermostat is connected.
- PICkit pins 1-5 have a short direct connection to the provisionally mapped
  main-board J5; connection remains blocked pending independent continuity proof.
- The stove is cold, mains and actuators are disconnected, and the programmer
  is the only permitted service power relationship.

## Thermostat transfer

Both poles of a non-latching DPDT relay preserve a completely floating transfer:

```text
 released / fail-back                    energized / automated call

 STOVE_A --COM_A--NC_A-- BACKUP_A        STOVE_A --COM_A--NO_A--+
                                              wall thermostat    +-- short node
 STOVE_B --COM_B--NC_B-- BACKUP_B        STOVE_B --COM_B--NO_B--+
```

When K501 is energized, both COM-NO contacts join the two stove thermostat leads
at a floating short node so OpenMaxFire can regulate through J3. When K501
releases, the two COM-NC contacts connect the physical thermostat leads back to
the stove. No contact is tied to either PCB ground.

Relay current additionally passes through a removable, open-fail force-backup
link. A missing shunt or open external NC contact releases K501 independently of
the ESP, watchdog, and mode logic.

A removable passive bypass plug/harness shall be supplied for field recovery
from a PCB or relay mechanical failure. The bypass directly restores the
original thermostat wiring without relying on any OpenMaxFire component.

## Dead-man timing and edge contract

U501 is a `TPS3851H33E` supervisor/window watchdog with a specified 22 nF,
+/-5% C0G C501. The resulting watchdog interval is 1.758 s nominal and about
1.51-2.02 s after the documented capacitor and watchdog tolerances are applied.
Those limits remain a bench-verification gate.

The ESP `HEARTBEAT` net has a 100 kohm pulldown. U501 services on the ESP
falling edge. U504, a Schmitt inverter, converts that same falling edge to a
rising `HEARTBEAT_ARM_CLK` edge for U503. Consequently a stale high or low
level cannot qualify the relay after mode entry: returning to NORMAL requires a
new high-to-low heartbeat transition. U503 is asynchronously cleared whenever
`RUN_MODE` is false or U501 asserts reset/watchdog fault.

## USB power relationship

The native USB-C port is a self-powered USB 2.0 device interface. VBUS does not
feed `V5_MAIN`, `V3V3_MAIN`, or any service rail. It reaches only R207 and the
insulated gate of Q201; the controller-powered drain is
`USB_VBUS_PRESENT_N`. Firmware must interpret low as cable/VBUS present and may
read it only while the main 3.3 V domain is valid.

## Expansion policy

Rev A exposes only protected low-speed I/O. There is no external I2C connector;
the ESP I2C bus is local to the TCA9535 expander.

- J601 is a keyed 16-position connector with two grounds, two copies of the
  switched `EXP_3V3` rail, and twelve protected TCA9535 GPIOs.
- J602 is a keyed three-position local-temperature port: ground, switched
  `EXP_3V3`, and protected 1-Wire data.
- J603 is a keyed five-position auxiliary port: ground, switched `EXP_3V3`,
  protected 0-3.3 V ADC, protected bidirectional GPIO, and active-low hopper
  switch input.

GPIO11 drives `EXPANSION_ENABLE`; its hardware pulldown keeps U602 and the
shared `EXP_3V3` rail off through reset. U602 nominally limits the combined
accessory load to about 200 mA. TCA9535 P14-P17 are unused and pulled low; no
expander pin controls accessory power.

Every one of the sixteen external data conductors passes through U607/U608
`SN74CBTLV3245A` bus switches. Their active-low OE can assert only when all
three hardware conditions are true: GPIO11 requests expansion power, U609
(`TLV809EA29DBZR`) has qualified `EXP_3V3` for its approximately 200 ms release
delay, and `EXPANSION_FAULT_N` is high. Q601-Q603 implement that series
qualification;
loss of any condition disconnects all data conductors, and U607/U608 provide
specified powered-off isolation when their supply is at 0 V. The J602 4.7 kohm
1-Wire pull-up is on the connector side of U608 so an ESP output cannot feed a
disabled accessory rail through the pull-up.

J603 pin 3 reaches ESP GPIO1/ADC1 through the bus switch and a 20 kohm/100 kohm
divider, producing five-sixths of the connector voltage, with 100 nF filtering
at the ADC node. Direct stove actuator control is explicitly out of scope.

## Physical partition and probe access

Rev A uses a 140 mm x 100 mm four-layer engineering outline. An 8 mm-wide,
102 mm-tall all-layer keepout centered at `x=-23 mm` separates the stove-target
island on the left from the controller domain on the right. Only the four
specified isolation components may cross it.

TP101-TP124 form the controller/service probe bank. TP201-TP209 form a separate
target-domain bank for target ground, target rails, J3, and J5 signals. Probe
equipment can itself bridge domains, so the test procedure must control scope
grounds and isolation even though the pads are physically separated.
