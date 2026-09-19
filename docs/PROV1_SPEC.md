# PROV1 — Signature Provenance Sidecar

The Signature Feature Provenance Audit closed as **B — EXACTLY_RECONSTRUCTABLE**:
14/14 historical controls and 20,839/20,839 atom hashes matched, with no mismatch
or untested control. R2.2 need not be rerun. PROV1 is non-analytical and is neither
R3c.4 nor R4. This implementation turn authorizes synthetic validation only.

## Trust and reconstruction

The CLI requires five exact historical inputs. SHA256 constants in the sidecar
pin the accepted generator, R2.2, R3b.2, R3b.3 and real R3c.3 ZIP. All five byte
hashes are verified before parsing/derivation. ZIP CRC, safe member paths and
the R3c.3 manifest/source-chain metadata are checked. The generator is read only
for verification; it is never imported or executed. No R1/BHSA/R2.2 main runs.

Historical generator SHA256:
`125bbda9d0ffbb777d811e3f464a3a85f24526b060df67d564ef229d483b79cd`.
R2.2 SHA256:
`a1a6845101f3957756e7748ab78ba85c4c9f39cf7f8e1ba86aed4396fd2716a2`.
Accepted R3c.3 ZIP SHA256:
`5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981`.
The remaining two hashes are the frozen source hashes documented in R3C_3_SPEC.

The pure rules are transcribed from generator lines 100–122, 502–523, 556–557,
638–639, 669, 768 and 859–861. Independent golden assertions cover the historical
xYq0 G0 atom/family hashes and S02135 G6 atom hash. Historical target hashes are
comparison values, never reconstruction inputs.

For atom a and level k, reconstruct `P_k = tuple((key_i, component_i), i=0..k)`.
G0 is `(norm(atom_typ),)`; G1–G6 arrays are decoded from exact R2.2 component
columns and recursively restored to tuples. The names/order are:
G0_atom_type, G1_verbal_morphology, G2_constituent_shape,
G3_core_argument_realization, G4_verbal_lexemes, G5_general_content_lexemes,
G6_entity_identity_lexical_bundles. The historical norm maps only its explicit
missing-token set to ∅; unknown stays unknown, empty tuples serialize as [].

Reading the component tuples in the catalog:

- G1: `(word_vt, word_vs, word_ps, word_gn, word_nu)` for each verb.
- G2: `(phrase_function, phrase_typ)` for each phrase.
- G3: `(phrase_function, phrase_typ, word_class_tuples)` for core arguments;
  each word class is `(word_pdp, word_ps, word_gn, word_nu)`.
- G4/G5: ordered lexeme strings under the historical verb/content filters.
- G6: `(phrase_function, phrase_typ, identity_tokens)`, each token being
  `(word_pdp, word_ls, word_lex)` for proper names/gentilics.

These are source feature names and values, not assigned discourse functions.
Only None and the exact strings `''`, `NA`, `n/a`, `absent`, `?`, `None`, `none`,
`null` normalize to ∅. No whitespace/case/Unicode normalization is added.

`H(x) = SHA256(json.dumps(x, ensure_ascii=False, sort_keys=True,
separators=(',', ':')).encode('utf-8')).hexdigest()`.
Atom hashes are `H(P_k)`. Window/family/refinement hashes are
`H((level, length, tuple(reconstructed atom hashes in explicit sequence order)))`.
Coordinates, IDs, parent metadata and text do not enter that preimage.
Single-atom singleton signatures remain atom hashes, not length-one window hashes.

All family occurrences are verified against the reconstructed family signature.
Downstream bundle occurrence multisets must equal their member-family multisets.
Refinement children partition their parent's occurrences; added values are the
exact child-level component, not a comparison of Hebrew text. Singleton counts
and first uniqueness are recomputed from all reconstructed atom hashes.

## Output contract

All twelve requested filenames are unchanged. Nested CSV cells are compact JSON.
Source locators contain archive role/hash, member/hash, one-based **data** row and
the complete original row. Component position records distinguish newly added
values from cumulative values. Family records retain every occurrence source row.

| Output | Contents |
|---|---|
| 01_atom_signature_provenance.csv | atom/ref/level, added component, cumulative payload, canonical preimage, reconstructed/historical hash, match, source |
| 02_family_signature_provenance.csv | family/level/length/count, sequence key, per-position added/cumulative values, bundle IDs, all occurrences, hashes, source |
| 03_refinement_feature_delta.csv | unchanged parent/child identities and levels, explicit singleton event links, added values, parent/child counts, occurrence windows, child hashes, source |
| 04_singleton_signature_provenance.csv | atom/review identities, counts, first unique and G6 payloads, all seven atom hashes and source |
| 05_downstream_identity_links.csv | lossless source graph: family→bundle, bundle→lineage, atom→review item, review-unit/case summaries, event source mappings, boundary rows and separate overlay rows |
| 06_hash_reconstruction_audit.csv | atom/family/refinement/singleton checks, exact preimages, expected/actual hashes and match |
| 07_human_readable_signature_catalog.md | every family and every G6 singleton, added and cumulative feature values |
| 08_five_case_validation.md | five accepted control IDs, target evidence, explicit ancestor bundles, refinements, separate singleton hash domains, all boundary participants |
| 09_gates.csv | computed gate results |
| 10_method_note.md | interpretation limits and reconstruction rules |
| 90_run_metadata.json | exact source hashes, original R3c.3 metadata/evidence references, mode, counts, no sampling |
| 99_manifest_sha256.csv | SHA256/bytes for every other output; excludes itself |

The crosswalk is a graph of lossless source rows rather than a Cartesian product.
Every review-unit summary has separate case/unit/bundle/lineage/item columns;
family IDs connect through the preserved membership rows. Missing direct fields
are NOT_AVAILABLE_FROM_SOURCE. Event-only identities connect through explicit
R3c.3 source_rows, never synthesized from a hash/text resemblance. Original input
archives must be retained: referenced raw context/boundary evidence is not rewritten.

## Gates and controls

22 gates: exact generator/R2/downstream hashes; schemas; atom/family/refinement/
singleton hash reconstruction; historical IDs; occurrences; genealogy; blank human
judgments; no automatic labels; lossless explicit links; CASE001; CASE007; CASE013;
S02135; CASE025 multiplicity; overlay separation; complete reconstruction audit;
actual output manifest integrity. Every gate has a negative test.

Required columns are checked by exact names without aliases or guessed defaults;
extra source columns are preserved. Invalid geometry, identity, source schemas or
refinement partitioning fail before output. Gates compare derived content to
source-grounded recomputation, not a cached PASS flag. Manifest integrity is
checked against serialized bytes and again after writing. Outputs require a new
directory; no historical file is overwritten.

The five case IDs and Job object IDs are this accepted-artifact validation profile,
not definitions of MILAL semantics. Atom record count is dynamically seven times
the source atom count; 20,839 is a historical Job expectation, not a semantic
constant. Synthetic mode uses explicitly different fixture hashes/counts and is
unavailable as a bypass for real CLI inputs.

## Boundaries

No IDs, memberships, occurrence sets, genealogy, singleton identities, boundary
units, sequence-extension status or human fields are modified. No interpretation
labels are generated. Frozen R3c analytical cores remain unchanged. No real PROV1
execution, commit, push, corrective analytical pipeline, R3c.4 or R4 is authorized
in this implementation turn. The next step is review of synthetic validation,
then a separately authorized real sidecar run.
