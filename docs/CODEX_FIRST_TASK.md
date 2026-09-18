# Historical First Codex Task

> Historical bootstrap instructions for the initial R3c.0.2 implementation. Not the current development entry point. See [HANDOFF.md](HANDOFF.md) for the current stage and active specification.

Paste the prompt below into Codex after opening the repository folder.

---

Read the repository before modifying anything.

Required reading:
- `AGENTS.md`
- `docs/HANDOFF.md`
- `docs/R3C_0_2_SPEC.md`
- `docs/README_MILAL_R3c_0_1.md`
- `src/milal_r3c_0_1_reviewability.py`
- `scripts/run_milal_r3c_0_1_termux.sh`

Also inspect the actual baseline outputs under:
- `results/r3c_0_1/07_pilot_review_container_packet.md`
- `results/r3c_0_1/08_boundary_control_pattern_matches.csv`
- `results/r3c_0_1/10_boundary_control_panels.md`
- `results/r3c_0_1/12_r3c_0_1_gates.csv`
- `results/r3c_0_1/14_run_summary.json`

Do not write code yet.

First give me a concise implementation review containing:
1. your understanding of R3b.3, R3c.0.1, and the purpose of R3c.0.2;
2. concrete evidence from the actual R3c.0.1 outputs showing why navigation containers are not always human-review units;
3. the functions/classes in `src/milal_r3c_0_1_reviewability.py` that should be replaced, reused, or split;
4. a proposed R3c.0.2 file/output schema;
5. the tests you will add before implementation;
6. any disagreement or ambiguity you find in `docs/R3C_0_2_SPEC.md`.

Methodological constraints:
- no automatic rhetorical/function labels;
- no candidate-count optimization as an objective;
- preserve R3b.3 as a frozen navigation layer;
- keep sequence-extension separate from refinement genealogy;
- preserve all provenance even when duplicate human-facing rows are folded;
- do not use the six random cases to estimate total population review time.

Wait for my next instruction before implementing R3c.0.2.
