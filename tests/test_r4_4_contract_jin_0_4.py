from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_jin_human_batch as batch
import milal_jin_io as io


def decision(m,bid):return next(r for r in m['decisions'] if r['batch_case_id']==bid)
def cross(m,bid):return next(r for r in m['crosswalk'] if r['batch_case_id']==bid)

MUTATIONS={
 'BASELINE_COMMIT_VERIFIED':lambda m:m.update(baseline='bad'),
 'FROZEN_FILES_VERIFIED':lambda m:m['pins'][0].update(actual='bad'),
 'EXACT_RESEARCHER_SOURCE':lambda m:m.update(request=b'bad'),
 'BATCH_EXACTLY_SEVEN':lambda m:m['decisions'].append(deepcopy(m['decisions'][0])),
 'DECISION_DISTRIBUTION':lambda m:decision(m,'B1').update(relation_decision='BAD'),
 'B1_PARATAXIS_ACCEPTED':lambda m:decision(m,'B1').update(evidence_sufficient=False),
 'B1_NO_PARENT_CREATED':lambda m:decision(m,'B1')['new_parent_edges'].append('bad'),
 'B7_PARATAXIS_ACCEPTED':lambda m:decision(m,'B7').update(relation_decision='BAD'),
 'B7_NO_PARENT_CHILD_EDGE':lambda m:decision(m,'B7').update(selected_mother='38:1'),
 'B2_HUMAN_DEFERRED':lambda m:decision(m,'B2').update(active_review_status='ACCEPTED'),
 'B2_HISTORICAL_CHILD_PRESERVED':lambda m:cross(m,'B2').update(source_mutated=True),
 'B2_NOT_REJECTED':lambda m:cross(m,'B2').update(rejected=True),
 'B2_NO_NEW_MOTHER':lambda m:decision(m,'B2').update(selected_mother='1:6'),
 'B3_HUMAN_DEFERRED':lambda m:decision(m,'B3').update(review_status='ACCEPTED'),
 'B3_HISTORICAL_RELATION_PRESERVED':lambda m:cross(m,'B3').update(source_status='REMOVED'),
 'B3_NOT_REJECTED':lambda m:cross(m,'B3').update(superseded=True),
 'B3_NO_NEW_MOTHER':lambda m:decision(m,'B3').update(selected_mother='3:1'),
 'B4_INSUFFICIENT_MACRO_EVIDENCE':lambda m:decision(m,'B4').update(macro_projection_decision='MACRO_TEXTUAL'),
 'B4_NO_MOTHER':lambda m:decision(m,'B4').update(selected_mother='2:1'),
 'B5_INSUFFICIENT_MACRO_EVIDENCE':lambda m:decision(m,'B5').update(single_mother_target='DIRECT_TEXTUAL_PARENT_NOT_REQUIRED'),
 'B5_NO_MOTHER':lambda m:decision(m,'B5').update(selected_mother='31:40'),
 'B6_HYPOTAXIS_ACCEPTED':lambda m:decision(m,'B6').update(relation_decision='PARATACTIC'),
 'B6_MOTHER_38_1':lambda m:decision(m,'B6').update(references=['38:1','40:1']),
 'B6_NO_DUPLICATE_EDGE':lambda m:decision(m,'B6')['new_canonical_edge_ids'].append('NEW'),
 'NO_DUPLICATE_CANONICAL_RELATION':lambda m:decision(m,'B1')['canonical_relation_ids'].pop(),
 'ALL_DECISIONS_SOURCE_GROUNDED':lambda m:decision(m,'B7').update(verbatim_researcher_decision='invented'),
 'EXACT_LINKAGE_AND_PROVENANCE':lambda m:m['provenance'][0].update(pair_ids=['fuzzy']),
 'PAIRWISE_EVIDENCE_PRESERVED':lambda m:m['history'].update({'01_context_supported_pair_inventory.csv':b'changed'}),
 'CONTEXT_EVIDENCE_PRESERVED':lambda m:m['history'].update({'02_context_windows.csv':b'changed'}),
 'HISTORICAL_ARTIFACTS_UNCHANGED':lambda m:m['history'].update({'history/r4_4_contract_jin_0_2/edges.csv':b'changed'}),
 'EXPLICIT_SUBORDINATION_CONTROL_PRESENT':lambda m:m['explicit'].pop(),
 'EXPLICIT_SUBORDINATION_NOT_AUTO_HUMAN_ACCEPTED':lambda m:m['explicit'][0].update(human_accepted=True),
 'NEXT_FOCUSED_AUDITS_DEFINED':lambda m:m['scopes'][1].update(scope='JOB_3_ONLY'),
 'NO_R4_4_CONSUMER':lambda m:m.update(consumer_implemented=True),
 'PARTICIPANT_ARC_UNADJUDICATED':lambda m:m.update(participant_arc='ACCEPTED'),
 'Q1_Q9_NOT_APPROVED':lambda m:m.update(q1_q9_approved=True),
}


class HumanBatchTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.cfg=batch.config();cls.files=batch.fixture(cls.cfg)
  cls.model=batch.enrich(batch.prepare(cls.files,cls.cfg),cls.cfg,'SYNTHETIC')
 def test_positive_and_gate_negative_coverage(self):
  gg=batch.gates(self.model,self.cfg)
  self.assertEqual({r['gate'] for r in gg},set(MUTATIONS));self.assertTrue(all(r['status']=='PASS' for r in gg))
 def test_distribution_and_symmetric_ids_preserved(self):
  s=batch.summary(self.model);self.assertEqual(s['duplicate_edges_avoided'],3);self.assertEqual(s['new_unique_textual_edges'],0);self.assertEqual(s['reconfirmed_historical_id_references'],5)
  self.assertEqual(len(decision(self.model,'B1')['canonical_relation_ids']),2)
 def test_missing_exact_relation_fails_without_fuzzy_fallback(self):
  f=dict(self.files);rr=io.rows(f[batch.COMPARISON]);rr.pop();f[batch.COMPARISON]=io.csv_bytes(rr);io.seal(f)
  with self.assertRaisesRegex(ValueError,'exact identity'):batch.prepare(f,self.cfg)
 def test_historical_row_tamper_fails(self):
  f=dict(self.files);f['history/r4_4_contract_jin_0_2/edges.csv']+=b'bad';io.seal(f)
  with self.assertRaisesRegex(ValueError,'historical member hash'):batch.prepare(f,self.cfg)
 def test_unknown_explicit_control_fails(self):
  cfg=deepcopy(self.cfg);cfg['explicit_controls'][0]='MISSING'
  with self.assertRaisesRegex(ValueError,'exact identity'):batch.prepare(self.files,cfg)
 def test_outputs_manifest_negative_and_lossless_history(self):
  f=batch.serialize(self.model,self.cfg,'SYNTHETIC');self.assertTrue(io.manifest_ok(f));self.assertEqual(len(io.rows(f['01_jin_human_batch1_decisions.csv'])),7)
  for k,v in self.files.items():self.assertEqual(f[batch.HISTORY+k],v)
  f['01_jin_human_batch1_decisions.csv']+=b'bad';self.assertFalse(io.manifest_ok(f))
 def test_determinism_and_release_gate_negatives(self):
  a=batch.serialize(self.model,self.cfg,'SYNTHETIC');b=batch.serialize(deepcopy(self.model),self.cfg,'SYNTHETIC');self.assertEqual(a,b)
  good=dict(tests_run=1,failures=0,errors=0,skipped=0)
  self.assertTrue(all(r['status']=='PASS' for r in batch.release_gates(b'a',b'a',good)))
  self.assertEqual(batch.release_gates(b'a',b'b',good)[0]['status'],'FAIL')
  for key in ('failures','errors','skipped'):
   bad=dict(good);bad[key]=1;self.assertEqual(batch.release_gates(b'a',b'a',bad)[1]['status'],'FAIL')
 def test_no_unsupplied_review_fields_or_automatic_acceptance(self):
  self.assertTrue(all(r['decision_origin']=='EXPLICIT_RESEARCHER_TRANSCRIPTION' for r in self.model['decisions']))
  self.assertTrue(all(r['review_status']=='UNREVIEWED' and not r['human_accepted'] for r in self.model['explicit']))
 def test_reopened_is_not_rejected_or_deleted(self):
  for b in ('B2','B3'):
   self.assertEqual(cross(self.model,b)['source_status'],'ACCEPTED_SOURCE');self.assertFalse(cross(self.model,b)['rejected']);self.assertFalse(cross(self.model,b)['superseded'])


def negative(name,mutate):
 def test(self):
  m=deepcopy(self.model);mutate(m);gg={r['gate']:r['status'] for r in batch.gates(m,self.cfg)};self.assertEqual(gg[name],'FAIL')
 return test
for name,mutate in MUTATIONS.items():setattr(HumanBatchTests,'test_negative_'+name.lower(),negative(name,mutate))

if __name__=='__main__':unittest.main()
