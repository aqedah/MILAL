import sys,unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_h01_model import sieve
from milal_h01_synthetic import cases,relation
from milal_h01_validation import fixture,mutations,evaluate,gates
from milal_q13_model import AssignmentModel
from milal_h01_evidence import partition_evidence
from milal_h01_runner import ensure_code_unchanged


class H01Tests(unittest.TestCase):
    def test_global_cycle_not_local_target_pivot(self):
        r=sieve([relation('a','A','B'),relation('b','B','A')],['A','B'])
        self.assertEqual(len(r['components']),1)
        self.assertTrue(all(t['human_review_required'] for t in r['targets']))
        self.assertFalse(any(t['true_target_decision_pivot'] for t in r['targets']))
    def test_context_target_not_promoted_by_connected_mother_competition(self):
        r=sieve([relation('a','A','T'),relation('b','B','T'),relation('c','T','A')],['A','B','T'])
        tt={t['target']:t for t in r['targets']}
        self.assertTrue(tt['T']['true_target_decision_pivot']);self.assertFalse(tt['A']['true_target_decision_pivot'])
        self.assertEqual(tt['A']['target_status'],'GLOBAL_CONSTRAINT_DECISION')
    def test_explicit_negative_is_positive_target_alternative(self):
        r=sieve([relation('a','A','T'),relation('n','','T','EXCLUDED',excluded_outcome_id='a',constraint_provenance='SOURCE')],['T'])
        self.assertTrue(r['targets'][0]['true_target_decision_pivot'])
    def test_execution_code_change_is_rejected(self):
        with patch('milal_h01_runner.code_fingerprint',return_value='new'):
            self.assertRaises(ValueError,ensure_code_unchanged,'old')
    def test_execution_stable_code_is_allowed(self):
        with patch('milal_h01_runner.code_fingerprint',return_value='same'):ensure_code_unchanged('same')
    def test_other_pair_primary_binding_is_context_only(self):
        pp={k:dict(primary_role='PRIMARY_SOURCE_BINDING',detail=dict(witness=dict(source_id=s,target_id='T'))) for k,s in [('own','A'),('other','B')]}
        direct,context=partition_evidence(pp,{'own'},{'A','T'})
        self.assertEqual(set(direct),{'own'});self.assertEqual(set(context),{'other'})
    def test_local_reference_observation_retained_without_pair_binding(self):
        pp={'ref':dict(primary_role='REFERENCE_VISIBILITY_CONTEXT',detail=dict(form=dict(target_clause_id='T')))}
        direct,context=partition_evidence(pp,set(),{'S','T'})
        self.assertEqual(set(direct),{'ref'});self.assertFalse(context)
    def test_three_mothers_all_pairwise_cores(self):
        r=sieve([relation(x,x,'T') for x in ('A','B','C')],['T'])
        self.assertEqual(len(r['constraints']),3);self.assertEqual(len(r['components']),1)
    def test_unrelated_cycles_are_distinct_components(self):
        r=sieve([relation('a','A','B'),relation('b','B','A'),relation('c','C','D'),relation('d','D','C')],['A','B','C','D'])
        self.assertEqual(len(r['components']),2)
    def test_shared_target_without_conflict_not_component(self):
        r=sieve([relation('a','A','T','PARATACTIC'),relation('b','B','T','PARATACTIC')],['T'])
        self.assertFalse(r['components'])
    def test_higher_order_sb12_constraint_is_preserved(self):
        rs=[relation(str(i),'S'+str(i),'T'+str(i)) for i in range(3)]
        c=dict(kind='FORBIDDEN_COMBINATION',constraint_id='EXPLICIT',constraint_provenance='SYNTHETIC_EXPLICIT_SOURCE',independent=True,outcome_ids=['0','1','2'])
        r=sieve(rs,[x['target'] for x in rs],constraints=[c])
        self.assertEqual(len(r['components']),1);self.assertEqual(r['constraints'][0]['constraint_types'],['SB12_HARD_CONFLICT'])
    def test_empty_qualified_target_preserved_with_gap(self):
        r=sieve([],['A'],[dict(target='A')]);self.assertEqual(r['targets'][0]['target_status'],'NO_QUALIFIED_RELATION')
    def test_unresolved_evidence_does_not_create_exclusion(self):
        r=sieve([relation('a','S','T')],['T'],[dict(target='T')]);self.assertEqual(len(r['dispositions']),1);self.assertFalse(r['components'])
    def test_global_cycle_assignments_are_coherent(self):
        rs=[relation('a','A','B'),relation('b','B','C'),relation('c','C','A')];r=sieve(rs,['A','B','C']);m=AssignmentModel(rs)
        self.assertEqual(len(r['constraints']),1)
        for a in r['assignments']:self.assertFalse(m.errors(a['selected_relation_ids']))
    def test_multiple_rule_paths_never_multiply_disposition(self):
        r=relation('a','S','T');r['provenance_paths']*=3
        self.assertEqual(len(sieve([r],['T'])['dispositions']),1)
    def test_duplicate_relation_identity_rejected(self):
        r=relation('a','S','T');self.assertRaises(ValueError,sieve,[r,r],['T'])
    def test_unverified_global_constraint_rejected(self):
        rs=[relation('a','A','T'),relation('b','B','T')]
        self.assertRaises(ValueError,sieve,rs,['T'],constraints=[dict(kind='FORBIDDEN_COMBINATION',constraint_provenance='',independent=False)])
    def test_provenance_change_not_structural_choice(self):
        rs=[relation('a','S','T'),relation('b','S','T')];r=sieve(rs,['T'])
        self.assertFalse(r['components']);self.assertEqual(r['targets'][0]['distinct_commitment_count'],1)
    def test_zero_review_valid_universe_gate(self):
        e=fixture();e['result']=deepcopy(cases()[1]['single']);e['universe']=[]
        self.assertTrue(evaluate(e)['HUMAN_REVIEW_UNIVERSE_DECISION_ONLY'])
    def test_valid_all_gates(self):self.assertEqual(len(gates(fixture())),36)
    def test_selection_vs_omission_has_no_two_positive_assignments(self):
        r=sieve([relation('a','S','T')],['T']);self.assertFalse(r['assignments']);self.assertFalse(r['components'])


for key in ['H01-S'+str(i) for i in range(1,15)]:
    def test(self,k=key):self.assertTrue(cases()[0][k])
    setattr(H01Tests,'test_'+key.replace('-','_'),test)
for key,mutation in mutations().items():
    def test(self,k=key,m=mutation):
        e=fixture();m(e);self.assertFalse(evaluate(e)[k]);self.assertRaises(ValueError,gates,e)
    setattr(H01Tests,'test_negative_'+key,test)
if __name__=='__main__':unittest.main()
