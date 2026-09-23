# HSA3-A/C validation receipt — 2026-09-23

Starting commit: `9abbb45f1a4159db99a86ce4647f26d538937808`, `main`,
verified origin `https://github.com/aqedah/MILAL.git`. Initial working tree was
clean; `git pull --ff-only origin main` reported already up to date.
This report is part of the resulting commit, titled
`Freeze opening and dialogue global seam adjudications`.

## Decisions and accounting

| Item | Validated result |
| --- | --- |
| SEAM_A | FROZEN: separate friends arrival 2:11–13, outside second testing scene; exact textual parent UNRESOLVED |
| Opening complex | New NON_TEXTUAL_COMPOSITION_GROUP, 1:1–2:13; household, test 1, test 2, arrival in order |
| SEAM_B | FROZEN: existing H:HSA013 reused as INITIAL_JOB_SPEECH, 3:1–26, NOT_MEMBER_OF_CYCLE_1 |
| Cycle 1 start | 4:1; 3:1 above 3:2 and 3:2 continuation preserved |
| SEAM_C | FROZEN: three cycles and post-dialogue Job are distinct composition components, not parent/child |
| Cycle pattern | Exact 6/6/4 members; 4:1/15:1/22:1 onsets preserved; no synthetic Zophar III or Cycle 4 |
| Post-dialogue Job | 27:1–31:40; 27:1/29:1 siblings, 28:1 continuation/NO_BOUNDARY and HSA2-F preserved |
| Dispute complex | New NON_TEXTUAL_COMPOSITION_GROUP, 3:1–31:40; initial speech, cycle sequence, post-dialogue Job in order |
| Job 2:11 attachment | Not attached to dispute complex; broader 2:11–42:9 frame unadjudicated |
| New seam decisions | 3 |
| New composition groups | 2 (separate from relation count) |
| New positive relations | 7 ordered GROUP_MEMBER_OF records |
| Confirmed existing relations | 123 unique historical edge-row IDs; no recreation or collapse of reciprocal records |
| New negative constraints | 6: A containment, B non-membership, four directional C parent exclusions |
| Unresolved retained actions | 43 |
| Duplicate skipped | 0 |
| Crosswalk resolved by A/B/C | 0 / 0 / 0 |
| Crosswalk remains unresolved | 43 A/B/C-participating parent questions |
| Crosswalk not applicable | 14; these still remain historically unresolved |
| Historical unresolved total | All 57 preserved |

Frozen seam decisions are complete supplied judgments, not a claim that every
parentage question has a positive parent. New groups are composition/reporting
units, never textual parents or BHSA mother surrogates. Group spans are supplied
human metadata, including the cycle-sequence end at 26:14; no new closure scan.
The historical dual PARAGRAPH_ONSET/SPEECH_UNIT_ONSET evidence at H:HSA013 is intact.

## Tests and empirical verification

- Python syntax and both JSON inputs: PASS.
- New stage tests: **67 PASS**, zero skips. All 38 model gates have failure
  mutations; MANIFEST_VALID has a corruption negative test (39 gates total).
- Full regression: **1,006 PASS**, zero failures/errors/skips, **173.716 seconds**.
  This includes the 939 previous regression tests and the 67 new tests.
- Synthetic runner/self-test: **39/39 gates PASS**; report and F/G packet inspected.
  All report/packet links resolve; canonical review fields remain unfilled except
  UNREVIEWED. Synthetic contains 144 members and passes all nested manifests.
- Real frozen-artifact runner: **39/39 gates PASS**.
- Independent real invocation: **39/39 gates PASS**; complete ZIP bytes identical,
  not only tabular counts or selected fields.
- Real ZIP: CRC PASS, 146 members, 10 manifest checks PASS.
- All 129 upstream ZIP members are byte-identical beneath `history/hsa3_de/`.
- All 125 pinned prior repository files retain exact SHA256.
- **264 source row links** independently checked against exact identity, data-row
  number, raw CSV row SHA256 and member SHA256. No fuzzy matching.
- Real group order/spans and F/G UNREVIEWED records independently inspected.
- Generated artifacts/logs are ignored; no BHSA/input/result bytes staged for Git.

Commands used (repository-root PowerShell):

```powershell
& .venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -p test_hsa3_abc_seam_adjudication.py -v
& .venv\Scripts\python.exe -B -X utf8 -m unittest discover -s tests -v
& scripts\run_milal_hsa3_abc_windows.ps1 -SelfTest -Out results\hsa3_abc_synthetic_final_20260923_a
& scripts\run_milal_hsa3_abc_windows.ps1 -Out results\hsa3_abc_opening_dialogue_final_20260923_a
& scripts\run_milal_hsa3_abc_windows.ps1 -Out results\hsa3_abc_opening_dialogue_repeat_20260923_a
```

Real artifact:
`C:\MILAL\results\hsa3_abc_opening_dialogue_final_20260923_a_results.zip`

SHA256:
`e79575a4290913edce774f68d2bf94c2f03583f35636d9086a6bc0cca40f147b`

Independent repeat:
`C:\MILAL\results\hsa3_abc_opening_dialogue_repeat_20260923_a_results.zip`
with the same SHA256 and exact bytes.

Synthetic:
`C:\MILAL\results\hsa3_abc_synthetic_final_20260923_a_results.zip`
SHA256 `a585bb4da847b08a41414178dc3df6c40bd7a04ff34392cbd52bbb732c1feba1`.

Local logs: `results/hsa3_abc_tests_final.log`,
`results/hsa3_abc_full_regression.log`, and matching runner `_run.log` files.

## Frozen layers and remaining review

No earlier analytical core was modified. D/E stay FROZEN. ANA Q2/Q4/Q5 remain
ACCEPTED; Q3 remains UNRESOLVED/HUMAN_DEFERRED. All three HSA2-F 31:40 relations
and historical artifacts remain unchanged. No BHSA or lexical scan occurred.
R4.4 is not started.

Remaining packet:
`C:\MILAL\results\hsa3_abc_opening_dialogue_final_20260923_a\09_hsa3_fg_remaining_review_packet.md`.
Only F/G remain as unadjudicated global seams. The packet retains exact original
questions, participating nodes, evidence links, positive/negative constraints,
unresolved rows, canonical criteria dimensions and blank researcher fields.
ANA accepted/deferred context and frozen D/E negatives are preserved separately.
Next: researcher adjudication of F/G. The broader participant frame is outside
this decision and must not be silently resolved by later composition use.

## Intended repository files

- `.gitattributes`
- `config/hsa3_abc_human_decisions.json`
- `config/hsa3_abc_job.json`
- `docs/HANDOFF.md`
- `docs/HSA3_ABC_RESEARCHER_SOURCE.txt`
- `docs/HSA3_ABC_SPEC.md`
- `docs/HSA3_ABC_VALIDATION_REPORT.md`
- `docs/README_MILAL_HSA3_ABC.md`
- `scripts/run_milal_hsa3_abc_windows.ps1`
- `src/milal_hsa3_abc_seam_adjudication.py`
- `tests/test_hsa3_abc_seam_adjudication.py`
