# HSA2-F — Job 31:40 Closure Final Adjudication

Authorized on 2026-09-22 from `21225566974ca4b18d38679c790a2b5c37066cd3`:
append the supplied final human decisions, validate synthetic and accepted-real
audits, inspect, commit and push. This is not R4.3 or an analytical extraction stage.

## Authority and history

The separate [final Markdown](HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.md) and
[final CSV](HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv) contain three supplied
REVIEWED decisions. HSA1 and HSA2 are frozen, including original UNRESOLVED fields.
The code reads these authored rows; it does not complete a review or choose a target.
Prior HSA2 remains correct as an evidence audit without a human target decision.

| Candidate | Dimension | Final existing vocabulary | Meaning |
| --- | --- | --- | --- |
| CT01: 31:40 → 29:1 | DIRECT_CLOSURE_TARGET | DIRECT_LOCAL_CLOSURE | Direct local ending |
| CT02: 31:40 → 27:1 | DIRECT_CLOSURE_TARGET | NO_DIRECT_RELATION | NO_DIRECT_CLOSURE only |
| CT03: 31:40 → 27:1–31:40 group | HIGHER_ORDER_TERMINAL_EFFECT | TERMINATES_ENCLOSING_GROUP | Separate higher termination |

No new controlled relation vocabulary is needed. `semantic_meaning` maps the
researcher's wording to the existing dimension-qualified vocabulary. A rejection in
the direct-target dimension does not reject a higher-order relation. CT01 and CT03
remain distinct records, not a single closure field. No new enclosure node is made.

Marker evidence alone leaves the direct target unresolved. The researcher uses the
previously adjudicated peer onsets at 27:1 and 29:1 (same TAKE_MASHAL+AMR formula,
matching corresponding signatures), and 28:1 NO_BOUNDARY / CONTINUES_WITHIN 27:1.
The new same-level speech at 29:1 is locally active thereafter; the researcher
therefore adjudicates 31:40 as its direct ending, while separately terminating the
group beginning at 27:1. 29:1 is not subordinated to 27:1. This reasoning is recorded
as the supplied human decision, not executed as a general closure algorithm.

No nearest-opening, chapter, shortest/longest span, topic or commentary heuristic.
The relation projection accepts only authored rows and has no evidence geometry
input. Exact candidate and supporting human IDs are required; no fuzzy fallback.
No whole-book parentage, transitive/inverse completion or unreviewed parent is added.

## Accepted sources and outputs

The configuration pins the accepted HSA2 ZIP and 67 baseline repository files:
all then-tracked source, tests and configuration, plus HSA1/HSA2 human/specification
documents. HANDOFF is deliberately updated separately; the earlier sections survive.
Before/after execution, verify pinned files. Verify accepted HSA2 SHA256, CRC,
manifest, mode/status and gates. Its human files must equal frozen repository bytes.
Use the frozen read-only HSA2 adapter to verify all original source/context links
against the accepted upstream archives. No BHSA extraction or marker rerun occurs.

All 17 original HSA2 members are copied byte-for-byte under `hsa2/`, including its
manifest, reports, controls, 25 judgments, 83 directed relations, 1968 links, and
three unresolved candidate rows. No source/evidence identity is rewritten.
Top-level outputs:

- 01 final human decisions: three rows, exact committed CSV bytes.
- 02 final decision provenance: 15 links (one candidate plus four prior human
  judgments per decision); each has archive/member/row identity and SHA256.
  These are human-decision provenance links, not newly detected textual evidence.
- 03 final typed relations: three supplied relations; the rejection is not a
  positive closure edge. The historical 83 relations remain separately unchanged.
- 04 compact final closure report with exact source evidence and decision history.
- 05 exact authored final Markdown; 08 computed gates; 90 metadata; 99 manifest.

Total human records across layers: HSA1 31 + HSA2 25 + HSA2-F 3 = 59.
This is an additive decision history, not 59 distinct textual boundary units.
HSA2 relation view: 83 historical + 3 final typed assertions = 86; two are affirmative
closure/effect assertions and one is a dimension-qualified rejection. HSA1's 33
directed pairs remain separate. No inverse or transitive edges are inferred.

## Validation and advancement

Syntax, full regression (including original HSA2), stage unit tests and synthetic
self-test precede accepted-real execution. Every computed gate has a negative
mutation. Inspect the synthetic report, then accepted-real report. Independent
processes must reproduce all members and the ZIP; verify both nested and outer
manifests. Original analytical cores and human histories remain hash-frozen.

If an implementation assumption creates parentage beyond these supplied decisions,
stop and report it. Successful validation unblocks the closure-review prerequisite
for R4.3, but this task does not generate that stage or claim whole-book acceptance.
