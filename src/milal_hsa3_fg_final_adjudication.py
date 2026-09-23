"""HSA3-F/G: supplied human composition decisions over frozen FG-PREP evidence."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_hsa3_fg_prep as p

a, d = p.prior, p.prior.d
ROOT, sha, rows, util = p.ROOT, p.sha, p.rows, p.util
REVIEW_FIELDS = p.REVIEW_FIELDS
CONFIG = ROOT / 'config/hsa3_fg_job.json'
HISTORY = 'history/fg_prep/'
NODES, EDGES, SEAMS, REGISTRY = (p.HISTORY + x for x in (p.NODES, p.EDGES, p.SEAMS, p.REGISTRY))
UNRESOLVED, ANA = (p.HISTORY + a.HISTORY + x for x in (a.UNRESOLVED, a.ANA))
ABC = p.HISTORY + '01_hsa3_abc_seam_adjudications.csv'
DE = p.HISTORY + a.HISTORY + a.DE
C1, C2, SEQUENCE, FINAL = ('YHWH_JOB_RESPONSE_COMPLEX_1', 'YHWH_JOB_RESPONSE_COMPLEX_2', 'YHWH_JOB_RESPONSE_SEQUENCE', 'FINAL_NARRATIVE_COMPLEX')
F_PANEL, G_PANEL = '06_seam_f_response_complex_evidence.csv', '08_seam_g_final_narrative_evidence.csv'
COMPARISON = '09_job_42_7_16_temporal_comparison.csv'
PEER, TRANSITION = 'SAME_LEVEL_COMPOSITION_PEERS', 'POST_SPEECH_NARRATIVE_TRANSITION'


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-F/G STOP: ' + message)


def audit(files, cfg, digest, synthetic=False):
    require(util.manifest_ok(files) and all(r['valid'] for r in d.h.nested_manifests(files)), 'input manifests')
    require(synthetic or (digest == cfg['archive']['sha256'] and len(files) == cfg['archive']['members']), 'FG-PREP SHA/member count')
    meta = json.loads(files['90_run_metadata.json'])
    gg = rows(files['12_gates.csv'])
    require(meta['version'] == 'HSA3-FG-PREP' and meta['status'] == 'PASS' and not meta['r44_started'], 'FG-PREP status')
    require(len(gg) == meta['gate_count'] and all(g['status'] == 'PASS' for g in gg), 'FG-PREP gates')
    require(meta['mode'] == ('SYNTHETIC_ONLY' if synthetic else 'REAL_BHSA_2021_AUDIT'), 'source execution mode')
    for name, ids in [(ABC, ['SEAM_A','SEAM_B','SEAM_C']), (DE, ['SEAM_D','SEAM_E'])]:
        rr = rows(files[name])
        require([r['seam_id'] for r in rr] == ids and all(r['status'] == 'FROZEN' for r in rr), 'prior seam decisions')
    review = rows(files['18_fg_review_fields.csv'])
    require(len(review) == 2 and all(r[k] == ('UNREVIEWED' if k == 'review_status' else '') for r in review for k in REVIEW_FIELDS), 'F/G prior review fields')
    require(all(r['direct_parent'] == 'UNRESOLVED' for r in rows(files[UNRESOLVED])), 'parent questions')
    return dict(sha256=digest, members=len(files), synthetic=synthetic, manifests=d.h.nested_manifests(files),
                prior_mode=meta['mode'], prior_gate_count=len(gg), source_snapshot_sha256=sha(files['16_bhsa_source_snapshot.json']))


def load(self_test=False, archive=None):
    cfg = json.loads(CONFIG.read_bytes())
    commit = d.baseline_receipt(cfg)
    frozen = d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['expected'] == r['actual'] for r in frozen), 'frozen repository pins')
    hb = (ROOT / cfg['human_source']['path']).read_bytes()
    require(sha(hb) == cfg['human_source']['sha256'], 'human source hash')
    human = json.loads(hb)
    request = (ROOT / human['source_path']).read_bytes()
    require(sha(request) == human['source_sha256'], 'request hash')
    if self_test:
        ps = p.load(True)
        files = p.serialize(p.build(ps), ps)
        digest = sha(files['99_manifest_sha256.csv'])
    else:
        data = (Path(archive) if archive else ROOT / cfg['archive']['path']).read_bytes()
        digest = sha(data)
        require(digest == cfg['archive']['sha256'], 'FG-PREP archive hash')
        files = d.h.f.a.prep.r43.h1.src.archive(data, digest, mr1=True)['files']
    return dict(cfg=cfg, commit=commit, frozen=frozen, human=human, human_bytes=hb, request=request, files=files,
                receipt=audit(files,cfg,digest,self_test), mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_ARTIFACT_ADJUDICATION')


def locate(s, member, field, ident):
    rr = [(i,r) for i,r in enumerate(d.h.raw_rows(s['files'][member]),1) if r[field] == ident]
    require(len(rr) == 1, 'missing/duplicate exact source identity ' + str(ident))
    i,r = rr[0]
    return dict(source_member=HISTORY+member, source_data_row=i, source_identity_field=field, source_identity=ident,
                source_row_sha256=d.h.f.rowhash(r), source_member_sha256=sha(s['files'][member]), source_artifact_sha256=s['receipt']['sha256'])


def catalog(s):
    """Audit existing canonical objects, excluding confirmations and proposals."""
    rels = [dict(r, canonical_relation_id=r['edge_id']) for r in rows(s['files'][EDGES])]
    groups = []
    for name,data in sorted(s['files'].items()):
        if name.endswith('relation_actions.csv'):
            rels += [r for r in rows(data) if r['action'] in ('CREATED','NEGATIVE_CONSTRAINT_CREATED')]
        if name.endswith('composition_groups.csv'):
            groups += rows(data)
    return rels, groups


def semantic_key(r):
    ends = [r['source_node'],r['target_node']]
    if r['relation_type'] == PEER:
        ends.sort()
    # Historical NO_DIRECT_RELATION is dimension-specific, not universal denial.
    return (*ends, r['relation_type'], r.get('dimension','') if r['relation_type'] == 'NO_DIRECT_RELATION' else '')


def evidence(s):
    return [dict(panel=panel, original_record=deepcopy(r), **locate(s,panel,'evidence_id',r['evidence_id']))
            for panel in (F_PANEL,G_PANEL) for r in rows(s['files'][panel])]


def groups(s):
    _, old = catalog(s)
    nodes = {r['node_id'] for r in rows(s['files'][NODES])}
    available = nodes | {r['group_id'] for r in old}
    result = []
    for supplied in s['human']['groups']:
        g = deepcopy(supplied)
        equivalents = [x for x in old if x['members'] == g['members']]
        require(len(equivalents) <= 1, 'ambiguous existing composition')
        if equivalents:
            require(equivalents[0]['group_id'] == g['group_id'] and all(equivalents[0][k] == g[k] for k in ('node_type','span_start','span_end')), 'existing composition requires explicit canonical mapping')
        require(g['group_id'] not in available or bool(equivalents), 'group ID collision')
        require(all(x in available for x in g['members']), 'unknown member ID')
        refs = g['anchor_references']
        ee = [r for r in evidence(s) if r['original_record']['reference'] in refs]
        require(set(refs) == {r['original_record']['reference'] for r in ee}, 'missing anchor evidence')
        g.update(action='CONFIRMED_EXISTING' if equivalents else 'CREATED', textual_parent=False,
                 evidence_anchor_ids=[r['original_record']['evidence_id'] for r in ee],
                 anchor_policy='EVIDENCE_ONLY_NOT_NEW_TEXTUAL_NODES', authority='EXPLICIT_RESEARCHER_COMPOSITION',
                 scope_authority='HUMAN_SUPPLIED_SPAN_NOT_COMPUTED_CLOSURE', source_request_sha256=sha(s['request']))
        result.append(g)
        available.add(g['group_id'])
    return result


def crosswalk(s):
    cases = rows(s['files'][SEAMS])
    result = []
    for r in rows(s['files'][UNRESOLVED]):
        owner = [c['case_id'] for c in cases if r['node_id'] in c['primary_unresolved_rows']]
        involved = [c['case_id'] for c in cases if c['case_id'] in ('SEAM_F','SEAM_G') and r['node_id'] in c['participating_unresolved_rows']]
        require(len(owner) == 1, 'unresolved ownership')
        result.append(dict(node_id=r['node_id'], reference=r['reference'], primary_seam=owner[0], participating_fg_seams=involved,
            status='REMAINS_UNRESOLVED' if involved else 'NOT_APPLICABLE_TO_APPROVED_DECISION', direct_parent='UNRESOLVED',
            direct_parent_resolved=False, reason='Composition and negative constraints do not assign a direct textual parent.',
            historical_record=deepcopy(r), **locate(s,UNRESOLVED,'node_id',r['node_id'])))
    return result


def requests(s, gg):
    result = []
    for g in gg:
        for i, ident in enumerate(g['members'],1):
            result.append(dict(seam_id=g['seam_id'], source_node=ident,target_node=g['group_id'],relation_type='GROUP_MEMBER_OF',
                               dimension='COMPOSITION_GROUPING',membership_position=i,symmetric=False))
    result += deepcopy(s['human']['positive_relations'])
    # Negative claims target exact existing clause evidence, not invented verse nodes.
    for rule in s['human']['negative_rules']:
        matched = [r['original_record'] for r in evidence(s) if r['original_record']['reference'] == rule['reference']]
        require(bool(matched), 'negative control evidence missing')
        for r in matched:
            q = dict(rule, seam_id='SEAM_G',source_node=r['evidence_id'],symmetric=False,negative=True)
            result.append(q)
            if rule.get('direction') == 'BOTH_EXCLUDED_PARENT_DIRECTIONS':
                result.append(dict(q,source_node=q['target_node'],target_node=q['source_node']))
    return result


def actions(s, gg):
    old,_ = catalog(s)
    cases = [c for c in rows(s['files'][SEAMS]) if c['case_id'] in ('SEAM_F','SEAM_G')]
    ids = {x for c in cases for x in c['relation_ids']}
    result=[]
    for e in rows(s['files'][EDGES]):
        if e['edge_id'] in ids:
            result.append(dict(action_id='FG:CONFIRM:'+e['edge_id'],action='CONFIRMED_EXISTING',object_kind='RELATION',
                canonical_relation_id=e['edge_id'],source_node=e['source_node'],target_node=e['target_node'],relation_type=e['relation_type'],
                dimension=e['dimension'],textual_parentage_created=False,original_record=deepcopy(e),
                **locate(s,EDGES,'edge_id',e['edge_id'])))
    seen = set()
    for q in requests(s,gg):
        k=semantic_key(q)
        eq=[e for e in old if semantic_key(e)==k]
        require(len(eq)<=1,'ambiguous equivalent relation')
        action='NO_ACTION_DUPLICATE' if k in seen else 'CONFIRMED_EXISTING' if eq else 'NEGATIVE_CONSTRAINT_CREATED' if q.get('negative') else 'CREATED'
        seen.add(k)
        result.append(dict(q,action_id='FG:REQUEST:'+str(len(result)+1),action=action,object_kind='RELATION',
            canonical_relation_id=eq[0]['canonical_relation_id'] if eq else 'FG:R:'+d.h.f.rowhash(k)[:20],
            textual_parentage_created=False,authority='EXPLICIT_RESEARCHER_DECISION',source_request_sha256=sha(s['request'])))
    for r in crosswalk(s):
        if r['status']=='REMAINS_UNRESOLVED':
            result.append(dict(action_id='FG:UNRESOLVED:'+r['node_id'],action='UNRESOLVED_RETAINED',object_kind='PARENT_QUESTION',
                canonical_relation_id='',source_node=r['node_id'],target_node='',relation_type='UNRESOLVED',dimension='PARENTAGE_CONTAINMENT',textual_parentage_created=False))
    return result


def criteria(s):
    registry={r['evidence_code']:r for r in rows(s['files'][REGISTRY])}
    result=[]
    for seam,codes in s['human']['criteria'].items():
        for code in codes:
            require(code in registry,'unknown evidence criterion')
            result.append(dict(seam_id=seam,evidence_code=code,sole_basis_sufficient=False,
                role='INSUFFICIENT_ALONE' if code.startswith('N-') else 'SUPPLIED_HUMAN_RATIONALE',
                original_registry_record=deepcopy(registry[code]),evidence_panel=HISTORY+(F_PANEL if seam=='SEAM_F' else G_PANEL),
                note='Converging correspondences support supplied composition only. Repeated formula alone is insufficient.',
                **locate(s,REGISTRY,'evidence_code',code)))
    return result


def all_seams(s, decisions):
    result=[]
    for member in (ABC,DE):
        for r in rows(s['files'][member]):
            result.append(dict(seam_id=r['seam_id'],status=r['status'],authority='PRESERVED_RESEARCHER_DECISION',
                original_record=deepcopy(r),**locate(s,member,'seam_id',r['seam_id'])))
    result += [dict(seam_id=r['seam_id'],status=r['status'],authority='CURRENT_RESEARCHER_DECISION',original_record=deepcopy(r)) for r in decisions]
    return result


def counts(m):
    cc=Counter(r['action'] for r in m['actions'])
    return dict(researcher_seam_decisions=len(m['adjudications']),new_composition_groups=sum(g['action']=='CREATED' for g in m['groups']),
        confirmed_existing_groups=sum(g['action']=='CONFIRMED_EXISTING' for g in m['groups']),new_positive_relations=cc['CREATED'],
        confirmed_relations=cc['CONFIRMED_EXISTING'],new_negative_constraints=cc['NEGATIVE_CONSTRAINT_CREATED'],
        unresolved_retained=cc['UNRESOLVED_RETAINED'],duplicate_skipped=cc['NO_ACTION_DUPLICATE'],
        crosswalk=dict(Counter(r['status'] for r in m['crosswalk'])),remaining_direct_parent_questions=sum(r['direct_parent']=='UNRESOLVED' for r in m['crosswalk']),
        resolved_by_F=sum(r['status']=='RESOLVED_BY_SEAM_F' for r in m['crosswalk']),resolved_by_G=sum(r['status']=='RESOLVED_BY_SEAM_G' for r in m['crosswalk']))


STATEMENTS = [
 'Repeated configurations may support composition-level parallelism without creating textual parentage.',
 '38:1–40:5 and 40:6–42:6 are adjudicated as composition peers because multiple independent formal/distributional correspondences converge.',
 '42:7 marks resumption of narrative discourse after the YHWH–Job sequence, but the transition is between larger discourse complexes, not a direct 42:6→42:7 parent relation.',
 '42:10, 42:12, and 42:16 may mark semantic/event development without constituting independent macro boundaries.',
 'A frozen HSA3 does not imply a fully resolved tree. MILAL retains unresolved direct parentage where evidence does not warrant it.']


def report(m,s):
    lines=['# HSA3-F/G final human adjudication','',*STATEMENTS,'',
        'SEAM_F and SEAM_G: ACCEPTED / FROZEN. All A–G supplied decisions are FROZEN.',
        'New types SAME_LEVEL_COMPOSITION_PEERS and POST_SPEECH_NARRATIVE_TRANSITION are composition-only. The peer is symmetric, stored once; historical reciprocal textual siblings remain intact.',
        'Canonical schema audit: GROUP_MEMBER_OF is reused. Textual SAME_LEVEL_SIBLING and ANA POST_CLOSURE_TRANSITION are not equivalent to the supplied composition peer/transition claims.',
        '38:3/40:7 remain source evidence anchors, not new structural nodes. Existing H:HSA027/029 carry human response spans 40:3–5/42:1–6 without duplicate units.',
        '42:7 backward framing concerns YHWH speaking, not a direct edge from the Job response at 42:6.',
        '42:10/12 are internal evidence; WXQt comparison is preserved. 42:16 retains NO_BOUNDARY / CONTINUES_WITHIN 42:7, חיה rather than היה, and Time after predicate/subject.',
        'ANA-Q2/Q4/Q5 and HSA2-F remain unchanged. ANA-Q3 remains UNRESOLVED / HUMAN_DEFERRED; no fulfilment or causal claim is added.',
        '2:11–42:9 participant-frame hypothesis remains unadjudicated. R4.4 is not started. No new marker/lexical extraction or parent inference.',
        'Real validation consumes hash-pinned FG-PREP BHSA 2021 evidence; it is not a fresh BHSA extraction.', '',
        '## Composition groups','', '| ID | Span | Ordered members |','| --- | --- | --- |']
    lines += [f"| {g['group_id']} | {g['span_start']}–{g['span_end']} | {', '.join(g['members'])} |" for g in m['groups']]
    lines += ['', '## Computed accounting','','```json',json.dumps(counts(m),ensure_ascii=False,indent=2),'```','',
        '[Exact source evidence and row receipts](11_hsa3_fg_evidence_links.csv); [response spans](12_hsa3_fg_span_annotations.csv); [schema audit](13_hsa3_fg_schema_audit.json).',
        'All prior artifacts are retained byte-for-byte under '+HISTORY+'. Negative exclusions concern specified dimensions only; they do not deny all possible relationships.']
    return '\n'.join(lines)


def summary(m,s):
    lines=['# HSA3 complete review summary','','All seven global seam decisions are FROZEN. This is a layered account, not a fully resolved textual tree.','',
        '## Composition and narrative sequence','','| Component | Span | Layer |','| --- | --- | --- |',
        '| OPENING_NARRATIVE_COMPLEX | 1:1–2:13 | Non-textual composition |',
        '| JOB_FRIENDS_DISPUTE_COMPLEX | 3:1–31:40 | Non-textual composition |',
        '| H:HSA018 | 32:1 | TRANSITION_COMPONENT |',
        '| Elihu introduction + speech sequence | 32:2–37:24 | Introduction 32:2–5 and existing ELIHU_SPEECH_SEQUENCE 32:6–37:24 |',
        '| YHWH_JOB_RESPONSE_SEQUENCE | 38:1–42:6 | Non-textual composition |',
        '| YHWH_JOB_RESPONSE_COMPLEX_1 | 38:1–40:5 | First sequence member |',
        '| YHWH_JOB_RESPONSE_COMPLEX_2 | 40:6–42:6 | Second sequence member, composition peer |',
        '| FINAL_NARRATIVE_COMPLEX | 42:7–42:17 | Non-textual composition; post-speech narrative transition |','',
        '## Accepted textual relations','','CHILD_OF, CONTINUES_WITHIN and HIERARCHICALLY_ABOVE remain distinct from textual SAME_LEVEL_SIBLING.',
        '38:1 ↔ 40:6 and 40:3 ↔ 42:1 retain textual SAME_LEVEL_SIBLING. 40:1 CHILD_OF 38:1. 42:16 CONTINUES_WITHIN 42:7.',
        '[Complete frozen textual edge table, including all source IDs]('+HISTORY+EDGES+').','',
        '## Accepted negative constraints','','42:16 NO_BOUNDARY. 42:10/12 have no new boundary or textual parent promotion. No direct 42:6/42:7 parentage, response or continuation edge.',
        '[Current negative constraints](05_hsa3_fg_negative_constraints.csv); [A–C negatives]('+HISTORY+p.HISTORY+'04_hsa3_abc_negative_constraints.csv); [D/E negatives]('+HISTORY+p.HISTORY+a.HISTORY+'05_hsa3_de_negative_constraints.csv).',
        'Earlier 31:40 closure-target exclusions, cycle constraints and all historical negatives remain in the complete frozen edge/action tables.','',
        '## Overlay / responsio','','ANA-Q2 POST_CLOSURE_TRANSITION, ANA-Q4 CONTRASTIVE_ANA_FRAME and ANA-Q5 ELIHU_RESPONSE_ROLE_INTERVENTION remain ACCEPTED.',
        'ANA-Q3 LONG_DISTANCE_RESPONSE (31:35→38:1) remains UNRESOLVED / HUMAN_DEFERRED. No causal or fulfilment assertion.',
        '[Exact ANA decisions and limitations]('+HISTORY+ANA+').','',
        '## Unresolved questions','',
        str(counts(m)['remaining_direct_parent_questions'])+' exact direct-parent questions remain unresolved. Composition is not an answer to textual parentage.',
        '[All original questions and current crosswalk](06_hsa3_fg_unresolved_crosswalk.csv).',
        'The 2:11–42:9 participant frame remains unadjudicated and may overlap final narrative at a separate layer.',
        'Recommended next step: researcher reviews this complete layered summary and separately scopes unresolved parentage / participant-frame questions. R4.4 requires a new authorization; it is not started.']
    return '\n'.join(lines)


def derive(s):
    gg=groups(s); aa=actions(s,gg)
    decisions=[dict(r,researcher_supplied=True,source_request_sha256=sha(s['request']),exact_textual_parent_assigned=False,
                    **locate(s,SEAMS,'case_id',r['seam_id'])) for r in s['human']['decisions']]
    rr,oldgroups=catalog(s)
    m=dict(groups=gg,actions=aa,adjudications=decisions,all_seams=all_seams(s,decisions),crosswalk=crosswalk(s),criteria=criteria(s),
        negative=[deepcopy(r) for r in aa if r['action']=='NEGATIVE_CONSTRAINT_CREATED'],evidence=evidence(s),annotations=deepcopy(s['human']['annotations']),
        historical=deepcopy(s['files']),commit=deepcopy(s['commit']),receipt=deepcopy(s['receipt']),
        facts=deepcopy(rows(s['files'][NODES])),ana=deepcopy(rows(s['files'][ANA])),comparison=deepcopy(rows(s['files'][COMPARISON])),
        schema=dict(existing_relation_types=sorted({r['relation_type'] for r in rr}),existing_group_ids=sorted(g['group_id'] for g in oldgroups),
                    reused_type='GROUP_MEMBER_OF',new_types=[PEER,TRANSITION,'NO_BOUNDARY_PROMOTION'],
                    equivalence_policy='Exact identity and documented semantics; no textual sibling or post-closure overlay substitution.'),
        r44_started=False,lexical_scans=[],participant_frame_adjudications=[])
    m['report'],m['summary']=report(m,s),summary(m,s)
    return m


def digest(m):
    return d.h.f.rowhash({k:({n:sha(b) for n,b in v.items()} if k=='historical' else v) for k,v in m.items() if k!='rerun_digest'})


def build(s):
    m=derive(s);m['rerun_digest']=digest(derive(s));return m


def gates(m,s):
    checks={}
    original=derive(s)
    gs={g['group_id']:g for g in m['groups']}
    facts={r['node_id']:r for r in m['facts']}
    new=[r for r in m['actions'] if r['action']=='CREATED']
    unchanged=lambda n:m['historical'].get(n)==s['files'][n]
    has=lambda src,tgt,rel:any(r['source_node']==src and r['target_node']==tgt and r['relation_type']==rel and r['action'] in ('CREATED','CONFIRMED_EXISTING') for r in m['actions'])
    def group_ok(ident):
        expected=next(g for g in original['groups'] if g['group_id']==ident)
        members=[r['source_node'] for r in sorted((r for r in m['actions'] if r['target_node']==ident and r['relation_type']=='GROUP_MEMBER_OF'),key=lambda r:int(r.get('membership_position',0)))]
        return gs.get(ident)==expected and members==expected['members']
    checks['BASELINE_COMMIT_VERIFIED']=m['commit']==s['commit'] and m['commit']['verified_commit']==s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    checks['FG_PREP_VERIFIED']=m['receipt']==s['receipt'] and all(unchanged(n) for n in ('90_run_metadata.json','12_gates.csv','18_fg_review_fields.csv','16_bhsa_source_snapshot.json'))
    for seam in ('SEAM_F','SEAM_G'):
        checks[seam+'_RESEARCHER_DECISION_RECORDED']=[r for r in m['adjudications'] if r['seam_id']==seam]==[r for r in original['adjudications'] if r['seam_id']==seam]
    checks['ALL_A_G_SEAMS_FROZEN']=m['all_seams']==original['all_seams'] and [r['seam_id'] for r in m['all_seams']]==['SEAM_'+x for x in 'ABCDEFG'] and all(r['status']=='FROZEN' for r in m['all_seams']) and unchanged(ABC) and unchanged(DE)
    for ident,gate in [(C1,'RESPONSE_COMPLEX_1_PRESENT'),(C2,'RESPONSE_COMPLEX_2_PRESENT'),(SEQUENCE,'RESPONSE_SEQUENCE_PRESENT'),(FINAL,'FINAL_NARRATIVE_COMPLEX_PRESENT')]:
        checks[gate]=group_ok(ident)
    checks['RESPONSE_COMPLEX_PEERS_PRESENT']=has(C1,C2,PEER) and any(r.get('symmetric') is True and r.get('dimension')=='COMPOSITION_PEER' for r in m['actions'] if r['relation_type']==PEER)
    checks['RESPONSE_GROUPS_NON_TEXTUAL']=bool(gs) and all(g['node_type']=='NON_TEXTUAL_COMPOSITION_GROUP' and g['textual_parent'] is False for g in gs.values()) and not any(r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE','CONTINUES_WITHIN','SAME_LEVEL_SIBLING') and (r['source_node'] in gs or r['target_node'] in gs) for r in new)
    pairs=[('H:HSA025','H:HSA028'),('H:HSA027','H:HSA029')]
    checks['EXISTING_YHWH_JOB_RELATIONS_PRESERVED']=all(has(x,y,'SAME_LEVEL_SIBLING') and has(y,x,'SAME_LEVEL_SIBLING') for x,y in pairs) and has('H:HSA026','H:HSA025','CHILD_OF') and unchanged(EDGES)
    checks['POST_SPEECH_NARRATIVE_TRANSITION_PRESENT']=has(SEQUENCE,FINAL,TRANSITION) and all(r.get('dimension')=='COMPOSITION_TRANSITION' for r in m['actions'] if r['relation_type']==TRANSITION)
    six={r['original_record']['evidence_id'] for r in m['evidence'] if r['original_record']['reference']=='42:6'}
    pair=lambda r:(r['source_node'] in six and r['target_node']=='H:HSA030') or (r['target_node'] in six and r['source_node']=='H:HSA030')
    checks['NO_42_6_42_7_PARENTAGE']=bool(six) and not any(pair(r) and r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE','CONTINUES_WITHIN') for r in new)
    checks['NO_42_6_42_7_RESPONSE_EDGE']=bool(six) and not any(pair(r) and r['relation_type']=='RESPONSE_TO' for r in new)
    for ref,gate in [('42:10','JOB_42_10_NOT_PROMOTED'),('42:12','JOB_42_12_NOT_PROMOTED')]:
        ids={r['original_record']['evidence_id'] for r in m['evidence'] if r['original_record']['reference']==ref}
        checks[gate]=bool(ids) and not any(n['reference_start']==ref and (n['textual_boundary'] or n['structural_function'] in ('PARAGRAPH_ONSET','MACRO_BOUNDARY')) for n in m['facts']) and not any((r['source_node'] in ids or r['target_node'] in ids) and r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE','SAME_LEVEL_SIBLING','PARAGRAPH_ONSET','MACRO_BOUNDARY') for r in new)
    checks['JOB_42_16_NO_BOUNDARY_PRESERVED']=facts.get('H:HSA031',{}).get('structural_function')=='NO_BOUNDARY' and has('H:HSA031','H:HSA030','CONTINUES_WITHIN') and has('H:HSA031','H:HSA031','NO_BOUNDARY') and facts.get('H:HSA030',{}).get('structural_function')=='PARAGRAPH_ONSET'
    life=[r['original_record'] for r in m['evidence'] if r['original_record']['reference']=='42:16' and r['original_record']['lexical_waychi_words']]
    checks['WAYHI_WAYHI_LIFE_VERB_DISTINCTION_PRESERVED']=bool(life) and all(not r['lexical_wayhi_words'] and any(w['lex']=='XJH[' for w in r['verbal_words']) for r in life) and m['comparison']==original['comparison']
    aq=lambda obj,ids:[r for r in obj['ana'] if r['review_question_id'] in ids]
    checks['ANA_Q3_STILL_UNRESOLVED']=aq(m,['ANA-Q3'])==aq(original,['ANA-Q3']) and bool(aq(m,['ANA-Q3']))
    checks['ANA_Q4_Q5_PRESERVED']=aq(m,['ANA-Q2','ANA-Q4','ANA-Q5'])==aq(original,['ANA-Q2','ANA-Q4','ANA-Q5'])
    checks['NO_2_11_42_9_FRAME_ADJUDICATION']=m['participant_frame_adjudications']==[] and set(gs)=={C1,C2,SEQUENCE,FINAL} and not any(r['source_node']=='H:HSA012' for r in new)
    checks['UNRESOLVED_PARENTAGE_NOT_FAKE_RESOLVED']=m['crosswalk']==original['crosswalk'] and all(r['direct_parent']=='UNRESOLVED' and r['direct_parent_resolved'] is False for r in m['crosswalk']) and unchanged(UNRESOLVED)
    checks['HISTORICAL_ARTIFACTS_UNCHANGED']=m['historical']==s['files']
    created=[r for r in m['actions'] if r['action'] in ('CREATED','NEGATIVE_CONSTRAINT_CREATED')]
    old,_=catalog(s);oldkeys={semantic_key(r) for r in old}
    checks['NO_DUPLICATE_RELATIONS']=len({semantic_key(r) for r in created})==len(created) and not any(semantic_key(r) in oldkeys for r in created)
    checks['NO_R4_4']=m['r44_started'] is False
    checks['NO_NEW_LEXICAL_ANALYSIS']=m['lexical_scans']==[]
    checks['RESEARCHER_SOURCE_EXACT']=sha(s['human_bytes'])==s['cfg']['human_source']['sha256'] and json.loads(s['human_bytes'])==s['human'] and sha(s['request'])==s['human']['source_sha256']
    checks['FROZEN_SOURCE_FILES']=len(s['frozen'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'][r['path']] for r in s['frozen'])
    for field,gate in [('actions','RELATION_ACTIONS_EXACT'),('negative','NEGATIVE_CONSTRAINTS_EXACT'),('criteria','CRITERIA_CANONICAL'),('evidence','SOURCE_EVIDENCE_EXACT'),('annotations','RESPONSE_SPANS_NO_DUPLICATE_NODES'),('facts','FROZEN_NODES_EXACT'),('schema','SCHEMA_AUDIT_EXACT')]:
        checks[gate]=m[field]==original[field]
    checks['REPORT_FAITHFUL']=m['report']==report(m,s) and m['summary']==summary(m,s)
    checks['DETERMINISTIC_RERUN']=m['rerun_digest']==digest(m)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


OUTPUTS={'01_hsa3_fg_final_adjudications.csv':'adjudications','02_hsa3_fg_relation_actions.csv':'actions',
 '03_hsa3_fg_composition_groups.csv':'groups','04_hsa3_fg_criteria_application.csv':'criteria','05_hsa3_fg_negative_constraints.csv':'negative',
 '06_hsa3_fg_unresolved_crosswalk.csv':'crosswalk','07_hsa3_all_seams_status.csv':'all_seams','11_hsa3_fg_evidence_links.csv':'evidence',
 '12_hsa3_fg_span_annotations.csv':'annotations','16_hsa3_fg_preserved_nodes.csv':'facts','17_hsa3_fg_preserved_ana.csv':'ana'}


def seal(files):
    files.pop('99_manifest_sha256.csv',None)
    files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(files.items())])


def serialize(m,s):
    gg=gates(m,s)
    require(all(g['status']=='PASS' for g in gg),str([g for g in gg if g['status']=='FAIL']))
    files={HISTORY+k:v for k,v in m['historical'].items()}
    for name,field in OUTPUTS.items():files[name]=util.csv_bytes(m[field])
    files['08_hsa3_fg_final_report.md']=m['report'].encode()
    files['09_hsa3_complete_review_summary.md']=m['summary'].encode()
    files['13_hsa3_fg_schema_audit.json']=util.json_bytes(m['schema'])
    files['14_researcher_decisions.json'],files['15_researcher_source.txt']=s['human_bytes'],s['request']
    files['90_run_metadata.json']=util.json_bytes(dict(version='HSA3-F/G',status='PASS',mode=s['mode'],gate_count=len(gg)+1,
        counts=counts(m),baseline_commit=m['commit'],input_receipt=m['receipt'],frozen_receipts=s['frozen'],
        config_sha256=sha(CONFIG.read_bytes()),code_sha256=sha(Path(__file__).read_bytes()),human_input_sha256=sha(s['human_bytes']),
        researcher_source_sha256=sha(s['request']),rerun_payload_sha256=m['rerun_digest'],r44_started=False,lexical_scans=[],
        claim='ALL_A_G_FROZEN; COMPOSITION_NOT_TEXTUAL_PARENTAGE; ANA_Q3_DEFERRED; PARTICIPANT_FRAME_UNADJUDICATED'))
    seal(files)
    gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['10_gates.csv']=util.csv_bytes(gg);seal(files)
    require(util.manifest_ok(files),'output manifest')
    return files


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True);parser.add_argument('--archive');parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args(argv)
    require(not(args.self_test and args.archive),'self-test cannot use real archive')
    s=load(args.self_test,args.archive);files=serialize(build(s),s)
    require(d.h.f.a.prep.r43.frozen_receipts(s['cfg'])==s['frozen'],'frozen files changed during run')
    require((ROOT/s['cfg']['human_source']['path']).read_bytes()==s['human_bytes'] and (ROOT/s['human']['source_path']).read_bytes()==s['request'],'authority changed during run')
    if not args.self_test:require(sha((Path(args.archive) if args.archive else ROOT/s['cfg']['archive']['path']).read_bytes())==s['receipt']['sha256'],'input changed during run')
    d.h.f.a.prep.publish(files,args.out)
    out=Path(args.out).resolve();zp=out.with_name(out.name+'_results.zip')
    receipt='HSA3-F/G PASS\n'+s['mode']+'\nZIP SHA256 '+sha(zp.read_bytes())+'\n'
    out.with_name(out.name+'_run.log').write_text(receipt,encoding='utf-8');print(receipt)
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
