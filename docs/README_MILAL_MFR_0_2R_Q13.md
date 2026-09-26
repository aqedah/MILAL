# Running MFR.0.2R-Q1.3

Read [the specification](MFR_0_2R_Q13_SPEC.md) and current HANDOFF first.
The runner consumes the frozen Q1.2 release and never loads BHSA or performs
source binding again. Its input archive must be at `<extracted-directory>_results.zip`.
All output paths must be new; existing historical runs are not overwritten.

The following PowerShell block runs synthetic validation, full regression,
two independent real executions and release verification. Choose fresh output
names if these directories already exist. Paths are runner arguments, not
analytical defaults. D:/F: locations below are this computer's local artifacts.

```powershell
$repo = 'C:\MILAL'
$python = Join-Path $repo '.venv\Scripts\python.exe'
$q12 = 'D:\MILAL_runs\mfr02r_q12_20260926\release_a'
$runA = 'D:\MILAL_runs\mfr02r_q13_reproduce\release_a'
$runB = 'F:\MILAL_runs\mfr02r_q13_reproduce\release_b'
$validationRoot = Split-Path $runA
$synthetic = Join-Path $validationRoot 'synthetic'
$regression = Join-Path $validationRoot 'regression.json'
$runner = Join-Path $repo 'src\milal_q13_runner.py'
Set-Location $repo
New-Item -ItemType Directory -Path (Join-Path $validationRoot 'temp') -Force | Out-Null
$env:TEMP = Join-Path $validationRoot 'temp'
$env:TMP = $env:TEMP
& $python -B -X utf8 -m unittest discover -s tests -p test_milal_q13.py
if ($LASTEXITCODE -ne 0) { throw 'Focused tests failed' }
& $python -B -X utf8 $runner --self-test --out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
Get-Content (Join-Path $synthetic 'a\14_q13_method_report.md')
& $python -B -X utf8 (Join-Path $repo 'src\milal_mfr02r_pipeline.py') --regression-only $regression
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
foreach ($destination in @($runA, $runB)) {
    & $python -B -X utf8 $runner --q12 $q12 --out $destination --regression $regression --synthetic (Join-Path $synthetic 'receipt.json')
    if ($LASTEXITCODE -ne 0) { throw "Q1.3 run failed: $destination" }
}
& $python -B -X utf8 $runner --release $runA $runB
if ($LASTEXITCODE -ne 0) { throw 'Independent release verification failed' }
Get-Content (Join-Path $runA '13_q13_assignment_statistics.json')
Get-Content (Join-Path $runA '16_q13_gates.csv')
Write-Host "Report: $runA\14_q13_method_report.md"
Write-Host "Verification: ${runA}_verification.json"
```

An initial run has `DETERMINISTIC_RERUN` pending. Only `--release` after matching
independent output manifests can change it to PASSED and mark the package
`VALIDATED_NOT_HUMAN_ACCEPTED`. Review `11_q13_q12_seven_pivot_reaudit.csv` and
`12_q13_job_2_1_diagnostic.md` alongside the method report. Q1.4 is not executed.
