# R4.4-CONTRACT.JIN.0.1 audit specification

Baseline: `28162717d229c8541d9386668ab7123cd7cded10`.
The exact request authorizes append-only compatibility audit, synthetic/real
validation, deterministic rerun and commit/push. No parent adjudication or R4.4
consumer is authorized. The audit harness lives in tests, not analytical src.

## Inputs and preservation

Read the pinned Contract.0.1 archive:
`results/r4_4_contract_0_1_real_final_20260924_a_results.zip`, SHA256
`9fb5e4ec65cb7eb8961a1ee25c4cd7f64a0c5ee598fb160d0dcd0bfaae5560f2`.
Verify CRC, stage, mode, gates, 257 members and all nested manifests. Preserve
every input member under `history/r4_4_contract_0_1/`; inspect the original
canonical LAYER.0.1 nodes/relations and LAYER.0.2 necessity records, not the
unapproved contract projection as if it were an accepted registry.
Verify 180 frozen repository pins. No historical source is edited or replayed
in real mode. Synthetic mode explicitly rebuilds frozen synthetic fixtures.

Each node, relation, necessity and native clause link carries exact member,
identity, row number, raw-row hash, member hash and outer artifact hash.
Keep complete original records, accepted annotations and nested provenance.
Anchor links use explicit BHSA clause identity only. Missing anchors remain
NOT_RECORDED; no location/surface matching or inferred coverage is allowed.

## Deterministic audit proposals

- SM3: explicit COMPOSITION_GROUP; SM4: explicit ROLE_ALIAS; SM5: TECHNICAL_ROOT.
- SM2: actual textual node with exactly one accepted mother under the frozen
  R4.3 parent semantics.
- SM1: motherless actual textual node with recorded TEXTUAL_HIERARCHY
  participation or explicit onset/introduction function listed in configuration.
  This is the requested macro-reading proposal, conditional on Q8/JIN-Q0 and
  separately adjudicated root exception. It does not create a unit or mother.
- SM7: evidence-only anchor, unclear hierarchy participation or multiple-mother
  conflict. In particular, a transition/ending label without hierarchy evidence
  does not automatically establish daughter status. SM7 is not an exemption.
- SM6 is reserved for explicit textual-root candidate evidence. None is supplied
  by this baseline; no candidate is fabricated from chronology or missing parent.

Count TEXTUAL_NODE and TRANSITION_ANCHOR with source textual=true separately from
ROLE_ALIAS. Preserve evidence-only anchors as a separate kind; their clause
identity does not make them accepted macro daughters. Report both total source
textual=true (including aliases) and actual non-alias textual-node totals.

All actual textual nodes with no mother are retained in the zero-mother table.
Flag SM1/SM7 actual textual nodes for later scope/parentage review. Before mother
adjudication, resolve SM7 participation and Q8/JIN-Q0. The separate evidence-only
SM7 rows belong to a clause-scope applicability question, not automatic macro
parentage. All node proposals remain UNREVIEWED with human_judgment=false.

Count unique existing mother IDs; report conflicts rather than select one.
The frozen schema only treats CHILD_OF and reversed HIERARCHICALLY_ABOVE as
direct. CONTINUES_WITHIN / DIRECT_LOCAL_CLOSURE remain placement. Any unrecognized
hierarchy type is explicitly ambiguous, never inferred from name.

Candidates use explicit accepted placement/closure between actual textual nodes
or same-level correspondence to a textual node with an existing mother. Keep
candidate=UNADJUDICATED and accepted_relation=false. Exclude self-candidates,
non-textual/technical/alias mothers and conservatively withhold a pair with any
explicit pairwise negative pending dimension-specific human review. No nearest,
chapter, speaker-only, theme-only, membership-only or technical rule is used.
No transitive parent is inferred. Native linguistic evidence remains available
by exact anchor links for subsequent adjudication; no fresh BHSA run is needed.

Same-level pairs with known mothers are checked for consistency; other pairs
remain review evidence. No common mother is automatically asserted. Proposed
candidate evidence must never modify existing parent lists or relations.

## Output and validation

Required files 01–13/90/99 plus same-level checks, the single methodological
decision, exact request, current readiness, source inventory and this spec.
The historical 57-row crosswalk preserves old necessity and additional-review
flags alongside current applicability and review status. Job 2:11 retains its
accepted unit, negative and composition claims; its new single-mother question
is OPEN with no assigned mother. All historical and revised questions remain
UNREVIEWED; no node-specific human judgment is created.

Syntax, stage unit tests, every computed gate's negative mutation, previous full
regression skip-zero, self-test, synthetic packet inspection, frozen-real audit
and independent deterministic ZIP rerun are required. Manifest verification and
external full-regression/ZIP-equality release gates must test actual payloads.
Passing technical gates is not scholarly acceptance. Only the one expressly
supplied methodological decision is human-authoritative.
