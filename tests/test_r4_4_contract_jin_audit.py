from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parent))
import r4_4_contract_jin_audit as j


def node(m,ident='H:HSA012'):return next(r for r in m['nodes'] if r['node_id']==ident)
def kind(m,typ):return next(r for r in m['nodes'] if r['node_kind']==typ)


MUTATIONS={
    'BASELINE_EXACT':lambda m,s:m['commit'].update(verified_commit='wrong'),
    'INPUT_VERIFIED':lambda m,s:m['receipt'].update(sha256='wrong'),
    'CONTRACT_ARTIFACT_PRESERVED':lambda m,s:m['historical'].update({'90_run_metadata.json':b'changed'}),
    'LAYER02_ARTIFACT_PRESERVED':lambda m,s:m['historical'].update({j.L2+'01_parentage_necessity_human_decisions.csv':b'changed'}),
    'HISTORICAL_57_PRESERVED':lambda m,s:m['crosswalk'].pop(),
    'SEAMS_FROZEN':lambda m,s:m['inputs']['seams'][0]['record'].update(status='UNREVIEWED'),
    'ANA_PRESERVED':lambda m,s:m['inputs']['questions'][-1]['record'].update(status='ACCEPTED'),
    'HISTORICAL_Q_UNREVIEWED':lambda m,s:m['supersession'][0].update(historical_review_status='ACCEPTED'),
    'ONE_METHODOLOGICAL_DECISION':lambda m,s:m['methodological_judgments'].append({'judgment_id':'extra'}),
    'ALL_NODES_CLASSIFIED':lambda m,s:m['nodes'].pop(),
    'GROUPS_EXEMPT':lambda m,s:kind(m,'COMPOSITION_GROUP').update(applicability_category=j.SM[0]),
    'ALIASES_EXEMPT':lambda m,s:kind(m,'ROLE_ALIAS').update(applicability_category=j.SM[0]),
    'TECHNICAL_EXEMPT':lambda m,s:kind(m,'TECHNICAL_ROOT').update(applicability_category=j.SM[0]),
    'TEXTUAL_COUNTS_SEPARATE':lambda m,s:m['summary'].update(textual_nodes=-1),
    'NO_NON_TEXTUAL_MOTHER':lambda m,s:m['candidates'][0].update(mother_candidate_id='OPENING_NARRATIVE_COMPLEX'),
    'NO_TECHNICAL_MOTHER':lambda m,s:m['candidates'][0].update(mother_candidate_id='JOB_BOOK'),
    'NO_PARENT_CREATED':lambda m,s:m['new_parent_edges'].append({'child_id':'H:HSA012','mother_id':'JOB_BOOK'}),
    'NO_NEAREST_HEURISTIC':lambda m,s:m['candidates'][0].update(basis=['NEAREST_PRECEDING_NODE']),
    'NO_COMPOSITION_AS_PARENT':lambda m,s:m['mothers'][0].update(relation_type='GROUP_MEMBER_OF'),
    'JOB_2_11_REOPENED':lambda m,s:node(m).update(additional_single_mother_review_required=False),
    'JOB_2_11_NO_MOTHER':lambda m,s:node(m).update(existing_direct_mother_ids=['H:HSA009']),
    'DIRECT_MOTHER_SEMANTICS':lambda m,s:m['mothers'].pop(),
    'MULTIPLE_MOTHER_CONFLICTS_REPORTED':lambda m,s:m['summary']['textual'].update(mother_gt1=-1),
    'ZERO_MOTHER_COVERAGE':lambda m,s:m['zero'].pop(),
    'ROOT_NOT_SELECTED':lambda m,s:node(m).update(root_status='ROOT_ACCEPTED',root_candidate=True),
    'CANDIDATES_UNADJUDICATED':lambda m,s:m['candidates'][0].update(candidate_status='ACCEPTED',accepted_relation=True),
    'REVISED_Q1_Q9_UNREVIEWED':lambda m,s:m['supersession'][0].update(review_status='ACCEPTED',researcher_answer='yes'),
    'READINESS_BLOCKED':lambda m,s:m.update(readiness='READY_FOR_IMPLEMENTATION'),
    'NO_CONSUMER':lambda m,s:m['consumer_implementations'].append('consumer'),
    'PARTICIPANT_ARC_UNADJUDICATED':lambda m,s:m.update(participant_arc='ACCEPTED'),
    'NO_NODE_JUDGMENTS':lambda m,s:m['node_judgments'].append('mother chosen'),
    'SAME_LEVEL_CONSISTENCY':lambda m,s:m['peers'][0].update(accepted_parent_created=True),
    'PROVENANCE_EXACT':lambda m,s:node(m).update(provenance={}),
    'FROZEN_PINS':lambda m,s:s['pins'][0].update(actual='wrong'),
    'REQUEST_EXACT':lambda m,s:s.update(request=b'wrong'),
    'REPORTS_FAITHFUL':lambda m,s:m['reports'].update({'08_job_2_11_single_mother_case.md':b'mother chosen'}),
    'DETERMINISTIC_PAYLOAD':lambda m,s:m.update(rerun_digest='wrong'),
}


class JinAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=j.load(True);cls.m=j.build(cls.s);cls.files=j.serialize(cls.m,cls.s)

    def test_all_gates_pass_and_negative_coverage(self):
        gg=j.gates(self.m,self.s)
        self.assertTrue(all(r['status']=='PASS' for r in gg))
        self.assertEqual({r['gate'] for r in gg},set(MUTATIONS))
        self.assertEqual(len(j.rows(self.files['13_gates.csv'])),len(MUTATIONS)+1)

    def test_manifest_positive_negative(self):
        self.assertTrue(j.util.manifest_ok(self.files))
        altered=dict(self.files);altered['02_single_mother_applicability_nodes.csv']+=b'corrupt'
        self.assertFalse(j.util.manifest_ok(altered))

    def test_release_positive_and_each_negative(self):
        good=dict(tests_run=1,successful=True,failures=0,errors=0,skipped=0)
        release=j.a.n.release_gates
        self.assertTrue(all(x['status']=='PASS' for x in release(good,b'zip',b'zip')))
        for key,value in [('tests_run',0),('successful',False),('failures',1),('errors',1),('skipped',1)]:
            self.assertEqual(release(dict(good,**{key:value}),b'zip',b'zip')[0]['status'],'FAIL')
        self.assertEqual(release(good,b'zip',b'different')[1]['status'],'FAIL')
        self.assertEqual(release(good,b'',b'')[1]['status'],'FAIL')

    def test_full_independent_payload_rebuild(self):
        self.assertEqual(self.files,j.serialize(j.build(deepcopy(self.s)),deepcopy(self.s)))

    def test_preserve_all_upstream_bytes_and_manifests(self):
        self.assertEqual({k[len(j.HISTORY):]:v for k,v in self.files.items() if k.startswith(j.HISTORY)},self.s['files'])
        self.assertTrue(all(r['valid'] for r in j.a.n.l.d.h.nested_manifests(self.files)))

    def test_every_receipt_resolves(self):
        for records in self.m['inputs'].values():
            for x in records:
                p=x['receipt'];data=self.files[p['member']];raw=j.a.n.l.d.h.raw_rows(data)[p['data_row']-1]
                self.assertEqual(raw[p['identity_field']],p['identity'])
                self.assertEqual(j.a.n.l.d.h.f.rowhash(raw),p['row_sha256'])
                self.assertEqual(j.sha(data),p['member_sha256'])
                self.assertEqual(p['artifact_sha256'],self.s['receipt']['sha256'])

    def test_role_alias_six_rows_not_six_exemptions(self):
        pp=[r for r in self.m['crosswalk'] if r['historical_category'].startswith('P3')]
        self.assertEqual(len(pp),6)
        self.assertEqual(sum(r['applicability_category']==j.SM[3] for r in pp),3)
        self.assertEqual(sum(r['actual_textual_node'] for r in pp),3)

    def test_historical_necessity_distinct_from_current_requirement(self):
        self.assertEqual(len(self.m['crosswalk']),57)
        self.assertTrue(all(r['historical_additional_parentage_review_required'] is False for r in self.m['crosswalk']))
        case=node(self.m)
        self.assertEqual(case['historical_necessity'],'DIRECT_TEXTUAL_PARENT_NOT_REQUIRED')
        self.assertEqual(case['historical_parent_status'],'UNRESOLVED')
        self.assertEqual(case['applicability_category'],j.SM[0])
        self.assertTrue(case['additional_single_mother_review_required'])
        self.assertEqual(case['existing_direct_mother_ids'],[])

    def test_exact_three_mother_edges_and_orientation(self):
        self.assertEqual(j.mother_index(self.m['mothers']),{'H:HSA003':['H:HSA002'],'H:HSA014':['H:HSA013'],'H:HSA026':['H:HSA025']})
        self.assertEqual(len(self.m['mothers']),3)
        self.assertTrue(all(r['classification']=='HIERARCHICAL_PLACEMENT_NOT_DIRECT_MOTHER' for r in self.m['semantics'] if r['relation_type']=='CONTINUES_WITHIN'))

    def test_duplicate_edge_same_mother_not_multiple_mothers(self):
        edges=deepcopy(self.m['mothers']);edges.append(deepcopy(edges[0]))
        self.assertEqual(j.mother_index(edges),j.mother_index(self.m['mothers']))

    def test_multiple_mother_conflict_reported_not_selected(self):
        edges=deepcopy(self.m['mothers']);extra=deepcopy(edges[0]);extra.update(child_id='H:HSA003',mother_id='H:HSA009');edges.append(extra)
        nn=j.audit_nodes(self.s,self.m['inputs'],edges);n=next(r for r in nn if r['node_id']=='H:HSA003')
        self.assertEqual(n['existing_direct_mother_count'],2)
        self.assertEqual(n['applicability_category'],j.SM[6]);self.assertTrue(n['additional_single_mother_review_required'])
        m=deepcopy(self.m);m['nodes']=nn
        self.assertEqual(j.counts(m)['textual']['mother_gt1'],1)

    def test_unknown_relation_type_ambiguous(self):
        rr=deepcopy(self.m['inputs']['relations']);r=next(x for x in rr if x['record']['layer']=='TEXTUAL_HIERARCHY');r['record']['relation_type']='UNKNOWN'
        sem=next(x for x in j.semantics(rr) if x['relation_id']==r['record']['relation_id'])
        self.assertEqual(sem['classification'],'AMBIGUOUS_MOTHER_SEMANTICS');self.assertEqual(sem['mother_id'],'')

    def test_source_evidence_not_promoted_to_macro_daughter(self):
        nn=[r for r in self.m['nodes'] if r['node_kind']=='SOURCE_EVIDENCE_ANCHOR']
        self.assertTrue(nn)
        self.assertTrue(all(r['applicability_category']==j.SM[6] and not r['actual_textual_node'] and not r['additional_single_mother_review_required'] for r in nn))
        self.assertTrue(all(r['clause_anchors'] and r['clause_atom_anchors'] for r in nn))

    def test_ambiguous_transition_not_deleted(self):
        n=node(self.m,'H:HSA018')
        self.assertEqual(n['applicability_category'],j.SM[6]);self.assertTrue(n['additional_single_mother_review_required'])
        self.assertTrue(n['existing_relations']['TRANSITION'])

    def test_candidates_are_not_accepted_parents(self):
        self.assertTrue(self.m['candidates'])
        for r in self.m['candidates']:
            self.assertEqual(r['candidate_status'],'UNADJUDICATED')
            self.assertFalse(r['accepted_relation'])
            self.assertEqual(node(self.m,r['node_id'])['existing_direct_mother_ids'],[])
        self.assertEqual(self.m['new_parent_edges'],[])

    def test_no_evidence_zero_pool_allowed(self):
        self.assertEqual(j.candidates(self.m['nodes'],[],[],self.m['inputs']['relations']),[])
        zero=next(r for r in self.m['zero'] if r['node_id']=='H:HSA012')
        self.assertEqual(zero['candidate_count'],0)

    def test_negative_pair_withholds_candidate(self):
        c=self.m['candidates'][0];rr=deepcopy(self.m['inputs']['relations']);r=deepcopy(rr[0]);r['record'].update(layer='NEGATIVE_CONSTRAINT',relation_id='NEG',source_node=c['node_id'],target_node=c['mother_candidate_id']);rr.append(r)
        result=j.candidates(self.m['nodes'],self.m['semantics'],self.m['peers'],rr)
        self.assertFalse(any(x['candidate_id']==c['candidate_id'] for x in result))

    def test_same_level_consistency_and_candidate_not_assignment(self):
        nn=deepcopy(self.m['nodes']);left=node({'nodes':nn},'H:HSA025');right=node({'nodes':nn},'H:HSA028')
        left['existing_direct_mother_ids']=['H:HSA013'];left['existing_direct_mother_count']=1
        rr=j.peers(nn,self.m['inputs']['relations'])
        pool=j.candidates(nn,[],rr,self.m['inputs']['relations'])
        self.assertTrue(any(r['node_id']=='H:HSA028' and r['mother_candidate_id']=='H:HSA013' for r in pool))
        self.assertEqual(right['existing_direct_mother_ids'],[])
        right['existing_direct_mother_ids']=['H:HSA015'];right['existing_direct_mother_count']=1
        rr=j.peers(nn,self.m['inputs']['relations'])
        self.assertTrue(any(r['source_id']=='H:HSA025' and r['target_id']=='H:HSA028' and r['consistency']=='CONFLICT_REQUIRES_REVIEW' for r in rr))
        right['existing_direct_mother_ids']=['H:HSA013']
        self.assertTrue(any(r['consistency']=='CONSISTENT' for r in j.peers(nn,self.m['inputs']['relations'])))

    def test_motherless_is_not_root_candidate(self):
        self.assertTrue(self.m['zero']);self.assertFalse(any(r['root_candidate'] for r in self.m['nodes']))
        self.assertEqual(node(self.m,'JOB_BOOK')['applicability_category'],j.SM[4])
        self.assertIn('JIN-Q0',self.files['09_root_scope_review.md'].decode())

    def test_no_location_fallback_for_anchors(self):
        inp=deepcopy(self.m['inputs']);n=next(x['record'] for x in inp['nodes'] if x['record']['node_id']=='H:HSA012')
        n['original_record']['source_evidence_ids']=[]
        result=next(r for r in j.audit_nodes(self.s,inp,self.m['mothers']) if r['node_id']=='H:HSA012')
        self.assertEqual(result['anchor_status'],'NOT_RECORDED');self.assertEqual(result['exact_native_clause_evidence'],[])

    def test_duplicate_identity_schema_fails(self):
        s=deepcopy(self.s);member=j.L1+'01_hsa3_canonical_nodes.csv';nn=deepcopy(j.rows(s['files'][member]));nn.append(nn[0]);s['files'][member]=j.util.csv_bytes(nn)
        with self.assertRaisesRegex(ValueError,'source identity schema'):j.inputs(s)

    def test_missing_identity_schema_fails(self):
        s=deepcopy(self.s);member=j.L1+'01_hsa3_canonical_nodes.csv';nn=deepcopy(j.rows(s['files'][member]));nn[0]['node_id']='';s['files'][member]=j.util.csv_bytes(nn)
        with self.assertRaisesRegex(ValueError,'source identity schema'):j.inputs(s)

    def test_historical_and_revised_packet_both_present(self):
        old=self.files[j.HISTORY+'13_r4_4_contract_review_packet.md'].decode();new=self.files['11_revised_r4_4_contract_review_packet.md'].decode()
        self.assertEqual(old.count('Review status: UNREVIEWED'),7)
        self.assertEqual(new.count('Review status: UNREVIEWED'),9)
        self.assertEqual(self.files['17_current_readiness.txt'],(j.READY+'\n').encode())

    def test_one_methodological_no_node_judgments(self):
        self.assertEqual(len(self.m['methodological_judgments']),1)
        self.assertEqual(self.m['methodological_judgments'][0]['individual_mother_assignments'],[])
        self.assertEqual(self.m['node_judgments'],[])

    def test_input_hash_failure(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'wrong.zip';p.write_bytes(b'wrong')
            with self.assertRaisesRegex(ValueError,'upstream ZIP SHA256'):j.load(archive=p)

    def test_synthetic_real_mix_rejected(self):
        with self.assertRaisesRegex(ValueError,'synthetic cannot consume'):j.load(True,'wrong.zip')


def negative(gate,mutate):
    def test(self):
        m=deepcopy(self.m);s=deepcopy(self.s);mutate(m,s)
        self.assertEqual(next(r['status'] for r in j.gates(m,s) if r['gate']==gate),'FAIL')
    return test


for gate,mutate in MUTATIONS.items():setattr(JinAuditTests,'test_negative_'+gate.lower(),negative(gate,mutate))

if __name__=='__main__':unittest.main()
