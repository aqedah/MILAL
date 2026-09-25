import copy
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_h0_synthetic import source_fixture
from milal_mfr02r_h0 import run, load_config
from milal_h0_validation import audit,evaluate,GATE_FIELDS
from milal_mfr02r_data import rows,table,manifest,verify_manifest


class H0Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=Path(cls.temp.name)
        cls.source=source_fixture(cls.root/'source');cls.out=cls.root/'out'
        cls.config=load_config();cls.config['job_validation_refs']=[]
        cls.stats=run(cls.source,cls.out,cls.config,synthetic=True)
        cls.receipts=dict(baseline=dict(baseline=cls.config['baseline'],differences=[]),
            tests=dict(test_scope='FULL_REGRESSION',failures=0,errors=0,skipped=0,tests_run=1))
        # Explicit in-memory gate fixture, never an empirical test receipt.
        cls.measured=audit(cls.source,cls.out,cls.config,cls.receipts,True)

    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()

    def test_all_computed_synthetic_gates(self):
        self.assertEqual(set(GATE_FIELDS),set(self.config['gates']))
        self.assertTrue(all(r['passed'] for r in evaluate(self.measured)),[r for r in evaluate(self.measured) if not r['passed']])

    def test_independent_determinism(self):
        b=self.root/'b';run(self.source,b,self.config,synthetic=True)
        self.assertEqual(list(rows(self.out/'99_manifest_sha256.csv')),list(rows(b/'99_manifest_sha256.csv')))

    def test_original_not_modified(self):self.assertTrue(verify_manifest(self.source))

    def test_missing_source_schema_fails(self):
        from milal_review_eligibility import classify
        with self.assertRaises(KeyError):classify({}, {})

    def test_compact_pages_complete(self):
        cards=list(rows(self.out/'display_card_manifest.csv'))
        self.assertEqual(sum(int(r['card_count']) for r in cards),self.stats['human_review_candidate_total'])
        self.assertTrue(all(int(r['largest_page'])<=10 for r in cards))
        page=next((self.out/'packets').glob('*_0001.md')).read_text(encoding='utf8')
        self.assertIn('Exact source fields',page);self.assertIn('observed predicates',page)
        self.assertIn('SOURCE_TARGET_OBSERVATIONS',page)
        self.assertIn('identity remains',page)

    def test_no_ready_claim_from_synthetic(self):
        from milal_h0_runner import release
        with self.assertRaises((ValueError,KeyError)):release(self.out,self.out)

    def test_current_classification_independent_of_history(self):
        changed=self.root/'history_source';shutil.copytree(self.source,changed)
        old=list(rows(changed/'mfr02a_original_decisions.csv'));old[0]['researcher_decision']='HYPOTACTIC'
        table(changed/'mfr02a_original_decisions.csv',old);manifest(changed)
        dest=self.root/'history_out';run(changed,dest,self.config,synthetic=True)
        self.assertEqual((self.out/'01_h0_candidate_review_eligibility.csv').read_bytes(),(dest/'01_h0_candidate_review_eligibility.csv').read_bytes())

    def test_artifact_missing_candidate_detected(self):
        changed=self.root/'mutated';shutil.copytree(self.out,changed)
        values=list(rows(changed/'01_h0_candidate_review_eligibility.csv'));table(changed/'01_h0_candidate_review_eligibility.csv',values[:-1])
        result={r['gate']:r['passed'] for r in evaluate(audit(self.source,changed,self.config,self.receipts,True))}
        self.assertFalse(result['NO_CANDIDATE_DELETED']);self.assertFalse(result['CANDIDATE_UNIVERSE_ROW_COUNT_UNCHANGED'])
        self.assertFalse(result['HISTORICAL_JUDGMENT_NO_LEAKAGE']);self.assertFalse(result['MANIFEST_VALID'])

    def test_nonselectivity_is_warning_not_candidate_pruning(self):
        from milal_mfr02r_h0 import metrics
        targets=[dict(raw_candidate_count=2,eligible_candidate_ids=['a','b'],target_review_status='TARGET_REVIEW_REQUIRED',review_tier='TIER_2')]
        m=metrics(targets,{'RELATION_ELIGIBLE':2},self.config)
        self.assertIn('REVIEW_SIEVE_NOT_SELECTIVE',m['warnings']);self.assertEqual(m['human_review_candidate_total'],2)

    def test_ninety_two_percent_required_warns(self):
        from milal_mfr02r_h0 import metrics
        targets=[dict(raw_candidate_count=2,eligible_candidate_ids=['a','b'],target_review_status='TARGET_REVIEW_REQUIRED' if i<92 else 'TARGET_ARCHIVE_ONLY',review_tier='TIER_2' if i<92 else '') for i in range(100)]
        m=metrics(targets,{'RELATION_ELIGIBLE':200},self.config)
        self.assertIn('REVIEW_SIEVE_NOT_SELECTIVE',m['warnings'])
        self.assertEqual(m['human_review_candidate_total'],200)


def negative(gate,field):
    def test(self):
        changed=copy.deepcopy(self.measured)
        changed[field]['actual']={'INVARIANT_MUTATION':changed[field]['actual']}
        found={r['gate']:r for r in evaluate(changed)}
        self.assertFalse(found[gate]['passed'])
    return test


for gate,field in GATE_FIELDS.items():
    setattr(H0Tests,'test_negative_'+gate.lower(),negative(gate,field))
