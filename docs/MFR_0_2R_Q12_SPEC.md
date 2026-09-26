# MFR.0.2R-Q1.2 — independent configuration and reference witnesses

Baseline: 1bd0cb64390423223acdddcf130733f8f5cc880c. The exact researcher
request is MFR_0_2R_Q12_RESEARCHER_SOURCE.txt; the subsequent authorized
clarification is MFR_0_2R_Q12_CLARIFICATION.md. Q1/Q1.1 are frozen.

## Operational contract (GENERALIZED_FOR_MILAL)

Job is the sole primary analysis. Raw candidate IDs, original rule matches,
source identities and historical human judgments are preserved. No new rule
match is inferred from a configuration. Family membership is not binding and
is not textual-level identity. Candidate edges and variants are not inputs to
profile/configuration extraction.

Profiles retain every source word and phrase, morphology, ordered grammatical
functions, speech predicates, time/location, reference forms and source hashes.
Each clause supplies a minimal configuration. A configuration extends across
adjacent source words only through exact native subordinate/speech-complement
annotations; it stops at the first gap or unbound continuation. This is a
documented operational subset of independently observable configurations, not
a universal definition of textual units. Native annotations remain database
evidence, not an accepted MILAL hierarchy.

Families are hashes of ordered compositional core shapes: clause type,
predicate class/morphology, core grammatical-function order and subordinator
forms. Time/location multiplicity and lexical fillers remain distinct observed
profiles within a family. Whole-profile equality is not required. Predicate
lexemes, including speech formulas, remain visible in observed profiles.
Different sequence lengths remain distinct in this operational subset.

Positive configuration witnesses require disjoint independently bounded units,
corresponding internal positions, structural content beyond same clause type,
and a researcher-confirmed pair-binding witness. The implemented anchor subset
is explicit nominal lexemes in corresponding grammatical functions. Frame
witnesses additionally preserve both phrases and their formal differences;
shared generic TIME/LOCATION flags cannot bind a pair. Opening correspondences
use SB06; embedded corresponding positions use SB11. These qualify only an
already present compatible relation-rule match. Surface positions do not assign
canonical levels. Deferred Oosting clause binding remains a prior blocker.

Reference search preserves all preceding explicit nominal candidates in subject,
object and complement functions (Subj/PreS/Objc/PreO/Cmpl/PreC) compatible with
morphology or lexical recurrence, without a distance cutoff. This is the
operational antecedent-search subset; every other source word/phrase remains
available in the frozen observations and profiles. Search includes gender/number-
compatible nominals whose person is NA; the missing person is recorded unchanged,
never imputed as third person. This is search evidence only. Unique search
results are UNIQUE_SURFACE_CANDIDATE, not referent identification. EXACT_NATIVE
requires an explicitly typed antecedent annotation with exact word endpoints;
BHSA clause attachment or a `Rela` relation alone is not such an annotation.
The frozen input currently supplies no such referential-semantic type. The
SB02/SB03/SB10 adapter can consume it when genuinely provided; synthetic typed
fixtures test the architecture. New empirical referent resolution must remain
unresolved absent such evidence. SB03 additionally requires independently
bounded source-unit membership; provisional reachability cannot supply it.

SB12 evaluates only positively qualified outcomes using frozen single-mother,
strict/equal-level and cycle constraints. It cannot create/upgrade an edge,
select a mother or choose a canonical hierarchy. Symbolic unselected edges
mean UNDECIDED. Pivots require two positively distinct coherent assignments.

## Execution and validation

All source/Q1/Q1.1 ZIP hashes, archive integrity and extracted manifests are
verified. Job runs blind before external control loading. External controls
reuse only the exact Q1.1 fixture evidence and original candidate matches.
No full Pentateuch or other-book candidate generation is permitted.

Syntax, focused tests, synthetic self-test and full regression with zero skips
precede real execution. Two independent runs must have byte-identical manifests
and deterministic ZIPs. All computed gates have negative mutations. H0.1 does
not start automatically. Technical validation is not scholarly acceptance.
