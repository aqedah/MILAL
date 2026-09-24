"""Small synthetic source with every authorized application category."""
from copy import deepcopy
from collections import Counter
import milal_jin_io as io


def fixture(cfg):
    cfg=deepcopy(cfg);cfg['question_source']='questions.md'
    cases=[
      ('E:5645a90df42fba6884a0','CHILD_OF','1:13','1:6'),
      ('E:e664ee6af98d968e0ec6','HIERARCHICALLY_ABOVE','3:1','3:2'),
      ('E:b2b850faaf0159baeadc','CONTINUES_WITHIN','3:2','3:1'),
      ('E:94026f426d623f2921a2','CHILD_OF','40:1','38:1')]
    for i,(a,b) in enumerate([('1:14','1:13'),('1:16','1:13'),('1:17','1:13'),('1:18','1:13'),('2:9','2:1–2:10'),('11:4','11:1'),('1:5','1:1–1:5'),('28:1','27:1'),('42:16','42:7')]):cases.append(('SYN:C'+str(i),'CONTINUES_WITHIN',a,b))
    cases += [('SYN:S1','SAME_LEVEL_SIBLING','1:6','2:1'),('SYN:S2','SAME_LEVEL_SIBLING','2:1','1:6')]
    inv=[dict(relation_id=rid,relation_type=typ,source_ref=a,target_ref=b,proposal_status='UNREVIEWED',historical_status='ACCEPTED_SOURCE',latest_review_status='UNREVIEWED',proposed_semantics='NO_NEW_BOUNDARY' if a in ('28:1','42:16') else 'MACRO_TEXTUAL_CONTINUATION') for rid,typ,a,b in cases]
    cfg['expected_registry_count']=len(inv);cfg['expected_counts']=dict(Counter(r['relation_type'] for r in inv))
    f={'01_hierarchy_relation_inventory.csv':io.csv_bytes(inv),'questions.md':('\n'.join(f'Q{i}: Synthetic historical question {i}?' for i in range(1,10))+'\n').encode(),
       '09_strict_clause_positive_controls.csv':io.csv_bytes([dict(control_id='SYN:STRICT',human_accepted=False,macro_evidence=False,proposed_relation_layer='STRICT_CLAUSE_HIERARCHY')]),
       '90_run_metadata.json':io.js(dict(mother_search_results={'2:11':'NO_MACRO_MOTHER_FOUND','32:1':'NO_MACRO_MOTHER_FOUND'},q1_q9={f'Q{i}':'UNAPPROVED' for i in range(1,10)},participant_arc='UNADJUDICATED'))}
    io.seal(f);return f,cfg
