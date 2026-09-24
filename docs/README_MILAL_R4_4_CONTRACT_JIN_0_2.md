# Run JIN.0.2 blind linguistic audit

Read [specification](R4_4_CONTRACT_JIN_0_2_SPEC.md) and
[validation](R4_4_CONTRACT_JIN_0_2_VALIDATION_REPORT.md). This is an audit;
it neither selects a mother nor implements the R4.4 consumer.

Python standard library only. Git must contain the pinned baseline and the 188
unchanged source files. Real mode requires the exact JIN.0.1 ZIP from the config
and the external BHSA 2021 directory. Alternative data and fuzzy linkage are
rejected. Output and its `_work` sibling must not exist. The output directory,
`_results.zip`, `_run.log` and work files remain ignored local artifacts.

## Windows

From the repository, one block validates syntax/tests and synthetic output:

```powershell
$ErrorActionPreference = 'Stop'
$py = '.\.venv\Scripts\python.exe'
& $py -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_2.py -v
if ($LASTEXITCODE -ne 0) { throw 'Stage tests failed' }
& .\scripts\run_milal_jin_blind_audit_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
```

Inspect the synthetic `14_revised_contract_review_packet.md`, then use the real
runner with an explicit corpus path (the path below is this verified Windows
machine's data location, never a Python default):

```powershell
& .\scripts\run_milal_jin_blind_audit_windows.ps1 -TfData 'C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021'
if ($LASTEXITCODE -ne 0) { throw 'Real audit failed' }
```

Use `-Out` to select a fresh output directory and `-Archive` only to relocate
the same hash-pinned ZIP. `-Python` overrides the repository-local environment.
No real run begins automatically from a failed synthetic run. Full regression:
`python -B -X utf8 -m unittest discover -s tests -p 'test_*.py' -v` (skip 0 required).

## Termux

Termux uses the existing Bash/Python runner convention. This is an executable
command, not a claim of Termux empirical validation. First restore the exact
configured JIN.0.1 ZIP under `results/` and BHSA 2021 under the indicated external
path (or replace it with the verified path on that device).

```bash
cd ~/MILAL
git pull --ff-only
python -B -X utf8 -m unittest discover -s tests -p test_r4_4_contract_jin_0_2.py -v &&
bash scripts/run_milal_jin_blind_audit_termux.sh --self-test --out "results/jin_0_2_synthetic_$(date +%Y%m%d_%H%M%S)"
```

After inspecting synthetic results:

```bash
cd ~/MILAL
run_out="results/jin_0_2_real_$(date +%Y%m%d_%H%M%S)"
bash scripts/run_milal_jin_blind_audit_termux.sh \
  --tf-data "$HOME/text-fabric-data/github/etcbc/bhsa/tf/2021" --out "$run_out" &&
sha256sum "${run_out}_results.zip"
```

The runner creates the ZIP automatically with fixed member ordering/timestamps.
An independent invocation with a fresh `--out` must produce identical ZIP bytes.
Keep the physical source-access log for each invocation; it intentionally stays
outside the deterministic ZIP because it contains machine-specific paths.

## Review entry points

01/02: neutral target and raw linguistic evidence; 03/04: all eligible pairs and
unadjudicated hypotheses; 05: every supported hypotactic mother candidate;
06/07/18/19: blind source audit/freeze/metadata/rules; 08–11: post-blind historical
comparison; 12: native comparison; 13: unreviewed placements; 14: researcher
packet; 16: next review scope; 21: complete unranked distinct relation-case list.
The 21 review fields remain blank except UNREVIEWED. The packet's RQ1–RQ7 are new
questions; historical Q1–Q9 are preserved byte-for-byte in `history/`.
