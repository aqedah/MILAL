"""Explicit authority, exact identity, frozen preservation and negative H0.2 gates."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_h02_overlay import build, bind_registry, write_outputs, reports
from milal_h02_validation import evaluate, gates, MUTATIONS
from milal_h02_synthetic import fixture, CASE_GATES, self_test
from milal_h02_runner import read_state, authority, CONFIG, current_receipts
from milal_mfr02r_data import manifest,verify_manifest,pack,digest
from milal_mfr02r_io import verify_archive


class H02Tests(unittest.TestCase):
    def test_all_gates_and_negative_coverage(self):
        e=fixture();self.assertTrue(all(evaluate(e).values()))
        self.assertEqual(set(evaluate(e)),set(MUTATIONS))

    def test_missing_relation_never_fuzzy_matched(self):
        e=fixture();e['authority'][0]['candidate_relation_id']='missing'
        with self.assertRaisesRegex(ValueError,'exact relation'):
            bind_registry(e['original_outcomes'],e['packets'],e['pivots'],e['authority'])

    def test_wrong_atom_rejected(self):
        e=fixture();e['authority'][0]['target_atom_ids']=[1]
        with self.assertRaisesRegex(ValueError,'atom'):
            bind_registry(e['original_outcomes'],e['packets'],e['pivots'],e['authority'])

    def test_wrong_alternative_rejected(self):
        e=fixture();e['authority'][0]['alternative_id']='wrong'
        with self.assertRaisesRegex(ValueError,'alternative'):
            bind_registry(e['original_outcomes'],e['packets'],e['pivots'],e['authority'])

    def test_wrong_primary_binding_rejected(self):
        e=fixture();e['authority'][0]['machine_binding']=['SB01']
        with self.assertRaisesRegex(ValueError,'binding'):
            bind_registry(e['original_outcomes'],e['packets'],e['pivots'],e['authority'])

    def test_duplicate_relation_rejected(self):
        e=fixture();e['original_outcomes'].append(deepcopy(e['original_outcomes'][0]))
        with self.assertRaisesRegex(ValueError,'duplicate source'):
            bind_registry(e['original_outcomes'],e['packets'],e['pivots'],e['authority'])

    def test_no_implicit_decision_from_proximity(self):
        e=fixture();e['authority'][1]['rationale_observations']=['IMMEDIATE_LOCALITY_DESCRIPTIVE_ONLY']
        with self.assertRaisesRegex(ValueError,'proximity'):
            build(e['original_outcomes'],e['packets'],e['pivots'],e['authority'],e['original_historical'])

    def test_inputs_remain_unchanged(self):
        e=fixture();before=deepcopy(e)
        build(e['original_outcomes'],e['packets'],e['pivots'],e['authority'],e['original_historical'])
        self.assertEqual(e,before)

    def test_authority_bytes_and_no_invented_adjudication_date(self):
        registry,_=authority(json.loads(CONFIG.read_text(encoding='utf8')))
        self.assertTrue(all(r['adjudication_date']=='NOT_SUPPLIED' for r in registry))
        self.assertEqual(len({r['judgment_id'] for r in registry}),1)

    def test_serialized_outputs_and_independent_archives(self):
        e=fixture()
        with tempfile.TemporaryDirectory() as d:
            root=Path(d); zs=[]
            for name in ('a','b'):
                p=root/name;p.mkdir();write_outputs(p,e['state'])
                (p/'overlay_scope.json').write_text(json.dumps(dict(new_relations=[],canonical_hierarchy=[])),encoding='utf8')
                ee=deepcopy(e);ee['state']=read_state(p)
                self.assertTrue(all(evaluate(ee).values()))
                manifest(p);self.assertTrue(verify_manifest(p));z=root/(name+'.zip');pack(p,z);zs.append(z)
                self.assertTrue(verify_archive(z,digest(z))['crc_valid'])
            self.assertEqual(zs[0].read_bytes(),zs[1].read_bytes())
            (root/'a/08_h02_ki_function_caution.md').write_text('changed',encoding='utf8')
            self.assertFalse(verify_manifest(root/'a'))

    def test_self_test(self):
        with tempfile.TemporaryDirectory() as d:
            r=self_test(Path(d)/'synthetic.json')
            self.assertTrue(r['passed']);self.assertEqual(len(r['cases']),12)
            self.assertTrue((Path(d)/'synthetic.md').is_file())

    def test_invalid_receipts_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'s.json';q=Path(d)/'r.json'
            p.write_text('{}');q.write_text('{}')
            with self.assertRaises(ValueError):current_receipts(p,q,'current')

    def test_human_report_scope(self):
        text=reports(fixture()['state'])
        self.assertIn('NO_DIRECT_STRICT_MOTHER_RELATION',text['07_h02_job_37_20_adjudication.md'])
        self.assertIn('proximity alone would be insufficient',text['10_h02_method_report.md'])
        self.assertIn('Do not start H1.0 automatically',text['11_h02_next_scope.md'])


def negative(name):
    def test(self):
        e=fixture();MUTATIONS[name](e)
        self.assertFalse(evaluate(e)[name])
        with self.assertRaises(ValueError):gates(e)
    return test


def synthetic_case(names):
    def test(self):
        e=fixture()
        for name in names:
            self.assertTrue(evaluate(e)[name]);bad=deepcopy(e);MUTATIONS[name](bad)
            self.assertFalse(evaluate(bad)[name])
    return test


for name in MUTATIONS:setattr(H02Tests,'test_negative_'+name.lower(),negative(name))
for name,names in CASE_GATES.items():setattr(H02Tests,'test_'+name.replace('-','_'),synthetic_case(names))
if __name__=='__main__':unittest.main()
