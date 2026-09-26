# Running Q1.5 reference visibility qualification

Read [the contract](MFR_0_2R_Q15_SPEC.md) and HANDOFF first. Q1.5 consumes exact
frozen archives and extracted directories; no BHSA reload or upstream analytical
rerun is needed. Keep each archive at `<extracted-directory>_results.zip`.
Result paths below must be new. Generated outputs remain local-only.

```powershell
$repo = 'C:\MILAL'
$py = Join-Path $repo '.venv\Scripts\python.exe'
$runner = Join-Path $repo 'src\milal_q15_runner.py'
$source = 'D:\MILAL_runs\mfr02r_20260925\release_a'
$q11 = 'D:\MILAL_runs\mfr02r_q1_1_20260926\release_a_final'
$q12 = 'D:\MILAL_runs\mfr02r_q12_20260926\release_a'
$q14 = 'D:\MILAL_runs\mfr02r_q14_20260926\release_a'
$work = 'D:\MILAL_runs\mfr02r_q15_reproduce'
$a = Join-Path $work 'release_a'
$b = 'F:\MILAL_runs\mfr02r_q15_reproduce\release_b'
$synthetic = Join-Path $work 'synthetic'
$regression = Join-Path $work 'regression.json'
Set-Location $repo
New-Item -ItemType Directory -Path (Join-Path $work 'temp') -Force | Out-Null
$env:TEMP = Join-Path $work 'temp'
$env:TMP = $env:TEMP
& $py -B -X utf8 -m unittest discover -s tests -p test_milal_q15.py
if ($LASTEXITCODE -ne 0) { throw 'Focused validation failed' }
& $py -B -X utf8 $runner --self-test --out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
Get-Content (Join-Path $synthetic 'review.md')
& $py -B -X utf8 (Join-Path $repo 'src\milal_mfr02r_pipeline.py') --regression-only $regression
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
foreach ($destination in @($a, $b)) {
    & $py -B -X utf8 $runner --source $source --q11 $q11 --q12 $q12 --q14 $q14 --out $destination --synthetic (Join-Path $synthetic 'receipt.json') --regression $regression
    if ($LASTEXITCODE -ne 0) { throw "Q1.5 execution failed: $destination" }
}
& $py -B -X utf8 $runner --release $a $b
if ($LASTEXITCODE -ne 0) { throw 'Release verification failed' }
Get-Content (Join-Path $a '25_q15_gates.csv')
Write-Host "Report: $a\23_q15_method_report.md"
Write-Host "RESULT ZIP A: ${a}_results.zip"
Write-Host "RESULT ZIP B: ${b}_results.zip"
Get-Content "${a}_verification.json"
```

Omitting `--regression` permits a preliminary diagnostic run after current
synthetic validation, but FULL_REGRESSION_PASS remains pending and release is
blocked. A new fingerprint requires rerunning validation. Do not use an earlier
draft's counts or ZIP as the final release. Do not change source/config/tests
during full regression.

`--release` requires distinct A/B directories with matching manifests. It checks
a provisional archive before sealing the CRC gate, then independently verifies
both actual final archives and records their exact paths, hashes, existence,
member manifests and CRCs in the external verification JSON. A valid exit alone
is not human acceptance. Q1.6 is not executed automatically.
