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
units. No real BHSA loading is part of these tests. The researcher subsequently
reported a real R3c.1 run passing 24 gates; R4 remains out of scope.

## R3c.2

`test_r3c_2.py` consumes a synthetic frozen R3c.1 result ZIP generated through
the unchanged R3c.1 writer. It verifies manifest preflight, exact case/evidence
preservation, full context JSON, relation display folding with raw multiplicity,
boundary/overlay preservation, S02135, packet traces/metrics, no-overwrite and
non-case source-row ordering independence. Every one of the 23 gates has a
negative mutation subtest; no test skips a gate merely because it always passes.

`test_r3c_2_windows_runner.py` exercises the actual wrapper on PowerShell 5.1/7
where available: default local venv, explicit Python, self-test ordering, no BHSA
arguments, UTF-8 logs, preserved statuses and exclusive output/archive creation.
The older test files remain unchanged.

Run `python -m unittest discover -s tests -v`, then
`python src/milal_r3c_2_compact_review.py --self-test`. Add `--output-dir` with a
fresh path to retain the compact packet and its source ZIP for manual inspection.
Do not run the real R3c.1 ZIP as part of this development validation.

Validation on the B computer (2026-09-18): all 101 tests passed, with no skips,
including both PowerShell 5.1 and 7. The 23 new test methods include negative
subtests for every R3c.2 gate. The initial full run had 20 older runner subtest
failures caused by Windows short (`~1`) versus expanded temporary path spelling.
No historical tests or runners were changed. Canonicalizing the test process's
temporary directory resolved those comparisons:

```powershell
python -c "import pathlib,tempfile,unittest; tempfile.tempdir=str(pathlib.Path(tempfile.gettempdir()).resolve()); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not result.wasSuccessful())"
```

Syntax validation and R3c.2 self-test passed. The inspected synthetic packet has
30 cases, 93 target evidence rows, 407 boundary rows, 8 context records,
383 raw / 324 compact relation rows and 73 overlay rows. All 23 gates pass;
the whole packet is 2,466 lines / 276,551 UTF-8 bytes. These are synthetic
fixture measurements, not empirical Job results or review-time estimates.
