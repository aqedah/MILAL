import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_mfr_common as cm
from milal_mfr01b_synthetic import dataset
from milal_mfr01b_core import build
from milal_mfr01b_roles import audit as roles
from milal_mfr01b_evidence import audit as evidence,components
from milal_mfr01b_configuration import build as configurations
from milal_mfr01b_gates import core_gates,release_gates,final_gates
from milal_mfr01b_io import scan

def release_fixture():
    return dict(baseline=True,raw_integrity=True,consolidated_integrity=True,controls=dict(speech_word=True,speech_activity=True,contrast=True,external=True),static_issues=[],readsets=[True],events=['ROLE_AND_RELATION_OUTPUTS_FROZEN','CONTROLS_LOADED'],human_rows=[dict(selected_relation='')],human_fields=['selected_relation'],consumers=[],participant_arc='UNADJUDICATED',manifests=[True])

def damage(name,d,o):
    if name=='MARKER_ROLE_AUDIT_COMPLETE':o['roles'].pop()
    elif name=='PRIMARY_FORMAL_VS_SUPPORT_SIGNAL_DISTINGUISHED':o['roles'][0]['formal_role_sources'].append('DOMAIN_CONFIGURATION_CHANGE')
    elif name=='SUPPORT_ONLY_MARKERS_PRESERVED':next(r for r in o['roles'] if r['role']=='SUPPORT_SIGNAL_ONLY')['force_context_usable']=False
    elif name=='RAW_BUNDLE_FAMILY_IDS_PRESERVED':o['bundles'][0]['raw_family_ids'].pop()
    elif name=='CESSATION_ROLE_AUDIT_COMPLETE':o['cessations'].pop()
    elif name=='CESSATION_LEXEME_NOT_EQUAL_DISCOURSE_CESSATION':next(r for r in o['cessations'] if r['physical_temporal_arguments'])['role_candidate']='DISCOURSE_CESSATION_FORM_CANDIDATE'
    elif name=='RELATION_PROVENANCE_COMPLETE':o['evidence']=[e for e in o['evidence'] if e['raw_relation_id']!=next(iter(d['r']))]
    elif name=='COVERAGE_CESSATION_DERIVATION_TRACKED':next(e for e in o['evidence'] if e['provenance_family']=='EVID_COVERAGE_CESSATION_DERIVED')['dependency_root_ids']=['FAKE']
    elif name=='NESTED_FROM_COVERAGE_DERIVATION_TRACKED':next(e for e in o['evidence'] if e['provenance_family']=='EVID_NESTED_FROM_COVERAGE')['dependency_root_ids']=['FAKE']
    elif name=='DEPENDENT_EVIDENCE_NOT_DOUBLE_COUNTED':o['closures'][0]['cessation_derived_chains'].append(dict(dependency_root_ids=['fake'],evidence_ids=['fake']))
    elif name=='RAW_963_CLOSURE_PAIRS_PRESERVED':o['closures'].pop()
    elif name=='CESSATION_DERIVED_ONLY_ARCHIVE_SUPPORTED':o['closures'][0]['review_eligible']=not o['closures'][0]['review_eligible']
    elif name=='SUPPORT_NOT_STANDALONE_CLOSURE_SOURCE':o['closures'][0]['source_primary_bearing']=not o['closures'][0]['source_primary_bearing']
    elif name=='DEPENDENCY_GRAPH_VALID':o['edges'].append(dict(raw_relation_id='x',node_id='fake',parent_id='fake',edge_type='DEPENDENCY_ROOT'))
    elif name=='CONFIGURATION_LEVEL_CASES_CREATED':o['configurations'][0]['bundle_ids']=[]
    elif name=='RAW_PAIR_TRACEABILITY_COMPLETE':o['membership'][0]['raw_candidate_labels'].append('FAKE')
    elif name=='HIERARCHY_32_RAW_PAIRS_PRESERVED':next(c for c in o['configurations'] if c['hierarchy_pair_ids'])['hierarchy_pair_ids'].pop()
    elif name=='HIERARCHY_CONFIGURATION_CASES_GENERATED':o['h1'].pop()
    elif name=='PHASE_SPECIFIC_REVIEW_SETS_GENERATED':o['r1'][0]['bundle_ids']=[]
    elif name=='NO_BOOK_BOUNDARY_FILTER':
        for c in o['configurations']:c['cross_book']=False
    elif name=='SUPPORT_NOT_STANDALONE_FORMAL_REVIEW':
        bid=next(b['bundle_id'] for b in o['bundles'] if b['bundle_role']=='SUPPORT_ONLY_BUNDLE');next(b for b in o['family_review'] if b['bundle_id']==bid)['standalone_formal_review']=True
    elif name=='NO_NUMERIC_RANKING':o['roles'][0]['score']=10
    else:o['roles'][0][{'NO_HUMAN_JUDGMENT':'human_judgment','NO_ACCEPTED_RELATION':'accepted_relation','NO_PARENT':'mother','NO_HIERARCHY':'hierarchy'}[name]]='INVENTED'

class MFR01BTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d,_=dataset();cls.rules=json.loads((cm.ROOT/'config/mfr_0_1b_role_rules.json').read_bytes());cls.o=build(cls.d,cls.rules)
    def test_positive_gates(self):self.assertTrue(all(core_gates(self.d,self.o,self.rules).values()))
    def test_release_positive(self):self.assertTrue(all(release_gates(release_fixture()).values()))
    def role_with(self,tags):
        d=deepcopy(self.d);m=d['markers'][0];m['discovery_sources']=tags
        return next(r for r in roles(d,self.rules)['roles'] if r['marker_id']==m['marker_id'])
    def test_s1_subject_only(self):self.assertEqual(self.role_with(['EXPLICIT_SUBJECT_CONFIGURATION_SHIFT'])['role'],'SUPPORT_SIGNAL_ONLY')
    def test_s2_domain_only(self):self.assertEqual(self.role_with(['DOMAIN_CONFIGURATION_CHANGE'])['role'],'SUPPORT_SIGNAL_ONLY')
    def test_s3_formula_subject(self):self.assertEqual(self.role_with(['REPEATED_CLAUSE_FORMULA','EXPLICIT_SUBJECT_CONFIGURATION_SHIFT'])['role'],'COMPOSITE_MARKER_CANDIDATE')
    def test_s4_physical_cessation_not_discourse(self):
        r=next(r for r in self.o['cessations'] if r['physical_temporal_arguments']);self.assertEqual(r['role_candidate'],'NON_DISCOURSE_CESSATION_USAGE_CANDIDATE');self.assertEqual(r['human_acceptance'],'')
    def test_s5_word_argument(self):self.assertTrue(any(r['speech_arguments'] and r['role_candidate']=='DISCOURSE_CESSATION_FORM_CANDIDATE' for r in self.o['cessations']))
    def test_s6_answer_infinitive(self):
        r=next(r for r in self.o['cessations'] if r['speech_infinitive_candidates']);self.assertEqual(r['role_candidate'],'SPEECH_ACTIVITY_CESSATION_CANDIDATE');self.assertEqual(r['speech_infinitive_candidates'][0]['link_basis'],'ADJACENT_PREPOSITIONAL_INFINITIVE_CANDIDATE')
    def chain_fixture(self,onset=False):
        d=deepcopy(self.d);r=next(r for r in d['relations'] if 'CLOSURE_TARGET_CANDIDATE' in r['relation_candidates']);d['relations']=[r]
        s=d['m'][r['source_marker_id']];s['discovery_sources']=['DOMAIN_CONFIGURATION_CHANGE'];s['family_ids']=[]
        if onset:
            s['discovery_sources']=['REPEATED_CLAUSE_FORMULA'];s['family_ids']=['FSLOT'];d['f']['FSLOT']=dict(family_type='SLOT_NORMALIZED_FAMILY')
        r.update(exact_form_correspondence=False,construction_correspondence=False,context_before_correspondence=False,context_after_correspondence=False,participant_correspondence=[],domain_correspondence=False,resumption_evidence=dict(lexical_participant=False,temporal_context_recurrence=False,death_temporal=False))
        r['coverage_relationship']=[c for c in r['coverage_relationship'] if d['c'][c]['end_basis']=='EXPLICIT_CLOSURE']
        return evidence(d,roles(d,self.rules),self.rules)
    def test_s7_derived_chain_once(self):
        e,edges,c=self.chain_fixture();self.assertEqual(len(c[0]['cessation_derived_chains']),1);self.assertFalse(c[0]['independent_evidence_ids']);self.assertFalse(c[0]['review_eligible']);self.assertIn('CLOSURE_CESSATION_DERIVED_ONLY',c[0]['statuses'])
    def test_s8_independent_onset_separate(self):
        e,edges,c=self.chain_fixture(True);self.assertEqual(len(c[0]['cessation_derived_chains']),1);self.assertTrue(c[0]['independent_evidence_ids']);self.assertTrue(c[0]['review_eligible'])
    def five_pairs(self):
        d=deepcopy(self.d);seed=deepcopy(next(iter(d['m'].values())));d['m']={};d['markers']=[];d['observation']=deepcopy(d['observation'][:6]);d['by_marker']={}
        for i in range(6):
            mid='M'+str(i);m=deepcopy(seed);m.update(marker_id=mid,sequence_index=i,clause_id=d['observation'][i]['clause_id'],clause_atom_ids=[100+i]);d['m'][mid]=m;d['markers'].append(m);d['by_marker'][mid]=['B'+mid]
        d['families']=[dict(family_id='SEQ',family_type='MULTI_CLAUSE_CONFIGURATION_FAMILY',occurrence_count=2,signature_resolution='SIG_SEQUENCE_3',marker_ids=['M0','M3'])]
        d['relations']=[];d['old_cross']={}
        for i,(a,b) in enumerate([(0,3),(1,4),(2,5),(0,4),(1,5)]):
            rid='R'+str(i);r=dict(relation_candidate_id=rid,source_marker_id='M'+str(a),target_marker_id='M'+str(b),relation_candidates=['PARATAXIS_CANDIDATE'],resumption_evidence={},cross_book=False);d['relations'].append(r);d['old_cross'][rid]={'case_id':'OLD'+rid}
        d['r']={r['relation_candidate_id']:r for r in d['relations']};return d
    def test_s9_five_pairs_one_configuration(self):
        c,m=configurations(self.five_pairs(),[]);self.assertEqual((len(c),len(m)),(1,5));self.assertEqual(len(c[0]['raw_pair_ids']),5)
    def test_no_sequence_witness_no_merge(self):
        d=self.five_pairs();d['families']=[];c,m=configurations(d,[]);self.assertEqual(len(c),5)
    def test_nonadjacent_witness_not_enough(self):
        d=self.five_pairs();d['relations']=d['relations'][:3:2];d['r']={r['relation_candidate_id']:r for r in d['relations']};c,m=configurations(d,[]);self.assertEqual(len(c),2)
    def test_s10_metadata_does_not_select(self):
        d=deepcopy(self.d)
        for m in d['markers']:m.update(book='Different',chapter=999,verse=888)
        changed=build(d,self.rules);self.assertEqual(self.o['configurations'],changed['configurations']);self.assertEqual(self.o['family_review'],changed['family_review'])
    def test_s11_support_context_not_standalone(self):
        r=next(r for r in self.o['roles'] if r['role']=='SUPPORT_SIGNAL_ONLY');self.assertTrue(r['force_context_usable']);self.assertFalse(r['primary_bearing'])
    def test_s12_all_raw_traceable(self):self.assertEqual({r['raw_relation_id'] for r in self.o['membership']},set(self.d['r']))
    def test_duplicate_roots_form_one_component(self):
        self.assertEqual(len(components([dict(evidence_id='a',dependency_root_ids=['x']),dict(evidence_id='b',dependency_root_ids=['y']),dict(evidence_id='c',dependency_root_ids=['x','y'])])),1)
    def test_unknown_discovery_source_fails(self):
        d=deepcopy(self.d);d['markers'][0]['discovery_sources']=['INVENTED']
        with self.assertRaisesRegex(ValueError,'untyped'):roles(d,self.rules)
    def test_deterministic_reordering(self):
        d=deepcopy(self.d);d['relations'].reverse();other=build(d,self.rules);self.assertEqual(cm.js(self.o),cm.js(other))
    def test_static_safeguards(self):
        self.assertEqual(scan(),[]);self.assertTrue(scan({'roles':'if reference == "31:40": pass'}));self.assertTrue(scan({'roles':'import milal_jin_top_level_postblind'}));self.assertTrue(scan({'roles':'if r["book"] == x["book"]: pass'}))
    def test_syntax(self):
        for p in (cm.ROOT/'src').glob('milal_mfr01b_*.py'):ast.parse(p.read_text(encoding='utf8'))
    def test_blind_read_guard(self):
        script=f"import sys;sys.path.insert(0,{str(cm.ROOT/'src')!r});from milal_mfr01b_io import guard;from pathlib import Path;guard([],{str(cm.ROOT/'results')!r});Path({str(cm.ROOT/'docs/HANDOFF.md')!r}).read_bytes()"
        p=subprocess.run([sys.executable,'-B','-c',script],capture_output=True,text=True);self.assertNotEqual(p.returncode,0);self.assertIn('blind read outside allowlist',p.stderr)
    def test_external_determinism_negative(self):self.assertFalse(final_gates('a','b',dict(tests_run=2026,failures=0,errors=0,skipped=0))['DETERMINISTIC_RERUN'])
    def test_external_regression_negative(self):self.assertFalse(final_gates('a','a',dict(tests_run=2026,failures=1,errors=0,skipped=0))['FULL_REGRESSION_PASS'])
    def test_external_skip_negative(self):self.assertFalse(final_gates('a','a',dict(tests_run=2026,failures=0,errors=0,skipped=1))['SKIP_ZERO'])

def core_negative(name):
    def test(self):
        d,o=deepcopy(self.d),deepcopy(self.o);damage(name,d,o);self.assertFalse(core_gates(d,o,self.rules)[name])
    return test

def release_negative(name):
    def test(self):
        e=release_fixture()
        mapping={'BASELINE_COMMIT_VERIFIED':'baseline','MFR_0_1_FROZEN_VERIFIED':'raw_integrity','MFR_0_1A_FROZEN_VERIFIED':'consolidated_integrity'}
        controls={'JOB_31_40_POSTFREEZE_CONTROL_PRESENT':'speech_word','JOB_32_1_POSTFREEZE_CONTROL_PRESENT':'speech_activity','NONDISCOURSE_CESSATION_CONTROLS_PRESENT':'contrast','CROSS_CORPUS_CONTROLS_PRESERVED':'external'}
        if name in mapping:e[mapping[name]]=False
        elif name in controls:e['controls'][controls[name]]=False
        elif name=='NO_REFERENCE_HARDCODING_IN_DISCOVERY':e['static_issues']=['reference']
        elif name=='BLIND_READSET_VALID':e['readsets']=[False]
        elif name=='OUTPUTS_FROZEN_BEFORE_CONTROLS':e['events'].reverse()
        elif name=='HUMAN_FIELDS_BLANK':e['human_rows'][0]['selected_relation']='DECIDED'
        elif name=='R4_4_CONSUMER_ABSENT':e['consumers']=['consumer']
        elif name=='PARTICIPANT_ARC_UNTOUCHED':e['participant_arc']='RESOLVED'
        elif name=='MANIFEST_VALID':e['manifests']=[False]
        else:raise AssertionError(name)
        self.assertFalse(release_gates(e)[name])
    return test

_d,_=dataset();_rules=json.loads((cm.ROOT/'config/mfr_0_1b_role_rules.json').read_bytes());_o=build(_d,_rules)
for _gate in core_gates(_d,_o,_rules):setattr(MFR01BTests,'test_negative_'+_gate.lower(),core_negative(_gate))
for _gate in release_gates(release_fixture()):setattr(MFR01BTests,'test_negative_'+_gate.lower(),release_negative(_gate))
del _d,_o,_rules
if __name__=='__main__':unittest.main()
