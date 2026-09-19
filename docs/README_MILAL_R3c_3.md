# MILAL R3c.3 usage

See [HANDOFF](HANDOFF.md) for state and [specification](R3C_3_SPEC.md) for inspected
source fields, availability, derivations and schemas. Python standard library only;
no Text-Fabric/BHSA loading. Hashes are not decoded structural signatures.

## Synthetic validation

```powershell
python -m py_compile src/milal_r3c_3_signature_context.py tests/test_r3c_3.py tests/test_r3c_3_windows_runner.py
python src/milal_r3c_3_signature_context.py --self-test
python src/milal_r3c_3_signature_context.py --self-test --output-dir results/r3c_3_synthetic_new
python -c "import pathlib,tempfile,unittest; tempfile.tempdir=str(pathlib.Path(tempfile.gettempdir()).resolve()); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=1).run(suite); raise SystemExit(not result.wasSuccessful())"
```

Use fresh paths. Retained self-test saves four source ZIPs beside the output for
auditability. Canonical temporary paths avoid historical Windows short-path test
comparisons without modifying old tests.

## Later separately authorized real-input run

Do not execute this example during development acceptance:

```powershell
& C:\MILAL\scripts\run_milal_r3c_3_windows.ps1 `
  -R3c2Zip 'C:\MILAL\results\r3c_2_windows_20260918_154011_results.zip' `
  -R3c1Zip 'C:\MILAL\results\r3c_1_windows_20260918_091408_results.zip' `
  -R3b2Zip 'C:\MILAL\inputs\job_r3b_2_results.zip' `
  -R3b3Zip 'C:\MILAL\inputs\job_r3b_3_results.zip' `
  -OutputDir 'C:\MILAL\results\r3c_3_windows_01'
```

Default Python is repository-local `.venv\Scripts\python.exe`; override with
`-PythonExe`. Runner self-tests first, preserves exit codes, writes UTF-8 logs,
packages results, and never overwrites existing output/log/ZIP paths. Optional
`-ResultZip`/`-RunLog` must be distinct and outside the output tree.

Direct CLI: `--r3c2-zip`, `--r3c1-zip`, `--r3b2-zip`, `--r3b3-zip`, `--output-dir`.
The R3c.1 ZIP supplies its verified inventory and singleton provenance, which are
not embedded in R3c.2. All four archives must be retained for reference resolution.
Source/schema errors return nonzero without guessing structural definitions.

Inspect the enriched packet together with the unchanged R3c.2 packet/indexes.
Definition CSVs hold exact source rows and locators. Readiness is availability,
not a human judgment of reviewability.
