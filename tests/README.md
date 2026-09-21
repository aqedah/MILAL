# Tests

## PROV1

`test_prov1.py` adds 43 tests: independent golden hashes, cumulative reconstruction,
normalization and ordering, target-hash independence, first uniqueness, source and
occurrence preservation, explicit controls, archive-loader roundtrip, output
integrity, and negative coverage of every one of the 22 gates.
`test_prov1_windows_runner.py` adds two process tests, exercised under installed
PowerShell 5.1/7, for self-test-first ordering, exact arguments, failure statuses
and protection against overwriting an output directory. No real PROV1 run occurs
in these tests. Synthetic inputs have independent fixture hashes and fewer atoms.

Run `python -B src/milal_prov1_signature_provenance.py --self-test` after the complete
suite. Add `--output-dir` with a new directory to retain the twelve synthetic
outputs and inspect both Markdown packets. Frozen analytical tests are unchanged.

2026-09-20 validation: complete suite 171 passed, zero failures/skips. The final
Markdown presentation refinements were rechecked with all 43 PROV1 tests.
Synthetic self-test: 22/22 gates PASS and 234/234 reconstructed hashes MATCH;
112 atom-level rows, 57 families, 51 refinements, two singletons. Both generated
Markdown documents and the on-disk manifest were inspected. No real PROV1 run.

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

## R3c.3

`test_r3c_3.py` adds 19 tests, including negative mutations for all 26 gates.
It covers archive/hash-chain rejection, filename-independent schema discovery,
ambiguity and missing schemas, exact row locators, opaque-signature limitations,
explicit deltas, five case controls, S02135, boundary multiplicity, unchanged
forms, distributions, output manifests and no-overwrite behavior.
`test_r3c_3_windows_runner.py` adds six process tests, exercised under both
PowerShell 5.1 and 7, including default/explicit Python, four input arguments,
UTF-8 logging, failure codes, missing inputs and protected output destinations.

Development validation on 2026-09-18: all 126 tests passed, no skips; Python syntax
validation and R3c.3 self-test passed, all 26 gates PASS. The directly inspected
synthetic packet has 30 cases, 4,248 lines and 256,623 UTF-8 bytes. CASE001/007/
013/019/025 contain structural enrichment or explicit unavailability, with full
original evidence referenced. Real R3b source schema/CRC/hash inspection was
performed; no real R3c.3 enrichment dataset was executed. Frozen cores and prior
tests remain unchanged. Use the canonical-temporary-path full-suite command in
the R3c.3 usage guide on Windows.

## HR1

`test_hr1_adjudication_linkage.py` adds 31 tests. Every one of the 22 HR1 gates
has a negative mutation (source integrity/commit defects abort at preflight).
Tests also cover missing/duplicate explicit links, source-anchor disagreement,
verbatim human-field roundtrips, independent event-only singleton review,
boundary multiplicity, extension connectivity, deterministic synthetic output,
fresh output enforcement and ZIP/log verification. Real result ZIPs are not
required by the regression suite. No frozen stage or previous test was changed.

2026-09-21: complete regression suite 202 PASS, zero failures/skips, including
both installed PowerShell versions; Python syntax PASS; HR1 synthetic self-test
22/22 gates PASS. Synthetic packet inspected: 30 case rows, 90 evidence locators,
136 provenance locators, five overlay rows, six boundary panels, six summary rows.
See `docs/HR1_SPEC.md` and `docs/README_MILAL_HR1.md` for schema and execution.
