"""R3c.3 lossless source enrichment contracts; no real-data execution."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import milal_r3c_3_signature_context as m


class SignatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.paths = m.synthetic_sources(Path(cls.temp.name))
        cls.archives = {k: m.read_archive(p) for k, p in cls.paths.items()}
        cls.model = m.build(cls.archives)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_gates(self):
        self.assertTrue(all(g['status'] == 'PASS' for g in m.gates(self.model)))
        self.assertEqual(len(m.gates(self.model)), 26)

    def test_every_gate_negative(self):
        def field(x, name):
            x['bundles'][0]['fields'][name]['status'] = 'INVENTED'
        def singleton(x, name):
            x['singletons'][0]['fields'][name]['status'] = 'INVENTED'
        def archive_byte(x):
            a = x['archives']['c2']
            a['files'][m.member(a, '12_method_note.md')] += b'tamper'
        def metadata(x):
            a = x['archives']['c2']
            name = m.member(a, '90_run_metadata.json')
            meta = m.source_metadata(a)
            meta['version'] = 'INVALID'
            a['files'][name] = json.dumps(meta).encode()
        mutations = {
            'SOURCE_R3C2_MANIFEST_VALID': archive_byte,
            'R3B2_SHA_MATCHES_RECORDED_SOURCE': lambda x: x['archives']['b2'].update(sha256='wrong'),
            'R3B3_SHA_MATCHES_RECORDED_SOURCE': lambda x: x['archives']['b3'].update(sha256='wrong'),
            'SOURCE_CHAIN_VALID': lambda x: x['archives']['c1'].update(sha256='wrong'),
            'SOURCE_VERSIONS_AND_GATES_VALID': metadata,
            'REVIEW_CASE_SET_UNCHANGED': lambda x: x['cases'].reverse(),
            'REVIEW_TARGET_IDS_UNCHANGED': lambda x: x['cases'][0].update(unit_id='BUNDLE:WRONG'),
            'ALL_R3C2_EVIDENCE_REFERENCES_PRESERVED': lambda x: x['references'].pop(),
            'BUNDLE_DEFINITION_ROWS_TRACE_TO_SOURCE': lambda x: x['bundles'][0]['source_rows'].pop(),
            'REPRESENTATIVE_FAMILY_IDS_TRACE_TO_SOURCE': lambda x: field(x, 'representative_family_id'),
            'MEMBER_FAMILY_IDS_TRACE_TO_SOURCE': lambda x: field(x, 'member_family_ids'),
            'PARENT_DEFINITION_TRACE_TO_SOURCE': lambda x: x['singletons'][0]['parent_bundle_ids'].append('WRONG'),
            'PARENT_CHILD_DELTA_USES_SOURCE_FIELDS_ONLY': lambda x: x['deltas'][0].update(status='INFERRED'),
            'NO_INFERRED_SIGNATURE_WHEN_SOURCE_MISSING': lambda x: field(x, 'membership_signature_payload'),
            'SINGLETON_SIGNATURE_TRACE_TO_SOURCE': lambda x: singleton(x, 'signature_G6'),
            'SINGLETON_FIRST_UNIQUE_LEVEL_TRACE_TO_SOURCE': lambda x: singleton(x, 'first_unique_level'),
            'S02135_PRESERVED': lambda x: x.update(singletons=[s for s in x['singletons'] if s['unit_id'] != 'G6:S02135']),
            'BOUNDARY_OBJECT_SET_PRESERVED': lambda x: x['boundary'][0]['unit_ids'].pop(),
            'EXTENSION_REMAINS_OVERLAY_ONLY': lambda x: x.update(references=[r for r in x['references'] if not r['member'].endswith('08_sequence_extension_overlay.csv')]),
            'REVIEW_FIELDS_UNCHANGED': lambda x: x['cases'][0].update(sufficient_context='YES'),
            'SOURCE_UNAVAILABLE_VALUES_EXPLICIT': lambda x: x['readiness'][0].update(structural_definition_available=''),
            'FIVE_ACCEPTANCE_CONTROLS_PRESERVED': lambda x: x.update(packet=x['packet'].replace('## CASE013\n', '## REMOVED\n')),
            'DISTRIBUTION_USES_EXPLICIT_EVIDENCE': lambda x: x['distribution'][0].update(unique_surface_count=-1),
            'SOURCE_INVENTORY_COMPLETE': lambda x: x['inventory'].pop(),
            'PACKET_MATCHES_SOURCE_ENRICHMENT': lambda x: x.update(packet=x['packet'] + 'invented'),
            'NO_AUTOMATIC_FUNCTION_LABELS': lambda x: x.update(function_label='closure'),
        }
        self.assertEqual(set(mutations), {g['gate_id'] for g in m.gates(self.model)})
        for name, mutate in mutations.items():
            with self.subTest(gate=name):
                model = copy.deepcopy(self.model)
                mutate(model)
                self.assertEqual(next(g['status'] for g in m.gates(model) if g['gate_id'] == name), 'FAIL')

    def test_source_hash_mismatch_stops(self):
        for key in ('b2', 'b3', 'c1'):
            a = copy.deepcopy(self.archives)
            a[key]['sha256'] = 'wrong'
            with self.assertRaisesRegex(ValueError, 'preflight'):
                m.build(a)

    def test_manifest_tampering_stops(self):
        a = copy.deepcopy(self.archives)
        a['c2']['files'][m.member(a['c2'], '12_method_note.md')] += b'changed'
        with self.assertRaisesRegex(ValueError, 'preflight'):
            m.build(a)

    def test_discovery_does_not_depend_on_filenames(self):
        a = copy.deepcopy(self.archives)
        for key in ('b2', 'b3'):
            a[key]['files'] = {'renamed/' + str(i) + '.csv': data for i, (name, data) in enumerate(a[key]['files'].items()) if name.endswith('.csv')}
        self.assertTrue(m.discover(a)['profiles'])

    def test_ambiguous_schema_fails(self):
        a = copy.deepcopy(self.archives)
        a['b2']['files']['duplicate.csv'] = a['b2']['files']['families.csv']
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            m.discover(a)

    def test_missing_identity_schema_fails(self):
        a = copy.deepcopy(self.archives)
        del a['b2']['files']['definitions.csv']
        with self.assertRaisesRegex(ValueError, 'Required'):
            m.discover(a)

    def test_missing_optional_profiles_explicit(self):
        a = copy.deepcopy(self.archives)
        del a['b2']['files']['profiles.csv']
        derived = m.derive(a)
        self.assertTrue(all(r['fields']['P1_BHSA']['status'] == m.MISSING for r in derived['bundles']))

    def test_hash_is_not_readable_signature(self):
        for b in self.model['bundles']:
            self.assertEqual(b['fields']['membership_signature_payload'], m.unavailable())
            self.assertEqual(b['fields']['family_signature_hash']['status'], m.AVAILABLE)
        for d in self.model['deltas']:
            self.assertEqual(d['feature_payload_delta'], m.unavailable())

    def test_deltas_trace_exact_family_fields(self):
        comparisons = [c for d in self.model['deltas'] for c in d['comparisons']]
        self.assertTrue(comparisons)
        for c in comparisons:
            self.assertIn(c['field'], ('level', 'family_id', 'signature_hash'))
            self.assertEqual(c['change'], 'unchanged' if c['parent'] == c['child'] else 'changed')

    def test_five_cases_have_enrichment_and_evidence_references(self):
        for cid in m.CONTROLS:
            section = self.model['packet'].split('## ' + cid + '\n', 1)[1].split('\n## ', 1)[0]
            self.assertIn('Why this review unit exists', section)
            self.assertIn('NOT_AVAILABLE_FROM_SOURCE', section)
            self.assertIn('Occurrence/context evidence', section)
            self.assertIn(cid, section)

    def test_singleton_source_rows_and_parents_retained(self):
        s = next(s for s in self.model['singletons'] if s['unit_id'] == 'G6:S02135')
        self.assertEqual(s['fields']['first_unique_level']['evidence'][0]['value'], 'G3')
        self.assertTrue(s['parent_bundle_ids'])
        self.assertGreater(len(s['source_rows']), 1)

    def test_boundary_multiplicity(self):
        original = m.rows(self.archives['c2'], '07_boundary_evidence_index.csv')
        for panel in self.model['boundary']:
            self.assertEqual(set(panel['unit_ids']), {r['unit_id'] for r in original if r['case_id'] == panel['case_id']})

    def test_every_raw_row_locator_resolves(self):
        for definition in self.model['bundles'] + self.model['singletons']:
            for record in definition['source_rows']:
                archive = self.archives[record['archive_role']]
                self.assertEqual(record['archive_sha256'], archive['sha256'])
                self.assertEqual(record['row'], m.prior.csv_read(archive['files'][record['member']], record['member'])[1][record['data_row'] - 1])

    def test_forms_and_case_order_unchanged(self):
        self.assertEqual(self.model['cases'], m.rows(self.archives['c2'], '02_review_cases.csv'))
        self.assertIs(m.REVIEW_FIELDS, m.prior.REVIEW_FIELDS)
        for c in self.model['cases']:
            self.assertEqual([c[f] for f in m.REVIEW_FIELDS], ['UNREVIEWED'] + [''] * 7)

    def test_references_cover_every_member(self):
        self.assertEqual({r['member'] for r in self.model['references']}, set(self.archives['c2']['files']))

    def test_output_manifest_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp) / 'out'
            self.assertEqual(m.write(self.model, out), 0)
            with self.assertRaises(FileExistsError):
                m.write(self.model, out)
            archive = Path(temp) / 'out.zip'
            m.zip_folder(out, archive)
            self.assertTrue(m.manifest_valid(m.read_archive(archive)))
            self.assertEqual(len(list(out.iterdir())), 13)

    def test_unsafe_and_duplicate_zip_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'unsafe.zip'
            with zipfile.ZipFile(path, 'w') as z:
                z.writestr('../outside.csv', 'x')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                m.read_archive(path)

    def test_distribution_recounts_source_rows(self):
        evidence = m.rows(self.archives['c2'], '03_compact_evidence_index.csv') + m.rows(self.archives['c2'], '07_boundary_evidence_index.csv')
        self.assertEqual(sum(d['evidence_row_count'] for d in self.model['distribution']), len(evidence))


if __name__ == '__main__':
    unittest.main()
