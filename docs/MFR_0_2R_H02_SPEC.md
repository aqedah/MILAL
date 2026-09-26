# MFR.0.2R-H0.2 — append-only human adjudication

Authority: [exact researcher request](MFR_0_2R_H02_RESEARCHER_SOURCE.txt).
Required start: `f343a06dbb93e026d570eb5638316843d6c98724`.
The source request SHA256 is
`903842a2819f7cf727f5d2b6e1219dbc95bc777a042e3c5ac817618bf91e9f29`.
H0.1 and all earlier analytical cores are frozen. 593 tracked file hashes protect
the baseline, excluding the active HANDOFF and appendable .gitattributes.

## Authority and identity

The researcher has supplied one explicit adjudication of the H0.1 packet for
Job 37:20, clause 500065, atom 590199. This is not machine inference or a new
relation-discovery rule. The append-only [CSV registry](HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.csv)
and [human-readable registry](HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.md) transcribe
that authority. Their bytes and the request are pinned in H0.2 configuration.
Future corrections require a new explicit version, not rewriting these records.
The researcher did not supply an adjudication date: it is NOT_SUPPLIED. The
separate recording date is 2026-09-26; review duration is not invented.

Link by exact packet, alternative, relation, clause and atom IDs. Do not match
Hebrew text fuzzily. Researcher surface forms and original machine surface forms
are separate representations linked through those exact identities.

## Decision scope

- 500062 → 500065 remains machine-qualified; the human disposition is
  REJECTED_AS_DIRECT_MOTHER / NO_DIRECT_STRICT_MOTHER_RELATION.
- 500064 → 500065 is HUMAN_ACCEPTED_LOCAL_MOTHER_RELATION, HYPOTACTIC,
  with 500065 STRICTLY_BELOW 500064 in the local hierarchy only.
- Machine W-A01 and SB03 versus SB01/SB02 provenance is retained without revision.
- The accepted human rationale is LOCAL_CONDITIONAL_PROTASIS_APODOSIS_CONFIGURATION;
  machine_rule_rationale_adopted=false. Immediate locality alone is insufficient.
- KI_FUNCTION_CAUTION records that כי is an observed form, not a universal
  semantic assignment. The lexical interpretation of יבלע remains
  UNRESOLVED_FOR_HIERARCHY_PURPOSES while STRUCTURAL_MOTHER_DECISION is RESOLVED.
- Two-colon correspondence is human POST_RELATION_VALIDATION_CONTEXT, not a new
  qualified paratactic edge. W-A01 is not changed, and other כי cases are not reopened.

The other 271 relations are NOT_ADJUDICATED_BY_H02. This status does not override
any earlier explicit human judgments, which remain separately preserved.
Qualified does not imply accepted. No canonical whole-book hierarchy is generated.

## Counting and preservation

One new human decision packet contains two candidate dispositions. The historical
registry has 13 original decision entries. The combined count is 14 decision
entries: 13 legacy entries plus one new packet, not 15 independent decisions.
Historical entries are not relabeled as H0.2 packets. Machine-qualified relations
remain 273 (203 mother, 70 parallel, zero overlay); raw universe remains 1,049,504.
The original machine pivot remains TRUE_DECISION_PIVOT in frozen H0.1. A separate
overlay marks one pivot RESOLVED_BY_HUMAN and zero awaiting adjudication.

Verify the H0.1 ZIP hash, CRC and extracted manifest before use. Copy its complete
30-file package byte-for-byte under frozen_h01; never write into the original.
Hash the actual raw table and historical-human source against the authenticated
H0.1 receipt before and after execution. Preserve the original historical-human
file bytes and all machine-qualified rows. Additional machine_provenance.csv
retains complete original alternatives, grammar, source features and witness IDs.

## Outputs and validation

Required outputs 01–12, metadata 90 and manifest 99 follow the researcher request.
Supplemental machine files preserve the source package, original candidates,
historical judgments, complete provenance, scope and measured gate evidence.
Gates inspect deserialized outputs, check exact authority transcription, and
rebuild expected derived views from the unchanged authority and frozen source.

Required: syntax; focused tests; H02-S1 through H02-S12; negative mutations for
every gate; full regression with zero skips; independent A/B manifests and ZIPs;
CRC checks. Read-only source checks are not empirical execution. Actual output
construction requires both current synthetic and complete regression receipts.
The user authorizes real frozen-input execution and commit/push after validation.

Success: READY_FOR_MFR_0_2R_H1_0. Do not begin H1.0 automatically.
See [execution instructions](README_MILAL_MFR_0_2R_H02.md).
