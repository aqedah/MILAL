# MFR.0.2R-Q1.2 validation

**Technically validated. NEEDS_ADDITIONAL_SOURCE_REVIEW. H0.1 has not started.**

Baseline: `1bd0cb64390423223acdddcf130733f8f5cc880c` (main, fetched origin/main).
All 484 frozen repository pins verify. The three exact upstream ZIPs and extracted manifests verify; no frozen analytical core or historical output was rewritten. All 1,049,504 raw row identities/hashes and 13 human judgments are preserved. No new human judgment, canonical mother or canonical hierarchy was created.

Authority: [original request](MFR_0_2R_Q12_RESEARCHER_SOURCE.txt), SHA256 `e09039c94d89c5efb8d68c760587bbc7dca6e075f844688fb135ac23fbb1e632`, plus [researcher clarification](MFR_0_2R_Q12_CLARIFICATION.md).

## Validation

- Syntax: nine Python files.
- Focused tests: 71 passed.
- Full regression: 2,633 passed in 742.464 seconds; errors/failures/skips 0.
- Synthetic: 57 checks, including every negative mutation for 34 gates; deterministic bytes and human-facing output inspected.
- Real gates: 34/34 passed. Two independent D/F runs have identical manifests and ZIP bytes.
- Archive: 52 members, 51 manifest entries; CRC and manifest valid.
- ZIP SHA256: `3a3118876006a9eaf7ba5f79b435ab5521cd6d4087711def8854512815816770`.
- Code/config/test fingerprint: `2a931d7486f96edd4f5eb39a038e55055861ba13c7e6aec739e195ea06fa3907`.

Pre-release review found that the new external-fixture path initially omitted the existing Oosting deferred blocker. Q1.2 was corrected and tested through the fixture path; the incomplete first regression log is not a success receipt. The corrected full regression and both real runs use the fingerprint above. Frozen code was not changed.

## Job results

| Measure | Result |
|---|---:|
| raw | 1049504 |
| original_relation_pairs | 95929 |
| q1_qualified | 185 |
| qualified | 195 |
| QUALIFIED_DIRECT | 173 |
| QUALIFIED_CONFIGURATION | 22 |
| profiles | 2938 |
| families | 1594 |
| configurations | 2938 |
| correspondences | 2283 |
| outcome_groups | 195 |
| targets_0 | 2754 |
| targets_1 | 177 |
| targets_2_plus | 7 |
| variant_members | 342 |
| variant_pivots | 7 |
| reference_witnesses | 5854 |
| reference_antecedents | 1329190 |

SB06: 14 qualified witnesses/pairs; SB11: 8. SB01: 173 qualified witnesses; SB04: 1 overlapping direct pair. SB02/SB03/SB10: 0 qualified paths. Direct and configuration qualifications total 173 + 22 = 195.

Q1.2 retains 182 Q1 pairs, adds 13 and does not qualify 3 previously qualified pairs. This is not a rewrite of Q1 or a human rejection of those candidates.

Added: `P497534-499798`, `P497538-497569`, `P497540-497625`, `P497550-497636`, `P497569-497623`, `P497580-497588`, `P497580-497597`, `P497580-497609`, `P497588-497597`, `P497588-497609`, `P497597-497609`, `P497716-498892`, `P498019-498057`.

Not qualified in Q1.2: `P497545-497631`, `P497546-497632`, `P499251-499383`.

In these three cases, Q1 used native atom links with `NA` and/or clause `Coor` links to assemble units. The new operational unit subset requires exact subordinate/speech-complement continuation. In particular Job 27:1 (499251) remains a singleton, while 29:1 (499383) has an independently typed Objc continuation to 499384. Their unequal unit patterns do not bind under this adapter. This is a material boundary-adapter limitation requiring review, not evidence that the 27:1/29:1 correspondence is false. No ID exception was added.

Pivots: `497588` (2 outcomes), `497596` (2 outcomes), `497597` (3 outcomes), `497608` (3 outcomes), `497609` (4 outcomes), `497623` (2 outcomes), `497625` (2 outcomes).
Variant membership here is computed from the new qualified graph, whereas Q1 membership referred to the frozen original graph. Component membership is not a pivot. UNSELECTED remains UNDECIDED.

## Reference and global evidence

| Reference status | Witnesses |
|---|---:|
| EXACT_NATIVE | 0 |
| UNIQUE_SURFACE_CANDIDATE | 376 |
| MULTIPLE_PLAUSIBLE | 3856 |
| UNRESOLVED | 806 |
| NO_CANDIDATE | 816 |

All empirical referential identities remain unresolved. A unique candidate is not an identified referent. PNG, unknown nominal person, lexical recurrence and native clause attachment never become automatic coreference. The new typed-reference adapter is validated synthetically; no antecedent semantics are invented for BHSA `Rela`.

SB12 records four conditional COMPETING_PARALLEL_CHAIN constraints, 195 compatibility rows, 158 components (157 materialized; one symbolic) and 372 materialized variants. It creates zero positive bindings or new edges and chooses no mother/hierarchy.

## Post-freeze controls

Exact fixture scope: 181 clauses and 3,834 existing pairs. No new external candidates or full external-book analysis. Qualified fixture pairs: Pentateuch 75/3,650; Qohelet 3/83; Lamentations 2/52; Isaiah 5/49. These are candidate results, not accepted structures. Oosting deferred targets remain unqualified.

### Five Numbers relation alternatives

All five remain EVIDENCE_ONLY. No recovery count was imposed. Full source profiles, Q1.1 failed conditions, reference witnesses and SB12 effects are retained in `13_q12_numbers_postfreeze_controls.csv`. The qualitative dimension comparison below is derived from those exact stored profiles with `milal_q12_profiles.compare_dimensions`; it does not change qualification.

| Pair | Relation | Different dimensions | Corresponding variants | Result |
|---|---|---|---|---|
| P443836-443840 | HYPOTACTIC | PREDICATE_MORPHOLOGY, CONSTITUENT_STRUCTURE, PHRASE_ARRANGEMENT, SUBJECT_CONFIGURATION, COMPLEMENT_CONFIGURATION, PARTICIPANT_CONFIGURATION, REFERENCE_MORPHOLOGY, LEXICAL_ANCHOR, SPEECH_FORMULA | LOCATION_CONFIGURATION | EVIDENCE_ONLY |
| P443836-443840 | PARATACTIC | PREDICATE_MORPHOLOGY, CONSTITUENT_STRUCTURE, PHRASE_ARRANGEMENT, SUBJECT_CONFIGURATION, COMPLEMENT_CONFIGURATION, PARTICIPANT_CONFIGURATION, REFERENCE_MORPHOLOGY, LEXICAL_ANCHOR, SPEECH_FORMULA | LOCATION_CONFIGURATION | EVIDENCE_ONLY |
| P443837-443841 | PARATACTIC | none | none | EVIDENCE_ONLY |
| P443836-443956 | PARATACTIC | PREDICATE_MORPHOLOGY, COMPLEMENT_CONFIGURATION, PARTICIPANT_CONFIGURATION, LEXICAL_ANCHOR, SPEECH_FORMULA | none | EVIDENCE_ONLY |
| P443837-443957 | PARATACTIC | none | none | EVIDENCE_ONLY |

The opening configurations remain outside a shared operational family because predicate morphology/core constituent patterns differ. The identical לאמר forms alone have no independent nominal/frame anchor or structural content beyond a bare formula; parent configurations do not provide qualified internal correspondence. SB12 does not manufacture missing binding. See the source/target observations, not a claimed known-correct answer.

### Bosman references

- UC-504907 → 504911: independent surface unit currently contains only 504907; conditional legacy evidence involving antecedent 504908 is preserved separately. Reference UNRESOLVED.
- UC-504910 → 504924: independent native Adju continuation supports unit [504910, 504911], but target lexical recurrence still does not establish referential identity. Reference UNRESOLVED.
Both complete old records and candidate reference witnesses are preserved in `14_q12_bosman_postfreeze_controls.csv`. No provisional edge or conditional reachability is used to prove itself.

## Methodological interpretation and limits

Observed profiles retain speech formulas, TIME/LOCATION structures, morphology and source nodes. Data-derived compositional families are separate from observed identity. Correspondence requires independent units, matching internal positions and an explicit corresponding-role nominal anchor or pair-specific frame witness. Whole phrases need not be identical. No score, feature-count threshold, fuzzy identity or control-specific family is used.

The empirical configuration positives number 22: 14 opening and 8 internal correspondences. They include repeated messenger escape/report constructions, temporal frames and a few other formally anchored configurations; ordinary repeated speech formulae do not form a broad all-to-all relation universe. The synthetic 100-formula negative remains valid. All positive witnesses, including long-range ones, remain candidates for human review.

The unit adapter is a limited typed-native/adjacency subset, not a universal boundary theory. Different sequence lengths and some predicate/constituent variants remain separate families. Reference search covers explicit nominal subject/object/complement candidates; other words/phrases remain in source observations/profiles. These limitations, including the three Q1 differences and still unresolved control correspondence, require additional source review.

**Readiness: NEEDS_ADDITIONAL_SOURCE_REVIEW.** Technical gates do not establish methodological acceptance. Review the independent unit-boundary and cross-family correspondence contracts, and the reference evidence gaps, before separately authorizing H0.1.

## Reproducible artifacts

- A: `D:\MILAL_runs\mfr02r_q12_20260926\release_a`
- B: `F:\MILAL_runs\mfr02r_q12_20260926\release_b`
- ZIPs: each directory path plus `_results.zip`.
- Verification: `D:\MILAL_runs\mfr02r_q12_20260926\release_a_verification.json`.
- Regression: `D:\MILAL_runs\mfr02r_q12_20260926\regression_corrected.json` and `.log`.
- Synthetic: `C:\MILAL\results\q12_synthetic_02\receipt.json`.
- [Execution instructions](README_MILAL_MFR_0_2R_Q12.md).

## Repository files

- `.gitattributes`
- `config/mfr_0_2r_q12_job.json`
- `src/milal_q12_binding.py`
- `src/milal_q12_controls.py`
- `src/milal_q12_pipeline.py`
- `src/milal_q12_profiles.py`
- `src/milal_q12_references.py`
- `src/milal_q12_runner.py`
- `src/milal_q12_synthetic.py`
- `src/milal_q12_validation.py`
- `tests/test_mfr_0_2r_q12.py`
- `docs/MFR_0_2R_Q12_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_2R_Q12_CLARIFICATION.md`
- `docs/MFR_0_2R_Q12_SPEC.md`
- `docs/README_MILAL_MFR_0_2R_Q12.md`
- `docs/MFR_0_2R_Q12_VALIDATION_REPORT.md`
- `docs/HANDOFF.md`

Large source/result archives, logs, caches and BHSA data are not committed. Four pre-existing user research PDFs remain untouched and untracked.
