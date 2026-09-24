# JIN.0.3 contextual relation consolidation — validation

Date: 2026-09-24. Start commit: `4455716793eb6e015b309ccfa5106c6c19a5bf24`.
Readiness: **READY_FOR_CONTEXTUAL_HUMAN_RELATION_REVIEW**.
This is technical validation of evidence preparation, not human acceptance of a relation.
Commit message: `Consolidate blind relations with multi-clause context`.
The containing Git commit identifies the final repository version without a self-referential hash.

## Sources and separation

Authoritative upstream ZIP: `results/r4_4_contract_jin_0_2_blind_relation_audit_final_20260924_e_results.zip`.
SHA256: `837e34f552a63e9143eeaf0fe747b466f80c8d6868e8bb904519a47732fe3abd`.
Raw TF directory: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
C1 independently reads the 23 permitted raw features and checks exact feature values and
receipts against frozen JIN.0.2. It consumes no native hierarchy feature. The C1 read
allowlist contains 38 sources including those raw files, frozen blind inputs, neutral
rules and code receipts. Human sources, composition sources, native hierarchy sources,
and human-label leakage are each **0**. Actual paths are recorded in external run logs.

C1 manifest SHA256: `673c3f5135e9268cae729c3d0b4d390a47ada3a6cfa75bedadc74ed796b896c5`.
C2 opens the complete human-containing upstream archive only after verifying that freeze.
C1 bytes remain unchanged after C2. All 304 upstream files, 203 frozen repository pins,
19 recursive result manifests, the C1 manifest and original blind manifest verify.

## Populations and review reduction

| Measure | Actual |
|---|---:|
| Frozen eligible pair rows | 13,355 |
| Supported parataxis / hypotaxis | 80 / 149 |
| Supported primary rows / exact memberships | 229 / 229 |
| Insufficient archive rows | 13,126 |
| Neutral loci | 49 |
| Focal clause contexts | 255 |
| Fixed plus four adaptive window bundles / signatures | 1,275 / 1,275 |
| Computed pair contextual comparisons | 3,606 |
| C1 supported consolidated locus cases | 190 |
| Archived auxiliary memberships | 131 |
| Clause-internal hypotheses / consolidated cases | 43 / 19 |
| Supported cases with distinct explicit JT endpoints | 75 |
| Possible cross-locus or macro projection cases | 72 |
| Scope-D macro-projection cases | 2 |
| Hypotactic macro-mother candidates | 0 |
| Historical conflict/reopen grouped cases | 36 |
| Old unique pair review queue / final default queue | 13,344 / 206 |

Reduction = **98.45623501199041%**, computed after consolidation without a cap.
The 72 projection-eligible cross-locus cases differ from 75 literal cross-locus cases:
three local cases cross a locus boundary without qualifying for cross/macro projection.
The two scope-D cases are paratactic candidates, not selected mothers.
C1 has 190 supported cases; C2's default queue additionally groups historical comparison
cases and excludes 19 internal-only cases. Counts must not be conflated with pair rows.

Default buckets: REVIEW_A_CONFLICT_OR_REOPEN **136**;
REVIEW_B_SUPPORTED_CROSS_LOCUS **70**. Internal appendix **19**, archive **13,126**,
both excluded from the default queue. Historical-linked reopen cases are a subset of A.
Packet sections A–D show conflicts, supported cross-locus evidence, grouped SAME_LEVEL
comparisons and 2:11/32:1 controls; E summarizes internal evidence and F the archive.
All original pair rows and the old 13,344-case list are preserved losslessly under history/.

## Manual control inspection

Inspected raw Hebrew, source clause IDs, fixed/adaptive windows, categorical flags,
special panels 19–23, controls 33 and packet 25. Results are descriptive:

| Control | Observed context |
|---|---|
| 1:6 / 1:13 | Focal MATCH; following 1/2/3 DIFFERENT; CONFIGURATION_CONTRAST |
| 1:6 / 2:1 | Focal and following 1/2/3 MATCH; EXACT_CONFIGURATION_CORRESPONDENCE |
| 38:1 / 40:1 | Focal and following 1 MATCH; following 2/3 DIFFERENT; PARTIAL_CONFIGURATION_CORRESPONDENCE |
| 38:1 / 40:6 | Focal and following 1 MATCH; following 2/3 DIFFERENT; PARTIAL_CONFIGURATION_CORRESPONDENCE |
| 40:1 / 40:6 | Same categorical partial pattern; three-way raw panel retained |
| 3:1 / 3:2 | NO_CONTEXTUAL_CORRESPONDENCE; historical relation remains insufficient |

For 1:6, same-verse nodes are 497538–497541; 2:1 has 497623–497627,
including the additional final infinitive clause. Exact configuration refers to the
configured focal/following-three comparison, not identity of entire verses or scenes.
Preceding contexts differ and remain visible. No child/peer decision is inferred.
For 3:1, same-verse nodes 497687/497688 remain distinct from 3:2 nodes 497689/497690.
Raw domain `?` at 497687 stays Unknown and its domain-run window is a singleton;
participant-continuity window includes 497687–497690 without asserting coreference.
Generic next-raw-formula probes are descriptive and use frozen formula atoms; they
are not new speech-turn detection or accepted boundaries. In particular 40:1's next
raw formula is at 40:2 (500260), not an inferred next speaker identity.

| Special panel | Original hypo pairs | Internal | Literal cross-locus | Macro-projectable |
|---|---:|---:|---:|---:|
| Job 2:11 | 4 | 3 | 1 | 0 |
| Job 32:1 | 2 | 0 | 2 | 0 |

2:11: 497667→497669 is CROSS_VERSE_LOCAL_DEPENDENCY; 497668→497669,
497668→497671 and 497672→497675 are SAME_VERSE_LOCAL_EMBEDDING.
32:1: 499623→499625 is INFINITIVE_DEPENDENCY; 499623→499626 is
CROSS_VERSE_LOCAL_DEPENDENCY. Both are possible local projection only.
Original direction and source hypothesis are preserved; none is assigned as a macro mother.

## Historical comparison and proposals

Existing 1:13 CHILD_OF 1:6 and 40:1 CHILD_OF 38:1 retain their original pairwise
conflict. Context result is PAIRWISE_CONFLICT_CONTEXT_SOFTENS_CONFLICT for both,
without accepting those human relations or converting para into hypo.
3:1 HIERARCHICALLY_ABOVE 3:2 remains CONTEXT_INSUFFICIENT.
Historical SAME_LEVEL **98**: CONTEXT_SUPPORTS_HUMAN_RELATION **2**,
CONTEXT_PARTIAL_SUPPORT **96**. All 98 retain individual machine-readable rows.

CP1/CP2/CP3/CP4/CP5/CP6/CP7 = **0/27/3/5/2/12/0**, all UNREVIEWED.
Old JP proposals are preserved as pairwise-only proposals. Context refinements are
append-only differences, never automatic supersession. CP2 is a candidate label;
its 27 placements are not the two stricter scope-D case count.

New human judgments = accepted parataxis = accepted hypotaxis = new parent edges = **0**.
Participant arc **UNADJUDICATED**; root unselected; R4.4 consumer **NOT IMPLEMENTED**.
Previous frozen analytical cores were not modified.

## Validation and artifacts

Python syntax and Windows/Termux runner syntax PASS. Stage-specific suite: **68 tests**,
all included in final full regression **1,529 PASS, failures 0, errors 0, skipped 0**.
Full regression elapsed 708.121 seconds. Early development failures in two negative-test
fixture mutations were corrected before this final run; no skipped or weakened old tests.
S1–S12 all PASS. All **52 run gates** PASS (51 model invariants plus manifest), with
negative tests; both external release gates PASS and have negative coverage.
Final synthetic packet inspected before real execution. Windows real runs A and B are
independent processes and their **entire ZIP bytes are identical**. No Termux empirical
run is claimed. Independent audit additionally checks all raw window node membership,
surfaces, source files, manifests, full original rows and blank review fields.

Real ZIP A: `results/r4_4_contract_jin_0_3_contextual_audit_final_20260924_a_results.zip`.
Real ZIP B: `results/r4_4_contract_jin_0_3_contextual_audit_final_20260924_b_results.zip`.
Both SHA256: `5412da317a698cbc506114464d2c7ed328f5e65e1b3af9511cf1eff224070387`.
350 members, CRC and manifests PASS. Results and logs remain ignored/local-only.
Synthetic ZIP: `results/r4_4_contract_jin_0_3_synthetic_final_20260924_a_results.zip`;
SHA256 `2ef27b06a7ebc90d149a03b1f26b9f98cfea850866bf532b6aed284aaee1097d`.
Regression receipt: `results/r4_4_contract_jin_0_3_regression_final_20260924_a.json`.
Independent receipt: `results/r4_4_contract_jin_0_3_independent_release_receipt.json`.

## Remaining work and limitations

Human adjudication of the 206 contextual cases remains pending. The deterministic
scope helper uses explicit neutral locus membership and focal heads; its conservative
projection classification is evidence for review, not proof that other macro relations
are impossible. Fixed/adaptive windows and all exceptions remain available. Surface
participant recurrence is not referential identity. Absence of a projectable hypo
candidate does not reject a historical mother judgment. R4.4 implementation stays deferred.

## Changed repository files

- `.gitattributes`
- `config/jin_context_rules.json`
- `config/r4_4_contract_jin_0_3_job.json`
- `docs/HANDOFF.md`
- `docs/R4_4_CONTRACT_JIN_0_3_RESEARCHER_SOURCE.txt`
- `docs/R4_4_CONTRACT_JIN_0_3_SPEC.md`
- `docs/R4_4_CONTRACT_JIN_0_3_VALIDATION_REPORT.md`
- `docs/README_MILAL_R4_4_CONTRACT_JIN_0_3.md`
- `scripts/run_milal_jin_context_windows.ps1`
- `scripts/run_milal_jin_context_termux.sh`
- `src/milal_jin_context_configuration.py`
- `src/milal_jin_contextual_relation_audit.py`
- `src/milal_jin_postcontext_comparison.py`
- `src/milal_jin_context_pipeline.py`
- `src/milal_jin_context_synthetic.py`
- `tests/test_r4_4_contract_jin_0_3.py`
