# HSA1 validation — 2026-09-22

Starting commit: `77ca713b9520ce085135dc845f60d920095756cb`, clean main, origin
`https://github.com/aqedah/MILAL.git`, fast-forward pull already up to date.
The completion commit is the commit containing this report; no self-referential
commit hash is embedded in generated artifacts.

## Human record and methodological meaning

31 human-authored REVIEWED judgments, including one span-level 32:2–5 record.
The source-of-truth Markdown and CSV are field-equivalent. Derived copies are
byte-identical to those inputs. Code never writes either human source file.
All unique primary-anchor fields remain blank because no unique atom was adjudicated;
linked panels preserve all actual native atoms.

33 directed human relation pairs: 20 SAME_LEVEL_SIBLING, 8 CONTINUES_WITHIN,
2 CHILD_OF, 2 PARALLEL_TO and 1 HIERARCHICALLY_ABOVE. Counts include reciprocal
relations; they are not 33 inferred hierarchy decisions or completed parent objects.
The four explicitly adjudicated Elihu siblings contribute 12 directed peer pairs.
No inverse/transitive completion, global parent inference or Job 3–26 unit inference.

31 source-linked judgments / 0 without exact machine links; **1122 expanded links**.
These include native/context links, not necessarily machine-detected markers.
All structural conclusions remain human judgments. Formal, participant and HR1
context is preserved separately; HR1 itself carries prior human adjudication.

## Validation

- Python syntax: all three new Python files PASS.
- Full regression: **482 tests PASS, zero failures/errors/skips**; 436 unchanged
  earlier tests plus 46 HSA1 tests.
- HSA1 tests rerun after final source-ID and LF byte-fidelity checks: **46 PASS**.
- Final synthetic self-test: **30/30 gates PASS**. The report and per-judgment
  Markdown were inspected, including synthetic labels, direct pairs, 32:2–5 span,
  sibling groups, unresolved identities and methodological cautions.
- Accepted-artifact audit and independent rerun: **30/30 gates PASS** each.
- Every gate has a negative test: judgment presence and each specified relation;
  false MR1 closure/event promotion; identity/first-appearance/named-role mutation;
  missing overt entry, HR1 scope or closure; invented hierarchy, score and label;
  altered locator, wrong reference/span/related ID, schema/Markdown mismatch;
  source-pin mismatch, lost negative control, reordered output and manifest corruption.
- Publication verifies fresh paths, exact written members, ZIP CRC and manifests.
  A second independent process reproduces **10/10 files and the ZIP byte-for-byte**.
- All seven input ZIP pins, CRCs, manifests and accepted PASS gates verified. Exact
  upstream archive/member/data-row hashes resolve without fuzzy matching.

The audit consumes the accepted R4.2 BHSA 2021 native snapshot, not a new Text-Fabric
execution. R1.1 ZIP and legacy v6 package recovery are not prerequisites for this
authorized accepted-source registry and were not substituted or reconstructed.

## Critical source spot-checks

| Human judgment | Preserved source distinction |
| --- | --- |
| 1:14 | Overt source event P:853270; no removal or inferred later messenger identities |
| 1:16/17/18 | P:853300 / P:853321 / P:853346; identity and first appearance UNRESOLVED, named role blank |
| 1:22/2:10 | MR1_EXPLICIT_CLOSURE=false; F000020/G0 and F001232/G1 retained; 2:10 CSF 18 remains separate |
| 2:9 / 2:11 | Human internal-vs-new-paragraph distinction; exact participant panels retained |
| 3:1 / 3:2 | Native transition evidence without a fabricated MR1 event; actual 3:2 CSF distinct |
| 31:40 | MR1 closure, CASE025 and S02135 evidence retained independently |
| 32:1 | MR1 closure and CASE026 remain distinct from Elihu introduction |
| 32:2–5 | All four native control panels; CASE027 not converted to a marker |
| 27:1/29:1; 32:6/34:1/35:1/36:1 | Supplied same-level relations preserved, no subordinate reclassification |
| 37:24 | CASE028 human ending context; no direct Elihu→YHWH continuity inference |
| 38:1 / 40:1 / 40:6 | Two peer speech onsets and the explicitly supplied child relation kept distinct |
| 40:3 / 42:1 | The two human-reviewed response onsets remain peers |
| 42:7 | MR1 way0:["500411"], csf:["56"] SIMPLE_AMR and HR1 CASE030 separately linked |
| 42:16 | NO_BOUNDARY human control despite 26 exact source/context links; formal presence is not a boundary |

19 negative-control rows retain internal-vs-peer distinctions, messenger ambiguity,
non-MR1 endings/3:1, no global parent for 2:11, no subordinate reclassification of
27/29 or later Elihu speeches, continuity caution, internal 40:1 and NO_BOUNDARY 42:16.

## Final artifacts

- Synthetic: `results/hsa1_synthetic_lf_final_20260922/`
- Final: `results/hsa1_structural_adjudication_lf_final_20260922_a/`
- Rerun: `results/hsa1_structural_adjudication_lf_final_20260922_b/`
- ZIP: `results/hsa1_structural_adjudication_lf_final_20260922_a_results.zip`
- Log: `results/hsa1_structural_adjudication_lf_final_20260922_a_run.log`
- ZIP bytes: **555911**
- SHA256: `9ed87863ccc4388cf608d72675ba69354846c2376e3d764c96f5a79c2599a885`

Earlier exploratory HSA1 audit outputs are not the final artifact. All generated
results/logs and one-time local authoring utilities stay ignored. Intended tracked
files: HSA1 config, source and synthetic fixture, tests, human Markdown/CSV, spec,
usage, this report and HANDOFF. No existing analytical Python core was modified.

Next required human review is **Job 3–26 speech-unit structure**. 2:11 is accepted
as a paragraph onset; whole-book hierarchy remains incomplete. **R4.3 whole-book
parentage remains blocked pending dialogue-unit review.**
