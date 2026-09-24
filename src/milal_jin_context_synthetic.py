"""Constructed contextual controls; no empirical relation is supplied as truth."""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import milal_jin_io as io
import milal_jin_context_configuration as cc
from milal_jin_relation_rules import extract,evidence
from milal_jin_synthetic import clause
from milal_jin_blind_linguistic_audit import discover,neutral

ROOT=Path(__file__).resolve().parents[1]


def fixture():
    rules=json.loads((ROOT/'config/jin_blind_linguistic_rules.json').read_bytes())
    targets=[dict(audit_target_id='JT0001',book='Job',chapter=1,verse=1),dict(audit_target_id='JT0002',book='Job',chapter=1,verse=2)]
    raw=[clause(i,verse=1 if i<5 else 2,verb='HLK[' if i in (3,7) else '>MR[') for i in range(1,9)]
    m=discover(targets,raw,rules)
    blind={cc.FROZEN_NAMES[i]:io.csv_bytes(m[key]) for i,key in enumerate(('targets','features','pairs','hypotheses'))}
    return blind


def controls():
    rules=json.loads((ROOT/'config/jin_blind_linguistic_rules.json').read_bytes());context_rules=json.loads((ROOT/'config/jin_context_rules.json').read_bytes())
    raw=[clause(i,verse=i) for i in range(1,9)];ff=extract(raw,rules)
    ctx=cc.Context(ff,[],context_rules);out={}
    out['S1']=ctx.compare(1,5)['configuration_status']=='EXACT_CONFIGURATION_CORRESPONDENCE'
    changed=deepcopy(raw)
    for i in (5,6,7):changed[i]=clause(i+1,verse=i+1,verb='HLK[',typ='NmCl',subject='OTHER/')
    out['S2']=cc.Context(extract(changed,rules),[],context_rules).compare(1,5)['configuration_status']=='CONFIGURATION_CONTRAST'
    changed=deepcopy(raw);changed[0]=clause(1,verb='HLK[',typ='NmCl')
    out['S3']=cc.Context(extract(changed,rules),[],context_rules).compare(1,5)['configuration_status']=='PARTIAL_CONFIGURATION_CORRESPONDENCE'
    raw=[clause(1,verse=1),clause(2,verse=1,relative=True),clause(3,verse=2,relative=True)]
    ff=extract(raw,rules);targets=[dict(audit_target_id='JT1',clause_id=[1,2]),dict(audit_target_id='JT2',clause_id=[3])];ctx=cc.Context(ff,targets,context_rules)
    h=evidence(ff[0],ff[1],rules);p=dict(pair_id='P',preceding_clause_id=1,later_clause_id=2)
    s=ctx.scope(p,h,ctx.compare(1,2));out['S4']=s['clause_internal_only'] and s['macro_projection_status']==cc.INTERNAL
    h=evidence(ff[0],ff[2],rules);p=dict(pair_id='P2',preceding_clause_id=1,later_clause_id=3)
    s=ctx.scope(p,h,ctx.compare(1,3));out['S5']=h['hypotaxis_supported'] and not s['clause_internal_only'] and s['macro_projection_status'] in cc.PROJECTABLE
    m=cc.build(fixture(),context_rules)
    out['S6']=any(r['member_pair_count']>1 for r in m['cases'])
    out['S7']=any(r['auxiliary_pair_ids'] and r['relation_family']=='PARATAXIS' for r in m['cases'])
    rejected=False
    try:neutral({'human_judgment':'SAME_LEVEL_SIBLING'})
    except ValueError:rejected=True
    out['S8']=rejected
    out['S9']=bool(m['archive']) and all(r['default_human_review'] is False for r in m['archive']) and not ({r['pair_id'] for r in m['archive']} & {p for c in m['cases'] for p in c['member_pair_ids']})
    out['S10']=cc.case_type('PARATAXIS',cc.CROSS,['CONFIGURATION_CONTRAST'])=='CTX_PARATAXIS_WITH_CONFIGURATION_CONTRAST'
    out['S11']=bool(m['cases']) and all(r['adjudication_applied'] is False and r['automatic_resolution'] is False for r in m['cases'])
    from milal_jin_postcontext_comparison import load
    with TemporaryDirectory() as tmp:
        root=Path(tmp);(root/'14_context_blind_manifest.csv').write_bytes(b'bad')
        try:load(root,root/'MISSING_HUMAN.zip',root/'MISSING_CONFIG.json');out['S12']=False
        except ValueError as error:out['S12']='C1 freeze first' in str(error)
    return out
