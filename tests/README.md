# Tests

Run `python -m unittest discover -s tests -v` from the repository root.
`test_r3c_0_2.py` exercises synthetic success/failure contracts without BHSA,
including negative tests for all four extension-separation invariants.
Also run `python src/milal_r3c_0_2_reviewability.py --self-test`.

`test_windows_runner.py` executes the actual PowerShell wrapper against a recording
Python fixture, using both Windows PowerShell and PowerShell 7 when available.
It checks argument boundaries with spaces, self-test ordering, UTF-8/stderr logs,
TF file preflight, existing-result preservation, archive contents, and failure
exit codes (including simultaneous analysis/ZIP failures). It skips off Windows
or when no PowerShell is available; it does not load real BHSA.
The default-interpreter regression creates a fixture-local `.venv`, omits
`-PythonExe`, runs from a different working directory, and checks the actual
`sys.executable` path. Existing tests retain explicit interpreter overrides.

Three mandatory historical regressions use the minimal version-controlled CSVs
in [fixtures/r3c_0_1](fixtures/r3c_0_1/README.md): S02135's original parent/lineage
and two representations, its independent review/rendering through a synthetic
genealogy, and required source-schema columns. Missing fixtures fail the tests;
the full `results/r3c_0_1/` directory is unnecessary.
The real R3c.0.2 Termux/BHSA run has been completed, inspected and accepted.
These tests do not replace Windows cross-validation against that execution.
