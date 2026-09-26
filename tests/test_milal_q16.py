import copy,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q16_evidence import EvidenceGraph,dependency_contract,conflicts,empirical_status
from milal_q16_synthetic import checks,graph_fixture,sample
from milal_q16_validation import GATE_FIELDS,gates
from milal_q1_binding import qualify,witness

class Q16Tests(unittest.TestCase):
    def test_runner_reads_core_source(self):
        from milal_q16_runner import ROOT,CORE
        self.assertTrue(all((ROOT/'src'/n).read_text(encoding='utf-8-sig') for n in CORE))
    def test_cycle_rejected(self):
        g,os,r,s=graph_fixture();g.nodes['w1']['dependencies']=['w2'];g.nodes['w2']['dependencies']=['w1']
        with self.assertRaises(ValueError):g.analyze(os)
    def test_missing_source_rejected(self):
        g,os,r,s=graph_fixture();del g.nodes[r]
        with self.assertRaises(KeyError):g.analyze(os)
    def test_no_unsupported_qualified_outcome(self):
        g,os,r,s=graph_fixture();g.paths.clear()
        with self.assertRaises(ValueError):g.analyze(os)
    def test_raw_identity_ignores_view(self):
        g,os,r,s=graph_fixture();self.assertEqual(r,g.raw('GRAMMAR','one',{'head':'a','dependent':'b'},'SYNTHETIC'))
    def test_native_identity_distinguishes_source_hash(self):
        g,os,r,s=graph_fixture();self.assertNotEqual(r,g.raw('GRAMMAR','one',{'head':'a','dependent':'b'},'OTHER_HASH'))
    def test_support_view_cannot_rescue_ablation(self):
        g,os,r,s=graph_fixture();g.add_view('view','SB09',[r],{'candidate_id':'Pa-b'})
        self.assertEqual(next(x for x in g.analyze(os)['ablation'] if x['mechanism']=='SB01')['lose_all_binding_support'],1)
    def test_shared_positive_raw_survives_unique_ablation(self):
        g,os,r,s=graph_fixture();g.derived('w3',{'positive_binding':True},[r],'SB05');g.paths[os[0]['structural_outcome_group_id']].append(dict(witness_id='w3'))
        x=g.analyze(os);self.assertEqual(next(x for x in x['ablation'] if x['mechanism']=='SB01')['lose_all_binding_support'],0)
        self.assertEqual(x['provenance'][0]['qualification_basis'],'MULTI_MECHANISM_SHARED_RAW_EVIDENCE')
    def test_independent_chain_classification(self):
        g,os,r,s=graph_fixture();g.paths[os[0]['structural_outcome_group_id']].append(dict(witness_id='w2'))
        self.assertEqual(g.analyze(os)['provenance'][0]['qualification_basis'],'MULTI_MECHANISM_INDEPENDENT')
    def test_derived_dependency_shares_raw(self):
        g,os,r,s=graph_fixture();g.derived('w3',{'positive_binding':True},['w1',s],'SB04');self.assertEqual(g.roots('w3'),{r,s})
    def test_absence_is_not_counterevidence(self):
        self.assertEqual(conflicts([dict(candidate_id='p',polarity='UNRESOLVED',raw_evidence=['x'],witness_id='w')]),[])
    def test_shared_counterevidence_not_independent_conflict(self):
        rr=[dict(candidate_id='p',polarity=p,raw_evidence=['x'],witness_id=str(i)) for i,p in enumerate(['POSITIVE_BINDING','COUNTEREVIDENCE'])];self.assertEqual(conflicts(rr),[])
    def test_semantic_valency_guess_rejected(self):
        v=sample('SB05');v['semantic_valency_guess']=True;self.assertEqual(dependency_contract(v),'UNRESOLVED')
    def test_missing_grammar_never_qualifies(self):
        w=witness('SB05','DIRECT_BINDING','a','b',sample('SB05'),['HYPOTACTIC']);self.assertEqual(qualify('a','b',[],[w])['qualified_relations'],[])
    def test_deferred_grammar_never_qualifies(self):
        w=witness('SB05','DIRECT_BINDING','a','b',sample('SB05'),['HYPOTACTIC']);self.assertEqual(qualify('a','b',[dict(rule_id='W-A01',relation='HYPOTACTIC')],[w],deferred=True)['qualified_relations'],[])
    def test_sb12_does_not_supply_audit_positive(self):
        self.assertRaises(ValueError,dependency_contract,dict(mechanism='SB12'))
    def test_missing_gate_evidence_rejected(self):
        self.assertRaises(ValueError,gates,{})
    def test_pending_gate_not_passed(self):
        e={f:True for f in GATE_FIELDS.values()};e['independent_equal']=False;rr=gates(e,['DETERMINISTIC_RERUN']);self.assertEqual(next(r for r in rr if r['gate']=='DETERMINISTIC_RERUN')['status'],'PENDING')
    def test_no_witness_status_not_fabricated(self):
        self.assertEqual(empirical_status([],[]),'NO_JOB_WITNESS');self.assertEqual(empirical_status([],['shared']),'OPERATIONAL_VIA_EXISTING_LAYER')

for name in [f'Q16-S{i}' for i in range(1,15)]:
    def synthetic(self,n=name):self.assertTrue(checks()[n],n)
    setattr(Q16Tests,'test_'+name.replace('-','_'),synthetic)
for name,field in GATE_FIELDS.items():
    def negative(self,n=name,f=field):
        ev={x:True for x in GATE_FIELDS.values()};ev[f]=False
        with self.assertRaisesRegex(ValueError,n):gates(ev)
    setattr(Q16Tests,'test_negative_'+name,negative)
if __name__=='__main__':unittest.main()
