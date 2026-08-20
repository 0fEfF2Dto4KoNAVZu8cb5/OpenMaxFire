#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CHUNKS="$ROOT/firmware/archives/chunks"
OUT="$ROOT/firmware/archives/restored"
mkdir -p "$OUT"

restore_b64_chunks() {
  local prefix="$1"
  local output="$2"
  local tmp
  tmp="$(mktemp)"
  cat "$CHUNKS/${prefix}.part-"* | tr -d '\r\n' > "$tmp"
  base64 -d "$tmp" > "$output"
  rm -f "$tmp"
}

restore_b64_chunks \
  "bixby_hex_analysis_20260820_133700.tar.gz.b64" \
  "$OUT/bixby_hex_analysis_20260820_133700.tar.gz"

restore_b64_chunks \
  "Bixby_0271_080315_DISASSEMBLED.tar.gz.b64" \
  "$OUT/Bixby_0271_080315_DISASSEMBLED.tar.gz"

restore_b64_chunks \
  "Bixby_0271_080315_annotated.asm.gz.b64" \
  "$OUT/Bixby_0271_080315_annotated.asm.gz"

gzip -dc "$OUT/Bixby_0271_080315_annotated.asm.gz" \
  > "$OUT/Bixby_0271_080315_annotated.asm"

cat > "$OUT/SHA256SUMS.expected" <<'EOF'
ad62f89980abeacef987648b5cc8ef17d8e0f8f741850fe03d61a7daad1a80b1  bixby_hex_analysis_20260820_133700.tar.gz
98fbbb0246c36177a298a1a745646fe9b6e23ab34c6ad77fb85f458d870b262f  Bixby_0271_080315_DISASSEMBLED.tar.gz
16d544f6f43ac9ee10fce070a126c3f86a97dfb0600cb13a798e91571a1cb028  Bixby_0271_080315_annotated.asm
EOF

(
  cd "$OUT"
  sha256sum -c SHA256SUMS.expected
)

echo "Restored archives are in: $OUT"
