#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 firmware.hex" >&2
  exit 2
fi

HEX=$1
BASE=$(basename "$HEX")
BASE=${BASE%.*}
CLEAN="${BASE}_clean.hex"

grep '^:' "$HEX" > "$CLEAN"

gpdasm -p p16f877a -n -o -c "$CLEAN" > "${BASE}_disassembly.asm"
gpdasm -p p16f877a -s -n -o -c "$CLEAN" > "${BASE}_reassemblable.asm"
gpdasm -p p16f877a -m "$CLEAN" > "${BASE}_memory_dump.txt"
gpdasm -p p16f877a -i "$CLEAN" > "${BASE}_hex_info.txt"

echo "Generated ${BASE}_disassembly.asm and related files"
