"""Lossless HSA3 layer integration and UNREVIEWED parentage-necessity proposals."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_hsa3_fg_final_adjudication as f

ROOT, sha, rows, util, d = f.ROOT, f.sha, f.rows, f.util, f.d
REVIEW_FIELDS = f.REVIEW_FIELDS
CONFIG = ROOT / 'config/hsa3_layer_0_1_job.json'
HISTORY = 'history/hsa3_fg/'
NODES, EDGES, UNRESOLVED, SEAMS, ANA = (f.HISTORY+x for x in (f.NODES,f.EDGES,f.UNRESOLVED,f.SEAMS,f.ANA))
PREP = SEAMS.rsplit('/',1)[0]+'/'
TRIAGE, ALIASES = PREP+'01_unresolved_row_triage.csv', PREP+'02_same_textual_locus_role_audit.csv'
ABC_PREFIX = f.HISTORY+f.p.HISTORY
DE_PREFIX = ABC_PREFIX+f.a.HISTORY
ACTIONS = [(ABC_PREFIX+'02_hsa3_abc_relation_actions.csv','HSA3-A/C'),(DE_PREFIX+'02_hsa3_de_relation_actions.csv','HSA3-D/E'),('02_hsa3_fg_relation_actions.csv','HSA3-F/G')]
GROUPS = [(ABC_PREFIX+'03_hsa3_abc_composition_groups.csv','HSA3-A/C'),('03_hsa3_fg_composition_groups.csv','HSA3-F/G')]
P2='P2_DIRECT_PARENT_NOT_REQUIRED_NON_TEXTUAL_GROUP'
P3='P3_DIRECT_PARENT_NOT_REQUIRED_ROLE_ALIAS'
P4='P4_LOCAL_RELATION_SUFFICIENT'
P5='P5_CONTAINER_MEMBERSHIP_SUFFICIENT'
P6='P6_GLOBAL_LAYER_RELATION_SUFFICIENT'
P7='P7_GENUINELY_UNRESOLVED_AFTER_LAYERED_REVIEW'
CATEGORIES=(P2,P3,P4,P5,P6,P7)
STATEMENTS=[
 'A direct textual parent is not a mandatory property of every MILAL node.',
 'Unresolved parentage must be distinguished from parentage that is not required by the analytical layer.',
 'Composition membership, textual hierarchy, transition, and rhetorical overlay are independent relation dimensions.',
 'Therefore the number of unresolved R4.3 parent fields is not itself a measure of structural incompleteness.',
 'NO DIRECT TEXTUAL PARENT ≠ STRUCTURAL INFORMATION MISSING.']


def require(ok,message):
    if not ok:raise ValueError('HSA3-LAYER.0.1 STOP: '+message)


def locate(s,member,field,ident):
    matches=[(i,r) for i,r in enumerate(d.h.raw_rows(s['files'][member]),1) if r[field]==ident]
    require(len(matches)==1,'exact source identity '+str(ident))
    i,r=matches[0]
    return dict(member=HISTORY+member,data_row=i,identity_field=field,identity=ident,row_sha256=d.h.f.rowhash(r),
                member_sha256=sha(s['files'][member]),artifact_sha256=s['receipt']['sha256'])


def input_audit(files,cfg,digest,synthetic=False):
    require(util.manifest_ok(files) and all(r['valid'] for r in d.h.nested_manifests(files)),'input manifests')
    require(synthetic or (digest==cfg['archive']['sha256'] and len(files)==cfg['archive']['members']),'input SHA/count')
    meta=json.loads(files['90_run_metadata.json']);gg=rows(files['10_gates.csv'])
    require(meta['version']=='HSA3-F/G' and meta['status']=='PASS' and not meta['r44_started'],'input stage')
    require(meta['mode']==('SYNTHETIC_ONLY' if synthetic else 'FROZEN_REAL_ARTIFACT_ADJUDICATION'),'input mode')
    require(len(gg)==meta['gate_count'] and all(g['status']=='PASS' for g in gg),'input gates')
    ss=rows(files['07_hsa3_all_seams_status.csv'])
    require([r['seam_id'] for r in ss]==['SEAM_'+x for x in 'ABCDEFG'] and all(r['status']=='FROZEN' for r in ss),'all seams frozen')
    tt=rows(files[TRIAGE]);uu=rows(files[UNRESOLVED])
    require(dict(Counter(r['triage_category'] for r in tt))==cfg['regression']['triage'],'historical triage counts')
    require(len(tt)==len(uu)==cfg['regression']['unresolved'] and {r['unresolved_node_id'] for r in tt}=={r['node_id'] for r in uu},'historical unresolved coverage')
    require(all(r['direct_parent']=='UNRESOLVED' for r in uu),'historical parent states')
    return dict(sha256=digest,members=len(files),synthetic=synthetic,manifests=d.h.nested_manifests(files))


def load(self_test=False,archive=None):
    cfg=json.loads(CONFIG.read_bytes());commit=d.baseline_receipt(cfg)
    frozen=d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['actual']==r['expected'] for r in frozen),'frozen pins')
    request=(ROOT/cfg['source_request']['path']).read_bytes()
    require(sha(request)==cfg['source_request']['sha256'],'request hash')
    if self_test:
        ps=f.load(True);files=f.serialize(f.build(ps),ps);digest=sha(files['99_manifest_sha256.csv'])
    else:
        b=(Path(archive) if archive else ROOT/cfg['archive']['path']).read_bytes();digest=sha(b)
        require(digest==cfg['archive']['sha256'],'input ZIP hash')
        files=d.h.f.a.prep.r43.h1.src.archive(b,digest,mr1=True)['files']
    return dict(cfg=cfg,commit=commit,frozen=frozen,request=request,files=files,
        receipt=input_audit(files,cfg,digest,self_test),mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_LAYER_INTEGRATION')


def role_crosswalk(s):
    nn={r['node_id']:r for r in rows(s['files'][NODES])};result=[]
    for r in rows(s['files'][ALIASES]):
        require(r['identity_basis']=='EXPLICIT_RESEARCHER_PAIR_AND_SHARED_EXACT_EVIDENCE' and r['shared_source_evidence_ids'],'unverified role identity')
        canonical=[i for i in r['node_ids'] if nn[i]['structural_function']=='SPEECH_UNIT_ONSET']
        require(len(canonical)==1,'canonical speech-role ambiguity')
        for ident in r['node_ids']:
            require(set(r['shared_source_evidence_ids'])<=set(nn[ident]['source_evidence_ids']),'role source mismatch')
            result.append(dict(node_id=ident,canonical_textual_node=canonical[0],is_role_alias=ident!=canonical[0],
                same_textual_locus=r['locus'],paired_node_ids=r['node_ids'],source_judgments=r['judgments'],
                identity_basis=r['identity_basis'],shared_source_evidence_ids=r['shared_source_evidence_ids'],
                separate_parentage_adds_information='NO_SEPARATE_ROLE_COPY_PROPOSED; CANONICAL_PLACEMENT_REVIEW_RETAINED',
                historical_records_merged=False,source_link=locate(s,ALIASES,'locus',r['locus'])))
    return result


def relations(s):
    result=[];ids=set();confirmations=[]
    def add(r,ident,member,field,source_id,stage):
        require(ident not in ids,'duplicate canonical relation ID '+ident);ids.add(ident)
        typ=r['relation_type'];require(typ in s['cfg']['layer_map'],'unmapped relation type '+typ)
        authority=r.get('authorities',r.get('authority',r.get('source_authority','RESEARCHER_SUPPLIED')))
        authority_list=authority if isinstance(authority,list) else [authority]
        origin='AUTOMATIC_TECHNICAL' if authority_list==['TECHNICAL_ONLY'] else 'AUTOMATIC_DERIVED_FROM_HUMAN' if 'HUMAN_RELATION_DERIVED' in authority_list else 'HUMAN_ACCEPTED_SOURCE'
        result.append(dict(relation_id=ident,relation_type=typ,layer=s['cfg']['layer_map'][typ],
            source_node=r.get('source_node',''),target_node=r.get('target_node',''),source_ref=r.get('source_ref',''),
            target_ref=r.get('target_ref',''),scope_ref=r.get('scope_ref',''),source_stage=stage,
            source_authority=authority,
            integration_operation='AUTOMATIC_LOSSLESS_PROJECTION',human_or_automatic=origin,
            frozen_status='FROZEN_SOURCE',source_status=r.get('status','ACCEPTED_SOURCE'),original_dimension=r.get('dimension',r.get('relation_dimension','')),
            membership_position=r.get('membership_position',''),original_record=deepcopy(r),
            provenance=[locate(s,member,field,source_id)],new_relation=False))
    for r in rows(s['files'][EDGES]):add(r,r['edge_id'],EDGES,'edge_id',r['edge_id'],'R4.3 / HSA1-HSA2-F')
    for member,stage in ACTIONS:
        for r in rows(s['files'][member]):
            if r['action'] in ('CREATED','NEGATIVE_CONSTRAINT_CREATED'):
                add(r,r['canonical_relation_id'],member,'action_id',r['action_id'],stage)
            elif r['action']=='CONFIRMED_EXISTING':confirmations.append((member,r))
    byid={r['relation_id']:r for r in result}
    for member,r in confirmations:
        ident=r['canonical_relation_id'];require(ident in byid,'confirmation without canonical relation')
        target=byid[ident]
        require((target['source_node'],target['target_node'],target['relation_type'])==(r['source_node'],r['target_node'],r['relation_type']),'confirmation semantic mismatch')
        target['provenance'].append(locate(s,member,'action_id',r['action_id']))
    for r in rows(s['files'][ANA]):
        if r['status']=='ACCEPTED':add(r,r['judgment_id'],ANA,'review_question_id',r['review_question_id'],'HSA3-ANA.0.3')
    return sorted(result,key=lambda r:r['relation_id'])


def nodes(s,rolemap,rr):
    roles={r['node_id']:r for r in rolemap};out=[]
    for r in rows(s['files'][NODES]):
        ident=r['node_id'];nt=r['node_type'];fn=r['structural_function']
        kind='COMPOSITION_GROUP' if fn=='NON_TEXTUAL_GROUP' else 'TECHNICAL_ROOT' if nt=='TECHNICAL_ROOT' else 'ROLE_ALIAS' if roles.get(ident,{}).get('is_role_alias') else 'TRANSITION_ANCHOR' if nt=='TRANSITION_UNIT' else 'TEXTUAL_NODE'
        out.append(dict(node_id=ident,node_kind=kind,textual=kind not in ('COMPOSITION_GROUP','TECHNICAL_ROOT'),
            canonical_textual_node=roles.get(ident,{}).get('canonical_textual_node',ident if kind not in ('COMPOSITION_GROUP','TECHNICAL_ROOT') else ''),
            structural_function=fn,reference=r['reference_start'],source_stage='R4.3 / HSA1-HSA2-F',
            source_authority=r['authority'],frozen_status='FROZEN_SOURCE',new_structural_node=False,
            original_record=deepcopy(r),provenance=[locate(s,NODES,'node_id',ident)]))
    for member,stage in GROUPS:
        for r in rows(s['files'][member]):
            out.append(dict(node_id=r['group_id'],node_kind='COMPOSITION_GROUP',textual=False,canonical_textual_node='',
                structural_function=r['node_type'],reference=r['span_start']+'–'+r['span_end'],source_stage=stage,
                source_authority=r['authority'],frozen_status='FROZEN_SOURCE',new_structural_node=False,
                original_record=deepcopy(r),provenance=[locate(s,member,'group_id',r['group_id'])]))
    known={r['node_id'] for r in out}
    # Source evidence anchors are already used by frozen FG constraints; no boundary nodes are invented.
    missing={r[k] for r in rr for k in ('source_node','target_node') if r[k] and r[k] not in known}
    evidence={r['original_record']['evidence_id']:r for r in rows(s['files']['11_hsa3_fg_evidence_links.csv'])}
    require(missing<=set(evidence),'unknown relation endpoint')
    for ident in sorted(missing):
        r=evidence[ident];c=r['original_record']
        out.append(dict(node_id=ident,node_kind='SOURCE_EVIDENCE_ANCHOR',textual=False,canonical_textual_node='',
            structural_function='EVIDENCE_ONLY_NOT_BOUNDARY',reference=c['reference'],source_stage='HSA3-FG-PREP / HSA3-F/G',
            source_authority='SOURCE_NODE_EVIDENCE',frozen_status='FROZEN_SOURCE',new_structural_node=False,
            original_record=deepcopy(c),provenance=[locate(s,'11_hsa3_fg_evidence_links.csv','source_identity',ident)]))
    require(len({r['node_id'] for r in out})==len(out),'duplicate node identity')
    byid={r['node_id']:r for r in out}
    for n in out:n['accepted_annotations']=[]
    # Keep later accepted human labels/spans alongside the frozen R4.3 record.
    # They do not overwrite the original function or create another unit.
    for member,stage in [(ABC_PREFIX+'12_hsa3_abc_unit_annotations.csv','HSA3-A/C'),('12_hsa3_fg_span_annotations.csv','HSA3-F/G')]:
        for r in rows(s['files'][member]):
            require(r['node_id'] in byid,'annotation without canonical node')
            link=locate(s,member,'node_id',r['node_id'])
            byid[r['node_id']]['accepted_annotations'].append(dict(source_stage=stage,original_record=deepcopy(r),source_link=link))
            byid[r['node_id']]['provenance'].append(link)
    member=DE_PREFIX+'14_researcher_decisions.json';preserve=json.loads(s['files'][member])['preserve']
    require(preserve['group'] in byid,'D/E group scope identity')
    byid[preserve['group']]['accepted_annotations'].append(dict(source_stage='HSA3-D/E',
        original_record=dict(group_id=preserve['group'],group_scope=preserve['group_scope']),
        source_json_member=HISTORY+member,json_pointer='/preserve',member_sha256=sha(s['files'][member]),artifact_sha256=s['receipt']['sha256']))
    return sorted(out,key=lambda r:r['node_id'])


def composition_groups(nn,rr):
    result=[]
    for n in nn:
        if n['node_kind']!='COMPOSITION_GROUP':continue
        mm=sorted([r for r in rr if r['relation_type']=='GROUP_MEMBER_OF' and r['target_node']==n['node_id']],key=lambda r:int(r['membership_position']))
        result.append(dict(group_id=n['node_id'],textual=False,node_layer='COMPOSITION_GROUPING',original_record=n['original_record'],
            members=[r['source_node'] for r in mm],ordered_membership=[dict(node_id=r['source_node'],position=r['membership_position'],relation_id=r['relation_id']) for r in mm],
            source_stage=n['source_stage'],provenance=n['provenance'],parentage_necessity_proposal='NOT_REQUIRED_FOR_NON_TEXTUAL_LAYER',proposal_status='UNREVIEWED',
            qualification='Layer audit only; no historical unresolved parent is resolved.'))
    return result


def unresolved(s):
    rr=[dict(question_id='PARENT:'+r['node_id'],question_kind='HISTORICAL_DIRECT_PARENT',node_id=r['node_id'],status='UNRESOLVED',
        original_record=deepcopy(r),source_stage='R4.3',provenance=[locate(s,UNRESOLVED,'node_id',r['node_id'])]) for r in rows(s['files'][UNRESOLVED])]
    rr += [dict(question_id=r['review_question_id'],question_kind='DEFERRED_OVERLAY',node_id='',status=r['status'],original_record=deepcopy(r),
        source_stage='HSA3-ANA.0.3',provenance=[locate(s,ANA,'review_question_id',r['review_question_id'])]) for r in rows(s['files'][ANA]) if r['status']!='ACCEPTED']
    return rr


def proposals(s,nn,rr,roles):
    bynode={r['node_id']:r for r in nn};byrole={r['node_id']:r for r in roles}
    triage={r['unresolved_node_id']:r for r in rows(s['files'][TRIAGE])}
    seams={r['seam_id']:r for r in rows(s['files']['07_hsa3_all_seams_status.csv'])}
    result=[]
    for old in rows(s['files'][UNRESOLVED]):
        ident=old['node_id'];node=bynode[ident];tr=triage[ident]
        incident=[r for r in rr if ident in (r['source_node'],r['target_node']) and r['layer']!='TECHNICAL_NAVIGATION']
        members=[r for r in incident if r['source_node']==ident and r['relation_type']=='GROUP_MEMBER_OF']
        peers=[r for r in incident if r['layer']=='TEXTUAL_SAME_LEVEL']
        local=[r for r in incident if r['relation_type'] in ('CHILD_OF','CONTINUES_WITHIN','HIERARCHICALLY_ABOVE','NO_BOUNDARY','DIRECT_LOCAL_CLOSURE') or (r['source_node']==ident and r['relation_type']=='TERMINATES_ENCLOSING_GROUP')]
        transitions=[r for r in incident if r['layer']=='TRANSITION']
        negatives=[r for r in incident if r['layer']=='NEGATIVE_CONSTRAINT']
        # A group transition can support layer placement, not a synthesized parent edge.
        group_transition=[r for r in rr if r['layer']=='TRANSITION' and any(mm['target_node'] in (r['source_node'],r['target_node']) for mm in members)]
        special=[r for r in incident if r['relation_type'] in ('NARRATIVE_INTRODUCTION','TERMINATES_ENCLOSING_GROUP')]
        historical=tr['triage_category'];seam=seams[tr['controlling_case_id']]
        if node['node_kind']=='COMPOSITION_GROUP':
            category=P2;basis='NON_TEXTUAL_SCHEMA';rationale='Schema identifies a non-textual group; adding a textual parent would conflate relation dimensions.'
        elif ident in byrole:
            category=P3;basis='EXPLICIT_ROLE_PAIR';rationale='Explicit paired roles share exact evidence. Do not require two independent parent assignments; keep canonical speech placement and both source records.'
        elif historical=='LOCAL_RELATION_ALREADY_CONSTRAINS_STRUCTURE' and local:
            category=P4;basis='ACCEPTED_TYPED_LOCAL_RELATIONS';rationale='Existing typed local placement/closure constrains this record. Proposal does not reinterpret continuation, closure or no-boundary as CHILD_OF.'
        elif historical=='KNOWN_CONTAINER_BUT_DIRECT_PARENT_UNRESOLVED' and members and peers and node['structural_function']=='SPEECH_UNIT_ONSET':
            category=P5;basis='MEMBERSHIP_PLUS_PEERS_PLUS_FUNCTION';rationale='Accepted membership, speech-onset function and peer relations already provide layered placement. No nearest-onset parent is needed by this audit rule.'
        elif historical=='TRUE_GLOBAL_SEAM' and seam['status']=='FROZEN' and (peers or local or transitions or special or group_transition):
            category=P6;basis='FROZEN_SEAM_WITH_INDEPENDENT_TYPED_SUPPORT';rationale='Frozen global decision plus independent typed local/peer/introduction/terminal/transition evidence supports layer placement, without assigning a direct parent.'
        else:
            category=P7;basis='CONSERVATIVE_REVIEW_REMAINDER';rationale='No configured sufficiency rule is supported. Ask whether an exact textual parent is needed; this is not a finding that one must exist.'
        result.append(dict(node_id=ident,reference=old['reference'],historical_triage=historical,initial_category='P1_GENUINE_TEXTUAL_PARENTAGE_QUESTION',
            proposed_category=category,proposal_kind='AUDIT_PROPOSAL',proposal_status='UNREVIEWED',human_judgment=False,
            direct_parent='UNRESOLVED',direct_parent_resolved=False,necessity_rule=basis,rationale=rationale,
            node_kind=node['node_kind'],textual=node['textual'],canonical_textual_node=node['canonical_textual_node'],
            role_crosswalk=byrole.get(ident,{}),structural_function=node['structural_function'],
            composition_membership_ids=[r['relation_id'] for r in members],same_level_relation_ids=[r['relation_id'] for r in peers],
            ordered_group_members=[dict(node_id=r['source_node'],position=r['membership_position'],relation_id=r['relation_id']) for r in sorted(
                (r for r in rr if r['relation_type']=='GROUP_MEMBER_OF' and r['target_node']==ident),key=lambda r:int(r['membership_position']))],
            local_relation_ids=[r['relation_id'] for r in local],transition_relation_ids=[r['relation_id'] for r in transitions+group_transition],
            negative_constraint_ids=[r['relation_id'] for r in negatives],all_existing_relation_ids=[r['relation_id'] for r in incident],
            seam_id=tr['controlling_case_id'],frozen_seam_decision=deepcopy(seam),exact_direct_parent_still_unknown=True,
            parent_required_proposal='REVIEW_NEEDED' if category==P7 else 'NOT_REQUIRED_PROPOSED',
            collapse_risk='Never reinterpret non-textual membership, continuation, closure or overlay as direct parentage.',
            original_unresolved_record=deepcopy(old),original_triage_record=deepcopy(tr),
            provenance=[locate(s,UNRESOLVED,'node_id',ident),locate(s,TRIAGE,'unresolved_node_id',ident)],
            **{k:'UNREVIEWED' if k=='review_status' else '' for k in REVIEW_FIELDS}))
    return result


def matrix(s,nn,rr,pp):
    result=[];index={r['node_id']:r for r in nn}
    clause_panel=f.HISTORY+'13_clause_evidence.csv'
    evidence=rows(s['files'][clause_panel])
    for ident in s['cfg']['matrix_ids']:
        n=index[ident];context={ident}
        # Traverse only explicit composition memberships for a reporting context.
        # This emits no transitive relation and never implies textual parentage.
        membership_paths=[];pending=[ident]
        while pending:
            parent=pending.pop()
            for edge in rr:
                if edge['relation_type']=='GROUP_MEMBER_OF' and edge['target_node']==parent:
                    membership_paths.append(edge['relation_id'])
                    if edge['source_node'] not in context:
                        context.add(edge['source_node']);pending.append(edge['source_node'])
        # The ANA:W namespace names the same explicit BHSA word nodes retained
        # in FG-PREP. Shared witnesses supply report context, not endpoint identity.
        linked_clauses=[c for c in evidence if context & {n['node_id'] for n in c['current_hsa']['nodes']}]
        word_ids={'ANA:W:'+str(w['node']) for c in linked_clauses for w in c['verbal_words']}
        judgment_ids={j for x in context for j in index[x]['original_record'].get('source_judgment_ids',[])}
        related=[r for r in rr if r['source_node'] in context or r['target_node'] in context or bool(set(r['original_record'].get('evidence_ids',[])) & (judgment_ids|word_ids))]
        views={layer:[r['relation_id'] for r in related if r['layer']==layer] for layer in ('TEXTUAL_HIERARCHY','TEXTUAL_SAME_LEVEL','COMPOSITION_GROUPING','TRANSITION','OVERLAY_RESPONSIO','NEGATIVE_CONSTRAINT')}
        # Display spans explicitly supplied in the current request, not new coverage claims.
        display=s['cfg']['matrix_display_spans'][ident]
        result.append(dict(node_id=ident,display_span=display,span_authority='CURRENT_REQUEST_DISPLAY_ONLY',node_kind=n['node_kind'],
            **views,onset_terminal_functions=[dict(node_id=x,structural_function=index[x]['structural_function']) for x in sorted(context)],
            explicit_membership_context_relation_ids=sorted(set(membership_paths)),
            shared_word_context_ids=sorted(word_ids),source_clause_context_ids=[c['evidence_id'] for c in linked_clauses],
            overlay_context_basis='EXACT_JUDGMENT_OR_BHSA_WORD_WITNESS_ONLY; NOT_ENDPOINT_IDENTITY_OR_PARENTAGE',
            unresolved_questions=[p['node_id'] for p in pp if p['node_id'] in context],
            hierarchy_status='PARTIAL_TYPED_GRAPH; NO_INFERRED_PARENT',composition_status='EXISTING_RECORDS_ONLY',
            transition_status='EXPLICIT_TYPED_RELATIONS_ONLY',overlay_status='INDEPENDENT_SOURCE_CLAIMS; NOT_PARENTAGE',
            provenance=n['provenance']))
    return result


def counts(m):
    cc=Counter(r['layer'] for r in m['relations'])
    return dict(original_triage=dict(Counter(r['historical_triage'] for r in m['proposals'])),
        proposed_categories=dict(Counter(r['proposed_category'] for r in m['proposals'])),
        p7_nodes=[r['node_id'] for r in m['proposals'] if r['proposed_category']==P7],
        canonical_nodes=len(m['nodes']),composition_groups=len(m['groups']),relation_layers=dict(cc),unresolved_deferred=len(m['unresolved']),
        original_direct_parent_questions=sum(r['question_kind']=='HISTORICAL_DIRECT_PARENT' for r in m['unresolved']),
        role_rows=len(m['roles']),role_loci=len({r['same_textual_locus'] for r in m['roles']}),
        new_human_judgment_count=len(m['new_human_judgments']),new_structural_relation_count=len(m['new_structural_relations']),
        new_composition_relation_count=len(m['new_composition_relations']))


def reports(m,s):
    c=counts(m)
    necessity='\n'.join(['# Parentage necessity audit','',*STATEMENTS,'',
        'Every row is an AUDIT_PROPOSAL / UNREVIEWED. P1 is only the starting question; P2–P7 are machine-generated recommendations, never human conclusions.',
        'P7 is a conservative remainder under explicit rules, not proof that a parent exists or that this is the uniquely minimal scholarly set.',
        'Role category covers six historical rows at three exact paired loci: three canonical speech nodes and three cycle-role aliases. No speech node is deleted or declared non-textual.',
        'A–G stay FROZEN; all 57 original direct-parent values remain UNRESOLVED. No numerical completion target.',
        '', '```json',json.dumps(c,ensure_ascii=False,indent=2),'```','',
        'Rules: non-textual schema → P2; explicit role pair → P3; typed local support for historical local category → P4; membership + peers + speech-onset function for known-container → P5; frozen global seam + independent typed support → P6; otherwise P7.',
        'Membership plus a negative exclusion alone is not enough for the conservative global rule. No verse ID is used to force a P7 outcome.',
        '[All 57 proposals with exact source rows](10_parentage_necessity_audit.csv).'])
    layered=['# Complete layered HSA3 summary','',*STATEMENTS,'','| Component | Display span | Textual placement | Composition | Transition | Overlay | Unresolved questions |','| --- | --- | --- | --- | --- | --- | --- |']
    ri={r['relation_id']:r for r in m['relations']}
    def cell(ids):
        types=Counter(ri.get(i,{}).get('relation_type','INVALID_RELATION_ID') for i in ids)
        return '; '.join(t+': '+str(n) for t,n in sorted(types.items())) or 'None asserted'
    for r in m['matrix']:
        layered.append('| '+' | '.join([r['node_id'],r['display_span'],cell(r['TEXTUAL_HIERARCHY']),cell(r['COMPOSITION_GROUPING']),cell(r['TRANSITION']),cell(r['OVERLAY_RESPONSIO']),str(len(r['unresolved_questions']))])+' |')
    layered += ['', 'These are side-by-side dimensions, not a fully resolved tree. Matrix context traverses only explicit group membership paths and exact judgment/BHSA-word evidence, never verse-range containment. Shared overlay witnesses are reporting context, not endpoint identity or parentage. No transitive structural edge is created.',
        'CHILD_OF/HIERARCHICALLY_ABOVE, CONTINUES_WITHIN and DIRECT_LOCAL_CLOSURE retain different meanings inside the textual placement file. Only the first two are direct hierarchy claims.',
        'SAME_LEVEL_SIBLING and PARALLEL_ENDING retain distinct types. Group onset, introduction and termination remain typed composition relations. ANA-Q2 is a transition overlay; its original TRANSITION_OVERLAY dimension remains intact.',
        'ANA-Q4/Q5 remain accepted independent overlays. ANA-Q3 remains UNRESOLVED/HUMAN_DEFERRED. 42:16 stays NO_BOUNDARY / CONTINUES_WITHIN 42:7; no 42:10/12 promotion.',
        'Technical root links are preserved separately, not textual parentage. All historical source objects and confirmations remain traceable.',
        '[Canonical nodes](01_hsa3_canonical_nodes.csv); [hierarchy/placement](02_hsa3_textual_hierarchy_edges.csv); [peers](03_hsa3_textual_same_level_edges.csv); [groups](04_hsa3_composition_groups.csv); [composition](05_hsa3_composition_relations.csv); [transitions](06_hsa3_transition_relations.csv); [overlays](07_hsa3_overlay_relations.csv); [negatives](08_hsa3_negative_constraints.csv); [unresolved/deferred](09_hsa3_unresolved_deferred.csv).']
    scope='\n'.join(['# NEXT_RESEARCH_SCOPE — FRIENDS_ENTRY_RESOLUTION_PARTICIPANT_ARC','',
        'UNADJUDICATED; proposed future audit scope only. No accepted frame, continuous span object, textual parentage or 42:10 boundary is created.',
        'Opening candidate loci: 2:11–13. Resolution candidate loci: 42:7–9. These are separate research windows, not an accepted 2:11–42:9 unit.',
        'Future observations: the three-friend participant set; introduction versus divine adjudication; 42:9 obedience and subsequent absence; Job-focused restoration at 42:10; relation to 32:1–5; possible חרה אף correspondence at 32:2/42:7; narrator voice; participant continuity/discontinuity.',
        'These are questions, not findings from a new lexical or identity audit.'])
    readiness='\n'.join(['# R4.4 readiness — design recommendation only','',
        'Repository inspection found no implemented R4.4 input contract/specification requiring a direct-parent-complete tree. Historical plans mention hierarchy recompilation, not an approved single-parent requirement.',
        '1. A complete-tree requirement is not established. Do not assume every node needs one direct textual parent.',
        '2. If imposed, that requirement would conflict with the accepted non-textual groups, separate transitions/overlays and explicit unresolved states.',
        '3. Recommend an explicitly versioned input schema preserving the partial textual graph, typed composition graph, transitions, overlays, negative constraints, technical links, provenance and unresolved/deferred states.',
        '4. A future consumer can in principle be lossless without resolving all 57 parent fields, by retaining them as states and never synthesizing default parents. This is a design feasibility conclusion, not an executed R4.4 validation.',
        'READINESS: DESIGN_CONTRACT_REVIEW_REQUIRED. Human approval of necessity proposals and a separately authorized R4.4 contract are pending. R4.4 implementation is NOT STARTED.'])
    packet=['# Researcher review packet','','## A. Proposed categories (all UNREVIEWED)','']
    packet += [k+': '+str(c['proposed_categories'].get(k,0)) for k in CATEGORIES]
    packet += ['', '## B. P7 candidates','']+[r['node_id']+' ('+r['reference']+'): '+r['rationale'] for r in m['proposals'] if r['proposed_category']==P7]
    packet += ['', '## C. Researcher question','', '이 node에 direct textual parent를 계속 요구할 것인가, 아니면 현재 layered relation을 충분한 최종 표현으로 볼 것인가?',
        '', 'Researcher conclusion: ', '', 'Full 57-row review fields remain blank except UNREVIEWED in [audit CSV](10_parentage_necessity_audit.csv).',
        '', '## D. Next participant-arc scope','', '[FRIENDS_ENTRY_RESOLUTION_PARTICIPANT_ARC](14_participant_arc_next_scope.md): separate opening/resolution windows, no adjudication.',
        '', '## E. R4.4 readiness','', '[Design contract review required](15_r4_4_readiness_audit.md); no R4.4 implementation.']
    return dict(necessity=necessity,layered='\n'.join(layered),scope=scope,readiness=readiness,packet='\n'.join(packet))


def derive(s):
    rr=relations(s);roles=role_crosswalk(s);nn=nodes(s,roles,rr);pp=proposals(s,nn,rr,roles)
    m=dict(relations=rr,nodes=nn,roles=roles,groups=composition_groups(nn,rr),proposals=pp,unresolved=unresolved(s),
        matrix=matrix(s,nn,rr,pp),seams=deepcopy(rows(s['files']['07_hsa3_all_seams_status.csv'])),
        historical=deepcopy(s['files']),commit=deepcopy(s['commit']),receipt=deepcopy(s['receipt']),
        new_human_judgments=[],new_structural_relations=[],new_composition_relations=[],participant_frames=[],r44_started=False)
    m['reports']=reports(m,s);return m


def digest(m):
    return d.h.f.rowhash({k:({n:sha(b) for n,b in v.items()} if k=='historical' else v) for k,v in m.items() if k!='rerun_digest'})


def build(s):
    m=derive(s);m['rerun_digest']=digest(derive(s));return m


def gates(m,s):
    original=derive(s);checks={}
    unchanged=lambda n:m['historical'].get(n)==s['files'][n]
    checks['BASELINE_COMMIT_VERIFIED']=m['commit']==s['commit'] and m['commit']['verified_commit']==s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    checks['INPUT_FG_VERIFIED']=m['receipt']==s['receipt'] and unchanged('90_run_metadata.json') and unchanged('10_gates.csv')
    checks['ALL_A_G_FROZEN']=m['seams']==original['seams'] and all(r['status']=='FROZEN' for r in m['seams'])
    checks['ANA_PRESERVED']=unchanged(ANA) and [r for r in m['relations'] if r['source_stage']=='HSA3-ANA.0.3']==[r for r in original['relations'] if r['source_stage']=='HSA3-ANA.0.3']
    checks['HSA2_F_PRESERVED']=unchanged(EDGES) and all(r in m['relations'] for r in original['relations'] if r['relation_type'] in ('DIRECT_LOCAL_CLOSURE','TERMINATES_ENCLOSING_GROUP','NO_DIRECT_RELATION'))
    checks['ORIGINAL_57_LOSSLESS']=m['unresolved']==original['unresolved'] and unchanged(UNRESOLVED)
    checks['TRIAGE_COUNTS_EXACT']=counts(m)['original_triage']==s['cfg']['regression']['triage'] and unchanged(TRIAGE)
    checks['NO_ROW_DROPPED']=len(m['proposals'])==len(original['proposals']) and {r['node_id'] for r in m['proposals']}=={r['node_id'] for r in original['proposals']}
    checks['ONE_PROPOSAL_PER_ROW']=len({r['node_id'] for r in m['proposals']})==len(m['proposals']) and all(r['proposed_category'] in CATEGORIES for r in m['proposals'])
    checks['ALL_PROPOSALS_UNREVIEWED']=all(r['proposal_status']=='UNREVIEWED' and r['proposal_kind']=='AUDIT_PROPOSAL' and not r['human_judgment'] and all(r[k]==('UNREVIEWED' if k=='review_status' else '') for k in REVIEW_FIELDS) for r in m['proposals'])
    checks['NO_NEW_HUMAN_JUDGMENT']=m['new_human_judgments']==[]
    checks['NO_NEW_STRUCTURAL_RELATION']=m['new_structural_relations']==[] and {r['relation_id'] for r in m['relations']}=={r['relation_id'] for r in original['relations']} and all(r['new_relation'] is False for r in m['relations'])
    checks['NO_NEW_COMPOSITION_RELATION']=m['new_composition_relations']==[] and [r for r in m['relations'] if r['layer']=='COMPOSITION_GROUPING']==[r for r in original['relations'] if r['layer']=='COMPOSITION_GROUPING']
    checks['NON_TEXTUAL_GROUPS_STAY_NON_TEXTUAL']=m['groups']==original['groups'] and [r for r in m['nodes'] if r['node_kind']=='COMPOSITION_GROUP']==[r for r in original['nodes'] if r['node_kind']=='COMPOSITION_GROUP']
    checks['ROLE_ALIASES_EXPLICIT']=m['roles']==original['roles'] and all(r['identity_basis']=='EXPLICIT_RESEARCHER_PAIR_AND_SHARED_EXACT_EVIDENCE' and not r['historical_records_merged'] for r in m['roles'])
    checks['MEMBERSHIP_NOT_PARENTAGE']=all(r['direct_parent']=='UNRESOLVED' and not r['direct_parent_resolved'] for r in m['proposals']) and [r for r in m['relations'] if r['layer']=='TEXTUAL_HIERARCHY']==[r for r in original['relations'] if r['layer']=='TEXTUAL_HIERARCHY']
    for cat,gate in [(P4,'LOCAL_RELATION_NOT_REWRITTEN'),(P5,'CONTAINER_NO_HIDDEN_PARENT'),(P6,'GLOBAL_LAYER_PROPOSAL_GROUNDED'),(P7,'P7_CONSERVATIVE_REMAINDER')]:
        checks[gate]=[r for r in m['proposals'] if r['proposed_category']==cat]==[r for r in original['proposals'] if r['proposed_category']==cat]
    checks['Q3_STILL_DEFERRED']=[r for r in m['unresolved'] if r['question_id']=='ANA-Q3']==[r for r in original['unresolved'] if r['question_id']=='ANA-Q3']
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_frames']==[] and m['reports']['scope']==original['reports']['scope']
    checks['NO_42_10_PROMOTION']=m['nodes']==original['nodes']
    checks['ACCEPTED_ANNOTATIONS_PRESERVED']=[r['accepted_annotations'] for r in m['nodes']]==[r['accepted_annotations'] for r in original['nodes']]
    checks['NO_R4_4_IMPLEMENTATION']=m['r44_started'] is False and m['reports']['readiness']==original['reports']['readiness']
    checks['ALL_RELATION_LAYERS_LOSSLESS']=m['relations']==original['relations']
    checks['NO_LAYER_COLLAPSE']=all(r['layer']==s['cfg']['layer_map'][r['relation_type']] for r in m['relations'])
    checks['PROVENANCE_PRESERVED']=[r['provenance'] for r in m['relations']+m['nodes']+m['proposals']]==[r['provenance'] for r in original['relations']+original['nodes']+original['proposals']]
    checks['HISTORICAL_ARTIFACTS_UNCHANGED']=m['historical']==s['files']
    checks['PROPOSALS_REPRODUCIBLE']=m['proposals']==original['proposals']
    checks['MATRIX_SOURCE_GROUNDED']=m['matrix']==original['matrix']
    checks['REPORTS_FAITHFUL']=m['reports']==reports(m,s)
    checks['FROZEN_REPOSITORY_PINS']=len(s['frozen'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'][r['path']] for r in s['frozen'])
    checks['REQUEST_SOURCE_EXACT']=sha(s['request'])==s['cfg']['source_request']['sha256']
    checks['DETERMINISTIC_RERUN']=m['rerun_digest']==digest(m)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


TABLES={'01_hsa3_canonical_nodes.csv':'nodes','04_hsa3_composition_groups.csv':'groups','09_hsa3_unresolved_deferred.csv':'unresolved',
 '10_parentage_necessity_audit.csv':'proposals','12_hsa3_complete_layered_matrix.csv':'matrix','19_role_alias_crosswalk.csv':'roles','20_all_seams_preserved.csv':'seams'}
LAYERS={'02_hsa3_textual_hierarchy_edges.csv':'TEXTUAL_HIERARCHY','03_hsa3_textual_same_level_edges.csv':'TEXTUAL_SAME_LEVEL',
 '05_hsa3_composition_relations.csv':'COMPOSITION_GROUPING','06_hsa3_transition_relations.csv':'TRANSITION',
 '07_hsa3_overlay_relations.csv':'OVERLAY_RESPONSIO','08_hsa3_negative_constraints.csv':'NEGATIVE_CONSTRAINT','18_technical_navigation_relations.csv':'TECHNICAL_NAVIGATION'}
REPORTS={'11_parentage_necessity_summary.md':'necessity','13_hsa3_complete_layered_summary.md':'layered',
 '14_participant_arc_next_scope.md':'scope','15_r4_4_readiness_audit.md':'readiness','16_researcher_review_packet.md':'packet'}


def serialize(m,s):
    gg=gates(m,s);require(all(g['status']=='PASS' for g in gg),str([g for g in gg if g['status']=='FAIL']))
    files={HISTORY+n:b for n,b in m['historical'].items()}
    for n,k in TABLES.items():files[n]=util.csv_bytes(m[k])
    for n,layer in LAYERS.items():files[n]=util.csv_bytes([r for r in m['relations'] if r['layer']==layer])
    for n,k in REPORTS.items():files[n]=m['reports'][k].encode()
    files['21_researcher_source.txt']=s['request']
    files['90_run_metadata.json']=util.json_bytes(dict(version='HSA3-LAYER.0.1',status='PASS',mode=s['mode'],gate_count=len(gg)+1,
        counts=counts(m),baseline_commit=m['commit'],input_receipt=m['receipt'],frozen_receipts=s['frozen'],
        config_sha256=sha(CONFIG.read_bytes()),code_sha256=sha(Path(__file__).read_bytes()),request_sha256=sha(s['request']),
        rerun_payload_sha256=m['rerun_digest'],r44_started=False,claim='AUDIT_PROPOSALS_ONLY; NO_NEW_HUMAN_OR_STRUCTURAL_RELATIONS'))
    f.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['17_gates.csv']=util.csv_bytes(gg);f.seal(files);require(util.manifest_ok(files),'output manifest');return files


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--self-test',action='store_true');ap.add_argument('--archive');ap.add_argument('--out',required=True)
    args=ap.parse_args(argv);require(not(args.self_test and args.archive),'self-test cannot load a real archive')
    s=load(args.self_test,args.archive);files=serialize(build(s),s)
    require(d.h.f.a.prep.r43.frozen_receipts(s['cfg'])==s['frozen'],'frozen source changed during run')
    require((ROOT/s['cfg']['source_request']['path']).read_bytes()==s['request'],'request changed during run')
    if not args.self_test:require(sha((Path(args.archive) if args.archive else ROOT/s['cfg']['archive']['path']).read_bytes())==s['receipt']['sha256'],'input changed during run')
    d.h.f.a.prep.publish(files,args.out);out=Path(args.out).resolve();zp=out.with_name(out.name+'_results.zip')
    receipt='HSA3-LAYER.0.1 PASS\n'+s['mode']+'\nZIP SHA256 '+sha(zp.read_bytes())+'\n'
    out.with_name(out.name+'_run.log').write_text(receipt,encoding='utf-8');print(receipt);return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
