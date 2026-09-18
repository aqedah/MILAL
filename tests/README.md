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
The real R3c.0.2 Termux/Windows runs have been completed, inspected and matched
on analytical invariants. Those historical outputs remain unchanged.

## R3c.1

`test_r3c_1.py` preserves the older suite and checks object-level population,
lexicographic sampling, occurrence completeness, direct relations without
descendant target expansion, exact singleton identities, historical S02135,
boundary panels, span context and output provenance/manifests. Every one of the
24 computed gates has a deliberate negative mutation checked by the suite.
`test_r3c_1_windows_runner.py` tests the actual new wrapper with a recording
Python fixture under Windows PowerShell 5.1 and PowerShell 7 where available.

```powershell
python -m unittest discover -s tests -v
python src/milal_r3c_1_review_units.py --self-test
python src/milal_r3c_1_review_units.py --self-test --output-dir results/r3c_1_synthetic
```

The retained packet is synthetic, with 30 cases, 82 repeated units and 27 singleton
units. No real BHSA loading is part of these tests. R3c.1 empirical acceptance
requires a separately requested Windows run and human review; R4 is out of scope.
