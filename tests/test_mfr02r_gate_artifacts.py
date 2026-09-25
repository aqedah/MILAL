"""Each gate is challenged through its source artifact, receipt or control input."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from test_mfr02r_grammar import ROOT, sample
import milal_mfr02r_gates as gates
from milal_mfr02r_data import table, rows, encode, manifest, digest
from milal_mfr02r_engine import run_engine
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_review import REVIEW_FIELDS, EXTRA_REVIEW_FIELDS
from milal_mfr02r_pipeline import release, code_fingerprint

NAMES = json.loads((ROOT/'config/mfr_0_2r_required_gates.json').read_text())['gates']


class ArtifactGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.storage = tempfile.TemporaryDirectory()
        cls.base = Path(cls.storage.name)/'base'; (cls.base/'src').mkdir(parents=True)
        (cls.base/'config').mkdir()
        shutil.copy2(ROOT/'config/mfr_0_2r_required_gates.json', cls.base/'config')
        for name in ('engine','features','grammar','graph','layers','valency','revision'):
            shutil.copy2(ROOT/'src'/('milal_mfr02r_'+name+'.py'), cls.base/'src')
        cls.registry = load_registry(ROOT/'config/clause_relation_grammar_v1.json')
        labels = json.loads((ROOT/'config/mfr_0_2r_evidence_labels.json').read_text())
        out = cls.base/'out'; job = out/'blind/job'
        observations=sample()
        for row in observations: row['book']='Iob'
        run_engine(observations,cls.registry,[],job,label_definitions=labels,analysis_scope='FIXTURE',comparison_scope='FIXTURE_CORPUS')
        search=out/'corpus_search';search.mkdir()
        (search/'hb_comparison_index.json').write_text('{}')
        (search/'corpus_search_receipt.json').write_text(encode(dict(analysis_scope='JOB',corpus_comparison_scope='HB_CORPUS',
            hierarchy_generated=False,unique_clauses=7,comparison_index_sha256=digest(search/'hb_comparison_index.json'))))
        original = dict(decision_id='SYNTHETIC',researcher_decision='PARATACTIC')
        table(out/'mfr02a_original_decisions.csv',[original])
        table(out/'18_mfr02a_revalidation.csv',[dict(decision_id='SYNTHETIC',original_decision=original,
            provisional_status='PROVISIONAL_HUMAN_ADJUDICATION',revised_human_decision='')])
        table(out/'24_human_review_cases.csv',[{k:'' for k in (*REVIEW_FIELDS,*EXTRA_REVIEW_FIELDS)}])
        cls.review = dict(new_human_judgments=0,original_decision_hashes={'SYNTHETIC':hashlib.sha256(encode(original).encode()).hexdigest()})
        cls.config = json.loads((ROOT/'config/mfr_0_2r_job.json').read_text())
        tree = ast.parse((ROOT/'src/milal_mfr02r_gates.py').read_text())
        proofs = {n.args[0].value for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='proof'}
        # These are explicitly synthetic receipt inputs for testing the gate
        # evaluator; they are never persisted as an empirical validation receipt.
        cls.tests = dict(passed_tests=['fixture.'+n for n in proofs],tests_run=2152,failures=0,errors=0,skipped=0,baseline=cls.config['baseline'])
        cls.control = dict(leviticus_candidates_recovered=4,numbers_variants_representable=2,
            pentateuch_variants_representable=2,same_pattern_different_level=5,
            crossbook_candidate_counts=dict(explicit_fixtures=1),oosting_binding_controls=1,
            control_fixture_scope='EXPLICIT_REFERENCES_ONLY',fixture_scope_receipts={'pentateuch':dict(
                full_book_inventory_created=False,requested_references=[['Synthetic',1,1]],selected_clause_ids=[1],
                selection_reasons={'1':'EXPLICIT_VERSE_COMPLETE_CLAUSE'})})

    @classmethod
    def tearDownClass(cls):
        cls.storage.cleanup()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'root'; shutil.copytree(self.base,self.root)
        self.out = self.root/'out'; self.job = self.out/'blind/job'
        self.r = copy.deepcopy(self.registry); self.t = copy.deepcopy(self.tests)
        self.c = copy.deepcopy(self.control); self.v = copy.deepcopy(self.review)
        self.receipts = [dict(expected_sha256='SYNTHETIC_SAME_DIGEST',actual_sha256='SYNTHETIC_SAME_DIGEST')]

    def facts(self):
        with patch.object(gates,'ROOT',self.root):
            return gates.artifact_facts(self.job,self.r,self.t,self.config,self.receipts,self.c,self.v,self.out)

    def change(self,path,field,value):
        records=list(rows(path)); records[0][field]=value; table(path,records)

    def challenge(self,name):
        if name=='DETERMINISTIC_RERUN':
            a,b=self.root/'a',self.root/'b';a.mkdir();b.mkdir()
            (a/'value').write_text('one');(b/'value').write_text('two')
            manifest(a);manifest(b)
            with self.assertRaisesRegex(ValueError,'bytes differ'): release(a,b)
            return
        self.assertTrue(self.facts()[name], 'synthetic positive fixture: '+name)
        # Missing a required successful semantic-test receipt is a genuine
        # validation-evidence failure, rather than flipping a computed gate bit.
        self.t['passed_tests']=[]
        if name in ('BASELINE_COMMIT_VERIFIED','MFR_0_1_FROZEN','MFR_0_1A_FROZEN','MFR_0_1B_FROZEN','MFR_0_2A_FROZEN'):
            self.receipts[0]['actual_sha256']='SYNTHETIC_CHANGED_DIGEST'
        elif name=='RELATION_GRAMMAR_REGISTRY_CREATED': self.r['rules']=self.r['rules'][1:]
        elif name in ('MAIN_CLAUSE_PARATAXIS_RULES_ACTIVE','SAME_CLAUSE_TYPE_CAN_BE_HYPOTACTIC','DIFFERENT_CLAUSE_TYPE_CAN_BE_PARATACTIC'):
            records=list(rows(self.job/'09_candidate_evidence_matrix.csv'))
            for r in records:r['candidate_relations']='INSUFFICIENT'
            table(self.job/'09_candidate_evidence_matrix.csv',records)
        elif name=='FULL_PRECEDING_CANDIDATE_SET_GENERATED': self.change(self.job/'09_candidate_evidence_matrix.csv','candidate_clause_id',999999)
        elif name in {d+'_FIRST_CLASS_EVIDENCE' for d in ('TIME','LOCATION','PARTICIPANT','REFERENCE','DOMAIN')}:
            self.change(self.job/'02_clause_feature_inventory.csv',name.removesuffix('_FIRST_CLASS_EVIDENCE'),None)
        elif name=='TIME_PLACE_FIRST_CLASS_EVIDENCE': self.change(self.job/'02_clause_feature_inventory.csv','TIME',None)
        elif name in ('NO_PRIMARY_SUPPORT_EPISTEMIC_RANK','NO_NUMERIC_RELATION_SCORE'):
            p=self.root/'src/milal_mfr02r_features.py'
            with p.open('a') as f:f.write("\nPRIMARY_FORMAL_MARKER = 1\n" if name=='NO_PRIMARY_SUPPORT_EPISTEMIC_RANK' else '\nrelation_score = 1\n')
        elif name=='PROVISIONAL_RELATION_GRAPH_CREATED': table(self.job/'12_provisional_relation_graph.csv',[])
        elif name=='MFR02A_PROVISIONAL_STATUS_PRESERVED': self.change(self.out/'18_mfr02a_revalidation.csv','provisional_status','FINAL')
        elif name=='MFR02A_NOT_SILENTLY_OVERWRITTEN': self.change(self.out/'18_mfr02a_revalidation.csv','revised_human_decision','HYPOTACTIC')
        elif name=='LEV25_26_CONTROL_EXECUTED': self.c.pop('leviticus_candidates_recovered')
        elif name=='NUM26_VARIANT_CONTROL_EXECUTED': self.c['numbers_variants_representable']=1
        elif name=='PENTATEUCH_VARIANT_CONTROL_EXECUTED': self.c['pentateuch_variants_representable']=1
        elif name=='SAME_PATTERN_DIFFERENT_LEVEL_CONTROL_PASS': self.c['same_pattern_different_level']=0
        elif name=='BOOK_BOUNDARY_NOT_HIERARCHY_FILTER': self.c['crossbook_candidate_counts']={}
        elif name in ('RHETORIC_NOT_USED_IN_PASS1','SEMANTIC_CORRESPONDENCE_SECONDARY_ONLY'):
            self.change(self.job/'09_candidate_evidence_matrix.csv','RHETORICAL_SECONDARY',dict(status='LOADED'))
        elif name=='NO_NEW_HUMAN_JUDGMENT': self.change(self.out/'24_human_review_cases.csv','reviewer_notes','AUTOMATICALLY_FILLED')
        elif name in ('NO_CANONICAL_NEW_MOTHER','NO_CANONICAL_WHOLE_TREE'):
            self.change(self.job/'10_relation_candidates.csv','accepted_mother','1')
        elif name=='R4_4_CONSUMER_ABSENT': (self.root/'src/milal_mfr02r_consumer.py').write_text('')
        elif name=='FULL_REGRESSION_PASS': self.t['errors']=1
        elif name=='SKIP_ZERO': self.t['skipped']=1
        elif name=='MANIFEST_VALID': (self.job/'unexpected.txt').write_text('changed universe')
        elif name=='WALTON_SOURCE_PROVENANCE_COMPLETE': next(r for r in self.r['rules'] if r['source_author']=='WALTON')['source_work']=''
        elif name=='NO_CORRESPONDENCE_NOT_AUTO_ROOT': self.change(self.job/'target_search_receipts.csv','canonical_level',0)
        elif name=='BOSMAN_SOURCE_PROVENANCE_COMPLETE': self.change(self.job/'bosman_source_crosswalk.csv','source_work','')
        elif name=='RULE_DISCOVERY_DATASET_CREATED': table(self.job/'relation_decision_learning_table.csv',[])
        elif name=='NO_BLACK_BOX_LEARNING':
            with (self.root/'src/milal_mfr02r_layers.py').open('a') as f:f.write('\nimport sklearn\n')
        elif name=='OOSTING_SOURCE_PROVENANCE_COMPLETE': self.change(self.job/'construction_inventory.csv','source_author','UNATTRIBUTED')
        elif name=='VALENCY_LAYER_ACTIVE': table(self.job/'construction_inventory.csv',list(rows(self.job/'construction_inventory.csv'))[1:])
        elif name=='EXACT_CONSTRUCTION_SIGNATURE_AVAILABLE': self.change(self.job/'construction_inventory.csv','exact_construction_signature_id','')
        elif name=='OBSERVED_AND_GENERALIZED_PATTERNS_SEPARATE': self.change(self.job/'construction_inventory.csv','generalized_pattern','INVENTED')
        elif name=='CORPUS_SCOPE_SEPARATE_FROM_HIERARCHY_SCOPE': self.change(self.job/'corpus_analogue_evidence.csv','corpus_comparison_scope','FIXTURE')
        elif name=='TEXT_AS_ENCODED_PRIMARY_PASS': self.change(self.job/'construction_inventory.csv','analysis_form','EMENDED')
        elif name=='OOSTING_CONTROLS_EXECUTED': self.c.pop('oosting_binding_controls')
        elif name=='PRIMARY_ANALYSIS_SCOPE_JOB_ONLY': self.change(self.job/'02_clause_feature_inventory.csv','book','Genesis')
        elif name=='PENTATEUCH_FULL_ANALYSIS_ABSENT': (self.out/'blind/pentateuch').mkdir()
        elif name=='PENTATEUCH_CONTROLS_FIXTURE_ONLY': self.c['fixture_scope_receipts']['pentateuch']['full_book_inventory_created']=True
        elif name=='CORPUS_SEARCH_NOT_CONFUSED_WITH_ANALYSIS_SCOPE': (self.out/'corpus_search/hb_comparison_index.json').write_text('CHANGED')
        self.assertFalse(self.facts()[name], 'mutation did not fail gate: '+name)

    def test_release_rejects_missing_gate_universe_and_wrong_mode(self):
        for label, gate_rows, mode, error in [('missing',[], 'REAL','universe'),
            ('synthetic',[dict(gate=n,passed=True) for n in NAMES],'SYNTHETIC','mode')]:
            paths=[self.root/(label+s) for s in ('a','b')]
            for p in paths:
                p.mkdir();table(p/'27_gates.csv',gate_rows)
                (p/'90_run_metadata.json').write_text(encode(dict(stage='MFR.0.2R',mode=mode,code_fingerprint=code_fingerprint())))
                manifest(p)
            with self.assertRaisesRegex(ValueError,error): release(*paths)


for gate in NAMES:
    def check(self,name=gate): self.challenge(name)
    setattr(ArtifactGateTests,'test_artifact_negative_'+gate,check)
