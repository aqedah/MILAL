# R4.3 whole-book partial hierarchy scaffold

See [specification](R4_3_SPEC.md). This compiler reads frozen human decisions and
accepted artifacts. It preserves unresolved parents and never builds a complete tree.

## Windows

From the repository root, after installing the project's Python environment:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
$synthetic = "results\r4_3_synthetic_$stamp"
$real = "results\r4_3_real_$stamp"
& powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_milal_r4_3_windows.ps1 -SelfTest -Out $synthetic
if ($LASTEXITCODE -ne 0) { throw 'R4.3 synthetic validation failed' }
Get-Content -Encoding UTF8 (Join-Path $synthetic '04_whole_book_hierarchy_scaffold.md')
# Inspect the synthetic scaffold before starting the authorized accepted-real run.
& powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_milal_r4_3_windows.ps1 -Out $real
if ($LASTEXITCODE -ne 0) { throw 'R4.3 accepted-real audit failed' }
Get-Content -Encoding UTF8 "${real}_run.log"
```

Runner options: `-SelfTest`, `-Out`, `-Python`. Defaults derive from repository root;
no user-specific BHSA path is needed. Python CLI: `--out PATH` and optional
`--self-test`. It verifies required artifacts/frozen hashes before compilation,
emits UTF-8, rejects existing outputs, and creates a directory, `_results.zip` and
`_run.log`. A missing or changed input fails explicitly; no fallback source is used.

Real input paths/hashes are in `config/r4_3_job.json` plus the frozen HSA1/HSA2/HSA2-F
configuration chain: HSA1, HSA2, HSA2-F and seven upstream ZIPs (10 unique archives).
Copy exact accepted local artifacts to those relative paths on another machine.
Some historical checkout files have exact Windows raw-byte pins; a mismatch must
be investigated, not bypassed or fixed by rewriting frozen files.

## Termux instructions (secondary environment; not empirically run here)

Use the repository's prepared Python environment and exact source artifacts. From
the repository root, with a fresh output directory name:

```sh
python -B -X utf8 src/milal_r4_3_hierarchy_scaffold.py --self-test --out results/r4_3_termux_synthetic
# Inspect results/r4_3_termux_synthetic/04_whole_book_hierarchy_scaffold.md first.
python -B -X utf8 src/milal_r4_3_hierarchy_scaffold.py --out results/r4_3_termux_real
cat results/r4_3_termux_real_run.log
```

Do not proceed to real execution after a failed self-test or source/hash mismatch.
Exact raw-byte pins from historical Windows validation may block a checkout with
different line endings; do not weaken gates or claim equivalence without an audit.

## Reading the outputs

`01` reference spans describe judgment loci, not computed full speech coverage.
`02` separates HIERARCHY from MEMBERSHIP, CONTINUATION, closures, horizontal,
descriptive and technical links. Only HIERARCHY defines direct_parent_ids. Groups
are non-textual. `03` enumerates every unresolved parent, including units whose
group membership is known. `04` labels indentation accordingly. `10` accounts for
all 59 original records; `history/` preserves the historical UNRESOLVED states.

Do not interpret group membership, closure targets, responses or technical root
links as settled hierarchical parents. The next step is human review of global seams.
