"""Q1.6 synthetic contracts, graph ablation, and compatibility checks."""
import copy,json
from pathlib import Path
from milal_q16_evidence import EvidenceGraph,dependency_contract,conflicts,empirical_status
from milal_q16_validation import GATE_FIELDS,gates
from milal_q1_binding import outcome,qualify,witness
from milal_q13_model import AssignmentModel
from milal_mfr02r_pipeline import code_fingerprint


def sample(mechanism):
    return dict(mechanism=mechanism,source_id='a',target_id='b',raw_evidence=['raw1'],provenance='SYNTHETIC_EXPLICIT_PATH',independent=True,grammatical_governance_path=['predicate','recorded_governance','complement'],pair_specific_temporal_path=['explicit_resumption'],pair_specific_locative_path=['explicit_continuation'],positive_domain_continuity_path=['explicit_reference'],independent_domain=True)


def graph_fixture():
    g=EvidenceGraph();r=g.raw('GRAMMAR','one',{'head':'a','dependent':'b'},'SYNTHETIC');s=g.raw('FRAME','two',{'source':'a','target':'c'},'SYNTHETIC')
    g.derived('w1',dict(positive_binding=True),[r],'SB01');g.derived('w2',dict(positive_binding=True),[s],'SB07')
    os=[outcome('a','b','HYPOTACTIC'),outcome('a','c','HYPOTACTIC')]
    for o,w in zip(os,['w1','w2']):o['provenance_paths']=[dict(witness_id=w,rule_id='RG-A01')];g.paths[o['structural_outcome_group_id']]=o['provenance_paths']
    return g,os,r,s


def checks():
    c={};v=sample('SB05');c['Q16-S1']=dependency_contract(v)=='POSITIVE_BINDING'
    v['duplicate_of']='SB01';c['Q16-S2']=dependency_contract(v)=='REDUNDANT_ALIAS_BLOCKED'
    v=sample('SB07');v['pair_specific_temporal_path']=[];v['both_TIME']=True;c['Q16-S3']=dependency_contract(v)=='UNRESOLVED'
    c['Q16-S4']=dependency_contract(sample('SB07'))=='POSITIVE_BINDING'
    v=sample('SB08');v['pair_specific_locative_path']=[];v['same_place']=True;c['Q16-S5']=dependency_contract(v)=='UNRESOLVED'
    c['Q16-S6']=dependency_contract(sample('SB08'))=='POSITIVE_BINDING'
    v=sample('SB09');v['positive_domain_continuity_path']=[];v['no_boundary']=True;c['Q16-S7']=dependency_contract(v)=='UNRESOLVED'
    c['Q16-S8']=dependency_contract(sample('SB09'))=='POSITIVE_BINDING'
    g,os,r,s=graph_fixture();g.add_view('temporal_view','SB06',[s],{'candidate_id':'Pa-c'});res=g.analyze(os)
    c['Q16-S9']=any(x['raw_evidence_identity']==s and x['mechanism_views']==['SB06','SB07'] and x['independent_reason_count']==1 for x in res['groups'])
    v=sample('SB09');v['tested_relation_used_for_domain']=True
    try:dependency_contract(v);c['Q16-S10']=False
    except ValueError:c['Q16-S10']=True
    before=copy.deepcopy(os);abl=g.analyze(os)['ablation'];c['Q16-S11']=next(r for r in abl if r['mechanism']=='SB01')['lose_all_binding_support']==1 and os==before
    records=[dict(candidate_id='Pa-b',witness_id='w1',raw_evidence=['one'],polarity='POSITIVE_BINDING'),dict(candidate_id='Pa-b',witness_id='w2',raw_evidence=['two'],polarity='COUNTEREVIDENCE')]
    c['Q16-S12']=conflicts(records)[0]['status']=='MECHANISM_SUPPORT_CONFLICT'
    x,y=outcome('a','c','PARATACTIC'),outcome('b','c','PARATACTIC')
    for o in (x,y):o['provenance_paths']=[dict(witness_id='SYNTHETIC',rule_id='W-P01')]
    model=AssignmentModel([x,y],['a','b','c']).analyze();c['Q16-S13']=not any(r['human_review_required'] for r in model['pivots'])
    # No empirical positive record is synthesized from a conceptual mechanism definition.
    c['Q16-S14']=empirical_status([],[])=='NO_JOB_WITNESS' and dependency_contract(dict(mechanism='SB08'))=='UNRESOLVED'
    return c


def self_test(out):
    c=checks();base={f:True for f in GATE_FIELDS.values()};negative=[]
    for name,f in GATE_FIELDS.items():
        e=dict(base);e[f]=False
        try:gates(e)
        except ValueError:negative.append(name)
    result=dict(stage='MFR.0.2R-Q1.6',checks=c,synthetic_tests=len(c),gate_negative_tests=len(negative),negative_gate_names=negative,passed=all(c.values()) and len(negative)==len(GATE_FIELDS),code_fingerprint=code_fingerprint())
    if out:
        Path(out).write_text(json.dumps(result,indent=2)+'\n',encoding='utf8')
        g,os,_,_=graph_fixture()
        Path(str(out)+'.md').write_text('# Q1.6 synthetic review\n\nSynthetic explicit paths are contracts, not empirical detection.\n\n```json\n'+json.dumps(dict(checks=c,ablation=g.analyze(os)['ablation']),indent=2)+'\n```\n',encoding='utf8')
    return result
