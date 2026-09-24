from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
import milal_jin_io as io
import milal_jin_focused_pipeline as pipeline
import milal_jin_focused_postblind_comparison as post
from milal_jin_human_batch import release_gates

A='01_job_1_13_candidate_inventory.csv';B='06_job_speech_frame_candidates.csv';C='10_macro_parent_candidate_inventory.csv'

def edit(m,phase,name,fn):
 rr=io.rows(m['phases'][phase][name]);fn(rr);m['phases'][phase][name]=io.csv_bytes(rr)
def source(m,name,key):edit(m,name,'source_audit.csv',lambda rr:rr[0].update({key:True}))
def local(m,ref):
 def change(rr):
  row=next((r for r in rr if r['target_ref']==ref),None)
  if row:row['excluded_from_macro']=not row['excluded_from_macro']
  else:rr.append(dict(target_ref=ref,scope=dict(clause_internal_only=True),excluded_from_macro=False))
 edit(m,'C','11_macro_parent_local_exclusions.csv',change)

MUTATIONS={
 'BASELINE_COMMIT_VERIFIED':lambda m:m.update(baseline='bad'),
 'FROZEN_REPOSITORY_PINS':lambda m:m['pins'][0].update(actual='bad'),
 'JIN_0_4_FROZEN_PRESERVED':lambda m:m['history'].update({'90_run_metadata.json':b'bad'}),
 'EXACT_RESEARCHER_REQUEST':lambda m:m.update(request=b'bad'),
 'BHSA_NATIVE_HIERARCHY_POSTBLIND_ONLY':lambda m:m['events'].reverse(),
 'JOB_1_13_NO_MOTHER_AUTO_SELECTED':lambda m:edit(m,'A',A,lambda rr:rr[0].update(selected_mother='chosen')),
 'JOB_1_13_THREE_WAY_CONTROL_PRESENT':lambda m:edit(m,'A','02_job_1_13_context_comparison.csv',lambda rr:rr.pop()),
 'JOB_1_13_RESUMPTION_AUDITED':lambda m:edit(m,'A','03_job_1_13_resumption_audit.csv',lambda rr:rr.pop()),
 'JOB_3_1_2_GENERIC_SPEECH_FRAME_AUDIT':lambda m:edit(m,'B',B,lambda rr:rr.pop()),
 'JOB_3_1_2_NO_RELATION_AUTO_SELECTED':lambda m:edit(m,'B',B,lambda rr:rr[0].update(automatic_resolution=True)),
 'SPEECH_FRAME_WHOLE_JOB_INVENTORY_PRESENT':lambda m:edit(m,'B','b_clause_event_inventory.csv',lambda rr:rr.pop()),
 'EXPLICIT_HYPOTAXIS_CONTROL_PRESENT':lambda m:edit(m,'B','08_explicit_hypotaxis_controls.csv',lambda rr:rr[0].update(human_accepted=True)),
 'JOB_2_11_LOCAL_HYPOTAXIS_EXCLUDED_FROM_MACRO':lambda m:local(m,'2:11'),
 'JOB_32_1_LOCAL_HYPOTAXIS_EXCLUDED_FROM_MACRO':lambda m:local(m,'32:1'),
 'JOB_2_11_NO_MOTHER_AUTO_SELECTED':lambda m:edit(m,'C',C,lambda rr:next(r for r in rr if r['target_ref']=='2:11').update(selected_mother='chosen')),
 'JOB_32_1_NO_MOTHER_AUTO_SELECTED':lambda m:edit(m,'C',C,lambda rr:next(r for r in rr if r['target_ref']=='32:1').update(selected_mother='chosen')),
 'NO_NEAREST_PRECEDING_HEURISTIC':lambda m:edit(m,'C',C,lambda rr:rr[0].update(retained=not rr[0]['retained'])),
 'MULTIPLE_CANDIDATES_PRESERVED':lambda m:edit(m,'C',C,lambda rr:rr.pop()),
 'NO_NUMERIC_RANKING':lambda m:edit(m,'A',A,lambda rr:rr[0].update(mother_score=99)),
 'NO_NEW_HUMAN_JUDGMENT':lambda m:m['reviews'][0].update(review_status='ACCEPTED'),
 'NO_NEW_ACCEPTED_RELATION':lambda m:m['accepted_relations'].append('bad'),
 'NO_NEW_PARENT_EDGE':lambda m:m['new_parent_edges'].append('bad'),
 'Q1_Q9_STILL_UNAPPROVED':lambda m:m.update(q1_q9_approved=True),
 'PARTICIPANT_ARC_UNADJUDICATED':lambda m:m.update(participant_arc='ACCEPTED'),
 'R4_4_CONSUMER_ABSENT':lambda m:m.update(consumer_implemented=True),
 'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m:m['history'].update({'extra':b'bad'}),
 'POSTBLIND_COMPARISON_ONLY':lambda m:m['comparisons'][0].update(new_human_acceptance=True),
 'REVIEW_PACKET_FAITHFUL':lambda m:m.update(packet='bad'),
 'SYNTHETIC_S1_S12':lambda m:m['synthetic_controls'].update(S1=False),
}
for phase,file in [('A',A),('B',B),('C',C)]:
 MUTATIONS['AUDIT_'+phase+'_BLIND']=lambda m,p=phase:m['phases'][p].update({'extra':b'bad'})
 MUTATIONS[phase+'_EVIDENCE_RECOMPUTES']=lambda m,p=phase,f=file:edit(m,p,f,lambda rr:rr.pop())
 for key,suffix in [('human_source','HUMAN_SOURCE_COUNT_ZERO'),('human_label_leakage','HUMAN_LABEL_LEAKAGE_ZERO'),('composition_source','COMPOSITION_INPUT_ZERO'),('native_hierarchy_source','NATIVE_INPUT_ZERO')]:MUTATIONS[phase+'_'+suffix]=lambda m,p=phase,k=key:source(m,p,k)


class FocusedTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=TemporaryDirectory();cls.addClassCleanup(cls.tmp.cleanup);out=Path(cls.tmp.name)/'synthetic';pipeline.execute(out,self_test=True);cls.cfg=json.loads(pipeline.CONFIG.read_bytes());work=out.with_name(out.name+'_work')
  cls.model=pipeline.enrich(post.load(work/'blind',work/'synthetic_jin04_results.zip',cls.cfg,True),cls.cfg);cls.output=io.read_dir(out)
 def test_positive_and_all_gate_mutations(self):
  gg=pipeline.gates(self.model,self.cfg,True);self.assertEqual(set(MUTATIONS),{r['gate'] for r in gg});self.assertTrue(all(r['status']=='PASS' for r in gg))
 def test_synthetic_controls_all_twelve(self):self.assertEqual(self.model['synthetic_controls'],{'S'+str(i):True for i in range(1,13)})
 def test_later_anchor_never_mother_candidate(self):
  rows=io.rows(self.model['phases']['A'][A]);self.assertTrue(all(r['preceding']['reference']!='2:1' and r['preceding']['clause_id']<r['target']['clause_id'] for r in rows))
 def test_all_neutral_predecessors_scan(self):
  rows=io.rows(self.model['phases']['C'][C]);self.assertEqual(sum(r['target_ref']=='2:11' for r in rows),11);self.assertEqual(sum(r['target_ref']=='32:1' for r in rows),35)
 def test_blind_invalid_freeze_before_missing_human_archive(self):
  with TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in ('A','B','C'):io.publish(self.model['phases'][name],root/name,False)
   (root/'B'/'metadata.json').write_bytes(b'bad')
   with self.assertRaisesRegex(ValueError,'freeze invalid'):post.load(root,root/'missing_human.zip',self.cfg)
 def test_real_mode_rejects_synthetic_archive_hash(self):
  with TemporaryDirectory() as tmp:
   root=Path(tmp)
   for name in ('A','B','C'):io.publish(self.model['phases'][name],root/name,False)
   z=io.publish(self.model['history'],root/'history')
   with self.assertRaisesRegex(ValueError,'ZIP hash'):post.load(root,z,self.cfg)
 def guard_run(self,action):
  code="import sys;from pathlib import Path;sys.path.insert(0,str(Path('src').resolve()));import milal_jin_focused_blind as b;b.guard({},Path('results/guard_output'));"+action
  return subprocess.run([sys.executable,'-B','-X','utf8','-c',code],cwd=ROOT,capture_output=True,text=True)
 def test_actual_guard_rejects_human_read(self):
  r=self.guard_run("Path('config/jin_human_batch1.json').read_bytes()");self.assertNotEqual(r.returncode,0);self.assertIn('forbidden read',r.stderr)
 def test_actual_guard_rejects_native_read(self):
  r=self.guard_run("Path('mother.tf').read_bytes()");self.assertNotEqual(r.returncode,0);self.assertIn('forbidden read',r.stderr)
 def test_actual_guard_rejects_human_module(self):
  r=self.guard_run('import milal_jin_human_batch');self.assertNotEqual(r.returncode,0);self.assertIn('forbidden import',r.stderr)
 def test_output_manifests_and_negative(self):
  f=dict(self.output);self.assertTrue(io.manifest_ok(f));f['18_focused_relation_review_packet.md']+=b'bad';self.assertFalse(io.manifest_ok(f))
 def test_combined_blind_manifest(self):
  names=[r['path'] for r in io.rows(self.output['15_focused_blind_manifest.csv'])];subset={n:self.output[n] for n in names+['15_focused_blind_manifest.csv']};self.assertTrue(io.manifest_ok(subset,'15_focused_blind_manifest.csv'))
 def test_history_lossless_and_review_blank(self):
  for k,v in self.model['history'].items():self.assertEqual(self.output[pipeline.HISTORY+k],v)
  for r in self.model['reviews']:
   self.assertEqual(r['review_status'],'UNREVIEWED')
   for k in ('relation_decision','selected_mother','paratactic_peer','macro_projection_decision','evidence_sufficient'):self.assertEqual(r[k],'')
 def test_release_gate_negative_mutations(self):
  ok=dict(tests_run=1,failures=0,errors=0,skipped=0);self.assertTrue(all(r['status']=='PASS' for r in release_gates(b'a',b'a',ok)))
  self.assertEqual(release_gates(b'a',b'b',ok)[0]['status'],'FAIL')
  for key in ('failures','errors','skipped'):
   bad=dict(ok);bad[key]=1;self.assertEqual(release_gates(b'a',b'a',bad)[1]['status'],'FAIL')


def negative(name,fn):
 def test(self):
  m=deepcopy(self.model);fn(m);self.assertEqual({r['gate']:r['status'] for r in pipeline.gates(m,self.cfg,True)}[name],'FAIL')
 return test
for name,fn in MUTATIONS.items():setattr(FocusedTests,'test_negative_'+name.lower(),negative(name,fn))

if __name__=='__main__':unittest.main()
