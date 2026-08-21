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

## Deterministic analysis line

`tools/firmware_pipeline.py` reads the three preserved ZIP packages, inventories every member, extracts four firmware delivery images, validates all Intel HEX checksums, parses sparse PIC memory, disassembles the PIC14 instruction words, and produces comparison tables. Generated outputs are reproducible and contain no device-communication path.

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

`1000000390.jpg` through `1000000400.jpg` (ten supplied files; no `0393`)

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
