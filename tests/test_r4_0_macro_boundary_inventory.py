from copy import deepcopy
from pathlib import Path
import io
import json
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_r4_0_macro_boundary_inventory as r4
import milal_r4_0_sources as src
from milal_r4_0_synthetic import source


class TestR40Behavior(unittest.TestCase):
    def setUp(self):
        self.s=source();self.m=r4.build(self.s)

    def test_synthetic_gates(self):
        self.assertTrue(all(g['status']=='PASS' for g in r4.gates(self.m,self.s)))

    def test_whole_book_and_final_verse(self):
        self.assertEqual(len(self.m['coverage']),13)
        self.assertEqual(self.m['coverage'][-1]['ref'],'Job 42:17')
        self.assertEqual(self.m['coverage'][-1]['candidate_ids'],[])

    def test_multi_atom_preserved(self):
        self.assertEqual(self.m['markers'][0]['clause_atom_ids'],[100,101])

    def test_only_positive_wayhi(self):
        self.assertEqual([r['source_event_id'] for r in self.m['markers'] if r['marker_family']=='MR1_WAYHI_POSITIVE'],['way0:1'])
        self.assertEqual(len(self.m['way0_audit']),2)
        self.assertEqual(self.m['way0_audit'][1]['promoted_marker_id'],'')
        self.assertFalse(any('MR1:way0:2' in c['trigger_ids'] for c in self.m['candidates']))

    def test_csf_candidate(self):
        c=next(c for c in self.m['candidates'] if c['anchor_clause_atom']==100)
        self.assertIn('MR1:csf:1',c['trigger_ids'])
        self.assertEqual(self.m['markers'][0]['observation_role'],'SPEECH_FRAME_CANDIDATE')

    def test_closure_end_not_start(self):
        self.s['markers'][2]['atom_ids']=[104,106]
        m=r4.build(self.s)
        self.assertIn('MR1:closure:1',next(c for c in m['candidates'] if c['anchor_clause_atom']==106)['trigger_ids'])
        self.assertNotIn('MR1:closure:1',next(c for c in m['candidates'] if c['anchor_clause_atom']==104)['trigger_ids'])

    def test_explicit_hr1_scope(self):
        case=next(r for r in self.m['human_scopes'] if r['case_id']=='CASE025')
        self.assertEqual(case['clause_atom_ids'],[106])
        self.assertEqual(case['scope_precision'],'VERSE_SCOPE_NOT_ATOM_ADJUDICATED')
        self.assertEqual(case['participating_unit_ids'],['SYNTHETIC_UNIT'])

    def test_hr1_multi_atom_verse_no_narrowing(self):
        self.s['boundaries'][0]['boundary_identity']['boundary_ref']='1:1'
        m=r4.build(self.s)
        scope=next(r for r in m['human_scopes'] if r['case_id']=='CASE025')
        self.assertEqual(scope['clause_atom_ids'],[100,101])
        self.assertEqual(sum('HR1:CASE025' in c['trigger_ids'] for c in m['candidates']),2)

    def test_no_fuzzy_case_scope(self):
        self.s['boundaries'][0]['boundary_identity']['boundary_ref']='31:41'
        with self.assertRaisesRegex(ValueError,'unresolved HR1'):
            r4.build(self.s)

    def test_partial_insufficient_verbatim(self):
        self.assertEqual(self.m['human'][0]['human_source_record']['form_assessment'],'PARTIAL')
        self.assertEqual(self.m['human'][1]['human_source_record']['form_assessment'],'INSUFFICIENT')
        self.assertEqual([r['human_source_record'] for r in self.m['human']],self.s['human'])

    def test_model_mutation_cannot_change_source(self):
        self.m['human'][0]['human_source_record']['reviewer_notes']='mutated'
        self.m['markers'][0]['clause_atom_ids'].pop()
        self.assertNotEqual(self.s['human'][0]['reviewer_notes'],'mutated')
        self.assertEqual(self.s['markers'][0]['atom_ids'],[100,101])

    def test_nonboundary_human_not_generalized(self):
        self.assertFalse(any(x['case_id']=='CASE001' for c in self.m['candidates'] for x in c['human_review_status']))
        self.assertEqual(len(self.m['human']),30)

    def test_extension_dependency_preserved(self):
        self.assertEqual(self.m['extensions'],self.s['extensions'])
        for r in self.m['human'][6:12]:
            self.assertEqual(r['extension_dependency_cases'],list(src.hr.SEQUENCE_CASES))

    def test_singleton_rarity_not_trigger(self):
        self.assertEqual(self.m['singletons'][0]['atom'],120)
        self.assertFalse(any(c['anchor_clause_atom']==120 for c in self.m['candidates']))

    def test_control_without_evidence(self):
        row=next(r for r in self.m['controls'] if r['control_ref']=='42:16')
        self.assertEqual(row['source_status'],'NO_MATCHING_SOURCE_EVIDENCE')

    def test_controls_do_not_generate(self):
        self.s['config']['controls']=[]
        other=r4.build(self.s)
        for k in ('markers','formal','candidates','links','zones'):self.assertEqual(other[k],self.m[k])

    def test_formal_both_endpoints_lossless(self):
        self.assertEqual([c['anchor_clause_atom'] for c in self.m['candidates'] if 'FORMAL:RB1:W1' in c['trigger_ids']],[102,104])
        self.assertEqual(sum(r['evidence_id']=='FORMAL:RB1:W1' for r in self.m['links']),4)

    def test_adjacent_events_remain_distinct(self):
        self.assertTrue(any(r['directly_adjacent'] for r in self.m['adjacent']))
        self.assertEqual(len(self.m['markers']),4)
        self.assertEqual(len({r['marker_event_id'] for r in self.m['markers']}),4)

    def test_distance_uses_native_order_not_id_arithmetic(self):
        r=next(r for r in self.m['adjacent'] if r['left_id']=='CAND:A102')
        self.assertEqual(r['clause_atom_distance'],1)
        self.assertEqual(r['right_id'],'CAND:A104')

    def test_zones_bounded_overlay_only(self):
        for z in self.m['zones']:
            self.assertTrue(z['overlay_only'])
            self.assertLessEqual(self.s['atoms'][z['end_atom']]['index']-self.s['atoms'][z['start_atom']]['index'],2)
            self.assertGreaterEqual(len(z['evidence_ids']),2)
        changed=deepcopy(self.s);changed['config']['zone_span_atoms']=1
        other=r4.build(changed)
        self.assertEqual(other['candidates'],self.m['candidates'])
        self.assertNotEqual(other['zones'],self.m['zones'])

    def test_no_parent_score_rhetoric_fields(self):
        for key in ('markers','formal','candidates','adjacent','zones'):
            for row in self.m[key]:self.assertFalse(set(row)&{'parent','mother','score','rank','rhetorical_label'})

    def test_focus_after_whole_book(self):
        self.assertNotIn('## Job 1:1',self.m['focus_report'])
        self.assertIn('## Job 42:16',self.m['focus_report'])
        self.assertIn('| 1 |',self.m['whole_report'])

    def test_cautions_quoted(self):
        for cid in ['CASE028','CASE029']:
            h=next(r for r in self.s['human'] if r['case_id']==cid)
            self.assertIn('> '+h['reviewer_notes'],self.m['focus_report'])

    def test_deterministic_bytes(self):
        self.assertEqual(r4.serialize(self.m,self.s),r4.serialize(r4.build(source()),source()))

    def test_manifest_corruption_negative(self):
        f=r4.serialize(self.m,self.s)
        self.assertEqual(r4.util.manifest_gate(f)['status'],'PASS')
        f['02_boundary_candidate_inventory.csv']+=b'X'
        self.assertEqual(r4.util.manifest_gate(f)['status'],'FAIL')

    def test_publish_integrity_and_no_overwrite(self):
        f=r4.serialize(self.m,self.s)
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'run';r4.publish(f,p)
            with zipfile.ZipFile(str(p)+'_results.zip') as z:self.assertEqual({n:z.read(n) for n in z.namelist()},f)
            with self.assertRaisesRegex(ValueError,'already exists'):r4.publish(f,p)

    def test_duplicate_marker_identity_stops(self):
        self.s['markers'].append(deepcopy(self.s['markers'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate explicit ID'):r4.build(self.s)

    def test_unknown_native_atom_stops(self):
        self.s['markers'][0]['atom_ids']=[9999]
        with self.assertRaisesRegex(ValueError,'unknown event atom'):r4.build(self.s)

    def test_source_exact_hash_and_manifest(self):
        f={'sample.csv':b'id\n1\n'}
        f['99_manifest_sha256.csv']=r4.util.csv_bytes([dict(file='sample.csv',sha256=src.sha(f['sample.csv']))])
        def blob(files):
            out=io.BytesIO()
            with zipfile.ZipFile(out,'w') as z:
                for n,data in files.items():z.writestr(n,data)
            return out.getvalue()
        b=blob(f);self.assertEqual(src.archive(b,src.sha(b),mr1=True)['files'],f)
        with self.assertRaisesRegex(ValueError,'SHA256'):src.archive(b,'0'*64,mr1=True)
        f['sample.csv']=b'changed';b=blob(f)
        with self.assertRaisesRegex(ValueError,'manifest'):src.archive(b,src.sha(b),mr1=True)

    def test_unsafe_source_archive_stops(self):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr('../outside',b'x')
        b=out.getvalue()
        with self.assertRaisesRegex(ValueError,'unsafe'):src.archive(b,src.sha(b),mr1=True)


def mutation(name,m,s):
    if name=='BHSA_2021_VERIFIED':s['execution']['bhsa_version']='2017'
    elif name=='MR1_MANIFEST_VERIFIED':s['manifest_receipts']['mr1']['actual']['x']='bad'
    elif name=='MR1_REPRODUCTION_ACCEPTED':s['mr_meta']['status']='FAIL'
    elif name=='FULL_JOB_COVERAGE':m['coverage'].pop(0)
    elif name=='NATIVE_SOURCE_COUNTS':s['config']['expected']['atoms']+=1
    elif name=='ALL_MR1_MARKER_IDS_RESOLVE':m['markers'][0]['marker_subtype']='changed'
    elif name=='ALL_CLAUSE_ATOM_LINKS_RESOLVE':m['markers'][0]['clause_atom_ids'].pop()
    elif name=='WAY0_AUDIT_170':m['way0_audit'].pop()
    elif name=='ONLY_WAYHI_POSITIVES':m['markers']=[r for r in m['markers'] if r['marker_family']!='MR1_WAYHI_POSITIVE']
    elif name=='NEGATIVES_NOT_PROMOTED':m['candidates'][0]['trigger_ids'].append('MR1:way0:2')
    elif name=='CSF_PRESERVED':m['markers']=[r for r in m['markers'] if r['marker_family']!='MR1_CSF']
    elif name=='CLOSURES_PRESERVED':m['markers']=[r for r in m['markers'] if r['marker_family']!='MR1_EXPLICIT_CLOSURE']
    elif name=='EVERY_CANDIDATE_TRIGGERED':m['candidates'][0]['trigger_ids']=[]
    elif name=='CONTROLS_NOT_TRIGGERS':m['candidates'].append(dict(m['candidates'][0],candidate_id='CONTROL_ONLY'))
    elif name=='RARITY_NOT_TRIGGER':m['candidates'][0]['trigger_types'].append('SINGLETON_RARITY')
    elif name=='HUMAN_FIELDS_UNCHANGED':m['human'][0]['human_source_record']['review_status']='AUTO'
    elif name=='SEQUENCE_DEPENDENCY_PRESERVED':m['extensions'].pop()
    elif name=='CASE028_CONTINUITY_CAUTION':m['focus_report']=m['focus_report'].replace('> Synthetic ending; adjacency is not direct discourse continuity.','removed')
    elif name=='CASE029_JOB_ADDRESSEE_CAUTION':m['focus_report']=m['focus_report'].replace('> Synthetic beginning; Job is explicit addressee.','removed')
    elif name=='ADJACENT_EVENTS_DISTINCT':m['adjacent'].pop()
    elif name=='ZONES_OVERLAY_ONLY':m['zones'][0]['overlay_only']=False
    elif name=='NO_SCORES_RANKINGS':m['candidates'][0]['score']=1
    elif name=='NO_FINAL_BOUNDARY_LABEL':m['candidates'][0]['candidate_only']=False
    elif name=='NO_HIERARCHY_PARENTAGE':m['candidates'][0]['parent']='x'
    elif name=='NO_NEW_RHETORICAL_LABELS':m['candidates'][0]['rhetorical_label']='x'
    elif name=='FOCUS_FROM_WHOLE_BOOK':m['focus_report']+='fabricated'
    elif name=='FINAL_VERSE_INCLUDED':m['coverage'].pop()
    elif name=='SOURCE_HASHES_PRESENT':m['sources'][0]['SHA256']=''
    elif name=='NO_FUZZY_LINKAGE':m['links'][0]['source_locator']['data_row']=999
    elif name=='DETERMINISTIC_RERUN':m['controls'][0]['notes']='changed'
    elif name=='FORMAL_OCCURRENCES_LOSSLESS':m['formal'][0]['family_ids']=[]
    elif name=='PARTIAL_INSUFFICIENT_RETAINED':m['human'].pop(0)
    elif name=='UPSTREAM_MANIFESTS_VERIFIED':s['manifest_receipts']['prov1']['actual']['x']='bad'
    else:raise AssertionError('Missing mutation '+name)


class TestR40GateNegatives(unittest.TestCase):pass


def negative(name):
    def test(self):
        s=source();m=r4.build(s);mutation(name,m,s)
        checks={r['gate']:r['status'] for r in r4.gates(m,s)}
        self.assertEqual(checks[name],'FAIL',name)
    return test


_source=source()
for _gate in r4.gates(r4.build(_source),_source):
    setattr(TestR40GateNegatives,'test_negative_'+_gate['gate'].lower(),negative(_gate['gate']))


if __name__=='__main__':unittest.main()
