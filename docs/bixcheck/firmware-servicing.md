# Firmware servicing evidence

The recovered 2.06 release package contains:

- `Bixby_02060021_Downloader.hex` for BixCheck's Downloader
- `Bixby_02060021_PICkit.hex` for a PICkit programmer
- `BixCheck_5021.exe`
- `Bixby_02060021_Notes.txt`
- the 2023480 Rev. A BixCheck manual

BixCheck 5.5.01 embeds `Bixby_0271_080315.hex` and labels its Downloader
version 2.71.

BixCheck 5.5.00 embeds `Bixby_0270_070206.hex` and labels its Downloader
version 2.70. The static pipeline deterministically extracts both ASCII-hex
embedded payloads and validates their Intel HEX checksums.

## Image types are not interchangeable

The 2.06 PICkit image is a complete external-programmer image. It maps all
8,192 PIC16F877A program words, including the resident loader, and contains
256 data-EEPROM bytes. It also has a different configuration word from the
2.06 Downloader image.

The 2.06 Downloader image and the images embedded in BixCheck 5.5.00 and
5.5.01 update the application through the loader already in the PIC. They
must not be substituted for a full PICkit recovery image, and the full PICkit
image must not be sent through the J3 Downloader.

## Vendor workflow

1. Connect the custom PC cable to J3.
2. Start the matching BixCheck version and select the serial port.
3. Open Downloader.
4. Unplug the stove.
5. Load the matching `_Downloader` image or use BixCheck's internal copy.
6. Select Send.
7. Plug in the stove so the downloader can identify it and transfer the image.
8. Wait for 100% completion; the 2.06 notes estimate about two minutes.
9. Exit Downloader and recalibrate or format with the matching Monitor if
   required.

The BixCheck 5.5.01 user-facing strings say to plug the igniters back in after
the download completes, indicating that the vendor servicing procedure
expected them to be disconnected during programming.

The manual warns that an interrupted transfer can leave the stove
non-functional. It says the update can be attempted again because the
protected update software is not damaged.

## Reconstructed update sequence

All three recovered BixCheck Downloader implementations are semantically
identical. They:

1. Read `CR08` and `CR0B` through `CR0E`.
2. Optionally issue the state-changing reset request `CW0FC4` when the installed
   application supports it. Exact original 2.02 does not; 2.06/2.70/2.71 do.
3. Repeatedly send `EA` until the reset-time loader answers `EB`.
4. Transfer binary `E3` program blocks containing a PIC word address, byte
   count, additive data checksum, and no more than 32 data bytes.
5. Require `E7` when the PIC accepts a block checksum.
6. Require `E4` after the PIC writes and reads the block back successfully.
7. Retransmit the whole block after a timeout or unexpected response.
8. Send `ED` and require a final `E4` before the application starts.

The PIC returns `E8` when the received data checksum is wrong and `E5` when
writing or PIC-side readback verification fails. BixCheck does not explain
those replies separately; both enter its generic block-retry path.

See the [complete protocol reconstruction](../reverse-engineering/bixcheck-downloader-protocol.md).

## What the loader changes

The loader writes Flash in four-word rows using the PIC's required erase and
write sequence. It preserves neighboring words during a partial-row update,
reads programmed words back, and makes up to two row-write attempts. There is
no standalone whole-chip erase command in the J3 protocol.

The loader protects direct addresses at and above `0x1E80`. The application
reset vector at `0x0000` through `0x0003` is redirected to a trampoline at
`0x1E84` through `0x1E87`, leaving the physical reset vector under loader
control.

The recovered Downloader images contain no data-EEPROM words, so ordinary J3
updates leave calibration and settings EEPROM in place. Configuration and
User ID records in the HEX files fall within the loader's skip range and are
not applied through J3.

BixCheck does not perform a final whole-image readback. Its positive evidence
is the PIC's local `E4` response after each block and the final `ED`/`E4`
exchange.

## Recovery boundary

A failed J3 update can normally be retried because the reset vector and
resident loader are outside the normal application update path. J3 cannot
recover a loader or physical reset vector damaged by external programming.
That requires a PICkit or equivalent programmer and a verified complete
image.

The first complete original-chip read now proves that firmware 2.02 carries
the same protected loader as the preserved 2.06 PICkit image. Its electrical
timing and interrupted-transfer recovery remain unvalidated. Later J3
Downloader images still do not replace a complete external-programmer image.

## Derived complete PICkit predictions

OpenMaxFire can now construct a complete predicted programmer image from a
complete PICkit base plus one or more authenticated Downloader images. The
composer applies the loader's actual effective targets: source reset words are
relocated to `0x1E84`-`0x1E87`, sparse missing words are retained, and physical
reset, resident loader, User IDs, configuration, and EEPROM remain from the
base. Downloader metadata records are not substituted into those protected
sections.

This model passes a factory golden check: applying the 2.06 Downloader to the
factory 2.06 PICkit base reproduces every mapped memory byte of the factory
PICkit image. Derived 2.70/2.71 factory-lineage images and the predicted
serial-5215 2.06/2.70/2.71 sequence are preserved under
`reverse-engineering/firmware/derived-pickit/` with hashes and manifests.

They represent the immediate post-download state. They cannot predict later
Individualize, Format, or calibration writes, and they are not vendor-supplied
images. A whole-chip physical read from an expendable PIC immediately after J3
programming must match before they are promoted to verified recovery images.

## OpenMaxFire policy

Version 0.9 provides offline planning plus simulator-only rehearsal and complete
write executors. Its historical physical zero-write research path is now
retired. Failed physical first-block attempts
provided adverse evidence, not a validated updater; the corrected frame has
never been sent. The CLI and public executors reject all physical loader
traffic before its first byte. New fixture-specific paths will not be added until:

- the sole pre-write 2.02 program/EEPROM/configuration/User-ID read is preserved
  immutably and a spare readback is matched against it;
- a 2.02 clone is proven on a spare PIC;
- full external-programmer recovery is proven on expendable hardware;
- the loader exchange is first captured and validated on expendable hardware;
- the newly decoded `E5`, `E8`, protection, row-write, retry, and completion
  behavior is represented in the loader simulator (completed in v0.8);
- current calibration is backed up;
- image, controller, and data-format compatibility are checked automatically;
- interruption and recovery tests pass on a bench controller that is not
  responsible for heating.

The original-chip preparation and offline dump-authentication commands are in
the [PICkit 3 read-only preservation guide](../guides/pickit3-firmware-preservation.md).
That workflow stops rather than erases if code protection is enabled or
unknown. The retained offline planner and simulator host, its stronger checks, and
the bench qualification procedure are documented in the
[guarded J3 flashing guide](../guides/safe-j3-firmware-flashing.md). Physical
release requires every case in the
[J3 flasher qualification plan](../guides/j3-flasher-qualification.md).
