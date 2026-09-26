# Reproduce Q1.6 source-binding coverage audit

Read [the specification](MFR_0_2R_Q16_SPEC.md) and HANDOFF. This runner consumes
verified frozen packages; it does not reload BHSA or re-run earlier analytical
stages. Each archive must be adjacent to its extracted directory as
`<directory>_results.zip`. Outputs must use new directories. Intermediate runs
with no full-regression receipt retain pending gates and cannot be released.

```powershell
$repo = 'C:\MILAL'
$py = Join-Path $repo '.venv\Scripts\python.exe'
$runner = Join-Path $repo 'src\milal_q16_runner.py'
$work = 'D:\MILAL_runs\mfr02r_q16_reproduce'
$a = Join-Path $work 'release_a'
$b = 'F:\MILAL_runs\mfr02r_q16_reproduce\release_b'
$synthetic = Join-Path $work 'synthetic.json'
$regression = Join-Path $work 'regression.json'
Set-Location $repo
New-Item -ItemType Directory -Path (Join-Path $work 'temp') -Force | Out-Null
$env:TEMP = Join-Path $work 'temp'
$env:TMP = $env:TEMP
& $py -B -X utf8 -m unittest discover -s tests -p test_milal_q16.py
if ($LASTEXITCODE -ne 0) { throw 'Focused tests failed' }
& $py -B -X utf8 $runner --self-test --out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'Synthetic checks failed' }
Get-Content ($synthetic + '.md')
& $py -B -X utf8 (Join-Path $repo 'src\milal_mfr02r_pipeline.py') --regression-only $regression
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
$inputs = @(
  '--source', 'D:\MILAL_runs\mfr02r_20260925\release_a',
  '--q11', 'D:\MILAL_runs\mfr02r_q1_1_20260926\release_a_final',
  '--q12', 'D:\MILAL_runs\mfr02r_q12_20260926\release_a',
  '--q14', 'D:\MILAL_runs\mfr02r_q14_20260926\release_a',
  '--q15', 'D:\MILAL_runs\mfr02r_q15_20260926\release_a',
  '--synthetic', $synthetic, '--regression', $regression
)
& $py -B -X utf8 $runner @inputs --out $a
if ($LASTEXITCODE -ne 0) { throw 'A audit failed' }
& $py -B -X utf8 $runner @inputs --out $b
if ($LASTEXITCODE -ne 0) { throw 'B audit failed' }
& $py -B -X utf8 $runner --release $a $b
if ($LASTEXITCODE -ne 0) { throw 'Independent release validation failed' }
Write-Host ('ZIP A: ' + $a + '_results.zip')
Write-Host ('ZIP B: ' + $b + '_results.zip')
Get-Content ($a + '_verification.json')
```

`01`/`21` contain all twelve mechanism statuses; `02`/`03` preserve exact raw and
derived evidence dependencies. `04`–`07` distinguish support, unresolved and
neutral views from positive binding. `09` is non-destructive unique-evidence
ablation; `10` retains relation provenance. `11` diagnoses zero visibility.
`14` preserves all frozen outcomes, while `15`/`16` recompute Q1.3 compatibility.
`17`/`18` are post-freeze Job diagnostics. `19`/`20` replay the exact frozen
Numbers/Bosman fixtures. `22`/`23` explain limitations and readiness. `24` contains
41 release gates, with metadata and SHA256 manifest in `90` and `99`.

The supplemental synthetic path contract is not an empirical extraction engine.
A successful technical release may still report
`NEEDS_SOURCE_BINDING_COVERAGE_REVIEW`. H0.1 is not started by this runner.
