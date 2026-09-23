# HSA3-ANA.0.2 validation — 2026-09-23, computer A

Starting commit: `51d9c5e04b1d4ef148b401d48a69aa7d565e6d37`.
Scope: response-family evidence addendum and relation-specific criteria **draft**.
No researcher choice between Q2–Q5 alternatives is made. R4.4 remains unstarted.

## Baseline audit before implementation

The actual 0.1 ZIP was read and passed exact SHA256
`b7238ddcb0ee0940bd6a397a23bbef95a18da0dacb5af98e2b1b17396eb89294`, CRC,
78-member count and manifest checks. Four candidates remained UNADJUDICATED,
automatic_resolution=false and new_human_judgment=false. Q1–Q5 were present
and all canonical review fields were unchanged. Verified 62 verbal records,
two non-answer homonyms, 59 human judgments, 57 unresolved rows, zero new
judgments/relations, and all three HSA2-F closure decisions.

The real 0.1 pipeline was not regenerated. Its entire 78-member package remains
byte-identical beneath the new history directory. Test-only synthetic fixtures
use existing synthetic helpers; their smaller counts are not empirical outputs.

## Tests and integrity

| Check | Result |
| --- | --- |
| Python syntax validation | PASS for three new source modules and test module |
| New unit tests | 70 PASS, skip 0 |
| Full regression, including unchanged prior 737 tests | 807 PASS, skip 0 |
| Existing HR1 self-test within full regression | 22/22 gates PASS |
| ANA.0.2 synthetic self-test / Windows runner | 30/30 gates PASS |
| Actual BHSA / Windows runner | 30/30 gates PASS |
| Negative gate coverage | All 29 model gates mutated to FAIL; manifest corruption rejected |
| Frozen repository files | 97 exact hashes unchanged |
| BHSA native snapshot | Serialized clauses equal frozen 0.1 native snapshot |
| BHSA features | 70 exact loaded `.tf` hashes equal 0.1 and rechecked |
| Final ZIP | CRC PASS, 97 members |
| Nested/current manifests | 7/7 PASS |
| Independent source-row link audit | 155/155 exact row hashes resolve |
| Additional locators | 4 candidate and 2 seam-dependency hashes resolve |
| Independent actual process rerun | ZIP and every member byte-identical |
| Independent synthetic process rerun | Byte-identical, exercised in new tests |
| Human-facing inspection | Synthetic/actual cluster, continuation panels, criteria and blank Q1–Q5 inspected |

Commands: `python -m compileall -q` for the new Python files;
`python -m unittest discover -s tests -p test_hsa3_ana_response_family_addendum.py -q`;
`python -m unittest discover -s tests -q`; and the new Windows runner with
`-SelfTest` or explicit `-TfData` and distinct `-Out` paths.
DETERMINISTIC_RERUN computes equality of two independent model builds; the
separate empirical check additionally compares independent-process ZIP bytes.
No skipped, weakened or modified old regression tests.

## Actual linguistic results

BHSA path: `C:\Users\yisaa\text-fabric-data\github\ETCBC\bhsa\tf\2021`.
BHSA 2021, Text-Fabric 13.1.0; 10,912 Job words and 2,938 clauses.

Frozen verbal inventory remains **62**: **60** answer-sense plus **2** different
non-answer homonym occurrences. The new layer does not reclassify those records.

The broad nonverbal spelling/root screen retains **32** candidates. Exactly
**2** are confirmed nominal answer-family candidates:

| Reference | Word / clause | BHSA identity | Classification |
| --- | --- | --- | --- |
| 32:3 | 343853 / 499631 | M<NH=/; M<NH; answer; subs | CORE_ANA_NOMINAL_COGNATE |
| 32:5 | 343876 / 499636 | M<NH=/; M<NH; answer; subs | CORE_ANA_NOMINAL_COGNATE |

Both have **root unavailable**. Inclusion is based on explicit lexical/gloss/POS
convergence, not fabricated root data. The 0.1 NO_ANA focus records remain intact.
The new crosswalk explicitly combines NO_VERBAL_ANA_AT_THIS_WORD with the nominal
category. The other **30** screen hits are NON_RESPONSE_SIMILAR_FORM; no actual
POSSIBLE_ANA_NOMINAL_COGNATE remains in this corpus run.

The Hebrew lex_utf8 spelling **מענה occurs four times**: the two answer nouns
above and **37:8 / 38:40** with distinct `M<NH/`, gloss `hiding place`, root `<WN`.
Those two are excluded from the answer family. Other root `<NH` screen hits
(time, poverty/humble, because-of) demonstrate why root identity alone is unsafe.

The whole-book normalized שוב **verbal** scan yields **39 occurrences**:
38 `CWB[` and one distinct `CWB=[` at 42:10. Raw lexemes are never merged.

| Provisional construction reading | Count |
| --- | ---: |
| SEMANTIC_REPLY_SHWB | 7 |
| RETURN_RESTORE_SHWB | 16 |
| OTHER_SHWB | 4 |
| UNRESOLVED_SHWB | 12 |

Reply readings occur at **13:22, 31:14, 32:14, 33:5, 33:32, 35:4, 40:4**.
They are transparent contextual/construction readings, not finalized lexical
sense adjudications or new response relations. In particular 20:2 remains
UNRESOLVED_SHWB. Return/restore and other constructions supply actual negative
controls, including Hiphil forms; Hiphil is not equated with reply.

32:14 word **343981**, clause **499669**: hif/impf, first-person subject marking,
third-person object suffix, local negation and באמריכם utterance complement
(word **343979**, `>MR/`). These support the provisional SEMANTIC_REPLY_SHWB
reading. The suffix referent is not computationally resolved to Job; that
contextual connection and friends-failure relation remain review evidence.

33:13 retains **ANA:W:344161**, clause **499725**, with its unresolved subject.
33:14 word **344165**, clause **499726**, has `DBR[` with explicit אל subject.
It is one **POSSIBLE_RESPONSE_REFRAMING** context candidate, UNADJUDICATED and
automatic_resolution=false. It is neither core ANA nor a semantic-neighbor
lexeme, and it does not increase the four structural-candidate count.

## Cluster and unchanged hypotheses

32:1–33:14 contains **14** separately layered rows: **9 verbal**, **2 nominal**,
**2 semantic reply-neighbor** (32:14 and additionally discovered 33:5), and
**1 local reframing candidate**. All requested loci are included in canonical
order. 32:13 stays local context only. Continuation controls include 34:1,
35:1, 36:1 (NO_ANA / ADD_SPEECH), 37:24 and 38:1. Chapter/local-window
counts are unweighted and imply no structural-strength conclusion.

ANA-C1–C4 are copied verbatim. C4 additionally carries the separate label
ELIHU_RESPONSE_ROLE_INTERVENTION, refinement_status=UNADJUDICATED.
POSITIONAL_ONLY and RESPONSE_ROLE_INTERVENTION are unselected alternatives.
Candidate count **4**, new human judgments **0**, new structural relations **0**.
The 59 frozen human judgments, 57 unresolved rows, A–G review fields, 3:2 control
and three 31:40 HSA2-F relations are byte-preserved. All prior analytical cores
remain unchanged. 37:24 adjacency never becomes an antecedent or parent.

## Criteria draft

**7 dimensions:** BOUNDARY_EXISTENCE, STRUCTURAL_FUNCTION, SAME_LEVEL_RELATION,
PARENTAGE_CONTAINMENT, CLOSURE_TARGET, OVERLAY_RESPONSIO, RESPONSE_RELATION.
**24 codes:** 16 positive/constraining evidence categories and 8 forbidden or
insufficient sole bases. **21** exact-ID frozen judgment crosswalks cover all
requested representative cases. Source records and historical rationale remain
visible; illustrative draft code associations do not invent past human reasoning.
There are no numerical weights, global priority ranking or automatic decisions.
BHSA mother is never converted to MILAL literary parentage.

## Final artifacts and pending review

Actual: `results/hsa3_ana_0_2_response_family_final_20260923_a_results.zip`

SHA256: `00c3c052f6133456d371b2736261e469b69ba5ad91891d0ccf44d6b59a90aa5d`.

Independent repeat:
`results/hsa3_ana_0_2_response_family_final_repeat_20260923_a_results.zip`
has exactly the same SHA256 and all 97 members match byte-for-byte.

Synthetic: `results/hsa3_ana_0_2_synthetic_final2_20260923_a_results.zip`

SHA256: `49f015e532a5163212e2be47800b42cceb0812b7984bcfc9266fb6a5fb9bf381`.

Earlier development runs are superseded by these final artifacts. All outputs,
logs and corpus data remain local/ignored. Cross-machine archive byte equality
is not claimed because exact local paths are deliberately part of provenance.

Researcher review remains:

- Q2: accept 31:40→32:1 POST_CLOSURE_TRANSITION? Nominal answer absence is
  surrounding context, not a new direct-closure decision.
- Q3: accept 31:35→38:1 LONG_DISTANCE_RESPONSE? No new direct fulfillment
  proof or computational שדי=יהוה identity is supplied.
- Q4: accept 32:1↔38:1 CONTRASTIVE_ANA_FRAME? Compare cessation, 32:3/5
  answer absence and later directed answering; recurrence alone is insufficient.
- Q5: POSITIONAL_ONLY or RESPONSE_ROLE_INTERVENTION, or unresolved/insufficient?
  Evaluate 32:12/14–17/20 and 33:5/12–14 alongside the 3:2 counterexample.

All Q2–Q5 remain UNREVIEWED. Their allowed outcomes include a source-supported
human relation, UNRESOLVED or INSUFFICIENT_EVIDENCE. No choice has been made.
