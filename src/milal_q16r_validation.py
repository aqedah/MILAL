"""Data-level invariants for the Q1.6R classification-only stage."""
from milal_q16r_roles import ROLES,INDEPENDENCE

def evaluate(e):
    tests={
'BASELINE_COMMIT_VERIFIED':bool(e['baseline']) and len(set(e['baseline_heads']+[e['baseline']]))==1,
'Q1_6_FROZEN':not e['frozen_differences'] and e['input_hashes']==e['current_input_hashes'],
'Q1_6_273_RELATIONS_PRESERVED':e['old_outcomes']==e['new_outcomes'] and len(e['new_outcomes'])==e['expected_relations'],
'RAW_UNIVERSE_UNCHANGED':e['raw_hash_before']==e['raw_hash_after'] and e['raw_count']==e['expected_raw'],
'HUMAN_JUDGMENTS_UNCHANGED':e['human_hash_before']==e['human_hash_after'] and e['human_count']==e['expected_human'],
'ALL_SB01_SB12_ROLES_CLASSIFIED':{r['mechanism_id'] for r in e['registry']}=={'SB%02d'%i for i in range(1,13)} and all(r['primary_methodological_role'] in ROLES and r['primary_methodological_role']!='UNRESOLVED_ROLE' for r in e['registry']),
'PRE_RELATION_VS_SOURCE_BINDING_SEPARATED':all(not r['distinct_positive_binding'] and not r['new_relation'] for r in e['processes'] if r['primary_role']=='PRE_RELATION_STRUCTURE'),
'SB05_INTRA_CLAUSE_VALENCY_SEPARATED':len(e['valency_cases'])==e['expected_valency_cases'] and all(c['same_native_clause'] and c['primary_role']=='PRE_RELATION_STRUCTURE' and not c['new_relation'] for c in e['valency_cases']),
'TIME_PARAMETER_VS_TEMPORAL_BINDING_SEPARATED':all(r['primary_role']=='CONFIGURATION_CONTEXT' and not r['distinct_positive_binding'] for r in e['processes'] if r['process_kind']=='TIME_PARAMETER') and e['semantic_checks']['Q16R-S3'],
'LOCATION_PARAMETER_VS_LOCATIVE_BINDING_SEPARATED':all(r['primary_role']=='CONFIGURATION_CONTEXT' and not r['distinct_positive_binding'] for r in e['processes'] if r['process_kind']=='LOCATION_PARAMETER') and not e['native_annotation_changes'],
'DERIVED_DOMAIN_NOT_DOUBLE_COUNTED':all(r['primary_role']=='REFERENCE_VISIBILITY_CONTEXT' and not r['distinct_positive_binding'] for r in e['processes'] if r['process_kind']=='DERIVED_DOMAIN'),
'LEXICAL_REPETITION_VS_ANAPHORA_SEPARATED':all(r['primary_role']=='CORROBORATIVE_RELATION_EVIDENCE' and not r['detail'].get('referential_identity_created') for r in e['processes'] if r['process_kind']=='LEXICAL_REPETITION'),
'LEXICAL_FORM_VS_SEMANTICS_SEPARATED':all(r['primary_role']=='POST_RELATION_VALIDATION' and not r['distinct_positive_binding'] for r in e['processes'] if r['process_kind']=='LEXICAL_SEMANTICS'),
'EVIDENCE_INDEPENDENCE_CLASSES_REFINED':all(r['independence_class'] in INDEPENDENCE and not (r['independence_class']=='SAME_RAW_EVIDENCE' and not r['same_direct_raw']) for r in e['independence_rows']) and e['semantic_checks']['Q16R-S9'],
'NO_EVIDENCE_SCORING':not e['forbidden_weighting_fields'],
'NO_FORCED_POSITIVE_MECHANISM':not e['new_positive_witnesses'],
'NO_NEW_RELATION_QUALIFICATION':e['new_outcomes']==e['old_outcomes'] and e['new_relation_count']==0,
'NO_CANONICAL_MOTHER':not any(a['canonical_mother'] for a in e['assignments']),
'NO_CANONICAL_HIERARCHY':not any(a['canonical_hierarchy'] for a in e['assignments']),
'NO_NEW_HUMAN_JUDGMENT':e['new_human_judgments']==0,
'FULL_REGRESSION_PASS':e['regression'].get('test_scope')=='FULL_REGRESSION' and e['regression'].get('tests_run',0)>0 and not e['regression'].get('failures',1) and not e['regression'].get('errors',1) and e['regression'].get('code_fingerprint')==e['fingerprint'],
'SKIP_ZERO':e['regression'].get('skipped')==0,
'DETERMINISTIC_RERUN':e['independent_equal'],
'MANIFEST_VALID':e['manifest_valid'],
'ZIP_CRC_VALID':e['zip_crc_valid']}
    return tests

def gates(e,pending=()):
    rr=[dict(gate=k,passed=bool(v),status='PASS' if v else 'PENDING' if k in pending else 'FAIL') for k,v in evaluate(e).items()]
    fail=[r['gate'] for r in rr if r['status']=='FAIL']
    if fail:raise ValueError('Q1.6R gates failed: '+str(fail))
    return rr
