# Portable service adapter electrical design

Status: schematic-ready connection definition; package pinouts and values still require independent review

## 1. Electrical overview

The adapter has two isolated service systems that share only the target J5 connector:

1. **UART system:** FTDI host signals cross a galvanic isolation barrier. The target side is powered from the controller's own J5 VDD only while a physical jumper is in UART position. A supervisor and tri-state buffer prevent target drive during startup, brownout, or power loss.
2. **ICSP system:** PICkit pins 1-5 connect directly to J5 pins 1-5. It contains no active component and does not cross the UART isolation barrier.

The adapter contains no power source capable of powering the Bixby controller. J5 VDD is either sensed/supplied by the PICkit or supplied by a separately qualified target arrangement; the adapter does not choose or combine those sources.

## 2. Electrical domains

| Domain | Rails/reference | Included circuits |
| --- | --- | --- |
| Host/FTDI | `VHOST_RAW`, `VHOST`, `GND_HOST` | FTDI connector, host side of U101, U104 LED, host decoupling |
| Target/J3/J5 | `VTGT_RAW`, `VTGT_AUX`, `GND_TGT` | target side of U101, U102, U103, J3, main-board J5, PICkit header, reset phototransistor |

`GND_HOST` and `GND_TGT` shall never be connected by copper, test equipment assumptions, shielding, mounting hardware, or enclosure hardware. The only intended crossings are U101 and U104.

## 3. Reference designators

| Reference | Selected part | Function |
| --- | --- | --- |
| U101 | `ISO7721DWVR` | reinforced 1-forward/1-reverse digital isolator, default output high |
| U102 | `SN74LVC2G126DCUR` | target-side dual non-inverting tri-state buffer with `Ioff` |
| U103 | `TLV803EA42RDBZR` | 4.2 V, delayed, active-low open-drain target supervisor |
| U104 | `VOL618A-3X001T` | isolated FTDI RTS# to MCLR open-collector pull-down |
| F101 | `0805L005/30YR` | host auxiliary resettable fuse, 50 mA hold class |
| F201 | `0805L005/30YR` | target UART auxiliary resettable fuse, 50 mA hold class |
| J101 | six-position polarized adapter header | FTDI cable input |
| J201 | four-position polarized adapter header | J3 target harness |
| J202 | five-position polarized adapter header | main-board J5 target harness |
| J203 | six-position 2.54 mm header | standard PICkit input |
| JP201 | three-position 2.54 mm header | target UART power select/park |
| JP301 | three-position 2.54 mm header | automatic reset arm/park |

Reference designators are reserved for the later schematic and should not be renumbered without updating every table, harness drawing, BOM row, and validation fixture.

## 4. Host power and FTDI connector

### 4.1 J101 pinout

| J101 | FTDI wire | Signal | Treatment |
| ---: | --- | --- | --- |
| 1 | black | `GND_HOST` | host reference only |
| 2 | red | `VHOST_RAW` | FTDI +5 V output |
| 3 | orange | `FTDI_TXD` | host transmit to stove |
| 4 | yellow | `FTDI_RXD` | host receive from stove |
| 5 | green | `FTDI_RTS_N` | optional active-low reset control |
| 6 | brown | `FTDI_CTS_N` | deliberate no-connect in Rev A |

The exact wire order shall be verified against the received genuine cable before the harness drawing is released. Wire color is a construction aid, not a substitute for continuity testing.

### 4.2 Host supply

```text
J101-2 VHOST_RAW
  -> F101
  -> VHOST

VHOST -> C101 1 uF -> GND_HOST
VHOST -> C102 100 nF -> GND_HOST, placed at U101 VCC1
VHOST -> C103 100 nF -> GND_HOST, placed at the U104 LED branch if layout distance requires
```

The host circuit is expected to draw only the U101 side-1 current plus the reset optocoupler LED when RTS# is active. F101 is not a precision current limiter; its trip/hold behavior and voltage drop must be checked against the FTDI cable's output limits.

## 5. UART isolation and signal paths

U101 uses the non-`F` default-high behavior so loss of the opposite side presents UART idle rather than an intentional BREAK. The later schematic must verify the exact `DWV0008A` pin assignment from the current TI drawing.

Functional assignment, matching the present full-controller design:

| U101 function | Connection |
| --- | --- |
| VCC1 | `VHOST` |
| GND1 | `GND_HOST` |
| INB, host-to-target channel | from `FTDI_TXD` through R101 |
| OUTB, host-to-target channel | to U102 channel 1 input |
| INA, target-to-host channel | from U102 channel 2 output |
| OUTA, target-to-host channel | to `FTDI_RXD` through R102 |
| VCC2 | `VTGT_AUX` |
| GND2 | `GND_TGT` |

Recommended host-side series resistors:

- R101: 100 ohm between J101 TXD and U101 host input;
- R102: 100 ohm between U101 host output and J101 RXD.

These values are fault/edge damping, not level shifting. Final values may be reduced or replaced with zero-ohm links after waveform review.

### 5.1 Host transmit to stove receive

```text
J101-3 FTDI_TXD
  -> R101 100 ohm
  -> U101 host-to-target input
  || isolation barrier ||
  -> U101 target output
  -> U102 A1
  -> U102 Y1, enabled only by VTGT_GOOD
  -> R204 330 ohm
  -> J201-1
  -> stove J3 pin 1 / PIC RC7 receive
```

### 5.2 Stove transmit to host receive

```text
stove J3 pin 2 / PIC RC6 transmit
  -> J201-2
  -> R205 330 ohm
  -> U102 A2
       <- R206 47 kohm <- VTGT_AUX
  -> U102 Y2, enabled only by VTGT_GOOD
  -> U101 target input
  || isolation barrier ||
  -> U101 host output, default high on target-side loss
  -> R102 100 ohm
  -> J101-4 FTDI_RXD
```

R206 supplies a weak target-derived idle-high bias when the J3 transmit conductor is open. It must never be connected to VHOST.

## 6. Target UART auxiliary power

### 6.1 Direct target VDD and protected branch

`VTGT_RAW` is the direct J5/PICkit target-voltage node. It must remain direct between J202 pin 2 and J203 pin 2.

A separate branch powers the UART target electronics:

```text
J202-2 / J203-2 VTGT_RAW
  -> F201
  -> JP201 pin 1, UART source

JP201 pin 2
  -> VTGT_AUX

JP201 pin 3
  -> NC_PARK, no other copper

R201 100 kohm: VTGT_AUX -> GND_TGT
```

Shunt positions:

- pins 1-2: `UART POWER`; target UART circuitry may be powered;
- pins 2-3: `ICSP/PARK`; target UART circuitry is disconnected and discharged by R201;
- missing shunt: same safe electrical result as PARK.

The parked pad is deliberately floating. It is not tied to ground, because an incorrectly fitted shunt should not short target VDD.

### 6.2 Decoupling

- C201: 1 uF from `VTGT_AUX` to `GND_TGT`, near JP201/U101;
- C202: 100 nF at U101 VCC2;
- C203: 100 nF at U102 VCC;
- C204: 100 nF at U103 VDD.

The current budget shall include U101 side 2, U102, U103, supervisor pull-up, R206, and leakage across the full operating range. The target branch must remain comfortably below the selected fuse hold current and must not disturb the original PIC supply.

## 7. Target power-good and output gate

U103 monitors `VTGT_AUX`:

```text
U103 VDD   -> VTGT_AUX
U103 GND   -> GND_TGT
U103 RESET# -> VTGT_GOOD
R202 10 kohm: VTGT_GOOD -> VTGT_AUX
R203 100 kohm: VTGT_GOOD -> GND_TGT
```

R203 defines the disabled state while the rail is absent. The pull-up/down combination must be checked against U103 sink current and U102 input thresholds; if needed, R203 may be increased after leakage analysis.

U102 connections:

```text
U102 VCC -> VTGT_AUX
U102 GND -> GND_TGT
U102 OE1 -> VTGT_GOOD
U102 OE2 -> VTGT_GOOD
U102 A1  <- U101 target TX output
U102 Y1  -> R204 -> J3 pin 1
U102 A2  <- R205 <- J3 pin 2
U102 Y2  -> U101 target RX input
```

The selected U102 must retain specified powered-off protection for inputs and outputs at VCC = 0. U103's nominal 4.2 V threshold and delayed release are intended to prevent drive during rail rise and collapse. Exact falling threshold, hysteresis, reset delay, and low-voltage output behavior must be verified for the purchased suffix.

## 8. Isolated automatic reset

The reset circuit is independent of the UART signal isolator.

### 8.1 Host LED branch

```text
VHOST
  -> R301 1.5 kohm
  -> U104 LED anode
U104 LED cathode
  -> J101-5 FTDI_RTS_N

D301 1N4148W placed anti-parallel across the U104 LED
```

RTS# low illuminates U104. R301 shall be recalculated using the selected VOL618A LED forward-voltage range, minimum CTR grade, FTDI low-level capability, and VHOST range. The preliminary 1.5 kohm value targets a few milliamperes, not maximum LED drive.

### 8.2 Target pull-down branch

```text
U104 emitter -> GND_TGT
U104 collector
  -> R302 100 ohm
  -> JP301 pin 1, RESET_SINK

JP301 pin 2
  -> J5_MCLR_VPP
  -> J202-1 and J203-1 direct node

JP301 pin 3
  -> NC_PARK, no other copper
```

Shunt positions:

- pins 1-2: `RESET ARM`; FTDI RTS# may pull MCLR low;
- pins 2-3: `PARK`; MCLR is physically disconnected from the reset transistor;
- missing shunt: reset sink disconnected.

The park pad must not add a clamp, pull-up, capacitance, LED, or test circuit to MCLR. The optocoupler branch may pull low only. PICkit programming requires JP301 in PARK and the FTDI cable disconnected.

## 9. Direct ICSP path

```text
J203 PICkit pin 1 <-> J202 main-board J5 pin 1  MCLR/VPP
J203 PICkit pin 2 <-> J202 main-board J5 pin 2  VDD/VTGT_RAW
J203 PICkit pin 3 <-> J202 main-board J5 pin 3  VSS/GND_TGT
J203 PICkit pin 4 <-> J202 main-board J5 pin 4  PGD
J203 PICkit pin 5 <-> J202 main-board J5 pin 5  PGC
J203 PICkit pin 6     deliberate NC
```

Requirements:

- no switch contact in pins 1-5;
- no ordinary ESD device on MCLR/VPP, PGD, or PGC;
- no capacitor on MCLR, PGD, or PGC;
- no diode in PGD or PGC;
- no series resistor unless Microchip and measured signal-integrity evidence later require one;
- no connection from pin 6 to the target or board; and
- a durable pin-1 mark at J203 and J202.

JP201 in PARK removes the UART auxiliary load from VDD. JP301 in PARK removes the automatic MCLR sink. The PICkit/computer is not galvanically isolated from `GND_TGT` during ICSP; the target must therefore be removed, cold, de-harnessed, and offline.

## 10. Optional indicators and ESD footprints

To preserve cost and power margin, Rev A should ship with no required LEDs. The PCB may reserve, as `DNP`:

- D101/R103: host-power indicator on VHOST/GND_HOST;
- D201/R207: target-ready indicator driven from VTGT_GOOD/VTGT_AUX; and
- one low-capacitance two-line target-domain ESD footprint adjacent to J201 pins 1 and 2.

No optional footprint may narrow the isolation corridor or create a route to the opposite ground. The J3 ESD part may be fitted only after its capacitance, leakage, clamping behavior, and ground reference are qualified.

## 11. Test points

Unfitted exposed pads are required for:

Host bank:

- TP101 `GND_HOST`
- TP102 `VHOST`
- TP103 `FTDI_TXD_AFTER_R101`
- TP104 `FTDI_RXD_BEFORE_R102`
- TP105 `FTDI_RTS_N`

Target bank:

- TP201 `GND_TGT`
- TP202 `VTGT_RAW`
- TP203 `VTGT_AUX`
- TP204 `VTGT_GOOD`
- TP205 `J3_STOVE_RX`
- TP206 `J3_STOVE_TX`
- TP207 `J5_MCLR_VPP`
- TP208 `J5_PGD`
- TP209 `J5_PGC`

The two banks shall be physically separated. Scope and bench-supply grounds can defeat PCB isolation, so the validation procedure must specify probe isolation and connection order.

## 12. Net list summary

| Net | Domain | Required connections |
| --- | --- | --- |
| `GND_HOST` | host | J101-1, U101 GND1, U104 LED return-side reference components, C101-C103 |
| `VHOST_RAW` | host | J101-2, F101 input |
| `VHOST` | host | F101 output, U101 VCC1, U104 LED source, host capacitors |
| `FTDI_TXD` | host | J101-3, R101 |
| `FTDI_RXD` | host | J101-4, R102 |
| `FTDI_RTS_N` | host | J101-5, U104 LED cathode |
| `GND_TGT` | target | J201-4, J202-3, J203-3, U101 GND2, U102/U103, U104 emitter |
| `VTGT_RAW` | target | J202-2, J203-2, F201 input |
| `VTGT_AUX` | target | JP201 center, U101 VCC2, U102 VCC, U103 VDD, target decoupling |
| `VTGT_GOOD` | target | U103 RESET#, U102 OE1/OE2, R202/R203 |
| `J3_STOVE_RX` | target | U102 Y1 through R204, J201-1 |
| `J3_STOVE_TX` | target | J201-2 through R205 to U102 A2, R206 pull-up |
| `J5_MCLR_VPP` | target | J202-1, J203-1, JP301 center |
| `J5_PGD` | target | J202-4, J203-4 |
| `J5_PGC` | target | J202-5, J203-5 |

## 13. Required independent checks before schematic release

- Confirm exact U101, U102, U103, and U104 pin numbers and default states from current manufacturer drawings.
- Confirm U103 ordering code actually provides the intended 4.2 V threshold, open-drain output, and delayed release.
- Calculate R202/R203 logic levels at every leakage and supply corner.
- Calculate U104 LED current and prove reset-low voltage at minimum CTR and maximum target MCLR pull-up current.
- Verify F101/F201 resistance, hold/trip current, voltage rating, and temperature derating.
- Confirm J203 orientation against the PICkit pin-1 triangle and J202 against the target square pad.
- Simulate or bench-prove every partial-power state before committing the connection list to PCB copper.
