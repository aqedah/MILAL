"""Abstract structural cases; no corpus-specific expectations in the sieve."""
import json
from functools import lru_cache
from pathlib import Path
from milal_h01_model import sieve
from milal_mfr02r_pipeline import code_fingerprint


def relation(i,s,t,typ='HYPOTACTIC',**extra):
    return dict(structural_outcome_group_id=i,source_or_peer=s,target=t,relation_type=typ,provenance_paths=[dict(rule_id='RULE',witness_id='W-'+i,binding_mode='DIRECT_BINDING')],**extra)


@lru_cache(maxsize=1)
def cases():
    m=relation('m','M','T');p=relation('p','P','T','PARATACTIC');p2=relation('p2','Q','T','PARATACTIC')
    exclusion=relation('n','','T','EXCLUDED',excluded_outcome_id='m',constraint_provenance='EXPLICIT_SYNTHETIC_CONSTRAINT')
    a=sieve([m],['T']);b=sieve([m,relation('m2','N','T')],['T']);c=sieve([m,p],['T']);d=sieve([p,p2],['T'])
    e=sieve([m,relation('same','M','T','PARATACTIC')],['T']);f=sieve([m,exclusion],['T'])
    g=sieve([m],['T'],[dict(target='T',gap_type='REFERENCE_IDENTITY')])
    h=sieve([relation('a','A','B'),relation('b','B','A')],['A','B'])
    i=sieve([relation('a','A','B'),relation('b','B','C'),relation('p','A','C','PARATACTIC')],['A','B','C'])
    duplicate=dict(m,provenance_paths=m['provenance_paths']+[dict(rule_id='SECOND',witness_id='W2',binding_mode='DIRECT_BINDING')])
    j=sieve([duplicate],['T']);many=[relation('r'+str(n),'S'+str(n),'T'+str(n)) for n in range(273)];k=sieve(many,[r['target'] for r in many])
    l=sieve([dict(m,historical_review_status='REVIEW_REQUIRED',historical_human_parent='OTHER')],['T'])
    checks={
      'H01-S1':a['targets'][0]['target_status']=='QUALIFIED_NONCOMPETING_CANDIDATE' and not a['components'] and not a['targets'][0]['human_accepted'],
      'H01-S2':b['targets'][0]['target_status']=='TRUE_DECISION_PIVOT' and len(b['components'])==1,
      'H01-S3':c['targets'][0]['target_status']=='QUALIFIED_COMPATIBLE_SET' and not c['components'],
      'H01-S4':d['targets'][0]['target_status']=='QUALIFIED_COMPATIBLE_SET' and not d['components'],
      'H01-S5':'TRUE_PAIR_RELATION_CONFLICT' in e['constraints'][0]['constraint_types'],
      'H01-S6':not a['components'] and a['search']['cartesian_products_enumerated']==0,
      'H01-S7':f['targets'][0]['target_status']=='EXPLICIT_NEGATIVE_CONFLICT' and len(f['components'])==1,
      'H01-S8':g['targets'][0]['target_status']=='EVIDENCE_GAP_NOT_STRUCTURAL_DECISION' and not g['components'],
      'H01-S9':len(h['components'])==1 and 'STRICT_MOTHER_CYCLE' in h['constraints'][0]['constraint_types'] and not any(t['true_target_decision_pivot'] for t in h['targets']),
      'H01-S10':len(i['components'])==1 and 'PARALLEL_HIERARCHY_INCOMPATIBILITY_CANDIDATE' in i['constraints'][0]['constraint_types'],
      'H01-S11':not j['components'] and len(j['dispositions'])==1,
      'H01-S12':len(k['dispositions'])==273 and len({r['relation_id'] for r in k['dispositions']})==273,
      'H01-S13':a['targets']==l['targets'] and a['components']==l['components'],
      'H01-S14':not a['components'] and len(a['dispositions'])==1}
    probes=dict(single=a,competition=b,orthogonal=c,peers=d,cycle=h,parallel_path=i,gap=g,same_pair=e,exclusion=f,duplicate=j,many=k,historical=l)
    for value in probes.values():value.pop('matrix',None)
    return checks,probes


def self_test(out):
    from milal_h01_validation import fixture,mutations,evaluate
    checks,review=cases();negative={}
    for name,mutate in mutations().items():
        e=fixture();mutate(e);negative[name]=not evaluate(e)[name]
    result=dict(stage='MFR.0.2R-H0.1',checks=checks,gate_negative_tests=negative,passed=all(checks.values()) and all(negative.values()),code_fingerprint=code_fingerprint())
    if out:
        p=Path(out);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        small={k:dict(targets=v['targets'],components=v['components'],assignments=v['assignments']) for k,v in review.items()}
        Path(str(out)+'.md').write_text('# H0.1 synthetic review\n\nFeasibility witnesses only. No candidate is accepted.\n\n```json\n'+json.dumps(small,indent=2)+'\n```\n',encoding='utf8')
    return result
