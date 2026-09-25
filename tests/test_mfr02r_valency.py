"""Valency, corpus comparison and secondary textual-tradition invariants."""
import copy
import unittest
from test_mfr02r_grammar import clause
from milal_mfr_observation import observe
from milal_mfr02r_valency import (construction, internal_bindings, atom_relation_status,
    corpus_index, analogues, behavior_variation, tradition_evidence, recursive_patterns)


class ValencyTests(unittest.TestCase):
    def split(self, vocative=False):
        a = clause(1); b = clause(2, subject='INT/', complement=None)
        first, last = a['word_ids'][:2], a['word_ids'][2:]
        remap = {last[0]: 301}
        a['words'][-1]['node'] = 301
        a['word_ids'][-1] = 301
        a['phrases'][-1]['word_ids'] = [301]
        a['atoms'] = [dict(node=10001, word_ids=first, typ='WayX'), dict(node=10002, word_ids=[301], typ='Ellp')]
        a['clause_atom_ids'] = [10001, 10002]
        if vocative:
            b['phrases'][0]['function'] = 'Voct'
        obs = observe([a, b]); cs = [construction(r) for r in obs]
        return obs, cs, list(internal_bindings(obs, cs))

    def test_o_s1_vocative_interruption(self):
        _, _, bindings = self.split(True)
        self.assertIn('VOCATIVE_INTERRUPTION', bindings[0]['binding_evidence']['reasons'])
        self.assertIn('VALENCY_COMPLETION', bindings[0]['binding_evidence']['reasons'])

    def test_o_s2_inserted_clause_deferred(self):
        _, _, bindings = self.split()
        self.assertIn('INSERTED_CLAUSE_INTERRUPTION', bindings[0]['binding_evidence']['reasons'])
        self.assertEqual(atom_relation_status(10001, 10002, bindings), 'RELATION_DEFERRED_PENDING_CLAUSE_BINDING')

    def test_o_s3_distinct_valency_same_clause_type(self):
        a, b = clause(1), clause(2)
        b['phrases'][-1]['function'] = 'Loca'
        aa, bb = [construction(r) for r in observe([a, b])]
        self.assertEqual(aa['clause_type'], bb['clause_type'])
        self.assertNotEqual(aa['valency_signature_id'], bb['valency_signature_id'])

    def test_o_s4_crossbook_analogue(self):
        cs = [construction(r) for r in observe([clause(1), clause(2, book='Other')])]
        result = list(analogues(cs[:1], corpus_index(cs), 'FIRST_BOOK', 'TWO_BOOKS'))[0]
        self.assertEqual(result['analogue_status'], 'EXACT_ANALOGUE')
        self.assertEqual(result['exact_analogues'][0]['book'], 'Other')

    def test_o_s5_analogue_not_hierarchy(self):
        cs = [construction(r) for r in observe([clause(1), clause(2)])]
        self.assertTrue(all(not r['accepted_relation'] for r in analogues(cs, corpus_index(cs), 'A', 'A')))

    def test_o_s6_no_analogue_not_impossible(self):
        cs = [construction(r) for r in observe([clause(1)])]
        r = list(analogues(cs, corpus_index(cs), 'A', 'A'))[0]
        self.assertEqual(r['analogue_status'], 'NO_ANALOGUE_FOUND')
        self.assertEqual(r['regularity_status'], 'NO_CORPUS_SUPPORT_FOUND')
        self.assertEqual(r['accepted_relation'], '')

    def test_nominal_predicate_is_source_phrase_grounded(self):
        raw = clause(1, typ='NmCl', verb=None, complement='PRED/')
        raw['phrases'][-1]['function'] = 'PreC'
        c = construction(observe([raw])[0])
        self.assertEqual(c['valency_signature']['predicate_lexeme'], ['PRED/'])
        self.assertEqual(c['predicate'][0]['source_phrase_nodes'], [raw['phrases'][-1]['node']])
        self.assertEqual(c['valency_signature']['stem'], ['NOT_APPLICABLE'])

    def test_missing_predicates_do_not_create_corpus_analogy(self):
        cs = [construction(r) for r in observe([clause(1,typ='NmCl',verb=None,subject='A/',complement=None),
                                               clause(2,typ='NmCl',verb=None,subject='B/',complement=None)])]
        self.assertEqual(cs[0]['valency_signature']['predicate_observation'], 'NOT_AVAILABLE')
        self.assertEqual(dict(corpus_index(cs)['predicate']), {})
        self.assertTrue(all(r['analogue_status']=='NO_ANALOGUE_FOUND' for r in analogues(cs,corpus_index(cs),'A','A')))

    def test_stale_comparison_index_rejected_by_source_identity(self):
        from milal_mfr02r_valency import validate_comparison_index
        cs = [construction(r) for r in observe([clause(1)])]
        index = corpus_index(cs)
        validate_comparison_index(cs,index)
        changed = copy.deepcopy(cs); changed[0]['valency_signature_id'] = 'incompatible'
        with self.assertRaisesRegex(ValueError,'incompatible'):
            validate_comparison_index(changed,index)
        duplicate = copy.deepcopy(index)
        bucket = next(iter(duplicate['exact'].values())); bucket.append(bucket[0])
        with self.assertRaisesRegex(ValueError,'identity'):
            validate_comparison_index(cs,duplicate)

    def test_o_s7_accent_conflict_secondary(self):
        row = observe([clause(1)])[0]
        result = tradition_evidence(row, assessment='CONFLICTS_WITH_CURRENT_ANALYSIS')
        self.assertFalse(result['automatic_boundary'])
        self.assertEqual(result['evidence_stage'], 'SECONDARY_AFTER_LINGUISTIC_ANALYSIS')

    def test_o_s8_tiebreaker_needs_alternatives(self):
        row = observe([clause(1)])[0]
        self.assertFalse(tradition_evidence(row, plausible_analyses=['A'])['display_as_tiebreaker'])
        self.assertTrue(tradition_evidence(row, plausible_analyses=['A', 'B'])['display_as_tiebreaker'])

    def test_o_s9_participant_use_separate(self):
        from milal_mfr02r_valency import participant_use
        row = construction(observe([clause(1)])[0])
        self.assertEqual(row['participant_use_type'], 'RELATION_EVIDENCE')
        self.assertNotIn('DISCOURSE_INTERPRETATION', row.values())
        later = dict(hierarchy_freeze_sha256='fixture-hierarchy', reviewer='fixture-reviewer', source_sha256='fixture-source', interpretation='fixture-explicit-human-observation')
        both = participant_use(row, later)
        self.assertEqual(both['participant_use_type'], 'BOTH')
        self.assertEqual(row['participant_use_type'], 'RELATION_EVIDENCE')
        with self.assertRaisesRegex(ValueError, 'provenance'):
            participant_use(row, dict(interpretation='unattributed'))

    def test_o_s10_raw_atom_not_independent(self):
        _, constructions, bindings = self.split()
        self.assertEqual(constructions[0]['clause_atom_ids'], [10001, 10002])
        self.assertEqual(atom_relation_status(10001, 10002, bindings), 'RELATION_DEFERRED_PENDING_CLAUSE_BINDING')
        self.assertFalse(bindings[0]['automatic_atom_merge'])

    def test_o_s11_same_form_different_behavior(self):
        cs = [construction(r) for r in observe([clause(1), clause(2)])]
        result = list(behavior_variation(cs, {1: {'HYPOTACTIC'}, 2: {'PARATACTIC'}}))
        self.assertEqual(result[0]['status'], 'CORPUS_BEHAVIOR_VARIATION')
        self.assertFalse(result[0]['hierarchy_generalization'])

    def test_o_s12_no_emendation(self):
        row = observe([clause(1)])[0]; original = copy.deepcopy(row)
        result = tradition_evidence(row, qere={row['word_ids'][0]: 'ALTERNATIVE'}, text_status='TEXT_CRITICAL_ISSUE_FLAGGED')
        self.assertEqual(row, original)
        self.assertEqual(result['textual_tradition'][0]['analysis_form'], row['words'][0]['g_word_utf8'])
        self.assertEqual(result['textual_tradition'][0]['qere_form'], 'ALTERNATIVE')
        self.assertFalse(result['automatic_emendation'])

    def test_participial_inner_potential_preserved(self):
        raw = clause(1)
        raw['words'][-1].update(sp='verb', vt='ptca', vs='qal')
        row = observe([raw])[0]
        result = list(recursive_patterns([row]))
        self.assertEqual(result[0]['inner_verbal_potential'], 'PARTICIPLE_VERBAL_POTENTIAL')
        self.assertFalse(result[0]['accepted_containment'])


if __name__ == '__main__':
    unittest.main()
