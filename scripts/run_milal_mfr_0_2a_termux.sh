#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
out="results/mfr02a_termux_$(date +%Y%m%d_%H%M%S)"
input=""; receipt=""; self_test=false
while (($#)); do
  case "$1" in
    --out) out="$2"; shift 2 ;;
    --input) input="$2"; shift 2 ;;
    --regression-receipt) receipt="$2"; shift 2 ;;
    --self-test) self_test=true; shift ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done
python -B -X utf8 -m unittest discover -s tests -p test_mfr_0_2a.py
if "$self_test"; then
  python -B -X utf8 src/milal_mfr02a_pipeline.py --self-test --out "$out"
  exit
fi
python -B -X utf8 src/milal_mfr02a_pipeline.py --self-test --out "${out}_synthetic"
if [[ -z "$receipt" ]]; then
  receipt="${out}_regression.json"
  python -B -X utf8 src/milal_mfr02a_pipeline.py --regression-only "$receipt"
fi
python -B -c 'import json,sys;r=json.load(open(sys.argv[1]));assert r["tests_run"]>=2152 and r["failures"]==r["errors"]==r["skipped"]==0' "$receipt"
args=(--out "$out")
if [[ -n "$input" ]]; then args+=(--input "$input"); fi
python -B -X utf8 src/milal_mfr02a_pipeline.py "${args[@]}"
