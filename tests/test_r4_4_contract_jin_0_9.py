"""Independent discovery semantics, process isolation and every gate's negative."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_jin_io as io
import milal_jin_top_level_common as common
import milal_jin_strict_top_level_audit as strict
import milal_jin_macro_top_level_audit as macro
import milal_jin_top_level_pipeline as pipe
from milal_jin_top_level_synthetic import corpus,history_fixture
from milal_jin_synthetic import clause
from milal_jin_human_batch import release_gates

ROOT=pipe.ROOT
LING=json.loads((ROOT/'config/jin_blind_linguistic_rules.json').read_bytes())
RULES=json.loads((ROOT/'config/jin_top_level_rules.json').read_bytes())


def model():
    cfg=json.loads(pipe.CONFIG.read_bytes());history,cfg=history_fixture(cfg);phases={}
    for role,builder in [('S',strict.build),('M',macro.build)]:
        built=builder(corpus(),LING,RULES);f=built['files'];f['raw_inventory.json']=io.js(corpus())
        f['06_strict_blind_source_audit.csv' if role=='S' else '15_macro_blind_source_audit.csv']=io.csv_bytes([dict(source_id='SYNTHETIC_RAW_CORPUS',human_source=False,native_hierarchy_source=False)])
        f['metadata.json']=io.js(dict(linguistic_rules=LING,rules=RULES,human_source_count=0,human_label_leakage=0,native_hierarchy_source_count=0,loaded_sources=['SYNTHETIC_RAW_CORPUS'],allowed_configurations=common.CONFIGURATIONS[role]));io.seal(f,pipe.MANIFESTS[role]);phases[role]=f
    m=pipe.assemble(phases,history,cfg,'SYNTHETIC',['S_FREEZE_VERIFIED','M_FREEZE_VERIFIED','HUMAN_ARCHIVE_OPENED','POSTBLIND_COMPARISON'],True)
    return m,cfg


class TopLevelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.m,cls.c=model()
    def test_valid_gates(self):self.assertTrue(all(pipe.gates(self.m,self.c).values()))
    def sb(self,raw):return strict.build(raw,LING,RULES)['model']
    def mb(self,raw):return macro.build(raw,LING,RULES)['model']
    def test_S1_unique_strict_candidate_with_daughter(self):
        m=self.sb([clause(1),clause(2,relative=True)])
        self.assertIn('S_CONFIG_ONE_UNIQUE_ROOT_CANDIDATE',[r['configuration'] for r in m['hypotheses']]);self.assertFalse(any(r['selected'] for r in m['hypotheses']))
    def test_S2_multiple_paratactic_main_clauses(self):
        m=self.sb([clause(i+1) for i in range(5)])
        self.assertIn('S_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_CANDIDATES',[r['configuration'] for r in m['hypotheses']])
    def test_S3_scope_initial_not_unique(self):
        m=self.sb([clause(1,verb='HLK[',subject='A/'),clause(2,verb='DBR[',subject='B/')])
        self.assertNotIn('S_CONFIG_ONE_UNIQUE_ROOT_CANDIDATE',[r['configuration'] for r in m['hypotheses']]);self.assertFalse(m['top'][0]['selected_root'])
    def test_S4_explicit_daughter_single_candidate(self):
        m=self.sb([clause(1),clause(2,relative=True)]);rr=[r for r in m['relations'] if r['explicit_local_dependency']]
        self.assertEqual(len(rr),1);self.assertEqual(rr[0]['selected_mother'],'')
    def test_S5_multiple_mother_candidates_preserved(self):
        m=self.sb([clause(1),clause(2),clause(3,relative=True)])
        self.assertEqual({r['preceding_clause_id'] for r in m['relations'] if r['later_clause_id']==3 and r['explicit_local_dependency']},{1,2})
    def test_actual_clause_internal_observation(self):
        c=clause(1);c['words'][-1].update(sp='verb',vt='infc',lex='HLK[');c['phrases'][-1]['function']='Objc'
        m=self.sb([c]);self.assertEqual(len(m['internal']),1);self.assertEqual(m['internal'][0]['scope'],'WITHIN_ONE_ACTUAL_CLAUSE');self.assertFalse(m['relations'])
    def test_M1_higher_frame_and_nested_units(self):
        m=self.mb(corpus());self.assertEqual(m['frame']['candidate_kind'],'WHOLE_BOOK_FRAME_CANDIDATE')
        self.assertTrue(any(r['candidate_kind']=='M_MACRO_CONTAINMENT_POSSIBLE' for r in m['relations']))
    def test_M2_multiple_macro_peers(self):
        m=self.mb(corpus());self.assertIn('M_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_UNITS',[r['configuration'] for r in m['hypotheses']])
    def test_M3_local_strict_daughter_not_macro_mother(self):
        raw=corpus();m=self.mb(raw);s=self.sb(raw)
        self.assertTrue(any(r['later_clause_id']==10 and r['explicit_local_dependency'] for r in s['relations']))
        self.assertFalse(any(r['target_clause_id']==10 and r['candidate_kind']=='M_MACRO_CONTAINMENT_POSSIBLE' for r in m['relations']))
    def test_M4_frame_does_not_select_root(self):
        m=self.mb(corpus());self.assertTrue(m['frame']['shared_participant_surfaces']);self.assertFalse(m['frame']['root_selected']);self.assertFalse(m['frame']['span_created'])
    def test_M5_technical_root_rejected(self):
        raw=corpus();raw[0]['surface']='JOB_BOOK'
        with self.assertRaises(ValueError):self.mb(raw)
    def test_M6_composition_input_rejected(self):
        raw=corpus();raw[0]['composition_group']='OPENING_NARRATIVE_COMPLEX'
        with self.assertRaises(ValueError):self.mb(raw)
    def test_M7_longer_coverage_no_winner(self):
        m=self.mb(corpus());self.assertTrue(any(r['coverage_evidence']['candidate_coverage_end_if_observable'] for r in m['top']))
        self.assertTrue(all(not r['selected_root'] for r in m['top']))
    def test_same_type_alone_insufficient_and_different_type_allowed(self):
        x=self.sb([clause(1,verb='HLK[',subject='A/'),clause(2,verb='DBR[',subject='B/')]);self.assertFalse(any(r['evidence_bundle']['parataxis_supported'] for r in x['relations']))
        x=self.sb([clause(1),clause(2,typ='WayX')]);self.assertTrue(any(r['evidence_bundle']['parataxis_supported'] for r in x['relations']))
    def test_reference_changes_do_not_seed_discovery(self):
        a=corpus();b=deepcopy(a)
        for c in b:c['chapter']=99;c['verse']+=40;c['reference']='99:'+str(c['verse'])
        x=self.mb(a);y=self.mb(b)
        self.assertEqual([r['clause_id'] for r in x['top']],[r['clause_id'] for r in y['top']]);self.assertEqual([r['candidate_kind'] for r in x['relations']],[r['candidate_kind'] for r in y['relations']])
    def test_recomputed_independent_builds(self):
        self.assertEqual(strict.build(corpus(),LING,RULES),strict.build(corpus(),LING,RULES));self.assertEqual(macro.build(corpus(),LING,RULES),macro.build(corpus(),LING,RULES))
    def test_parataxis_does_not_confirm_historical_hypotaxis(self):
        import milal_jin_top_level_postblind as post
        h,c=history_fixture(self.c);rr=io.rows(h['01_hierarchy_relation_inventory.csv'])
        rr[0].update(source_clause_id=[5],target_clause_id=[1],source_ref='1:5',target_ref='1:1')
        h['01_hierarchy_relation_inventory.csv']=io.csv_bytes(rr);io.seal(h)
        p=post.compare(self.m['models']['S'],self.m['models']['M'],h,c,True)
        r=next(r for r in p['strict'] if r['comparison_id']=='STRICT_UNRESOLVED:SYN:E1')
        self.assertEqual(r['status'],'S_ALTERNATIVE_SUPPORTED');self.assertFalse(r['automatic_resolution'])
    def test_manifest_mutation(self):
        f=deepcopy(self.m['phases']['S']);f['raw_inventory.json']+=b'x';self.assertFalse(io.manifest_ok(f,pipe.MANIFESTS['S']))
    def test_release_negatives(self):
        receipt=dict(tests_run=1,failures=0,errors=0,skipped=0);self.assertEqual(release_gates(b'a',b'b',receipt)[0]['status'],'FAIL')
        for k in ('failures','errors','skipped'):
            r=dict(receipt);r[k]=1;self.assertEqual(release_gates(b'a',b'a',r)[1]['status'],'FAIL')
    def test_isolation_actual_forbidden_read(self):
        self.guard_probe("Path('docs/HANDOFF.md').read_bytes()")
    def test_isolation_actual_human_import(self):
        self.guard_probe('import milal_jin_contract_freeze')
    def test_isolation_other_audit_import(self):
        self.guard_probe('import milal_jin_macro_top_level_audit')
    def test_isolation_native_read(self):
        self.guard_probe("Path('mother.tf').read_bytes()")
    def guard_probe(self,statement):
        code="import sys;from pathlib import Path;sys.path.insert(0,'src');import milal_jin_top_level_common as c;c.guard({},Path('results/guard_probe'),c.BASE_SAFE);"+statement
        r=subprocess.run([sys.executable,'-B','-X','utf8','-c',code],cwd=ROOT,capture_output=True,text=True,encoding='utf8');self.assertNotEqual(r.returncode,0);self.assertIn('forbidden' if 'import ' in statement else 'allowlist',r.stderr)


def mutate(g,m):
    p=m['post'];s=m['models']['S'];a=m['models']['M']
    if g=='BASELINE_EXACT':m['baseline']='wrong'
    elif g=='JIN_0_8_FROZEN_CONTRACT_VERIFIED':p['contract']['contract_status']='wrong'
    elif g=='FROZEN_REPOSITORY_PINS':m['pins']={}
    elif g=='EXACT_RESEARCHER_SOURCE':m['request']=b'wrong'
    elif g=='HISTORICAL_250_RELATIONS_UNCHANGED':p['historical_relations'].pop()
    elif g.startswith(('S_','M_')) and any(g.endswith(x) for x in ('HUMAN_SOURCE_COUNT_ZERO','HUMAN_LABEL_LEAKAGE_ZERO','NATIVE_HIERARCHY_INPUT_ZERO','SOURCE_READ_ALLOWLIST','FROZEN_BEFORE_POSTBLIND','EVIDENCE_RECOMPUTES','CONFIGURATION_SCHEMA')):
        role=g[0];f=m['phases'][role];meta=json.loads(f['metadata.json'])
        if g.endswith('HUMAN_SOURCE_COUNT_ZERO'):meta['human_source_count']=1
        elif g.endswith('HUMAN_LABEL_LEAKAGE_ZERO'):meta['human_label_leakage']=1
        elif g.endswith('NATIVE_HIERARCHY_INPUT_ZERO'):meta['native_hierarchy_source_count']=1
        elif g.endswith('SOURCE_READ_ALLOWLIST'):meta['loaded_sources'].append('HUMAN')
        elif g.endswith('FROZEN_BEFORE_POSTBLIND'):m['events']=['HUMAN_ARCHIVE_OPENED','S_FREEZE_VERIFIED','M_FREEZE_VERIFIED','POSTBLIND_COMPARISON']
        elif g.endswith('EVIDENCE_RECOMPUTES'):m['models'][role]['top'].pop()
        else:meta['allowed_configurations']=[]
        f['metadata.json']=io.js(meta)
    elif g=='ALL_JOB_CLAUSES_INVENTORIED':s['inventory'].pop()
    elif g=='EXPLICIT_HYPOTAXIS_CONTROLS_RECOVERED':
        for r in s['relations']:r['explicit_local_dependency']=False
    elif g=='PARATAXIS_POSSIBILITY_PRESERVED':
        for r in s['relations']:r['evidence_bundle']['parataxis_supported']=False
    elif g=='NO_ALL_CLAUSE_ONE_MOTHER':s['relations'][0]['selected_mother']='forced'
    elif g=='SCOPE_INITIAL_NOT_ROOT':s['top'][0]['selected_root']=True
    elif g in ('M_GENERIC_ONSET_DISCOVERY','M_GENERIC_CLOSURE_DISCOVERY','M_REPEATED_FAMILIES_PRODUCED'):a[{'M_GENERIC_ONSET_DISCOVERY':'onsets','M_GENERIC_CLOSURE_DISCOVERY':'closures','M_REPEATED_FAMILIES_PRODUCED':'families'}[g]].pop()
    elif g=='M_MULTIPLE_EVIDENCE_CONTAINMENT':next(r for r in a['relations'] if r['candidate_kind']=='M_MACRO_CONTAINMENT_POSSIBLE')['evidence_bundle']={}
    elif g=='M_NO_LONGEST_COVERAGE_WINNER':a['top'][0]['selected_root']=True
    elif g=='NO_NUMERIC_RANKING':a['top'][0]['root_score']=1
    elif g=='NO_TECHNICAL_COMPOSITION_ROOT':p['groups'][0]['root_candidate']=True
    elif g=='POSTBLIND_SOURCE_ORDER':m['events'].reverse()
    elif g=='BLIND_OUTPUTS_UNMUTATED':m['phases']['S']['raw_inventory.json']+=b'x'
    elif g in ('STRICT_POSTBLIND_COMPARISON','MACRO_POSTBLIND_COMPARISON','GROUPS_POSTBLIND_ONLY','CROSS_LAYER_COMPARISON','OPEN_SCOPE_IMPACT_LOSSLESS'):
        p[{'STRICT_POSTBLIND_COMPARISON':'strict','MACRO_POSTBLIND_COMPARISON':'macro','GROUPS_POSTBLIND_ONLY':'groups','CROSS_LAYER_COMPARISON':'cross','OPEN_SCOPE_IMPACT_LOSSLESS':'impacts'}[g]].pop()
    elif g=='SAME_ANCHOR_NOT_AUTO_UNIFIED':p['cross'][0]['automatic_unification']=True
    elif g=='ONLY_TWO_ROOT_SCOPES_DIRECT':p['impacts'][0]['direct_review']=False
    elif g=='REMAINING_SCOPES_NOT_RESOLVED':p['impacts'][-1]['resolved']=True
    elif g=='HUMAN_REVIEW_FIELDS_BLANK':p['questions'][0]['review_status']='ACCEPTED'
    elif g in ('JOB_2_11_UNCHANGED','JOB_32_1_UNCHANGED'):p['mother_status']['2:11' if '2_11' in g else '32:1']='ASSIGNED'
    elif g in ('NO_NEW_HUMAN_JUDGMENT','NO_NEW_PARENT_EDGE','NO_NEW_ROOT','NO_NEW_MACRO_RELATION','NO_NEW_STRICT_RELATION','NO_MIGRATION'):
        p[{'NO_NEW_HUMAN_JUDGMENT':'new_human_judgments','NO_NEW_PARENT_EDGE':'new_parent_edges','NO_NEW_ROOT':'new_roots','NO_NEW_MACRO_RELATION':'new_macro_relations','NO_NEW_STRICT_RELATION':'new_strict_relations','NO_MIGRATION':'migrations'}[g]].append('forbidden')
    elif g=='PARTICIPANT_ARC_UNTOUCHED':p['participant_arc']='ACCEPTED'
    elif g=='R4_4_CONSUMER_ABSENT':p['consumer_implemented']=True
    else:raise AssertionError('missing negative '+g)


def negative(g):
    def test(self):
        m=deepcopy(self.m);mutate(g,m);self.assertFalse(pipe.gates(m,self.c)[g])
    return test

_m,_c=model()
for _g in pipe.gates(_m,_c):setattr(TopLevelTests,'test_negative_'+_g.lower(),negative(_g))

if __name__=='__main__':unittest.main()
