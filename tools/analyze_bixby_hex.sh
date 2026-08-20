#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 || $# -gt 2 ]]; then
  echo "Usage: $0 INPUT.hex [OUTPUT_DIR]" >&2
  exit 2
fi

script_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
input_hex=$1
output_dir=${2:-bixby-hex-analysis}

exec python3 "$script_dir/firmware_pipeline.py" analyze "$input_hex" "$output_dir"
