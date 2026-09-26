"""Computed Q1.5 gates with independently mutable evidence inputs."""
import ast

GATES='''BASELINE_COMMIT_VERIFIED Q1_4_FROZEN RAW_RELATION_UNIVERSE_UNCHANGED Q1_4_243_RELATIONS_PRESERVED
Q1_4_SURFACE_SPANS_PRESERVED HUMAN_JUDGMENTS_UNCHANGED REFERENCE_MENTION_TYPES_SEPARATED LEXICAL_NP_NOT_AUTOMATIC_REFERENCE
REFERENCE_VISIBILITY_DOMAIN_IMPLEMENTED DOMAINS_INDEPENDENT_OF_TESTED_RELATION OVERLAPPING_DOMAINS_ALLOWED
GLOBAL_SEARCH_CANDIDATES_PRESERVED ACTIVE_CANDIDATE_SET_SEPARATE NO_DISTANCE_CUTOFF NO_NEAREST_ANTECEDENT_RULE
NO_TOP_N_REFERENCE_RULE NO_REFERENCE_SCORE PNG_ONLY_NOT_IDENTITY UNIQUE_VISIBLE_NOT_AUTOMATIC_CONFIRMED_IDENTITY
SB02_OPERATIONAL SB03_OPERATIONAL SB10_OPERATIONAL_OR_EXPLICITLY_EVIDENCE_ONLY BOSMAN_INTERNAL_ANTECEDENT_REPRESENTABLE
LEXICAL_RECURRENCE_ONLY_NOT_SB10 REFERENCE_BINDING_DOES_NOT_INVENT_RELATION_TYPE NEW_RELATIONS_PASS_Q13_COMPATIBILITY
NO_CANONICAL_COREFERENCE_GRAPH NO_CANONICAL_MOTHER NO_CANONICAL_HIERARCHY JOB_BLIND_BEFORE_EXTERNAL_CONTROLS
NO_JOB_DIAGNOSTIC_IDS_IN_CORE_LOGIC NO_BOSMAN_CONTROL_IDS_IN_CORE_LOGIC NO_NUMBERS_CONTROL_IDS_IN_CORE_LOGIC
FULL_REGRESSION_PASS SKIP_ZERO DETERMINISTIC_RERUN MANIFEST_VALID ZIP_CRC_VALID'''.split()


def policy(source):
    ast.parse(source)
    return dict(distance=not any(k in source for k in ('lookback','distance_cutoff','verse_distance','chapter_distance')),
        nearest=not any(k in source for k in ('nearest_antecedent','min_distance')),top=not any(k in source for k in ('top_n','top_candidates')),
        score=not any(k in source for k in ('similarity_score','weighted_score','jaccard','cosine')),
        controls=not any(k in source for k in ('497626','499626','504907','504910','443836','443840')),
        hierarchy=not any(k in source for k in ('accepted_parent','canonical_mother','final_textual_level','final_speech_unit','milal_q13_model','milal_hsa')))


def measurements(e):
    s=e['semantic'];p=e['policy'];t=e['tests']
    vals=[e['baseline']==e['expected_baseline'] and e['baseline_verified'],e['inputs_verified'] and not e['frozen_differences'],
        e['raw']==e['expected_raw'] and not e['grammar_errors'],e['retained']==e['expected_relations'] and e['old_outcomes_equal'],
        e['spans_equal'],e['human_equal'],e['form_types_correct'],not e['lexical_positive'],e['domains_valid'] and s['S1'],
        not e['circular_domains'] and not e['circular_bindings'] and s['S5'],e['overlap_supported'],e['global_equal'],e['candidate_sets_separate'] and s['S7'],
        p['distance'],p['nearest'] and s['S6'],p['top'],p['score'],not e['png_confirmed'] and s['S11'],not e['unique_confirmed'] and s['S1'],
        s['S8'] and e['sb02_present'],s['S4'] and e['sb03_present'],e['sb10_evidence_only'] and s['S3'],s['S12'],
        not e['sb10_lexical_positive'] and s['S9'],not e['grammar_errors'] and e['relation_types_valid'],e['q13_complete'] and s['S10'],
        not e['canonical_coreference'],not e['canonical_mothers'],not e['canonical_hierarchies'],e['blind_unchanged'] and e['controls_after_freeze'],
        p['controls'],p['controls'] and e['bosman_fixture_only'],p['controls'] and e['numbers_fixture_only'],
        t['test_scope']=='FULL_REGRESSION' and t['tests_run']>0 and t['failures']==t['errors']==0 and e['fingerprint_matches'],
        t['skipped']==0,e['independent_equal'],e['manifest_valid'],e['zip_crc_valid']
    ]
    assert len(vals)==len(GATES)
    return dict(zip(GATES,map(bool,vals)))


def assert_gates(e,pending=()):
    checks=measurements(e);bad=[k for k,v in checks.items() if not v and k not in pending]
    if bad:raise ValueError('Q1.5 gates failed: '+repr(bad))
    return [dict(gate=k,status='PASSED' if v else 'PENDING_VALIDATION') for k,v in checks.items()]
