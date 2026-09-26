# MFR.0.2R-Q1.3 validation report

Date: 2026-09-26. Start: `f47756caf72cf1aa171568e6c1a5efa0623753fd` on
`main`, verified equal to freshly fetched `origin/main` at
`https://github.com/aqedah/MILAL.git`. Four pre-existing untracked PDFs were
preserved; synchronization fetched without pulling into the non-clean tree.
Authority: [request](MFR_0_2R_Q13_RESEARCHER_SOURCE.txt).
Contract: [specification](MFR_0_2R_Q13_SPEC.md).

**READY_FOR_MFR_0_2R_Q1_4** — technical compatibility readiness only.
No canonical mother/hierarchy or new human judgment. Q1.4 has not started.

## Integrity and validation

- All **499** frozen source pins unchanged, including Q1.2 source/config/tests/docs.
- Raw crosswalk: **1,049,504** records retained in the verified upstream package.
- Qualified relations **195**, outcome groups **195**, historical judgments **13**:
  original bytes and provenance preserved. Prior Q1.2 pivot output also preserved.
- Reference tables and independently bounded configuration units unchanged.
- Syntax: **6** Python files passed; focused tests **64 passed**.
- Synthetic self-test: **17/17** checks, including S1–S10, overlays, explicit
  exclusions, global-versus-target differences, pipeline preservation and
  deterministic serialization. Human-facing synthetic report/diagnostics inspected.
- Full regression: **2,697 passed**, failures **0**, errors **0**, skipped **0**,
  **822.998 seconds**. Source fingerprint stayed constant throughout.
- **25/25 computed gates passed**: 23 requested gates plus proof-validity and
  source-binding guards. Every gate has a negative mutation. Actual diagnostic
  output tampering also fails the two coexistence gates.
- Independent A/B runs have identical manifests and ZIP bytes; both ZIPs have
  **29 members**, **28 manifest entries**, valid member hashes and CRCs.

An initial full regression was deliberately interrupted before completion to
add explicit UNRESOLVED_COMPATIBILITY output and connect real diagnostic
assignments to the coexistence gates. It is not a validation receipt. Only
`regression_corrected.json` and synthetic run 02 authorize this release.

Fingerprint:
`0afec420169c47af35c353e7b39e3810c24b67c95bc63414e92ae7f60b8d4401`.

## Observed relation and compatibility counts

| Measure | Count |
| --- | ---: |
| Source Job targets | 2,938 |
| Mother relations | 173 |
| Parallel relations | 22 |
| Typed overlay relations in this input | 0 |
| Targets with multiple qualified outcomes | 7 |
| Targets with multiple mothers / mother competitions | 0 |
| Targets with multiple parallel peers / additive parallel sets | 5 |
| Mother-plus-parallel orthogonal sets | 4 |
| Same-pair HYPOTACTIC/PARATACTIC conflicts | 0 |
| True mother-competition targets | 0 |
| True same-pair conflict targets | 0 |
| Global structural-conflict targets | 0 |
| Parallel-bearing targets with unresolved final level compatibility | 15 |
| Multi-relation targets with unresolved final compatibility | 7 |
| Symbolic constraint components | 158 |
| Prior Q1.2 pivots | 7 |
| Q1.3 true decision pivots | **0** |

The whole qualified pool is coherent under the current explicit constraints.
This is a feasibility result, not an accepted whole-book hierarchy. Zero pivots
does not establish complete source coverage or resolve unknown textual levels.
The additive and orthogonal counts overlap; they are not disjoint partitions.

## Reaudit of all seven previous pivots

The mother and peer columns describe simultaneous **hypothetical** assignments,
not accepted selections. All original Q1.2 outcomes remain present.

| Target | Mother option | Parallel peer options that coexist | Q1.3 |
| --- | --- | --- | --- |
| 497588 | 497587 | 497580 | NON_PIVOT — orthogonal |
| 497596 | None | 497579, 497587 | NON_PIVOT — additive parallel |
| 497597 | 497596 | 497580, 497588 | NON_PIVOT — additive and orthogonal |
| 497608 | None | 497579, 497587, 497596 | NON_PIVOT — additive parallel |
| 497609 | 497608 | 497580, 497588, 497597 | NON_PIVOT — additive and orthogonal |
| 497623 | None | 497538, 497569 | NON_PIVOT — additive parallel |
| 497625 | 497624 | 497540 | NON_PIVOT — orthogonal |

Job 2:1 target **497625** represents mother 497624 and peer 497540 together.
Target **497623** represents both peers 497538 and 497569 together. Both
diagnostics have no structural violations and `human_accepted=false`.
The four historical SB12 competing-chain notices remain soft provenance;
they did not establish mutual exclusion.

## Reproducible local artifacts

- A: `D:\MILAL_runs\mfr02r_q13_20260926\release_a`
- B: `F:\MILAL_runs\mfr02r_q13_20260926\release_b`
- ZIPs: append `_results.zip` to either directory path.
- SHA256 (both):
  `08e90e1508f79448b49742888f6cda65e8717a5aa5a1202c4594b05157a4f586`
- Verification: `D:\MILAL_runs\mfr02r_q13_20260926\release_a_verification.json`
- Regression: `D:\MILAL_runs\mfr02r_q13_20260926\regression_corrected.json` and `.log`
- Synthetic: `C:\MILAL\results\q13_synthetic_02\receipt.json`
- Upstream Q1.2 SHA256:
  `3a3118876006a9eaf7ba5f79b435ab5521cd6d4087711def8854512815816770`

These generated artifacts are local-only and must not be committed.
Execution on another computer requires recovery of the exact upstream archive;
follow [the runner guide](README_MILAL_MFR_0_2R_Q13.md).

## Implementation files and remaining work

- `src/milal_q13_model.py`: dimension, compatibility, symbolic assignment and proof model.
- `src/milal_q13_pipeline.py`: unchanged outcome input, reports and post-freeze diagnostic layer.
- `src/milal_q13_runner.py`: source integrity, empirical execution and independent release.
- `src/milal_q13_validation.py`: computed gates and semantic probes.
- `src/milal_q13_synthetic.py`: portable synthetic frozen-output fixtures.
- `tests/test_milal_q13.py`: focused tests and all gate negatives.
- `config/mfr_0_2r_q13_job.json`: frozen pins, input receipt and post-freeze controls.
- `docs/MFR_0_2R_Q13_RESEARCHER_SOURCE.txt`, `docs/MFR_0_2R_Q13_SPEC.md`,
  `docs/README_MILAL_MFR_0_2R_Q13.md`, this report and `docs/HANDOFF.md`.
- `.gitattributes`: exact-byte handling for the researcher request.

No previous analytical core changed. Q1.2's unit-boundary and reference gaps,
including the 27:1–29:1 adapter limitation, remain explicit. A separately
authorized Q1.4 can address independent composite surface units and cross-family
correspondence; no such adapter or new binding was added here.
