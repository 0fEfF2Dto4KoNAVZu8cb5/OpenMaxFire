# Research log

## 2026-08-29 - guarded J3 flasher and loader timing

- Re-analyzed the preserved 5.0.21 and 5.5.01 Downloader paths and confirmed
  that `Bixby110Downloader()` hard-codes baud selector `1`, or 9,600. The
  resident 2.02/2.06 loader independently sets `SPBRG=0x40` at the photographed
  10 MHz oscillator. Application firmware 2.70/2.71 switches to 19,200 only
  after handoff.
- Derived the first-byte reset window from the byte-identical loader:
  three Timer1 overflows from `TMR1H=0x0B` at Fosc/4, approximately 78 ms.
  The new host uses 20 ms read probes and 20 ms spacing instead of applying the
  normal register timeout to loader entry.
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
- The complete source suite passes 234 tests. A clean version-0.9 wheel was
  built and installed, and its 2.06→2.70 plan executed successfully. Source-
  tree checks authenticated the complete 2.02→2.06, 2.06→2.70, and 2.70→2.71
  sequence as 476/481/486 blocks at fixed 9,600-baud loader transport. No
  physical loader traffic was sent during this implementation pass.

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
  BixCheck storage from the T array. Documented 2.71's non-periodic T20 event
  path and the lack of a recovered 2.71 producer for table-only TFD-TFF.
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
