"""Post-freeze coverage review of existing external fixtures only."""
from collections import Counter
from pathlib import Path
import json
from milal_mfr02r_data import rows, table, digest, encode
from milal_mfr_observation import read_feature
from milal_mfr02r_scope import read_references
from milal_mfr02r_features import build_features, evidence_values
from milal_mfr02r_layers import unit_candidates, expand_unit_reference
from milal_q1_binding import SourceIndex, MECHANISMS
from milal_q11_diagnostic import binding_obstacles, diagnose_pair, sensitivity, classify_nonretention

SCOPES = ('pentateuch', 'qohelet', 'lamentations', 'isaiah')


def load_fixture(source, q1, tf_path, grammar, scope, native):
    frozen = list(rows(source/'controls'/(scope+'_fixture_source_clauses.csv')))
    refs = sorted({(r['book'], int(r['chapter']), int(r['verse'])) for r in frozen})
    obs, receipt = read_references(tf_path, refs, include_preceding_verse=False)
    ids = {int(r['clause_id']) for r in frozen}
    obs = [r for r in obs if int(r['clause_id']) in ids]
    if {int(r['clause_id']) for r in obs} != ids:
        raise ValueError('fixture identity missing')
    old = json.loads((q1/'control_source_receipts.json').read_text())[scope]
    if json.loads(encode(receipt)) != old['read_receipt'] or digest(source/'controls'/(scope+'_fixture_source_clauses.csv')) != old['source_csv_sha256']:
        raise ValueError('fixture source receipts changed')
    features = build_features(obs, grammar, native)
    inventory = [dict(clause_id=f['clause_id'], position=f['position'],
        clause_atom_ids=f['row']['clause_atom_ids'], word_ids=f['row']['word_ids'],
        clause_type=f['clause_type'], **evidence_values(f)) for f in features]
    index = SourceIndex(inventory, grammar['lexicons']['subordinate_rela'], grammar['lexicons']['speech'])
    return index, features, receipt


def review(source, q1, out, tf_path, grammar, config):
    freeze = json.loads((out/'blind_diagnostic_freeze.json').read_text())
    if not all(digest(out/k) == h for k,h in freeze['files'].items()):
        raise ValueError('blind diagnostics changed before controls')
    mothers, mh = read_feature(tf_path/'mother.tf'); relas, rh = read_feature(tf_path/'rela.tf')
    native = [dict(dependent_node=n, head_node=h, rela=relas.get(n, 'NA'),
        source_feature_sha256=mh['sha256'], relation_feature_sha256=rh['sha256'],
        status='DATABASE_EXISTING_RELATION') for n,heads in mothers.items() for h in heads]
    # Exact native feature hashes are already pinned in the frozen Job inventory;
    # compare again here before building the bounded fixture projection.
    all_native_hashes = {(e['source_feature_sha256'], e['relation_feature_sha256'])
        for r in rows(source/'blind/job/02_clause_feature_inventory.csv') for e in r['CLAUSE']['native_annotations']}
    if all_native_hashes != {(mh['sha256'], rh['sha256'])}:
        raise ValueError('native source changed')
    frozen_controls = list(rows(q1/'16_q1_control_fixture_validation.csv'))
    registry = {r['rule_id']:r for r in grammar['rules']}
    numbers=[]; bosman=[]; coverage=[]; sensitivities=[]; details=[]; receipts={}
    wanted = {tuple(x) for x in config['numbers_controls']}
    for scope in SCOPES:
        index, features, receipt = load_fixture(source,q1,tf_path,grammar,scope,native)
        table(out/(scope+'_source_evidence.csv'), index.rows.values())
        table(out/(scope+'_fixed_q1_units.csv'), (dict(clause_id=k, **v) for k,v in index.units.items()))
        raw = {r['pair_id']:r for r in rows(source/'controls'/(scope+'_fixture_relation_checks.csv'))}
        controls = [r for r in frozen_controls if r['scope']==scope]
        if set(raw) != {r['candidate_id'] for r in controls}:
            raise ValueError('control pair universe changed')
        diagnostic_rows=[]
        for control in controls:
            sid,tid=control['source_id'],control['target_id']; pair=control['candidate_id']
            diagnostic=binding_obstacles(index,sid,tid)
            frozen_witnesses=index.bindings(sid,tid)
            if encode(frozen_witnesses) != encode(control['witnesses']):
                raise ValueError('Q1 frozen fixture witness does not reproduce')
            d=dict(candidate_id=pair,**diagnostic['sb06'])
            if control['original_relations']: diagnostic_rows.append(d)
            relation_mechanisms={rel:sorted({w['mechanism'] for w in control['witnesses']
                if rel in w['allowed_relations']}) for rel in control['qualified_relations']}
            details.append(dict(scope=scope,candidate_id=pair,original=raw[pair],q1=control,
                diagnostic=diagnostic,retained_relation_mechanisms=relation_mechanisms,
                nonretention_categories=classify_nonretention(control,diagnostic),
                classification_limit='DIAGNOSTIC_CAUSES; NOT_ADJUDICATED_FALSE_NEGATIVES'))
            for relation in control['original_relations']:
                if (pair,relation) not in wanted: continue
                admitting=[registry[rid] for rid in raw[pair]['rule_ids'] if registry[rid]['candidate_relation']==relation]
                numbers.append(dict(candidate_id=pair,relation=relation,
                    control_identity='controls/20_num26_variant_control.csv:actual_edges',
                    source_id=sid,target_id=tid,source_nodes=index.rows[sid],target_nodes=index.rows[tid],
                    original_admitting_rules=admitting,original_pair_evidence=raw[pair],
                    q1_record=control,binding_diagnostic=diagnostic,
                    available_evidence_receipts=[scope+'_source_evidence.csv',scope+'_fixed_q1_units.csv',
                        'source/controls/'+scope+'_fixture_global_configuration_checks.csv'],
                    unsupported_relevant_categories=['SB02','SB05','SB10'] if relation=='HYPOTACTIC' else ['SB11','SB12'],
                    unsupported_applicability='CATEGORY_INTENT_ONLY; NO_VERIFIED_ADAPTER_OR_INDEPENDENT_PROOF',
                    failed_requirement='NO_EXACT_NATIVE_OR_CONSTITUENT_PATH_BINDING' if relation=='HYPOTACTIC' else
                        'SB06_CONJUNCTION_FALSE: '+','.join(diagnostic['sb06']['failed_restrictions']),
                    recovery_category='ADDITIONAL_SOURCE_EVIDENCE_AND_PRINCIPLED_MECHANISM' if relation=='HYPOTACTIC' else
                        'REVIEW_CONSERVATIVE_OPERATIONALIZATION_OR_IMPLEMENT_SB11_SB12_WITH_INDEPENDENT_WITNESS',
                    no_control_specific_recovery=True,authoritative_relation_created=False))
        sensitivities.extend(sensitivity(diagnostic_rows,scope))
        table(out/(scope+'_sb06_pair_diagnostics.csv'),diagnostic_rows)
        scoped=[r for r in details if r['scope']==scope]
        coverage.append(dict(scope=scope,fixture_clause_count=len(index.rows),fixture_pair_count=len(controls),
            original_relation_pair_count=sum(bool(r['original_relations']) for r in controls),
            original_relation_alternative_count=sum(len(r['original_relations']) for r in controls),
            qualified_relation_pair_count=sum(bool(r['qualified_relations']) for r in controls),
            qualified_relation_alternative_count=sum(len(r['qualified_relations']) for r in controls),
            retained_relations=[dict(candidate_id=r['candidate_id'],mechanisms=r['retained_relation_mechanisms']) for r in scoped if r['q1']['qualified_relations']],
            missing_known_controls=[list(x) for x in sorted(wanted) if x[0] in raw],
            nonretention_category_counts=dict(Counter(c for r in scoped for c in r['nonretention_categories'])),
            complete_pair_audit='external_pair_coverage_details.csv',
            classification_limit='A_ONLY_NO_ORIGINAL_RELATION; B_C_D_MAY_OVERLAP; NO_HUMAN_CORRECTNESS_ADJUDICATION'))
        if scope=='lamentations':
            edges=[dict(edge_id=r['pair_id']+'-'+rel,source=int(r['source_clause_id']),
                target=int(r['target_clause_id']),relation=rel) for r in raw.values() for rel in r['relations']]
            units={u['unit_id']:u for u in unit_candidates(edges,features,compact=True)}
            table(out/'bosman_existing_fixture_graph.csv',edges)
            for record in rows(q1/'preserved_bosman_control_unit_references.csv'):
                unit=units[record['source_unit_candidate_id']]
                expanded=list(expand_unit_reference(record,unit,features,edges))
                if len(expanded)!=int(record['antecedent_target_pair_count']):
                    raise ValueError('factorized reference expansion changed')
                bosman.append(dict(source_clause_id=record['source_clause_id'],
                    source_unit_candidate_id=record['source_unit_candidate_id'],target_clause_ids=record['target_clause_ids'],
                    frozen_record=record,exact_expansion=expanded,conditional_unit=unit,
                    source_node_identity='EXACT',target_node_identity='EXACT',
                    referential_identity='UNRESOLVED: PNG_OR_LEXICAL_MATCH_DOES_NOT_IDENTIFY_REFERENT',
                    antecedent_selection='EXACT_CANDIDATE_SET_NOT_REFERENTIAL_ADJUDICATION',
                    unit_boundary='CONDITIONAL_REACHABILITY; NO_INDEPENDENT_CLOSURE',
                    path_dependence='ASSIGNMENT_DEPENDENT; USING_TESTED_HIERARCHY_AS_PROOF_IS_CIRCULAR',
                    existing_mechanisms=['SB03','SB02','SB10'],
                    taxonomy_status='SB03_NAMES_THIS_INTENT; IMPLEMENTED_NATIVE_WORD_EDGE_SUBSET_DOES_NOT_COVER_IT',
                    minimum_evidence='INDEPENDENT_TARGET_TO_ANTECEDENT_REFERENCE_PLUS_SOURCE_TO_UNIT_CONSTITUENCY; SOURCE_NODE_RECEIPTS; NOT_THE_EDGE_UNDER_TEST',
                    hierarchy_independent_feasibility='CONDITIONAL_ON_ADDITIONAL_REFERENCE_AND_UNIT_EVIDENCE; NOT_ESTABLISHED_HERE',
                    reference_identity_status='UNRESOLVED',authoritative_relation_created=False))
        receipts[scope]=dict(read_receipt=receipt,clause_ids=sorted(index.rows,key=int),
            full_book_analysis=False,native_hashes=[mh['sha256'],rh['sha256']])
        print('Q1.1 bounded fixture review',scope,len(index.rows),flush=True)
    table(out/'02_q1_1_numbers_missing_control_audit.csv',sorted(numbers,key=lambda r:(r['candidate_id'],r['relation'])))
    table(out/'03_q1_1_bosman_unit_reference_audit.csv',bosman)
    table(out/'06_q1_1_external_control_coverage.csv',coverage)
    table(out/'external_pair_coverage_details.csv',details)
    return sensitivities,receipts


def mechanism_matrix(q1, out):
    counts=Counter(r['mechanism'] for r in rows(q1/'source_binding_witnesses.csv'))
    external=Counter(w['mechanism'] for r in rows(q1/'16_q1_control_fixture_validation.csv') for w in r['witnesses'])
    # Categories in researcher source are intentions, not complete executable definitions.
    basis={
        'SB01':('direct dependency','Exact native head/dependent membership; subordinate rela lexicon','Available native source annotation','LOW: database annotation is not canonical mother'),
        'SB02':('explicit reference','Category only; target suffix/pronoun refers to source constituent','Independently resolved reference with exact nodes','HIGH if inferred from selected hierarchy'),
        'SB03':('constituent/path reference; larger textual unit','Native dependency path from source to antecedent plus target-to-word native edge','Broader unit membership and reference independent of tested assignment','HIGH for Bosman conditional paths; native subset separate'),
        'SB04':('participant linkage','Adjacent native dependency plus secondary-role explicit NP lexical recurrence','Beyond pair-local context: independently established active unit','HIGH if recurrence becomes referential identity'),
        'SB05':('valency dependency','Category only; a valency slot connects the pair','Resolved construction and slot binding with source identities','HIGH if corpus analogue alone supplies attachment'),
        'SB06':('repeated configuration','Contiguous root-linked multi-clause units; lexical NP; non-speech predicate; exact full signature','Validated correspondence independent of tested hierarchy','MEDIUM: sequence link and form do not adjudicate all levels'),
        'SB07':('temporal dependency','Category only; temporal dependency must connect the source and target','Resolved temporal anchor and scope; marker presence insufficient','HIGH if temporal recurrence substitutes for anchoring'),
        'SB08':('locative frame dependency','Category only; locative frame depends on source','Explicit frame anchoring and scope','HIGH if same place lexeme implies shared frame'),
        'SB09':('domain continuation/embedding','Category only; continuation or embedding in a source-bound domain','Source-bound domain transition independent of flags','HIGH if raw domain flags become hierarchy'),
        'SB10':('lexical anaphoric dependency','Category only; lexical anaphor refers to source','Resolved antecedent distinct from lexical equality','HIGH if lexical repetition is treated as identity'),
        'SB11':('established parallel configuration','Category only; independently established parallel configuration','Non-circular correspondence/level witness beyond resemblance','HIGH if same pattern automatically means same level'),
        'SB12':('global configuration constraint','Category only; global constraint on competing configurations','Positive independent constraints; compatibility alone is insufficient','HIGH if selecting graph first supplies its own proof')}
    details=list(rows(out/'external_pair_coverage_details.csv'))
    result=[]
    for mechanism,name in MECHANISMS.items():
        category,definition,missing,risk=basis[mechanism]
        implemented=mechanism in ('SB01','SB03','SB04','SB06')
        result.append(dict(mechanism_id=mechanism,registry_name=name,existing_definition=definition,
            definition_status='GENERALIZED_FOR_MILAL_EXECUTABLE_SUBSET' if implemented else 'INTENT_CATEGORY_NOT_OPERATIONAL_SPECIFICATION',
            definition_provenance='docs/MFR_0_2R_Q1_RESEARCHER_SOURCE.txt:section 4-5; src/milal_q1_binding.py:MECHANISMS'+
                ('; SourceIndex.bindings/native_configuration' if implemented else ''),
            intended_evidence=category,implementation_status='IMPLEMENTED' if implemented else 'UNSUPPORTED_UNRESOLVED',
            q1_available=implemented,q1_job_witness_count=counts[mechanism],q1_external_witness_count=external[mechanism],
            affected_controls=[dict(scope=r['scope'],candidate_id=r['candidate_id']) for r in details
                if any(w['mechanism']==mechanism for w in r['q1']['witnesses'])],
            potential_missing_control_intent='Numbers parallel configurations: SB11/SB12; Bosman containing-unit references: SB03 with SB02/SB10; applicability requires independent evidence',
            missing_prerequisites=missing,circularity_risk=risk,
            similarity_to_proof_risk='Reference identity/structural binding must not be inferred solely from matching forms',
            next_action='Audit conservative scope; retain frozen adapter' if implemented else 'Establish source-grounded operational contract before implementation',
            scholarly_basis='Q1 researcher contract; original Jin/Walton/Bosman/Oosting crosswalks; adapter details GENERALIZED_FOR_MILAL'))
    table(out/'04_q1_1_sb01_sb12_coverage_matrix.csv',result)
    return result
