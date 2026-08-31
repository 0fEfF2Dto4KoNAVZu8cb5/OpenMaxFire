# Research log

## 2026-08-30 - first live firmware-2.06 compatibility pass

- Recorded owner-reported unpowered J3-3 tracing on serial 5215's `9067-0604`
  controller: approximately 100 ohms from J3-3 to each PIC16F877A VDD pin,
  physical pins 11 and 32, with the post-resistor node observed to fan out
  across multiple IC supply paths.
- Classified J3-3 as board VDD through approximately 100 ohms and provisionally
  nominal +5 V. This is a passive topology result, not a powered voltage or
  available-current measurement; J3-3 and FTDI VCC remain disconnected.
- Recorded the plan to attach a red identification lead at the board while
  keeping its free connector end disconnected and individually insulated until
  protected powered verification is complete.
- Identified the externally programmed spare controller as exact firmware
  2.06/data format 05/build 21 through read-only J3 traffic. A leading NUL on
  the first valid reply exposed a receive-resynchronization edge case; the
  parser now accepts only leading NUL/control prefixes and still rejects an
  embedded NUL.
- Preserved two independent byte-identical A00-AFF backups. They decode format
  05, `Bixby Model 115`, serial `Unknown`, and date `08282026`. All calibration
  and fuel-table bytes match the complete vendor 2.06 PICkit defaults, but
  stored checksum `D168` does not match calculated `576B`. The stale value is
  exactly the checksum of the vendor record after changing only serial `5015`
  to `Unknown`; applying the later date edit produces `576B`. This establishes
  edit order but not which software performed it.
- Executed the real 2.06 Downloader application with the captured record and a
  checksum-corrected twin. Their first control-flow divergence occurs in the
  validator around `0x0732`; the failing path clears configuration-validation
  flags. This proves the mismatch is firmware-visible without assigning every
  downstream physical effect from the incomplete emulator.
- Located the nonperiodic T20 display-event path in 2.06, 2.70, and 2.71. Live
  2.06 T20 alternated `02`/`00` with the owner-observed flashing second light;
  T07 sampled the same display state and T13 remained raw `02`. The factory
  meaning, operating temperature not reached, matches the no-fuel/no-ignition
  condition.
- Diagnosed the persistent fans from live command/feedback rather than EEPROM
  speculation: T09=`10` Cooldown, T06=`19`, T18=`57`, and nonzero T04/T05/CR05.
  Without a host command, T18/T06 fell to zero, T09 changed to `20` Off, and
  T04/CR05 tracked the fan coast-down; the owner observed it stop.
- Reconstructed the exact 2.06 duration. CCPR1=`C674`, CCP1 special-event mode,
  T1CON=`31`, the 10 MHz oscillator, and the `1518` event threshold produce
  877.893 seconds, or about 14 minutes 38 seconds. The live transition at
  `22:50:29Z` back-calculates power-up to `22:35:51Z`, matching session start.
  The fan was normal power-up cooldown, not a migrated fan curve or stuck
  output. The invalid EEPROM checksum remains a separate defect to repair
  before active 2.06 qualification.
- Retained exact identify, EEPROM, baseline, cooldown-transition, and final-Off
  traffic plus decoded JSONL. No remote button, actuator, EEPROM write, reset,
  loader, or firmware-programming command was sent.
- After explicit authorization, re-established exact identity, stable Off, and
  a third byte-identical pre-write backup, then transmitted exactly one
  `CW0100`. Two immediate complete backups showed only A00/A01 changing
  `D1 68`→`57 6B` and both validated `576B/576B`. Following AC removal, USB
  removal, and a cold boot with USB absent, a third complete backup remained
  byte-identical and valid. Identity stayed 2.06/05/21 and the final monitor
  showed normal power-up Cooldown with zero timeouts. This live-validates the
  narrow 2.06 checksum-persistence command; no other write was sent.
- Continued with the repaired checksum and an operator-present read-only input
  matrix. One-at-a-time door, drawer, wood/corn, and thermostat actions changed
  CR02 `12→32`, `12→52`, `12→16` and CR06 `03→07`, respectively; independent
  fields and every return edge were retained. This live-confirms the recovered
  2.06 input polarity rather than projecting the original 2.02 capture.
- An accidental physical ON immediately after the input capture provided a
  bounded checksum-valid startup test: T09=`30` Prefill, T07=`01`, T06=`19`,
  T18=`5C`, and live T04/CR05 exhaust feedback. A `CW0E11` at
  `23:26:27.602845Z` was followed by Prefill through `23:26:37.735946Z` and was
  therefore ignored. One retry at `23:26:48.669208Z` was followed by repeated
  T09=`10` Cooldown beginning with the first complete sample at
  `23:26:58.294226Z`. Final monitoring had zero timeouts; no further active
  test was needed.
- Continued that checksum-valid cleanup unattended with read-only CR polling.
  The last nonzero Cooldown command evidence was T06=`19` at
  `23:41:34.543018Z`; after a 20.18-second serial gap, T09 first reported
  `20`/Off at `23:41:54.722898Z`, with T18/T06 zero on their first subsequent
  responses. The 877.893-second prediction from the first observed Cooldown
  lands at `23:41:36.187Z`, inside the preserved bracket. T04 reached zero at
  `23:42:08.667186Z`, CR05 at `23:42:11.960806Z`, and every later snapshot
  remained Off with T07/T13 clear. All unattended transmissions were CR reads;
  there was no state-changing request.

## 2026-08-30 - exact firmware-2.02 compatibility pass

- Re-ran a complete read-only baseline on the restored original controller:
  exact 2.02/format-04 identity, a complete A00-AFF backup byte-identical to
  the authenticated PICkit image, and eight cold/off monitor cycles with no
  timeout. All artifacts are under
  `research/live/2026-08-30-fw202-compatibility/`.
- Mapped the older application rather than projecting 2.06 semantics onto it.
  CR00-CR0C have real handlers; CR0D/CR0E use a generic zero-response path.
  CW00-CW0E have real handlers; CW0F is absent, independently confirming that
  2.02 cannot enter the loader through the later `CW0FC4` request.
- Traced format-04 periodic production exactly. T0C reads RAM 0x4C, the same
  byte consumed by the state-family dispatcher at 0x191F. T09 reads unrelated
  RAM 0x2D, and T15 has no state assignment. The API now decodes state and
  family-carried levels from T0C while retaining T09/T15 as raw non-state data.
- Live monitoring confirmed `T0C=20` as Off. A bounded ON transitioned to the
  decoded `0x30` Prefill family, but 2.02 temporarily stopped servicing UART;
  an OFF transmitted 0.729 seconds after ON was ignored. A retried OFF after
  UART recovery returned repeated fresh snapshots to `T0C=20`/Off.
- Changed the live-validation cleanup contract twice in response to physical
  evidence. It first retried OFF rather than trusting transmission. A later
  bounded sensor run proved that global snapshot freshness could still retain
  a pre-ON T0C `20`; the operator saw light 1 and the blower running after the
  tool had incorrectly reported Off. The monitor now timestamps every
  telemetry index, and recovery requires two distinct post-OFF T0C/T09 samples
  reporting Off or Cooldown.
- Extended the PIC14 harness and generated matrices to all four applications:
  58/58 real CR handlers, 63/63 safe CW handlers, 55 normal CW exits plus eight
  expected modeled actuator nonreturns, 113/113 requested telemetry slots, and
  1,024/1,024 internal-EEPROM reads. Fixed two harness-only defects found by
  this expansion: reusing a pre-idle parser boundary between A reads and
  selecting an earlier auxiliary T line for the requested T15 row.
- Extended the opcode-anchored input and sensor maps through exact 2.02 code.
  Its mux topology matches later firmware but uses different RAM staging:
  buttons pass through `0x51`→`0x52`, while external inputs use `0x50`.
  The J9/J10 functional paths also match, except 2.02 right-shifts the feeder
  interval once during its latch and then applies the common four-bit `CR07`
  shift. Later versions copy at the latch, so raw `CR07` units differ by a
  factor of two across that boundary.
- Obtained the first physical J10 correlation on the 2.02 controller. During a
  no-fuel start with igniters disconnected, the operator observed the blower
  running while `CR05` changed `00`→`0C`; after a separate accepted OFF it
  returned to `00`. Across the same interval J9-related `CR02.4` changed 0→1
  and `CR07` changed `1E`→`1F`; the new values then remained stable for 20
  read-only Off cycles with zero timeouts. Other bank-0 writers would yield
  CR07 `2D` at boot or `16` at the range clamp, so `1F` proves the RB1-gated
  RD0-cycle latch executed. Physical edge polarity, movement per edge, and
  timing units remain unresolved. The operator-observed first light coincided
  with T08 `01`.

## 2026-08-30 - complete flash-session retrospective and new entry design

- Analyzed every saved rehearsal/loader traffic file: 13,879 `EA`, 13 `EB`,
  12 `E3`, three `E7`, ten `ED`, ten final `E4`, and no `E5`/`E8`. Ten
  rehearsals completed `EA/EB` then `ED/E4` with zero program frames. All 24
  saved EEPROM images are byte-identical.
- Proved that all 12 host-recorded physical `E3` attempts used the former wrong
  word-byte order. TX recording preceded the underlying write, so only the
  three subsequent `E7` replies prove complete controller receipt. The
  corrected high-byte-first frame has never been attempted: both later
  programming phases failed before `EB`, recorded no `E3`, and caused no
  change.
- The dense 5,000-probe run contained a 255.301 ms host-side gap, longer than
  the reconstructed approximately 200 ms first-byte window. Old traffic
  timestamps occurred before JSON serialization, flush, `fsync`, and the
  serial write, so they were not wire-time evidence. Physical AC-on time was
  also not recorded.
- Buffered only the non-state-changing identify evidence, timestamped `EA`
  after the serial flush, aggregated in-window probe misses, and added an
  explicit durable barrier before `ED` or any `E3`. A failed barrier now blocks
  the first program frame. Identify pacing is independent of block-retry delay
  and defaults to no added inter-probe delay.
- Authenticated static regression proved original 2.02 has only `CW00`-`CW0E`
  table GOTOs. Its `CW0F` lands on NOPs and it has no `SUBLW 0xC4` reset
  handler. Firmware 2.06 does implement `CW0FC4`; therefore software reset
  cannot bootstrap the initial 2.02-to-2.06 update.
- Direct FTDI demonstrated functional loader-protocol and UART logic-level
  behavior when entry occurred, but its shared electrical reference remains
  unclassified and its
  USB-powered idle-high TX can plausibly backfeed the unpowered PIC RX/VDD
  network. BREAK reduces that injection only while held and cannot be released
  without an unqualified transition at the power edge. The bare-FTDI/manual-AC
  method is retired for writes pending waveform confirmation and replacement
  hardware.
- Defined two deterministic paths: a target-powered two-supply UART isolator
  with an isolated open-drain MCLR channel, or receive-domain `Ioff` buffers
  plus a fail-safe open-drain MCLR channel. An upstream USB isolator or an
  always-powered isolated secondary does not by itself prevent UART-line
  backpower.
- The operator reported restoring the sole hash-pinned pre-write 2.02 image;
  the controller then showed a normal boot and matching J3 identity/EEPROM,
  without a retained IPE log or post-program whole-chip readback. All physical
  loader traffic is now software-locked in the CLI and public executors. The 100/100 zero-write
  and complete spare-target flash/PICkit-readback gates admit only a reviewed
  qualification executor; production use additionally requires the complete
  multi-specimen, forced-interruption, and cross-host release plan.

Full evidence and acceptance criteria are in
[physical flash-session forensics](reverse-engineering/physical-flash-session-forensics.md)
and [loader-entry fixture](hardware/j3-loader-entry-fixture.md).

## 2026-08-29 - physical J3 failure, root cause, and PICkit recovery image

- The first physical 2.02-to-2.06 J3 program attempt entered the resident
  loader and sent an image-derived but incorrectly low-byte-first `E3` block.
  The loader returned `E7` for the byte-sum checksum but never returned `E4`;
  bounded identical retries were silent. Source-bound recovery attempts repeated
  the same frame and outcome before later corrected entries sent no `E3`.
- A full PICkit read at 4.75 V preserved all 8,192 program words, all 256
  EEPROM bytes, four User IDs, and configuration `0x3F32`; CP and CPD are
  disabled. The readback SHA-256 is
  `b281357f6b38db046361de3be1cdd455999b9b8b65d098d0b9d329d8fb789fca`.
  EEPROM, User IDs, configuration, and every program word except three remain
  identical to the original 2.02 preservation.
- The only changed words are the relocated application reset vector:
  `0x1E84 3018->1830`, `0x1E85 008A->0A00`, and
  `0x1E86 2800->0028`. Each intended word's byte pair was reversed.
- Rechecked BixCheck 5.0.21 assembly. `LoadHex()` stores the first Intel HEX
  byte at object offset `e4b` and the second at `e4a`; `DownLoad()` sends
  `e4a` first. The real wire order is therefore high byte then low byte. The
  host and its simulator had shared the inverse assumption. The byte-sum
  checksum is invariant under reversal, explaining `E7`. The invalid reset
  vector explains why the application could not boot; it does not explain the
  absent per-block `E4`, which remains unresolved because `ED`/handoff was
  never reached.
- Corrected host framing and simulator decoding, added a regression anchored
  to the physical first block, and regenerated all authenticated wire hashes.
- Constructed a 2.06-program/format-04-data hybrid from the hash-pinned donor
  program/configuration plus the controller readback's EEPROM/User IDs. It was
  not the image used for the reported restore, is incompatible with 2.06's
  expected format-05/calibration path, and is now explicitly quarantined as an
  unqualified do-not-import/do-not-program forensic candidate. No PICkit erase
  or program action was performed by the build tool. Its original manifest is
  immutable historical evidence and is superseded by the current quarantine.

## 2026-08-29 - first physical zero-write loader rehearsal

- On the original firmware-2.02 controller, a direct FTDI
  `TTL-232R-5V-WE` cable did not enter the loader while TX remained at its
  normal idle-high level during stove power removal. The adapter VCC lead and
  J3 pin 3 were disconnected.
- Added an explicit rehearsal-only UART BREAK option. It asserts BREAK before
  the AC-off confirmation, holding FTDI orange/TX low, then releases BREAK
  immediately before the bounded `EA` probes. Both transitions are journaled,
  and cleanup releases BREAK after operator aborts and errors.
- The first physical BREAK-assisted run entered the resident loader: attempt
  331 received `EB`, then `ED` received `E4`. The durable audit contains zero
  `E3` bytes and reports `program_blocks_sent=0` and
  `flash_write_commands_sent=0`.
- The front panel resumed after `ED/E4`, but J3 application reads did not resume
  on that warm handoff. A true cold boot with stove AC removed and the FTDI USB
  cable physically unplugged restored normal 2.02/format-04 identity. A fresh
  complete `A00`-`AFF` backup was byte-identical to the pre-rehearsal backup.
  This validates physical zero-write loader entry once, but does not validate
  application programming, interrupted-write recovery, or a production flash.
- Extended the BREAK workflow to guard loader-entry power cycles. Application
  exit is treated separately: the operator must remove both stove AC and FTDI
  USB power, start the controller normally with USB absent, reconnect USB, and
  let the host open a newly enumerated handle before verification. A post-write
  operator abort closes or releases the transport but deliberately retains the
  exact-image recovery marker.
- The complete source suite passes 238 tests after adding sustained-BREAK
  transport, simulator, full-flow success, and abort-cleanup coverage.

## 2026-08-29 - guarded J3 flasher and loader timing

- Added a deterministic complete-PICkit composer for the preserved Downloader
  images. It overlays only effective resident-loader targets on a complete
  base, redirects source `0x0000`-`0x0003` to `0x1E84`-`0x1E87`, preserves
  sparse omitted words, and retains physical reset, loader, User IDs,
  configuration, and all EEPROM bytes from the base.
- Validated the composition rule against the vendor's independent 2.06 pair:
  applying `Bixby_02060021_Downloader.hex` over
  `Bixby_02060021_PICkit.hex` reproduces every mapped byte of the factory
  PICkit image. This is a strong static golden check independent of the later
  2.70/2.71 outputs.
- Generated five complete, hash-manifested predictions: factory-2.06-based
  2.70/2.71 and serial-5215-based 2.06/2.70/2.71. They are labeled derived and
  `precal` because EEPROM remains inherited from the base; later Format and
  calibration changes cannot be predicted. Physical post-J3/pre-calibration
  readback comparison on a spare remains pending.
- Reparsed every derived HEX as a complete 8,192-word/256-byte PIC16F877A image
  and booted all five through the inherited resident loader in the real PIC14
  emulator. Each target application completed a `CR00` exchange as `CR0000`.
- Published this offline composer/API and the five generated images as version
  0.10.0. The images remain explicitly derived and unqualified for production
  recovery until a physical post-J3/pre-calibration whole-chip read matches.

- Analyzed seven owner-supplied physical rehearsal session directories from
  serial 5215. Sessions 003, 004, and 006 positively recorded `EA/EB` followed
  by `ED/E4`, with zero `E3` frames and zero program blocks. Sessions 002 and
  005 exhausted the bounded identify probes without `EB`; session 007 ended
  in an operating-system I/O error when USB was removed. All complete EEPROM
  backups in the archive are byte-identical and retain checksum `EFCE`.
- In the three successful loader handoffs, the old host sent its first `CR00`
  approximately 764 ms, 780 ms, and 764 ms after the final `E4`. Each attempt
  then received zero application frames, and normal serial access remained
  unavailable until a controller reset. Because no `E3` was sent, this is a
  post-handoff application-UART failure, not application-image corruption.
- Static firmware-2.02 analysis shows the receiver enabled before receive
  interrupts begin servicing it. The PIC16F877A receive FIFO is two bytes;
  Microchip specifies that a third unread character sets `OERR` and prevents
  further reception until `CREN` is cleared and set. The early four-byte
  `CR00` is therefore the best-supported explanation for the persistent
  failure, although a logic-analyzer/UART trace is still required to prove the
  mechanism electrically.
- Version 0.9.1 replaces the fixed-delay-first-`CR00` behavior with a passive
  readiness gate. After `ED/E4`, the retained serial handle transmits nothing
  until a valid unsolicited `T` or periodic `DW` frame proves the application
  is running and servicing serial input. A bounded timeout fails explicitly
  while guaranteeing that no `CR00` or other application request was sent.
  Readiness evidence is saved with the rehearsal and each post-flash attempt.
  This fixes the host-side handoff defect but does not resolve or qualify the
  separate controller-power/reset and possible USB backfeed question.

- Re-analyzed the preserved 5.0.21 and 5.5.01 Downloader paths and confirmed
  that `Bixby110Downloader()` hard-codes baud selector `1`, or 9,600. The
  resident 2.02/2.06 loader independently sets `SPBRG=0x40` at the photographed
  10 MHz oscillator. Application firmware 2.70/2.71 switches to 19,200 only
  after handoff.
- Corrected the first-byte reset-window calculation from the byte-identical
  loader. A pre-set `TMR1IF` consumes the first count immediately; the two real
  overflows use `T1CON=0x21` (Fosc/4 with 1:4 prescale) from `TMR1H=0x0B`, or
  approximately 200 ms. The host supports bounded 5 ms read/spacing settings
  so many `EA` probes can land inside that window.
- Cross-checked the loader's four-word row preservation and write sequence
  against Microchip PIC16F87XA data-sheet section 3.6. Microchip specifies
  edge-aligned four-word erase/write blocks, preservation of untouched words,
  and a typical 4 ms final erase/write halt; the host allows a bounded 500 ms
  block response.
- Confirmed from the vendor guide that both igniters are physically unplugged
  for downloading and that the Downloader timing controls are shown as zero.
  Confirmed from the 2.06 release notes that a version/data-format upgrade is
  followed by model selection, Individualize, Calculate Fuel A/B, and Format.
- Added an exact three-image live allowlist. Each entry authenticates file
  SHA-256, metadata, word count, configuration word, block count, and the
  SHA-256 of every length-delimited wire frame. PICkit, unknown, modified,
  renamed, and 2.73 images fail closed.
- Implemented the separate `maxfirectl flash` workflow: exact current identity,
  valid complete EEPROM backup, authenticated self-contained rescue bundle,
  manual power-cycle entry only, fixed 9,600-baud loader, classified/bounded
  E8/E5/pre-accept/post-accept retry behavior, no BixCheck terminal unread send,
  fsync'd state/traffic evidence, conservative final-ED recovery, target-baud
  application identity, and byte-identical post-flash EEPROM.
- Added a mandatory non-writing physical rehearsal (`EA/EB`, `ED/E4`, zero
  `E3`), backed by execution of the recovered 2.02 PIC code with queued `EA ED`
  producing exactly `EB E4`. The live workflow retains one exclusive serial
  handle across preflight, rehearsal, programming, and verification, inhibits
  host sleep, and defers ordinary termination during the destructive exchange.
- Made recovery source-bound and one-way. Recovery requires an unresolved
  durable marker, cross-authenticates the image/preparation/profile/identity/
  EEPROM manifest, creates a complete successor first, then delegates recovery
  responsibility so completed or older sessions cannot bypass rewrite rules.
- Tightened delayed-byte handling so `E4` is accepted only after that attempt's
  observed `E7`, while `E7 E4` is accepted only after a pre-accept timeout.
  Stray acknowledgements after `E5`/`E8` and receive-buffer errors abort without
  retransmission. Post-write identity/EEPROM verification continues even when
  its diagnostic recorder fails.
- Added full-image emulator and fault-injection coverage for successful 476-
  block 2.06 programming, E8, E5, exhaustion, wrong baud, final-ED recovery,
  target identity, EEPROM mutation, safety gates, and offline CLI planning.
  The host also preserves a complete backup when a checksum/format gate fails,
  retains a late buffered `EB`, and writes a durable result for post-flash
  verification failure.
- The complete source suite passes 237 tests. A clean version-0.9.1 wheel was
  built and installed. The earlier 2.06→2.70 plan executed successfully. Source-
  tree checks authenticated the complete 2.02→2.06, 2.06→2.70, and 2.70→2.71
  sequence as 476/481/486 blocks at fixed 9,600-baud loader transport. The
  initial implementation/test run sent no physical loader traffic; the later
  owner-supplied zero-write sessions are summarized above.

## 2026-08-28

- Preserved the first complete PICkit export from serial 5215's original
  firmware-2.02 PIC without altering its bytes. SHA-256 is
  `272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab`;
  additional independent exports remain pending.
- Validated all Intel HEX checksums, all 8,192 program words, all 256 EEPROM
  bytes, four User ID words, configuration `0x3F32`, and disabled CP/CPD.
- Proved the recovered EEPROM is byte-identical to the independent 2026-08-22
  live J3 backup from the controller, creating a direct provenance link.
- Generated the complete deterministic 2.02 memory map, EEPROM extraction,
  program binary, PIC14 disassembly, pairwise comparisons, and loader-emulator
  trace. The entire protected loader range matches 2.06 PICkit word-for-word,
  while 7,478 of 7,808 application-range words differ at the same addresses.
- Added 2.02 to the authenticated firmware catalog and regression suite. No
  programmer-control or physical flashing path was added. The complete
  portable suite now contains 191 passing tests.

## 2026-08-27

- Replayed the preserved 2.02 control-session traffic by command phase. T09
  remained `07` before ON, after physically confirmed UP/DOWN responses during
  startup, and after OFF, proving it cannot verify format-04 state. Added
  explicit non-control T0C/T15 cold/off and startup/control-active candidates.
- Completed the evidence-backed loader simulator gaps: distinct E8 and E5
  receipts, four-word partial-row preservation, two internal row-write
  attempts, `0x1E80` direct protection, reset-word relocation to
  `0x1E84`-`0x1E87`, 30 accepted attempts plus BixCheck's terminal unread
  transmission, one-shot ED completion, and fail-closed application reconnect.
- Added a read-only PIC16F877A preservation API and CLI that compare normalized
  program memory, EEPROM, User IDs, configuration, Device ID, CP/CPD state,
  and SHA-256 across repeated reads or original/clone readbacks.
- Added the PICkit 3 original-chip procedure, including exact socket pins,
  three independent reads, immutable manifests, a code-protection hard stop,
  and the rule that only a spare chip may be programmed.
- Reaffirmed that the red conductor position in the historical forum cable
  photograph is electrically unverified and does not justify connecting J3-3.
  J3-3 and adapter VCC remain disconnected.

## 2026-08-23

- Preserved an audited live normal-control session on firmware 2.02. Exact
  `CW0E12`, `CW0E14`, `CW0E18`, and `CW0E11` requests produced the expected
  operator-observed ON, UP, DOWN, and OFF behavior.
- Captured the controller while the single rightmost/light-8 problem indicator
  was visibly flashing. Raw traffic alternated T08 between `00` and `80`; T13
  remained `BA`. This live-correlates T08.7 with factory feeder-wheel fault
  light 8 and rejects later-format T13 semantics for this format-04 profile.
- Added a profile-aware fault API. Format-04 T08 bits are retained across an
  eight-second observed-stream window, exact factory light combinations return
  stable machine codes and evidence levels, and later BixCheck T13 remains raw.
- Added byte-exact control/fault preservation, checksum manifests, protocol/API
  documentation, and replay regression coverage for a final T08=00 dark phase.

- Added the version-0.5 reusable Python API foundations without adding CLI,
  GUI, or Home Assistant policy: exact controller profiles/capabilities,
  read-only baud detection, typed profile-aware snapshots, and a common error
  taxonomy.
- Added lossless configuration images and exact format-05/07 schemas (71/82
  recovered adjustments), typed edits/transforms/diffs, identity-preserving
  restore plans, firmware checksum persistence through CW01, and whole-image
  verification requirements. Physical execution remains blocked.
- Represented all 45 reachable BixCheck Checkout tests as data with passive
  predicates, format-specific actions, cleanup metadata, and report models.
- Added strict Intel HEX/PIC14 firmware images, delivery-layout and migration
  checks, reconstructed E3 loader blocks, and an explicit unsupported loader
  execution boundary pending recovery validation.
- Added idempotent normal-control planning and an API-compatible simulated
  controller/transport with writes disabled by default and deterministic fault
  injection. The portable suite now contains 102 passing offline tests.
- Added the version-0.6 `ControllerSession` facade for exact detection,
  connection ownership, profile/capability access, typed polling/iteration,
  configuration images, and backup documents.
- Added bounded read-only execution for all currently machine-evaluable
  Checkout tests. Manual and actuator-only cases explicitly return `not_run`.
- Added simulator-only configuration, normal-control, and Checkout workflow
  execution. These enforce authorization, stale-source rejection, whole-image
  verification, rate/input interlocks, and unconditional actuator cleanup while
  hard-blocking physical state changes. The portable suite now has 116 tests.

## 2026-08-18

- Defined the preservation-first project scope.
- Recovered the BixCheck 5.x manual and three vendor software packages.
- Identified BixCheck's Monitor, calibration, telemetry, logging, Checkout, and Downloader functions.
- Recorded the factory cable part number and J3 location from vendor documentation.
- Established the reliability requirement: the smart layer must not impair factory operation.

## 2026-08-19

- Built the first OpenMaxFire v0.1 Python protocol/CLI skeleton.
- Statically reconstructed `CRXX` and `CWXXYY` command encodings from BixCheck 5.5.01.
- Reconstructed remote OFF/ON/UP/DOWN writes to controller register 0x0E.
- Recorded the owner's stove/PCB identification details.
- Investigated door-state feasibility and automatic heating-source coordination.

## 2026-08-20

- Extracted embedded `Bixby_0271_080315.hex` from BixCheck 5.5.01.
- Parsed and disassembled firmware 2.71 as PIC16F877A code.
- Annotated the reset vector, UART setup, ASCII-hex decoder, read/write parser, CR register handlers, and response terminator.
- Identified UART register values `SPBRG=0x20`, `TXSTA=0x26`, and `RCSTA=0x90`.
- Mapped CR00-CR0E static handlers and narrowed door-switch candidates to CR02/CR06 input bits.
- Created this structured GitHub archive and documented the initial baud/divisor ambiguity.
- Completed a reproducible deep reverse-engineering pass over BixCheck 5.0.21,
  5.5.00, and 5.5.01 using retained MinGW COFF symbols, focused disassembly,
  decoded tables, call graphs, and normalized function comparison.
- Established exact BixCheck host settings: 5.0.21 uses 9,600 baud; 5.5.x
  selects 9,600/19,200; all are 8N1. This resolves the earlier divisor ambiguity
  in favor of a strongly inferred 10 MHz controller oscillator.
- Reconstructed the complete outer response grammar, no-terminator request
  framing, 34-record 5.5.01 telemetry map, 0x58-byte configuration record,
  lean-burn transforms, and add/rotate checksum.
- Decoded all direct Checkout actions and found the dormant, unreachable ninth
  automatic plate-motor record shared by every EXE.
- Reconstructed Downloader identity/block framing and kept it isolated from the
  normal protocol API.
- Built a read-only-by-default PTY serial lab and strict response parser.
- Built an experimental PIC16F877A execution harness. The real 2.06, 2.70, and
  2.71 images responded to `CR00` with `CR0000` plus LF; the PICkit loader
  responded to reset-time `EA` with `EB`.
- Extended the emulator across every CR00-CR0E handler in all three application
  generations. All 45 handlers and formatters completed, with exact RAM/SFR
  read dependencies, instruction watchpoints, and net-change exports.
- Discovered that the real response formatter uses lowercase hexadecimal
  letters (`CR0A` returns `CR0a...`) even though host requests are uppercase.
- Added separate GPIO latch/input modeling and cross-referenced BixCheck's
  result masks: firebox door=CR02.5/RD1, ash drawer=CR02.6/RD4, and
  thermostat=CR06.2/RB4. This first pass identified CR02.2 as a fuel-select
  candidate; the later scanner/configuration-bank analysis below resolves it.
- Added reset-time ten-bit ADC replay and identified fan potentiometer=CR09/AN3
  and feed potentiometer=CR0A/AN4 across all three generations.
- Corrected A-unit storage to the PIC16F877A internal data EEPROM path, built
  checksum-valid synthetic format-05/07 fixtures, and verified all 768
  AR00-ARFF reads byte-for-byte.
- Preserved the owner-supplied `MaxFire Mother Board Pin Out` image and recorded
  its exact hash and public-match provenance. Its visible PCB number is
  `9067-0404`; serial 5215's installed controller remains owner-reported as
  `9067-0604`, so it is explicitly classified as related-family evidence.
- Reconstructed identical input scanners in 2.06, 2.70, and 2.71. The button
  bank uses RD2/RD6:RD5 with an active-low RD3 return and produces CR01. The
  external bank uses RD7/RD6:RD5 with an active-high RD3 return and produces
  CR02.0-2.
- Cross-referenced the diagram, firmware, and BixCheck result predicates to map
  the burn-drive limit switch to CR02.0 and the fuel selector to CR02.2. The
  firmware's `0x30` configuration-bank offset establishes `1`=Fuel A/corn and
  `0`=Fuel B/wood. CR02.1 remains physically unassigned.
- Followed the complete J10 producer path in all three application generations:
  RA4/T0CKI falling edges increment unprescaled TMR0, the external-interrupt
  path samples it every 30 ticks into RAM 0x34, and CR05 returns the count.
  BixCheck's exhaust predicates are full `>=0x78`, half `0x38`-`0x48`, and off
  zero in 5.5.x (`<=0x03` in 5.0.21).
- Followed the complete J9 producer path: while RB1 is active, external
  interrupts count into RAM 0x47:0x46; an RD0 high-then-low wheel cycle latches
  that interval into 0x45:0x44; CR07 returns its low byte shifted right four.
  CR02.4 exposes the current RD0 level, and all BixCheck versions accept CR07
  `0x10`-`0x68` in the feed-motor/sensor test.
- Added masked, cross-generation opcode signatures and a generated
  `sensor-signal-paths.csv` so the J9/J10 conclusions fail regeneration if a
  preserved image no longer matches the documented flow.

## 2026-08-21

- Reconstructed all sixteen C-unit write dispatch entries in firmware 2.06,
  2.70, and 2.71. Roles now cover service countdown, checksum persistence,
  telemetry suppression/resume, LEDs, burn drive, compressor, convection and
  exhaust outputs, igniter/feed/service workflows, remote buttons, and the
  keyed loader request.
- Extended the PIC emulator with disposable-clone C-write experiments. All 48
  version/register combinations reach the expected handler; 42 reach the
  normal exit, while CW05/CW0A in each generation are expected bounded
  nonreturns in the incomplete actuator/timer model. CW0FC4 remains excluded.
- Modeled PIC data-EEPROM programming and observed exactly two CW01 write
  events per firmware generation, at checksum bytes A00/A01.
- Traced the complete periodic telemetry blocks and senders. All 91 slots reach
  the real UART formatter in emulation. The firmware emits one-byte `Txxvv`
  lines; six logical 16-bit fields are adjacent big-endian slot pairs rather
  than physical seven-character frames.
- Identified optional addressed D-unit auxiliary lines and separated their
  BixCheck storage from the T array. The later live 2.06 pass proved that the
  non-periodic T20 display-event path is shared by 2.06/2.70/2.71: T20 `02`
  and `00` alternated with the flashing second light. No recovered 2.71
  producer exists for table-only TFD-TFF.
- Recovered BixCheck display math for control-board C/F temperature, fan/feed
  trim percentages, exhaust count-to-RPM, exhaust phase microseconds, feed
  ticks-to-seconds, and the vendor timer units. Kept thermocouple points and
  physical calibration explicitly uncalibrated.
- Reconstructed T09 from bank-0 RAM 0x4C through all cross-version state-family
  dispatchers. Mapped 2.71's reset, cooldown, off, startup, operating/ramping,
  ash-dump, and shutdown transition sites.
- Recovered the exact 5.5.01 display decoder: startup is Prefill/Started/
  Starting/Ignited, family 4 exposes Level/TSTAT, family 5 is Ramping, family 6
  is Ash dump, and bit 7 is ignored by both BixCheck and firmware.
- Added focused static excerpts for telemetry/conversions, writes/UI, logging/
  reports, and flue/fuel monitoring to every BixCheck version. Documented the
  generic write/response-refresh sequence, lean-burn pre-write conversion,
  selected-field CSV-style logs, report naming/loading, and utility-window
  control structure.
- Added protocol helpers/tests for adjacent telemetry words and exact operating
  state decoding, plus firmware/emulator assertions for C writes, telemetry
  senders, and state dispatch anchors.
- Recovered the cross-version T08 igniter decoder (`L R failed`, `R failed`,
  `L failed`, `L R good`, or `Error`). Confirmed that BixCheck leaves T12 IIC
  and T13 alarm status as raw hexadecimal and only derives T14 Flag mode as
  `(raw & 7) + 1`; it does not contain the previously implied named decoders.
- Preserved ten owner-supplied installed-controller/interior JPEGs byte-for-byte
  with SHA-256 provenance. The photographs make the main-PCB `-0604` suffix
  legible, corroborating the owner-reported `9067-0604`, and directly confirm
  the black four-contact main-board J3, its placement beside the J7 ribbon area,
  and the nearby visible `LM1815N` marking. Pin functions, electrical levels,
  solder-side routing, and oscillator marking remain open.
- Promoted the service-tool target from Linux-only to a single Windows/Linux/
  macOS codebase. Added portable serial-port discovery, bounded addressed-read
  matching with telemetry interleaving, the safe identity sequence, exact
  timestamped JSONL traffic capture, and lossless AR00-AFF JSON backups with
  identity/data-format/checksum diagnostics.
- Made the POSIX PTY lab import-safe on Windows, added a six-entry OS/Python CI
  matrix, and expanded the offline suite from 48 to 63 tests. The new software
  remains unvalidated on J3 and does not authorize a physical connection.

- Preserved the user-supplied 40-page MaxFire Model 115 owner manual, document
  `2020866 REV A`, byte-for-byte with SHA-256 provenance.
- Extracted vendor-documented thermostat behavior, door/drawer shutdown timing,
  fault indicators, maintenance intervals, wiring labels, and service-part
  numbers into a revision-scoped research note.
- Used the factory wiring diagram to corroborate J3 and existing switch/sensor
  roles while confirming that it provides no J3 electrical pinout and depicts
  no hopper-level or hopper-lid sensor.
- Corrected heating-orchestration guidance: the Rev. A wall thermostat does not
  start the stove, so it cannot be assumed to provide independent restart
  failover without configuration-aware live validation.

## 2026-08-22

- Preserved full component- and solder-side photographs of serial 5215's bare
  controller. The images directly identify PCB `9067-0604`, PIC16F877A-I/P,
  and the `10.000` MHz oscillator.
- Combined corrected owner continuity tracing with the photographed square pad
  and successful live wiring: J3-1 is stove RX toward PIC26/RC7, J3-2 is stove
  TX toward PIC25/RC6, J3-4 is board ground, and J3-3 remains
  unresolved/disconnected.
- Inventoried the exact live cable as FTDI `TTL-232R-5V-WE`, VID:PID
  `0403:6001`, serial `ABBAUPPN`; black/orange/yellow connected to
  J3-4/ground, J3-1/stove-RX, and J3-2/stove-TX respectively. Adapter VCC
  remained disconnected.
- Rejected 19,200 baud and completed the first physical `CR00` exchange at
  9,600 8N1. Captured exact no-terminator request framing, LF responses, and
  lowercase response nibbles.
- Identified the installed controller as previously unpreserved firmware 2.02,
  data format 04 (`CR00=00`, `CR08=04`, `CR0B=02`, `CR0C=02`, `CR0D=00`,
  `CR0E=00`).
- Captured the complete CR00-CR0E cold baseline and physically validated
  firebox door (`CR02 & 20`), ash drawer (`CR02 & 40`), corn/Fuel-A selector
  (`CR02 & 04`), thermostat-open (`CR06 & 04`), OFF/UP/DOWN buttons, and both
  full-range trim potentiometers. Physical ON was intentionally excluded.
- Completed three byte-identical A00-AFF reads. The 256-byte EEPROM checksum
  `EFCE` matches; it decodes format 04, model `Bixby Model 115`, serial string
  `2060`, and production-date string `01102007`. The mismatch with appliance
  serial 5215/December 2005 is preserved without assigning a cause.
- Measured about a 3.58-second format-04 telemetry cycle during active polling.
  Live correlations identify T03 fan trim, T04 feed trim, T06 as a dynamic
  firebox-related value, flashing T08 bits 08/10 for firebox/ash warnings, and
  T0C bit 08 for thermostat-open. DW06 is not uniquely an ash-drawer field.
- Established that passive capture produces no spontaneous telemetry; the
  controller emits telemetry bursts while requests are active. Port opening can
  expose a partial line or ambiguous `00 0A` fragment.
- Reproduced two client failures: a partial opening fragment and a valid CR08
  reply arriving after more than 16 interleaved frames. Changed query matching
  to continue until transport timeout, added delimiter resynchronization, and
  added regression tests.
- Preserved the raw JSONL traffic, adapter inventory, EEPROM artifact, hashes,
  photographs, and interpreted live report. No C/A write, remote ON, loader,
  or actuator command was sent.

## 2026-08-23

- Promoted the experimental differential reader into `maxfirectl monitor`, a
  first-class read-only CR00-CR0E polling loop that retains rather than discards
  interleaved telemetry and tolerates individual addressed-read timeouts.
- Added a latest-value monitor state with raw CR/T/status preservation,
  adjacent-slot words, frame counts, timestamp/age fields, configurable stale
  detection, compact console output, and durable decoded JSONL snapshots.
- Added `maxfirectl replay` for offline reconstruction from exact
  `openmaxfire.serial-capture.v1` logs, including arbitrary RX chunk boundaries,
  malformed opening-line resynchronization, and explicit trailing-byte counts.
- Replayed the preserved all-closed, firebox-open, ash-drawer-open, and
  thermostat-open format-04 captures as regression fixtures. Their observed
  T08 warning bits and T0C thermostat bit reconstruct correctly.
- Tightened the evidence boundary after replay showed format-04 `T09=07` while
  cold/off: the monitor preserves that byte as unresolved instead of applying
  the later BixCheck 5.5 state decoder. No live command or write was issued in
  this development pass.
- Added the version-0.4 low-level service layer: A/C/D reads and send-only
  writes, optional fresh-readback verification, uninterpreted exact-byte
  exchange, and validated fail-fast JSON register transactions.
- Corrected addressed-read matching to require an `R` opcode, preventing a
  possible same-address `W` echo from being accepted as write verification.
- Added a second explicit acknowledgement for live state-changing traffic and
  blocked `CW0FC4`, `EA`, `E3`, and `ED` from generic raw/transaction paths.
  Loader support remains a separate unfinished state machine; no physical
  write or loader traffic was issued during this implementation pass.
- Added the version-0.5 controller-aware API foundations: exact profiles and
  read-only discovery, conservative typed snapshots, configuration schemas and
  plans, all 45 Checkout definitions, Intel HEX/PIC14 validation, control
  planning, and a writes-disabled simulator/fault backend.
- Added the version-0.6 `ControllerSession` facade, typed snapshot iteration,
  configuration backup access, bounded read-only Checkout execution, and
  simulator-only configuration, normal-control, and actuator-cleanup workflows
  with authorization, stale-source checks, interlocks, and full verification.
- Added version-0.7 exact-byte `AuditTrail` sessions and digestable workflow
  spans, then attached them to control, configuration, Checkout, and loader
  results. Failed initial identity now closes both the owned transport and audit
  sink.
- Added an authenticated public catalog/validator for all four preserved
  firmware images, checking exact path, size, SHA-256, version, delivery
  variant, program-word count, and configuration word.
- Added the isolated loader laboratory: typed plans/results, `EA`/`EB`
  identification, reconstructed `E3` frames, ordered `E7`/`E4` block
  acknowledgements, bounded retries, `ED`/`E4` completion, progress receipts,
  programmed-memory comparison, and deterministic disconnect/corruption
  injection. The executor accepts only its concrete simulator transport and
  contains no `CW0FC4`, erase, reset, or physical serial path.
- Expanded the portable API-only suite to 131 passing tests plus one preserved-
  corpus integration test that runs when the full archive is present. No live
  state-changing or loader traffic was issued.
- Added a guided physical-validation harness outside the reusable API. Its
  default path is read-only and preserves audited discovery, repeated identity,
  complete snapshots, EEPROM integrity, and one-at-a-time input/trim evidence.
  Remote OFF/UP/DOWN and ON/start are isolated behind progressively stronger
  command-line, safety-checklist, and per-command authorization gates. The
  harness contains no configuration, Checkout-actuator, raw, or loader path.
- Added four offline validation-harness regressions, bringing the work-export
  suite to 135 passing tests plus the conditional full-corpus integration test.
  No physical traffic was issued while developing the harness.
- Corrected the J3 wiring record after owner review: J3-1 is stove RX/PIC26 and
  uses the FTDI orange TX conductor; J3-2 is stove TX/PIC25 and uses the yellow
  RX conductor. Renamed the earlier reversed-wire photograph as incorrect
  evidence and marked it not to be copied; it does not show the successful live
  connection.
