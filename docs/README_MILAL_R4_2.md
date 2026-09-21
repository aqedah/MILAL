# Running R4.2 on Windows

Use the existing Python environment, Text-Fabric 13.1.0 and external BHSA 2021.
Exact accepted pins are inherited from R4.0/R4.1 configuration plus the R4.1
archive pin in config/r4_2_job.json. New explicit researcher judgments live in
docs/R4_2_HUMAN_JUDGMENTS.json. They are human evidence, not extraction rules.

```powershell
Set-Location C:\MILAL
$tfData = Join-Path $env:USERPROFILE 'text-fabric-data\github\etcbc\bhsa\tf\2021'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_r4_2_windows.ps1 -SelfTest
if ($LASTEXITCODE -ne 0) { throw 'Synthetic failed' }
# Inspect the printed synthetic output before running real data.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_milal_r4_2_windows.ps1 -TfData $tfData
if ($LASTEXITCODE -ne 0) { throw 'Real execution failed' }
```

ExecutionPolicy is process-only; no persistent policy change. `-Out` accepts a
fresh directory, never overwrites. `-Python` overrides the executable. ZIP/log
are siblings of the result directory and stay ignored. Real execution replays
accepted R4.0/R4.1 in memory, so the prior strict path-metadata portability limit
remains: only computer A has been validated. No accepted source is rewritten.

Review 04/05/06 for critical cases; 08 indexes **every** event. CSV 01 contains
source nodes, identity status and blank human fields. CSV 07 explains inclusion
or exclusion for every phrase. CSV 12 retains full native features, and CSV 27
retains event/formal positions relative to the source clause, not an inferred scene.
Full phrase/word morphology makes these CSVs contain large JSON cells; Python CSV
readers should set `csv.field_size_limit(16 * 1024 * 1024)` when reading them.

The event inventory is deliberately a surface candidate audit. Proper names,
plural subjects and speech arguments are not automatically animate scene actors.
Identity EXPLICIT means an overt source mention, not resolved global identity.
Anonymous entries remain UNRESOLVED. Human-supplied enclosures do not constitute
automatic macro units. No hierarchy field is prefilled.
