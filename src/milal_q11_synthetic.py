"""Small fixed-unit fixtures and negative invariants for Q1.1 diagnostics."""
import copy
from pathlib import Path
from milal_q11_diagnostic import restriction_vector,diagnose_pair,sensitivity,RESTRICTIONS
from milal_q11_validation import measurements,code_policy,GATES
from milal_mfr02r_data import table,encode,digest
from milal_mfr02r_pipeline import code_fingerprint


def unit():
    return dict(members=['a','b'],links=[],explicit_np_witnesses=[dict(clause_id='a',function='Subj',lex='N/')],
        nonformula_predicate_witnesses=[dict(lex='GO[')],signature=[['WayX',[['GO[','verb','impf','qal']]],['NmCl']],eligible=True)


def evidence_fixture():
    expected=dict(raw=4,qualified=1,outcome_groups=1,pivot_targets=['t'],human_decisions=1)
    return dict(counts=expected.copy(),expected=expected,baseline='base',expected_baseline='base',frozen_differences=[],
        raw_crosswalk_errors=0,inputs_verified=True,universe_equal=True,outcomes_equal=True,pivots_equal=True,
        human_equal=True,new_judgments=[],canonical_mothers=[],canonical_hierarchies=[],new_relations=[],
        policy=code_policy('def diagnostic(a):\n    return a\n'),
        events=['BLIND_DIAGNOSTICS_STARTED','BLIND_DIAGNOSTICS_FROZEN','CONTROLS_STARTED','CONTROLS_FINISHED'],blind_files_equal=True,
        numbers_identities=[['p','r']],expected_numbers=[['p','r']],numbers_complete=True,
        bosman_identities=[['s','u',['t']]],expected_bosman=[['s','u',['t']]],bosman_unresolved=True,bosman_expansion_verified=True,
        matrix_ids=['SB%02d'%i for i in range(1,13)],matrix_counts_equal=True,sensitivity_complete=True,
        sensitivity_arithmetic=True,decomposition_errors=0,tests=dict(test_scope='FULL_REGRESSION',tests_run=2520,failures=0,errors=0,skipped=0),
        fingerprint_matches=True,independent_equal=True,manifest_valid=True)


MUTATIONS = dict(zip(GATES,[
    ('baseline','wrong'),('raw_crosswalk_errors',1),('universe_equal',False),('outcomes_equal',False),('pivots_equal',False),
    ('human_equal',False),('new_judgments',['injected']),('canonical_mothers',['injected']),('canonical_hierarchies',['injected']),
    ('new_relations',['injected']),('policy.no_id_exception',False),('events',[]),('numbers_identities',[]),('bosman_unresolved',False),
    ('matrix_ids',[]),('sensitivity_arithmetic',False),('policy.no_score',False),('policy.no_distance_cutoff',False),
    ('policy.no_top_n',False),('tests.skipped',1),('tests.errors',1),('independent_equal',False),('manifest_valid',False)]))


def mutated_evidence(gate):
    result=evidence_fixture();key,value=MUTATIONS[gate]
    target=result
    parts=key.split('.')
    for part in parts[:-1]:target=target[part]
    target[parts[-1]]=copy.deepcopy(value)
    return result


def semantic_checks():
    left=unit();right=unit()
    checks={'identical_fixed_units_pass':all(restriction_vector(left,right).values())}
    right['signature']=[['different']]
    vector=restriction_vector(left,right)
    checks['signature_only_failure']=[k for k,v in vector.items() if not v]==['IDENTICAL_FULL_SIGNATURE']
    right['nonformula_predicate_witnesses']=[]
    vector2=restriction_vector(left,right)
    records=[dict(failed_restrictions=[k for k,v in vector.items() if not v]),dict(failed_restrictions=[k for k,v in vector2.items() if not v])]
    values={r['restriction']:r for r in sensitivity(records,'synthetic')}
    checks['sole_joint_distinguished']=values['IDENTICAL_FULL_SIGNATURE']['excluded_solely']==1 and values['IDENTICAL_FULL_SIGNATURE']['excluded_with_others']==1
    checks['all_predicates_accounted']=all(r['passed']+r['excluded_solely']+r['excluded_with_others']==2 for r in values.values())
    checks['positive_gate_fixture']=all(r['passed'] for r in measurements(evidence_fixture()))
    for gate in GATES:
        checks['negative_'+gate]=not next(r['passed'] for r in measurements(mutated_evidence(gate)) if r['gate']==gate)
    for key,text in {
        'no_id_exception':"def bad(): return 'P443836-443840'",
        'no_book_rule':"def bad(book): return book == 'Numbers'",
        'no_known_positive':'def bad(known_positive): return known_positive',
        'no_new_qualification':'def bad(): return qualify()',
        'no_score':'def bad(score): return score',
        'no_distance_cutoff':'def bad(distance_cutoff): return distance_cutoff',
        'no_top_n':'def bad(top_n): return top_n',
        'no_count_tuning':'def bad(desired_count): return desired_count'}.items():
        checks['policy_negative_'+key]=not code_policy(text)[key]
    return checks,records


def self_test(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    checks,records=semantic_checks()
    for name in ('a','b'):
        table(out/(name+'.csv'),sensitivity(records,'synthetic'))
    equal=(out/'a.csv').read_bytes()==(out/'b.csv').read_bytes()
    result=dict(mode='SYNTHETIC',passed=all(checks.values()) and equal,checks=checks,bytes_equal=equal,
                code_fingerprint=code_fingerprint())
    (out/'receipt.json').write_text(encode(result)+'\n',encoding='utf8',newline='\n')
    (out/'review.md').write_text('# Synthetic sensitivity review\n\nTwo pairs: signature fails alone once and jointly with non-speech once. No relation is created.\n',encoding='utf8')
    if not result['passed']:raise ValueError('synthetic checks failed')
    return result
