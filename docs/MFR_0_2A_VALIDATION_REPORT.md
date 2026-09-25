# MFR.0.2A validation report

**MFR_H1_CONFIGURATION_ADJUDICATED**.
**READY_FOR_MFR_0_2B_RESUMPTION_ADJUDICATION**.

## Repository and authority (1–3)

Start commit: `9c005d862452709b4b53cf80de6185fd081d825b`. Branch main; verified origin:
`https://github.com/aqedah/MILAL.git`. The containing commit uses
`Adjudicate marker-first hierarchy configurations`. Its exact end hash, push and
clean-tree result are reported in the task completion response.

Authority: [exact researcher request](MFR_0_2A_RESEARCHER_SOURCE.txt), SHA256
`1141e397cc824efbcb8c54edd8609f23afe460c2b8d07d4080adf47a913a8309`. [Specification](MFR_0_2A_SPEC.md) and
[execution README](README_MILAL_MFR_0_2A.md) document the serialization rules.

This is the first MFR marker-first human relation adjudication. Historical HSA/JIN
outcomes are comparison provenance, never inputs to the supplied human decisions.
The tracked human registry is `config/mfr_0_2a_human_decisions.json`;
its SHA256 is `f0f7a3f8d54fb374f12a38121be4fd6d67510502af74328b99dae20f85ae43e2`.

## Human decisions (4–12)

| Measure | Count |
| --- | ---: |
| H1 decisions | 13 |
| PARATACTIC | 5 |
| FORMAL_ONLY | 7 |
| INSUFFICIENT | 1 |
| HYPOTACTIC | 0 |
| EMBEDDING | 0 |
| Accepted configuration relations | 5 |
| Raw constituent edges created | 0 |
| New mothers | 0 |
| Underlying raw pairs retained | 32 |

The five accepted configurations are CFG000028, CFG000046, CFG000227,
CFG000230 and CFG001981. FORMAL_ONLY: CFG000037, CFG000231, CFG000281,
CFG000282, CFG000333, CFG000432 and CFG001192. INSUFFICIENT: CFG001053.

PARATACTIC accepts a configuration-level textual relation only. Raw constituent
pairs remain evidence memberships. No sibling expansion, hierarchy tree or root
was created. FORMAL_ONLY preserves meaningful linguistic correspondence;
INSUFFICIENT does not mean NO_RELATION in every dimension.

CFG000227 uses the observable analytical label REPEATED_TRANSITION_CONFIGURATION.
Its verbatim supplied label is retained in provenance. Unspecified configuration
validity remains blank. No review time, literary interpretation or participant
identity is invented. Source excerpts and explicit inherited rationale references
remain attached to each decision.

## Deferred dimensions (13–14)

H1 cases deferred to MFR.0.2B: **8** with raw resumption
membership. The remaining five have no H1 resumption membership; this is not a
negative resumption judgment. All 13 have RESUMPTIVE unreviewed.

H1 cases deferred to MFR.0.2C: **13**, including archival
cessation/coverage/nested evidence. No closure judgment is inherited from H1.
Full future scopes preserve **182 R1 cases** and
**69 C1 cases**; all future human decisions are blank.

## Post-freeze historical comparison (15)

- AGREES_WITH_HISTORICAL: 1 — CFG001981, exact 27:1/29:1 clause endpoint sets.
- PARTIALLY_AGREES: 1 — CFG000028. Historical 2:1 contains five clauses;
  this MFR target contains its first four. Parataxis agrees but scope differs.
- NO_HISTORICAL_COMPARISON: 11.
- HISTORICAL_MORE_SPECIFIC, MFR_MORE_CONSERVATIVE, CONFLICTS: 0 in this run.

Comparison covers the 111 historical relations in the pinned JIN.0.7 crosswalk
embedded in JIN.0.8. It retains HSA relation IDs and later JIN typing/review
provenance. Eight records with UNRESOLVED clause endpoints are explicitly listed
as non-joinable, not guessed. No match means no comparison in this inventory,
not a historical rejection. Opposite stored directions retain their distinct IDs.

Matching uses explicit clause-node sets. A single full endpoint plus an explicit
subset can support scope comparison; neither matching references nor Hebrew
similarity is used. No historical unit is asserted identical to an MFR object.

The initial actual human freeze preceded historical inspection; its hash was
`b74c367d3f0ea701d5aae3de4063b4e2485895d29524f459c956f138c516b699`. Both final releases reproduce that same human freeze.
Decisions were never changed to improve historical agreement.

## Calibration principles (16)

Seven researcher-approved principles, CAL-H1-01 through CAL-H1-07, are frozen:
repeated configurations may support parataxis; isolated repetition does not imply
direct edges; homologous constituents do not automatically become siblings;
lexical recurrence alone is insufficient; long-distance construction may remain
formal-only; independently recovered onset configurations may support parataxis;
cessation-derived coverage is not independent hierarchy evidence.

## Validation and artifacts (17–19)

- Syntax: PASS; Windows synthetic runner: 61 tests and 35 gate assertions PASS.
- Final full regression: **2152 PASS**, failures/errors/skips **0**.
- Real A and B: **35 in-package gates PASS** each.
- Four independent release gates PASS: full regression, zero skips, manifests,
  deterministic rerun. **39 distinct gate definitions**, each negative-tested.
- A/B ZIP bytes, human freeze and historical comparisons are identical.
- All 405 immutable baseline repository pins verify unchanged.
- Full upstream ZIP, attachments, decision/source serialization, all raw pair
  memberships and both future scope tables independently verify.
- Synthetic human output and actual adjudication report were inspected.
- Termux shell syntax PASS; no empirical Termux execution is claimed.

An earlier pre-comparison regression run was superseded when historical comparison
code and tests were added. It was stopped and is not used as a validation receipt.
The final receipt covers the unchanged final source.

ZIP: `results/mfr02a_release_20260925_a_results.zip`.
SHA256: `6be4c760a07aaa18cfbdb8229dd575bf3ffb6fef2941bdb926ab4e351007d2cf`.

Independent verification: `results/mfr02a_release_20260925_a_independent_verification.json`.
Release gates: `results/mfr02a_release_20260925_a_release_gates.csv`.
Human decision freeze: `14_human_decision_freeze.csv` inside the ZIP.
The complete original MFR.0.1b ZIP is included byte-for-byte.

## Frozen layers and readiness (20)

No previous analytical core or historical judgment was modified. MFR.0.1 discovery,
MFR.0.1a consolidation and MFR.0.1b role/independence audit remain frozen. The new
human registry is a separate append-only phase. New accepted relations are exactly
five CONFIGURATION_RELATION_DECISION objects; no constituent edge or mother.

**MFR_H1_CONFIGURATION_ADJUDICATED**.
**READY_FOR_MFR_0_2B_RESUMPTION_ADJUDICATION**.

Next: researcher adjudication of the preserved resumption scope. Closure follows
in MFR.0.2C. No whole-book hierarchy assembly, root or R4.4 consumer is implemented.
Upload the complete result ZIP and its independent verification receipt; this
report is optional supporting documentation.

## Changed repository files

- `.gitattributes`
- `config/mfr_0_2a_historical_comparison.json`
- `config/mfr_0_2a_human_decisions.json`
- `config/mfr_0_2a_job.json`
- `docs/HANDOFF.md`
- `docs/MFR_0_2A_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_2A_SPEC.md`
- `docs/MFR_0_2A_VALIDATION_REPORT.md`
- `docs/README_MILAL_MFR_0_2A.md`
- `scripts/run_milal_mfr_0_2a_termux.sh`
- `scripts/run_milal_mfr_0_2a_windows.ps1`
- `src/milal_mfr02a_core.py`
- `src/milal_mfr02a_finish.py`
- `src/milal_mfr02a_freeze.py`
- `src/milal_mfr02a_history.py`
- `src/milal_mfr02a_pipeline.py`
- `src/milal_mfr02a_synthetic.py`
- `src/milal_mfr02a_verify.py`
- `tests/test_mfr_0_2a.py`
