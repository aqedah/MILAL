"""Release guard negatives and stage-wide serialization/integration checks."""
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest
import zipfile
from test_mfr02r_grammar import ROOT, clause, sample
from milal_mfr_observation import observe
from milal_mfr02r_grammar import load_registry, match_rules
from milal_mfr02r_features import build_features, pair_facts
from milal_mfr02r_layers import poetic_observation
from milal_mfr02r_data import table, rows, manifest, verify_manifest, pack
import milal_mfr02r_data as data
from milal_mfr02r_gates import evaluate
from milal_mfr02r_review import revalidation_rows


class ValidationTests(unittest.TestCase):
    def test_static_control_reference_leakage(self):
        modules = ('engine', 'features', 'grammar', 'graph', 'layers', 'valency', 'revision')
        for name in modules:
            text = (ROOT / 'src' / ('milal_mfr02r_' + name + '.py')).read_text(encoding='utf8')
            # Inspect string constants, not slicing notation or schema section numbers.
            strings = [n.value for n in ast.walk(ast.parse(text)) if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            self.assertFalse(any(re.search(r'\b(?:Job|Iob|Numeri|Leviticus|Qohelet|Threni|Jesaia)\s+\d', s) for s in strings), name)
            self.assertFalse(any(re.search(r'(?<!\d)(?:1:6|1:13|2:1|27:1|29:1|31:40|42:7)(?!\d)', s) for s in strings), name)

    def test_different_type_parataxis_context_required(self):
        registry = load_registry(ROOT / 'config/clause_relation_grammar_v1.json')
        features = build_features(observe([clause(1, typ='Way0'), clause(2, typ='WayX')]), registry)
        result = match_rules(*features, pair_facts(*features), registry)
        self.assertIn('RG-E03', {r['rule_id'] for r in result})
        self.assertNotIn('RG-E03', {r['rule_id'] for r in match_rules(*features, {}, registry)})

    def test_poetry_exception_is_candidate_only(self):
        registry = load_registry(ROOT / 'config/clause_relation_grammar_v1.json')
        labels = json.loads((ROOT / 'config/mfr_0_2r_evidence_labels.json').read_text())
        features = build_features(sample(), registry)
        facts = pair_facts(features[0], features[1])
        facts.update(sequence_correspondence=True, embedded_reference=True)
        result = poetic_observation(features[0], features[1], facts, labels)
        self.assertEqual(result['exception_status'], 'POETRY_AWARE_EXCEPTION_CANDIDATE')
        self.assertFalse(result['syntactic_override'])

    def test_binding_precedes_grammar_in_engine(self):
        code = (ROOT / 'src/milal_mfr02r_engine.py').read_text(encoding='utf8')
        tree = ast.parse(code)
        calls = [(n.lineno, getattr(n.func, 'id', '')) for n in ast.walk(tree) if isinstance(n, ast.Call)]
        order = {name: min(line for line, called in calls if called == name) for name in ('internal_bindings', 'preceding_sets', 'match_rules')}
        self.assertLess(order['internal_bindings'], order['preceding_sets'])
        self.assertLess(order['preceding_sets'], order['match_rules'])

    def test_provisional_h1_never_overwritten(self):
        old = dict(decision_id='FIXTURE', researcher_decision='PARATACTIC', source_clause_ids=[1], target_clause_ids=[3])
        original = copy.deepcopy(old)
        result = list(revalidation_rows([old], {3: [1, 2]}, {(1, 3): dict(relations=['HYPOTACTIC'], status='HYPOTACTIC')}))[0]
        self.assertEqual(old, original)
        self.assertEqual(result['original_decision'], original)
        self.assertEqual(result['current_human_decision'], 'PARATACTIC')
        self.assertEqual(result['revised_human_decision'], '')

    def test_compressed_storage_and_archive_manifest(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'out'; out.mkdir()
            previous = data.COMPACT_TABLES; data.COMPACT_TABLES = True
            try:
                table(out / 'scope/one.csv', [dict(id=1, values=['a', 'b'])])
                manifest(out / 'scope'); manifest(out)
            finally:
                data.COMPACT_TABLES = previous
            self.assertEqual(next(rows(out / 'scope/one.csv'))['values'], ['a', 'b'])
            self.assertTrue(verify_manifest(out))
            destination = Path(tmp) / 'out.zip'; pack(out, destination)
            with zipfile.ZipFile(destination) as archive:
                self.assertIn('scope/one.csv.gz', archive.namelist())
                self.assertNotIn('scope/one.csv', archive.namelist())
                self.assertEqual(archive.read('scope/99_manifest_sha256.csv'), (out / 'scope/99_manifest_sha256.csv').read_bytes())
                from milal_mfr02r_data import zip_rows
                for prefix in ('', 'scope/'):
                    for record in zip_rows(archive, prefix + '99_manifest_sha256.csv'):
                        self.assertEqual(hashlib.sha256(archive.read(prefix + record['path'])).hexdigest(), record['sha256'])
                # Packaging must preserve every frozen byte identity, not merely
                # produce a different internally consistent manifest universe.
                for p in out.rglob('*'):
                    if p.is_file():
                        self.assertEqual(archive.read(p.relative_to(out).as_posix()), p.read_bytes())

    def test_missing_gate_evidence_is_failure(self):
        self.assertTrue(all(not r['passed'] for r in evaluate({})))

    def test_control_preserves_non_onset_clause_alternatives(self):
        from milal_mfr02r_controls import reference, triple_variants
        inventory = [dict(clause_id=i, book='Fixture', chapter=1, verse=7, position=i) for i in (1,2)]
        self.assertEqual([r['clause_id'] for r in reference(inventory, 'Fixture', 1, 7)], [1,2])
        lookup = {(2,3):dict(pair_id='p23', rule_ids=['fixture'], relations=['HYPOTACTIC','PARATACTIC']),
                  (2,4):dict(pair_id='p24', rule_ids=['fixture'], relations=['PARATACTIC'])}
        result = list(triple_variants(lookup, [[1,2],[3],[4]]))
        self.assertEqual(len(result),4)
        self.assertEqual({tuple(r['exact_clause_ids']) for r in result}, {(1,3,4),(2,3,4)})
        self.assertEqual(sum(r['representable'] for r in result),2)
        lookup[2,3]['relations'] = ['PARATACTIC']
        self.assertEqual(sum(r['representable'] for r in triple_variants(lookup, [[1,2],[3],[4]])),1)

    def test_crossbook_admission_is_not_relation_support(self):
        from milal_mfr02r_controls import crossbook_relation_count
        records = [dict(source_clause_id=1,target_clause_id=2,relations=[])]
        self.assertEqual(crossbook_relation_count(records,{1:'A',2:'B'}),0)
        records[0]['relations'] = ['HYPOTACTIC']
        self.assertEqual(crossbook_relation_count(records,{1:'A',2:'B'}),1)
        self.assertEqual(crossbook_relation_count(records,{1:'A',2:'A'}),0)

    def test_historical_rows_checked_against_loaded_source_hashes(self):
        from milal_mfr02r_gates import historical_preservation
        from milal_mfr02r_data import encode
        original = [dict(decision_id='A', decision='PARATACTIC'), dict(decision_id='B',decision='FORMAL_ONLY')]
        expected = dict(original_decision_hashes={r['decision_id']:hashlib.sha256(encode(r).encode()).hexdigest() for r in original})
        revised = [dict(decision_id=r['decision_id'], original_decision=r) for r in original]
        self.assertTrue(historical_preservation(original,revised,expected))
        self.assertFalse(historical_preservation(original[:1],revised[:1],expected))
        self.assertFalse(historical_preservation(original,[revised[0],revised[0]],expected))
        altered = copy.deepcopy(original); altered[0]['decision']='HYPOTACTIC'
        self.assertFalse(historical_preservation(altered,[dict(decision_id=r['decision_id'],original_decision=r) for r in altered],expected))

    def test_single_candidate_multiple_relations_is_reviewable(self):
        from milal_mfr02r_review import select_review_targets
        receipts={2:dict(hierarchy_candidate_count=1)}; inventory={2:dict(frame_candidate=False)}
        self.assertEqual(select_review_targets(receipts,inventory,set(),set(),{2}),{2})
        self.assertEqual(select_review_targets(receipts,inventory,set(),set(),set()),set())

    def test_compact_matrix_is_logically_identical(self):
        from milal_mfr02r_engine import run_engine
        registry = load_registry(ROOT / 'config/clause_relation_grammar_v1.json')
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / 'plain', Path(tmp) / 'compact'
            previous = data.COMPACT_TABLES
            try:
                data.COMPACT_TABLES = False
                run_engine(sample(), registry, [], a)
                data.COMPACT_TABLES = True
                run_engine(sample(), registry, [], b)
            finally:
                data.COMPACT_TABLES = previous
            for name in ('07_preceding_candidate_sets.csv', '08_relation_rule_matches.csv', '09_candidate_evidence_matrix.csv', '10_relation_candidates.csv', '12_provisional_relation_graph.csv'):
                self.assertEqual(list(rows(a / name)), list(rows(b / name)), name)


def negative_gate_test(name):
    def test(self):
        names = json.loads((ROOT / 'config/mfr_0_2r_required_gates.json').read_text())['gates']
        measured = {n: True for n in names}
        self.assertTrue(next(r['passed'] for r in evaluate(measured) if r['gate'] == name))
        # A violated measured invariant must never be rescued by other passing
        # invariants. Semantic/data mutations are exercised in the companion suites.
        measured[name] = False
        result = evaluate(measured)
        self.assertFalse(next(r['passed'] for r in result if r['gate'] == name))
        self.assertEqual(sum(not r['passed'] for r in result), 1)
    return test


for gate in json.loads((ROOT / 'config/mfr_0_2r_required_gates.json').read_text())['gates']:
    setattr(ValidationTests, 'test_negative_gate_' + gate, negative_gate_test(gate))


if __name__ == '__main__':
    unittest.main()
