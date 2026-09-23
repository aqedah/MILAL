from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import milal_hsa3_de_seam_adjudication as d


def hist(member):
    return lambda m, s: m['historical'].update({member: b'changed'})


def remove(m, name):
    m['actions'] = [a for a in m['actions'] if a['request_id'] != name]


MUTATIONS = {
 'BASELINE_COMMIT_VERIFIED': lambda m, s: m['commit'].update(verified_commit='wrong'),
 'ANA_0_3_FROZEN_VERIFIED': lambda m, s: m['receipt'].update(sha256='wrong'),
 'FROZEN_SOURCE_FILES': lambda m, s: s['frozen'][0].update(actual='wrong'),
 'RESEARCHER_SOURCE_EXACT': lambda m, s: s.update(human_bytes=b'bad'),
 'SEAM_D_RESEARCHER_DECISION_RECORDED': lambda m, s: m['adjudications'][0].update(status='UNREVIEWED'),
 'SEAM_E_RESEARCHER_DECISION_RECORDED': lambda m, s: m['adjudications'][1].update(researcher_supplied=False),
 'JOB_32_1_REMAINS_TRANSITION': lambda m, s: m['facts'][0]['original_record'].update(structural_function='TEXTUAL_PARENT'),
 'JOB_32_1_NOT_PARENT_OF_ELIHU': lambda m, s: remove(m, 'D1-N2'),
 'ELIHU_INTRO_RELATION_PRESENT': lambda m, s: remove(m, 'D2'),
 'ELIHU_SPEECH_SIBLINGS_PRESERVED': lambda m, s: m['actions'].pop(),
 'ELIHU_SEQUENCE_TERMINAL_37_24': lambda m, s: remove(m, 'D4'),
 'NO_DIRECT_PARENTAGE_37_24_38_1': lambda m, s: remove(m, 'E1'),
 'NO_DIRECT_RESPONSE_ANTECEDENT_37_24_38_1': lambda m, s: remove(m, 'E2'),
 'ANA_Q2_PRESERVED': lambda m, s: m['ana'][0].update(status='UNRESOLVED'),
 'ANA_Q3_STILL_UNRESOLVED': lambda m, s: m['ana'][1].update(status='ACCEPTED'),
 'ANA_Q4_PRESERVED': lambda m, s: m['ana'][2].update(relation_type='CHILD_OF'),
 'ANA_Q5_PRESERVED': lambda m, s: m['ana'][3].update(relation_type='RESPONSE_TO_GOD'),
 'OVERLAYS_NOT_DELETED_OR_PROMOTED': lambda m, s: m['overlays'].pop(),
 'NO_DUPLICATE_RELATIONS': lambda m, s: m['actions'].append(deepcopy(next(a for a in m['actions'] if a['action'] == 'CREATED'))),
 'RELATION_ACTIONS_EXACT': lambda m, s: m['actions'][0].update(canonical_relation_id='invented'),
 'NEGATIVE_CONSTRAINTS_EXPLICIT': lambda m, s: m['negative'][0].update(negative_authority='AUTOMATIC_ABSENCE_OF_EVIDENCE'),
 'NO_ADJACENCY_PARENTAGE': lambda m, s: m['actions'][0].update(basis='ADJACENCY_ONLY'),
 'NO_FORMULA_LENGTH_RULE': lambda m, s: m['actions'][0].update(basis='FORMULA_LENGTH'),
 'OTHER_SEAMS_UNCHANGED': lambda m, s: m['remaining'][0].update(review_status='ACCEPTED'),
 'HSA2_F_INTEGRITY': hist(d.EDGES),
 'HISTORICAL_ARTIFACTS_UNCHANGED': hist(d.NODES),
 'UNRESOLVED_CROSSWALK_FAITHFUL': lambda m, s: m['crosswalk'][0].update(status='RESOLVED_BY_SEAM_D', direct_parent_resolved=True),
 'DEPENDENCIES_Q3_NOT_RESOLVED': lambda m, s: m['dependencies'][-1].update(resolves_q3=True),
 'NO_NEW_COMPOSITION_PARENT': lambda m, s: m['groups_created'].append('ELIHU_INTERVENTION_COMPLEX'),
 'NO_CAUSAL_OR_FULFILLMENT': lambda m, s: m.update(report='38:1 fulfills 31:35'),
 'SOURCE_FACTS_EXACT': lambda m, s: m['facts'][2].update(source_row_sha256='fuzzy'),
 'INTEGRITY_RECEIPTS_COMPUTED': lambda m, s: m['integrity'][0].update(actual_sha256='wrong'),
 'NO_R4_4': lambda m, s: m.update(r44_started=True),
 'NO_NEW_LEXICAL_ANALYSIS': lambda m, s: m['lexical_scans'].append('new BHSA scan'),
 'REMAINING_PACKET_FAITHFUL': lambda m, s: m.update(packet='SEAM_F accepted'),
 'DETERMINISTIC_RERUN': lambda m, s: m.update(rerun_digest='wrong'),
}


class SeamTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = d.load(self_test=True)
        cls.m = d.build(cls.s)
        cls.files = d.serialize(cls.m, cls.s)

    def gate(self, model, name):
        return next(g['status'] for g in d.gates(model, self.s) if g['gate'] == name)

    def test_all_positive_and_negative_coverage(self):
        gg = d.gates(self.m, self.s)
        self.assertEqual({g['gate'] for g in gg}, set(MUTATIONS))
        self.assertTrue(all(g['status'] == 'PASS' for g in gg))

    def test_manifest_negative(self):
        files = dict(self.files)
        files['05_hsa3_de_negative_constraints.csv'] += b'changed'
        self.assertFalse(d.util.manifest_ok(files))

    def test_baseline_commit_authorized(self):
        self.assertEqual(self.s['commit']['verified_commit'], '60b6a5a0cdb2e8e8dde55ae2210774f58c84eb24')
        self.assertTrue(self.s['commit']['is_ancestor'])

    def test_actual_counts_are_computed_after_audit(self):
        c = d.counts(self.m)
        self.assertEqual((c['researcher_seam_decisions'], c['new_positive_relations'], c['confirmed_existing_relations'], c['new_negative_constraints'], c['duplicate_skipped_relations']), (2, 1, 18, 4, 0))
        self.assertNotIn('new_positive_relations', self.s['cfg']['expected'])

    def test_intro_reuses_exact_existing_id(self):
        a = next(a for a in self.m['actions'] if a['request_id'] == 'D2')
        self.assertEqual(a['action'], 'CONFIRMED_EXISTING')
        self.assertEqual(a['canonical_relation_id'], a['existing_record']['edge_id'])
        self.assertEqual(a['relation_type'], 'NARRATIVE_INTRODUCTION')
        self.assertEqual(a['assertion_scope'], 'UNIT_COMPOSITION_NOT_VERSE_PARENTAGE')

    def test_existing_terminal_is_confirmed_not_recreated(self):
        s = deepcopy(self.s)
        edges = d.rows(s['files'][d.EDGES])
        edges.append(dict(edge_id='EXISTING-TERMINAL', source_node='H:HSA024', target_node='ELIHU_SPEECH_SEQUENCE', relation_type='TERMINATES_ENCLOSING_GROUP', dimension='HIGHER_ORDER_TERMINAL_EFFECT'))
        s['files'][d.EDGES] = d.util.csv_bytes(edges)
        aa = d.relation_actions(s)
        terminal = next(a for a in aa if a['request_id'] == 'D4')
        self.assertEqual(terminal['action'], 'CONFIRMED_EXISTING')
        self.assertEqual(terminal['canonical_relation_id'], 'EXISTING-TERMINAL')
        self.assertFalse(any(a['action'] == 'CREATED' for a in aa))

    def test_explicit_intro_alias_does_not_duplicate(self):
        s = deepcopy(self.s)
        s['human']['requests'][2]['relation_type'] = 'INTRODUCES_AND_ENCLOSES'
        a = next(a for a in d.relation_actions(s) if a['request_id'] == 'D2')
        self.assertEqual(a['action'], 'CONFIRMED_EXISTING')

    def test_duplicate_request_logged_without_second_creation(self):
        s = deepcopy(self.s)
        duplicate = deepcopy(s['human']['requests'][3])
        duplicate['request_id'] = 'D4-REPEATED'
        s['human']['requests'].append(duplicate)
        aa = d.relation_actions(s)
        dup = next(a for a in aa if a['request_id'] == 'D4-REPEATED')
        self.assertEqual(dup['action'], 'NO_ACTION_DUPLICATE')
        self.assertEqual(sum(a['action'] == 'CREATED' for a in aa), 1)

    def test_ambiguous_existing_semantic_relation_stops(self):
        s = deepcopy(self.s)
        edges = d.rows(s['files'][d.EDGES])
        intro = deepcopy(next(e for e in edges if e['relation_type'] == 'NARRATIVE_INTRODUCTION'))
        intro['edge_id'] = 'DIFFERENT-ID-SAME-RELATION'
        edges.append(intro)
        s['files'][d.EDGES] = d.util.csv_bytes(edges)
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            d.relation_actions(s)

    def test_no_extra_group(self):
        self.assertEqual(self.m['groups_created'], [])
        self.assertEqual(self.m['scope']['scope_ref'], '32:6–37:24')

    def test_32_1_not_parent_of_intro(self):
        self.assertTrue(any(a['source_node'] == 'H:HSA018' and a['target_node'] == 'H:HSA019' and a['relation_type'] == 'NO_DIRECT_PARENTAGE' for a in self.m['negative']))

    def test_32_1_not_parent_of_sequence(self):
        self.assertTrue(any(a['source_node'] == 'H:HSA018' and a['target_node'] == 'ELIHU_SPEECH_SEQUENCE' for a in self.m['negative']))

    def test_all_twelve_historical_directed_siblings_confirmed(self):
        aa = [a for a in self.m['actions'] if a['relation_type'] == 'SAME_LEVEL_SIBLING']
        self.assertEqual(len(aa), 12)
        self.assertTrue(all(a['action'] == 'CONFIRMED_EXISTING' for a in aa))

    def test_four_membership_edges_preserved(self):
        aa = [a for a in self.m['actions'] if a['relation_type'] == 'GROUP_MEMBER_OF']
        self.assertEqual({a['source_node'] for a in aa}, set(self.s['human']['preserve']['onsets']))

    def test_terminal_is_group_not_local_closure(self):
        a = self.m['positive'][0]
        self.assertEqual((a['source_node'], a['target_node'], a['relation_type']), ('H:HSA024', 'ELIHU_SPEECH_SEQUENCE', 'TERMINATES_ENCLOSING_GROUP'))
        self.assertFalse(a['textual_parentage_created'])

    def test_dimension_specific_human_negative_not_absence(self):
        for a in self.m['negative']:
            self.assertEqual(a['negative_authority'], 'EXPLICIT_HUMAN_NEGATIVE_CONSTRAINT_NOT_AUTOMATIC_ABSENCE_OF_EVIDENCE')
        self.assertEqual({a['dimension'] for a in self.m['negative']}, {'TEXTUAL_PARENTAGE', 'RESPONSE_RELATION'})

    def test_negative_parentage_does_not_delete_overlays(self):
        self.assertEqual([r['review_question_id'] for r in self.m['overlays']], ['ANA-Q2', 'ANA-Q4', 'ANA-Q5'])
        self.assertIn('NO RHETORICAL/DISCOURSE RELATION', self.m['report'])

    def test_q3_still_deferred_not_accepted(self):
        q = self.m['ana'][1]
        self.assertEqual((q['status'], q['decision_type']), ('UNRESOLVED', 'HUMAN_DEFERRED'))
        self.assertFalse(q['accepted_relation_created'])
        deps = [r for r in self.m['dependencies'] if r['review_question_id'] == 'ANA-Q3']
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0]['role'], 'UNRESOLVED_CANDIDATE_EVIDENCE_ONLY')

    def test_all_57_crosswalk_rows_keep_exact_parent_unresolved(self):
        self.assertEqual(len(self.m['crosswalk']), 57)
        self.assertTrue(all(r['direct_parent_after'] == 'UNRESOLVED' and not r['direct_parent_resolved'] for r in self.m['crosswalk']))
        c = d.counts(self.m)
        self.assertEqual((c['resolved_by_de'], c['de_relevant_still_unresolved'], c['not_applicable'], c['all_still_unresolved'], c['remaining_seam_primary_rows']), (0, 9, 48, 57, 49))

    def test_shared_38_1_still_owned_by_f(self):
        row = next(r for r in self.m['crosswalk'] if r['node_id'] == 'H:HSA025')
        self.assertEqual(row['primary_seam'], 'SEAM_F')
        self.assertEqual(row['status'], 'REMAINS_UNRESOLVED')
        self.assertEqual([r['seam_id'] for r in self.m['adjudications']], ['SEAM_D', 'SEAM_E'])

    def test_no_other_seam_adjudication_and_blank_fields(self):
        self.assertEqual([c['case_id'] for c in self.m['remaining']], ['SEAM_A', 'SEAM_B', 'SEAM_C', 'SEAM_F', 'SEAM_G'])
        for c in self.m['remaining']:
            for key in d.REVIEW_FIELDS:
                self.assertEqual(c[key], 'UNREVIEWED' if key == 'review_status' else '')

    def test_remaining_packet_contains_exact_questions_and_constraints(self):
        for c in self.m['remaining']:
            self.assertIn(c['question'], self.m['packet'])
            for ident in c['positive_constraint_ids'] + c['negative_constraint_ids']:
                self.assertIn(ident, self.m['packet'])

    def test_no_formula_length_basis(self):
        self.assertTrue(all(a['basis'] == 'EXPLICIT_RESEARCHER_DECISION' for a in self.m['actions']))
        self.assertIn('N-FORMULA-LENGTH-ONLY', {r['evidence_code'] for r in self.m['criteria']})

    def test_no_bhsa_loader_for_stage(self):
        from unittest.mock import patch
        with patch.object(d.h.f.a, 'native_bhsa', side_effect=AssertionError('no new lexical scan')):
            m = d.build(self.s)
        self.assertEqual(m['lexical_scans'], [])

    def test_all_frozen_files_and_nested_manifests(self):
        self.assertTrue(all(v['valid'] for v in d.h.nested_manifests(self.files)))
        for k, v in self.s['files'].items():
            self.assertEqual(self.files[d.HISTORY+k], v)

    def test_exact_source_row_links(self):
        for key in ('actions', 'adjudications', 'criteria', 'crosswalk', 'dependencies', 'facts'):
            for link in self.m[key]:
                if not link.get('source_member'):
                    continue
                data = self.files[link['source_member']]
                row = d.h.raw_rows(data)[int(link['source_data_row'])-1]
                self.assertEqual(d.sha(data), link['source_member_sha256'])
                self.assertEqual(d.h.f.rowhash(row), link['source_row_sha256'])
                self.assertEqual(row[link['source_identity_field']], link['source_identity'])

    def test_bad_baseline_sha_stops(self):
        with self.assertRaisesRegex(ValueError, 'SHA'):
            d.audit(self.s['files'], self.s['cfg'], 'wrong')

    def test_bad_baseline_manifest_stops(self):
        ff = dict(self.s['files'])
        ff[d.ANA] += b'corrupt'
        with self.assertRaisesRegex(ValueError, 'manifest'):
            d.audit(ff, self.s['cfg'], 'wrong', True)

    def test_missing_identity_stops_not_fuzzy(self):
        with self.assertRaisesRegex(ValueError, 'exact identity'):
            d.locate(self.s, d.NODES, 'node_id', '32:2-similar')

    def test_required_field_is_not_guessed(self):
        s = deepcopy(self.s)
        rr = d.rows(s['files'][d.UNRESOLVED])
        del rr[0]['direct_parent']
        s['files'][d.UNRESOLVED] = d.util.csv_bytes(rr)
        with self.assertRaisesRegex(ValueError, 'schema'):
            d.resolution_crosswalk(s, self.m['actions'])

    def test_bad_model_not_published(self):
        m = deepcopy(self.m)
        m['ana'][1]['status'] = 'ACCEPTED'
        with self.assertRaisesRegex(ValueError, 'FAIL'):
            d.serialize(m, self.s)

    def test_independent_process_zip_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            zz = []
            for name in ('first', 'second'):
                out = Path(temp)/name
                result = subprocess.run([sys.executable, str(d.ROOT/'src/milal_hsa3_de_seam_adjudication.py'), '--self-test', '--out', str(out)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                zz.append(out.with_name(name+'_results.zip').read_bytes())
            self.assertEqual(zz[0], zz[1])


def negative(name, mutation):
    def test(self):
        m, s = deepcopy(self.m), deepcopy(self.s)
        mutation(m, s)
        self.assertEqual(next(g['status'] for g in d.gates(m, s) if g['gate'] == name), 'FAIL')
    return test


for name, mutation in MUTATIONS.items():
    setattr(SeamTests, 'test_negative_' + name.lower(), negative(name, mutation))


def forbidden_relation(relation, source, target):
    def test(self):
        m = deepcopy(self.m)
        bad = deepcopy(m['actions'][0])
        bad.update(relation_type=relation, source_node=source, target_node=target, textual_parentage_created=relation == 'CHILD_OF')
        m['actions'].append(bad)
        self.assertEqual(self.gate(m, 'NO_ADJACENCY_PARENTAGE'), 'FAIL')
    return test


for rel in ('CHILD_OF', 'CONTINUES_WITHIN', 'RESPONSE_TO'):
    setattr(SeamTests, 'test_forbidden_37_24_38_1_' + rel.lower(), forbidden_relation(rel, 'H:HSA024', 'H:HSA025'))
for target in ('H:HSA018', 'H:HSA019'):
    setattr(SeamTests, 'test_no_32_6_child_of_' + target.replace(':','_'), forbidden_relation('CHILD_OF', 'H:HSA020', target))


if __name__ == '__main__':
    unittest.main()
