# HSA2-F audit runner

See [specification](HSA2_FINAL_SPEC.md). The runner reads the three researcher-authored
final decisions and frozen HSA2 outputs; it never chooses targets automatically.

From the repository root, use fresh output names (existing results are rejected):

```powershell
& .\.venv\Scripts\python.exe -B -X utf8 src/milal_hsa2_final.py --self-test --out results/hsa2_f_synthetic_new
if ($LASTEXITCODE -ne 0) { throw 'Synthetic audit failed' }
# Inspect the synthetic report before the authorized accepted-real audit.
Get-Content -Encoding UTF8 results/hsa2_f_synthetic_new/04_job_27_31_closure_target_final_adjudication.md
& .\.venv\Scripts\python.exe -B -X utf8 src/milal_hsa2_final.py --out results/hsa2_f_real_new
if ($LASTEXITCODE -ne 0) { throw 'Accepted-real audit failed' }
Get-Content -Encoding UTF8 results/hsa2_f_real_new_run.log
```

Paths are derived from the repository root. The only CLI arguments are `--out`
(required) and `--self-test`. Required accepted ZIP paths/hashes are in
`config/hsa2_final_job.json` and the frozen HSA1/HSA2 configuration chain. Missing,
changed or unaccepted inputs fail explicitly. No substitute source is allowed.

Outputs are an ignored directory, sibling `_results.zip` and `_run.log`. The final
report is `04_job_27_31_closure_target_final_adjudication.md`. All original HSA2
members remain under `hsa2/`; original unresolved candidates are not overwritten.
For machine use, read dimension and relation together in `03_final_closure_relations.csv`.
Do not interpret NO_DIRECT_RELATION outside its direct-target dimension.
