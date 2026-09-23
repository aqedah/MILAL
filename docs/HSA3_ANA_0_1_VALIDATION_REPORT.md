# HSA3-ANA.0.1 validation — 2026-09-23, computer A

Starting commit: `f1292ba51b90fd545069741ee5ccce3d63d9704a`.
Implementation and technical validation are complete. No hypothesis has received
human acceptance. All A–G parentage questions remain open; R4.4 is not started.

## Executed checks

| Check | Result |
| --- | --- |
| Python syntax / Windows runner execution | PASS |
| New unit tests | 58 passed, 0 skipped |
| Full regression | 737 passed, 0 skipped (includes the 58 new tests) |
| Existing HR1 synthetic self-test during regression | 22/22 gates PASS |
| ANA synthetic runner/self-test | 32/32 gates PASS |
| Actual BHSA 2021 / accepted-artifact audit | 32/32 gates PASS |
| Negative gate coverage | 31 computed gates each mutated to FAIL; manifest corruption also rejected |
| Frozen repository files | 89/89 SHA256 unchanged |
| Accepted upstream ZIPs | 12/12 exact hashes and CRCs verified |
| Native feature files | 70 loaded `.tf` hashes verified again after execution |
| Final ZIP / manifests | CRC PASS; all 6 nested/current manifests PASS |
| Evidence links | 251 exact serialized source-row hashes resolved independently |
| SEAM_D/E addendum links | Exact original case-row hashes verified |
| Independent actual process rerun | ZIP and all 78 members byte-identical |
| Independent synthetic process rerun | Byte-identical; exercised in new tests |
| Human-facing outputs | Synthetic worksheet and actual Hebrew focus/inventory panels inspected |

Syntax command: `.venv/Scripts/python.exe -m compileall -q` for both new source
modules and the new test module. New tests used `unittest discover -s tests -p
test_hsa3_ana_response_frame.py -q`; full suite used `unittest discover -s tests -q`.
Actual runs used `scripts/run_milal_hsa3_ana_windows.ps1 -TfData ... -Out ...`.
The final full suite took 108.908 seconds. No regression was weakened or skipped.

## Actual source and inventory

BHSA: `C:\Users\yisaa\text-fabric-data\github\ETCBC\bhsa\tf\2021`.
Dataset version 2021; Text-Fabric 13.1.0; Job book node 426618.
The metadata records exact paths, feature versions and file hashes.

Native coverage: **10,912 words / 2,938 clauses**. Whole-book lex_utf8 ענה
selection returns **62 occurrences**: **60** `<NH[` answer occurrences and **2**
`<NH=[` be-lowly homonym occurrences, at **30:11** and **37:23** (both piel).
No homonym is counted as a response event. No root was invented from spelling.
Counts are empirical observations, not corpus-semantic constants.

| Primary construction | Occurrences |
| --- | ---: |
| FORMULAIC_CSF | 4 |
| DIALOGUE_TURN_CSF | 16 |
| DIRECTED_ANA_CSF | 9 |
| RESPONSE_REQUEST | 1 |
| ANSWERING_CESSATION | 1 |
| SELF_DECLARED_RESPONSE | 1 |
| NEGATED_OR_WITHHELD_RESPONSE | 12 |
| OTHER_ANA | 10 |
| NON_ANSWER_HOMONYM | 2 |
| FIRST_PERSON_RESPONSE_PROSPECT | 4 |
| FIRST_PERSON_DIRECTED_RESPONSE | 2 |
| Total | 62 |

The classifications preserve separate formal/contextual fields and never assert
a specific semantic antecedent. FIRST_PERSON_RESPONSE_PROSPECT does not erase
conditional, interrogative or optative ambiguity. RESPONSE_REQUEST describes the
31:35 wish construction, not an impf-only/jussive morphological claim.

## Source spot-checks

| Locus | Verified evidence | Limit retained |
| --- | --- | --- |
| 2:13 / 3:1 | Silence DBR with אין; Job opens mouth | Context for 3:2, not a new parent rule |
| 3:2 | Word 336847, clause 497689; formal CSF | No automatic semantic RESPONSE_TO; accepted 3:1/3:2 relations unchanged |
| 31:35 | Word 343759, clause 499611; explicit שדי subject, impf and first-person suffix in wish context | Request, not actual response; no שדי=יהוה identity assertion |
| 31:40 | Clause 499623, תמו דברי איוב | All three HSA2-F relations preserved |
| 32:1 | Word 343815, infinitival answer clause 499625; mother 499624 שבת; explicit Job object | Cessation does not create CHILD_OF 31:40 |
| 32:6 | Word 343886, clause 499638, formal CSF | Not sufficient alone to resolve Elihu's role |
| 32:12 | Word 343961, clause 499663 → 499662 → 499661 containing אין | Source-linked negative context; no guessed nearest-negative attachment |
| 32:14 | שוב in אשיבנו, no ענה lexeme | Response-role context remains visible |
| 32:15–17 | Negative answer forms, then word 343999 hif impf with אף אני | Explicit self-response language; no automatic fourth-friend classification |
| 33:12–14 | First-person answer with second-person suffix; negative third-person answer; then אל with דבר | 33:13 implicit subject referent stays unresolved |
| 36:1 | Clauses 499931–499932, יסף + אמר | NO_ANA / ADD_SPEECH |
| 37:24 / 38:1 | No ANA at 37:24; word 345442, clause 500078 with YHWH subject and Job object | Adjacency does not supply a response antecedent |
| 38–42 | All inventory occurrences retained, including additional 40:2 and 40:5 | 40:2 remains OTHER_ANA; 40:5 retains explicit negative response evidence |

32:2–5 panels also preserve מענה noun/context without misidentifying it as the
ענה verb lexeme. 34:1/35:1 remain formal CSFs; 32:20's prospective first-person
form is in the complete inventory. Every occurrence remains independently visible.

## Preservation and pending hypotheses

New human judgments **0**; new structural relations **0**. Existing **59** human
judgments, **61** nodes, **205** relations and **57** unresolved parent rows remain
unchanged. The complete **62-member** HSA3-PREP archive is nested byte-for-byte;
therefore all seven A–G cases and review fields remain unchanged.
Canonical historical human-accounting hash:
`3db2befcdd32066a48561ab214a55f37f51f9f62b7cb1e5c867194acab54fde5`.
Individual frozen repository hashes and nested source/member hashes are also checked.

Exactly four unadjudicated candidate overlays: ANA-C1 POST_CLOSURE_TRANSITION
(31:40→32:1); ANA-C2 LONG_DISTANCE_RESPONSE (31:35→38:1); ANA-C3
CONTRASTIVE_ANA_FRAME (32:1→38:1); ANA-C4 ELIHU_WITHIN_ANA_RESPONSE_INTERVAL
(32:1–38:1). All have `automatic_resolution=false`, no parent and no new human
judgment. Q2–Q5 await source-supported human relation, UNRESOLVED or
INSUFFICIENT_EVIDENCE. Q1 displays the frozen counterexample without reopening it.

## Final artifacts

Actual:
`results/hsa3_ana_0_1_response_frame_final_20260923_a_results.zip`

SHA256: `b7238ddcb0ee0940bd6a397a23bbef95a18da0dacb5af98e2b1b17396eb89294`.

Independent repeat:
`results/hsa3_ana_0_1_response_frame_repeat_20260923_a_results.zip`
has the same SHA256 and all 78 members match byte-for-byte.

Synthetic:
`results/hsa3_ana_0_1_synthetic_final_20260923_a_results.zip`

SHA256: `8fa90c6630dda058680c46a5b68aabbc657e79cf1537c52582103d8693d0aa79`.

Earlier `_a`/`_b` development runs are superseded by the final artifacts above.
All outputs, ZIPs and logs remain local and ignored. No empirical data is committed.
Cross-machine byte equality is not claimed because exact machine paths are
deliberately recorded in provenance; same-input local independent reruns are verified.
