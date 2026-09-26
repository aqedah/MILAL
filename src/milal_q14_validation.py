"""Computed Q1.4 gates. No empirical expected discovery count is encoded."""
import ast

GATES='''BASELINE_COMMIT_VERIFIED Q1_3_FROZEN RAW_UNIVERSE_UNCHANGED Q1_3_195_RELATIONS_PRESERVED
HUMAN_JUDGMENTS_UNCHANGED NO_CANONICAL_MOTHER NO_CANONICAL_HIERARCHY COMPOSITE_SURFACE_SPAN_IMPLEMENTED
SPAN_BOUNDARY_INDEPENDENT_OF_TESTED_RELATION OVERLAPPING_SPANS_ALLOWED NO_FIXED_LINGUISTIC_SPAN_WINDOW
COMPOSITE_PROFILE_IMPLEMENTED DATA_DERIVED_COMPOSITE_FAMILIES CROSS_FAMILY_CORRESPONDENCE_IMPLEMENTED
CROSS_FAMILY_NOT_FAMILY_MERGE POSITION_MAPPING_IMPLEMENTED PAIR_SPECIFIC_COMPOSITE_BINDING_REQUIRED
BARE_SPEECH_FORMULA_NOT_SUFFICIENT NO_PNG_ONLY_IDENTITY COMPOSITE_BINDING_DOES_NOT_INVENT_RELATION_TYPE
EXISTING_RELATION_GRAMMAR_REQUIRED NEW_RELATIONS_PASS_Q13_COMPATIBILITY UNIT_MEMBERSHIP_OBSERVATIONAL_ONLY
NO_HIERARCHY_LEAKAGE JOB_BLIND_BEFORE_POSTFREEZE_DIAGNOSTICS NO_JOB_CONTROL_IDS_IN_CORE_LOGIC
NO_NUMBERS_CONTROL_IDS_IN_CORE_LOGIC NO_NUMERIC_SIMILARITY_SCORE NO_NEW_HUMAN_JUDGMENT
FULL_REGRESSION_PASS SKIP_ZERO DETERMINISTIC_RERUN MANIFEST_VALID ZIP_CRC_VALID'''.split()


def policy(text):
    tree=ast.parse(text);imports=[];strings=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.ImportFrom):imports.append(n.module or '')
        if isinstance(n,ast.Constant) and isinstance(n.value,str):strings.append(n.value)
    return dict(no_hierarchy=not any(any(bad in m for bad in ('q13_model','q12_pipeline','human','hsa','r4_')) for m in imports) and
        not any(s in ('accepted_mother','accepted_parent','final_textual_unit','final_hierarchy_level') for s in strings),
        no_controls=not any(bad in text for bad in ('499251','499383','443836','443840','JOB_27','JOB_29','TAKE_MASHAL_FAMILY','ELIHU_FAMILY','YHWH_RESPONSE_FAMILY')),
        no_score=not any(bad in text.lower() for bad in ('jaccard','cosine','similarity_score','weighted_score','top_n','distance_cutoff')),
        no_span_limit=not any(bad in text.lower() for bad in ('max_span','lookahead_limit','span_window')))


def measurements(e):
    s=e['semantic'];p=e['policy'];t=e['tests']
    values=[e['baseline']==e['expected_baseline'] and e['baseline_verified'],
        e['inputs_verified'] and not e['frozen_differences'],e['raw_count']==e['expected_raw'] and not e['raw_errors'],
        e['retained']==e['expected_baseline_relations'] and e['baseline_outcomes_unchanged'],e['human_equal'],
        not e['canonical_mothers'],not e['canonical_hierarchies'],s['S1'] and not e['invalid_spans'],
        s['S4'] and not e['dependent_positive'],s['S11'],p['no_span_limit'] and e['traversal_has_no_fixed_upper_bound'],
        e['profile_coverage'] and s['S1'],e['family_derived'] and p['no_controls'],s['S5'],not e['families_merged'] and s['S5'],
        not e['unresolved_positive_mapping'] and s['S2'],not e['unanchored_positive'] and s['S2'],
        s['S3'] and e['bare_formula_positive']==0,s['S8'] and e['reference_unchanged'],s['S6'] and not e['invented_relation_types'],
        not e['grammar_errors'] and s['S6'],e['q13_complete'] and s['S9'] and s['S10'],e['membership_observational'],
        p['no_hierarchy'] and s['S4'] and s['S12'],e['blind_unchanged'] and e['events']==['BLIND_FROZEN','POSTFREEZE_CONTROLS_COMPLETED'],
        p['no_controls'],p['no_controls'] and e['external_fixture_only'],p['no_score'],not e['new_human_judgments'],
        t['test_scope']=='FULL_REGRESSION' and t['tests_run']>0 and t['errors']==t['failures']==0 and e['fingerprint_matches'],
        t['skipped']==0,e['independent_equal'],e['manifest_valid'],e['zip_crc_valid']]
    assert len(values)==len(GATES)
    return dict(zip(GATES,map(bool,values)))


def assert_gates(e,pending=()):
    m=measurements(e);failed=[k for k,v in m.items() if not v and k not in pending]
    if failed:raise ValueError('Q1.4 gates failed: '+repr(failed))
    return [dict(gate=k,status='PASSED' if v else 'PENDING_VALIDATION') for k,v in m.items()]
