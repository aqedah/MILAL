# HSA3-ANA.0.2 — Response Lexical-Family Addendum

Includes the **draft**, dimension-specific HSA Adjudication Criteria Registry.
Baseline: `51d9c5e04b1d4ef148b401d48a69aa7d565e6d37` (HSA3-ANA.0.1 complete).
The researcher authorized implementation, synthetic and actual BHSA execution,
independent rerun, and commit/push after successful tests. No Q2–Q5 or HSA3 A–G
adjudication is authorized; R4.4 is not started.

## Immutable input

The exact 0.1 ZIP is pinned by `config/hsa3_ana_0_2_job.json`:
`results/hsa3_ana_0_1_response_frame_final_20260923_a_results.zip`, SHA256
`b7238ddcb0ee0940bd6a397a23bbef95a18da0dacb5af98e2b1b17396eb89294`.
Check SHA, CRC, manifest, 78 members, metadata, all gates, four unadjudicated
candidates, Q1–Q5 and their blank review fields, zero new judgments/relations,
62 verbal records including two non-answer homonyms, 59 human judgments,
57 unresolved rows and the three HSA2-F closure relations **before extraction**.
Any mismatch stops execution. No alternative run or fuzzy linkage is allowed.

The new configuration pins 97 existing source/config/test/document/runner files.
The whole original 78-member package is copied byte-for-byte beneath
`history/ana_0_1/`. The real 0.1 pipeline is neither rerun nor edited. Existing
synthetic helpers may build a synthetic-only baseline fixture for portable tests;
it is explicitly marked and never substituted for the real frozen input.

Reuse 0.1's native BHSA loader, requiring BHSA 2021 and Text-Fabric 13.1.0.
The fresh native clause serialization and loaded feature hashes must equal the
frozen 0.1 snapshot. Recheck all source hashes before publishing. No duplicate
BHSA loader, machine-specific Python default or network data download is added.

## Four separate evidence layers

1. CORE_VERBAL_ANA: exact cross-references to all frozen 0.1 records, including
   explicit non-answer flags. Preserve original IDs, classifications and source rows.
2. CORE_ANA_LEXICAL_FAMILY: whole-book nonverbal candidate screen using
   normalized lex_utf8 containing ענה or recorded root `<NH`. This is a broad
   screen, **not** an automatic family assertion. Preserve every hit, including
   non-nominal or unrelated root/spelling false positives.
3. SEMANTIC_RESPONSE_NEIGHBOR: whole-book verbal normalized שוב screen,
   retaining both `CWB[` and `CWB=[`. Keep all senses and uncertain cases.
4. RESPONSE_CONTEXT_REFRAMING: the specifically requested 33:13–14 local
   context candidate only; דבר is not promoted to either preceding lexical layer.

Normalized spelling is used only for broad candidate discovery, never to merge
identities. Raw lex, lex_utf8, lex0, root, morphology and source-node IDs remain.

### Nominal family decisions

CORE_ANA_NOMINAL_COGNATE requires exact `M<NH=/`, lex0 `M<NH`, gloss `answer`
and nominal POS. Root is **unavailable** for these nouns: do not manufacture a
root/etymology. The transparent basis is lexical identity + gloss + morphology,
with local negative/existential context supplied for corroboration.
POSSIBLE_ANA_NOMINAL_COGNATE is retained for root-screen hits with a compatible
or unknown response gloss but insufficient exact lexical evidence.
Other screen hits are NON_RESPONSE_SIMILAR_FORM, meaning not included as a
confirmed response-family member. Same root is not sense identity.

In particular `M<NH/` / hiding place / root `<WN` is distinct despite the same
Hebrew lex_utf8 string. Time, poverty/humble, because-of and other screen hits
are not silently dropped. Every row preserves source words, clause/atoms,
phrase functions, local subject/object/complements, pronominal references,
negative/existential evidence and neighboring verbal IDs. Neighbors are source
order only, never inferred antecedents. Raw native clauses preserve the complete
nominal/construct/suffix context; no possessor identity is guessed.

32:3 and 32:5 remain NO_ANA in 0.1. Their new crosswalk can say
NO_VERBAL_ANA_AT_THIS_WORD + CORE_ANA_NOMINAL_COGNATE simultaneously.

### SHWB construction readings

Semantic classifications are provisional construction descriptions, not new
human judgments. Hiphil alone never means reply. Rules use lexical/morphological
and explicit phrase data; BHSA mother is only retained as corroborating context.

- SEMANTIC_REPLY_SHWB: hif with an explicit utterance object/complement; or hif
  imperative with first-person object suffix and immediate-verse speech/turn-
  preparation evidence; or first-person hif, personal suffix and interrogative
  מה object. The exact lexical sets are configured. No locus whitelist detects replies.
- RETURN_RESTORE_SHWB: explicit configured spatial source/destination or
  restored object; includes the separately identified 42:10 lexeme.
- OTHER_SHWB: explicit wrath/breath/spirit construction outside the reply rules.
- UNRESOLVED_SHWB: the permitted construction evidence does not safely
  distinguish the contextual sense. Preserve the occurrence for review.

32:14 records hif/impf, personal object suffix, negation, באמריכם utterance
complement, complete immediate verse and the separate friends-failure cluster.
The suffix's referent is unresolved computationally. Job as contextual target
and the friends' inability are review evidence, not an automatically resolved
participant, RESPONSE_TO edge or structural relation.

### Local context and distribution

33:13 retains its exact ANA ID and unresolved subject; 33:14 has אל + דבר.
Emit POSSIBLE_RESPONSE_REFRAMING, UNADJUDICATED, automatic_resolution=false.
The local context candidate is not a fifth structural candidate. No whole-book
דבר response lexicon is created; 2:13 supplies an unrelated speech control.

Output the 32:1–33:14 cluster in canonical reference/word order, including
all requested loci and any additional discovered response-neighbor occurrence
(such as 33:5). Preserve 32:13 as context without lexical promotion. Include
34:1, 35:1, 36:1, 37:24 and 38:1 in continuation panels.
Chapter and local-window distributions keep verbal, answer-sense, non-answer
homonym, nominal-family, semantic-neighbor and context counts separate.
No weighted sum or strongest-structure conclusion is permitted.

## Candidate addendum and criteria

Preserve ANA-C1–C4 verbatim. Add only source-linked evidence and distinguish
direct evidence from contextual evidence. C1 receives no invented direct closure
evidence; C2 receives context, not new proof of fulfillment or שדי=יהוה.
C3/C4 expose local nominal absence and explicit response-role language.
C4 may additionally carry ELIHU_RESPONSE_ROLE_INTERVENTION as an UNADJUDICATED
refinement label. POSITIONAL_ONLY and RESPONSE_ROLE_INTERVENTION remain
unselected alternatives. All automatic relations/parent fields remain empty.

The criteria registry has seven dimensions: BOUNDARY_EXISTENCE,
STRUCTURAL_FUNCTION, SAME_LEVEL_RELATION, PARENTAGE_CONTAINMENT, CLOSURE_TARGET,
OVERLAY_RESPONSIO and RESPONSE_RELATION. Twenty-four evidence codes define
admissibility and insufficiency, never weights, global priorities or sufficiency.
The original records of 21 representative frozen judgments are crosswalked by
ID/row/hash. Code associations are explicitly draft illustrative mappings, not
retroactive reconstruction of unstated human reasoning. Preserve original
linguistic_basis/reasoning and methodological_note beside each mapping.

See [registry methodology](HSA_ADJUDICATION_CRITERIA_REGISTRY.md).
BHSA clause/clause_atom syntax is not MILAL discourse/literary hierarchy.
Morphology/phrases/clauses provide primary linguistic evidence; mother/tab/
pargr/rela/code are distinct validation/corroboration evidence. No automatic
literary parent derives from syntactic mother. Marker selection is theory-informed;
adjudication remains outcome-open. The same marker can have different relevance
to different relation questions.

## Outputs and validation

Required outputs 01–14, metadata 90 and manifest 99 follow the user request.
Additional 15 native clauses, 16 unchanged review questions and 17 continuation
panels preserve inspectability. Human-review schemas come from the canonical
import; no duplicate REVIEW_FIELDS definition. SEAM_D/E receive dependency
addenda only. All A–G and Q1–Q5 source review fields remain unchanged.

Run syntax, new unit tests, all 737 prior tests, synthetic self-test and packet
inspection before actual execution. Every gate has a negative mutation, including
manifest corruption. DETERMINISTIC_RERUN compares two independent model builds;
separately compare independent-process ZIPs and every member. Technical PASS
does not settle Q2–Q5. Results/data/logs remain ignored by Git.
