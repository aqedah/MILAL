import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q16r_roles import process_role,valency_case,independence,readiness,INDEPENDENCE,mechanism_overlaps
from milal_q16r_synthetic import checks,fixture,mutations,basis
from milal_q16r_validation import evaluate,gates
from milal_q16r_provenance import Projection
class Q16RTests(unittest.TestCase):
    def test_overlap_includes_analytical_parent_and_shared_core(self):
        aa=dict(basis('a',['x']),mechanism='SB01');bb=dict(basis('b',['y'],parents=['a']),mechanism='SB04');cc=dict(basis('c',['x']),mechanism='SB05')
        result=mechanism_overlaps({r['id']:r for r in (aa,bb,cc)})
        self.assertEqual(result['SB01'],{'SB04','SB05'});self.assertIn('SB01',result['SB04'])
    def test_overlap_does_not_promote_shared_context(self):
        aa=dict(basis('a',['x'],['context']),mechanism='SB01');bb=dict(basis('b',['y'],['context']),mechanism='SB06')
        self.assertEqual(mechanism_overlaps({'a':aa,'b':bb})['SB01'],set())
    def test_direct_vs_inherited_same_raw_is_derived(self):
        self.assertEqual(independence(basis('a',['x']),basis('b',['y'],inherited=['x']))['independence_class'],'DERIVED_FROM_SAME_RAW_EVIDENCE')

    def test_phrase_raw_does_not_invent_word_dependency(self):
        p=Projection.__new__(Projection);p.raw={('PHRASE','1'):'phrase',('WORD','2'):'word'};p.active_raw={'phrase'}
        self.assertEqual(p.frame(dict(node=1,word_ids=[2])),{'phrase'})
    def test_separately_attested_frame_word_is_preserved(self):
        p=Projection.__new__(Projection);p.raw={('PHRASE','1'):'phrase',('WORD','2'):'word'};p.active_raw={'phrase','word'}
        self.assertEqual(p.frame(dict(node=1,word_ids=[2])),{'phrase','word'})
    def test_missing_frame_identity_fails(self):
        p=Projection.__new__(Projection);p.raw={};p.active_raw=set()
        self.assertRaises(ValueError,p.frame,dict(node=1,word_ids=[]))

    def test_distinct_raw_observations(self):
        self.assertEqual(independence(basis('a',['x']),basis('b',['y']))['independence_class'],'INDEPENDENT_RAW_EVIDENCE')
    def test_derived_shared_not_direct_identity(self):
        self.assertEqual(independence(basis('a',['x'],inherited=['shared']),basis('b',['y'],inherited=['shared']))['independence_class'],'DERIVED_FROM_SAME_RAW_EVIDENCE')
    def test_analytical_dependency_not_raw_identity(self):
        r=independence(basis('a',['x']),basis('b',['y'],parents=['a'],inherited=['x']));self.assertEqual(r['independence_class'],'ANALYTICALLY_DEPENDENT');self.assertEqual(r['same_direct_raw'],[])
    def test_incomplete_projection_unresolved(self):
        self.assertEqual(independence(basis('a',[],complete=False),basis('b',['y']))['independence_class'],'UNRESOLVED_INDEPENDENCE')
    def test_shared_context_not_vote(self):
        r=independence(basis('a',['x'],['ctx']),basis('b',['y'],['ctx']));self.assertNotIn('score',r);self.assertEqual(r['same_direct_raw'],[])
    def test_atom_different_owner_not_auto_binding(self):
        r=valency_case('a','b',{'c'},{'d'},'c');self.assertEqual(r['primary_role'],'UNRESOLVED_ROLE');self.assertFalse(r['new_relation'])
    def test_ambiguous_atom_owner_not_auto_reconstruct(self):
        self.assertEqual(valency_case('a','b',{'c','d'},{'c'},'c')['case_class'],'UNRESOLVED_OWNERSHIP_OR_GOVERNANCE')
    def test_native_dependency_requires_path(self):
        self.assertEqual(process_role(dict(process_kind='NATIVE_DEPENDENCY')),'UNRESOLVED_ROLE')
    def test_participant_dependency_is_corroborative(self):
        self.assertEqual(process_role(dict(process_kind='PARTICIPANT_CONTINUATION',dependent_on=['SB01'])),'CORROBORATIVE_RELATION_EVIDENCE')
    def test_explicit_deictic_delegates(self):
        self.assertEqual(process_role(dict(process_kind='EXPLICIT_DEICTIC')),'REFERENCE_VISIBILITY_CONTEXT')
    def test_interpretation_is_downstream(self):
        for k in ('TEMPORAL_INTERPRETATION','GEOGRAPHICAL_INTERPRETATION'):self.assertEqual(process_role(dict(process_kind=k)),'POST_RELATION_VALIDATION')
    def test_unknown_process_not_assigned(self):self.assertEqual(process_role(dict(process_kind='NEW_UNVERIFIED_RULE')),'UNRESOLVED_ROLE')
    def test_valid_gates(self):self.assertEqual(len(gates(fixture())),25)
    def test_readiness_known_primary_gap(self):self.assertEqual(readiness(fixture()['registry'],['known_gap'],[],True,True),'NEEDS_PRIMARY_BINDING_IMPLEMENTATION')
    def test_readiness_role_ambiguity(self):self.assertEqual(readiness(fixture()['registry'],[],['unclear'],True,True),'NEEDS_MECHANISM_ONTOLOGY_REVIEW')
    def test_readiness_zero_not_failure(self):self.assertEqual(readiness(fixture()['registry'],[],[],True,True),'READY_FOR_MFR_0_2R_H0_1')
for name in ['Q16R-S'+str(i) for i in range(1,11)]:
    def test(self,n=name):self.assertTrue(checks()[n])
    setattr(Q16RTests,'test_'+name.replace('-','_'),test)
for name,mutation in mutations().items():
    def test(self,n=name,m=mutation):
        e=fixture();m(e);self.assertFalse(evaluate(e)[n]);self.assertRaises(ValueError,gates,e)
    setattr(Q16RTests,'test_negative_'+name,test)
if __name__=='__main__':unittest.main()
