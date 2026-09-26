"""Q1.6R synthetic role/independence cases and data-level gate mutations."""
import copy,json
from pathlib import Path
from milal_q16r_roles import process_role,valency_case,independence,readiness
from milal_q16r_validation import evaluate,gates
from milal_mfr02r_pipeline import code_fingerprint


def basis(key,core,context=(),parents=(),inherited=(),complete=True):
    return dict(id=key,core_raw=list(core),context_raw=list(context),full_raw=sorted(set(core)|set(context)|set(inherited)),analytical_dependencies=list(parents),inherited_core_raw=list(inherited),complete=complete)


def checks():
    c={};v=valency_case('a','b',{'clause'},{'clause'},'clause')
    c['Q16R-S1']=v['primary_role']=='PRE_RELATION_STRUCTURE' and not v['new_relation']
    c['Q16R-S2']=process_role(dict(process_kind='TIME_PARAMETER'))=='CONFIGURATION_CONTEXT'
    c['Q16R-S3']=process_role(dict(process_kind='TEMPORAL_REFERENCE_FORM'))=='REFERENCE_VISIBILITY_CONTEXT'
    c['Q16R-S4']=process_role(dict(process_kind='LOCATION_PARAMETER'))=='CONFIGURATION_CONTEXT'
    c['Q16R-S5']=process_role(dict(process_kind='DERIVED_DOMAIN'))=='REFERENCE_VISIBILITY_CONTEXT'
    c['Q16R-S6']=process_role(dict(process_kind='LEXICAL_REPETITION'))=='CORROBORATIVE_RELATION_EVIDENCE'
    c['Q16R-S7']=process_role(dict(process_kind='LEXICAL_SEMANTICS'))=='POST_RELATION_VALIDATION'
    c['Q16R-S8']=independence(basis('a',['raw']),basis('b',['raw']))['independence_class']=='SAME_RAW_EVIDENCE'
    c['Q16R-S9']=independence(basis('a',['first'],['domain']),basis('b',['second'],['domain']))['independence_class']=='SHARED_CONTEXT_ONLY'
    e=fixture();c['Q16R-S10']=evaluate(e)['NO_NEW_RELATION_QUALIFICATION']
    return c


def fixture():
    def p(kind,role):return dict(process_kind=kind,primary_role=role,distinct_positive_binding=False,new_relation=False,detail={})
    pp=[p('ATOM_CONSTITUTION','PRE_RELATION_STRUCTURE'),p('TIME_PARAMETER','CONFIGURATION_CONTEXT'),p('LOCATION_PARAMETER','CONFIGURATION_CONTEXT'),p('DERIVED_DOMAIN','REFERENCE_VISIBILITY_CONTEXT'),p('LEXICAL_REPETITION','CORROBORATIVE_RELATION_EVIDENCE'),p('LEXICAL_SEMANTICS','POST_RELATION_VALIDATION')]
    return dict(baseline='base',baseline_heads=['base','base','base'],frozen_differences=[],input_hashes={'a':'hash'},current_input_hashes={'a':'hash'},old_outcomes=[{'id':'r'}],new_outcomes=[{'id':'r'}],expected_relations=1,raw_hash_before='raw',raw_hash_after='raw',raw_count=1,expected_raw=1,human_hash_before='h',human_hash_after='h',human_count=1,expected_human=1,
        registry=[dict(mechanism_id='SB%02d'%i,primary_methodological_role='PRIMARY_SOURCE_BINDING') for i in range(1,13)],processes=pp,valency_cases=[valency_case('a','b',{'c'},{'c'},'c')],expected_valency_cases=1,semantic_checks={'Q16R-S3':True,'Q16R-S9':True},native_annotation_changes=[],independence_rows=[independence(basis('a',['raw']),basis('b',['raw']))],forbidden_weighting_fields=[],new_positive_witnesses=[],new_relation_count=0,assignments=[dict(canonical_mother='',canonical_hierarchy='')],new_human_judgments=0,regression=dict(test_scope='FULL_REGRESSION',tests_run=1,failures=0,errors=0,skipped=0,code_fingerprint='fp'),fingerprint='fp',independent_equal=True,manifest_valid=True,zip_crc_valid=True)


def mutations():
    return {
'BASELINE_COMMIT_VERIFIED':lambda e:e['baseline_heads'].append('wrong'),
'Q1_6_FROZEN':lambda e:e['current_input_hashes'].update(a='changed'),
'Q1_6_273_RELATIONS_PRESERVED':lambda e:e['new_outcomes'].append({'id':'new'}),
'RAW_UNIVERSE_UNCHANGED':lambda e:e.update(raw_count=2),
'HUMAN_JUDGMENTS_UNCHANGED':lambda e:e.update(human_hash_after='changed'),
'ALL_SB01_SB12_ROLES_CLASSIFIED':lambda e:e['registry'].pop(),
'PRE_RELATION_VS_SOURCE_BINDING_SEPARATED':lambda e:e['processes'][0].update(distinct_positive_binding=True),
'SB05_INTRA_CLAUSE_VALENCY_SEPARATED':lambda e:e['valency_cases'][0].update(same_native_clause=False),
'TIME_PARAMETER_VS_TEMPORAL_BINDING_SEPARATED':lambda e:e['processes'][1].update(primary_role='PRIMARY_SOURCE_BINDING'),
'LOCATION_PARAMETER_VS_LOCATIVE_BINDING_SEPARATED':lambda e:e['native_annotation_changes'].append('Adju->Loca'),
'DERIVED_DOMAIN_NOT_DOUBLE_COUNTED':lambda e:e['processes'][3].update(distinct_positive_binding=True),
'LEXICAL_REPETITION_VS_ANAPHORA_SEPARATED':lambda e:e['processes'][4]['detail'].update(referential_identity_created=True),
'LEXICAL_FORM_VS_SEMANTICS_SEPARATED':lambda e:e['processes'][5].update(primary_role='PRIMARY_SOURCE_BINDING'),
'EVIDENCE_INDEPENDENCE_CLASSES_REFINED':lambda e:e['independence_rows'][0].update(same_direct_raw=[]),
'NO_EVIDENCE_SCORING':lambda e:e['forbidden_weighting_fields'].append('weight'),
'NO_FORCED_POSITIVE_MECHANISM':lambda e:e['new_positive_witnesses'].append('invented'),
'NO_NEW_RELATION_QUALIFICATION':lambda e:e.update(new_relation_count=1),
'NO_CANONICAL_MOTHER':lambda e:e['assignments'][0].update(canonical_mother='chosen'),
'NO_CANONICAL_HIERARCHY':lambda e:e['assignments'][0].update(canonical_hierarchy='chosen'),
'NO_NEW_HUMAN_JUDGMENT':lambda e:e.update(new_human_judgments=1),
'FULL_REGRESSION_PASS':lambda e:e['regression'].update(failures=1),
'SKIP_ZERO':lambda e:e['regression'].update(skipped=1),
'DETERMINISTIC_RERUN':lambda e:e.update(independent_equal=False),
'MANIFEST_VALID':lambda e:e.update(manifest_valid=False),
'ZIP_CRC_VALID':lambda e:e.update(zip_crc_valid=False)}


def self_test(out):
    cc=checks();negative={}
    for k,m in mutations().items():
        e=fixture();m(e);negative[k]=not evaluate(e)[k]
    r=dict(stage='MFR.0.2R-Q1.6R',checks=cc,gate_negative_tests=negative,passed=all(cc.values()) and all(negative.values()),code_fingerprint=code_fingerprint())
    if out:
        Path(out).parent.mkdir(parents=True,exist_ok=True);Path(out).write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
        review=dict(intra_clause=valency_case('atom_a','atom_b',{'clause'},{'clause'},'clause'),shared_context=independence(basis('w1',['observation_a'],['context']),basis('w2',['observation_b'],['context'])),same_raw=independence(basis('w1',['observation']),basis('w2',['observation'])),semantic_role=process_role(dict(process_kind='LEXICAL_SEMANTICS')),new_relations=0)
        Path(str(out)+'.md').write_text('# Q1.6R synthetic methodological review\n\nNo hierarchy or identity is inferred.\n\n```json\n'+json.dumps(review,indent=2)+'\n```\n',encoding='utf8')
    return r
