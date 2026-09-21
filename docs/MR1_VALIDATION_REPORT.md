# MR1 validation — 2026-09-21

MR1 technical reproduction succeeded. Researcher acceptance remains pending;
R4.0 is not authorized to proceed. Starting commit:
`fa7d4477470306513a2002c26982368e6954de2d`. The commit introducing this report
contains the validated implementation; its resulting SHA is reported after push.

## Source and versions

- Current data: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
- BHSA 2021; Text-Fabric 13.1.0; Job 1:1–42:17, 2938 clauses, 2977 atoms.
- Historical script: `C:\py\5.2.5\job_tf_structure_pipeline_v5_2_5.py`.
- Historical config: `C:\py\5.2.5\job_tf_config_v5_2_5.json`.
- Historical baseline: `C:\py\5.2.5\output_v5_2_5`.
- Historical version 5.2.5; recorded BHSA validation COMPLETE and 70/70
  regression PASS. Historical process exit code not recovered.
- 77 isolated source dependencies match pinned historical AST digests. The
  original complete pipeline is not imported/executed.

All hashes below are verified **current local source/comparison fingerprints**,
not recovered historical acceptance hashes. The historical raw BHSA input-byte
identity is UNKNOWN_NOT_VERIFIED. The real run records SHA256 for 65 actual TF
files, including automatically loaded text/section dependencies; mother/tab/
pargr/rela/code are not loaded for MR1.

| Local source | SHA256 |
| --- | --- |
| Historical script | `26854a0adcdeabf61199d0786974c1a0dc153dbfe6de86781ac14b98caea6ac1` |
| Historical config | `a3152566b88747b50edb0e3d567a93ce7dbb1c71f2364bb4fccf5f163d2e1a02` |
| 90_run_metadata.json | `b14adb9fe20f6adf26fdb851f3db5e4da64c0df3629958bf4c0971ad04df781e` |
| 91_config_audit.csv | `c8b82d04d33395801f6bd30e9a8a31e1da45f1658747213ef801c8173533bc0b` |
| 00_job_surface_clauses.csv | `951933a166d343546d249676319672ce54319562f2ba64f25fd1a6da944b37d8` |
| 01_job_csf_speech_turns.csv | `7d5844f5ed58b1ccbe5d56388005b0919f1dc8dcc17e5e714287791bb595dbf1` |
| 02_job_explicit_closures.csv | `0f8e90ac8f10239c735557dc52c5477006b4548b038ab8ecb9ac9927fc91584c` |
| 03_job_way0_wayhi.csv | `ee7d939e7293813a3ad0b810330ef3b4702d6967162b4a8306da89894d7970a7` |

## Exact historical comparison

| Population | Historical/current | Fields per row | Exact identity and fields | Historical-only/current-only | Historical-schema byte equality |
| --- | ---: | ---: | ---: | ---: | --- |
| Surface clauses | 2938 / 2938 | 35 | 2938 | 0 / 0 | Yes |
| CSF events | 56 / 56 | 39 | 56 | 0 / 0 | Yes |
| Explicit closures | 2 / 2 | 7 | 2 | 0 / 0 | Yes |
| Way0 audit population | 170 / 170 | 12 | 170 | 0 / 0 | Yes |

All 3166 audit rows are EXACT; zero FIELD_DIFFERENCE rows. All historical columns
are compared, not merely a selected intersection. Normalized row comparison and
the separately generated historical-schema bytes both match. The enriched MR1
primary outputs have a new schema and are not claimed byte-identical to legacy
CSV files.

CSF identity uses supplied ordinal event_id, then checks starting/ending reference,
family and speech level, plus every other field. Historical CSVs do not supply
CSF native clause IDs. Current native clause IDs come from actual extraction;
no historical clause ID is inferred from text/reference. The historical CSF
classification is 46 TOP_LEVEL_CSF, 8 EMBEDDED_CSF, 2 REPORTED_SPEECH, retained
solely for reproduction and not accepted as new interpretation.

Historical `03_job_way0_wayhi.csv` is an audit table of all Way0 candidates, not a table containing only positive Wayhi events.

The temporal-lexeme auxiliary condition checks for a verbal word with a non-empty/non-NA `vt` value according to the historical implementation; MR1 does not strengthen this into a newly imposed finite-only criterion.

| Wayhi-positive reference | Clause | Atom | Framing detected |
| --- | ---: | ---: | --- |
| Job 1:5 | 497528 | 587631 | No |
| Job 1:6 | 497538 | 587641 | Yes |
| Job 1:13 | 497569 | 587674 | Yes |
| Job 2:1 | 497623 | 587728 | Yes |
| Job 42:7 | 500411 | 590552 | Yes |

Positive 5 / negative 165. Job 1:5 illustrates why framing is not a condition
for core Wayhi classification. These are observed results; locations appear
only in regression/control assertions, never in detection logic.

## Explicit linkage and inspected controls

2938 clauses map to 2977 native atoms. All 39 multi-atom clauses preserve complete
ordered membership, including non-consecutive atom IDs. There are 3201
event/clause linkage rows: 2938 surface, 90 CSF formula-span, 3 closure-span,
170 Way0. Expanded event/clause/atom memberships total 3240; these include
intentional participation of a clause in several kinds of evidence.

The control CSV includes all 175 clauses in Job 1:1–3:1 and all clauses at the
other requested controls. Spot-checks of source features/projections/linkages:

- 1:1: four clauses, no forced CSF/closure/Wayhi. 1:6, 1:13, 2:1 reproduce
  positive Wayhi; 2:11 and 3:1 do not gain a forced marker.
- 27:1 and 29:1: TAKE_MASHAL+AMR across three clauses each. משל remains a
  formula lexeme, rejected as an inferred addressee; BASIC profile / CORE scope.
- 31:40: תמם+דבר closure is only clause 499623, atom 589751, width 1. It remains
  independently represented; frozen R3 S02135 is not changed or redefined.
- 32:1: שבת+ענה closure spans 499624–499625, atoms 589752/589753, width 2.
- 32:2 and 37:24: no forced CSF, explicit closure or Wayhi.
- 38:1: ANSWER+AMR, explicit addressee plus adjunct, historical SCOPE_EXPANDED.
- 40:1: ANSWER+AMR, explicit addressee yields EXPANDED profile but CORE scope.
- 42:7: separate Wayhi clause 500411 and SIMPLE_AMR clause 500413. The CSF
  explicit addressee yields EXPANDED profile with CORE scope.
- 42:16: three clauses, no forced CSF, explicit closure or Wayhi.

## Validation and reproducibility

- Python syntax validation: PASS for all new Python modules/tests.
- Complete unittest regression: **273 PASS, 0 failures/errors/skips**, comprising
  **202 prior tests + 71 MR1 tests**.
- MR1 tests cover closure spans/dedup, CSF inclusion/anchors/scope/lookahead,
  Way0 versus WayX and morphology, separate framing, temporal auxiliary
  infinitives/participles, mapping, exact comparison and package corruption.
- **33/33 computed gates PASS** in synthetic and both real runs. Every gate
  has a negative mutation/test; the manifest test corrupts bytes and membership.
- Synthetic packet was inspected before real execution. Its small CSV snapshots
  are fabricated regression fixtures, not historical evidence.
- PowerShell 5.1 synthetic runner and PowerShell 7 real runner: exit 0.
- Two independent Analyzer instances agree within each run. Two fresh real
  processes agree on **all 17 member bytes and complete ZIP bytes**.
- Input fingerprints rechecked before publication; disk/ZIP/manifest verified.

Before final commit, new source files were normalized to repository LF and the
four byte-regression CSVs received a scoped CRLF checkout attribute. Validation
was rerun after source normalization. Relative to the initial successful run,
only source-hash metadata and its manifest changed; all analytical/evidence
outputs remained byte-identical. Staged source bytes and filtered fixture
checkout bytes were verified against the validated working files.

Local ignored outputs:

- `C:\MILAL\results\mr1_synthetic_final_20260921\`
- `C:\MILAL\results\mr1_real_final_20260921_a\`
- `C:\MILAL\results\mr1_real_final_20260921_a_results.zip`
- `C:\MILAL\results\mr1_real_final_20260921_a_run.log`
- `C:\MILAL\results\mr1_real_final_20260921_b\`
- `C:\MILAL\results\mr1_real_final_20260921_b_results.zip`
- `C:\MILAL\results\mr1_real_final_20260921_b_run.log`

Both real ZIP SHA256:
`9f287dca2a7689e04f37b4a9dbcfe53dd714dcc8dc9d1a702f46f476f6537ec0`.

## Repository changes and decision

- `.gitattributes`: scoped CRLF checkout for the four byte-regression CSVs.
- `src/milal_mr1_historical_rules.py`: isolated pinned historical dependencies.
- `src/milal_mr1_surface_marker_provenance.py`: direct source adapter, evidence,
  mapping, strict comparison, gates and deterministic package writer.
- `src/milal_mr1_synthetic.py`: small synthetic API corpus/self-test.
- `config/mr1_job.json`: source fingerprints, AST locators, rule configuration
  and Job-specific regression expectations.
- `tests/test_milal_mr1.py` and `tests/fixtures/mr1/`: tests and tiny fabricated
  snapshots (README plus surface/csf/closure/way0 CSVs).
- `scripts/run_milal_mr1_windows.ps1`: explicit-path Windows runner.
- `docs/MR1_SPEC.md`, `docs/README_MILAL_MR1.md`, this report and
  `docs/HANDOFF.md`: scope, workflow, results and pending review.

No hierarchy, parentage, macro composition or final boundary assignment was
produced. Historical comparison fields remain identified as such. Frozen
R1–R3/PROV1/HR1 cores were not modified. Generated empirical data and ZIPs are
not committed.

MR1 is ready for researcher acceptance review as a reproducibility/provenance
result. It does not recover frozen R1.1 or v6.42.12 and does not establish
accepted macro-marker semantics. Those packages remain unavailable. R4.0 must
remain on hold until MR1 and the future role of CSF are reviewed explicitly.
