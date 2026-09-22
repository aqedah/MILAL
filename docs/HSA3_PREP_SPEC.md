# HSA3-PREP — Unresolved-Parentage Triage and Global Structural Seam Audit

Authorized from R4.3 commit `b7834a76dceae046e4b83821445353793318a056` on
2026-09-22. Implement review preparation, synthetic and accepted-real validation,
independent deterministic rerun, documentation, commit and push. R4.4 recompilation
is not authorized until researcher adjudication is complete.

## Authority and preservation

HSA1 (31 records), HSA2 (25), HSA2-F (3), and R4.3 are frozen. The SHA256-pinned
R4.3 ZIP is the input, not a newly compiled scaffold. It contains 61 nodes,
205 typed relations, 3 resolved hierarchy edges and 57 unresolved direct-parent
rows. Retain all 50 accepted files byte-for-byte under `history/r4_3/`, including
59 original human records, source/context relations, original manifests and the
unresolved registry. Verify 82 frozen source/config/test/human/documentation files
and the 11 accepted input archives before and after execution.

Synthetic mode uses the frozen R4.3 synthetic adapter; real mode reads accepted
R4.3 bytes and verifies its nested source chain. No BHSA extraction, new marker
rule, source substitution, fuzzy identity or mutation of an analytical core.

## Meaning of triage

`direct_parent=UNRESOLVED` does not imply a separate independent judgment for each
row. The review-only categories are not permanent MILAL relation types:

1. TRUE_GLOBAL_SEAM: textual participants lacking the more specific dependency
   classification below; existing sibling/ending/function evidence still applies.
2. ROLE_ALIAS_OR_SAME_TEXTUAL_LOCUS: both original role nodes in an explicitly
   authorized same-locus pair with shared exact source evidence.
3. KNOWN_CONTAINER_BUT_DIRECT_PARENT_UNRESOLVED: explicit outgoing group membership.
4. GROUP_PARENTAGE_UNRESOLVED: a non-textual human or derived group itself.
5. LOCAL_RELATION_ALREADY_CONSTRAINS_STRUCTURE: continuation, direct local closure
   or higher-order termination already constrains the node's context.
6. TECHNICAL_OR_REPRESENTATIONAL_CASE: a technical node, if encountered in an
   unresolved input. JOB_BOOK is a technical root, not an unresolved input here.

Exclusive counting precedence: group, verified role pair, membership, local
relation, technical, remaining global participant. This is presentation triage,
not a strength ranking. Additional underlying constraints remain in source rows
and dependency tables. In particular the three speech-onset role cases also have
membership: the exclusive membership category is not the total membership count.

GROUP_MEMBER_OF, CONTINUES_WITHIN, SAME_LEVEL_SIBLING, exact parentage, role,
closure, higher termination, response and technical attachment remain distinct.
All 57 original parents stay UNRESOLVED. No review field is filled except
`review_status=UNREVIEWED`; import the existing canonical REVIEW_FIELDS.

## Same-locus audit

Scan the entire 61-node inventory. Non-textual groups/root cannot count as textual
events. Group textual nodes by exact reference pair to identify audit candidates,
not to prove identity. The researcher explicitly identifies these pairs:

- H:HSA2-C1-S1 / H:HSA2-CYCLE-1, Job 4:1.
- H:HSA2-C2-S1 / H:HSA2-CYCLE-2, Job 15:1.
- H:HSA2-C3-S1 / H:HSA2-CYCLE-3, Job 22:1.

Require both explicit authorization and nonempty intersection of exact source
evidence IDs. Preserve the two roles and distinct judgment IDs; record
SAME_TEXTUAL_LOCUS_DIFFERENT_STRUCTURAL_ROLE only in this audit. Unlisted same
references are UNVERIFIED_SAME_REFERENCE_ONLY, never silently merged. A new
unverified duplicate blocks accepted publication through the identity gate.

## Review dependence and case construction

`config/hsa3_prep_job.json` records the researcher's A–G minimum inspection scopes
using exact node IDs, and explicit display-owner seeds. These are review scopes,
not candidate parents or new human judgments. Derive directed review-dependency
paths exclusively from existing GROUP_MEMBER_OF, CONTINUES_WITHIN, CYCLE_ONSET_OF,
TERMINATES_ENCLOSING_GROUP, CHILD_OF and inverse HIERARCHICALLY_ABOVE edges.
Direction records how a context question can coordinate review; no relation is
converted or transitively asserted in the structural graph. Sibling, adjacency,
response, negative closure and parallel endings do not establish common parents.

Follow these paths to a unique configured review scope. Multiple or absent scopes
produce an additional SEAM_EXTRA case; do not choose by distance, rank, speaker,
chapter, topic or span. Thus the case count is computed, not a fixed required
answer. Negative tests demonstrate extra-case discovery and non-ranking.

Each unresolved row receives one primary presentation owner for an exact 57-row
partition, plus all participating cases for overlaps. Expand the supplied case
seeds through incoming dependency paths to preserve all affected local/group
members. Include incident nontechnical relations with their exact endpoints,
dimensions, human provenance and context. External endpoints in a constraint
remain source context, not new case parentage.

Primary assignment is not a claim that one later decision resolves every row.
The dependency map marks local/member decisions as deferred pending case review,
not unnecessary forever. Exact parent representation remains a separate question.
Group audit records origin, false textual_boundary, explicit members, original
relations, dependent rows and an open need-for-parent-representation question.

The seven observed nonredundant review scopes A–G coordinate 57 rows. This tests
and confirms substantial **review-scope compression**, not the mathematically
independent number of future atomic judgments. That number cannot be established
before adjudication. E is a genuine interface question with overlapping participants
and zero exclusively assigned rows. H is a summary of A–G, not another independent
case or a proposed tree. No groups are forcibly attached under a new textual parent.

## Preserved questions and constraints

- A: opening/testing structure, its two scopes, 1:6/2:1 peers, explicit 1:13 child,
  parallel endings, 2:11 and 3:1. Local messenger/continuation cases are dependent.
- B: independent 3:1 above 3:2 versus the dialogue-cycle sequence. 3:2 is already
  resolved and included as context, never manufactured as a 58th unresolved row.
- C: cycles 6/6/4, final cycle-3 onset 26:1, no Zophar III, and POST_DIALOGUE_JOB.
  27:1/29:1 are peers; 28:1 continues within 27:1. Preserve all three HSA2-F
  31:40 decisions; its parent representation does not reopen closure adjudication.
- D: 31:40 / 32:1 / 32:2–5 / Elihu sequence and 37:24. Introduction and speeches
  are not peer speech units. Preserve the researcher's introductory/subordinate
  organization; only exact node-level enclosure/attachment remains for review.
  The four speeches are peers. Do not supply a direct closure target for 37:24.
- E: Elihu ending / YHWH onset. Adjacency neither supplies hierarchy nor proves a
  rhetorical-response antecedent. No subordinate YHWH relation is inferred.
- F: YHWH onsets 38:1/40:6 and Job responses 40:3/42:1 remain respective peers;
  40:1 remains child of 38:1. Higher organization is open.
- G: speech complex / final narrative at 42:7. 42:16 continues within it;
  no 42:10/42:12 promotion.
- H: whole-book summary of known contexts and unresolved attachments only.

## Evidence and usable packet

Each case includes exact node/reference/function rows, historical human IDs and
linguistic/methodological text, all incident positive/negative constraints, exact
BHSA clause/clause_atom and historical marker IDs, accepted frame context where
linked, an unresolved question, redundant review warnings and blank review fields.
Candidate lists stay empty: no new parent possibility needs to be fabricated.
UNRESOLVED and INSUFFICIENT_EVIDENCE are valid outcomes.

05 retains every selected raw source/context occurrence, exact member/row locator,
hash and original upstream locators. Frames use only the existing R4.3 unresolved
frame-ID linkage. Absence of a linked frame is reported, not filled by nearby data.
All raw source files remain lossless even where the Markdown consolidates IDs.

## Outputs and validation

01 triage; 02 role audit; 03 case records; 04 Markdown packet; 05 evidence links;
06 dependency map; 07 negative controls; 08 gates; 09 original-row crosswalk;
10 non-textual group audit; 90 metadata; 99 manifest. Original R4.3 files remain
under history/r4_3. Fixed ZIP timestamps and deterministic serialization.

Syntax, full regression, stage tests, every-gate negative mutations and manual
synthetic inspection precede accepted-real execution. Run twice independently;
require every file and ZIP byte-identical. Verify all original frozen hashes,
crosswalk, alias completeness, typed paths, provenance locators, outer/nested
manifests, CRC, disk bytes and the human packet. Stop on source inconsistency,
unaccountable row, destructive role merge or invented hierarchy. Technical PASS
does not constitute researcher adjudication or authorize R4.4.
