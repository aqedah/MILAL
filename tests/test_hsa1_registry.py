import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa1_registry as h
from milal_hsa1_synthetic import source


class Registry(unittest.TestCase):
    def setUp(self):
        self.s, self.rows, self.md = source()
        self.m = h.build(self.s, self.rows, self.md)

    def row(self, ref):
        return next(r for r in self.m['judgments'] if r['reference_start']==ref)

    def failed(self, gate):
        self.assertEqual(next(r['status'] for r in h.gates(self.m,self.s) if r['gate']==gate),'FAIL')

    def test_all_gates(self):
        self.assertTrue(all(r['status']=='PASS' for r in h.gates(self.m,self.s)))
        self.assertTrue(h.util.manifest_ok(h.serialize(self.m,self.s)))

    def test_authored_document_matches_csv(self):
        self.assertIn(h.markdown_table(h.registry()),h.MD.read_text(encoding='utf-8'))

    def test_human_csv_matches_git_lf_contract(self):
        self.assertNotIn(b'\r\n',h.CSV.read_bytes())
        self.assertEqual(h.CSV.read_bytes(),h.registry_bytes(h.registry()))

    def test_all_human_judgments_present_negative(self):
        self.m['judgments'][0]['judgment_id']=self.m['judgments'][1]['judgment_id']
        self.failed('ALL_HUMAN_JUDGMENTS_PRESENT')

    def test_friends_negative(self):
        self.row('2:11')['structural_function']='INTERNAL_TRANSITION';self.failed('FRIENDS_2_11_PARAGRAPH')

    def test_wife_negative(self):
        self.row('2:9')['related_reference']='["2:1"]';self.failed('WIFE_2_9_INTERNAL')

    def test_scene_negative(self):
        self.row('1:13')['hierarchy_relation']='SAME_LEVEL_SIBLING';self.failed('SCENE_1_13_CHILD')

    def test_testing_units_negative(self):
        self.row('2:1')['hierarchy_relation']='CHILD_OF';self.failed('TESTING_UNITS_SAME_LEVEL')

    def test_job_27_29_negative(self):
        self.row('29:1')['hierarchy_relation']='CHILD_OF';self.failed('JOB_27_29_SAME_LEVEL')

    def test_elihu_negative(self):
        self.row('34:1')['hierarchy_relation']='CHILD_OF';self.failed('FOUR_ELIHU_SIBLINGS')

    def test_yhwh_negative(self):
        self.row('40:6')['hierarchy_relation']='CHILD_OF';self.failed('TWO_YHWH_SIBLINGS')

    def test_internal_40_1_negative(self):
        self.row('40:1')['hierarchy_relation']='SAME_LEVEL_SIBLING';self.failed('40_1_CHILD_OF_38_1')

    def test_job_responses_negative(self):
        self.row('42:1')['hierarchy_relation']='CHILD_OF';self.failed('TWO_JOB_RESPONSE_SIBLINGS')

    def test_42_7_negative(self):
        self.row('42:7')['structural_function']='INTERNAL_TRANSITION';self.failed('42_7_PARAGRAPH')

    def test_42_16_negative(self):
        self.row('42:16')['structural_function']='PARAGRAPH_ONSET';self.failed('42_16_NO_BOUNDARY')

    def test_endings_not_mr1_negative(self):
        ident=self.row('1:22')['judgment_id']
        next(r for r in self.m['links'] if r['judgment_id']==ident and r['evidence_kind']=='EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION')['source_row']['MR1_EXPLICIT_CLOSURE']='True'
        self.failed('ENDINGS_NOT_MR1_CLOSURE')

    def test_3_1_not_mr1_negative(self):
        fake=copy.deepcopy(self.m['links'][0]);fake.update(judgment_id=self.row('3:1')['judgment_id'],evidence_kind='MR1_CSF',source_layer='mr1')
        self.m['links'].append(fake)
        self.failed('3_1_NOT_MR1')

    def test_anonymous_negative(self):
        next(r for r in self.m['links'] if r['source_row'].get('anonymous_entry')=='True')['source_row']['participant_identity']='messenger_2'
        self.failed('ANONYMOUS_IDENTITIES_UNRESOLVED')

    def test_anonymous_first_appearance_negative(self):
        next(r for r in self.m['links'] if r['source_row'].get('anonymous_entry')=='True')['source_row']['first_appearance_in_book_if_exact']='FIRST'
        self.failed('ANONYMOUS_IDENTITIES_UNRESOLVED')

    def test_anonymous_role_negative(self):
        next(r for r in self.m['links'] if r['source_row'].get('anonymous_entry')=='True')['source_row']['named_role']='messenger_2'
        self.failed('ANONYMOUS_IDENTITIES_UNRESOLVED')

    def test_overt_entry_negative(self):
        ident=self.row('1:14')['judgment_id']
        self.m['links']=[r for r in self.m['links'] if not (r['judgment_id']==ident and r['evidence_kind']=='SOURCE_PHRASE_CANDIDATE_NOT_ENTITY_RESOLUTION')]
        self.failed('OVERT_1_14_ENTRY_RETAINED')

    def test_42_7_hr1_not_lost_negative(self):
        ident=self.row('42:7')['judgment_id']
        self.m['links']=[r for r in self.m['links'] if not (r['judgment_id']==ident and r['source_row'].get('human_case')=='CASE030')]
        self.failed('42_7_THREE_SOURCE_EVENTS_SEPARATE')

    def test_closure_hr1_not_lost_negative(self):
        self.m['links']=[r for r in self.m['links'] if r['source_row'].get('case_id')!='CASE025']
        self.failed('CLOSURES_AND_HR1_PRESERVED')

    def test_no_automatic_hierarchy_negative(self):
        self.m['pairs'].append(dict(judgment_id='INFERRED',reference='4:1',relation='CHILD_OF',related_reference='3:1',related_judgment_id='',authority='AUTOMATIC'))
        self.failed('NO_AUTOMATIC_HIERARCHY')

    def test_no_score_negative(self):
        self.m['pairs'][0]['confidence_percentage']=99;self.failed('NO_SCORE_RANK')

    def test_no_interpretive_label_negative(self):
        self.row('2:11')['theological_label']='invented';self.failed('NO_NEW_INTERPRETIVE_LABEL')

    def test_exact_linkage_negative(self):
        self.m['links'][0]['source_locator']['row_sha256']='wrong';self.failed('EXACT_SOURCE_LINKAGE_ONLY')

    def test_schema_negative(self):
        self.row('2:11')['review_status']='UNREVIEWED';self.failed('HUMAN_SCHEMA_AND_TARGET_IDS')

    def test_wrong_related_id_negative(self):
        self.m['pairs'][0]['related_judgment_id']='HSA999';self.failed('HUMAN_SCHEMA_AND_TARGET_IDS')

    def test_reference_span_negative(self):
        self.row('32:2')['reference_end']='32:6';self.failed('REFERENCE_SPANS_AND_LINK_SCOPES')

    def test_exact_id_from_wrong_reference_negative(self):
        ident=self.row('2:11')['judgment_id']
        next(r for r in self.m['links'] if r['judgment_id']==ident and r['evidence_kind']=='EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION')['source_row']['ref']='2:9'
        self.failed('REFERENCE_SPANS_AND_LINK_SCOPES')

    def test_md_csv_negative(self):
        self.m['markdown']=self.m['markdown'].replace('PARAGRAPH_ONSET','SCENE_ONSET');self.failed('MD_CSV_AGREE')

    def test_3_1_above_3_2_negative(self):
        self.row('3:1')['hierarchy_relation']='SAME_LEVEL_SIBLING';self.failed('DIRECT_3_1_ABOVE_3_2')

    def test_archive_integrity_negative(self):
        self.s['receipts'][0]['sha256']='bad';self.failed('SOURCE_ARCHIVE_INTEGRITY')

    def test_negative_controls_negative(self):
        self.m['negative'].pop();self.failed('NEGATIVE_CONTROLS_RETAINED')

    def test_determinism_negative(self):
        self.m['links'].reverse();self.failed('DETERMINISTIC_OUTPUT')

    def test_manifest_negative(self):
        files=h.serialize(self.m,self.s);files['01_structural_judgments.csv']+=b'corrupt'
        self.assertEqual(h.util.manifest_gate(files)['status'],'FAIL')

    def test_no_fuzzy_fallback(self):
        rows=copy.deepcopy(self.rows);rows[0]['source_evidence_ids']='["nearly_the_same_ID"]'
        with self.assertRaisesRegex(ValueError,'unresolved exact ID'):h.build(self.s,rows,self.md)

    def test_human_only_retained(self):
        rows=copy.deepcopy(self.rows);rows[-1]['source_evidence_ids']='["NO_EXACT_MACHINE_LINK"]'
        m=h.build(self.s,rows,self.md)
        self.assertEqual(m['judgments'][-1]['structural_function'],'NO_BOUNDARY')
        self.assertFalse(any(x['judgment_id']==rows[-1]['judgment_id'] for x in m['links']))

    def test_mixed_unknown_and_exact_rejected(self):
        rows=copy.deepcopy(self.rows);rows[0]['source_evidence_ids']=h.canonical(['NO_EXACT_MACHINE_LINK','SYNTHETIC:CONTROL:1:5'])
        with self.assertRaisesRegex(ValueError,'mixed'):h.build(self.s,rows,self.md)

    def test_direct_relations_not_transitively_completed(self):
        pairs=self.m['pairs']
        self.assertFalse(any(r['reference']=='1:14' and r['related_reference']=='1:6' for r in pairs))
        self.assertEqual(len([r for r in pairs if r['reference'] in ('32:6','34:1','35:1','36:1')]),12)

    def test_no_primary_atom_guessed(self):
        self.assertTrue(all(r['primary_anchor_atom_if_known']=='' for r in h.registry()))

    def test_registry_never_overwritten_by_audit(self):
        before=h.CSV.read_bytes(),h.MD.read_bytes()
        h.serialize(self.m,self.s)
        self.assertEqual(before,(h.CSV.read_bytes(),h.MD.read_bytes()))

    def test_independent_serialization_byte_identical(self):
        self.assertEqual(h.serialize(self.m,self.s),h.serialize(h.build(self.s,self.rows,self.md),self.s))

    def test_publication_and_rerun_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            a,b=Path(tmp)/'a',Path(tmp)/'b'
            files=h.serialize(self.m,self.s)
            h.publish(files,a);h.publish(h.serialize(h.build(self.s,self.rows,self.md),self.s),b)
            self.assertEqual(a.with_name('a_results.zip').read_bytes(),b.with_name('b_results.zip').read_bytes())
            with zipfile.ZipFile(a.with_name('a_results.zip')) as z:
                self.assertIsNone(z.testzip());self.assertEqual(set(z.namelist()),set(files))
            with self.assertRaisesRegex(ValueError,'output exists'):h.publish(files,a)

    def test_rejected_archive_pin(self):
        with self.assertRaisesRegex(ValueError,'SHA256'):h.src.archive(b'not an archive','0'*64,True)


if __name__=='__main__':unittest.main()
