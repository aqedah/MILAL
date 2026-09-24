# R4.4-CONTRACT.JIN.0.1 validation — 2026-09-24

Start commit: `28162717d229c8541d9386668ab7123cd7cded10`, main.
Commit message: `Reconcile R4.4 contract with Jin single-mother principle`.
This report belongs to that commit; final remote equality is checked after push.

## Result and methodological meaning

Append-only compatibility audit complete. Current readiness:
**BLOCKED_PENDING_SINGLE_MOTHER_COMPATIBILITY_REVIEW**.
The historical READY_FOR_HUMAN_CONTRACT_REVIEW artifact remains byte-identical.
Revised Q1–Q9 and JIN-Q0/Q1/Q2 remain UNREVIEWED; answers remain blank.

The overall representation stays a layered typed graph; textual daughters in
the textual hierarchy require one mother except a separately adjudicated root.
Historical necessity decisions concern layered-representation sufficiency and
are preserved on their own axis. They do not automatically exempt applicable
textual daughters. Strict clause hierarchy and macro-unit applicability remain
distinct, pending Q8/JIN-Q0. No root or individual mother is chosen.

Jin attribution and its verification limits are documented in the
[methodological addendum](R4_4_CONTRACT_JIN_0_1_ADDENDUM.md).
The official thesis record was verified; PDF §3.2.9 could not be independently
read because the linked PDF returned 403. The detailed principle is explicitly
attributed to the researcher's supplied summary. No external PDF was added.

## Canonical inventory

| Actual canonical kind | Count |
|---|---:|
| TEXTUAL_NODE | 42 |
| TRANSITION_ANCHOR | 7 |
| COMPOSITION_GROUP | 14 |
| ROLE_ALIAS | 3 |
| SOURCE_EVIDENCE_ANCHOR | 8 |
| TECHNICAL_ROOT | 1 |
| Total | 75 |

Actual non-alias textual nodes: **49**. Source textual=true including the three
aliases: **52**. Evidence-only anchors are neither lost nor promoted to macro units.

| Textual-node audit | Count |
|---|---:|
| One existing accepted direct mother | 3 |
| Zero existing accepted direct mothers | 46 |
| More than one existing direct mother | 0 |
| Explicit textual-root candidates supplied/selected | 0 / 0 |
| Applicability unresolved within textual nodes | 4 |
| Additional scope/single-mother review | 46 |

Root status is globally UNADJUDICATED; zero proposed root candidates is not an
answer to the root question. Job 1:1 has native FG-PREP clause evidence but no
accepted canonical textual unit/root in this registry. JOB_BOOK stays technical.

SM1/SM2/SM3/SM4/SM5/SM6/SM7 = **42 / 3 / 14 / 3 / 1 / 0 / 12**.
The twelve SM7 rows comprise eight evidence-only anchors and four textual nodes:
H:HSA008 (1:22), H:HSA011 (2:10), H:HSA018 (32:1), H:HSA024 (37:24).
Their recorded ending/transition roles do not by themselves establish daughter
participation. This is an applicability proposal, not a change to those roles.

## Historical 57 crosswalk

All 57 historical parents remain UNRESOLVED and all original additional-review
flags remain false. P2/P3/P4/P5/P6/P7 counts remain **8/6/10/19/13/1**.

| Current audit of historical 57 | Count |
|---|---:|
| Exempt non-textual groups | 8 |
| Exempt actual role aliases | 3 |
| Actual textual nodes | 46 |
| Already mothered despite historical UNRESOLVED field | 0 |
| Single-mother/scope review required | 46 |
| Explicit root-candidate review rows | 0 |

P3's six historical rows are three canonical speech representatives and three
aliases, not six aliases. Among the 46 textual rows, 42 are SM1 proposals and
four need SM7 applicability review before mother adjudication.

Job 2:11 / H:HSA012 retains DIRECT_TEXTUAL_PARENT_NOT_REQUIRED, PARAGRAPH_ONSET,
FRIENDS_ARRIVAL / PARTICIPANT_INTRODUCTION, NOT_WITHIN_SECOND_TESTING_SCENE and
OPENING_NARRATIVE_COMPLEX membership. Its current proposal is SM1 / REQUIRED
under the instructed macro reading, pending scope review. The single-mother
question is OPEN; no mother or root is assigned.

## Relation semantics and candidate pool

The 14 existing TEXTUAL_HIERARCHY rows contain:

- CHILD_OF: two accepted direct-mother edges.
- HIERARCHICALLY_ABOVE: one accepted direct-mother edge, reverse orientation.
- CONTINUES_WITHIN: ten placement relations, not direct mothers.
- DIRECT_LOCAL_CLOSURE: one closure relation, not a direct mother.

No ambiguous current relation type. The three existing assignments remain:
H:HSA003 → H:HSA002; H:HSA014 → H:HSA013; H:HSA026 → H:HSA025.
All 250 canonical relations remain unchanged, including technical links.

Candidate review covers all **46** motherless textual nodes: **8** candidate rows
on **8** nodes; **38** nodes have zero candidates in this conservative pool.
All eight are UNADJUDICATED, never accepted edges:

| Daughter under review | Candidate | Existing review evidence |
|---|---|---|
| H:HSA004 / H:HSA005 / H:HSA006 / H:HSA007 | H:HSA003 | Explicit CONTINUES_WITHIN placement, four separate rows |
| H:HSA017 | H:HSA016 | DIRECT_LOCAL_CLOSURE |
| H:HSA031 | H:HSA030 | CONTINUES_WITHIN |
| H:HSA2-INTERNAL-11-4 | H:HSA2-C1-S5 | CONTINUES_WITHIN |
| H:HSA2-NO-28 | H:HSA015 | CONTINUES_WITHIN |

Candidate generation does not establish directness or choose a mother. It is not
an exhaustive linguistic search. Exact native clause links are retained for
later source-grounded examination. No nearest, speaker-only, theme-only,
membership-only or technical-root heuristic is used. The 98 directed sibling
rows all have an unknown parent on at least one side; no common mother is
generated. Synthetic tests additionally exercise known-parent consistency and
conflict, multiple-mother conflict and unknown relation semantics.

New textual parent edges **0**; new node-specific human judgments **0**;
new methodological human judgments **1**:
JIN_SINGLE_MOTHER_PRINCIPLE_ADOPTED_FOR_REVIEW.
Participant arc UNADJUDICATED; R4.4 consumer NOT IMPLEMENTED.

## Validation

- Syntax PASS for audit harness and tests.
- Stage tests: **63 PASS**, zero failures/errors/skips, 28.507 seconds (final configuration-byte revalidation).
- Full regression: **1,388 PASS**, zero failures/errors/skips, 302.500 seconds.
- Synthetic self-test and human-facing packet inspection PASS.
- Frozen-real audit and separate-process rerun: **38/38 gates PASS** each.
- Every one of 37 model gates has a dedicated negative mutation; manifest
  tampering is separately negative-tested. Both external release gates also have
  negative tests.
- External release gates: **2/2 PASS** (actual full regression skip-zero and
  byte-identical independent real ZIPs).
- Independent output audit: **278 ZIP members**, all **257 upstream members**
  byte-identical, **17 valid manifests**, **779 exact input row receipts**,
  **180 frozen repository pins** verified. Original canonical records, 57 human
  necessity decisions, A–G, ANA and all relation layers preserved.
- The independent checker initially compared a CSV scalar string to an integer;
  explicit integer decoding corrected that checker. Audit code and output bytes
  were unchanged, and all independent checks then passed.

Final configuration was normalized to repository LF without semantic changes.
Stage tests and synthetic/real/independent runs were repeated; final archives
below supersede development runs. The full regression tested identical parsed
configuration and unchanged implementation.

Synthetic archive:
`results/r4_4_contract_jin_0_1_synthetic_final_20260924_b_results.zip`, SHA256
`3f52755a8dc7490cea97e21bad7dec548573936c01efeb0c150516488da3dbbc`.

Real and independent rerun:
`results/r4_4_contract_jin_0_1_real_final_20260924_b_results.zip` and
`results/r4_4_contract_jin_0_1_real_repeat_20260924_b_results.zip`.
Both SHA256:
`895264dfd4a11efc147464c393933ed8650e4ad146da42fa067a1c9e9eb30d5e`.

Local receipts/logs:
`results/r4_4_contract_jin_0_1_unit_final_20260924_b.log`,
`results/r4_4_contract_jin_0_1_full_regression_final_20260924_a.log`,
`results/r4_4_contract_jin_0_1_full_regression_final_20260924_a.json`,
`results/r4_4_contract_jin_0_1_independent_audit_20260924_b.json`.
These and all ZIPs remain ignored/local-only.

## Changed repository files

- `.gitattributes` — preserve exact researcher request bytes.
- `config/r4_4_contract_jin_0_1_job.json` — source pins and auditable classification policy.
- `tests/r4_4_contract_jin_audit.py` — compatibility audit harness only.
- `tests/test_r4_4_contract_jin_audit.py` — positive, negative and mutation coverage.
- `docs/R4_4_CONTRACT_JIN_0_1_RESEARCHER_SOURCE.txt` — exact request.
- `docs/R4_4_CONTRACT_JIN_0_1_ADDENDUM.md` — method/source verification boundaries.
- `docs/R4_4_CONTRACT_JIN_0_1_SPEC.md` — audit/source/output contract.
- `docs/README_MILAL_R4_4_CONTRACT_JIN_0_1.md` — execution workflow.
- `docs/R4_4_CONTRACT_JIN_0_1_VALIDATION_REPORT.md` — this report.
- `docs/HANDOFF.md` — current stage and pending research questions; history retained.

## Remaining work

Researcher review of Q1–Q9, especially Q8/JIN-Q0 clause-versus-macro scope.
If needed, authorize TEXTUAL ROOT AUDIT separately. Only after applicability
review should SINGLE-MOTHER PARENTAGE ADJUDICATION cover the 46 flagged actual
textual nodes, with the four SM7 cases resolved for participation first. The
eight evidence-only anchors require clause-scope applicability review separately.
No methodological acceptance, root choice or mother choice is inferred from
these technical validation results. Previous analytical cores are unchanged.
