# R4.0 validation — 2026-09-21

R4.0 whole-book source-trigger inventory completed with 34/34 gates PASS. This
is technical validation of an inventory/scaffold, not acceptance of any final
macro boundary or hierarchy. Starting commit:
`5cfb91847bc967858c75cf850050036b4e4c5bc6`. The commit introducing this report
contains the validated R4 implementation; its ending SHA is reported after push.

## Source recovery and identity

The initial preflight stopped before implementation because R3c.3/PROV1/HR1
packages were not local. The researcher restored them. PROV1/HR1 have download
suffixes (1)/(2); their exact supplied hashes match the accepted originals.
No replacement, filename-based identity inference or fuzzy linkage was used.
All four ZIPs passed CRC, safe/unique member names and complete manifests.
Their status/gates/source-chain references were verified. HR1's six source-link
tables were independently rederived by the frozen non-analytical linkage code
and matched the accepted tables exactly after CSV decoding.

| Source layer | Actual local path | Verified SHA256 |
| --- | --- | --- |
| MR1 accepted marker provenance | `C:\MILAL\results\mr1_real_final_20260921_a_results.zip` | `9f287dca2a7689e04f37b4a9dbcfe53dd714dcc8dc9d1a702f46f476f6537ec0` |
| Frozen R3c.3 review evidence | `C:\MILAL\results\r3c_3_windows_20260919_091111_results.zip` | `5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981` |
| PROV1 formal/provenance evidence | `C:\MILAL\results\prov1_windows_20260920_081304_results(1).zip` | `38c6703721e2f9cca590ab96d64d7a2860a3d075e059cabeb2abe9eb6708c482` |
| HR1 exact human case linkage | `C:\MILAL\results\hr1_human_review_linkage_20260921_114012_results(2).zip` | `7566dcd6191da1b7e4d29b11af4a44c37511dcf0fefa24449a0489ee97c64191` |
| Committed human judgments | `C:\MILAL\docs\HUMAN_REVIEW_PILOT_ADJUDICATION.csv` | `4fb8c15a9ae530e778122f97c3ffcdcc78ded89f534535e4c7afe5cb2272abe3` |

Current canonical data:
`C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
BHSA 2021 / Text-Fabric 13.1.0 loads directly. All 65 loaded TF source-file
hashes match accepted MR1 metadata. All 2938 clause memberships, 2977 native
atoms and 39 multi-atom clauses match MR1. PROV1's 20,839 atom/level records
resolve to all native IDs/order/references with exact reconstructed hashes.
`09_evidence_source_inventory.csv` records all 70 consumed sources and hashes.
R2/R3 original rows are consumed as materialized provenance inside accepted
PROV1, not reconstructed from unavailable raw artifacts or rerun pipelines.

MR1 facts reverified: 2938 surface, 56 CSF, 2 closures, 170 Way0, 5 positive /
165 negative, 3166 EXACT audit rows, four historical-schema export hashes equal
their historical comparison hashes. MR1 acceptance here is marker provenance
only, not acceptance of historical hierarchy or macro importance.

## Whole-book inventory counts

| Record type | Count |
| --- | ---: |
| MR1 CSF (SPEECH_FRAME_CANDIDATE) | 56 |
| MR1 explicit closures | 2 |
| MR1 Wayhi-positive | 5 |
| Total MR1 marker events | 63 |
| Retained Way0 audit records | 170 |
| Negative Way0 rows promoted as markers | 0 |
| Formal bundle/window occurrences | 12,722 |
| Explicit linked family occurrences | 15,292 |
| Candidate native atom anchors | 2,976 |
| Candidate/source-locator evidence links | 39,414 |
| Adjacent candidate-anchor relations | 2,975 |
| Bounded positional zone overlays | 2,975 |
| Control locations | 16 |
| Human records, unchanged | 30 |
| Human reviewed verse scopes | 6 |
| Preserved extension dependency rows | 3,540 |
| Preserved HR1 source locators | 1,018 |
| Singleton contexts not promoted from rarity | 2,673 |
| Whole-book native atom coverage rows | 2,977 |

The nearly complete candidate coverage is an important limitation of this broad
inventory: all repeated formal-window endpoints were retained, including
low-resolution classes. **2,976 candidates are not 2,976 macro boundaries.**
Raw multiplicity also does not measure independent corroboration. No pruning,
scoring, ranking, threshold fitting or source-trigger modification was applied.
The sole atom without an eligible trigger is 587997 (clause 497887, Job 5:27);
it remains in coverage with no invented candidate. Job 42:17 is included through
atom 590593 and retains only its actual source-derived candidate evidence.

Zones use native atom index distance <= 8 in bounded forward windows; all
eligible overlapping windows remain. Changing that review width would not
change candidate identities. No transitive grouping or macro unit is created.

## Complete control audit

Formal counts below mean all occurrence spans overlapping each exact control
verse, not independent votes or automatically adjudicated boundaries.

| Control | MR1 events | Formal occurrences | Exact HR1 boundary case |
| --- | ---: | ---: | --- |
| 1:1 | 0 | 15 | none |
| 1:6 | 1 | 30 | none |
| 1:13 | 1 | 20 | none |
| 2:1 | 1 | 37 | none |
| 2:11 | 0 | 39 | none |
| 3:1 | 0 | 8 | none |
| 27:1 | 1 | 22 | none |
| 29:1 | 1 | 22 | none |
| 31:40 | 1 | 15 | CASE025 |
| 32:1 | 1 | 10 | CASE026 |
| 32:2 | 0 | 9 | CASE027 |
| 37:24 | 0 | 10 | CASE028 |
| 38:1 | 1 | 16 | CASE029 |
| 40:1 | 1 | 16 | none |
| 42:7 | 2 | 19 | CASE030 |
| 42:16 | 0 | 21 | none |

All 16 real controls have some source evidence, often formal evidence alone.
NO_MATCHING_SOURCE_EVIDENCE is not forced into a real row; a synthetic no-source
control tests that required behavior. Absence of MR1 at 42:16 is explicitly
retained despite the requested control and available formal evidence.

## Focus inspection and unresolved questions

- **27:1 / 29:1:** both have TAKE_MASHAL+AMR, BASIC profile / CORE scope and
  22 overlapping formal occurrences each. Complete bundle/window IDs, family
  IDs and levels are displayed separately; equal counts are not identity or
  equal macro-level importance. Their formal/marker relationship remains for review.
- **31:40 / 32:1 / 32:2:** preserve three human cases rather than one merged
  event. Closure תמם+דבר retains atom 589751 independently; שבת+ענה spans
  589752/589753. 32:2 has exact CASE027 and formal evidence but no MR1 marker.
  One boundary versus termination–transition–introduction is unresolved.
- **37:24 / 38:1:** native adjacency 590212→590213 has atom distance 1 and
  verse distance 1. CASE028 ending and CASE029 beginning remain exact human
  statements. No direct Elihu-to-YHWH discourse continuity is inferred; Job
  remains the explicit addressee.
- **38:1 / 40:1:** both ANSWER+AMR with Job as explicit addressee. MR1's
  historical observed fields distinguish 38:1 adjunct `מן ה סערה` /
  SCOPE_EXPANDED from 40:1 CORE scope. Both retain EXPANDED csf_profile.
  The formal family evidence is shown, with no predetermined shared hierarchy level.
- **42:7:** separate positive Wayhi atom 590552 and SIMPLE_AMR atom 590554,
  19 formal occurrences, exact CASE030. Co-location is established; independent
  corroboration and final macro status are not automatically asserted.
- **42:16:** no MR1 marker, 21 formal occurrences, no exact HR1 boundary case.
  The control did not manufacture a marker.

The six human verse scopes retain 3/3/3/2/2/5 native atoms respectively and all
23/16/13/17/21/27 panel participants (117 total). Their judgments were not
narrowed to invented atom decisions. All 30 original human rows remain verbatim:
CLEAR 21, PARTIAL 5, INSUFFICIENT 4. CASE007–012 dependency and all associated
source locators are preserved without generalizing their judgments to other events.

## Validation and output package

- Syntax PASS for all new Python modules/tests; both PowerShell runners exercised.
- Full existing + stage regression **336 PASS**, no failures/errors/skips:
  273 prior tests plus 63 R4 tests. All 63 R4 tests were rerun after the final
  focus-field presentation additions and passed.
- Synthetic packet inspected before real execution; **34/34 gates PASS**.
- Both real processes: exit 0, **34/34 gates PASS**; every gate has a negative
  test/mutation, including manifest bytes/member corruption.
- Actual source files rehashed before publishing; disk, ZIP CRC, member bytes
  and manifest verified. Two independent processes produce **21/21 identical
  member bytes and identical complete ZIP bytes**.
- Full 324-line focus report and whole-book control/coverage inventories inspected.

Local ignored artifacts:

- `C:\MILAL\results\r4_0_synthetic_validated_20260921\`
- `C:\MILAL\results\r4_0_real_20260921_a\`
- `C:\MILAL\results\r4_0_real_20260921_a_results.zip`
- `C:\MILAL\results\r4_0_real_20260921_a_run.log`
- `C:\MILAL\results\r4_0_real_20260921_b\`
- `C:\MILAL\results\r4_0_real_20260921_b_results.zip`
- `C:\MILAL\results\r4_0_real_20260921_b_run.log`

Both real ZIP SHA256:
`c313d102e65854c4d40ff9efac716f78a2388750e1c983b200655984ad7ded47`.

## Repository changes and remaining work

New source modules: `src/milal_r4_0_sources.py`,
`src/milal_r4_0_macro_boundary_inventory.py`, `src/milal_r4_0_synthetic.py`.
New config: `config/r4_0_job.json`. New tests:
`tests/test_r4_0_macro_boundary_inventory.py`. New runner:
`scripts/run_milal_r4_0_windows.ps1`. Documentation: `docs/R4_0_SPEC.md`,
`docs/README_MILAL_R4_0.md`, this report, and updated `docs/HANDOFF.md`.

No final hierarchy/parentage, macro composition, scores/rankings or new
rhetorical/theological labels were generated. Legacy hierarchy was not reused.
Frozen R1–R3/PROV1/HR1/MR1 analytical cores and input/output bytes are unchanged.
Generated data are not committed. Researcher review of this broad inventory and
positional zone convention is the next task; hierarchy questions remain open.
