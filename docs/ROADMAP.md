# Roadmap

## Phase 0 - preservation foundation

- [x] Preserve recovered vendor ZIP packages and standalone BixCheck 5.5.01 executable.
- [x] Preserve the BixCheck 5.x manual and release notes.
- [x] Extract and checksum all 2.06, 2.70, and 2.71 firmware delivery images.
- [x] Preserve the earlier 2.71 analysis bundle and independent gpdasm disassembly.
- [x] Add a dependency-free Intel HEX parser/PIC14 disassembler and deterministic analysis for all images.
- [x] Map cross-version protocol anchors, constant CR responses, UART changes, and the 2.06 bootloader/EEPROM delta.
- [x] Record hashes, sizes, provenance, and the relationship between original and derived files.
- [x] Preserve the prior OpenMaxFire v0.1 snapshot.
- [ ] Publish a public preservation copy to Archive.org after reviewing redistribution and privacy.

## Phase 1 - electrical and read-only bench validation

- [ ] Photograph both ends of the received cable and record all labels/part numbers.
- [ ] Identify J3 ground and supply pins without assuming standard RS-232 pinout.
- [ ] Measure idle voltage and polarity through a protected interface.
- [ ] Confirm controller oscillator frequency.
- [ ] Capture BixCheck startup traffic if the Windows application can run.
- [ ] Test read-only commands first at 38,400 baud, then 19,200 only if necessary.
- [ ] Record exact request bytes, response bytes, timing, and line termination.
- [ ] Poll CR00-CR0E with the stove safely off.
- [ ] Repeat polling while operating the fire door, ash drawer, thermostat, fuel switch, trim pots, and panel buttons.

## Phase 2 - read-only Linux monitor

- [ ] Decode acknowledgements and response framing.
- [ ] Implement robust timeouts, resynchronization, and stale-data detection.
- [ ] Map firmware register values to the vendor telemetry field list.
- [ ] Expose stove identity, state, heat level, alarms, temperatures, fan values, door timers, and ash values.
- [ ] Add CSV/JSON logging and replayable capture fixtures.
- [ ] Back up complete configuration/EEPROM before enabling any write.

## Phase 3 - verified normal control

- [ ] Validate OFF, ON, UP, and DOWN individually.
- [ ] Read back state after every command.
- [ ] Add idempotent command handling, rate limits, lockouts, and failure recovery.
- [ ] Never infer success from transmission alone.
- [ ] Expose only the everyday safe subset to Home Assistant.

## Phase 4 - BixCheck configuration parity

- [ ] Decode identification, checksum, data-format, serial-number, production-date, and model fields.
- [ ] Implement readback and backups.
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

- [ ] Decode the Downloader/PICkit serial boot protocol (its code region and reset entry are now mapped).
- [x] Distinguish Downloader and PICkit firmware layouts and preserve their exact word-level delta.
- [ ] Implement firmware identity and compatibility checks.
- [ ] Add interrupted-transfer recovery and post-flash calibration guidance.
- [ ] Do not flash a production controller until recovery has been proven on spare hardware.

## Phase 7 - permanent controller

- [ ] Build an isolated ESP32/ESPHome interface that electrically fails open.
- [ ] Limit it to telemetry, faults, start/stop, heat level, and command verification.
- [ ] Preserve factory front-panel and thermostat operation when the ESP32, network, or Home Assistant is unavailable.
- [ ] Add optional heating-source coordination only after stove control is proven reliable.
