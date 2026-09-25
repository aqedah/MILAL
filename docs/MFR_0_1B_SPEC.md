# MFR.0.1b — Marker Role & Evidence-Independence Audit

Authority: [exact researcher request](MFR_0_1B_RESEARCHER_SOURCE.txt).
Start baseline: `3afd37a08ca5e0745bd1e0c46c756c1f8004751b`.
MFR.0.1 discovery, MFR.0.1a bundles/crosswalks and historical judgments stay frozen.
This is a new overlay, not a correction to either frozen analytical core.

## Scope and input isolation

The complete MFR.0.1a ZIP is pinned by SHA256; its CRC and every manifest entry
are verified, followed by its embedded complete MFR.0.1 ZIP. All 384 baseline
repository files except mutable HANDOFF and gitattributes are hash-pinned.
The full prior ZIP is included byte-for-byte in the new release, preserving all
raw observations, signatures, family memberships, force, coverage, nested and
relation evidence, including rows not in a default review queue.

Job receives the complete marker-role, bundle-role, cessation, relation-provenance,
closure-independence, configuration and phase-dependency audit. The four external
corpus scopes receive complete marker/bundle/cessation role overlays. Their existing
frozen control relations are verified afterward; a new all-pair relation audit of
those external corpora is not claimed. No BHSA reload or new discovery occurs.

A compact blind input ZIP contains only explicitly named frozen observation,
marker, family, force, coverage, nested, relation and MFR.0.1a consolidation tables
needed for that scope. Original member names and byte hashes are recorded.
An isolated process enforces file-read/write boundaries and excludes historical
imports. It records all logical member reads and code hashes. Interpreter startup
precedes this application-level audit. All five role outputs and Job relation
outputs freeze under one manifest before control lookup or human rendering.

## Marker and bundle roles

`config/mfr_0_1b_role_rules.json` is the explicit generic rule registry. The three
subject/addressee/domain shift tags are support signals. They never become formal
triggers merely because MFR.0.1a called them formally explicit.
All requested primary-trigger tags are retained. Three additional attested frozen
tags are explicitly typed as formal constructions: DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION,
AFTER_DEATH_TEMPORAL_CONSTRUCTION and YEAR_ONE_CONFIGURATION. An unknown source tag
fails rather than receiving a guessed role.

Effective formal triggers plus support signals yield COMPOSITE_MARKER_CANDIDATE;
effective formal triggers alone yield PRIMARY_FORMAL_MARKER_CANDIDATE. Support-only
rows remain SUPPORT_SIGNAL_ONLY with their IDs, anchors, bundles and context use.
A cessation lexical trigger with no other effective formal trigger remains
LEXICAL_EVENT_CANDIDATE_REQUIRES_ROLE_AUDIT when its role is non-discourse or ambiguous.
Historical trigger fields are preserved separately, including EXPLICIT_CESSATION.
Primary-bearing counts include composite rows and exclude this lexical-only group.

Bundles keep exactly the original occurrence sets and contributing family IDs.
All-primary bundles, all-support bundles and other mixtures are reported separately.
A lexical-only bundle falls in MIXED_ROLE_BUNDLE as the residual category; its
explicit lexical-audit membership is retained, so this label does not imply that
two roles necessarily occur in that bundle.

## Cessation role candidates

Every original cessation marker is audited, without discovering new markers.
The overlay records predicate words and morphology, phrase/word nodes for subject,
object and complement, speech nouns, infinitives, participants, neighboring domain
values and clause identities.

- A registered word/speech/answer noun in a same-clause subject or object supports
  DISCOURSE_CESSATION_FORM_CANDIDATE. The implementation also records complement
  arguments as candidates; it does not assert a resolved grammatical head.
- A registered speech verb in an infinitive supports
  SPEECH_ACTIVITY_CESSATION_CANDIDATE. An immediately following clause must begin
  with a registered preposition and contain that infinitive. Its link is explicitly
  ADJACENT_PREPOSITIONAL_INFINITIVE_CANDIDATE, not a recovered BHSA mother edge.
- A registered bodily, physical or temporal lexical argument without either speech
  condition supports NON_DISCOURSE_CESSATION_USAGE_CANDIDATE. Polysemous words such
  as breath/spirit are not given a final sense or a human rejection.
- Missing or unsupported role evidence remains CESSATION_ROLE_AMBIGUOUS.

Speech/cessation predicate spellings come from the frozen MFR.0.1 rule registry.
The small new argument lexicons are explicit, inspectable audit criteria; they are
not claimed to be an exhaustive Hebrew ontology. No prior subject is resolved as
an implicit identity. Domain changes are displayed, not sufficient by themselves
to turn a lexical event into a discourse-cessation form.

## Evidence provenance and independence

Evidence rows contain raw upstream IDs, parent evidence IDs, dependency root IDs,
provenance family, observed details and whether the evidence is usable independently
of a cessation-derived chain. Root IDs name upstream computational evidence units,
not statistical independence or distinct copies of the entire BHSA dataset.

Direct formal, sequence, independently computed contextual, participant, domain
and frozen resumption evidence remain separate dimensions. Resumption's participant
and context roots are shared with the corresponding underlying evidence, so its
label is not counted again as an independent root. Repeated onset evidence shares
its corresponding family roots. A generic clause-function-order match is retained
but does not alone qualify as an independent formal closure link.

For coverage with `end_basis=EXPLICIT_CLOSURE`, `end_evidence` supplies the original
cessation target identity. Target identity, that coverage and every nested row
derived from it all share `CESSATION:<marker_id>`. Nested rows from any coverage
inherit that coverage's roots and never introduce another independent root.
No EVID_NESTED_INDEPENDENT rows are manufactured: the frozen implementation derives
all nested intervals from coverage. Multiple display types can therefore be one
ONE_CESSATION_DERIVED_CHAIN_PER_SHARED_ROOT.

Other coverage retains family-recurrence or domain-boundary roots. It is eligible
as a closure link only when its exact endpoint matches the target atom/position.
Mere containment is not endpoint support. ANALYSIS_SCOPE_END is a scope limit and
never an independent closure link. An independent coverage category is reported
in addition to the requested minimum closure categories.

Root-sharing evidence is combined into connected dependency components. Multiple
independent-family status requires both multiple families and multiple disjoint
root components. These are inspectable provenance groupings, not strength scores.

## Closure and family review eligibility

Every raw closure pair is preserved. A default closure review case requires an
eligible discourse/speech/ambiguous target role, at least one non-cessation-derived
link and a primary-bearing source. The final condition implements request section
14: support signals may contribute context but do not become standalone closure
sources. All excluded pairs remain archived with the precise reasons. Consequently
`09_closure_derived_only_archive.csv` also retains non-discourse targets and
support-only sources with independent contextual evidence; it is not falsely
reported as a count containing only derived-only chains.

FAM_A requires primary-bearing repetition with exact, slot or sequence evidence;
generic order-only repetition remains reference. FAM_B requires an explicit formal
singleton; FAM_C requires primary-bearing observed expansion membership. FAM_D is
the dependency closure of actual H1/R1/C1 cases. Support-only bundles can be needed
as context in a phase while remaining non-standalone FAM_E/F reference material.
No family validity or textual level is decided.

## Configuration review groups and phase sets

A raw pair can carry a witness from an existing repeated sequence family when its
source and target lie inside two explicit occurrences of that sequence. The
SIG_SEQUENCE length determines each span; there is no reference-specific window.
Pair rows join only when they share that occurrence-pair witness and both their
source markers and target markers overlap or are immediately adjacent. Hierarchy
and non-hierarchy witnesses are not mixed merely to lower a count. Connected groups
retain every grouping edge, witness, raw pair and candidate label. No witness means
a singleton case. Stable sorted raw-pair identities determine configuration IDs.

Every raw relation maps exactly once to a configuration case. H1 contains all
hierarchy-competing pairs, R1 contains frozen evidenced resumption pairs, and C1
contains eligible independent-evidence closure pairs. Sets may overlap. Each set
includes the complete configuration's raw pairs and the markers/bundles needed to
read its sequence spans, including support context. Reference records remain
accessible. Group spans are review context, not accepted textual units.

The H1 packet shows ordered Hebrew clauses, context, roles, participants/domain,
adjuncts, correspondence, evidence roots and competing labels. Per-case attachments
preserve full raw pair rows, force, coverage, signatures and bundle definitions.
Human fields derive from canonical REVIEW_FIELDS plus the requested fields.
This request explicitly requires no prefill: even review_status is blank here.

## Validation and readiness

S1–S12, no-witness/non-adjacent negatives, root-component tests, read-boundary tests,
reference-invariance checks and a negative mutation for every gate are required.
Historical numeric gate names retain their names but compare with actual frozen
row sets, not hard-coded expected corpus totals. Syntax, stage tests, synthetic
packet, full regression, real frozen execution, independent ZIP rerun, manifest/ID
verification and post-freeze manual controls precede release.

Success is MARKER_ROLE_AND_EVIDENCE_INDEPENDENCE_ESTABLISHED and
READY_FOR_MFR_0_2A_HIERARCHY_CONFIGURATION_ADJUDICATION. MFR.0.2A comes first;
MFR.0.2B and MFR.0.2C remain separate later batches. Full MFR.0.2 readiness,
hierarchy assembly and R4.4 implementation readiness are not declared.
