# Running MFR.0.1a

Only the pinned frozen MFR.0.1 result ZIP is required; this stage does not reload
BHSA. Fresh output paths are mandatory. The runners validate stage tests and a
synthetic packet, run the full regression (or use a supplied completed same-code
receipt), then consolidate all five scopes. Logs are UTF-8 under `<out>_work`.
The Python modules use the `milal_mfr01a_` namespace to keep frozen MFR.0.1 discovery
and its module inventory unchanged.

```powershell
$ErrorActionPreference = 'Stop'
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_1a_windows.ps1 -Out .\results\mfr01a_windows_new_a
if ($LASTEXITCODE -ne 0) { throw 'First execution failed' }
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_1a_windows.ps1 -Out .\results\mfr01a_windows_new_b -RegressionReceipt .\results\mfr01a_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'Independent execution failed' }
& .\.venv\Scripts\python.exe -B -X utf8 .\src\milal_mfr01a_verify.py .\results\mfr01a_windows_new_a_results.zip .\results\mfr01a_windows_new_b_results.zip .\results\mfr01a_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'Release verification failed' }
```

Use `-InputZip <path>` to locate the same pinned ZIP elsewhere; its required hash
does not change. `-SelfTest` produces only a synthetic package.

```bash
cd ~/MILAL
git pull --ff-only
bash scripts/run_milal_mfr_0_1a_termux.sh --out results/mfr01a_termux_new_a
bash scripts/run_milal_mfr_0_1a_termux.sh --out results/mfr01a_termux_new_b \
  --regression-receipt results/mfr01a_termux_new_a_regression.json
python -B -X utf8 src/milal_mfr01a_verify.py \
  results/mfr01a_termux_new_a_results.zip results/mfr01a_termux_new_b_results.zip \
  results/mfr01a_termux_new_a_regression.json
```

Termux uses the same schema; no empirical Termux success is claimed without a run.
Required upload: the complete final result ZIP. It includes original frozen input,
all corpus consolidation tables, review/archive crosswalks and Job marker pages.
Optional: validation report and human packet. Extract the ZIP before following
relative packet links. Results, source ZIPs and logs remain untracked local data.
