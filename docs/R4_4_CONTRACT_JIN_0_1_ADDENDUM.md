# Jin single-mother methodological addendum

R4.4-CONTRACT.JIN.0.1. One explicit human methodological decision:
`JIN_SINGLE_MOTHER_PRINCIPLE_ADOPTED_FOR_REVIEW`.
Authority: [exact researcher instruction](R4_4_CONTRACT_JIN_0_1_RESEARCHER_SOURCE.txt),
sections 1 and 17. No node-specific mother judgment is supplied or generated.

MILAL retains a layered typed graph as its overall representation, but textual
hierarchy is a distinct layer governed by a single-mother principle.
Every textual daughter in the textual-hierarchy layer must ultimately have one
direct textual mother, except a separately adjudicated textual root.
Composition, transition, overlay, same-level correspondence and technical
navigation cannot substitute for a missing textual mother.
The former judgment that a direct parent was not required was a statement about
sufficiency of the layered representation; it does not by itself exempt a textual
daughter from the single-mother principle.
Historical judgments are preserved; methodological correction is represented
through an append-only superseding layer.

## Methodological source and verification boundary

Gyusang Jin, *Investigating the Text-hierarchical Structures and Composition of
Numbers*, methodology §3.2.9. The researcher supplies the principle: analysis may
retain multiple candidate mothers, but the final hierarchy selects one mother
for each daughter; one mother can have several daughters. Syntactic and linguistic
correspondence guides selection, rather than a nearest-preceding rule.

The [VU institutional thesis record](https://research.vu.nl/en/publications/investigating-the-text-hierarchical-structures-and-composition-of/)
was checked on 2026-09-24 and confirms the author, title, 2021 PhD and syntactic
methodology. Its linked thesis PDF returned HTTP 403 through the research tool.
Consequently §3.2.9 and the detailed principle above are attributed to the
researcher's supplied source summary, not falsely claimed as independently
verified PDF quotations. No external PDF is added to the repository.

A repository search of docs/config found no pre-existing Jin methodology summary
apart from unrelated hash substrings. No separate user thesis-methodology file
was supplied for this task. Cross-references to existing MILAL methodological
state: [LAYER.0.2](HSA3_LAYER_0_2_SPEC.md),
[historical contract](R4_4_CONTRACT_0_1_SPEC.md) and
[architecture audit](R4_4_CONTRACT_0_1_ARCHITECTURE.md).
These are MILAL context, not substitutes for Jin's thesis text.

## Distinct scopes and unanswered questions

`STRICT_JIN_CLAUSE_HIERARCHY` concerns actual clauses/clause atoms.
`MILAL_MACRO_TEXTUAL_HIERARCHY` concerns the registry's anchored macro units,
onsets and closures. They are not silently equated. JIN-Q0 / revised Q8 asks
whether to extend the principle to the latter. JIN-Q1/Q2 and revised Q9 ask
about a separately adjudicated whole-Job textual root. All remain UNREVIEWED.
Technical JOB_BOOK is not such a root. Mother absence alone creates no root
candidate. Native evidence at 1:1 does not create a canonical textual unit.

All seven canonical layers remain: TEXTUAL_HIERARCHY, TEXTUAL_SAME_LEVEL,
COMPOSITION_GROUPING (the established name for composition), TRANSITION,
OVERLAY_RESPONSIO, NEGATIVE_CONSTRAINT and TECHNICAL_NAVIGATION.

The historical 57 UNRESOLVED records and their 57 false additional-review flags
remain unchanged. New applicability and review flags answer a different question.
SM1–SM7 are audit proposals, not new human judgments. P3's six historical rows
must be checked by actual kind, rather than treating six rows as six aliases.

## Existing relation semantics

`src/milal_r4_3_hierarchy_scaffold.py::parents` recognizes CHILD_OF from source
daughter to target mother, and HIERARCHICALLY_ABOVE from source mother to target
daughter. Distinct mother IDs, not relation-row multiplicity, determine counts.
CONTINUES_WITHIN and DIRECT_LOCAL_CLOSURE are placement/closure evidence, not
accepted direct mothers. Unknown future types are AMBIGUOUS_MOTHER_SEMANTICS.
Neither same-level reciprocity nor membership creates a mother.

The candidate pool retains explicit placement/closure and, where available,
same-level evidence with an already known sibling mother. All candidates are
UNADJUDICATED, with exact relation receipts. This conservative pool is not an
exhaustive clause-morphology or referential analysis. It neither picks a mother
nor upgrades placement into a mother edge. A zero pool is a limitation of current
evidence/rules, not proof that no possible mother exists.

The historical contract readiness is preserved. Current readiness is
`BLOCKED_PENDING_SINGLE_MOTHER_COMPATIBILITY_REVIEW`. Revised Q1–Q9 require
researcher review before any subsequent consumer implementation.
