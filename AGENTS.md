# MILAL Agent Instructions

MILAL stands for **Marker-Informed Linguistic Analysis of Layers**.

This repository implements a bottom-up, surface-marker-based analysis of the Hebrew Bible. The project must preserve the distinction between detected textual structure, navigation structure, human review, and later interpretation.

The repository is used on multiple Windows computers through the same GitHub repository. The Git repository is authoritative project state. The verified remote is the shared synchronization point; local commits and uncommitted changes must be inspected and preserved. Local Codex conversation history is not authoritative project state.

---

## 1. Source of truth

Use the following hierarchy when determining the current project state:

1. Git repository and current checked-out files
2. `docs/HANDOFF.md`
3. Current specifications under `docs/`
4. Tests and configuration
5. Previous Codex conversation history

Never assume that local Codex chat history is current.

`docs/HANDOFF.md` is the sole authoritative entry point for determining the current development stage and active specification.

Do not reconstruct project state from memory when the repository and `HANDOFF.md` provide a more recent state.

---

## 2. Beginning a work session

When the user says:

`작업 시작`

or otherwise asks to continue MILAL development on a different computer, perform the following before modifying files.

1. Read local `AGENTS.md` before synchronization.
2. Verify the repository root, `origin` URL, current branch, and configured upstream.
3. Run `git status` and inspect local commits and uncommitted changes.
4. If the working tree is clean and the branch is `main` tracking `origin/main`, run:

   `git pull --ff-only origin main`

5. Confirm:
   - current branch
   - latest commit
   - whether local `main` matches `origin/main`
6. Reread `AGENTS.md` after synchronization in case it changed.
7. Read or reread `docs/HANDOFF.md` after synchronization in case it changed.
8. Read the active specification named by HANDOFF.
9. Report the current MILAL stage and the next pending task.
10. Only then begin implementation.

On another branch or detached HEAD, do not switch automatically. Report the state. If synchronization is skipped, make clear that an unfetched `origin/main` is only the locally recorded remote state.

If the working tree is not clean:

- do not pull automatically;
- do not discard local changes;
- inspect and report the changes first.

If `git pull --ff-only origin main` fails, report the actual failure. Distinguish divergence from authentication, network, remote, and upstream-configuration failures. Do not automatically merge, rebase, reset, or force. Stop Git synchronization until the failure is resolved.

Never use `git push --force`.

Never rewrite published history.

---

## 3. Ending a work session

When the user says:

`작업 종료`

perform the following:

1. Run all tests relevant to the work just completed.
2. Run the full regression suite when the change affects shared analytical logic.
3. Run the current stage self-test.
4. Inspect `git diff`.
5. Run `git status`.
6. Summarize:
   - changed files
   - methodological changes
   - test results
   - unresolved assumptions
   - whether frozen analytical layers remained unchanged
7. Propose a concise commit message.

Do not commit or push merely because the user said `작업 종료`.

When the user says:

`작업 종료. GitHub에 반영하세요.`

or explicitly instructs Codex to finalize and synchronize the work:

1. update `docs/HANDOFF.md` if the project stage, state, or pending task materially changed;
2. validate the final intended changes, including HANDOFF updates, using the requirements above;
3. stage only intended repository files and inspect the staged diff;
4. verify that local inputs, BHSA data, result ZIPs, logs, caches, temporary files, and other ignored artifacts are not being committed;
5. commit only intended files with a concise descriptive message;
6. push the intended branch to the verified `origin` without force;
7. if push is rejected, stop and report the cause;
8. confirm the resulting commit and remote branch state;
9. report any unrelated remaining changes without staging or discarding them.

---

## 4. Multi-computer workflow

MILAL may be developed on computer A or computer B.

The workflow is:

`finish work → validate → commit → push → move computers → pull --ff-only → continue`

Do not rely on Codex conversation synchronization between computers.

Repository files carry project continuity.

In particular:

- `AGENTS.md` carries operating rules.
- `docs/HANDOFF.md` carries current project state.
- Git history carries implementation history.
- Specifications carry methodological decisions.
- Tests carry executable invariants.

Avoid simultaneous uncommitted development on multiple computers.

---

## 5. Analytical-layer discipline

MILAL is a bottom-up structural analysis.

Do not introduce interpretive labels without authorization for a later interpretive stage. The R3 prohibition in section 7 remains unconditional within R3.

Surface evidence must remain distinguishable from later interpretation.

Do not reduce candidates merely to make outputs smaller or easier to review.

Do not silently discard exceptions.

Do not merge structurally different objects because they look semantically similar.

Do not infer identity from similar Hebrew surface text, span, signature, or location when explicit source identity exists.

Preserve provenance.

Preserve source identifiers.

Preserve source relationships.

Prefer deterministic behavior. Random sampling must use a fixed seed recorded in run metadata and relevant outputs.

Never guess a missing required source column. Fail with an explicit schema error when a required invariant cannot be established.

Keep BHSA/Text-Fabric assumptions explicit and inspectable. Update applicable specifications, README instructions, and runners whenever CLI arguments or output schemas change.

---

## 6. Frozen layers

Once a stage has been empirically validated and frozen, do not modify its analytical core merely to make a later stage easier to implement.

Later stages should consume or derive from frozen outputs whenever possible.

Historical output artifacts must not be retroactively rewritten to reflect later methodological decisions.

If a genuine bug is discovered in a frozen layer:

1. document the bug;
2. demonstrate it with a failing test;
3. explain which historical results are affected;
4. create an explicit corrective version rather than silently changing historical behavior.

---

## 7. R3 methodological constraints

R3 detects, organizes, and presents structural evidence.

R3 must not automatically assign rhetorical, discourse, theological, semantic, or functional labels. Later interpretation belongs in a separately authorized stage.

R3b.3 remains frozen as the navigation layer. R3c derives human-review objects or views without redefining that layer. A navigation object is not automatically a human-review unit.

Every singleton outcome must remain independently reviewable, including outcomes genealogically attached to a parent lineage.

Boundary verses may participate in multiple patterns simultaneously. Never replace a complete boundary panel with one representative pattern.

Do not hard-code Job-specific corpus counts into MILAL semantics. Job-specific expected counts may appear only as optional regression assertions. Corpus-specific controls belong in configuration.

Sequence-extension relations are a separate overlay and must not contaminate the core genealogy.

Where extension evidence is exemplar-based only, label it accordingly.

Absence of exemplar evidence must not be interpreted as proof that no extension exists.

Canonical singleton folding must use explicit identity only.

For mapped singleton outcomes, equivalence depends on the explicit mapping relation, not textual similarity.

The Job control `S02135` (`תמו דברי איוב`, Job 31:40) must remain independently reviewable and must remain a regression control unless a later specification explicitly supersedes it.

---

## 8. Human-review discipline

Human-review fields must not be automatically completed by the code.

Keep one canonical `REVIEW_FIELDS` definition and derive or import all human-review schemas from it; do not duplicate its literal definition across implementation code.

Unless a specification explicitly changes the rule, use the canonical review fields:

- `review_status`
- `observable_behavior`
- `recurring_context`
- `exceptions`
- `sufficient_context`
- `additional_information_needed`
- `review_time_seconds`
- `reviewer_notes`

Only `review_status = UNREVIEWED` may be prefilled.

Human review time is diagnostic only.

Do not extrapolate total review time from a small pilot unless a later methodology explicitly authorizes such inference.

---

## 9. Evidence preservation

A presentation-layer improvement must not become an analytical deletion.

When compacting or reorganizing human-facing evidence:

- preserve every source evidence ID;
- preserve every target occurrence;
- preserve raw relations in machine-readable form;
- preserve boundary evidence;
- preserve provenance;
- preserve extension overlay rows;
- keep compact summaries traceable to raw data.

Human-facing packets may collapse repeated presentation, but machine-readable evidence must remain lossless and every summary must remain traceable to source records. A later specification must not silently relax this invariant.

---

## 10. BHSA and Text-Fabric

Windows is the primary empirical execution environment.

The normal external BHSA/Text-Fabric 2021 location is outside the Git repository.

Do not commit BHSA data to this repository.

Do not hard-code a user-specific absolute BHSA path into analytical Python code.

Runners may accept explicit paths.

Repository-local Python defaults should be derived from the repository root rather than hard-coded to `C:\MILAL`.

Termux remains a secondary or cross-validation environment unless `docs/HANDOFF.md` states otherwise.

---

## 11. Git-tracked versus local data

Source code, specifications, configuration, tests, small regression fixtures, and handoff documentation belong in Git.

Large or machine-specific artifacts generally do not.

Do not commit:

- real pipeline input ZIPs;
- generated result directories;
- generated result ZIPs;
- run logs;
- BHSA/Text-Fabric corpus data;
- virtual environments;
- caches;
- temporary files.

Minimal regression fixtures may be committed when they preserve documented historical invariants required for reproducible tests.

---

## 12. Testing requirements

Do not report implementation success merely because code runs.

These validation requirements apply to analytical stages and evidence-presentation stages.

For a new stage:

1. run syntax validation;
2. run stage-specific unit tests;
3. run previous regression tests;
4. run the stage self-test;
5. verify computed gates;
6. include a negative test or mutation for every gate demonstrating failure when its invariant is violated;
7. inspect the human-facing synthetic output;
8. perform real-data execution only after synthetic validation passes.

Synthetic validation does not itself authorize real-data execution; follow the user-authorized execution scope recorded in `docs/HANDOFF.md`.

Do not weaken an old regression test merely to make new code pass.

When a test is skipped, report:

- exact test name;
- what it verifies;
- why it was skipped;
- whether the skip affects empirical execution.

Prefer zero skipped regression tests when stable minimal fixtures can reasonably be committed.

---

## 13. Gates

Every gate must compute an invariant from actual data. No gate may pass unconditionally.

Every gate must have a negative test or mutation demonstrating failure when its invariant is violated.

A successful process exit means the programmed invariants passed. It does not by itself constitute scholarly or human acceptance of the resulting evidence.

---

## 14. Version progression

Do not advance to the next methodological stage merely because the current code is technically functional.

Advance only when the empirical question of the current stage has been answered.

Keep separate:

- implementation success;
- data integrity;
- cross-platform reproducibility;
- human reviewability;
- methodological acceptance.

Do not proceed to R4 until the R3 human-review design is empirically accepted.

The current stage and next pending task must be taken from `docs/HANDOFF.md`, not hard-coded in this file.

---

## 15. Codex reporting format

At the end of a development task, report concisely:

### Implemented
What was changed.

### Methodological interpretation
What analytical decision the implementation embodies.

### Files changed
Exact repository paths.

### Validation
Exact test counts, gate counts, self-test results, and empirical-run status.

### Frozen layers
State explicitly whether previous analytical cores were modified.

### Remaining work
Identify the next unresolved methodological or empirical question.

Do not substitute implementation description for methodological interpretation.

---

## 16. User-facing execution workflow

The user prefers commands that can be executed with minimal manual repetition.

When giving PowerShell execution instructions:

- prefer one complete copy-and-paste block;
- perform related checks and execution in the same block where safe;
- avoid making the user enter many separate commands unless troubleshooting requires it;
- print clear section headers and final result paths.

Do not sacrifice safety merely to make commands shorter.

---

## 17. General principle

MILAL should move from evidence to interpretation in explicit stages.

A later interpretive convenience must never be allowed to silently redefine earlier textual evidence.

When uncertain, preserve the evidence, preserve provenance, preserve object identity, and defer interpretation.
