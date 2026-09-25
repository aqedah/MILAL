# Run Q1

Use the repository virtual environment. Original MFR.0.2R and H0 directories
and ZIPs are immutable inputs. `--tf-path` is used solely to inspect exact
existing external fixture identities after the Job blind result is frozen.
All destination directories must be fresh. The full historical regression suite
needs substantial temporary space; choose a drive with adequate free space for
both TEMP/TMP and outputs. The example uses the computer-A D drive.

```powershell
$ErrorActionPreference = 'Stop'
$repo = (git rev-parse --show-toplevel)
$python = Join-Path $repo '.venv\Scripts\python.exe'
$q1Root = Join-Path 'D:\MILAL_runs' ('q1_' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path "$q1Root\temp" -Force | Out-Null
$env:TEMP = "$q1Root\temp"
$env:TMP = $env:TEMP
& $python -B -X utf8 "$repo\src\milal_q1_runner.py" --self-test --out "$q1Root\synthetic"
if ($LASTEXITCODE) { throw 'Q1 self-test failed' }
& $python -B -X utf8 "$repo\src\milal_mfr02r_pipeline.py" --regression-only "$q1Root\regression.json"
if ($LASTEXITCODE) { throw 'Full regression failed' }
$q1Args = @('--source','D:\MILAL_runs\mfr02r_20260925\release_a',
  '--archive','D:\MILAL_runs\mfr02r_20260925\release_a_results.zip',
  '--h0','D:\MILAL_runs\mfr02r_h0_20260925\release_a',
  '--h0-archive','D:\MILAL_runs\mfr02r_h0_20260925\release_a_results.zip',
  '--tf-path',"$env:USERPROFILE\text-fabric-data\github\etcbc\bhsa\tf\2021",
  '--regression-receipt',"$q1Root\regression.json",
  '--synthetic-receipt',"$q1Root\synthetic\self_test.json")
& $python -B -X utf8 "$repo\src\milal_q1_runner.py" @q1Args --out "$q1Root\a"
if ($LASTEXITCODE) { throw 'Q1 first execution failed' }
& $python -B -X utf8 "$repo\src\milal_q1_runner.py" @q1Args --out "$q1Root\b"
if ($LASTEXITCODE) { throw 'Q1 independent execution failed' }
& $python -B -X utf8 "$repo\src\milal_q1_runner.py" --release "$q1Root\a" "$q1Root\b"
if ($LASTEXITCODE) { throw 'Q1 release verification failed' }
Write-Host "Q1 output: $q1Root"
```

Individual executions report DETERMINISTIC_RERUN pending. Release verifies
independent bytes before completing that gate. Review 18_q1_method_report.md,
19_q1_next_scope.md and warning/coverage fields before considering H0.1.
