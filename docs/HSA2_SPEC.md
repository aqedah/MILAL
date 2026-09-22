# HSA2 — Dialogue-cycle adjudication and closure-target audit

Researcher-authorized on 2026-09-22 from HEAD
`28892b3f0ecab3d42749ab50d8a65bc4aa9e09c5`: implement, test, inspect synthetic,
audit accepted real artifacts, rerun deterministically, inspect and commit/push.
This is an append-only human layer and evidence comparison, not whole-book parentage.

## Human authority

HSA1 Markdown/CSV, code, tests and configuration are frozen. Their exact hashes,
and those of MR1/R4 analytical modules, are checked before real execution and again
before publication. HSA2 uses separate
[Markdown](HUMAN_STRUCTURAL_ADJUDICATION_HSA2.md) and
[CSV](HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv), never rewriting the earlier judgments.
REVIEWED applies only to supplied human assertions. The program reads these files;
it never supplies new human conclusions or chooses a closure target.

25 HSA2 records: 16 cycle speech-unit onsets, 3 separately identified cycle onsets,
3:1 initial-speech context, internal 11:4, and 27:1/28:1/29:1/31:40 context decisions.
Same-reference speech and cycle functions use different judgment IDs. The historical
marker remains ANSWER+AMR at all three cycle starts. Named speaker sequences are
human assertions; no new participant identity inference is performed.

83 directed human relation pairs: 72 within the explicitly reviewed cycles, 6
between cycle-onset judgments, 2 between 27:1/29:1, and 3 supplied above/continuation
relations (3:1→3:2, 11:4 within 11:1, 28:1 within 27:1). The reference to 3:2 resolves
to frozen HSA1 HSA014. Reciprocal pairs count twice. No implicit inverse/transitive
completion, exact cycle closing span, closing edge after chapter 26, Zophar III,
or whole-book parent graph is constructed.

## Independent closure dimensions

31:40 remains SPEECH_UNIT_END. Both `direct_closure_target` and
`higher_order_terminal_effect` remain UNRESOLVED. Three separately identified
UNREVIEWED candidate rows retain the research question: direct local closure of
29:1, direct closure of the complex beginning at 27:1, and termination of the
human-supplied enclosing 27:1–31:40 group. Candidates are not direct relation pairs.

Direct-dimension options: DIRECT_LOCAL_CLOSURE / NO_DIRECT_RELATION / UNRESOLVED.
Higher-dimension options: TERMINATES_ENCLOSING_GROUP / NO_DIRECT_RELATION / UNRESOLVED.
The schema allows simultaneous local closure and higher termination; it does not
force a single closure level. All real selected fields remain UNRESOLVED. The unit
test demonstrating coexistence changes only a copied test object, not human records.

A marker may close the immediately active speech unit and simultaneously produce
termination at one or more enclosing structural levels. Proximity, chapter boundary,
semantic topic, traditional commentary, longest span and shortest span are not target
selection rules. No routine ranks candidate targets or attaches an ending to an opening.

## Evidence and scopes

Use HSA1's read-only accepted-source adapter without changing it. Its seven pinned
ZIPs (MR1/R3c.3/PROV1/HR1/R4.0/R4.1/R4.2) are verified for exact SHA256, member
manifest, safe unique names, CRC and accepted PASS gates. No BHSA extraction rerun.
Native evidence is the accepted R4.2 BHSA 2021 snapshot.

HSA2 reference panels join exact native reference coordinates to explicit native
clause/atom IDs. They include every overlapping participant, MR1/HR1 anchor and
formal occurrence by native-atom identity, never by similar surface or span text.
These are context panels, not new marker/event IDs. Expand all source dependencies
and preserve full source rows and original archive/member/row hashes.

Add exact PROV1 G0–G6 atom signatures and canonical preimages for all panel atoms.
Native order comes from PROV1's explicit `atom_index_1based`, not flattened clause
membership: a clause may contain discontinuous atoms (for example 28:28). Validate
the complete index inventory and every accepted formal occurrence's stored indices.
Historical, reconstructed and SHA256-of-preimage values must match. Original R2
provenance embedded in accepted PROV1 remains visible; no unavailable R2 ZIP is
substituted or claimed freshly verified. PROV1 archive/member/row provenance is verified.

For 27:1/29:1/31:40 show every clause in the full verse, the explicit MR1 marker span,
and complete preceding/following verses in native order. At 31:40, the marker is
the final clause/atom, not automatically the entire verse. Formal edge relations
use explicit MR1 start/end indices: STARTS_AT_MARKER_START, ENDS_AT_MARKER_END,
CROSSES_START_EDGE, CROSSES_END_EDGE and WITHIN_MARKER_SPAN. Labels may coexist.
All occurrences, families, levels, spans and provenance survive; no representative
pattern is substituted. Exact corresponding-position opening hashes are compared
only across the explicit 27:1 and 29:1 formula spans; this is not a closure heuristic.

The audit also lists all MR1 events within the researcher-supplied 27:1–31:40 review
range, preserving embedded expressions without calling them new human units.
Lexical presence of the source `MCL/` lexeme is reported at the opening and ending
markers. Its presence/absence does not establish semantic equivalence or a target.

Comparison controls: 1:6/1:22, 2:1/2:10, 36:1/37:24 and
38:1/40:1/40:3/40:6/42:1. Preserve full-verse control context even when an MR1 CSF is
also present (notably 2:10). A full-verse human comparison scope is labeled separately
from an exact MR1 marker span. Human 1:22/2:10 endings remain non-MR1. Frozen HSA1
judgments accompany controls; no new control closure relation is inferred.

## Validation and artifacts

Run syntax, previous regressions, HSA2 tests and synthetic self-test; inspect synthetic
reports before the authorized accepted-real audit. Every gate has a negative mutation.
Real audit outputs must preserve source CSV/Markdown bytes, and independent processes
must reproduce every file and ZIP. Input and frozen-file hashes are checked again
before publication. Fresh output paths only; results/logs are ignored.

Outputs 01–08 follow the requested human records, source links, candidate relations,
focused audit, cycle report, summary, negative controls and gates. Additional tables:
09 all formal edge relations, 10 exact marker/control scopes, 11 marker lexemes,
12 direct human relation pairs, 13 full atom signature provenance, 14 frozen HSA1
human records, 15 exact HSA2 Markdown; 90 metadata and 99 complete SHA256 manifest.
The human CSV uses repository LF line endings so Git checkout preserves its bytes.

Job 3–26 cycle review is now recorded, but the direct closure target of 31:40 remains
unresolved. Next required review: local 29:1 closure versus 27:1 complex closure,
and the independently possible enclosing terminal effect. R4.3 whole-book parentage
remains blocked pending that closure-target review.
