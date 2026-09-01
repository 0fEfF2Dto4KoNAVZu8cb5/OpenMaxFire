# Roadmap

This file tracks project-wide research, preservation, validation, packaging,
and hardware work. The reusable Python implementation has its own
[API architecture and completion roadmap](api/README.md). CLI, future GUI, and
Home Assistant work are separate clients of that API and must not duplicate
protocol or controller logic.

## Phase 0 - preservation foundation

- [x] Preserve recovered vendor ZIP packages and standalone BixCheck 5.5.01 executable.
- [x] Preserve the BixCheck 5.x manual and release notes.
- [x] Preserve and analyze the MaxFire Model 115 owner manual, document 2020866 Rev. A.
- [x] Extract and checksum all 2.06, 2.70, and 2.71 firmware delivery images.
- [x] Preserve the earlier 2.71 analysis bundle and independent gpdasm disassembly.
- [x] Add a dependency-free Intel HEX parser/PIC14 disassembler and deterministic analysis for all images.
- [x] Map cross-version protocol anchors, constant CR responses, UART changes, and the 2.06 bootloader/EEPROM delta.
- [x] Deep-analyze all three BixCheck EXEs and export symbols, call graphs,
  configuration/telemetry/Checkout tables, focused assembly, and semantic diffs.
- [x] Build a read-only virtual serial lab and experimental PIC execution harness.
- [x] Execute all real CR handlers across all four application generations with
  handler-level RAM/SFR traces, watchpoints, and response artifacts.
- [x] Model synthetic GPIO/ADC inputs and map door, drawer, thermostat, and both
  potentiometers offline.
- [x] Recover both RD3 input-multiplexer banks and map the panel buttons,
  burn-drive limit switch, and fuel selector (`1`=Fuel A/corn, `0`=Fuel B/wood).
- [x] Trace J10 exhaust-sensor pulses through RA4/T0CKI/TMR0 to CR05 and J9
  feeder-wheel transitions through RD0 and the interval counter to CR02.4/CR07.
- [x] Preserve and revision-check the online-found 9067-0404 MaxFire motherboard
  diagram against serial 5215's owner-reported, photo-corroborated 9067-0604
  controller.
- [x] Preserve the installed component-side, J3, harness, auxiliary-board, and
  stove-interior photograph set for serial 5215.
- [x] Preserve the bare 9067-0604 component/solder-side, J3/PIC, oscillator,
  routing, and working-cable photograph set.
- [x] Model PIC internal data EEPROM and verify AR00-ARFF across all four
  generations with checksum-valid format-04/05/07 fixtures.
- [x] Map every real C-write dispatcher/handler—CW00-CW0E in 2.02 and
  CW00-CW0F later—and execute safe synthetic probes in disposable clones
  without taking the CW0FC4 loader branch.
- [x] Trace every periodic telemetry producer through the real UART sender,
  resolve physical one-byte framing, adjacent-slot words, auxiliary D lines,
  and core BixCheck display conversions.
- [x] Reconstruct the cross-version T09 state-family dispatcher, 2.71
  structural transitions, and exact BixCheck state labels.
- [x] Recover BixCheck's configuration-write lifecycle, selected-field data
  logging, report files, QuickCal/debug construction, and flue/fuel monitors.
- [x] Record hashes, sizes, provenance, and the relationship between original and derived files.
- [x] Preserve the prior OpenMaxFire v0.1 snapshot.
- [x] Publish all three recovered factory firmware/service-software releases to Archive.org after reviewing redistribution and privacy.
- [x] Add a fail-closed PIC16F877A read-export/clone comparator covering
  program memory, EEPROM, User IDs, configuration, Device ID, CP/CPD, and
  section-level SHA-256 manifests.
- [x] Preserve the first complete original-controller firmware 2.02 PICkit
  export, validate its structure/protection state, tie it to serial 5215 by an
  exact live-EEPROM match, and generate deterministic analysis artifacts.
- [x] Record that the preserved 2.02 export is the sole pre-write original
  capture; the original was subsequently restored externally, so independent
  pre-write reads cannot be recreated retroactively.
- [x] Generate complete derived PICkit predictions for factory-2.06 and
  serial-5215 lineages by applying the reconstructed loader overlay/remap rules.
- [ ] Compare each derived image against a complete physical PICkit read taken
  immediately after the matching J3 update and before calibration.

## Phase 1 - electrical and read-only bench validation

- [ ] Photograph both ends of the received cable and record all labels/part numbers.
- [x] Photograph the component side and J3 area of the installed 9067-0604 board
  and compare visible connector placement with the preserved 9067-0404 diagram.
- [x] Photograph the unobstructed full part-number silkscreen and solder side of
  the installed board, then trace J3 without assuming the 9067-0404 routing.
- [x] Identify J3 ground/TX/RX without assuming standard RS-232 and passively
  trace pin 3 through approximately 100 ohms to PIC VDD; leave pin 3
  disconnected pending powered-voltage verification.
- [ ] Measure idle voltage and polarity through a protected interface.
- [x] Physically confirm the controller oscillator's `10.000` MHz marking.
- [ ] Capture BixCheck startup traffic if the Windows application can run.
- [x] Test only `CR00`; reject 19,200 and establish 9,600 for live firmware
  2.02/data format 04.
- [x] Record exact request bytes, response bytes, timing, lowercase hex, and LF
  termination.
- [x] Poll CR00-CR0E with the stove safely off.
- [x] Repeat polling while operating the fire door, ash drawer, thermostat,
  fuel switch, trim pots, and OFF/UP/DOWN panel buttons; intentionally exclude
  physical ON.
- [x] Add an audited guided validation harness for repeatable identity, snapshot,
  EEPROM-integrity, input, trim, and separately gated remote-control sessions.
- [ ] Correlate CR05 and CR07 with passive J10/J9 observations; do not run
  factory actuator tests through the unfinished interface.
- [ ] Identify the physical function of CR02.1 by cold/off correlation.

## Phase 2 - read-only cross-platform monitor

- [x] Decode addressed/telemetry response framing statically and in emulation.
- [x] Add platform-neutral serial-port discovery for Windows, Linux, and macOS.
- [x] Add timeout-bounded addressed-response matching that skips interleaved telemetry.
- [x] Add the read-only controller identity sequence, exact JSONL traffic
  recording, and a lossless A00-AFF JSON backup artifact with checksum checks.
- [x] Add Windows/Linux/macOS CI coverage while keeping the POSIX PTY endpoint
  outside the portable core.
- [x] Match addressed replies until transport timeout and resynchronize after a
  bounded partial opening line; live regression covers more than 16 interleaved
  telemetry frames.
- [x] Implement latest-value monitoring state and stale-data detection with
  explicit age/freshness fields.
- [x] Map BixCheck T-stream indexes, physical slots, producer sources, widths,
  and core numeric conversions to the vendor telemetry fields.
- [ ] Complete remaining status/flag meanings, physical calibration, table-only
  TFD-TFF provenance, and M/I payload semantics.
- [x] Expose profile-aware alarm state, including temporal format-04 flashing
  indicators and later-format raw BixCheck alarm status.
- [x] Prove format-04 T09 is non-discriminating, trace exact 2.02 state RAM
  0x4C to T0C, reject T15 as a state source, and live-confirm T0C Off/Prefill.
- [ ] Complete stove state, heat level, temperatures, fan values, door timers,
  ash values, and remaining alarm semantics.
- [x] Add decoded JSONL snapshot logging and offline replay against preserved
  live serial-capture fixtures, including format-04 door/drawer/thermostat A/B cases.
- [ ] Add a flattened CSV export after the stable monitor field set is validated live.
- [x] Validate three identical complete format-04 A00-AFF backups with matching
  stored/calculated checksum against serial 5215.
- [ ] Publish checksummed standalone Windows, Linux, and macOS packages.

## Phase 3 - verified normal control

- [x] Add offline-tested generic A/C/D writes, optional fresh-readback
  verification, exact complete-request exchange, and fail-fast JSON register
  transactions; later disable arbitrary/fragmented raw transmission.
- [x] Prevent possible write echoes from satisfying readback matching; require
  an actual addressed `R` response.
- [x] Isolate known loader traffic from generic raw/transaction commands.
- [x] Validate OFF, ON, UP, and DOWN individually on firmware 2.02 with exact
  traffic preservation and operator-observed physical response.
- [ ] Read back state after every command.
- [x] Demonstrate that one OFF can be ignored during the post-ON UART-silent
  interval; make the validation harness retry OFF until two distinct state
  samples timestamped after OFF prove Off or Cooldown.
- [x] Add offline idempotent OFF/ON/UP/DOWN/set-level planning with profile and
  stale-state checks; live rate limits, lockouts, and recovery remain pending.
- [x] Execute and verify complete control workflows against the public simulator
  with authorization, rate limiting, and door/drawer interlocks; physical use
  remains blocked.
- [x] Never infer success from transmission alone; require machine or explicit
  operator observation and report missing verification as indeterminate/fail.
- [ ] Expose only the everyday safe subset to Home Assistant.

## Phase 4 - BixCheck configuration parity

- [x] Decode identification, checksum, data-format, serial-number, production-date, and model addresses statically.
- [x] Implement offline-tested read-only AR00-AFF readback and durable backups.
- [x] Validate identity strings, checksum, and three identical read-only backups
  against serial 5215; restore remains unimplemented and unauthorized.
- [x] Generate the recovered format-05/07 fuel A/B fan, feed, ash, startup,
  igniter, ash-dump, convection, flag, and lean-burn field schemas.
- [x] Add offline range validation, version/data-format checks, typed edits,
  diff/restore plans, checksum persistence, identity preservation, and a
  whole-image verification contract; execution remains blocked.
- [x] Execute the complete configuration plan against simulation with an exact
  pre-write image check, backup hash, CW01 checksum persistence, and A00-AFF
  post-write comparison; physical use remains blocked.
- [ ] Keep full memory formatting behind a separate expert workflow.

## Phase 5 - service and factory Checkout parity

- [x] Represent all 45 reachable documented tests as a machine-readable API catalog.
- [x] Keep actuator tests separate from normal-operation APIs.
- [x] Require explicit API authorization for simulated actuator workflows;
  operator confirmation remains a client responsibility.
- [x] Add structured Checkout result/report models with configuration-backup identity.
- [x] Add a bounded read-only runner for every machine-evaluable passive test
  and a simulator-only actuator executor with unconditional cleanup.
- [ ] Add raw/debug communication tools for research.

## Phase 6 - firmware servicing

- [x] Decode Downloader/PICkit identify and program-block framing; confirm
  reset-time `EA`/`EB` in emulation.
- [ ] Resolve erase/program acknowledgement semantics and validate recovery on
  sacrificial bench hardware.
- [x] Distinguish Downloader and PICkit firmware layouts and preserve their exact word-level delta.
- [x] Implement strict Intel HEX/PIC14 images, metadata, target/data-format
  compatibility checks, and reconstructed E3 program-block planning.
- [x] Add an isolated simulator-only identify/program/complete state machine,
  bounded acknowledgement retries, progress receipts, exact audit spans,
  disconnect/corruption injection, and final simulated-memory comparison.
- [x] Add classified E8/E5 responses, four-word partial-row preservation, two
  internal row attempts, protected-range skipping, reset-vector relocation,
  BixCheck's exact 30-accepted/31st-unread retry edge, one-shot completion, and
  simulated application handoff/reconnect.
- [x] Implement authenticated planning, a historical zero-E3 physical research
  rehearsal now retired, and a complete simulator-only rehearsal/write/recovery state machine: exact file and
  wire-frame allowlist and rescue bundle, fixed 9,600-baud loader, rapid
  reset-window probing, repeated identity/EEPROM preflight, outcome-specific
  retries, durable state, phase-matched delayed replies, target identity, and
  EEPROM comparison. Hard-lock all physical loader traffic in the CLI and
  public executors.
- [ ] After the target-power-safe reset fixture passes its spare-target gates,
  add separately reviewed fixture-specific non-writing and write executors; do
  not revive the retired manual-AC/BREAK path.
- [x] Document a PICkit 3 original-chip read procedure with a hard code-
  protection stop and offline repeated-read/clone authentication commands.
- [x] Read and preserve one complete firmware 2.02 program-memory, EEPROM,
  configuration, and User-ID export.
- [x] Preserve and hash the sole pre-write 2.02 export; record that later reads
  can verify restored state but cannot independently authenticate the former
  factory state.
- [ ] Program only a spare chip, verify it, read it back, authenticate it
  against the original, and prove controlled board recovery.
- [ ] Resolve physical loader entry timing, row programming/readback behavior,
  interrupted-transfer recovery, application reconnect, and post-flash
  calibration guidance on sacrificial hardware.
- [ ] Execute and publish the complete multi-controller, multi-host, multi-
  adapter forced-interruption matrix in the
  [J3 flasher qualification plan](guides/j3-flasher-qualification.md).
- [ ] Do not flash a production controller until recovery has been proven on spare hardware.

## Phase 7 - permanent controller

- [x] Document the candidate Olimex ESP32-POE-ISO-IND plus consolidated
  stove-interface daughterboard architecture.
- [x] Split the product plan into a full controller and a later separate,
  low-cost portable service cable; keep complete J3 and provisional main-board
  J5/PICkit capability in the full controller.
- [x] Implement the fresh four-layer Rev A in tscircuit with ESP32-S3, native
  USB, FTDI service, isolated target interface, hardware watchdog/latch,
  released-state thermostat fail-back, protected power, test points, and
  powered-off-isolating expansion I/O.
- [x] Add a verified Specctra export/session-import/KiCad handoff that checks
  physical pad coordinates and net membership, preserves four-layer vias, and
  enforces the 8 mm isolation keepout in both Freerouting and KiCad.
- [x] Correct the expansion interface so its 1-Wire pull-up is connector-side
  and signal OE requires firmware enable, delayed rail-good, and inactive
  current-limit fault in hardware.
- [x] Reconcile the engineering BOM to the corrected 250-reference source and
  document every unresolved purchasing and footprint gate.
- [ ] Complete J3-3 powered-voltage/source-limit, UART idle-level/noise-margin,
  and thermostat-contact measurements required to select isolation,
  protection, and relay ratings.
- [ ] Prototype isolated read-only UART with the controller powered independently
  from J3.
- [ ] Prototype the non-latching thermostat transfer relay and verify that its
  de-energized state reconnects the physical backup thermostat.
- [x] Document a preliminary consolidated daughterboard circuit with integrated
  isolated UART power, heartbeat-qualified relay driver, protection footprints,
  connectors, signal allocation, parts list, and layout constraints.
- [ ] Route the post-safety-fix Rev A input to zero airwires, import it through
  the checked handoff, refill zones, and close native KiCad DRC with zero
  unexplained violations before generating any fabrication archive.
- [ ] Independently verify every exact footprint, polarity, pin-one convention,
  connector orientation, relay pinout, mode-switch truth table, and provisional
  main-board J5 mapping against drawings and received parts.
- [ ] Design the enclosure, antenna mounting, cable strain relief, harnesses,
  labels, passive thermostat bypass, and force-backup loop as controlled
  manufacturing artifacts.
- [ ] Build current-limited offline first articles and complete the full
  validation/bring-up matrix before any installed-stove evaluation.
- [ ] Limit the permanent controller to telemetry, faults, start/stop, heat level,
  command verification, and local temperature control.
- [ ] Preserve factory front-panel operation and transfer to the physical backup
  thermostat whenever the ESP32 is booting, failed, unpowered, or stale.
- [ ] Add optional heating-source coordination only after stove control and the
  complete failure matrix are proven reliable.

See [Candidate permanent-controller hardware](hardware/permanent-controller-candidate.md)

## Phase 8 - portable service cable

- [ ] Begin only after the full controller's J3/J5 service interface and
  partial-power behavior are electrically qualified.
- [ ] Derive a separate small, low-cost board without the ESP32, permanent
  supply, thermostat relay, or expansion circuitry.
- [ ] Preserve the same target-safe J3 behavior, provisional main-board J5
  identification boundary, FTDI support, keying, labeling, and serialized cable
  continuity tests established by the full controller.
and [Preliminary stove-interface daughterboard design](hardware/daughterboard-preliminary-design.md).
