"""R3c.1 structural unit contracts. All data are synthetic or historical extracts."""
import contextlib
import copy
import csv
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import milal_r3c_1_review_units as m


class ReviewUnitTests(unittest.TestCase):
    def setUp(self):
        self.tables, self.config, self.provider = m.synthetic_fixture()

    def build(self):
        return m.build_model(self.tables, self.config, self.provider)

    def test_population_and_all_gates(self):
        model = self.build()
        self.assertEqual(len(model['population']), 109)
        self.assertEqual(m.Counter(r['unit_type'] for r in model['population']), {m.BUNDLE: 82, m.SINGLETON: 27})
        gates = m.build_gates(model)
        self.assertEqual(len(gates), 24)
        self.assertTrue(all(g['status'] == 'PASS' for g in gates), gates)
        self.assertEqual(m.Counter(c['case_type'] for c in model['cases']), dict.fromkeys(m.CASE_TYPES, 6))
        self.assertIs(m.REVIEW_FIELDS, m.base.REVIEW_FIELDS)

    def test_high_and_low_full_lexicographic_tie_breaks(self):
        source = m.source_population(self.tables, self.config)
        # Independent hand-built measures exercise all four numeric tie-breakers.
        rows = []
        values = [(9, 0, 0, 0), (8, 9, 0, 0), (8, 8, 9, 0), (8, 8, 8, 9),
                  (8, 8, 8, 8), (8, 8, 8, 8), (1, 0, 0, 0), (1, 0, 0, 1),
                  (1, 0, 1, 0), (1, 1, 0, 0), (2, 0, 0, 0), (2, 0, 0, 0)]
        values.extend([(5, 5, 5, 5)] * 8)
        for i, measures in enumerate(values):
            bid = f'B{i:02d}'
            rows.append(dict(zip(('occurrence_count', 'direct_repeated_child_count',
                                  'explicit_singleton_branch_count', 'refinement_depth'), measures),
                             bundle_id=bid, unit_id='BUNDLE:' + bid, unit_type=m.BUNDLE))
        cases = m.select_cases(list(reversed(rows)), source['outcomes'], self.config)
        self.assertEqual([c['unit_id'] for c in cases[:6]], [f'BUNDLE:B{i:02d}' for i in range(6)])
        self.assertEqual([c['unit_id'] for c in cases[6:12]], [f'BUNDLE:B{i:02d}' for i in range(6, 12)])

    def test_random_selection_and_disjoint_strata(self):
        model = self.build()
        cases = model['cases']
        excluded = {c['unit_id'] for c in cases[:12]}
        pool = sorted(r['unit_id'] for r in model['population'] if r['unit_type'] == m.BUNDLE and r['unit_id'] not in excluded)
        self.assertEqual([c['unit_id'] for c in cases[12:18]], random.Random(self.config['seed']).sample(pool, 6))
        self.assertEqual(len({c['unit_id'] for c in cases[:18]}), 18)
        outcomes = sorted(r['unit_id'] for r in model['population'] if r['unit_type'] == m.SINGLETON and r['unit_id'] != 'G6:S00001')
        self.assertEqual([c['unit_id'] for c in cases[19:24]], random.Random(self.config['seed']).sample(outcomes, 5))

    def test_source_order_independence(self):
        first = self.build()
        for t in self.tables.values():
            random.Random(91).shuffle(t.rows)
        second = self.build()
        for key in ('cases', 'population', 'evidence', 'boundary', 'relations', 'overlay', 'contexts'):
            self.assertEqual(first[key], second[key], key)
        # Source row numbers legitimately change with reordered source files.
        self.assertNotEqual(first['provenance'], second['provenance'])

    def test_insufficient_populations(self):
        source = m.source_population(self.tables, self.config)
        with self.assertRaisesRegex(m.InvariantError, 'Insufficient'):
            m.select_cases(source['population'][:5], source['outcomes'], self.config)
        with self.assertRaisesRegex(m.InvariantError, 'Insufficient'):
            m.select_cases(source['population'], dict(list(source['outcomes'].items())[:5]), self.config)

    def test_blank_and_duplicate_bundle_ids(self):
        for value in ('', self.tables['members'].rows[1]['bundle_id']):
            with self.subTest(value=value):
                tables = copy.deepcopy(self.tables)
                tables['members'].rows[0]['bundle_id'] = value
                with self.assertRaisesRegex(m.InvariantError, 'blank/duplicate'):
                    m.build_model(tables, self.config, self.provider)

    def test_root_and_branching_genealogy(self):
        model = self.build()
        units = {r['unit_id']: r for r in model['population']}
        root = units['BUNDLE:B001a']
        self.assertEqual(root['parent_bundle_id'], '')
        self.assertEqual(root['direct_repeated_child_count'], 12)
        self.assertEqual(root['ancestry'], ['B001a'])
        self.assertEqual(units['BUNDLE:B001c']['ancestry'], ['B001a', 'B001c'])
        self.assertEqual(units['BUNDLE:B001c']['explicit_singleton_branch_count'], 3)

    def test_parent_mismatch_missing_parent_and_cycle(self):
        for row_index, parent, message in ((1, 'B002a', 'Cross-lineage'), (1, 'MISSING', 'Missing parent'),
                                           (0, 'B001b', 'cycle'), (1, '', 'depth/parent')):
            with self.subTest(parent=parent):
                tables = copy.deepcopy(self.tables)
                tables['members'].rows[row_index]['parent_bundle_id'] = parent
                with self.assertRaisesRegex(m.InvariantError, message):
                    m.build_model(tables, self.config, self.provider)

    def test_source_occurrence_count_mismatch(self):
        self.tables['members'].rows[0]['occurrence_count'] = '999'
        with self.assertRaisesRegex(m.InvariantError, 'occurrence count mismatch'):
            self.build()

    def test_occurrence_wrong_bundle(self):
        for bid in ('ABSENT', 'B002a'):
            with self.subTest(bid=bid):
                tables = copy.deepcopy(self.tables)
                tables['occurrences'].rows[0]['bundle_id'] = bid
                with self.assertRaises(m.InvariantError):
                    m.build_model(tables, self.config, self.provider)

    def test_all_selected_occurrences_and_no_subtree_target_expansion(self):
        model = self.build()
        packet = m.render_packet(model)
        for case in model['cases'][:18]:
            bid = case['unit_id'].removeprefix('BUNDLE:')
            expected = [r for r in self.tables['occurrences'].rows if r['bundle_id'] == bid]
            emitted = [r for r in model['evidence'] if r['case_id'] == case['case_id']]
            self.assertEqual(len(emitted), len(expected))
            self.assertEqual({r['unit_id'] for r in emitted}, {case['unit_id']})
            part = packet.split(f"## {case['case_id']} —", 1)[1].split('\n## CASE', 1)[0]
            self.assertEqual(part.count('### REPEATED_BUNDLE_UNIT'), 1)
            self.assertNotIn('### SINGLETON_OUTCOME_UNIT', part)
            self.assertEqual(part.count('- Evidence `'), len(expected))

    def test_occurrence_replacement_same_count_fails(self):
        model = self.build()
        row = next(r for r in model['evidence'] if r['unit_type'] == m.BUNDLE)
        row['bundle_id'] = 'WRONG'
        gates = {g['gate_id']: g['status'] for g in m.build_gates(model)}
        self.assertEqual(gates['NO_TARGET_OCCURRENCE_TRUNCATION'], 'FAIL')

    def test_multiverse_cross_chapter_and_book_edges(self):
        model = self.build()
        c = model['contexts']['TestBook:1:1..1:3']
        self.assertEqual(c['prev_ref'], '')
        self.assertEqual(c['next_ref'], '2:1')
        self.assertIn('1:2 ::', c['span_text'])
        crossing = model['contexts']['TestBook:1:3..2:1']
        self.assertEqual(crossing['prev_ref'], '1:2')
        self.assertEqual(crossing['next_ref'], '2:2')
        self.assertIn('sentence-cross', {s['node_id'] for s in crossing['sentences']})
        self.assertEqual(model['contexts']['TestBook:2:3..2:3']['next_ref'], '')

    def test_all_singleton_kinds_and_explicit_branches(self):
        model = self.build()
        units = {r['unit_id']: r for r in model['population']}
        o = units['G6:S00001']
        self.assertEqual(o['outcome_kind'], 'MAPPED')
        self.assertEqual(len(o['branches']), 3)  # G6 link + two event branches
        self.assertEqual({b['parent_bundle_id'] for b in o['branches']}, {'B001b', 'B001c'})
        self.assertEqual(len(o['spans']), 4)
        events = [r for r in units.values() if r.get('outcome_kind') == 'EVENT_ONLY']
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]['surface_text'], events[1]['surface_text'])
        self.assertNotEqual(events[0]['unit_id'], events[1]['unit_id'])
        self.assertEqual(units['G6:ORPHAN']['outcome_kind'], 'G6_ONLY')
        self.assertEqual(units['G6:ORPHAN']['branches'], [])

    def test_identical_surface_g6_ids_remain_distinct(self):
        for key in ('items', 'links'):
            self.tables[key].rows[1].update(surface_text='SYNTH singleton S00001', ref_start='1:1', ref_end='1:1')
        next(r for r in self.tables['events'].rows if r['mapped_g6_singleton_review_item_id'] == 'S00002').update(exemplar_ref_start='1:1', exemplar_ref_end='1:1')
        units = {r['unit_id']: r for r in self.build()['population']}
        self.assertEqual(units['G6:S00001']['surface_text'], units['G6:S00002']['surface_text'])
        self.assertNotEqual(units['G6:S00001']['source_ids'], units['G6:S00002']['source_ids'])

    def test_mapped_identity_conflicts(self):
        for field, value in (('lineage_id', 'L002'), ('sequence_length', '2'),
                             ('exemplar_start_index_1based', '999'), ('mapped_g6_singleton_review_item_id', 'ABSENT'),
                             ('exemplar_ref_start', '2:2')):
            with self.subTest(field=field):
                tables = copy.deepcopy(self.tables)
                tables['events'].rows[0][field] = value
                with self.assertRaises((m.InvariantError, m.SchemaError)):
                    m.build_model(tables, self.config, self.provider)

    def test_overlapping_singleton_spans_preserved(self):
        self.tables['events'].rows[0]['exemplar_ref_end'] = '1:2'
        model = self.build()
        o = next(r for r in model['population'] if r['unit_id'] == 'G6:S00001')
        self.assertEqual({s['ref_end'] for s in o['spans']}, {'1:1', '1:2'})
        selected = next(c for c in model['cases'] if c['unit_id'] == o['unit_id'])
        self.assertEqual(len([r for r in model['evidence'] if r['case_id'] == selected['case_id']]), 4)

    def test_s02135_historical_surface_through_job_configuration(self):
        with (ROOT / 'tests/fixtures/r3c_0_1/08_boundary_control_pattern_matches.csv').open(encoding='utf-8-sig') as f:
            historical = next(csv.DictReader(f))
        config = json.loads((ROOT / 'config/r3c_1_job_pilot.json').read_text(encoding='utf-8'))
        mapping = dict(zip(self.config['boundary_refs'], config['boundary_refs']))
        for table in self.tables.values():
            for row in table.rows:
                for k, value in list(row.items()):
                    if 'ref_start' in k or 'ref_end' in k:
                        row[k] = mapping.get(value, value)
                    if value == 'S00001':
                        row[k] = 'S02135'
                if row.get('review_item_id') == 'S02135' or row.get('mapped_g6_singleton_review_item_id') == 'S02135':
                    for k in ('surface_text', 'exemplar_surface_text'):
                        if k in row:
                            row[k] = historical['surface_text']
        provider = m.base.SpanContext('Job', [{**v, 'ref': mapping[v['ref']]} for v in self.provider.verses], self.provider.structures)
        model = m.build_model(self.tables, config, provider)
        self.assertEqual(model['cases'][18]['unit_id'], 'G6:S02135')
        self.assertTrue(all(g['status'] == 'PASS' for g in m.build_gates(model)))
        self.assertIn('### SINGLETON_OUTCOME_UNIT `G6:S02135`', m.render_packet(model))

    def test_fixed_control_missing_wrong_surface_or_span(self):
        for update in ({'review_item_id': 'ABSENT'}, {'surface_letters': 'אחר'}, {'ref_start': '1:2', 'ref_end': '1:2'}):
            with self.subTest(update=update):
                config = copy.deepcopy(self.config)
                config['singleton_control'].update(update)
                with self.assertRaisesRegex(m.InvariantError, 'control'):
                    m.build_model(self.tables, config, self.provider)

    def test_boundary_all_matching_objects(self):
        model = self.build()
        source = m.source_population(self.tables, self.config)
        for case in model['cases'][24:]:
            ref = case['boundary_ref']
            expected = {('BUNDLE:' + r['row']['bundle_id'], r['source_id']) for r in source['occurrences']
                        if m.base.contains(r['row']['ref_start'], r['row']['ref_end'], ref, self.config['book'])}
            for oid, o in source['outcomes'].items():
                if any(m.base.contains(s['ref_start'], s['ref_end'], ref, self.config['book']) for s in o['spans']):
                    expected.update((oid, s['source_id']) for s in o['spans'])
            actual = {(r['unit_id'], r['source_id']) for r in model['boundary'] if r['case_id'] == case['case_id']}
            self.assertEqual(actual, expected)
            self.assertGreater(len(actual), 1)
        self.assertFalse(any(r['unit_id'].startswith('CASE') for r in model['population']))

    def test_extension_coverage_and_direct_incidence(self):
        self.tables['overlay'].rows[0]['short_exemplar_ref_start'] = ''
        model = self.build()
        self.assertEqual({r['coverage'] for r in model['overlay']}, {'UNRESOLVED', 'EXEMPLAR_ONLY'})
        for case in model['cases'][:18]:
            for r in model['overlay']:
                if r['case_id'] == case['case_id']:
                    self.assertIn(case['unit_id'].removeprefix('BUNDLE:'), (r['short_bundle_id'], r['long_bundle_id']))
        self.assertNotIn('OCCURRENCE_VERIFIED', m.render_packet(model))

    def test_unknown_overlay_endpoint_rejected(self):
        self.tables['overlay'].rows[0]['short_bundle_id'] = 'ABSENT'
        with self.assertRaisesRegex(m.InvariantError, 'Overlay endpoint'):
            self.build()

    def test_extra_source_overlay_fields_cannot_upgrade_coverage(self):
        self.tables['overlay'].fields.extend(['coverage', 'relation_layer'])
        for row in self.tables['overlay'].rows:
            row.update(coverage='OCCURRENCE_VERIFIED', relation_layer='CORE')
        model = self.build()
        self.assertEqual({r['coverage'] for r in model['overlay']}, {'EXEMPLAR_ONLY'})
        self.assertEqual({r['relation_layer'] for r in model['overlay']}, {m.base.OVERLAY})
        self.assertTrue(all(g['status'] == 'PASS' for g in m.build_gates(model)))

    def test_review_fields_and_no_semantic_columns(self):
        model = self.build()
        for case in model['cases']:
            self.assertEqual({f: case[f] for f in m.REVIEW_FIELDS}, m.base.review_defaults())
        for row in model['population'] + model['evidence'] + model['boundary'] + model['relations']:
            self.assertFalse(set(row) & m.base.FORBIDDEN_FIELDS)
        self.assertEqual(m.render_packet(model).count('### Human review\n'), 30)

    def test_extra_source_columns_required_explicitly(self):
        for field in m.MEMBER_FIELDS:
            with self.subTest(field=field):
                tables = copy.deepcopy(self.tables)
                tables['members'].fields.remove(field)
                with self.assertRaisesRegex(m.SchemaError, field):
                    m.build_model(tables, self.config, self.provider)

    def test_configuration_schema(self):
        for change in ({'book': ''}, {'seed': '1'}, {'singleton_control': None}, {'boundary_refs': ['1:1'] * 6}):
            with self.subTest(change=change):
                with self.assertRaises(m.SchemaError):
                    m.build_model(self.tables, {**self.config, **change}, self.provider)

    def test_negative_mutation_for_every_computed_gate(self):
        model = self.build()
        def repeated(x):
            return next(r for r in x['evidence'] if r['unit_type'] == m.BUNDLE)
        def unit(x):
            return next(r for r in x['population'] if r['unit_type'] == m.BUNDLE)
        def singleton(x):
            return next(r for r in x['population'] if r['unit_id'] == 'G6:S00001')
        mutations = {
            'SOURCE_NAVIGATION_AND_COUNTS_VALID': lambda x: x['tables']['members'].rows[0].update(occurrence_count='999'),
            'REVIEW_UNIT_POPULATION_COMPLETE': lambda x: x['population'].pop(),
            'REVIEW_UNIT_IDS_UNIQUE': lambda x: x['population'].append(copy.deepcopy(x['population'][0])),
            'NO_CONTAINER_AS_REVIEW_TARGET': lambda x: x['cases'][0].update(unit_id='C001', unit_type='CONTAINER'),
            'REPEATED_UNIT_LINEAGE_MATCHES_SOURCE': lambda x: unit(x).update(lineage_id='WRONG'),
            'REPEATED_UNIT_PARENT_MATCHES_SOURCE': lambda x: unit(x).update(parent_bundle_id='WRONG'),
            'REPEATED_METADATA_COMPLETE': lambda x: unit(x).update(sequence_length=999),
            'ALL_SELECTED_BUNDLE_OCCURRENCES_EMITTED': lambda x: x['evidence'].remove(repeated(x)),
            'NO_TARGET_OCCURRENCE_TRUNCATION': lambda x: x['evidence'].remove(repeated(x)),
            'SELECTED_SINGLETON_SPANS_COMPLETE': lambda x: x['evidence'].remove(next(r for r in x['evidence'] if r['unit_type'] == m.SINGLETON)),
            'ALL_SELECTED_CONTEXTS_RESOLVED': lambda x: x['contexts'].pop(next(iter(x['contexts']))),
            'SINGLETON_IDENTITY_FOLDING_VALID': lambda x: singleton(x).update(outcome_kind='G6_ONLY'),
            'SINGLETON_PARENT_LINEAGE_MATCHES': lambda x: singleton(x)['branches'][0].update(parent_bundle_id='WRONG'),
            'S02135_REGRESSION_VALID': lambda x: x['cases'][18].update(unit_id='G6:S00002'),
            'BOUNDARY_CONTROLS_COMPLETE': lambda x: x['boundary'].pop(),
            'NO_EXTENSION_OBJECT_IN_CORE': lambda x: repeated(x).update(unit_type=m.base.OVERLAY),
            'EXTENSION_RELATIONS_OVERLAY_ONLY': lambda x: x['relations'][0].update(relation='EXTENDS'),
            'REVIEW_FIELDS_BLANK_EXCEPT_STATUS': lambda x: x['cases'][0].update(exceptions='AUTOMATIC'),
            'NO_AUTOMATIC_FUNCTION_LABELS': lambda x: unit(x).update(rhetorical_function=''),
            'PILOT_CASE_COUNTS_VALID': lambda x: x['cases'].pop(),
            'PILOT_SELECTIONS_DISJOINT_WHERE_REQUIRED': lambda x: x['cases'][6].update(unit_id=x['cases'][0]['unit_id']),
            'FIXED_SEED_SELECTION_REPRODUCIBLE': lambda x: x['cases'][12].update(seed=999),
            'RELATION_CONTEXT_COMPLETE': lambda x: x['relations'].pop(),
            'PROVENANCE_COMPLETE': lambda x: x['provenance'][0]['source_row_json'].update(tampered='yes'),
        }
        self.assertEqual(set(mutations), {g['gate_id'] for g in m.build_gates(model)})
        for gate, mutate in mutations.items():
            with self.subTest(gate=gate):
                changed = copy.deepcopy(model)
                mutate(changed)
                self.assertEqual(next(g for g in m.build_gates(changed) if g['gate_id'] == gate)['status'], 'FAIL')

    def test_overlay_dropped_and_coverage_overclaim_fail(self):
        for mutate in (lambda x: x['overlay'].pop(), lambda x: x['overlay'][0].update(coverage='OCCURRENCE_VERIFIED')):
            model = self.build()
            mutate(model)
            self.assertEqual(next(g for g in m.build_gates(model) if g['gate_id'] == 'EXTENSION_RELATIONS_OVERLAY_ONLY')['status'], 'FAIL')

    def test_output_roundtrip_provenance_manifest_and_packet(self):
        model = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            self.assertEqual(m.write_outputs(model, out, {'run_kind': 'SYNTHETIC_TEST'}), 0)
            self.assertEqual(len(list(out.iterdir())), 14)
            with (out / '99_manifest_sha256.csv').open(encoding='utf-8-sig') as f:
                manifest = list(csv.DictReader(f))
            self.assertEqual(len(manifest), 13)
            for row in manifest:
                self.assertEqual(m.base.sha256_file(out / row['file']), row['sha256'])
            with (out / '06_object_provenance.csv').open(encoding='utf-8-sig') as f:
                rows = list(csv.DictReader(f))
            self.assertTrue(all(json.loads(r['source_row_json']) for r in rows))
            meta = json.loads((out / '90_run_metadata.json').read_text())
            self.assertEqual(meta['gate_count'], 24)
            self.assertEqual(meta['exit_code'], 0)
            self.assertEqual(meta['review_unit_population_counts'], {m.BUNDLE: 82, m.SINGLETON: 27})

    def test_cli_zip_loading_failure_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            z2, z3 = m.base.write_synthetic_archives(self.tables, root)
            cfg = root / 'config.json'
            cfg.write_text(json.dumps(self.config))
            args = ['--r3b2-zip', str(z2), '--r3b3-zip', str(z3), '--tf-dir', str(root),
                    '--pilot-config', str(cfg), '--output-dir', str(root / 'output')]
            with patch.object(m, 'TFContext', return_value=self.provider), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(m.main(args), 0)
                manifest = m.base.sha256_file(root / 'output/99_manifest_sha256.csv')
                self.assertEqual(m.main(args), 2)
                self.assertEqual(manifest, m.base.sha256_file(root / 'output/99_manifest_sha256.csv'))
                self.tables['members'].rows[0]['occurrence_count'] = '999'
                m.base.write_synthetic_archives(self.tables, root)
                args[-1] = str(root / 'failure')
                self.assertEqual(m.main(args), 2)
            self.assertIn('occurrence count mismatch', (root / 'failure/00_FATAL_ERROR.txt').read_text())
            self.assertEqual(json.loads((root / 'failure/90_run_metadata.json').read_text())['exit_code'], 2)


if __name__ == '__main__':
    unittest.main()
