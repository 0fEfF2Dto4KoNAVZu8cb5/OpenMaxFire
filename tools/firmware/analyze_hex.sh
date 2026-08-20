#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 firmware.hex" >&2
  exit 2
fi

HEX=$1
BASE=$(basename "$HEX")
BASE=${BASE%.*}
OUT="${BASE}_analysis"
mkdir -p "$OUT"

command -v srec_info >/dev/null || { echo "Install srecord" >&2; exit 1; }
command -v objcopy >/dev/null || { echo "Install binutils" >&2; exit 1; }

sha256sum "$HEX" > "$OUT/sha256.txt"
file "$HEX" > "$OUT/file.txt"
srec_info "$HEX" -Intel > "$OUT/address_map.txt" 2>&1 || true
srec_cat "$HEX" -Intel -o - -HEX_Dump > "$OUT/addressed_hex_dump.txt" 2>&1 || true
objcopy -I ihex -O binary "$HEX" "$OUT/firmware.bin"
strings -a -n 3 -t x "$OUT/firmware.bin" > "$OUT/all_strings.txt"

echo "Analysis written to $OUT"
