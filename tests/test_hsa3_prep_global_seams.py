import ast
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_prep_global_seams as h


def frozen(path):
    return lambda m,s:next(x for x in s['frozen'] if x['path']==path).update(actual='bad')


def invented(kind):
    return lambda m,s:m['new_structural_relations'].append(dict(relation_type=kind))


def remove_relation(kind):
    return lambda m,s:m['source_edges'].remove(next(e for e in m['source_edges'] if e['relation_type']==kind))


MUTATIONS={
    'HSA1_FROZEN':frozen('docs/HUMAN_STRUCTURAL_ADJUDICATION.csv'),
    'HSA2_FROZEN':frozen('docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv'),
    'HSA2_F_FROZEN':frozen('docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv'),
    'R43_FROZEN':lambda m,s:m['historical'].update({'invented':b'changed'}),
    'ALL_FROZEN_CORES':frozen('src/milal_r4_2_participant_audit.py'),
    'NO_NEW_MR1_RULE':frozen('src/milal_mr1_historical_rules.py'),
    'SOURCE_NODES_UNCHANGED':lambda m,s:m['source_nodes'].pop(),
    'SOURCE_RELATIONS_UNCHANGED':lambda m,s:m['source_edges'].pop(),
    'NO_NEW_CHILD_OF':invented('CHILD_OF'),
    'NO_NEW_HIERARCHICALLY_ABOVE':invented('HIERARCHICALLY_ABOVE'),
    'NO_NEW_DIRECT_CLOSURE':invented('DIRECT_LOCAL_CLOSURE'),
    'NO_STRUCTURAL_ASSERTIONS':invented('SAME_TEXTUAL_LOCUS_DIFFERENT_STRUCTURAL_ROLE'),
    'NO_HEURISTIC_SELECTION':lambda m,s:m.update(candidate_method='NEAREST_OPENING'),
    'HUMAN_ACCOUNTING_INTACT':lambda m,s:m['accounting'].pop(),
    'ALL_UNRESOLVED_CROSSWALKED':lambda m,s:m['crosswalk'].pop(),
    'COMPLETE_LOCUS_SCAN':lambda m,s:m['aliases'].pop(),
    'EXACT_ROLE_IDENTITY_ONLY':lambda m,s:m['aliases'][0].update(identity_basis='REFERENCE_ONLY'),
    'TRIAGE_PARTITION':lambda m,s:m['triage'][0].update(triage_category='TRUE_GLOBAL_SEAM'),
    'TYPED_DEPENDENCY_INTEGRITY':lambda m,s:m['dependencies'][0].update(dependency_path=[]),
    'CASE_INVENTORY_FROM_DATA':lambda m,s:m['cases'].pop(),
    'GROUP_AUDIT_NO_PARENT_DECISION':lambda m,s:m['groups'][0].update(automatic_member_resolution=True),
    'PRIMARY_COUNTS_PARTITION':lambda m,s:m['cases'][0].update(primary_row_count=999),
    'CROSSWALK_DEPENDENCY_MATCH':lambda m,s:m['crosswalk'][0].update(controlling_case_id='SEAM_A'),
    'SOURCE_EVIDENCE_LOSSLESS':lambda m,s:m['evidence'].pop(),
    'REVIEW_FIELDS_BLANK':lambda m,s:m['cases'][0].update(reviewer_notes='Automatically reviewed'),
    'NO_CANDIDATE_SCORING':lambda m,s:m['cases'][0].update(parent_score=1),
    'SUMMARY_NOT_TREE':lambda m,s:m['summary_panel'].update(proposed_tree=True),
    'MEMBERS_AND_CYCLES_PRESERVED':remove_relation('GROUP_MEMBER_OF'),
    'ELIHU_INTRO_NOT_PEER':lambda m,s:m['source_edges'].append(dict(source_node='H:HSA019',target_node='H:HSA020',relation_type='SAME_LEVEL_SIBLING')),
    'NO_42_10_12_PROMOTION':lambda m,s:m['source_nodes'].append(dict(node_id='INVENTED',reference_start='42:10',textual_boundary=True)),
    'LOCAL_RELATIONS_NOT_PARENT':lambda m,s:m['triage'][0].update(direct_parent='JOB_BOOK'),
    'NO_RESPONSE_ADJACENCY_PARENT':invented('ADJACENCY_PARENT'),
    'NEGATIVE_CONTROLS':lambda m,s:m['negative'][0].update(status='FAIL'),
    'REPORT_FAITHFUL':lambda m,s:m.update(report='All parents settled'),
}


class Triage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=h.load(True);cls.model=h.build(cls.source)

    def test_positive_and_negative_gate_coverage(self):
        gates=h.gates(self.model,self.source)
        self.assertEqual(set(MUTATIONS),{g['gate'] for g in gates})
        self.assertTrue(all(g['status']=='PASS' for g in gates))

    def test_manifest_negative(self):
        files=h.serialize(self.model,self.source)
        self.assertTrue(h.r43.h1.util.manifest_ok(files))
        files['01_unresolved_row_triage.csv']+=b'bad'
        self.assertFalse(h.r43.h1.util.manifest_ok(files))

    def test_partition_without_deletion(self):
        self.assertEqual(len(self.model['triage']),57)
        self.assertEqual(sum(c['primary_row_count'] for c in self.model['cases']),57)
        self.assertEqual(self.model['source_edges'],self.source['edges'])
        self.assertEqual(len(self.model['accounting']),59)

    def test_alias_roles_remain_six_records_at_three_loci(self):
        self.assertEqual({a['locus'] for a in self.model['aliases']},{'4:1','15:1','22:1'})
        self.assertEqual(sum(len(a['node_ids']) for a in self.model['aliases']),6)
        for a in self.model['aliases']:
            self.assertEqual(len(set(a['roles'].values())),2)
            self.assertTrue(a['shared_source_evidence_ids'])

    def test_reference_only_never_establishes_alias(self):
        s=deepcopy(self.source)
        n=deepcopy(next(n for n in s['nodes'] if n['node_id']=='H:HSA025'))
        n['node_id']='OTHER_SAME_REFERENCE';s['nodes'].append(n)
        audit=next(a for a in h.role_audit(s) if a['locus']=='38:1')
        self.assertEqual(audit['identity_basis'],'NO_IDENTITY_INFERENCE')

    def test_authorized_pair_without_shared_evidence_is_unverified(self):
        s=deepcopy(self.source)
        next(n for n in s['nodes'] if n['node_id']=='H:HSA2-CYCLE-1')['source_evidence_ids']=[]
        self.assertEqual(next(a for a in h.role_audit(s) if a['locus']=='4:1')['audit_status'],'UNVERIFIED_SAME_REFERENCE_ONLY')

    def test_uncovered_node_creates_additional_review_case(self):
        s=deepcopy(self.source)
        s['cfg']['primary_scope_seeds'].pop('H:HSA030')
        rows=h.triage(s,h.role_audit(s));cc=h.cases(s,rows)
        self.assertGreater(len(cc),len(self.model['cases']))
        self.assertTrue(any(c['case_id'].startswith('SEAM_EXTRA_') for c in cc))
        self.assertEqual(sum(c['primary_row_count'] for c in cc),57)

    def test_ambiguous_review_owner_is_not_ranked(self):
        s=deepcopy(self.source)
        s['cfg']['primary_scope_seeds']['CYCLE_1']='SEAM_B'
        row=next(x for x in h.triage(s,h.role_audit(s)) if x['unresolved_node_id']=='H:HSA2-C1-S2')
        self.assertTrue(row['controlling_case_id'].startswith('SEAM_EXTRA_'))

    def test_no_new_membership_parent(self):
        row=next(x for x in self.model['triage'] if x['unresolved_node_id']=='H:HSA2-C1-S2')
        self.assertEqual(row['already_known_container'],['CYCLE_1'])
        self.assertEqual(row['direct_parent'],'UNRESOLVED')
        self.assertEqual(row['controlling_case_id'],'SEAM_C')

    def test_continuation_chain_is_review_dependency_only(self):
        row=next(x for x in self.model['triage'] if x['unresolved_node_id']=='H:HSA004')
        self.assertEqual({x['relation'] for x in row['dependency_path']},{'CONTINUES_WITHIN','CHILD_OF'})
        self.assertEqual(row['direct_parent'],'UNRESOLVED')

    def test_resolved_3_2_is_context_not_unresolved(self):
        self.assertNotIn('H:HSA014',[x['unresolved_node_id'] for x in self.model['triage']])
        for c in self.model['cases'][:2]:self.assertIn('H:HSA014',c['involved_nodes'])

    def test_closure_target_not_reopened(self):
        row=next(x for x in self.model['triage'] if x['unresolved_node_id']=='H:HSA017')
        self.assertEqual(row['triage_category'],h.CATEGORIES[4])
        self.assertEqual(row['controlling_case_id'],'SEAM_C')
        types={e['relation_type'] for e in self.model['source_edges'] if e['source_node']=='H:HSA017'}
        self.assertTrue({'DIRECT_LOCAL_CLOSURE','NO_DIRECT_RELATION','TERMINATES_ENCLOSING_GROUP'}<=types)

    def test_interface_case_has_no_exclusive_rows(self):
        e=next(c for c in self.model['cases'] if c['case_id']=='SEAM_E')
        self.assertEqual(e['primary_row_count'],0)
        self.assertEqual(e['participating_row_count'],3)
        self.assertFalse(self.model['summary_panel']['proposed_tree'])

    def test_no_fixed_independent_decision_claim(self):
        self.assertIn('NOT a proved number of independent atomic human decisions',self.model['report'])
        self.assertIn('not an eighth independent case',self.model['report'])

    def test_source_unresolved_missing_stops(self):
        s=deepcopy(self.source);s['unresolved'].pop()
        with self.assertRaisesRegex(ValueError,'unaccountable'):h.validate_source(s)

    def test_source_schema_missing_stops(self):
        s=deepcopy(self.source);s['nodes'][0].pop('parentage_status')
        with self.assertRaises(KeyError):h.validate_source(s)

    def test_review_model_does_not_alias_source(self):
        s=deepcopy(self.source);m=h.build(s);before=deepcopy(s)
        m['summary_panel']['involved_nodes'].pop()
        m['triage'][0]['source_judgment_ids'].clear()
        m['aliases'][0]['judgments'].clear()
        self.assertEqual(s,before)
        self.assertEqual({g['gate']:g['status'] for g in h.gates(m,s)}['SUMMARY_NOT_TREE'],'FAIL')

    def test_source_order_does_not_change_case_expansion(self):
        s=deepcopy(self.source);s['nodes'].reverse();s['edges'].reverse()
        cc=h.cases(s,h.triage(s,h.role_audit(s)))
        self.assertEqual([c['involved_nodes'] for c in cc],[c['involved_nodes'] for c in self.model['cases']])

    def test_synthetic_deterministic_and_archive(self):
        files=h.serialize(self.model,self.source)
        self.assertEqual(files,h.serialize(h.build(self.source),self.source))
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'audit';h.publish(files,out)
            self.assertTrue(out.with_name('audit_results.zip').is_file())
            with self.assertRaisesRegex(ValueError,'already exists'):h.publish(files,out)

    def test_syntax(self):
        ast.parse(Path(h.__file__).read_text(encoding='utf-8'))


def negative_test(gate, mutation):
    def test(self):
        s=deepcopy(self.source);m=deepcopy(self.model);mutation(m,s)
        result={g['gate']:g['status'] for g in h.gates(m,s)}
        self.assertEqual(result[gate],'FAIL')
    return test


for gate,mutation in MUTATIONS.items():
    setattr(Triage,'test_negative_'+gate.lower(),negative_test(gate,mutation))


if __name__=='__main__':unittest.main()
