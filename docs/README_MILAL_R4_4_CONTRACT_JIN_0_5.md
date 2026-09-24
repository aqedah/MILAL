# JIN.0.5 focused audit execution

See [spec](R4_4_CONTRACT_JIN_0_5_SPEC.md) and
[validation report](R4_4_CONTRACT_JIN_0_5_VALIDATION_REPORT.md).
Requires the exact JIN.0.4 ZIP specified in config and external BHSA 2021.
No source artifacts belong in Git. Every output path must be fresh.

Windows PowerShell, from repository root:

```powershell
$ErrorActionPreference = 'Stop'
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_5.py -v
if ($LASTEXITCODE) { throw 'Focused unit tests failed' }
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v
if ($LASTEXITCODE) { throw 'Full regression failed' }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .\scripts\run_milal_jin_focused_windows.ps1 -SelfTest -Out "results\jin05_synthetic_$stamp"
if ($LASTEXITCODE) { throw 'Synthetic failed' }
```

Inspect synthetic 18_focused_relation_review_packet.md and 21_gates.csv before real execution.

```powershell
$ErrorActionPreference = 'Stop'
$tfData = Join-Path $HOME 'text-fabric-data\github\etcbc\bhsa\tf\2021'
foreach ($name in @('otype.tf','oslots.tf','otext.tf')) {
    if (-not (Test-Path -LiteralPath (Join-Path $tfData $name))) { throw "Missing TF file: $name" }
}
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
& .\scripts\run_milal_jin_focused_windows.ps1 -TfData $tfData -Out "results\jin05_real_$stamp"
if ($LASTEXITCODE) { throw 'Real focused audit failed' }
Get-FileHash "results\jin05_real_${stamp}_results.zip" -Algorithm SHA256
```

The coordinator runs A → A freeze → B → B freeze → C → C freeze → postblind comparison.
No partial stage bypass or human-source fallback. Each A/B/C raw read is independently
verified against frozen JIN.0.2 feature values and receipts. Physical source paths are
logged outside deterministic ZIPs. Inspect separate blind/A, blind/B, blind/C manifests
and combined 15 before reviewing human comparison 16. Review fields 17 remain blank.

Termux (actual executable entrypoints; no empirical Termux run claimed):

```bash
cd ~/MILAL
git pull --ff-only &&
python -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_5.py -v &&
python -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v &&
bash scripts/run_milal_jin_focused_termux.sh --self-test --out "results/jin05_synthetic_$(date +%Y%m%d_%H%M%S)"
```

After inspecting synthetic results and recovering the pinned JIN.0.4 ZIP:

```bash
cd ~/MILAL
tf_data="$HOME/text-fabric-data/github/etcbc/bhsa/tf/2021"
test -f "$tf_data/otype.tf" && test -f "$tf_data/oslots.tf" && test -f "$tf_data/otext.tf" || exit 1
run_out="results/jin05_real_$(date +%Y%m%d_%H%M%S)"
bash scripts/run_milal_jin_focused_termux.sh --tf-data "$tf_data" --out "$run_out" &&
sha256sum "${run_out}_results.zip"
```

For independent reproducibility, rerun in a new process with a fresh output path and
compare complete ZIP bytes. Result/log paths are local-only. Readiness is for focused
human adjudication, never for R4.4 consumer implementation.
