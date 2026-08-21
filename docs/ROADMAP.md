# Roadmap

## Phase 0 - preservation foundation

- [x] Preserve recovered vendor ZIP packages and standalone BixCheck 5.5.01 executable.
- [x] Preserve the BixCheck 5.x manual and release notes.
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
- [ ] Publish a public preservation copy to Archive.org after reviewing redistribution and privacy.

## Phase 1 - electrical and read-only bench validation

- [ ] Photograph both ends of the received cable and record all labels/part numbers.
- [x] Photograph the component side and J3 area of the installed 9067-0604 board
  and compare visible connector placement with the preserved 9067-0404 diagram.
- [ ] Photograph the unobstructed full part-number silkscreen and solder side of
  the installed board, then trace J3 without assuming the 9067-0404 routing.
- [ ] Identify J3 ground and supply pins without assuming standard RS-232 pinout.
- [ ] Measure idle voltage and polarity through a protected interface.
- [ ] Confirm controller oscillator frequency.
- [ ] Capture BixCheck startup traffic if the Windows application can run.
- [ ] Test only `CR00` at 9,600 for likely 2.06; try 19,200 only if the
  protected electrical capture shows no valid response.
- [ ] Record exact request bytes, response bytes, timing, and line termination.
- [ ] Poll CR00-CR0E with the stove safely off.
- [ ] Repeat polling while operating the fire door, ash drawer, thermostat, fuel switch, trim pots, and panel buttons.
- [ ] Correlate CR05 and CR07 with passive J10/J9 observations; do not run
  factory actuator tests through the unfinished interface.
- [ ] Identify the physical function of CR02.1 by cold/off correlation.

## Phase 2 - read-only cross-platform monitor

- [x] Decode addressed/telemetry response framing statically and in emulation.
- [x] Add platform-neutral serial-port discovery for Windows, Linux, and macOS.
- [x] Add bounded addressed-response matching that skips interleaved telemetry.
- [x] Add the read-only controller identity sequence, exact JSONL traffic
  recording, and a lossless A00-AFF JSON backup artifact with checksum checks.
- [x] Add Windows/Linux/macOS CI coverage while keeping the POSIX PTY endpoint
  outside the portable core.
- [ ] Implement robust timeouts, resynchronization, and stale-data detection.
- [x] Map BixCheck T-stream indexes, physical slots, producer sources, widths,
  and core numeric conversions to the vendor telemetry fields.
- [ ] Complete remaining status/flag meanings, physical calibration, table-only
  TFD-TFF provenance, and M/I payload semantics.
- [ ] Expose stove identity, state, heat level, alarms, temperatures, fan values, door timers, and ash values.
- [ ] Add CSV/JSON logging and replayable capture fixtures.
- [ ] Validate the complete configuration/EEPROM backup against serial 5215
  before enabling any write.
- [ ] Publish checksummed standalone Windows, Linux, and macOS packages.

## Phase 3 - verified normal control

- [ ] Validate OFF, ON, UP, and DOWN individually.
- [ ] Read back state after every command.
- [ ] Add idempotent command handling, rate limits, lockouts, and failure recovery.
- [ ] Never infer success from transmission alone.
- [ ] Expose only the everyday safe subset to Home Assistant.

## Phase 4 - BixCheck configuration parity

- [x] Decode identification, checksum, data-format, serial-number, production-date, and model addresses statically.
- [x] Implement offline-tested read-only AR00-AFF readback and durable backups.
- [ ] Validate identity strings, checksum, and backup round-trip against serial
  5215 before implementing restore.
- [ ] Map fuel A/B fan, feed, ash, startup, igniter, ash-dump, and convection-fan calibration fields.
- [ ] Add range validation, version/data-format checks, diff preview, verify-after-write, and restore.
- [ ] Keep full memory formatting behind a separate expert workflow.

## Phase 5 - service and factory Checkout parity

- [ ] Reproduce the 45 documented tests.
- [ ] Keep actuator tests separate from normal-operation APIs.
- [ ] Require explicit test context and operator confirmation.
- [ ] Generate durable Checkout reports with calibration backup.
- [ ] Add raw/debug communication tools for research.

## Phase 6 - firmware servicing

- [x] Decode Downloader/PICkit identify and program-block framing; confirm
  reset-time `EA`/`EB` in emulation.
- [ ] Resolve erase/program acknowledgement semantics and validate recovery on
  sacrificial bench hardware.
- [x] Distinguish Downloader and PICkit firmware layouts and preserve their exact word-level delta.
- [ ] Implement firmware identity and compatibility checks.
- [ ] Add interrupted-transfer recovery and post-flash calibration guidance.
- [ ] Do not flash a production controller until recovery has been proven on spare hardware.

## Phase 7 - permanent controller

- [ ] Build an isolated ESP32/ESPHome interface that electrically fails open.
- [ ] Limit it to telemetry, faults, start/stop, heat level, and command verification.
- [ ] Preserve factory front-panel and thermostat operation when the ESP32, network, or Home Assistant is unavailable.
- [ ] Add optional heating-source coordination only after stove control is proven reliable.
