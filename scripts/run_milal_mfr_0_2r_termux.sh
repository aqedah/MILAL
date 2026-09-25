#!/usr/bin/env bash
set -euo pipefail
repo="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
tf_path="${1:?Usage: runner TF_PATH NEW_RUN_ROOT [PYTHON]}"
run_root="${2:?A new output directory is required}"
python_bin="${3:-python}"
test ! -e "$run_root" || { echo 'Existing output is preserved; select a new run directory.' >&2; exit 1; }
mkdir -p -- "$run_root"
entry="$repo/src/milal_mfr02r_pipeline.py"
"$python_bin" -B "$entry" --self-test --out "$run_root/synthetic"
"$python_bin" -B "$entry" --regression-only "$run_root/regression.json"
"$python_bin" -B "$entry" --prepare --tf-path "$tf_path" --projection "$run_root/projection"
for label in a b; do
  "$python_bin" -B "$entry" --out "$run_root/$label" --projection "$run_root/projection" --regression-receipt "$run_root/regression.json"
done
"$python_bin" -B "$entry" --release "$run_root/a" "$run_root/b"
printf 'Verified results: %s\n' "$run_root/a_results.zip"
