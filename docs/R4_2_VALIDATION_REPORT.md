# R4.2 participant transition/enclosure audit — 2026-09-21

Starting commit: `16e13b525a467e63181eb1a434e0c152d96d309a`. Final commit SHA is
reported after push. R4.2 separates source event existence, referential identity,
human control judgments and positional enclosure. Technical validation does not
adjudicate scene status or hierarchy.

## Source contract and scope

Exact accepted pins for MR1/R3c.3/PROV1/HR1 and prior human CSV remain in
config/r4_0_job.json. R4.0 pin remains in config/r4_1_job.json; R4.1 pin is
`92d01bd0deccd6c77c288cd69e7d1eaebeea289f64378f59b667e4aaa91af966` in
config/r4_2_job.json. All six accepted ZIP hashes, CRCs and manifests pass.
Every R4.0/R4.1 member was replayed in memory and matched exactly.

BHSA path: `C:\Users\yisaa\text-fabric-data\github\etcbc\bhsa\tf\2021`.
BHSA 2021 / Text-Fabric 13.1.0; all 65 TF source hashes match accepted MR1.
The source inventory contains 73 actual files: six ZIPs, 65 TF files, prior
human CSV and the newly versioned R4_2_HUMAN_JUDGMENTS.json. All input bytes
are rehashed before publication. No fuzzy linkage or unavailable legacy source.

## Whole-book counts and meaning

Every one of 2938 clauses and **8286 phrases** is audited across Job 1–42.
The inventory retains matched rules and excluded phrases. **452 source-phrase
event candidates** are retained, not 452 proven scene transitions or distinct
referential participants. Proper-name mentions, plural grammatical groups and
overt speech arguments may include reported content/inanimate expressions; no
semantic filter, actor completion or convenience pruning is applied.

| Primary serialization type | Count |
| --- | ---: |
| EXPLICIT_NEW_PARTICIPANT | 39 |
| EXPLICIT_NEW_PARTICIPANT_GROUP | 232 |
| EXPLICIT_SPEAKER_CHANGE | 49 |
| EXPLICIT_ADDRESSEE_CHANGE | 34 |
| OTHER_EXPLICIT_SET_CHANGE | 98 |

All matching types are separately retained. These are surface audit tags:
speaker/addressee tags compare overt expressions, not resolved entities.
EXPLICIT identity means **overt source mention** (449 rows); the three anonymous
deictic entries remain UNRESOLVED. No global entity resolution is performed.
Referential first appearance stays UNRESOLVED for all rows; separate exact-name
lexeme first-word facts do not assert first appearance of a person.

Other counts: 66 frame endpoints (63 MR1 plus three human endpoints), three
explicitly supplied candidate frames, 3362 event/formal span relations,
12722 preserved formal occurrences, 69 shared-ending-family recurrence records,
34 controls, 14 new human judgments, 30 prior human records, 3540 extension rows,
1018 prior human source locators, all 170 Way0 audit rows and 56 historical CSF
speaker-provenance records. Historical implicit speaker records are not identity authority.

## Four-entry result

| Ref | Event / phrase | Clause | Atom | Word node | Identity status |
| --- | --- | --- | --- | --- | --- |
| 1:14 | P:853270 | 497572 | 587677 | 336321 | EXPLICIT overt מלאך |
| 1:16 | P:853300 | 497582 | 587687 | 336363 | UNRESOLVED זה |
| 1:17 | P:853321 | 497590 | 587695 | 336397 | UNRESOLVED זה |
| 1:18 | P:853346 | 497599 | 587704 | 336433 | UNRESOLVED זה |

All four lie positionally inside both supplied candidate envelopes 1:6–1:22 and
1:13–1:22. No anonymous event is deleted or renamed messenger_2/3/4. MR1's
זה_2/3/4 are retained only in the historical-provenance namespace with
identity_authority=false. The four-messenger sequence remains human judgment R42H13.
There were no additional anonymous-entry cases requiring a new resolution rule.

## Wife, friends and Elihu

**Wife 2:9:** P:853525, clause 497658, atom 587764, word 336706, overt אשתו.
The source phrase is explicit; its possessive suffix is not computationally
resolved to Job. The event lies inside the supplied 2:1–2:10 candidate frame.
It is an overt speech-subject expression change candidate, never automatically
promoted to a sibling macro boundary.

**Friends 2:11:** P:853553, clause 497668, atom 587774, words 336749–336751,
retains שלשת רעי איוב as one group phrase. The separate overt name-list phrase
P:853562 at atom 587778 also remains, without invented entity merging. The group
occurs after human ending 2:10 and before human transition 3:1; 3:2 MR1 CSF is
shown separately. No rule branches on the friend names or this reference.

**Elihu 32:2:** P:859068, clause 499627, atom 589755, preserves the entire source
NP with Elihu and identifying names. It is after MR1's 32:1 שבת+ענה closure
and before 32:6 CSF event 43. 31:40 closure,32:1 closure,32:2–5 narrative source
clauses and 32:6 onset remain separate. No role assignment or inferred actor list
is generated from the names within that NP.

Wife/friends differ in their positions relative to the **supplied** frame, while
friends/Elihu both have preceding closure and following opening evidence of
different source kinds. These are audit facts, not automatic same-level/child
or rhetorical-bridge conclusions. New human conclusion/hierarchy fields are blank.

## Enclosure counts

| Positional relation | Rows |
| --- | ---: |
| INSIDE_MARKED_SPAN | 70 |
| BETWEEN_CLOSURE_AND_OPENING | 362 |
| AFTER_CLOSURE | 28 |
| BEFORE_OPENING | 9 |
| Total | 469 |

An event may have two supplied enclosing frames, hence more rows than events.
Nearest anchors are strictly preceding/following, retain ties and are unpaired
context. In particular, a speech onset overlapping its own MR1 event is not its
own strictly following anchor. This positional convention is not hierarchy.

## 1:22 / 2:10 ending comparison

The full verse comparison preserves both 1:22 clauses and all six 2:10 clauses,
including 2:10 speech content preceding the evaluation. No source is truncated
to manufacture a match. The matching evaluation clauses are:

- 497621 / atom 587726: בכל זאת לא חטא איוב.
- 497667 / atom 587773: בכל זאת לא חטא איוב בשפתיו.

Both have type **xQtX**, constituent sequence Cmpl/PP, Nega/NegP, Pred/VP,
Subj/PrNP, and חטא **qal, perfect, third person masculine singular**.
2:10 adds Adju/PP בשפתיו. Exact vocalized/accented surfaces and all morphology
are retained in CSV 03/12 and the reports; the unpointed strings above are explanatory.

Shared formal families: **F000020 (G0), F001232 (G1)**. Full-verse family sets
also contain seven left-only and eighteen right-only families. The 69 whole-book
occurrences of shared families remain formal recurrences only, not newly detected
endings. Both **MR1_EXPLICIT_CLOSURE=false**. The ending/enclosure interpretation
is separately labeled HUMAN_REVIEWED_PARALLEL_ENDING_CANDIDATE.

## 3:1 versus 3:2

3:1: atoms 587793/587794, no MR1 marker. Clause 497687 retains actual Time phrase
אחרי כן, predicate פתח, subject איוב and object את פיהו. This supports the
documented marker-layer gap, with no MR1 extension. 3:2: atoms 587795/587796,
MR1 CSF event 19. The human judgment placing 3:1 above 3:2 remains human-only.

## Validation and artifacts

- Syntax: three new Python source/test files PASS.
- Final full regression: **436 PASS**, no failures/errors/skips: 383 previous
  tests plus **53 R4.2 tests**. Earlier development runs are not substituted for
  this final full-suite result.
- Every computed gate has a negative mutation, including source/manifests,
  anonymous-event deletion, forced identity, human injection, missing frame links,
  formal IDs, closure promotion and forbidden hierarchy fields.
- Final synthetic packet: **31/31 gates PASS**, Windows PowerShell 5.1; inspected
  source tables, unresolved entries and every-event expanded context.
- Final real execution and independent process rerun: **31/31 gates PASS** each,
  PowerShell 7, exit 0. All **27 files and complete ZIP bytes identical**.
- Independent serialized-output audit verified ZIP CRC, exact disk/member bytes,
  manifest completeness/hashes, all 8286 phrase eligibility rows, all blank human
  decision fields, the three unresolved entries and every claimed enclosure.
- All 452 events occur exactly once in the packet's expanded-event section;
  critical reference profiles additionally show full native phrase/morphology tables.

Final ignored artifacts:

- `C:\MILAL\results\r4_2_synthetic_packet_20260921\`
- `C:\MILAL\results\r4_2_real_final_20260921_a\`
- `C:\MILAL\results\r4_2_real_final_20260921_a_results.zip`
- `C:\MILAL\results\r4_2_real_final_20260921_a_run.log`
- `C:\MILAL\results\r4_2_real_final_20260921_b\`
- `C:\MILAL\results\r4_2_real_final_20260921_b_results.zip`
- `C:\MILAL\results\r4_2_real_final_20260921_b_run.log`

Both final ZIPs: 3364490 bytes; SHA256
`7b6c91fb862bf1755c097a9edc31783933388279b54f88796531b0a2419be8d3`.

Results remain ignored; frozen analytical cores and accepted outputs remain
unchanged. No hierarchy edge, score/rank, theological/literary role or new
rhetorical label was generated. Existing human hierarchy statements are retained
only in the explicitly attributed human layer.

Repository files: `src/milal_r4_2_participant_audit.py`,
`src/milal_r4_2_synthetic.py`, `tests/test_r4_2_participant_audit.py`,
`scripts/run_milal_r4_2_windows.ps1`, `config/r4_2_job.json`,
`docs/R4_2_HUMAN_JUDGMENTS.json`, `docs/R4_2_SPEC.md`,
`docs/README_MILAL_R4_2.md`, `docs/R4_2_VALIDATION_REPORT.md`, `docs/HANDOFF.md`.

## Remaining methodological work

Researcher review must decide which broad grammatical candidates are actual
participant-set/scene changes, and how supplied enclosing evidence bears on the
already recorded human hierarchy judgments. No universal participant-change
hierarchy rule has been inferred. Computer-A technical reproducibility is tested;
the inherited strict archived-path portability limitation remains explicit.
