"""Historical and cross-layer comparison, callable only with two frozen audits."""
from collections import Counter, defaultdict
from copy import deepcopy
import json
import re
import milal_jin_io as io
from milal_jin_postcontext_comparison import review_fields

S_MANIFEST='07_strict_blind_manifest.csv'
M_MANIFEST='16_macro_blind_manifest.csv'
S_QUESTIONS=[
 'Strict clause hierarchy: one top-level candidate or multiple?',
 'If multiple, is there top-level paratactic relation evidence?',
 'Is Job 1:1 only BOOK_SCOPE_INITIAL or a linguistically supported unique strict-root candidate?',
 'Define strict root within Job book scope and leave external canonical context separate?',
 'If evidence is insufficient, defer a unique strict root?']
M_QUESTIONS=[
 'Does macro configuration support one root, multiple peers or a higher frame?',
 'Is Job 1:1 a macro-root candidate or only an opening-unit onset?',
 'What top-level relation candidates do the major transitions/onsets including 3:1, 32:1/32:2, 38:1 and 42:7 form?',
 'Does raw opening/final narrative correspondence support a higher whole-book frame?',
 'Does present evidence require selecting a unique macro root?']
WORDING='''Top-level/root cardinality is discovered rather than assumed.

The first clause in the analysis scope is not automatically the linguistic root.

Strict clause top-level structure and macro textual top-level structure are separately investigated.

Paratactic top-level units are a valid possible hierarchy outcome.

A technical root is not an analytical root.

A non-textual composition group is not a textual root.

Absence of a supported mother candidate does not by itself establish root status.

Coverage and formula elaboration are evidence of hierarchical force, not automatic root-selection rules.
'''


def unique(files,suffix):
    hits=[p for p in files if p.endswith('/'+suffix) or p==suffix]
    io.require(len(hits)==1,'unique historical member: '+suffix);return hits[0]


def source(files,path,index,row):
    return dict(member=path,data_row=index,sha256=io.sha(files[path]),record=row)


def clause_ids(value):
    if not isinstance(value,list):value=[value]
    out=[]
    for item in value:
        if isinstance(item,int) or (isinstance(item,str) and item.isdecimal()):out.append(int(item))
        elif isinstance(item,str) and re.fullmatch(r'BHSA2021:clause:\d+',item):out.append(int(item.rsplit(':',1)[1]))
        elif item not in ('','UNRESOLVED',None):io.require(False,'non-explicit clause identity: '+str(item))
    return out


def compare(s,m,history,cfg,synthetic=False):
    invpath=unique(history,'01_hierarchy_relation_inventory.csv');inv=io.rows(history[invpath])
    scopepath='08_open_strict_macro_questions.csv';scopes=io.rows(history[scopepath])
    contract=json.loads(history['15_contract.json'])
    io.require(contract['contract_status']=='REVISED_R4_4_CONTRACT_HUMAN_FROZEN','frozen JIN.0.8 contract')
    io.require(len(inv)==(cfg.get('synthetic_registry_count') if synthetic else 250),'historical relation count')
    sr={(r['preceding_clause_id'],r['later_clause_id']):r for r in s['relations']};strict=[];incoming=defaultdict(set)
    for r in s['relations']:
        if r['evidence_bundle']['hypotaxis_supported']:incoming[r['later_clause_id']].add(r['preceding_clause_id'])
    def strict_row(identity,a,b,original,expect_explicit=False,expected_family='CANDIDATE_EVIDENCE'):
        pairs=[sr[(x,y)] for x in a for y in b if (x,y) in sr]
        if expect_explicit:supported=[r for r in pairs if r['explicit_local_dependency']]
        elif expected_family=='HYPOTAXIS':supported=[r for r in pairs if r['evidence_bundle']['hypotaxis_supported']]
        else:supported=[r for r in pairs if r['evidence_bundle']['hypotaxis_supported'] or r['evidence_bundle']['parataxis_supported']]
        alternative=expected_family=='HYPOTAXIS' and any(r['evidence_bundle']['parataxis_supported'] for r in pairs)
        competing=set().union(*(incoming[x] for x in b)) if b else set()
        status='S_MULTIPLE_OPTIONS' if supported and (len(competing)>1 or alternative) else 'S_HISTORICAL_SUPPORTED' if supported else 'S_ALTERNATIVE_SUPPORTED' if alternative else 'S_HISTORICAL_PARTIAL' if pairs else 'S_HISTORICAL_NOT_RECOVERED' if a and b else 'S_INSUFFICIENT'
        strict.append(dict(comparison_id=identity,status=status,expected_relation_family='EXPLICIT_LOCAL_HYPOTAXIS' if expect_explicit else expected_family,preceding_clause_ids=a,later_clause_ids=b,blind_candidate_ids=[r['candidate_relation_id'] for r in pairs],historical_source=original,
            historical_state_unchanged=True,automatic_resolution=False,limitations='Exact clause identities; support concerns candidate evidence only, not acceptance or macro projection.'))
    for i,(a,b) in enumerate(cfg['explicit_controls'],1):strict_row('CONTROL:'+str(i),[a],[b],dict(control_kind='EXPLICIT_LOCAL_REGRESSION'),True)
    for suffix,idcol in [('21_relation_review_cases.csv','relation_case_id'),('05_relation_scope_classification.csv','pair_id')]:
        p=unique(history,suffix)
        for i,r in enumerate(io.rows(history[p]),1):strict_row(suffix+':'+r[idcol],clause_ids(r['preceding_clause_id']),clause_ids(r['later_clause_id']),source(history,p,i,r))
    for i,r in enumerate(inv,1):
        if r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE'):
            a,b=clause_ids(r['target_clause_id']),clause_ids(r['source_clause_id'])
            if r['relation_type']=='HIERARCHICALLY_ABOVE':a,b=b,a
            strict_row('STRICT_UNRESOLVED:'+r['relation_id'],a,b,source(history,invpath,i,r),expected_family='HYPOTAXIS')
    macro=[];onsetids={r['clause_id'] for r in m['onsets']};closeids={r['clause_id'] for r in m['closures']}
    relevant={'CHILD_OF','HIERARCHICALLY_ABOVE','SAME_LEVEL_SIBLING','CONTINUES_WITHIN','POST_CLOSURE_TRANSITION','TRANSITION_COMPONENT','POST_SPEECH_NARRATIVE_TRANSITION'}
    for i,r in enumerate(inv,1):
        if r['relation_type'] not in relevant:continue
        a=set(clause_ids(r['source_clause_id']));b=set(clause_ids(r['target_clause_id']));typ=r['relation_type']
        pairs=[x for x in m['relations'] if (x['source_clause_id'] in a and x['target_clause_id'] in b) or (x['source_clause_id'] in b and x['target_clause_id'] in a)]
        matching=[x for x in pairs if x['candidate_kind']==('M_MACRO_PARATAXIS_POSSIBLE' if typ=='SAME_LEVEL_SIBLING' else 'M_MACRO_CONTAINMENT_POSSIBLE')]
        # Direction is material for containment: CHILD_OF stores daughter -> mother.
        if typ=='CHILD_OF':matching=[x for x in matching if x['source_clause_id'] in b and x['target_clause_id'] in a]
        elif typ=='HIERARCHICALLY_ABOVE':matching=[x for x in matching if x['source_clause_id'] in a and x['target_clause_id'] in b]
        if typ not in ('CHILD_OF','HIERARCHICALLY_ABOVE','SAME_LEVEL_SIBLING'):matching=[]
        status='M_MULTIPLE_OPTIONS' if len(matching)>1 else 'M_HISTORICAL_SUPPORTED' if matching else 'M_HISTORICAL_PARTIAL' if (a&onsetids and b&onsetids) or (a&closeids and b&onsetids) else 'M_HISTORICAL_NOT_RECOVERED'
        if r.get('proposed_semantics')=='NO_NEW_BOUNDARY':status='M_INSUFFICIENT'
        macro.append(dict(historical_relation_id=r['relation_id'],relation_type=typ,source_ref=r['source_ref'],target_ref=r['target_ref'],status=status,
            blind_relation_ids=[x['relation_candidate_id'] for x in matching],marker_anchor_matches=sorted((a|b)&(onsetids|closeids)),historical_source=source(history,invpath,i,r),
            historical_state_unchanged=True,automatic_resolution=False,limitations='Marker recovery alone is partial evidence, never relationship recovery; no-boundary cannot be proved by marker absence.'))
    groups=[]
    for gid in sorted({r['target_id'] for r in inv if r['relation_type']=='GROUP_MEMBER_OF'}):
        members=[(i,r) for i,r in enumerate(inv,1) if r['relation_type']=='GROUP_MEMBER_OF' and r['target_id']==gid]
        ids={cid for _,r in members for cid in clause_ids(r['source_clause_id'])};hits=ids&onsetids
        groups.append(dict(group_id=gid,group_reference=members[0][1]['target_ref'],historical_member_ids=[r['source_id'] for _,r in members],
            recovered_onset_clause_ids=sorted(hits),status='M_HISTORICAL_PARTIAL' if hits else 'M_HISTORICAL_NOT_RECOVERED',
            source_records=[source(history,invpath,i,r) for i,r in members],root_candidate=False,mother_candidate=False,
            limitations='Existing non-textual grouping is post-blind validation context; onset recovery does not establish grouping or a textual mother.'))
    by_s={r['clause_id']:r for r in s['top']};by_m={r['clause_id']:r for r in m['top']}
    cross=[dict(clause_id=cid,reference=(by_s.get(cid) or by_m[cid])['reference'],strict_candidate_id=by_s.get(cid,{}).get('candidate_id',''),macro_candidate_id=by_m.get(cid,{}).get('candidate_id',''),
        comparison='SHARED_EXACT_ANCHOR_DISTINCT_LAYERS' if cid in by_s and cid in by_m else 'STRICT_ONLY' if cid in by_s else 'MACRO_ONLY',same_root_status_inferred=False,automatic_unification=False) for cid in sorted(set(by_s)|set(by_m))]
    impacts=[dict(question_id=r['question_id'],question_class=r['question_class'],direct_review=r['question_id'] in ('ROOT:STRICT','ROOT:MACRO'),
        impact='TOP_LEVEL_EVIDENCE_PACKET_AVAILABLE' if r['question_id'] in ('ROOT:STRICT','ROOT:MACRO') else 'CONTEXT_ONLY; REASSESS_NECESSITY_AFTER_HUMAN_TOP_LEVEL_ADJUDICATION',
        resolved=False,original_scope_record=r,source_member=scopepath,source_sha256=io.sha(history[scopepath])) for r in scopes]
    questions=[dict(question_id=role+'-Q'+str(i),scope_id='ROOT:'+('STRICT' if role=='S' else 'MACRO'),question=q,**review_fields()) for role,qs in [('S',S_QUESTIONS),('M',M_QUESTIONS)] for i,q in enumerate(qs,1)]
    return dict(strict=strict,macro=macro,groups=groups,cross=cross,impacts=impacts,questions=questions,historical_relations=inv,contract=contract,
        history=deepcopy(history),new_human_judgments=[],new_parent_edges=[],new_roots=[],new_macro_relations=[],new_strict_relations=[],migrations=[],
        participant_arc='UNADJUDICATED',consumer_implemented=False,mother_status=json.loads(history['90_run_metadata.json'])['mother_status'])


def table(rows,columns):
    def cell(v):return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(columns)+' |\n|'+'|'.join('---' for _ in columns)+'|\n'+''.join('| '+' | '.join(cell(r.get(k,'')) for k in columns)+' |\n' for r in rows)


def render(p,s,m):
    f={name:io.csv_bytes(p[key]) for name,key in [('17_strict_postblind_comparison.csv','strict'),('18_macro_postblind_comparison.csv','macro'),('19_existing_groups_postblind_comparison.csv','groups'),('20_top_level_cross_layer_comparison.csv','cross'),('21_top_level_human_review_cases.csv','questions'),('23_open_scope_impact.csv','impacts')]}
    packet='# Top-level human review — candidate audit only\n\n'+WORDING+'\n'
    for role,title,model in [('S','STRICT',s),('M','MACRO',m)]:
        packet+='## SECTION '+role+' — '+title+'\n\n'
        packet+=table(model['top'],['candidate_id','reference','candidate_kind','formal_family','possible_containing_candidates','possible_peer_candidates'])+'\n'
        packet+=table(model['hypotheses'],['configuration','candidate_ids','status','limitations'])+'\n'
        for q in p['questions']:
            if q['question_id'].startswith(role+'-'):packet+='### '+q['question_id']+'\n\n'+q['question']+'\n\nUNREVIEWED — Researcher answer:\n\n'
    packet+='## Reading limits\n\nRaw clause inventory and every retained relation candidate are machine-readable appendices. Positive frame/configuration evidence selects top-level review candidates; lack of a mother alone does not. No numeric ranking or winner. Exact-anchor overlap across layers does not unify roots.\n\n'
    packet+='BOOK_SCOPE_ROOT concerns only the current Job scope. CORPUS_ABSOLUTE_ROOT is OUT_OF_SCOPE_FUTURE_RESEARCH. Existing composition groups are validation context only. All remaining scope records stay unresolved.\n'
    f['22_top_level_human_review_packet.md']=packet.encode()
    f['24_method_compliance_report.md']=('# Method compliance\n\n'+WORDING+'\nS and M read raw sources independently under file/module allowlists. Each physical manifest is verified before the historical archive is opened. Original blind bytes are rechecked after comparison.\n\nBOOK_SCOPE only; CORPUS_ABSOLUTE_ROOT is OUT_OF_SCOPE_FUTURE_RESEARCH. No full-tree synthesis, numeric ranking, parent/root selection, migration or participant adjudication. No native BHSA hierarchy features were loaded in either blind phase; no native comparison is needed for this release.\n\nCandidate support is not human acceptance. Insufficient evidence is a valid audit outcome.\n').encode()
    f['25_next_scope.md']=b'# Next scope\n\nHuman adjudication of ROOT:STRICT and ROOT:MACRO only. Remaining strict/macro scope records may be reassessed after those decisions, never automatically resolved. Participant arc remains separate. R4.4 consumer remains absent.\n'
    return f
