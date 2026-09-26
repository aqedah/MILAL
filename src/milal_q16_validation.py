"""Computed Q1.6 release invariants. Every predicate has a negative mutation."""
GATE_FIELDS={
'BASELINE_COMMIT_VERIFIED':'baseline_verified','Q1_5_FROZEN':'frozen_equal','RAW_RELATION_UNIVERSE_UNCHANGED':'raw_equal','Q1_5_273_RELATIONS_PRESERVED':'outcomes_equal','REFERENCE_LAYER_PRESERVED':'references_equal','COMPOSITE_SPANS_PRESERVED':'spans_equal','HUMAN_JUDGMENTS_UNCHANGED':'human_equal','MECHANISM_AUDIT_BEFORE_IMPLEMENTATION':'audit_first',
'SB05_AUDITED':'sb05_audited','SB07_AUDITED':'sb07_audited','SB08_AUDITED':'sb08_audited','SB09_AUDITED':'sb09_audited','NO_DUPLICATE_MECHANISM_ALIAS':'aliases_blocked','EVIDENCE_DEPENDENCY_GRAPH_IMPLEMENTED':'graph_complete','SHARED_RAW_EVIDENCE_NOT_DOUBLE_COUNTED':'shared_once','MECHANISM_ABLATION_IMPLEMENTED':'ablation_complete',
'SB05_NO_SEMANTIC_VALENCY_GUESS':'no_valency_guess','SB07_PAIR_SPECIFIC_TIME_REQUIRED':'time_pair_required','SB08_PAIR_SPECIFIC_LOCATION_REQUIRED':'location_pair_required','SB09_POSITIVE_DOMAIN_CONTINUITY_REQUIRED':'domain_positive','NO_BOUNDARY_ABSENCE_AS_DOMAIN_PROOF':'no_absence_domain','DOMAIN_INDEPENDENT_OF_TESTED_RELATION':'domain_independent','NATIVE_ANNOTATION_NOT_REWRITTEN':'native_equal',
'NO_DISTANCE_RULE':'no_distance','NO_SCORE':'no_score','NO_TOP_N':'no_top_n','RELATION_GRAMMAR_STILL_REQUIRED':'grammar_retained','NEW_RELATIONS_PASS_Q13_COMPATIBILITY':'q13_complete','SB12_CONSTRAINT_ONLY':'sb12_constraint',
'JOB_BLIND_BEFORE_POSTFREEZE_DIAGNOSTICS':'blind_unchanged','NO_JOB_IDS_IN_CORE_LOGIC':'no_job_ids','NO_NUMBERS_IDS_IN_CORE_LOGIC':'no_numbers_ids','NO_BOSMAN_IDS_IN_CORE_LOGIC':'no_bosman_ids','NO_CANONICAL_MOTHER':'no_canonical_mother','NO_CANONICAL_HIERARCHY':'no_canonical_hierarchy','NO_NEW_HUMAN_JUDGMENT':'no_new_human',
'FULL_REGRESSION_PASS':'regression_pass','SKIP_ZERO':'skip_zero','DETERMINISTIC_RERUN':'independent_equal','MANIFEST_VALID':'manifest_valid','ZIP_CRC_VALID':'zip_crc_valid'}


def gates(e,pending=()):
    result=[]
    for name,field in GATE_FIELDS.items():
        if field not in e:raise ValueError('missing gate evidence '+field)
        valid=e[field] is True
        result.append(dict(gate=name,passed=valid,status='PASS' if valid else 'PENDING' if name in pending else 'FAIL',evidence_field=field))
    failures=[r['gate'] for r in result if r['status']=='FAIL']
    if failures:raise ValueError('Q1.6 gate failures '+str(failures))
    return result
