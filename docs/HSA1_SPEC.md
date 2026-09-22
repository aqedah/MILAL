# HSA1 — Human Structural Adjudication Registry

Authorized by the researcher on 2026-09-22, starting from
`77ca713b9520ce085135dc845f60d920095756cb`. This is a human-authored registry and
source-linkage audit, not an analytical stage or an automatic hierarchy generator.
The task authorizes implementation, synthetic validation, an accepted-artifact
audit, deterministic rerun and commit/push after validation.

## Authority and scope

[HUMAN_STRUCTURAL_ADJUDICATION.md](HUMAN_STRUCTURAL_ADJUDICATION.md) and the equivalent
[CSV](HUMAN_STRUCTURAL_ADJUDICATION.csv) contain 31 researcher-adjudicated records.
REVIEWED is explicitly authorized here. The auditor never writes these files or
fills any human field. Runtime operations only validate and serialize their content.
Configuration assertions are Job-specific regression controls for the supplied
human decisions, not analytical detection rules. Changing human decisions requires
new researcher authorization and a coordinated update of both records and controls.

33 directed pairs express only directly supplied relations. Reciprocal sibling and
parallel judgments count twice; the four explicitly adjudicated Elihu siblings
have 12 directed peer pairs. UNRESOLVED judgments emit no edge. Supplied containing
spans without their own judgment have a blank related judgment ID. No inferred
inverse, transitive closure, parent-span completion or segmentation is performed.
All primary-anchor fields stay blank because the human supplied verse/span-level
decisions rather than unique native-atom choices. Exact source atoms remain linked.

Important distinctions: 2:11 is a paragraph onset; 2:9 remains internal to 2:1–10;
1:13 is a child of 1:6; 27:1/29:1 and the four Elihu onsets are same-level peers.
Not macro-level does not mean subordinate. 40:1 belongs under 38:1, whereas 38:1
and 40:6 are peers. 42:16 is an explicit NO_BOUNDARY human control.

## Accepted source linkage

`config/hsa1_job.json` pins seven accepted result ZIPs: MR1, R3c.3, PROV1, HR1,
R4.0, R4.1 and R4.2. Verify exact SHA256, safe unique members, CRC, complete member
manifests and PASS gates. No fallback paths, fuzzy identities or replacement data.
HSA1 reads the accepted BHSA 2021 native snapshot in R4.2; it does not reload BHSA,
rerun extraction or modify analytical outputs. This validates accepted artifact
provenance, not a new empirical Text-Fabric execution or cross-platform reproduction.

Each existing R4.2 control panel explicitly identifies native clauses, participant
candidates, MR1 markers and formal occurrences. Expand those IDs without truncation.
R4.1's six prior human scopes are separately linked where the researcher cited them;
the R4.2 marker list contains MR1 markers, not those human scopes. Preserve original
MR1 IDs, R4.1 anchor IDs, R4.2 event IDs, HR1 cases and all linked formal IDs.
Validate each upstream archive/member/row hash against the actual pinned source.
Formal PROV1 occurrence indexes and case-source indexes remain in original locators.
HR1 records retain all prior source links, including singleton and extension context.

Native/formal/participant context is evidence to inspect, not computational
confirmation of the human judgment. HR1 itself carries earlier human review.
There is no promotion of 3:1 into MR1, nor of 1:22/2:10 into MR1 explicit closures.
42:7 keeps Wayhi-positive, SIMPLE_AMR and CASE030 separate. Three anonymous entry
events remain UNRESOLVED, including first appearance; four messengers is human-only.
If an exact link is absent, preserve the judgment and use NO_EXACT_MACHINE_LINK.
All current judgments have exact native/context links; this does not erase their
human authority or assert that all have machine-detected markers.

## Validation and output

Stage tests include a negative mutation for every computed gate. Synthetic sources
use fictional IDs and are visibly labeled SYNTHETIC; the human judgments are copied
from the authored source without changing their substantive claims. Synthetic success
does not itself verify real sources. Inspect the synthetic registry/report before the
authorized accepted-artifact audit. Run all earlier regression tests unchanged.

The optional audit package contains 01 judgments, 02 expanded source links with full
source rows and locators, 03 direct relation pairs, 04 negative controls, 05 principles,
06 report, 07 gates, 08 exact human Markdown, 90 metadata and 99 manifest.
No source evidence is reduced to a representative pattern. Output metadata includes
all archive pins, registry/Markdown/config/code hashes, counts and execution mode.
CSV and Markdown must be byte-identical to the human-authoritative inputs.
The human CSV uses the repository's LF contract so Git checkout does not change
its bytes; other derived CSVs use the existing pipeline CSV serializer.
Deterministic serialization and an independent run must reproduce all files and ZIP
bytes. Publication creates fresh paths, verifies written files/ZIP CRC and manifest,
and rehashes inputs before writing. Results and logs remain ignored.

Next required review: **Job 3–26 speech-unit structure**, using the same linguistic
marker criteria. The supplied 3:1/3:2 judgment is only one reviewed part of that
scope. R4.3 whole-book parentage remains blocked pending dialogue-unit review.
All earlier analytical cores and accepted artifacts remain unchanged.
