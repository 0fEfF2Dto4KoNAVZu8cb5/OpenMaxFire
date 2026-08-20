# Preservation archive

`original/` contains recovered Bixby vendor files and user-supplied photographs without modifying their bytes. Renaming a photograph for clarity does not change its contents; the provenance manifest records its earlier upload name.

OpenMaxFire's MIT License does not apply to these vendor artifacts or photographs. They are retained for research, interoperability, appliance maintenance, and historical preservation. Review rights and privacy before making the repository public or mirroring it elsewhere.

`project-snapshots/` preserves earlier OpenMaxFire-generated bundles. Reverse-engineering outputs live outside `original/` so originals and derived work cannot be confused.

## Integrity

- `SHA256SUMS.txt` covers every file in `preservation/` and `reverse-engineering/`.
- `MANIFEST.md` records provenance, relationships, versions, and important notes.
- Original files should never be edited in place. Add a derived copy under `reverse-engineering/` instead.
- Future Archive.org identifiers/URLs belong in the manifest; none has been assigned yet.

Five larger originals are awaiting direct GitHub upload. See [PENDING_UPLOADS.md](PENDING_UPLOADS.md). No split, encoded, or reconstructed copies are used.
