# HR1 usage

See [HR1_SPEC.md](HR1_SPEC.md). HR1 links the committed human CSV to immutable
R3c.3 and PROV1 archives. No BHSA, generator, or R2.2 rerun is needed.

The CLI is `src/milal_hr1_adjudication_linkage.py --help`. It accepts
`--self-test`, `--r3c3-zip`, `--prov1-zip`, `--adjudication`, `--output-dir`.
The human CSV defaults to the repository's committed adjudication path.
It requires the recorded source commit to remain available in Git.

From the repository root, this complete PowerShell block validates and runs the
authorized accepted real inputs. Both output directories must be new. It uses
the local virtual environment; absence is an error, not an interpreter fallback.

```powershell
$ErrorActionPreference = 'Stop'
$repoDir = (Get-Location).Path
$py = Join-Path $repoDir '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $py -PathType Leaf)) { throw 'Repository-local Python is missing.' }
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$entry = Join-Path $repoDir 'src\milal_hr1_adjudication_linkage.py'
& $py -B -X utf8 -c "from pathlib import Path; [compile(p.read_bytes(),str(p),'exec') for p in [Path('src/milal_hr1_adjudication_linkage.py'),Path('src/milal_hr1_synthetic.py'),Path('tests/test_hr1_adjudication_linkage.py')]]"
if ($LASTEXITCODE -ne 0) { throw 'Syntax validation failed.' }
& $py -B -X utf8 -c "import pathlib,tempfile,unittest; tempfile.tempdir=str(pathlib.Path(tempfile.gettempdir()).resolve()); r=unittest.TextTestRunner().run(unittest.defaultTestLoader.discover('tests')); raise SystemExit(not r.wasSuccessful())"
if ($LASTEXITCODE -ne 0) { throw 'Regression suite failed.' }
& $py -B -X utf8 $entry --self-test --output-dir (Join-Path $repoDir "results\hr1_synthetic_$stamp")
if ($LASTEXITCODE -ne 0) { throw 'Synthetic self-test failed.' }
& $py -B -X utf8 $entry --r3c3-zip (Join-Path $repoDir 'results\r3c_3_windows_20260919_091111_results.zip') --prov1-zip (Join-Path $repoDir 'results\prov1_windows_20260920_081304_results.zip') --output-dir (Join-Path $repoDir "results\hr1_human_review_linkage_$stamp")
if ($LASTEXITCODE -ne 0) { throw 'Real HR1 failed: preserve diagnostics and stop.' }
```

The CLI prints the result ZIP and success-log paths. Each fresh directory has
11 artifacts; the adjacent ZIP uses `_results.zip`, the adjacent log `_run.log`.
Inspect 07 and 08 Markdown files, all 22 gate rows and metadata counts. A
successful exit verifies programmed invariants; scholarly acceptance remains
distinct. No historical output receives human-field writeback.

For synthetic-only validation omit the last real-run invocation. Synthetic
targets are intentionally artificial and clearly labeled, while human strings
come from the committed source to exercise exact Unicode/multiline preservation.
