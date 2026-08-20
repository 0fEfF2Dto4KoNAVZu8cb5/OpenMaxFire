#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 INPUT.hex [OUTPUT_DIR]" >&2
}

if [[ $# -lt 1 || $# -gt 2 ]]; then
  usage
  exit 2
fi

input_hex=$1
output_dir=${2:-bixby-hex-analysis}

if [[ ! -f "$input_hex" ]]; then
  echo "Input file not found: $input_hex" >&2
  exit 2
fi

for tool in gpdasm objcopy sha256sum file rg sed; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "Missing $tool. On Debian install: gputils binutils coreutils file ripgrep sed" >&2
    exit 3
  fi
done

mkdir -p "$output_dir"
clean_hex="$output_dir/$(basename "${input_hex%.hex}")_clean.hex"
disassembly="$output_dir/$(basename "${input_hex%.hex}")_disassembly.asm"
binary="$output_dir/firmware.bin"

# gpdasm accepts the Intel HEX records but not the trailing processor comment
# present in the recovered image.
sed '/^;/d' "$input_hex" > "$clean_hex"

gpdasm -p 16f877a "$clean_hex" > "$disassembly"
objcopy -I ihex -O binary "$clean_hex" "$binary"

{
  file "$input_hex" "$clean_hex" "$disassembly" "$binary"
  sha256sum "$input_hex" "$clean_hex" "$disassembly" "$binary"
} > "$output_dir/file-info-and-sha256.txt"

{
  echo "Input: $input_hex"
  echo "Processor: PIC16F877A"
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "Protocol anchors:"
  rg -n "3c43|3c57|3c52|300a" "$disassembly" || true
} > "$output_dir/analysis-summary.txt"

echo "Analysis written to $output_dir"
