# Developer and research tools

These scripts support reproducible analysis and offline testing. User-facing
controller behavior belongs in the `openmaxfire` package and its separate CLI.

| Tool | Purpose | Hardware I/O |
| --- | --- | --- |
| `analyze_bixcheck.py` | Deterministically recover symbols, tables, call graphs, and focused assembly from preserved BixCheck executables | None |
| `firmware_pipeline.py` | Extract, authenticate, map, compare, and disassemble preserved PIC16F877A firmware | None |
| `pic14_emulator.py` | Experimental instruction/peripheral harness for controlled execution of all four preserved application generations and the resident loader identify path | None |
| `analyze_bixby_hex.sh` | Legacy convenience wrapper for firmware inspection | None |
| `virtual_serial_lab.py` | Local synthetic serial endpoint and demo | Synthetic only |
| `experimental_read_only_monitor.py` | Historical research monitor retained for comparison; current behavior is in the package/CLI | Serial reads only when explicitly run |
| `live_validation_session.py` | Guided, timestamped controller validation with exact traffic, repeated identities, EEPROM integrity, physical-input correlation, and separately gated remote-control evidence; OFF cleanup requires two distinct post-command T09/T0C samples proving Off/Cooldown | Read-only by default; optional remote buttons require explicit gates |
| `pickit_preservation.py` | Compare repeated PIC16F877A read exports or original/clone readbacks by program, EEPROM, User IDs, configuration, code protection, and SHA-256 | None; parses HEX files only |
| `compose_pickit_image.py` | Apply resident-loader address/remap rules over a complete PICkit base and generate deterministic post-J3/pre-calibration full-chip predictions | None; reads and writes HEX files only |
| `build_pickit_recovery_image.py` | Retired, analysis-only constructor for the unqualified 2.06-program/format-04-data hybrid; emits explicit do-not-program metadata and requires an acknowledgement flag | None; reads/writes HEX files only and cannot access a programmer |
| `analyze_flash_sessions.py` | Deterministic loader-frame counts, E3 byte-order checks, EEPROM hashes, journal/result summaries, and per-log EA timing from preserved flash sessions | None; opens session evidence and firmware references read-only |
| `verify_archive.sh` | Verify preserved and derived archive hashes and inventory | None |

`build_pickit_recovery_image.py` is not a recovery-image generator. Its hybrid
combines 2.06 code with serial 5215's format-04 data even though 2.06 expects
format 05 and vendor calibration/Format. The historical
`Bixby_02060021_PICkit_controller-preserved_recovery.hex` and its original
manifest are superseded forensic artifacts: do not import or program them. For
serial 5215, the conservative recovery source is the exact complete 2.02 image
named and hash-pinned in the emergency-recovery guide.

Run deterministic project regeneration from the repository root:

```bash
python tools/analyze_bixcheck.py --repo-root .
python tools/firmware_pipeline.py project --repo-root .
python tools/pic14_emulator.py project --repo-root .
PYTHONPATH=src python tools/compose_pickit_image.py project --repo-root .
bash tools/verify_archive.sh
```

Authenticate three independently exported original-chip reads without opening
a programmer connection:

```bash
PYTHONPATH=src python tools/pickit_preservation.py \
  read-01.hex read-02.hex read-03.hex \
  --output original-read-manifest.json
```

See the [PICkit 3 read-only preservation procedure](../docs/guides/pickit3-firmware-preservation.md)
before handling the original firmware-2.02 chip.

Summarize every preserved rehearsal/loader traffic log without opening a
serial port or changing the evidence:

```bash
python3 tools/analyze_flash_sessions.py --repo-root .
```

The JSON report counts loader records only in their expected direction,
classifies each `E3` payload against the session's hash-matched firmware image,
groups raw 256-byte EEPROM hashes, and reports monotonic `EA` probe gaps for
each log.
