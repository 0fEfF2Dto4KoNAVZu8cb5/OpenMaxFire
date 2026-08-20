# Session archives

This directory preserves exact reverse-engineering session artifacts even though the GitHub connector used for the initial import accepts text payloads rather than arbitrary local binary files.

Binary archives are therefore stored as lexically ordered Base64 chunks under `chunks/`. They can be reconstructed byte-for-byte with `tools/firmware/restore_archives.sh`.

## Preserved bundles

| Artifact | SHA-256 |
|---|---|
| `bixby_hex_analysis_20260820_133700.tar.gz` | `ad62f89980abeacef987648b5cc8ef17d8e0f8f741850fe03d61a7daad1a80b1` |
| `Bixby_0271_080315_DISASSEMBLED.tar.gz` | `98fbbb0246c36177a298a1a745646fe9b6e23ab34c6ad77fb85f458d870b262f` |
| restored `Bixby_0271_080315_annotated.asm` | `16d544f6f43ac9ee10fce070a126c3f86a97dfb0600cb13a798e91571a1cb028` |

The first archive contains the untouched Intel HEX plus the initial address-aware analysis outputs. The second contains the generated PIC16F877A disassembly, reassemblable listing, memory dump, HEX information, and cleaned HEX input. The annotated ASM is preserved separately because it contains the OpenMaxFire reverse-engineering annotations added after disassembly.

These chunks are an archival transport format, not the preferred human-browsing format. Important findings are separately documented under `docs/`, `protocol/`, and `firmware/analysis/`.
