# Running MFR.0.1b

Use the exact pinned MFR.0.1a ZIP. Its embedded MFR.0.1 ZIP is verified separately.
No BHSA reload is needed. The new release embeds the complete unchanged prior ZIP.
Job receives full relation auditing; external scopes receive role overlays and
frozen control checks. Fresh output paths are required.

The runner checks stage tests and a synthetic package, then runs full regression
before real execution. Run A and B sequentially to avoid competing temporary-space
peaks. A supplied regression receipt must come from the same unchanged source.

```powershell
$ErrorActionPreference = 'Stop'
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_1b_windows.ps1 -Out .\results\mfr01b_windows_new_a
if ($LASTEXITCODE -ne 0) { throw 'A execution failed' }
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_1b_windows.ps1 -Out .\results\mfr01b_windows_new_b -RegressionReceipt .\results\mfr01b_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'B execution failed' }
& .\.venv\Scripts\python.exe -B -X utf8 .\src\milal_mfr01b_verify.py .\results\mfr01b_windows_new_a_results.zip .\results\mfr01b_windows_new_b_results.zip .\results\mfr01b_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'Independent release verification failed' }
```

`-InputZip <path>` relocates the same pinned input; its hash remains mandatory.
`-SelfTest` runs stage tests and synthetic execution only.

```bash
cd ~/MILAL
git pull --ff-only
bash scripts/run_milal_mfr_0_1b_termux.sh --out results/mfr01b_termux_new_a
bash scripts/run_milal_mfr_0_1b_termux.sh --out results/mfr01b_termux_new_b \
  --regression-receipt results/mfr01b_termux_new_a_regression.json
python -B -X utf8 src/milal_mfr01b_verify.py \
  results/mfr01b_termux_new_a_results.zip results/mfr01b_termux_new_b_results.zip \
  results/mfr01b_termux_new_a_regression.json
```

Termux syntax support is not empirical cross-platform validation. Upload the complete
result ZIP for review; optionally include the validation report and H1 packet.
Extract the ZIP before opening relative case-evidence links. Generated artifacts,
inputs, logs and temporary work directories stay outside Git.
