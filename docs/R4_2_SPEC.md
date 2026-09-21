# R4.2 — Participant-Set Transition & Enclosure Audit

Authorized by the researcher's task and anonymous-entry clarification of 2026-09-21.
Starting HEAD: 16e13b525a467e63181eb1a434e0c152d96d309a. Implement, test, inspect
synthetic, execute real BHSA, rerun deterministically, inspect and commit/push after
validation. No final hierarchy or parentage. Frozen MR1/R4.0/R4.1 remain unchanged.

## Event existence and identity

An explicit participant-entry event may be preserved even when the participant's
referential identity cannot be resolved from the permitted surface evidence.
Event existence and participant identity are separate claims.

1:14 has overt מלאך. 1:16/17/18 have overt זה plus בוא. All four source-node
events remain. The three deictic entries have identity UNRESOLVED, first appearance
UNRESOLVED and no named role. Historical MR1 זה_2/3/4 and
IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT remain provenance only, never identity authority.
The researcher's four-messenger sequence is a separate human control.

## Uniform extraction contract

Traverse every BHSA Job clause and every phrase in native order. Store every
phrase's matched rules or exclusion; no reference/control list enters extraction.
One event per matching source phrase preserves all matching rule names/types.
The rules are intentionally surface **audit candidates**, not an animate-entity
classifier, a scene detector or inferred participant-state model:

1. Any overt proper name (`sp=nmpr`) within a phrase: preserve the entire source
   phrase and each name word. Names inside identifying/genitive phrases are not
   split into inferred actors; geographical/patronymic roles are not guessed.
2. Overt nominal subject (`pdp=subs/nmpr`) in a clause with source verbal lexeme
   בוא or configured אמר/ענה/דבר: retain the explicit entry/speech argument.
3. Overt plural nominal or configured numeral in a subject phrase: retain as
   one grammatical group candidate, never split members or infer group identity.
4. Demonstrative subject (`sp=prde`) with בוא: anonymous entry, not deleted.
5. Overt nominal Objc/Cmpl/Voct in a speech-verb clause: retain source argument
   as addressee-context candidate, without declaring every argument a recipient.

Plural/nominal morphology may include inanimate or reported-content expressions.
They remain explicitly unadjudicated, with source function/domain in native data;
semantic knowledge cannot suppress inconvenient cases or make actors out of them.
The review must decide whether these candidates are actual scene participants.

Type tags NEW_PARTICIPANT/GROUP describe overt introduction candidates, not claims
of a previously nonexistent referent. SPEAKER/ADDRESSEE_CHANGE compares the exact
overt expression against the preceding explicit expression in that source channel.
It does not establish entity inequality, speaker identity or semantic addressee.
All matching types are preserved; the primary type is only serialization order.
EXPLICIT_REENTRY is not asserted without permitted cross-occurrence identity.

Explicit source mention identity is its phrase node, not a global entity ID.
Even proper-name homonyms and possessive suffix referents are not resolved.
First referential appearance remains UNRESOLVED. A separate field records the
first encountered **exact proper-name lexeme word node**, solely as a lexical
occurrence fact. The wife surface אשתו does not computationally resolve its
possessor; the supplied wife label stays in the human/control report.
No named roles, pronoun resolution, previous-subject transfer, animacy inference,
literary/theological labels or free coreference are introduced.

## Human judgments and frame evidence

All researcher judgments are versioned verbatim in R4_2_HUMAN_JUDGMENTS.json.
Their explicit same-level/internal/new-paragraph conclusions remain human-only;
none generates a computational hierarchy edge. Prior HR1 records and dependencies
are preserved. New human conclusion/hierarchy fields stay blank and status UNREVIEWED.

MR1 CSF/Wayhi are opening **candidates**, not proven openings. MR1's two closures
remain unchanged. Human 1:22/2:10 endings are separate
HUMAN_REVIEWED_PARALLEL_ENDING_CANDIDATE endpoints, never new MR1 closures.
Human 3:1 is a separate surface-transition control endpoint, not an MR1 extension.

Only explicitly supplied human candidate pairs form enclosures: 1:6–1:22,
1:13–1:22,2:1–2:10. Preserve every source opening at each supplied reference.
Enclosure compares complete event clause spans to inclusive native-index endpoints.
INSIDE_MARKED_SPAN means positional inclusion in that human-supplied candidate
frame, not acceptance of its boundary or parentage. Outside those supplied frames,
record nearest strictly preceding/following opening/closure candidates, preserving
ties. BETWEEN_CLOSURE_AND_OPENING and related tags are positional descriptions of
unpaired anchors. They must not be read as automatic scene or macro segmentation.

Participant change is scene-transition evidence, not automatic macro-boundary.
The same rule applies to messengers/wife/friends/Elihu and the whole book.
Surrounding opening/closure frames can inform later hierarchy review. Semantic
content alone never creates a structural unit. Explicit linguistic evidence remains
primary; human hierarchy adjudication stays separate.

## Parallel endings and 3:1 gap

Compare full native evidence at 1:22 and 2:10: atom membership/type, clause type,
phrase function/type, every word's exact surface, lexeme, POS and verbal morphology.
The complete 2:10 verse includes speech material before its final evaluation;
never silently truncate it to fit 1:22. Clause rows let the researcher separately
inspect 497621/587726 versus 497667/587773 and all differences.
Formal family overlap uses all exact occurrences overlapping the control verse.
Shared family levels and exact family/lexeme set intersections/differences have
no score. All book occurrences of those shared families are retained as formal
correspondences, not automatically discovered endings or new MR1 closures.

3:1 retains actual Time/Pred/Objc evidence for אחרי כן / פתח איוב את פיהו.
3:2 CSF remains separate. This documents a marker-layer extension question without
editing the frozen MR1 rule. Human 42:16 continuation remains an exact judgment,
not a universal suppression rule for overt mentions in that verse.

## Accepted input and outputs

Verify exact pins/manifests/CRC for MR1,R3c.3,PROV1,HR1,R4.0,R4.1 and committed
human data; replay frozen R4.0/R4.1 members in memory and require byte equality.
All current BHSA feature hashes match accepted MR1. Source IDs link native
word/phrase/clause/atom records. No replacement/fuzzy sources. Strict replay
retains the prior computer-A path limitation. Rehash sources before publication.

01 events; 02 enclosure positions; 03 endings; 04 Job1–3; 05 wife/friends;
06 friends/Elihu; 07 every phrase's whole-book inclusion/exclusion; 08 all event
review index plus critical profiles; 11 gates; 12 full native features; 13 endpoints;
14 supplied human frames; 15 new human judgments; 16 controls; 17 all shared-family
recurrences; 18 sources; 19 historical speaker provenance; 20 complete formal
inventory; 21 prior human rows; 22 extensions; 23 prior human locators; 24 Way0
audit; 25 this method; 26 exact new human JSON; 27 participant/formal span relations
relative to each native source clause (not inferred scene extent); 90 metadata; 99 manifest.

Every new gate has a negative mutation. Synthetic inspection precedes real
execution; all regression tests, independent rerun and manifest audits must pass.
New identity ambiguity requiring a rule beyond this explicit contract stops work.
No inference to resolve such ambiguity is allowed.
