from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parent))
import r4_4_contract_audit as a


def item(m,kind):return next(r for r in m['mapping'] if r['record_kind']==kind)
def node(m,ident):return next(r['contract_record'] for r in m['mapping'] if r['record_kind']=='NODE' and r['source_identity']==ident)
def relation(m,typ):return next(r['contract_record'] for r in m['mapping'] if r['record_kind']=='RELATION' and r['contract_record']['relation_type']==typ)


MUTATIONS={
 'BASELINE_EXACT':lambda m,s:m['commit'].update(verified_commit='wrong'),
 'INPUT_VERIFIED':lambda m,s:m['receipt'].update(sha256='wrong'),
 'SEAMS_FROZEN':lambda m,s:item(m,'SEAM_STATUS')['contract_record']['state'].update(status='UNREVIEWED'),
 'NECESSITY_57_FROZEN':lambda m,s:item(m,'NECESSITY')['contract_record']['state'].update(human_status='UNREVIEWED'),
 'ACTIVE_QUESTIONS_ZERO':lambda m,s:item(m,'NECESSITY')['contract_record']['state'].update(additional_parentage_review_required=True),
 'HISTORICAL_PARENT_57':lambda m,s:item(m,'QUESTION')['contract_record']['state'].update(status='RESOLVED'),
 'NO_PARENT_SYNTHESIS':lambda m,s:node(m,'H:HSA012').update(direct_parent_ids=['JOB_BOOK']),
 'NO_NEW_HUMAN_JUDGMENT':lambda m,s:m['new_human_judgments'].append('Q1_ACCEPTED'),
 'NO_NEW_ANALYTICAL_RELATION':lambda m,s:m['new_structural_relations'].append('CHILD_OF'),
 'PARTICIPANT_ARC_UNADJUDICATED':lambda m,s:m['new_overlay_relations'].append('FRIENDS_ENTRY_RESOLUTION_PARTICIPANT_ARC'),
 'NO_R4_4_CONSUMER':lambda m,s:m['consumer_implementations'].append('consumer'),
 'NODE_TYPES_DISTINCT':lambda m,s:node(m,'JOB_BOOK').update(textuality='TEXTUAL'),
 'RELATION_LAYER_EXPLICIT':lambda m,s:item(m,'RELATION')['contract_record'].update(relation_layer='COLLAPSED'),
 'UNRESOLVED_AND_NOT_REQUIRED_COEXIST':lambda m,s:node(m,'H:HSA012').update(historical_parent_status='RESOLVED'),
 'LAYER_SPECIFIC_CYCLE_POLICY':lambda m,s:m['proposal']['cycle_policy'].update(same_level_policy='REJECT_ALL_CYCLES'),
 'ROLE_ALIAS_NOT_DUPLICATE_UNIT':lambda m,s:node(m,'H:HSA2-CYCLE-1').update(node_kind='TEXTUAL_NODE'),
 'GROUP_AND_ROOT_NOT_TEXTUAL_PARENTS':lambda m,s:relation(m,'CHILD_OF').update(target_id='JOB_BOOK'),
 'FUTURE_OVERLAY_APPEND_ONLY':lambda m,s:m['proposal']['future_overlay_extension'].update(lower_layer_mutation_required=True),
 'ALL_RECORDS_MAPPED':lambda m,s:m['mapping'].pop(),
 'MAPPING_REPRODUCIBLE':lambda m,s:m['mapping'][0].update(extension='changed'),
 'NO_DROPPED_PROVENANCE':lambda m,s:m['mapping'][0]['contract_record'].update(provenance_ids=[]),
 'MAPPING_ISSUES_REPORTED':lambda m,s:m['issues'].append(dict(mapping_status='AMBIGUOUS_SCHEMA')),
 'R43_ALL_FIELDS_AUDITED':lambda m,s:m['schema_audit'].pop(),
 'CONTRACT_PROPOSAL_NOT_APPROVAL':lambda m,s:m['proposal'].update(proposal_status='FROZEN'),
 'REPORTS_FAITHFUL':lambda m,s:m['reports'].update({'14_r4_4_implementation_readiness.md':b'READY_FOR_IMPLEMENTATION\n'}),
 'HISTORICAL_BYTES_UNCHANGED':lambda m,s:m['historical'].update({'90_run_metadata.json':b'changed'}),
 'FROZEN_PINS':lambda m,s:s['pins'][0].update(actual='wrong'),
 'REQUEST_AND_PROPOSAL_EXACT':lambda m,s:s.update(request=b'wrong'),
 'DETERMINISTIC_PAYLOAD':lambda m,s:m.update(rerun_digest='wrong'),
}
for layer in a.n.l.LAYERS.values():
    MUTATIONS['LAYER_'+layer]=lambda m,s,layer=layer:next(r for r in m['mapping'] if r['record_kind']=='RELATION' and r['contract_record']['relation_layer']==layer)['contract_record'].update(relation_type='COLLAPSED')


def break_fixture(m,s,ident):
    fixture=next(f for f in m['fixtures'] if f['fixture_id']==ident)
    ids=set(fixture['assertions'][0]['mapping_ids'])
    m['mapping']=[r for r in m['mapping'] if r['mapping_id'] not in ids]


for ident in ('JOB_2_11','JOB_31_40','JOB_32_1','ELIHU','JOB_37_24_38_1','YHWH_RESPONSE','JOB_42'):
    MUTATIONS['FIXTURE_'+ident]=lambda m,s,ident=ident:break_fixture(m,s,ident)


class ContractAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=a.load(True);cls.m=a.build(cls.s);cls.files=a.serialize(cls.m,cls.s)

    def test_gate_negative_coverage(self):
        self.assertEqual(set(MUTATIONS),{r['gate'] for r in a.gates(self.m,self.s)})

    def test_all_gates_pass(self):self.assertTrue(all(r['status']=='PASS' for r in a.rows(self.files['15_gates.csv'])))

    def test_manifest_negative(self):
        f=dict(self.files);f['10_r4_4_dry_run_mapping.csv']+=b'changed';self.assertFalse(a.util.manifest_ok(f))

    def test_rebuild_byte_identical(self):self.assertEqual(self.files,a.serialize(a.build(deepcopy(self.s)),deepcopy(self.s)))

    def test_exact_baseline(self):self.assertEqual(self.s['commit']['verified_commit'],'113a1f3fe13ff9698a97f82f3f1a53b41b4f3b21')

    def test_proposal_only_and_no_production_exports(self):
        self.assertEqual(self.m['proposal']['proposal_status'],'CONTRACT_PROPOSAL')
        self.assertEqual(len(self.m['proposal']['review_questions']),7)
        packet=self.files['13_r4_4_contract_review_packet.md'].decode()
        self.assertEqual(packet.count('Researcher answer: '),7)
        self.assertEqual(packet.count('Review status: UNREVIEWED'),7)
        self.assertEqual(self.files['14_r4_4_implementation_readiness.md'],b'READY_FOR_HUMAN_CONTRACT_REVIEW\n')
        self.assertFalse(any(k.startswith(('01_canonical','02_canonical','r4_4_final')) for k in self.files))
        self.assertEqual(a.counts(self.m)['new_human_judgment_count'],0)
        self.assertEqual(a.counts(self.m)['r44_analytical_implementation_count'],0)

    def test_r43_complete_schema_coverage(self):
        expected={(name,field) for name,fields in self.s['cfg']['r43_fields'].items() for field in fields}
        self.assertEqual({(r['artifact'],r['field']) for r in self.m['schema_audit']},expected)
        self.assertEqual(len(expected),83)
        flag=next(r for r in self.m['schema_audit'] if r['field']=='later_human_review_required')
        self.assertEqual(flag['classification'],'DEPRECATED_FOR_R4_4')
        overlay=[r for r in self.m['schema_audit'] if r['artifact']=='06_overlay_relations.csv']
        self.assertTrue(all(r['classification']=='DEPRECATED_FOR_R4_4' for r in overlay))

    def test_all_source_rows_roundtrip(self):
        decoded=a.rows(self.files['10_r4_4_dry_run_mapping.csv'])
        self.assertEqual(len(decoded),len(a.source_records(self.s)))
        for r in decoded:
            self.assertEqual(r['source_record'],r['contract_record']['original_record'])
            self.assertEqual(r['source_receipt'],r['contract_record']['provenance_ids'][0])
        self.assertEqual(a.counts(self.m)['mapping_statuses']['INCOMPATIBLE'],0)
        self.assertEqual(a.counts(self.m)['mapping_statuses']['AMBIGUOUS_SCHEMA'],0)
        self.assertEqual(a.counts(self.m)['mapping_statuses']['NOT_APPLICABLE'],7)

    def test_every_source_receipt_resolves(self):
        for r in self.m['mapping']:
            receipt=r['source_receipt'];data=self.files[receipt['member']]
            raw={'text':data.decode()} if receipt['identity_field']=='DOCUMENT' else a.n.l.d.h.raw_rows(data)[receipt['data_row']-1]
            self.assertEqual(a.sha(data),receipt['member_sha256'])
            self.assertEqual(a.n.l.d.h.f.rowhash(raw),receipt['row_sha256'])
            self.assertEqual(receipt['artifact_sha256'],self.s['receipt']['sha256'])
            if receipt['identity_field']!='DOCUMENT':self.assertEqual(raw[receipt['identity_field']],receipt['identity'])

    def test_historical_unresolved_and_necessity_57(self):
        nn=[r['contract_record'] for r in self.m['mapping'] if r['record_kind']=='NODE' and r['contract_record']['parentage_necessity_status'] is not None]
        self.assertEqual(len(nn),57)
        for r in nn:
            self.assertEqual(r['historical_parent_status'],'UNRESOLVED');self.assertFalse(r['additional_parentage_review_required'])
            self.assertFalse(r['direct_parent_edge_resolved']);self.assertEqual(r['direct_parent_ids'],[])
        self.assertEqual(node(self.m,'H:HSA012')['parentage_necessity_status'],'DIRECT_TEXTUAL_PARENT_NOT_REQUIRED')

    def test_optional_absence_is_not_unresolved_or_false(self):
        root=node(self.m,'JOB_BOOK')
        self.assertEqual(root['span_type'],'NO_SPAN_RECORDED')
        self.assertEqual(root['historical_parent_status'],'NOT_APPLICABLE')
        self.assertIsNone(root['parentage_necessity_status'])
        self.assertEqual(root['field_presence']['parentage_necessity_status'],'NOT_RECORDED')
        human=node(self.m,'H:HSA012')
        self.assertIs(human['additional_parentage_review_required'],False)
        self.assertEqual(human['field_presence']['additional_parentage_review_required'],'SOURCE_RECORDED')

    def test_reference_and_scope_endpoints_preserved(self):
        rr=[r['contract_record'] for r in self.m['mapping'] if r['record_kind']=='RELATION']
        pair=next(r for r in rr if r['relation_id']=='ANA-H4');scope=next(r for r in rr if r['relation_id']=='ANA-H5')
        self.assertEqual(pair['endpoint_form'],'REFERENCE_PAIR');self.assertEqual(pair['source_id'],'');self.assertEqual(pair['target_id'],'')
        self.assertEqual(scope['endpoint_form'],'REFERENCE_SCOPE');self.assertEqual(scope['scope_ref'],'32:2–37:24')
        self.assertEqual(scope['source_id'],'');self.assertEqual(scope['target_id'],'')

    def test_group_scope_absence_not_fabricated(self):
        self.assertEqual(node(self.m,'CYCLE_1')['span_type'],'NO_SPAN_RECORDED')
        self.assertEqual(node(self.m,'CYCLE_1')['qualified_spans'],[])
        opening=node(self.m,'OPENING_NARRATIVE_COMPLEX')
        self.assertEqual(opening['span_type'],'SUPPLIED_GROUP_SCOPE')
        self.assertTrue(any(r.get('source_fields',{}).get('span_start')=='1:1' for r in opening['qualified_spans']))

    def test_unknown_endpoint_reports_schema_block(self):
        s=deepcopy(self.s)
        member=next(x['member'] for x in s['cfg']['inputs'] if x['authority_role']=='OVERLAY_RESPONSIO')
        rr=deepcopy(a.rows(s['files'][member]));rr[0]['target_ref']=''
        s['files'][member]=a.util.csv_bytes(rr)
        m=a.build(s)
        self.assertEqual(a.counts(m)['mapping_statuses']['AMBIGUOUS_SCHEMA'],1)
        self.assertEqual(len(m['issues']),1)
        self.assertEqual(m['reports']['14_r4_4_implementation_readiness.md'],b'BLOCKED_BY_SCHEMA_ISSUES\n')

    def test_incompatible_status_count_reported(self):
        m=deepcopy(self.m);m['mapping'][0].update(mapping_status='INCOMPATIBLE',extension='Contradictory required state')
        self.assertEqual(a.counts(m)['mapping_statuses']['INCOMPATIBLE'],1)
        self.assertEqual(a.mapping_issues(m['mapping'])[0]['mapping_status'],'INCOMPATIBLE')
        self.assertEqual(a.reports(m,self.s)['14_r4_4_implementation_readiness.md'],b'BLOCKED_BY_SCHEMA_ISSUES\n')

    def test_different_relation_dimensions_coexist(self):
        rr=[r['contract_record'] for r in self.m['mapping'] if r['record_kind']=='RELATION' and r['contract_record']['source_id']=='H:HSA017']
        types={r['relation_type'] for r in rr}
        self.assertTrue({'DIRECT_LOCAL_CLOSURE','NO_DIRECT_RELATION','TERMINATES_ENCLOSING_GROUP'}<=types)
        self.assertEqual(next(r['original_dimension'] for r in rr if r['relation_type']=='NO_DIRECT_RELATION'),'DIRECT_CLOSURE_TARGET')
        self.assertNotEqual(next(r['relation_layer'] for r in rr if r['relation_type']=='DIRECT_LOCAL_CLOSURE'),next(r['relation_layer'] for r in rr if r['relation_type']=='TERMINATES_ENCLOSING_GROUP'))

    def test_reciprocal_siblings_without_common_parent(self):
        self.assertTrue(a.hierarchy_acyclic(self.m['mapping']))
        self.assertEqual(node(self.m,'H:HSA025')['direct_parent_ids'],[])
        self.assertEqual(node(self.m,'H:HSA028')['direct_parent_ids'],[])
        rr=[r['contract_record'] for r in self.m['mapping'] if r['record_kind']=='RELATION']
        self.assertTrue(any(r['relation_type']=='SAME_LEVEL_SIBLING' and r['source_id']=='H:HSA025' and r['target_id']=='H:HSA028' for r in rr))
        self.assertTrue(any(r['relation_type']=='SAME_LEVEL_SIBLING' and r['source_id']=='H:HSA028' and r['target_id']=='H:HSA025' for r in rr))

    def test_true_parent_cycle_rejected(self):
        m=deepcopy(self.m);r=deepcopy(next(r for r in m['mapping'] if r['record_kind']=='RELATION' and r['contract_record']['relation_type']=='CHILD_OF'))
        c=r['contract_record'];c['source_id'],c['target_id']=c['target_id'],c['source_id'];m['mapping'].append(r)
        self.assertFalse(a.hierarchy_acyclic(m['mapping']))

    def test_group_parent_rejected_but_continuation_allowed(self):
        self.assertTrue(a.hierarchy_acyclic(self.m['mapping']))
        for parent in ['OPENING_NARRATIVE_COMPLEX','JOB_BOOK']:
            m=deepcopy(self.m);relation(m,'CHILD_OF')['target_id']=parent
            self.assertEqual(next(r['status'] for r in a.gates(m,self.s) if r['gate']=='GROUP_AND_ROOT_NOT_TEXTUAL_PARENTS'),'FAIL')

    def test_future_extensibility_creates_no_relation(self):
        before={k:v for k,v in self.s['files'].items() if any(k.endswith(x) for x in a.n.l.LAYERS)}
        proposal=deepcopy(self.s['proposal']);ext=proposal['future_overlay_extension']
        self.assertFalse(ext['lower_layer_mutation_required']);self.assertEqual(ext['actual_relations_created'],[])
        self.assertEqual(proposal['endpoint_forms'],['NODE_IDS','REFERENCE_PAIR','REFERENCE_SCOPE'])
        after={k:v for k,v in self.m['historical'].items() if any(k.endswith(x) for x in a.n.l.LAYERS)}
        self.assertEqual(before,after)
        self.assertEqual(self.m['new_overlay_relations'],[])
        self.assertFalse(any(r['record_kind']=='RELATION' and r['contract_record']['relation_type']=='FRIENDS_ENTRY_RESOLUTION_PARTICIPANT_ARC' for r in self.m['mapping']))

    def test_q3_deferred_not_accepted_relation(self):
        q=next(r['contract_record']['state'] for r in self.m['mapping'] if r['record_kind']=='QUESTION' and r['source_identity']=='ANA-Q3')
        self.assertEqual(q['status'],'UNRESOLVED');self.assertEqual(q['original_record']['decision_type'],'HUMAN_DEFERRED')
        self.assertFalse(q['original_record']['accepted_relation_created'])

    def test_duplicate_source_identity_rejected(self):
        s=deepcopy(self.s);member=s['cfg']['inputs'][0]['member'];rr=deepcopy(a.rows(s['files'][member]));rr.append(rr[0]);s['files'][member]=a.util.csv_bytes(rr)
        with self.assertRaisesRegex(ValueError,'duplicate/empty'):a.mapping(s)

    def test_layer_member_contradiction_rejected(self):
        s=deepcopy(self.s);member=next(r['member'] for r in s['cfg']['inputs'] if r['record_kind']=='RELATION')
        rr=deepcopy(a.rows(s['files'][member]));rr[0]['layer']='COMPOSITION_GROUPING';s['files'][member]=a.util.csv_bytes(rr)
        with self.assertRaisesRegex(ValueError,'layer/source member'):a.mapping(s)

    def test_raw_history_and_manifests(self):
        self.assertEqual({k[len(a.HISTORY):]:v for k,v in self.files.items() if k.startswith(a.HISTORY)},self.s['files'])
        self.assertTrue(all(x['valid'] for x in a.n.l.d.h.nested_manifests(self.files)))

    def test_release_gates_negative(self):
        good=dict(tests_run=1,successful=True,failures=0,errors=0,skipped=0)
        self.assertTrue(all(r['status']=='PASS' for r in a.n.release_gates(good,b'zip',b'zip')))
        bad=dict(good,skipped=1)
        self.assertEqual(a.n.release_gates(bad,b'zip',b'zip')[0]['status'],'FAIL')
        self.assertEqual(a.n.release_gates(good,b'zip',b'wrong')[1]['status'],'FAIL')


def mutation_test(gate,mutate):
    def test(self):
        m=deepcopy(self.m);s=deepcopy(self.s);mutate(m,s)
        self.assertEqual(next(r['status'] for r in a.gates(m,s) if r['gate']==gate),'FAIL')
    return test


for gate,mutate in MUTATIONS.items():setattr(ContractAuditTests,'test_negative_'+gate.lower(),mutation_test(gate,mutate))


if __name__=='__main__':unittest.main()
