import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q13_model import AssignmentModel,dimension,MOTHER,PARALLEL,OVERLAY
from milal_q13_validation import edge,semantic_checks,core_policy,measurements,GATES
from milal_q13_pipeline import blind,postfreeze,verify_qualification,sb12_constraints,write
from milal_q13_synthetic import fixture,self_test
from milal_q13_runner import audit,ROOT
from milal_mfr02r_data import rows,manifest,verify_manifest
from milal_mfr02r_pipeline import code_fingerprint


class ModelTests(unittest.TestCase):
    def test_dimensions(self):
        self.assertEqual([dimension(edge('a','s',relation=r)) for r in ('HYPOTACTIC','PARATACTIC')],[MOTHER,PARALLEL])
        self.assertEqual(dimension(edge('o','s',relation='TYPED_OVERLAY',non_hierarchical=True)),OVERLAY)
        with self.assertRaises(ValueError):dimension(edge('o','s',relation='UNKNOWN'))

    def test_input_schema(self):
        o=edge('a','s')
        for bad in [dict(o,target=1),{k:v for k,v in o.items() if k!='provenance_paths'},dict(o,relation_type='UNKNOWN')]:
            with self.assertRaises(ValueError):AssignmentModel([bad])
        with self.assertRaises(ValueError):AssignmentModel([o,o])

    def test_mother_conflict_is_not_deduplicated(self):
        m=AssignmentModel([edge('a','m1'),edge('b','m2')])
        self.assertTrue(m.errors(['a','b']))
        self.assertEqual(len(m.analyze()['dimensions']),2)
        with self.assertRaises(ValueError):m.assignment('t',['a','b'])

    def test_unqualified_selection_rejected(self):
        with self.assertRaises(ValueError):AssignmentModel([edge('a','s')]).assignment('t',['missing'])

    def test_reverse_same_pair(self):
        m=AssignmentModel([edge('a','s'),edge('b','t',target='s',relation='PARATACTIC')])
        self.assertTrue(m.errors(['a','b']))
        self.assertEqual(len(m.analyze()['same_pair_conflicts']),1)

    def test_cycle_after_parallel_contraction(self):
        m=AssignmentModel([edge('a','x',target='y'),edge('b','y',target='z'),edge('c','x',target='z',relation='PARATACTIC')])
        self.assertTrue(m.errors(['a','b','c']))
        self.assertFalse(m.errors(['b','c']))

    def test_search_finds_relevant_core_among_distractors(self):
        rs=[edge('a','p1',relation='PARATACTIC'),edge('b','p2',relation='PARATACTIC'),edge('c','s',target='x'),edge('d','u',target='v'),edge('e','u2',target='v')]
        constraint=dict(kind='FORBIDDEN_COMBINATION',constraint_id='g',outcome_ids=['a','b','c'],independent=True,constraint_provenance='verified test')
        m=AssignmentModel(rs,constraints=[constraint]);p=m.incompatible_witness('a','b')
        self.assertEqual(p['incompatible_union'],['a','b','c'])
        self.assertFalse(m.errors(p['assignment_a']['selected_outcome_ids']))
        self.assertFalse(m.errors(p['assignment_b']['selected_outcome_ids']))

    def test_global_difference_is_not_target_pivot(self):
        m=AssignmentModel([edge('a','m'),edge('b','x',target='other'),edge('c','y',target='other')])
        a=m.assignment('t',['a','b']);b=m.assignment('t',['a','c'])
        self.assertNotEqual(a,b);self.assertEqual(a['mother_assignment'],b['mother_assignment'])
        self.assertFalse(next(r for r in m.analyze()['pivots'] if r['target_id']=='t')['human_review_required'])

    def test_explicit_exclusion_requires_provenance(self):
        with self.assertRaises(ValueError):AssignmentModel([edge('a','s'),edge('e','s',relation='EXCLUDED',excluded_outcome_id='a')])

    def test_soft_sb12_not_hard(self):
        os=[edge('a','s'),edge('b','p',relation='PARATACTIC')]
        sb=dict(input_outcome_ids=['a','b'],output_outcome_ids=['a','b'],positive_binding=False,
            conflicts=[dict(edge_ids=['a','b'],severity='SOFT_CONFLICT',kind='COMPETING_PARALLEL_CHAIN')])
        self.assertEqual(sb12_constraints(sb,os),[])
        sb['positive_binding']=True
        with self.assertRaises(ValueError):sb12_constraints(sb,os)

    def test_hard_sb12_unknown_fails(self):
        os=[edge('a','s'),edge('b','p',relation='PARATACTIC')]
        sb=dict(input_outcome_ids=['a','b'],output_outcome_ids=['a','b'],positive_binding=False,
            conflicts=[dict(edge_ids=['a','b'],severity='HARD_CONFLICT',kind='UNKNOWN')])
        with self.assertRaises(ValueError):sb12_constraints(sb,os)

    def test_hard_sb12_preserves_all_mother_alternatives(self):
        os=[edge('a','s'),edge('b','s2'),edge('c','s3')]
        sb=dict(input_outcome_ids=['a','b','c'],output_outcome_ids=['a','b','c'],positive_binding=False,
            conflicts=[dict(conflict_id='g',edge_ids=['a','b','c'],severity='HARD_CONFLICT',kind='AT_MOST_ONE_MOTHER')])
        constraints=sb12_constraints(sb,os);self.assertEqual(len(constraints),3)
        model=AssignmentModel(os,constraints=constraints)
        self.assertEqual(len(model.analyze()['dimensions']),3)
        self.assertTrue(all(not model.errors([i]) for i in ('a','b','c')))

    def test_constraint_schema_cannot_create_new_edge(self):
        with self.assertRaises(ValueError):AssignmentModel([edge('a','s')],constraints=[dict(
            kind='FORBIDDEN_COMBINATION',constraint_id='g',outcome_ids=['a','new'],independent=True,constraint_provenance='test')])

    def test_parallel_does_not_infer_shared_mother(self):
        m=AssignmentModel([edge('m','mother'),edge('p','peer',relation='PARATACTIC')],targets=['t','peer'])
        a=m.assignment('peer',['m','p'])
        self.assertIsNone(a['mother_assignment'])
        self.assertTrue(all(not r['shared_mother_assigned'] for r in m.analyze()['peer_sets']))

    def test_overlay_cannot_create_cycle_or_consume_slot(self):
        m=AssignmentModel([edge('m','s'),edge('o','t',target='s',relation='EXTENSION',non_hierarchical=True)])
        self.assertFalse(m.errors(['m','o']))
        self.assertIsNone(m.assignment('s',['m','o'])['mother_assignment'])

    def test_all_targets_including_zero_relation_preserved(self):
        r=AssignmentModel([edge('a','s')],targets=['t','zero']).analyze()
        self.assertEqual({a['target_id'] for a in r['assignments']},{'t','zero'})
        self.assertEqual(next(a for a in r['assignments'] if a['target_id']=='zero')['coherent_combined_assignment']['selected_outcome_ids'],[])

    def test_no_accepted_assignment(self):
        r=AssignmentModel([edge('a','s')]).analyze()
        self.assertTrue(all(a['canonical_mother']==a['canonical_hierarchy']==a['human_accepted']=='' for a in r['assignments']))
        self.assertFalse(r['assignments'][0]['coherent_combined_assignment']['accepted'])

    def test_output_tampering_detected_by_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input';fixture(p);self.assertTrue(verify_manifest(p))
            (p/'preserved_human_judgments.csv').write_text('changed',encoding='utf8')
            self.assertFalse(verify_manifest(p))

    def test_previous_pivot_identity_mismatch_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input';out=Path(tmp)/'out';out.mkdir();c=fixture(p);m,r,n=blind(p,out)
            c['previous_pivot_targets']=['missing']
            with self.assertRaises(ValueError):postfreeze(p,out,m,r,n,c)

    def test_unresolved_status_is_explicit(self):
        r=AssignmentModel([edge('a','s'),edge('p','peer',relation='PARATACTIC')]).analyze()
        self.assertEqual(r['matrix'][0]['level_compatibility_classification'],'UNRESOLVED_COMPATIBILITY')
        self.assertFalse(r['pivots'][0]['human_review_required'])

    def test_qualification_provenance_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'input';fixture(p);q=list(rows(p/'10_q12_qualified_relation_universe.csv'));o=list(rows(p/'11_q12_structural_outcome_groups.csv'))
            verify_qualification(q,o);o[0]['provenance_paths'][0]['witness_id']='changed'
            with self.assertRaises(ValueError):verify_qualification(q,o)

    def test_policy_mutations(self):
        self.assertFalse(core_policy('from itertools import product\nproduct([1],[2])')['no_cartesian'])
        self.assertFalse(core_policy('from milal_q12_binding import qualify')['no_source_binding'])
        self.assertFalse(core_policy('target = "497625"')['no_control_ids'])

    def test_end_to_end_synthetic(self):
        with tempfile.TemporaryDirectory() as tmp:
            r=self_test(Path(tmp)/'run');self.assertTrue(r['passed'])


for _name in semantic_checks():
    def _test(self,name=_name):self.assertTrue(semantic_checks()[name],name)
    setattr(ModelTests,'test_semantic_'+_name,_test)


class GateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();root=Path(cls.temp.name);source=root/'input';out=root/'out';out.mkdir()
        config=fixture(source);config['baseline']='synthetic-baseline'
        model,result,counts=blind(source,out);reaudit,diag,preserved=postfreeze(source,out,model,result,counts,config);manifest(out)
        tests=dict(test_scope='FULL_REGRESSION',tests_run=1,failures=0,errors=0,skipped=0,code_fingerprint=code_fingerprint())
        # This receipt is an in-memory gate fixture, never authorization for a real run.
        cls.e=audit(source,out,model,result,counts,reaudit,preserved,config,
            dict(baseline=config['baseline'],differences=[]),dict(crc_valid=True,manifest_valid=True),tests,dict(checks=semantic_checks()))
        cls.e['independent_equal']=True
        cls.context=(source,out,model,result,counts,reaudit,preserved,config,tests)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_positive_computed_fixture(self):self.assertTrue(all(measurements(self.e).values()))

    def test_real_diagnostic_output_tamper_fails_gates(self):
        source,out,model,result,counts,reaudit,preserved,config,tests=self.context
        p=out/'postfreeze_diagnostics.json';original=p.read_bytes();ds=json.loads(original)
        try:
            for d in ds:d['representable']=False
            write(p,ds)
            e=audit(source,out,model,result,counts,reaudit,preserved,config,dict(baseline=config['baseline'],differences=[]),
                dict(crc_valid=True,manifest_valid=True),tests,dict(checks=semantic_checks()))
            self.assertFalse(measurements(e)['MOTHER_AND_PARALLEL_CAN_COEXIST'])
            self.assertFalse(measurements(e)['MULTIPLE_PARALLEL_PEERS_ALLOWED'])
        finally:p.write_bytes(original)


MUTATIONS={
 'BASELINE_COMMIT_VERIFIED':('baseline','wrong'), 'Q1_2_FROZEN':('frozen_differences',['changed']),
 'Q1_2_QUALIFIED_RELATIONS_UNCHANGED':('qualified_equal',False), 'RELATION_DIMENSIONS_SEPARATED':('dimension_errors',['bad']),
 'ONE_MOTHER_CONSTRAINT_PRESERVED':('incoherent_assignments',['two mothers']), 'MULTIPLE_PARALLEL_PEERS_ALLOWED':('semantic.S2',False),
 'MOTHER_AND_PARALLEL_CAN_COEXIST':('semantic.S1',False), 'PARALLEL_MULTIPLICITY_NOT_AUTOMATIC_COMPETITION':('multiplicity_only_pivots',['t']),
 'UNSELECTED_EQUALS_UNDECIDED':('unselected_errors',['NO_RELATION']), 'SAME_PAIR_RELATION_CONFLICT_IMPLEMENTED':('semantic.S4',False),
 'COHERENT_MULTI_RELATION_ASSIGNMENT_IMPLEMENTED':('assignment_errors',['bad']), 'NO_CARTESIAN_VARIANT_EXPLOSION':('policy.no_cartesian',False),
 'SB12_CONSTRAINT_ONLY':('new_positive_ids',['new']), 'NO_NEW_HUMAN_JUDGMENT':('human_equal',False),
 'NO_CANONICAL_MOTHER':('canonical_mothers',['chosen']), 'NO_CANONICAL_HIERARCHY':('canonical_hierarchies',['chosen']),
 'Q12_SEVEN_PIVOTS_REAUDITED':('reaudit_targets',[]), 'REFERENCE_LAYER_UNCHANGED':('reference_equal',False),
 'UNIT_BOUNDARY_ADAPTER_NOT_YET_CHANGED':('unit_boundary_equal',False), 'FULL_REGRESSION_PASS':('tests.failures',1),
 'SKIP_ZERO':('tests.skipped',1), 'DETERMINISTIC_RERUN':('independent_equal',False), 'MANIFEST_VALID':('manifest_valid',False),
 'PIVOTS_REQUIRE_INCOMPATIBLE_POSITIVE_ASSIGNMENTS':('invalid_pivot_proofs',['bad']), 'SOURCE_BINDING_NOT_RERUN':('policy.no_source_binding',False)}
assert set(MUTATIONS)==set(GATES)
for _gate,(_field,_value) in MUTATIONS.items():
    def _negative(self,gate=_gate,field=_field,value=_value):
        e=copy.deepcopy(self.e);parts=field.split('.');obj=e
        for part in parts[:-1]:obj=obj[part]
        obj[parts[-1]]=value
        self.assertFalse(measurements(e)[gate])
    setattr(GateTests,'test_negative_'+_gate,_negative)


if __name__=='__main__':unittest.main()
