# Running R4.1 on Windows

Use the existing environment with Text-Fabric 13.1.0 and external BHSA 2021.
If Windows PowerShell blocks the script, run it via
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File` with the same arguments;
this applies only to that invocation, not persistent machine policy.
Accepted upstream files/pins are in config/r4_0_job.json and config/r4_1_job.json.
`-Mr1`, `-R3c3`, `-Prov1`, `-Hr1`, `-Human`, `-R40` override paths only, never hashes.
The restored PROV1/HR1 defaults retain their actual (1)/(2) download suffixes.

```powershell
Set-Location C:\MILAL
$tfData = Join-Path $env:USERPROFILE 'text-fabric-data\github\etcbc\bhsa\tf\2021'
& .\scripts\run_milal_r4_1_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
# Inspect the printed synthetic packet before the real command.
& .\scripts\run_milal_r4_1_windows.ps1 -TfData $tfData
if ($LASTEXITCODE -ne 0) { throw 'Real validation failed' }
```

`-Out` selects a fresh output directory; existing outputs are never overwritten.
Results, sibling `_results.zip` and `_run.log` remain ignored. Real execution
first verifies all inputs and reproduces every accepted R4.0 member in memory.
No frozen artifacts are changed. R4.1 creates source-event anchors, not a hierarchy.
Strict R4.0 byte replay includes archived path metadata; relocation to different
paths can fail closed even if content hashes match. Only computer A is validated.

Start review with `10_macro_anchor_review_packet.md`. Expanded transition reports
05–09 provide the requested control views. Edge counts partition the whole formal
inventory; only `incident_formal_ids` touch/cross the edge. Do not mistake remote
before/after entries for local evidence. Exact definitions: docs/R4_1_SPEC.md.
