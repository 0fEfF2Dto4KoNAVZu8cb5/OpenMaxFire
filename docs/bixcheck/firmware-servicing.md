# Firmware servicing evidence

The recovered 2.06 release package contains:

- `Bixby_02060021_Downloader.hex` for BixCheck's Downloader
- `Bixby_02060021_PICkit.hex` for a PICkit programmer
- `BixCheck_5021.exe`
- `Bixby_02060021_Notes.txt`
- the 2023480 Rev. A BixCheck manual

BixCheck 5.5.01 instead embeds `Bixby_0271_080315.hex` and labels its Downloader as version 2.71.

BixCheck 5.5.00 embeds `Bixby_0270_070206.hex` and labels its Downloader as
version 2.70. The static pipeline deterministically extracts both ASCII-hex
embedded payloads and validates their Intel HEX checksums.

## Vendor workflow

1. Connect the custom PC cable to J3.
2. Start the matching BixCheck version and select the serial port.
3. Open Downloader.
4. Unplug the stove.
5. Load the matching `_Downloader` image or use BixCheck's internal copy.
6. Select Send.
7. Plug in the stove so the downloader can identify it and transfer the image.
8. Wait for 100% completion; the 2.06 notes estimate about two minutes.
9. Exit Downloader and recalibrate/format with the matching Monitor if required.

The manual warns that an interrupted transfer can leave the stove non-functional, although the update can be attempted again because the protected update software is not damaged.

## Reconstructed wire sequence

All three Downloader implementations are semantically equivalent. They read
CR08 and CR0B-CR0E, issue state-changing reset request `CW0FC4`, identify the
reset-time loader with raw `EA`/`EB`, and transfer binary `E3` program blocks.
Each block carries a PIC word address, byte count, additive data checksum, and
up to 32 data bytes. `ED` finishes the transfer.

The experimental emulator executes the PICkit reset-time code and confirms
that `EA` produces `EB`. It intentionally does not attempt erase/program
operations. See [the protocol reconstruction](../reverse-engineering/bixcheck-downloader-protocol.md).

## OpenMaxFire policy

No firmware write will be implemented or attempted on serial 5215 until:

- normal read/write framing is captured;
- the remaining boot acknowledgement/erase semantics are independently decoded;
- current calibration is backed up;
- a known-good recovery image and programmer method exist;
- recovery is proven on spare or bench hardware;
- compatibility and database format are checked automatically.
