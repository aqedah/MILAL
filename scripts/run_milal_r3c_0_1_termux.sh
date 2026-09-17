#!/data/data/com.termux/files/usr/bin/bash
set -u

PROGRAM="MILAL"
VERSION="R3c.0.1"

DOWNLOADS="$HOME/storage/downloads"
R3B2_ZIP="${1:-$DOWNLOADS/job_r3b_2_results.zip}"
R3B3_ZIP="${2:-$DOWNLOADS/job_r3b_3_results.zip}"
TF_DIR="${3:-$HOME/text-fabric-data/github/ETCBC/bhsa/tf/2021}"
OUTPUT_DIR="${4:-$HOME/milal_r3c_0_1_output}"
RESULT_ZIP="${5:-$DOWNLOADS/milal_r3c_0_1_results.zip}"
RUN_LOG="$DOWNLOADS/milal_r3c_0_1_run.log"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$SCRIPT_DIR/milal_r3c_0_1_reviewability.py"

rm -rf "$OUTPUT_DIR"
rm -f "$RESULT_ZIP"

{
  echo "========================================"
  echo "$PROGRAM $VERSION"
  echo "SCRIPT=$SCRIPT"
  echo "R3B2_ZIP=$R3B2_ZIP"
  echo "R3B3_ZIP=$R3B3_ZIP"
  echo "TF_DIR=$TF_DIR"
  echo "OUTPUT_DIR=$OUTPUT_DIR"
  echo "RESULT_ZIP=$RESULT_ZIP"
  echo "START=$(date -Iseconds 2>/dev/null || date)"
  echo "========================================"

  STATUS=0

  if [ ! -f "$SCRIPT" ]; then
    echo "ERROR: MILAL R3c.0.1 script not found: $SCRIPT"
    STATUS=2
  elif [ ! -f "$R3B2_ZIP" ]; then
    echo "ERROR: R3b.2 results ZIP not found: $R3B2_ZIP"
    STATUS=2
  elif [ ! -f "$R3B3_ZIP" ]; then
    echo "ERROR: R3b.3 results ZIP not found: $R3B3_ZIP"
    STATUS=2
  elif [ ! -d "$TF_DIR" ]; then
    echo "ERROR: BHSA Text-Fabric directory not found: $TF_DIR"
    STATUS=2
  elif [ ! -f "$TF_DIR/otype.tf" ] || [ ! -f "$TF_DIR/oslots.tf" ]; then
    echo "ERROR: TF_DIR is not the BHSA tf/2021 directory: $TF_DIR"
    STATUS=2
  else
    python "$SCRIPT" \
      --r3b2-zip "$R3B2_ZIP" \
      --r3b3-zip "$R3B3_ZIP" \
      --tf-dir "$TF_DIR" \
      --output-dir "$OUTPUT_DIR"
    STATUS=$?
  fi

  mkdir -p "$OUTPUT_DIR"
  echo "$STATUS" > "$OUTPUT_DIR/TERMUX_EXIT_STATUS.txt"

  (
    cd "$(dirname "$OUTPUT_DIR")" &&
    rm -f "$RESULT_ZIP" &&
    zip -qr "$RESULT_ZIP" "$(basename "$OUTPUT_DIR")"
  )
  ZIP_STATUS=$?

  echo "========================================"
  echo "PIPELINE STATUS: $STATUS"
  echo "ZIP STATUS: $ZIP_STATUS"
  echo "RESULT:"
  ls -lh "$RESULT_ZIP" 2>/dev/null || true
  echo "RUN LOG:"
  echo "$RUN_LOG"
  echo "END=$(date -Iseconds 2>/dev/null || date)"
  echo "========================================"

  if [ "$ZIP_STATUS" -ne 0 ]; then
    exit "$ZIP_STATUS"
  fi
  exit "$STATUS"
} 2>&1 | tee "$RUN_LOG"

exit "${PIPESTATUS[0]}"
