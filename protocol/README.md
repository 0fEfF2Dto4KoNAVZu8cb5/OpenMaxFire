# Machine-readable protocol evidence

This directory contains static evidence maps intended for analysis and
cross-checking. The authoritative executable behavior is the versioned Python
API under `src/openmaxfire/`; applications should use that API instead of
parsing these files directly.

| File | Scope |
| --- | --- |
| [`registers.yaml`](registers.yaml) | Cross-version serial framing and controller-register evidence, with explicit live/static confidence |

Human-readable protocol references live under [`docs/protocol/`](../docs/protocol/).
Unknown meanings remain unknown, and later-format semantics are not applied to
the live 2.02/format-04 controller without supporting evidence.
