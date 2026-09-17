# MILAL Repository Instructions

MILAL = **Marker-Informed Linguistic Analysis of Layers**.

This repository supports a Hebrew Bible surface-text / Text-Fabric research pipeline. Read these documents before changing code:

1. `docs/HANDOFF.md` — current research and development state.
2. `docs/R3C_0_2_SPEC.md` — active implementation specification.
3. `docs/README_MILAL_R3c_0_1.md` — current baseline behavior.
4. `results/r3c_0_1/` — actual Termux/BHSA output from the current baseline.

## Methodological invariants

- Do **not** assign rhetorical, discourse, theological, or functional labels automatically in R3.
- Do **not** optimize by merely reducing candidate counts.
- Keep refinement genealogy and sequence-extension relations as separate layers.
- Preserve provenance. Human-facing folding may collapse duplicate display rows, but source provenance must remain recoverable.
- R3b.3 is frozen as a **navigation layer**. R3c creates **human-review objects/views** on top of it.
- A navigation container is not automatically a human review unit.
- Singleton outcomes must remain independently reviewable even when genealogically attached to a parent lineage.
- Boundary verses can participate in multiple patterns simultaneously; never reduce a boundary verse to one representative bundle.
- Do not hard-code Job-specific corpus counts into MILAL semantics. Job-specific expected counts may only be optional regression assertions.

## Active task

The next target is **MILAL R3c.0.2 — Human Review Case Pilot**. Follow `docs/R3C_0_2_SPEC.md`.

## Coding rules

- Preserve `src/milal_r3c_0_1_reviewability.py` as the baseline unless the user explicitly authorizes destructive replacement.
- Implement the next version in a new file first: `src/milal_r3c_0_2_reviewability.py`.
- Keep a single canonical `REVIEW_FIELDS` definition and derive all human-review schemas from it.
- No declarative gates that always pass. Every gate must compute an invariant from actual data.
- Prefer deterministic behavior. Random sampling must use a recorded fixed seed.
- Never silently guess a missing source column. Fail with an explicit schema error when a required invariant cannot be established.
- Keep BHSA/Text-Fabric assumptions explicit and inspectable.
- Update README/spec notes and Termux runner whenever CLI arguments or outputs change.

## Validation requirements

Before reporting completion:

1. Run Python syntax validation.
2. Run `--self-test`.
3. Run any unit/regression tests added under `tests/`.
4. Inspect generated review packets, not only CSV row counts.
5. Confirm no automatic function labels are introduced.
6. Confirm sequence-extension rows do not enter core genealogy review objects.
7. Report changed files, tests run, test results, and remaining risks.

## Real-data execution boundary

The development machine may not have the user's BHSA Termux installation. Synthetic/self-tests are not substitutes for the final real-data run. The final empirical validation is performed on Termux with the user's BHSA 2021 data, then the resulting ZIP is reviewed separately.
