"""Append-only single-mother compatibility audit; not an R4.4 consumer."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import r4_4_contract_audit as a

ROOT, sha, rows, util = a.ROOT, a.sha, a.rows, a.util
CONFIG = ROOT/'config/r4_4_contract_jin_0_1_job.json'
HISTORY = 'history/r4_4_contract_0_1/'
L2 = a.HISTORY
L1 = L2+a.n.HISTORY
FG = L1+a.n.l.HISTORY
READY = 'BLOCKED_PENDING_SINGLE_MOTHER_COMPATIBILITY_REVIEW'
SM = ('SM1_TEXTUAL_DAUGHTER_SINGLE_MOTHER_REQUIRED','SM2_TEXTUAL_MOTHER_ALREADY_RESOLVED',
      'SM3_NON_TEXTUAL_GROUP_EXEMPT','SM4_ROLE_ALIAS_EXEMPT','SM5_TECHNICAL_NODE_EXEMPT',
      'SM6_TEXTUAL_ROOT_CANDIDATE_REVIEW_REQUIRED','SM7_APPLICABILITY_UNRESOLVED')
DIRECT = {'CHILD_OF':('source_node','target_node'),'HIERARCHICALLY_ABOVE':('target_node','source_node')}
PLACEMENT = {'CONTINUES_WITHIN','DIRECT_LOCAL_CLOSURE'}
DOCUMENTS = {'01_jin_single_mother_methodological_addendum.md':'docs/R4_4_CONTRACT_JIN_0_1_ADDENDUM.md',
             '19_audit_specification.md':'docs/R4_4_CONTRACT_JIN_0_1_SPEC.md'}
TABLES = {'nodes':'02_single_mother_applicability_nodes.csv','crosswalk':'03_historical_57_single_mother_crosswalk.csv',
          'semantics':'04_existing_hierarchy_relation_semantics.csv','mothers':'05_existing_direct_mother_edges.csv',
          'zero':'06_textual_nodes_without_direct_mother.csv','candidates':'07_single_mother_candidate_pool.csv',
          'supersession':'10_contract_0_1_supersession_crosswalk.csv','peers':'14_same_level_parent_consistency.csv'}


def require(ok, message):
    if not ok: raise ValueError('R4.4-CONTRACT.JIN.0.1 STOP: '+message)


def load(self_test=False, archive=None):
    require(not (self_test and archive),'synthetic cannot consume real archive')
    cfg=json.loads(CONFIG.read_bytes());commit=a.n.l.d.baseline_receipt(cfg)
    pins=a.n.l.d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['actual']==r['expected'] for r in pins),'frozen file changed')
    request=(ROOT/cfg['source_request']['path']).read_bytes()
    require(sha(request)==cfg['source_request']['sha256'],'researcher request hash')
    if self_test:
        old=a.load(True);files=a.serialize(a.build(old),old);digest=sha(files['99_manifest_sha256.csv'])
    else:
        data=(Path(archive) if archive else ROOT/cfg['archive']['path']).read_bytes();digest=sha(data)
        require(digest==cfg['archive']['sha256'],'upstream ZIP SHA256')
        files=a.n.l.d.h.f.a.prep.r43.h1.src.archive(data,digest,mr1=True)['files']
        require(len(files)==cfg['archive']['members'],'upstream member count')
    require(util.manifest_ok(files) and all(x['valid'] for x in a.n.l.d.h.nested_manifests(files)),'upstream manifests')
    meta=json.loads(files['90_run_metadata.json']);gg=rows(files['15_gates.csv'])
    require(meta['version']=='R4.4-CONTRACT.0.1' and meta['status']=='PASS' and meta['r44_consumer_implemented'] is False,'upstream stage')
    require(meta['mode']==('SYNTHETIC_CONTRACT_TEST_ONLY' if self_test else 'FROZEN_REAL_CONTRACT_DRY_RUN'),'upstream mode')
    require(len(gg)==meta['gate_count'] and all(x['status']=='PASS' for x in gg),'upstream gates')
    return dict(cfg=cfg,commit=commit,pins=pins,request=request,files=files,
                receipt=dict(sha256=digest,members=len(files),synthetic=self_test),
                mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_SINGLE_MOTHER_AUDIT',
                documents={k:(ROOT/v).read_bytes() for k,v in DOCUMENTS.items()})


def source(s, member, field):
    data=s['files'][member];raw=a.n.l.d.h.raw_rows(data);typed=rows(data);out=[];seen=set()
    for i,(r,rr) in enumerate(zip(typed,raw),1):
        require(field in r and r[field] and r[field] not in seen,'source identity schema: '+member)
        seen.add(r[field]);out.append(dict(record=deepcopy(r),receipt=dict(member=HISTORY+member,
            identity_field=field,identity=r[field],data_row=i,row_sha256=a.n.l.d.h.f.rowhash(rr),
            member_sha256=sha(data),artifact_sha256=s['receipt']['sha256'])))
    return out


def inputs(s):
    nn=source(s,L1+'01_hsa3_canonical_nodes.csv','node_id')
    rr=[]
    for member,layer in a.n.l.LAYERS.items():
        part=source(s,L1+member,'relation_id')
        require(all(x['record']['layer']==layer for x in part),'relation layer mismatch')
        rr.extend(part)
    return dict(nodes=nn,relations=rr,necessities=source(s,L2+'01_parentage_necessity_human_decisions.csv','node_id'),
        proposals=source(s,L1+'10_parentage_necessity_audit.csv','node_id'),
        questions=source(s,L1+'09_hsa3_unresolved_deferred.csv','question_id'),
        seams=source(s,L1+'20_all_seams_preserved.csv','seam_id'),
        clauses=source(s,FG+'history/fg_prep/13_clause_evidence.csv','evidence_id'))


def textual(r):
    return r['textual'] is True and r['node_kind'] in ('TEXTUAL_NODE','TRANSITION_ANCHOR')


def semantics(relations):
    out=[]
    for x in relations:
        r=x['record']
        if r['layer']!='TEXTUAL_HIERARCHY':continue
        typ=r['relation_type'];direct=typ in DIRECT
        out.append(dict(relation_id=r['relation_id'],relation_type=typ,source_node=r['source_node'],target_node=r['target_node'],
            classification='DIRECT_MOTHER_EDGE' if direct else 'HIERARCHICAL_PLACEMENT_NOT_DIRECT_MOTHER' if typ in PLACEMENT else 'AMBIGUOUS_MOTHER_SEMANTICS',
            child_id=r[DIRECT[typ][0]] if direct else '',mother_id=r[DIRECT[typ][1]] if direct else '',
            rationale='Explicit direction in R4.3 parents(); accepted relation retained.' if direct else 'Excluded from R4.3 parents(); placement/closure is not an asserted mother.' if typ in PLACEMENT else 'No verified direct-mother semantics; review required.',
            schema_source='src/milal_r4_3_hierarchy_scaffold.py::parents; docs/R4_4_CONTRACT_0_1_SPEC.md::Relation proposal',
            original_record=deepcopy(r),provenance=x['receipt']))
    return out


def mother_index(edges):
    out={}
    for r in edges:out.setdefault(r['child_id'],set()).add(r['mother_id'])
    return {k:sorted(v) for k,v in out.items()}


def audit_nodes(s,inp,edges):
    parents=mother_index(edges);necess={r['record']['node_id']:r for r in inp['necessities']};out=[]
    for x in inp['nodes']:
        n=x['record'];ident=n['node_id'];old=n['original_record'];kind=n['node_kind'];human=necess.get(ident)
        rel={layer:[r['record']['relation_id'] for r in inp['relations'] if r['record']['layer']==layer and ident in (r['record']['source_node'],r['record']['target_node'])] for layer in a.n.l.LAYERS.values()}
        pp=parents.get(ident,[]);is_text=textual(n)
        if kind=='COMPOSITION_GROUP':cat=SM[2];reason='Explicit non-textual composition/group node.'
        elif kind=='ROLE_ALIAS':cat=SM[3];reason='Explicit canonical_textual_node alias; not another daughter.'
        elif kind=='TECHNICAL_ROOT':cat=SM[4];reason='Technical navigation only; not a textual root.'
        elif is_text and len(pp)==1:cat=SM[1];reason='One existing accepted direct mother, independently counted from relation semantics.'
        elif is_text and len(pp)>1:cat=SM[6];reason='Conflicting existing mothers require review; none selected.'
        elif is_text and (rel['TEXTUAL_HIERARCHY'] or n['structural_function'] in s['cfg']['clear_macro_functions']):
            cat=SM[0];reason='Recorded hierarchy participation or explicit macro-unit onset/introduction; proposed required under the instructed macro reading, pending Q8/JIN-Q0 and separate root adjudication.'
        else:cat=SM[6];reason='Evidence-only, ending/transition anchor without explicit hierarchy participation; daughter applicability not established. Not an exemption.'
        status={SM[0]:'NO_MOTHER_REQUIRES_REVIEW',SM[1]:'ALREADY_HAS_ONE_MOTHER',SM[2]:'EXEMPT_NON_TEXTUAL',SM[3]:'EXEMPT_ALIAS',SM[4]:'EXEMPT_TECHNICAL',SM[5]:'ROOT_STATUS_REQUIRES_REVIEW',SM[6]:'APPLICABILITY_UNRESOLVED'}[cat]
        ids=old.get('source_evidence_ids',old.get('source_provenance_ids',[]))
        clause_ids=[v for v in ids if isinstance(v,str) and v.startswith('BHSA2021:clause:')]
        if old.get('clause_node'):clause_ids=sorted(set(clause_ids+['BHSA2021:clause:'+str(old['clause_node'])]))
        atom_ids=[v for v in ids if isinstance(v,str) and v.startswith('BHSA2021:clause_atom:')]
        atom_ids+=['BHSA2021:clause_atom:'+str(v) for v in old.get('clause_atom_nodes',[])]
        linked=[c for c in inp['clauses'] if 'BHSA2021:clause:'+str(c['record']['clause_node']) in clause_ids]
        # Exact clause identities only, never join by reference or Hebrew surface.
        atom_ids+=['BHSA2021:clause_atom:'+str(v) for c in linked for v in c['record']['clause_atom_nodes']]
        out.append(dict(node_id=ident,canonical_node_id=n['canonical_textual_node'] or ident,node_kind=kind,
            textuality='TEXTUAL' if n['textual'] else 'TECHNICAL' if kind=='TECHNICAL_ROOT' else 'NON_TEXTUAL',
            actual_textual_node=is_text,reference=n['reference'],textual_span=dict(historical_start=old.get('reference_start'),historical_end=old.get('reference_end'),accepted_annotations=n['accepted_annotations']),
            clause_anchors=clause_ids,clause_atom_anchors=sorted(set(atom_ids)),anchor_status='SOURCE_RECORDED' if clause_ids or atom_ids else 'NOT_RECORDED',
            role_alias=kind=='ROLE_ALIAS',composition_group=kind=='COMPOSITION_GROUP',technical=kind=='TECHNICAL_ROOT',
            structural_function=n['structural_function'],existing_relations=rel,
            historical_parent_status=old.get('parentage_status','NOT_RECORDED'),
            historical_necessity=human['record']['researcher_necessity_status'] if human else 'NOT_RECORDED',
            historical_additional_parentage_review_required=human['record']['additional_parentage_review_required'] if human else None,
            applicability_category=cat,single_mother_applicability='REQUIRED' if cat in SM[:2] else 'EXEMPT' if cat in SM[2:5] else 'REVIEW_REQUIRED',
            single_mother_status=status,existing_direct_mother_count=len(pp),existing_direct_mother_ids=pp,
            additional_single_mother_review_required=is_text and cat in (SM[0],SM[5],SM[6]),
            applicability_review_required=cat==SM[6],root_status='UNADJUDICATED' if is_text else 'NOT_APPLICABLE',root_candidate=False,
            strict_jin_clause_hierarchy='SOURCE_CLAUSE_ANCHOR_ONLY; PARTICIPATION_UNADJUDICATED' if kind=='SOURCE_EVIDENCE_ANCHOR' else 'NOT_AN_ACTUAL_CLAUSE_REGISTRY_ROW',
            macro_textual_hierarchy='AUDIT_PROPOSAL_PENDING_Q8_JIN_Q0' if is_text else 'NOT_A_MACRO_DAUGHTER',
            rationale=reason,proposal_status='UNREVIEWED',human_judgment=False,
            original_record=deepcopy(n),provenance=x['receipt'],necessity_source=human,
            exact_native_clause_evidence=linked))
    return out


def crosswalk(nodes,inp):
    byid={r['node_id']:r for r in nodes};out=[]
    for x in inp['necessities']:
        h=x['record'];n=byid[h['node_id']]
        out.append(dict(node_id=n['node_id'],reference=n['reference'],historical_triage=h['original_proposal']['historical_triage'],
            historical_category=h['proposal_category'],historical_necessity=h['researcher_necessity_status'],
            historical_parent_status=h['historical_direct_parent'],historical_additional_parentage_review_required=h['additional_parentage_review_required'],
            applicability_category=n['applicability_category'],single_mother_applicability=n['single_mother_applicability'],
            actual_textual_node=n['actual_textual_node'],existing_direct_mother_count=n['existing_direct_mother_count'],existing_direct_mother_ids=n['existing_direct_mother_ids'],
            single_mother_status=n['single_mother_status'],additional_single_mother_review_required=n['additional_single_mother_review_required'],
            root_candidate=n['root_candidate'],original_necessity=deepcopy(h),provenance=x['receipt']))
    return out


def peers(nodes,relations):
    byid={n['node_id']:n for n in nodes};out=[]
    for x in relations:
        r=x['record']
        if r['layer']!='TEXTUAL_SAME_LEVEL' or r['relation_type']!='SAME_LEVEL_SIBLING':continue
        left,right=byid[r['source_node']],byid[r['target_node']];p,q=left['existing_direct_mother_ids'],right['existing_direct_mother_ids']
        out.append(dict(relation_id=r['relation_id'],source_id=left['node_id'],target_id=right['node_id'],source_mothers=p,target_mothers=q,
            consistency='CONSISTENT' if p and q and p==q else 'CONFLICT_REQUIRES_REVIEW' if p and q else 'PARENT_UNKNOWN_REVIEW_EVIDENCE_ONLY',
            accepted_parent_created=False,provenance=x['receipt']))
    return out


def candidates(nodes,sem,peer_rows,relations):
    byid={r['node_id']:r for r in nodes};out={}
    def add(child,parent,evidence,basis):
        n=byid[child];p=byid[parent]
        if not n['actual_textual_node'] or n['existing_direct_mother_count'] or not p['actual_textual_node'] or child==parent:return
        negatives=[x['record']['relation_id'] for x in relations if x['record']['layer']=='NEGATIVE_CONSTRAINT' and {x['record']['source_node'],x['record']['target_node']}=={child,parent}]
        # Scope-sensitive adjudication is deferred; conservatively withhold any pair with an explicit negative.
        if negatives:return
        key=(child,parent)
        row=out.setdefault(key,dict(candidate_id='JIN-C:'+sha((child+'::'+parent).encode())[:20],node_id=child,mother_candidate_id=parent,
            candidate_status='UNADJUDICATED',accepted_relation=False,evidence=[],basis=[],
            limitation='Candidate for later source-grounded review only; neither directness nor selection is established. Not an exhaustive linguistic search.',
            daughter_source=n['provenance'],mother_source=p['provenance']))
        row['evidence'].append(evidence);row['basis'].append(basis)
    for r in sem:
        if r['classification']=='HIERARCHICAL_PLACEMENT_NOT_DIRECT_MOTHER':
            add(r['source_node'],r['target_node'],dict(relation_id=r['relation_id'],provenance=r['provenance']),
                'ACCEPTED_BOUNDARY_CLOSURE' if r['relation_type']=='DIRECT_LOCAL_CLOSURE' else 'EXISTING_EXPLICIT_HIERARCHICAL_PLACEMENT')
    for r in peer_rows:
        if not r['source_mothers']:
            for parent in r['target_mothers']:add(r['source_id'],parent,dict(relation_id=r['relation_id'],provenance=r['provenance']),'ESTABLISHED_SAME_LEVEL_WITH_EXISTING_SIBLING_MOTHER')
    return [out[k] for k in sorted(out)]


def questions(s):
    old=json.loads(s['files']['18_contract_proposal.json'])['review_questions']
    revised=[
        'Retain the layered typed graph while requiring a single mother for each textual-hierarchy daughter?',
        'Preserve historical UNRESOLVED and necessity decisions, without treating parent-not-required as a final exemption for an applicable textual daughter?',
        *old[2:],
        'Apply the principle strictly to clause/clause_atom only, or also to anchored macro textual units?',
        'Perform whole-Job textual root selection through separate human adjudication?']
    return [dict(question_id='Q'+str(i),historical_question=old[i-1] if i<=7 else '',historical_review_status='UNREVIEWED' if i<=7 else 'NOT_APPLICABLE',
        revised_question=q,review_status='UNREVIEWED',researcher_answer='',change='REVISE_FOR_SINGLE_MOTHER' if i<=2 else 'PRESERVE_QUESTION' if i<=7 else 'ADD_SCOPE_OR_ROOT_QUESTION') for i,q in enumerate(revised,1)]


def counts(m):
    nn=m['nodes'];tt=[r for r in nn if r['actual_textual_node']];hh=m['crosswalk'];cc=m['candidates']
    stats=lambda rr:dict(mother_1=sum(r['existing_direct_mother_count']==1 for r in rr),mother_0=sum(r['existing_direct_mother_count']==0 for r in rr),mother_gt1=sum(r['existing_direct_mother_count']>1 for r in rr),root_candidate_review=sum(r['root_candidate'] for r in rr),applicability_unresolved=sum(r['applicability_category']==SM[6] for r in rr),single_mother_review=sum(r['additional_single_mother_review_required'] for r in rr))
    return dict(total_canonical_nodes=len(nn),node_kinds=dict(Counter(r['node_kind'] for r in nn)),textual_nodes=len(tt),
        textuality_true_including_aliases=sum(r['textuality']=='TEXTUAL' for r in nn),applicability=dict(Counter(r['applicability_category'] for r in nn)),
        textual=stats(tt),historical_57=dict(total=len(hh),exempt_non_textual=sum(r['applicability_category']==SM[2] for r in hh),exempt_alias=sum(r['applicability_category']==SM[3] for r in hh),actual_textual=sum(r['actual_textual_node'] for r in hh),**stats(hh)),
        existing_direct_mother_edges=len(m['mothers']),candidate_pool=dict(audited_zero_mother_textual_nodes=len(m['zero']),candidate_count=len(cc),nodes_with_candidates=len({r['node_id'] for r in cc}),zero_candidate_nodes=sum(not any(c['node_id']==r['node_id'] for c in cc) for r in m['zero'])),
        same_level_consistency=dict(Counter(r['consistency'] for r in m['peers'])),new_textual_parent_edge_count=len(m['new_parent_edges']),
        new_node_specific_human_judgment_count=len(m['node_judgments']),new_methodological_human_judgment_count=len(m['methodological_judgments']))


def derive(s):
    inp=inputs(s);sem=semantics(inp['relations']);edges=[deepcopy(r) for r in sem if r['classification']=='DIRECT_MOTHER_EDGE']
    nn=audit_nodes(s,inp,edges);pp=peers(nn,inp['relations']);cc=candidates(nn,sem,pp,inp['relations'])
    zero=[]
    for n in nn:
        if n['actual_textual_node'] and n['existing_direct_mother_count']==0:
            zero.append(dict(**deepcopy(n),candidate_count=sum(r['node_id']==n['node_id'] for r in cc),
                candidate_search_scope='EXPLICIT_FROZEN_PLACEMENT_CLOSURE_AND_SAME_LEVEL_WITH_KNOWN_MOTHER',
                candidate_limitation='No exhaustive morphology/coreference matching; existing source anchors retained for later linguistic adjudication. Zero does not mean no possible mother.'))
    m=dict(nodes=nn,semantics=sem,mothers=edges,crosswalk=crosswalk(nn,inp),peers=pp,candidates=cc,zero=zero,
        supersession=questions(s),inputs=inp,historical=deepcopy(s['files']),commit=deepcopy(s['commit']),receipt=deepcopy(s['receipt']),
        new_parent_edges=[],node_judgments=[],consumer_implementations=[],participant_arc='UNADJUDICATED',readiness=READY,
        methodological_judgments=[dict(judgment_id='JIN_SINGLE_MOTHER_PRINCIPLE_ADOPTED_FOR_REVIEW',authority='EXPLICIT_RESEARCHER_METHODOLOGICAL_DECISION',
            source_request_sha256=sha(s['request']),source_sections=['1','17'],scope='TEXTUAL_HIERARCHY_CONTRACT_PRINCIPLE_ONLY',individual_mother_assignments=[])])
    m['summary']=counts(m);m['reports']=reports(m,s);return m


def reports(m,s):
    node=next(r for r in m['nodes'] if r['node_id']=='H:HSA012')
    root=['# Textual root / applicability review','','JIN-Q0: Strict clause/clause_atom hierarchy, or also anchored macro textual units?',
          'JIN-Q1: Should a single actual textual clause/unit be adjudicated as the whole-Job canonical root?',
          'JIN-Q2: Job 1:1, or a separate source-grounded root-selection audit?','',
          'All three: UNREVIEWED. Researcher answers: blank. No root selected.',
          'JOB_BOOK remains technical only. Absence of a mother is not evidence of root status.',
          'No existing canonical node is explicitly supplied as a textual root candidate; SM6 count is zero.',
          'This is a registry gap, not a finding that the text has no root. Job 1:1 native clause evidence exists in FG-PREP but was not promoted to a canonical textual unit.',
          'STRICT_JIN_CLAUSE_HIERARCHY is not implemented by this macro registry. Evidence-only clause anchors stay SM7, not new daughters.',
          'MILAL_MACRO_TEXTUAL_HIERARCHY categories are audit proposals pending Q8/JIN-Q0; no new unit or clause-to-macro equivalence is asserted.']
    packet=['# Revised R4.4 contract review','','Readiness: '+m['readiness'],'','One methodological principle is researcher supplied; individual applicability proposals and Q1–Q9 remain UNREVIEWED.','',
            '```json',json.dumps(counts(m),ensure_ascii=False,indent=2),'```','']
    for q in m['supersession']:packet += [q['question_id']+': '+q['revised_question'],'','Review status: '+q['review_status'],'Researcher answer: '+q['researcher_answer'],'']
    packet += ['See 09_root_scope_review.md for JIN-Q0/Q1/Q2 and 02/03 for every node and historical necessity decision.',
               'P3 is not six aliases: the canonical speech representatives remain distinct from their three role aliases.',
               'First approve the applicability scope. Then review only flagged actual textual nodes, resolving SM7 participation before assigning any mother.']
    case=['# Job 2:11 — H:HSA012','','Historical necessity: '+node['historical_necessity'],
          'layered_representation_parent_needed = false (historical human judgment).',
          'textual_hierarchy_single_mother_question = OPEN.',
          'Current audit proposal: '+node['applicability_category']+' / '+node['single_mother_applicability'],
          'Existing mothers: '+json.dumps(node['existing_direct_mother_ids'])+'; new assigned mothers: [].',
          'PARAGRAPH_ONSET, FRIENDS_ARRIVAL / PARTICIPANT_INTRODUCTION, NOT_WITHIN_SECOND_TESTING_SCENE and OPENING_NARRATIVE_COMPLEX membership remain frozen.',
          'No 1:1, 2:1, 2:10, 3:1 or other mother is assigned. The explicit macro-unit classification supports SM1 as an audit proposal; scope/root review remains pending.',
          'Full original record, human necessity decision and exact receipts are retained in 02/03.']
    scope=['# Next scope','','Current readiness: '+m['readiness'],
           'A. Review Q8/JIN-Q0 and JIN-Q1/Q2; authorize a separate TEXTUAL ROOT AUDIT if needed.',
           'B. SINGLE-MOTHER PARENTAGE ADJUDICATION may subsequently cover only the actual textual nodes flagged additional_single_mother_review_required=true.',
           'Resolve applicability for SM7 first. Do not reopen all 57 indiscriminately. Source-evidence anchors require a separate clause-scope decision, not macro mother assignment.',
           'Review-node IDs: '+json.dumps([r['node_id'] for r in m['nodes'] if r['additional_single_mother_review_required']]),
           'Candidate rows remain UNADJUDICATED. Explicit placement/closure and sibling-with-known-mother evidence are only a conservative starting pool, not a complete linguistic search.',
           'No nearest-node, chapter, speaker-only, theme-only, group-membership or technical-root candidate rule is used.',
           'Participant arc remains UNADJUDICATED; R4.4 consumer remains NOT IMPLEMENTED.']
    out=deepcopy(s['documents'])
    for name,lines in [('08_job_2_11_single_mother_case.md',case),('09_root_scope_review.md',root),('11_revised_r4_4_contract_review_packet.md',packet),('12_single_mother_next_scope.md',scope)]:out[name]=('\n'.join(lines)+'\n').encode()
    return out


def digest(m):
    return sha(util.json_bytes({k:v for k,v in m.items() if k not in ('reports','historical','rerun_digest')}))


def build(s):
    m=derive(s);m['rerun_digest']=digest(derive(s));return m


def gates(m,s):
    expected=derive(s);nn=m['nodes'];byid={r['node_id']:r for r in nn};check={}
    eq=lambda key:m[key]==expected[key]
    historical=lambda prefix:{k:v for k,v in m['historical'].items() if k.startswith(prefix)}=={k:v for k,v in s['files'].items() if k.startswith(prefix)}
    subset=lambda pred:[r for r in nn if pred(r)]==[r for r in expected['nodes'] if pred(r)]
    check['BASELINE_EXACT']=eq('commit') and m['commit']['verified_commit']==s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    check['INPUT_VERIFIED']=eq('receipt') and m['receipt']['members']==len(s['files'])
    check['CONTRACT_ARTIFACT_PRESERVED']=m['historical']==s['files']
    check['LAYER02_ARTIFACT_PRESERVED']=historical(L2)
    check['HISTORICAL_57_PRESERVED']=eq('crosswalk') and len(m['crosswalk'])==s['cfg']['regression']['historical_parents'] and all(r['historical_parent_status']=='UNRESOLVED' and r['historical_additional_parentage_review_required'] is False for r in m['crosswalk'])
    check['SEAMS_FROZEN']=m['inputs']['seams']==expected['inputs']['seams'] and len(m['inputs']['seams'])==s['cfg']['regression']['seams'] and all(r['record']['status']=='FROZEN' for r in m['inputs']['seams'])
    check['ANA_PRESERVED']=m['inputs']['questions']==expected['inputs']['questions'] and m['inputs']['relations']==expected['inputs']['relations']
    check['HISTORICAL_Q_UNREVIEWED']=m['historical']['13_r4_4_contract_review_packet.md']==s['files']['13_r4_4_contract_review_packet.md'] and all(r['historical_review_status']=='UNREVIEWED' for r in m['supersession'][:7])
    check['ONE_METHODOLOGICAL_DECISION']=eq('methodological_judgments') and len(m['methodological_judgments'])==1 and m['reports']['01_jin_single_mother_methodological_addendum.md']==s['documents']['01_jin_single_mother_methodological_addendum.md']
    check['ALL_NODES_CLASSIFIED']=eq('nodes') and len({r['node_id'] for r in nn})==len(nn) and all(r['applicability_category'] in SM for r in nn)
    for key,kind,category in [('GROUPS_EXEMPT','COMPOSITION_GROUP',SM[2]),('ALIASES_EXEMPT','ROLE_ALIAS',SM[3]),('TECHNICAL_EXEMPT','TECHNICAL_ROOT',SM[4])]:
        ids={x['record']['node_id'] for x in expected['inputs']['nodes'] if x['record']['node_kind']==kind}
        check[key]=bool(ids) and all(i in byid and byid[i]['applicability_category']==category for i in ids)
    check['TEXTUAL_COUNTS_SEPARATE']=m['summary']==counts(m) and subset(lambda r:r['actual_textual_node'])
    targets=[r['mother_candidate_id'] for r in m['candidates']]+[r['mother_id'] for r in m['mothers']]
    check['NO_NON_TEXTUAL_MOTHER']=all(p in byid and byid[p]['actual_textual_node'] for p in targets)
    check['NO_TECHNICAL_MOTHER']=all(p in byid and not byid[p]['technical'] for p in targets)
    check['NO_PARENT_CREATED']=eq('mothers') and m['new_parent_edges']==[] and m['inputs']['relations']==expected['inputs']['relations']
    check['NO_NEAREST_HEURISTIC']=eq('candidates') and all(set(r['basis'])<={'ACCEPTED_BOUNDARY_CLOSURE','EXISTING_EXPLICIT_HIERARCHICAL_PLACEMENT','ESTABLISHED_SAME_LEVEL_WITH_EXISTING_SIBLING_MOTHER'} for r in m['candidates'])
    check['NO_COMPOSITION_AS_PARENT']=eq('semantics') and all(r['relation_type'] in DIRECT for r in m['mothers'])
    case=byid.get('H:HSA012',{})
    check['JOB_2_11_REOPENED']=case.get('additional_single_mother_review_required') is True and case.get('historical_necessity')=='DIRECT_TEXTUAL_PARENT_NOT_REQUIRED' and case.get('single_mother_applicability') in ('REQUIRED','REVIEW_REQUIRED')
    check['JOB_2_11_NO_MOTHER']=case.get('existing_direct_mother_ids')==[] and not any(r['child_id']=='H:HSA012' for r in m['mothers']+m['new_parent_edges'])
    check['DIRECT_MOTHER_SEMANTICS']=eq('semantics') and eq('mothers') and all(r['existing_direct_mother_ids']==mother_index(m['mothers']).get(r['node_id'],[]) for r in nn)
    check['MULTIPLE_MOTHER_CONFLICTS_REPORTED']=m['summary']['textual']['mother_gt1']==counts(m)['textual']['mother_gt1']
    check['ZERO_MOTHER_COVERAGE']=eq('zero') and {r['node_id'] for r in m['zero']}=={r['node_id'] for r in nn if r['actual_textual_node'] and r['existing_direct_mother_count']==0}
    check['ROOT_NOT_SELECTED']=all(r['root_candidate'] is False and r['root_status']==('UNADJUDICATED' if r['actual_textual_node'] else 'NOT_APPLICABLE') for r in nn) and m['reports']['09_root_scope_review.md']==expected['reports']['09_root_scope_review.md']
    check['CANDIDATES_UNADJUDICATED']=all(r['candidate_status']=='UNADJUDICATED' and r['accepted_relation'] is False for r in m['candidates'])
    check['REVISED_Q1_Q9_UNREVIEWED']=eq('supersession') and len(m['supersession'])==9 and all(r['review_status']=='UNREVIEWED' and not r['researcher_answer'] for r in m['supersession'])
    check['READINESS_BLOCKED']=m['readiness']==READY
    check['NO_CONSUMER']=m['consumer_implementations']==[] and not list((ROOT/'src').glob('*r4_4*.py')) and not list((ROOT/'scripts').glob('*r4_4*'))
    check['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED' and historical(L2+'06_remaining_research_scope.md')
    check['NO_NODE_JUDGMENTS']=m['node_judgments']==[] and all(r['human_judgment'] is False and r['proposal_status']=='UNREVIEWED' for r in nn)
    check['SAME_LEVEL_CONSISTENCY']=eq('peers') and all(r['accepted_parent_created'] is False for r in m['peers'])
    check['PROVENANCE_EXACT']=all(r['provenance']==x['receipt'] and r['original_record']==x['record'] for r,x in zip(nn,expected['inputs']['nodes'])) and len(nn)==len(expected['inputs']['nodes'])
    check['FROZEN_PINS']=len(s['pins'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'][r['path']] for r in s['pins'])
    check['REQUEST_EXACT']=sha(s['request'])==s['cfg']['source_request']['sha256']
    check['REPORTS_FAITHFUL']=m['reports']==reports(m,s)
    check['DETERMINISTIC_PAYLOAD']=m['rerun_digest']==digest(m)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in check.items()]


def serialize(m,s):
    gg=gates(m,s);require(all(r['status']=='PASS' for r in gg),str([r for r in gg if r['status']!='PASS']))
    files={HISTORY+k:v for k,v in m['historical'].items()};files.update(m['reports'])
    for key,name in TABLES.items():
        fields=['candidate_id','node_id','mother_candidate_id','candidate_status','accepted_relation','evidence','basis','limitation','daughter_source','mother_source'] if key=='candidates' else None
        files[name]=util.csv_bytes(m[key],fields) if fields else util.csv_bytes(m[key])
    files['15_methodological_human_decision.json']=util.json_bytes(m['methodological_judgments'])
    files['16_researcher_source.txt']=s['request'];files['17_current_readiness.txt']=(m['readiness']+'\n').encode()
    files['18_source_input_inventory.json']=util.json_bytes({key:[x['receipt'] for x in vv] for key,vv in m['inputs'].items()})
    files['90_run_metadata.json']=util.json_bytes(dict(version='R4.4-CONTRACT.JIN.0.1',status='PASS',mode=s['mode'],gate_count=len(gg)+1,
        counts=counts(m),readiness=m['readiness'],baseline_commit=m['commit'],input_receipt=m['receipt'],frozen_receipts=s['pins'],
        config_sha256=sha(CONFIG.read_bytes()),audit_harness_sha256=sha(Path(__file__).read_bytes()),request_sha256=sha(s['request']),
        document_hashes={k:sha(v) for k,v in s['documents'].items()},rerun_payload_sha256=m['rerun_digest'],r44_consumer_implemented=False,
        release_checks='Full regression skip-zero and independent ZIP equality are external release gates, not inferred from this run.'))
    a.n.l.f.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['13_gates.csv']=util.csv_bytes(gg);a.n.l.f.seal(files);require(util.manifest_ok(files),'output manifest');return files


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--self-test',action='store_true');ap.add_argument('--archive');ap.add_argument('--out',required=True)
    args=ap.parse_args(argv);s=load(args.self_test,args.archive);m=build(s);files=serialize(m,s)
    require(a.n.l.d.h.f.a.prep.r43.frozen_receipts(s['cfg'])==s['pins'],'frozen files changed during run')
    require(all((ROOT/p).read_bytes()==s['documents'][k] for k,p in DOCUMENTS.items()),'audit documents changed during run')
    if not args.self_test:require(sha((Path(args.archive) if args.archive else ROOT/s['cfg']['archive']['path']).read_bytes())==s['receipt']['sha256'],'upstream changed during run')
    a.n.l.d.h.f.a.prep.publish(files,args.out);out=Path(args.out).resolve();zp=out.with_name(out.name+'_results.zip')
    msg='R4.4-CONTRACT.JIN.0.1 AUDIT PASS\n'+s['mode']+'\nZIP SHA256 '+sha(zp.read_bytes())+'\n'
    out.with_name(out.name+'_run.log').write_text(msg,encoding='utf-8');print(msg);print(json.dumps(counts(m),ensure_ascii=False,indent=2));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
