# MILAL

**Marker-Informed Linguistic Analysis of Layers**

This folder is a Codex-ready development handoff for the current MILAL pipeline.

## Open this folder in Codex

Read `AGENTS.md` first. Codex should then follow the active specification in `docs/R3C_0_2_SPEC.md`.

The first prompt to use is in `docs/CODEX_FIRST_TASK.md`.

## Current baseline

- Source: `src/milal_r3c_0_1_reviewability.py`
- Termux runner: `scripts/run_milal_r3c_0_1_termux.sh`
- Actual real-data outputs: `results/r3c_0_1/`
- Original result ZIP: `results/milal_r3c_0_1_results.zip`

## Inputs not bundled here

Copy the following real pipeline inputs into `inputs/` on your desktop before asking Codex to run any real-input parsing tests:

- `job_r3b_2_results.zip`
- `job_r3b_3_results.zip`

The user's real BHSA/Text-Fabric 2021 corpus remains on Termux and is used for final empirical execution.

## R3c.0.2 implementation

- Source: `src/milal_r3c_0_2_reviewability.py`
- Job pilot configuration: `config/r3c_0_2_job_pilot.json`
- Termux runner: `scripts/run_milal_r3c_0_2_termux.sh`
- Instructions and output schema: [R3c.0.2 README](docs/README_MILAL_R3c_0_2.md)
- Tests: `python -m unittest discover -s tests -v`

The implementation preserves R3c.0.1 and the frozen R3b.3 navigation layer.
Empirical acceptance remains pending real Termux/BHSA execution and packet review.
