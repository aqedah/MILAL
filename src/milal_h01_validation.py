"""Computed H0.1 gates and data mutations; feasibility is rechecked with Q1.3."""
from copy import deepcopy
from milal_h01_model import STATUSES,REVIEW_STATUSES
from milal_h01_evidence import DISPLAY_ROLES,REVIEW_FIELDS
from milal_q13_model import AssignmentModel


def valid_proofs(e):
    model=AssignmentModel(e['outcomes'],e['target_ids'],e['sb12']);aa={a['assignment_id']:a for a in e['result']['assignments']}
    for c in e['result']['components']:
        if not c['positive_incompatibility_proofs']:return False
        for p in c['positive_incompatibility_proofs']:
            if p['assignment_a'] not in aa or p['assignment_b'] not in aa:return False
            a=set(aa[p['assignment_a']]['selected_relation_ids']);b=set(aa[p['assignment_b']]['selected_relation_ids'])
            if not a-b or not b-a or model.errors(a) or model.errors(b) or not model.errors(a|b):return False
    for t in e['result']['targets']:
        local=any(len({(model.rows[i]['relation_type'],model.rows[i]['source_or_peer'],model.rows[i].get('excluded_outcome_id')) for i in c['relation_ids'] if model.rows[i]['target']==t['target']})>=2 for c in e['result']['constraints'])
        if t['true_target_decision_pivot']!=local:return False
    return True


def evaluate(e):
    r=e['result'];p=e['probes'];ts=r['targets'];ds=r['dispositions'];ids=[x['structural_outcome_group_id'] for x in e['outcomes']]
    cid={c['component_id'] for c in r['components']};tests=e['regression']
    return {
 'BASELINE_COMMIT_VERIFIED':bool(e['baseline']) and set(e['start_heads'])=={e['baseline']},
 'Q1_6R_FROZEN':not e['frozen_differences'] and e['input_hashes']==e['current_hashes'],
 'RAW_UNIVERSE_UNCHANGED':e['raw_count']==e['expected']['raw'] and e['raw_hash_before']==e['raw_hash_after'],
 'QUALIFIED_273_PRESERVED':e['outcomes']==e['preserved_outcomes'] and len(ids)==e['expected']['qualified'],
 'MOTHER_203_PRESERVED':sum(x['relation_type']=='HYPOTACTIC' for x in e['preserved_outcomes'])==e['expected']['mother'],
 'PARALLEL_70_PRESERVED':sum(x['relation_type']=='PARATACTIC' for x in e['preserved_outcomes'])==e['expected']['parallel'],
 'HUMAN_JUDGMENTS_13_UNCHANGED':e['human_count']==e['expected']['human'] and e['human_hash_before']==e['human_hash_after'],
 'ALL_QUALIFIED_RELATIONS_DISPOSED':len(ds)==len(ids) and {d['relation_id'] for d in ds}==set(ids),
 'ALL_TARGETS_CLASSIFIED':len(ts)==len(e['target_ids']) and {t['target'] for t in ts}==set(e['target_ids']) and all(t['target_status'] in STATUSES for t in ts),
 'QUALIFIED_NOT_EQUAL_ACCEPTED':all(not t['human_accepted'] for t in ts) and not p['single']['targets'][0]['human_review_required'],
 'MULTIPLE_NOT_EQUAL_REVIEW':not p['orthogonal']['components'] and not p['peers']['components'],
 'UNSELECTED_EQUALS_UNDECIDED':all(a['unselected_semantics']=='UNDECIDED' for a in r['assignments']) and not p['single']['components'],
 'ONE_MOTHER_CONSTRAINT_APPLIED':any('MOTHER_COMPETITION' in c['constraint_types'] for c in p['competition']['constraints']),
 'ADDITIVE_PARALLEL_PRESERVED':all(d['disposition']=='ADDITIVE_PARALLEL' for d in p['peers']['dispositions']) and not p['peers']['components'],
 'ORTHOGONAL_RELATIONS_PRESERVED':p['orthogonal']['targets'][0]['structural_status']=='QUALIFIED_COMPATIBLE_SET' and not p['orthogonal']['components'],
 'SAME_PAIR_CONFLICT_DETECTED':any('TRUE_PAIR_RELATION_CONFLICT' in c['constraint_types'] for c in p['same_pair']['constraints']),
 'GLOBAL_CYCLE_CONSTRAINT_IMPLEMENTED':any('STRICT_MOTHER_CYCLE' in c['constraint_types'] for c in p['cycle']['constraints']),
 'EVIDENCE_GAP_NOT_AUTOMATIC_REVIEW':not p['gap']['components'] and p['gap']['targets'][0]['target_status']=='EVIDENCE_GAP_NOT_STRUCTURAL_DECISION' and all(not t['human_review_required'] for t in ts if t['target_status']=='EVIDENCE_GAP_NOT_STRUCTURAL_DECISION'),
 'TRUE_PIVOT_REQUIRES_INCOMPATIBLE_POSITIVE_COMMITMENTS':valid_proofs(e),
 'HUMAN_REVIEW_UNIVERSE_DECISION_ONLY':len(e['universe'])==len(cid) and {u['component_id'] for u in e['universe']}==cid and all(u['status'] in REVIEW_STATUSES for u in e['universe']),
 'Q16R_EVIDENCE_ROLES_USED':bool(e['role_catalog']) and all(x['primary_role'] in DISPLAY_ROLES for x in e['role_catalog']) and set(e['packet_roles'])==set(DISPLAY_ROLES),
 'NO_SCORE':not (set(e['policy_names'])&{'score','scores','weight','votes'}),
 'NO_RANKING':not (set(e['policy_names'])&{'rank','ranking','ranked'}),
 'NO_TOP_N':not (set(e['policy_names'])&{'top_n','topN','max_candidates'}),
 'NO_DISTANCE_HEURISTIC':not (set(e['policy_names'])&{'distance','nearest','shortest','longest'}),
 'NO_CANONICAL_MOTHER':all(not t['canonical_mother'] for t in ts),
 'NO_CANONICAL_HIERARCHY':all(not t['canonical_hierarchy'] for t in ts),
 'NO_NEW_HUMAN_JUDGMENT':e['new_human_judgments']==0 and all(all(c[f]==('UNREVIEWED' if f=='review_status' else '') for f in REVIEW_FIELDS) for c in e['cards']),
 'HISTORICAL_H0_NOT_DISCOVERY_INPUT':not e['blind_access']['historical_review_inputs'] and not e['blind_access']['human_judgment_inputs'] and p['historical']['targets']==p['single']['targets'],
 'JOB_BLIND_BEFORE_POSTFREEZE_DIAGNOSTICS':e['blind_freeze_hashes']==e['postfreeze_hashes'] and not e['blind_access']['diagnostic_inputs'],
 'NO_JOB_DIAGNOSTIC_IDS_IN_CORE_LOGIC':not (set(e['core_literals'])&set(e['diagnostic_ids'])),
 'FULL_REGRESSION_PASS':tests.get('test_scope')=='FULL_REGRESSION' and tests.get('tests_run',0)>0 and tests.get('failures')==tests.get('errors')==0 and tests.get('code_fingerprint')==e['fingerprint'],
 'SKIP_ZERO':tests.get('skipped')==0,
 'DETERMINISTIC_RERUN':e['independent_equal'],
 'MANIFEST_VALID':e['manifest_valid'],
 'ZIP_CRC_VALID':e['crc_valid']}


def gates(e,pending=()):
    rr=[dict(gate=k,passed=bool(v),status='PASS' if v else 'PENDING' if k in pending else 'FAIL') for k,v in evaluate(e).items()]
    failed=[r['gate'] for r in rr if r['status']=='FAIL']
    if failed:raise ValueError('H0.1 gates failed: '+repr(failed))
    return rr


def fixture():
    from milal_h01_synthetic import cases,relation
    _,original=cases();probes=deepcopy(original);outcomes=[relation('m','M','T'),relation('m2','N','T')];r=deepcopy(probes['competition'])
    return dict(baseline='B',start_heads=['B']*3,frozen_differences=[],input_hashes={'x':'h'},current_hashes={'x':'h'},raw_count=4,raw_hash_before='raw',raw_hash_after='raw',
        expected=dict(raw=4,qualified=2,mother=2,parallel=0,human=1),outcomes=outcomes,preserved_outcomes=deepcopy(outcomes),human_count=1,human_hash_before='human',human_hash_after='human',
        target_ids=['T'],result=r,probes=probes,sb12=[],universe=[dict(component_id=c['component_id'],status=c['decision_status']) for c in r['components']],
        role_catalog=[dict(primary_role='PRIMARY_SOURCE_BINDING')],packet_roles=list(DISPLAY_ROLES),policy_names=[],core_literals=[],diagnostic_ids=['DIAGNOSTIC'],new_human_judgments=0,cards=[],
        blind_access=dict(historical_review_inputs=[],human_judgment_inputs=[],diagnostic_inputs=[]),blind_freeze_hashes={'x':'h'},postfreeze_hashes={'x':'h'},
        regression=dict(test_scope='FULL_REGRESSION',tests_run=1,failures=0,errors=0,skipped=0,code_fingerprint='fp'),fingerprint='fp',independent_equal=True,manifest_valid=True,crc_valid=True)


def mutations():
    return {
 'BASELINE_COMMIT_VERIFIED':lambda e:e['start_heads'].append('wrong'),
 'Q1_6R_FROZEN':lambda e:e['current_hashes'].update(x='mutated'),
 'RAW_UNIVERSE_UNCHANGED':lambda e:e.update(raw_count=3),
 'QUALIFIED_273_PRESERVED':lambda e:e['preserved_outcomes'].pop(),
 'MOTHER_203_PRESERVED':lambda e:e['preserved_outcomes'][0].update(relation_type='PARATACTIC'),
 'PARALLEL_70_PRESERVED':lambda e:e['preserved_outcomes'][0].update(relation_type='PARATACTIC'),
 'HUMAN_JUDGMENTS_13_UNCHANGED':lambda e:e.update(human_hash_after='changed'),
 'ALL_QUALIFIED_RELATIONS_DISPOSED':lambda e:e['result']['dispositions'].pop(),
 'ALL_TARGETS_CLASSIFIED':lambda e:e['result']['targets'].pop(),
 'QUALIFIED_NOT_EQUAL_ACCEPTED':lambda e:e['result']['targets'][0].update(human_accepted=True),
 'MULTIPLE_NOT_EQUAL_REVIEW':lambda e:e['probes']['peers']['components'].append({'invented':'multiplicity'}),
 'UNSELECTED_EQUALS_UNDECIDED':lambda e:e['result']['assignments'][0].update(unselected_semantics='NO_RELATION'),
 'ONE_MOTHER_CONSTRAINT_APPLIED':lambda e:e['probes']['competition']['constraints'].clear(),
 'ADDITIVE_PARALLEL_PRESERVED':lambda e:e['probes']['peers']['dispositions'][0].update(disposition='PART_OF_TRUE_DECISION'),
 'ORTHOGONAL_RELATIONS_PRESERVED':lambda e:e['probes']['orthogonal']['targets'][0].update(structural_status='TRUE_DECISION_PIVOT'),
 'SAME_PAIR_CONFLICT_DETECTED':lambda e:e['probes']['same_pair']['constraints'].clear(),
 'GLOBAL_CYCLE_CONSTRAINT_IMPLEMENTED':lambda e:e['probes']['cycle']['constraints'].clear(),
 'EVIDENCE_GAP_NOT_AUTOMATIC_REVIEW':lambda e:e['probes']['gap']['components'].append({'invented':'gap'}),
 'TRUE_PIVOT_REQUIRES_INCOMPATIBLE_POSITIVE_COMMITMENTS':lambda e:e['result']['components'][0].update(positive_incompatibility_proofs=[]),
 'HUMAN_REVIEW_UNIVERSE_DECISION_ONLY':lambda e:e['universe'].append(dict(component_id='fake',status='QUALIFIED_COMPATIBLE_SET')),
 'Q16R_EVIDENCE_ROLES_USED':lambda e:e['role_catalog'][0].update(primary_role='EQUAL_VOTE'),
 'NO_SCORE':lambda e:e['policy_names'].append('score'),
 'NO_RANKING':lambda e:e['policy_names'].append('ranking'),
 'NO_TOP_N':lambda e:e['policy_names'].append('top_n'),
 'NO_DISTANCE_HEURISTIC':lambda e:e['policy_names'].append('nearest'),
 'NO_CANONICAL_MOTHER':lambda e:e['result']['targets'][0].update(canonical_mother='M'),
 'NO_CANONICAL_HIERARCHY':lambda e:e['result']['targets'][0].update(canonical_hierarchy='H'),
 'NO_NEW_HUMAN_JUDGMENT':lambda e:e.update(new_human_judgments=1),
 'HISTORICAL_H0_NOT_DISCOVERY_INPUT':lambda e:e['blind_access']['historical_review_inputs'].append('historical_labels'),
 'JOB_BLIND_BEFORE_POSTFREEZE_DIAGNOSTICS':lambda e:e['postfreeze_hashes'].update(x='changed'),
 'NO_JOB_DIAGNOSTIC_IDS_IN_CORE_LOGIC':lambda e:e['core_literals'].append('DIAGNOSTIC'),
 'FULL_REGRESSION_PASS':lambda e:e['regression'].update(errors=1),
 'SKIP_ZERO':lambda e:e['regression'].update(skipped=1),
 'DETERMINISTIC_RERUN':lambda e:e.update(independent_equal=False),
 'MANIFEST_VALID':lambda e:e.update(manifest_valid=False),
 'ZIP_CRC_VALID':lambda e:e.update(crc_valid=False)}
