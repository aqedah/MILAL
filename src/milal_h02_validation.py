"""Data-derived H0.2 gates; mutations alter the measured records, never gate flags."""
from copy import deepcopy
from milal_h02_overlay import ACCEPT, REJECT, rationale_valid, bind_registry, build, FILES
from milal_mfr02r_data import encode


def derived_matches(e):
    expected = build(e['original_outcomes'],e['packets'],e['pivots'],e['authority'],e['original_historical'])
    def cells(records):
        return [{k:encode(v) if isinstance(v,(dict,list,tuple,bool)) or v is None else str(v)
                 for k,v in row.items()} for row in records]
    return all(cells(e['state'][k]) == cells(expected[k]) for k in FILES)


def exact_links(e):
    try:
        bind_registry(e['original_outcomes'], e['packets'], e['pivots'], e['state']['dispositions'])
        return True
    except (KeyError, ValueError, TypeError):
        return False


def evaluate(e):
    s, expected, authority = e['state'], e['expected'], e['authority']
    a, r = s['accepted'], s['rejected']
    aa = [x for x in authority if x['human_decision'] == ACCEPT]
    rr = [x for x in authority if x['human_decision'] == REJECT]
    qualified = {x['structural_outcome_group_id'] for x in s['outcomes']}
    accepted_ids = {x['candidate_relation_id'] for x in a}
    historical = e['original_historical']
    tests = e['regression']
    return {
        'BASELINE_COMMIT_VERIFIED': bool(e['baseline']) and len(e['start_heads']) == 3 and set(e['start_heads']) == {e['baseline']},
        'H0_1_FROZEN': not e['frozen_differences'] and bool(e['input_before']) and e['input_before'] == e['input_after'] == e['copied_input'],
        'RAW_UNIVERSE_UNCHANGED': e['raw_count'] == expected['raw'] and bool(e['raw_expected_hash']) and e['raw_expected_hash'] == e['raw_before'] == e['raw_after'],
        'QUALIFIED_273_PRESERVED': s['outcomes'] == e['original_outcomes'] and len(s['outcomes']) == len(qualified) == expected['qualified'],
        'H0_1_REVIEW_PACKET_UNCHANGED': e['packet_before'] == e['packet_after'] == e['packet_copy'] and bool(e['packet_before']),
        'ONE_HUMAN_DECISION_PACKET_ADDED': len(s['decisions']) == 1 and len({x['judgment_id'] for x in s['dispositions']}) == 1 and int(s['review'][0]['new_human_decision_packets']) == 1 and int(s['review'][0]['combined_registry_decision_entries']) == len(historical)+1,
        'TWO_CANDIDATE_DISPOSITIONS_RECORDED': len(s['dispositions']) == len({x['candidate_relation_id'] for x in s['dispositions']}) == expected['dispositions'],
        '500062_DIRECT_MOTHER_REJECTED': len(r) == 1 and r[0]['source_clause_id'] == rr[0]['source_clause_id'] and r[0]['human_decision'] == REJECT and r[0]['direct_mother_status'] == 'REJECTED',
        '500062_MACHINE_CANDIDATE_PRESERVED': len(r) == 1 and r[0]['candidate_relation_id'] in qualified and r[0]['historical_candidate_preserved'] is True and r[0]['candidate_relation_id'] not in accepted_ids,
        '500062_NOT_GLOBAL_NO_RELATION': len(r) == 1 and r[0]['no_relation_all_layers'] is False and r[0]['human_relation_type'] == 'NO_DIRECT_STRICT_MOTHER_RELATION',
        '500064_LOCAL_MOTHER_ACCEPTED': len(a) == 1 and a[0]['source_clause_id'] == aa[0]['source_clause_id'] and a[0]['human_decision'] == ACCEPT and a[0]['direct_mother_status'] == 'ACCEPTED',
        '500064_HYPOTACTIC_ACCEPTED_LOCALLY': len(a) == 1 and a[0]['human_relation_type'] == 'HYPOTACTIC' and a[0]['human_structural_effect'] == 'STRICTLY_BELOW' and a[0]['canonical_whole_book_status'] == 'NOT_CANONICAL',
        'MACHINE_RULE_PROVENANCE_PRESERVED': exact_links(e) and all(x['machine_rule_provenance'] == 'PRESERVED' for x in s['dispositions']),
        'HUMAN_RATIONALE_SEPARATE_FROM_MACHINE_RULE': len(a) == 1 and rationale_valid(a[0]) and a[0]['human_edge_decision'] == 'ACCEPTED',
        'KI_FUNCTION_CAUTION_RECORDED': all(x['ki_function_caution'] == 'KI_FUNCTION_CAUTION' and x['ki_universal_semantics'] == 'NOT_ASSIGNED' for x in s['dispositions']) and 'KI_FUNCTION_CAUTION' in e['caution_report'],
        'LEXICAL_SEMANTICS_NOT_FORCED': len(a) == 1 and all(x['lexical_semantics_status'] == 'UNRESOLVED_FOR_HIERARCHY_PURPOSES' for x in s['dispositions']),
        'NO_NEW_RELATION_QUALIFICATION': not s['new_relations'] and qualified == {x['structural_outcome_group_id'] for x in e['original_outcomes']},
        'NO_PROXIMITY_HEURISTIC': len(a) == 1 and rationale_valid(a[0]) and 'proximity alone would be insufficient' in e['method_report'],
        'NO_OTHER_RELATION_AUTO_ACCEPTED': accepted_ids == {x['candidate_relation_id'] for x in aa} and {x['relation_id'] for x in s['status'] if x['human_accepted_by_h02']} == accepted_ids and all(x['h02_human_status'] == 'NOT_ADJUDICATED_BY_H02' for x in s['status'] if x['relation_id'] not in {d['candidate_relation_id'] for d in authority}),
        'NO_CANONICAL_WHOLE_BOOK_HIERARCHY': not s['canonical_hierarchy'] and all(x['canonical_accepted'] is False for x in s['status']) and all(x['canonical_whole_book_status'] == 'NOT_CANONICAL' for x in s['dispositions']),
        'NO_HISTORICAL_HUMAN_JUDGMENT_REWRITE': s['historical'] == historical and len(historical) == expected['historical_human'] and e['human_expected_hash'] == e['human_before'] == e['human_after'] == e['human_copy'],
        'REMAINING_TRUE_PIVOTS_ZERO_AFTER_OVERLAY': len(s['overlay']) == len(e['pivots']) == expected['pivots'] and {str(x['target']) for x in s['overlay']} == {str(x['target']) for x in e['pivots']} and all(x['pivot_status_after_human_adjudication'] == 'RESOLVED_BY_HUMAN' and x['selected_local_mother'] == aa[0]['source_clause_id'] and x['rejected_direct_mother'] == rr[0]['source_clause_id'] for x in s['overlay']) and int(s['review'][0]['remaining_unadjudicated_true_pivots']) == 0,
        'FULL_REGRESSION_PASS': tests.get('test_scope') == 'FULL_REGRESSION' and tests.get('tests_run',0) > 0 and tests.get('failures') == tests.get('errors') == 0 and tests.get('code_fingerprint') == e['fingerprint'],
        'SKIP_ZERO': tests.get('test_scope') == 'FULL_REGRESSION' and tests.get('skipped') == 0,
        'DETERMINISTIC_RERUN': e['independent_equal'] is True,
        'MANIFEST_VALID': e['manifest_valid'] is True,
        'ZIP_CRC_VALID': e['crc_valid'] is True,
        'EXACT_AUTHORITY_TRANSCRIPTION': s['dispositions'] == authority and e['authority_hashes'] == e['current_authority_hashes'] and bool(e['authority_hashes']),
        'EXACT_PACKET_LINKAGE': exact_links(e) and s['decisions'][0]['review_packet_id'] == authority[0]['review_packet_id'],
        'COMPLETE_MACHINE_STATUS_OVERLAY': len(s['status']) == len(qualified) and {x['relation_id'] for x in s['status']} == qualified and all(x['machine_status'] == 'MACHINE_QUALIFIED' for x in s['status']),
        'LOSSLESS_MACHINE_PROVENANCE': s['machine_provenance'] == bind_registry(e['original_outcomes'],e['packets'],e['pivots'],authority),
        'DERIVED_OVERLAY_MATCHES_AUTHORITY': derived_matches(e),
    }


def gates(e, pending=()):
    values = evaluate(e)
    rows = [dict(gate=k, status='PENDING' if k in pending else ('PASS' if v else 'FAIL')) for k,v in values.items()]
    failed = [x['gate'] for x in rows if x['status'] == 'FAIL']
    if failed:
        raise ValueError('H0.2 failed gates: '+repr(failed))
    return rows


MUTATIONS = {
    'BASELINE_COMMIT_VERIFIED':lambda e:e['start_heads'].append('wrong'),
    'H0_1_FROZEN':lambda e:e['copied_input'].update(changed='hash'),
    'RAW_UNIVERSE_UNCHANGED':lambda e:e.update(raw_after='changed'),
    'QUALIFIED_273_PRESERVED':lambda e:e['state']['outcomes'].pop(),
    'H0_1_REVIEW_PACKET_UNCHANGED':lambda e:e.update(packet_copy='changed'),
    'ONE_HUMAN_DECISION_PACKET_ADDED':lambda e:e['state']['decisions'].append(deepcopy(e['state']['decisions'][0])),
    'TWO_CANDIDATE_DISPOSITIONS_RECORDED':lambda e:e['state']['dispositions'].pop(),
    '500062_DIRECT_MOTHER_REJECTED':lambda e:e['state']['rejected'][0].update(direct_mother_status='ACCEPTED'),
    '500062_MACHINE_CANDIDATE_PRESERVED':lambda e:e['state']['rejected'][0].update(historical_candidate_preserved=False),
    '500062_NOT_GLOBAL_NO_RELATION':lambda e:e['state']['rejected'][0].update(no_relation_all_layers=True),
    '500064_LOCAL_MOTHER_ACCEPTED':lambda e:e['state']['accepted'][0].update(direct_mother_status='REJECTED'),
    '500064_HYPOTACTIC_ACCEPTED_LOCALLY':lambda e:e['state']['accepted'][0].update(human_relation_type='PARATACTIC'),
    'MACHINE_RULE_PROVENANCE_PRESERVED':lambda e:e['state']['dispositions'][0].update(machine_rule='INVENTED'),
    'HUMAN_RATIONALE_SEPARATE_FROM_MACHINE_RULE':lambda e:e['state']['accepted'][0].update(machine_rule_rationale_adopted=True),
    'KI_FUNCTION_CAUTION_RECORDED':lambda e:e['state']['dispositions'][0].update(ki_universal_semantics='UNIVERSAL_SUBORDINATOR'),
    'LEXICAL_SEMANTICS_NOT_FORCED':lambda e:e['state']['dispositions'][1].update(lexical_semantics_status='RESOLVED_TRANSLATION'),
    'NO_NEW_RELATION_QUALIFICATION':lambda e:e['state']['new_relations'].append('POETIC_EDGE'),
    'NO_PROXIMITY_HEURISTIC':lambda e:e['state']['accepted'][0].update(rationale_observations=['NEAREST']),
    'NO_OTHER_RELATION_AUTO_ACCEPTED':lambda e:e['state']['status'][-1].update(human_accepted_by_h02=True),
    'NO_CANONICAL_WHOLE_BOOK_HIERARCHY':lambda e:e['state']['canonical_hierarchy'].append('ROOT'),
    'NO_HISTORICAL_HUMAN_JUDGMENT_REWRITE':lambda e:e['state']['historical'].pop(),
    'REMAINING_TRUE_PIVOTS_ZERO_AFTER_OVERLAY':lambda e:e['state']['overlay'][0].update(selected_local_mother='WRONG'),
    'FULL_REGRESSION_PASS':lambda e:e['regression'].update(errors=1),
    'SKIP_ZERO':lambda e:e['regression'].update(skipped=1),
    'DETERMINISTIC_RERUN':lambda e:e.update(independent_equal=False),
    'MANIFEST_VALID':lambda e:e.update(manifest_valid=False),
    'ZIP_CRC_VALID':lambda e:e.update(crc_valid=False),
    'EXACT_AUTHORITY_TRANSCRIPTION':lambda e:e['state']['dispositions'][0].update(adjudication_date='INVENTED'),
    'EXACT_PACKET_LINKAGE':lambda e:e['state']['decisions'][0].update(review_packet_id='FUZZY'),
    'COMPLETE_MACHINE_STATUS_OVERLAY':lambda e:e['state']['status'].pop(),
    'LOSSLESS_MACHINE_PROVENANCE':lambda e:e['state']['machine_provenance'].pop(),
    'DERIVED_OVERLAY_MATCHES_AUTHORITY':lambda e:e['state']['accepted'][0].update(human_rationale_text='UNAUTHORIZED_REWRITE'),
}
