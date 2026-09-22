import ast
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa2_closure_audit as h
from milal_hsa2_synthetic import source


class Audit(unittest.TestCase):
    def setUp(self):
        self.s,self.rows,self.md=source();self.m=h.build(self.s,self.rows,self.md)

    def test_all_gates(self):
        self.assertTrue(all(r['status']=='PASS' for r in h.gates(self.m,self.s)))

    def test_human_files_equivalent_lf(self):
        self.assertEqual(h.CSV.read_bytes(),h.registry_bytes(h.registry()))
        self.assertNotIn(b'\r\n',h.CSV.read_bytes())
        self.assertIn(h.registry_markdown(h.registry()),h.MD.read_text(encoding='utf-8'))

    def test_duplicate_reference_distinct_human_functions(self):
        for ref in ('4:1','15:1','22:1'):
            rows=[r for r in self.rows if r['reference_start']==ref]
            self.assertEqual(len(rows),2);self.assertEqual(len({r['judgment_id'] for r in rows}),2)
            self.assertEqual({r['structural_function'] for r in rows},{'SPEECH_UNIT_ONSET','DIALOGUE_CYCLE_ONSET'})

    def test_two_dimensions_can_coexist_without_collapsing(self):
        rows=deepcopy(self.m['candidates'])
        rows[0]['selected_relation']='DIRECT_LOCAL_CLOSURE'
        rows[2]['selected_relation']='TERMINATES_ENCLOSING_GROUP'
        self.assertTrue(h.candidate_model_valid(rows))
        self.assertEqual(self.m['candidates'][0]['selected_relation'],'UNRESOLVED')

    def test_candidate_targets_independent_of_native_proximity(self):
        baseline=h.candidates(self.s['cfg2'])
        self.s['atom_index']={a:-i for a,i in self.s['atom_index'].items()}
        self.assertEqual(h.candidates(self.s['cfg2']),baseline)
        self.s['catalog'].clear()
        self.assertEqual(h.candidates(self.s['cfg2']),baseline)

    def test_no_closure_candidate_is_a_direct_human_pair(self):
        self.assertFalse(any(p['reference']=='31:40' for p in self.m['pairs']))
        self.assertEqual(len(self.m['pairs']),83)

    def test_edge_classification_not_reference_guessing(self):
        self.assertEqual(h.edge_labels(4,7,5,6),['CROSSES_START_EDGE','CROSSES_END_EDGE'])
        self.assertEqual(h.edge_labels(5,6,5,6),['STARTS_AT_MARKER_START','ENDS_AT_MARKER_END','WITHIN_MARKER_SPAN'])
        self.assertEqual(h.edge_labels(0,4,5,6),[])
        self.assertEqual(h.edge_labels(7,9,5,6),[])

    def test_ending_marker_span_not_full_verse(self):
        scope=next(r for r in self.m['scopes'] if r['reference']=='31:40')
        self.assertEqual(len(scope['atom_ids']),1)
        self.assertEqual(len(self.s['catalog']['HSA2:PANEL:31:40']['atom_ids']),3)

    def test_discontinuous_clause_does_not_reorder_native_atoms(self):
        native=[{'atom_ids':[10,30]},{'atom_ids':[20]}]
        signatures=[dict(atom_node=str(a),source=json.dumps({'source_row':{'atom_node':str(a),'atom_index_1based':str(i)}})) for a,i in [(30,3),(10,1),(20,2)]]
        ordered,positions=h.native_geometry(native,signatures)
        self.assertEqual(ordered,[10,20,30]);self.assertEqual(positions,{10:0,20:1,30:2})

    def test_conflicting_native_index_rejected(self):
        signatures=[dict(atom_node='10',source=json.dumps({'source_row':{'atom_node':'10','atom_index_1based':str(i)}})) for i in (1,2)]
        with self.assertRaisesRegex(ValueError,'conflicting native index'):h.native_geometry([{'atom_ids':[10]}],signatures)

    def test_comparison_endings_include_full_verse_even_with_csf(self):
        scopes=[r for r in self.m['scopes'] if r['reference']=='2:10']
        self.assertEqual({r['scope_type'] for r in scopes},{'EXACT_MR1_EVENT','FULL_VERSE_HUMAN_COMPARISON_NOT_MR1'})

    def test_lexical_presence_not_semantic_equivalence(self):
        self.assertEqual({r['reference']:r['mashal_present'] for r in self.m['lexical']},{'27:1':True,'29:1':True,'31:40':False})
        self.assertTrue(all('NO_SEMANTIC_EQUIVALENCE' in r['status'] for r in self.m['lexical']))

    def test_unresolved_link_rejected_without_fuzzy_fallback(self):
        self.rows[0]['source_evidence_ids']='["NEARLY_SAME_HEBREW_TEXT"]'
        with self.assertRaisesRegex(ValueError,'unresolved exact ID'):h.build(self.s,self.rows,self.md)

    def test_no_source_writes(self):
        paths=[h.CSV,h.MD,h.h1.CSV,h.h1.MD];before=[p.read_bytes() for p in paths]
        h.serialize(self.m,self.s)
        self.assertEqual(before,[p.read_bytes() for p in paths])

    def test_manifest_negative(self):
        files=h.serialize(self.m,self.s);files['03_closure_target_candidate_relations.csv']+=b'bad'
        self.assertEqual(h.h1.util.manifest_gate(files)['status'],'FAIL')

    def test_independent_rerun_and_publication(self):
        files=h.serialize(self.m,self.s)
        self.assertEqual(files,h.serialize(h.build(self.s,self.rows,self.md),self.s))
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b';h.publish(files,a);h.publish(files,b)
            self.assertEqual((Path(tmp)/'a_results.zip').read_bytes(),(Path(tmp)/'b_results.zip').read_bytes())
            with self.assertRaisesRegex(ValueError,'output exists'):h.publish(files,a)


def row(m,ident):return next(r for r in m['judgments'] if r['judgment_id']==ident)
def change_row(ident,key,value):return lambda m,s:row(m,ident).__setitem__(key,value)
def receipt(m,s):s['frozen_receipts'][0]['actual']='bad'
def mr1(m,s):next(r for r in s['frozen_receipts'] if 'mr1' in r['path'])['actual']='bad'
def scope(m,s):next(r for r in m['scopes'] if r['reference']=='1:22')['scope_type']='EXACT_MR1_EVENT'
def link(m,s):m['links'][0]['source_locator']['row_sha256']='bad'
def lexical(m,s):m['lexical'][-1]['mashal_present']=True
def peer(m,s):row(m,'HSA2-C1-S1')['hierarchy_relation']='CHILD_OF'


MUTATIONS={
 'ALL_HUMAN_JUDGMENTS':change_row('HSA2-INITIAL','structural_function','NO_BOUNDARY'),
 'HSA1_AND_FROZEN_CORES_UNCHANGED':receipt,
 'CYCLE_1_SPEECH_UNITS':change_row('HSA2-C1-S2','human_speaker','Invented'),
 'CYCLE_2_SPEECH_UNITS':change_row('HSA2-C2-S2','human_speaker','Invented'),
 'CYCLE_3_SPEECH_UNITS':change_row('HSA2-C3-S2','human_speaker','Invented'),
 'NO_SYNTHETIC_ZOPHAR_III':change_row('HSA2-C3-S4','human_speaker','Zophar'),
 'CYCLE_ONSET_PEERS':change_row('HSA2-CYCLE-2','hierarchy_relation','CHILD_OF'),
 'INDIVIDUAL_SPEECH_PEERS':peer,
 '26_1_THIRD_CYCLE':change_row('HSA2-C3-S4','human_group','POST_DIALOGUE_JOB'),
 '27_1_DISTINCT_FORMULA':change_row('HSA2-JOB-27','higher_order_function','DIALOGUE_CYCLE_ONSET'),
 '27_29_SAME_LEVEL':change_row('HSA2-JOB-29','hierarchy_relation','CHILD_OF'),
 '28_1_NO_BOUNDARY':change_row('HSA2-NO-28','structural_function','SPEECH_UNIT_ONSET'),
 '31_40_ENDING_RETAINED':change_row('HSA2-END-31','structural_function','NO_BOUNDARY'),
 'DIRECT_TARGET_UNRESOLVED':change_row('HSA2-END-31','direct_closure_target','29:1'),
 'NO_NEAREST_OPENING_CHOICE':lambda m,s:m['candidates'][0].update(selected_relation='DIRECT_LOCAL_CLOSURE',direct_closure_target='29:1'),
 'LOCAL_AND_HIGHER_SEPARATE':lambda m,s:m['candidates'][-1].update(dimension='DIRECT_CLOSURE_TARGET'),
 'HUMAN_ENDINGS_NOT_MR1':scope,
 'MR1_RULES_UNCHANGED':mr1,
 'NO_WHOLE_BOOK_HIERARCHY':lambda m,s:m['pairs'].append(dict(reference='31:40',related_reference='29:1',related_judgment_id='',relation='CLOSES')),
 'NO_SCORE_RANK':lambda m,s:m['candidates'][0].update(score=1),
 'EXACT_SOURCE_LINKS':link,
 'FORMAL_EDGES_EXACT':lambda m,s:m['edges'].pop(),
 'NATIVE_ATOM_ORDER_EXACT':lambda m,s:s['native_order'].reverse(),
 'LEXICAL_FACTS_ONLY':lexical,
 '11_4_INTERNAL_PRESERVED':change_row('HSA2-INTERNAL-11-4','structural_function','SPEECH_UNIT_ONSET'),
 'HUMAN_MD_CSV_MATCH':lambda m,s:m.update(markdown='changed'),
 'DIRECT_TARGET_IDS_EXACT':lambda m,s:m['pairs'][0].update(related_judgment_id='MISSING'),
 'REPORTS_AND_CONTROLS_PRESERVED':lambda m,s:m.update(audit='automatic chosen target 29:1'),
 'ACCEPTED_ARCHIVE_PINS':lambda m,s:s['receipts'][0].update(sha256='bad'),
 'DETERMINISTIC_OUTPUT':lambda m,s:m['links'].reverse(),
}


def negative_test(gate,mutation):
    def test(self):
        mutation(self.m,self.s)
        self.assertEqual(next(r['status'] for r in h.gates(self.m,self.s) if r['gate']==gate),'FAIL')
    return test


for gate,mutation in MUTATIONS.items():setattr(Audit,'test_negative_'+gate.lower(),negative_test(gate,mutation))


class Coverage(unittest.TestCase):
    def test_every_gate_has_negative(self):
        s,rows,md=source();m=h.build(s,rows,md)
        self.assertEqual({r['gate'] for r in h.gates(m,s)},set(MUTATIONS))


if __name__=='__main__':unittest.main()
