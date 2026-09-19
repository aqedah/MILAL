# MILAL

**Marker-Informed Linguistic Analysis of Layers**

This folder is a Codex-ready development handoff for the current MILAL pipeline.

## Open this folder in Codex

For a new development session, read:

1. `AGENTS.md` for operating instructions.
2. `docs/HANDOFF.md`, the sole authoritative entry point for the current development stage.
3. The active specification named by HANDOFF.

`docs/CODEX_FIRST_TASK.md` preserves historical bootstrap instructions; it is not the current starting point.

R3c.3 source enrichment usage is documented in [its guide](docs/README_MILAL_R3c_3.md).
HANDOFF remains authoritative for current-stage selection.

## Historical R3c.0.1 baseline

- Source: `src/milal_r3c_0_1_reviewability.py`
- Termux runner: `scripts/run_milal_r3c_0_1_termux.sh`
- Actual real-data outputs: `results/r3c_0_1/`
- Original result ZIP: `results/milal_r3c_0_1_results.zip`

## Inputs not bundled here

Copy the following real pipeline inputs into `inputs/` on your desktop before asking Codex to run any real-input parsing tests:

- `job_r3b_2_results.zip`
- `job_r3b_3_results.zip`

BHSA/Text-Fabric 2021 is available on Windows at `C:\MILAL-data\bhsa\tf\2021`
and in the user's Termux installation. Real R3c.0.2 executions on both Termux and
Windows have been completed and inspected; analytical invariants matched.
Windows is now primary for the next empirical stage.

## R3c.0.2 implementation

- Source: `src/milal_r3c_0_2_reviewability.py`
- Job pilot configuration: `config/r3c_0_2_job_pilot.json`
- Termux runner: `scripts/run_milal_r3c_0_2_termux.sh`
- Windows runner: `scripts/run_milal_r3c_0_2_windows.ps1` (self-test, analysis, ZIP and log)
- Instructions and output schema: [R3c.0.2 README](docs/README_MILAL_R3c_0_2.md)
- Tests: `python -m unittest discover -s tests -v`

The implementation preserves R3c.0.1 and the frozen R3b.3 navigation layer.
The real Termux/Windows cross-validation is complete. Historical outputs remain unchanged.

## R3c.1 implementation

- Source: `src/milal_r3c_1_review_units.py`
- Job configuration: `config/r3c_1_job_pilot.json`
- Windows runner: `scripts/run_milal_r3c_1_windows.ps1`
- [Specification](docs/R3C_1_SPEC.md) and [usage/output documentation](docs/README_MILAL_R3c_1.md)
- Synthetic self-test: `python src/milal_r3c_1_review_units.py --self-test`

One existing repeated bundle or canonical singleton outcome is one human review
unit. All target occurrences are preserved; structural relations are context.
Containers and lineages remain navigation metadata. The pilot has 30 cases,
six in each of five groups. The researcher reports a real Windows/BHSA R3c.1 run
passing 24 gates. Its frozen result is the input to the next presentation stage.

## R3c.2 implementation

- Source: `src/milal_r3c_2_compact_review.py`
- Windows runner: `scripts/run_milal_r3c_2_windows.ps1`
- [Specification](docs/R3C_2_SPEC.md) and [usage/output documentation](docs/README_MILAL_R3c_2.md)
- Synthetic self-test: `python src/milal_r3c_2_compact_review.py --self-test`

Lossless compact presentation reuses the exact R3c.1 cases and target evidence.
It groups context/relation display, preserves full detail indexes, and does not
load BHSA or change analytical units. Development acceptance is synthetic only;
processing the real source ZIP and R4 are not part of this task.
