from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_ana_response_family_addendum as h


def nominal(m,ref):return next(r for r in m['family'] if r['reference']==ref and r['response_layer']==h.LAYERS[1])
def neighbor(m,ref):return next(r for r in m['neighbors'] if r['reference']==ref)
def historical(key):return lambda m,s:m['historical'].update({key:b'changed'})


MUTATIONS={
 'BASELINE_0_1_ARTIFACT_VERIFIED':lambda m,s:m['baseline_receipt'].update(sha256='bad'),
 'FROZEN_SOURCE_FILES':lambda m,s:s['frozen'][0].update(actual='bad'),
 'VERBAL_ANA_INVENTORY_FROZEN':lambda m,s:m['family'][0].update(category='CHANGED'),
 'NOMINAL_MAANEH_DETECTED':lambda m,s:nominal(m,'32:3').update(category='VERBAL'),
 'SHWB_WHOLE_BOOK_COVERAGE':lambda m,s:m['neighbors'].pop(),
 'SHWB_SEMANTIC_DISAMBIGUATION_PRESENT':lambda m,s:neighbor(m,'1:21').update(category='SEMANTIC_REPLY_SHWB'),
 'DABAR_NOT_PROMOTED_TO_CORE_RESPONSE_LEXEME':lambda m,s:m['context'][0].update(core_ana_lexeme=True),
 'JOB_32_RESPONSE_CLUSTER_COMPLETE':lambda m,s:m['cluster'].pop(),
 'DISTRIBUTION_LAYERS_SEPARATE':lambda m,s:m['distribution'][0].update(CORE_ANA_FAMILY_COUNT=999),
 'CANDIDATE_COUNT_UNCHANGED':lambda m,s:m['addendum'][3]['original_candidate_record'].update(candidate_type='RENAMED'),
 'CANDIDATE_EVIDENCE_ADDENDUM_EXACT':lambda m,s:m['addendum'][1].update(direct_new_evidence_ids=['invented']),
 'NO_AUTOMATIC_REFINEMENT':lambda m,s:m['addendum'][3].update(selected_alternative='RESPONSE_ROLE_INTERVENTION'),
 'REVIEW_STATUS_UNCHANGED':lambda m,s:m['questions'][1].update(review_status='REVIEWED'),
 'NO_NEW_HUMAN_JUDGMENT':lambda m,s:m['new_human_judgments'].append('invented'),
 'NO_NEW_STRUCTURAL_RELATION':lambda m,s:m['new_structural_relations'].append('RESPONSE_TO'),
 'FROZEN_HSA_UNCHANGED':historical(h.R43+'10_human_judgment_accounting.csv'),
 'HSA3_PREP_UNCHANGED':historical('history/hsa3_prep/03_global_seam_cases.csv'),
 'CRITERIA_REGISTRY_DIMENSION_SPECIFIC':lambda m,s:m['registry'][0].update(admissible_for=['ALL']),
 'NO_GLOBAL_EVIDENCE_WEIGHTING':lambda m,s:m['registry'][0].update(weight=1),
 'BHSA_MOTHER_NOT_AUTO_PARENT':lambda m,s:neighbor(m,'32:14').update(automatic_parent_ids=['BHSA_MOTHER']),
 'NEGATIVE_CONTROLS_PRESENT':lambda m,s:m['negative'].pop(),
 'EXACT_0_1_CROSSWALK':lambda m,s:m['crosswalk'][0].update(original_occurrence_id='FUZZY'),
 'FROZEN_JUDGMENT_CRITERIA_CROSSWALK':lambda m,s:m['human_crosswalk'][0].update(adjudication_changed=True),
 'SEAM_DEPENDENCY_ONLY':lambda m,s:m['dependencies'][0].update(resolves_parentage=True),
 'NATIVE_SOURCE_IDENTITY':lambda m,s:m['native'][0]['words'][0].update(lex='BAD'),
 'LOCAL_CONTINUATION_PANELS':lambda m,s:m['panels'].pop(),
 'METHODOLOGY_DRAFT_FAITHFUL':lambda m,s:m.update(methodology='invented'),
 'REVIEW_PACKET_FAITHFUL':lambda m,s:m.update(report='adjudicated'),
 'DETERMINISTIC_RERUN':lambda m,s:m.update(rerun_digest='nondeterministic'),
}


class FamilyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.s=h.load(self_test=True);cls.m=h.build(cls.s);cls.files=h.serialize(cls.m,cls.s)

    def test_positive_gates_and_complete_negative_coverage(self):
        gg=h.gates(self.m,self.s);self.assertTrue(all(g['status']=='PASS' for g in gg));self.assertEqual(set(MUTATIONS),{g['gate'] for g in gg})

    def test_baseline_manifest_and_sha_validation(self):
        cfg=deepcopy(self.s['cfg']);cfg['archive'].update(sha256=self.s['receipt']['sha256'],members=len(self.s['files']))
        cfg['expected'].update(verbal=len(self.s['verbal']),homonyms=sum(not r['answer_lexeme'] for r in self.s['verbal']))
        h.baseline_audit(self.s['files'],cfg,self.s['receipt']['sha256'])
        with self.assertRaisesRegex(ValueError,'SHA'):h.baseline_audit(self.s['files'],cfg,'bad')

    def test_baseline_tampered_file_stops(self):
        f=deepcopy(self.s['files']);f['01_ana_occurrence_inventory.csv']+=b'changed'
        with self.assertRaisesRegex(ValueError,'manifest'):h.baseline_audit(f,self.s['cfg'],'bad',True)

    def test_frozen_count_assertions_configured(self):
        self.assertEqual(self.s['cfg']['expected']['verbal'],62);self.assertEqual(self.s['cfg']['expected']['homonyms'],2)
        self.assertEqual(len([r for r in self.m['family'] if r['response_layer']==h.LAYERS[0]]),len(self.s['verbal']))

    def test_homonym_rows_unchanged(self):
        before=[r for r in self.s['verbal'] if not r['answer_lexeme']]
        after=[r['original_record'] for r in self.m['family'] if r['response_layer']==h.LAYERS[0] and not r['answer_sense']]
        self.assertEqual(after,before);self.assertEqual(len(after),2)

    def test_nominal_32_3(self):self.assertEqual(nominal(self.m,'32:3')['category'],'CORE_ANA_NOMINAL_COGNATE')
    def test_nominal_32_5(self):self.assertEqual(nominal(self.m,'32:5')['category'],'CORE_ANA_NOMINAL_COGNATE')

    def test_nominal_root_unavailable_not_reconstructed(self):
        r=nominal(self.m,'32:3');self.assertEqual(r['root_availability'],'ROOT_UNAVAILABLE');self.assertFalse(r['direct_root_derivation_asserted'])

    def test_same_spelling_different_lexeme_excluded(self):
        r=nominal(self.m,'37:24');self.assertEqual(r['category'],'NON_RESPONSE_SIMILAR_FORM');self.assertFalse(r['counts_as_response_family'])

    def test_same_root_different_gloss_excluded(self):self.assertFalse(nominal(self.m,'32:13')['counts_as_response_family'])

    def test_nominal_selection_not_verse_whitelist(self):
        s=deepcopy(self.s);w=next(w for c in s['native'] for w in c['words'] if w['lex']=='M<NH=/');w['reference']='2:13'
        self.assertIn(w['node'],[r['word_node'] for r in h.nominal(s)])

    def test_nominal_requires_lex_gloss_and_pos(self):
        for field,value in [('gloss','hiding place'),('lex','M<NH/'),('sp','prep')]:
            s=deepcopy(self.s);w=next(w for c in s['native'] for w in c['words'] if w['lex']=='M<NH=/');w[field]=value
            self.assertFalse(next(r for r in h.nominal(s) if r['word_node']==w['node'])['counts_as_response_family'])

    def test_32_3_5_original_no_ana_preserved(self):
        focus=h.a.prep.decode_rows(self.m['historical']['02_ana_focus_loci.csv'])
        for ref in ('32:3','32:5'):self.assertEqual(next(r for r in focus if r['reference']==ref)['status'],'NO_ANA')

    def test_crosswalk_simultaneous_no_verbal_and_nominal(self):
        for ref in ('32:3','32:5'):
            r=next(r for r in self.m['crosswalk'] if r['reference']==ref and r['response_layer']==h.LAYERS[1])
            self.assertEqual((r['original_focus_status'],r['verbal_status'],r['addendum_category']),('NO_ANA','NO_VERBAL_ANA_AT_THIS_WORD','CORE_ANA_NOMINAL_COGNATE'))

    def test_32_14_reply_evidence_components(self):
        r=neighbor(self.m,'32:14');self.assertEqual(r['category'],'SEMANTIC_REPLY_SHWB');self.assertEqual(r['vs'],'hif');self.assertEqual(r['pronominal_object_evidence']['ps'],'p3');self.assertTrue(r['utterance_complement_word_ids']);self.assertTrue(r['negation_evidence'])

    def test_32_14_without_utterance_evidence_stays_unresolved(self):
        s=deepcopy(self.s)
        for c in s['native']:
            if c['ref']=='32:14':
                for w in c['words']:
                    if w['lex']=='>MR/':w['lex']='OTHER'
        self.assertEqual(next(r for r in h.shwb(s) if r['reference']=='32:14')['category'],'UNRESOLVED_SHWB')

    def test_hif_not_automatically_reply(self):
        self.assertEqual(neighbor(self.m,'1:21')['category'],'RETURN_RESTORE_SHWB');self.assertEqual(neighbor(self.m,'1:22')['category'],'UNRESOLVED_SHWB')

    def test_second_shwb_lexeme_not_silently_dropped(self):
        s=deepcopy(self.s);w=next(w for c in s['native'] for w in c['words'] if w['lex']=='CWB[');w['lex']='CWB=['
        self.assertIn(w['node'],[r['word_node'] for r in h.shwb(s)])

    def test_33_13_exact_verbal_id_crosswalk(self):
        r=next(r for r in self.s['verbal'] if r['reference']=='33:13');self.assertIn(r['occurrence_id'],[x['original_occurrence_id'] for x in self.m['crosswalk']])

    def test_33_14_only_context_candidate(self):
        r=self.m['context'][0];self.assertEqual(r['relation_candidate'],'POSSIBLE_RESPONSE_REFRAMING');self.assertEqual(r['status'],'UNADJUDICATED');self.assertIs(r['automatic_resolution'],False);self.assertFalse(r['core_ana_lexeme']);self.assertFalse(r['semantic_response_neighbor'])

    def test_dabar_elsewhere_not_selected(self):
        self.assertFalse(any(r['lex']=='DBR[' for r in self.m['family']+self.m['neighbors']))
        self.assertEqual([r['reference'] for r in self.m['context']],['33:14'])

    def test_cluster_required_and_canonical_order(self):
        self.assertTrue(set(self.s['cfg']['cluster']['required'])<={r['reference'] for r in self.m['cluster']})
        self.assertEqual(self.m['cluster'],sorted(self.m['cluster'],key=lambda r:(h.order(r['reference']),r['word_node'],r['response_layer'])))

    def test_32_13_not_response_occurrence(self):self.assertNotIn('32:13',[r['reference'] for r in self.m['cluster']])

    def test_continuation_panels_present(self):self.assertTrue(set(self.s['cfg']['cluster']['controls'])<={r['reference'] for r in self.m['panels']})

    def test_36_1_frozen_control(self):self.assertEqual(next(r['status'] for r in self.m['negative'] if r['control']=='36_1_ADD_SPEECH_NO_ANA'),'PASS')
    def test_3_2_frozen_control(self):self.assertEqual(next(r['status'] for r in self.m['negative'] if r['control']=='3_2_FORMAL_NOT_RESPONSE'),'PASS')

    def test_four_original_candidate_types_preserved(self):self.assertEqual([r['original_candidate_record'] for r in self.m['addendum']],self.s['candidates']);self.assertEqual(len(self.m['addendum']),4)

    def test_c4_refinement_not_rename_or_selection(self):
        r=self.m['addendum'][3];self.assertEqual(r['original_candidate_type'],'ELIHU_WITHIN_ANA_RESPONSE_INTERVAL');self.assertEqual(r['refinement_candidate_label'],'ELIHU_RESPONSE_ROLE_INTERVENTION');self.assertEqual(r['refinement_status'],'UNADJUDICATED');self.assertFalse(r['selected_alternative'])

    def test_review_questions_unchanged(self):self.assertEqual(self.m['questions'],self.s['questions']);self.assertTrue(all(q['review_status']=='UNREVIEWED' for q in self.m['questions']))
    def test_new_judgments_and_relations_zero(self):self.assertEqual(self.m['new_human_judgments'],[]);self.assertEqual(self.m['new_structural_relations'],[])

    def test_frozen_59_human_and_57_unresolved(self):
        self.assertEqual(len(self.s['accounting']),59);self.assertEqual(len(h.a.prep.decode_rows(self.m['historical'][h.R43+'03_unresolved_parentage.csv'])),57)

    def test_a_to_g_and_closure_bytes_unchanged(self):
        for member in ['history/hsa3_prep/03_global_seam_cases.csv',h.R43+'history/hsa2_f/03_final_closure_relations.csv']:
            self.assertEqual(self.m['historical'][member],self.s['files'][member])

    def test_37_24_not_antecedent(self):self.assertEqual(next(r['status'] for r in self.m['negative'] if r['control']=='37_24_ADJACENCY_INSUFFICIENT'),'PASS')

    def test_no_weights_ranks_or_priorities(self):
        for r in self.m['registry']+self.m['distribution']:self.assertFalse(any(term in k.lower() for term in ('weight','score','rank','priority') for k in r))

    def test_seven_relation_dimensions(self):self.assertEqual(len(h.criteria.DIMENSIONS),7);self.assertEqual(len(self.m['registry']),24)

    def test_mother_not_parent(self):self.assertTrue(all(not r.get('automatic_parent_ids') for r in self.m['family']+self.m['neighbors']+self.m['context']))

    def test_every_candidate_resolution_false(self):self.assertTrue(all(r['automatic_resolution'] is False for r in self.m['context']+self.m['addendum']))

    def test_criteria_crosswalk_is_draft_not_human_reasoning_reconstruction(self):
        self.assertEqual(len(self.m['human_crosswalk']),21);self.assertTrue(all('NOT_RECONSTRUCTED' in r['mapping_status'] and not r['adjudication_changed'] for r in self.m['human_crosswalk']))

    def test_all_row_hash_links_resolve(self):
        files=self.files;cache={}
        for row in self.m['family']+self.m['neighbors']+self.m['context']+self.m['human_crosswalk']:
            member=row['source_member']
            if member not in cache:cache[member]=h.a.prep.r43.h1.read_csv(files[member])
            self.assertEqual(h.rowhash(cache[member][row['source_data_row']-1]),row['source_row_sha256'])

    def test_manifest_negative_path(self):
        files=deepcopy(self.files);self.assertTrue(h.util.manifest_ok(files));files['04_job_32_response_cluster.csv']+=b'bad';self.assertFalse(h.util.manifest_ok(files))

    def test_independent_process_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            archives=[]
            for name in ('first','repeat'):
                out=Path(temp)/name
                result=subprocess.run([sys.executable,str(h.ROOT/'src/milal_hsa3_ana_response_family_addendum.py'),'--self-test','--out',str(out)],capture_output=True,text=True)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
                zp=out.with_name(name+'_results.zip');archives.append(zp.read_bytes())
                with zipfile.ZipFile(zp) as z:self.assertIsNone(z.testzip())
            self.assertEqual(*archives)


def negative(name,mutate):
    def test(self):
        m,s=deepcopy(self.m),deepcopy(self.s);mutate(m,s)
        self.assertEqual(next(r['status'] for r in h.gates(m,s) if r['gate']==name),'FAIL')
    return test


for name,mutate in MUTATIONS.items():setattr(FamilyTests,'test_negative_gate_'+name.lower(),negative(name,mutate))
if __name__=='__main__':unittest.main()
