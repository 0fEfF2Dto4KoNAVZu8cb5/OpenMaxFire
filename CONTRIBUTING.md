# Contributing to OpenMaxFire

OpenMaxFire combines ordinary source code with irreplaceable historical files
and safety-sensitive appliance research. Contributions are welcome, but those
three categories have different rules.

## Before changing anything

1. Read [SAFETY.md](SAFETY.md).
2. Check the current evidence boundary in [docs/STATUS.md](docs/STATUS.md).
3. Keep reusable controller behavior in `src/openmaxfire/`. CLI, future GUI,
   and Home Assistant clients must not duplicate protocol or safety logic.
4. Do not enable a physical state-changing path merely because it works in the
   simulator. Capability gates require preserved live evidence and a documented
   recovery path.

## Preservation rules

- Never edit a file under `preservation/original/` in place.
- Put derived output under `reverse-engineering/` and record its source.
- Update provenance, manifests, and checksums whenever a preserved or derived
  archive artifact is added or intentionally changed.
- Keep raw live traffic byte-identical. Put interpretation in documentation,
  not inside the capture.
- Do not recommit duplicate root-level bench captures after they have been
  curated under `research/live/`.
- Vendor artifacts and user photographs are not relicensed by the MIT license.

## Python development

OpenMaxFire supports Python 3.11 and 3.13 on Windows, Linux, and macOS.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
```

Before submitting a change:

- add or update tests for observable behavior;
- keep hardware I/O bounded and fail closed;
- preserve exact raw bytes in structured results or audit trails;
- update the applicable API/status/research documentation;
- run `bash tools/verify_archive.sh` if archive content changed.

## Documentation boundaries

- `docs/api/` describes the presentation-neutral Python API.
- `docs/cli/` describes the human-facing command-line client.
- future GUI and Home Assistant documentation should remain separate clients.
- `docs/reverse-engineering/` records interpreted technical evidence.
- `research/live/` contains raw physical evidence and local session notes.

When a conclusion is uncertain, retain the raw value and state the evidence
level instead of assigning a convenient meaning.
