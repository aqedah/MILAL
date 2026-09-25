# Run H0 from the frozen MFR.0.2R package

Use the exact upstream ZIP and its extracted directory. H0 verifies the ZIP
hash, CRC, member manifest and extracted file hashes before reading evidence.
BHSA paths and external corpora are not H0 execution inputs.

```powershell
& .\scripts\run_milal_mfr_0_2r_h0_windows.ps1 `
  -Source 'D:\MILAL_runs\mfr02r_20260925\release_a' `
  -Archive 'D:\MILAL_runs\mfr02r_20260925\release_a_results.zip' `
  -RunRoot 'D:\MILAL_runs\mfr02r_h0_new_run'
```

RunRoot must not exist. The runner performs synthetic validation, full
regression, independent H0 A/B classification and deterministic release.
It does not run MFR.0.2R, raw corpus extraction or an external-book analysis.
It does not commit or push. Inspect the metrics' warnings separately from
technical gate status. A selectivity warning withholds unconditional H readiness.

Start review with `11_h0_mfr02a_13_case_packet.md`, then target indexes and
complete paged cards. Blank human fields are in the tier CSVs. Full candidate
provenance is in `01_h0_candidate_review_eligibility.csv`; obtain the upstream
ZIP separately to follow original table references. The H0 ZIP does not duplicate
the large upstream tables. Never edit either frozen package to record new judgments.

Termux: `bash scripts/run_milal_mfr_0_2r_h0_termux.sh SOURCE ZIP NEW_RUN_ROOT`.
Cross-platform empirical validation is not implied by providing the runner.
