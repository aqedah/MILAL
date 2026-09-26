# H0.2 execution

H0.2 consumes the verified H0.1 package and the explicitly authored researcher
registry. It neither reruns relation discovery nor modifies source data.
Run from the repository root. Python paths below are repository-relative;
external paths are caller-supplied local inputs and output destinations.
Fresh output directories and ZIP names are required; existing releases are not overwritten.

```powershell
$ErrorActionPreference = 'Stop'
$h02Python = Join-Path (Get-Location) '.venv\Scripts\python.exe'
$h02A = 'D:\MILAL_runs\mfr02r_h02_20260926\release_a'
$h02B = 'F:\MILAL_runs\mfr02r_h02_20260926\release_b'
$h02Regression = 'D:\MILAL_runs\mfr02r_h02_20260926\regression_verified.json'
$h02Synthetic = Join-Path (Get-Location) 'tmp\h02_synthetic.json'
& $h02Python -B -X utf8 -m unittest discover -s tests -p test_milal_h02.py
if ($LASTEXITCODE) { throw 'H0.2 focused tests failed' }
& $h02Python -B -X utf8 src/milal_h02_runner.py --self-test --out $h02Synthetic
if ($LASTEXITCODE) { throw 'H0.2 synthetic validation failed' }
& $h02Python -B -X utf8 -c 'import sys; sys.path.insert(0,"src"); from milal_mfr02r_pipeline import regression; regression(sys.argv[1])' $h02Regression
if ($LASTEXITCODE) { throw 'Full regression failed; inspect the adjacent .log' }
$h02Args = @(
  '--h01', 'D:\MILAL_runs\mfr02r_h01_20260926\release_a',
  '--raw-source', 'D:\MILAL_runs\mfr02r_20260925\release_a\blind\job\09_candidate_evidence_matrix.csv',
  '--historical-human', 'D:\MILAL_runs\mfr02r_q15_20260926\release_a\preserved_human_judgments.csv',
  '--synthetic', $h02Synthetic, '--regression', $h02Regression
)
foreach ($h02Destination in @($h02A, $h02B)) {
  & $h02Python -B -X utf8 src/milal_h02_runner.py @h02Args --out $h02Destination
  if ($LASTEXITCODE) { throw "H0.2 run failed: $h02Destination" }
}
& $h02Python -B -X utf8 src/milal_h02_runner.py --release $h02A $h02B
if ($LASTEXITCODE) { throw 'H0.2 release validation failed' }
Write-Output "ZIP A: ${h02A}_results.zip"
Write-Output "ZIP B: ${h02B}_results.zip"
```

The raw table can be stored as `.csv.gz`; the existing physical-path resolver
finds it without modifying or decompressing the input. Historical counts are
validated against the authenticated H0.1 receipt and original human-source rows.
The full-regression helper retains its historical baseline field; the H0.2 start
commit is separately verified and recorded in H0.2 metadata. The current code
fingerprint must match both receipts; stale receipts are rejected.

Review `07_h02_job_37_20_adjudication.md`, `08_h02_ki_function_caution.md`,
`09_h02_post_adjudication_review_status.csv` and `12_h02_gates.csv`.
The final release JSON prints exact ZIP paths, SHA256, CRC and manifest results.
Readiness permits researcher consideration of H1.0; it does not start it.
