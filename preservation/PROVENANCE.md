# Provenance and derivation graph

## BixCheck 5.5.01 line

`BixCheck_080315.zip`

- contains `BixCheck_080315.exe`
- the executable embeds `Bixby_0271_080315.hex`
- the embedded HEX was extracted without intentional modification; deterministic re-extraction matches the prior copy byte-for-byte
- the HEX was parsed to a 16,400-byte address-span binary
- gpdasm produced raw and reassemblable PIC16F877A listings
- the annotated listing adds comments while leaving instruction lines intact

## BixCheck 5.5.00 line

`BixCheck_080206.zip`

- contains `BixCheck_080206.exe`
- executable strings identify BixCheck 5.5.00, Downloader 2.70, stove software 02.70, and database 07
- the executable embeds ASCII-hex-encoded `Bixby_0270_070206.hex`
- deterministic extraction produced a checksum-valid PIC16F877A image with SHA-256 `c6decc8173cadd13f59743df416d783c6de22e55cc9636f5f79dd22dec3e7bca`

## BixCheck 5.0.21 / firmware 2.06 line

`Bixby110_115_02060021_and_manual.zip`

- contains distinct Downloader and PICkit firmware images
- contains BixCheck 5.0.21 and vendor release notes
- contains the BixCheck How-To Guide as `2023480-A.pdf`
- the standalone `1394047.pdf` has the same SHA-256 as that manual member
- exact extraction shows the same main application in both firmware files; the PICkit image adds reset redirection, service/bootloader code, and EEPROM defaults

## MaxFire Model 115 owner-manual line

`7346103.pdf`

- was supplied by the stove owner on 2026-08-21 and is preserved byte-for-byte under `original/manuals/`;
- is a 40-page factory *Installation, Operating and Maintenance Instructions* manual, printed document `2020866 REV A`;
- has embedded title `Owner Manual_115_2020866 Rev A` and author metadata `Bixby Energy Systems`;
- has PDF creation metadata 2005-10-17 and modification metadata 2008-10-22; those file dates are not treated as independently verified publication dates; and
- has SHA-256 `ed04d708590fa8bec0d0276463abd736409ddbdd8d8eee6c7a66fb0cd7fba33d`.

Its owner-manual statements are vendor-documented evidence for the appliance,
but Rev. A behavior is not automatically generalized to later format-07
firmware/configuration features.

## Original-controller firmware 2.02 line

`Bixby_0202_260827_PICkit.hex`

- was supplied by the stove owner on 2026-08-28 as a PICkit export from the
  original PIC16F877A removed from serial 5215's `9067-0604` controller;
- is preserved byte-for-byte under `original/firmware/2.02/` with SHA-256
  `272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab`;
- contains all 8,192 program words, all 256 EEPROM bytes, four User ID words,
  and configuration word `0x3F32`, with CP and CPD disabled;
- contains EEPROM bytes identical to the independently preserved 2026-08-22
  J3 backup from the controller while it identified as 2.02/data format 04;
- contains a protected loader range identical to the factory 2.06 PICkit image;
  and
- is one complete read, not yet an independently repeated read set. Additional
  owner exports and programmer logs remain pending.

## Deterministic analysis line

`tools/firmware_pipeline.py` reads the three preserved ZIP packages and the
immutable original-controller 2.02 read, inventories every package member,
produces five firmware analysis copies, validates every Intel HEX checksum,
parses sparse PIC memory, disassembles the PIC14 instruction words, and produces
comparison tables. Generated outputs are reproducible and contain no device-
communication path.

Derived work must always point back to one of these preserved sources and record the exact source SHA-256.

## Motherboard-diagram line

`1000000387.jpg`

- was supplied by the stove owner on 2026-08-20 after being found online;
- is preserved byte-for-byte as `original/diagrams/maxfire-mother-board-pinout.jpg`;
- visibly identifies the pictured PCB as `9067-0404`;
- has an indexed public match titled `115 110 Mother Board Pin Out` on Scribd;
- has no verified original author, issue date, or vendor-publication status; and
- is used only as related-family corroboration because serial 5215's installed
  board is owner-reported as `9067-0604`, with its `-0604` suffix corroborated
  by the installed photographs.

The hardware cross-reference records which labels agree with independently
recovered firmware and BixCheck behavior. It does not promote the image to an
exact revision-specific schematic or J3 electrical pinout.

## Installed-controller photograph line

`1000000390.jpg` through `1000000400.jpg` (eleven supplied files)

- were supplied by the stove owner on 2026-08-21;
- are preserved byte-for-byte under
  `original/photos/serial-5215-installed-controller/` with the received names;
- directly show the installed component side, harnesses, auxiliary board, and
  stove interior;
- visibly confirm the main PCB's `-0604` silkscreen suffix and the black,
  four-contact main-board J3 housing, corroborating the owner-reported full
  `9067-0604` part number; and
- do not show the solder side or establish any J3 pin function/electrical level.

The research index records image-by-image content without altering the original
JPEGs. Temporary crops used for visual inspection are not preservation files
and are not included in the repository.

## Bare-controller photograph line

Seven unique JPEG byte streams were supplied on 2026-08-22. Two `PXL` filename
pairs were byte-identical duplicates; the repository retains one copy of each
unique stream under descriptive names in
`original/photos/serial-5215-bare-controller/` and records every received alias
in `MANIFEST.md`.

The set directly exposes the full component and solder sides, complete
`9067-0604` silkscreen, PIC16F877A-I/P, `10.000` oscillator, J3/PIC routing
area, and working FTDI attachment. Owner-performed continuity observations are
documented separately from what pixels alone prove.

The accompanying `1000000401.mp4` is hash-catalogued in `MANIFEST.md` but is
not committed to Git because it is 78,737,900 bytes. It remains pending an
external preservation target.

## Live controller evidence line

The 2026-08-22 read-only session produced JSONL serial traffic, an adapter
inventory, and a lossless A00-AFF EEPROM artifact. These device-generated
research records are preserved under
`research/live/2026-08-22-fw202-format04/`, outside `original/`, with their own
SHA-256 inventory. The directory README distinguishes raw evidence from the
interpreted live report.
