from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_layer_0_1 as l


def proposal(m,cat):return next(r for r in m['proposals'] if r['proposed_category']==cat)
def relation(m,layer):return next(r for r in m['relations'] if r['layer']==layer)


MUTATIONS={
 'BASELINE_COMMIT_VERIFIED':lambda m,s:m['commit'].update(verified_commit='wrong'),
 'INPUT_FG_VERIFIED':lambda m,s:m['receipt'].update(sha256='wrong'),
 'ALL_A_G_FROZEN':lambda m,s:m['seams'][0].update(status='UNREVIEWED'),
 'ANA_PRESERVED':lambda m,s:relation(m,'OVERLAY_RESPONSIO').update(source_status='UNRESOLVED'),
 'HSA2_F_PRESERVED':lambda m,s:m['historical'].update({l.EDGES:b'changed'}),
 'ORIGINAL_57_LOSSLESS':lambda m,s:m['unresolved'][0]['original_record'].update(direct_parent='GUESSED'),
 'TRIAGE_COUNTS_EXACT':lambda m,s:m['proposals'][0].update(historical_triage='GUESSED'),
 'NO_ROW_DROPPED':lambda m,s:m['proposals'].pop(),
 'ONE_PROPOSAL_PER_ROW':lambda m,s:m['proposals'].append(deepcopy(m['proposals'][0])),
 'ALL_PROPOSALS_UNREVIEWED':lambda m,s:m['proposals'][0].update(proposal_status='ACCEPTED'),
 'NO_NEW_HUMAN_JUDGMENT':lambda m,s:m['new_human_judgments'].append('ACCEPTED'),
 'NO_NEW_STRUCTURAL_RELATION':lambda m,s:m['new_structural_relations'].append('CHILD_OF'),
 'NO_NEW_COMPOSITION_RELATION':lambda m,s:m['new_composition_relations'].append('GROUP_MEMBER_OF'),
 'NON_TEXTUAL_GROUPS_STAY_NON_TEXTUAL':lambda m,s:m['groups'][0].update(textual=True),
 'ROLE_ALIASES_EXPLICIT':lambda m,s:m['roles'][0].update(canonical_textual_node='NEAREST'),
 'MEMBERSHIP_NOT_PARENTAGE':lambda m,s:m['proposals'][0].update(direct_parent='CYCLE_1'),
 'LOCAL_RELATION_NOT_REWRITTEN':lambda m,s:proposal(m,l.P4).update(local_relation_ids=[]),
 'CONTAINER_NO_HIDDEN_PARENT':lambda m,s:proposal(m,l.P5).update(direct_parent_resolved=True),
 'GLOBAL_LAYER_PROPOSAL_GROUNDED':lambda m,s:proposal(m,l.P6).update(seam_id='GUESSED'),
 'P7_CONSERVATIVE_REMAINDER':lambda m,s:proposal(m,l.P7).update(proposed_category=l.P6),
 'Q3_STILL_DEFERRED':lambda m,s:next(r for r in m['unresolved'] if r['question_id']=='ANA-Q3').update(status='ACCEPTED'),
 'PARTICIPANT_ARC_UNADJUDICATED':lambda m,s:m['participant_frames'].append('2:11–42:9'),
 'NO_42_10_PROMOTION':lambda m,s:m['nodes'].append(dict(node_id='42:10',node_kind='TEXTUAL_NODE',provenance=[],accepted_annotations=[])),
 'ACCEPTED_ANNOTATIONS_PRESERVED':lambda m,s:next(r for r in m['nodes'] if r['accepted_annotations']).update(accepted_annotations=[]),
 'NO_R4_4_IMPLEMENTATION':lambda m,s:m.update(r44_started=True),
 'ALL_RELATION_LAYERS_LOSSLESS':lambda m,s:m['relations'].pop(),
 'NO_LAYER_COLLAPSE':lambda m,s:relation(m,'COMPOSITION_GROUPING').update(layer='TEXTUAL_HIERARCHY'),
 'PROVENANCE_PRESERVED':lambda m,s:m['relations'][0].update(provenance=[]),
 'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m,s:m['historical'].update({l.ALIASES:b'changed'}),
 'PROPOSALS_REPRODUCIBLE':lambda m,s:m['proposals'][0].update(rationale='invented'),
 'MATRIX_SOURCE_GROUNDED':lambda m,s:m['matrix'][0].update(TEXTUAL_HIERARCHY=['invented']),
 'REPORTS_FAITHFUL':lambda m,s:m['reports'].update(packet='All approved'),
 'FROZEN_REPOSITORY_PINS':lambda m,s:s['frozen'][0].update(actual='wrong'),
 'REQUEST_SOURCE_EXACT':lambda m,s:s.update(request=b'wrong'),
 'DETERMINISTIC_RERUN':lambda m,s:m.update(rerun_digest='wrong'),
}


class LayerAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=l.load(True);cls.m=l.build(cls.s);cls.files=l.serialize(cls.m,cls.s)

    def test_gate_negative_coverage(self):self.assertEqual(set(MUTATIONS),{r['gate'] for r in l.gates(self.m,self.s)})
    def test_all_gates_pass(self):self.assertTrue(all(r['status']=='PASS' for r in l.rows(self.files['17_gates.csv'])))
    def test_manifest_negative(self):
        ff=dict(self.files);ff['10_parentage_necessity_audit.csv']+=b'changed';self.assertFalse(l.util.manifest_ok(ff))
    def test_independent_build(self):self.assertEqual(self.files,l.serialize(l.build(deepcopy(self.s)),deepcopy(self.s)))
    def test_exact_baseline(self):self.assertEqual(self.s['commit']['verified_commit'],'45a23a833d98c1e6aa7f37824d98ac6c85768fa4')
    def test_triage_regression(self):
        self.assertEqual(l.counts(self.m)['original_triage'],self.s['cfg']['regression']['triage'])
        self.assertEqual(len(self.m['proposals']),57)
    def test_proposal_regression_not_resolution(self):
        self.assertEqual(l.counts(self.m)['proposed_categories'],{l.P2:8,l.P3:6,l.P4:10,l.P5:19,l.P6:13,l.P7:1})
        self.assertEqual(l.counts(self.m)['p7_nodes'],['H:HSA012'])
        self.assertTrue(all(r['direct_parent']=='UNRESOLVED' and not r['direct_parent_resolved'] for r in self.m['proposals']))
    def test_human_fields_blank(self):
        for r in self.m['proposals']:
            for k in l.REVIEW_FIELDS:self.assertEqual(r[k],'UNREVIEWED' if k=='review_status' else '')
    def test_three_role_pairs_six_rows_no_merge(self):
        self.assertEqual(len(self.m['roles']),6);self.assertEqual(sum(r['is_role_alias'] for r in self.m['roles']),3)
        for r in self.m['roles']:
            self.assertIn(r['canonical_textual_node'],r['paired_node_ids']);self.assertFalse(r['historical_records_merged'])
        speech=[n for n in self.m['nodes'] if n['node_id'] in {r['canonical_textual_node'] for r in self.m['roles']}]
        self.assertTrue(all(n['node_kind']=='TEXTUAL_NODE' and n['textual'] for n in speech))
    def test_role_identity_not_reference_similarity(self):
        s=deepcopy(self.s);rr=deepcopy(l.rows(s['files'][l.ALIASES]));rr[0]['identity_basis']='SAME_VERSE_ONLY';s['files'][l.ALIASES]=l.util.csv_bytes(rr)
        with self.assertRaisesRegex(ValueError,'unverified role identity'):l.role_crosswalk(s)
    def test_role_shared_evidence_required(self):
        s=deepcopy(self.s);rr=deepcopy(l.rows(s['files'][l.ALIASES]));rr[0]['shared_source_evidence_ids']=[];s['files'][l.ALIASES]=l.util.csv_bytes(rr)
        with self.assertRaisesRegex(ValueError,'unverified role identity'):l.role_crosswalk(s)
    def test_nontextual_classification_uses_schema(self):
        s=deepcopy(self.s);rr=deepcopy(l.rows(s['files'][l.NODES]));r=next(r for r in rr if r['node_id']=='CYCLE_1');r['structural_function']='UNKNOWN';s['files'][l.NODES]=l.util.csv_bytes(rr)
        rels=l.relations(s);roles=l.role_crosswalk(s);nn=l.nodes(s,roles,rels);pp=l.proposals(s,nn,rels,roles)
        self.assertNotEqual(next(r for r in pp if r['node_id']=='CYCLE_1')['proposed_category'],l.P2)
    def test_container_needs_peer_support(self):
        rr=[r for r in self.m['relations'] if not(r['layer']=='TEXTUAL_SAME_LEVEL' and 'H:HSA015' in (r['source_node'],r['target_node']))]
        pp=l.proposals(self.s,self.m['nodes'],rr,self.m['roles'])
        self.assertEqual(next(r for r in pp if r['node_id']=='H:HSA015')['proposed_category'],l.P7)
    def test_container_needs_membership(self):
        rr=[r for r in self.m['relations'] if not(r['relation_type']=='GROUP_MEMBER_OF' and r['source_node']=='H:HSA020')]
        pp=l.proposals(self.s,self.m['nodes'],rr,self.m['roles'])
        self.assertEqual(next(r for r in pp if r['node_id']=='H:HSA020')['proposed_category'],l.P7)
    def test_local_category_needs_local_edge(self):
        rr=[r for r in self.m['relations'] if 'H:HSA001' not in (r['source_node'],r['target_node'])]
        pp=l.proposals(self.s,self.m['nodes'],rr,self.m['roles'])
        self.assertEqual(next(r for r in pp if r['node_id']=='H:HSA001')['proposed_category'],l.P7)
    def test_p7_not_hardcoded_to_friends(self):
        rr=deepcopy(self.m['relations']);rr.append(dict(relation_id='SYN:PEER',source_node='H:HSA012',target_node='H:HSA013',relation_type='SAME_LEVEL_SIBLING',layer='TEXTUAL_SAME_LEVEL'))
        pp=l.proposals(self.s,self.m['nodes'],rr,self.m['roles'])
        self.assertEqual(next(r for r in pp if r['node_id']=='H:HSA012')['proposed_category'],l.P6)
        # This isolated rule test does not add the synthetic edge to a valid output.
    def test_no_direct_parent_conversion(self):
        old=l.rows(self.s['files'][l.EDGES]);oldparents=[r['edge_id'] for r in old if r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE')]
        now=[r['relation_id'] for r in self.m['relations'] if r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE')]
        self.assertEqual(sorted(oldparents),sorted(now));self.assertEqual(len(now),3)
    def test_typed_local_relations_remain_distinct(self):
        rr=[r for r in self.m['relations'] if r['layer']=='TEXTUAL_HIERARCHY']
        self.assertEqual({r['relation_type'] for r in rr},{'CHILD_OF','HIERARCHICALLY_ABOVE','CONTINUES_WITHIN','DIRECT_LOCAL_CLOSURE'})
    def test_technical_edges_separate(self):
        rr=[r for r in self.m['relations'] if r['layer']=='TECHNICAL_NAVIGATION'];self.assertEqual(len(rr),57)
        self.assertTrue(all(r['human_or_automatic']=='AUTOMATIC_TECHNICAL' for r in rr))
    def test_source_automatic_derivation_not_human_promotion(self):
        rr=[r for r in self.m['relations'] if r['human_or_automatic']=='AUTOMATIC_DERIVED_FROM_HUMAN'];self.assertEqual(len(rr),8)
    def test_q3_not_accepted_overlay(self):
        self.assertNotIn('ANA-H3',{r['relation_id'] for r in self.m['relations']})
        r=next(r for r in self.m['unresolved'] if r['question_id']=='ANA-Q3');self.assertEqual(r['original_record']['decision_type'],'HUMAN_DEFERRED')
    def test_ana_q2_dimension_preserved(self):
        r=next(r for r in self.m['relations'] if r['relation_id']=='ANA-H2')
        self.assertEqual((r['layer'],r['original_dimension']),('TRANSITION','TRANSITION_OVERLAY'))
    def test_confirmation_provenance_not_duplicate_relation(self):
        ids=[r['relation_id'] for r in self.m['relations']];self.assertEqual(len(ids),len(set(ids)))
        self.assertTrue(any(len(r['provenance'])>1 for r in self.m['relations']))
    def test_all_layer_outputs_partition(self):
        projected=[r for n in l.LAYERS for r in l.rows(self.files[n])]
        self.assertEqual(sorted(r['relation_id'] for r in projected),sorted(r['relation_id'] for r in self.m['relations']))
    def test_lossless_history_and_manifests(self):
        self.assertTrue(all(self.files[l.HISTORY+n]==b for n,b in self.s['files'].items()))
        self.assertTrue(all(r['valid'] for r in l.d.h.nested_manifests(self.files)))
    def test_provenance_resolves(self):
        for r in self.m['relations']+self.m['nodes']+self.m['proposals']+self.m['unresolved']:
            for p in r['provenance']:
                b=self.files[p['member']];raw=l.d.h.raw_rows(b)[int(p['data_row'])-1]
                self.assertEqual(raw[p['identity_field']],p['identity']);self.assertEqual(l.d.h.f.rowhash(raw),p['row_sha256']);self.assertEqual(l.sha(b),p['member_sha256'])
    def test_unknown_relation_type_stops(self):
        s=deepcopy(self.s);rr=deepcopy(l.rows(s['files'][l.EDGES]));rr[0]['relation_type']='GUESS';s['files'][l.EDGES]=l.util.csv_bytes(rr)
        with self.assertRaisesRegex(ValueError,'unmapped relation'):l.relations(s)
    def test_historical_triage_drift_rejected(self):
        ff=dict(self.s['files']);rr=deepcopy(l.rows(ff[l.TRIAGE]));rr[0]['triage_category']='WRONG';ff[l.TRIAGE]=l.util.csv_bytes(rr);l.f.seal(ff)
        with self.assertRaises(ValueError):l.input_audit(ff,self.s['cfg'],self.s['receipt']['sha256'],True)
    def test_reports_include_methodology(self):
        for sentence in l.STATEMENTS:self.assertIn(sentence,self.m['reports']['necessity'])
        self.assertIn('not proof',self.m['reports']['necessity'])
        self.assertIn('not an executed R4.4 validation',self.m['reports']['readiness'])
    def test_matrix_nested_composition_keeps_textual_evidence(self):
        r=next(r for r in self.m['matrix'] if r['node_id']=='YHWH_JOB_RESPONSE_SEQUENCE')
        self.assertTrue(r['TEXTUAL_HIERARCHY']);self.assertTrue(r['TEXTUAL_SAME_LEVEL'])
        self.assertIn('H:HSA025',{x['node_id'] for x in r['onset_terminal_functions']})
        self.assertTrue(r['explicit_membership_context_relation_ids'])
    def test_later_human_labels_spans_are_integrated(self):
        nn={r['node_id']:r for r in self.m['nodes']}
        self.assertEqual(nn['H:HSA012']['accepted_annotations'][0]['original_record']['span_end'],'2:13')
        self.assertEqual(nn['H:HSA013']['accepted_annotations'][0]['original_record']['label'],'INITIAL_JOB_SPEECH')
        self.assertEqual(nn['H:HSA027']['accepted_annotations'][0]['original_record']['span_end'],'40:5')
        self.assertEqual(nn['H:HSA029']['accepted_annotations'][0]['original_record']['span_end'],'42:6')
        self.assertEqual(nn['ELIHU_SPEECH_SEQUENCE']['accepted_annotations'][0]['original_record']['group_scope'],'32:6–37:24')


def negative(gate,mutate):
    def test(self):
        m,s=deepcopy(self.m),deepcopy(self.s);mutate(m,s)
        self.assertEqual(next(r['status'] for r in l.gates(m,s) if r['gate']==gate),'FAIL')
    return test


for _gate,_mutation in MUTATIONS.items():setattr(LayerAuditTests,'test_negative_'+_gate.lower(),negative(_gate,_mutation))

if __name__=='__main__':unittest.main()
