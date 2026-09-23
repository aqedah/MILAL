from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_layer_0_2 as n


def special(m):
    return next(r for r in m['decisions'] if r['proposal_category'] == n.l.P7)


MUTATIONS = {
 'BASELINE_COMMIT_EXACT':lambda m,s:m['commit'].update(verified_commit='wrong'),
 'UPSTREAM_VERIFIED':lambda m,s:m['receipt'].update(sha256='wrong'),
 'HISTORICAL_57_PRESERVED':lambda m,s:m['unresolved'][0]['original_record'].update(direct_parent='GUESSED'),
 'PROPOSAL_CATEGORIES_PRESERVED':lambda m,s:m['decisions'][0]['original_proposal'].update(proposal_status='ACCEPTED'),
 'JOB_2_11_IDENTITY':lambda m,s:special(m).update(reference='2:1'),
 'JOB_2_11_HISTORICAL_UNRESOLVED':lambda m,s:special(m).update(historical_direct_parent='NO_PARENT'),
 'JOB_2_11_HUMAN_NECESSITY':lambda m,s:special(m).update(researcher_necessity_status='PARENT_IS_1_1'),
 'NO_JOB_2_11_PARENT':lambda m,s:special(m)['assigned_parent_ids'].append('H:HSA009'),
 'ALL_57_REVIEWED':lambda m,s:m['decisions'][0].update(human_status='UNREVIEWED'),
 'ACTIVE_FUTURE_QUESTIONS_ZERO':lambda m,s:special(m).update(additional_parentage_review_required=True),
 'HISTORICAL_UNRESOLVED_COUNT_57':lambda m,s:m['unresolved'].pop(0),
 'NEW_PARENT_EDGES_ZERO':lambda m,s:m['decisions'][0].update(direct_parent_edge_resolved=True),
 'NO_TREE_OR_DEFAULT_PARENT_SYNTHESIS':lambda m,s:m['decisions'][0]['assigned_parent_ids'].append('DEFAULT_ROOT'),
 'NON_TEXTUAL_GROUPS_PRESERVED':lambda m,s:next(r for r in m['nodes'] if r['node_kind']=='COMPOSITION_GROUP').update(textual=True),
 'ROLE_ALIASES_AND_CANONICAL_SPEECH_PRESERVED':lambda m,s:m['historical'].update({'19_role_alias_crosswalk.csv':b'changed'}),
 'LOCAL_RELATIONS_PRESERVED':lambda m,s:m['historical'].update({'02_hsa3_textual_hierarchy_edges.csv':b'changed'}),
 'CONTAINER_RELATIONS_PRESERVED':lambda m,s:m['new_composition_relations'].append('GROUP_MEMBER_OF'),
 'GLOBAL_SEAMS_FROZEN':lambda m,s:m['historical'].update({n.SEAMS:b'changed'}),
 'ANA_PRESERVED_Q3_DEFERRED':lambda m,s:next(r for r in m['unresolved'] if r['question_id']=='ANA-Q3').update(status='ACCEPTED'),
 'PARTICIPANT_ARC_UNADJUDICATED':lambda m,s:m['participant_frames'].append('2:11–42:9'),
 'NO_42_10_PROMOTION':lambda m,s:m['nodes'].append(dict(node_id='42:10',node_kind='TEXTUAL_NODE')),
 'R4_4_NOT_STARTED':lambda m,s:m.update(r44_started=True),
 'ALL_HUMAN_DECISIONS_AUTHORIZED':lambda m,s:m['decisions'][0].update(rationale='invented'),
 'CROSSWALK_EXACT':lambda m,s:m['crosswalk'][0].update(source_row_sha256='wrong'),
 'FINAL_STATUS_EXACT':lambda m,s:m['final'][0].update(historical_direct_parent='RESOLVED'),
 'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m,s:m['historical'].update({'extra.csv':b'added'}),
 'ALL_RELATION_DIMENSIONS_PRESERVED':lambda m,s:m['historical'].update({'18_technical_navigation_relations.csv':b'deleted'}),
 'REPORTS_FAITHFUL':lambda m,s:m['reports'].update({'05_hsa3_layered_completion_summary.md':b'57 parentages resolved'}),
 'FROZEN_REPOSITORY_PINS':lambda m,s:s['frozen'][0].update(actual='wrong'),
 'RESEARCHER_AUTHORITY_EXACT':lambda m,s:s.update(request=b'wrong'),
 'DETERMINISTIC_PAYLOAD':lambda m,s:m.update(rerun_digest='wrong'),
}
for cat in n.l.CATEGORIES:
    MUTATIONS[cat[:2]+'_COUNT'] = lambda m,s,cat=cat:next(r for r in m['decisions'] if r['proposal_category']==cat).update(proposal_category='UNKNOWN')


class NecessityFreezeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=n.load(True); cls.m=n.build(cls.s); cls.files=n.serialize(cls.m,cls.s)

    def test_negative_coverage(self):
        self.assertEqual(set(MUTATIONS),{r['gate'] for r in n.gates(self.m,self.s)})

    def test_positive_gates(self):
        self.assertTrue(all(r['status']=='PASS' for r in n.rows(self.files['08_gates.csv'])))

    def test_manifest_mutation(self):
        ff=dict(self.files);ff['03_parentage_necessity_final_status.csv']+=b'changed'
        self.assertFalse(n.util.manifest_ok(ff))

    def test_independent_build(self):
        self.assertEqual(self.files,n.serialize(n.build(deepcopy(self.s)),deepcopy(self.s)))

    def test_exact_baseline(self):
        self.assertEqual(self.s['commit']['verified_commit'],'a8fbd794bfec3f05132f847a8ba51f9f0e63567b')

    def test_57_necessities_not_57_parents(self):
        c=n.counts(self.m)
        self.assertEqual(c['historical_unresolved_parent_rows'],57)
        self.assertEqual(c['PARENTAGE_NECESSITY_REVIEW_COMPLETED'],57)
        self.assertEqual(c['active_future_direct_parent_questions'],0)
        self.assertEqual(c['DIRECT_PARENT_EDGE_RESOLVED'],0)
        self.assertEqual(c['proposal_categories'],dict(zip(n.l.CATEGORIES,[8,6,10,19,13,1])))
        self.assertEqual(c['human_necessity_statuses'],{'DIRECT_PARENT_NOT_REQUIRED':14,'CURRENT_LAYERED_RELATIONS_SUFFICIENT':42,'DIRECT_TEXTUAL_PARENT_NOT_REQUIRED':1})

    def test_historical_machine_and_human_separate(self):
        for r in self.m['decisions']:
            self.assertEqual(r['proposal_status'],'UNREVIEWED');self.assertEqual(r['human_status'],'FROZEN')
            self.assertEqual(r['researcher_decision'],'ACCEPT')
            for k in n.l.REVIEW_FIELDS:
                self.assertEqual(r['original_proposal'][k],'UNREVIEWED' if k=='review_status' else '')
            self.assertEqual(r['original_proposal']['direct_parent'],'UNRESOLVED')
            self.assertEqual(r['assigned_parent_ids'],[])

    def test_every_crosswalk_resolves_raw_row_and_hash(self):
        raw=n.l.d.h.raw_rows(self.s['files'][n.PROPOSALS])
        for r in self.m['crosswalk']:
            source=raw[r['source_data_row']-1]
            self.assertEqual(source[r['source_identity_field']],r['node_id'])
            self.assertEqual(r['source_row_sha256'],n.l.d.h.f.rowhash(source))
            self.assertEqual(r['source_member_sha256'],n.sha(self.s['files'][n.PROPOSALS]))
            self.assertEqual(r['source_artifact_sha256'],self.s['receipt']['sha256'])
            self.assertEqual(r['source_proposal_id'],'HSA3-LAYER.0.1::'+n.PROPOSALS+'::node_id='+r['node_id'])

    def test_special_rationale_and_existing_constraints(self):
        r=special(self.m);self.assertEqual(r['node_id'],'H:HSA012');self.assertEqual(r['reference'],'2:11')
        self.assertEqual(r['researcher_necessity_status'],'DIRECT_TEXTUAL_PARENT_NOT_REQUIRED')
        self.assertEqual(r['rationale'],self.s['human']['category_decisions'][n.l.P7]['rationale'])
        nn=next(r for r in self.m['nodes'] if r['node_id']=='H:HSA012')
        self.assertTrue(nn['textual']);self.assertEqual(nn['structural_function'],'PARAGRAPH_ONSET')
        self.assertEqual(nn['accepted_annotations'][0]['original_record']['label'],'FRIENDS_ARRIVAL / PARTICIPANT_INTRODUCTION')
        rr=[r for member in n.l.LAYERS for r in n.rows(self.s['files'][member]) if r['source_node']=='H:HSA012']
        self.assertTrue(any(r['relation_type']=='NOT_WITHIN_SECOND_TESTING_SCENE' for r in rr))
        self.assertTrue(any(r['relation_type']=='GROUP_MEMBER_OF' and r['target_node']=='OPENING_NARRATIVE_COMPLEX' for r in rr))
        self.assertFalse(any(r['relation_type']=='CHILD_OF' for r in rr))

    def test_forbidden_parent_assignments_each_fail(self):
        for ident in ['1:1','2:1','3:1','H:HSA009','H:HSA013','DEFAULT_ROOT','NO_PARENT']:
            with self.subTest(ident=ident):
                m=deepcopy(self.m);special(m)['assigned_parent_ids']=[ident]
                self.assertEqual(next(r['status'] for r in n.gates(m,self.s) if r['gate']=='NO_JOB_2_11_PARENT'),'FAIL')

    def test_canonical_speech_not_deleted(self):
        roles=n.rows(self.s['files']['19_role_alias_crosswalk.csv'])
        self.assertEqual(len(roles),6);self.assertEqual(sum(r['is_role_alias'] for r in roles),3)
        nodes={r['node_id']:r for r in self.m['nodes']}
        for r in roles:
            self.assertTrue(nodes[r['canonical_textual_node']]['textual'])
            self.assertEqual(nodes[r['canonical_textual_node']]['node_kind'],'TEXTUAL_NODE')

    def test_all_source_bytes_and_nested_manifests(self):
        self.assertEqual({k[len(n.HISTORY):]:v for k,v in self.files.items() if k.startswith(n.HISTORY)},self.s['files'])
        self.assertTrue(all(r['valid'] for r in n.l.d.h.nested_manifests(self.files)))
        self.assertEqual(len(self.s['files']),self.s['receipt']['members'])
        self.assertEqual(self.s['cfg']['archive']['members'],225)

    def test_scope_exact_and_readiness_only(self):
        self.assertEqual(self.files['06_remaining_research_scope.md'],self.s['files'][n.SCOPE])
        for word in [b'PARENTAGE_NECESSITY_REVIEW_COMPLETE',b'R4_4_CONTRACT_REVIEW_STILL_REQUIRED',b'NOT STARTED']:
            self.assertIn(word,self.files['07_r4_4_readiness_update.md'])

    def test_duplicate_identity_rejected(self):
        s=deepcopy(self.s);pp=deepcopy(n.rows(s['files'][n.PROPOSALS]));pp.append(deepcopy(pp[0]))
        s['files'][n.PROPOSALS]=n.util.csv_bytes(pp);n.l.f.seal(s['files'])
        with self.assertRaisesRegex(ValueError,'proposal categories|unique proposal'):
            n.input_audit(s['files'],s['cfg'],s['receipt']['sha256'],True)
        with self.assertRaisesRegex(ValueError,'exact proposal identity'):
            n.source_link(s,pp[0]['node_id'])

    def test_missing_schema_rejected(self):
        s=deepcopy(self.s);pp=deepcopy(n.rows(s['files'][n.PROPOSALS]));pp[0].pop('node_id')
        s['files'][n.PROPOSALS]=n.util.csv_bytes(pp);n.l.f.seal(s['files'])
        with self.assertRaises((ValueError,KeyError)):
            n.input_audit(s['files'],s['cfg'],s['receipt']['sha256'],True)

    def test_unknown_human_category_rejected(self):
        s=deepcopy(self.s);s['human']['category_decisions'].pop(n.l.P2)
        with self.assertRaises(KeyError):n.decisions(s)

    def test_unapproved_decision_rejected(self):
        s=deepcopy(self.s);s['human']['category_decisions'][n.l.P2]['researcher_decision']='UNREVIEWED'
        with self.assertRaisesRegex(ValueError,'unapproved'):n.decisions(s)

    def test_real_hash_and_mode_rejected(self):
        with self.assertRaisesRegex(ValueError,'SHA/count'):
            n.input_audit(self.s['files'],self.s['cfg'],'wrong')
        ff=deepcopy(self.s['files']);meta=json.loads(ff['90_run_metadata.json']);meta['mode']='FROZEN_REAL_LAYER_INTEGRATION'
        ff['90_run_metadata.json']=n.util.json_bytes(meta);n.l.f.seal(ff)
        with self.assertRaisesRegex(ValueError,'input mode'):
            n.input_audit(ff,self.s['cfg'],self.s['receipt']['sha256'],True)

    def test_no_real_zip_in_synthetic(self):
        with self.assertRaisesRegex(ValueError,'synthetic cannot'):n.load(True,'anything.zip')

    def test_full_regression_release_negative(self):
        good=dict(tests_run=1,successful=True,failures=0,errors=0,skipped=0)
        self.assertTrue(all(r['status']=='PASS' for r in n.release_gates(good,b'zip',b'zip')))
        for key,value in [('tests_run',0),('successful',False),('failures',1),('errors',1),('skipped',1)]:
            bad=dict(good);bad[key]=value
            self.assertEqual(n.release_gates(bad,b'zip',b'zip')[0]['status'],'FAIL')

    def test_independent_zip_release_negative(self):
        good=dict(tests_run=1,successful=True,failures=0,errors=0,skipped=0)
        self.assertEqual(n.release_gates(good,b'zip',b'changed')[1]['status'],'FAIL')
        self.assertEqual(n.release_gates(good,b'',b'')[1]['status'],'FAIL')


def mutation_test(gate, mutate):
    def test(self):
        m=deepcopy(self.m);s=deepcopy(self.s);mutate(m,s)
        self.assertEqual(next(r['status'] for r in n.gates(m,s) if r['gate']==gate),'FAIL')
    return test


for gate,mutate in MUTATIONS.items():
    setattr(NecessityFreezeTests,'test_negative_'+gate.lower(),mutation_test(gate,mutate))


if __name__=='__main__':unittest.main()
