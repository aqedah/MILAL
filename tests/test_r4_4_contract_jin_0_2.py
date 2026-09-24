from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import milal_jin_io as io
import milal_jin_relation_rules as rules
import milal_jin_blind_linguistic_audit as blind
import milal_jin_postblind_human_comparison as post
import milal_jin_audit_pipeline as pipeline
import milal_jin_synthetic as synthetic


def edit(m,name,change):
    rr=deepcopy(io.rows(m['blind'][name]));change(rr);m['blind'][name]=io.csv_bytes(rr)


def placement(m,ref):return next(r for r in m['placements'] if r['reference']==ref)


MUTATIONS={
    'BLIND_PHASE_HUMAN_LABEL_LEAKAGE_ZERO':lambda m:edit(m,'02_blind_linguistic_features.csv',lambda rr:rr[0].update(human_judgment='forbidden')),
    'PHASE_A_HUMAN_SOURCE_COUNT_ZERO':lambda m:m['phase_a_meta'].update(human_source_count=1),
    'NO_BHSA_NATIVE_MOTHER_USED_BEFORE_BLIND_FREEZE':lambda m:m['phase_a_meta'].update(native_hierarchy_source_count=1),
    'BASELINE_COMMIT_VERIFIED':lambda m:m['baseline'].update(verified_commit='wrong'),
    'JIN_0_1_FROZEN_PRESERVED':lambda m:m['pins'][0].update(actual='wrong'),
    'BLIND_TARGET_SCHEMA_NEUTRAL':lambda m:edit(m,'01_blind_target_inventory.csv',lambda rr:rr[0].update(extra_label='forbidden')),
    'BLIND_DISCOVERY_COMPLETE_BEFORE_HUMAN_LOAD':lambda m:m['events'].reverse(),
    'NO_AUTOMATIC_WINNER':lambda m:m['placements'][0].update(selected_mother='auto'),
    'NO_WEIGHTED_SCORE':lambda m:edit(m,'03_blind_candidate_pairs.csv',lambda rr:rr[0]['evidence_flags'].update(MOTHER_SCORE=1)),
    'ALL_ELIGIBLE_HYPOTAXIS_CANDIDATES_PRESERVED':lambda m:m['blind'].update({'05_blind_hypotaxis_mother_candidates.csv':io.csv_bytes([dict(pair_id='fake',relation_candidate_status='UNADJUDICATED',automatic_resolution=False)])}),
    'CANDIDATE_UNIVERSE_ACCOUNTED':lambda m:m['phase_a_meta']['summary'].update(scanned_pair_count=-1),
    'HYPOTHESIS_COUNTS_COMPUTED':lambda m:m['phase_a_meta']['summary']['relation_hypotheses'].update(PARATAXIS_SUPPORTED=-1),
    'EXISTING_PARENT_3_BLINDLY_BACK_AUDITED':lambda m:next(r for r in m['crosswalk'] if r['comparison_family']=='HYPOTAXIS').update(comparison_status='invented'),
    'EXISTING_SAME_LEVEL_BLINDLY_BACK_AUDITED':lambda m:next(r for r in m['crosswalk'] if r['comparison_family']=='PARATAXIS').update(comparison_status='invented'),
    'HUMAN_COMPARISON_FACTS_ONLY':lambda m:m['crosswalk'][0].update(directive='KEEP_FOR_NOW'),
    'PLACEMENT_PROPOSALS_UNREVIEWED':lambda m:m['placements'][0].update(proposal_status='ACCEPTED'),
    'JOB_2_11_NO_MOTHER_ASSIGNED':lambda m:placement(m,'2:11').update(selected_mother='auto'),
    'JOB_32_1_NO_PARENT_ASSIGNED':lambda m:placement(m,'32:1').update(selected_mother='auto'),
    'ROOT_NOT_SELECTED':lambda m:m['placements'][0].update(selected_root=True),
    'BHSA_NATIVE_POSTBLIND_ONLY':lambda m:m['native_comparison'][0].update(blind_overwritten=True),
    'NATIVE_COMPARISON_REPRODUCIBLE':lambda m:m['native_comparison'][0].update(comparison_status='invented'),
    'NO_NEW_ACCEPTED_RELATION':lambda m:m['new_relations'].append('accepted'),
    'NO_NEW_PARENT_EDGE':lambda m:m['new_parent_edges'].append('parent'),
    'Q1_Q9_REMAIN_HISTORICAL_UNREVIEWED':lambda m:m['historical'].update({'11_revised_r4_4_contract_review_packet.md':b'ACCEPTED'}),
    'PARTICIPANT_ARC_UNADJUDICATED':lambda m:m.update(participant_arc='ACCEPTED'),
    'R4_4_CONSUMER_NOT_IMPLEMENTED':lambda m:m.update(consumer_implemented=True),
    'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m:m['historical'].update({'90_run_metadata.json':b'changed'}),
    'ALL_REVIEW_CASES_RETAINED':lambda m:m['review_cases'].pop(),
    'BLANK_HUMAN_REVIEW_FIELDS':lambda m:m['review_cases'][0].update(relation_decision='PARATAXIS'),
    'REPORTS_FAITHFUL':lambda m:m['reports'].update({'14_revised_contract_review_packet.md':b'wrong'}),
    'EXACT_RESEARCHER_REQUEST':lambda m:m.update(request=b'wrong'),
}
for gate in ('NO_EXISTING_HUMAN_RELATION_USED_AS_DISCOVERY_FEATURE','NO_COMPOSITION_MEMBERSHIP_USED_AS_DISCOVERY_FEATURE','NO_CYCLE_MEMBERSHIP_USED_AS_DISCOVERY_FEATURE','NO_SEAM_DECISION_USED_AS_DISCOVERY_FEATURE','SAME_LEVEL_NOT_USED_AS_DISCOVERY_INPUT','CHILD_OF_NOT_USED_AS_DISCOVERY_INPUT'):
    MUTATIONS[gate]=lambda m:m['phase_a_meta']['loaded_sources'].append('HUMAN_REGISTRY')
for gate,key in [('SAME_TYPE_PARATAXIS_CONTROL_PASS','S1'),('SAME_TYPE_HYPOTAXIS_CONTROL_PASS','S2'),('DIFFERENT_TYPE_PARATAXIS_CONTROL_PASS','S3'),('DIFFERENT_TYPE_HYPOTAXIS_CONTROL_PASS','S4'),('EXPLICIT_SUBORDINATE_CONTROL_PASS','S5'),('AMBIGUOUS_RELATION_PRESERVED','S6'),('MULTIPLE_MOTHER_CANDIDATES_PRESERVED','S7'),('SPEAKER_ALONE_INSUFFICIENT','S8'),('ADJACENCY_ALONE_INSUFFICIENT','S9'),('COMPOSITION_INPUT_REJECTED','S10')]:
    MUTATIONS[gate]=lambda m,key=key:m['controls'][key].update(extra='broken')


class IndependentJinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=TemporaryDirectory();cls.out=Path(cls.tmp.name)/'synthetic'
        pipeline.execute(out=cls.out,self_test=True)
        work=cls.out.with_name(cls.out.name+'_work')
        cls.m,cls.cfg=post.load(work/'blind',work/'synthetic_upstream_results.zip',pipeline.CONFIG,synthetic=True)
        pipeline.enrich(cls.m,cls.cfg);cls.rules=json.loads((ROOT/cls.cfg['rules_path']).read_bytes())

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_all_gates_pass_and_negative_coverage(self):
        gg=pipeline.gates(self.m,self.cfg)
        self.assertEqual({r['gate'] for r in gg},set(MUTATIONS))
        self.assertTrue(all(r['status']=='PASS' for r in gg))

    def test_all_ten_controls(self):
        c=pipeline.controls(self.rules);self.assertEqual(set(c),{f'S{i}' for i in range(1,11)})
        self.assertTrue(c['S1']['hypotheses'][0]['parataxis_supported']);self.assertTrue(c['S2']['hypotheses'][0]['hypotaxis_supported'])
        self.assertFalse(c['S3']['same_type']);self.assertTrue(c['S3']['hypotheses'][0]['parataxis_supported'])
        self.assertFalse(c['S4']['same_type']);self.assertTrue(c['S4']['hypotheses'][0]['hypotaxis_supported'])
        self.assertEqual(c['S5']['hypotheses'][0]['relation_hypothesis'],'HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED')
        self.assertEqual(c['S6']['hypotheses'][0]['relation_hypothesis'],'PARATAXIS_AND_HYPOTAXIS_SUPPORTED')
        self.assertEqual(len(c['S7']['hypotheses']),3)
        for key in ('S8','S9'):self.assertFalse(c[key]['hypotheses'][0]['parataxis_supported'] or c[key]['hypotheses'][0]['hypotaxis_supported'])
        self.assertTrue(c['S10']['composition_input_rejected'])

    def test_clause_type_identity_not_sufficient(self):
        cc=[synthetic.clause(1,verb='>MR[',subject='A/'),synthetic.clause(2,verb='HLK[',subject='B/',tense='impf')]
        ff=rules.extract(cc,self.rules);ev=rules.evidence(*ff,self.rules)
        self.assertTrue(ev['evidence_flags']['F_CLAUSE_TYPE_SAME']);self.assertFalse(ev['parataxis_supported'])

    def test_na_png_not_reference_evidence(self):
        self.assertFalse(rules.png_equal(('NA','NA','NA'),('NA','NA','NA')))
        cc=[synthetic.clause(1),synthetic.clause(2)];cc[1]['words'][0]['ps']='NA'
        ff=rules.extract(cc,self.rules);self.assertFalse(rules.evidence(*ff,self.rules)['parataxis_supported'])

    def test_all_predecessors_not_nearest_only(self):
        cc=[synthetic.clause(i,verse=i) for i in range(1,9)]
        m=blind.discover([dict(audit_target_id='JT0001',book='Job',chapter=1,verse=8)],cc,self.rules)
        self.assertEqual(m['summary']['scanned_predecessor_pair_count'],7)
        self.assertEqual({r['preceding_clause_id'] for r in m['pairs']},set(range(1,8)))

    def test_forward_context_is_distinct(self):
        self.assertGreater(self.m['phase_a_meta']['summary']['scanned_forward_context_pair_count'],0)
        self.assertTrue(any(r['target_role']=='TARGET_IS_EARLIER_CONTEXT' for r in io.rows(self.m['blind']['03_blind_candidate_pairs.csv'])))

    def test_neutral_schema_rejects_all_forbidden_fields(self):
        for key in blind.FORBIDDEN:
            with self.subTest(key=key),self.assertRaises(ValueError):blind.neutral({key:'x'})
        with self.assertRaises(ValueError):blind.neutral({'x':'H:HSA012'})

    def test_empty_inventory_rejected(self):
        with self.assertRaisesRegex(ValueError,'empty'):blind.inventory([],[])

    def test_phase_a_actual_forbidden_file_access_blocked(self):
        code="import sys;sys.path.insert(0,'src');import milal_jin_blind_linguistic_audit as a;from pathlib import Path;a.install_guard({},'results/unused');Path('config/hsa1_job.json').read_bytes()"
        r=subprocess.run([sys.executable,'-B','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('outside Phase A allowlist',r.stderr)

    def test_phase_a_actual_native_access_blocked(self):
        code="import sys;sys.path.insert(0,'src');import milal_jin_blind_linguistic_audit as a;from pathlib import Path;a.install_guard({},'results/unused');Path('mother.tf').read_bytes()"
        r=subprocess.run([sys.executable,'-B','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('outside Phase A allowlist',r.stderr)

    def test_phase_a_human_module_import_blocked(self):
        code="import sys;sys.path.insert(0,'src');import milal_jin_blind_linguistic_audit as a;a.install_guard({},'results/unused');import milal_hsa1_human_registry"
        r=subprocess.run([sys.executable,'-B','-c',code],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(r.returncode,0);self.assertIn('prohibited MILAL import',r.stderr)

    def test_phase_b_refuses_unfrozen_before_missing_human_file(self):
        with TemporaryDirectory() as temp:
            Path(temp,'bad').write_text('bad')
            with self.assertRaisesRegex(ValueError,'frozen before Phase B'):post.load(temp,'missing-human.zip','missing-config.json')

    def test_phase_b_does_not_change_blind_bytes(self):
        on_disk=io.read_dir(self.out.with_name(self.out.name+'_work')/'blind')
        self.assertEqual(on_disk,self.m['blind'])
        self.assertTrue(io.manifest_ok(on_disk,'07_blind_discovery_manifest.csv'))

    def test_historical_preserved_and_neutral_alias_projection_explicit(self):
        files=io.read_dir(self.out)
        self.assertEqual({k[len(post.HISTORY):]:v for k,v in files.items() if k.startswith(post.HISTORY)},self.m['historical'])
        alias=[r for r in self.m['crosswalk'] if 'EXPLICIT_ROLE_ALIAS_TO_LOCUS' in r['endpoint_projection']]
        self.assertTrue(alias);self.assertTrue(all(r['projection_scope'].endswith('NOT_AUTOMATIC_MACRO_RELATION') for r in alias))

    def test_synthetic_disagreement_does_not_rewrite_human(self):
        human=[r for r in self.m['crosswalk'] if r['comparison_family']=='HYPOTAXIS']
        self.assertEqual(len(human),3);self.assertTrue(all(r['comparison_status']==post.COMPARISONS[5] for r in human))
        self.assertEqual(self.m['new_relations'],[]);self.assertEqual(self.m['new_human_judgments'],[])

    def test_review_schema_extended_but_blank(self):
        self.assertTrue(self.m['review_cases'])
        for r in self.m['review_cases']:
            self.assertEqual(r['review_status'],'UNREVIEWED')
            for key in ('relation_decision','selected_mother_if_hypotactic','paratactic_peer_if_applicable','evidence_sufficient'):self.assertEqual(r[key],'')

    def test_review_cases_lossless_identity_dedup(self):
        pairs=io.rows(self.m['blind']['03_blind_candidate_pairs.csv'])
        self.assertEqual({p['pair_id'] for p in pairs},{p for c in self.m['review_cases'] for p in c['blind_pair_ids']})
        self.assertEqual(len(self.m['review_cases']),len({(p['preceding_clause_id'],p['later_clause_id']) for p in pairs}))

    def test_native_four_statuses(self):
        p=io.rows(self.m['blind']['03_blind_candidate_pairs.csv'])[0];h=io.rows(self.m['blind']['04_blind_relation_hypotheses.csv'])[0]
        bb={'03_blind_candidate_pairs.csv':io.csv_bytes([p]),'04_blind_relation_hypotheses.csv':io.csv_bytes([h])}
        child=int(p['later_clause_id']);parent=int(p['preceding_clause_id']);native={'mother':{child:[parent]},'rela':{child:'Coor'}}
        self.assertEqual(post.native_comparison(bb,native)[0]['comparison_status'],'BHSA_NATIVE_AGREES')
        h.update(parataxis_supported=False,hypotaxis_supported=True);bb['04_blind_relation_hypotheses.csv']=io.csv_bytes([h])
        self.assertEqual(post.native_comparison(bb,native)[0]['comparison_status'],'BHSA_NATIVE_DIFFERS')
        self.assertEqual(post.native_comparison(bb,{})[0]['comparison_status'],'BHSA_NATIVE_NO_DATA')
        self.assertEqual(post.native_comparison(bb,{'code':{child:200}})[0]['comparison_status'],'BHSA_NATIVE_NOT_COMPARABLE')

    def test_tf_implicit_node_ranges_and_escapes(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'x.tf';p.write_bytes(b'@node\n@version=2021\n@valueType=str\n\n1-2\ta\\tb\nc\n5\td\n')
            rr,_=io.read_tf(p);self.assertEqual(rr,{1:'a\tb',2:'a\tb',3:'c',5:'d'})
            p.write_bytes(b'@edge\n@version=2021\n\n10\t1-3\n4,6\n')
            rr,_=io.read_tf(p);self.assertEqual(rr,{10:[1,2,3],11:[4,6]})

    def test_tf_version_and_valued_edge_rejected(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/'x.tf';p.write_bytes(b'@node\n@version=2017\n\n1\ta\n')
            with self.assertRaises(ValueError):io.read_tf(p)
            p.write_bytes(b'@edge\n@version=2021\n@edgeValues\n\n1\t2\t3\n')
            with self.assertRaises(ValueError):io.read_tf(p)

    def test_raw_book_identity_filters_repeated_name_by_otype(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            features={name:'1-2\tNA\n' for name in io.RAW_FEATURES}
            features.update(book='10-12\tIob\n',otype='1-2\tword\n10\tbook\nchapter\nverse\nclause\nclause_atom\nphrase\n',
                oslots='10-15\t1-2\n',chapter='11\t1\n',verse='12\t1\n',typ='13\tWay0\n15\tVP\n',
                function='15\tPred\n',domain='13\tN\n',txt='13\tN\n',lex='1-2\tHJH[\n',sp='1-2\tverb\n',g_word_utf8='1-2\tx\n')
            for name,body in features.items():
                kind='edge' if name=='oslots' else 'node';value='int' if name in ('chapter','verse') else 'str'
                (root/(name+'.tf')).write_bytes(f'@{kind}\n@version=2021\n@valueType={value}\n\n{body}'.encode())
            cc,receipts=io.raw_corpus(root,book='Iob')
            self.assertEqual([c['clause_id'] for c in cc],[13]);self.assertEqual(cc[0]['word_nodes'],[1,2])
            self.assertEqual(len(receipts),len(io.RAW_FEATURES))
            with self.assertRaisesRegex(ValueError,'book identity'):io.raw_corpus(root,book='Job')

    def test_unknown_domain_is_not_correspondence_or_embedding_evidence(self):
        from milal_jin_synthetic import clause
        from milal_jin_relation_rules import extract,evidence
        rules=json.loads((pipeline.ROOT/self.cfg['rules_path']).read_bytes())
        cc=[clause(1),clause(2)]
        for c in cc:c['domain']='?'
        ff=extract(cc,rules);ev=evidence(*ff,rules)
        self.assertFalse(ev['evidence_flags']['D_SAME_DOMAIN']);self.assertFalse(ev['parataxis_supported'])
        cc[1]['domain']='Q';ff=extract(cc,rules);ev=evidence(*ff,rules)
        self.assertFalse(ev['evidence_flags']['D_DOMAIN_SHIFT']);self.assertFalse(ev['evidence_flags']['D_EMBEDDED_LINE_CANDIDATE'])

    def test_manifest_both_schemas_and_tampering(self):
        files={'x':b'data'};io.seal(files);self.assertTrue(io.manifest_ok(files));files['x']=b'bad';self.assertFalse(io.manifest_ok(files))
        self.assertTrue(io.manifest_ok(self.m['historical']))

    def test_deterministic_serialization_and_zip_negative(self):
        files=pipeline.finalize(deepcopy(self.m),self.cfg,True)
        self.assertEqual(files,io.read_dir(self.out))
        with TemporaryDirectory() as tmp:
            one=io.publish(files,Path(tmp)/'one');two=io.publish(files,Path(tmp)/'two')
            self.assertEqual(one.read_bytes(),two.read_bytes());self.assertNotEqual(one.read_bytes(),two.read_bytes()+b'bad')

    def test_existing_destination_refused(self):
        with self.assertRaisesRegex(ValueError,'already exists'):io.publish({'x':b'y'},self.out)

    def test_external_release_gates_and_negative_mutations(self):
        receipt=dict(tests_run=70,failures=0,errors=0,skipped=0)
        self.assertTrue(all(r['status']=='PASS' for r in pipeline.release_gates(b'zip',b'zip',receipt)))
        self.assertEqual(pipeline.release_gates(b'zip',b'changed',receipt)[0]['status'],'FAIL')
        self.assertEqual(pipeline.release_gates(b'',b'',receipt)[0]['status'],'FAIL')
        for key in ('failures','errors','skipped'):
            self.assertEqual(pipeline.release_gates(b'zip',b'zip',dict(receipt,**{key:1}))[1]['status'],'FAIL')
        self.assertEqual(pipeline.release_gates(b'zip',b'zip',dict(receipt,tests_run=0))[1]['status'],'FAIL')


def negative(gate,mutate):
    def test(self):
        m=deepcopy(self.m);mutate(m)
        self.assertEqual(next(r['status'] for r in pipeline.gates(m,self.cfg) if r['gate']==gate),'FAIL')
    return test


for gate,mutate in MUTATIONS.items():setattr(IndependentJinTests,'test_negative_'+gate.lower(),negative(gate,mutate))

if __name__=='__main__':unittest.main()
