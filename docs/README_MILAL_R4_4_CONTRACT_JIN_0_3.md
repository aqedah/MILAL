# Execute the JIN.0.3 contextual audit

Read [specification](R4_4_CONTRACT_JIN_0_3_SPEC.md) and the
[validation report](R4_4_CONTRACT_JIN_0_3_VALIDATION_REPORT.md).
Python standard library and Git are required. Restore the exact configured
JIN.0.2 ZIP under results/ (or use --archive / -Archive to relocate identical
bytes). Real mode also requires raw BHSA 2021 matching the frozen feature hashes.
No automatic download, replacement source or fuzzy linkage is available.

## Windows

From the repository directory:

```powershell
$ErrorActionPreference = 'Stop'
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_3.py -v
if ($LASTEXITCODE -ne 0) { throw 'JIN.0.3 tests failed' }
& .\.venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v
if ($LASTEXITCODE -ne 0) { throw 'Full regression failed' }
& .\scripts\run_milal_jin_context_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
```

Require skip 0 and inspect the printed output's `25_contextual_human_review_packet.md`
before real execution. Verified data path on this Windows machine:

```powershell
& .\scripts\run_milal_jin_context_windows.ps1 -TfData 'C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021'
if ($LASTEXITCODE -ne 0) { throw 'Real contextual audit failed' }
```

Optional `-Out` selects a fresh directory and `-Python` another interpreter.
Both `<out>` and `<out>_work` must be absent. The runner prints the result directory,
automatic deterministic `<out>_results.zip` and external physical source log.
Repeat with a fresh output directory to verify byte-identical ZIPs. All these
generated artifacts remain ignored and must not be committed.

## Termux

Use actual repository Bash/Python entrypoints; this does not claim an empirical
Termux run. Restore the exact upstream ZIP and external BHSA 2021 first.

```bash
cd ~/MILAL
git pull --ff-only
python -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_3.py -v &&
python -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v &&
bash scripts/run_milal_jin_context_termux.sh --self-test --out "results/jin_0_3_synthetic_$(date +%Y%m%d_%H%M%S)"
```

After synthetic validation and packet inspection, use the verified device path:

```bash
cd ~/MILAL
run_out="results/jin_0_3_real_$(date +%Y%m%d_%H%M%S)"
bash scripts/run_milal_jin_context_termux.sh --tf-data "$HOME/text-fabric-data/github/etcbc/bhsa/tf/2021" --out "$run_out" &&
sha256sum "${run_out}_results.zip"
```

## Review entrypoints

24 lists the actual default locus-level review cases; 25 is the six-section packet.
19–22 show every 2:11/32:1 hypothesis; 23 shows all old mother cases and the
38:1/40:1/40:6 panel. 16 groups the 98 historical SAME_LEVEL comparisons. 36 is the
clause-internal appendix, not an automatic macro-parent queue. 08 preserves all
insufficient evidence and 30 records contextual auxiliaries. All old JIN.0.2 files
remain under history/. C1 files are frozen by 14 before C2 reads human judgments.
Only UNREVIEWED is prefilled; no relation or macro-projection decision is supplied.
