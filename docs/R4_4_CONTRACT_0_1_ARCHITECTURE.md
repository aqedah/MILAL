# Repository architecture audit — R4.4-CONTRACT.0.1

CONTRACT_PROPOSAL. Baseline `113a1f3fe13ff9698a97f82f3f1a53b41b4f3b21`.
This is an audit of observed code and frozen schemas, not a claim that R4.3
implemented a complete tree. Source paths below identify frozen repository files.

## Observed architecture

| Component | Source | Observed behavior and contract consequence |
| --- | --- | --- |
| R4.2 participant/frame audit | `src/milal_r4_2_participant_audit.py:55` extraction; `:113` derive | Event existence is independent of referential identity. Anonymous entry events stay unresolved. 01 events, 02 enclosures, 13 endpoints and 14 candidate frames retain source identities. |
| R4.2 frame semantics | Same file, `:127`–`:151` | Candidate frame pairing is human supplied; nearest anchors are positional context, explicitly not parentage. Accepted artifact means accepted audit output, not every candidate accepted as a macro unit. |
| HSA1 ingestion | `src/milal_hsa1_registry.py:69`, `:84`, `:185` | Supplied direct relation pairs only, no inverse/transitive completion; hash-pinned accepted artifacts and exact source IDs. |
| HSA2 ingestion | `src/milal_hsa2_closure_audit.py:177`, `:286` | New human records and evidence links are separate from unresolved closure candidates. |
| HSA2-F ingestion | `src/milal_hsa2_final.py:51`, `:78`, `:84` | Frozen candidate records retained; final human decisions linked through candidate IDs. Active closure edges have explicit dimension and authority. |
| R4.3 nodes/edges | `src/milal_r4_3_hierarchy_scaffold.py:106` | Human records compiled through explicit aliases and configuration; node references are judgment loci, not computed coverage. Edge key includes source, target, type and dimension. |
| R4.3 parent constraint | Same file, `:176` | Requires at most one asserted direct parent; zero is allowed. This is an actual cardinality restriction, not evidence of a complete-parent requirement. Future multi-parent policy remains unapproved. |
| R4.3 technical root | Same file, `:131`, `:177`–`:180` | JOB_BOOK is TECHNICAL_ROOT. Every unresolved node gets TECHNICAL_ROOT_LINK for connectivity, not an analytical CHILD_OF edge. Preserve history; never infer hierarchy from it. |
| R4.3 parent/cycle functions | Same file, `:187`, `:196` | Only HIERARCHY-class CHILD_OF/HIERARCHICALLY_ABOVE count as parents. Cycle validation already excludes heterogeneous peer/overlay/navigation edges. |
| R4.3 unresolved model | Same file, `:203` | direct_parent=UNRESOLVED plus known relations/groups/frame context; later_human_review_required=True for every row. Latest necessity decisions supersede that blanket active-review instruction only. |
| R4.3 presentation | Same file, `:265` | Explicitly says partial scaffold, not completed tree. Group indentation is membership only. The later statement that all unresolved rows require review is historical after LAYER.0.2. |
| R4.3 outputs | Same file, `:387` | 06_overlay_relations includes every class except MEMBERSHIP/HIERARCHY/TECHNICAL. It contains horizontal, closure, descriptive and negative relations; it is not the modern OVERLAY_RESPONSIO layer. |
| R4.3 provenance | Same file, `:218`, `:230` | Original human IDs and rows/locators preserved; all 59 historical human records accounted for. Technical objects legitimately have no human judgment IDs. |
| HSA3 canonical registry | `src/milal_hsa3_layer_0_1.py:82`, `:98`, `:131`, `:177`, `:189` | Exact role pairs, canonical node IDs, typed relation layers, qualified annotations, groups and historical/deferred questions remain separate. Confirmed source relations append provenance rather than duplicate edges. |
| HSA3 necessity layer | `src/milal_hsa3_layer_0_2.py:80`, `:92`, `:117` | Exact member+node identity links 57 supplied human necessity decisions; original proposals remain UNREVIEWED and parent fields UNRESOLVED. |
| Archive loading | `src/milal_r4_0_sources.py:44`; LAYER.0.2 `:56` | Exact archive SHA, ZIP integrity, manifests, stage/mode/gates and frozen pins; no replacement artifacts or analytical replay in real mode. |
| Manifest/provenance | LAYER.0.1 `:42`, `:405`; LAYER.0.2 `:80`, `:233` | Raw CSV row/member/artifact hashes plus nested original records; historical archives embedded byte-for-byte. Synthetic receipts are explicitly synthetic. |

The code line ranges are explanatory citations, not executable matching rules.
The audit pins these files and checks the exact source schemas at execution.

## R4.3 assumption findings

- **At most one parent:** observed explicit guard. Preserve current explicit
  claims; do not silently permit multiple parents or require exactly one.
- **Technical root attachment:** observed for unresolved rows, clearly technical.
  Treating those edges as analytical parents would be incompatible with HSA3
  and with R4.3's own documentation.
- **Parent-complete tree:** not observed; expressly disclaimed in code/report.
- **Hierarchy edge as universal relation:** not observed. A common edge table
  contains separate classes and dimensions; its naming is insufficient as an
  R4.4 layer discriminator.
- **Group membership as hierarchy:** not observed; separate MEMBERSHIP class.
  CONTINUES_WITHIN may target an explicit non-textual scope; that is continuation,
  not a direct-parent assertion and must not be rejected as one.
- **Unresolved implies structural incompleteness:** code preserves known relations
  and does not declare them absent. It does require later review of every row;
  that blanket queue policy is obsolete after the 57 necessity decisions.

Reusable unchanged: exact IDs, original records, explicit parent edges, source
judgments/evidence, typed relations, membership positions and raw provenance.
Reusable with extension: node kind/textuality, qualified spans, explicit relation
layer and separate status axes. Deprecated as an active contract: the mixed
06_overlay view, scaffold display and blanket later-human-review flag.
Historical bytes remain unchanged regardless of classification.

## Existing R4.4 material

Before creating this audit, repository filename search found no R4.4 implementation,
specification, tests or runner. Text search across src/tests/config/scripts/docs
found planning/readiness/prohibition references in HSA3 materials, including
HSA3_PREP_SPEC and LAYER.0.1/.0.2 readiness notes. Those propose later recompilation
or contract review; they do not define an implemented complete-tree contract.
This stage adds only contract documentation, proposal configuration and a test
harness under tests. No analytical consumer or final-output schema is created.

## Authoritative artifact chain

The accepted HSA3-LAYER.0.2 ZIP is the outer input, SHA256
`0754eb4c3c22e17ff59627440f8ca5aeb92ee20ecb6a7cdc197240850bb31983`.
Its 01–03 files are authoritative for necessity decisions and exact crosswalks.
Its `history/hsa3_layer_0_1/` registry supplies canonical nodes, seven typed relation
tables, groups, unresolved/deferred records, roles and frozen seams. Its earlier
nested history supplies original observations, HSA1/HSA2/HSA2-F, ANA and A–G decisions.
No latest file overwrites the older authority in a different question/dimension.
All current canonical and supporting state/view records receive a mapping receipt;
historical ancestors are retained wholesale, not miscounted as new active objects.
