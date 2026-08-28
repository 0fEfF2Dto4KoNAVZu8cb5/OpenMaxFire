# Firmware research archive

This tree contains deterministic extractions and static analysis for every
preserved Bixby stove-firmware generation. The three source packages and the
original-controller 2.02 read are never modified; extracted images and all
analysis outputs are derived copies.

## Image index

| Generation | Delivery image | Bytes | Program words | Program range | Config | SHA-256 |
| --- | --- | ---: | ---: | --- | --- | --- |
| 2.02 | Original PICkit read | 46,536 | 8,192 | `0x0000-0x1FFF` | `0x3F32` | `272b12f6f1b42a934e8bb6dab79aa4e9c08748124f1a74ba1d5425b84decccab` |
| 2.06 | Downloader | 42,831 | 7,599 | `0x0000-0x1E26`, sparse | `0x3F76` | `90a5289f273d79bf1ee0029777940d6d4cecfc15041d12f5b24a869ce9b30f0b` |
| 2.06 | PICkit | 47,596 | 8,192 | `0x0000-0x1FFF` | `0x3F32` | `2adb6dca20a0318662aa73d96b700d5f83a76b36779596fa0e9db8a26db357d4` |
| 2.70 | Embedded | 42,336 | 7,681 | `0x0000-0x1E3E`, sparse | `0x3F72` | `c6decc8173cadd13f59743df416d783c6de22e55cc9636f5f79dd22dec3e7bca` |
| 2.71 | Embedded | 42,740 | 7,755 | `0x0000-0x1E5E`, sparse | `0x3F72` | `dc4dcf7aeb83c95525053018e010194c55498796b0b65c0ff26a11eb695e556b` |

All five images identify the target as `PIC16F877A`. “Program words” excludes user-ID, configuration, and EEPROM spaces.

> **Have an unlisted firmware version?** If you have MaxFire firmware from a
> version not listed above, please contact me at [contact@openmaxfire.com](mailto:contact@openmaxfire.com) or open a pull request so it can
> be preserved and reverse-engineered.

## Source-package relationships

- `preservation/original/firmware/2.02/Bixby_0202_260827_PICkit.hex` is the
  owner-supplied first complete read from serial 5215's original controller.
  Its EEPROM exactly matches the earlier live J3 backup; repeat PICkit exports
  remain pending.
- `Bixby110_115_02060021_and_manual.zip` contains the two 2.06 HEX files directly. The vendor notes distinguish the Downloader and external-PICkit workflows.
- `BixCheck_080206.zip` contains `BixCheck_080206.exe`; the executable embeds `Bixby_0270_070206.hex` as an ASCII-hex-encoded Intel HEX file.
- `BixCheck_080315.zip` contains `BixCheck_080315.exe` and embeds 2.71 by the same method. A clean regeneration exactly matches the previously recovered 2.71 file.

Exact executable offsets and hashes are in `extraction-metadata.json`. Every ZIP member is indexed in `package-inventory.json`.

## Generated artifacts

Each image has:

- its exact extracted Intel HEX source;
- a JSON summary with hashes, record counts, memory layout, and decode statistics;
- CSV memory ranges and decoded program words;
- a sparse-aware program binary, padded with `0xFF` only between mapped program addresses;
- portable raw and annotated PIC14 assembly listings.

`comparison/multiplexed-inputs.csv` records the common front-panel and
external-switch mux selectors across 2.06, 2.70, and 2.71, including exact
routine addresses, PORTD selector values, CR mappings, interpretations, and
confidence boundaries.

`comparison/sensor-signal-paths.csv` records the complete J10 exhaust-sensor
and J9 feeder-wheel producer chains in every application generation. The
pipeline verifies masked opcode signatures for T0CKI setup, counter latching,
RD0 cycle detection, interval capture, and CR07 scaling before emitting it.

`comparison/2.02-vs-2.06-pickit.json` records the initial recovered-image
comparison. The complete protected loader range is identical, while 7,478 of
7,808 application-range words differ at the same addresses.

`emulation/` contains experimental execution evidence from
`tools/pic14_emulator.py`: per-image summaries, UART/peripheral events, and
recent instruction traces. Its `deep/` subtree contains the exhaustive 45-read
CR matrix, handler RAM/SFR dependencies, watchpoints, GPIO/ADC differentials,
and 768 verified synthetic internal-EEPROM reads. It also corroborates the
PICkit loader's reset-time `EA`→`EB` identify pair. See the
[deep-pass report](../../docs/reverse-engineering/emulator-deep-pass.md).

The earlier gpdasm-based 2.71 bundle is retained as independent prior work. The portable decoder was checked against it and produced zero mnemonic/word mismatches over all 7,755 mapped 2.71 program words.

## Regeneration

From the repository root:

```bash
python3 tools/firmware_pipeline.py project --repo-root .
python3 tools/pic14_emulator.py project --repo-root .
```

The pipeline uses only Python's standard library, verifies every Intel HEX checksum, rejects conflicting/partial words, and emits deterministic outputs. It does not contain any device-write or serial communication path.

See [the comparative report](../../docs/reverse-engineering/firmware-comparison.md) for findings and cautions.
