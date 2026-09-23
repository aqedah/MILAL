# HSA3-D/E validation — 2026-09-23

Starting commit: `60b6a5a0cdb2e8e8dde55ae2210774f58c84eb24`.
`main` tracked `origin/main`; remote verified as `https://github.com/aqedah/MILAL.git`.
The initial tree was clean and `git pull --ff-only origin main` was already current.
Commit message: `Freeze Elihu global seam adjudications`.

## Final human decisions

SEAM_D and SEAM_E are FROZEN in the new human layer. Original PREP case bytes
and review worksheets remain historical and unmodified.

- **32:1** retains TRANSITION_COMPONENT and Q2 POST_CLOSURE_TRANSITION. Explicit
  NO_DIRECT_PARENTAGE constraints exclude it as parent of the introduction and
  the Elihu speech sequence. No 32:6 CHILD_OF 32:1 is generated.
- **32:2–5** retains NARRATIVE_INTRODUCTION. Existing edge
  `E:440d08279bd9b22af859`, HSA019 → ELIHU_SPEECH_SEQUENCE, is confirmed with its
  original ID and source row. No duplicate INTRODUCES_AND_ENCLOSES edge and no
  32:6 CHILD_OF 32:2 are created.
- **32:6 / 34:1 / 35:1 / 36:1** retain their historical directed sibling and
  grouping records. ELIHU_SPEECH_SEQUENCE remains a NON_TEXTUAL_GROUP. No new
  ELIHU_INTERVENTION_COMPLEX is needed.
- **37:24** retains the SPEECH_UNIT_END judgment. The newly created canonical
  relation to ELIHU_SPEECH_SEQUENCE is TERMINATES_ENCLOSING_GROUP in
  HIGHER_ORDER_TERMINAL_EFFECT. Its supplied group scope is 32:6–37:24, kept
  as human metadata rather than rewritten historical coverage.
- **37:24 → 38:1** receives NO_DIRECT_PARENTAGE (TEXTUAL_PARENTAGE) and
  NO_DIRECT_RESPONSE_ANTECEDENT (RESPONSE_RELATION), both explicit human
  negatives. No CHILD_OF, CONTINUES_WITHIN or RESPONSE_TO is created.

## Computed counts and duplicate audit

| Category | Count |
| --- | ---: |
| New researcher seam decisions | 2 |
| Newly created canonical positive relations | 1 |
| Confirmed-existing canonical edge rows | 18 |
| Newly created negative constraints | 4 |
| NO_ACTION_DUPLICATE requests | 0 |
| New textual parentage relations | 0 |

The 18 confirmations consist of one transition record, one introduction relation,
four membership edges and twelve historical directed sibling records. They are
not 18 new human judgments or recreated equivalent relations. The existing
introduction was confirmed rather than counted a second time as duplicate-skipped.
No redundant request remained for NO_ACTION_DUPLICATE in this actual input.

All five new positive/negative records have distinct exact semantic keys and
none matches an old canonical relation. Negative tests cover repeated requests,
preexisting terminal relations, the explicit introduction alias and ambiguous
multiple existing equivalents. No fuzzy source identity or inferred source ID.

## Methodological interpretation

32:1's transition and 32:2–37:24's composition are different claims. A narrative
introduction can introduce/compositionally enclose a speech sequence without
making one verse the textual parent of another. Adjacent ending/onset or speaker
succession alone establishes neither parentage nor a response antecedent.

Conversely, **NO DIRECT HIERARCHICAL EDGE does not mean NO RHETORICAL/DISCOURSE
RELATION**. Q4 CONTRASTIVE_ANA_FRAME and Q5 ELIHU_RESPONSE_ROLE_INTERVENTION remain
accepted. TEXTUAL HIERARCHY, COMPOSITION/GROUPING, TRANSITION, OVERLAY/RESPONSIO
and RESPONSE RELATION are separately represented here. The negative constraints
are supplied human judgments, not automated absence-of-evidence rules or claims
of universally absent relationships.

All criteria codes come from the unchanged 24-code registry. Missing concepts
are methodological notes. There is no formula-length, adjacency, speaker-only,
theme-only or nearest-opening parent rule. The contextual/distributional accepted
38:1/40:6 same-level onsets and 40:1 CHILD_OF 38:1 remain intact.

## ANA and frozen integrity

Q2 ACCEPTED, Q3 UNRESOLVED/HUMAN_DEFERRED, Q4 ACCEPTED and Q5 ACCEPTED are
byte/provenance intact. Q3 retains lexical/participant evidence as a dependency
only, and is not solved by SEAM_E. No causal or fulfillment claim is created.

All 59 historical judgments, all 57 historical unresolved rows, all seven
original PREP cases and all ANA.0.1/0.2/0.3 artifacts remain intact. The HSA2-F
relations are unchanged: 31:40 → 29:1 DIRECT_LOCAL_CLOSURE; → 27:1
NO_DIRECT_RELATION; → POST_DIALOGUE_JOB TERMINATES_ENCLOSING_GROUP.
Other analytical cores and criteria were not modified. No new lexical scan,
BHSA extraction, ANA re-adjudication, A–C/F–G judgment or R4.4 work occurred.

## Unresolved crosswalk

The historical question in every row is exact direct textual parentage, not
whether introduction/grouping/terminal relations are known. This stage assigns
no positive direct textual parent. The complete 57-row crosswalk therefore has:

- **Resolved by D/E: 0**.
- **REMAINS_UNRESOLVED, directly D/E-relevant: 9** — eight D-owned nodes and
  the 38:1 node shared with E but still owned by unadjudicated F.
- **NOT_APPLICABLE_TO_THIS_SEAM_DECISION: 48** — original parentage retained.
- **All exact direct-parent questions still unresolved: 57**.
- **Primary A–C/F–G rows retained: 49** (A 13, B 1, C 29, F 4, G 2).

The final two totals overlap the preceding categories. They must not be added.
Freezing D/E's supplied decisions does not manufacture a resolution of their
residual exact-parent questions. Historical inputs are not reduced or rewritten.

## Tests, gates and reproducibility

- Syntax validation on the new implementation/tests: PASS.
- **73 new tests PASS**, skip 0.
- **939 full regression tests PASS**, skip 0, 135.784 seconds; all 866 previous
  tests retained. Final code includes the required-field schema rejection test.
- **37/37 synthetic gates PASS**, self-test and human-facing packet inspected
  before real-artifact execution.
- **37/37 real gates PASS**.
- All 36 model gates have explicit failing mutations; the 37th manifest gate
  has a separate corruption test. Forbidden parentage/continuation/response,
  duplicate semantics and Q3 promotion also have targeted negative tests.
- Independent processes: **ZIP bytes and 129/129 member bytes identical**.
- **112/112 original ANA.0.3 members** preserved byte-for-byte.
- **9/9 current/nested manifests** verified and input/output/repeat ZIP CRC PASS.
- **200 exact row links** independently re-resolved by CSV member, row number,
  identity field/value, raw row SHA256 and member SHA256.
- **116/116 frozen repository file hashes** unchanged.
- Researcher request bytes retain exact CRLF/SHA with a path-specific Git
  attribute; canonical JSON uses repository-standard LF.

Local ignored logs/receipts:
`results/hsa3_de_full_regression_20260923.log` and
`results/hsa3_de_independent_audit_20260923.json`.
These are Windows validations; no unperformed cross-machine run is claimed.

## Artifact receipts

Final ZIP:
`results/hsa3_de_elihu_seam_final_20260923_a_results.zip`

SHA256: `bff67a7d8b67b40134fe3a1114eb04f3d8c7a683f33442479fb36dfd1d1d3cab`.

Independent repeat:
`results/hsa3_de_elihu_seam_repeat_20260923_a_results.zip`
has the same SHA256 and all member bytes.

Synthetic:
`results/hsa3_de_synthetic_final_20260923_a_results.zip`

SHA256: `f26e3232693ba38a8a0770eeba9f0996696f3cf6e14bf8957999a9a870db7e53`.

Input ANA.0.3 SHA256:
`460b8f82764ea3c382c97ac6d382855a8a264272e7f152e60d133179f29c9ee1`.

Researcher request SHA256:
`b321a0ff3a9185ed9d20957c8b681c979dfdecf7fb0ebee1b92bf677282348f2`.
Results, ZIPs, logs and data remain ignored and are not committed.

## Remaining packet and repository files

`09_hsa3_remaining_seams_review_packet.md` marks D/E FROZEN and presents only
A/B/C/F/G for new adjudication. It includes exact original questions, primary
and participating unresolved IDs, evidence links, accepted positive/negative
constraints, relevant criteria dimensions and blank canonical researcher fields.
The frozen D/E constraints at the shared 38:1 node are context for F, not its
answer. The next step requires separately authorized researcher review; Q3 and
residual exact-direct-parent questions stay unresolved. R4.4 remains unstarted.

Changed repository files:

- [.gitattributes](../.gitattributes).
- [canonical human decisions](../config/hsa3_de_human_decisions.json).
- [stage configuration](../config/hsa3_de_job.json).
- [researcher source](HSA3_DE_RESEARCHER_SOURCE.txt).
- [specification](HSA3_DE_SPEC.md).
- [execution instructions](README_MILAL_HSA3_DE.md).
- [this validation report](HSA3_DE_VALIDATION_REPORT.md).
- [HANDOFF](HANDOFF.md).
- [Windows runner](../scripts/run_milal_hsa3_de_windows.ps1).
- [implementation](../src/milal_hsa3_de_seam_adjudication.py).
- [tests](../tests/test_hsa3_de_seam_adjudication.py).
