# Developer and research tools

These scripts support reproducible analysis and offline testing. User-facing
controller behavior belongs in the `openmaxfire` package and its separate CLI.

| Tool | Purpose | Hardware I/O |
| --- | --- | --- |
| `analyze_bixcheck.py` | Deterministically recover symbols, tables, call graphs, and focused assembly from preserved BixCheck executables | None |
| `firmware_pipeline.py` | Extract, authenticate, map, compare, and disassemble preserved PIC16F877A firmware | None |
| `pic14_emulator.py` | Experimental instruction/peripheral harness for controlled execution of preserved firmware | None |
| `analyze_bixby_hex.sh` | Legacy convenience wrapper for firmware inspection | None |
| `virtual_serial_lab.py` | Local synthetic serial endpoint and demo | Synthetic only |
| `experimental_read_only_monitor.py` | Historical research monitor retained for comparison; current behavior is in the package/CLI | Serial reads only when explicitly run |
| `live_validation_session.py` | Guided, timestamped controller validation with exact traffic, repeated identities, EEPROM integrity, physical-input correlation, and separately gated remote-control evidence | Read-only by default; optional remote buttons require explicit gates |
| `pickit_preservation.py` | Compare repeated PIC16F877A read exports or original/clone readbacks by program, EEPROM, User IDs, configuration, code protection, and SHA-256 | None; parses HEX files only |
| `verify_archive.sh` | Verify preserved and derived archive hashes and inventory | None |

Run deterministic project regeneration from the repository root:

```bash
python tools/analyze_bixcheck.py --repo-root .
python tools/firmware_pipeline.py project --repo-root .
python tools/pic14_emulator.py project --repo-root .
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
