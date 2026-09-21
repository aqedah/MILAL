# R4.1 validation — 2026-09-21

Starting commit: `fc81663ccddf1fdc343e60d5ee70152850d02103`. The commit containing
this report introduces R4.1; final commit SHA is reported after successful push.
R4.0 is technically accepted by the researcher. R4.1 is technically validated,
with methodological review still pending. No hierarchy/parentage is generated.

## Verified sources

All pins, CRCs, manifests, native BHSA relationships and committed human bytes
passed. All 21 accepted R4.0 members were replayed and matched byte-for-byte in
memory without rewriting R4.0. Sources were rehashed immediately before publication.

| Source | Actual path under C:\MILAL | SHA256 |
| --- | --- | --- |
| MR1 | `results/mr1_real_final_20260921_a_results.zip` | `9f287dca2a7689e04f37b4a9dbcfe53dd714dcc8dc9d1a702f46f476f6537ec0` |
| R3c.3 | `results/r3c_3_windows_20260919_091111_results.zip` | `5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981` |
| PROV1 | `results/prov1_windows_20260920_081304_results(1).zip` | `38c6703721e2f9cca590ab96d64d7a2860a3d075e059cabeb2abe9eb6708c482` |
| HR1 | `results/hr1_human_review_linkage_20260921_114012_results(2).zip` | `7566dcd6191da1b7e4d29b11af4a44c37511dcf0fefa24449a0489ee97c64191` |
| R4.0 | `results/r4_0_real_20260921_a_results.zip` | `c313d102e65854c4d40ff9efac716f78a2388750e1c983b200655984ad7ded47` |
| Human | `docs/HUMAN_REVIEW_PILOT_ADJUDICATION.csv` | `4fb8c15a9ae530e778122f97c3ffcdcc78ded89f534535e4c7afe5cb2272abe3` |

Canonical data: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`,
BHSA 2021 / Text-Fabric 13.1.0. All 65 TF source hashes match MR1.
The source inventory contains 71 actual files (six above plus 65 TF files).
Frozen R1.1/v6.42.12 remain historically unavailable; no legacy hierarchy is used.

## Methodological result and counts

R4.0 saturation is preserved: 2977 atoms, 2976 candidates, **2900 formal-only**,
2975 zones. This motivates evidence-role separation, not a claim that R4.0 failed.

| Output | Count |
| --- | ---: |
| Boundary-oriented source anchors | 69 |
| MR1 CSF | 56 |
| MR1 explicit closures | 2 |
| MR1 Wayhi positives | 5 |
| Exact HR1 CASE025–030 scopes | 6 |
| Formal-only anchors | 0 |
| Exact source-anchor overlap links | 5 |
| Full formal occurrences | 12722 |
| Anchor/formal span relation rows | 1140 |
| Overlapping span relation labels | 3002 |
| Distinct edges (two per anchor) | 138 |
| Edge classification rows (three per edge) | 414 |
| All formal occurrence/edge assignments | 1755636 |
| Incident occurrence/edge assignments | 2400 |
| Same-family/subtype comparison pairs | 693 |
| Controls, including book endpoints | 24 |
| Original human records | 30 |
| Extension dependency rows | 3540 |
| Human source locators | 1018 |
| Preserved Way0 audit rows | 170 |

Edge partitions include the entire book's formal inventory. The large 1755636
count therefore includes remote before/after records and is not local support.
Incident subsets mean immediate ending, crossing or immediate beginning only.
No counts serve as scores, rankings, salience, independent votes or macro decisions.
Formal crossings mean positional/formal continuity, not discourse continuity.

## Inspected profiles

**31:40–32:6:** six separate source anchors cover the four requested locations.
31:40 MR1 closure תממ+דבר is atom 589751; CASE025 retains all three verse atoms.
32:1 MR1 closure שבת+ענה spans 589752/589753; CASE026 retains three verse atoms.
32:2 CASE027 retains 589755–589757 without an MR1 marker. 32:6 CSF event 43,
ANSWER+AMR, spans 589766/589767 and retains historical Elihu speaker identification
with SCOPE_EXPANDED. It is not collapsed into the narrative introduction.
34:1/35:1 ANSWER+AMR and 36:1 ADD_SPEECH+AMR also remain whole-book anchors.

**37:24–38:1:** CASE028 and CASE029 retain their original statements and full
verse scopes. Three exact formal occurrences cross the shared positional edge:
RB00106:W2596L02, RB00108:W2596L03, RB00216:W2596L04. This does not establish
direct Elihu→YHWH discourse continuity. The separate MR1 CSF at 38:1 retains
speaker יהוה, named addressee איוב and adjunct מן ה סערה.

**38:1–42:1:** six MR1 CSFs appear in order. Five are ANSWER+AMR at
38:1,40:1,40:3,40:6,42:1. **38:11 SIMPLE_AMR** is additionally preserved, with
historical IMPLICIT_SELF_QUOTE_P1 speaker source. No example list prunes it.
40:3/42:1 retain Job speaker / YHWH addressee; 40:1/40:6 retain YHWH speaker /
Job addressee. No new speaker-change adjudication or parentage is assigned.

**42:7:** three anchors: Wayhi at 590552, SIMPLE_AMR at 590554, and CASE030's
five-atom verse scope. Their two overlap links preserve identities. MR1 CSF retains
explicit Eliphaz addressee. All formal span and edge IDs remain inspectable.

**42:16:** zero MR1 events, zero exact HR1 cases, 21 overlapping formal
occurrences; status NO_BOUNDARY_ORIENTED_SOURCE_ANCHOR. Book controls alone
likewise never create anchors.

## Exact same-form comparisons

All 693 same-family/subtype pairs are retained. Context is explicitly anchor
overlap plus immediate edge incidence, using exact family IDs, no fuzzy match.

- 27:1 / 29:1 TAKE_MASHAL+AMR: native surfaces exactly equal; 42 shared family
  IDs, 12 left-only and 13 right-only. Historical fields retain the same formula
  and speaker but distinct source events and references.
- 38:1 / 40:1 ANSWER+AMR: surfaces not exactly equal; 11 shared family IDs,
  25 left-only and 23 right-only. 38:1 preserves adjunct/SCOPE_EXPANDED;
  40:1 retains CORE. Both have explicit Job addressee and EXPANDED profile.

These cardinalities only describe exact sets. They imply neither equal hierarchy
level nor different parentage. Complete family IDs, occurrence locators, source
properties, exact token sets and left/right edge keys are in comparison CSV 04.

## Validation

- Syntax: three new Python modules/test files parsed successfully.
- Full regression: **383 PASS**, no failures/errors/skips (336 prior + 47 R4.1).
- Final stage tests rerun after presentation formatting: **47 PASS**.
- Synthetic Windows PowerShell 5.1 run: **32/32 gates PASS**, packet inspected.
- Two real PowerShell 7 runs: exit 0, **32/32 gates PASS** each.
- Every gate has a negative test, including source receipt, missing event/scope,
  relation ID, edges, human record, comparison, forbidden fields and manifest mutation.
- Independent serialized-output audit checked all 1755636 edge assignments,
  69 unique anchor blocks and 693 comparison blocks in the packet.
- Two independent processes: **22/22 files identical; whole ZIP bytes identical**.
  ZIP CRC, disk bytes, complete manifest membership and SHA256 independently verified.

The default Windows PowerShell execution policy initially blocked the local runner;
the successful 5.1 invocation used process-only `-ExecutionPolicy Bypass`.
No persistent machine policy was changed.

## Artifacts and limitations

- `C:\MILAL\results\r4_1_synthetic_final_20260921\`
- `C:\MILAL\results\r4_1_real_20260921_a\`
- `C:\MILAL\results\r4_1_real_20260921_a_results.zip`
- `C:\MILAL\results\r4_1_real_20260921_a_run.log`
- `C:\MILAL\results\r4_1_real_20260921_b\`
- `C:\MILAL\results\r4_1_real_20260921_b_results.zip`
- `C:\MILAL\results\r4_1_real_20260921_b_run.log`

Both real ZIPs (9224096 bytes) have SHA256
`92d01bd0deccd6c77c288cd69e7d1eaebeea289f64378f59b667e4aaa91af966`.

Validated on computer A only. Strict R4.0 member replay includes recorded path
metadata, so relocation to a different filesystem may stop even when source content
hashes match; cross-computer portability has not been claimed or silently relaxed.
The complete 693-pair packet is large (about 1.86 MB); family/event navigation and
focused profiles provide entry points while all evidence remains available.

No hierarchy, parentage, macro ranking, convenience pruning or new interpretive
label was produced. Legacy hierarchy was not reused. All earlier analytical
cores and accepted artifacts, including R4.0, are unchanged. Researcher review of
these boundary-oriented profiles is the next task; hierarchy remains unassigned.

## Repository files

`src/milal_r4_1_boundary_profiles.py`, `src/milal_r4_1_synthetic.py`,
`tests/test_r4_1_boundary_profiles.py`, `config/r4_1_job.json`,
`scripts/run_milal_r4_1_windows.ps1`, `docs/R4_1_SPEC.md`,
`docs/README_MILAL_R4_1.md`, `docs/R4_1_VALIDATION_REPORT.md`, `docs/HANDOFF.md`.
Generated data, ZIPs, logs and external BHSA are not committed.
