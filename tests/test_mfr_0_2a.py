import ast
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_mfr_common as cm
from milal_mfr02a_core import assemble,gates,release_gates,scope
from milal_mfr02a_synthetic import fixture,environment,selftest


class MFR02ATests(unittest.TestCase):
    def setUp(self):
        self.s,self.h,self.a=fixture();self.o=assemble(self.s,self.h,self.a);self.e=environment()
    def test_exact_distribution(self):
        self.assertTrue(all(gates(self.o,self.s,self.h,self.a,self.e).values()))
        self.assertEqual({r['configuration_case_id'] for r in self.o['accepted']},{'CFG000028','CFG000046','CFG000227','CFG000230','CFG001981'})
    def test_constituents_are_not_edges(self):
        self.assertEqual(len(self.o['crosswalk']),26);self.assertEqual(len(self.o['accepted']),5);self.assertEqual(self.o['representation']['constituent_edges'],[])
    def test_no_evidence_rewriting(self):
        before=deepcopy(self.a);assemble(self.s,self.h,self.a);self.assertEqual(before,self.a)
    def test_insufficient_and_formal_retain_raw(self):
        for cid in ('CFG001053','CFG001192','CFG000037'):
            row=next(r for r in self.o['decisions'] if r['configuration_case_id']==cid)
            self.assertEqual(row['underlying_raw_pair_ids'],self.a[cid]['configuration']['raw_pair_ids'])
            self.assertEqual(row['resumption_review_status'],'DEFERRED_TO_MFR_0_2B')
    def test_missing_case_fails(self):
        self.h.pop()
        with self.assertRaisesRegex(ValueError,'universe'):assemble(self.s,self.h,self.a)
    def test_wrong_pair_fails(self):
        self.a['CFG000028']['raw_relations'].pop()
        with self.assertRaisesRegex(ValueError,'Raw pair'):assemble(self.s,self.h,self.a)
    def test_append_only(self):
        with self.assertRaisesRegex(ValueError,'Append-only'):assemble(self.s,self.h,self.a,self.o['decisions'])
        prior=[dict(decision_id='OLD',phase='OLDER',payload='unchanged')]
        self.assertEqual(assemble(self.s,self.h,self.a,prior)['decisions'][0],prior[0])
    def test_independent_support_required(self):
        self.a['CFG000028']['evidence_provenance']=self.a['CFG000028']['evidence_provenance'][1:]
        with self.assertRaisesRegex(ValueError,'independent formal'):assemble(self.s,self.h,self.a)
    def test_deferred_scope_not_filtered_by_h1(self):
        rr=[dict(configuration_case_id='OUTSIDE',decision=''),dict(configuration_case_id='CFG001053',decision='')]
        for dim in ('resumption','closure'):
            result=scope(rr,self.o['decisions'],dim);self.assertEqual(len(result),2);self.assertTrue(all(x['human_decision']=='' for x in result))
    def test_synthetic_serialization(self):
        with tempfile.TemporaryDirectory() as tmp:selftest(Path(tmp)/'run')
    def test_historical_read_blocked(self):
        script="from milal_mfr02a_freeze import guard;from pathlib import Path;guard([],'.');Path('docs/HANDOFF.md').read_bytes()"
        p=subprocess.run([sys.executable,'-B','-c',"import sys;sys.path.insert(0,'src');"+script],cwd=cm.ROOT,capture_output=True,text=True)
        self.assertNotEqual(p.returncode,0);self.assertIn('boundary violation',p.stderr)
    def test_syntax(self):
        for p in (cm.ROOT/'src').glob('milal_mfr02a_*.py'):ast.parse(p.read_bytes())
    def test_researcher_authority(self):
        cfg=json.loads((cm.ROOT/'config/mfr_0_2a_job.json').read_bytes())
        self.assertEqual(cm.sha((cm.ROOT/'docs/MFR_0_2A_RESEARCHER_SOURCE.txt').read_bytes()),cfg['authority_sha256'])
        self.assertEqual(cm.sha((cm.ROOT/'config/mfr_0_2a_human_decisions.json').read_bytes()),cfg['human_registry_sha256'])
    def test_all_frozen_files_unchanged(self):
        cfg=json.loads((cm.ROOT/'config/mfr_0_2a_job.json').read_bytes())
        for n,h in cfg['frozen_files'].items():self.assertEqual(cm.sha((cm.ROOT/n).read_bytes()),h,n)

    def test_historical_status_vocabulary(self):
        from milal_mfr02a_history import classify
        self.assertEqual(classify('PARATACTIC','SAME_LEVEL_SIBLING',True),'AGREES_WITH_HISTORICAL')
        self.assertEqual(classify('PARATACTIC','SAME_LEVEL_SIBLING',False),'PARTIALLY_AGREES')
        self.assertEqual(classify('FORMAL_ONLY','SAME_LEVEL_SIBLING',True),'MFR_MORE_CONSERVATIVE')
        self.assertEqual(classify('PARATACTIC','CHILD_OF',True),'CONFLICTS')
        self.assertEqual(classify('PARATACTIC','CONTINUES_WITHIN',True),'HISTORICAL_MORE_SPECIFIC')
        self.assertEqual(classify('FORMAL_ONLY','SAME_LEVEL_SIBLING',False),'NO_HISTORICAL_COMPARISON')
    def test_historical_exact_nodes_and_scope_difference(self):
        from milal_mfr02a_history import compare
        d=self.o['decisions'][0]
        h=dict(historical_relation_id='H1',historical_relation_type='SAME_LEVEL_SIBLING',historical_review_status='FROZEN',
            historical_source=dict(record=dict(source_clause_id=['BHSA2021:clause:'+x for x in d['source_clause_ids']],target_clause_id=['BHSA2021:clause:'+x for x in d['target_clause_ids']])))
        self.assertEqual(compare([d],[h])[0]['status'],'AGREES_WITH_HISTORICAL')
        h['historical_source']['record']['target_clause_id'].append('BHSA2021:clause:OTHER')
        self.assertEqual(compare([d],[h])[0]['status'],'PARTIALLY_AGREES')
        h['historical_source']['record']['source_clause_id'].append('BHSA2021:clause:OTHER2')
        self.assertEqual(compare([d],[h])[0]['status'],'NO_HISTORICAL_COMPARISON')
        h['historical_source']['record']['source_clause_id']='UNRESOLVED'
        result=compare([d],[h])[0];self.assertEqual(result['historical_unresolved_endpoint_relation_ids'],['H1'])
        self.assertEqual(result['status'],'NO_HISTORICAL_COMPARISON')
    def test_historical_load_requires_freeze(self):
        from milal_mfr02a_history import load
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises((ValueError,FileNotFoundError)):load(Path(tmp),{})
    def test_freeze_tamper_detected(self):
        from milal_mfr02a_pipeline import freeze_valid
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'run';selftest(p)
            (p/'freeze/01_mfr_0_2a_human_decisions.csv').write_bytes(b'changed')
            self.assertFalse(freeze_valid(p/'freeze'))
    def test_duplicate_human_case_rejected(self):
        self.s['decisions'].append(self.s['decisions'][0])
        with self.assertRaisesRegex(ValueError,'Duplicate identity'):assemble(self.s,self.h,self.a)
    def test_no_literary_labels_in_analytical_decisions(self):
        for r in self.o['decisions']:
            for field in ('formal_relationship','rationale'):
                for term in ('testing scene','dialogue cycle','post-dialogue speech','prologue','messenger scene'):
                    self.assertNotIn(term,r[field].lower())
    def test_supply_is_not_inferred_from_candidate_labels(self):
        for a in self.a.values():
            for r in a['raw_relations']:r['relation_candidates']=['HYPOTAXIS_CANDIDATE']
        self.assertEqual(assemble(self.s,self.h,self.a)['decisions'],self.o['decisions'])
    def test_calibration_authority_exact(self):
        self.assertEqual([r['calibration_id'] for r in self.o['calibration']],[f'CAL-H1-{i:02}' for i in range(1,8)])
        self.assertEqual([r['principle'] for r in self.o['calibration']],[r['principle'] for r in self.s['calibration_principles']])


def negative(name):
    def test(self):
        o,e=self.o,self.e
        if name in ('BASELINE_COMMIT_VERIFIED','MFR_0_1_FROZEN_VERIFIED','MFR_0_1A_FROZEN_VERIFIED','MFR_0_1B_FROZEN_VERIFIED'):e[name]=False
        elif name=='H1_CASE_COUNT_13':o['decisions'].pop()
        elif '_COUNT_' in name:
            decision=name.split('_COUNT_')[0];o['decisions'][0][decision]=not o['decisions'][0][decision]
        elif name.startswith('CFG'):
            cid=name.split('_')[0];next(r for r in o['decisions'] if r['configuration_case_id']==cid)['hierarchy_relation_decision']='WRONG'
        elif name=='NO_CONSTITUENT_EDGE_AUTO_EXPANSION':o['representation']['constituent_edges'].append('invented')
        elif name=='NO_NEW_MOTHER':o['representation']['mothers'].append('invented')
        elif name=='RESUMPTION_NOT_ADJUDICATED':o['decisions'][0]['RESUMPTIVE']=True
        elif name=='CLOSURE_NOT_ADJUDICATED':o['decisions'][0]['CLOSURE']=False
        elif name=='CESSATION_DERIVED_EVIDENCE_NOT_USED_AS_INDEPENDENT_HIERARCHY_SUPPORT':o['decisions'][0]['independent_hierarchy_support_ids'].append(self.a['CFG000028']['evidence_provenance'][1]['evidence_id'])
        elif name=='HUMAN_DECISIONS_FROZEN_BEFORE_HISTORICAL_LOAD':e['events'].reverse()
        elif name=='HISTORICAL_RELATIONS_UNCHANGED':e['historical_after']={}
        elif name=='NO_TREE_ASSEMBLY':o['representation']['trees'].append('invented')
        elif name=='NO_ROOT':o['representation']['roots'].append('invented')
        elif name=='NO_R4_4_CONSUMER':e['new_consumers'].append('consumer')
        elif name=='RAW_EVIDENCE_MEMBERSHIP_LOSSLESS':o['crosswalk'].pop()
        elif name=='RESEARCHER_AUTHORITY_EXACT':o['decisions'][0]['researcher_supplied']=False
        else:raise AssertionError(name)
        self.assertFalse(gates(o,self.s,self.h,self.a,e)[name])
    return test


def release_negative(name):
    def test(self):
        r=dict(tests_run=1,errors=0,failures=0,skipped=0);same=valid=True
        if name=='FULL_REGRESSION_PASS':r['failures']=1
        elif name=='SKIP_ZERO':r['skipped']=1
        elif name=='MANIFEST_VALID':valid=False
        else:same=False
        self.assertFalse(release_gates(r,same,valid)[name])
    return test


_s,_h,_a=fixture()
for _g in gates(assemble(_s,_h,_a),_s,_h,_a,environment()):setattr(MFR02ATests,'test_negative_'+_g.lower(),negative(_g))
for _g in release_gates(dict(tests_run=1,errors=0,failures=0,skipped=0),True,True):setattr(MFR02ATests,'test_negative_'+_g.lower(),release_negative(_g))
if __name__=='__main__':unittest.main()
