# MFR.0.2R-H0.2 validation report

Status: TECHNICALLY_VALIDATED — full regression and independent real A/B release passed.

## Baseline

Start local HEAD, fetched origin/main and actual remote main all matched
`f343a06dbb93e026d570eb5638316843d6c98724`. Repository: C:\MILAL;
branch main; upstream origin/main; origin https://github.com/aqedah/MILAL.git.
No reset, rollback, reconstruction or branch switch. Automatic pull was skipped
because the four pre-existing untracked PDFs were present; fetch and actual
remote verification were completed. All four PDF SHA256 values remain unchanged.

## Authority and scope

Exact authority: docs/MFR_0_2R_H02_RESEARCHER_SOURCE.txt, SHA256
`903842a2819f7cf727f5d2b6e1219dbc95bc777a042e3c5ac817618bf91e9f29`.
The CSV and Markdown human registry are separate append-only records of the
explicit researcher decision. They do not compute a human answer from proximity
or any machine evidence. Adjudication date is NOT_SUPPLIED; recording date is
2026-09-26. No review time is invented.

Review packet:
`HR-HD-0f03f7103f29e43daa1a42628ae0fd98384025b2f0a3ed5153bd4c6542738d3d`.
Target: Job 37:20, clause 500065, atom 590199, כִּי יְבֻלָּע.

| Source | Human disposition | Scope |
|---|---|---|
| 500062 | REJECTED_AS_DIRECT_MOTHER | NO_DIRECT_STRICT_MOTHER_RELATION, not NO_RELATION_IN_ALL_LAYERS |
| 500064 | ACCEPTED_AS_LOCAL_MOTHER | HYPOTACTIC; 500065 STRICTLY_BELOW 500064 locally |

Rejected machine-qualified relation:
`QO-0aa7db8fd123f185d7e43968b314d6c880ad4a14772cad5daa1076739fdf457c`,
alternative `HA-40ce77033c7906b6bfb4ced56e3f18bc3cfa0a0b5003c647439c829b1aa67fc9`.
Accepted local relation:
`QO-38b23910f94e6f0879d52d1d2ca503e70e1ee4265df90e392e339795eb5786d9`,
alternative `HA-7bdd373de96c006d336330af5ee703f5959e92bc7779478826d934263e98027f`.

Machine W-A01 and SB03 / SB01+SB02 provenance is preserved exactly. The human
accepts the edge through LOCAL_CONDITIONAL_PROTASIS_APODOSIS_CONFIGURATION;
machine_rule_rationale_adopted=false. The local אם־אמר אישׁ / כי יבלע construction,
direct primary binding, structural completion and two-colon arrangement are the
researcher rationale. Proximity alone is insufficient. The poetic correspondence
remains POST_RELATION_VALIDATION_CONTEXT and creates no new paratactic relation.

KI_FUNCTION_CAUTION is explicit. No universal semantic function of כי is assigned,
W-A01 is not changed and other כי cases are not reopened. Lexical semantics of
יבלע remains UNRESOLVED_FOR_HIERARCHY_PURPOSES; structural motherhood is RESOLVED.

## Frozen integrity and counting

Baseline protection: 593 tracked files, differences zero through final release.
H0.1 source archive expected SHA256:
`e07a3a6cc90674acf1e408372f7faf43b302e9d389c013e3609b4f71f9ad04c8`.
The entire source package is retained byte-for-byte in frozen_h01, including its
unaltered review packet and machine pivot classification. Source raw and historical
human hashes are checked against the authenticated H0.1 receipt before and after.

Verified invariants: raw 1,049,504; qualified 273 (mother 203, parallel 70, overlay 0).
Historical human registry has 13 original decision entries with 13 unique original
hashes; H0.2 adds one decision packet containing two candidate dispositions. The
combined decision-entry count is 14, not 15 independent human decisions.

The separate pivot overlay marks one HUMAN_ADJUDICATED / RESOLVED_BY_HUMAN,
with zero remaining unadjudicated true pivots. The rejected candidate stays in
the 273 machine-qualified universe. The other 271 qualified relations remain
NOT_ADJUDICATED_BY_H02, preserving any historical judgments separately. No new
relations, other automatic acceptance or canonical whole-book hierarchy.

## Validation

Syntax: 5 files PASS. Focused tests: 57 PASS. Synthetic cases H02-S1–S12: 12/12.
Negative gate mutations: 32/32 PASS, including the 27 requested critical gates
and five additional exact-authority/provenance/derived-output integrity gates.
Synthetic and actual human-facing reports inspected. Full regression: 3,107 PASS
in 781.701 seconds; failures/errors/skips: 0/0/0. Final computed release gates:
32/32 PASS in each independent real run. No tests skipped.

Code fingerprint:
`f4f3721dad1f8d83763c421c999a24a7cea17958b87b9124df3397c853117ceb`.
Regression log: `D:\MILAL_runs\mfr02r_h02_20260926\regression_verified.log`.
The generic regression helper's historical baseline field is not the H0.2 start;
the H0.2 baseline is independently verified above and recorded in stage metadata.

ZIP A: `D:\MILAL_runs\mfr02r_h02_20260926\release_a_results.zip`.
ZIP B: `F:\MILAL_runs\mfr02r_h02_20260926\release_b_results.zip`.
Both ZIPs exist, contain 50 members, and pass CRC and manifest validation.
Independent manifests and ZIP bytes are identical. Shared SHA256:
`4e58833a9da1160483333c0a04ac3f173d4e27e56cbe8032c4d3f6206d94aae2`.

Adjudication report:
`D:\MILAL_runs\mfr02r_h02_20260926\release_a\07_h02_job_37_20_adjudication.md`.
Candidate dispositions:
`D:\MILAL_runs\mfr02r_h02_20260926\release_a\02_h02_candidate_dispositions.csv`.
Registry:
`C:\MILAL\docs\HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.csv` and
`C:\MILAL\docs\HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.md`.
All 30 original H0.1 files remain byte-identical in both frozen_h01 copies;
the H0.1 source directory and ZIP remain unchanged. Earlier human registries
and all frozen analytical cores remain unchanged.

## Files changed

- `.gitattributes`
- `config/mfr_0_2r_h02_job.json`
- `src/milal_h02_overlay.py`
- `src/milal_h02_validation.py`
- `src/milal_h02_synthetic.py`
- `src/milal_h02_runner.py`
- `tests/test_milal_h02.py`
- `docs/HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.csv`
- `docs/HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.md`
- `docs/MFR_0_2R_H02_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_2R_H02_SPEC.md`
- `docs/README_MILAL_MFR_0_2R_H02.md`
- `docs/MFR_0_2R_H02_VALIDATION_REPORT.md`
- `docs/HANDOFF.md`

Generated outputs, inputs, ZIPs, logs, PDFs and corpus data remain local-only.

## Next scope

Final release readiness: READY_FOR_MFR_0_2R_H1_0.
Do not start H1.0 automatically. A later explicitly authorized provisional graph
must distinguish machine qualification, human acceptance/rejection, provisional
instantiation and canonical acceptance. This stage makes no whole-book canonical claim.
