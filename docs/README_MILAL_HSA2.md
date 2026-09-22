# HSA2 audit usage

Read [HSA2_SPEC.md](HSA2_SPEC.md) and the new
[human registry](HUMAN_STRUCTURAL_ADJUDICATION_HSA2.md). The auditor consumes the
same seven exact local ZIPs configured for frozen HSA1. It does not overwrite HSA1,
run marker extraction or choose a closure target. Missing/mismatched sources stop.

From the repository root, validate and inspect synthetic output first:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_hsa2_closure_audit.py
if ($LASTEXITCODE -ne 0) { throw 'HSA2 tests failed' }
& .\.venv\Scripts\python.exe -B -X utf8 src/milal_hsa2_closure_audit.py --self-test --out "results/hsa2_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic audit failed' }
Write-Host "Inspect results/hsa2_synthetic_$stamp/04_job_27_31_closure_target_audit.md"
```

After synthetic inspection, run the authorized accepted-artifact audit twice:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$a = "results/hsa2_dialogue_structure_${stamp}_a"
$b = "results/hsa2_dialogue_structure_${stamp}_b"
foreach ($out in @($a,$b)) {
    & .\.venv\Scripts\python.exe -B -X utf8 src/milal_hsa2_closure_audit.py --out $out
    if ($LASTEXITCODE -ne 0) { throw "HSA2 failed: $out" }
}
if ((Get-FileHash "${a}_results.zip").Hash -ne (Get-FileHash "${b}_results.zip").Hash) {
    throw 'Independent ZIP rerun differs'
}
Write-Host "Deterministic PASS; report: $a/04_job_27_31_closure_target_audit.md"
Write-Host "ZIP: ${a}_results.zip"
Write-Host "Log: ${a}_run.log"
```

The review question remains open after a technically successful audit. Candidate
options in 03 remain UNREVIEWED / UNRESOLVED; neither direct target nor enclosing
termination is selected. 12 contains only direct human-authored relations, with no
31:40 closure-target edge. Further researcher adjudication is required before R4.3.
