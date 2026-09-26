import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from milal_q15_synthetic import fixture,run_fixture,target_record,hidden,semantic_checks,self_test
from milal_q15_domains import Domains,compatibility,form_type
from milal_q15_references import Visibility
from milal_q15_validation import GATES,measurements,policy,assert_gates
from milal_q12_synthetic import GRAMMAR,clause
from milal_q12_profiles import ConfigurationIndex
from milal_q12_references import ReferenceIndex


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.checks,cls.v,cls.records=semantic_checks()
    def test_self_test(self):
        with tempfile.TemporaryDirectory() as tmp:self.assertTrue(self_test(Path(tmp)/'s')['passed'])
    def test_missing_identity_fails(self):
        data=fixture(2);old=ReferenceIndex(ConfigurationIndex(data,GRAMMAR['lexicons'])).witnesses
        old[-1]['candidate_antecedent_ids'].append('ANT-missing');old[-1]['candidate_count']+=1
        with self.assertRaisesRegex(ValueError,'identity'):Visibility(Domains(data,[],GRAMMAR['lexicons']),old).process(lambda r:None)
    def test_unknown_form_fails(self):
        with self.assertRaises(ValueError):form_type({'kind':'invented'},{'sp':'subs'})
    def test_np_and_pronouns_separate(self):
        for sp,kind in [('prps','INDEPENDENT_PRONOUN'),('prde','DEICTIC_PRONOUN_OR_DETERMINER')]:self.assertEqual(form_type({'kind':'PRONOUN_OR_DEICTIC'},{'sp':sp}),kind)
    def test_provisional_domain_not_visible(self):
        data=fixture(2);data[-1]['CLAUSE']['native_annotations'][0]['status']='PROVISIONAL_RELATION_UNDER_TEST'
        v,_=run_fixture(data);self.assertEqual(target_record(v)['visible_candidate_count'],0)
    def test_native_sequence_alone_not_domain(self):
        data=fixture(2);data[-1]['CLAUSE']['native_annotations'][0]['rela']='NA'
        v,_=run_fixture(data);self.assertEqual(target_record(v)['visible_candidate_count'],0)
    def test_adjacency_alone_not_domain(self):
        data=fixture(1);data[-1]['CLAUSE']['native_annotations']=[]
        v,_=run_fixture(data);self.assertEqual(target_record(v)['source_bound_candidate_count'],0)
    def test_chapter_does_not_cut_native_path(self):
        data=fixture(2);data[-1]['chapter']=99
        v,_=run_fixture(data);self.assertEqual(target_record(v)['visible_candidate_count'],1)
    def test_conflicting_gender_not_bound(self):
        data=fixture(2);data[0]['WORD'][1]['gn']='f'
        v,_=run_fixture(data);self.assertEqual(target_record(v)['source_bound_candidate_count'],0)
    def test_unknown_gender_not_bound(self):
        data=fixture(2);data[0]['WORD'][1]['gn']='unknown'
        v,_=run_fixture(data);r=target_record(v);self.assertEqual(r['reference_status'],'VISIBLE_BUT_ROLE_AMBIGUOUS');self.assertEqual(r['source_bound_candidate_count'],0)
    def test_implicit_subject_object_blocked(self):
        data=fixture(2);data[0]['PHRASE'][1]['function']='Objc'
        v,rr=run_fixture(data);self.assertEqual(target_record(v)['visible_candidate_count'],0);self.assertTrue(any(r['visibility_status']=='BLOCKED_BY_ROLE' for r in rr))
    def test_second_person_no_invented_addressee(self):
        v,_=run_fixture(fixture(2,person='p2'));self.assertEqual(target_record(v)['source_bound_candidate_count'],0)
    def test_non_speaker_cannot_bind_first_person(self):
        data=fixture(2,person='p1');data[0]['WORD'][0]['lex']='DO['
        v,_=run_fixture(data);self.assertEqual(target_record(v)['source_bound_candidate_count'],0)
    def test_no_grammar_no_relation(self):
        v,_=hidden();self.assertFalse(v.evaluate('10','12',[])['qualified_paths'])
    def test_reference_cannot_invent_parallel(self):
        v,_=hidden();self.assertFalse(v.evaluate('10','12',[dict(rule_id='W-P01',relation='PARATACTIC')])['qualified_paths'])
    def test_deferred_stays_deferred(self):
        v,_=hidden();self.assertFalse(v.evaluate('10','12',[dict(rule_id='W-A01',relation='HYPOTACTIC')],True)['qualified_paths'])
    def test_w_h_needs_active_context(self):
        v,_=hidden();self.assertFalse(v.evaluate('10','12',[dict(rule_id='W-H01',relation='HYPOTACTIC')])['qualified_paths'])
    def test_circular_binding_fails(self):
        v,_=hidden();v.by_pair['10','12'][0]['tested_relation_used_for_domain']=True
        with self.assertRaisesRegex(ValueError,'circular'):v.evaluate('10','12',[])
    def test_multiple_never_arbitrarily_qualify(self):
        v,_=run_fixture(fixture(two=True));self.assertFalse(v.evaluate('1000','2000',[dict(rule_id='W-A01',relation='HYPOTACTIC')])['qualified_paths'])
    def test_native_exact_separate_confirmation(self):
        data=fixture(2);data[-1]['CLAUSE']['native_annotations'].append(dict(head_node=10001,dependent_node=20000,rela='Rela',resolution='EXACT_NODE_MEMBERSHIP',status='DATABASE_EXISTING_RELATION',reference_semantics='EXPLICIT_ANTECEDENT'))
        v,_=run_fixture(data);self.assertEqual(target_record(v)['referential_identity_status'],'CONFIRMED_NATIVE')
    def test_native_attachment_not_coreference(self):
        self.assertEqual(target_record(self.v)['referential_identity_status'],'PROVISIONAL_UNIQUE_VISIBLE')
    def test_supplemental_same_clause_preserved(self):
        data=fixture(1);r=data[-1];w=copy.deepcopy(data[0]['WORD'][1]);w['node']=19999;r['WORD'].insert(0,w);r['word_ids'].insert(0,19999);r['PHRASE'].append(dict(node=99999,function='Subj',typ='NP',word_ids=[19999]))
        v,records=run_fixture(data);self.assertTrue(any(x['supplemental_domain_candidate'] for x in records));self.assertEqual(target_record(v)['visible_candidate_count'],2)
    def test_future_candidate_not_supplemented(self):
        v,_=run_fixture(fixture(2));self.assertFalse(any(a['word_node']>=f['word_node'] for f in v.forms for aid in v.by_reference[f['reference_witness_id']]['visible_antecedent_ids'] for a in [v.d.antecedents[aid]]))
    def test_no_collapse_mentions(self):
        self.assertEqual(len(self.v.d.antecedents),100)
    def test_domain_fields_neutral(self):
        self.assertFalse(any(set(d)&{'accepted_parent','canonical_mother','final_textual_level','final_speech_unit'} for d in self.v.d.domains.values()))
    def test_overlapping_spans_preserved(self):
        data=fixture(3);spans=[dict(span_id=str(i),start_clause=str(1000+i),clause_ids=[str(1000+i),str(1001+i)],construction_independence_status='INDEPENDENT_NATIVE_BINDING',boundary_witnesses={'synthetic':True}) for i in range(2)]
        d=Domains(data,spans,GRAMMAR['lexicons']);self.assertTrue(any(p['path_type']=='OVERLAPPING_SPAN_PATH' for p in d.paths('1000','1002')))
    def test_global_search_cannot_bind(self):
        data=fixture(100);data[-1]['CLAUSE']['native_annotations']=[]
        v,_=run_fixture(data);r=target_record(v);self.assertEqual(r['global_candidate_count'],100);self.assertEqual(r['source_bound_candidate_count'],0)
    def test_policy_rejects_control_and_scoring(self):
        self.assertFalse(policy('x="504910"')['controls']);self.assertFalse(policy('similarity_score=1')['score'])
    def test_visible_unresolved_pronoun_retains_competition(self):
        data=fixture(2,two=True);data[0]['WORD'][-1].update(sp='prps',lex='HE')
        v,_=run_fixture(data);r=target_record(v)
        self.assertEqual(r['visible_candidate_count'],2);self.assertEqual(r['source_bound_candidate_count'],0)
    def test_unique_pronominal_antecedent_not_identified(self):
        data=fixture(2);data[0]['WORD'][1].update(sp='prps',lex='HE')
        v,_=run_fixture(data);r=target_record(v)
        self.assertEqual(r['visible_candidate_count'],1);self.assertEqual(r['source_bound_candidate_count'],0)
    def test_interrogative_not_lexical_recurrence(self):
        data=fixture(1);data[-1]['WORD'][0]['sp']='prin';data[-1]['REFERENCE']['mentions'][0].update(kind='PRONOUN_OR_DEICTIC',png=None)
        v,_=run_fixture(data);r=next(r for r in v.reclassified if r['reference_form_type']=='INTERROGATIVE_PRONOUN_OR_FORM')
        self.assertEqual(r['reference_status'],'UNRESOLVED')


for _n in range(1,13):
    def _test(self,n=_n):self.assertTrue(self.checks['S'+str(n)])
    setattr(ReferenceTests,'test_S'+str(_n),_test)


def evidence():
    return dict(semantic=semantic_checks()[0],policy=policy('pass'),baseline='x',expected_baseline='x',baseline_verified=True,inputs_verified=True,
        frozen_differences=[],raw=1,expected_raw=1,grammar_errors=[],retained=1,expected_relations=1,old_outcomes_equal=True,spans_equal=True,human_equal=True,
        form_types_correct=True,lexical_positive=[],domains_valid=True,circular_domains=[],circular_bindings=[],overlap_supported=True,global_equal=True,
        candidate_sets_separate=True,png_confirmed=[],unique_confirmed=[],sb02_present=True,sb03_present=True,sb10_evidence_only=True,sb10_lexical_positive=[],
        relation_types_valid=True,q13_complete=True,canonical_coreference=[],canonical_mothers=[],canonical_hierarchies=[],blind_unchanged=True,controls_after_freeze=True,
        bosman_fixture_only=True,numbers_fixture_only=True,tests=dict(test_scope='FULL_REGRESSION',tests_run=1,failures=0,errors=0,skipped=0),fingerprint_matches=True,
        independent_equal=True,manifest_valid=True,zip_crc_valid=True)

MUTATIONS=[('baseline','bad'),('frozen_differences',['bad']),('raw',0),('retained',0),('spans_equal',False),('human_equal',False),
 ('form_types_correct',False),('lexical_positive',['bad']),('domains_valid',False),('circular_domains',['bad']),('overlap_supported',False),
 ('global_equal',False),('candidate_sets_separate',False),('policy.distance',False),('policy.nearest',False),('policy.top',False),('policy.score',False),
 ('png_confirmed',['bad']),('unique_confirmed',['bad']),('sb02_present',False),('sb03_present',False),('sb10_evidence_only',False),('semantic.S12',False),
 ('sb10_lexical_positive',['bad']),('relation_types_valid',False),('q13_complete',False),('canonical_coreference',['bad']),('canonical_mothers',['bad']),
 ('canonical_hierarchies',['bad']),('blind_unchanged',False),('policy.controls',False),('bosman_fixture_only',False),('numbers_fixture_only',False),
 ('tests.failures',1),('tests.skipped',1),('independent_equal',False),('manifest_valid',False),('zip_crc_valid',False)]
assert len(MUTATIONS)==len(GATES)


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.e=evidence()
    def test_positive(self):self.assertTrue(all(measurements(self.e).values()))
    def test_no_pending_regression_release(self):
        e=copy.deepcopy(self.e);e['tests']['test_scope']='NOT_RUN'
        with self.assertRaises(ValueError):assert_gates(e)


for _gate,(_field,_value) in zip(GATES,MUTATIONS):
    def _test(self,gate=_gate,field=_field,value=_value):
        e=copy.deepcopy(self.e);obj=e;parts=field.split('.')
        for part in parts[:-1]:obj=obj[part]
        obj[parts[-1]]=value;self.assertFalse(measurements(e)[gate])
    setattr(GateTests,'test_negative_'+_gate,_test)


if __name__=='__main__':unittest.main()
