# Run the Q1.1 diagnostic review

See [specification](MFR_0_2R_Q11_SPEC.md). Requires the exact extracted Q1 and
MFR.0.2R releases and sibling `_results.zip` archives, external BHSA 2021, and
the repository Python environment. Paths are runner arguments; no user-specific
data path is embedded in analytical code. Q1/H0 and lower cores are read-only.

Run from the repository root. Use D/F or other sufficiently large local disks:
the full regression suite uses substantial temporary storage. Do not redirect
regression stdout into its own receipt `.log` file.

```powershell
$python = Join-Path $PWD '.venv\Scripts\python.exe'
$run = 'D:\MILAL_runs\mfr02r_q1_1_20260926'
$other = 'F:\MILAL_runs\mfr02r_q1_1_20260926'
$source = 'D:\MILAL_runs\mfr02r_20260925\release_a'
$q1 = 'D:\MILAL_runs\mfr02r_q1_20260926\release_a'
$tf = Join-Path $env:USERPROFILE 'text-fabric-data\github\etcbc\bhsa\tf\2021'
New-Item -ItemType Directory -Path (Join-Path $run 'temp') -Force | Out-Null
$env:TEMP = Join-Path $run 'temp'; $env:TMP = $env:TEMP
& $python -B -X utf8 -m unittest discover -s tests -p test_mfr_0_2r_q11.py
if ($LASTEXITCODE) { throw 'Q1.1 focused tests failed' }
& $python -B -X utf8 src/milal_q11_runner.py --self-test --out (Join-Path $run 'synthetic')
if ($LASTEXITCODE) { throw 'Synthetic validation failed' }
& $python -B -X utf8 src/milal_mfr02r_pipeline.py --regression-only (Join-Path $run 'regression_final.json')
if ($LASTEXITCODE) { throw 'Full regression failed' }
$common = @('--source',$source,'--q1',$q1,'--tf-path',$tf,
  '--regression',(Join-Path $run 'regression_final.json'),
  '--synthetic',(Join-Path $run 'synthetic\receipt.json'))
& $python -B -X utf8 src/milal_q11_runner.py @common --out (Join-Path $run 'release_a')
if ($LASTEXITCODE) { throw 'First diagnostic execution failed' }
& $python -B -X utf8 src/milal_q11_runner.py @common --out (Join-Path $other 'release_b')
if ($LASTEXITCODE) { throw 'Independent diagnostic execution failed' }
& $python -B -X utf8 src/milal_q11_runner.py --release (Join-Path $run 'release_a') (Join-Path $other 'release_b')
if ($LASTEXITCODE) { throw 'Determinism or release gate failed' }
Write-Host (Join-Path $run 'release_a_results.zip')
```

Choose fresh output directories for a new run: the runner refuses to overwrite
existing results. Inspect `09_q1_1_methodological_findings.md`, then the Numbers,
Bosman, mechanism and sensitivity CSVs. Nested CSV cells are canonical JSON.
`source_receipts.json` binds all source files and BHSA feature hashes. Exact
upstream archives remain required for complete historical evidence lookup.
