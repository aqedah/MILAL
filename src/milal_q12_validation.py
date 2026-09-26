"""Computed Q1.2 release gates with independently mutable evidence."""
from milal_q11_validation import code_policy

GATES='''BASELINE_COMMIT_VERIFIED Q1_FROZEN Q1_1_FROZEN RAW_UNIVERSE_UNCHANGED
HUMAN_JUDGMENTS_UNCHANGED NO_CANONICAL_MOTHER NO_CANONICAL_HIERARCHY
SURFACE_CONFIGURATION_PROFILE_IMPLEMENTED CONFIGURATION_INDEPENDENT_OF_TESTED_EDGE
NO_UNIVERSAL_IDENTICAL_FULL_SIGNATURE_REQUIREMENT NO_GENERIC_SIMILARITY_QUALIFICATION
NO_NUMERIC_SIMILARITY_SCORE NO_FEATURE_COUNT_THRESHOLD SB06_COMPOSITIONAL SB11_OPERATIONAL
REFERENCE_WITNESS_LAYER_CREATED NO_PNG_ONLY_COREFERENCE NO_LEXEME_ONLY_COREFERENCE
BOSMAN_UNIT_REFERENCE_NONCIRCULAR SB12_CONSTRAINT_ONLY SB12_NOT_POSITIVE_BINDING
SAME_FAMILY_NOT_EQUAL_SAME_LEVEL JOB_BLIND_BEFORE_EXTERNAL_CONTROLS
CONTROL_FIXTURE_IDS_ABSENT_FROM_CORE_LOGIC FULL_PENTATEUCH_ANALYSIS_ABSENT
NO_NEW_HUMAN_JUDGMENT FULL_REGRESSION_PASS SKIP_ZERO DETERMINISTIC_RERUN MANIFEST_VALID
PRIMARY_ANALYSIS_SCOPE_JOB_ONLY PENTATEUCH_CONTROLS_FIXTURE_ONLY
CORPUS_SEARCH_NOT_CONFUSED_WITH_ANALYSIS_SCOPE OOSTING_CLAUSE_BINDING_PRIOR_PRESERVED'''.split()


def policy(text):
    p=code_policy(text)
    p['no_feature_threshold']=not any(n in text for n in ('similarity_threshold','minimum_matching_features','feature_count_threshold'))
    return p


def measurements(e):
    s=e['semantic'];p=e['policy'];t=e['tests']
    values=[
        e['baseline']==e['expected_baseline'] and not e['frozen_differences'],
        e['q1_verified'] and not e['frozen_differences'],e['q11_verified'] and not e['frozen_differences'],
        e['raw_count']==e['expected_raw_count'] and e['raw_errors']==0 and e['source_verified'],
        e['human_equal'] and e['human_count']==e['expected_human_count'],
        not e['canonical_mothers'],not e['canonical_hierarchies'],
        e['profile_count']==e['source_clause_count'] and e['profile_count']>0 and s['profile_fields'],
        e['dependent_positives']==0 and s['N5'],s['N8'] and s['S1'] and s['S2'],
        e['unanchored_positives']==0 and all(s[k] for k in ('N1','N2','N4','S6')),
        p['no_score'],p['no_feature_threshold'],s['S1'] and s['N1'] and e['invalid_positive_composition']==0,
        s['SB11'] and s['N4'],e['reference_count']>0 and s['S3'],
        e['png_only_resolved']==0 and s['N3'],e['lexeme_only_resolved']==0 and s['N2'],
        e['circular_reference_bindings']==0 and s['S4'],e['sb12_input_ids']==e['sb12_output_ids'] and s['S5'],
        not e['sb12_positive'] and s['N6'],e['family_assigned_levels']==0 and s['N9'],
        e['events']==['BLIND_STARTED','BLIND_FROZEN','CONTROLS_STARTED','CONTROLS_FINISHED'] and e['blind_files_equal'],
        p['no_id_exception'] and p['no_book_rule'] and p['no_known_positive'] and s['N7'],
        e['full_external_analyses']==0 and e['generated_external_candidates']==0,
        not e['new_judgments'],t['test_scope']=='FULL_REGRESSION' and t['tests_run']>0 and
            t['failures']==t['errors']==0 and e['fingerprint_matches'],t['skipped']==0,
        e['independent_equal'],e['manifest_valid'],e['analysis_books']==['Iob'],
        e['fixture_identities_equal'] and e['generated_external_candidates']==0,
        e['analysis_scope']=='JOB' and e['corpus_comparison_scope']=='HB_CORPUS',e['deferred_qualified']==0]
    if len(values)!=len(GATES):raise ValueError('gate schema mismatch')
    return [dict(gate=g,passed=bool(v)) for g,v in zip(GATES,values)]


def assert_gates(e,pending=()):
    result=measurements(e);failed=[r['gate'] for r in result if not r['passed'] and r['gate'] not in pending]
    if failed:raise ValueError('Q1.2 gates failed: '+repr(failed))
    return result
