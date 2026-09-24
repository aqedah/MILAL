# R4.4-CONTRACT.JIN.0.2 — independent linguistic audit

Baseline `178bea7fd73634c00a68828eb533c91991a3d69e`.
Authority: [exact researcher request](R4_4_CONTRACT_JIN_0_2_RESEARCHER_SOURCE.txt).
This append-only stage is an analytical candidate audit, not an R4.4 consumer,
accepted hierarchy, mother selector or new human judgment. The request authorizes
synthetic validation, actual BHSA 2021 execution, independent rerun and commit;
push follows the repository approval workflow. Prior cores and outputs stay frozen.

## Method and scope correction

MILAL does not use prior researcher judgments to discover the paratactic or
hypotactic relation that those judgments are supposed to establish.
Linguistic evidence is extracted first, relation candidates are generated second,
and human adjudication follows third.
Human judgments are used after blind discovery for comparison, validation and
final adjudication, not as discovery features.
Parataxis and hypotaxis are both possible between clauses of the same type and
between clauses of different types; clause-type identity alone does not determine
the relation. A hypotactic daughter ultimately requires one mother, but the code
does not select that mother automatically when multiple linguistically supported
candidates remain. This supersedes the blanket application of JIN.0.1's textual
node requirement as an open methodological question, without rewriting JIN.0.1.

The procedural Jin §3.2.9 / §3.2.9.5 account is researcher supplied. The exact
operational bundles below are inspectable MILAL candidate rules, not a claim to
reproduce an independently verified Jin executable classifier. See the previous
[source-verification boundary](R4_4_CONTRACT_JIN_0_1_ADDENDUM.md).

## Process boundary and sources

Preparation reads only the pinned JIN.0.1 ZIP for target selection and emits
neutral JT IDs plus book/chapter/verse. This explicitly authorized inventory
projection is separate from discovery. Human identifiers and labels do not pass
into the Phase A subprocess. The post-blind phase independently reproduces this
projection and verifies all 49 neutral references against the source artifact.

Phase A is a separate executable with a CPython audit hook enforcing an exact
read-file allowlist and a MILAL import allowlist. It has no historical-helper or
human-registry import. Allowed data: neutral target JSON, neutral linguistic rule
JSON and the explicitly named TF files below (or constructed raw synthetic JSON).
No directory-wide TF feature loading, caches or native hierarchy are read.
Physical source paths are recorded in the external execution log; deterministic
logical source IDs and byte hashes are recorded in 06 and Phase A metadata.

Raw TF files: otype, oslots, book, chapter, verse, typ, function, domain, txt,
lex, lex_utf8, g_word_utf8, trailer_utf8, sp, pdp, vt, vs, ps, gn, nu,
prs_ps, prs_gn, prs_nu. Each must declare version 2021.
The explicit config maps the display book name `Job` to the attested Latin
`book.tf` value `Iob`; lookup requires `otype == book` because the book-name
feature also occurs on chapter/verse nodes. No fuzzy name fallback is used.
Source identifiers, whole-book word partition and exact overlapping verse-to-clause/atom anchors
are retained. A target denotes every raw clause intersecting that locus, not a
human-selected representative clause. The Hebrew rendering uses the explicit
ketiv g_word_utf8 + trailer_utf8 convention; no qere substitution is inferred.

Raw parsing follows the official [TF file format](https://annotation.github.io/text-fabric/tf/about/fileformats.html)
and [implicit-node conventions](https://annotation.github.io/text-fabric/tf/about/optimizations.html).
The [BHSA feature reference](https://etcbc.github.io/bhsa/features/0_home/)
documents the source-feature distinction. The direct parser is deliberate: it
cannot implicitly load mother/tab/pargr/rela/code or auxiliary derived hierarchy.
Text-Fabric library execution is not a dependency of this new reader.

Phase A finalizes files 01–06, metadata and rule config, then hashes every member
in 07_blind_discovery_manifest.csv. Phase B verifies this freeze before opening
the historical ZIP, config or native hierarchy. The coordinator checks the same
freeze before launching B and verifies the Phase A directory byte-for-byte
afterward. Event order and separate source inventories are included in output.

Historical ZIP: `results/r4_4_contract_jin_0_1_real_final_20260924_b_results.zip`,
SHA256 `895264dfd4a11efc147464c393933ed8650e4ad146da42fa067a1c9e9eb30d5e`.
All 278 members remain under history/r4_4_contract_jin_0_1/; 188 frozen repository
pins are verified. Real mode never replays historical analytical stages.

## Evidence and candidate universe

For every neutral target clause, scan **all earlier non-overlapping clauses in
Job**, not the nearest clause or opening. Also inspect up to three following
clauses as explicit forward syntactic context, uniformly for every target.
The two scan populations are counted separately. Forward pairs do not assert
that the target is a daughter. No pair is eligible from adjacency alone.

Retain every pair with at least one implemented linguistic trigger: matching
type, lexical/morphological/formula recurrence, repeated constituent configuration,
explicit participant surface recurrence, qualified pronominal/subordination,
temporal/locative or speech-embedding evidence. Eligibility is not support.
Unsupported scanned pairs contribute to the NO_LINGUISTIC_SUPPORT count; all
eligible pairs, including insufficient ones, remain in the machine outputs.
No score, weight, rank, top-N truncation or automatic best candidate exists.

Raw features include clause/atom and word identity, surface, type/domain/txt,
lexemes, verb stem/form/PNG, phrase functions and positions, subjects, objects,
complements, adjuncts, temporal/locative phrases, suffix PNG and pronouns.
Separate derived fields expose explicit rule tests. Morphological compatibility
never resolves participant identity. NA/blank PNG never matches as positive
reference evidence. Implicit subject identities remain UNRESOLVED.
The `domain.tf` header explicitly defines `?` as Unknown. It contributes no
positive domain correspondence/shift or say-to-quotation embedding evidence.

Formula atoms are ordered lexical subsequences anchored in the current clause,
within a recorded three-clause context: answer/say, add/proverb/say, open/mouth,
and be/day. These are raw lexical configurations, not historical CSF or macro
labels. Both the formula context and current clause are retained. Formula names
and marker lexemes live in the neutral rule configuration.

## Boolean candidate bundles

P1 requires all of: main-clause-compatible finite/nonverbal form, same known
domain, matching formula or matching verb-lexeme/stem/form plus constituent and
phrase-function arrangement, non-NA verbal PNG correspondence, and explicit
subject recurrence or temporal/locative correspondence. An explicit relative,
infinitive dependency, contextual causal/conditional marker or speech-domain
embedding blocks P1. Clause type is neither sufficient nor an exclusion.

Hypotaxis bundles require one of:

- H1: relative marker >CR and a local explicit nominal antecedent candidate.
- H2: infinitive construction and local finite antecedent with shared argument
  surface or compatible verb PNG.
- H3: polysemous conditional/causal marker (>M/KJ/LM<N) with local reference or
  morphological correspondence. This is contextual candidate evidence, never a
  disambiguated causal interpretation.
- H4: local explicit nominal antecedent and matching non-NA pronoun/suffix PNG.
  Referent identity remains unresolved.
- H5: temporal phrase, non-wayyiqtol finite form and local participant recurrence,
  as a background-dependency candidate.
- H6: local say verb followed by a shift into quoted domain, as an embedding
  candidate. Domain annotation is permitted raw input, not a human seam decision.

Local means up to three preceding clause positions for these dependency probes;
the complete predecessor universe is still scanned for all other triggers. The
window is an explicit bounded operational assumption, not a claim that all
dependencies are local. Relative and infinitive constructions are not exhausted
by these rules. Same evidence can support P1 and H4/H5 simultaneously: BOTH is
retained. Multiple antecedents remain parallel UNADJUDICATED candidates.

## Post-blind comparison and limitations

Audit all 98 historical SAME_LEVEL_SIBLING rows and all three historical direct
mother rows independently. Alias endpoints use only the explicit canonical
alias crosswalk in Phase B; a clause-level correspondence does not adjudicate
the alias's cycle/macro role. Preserve all 250 historical relations, with other
relation types marked outside this comparison's scope.

Comparison statuses are facts: expected support; expected support with competing
alternative; partial morphology/reference support; insufficient evidence;
not recovered; opposite supported hypothesis; or outside scope. Partial support
is an explicit verb-form plus PNG/subject conjunction, not a score. Do not infer
rejection from absence of support, and do not emit KEEP/REVIEW directives.

All existing mother cases, 2:11, 32:1 and the supplied control loci receive full
raw/context evidence and post-blind comparisons. All 49 placement proposals stay
UNREVIEWED. JP2 is post-blind only and requires matching blind hypotaxis support
for an existing human mother. Competing evidence stays JP5. A lexical cessation
probe plus domain shift may yield JP6 only when neither relation is supported;
this provisional transition question never consumes the historical function.
No mother or root is selected, including Job 1:1. Clause results and macro
projection are distinct outputs; the latter is not an accepted relation.

Native mother/tab/pargr/rela/code are loaded only after freeze. Report raw values
and exact native endpoints. Only documented Coor versus argument/adjunct rela
tokens with exact mother endpoint alignment are used for comparable checks;
tab/pargr/code are retained without guessing a decoder. Everything else is
NO_DATA or NOT_COMPARABLE. Native evidence never overwrites blind output.

## Review, outputs and acceptance

Required 01–17/90/99 outputs plus phase metadata, rule config, neutral-to-canonical
crosswalk, complete relation-case inventory, exact request, synthetic control
results and post-blind source audit. Every distinct ordered clause pair has a
review case linked losslessly to all target occurrences. Canonical review fields
are imported only post-blind and extended with the requested decision fields;
only UNREVIEWED is prefilled. The packet shows raw Hebrew, nodes, evidence flags,
P/H bundles, competing candidates, native comparisons and historical judgments.

Q1–Q9 remain historical UNREVIEWED. RQ1–RQ7 ask about support, discrepancies,
equal status of parataxis/hypotaxis, hypotactic-only mother cardinality, separate
macro projection and root review. Current readiness is
BLOCKED_PENDING_BLIND_RELATION_HUMAN_REVIEW. New human judgments, accepted
paratactic/hypotactic relations, parent edges and structural relations are zero.
Participant arc remains UNADJUDICATED; R4.4 consumer NOT IMPLEMENTED.

Validation requires syntax, unit tests, every gate's negative test, ten specified
synthetic controls, full regression skip-zero, inspected synthetic outputs,
real BHSA 2021 isolated discovery, frozen-output comparison/native validation,
independent byte-identical ZIP rerun, manifest and source-access audits. Windows
is the empirical environment; executable Termux commands are documented without
claiming a Termux empirical run. Technical PASS does not constitute human acceptance.
