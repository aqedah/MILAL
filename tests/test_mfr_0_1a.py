import ast
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_mfr_common as cm
from milal_mfr01a_data import TABLES,table,load
from milal_mfr01a_synthetic import snapshot
from milal_mfr01a_core import build
from milal_mfr01a_bundle import bundle,review_universe,TYPE_FIELDS
from milal_mfr01a_lattice import lattice,expansions
from milal_mfr01a_relation import consolidate
from milal_mfr01a_gates import core_gates,release_gates,final_gates
from milal_mfr01a_provenance import static_scan

def release_fixture():
    return dict(baseline=dict(expected='sha',object='sha',ancestor=True),receipts=[dict(actual_sha256='h',expected_sha256='h')],reads=[dict(human_dependency=False,structural_dependency=False)],static_issues=[],scopes=['one','two'],events=['one_FREEZE','two_FREEZE','CONTROLS_LOADED'],
        controls=dict(pentateuch_expected=12,pentateuch_valid=12,prophet_cross_formal=1,prophet_preserved=1,death_expected=3,death_preserved=3,daniel_expected=2,daniel_preserved=2,nonrecovery_raw_markers=[],nonrecovery_profiles=[],nonrecovery_checked=True),
        post=dict(cases=[dict(review_status='UNREVIEWED',reviewer_notes='')],review_fields=['review_status','reviewer_notes'],participant_arc='UNADJUDICATED'),manifests=[True,True],consumer_files=[])

def damage_core(name,d,o):
    if name=='NO_RAW_MARKER_LOSS':o['profiles'].pop()
    elif name=='NO_RAW_FAMILY_LOSS':o['bundles'][0]['contributing_family_ids'].pop()
    elif name=='NO_RAW_RELATION_LOSS':o['crosswalk'].pop()
    elif name in ('NO_COVERAGE_LOSS','NO_NESTED_EVIDENCE_LOSS'):
        kind='coverage' if name=='NO_COVERAGE_LOSS' else 'nested';o['trace']=[r for r in o['trace'] if r['raw_kind']!=kind]
    elif name=='CANONICAL_OCCURRENCE_SET_BUNDLES_CREATED':o['bundles'][0]['marker_ids'].append('missing')
    elif name=='MULTI_RESOLUTION_DUPLICATES_CONSOLIDATED_FOR_REVIEW':
        r=deepcopy(o['bundles'][0]);r['bundle_id']='DUPLICATE';o['bundles'].append(r)
    elif name=='RAW_FAMILY_IDS_PRESERVED':o['membership'].pop()
    elif name=='RAW_RELATION_IDS_PRESERVED':o['crosswalk'][0]['raw_labels'].append('CHANGED')
    elif name=='FAMILY_LATTICE_PRESENT':o['lattice'][0]['status']='ACCEPTED'
    elif name=='EXPANSION_RELATIONS_EVIDENCE_ONLY':o['expansion'][0]['status']='ACCEPTED'
    elif name=='SINGLETON_EXPLICIT_PRESERVED':
        b=next(b for b in o['bundles'] if 'SINGLETON_EXPLICIT_BUNDLE' in b['categories']);o['family_review']=[r for r in o['family_review'] if r['bundle_id']!=b['bundle_id']]
    elif name=='SINGLETON_GENERIC_ARCHIVE_SUPPORTED':
        r=deepcopy(o['family_review'][0]);r['disposition']='DELETED';o['family_archive'].append(r)
    elif name=='RELATION_CASES_CONSOLIDATED':
        r=deepcopy(o['cases'][0]);r['case_id']='DUPLICATE';o['cases'].append(r)
    elif name=='FORMAL_ONLY_ARCHIVE_SUPPORTED':next(r for r in o['cases'] if 'SYN_FORMAL_ARCHIVE' in r['raw_relation_ids'])['default_review']=True
    elif name=='CLOSURE_MARKER_NOT_EQUAL_CLOSURE_TARGET':o['closures'][0]['review_eligible']=False
    elif name=='CLOSURE_WEAK_PAIRS_PRESERVED':o['closures'].pop()
    elif name=='CLOSURE_REVIEW_LINK_EVIDENCE_REQUIRED':o['closure_review'][0].update(coverage_end_ids=[],formal_family_ids=[],onset_form_evidence=[])
    elif name=='NO_NUMERIC_RANKING':o['bundles'][0]['score']=1
    elif name=='NO_HIERARCHY_ADJUDICATION':o['cases'][0]['selected_relation']='DECIDED'
    elif name=='CROSS_BOOK_RELATIONS_PRESERVED':next(r for r in o['cases'] if r['cross_book'])['cross_book']=False
    elif name=='HUMAN_REVIEW_UNIVERSE_REDUCED':o['relation_review']=deepcopy(d['relations'])
    elif name=='HUMAN_REVIEW_CASES_TRACEABLE':o['trace'][0]['raw_id']='missing'
    else:
        field={'NO_HUMAN_JUDGMENT':'human_judgment','NO_ACCEPTED_RELATION':'accepted_relation','NO_PARENT_EDGE':'parent_id','NO_TREE_SYNTHESIS':'root_id'}[name];o['cases'][0][field]='ADDED'

def damage_release(name,e):
    if name=='BASELINE_COMMIT_VERIFIED':e['baseline']['object']='bad'
    elif name=='MFR_0_1_FROZEN_VERIFIED':e['receipts'][0]['actual_sha256']='bad'
    elif name=='CONSOLIDATION_HUMAN_INPUT_COUNT_ZERO':e['reads'][0]['human_dependency']=True
    elif name=='CONSOLIDATION_STRUCTURAL_LABEL_INPUT_ZERO':e['reads'][0]['structural_dependency']=True
    elif name=='CONSOLIDATION_FROZEN_BEFORE_CONTROL_LOOKUP':e['events']=['CONTROLS_LOADED','one_FREEZE','two_FREEZE']
    elif name=='PENTATEUCH_EDSF_CONSOLIDATION_VALID':e['controls']['pentateuch_valid']-=1
    elif name=='PROPHET_CONTROL_CONSOLIDATION_VALID':e['controls']['prophet_preserved']=0
    elif name=='DEATH_RESUMPTION_CONSOLIDATION_VALID':e['controls']['death_preserved']-=1
    elif name=='DANIEL_EZRA_CONSOLIDATION_VALID':e['controls']['daniel_preserved']-=1
    elif name=='JOB_37_24_NONRECOVERY_PRESERVED':e['controls']['nonrecovery_profiles']=['created']
    elif name=='HUMAN_REVIEW_FIELDS_BLANK':e['post']['cases'][0]['reviewer_notes']='inferred'
    elif name=='R4_4_CONSUMER_ABSENT':e['consumer_files']=['added']
    elif name=='PARTICIPANT_ARC_UNTOUCHED':e['post']['participant_arc']='RESOLVED'
    elif name=='MANIFEST_VALID':e['manifests'][0]=False
    else:raise AssertionError(name)

class MFR01ATests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();m=snapshot()
        for key,name in TABLES.items():table(Path(cls.tmp.name)/name,m[key])
        cls.d=load(cls.tmp.name);cls.o=build(cls.d)
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_all_core_gates(self):self.assertTrue(all(core_gates(self.d,self.o).values()))
    def test_all_release_gates(self):self.assertTrue(all(release_gates(release_fixture()).values()))
    def test_syntax_static(self):
        for p in (cm.ROOT/'src').glob('milal_mfr01a_*.py'):ast.parse(p.read_text(encoding='utf8'))
        self.assertEqual(static_scan(),[])
    def minimal(self,occurrences=1,families=7,explicit=None):
        mids=list(self.d['m'])[:occurrences];d={'m':{mid:deepcopy(self.d['m'][mid]) for mid in mids},'families':[]}
        if explicit is not None:
            for m in d['m'].values():m['formal_explicitness']=explicit
        for i,typ in enumerate(list(TYPE_FIELDS)[:families]):
            d['families'].append(dict(family_id='F'+str(i),family_type=typ,marker_ids=mids,occurrence_count=len(mids),construction_definition={'view':i},signature_resolution=typ))
        return d
    def test_s1_seven_views_one_bundle(self):
        b,m,_,_=bundle(self.minimal());self.assertEqual(len(b),1);self.assertEqual(len(m),7);self.assertEqual(len(b[0]['contributing_family_ids']),7)
    def test_s2_five_views_repeated_bundle(self):
        b,m,_,_=bundle(self.minimal(2,5));self.assertEqual(len(b),1);self.assertEqual(len(m),5);self.assertIn('REPEATED_OCCURRENCE_BUNDLE',b[0]['categories'])
    def test_s3_subset_lattice(self):
        d=self.minimal(2,2);d['families'][1]['marker_ids']=d['families'][1]['marker_ids'][:1];d['families'][1]['occurrence_count']=1
        b,_,_,by=bundle(d);ll=lattice(d,b,by);self.assertEqual(len(b),2);self.assertTrue(any(r['set_relation'] in ('STRICT_SUBSET','STRICT_SUPERSET') for r in ll))
    def test_s4_locative_expansion_only(self):
        d=self.minimal(2,2);mids=list(d['m']);d['m'][mids[1]]['base_construction']=deepcopy(d['m'][mids[0]]['base_construction']);d['m'][mids[0]]['extension_features'].update(time=0,loca=0);d['m'][mids[1]]['extension_features'].update(time=0,loca=1)
        ee=expansions(d,{mids[0]:['B1'],mids[1]:['B2']});self.assertEqual(len(ee),1);self.assertEqual(ee[0]['status'],'EVIDENCE_ONLY');self.assertNotIn('textual_level',ee[0])
    def test_s5_singleton_cessation_default(self):
        b,_,_,_=bundle(self.minimal(explicit=['EXPLICIT_CESSATION']));r,a=review_universe(b,[],[]);self.assertEqual((len(r),len(a)),(1,0))
    def test_s6_singleton_generic_archive(self):
        b,_,_,_=bundle(self.minimal(explicit=[]));r,a=review_universe(b,[],[]);self.assertEqual((len(r),len(a)),(0,1))
    def test_s7_one_of_100_closure_pairs_has_link(self):
        template=deepcopy(next(iter(self.d['m'].values())));target='Z';d=deepcopy(self.d);d['m']={};d['relations']=[];d['by_coverage']=defaultdict(list);d['by_nested']=defaultdict(list)
        observation=deepcopy(self.d['observation'][0]);observation.update(participant_surface_set=[],domain='?');d['observation']=[deepcopy(observation) for _ in range(101)]
        for i,mid in enumerate([f'S{x:03}' for x in range(100)]+[target]):
            m=deepcopy(template);m.update(marker_id=mid,sequence_index=i,marker_index=i,clause_atom_ids=[i+10000],family_ids=[],discovery_sources=['EXPLICIT_CESSATION'] if mid==target else []);d['m'][mid]=m
        d['by_coverage']['S000']=[dict(coverage_candidate_id='C',end_index=100,candidate_end_anchor=10100,end_basis='CONFIGURATION_BREAK')]
        for i in range(100):
            r=deepcopy(self.d['relations'][0]);r.update(relation_candidate_id='R'+str(i),source_marker_id=f'S{i:03}',target_marker_id=target,relation_candidates=['CLOSURE_TARGET_CANDIDATE'],coverage_relationship=[]);d['relations'].append(r)
        rr,cw,cl,review,archive=consolidate(d,{mid:[mid+'B'] for mid in d['m']})
        self.assertEqual((len(rr),len(cw),len(cl)),(100,100,100));self.assertEqual((len(review),len(archive)),(1,99));self.assertTrue(all('CLOSURE_WEAK_PAIR_ONLY' in r['closure_status'] for r in cl if not r['review_eligible']))
    def test_s8_formal_only_archive(self):
        r=next(r for r in self.o['cases'] if 'SYN_FORMAL_ARCHIVE' in r['raw_relation_ids']);self.assertFalse(r['default_review']);self.assertIn(r['case_id'],{r['case_id'] for r in self.o['relation_archive']})
    def test_s9_competing_default(self):self.assertTrue(all(r['default_review'] for r in self.o['cases'] if 'REL_A_HIERARCHY_COMPETING' in r['buckets']))
    def test_s10_cross_book_survives(self):self.assertEqual(sum(r['cross_book'] for r in self.d['relations']),sum(r['cross_book'] for r in self.o['cases']))
    def test_s11_force_not_collapsed(self):
        self.assertTrue(all(p['force_evidence']==self.d['h'][p['marker_id']] for p in self.o['profiles']));self.assertTrue(all(not p['automatic_resolution'] for p in self.o['profiles']))
    def test_s12_trace_complete(self):self.assertTrue(core_gates(self.d,self.o)['HUMAN_REVIEW_CASES_TRACEABLE'])
    def test_rerun_byte_identity(self):self.assertEqual(cm.js(self.o),cm.js(build(self.d)))
    def test_marker_anchor_mutation_fails(self):
        o=deepcopy(self.o);o['profiles'][0]['anchor']='invented';self.assertFalse(core_gates(self.d,o)['NO_RAW_MARKER_LOSS'])
    def test_lattice_relation_mutation_fails(self):
        o=deepcopy(self.o);o['lattice'][0]['set_relation']='PARTIAL_OVERLAP';self.assertFalse(core_gates(self.d,o)['FAMILY_LATTICE_PRESENT'])
    def test_row_order_stable_ids(self):
        d=deepcopy(self.d)
        for k in ('families','markers','relations','membership'):d[k].reverse()
        other=build(d);self.assertEqual([(b['bundle_id'],b['marker_ids']) for b in self.o['bundles']],[(b['bundle_id'],b['marker_ids']) for b in other['bundles']]);self.assertEqual(self.o['cases'],other['cases'])
    def test_reference_metadata_not_selection(self):
        d=deepcopy(self.d)
        for m in d['m'].values():m.update(book='Changed',chapter=999,verse=999)
        o=build(d);projection=lambda x:[(r['case_id'],r['buckets'],r['default_review']) for r in x['cases']]
        self.assertEqual(projection(self.o),projection(o))
    def test_static_negative_target(self):self.assertTrue(static_scan({'core':'value="31:40"'}))
    def test_static_negative_human(self):self.assertTrue(static_scan({'core':'import milal_jin_top_level_postblind'}))
    def test_static_negative_book_filter(self):self.assertTrue(static_scan({'relation':'r=[x for x in rows if x["book"]==a["book"]]'}))
    def test_actual_read_guard_rejects_history(self):
        code=f"import sys;sys.path.insert(0,{str(cm.ROOT/'src')!r});from milal_mfr01a_blind import guard;from pathlib import Path;guard({{}},{self.tmp.name!r});Path({str(cm.ROOT/'docs/HANDOFF.md')!r}).read_bytes()"
        p=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('outside consolidation read allowlist',p.stderr)
    def test_actual_import_guard_rejects_postblind(self):
        code=f"import sys;sys.path.insert(0,{str(cm.ROOT/'src')!r});from milal_mfr01a_blind import guard;guard({{}},{self.tmp.name!r});import milal_mfr01a_controls"
        p=subprocess.run([sys.executable,'-B','-c',code],capture_output=True,text=True);self.assertNotEqual(p.returncode,0)
    def test_final_determinism_negative(self):self.assertFalse(final_gates('a','b',dict(tests_run=1957,failures=0,errors=0,skipped=0))['DETERMINISTIC_RERUN'])
    def test_final_regression_negative(self):self.assertFalse(final_gates('a','a',dict(tests_run=1957,failures=1,errors=0,skipped=0))['FULL_REGRESSION_PASS'])
    def test_final_skip_negative(self):self.assertFalse(final_gates('a','a',dict(tests_run=1957,failures=0,errors=0,skipped=1))['SKIP_ZERO'])

def core_negative(name):
    def test(self):
        o=deepcopy(self.o);damage_core(name,self.d,o);self.assertFalse(core_gates(self.d,o)[name])
    return test
def release_negative(name):
    def test(self):
        e=release_fixture();damage_release(name,e);self.assertFalse(release_gates(e)[name])
    return test
with tempfile.TemporaryDirectory() as _t:
    _m=snapshot()
    for _k,_n in TABLES.items():table(Path(_t)/_n,_m[_k])
    _d=load(_t)
    for _name in core_gates(_d,build(_d)):setattr(MFR01ATests,'test_negative_'+_name.lower(),core_negative(_name))
for _name in release_gates(release_fixture()):setattr(MFR01ATests,'test_negative_'+_name.lower(),release_negative(_name))
if __name__=='__main__':unittest.main()
