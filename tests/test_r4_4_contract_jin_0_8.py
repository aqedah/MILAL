"""Contract source fidelity and an explicit mutation for every computed gate."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_jin_contract_freeze as a
import milal_jin_io as io
from milal_jin_contract_freeze_fixture import fixture
from milal_jin_human_batch import release_gates


class ContractFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.f,cls.c=fixture(a.config());cls.request=(a.ROOT/cls.c['source_request']['path']).read_bytes();cls.m=a.build(cls.f,cls.c,cls.request)

    def test_valid(self):self.assertTrue(all(a.gates(self.m,self.m).values()))

    def test_source_qualifications(self):
        self.assertEqual([r['qualification_type'] for r in self.m['primary']],['NONE','NONE','QUALIFICATION','NONE','NONE','NONE','NONE','QUALIFICATION','NONE','REWORDING'])
        self.assertEqual(len(self.m['invariants']),20)
        for r in self.m['primary']:
            p=r['provenance'];b=self.request[p['byte_start']:p['byte_end']]
            self.assertEqual(b.decode(),r['approved_text']);self.assertEqual(io.sha(b),p['excerpt_sha256'])

    def test_authority_negative(self):
        with self.assertRaises(ValueError):a.authority(self.c,self.request+b'x')
        for key,value in [('decision','UNREVIEWED'),('qualification_type','NONE'),('approved_text','fake'),('byte_start',0),('excerpt_sha256','bad')]:
            c=deepcopy(self.c);c['decisions'][2][key]=value
            with self.assertRaises(ValueError):a.authority(c,self.request)
        c=deepcopy(self.c);c['invariants'][0]['approved_text']='false'
        with self.assertRaises(ValueError):a.authority(c,self.request)

    def test_old_review_fields_unchanged(self):
        out=a.render(self.m,self.c,self.request)
        self.assertTrue(all(out[a.HISTORY+k]==v for k,v in self.f.items()))
        self.assertTrue(all(r['review_status']=='UNREVIEWED' for r in io.rows(out[a.HISTORY+'10_remaining_strict_macro_questions.csv'])))

    def test_no_blanket_mother_requirement(self):
        c=self.m['contract'];self.assertEqual(c['strict_mother_rule']['placement'],'STRICT_HYPOTACTIC_DAUGHTER')
        self.assertEqual(c['macro_mother_rule']['placement'],'MACRO_HYPOTACTIC_DAUGHTER')
        self.assertFalse(c['synthetic_macro_mother']);self.assertFalse(c['composition_can_be_mother']);self.assertFalse(c['technical_root_can_be_mother'])

    def test_scope_not_only_five_and_later_judgment_preserved(self):
        q=self.m['questions'];self.assertGreater(len(q),5)
        r=next(r for r in q if r['question_id']=='SCOPE:SYN:REVIEW2')
        self.assertEqual(r['source_records'][1]['record']['relation_decision'],'PARATACTIC')
        self.assertTrue(all(r['review_status']=='UNREVIEWED' and not r['selected_mother_if_hypotactic'] for r in q))

    def test_deterministic(self):
        self.assertEqual(a.render(self.m,self.c,self.request),a.render(a.build(self.f,self.c,self.request),self.c,self.request))

    def test_missing_schema_no_inference(self):
        for kind in ('identity','duplicate','count','scope'):
            f=deepcopy(self.f)
            if kind=='scope':del f[a.unique_member(f,'24_contextual_human_review_cases.csv')]
            else:
                rr=io.rows(f[a.INVENTORY])
                if kind=='identity':rr[0]['relation_id']='wrong'
                elif kind=='duplicate':rr[0]['relation_id']=rr[1]['relation_id']
                else:rr.pop()
                f[a.INVENTORY]=io.csv_bytes(rr)
            io.seal(f)
            with self.assertRaises((ValueError,KeyError)):a.build(f,self.c,self.request)

    def test_preflight_negatives(self):
        args=[self.c,self.request,self.c['frozen_files'],self.c['baseline'],self.c['archive']['sha256'],[]]
        self.assertTrue(all(a.preflight(*args).values()))
        for i,v,k in [(1,b'x','EXACT_RESEARCHER_SOURCE'),(2,{},'JIN_0_7_FROZEN_VERIFIED'),(3,'wrong','BASELINE_COMMIT_VERIFIED'),(4,'bad','JIN_0_7_FROZEN_VERIFIED'),(5,['consumer'],'NO_CONSUMER_FILES')]:
            x=deepcopy(args);x[i]=v;self.assertFalse(a.preflight(*x)[k])

    def test_manifest_negative(self):
        f=deepcopy(self.f);f[a.INVENTORY]+=b'x';self.assertFalse(io.manifest_ok(f))
        with self.assertRaises(ValueError):a.build(f,self.c,self.request)

    def test_release_negatives(self):
        receipt=dict(tests_run=1,failures=0,errors=0,skipped=0)
        self.assertEqual(release_gates(b'a',b'b',receipt)[0]['status'],'FAIL')
        for k in ('failures','errors','skipped'):
            r=dict(receipt);r[k]=1;self.assertEqual(release_gates(b'a',b'a',r)[1]['status'],'FAIL')


def mutation(gate,m):
    c=m['contract']
    if gate=='TEN_PRIMARY_DECISIONS':m['primary'].pop()
    elif gate.startswith('R') and '_ACCEPTED' in gate:
        q=gate.split('_')[0];next(r for r in m['primary'] if r['question_id']==q)['decision']='UNREVIEWED'
    elif gate in {'CONTRACT_INVARIANTS_FROZEN','HISTORICAL_Q1_Q9_CROSSWALK','ALL_FIXTURES_PRESERVED','MIGRATION_PREVIEW_ONLY','DERIVED_INTERPRETATIONS_PRESERVED','OPEN_SCOPE_COMPLETE'}:
        k={'CONTRACT_INVARIANTS_FROZEN':'invariants','HISTORICAL_Q1_Q9_CROSSWALK':'crosswalk','ALL_FIXTURES_PRESERVED':'fixtures','MIGRATION_PREVIEW_ONLY':'preview','DERIVED_INTERPRETATIONS_PRESERVED':'derived','OPEN_SCOPE_COMPLETE':'questions'}[gate];m[k].pop()
    elif gate in {'RELATION_LAYER_VOCABULARY_FROZEN','STRICT_SINGLE_MOTHER_SCOPE_CORRECT','MACRO_SINGLE_MOTHER_SCOPE_CORRECT','SCHEMA_STATUS_AXES_SEPARATE','STATUS_AXES_FROZEN','LAYER_SPECIFIC_VALIDATION','SUPERSEDING_ADJUDICATION_REQUIRED'}:
        k={'RELATION_LAYER_VOCABULARY_FROZEN':'relation_layers','STRICT_SINGLE_MOTHER_SCOPE_CORRECT':'strict_mother_rule','MACRO_SINGLE_MOTHER_SCOPE_CORRECT':'macro_mother_rule','SCHEMA_STATUS_AXES_SEPARATE':'minimum_fields','STATUS_AXES_FROZEN':'status_axes','LAYER_SPECIFIC_VALIDATION':'validation_by_layer','SUPERSEDING_ADJUDICATION_REQUIRED':'lower_layer_revision_requires'}[gate];c[k]=[]
    elif gate in ('NO_SYNTHETIC_MACRO_PARENT','NO_SYNTHETIC_STRICT_PARENT'):m['new_parents'].append('FAKE')
    elif gate=='COMPOSITION_NOT_MOTHER':c['composition_can_be_mother']=True
    elif gate=='TECHNICAL_ROOT_NOT_ANALYTICAL_ROOT':c['technical_root_can_be_mother']=True
    elif gate=='HISTORICAL_RELATIONS_UNCHANGED':m['history'][a.INVENTORY]+=b'x'
    elif gate=='HISTORICAL_Q1_Q9_UNCHANGED':m['history']['09_revised_contract_review_packet.md']+=b'x'
    elif gate in FIXTURE_GATES:
        next(r for r in m['fixtures'] if r['fixture_id']==FIXTURE_GATES[gate])['layer_collapsed']=True
    elif gate in ('JOB_2_11_UNRESOLVED','JOB_32_1_UNRESOLVED'):m['mother_status']['2:11' if '2_11' in gate else '32:1']='ASSIGNED'
    elif gate=='NO_ROOT_SELECTED':m['new_roots'].append('JOB_BOOK')
    elif gate in ('STRICT_TOP_LEVEL_AUDIT_SCOPED','MACRO_TOP_LEVEL_AUDIT_SCOPED'):m['scope'][gate.split('_')[0].lower()]['outcomes']=['ONE_UNIQUE_ROOT']
    elif gate=='AUDIT_FORBIDDEN_HEURISTICS':m['scope']['forbidden']=[]
    elif gate=='NO_RELATION_MIGRATION':m['migrations'].append('FAKE')
    elif gate in ('NO_NEW_ANALYTICAL_RELATION','NO_NEW_PARENT','NO_NEW_COMPOSITION','NO_NEW_PARTICIPANT'):
        m[{'NO_NEW_ANALYTICAL_RELATION':'new_relations','NO_NEW_PARENT':'new_parents','NO_NEW_COMPOSITION':'new_composition','NO_NEW_PARTICIPANT':'new_participant'}[gate]].append('FAKE')
    elif gate=='NO_R4_4_CONSUMER':c['consumer_implemented']=True
    elif gate=='PARTICIPANT_ARC_UNADJUDICATED':m['participant_arc']='ACCEPTED'
    elif gate=='COMPLETE_CONTRACT_FROZEN':c['representation']='UNIVERSAL_TREE'
    else:raise AssertionError('missing mutation '+gate)


FIXTURE_GATES=dict(zip(['JOB_1_13_MACRO_STRICT_SPLIT_PRESERVED','JOB_3_1_2_MACRO_STRICT_SPLIT_PRESERVED','JOB_40_1_MACRO_STRICT_SPLIT_PRESERVED','JOB_28_1_NO_NEW_BOUNDARY','JOB_42_16_NO_NEW_BOUNDARY','SAME_LEVEL_MACRO_PARATAXIS','NEGATIVE_OVERLAY_COEXISTENCE','JOB_31_40_TYPED_DIMENSIONS'],['F'+str(i) for i in range(1,9)]))
def negative(gate):
    def test(self):
        m=deepcopy(self.m);mutation(gate,m);self.assertFalse(a.gates(m,self.m)[gate])
    return test

_f,_c=fixture(a.config());_m=a.build(_f,_c,(a.ROOT/_c['source_request']['path']).read_bytes())
for _g in a.gates(_m,_m):setattr(ContractFreezeTests,'test_negative_'+_g.lower(),negative(_g))

if __name__=='__main__':unittest.main()
