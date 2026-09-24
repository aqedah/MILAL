"""Source-derived coverage and adversarial layer separation invariants."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_jin_relation_layers as a
import milal_jin_io as io
from milal_jin_relation_layers_fixture import fixture
from milal_jin_human_batch import release_gates


class RelationLayers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files,cls.cfg=fixture(a.config());cls.model=a.build(cls.files,cls.cfg)

    def test_all_gates_pass(self):
        self.assertTrue(all(a.gates(self.model,self.model).values()))

    def test_atom_is_not_clause_unit(self):
        n=next(n for n in self.model['nodes'] if n['clause_atom_ids'])
        self.assertEqual(n['proposed_node_layer'],'MACRO_TEXTUAL_UNIT')
        self.assertEqual(n['is_single_clause_atom'],'UNRESOLVED')

    def test_no_boundary_vs_speech_continuation(self):
        rr={r['source_ref']:r for r in self.model['inventory'] if r['relation_type']=='CONTINUES_WITHIN'}
        self.assertEqual(rr['28:1']['proposed_semantics'],'NO_NEW_BOUNDARY')
        self.assertEqual(rr['42:16']['proposed_semantics'],'NO_NEW_BOUNDARY')
        self.assertEqual(rr['3:2']['proposed_semantics'],'MACRO_TEXTUAL_CONTINUATION')

    def test_deterministic_render(self):
        self.assertEqual(a.render(self.model),a.render(a.build(self.files,self.cfg)))

    def test_bad_manifest(self):
        f=deepcopy(self.files);f['90_run_metadata.json']+=b' '
        with self.assertRaises(ValueError):a.build(f,self.cfg)

    def test_empty_manifest_rejected(self):
        with self.assertRaises(ValueError):a.build({'99_manifest_sha256.csv':b''},self.cfg)

    def test_duplicate_identity_rejected(self):
        f=deepcopy(self.files);p='registry/'+a.TABLES[0];rr=io.rows(f[p]);rr.append(rr[0]);f[p]=io.csv_bytes(rr);io.seal(f)
        with self.assertRaises(ValueError):a.build(f,self.cfg)

    def test_missing_required_column_rejected(self):
        f=deepcopy(self.files);p='registry/'+a.TABLES[0];rr=io.rows(f[p]);del rr[0]['relation_type'];f[p]=io.csv_bytes(rr, list(set().union(*(r.keys() for r in rr))));io.seal(f)
        # Blank required type must not silently become an unresolved proposal.
        with self.assertRaises(ValueError):a.build(f,self.cfg)

    def test_strict_requires_independent_evidence(self):
        r=deepcopy(next(r for r in self.model['inventory'] if r['relation_type']=='CHILD_OF'))
        self.assertTrue(a.classify(r)[0].startswith('RL2'))
        r['strict_evidence_status']='INDEPENDENT_LOCAL_DEPENDENCY'
        self.assertTrue(a.classify(r)[0].startswith('RL3'))
        r['macro_evidence_status']='UNRESOLVED';self.assertTrue(a.classify(r)[0].startswith('RL1'))

    def test_release_negative_determinism(self):
        self.assertEqual(release_gates(b'a',b'b',dict(tests_run=1,failures=0,errors=0,skipped=0))[0]['status'],'FAIL')

    def test_release_negative_regression(self):
        for key in ('skipped','failures','errors'):
            receipt=dict(tests_run=1,failures=0,errors=0,skipped=0);receipt[key]=1
            self.assertEqual(release_gates(b'a',b'a',receipt)[1]['status'],'FAIL')

    def test_preflight_gate_negatives(self):
        cfg=self.cfg;request=(a.ROOT/cfg['source_request']['path']).read_bytes()
        args=[cfg['baseline'],cfg['frozen_files'],self.files,request,[],cfg]
        self.assertTrue(all(a.preflight_gates(*args).values()))
        for index,value,gate in [(0,'wrong','BASELINE_COMMIT_VERIFIED'),(1,{},'JIN_0_5_FROZEN_PRESERVED'),(3,b'wrong','EXACT_REQUEST_PRESERVED'),(4,['consumer.py'],'R4_4_CONSUMER_ABSENT')]:
            changed=deepcopy(args);changed[index]=value
            self.assertFalse(a.preflight_gates(*changed)[gate])

    def test_linguistic_flags_extracted_from_pair_not_hypothesis(self):
        f=deepcopy(self.files)
        p=self.cfg['sources']['15_postcontext_human_comparison.csv']
        f[p]=io.csv_bytes([dict(human_relation_id='SYN:0',exact_pair_ids=['P1'])])
        p=self.cfg['sources']['01_context_supported_pair_inventory.csv']
        f[p]=io.csv_bytes([dict(pair_id='P1',source_pair=dict(evidence_flags=dict(S_EXPLICIT_SUBORDINATION_MARKER=True,S_ANAPHORIC_DEPENDENCY=True)),source_hypothesis=dict(hypotaxis_supported=True))])
        io.seal(f);m=a.build(f,self.cfg);r=m['inventory'][0]
        self.assertTrue(r['explicit_subordination_evidence'])
        self.assertTrue(r['syntactic_dependency_evidence'])
        self.assertTrue(r['reference_dependency_evidence'])
        self.assertEqual(r['strict_evidence_status'],'UNPROVEN_FOR_THIS_MACRO_EDGE')
        self.assertEqual(r['proposal_category'],'RL2_MACRO_TEXTUAL_HIERARCHY')

    def test_non_hsa_human_ids_and_nested_evidence_preserved(self):
        f=deepcopy(self.files);p='registry/06_hsa3_transition_relations.csv';rr=io.rows(f[p])
        rr[0]['original_record']=dict(judgment_id='ANA-H2',evidence_ids=['E1'],original_record=dict(action_id='A1',source_evidence_ids=['E2']))
        f[p]=io.csv_bytes(rr);io.seal(f);m=a.build(f,self.cfg)
        r=next(r for r in m['inventory'] if r['relation_type']=='POST_CLOSURE_TRANSITION')
        self.assertEqual(r['human_source_id'],['A1','ANA-H2'])
        self.assertEqual(r['evidence_ids'],['E1','E2'])


def mutation_test(gate):
    def test(self):
        m=deepcopy(self.model)
        if gate in ('HIERARCHY_RELATIONS_INVENTORIED','RELATION_LAYER_AUDIT_COMPLETE','NO_HISTORICAL_REWRITE'):
            m['inventory'].pop()
        elif gate in ('NODE_LAYER_CROSSWALK_COMPLETE','CLAUSE_ATOM_ANCHOR_NOT_EQUAL_STRICT_HIERARCHY'):
            m['nodes'][0]['proposed_node_layer']='STRICT_CLAUSE_NODE'
        elif gate=='STRICT_CONTROL_PRESENT':m['strict'][0]['human_accepted']=True
        elif gate=='MACRO_CONTROL_PRESENT':
            next(r for r in m['inventory'] if r['batch_decisions'])['strict_evidence_status']='INDEPENDENT_LOCAL_DEPENDENCY'
        elif gate.endswith('_LAYER_AUDITED'):
            typ=gate.removesuffix('_LAYER_AUDITED');next(r for r in m['inventory'] if r['relation_type']==typ)['proposed_relation_layer']='STRICT_CLAUSE_HIERARCHY'
        elif gate.endswith('_LAYER_DISTINCTION_PRESENT'):
            ref={'JOB_1_13':'1:13','JOB_3_1_2':'3:1','JOB_40_1':'40:1','JOB_28_1':'28:1','JOB_42_16':'42:16'}[gate.removesuffix('_LAYER_DISTINCTION_PRESENT')]
            next(r for r in m['inventory'] if r['source_ref']==ref and r['relation_type'] in a.PRIMARY)['strict_evidence_status']='INDEPENDENT_LOCAL_DEPENDENCY'
        elif gate.endswith('_NO_MOTHER_CREATED'):m['new_parents'].append(dict(source='2:11',target='1:1'))
        elif gate.endswith('_NOT_STRICT_HIERARCHY'):
            layer={'COMPOSITION':'COMPOSITION_GROUPING','TRANSITION':'TRANSITION','OVERLAY':'OVERLAY_RESPONSIO'}[gate.removesuffix('_NOT_STRICT_HIERARCHY')]
            next(r for r in m['inventory'] if r['historical_layer']==layer)['proposed_relation_layer']='STRICT_CLAUSE_HIERARCHY'
        elif gate in ('NO_RELATION_MIGRATION','NO_NEW_RELATION','NO_NEW_PARENT','NO_NEW_HUMAN_JUDGMENT'):
            key={'NO_RELATION_MIGRATION':'migrations','NO_NEW_RELATION':'new_relations','NO_NEW_PARENT':'new_parents','NO_NEW_HUMAN_JUDGMENT':'human_judgments'}[gate];m[key].append('UNAUTHORIZED')
        elif gate=='Q1_Q9_UNAPPROVED':m['q1_q9']['Q1']='APPROVED'
        elif gate=='QA_QF_UNREVIEWED':m['reviews'][0]['review_status']='ACCEPTED'
        elif gate=='PARTICIPANT_ARC_UNADJUDICATED':m['participant_arc']='ACCEPTED'
        elif gate=='OVERLOADING_SUMMARY_RECONCILES':m['summary'][0]['strict_count']+=1
        else:self.fail('Missing negative mutation for '+gate)
        self.assertFalse(a.gates(m,self.model)[gate],gate)
    return test

_f,_c=fixture(a.config());_m=a.build(_f,_c)
for _gate in a.gates(_m,_m):setattr(RelationLayers,'test_negative_'+_gate.lower(),mutation_test(_gate))

if __name__=='__main__':unittest.main()
