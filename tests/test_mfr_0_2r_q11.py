"""Independent diagnostic decomposition, source identities and gate mutations."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q11_diagnostic import restriction_vector,sensitivity,diagnose_pair,classify_nonretention,RESTRICTIONS,competition_count
from milal_q11_synthetic import unit,evidence_fixture,mutated_evidence,semantic_checks,self_test
from milal_q11_validation import measurements,GATES,code_policy,assert_gates
from milal_q1_binding import SourceIndex
from milal_q1_synthetic import source_fixture
from milal_mfr02r_data import rows
from milal_mfr02r_grammar import load_registry


class Q11Tests(unittest.TestCase):
    def test_competition_table_rows_are_not_competitions(self):
        records=[dict(target_id='a',qualified_alternatives=[],competition=False),
                 dict(target_id='b',qualified_alternatives=['one'],competition=False),
                 dict(target_id='c',qualified_alternatives=['one','two'],competition=True)]
        self.assertEqual(competition_count(records),1)

    def test_competition_disagrees_with_distinct_alternatives(self):
        with self.assertRaises(ValueError):
            competition_count([dict(target_id='a',qualified_alternatives=['one','one'],competition=True)])

    def test_duplicate_competition_target_rejected(self):
        r=dict(target_id='a',qualified_alternatives=[],competition=False)
        with self.assertRaises(ValueError):competition_count([r,r])

    def test_semantic_checks(self):
        self.assertTrue(all(semantic_checks()[0].values()))

    def test_self_test_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=self_test(Path(tmp)/'run')
            self.assertTrue(result['passed'])
            self.assertEqual((Path(tmp)/'run/a.csv').read_bytes(),(Path(tmp)/'run/b.csv').read_bytes())

    def test_no_mutation(self):
        a,b=unit(),unit(); before=copy.deepcopy((a,b));restriction_vector(a,b)
        self.assertEqual((a,b),before)

    def test_np_morphology_not_identity(self):
        a,b=unit(),unit();b['explicit_np_witnesses'][0]['lex']='OTHER/'
        v=restriction_vector(a,b)
        self.assertFalse(v['CORRESPONDING_LEXICAL_NP']);self.assertFalse(v['CORRESPONDING_GRAMMATICAL_POSITION'])

    def test_same_lex_different_position(self):
        a,b=unit(),unit();b['explicit_np_witnesses'][0]['clause_id']='b'
        v=restriction_vector(a,b)
        self.assertTrue(v['CORRESPONDING_LEXICAL_NP']);self.assertFalse(v['CORRESPONDING_GRAMMATICAL_POSITION'])

    def test_same_lex_different_function(self):
        a,b=unit(),unit();b['explicit_np_witnesses'][0]['function']='Objc'
        self.assertFalse(restriction_vector(a,b)['CORRESPONDING_GRAMMATICAL_POSITION'])

    def test_singleton_is_not_multiclause(self):
        a,b=unit(),unit();b['members']=['a']
        self.assertFalse(restriction_vector(a,b)['CONTIGUOUS_NATIVE_MULTICLAUSE'])

    def test_speech_only_fails(self):
        a,b=unit(),unit();a['nonformula_predicate_witnesses']=[]
        self.assertFalse(restriction_vector(a,b)['NON_SPEECH_PREDICATE'])

    def test_empty_population_explicit(self):
        result=sensitivity([],'synthetic')
        self.assertEqual(len(result),5);self.assertTrue(all(r['population']==0 for r in result))

    def test_joint_failures_not_recovered_relations(self):
        result=sensitivity([dict(failed_restrictions=list(RESTRICTIONS))],'synthetic')
        self.assertTrue(all(r['excluded_solely']==0 and r['excluded_with_others']==1 for r in result))

    def test_no_false_negative_claim(self):
        labels=classify_nonretention(dict(qualified_relations=[],original_relations=['PARATACTIC']),
            dict(sb06=dict(failed_restrictions=['IDENTICAL_FULL_SIGNATURE'])))
        self.assertIn('B_UNRESOLVED_EVIDENCE',labels)
        self.assertIn('D_CONSERVATIVE_SB06_SUBSET',labels)
        self.assertNotIn('FALSE_NEGATIVE',labels)

    def test_decomposition_guard(self):
        class Index:pass
        index=Index();index.units={'a':unit(),'b':unit()}
        index.units['b']['eligible']=False
        with self.assertRaises(ValueError):diagnose_pair(index,'a','b')

    def test_policy_current_diagnostic(self):
        path=Path(__file__).resolve().parents[1]/'src/milal_q11_diagnostic.py'
        self.assertTrue(all(code_policy(path.read_text()).values()))

    def test_gate_missing_evidence_fails_closed(self):
        with self.assertRaises(KeyError):measurements({})

    def test_actual_frozen_adapter_conjunction(self):
        root=Path(__file__).resolve().parents[1]
        grammar=load_registry(root/'config/clause_relation_grammar_v1.json')
        with tempfile.TemporaryDirectory() as tmp:
            source=source_fixture(Path(tmp)/'source')
            index=SourceIndex(list(rows(source/'blind/job/02_clause_feature_inventory.csv')),
                grammar['lexicons']['subordinate_rela'],grammar['lexicons']['speech'])
            checked=0
            for target in index.ordered:
                for sid in index.ordered[:index.index[target]]:
                    d=diagnose_pair(index,sid,target)
                    actual=any(w['mechanism']=='SB06' for w in index.bindings(sid,target))
                    self.assertEqual(d['frozen_sb06_conjunction'],actual);checked+=1
            self.assertGreater(checked,0)

    def test_policy_generic_id_not_just_control(self):
        self.assertFalse(code_policy("def bad(): return 'P987654-123456'")['no_id_exception'])
        self.assertFalse(code_policy('def bad(): return 987654')['no_id_exception'])


def negative_test(gate):
    def test(self):
        e=mutated_evidence(gate)
        self.assertFalse(next(r['passed'] for r in measurements(e) if r['gate']==gate))
        with self.assertRaises(ValueError):assert_gates(e)
    return test

for gate in GATES:setattr(Q11Tests,'test_negative_'+gate.lower(),negative_test(gate))

if __name__=='__main__':unittest.main()
