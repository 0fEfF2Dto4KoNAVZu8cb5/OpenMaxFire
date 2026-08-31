# Firmware 2.06 compatibility session

Date: 2026-08-30  
Connection: J3 through the known bare FTDI cable at 9,600 8N1  
Controller condition: separate externally programmed PIC, no fuel, igniters
disconnected  
Initial-identification boundary: read-only CR/A requests and passive telemetry;
later explicitly authorized checksum-repair and normal-control phases are
documented separately

## Result

The controller identifies exactly as firmware 2.06 / data format 05 / build 21:

| Register | Value |
| --- | --- |
| CR00 | `00` |
| CR08 | `05` |
| CR0B | `02` |
| CR0C | `06` |
| CR0D | `00` |
| CR0E | `21` |

The first reply contained a leading NUL before the valid `CR0000` line. The
receive parser was corrected to accept only leading NUL/control resynchronization
bytes. It continues to reject an embedded NUL, and the transmit protocol was not
changed.

Two independent A00-AFF backups contain byte-identical EEPROM data. Their raw
256-byte SHA-256 is
`c1b8da891e94357f1d3bb23004d44aa663943f1d28fb734bef56dfa3e5bd0cfd`.

| Field | Captured value |
| --- | --- |
| Data format | `05` |
| Model | `Bixby Model 115` |
| Serial | `Unknown` |
| Production date | `08282026` |
| Stored checksum | `D168` |
| Calculated checksum | `576B` |

The captured data differs from the complete vendor 2.06 PICkit EEPROM in only
13 identity/checksum bytes. All calibration and fuel-table bytes match vendor
defaults. The image is therefore format-compatible but checksum-invalid, and it
is not a qualified normal-behavior baseline.

The stale checksum's edit order is recoverable exactly. Vendor defaults
(`5015`, `04162007`) calculate to `7068`. Replacing only the serial with
`Unknown` calculates to `D168`, exactly the checksum still stored on the live
chip. Replacing the date as well with `08282026` calculates to `576B`.
Therefore the serial was incorporated into the checksum, after which the date
changed without checksum persistence. The bytes do not identify which program
or workflow performed those edits.

Later in the same session, an explicitly authorized J3 repair sent exactly one
`CW0100`. Firmware changed only A00/A01 from `D1 68` to `57 6B`; two immediate
complete backups and a third after a true AC-off/USB-out cold boot were
byte-identical and reported `576B/576B`. The controller retained exact
2.06/05/21 identity and resumed its normal power-up Cooldown. Full evidence is
in [`checksum-repair/README.md`](checksum-repair/README.md).

The actual 2.06 application was emulated with the captured record and an
otherwise identical copy containing checksum `576B`. Their first control-flow
divergence occurs in the checksum validator around program word `0x0732`; the
invalid path clears configuration-validation flags. This proves that the bad
checksum is firmware-visible. It does not assign every later physical effect,
because the hardware model remains incomplete.

## Fan and flashing-light observation

During the passive baseline the firmware reported:

- T09 `10`: Cooldown.
- T06 `19`: 25% convection command.
- T18 `57`: exhaust target.
- T04 approximately `55`-`5A`: measured exhaust rotation count.
- T05 approximately `5E`-`62`: exhaust phase/control value.
- T13 `02`: raw Alarm-mode value.
- T20 alternating `02`/`00`, coincident with the owner-observed flashing second
  light.

The nonzero command and target fields establish that the fan operation was
intentional firmware output rather than merely a stuck triac. Firmware analysis
also locates the nonperiodic T20 display-event sender in 2.06, 2.70, and 2.71.
The factory fault table describes flashing light 2 as failure to reach operating
temperature, which is consistent with the no-fuel/no-ignition test condition.

The controller left Cooldown without any command. The exact traffic shows the
exhaust target first at zero at `22:50:29.313Z`, T09 first reporting Off at
`22:50:31.600Z`, and measured exhaust speed coasting from `21` through `0F`
and `02` to `00` by `22:50:45.576Z`. Convection command T06 and exhaust target
T18 remained `00`; CR05 reached `00` on the following complete poll. The owner
independently observed that the fan had stopped.

This timing is explained by exact 2.06 code rather than the EEPROM tables. The
firmware configures CCPR1=`C674`, CCP1 special-event compare, and Timer1 at
Fosc/4 with a 1:8 prescaler. At the photographed 10 MHz oscillator, the
16-bit cooldown counter advances every 0.1625728 seconds. The Off branch is
taken after `1518` hexadecimal (5,400) events, subject to its thermocouple and
input predicates: 877.893 seconds, or approximately 14 minutes 38 seconds.
Back-calculating from the live transition gives a power-up near `22:35:51Z`,
consistent with the session start.

T20 continued alternating `02`/`00` after the fan stopped, while T07 sampled
the same `02`/`00` display state and T13 remained `02`. This separates the
latched light-2/no-temperature fault indication from the completed fan
cooldown. A final independent 12-second monitor confirmed stable Off,
T04/T05/T06/T18=`00`, CR05=`00`, and zero read timeouts.

## Preserved artifacts

- `initial-identification/identify-traffic-02.jsonl`: successful exact identity
  exchange.
- `initial-identification/baseline-monitor.jsonl`: short decoded baseline.
- `initial-identification/baseline-monitor-traffic.jsonl`: exact baseline bytes.
- `initial-identification/eeprom-01.json` and `eeprom-02.json`: independently
  decoded complete EEPROM backups.
- `initial-identification/eeprom-01-traffic.jsonl` and
  `eeprom-02-traffic.jsonl`: exact EEPROM request/response bytes.
- `initial-identification/cooldown-monitor.jsonl`: long decoded passive monitor.
- `initial-identification/cooldown-monitor-traffic.jsonl`: exact long-monitor
  bytes.
- `initial-identification/final-off-monitor.jsonl`: independent decoded Off
  confirmation after the fan stopped.
- `initial-identification/final-off-monitor-traffic.jsonl`: exact final
  confirmation bytes.
- `checksum-provenance.json`: reproducible checksum variants establishing the
  identity-edit order.
- `checksum-repair/`: one live-validated `CW0100` repair with complete
  immediate and cold-boot verification.
- `live-qualification/`: one-at-a-time 2.06 input correlations and the bounded
  checksum-valid Prefill/Cooldown control capture, followed by a passive
  Cooldown-to-Off transition. The recovered 877.893-second timer prediction
  falls inside the transition's preserved 20.18-second serial-gap bracket;
  command/target values dropped to zero and measured fan feedback coasted to
  zero with T07/T13 clear.

The initial-identification phase sent no write. Later phases sent exactly one
`CW0100` and two cleanup `CW0E11` requests. No Checkout actuator, direct
fan/feed/igniter command, reset, loader, or firmware-programming request was
sent.
