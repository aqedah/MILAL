"""Recompute Q1 invariants from source records and produced tables."""
from collections import Counter, defaultdict
from itertools import zip_longest
from pathlib import Path
import json

from milal_mfr02r_data import rows, digest, physical_path, verify_manifest
from milal_q1_binding import SourceIndex, qualify, outcome, identity, QUALIFIED, STATUSES, pivot, rule_roles

GATES = '''BASELINE_COMMIT_VERIFIED MFR_0_2R_FROZEN MFR_0_2R_H0_FROZEN
RAW_CANDIDATE_UNIVERSE_UNCHANGED SEARCH_AND_RELATION_CANDIDATES_SEPARATED SOURCE_BINDING_REQUIRED
TARGET_FEATURE_ALONE_NOT_RELATION W_A01_SOURCE_BOUND W_P01_SAME_TYPE_NOT_RELATION_BY_ITSELF
W_H01_ACTIVE_PARTICIPANT_REQUIRED JIN_RULE_SOURCE_BINDING_AUDITED VALENCY_BEFORE_RELATION_PRESERVED
CORPUS_ANALOGUE_NOT_RELATION_BINDING PROSODY_NOT_HIERARCHY_EDGE_BY_ITSELF
QUALIFIED_RELATION_UNIVERSE_CREATED STRUCTURAL_OUTCOME_GROUPS_CREATED
MULTIPLE_CANDIDATES_NOT_EQUAL_MULTIPLE_OUTCOMES VARIANT_MEMBER_NOT_EQUAL_REVIEW_REQUIRED
VARIANT_DECISION_PIVOT_IMPLEMENTED GIANT_COMPONENT_MEMBERSHIP_NOT_REVIEW_TRIGGER
NO_NUMERIC_SCORE NO_DISTANCE_CUTOFF NO_TOP_N NO_NEW_HUMAN_JUDGMENT NO_CANONICAL_MOTHER
NO_CANONICAL_HIERARCHY MFR02A_13_PRESERVED CONTROL_FIXTURES_ONLY FULL_REGRESSION_PASS SKIP_ZERO
DETERMINISTIC_RERUN MANIFEST_VALID'''.split()


def evaluate(measurements):
    if set(measurements)!=set(GATES): raise ValueError('incomplete gate measurements')
    return [dict(gate=k,passed=m['actual']==m['expected'],evidence=m) for k in GATES for m in [measurements[k]]]


def audit(source,out,grammar,receipts,semantics):
    source,out=Path(source),Path(out); job=source/'blind/job'
    inventory=list(rows(job/'02_clause_feature_inventory.csv'))
    index=SourceIndex(inventory,grammar['lexicons']['subordinate_rela'],grammar['lexicons']['speech'])
    deferred={str(r['binding_evidence']['raw_clause_membership']) for r in rows(job/'clause_internal_binding_candidates.csv')}
    bound=defaultdict(list)
    for r in rows(out/'source_binding_witnesses.csv'):
        w={k:v for k,v in r.items() if k!='candidate_id' and v!=''}
        bound[r['candidate_id']].append(w)
    problems=Counter(); expected_universe={}; expected_outcomes={}; expected_audits={}; raw_count=0
    expected_paths=defaultdict(list)
    sha=digest(physical_path(job/'09_candidate_evidence_matrix.csv'))
    streams=[rows(job/'09_candidate_evidence_matrix.csv'),rows(job/'08_relation_rule_matches.csv'),
             rows(out/'03_q1_pair_qualification.csv'),rows(out/'02_q1_source_binding_crosswalk.csv')]
    for raw,match,q,cross in zip_longest(*streams):
        raw_count+=1
        if any(x is None for x in (raw,match,q,cross)):
            problems['raw']+=1;continue
        pair=raw['pair_id'];sid=str(raw['candidate_clause_id']);tid=str(raw['target_clause_id'])
        if any(x!=pair for x in (match['pair_id'],q['candidate_id'],cross['candidate_id'])):problems['raw']+=1
        if cross['raw_row_sha256']!=identity(raw) or cross['raw_table_sha256']!=sha:problems['raw']+=1
        if (cross['source_id'],cross['target_id'])!=(sid,tid) or (q['source_id'],q['target_id'])!=(sid,tid):problems['raw']+=1
        ws=index.bindings(sid,tid) if match['matches'] else []
        if identity(bound[pair])!=identity(ws):problems['binding']+=1
        if cross['witnesses']!=[w['witness_id'] for w in ws]:problems['binding']+=1
        expected=qualify(sid,tid,match['matches'],ws,deferred=tid in deferred)
        if q['relation_candidate_qualification']!=expected['qualification'] or any(q[k]!=expected[k] for k in ('qualified_paths','qualified_relations','qualification_reason','disqualification_reason')):problems['binding']+=1
        if q['relation_candidate_qualification'] not in STATUSES or q['search_candidate_status']!='SEARCH_CANDIDATE':problems['separation']+=1
        if q['relation_candidate_qualification'] in QUALIFIED:expected_universe[pair]=q
        for rel in expected['qualified_relations']:
            o=outcome(sid,tid,rel);oid=o['structural_outcome_group_id'];expected_outcomes[oid]=o
            expected_paths[oid].extend(dict(candidate_id=pair,**p) for p in expected['qualified_paths'] if p['relation']==rel)
        for m in match['matches']:
            paths=[p for p in expected['qualified_paths'] if p['rule_id']==m['rule_id']]
            expected_audits[pair,m['rule_id']]=dict(original=m,bound='YES' if paths else 'NO',witnesses=sorted({p['witness_id'] for p in paths}))
        if tid in deferred and q['qualified_relations']:problems['valency']+=1
    audits={}
    for name in ('05_q1_walton_rule_audit.csv','06_q1_jin_rule_audit.csv'):
        for r in rows(out/name):
            k=r['candidate_id'],r['rule_id']
            if k in audits:problems['audit']+=1
            audits[k]=dict(original=r['original_match'],bound=r['source_bound'],witnesses=r['qualified_witness_ids'])
    problems['audit']+=audits!=expected_audits
    universe=list(rows(out/'07_q1_qualified_relation_universe.csv'))
    universe_ok=len(universe)==len(expected_universe) and {r['candidate_id']:r for r in universe}==expected_universe
    os=list(rows(out/'09_q1_structural_outcomes.csv'))
    actual_outcomes={r['structural_outcome_group_id']:{k:v for k,v in r.items() if k!='provenance_paths'} for r in os}
    outcomes_ok=actual_outcomes==expected_outcomes and len(os)==len(expected_outcomes)
    outcomes_ok &= all(r['provenance_paths']==expected_paths[r['structural_outcome_group_id']] for r in os)
    groups=list(rows(out/'10_q1_structural_outcome_groups.csv'))
    groups_ok={r['structural_outcome_group_id'] for r in groups}==set(expected_outcomes) and len(groups)==len(expected_outcomes)
    groups_ok &= all(r['provenance_paths']==expected_paths[r['structural_outcome_group_id']] and
        r['candidate_ids']==sorted({p['candidate_id'] for p in expected_paths[r['structural_outcome_group_id']]}) and
        r['rule_ids']==sorted({p['rule_id'] for p in expected_paths[r['structural_outcome_group_id']]}) for r in groups)
    by_target=defaultdict(list)
    for o in expected_outcomes.values():by_target[o['target']].append(o)
    members={str(t) for r in rows(job/'15_variant_components.csv') for t in r['affected_clauses']}
    actual_pivots=list(rows(out/'11_q1_variant_pivots.csv'))
    expected_pivots=[pivot(t,by_target[t],t in members) for t in index.ordered]
    # CSV numeric fields intentionally parse as strings.
    for r in actual_pivots:r['outcome_count']=int(r['outcome_count'])
    pivots_ok=actual_pivots==expected_pivots
    historical=list(rows(source/'mfr02a_original_decisions.csv'))
    history=list(rows(out/'14_q1_mfr02a_13_case_reaudit.csv'))
    history_ok=[r['original_decision'] for r in history]==historical and all(r['original_decision_sha256']==identity(r['original_decision']) for r in history)
    fixtures=list(rows(out/'16_q1_control_fixture_validation.csv'))
    control_receipts=json.loads((out/'control_source_receipts.json').read_text())
    fixtures_ok=bool(fixtures) and {r['scope'] for r in fixtures}=={'pentateuch','qohelet','lamentations','isaiah'} and all(r['full_external_book_analysis'] is False and r['exact_fixture_identity'] is True for r in fixtures)
    fixtures_ok &= all(set(map(str,r['original_clause_ids']))==set(r['selected_clause_ids']) and r['full_external_book_analysis'] is False for r in control_receipts.values())
    freeze=json.loads((out/'blind_freeze.json').read_text())
    frozen_blind=all(digest(out/k)==v for k,v in freeze['files'].items())
    rules=list(rows(job/'01_relation_grammar_registry.csv'))
    roles_ok=list(rows(out/'01_q1_rule_execution_roles.csv'))==list(map(rule_roles,rules))
    tests=receipts['tests']; frozen=receipts['baseline']
    measurements={}
    def m(k,actual,expected=True):measurements[k]=dict(actual=actual,expected=expected)
    m('BASELINE_COMMIT_VERIFIED',frozen['baseline']==receipts['expected_baseline'])
    m('MFR_0_2R_FROZEN',not frozen['differences'] and receipts['source']['manifest_valid'] and receipts['source']['crc_valid'])
    m('MFR_0_2R_H0_FROZEN',not frozen['differences'] and receipts['h0']['manifest_valid'] and receipts['h0']['crc_valid'])
    m('RAW_CANDIDATE_UNIVERSE_UNCHANGED',problems['raw'],0)
    m('SEARCH_AND_RELATION_CANDIDATES_SEPARATED',not problems['separation'] and universe_ok)
    m('SOURCE_BINDING_REQUIRED',problems['binding'],0)
    m('TARGET_FEATURE_ALONE_NOT_RELATION',semantics['target_only_rejected'] and not problems['binding'])
    for gate,key in [('W_A01_SOURCE_BOUND','target_only_rejected'),('W_P01_SAME_TYPE_NOT_RELATION_BY_ITSELF','same_type_only_rejected'),('W_H01_ACTIVE_PARTICIPANT_REQUIRED','inactive_participant_rejected')]:
        m(gate,semantics[key] and not problems['audit'] and not problems['binding'])
    m('JIN_RULE_SOURCE_BINDING_AUDITED',roles_ok and not problems['audit'])
    m('VALENCY_BEFORE_RELATION_PRESERVED',problems['valency'],0)
    m('CORPUS_ANALOGUE_NOT_RELATION_BINDING',semantics['corpus_only_rejected'] and not problems['binding'])
    m('PROSODY_NOT_HIERARCHY_EDGE_BY_ITSELF',semantics['prosody_only_rejected'] and not problems['binding'])
    m('QUALIFIED_RELATION_UNIVERSE_CREATED',universe_ok)
    m('STRUCTURAL_OUTCOME_GROUPS_CREATED',outcomes_ok and groups_ok)
    m('MULTIPLE_CANDIDATES_NOT_EQUAL_MULTIPLE_OUTCOMES',semantics['many_rules_one_outcome'] and groups_ok)
    m('VARIANT_MEMBER_NOT_EQUAL_REVIEW_REQUIRED',pivots_ok and semantics['membership_only_nonpivot'])
    m('VARIANT_DECISION_PIVOT_IMPLEMENTED',pivots_ok and semantics['distinct_positive_pivot'])
    m('GIANT_COMPONENT_MEMBERSHIP_NOT_REVIEW_TRIGGER',pivots_ok and semantics['membership_only_nonpivot'])
    for key in ('NO_NUMERIC_SCORE','NO_DISTANCE_CUTOFF','NO_TOP_N'):m(key,semantics[key] and not problems['binding'])
    m('NO_NEW_HUMAN_JUDGMENT',history_ok and all(r['new_human_judgment']=='' for r in history) and frozen_blind and freeze['human_judgments_loaded'] is False)
    m('NO_CANONICAL_MOTHER',all(r['canonical_mother']=='' for r in actual_pivots) and all(r['accepted']=='' for r in rows(out/'12_q1_mother_competition.csv')))
    m('NO_CANONICAL_HIERARCHY',all(r['canonical_hierarchy']=='' for r in actual_pivots))
    m('MFR02A_13_PRESERVED',history_ok and len(history)==13)
    expected_book='Synthetic' if receipts.get('mode')=='SYNTHETIC' else 'Iob'
    m('CONTROL_FIXTURES_ONLY',fixtures_ok and freeze['controls_loaded'] is False and all(r['book']==expected_book for r in inventory))
    m('FULL_REGRESSION_PASS',tests['test_scope']=='FULL_REGRESSION' and tests['tests_run']>=2465 and tests['failures']==tests['errors']==0 and receipts['fingerprint_matches'])
    m('SKIP_ZERO',tests['skipped'],0)
    m('DETERMINISTIC_RERUN',receipts.get('independent_bytes_equal',False))
    m('MANIFEST_VALID',verify_manifest(out))
    return measurements
