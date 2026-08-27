# Test suite

The suite is intentionally split by responsibility while remaining runnable
with the standard library's `unittest` discovery:

```bash
python -m unittest discover -s tests -v
```

| Group | Files | Purpose |
| --- | --- | --- |
| Protocol and transport | `test_protocol.py`, `test_transport.py`, `test_client.py`, `test_transactions.py` | Exact bytes, parsing, timeouts, matching, recording, and generic A/C/D behavior |
| Controller API | `test_profiles.py`, `test_discovery.py`, `test_models.py`, `test_monitor.py`, `test_session.py` | Exact profiles, detection, typed state, replay, and owned sessions |
| Service domains | `test_control.py`, `test_configuration.py`, `test_checkout.py`, `test_services.py`, `test_backup.py` | Plans, interlocks, workflows, cleanup, backups, and structured results |
| Firmware laboratory | `test_firmware.py`, `test_firmware_catalog.py`, `test_loader.py`, `test_preservation.py`, `test_simulator.py` | Intel HEX, preserved corpus, loader rows/replies/retries/handoff, dump authentication, corruption, and isolated simulation |
| Deterministic analysis | `test_bixcheck_analysis.py`, `test_firmware_pipeline.py`, `test_pic14_emulator.py` | Reproducibility and static/emulator regression coverage |
| Live-validation harness | `test_live_validation_tool.py` | Offline workflow, evidence files, conservative expectations, and overwrite refusal |
| CLI adapter | `test_cli.py` | Presentation-layer argument and safety gates without redefining controller semantics |

The cross-platform workflow runs on Python 3.11 and 3.13 under Linux, Windows,
and macOS. Tests that require the preserved firmware corpus run when those
artifacts are present in the checkout; the smaller API work export skips only
that corpus integration case.
