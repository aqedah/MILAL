"""Measured release gates; semantic probes also run in synthetic validation."""
import ast
from pathlib import Path
from milal_q13_model import AssignmentModel,MOTHER,PARALLEL,OVERLAY

GATES='''BASELINE_COMMIT_VERIFIED Q1_2_FROZEN Q1_2_QUALIFIED_RELATIONS_UNCHANGED
RELATION_DIMENSIONS_SEPARATED ONE_MOTHER_CONSTRAINT_PRESERVED MULTIPLE_PARALLEL_PEERS_ALLOWED
MOTHER_AND_PARALLEL_CAN_COEXIST PARALLEL_MULTIPLICITY_NOT_AUTOMATIC_COMPETITION
UNSELECTED_EQUALS_UNDECIDED SAME_PAIR_RELATION_CONFLICT_IMPLEMENTED
COHERENT_MULTI_RELATION_ASSIGNMENT_IMPLEMENTED NO_CARTESIAN_VARIANT_EXPLOSION
SB12_CONSTRAINT_ONLY NO_NEW_HUMAN_JUDGMENT NO_CANONICAL_MOTHER NO_CANONICAL_HIERARCHY
Q12_SEVEN_PIVOTS_REAUDITED REFERENCE_LAYER_UNCHANGED UNIT_BOUNDARY_ADAPTER_NOT_YET_CHANGED
FULL_REGRESSION_PASS SKIP_ZERO DETERMINISTIC_RERUN MANIFEST_VALID
PIVOTS_REQUIRE_INCOMPATIBLE_POSITIVE_ASSIGNMENTS SOURCE_BINDING_NOT_RERUN'''.split()


def edge(oid,source,target='t',relation='HYPOTACTIC',**extra):
    return dict(structural_outcome_group_id=oid,source_or_peer=source,target=target,
        relation_type=relation,provenance_paths=[{'witness_id':oid}],**extra)


def semantic_checks():
    m=edge('m','mother');p=edge('p','peer',relation='PARATACTIC');p2=edge('p2','peer2',relation='PARATACTIC')
    orth=AssignmentModel([m,p]);parallel=AssignmentModel([p,p2]);comp=AssignmentModel([m,edge('m2','mother2')])
    samepair=AssignmentModel([m,edge('mp','mother',relation='PARATACTIC')])
    oa=orth.assignment('t',['m','p']);pa=parallel.assignment('t',['p','p2'])
    other=edge('other','x',target='y')
    constraint=dict(kind='FORBIDDEN_COMBINATION',constraint_id='independent',outcome_ids=['p','p2','other'],
        independent=True,constraint_provenance='SYNTHETIC_EXPLICIT_SB12_GLOBAL_CONSTRAINT')
    globalmodel=AssignmentModel([p,p2,other],constraints=[constraint]);proof=globalmodel.incompatible_witness('p','p2')
    overlay=AssignmentModel([m,edge('overlay','overlay-source',relation='SEQUENCE_EXTENSION',non_hierarchical=True)])
    corroboration=AssignmentModel([p,dict(p,structural_outcome_group_id='corroboration',provenance_paths=[{'other':'evidence'}])])
    many=AssignmentModel([edge('p'+str(i),'peer'+str(i),relation='PARATACTIC') for i in range(30)]).analyze()
    exclusion=AssignmentModel([p,edge('excluded','peer',relation='EXCLUDED',excluded_outcome_id='p',constraint_provenance='EXPLICIT_CONSTRAINED_OUTCOME')])
    return dict(
        S1=oa['mother_assignment']['source_id']=='mother' and len(oa['parallel_peer_assignments'])==1 and not orth.analyze()['pivots'][0]['human_review_required'],
        S2=len(pa['parallel_peer_assignments'])==2 and not parallel.errors(['p','p2']) and not parallel.analyze()['pivots'][0]['human_review_required'],
        S3=bool(comp.errors(['m','m2'])) and comp.compatibility('m','m2')['classification']=='TRUE_MOTHER_COMPETITION' and comp.incompatible_witness('m','m2') is not None,
        S4=bool(samepair.errors(['m','mp'])) and samepair.compatibility('m','mp')['classification']=='TRUE_PAIR_RELATION_CONFLICT',
        S5=parallel.assignment('t',['p'])['unresolved_relations']==['p2'] and parallel.assignment('t',[])['unselected_semantics']=='UNDECIDED',
        S6=orth.assignment('t',['m'])['unresolved_relations']==['p'] and orth.incompatible_witness('m','p') is None,
        S7=corroboration.compatibility('p','corroboration')['classification']=='CORROBORATED_RELATIONS' and corroboration.incompatible_witness('p','corroboration') is None,
        S8=proof is not None and not globalmodel.errors(proof['assignment_a']['selected_outcome_ids']) and not globalmodel.errors(proof['assignment_b']['selected_outcome_ids']) and bool(globalmodel.errors(proof['incompatible_union'])),
        S9=parallel.compatibility('p','p2')['parallel_level_constraint']=='UNRESOLVED' and parallel.incompatible_witness('p','p2') is None,
        S10={r['outcome_id'] for r in orth.analyze()['dimensions']}=={'m','p'},
        OVERLAY=overlay.assignment('t',['m','overlay'])['overlay_relations']==['overlay'] and overlay.assignment('t',['m','overlay'])['mother_assignment']['source_id']=='mother',
        SYMBOLIC=len(many['components'])==1 and len(many['assignments'])==1 and len(many['assignments'][0]['coherent_combined_assignment']['selected_outcome_ids'])==30,
        EXPLICIT_EXCLUSION=exclusion.incompatible_witness('p','excluded') is not None,
        GLOBAL_NOT_TARGET=globalmodel.analyze()['pivots'][1]['human_review_required'] is False)


def core_policy(text):
    tree=ast.parse(text);imports=[];calls=[]
    for node in ast.walk(tree):
        if isinstance(node,ast.ImportFrom):imports.append(node.module or '')
        if isinstance(node,ast.Import):imports += [a.name for a in node.names]
        if isinstance(node,ast.Call):calls.append(node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else '')
    return dict(no_cartesian=not {'product','powerset'}&set(calls),
        no_source_binding=not any(any(x in m for x in ('q12_profiles','q12_references','q12_binding','tf.fabric')) for m in imports),
        no_control_ids=not any(x in text for x in ('497625','497623','Job','Numbers','Leviticus')))


def measurements(e):
    s=e['semantic'];t=e['tests']
    values=[e['baseline']==e['expected_baseline'] and e['baseline_verified'],
        not e['frozen_differences'] and e['input_verified'],
        e['qualified_equal'] and e['outcomes_equal'] and e['raw_count']==e['expected_raw'] and s['S10'],
        not e['dimension_errors'] and s['OVERLAY'],s['S3'] and not e['incoherent_assignments'],
        s['S2'] and e['multiple_peers_diagnostic'],s['S1'] and e['mother_parallel_diagnostic'],
        s['S2'] and not e['multiplicity_only_pivots'],s['S5'] and s['S6'] and not e['unselected_errors'],s['S4'],
        s['S1'] and s['S2'] and not e['assignment_errors'],s['SYMBOLIC'] and e['policy']['no_cartesian'] and e['symbolic_coverage'],
        not e['new_positive_ids'] and not e['sb12_positive'] and e['sb12_ids_equal'] and s['S8'],
        e['human_equal'] and e['human_count']==e['expected_human'],not e['canonical_mothers'],not e['canonical_hierarchies'],
        e['reaudit_targets']==e['expected_reaudit_targets'] and e['reaudit_consistent'],
        e['reference_equal'],e['unit_boundary_equal'],
        t['test_scope']=='FULL_REGRESSION' and t['tests_run']>0 and t['failures']==t['errors']==0 and e['fingerprint_matches'],
        t['skipped']==0,e['independent_equal'],e['manifest_valid'],
        not e['invalid_pivot_proofs'] and s['S7'] and s['S8'] and s['S9'] and s['GLOBAL_NOT_TARGET'],
        e['policy']['no_source_binding'] and e['policy']['no_control_ids']]
    assert len(values)==len(GATES)
    return dict(zip(GATES,map(bool,values)))


def assert_gates(e,allow_pending=False):
    result=measurements(e)
    pending={'DETERMINISTIC_RERUN'} if allow_pending else set()
    failed=[k for k,v in result.items() if not v and k not in pending]
    if failed:raise ValueError('Q1.3 gates failed: '+', '.join(failed))
    return [dict(gate=k,status='PASSED' if v else 'PENDING_INDEPENDENT_RERUN') for k,v in result.items()]
