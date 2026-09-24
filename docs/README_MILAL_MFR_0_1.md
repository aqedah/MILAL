# Running MFR.0.1

Use the pinned JIN.0.9 release ZIP and external raw BHSA 2021. Never commit inputs,
outputs, ZIPs, logs or TF data. Choose new output names; existing paths are rejected.
The runner verifies baseline ancestry and frozen hashes, runs MFR tests/synthetic,
then full regression unless a completed same-workspace receipt is explicitly supplied.
All five real scopes run before controls and history are loaded. UTF-8 child logs
are kept at `<out>_work/runner_utf8.log`; the final SHA256 is printed.

```powershell
$ErrorActionPreference = 'Stop'
$tfData = Join-Path $HOME 'text-fabric-data\github\etcbc\bhsa\tf\2021'
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_1_windows.ps1 -Bhsa $tfData -Out .\results\mfr01_windows_new_a
if ($LASTEXITCODE -ne 0) { throw 'MFR failed' }
& powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_mfr_0_1_windows.ps1 -Bhsa $tfData -Out .\results\mfr01_windows_new_b -RegressionReceipt .\results\mfr01_windows_new_a_regression.json
if ($LASTEXITCODE -ne 0) { throw 'Independent rerun failed' }
Get-FileHash .\results\mfr01_windows_new_a_results.zip, .\results\mfr01_windows_new_b_results.zip -Algorithm SHA256
```

Termux, after obtaining the same pinned historical ZIP and checking the case-sensitive
BHSA directory:

```bash
cd ~/MILAL
git pull --ff-only
bash scripts/run_milal_mfr_0_1_termux.sh \
  --bhsa "$HOME/text-fabric-data/github/ETCBC/bhsa/tf/2021" \
  --out results/mfr01_termux_new_a
sha256sum results/mfr01_termux_new_a_results.zip
```

Use `--self-test` (PowerShell `-SelfTest`) for a synthetic package only. Termux and
Windows use the same schema and deterministic ZIP writer. No empirical Termux
success is claimed without its results. Required upload: the complete final results
ZIP. Optional additional review material: validation report, human packet and selected
CSVs. The ZIP already contains all generated evidence and comparisons.
