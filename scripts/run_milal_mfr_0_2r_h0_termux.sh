#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
source_dir="$1"
archive="$2"
run_root="$3"
python_bin="${PYTHON:-python}"
test ! -e "$run_root"
mkdir -p "$run_root"
"$python_bin" -B "$repo/src/milal_h0_runner.py" --self-test --out "$run_root/synthetic"
"$python_bin" -B "$repo/src/milal_mfr02r_pipeline.py" --regression-only "$run_root/regression.json"
for label in a b; do
  "$python_bin" -B "$repo/src/milal_h0_runner.py" --source "$source_dir" --archive "$archive" --out "$run_root/$label" --regression-receipt "$run_root/regression.json"
done
"$python_bin" -B "$repo/src/milal_h0_runner.py" --release "$run_root/a" "$run_root/b"
