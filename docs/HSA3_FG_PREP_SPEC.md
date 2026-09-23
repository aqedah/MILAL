# HSA3-FG-PREP — Narrator / Temporal / Response-Complex Audit

Baseline `92f989e8da282f105781b57688174d57257bc9ca`, main.
Authority: [exact request](HSA3_FG_PREP_RESEARCHER_SOURCE.txt).
This is evidence preparation, not F/G adjudication. A–E remain frozen; F/G remain
UNREVIEWED; Q2/Q4/Q5 accepted and Q3 deferred remain untouched. R4.4 is prohibited.
New human judgments, textual relations and accepted overlay relations must be zero.

## Sources and execution scope

The researcher authorizes direct BHSA 2021 extraction, synthetic validation,
real execution, deterministic independent rerun and commit/push after all PASS.
Require the A/C ZIP SHA256
`e79575a4290913edce774f68d2bf94c2f03583f35636d9086a6bc0cca40f147b`
and the MR1 ZIP SHA256
`9f287dca2a7689e04f37b4a9dbcfe53dd714dcc8dc9d1a702f46f476f6537ec0`.
The configuration records exact local relative paths. Preserve all original
members under history/hsa3_abc and history/mr1. Pin 134 prior repository files.
No frozen analytical core, original artifact or human judgment is rewritten.

Use the frozen MR1 version-checked loader for BHSA 2021 / Text-Fabric 13.1.0.
Add lex0, gloss, txt, mother, rela, code, tab and pargr with explicit 2021 header
checks. Record loaded feature hashes, versions, actual data path and whole-Job
word coverage. The runner accepts an explicit TF path; the default is the user's
standard external Text-Fabric directory, never hard-coded in analytical Python.

The complete Job clause/word/phrase snapshot is emitted, with clause_atom IDs,
exact T.text surfaces and native morphological values. No normalization replaces
source surface. Exact lexical sequences are used for specified comparisons;
they are never object-identity or parentage links.

## Evidence fields and identity

Panels retain every clause at a requested locus, including quoted clauses;
they do not replace a verse with one representative clause. Each clause includes
raw type, domain, txt, verbs/forms, subject/object/complement phrases, participant
surface mentions, phrase functions, temporal phrases/positions, conjunctions,
lexical היה and חיה wayyiqtol flags, preceding/following clause IDs/types, current
HSA records, relations and source IDs. Participant mentions are not coreference
assignments. A speaker is explicit only where a speech predicate has a subject;
otherwise retain separately sourced HSA speakers or UNRESOLVED_IN_THIS_CLAUSE.
No nearest-onset speaker or addressee identity is inferred.

HSA links use exact BHSA2021:clause IDs already present in frozen evidence IDs,
not Hebrew, verse/span resemblance or nearest opening. Synthetic fixtures use
explicit SYNTHETIC:NATIVE anchors where supplied by prior fixtures, never the
empirical linker. Source CSV links include artifact/member/raw-row hashes and
one-based data-row identity. Clause records include snapshot-record SHA256.

BHSA domain N/Q/unknown is a source annotation, not an automatic narrator-voice
or boundary adjudication. Mother, tab, pargr, rela and code are only a separate
post-discovery corroboration object. They do not influence temporal selection,
formula comparison, grouping or parentage. Mutation tests replace them to verify
that lexical/phrase classification and formal comparison remain unchanged.

## Narrow whole-book temporal control

Select every Job word with exact lexeme `>XR/` (after) or `>XR=/` (other homonym).
This is an explicit narrow lexical inventory, not a Hebrew-prefix search.
`>XRJT/` (אחרית) and `>XRWN/` (אחרון) are outside that scope, remain in the full
snapshot, and are not silently counted as the same lexeme. In particular the
אחרית token in 42:12 is distinct from the אחר/אחרי construction.

Classification is deliberately inspectable and does not claim full semantic
disambiguation:

- TEMPORAL_SUPPORTED: the selected after word occurs in a BHSA Time phrase, or
  is clause-initial Conj followed by an overt perfect verb.
- NON_TEMPORAL_OTHER_HOMONYM: the distinct `>XR=/` lexical identity.
- UNRESOLVED_SENSE: other functions, including Adju/Cmpl, do not alone decide
  temporal versus spatial/other readings. Keep all such tokens and context.

No verse ID supplies a classification. 3:1, 42:7 and 42:16 are optional regression
controls on the resulting inventory, not the detector. Positions are one-based
within the clause, including conjunction tokens. Report clause-initial, before
first verb and after first verb independently. At 42:7 Conj introduces a separate
clause following the היה clause; do not relabel it as a Time phrase. At 42:16,
the Time phrase follows the חיה predicate and explicit Job subject.

Current HSA boundary assertions are separate from absence of an assertion.
Explicit CONTINUES_WITHIN links and positional inclusion in researcher-approved
group spans are separate fields; neither creates a new unit membership.

## Comparison panels and controls

The config contains all requested spine, F/G, temporal and formal-shift loci.
Scene windows 1:6–12, 1:13–19 and 2:1–7 preserve ordered clause configurations.
Match exact lexical sequences for ויהי היום, בני האלהים, להתיצב על יהוה;
retain Satan token witnesses and clauses with divine/Satan speech evidence.
Compare configurations without claiming the windows are identical. The accepted
1:6/2:1 siblings and 1:13 CHILD_OF 1:6 remain frozen.

Keep lexical W + HJH[ + wayq (p3/m/sg) separate from MR1 Way0 classification. Preserve MR1
positive/negative records by exact start_clause. W + XJH[ + wayq is distinct;
The חיה flag also requires p3/m/sg. 42:16 cannot become a Wayhi event through string-prefix similarity. A WayX היה
form, such as the later clause at 42:12, does not become a MR1 Way0 candidate.

For all configured cycle/Elihu onsets, compare the first verbal lexical identity
(ANSWER/ADD/OTHER), full verbal sequence, exact clause surfaces, שאת משלו witnesses,
MR1 CSF provenance and accepted HSA group memberships. The 27:1/36:1 similarity
is evidence only; neither formula length nor expansion supplies hierarchy.

F includes 38:1, 38:3, 40:1, 40:3, 40:6, 40:7, 42:1 and 42:6, with explicit
speaker/addressee evidence, CSF type, storm lexemes and repeated imperative
witnesses. Preserve articles, conjunctions and surrounding-clause differences.
The three FG-F-C1/C2/C3 records are UNADJUDICATED proposals, not actual composition
objects: automatic_resolution=false, review_status=UNREVIEWED, no relation IDs.

G includes 42:7/9/10/12/16. 42:10 and 42:12 retain all positive/countervailing
observations without boundary promotion. 42:16 retains אחרי זאת, overt Job,
clause form and possible life-summary-shift description. SIMILARITY, DIFFERENCE,
STRUCTURAL_IMPLICATION and CURRENT_JUDGMENT are separate fields. No finding in
this PREP stage adjudicates a contradiction of the frozen NO_BOUNDARY judgment.

## Criteria and human review

Use only exact IDs in the existing criteria registry, preserving original
dimension/admissibility records. Crosswalk evidence and insufficient-alone
codes without scores, new codes or automatic structural consequences.

Narratorial Frame Spine is an evidence/reporting overlay, not a rule generating
macrostructure, a textual parent, a composition group or a structural relation.
Same marker ≠ same structural function. Same temporal lexeme ≠ same boundary.
Same formal shift ≠ same structural transition. Narratorial clause ≠ automatic
higher-level clause. Adjacency, chapter, theme, speaker alternation and longer
formula alone never determine parentage.

The packet leaves exactly the supplied final F and G adjudication questions,
with 42:10/12/16 internal controls. Import canonical REVIEW_FIELDS; prefill only
UNREVIEWED, leaving all researcher responses blank. Earlier F/G questions,
constraints and ANA judgments remain in the nested unchanged A/C packet.

## Validation and outputs

Emit all 14 requested files, plus clause evidence, criteria/source links,
frozen integrity, whole-book source snapshot, exact request and F/G blank fields.
Computed gates cover version/baseline, source coverage, specified observations,
negative controls, all frozen decisions, zero new judgments/relations, manifest
and deterministic rerun. Every gate has a negative test. Validate syntax and
stage/full tests with zero skips, inspect synthetic packet, then run actual BHSA
and an independent invocation. Verify complete ZIP bytes and all manifests.
