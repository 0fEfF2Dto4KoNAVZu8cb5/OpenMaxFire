# Preservation archive

`original/` contains recovered Bixby vendor files, an owner-supplied original-
controller firmware read, user-supplied photographs, and an online-found
motherboard diagram without modifying their bytes. Renaming
an artifact for clarity does not change its contents; the provenance manifest
records earlier upload names, duplicate hashes, and evidence limits.

OpenMaxFire's MIT License does not apply to these vendor artifacts or photographs. They are retained for research, interoperability, appliance maintenance, and historical preservation. Review rights and privacy before making the repository public or mirroring it elsewhere.

`project-snapshots/` preserves earlier OpenMaxFire-generated bundles. Reverse-engineering outputs live outside `original/` so originals and derived work cannot be confused.

Live controller traffic and device-generated EEPROM artifacts are preserved
under `../research/live/` rather than `original/`; each session directory has
its own checksums and interpretation boundary.

## Integrity

- `SHA256SUMS.txt` covers every file in `preservation/` and `reverse-engineering/`.
- `MANIFEST.md` records provenance, relationships, versions, and important notes.
- Original files should never be edited in place. Add a derived copy under `reverse-engineering/` instead.
- Archive.org identifiers and URLs for the preserved factory releases are recorded in `MANIFEST.md`; the newly recovered owner-controller read is preserved on GitHub while an external mirror remains pending.

All retained originals catalogued with repository paths in `MANIFEST.md` are
present in normal binary form. No split, encoded, or reconstructed copies are
used. The separately listed 78.7 MB supplied video is hash-catalogued but
pending external archival and is not committed to Git.
