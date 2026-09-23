from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_fg_final_adjudication as f


def remove_relation(m,relation):
    m['actions']=[r for r in m['actions'] if r['relation_type']!=relation]


def add_relation(m,src,tgt,rel):
    m['actions'].append(dict(action='CREATED',source_node=src,target_node=tgt,relation_type=rel,dimension='MUTATED'))


def six(m):
    return next(r['original_record']['evidence_id'] for r in m['evidence'] if r['original_record']['reference']=='42:6')


def promote(m,ref):
    r=next(r['original_record'] for r in m['evidence'] if r['original_record']['reference']==ref)
    add_relation(m,r['evidence_id'],f.FINAL,'CHILD_OF')


def mutate_life(m):
    r=next(r['original_record'] for r in m['evidence'] if r['original_record']['reference']=='42:16' and r['original_record']['lexical_waychi_words'])
    r['verbal_words'][0]['lex']='HJH['


MUTATIONS={
 'BASELINE_COMMIT_VERIFIED':lambda m,s:m['commit'].update(verified_commit='bad'),
 'FG_PREP_VERIFIED':lambda m,s:m['receipt'].update(sha256='bad'),
 'SEAM_F_RESEARCHER_DECISION_RECORDED':lambda m,s:m['adjudications'][0].update(status='UNREVIEWED'),
 'SEAM_G_RESEARCHER_DECISION_RECORDED':lambda m,s:m['adjudications'][1].update(status='UNREVIEWED'),
 'ALL_A_G_SEAMS_FROZEN':lambda m,s:m['all_seams'][0].update(status='UNREVIEWED'),
 'RESPONSE_COMPLEX_1_PRESENT':lambda m,s:m['groups'][0].update(span_end='40:6'),
 'RESPONSE_COMPLEX_2_PRESENT':lambda m,s:m['groups'][1].update(span_start='40:7'),
 'RESPONSE_SEQUENCE_PRESENT':lambda m,s:m['groups'][2]['members'].reverse(),
 'FINAL_NARRATIVE_COMPLEX_PRESENT':lambda m,s:m['groups'][3].update(span_end='42:16'),
 'RESPONSE_COMPLEX_PEERS_PRESENT':lambda m,s:remove_relation(m,f.PEER),
 'RESPONSE_GROUPS_NON_TEXTUAL':lambda m,s:add_relation(m,'H:HSA025',f.C1,'CHILD_OF'),
 'EXISTING_YHWH_JOB_RELATIONS_PRESERVED':lambda m,s:remove_relation(m,'CHILD_OF'),
 'POST_SPEECH_NARRATIVE_TRANSITION_PRESENT':lambda m,s:remove_relation(m,f.TRANSITION),
 'NO_42_6_42_7_PARENTAGE':lambda m,s:add_relation(m,six(m),'H:HSA030','CHILD_OF'),
 'NO_42_6_42_7_RESPONSE_EDGE':lambda m,s:add_relation(m,six(m),'H:HSA030','RESPONSE_TO'),
 'JOB_42_10_NOT_PROMOTED':lambda m,s:promote(m,'42:10'),
 'JOB_42_12_NOT_PROMOTED':lambda m,s:promote(m,'42:12'),
 'JOB_42_16_NO_BOUNDARY_PRESERVED':lambda m,s:remove_relation(m,'CONTINUES_WITHIN'),
 'WAYHI_WAYHI_LIFE_VERB_DISTINCTION_PRESERVED':lambda m,s:mutate_life(m),
 'ANA_Q3_STILL_UNRESOLVED':lambda m,s:next(r for r in m['ana'] if r['review_question_id']=='ANA-Q3').update(status='ACCEPTED'),
 'ANA_Q4_Q5_PRESERVED':lambda m,s:next(r for r in m['ana'] if r['review_question_id']=='ANA-Q4').update(status='UNRESOLVED'),
 'NO_2_11_42_9_FRAME_ADJUDICATION':lambda m,s:m['participant_frame_adjudications'].append('ACCEPTED'),
 'UNRESOLVED_PARENTAGE_NOT_FAKE_RESOLVED':lambda m,s:m['crosswalk'][-1].update(direct_parent=f.FINAL,direct_parent_resolved=True),
 'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m,s:m['historical'].update({f.NODES:b'corrupt'}),
 'NO_DUPLICATE_RELATIONS':lambda m,s:m['actions'].append(deepcopy(next(r for r in m['actions'] if r['action']=='CREATED'))),
 'NO_R4_4':lambda m,s:m.update(r44_started=True),
 'NO_NEW_LEXICAL_ANALYSIS':lambda m,s:m['lexical_scans'].append('scan'),
 'RESEARCHER_SOURCE_EXACT':lambda m,s:s.update(request=b'changed'),
 'FROZEN_SOURCE_FILES':lambda m,s:s['frozen'][0].update(actual='changed'),
 'RELATION_ACTIONS_EXACT':lambda m,s:m['actions'].pop(),
 'NEGATIVE_CONSTRAINTS_EXACT':lambda m,s:m['negative'].pop(),
 'CRITERIA_CANONICAL':lambda m,s:m['criteria'][0].update(evidence_code='GUESSED'),
 'SOURCE_EVIDENCE_EXACT':lambda m,s:m['evidence'][0]['original_record'].update(clause_node='guessed'),
 'RESPONSE_SPANS_NO_DUPLICATE_NODES':lambda m,s:m['annotations'][0].update(new_node=True),
 'FROZEN_NODES_EXACT':lambda m,s:m['facts'].pop(),
 'SCHEMA_AUDIT_EXACT':lambda m,s:m['schema'].update(reused_type='SAME_LEVEL_SIBLING'),
 'REPORT_FAITHFUL':lambda m,s:m.update(summary='Fully resolved tree'),
 'DETERMINISTIC_RERUN':lambda m,s:m.update(rerun_digest='wrong'),
}


class FGFinalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=f.load(True);cls.m=f.build(cls.s);cls.files=f.serialize(cls.m,cls.s)

    def test_gate_negative_coverage(self):
        self.assertEqual(set(MUTATIONS),{r['gate'] for r in f.gates(self.m,self.s)})

    def test_all_gates_pass(self):
        self.assertTrue(all(r['status']=='PASS' for r in f.rows(self.files['10_gates.csv'])))

    def test_manifest_negative(self):
        ff=dict(self.files);ff['03_hsa3_fg_composition_groups.csv']+=b'corrupt'
        self.assertFalse(f.util.manifest_ok(ff))

    def test_independent_rebuild(self):
        self.assertEqual(self.files,f.serialize(f.build(deepcopy(self.s)),deepcopy(self.s)))

    def test_all_historical_members_exact(self):
        self.assertTrue(all(self.files[f.HISTORY+n]==b for n,b in self.s['files'].items()))
        self.assertTrue(all(r['valid'] for r in f.d.h.nested_manifests(self.files)))

    def test_baseline_exact(self):
        self.assertEqual(self.s['commit']['verified_commit'],'d720d805f771cb18912728dd6982177c57459ef6')

    def test_prior_review_fields_blank(self):
        for r in f.rows(self.s['files']['18_fg_review_fields.csv']):
            for k in f.REVIEW_FIELDS:self.assertEqual(r[k],'UNREVIEWED' if k=='review_status' else '')

    def test_groups_and_spans(self):
        self.assertEqual([(g['group_id'],g['span_start'],g['span_end']) for g in self.m['groups']],
            [(f.C1,'38:1','40:5'),(f.C2,'40:6','42:6'),(f.SEQUENCE,'38:1','42:6'),(f.FINAL,'42:7','42:17')])

    def test_peer_reverse_is_duplicate(self):
        m,s=deepcopy(self.m),deepcopy(self.s)
        q=deepcopy(s['human']['positive_relations'][0]);q['source_node'],q['target_node']=q['target_node'],q['source_node']
        s['human']['positive_relations'].append(q)
        aa=f.actions(s,f.groups(s))
        self.assertEqual(sum(r['action']=='NO_ACTION_DUPLICATE' for r in aa),1)
        self.assertEqual(sum(r['action']=='CREATED' and r['relation_type']==f.PEER for r in aa),1)

    def test_existing_group_reused(self):
        s=deepcopy(self.s);g=deepcopy(s['human']['groups'][0])
        s['files']['test_composition_groups.csv']=f.util.csv_bytes([g])
        self.assertEqual(f.groups(s)[0]['action'],'CONFIRMED_EXISTING')

    def test_equivalent_group_other_id_stops(self):
        s=deepcopy(self.s);g=deepcopy(s['human']['groups'][0]);g['group_id']='OTHER_CANONICAL_ID'
        s['files']['test_composition_groups.csv']=f.util.csv_bytes([g])
        with self.assertRaisesRegex(ValueError,'canonical mapping'):f.groups(s)

    def test_existing_peer_reused(self):
        s=deepcopy(self.s);q=deepcopy(s['human']['positive_relations'][0])
        q.update(action='CREATED',canonical_relation_id='EXISTING:PEER')
        s['files']['test_relation_actions.csv']=f.util.csv_bytes([q])
        aa=f.actions(s,f.groups(s));r=next(r for r in aa if r['relation_type']==f.PEER)
        self.assertEqual((r['action'],r['canonical_relation_id']),('CONFIRMED_EXISTING','EXISTING:PEER'))

    def test_missing_exact_node_stops(self):
        s=deepcopy(self.s);s['human']['groups'][0]['members'][0]='GUESSED'
        with self.assertRaisesRegex(ValueError,'unknown member'):f.groups(s)

    def test_challenge_anchors_not_nodes(self):
        for ref in ('38:3','40:7'):
            ee=[r['original_record'] for r in self.m['evidence'] if r['original_record']['reference']==ref]
            self.assertTrue(any(r['repeated_challenge'] for r in ee))
            self.assertFalse(any(n['reference_start']==ref for n in self.m['facts']))

    def test_negative_parent_directions(self):
        for r in [e['original_record'] for e in self.m['evidence'] if e['original_record']['reference']=='42:6']:
            pairs={(n['source_node'],n['target_node']) for n in self.m['negative'] if n['relation_type']=='NO_DIRECT_PARENTAGE'}
            self.assertIn((r['evidence_id'],'H:HSA030'),pairs);self.assertIn(('H:HSA030',r['evidence_id']),pairs)

    def test_continuation_and_reverse_parent_rejected(self):
        for rel,reverse in [('CONTINUES_WITHIN',False),('CHILD_OF',True)]:
            m=deepcopy(self.m);src,tgt=six(m),'H:HSA030'
            if reverse:src,tgt=tgt,src
            add_relation(m,src,tgt,rel)
            self.assertEqual(next(g['status'] for g in f.gates(m,self.s) if g['gate']=='NO_42_6_42_7_PARENTAGE'),'FAIL')

    def test_no_fake_resolution(self):
        c=f.counts(self.m)
        self.assertEqual((c['resolved_by_F'],c['resolved_by_G'],c['remaining_direct_parent_questions']),(0,0,57))
        self.assertEqual(c['crosswalk'],{'REMAINS_UNRESOLVED':6,'NOT_APPLICABLE_TO_APPROVED_DECISION':51})

    def test_ana_deferred_and_accepted(self):
        aq={r['review_question_id']:r for r in self.m['ana']}
        self.assertEqual((aq['ANA-Q3']['status'],aq['ANA-Q3']['decision_type']),('UNRESOLVED','HUMAN_DEFERRED'))
        for q in ('ANA-Q2','ANA-Q4','ANA-Q5'):self.assertEqual(aq[q]['status'],'ACCEPTED')

    def test_temporal_three_distinctions(self):
        dd={r['reference']:r['DIFFERENCE'] for r in self.m['comparison']}
        self.assertEqual([dd[r]['phrase_function'] for r in ('3:1','42:7','42:16')],['Time','Conj','Time'])
        self.assertTrue(dd['42:16']['after_first_verb'])

    def test_summary_layered_and_deferred(self):
        for token in ('not a fully resolved textual tree','CHILD_OF','CONTINUES_WITHIN','SAME_LEVEL_SIBLING','ANA-Q3','UNRESOLVED','2:11–42:9','R4.4'):
            self.assertIn(token,self.m['summary'])

    def test_all_source_links_resolve(self):
        records=self.m['evidence']+self.m['criteria']+self.m['crosswalk']+self.m['adjudications']
        records += [r for r in self.m['actions']+self.m['all_seams'] if 'source_member' in r]
        for r in records:
            b=self.files[r['source_member']];rr=f.d.h.raw_rows(b)[int(r['source_data_row'])-1]
            self.assertEqual(rr[r['source_identity_field']],r['source_identity'])
            self.assertEqual(f.sha(b),r['source_member_sha256']);self.assertEqual(f.d.h.f.rowhash(rr),r['source_row_sha256'])

    def test_input_tamper_stops(self):
        ff=dict(self.s['files']);ff['12_gates.csv']+=b'changed'
        with self.assertRaisesRegex(ValueError,'manifests'):f.audit(ff,self.s['cfg'],self.s['receipt']['sha256'],True)

    def test_input_failed_gate_even_resealed_stops(self):
        ff=dict(self.s['files']);gg=deepcopy(f.rows(ff['12_gates.csv']));gg[0]['status']='FAIL';ff['12_gates.csv']=f.util.csv_bytes(gg);f.seal(ff)
        with self.assertRaisesRegex(ValueError,'FG-PREP gates'):f.audit(ff,self.s['cfg'],self.s['receipt']['sha256'],True)

    def test_prior_frozen_tamper_even_resealed_stops(self):
        ff=dict(self.s['files']);rr=deepcopy(f.rows(ff[f.ABC]));rr[0]['status']='UNREVIEWED';ff[f.ABC]=f.util.csv_bytes(rr);f.seal(ff)
        with self.assertRaises(ValueError):f.audit(ff,self.s['cfg'],self.s['receipt']['sha256'],True)


def negative_test(gate,mutation):
    def test(self):
        m,s=deepcopy(self.m),deepcopy(self.s);mutation(m,s)
        self.assertEqual(next(r['status'] for r in f.gates(m,s) if r['gate']==gate),'FAIL')
    return test


for _gate,_mutation in MUTATIONS.items():
    setattr(FGFinalTests,'test_negative_'+_gate.lower(),negative_test(_gate,_mutation))


if __name__=='__main__':unittest.main()
