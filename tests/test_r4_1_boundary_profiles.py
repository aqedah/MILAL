import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_r4_1_boundary_profiles as p
from milal_r4_1_synthetic import source


class Profiles(unittest.TestCase):
    def setUp(self):
        self.s=source();self.m=p.build(self.s)

    def test_all_gates(self):
        self.assertTrue(all(g['status']=='PASS' for g in p.gates(self.m,self.s)))

    def test_span_truth_table(self):
        cases=[((1,2,3,5),[]),((1,3,3,5),['LEFT_CROSS','ENDS_WITHIN']),
               ((1,7,3,5),['LEFT_CROSS','RIGHT_CROSS','SPANS_ANCHOR']),
               ((3,5,3,5),['STARTS_WITHIN','ENDS_WITHIN','INTERNAL_TO_ANCHOR']),
               ((4,4,3,5),['STARTS_WITHIN','ENDS_WITHIN','INTERNAL_TO_ANCHOR']),
               ((5,6,3,5),['STARTS_WITHIN','RIGHT_CROSS']),((6,7,3,5),[])]
        for args,expected in cases:self.assertEqual(p.span_relations(*args),expected)

    def test_single_atom_crossing(self):
        self.assertEqual(p.span_relations(1,5,3,3),['LEFT_CROSS','RIGHT_CROSS','SPANS_ANCHOR'])

    def test_edge_partition_all_occurrences(self):
        ids={f['source_event_id'] for f in self.m['formal']}
        for a in self.m['anchors']:
            for side in ('LEFT_EDGE','RIGHT_EDGE'):
                rows=[r for r in self.m['edges'] if r['anchor_id']==a['anchor_id'] and r['edge']==side]
                all_ids=[i for r in rows for i in r['formal_ids']]
                self.assertEqual(len(all_ids),len(ids));self.assertEqual(set(all_ids),ids)
                for r in rows:self.assertLessEqual(set(r['incident_formal_ids']),set(r['formal_ids']))

    def test_edge_incidence_independent_oracle(self):
        for e in self.m['edges']:
            k=e['cut_index'];fs=self.m['formal']
            if e['relation']=='TERMINATES_BEFORE_OR_AT':expected=[f['source_event_id'] for f in fs if f['last_index']==k-1]
            elif e['relation']=='BEGINS_AFTER_OR_AT':expected=[f['source_event_id'] for f in fs if f['first_index']==k]
            else:expected=[f['source_event_id'] for f in fs if f['first_index']<k<=f['last_index']]
            self.assertEqual(e['incident_formal_ids'],expected)

    def test_formal_removal_never_changes_anchors(self):
        changed=copy.deepcopy(self.s);changed['formal']=[]
        self.assertEqual(p.derive(changed)['anchors'],self.m['anchors'])

    def test_controls_never_create_anchors(self):
        self.s['profile_config']['controls']+=['42:15']
        self.assertEqual(p.derive(self.s)['anchors'],self.m['anchors'])

    def test_human_full_multiatom_scope(self):
        a=next(a for a in self.m['anchors'] if a['human_case']=='CASE027')
        self.assertEqual(len(a['atom_ids']),2)

    def test_speech_frames_visible(self):
        for ref in ('38:1','40:1','40:3','40:6','42:1'):self.assertIn('Job '+ref,self.m['reports'][p.REPORTS[2]])
        self.assertIn('Job 32:6',self.m['reports'][p.REPORTS[0]])

    def test_same_family_all_pairs(self):
        from collections import Counter
        c=Counter((a['marker_family'],a['marker_subtype']) for a in self.m['anchors'] if a['source_type']=='MR1')
        self.assertEqual(len(self.m['comparisons']),sum(n*(n-1)//2 for n in c.values()))

    def test_source_is_not_aliased(self):
        original=copy.deepcopy(self.s)
        self.m['anchors'][0]['observed_marker_fields']['speaker_canonical']='MUTATED'
        self.assertEqual(self.s,original)

    def test_unknown_anchor_atom_stops(self):
        self.s['markers'][0]['atom_ids']=[-1]
        with self.assertRaises(ValueError):p.derive(self.s)

    def test_duplicate_source_id_stops(self):
        self.s['markers'].append(copy.deepcopy(self.s['markers'][0]))
        with self.assertRaises(ValueError):p.derive(self.s)

    def test_exact_zip_hash_required(self):
        with self.assertRaises(ValueError):p.src.archive(b'not a ZIP','0'*64,True)

    def test_manifest_negative(self):
        files=p.serialize(self.m,self.s)
        self.assertTrue(p.util.manifest_ok(files))
        files['01_boundary_oriented_anchors.csv']+=b'corruption'
        self.assertFalse(p.util.manifest_ok(files))
        self.assertEqual(p.util.manifest_gate(files)['status'],'FAIL')

    def test_deterministic_zip_and_no_overwrite(self):
        files=p.serialize(self.m,self.s)
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b';p.publish(files,a);p.publish(files,b)
            self.assertEqual(a.with_name('a_results.zip').read_bytes(),b.with_name('b_results.zip').read_bytes())
            with self.assertRaises(ValueError):p.publish(files,a)


def mutate(gate,m,s):
    if gate=='R40_SOURCE_INTEGRITY':s['r40_receipt']['actual']='bad'
    elif gate in ('NO_FORMAL_ONLY_ANCHORS','COLOCATED_EVENTS_SEPARATE','EXACT_SOURCE_PROVENANCE','OBSERVED_FIELDS_UNCHANGED'):m['anchors'][0]['source_type']='FORMAL'
    elif gate in ('CSF_PRESERVED','CLOSURES_PRESERVED','WAYHI_PRESERVED'):
        f={'CSF_PRESERVED':'MR1_CSF','CLOSURES_PRESERVED':'MR1_EXPLICIT_CLOSURE','WAYHI_PRESERVED':'MR1_WAYHI_POSITIVE'}[gate]
        m['anchors'].remove(next(a for a in m['anchors'] if a['marker_family']==f))
    elif gate=='SIX_HUMAN_SCOPES' or gate.endswith('_SCOPE_RETAINED'):
        case='CASE025' if gate=='SIX_HUMAN_SCOPES' else gate.split('_')[0]
        m['anchors'].remove(next(a for a in m['anchors'] if a['human_case']==case))
    elif gate in ('FORMAL_RELATIONS_EXACT','NO_FUZZY_LINKAGE'):m['relations'][0]['formal_id']='FUZZY_UNKNOWN'
    elif gate=='TWO_EDGE_PARTITIONS':m['edges'][0]['formal_ids'].append('UNKNOWN')
    elif gate=='CONTROL_42_16_NOT_PROMOTED':m['controls'][-2]['anchor_ids']=['INVENTED']
    elif gate in ('TRANSITION_32_6_VISIBLE','CONTINUITY_CAUTION_PRESERVED','ORDERED_SPEECH_FRAMES','42_7_DISTINCT_EVENTS','NEGATIVE_CONTROL_REPORT','WHOLE_BOOK_PACKET'):
        idx=['TRANSITION_32_6_VISIBLE','CONTINUITY_CAUTION_PRESERVED','ORDERED_SPEECH_FRAMES','42_7_DISTINCT_EVENTS','NEGATIVE_CONTROL_REPORT','WHOLE_BOOK_PACKET'].index(gate)
        m['reports'][p.REPORTS[idx]]='OMITTED'
    elif gate in ('COMPARE_27_29','COMPARE_38_40'):
        left='Job 27:1' if gate=='COMPARE_27_29' else 'Job 38:1'
        next(r for r in m['comparisons'] if r['left_ref']==left)['shared_family_ids']=['INVENTED']
    elif gate=='ALL_SAME_FAMILY_PAIRS':m['comparisons'].pop()
    elif gate=='HUMAN_JUDGMENTS_UNCHANGED':m['human'][0]['human_source_record']['reviewer_notes']='AUTO'
    elif gate in ('NO_PARENTAGE','NO_SCORE_RANK','NO_NEW_INTERPRETIVE_LABEL'):
        m['anchors'][0][{'NO_PARENTAGE':'parent_id','NO_SCORE_RANK':'score','NO_NEW_INTERPRETIVE_LABEL':'rhetorical_label'}[gate]]='FORBIDDEN'
    elif gate=='R40_SATURATION_RETAINED':m['saturation']['formal_only']=-1
    elif gate=='WAY0_NEGATIVES_NOT_PROMOTED':m['way0_audit'][-1]['is_wayhi']=True
    elif gate=='DETERMINISTIC_REPLAY':m['formal'].reverse()
    else:raise AssertionError('Missing gate mutation '+gate)


def negative(gate):
    def test(self):
        mutate(gate,self.m,self.s)
        self.assertEqual({g['gate']:g['status'] for g in p.gates(self.m,self.s)}[gate],'FAIL')
    return test

_s=source()
for _gate in p.gates(p.build(_s),_s):
    setattr(Profiles,'test_negative_'+_gate['gate'].lower(),negative(_gate['gate']))

if __name__=='__main__':unittest.main()
