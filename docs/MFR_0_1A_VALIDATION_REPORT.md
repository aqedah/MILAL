# MFR.0.1a validation report

**MARKER_EVIDENCE_CONSOLIDATED**.
**READY_FOR_MFR_0_2_HUMAN_ADJUDICATION**.
This readiness is for consolidated human evidence review. No hierarchy, closure,
family validity, participant identity or root has been adjudicated.

## Git and authority (1–3)

Start commit: `86b739c6f1f3ebc4675588a3452edd09e99387fd`. Branch `main`; verified origin
`https://github.com/aqedah/MILAL.git`. The final commit is the commit containing this
report, message `Consolidate marker evidence for human review`. The final response
records its exact hash, push result and clean-tree verification without putting a
self-referential hash here.

Authority: [exact request](MFR_0_1A_RESEARCHER_SOURCE.txt), SHA256
`627691f10b8fd0d19530a740ce6e2b05c6bdad29d4ac544b173a22b0d43c9f00`.
[Specification](MFR_0_1A_SPEC.md); [Windows/Termux commands](README_MILAL_MFR_0_1A.md).
MFR.0.1 original semantics and all 362 pinned baseline files remain unchanged.
The new modules have a separate namespace. No historical JIN/HSA code was reused.

## Frozen raw counts (4–8)

| measure | count |
| --- | --- |
| atoms | 2977 |
| coverage | 4092 |
| families | 5717 |
| force | 1120 |
| markers | 1120 |
| membership | 7357 |
| nested | 4092 |
| observation | 2938 |
| relations | 2435 |
| signatures | 41405 |

These counts were reread from the exact frozen MFR.0.1 ZIP and verified against its
complete manifest. No new marker discovery or BHSA reload occurred. The original
ZIP is included byte-for-byte, with SHA256
`a0904cb11931790e6d78d53f5f67731aba067c5feca4ed50dd10eb11e268b05d`.

## Bundles and family evidence (9–16)

| measure | count |
| --- | --- |
| MULTI_RESOLUTION_BUNDLE | 1012 |
| REPEATED_OCCURRENCE_BUNDLE | 322 |
| SINGLETON_EXPLICIT_BUNDLE | 958 |
| SINGLETON_GENERIC_BUNDLE | 134 |
| SINGLE_RESOLUTION_BUNDLE | 402 |
| unique evidence bundles | 1414 |
| original families represented | 5717 |
| duplicate occurrence-set bundles | 1012 |
| families represented in multi-family bundles | 5315 |
| lattice relations | 2581 |
| expansion relations | 62 |

Each exact occurrence set has one bundle, with every distinct contributing family
ID, construction definition and signature resolution retained. Multi-resolution
and repeated/singleton categories overlap; they are not quality rankings. Singleton
explicitness uses the frozen marker's existing formal-explicitness field, including
configuration shifts. Bundle singleton counts differ from slot-repeat singleton
counts because these measure different things.

Raw family-type distribution:

| family_type | count |
| --- | --- |
| ADJUNCT_EXPANSION_FAMILY | 718 |
| CONSTRUCTION_FAMILY | 622 |
| EXACT_FORM_FAMILY | 959 |
| LEXICAL_RESUMPTION_FAMILY | 683 |
| MULTI_CLAUSE_CONFIGURATION_FAMILY | 1103 |
| PARTIAL_FORMAL_FAMILY | 715 |
| SLOT_NORMALIZED_FAMILY | 917 |

Occurrence-count distribution:

| occurrence_count | families |
| --- | --- |
| 1 | 5037 |
| 2 | 436 |
| 3 | 114 |
| 4 | 54 |
| 5 | 16 |
| 6 | 13 |
| 7 | 16 |
| 8 | 4 |
| 9 | 5 |
| 10 | 2 |
| 11 | 4 |
| 13 | 2 |
| 15 | 1 |
| 16 | 1 |
| 17 | 1 |
| 18 | 2 |
| 20 | 2 |
| 31 | 1 |
| 40 | 1 |
| 44 | 3 |
| 61 | 1 |
| 65 | 1 |

Raw singleton families: **5037**; repeated families:
**680**. Families per bundle:

| families_per_bundle | bundles |
| --- | --- |
| 1 | 402 |
| 2 | 94 |
| 3 | 154 |
| 4 | 111 |
| 5 | 52 |
| 6 | 246 |
| 7 | 355 |

## Default family review and reference archive (17–19)

**5717 raw family rows → 1414 bundles →
1400 default family cases + 14 archived bundles**.
This is a **75.51%** reduction in default
family review units relative to raw family rows, computed after semantic grouping.
No target percentage or numerical ranking was used. Archive does not mean invalid.

## Relation evidence cases (20–24)

**2435 raw rows → 2435 exact oriented-pair cases →
1182 default cases + 1253 archived cases**.
Raw rows already have unique pairs, so pair grouping itself does not reduce their
count; classification changes the default review universe without deleting rows.
Default relation review is reduced by **51.46%**.

| bucket | cases |
| --- | --- |
| REL_A_HIERARCHY_COMPETING | 32 |
| REL_B_RESUMPTION | 195 |
| REL_C_CLOSURE_REVIEW | 963 |
| REL_D_FORMAL_CORRESPONDENCE | 1265 |
| REL_E_WEAK_CLOSURE_ARCHIVE | 0 |
| REL_F_INSUFFICIENT | 1 |

Archived generic formal-only cases: **1252**.
Buckets overlap and have no primary rank. Hierarchy possibilities, resumption,
closure, formal correspondence and insufficiency retain their original labels.
Only a true frozen resumption-evidence flag qualifies a resumption case for default
review; shared words alone do not. Formal-only force-comparison exceptions are
traceable to shared expansion or repeated multi-clause families.

## Cessation and closure links (25–28)

Explicit cessation markers: **14**.
Raw closure pairs: **963**; review-linked: **963**;
weak/insufficient archive: **0**.

| status | cases |
| --- | --- |
| CLOSURE_STRUCTURALLY_LINKED | 192 |
| CLOSURE_FORMALLY_LINKED | 0 |
| CLOSURE_COVERAGE_LINKED | 963 |
| CLOSURE_MULTIPLE_LINK_TYPES | 192 |
| CLOSURE_WEAK_PAIR_ONLY | 0 |
| CLOSURE_LINK_INSUFFICIENT | 0 |

All 963 real Job closure pairs already end at the cessation in a raw MFR.0.1
coverage candidate. MFR.0.1 constructed this endpoint mechanically, so coverage
linking is not independent confirmation of a closure target. The requested rule
keeps these cases in default review with the original endpoint basis visible.
No ad-hoc narrowing was added to create a desired reduction. The synthetic
100-pair test independently verifies 1 linked review case and 99 preserved weak
archive cases when only one pair has endpoint evidence.

Onset, coverage, formal-family, participant-surface, domain and terminal-nested
evidence remain separate fields. Structural linking requires onset plus another
listed contextual dimension. Participant surface intersection never resolves
referential identity. No closure or terminated textual level has been selected.

## Controls and post-consolidation inspection (29–33)

All five consolidation outputs froze before known references were loaded. Counts
by corpus (cross-book cases are preserved, with no same-book eligibility filter):

| scope | markers | families | bundles | raw_relations | cases | cross_book |
| --- | --- | --- | --- | --- | --- | --- |
| daniel_ezra | 1199 | 5405 | 1521 | 3216 | 3216 | 251 |
| death | 9481 | 34563 | 12633 | 161034 | 161034 | 108865 |
| job | 1120 | 5717 | 1414 | 2435 | 2435 | 0 |
| pentateuch | 11861 | 40393 | 15479 | 206996 | 206996 | 123884 |
| prophets | 10606 | 38660 | 13653 | 136068 | 136068 | 83929 |

### External controls

| book | reference | status | profiles | bundles | cases |
| --- | --- | --- | --- | --- | --- |
| Exodus | 4:19 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 14 | 13 |
| Exodus | 12:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 20 |
| Leviticus | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 16 | 28 |
| Leviticus | 16:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 12 | 15 |
| Leviticus | 25:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 10 | 21 |
| Numeri | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 13 | 22 |
| Numeri | 3:14 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 21 |
| Numeri | 9:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 13 | 22 |
| Numeri | 20:23 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 8 | 20 |
| Numeri | 33:50 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 8 | 21 |
| Numeri | 35:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 21 |
| Deuteronomium | 32:48 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 21 |
| Jesaia | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 6 | 1 |
| Hosea | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 8 | 1 |
| Deuteronomium | 34:5 | CONSOLIDATED_EVIDENCE_PRESERVED | 1 | 2 | 3 |
| Josua | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 10 | 6 |
| Josua | 24:29 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 7 | 8 |
| Josua | 24:30 | POSTBLIND_NONRECOVERY_PRESERVED | 0 | 0 | 0 |
| Judices | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 5 | 21 | 8 |
| Samuel_I | 31:4 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 8 | 0 |
| Samuel_I | 31:5 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 11 | 7 |
| Samuel_I | 31:6 | CONSOLIDATED_EVIDENCE_PRESERVED | 1 | 1 | 5 |
| Samuel_II | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 6 |
| Daniel | 9:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 1 | 2 | 2 |
| Daniel | 9:2 | CONSOLIDATED_EVIDENCE_PRESERVED | 4 | 8 | 2 |
| Esra | 1:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 4 | 8 | 3 |

### Job controls

| book | reference | status | profiles | bundles | cases |
| --- | --- | --- | --- | --- | --- |
| Iob | 1:6 | CONSOLIDATED_EVIDENCE_PRESERVED | 4 | 11 | 10 |
| Iob | 1:13 | CONSOLIDATED_EVIDENCE_PRESERVED | 1 | 4 | 3 |
| Iob | 2:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 5 | 12 | 11 |
| Iob | 2:11 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 4 | 0 |
| Iob | 3:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 1 | 1 | 0 |
| Iob | 27:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 11 | 13 |
| Iob | 29:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 11 | 13 |
| Iob | 31:40 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 3 | 2 |
| Iob | 32:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 5 | 1 |
| Iob | 32:2 | CONSOLIDATED_EVIDENCE_PRESERVED | 3 | 5 | 0 |
| Iob | 32:6 | CONSOLIDATED_EVIDENCE_PRESERVED | 5 | 14 | 12 |
| Iob | 34:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 10 | 12 |
| Iob | 35:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 10 | 12 |
| Iob | 36:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 8 | 12 |
| Iob | 37:24 | POSTBLIND_NONRECOVERY_PRESERVED | 0 | 0 | 0 |
| Iob | 38:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 14 |
| Iob | 40:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 10 | 14 |
| Iob | 40:3 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 11 | 14 |
| Iob | 40:6 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 9 | 14 |
| Iob | 42:1 | CONSOLIDATED_EVIDENCE_PRESERVED | 2 | 11 | 14 |
| Iob | 42:7 | CONSOLIDATED_EVIDENCE_PRESERVED | 5 | 13 | 3 |
| Iob | 42:16 | CONSOLIDATED_EVIDENCE_PRESERVED | 1 | 1 | 0 |

The twelve Pentateuch DSF controls retain family/bundle traceability, raw adjunct
variants and cross-book candidate labels. Num 9:1/35:1 remain the same descriptive
partial matches as in MFR.0.1; bundling does not force common placement for Pattern 4.
Isa/Hos retain formal correspondence without new automatic parataxis. Death/resumption
keeps formal similarity separate from temporal-resumption evidence. Daniel/Ezra
preserves simultaneous formal, resumption, hypotaxis and long-distance possibilities.
Job 37:24 remains POSTBLIND_NONRECOVERY_PRESERVED; no marker was added. Josh 24:30's
non-recovery is also preserved. Existing human judgments were never input to selection.

Manual inspection covers all requested Job/control references, Hebrew surfaces,
bundle definitions, source/target cases, coverage alternatives and nested membership.
The packet has one section per consolidated default case, with marker pages giving
context and full signature/force evidence. Machine-readable review fields are blank
except UNREVIEWED. Archive appendices retain every excluded-from-default case.

## Integrity (34–38)

Raw marker/family/membership/relation/coverage/nested/force evidence loss: **0**.
Human-input and structural-label-input leakage: **0**. New human judgments,
accepted families/relations/parataxis/hypotaxis/closures, parents and hierarchy:
**0**. Participant arc remains UNADJUDICATED. R4.4 consumer absent.
Every case traces to raw IDs; original observation/signature tables remain unchanged
inside the preserved ZIP. Existing HSA/JIN judgments remain unchanged opaque input
archive bytes, not consolidation inputs.

## Validation and artifacts (39–44)

Stage tests: **69 PASS**. Full regression: **2026 PASS**,
failures/errors/skips all zero. S1–S12 and mutation tests cover the required semantics.
The final synthetic self-test passed all 149 run assertions. The Windows runner's
`-SelfTest` invocation also passed its 69 tests and synthetic package validation.
There are **44 distinct gate definitions**, including 27 core
definitions run across five corpora, 14 package definitions and 3 external release
definitions: **149 run assertions + 3 release checks PASS**. Each gate
definition has a negative test. Independent final Windows A/B ZIP bytes match.
ZIP CRC, all file hashes, upstream bytes, original family records, memberships,
raw relation labels/identities, traceability and all five freezes verify independently.
No empirical Termux execution is claimed.

An initial diagnostic real run was interrupted after a large-scope validation
performance issue: identical ID sets were rebuilt per traceability row. Caching
those sets changed no semantics. Stage tests and synthetic validation were rerun
before final execution. The early diagnostic directory is preserved locally and is
not the release artifact.

The independent B execution completed all 149 analytical/package assertions and
its final manifest, then ran out of disk space during ZIP serialization. After
space became available, its complete manifest was verified against disk and was
identical to A's manifest. The incomplete ZIP was preserved as a diagnostic; the
unchanged serializer then packaged the existing B files successfully. No analytical
output, code, source or manifest was edited for this recovery. B's failed process
exit is not reported as a successful end-to-end invocation; the recovered package
and independent byte/integrity checks establish the release result.

Final ZIP: `results/mfr01a_real_release_20260925_a_results.zip`.
SHA256: **`c5815d00ec4383296568d24b03693dc8fc64ba52803d76563a2b34a46b2f1a92`**.
ZIP member count: 1238.
Independent verification: `results/mfr01a_real_release_20260925_a_independent_verification.json`.
Human review cases: 2582. Complete packet:
`results/mfr01a_real_release_20260925_a/22_mfr_0_2_human_review_packet.md`.

## Readiness and remaining work (45–46)

**MARKER_EVIDENCE_CONSOLIDATED**.
**READY_FOR_MFR_0_2_HUMAN_ADJUDICATION**.
Next: MFR.0.2 adjudicates the consolidated family and relation cases. In particular,
the researcher must assess whether mechanically cessation-derived coverage gives
adequate closure evidence and which competing relations are supported. No hierarchy
assembly, root resolution or R4.4 implementation readiness is claimed.

Required upload: final complete ZIP. Optional: validation report and human packet.
Extract the ZIP before following relative marker-page links.

## Changed files

- `.gitattributes`
- `config/mfr_0_1a_job.json`
- `docs/HANDOFF.md`
- `docs/MFR_0_1A_RESEARCHER_SOURCE.txt`
- `docs/MFR_0_1A_SPEC.md`
- `docs/MFR_0_1A_VALIDATION_REPORT.md`
- `docs/README_MILAL_MFR_0_1A.md`
- `scripts/run_milal_mfr_0_1a_termux.sh`
- `scripts/run_milal_mfr_0_1a_windows.ps1`
- `src/milal_mfr01a_blind.py`
- `src/milal_mfr01a_bundle.py`
- `src/milal_mfr01a_closure.py`
- `src/milal_mfr01a_controls.py`
- `src/milal_mfr01a_core.py`
- `src/milal_mfr01a_data.py`
- `src/milal_mfr01a_gates.py`
- `src/milal_mfr01a_lattice.py`
- `src/milal_mfr01a_pipeline.py`
- `src/milal_mfr01a_provenance.py`
- `src/milal_mfr01a_relation.py`
- `src/milal_mfr01a_review.py`
- `src/milal_mfr01a_synthetic.py`
- `src/milal_mfr01a_verify.py`
- `tests/test_mfr_0_1a.py`

No previous analytical core was modified. Inputs, generated files, ZIPs, logs and local report scripts are excluded from Git.
