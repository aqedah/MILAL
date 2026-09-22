# HSA2-F validation — 2026-09-22

Starting commit: `21225566974ca4b18d38679c790a2b5c37066cd3` (clean main,
fast-forward pull already current with verified origin). Researcher authorized
the three final human judgments and validation through commit/push.

## Results and methodological meaning

Three new REVIEWED human records, not newly computed boundaries:

| Original candidate | Final relation | Dimension |
| --- | --- | --- |
| CT01: 31:40 → 29:1 | DIRECT_LOCAL_CLOSURE | DIRECT_CLOSURE_TARGET |
| CT02: 31:40 → 27:1 | NO_DIRECT_RELATION (= NO_DIRECT_CLOSURE) | DIRECT_CLOSURE_TARGET |
| CT03: 31:40 → 27:1–31:40 | TERMINATES_ENCLOSING_GROUP (= HIGHER_ORDER_TERMINAL_EFFECT) | HIGHER_ORDER_TERMINAL_EFFECT |

The researcher uses previously adjudicated peer speech onsets to identify the
locally active unit beginning at 29:1, and separately adjudicates the group effect.
No nearest-opening or other generic closure selection rule was implemented.
27:1/29:1 remain SAME_LEVEL_SIBLING, with no parent/child or subordinate-continuation
edge. 28:1 remains NO_BOUNDARY / CONTINUES_WITHIN 27:1. Cycles remain 6/6/4, incomplete
third cycle and no Zophar III. 3:1, cycle onsets 4:1/15:1/22:1, 26:1 and MR1 labels
remain unchanged. Whole-book hierarchy was not generated.

HSA1 31 + HSA2 25 + final 3 = **59 historical human decision records** (increase 3),
not a count of distinct boundary units. HSA2's 83 directed pairs remain unchanged;
the final layer adds three typed relations (two affirmative effects, one rejection):
**83 + 3 = 86** in the combined HSA2/final relation view. HSA1's 33 directed pairs
remain separately frozen; there is no transitive/inverse completion or deduplication.

**1968 source/context links unchanged**. **15 added human-decision provenance links**
(candidate plus four prior judgments per decision), giving 1983 link rows across
these two distinct tables; the added rows are not new textual evidence. All exact
candidate, human, source and context IDs remain traceable without fuzzy matching.

## Validation performed

- Syntax: both new Python modules parsed successfully.
- Full unittest discovery: **566 PASS, zero skips** (529 prior + 37 HSA2-F).
  Includes all **47 original HSA2 tests** unchanged and **37 HSA2-F tests**.
- Stage self-test: **26/26 gates PASS**; synthetic report manually inspected.
- Accepted-real audits A and B: **26/26 gates PASS** in each independent process.
- Negative coverage: 25 named data/model gate mutations plus the serialized
  manifest mutation cover all 26 gates. Additional tests reject missing/duplicate
  exact IDs and existing output paths, and verify projection independence from
  candidate order, preserved history, human file fidelity and publication.
- **25/25 output files and the entire ZIP are byte-identical** between processes.
- Outer manifest, nested original HSA2 manifest, ZIP CRC and extracted disk bytes PASS.
- **17/17 original HSA2 members preserved byte-for-byte** from the accepted ZIP.
  Original CT01/CT02/CT03 remain UNREVIEWED/UNRESOLVED. HSA2-END-31 retains both
  original UNRESOLVED closure fields. HSA2 does not appear to have computed 29:1.
- **67/67 baseline repository files retain their pinned exact local SHA256**.
  Independently checked Git baseline identity using Git's configured clean
  conversion, in addition to exact raw local hashes: PASS. Some pre-existing
  fixture working copies use CRLF while Git stores normalized text; no frozen
  file was rewritten to change line endings. Pins describe this validated Windows
  checkout; this run does not claim cross-platform checkout-byte equivalence.
- Eight accepted ZIPs verified: HSA2 plus its seven upstream MR1/R3c.3/PROV1/HR1/
  R4.0/R4.1/R4.2 sources. Their exact archive, member and source-row provenance
  was verified through the frozen read-only adapter. All 15 final human-provenance
  links independently resolve to their exact candidate/prior row and hashes.
- Real compact report manually inspected: correct Hebrew opening/ending surfaces,
  exact clause/atom IDs and locators, original history, three final judgments,
  dimension-qualified rejection, and separate local/group reasoning.

No new BHSA extraction, analytical rerun, cross-platform validation or whole-book
methodological acceptance is claimed. This is an accepted-artifact human-decision audit.

## Artifacts

- Synthetic: `results/hsa2_f_synthetic_final2_20260922/`
- Accepted A: `results/hsa2_f_final2_20260922_a/`
- Independent B: `results/hsa2_f_final2_20260922_b/`
- ZIP: `results/hsa2_f_final2_20260922_a_results.zip` (1,003,900 bytes)
- Log: `results/hsa2_f_final2_20260922_a_run.log`
- ZIP SHA256: `64cf4c0eae884f8c7d407d3880e0d867a70bdd56d79bd2bb557ee2b119103bcc`
- Report: `04_job_27_31_closure_target_final_adjudication.md` inside each run.

Source HSA2 ZIP SHA256:
`669018ceacacef21db426028854ea1f88879a446d4d4ca113d24bec6ef8f2994`.
All run directories, ZIPs, logs and temporary verification scripts remain ignored.

## Changed repository files

- `config/hsa2_final_job.json`
- `docs/HANDOFF.md`
- `docs/HSA2_FINAL_SPEC.md`
- `docs/HSA2_FINAL_VALIDATION_REPORT.md`
- `docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv`
- `docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.md`
- `docs/README_MILAL_HSA2_FINAL.md`
- `src/milal_hsa2_final.py`
- `tests/test_hsa2_final.py`

Frozen HSA1/HSA2 human records, code/config/tests and all earlier analytical cores
are unchanged. The 31:40 closure review prerequisite is now satisfied. R4.3 is
unblocked as a next stage after this successful validation, but has not been executed.
