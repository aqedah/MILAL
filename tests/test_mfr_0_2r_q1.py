"""Q1 specification controls, actual source adapters and negative gate coverage."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import shutil
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_q1_binding import qualify, witness, outcome, pivot, SourceIndex, identity, rule_roles
from milal_q1_synthetic import semantic_checks, native_witness, configuration, match, self_test
from milal_q1_validation import evaluate, GATES
from milal_q1_validation import audit
from milal_q1_pipeline import run_blind, write_json, ROOT
from milal_q1_synthetic import source_fixture
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_data import rows, table, manifest


def clause(cid,pos,lex='DBR[',typ='WayX',head=None,rela='Objc',subject=True):
    node=cid*10
    words=[dict(node=node,lex=lex,sp='verb',vt='impf',vs='qal')]
    phrases=[dict(node=cid*100,word_ids=[node],function='Pred',typ='VP')]
    if subject:
        words.append(dict(node=node+1,lex='NAME/',sp='nmpr',vt='NA',vs='NA'))
        phrases.append(dict(node=cid*100+1,word_ids=[node+1],function='Subj',typ='NP'))
    edges=[] if head is None else [dict(dependent_node=cid,head_node=head,rela=rela,resolution='EXACT_NODE_MEMBERSHIP',resolved_head_clause_ids=[head])]
    return dict(clause_id=cid,position=pos,clause_atom_ids=[cid+10000],word_ids=[w['node'] for w in words],
        clause_type=typ,WORD=words,PHRASE=phrases,CLAUSE=dict(native_annotations=edges),
        PARTICIPANT=dict(mentions=[]))


class Q1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();base=Path(cls.temp.name)
        cls.source=source_fixture(base/'source')
        cls.grammar=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
        table(cls.source/'blind/job/clause_internal_binding_candidates.csv',
              [dict(binding_id='SYNTHETIC-DEFER',binding_evidence=dict(raw_clause_membership=5))])
        cls.template=base/'template';run_blind(cls.source,cls.template,cls.grammar)
        history=list(rows(cls.source/'mfr02a_original_decisions.csv'))
        table(cls.template/'14_q1_mfr02a_13_case_reaudit.csv',
              [dict(original_decision=d,original_decision_sha256=identity(d),new_human_judgment='') for d in history])
        scopes=('pentateuch','qohelet','lamentations','isaiah')
        table(cls.template/'16_q1_control_fixture_validation.csv',
              [dict(scope=s,exact_fixture_identity=True,full_external_book_analysis=False) for s in scopes])
        write_json(cls.template/'control_source_receipts.json',
                   {s:dict(original_clause_ids=[1,2],selected_clause_ids=['1','2'],full_external_book_analysis=False) for s in scopes})
        manifest(cls.template)
        cls.receipts=dict(mode='SYNTHETIC',baseline=dict(baseline='SYNTHETIC',differences=[]),expected_baseline='SYNTHETIC',
            source=dict(manifest_valid=True,crc_valid=True),h0=dict(manifest_valid=True,crc_valid=True),
            tests=dict(test_scope='FULL_REGRESSION',tests_run=2465,failures=0,errors=0,skipped=0),
            fingerprint_matches=True,independent_bytes_equal=True)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_actual_audit_positive_fixture(self):
        gates=evaluate(audit(self.source,self.template,self.grammar,self.receipts,semantic_checks()))
        self.assertEqual([r['gate'] for r in gates if not r['passed']],[])

    def test_all_fifteen_specification_controls(self):
        checks=semantic_checks()
        self.assertEqual(set(checks['cases']),{'S'+str(i) for i in range(1,16)})
        self.assertTrue(all(checks['cases'].values()))

    def test_native_endpoints_are_recomputed(self):
        a=clause(1,0);b=clause(2,1,head=1)
        self.assertTrue(SourceIndex([a,b],['Objc'],[]).bindings('1','2'))
        b['CLAUSE']['native_annotations'][0]['head_node']=999
        # A stale cached resolved_head_clause_ids list must not bind.
        self.assertFalse(SourceIndex([a,b],['Objc'],[]).bindings('1','2'))

    def test_na_annotation_not_direct_dependency(self):
        index=SourceIndex([clause(1,0),clause(2,1,head=1,rela='NA')],['Objc'],[])
        self.assertFalse(index.bindings('1','2'))

    def test_adjacency_alone_never_governing_eligibility(self):
        index=SourceIndex([clause(1,0),clause(2,1,typ='InfC')],['Objc'],[])
        self.assertFalse(index.bindings('1','2'))

    def test_remote_dependency_is_retained(self):
        data=[clause(1,0)]+[clause(i,i-1) for i in range(2,101)]+[clause(101,100,head=1)]
        ws=SourceIndex(data,['Objc'],[]).bindings('1','101')
        self.assertEqual(ws[0]['intervening_context_status'],'REFERENCE_CROSSES_INTERVENING_MATERIAL')

    def test_configuration_has_actual_links_and_nodes(self):
        data=[clause(1,0),clause(2,1,typ='InfC',head=1,subject=False),clause(3,2,head=1,subject=False),
              clause(4,3),clause(5,4,typ='InfC',head=4,subject=False),clause(6,5,head=4,subject=False)]
        index=SourceIndex(data,['Objc'],[])
        ws=index.bindings('1','4')
        self.assertEqual([w['mechanism'] for w in ws],['SB06'])
        data[4]['CLAUSE']['native_annotations']=[]
        self.assertFalse(SourceIndex(data,['Objc'],[]).bindings('1','4'))

    def test_bare_answer_amr_formula_is_not_configuration(self):
        data=[clause(1,0,'<NH['),clause(2,1,'>MR[',head=1,subject=False),
              clause(3,2,'<NH['),clause(4,3,'>MR[',head=3,subject=False)]
        self.assertFalse(SourceIndex(data,['Objc'],['<NH[','>MR[']).bindings('1','3'))

    def test_domain_and_participant_similarity_are_not_binding(self):
        a,b=clause(1,0),clause(2,1)
        a['DOMAIN']=b['DOMAIN']={'raw':'Q'}
        self.assertFalse(SourceIndex([a,b],['Objc'],[]).bindings('1','2'))

    def test_walton_rule_cannot_borrow_wrong_binding_mode(self):
        self.assertFalse(qualify('1','2',[match()],[configuration()])['qualified_paths'])
        self.assertFalse(qualify('1','2',[match('W-H01')],[native_witness()])['qualified_paths'])
        w=configuration();del w['independent_correspondence_and_same_line']
        self.assertFalse(qualify('1','2',[match('W-P01','PARATACTIC')],[w])['qualified_paths'])

    def test_unknown_mechanism_rejected(self):
        w=native_witness();w['mechanism']='CORPUS_ANALOGUE_ONLY'
        with self.assertRaises(ValueError):qualify('1','2',[match()],[w])

    def test_mismatched_source_rejected(self):
        with self.assertRaises(ValueError):qualify('99','2',[match()],[native_witness()])

    def test_deferred_binding_cannot_qualify(self):
        r=qualify('1','2',[match()],[native_witness()],deferred=True)
        self.assertEqual(r['qualification'],'UNRESOLVED');self.assertEqual(r['qualified_paths'],[])

    def test_context_block_is_distinct(self):
        r=qualify('1','2',[match()],[native_witness()],blocked=True)
        self.assertEqual(r['qualification'],'BLOCKED_BY_CONTEXT')

    def test_unselected_not_no_relation(self):
        self.assertFalse(pivot('2',[],True)['review_required'])
        self.assertFalse(pivot('2',[outcome('1','2','HYPOTACTIC')],True)['review_required'])

    def test_same_target_assignment_despite_global_difference(self):
        o=outcome('1','2','HYPOTACTIC')
        self.assertEqual(pivot('2',[o,dict(o)],True)['status'],'VARIANT_MEMBER_NON_PIVOT')
        self.assertEqual(pivot('2',[o,outcome('9','10','PARATACTIC')],True)['status'],'VARIANT_MEMBER_NON_PIVOT')

    def test_unit_mediation_requires_actual_word_reference_and_path(self):
        data=[clause(1,0),clause(2,1,head=1),clause(3,2,head=20)]
        ws=SourceIndex(data,['Objc'],[]).bindings('1','3')
        self.assertEqual(ws[0]['mechanism'],'SB03')
        self.assertEqual(ws[0]['evidence']['native_dependency_paths'],[['1','2']])
        data[1]['CLAUSE']['native_annotations']=[]
        self.assertFalse(SourceIndex(data,['Objc'],[]).bindings('1','3'))

    def test_configuration_does_not_require_proper_name_or_nonfinite(self):
        data=[clause(1,0),clause(2,1,head=1,subject=False),clause(3,2),clause(4,3,head=3,subject=False)]
        for row in data:
            for w in row['WORD']:
                if w['sp']=='nmpr':w['sp']='subs'
        self.assertEqual(SourceIndex(data,['Objc'],[]).bindings('1','3')[0]['mechanism'],'SB06')

    def test_different_relation_and_peer_are_pivots(self):
        for os in ([outcome('1','3','PARATACTIC'),outcome('2','3','PARATACTIC')],
                   [outcome('1','3','HYPOTACTIC'),outcome('1','3','PARATACTIC')]):
            self.assertTrue(pivot('3',os,True)['review_required'])

    def test_bad_relation_fails_variant(self):
        with self.assertRaises(ValueError):pivot('2',[outcome('1','2','POETIC_TYPED_RELATION')],True)

    def test_rule_role_audit_does_not_mutate_registry(self):
        r=dict(rule_id='W-A01',required_features=[['explicit_subordinator','adjacent']],supporting_features=['TIME'])
        old=copy.deepcopy(r);a=rule_roles(r)
        self.assertEqual(a['required_feature_roles']['explicit_subordinator'],'TARGET_FEATURE')
        self.assertEqual(r,old)

    def test_incomplete_gate_measurements_fail(self):
        with self.assertRaises(ValueError):evaluate({})

    def test_synthetic_stream_and_determinism(self):
        with tempfile.TemporaryDirectory() as d:
            result=self_test(Path(d)/'q1')
            self.assertTrue(result['bytes_equal'])
            self.assertEqual(result['metrics']['counts']['raw'],21)


def gate_negative(gate):
    def test(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'out';shutil.copytree(self.template,out)
            receipts=copy.deepcopy(self.receipts);semantics=semantic_checks()
            def mutate(name,fn):
                rr=list(rows(out/name));fn(rr);table(out/name,rr)
            if gate=='BASELINE_COMMIT_VERIFIED':receipts['baseline']['baseline']='WRONG_BASELINE'
            elif gate=='MFR_0_2R_FROZEN':receipts['source']['manifest_valid']=False
            elif gate=='MFR_0_2R_H0_FROZEN':receipts['h0']['crc_valid']=False
            elif gate=='RAW_CANDIDATE_UNIVERSE_UNCHANGED':
                mutate('02_q1_source_binding_crosswalk.csv',lambda rr:rr[0].update(raw_row_sha256='ALTERED'))
            elif gate=='SEARCH_AND_RELATION_CANDIDATES_SEPARATED':
                mutate('03_q1_pair_qualification.csv',lambda rr:rr[0].update(search_candidate_status='ACCEPTED_RELATION'))
            elif gate in ('SOURCE_BINDING_REQUIRED','TARGET_FEATURE_ALONE_NOT_RELATION','W_A01_SOURCE_BOUND',
                'W_P01_SAME_TYPE_NOT_RELATION_BY_ITSELF','W_H01_ACTIVE_PARTICIPANT_REQUIRED',
                'CORPUS_ANALOGUE_NOT_RELATION_BINDING','PROSODY_NOT_HIERARCHY_EDGE_BY_ITSELF'):
                mutate('source_binding_witnesses.csv',lambda rr:rr[0].update(source_id='99999'))
            elif gate=='JIN_RULE_SOURCE_BINDING_AUDITED':
                mutate('06_q1_jin_rule_audit.csv',lambda rr:rr[0].update(source_bound='UNAUDITED'))
            elif gate=='VALENCY_BEFORE_RELATION_PRESERVED':
                mutate('03_q1_pair_qualification.csv',lambda rr:next(r for r in rr if r['target_id']=='5').update(qualified_relations=['HYPOTACTIC']))
            elif gate=='QUALIFIED_RELATION_UNIVERSE_CREATED':
                mutate('07_q1_qualified_relation_universe.csv',lambda rr:rr.pop())
            elif gate=='STRUCTURAL_OUTCOME_GROUPS_CREATED':
                mutate('09_q1_structural_outcomes.csv',lambda rr:rr[0].update(source_or_peer='99999'))
            elif gate=='MULTIPLE_CANDIDATES_NOT_EQUAL_MULTIPLE_OUTCOMES':
                mutate('10_q1_structural_outcome_groups.csv',lambda rr:rr.append(dict(rr[0],structural_outcome_group_id='PROVENANCE_ONLY_DUPLICATE')))
            elif gate in ('VARIANT_MEMBER_NOT_EQUAL_REVIEW_REQUIRED','VARIANT_DECISION_PIVOT_IMPLEMENTED',
                          'GIANT_COMPONENT_MEMBERSHIP_NOT_REVIEW_TRIGGER'):
                mutate('11_q1_variant_pivots.csv',lambda rr:rr[0].update(status='VARIANT_DECISION_PIVOT',review_required=True))
            elif gate in ('NO_NUMERIC_SCORE','NO_DISTANCE_CUTOFF','NO_TOP_N'):
                def policy_mutant(source,target,matches,witnesses,**kw):
                    r=qualify(source,target,matches,witnesses,**kw)
                    if gate=='NO_NUMERIC_SCORE' and any(m.get('score',0)<0 for m in matches):r['qualified_paths']=[]
                    if gate=='NO_DISTANCE_CUTOFF' and int(target)-int(source)>20:r['qualification']='EVIDENCE_ONLY'
                    if gate=='NO_TOP_N':r['qualified_paths']=r['qualified_paths'][:1]
                    return r
                with patch('milal_q1_synthetic.qualify',policy_mutant):semantics=semantic_checks()
            elif gate in ('NO_NEW_HUMAN_JUDGMENT','MFR02A_13_PRESERVED'):
                mutate('14_q1_mfr02a_13_case_reaudit.csv',lambda rr:rr[0]['original_decision'].update(researcher_decision='AUTO_ACCEPTED'))
            elif gate=='NO_CANONICAL_MOTHER':
                mutate('11_q1_variant_pivots.csv',lambda rr:rr[0].update(canonical_mother='AUTO_SELECTED'))
            elif gate=='NO_CANONICAL_HIERARCHY':
                mutate('11_q1_variant_pivots.csv',lambda rr:rr[0].update(canonical_hierarchy='AUTO_SELECTED'))
            elif gate=='CONTROL_FIXTURES_ONLY':
                mutate('16_q1_control_fixture_validation.csv',lambda rr:rr[0].update(full_external_book_analysis=True))
            elif gate=='FULL_REGRESSION_PASS':receipts['tests']['failures']=1
            elif gate=='SKIP_ZERO':receipts['tests']['skipped']=1
            elif gate=='DETERMINISTIC_RERUN':receipts['independent_bytes_equal']=False
            elif gate=='MANIFEST_VALID':(out/'UNMANIFESTED.txt').write_text('mutation')
            else:raise AssertionError('missing gate mutation '+gate)
            if gate!='MANIFEST_VALID':manifest(out)
            gates=evaluate(audit(self.source,out,self.grammar,receipts,semantics))
            self.assertIn(gate,[r['gate'] for r in gates if not r['passed']])
    return test


for gate in GATES:setattr(Q1Tests,'test_negative_gate_'+gate.lower(),gate_negative(gate))

if __name__=='__main__':unittest.main()
