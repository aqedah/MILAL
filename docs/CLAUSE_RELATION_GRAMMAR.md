# MFR.0.2R executable relation grammar

Status: implementation under validation; no empirical acceptance is claimed.
The researcher requests and additions preserved in `MFR_0_2R_*_SOURCE.txt`
are the authority. The frozen baseline is
`2ff2536f50998beec585b8cb187abbf2086d97e0`.

## Methodological source families

| Family | Contribution | Verified local source |
|---|---|---|
| ETCBC / Talstra | Form-to-function, bottom-up hierarchy; raw database features | BHSA 2021 feature metadata |
| Walton | Clause connection, participant/time/place, iterative revision | Experimenting with Qohelet, §§2.1.1.1–2.1.2.4, pp.16–19; long-distance discussion p.28 |
| Jin | Different/same-type hypotaxis/parataxis and global alternatives | Investigating the Text-hierarchical Structures and Composition of Numbers, §§3.2.9.2–3.2.9.4.2, pp.25–35 |
| Bosman | Separate syntax/reference/prosody layers, hidden antecedents, human/program comparison | Prosodic Influence on the Text Syntax of Lamentations, §9.1 pp.201–207, §12.1 pp.246–247, §§13.1–13.5 pp.251–256 |
| Oosting | Observed valency, clause constitution, corpus analogy, secondary Masoretic evidence | Walls of Zion and Ruins of Jerusalem, §§1.1.4, 1.2.3–1.2.4, 1.3, 1.3.6, 1.4; pp.25–27,39–43,48,61–65 |
| MILAL | Executable predicates, exhaustive indexed search, typed graphs, provenance, deterministic packaging | This specification and versioned configuration |

MILAL selectively incorporates Oosting’s valency-oriented and corpus-linguistic
procedures where they improve clause constitution and syntactic validation.
It does not import his Isaiah hierarchy, participant conclusions, participle
interpretations, or emendations. Bosman's Lamentations-specific acrostic and
strophe conclusions are not rules for Job. Walton's nearest preference and
automatic level-zero assignment are not hard rules in this implementation.

Each author remains a distinct provenance family. PDF SHA256 values are pinned
in `config/mfr_0_2r_job.json`. The Jin type relations are DIRECTLY_ADOPTED;
MILAL contextual predicates, required/supporting/counterevidence fields and
functional-role candidate names are GENERALIZED_FOR_MILAL. Unverified extra
rules remain disabled UNKNOWN_NOT_VERIFIED. See `MFR_0_2R_SOURCE_CLARIFICATION.md`.

## Execution order and claims

Raw BHSA words, phrases, clauses and clause atoms → observed valency and internal
binding candidates → exact construction signatures → corpus analogue evidence
→ preceding clause candidates → Jin/Walton relation grammar → conditional graph
and global alternatives → larger-unit reference and poetry-aware evidence →
secondary Masoretic display → human adjudication. Later participant/discourse
interpretation requires separate explicit provenance and a hierarchy freeze.

The engine preserves BHSA clause constitution as a provisional analysis unit.
It examines all atom pairs within that clause, including nonadjacent atoms with
intervening clauses. Binding evidence defers inter-atom hierarchy classification;
it never merges atoms or rewrites the database. Observed argument realization
does not establish obligatory valency. Missing arguments remain
UNKNOWN_NOT_VERIFIED_NO_VALENCY_LEXICON. This version does not claim to recover
arbitrary previously unannotated cross-clause valency frames.

Construction signatures preserve predicate/stem, realized slots, prepositions,
phrase sequence, constituent order and morphology. Inner participial/infinitival
potentials remain separately represented, with argument governance unresolved.
Nonverbal predicate expressions are recorded only from explicit BHSA Pred/PreC
phrases, preserving their word/phrase nodes. Missing predicates remain
NOT_AVAILABLE and cannot form a shared valency/predicate analogue key. Exact
complete observed signatures may still be compared without inventing a head.
Exact analogues share the complete observed signature; close analogues share
observed valency; partial analogues share predicate and stem. Partial matches
are retained as counterexample candidates, not treated as positive identity.
Corpus analogues do not prove a hierarchy relation. Primary analysis is Job
only. HB_CORPUS is a raw construction-search index, not a hierarchy, participant,
marker or full-book valency analysis. The completed Job analysis retains its
original comparison evidence; a separately identified HB supplement expands
corpus evidence without modifying the Job candidate graph.

## Candidate search and grammar

Indexed search unions every preceding candidate supported by formal sequence,
predicate/lexical correspondence, participant recurrence/reintroduction,
potential grammatical reference, time, location or explicit native dependency.
Explicit subordinate constructions also retain preceding alternative mothers.
No nearest-only, book/chapter boundary, numeric score or maximum-distance filter
is used. Distance is reported only. Identical text is never an identity join.
Native `mother`/`rela` annotations are DATABASE_EXISTING_RELATION, not accepted
textual hierarchy. All original source object IDs remain available.

`clause_relation_grammar_v1.json` contains 24 Jin type relations: A4/B10/C4/D2/E4.
Their executable contextual predicates are explicit MILAL generalizations.
Type matching alone cannot propose a relation. Context predicates can support
both relations; the engine preserves this ambiguity. Participant lexical
recurrence and person/gender/number compatibility are potential evidence, not
resolved referential identity. All such identities remain UNRESOLVED.
NEW/CONTINUED/REINTRODUCED/ABSENT describe observed lexical recurrence only.

Function labels in a matched rule are hypotheses, never final literary or
discourse labels. Frame evidence, reference, time/place and domain do not become
boundaries by themselves. The old PRIMARY/SUPPORT labels remain historical
provenance without epistemic priority. Rhetorical and semantic interpretation
are not loaded in pass 1.

## Graphs, larger units and revisions

The candidate graph may have multiple potential mothers. A selected assignment
may have at most one strict mother per target. Parataxis imposes equal level;
strict edges must remain acyclic after parallel-component contraction.
Hard conflicts constrain jointly selected assignments; they do not delete
individual candidate edges. Soft conflicts remain visible.

Small components enumerate all coherent subsets. Large components preserve
every edge plus exact selection constraints symbolically; this avoids a
whole-book Cartesian expansion without pruning alternatives.
Conditional larger units preserve reachable descendants and every alternative
edge path. Their members are not asserted to coexist under one hierarchy.
Large-run membership uses exact bitsets indexed by clause position. Hidden
reference sets retain every target ID, the exact antecedent selection predicate,
the full conditional graph and the total antecedent/target cardinality.
The query utility reconstructs individual source-node identities and minimal
path witnesses. Tests compare expanded sets exactly with the original row-wise
representation; no occurrence is sampled or truncated. A shortest witness is
not a preferred hierarchy.

TEXTUAL_SYNTACTIC_LAYER, PARTICIPANT_REFERENCE_LAYER and POETIC_PROSODIC_LAYER
remain distinct. Unit-internal reference cannot replace a syntactic mother.
Formal poetic correspondence is observed evidence, not verified poetic intent.
Without verified poetic segmentation, boundaries remain
PROSODIC_NOT_AVAILABLE / UNKNOWN_POETIC_BOUNDARY. No Job strophes are invented.
Pass 2 preserves the pass-1 file hashes. Append-only, hash-chained histories
record later evidence and reconsideration; they never silently rewrite proposals.

Program-proposed/rejected/unproposed/accepted human combinations remain distinct.
The learning table preserves proposals and future explicit human events; no
black-box learning or automatic human completion occurs. Participant evidence
has RELATION_EVIDENCE provenance. An explicitly sourced later interpretation may
add DISCOURSE_INTERPRETATION or BOTH without rewriting the earlier observation.

## Encoded text and Masoretic evidence

Pass 1 uses BHSA's encoded text. Qere readings and accent codepoints are stored
separately. Neither changes the analysis form. Accents are secondary evidence
after linguistic alternatives exist, never automatic boundaries or clause
splits. Display eligibility does not claim that an accent resolves a case.

## Freeze, controls and human review

Blind workers receive only raw projections, native annotations, construction
comparison indexes, textual-tradition observations and versioned grammar.
A deny-by-default file guard excludes human decisions and control answers.
The sole Job blind scope must freeze before controls run. Other books enter only
through explicit-reference fixtures, one immediately preceding verse within
the same book, and whole-clause/interruption context. This bounded reading
context is separately recorded and is not a nearest-mother selection rule.
Full Pentateuch or other full-book engine runs are prohibited. Controls freeze
before MFR.0.2A's 13 historical human decisions are loaded for comparison.
The five prior PARATACTIC judgments remain provisional; no configuration is
silently promoted into a constituent edge. Compound configurations are not
equated to one onset edge. Each control verse retains its complete exact clause
panel; no first-clause representative is substituted for the panel. Variant
checks enumerate all exact panel combinations, and both Numbers alternatives
must be supported for the same clause triple. Cross-book control counts require
actual relation candidates, not just an admitted but insufficient pair.
Source controls are checks, never detection rules.

Human cases are target-centered and retain every admitted candidate, all
evidence dimensions, global alternatives and unit-reference selectors. The
canonical REVIEW_FIELDS are imported, and all new human fields are blank.
Next authorized review scope is MFR.0.2R-H. No automatic MFR.0.2B continuation,
canonical tree, new accepted mother, closure/resumption decision or R4.4 consumer
is produced.

## Output layout and lossless storage

`blind/job/01–17` contain grammar, observations, candidate sets, matched
rules, evidence matrix, conditional graph and force evidence. Additional named
tables carry bindings, exact signatures, corpus analogues, revisions and layers.
The matrix's exact source/target IDs and dimension name dereference the complete
observed values in `02_clause_feature_inventory.csv`; values are not duplicated
for every pair. Symbolic analogue selectors resolve against the complete
`corpus_analogue_index.json` and have explicit exclusion semantics.

Root `16` preserves frozen force/role provenance; root `18` preserves/revalidates
historical decisions. `controls/19–22` contain post-freeze comparisons. Root
`23–27` contain methodology, blank review, review index, next scope and gates.
Local large tables use deterministic gzip storage. Release ZIPs retain the
same `.csv.gz` files and every original manifest byte. This preserves pass-1
and blind freeze hashes inside the archive. Logical CSV names in selectors
resolve through the supplied `rows()` reader without changing the frozen files.
Human review CSVs and Markdown packets at the run root remain uncompressed.

## Validation and acceptance

Syntax, semantic unit tests, prior regression, stage self-test, synthetic output
inspection, real runs, independent deterministic rerun, manifests and computed
gates are separate requirements. The 89 gate declarations fail closed when an
invariant is missing or false. Gate boolean-propagation mutations alone are not
a substitute for semantic source/data mutations; report their coverage honestly.
Controls may be PARTIALLY_RECOVERED or NOT_RECOVERED. Do not alter generalized
rules to force expected references. Technical release is conditional on every
required gate; scholarly acceptance remains a human judgment.
