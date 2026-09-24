"""Human source fidelity, derived accounting and negative tests for every gate."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_jin_layer_freeze as a
import milal_jin_io as io
from milal_jin_layer_freeze_fixture import fixture
from milal_jin_human_batch import release_gates


class LayerFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f,cls.c=fixture(a.config());cls.request=(a.ROOT/cls.c['source_request']['path']).read_bytes();cls.m=a.build(cls.f,cls.c,cls.request)

    def test_valid(self):self.assertTrue(all(a.gates(self.m,self.m).values()))

    def test_shared_qb_qd_one_application(self):
        r=[r for r in self.m['applications'] if r['historical_relation_id']=='E:b2b850faaf0159baeadc']
        self.assertEqual(len(r),1);self.assertEqual(r[0]['source_judgment'],['Q-B','Q-D'])
        self.assertEqual(len(self.m['primary']),6)

    def test_provisional_seven_not_promoted(self):
        self.assertEqual(sum(r['macro_status']=='PROVISIONAL_CURRENT_AUDIT' for r in self.m['applications']),7)

    def test_deterministic_and_original_bytes(self):
        x=a.render(self.m,self.c,self.request);y=a.render(a.build(self.f,self.c,self.request),self.c,self.request)
        self.assertEqual(x,y);self.assertTrue(all(x[a.HISTORY+k]==v for k,v in self.f.items()))

    def test_authority_negatives(self):
        with self.assertRaises(ValueError):a.authority(self.c,self.request+b'x')
        for field,value in [('human_decision','UNREVIEWED'),('verbatim','fabricated'),('byte_start',0),('excerpt_sha256','bad')]:
            c=deepcopy(self.c);c['decisions'][0][field]=value
            with self.assertRaises(ValueError):a.authority(c,self.request)

    def test_schema_identity_count_negatives(self):
        for kind in ('missing','duplicate','count','status'):
            f=deepcopy(self.f);rr=io.rows(f[a.INVENTORY])
            if kind=='missing':rr[0]['relation_id']='wrong'
            elif kind=='duplicate':rr[0]['relation_id']=rr[1]['relation_id']
            elif kind=='count':rr.pop()
            else:rr[0]['proposal_status']='ACCEPTED'
            f[a.INVENTORY]=io.csv_bytes(rr);io.seal(f)
            with self.assertRaises(ValueError):a.build(f,self.c,self.request)

    def test_missing_question_not_invented(self):
        f=deepcopy(self.f);f[self.c['question_source']]=b'Q1: Only one\n';io.seal(f)
        with self.assertRaises(ValueError):a.build(f,self.c,self.request)

    def test_source_mother_not_substituted(self):
        import json
        f=deepcopy(self.f);meta=json.loads(f['90_run_metadata.json']);meta['mother_search_results']['2:11']='ASSIGNED';f['90_run_metadata.json']=io.js(meta);io.seal(f)
        with self.assertRaises(ValueError):a.build(f,self.c,self.request)

    def test_manifest_corruption(self):
        f=deepcopy(self.f);f[a.INVENTORY]+=b'x'
        self.assertFalse(io.manifest_ok(f))
        with self.assertRaises(ValueError):a.build(f,self.c,self.request)

    def test_preflight_negatives(self):
        args=[self.c,self.request,self.c['frozen_files'],self.c['baseline'],self.c['archive']['sha256'],[]]
        self.assertTrue(all(a.preflight(*args).values()))
        for index,val,key in [(1,b'x','EXACT_RESEARCHER_SOURCE'),(2,{},'JIN_0_6_FROZEN_VERIFIED'),(3,'wrong','BASELINE_COMMIT_VERIFIED'),(4,'wrong','JIN_0_6_FROZEN_VERIFIED'),(5,['consumer'],'NO_CONSUMER_FILES')]:
            x=deepcopy(args);x[index]=val;self.assertFalse(a.preflight(*x)[key])

    def test_release_gate_negatives(self):
        receipt=dict(tests_run=1,failures=0,errors=0,skipped=0)
        self.assertEqual(release_gates(b'a',b'b',receipt)[0]['status'],'FAIL')
        for k in ('failures','errors','skipped'):
            r=dict(receipt);r[k]=1;self.assertEqual(release_gates(b'a',b'a',r)[1]['status'],'FAIL')


def negative(gate):
    def test(self):
        m=deepcopy(self.m);aa=m['applications']
        if gate=='SIX_PRIMARY_HUMAN_DECISIONS':m['primary'].pop()
        elif gate.endswith('_ACCEPTED'):
            q='Q-'+gate[1];next(r for r in m['primary'] if r['source_judgment']==q)['human_decision']='UNREVIEWED'
        elif gate in ('QA_STRICT_1_13_UNRESOLVED','QB_STRICT_3_1_2_UNRESOLVED','QC_STRICT_40_1_UNPROVEN'):
            q='Q-'+gate[1];next(r for r in aa if q in r['source_judgment'])['strict_status']='ACCEPTED'
        elif gate=='DERIVED_APPLICATIONS_COMPLETE':aa.pop()
        elif gate in ('CONTINUATION_APPLICATIONS_COMPLETE','SAME_LEVEL_ROWS_UNCHANGED'):
            typ='CONTINUES_WITHIN' if gate.startswith('CONTINUATION') else 'SAME_LEVEL_SIBLING';next(r for r in aa if r['historical_relation_type']==typ)['approved_relation_layer']='STRICT_CLAUSE_HIERARCHY'
        elif gate=='HISTORICAL_RELATIONS_UNCHANGED':m['history'][a.INVENTORY]+=b'x'
        elif gate in ('NO_RELATION_MIGRATION','NO_NEW_PARENT','NO_NEW_RELATION'):
            m[{'NO_RELATION_MIGRATION':'migrations','NO_NEW_PARENT':'new_parents','NO_NEW_RELATION':'new_relations'}[gate]].append('FORBIDDEN')
        elif gate in ('MACRO_NOT_EQUAL_STRICT','CLAUSE_ATOM_NOT_EQUAL_STRICT','MACRO_PARATAXIS_NOT_STRICT','STRICT_NOT_AUTOMATIC_MACRO'):
            key={'MACRO_NOT_EQUAL_STRICT':'macro_does_not_entail_strict','CLAUSE_ATOM_NOT_EQUAL_STRICT':'anchor_does_not_determine_layer','MACRO_PARATAXIS_NOT_STRICT':'macro_sibling_does_not_entail_strict_parataxis','STRICT_NOT_AUTOMATIC_MACRO':'strict_does_not_entail_macro'}[gate];m['contract'][key]=False
        elif gate=='NO_BOUNDARY_NOT_EQUAL_MOTHER':m['contract']['no_boundary_is_not_mother']=False
        elif gate in ('JOB_28_1_NO_NEW_BOUNDARY','JOB_42_16_NO_NEW_BOUNDARY'):
            ref='28:1' if '28_1' in gate else '42:16';next(r for r in aa if r['source_ref']==ref)['approved_semantic_subtype']='STRICT_SYNTACTIC_CONTINUATION'
        elif gate=='PROVISIONAL_CONTINUATIONS_NOT_PROMOTED':next(r for r in aa if r['macro_status']=='PROVISIONAL_CURRENT_AUDIT')['macro_status']='ACCEPTED'
        elif gate=='TYPE_LAYER_VOCABULARY_FROZEN':m['contract']['relation_layer_values'].append('BOUNDARY_PLACEMENT')
        elif gate in ('JOB_2_11_UNRESOLVED','JOB_32_1_UNRESOLVED'):m['mother_status']['2:11' if '2_11' in gate else '32:1']='ASSIGNED'
        elif gate=='HISTORICAL_Q1_Q9_NOT_AUTO_APPROVED':m['question_crosswalk'][0]['new_approval']=True
        elif gate=='REVISED_R1_R10_UNREVIEWED':m['questions'][0]['review_status']='ACCEPTED'
        elif gate=='STRICT_CONTROLS_NOT_PROMOTED':m['strict_controls'][0]['human_accepted']=True
        elif gate=='NO_R4_4_CONSUMER':m['contract']['consumer_implemented']=True
        elif gate=='PARTICIPANT_ARC_UNADJUDICATED':m['participant_arc']='ACCEPTED'
        else:self.fail('Missing mutation '+gate)
        self.assertFalse(a.gates(m,self.m)[gate],gate)
    return test

_f,_c=fixture(a.config());_m=a.build(_f,_c,(a.ROOT/_c['source_request']['path']).read_bytes())
for _g in a.gates(_m,_m):setattr(LayerFreezeTests,'test_negative_'+_g.lower(),negative(_g))

if __name__=='__main__':unittest.main()
