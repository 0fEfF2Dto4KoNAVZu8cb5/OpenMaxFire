# Portable service adapter operating and safety rules

Status: preliminary operating contract; physical use remains blocked pending first-article qualification

## 1. Non-negotiable rule

The FTDI/J3 path and PICkit/J5 path are **different service modes**. They must not be connected or used simultaneously.

The adapter does not make an open or energized appliance safe. During ICSP, a PICkit intentionally references the Bixby target ground and therefore bypasses the UART isolation boundary.

## 2. Positive target identification

Before any target cable is inserted:

1. Confirm the appliance is a Bixby MaxFire in the documented family.
2. For J5 work, remove the large main controller and read its complete `PCB Part Number 9067-0604` marking.
3. Confirm that the same PCB carries U3, a 40-pin PIC16F877A.
4. Locate the five-contact J5 beside the PIC and red indicator LED.
5. Identify pin 1 by the square PCB pad, not viewing direction or wire color.
6. Confirm the cable label says `9067-0604 MAIN-BOARD J5 ICSP — NOT IGNITER J5`.
7. Stop if any board number, contact count, physical location, PIC type, key, or continuity result differs.

The separate igniter/power board also has a connector called J5. It is not this interface and may carry 120 VAC.

## 3. Safe/storage state

When the adapter is not actively being used:

- JP201 target power: pins 2-3, `ICSP/PARK`;
- JP301 reset: pins 2-3, `PARK`;
- FTDI disconnected;
- PICkit disconnected;
- J3 and J5 target harnesses disconnected; and
- both shunts accounted for and retained on their park pins.

A missing shunt leaves the associated function disabled and is electrically acceptable, but the adapter shall not be transported with a loose shunt in the enclosure.

## 4. J3 monitor/control mode

This mode is for ordinary serial identification, telemetry, captures, configuration backups, and separately qualified normal commands.

Required configuration:

- PICkit physically disconnected;
- JP201 on pins 1-2, `UART`;
- JP301 on pins 2-3, `PARK`;
- both J3 and `9067-0604` main-board J5 target harnesses connected;
- FTDI connected last; and
- stove/controller power applied only through its normal, separately accepted operating arrangement.

Connection sequence:

1. Verify both target connectors and jumper positions with all sources off.
2. Attach J3 and main-board J5 to the correct controller.
3. Attach the FTDI harness to J101.
4. Apply normal controller power.
5. Connect FTDI USB to the host.
6. Confirm host power, target auxiliary power, and UART idle levels before transmitting.
7. Begin with `maxfirectl identify` or an equivalent read-only transaction.

Disconnection sequence:

1. Stop the software session and close the serial port.
2. Remove FTDI USB.
3. Remove controller/stove power according to the factory procedure.
4. Disconnect J3 and J5 target harnesses.
5. Return JP201 to `ICSP/PARK`.

J3 pin 3 remains unused in every mode.

## 5. Attended J3 reset/loader-entry mode

This mode exists to make reset-time loader entry repeatable without AC cycling or a direct ground connection. It is not permission to transmit physical firmware-programming frames.

Prerequisites:

- the complete ordinary J3 mode has already passed;
- the reset optocoupler, MCLR low level, timing, and release behavior are scoped on expendable hardware;
- the software uses an explicitly reviewed fixture-specific reset executor; and
- an authenticated full-chip rescue image and PICkit recovery path exist.

Procedure boundary:

1. Configure ordinary J3 mode with JP301 still in PARK.
2. Confirm RTS# idle behavior on port open, close, cable insertion, host reset, and application crash.
3. With the software closed and controller in an accepted state, move JP301 to pins 1-2 `RESET ARM`.
4. Perform one attended reset/loader-entry attempt.
5. Return JP301 to PARK immediately after the reset sequence, whether successful or not.
6. Record the exact traffic, timestamps, mode, jumper state, controller identity, and result.

Never leave RESET ARM fitted during normal monitoring, unattended operation, storage, or PICkit use.

## 6. J5 ICSP mode

ICSP is an offline bench operation on a removed controller.

Required state:

- stove cold and mains unplugged;
- main controller removed from the appliance;
- every actuator, igniter, sensor, power, thermostat, J3, and other harness disconnected;
- FTDI and all host USB cables disconnected from the adapter;
- J3 target harness disconnected;
- JP201 on pins 2-3 `ICSP/PARK`;
- JP301 on pins 2-3 `PARK`;
- only the verified main-board J5 harness connected; and
- exactly one target VDD source selected.

### 6.1 Target power decision

The adapter supplies no target power. The PICkit has two possible relationships:

- **PICkit-powered target:** permitted only if measured controller inrush and steady current remain within the tool's supported limit with adequate VDD at the target; or
- **externally powered target:** the controller is powered from a separately reviewed, current-limited low-voltage bench arrangement while PICkit target-power output is disabled and pin 2 senses target VDD.

Never let the PICkit and another source both drive VDD. Do not apply appliance mains merely to make ICSP work.

### 6.2 First J5 operations

The first operation on a target shall be:

1. measure VDD and verify polarity;
2. connect PICkit USB and confirm the expected PIC16F877A device identity;
3. read all program memory, EEPROM, configuration, User IDs, and protection state;
4. save an immutable export and hash manifest;
5. disconnect and repeat the complete read at least twice; and
6. compare all three reads byte-for-byte or by section hash.

Stop immediately if code/data protection is reported or unclear. Erasing to clear protection is destructive.

### 6.3 Write boundary

A write is permitted only after a separate procedure has approved:

- expendable controller/PIC hardware;
- exact source and target identities;
- authenticated firmware, EEPROM, configuration, and User IDs;
- recovery from an interrupted operation;
- full readback and hash comparison; and
- restoration of the target's unique data.

The adapter documentation alone does not authorize erase or programming.

## 7. Prohibited configurations

- FTDI and PICkit attached at the same time.
- PICkit attached while J3 is connected.
- RESET ARM fitted during PICkit operation.
- JP201 in UART while using PICkit.
- Two target VDD sources.
- Target harness insertion or removal while a source is active.
- PICkit operation on an installed or harnessed controller.
- Any connection to the auxiliary igniter-board J5.
- Direct DB9 RS-232, bipolar serial, or an unknown generic USB adapter on J101/J3.
- Connection to J3 pin 3.
- Loose Dupont leads, clips, or unverified color-based wiring.
- Unattended loader/reset operation.
- Use on a controller revision not explicitly supported.

## 8. Stop conditions

Disconnect sources and preserve the setup record if any of the following occurs:

- unexpected board number, connector, pinout, or device ID;
- target VDD absent, reversed, unstable, or outside the accepted range;
- host or target domain becomes powered from the opposite side;
- continuity between `GND_HOST` and `GND_TGT`;
- unexplained current increase, heating, odor, sound, or discoloration;
- J3 pin 1 drives while target UART power is parked or target VDD is absent;
- RTS# affects MCLR while JP301 is parked;
- PICkit reports protection, target-voltage error, VPP error, or device mismatch;
- inconsistent repeated reads;
- any actuator movement during ICSP preparation; or
- loss of certainty about which J5 is connected.

Record adapter serial/revision, controller PCB number, controller serial, both connector faces, jumper positions, attached sources, instrument readings, exact software output, and file hashes before changing the setup further.

## 9. Qualification states

The project shall label each physical adapter with one of these states:

| State | Permitted use |
| --- | --- |
| `ENGINEERING — UNPOWERED ONLY` | continuity, mechanical fit, and insulation tests |
| `UART READ-ONLY QUALIFIED` | J3 identify/monitor/backup only |
| `UART CONTROL QUALIFIED` | specifically listed normal commands with readback |
| `RESET FIXTURE QUALIFIED` | attended MCLR reset/loader entry, no programming implied |
| `J5 READ-ONLY QUALIFIED` | PICkit identity and complete repeated reads on listed board revisions |
| `J5 WRITE QUALIFIED` | only the separately listed expendable/recovery workflows |

Passing a later state does not authorize installed or unattended use unless the release record explicitly says so.
