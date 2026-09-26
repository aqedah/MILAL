# Reproduce Q1.6R mechanism ontology audit

Read [the specification](MFR_0_2R_Q16R_SPEC.md) and HANDOFF. This runner consumes
verified frozen packages; it does not reload BHSA or re-run earlier analytical
stages. Each archive must be adjacent to its extracted directory as
`<directory>_results.zip`. Outputs must use new directories. Intermediate runs
with no full-regression receipt retain pending gates and cannot be released.

```powershell
$repo = 'C:\MILAL'
$py = Join-Path $repo '.venv\Scripts\python.exe'
$runner = Join-Path $repo 'src\milal_q16r_runner.py'
$work = 'D:\MILAL_runs\mfr02r_q16r_reproduce'
$a = Join-Path $work 'release_a'
$b = 'F:\MILAL_runs\mfr02r_q16r_reproduce\release_b'
$synthetic = Join-Path $work 'synthetic.json'
$regression = Join-Path $work 'regression.json'
Set-Location $repo
New-Item -ItemType Directory -Path (Join-Path $work 'temp') -Force | Out-Null
$env:TEMP = Join-Path $work 'temp'
$env:TMP = $env:TEMP
& $py -B -X utf8 -m unittest discover -s tests -p test_milal_q16r.py
if ($LASTEXITCODE -ne 0) { throw 'Focused tests failed' }
& $py -B -X utf8 $runner --self-test --out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'Synthetic checks failed' }
Get-Content ($synthetic + '.md')
& $py -B -X utf8 (Join-Path $repo 'src\milal_mfr02r_pipeline.py') --regression-only $regression
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
$inputs = @(
  '--source', 'D:\MILAL_runs\mfr02r_20260925\release_a',
  '--q16', 'D:\MILAL_runs\mfr02r_q16_20260926\release_a',
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


Outputs classify roles and provenance only; all frozen qualified outcomes remain unchanged. H0.1 is never started automatically. The two source PDFs listed in configuration must be available with their verified hashes.
