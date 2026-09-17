# MILAL R3c.0.2 — Human Review Case Pilot

This version creates 30 review cases over the frozen R3b.3 navigation layer.
R3c.0.1 source, runner and real outputs remain unchanged. Local synthetic success
is **not empirical acceptance**: inspect the real Termux/BHSA 2021 result next.

## Run on Termux

Keep this repository layout together:

```text
src/milal_r3c_0_2_reviewability.py
scripts/run_milal_r3c_0_2_termux.sh
config/r3c_0_2_job_pilot.json
```

With the two input ZIPs in Downloads and BHSA installed at its existing location:

```bash
bash scripts/run_milal_r3c_0_2_termux.sh
```

The runner locates `../src/` and `../config/` relative to itself, regardless of
the current working directory. It creates a fresh timestamped output directory,
ZIP and log; it never deletes previous results. Positional overrides are:

```text
1 R3b.2 ZIP
2 R3b.3 ZIP
3 BHSA tf/2021 directory
4 new output directory
5 new result ZIP path
6 pilot configuration JSON
7 random seed (default 20260917)
```

The runner's explicit seed overrides the configuration seed. For direct Python:

```bash
python src/milal_r3c_0_2_reviewability.py \
  --r3b2-zip "$HOME/storage/downloads/job_r3b_2_results.zip" \
  --r3b3-zip "$HOME/storage/downloads/job_r3b_3_results.zip" \
  --tf-dir "$HOME/text-fabric-data/github/ETCBC/bhsa/tf/2021" \
  --pilot-config config/r3c_0_2_job_pilot.json \
  --output-dir "$HOME/milal_r3c_0_2_output"
```

Python requires an empty/new output directory. Optional `--seed` overrides the
configuration. Optional `--expected-review-containers 1066` asserts the current
Job regression count; it is not a semantic requirement. Exit 0 means computed
checks passed, not that a researcher has accepted the evidence. Exit 2 means
validation failed; inspect `00_FATAL_ERROR.txt`, gates and metadata.

## Selection and identity

There are six each of HIGH_COMPLEXITY_CONTAINER, LOW_COMPLEXITY_CONTAINER,
RANDOM_CONTAINER, SINGLETON_ITEM and BOUNDARY_CONTROL. Counts are fixed at 30.
HIGH sorts by bundle count, distinct singleton outcome count and maximum depth
descending, then container ID ascending. LOW uses ascending measures after HIGH
exclusion. RANDOM samples six from the remaining ID-sorted containers. These are
structural stress-test strata, never importance scores.

The Job configuration requires S02135 / תמו דברי איוב / 31:40 and samples five
other singleton outcomes using the recorded seed. It also defines the six Job
boundary panels. These controls live in configuration, not generic semantics.
The optional Hebrew regression strips marks and a trailing BHSA paragraph marker;
source surfaces remain untouched. A missing/mismatched required control fails.

Only explicit mapped G6 item IDs fold events. The G6 ID is canonical, and every
mapped event remains attached. EVENT_ONLY and G6_ONLY outcomes survive. Multiple
parents within one lineage remain separate provenance branches. Conflicting
lineage/atom identity, incompatible mapped sequence length, or non-overlapping
mapped spans fail with source records in the diagnostic. Overlapping source spans
remain separate. No text, span or signature matching establishes identity.

All repeated bundle identities and their occurrences remain available. Boundary
membership uses every source span, including spans crossing the boundary verse.
Repeated bundles are not merged because they happen to share text with a singleton.

## Outputs

Use a versioned directory/ZIP; all files declare R3c.0.2 through metadata/packet.
CSV list/object cells are JSON, not lossy delimiter-separated strings.

| File | Contents |
|---|---|
| `01_source_schema_inventory.csv` | Exact source columns/counts and input ZIP hashes |
| `02_review_cases.csv` | 30 case IDs, targets, structural measures, seed, canonical review fields |
| `03_container_case_evidence.csv` | Container and independent-singleton case attachments, repeated members/occurrences and ancestry |
| `04_singleton_outcomes.csv` | One emitted outcome per identity, all branches/transitions and source spans/context IDs |
| `05_object_provenance.csv` | Archive hash/member path, one-based CSV data row, stable source key, role, original row JSON |
| `06_boundary_case_evidence.csv` | Every relevant occurrence/outcome plus explicitly marked ancestry evidence |
| `07_sequence_extension_overlay.csv` | Separate relation attachments and coverage limitation |
| `08_span_context_inventory.csv` | Full covering verses, neighbors, overlapping clauses/sentences, resolution status |
| `09_review_packet.md` | All cases, parent-child trees, evidence, contexts, provenance, review forms |
| `10_gates.csv` | Executable invariants with violations |
| `11_method_note.md` | Selection, identity, context and coverage assumptions |
| `90_run_metadata.json` | Configuration/seed, source hashes, counts, run type, failures, pending empirical status |
| `99_manifest_sha256.csv` | Every other generated file's checksum and size |

Case IDs, evidence-object IDs and source-record IDs are separate. Source row
snapshots cover referenced evidence only: complete input tables/ZIPs are not
copied into the result. The manifest intentionally cannot hash itself.

## Context and extension limitations

Context covers every complete verse in a source span. The next verse follows the
end, not the start. Cross-chapter spans are supported; book edges have a blank
neighbor without wrapping into another book. Clause/sentence overlap is computed
through word membership, including structures crossing verse boundaries. This is
covering-verse context, not an assertion about exact pattern word boundaries.

The extension adapter reads the documented R3b.3 overlay containing exemplar
starts. Coverage is `EXEMPLAR_ONLY`, or `UNRESOLVED` when starts are missing.
It never labels this schema `OCCURRENCE_VERIFIED`: a subwindow count is not a list
of occurrence locations. Boundary extension coverage is explicitly non-exhaustive.
An occurrence-level adapter would require a documented source schema and tests.

Review fields come from one `REVIEW_FIELDS` definition. Only review_status starts
UNREVIEWED. No function/rhetorical labels are generated. Review time is diagnostic
only; the six random cases cannot estimate population-wide hours. Packet volume
can remain substantial because evidence is not truncated to reduce counts.

## Local validation

```bash
python -m py_compile src/milal_r3c_0_2_reviewability.py tests/test_r3c_0_2.py
python src/milal_r3c_0_2_reviewability.py --self-test
python -m unittest discover -s tests -v
```

Retain a synthetic packet for direct inspection with a fresh directory:

```bash
python src/milal_r3c_0_2_reviewability.py --self-test \
  --output-dir results/r3c_0_2_synthetic
```

The self-test uses a 25-container synthetic corpus, ZIP loading, branching,
explicit folding, event-only outcomes, an orphan, span/structure context,
boundary panels, deterministic sampling and deliberately broken invariants.
Unit tests add schema/conflict failures and an optional checked-in Job identity
regression. They do not replace real TF feature loading or empirical review.
