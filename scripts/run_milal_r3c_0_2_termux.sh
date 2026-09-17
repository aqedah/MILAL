#!/data/data/com.termux/files/usr/bin/bash
# Keep the repository's src/, scripts/ and config/ directories together.
set -u
set -o pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || exit 2
REPO_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)" || exit 2
SCRIPT="$REPO_DIR/src/milal_r3c_0_2_reviewability.py"
DOWNLOADS="$HOME/storage/downloads"
STAMP="$(date +%Y%m%d_%H%M%S)_$$"
R3B2_ZIP="${1:-$DOWNLOADS/job_r3b_2_results.zip}"
R3B3_ZIP="${2:-$DOWNLOADS/job_r3b_3_results.zip}"
TF_DIR="${3:-$HOME/text-fabric-data/github/ETCBC/bhsa/tf/2021}"
OUTPUT_DIR="${4:-$HOME/milal_r3c_0_2_$STAMP}"
RESULT_ZIP="${5:-$DOWNLOADS/milal_r3c_0_2_${STAMP}_results.zip}"
PILOT_CONFIG="${6:-$REPO_DIR/config/r3c_0_2_job_pilot.json}"
SEED="${7:-20260917}"
RUN_LOG="$DOWNLOADS/milal_r3c_0_2_${STAMP}_run.log"

# Never delete an earlier run or update an existing ZIP with stale entries.
if [[ -e "$OUTPUT_DIR" || -e "$RESULT_ZIP" ]]; then
  echo "ERROR: choose a new output directory and result ZIP; existing paths are preserved." >&2
  exit 2
fi
if [[ ! -f "$SCRIPT" || ! -f "$PILOT_CONFIG" ]]; then
  echo "ERROR: keep src/, scripts/ and config/ in the repository layout." >&2
  exit 2
fi
mkdir -p -- "$DOWNLOADS" "$(dirname -- "$RESULT_ZIP")" || exit 2

{
  echo "MILAL R3c.0.2; seed=$SEED; output=$OUTPUT_DIR"
  python "$SCRIPT" --r3b2-zip "$R3B2_ZIP" --r3b3-zip "$R3B3_ZIP" \
    --tf-dir "$TF_DIR" --output-dir "$OUTPUT_DIR" --pilot-config "$PILOT_CONFIG" --seed "$SEED"
  STATUS=$?
  # Python writes failure diagnostics and metadata as well as successful results.
  if [[ ! -d "$OUTPUT_DIR" ]]; then
    echo "ERROR: no output directory was produced; pipeline status=$STATUS"
    exit "$STATUS"
  fi
  # Python zipfile avoids zip utility dependencies and creates a fresh archive.
  python -c 'import pathlib,sys,zipfile; root=pathlib.Path(sys.argv[1]); z=zipfile.ZipFile(sys.argv[2], "x", compression=zipfile.ZIP_DEFLATED); [z.write(p, p.relative_to(root.parent)) for p in sorted(root.rglob("*")) if p.is_file()]; z.close()' "$OUTPUT_DIR" "$RESULT_ZIP"
  ZIP_STATUS=$?
  echo "PIPELINE STATUS: $STATUS; ZIP STATUS: $ZIP_STATUS"
  echo "RESULT: $RESULT_ZIP"
  echo "RUN LOG: $RUN_LOG"
  if [[ "$ZIP_STATUS" -ne 0 ]]; then exit "$ZIP_STATUS"; fi
  exit "$STATUS"
} 2>&1 | tee "$RUN_LOG"

exit "${PIPESTATUS[0]}"
