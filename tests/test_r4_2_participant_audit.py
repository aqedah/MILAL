import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_r4_2_participant_audit as p
from milal_r4_2_synthetic import source


class Audit(unittest.TestCase):
    def setUp(self):self.s=source();self.m=p.build(self.s)

    def test_all_gates(self):self.assertTrue(all(r['status']=='PASS' for r in p.gates(self.m,self.s)))

    def test_three_anonymous_entries(self):
        for ref in ('1:16','1:17','1:18'):
            e=next(e for e in self.m['events'] if e['ref']=='Job '+ref)
            self.assertTrue(e['anonymous_entry']);self.assertEqual(e['participant_identity'],'UNRESOLVED')
            self.assertEqual(e['first_appearance_in_book_if_exact'],'UNRESOLVED');self.assertEqual(e['named_role'],'')

    def test_explicit_first_entry(self):
        e=next(e for e in self.m['events'] if e['ref']=='Job 1:14')
        self.assertEqual(e['identity_status'],'EXPLICIT');self.assertIn('מלאך',e['participant_surface'])

    def test_wife_overt_suffix_not_resolved(self):
        e=next(e for e in self.m['events'] if e['ref']=='Job 2:9')
        self.assertEqual(e['identity_status'],'EXPLICIT');self.assertEqual(e['named_role'],'')
        self.assertNotIn('איוב',e['participant_identity'])

    def test_explicit_speaker_expression_change_retained(self):
        e=next(e for e in self.m['events'] if e['ref']=='Job 2:9')
        self.assertIn('EXPLICIT_SPEAKER_CHANGE',e['event_types'])
        self.assertEqual(e['previous_explicit_participant_context']['relation'],'PREVIOUS_OVERT_EXPRESSION_NOT_COREFERENCE')

    def test_explicit_addressee_expression_change_retained(self):
        for i,c in enumerate(self.s['native_clauses'][:2]):
            ph=copy.deepcopy(c['phrases'][1]);ph['function']='Cmpl';ph['node']+=99999
            ph['words'][0].update(lex='SYNTHETIC_'+str(i),lex_utf8='SYNTHETIC_'+str(i))
            c['phrases'].append(ph)
        e=next(e for e in p.extraction(self.s)[0] if e['participant_source_node']==self.s['native_clauses'][1]['phrases'][-1]['node'])
        self.assertIn('EXPLICIT_ADDRESSEE_CHANGE',e['event_types'])

    def test_friends_group_is_one_phrase(self):
        rows=[e for e in self.m['events'] if e['ref']=='Job 2:11']
        self.assertEqual(len(rows),1);self.assertTrue(rows[0]['group_preserved']);self.assertEqual(len(rows[0]['participant_word_nodes']),3)

    def test_elihu_name_within_full_source_np(self):
        row=next(e for e in self.m['events'] if e['ref']=='Job 32:2')
        self.assertIn('אליהוא',row['participant_surface']);self.assertEqual(len(row['participant_word_nodes']),2)

    def test_control_and_human_do_not_drive_detection(self):
        baseline=p.extraction(self.s)
        self.s['human42']['judgments']=[];self.s['cfg42']['controls']=[];self.s['cfg42']['control_expectations']={}
        self.assertEqual(p.extraction(self.s),baseline)

    def test_ref_relocation_keeps_event_identity_and_types(self):
        before=p.extraction(self.s)[0]
        for c in self.s['native_clauses']:c['ref']='Job 9:9';c['chapter']=9;c['verse']=9
        after=p.extraction(self.s)[0]
        fields=('participant_event_id','event_type','identity_status','matched_rules')
        self.assertEqual([[r[k] for k in fields] for r in before],[[r[k] for k in fields] for r in after])

    def test_historical_speaker_does_not_drive_identity(self):
        before=p.extraction(self.s)
        for r in self.s['markers']:r['historical_projection']={'speaker_canonical':'messenger_2','speaker_source_type':'IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT'}
        self.assertEqual(p.extraction(self.s),before)

    def test_unknown_pronoun_no_entry_is_not_invented(self):
        c=self.s['native_clauses'][0];ph=c['phrases'][1]
        ph['words'][0].update(sp='prps',pdp='prps',lex='הוא',lex_utf8='הוא');ph['surface']='הוא'
        self.assertFalse(any(e['participant_source_node']==ph['node'] for e in p.extraction(self.s)[0]))

    def test_first_appearance_not_entity_claim(self):
        self.assertTrue(all(e['first_appearance_in_book_if_exact']=='UNRESOLVED' for e in self.m['events']))

    def test_human_hierarchy_blank(self):
        self.assertTrue(all(e['human_hierarchy_relation']==e['human_conclusion']=='' for e in self.m['events']))

    def test_wife_inside_and_friends_after_supplied_ending(self):
        wife=next(e for e in self.m['events'] if e['ref']=='Job 2:9')['participant_event_id']
        friend=next(e for e in self.m['events'] if e['ref']=='Job 2:11')['participant_event_id']
        self.assertTrue(any(r['participant_event_id']==wife and r['inside_open_close_span'] for r in self.m['enclosures']))
        rr=[r for r in self.m['enclosures'] if r['participant_event_id']==friend]
        self.assertTrue(all(not r['inside_open_close_span'] and 'HUMAN_ENDPOINT:2:10' in r['nearest_preceding_closure_anchor'] for r in rr))

    def test_all_messenger_entries_in_two_candidate_frames(self):
        for ref in ('1:14','1:16','1:17','1:18'):
            eid=next(e for e in self.m['events'] if e['ref']=='Job '+ref)['participant_event_id']
            self.assertEqual(sum(r['participant_event_id']==eid and r['inside_open_close_span'] for r in self.m['enclosures']),2)

    def test_ending_not_promoted(self):
        self.assertFalse(self.m['endings'][0]['left_MR1_EXPLICIT_CLOSURE']);self.assertFalse(self.m['endings'][0]['right_MR1_EXPLICIT_CLOSURE'])

    def test_gap_and_csf_separate(self):
        control={r['ref']:r for r in self.m['controls']}
        self.assertFalse(control['3:1']['marker_ids']);self.assertTrue(control['3:2']['marker_ids'])

    def test_complete_phrase_audit(self):self.assertEqual(len(self.m['inventory']),sum(len(c['phrases']) for c in self.s['native_clauses']))

    def test_every_event_has_expanded_review_context(self):
        packet=self.m['reports'][p.REPORTS[3]]
        for e in self.m['events']:self.assertEqual(packet.count('### Event '+e['participant_event_id']+' — '),1)

    def test_model_not_aliased(self):
        original=copy.deepcopy(self.s);self.m['events'][0]['clause_atom_ids'].append(-1);self.assertEqual(original,self.s)

    def test_manifest_negative(self):
        files=p.serialize(self.m,self.s);self.assertTrue(p.util.manifest_ok(files));files['01_participant_transition_events.csv']+=b'bad'
        self.assertEqual(p.util.manifest_gate(files)['status'],'FAIL')

    def test_deterministic_package(self):
        files=p.serialize(self.m,self.s)
        with tempfile.TemporaryDirectory() as td:
            p.previous.publish(files,Path(td)/'a');p.previous.publish(files,Path(td)/'b')
            self.assertEqual((Path(td)/'a_results.zip').read_bytes(),(Path(td)/'b_results.zip').read_bytes())


def mutate(gate,m,s):
    if gate=='ACCEPTED_SOURCE_MANIFESTS':s['receipt42']['actual']['CORRUPT']='bad'
    elif gate=='EXPLICIT_RULES_DOCUMENTED':s['rules_receipt']='bad'
    elif gate=='WHOLE_BOOK_SCOPE':m['clauses'].pop()
    elif gate in ('NO_SEMANTIC_INVENTION','NO_FORCED_MESSENGER_IDENTITIES'):
        next(e for e in m['events'] if e['anonymous_entry'])['named_role']='messenger_2'
    elif gate.endswith('_RESOLVED'):
        refs={'EXPLICIT_MESSENGER_RESOLVED':'1:14','WIFE_RESOLVED':'2:9','FRIENDS_GROUP_RESOLVED':'2:11','ELIHU_RESOLVED':'32:2'}
        m['events'].remove(next(e for e in m['events'] if e['ref']=='Job '+refs[gate]))
    elif gate in ('ANONYMOUS_ENTRIES_RETAINED','UNRESOLVED_EVENT_NOT_DELETED'):m['events'].remove(next(e for e in m['events'] if e['anonymous_entry']))
    elif gate=='HISTORICAL_IMPLICIT_NOT_IDENTITY':m['historical_speakers'][0]['identity_authority']=True
    elif gate=='FIRST_APPEARANCE_UNRESOLVED':m['events'][0]['first_appearance_in_book_if_exact']=True
    elif gate=='HUMAN_CONTROL_SEPARATE':m['human'][0]['statement']='COMPUTED'
    elif gate=='UNIFORM_EXTRACTION_RULE':m['inventory'].pop()
    elif gate=='SOURCE_ATOM_MAPPING':m['events'][0]['clause_atom_ids']=[-1]
    elif gate in ('ENCLOSURE_LINKS','WIFE_ENCLOSED','MESSENGERS_ENCLOSED'):m['enclosures']=[]
    elif gate=='FORMAL_SPAN_RELATIONS':m['formal_relations'][0]['formal_id']='UNKNOWN'
    elif gate=='ENDING_COMPARISON_RETAINED':m['endings'][0]['shared_family_ids']=['INVENTED']
    elif gate=='MR1_CLOSURES_UNCHANGED':m['endings'][0]['left_MR1_EXPLICIT_CLOSURE']=True
    elif gate in ('GAP_3_1_RETAINED','CSF_3_2_SEPARATE'):m['controls']=[]
    elif gate=='HUMAN_FIELDS_BLANK':m['events'][0]['human_hierarchy_relation']='CHILD'
    elif gate in ('NO_HIERARCHY','NO_SCORE_RANK','NO_INTERPRETIVE_LABELS'):
        m['events'][0][{'NO_HIERARCHY':'parent_id','NO_SCORE_RANK':'score','NO_INTERPRETIVE_LABELS':'literary_role'}[gate]]='INVENTED'
    elif gate=='REPORTS_SOURCE_GROUNDED':m['reports'][p.REPORTS[0]]='missing'
    elif gate=='DETERMINISTIC_REPLAY':m['events'].reverse()
    else:raise AssertionError('missing negative mutation '+gate)


def negative(name):
    def test(self):
        mutate(name,self.m,self.s)
        self.assertEqual({g['gate']:g['status'] for g in p.gates(self.m,self.s)}[name],'FAIL')
    return test

_source=source()
for _gate in p.gates(p.build(_source),_source):setattr(Audit,'test_negative_'+_gate['gate'].lower(),negative(_gate['gate']))

if __name__=='__main__':unittest.main()
