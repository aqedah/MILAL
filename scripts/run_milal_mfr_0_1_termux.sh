#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python_bin="${MFR_PYTHON:-python}"
bhsa="$HOME/text-fabric-data/github/ETCBC/bhsa/tf/2021"
out="results/mfr01_termux_$(date +%Y%m%d_%H%M%S)"
receipt=""
self_test=false
while (($#)); do
  case "$1" in
    --bhsa) bhsa="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    --regression-receipt) receipt="$2"; shift 2;;
    --self-test) self_test=true; shift;;
    *) echo "Unknown option: $1" >&2; exit 2;;
  esac
done
"$python_bin" -B -X utf8 -m unittest discover -s tests -p test_mfr_0_1.py
if "$self_test"; then
  "$python_bin" -B -X utf8 src/milal_mfr_pipeline.py --self-test --out "$out"
else
  test -f "$bhsa/otype.tf" && test -f "$bhsa/oslots.tf" && test -f "$bhsa/otext.tf"
  "$python_bin" -B -X utf8 src/milal_mfr_pipeline.py --self-test --out "${out}_synthetic"
  if [[ -z "$receipt" ]]; then
    receipt="${out}_regression.json"
    "$python_bin" -B -X utf8 src/milal_mfr_pipeline.py --regression-only "$receipt"
  fi
  "$python_bin" -B -X utf8 src/milal_mfr_pipeline.py --bhsa "$bhsa" --out "$out" --regression-receipt "$receipt"
fi
