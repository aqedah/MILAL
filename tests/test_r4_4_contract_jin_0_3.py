from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import milal_jin_io as io
import milal_jin_context_pipeline as pipeline
import milal_jin_context_configuration as cc
import milal_jin_postcontext_comparison as post
from milal_jin_context_synthetic import controls,fixture


def edit(m,name,fn):
    rr=io.rows(m['c1'][name]);fn(rr);m['c1'][name]=io.csv_bytes(rr)


def meta(m,key,value):
    r=json.loads(m['c1']['29_c1_metadata.json']);r[key]=value;m['c1']['29_c1_metadata.json']=io.js(r)


def human(m,family):next(r for r in m['comparisons'] if r['relation_family']==family)['context_comparison_status']='BAD'


MUTATIONS={
 'BASELINE_EXACT':lambda m:m.update(baseline='bad'),
 'FROZEN_SOURCE_PINS':lambda m:m['pins'][0].update(actual='bad'),
 'JIN_0_2_ARTIFACT_VERIFIED':lambda m:m['history'].update({'90_run_metadata.json':b'bad'}),
 'SUPPORTED_PAIR_COUNTS_PRESERVED':lambda m:edit(m,'01_context_supported_pair_inventory.csv',lambda rr:rr[0]['source_hypothesis'].update(relation_hypothesis='BAD')),
 'INSUFFICIENT_ARCHIVE_PRESERVED':lambda m:edit(m,'08_insufficient_pair_archive.csv',lambda rr:rr[0].update(default_human_review=True)),
 'ALL_PAIRS_LOSSLESS':lambda m:edit(m,'08_insufficient_pair_archive.csv',lambda rr:rr[0]['source_pair'].update(preceding_ref='changed')),
 'ALL_SUPPORTED_CONTEXT_BUNDLES':lambda m:edit(m,'04_context_correspondence.csv',lambda rr:rr[0]['preceding_bundle_ids'].pop()),
 'SUPPORTED_MAPPING_COMPLETE':lambda m:edit(m,'07_contextual_case_membership.csv',lambda rr:rr.pop()),
 'NO_SUPPORTED_PAIR_DROPPED':lambda m:edit(m,'06_contextual_relation_cases.csv',lambda rr:rr[0]['member_pair_ids'].pop()),
 'PAIR_IDS_TRACEABLE':lambda m:edit(m,'06_contextual_relation_cases.csv',lambda rr:rr[0].update(member_pair_count='999999')),
 'ALL_PAIR_DISPOSITIONS_TRACEABLE':lambda m:edit(m,'11_pairwise_to_contextual_crosswalk.csv',lambda rr:rr[0].update(disposition='DROPPED')),
 'CANDIDATES_UNADJUDICATED':lambda m:edit(m,'06_contextual_relation_cases.csv',lambda rr:rr[0].update(automatic_resolution=True)),
 'REVIEW_CASE_REDUCTION':lambda m:m['review'].clear(),
 'CONTEXT_CORRESPONDENCE_COMPUTED':lambda m:edit(m,'04_context_correspondence.csv',lambda rr:rr[0].update(configuration_status='BAD')),
 'SCOPE_CLASSIFICATION_COMPUTED':lambda m:edit(m,'05_relation_scope_classification.csv',lambda rr:rr[0].update(clause_relation_scope='BAD')),
 'FIXED_ADAPTIVE_WINDOWS_PRESERVED':lambda m:edit(m,'02_context_windows.csv',lambda rr:rr[0].update(surface='BAD')),
 'ORDERED_SIGNATURES_COMPUTED':lambda m:edit(m,'03_context_signatures.csv',lambda rr:rr[0].update(participant_identity='BAD')),
 'CONTROL_CONTEXTS_GENERATED':lambda m:m['controls'][0].update(human_decision='FILLED'),
 'WAYHI_CONTRAST_CAPTURED':lambda m:m['synthetic_controls'].update(S2=False),
 'WAYHI_REPEATED_CONFIGURATION_CAPTURED':lambda m:m['synthetic_controls'].update(S1=False),
 'ALL_SYNTHETIC_CONTROLS':lambda m:m['synthetic_controls'].update(S12=False),
 'JOB_2_11_SCOPE_CLASSIFIED':lambda m:m['special']['2:11'].pop(),
 'JOB_32_1_SCOPE_CLASSIFIED':lambda m:m['special']['32:1'].pop(),
 'CLAUSE_INTERNAL_EXCLUDED_FROM_MACRO':lambda m:edit(m,'09_clause_internal_hypotaxis.csv',lambda rr:rr.pop()),
 'MACRO_MOTHER_POOL_PROJECTABLE_ONLY':lambda m:edit(m,'10_contextual_macro_mother_candidates.csv',lambda rr:rr.append(dict(pair_id='BAD',clause_internal_only=False))),
 'NO_MOTHER_SELECTED':lambda m:edit(m,'06_contextual_relation_cases.csv',lambda rr:rr[0].update(selected_mother='JT0001')),
 'NO_ACCEPTED_PARATAXIS':lambda m:meta(m,'accepted_parataxis',['BAD']),
 'NO_ACCEPTED_HYPOTAXIS':lambda m:meta(m,'accepted_hypotaxis',['BAD']),
 'NO_NEW_HUMAN_JUDGMENT_OR_PARENT':lambda m:meta(m,'new_parent_edges',['BAD']),
 'C1_HUMAN_SOURCE_COUNT_ZERO':lambda m:meta(m,'human_source_count',1),
 'C1_HUMAN_LABEL_LEAKAGE_ZERO':lambda m:meta(m,'human_label_leakage_count',1),
 'C1_COMPOSITION_SOURCE_COUNT_ZERO':lambda m:meta(m,'composition_source_count',1),
 'C1_NATIVE_HIERARCHY_SOURCE_COUNT_ZERO':lambda m:meta(m,'native_hierarchy_source_count',1),
 'C1_FREEZE_BEFORE_HUMAN_LOAD':lambda m:m['events'].reverse(),
 'C2_CANNOT_MUTATE_C1':lambda m:m['c1_after'].update({'tampered':b'x'}),
 'SAME_LEVEL_POSTBLIND_ONLY':lambda m:human(m,'PARATAXIS'),
 'MOTHER_JUDGMENTS_POSTBLIND_ONLY':lambda m:human(m,'HYPOTAXIS'),
 'PAIRWISE_CONTEXT_BOTH_PRESERVED':lambda m:m['comparisons'][0].update(historical_relation_unchanged=False),
 'REVIEW_UNIVERSE_COMPUTED':lambda m:m['review'].pop(),
 'ARCHIVE_NOT_DEFAULT_REVIEW':lambda m:m['review'][0].update(member_pair_ids=[io.rows(m['c1']['08_insufficient_pair_archive.csv'])[0]['pair_id']],default_human_review=True,case_origin='BLIND_CONTEXTUAL_CASE'),
 'REVIEW_FIELDS_BLANK':lambda m:m['review'][0].update(relation_decision='HYPOTACTIC'),
 'CONTEXTUAL_PLACEMENTS_APPEND_ONLY':lambda m:m['placements'][0].update(automatic_supersession=True),
 'NO_NUMERIC_RELATION_SCORE':lambda m:edit(m,'06_contextual_relation_cases.csv',lambda rr:rr[0].update(score=1)),
 'NO_CANDIDATE_RANKING':lambda m:m['review'][0].update(rank=1),
 'NO_ARBITRARY_REVIEW_CAP':lambda m:meta(m,'rules',dict(json.loads(m['c1']['29_c1_metadata.json'])['rules'],case_cap=50)),
 'PARTICIPANT_ARC_UNTOUCHED':lambda m:meta(m,'participant_arc','ADJUDICATED'),
 'R4_4_CONSUMER_ABSENT':lambda m:meta(m,'consumer_implemented',True),
 'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m:m['history'].update({'90_run_metadata.json':b'bad'}),
 'C1_MANIFEST_VALID':lambda m:m['c1'].update({'14_context_blind_manifest.csv':b'bad'}),
 'REPORTS_FAITHFUL':lambda m:m['reports'].update({'27_next_adjudication_scope.md':b'bad'}),
 'EXACT_REQUEST':lambda m:m.update(request=b'bad'),
}


class ContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=TemporaryDirectory();cls.out=Path(cls.tmp.name)/'synthetic';pipeline.execute(out=cls.out,self_test=True)
        work=cls.out.with_name(cls.out.name+'_work')
        cls.m,cls.cfg=post.load(work/'c1',work/'synthetic_jin02_results.zip',pipeline.CONFIG,True);pipeline.enrich(cls.m,cls.cfg)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_all_gates_and_negative_coverage(self):
        gg=pipeline.gates(self.m,self.cfg,True)
        self.assertTrue(all(r['status']=='PASS' for r in gg),gg);self.assertEqual(set(MUTATIONS),{r['gate'] for r in gg})

    def test_twelve_synthetic_controls(self):self.assertEqual(controls(),{f'S{i}':True for i in range(1,13)})

    def test_actual_forbidden_human_file_read(self):
        code="import sys;from pathlib import Path;sys.path.insert(0,'src');from milal_jin_contextual_relation_audit import install_guard;install_guard({},Path('results/c1_guard_test'));Path('docs/HANDOFF.md').read_bytes()"
        r=subprocess.run([sys.executable,'-B','-X','utf8','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('C1 forbidden read',r.stderr)

    def test_actual_forbidden_native_file_read(self):
        code="import sys;from pathlib import Path;sys.path.insert(0,'src');from milal_jin_contextual_relation_audit import install_guard;install_guard({},Path('results/c1_guard_test'));Path('mother.tf').read_bytes()"
        r=subprocess.run([sys.executable,'-B','-X','utf8','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('C1 forbidden read',r.stderr)

    def test_actual_human_module_import_blocked(self):
        code="import sys;from pathlib import Path;sys.path.insert(0,'src');from milal_jin_contextual_relation_audit import install_guard;install_guard({},Path('results/c1_guard_test'));import milal_r3c_0_2_reviewability"
        r=subprocess.run([sys.executable,'-B','-X','utf8','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('C1 forbidden import',r.stderr)

    def test_freeze_required_before_missing_human_sources(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp);(p/'14_context_blind_manifest.csv').write_bytes(b'bad')
            with self.assertRaisesRegex(ValueError,'C1 freeze first'):post.load(p,p/'missing.zip',p/'missing.json')

    def test_c1_bytes_unchanged_and_history_lossless(self):
        f=io.read_dir(self.out)
        self.assertEqual(self.m['c1'],io.read_dir(self.out.with_name(self.out.name+'_work')/'c1'))
        self.assertTrue(all(f[post.HISTORY+k]==v for k,v in self.m['history'].items()))
        self.assertTrue(io.manifest_ok(f))

    def test_insufficient_has_full_pair_and_hypothesis(self):
        c=post.tables(self.m['c1']);self.assertTrue(c['archive'])
        self.assertTrue(all(r['source_pair']['pair_id']==r['source_hypothesis']['pair_id']==r['pair_id'] for r in c['archive']))

    def test_no_similarity_identity_merge(self):
        c=post.tables(self.m['c1'])
        for r in c['cases']:
            self.assertEqual(r['case_id'],f"JC:{r['earlier_neutral_locus']}:{r['later_neutral_locus']}:{r['relation_family']}:{r['projection_scope']}")

    def test_boundary_windows_clipped_and_distinct(self):
        c=post.tables(self.m['c1']);byfocal={}
        for w in c['windows']:byfocal.setdefault(w['focal_clause_id'],set()).add(w['window_type'])
        self.assertTrue(all(len(x)==5 for x in byfocal.values()))
        first=min(int(k) for k in byfocal)
        fixed=next(w for w in c['windows'] if int(w['focal_clause_id'])==first and w['window_type']=='FIXED_MINUS3_PLUS3')
        self.assertLessEqual(len(fixed['clause_ids']),4)

    def test_unknown_domain_not_exact_configuration(self):
        self.assertEqual(cc.categorical(None,None),'NOT_AVAILABLE')
        from milal_jin_synthetic import clause
        from milal_jin_relation_rules import extract
        rules=json.loads((ROOT/'config/jin_blind_linguistic_rules.json').read_bytes())
        raw=[clause(1),clause(2)]
        for r in raw:r['domain']='?'
        ff=extract(raw,rules);self.assertNotEqual(cc.clause_comparison(*ff),'MATCH')

    def test_next_formula_probe_is_descriptive_and_beyond_fixed_window(self):
        from milal_jin_synthetic import clause
        from milal_jin_relation_rules import extract
        rules=json.loads((ROOT/'config/jin_blind_linguistic_rules.json').read_bytes());r=json.loads((ROOT/'config/jin_context_rules.json').read_bytes())
        ff=extract([clause(i,verb='HLK[') for i in range(1,8)],rules)
        ff[5]['formula_atoms']=['ANSWER_SAY']
        context=cc.Context(ff,[],r);w=context.bundle(1)[0]
        self.assertEqual(w['clause_ids'],[1,2,3,4]);self.assertEqual(w['next_raw_formula']['clause_id'],6)
        self.assertEqual(w['next_raw_formula']['clause_distance'],5)

    def test_macro_pool_does_not_contain_internal_hypotaxis(self):
        c=post.tables(self.m['c1']);internal={r['pair_id'] for r in c['clause_internal']}
        self.assertFalse(internal & {r['pair_id'] for r in c['macro_mothers']})

    def test_historical_proposals_append_not_supersede(self):
        self.assertTrue(all(r['historical_proposal_status']=='PAIRWISE_ONLY_PLACEMENT_PROPOSAL' and r['automatic_supersession'] is False for r in self.m['placements']))

    def test_packet_six_sections_and_blank_answers(self):
        packet=self.m['reports']['25_contextual_human_review_packet.md'].decode()
        for heading in 'ABCDEF':self.assertIn('## '+heading+' — ',packet)
        self.assertTrue(all(r['review_status']=='UNREVIEWED' and r['macro_projection_decision']=='' for r in self.m['review']))

    def test_final_manifest_negative(self):
        f=io.read_dir(self.out);self.assertTrue(io.manifest_ok(f));f['90_run_metadata.json']=b'bad';self.assertFalse(io.manifest_ok(f))

    def test_deterministic_serialization_and_external_gate_negatives(self):
        from milal_jin_audit_pipeline import release_gates
        f=pipeline.finalize(deepcopy(self.m),self.cfg,True);self.assertEqual(f,io.read_dir(self.out))
        receipt=dict(tests_run=1,failures=0,errors=0,skipped=0)
        with TemporaryDirectory() as tmp:
            a=io.publish(f,Path(tmp)/'a').read_bytes();b=io.publish(f,Path(tmp)/'b').read_bytes()
            self.assertTrue(all(r['status']=='PASS' for r in release_gates(a,b,receipt)))
            self.assertEqual(release_gates(a,b+b'bad',receipt)[0]['status'],'FAIL')
            self.assertEqual(release_gates(a,b,dict(receipt,skipped=1))[1]['status'],'FAIL')


def negative(gate,mutate):
    def test(self):
        m=deepcopy(self.m);mutate(m)
        self.assertEqual(next(r['status'] for r in pipeline.gates(m,self.cfg,True) if r['gate']==gate),'FAIL')
    return test


for key,mutate in MUTATIONS.items():setattr(ContextTests,'test_negative_'+key.lower(),negative(key,mutate))

if __name__=='__main__':unittest.main()
