# Firmware servicing evidence

The recovered 2.06 release package contains:

- `Bixby_02060021_Downloader.hex` for BixCheck's Downloader
- `Bixby_02060021_PICkit.hex` for a PICkit programmer
- `BixCheck_5021.exe`
- `Bixby_02060021_Notes.txt`
- the 2023480 Rev. A BixCheck manual

BixCheck 5.5.01 instead embeds `Bixby_0271_080315.hex` and labels its Downloader as version 2.71.

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

## OpenMaxFire policy

No firmware write will be implemented or attempted on serial 5215 until:

- normal read/write framing is captured;
- the boot protocol is independently decoded;
- current calibration is backed up;
- a known-good recovery image and programmer method exist;
- recovery is proven on spare or bench hardware;
- compatibility and database format are checked automatically.
