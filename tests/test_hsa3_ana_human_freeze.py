from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
import milal_hsa3_ana_human_freeze as h


def history(member):
    return lambda m, s: m['historical'].update({member: b'changed'})


MUTATIONS = {
    'VERIFIED_BASELINE': lambda m, s: m['receipt'].update(sha256='wrong'),
    'FROZEN_SOURCE_FILES': lambda m, s: s['frozen'][0].update(actual='wrong'),
    'HUMAN_SOURCE_EXACT': lambda m, s: s.update(human_bytes=b'changed'),
    'ANA_Q2_EXACT_DECISION': lambda m, s: m['decisions'][0].update(status='UNRESOLVED'),
    'ANA_Q3_EXACT_DECISION': lambda m, s: m['decisions'][1].update(decision_type='HUMAN_SUPPLIED_RELATION'),
    'ANA_Q4_EXACT_DECISION': lambda m, s: m['decisions'][2].update(relation_type='SAME_LEVEL_SIBLING'),
    'ANA_Q5_EXACT_DECISION': lambda m, s: m['decisions'][3].update(scope_ref='32:6–37:24'),
    'THREE_ACCEPTED_ONE_DEFERRED': lambda m, s: m['decisions'][1].update(status='ACCEPTED'),
    'ACCEPTED_OVERLAYS_ONLY': lambda m, s: m['accepted'].append(deepcopy(m['decisions'][1])),
    'NO_TEXTUAL_HIERARCHY': lambda m, s: m['hierarchy'].append('CHILD_OF'),
    'FOUR_CANDIDATES_PRESERVED': lambda m, s: m['crosswalk'].pop(),
    'C2_LIVE_UNRESOLVED_NOT_ACCEPTED': lambda m, s: m['crosswalk'][1].update(live_candidate=False),
    'NO_CAUSAL_OR_FULFILLMENT_ASSERTION': lambda m, s: m['decisions'][1].update(fulfillment_asserted=True),
    'Q3_POSITIVE_AND_INSUFFICIENT_EVIDENCE': lambda m, s: m['decisions'][1].update(methodological_notes=[]),
    'FROZEN_59_UNCHANGED': history(h.ACCOUNTING),
    'UNRESOLVED_57_UNCHANGED': history(h.UNRESOLVED),
    'HSA3_AG_UNCHANGED': history(h.SEAMS),
    'HSA2_F_CLOSURE_UNCHANGED': history(h.EDGES),
    'REGISTRY_UNCHANGED_EXISTING_CODES_ONLY': lambda m, s: m['registry'][0].update(evidence_code='INVENTED'),
    'CRITERIA_APPLICATION_FAITHFUL': lambda m, s: m['criteria'][0].update(criterion_code='INVENTED'),
    'NEGATIVE_CONTROLS_RETAINED': lambda m, s: m['negative'].pop(),
    'EXACT_ID_ROW_PROVENANCE': lambda m, s: m['provenance'][0].update(source_row_sha256='fuzzy'),
    'CANDIDATE_JUDGMENT_CROSSWALK': lambda m, s: m['crosswalk'][1].update(accepted_relation_created=True),
    'DEPENDENCIES_ONLY_NO_PARENTAGE': lambda m, s: m['dependencies'][-1].update(resolves_parentage=True),
    'INTEGRITY_RECEIPTS_COMPUTED': lambda m, s: m['integrity'][0].update(actual_row_sha256='wrong'),
    'NO_R4_4': lambda m, s: m.update(r44_started=True),
    'HUMAN_REPORT_FAITHFUL': lambda m, s: m.update(report='38:1 fulfills 31:35'),
    'SEAM_PACKET_UNADJUDICATED': lambda m, s: m.update(packet='A-G are adjudicated'),
    'DETERMINISTIC_RERUN': lambda m, s: m.update(rerun_digest='nondeterministic'),
}


class HumanFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = h.load(self_test=True)
        cls.m = h.build(cls.s)
        cls.files = h.serialize(cls.m, cls.s)

    def test_positive_gates_complete_negative_coverage(self):
        gg = h.gates(self.m, self.s)
        self.assertEqual(set(MUTATIONS), {g['gate'] for g in gg})
        self.assertTrue(all(g['status'] == 'PASS' for g in gg))

    def test_manifest_negative(self):
        files = dict(self.files)
        files['01_ana_human_adjudications.csv'] += b'tampered'
        self.assertFalse(h.util.manifest_ok(files))

    def test_original_rationales_verbatim(self):
        import re
        quotes = re.findall('“(.*?)”', self.s['request_bytes'].decode('utf-8-sig'), re.S)[:4]
        self.assertEqual([q.replace('\r\n', '\n') for q in quotes], [d['rationale'] for d in self.m['decisions']])

    def test_exact_researcher_provenance(self):
        self.assertEqual(h.sha(self.s['request_bytes']), self.s['human']['source_sha256'])
        self.assertEqual(h.sha(self.s['human_bytes']), self.s['cfg']['human_source']['sha256'])

    def test_q3_positive_evidence_retained(self):
        d = self.m['decisions'][1]
        self.assertGreaterEqual(len(d['evidence_ids']), 2)
        self.assertTrue({'E-LEXICAL-RECURRENCE', 'E-PARTICIPANT-ALIGNMENT', 'E-ADDRESSEE-ALIGNMENT', 'N-LEXEME-ONLY'} <= set(d['criteria_codes']))
        self.assertIn('3_2_FORMAL_NOT_RESPONSE', d['negative_controls'])
        self.assertFalse(d['accepted_relation_created'])

    def test_q3_insufficiency_has_all_reasons(self):
        notes = ' '.join(self.m['decisions'][1]['methodological_notes'])
        for phrase in ('causal/fulfillment', 'textual statement', 'interpretive necessity'):
            self.assertIn(phrase, notes)

    def test_q3_causal_mutation(self):
        m = deepcopy(self.m)
        m['decisions'][1]['causal_link_asserted'] = True
        self.assertEqual(self.gate(m, 'NO_CAUSAL_OR_FULFILLMENT_ASSERTION'), 'FAIL')

    def test_q3_prose_causal_mutation(self):
        m = deepcopy(self.m)
        m['report'] += '\nYHWH appears because of 31:35'
        self.assertEqual(self.gate(m, 'NO_CAUSAL_OR_FULFILLMENT_ASSERTION'), 'FAIL')

    def test_q3_delete_positive_evidence_fails(self):
        m = deepcopy(self.m)
        m['decisions'][1]['evidence_ids'] = []
        self.assertEqual(self.gate(m, 'Q3_POSITIVE_AND_INSUFFICIENT_EVIDENCE'), 'FAIL')

    def test_q3_delete_rationale_fails(self):
        m = deepcopy(self.m)
        m['decisions'][1]['rationale'] = ''
        self.assertEqual(self.gate(m, 'Q3_POSITIVE_AND_INSUFFICIENT_EVIDENCE'), 'FAIL')

    def test_q3_context_not_causal(self):
        d = self.m['decisions'][1]
        self.assertEqual(d['closure_context'], '31:40')
        self.assertEqual(d['closure_context_use'], 'CONTEXTUAL_METADATA_ONLY_NOT_CAUSAL_LINK')
        self.assertFalse(d['automatic_resolution'])

    def test_q5_historical_and_refined_distinct(self):
        d = self.m['decisions'][3]
        self.assertEqual(d['original_candidate_type'], 'ELIHU_WITHIN_ANA_RESPONSE_INTERVAL')
        self.assertEqual(d['relation_type'], 'ELIHU_RESPONSE_ROLE_INTERVENTION')
        self.assertEqual(d['scope_ref'], '32:2–37:24')
        self.assertIn('NARRATIVE_INTRODUCTION', ' '.join(d['methodological_notes']))
        self.assertIn('ELIHU_SPEECH_SEQUENCE', ' '.join(d['methodological_notes']))

    def test_q2_excludes_direct_closure_and_hierarchy(self):
        self.assertEqual(self.m['decisions'][0]['limitations'], ['CHILD_OF', 'SAME_LEVEL_SIBLING', 'DIRECT_CLOSURE_TARGET'])

    def test_q4_bidirectional_overlay(self):
        d = self.m['decisions'][2]
        self.assertEqual(d['direction'], 'BIDIRECTIONAL')
        self.assertEqual(d['relation_dimension'], 'OVERLAY_RESPONSIO')
        self.assertIn('INCLUSIO', d['limitations'])

    def test_criteria_do_not_add_missing_codes(self):
        codes = {r['evidence_code'] for r in self.m['registry']}
        self.assertEqual(len(codes), 24)
        self.assertTrue(all(code in codes for d in self.m['decisions'] for code in d['criteria_codes']))
        self.assertEqual(sum(r['application_role'] == 'METHODOLOGICAL_NOTE_NO_NEW_REGISTRY_CODE' for r in self.m['criteria']), 4)

    def test_dependency_q3_cannot_resolve_e(self):
        q3 = [d for d in self.m['dependencies'] if d['review_question_id'] == 'ANA-Q3']
        self.assertEqual(len(q3), 1)
        self.assertEqual(q3[0]['case_id'], 'SEAM_E')
        self.assertEqual(q3[0]['dependency_type'], 'UNRESOLVED_CANDIDATE_EVIDENCE')
        self.assertFalse(q3[0]['resolves_parentage'])

    def test_all_source_links_resolve_independently(self):
        for key in ('provenance', 'negative', 'crosswalk', 'dependencies', 'criteria'):
            for link in self.m[key]:
                if 'source_member' not in link:
                    continue
                data = self.files[link['source_member']]
                source = h.raw_rows(data)[int(link['source_data_row']) - 1]
                self.assertEqual(h.sha(data), link['source_member_sha256'])
                self.assertEqual(h.f.rowhash(source), link['source_row_sha256'])
                self.assertEqual(source[link['source_identity_field']], link['source_identity'])

    def test_all_historical_members_byte_identical(self):
        for name, data in self.s['files'].items():
            self.assertEqual(self.files[h.HISTORY + name], data)

    def test_nested_manifests_all_pass(self):
        self.assertTrue(all(x['valid'] for x in h.nested_manifests(self.files)))

    def test_frozen_accounting_has_59_receipts(self):
        self.assertEqual(sum(r['kind'] == 'FROZEN_HUMAN_JUDGMENT' for r in self.m['integrity']), 59)
        self.assertTrue(all(r['status'] == 'PASS' for r in self.m['integrity']))

    def test_historical_review_fields_not_filled(self):
        for member in (h.SEAMS, h.QUESTIONS):
            for r in h.rows(self.files[h.HISTORY + member]):
                for key in h.REVIEW_FIELDS:
                    self.assertEqual(r[key], 'UNREVIEWED' if key == 'review_status' else '')

    def test_baseline_bad_sha_stops(self):
        with self.assertRaisesRegex(ValueError, 'SHA'):
            h.baseline_audit(self.s['files'], self.s['cfg'], 'wrong')

    def test_baseline_bad_manifest_stops(self):
        files = dict(self.s['files'])
        files[h.CANDIDATES] += b'corrupt'
        with self.assertRaisesRegex(ValueError, 'manifest'):
            h.baseline_audit(files, self.s['cfg'], 'fixture', True)

    def test_missing_exact_identity_stops(self):
        with self.assertRaisesRegex(ValueError, 'exact source identity'):
            h.locate(self.s, h.CANDIDATES, 'candidate_id', 'ANA-C999')

    def test_duplicate_identity_stops(self):
        s = deepcopy(self.s)
        rr = h.rows(s['files'][h.CANDIDATES])
        s['files'][h.CANDIDATES] = h.util.csv_bytes(rr + [rr[0]])
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            h.locate(s, h.CANDIDATES, 'candidate_id', 'ANA-C1')

    def test_required_source_column_not_guessed(self):
        s = deepcopy(self.s)
        rr = h.rows(s['files'][h.CANDIDATES])
        for r in rr:
            del r['candidate_id']
        s['files'][h.CANDIDATES] = h.util.csv_bytes(rr)
        with self.assertRaises(KeyError):
            h.decisions(s)

    def test_no_real_bhsa_loader_called(self):
        from unittest.mock import patch
        with patch.object(h.f.a, 'native_bhsa', side_effect=AssertionError('BHSA must not load')):
            m = h.build(self.s)
        self.assertEqual(m['decisions'], self.m['decisions'])

    def test_serialization_rejects_invalid_decisions(self):
        m = deepcopy(self.m)
        m['decisions'][1]['accepted_relation_created'] = True
        with self.assertRaisesRegex(ValueError, 'FAIL'):
            h.serialize(m, self.s)

    def test_computed_counts_in_metadata(self):
        meta = json.loads(self.files['90_run_metadata.json'])
        self.assertEqual(meta['counts'], dict(accepted_human_judgments=3, deferred_human_decisions=1, accepted_overlay_relations=3, textual_hierarchy_relations=0, historical_candidates=4, frozen_human=59, unresolved=57, seams=7))
        self.assertFalse(meta['bhsa_extraction_performed'])
        self.assertFalse(meta['r44_started'])

    def test_independent_process_archive_byte_equality(self):
        with tempfile.TemporaryDirectory() as temp:
            outputs = []
            for name in ('first', 'second'):
                path = Path(temp) / name
                completed = subprocess.run([sys.executable, str(h.ROOT / 'src/milal_hsa3_ana_human_freeze.py'), '--self-test', '--out', str(path)], capture_output=True, text=True)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                outputs.append(path.with_name(name + '_results.zip').read_bytes())
            self.assertEqual(outputs[0], outputs[1])

    def gate(self, m, name):
        return next(g['status'] for g in h.gates(m, self.s) if g['gate'] == name)


def mutation_test(name, mutate):
    def test(self):
        m, s = deepcopy(self.m), deepcopy(self.s)
        mutate(m, s)
        actual = {g['gate']: g['status'] for g in h.gates(m, s)}
        self.assertEqual(actual[name], 'FAIL')
    return test


for gate, mutate in MUTATIONS.items():
    setattr(HumanFreezeTests, 'test_negative_' + gate.lower(), mutation_test(gate, mutate))


if __name__ == '__main__':
    unittest.main()
