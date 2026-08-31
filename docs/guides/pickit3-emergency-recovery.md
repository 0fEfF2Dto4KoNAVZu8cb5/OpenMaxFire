# PICkit 3 emergency recovery boundary

Status: conservative, not-yet-qualified external-programmer procedure for a controller already
made non-operational by a failed firmware attempt. This is not a consumer
update path and is not fully qualified. The 2026-08-30 serial-5215 recovery
included a complete pre-recovery read. The operator reported loading the exact
complete 2.02 image with SHA-256
`272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab`
at `reverse-engineering/firmware/2.02/extracted/Bixby_0202_260827_PICkit.hex`
and completing Program/Verify; the controller then showed a normal 2.02/format-
04 boot and matching J3 identity/EEPROM. No IPE Program/Verify log or post-
program whole-chip readback was retained, and the procedure was not exercised
on a spare. The evidence therefore records one observed restore but does not
independently prove the programmed bytes or a repeatable process.

Only a person qualified for the appliance and programmer work should perform
this procedure. Remove the PIC from an unpowered controller and program it in
the verified socket adapter. Never attach the PICkit to a powered stove or to
another target supply. Preserve every failed-session directory unchanged.

## Preconditions

- The controller is already non-operational or its program state is uncertain;
  this procedure is not permission to overwrite a working preservation chip.
- The exact PIC16F877A orientation, PICkit header mapping, programmer version,
  and target voltage have been verified using the
  [preservation guide](pickit3-firmware-preservation.md).
- A complete recovery image is hash-pinned and independently parsed. It must
  contain the intended program memory, EEPROM, User IDs, and configuration for
  this controller. Do not improvise a hybrid image at the programmer UI.
- For serial 5215, use only the exact complete hash-pinned 2.02 image above
  until a target-calibrated format-05 recovery path is qualified. The historical
  `Bixby_02060021_PICkit_controller-preserved_recovery.hex` combines 2.06 code
  with format-04 data. It is an unqualified, unprogrammed forensic construction:
  **do not import, program, or operate it**. Its historical manifest is immutable
  incident evidence, not current authorization.
- Code-protection state is readable. If CP/CPD is enabled or unknown, stop;
  clearing protection erases the device.

## Evidence-first sequence

1. Photograph and label the chip, notch/pin 1, adapter, wiring, PICkit, and
   controller. Record IPE and programmer firmware versions.
2. Before loading any recovery image, read and export the complete uncertain
   device: program memory, EEPROM, User IDs, configuration, and Device ID when
   available. Preserve the raw export and IPE log with hashes.
3. Offline, compare that read with the last known-good image and record every
   changed region. Resolve any unexpected configuration, protection, EEPROM,
   or loader difference before programming.
4. With the chip still isolated from the controller and all other power,
   import only the exact hash-pinned complete recovery image. Reconfirm the
   selected device and every included memory region, then Program and Verify.
   Stop and preserve evidence on any voltage, device-ID, programming, or verify
   anomaly.
5. Disconnect in software, remove programmer USB power, reconnect, and perform
   a fresh full-device read to a new file. An IPE “Verify” result alone is not
   an independent readback.
6. Compare the post-program read with the intended image by program word,
   EEPROM byte, User ID, configuration, and protection state. Device-revision
   bits may be recorded separately; no unexplained content difference passes.
7. Only after that comparison passes, install the chip in a safely bench-powered
   expendable controller or electrically faithful spare fixture, with no mains
   connection and all igniters and hazardous actuator loads absent or physically
   disconnected. Confirm normal boot, read identity repeatedly, and compare two
   full J3 EEPROM reads with the recovery image. Do not enter a burn cycle.
   Testing an installed mains controller requires a separately written and
   reviewed appliance procedure; this guide does not authorize it.
8. Preserve before/after HEX files, logs, comparisons, photographs, identity
   traffic, and EEPROM captures together. A successful boot does not replace
   the missing whole-chip comparison.

For serial 5215, the one-time 2026-08-30 evidence is under
`flash-sessions/pickit-recovery-006/`. It includes no post-program HEX and must
not be described as satisfying steps 4-7 or the spare-target recovery gate.
That directory also contains the unprogrammed hybrid named above, so its mere
presence does not identify which bytes were written.
