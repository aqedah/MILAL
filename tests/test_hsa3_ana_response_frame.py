from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_ana_response_frame as a


def occurrence(m,ref):return next(r for r in m['inventory'] if r['reference']==ref)
def change(ref,**kw):return lambda m,s:occurrence(m,ref).update(kw)


MUTATIONS={
    'FROZEN_89_FILES':lambda m,s:s['frozen'][0].update(actual='bad'),
    'ACCEPTED_HISTORY_BYTE_IDENTICAL':lambda m,s:m['historical'].update({'03_global_seam_cases.csv':b'REVIEWED'}),
    'SOURCE_NODES_EDGES_UNCHANGED':lambda m,s:m['edges'].pop(),
    'FROZEN_HUMAN_JUDGMENTS':lambda m,s:m['accounting'].pop(),
    'UNRESOLVED_57_UNCHANGED':lambda m,s:m['unresolved'].pop(),
    'NO_NEW_HUMAN_JUDGMENT':lambda m,s:m['new_human_judgments'].append({'invented':True}),
    'NO_NEW_STRUCTURAL_RELATION':lambda m,s:m['new_structural_relations'].append({'relation_type':'RESPONSE_TO'}),
    'NATIVE_SNAPSHOT_INTACT':lambda m,s:m['native'][0]['words'][0].update(lex='BAD'),
    'WHOLE_BOOK_ANA_COVERAGE':lambda m,s:m['inventory'].pop(),
    'OCCURRENCE_FIELDS_SOURCE_EXACT':change('33:13',actor_identity='GOD'),
    'CONSTRUCTION_PARTITION':lambda m,s:m['classes'][0].update(count=999),
    'FOCUS_COMPLETE_SOURCE_EXACT':lambda m,s:m['focus'].pop(),
    'CANDIDATES_EXACT_FOUR':lambda m,s:m['candidates'].pop(),
    'NO_AUTOMATIC_CANDIDATE_RESOLUTION':lambda m,s:m['candidates'][0].update(automatic_resolution=True),
    'RESPONDER_IDENTITY_UNASSERTED':lambda m,s:m['candidates'][1].update(responder_identity_equivalence='SAME'),
    'NO_OCCURRENCE_PARENT_OR_RESPONSE':change('32:6',automatic_parent_ids=['FRIENDS']),
    'REVIEW_QUESTIONS_BLANK':lambda m,s:m['questions'][1].update(reviewer_notes='AI decision'),
    'SEAM_D_E_ADDENDUM_ONLY':lambda m,s:m['dependencies'][0].update(resolves_parentage=True),
    'EXACT_EVIDENCE_LINKS':lambda m,s:m['evidence'][0].update(source_row_sha256='bad'),
    'NEGATIVE_CONTROLS':lambda m,s:m['negative'].pop(),
    '3_2_FORMAL_NOT_SEMANTIC':change('3:2',automatic_response_to=['2:13']),
    '31_35_REQUEST_NOT_ACTUAL_RESPONSE':change('31:35',construction_class='SELF_DECLARED_RESPONSE'),
    '32_1_CESSATION_EXPLICIT_JOB':change('32:1',explicit_target_names=[]),
    '32_6_FORMAL_NO_PARENT':change('32:6',automatic_parent_ids=['32:1']),
    '36_1_NO_ANA_ADD_SPEECH':lambda m,s:next(f for f in m['focus'] if f['reference']=='36:1').update(status='ANA_PRESENT'),
    '38_1_DIRECTED_EXPLICIT_JOB':change('38:1',explicit_target_names=[]),
    'NO_ADJACENCY_ANTECEDENT':change('38:1',automatic_response_to=['37:24']),
    'HOMONYMS_RETAINED_NOT_ANSWER':change('37:23',answer_lexeme=True),
    'THREE_CLOSURE_RELATIONS_PRESERVED':lambda m,s:m['edges'].remove(next(e for e in m['edges'] if e['relation_type']=='DIRECT_LOCAL_CLOSURE')),
    'AUDIT_REPORT_FAITHFUL':lambda m,s:m.update(audit=m['audit']+'invented'),
    'REVIEW_PACKET_FAITHFUL':lambda m,s:m.update(review=m['review']+'reviewed'),
}


class AnaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source=a.load(self_test=True);cls.model=a.build(cls.source)

    def test_positive_gates_and_mutation_coverage(self):
        gg=a.gates(self.model,self.source)
        self.assertTrue(all(g['status']=='PASS' for g in gg));self.assertEqual(set(MUTATIONS),{g['gate'] for g in gg})

    def test_manifest_tamper_rejected(self):
        files=a.serialize(self.model,self.source);self.assertTrue(a.prep.r43.h1.util.manifest_ok(files))
        files['01_ana_occurrence_inventory.csv']+=b'bad';self.assertFalse(a.prep.r43.h1.util.manifest_ok(files))

    def test_3_2_detected_without_response(self):
        r=occurrence(self.model,'3:2');self.assertEqual(r['lex_utf8'],'ענה');self.assertEqual(r['construction_class'],'FORMULAIC_CSF');self.assertFalse(r['automatic_response_to'])

    def test_request_requires_context_not_impf_alone(self):
        s=deepcopy(self.source)
        for c in s['native']:
            if c['ref']=='31:35':
                for w in c['words']:
                    if w['lex']=='MJ':w['lex']='OTHER'
        self.assertNotEqual(next(r for r in a.inventory(s) if r['reference']=='31:35')['construction_class'],'RESPONSE_REQUEST')

    def test_cessation_requires_explicit_mother_edge(self):
        s=deepcopy(self.source)
        for c in s['native']:
            if c['ref']=='32:1':c['bhsa_mother_nodes']=[]
        self.assertNotEqual(next(r for r in a.inventory(s) if r['reference']=='32:1')['construction_class'],'ANSWERING_CESSATION')

    def test_cessation_subject_and_target(self):
        r=occurrence(self.model,'32:1');self.assertTrue(r['governing_cessation_subjects']);self.assertIn('איוב',r['explicit_target_names'])

    def test_no_verse_whitelist_extraction(self):
        s=deepcopy(self.source);c=s['native'][0];w=c['words'][0];w.update(lex='<NH[',lex_utf8='ענה')
        self.assertIn(w['node'],[r['word_node'] for r in a.inventory(s)])

    def test_homonyms_distinguished(self):
        self.assertEqual([r['reference'] for r in self.model['inventory'] if not r['answer_lexeme']],['30:11','37:23'])

    def test_32_12_negative_scope_follows_two_source_edges(self):
        r=occurrence(self.model,'32:12');self.assertEqual(len(r['syntactic_ancestor_clause_ids']),2);self.assertTrue(r['negation_evidence'])

    def test_unlinked_nearby_negative_not_imported(self):
        s=deepcopy(self.source)
        for c in s['native']:
            if c['ref']=='32:12':c['bhsa_mother_nodes']=[]
        r=next(r for r in a.inventory(s) if r['reference']=='32:12');self.assertFalse(r['negation_evidence'])

    def test_hif_self_declaration_not_normalized(self):
        r=occurrence(self.model,'32:17');self.assertEqual((r['vs'],r['construction_class']),('hif','SELF_DECLARED_RESPONSE'))

    def test_33_13_unresolved_subject(self):self.assertEqual(occurrence(self.model,'33:13')['actor_identity'],'UNRESOLVED')

    def test_non_ana_response_language_preserved(self):
        for ref,lex in [('32:14','CWB['),('33:14','DBR[')]:
            r=next(f for f in self.model['focus'] if f['reference']==ref);self.assertEqual(r['status'],'NO_ANA');self.assertIn(lex,[e['lex'] for e in r['lexical_evidence']])

    def test_36_add_speech_not_answer(self):
        f=next(f for f in self.model['focus'] if f['reference']=='36:1');self.assertTrue(f['add_speech_control']);self.assertFalse(f['occurrence_ids'])

    def test_end_complex_focus_generated_from_inventory(self):
        self.assertIn('40:2',[f['reference'] for f in self.model['focus']]);self.assertIn('40:5',[f['reference'] for f in self.model['focus']])

    def test_dialogue_requires_explicit_event_id(self):
        self.assertEqual(occurrence(self.model,'4:1')['construction_class'],'DIALOGUE_TURN_CSF')
        s=deepcopy(self.source)
        for c in s['csf']:c['current_event_id']='UNLINKED'
        self.assertEqual(next(r for r in a.inventory(s) if r['reference']=='4:1')['construction_class'],'FORMULAIC_CSF')

    def test_prior_frozen_57_and_seven_cases(self):
        self.assertEqual(len(self.model['unresolved']),57)
        prior=self.source['files'];self.assertEqual(self.model['historical'],prior)
        self.assertEqual(len(a.prep.decode_rows(prior['03_global_seam_cases.csv'])),7)

    def test_no_new_judgments_or_relations(self):
        self.assertEqual(self.model['new_human_judgments'],[]);self.assertEqual(self.model['new_structural_relations'],[])
        self.assertTrue(all(r['automatic_resolution'] is False for r in self.model['candidates']))

    def test_c2_and_c3_unadjudicated(self):
        for cid in ('ANA-C2','ANA-C3'):
            c=next(x for x in self.model['candidates'] if x['candidate_id']==cid);self.assertEqual(c['status'],'UNADJUDICATED');self.assertFalse(c['candidate_parent'])

    def test_interval_not_containment(self):
        c=self.model['candidates'][3];self.assertTrue(c['positional_interval_occurrence_ids']);self.assertFalse(c['interval_is_hierarchical_containment'])

    def test_missing_feature_explicit_schema_error(self):
        s=deepcopy(self.source);del s['native'][0]['words'][0]['lex']
        with self.assertRaisesRegex(ValueError,'missing word schema'):a.validate_source(s)

    def test_duplicate_word_identity_rejected(self):
        s=deepcopy(self.source);s['native'][0]['words'].append(deepcopy(s['native'][0]['words'][0]))
        with self.assertRaisesRegex(ValueError,'coverage'):a.validate_source(s)

    def test_serialized_evidence_rows_independently_resolve(self):
        files=a.serialize(self.model,self.source)
        for e in self.model['evidence']:
            raw=a.prep.r43.h1.read_csv(files[e['source_member']])[e['source_data_row']-1]
            self.assertEqual(a.sha(a.canonical(raw).encode()),e['source_row_sha256'],e['evidence_id'])
        for d in self.model['dependencies']:
            raw=next(r for r in a.prep.r43.h1.read_csv(files[d['source_member']]) if r['case_id']==d['case_id'])
            self.assertEqual(a.sha(a.canonical(raw).encode()),d['source_row_sha256'])

    def test_word_reference_not_clause_initial_verse(self):
        s=deepcopy(self.source);w=next(w for c in s['native'] if c['ref']=='40:2' for w in c['words'] if w['lex']=='<NH[')
        w['reference']='40:7'
        ii=a.inventory(s);self.assertEqual(next(r for r in ii if r['word_node']==w['node'])['reference'],'40:7')
        self.assertIn('40:7',[f['reference'] for f in a.focus(s,ii)])

    def test_unknown_ana_lexeme_stops_without_sense_guess(self):
        s=deepcopy(self.source);w=next(w for c in s['native'] for w in c['words'] if w['lex']=='<NH[');w['lex']='UNKNOWN'
        with self.assertRaisesRegex(ValueError,'unreviewed ANA lexical identity'):a.inventory(s)

    def test_frozen_3_2_constraints_in_packet(self):
        rows=[e['source_record'] for e in self.model['evidence'] if e['kind']=='FROZEN_STRUCTURAL_CONSTRAINT']
        self.assertTrue(any(e['relation_type']=='CONTINUES_WITHIN' and e['source_node']=='H:HSA014' and e['target_node']=='H:HSA013' for e in rows))
        self.assertTrue(any(e['relation_type']=='HIERARCHICALLY_ABOVE' and e['source_node']=='H:HSA013' and e['target_node']=='H:HSA014' for e in rows))

    def test_independent_process_determinism_and_zip_crc(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs=[]
            for name in ('first','second'):
                out=Path(temp)/name
                run=subprocess.run([sys.executable,str(a.ROOT/'src/milal_hsa3_ana_response_frame.py'),'--self-test','--out',str(out)],capture_output=True,text=True)
                self.assertEqual(run.returncode,0,run.stdout+run.stderr)
                zp=out.with_name(name+'_results.zip');outputs.append(zp.read_bytes())
                with zipfile.ZipFile(zp) as z:self.assertIsNone(z.testzip())
            self.assertEqual(*outputs)


def make_negative(key,mutation):
    def test(self):
        m,s=deepcopy(self.model),deepcopy(self.source);mutation(m,s)
        self.assertEqual(next(g['status'] for g in a.gates(m,s) if g['gate']==key),'FAIL')
    return test


for key,mutation in MUTATIONS.items():setattr(AnaTests,'test_negative_gate_'+key.lower(),make_negative(key,mutation))


if __name__=='__main__':unittest.main()
