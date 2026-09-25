"""Executable source distinctions, candidate alternatives and structural negatives."""
import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from milal_mfr02r_grammar import load_registry, match_rules
from milal_mfr02r_features import build_features, preceding_sets, pair_facts, evidence_values
from milal_mfr02r_graph import validate_variant, analyze_graph
from milal_mfr02r_revision import RevisionHistory, verify_history, secondary_semantic_candidate
from milal_mfr02r_engine import run_engine
from milal_mfr02r_data import verify_manifest, rows
from milal_mfr_observation import observe
from milal_mfr02r_synthetic import clause, sample






class GrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(ROOT / 'config/clause_relation_grammar_v1.json')

    def features(self, raw=None, edges=()):
        return build_features(raw or sample(), self.registry, edges)

    def test_source_separation(self):
        adopted = [r for r in self.registry['rules'] if r['adoption'] == 'DIRECTLY_ADOPTED']
        self.assertEqual(len(adopted), 24)
        self.assertTrue(all(r['implementation_schema_adoption'] == 'GENERALIZED_FOR_MILAL' for r in adopted))
        self.assertTrue(all(not r['enabled'] for r in self.registry['rules'] if r['adoption'] == 'UNKNOWN_NOT_VERIFIED'))

    def test_unverified_rule_rejected(self):
        config = copy.deepcopy(self.registry)
        config['rules'][0]['source_reference']['jin_section'] = 'UNKNOWN_NOT_VERIFIED'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'rules.json'; path.write_text(json.dumps(config))
            with self.assertRaisesRegex(ValueError, 'unverified'):
                load_registry(path)

    def test_type_only_never_decides(self):
        fs = self.features()
        self.assertEqual(match_rules(fs[0], fs[2], {}, self.registry), [])

    def test_same_type_hypotaxis_and_parataxis_compete(self):
        a, b = self.features()[:2]
        matched = match_rules(a, b, pair_facts(a, b), self.registry)
        self.assertEqual({m['relation'] for m in matched}, {'HYPOTACTIC', 'PARATACTIC'})
        self.assertTrue({'JIN', 'WALTON'} <= {m['source_author'] for m in matched})

    def test_walton_secondary_participant_negative(self):
        a, b = self.features(observe([clause(1, subject='A/', complement='B/'), clause(2, subject='C/', complement='D/')]))
        self.assertNotIn('W-H01', [m['rule_id'] for m in match_rules(a, b, pair_facts(a, b), self.registry)])

    def test_explicit_subordination_and_alternative_mothers(self):
        raw = observe([clause(1), clause(2), clause(3, typ='Ptcp', subordinate=True, subject=None)])
        fs = self.features(raw, [dict(dependent_node=3, head_node=1, rela='Adju')])
        sets = list(preceding_sets(fs))
        self.assertEqual(set(sets[-1][1]), {1, 2})
        for source in fs[:2]:
            matched = match_rules(source, fs[2], pair_facts(source, fs[2]), self.registry)
            self.assertIn('HYPOTACTIC', {m['relation'] for m in matched})

    def test_native_identity_not_fuzzy(self):
        fs = self.features(sample(), [dict(dependent_node=5, head_node=999999999, rela='Adju')])
        self.assertEqual(fs[4]['native_preceding'], [])
        self.assertEqual(fs[4]['native_raw'][0]['resolution'], 'OUTSIDE_PROJECTION')

    def test_long_distance_and_book_boundary(self):
        raw = [clause(1)] + [clause(i, subject='X%d/' % i, complement=None, verb='V%d[' % i, typ='NmCl') for i in range(2, 40)]
        raw.append(clause(40, book='Another'))
        fs = self.features(observe(raw))
        admitted = list(preceding_sets(fs))[-1][1]
        self.assertIn(1, admitted)
        self.assertIn('PARTICIPANT_REINTRODUCTION_INDEX', admitted[1])
        self.assertEqual(fs[-1]['participant_mentions'][0]['participant_status'], 'REINTRODUCED')

    def test_participant_new_continued_reintroduced_absent(self):
        fs = self.features(observe([clause(1), clause(2), clause(3, subject='C/', complement='D/'), clause(4)]))
        self.assertEqual(fs[0]['participant_mentions'][0]['participant_status'], 'NEW')
        self.assertEqual(fs[1]['participant_mentions'][0]['participant_status'], 'CONTINUED')
        self.assertEqual(fs[3]['participant_mentions'][0]['participant_status'], 'REINTRODUCED')
        self.assertIn('A/', fs[2]['absent_participant_lexemes'])
        self.assertTrue(all(m['identity_status'] == 'UNRESOLVED' for f in fs for m in f['participant_mentions']))

    def test_time_location_change_not_boundary(self):
        a, b = self.features()[:2]
        facts = pair_facts(a, b)
        self.assertTrue(facts['time_contrast'] and facts['location_contrast'])
        self.assertNotIn('boundary', facts)
        ev = evidence_values(b)
        self.assertEqual(ev['TIME']['temporal_change'], 'PAIRWISE_MATRIX')
        self.assertEqual(ev['LOCATION']['locative_change'], 'PAIRWISE_MATRIX')

    def test_wayhi_core_not_every_way0(self):
        fs = self.features(observe([clause(1, typ='Way0', time='JWM/'), clause(2, typ='Way0', verb='HJH[', time='JWM/')]))
        self.assertNotIn('Wayhi+Time', fs[0]['types'])
        self.assertIn('Wayhi+Time', fs[1]['types'])

    def test_wayhi_relation_changes_with_context(self):
        raw = observe([clause(1, verb='HJH[', time='JWM/'),
                       clause(2, typ='Way0', verb='HJH[', subject=None, time='CNH/')])
        a, b = self.features(raw)
        relations = {r['relation'] for r in match_rules(a, b, pair_facts(a, b), self.registry)}
        self.assertEqual(relations, {'HYPOTACTIC', 'PARATACTIC'})
        different = self.features(observe([clause(1, subject='X/', complement='Y/', verb='OTHER['),
            clause(2, typ='Way0', verb='HJH[', subject=None, complement='Z/', time='CNH/')]))
        self.assertNotIn('PARATACTIC', {r['relation'] for r in match_rules(*different, pair_facts(*different), self.registry)})

    def test_infinitival_and_implicit_reference_hypotaxis(self):
        raw = observe([clause(1), clause(2, typ='InfC', subordinate=True, subject=None), clause(3, typ='Way0', subject=None)])
        fs = self.features(raw, [dict(dependent_node=2, head_node=1, rela='Cmpl')])
        self.assertIn('RG-A01', {r['rule_id'] for r in match_rules(fs[0], fs[1], pair_facts(fs[0], fs[1]), self.registry)})
        a, b = self.features(observe([clause(1), clause(2, typ='Way0', subject=None)]))
        self.assertIn('RG-B01', {r['rule_id'] for r in match_rules(a, b, pair_facts(a, b), self.registry)})

    def test_one_mother_only_in_selected_variant(self):
        es = [dict(edge_id='a', source=1, target=3, relation='HYPOTACTIC'), dict(edge_id='b', source=2, target=3, relation='HYPOTACTIC')]
        graph = analyze_graph(es, {1: 0, 2: 1, 3: 2})
        self.assertEqual(len(graph['components'][0]['alternative_edge_ids']), 2)
        self.assertIn('MULTIPLE_SELECTED_MOTHERS', validate_variant(es))
        self.assertEqual(validate_variant(es[:1]), [])
        self.assertEqual(len(graph['variants']), 3)

    def test_parallel_cycle_after_contraction(self):
        es = [dict(source=1, target=2, relation='HYPOTACTIC'), dict(source=2, target=3, relation='HYPOTACTIC'), dict(source=1, target=3, relation='PARATACTIC')]
        self.assertIn('CYCLE_AFTER_PARALLEL_CONTRACTION', validate_variant(es))
        self.assertEqual(validate_variant(es[:2]), [])

    def test_all_parallel_and_embedded_variants(self):
        para = [dict(source=1, target=2, relation='PARATACTIC'), dict(source=1, target=3, relation='PARATACTIC')]
        embedded = [dict(source=1, target=2, relation='HYPOTACTIC'), para[1]]
        self.assertEqual(validate_variant(para), [])
        self.assertEqual(validate_variant(embedded), [])

    def test_symbolic_preserves_every_option(self):
        es = [dict(edge_id=str(i), source=i, target=99, relation='HYPOTACTIC') for i in range(1, 9)]
        graph = analyze_graph(es, {**{i: i for i in range(1, 9)}, 99: 99})
        self.assertEqual(graph['components'][0]['representation'], 'SYMBOLIC_VARIANT_COMPONENT')
        self.assertEqual(len(graph['components'][0]['alternative_edge_ids']), 8)
        self.assertEqual(graph['variants'], [])

    def test_append_only_revision_and_tamper(self):
        history = RevisionHistory(); history.initialize('p', ['PARATACTIC'], 2, ['rule'])
        original = copy.deepcopy(history.rows)
        history.reconsider('p', [{'source_nodes': [3]}], 3, ['HYPOTACTIC'])
        self.assertEqual(history.rows[:2], original)
        self.assertEqual(history.rows[-1]['status'], 'REVISED_RELATION')
        self.assertTrue(verify_history(history.rows))
        changed = copy.deepcopy(history.rows); changed[0]['trigger_clause'] = 99
        self.assertFalse(verify_history(changed))

    def test_semantic_secondary_only(self):
        ev = dict(source_author='WALTON', source_section='2.1.2.3', source_page=19, concept='fixture', source_node_ids=[1])
        with self.assertRaises(ValueError):
            secondary_semantic_candidate(1, 2, ev, False)
        self.assertEqual(secondary_semantic_candidate(1, 2, ev, True)['accepted_mother'], '')

    def test_synthetic_engine_outputs_and_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            summary = run_engine(sample(), self.registry, [], out)
            self.assertEqual(summary['clauses'], 7)
            self.assertGreater(summary['MULTIPLE'], 0)
            self.assertTrue(verify_manifest(out))
            self.assertTrue(all(not r['accepted_mother'] for r in rows(out / '10_relation_candidates.csv')))
            self.assertTrue(verify_history(list(rows(out / 'relation_revision_history.csv'))))


if __name__ == '__main__':
    unittest.main()
