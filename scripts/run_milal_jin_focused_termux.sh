#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${PYTHON:-python}" -B -X utf8 "$repo/src/milal_jin_focused_pipeline.py" "$@"
