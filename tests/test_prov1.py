"""PROV1 reconstruction, lossless links and one negative test per gate."""
import copy
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import milal_prov1_signature_provenance as m
from milal_prov1_synthetic import synthetic_source


class ProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = synthetic_source()
        cls.model = m.build(cls.source)

    def test_all_gates(self):
        checks = m.gates(self.model)
        self.assertEqual(21, len(checks))
        self.assertTrue(all(g['status'] == 'PASS' for g in checks))
        files = m.serialize(self.model)
        self.assertTrue(m.manifest_ok(files))
        self.assertEqual(22, len(list(csv.DictReader(io.StringIO(files['09_gates.csv'].decode())))))

    def test_historical_g0_golden(self):
        row = self.source['tables']['atoms'][0]
        p = m.reconstruct_atom(row)[0]
        self.assertEqual(m.canonical_json(p), '[["G0_atom_type",["xYq0"]]]')
        ah = m.sig(p)
        self.assertEqual(ah, 'd196bac7148df9b835bcd0488b8b773efd47ee468e1cb69264b68ebd5bbf36eb')
        self.assertEqual(m.sig(('G0', 1, (ah,))), '86e9842e9af2e1fff286a73aeaa4a2e11c3ebac101d69eabb3ca0434fa366ded')

    def test_target_atom_hash_is_not_reconstruction_input(self):
        source = copy.deepcopy(self.source)
        source['tables']['atoms'][0]['signature_G0'] = 'wrong'
        model = m.build(source)
        self.assertEqual(self.model['atoms'][0]['reconstructed_hash'], model['atoms'][0]['reconstructed_hash'])
        self.assertFalse(model['atoms'][0]['hash_match'])
        self.assertEqual('FAIL', next(g['status'] for g in m.gates(model) if g['gate_id'] == 'ATOM_HASHES_EXACT'))

    def test_target_family_hash_is_not_reconstruction_input(self):
        source = copy.deepcopy(self.source)
        fid = source['tables']['families'][0]['family_id']
        source['tables']['families'][0]['signature_hash'] = 'wrong'
        for r in source['tables']['members']:
            if r['family_id'] == fid: r['signature_hash'] = 'wrong'
        model = m.build(source)
        self.assertEqual(self.model['families'][0]['reconstructed_hash'], model['families'][0]['reconstructed_hash'])
        self.assertFalse(model['families'][0]['hash_match'])

    def test_normalization_and_unicode(self):
        for v in [None, '', 'NA', 'n/a', 'absent', '?', 'None', 'none', 'null']:
            self.assertEqual('∅', m.norm(v))
        for v in ['unknown', '∅', ' NA ', 'UNKNOWN']:
            self.assertEqual(v, m.norm(v))
        self.assertEqual('["∅","איוב",[]]', m.canonical_json(('∅', 'איוב', ())))

    def test_order_and_hash_domain(self):
        self.assertNotEqual(m.sig(('G1', 2, ('a', 'b'))), m.sig(('G1', 2, ('b', 'a'))))
        self.assertNotEqual(m.sig(('G1', 1, ('a',))), m.sig(('G2', 1, ('a',))))
        self.assertNotEqual(m.sig(('G1', 1, ('a',))), m.sig('a'))

    def test_singleton_first_unique_and_atom_domain(self):
        s = next(s for s in self.model['singletons'] if 'S02135' in s['review_item_ids'])
        self.assertEqual('G3', s['first_unique_level'])
        self.assertEqual(2, s['cumulative_counts']['G2'])
        self.assertEqual(1, s['cumulative_counts']['G3'])
        self.assertEqual('b514a0f88b96d587993c54b3b325e3b6a68499203a3dc8d84c5ad5fe42c45d1f', s['atom_hashes'][6]['reconstructed_hash'])
        e = next(d for d in self.model['refinements'] if d['parent_family_id'] == 'F001969' and d['positions'][0]['atom_node'] == s['atom_node'])
        self.assertNotEqual(e['reconstructed_hash'], s['atom_hashes'][3]['reconstructed_hash'])

    def test_actual_added_component_visible(self):
        packet = self.model['five_cases']
        self.assertIn('Validation mode: SYNTHETIC', packet)
        self.assertIn('Validation mode: SYNTHETIC', self.model['catalog'])
        for text in ['F001301 → F001968', 'F001968 → F002481', 'G2_constituent_shape', 'G3_core_argument_realization', 'G6 atom hash', 'Separate window/refinement child hash']:
            self.assertIn(text, packet)

    def test_boundary_all_units_visible(self):
        units = json.loads(self.model['boundary'][0]['unit_ids'])
        self.assertGreater(len(units), 1)
        section = self.model['five_cases'].split('## CASE025')[1]
        for u in units: self.assertIn(u, section)

    def test_source_not_mutated(self):
        before = m.canonical_json(self.source)
        m.serialize(m.build(self.source))
        self.assertEqual(before, m.canonical_json(self.source))

    def test_occurrence_change_rejected(self):
        s = copy.deepcopy(self.source)
        s['tables']['occurrences'][0]['atom_nodes'] = '999'
        with self.assertRaisesRegex(ValueError, 'membership'): m.build(s)

    def test_bundle_occurrence_change_rejected(self):
        s = copy.deepcopy(self.source)
        s['tables']['bundle_occurrences'].pop()
        with self.assertRaisesRegex(ValueError, 'membership'): m.build(s)

    def test_nonadjacent_genealogy_rejected(self):
        s = copy.deepcopy(self.source)
        s['tables']['refinements'][0]['child_level'] = 'G6'
        with self.assertRaisesRegex(ValueError, 'genealogy'): m.build(s)

    def test_missing_component_rejected(self):
        s = copy.deepcopy(self.source)
        del s['tables']['atoms'][0]['G5_general_content_lexemes']
        with self.assertRaisesRegex(ValueError, 'Schema'): m.build(s)

    def test_duplicate_identity_rejected(self):
        s = copy.deepcopy(self.source)
        s['tables']['atoms'].append(s['tables']['atoms'][0])
        with self.assertRaisesRegex(ValueError, 'duplicate'): m.build(s)

    def test_missing_singleton_rejected(self):
        s = copy.deepcopy(self.source)
        s['tables']['singletons'].pop()
        with self.assertRaisesRegex(ValueError, 'population'): m.build(s)

    def test_preflight_wrong_bytes_before_zip_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'bad'; p.write_bytes(b'not a zip')
            with self.assertRaisesRegex(ValueError, 'SHA256 mismatch'):
                m.load({k: p for k in m.EXPECTED})

    def test_fresh_output_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = m.write(self.model, Path(tmp) / 'output')
            self.assertEqual(12, len(list(out.iterdir())))
            self.assertTrue(m.manifest_ok({p.name: p.read_bytes() for p in out.iterdir()}))
            with self.assertRaises(FileExistsError): m.write(self.model, out)

    def test_cli_synthetic_only(self):
        p = subprocess.run([sys.executable, '-B', str(ROOT / 'src/milal_prov1_signature_provenance.py'), '--self-test'], capture_output=True, text=True)
        self.assertEqual(0, p.returncode, p.stderr)
        self.assertIn('22/22', p.stdout)

    def test_verified_loader_synthetic_archive_roundtrip(self):
        # Exercise the real loader with independently sealed miniature archives;
        # production CLI pins cannot be overridden by a command-line flag.
        def zip_bytes(files):
            out = io.BytesIO()
            with zipfile.ZipFile(out, 'w') as z:
                for name, blob in files.items(): z.writestr(name, blob)
            return out.getvalue()
        by_role = {k: {} for k in ('r2', 'b2', 'b3', 'c3')}
        for key, (role, name, _) in m.SCHEMAS.items():
            by_role[role][name] = m.csv_bytes(self.source['tables'][key])
        blobs = {k: zip_bytes(v) for k, v in by_role.items() if k != 'c3'}
        expected = {k: m.sha(v) for k, v in blobs.items()}
        metadata = {'version':'R3c.3', 'gate_failures':[], 'sources':{k:{'sha256':expected[k]} for k in ('b2','b3')}}
        by_role['c3']['90_run_metadata.json'] = json.dumps(metadata).encode()
        m.add_manifest(by_role['c3'])
        blobs['c3'] = zip_bytes(by_role['c3'])
        blobs['generator'] = b'fixture generator bytes; never executed'
        expected.update({k:m.sha(blobs[k]) for k in ('c3','generator')})
        with tempfile.TemporaryDirectory() as tmp, patch.object(m, 'EXPECTED', expected):
            paths = {}
            for k, blob in blobs.items():
                paths[k] = Path(tmp) / k; paths[k].write_bytes(blob)
            model = m.build(m.load(paths))
            self.assertEqual(len(self.model['atoms']), len(model['atoms']))
            self.assertTrue(m.manifest_ok(m.serialize(model)))


MUTATIONS = {
    'GENERATOR_SHA_EXACT': lambda x: x['source']['hashes'].update(generator='bad'),
    'R2_ARCHIVE_SHA_EXACT': lambda x: x['source']['hashes'].update(r2='bad'),
    'DOWNSTREAM_SHA_EXACT': lambda x: x['source']['hashes'].update(b3='bad'),
    'SOURCE_SCHEMAS_VALID': lambda x: x['source']['tables']['atoms'][0].pop('atom_typ'),
    'ATOM_HASHES_EXACT': lambda x: x['atoms'][0].update(reconstructed_hash='bad'),
    'FAMILY_HASHES_EXACT': lambda x: x['families'][0].update(reconstructed_hash='bad'),
    'REFINEMENT_HASHES_EXACT': lambda x: x['refinements'][0].update(reconstructed_hash='bad'),
    'SINGLETON_HASHES_EXACT': lambda x: x['singletons'][0]['atom_hashes'][0].update(reconstructed_hash='bad'),
    'HISTORICAL_IDS_UNCHANGED': lambda x: x['families'][0].update(family_id='NEW'),
    'OCCURRENCES_UNCHANGED': lambda x: x['families'][0]['occurrences'].pop(),
    'GENEALOGY_UNCHANGED': lambda x: x['refinements'][0].update(parent_family_id='NEW'),
    'JUDGMENTS_UNFILLED': lambda x: x['cases'][0].update(sufficient_context='YES'),
    'NO_AUTOMATIC_LABELS': lambda x: x.update(function_label='closure'),
    'EXPLICIT_LOSSLESS_LINKS': lambda x: x['links'].pop(),
    'CASE001_PRESERVED': lambda x: x.update(five_cases=x['five_cases'].replace('## CASE001', 'REMOVED')),
    'CASE007_PRESERVED': lambda x: x.update(five_cases=x['five_cases'].replace('## CASE007', 'REMOVED')),
    'CASE013_PRESERVED': lambda x: x.update(five_cases=x['five_cases'].replace('## CASE013', 'REMOVED')),
    'S02135_PRESERVED': lambda x: x['singletons'][0].update(review_item_ids=['NEW']),
    'CASE025_MULTIPLICITY': lambda x: x['boundary'][0].update(unit_ids='[]'),
    'EXTENSION_OVERLAY_ONLY': lambda x: next(r for r in x['links'] if r['link_type'] == 'overlay').update(layer='CORE'),
    'AUDIT_COMPLETE': lambda x: x['audit'].pop(),
}


def negative(name, mutation):
    def test(self):
        model = copy.deepcopy(self.model)
        mutation(model)
        self.assertEqual('FAIL', next(g['status'] for g in m.gates(model) if g['gate_id'] == name))
    return test


for name, mutation in MUTATIONS.items():
    setattr(ProvenanceTests, 'test_negative_' + name.lower(), negative(name, mutation))


class ManifestNegativeTests(unittest.TestCase):
    def test_negative_output_manifest_integrity(self):
        files = m.serialize(m.build(synthetic_source()))
        files['07_human_readable_signature_catalog.md'] += b'tampered'
        self.assertEqual('FAIL', m.manifest_gate(files)['status'])

    def test_negative_gate_coverage(self):
        self.assertEqual(set(MUTATIONS), {g['gate_id'] for g in m.gates(m.build(synthetic_source()))})


if __name__ == '__main__':
    unittest.main()
