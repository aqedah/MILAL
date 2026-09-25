"""Bosman integration: layers, conditional units and retained human rejections."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from test_mfr02r_grammar import ROOT, clause, sample
from milal_mfr_observation import observe
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_features import build_features, pair_facts
from milal_mfr02r_layers import (unit_candidates, unit_reference_evidence, context_query,
    poetic_observation, labels_for, decision_learning_row, program_human_state)
from milal_mfr02r_engine import run_engine
from milal_mfr02r_data import rows, verify_manifest
from milal_mfr02r_graph import validate_variant


class BosmanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = load_registry(ROOT / 'config/clause_relation_grammar_v1.json')
        cls.labels = json.loads((ROOT / 'config/mfr_0_2r_evidence_labels.json').read_text())

    def hidden(self):
        raw = [clause(1, subject='X/', complement=None, verb=None),
               clause(2, subject='A/', complement='B/'), clause(3, subject=None, complement='Z/', suffix=True)]
        # Source opening has no PNG-compatible verb/subject. The explicit
        # synthetic unit member does. Identities remain unresolved in both.
        raw[0]['words'][0].update(ps=None, gn=None, nu=None)
        fs = build_features(observe(raw), self.registry)
        edges = [dict(edge_id='a', source=1, target=2, relation='HYPOTACTIC'),
                 dict(edge_id='b', source=1, target=3, relation='HYPOTACTIC')]
        return fs, edges

    def test_b_s1_hidden_reference(self):
        fs, edges = self.hidden(); units = unit_candidates(edges, fs)
        evidence = list(unit_reference_evidence(units, fs, edges))
        row = next(r for r in evidence if r['source_clause_id'] == 1 and r['target_clause_id'] == 3)
        self.assertFalse(row['direct_reference_match'])
        self.assertTrue(row['unit_internal_reference_match'])
        self.assertEqual(row['antecedent_clause_id'], 2)
        self.assertEqual(row['required_selected_path'], ['a'])

    def test_factorized_reference_sets_expand_exactly(self):
        from milal_mfr02r_layers import symbolic_unit_references, expand_unit_reference
        fs, edges = self.hidden()
        flat = list(unit_reference_evidence(unit_candidates(edges, fs), fs, edges))
        units = unit_candidates(edges, fs, compact=True)
        lookup = {u['unit_id']: u for u in units}
        records = list(symbolic_unit_references(units, fs))
        expanded = [r for record in records for r in expand_unit_reference(record, lookup[record['source_unit_candidate_id']], fs, edges)]
        order = lambda r: (r['source_clause_id'], r['target_clause_id'], r['antecedent_clause_id'])
        self.assertEqual(sorted(flat, key=order), sorted(expanded, key=order))
        self.assertEqual(sum(r['antecedent_target_pair_count'] for r in records), len(flat))
        changed = copy.deepcopy(records[0]); changed['target_clause_ids'] = []
        self.assertFalse(list(expand_unit_reference(changed, lookup[changed['source_unit_candidate_id']], fs, edges)))

    def test_factorized_reachability_keeps_every_path(self):
        from milal_mfr02r_layers import symbolic_unit_references, expand_unit_reference
        fs = build_features(observe([clause(i, subject='A/' if i > 1 else 'X/', complement=None, verb=None if i == 1 else '>MR[', suffix=i==5) for i in range(1,6)]), self.registry)
        edges = [dict(edge_id=str(i), source=a, target=b, relation='HYPOTACTIC') for i,(a,b) in enumerate([(1,2),(1,3),(2,4),(3,4)])]
        compact = unit_candidates(edges, fs, compact=True)
        ordinary = unit_candidates(edges, fs)
        for c, o in zip(compact, ordinary):
            bits = int(c['member_clause_selector']['membership_bitset_hex'],16)
            self.assertEqual([f['clause_id'] for f in fs if bits & (1 << f['position'])], o['member_clauses'])
        with self.assertRaisesRegex(ValueError, 'DAG'):
            unit_candidates(edges + [dict(edge_id='bad',source=4,target=1,relation='HYPOTACTIC')], fs, compact=True)

    def test_factorized_query_resolves_from_artifact_alone(self):
        from milal_mfr02r_layers import symbolic_unit_references
        from milal_mfr02r_query import resolve
        from milal_mfr02r_data import table, manifest
        fs, edges = self.hidden()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'
            run_engine([f['row'] for f in fs], self.registry, [], out)
            units = unit_candidates(edges, fs, compact=True)
            table(out / '12_provisional_relation_graph.csv', edges)
            table(out / 'textual_unit_candidates.csv', units)
            table(out / 'participant_unit_reference_evidence.csv', symbolic_unit_references(units, fs))
            manifest(out)
            result = list(resolve(out, 1, 3, self.registry))
            self.assertEqual(result[0]['antecedent_clause_id'], 2)
            self.assertEqual(result[0]['required_selected_path'], ['a'])
            self.assertEqual(list(resolve(out, 1, 999, self.registry)), [])

    def test_b_s2_candidate_survives_without_direct_match(self):
        fs, edges = self.hidden()
        result = list(unit_reference_evidence(unit_candidates(edges, fs), fs, edges))
        self.assertTrue(any(r['candidate_status'] == 'UNIT_CONTEXT_REFERENCE_CANDIDATE' for r in result))
        self.assertTrue(all(r['reference_identity_status'] == 'UNRESOLVED' for r in result))

    def test_b_s3_reference_does_not_replace_mother(self):
        fs, edges = self.hidden(); original = copy.deepcopy(edges)
        result = list(unit_reference_evidence(unit_candidates(edges, fs), fs, edges))
        self.assertEqual(edges, original)
        self.assertTrue(all(not r['syntactic_mother'] for r in result))
        self.assertEqual(validate_variant(edges), [])

    def test_b_s4_poetic_and_syntax_edges_differ(self):
        fs = build_features(observe([clause(1), clause(2), clause(3)]), self.registry)
        p = poetic_observation(fs[0], fs[2], pair_facts(fs[0], fs[2]), self.labels)
        self.assertEqual(p['layer'], 'POETIC_PROSODIC_LAYER')
        self.assertFalse(p['syntactic_override'])
        self.assertTrue(p['labels'])

    def test_b_s5_boundary_not_hierarchy_break(self):
        fs = build_features(observe([clause(1), clause(2)]), self.registry)
        annotations = dict(verified_source_sha256='synthetic-fixture-only', clause_units={1: 'a', 2: 'b'})
        p = poetic_observation(*fs, pair_facts(*fs), self.labels, annotations)
        self.assertEqual(p['poetic_boundary'], 'CROSSES_POETIC_UNIT_BOUNDARY')
        self.assertFalse(p['syntactic_override'])
        self.assertEqual(p['canonical_boundary'], '')

    def test_b_s6_multi_category_provenance(self):
        result = labels_for(dict(lexical_continuity=True, formal_correspondence=True), self.labels, 2)
        self.assertTrue({'LEXICAL_LABELS', 'POETIC_PROSODIC_LABELS'} <= {r['category'] for r in result})
        self.assertTrue(all(r['source_author'] == 'BOSMAN' for r in result))
        self.assertTrue(all(r['source_work'] == self.labels['source_work'] and r['source_page_if_verified'] for r in result))

    def test_b_s7_rejected_proposal_retained(self):
        row = decision_learning_row(dict(program_proposed=True, candidate_relation='HYPOTACTIC', rule_ids=['x']),
            dict(event_id='synthetic', reviewer='fixture', rationale='fixture rejection', source_sha256='fixture', decision='REJECTED'))
        self.assertTrue(row['candidate_retained'])
        self.assertEqual(row['final_status'], 'PROGRAM_PROPOSED_HUMAN_REJECTED')
        self.assertEqual(row['rule_ids'], ['x'])

    def test_b_s8_human_unproposed_acceptance(self):
        self.assertEqual(program_human_state(False, 'ACCEPTED'), 'PROGRAM_NOT_PROPOSED_HUMAN_ACCEPTED')

    def test_b_s9_learning_keeps_both_rejection_states(self):
        for proposed in (True, False):
            result = decision_learning_row(dict(program_proposed=proposed, candidate_relation='PARATACTIC'),
                dict(event_id='synthetic', reviewer='fixture', rationale='fixture', source_sha256='fixture', decision='REJECTED'))
            self.assertTrue(result['candidate_retained'])
            self.assertFalse(result['model_training_performed'])

    def test_b_s10_no_acrostic_rule(self):
        self.assertFalse(any('ACROSTIC' in r['label_id'] for r in self.labels['labels']))

    def test_b_s11_no_invented_poetic_boundary(self):
        fs = build_features(observe([clause(1), clause(2)]), self.registry)
        p = poetic_observation(*fs, pair_facts(*fs), self.labels)
        self.assertEqual(p['poetic_boundary'], 'UNKNOWN_POETIC_BOUNDARY')
        self.assertEqual(p['boundary_status'], 'PROSODIC_NOT_AVAILABLE')
        with self.assertRaises(ValueError):
            poetic_observation(*fs, pair_facts(*fs), self.labels, dict(clause_units={1: 1, 2: 2}))

    def test_b_s12_wider_context_is_source_linked(self):
        fs, edges = self.hidden(); units = unit_candidates(edges, fs)
        context = context_query(1, 3, fs, units)
        self.assertEqual(context['intervening_clauses'], [2])
        self.assertEqual(context['source_containing_unit'], ['UC-1'])

    def test_labels_extend_without_core_edits(self):
        labels = copy.deepcopy(self.labels)
        new = copy.deepcopy(labels['labels'][0]); new['label_id'] = 'RESEARCHER_ADDED_LABEL'
        labels['labels'].append(new)
        result = labels_for(dict(same_clause_type=True), labels, 1)
        self.assertIn('RESEARCHER_ADDED_LABEL', {r['label_id'] for r in result})

    def test_pass1_never_loads_poetic_labels(self):
        result = labels_for(dict(sequence_correspondence=True, lexical_continuity=True, formal_correspondence=True), self.labels, 1)
        self.assertNotIn('POETIC_PROSODIC_LABELS', {r['category'] for r in result})

    def test_synthetic_multilayer_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'run'
            run_engine(sample(), self.registry, [], out, label_definitions=self.labels)
            self.assertTrue(verify_manifest(out))
            layers = {r['layer'] for r in rows(out / 'relation_multilayer_edges.csv')}
            self.assertEqual(layers, {'TEXTUAL_SYNTACTIC_LAYER', 'PARTICIPANT_REFERENCE_LAYER', 'POETIC_PROSODIC_LAYER'})
            self.assertTrue(all(not r['human_decision'] for r in rows(out / 'program_human_decision_matrix.csv')))
            self.assertTrue((out / 'pass1_freeze.json').is_file())


if __name__ == '__main__':
    unittest.main()
