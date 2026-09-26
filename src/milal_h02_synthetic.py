"""Small synthetic source identities; human authority is an explicit fixture, not inferred."""
from copy import deepcopy
import json
from pathlib import Path
from milal_mfr02r_data import rows, encode
from milal_mfr02r_pipeline import code_fingerprint
from milal_h02_overlay import build, reports, write_outputs
from milal_h02_validation import evaluate, MUTATIONS

ROOT = Path(__file__).resolve().parents[1]


def fixture():
    # Reuse the authored fields as a human-judgment fixture; all machine records below
    # are synthetic and never substituted for the verified H0.1 empirical packet.
    registry = list(rows(ROOT/'docs/HUMAN_STRUCTURAL_ADJUDICATION_MFR_H02.csv'))
    outcomes, alternatives = [], []
    for r in registry:
        oid = r['candidate_relation_id']
        outcomes.append(dict(structural_outcome_group_id=oid,target=r['target_clause_id'],
                             source_or_peer=r['source_clause_id'],relation_type='HYPOTACTIC'))
        q = dict(relation_id=oid,grammar_rules=[dict(rule_id=r['machine_rule'])],
                 primary_source_binding=r['machine_binding'],
                 source=dict(clause_id=r['source_clause_id']),
                 target=dict(clause_id=r['target_clause_id'],clause_atom_ids=r['target_atom_ids']))
        alternatives.append(dict(assignment_id=r['alternative_id'],assignment=dict(selected_relation_ids=[oid]),relations=[q]))
    for i in range(271):
        outcomes.append(dict(structural_outcome_group_id=f'SYNTHETIC-{i}',target=f'T{i}',
                             source_or_peer=f'S{i}',relation_type='HYPOTACTIC' if i < 201 else 'PARATACTIC'))
    packets = [dict(review_item_id=registry[0]['review_packet_id'],alternatives=alternatives)]
    pivots = [dict(target=registry[0]['target_clause_id'],target_status='TRUE_DECISION_PIVOT')]
    historical = [dict(original_decision=dict(id=f'SYNTHETIC-H{i}'),new_human_judgment=False) for i in range(13)]
    state = build(outcomes,packets,pivots,registry,historical)
    text = reports(state)
    e = dict(state=state,original_outcomes=deepcopy(outcomes),original_historical=deepcopy(historical),
             packets=packets,pivots=pivots,authority=registry,expected=dict(raw=1049504,qualified=273,historical_human=13,dispositions=2,pivots=1),
             baseline='SYNTHETIC',start_heads=['SYNTHETIC']*3,frozen_differences=[],input_before={'file':'hash'},
             input_after={'file':'hash'},copied_input={'file':'hash'},raw_count=1049504,
             raw_expected_hash='synthetic-raw',raw_before='synthetic-raw',raw_after='synthetic-raw',
             packet_before='synthetic-packet',packet_after='synthetic-packet',packet_copy='synthetic-packet',
             human_expected_hash='synthetic-human',human_before='synthetic-human',human_after='synthetic-human',human_copy='synthetic-human',
             regression=dict(test_scope='FULL_REGRESSION',tests_run=1,failures=0,errors=0,skipped=0,code_fingerprint='SYNTHETIC'),
             fingerprint='SYNTHETIC',independent_equal=True,manifest_valid=True,crc_valid=True,
             authority_hashes={'authority':'synthetic'},current_authority_hashes={'authority':'synthetic'},
             caution_report=text['08_h02_ki_function_caution.md'],method_report=text['10_h02_method_report.md'])
    return e


CASE_GATES = {
    'H02-S1':['500062_MACHINE_CANDIDATE_PRESERVED','500062_DIRECT_MOTHER_REJECTED'],
    'H02-S2':['500064_LOCAL_MOTHER_ACCEPTED'], 'H02-S3':['500062_NOT_GLOBAL_NO_RELATION'],
    'H02-S4':['MACHINE_RULE_PROVENANCE_PRESERVED','HUMAN_RATIONALE_SEPARATE_FROM_MACHINE_RULE'],
    'H02-S5':['LEXICAL_SEMANTICS_NOT_FORCED'], 'H02-S6':['QUALIFIED_273_PRESERVED'],
    'H02-S7':['ONE_HUMAN_DECISION_PACKET_ADDED','TWO_CANDIDATE_DISPOSITIONS_RECORDED'],
    'H02-S8':['REMAINING_TRUE_PIVOTS_ZERO_AFTER_OVERLAY'],
    'H02-S9':['NO_OTHER_RELATION_AUTO_ACCEPTED'], 'H02-S10':['NO_CANONICAL_WHOLE_BOOK_HIERARCHY'],
    'H02-S11':['NO_NEW_RELATION_QUALIFICATION'], 'H02-S12':['NO_PROXIMITY_HEURISTIC'],
}


def self_test(destination):
    e = fixture(); values = evaluate(e)
    negatives = {}
    for name, mutate in MUTATIONS.items():
        bad = deepcopy(e); mutate(bad); negatives[name] = not evaluate(bad)[name]
    checks = {case:all(values[g] and negatives[g] for g in names) for case,names in CASE_GATES.items()}
    result = dict(mode='SYNTHETIC',cases=checks,negative_mutations=negatives,
                  passed=all(checks.values()) and all(negatives.values()) and all(values.values()),
                  code_fingerprint=code_fingerprint())
    if not result['passed']:
        raise ValueError(encode(result))
    p = Path(destination);p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(encode(result)+'\n',encoding='utf8',newline='\n')
    p.with_suffix('.md').write_text('# SYNTHETIC ONLY\n\n'+reports(e['state'])['07_h02_job_37_20_adjudication.md'],encoding='utf8',newline='\n')
    return result
