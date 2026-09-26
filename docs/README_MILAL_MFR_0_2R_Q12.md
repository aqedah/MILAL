# Running MFR.0.2R-Q1.2

The [specification](MFR_0_2R_Q12_SPEC.md) and
[researcher clarification](MFR_0_2R_Q12_CLARIFICATION.md) define this additive
stage. All previous analytical cores remain frozen. Python comes from the
repository virtual environment. No BHSA corpus download or full external-book
analysis is performed: verified frozen Job observations and the exact Q1.1
fixture projections provide source evidence.

The runner checks the three ZIP SHA256 values, archive integrity, extracted
manifests and all 484 frozen repository files. Full regression and synthetic
receipts must match the current code/config/test fingerprint. Output directories
must not exist; select a fresh run directory rather than overwriting history.

```powershell
$ErrorActionPreference = 'Stop'
$q12Repo = (Get-Location).Path
$q12Python = Join-Path $q12Repo '.venv\Scripts\python.exe'
$q12Root = 'D:\MILAL_runs\q12_new_run'
$q12Other = 'F:\MILAL_runs\q12_new_run'
$q12Source = 'D:\MILAL_runs\mfr02r_20260925\release_a'
$q12Q1 = 'D:\MILAL_runs\mfr02r_q1_20260926\release_a'
$q12Q11 = 'D:\MILAL_runs\mfr02r_q1_1_20260926\release_a_final'
New-Item -ItemType Directory -Path "$q12Root\temp" -Force | Out-Null
$env:TEMP = "$q12Root\temp"
$env:TMP = $env:TEMP
& $q12Python -B -X utf8 src/milal_q12_runner.py --self-test --out "$q12Root\synthetic"
if ($LASTEXITCODE) { throw 'Synthetic validation failed' }
& $q12Python -B -X utf8 src/milal_mfr02r_pipeline.py --regression-only "$q12Root\regression.json"
if ($LASTEXITCODE) { throw 'Full regression failed' }
foreach ($q12Output in @("$q12Root\release_a", "$q12Other\release_b")) {
    & $q12Python -B -X utf8 src/milal_q12_runner.py --source $q12Source --q1 $q12Q1 --q11 $q12Q11 --out $q12Output --regression "$q12Root\regression.json" --synthetic "$q12Root\synthetic\receipt.json"
    if ($LASTEXITCODE) { throw "Q1.2 failed: $q12Output" }
}
& $q12Python -B -X utf8 src/milal_q12_runner.py --release "$q12Root\release_a" "$q12Other\release_b"
if ($LASTEXITCODE) { throw 'Deterministic release failed' }
Write-Host "Results: $q12Root\release_a_results.zip"
Write-Host "Independent results: $q12Other\release_b_results.zip"
```

01–05 record profiles, families, pair correspondences and SB06/SB11 witnesses.
06–08 record unresolved reference searches and any independently qualified
reference paths. 09 holds constraint-only SB12 results. 10–12 hold qualified
candidates, distinct structural outcomes and pivots. 13–15 are post-freeze
controls/diagnostics; 16–19 are coverage, method, readiness and computed gates.
90 records provenance and 99 hashes all other output files.

Additional lossless tables retain every raw candidate with its frozen-row hash,
all independent units, source-binding witnesses, selected diagnostic raw pairs,
external fixture profiles and pair audits, and unchanged human decisions.
The full source evidence remains in the verified input archives. Readiness is
reported separately from technical success; H0.1 never starts automatically.
