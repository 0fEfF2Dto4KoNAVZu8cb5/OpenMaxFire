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
- [x] Execute CR00-CR0E on all three application generations with handler-level
  RAM/SFR traces, watchpoints, and response artifacts.
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
- [x] Model PIC internal data EEPROM and verify AR00-ARFF across all three
  generations with checksum-valid format-05/07 fixtures.
- [x] Map every CW00-CW0F dispatcher/handler and execute safe synthetic probes
  in disposable CPU/RAM/EEPROM clones without taking the CW0FC4 loader branch.
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

## Phase 1 - electrical and read-only bench validation

- [ ] Photograph both ends of the received cable and record all labels/part numbers.
- [x] Photograph the component side and J3 area of the installed 9067-0604 board
  and compare visible connector placement with the preserved 9067-0404 diagram.
- [x] Photograph the unobstructed full part-number silkscreen and solder side of
  the installed board, then trace J3 without assuming the 9067-0404 routing.
- [x] Identify J3 ground/TX/RX without assuming standard RS-232; leave the
  unresolved fourth function/pin 3 disconnected.
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
- [ ] Expose stove identity, state, heat level, alarms, temperatures, fan values, door timers, and ash values.
- [x] Add decoded JSONL snapshot logging and offline replay against preserved
  live serial-capture fixtures, including format-04 door/drawer/thermostat A/B cases.
- [ ] Add a flattened CSV export after the stable monitor field set is validated live.
- [x] Validate three identical complete format-04 A00-AFF backups with matching
  stored/calculated checksum against serial 5215.
- [ ] Publish checksummed standalone Windows, Linux, and macOS packages.

## Phase 3 - verified normal control

- [x] Add offline-tested generic A/C/D writes, optional fresh-readback
  verification, exact-byte exchange, and fail-fast JSON register transactions.
- [x] Prevent possible write echoes from satisfying readback matching; require
  an actual addressed `R` response.
- [x] Isolate known loader traffic from generic raw/transaction commands.
- [ ] Validate OFF, ON, UP, and DOWN individually.
- [ ] Read back state after every command.
- [x] Add offline idempotent OFF/ON/UP/DOWN/set-level planning with profile and
  stale-state checks; live rate limits, lockouts, and recovery remain pending.
- [x] Execute and verify complete control workflows against the public simulator
  with authorization, rate limiting, and door/drawer interlocks; physical use
  remains blocked.
- [ ] Never infer success from transmission alone.
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
- [ ] Resolve physical loader entry timing, erase semantics, readback limits,
  interrupted-transfer recovery, reset, and post-flash calibration guidance.
- [ ] Do not flash a production controller until recovery has been proven on spare hardware.

## Phase 7 - permanent controller

- [x] Document the candidate Olimex ESP32-POE-ISO-IND plus consolidated
  stove-interface daughterboard architecture.
- [ ] Complete remaining J3-3, idle-level/noise-margin, and thermostat contact
  measurements required to select isolation, protection, and relay ratings.
- [ ] Prototype isolated read-only UART with the controller powered independently
  from J3.
- [ ] Prototype the non-latching thermostat transfer relay and verify that its
  de-energized state reconnects the physical backup thermostat.
- [x] Document a preliminary consolidated daughterboard circuit with integrated
  isolated UART power, heartbeat-qualified relay driver, protection footprints,
  connectors, signal allocation, parts list, and layout constraints.
- [ ] Convert the preliminary design into a reviewed KiCad schematic and PCB
  after J3 and thermostat measurements lock voltage, polarity, protection, and
  contact requirements.
- [ ] Limit the permanent controller to telemetry, faults, start/stop, heat level,
  command verification, and local temperature control.
- [ ] Preserve factory front-panel operation and transfer to the physical backup
  thermostat whenever the ESP32 is booting, failed, unpowered, or stale.
- [ ] Add optional heating-source coordination only after stove control and the
  complete failure matrix are proven reliable.

See [Candidate permanent-controller hardware](hardware/permanent-controller-candidate.md)
and [Preliminary stove-interface daughterboard design](hardware/daughterboard-preliminary-design.md).
