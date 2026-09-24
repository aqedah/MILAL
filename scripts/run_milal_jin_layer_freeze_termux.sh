#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec "${PYTHON:-python}" -B -X utf8 "$repo_root/src/milal_jin_layer_freeze.py" "$@"
