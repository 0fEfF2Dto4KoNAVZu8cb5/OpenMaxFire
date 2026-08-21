# Candidate permanent-controller hardware

Status: design candidate; not construction-ready or electrically validated on J3.

This note records the preferred hardware direction for a permanent OpenMaxFire
controller. Part numbers are candidates, not an instruction to connect them to
the stove before the Phase 1 electrical measurements are complete.

## Design goals

- Keep the Bixby controller responsible for combustion and appliance safety.
- Provide local telemetry, verified ON/OFF/UP/DOWN control, and heat management.
- Continue local operation without Home Assistant, Ethernet, or Wi-Fi.
- Make pellet heat the normal primary source.
- Preserve a physical thermostat path when the OpenMaxFire controller loses
  power, crashes, or fails its health checks.
- Keep the independently controlled propane furnace available for minimum-house-
  temperature and freeze protection.
- Keep J3 electrically isolated from the network/controller side.

## Preferred two-board architecture

The preferred permanent assembly uses two replaceable boards rather than three
loose development modules or a fully custom PoE/Ethernet controller.

### 1. Controller and network board

Candidate: [Olimex ESP32-POE-ISO-IND](https://www.olimex.com/Products/IoT/ESP32/ESP32-POE-ISO/open-source-hardware)

Responsibilities:

- ESP32 application and local control loop
- IEEE 802.3af PoE and 100 Mb Ethernet
- Wi-Fi fallback
- Home Assistant/ESPHome exposure
- local wired temperature input
- health-state and watchdog servicing
- relay command and position verification

The industrial variant is rated by Olimex for -40 to +85 degrees C. Its isolated
PoE supply is specified as 5 V at 400 mA. The complete assembly must be measured
under simultaneous network, UART, relay, and sensor load before that budget is
accepted.

### 2. OpenMaxFire stove-interface daughterboard

The daughterboard should plug into the Olimex expansion/UEXT signals and contain
all stove-facing and fail-safe circuitry:

- one UART transmit channel and one UART receive channel;
- signal and power isolation for the J3 side;
- configurable 3.3 V or 5 V stove-side logic, selected only after measurement;
- J3 series-current limiting and appropriate transient/ESD protection;
- a non-latching transfer relay with a transistor driver, flyback diode, and
  hardware pulldown;
- a hardware watchdog or supervisor;
- relay-position feedback using a spare contact where practical;
- removable J3, thermostat, and temperature-sensor connectors.

A circuit-level starting point, signal allocation, fail-safe logic, preliminary
parts list, and layout constraints are recorded in
[Preliminary stove-interface daughterboard design](daughterboard-preliminary-design.md).

Candidate integrated UART isolation parts:

- [TI ISOW7721](https://www.ti.com/product/ISOW7721): one forward and one reverse
  digital channel with integrated isolated DC/DC power. The normal, non-F
  fail-state output is high, which is appropriate for UART idle.
- [Analog Devices ADuM5211](https://www.analog.com/en/products/adum5211.html):
  established one-forward/one-reverse alternative with integrated isolated
  DC/DC power.

Either candidate can supply the isolated stove-facing logic from the controller
side, so the proposed J3 serial boundary needs only TX, RX, and J3 ground. This
does not assert physical pin positions or prove that the fourth J3 connector
cavity is unused.

Candidate transfer relay:

- Panasonic TQ-series single-side-stable, non-latching DPDT signal relay.
- Prefer the gold-clad contact version and a coil appropriate to the measured
  board supply and driver.
- Use one pole for thermostat transfer and the spare pole for position feedback.

The TQ family is a signal relay rather than a large power relay. That is a better
fit for the uncharacterized, likely low-energy thermostat input. A mechanical
dry-contact relay is preferred over an SSR because it gives a definite
de-energized state without polarity assumptions or off-state leakage.

Candidate fail-safe gate:

- [TI SN74LVC1G123](https://www.ti.com/product/SN74LVC1G123), or an equivalent
  retriggerable hardware monostable, generates `HB_OK` only while firmware
  continuously supplies a heartbeat.
- A separate AND gate combines `HB_OK` with the firmware's relay request before
  a MOSFET can energize the relay coil.
- A reset-only watchdog is optional but is not accepted as the only relay
  safeguard: a missed heartbeat must remove coil power and keep it removed
  until liveness and the relay request are both re-established.
- The relay-control GPIO must default low/high-impedance so reset, boot, and
  power loss release the relay.

## Three-wire J3 boundary

The candidate isolated interface exposes only:

| Connection | Purpose |
| --- | --- |
| J3 TX | Data transmitted by the stove |
| J3 RX | Data received by the stove |
| J3 ground | Reference only for the isolated stove-facing side |

The controller-side ground and J3 ground must remain separated across the
isolation barrier. The earlier small purple ADuM1201-class breakout remains
useful for bench experiments, but a basic ADuM1201 requires power on both sides.
It should not be treated as a complete three-wire isolated interface unless its
specific board includes an isolated power converter.

## Thermostat transfer behavior

The relay is energized only after the controller has booted, the local
temperature input is valid, J3 communication is current, and the local control
loop is healthy.

| Controller state | Relay state | Thermostat-terminal path |
| --- | --- | --- |
| Healthy and verified | Energized | Direct closed path; OpenMaxFire controls ON/OFF and level through J3 |
| Booting, failed, unpowered, or stale | De-energized | Physical backup thermostat is reconnected |

Proposed single-pole wiring:

- Stove thermostat terminal A to relay COM.
- Relay NO directly to stove thermostat terminal B.
- Relay NC through the physical backup thermostat to terminal B.

This is a transfer function, not a second ON/OFF input. Factory documentation and
firmware analysis indicate that an open thermostat input reduces an already
operating stove to level 1 and a closed input allows the selected level. The
wall thermostat does not independently start a stopped stove. The independent
propane furnace thermostat therefore remains the final minimum-temperature and
freeze-protection system.

Home Assistant is supervisory during normal operation. The appliance-adjacent
ESP32 must retain a wired temperature sensor and enough local policy to operate
safely when Home Assistant or either network disappears.

## Why not a different all-in-one controller?

Commercial ESP32 relay boards were considered, including the Olimex ESP32-EVB
family and larger industrial Ethernet/relay controllers. They do not remove the
critical custom work:

- the ESP32-EVB has Ethernet, Wi-Fi, and relays but no native PoE input and no
  isolated TTL UART;
- its power relays are larger than necessary for a low-energy thermostat signal;
- many industrial ESP32 relay controllers isolate RS-485, not the unverified J3
  physical layer;
- no reviewed board combines industrial PoE, Wi-Fi, isolated three-wire UART,
  low-signal fail-safe transfer contacts, and the required boot/watchdog policy.

A completely custom ESP32/PoE/Ethernet board could reduce the assembly to one
PCB, but it would add PoE, Ethernet-PHY, RF-layout, programming, compliance, and
replacement risk. Keeping the certified/open Olimex board and placing the
project-specific circuitry on one replaceable daughterboard is the preferred
balance.

## Prototype versus permanent hardware

For initial protected bench work, separate modules remain appropriate:

1. Olimex ESP32-POE-ISO-IND
2. ADuM1201-class UART isolator plus a genuinely isolated secondary supply
3. non-latching relay module used only after the thermostat circuit is measured

For the permanent installation, consolidate items 2 and 3, the watchdog, and the
connectors onto the OpenMaxFire daughterboard.

## Required validation before schematic lock

- Identify J3 ground, TX, RX, any supply, and the physical cavity order.
- Measure idle voltage, active voltage, polarity, and whether the link is
  TTL/CMOS, inverted logic, or true RS-232.
- Do not connect J3 VCC, if present, to the controller.
- Confirm whether 3.3 V or 5 V isolated-side logic is required.
- Measure thermostat-terminal open-circuit voltage and closed-circuit current.
- Verify closed/open thermostat behavior in every relevant stove state.
- Validate J3 ON/OFF/UP/DOWN with the thermostat path closed.
- Measure worst-case Olimex power consumption with Ethernet, Wi-Fi, UART,
  isolator, relay, watchdog, and sensors active.
- Test power loss, boot loops, firmware lockup, stale J3 data, failed
  temperature sensor, network loss, and Home Assistant loss.
- Do not rely on this candidate design for unattended freeze protection until
  the complete failure matrix has passed live validation.
