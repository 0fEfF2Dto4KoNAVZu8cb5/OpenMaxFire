# Firmware 2.06 live input and start qualification

Date: 2026-08-30  
Configuration: checksum-valid format 05 after the documented `CW0100` repair  
Safety condition: no fuel; igniters disconnected; operator present for input
and control actions, then away during the final passive monitor

## One-at-a-time physical inputs

A continuous read-only monitor retained exact traffic and decoded snapshots.
The operator changed only the named input and verbally marked each interval.
CR02 baseline was `12`; bit 4 was already high from the feeder-wheel input and
remained separable from the tested bits.

| Physical action | Before | During | Independent fields |
| --- | --- | --- | --- |
| Firebox door open | CR02 `12` | CR02 `32` | Drawer closed, wood, thermostat closed |
| Ash drawer open | CR02 `12` | CR02 `52` | Door closed, wood, thermostat closed |
| Fuel selector wood→corn | CR02 `12` | CR02 `16` | Both doors and thermostat unchanged |
| Thermostat closed→open | CR06 `03` | CR06 `07` | Both doors and fuel unchanged |

Each input also returned repeatedly to its baseline after the operator restored
it. This live-validates the same 2.06 polarities recovered statically and seen
on the original 2.02 controller: CR02.5 firebox, CR02.6 ash drawer, CR02.2
corn/Fuel A, and CR06.2 thermostat open.

The physical-panel button value was not sampled during the input capture. While
preparing an UP-button test, the operator accidentally pressed ON after that
capture stopped. The physical response and later telemetry independently prove
the start was accepted, but this artifact does not assign a CR01 sample to it.

## Bounded accidental start and cleanup

The next monitor found exact 2.06 Prefill (`T09=30`) with first-light display
T07=`01`, convection command T06=`19`, exhaust target T18=`5C`, and exhaust
feedback T04/CR05 approximately `7F`. This is the first checksum-valid physical
2.06 startup-state capture.

The host transmitted remote OFF (`CW0E11`) at `23:26:27.602845Z`. The controller
still reported Prefill in every snapshot through `23:26:37.735946Z`, so that
first request was not accepted by the state machine. A second and final OFF was
transmitted at `23:26:48.669208Z`. The first complete state sample after the
next monitor opened reported Cooldown (`T09=10`) at `23:26:58.294226Z`, followed
by repeated Cooldown samples. The operator independently observed the active
start turn off.

During cleanup, CR02.4 returned from `1` to `0`, T07 returned to `00`, exhaust
target settled to `57`, and feedback tracked the running cooldown fan. A final
10-second monitor retained repeated Cooldown samples with zero timeouts. The
two command traffic files each contain exactly one `CW0E11`; no other write was
sent in this phase.

## Passive checksum-valid Cooldown completion

After the operator walked away, a read-only monitor followed the accepted
cleanup through autonomous Cooldown completion. The first complete Cooldown
sample after the accepted OFF had been `23:26:58.294226Z`. In the long capture,
the last T09=`10` response was `23:41:29.907099Z`; T18 was still `57` at
`23:41:32.642937Z`, and T06 was still `19` at `23:41:34.543018Z`. The first
post-gap state response was T09=`20` (Off) at `23:41:54.722898Z`.

A 20.18-second serial-response gap therefore brackets the actual transition
between the last nonzero command evidence and first Off response. Adding the
statically recovered 877.893-second 2.06 Cooldown duration to the first
observed Cooldown sample predicts `23:41:36.187Z`, inside that bracket. This is
consistent with the exact firmware timer while honestly retaining the serial
gap; it does not claim a sub-frame transition timestamp.

The first post-gap T18 and T06 responses were `00` at `23:41:57.187064Z` and
`23:41:59.091140Z`. T05 was also zero by the latter time. Measured fan feedback
coasted normally: T04 first reached `00` at `23:42:08.667186Z`, and CR05 first
reached `00` at `23:42:11.960806Z`. Every later complete snapshot through
`23:42:56.509885Z` remained Off with T04/T05/T06/T18 and CR05 all zero. T07 and
T13 remained `00`, and no T20 event was emitted.

The capture retained 189 decoded snapshots and 10,559 accepted frames. It
recovered from 19 read timeouts, including the gap that straddled the state
change. Every transmitted request in this unattended phase was a CR00-CR0E
read; no CW, AW, reset, loader, Checkout, or actuator request was sent.

## Preserved artifacts

- `input-matrix.jsonl` and `input-matrix-traffic.jsonl`: continuous physical
  input capture.
- `accidental-on-off-command-traffic.jsonl`: first OFF request.
- `accidental-on-off-monitor.jsonl` and its traffic file: Prefill evidence after
  the first OFF request.
- `accidental-on-off-retry-command-traffic.jsonl`: second OFF request.
- `accidental-on-off-retry-monitor.jsonl` and its traffic file: first confirmed
  Cooldown after cleanup.
- `post-accidental-start-cleanup.jsonl` and its traffic file: stable final
  Cooldown with zero timeouts.
- `checksum-valid-cooldown.jsonl` and its traffic file: unattended read-only
  Cooldown-to-Off transition and fan coast-down.

The decoded Cooldown capture is 619,243 bytes with SHA-256
`53c5d4ee60ebebf5fe8f2d01530b7e5a2fb1836f975ac5e34fa892d76a0ff802`.
The exact traffic capture is 17,334,521 bytes with SHA-256
`0c6d87e496d5cd74995c765af1431e8e4a174beeb96f3f1b7466b9f0738d57cb`.

No Checkout actuator, direct fan/feed/igniter command, EEPROM write, reset,
loader, or firmware-programming request was sent during this qualification
phase.
