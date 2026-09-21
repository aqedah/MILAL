"""HR1 invariants and their negative mutations; no real input dependencies."""
import copy
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import milal_hr1_adjudication_linkage as hr
from milal_hr1_synthetic import source_fixture, archive


class HR1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = source_fixture()
        cls.model = hr.build(cls.source)

    def assert_gate_fails(self, gate, mutate):
        model = copy.deepcopy(self.model)
        mutate(model)
        self.assertEqual({r['gate_id']:r['status'] for r in hr.gates(model)}[gate], 'FAIL')
        with self.assertRaises(ValueError): hr.serialize(model)

    def test_all_gates_and_determinism(self):
        files = hr.serialize(self.model)
        gates = hr.read_csv(files['09_gates.csv'])
        self.assertEqual(len(gates),22)
        self.assertTrue(all(r['status']=='PASS' for r in gates))
        self.assertEqual(files,hr.serialize(hr.build(source_fixture())))
        self.assertEqual(len(files),11)

    def test_negative_human_source_commit_verified(self):
        source = copy.deepcopy(self.source)
        source['source_commit'] = 'wrong'
        with self.assertRaisesRegex(ValueError,'source commit'): hr.build(source)

    def test_negative_exactly_30_adjudication_rows(self):
        self.assert_gate_fails('EXACTLY_30_ADJUDICATION_ROWS',lambda m:m['cases'].pop())

    def test_negative_case_ids_complete_unique(self):
        self.assert_gate_fails('CASE_IDS_COMPLETE_UNIQUE',lambda m:m['cases'][0].update(case_id='CASE002'))

    def test_negative_all_r3c3_cases_resolved(self):
        self.assert_gate_fails('ALL_R3C3_CASES_RESOLVED',lambda m:m['unresolved_links'].append('CASE001'))

    def test_negative_all_explicit_prov1_links_resolved(self):
        self.assert_gate_fails('ALL_EXPLICIT_PROV1_LINKS_RESOLVED',lambda m:m['provenance'].pop())

    def test_negative_no_fuzzy_linkage(self):
        self.assert_gate_fails('NO_FUZZY_LINKAGE',lambda m:m['ambiguous_links'].append('fuzzy'))

    def test_negative_human_fields_equivalent(self):
        self.assert_gate_fails('HUMAN_FIELDS_EQUIVALENT',lambda m:m['cases'][0].update(observable_behavior='automatic'))

    def test_negative_form_counts_exact(self):
        self.assert_gate_fails('FORM_COUNTS_EXACT',lambda m:m['cases'][0].update(form_assessment='CLEAR'))

    def test_negative_context_counts_exact(self):
        self.assert_gate_fails('CONTEXT_COUNTS_EXACT',lambda m:m['cases'][0].update(sufficient_context='NO'))

    def test_negative_all_reviewed(self):
        self.assert_gate_fails('ALL_REVIEWED',lambda m:m['cases'][0].update(review_status='UNREVIEWED'))

    def test_negative_time_unmeasured_blank(self):
        self.assert_gate_fails('TIME_UNMEASURED_BLANK',lambda m:m['cases'][0].update(review_time_seconds='0'))

    def test_negative_extension_dependency_preserved(self):
        self.assert_gate_fails('EXTENSION_DEPENDENCY_PRESERVED',lambda m:m['extensions'].clear())

    def test_negative_case028_continuity_caution(self):
        self.assert_gate_fails('CASE028_CONTINUITY_CAUTION',lambda m:m['cases'][27].update(reviewer_notes='adjacency implies continuity'))

    def test_negative_case029_job_addressee_caution(self):
        self.assert_gate_fails('CASE029_JOB_ADDRESSEE_CAUTION',lambda m:m['cases'][28].update(reviewer_notes=''))

    def test_negative_boundary_multiplicity_preserved(self):
        self.assert_gate_fails('BOUNDARY_MULTIPLICITY_PRESERVED',lambda m:m['boundary'][0]['participating_unit_ids'].pop())

    def test_negative_singleton_identities_preserved(self):
        self.assert_gate_fails('SINGLETON_IDENTITIES_PRESERVED',lambda m:m['cases'][18]['target_objects'][0].update(review_item_id='S999'))

    def test_negative_historical_hashes_unchanged(self):
        self.assert_gate_fails('HISTORICAL_HASHES_UNCHANGED',lambda m:m['provenance'][0]['locator'].update(row_sha256='wrong'))

    def test_negative_historical_ids_unchanged(self):
        self.assert_gate_fails('HISTORICAL_IDS_UNCHANGED',lambda m:m['cases'][0]['target_objects'][0].update(bundle_id='other'))

    def test_negative_membership_genealogy_unchanged(self):
        self.assert_gate_fails('MEMBERSHIP_GENEALOGY_UNCHANGED',lambda m:m['extensions'][0]['source_relation'].update(short_bundle_id='other'))

    def test_negative_source_zip_integrity(self):
        source = copy.deepcopy(self.source)
        source['blobs']['r3c3'] += b'changed'
        with self.assertRaisesRegex(ValueError,'SHA256'): hr.build(source)
        with zipfile.ZipFile(io.BytesIO(self.source['blobs']['r3c3'])) as z:
            files = {n:z.read(n) for n in z.namelist()}
        files['synthetic/02_review_cases.csv'] += b'changed'
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer,'w') as z:
            for n,b in files.items(): z.writestr(n,b)
        with self.assertRaisesRegex(ValueError,'manifest'): hr.read_zip(buffer.getvalue())

    def test_negative_reports_trace_to_human_source(self):
        self.assert_gate_fails('REPORTS_TRACE_TO_HUMAN_SOURCE',lambda m:m.update(acceptance='R4 authorized'))

    def test_negative_output_manifest_integrity(self):
        files = hr.serialize(self.model)
        files['07_human_review_pilot_report.md'] += b'changed'
        self.assertEqual(hr.prov.manifest_gate(files)['status'],'FAIL')

    def mutate_prov1(self, mutate):
        source = copy.deepcopy(self.source)
        a = hr.read_zip(source['blobs']['prov1'])
        files = {Path(n).name:b for n,b in a['files'].items()}
        rows = hr.read_csv(files['05_downstream_identity_links.csv'])
        mutate(rows)
        files['05_downstream_identity_links.csv'] = hr.prov.csv_bytes(rows)
        source['blobs']['prov1'] = archive(files)
        source['expected_hashes']['prov1'] = hr.sha(source['blobs']['prov1'])
        return source

    def test_missing_explicit_link_rejected(self):
        with self.assertRaisesRegex(ValueError,'Unresolved PROV1'):
            hr.build(self.mutate_prov1(lambda rows:rows.pop(0)))

    def test_duplicate_explicit_link_rejected(self):
        with self.assertRaisesRegex(ValueError,'Ambiguous PROV1'):
            hr.build(self.mutate_prov1(lambda rows:rows.append(dict(rows[0]))))

    def test_source_anchor_identity_rejected(self):
        def mutate(rows):
            anchor = json.loads(rows[0]['source']); anchor['data_row'] = 999
            rows[0]['source'] = hr.canonical(anchor)
        with self.assertRaisesRegex(ValueError,'locator disagrees'): hr.build(self.mutate_prov1(mutate))

    def test_all_human_fields_roundtrip_verbatim(self):
        output = hr.read_csv(hr.serialize(self.model)['01_case_adjudication_links.csv'])
        for actual, source in zip(output, hr.read_csv(self.source['blobs']['human'])):
            for field,value in source.items(): self.assertEqual(actual[field],value)

    def test_event_only_and_boundary_sources_remain_independent(self):
        cases = {c['case_id']:c for c in self.model['cases']}
        self.assertEqual(cases['CASE021']['target_objects'][0]['review_item_id'],hr.NA)
        self.assertEqual(cases['CASE021']['target_objects'][0]['family_ids'],['F21'])
        self.assertEqual(len(self.model['boundary']),6)
        self.assertTrue(all(len(r['participating_unit_ids'])==3 for r in self.model['boundary']))
        self.assertEqual(len(self.model['extensions']),5)
        self.assertTrue(hr.dependency_connected(self.model))

    def test_write_fresh_zip_log_and_no_source_mutation(self):
        before = copy.deepcopy(self.source)
        with tempfile.TemporaryDirectory() as d:
            output = Path(d)/'hr1_synthetic'
            zip_path,log = hr.write(self.model,output)
            hr.read_zip(zip_path.read_bytes())
            self.assertEqual(json.loads(log.read_text(encoding='utf-8'))['exit_code'],0)
            with self.assertRaises(FileExistsError): hr.write(self.model,output)
        self.assertEqual(before,self.source)

    def test_missing_columns_never_guessed(self):
        with self.assertRaises(ValueError): hr.read_csv(b'case_id\nCASE001\n',('case_type',))

    def test_self_test(self):
        self.assertEqual(hr.main(['--self-test']),0)


if __name__ == '__main__':
    unittest.main()
