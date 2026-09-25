# MFR.0.2R-H0 — Final validation report

**Technical validation passed; whole-book review selectivity remains unresolved.**
The exhaustive universe is intact. H0 exposes 95,929 existing relation candidates
in the default packet, a 90.86% reduction from 1,049,504 pairs. Nevertheless,
2,719/2,938 targets (92.55%) remain required. The machine-readable warning is
**REVIEW_SIEVE_NOT_SELECTIVE**. This is not unconditional readiness for H.

## Required final report

| No. | Item | Result |
|---:|---|---|
| 1 | Start commit | `3925b2b7a170dee2f2777941957a750248bfece8` |
| 2 | End commit | Commit containing this report: `Build human review eligibility sieve`; exact SHA reported after commit |
| 3 | Push | Actual result and remote HEAD verification reported at finalization |
| 4 | Working tree | Only intended H0 files; four existing source PDFs remain untracked |
| 5 | Original candidate universe rows | 1,049,504 |
| 6 | H0 candidate crosswalk rows | 1,049,504 |
| 7 | Deleted candidates | 0 |
| 8 | Frozen file changes | 0 across 451 pinned files, including the prior 422 pins |
| 9 | RELATION_ELIGIBLE | 95,929 |
| 10 | CONFIGURATION_ELIGIBLE | 0 (exclusive class; overlapping configuration reasons remain) |
| 11 | EVIDENCE_ONLY | 849,918 |
| 12 | INSUFFICIENT | 103,657 |
| 13 | Total targets | 2,938, including zero-candidate targets |
| 14 | TARGET_REVIEW_REQUIRED | 2,719 |
| 15 | TARGET_REVIEW_OPTIONAL | 0 |
| 16 | TARGET_ARCHIVE_ONLY | 219 |
| 17 | Tier 1 targets | 30 |
| 18 | Tier 2 targets | 2,689 |
| 19 | Tier 3 targets | 0 |
| 20 | Median candidates before | 126.5 |
| 21 | Median candidates after | 5 |
| 22 | Maximum candidates before | 2,922 |
| 23 | Maximum candidates after | 1,136 |
| 24 | Default human-review candidate total | 95,929 |
| 25 | Candidate reduction percentage | 90.859587%; descriptive only, not a score |
| 26 | Targets with multiple mothers | 602; no mother selected |
| 27 | HYP/PARA competing targets | 1,097 |
| 28 | Multi-source conflicts | 132 H0 reason-bearing pairs, across 42 targets |
| 29 | Global conflict involvement | 75,559 pairs, across 1,129 incoming-target competition sets |
| 30 | Variant involvement | 95,929 pairs, 2,315 incoming-target sets; 2,717 targets including source-side component membership |
| 31 | MFR.0.2A decisions preserved | All 13, exact original-record hashes |
| 32 | All 13 in Tier 1 | Yes; 290 eligible pairs across 30 targets, maximum 81 per target |
| 33 | Valency review cases | 39 atom-binding deferrals; none resolved |
| 34 | Poetry/syntax review cases | 1 existing exception candidate; not resolved |
| 35 | External fixture results | All 628 relation candidates retained: Pentateuch 594, Qohelet 9, Lamentations 9, Isaiah 16 |
| 36 | Full Pentateuch analysis | Absent; no external-book engine or raw corpus extraction run |
| 37 | H0 stage tests | 62 passed; failures/errors/skips 0 |
| 38 | Full regression | 2,465 passed in 759.401 seconds; failures/errors/skips 0 |
| 39 | Critical gates | 34/34 PASS, each with a negative invariant mutation |
| 40 | Deterministic rerun | Final independent A/B files and ZIP bytes identical; CRC/member hashes PASS |
| 41 | ZIP | `D:\MILAL_runs\mfr02r_h0_20260925\release_a_results.zip` |
| 42 | ZIP SHA256 | `d21c171798f02bd46f38fd8d84b2e9d60c3ae626f73d1a8ee384a8a1017af290` |
| 43 | REVIEW_UNIVERSE_REDUCED_WITHOUT_DATA_LOSS | Established technically |
| 44 | READY_FOR_MFR_0_2R_H | Withheld: REVIEW_SIEVE_SELECTIVITY_REQUIRES_HUMAN_REVIEW |

## Selectivity finding — do not silently accept

The target reason VARIANT_COMPONENT occurs for 2,717 targets. Existing component
membership includes source-side members, not just targets with competing incoming
edges. Consequently 404 required targets have no eligible incoming candidate.
183 targets retain more than 100 eligible candidates. Their complete paged cards
remain available; pagination does not erase that aggregate burden.

The former MFR.0.2R packet selected 2,528 targets under its older presentation
logic. H0 has 2,719 required targets under the newly requested T1–T9 criteria.
Thus candidate-level reduction is substantial, while target-level review
selectivity is not established. These are different measurements.

The initial 95% automatic diagnostic missed the observed 92.55% coverage. The
final documented convention is 90%, solely for a warning. No numerical reduction
pass threshold was introduced. The warning does not change eligibility, tiers,
relations or candidate counts. Full regression and independent real execution
were repeated after this correction. Preliminary `real_a/b` are audit attempts;
only `release_a/b` are final outputs.

The unresolved methodological question is whether mere variant-component
membership should require target review, or whether direct structural competition
needs a separate criterion. H0 does not answer that question by weakening frozen
rules or discarding alternatives. The 13-case scope is available for inspection;
no new human adjudication or next stage has started.

## Methodological interpretation and evidence preservation

- Candidate universe and human-review universe are separate. Every original pair
  remains in a one-to-one crosswalk with exact IDs, existing relation/rules,
  physical source-table SHA256 and canonical decoded-row SHA256.
- Class precedence is relation, configuration, evidence, insufficient. The zero
  exclusive configuration count does not erase configuration evidence: all
  structurally involved real pairs already qualify as relation candidates, and
  their global/variant/poetic reasons remain attached.
- H0 source-family conflict means matched rules from multiple source families
  propose differing hierarchy relations. Its 132 reason-bearing pairs are not
  a rewrite of the older MFR.0.2R Jin/Walton conflict table; that frozen table is
  unchanged. No new relation is inferred from either count.
- Evidence-only and insufficient rows are archived from default display, never
  deleted. A correspondence may be evidence even when the original relation
  status is INSUFFICIENT; that original status remains preserved verbatim.
- Binding deferrals are atom-level hypotheses with raw IDs, intervening material,
  construction/valency and corpus evidence. They do not promote every associated
  clause pair. Poetry exceptions remain separate unresolved evidence.
- All 13 human records are displayed after eligibility freeze. Altering a
  historical decision in a synthetic source leaves classification bytes identical.
  No historical HSA/JIN judgment supplies new eligibility.
- New human fields, accepted mothers and parallel peers remain blank. New human
  judgments, canonical mothers and canonical whole hierarchies are all zero.
- No scores, weighted ranking, top-N pruning, distance cutoff, nearest heuristic,
  grammar changes, resumption decisions or closure decisions were introduced.

## Human-facing inspection

The 13-case index shows original configuration Hebrew, original judgment and
rationale, exact source evidence IDs, separate relation/configuration candidate
lists and archive counts. Each target links to every eligible card, grouped into
10-card navigation pages. This is not a top-N selection or preference order.
There are 10,909 card pages in the whole-book output, plus target indexes.

Cards show source/target Hebrew and types, distance, matched Jin/Walton rules,
formal/time/location/participant/reference/domain/lexical evidence, construction
and valency signatures, corpus selectors, Bosman observations, conditional
compatibility/conflicts and variant effects. Readable summaries precede expandable
exact source fields. Participant surface is shown without resolving identity.
Original machine-readable data remains available through the upstream ZIP and
copied manifest; the large raw tables are not duplicated in the H0 ZIP.

Synthetic and actual Hebrew cards were inspected. All 2,938 original observation
records passed the new source/target-field rendering schema check. The special
Job references are post-freeze inventories of all matching source clauses, not
hard-coded decisions. Their output is `job_postfreeze_validation.csv`.

## Controls and validation evidence

Existing Lev 25–26, Num 26 and EDSF cases are covered by the unchanged Pentateuch
fixture relations; Qohelet, Lamentations and Isaiah fixtures are similarly read
from the frozen package. All existing fixture relation candidates survive H0.
No full external analysis is rerun, and control results do not feed eligibility.

- Syntax validation passed; PowerShell runner parsed without errors.
- Stage tests: 18 eligibility tests and 44 integration/gate tests, total 62.
- All requested H0-S1–S15 cases are covered, including preservation of 100 raw
  candidates while displaying only two eligible relations and consolidation of
  multiple matched rules into one card.
- Each of 34 gates has a negative mutation of measured artifact-derived evidence.
  Additional actual file-deletion, manifest, historical-label, schema, synthetic
  release and nonselectivity tests exercise failure paths.
- Synthetic pipeline: 21 pairs preserved, 10 relation cards, 11 evidence-only
  records; independent A/B bytes identical. Synthetic human records are explicitly
  fixtures and never substitute for empirical judgments.
- Final full regression: `D:\MILAL_runs\mfr02r_h0_20260925\regression_final.json`
  and adjacent `.log`; 2,465 tests in 759.401 seconds, no failures/errors/skips.
- The reused regression runner's receipt retains its older MFR.0.2R baseline
  field. H0 separately verifies `3925b2b...` ancestry and 451 frozen hashes;
  the test receipt's current code fingerprint and exact test results are checked.
- Final code/config/test fingerprint:
  `ce70590e3707f5833507958521cd6cc26bfd9af0a97ec88b485322ad9d7a59ab`.
- Initial versus final eligibility crosswalk SHA256 is identical:
  `35cf98a2aa8f08c9b75a4ca6319a58ef9a57af5dde784c3335bfca18536726b4`.
- Frozen upstream ZIP SHA256:
  `93ff58ba3f1498e5e93a4aaf23e15ceb777d54ef2704edf3c15fcffad9f05b7d`;
  CRC, all 2,613 ZIP members, member manifest and extracted files verified.
- Final A: `D:\MILAL_runs\mfr02r_h0_20260925\release_a`.
- Final B: `F:\MILAL_runs\mfr02r_h0_20260925\release_b`.
- Independent B ZIP: `F:\MILAL_runs\mfr02r_h0_20260925\release_b_results.zip`.
- Both ZIPs contain 13,875 members with valid manifests and CRC/member hashes.
- Release receipt: `D:\MILAL_runs\mfr02r_h0_20260925\release_a_verification.json`.
- These are independent Windows executions on computer A, not cross-platform
  validation. No Termux empirical execution is claimed.

## Files changed

- `.gitattributes`
- `config/mfr_0_2r_h0_job.json`
- `docs/HANDOFF.md`
- `docs/MFR_0_2R_H0_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_2R_H0_SPEC.md`
- `docs/MFR_0_2R_H0_VALIDATION_REPORT.md`
- `docs/README_MILAL_MFR_0_2R_H0.md`
- `scripts/run_milal_mfr_0_2r_h0_termux.sh`
- `scripts/run_milal_mfr_0_2r_h0_windows.ps1`
- `src/milal_h0_runner.py`
- `src/milal_h0_synthetic.py`
- `src/milal_h0_validation.py`
- `src/milal_mfr02r_h0.py`
- `src/milal_relation_competition.py`
- `src/milal_review_eligibility.py`
- `src/milal_review_packet.py`
- `tests/test_mfr_0_2r_h0.py`
- `tests/test_review_eligibility.py`
