# Physical J3 flash-session forensics

Status: complete retrospective of the 2026-08-29/30 serial-5215 sessions. No
new hardware traffic was generated for this analysis. The saved session
directories are evidence and must remain unedited.

## Bottom line

Two independent problems occurred:

1. The first three programming entries used the wrong byte order inside each
   PIC word. The additive block checksum could not detect the swap. That defect
   is corrected and is now covered by authenticated wire-image and PICkit-image
   regression tests.
2. The corrected frame has **never reached the physical controller**. Every
   later attempt failed before loader identification, so deterministic reset-
   time entry is the blocker actually observed in those runs. The corrected
   programming path remains physically untested and can still contain other
   undiscovered defects.

Do not send further physical loader traffic with the bare-FTDI/manual-AC/BREAK
procedure. It can pass ordinary UART traffic and often enters the loader, but
the shared reference and partial-power behavior remain unqualified and entry is
not deterministic. Historical zero-write sessions are evidence, not an
authorization to repeat the setup.

## Corpus-wide result

Across all saved `rehearsal-traffic.jsonl` and `loader-traffic.jsonl` files:

| Item | Count | Interpretation |
| --- | ---: | --- |
| Host `EA` identify probes | 13,879 | Repeated, non-writing loader probes |
| PIC `EB` identify replies | 13 | Definitive loader entries |
| Host-recorded `E3` attempts | 12 | All use the former, incorrect low-byte-first word order; TX was recorded before the underlying write |
| PIC `E7` replies | 3 | Three frames passed the order-insensitive byte-sum check |
| PIC `E5` / `E8` replies | 0 / 0 | No reported write-verify or checksum rejection |
| Host `ED` completions | 10 | Zero-write rehearsal handoffs |
| PIC final `E4` replies | 10 | Ten completed `EA/EB` -> `ED/E4` rehearsals |

The 12 recorded `E3` attempts all carry the old relocated-vector payload pattern
`18 30 8A 00 00 28 ...` (preceded by checksum `BC`). No physical traffic file contains the corrected
high-byte-first pattern. Because the recorder logged TX before calling the
underlying transport, the 12 records are transmission attempts, not proof that
all 12 complete frames reached the wire. The three subsequent `E7` replies
prove that at least three complete old-format frames reached the controller.
Ten rehearsals completed without an `E3`, proving that the resident loader,
9,600-baud link, `EA/EB`, and `ED/E4` handoff all work through the bare cable
when entry happens.

All 24 saved EEPROM images decode to the same 256 bytes, with SHA-256
`5ceb73151c785a4561f37abe5f379bd1f94d3b6833fc83636453d82124174f0e`.
The experiments did not change calibration EEPROM.

The counts, frame classification, EEPROM hashes, result/journal summaries, and
per-log probe cadence are reproducible with the read-only analyzer:

```bash
python3 tools/analyze_flash_sessions.py --repo-root .
```

It matches each `E3` against a session-declared, byte-for-byte hash-matched
local Intel HEX image rather than guessing byte order from the first payload
alone. This analyzer does not independently apply the canonical firmware
allowlist.

## What happened in the programming attempts

The first damaging session, `fw202-to-fw206-003`, received `EB` on identify
attempt 290. The saved timestamp for the first old-format `E3` record was about
2.58 ms after the `EB` record; the `E7` record was about 45.46 ms after that
TX record and no `E4` followed. Those are saved-event separations, not UART
latencies, because old TX audit records preceded serialization, durability
work, and the underlying write. Recovery sessions 004 and 005 recorded the
same old first block and produced the same `E7`-then-silence result.

PICkit readback localized the change to three relocated reset words:

| Address | Original | Read back |
| ---: | ---: | ---: |
| `0x1E84` | `0x3018` | `0x1830` |
| `0x1E85` | `0x008A` | `0x0A00` |
| `0x1E86` | `0x2800` | `0x0028` |

Those are exact byte swaps. Resident-loader code outside its four mutable
reset-trampoline slots, configuration, User IDs, and EEPROM remained intact;
the only changed locations were three of those slots. The invalid trampoline
explains why the application could not boot after handoff, but it does not
explain the missing per-block `E4`, which should precede `ED`; that silence
remains unresolved. The operator reported
restoring the sole hash-pinned pre-write 2.02 PICkit image. The controller then
showed a normal boot and matching read-only J3 identity/EEPROM. No post-program
whole-chip readback or retained IPE Program/Verify log independently proves the
programmed bytes.

After the host conversion was corrected:

- `fw202-to-fw206-corrected-007` completed its non-writing rehearsal, but its
  programming entry never received `EB`. It sent no `E3` and caused no change.
- `fw202-to-fw206-corrected-dense-008` transmitted 5,000 `EA` probes over
  59.7367 seconds, received no `EB`, sent no `E3`, and caused no change.

The correct physical write path therefore remains untested, rather than tested
and rejected.

## The dense-probe run exposed a logged host-side timing risk

The 4,999 gaps between saved `EA` events in corrected-dense-008 were:

| Statistic | Gap |
| --- | ---: |
| Minimum | 10.825 ms |
| Median | 11.771 ms |
| Mean | 11.950 ms |
| 99th percentile | 12.836 ms |
| Maximum | 255.301 ms |

Seven gaps exceeded 50 ms and three exceeded 100 ms. A cluster of
165.841/255.301/146.649 ms gaps occurred near 02:58:48 UTC. Numerically, the
maximum saved-event gap exceeds the loader's reconstructed roughly 200 ms
first-byte window, but AC-on was not timestamped and these were not wire-time
events. The corpus cannot show that this gap overlapped a reset window or
caused a missed entry.

Before the timing fix, each audit event was serialized, flushed, and `fsync`'d
*before* `transport.write()`. Each actual programming session also performed a
durable journal write for stale application bytes inside the identify loop.
The old timestamp therefore described host work before a serial write, not the
time at which the byte reached the OS serial driver. Those blocking operations
were a plausible contributor, not a proven cause of the observed gap.

The retained simulator/future-fixture executor now:

- writes each non-state-changing `EA` first and timestamps it immediately after
  the serial flush;
- buffers probe evidence during the short timing window;
- aggregates unexpected probe data instead of journaling it in-loop;
- makes the accumulated evidence durable after identify succeeds or exhausts;
- restores per-event pre-write durability before `ED` or any `E3`; and
- refuses to send the first `E3` if that durability barrier fails.

These changes remove one source of missed windows in the tested state machine.
All physical loader traffic is now hard-disabled in the CLI and public
executors, so they cannot reuse the retired manual electrical reset boundary.

## Reconstructed reset-time behavior

The 2.02 and 2.06 resident loaders are byte-identical. Reset enters the loader
at `0x1E88`; a normal POR or MCLR state with `STATUS.TO=1` initializes the UART
at 9,600 baud and waits for one byte. A watchdog reset with `TO=0` takes the
relocated application path.

The initial receiver is unforgiving:

- `EA` enters servicing and returns `EB`;
- any other byte value successfully returned from `RCREG` immediately
  transfers to the application; framing/overrun faults are unchecked and may
  instead yield a wrong byte, timeout, or stalled receive; and
- the receiver does not explicitly recover UART framing or overrun errors.

After `EA/EB`, repeated `EA` bytes are safe and receive `EB`; `E3` programs and
`ED` completes.

The first-byte timeout was originally reported as 78 ms. Re-reading the loader
corrected that value. `T1CON=0x21` uses the instruction clock with a 1:4
prescaler. A pre-set Timer1 flag consumes the first of the counter's three
iterations immediately, leaving two real overflows from `TMR1H=0x0B` at a
10.000 MHz oscillator: approximately 200 ms.

## Why `CW0FC4` cannot bootstrap this controller

BixCheck 5.5.01 contains `AttemptStoveReset()`, which sends `CW0FC4`, and its
identify routine then sends `EA` in a tight loop. That software reset is useful
only when the installed application implements it.

The exact original 2.02 image does not. Its computed C-write table has only 15
GOTOs, for `CW00` through `CW0E`; `CW0F` lands on three NOPs, and the image has
no `SUBLW 0xC4` keyed handler. In 2.06, the sixteenth entry dispatches to
`0x110B`, tests `0xC4`, and eventually jumps to reset vector `0x0000`.

Consequently, the initial 2.02 -> 2.06 update needs a genuine hardware reset.
After 2.06 is installed, the software reset can make later servicing much less
dependent on AC timing.

## BixCheck and the missing cable behavior

The [factory BixCheck manual](../../preservation/original/manuals/1394047.pdf)
tells the technician to press Send while the stove is
unplugged; the status becomes “Waiting for bootloader: Plug in the stove.” The
preserved screenshots show zero Read, Write, Retry, and Interleave delays.
BixCheck's disassembly matches this: it repeatedly writes `EA`, checks for
`EB`, beeps on a miss, and immediately loops.

In the preserved 5.5.01 reconstruction, `AttemptStoveReset()` is at
`0x41F050`; `Identify()` begins at `0x420140`, reaches the `EA` write around
`0x4201FD`-`0x420210`, compares the reply with `EB`, calls Windows
`Beep(1000, 1)` on a miss, and loops. With the dialog's zero-valued delay
fields, BixCheck is already probing while the manual still describes the target
as unplugged.

That workflow used active cable P/N 2013324 between PC RS-232 and the four-wire
J3 connector. The recovered evidence does not prove that the cable was
galvanically isolated. The fourth visible conductor and the R10/C5 network by
J3-3 are consistent with a target-powered level translator, but this remains a
hypothesis until J3-3 and an original cable are measured.

## Leading electrical explanation

The direct FTDI is not a baud, inversion, or basic signal-level mismatch: it
reliably carries application traffic and produced 13 loader entries. The
failures cluster around the reset/power boundary; the exact electrical and
host-timing contributions are not yet proven.

The USB-powered
[`TTL-232R-5V-WE`](https://ftdichip.com/Support/Documents/DataSheets/Cables/DS_TTL-232R_CABLES.pdf)
TX output idles high while the stove is off.
That voltage can inject current through the PIC RC7 input protection network
into the unpowered VDD rail. Original configuration `0x3F32` disables brown-out
reset, although the power-up timer is enabled. A partially powered or slowly
decaying rail can therefore prevent a clean POR or violate its required rise
condition. In the reverse state, the powered stove TX can backfeed an
unpowered FTDI receiver; FTDI documents that partial-power condition and
recommends external buffering in its
[back-power FAQ](https://ftdichip.com/faq/if-usb-vbus-is-used-to-power-the-chip-what-voltages-can-be-present-when-the-usb-cable-is-unplugged/).
The PIC reset/configuration and input-clamp basis is documented in Microchip's
[PIC16F87XA data sheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MCU08/ProductDocuments/DataSheets/39582C.pdf).

BREAK coincided with a better entry rate while it held FTDI TX low during
discharge, which is consistent with the backfeed hypothesis, but it cannot
solve the transition:

- releasing BREAK while AC is still off restores the high/backfeed condition;
- retaining BREAK through reset presents a low/framing event where the loader
  expects `EA`, potentially consuming its only first byte; and
- although continuous probing normally places another `EA` well inside the
  window, host stalls and the BREAK-to-UART transition remain unbounded at the
  exact power edge.

This electrical mechanism is strongly consistent with the evidence, but is
not yet a captured waveform. It remains a hypothesis until PIC VDD, MCLR, RC7,
and RC6 are observed through the transition.

### Why FTDI software tri-state is not sufficient by itself

The FT232R can leave asynchronous UART mode and configure all DBUS pins as
inputs with `FT_SetBitMode(handle, 0x00, 0x01)`. That removes the strong TXD
driver, but it is not a true disconnect: the
[FT232R data sheet](https://ftdichip.com/wp-content/uploads/2020/08/DS_FT232R.pdf)
specifies an approximately 200 kOhm pull-up on input pins, so a small current
can still reach an unpowered target clamp. Returning the same open handle to
reset/UART mode and immediately writing `EA` is technically possible, but the
transition latency and any TXD glitch are undocumented and would need logic-
analyzer qualification.

There is also no deterministic power-edge indication on the present three
signals. An unpowered target leaves FTDI RXD high through its internal pull-up;
a powered PIC UART also idles high; and the loader sends nothing until it sees
`EA`. A separate, protected target-power sense input would therefore still be
required. On Linux this approach also requires one direct-USB backend for the
whole operation because FTDI's
[Linux driver guide](https://ftdichip.com/wp-content/uploads/2020/08/AN_220_FTDI_Drivers_Installation_Guide_for_Linux-1.pdf)
says the D2XX interface and VCP/`ftdi_sio` driver cannot own the device
simultaneously.

Software tri-state may be characterized only on a safely powered spare after a
separate electrical review; the current CLI and public API expose no physical
loader experiment. It does not make the existing TX/RX/GND cable deterministic
and is inferior to a controlled MCLR reset with the target continuously powered.
Any future bench characterization must remain on one direct-USB handle, arm
input mode before target power is removed, and treat process exit as unsafe
because reopening/closing a backend can restore UART idle-high.
The timing-critical return sequence must reset bit-bang mode, reapply 9,600
8N1/no-flow, purge stale bit-bang samples from both directions, and only then
write `EA`; none of those software precautions substitutes for scope evidence.

## Hardware paths that can be deterministic

### Deterministic reset component: powered MCLR reset

Keep the controller logic and UART powered, hold PIC MCLR low through a
reviewed open-drain/open-collector stage, arm the serial receiver, release
MCLR, and start `EA` probes at a known delay. A normal-operation MCLR reset
leaves `STATUS.TO` unchanged; with WDT disabled and `TO=1`, this should re-enter
the resident loader without crossing the AC power boundary.

MCLR solves reset timing only; it does not remove either UART partial-power
path. A qualified no-isolator fixture must pair this reset stage with the
dual-supply/`Ioff` UART stage below. An isolated design must pair it with the
target-powered UART barrier. Bare FTDI plus MCLR is not sufficient unless both
USB-loss and target-loss backfeed states are independently measured and proven
harmless.

Develop and qualify this sequence on the spare controller with an electrically
safe logic supply and no appliance loads attached. Any later test on an
installed controller requires a cold stove, physically disconnected igniters
and actuator loads, and a separately reviewed mains-safety procedure. Resetting
a powered appliance controller can tri-state or reinitialize its outputs and is
not authorized by this design note.

This is a candidate, not current wiring authorization. Never drive MCLR high or
connect FTDI RTS directly. The board's pull-up/RC/ICSP network must be traced,
the control stage must default released on USB loss or process exit, and the
actual reset/entry sequence must be qualified on the spare fixture first.

### Preferred isolated UART fixture: target-powered secondary

Use a one-forward/one-reverse, non-inverting digital isolator with its stove
side powered only from verified stove VDD. When the stove is off, that side and
its UART output must be unpowered/high-impedance. An upstream USB isolator does
not achieve this: the downstream FTDI remains powered. An isolator with an
always-on isolated DC/DC secondary also does not achieve it unless a separate
target-power-controlled output gate is added.

The selected isolator must specify the stove-side output state and maximum
leakage not only at `VDD2=0`, but through secondary undervoltage, power-up, and
power-down ramps while the primary remains powered. A generic
“ADuM1201-class” label or a default-high truth-table entry is not evidence of
safe partial-power behavior. Worst-case input/output logic thresholds must also
overlap in both directions. The opposite partial-power case matters as well:
with the stove side powered but FTDI/primary power absent or ramping, the
stove-facing output must remain UART idle-high or high-impedance with a
verified target pull-up. A default-low, low pulse, or false start bit could
hold BREAK or become the loader's fatal first byte.

J3-3 is a plausible source for a target-powered interface but is unresolved and
must remain disconnected until continuity, powered voltage, and source
impedance are established.

### Non-isolated alternative: dual-supply partial-power translator

A fixed-direction dual-supply translator, or two separately powered buffers,
can break the backfeed paths while retaining a shared signal ground:

- host-domain input -> target-domain output -> J3-1;
- J3-2 -> target-domain input -> host-domain output -> FTDI RX.

Each device must guarantee `Ioff`/back-drive protection at VCC=0 and have a
defined disabled state during power transitions. Worst-case `VOH`/`VIH` and
`VOL`/`VIL` margins must be demonstrated at both supply extremes in each
direction. Only after those conditions and both asymmetric ramps are verified
can this architecture be said to prevent cross-powering; it does not provide
galvanic isolation or make an unsafe common-mode voltage safe.

TI's
[`TXU0202`](https://www.ti.com/lit/ds/symlink/txu0202.pdf)
is a substantially better candidate for this exact two-wire direction pattern
than two generic LVC buffers. It has one non-inverting channel in each
direction, independently supplied A/B ports, explicit `Ioff`/floating-supply
limits, and specifies that both outputs become high-impedance if either supply
is disconnected or below 100 mV. A candidate implementation would power the B
port from verified stove VDD and choose a lower regulated A-port rail whose
worst-case input threshold accepts the FTDI's guaranteed high while its output
still meets the FTDI receiver's guaranteed high threshold. OE must default
disabled and be enabled only after both rails are valid. The 100 mV disconnect
guarantee does not define every point in the intervening supply ramp, so this
part remains subject to power-ramp and waveform qualification rather than
being a construction-ready answer.

TI's [SN74LVC1G125 data sheet](https://www.ti.com/lit/ds/symlink/sn74lvc1g125.pdf)
is useful evidence for `Ioff`, back-drive protection, and OE power-transition
gating, but it is **not** a qualified 5 V host-to-target part here. At a
4.5-5.5 V supply it requires `VIH >= 0.7 * VCC`, while the
[`TTL-232R-5V-WE`](https://ftdichip.com/Support/Documents/DataSheets/Cables/DS_TTL-232R_CABLES.pdf)
guarantees only 3.2 V minimum `VOH`. Those worst-case limits do not provide a
valid high-level margin. Choose the two direction-specific devices only after
simultaneously satisfying partial-power, transition-state, and DC-level
requirements.

## Prototype gates before full qualification

1. With all power removed, map J3-3 to PIC VDD/VSS and trace R8/R9/R10/C5;
   map the complete MCLR pull-up/RC/ICSP network.
2. Derive numeric pass/fail limits and required instrument bandwidth from the
   exact PIC, interface, supply, and reset-network specifications, then use
   appropriately isolated or differential instrumentation to record PIC
   VDD, RC7/J3-1, MCLR, and RC6/J3-2 for the stove-off/USB-on, BREAK, power-up,
   and powered-MCLR cases. Never connect an earth-grounded scope reference to
   an unproven stove reference.
3. Verify the proposed interface in both partial-power states: neither side may
   lift the other side's supply rail; the fixture output toward PIC RX/J3-1
   must be high-impedance whenever target VDD is absent; with target VDD
   present and host power absent or ramping, PIC RX must stay idle-high or
   high-impedance without a low/glitch; and the fixture output toward FTDI RX
   must be high-impedance whenever host power is absent.
4. On the exact spare 2.02 fixture, pass 100/100 hardware-reset `EA/EB` then
   zero-write `ED/E4` cycles, with zero `E3` frames and captured waveforms.
5. Perform one complete corrected 2.02 -> 2.06 flash on the spare, then use a
   PICkit whole-chip readback to compare program memory, the four expected
   relocated reset words, all remaining loader words, EEPROM, configuration,
   and User IDs.
6. Passing these five gates admits the fixture only to the complete
   [multi-specimen, cross-host, forced-interruption qualification
   plan](../guides/j3-flasher-qualification.md). It does **not** authorize a
   production-stove write. Serial 5215 stays outside qualification and must not
   receive an `E3` until that entire plan passes, a signed release record
   exists, and the owner separately authorizes the production update.

The immediate next action is therefore hardware identification and measurement,
not another direct-cable power-cycle attempt.
