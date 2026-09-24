#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python_bin="${PYTHON:-python}"
exec "$python_bin" -B -X utf8 "$repo/src/milal_jin_audit_pipeline.py" \
  --config "$repo/config/r4_4_contract_jin_0_2_job.json" "$@"
