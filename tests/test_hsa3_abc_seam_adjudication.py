from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import milal_hsa3_abc_seam_adjudication as a


def hist(member):
    return lambda m, s: m['historical'].update({member: b'changed'})


def drop_relation(m, typ):
    m['actions'] = [r for r in m['actions'] if r['relation_type'] != typ]


def extra(m, source, target, typ):
    m['actions'].append(dict(action='CREATED', object_kind='RELATION', source_node=source, target_node=target,
        relation_type=typ, dimension='PARENTAGE_CONTAINMENT', membership_position=9))


MUTATIONS = {
 'BASELINE_COMMIT_VERIFIED': lambda m, s: m['commit'].update(verified_commit='wrong'),
 'PRIOR_DE_SEAMS_FROZEN': hist(a.DE),
 **{seam + '_RESEARCHER_DECISION_RECORDED': (lambda m, s, i=i: m['adjudications'][i].update(status='UNREVIEWED')) for i, seam in enumerate(a.ABC)},
 'FRIENDS_ARRIVAL_SEPARATE_FROM_TEST_2': lambda m, s: drop_relation(m, 'NOT_WITHIN_SECOND_TESTING_SCENE'),
 'FRIENDS_ARRIVAL_PARENT_UNRESOLVED': lambda m, s: next(r for r in m['crosswalk'] if r['node_id'] == 'H:HSA012').update(direct_parent='H:HSA009'),
 'OPENING_NARRATIVE_GROUP_NON_TEXTUAL': lambda m, s: m['groups'][0].update(textual_parent=True),
 'INITIAL_JOB_SPEECH_NOT_CYCLE1': lambda m, s: extra(m, 'H:HSA013', 'CYCLE_1', 'GROUP_MEMBER_OF'),
 'CYCLE1_STARTS_4_1': lambda m, s: next(r for r in m['facts'] if r['node_id'] == 'H:HSA2-C1-S1')['original_record'].update(reference_start='3:1'),
 'THREE_CYCLE_PATTERN_PRESERVED': lambda m, s: m['actions'].remove(next(r for r in m['actions'] if r['target_node'] == 'CYCLE_2' and r['relation_type'] == 'GROUP_MEMBER_OF')),
 'NO_SYNTHETIC_ZOPHAR_III': lambda m, s: extra(m, 'invented_Zophar_III', 'CYCLE_3', 'GROUP_MEMBER_OF'),
 'POST_DIALOGUE_JOB_DISTINCT_FROM_CYCLE3': lambda m, s: extra(m, 'POST_DIALOGUE_JOB', 'CYCLE_3', 'CHILD_OF'),
 'NO_CYCLE4_AT_27_1': lambda m, s: extra(m, 'H:HSA015', 'CYCLE_4', 'CYCLE_ONSET_OF'),
 'DISPUTE_COMPLEX_PRESENT': lambda m, s: m['groups'][1].update(span_start='2:11'),
 'DISPUTE_COMPLEX_NON_TEXTUAL': lambda m, s: extra(m, 'H:HSA013', a.DISPUTE, 'CHILD_OF'),
 'DISPUTE_COMPLEX_ORDERED_MEMBERS_CORRECT': lambda m, s: m['groups'][1]['members'].reverse(),
 'JOB_2_11_NOT_ATTACHED_TO_DISPUTE_COMPLEX': lambda m, s: extra(m, 'H:HSA012', a.DISPUTE, 'GROUP_MEMBER_OF'),
 'NO_2_11_42_9_FRAME_ADJUDICATION': lambda m, s: m['participant_frame_adjudications'].append('accepted'),
 'HSA2_F_INTEGRITY': hist(a.EDGES),
 'ANA_INTEGRITY': hist(a.ANA),
 'DE_INTEGRITY': hist('05_hsa3_de_negative_constraints.csv'),
 'FG_UNCHANGED': lambda m, s: m['remaining'][0].update(review_status='ACCEPTED'),
 'NO_DUPLICATE_RELATIONS': lambda m, s: m['actions'].append(deepcopy(next(r for r in m['actions'] if r['action'] == 'CREATED'))),
 'NO_R4_4': lambda m, s: m.update(r44_started=True),
 'FROZEN_SOURCE_FILES': lambda m, s: s['frozen'][0].update(actual='wrong'),
 'RESEARCHER_SOURCE_EXACT': lambda m, s: s.update(human_bytes=b'bad'),
 'SOURCE_FACTS_EXACT': lambda m, s: m['facts'][0].update(source_row_sha256='wrong'),
 'RELATION_ACTIONS_EXACT': lambda m, s: m['actions'][0].update(canonical_relation_id='invented'),
 'NEGATIVE_CONSTRAINTS_EXACT': lambda m, s: m['negative'][0].update(authority='AUTOMATIC_ABSENCE'),
 'CRITERIA_CANONICAL': lambda m, s: m['criteria'][0].update(evidence_code='INVENTED'),
 'CROSSWALK_FAITHFUL': lambda m, s: m['crosswalk'][0].update(status='RESOLVED_BY_SEAM_A'),
 'HISTORICAL_ARTIFACTS_UNCHANGED': hist(a.NODES),
 'INTEGRITY_RECEIPTS_COMPUTED': lambda m, s: m['integrity'][0].update(actual_sha256='wrong'),
 'NO_NEW_LEXICAL_ANALYSIS': lambda m, s: m['lexical_scans'].append('BHSA scan'),
 'REPORT_FAITHFUL': lambda m, s: m.update(report='All textual parents resolved'),
 'REMAINING_PACKET_FAITHFUL': lambda m, s: m.update(packet='F/G ACCEPTED'),
 'DETERMINISTIC_RERUN': lambda m, s: m.update(rerun_digest='wrong'),
}


class ABCTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = a.load(True)
        cls.m = a.build(cls.s)
        cls.files = a.serialize(cls.m, cls.s)

    def test_gate_mutation_coverage(self):
        self.assertEqual(set(MUTATIONS), {g['gate'] for g in a.gates(self.m, self.s)})

    def test_all_gates_pass(self):
        self.assertTrue(all(r['status'] == 'PASS' for r in a.rows(self.files['10_gates.csv'])))

    def test_manifest_mutation(self):
        damaged = dict(self.files)
        damaged['03_hsa3_abc_composition_groups.csv'] += b'corruption'
        self.assertFalse(a.util.manifest_ok(damaged))

    def test_independent_model_and_serialization(self):
        self.assertEqual(self.files, a.serialize(a.build(deepcopy(self.s)), deepcopy(self.s)))

    def test_all_original_members_are_byte_identical(self):
        self.assertEqual(self.s['files'], {k[len(a.HISTORY):]: v for k, v in self.files.items() if k.startswith(a.HISTORY)})

    def test_exact_source_links(self):
        for field in ('facts', 'crosswalk', 'criteria', 'adjudications'):
            for r in self.m[field]:
                data = self.files[r['source_member']]
                original = a.d.h.raw_rows(data)[r['source_data_row'] - 1]
                self.assertEqual(original[r['source_identity_field']], r['source_identity'])
                self.assertEqual(a.sha(data), r['source_member_sha256'])
                self.assertEqual(a.d.h.f.rowhash(original), r['source_row_sha256'])

    def test_no_parent_was_supplied(self):
        self.assertTrue(all(r['direct_parent'] == 'UNRESOLVED' and not r['direct_parent_resolved'] for r in self.m['crosswalk']))
        self.assertTrue(all(not r['textual_parentage_created'] for r in self.m['actions']))

    def test_three_one_dual_historical_functions(self):
        record = next(r['original_record'] for r in self.m['facts'] if r['node_id'] == 'H:HSA013')
        self.assertEqual(set(record['all_historical_functions']), {'PARAGRAPH_ONSET', 'SPEECH_UNIT_ONSET'})
        self.assertEqual(self.m['annotations'][1]['node_id'], 'H:HSA013')

    def test_three_one_three_two_relations_retained(self):
        triples = {(r['source_node'], r['target_node'], r['relation_type']) for r in self.m['actions']}
        self.assertIn(('H:HSA013', 'H:HSA014', 'HIERARCHICALLY_ABOVE'), triples)
        self.assertIn(('H:HSA014', 'H:HSA013', 'CONTINUES_WITHIN'), triples)

    def test_hsa2f_three_relations(self):
        triples = {(r['source_node'], r['target_node'], r['relation_type']) for r in self.m['actions']}
        for target, typ in [('H:HSA016', 'DIRECT_LOCAL_CLOSURE'), ('H:HSA015', 'NO_DIRECT_RELATION'), ('POST_DIALOGUE_JOB', 'TERMINATES_ENCLOSING_GROUP')]:
            self.assertIn(('H:HSA017', target, typ), triples)

    def test_opening_order_and_spans(self):
        g = self.m['groups'][0]
        self.assertEqual(g['members'], ['HUMAN_SCOPE_1_1_5', 'H:HSA002', 'HUMAN_SCOPE_2_1_10', 'H:HSA012'])
        self.assertEqual((g['span_start'], g['span_end']), ('1:1', '2:13'))

    def test_no_new_sequence_type(self):
        self.assertEqual({r['relation_type'] for r in self.m['actions'] if r['action'] == 'CREATED'}, {'GROUP_MEMBER_OF'})

    def test_exact_group_collision_stops(self):
        s = deepcopy(self.s)
        nn = a.rows(s['files'][a.NODES])
        nn.append(dict(nn[0], node_id=a.OPENING))
        s['files'][a.NODES] = a.util.csv_bytes(nn)
        with self.assertRaisesRegex(ValueError, 'collision'):
            a.group_records(s)

    def test_missing_exact_member_stops(self):
        s = deepcopy(self.s)
        s['human']['groups'][0]['members'][0] = 'similar_but_not_exact'
        with self.assertRaisesRegex(ValueError, 'missing exact member'):
            a.group_records(s)

    def test_equivalent_group_requires_explicit_mapping(self):
        s = deepcopy(self.s)
        ee = a.rows(s['files'][a.EDGES])
        for i, n in enumerate(s['human']['groups'][0]['members'], 1):
            ee.append(dict(ee[0], source_node=n, target_node='CYCLE_1', relation_type='GROUP_MEMBER_OF', membership_position=i))
        ee = [e for e in ee if e['target_node'] != 'CYCLE_1' or e['source_node'] in s['human']['groups'][0]['members']]
        s['files'][a.EDGES] = a.util.csv_bytes(ee)
        with self.assertRaisesRegex(ValueError, 'canonical-ID mapping'):
            a.group_records(s)

    def test_unknown_criteria_stops(self):
        s = deepcopy(self.s)
        s['human']['criteria']['SEAM_A'].append('GUESS')
        with self.assertRaisesRegex(ValueError, 'unknown criteria'):
            a.criteria(s)

    def test_fg_packet_exact_questions_and_blank_fields(self):
        for c in self.m['remaining']:
            self.assertIn(c['question'], self.m['packet'])
            for field in a.REVIEW_FIELDS:
                self.assertEqual(c[field], 'UNREVIEWED' if field == 'review_status' else '')
                self.assertIn(f'| {field} | {c[field]} |', self.m['packet'])

    def test_no_human_review_fields_generated(self):
        for r in self.m['adjudications']:
            self.assertFalse(set(a.REVIEW_FIELDS) & set(r))

    def test_source_hash_corruption_rejected(self):
        cfg = deepcopy(self.s['cfg'])
        with self.assertRaisesRegex(ValueError, 'SHA/count'):
            a.audit(self.s['files'], cfg, 'wrong', False)

    def test_upstream_failed_gate_rejected(self):
        files = deepcopy(self.s['files'])
        gg = a.rows(files['10_gates.csv']); gg[0]['status'] = 'FAIL'
        files['10_gates.csv'] = a.util.csv_bytes(gg)
        files.pop('99_manifest_sha256.csv')
        files['99_manifest_sha256.csv'] = a.util.csv_bytes([dict(file=k, sha256=a.sha(v)) for k, v in sorted(files.items())])
        with self.assertRaisesRegex(ValueError, 'D/E gates'):
            a.audit(files, self.s['cfg'], self.s['receipt']['sha256'], True)

    def test_relevant_and_outside_counts(self):
        c = a.counts(self.m)
        self.assertEqual(c['crosswalk'], {'REMAINS_UNRESOLVED': 43, 'NOT_APPLICABLE_TO_APPROVED_DECISION': 14})
        self.assertEqual((c['new_groups'], c['new_positive_relations'], c['new_negative_constraints']), (2, 7, 6))

    def test_opening_accepted_relations(self):
        triples = {(r['source_node'], r['target_node'], r['relation_type']) for r in self.m['actions']}
        for src, tgt, typ in [('H:HSA001', 'HUMAN_SCOPE_1_1_5', 'CONTINUES_WITHIN'),
                             ('H:HSA002', 'H:HSA009', 'SAME_LEVEL_SIBLING'),
                             ('H:HSA003', 'H:HSA002', 'CHILD_OF'),
                             ('H:HSA008', 'H:HSA011', 'PARALLEL_ENDING')]:
            self.assertIn((src, tgt, typ), triples)
        for ident in ('H:HSA004', 'H:HSA005', 'H:HSA006', 'H:HSA007'):
            self.assertIn((ident, 'H:HSA003', 'CONTINUES_WITHIN'), triples)
        for ident in ('H:HSA008', 'H:HSA011'):
            self.assertFalse(any(src == ident and typ == 'DIRECT_LOCAL_CLOSURE' for src, tgt, typ in triples))

    def test_post_dialogue_sibling_and_no_boundary(self):
        triples = {(r['source_node'], r['target_node'], r['relation_type']) for r in self.m['actions']}
        self.assertIn(('H:HSA015', 'H:HSA016', 'SAME_LEVEL_SIBLING'), triples)
        self.assertIn(('H:HSA2-NO-28', 'H:HSA2-NO-28', 'NO_BOUNDARY'), triples)
        self.assertIn(('H:HSA2-NO-28', 'H:HSA015', 'CONTINUES_WITHIN'), triples)

    def test_all_forbidden_arrival_parents_rejected(self):
        for target in ('H:HSA001', 'H:HSA009', 'H:HSA013', a.OPENING):
            with self.subTest(target=target):
                m = deepcopy(self.m)
                extra(m, 'H:HSA012', target, 'CHILD_OF')
                self.assertEqual(next(g['status'] for g in a.gates(m, self.s) if g['gate'] == 'FRIENDS_ARRIVAL_PARENT_UNRESOLVED'), 'FAIL')

    def test_initial_cycle_parentage_both_directions_rejected(self):
        for src, tgt in [('H:HSA013', 'H:HSA2-C1-S1'), ('H:HSA2-C1-S1', 'H:HSA013')]:
            m = deepcopy(self.m); extra(m, src, tgt, 'CHILD_OF')
            self.assertEqual(next(g['status'] for g in a.gates(m, self.s) if g['gate'] == 'INITIAL_JOB_SPEECH_NOT_CYCLE1'), 'FAIL')

    def test_duplicate_request_is_skipped(self):
        s = deepcopy(self.s)
        s['human']['negative_constraints'].append(deepcopy(s['human']['negative_constraints'][0]))
        aa = a.actions(s, a.group_records(s))
        self.assertEqual(sum(r['action'] == 'NO_ACTION_DUPLICATE' for r in aa), 1)

    def test_existing_relation_reuses_identity(self):
        s = deepcopy(self.s)
        rr = a.rows(s['files'][a.EDGES])
        r = dict(rr[0], **{k: v for k, v in s['human']['negative_constraints'][0].items() if k != 'seam_id'}, edge_id='EXACT_EXISTING_NEGATIVE')
        rr.append(r); s['files'][a.EDGES] = a.util.csv_bytes(rr)
        hit = [x for x in a.actions(s, a.group_records(s)) if x['canonical_relation_id'] == 'EXACT_EXISTING_NEGATIVE']
        self.assertEqual(len(hit), 1)
        self.assertEqual(hit[0]['action'], 'CONFIRMED_EXISTING')

    def test_dimension_rename_does_not_hide_duplicate(self):
        m = deepcopy(self.m)
        r = deepcopy(next(r for r in m['actions'] if r['action'] == 'CREATED'))
        r['dimension'] = 'RENAMED'; m['actions'].append(r)
        self.assertEqual(next(g['status'] for g in a.gates(m, self.s) if g['gate'] == 'NO_DUPLICATE_RELATIONS'), 'FAIL')

    def test_ana_decisions_preserved(self):
        aa = {r['review_question_id']: r for r in a.rows(self.files[a.HISTORY + a.ANA])}
        self.assertEqual(aa['ANA-Q3']['status'], 'UNRESOLVED')
        for q in ('ANA-Q2', 'ANA-Q4', 'ANA-Q5'):
            self.assertEqual(aa[q]['status'], 'ACCEPTED')


def negative_test(name, mutation):
    def run(self):
        m, s = deepcopy(self.m), deepcopy(self.s)
        mutation(m, s)
        gg = {g['gate']: g['status'] for g in a.gates(m, s)}
        self.assertEqual(gg[name], 'FAIL', name)
        with self.assertRaises(ValueError):
            a.serialize(m, s)
    return run


for name, mutation in MUTATIONS.items():
    setattr(ABCTests, 'test_negative_' + name.lower(), negative_test(name, mutation))


if __name__ == '__main__':
    unittest.main()
