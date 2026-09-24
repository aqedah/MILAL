"""Constructed raw structures; controls never seed real discovery."""
from copy import deepcopy
import milal_jin_io as io
from milal_jin_synthetic import clause


def corpus():
    out=[]
    specs=[('HJH[','N',True),('>MR[','N',False),('HLK[','Q',False),('TMM[','Q',False)]*2
    specs += [('HLK[','N',False),('HLK[','N',False),('MWT[','N',False),('HJH[','N',True)]
    for i,(verb,domain,time) in enumerate(specs,1):
        c=clause(i,verse=i,verb=verb,subject='A/',typ='Way0' if time else 'XQtl',tense='wayq' if time else 'perf',time=time,relative=i==10)
        c['domain']=domain;out.append(c)
    return out


def history_fixture(cfg):
    cfg=deepcopy(cfg);cfg['expected_clauses']=len(corpus());cfg['explicit_controls']=[[9,10]];cfg['macro_controls']=['1:1','1:5','1:10'];cfg['expected_scope_count']=4
    def relation(rid,typ,a,b,source_id,target_id):
        return dict(relation_id=rid,relation_type=typ,source_ref='1:'+str(a),target_ref='1:'+str(b),source_clause_id=[a],target_clause_id=[b],source_id=source_id,target_id=target_id,proposed_semantics='',historical_status='UNREVIEWED')
    inv=[relation('SYN:E1','CHILD_OF',2,1,'N2','N1'),relation('SYN:E2','SAME_LEVEL_SIBLING',1,5,'N1','N5'),relation('SYN:E3','GROUP_MEMBER_OF',1,12,'N1','G1'),relation('SYN:E4','GROUP_MEMBER_OF',5,12,'N5','G1')]
    cfg['synthetic_registry_count']=len(inv)
    f={'01_hierarchy_relation_inventory.csv':io.csv_bytes(inv),
       '21_relation_review_cases.csv':io.csv_bytes([dict(relation_case_id='SYN:C1',preceding_clause_id=9,later_clause_id=10)]),
       '05_relation_scope_classification.csv':io.csv_bytes([dict(pair_id='SYN:P1',preceding_clause_id=1,later_clause_id=5)]),
       '08_open_strict_macro_questions.csv':io.csv_bytes([dict(question_id=q,question_class=k,review_status='UNREVIEWED') for q,k in [('ROOT:STRICT','TOP_LEVEL_ROOT_OPEN'),('ROOT:MACRO','TOP_LEVEL_ROOT_OPEN'),('STRICT:X','STRICT_RELATION_OPEN'),('MACRO:X','MACRO_RELATION_OPEN')]]),
       '15_contract.json':io.js(dict(contract_status='REVISED_R4_4_CONTRACT_HUMAN_FROZEN')),
       '90_run_metadata.json':io.js(dict(mother_status={'2:11':'NO_MACRO_MOTHER_FOUND','32:1':'NO_MACRO_MOTHER_FOUND'}))}
    io.seal(f);return f,cfg
