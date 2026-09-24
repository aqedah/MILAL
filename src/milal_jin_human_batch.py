"""Append-only transcription of researcher Batch 1; no linguistic detection or consumer."""
from collections import Counter
from copy import deepcopy
import argparse
import json
from pathlib import Path
import subprocess
import sys
import milal_jin_io as io

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/jin_human_batch1.json'
HISTORY='history/jin_0_3/'
COMPARISON='15_postcontext_human_comparison.csv'
READY='BLOCKED_PENDING_FOCUSED_RELATION_AUDITS'


def config():return json.loads(CONFIG.read_bytes())
def exact_one(rows,key,value):
    found=[r for r in rows if r[key]==value]
    io.require(len(found)==1,f'exact identity required: {key}={value}')
    return found[0]


def source_link(files,row):
    source=row['original_pairwise_human_crosswalk']['historical_source']
    member='history/r4_4_contract_jin_0_2/'+source['member']
    io.require(io.sha(files[member])==source['member_sha256'],'historical member hash')
    original=io.rows(files[member])[int(source['data_row'])-1]
    io.require(original==source['record'] and original['relation_id']==row['human_relation_id'],'historical exact row identity')
    io.require(original['source_status']=='ACCEPTED_SOURCE','historical accepted source required')
    return dict(member=member,member_sha256=io.sha(files[member]),data_row=int(source['data_row']),record=original)


def prepare(files,cfg):
    io.require(io.manifest_ok(files),'upstream manifest')
    comparisons=io.rows(files[COMPARISON]);review=io.rows(files['24_contextual_human_review_cases.csv'])
    supported=io.rows(files['01_context_supported_pair_inventory.csv'])
    decisions=[];crosswalk=[];provenance=[]
    for supplied in cfg['batch']:
        d=deepcopy(supplied);bid=d['batch_case_id'];d['adjudication_id']='JIN04:'+bid
        d['decision_origin']='EXPLICIT_RESEARCHER_TRANSCRIPTION'
        d['active_review_status']='REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT' if d['review_status']=='HUMAN_DEFERRED' else 'HUMAN_RECONFIRMED_AFTER_BLIND_AUDIT' if d['relation_decision'] in ('PARATACTIC','HYPOTACTIC') else 'UNRESOLVED_PENDING_FOCUSED_AUDIT'
        d['new_canonical_edge_ids']=[];d['new_parent_edges']=[];d['consumer_precedence_executed']=False
        d['canonical_relation_ids']=list(d['historical_relation_ids'])
        linked=[]
        for rid in d['historical_relation_ids']:
            row=exact_one(comparisons,'human_relation_id',rid);source=source_link(files,row)
            io.require(set([row['source_ref'],row['target_ref']])==set(d['references']),'endpoint mismatch')
            linked.append(row)
            crosswalk.append(dict(batch_case_id=bid,historical_relation_id=rid,source_ref=row['source_ref'],target_ref=row['target_ref'],relation_type=row['historical_relation_type'],source_status='ACCEPTED_SOURCE',active_review_status=d['active_review_status'],historical_relation_status=d['historical_relation_status'],historical_source=source,pairwise_context_record=row,source_mutated=False,rejected=False,superseded=False))
        d['pair_ids']=sorted({p for r in linked for p in r['exact_pair_ids']})
        d['context_ids']=sorted({p for r in linked for p in r['context_ids']})
        if bid in ('B4','B5'):
            panel='19_job_2_11_context_panel.csv' if bid=='B4' else '21_job_32_1_context_panel.csv'
            rr=io.rows(files[panel]);d['pair_ids']=[r['pair_id'] for r in rr];d['context_ids']=[r['context_id'] for r in rr]
            d['scope_evidence']=[{k:r[k] for k in ('pair_id','clause_internal_only','cross_locus','macro_projectable','local_dependency_type')} for r in rr]
        else:d['scope_evidence']=[]
        d['contextual_review_case_ids']=sorted({r['review_case_id'] for r in review if set(r['human_relation_ids'])&set(d['historical_relation_ids']) or set(r['member_pair_ids'])&set(d['pair_ids'])})
        io.require(d['contextual_review_case_ids'],'no exact contextual review linkage')
        provenance.append(dict(batch_case_id=bid,researcher_source=cfg['source_request']['path'],researcher_source_sha256=cfg['source_request']['sha256'],source_section='CASE '+bid,verbatim_researcher_decision=d['verbatim_researcher_decision'],historical_relation_ids=d['historical_relation_ids'],pair_ids=d['pair_ids'],context_ids=d['context_ids'],contextual_review_case_ids=d['contextual_review_case_ids'],rationale_authority='RESEARCHER; NOT_NEW_AUTOMATIC_DISCOVERY'))
        decisions.append(d)
    controls=[]
    for ident in cfg['explicit_controls']:
        r=exact_one(supported,'pair_id',ident)
        io.require(r['source_hypothesis']['relation_hypothesis']=='HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED','explicit hypo source')
        controls.append(dict(pair_id=ident,label='EXPLICIT_SUBORDINATION_POSITIVE_CONTROL_FOR_REVIEW',review_status='UNREVIEWED',human_accepted=False,relation_decision='',selected_mother='NONE',source_record=r))
    return dict(decisions=decisions,crosswalk=crosswalk,provenance=provenance,explicit=controls,scopes=deepcopy(cfg['focused_audits']),history=dict(files),original_history=dict(files),consumer_implemented=False,participant_arc='UNADJUDICATED',q1_q9_approved=False)


def summary(m):
    d=m['decisions'];accepted=[r for r in d if r['relation_decision'] in ('PARATACTIC','HYPOTACTIC')]
    return dict(batch_cases=len(d),decision_distribution=dict(Counter(r['relation_decision'] for r in d)),new_unique_textual_edges=len({e for r in d for e in r['new_canonical_edge_ids']}),new_parent_edges=sum(len(r['new_parent_edges']) for r in d),reconfirmed_relation_judgments=len(accepted),duplicate_edges_avoided=sum(bool(r['canonical_relation_ids']) for r in accepted),reconfirmed_historical_id_references=sum(len(r['canonical_relation_ids']) for r in accepted),reopened_relations=sum(r['review_status']=='HUMAN_DEFERRED' for r in d),explicit_controls=len(m['explicit']))


def gates(m,cfg):
    ds={r['batch_case_id']:r for r in m['decisions']};cs={r['batch_case_id']:r for r in cfg['batch']}
    def matches(b,keys):return b in ds and all(ds[b].get(k)==cs[b][k] for k in keys)
    def none(b):return b in ds and ds[b]['selected_mother']=='NONE' and ds[b]['new_parent_edges']==[] and ds[b]['new_canonical_edge_ids']==[]
    def history(b):
        rr=[r for r in m['crosswalk'] if r['batch_case_id']==b]
        return {r['historical_relation_id'] for r in rr}==set(cs[b]['historical_relation_ids']) and bool(rr) and all(r['historical_source']==source_link(m['original_history'],exact_one(io.rows(m['original_history'][COMPARISON]),'human_relation_id',r['historical_relation_id'])) and r['source_status']=='ACCEPTED_SOURCE' and not r['source_mutated'] for r in rr)
    checks={'BASELINE_COMMIT_VERIFIED':m['baseline']==cfg['baseline'],'FROZEN_FILES_VERIFIED':all(r['actual']==r['expected'] for r in m['pins']),
        'EXACT_RESEARCHER_SOURCE':io.sha(m['request'])==cfg['source_request']['sha256'] and all(r['verbatim_researcher_decision'] in m['request'].decode('utf8') for r in cfg['batch']),
        'BATCH_EXACTLY_SEVEN':len(m['decisions'])==7 and set(ds)==set(cs),
        'DECISION_DISTRIBUTION':Counter(r['relation_decision'] for r in m['decisions'])==Counter(PARATACTIC=2,HYPOTACTIC=1,REQUIRES_ADDITIONAL_CONTEXT=2,INSUFFICIENT_EVIDENCE=2)}
    for b in ('B1','B7'):
        checks[b+'_PARATAXIS_ACCEPTED']=matches(b,['relation_decision','macro_projection_decision','evidence_sufficient'])
        checks[b+('_NO_PARENT_CREATED' if b=='B1' else '_NO_PARENT_CHILD_EDGE')]=none(b)
    for b in ('B2','B3'):
        checks[b+'_HUMAN_DEFERRED']=matches(b,['review_status','relation_decision','historical_relation_status']) and ds[b]['active_review_status']=='REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT'
        checks[b+('_HISTORICAL_CHILD_PRESERVED' if b=='B2' else '_HISTORICAL_RELATION_PRESERVED')]=history(b)
        checks[b+'_NOT_REJECTED']=all(not r['rejected'] and not r['superseded'] for r in m['crosswalk'] if r['batch_case_id']==b)
        checks[b+'_NO_NEW_MOTHER']=none(b)
    for b in ('B4','B5'):
        checks[b+'_INSUFFICIENT_MACRO_EVIDENCE']=matches(b,['relation_decision','macro_projection_decision','single_mother_target']) and all(not r['macro_projectable'] for r in ds[b]['scope_evidence']) and len(ds[b]['scope_evidence'])==(4 if b=='B4' else 2)
        checks[b+'_NO_MOTHER']=none(b)
    checks['B6_HYPOTAXIS_ACCEPTED']=matches('B6',['relation_decision','macro_projection_decision','evidence_sufficient','historical_relation_status'])
    checks['B6_MOTHER_38_1']=ds['B6']['selected_mother']=='38:1' and ds['B6']['references']==['40:1','38:1'] and all(r['source_ref']=='40:1' and r['target_ref']=='38:1' and r['relation_type']=='CHILD_OF' for r in m['crosswalk'] if r['batch_case_id']=='B6')
    checks['B6_NO_DUPLICATE_EDGE']=ds['B6']['new_canonical_edge_ids']==[] and ds['B6']['new_parent_edges']==[] and history('B6')
    checks['NO_DUPLICATE_CANONICAL_RELATION']=all(r['canonical_relation_ids']==cs[r['batch_case_id']]['historical_relation_ids'] and r['new_canonical_edge_ids']==[] and r['new_parent_edges']==[] for r in m['decisions']) and all(history(b) for b in ('B1','B7'))
    checks['ALL_DECISIONS_SOURCE_GROUNDED']=all(all(r[k]==cs[r['batch_case_id']][k] for k in cs[r['batch_case_id']]) for r in m['decisions'])
    checks['EXACT_LINKAGE_AND_PROVENANCE']=m['provenance']==prepare(m['original_history'],cfg)['provenance'] and all(r['pair_ids']==p['pair_ids'] and r['context_ids']==p['context_ids'] and r['contextual_review_case_ids']==p['contextual_review_case_ids'] for r,p in zip(m['decisions'],m['provenance']))
    checks['PAIRWISE_EVIDENCE_PRESERVED']=all(m['history'].get(k)==v for k,v in m['original_history'].items() if k.endswith(('03_blind_candidate_pairs.csv','04_blind_relation_hypotheses.csv','01_context_supported_pair_inventory.csv')))
    checks['CONTEXT_EVIDENCE_PRESERVED']=all(m['history'].get(k)==m['original_history'][k] for k in ('02_context_windows.csv','03_context_signatures.csv','04_context_correspondence.csv','24_contextual_human_review_cases.csv'))
    checks['HISTORICAL_ARTIFACTS_UNCHANGED']=m['history']==m['original_history'] and io.manifest_ok(m['history'])
    checks['EXPLICIT_SUBORDINATION_CONTROL_PRESENT']={r['pair_id'] for r in m['explicit']}==set(cfg['explicit_controls']) and all(r['source_record']==exact_one(io.rows(m['original_history']['01_context_supported_pair_inventory.csv']),'pair_id',r['pair_id']) for r in m['explicit'])
    checks['EXPLICIT_SUBORDINATION_NOT_AUTO_HUMAN_ACCEPTED']=all(r['label']=='EXPLICIT_SUBORDINATION_POSITIVE_CONTROL_FOR_REVIEW' and r['review_status']=='UNREVIEWED' and not r['human_accepted'] and r['relation_decision']=='' and r['selected_mother']=='NONE' for r in m['explicit'])
    checks['NEXT_FOCUSED_AUDITS_DEFINED']=m['scopes']==cfg['focused_audits']
    checks['NO_R4_4_CONSUMER']=not m['consumer_implemented'] and not list((ROOT/'src').glob('*r4_4*.py')) and all(not r['consumer_precedence_executed'] for r in m['decisions'])
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED'
    checks['Q1_Q9_NOT_APPROVED']=not m['q1_q9_approved']
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def contract():return '''# Contract implications — Q1–Q9 remain unapproved

A. Parataxis is a genuine textual-hierarchy placement relation, not a missing-parent error.
B. Wider formal/distributional evidence can support human hypotaxis despite similar focal formulas.
C. Pairwise linguistic support and macro textual relation remain separate records.
D. Contextual contrast weakens simple parataxis inference without proving a particular mother.
E. Historical judgments may be reopened when blind evidence is insufficient.

Historical ACCEPTED_SOURCE records remain immutable. The latest human layer marks B2/B3
REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT / HUMAN_DEFERRED, never REJECTED or SUPERSEDED.
Precedence is documented only: no canonical consumer executes it. B1/B6/B7 reuse every
exact historical relation ID, including both stored orientations of symmetric SAME_LEVEL.
Three relation-level duplicate creations are avoided; five historical ID references are
reconfirmed, with no new edge or ID. No automatic hierarchy construction is performed.
B4/B5 retain historical paragraph/participant/transition facts solely in the source layer;
composition is not a mother substitute. SINGLE_MOTHER_TARGET remains unresolved.
No DIRECT_TEXTUAL_PARENT_NOT_REQUIRED conclusion is restored.
Participant arc remains UNADJUDICATED. Readiness: BLOCKED_PENDING_FOCUSED_RELATION_AUDITS.
'''


def serialize(m,cfg,mode):
    gg=gates(m,cfg);io.require(all(r['status']=='PASS' for r in gg),str([r for r in gg if r['status']=='FAIL']))
    files={HISTORY+k:v for k,v in m['history'].items()};d=m['decisions']
    tables={'01_jin_human_batch1_decisions.csv':d,'02_jin_human_batch1_provenance.csv':m['provenance'],'03_jin_human_batch1_historical_crosswalk.csv':m['crosswalk'],
        '04_jin_human_batch1_controls.csv':[dict(batch_case_id=r['batch_case_id'],control=r['control'],relation_decision=r['relation_decision'],selected_mother=r['selected_mother'],authority='RESEARCHER_BATCH1') for r in d],
        '05_jin_human_batch1_reopened_relations.csv':[r for r in m['crosswalk'] if r['active_review_status']=='REOPENED_FOR_ADDITIONAL_LINGUISTIC_AUDIT'],
        '06_jin_human_batch1_deferred_cases.csv':[r for r in d if r['relation_decision'] in ('REQUIRES_ADDITIONAL_CONTEXT','INSUFFICIENT_EVIDENCE')],
        '07_explicit_hypotaxis_review_control.csv':m['explicit'],'08_next_focused_audit_scope.csv':m['scopes']}
    for name,rr in tables.items():files[name]=io.csv_bytes(rr)
    files['09_next_focused_audit_scope.md']=('# Focused audits — planned, no answers or mother selected\n\n'+'\n\n'.join('## '+r['audit_id']+'\n\n'+json.dumps(r,ensure_ascii=False,indent=2) for r in m['scopes'])+'\n').encode()
    report='# Contextual human adjudication Batch 1\n\n'+READY+'\n\nOnly B1–B7 are transcribed. The upstream 206-case queue is unchanged.\n\n'
    report+='| Case | Decision | Mother | Historical IDs |\n|---|---|---|---|\n'
    for r in d:report+=f"| {r['batch_case_id']} | {r['relation_decision']} | {r['selected_mother']} | {', '.join(r['canonical_relation_ids'])} |\n"
    report+='\n```json\n'+json.dumps(summary(m),ensure_ascii=False,indent=2)+'\n```\n'
    for r in d:report+='\n## '+r['batch_case_id']+' — supplied researcher decision\n\n'+r['verbatim_researcher_decision']+'\n'
    files['10_batch1_adjudication_report.md']=report.encode();files['11_contract_implications.md']=contract().encode()
    files['13_researcher_source.txt']=m['request'];files['14_batch_config.json']=io.js(cfg)
    files['90_run_metadata.json']=io.js(dict(stage=cfg['stage'],mode=mode,status='PASS',readiness=READY,baseline=m['baseline'],summary=summary(m),archive_sha256=m['archive_sha256'],frozen_receipts=m['pins'],source_request_sha256=io.sha(m['request']),implementation_sha256=io.sha(Path(__file__).read_bytes()),consumer_implemented=m['consumer_implemented'],participant_arc=m['participant_arc'],q1_q9_approved=m['q1_q9_approved'],external_release_gates=['DETERMINISTIC_RERUN','FULL_REGRESSION_PASS']))
    io.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if io.manifest_ok(files) else 'FAIL'));files['12_gates.csv']=io.csv_bytes(gg);io.seal(files);return files


def enrich(m,cfg,archive_hash):
    subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],'HEAD'],cwd=ROOT,check=True,capture_output=True)
    m.update(baseline=cfg['baseline'],pins=[dict(path=k,expected=v,actual=io.sha((ROOT/k).read_bytes())) for k,v in sorted(cfg['frozen_files'].items())],request=(ROOT/cfg['source_request']['path']).read_bytes(),archive_sha256=archive_hash)
    return m


def fixture(cfg):
    """Small explicit synthetic source graph; no real-data execution or detector import."""
    rows=[];edges=[];supported=[];reviews=[]
    for b in cfg['batch']:
        for i,rid in enumerate(b['historical_relation_ids']):
            rr=b['references'][::-1] if i else b['references'];typ='SAME_LEVEL_SIBLING' if b['batch_case_id'] in ('B1','B7') else 'HIERARCHICALLY_ABOVE' if b['batch_case_id']=='B3' else 'CHILD_OF'
            record=dict(relation_id=rid,source_status='ACCEPTED_SOURCE',relation_type=typ,source_node='SYN:'+rr[0],target_node='SYN:'+rr[1]);edges.append(record)
            rows.append(dict(human_relation_id=rid,source_ref=rr[0],target_ref=rr[1],historical_relation_type=typ,exact_pair_ids=['SYNPAIR:'+b['batch_case_id']],context_ids=['SYNCTX:'+b['batch_case_id']],original_pairwise_human_crosswalk=dict(historical_source=dict(member='edges.csv',data_row=len(edges),record=record))))
        reviews.append(dict(review_case_id='SYNREVIEW:'+b['batch_case_id'],human_relation_ids=b['historical_relation_ids'],member_pair_ids=['SYNPAIR:'+b['batch_case_id']]))
    eb=io.csv_bytes(edges)
    for r in rows:r['original_pairwise_human_crosswalk']['historical_source']['member_sha256']=io.sha(eb)
    for ident in cfg['explicit_controls']:supported.append(dict(pair_id=ident,source_hypothesis=dict(relation_hypothesis='HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED'),source_pair=dict(pair_id=ident)))
    f={COMPARISON:io.csv_bytes(rows),'history/r4_4_contract_jin_0_2/edges.csv':eb,'24_contextual_human_review_cases.csv':io.csv_bytes(reviews),'01_context_supported_pair_inventory.csv':io.csv_bytes(supported)}
    for name,bid,n in [('19_job_2_11_context_panel.csv','B4',4),('21_job_32_1_context_panel.csv','B5',2)]:
        f[name]=io.csv_bytes([dict(pair_id='SYNPAIR:'+bid,context_id='SYNCTX:'+bid,clause_internal_only=bid=='B4' and i>0,cross_locus=bid=='B5' or i==0,macro_projectable=False,local_dependency_type='SYNTHETIC_LOCAL') for i in range(n)])
    for name in ['02_context_windows.csv','03_context_signatures.csv','04_context_correspondence.csv']:f[name]=io.csv_bytes([dict(identity='SYNTHETIC',accepted=False)])
    io.seal(f);return f


def execute(out,self_test=False):
    cfg=config()
    if self_test:f=fixture(cfg);h=io.sha(io.js({k:io.sha(v) for k,v in f.items()}))
    else:
        data=(ROOT/cfg['archive']['path']).read_bytes();h=io.sha(data);io.require(h==cfg['archive']['sha256'],'pinned upstream archive');f=io.archive(data)
    m=enrich(prepare(f,cfg),cfg,h);files=serialize(m,cfg,'SYNTHETIC' if self_test else 'REAL_FROZEN_JIN_0_3')
    zp=io.publish(files,Path(out));print(json.dumps(dict(zip=str(zp),sha256=io.sha(zp.read_bytes()),summary=summary(m),gates=len(io.rows(files['12_gates.csv']))),ensure_ascii=False));return files


def release_gates(a,b,receipt):
    return [dict(gate='DETERMINISTIC_RERUN',status='PASS' if a==b and bool(a) else 'FAIL'),dict(gate='FULL_REGRESSION_PASS',status='PASS' if receipt.get('tests_run',0)>0 and all(receipt.get(k)==0 for k in ('failures','errors','skipped')) else 'FAIL')]


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);parser.add_argument('--self-test',action='store_true');args=parser.parse_args()
    execute(args.out,args.self_test)
