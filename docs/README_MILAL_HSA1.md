# HSA1 usage

Human authority: [registry](HUMAN_STRUCTURAL_ADJUDICATION.md) and
[CSV](HUMAN_STRUCTURAL_ADJUDICATION.csv). Contract: [HSA1_SPEC.md](HSA1_SPEC.md).
This command audits accepted artifacts; it does not run new analysis or write
human judgments. Inputs are the exact local ZIP paths pinned in
`config/hsa1_job.json`. No direct BHSA path is required: the accepted R4.2 native
snapshot carries the evidence. Missing or mismatched inputs stop execution.

From the repository root in PowerShell:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_hsa1_registry.py
if ($LASTEXITCODE -ne 0) { throw 'HSA1 tests failed' }
& .\.venv\Scripts\python.exe -B -X utf8 src/milal_hsa1_registry.py --self-test --out "results/hsa1_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic audit failed' }
Write-Host "Inspect results/hsa1_synthetic_$stamp/06_structural_adjudication_report.md and 08_human_registry.md before a real audit."
```

After synthetic inspection, the authorized accepted-source audit and independent
rerun can be executed together:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$outA = "results/hsa1_structural_adjudication_${stamp}_a"
$outB = "results/hsa1_structural_adjudication_${stamp}_b"
foreach ($out in @($outA, $outB)) {
    & .\.venv\Scripts\python.exe -B -X utf8 src/milal_hsa1_registry.py --out $out
    if ($LASTEXITCODE -ne 0) { throw "HSA1 failed: $out" }
}
$hashA = (Get-FileHash -Algorithm SHA256 "${outA}_results.zip").Hash
$hashB = (Get-FileHash -Algorithm SHA256 "${outB}_results.zip").Hash
if ($hashA -ne $hashB) { throw 'Independent ZIP rerun differs' }
Write-Host "HSA1 deterministic PASS: $hashA"
Write-Host "Report: $outA/06_structural_adjudication_report.md"
Write-Host "ZIP: ${outA}_results.zip"
Write-Host "Log: ${outA}_run.log"
```

The exact source links and complete native/formal context are in
`02_judgment_source_links.csv`. Relations in `03_hierarchy_relation_pairs.csv` are
direct human assertions, not generated hierarchy. A clean gate result is a
technical integrity check, not new scholarly acceptance or authorization for R4.3.
