# HSA3-ANA.0.1 — Job 31:40 Post-Closure and ענה Response-Frame Audit

Authorized baseline: `f1292ba51b90fd545069741ee5ccce3d63d9704a` (HSA3-PREP).
This is a surface-evidence audit before HSA3 A–G human review. It is not HSA3
adjudication or R4.4. The user authorized implementation, synthetic and actual
BHSA 2021 validation, independent rerun, and commit/push after passing tests.

## Frozen constraints and inputs

`config/hsa3_ana_job.json` pins 89 prior repository files and the accepted
HSA3-PREP ZIP (`06e41a935d1ccb18eed1b1773d4ca04a493a097533e36cf2875f741fa116cc77`).
Existing PREP/R4.3 loaders verify the R4.3 package and ten accepted upstreams;
with PREP this audit verifies twelve packages, CRCs/manifests and exact hashes.
No substitutes, reconstructed registry, fuzzy linkage or original ZIP rewriting.
All 62 PREP members are preserved under `history/hsa3_prep/`.

HSA1/HSA2/HSA2-F human bytes and all frozen analytical cores stay unchanged.
HSA2-F retains 31:40 → 29:1 DIRECT_LOCAL_CLOSURE, → 27:1 NO_DIRECT_RELATION in
DIRECT_CLOSURE_TARGET, and → POST_DIALOGUE_JOB TERMINATES_ENCLOSING_GROUP in
HIGHER_ORDER_TERMINAL_EFFECT. Job 3:1 HIERARCHICALLY_ABOVE 3:2 and 3:2
CONTINUES_WITHIN 3:1 remain accepted controls. All 57 unresolved rows and
seven A–G review records remain unchanged and unadjudicated.

## Native extraction

Reuse the frozen MR1 BHSA loader, requiring 2021 and Text-Fabric 13.1.0. Add
gloss, lex0, mother, rela and code features without changing MR1. Record every
loaded `.tf` file's exact path/SHA256 and recheck it before publication. No
user-specific path is embedded in Python. Standard TF binary-cache creation may
be needed on a fresh computer; `.tf` source content is never edited.

Scan every Job word through native clause membership, verifying complete,
unique coverage against the book's word nodes. Select `lex_utf8 == ענה`; do not
select by verse whitelist. Preserve raw lexical identifiers. `<NH[` is answer;
`<NH=[` is the independently identified be-lowly homonym. Unknown ANA lexical
identity stops with an explicit error instead of being assigned a sense.

Every occurrence preserves word/clause/clause_atoms, Hebrew surface, its word's
own verse reference, lex/lex_utf8/lex0/gloss/root availability, morphology,
clause type/domain, explicit subject/object/complement source phrases, suffix
features, CSF clauses and MR1 source event. Missing root is reported as absent,
never reconstructed. Missing required feature columns stop execution.

Clause snapshots retain exact words, phrases and raw BHSA mother targets;
mother targets outside the clause map are not guessed into clause identities.
Verse display sorts native word IDs, preserving discontinuous-clause word order.
Previous/following MR1 top-level speaker events are ordered context only. Neither
speaker identity nor antecedent is assigned by nearest opening or adjacency.
Unresolved pronominal identity remains UNRESOLVED even when an event is explicit.

## Construction classification

Classification is a reproducible surface description, not a semantic or human
hierarchy judgment. Priority is the following:

1. NON_ANSWER_HOMONYM: explicit different BHSA lexeme, retained in inventory.
2. DIRECTED_ANA_CSF: answer-wayyiqtol plus explicit subject followed by an
   אמר-wayyiqtol clause, with a proper-name object.
3. DIALOGUE_TURN_CSF: that formal construction with exact MR1 event identity
   in an accepted cycle-member speech node. Accepted namespace wrappers
   `MR1:` / `R4.1:MR1:` are explicit identities, not Hebrew/reference matching.
4. FORMULAIC_CSF: remaining formal answer/say construction. No semantic
   RESPONSE_TO is inferred from it, especially at the frozen 3:2 control.
5. ANSWERING_CESSATION: infinitival answer with an explicit mother-clause
   containing שבת. Preserve governing subjects and the answer's own object.
6. NEGATED_OR_WITHHELD_RESPONSE: negative lexical evidence in the clause or
   explicit mother-clause chain. This records syntax/context, not a proof of
   semantic negation scope; raw links and negation nodes remain inspectable.
7. RESPONSE_REQUEST: third-person impf answer with first-person suffix and
   explicit שדי subject in the מי יתן wish context. This configured construction
   is not a universal request detector; impf alone is not a jussive feature.
8. SELF_DECLARED_RESPONSE: first-person impf with explicit אף אני construction.
9. FIRST_PERSON_DIRECTED_RESPONSE: first-person impf with second-person suffix.
10. FIRST_PERSON_RESPONSE_PROSPECT: other first-person impf; conditional,
    interrogative or optative force is deliberately not decided.
11. OTHER_ANA: all remaining answer occurrences, preserving their full evidence.

No verse/count is a detection rule. Job-specific loci are presentation and
regression controls. Formal construction, reviewed dialogue context and a
specific semantic-response antecedent are separate fields. All automatic
response/parent fields remain empty; syntax does not supply long-distance identity.

## Focus and hypotheses

The focus configuration includes 2:13 silence, 3:1–2, 31:35/40, 32:1–6,
32:11–17, 33:12–14, 34:1, 35:1, 36:1, 37:24 and 38:1/40:1/3/6/42:1.
Every other actual ANA occurrence in chapters 38–42 is added from the inventory.
36:1 must retain verified NO_ANA / ADD_SPEECH. Non-ANA response-role language
at 32:14 (שוב) and 33:14 (דבר) remains in full source panels. Elihu's 32:12–17
and 33:12–14 evidence is not reduced to the 32:6 CSF. 33:13's implicit subject
is not promoted to a named identity; 32:17's BHSA hif is not normalized away.

Exactly four user-supplied hypotheses are emitted, all UNADJUDICATED:

| ID | Endpoints | Candidate type |
| --- | --- | --- |
| ANA-C1 | 31:40 → 32:1 | POST_CLOSURE_TRANSITION |
| ANA-C2 | 31:35 → 38:1 | LONG_DISTANCE_RESPONSE |
| ANA-C3 | 32:1 → 38:1 | CONTRASTIVE_ANA_FRAME |
| ANA-C4 | 32:1–38:1 interval | ELIHU_WITHIN_ANA_RESPONSE_INTERVAL |

31:40 is a closure context, not a new parent. שדי and יהוה are not computationally
equated. C4's positional interval is not hierarchical containment. No inclusio,
fourth-friend role, RESPONSE_TO, sibling or parent is asserted. Lexical recurrence
≠ semantic response ≠ discourse relation ≠ hierarchical parentage.

ANA-Q1 displays the frozen 3:2 counterexample without reopening it. Q2–Q5 ask
about C1–C4; allowed outcomes are HUMAN_SUPPLIED_RELATION_WITH_SOURCE,
UNRESOLVED or INSUFFICIENT_EVIDENCE. All canonical REVIEW_FIELDS are imported
from the prior canonical definition, blank except UNREVIEWED. A typed SEAM_D/E
addendum points to these pending questions without editing the original cases.

## Outputs and validation

Outputs 01–10 follow the requested inventory/focus/classes/candidates/negative
controls/evidence links/two Markdown reports/dependency/gates schema. Additional
11 native clauses, 12 full word scan, 13 accepted MR1 context and 14 blank review
questions make extraction and links independently inspectable. Metadata 90 records
all source receipts and counts; manifest 99 covers every other member. Original
human provenance remains accessible in nested immutable histories.

Syntax, new tests, full regression, synthetic self-test and human-facing synthetic
inspection precede actual BHSA execution. Every computed gate has a negative
mutation, including manifest corruption. Validate actual source snapshots, frozen
bytes, all manifests/ZIP CRCs and an independent process rerun. Technical PASS
does not adjudicate a research hypothesis. Do not begin R4.4.
