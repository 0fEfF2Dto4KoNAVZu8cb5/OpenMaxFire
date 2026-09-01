# Target service interface design

Status: **design-review draft; not approved for fabrication, installation, or
energized-stove service**.

Implementation source: [`../src/target-service.tsx`](../src/target-service.tsx).
This document describes that implementation as written. It does not convert a
provisional stove pinout, a library footprint, or a component rating into a
validated product claim. All gates in this document are cumulative with
[`VALIDATION_PLAN.md`](./VALIDATION_PLAN.md).

> **DANGER — TWO DIFFERENT CONNECTORS ARE CALLED J5.** This design connects
> only to the five-contact **9067-0604 main-controller-board J5**, believed to
> be low-voltage PIC ICSP. A separate connector also called **J5 on the
> auxiliary igniter board** is associated with **120 VAC** in the preserved
> factory drawing. Never probe, adapt, or connect the OpenMaxFire J5/PICkit
> cable to the auxiliary igniter-board J5. Location and the complete board part
> number, not the text `J5` by itself, must be checked before connection.

## 1. Scope and safety boundary

The target-service block provides these functions:

- isolated, bidirectional 5 V TTL UART access to stove main-board connector J3;
- a provisional five-wire adapter to the stove main-board J5 ICSP signals;
- a direct standard six-position PICkit header, with PICkit pin 6 deliberately
  unused;
- a target-derived, current-limited interface supply that is enabled only when
  UART service is selected;
- supervised, high-impedance J3 output behavior during target undervoltage or
  loss;
- optional, optically isolated automatic MCLR pull-down from either the ESP32
  or FTDI RTS#; and
- an 8 mm board isolation corridor between controller and target domains.

The block does **not** power the stove controller. `VTGT_RAW` is target voltage
sense and the source for only the target-side isolator and buffers. It also
does not decide which UART source is permitted: upstream mode logic must make
`UART_CONNECT`, `RUN_MODE`, `FTDI_5V_MODE`, and `SERVICE_TX_SELECTED` mutually
consistent and fail open.

No J3 signal, J5 signal, `GND_TGT`, `VTGT_RAW`, or `VTGT_PROTECTED` passes
through the mechanical mode switch. The switch acts only on controller-domain
mode qualification. Four reinforced-isolation components are the only intended
crossings: U401, U404, U406, and U407.

The isolation barrier is intended to prevent ground loops and partial-power
backfeed between the controller/service side and the stove logic side. It is
not evidence that either side may be treated as touch-safe, and it is not a
mains isolation or energized-service authorization. J3 and the main-board J5
are treated as SELV only as a pending measurement assumption.

## 2. Connector definitions

### 2.1 J401 — keyed four-position stove J3 harness

J401 is a JST XH `B4B-XH-A(LF)(SN)` board header. Signal names are from the
stove's point of view: stove RX is an output from this controller, while stove
TX is an input to this controller.

| J401 pin | Stove J3 function | OpenMaxFire net | Direction at J3 | Status |
| --- | --- | --- | --- | --- |
| 1 | Stove RX, PIC RC7/RX/DT | `J3_STOVE_RX` | OpenMaxFire to stove | Live-validated on 9067-0604 serial 5215 |
| 2 | Stove TX, PIC RC6/TX/CK | `J3_STOVE_TX` | Stove to OpenMaxFire | Live-validated on 9067-0604 serial 5215 |
| 3 | Probable target VDD/test function | none | **Deliberate NC** | Must have no copper, pin function, or cable termination |
| 4 | Stove signal ground | `GND_TGT` | reference only | Live-validated on 9067-0604 serial 5215 |

J3 is 5 V TTL, non-inverted UART in the validated installation, not RS-232.
The current protocol baseline is 9600 baud, 8 data bits, no parity, one stop
bit. That does not waive repeated electrical qualification on each supported
stove-board revision.

J3 pin 3 is intentionally unavailable. A production harness should omit that
contact and conductor. If a prototype cable contains the lead, it must be cut
back or individually insulated at both ends; it must never be tied to
`VTGT_RAW`, a protection rail, a pull-up, an LED, or a test point.

### 2.2 J402 — keyed five-position **main-board J5** harness

J402 is a JST XH `B5B-XH-A(LF)(SN)` board header.

> **PROVISIONAL MAPPING — RELEASE BLOCKER.** The table below is a strong working
> mapping for the large `PCB Part Number 9067-0604` main controller only. It
> requires a second independent continuity pass and physical pin-1/orientation
> confirmation on an unpowered spare board before a cable may be released.

| J402 pin | Provisional 9067-0604 main-board J5 signal | OpenMaxFire net | PIC16F877A relationship |
| --- | --- | --- | --- |
| 1 | MCLR/VPP | `J5_MCLR_VPP` | MCLR/VPP |
| 2 | VDD/target-voltage sense | `VTGT_RAW` | VDD |
| 3 | VSS | `GND_TGT` | VSS |
| 4 | PGD/ICSPDAT | `J5_PGD` | RB7/PGD |
| 5 | PGC/ICSPCLK | `J5_PGC` | RB6/PGC |

This connector has no relationship to the auxiliary igniter-board 120 VAC J5.
Production cable and enclosure labels must say, in full:

`9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5`

### 2.3 J403 — direct PICkit header

J403 is the conventional single-row, 2.54 mm, six-position PICkit ICSP header
(`61300611121`). Pins 1 through 5 are directly parallel with J402 and contain
no switch, translator, clamp, LED, or intentional series resistance.

| PICkit pin | PICkit function | OpenMaxFire net | J402 pin |
| --- | --- | --- | --- |
| 1 | MCLR/VPP | `J5_MCLR_VPP` | 1 |
| 2 | VDD/VTGT | `VTGT_RAW` | 2 |
| 3 | VSS | `GND_TGT` | 3 |
| 4 | PGD/ICSPDAT | `J5_PGD` | 4 |
| 5 | PGC/ICSPCLK | `J5_PGC` | 5 |
| 6 | AUX/PGM | none | none; deliberate NC |

The header itself is not shrouded or mechanically keyed. Pin 1 must be marked
on copper/silkscreen and on the cable, and the released enclosure must prevent
or clearly expose reversed insertion. PICkit use deliberately bridges the
external programmer/computer to the target domain and is allowed only by the
offline procedure in Section 9.

### 2.4 J404 — AUTO RESET ARM

J404 is a removable two-pin, 2.54 mm shunt header. It is **not fitted by
default**. Leaving it open physically disconnects both automatic MCLR sink
circuits from `J5_MCLR_VPP`; it does not interrupt the direct J402/J403 ICSP
path.

## 3. Electrical domains and permitted crossings

| Domain | Principal rails/nets | Components and interfaces |
| --- | --- | --- |
| Controller/service | `SERVICE_3V3`, `GND_CTRL`, `UART_CONNECT`, `SERVICE_TX_SELECTED`, `SERVICE_RX_ISOLATED`, `RUN_MODE`, `ESP_MCLR_ASSERT`, `FTDI_5V_MODE`, `FTDI_RTS_N` | U401/U406/U407 LEDs, U404 pins 1–4, their input resistors and controller-side decoupling |
| Stove target | `VTGT_RAW`, `VTGT_PROTECTED`, `VTGT_GOOD`, `GND_TGT`, J3 and J5 signals | U401/U406/U407 phototransistors, U404 pins 5–8, U402, U403, U405, J401–J404 and target-side decoupling |
| Thermostat dry-contact | separate isolated contact domain | Outside this block; must not be joined to either ground here |

There is no DC ground or rail connection between `GND_CTRL` and `GND_TGT`.
The only intended signal crossings are:

| Crossing | Controller side | Target side | Function |
| --- | --- | --- | --- |
| U401 VOL618A | `UART_CONNECT` LED drive | phototransistor from `VTGT_RAW` to U402 ON | isolated target-interface enable |
| U404 ISO7721DWVR | UART TX/RX, `SERVICE_3V3` | UART RX/TX, `VTGT_PROTECTED` | bidirectional digital isolation |
| U406 VOL618A | NORMAL/ESP MCLR LED drive | open collector to automatic reset branch | optional ESP MCLR assertion |
| U407 VOL618A | FTDI 5 V/RTS# LED drive | open collector to automatic reset branch | optional FTDI MCLR assertion |

## 4. Exact UART signal paths

Both target-facing UART conductors pass through one channel of U405
`SN74LVC2G126DCUR`. Its two active-high output enables, U405 pins 1 and 7, are
tied to `VTGT_GOOD`. U405 is powered from `VTGT_PROTECTED` at pin 8 and
`GND_TGT` at pin 4. The 330 ohm resistors are at the J3 edge and limit fault and
contention current; they are not level translators.

### 4.1 Controller or FTDI transmit to stove receive

```text
selected ESP/FTDI TX
  SERVICE_TX_SELECTED
  -> U404 pin 3 INB                  [controller domain]
  || ISO7721 reinforced barrier ||
  -> U404 pin 6 OUTB                 [target domain]
  -> U405 pin 2 A1
  -> U405 pin 6 Y1                   [enabled only by VTGT_GOOD]
  -> R405 330 ohm
  -> J3_STOVE_RX
  -> J401 pin 1
  -> stove J3 pin 1 / PIC RC7 receive
```

### 4.2 Stove transmit to controller or FTDI receive

```text
stove PIC RC6 transmit / J3 pin 2
  -> J401 pin 2
  -> J3_STOVE_TX
  -> R406 330 ohm
  -> U405 pin 5 A2
       <- R411 47 kohm <- VTGT_PROTECTED [target-derived idle bias]
  -> U405 pin 3 Y2                   [enabled only by VTGT_GOOD]
  -> U404 pin 7 INA                  [target domain]
  || ISO7721 reinforced barrier ||
  -> U404 pin 2 OUTA                 [controller domain]
  -> SERVICE_RX_ISOLATED
  -> upstream ESP/FTDI receive routing
```

U404 is the non-`F` ISO7721 variant. Its specified default output on loss of
input power or signal is high, which corresponds to UART idle rather than a
false BREAK. That behavior must still be scoped during partial-power and slow-
ramp tests; it does not justify relying on an undriven input outside the
datasheet conditions.

When `VTGT_GOOD` is low, U405 Y1 is high impedance, so the controller does not
drive J3 pin 1. J3 pin 2 is the stove-to-controller input: after R406, R411
pulls U405 A2 weakly to the target-derived `VTGT_PROTECTED` rail so an open J3
TX conductor reads UART idle high while that rail is valid. It is therefore not
an ideal high-impedance conductor. When target power is removed, R403 discharges
`VTGT_PROTECTED` and R411 becomes only a weak target-domain return; U405's Ioff
feature blocks powered-off back-drive through the buffer. R411 may never be
moved to a controller rail, and its target loading, rail-collapse behavior, and
target-off leakage remain measured release gates.

## 5. Target-derived interface rail and ready qualification

The intended active-high relationships are:

```text
VTGT_INTERFACE_ON = UART_CONNECT AND VTGT_RAW_PRESENT
J3_OE             = VTGT_GOOD
```

`UART_CONNECT` drives U401's LED through R401, 820 ohm, to `GND_CTRL`. On the
target side, U401's collector is at `VTGT_RAW`; its emitter drives U402 ON and
is held off by R402, 100 kohm, to `GND_TGT`. Thus a dead controller/service side
cannot enable the target interface merely because the stove is powered.

U402 is `TPS22948DCKR`:

- pin 1 IN: `VTGT_RAW`;
- pin 2 GND: `GND_TGT`;
- pin 3 ON: isolated U401 enable;
- pin 6 OUT: `VTGT_PROTECTED`;
- pin 4 NC and pin 5 FLT# are unconnected in this revision;
- C401 is 1 uF on the input;
- C402 1 uF and C403 100 nF decouple the output; and
- R403, 47 kohm, discharges `VTGT_PROTECTED` when disabled.

The switch's operating input range is 2.5–5.5 V. Its output-current limit is
130 mA minimum, 240 mA typical, and 350 mA maximum across the stated
temperature range, and it provides reverse-current blocking and thermal
shutdown. The design load must pass at the 130 mA minimum limit; 240 mA is not
a guaranteed available current. `FLT#` is not observed, so current-limit,
thermal, and reverse-current events cannot be distinguished by firmware.

U403 is the exact R-pinout `TLV803EA42RDBZR` supervisor:

- pin 1 RESET# is `VTGT_GOOD`, pulled up to `VTGT_PROTECTED` by R404, 10 kohm;
- pin 2 is `GND_TGT`;
- pin 3 monitors `VTGT_PROTECTED`; and
- C404, 100 nF, is local supply decoupling.

The `42` option has a nominal 4.2 V falling threshold and internal hysteresis.
The `A` option holds its open-drain output low for 130–270 ms (200 ms typical)
after the monitored rail rises above its hysteretic rising threshold. At the
datasheet test conditions, falling below threshold asserts RESET# in at most
50 us. The actual threshold, hysteresis, delay, and behavior during extremely
slow ramps must be measured on assembled hardware.

Below the supervisor's guaranteed low-voltage operating region its output is
not itself a valid logic guarantee, but `VTGT_GOOD` is pulled only to the same
collapsing rail and U405 is also powered from that rail. U405 Ioff, the load
switch off state, and the 47 kohm discharge path are therefore all part of the
power-off safety case; validation may not rely on U403 alone.

`VTGT_PROTECTED` powers only U404's target side, U405, U403, and their local
decoupling. It must never be connected to the stove VDD pin as a power output.

## 6. Automatic MCLR behavior

The automatic reset functions are wired-OR, target-side open-collector sinks.
They can pull MCLR low; they cannot source MCLR or VPP. Their active-low effect
is:

```text
ESP_MCLR_LOW  = AUTO_RESET_ARMED AND RUN_MODE
                AND ESP_MCLR_ASSERT

FTDI_MCLR_LOW = AUTO_RESET_ARMED AND FTDI_5V_MODE_PRESENT
                AND NOT FTDI_RTS_N
```

### ESP path

`RUN_MODE -> R407 1 kohm -> U406 LED -> Q401 drain`. Q401 is a BSS138 with its
source at `GND_CTRL`, gate at active-high `ESP_MCLR_ASSERT`, and R408, 100
kohm, holding the gate low. Loss of NORMAL qualification removes U406 LED
current independently of ESP GPIO state.

### FTDI path

`FTDI_5V_MODE -> D402 -> R409 1.5 kohm -> U407 LED -> FTDI_RTS_N`. RTS# must
sink low to illuminate U407. D402, `PMEG2010AEH`, admits current only from the
selected FTDI rail and prevents the unpowered `FTDI_5V_MODE` node from being
back-fed through the LED branch. D401, `1N4148W`, remains anti-parallel with the
optocoupler LED to limit reverse LED stress from cable transients or opposite
drive.

### Shared target-side branch

U406 and U407 emitters return to `GND_TGT`; their collectors join, pass through
R410, 100 ohm, and reach J404 pin 1. Only a fitted J404 shunt connects that node
to `J5_MCLR_VPP` on pin 2. R410 is therefore present only in the automatic
reset branch. The direct J402-to-J403 MCLR/VPP path remains unresisted and
VPP-capable.

The VOL618A target transistor has an 80 V collector-emitter rating, but the
automatic arm shunt must nevertheless be removed for PICkit operation. This
eliminates unintended VPP loading and tool contention and is the required
offline service state. Treat FTDI drivers' RTS/DTR behavior on cable insertion,
port open, reset, and close as uncontrolled until characterized; never leave
AUTO RESET ARM fitted during normal unattended operation.

## 7. Operating and fault truth table

The table assumes upstream mode logic is break-before-make, cross-inhibited,
and drives `UART_CONNECT` low for OFFLINE, open-contact, contradictory, or
unqualified states. This block consumes that result; it does not independently
prove selector validity.

| Condition | `UART_CONNECT` | Target interface | J3 behavior | Automatic MCLR | Direct J402/J403 ICSP |
| --- | ---: | --- | --- | --- | --- |
| Valid NORMAL, target rail healthy and release delay elapsed | 1 | U402 on; `VTGT_GOOD=1` | ESP TX/RX connected through isolation | ESP may pull low only if J404 armed and `ESP_MCLR_ASSERT=1`; FTDI path unavailable | Electrically present, but connecting a programmer is prohibited in NORMAL |
| Valid NORMAL, target absent or `VTGT_PROTECTED` below threshold | 1 | off, collapsing, or not ready | J3 pin-1 output high impedance; pin-2 input retains only R411's weak bias to the collapsing target rail | No valid automatic reset action may be assumed | Not in use |
| NORMAL qualification lost | 0 | U401 off; U402 off; R403 discharges rail | Transitions to high impedance; any decay transient must be bounded in test | ESP path disabled because `RUN_MODE=0` | Not in use |
| Valid FTDI SERVICE, FTDI cable/power valid, target ready | 1 | U402 on; `VTGT_GOOD=1` | FTDI TX/RX connected through isolation; ESP excluded upstream | FTDI RTS# may pull low only with J404 armed | Programmer prohibited while FTDI is connected |
| FTDI SERVICE selected but FTDI cable/power absent | 0 by upstream contract | off | high impedance | FTDI optocoupler has no LED current | Not in use |
| PICkit/OFFLINE | 0 | off even if PICkit supplies `VTGT_RAW` | high impedance | Both mode-qualified opto LED paths off; J404 must remain open | Pins 1–5 direct; pin 6 NC |
| Selector between positions, open, or contradictory | 0 by upstream contract | off | high impedance | no automatic reset | Use prohibited until selector state is stable |
| Controller/service power lost while stove remains powered | 0 after power loss | U401 loses LED current, U402 opens, protected rail discharges | high impedance after bounded turn-off; ISO7721 non-F default is UART-idle high during signal loss | no controller-side LED drive | No programmer connection |
| Stove/target power lost while service side remains powered | don't care | no `VTGT_RAW`; protected rail at 0 V | high impedance; U405 Ioff blocks backfeed | target-side open collectors unpowered | no target available |
| Target brownout below nominal 4.2 V falling threshold | may remain 1 | load switch can remain on, but `VTGT_GOOD` asserts low | U405 disables both channels | MCLR branch state is independent; do not use it as brownout protection | no programmer connection |
| `UART_CONNECT` stuck high with source-side UART supply absent | 1 fault | target rail may remain on | ISO7721 non-F default should produce idle high, not BREAK; must be fault-injection tested | mode equations still apply | no programmer connection |
| J404 mistakenly left armed but neither reset request is active | any | unchanged | unchanged | no pull-down expected, but this is a service-configuration fault | PICkit connection still prohibited until shunt removed |
| All sources absent | 0 | off | high impedance | off | inactive |

In unqualified rows, “high impedance” describes the actively driven J3 pin-1
output. The stove-to-controller pin-2 conductor retains R406 plus R411's weak
target-derived bias; acceptance tests must record that load and leakage rather
than treating both conductors as identical tri-state outputs.

The thermostat fail-safe relay is outside this block. Mode transitions and
service modes must force that separate subsystem to passive thermostat backup;
successful J3 communication is never permission to defeat the thermostat
fallback.

## 8. Isolation and physical-layout intent

The source places an 8 mm-wide, 102 mm-tall, all-layer keepout centered at PCB
`x=-23 mm`, extending beyond both edges of the 100 mm-tall board. Target
components and connectors are on the left; controller-side logic is on the
right. Only U401, U404, U406, and U407 may cross it.

The three VOL618A-3X001T optocouplers use Vishay's option-1 LSOP-4, specified
for at least 8 mm creepage and clearance and a 5 kVrms, one-minute UL 1577
withstand test. U404 is the wide-body eight-pin `ISO7721DWVR` (`DWV` package),
the non-F, default-high, reinforced-isolation variant. These component ratings
do not establish the assembled board's working-voltage category or regulatory
compliance.

The final PCB must preserve the required shortest creepage and clearance path,
not merely an 8 mm nominal rectangle. Measure from exposed conductive feature
to exposed conductive feature around every crossing package and board edge.
No trace, plane, via, thermal relief, test pad, fiducial, solder-mask opening,
silkscreen conductive ink, mounting hardware, shield, enclosure feature,
contamination path, or harness hardware may bridge or narrow the corridor.

Any claim of basic or reinforced insulation requires a separate standards
review using actual working and transient voltages, pollution degree, material
group/CTI, altitude, coating, enclosure, manufacturing tolerances, and the
applicable appliance standard. Slots or additional spacing must be added if
that review requires them.

## 9. Installer and service rules

1. Identify the large stove main PCB and read the full `9067-0604` marking.
2. Distinguish its low-voltage J3 and provisional main-board J5 from the
   auxiliary igniter-board J5 associated with 120 VAC.
3. Make the stove cold and off. Disconnect mains, actuators, igniters, J3, USB,
   and all other programmers or service adapters before PICkit work.
4. Verify the cable label, key, pin-1 marks, and both connector locations before
   insertion. Never force a connector.
5. For normal or FTDI UART service, leave PICkit disconnected. For PICkit
   service, leave J3, FTDI, USB, and AUTO RESET ARM disconnected.
6. During PICkit service, configure exactly one VDD source. Never let the stove
   and PICkit both source VDD. Measure before connecting, and begin with a
   read-only operation on a spare controller.
7. Fit J404 only for an explicit, attended UART reset procedure. Remove and
   account for the shunt immediately afterward.
8. Do not perform energized probing because an isolation component appears on
   the OpenMaxFire board. The barrier does not isolate the technician from all
   stove hazards.

J401 and J402 are polarized JST XH headers, but the released harness must also
use incompatible position counts, distinct colors/labels where practical,
strain relief, and board-revision tags. The unshrouded J403 PICkit header needs
a durable pin-1 mark and a cable that makes orientation unmistakable. J3, the
main-board J5, thermostat, and igniter harnesses must not be physically or
visually interchangeable.

## 10. Critical parts and footprint gates

| Ref. | Exact part | Function | Fabrication gate |
| --- | --- | --- | --- |
| U401, U406, U407 | [VOL618A-3X001T](https://www.vishay.com/docs/82405/vol618a.pdf) | reinforced optocouplers | Verify option-1 ordering suffix, pins 1=A/2=K/3=E/4=C, actual LSOP-4 land pattern, pad spacing, package outline, and 8 mm creepage |
| U402 | [TPS22948DCKR](https://www.ti.com/lit/ds/symlink/tps22948.pdf) | target-interface load switch | Verify TI DCK/SC70-6 pins 1 IN, 2 GND, 3 ON, 4 NC, 5 FLT#, 6 OUT and recommended layout/capacitance |
| U403 | [TLV803EA42RDBZR](https://www.ti.com/lit/ds/symlink/tlv803e.pdf) | 4.2 V, 200 ms supervisor | Verify **R pinout**: 1 RESET#, 2 GND, 3 VDD; do not substitute the DBZ default or V pinout |
| U404 | [ISO7721DWVR](https://www.ti.com/lit/ds/symlink/iso7721.pdf) | bidirectional reinforced UART isolation | Verify `DWV0008A`, eight-pin wide-body package—not D-8 or DW-16—including pin pitch, body length, lead span, pin 1, and land pattern; verify non-F ordering |
| U405 | [SN74LVC2G126DCUR](https://www.ti.com/lit/ds/symlink/sn74lvc2g126.pdf) | target-side dual tri-state buffer | Verify TI DCU/VSSOP-8 crossed output numbering: 1 OE1, 2 A1, 3 Y2, 4 GND, 5 A2, 6 Y1, 7 OE2, 8 VCC |
| Q401 | BSS138BK,215 | ESP reset LED sink | Verify SOT-23 1 G, 2 S, 3 D for the exact suffix and rotation |
| D401 | 1N4148W-7-F | FTDI opto-LED reverse clamp | Verify SOD-123 pin-1-cathode polarity and anti-parallel placement |
| D402 | PMEG2010AEH,115 | FTDI reset-branch backfeed block | Verify SOD-123F pin-1-cathode polarity and prove no current can lift an unpowered `FTDI_5V_MODE` node |
| J401/J402 | JST `B4B-XH-A(LF)(SN)` / `B5B-XH-A(LF)(SN)` | keyed stove harnesses | Verify mating housing/contact, latch direction, board-edge clearance, cable-face versus board-face numbering, and pin-1 marking |
| J403 | Würth `61300611121` | direct PICkit header | Verify standard PICkit order, no rotation, pin 6 NC, and enclosure access/orientation control |
| J404 | Harwin `M20-9990245` | removable reset arm | Build and ship with no shunt fitted; silkscreen must remain visible |

Generic CAD-library names are not approval evidence. Before fabrication, an
independent reviewer must compare every symbol pin number, footprint pad
number, recommended land pattern, courtyard, assembly orientation, and 3D
body against the current manufacturer's drawing. In particular, the VOL618A
LSOP-4 and ISO7721 `DWV0008A` footprints are isolation-critical release gates.

## 11. Validation and release gates

Every item below needs a recorded result, instrument/setup identification,
board serial number, reviewer, and date. A failed or skipped item blocks use on
a production stove.

### 11.1 Design-file and fabrication review

- [ ] Independently check all exact MPNs, pin maps, value tolerances, voltage
  ratings, temperature grades, lifecycle status, and approved alternates.
- [ ] Confirm J401–J404 schematic numbering matches PCB pad numbering, mating
  connector numbering, cable drawing, and installer labels.
- [ ] Confirm J401 pin 3 and J403 pin 6 have no copper, test pad, plane, via,
  component, or hidden net connection in schematic, PCB, and Gerbers.
- [ ] Confirm J402 and J403 pins 1–5 are direct one-to-one connections; verify
  no automatic-reset 100 ohm resistance appears in the direct MCLR/VPP path.
- [ ] Confirm R410 is present only before J404 in the automatic open-collector
  branch and that the default BOM does not include a J404 shunt.
- [ ] Confirm U405 OE1 and OE2 connect only to `VTGT_GOOD` and its VCC connects
  only to `VTGT_PROTECTED`.
- [ ] Confirm U402 OUT never reconnects to J402/J403 VDD; the load switch powers
  only the interface electronics.
- [ ] Run type, netlist, pin, short, schematic-placement, PCB-placement, and
  routing checks with zero unexplained errors.
- [ ] Inspect the generated schematic, PCB, both/all copper layers, solder
  masks, drill files, Gerbers, assembly drawings, pick-and-place data, BOM, and
  3D model; source-code success alone is insufficient.
- [ ] Measure the complete isolation path in fabrication outputs and prove only
  U401/U404/U406/U407 cross it. Resolve copper-pour and keepout behavior on
  every layer.
- [ ] Complete independent schematic review, safety review, FMEA, source/artifact
  hash capture, and signed release record.

### 11.2 Stove interface evidence

- [ ] On an unpowered spare 9067-0604 board, independently re-prove J3 pins 1,
  2, 3, and 4; then repeat live direction, idle voltage, logic thresholds,
  source impedance, polarity, and 9600-8-N-1 behavior with actuators and
  igniters disconnected.
- [ ] Establish a supported-board revision list. Reject or separately qualify
  any board whose complete marking or connector orientation differs.
- [ ] Independently continuity-map main-board J5 to MCLR/VPP, VDD, VSS, RB7/PGD,
  and RB6/PGC and photograph the square pad/pin-1 orientation. This closes the
  provisional J5 blocker only after second-person sign-off.
- [ ] Measure main-board J5 VDD minimum/nominal/maximum voltage, current-source
  capability, source impedance, startup, shutdown, reset, and brownout behavior.
- [ ] Prove by location, labeling, and incompatible harnessing that the cable
  cannot mate with the auxiliary igniter-board 120 VAC J5.

### 11.3 Unpowered bare-board and assembly tests

- [ ] AOI/microscope-inspect polarity, pin 1, solder bridges, contamination,
  missing parts, tombstones, and barrier damage.
- [ ] Measure resistance to ground on `SERVICE_3V3`, `VTGT_RAW`,
  `VTGT_PROTECTED`, `VTGT_GOOD`, UART, MCLR, PGD, and PGC nets before power.
- [ ] Prove no DC continuity between `GND_CTRL` and `GND_TGT`, across the
  isolation corridor, or into the thermostat dry-contact domain.
- [ ] Prove direct PICkit continuity and resistance for pins 1–5 and open
  circuit for pin 6. Confirm no unintended pull-up, clamp, LED, or rail path.
- [ ] Verify J404 open as built and continuity only when the removable service
  shunt is deliberately installed.
- [ ] Check every harness conductor end-to-end, perform a wrong-position and
  reversed-insertion review, verify strain relief/pull strength, and inspect
  all board-revision, pin-1, and hazard labels.

### 11.4 Single-domain and partial-power bench tests

- [ ] Power each source/domain alone: permanent controller supply, USB,
  FTDI VCC, stove `VTGT_RAW`, and PICkit VDD. Record every rail and source
  current for every combination allowed by the test matrix.
- [ ] With target power absent and service power present, measure J3 pin leakage
  over voltage and temperature; confirm no backfeed raises `VTGT_RAW` or
  `VTGT_PROTECTED`.
- [ ] Open the stove-side J3 pin-2 conductor and prove R411 establishes UART idle
  high only from `VTGT_PROTECTED`. Measure the R406/R411 target load, rail-ramp
  behavior, and target-off leakage; never count pin 2 as an ideal tri-state path.
- [ ] With stove target power present and all controller/service sources absent,
  confirm U402 remains off, `VTGT_PROTECTED` discharges, the J3 pin-1 output is
  high impedance, R411 provides no foreign-rail source at pin 2, and no
  controller rail rises.
- [ ] Test both sides unpowered, each side powered alone, both powered, power
  applied in both orders, slow ramps, brownouts, hot plug, repeated cycling,
  and abrupt removal.
- [ ] Scope J3 pin 1 and `SERVICE_RX_ISOLATED` throughout every transition.
  There must be no unintended low pulse long enough to be interpreted as UART
  BREAK, a bootloader request, or valid data.
- [ ] Define and meet numeric leakage, discharge-time, and high-impedance
  acceptance limits before release; do not accept a qualitative DMM result.

### 11.5 Target-interface rail tests

- [ ] Sweep `VTGT_RAW` across U402's complete intended range and measure U401
  enable margin, U402 ON/OFF behavior, voltage drop, turn-on slew, inrush, and
  R403 discharge time at minimum/nominal/maximum temperature and load.
- [ ] Demonstrate that worst-case steady and startup load stays below the
  TPS22948 130 mA minimum current-limit value with margin.
- [ ] Short and overload `VTGT_PROTECTED` using a current-safe bench setup;
  record current limiting, thermal cycling, recovery, and any disturbance of
  stove VDD. Verify the unobserved FLT# limitation is acceptable.
- [ ] Force reverse-voltage conditions within rated limits and verify reverse
  blocking without lifting `VTGT_RAW` or the stove VDD rail.
- [ ] Measure U403 falling threshold, rising threshold/hysteresis, fault-assert
  delay, and 130–270 ms release interval across temperature, ramp rate, and
  supply tolerance.
- [ ] Confirm U405 outputs are high impedance below `VTGT_GOOD` and enable only
  after the complete supervisor delay. Include the supervisor region below its
  guaranteed 0.7 V reset-output specification.
- [ ] Separately verify the J3 pin-2 receive input remains bounded by R406/R411
  throughout that sweep and cannot lift a target or controller rail.
- [ ] Verify local decoupling, output-capacitance choice, supply ripple, and
  stability against the current U402/U403/U404/U405 datasheets and the final
  routed layout.

### 11.6 UART functional and abuse tests

- [ ] Scope both exact paths in Section 4 in NORMAL and FTDI SERVICE. Confirm
  direction, non-inverted polarity, 5 V target levels, idle high, timing, rise
  and fall times, and absence of contention.
- [ ] Verify upstream mux exclusivity: ESP and FTDI transmitters can never drive
  `SERVICE_TX_SELECTED` simultaneously, including switch travel and partial
  power.
- [ ] Verify valid data and error rate at all supported baud rates, cable
  lengths, temperatures, and radio/relay load conditions.
- [ ] Inject stuck-high, stuck-low, malformed-byte, BREAK, cable-open,
  cable-short, cross-wired TX/RX, target-reset, and service-reset faults. Ensure
  no unsafe stove command is inferred from link state.
- [ ] Apply bounded ESD/EFT and common-mode disturbance tests only under an
  approved test plan; inspect both function and latent damage afterward.
- [ ] Confirm J3 pin 3 remains electrically uninvolved in every test fixture
  and released harness.

### 11.7 Automatic MCLR tests

- [ ] With J404 open, exercise every mode, ESP GPIO state, FTDI cable event,
  RTS# transition, software crash, reset, power sequence, and target voltage.
  Prove no automatic circuit can pull `J5_MCLR_VPP` low.
- [ ] With J404 deliberately armed on a spare target, verify NORMAL reset occurs
  only for `RUN_MODE=1` and `ESP_MCLR_ASSERT=1`; measure low voltage, sink
  current, pulse width, and release.
- [ ] With J404 deliberately armed, verify FTDI reset occurs only with valid
  `FTDI_5V_MODE` and RTS# low. Characterize plug-in, enumeration, port-open,
  port-close, suspend, disconnect, and host-crash behavior.
- [ ] Verify D401 polarity and measure optocoupler LED reverse voltage in all
  FTDI drive and partial-power states.
- [ ] Verify D402 polarity and demonstrate that RTS#, controller power, and
  target power cannot backfeed an unpowered `FTDI_5V_MODE` node.
- [ ] Confirm simultaneous ESP and FTDI LED drive is prevented upstream; then
  fault-inject it on the bench and verify the wired-OR sinks remain within all
  ratings.
- [ ] With J404 removed and automatic optocouplers off, apply the PICkit VPP
  waveform and measure MCLR loading/leakage. Confirm R410 is absent from the
  measured direct path.
- [ ] Prove the enclosure/service process makes it difficult to leave J404
  fitted and includes positive shunt-accounting after service.

### 11.8 PICkit/offline qualification

- [ ] Use a spare or sacrificial controller first, with stove mains, actuators,
  igniters, J3, USB, FTDI, and AUTO RESET ARM disconnected.
- [ ] Verify PICkit pin order at both cable ends immediately before insertion.
- [ ] Measure target VDD before enabling PICkit power and prove exactly one
  source powers VDD. Record current limit and target current.
- [ ] Begin read-only: identify the target and preserve/read flash, EEPROM,
  configuration words, user IDs, and calibration data before any write.
- [ ] Verify MCLR/VPP amplitude and waveform, PGD/PGC levels and edge quality,
  and target current without exceeding PIC, connector, or interface ratings.
- [ ] Prove `UART_CONNECT=0`, U402 off, `VTGT_PROTECTED` discharged, and J3 pin 1
  high impedance even when PICkit supplies `VTGT_RAW`; separately record the
  bounded pin-2 load through R406/R411.
- [ ] Qualify interrupted operations and recovery only on sacrificial hardware.
  A successful read does not authorize a production-stove write.

### 11.9 Isolation, environmental, and production qualification

- [ ] Have the applicable insulation/standards review approve working voltage,
  transient category, pollution degree, CTI/material group, altitude,
  creepage, clearance, enclosure, coating, and test voltage.
- [ ] Perform insulation resistance and hipot only to that written plan on an
  isolated test article. Never improvise a mains test on installed stove
  hardware.
- [ ] Inspect and measure barrier geometry after fabrication, assembly,
  cleaning, coating, enclosure installation, mounting hardware, and harness
  installation.
- [ ] Validate minimum/maximum ambient, humidity/condensation assumptions,
  vibration, connector retention, cable abrasion, thermal cycling, and aging.
- [ ] Complete EMC/ESD/EFT qualification appropriate to the final enclosure and
  cable installation.
- [ ] Define a serialized production test that checks connector continuity,
  deliberate NCs, domain isolation, rail threshold/delay, J3 pin-1 high
  impedance, R411 receive-path bias/leakage, both UART directions, and
  J404-open MCLR isolation on every unit.
- [ ] Release assembly drawings, harness drawings, BOM/alternate controls,
  factory-test limits, calibration requirements, installation instructions,
  service/recovery instructions, and the explicit remaining-limitations list.
- [ ] Obtain independent hardware, safety, firmware, installer-documentation,
  and manufacturing sign-off before connection to a non-sacrificial stove.

## 12. Review disposition

Fabrication and field use remain blocked until, at minimum:

1. the main-board J5 provisional map and pin-1 orientation are independently
   confirmed;
2. every isolation-critical symbol and footprint is checked against the exact
   orderable part and generated fabrication output;
3. the partial-power, brownout, high-impedance, UART-idle, target-current, and
   MCLR tests above have numeric acceptance limits and passing evidence;
4. harness keying and labels positively separate the main-board J5 ICSP cable
   from the auxiliary igniter-board 120 VAC J5; and
5. the full controller safety case, thermostat fallback, and release plan have
   independent sign-off.
