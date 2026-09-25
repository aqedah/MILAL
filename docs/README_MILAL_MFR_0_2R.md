# Running MFR.0.2R

Read [the methodology](CLAUSE_RELATION_GRAMMAR.md) and the four additive requests
before interpreting outputs. Windows is the primary empirical environment;
the Termux runner is supplied for later cross-platform checking, not claimed as
empirically validated by a Windows run.

The Python implementation uses the standard library. Source BHSA 2021 features
are read directly, without changing the frozen observation implementation.
Four upstream archives and their exact SHA256 values are pinned in
`config/mfr_0_2r_job.json`. Real raw projections, logs, result directories and
ZIPs stay outside Git. Use a new output directory with substantial free space.
Candidate sets have no arbitrary size limit and can be large.

Primary analysis is **Job only**. The other books supply explicit post-freeze
fixtures, never full-book relation runs. HB_CORPUS is a construction-search
index only; see [the scope correction](MFR_0_2R_SCOPE_CORRECTION.md).

Windows, from the repository root:

```powershell
.\scripts\run_milal_mfr_0_2r_windows.ps1 `
  -TfPath "$env:USERPROFILE\text-fabric-data\github\etcbc\bhsa\tf\2021" `
  -RunRoot 'D:\MILAL_runs\mfr02r_new_run'
```

The runner performs synthetic self-test, full regression, archive verification,
raw projection, independent A/B runs and conditional release. It stops on any
failure. It never commits or pushes. A failed run remains available for audit;
choose a new directory for a rerun rather than overwriting it.

Individual entry point: `src/milal_mfr02r_pipeline.py`. Options:

- `--self-test --out DIR`: source-neutral synthetic execution and manifest check.
- `--stage-tests-only RECEIPT`: stage test receipt and adjacent log.
- `--regression-only RECEIPT`: full regression receipt and adjacent log.
- `--prepare --tf-path DIR --projection NEW_DIR`: verify inputs and produce raw-only projections.
- `--out NEW_DIR --projection DIR --regression-receipt FILE`: Job blind scope, freeze, explicit-reference controls, historical comparison and gates.
- Add `--reuse-job VERIFIED_JOB_DIR` to retain the already completed Job analysis without rerunning it. The exact pinned manifest is required. The output receives a verified copy of Job only, plus a separate HB corpus-analogue supplement; original Job files stay unchanged.
- `--release A B`: compare independent outputs, require all gates, create deterministic ZIPs and a verification receipt.

Termux: `bash scripts/run_milal_mfr_0_2r_termux.sh TF_PATH NEW_RUN_ROOT python`.
Supply the same verified upstream ZIPs under their configured relative paths.

Open `25_human_review_packet.md` and `24_human_review_cases.csv` only after a
successful release. All judgments are blank. Historical judgments in `18` are
preserved provisional decisions, not newly entered human decisions. Do not use
the candidate graph as a canonical tree or an R4.4 consumer input.

See [output layout](CLAUSE_RELATION_GRAMMAR.md#output-layout-and-lossless-storage)
for logical CSV versus compressed storage. Do not decompress files in place
inside a frozen output directory, since that would invalidate its manifest.
The supplied reader accepts a logical `.csv` path and resolves `.csv.gz`.

To inspect a hidden reference set from a complete extracted result:

```powershell
.\.venv\Scripts\python.exe -X utf8 src\milal_mfr02r_query.py `
  'D:\MILAL_runs\mfr02r_new_run\a\blind\job' SOURCE_CLAUSE_ID TARGET_CLAUSE_ID
```

Replace the two node IDs with exact IDs from the review case. The command verifies
the scope manifest and returns every matching antecedent with a minimal path
witness. The complete conditional graph retains all alternative paths. It uses
the result artifact itself and does not require the original BHSA directory.

Actual readiness and empirical
counts belong in the validation report, not inferred from this runner.
