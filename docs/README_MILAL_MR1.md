# Running MR1 on Windows

See [MR1_SPEC.md](MR1_SPEC.md) for scope, gates, identity limits and provenance.
Use a fresh output directory; real inputs and generated packages remain ignored.
Python comes from the repository `.venv` by default. No downloads or installs
are performed by the runner. Text-Fabric 13.1.0 and local BHSA 2021 are required
for real runs; synthetic tests require only Python's standard library.

```powershell
$repo = (Get-Location).Path
$python = Join-Path $repo '.venv\Scripts\python.exe'
& $python -B -X utf8 -c "import pathlib,tempfile,unittest; tempfile.tempdir=str(pathlib.Path(tempfile.gettempdir()).resolve()); r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"
if ($LASTEXITCODE -ne 0) { throw 'Regression failed' }
& .\scripts\run_milal_mr1_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
& .\scripts\run_milal_mr1_windows.ps1 `
  -TfData (Join-Path $env:USERPROFILE 'text-fabric-data\github\etcbc\bhsa\tf\2021') `
  -HistoricalDir 'C:\py\5.2.5\output_v5_2_5' `
  -HistoricalScript 'C:\py\5.2.5\job_tf_structure_pipeline_v5_2_5.py' `
  -HistoricalConfig 'C:\py\5.2.5\job_tf_config_v5_2_5.json'
if ($LASTEXITCODE -ne 0) { throw 'MR1 reproduction failed; inspect diagnostics' }
```

Paths above describe computer A; change explicit source arguments on another
computer. The Python CLI has the same arguments in kebab case (`--tf-data`,
`--historical-dir`, `--historical-script`, `--historical-config`, `--out`,
`--self-test`). The source fingerprint pins cannot be overridden through CLI.

Review `08_reproduction_summary.md`, all rows of `09_gates.csv`, the field-level
audit and `11_control_spot_checks.csv`. Inspect historical_projection when legacy
comparison fields are needed. Review `10_current_feature_evidence.json` for actual
features and ordered memberships, and `90_run_metadata.json` for source paths and
hashes. R4 remains on hold pending researcher review even when every gate passes.
