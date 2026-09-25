# Running MFR.0.2A

Inputs are the exact pinned MFR.0.1b result ZIP and the historical JIN.0.8 ZIP
specified in `config/mfr_0_2a_historical_comparison.json`. The latter is read only
after the human decisions freeze. No BHSA reload or new discovery is performed.
The researcher decision registry is a separate, hash-pinned new phase.

Use fresh output directories. Existing freezes and completed results are never
overwritten. A/B runs must use the same code, supplied decisions and configuration.
The full result ZIP includes the complete unchanged MFR.0.1b input ZIP.

```powershell
$ErrorActionPreference = 'Stop'
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_2a_windows.ps1 -Out .\results\mfr02a_windows_new_a
if ($LASTEXITCODE -ne 0) { throw 'A failed' }
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_2a_windows.ps1 -Out .\results\mfr02a_windows_new_b -RegressionReceipt .\results\mfr02a_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'B failed' }
& .\.venv\Scripts\python.exe -B -X utf8 .\src\milal_mfr02a_verify.py .\results\mfr02a_windows_new_a_results.zip .\results\mfr02a_windows_new_b_results.zip .\results\mfr02a_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'Independent verification failed' }
```

`-SelfTest` runs stage tests and synthetic serialization only. `-InputZip` relocates
the same pinned MFR.0.1b input. The final verifier rejects a regression receipt from
different source code. An interrupted preliminary regression is not a valid receipt.

```bash
cd ~/MILAL
bash scripts/run_milal_mfr_0_2a_termux.sh --out results/mfr02a_termux_new_a
bash scripts/run_milal_mfr_0_2a_termux.sh --out results/mfr02a_termux_new_b \
  --regression-receipt results/mfr02a_termux_new_a_regression.json
python -B -X utf8 src/milal_mfr02a_verify.py \
  results/mfr02a_termux_new_a_results.zip results/mfr02a_termux_new_b_results.zip \
  results/mfr02a_termux_new_a_regression.json
```

The Python pipeline supports `--freeze-only`, then `--complete-frozen --out <same>`
for auditable two-phase execution. Completion requires an intact prior freeze and
refuses an already completed result. `--historical-config` is an advanced completion
input whose hash is recorded. Release verification uses the repository's pinned
historical configuration, so release runs must use that configuration.

The 35 in-package gates concern the phase's actual outputs. Four independent
release gates verify full regression, zero skips, manifests and A/B ZIP equality;
their receipt lives beside the result ZIP to avoid a self-hash dependency.

Upload the complete result ZIP and its independent verification receipt. Optional:
the tracked validation report. Only MFR.0.2B human resumption adjudication is next;
the future B/C scope CSVs have blank decisions and do not authorize tree assembly.
Termux runner syntax support is not empirical cross-platform validation.
