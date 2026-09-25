"""Q1.1 diagnostic release invariants; no analytical qualification."""
import ast
import re
from pathlib import Path

GATES = '''BASELINE_COMMIT_VERIFIED Q1_RAW_UNIVERSE_BYTE_STABLE
Q1_QUALIFIED_185_UNCHANGED Q1_OUTCOME_GROUPS_185_UNCHANGED Q1_PIVOTS_2_UNCHANGED
MFR02A_13_UNCHANGED NO_NEW_HUMAN_JUDGMENT NO_CANONICAL_MOTHER NO_CANONICAL_HIERARCHY
NO_NEW_QUALIFIED_RELATION NO_ID_SPECIFIC_CONTROL_EXCEPTION CONTROL_BLINDING_PRESERVED
NUMBERS_FIVE_RELATIONS_EXPLICITLY_AUDITED BOSMAN_TWO_UNIT_REFERENCES_EXPLICITLY_AUDITED
SB01_TO_SB12_MATRIX_COMPLETE SB06_RESTRICTIONS_INDEPENDENTLY_AUDITED NO_SCORE
NO_DISTANCE_CUTOFF NO_TOP_N NO_SKIPS FULL_REGRESSION_PASS DETERMINISTIC_RERUN MANIFEST_VALID'''.split()


def code_policy(text):
    tree=ast.parse(text)
    strings=[n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)]
    names={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
    attrs={n.attr for n in ast.walk(tree) if isinstance(n,ast.Attribute)}
    calls={n.func.id for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)}
    return dict(
        no_id_exception=not any(re.fullmatch(r'(?:P\d+-\d+|UC-\d+|\d{6,})',s) for s in strings) and
            not any(isinstance(n,ast.Constant) and type(n.value) is int and n.value>=100000 for n in ast.walk(tree)),
        no_book_rule=not set(strings)&{'Numbers','Numeri','Iob','Job','Lamentations','Threni','Qohelet','Isaiah','Pentateuch'},
        no_known_positive=not names&{'known_positive','known_controls','whitelist','target_whitelist','source_whitelist'},
        no_new_qualification=not calls&{'qualify','evaluate_pair','evaluate_rules','outcome'},
        no_score=not (names|attrs)&{'score','scores','ranking','weights'},
        no_distance_cutoff=not (names|attrs)&{'max_distance','distance_cutoff','distance_threshold'},
        no_top_n=not (names|attrs)&{'top_n','top_k','nlargest','nsmallest'},
        no_count_tuning=not (names|attrs)&{'desired_count','expected_control_count','recovery_threshold'})


def measurements(e):
    """e contains independently measured data/receipts, never desired gate flags."""
    c=e['counts']; expected=e['expected']; p=e['policy']; t=e['tests']
    values=[
        e['baseline']==e['expected_baseline'] and e['frozen_differences']==[],
        e['raw_crosswalk_errors']==0 and c['raw']==expected['raw'] and e['inputs_verified'],
        c['qualified']==expected['qualified'] and e['universe_equal'],
        c['outcome_groups']==expected['outcome_groups'] and e['outcomes_equal'],
        c['pivot_targets']==expected['pivot_targets'] and e['pivots_equal'],
        c['human_decisions']==expected['human_decisions'] and e['human_equal'],
        e['new_judgments']==[], e['canonical_mothers']==[],e['canonical_hierarchies']==[],
        e['universe_equal'] and p['no_new_qualification'] and e['new_relations']==[],
        p['no_id_exception'] and p['no_book_rule'] and p['no_known_positive'],
        e['events']==['BLIND_DIAGNOSTICS_STARTED','BLIND_DIAGNOSTICS_FROZEN','CONTROLS_STARTED','CONTROLS_FINISHED'] and e['blind_files_equal'] and p['no_count_tuning'],
        sorted(e['numbers_identities'])==sorted(e['expected_numbers']) and e['numbers_complete'],
        e['bosman_identities']==e['expected_bosman'] and e['bosman_unresolved'] and e['bosman_expansion_verified'],
        e['matrix_ids']==['SB%02d'%i for i in range(1,13)] and e['matrix_counts_equal'],
        e['sensitivity_complete'] and e['sensitivity_arithmetic'] and e['decomposition_errors']==0,
        p['no_score'],p['no_distance_cutoff'],p['no_top_n'],t['skipped']==0,
        t['test_scope']=='FULL_REGRESSION' and t['tests_run']>=2520 and t['failures']==t['errors']==0 and e['fingerprint_matches'],
        e['independent_equal'],e['manifest_valid']]
    return [dict(gate=k,passed=bool(v)) for k,v in zip(GATES,values)]


def assert_gates(e, pending=()):
    results=measurements(e)
    failed=[r['gate'] for r in results if not r['passed'] and r['gate'] not in pending]
    if failed: raise ValueError('Q1.1 failed gates: '+repr(failed))
    return results
