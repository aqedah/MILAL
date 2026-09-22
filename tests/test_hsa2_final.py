import ast
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import milal_hsa2_final as f


def change_old(m, name, field, ident, updates):
    rows = f.table(m['historical'], name)
    next(r for r in rows if r[field] == ident).update(updates)
    m['historical'][name] = f.h1.util.csv_bytes(rows)


def judgment(ident, **updates):
    return lambda m, s: change_old(m, '01_hsa2_structural_judgments.csv', 'judgment_id', ident, updates)


def final(ident, **updates):
    return lambda m, s: next(r for r in m['relations'] if r['candidate_id'] == ident).update(updates)


def receipt(token):
    return lambda m, s: next(r for r in s['frozen'] if token in r['path']) .update(actual='bad')


MUTATIONS = {
    'HSA1_FROZEN': receipt('hsa1'),
    'HSA2_HISTORY_TRACEABLE': judgment('HSA2-END-31', direct_closure_target='29:1'),
    '31_40_ENDING_RETAINED': judgment('HSA2-END-31', structural_function='NO_BOUNDARY'),
    'DIRECT_LOCAL_29': final('CT01', target_reference='27:1'),
    'NO_DIRECT_LOCAL_27': final('CT02', selected_relation='DIRECT_LOCAL_CLOSURE'),
    'HIGHER_GROUP_TERMINAL': final('CT03', selected_relation='NO_DIRECT_RELATION'),
    'LOCAL_HIGHER_INDEPENDENT': final('CT03', dimension='DIRECT_CLOSURE_TARGET'),
    '27_29_PEERS': judgment('HSA2-JOB-27', hierarchy_relation='UNRESOLVED'),
    '29_NOT_CHILD_27': judgment('HSA2-JOB-29', hierarchy_relation='CHILD_OF'),
    '27_NOT_PARENT_29': judgment('HSA2-JOB-27', hierarchy_relation='HIERARCHICALLY_ABOVE'),
    '28_NO_BOUNDARY_CONTINUES': judgment('HSA2-NO-28', structural_function='SPEECH_UNIT_ONSET'),
    'CYCLE_1_COUNT': judgment('HSA2-C1-S2', human_group='EXCLUDED'),
    'CYCLE_2_COUNT': judgment('HSA2-C2-S2', human_group='EXCLUDED'),
    'CYCLE_3_COUNT': judgment('HSA2-C3-S2', human_group='EXCLUDED'),
    'NO_ZOPHAR_III': judgment('HSA2-C3-S4', human_speaker='Zophar'),
    'NO_NEAREST_OPENING_RULE': final('CT01', authority='NEAREST_OPENING_AUTOMATIC'),
    'MR1_UNCHANGED': receipt('mr1'),
    'NO_WHOLE_BOOK_HIERARCHY': lambda m, s: m['historical'].update({'whole_book_tree.json': b'{}'}),
    'NO_UNREVIEWED_PARENTAGE': final('CT01', selected_relation='CHILD_OF', review_status='UNREVIEWED'),
    'SOURCE_CONTEXT_LINKS_VALID': lambda m, s: m['links'][0].update(row_sha256='bad'),
    'ALL_FROZEN_FILES': receipt('r4_2'),
    'HUMAN_FILE_FIDELITY': lambda m, s: m.update(markdown='rewritten'),
    'CANDIDATE_ID_RESOLUTION': final('CT01', candidate_id='CT_UNKNOWN'),
    'REPORT_FIDELITY': lambda m, s: m.update(report='invented result'),
    'DETERMINISTIC_OUTPUT': lambda m, s: m.update(nondeterministic_value='unexpected'),
}


class FinalAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = f.source(True)

    def setUp(self):
        self.s = deepcopy(self.source)
        self.m = f.build(self.s)

    def test_all_gates_and_complete_negative_coverage(self):
        gg = f.gates(self.m, self.s)
        self.assertEqual(set(MUTATIONS), {r['gate'] for r in gg})
        self.assertTrue(all(r['status'] == 'PASS' for r in gg))

    def test_manifest_negative(self):
        files = f.serialize(self.m, self.s)
        files['03_final_closure_relations.csv'] += b'bad'
        self.assertEqual(f.h1.util.manifest_gate(files)['status'], 'FAIL')

    def test_all_historical_members_preserved_byte_for_byte(self):
        files = f.serialize(self.m, self.s)
        self.assertEqual({k.removeprefix('hsa2/'): v for k, v in files.items() if k.startswith('hsa2/')}, self.s['files'])
        self.assertTrue(f.h1.util.manifest_ok(self.s['files']))

    def test_human_csv_markdown_equivalence_and_lf(self):
        self.assertEqual(f.registry_bytes(self.m['judgments']), f.CSV.read_bytes())
        self.assertNotIn(b'\r\n', f.CSV.read_bytes())
        self.assertIn(f.markdown_table(self.m['judgments']), f.MD.read_text(encoding='utf-8'))

    def test_three_separate_assertions_and_meanings(self):
        r = self.m['relations']
        self.assertEqual([(x['target_reference'], x['semantic_meaning']) for x in r],
                         [('29:1', 'DIRECT_LOCAL_CLOSURE'), ('27:1', 'NO_DIRECT_CLOSURE'),
                          ('27:1–31:40', 'HIGHER_ORDER_TERMINAL_EFFECT')])
        self.assertEqual(len({x['judgment_id'] for x in r}), 3)

    def test_original_unresolved_never_overwritten(self):
        candidates = f.table(self.m['historical'], '03_closure_target_candidate_relations.csv')
        self.assertTrue(all(r['selected_relation'] == 'UNRESOLVED' and r['review_status'] == 'UNREVIEWED' for r in candidates))
        self.assertEqual(len(self.m['links']), 15)
        self.assertEqual(sum(r['relationship'] == 'RESOLVES_HISTORICAL_CANDIDATE' for r in self.m['links']), 3)

    def test_no_parent_edge_or_extra_group_node(self):
        before = f.table(self.s['files'], '12_direct_human_relation_pairs.csv')
        after = f.table(self.m['historical'], '12_direct_human_relation_pairs.csv')
        self.assertEqual(before, after)
        self.assertEqual(len(after), 83)
        self.assertFalse(any(r['selected_relation'] in ('CHILD_OF', 'HIERARCHICALLY_ABOVE') for r in self.m['relations']))

    def test_projection_independent_of_candidate_order_and_geometry(self):
        baseline = f.relations(self.m['judgments'])
        self.s['files']['03_closure_target_candidate_relations.csv'] = f.h1.util.csv_bytes(list(reversed(f.table(self.s['files'], '03_closure_target_candidate_relations.csv'))))
        self.assertEqual(f.build(self.s)['relations'], baseline)
        # Function has no source/model argument or calls: it copies only authored fields.
        tree = ast.parse(Path(f.__file__).read_text(encoding='utf-8'))
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'relations')
        self.assertEqual([a.arg for a in node.args.args], ['rows'])
        self.assertFalse(any(isinstance(n, ast.Call) for n in ast.walk(node)))

    def test_missing_id_fails_without_fuzzy_matching(self):
        self.m['judgments'][0]['candidate_id'] = 'CT01_SIMILAR'
        with self.assertRaisesRegex(ValueError, 'missing/ambiguous exact human ID'):
            f.decision_links(self.m['judgments'], self.s)

    def test_duplicate_id_fails(self):
        name = '03_closure_target_candidate_relations.csv'
        rows = f.table(self.s['files'], name)
        self.s['files'][name] = f.h1.util.csv_bytes(rows + [rows[0]])
        with self.assertRaisesRegex(ValueError, 'missing/ambiguous exact human ID'):
            f.build(self.s)

    def test_no_source_writes(self):
        paths = [f.CSV, f.MD, f.h2.CSV, f.h2.MD, f.h1.CSV, f.h1.MD]
        before = [p.read_bytes() for p in paths]
        f.serialize(self.m, self.s)
        self.assertEqual(before, [p.read_bytes() for p in paths])

    def test_deterministic_zip_and_existing_output_rejected(self):
        a = f.serialize(self.m, self.s)
        self.assertEqual(a, f.serialize(f.build(self.s), self.s))
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp)
            f.publish(a, p/'a')
            f.publish(a, p/'b')
            self.assertEqual((p/'a_results.zip').read_bytes(), (p/'b_results.zip').read_bytes())
            with self.assertRaisesRegex(ValueError, 'output exists'):
                f.publish(a, p/'a')


def negative(name, mutation):
    def test(self):
        mutation(self.m, self.s)
        self.assertEqual(next(r['status'] for r in f.gates(self.m, self.s) if r['gate'] == name), 'FAIL')
    return test


for name, mutation in MUTATIONS.items():
    setattr(FinalAudit, 'test_negative_' + name.lower(), negative(name, mutation))


if __name__ == '__main__':
    unittest.main()
