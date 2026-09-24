import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_mfr_common as cm
import milal_mfr_gates as gates
import milal_mfr_provenance as provenance
from milal_mfr_synthetic import corpus
from milal_mfr_selftest import model,behavior
from milal_mfr_blind import NAMES
from milal_mfr_observation import observe
from milal_mfr_postblind import provenance_class

def bundle(directory):
    m=model();d=Path(directory);source=cm.ROOT/'config/mfr_0_1_blind_rules.json';sr=dict(source_id='NEUTRAL_RULES',actual_path=str(source),sha256=cm.sha(source.read_bytes()),human_dependency=False,structural_label_dependency=False,technical_root_dependency=False)
    for name,file in NAMES.items():cm.write(d/file,cm.csv_bytes(m[name]))
    counts={name:len(m[name]) for name in NAMES};cm.write(d/'02_blind_input_manifest.csv',cm.csv_bytes([sr]));meta=dict(counts=counts,clause_count=20,actual_source_reads=['NEUTRAL_RULES'])
    cm.write(d/'metadata.json',cm.js(meta));cm.manifest(d,'12_job_blind_manifest.csv');fact=gates.scan(d)
    scopes=('job','pentateuch','prophets','death','daniel_ezra');audit=[dict(asset_path='fixture',reuse_class='OBSERVATION_SAFE',sha256='abc',expected_sha256='abc')]
    return dict(phases={s:deepcopy(fact) for s in scopes},behavior=behavior(),audit=audit,expected_assets=['fixture'],baseline=dict(expected_baseline='baseline',baseline_object='baseline',baseline_is_ancestor=True),events=[s+'_FREEZE' for s in scopes]+['KNOWN_CONTROLS_LOADED','HISTORICAL_LOADED'],post=dict(historical_count=1,historical_unchanged=True,review_blank=True,new_roots=[],tree_edges=[],new_judgments=[],new_parents=[],new_siblings=[],participant_arc='UNADJUDICATED'),static=[],control_checks=dict(dsf_expected=2,dsf_recovered=2,prophet_cross_formal=1,death_cross_resumption=1,ketuvim_cross_formal=1,death_formula_expected=1,death_formula_recovered=1,death_pairs_expected=1,death_pairs_recovered=1),expected_clauses=20,expected_historical_count=1,consumer_files=[],final_manifest_valid=True)

def damage(g,e):
    j=e['phases']['job'];p=e['post'];b=e['behavior']
    if g=='BASELINE_COMMIT_VERIFIED':e['baseline']['baseline_object']='wrong'
    elif g=='HISTORICAL_GIT_HISTORY_PRESERVED':e['audit'][0]['sha256']='changed'
    elif g=='ASSET_PROVENANCE_AUDIT_COMPLETE':e['audit'].pop()
    elif g.startswith('BLIND_') and g.endswith('_ZERO'):
        field={'BLIND_HUMAN_INPUT_COUNT_ZERO':'human_dependency','BLIND_STRUCTURAL_LABEL_INPUT_COUNT_ZERO':'structural_label_dependency','BLIND_TECHNICAL_ROOT_INPUT_ZERO':'technical_root_dependency'}[g];j['sources'][0][field]=True
    elif g=='JOB_ALL_CLAUSES_OBSERVED':j['meta']['clause_count']-=1
    elif g=='MULTI_RESOLUTION_SIGNATURES_PRESENT':j['signature_resolutions'].pop()
    elif g in ('MARKER_DISCOVERY_GENERIC','NO_BOOK_BOUNDARY_FILTER','NO_CHAPTER_BOUNDARY_FILTER','NO_VERSE_BOUNDARY_FILTER','CONTROL_TARGET_REF_LEAKAGE_ZERO','NO_STRICT_MACRO_PRECLASSIFICATION','PLOT_LABELS_NOT_USED_IN_DISCOVERY'):e['static'].append('contaminated')
    elif g=='REPEATED_MARKERS_DISCOVERED':j['repeated']=0
    elif g=='SINGLETON_EXPLICIT_MARKERS_PRESERVED':j['singleton']=0
    elif g=='MARKER_FAMILIES_GENERATED':j['family_types'].pop()
    elif g in ('FAMILY_NOT_EQUAL_HIERARCHY','NO_RELATION_AUTO_ACCEPTED'):j['auto']=1
    elif g=='HIERARCHICAL_FORCE_EVIDENCE_PRESENT':j['meta']['counts']['force']-=1
    elif g in ('NO_HIERARCHICAL_FORCE_SCORE','NO_ROOT_GENERATED','NO_TREE_SYNTHESIS'):j['forbidden_fields']=1
    elif g=='COVERAGE_MULTIPLE_CANDIDATES_ALLOWED':j['coverage_multi']=0
    elif g=='NO_COVERAGE_AUTOWINNER':b['no_winner']=False
    elif g=='NESTED_MARKER_EVIDENCE_PRESENT':j['nested_nonempty']=0
    elif g=='RELATION_CANDIDATES_GENERATED':j['relations']=0
    elif g=='SCOPE_BOUNDARY_NOT_EQUAL_TEXTUAL_BOUNDARY':j['scope_bad']=1
    elif g in ('PENTATEUCH_CONTROL_BLIND','PROPHET_CONTROL_BLIND','DEATH_RESUMPTION_CONTROL_BLIND','DANIEL_EZRA_CONTROL_BLIND'):
        s={'PENTATEUCH_CONTROL_BLIND':'pentateuch','PROPHET_CONTROL_BLIND':'prophets','DEATH_RESUMPTION_CONTROL_BLIND':'death','DANIEL_EZRA_CONTROL_BLIND':'daniel_ezra'}[g];e['phases'][s]['manifest_valid']=False
    elif g in ('PENTATEUCH_EDSF_POSTBLIND_LOOKUP_ONLY','CONTROL_BLIND_FROZEN_BEFORE_KNOWN_REF_LOAD'):e['events'].remove('KNOWN_CONTROLS_LOADED');e['events'].insert(0,'KNOWN_CONTROLS_LOADED')
    elif g in ('JOB_BLIND_FROZEN_BEFORE_HISTORICAL_LOAD','HISTORICAL_RELATIONS_POSTBLIND_ONLY'):e['events'].remove('HISTORICAL_LOADED');e['events'].insert(0,'HISTORICAL_LOADED')
    elif g.startswith('CROSS_BOOK_'):
        key={'CROSS_BOOK_FORMAL_RELATION_REPRESENTABLE':'cross_formal','CROSS_BOOK_PARATAXIS_CANDIDATE_REPRESENTABLE':'cross_parataxis','CROSS_BOOK_HYPOTAXIS_CANDIDATE_REPRESENTABLE':'cross_hypotaxis','CROSS_BOOK_RESUMPTION_CANDIDATE_REPRESENTABLE':'cross_resumption'}[g];b[key]=False
    elif g=='SAME_FORM_NOT_AUTO_SAME_LEVEL':b['same_form']=False
    elif g=='DIFFERENT_FORM_NOT_AUTO_DIFFERENT_LEVEL':b['different_form']=False
    elif g=='NO_NEW_HUMAN_JUDGMENT':p['review_blank']=False
    elif g=='NO_NEW_ACCEPTED_PARENT':p['new_parents'].append('forbidden')
    elif g=='NO_NEW_ACCEPTED_SIBLING':p['new_siblings'].append('forbidden')
    elif g=='R4_4_CONSUMER_NOT_IMPLEMENTED':e['consumer_files'].append('consumer')
    elif g=='PARTICIPANT_ARC_UNTOUCHED':p['participant_arc']='ACCEPTED'
    elif g=='MANIFEST_VALID':e['final_manifest_valid']=False
    elif g=='BLIND_READSET_AND_HASHES_VERIFIED':j['sources'][0]['sha256']='false'
    elif g=='HISTORICAL_RELATION_INVENTORY_PRESERVED':p['historical_count']=0
    elif g in ('EDSF_GENERIC_OCCURRENCES_RECOVERED','PROPHET_CROSS_BOOK_FORMAL_CASE_RECOVERED','DEATH_CROSS_BOOK_RESUMPTION_RECOVERED','DANIEL_EZRA_CROSS_BOOK_CASE_PRESERVED'):
        key={'EDSF_GENERIC_OCCURRENCES_RECOVERED':'dsf_recovered','PROPHET_CROSS_BOOK_FORMAL_CASE_RECOVERED':'prophet_cross_formal','DEATH_CROSS_BOOK_RESUMPTION_RECOVERED':'death_cross_resumption','DANIEL_EZRA_CROSS_BOOK_CASE_PRESERVED':'ketuvim_cross_formal'}[g];e['control_checks'][key]=0
    else:raise AssertionError(g)

class MFRTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory();cls.e=bundle(cls.tmp.name);cls.m=model();cls.behavior=behavior()
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_all_gates_positive(self):self.assertTrue(all(gates.evaluate(self.e).values()))
    def test_syntax(self):
        for p in (cm.ROOT/'src').glob('milal_mfr_*.py'):ast.parse(p.read_text(encoding='utf8'))
    def test_static_clean(self):self.assertEqual(provenance.static_scan(),[])
    def test_static_target_negative(self):self.assertTrue(provenance.static_scan({'milal_mfr_marker_discovery.py':'x="1:13"'}))
    def test_static_human_import_negative(self):self.assertTrue(provenance.static_scan({'milal_mfr_marker_discovery.py':'import milal_jin_top_level_postblind'}))
    def test_static_book_filter_negative(self):self.assertTrue(provenance.static_scan({'milal_mfr_relation_candidates.py':'x=[r for r in rows if r["book"] == source["book"]]'}))
    def test_static_attribute_book_filter_negative(self):self.assertTrue(provenance.static_scan({'milal_mfr_relation_candidates.py':'x=[r for r in rows if r.book == source.book]'}))
    def test_raw_unknown_human_field_rejected(self):
        raw=corpus();raw[0]['human_decision']='ACCEPTED'
        with self.assertRaisesRegex(ValueError,'unknown derived'):observe(raw)
    def test_after_death_nominal_lexeme(self):
        raw=corpus()
        for w in raw[9]['words']:
            if w['lex']=='MWT[':w.update(lex='MWT/',sp='subs',pdp='subs',vt=None,vs=None)
        m=model(raw);target=next(x for x in m['markers'] if x['clause_id']==110)
        self.assertIn('AFTER_DEATH_TEMPORAL_CONSTRUCTION',target['discovery_sources'])
        self.assertTrue(any(r['source_clause_id']==109 and r['target_clause_id']==110 and 'TEMPORAL_RESUMPTION_CANDIDATE' in r['relation_candidates'] for r in m['relations']))
    def test_after_unrelated_event_not_future_death(self):
        raw=corpus()
        for w in raw[9]['words']:
            if w['lex']=='MWT[':w['lex']='QWM['
        raw[10]['words'][0]['lex']='MWT[';m=model(raw);target=next(x for x in m['markers'] if x['clause_id']==110)
        self.assertNotIn('AFTER_DEATH_TEMPORAL_CONSTRUCTION',target['discovery_sources'])
    def test_moses_modifier_is_not_addressee_head(self):
        raw=corpus();c=raw[0];p=next(p for p in c['phrases'] if p['function']=='Cmpl');w=next(w for w in c['words'] if w['lex']=='MCH=/');extra=deepcopy(w);w['lex']='JHWC</';extra['node']=max(c['word_ids'])+1;c['words'].append(extra);c['word_ids'].append(extra['node']);c['atoms'][0]['word_ids'].append(extra['node']);p['word_ids'].append(extra['node'])
        m=model(raw);first=next(x for x in m['markers'] if x['clause_id']==101);self.assertNotIn('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION',first['discovery_sources'])
    def test_day_one_not_year_one(self):
        raw=corpus();c=raw[0]
        for w in c['words']:
            if w['lex']=='CNH/':w['lex']='>XD/'
            elif w['lex']=='>XD/':w['lex']='CNH/'
        m=model(raw);first=next(x for x in m['markers'] if x['clause_id']==101);self.assertNotIn('YEAR_ONE_CONFIGURATION',first['discovery_sources'])
    def test_dsf_subject_not_borrowed_from_later_clause(self):
        raw=corpus();raw[0]['words'][1]['lex']='OTHER/';raw[1]['words'][1]['lex']='JHWH/'
        first=next(x for x in model(raw)['markers'] if x['clause_id']==101);self.assertNotIn('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION',first['discovery_sources'])
    def test_call_then_explicit_speech_configuration(self):
        raw=corpus();c=raw[0];c['words'][0]['lex']='QR>[';p=next(p for p in c['phrases'] if p['function']=='Subj');removed=set(p['word_ids']);c['phrases'].remove(p);c['words']=[w for w in c['words'] if w['node'] not in removed];c['word_ids']=[w for w in c['word_ids'] if w not in removed];c['atoms'][0]['word_ids']=list(c['word_ids']);raw[1]['words'][1]['lex']='JHWH/'
        first=next(x for x in model(raw)['markers'] if x['clause_id']==101);self.assertIn('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION',first['discovery_sources'])
    def test_read_guard_blocks_history(self):
        command=[sys.executable,'-B','-c',f"import sys;sys.path.insert(0,{str(cm.ROOT/'src')!r});from milal_mfr_blind import guard;from pathlib import Path;guard({{}},{self.tmp.name!r});Path({str(cm.ROOT/'docs/HANDOFF.md')!r}).read_bytes()"]
        p=subprocess.run(command,capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('outside blind read allowlist',p.stderr)
    def test_import_guard_blocks_postblind(self):
        command=[sys.executable,'-B','-c',f"import sys;sys.path.insert(0,{str(cm.ROOT/'src')!r});from milal_mfr_blind import guard;guard({{}},{self.tmp.name!r});import milal_mfr_postblind"]
        p=subprocess.run(command,capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('forbidden blind import',p.stderr)
    def test_syn1_identical_peers(self):self.assertTrue(any('PARATAXIS_CANDIDATE' in r['relation_candidates'] for r in self.m['relations']))
    def test_syn2_identical_different_nested(self):
        counts={r['nested_marker_count'] for r in self.m['coverage'] if r['marker_id'] in ('XM000001','XM000005')};self.assertGreater(len(counts),1)
    def test_syn3_locative_expansion(self):self.assertTrue(any(m['extension_features']['loca'] for m in self.m['markers']))
    def test_syn4_temporal_expansion(self):self.assertTrue(any(m['extension_features']['time'] for m in self.m['markers']))
    def test_syn5_cross_book_same_form(self):self.assertTrue(self.behavior['cross_formal'])
    def test_syn6_different_forms_parallel(self):self.assertTrue(self.behavior['different_form'])
    def test_different_lexemes_explicit_construction_family(self):
        raw=corpus();raw[13]['words'][0]['lex']='DBR[';m=model(raw)
        first=next(x for x in m['markers'] if x['clause_id']==101);second=next(x for x in m['markers'] if x['clause_id']==114)
        shared=set(first['family_ids'])&set(second['family_ids']);self.assertTrue(any(f['family_id'] in shared and f['family_type']=='PARTIAL_FORMAL_FAMILY' for f in m['families']))
    def test_nominal_heading_correspondence(self):
        raw=corpus()
        for i,lex in ((0,'XZWN/'),(13,'DBR/')):
            raw[i]['words'][0].update(lex=lex,sp='subs',pdp='subs',vt=None,vs=None)
        m=model(raw);a=next(x for x in m['markers'] if x['clause_id']==101);b=next(x for x in m['markers'] if x['clause_id']==114)
        self.assertIn('REVELATION_HEADING_CONFIGURATION',a['discovery_sources']);self.assertIn('REVELATION_HEADING_CONFIGURATION',b['discovery_sources']);self.assertTrue(set(a['family_ids'])&set(b['family_ids']))
    def test_syn7_formal_resumption(self):self.assertTrue(self.behavior['cross_resumption'])
    def test_syn8_singleton_closure(self):self.assertTrue(self.behavior['singleton'])
    def test_syn9_nested_configuration(self):self.assertTrue(any(r['nested_family_count']>3 for r in self.m['nested']))
    def test_syn10_same_family_different_coverage(self):
        ids=next(f['marker_ids'] for f in self.m['families'] if len(f['marker_ids'])>2);self.assertGreater(len({r['clause_count'] for r in self.m['coverage'] if r['marker_id'] in ids}),1)
    def test_syn11_boundary_invariance(self):self.assertTrue(self.behavior['metadata_invariance'])
    def test_syn12_outside_scope_untested(self):self.assertTrue(all(r['scope_external_status']=='OUTSIDE_SCOPE_NOT_TESTED' for r in self.m['coverage']))
    def test_syn13_not_nearest_only(self):self.assertTrue(any(int(r['competing_evidence']['distance'])>5 for r in self.m['relations']))
    def test_syn14_no_coverage_winner(self):self.assertTrue(self.behavior['no_winner'])
    def test_syn15_competing_relations(self):self.assertTrue(any('COMPETING_RELATIONS' in r['relation_candidates'] for r in self.m['relations']))
    def test_nested_range_exact(self):
        for r,n in zip(self.m['coverage'],self.m['nested']):
            nested=[m for m in self.m['markers'] if r['start_index']<m['sequence_index']<=r['end_index']]
            encoded=self.m['markers'][n['nested_marker_index_start']:n['nested_marker_index_end_exclusive']]
            self.assertEqual(nested,encoded);self.assertEqual(len({f for m in nested for f in m['family_ids']}),n['nested_family_count'])
    def test_signature_atoms_preserved(self):self.assertEqual({r['object_id'] for r in self.m['signatures'] if r['object_kind']=='clause_atom'},{a for c in self.m['observation'] for a in c['clause_atom_ids']})
    def test_provenance_no_inferred_chronology(self):self.assertEqual(provenance_class({'evidence_ids':['old']}),'PROVENANCE_UNCLEAR')
    def test_provenance_explicit_paths(self):
        self.assertEqual(provenance_class({'marker_first_provenance':{'structure_assumed_before_marker_discovery':True}}),'STRUCTURE_FIRST_CONTAMINATION')
        self.assertEqual(provenance_class({'marker_first_provenance':{'independent_blind_manifest_sha256':'h','discovery_before_judgment':True}}),'EVIDENCE_FIRST_BUT_NEEDS_READJUDICATION')
    def test_serialization_deterministic(self):self.assertEqual(cm.js(self.m),cm.js(model()))
    def test_release_gate_negatives(self):
        good=dict(tests_run=1860,failures=0,errors=0,skipped=0);self.assertTrue(all(gates.release_gates(b'a',b'a',good).values()));self.assertFalse(gates.release_gates(b'a',b'b',good)['DETERMINISTIC_RERUN'])
        bad=dict(good,failures=1);self.assertFalse(gates.release_gates(b'a',b'a',bad)['FULL_REGRESSION_PASS']);bad=dict(good,skipped=1);self.assertFalse(gates.release_gates(b'a',b'a',bad)['SKIP_ZERO'])
    def test_death_formula_not_merely_any_crosslink(self):
        e=deepcopy(self.e);e['control_checks']['death_formula_recovered']=0;self.assertFalse(gates.evaluate(e)['DEATH_CROSS_BOOK_RESUMPTION_RECOVERED'])
    def test_death_each_source_target_pair_required(self):
        e=deepcopy(self.e);e['control_checks']['death_pairs_recovered']=0;self.assertFalse(gates.evaluate(e)['DEATH_CROSS_BOOK_RESUMPTION_RECOVERED'])
    def test_manifest_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            cm.write(Path(d)/'a',b'a');cm.manifest(d,'manifest.csv');cm.write(Path(d)/'a',b'b');self.assertFalse(cm.verify(d,'manifest.csv'))

def negative(name):
    def test(self):
        e=deepcopy(self.e);damage(name,e);self.assertFalse(gates.evaluate(e)[name])
    return test
with tempfile.TemporaryDirectory() as _d:
    for _name in gates.evaluate(bundle(_d)):setattr(MFRTests,'test_negative_'+_name.lower(),negative(_name))

if __name__=='__main__':unittest.main()
