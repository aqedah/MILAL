# MFR.0.2R-Q1.4 validation report

Baseline: `6afd569fb7b625a40e42232e99ff3202077362c4`.
Stage: Independent Composite Surface Construction Adapter / Cross-Family
Configuration Correspondence / Composite Source-Binding Qualification.

## Method and preservation

This additive adapter consumes frozen raw Job observations and candidate IDs.
It discovers overlapping local constructions from exact native attachments and
surface adjacency before examining relations. Composite families are data-derived;
cross-family correspondence never merges families. Positive binding requires a
resolved internal position mapping and a pair-specific non-generic witness chain.
Existing SB06/SB11 qualification and frozen Q1.3 compatibility remain authoritative
for their respective operations. No new relation type is invented.

All 510 frozen file pins, the 1,049,504 raw candidate records, all 195 baseline
relations and all 13 human judgments remain unchanged. Reference identity,
closure targets and canonical hierarchy are not adjudicated. Numbers and Bosman
are explicit post-freeze fixtures, not additional whole-book analysis targets.

Native `Adju` phrases remain native adjunct evidence. In particular, the storm
phrases are not relabeled `Loca`: their semantic frame remains
`UNRESOLVED_NATIVE_ADJUNCT`. Corresponding common-noun lexical roles may contribute
to a generic native-pattern chain. Proper names, including object/addressee names,
cannot act as standalone non-generic lexical anchors.

## Empirical observations

| Measure | Count |
|---|---:|
| Surface spans / independent spans | 275 / 275 |
| Unresolved spans / overlapping spans | 0 / 86 |
| Composite profiles / families | 275 / 239 |
| Same-family / cross-family correspondences | 225 / 3,415 |
| Positive composite bindings | 144 |
| Raw pairs evaluated for composite evidence | 40,035 |
| Baseline / retained / newly qualified | 195 / 195 / 48 |
| Total relations | 243 |
| Mother / parallel / overlay | 173 / 70 / 0 |
| Compatibility conflicts / true decision pivots | 0 / 0 |

Binding counts are correspondence counts, not relation counts. There are 64
COMPOSITE_QUALIFIED pair rows including corroboration of previously qualified
relations. The 48 new outcomes are all PARATACTIC. Nonselection is UNDECIDED;
compatible additional peers are not decision pivots.

### Job controls

- **27:1 / 29:1:** independently discovered three-component constructions
  `[499251,499252,499253]` and `[499383,499384,499385]`, with overlapping two-component
  prefixes. The three components are `ויסף איוב`, `שאת משלו`, `ויאמר`.
  Their differing native configurations remain different families. Resolved
  cross-family position correspondence, lexical-role chains and native dependency
  pattern chains qualify the three corresponding existing pairs as PARATACTIC.
  No control identity or expected relation was used in discovery or qualification.
- **1:6 / 1:13 / 2:1:** 1:6 has `[497539,497540]`; 1:13 has no independently
  supported composite span under this adapter. 2:1 has `[497624,497625]`,
  `[497626,497627]` and the overlapping extension `[497626,497627,497628]`.
  The first correspondence corroborates two baseline relations; the second adds
  two PARATACTIC outcomes. No common hierarchy or complete narrative unit is imposed.
- **38:1 / 40:1 / 40:6:** speech constructions are preserved at all three
  locations. 38:1 and 40:6 preserve the paired storm `Adju` phrase, including
  article/form differences; native-pattern plus common-noun role correspondence
  qualifies `P500078-500270` and `P500079-500271` as PARATACTIC.
  Comparisons involving 40:1 remain CROSS_FAMILY_SUPPORT_ONLY: shared speaker and
  addressee names do not replace the absent paired non-generic witness.
- **Ordinary dialogue formulas:** 35 bare repeated-formula spans, 211 same-family
  comparisons, 493 blocked generic-only comparisons and **zero positive bindings**.
- **31:40:** no closure target or 27/29 extent was inferred from this control.

### External fixtures

All five Numbers alternatives remain EVIDENCE_ONLY:
`P443836-443840` HYPOTACTIC and PARATACTIC; `P443836-443956`,
`P443837-443841`, `P443837-443957` PARATACTIC. No fixed recovery count was imposed.
Only the exact existing fixture's necessary contiguous blocks (10 clauses) were
loaded for these diagnostics; no full Pentateuch candidate universe was generated.

Bosman source 504907 has no independent span membership; source 504910 has
independent membership in `[504910,504911]`. Both reference identities remain
UNRESOLVED. The existing 22-clause fixture and frozen reference records are retained.
Control IDs occur only in post-freeze selectors/configuration and diagnostics.

## Validation and release

- Syntax/static parsing: 8 new Python files passed.
- Focused tests: 68 passed; failures/errors/skips 0.
- Synthetic: S1–S12 plus deterministic rerun, 13/13 checks passed. Inspected
  human-facing `results/q14_synthetic_07/review.md`. The 100 same-speaker and
  same-addressee bare formulas produce 4,950 comparisons and zero positive bindings.
- Full regression: **2,765 passed in 763.156 seconds**, failures/errors/skips 0.
- Every one of the 34 gates has a negative mutation/test in the focused suite.
- Validated source/config/test fingerprint:
  `ebab33dbe1cae357daaaab7bb82e66134fc03c72d114237c36dc9bc0b513fcce`.

Full regression log:
`D:\MILAL_runs\mfr02r_q14_20260926\regression_final.log`.
Receipt: `D:\MILAL_runs\mfr02r_q14_20260926\regression_final.json`.
The reusable regression helper retains its historical `baseline` field; the
Q1.4 baseline is independently checked against the 510 frozen pins and the
required Git ancestor shown above. All receipt fingerprints match current code.

Independent D:/F: executions reproduced all counts and byte-identical final
manifests. **34/34 final gates PASSED**. Both archives exist on disk; both CRCs
and all member manifests passed. The final A/B ZIP bytes are identical.
Each archive contains 47 members.

RESULT ZIP A:
`D:\MILAL_runs\mfr02r_q14_20260926\release_a_results.zip`

RESULT ZIP B:
`F:\MILAL_runs\mfr02r_q14_20260926\release_b_results.zip`

ZIP SHA256 (both):
`fdfe8b9dfb0839d35b54dc71501e1fe506fe3d658945534f351aef6f9da93349`

External final verification receipt:
`D:\MILAL_runs\mfr02r_q14_20260926\release_a_verification.json`.
Human-facing outputs 15/20/21 and synthetic review were inspected; exact
Job node/phrase evidence was also checked in `job_diagnostic_data.json`.
Earlier diagnostic drafts are not releases and must not replace these ZIPs.

Final status: `VALIDATED_NOT_HUMAN_ACCEPTED`.
Readiness: **READY_FOR_MFR_0_2R_Q1_5**; Q1.5 has not been started.

## Repository changes

- `src/milal_q14_spans.py`: independent spans and lossless composite profiles.
- `src/milal_q14_binding.py`: position correspondence and pair-specific binding.
- `src/milal_q14_pipeline.py`: frozen raw-pair streaming and Q1.3 re-audit.
- `src/milal_q14_controls.py`: post-freeze Job, Numbers and Bosman diagnostics.
- `src/milal_q14_validation.py`: 34 computed release gates.
- `src/milal_q14_runner.py`: verified inputs, deterministic execution and ZIP release.
- `src/milal_q14_synthetic.py`: synthetic constructions and negative controls.
- `tests/test_milal_q14.py`: 68 focused tests including every gate's negative case.
- `config/mfr_0_2r_q14_job.json`: source pins and post-freeze selectors.
- `docs/MFR_0_2R_Q14_SPEC.md`, `docs/README_MILAL_MFR_0_2R_Q14.md`,
  `docs/MFR_0_2R_Q14_RESEARCHER_SOURCE.txt`, this report and `docs/HANDOFF.md`:
  specification, execution, exact authority, validation and continuity.
- `.gitattributes`: preserve exact researcher-source bytes.

Generated results, archives, logs and the four pre-existing untracked PDFs are
excluded from the commit. No earlier analytical core was edited.

## Limits and next step

The implemented native-attachment adapter does not claim exhaustive construction
coverage. Span membership is observational, not final textual constituency.
Unmapped or unbound candidates remain available; no ranking or top-N reduction
was applied. Technical readiness does not constitute human structural acceptance.
Q1.5 requires separate authorization and has not been started.
