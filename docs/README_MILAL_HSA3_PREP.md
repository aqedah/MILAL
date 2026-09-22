# HSA3-PREP execution

This stage prepares review cases; it makes no parentage decision. Read
[HSA3_PREP_SPEC.md](HSA3_PREP_SPEC.md) and [HANDOFF.md](HANDOFF.md).

## Inputs

The exact R4.3 ZIP is configured in `config/hsa3_prep_job.json`:

`results/r4_3_whole_book_scaffold_20260922_a_results.zip`

SHA256: `d8fc0227c6bd35517b0dea1d53b205517ad8a8308b5954486215a00955cba4f7`.

The frozen R4.3 adapter also verifies its ten accepted upstream ZIPs, source files,
CRC/manifests and human registry bytes. Preserve configured paths (including the
historical PROV1 `(1)` and HR1 `(2)` filenames). No substitutes or fuzzy linkage.
No direct BHSA extraction or network download occurs. Missing/mismatched inputs
fail clearly; do not reconstruct them. All artifacts remain ignored by Git.

## Windows

From the repository root, with the repository Python environment installed:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_prep_windows.ps1 -SelfTest -Out "results/hsa3_prep_synthetic_$stamp"
if ($LASTEXITCODE -ne 0) { throw 'Synthetic validation failed' }
Write-Host "Inspect results/hsa3_prep_synthetic_$stamp/04_global_seam_review_packet.md before accepted-real execution."
```

After synthetic inspection and within the researcher's authorized real scope:

```powershell
$ErrorActionPreference = 'Stop'
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss_fff'
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_prep_windows.ps1 -Out "results/hsa3_prep_global_seams_${stamp}_a"
if ($LASTEXITCODE -ne 0) { throw 'Accepted-real audit failed' }
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/run_milal_hsa3_prep_windows.ps1 -Out "results/hsa3_prep_global_seams_${stamp}_b"
if ($LASTEXITCODE -ne 0) { throw 'Independent rerun failed' }
$firstHash = (Get-FileHash -Algorithm SHA256 "results/hsa3_prep_global_seams_${stamp}_a_results.zip").Hash
$secondHash = (Get-FileHash -Algorithm SHA256 "results/hsa3_prep_global_seams_${stamp}_b_results.zip").Hash
if ($firstHash -ne $secondHash) { throw 'ZIP determinism failed' }
Write-Host "PASS. Review results/hsa3_prep_global_seams_${stamp}_a/04_global_seam_review_packet.md"
```

Runner options: `-SelfTest`, `-Out`, `-Python`. Python defaults relative to the
repository at `.venv\Scripts\python.exe`. Existing output directories, ZIPs or
logs are refused. Output is UTF-8; metadata records code/config/source hashes.

## Termux

No Termux empirical result is claimed. From an identically provisioned checkout:

```sh
python -B -X utf8 src/milal_hsa3_prep_global_seams.py --self-test --out results/hsa3_prep_termux_synthetic
# Inspect the synthetic packet before the following accepted-real command.
python -B -X utf8 src/milal_hsa3_prep_global_seams.py --out results/hsa3_prep_termux_real
```

Frozen raw-byte hashes are strict, including historical Windows checkout line
endings. If they differ, stop and report; do not rewrite frozen fixtures or relax
pins to get a different platform through. Recover exact accepted artifacts first.

## Reading the packet

01 partitions all 57 rows. 06 records typed review-dependency paths; 09 maps back
to exact original rows and distinguishes one display owner from all participating
cases. The seven cases overlap. H summarizes them; it is not a proposed tree.
Review-scope compression does not prove seven atomic judgments will suffice.
03 and the Markdown retain blank canonical review fields. 05 and history retain
complete source evidence; 10 audits non-textual groups. R4.4 must wait for human
adjudication, including explicit unresolved/insufficient-evidence outcomes.
