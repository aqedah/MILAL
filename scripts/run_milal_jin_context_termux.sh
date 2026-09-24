#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${PYTHON:-python}" -B -X utf8 "$repo/src/milal_jin_context_pipeline.py" \
  --config "$repo/config/r4_4_contract_jin_0_3_job.json" "$@"
