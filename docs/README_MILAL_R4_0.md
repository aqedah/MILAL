# R4.0 Windows execution

Read [R4_0_SPEC.md](R4_0_SPEC.md). This is inventory/scaffold only; no final
boundary hierarchy or macro-level acceptance follows from successful gates.

The default four ZIP paths and committed human CSV are explicit in
`config/r4_0_job.json`. On computer A the restored PROV1/HR1 filenames end in
`results(1).zip` / `results(2).zip`; their exact SHA256 values equal the accepted
originals. No renaming or fuzzy source selection is necessary. Other machines
can supply `-Mr1`, `-R3c3`, `-Prov1`, `-Hr1`, `-Human`; fingerprints cannot be
overridden. Data paths are runtime arguments, not user-specific analytical code.

```powershell
$python = Join-Path (Get-Location).Path '.venv\Scripts\python.exe'
& $python -B -X utf8 -c "import pathlib,tempfile,unittest; tempfile.tempdir=str(pathlib.Path(tempfile.gettempdir()).resolve()); r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"
if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
& .\scripts\run_milal_r4_0_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic failed' }
& .\scripts\run_milal_r4_0_windows.ps1 -TfData (Join-Path $env:USERPROFILE 'text-fabric-data\github\etcbc\bhsa\tf\2021')
if ($LASTEXITCODE -ne 0) { throw 'R4.0 stopped; inspect source or gate failure' }
```

Use a fresh output directory (`-Out` optional). Both ZIP and log are siblings of
that directory. No downloads, source rewriting or overwrite are performed.
Generated results are ignored. Direct Python flags use the same names in lower
case with `--`: `--tf-data`, `--mr1`, `--r3c3`, `--prov1`, `--hr1`, `--human`,
`--out`, `--self-test`.

Start review with 07 whole-book scaffold and 08 focus report. Full IDs, event
spans, source locators, untouched human records, all extension dependencies and
unpromoted singleton/Way0 contexts remain in the machine-readable tables.
Candidate counts and trigger multiplicity are not scores or evidence votes.
Zones use a documented positional width and overlap; they are not macro units.
