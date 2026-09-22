import ast
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_r4_3_hierarchy_scaffold as r


def node(m,ident):return next(n for n in m['nodes'] if n['node_id']==ident)
def edit_node(ident,**changes):return lambda m,s:node(m,ident).update(changes)
def frozen(path):return lambda m,s:next(x for x in s['frozen'] if x['path']==path).update(actual='bad')
def edge(m,a,b,kind):return next(e for e in m['edges'] if e['source_node']==a and e['target_node']==b and e['relation_type']==kind)
def remove_edge(a,b,kind):return lambda m,s:m['edges'].remove(edge(m,a,b,kind))
def false_parent(m,s,a='H:HSA025',b='H:HSA024',kind='CHILD_OF'):
    e=deepcopy(next(e for e in m['edges'] if e['edge_class']=='HIERARCHY'))
    e.update(edge_id='INVENTED',source_node=a,target_node=b,relation_type=kind,edge_class='HIERARCHY')
    m['edges'].append(e)


MUTATIONS={
 'HSA1_FROZEN':frozen('docs/HUMAN_STRUCTURAL_ADJUDICATION.csv'),
 'HSA2_FROZEN':frozen('docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv'),
 'HSA2_F_FROZEN':frozen('docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv'),
 'HISTORICAL_UNRESOLVED_INTACT':lambda m,s:m['historical'].update({'extra':b'rewritten'}),
 'ACTIVE_FINAL_PRECEDENCE':remove_edge('H:HSA017','H:HSA016','DIRECT_LOCAL_CLOSURE'),
 '59_HUMAN_RECORDS_ACCOUNTED':lambda m,s:m['accounting'].pop(),
 'EVERY_NODE_PROVENANCE':edit_node('H:HSA001',source_judgment_ids=[]),
 'EVERY_NONTECH_EDGE_PROVENANCE':lambda m,s:next(e for e in m['edges'] if e['edge_class']=='HIERARCHY').update(source_judgment_ids=[]),
 'DERIVED_GROUP_PROVENANCE':edit_node('DIALOGUE_CYCLE_SEQUENCE',derived_from_judgments=[]),
 'CYCLE_1_MEMBERS':remove_edge('H:HSA2-C1-S1','CYCLE_1','GROUP_MEMBER_OF'),
 'CYCLE_2_MEMBERS':remove_edge('H:HSA2-C2-S1','CYCLE_2','GROUP_MEMBER_OF'),
 'CYCLE_3_MEMBERS':remove_edge('H:HSA2-C3-S1','CYCLE_3','GROUP_MEMBER_OF'),
 'NO_ZOPHAR_III':lambda m,s:m['nodes'].append(dict(deepcopy(m['nodes'][0]),node_id='ZOPHAR_III')),
 'CYCLE_ONSET_PEERS':remove_edge('H:HSA2-CYCLE-1','H:HSA2-CYCLE-2','SAME_LEVEL_SIBLING'),
 '27_29_PEERS':remove_edge('H:HSA015','H:HSA016','SAME_LEVEL_SIBLING'),
 '28_CONTINUATION':remove_edge('H:HSA2-NO-28','H:HSA015','CONTINUES_WITHIN'),
 'THREE_FINAL_CLOSURE_RELATIONS':remove_edge('H:HSA017','H:HSA015','NO_DIRECT_RELATION'),
 'LOCAL_HIGHER_SEPARATE':lambda m,s:edge(m,'H:HSA017','POST_DIALOGUE_JOB','TERMINATES_ENCLOSING_GROUP').update(edge_class='LOCAL_CLOSURE',dimension='DIRECT_CLOSURE_TARGET'),
 'ELIHU_FOUR_PEERS':remove_edge('H:HSA020','H:HSA021','SAME_LEVEL_SIBLING'),
 '40_1_CHILD_38_1':remove_edge('H:HSA026','H:HSA025','CHILD_OF'),
 'YHWH_PEERS':remove_edge('H:HSA025','H:HSA028','SAME_LEVEL_SIBLING'),
 'JOB_RESPONSE_PEERS':remove_edge('H:HSA027','H:HSA029','SAME_LEVEL_SIBLING'),
 '42_16_CONTINUATION':remove_edge('H:HSA031','H:HSA030','CONTINUES_WITHIN'),
 'NO_RESPONSE_TO_PARENT':lambda m,s:false_parent(m,s,'H:HSA025','H:HSA017','RESPONSE'),
 'NO_ADJACENCY_PARENT':false_parent,
 'UNRESOLVED_PARENTAGE_EXPLICIT':lambda m,s:m['unresolved'].pop(),
 'NO_PARENT_RANKING':lambda m,s:m['unresolved'][0].update(parent_score=0.9),
 'NO_NEW_MR1_RULE':frozen('src/milal_mr1_historical_rules.py'),
 'NO_HUMAN_MUTATION':lambda m,s:m['accounting'][0]['historical_record'].update(review_status='UNREVIEWED'),
 'TECHNICAL_ROOT_ONLY':edit_node('JOB_BOOK',textual_boundary=True),
 'GROUPS_NOT_TEXTUAL':edit_node('CYCLE_1',textual_boundary=True),
 'ELIHU_INTRO_NOT_PEER_OR_PARENT':remove_edge('H:HSA019','ELIHU_SPEECH_SEQUENCE','NARRATIVE_INTRODUCTION'),
 'NO_FICTIONAL_CLOSURE_SPANS':edit_node('H:HSA2-C1-S1',coverage_end='5:27'),
 'SOURCE_LINKS_LOSSLESS':lambda m,s:m['provenance'][0]['source_locator'].update(row_sha256='bad'),
 'EXACT_TYPED_RELATIONS':lambda m,s:edge(m,'H:HSA2-NO-28','H:HSA015','CONTINUES_WITHIN').update(edge_class='HIERARCHY'),
 'ACYCLIC_HIERARCHY':lambda m,s:false_parent(m,s,'H:HSA002','H:HSA003'),
 'NEGATIVE_CONTROLS':lambda m,s:m['negative'][0].update(status='FAIL'),
 'FROZEN_CORES':frozen('src/milal_r4_2_participant_audit.py'),
 'REPORT_NO_FALSE_PARENTAGE':lambda m,s:m.update(report='All nodes have settled parents'),
 'DETERMINISTIC_OUTPUT':lambda m,s:m.update(random_extra='unstable'),
}


class Scaffold(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source=r.load(True)
    def setUp(self):
        self.s=deepcopy(self.source);self.m=r.build(self.s)

    def test_gates_and_negative_coverage(self):
        gg=r.gates(self.m,self.s)
        self.assertEqual(set(MUTATIONS),{x['gate'] for x in gg})
        self.assertTrue(all(x['status']=='PASS' for x in gg))

    def test_manifest_negative(self):
        files=r.serialize(self.m,self.s);files['03_unresolved_parentage.csv']+=b'bad'
        self.assertEqual(r.h1.util.manifest_gate(files)['status'],'FAIL')

    def test_59_rows_61_nodes_not_59_boundaries(self):
        self.assertEqual(len(self.m['accounting']),59);self.assertEqual(len(self.m['nodes']),61)
        self.assertEqual(len([n for n in self.m['nodes'] if n['node_type']=='TECHNICAL_ROOT']),1)
        self.assertEqual(len([n for n in self.m['nodes'] if n['node_type']=='DERIVED_SCAFFOLD_GROUP']),2)

    def test_aliases_retain_every_original_record(self):
        byid={a['judgment_id']:a for a in self.m['accounting']}
        self.assertEqual(byid['HSA013']['scaffold_node_id'],byid['HSA2-INITIAL']['scaffold_node_id'])
        self.assertEqual(byid['HSA013']['historical_record']['structural_function'],'PARAGRAPH_ONSET')
        self.assertEqual(node(self.m,'H:HSA013')['all_historical_functions'],['PARAGRAPH_ONSET','SPEECH_UNIT_ONSET'])
        self.assertEqual(node(self.m,'H:HSA017')['source_judgment_ids'],['HSA017','HSA2-END-31','HSA2-F-01','HSA2-F-02','HSA2-F-03'])

    def test_exact_parent_set_only_three_assertions(self):
        self.assertEqual(dict(r.parents(self.m['edges'])),{'H:HSA003':{'H:HSA002'},'H:HSA026':{'H:HSA025'},'H:HSA014':{'H:HSA013'}})
        self.assertEqual(len(self.m['unresolved']),57)

    def test_group_membership_not_a_direct_parent(self):
        self.assertEqual(node(self.m,'H:HSA2-C1-S1')['parentage_status'],'UNRESOLVED')
        self.assertTrue(r.has(self.m,'H:HSA2-C1-S1','CYCLE_1','GROUP_MEMBER_OF'))
        self.assertFalse(r.has(self.m,'H:HSA2-C1-S1','CYCLE_1','CHILD_OF'))

    def test_continuation_not_a_direct_parent(self):
        self.assertTrue(r.has(self.m,'H:HSA004','H:HSA003','CONTINUES_WITHIN'))
        self.assertEqual(node(self.m,'H:HSA004')['direct_parent_ids'],[])

    def test_higher_closure_not_parent(self):
        self.assertTrue(r.has(self.m,'H:HSA017','POST_DIALOGUE_JOB','TERMINATES_ENCLOSING_GROUP'))
        self.assertEqual(node(self.m,'H:HSA017')['direct_parent_ids'],[])

    def test_initial_job_not_in_cycle_group(self):
        self.assertFalse(any(e['source_node']=='H:HSA013' and e['edge_class']=='MEMBERSHIP' for e in self.m['edges']))

    def test_11_4_stays_internal(self):
        self.assertEqual(node(self.m,'H:HSA2-INTERNAL-11-4')['structural_function'],'INTERNAL_SPEECH_EXPRESSION')
        self.assertTrue(r.has(self.m,'H:HSA2-INTERNAL-11-4','H:HSA2-C1-S5','CONTINUES_WITHIN'))

    def test_32_1_and_37_24_no_automatic_closure_or_parent(self):
        for ident in ('H:HSA018','H:HSA024'):
            self.assertEqual(node(self.m,ident)['parentage_status'],'UNRESOLVED')
        self.assertFalse(any(e['edge_class']=='LOCAL_CLOSURE' and e['source_node']=='H:HSA024' for e in self.m['edges']))

    def test_cycle_member_sequence_uses_supplied_order(self):
        for group in self.s['cfg']['groups']:
            actual=sorted((e['membership_position'],e['source_node']) for e in self.m['edges'] if e['edge_class']=='MEMBERSHIP' and e['target_node']==group['node_id'])
            mapping=r.maps(self.s)[1]
            self.assertEqual([n for _,n in actual],[mapping.get(i,i) for i in group['members']])
            positions=[self.m['report'].index(n+' |',self.m['report'].index('] '+group['node_id'])) for _,n in actual]
            self.assertEqual(positions,sorted(positions))

    def test_geometry_and_source_order_do_not_choose_parent(self):
        expected=dict(r.parents(self.m['edges']))
        self.s['links']=list(reversed(self.s['links']))
        self.s['enclosures']=[dict(participant_event_id='UNRELATED',frame_id='NO_PARENT')]
        self.assertEqual(dict(r.parents(r.compile_scaffold(self.s)[1])),expected)

    def test_source_missing_target_stops_no_fuzzy_fallback(self):
        entry=next(x for x in self.s['human'] if x['record']['judgment_id']=='HSA003')
        entry['record']['related_judgment_id_if_available']='["SIMILAR_HSA002"]'
        with self.assertRaisesRegex(ValueError,'missing exact related judgment'):
            r.compile_scaffold(self.s)

    def test_unbound_span_stops(self):
        self.s['cfg']['explicit_reference_targets'].pop('HSA001')
        with self.assertRaisesRegex(ValueError,'unbound explicit human span'):r.compile_scaffold(self.s)

    def test_output_history_byte_fidelity_and_provenance(self):
        files=r.serialize(self.m,self.s)
        self.assertEqual({k.removeprefix('history/'):v for k,v in files.items() if k.startswith('history/')},self.s['historical'])
        for p in self.m['provenance']:
            loc=p['source_locator'];row=r.table(self.s['historical'],loc['member'])[loc['data_row']-1]
            self.assertEqual(r.sha(r.canonical(row).encode()),loc['row_sha256'])

    def test_report_lists_every_unresolved_and_only_true_hierarchy(self):
        text=self.m['report']
        for u in self.m['unresolved']:self.assertIn('| '+u['node_id']+' |',text)
        self.assertEqual(text.count('[RESOLVED CHILD]'),3)
        self.assertIn('MEMBERSHIP ONLY',text)
        self.assertIn('UNRESOLVED GLOBAL SEAMS',text)
        self.assertNotIn('HUMAN_CHILD_OF JOB_BOOK',text)

    def test_deterministic_publication(self):
        files=r.serialize(self.m,self.s)
        self.assertEqual(files,r.serialize(r.build(self.s),self.s))
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b';r.publish(files,a);r.publish(files,b)
            self.assertEqual(a.with_name('a_results.zip').read_bytes(),b.with_name('b_results.zip').read_bytes())
            with self.assertRaisesRegex(ValueError,'output exists'):r.publish(files,a)

    def test_windows_runner_no_user_path_or_tf_reload(self):
        text=(r.ROOT/'scripts/run_milal_r4_3_windows.ps1').read_text(encoding='utf-8')
        self.assertIn('$PSScriptRoot',text);self.assertIn('$LASTEXITCODE',text)
        self.assertNotIn('C:\\Users',text);self.assertNotIn('--tf-data',text)


def negative(name,mutation):
    def test(self):
        mutation(self.m,self.s)
        self.assertEqual(next(x['status'] for x in r.gates(self.m,self.s) if x['gate']==name),'FAIL')
    return test


for name,mutation in MUTATIONS.items():setattr(Scaffold,'test_negative_'+name.lower(),negative(name,mutation))

if __name__=='__main__':unittest.main()
