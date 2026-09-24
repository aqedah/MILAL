# JIN.0.4 Batch 1 validation — 2026-09-24

Start commit: `1781b36f52b9d0b47c1acfefbd07bb06411129a3`.
Commit message: `Record contextual relation adjudication batch 1`.
The containing Git commit identifies this final state; no self-referential hash is embedded.
Readiness: **BLOCKED_PENDING_FOCUSED_RELATION_AUDITS**.

## Implemented / methodological interpretation

Seven researcher-supplied decisions are transcribed into a new append-only layer.
This does not infer new linguistic evidence or adjudicate all 206 contextual cases.
Pairwise support, contextual evidence, historical acceptance and latest human review
remain separate records. Historical edge deletion, supersession and consumer execution
are all absent. Previous analytical cores and every frozen artifact remain unchanged.

| Case | Researcher judgment | Historical handling | Selected mother |
|---|---|---|---|
| B1 1:6 ↔ 2:1 | Accepted PARATAXIS | Reconfirmed | NONE |
| B2 1:13 relative to 1:6 | HUMAN_DEFERRED | Reopened focused mother audit | NONE |
| B3 3:2 relative to 3:1 | HUMAN_DEFERRED | Reopened generic speech-frame audit | NONE |
| B4 2:11 | Insufficient macro evidence | Single-mother target unresolved | NONE |
| B5 32:1 | Insufficient macro evidence | Single-mother target unresolved | NONE |
| B6 40:1 → 38:1 | Accepted HYPOTAXIS | CHILD_OF reaffirmed in original direction | 38:1 |
| B7 38:1 ↔ 40:6 | Accepted PARATAXIS | Reconfirmed | NONE |

B2 edge `E:5645a90df42fba6884a0` and B3 edge `E:e664ee6af98d968e0ec6`
remain ACCEPTED_SOURCE in frozen history. Latest status is
REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT; neither is REJECTED or SUPERSEDED.
B6 retains `E:94026f426d623f2921a2` (40:1 CHILD_OF 38:1).
B1 retains both `E:1e1cac2f463240ff6822` and `E:4890d3199e4962a2706c`;
B7 retains both `E:45e7bca183e3cc4ce8b5` and `E:d7914344ad4832c8be9e`.
These are the two stored orientations of each historical symmetric relation, not
new duplicates. Exactly **3** relation-level duplicate creations avoided, **5**
existing ID references reconfirmed, **0** new unique textual edges and **0** new parent edges.
No arbitrary canonical-ID merge or synthetic replacement is performed.

The raw +/-3 output remains frozen. Expanded-formula/38:3–40:7 rationale in B6/B7
is preserved as supplied researcher reasoning, not claimed as new automatic detection.
The batch may link several review rows to one supplied decision; the old 206-row
queue is preserved verbatim, so subtracting seven to infer a remaining queue is invalid.

## Calibration and next scope

Two clause controls, `JP:JT0037:499628:499631` and `JP:JT0037:499629:499631`,
resolve exactly to the original explicit-subordination hypotheses with later reference
32:3. Both are EXPLICIT_SUBORDINATION_POSITIVE_CONTROL_FOR_REVIEW, UNREVIEWED,
human_accepted=false; no clause-level human decision was supplied or invented.

Three plans are recorded, not executed:

1. JOB_1_13_MOTHER_AUDIT: 1:4–5, 1:6, 1:12, 1:13, 1:22, 2:1; no mother selected.
2. JOB_3_1_2_SPEECH_FRAME_AUDIT: generic whole-Job speech-event framing → CSF/quoted onset;
   פתח ... פה and אמר/ענה, not a Job 3-only detector.
3. MACRO_PARENT_AUDIT_2_11_32_1: actual preceding main textual loci, not internal clauses.

Q1–Q9 remain unapproved; R4.4 consumer NOT IMPLEMENTED; participant arc UNADJUDICATED.
Precedence behavior is documented only. B4/B5 historical paragraph/arrival/transition
facts remain in source history and do not substitute for a mother judgment.

## Validation

- Python and Windows/Termux runner syntax PASS.
- Stage unit tests **45 PASS**.
- Full regression **1,574 PASS**, failures **0**, errors **0**, skipped **0**;
  elapsed **694.382 seconds**.
- **37 run gates PASS**: 36 model gates plus manifest. Every gate has a negative mutation.
- **2 external release gates PASS**: deterministic rerun and full regression;
  negative tests cover byte mismatch, failures, errors and skips.
- Synthetic self-test PASS; inspected decision report, explicit-control status and gates
  before real execution.
- Real frozen-source runs A/B PASS; independent processes yield **byte-identical ZIPs**.
- Independent audit PASS: CRC, root/20 recursive manifests, all **350** upstream members
  byte-identical, **217** frozen repository pins unchanged, exact researcher bytes,
  seven decisions, exact historical records, two reopened records, no new edges,
  unaccepted explicit controls and output implementation hash.
- Manually inspected real decision rows, exact review/pair/context links, original B6
  direction, B2/B3 accepted-source/reopened separation and all three scope plans.
- No BHSA rerun was needed; this stage consumes frozen JIN.0.3. No Termux empirical run claimed.

## Artifacts (local-only / ignored)

Upstream ZIP SHA256:
`5412da317a698cbc506114464d2c7ed328f5e65e1b3af9511cf1eff224070387`.

Real A: `results/jin04_batch1_real_final_20260924_a_results.zip`.
Independent B: `results/jin04_batch1_real_final_20260924_b_results.zip`.
Both SHA256: `e0d188996973dcf04362cb1d09cf3084df8aa802024182666b474c7b881927e3`.
Each has **366 members**, including all 350 upstream members under history/jin_0_3/.

Synthetic: `results/jin04_synthetic_final_20260924_a_results.zip`.
SHA256: `015b0392e2f7a7fadbd1d00f27d4131b1093af0dcccc0187d7ab2b32fb66874c`.
Regression: `results/jin04_regression_20260924_a.json` and matching `.log`.
Independent release receipt: `results/jin04_independent_release_receipt.json`.

## Repository files changed

- `.gitattributes`
- `config/jin_human_batch1.json`
- `docs/HANDOFF.md`
- `docs/R4_4_CONTRACT_JIN_0_4_RESEARCHER_SOURCE.txt`
- `docs/R4_4_CONTRACT_JIN_0_4_SPEC.md`
- `docs/R4_4_CONTRACT_JIN_0_4_VALIDATION_REPORT.md`
- `docs/README_MILAL_R4_4_CONTRACT_JIN_0_4.md`
- `scripts/run_milal_jin_human_batch_windows.ps1`
- `scripts/run_milal_jin_human_batch_termux.sh`
- `src/milal_jin_human_batch.py`
- `tests/test_r4_4_contract_jin_0_4.py`

Remaining work is the three focused audits and later human re-adjudication, including
clause-level hypotaxis calibration. This batch does not make R4.4 implementation ready.
