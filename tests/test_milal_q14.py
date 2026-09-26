import ast
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q14_synthetic import construction,index,full_span,semantic_checks,self_test
from milal_q14_binding import compare,CompositeBinding
from milal_q14_validation import policy,measurements,GATES
from milal_q12_synthetic import clause
from milal_q14_spans import INDEPENDENT
from milal_mfr02r_data import verify_manifest,table
from milal_q14_controls import fixture_inventory


class ConstructionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.checks,cls.i,cls.c,cls.cross,cls.formula=semantic_checks()

    def test_synthetic_end_to_end(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'run';r=self_test(p);self.assertTrue(r['passed']);self.assertTrue(verify_manifest(p/'a'))

    def test_exact_native_identity_required(self):
        data=construction(1,100,0);data[1]['CLAUSE']['native_annotations'][0]['resolution']='FUZZY'
        i=index(data);self.assertFalse(i.composites)
        self.assertTrue(any(s['construction_independence_status']=='UNRESOLVED' for s in i.spans.values()))

    def test_no_word_gap_as_local_span(self):
        data=construction(1,100,0);data[1]['word_ids']=[900,901]
        for w,n in zip(data[1]['WORD'],[900,901]):w['node']=n
        data[1]['PHRASE'][0]['word_ids']=[900];data[1]['PHRASE'][1]['word_ids']=[901]
        self.assertFalse(index(data).spans)

    def test_native_na_alone_does_not_bind_finite_content(self):
        data=construction(1,100,0);data[1]['clause_type']='WayX';data[1]['WORD'][0]['vt']='impf'
        self.assertFalse(index(data).spans)

    def test_contiguous_native_infinitive_is_allowed_without_named_subordinator(self):
        i=index(construction(1,100,0));self.assertTrue(any(s['clause_ids']==['1','2'] for s in i.spans.values()))

    def test_no_fixed_three_clause_limit(self):
        data=[]
        for n in range(9):
            r=clause(n+1,100+n, n,subject=None,head=n if n else None,typ='InfC' if n else 'WayX')
            if n:
                r['WORD'][0]['vt']='infc';r['CLAUSE']['native_annotations'][0].update(status='DATABASE_EXISTING_RELATION',rela='NA')
            data.append(r)
        i=index(data);self.assertTrue(any(len(s['clause_ids'])==9 for s in i.spans.values()))

    def test_cross_family_different_component_count(self):
        data=construction(1,100,0)+construction(11,200,3)
        tail=data.pop();data.pop();tail['word_ids']=[202];tail['WORD'][0]['node']=202;tail['PHRASE'][0]['word_ids']=[202]
        tail['CLAUSE']['native_annotations'][0]['rela']='Objc';data.append(tail)
        i=index(data);a=full_span(i,1);b=next(s['span_id'] for s in i.spans.values() if s['start_clause']=='11')
        c=compare(i,a,b);self.assertTrue(c['mapping_resolved']);self.assertNotEqual(c['family_A'],c['family_B'])
        self.assertEqual([(m['source_position'],m['target_position']) for m in c['position_mapping']],[(0,0),(2,1)])

    def test_overlap_cannot_prove_binding_to_itself(self):
        i=index(construction(1,100,0));spans=list(i.spans)
        self.assertEqual(compare(i,*spans)['status'],'BLOCKED_NONINDEPENDENT_SPAN')

    def test_native_head_not_nearest_guess(self):
        data=construction(1,100,0);data[-1]['CLAUSE']['native_annotations'][0]['head_node']=77777
        i=index(data);self.assertFalse(any(len(s['clause_ids'])==3 for s in i.spans.values()))

    def test_hierarchy_fields_cannot_change_membership_or_families(self):
        data=construction(1,100,0);base=index(data)
        for r in data:r.update(accepted_mother=999,historical_HSA_parentage='changed',Q13_assignment='changed')
        mutated=index(data)
        self.assertEqual([s['clause_ids'] for s in base.spans.values()],[s['clause_ids'] for s in mutated.spans.values()])
        self.assertEqual(set(base.families),set(mutated.families))

    def test_membership_has_no_final_structural_columns(self):
        self.assertTrue(all(not {'accepted_mother','accepted_parent','final_textual_unit','final_hierarchy_level'}&set(r) for r in self.i.membership_rows()))

    def test_unlicensed_hypotaxis_not_invented(self):
        r=CompositeBinding(self.i).evaluate('1','11',[dict(rule_id='W-A01',relation='HYPOTACTIC')])
        self.assertFalse(r['qualified_relations']);self.assertEqual(r['status'],'COMPOSITE_SUPPORT_ONLY')

    def test_deferred_clause_binding_preserved(self):
        r=CompositeBinding(self.i).evaluate('1','11',[dict(rule_id='W-P01',relation='PARATACTIC')],deferred=True)
        self.assertFalse(r['qualified_paths']);self.assertEqual(r['status'],'UNRESOLVED')

    def test_qualification_anchor_identifies_existing_pair_component(self):
        r=CompositeBinding(self.i).evaluate('2','12',[dict(rule_id='W-P01',relation='PARATACTIC')])
        self.assertTrue(r['qualified_paths'])
        self.assertTrue(all(w['source_anchor']['anchor_clause_id']=='2' and w['target_anchor']['anchor_clause_id']=='12' for w in r['witnesses']))

    def test_families_derived_from_form(self):
        from milal_q1_binding import identity
        self.assertTrue(all(k=='CCF-'+identity(f['ordered_structural_template']) for k,f in self.i.families.items()))

    def test_frame_presence_without_matching_anchor_insufficient(self):
        from milal_q12_binding import frame_witness
        data=construction(1,100,0)+construction(11,200,3);i=index(data)
        self.assertEqual(frame_witness(i.profiles['1'],i.profiles['11'],'TEMPORAL'),[])

    def test_proper_name_object_alone_is_not_non_generic_anchor(self):
        from milal_q14_binding import non_generic_nominals
        i=index(construction(1,100,0)+construction(11,200,3))
        # OBJECT/ in this fixture is tagged nmpr: its spelling cannot override POS.
        self.assertEqual(non_generic_nominals(i,i.profiles['2']),set())
        self.assertTrue(self.checks['S3'])

    def test_unmatched_frame_does_not_let_same_name_bind(self):
        data=[clause(1,100,0,time='DAY/'),clause(2,103,1,subject=None,head=1),
            clause(11,200,2),clause(12,202,3,subject=None,head=11)]
        for r in data:
            for p in r['PHRASE']:
                if p['function']=='Subj':p['function']='Objc'
            for e in r['CLAUSE']['native_annotations']:e.update(status='DATABASE_EXISTING_RELATION',rela='NA')
        i=index(data);r=CompositeBinding(i).evaluate('1','11',[dict(rule_id='W-P01',relation='PARATACTIC')])
        self.assertFalse(r['qualified_paths']);self.assertFalse(r['witnesses'])

    def test_native_adjunct_is_first_class_without_invented_locative_type(self):
        data=[clause(1,100,0,time='FRAME/'),clause(2,103,1,subject=None,head=1),
            clause(11,200,2,time='FRAME/'),clause(12,203,3,subject=None,head=11)]
        for r in data:
            for p in r['PHRASE']:
                if p['function']=='Time':p['function']='Adju'
            for e in r['CLAUSE']['native_annotations']:e.update(status='DATABASE_EXISTING_RELATION',rela='NA')
        i=index(data);r=CompositeBinding(i).evaluate('1','11',[dict(rule_id='W-P01',relation='PARATACTIC')])
        self.assertTrue(r['qualified_paths'])
        self.assertTrue(all(not any(c['location_frame']) and any(c['adjunct_frame']) for c in i.composites.values()))
        self.assertTrue(any(a['grammatical_role']=='Adju' for w in r['witnesses'] for a in w['evidence']['lexical_role_mapping']))
        data[2]['WORD'][-1]['lex']='OTHER_FRAME/'
        self.assertFalse(CompositeBinding(index(data)).evaluate('1','11',[dict(rule_id='W-P01',relation='PARATACTIC')])['qualified_paths'])

    def test_no_fixed_control_in_core(self):
        root=Path(__file__).resolve().parents[1]
        text='\n'.join((root/'src'/f).read_text() for f in ('milal_q14_spans.py','milal_q14_binding.py'))
        self.assertTrue(all(policy(text).values()))
        self.assertFalse(policy('target="499251"')['no_controls'])
        self.assertFalse(policy('from milal_q13_model import AssignmentModel')['no_hierarchy'])
        self.assertFalse(policy('similarity_score=0.9')['no_score'])
        self.assertFalse(policy('max_span=3')['no_span_limit'])

    def test_fixture_location_requires_exact_node_join(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);q=p/'q11';q.mkdir();s=p/'source';(s/'controls').mkdir(parents=True)
            data=construction(1,100,0)
            table(q/'toy_source_evidence.csv',[{k:v for k,v in r.items() if k not in ('book','chapter','verse','surface_hebrew')} for r in data])
            loc=[{k:r[k] for k in ('clause_id','clause_atom_ids','word_ids','book','chapter','verse','surface_hebrew')} for r in data]
            table(s/'controls/toy_fixture_source_clauses.csv',loc)
            joined=fixture_inventory(s,q,'toy');self.assertEqual(joined[0]['book'],'Iob')
            loc[0]['word_ids']=[999];table(s/'controls/toy_fixture_source_clauses.csv',loc)
            with self.assertRaisesRegex(ValueError,'word/atom'):fixture_inventory(s,q,'toy')


for _name in ('S'+str(n) for n in range(1,13)):
    def _test(self,name=_name):self.assertTrue(self.checks[name],name)
    setattr(ConstructionTests,'test_'+_name,_test)


def gate_fixture():
    checks=semantic_checks()[0]
    return dict(semantic=checks,policy=policy('pass'),baseline='base',expected_baseline='base',baseline_verified=True,
        inputs_verified=True,frozen_differences=[],raw_count=1,expected_raw=1,raw_errors=[],retained=1,expected_baseline_relations=1,
        baseline_outcomes_unchanged=True,human_equal=True,canonical_mothers=[],canonical_hierarchies=[],invalid_spans=[],dependent_positive=[],
        traversal_has_no_fixed_upper_bound=True,profile_coverage=True,family_derived=True,families_merged=[],unresolved_positive_mapping=[],
        unanchored_positive=[],bare_formula_positive=0,reference_unchanged=True,invented_relation_types=[],grammar_errors=[],q13_complete=True,
        membership_observational=True,blind_unchanged=True,events=['BLIND_FROZEN','POSTFREEZE_CONTROLS_COMPLETED'],external_fixture_only=True,
        new_human_judgments=[],tests=dict(test_scope='FULL_REGRESSION',tests_run=1,errors=0,failures=0,skipped=0),fingerprint_matches=True,
        independent_equal=True,manifest_valid=True,zip_crc_valid=True)


MUTATIONS=[('baseline','wrong'),('frozen_differences',['changed']),('raw_count',0),('retained',0),('human_equal',False),
    ('canonical_mothers',['accepted']),('canonical_hierarchies',['accepted']),('invalid_spans',['gap']),('dependent_positive',['circular']),
    ('semantic.S11',False),('traversal_has_no_fixed_upper_bound',False),('profile_coverage',False),('family_derived',False),
    ('semantic.S5',False),('families_merged',['merged']),('unresolved_positive_mapping',['ambiguous']),('unanchored_positive',['bare']),
    ('bare_formula_positive',1),('reference_unchanged',False),('invented_relation_types',['invented']),('grammar_errors',['unlicensed']),
    ('q13_complete',False),('membership_observational',False),('policy.no_hierarchy',False),('blind_unchanged',False),
    ('policy.no_controls',False),('external_fixture_only',False),('policy.no_score',False),('new_human_judgments',['new']),
    ('tests.failures',1),('tests.skipped',1),('independent_equal',False),('manifest_valid',False),('zip_crc_valid',False)]
assert len(MUTATIONS)==len(GATES)


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.e=gate_fixture()
    def test_positive_fixture(self):self.assertTrue(all(measurements(self.e).values()))


for _gate,(_field,_value) in zip(GATES,MUTATIONS):
    def _test(self,gate=_gate,field=_field,value=_value):
        e=copy.deepcopy(self.e);parts=field.split('.');obj=e
        for part in parts[:-1]:obj=obj[part]
        obj[parts[-1]]=value;self.assertFalse(measurements(e)[gate])
    setattr(GateTests,'test_negative_'+_gate,_test)


if __name__=='__main__':unittest.main()
