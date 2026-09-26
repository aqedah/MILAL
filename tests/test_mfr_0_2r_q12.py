"""Q1.2 semantic, negative gate and streaming integration tests."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q12_synthetic import semantic_checks,evidence_fixture,MUTATIONS,data,GRAMMAR,clause,self_test
from milal_q12_pipeline import indexes,blind,write
from milal_q12_validation import measurements,GATES,policy
from milal_q12_binding import compare_configurations,pair_anchors
from milal_q12_profiles import profile
from milal_q12_controls import controls,diagnostics,SCOPES
from milal_q12_runner import reports
from milal_q1_binding import identity,pivot,outcome
from milal_mfr02r_data import table,rows,digest,manifest,verify_manifest


class Q12Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.checks=semantic_checks()[0];cls.evidence=evidence_fixture()

    def test_positive_gates(self):self.assertTrue(all(r['passed'] for r in measurements(self.evidence)))

    def test_gate_mutations_complete(self):self.assertEqual(set(GATES),{g for g,_ in MUTATIONS})

    def test_same_role_not_whole_phrase_identity(self):
        c,_,_=indexes(data(),GRAMMAR)
        c.profiles['3']['participant_grammatical_roles'][0]['lexemes'].append('EXTRA/')
        self.assertTrue(pair_anchors(c.profiles['1'],c.profiles['3']))

    def test_different_roles_do_not_anchor(self):
        c,_,_=indexes(data(),GRAMMAR)
        c.profiles['3']['participant_grammatical_roles'][0]['function']='Objc'
        self.assertFalse(pair_anchors(c.profiles['1'],c.profiles['3']))

    def test_pair_specific_frame_retains_five_fields(self):
        c,_,_=indexes([clause(1,10,0,subject=None,time='DAY/'),clause(2,20,1,subject=None,time='DAY/')],GRAMMAR)
        w=pair_anchors(c.profiles['1'],c.profiles['2'])[0]
        self.assertTrue(all(w[k] for k in ('source_frame','target_frame','shared_structural_basis','formal_difference','provenance')))

    def test_pronoun_frame_not_explicit_nominal_anchor(self):
        c,_,_=indexes([clause(1,10,0,subject=None,time='HE'),clause(2,20,1,subject=None,time='HE')],GRAMMAR)
        for p in c.profiles.values():p['temporal_adjuncts'][0]['nominals'][0]['sp']='prps'
        self.assertFalse(pair_anchors(c.profiles['1'],c.profiles['2']))

    def test_tested_edge_cannot_bound_own_overlapping_units(self):
        c,_,_=indexes(data(),GRAMMAR)
        c.configurations['3']=copy.deepcopy(c.configurations['1'])
        self.assertFalse(compare_configurations(c,'1','3','1','1')['positive_source_binding'])

    def test_no_fixed_window_across_fixture_gaps(self):
        d=data();d[1]['word_ids']=[99];d[1]['WORD'][0]['node']=99;d[1]['PHRASE'][0]['word_ids']=[99]
        self.assertEqual(indexes(d,GRAMMAR)[0].configurations['1']['members'],['1'])

    def test_missing_source_schema_fails(self):
        d=data()[0];del d['REFERENCE']
        with self.assertRaisesRegex(ValueError,'required profile'):profile(d,GRAMMAR['lexicons'])

    def test_nominal_person_na_preserved_not_invented(self):
        d=[clause(1,10,0),clause(2,20,1,subject=None,reference=True)]
        d[0]['WORD'][1]['ps']='NA'
        c,r,b=indexes(d,GRAMMAR)
        w=r.by_target['2'][0]
        self.assertEqual(w['reference_status'],'UNIQUE_SURFACE_CANDIDATE')
        self.assertIn('GENDER_NUMBER_COMPATIBLE_PERSON_UNSPECIFIED_ONLY',w['antecedent_basis'])
        self.assertEqual(r.candidates[w['reference_witness_id']][0]['png'][0],'NA')
        self.assertFalse(r.bindings('1','2'))

    def test_deferred_valency_prior_blocks_configuration(self):
        b=indexes(data(),GRAMMAR)[2]
        r=b.evaluate('1','3',[dict(rule_id='W-P01',relation='PARATACTIC')],True)
        self.assertFalse(r['qualified_paths']);self.assertIn('DEFERRED',r['disqualification_reason'])

    def test_original_match_is_required(self):
        self.assertFalse(indexes(data(),GRAMMAR)[2].evaluate('1','3',[])['qualified_paths'])

    def test_unselected_is_not_pivot(self):
        self.assertNotEqual(pivot('3',[outcome('1','3','PARATACTIC')],True)['status'],'VARIANT_DECISION_PIVOT')

    def test_distinct_positive_assignments_are_pivot(self):
        self.assertEqual(pivot('3',[outcome('1','3','PARATACTIC'),outcome('2','3','PARATACTIC')],True)['status'],'VARIANT_DECISION_PIVOT')

    def test_speech_profiles_preserve_distinct_predicate_lexemes(self):
        d=data();d[0]['WORD'][0]['lex']='ANSWER[';d[2]['WORD'][0]['lex']='ADD['
        c,_,_=indexes(d,GRAMMAR)
        self.assertNotEqual(c.profiles['1']['predicate_morphology'],c.profiles['3']['predicate_morphology'])

    def test_blind_and_postfreeze_integration(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);source=root/'source';job=source/'blind/job';q1=root/'q1';q11=root/'q11';out=root/'out'
            for p in (job,q1,q11,out,source/'controls'):p.mkdir(parents=True,exist_ok=True)
            inventory=data();table(job/'02_clause_feature_inventory.csv',inventory)
            raw=[dict(pair_id='P1-3',candidate_clause_id='1',target_clause_id='3'),dict(pair_id='P2-4',candidate_clause_id='2',target_clause_id='4')]
            table(job/'09_candidate_evidence_matrix.csv',raw)
            table(job/'08_relation_rule_matches.csv',[dict(pair_id=r['pair_id'],matches=[dict(rule_id='W-P01',relation='PARATACTIC')]) for r in raw])
            table(job/'clause_internal_binding_candidates.csv',[],['binding_evidence'])
            table(q1/'03_q1_pair_qualification.csv',[dict(candidate_id=r['pair_id'],source_id=r['candidate_clause_id'],target_id=r['target_clause_id'],
                relation_candidate_qualification='EVIDENCE_ONLY',qualified_relations=[]) for r in raw])
            table(q1/'02_q1_source_binding_crosswalk.csv',[dict(candidate_id=r['pair_id'],source_id=r['candidate_clause_id'],target_id=r['target_clause_id'],
                raw_table_sha256=digest(job/'09_candidate_evidence_matrix.csv'),raw_row_sha256=identity(r)) for r in raw])
            metrics,cfg,refs,positive,refbindings,g=blind(source,q1,out,GRAMMAR)
            self.assertEqual(metrics['counts']['raw'],2);self.assertEqual(metrics['counts']['qualified'],2)
            self.assertEqual({r['witness']['mechanism'] for r in rows(out/'05_q12_sb11_parallel_configuration.csv')},{'SB11'})
            snapshots={p.name:digest(p) for p in out.iterdir()}
            table(q11/'02_q1_1_numbers_missing_control_audit.csv',[],['candidate_id','relation'])
            table(q11/'03_q1_1_bosman_unit_reference_audit.csv',[],['source_clause_id'])
            old=[]
            table(source/'controls/oosting_control_bindings.csv',[dict(binding_evidence=dict(raw_clause_membership=3))])
            for scope in SCOPES:
                table(q11/(scope+'_source_evidence.csv'),inventory)
                table(source/'controls'/(scope+'_fixture_source_clauses.csv'),inventory)
                table(source/'controls'/(scope+'_fixture_relation_checks.csv'),[dict(pair_id='P1-3',source_clause_id='1',target_clause_id='3',rule_ids=['W-P01'],relations=['PARATACTIC'])])
                old.append(dict(scope=scope,candidate_id='P1-3',qualified_relations=[]))
            table(q1/'16_q1_control_fixture_validation.csv',old)
            grammar=dict(**GRAMMAR,rules=[dict(rule_id='W-P01',candidate_relation='PARATACTIC')])
            receipts,ns,bs=controls(source,q1,q11,out,grammar,dict(numbers_controls=[]))
            self.assertTrue(all(r['generated_new_candidates']==0 for r in receipts.values()))
            for scope in SCOPES:
                control=next(rows(out/(scope+'_postfreeze_pair_audit.csv')))
                self.assertTrue(control['deferred'])
                self.assertEqual(control['q12']['qualification'],'UNRESOLVED')
                self.assertFalse(control['q12']['qualified_paths'])
            self.assertTrue(all(digest(out/n)==h for n,h in snapshots.items()))
            history=[dict(decision_id=str(i),researcher_decision='UNRESOLVED') for i in range(13)]
            table(source/'mfr02a_original_decisions.csv',history)
            table(q1/'14_q1_mfr02a_13_case_reaudit.csv',[dict(original_decision=r) for r in history])
            human=diagnostics(source,q1,out,cfg,refs,metrics,dict(job_diagnostics=[[1,1]]))
            self.assertEqual(len(human),13)
            self.assertEqual(reports(out,metrics,ns,bs),'READY_FOR_MFR_0_2R_H0_1')
            manifest(out);self.assertTrue(verify_manifest(out))


def add_semantic(name):
    def test(self):self.assertTrue(self.checks[name],name)
    setattr(Q12Tests,'test_semantic_'+name,test)


def add_mutation(gate,key,value):
    def test(self):
        bad=copy.deepcopy(self.evidence);parts=key.split('.');obj=bad
        for part in parts[:-1]:obj=obj[part]
        obj[parts[-1]]=value
        self.assertFalse(next(r['passed'] for r in measurements(bad) if r['gate']==gate))
    setattr(Q12Tests,'test_negative_gate_'+gate,test)


for name in ('profile_fields','N1','N2','N3','N4','N5','N6','N7','N8','N9','N10','S1','S2','S3','S4','S5','S6','SB11','generic_frames','speech_preserved','native_attachment_not_coreference'):add_semantic(name)
for gate,(key,value) in MUTATIONS:add_mutation(gate,key,value)


if __name__=='__main__':unittest.main()
