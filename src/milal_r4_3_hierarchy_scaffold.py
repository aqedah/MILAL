"""Compile a partial scaffold from frozen human decisions; never infer global parents."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import sys
import zipfile

import milal_hsa2_final as final

h1, h2 = final.h1, final.h2
ROOT = final.ROOT
CONFIG = ROOT / 'config/r4_3_job.json'
sha, canonical = final.sha, final.canonical
REPORT = '04_whole_book_hierarchy_scaffold.md'
CLASSES = {'CHILD_OF':'HIERARCHY', 'HIERARCHICALLY_ABOVE':'HIERARCHY',
           'CONTINUES_WITHIN':'CONTINUATION', 'GROUP_MEMBER_OF':'MEMBERSHIP',
           'SAME_LEVEL_SIBLING':'HORIZONTAL', 'PARALLEL_TO':'HORIZONTAL',
           'PARALLEL_ENDING':'CLOSURE_COMPARISON', 'DIRECT_LOCAL_CLOSURE':'LOCAL_CLOSURE',
           'TERMINATES_ENCLOSING_GROUP':'HIGHER_TERMINATION', 'NO_DIRECT_RELATION':'NEGATIVE',
           'NO_BOUNDARY':'NEGATIVE', 'TRANSITION_COMPONENT':'DESCRIPTIVE',
           'NARRATIVE_INTRODUCTION':'DESCRIPTIVE', 'CYCLE_ONSET_OF':'DESCRIPTIVE',
           'RESPONSE':'RESPONSE_OVERLAY', 'TECHNICAL_ROOT_LINK':'TECHNICAL'}


def require(ok, message):
    if not ok:
        raise ValueError('R4.3 STOP: ' + message)


def table(files, name):
    return h1.read_csv(files[name])


def frozen_receipts(cfg):
    return [dict(path=p, expected=d, actual=sha((ROOT/p).read_bytes())) for p,d in cfg['frozen_files'].items()]


def load(self_test=False):
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    frozen = frozen_receipts(cfg)
    require(all(r['actual']==r['expected'] for r in frozen), 'frozen source changed')
    fs = final.source(self_test)
    if self_test:
        from milal_hsa1_synthetic import source
        hs, rows, md = source()
        a = h1.serialize(h1.build(hs, rows, md), hs)
        b = final.serialize(final.build(fs), fs)
        inputs = []
        frames, enclosures = [], []
        frame_files = {}
    else:
        archives = {}
        for role, pin in cfg['archives'].items():
            archives[role] = h1.src.archive((ROOT/pin['path']).read_bytes(), pin['sha256'], mr1=True)
        a, b = archives['hsa1']['files'], archives['hsa2_f']['files']
        for files, gatefile, version in ((a,'07_gates.csv','HSA1'),(b,'08_gates.csv','HSA2-F')):
            gg = table(files,gatefile)
            meta = json.loads(files['90_run_metadata.json'])
            require(gg and all(r['status']=='PASS' for r in gg) and meta['status']=='PASS', 'unaccepted '+version)
        require(a['01_structural_judgments.csv']==h1.CSV.read_bytes() and a['08_human_registry.md']==h1.MD.read_bytes(), 'HSA1 bytes differ')
        require(b['01_final_human_adjudications.csv']==final.CSV.read_bytes() and b['05_final_human_adjudications.md']==final.MD.read_bytes(), 'HSA2-F bytes differ')
        require({k.removeprefix('hsa2/'):v for k,v in b.items() if k.startswith('hsa2/')}==fs['files'], 'nested HSA2 differs')
        meta = json.loads(b['90_run_metadata.json'])
        require(meta['version']=='HSA2-F' and meta['mode']=='ACCEPTED_REAL_AUDIT_ONLY', 'HSA2-F is not accepted real')
        inputs = deepcopy(fs['inputs'])+[dict(role=k,path=v['path'],sha256=v['sha256'],expected=v['sha256']) for k,v in cfg['archives'].items()]
        pin = json.loads(h1.CONFIG.read_text(encoding='utf-8'))['archives']['r4_2']
        archive = h1.src.archive((ROOT/pin['path']).read_bytes(),pin['sha256'],mr1=True)
        frame_files = {n:archive['files'][n] for n in ('14_human_candidate_frames.csv','02_participant_enclosure_relations.csv')}
        frames = [dict(source_row=r,source_locator=h1.src.locator('r4_2',archive,'14_human_candidate_frames.csv',i,r)) for i,r in enumerate(table(frame_files,'14_human_candidate_frames.csv'),1)]
        enclosures = table(frame_files,'02_participant_enclosure_relations.csv')
    historical = {'hsa1/'+k:v for k,v in a.items()}
    historical.update({'hsa2_f/'+k:v for k,v in b.items()})
    historical.update({'r4_2/'+k:v for k,v in frame_files.items()})
    human = []
    for layer, name in [('HSA1','hsa1/01_structural_judgments.csv'),
                        ('HSA2','hsa2_f/hsa2/01_hsa2_structural_judgments.csv'),
                        ('HSA2-F','hsa2_f/01_final_human_adjudications.csv')]:
        for i,r in enumerate(table(historical,name),1):
            human.append(dict(layer=layer,record=r,locator=dict(member=name,data_row=i,member_sha256=sha(historical[name]),row_sha256=sha(canonical(r).encode()))))
    links = table(a,'02_judgment_source_links.csv')+table(fs['files'],'02_hsa2_source_links.csv')
    return dict(cfg=cfg,mode='SYNTHETIC_SCAFFOLD_ONLY' if self_test else 'ACCEPTED_REAL_SCAFFOLD',
                historical=historical,human=human,links=links,frozen=frozen,inputs=inputs,frames=frames,enclosures=enclosures)


def maps(s):
    cfg=s['cfg']; records={x['record']['judgment_id']:x for x in s['human']}
    require(len(records)==len(s['human']), 'duplicate human judgment ID')
    mapping={k:'H:'+cfg['explicit_record_aliases'].get(k,k) for k,v in records.items() if v['layer']!='HSA2-F'}
    for ident in cfg['explicit_record_aliases'].values():
        require(ident in records,'missing explicit alias antecedent')
    for ident,x in records.items():
        if x['layer']=='HSA2-F':
            mapping[ident]=mapping[cfg['final_ending_judgment']]
    return records,mapping


def evidence_ids(ids,s):
    # Full accepted context IDs, not one representative source.
    wanted=set(ids)
    return sorted({r['evidence_id'] for r in s['links'] if r['judgment_id'] in wanted})


def compile_scaffold(s):
    cfg=s['cfg']; records,mapping=maps(s)
    grouped=defaultdict(list)
    for ident,node in mapping.items():
        grouped[node].append(ident)
    nodes=[]
    for node,ids in sorted(grouped.items()):
        structural=[records[i] for i in ids if records[i]['layer']!='HSA2-F']
        active=max(structural,key=lambda x: {'HSA1':1,'HSA2':2}[x['layer']])['record']
        function=active['structural_function']
        require(function in cfg['function_types'],'unknown human function '+function)
        nodes.append(dict(node_id=node,node_type=cfg['function_types'][function],reference_start=active['reference_start'],reference_end=active['reference_end'],
            structural_function=function,human_speaker=active.get('human_speaker',''),all_historical_functions=sorted({x['record']['structural_function'] for x in structural}),
            textual_boundary=function in ('SPEECH_UNIT_ONSET','INTERNAL_SPEECH_ONSET','SCENE_ONSET','PARAGRAPH_ONSET','SPEECH_UNIT_END','PARALLEL_ENDING','DIALOGUE_CYCLE_ONSET'),
            group_origin='',authority=next(x['layer'] for x in structural if x['record'] is active),
            source_judgment_ids=sorted(ids),derived_from_judgments=[],source_evidence_ids=evidence_ids(ids,s),
            coverage_start='',coverage_end='',scope_note='Reference is the human judgment locus, not a computed unit coverage span.'))
    for g in cfg['groups']:
        require(all(i in records for i in g['source_judgment_ids']),'unknown grouping judgment')
        nodes.append(dict(node_id=g['node_id'],node_type=g['node_type'],reference_start=g['reference'],reference_end='',
            structural_function='NON_TEXTUAL_GROUP',human_speaker='',all_historical_functions=[],textual_boundary=False,group_origin=g['group_origin'],authority=g['group_origin'],
            source_judgment_ids=g['source_judgment_ids'],derived_from_judgments=g['source_judgment_ids'],source_evidence_ids=evidence_ids(g['source_judgment_ids'],s),
            coverage_start='',coverage_end='',scope_note=g['description']))
    nodes.append(dict(node_id='JOB_BOOK',node_type='TECHNICAL_ROOT',reference_start='',reference_end='',structural_function='TECHNICAL_ONLY',
        human_speaker='',all_historical_functions=[],textual_boundary=False,group_origin='TECHNICAL_ONLY',authority='TECHNICAL_ONLY',source_judgment_ids=[],derived_from_judgments=[],source_evidence_ids=[],
        coverage_start='',coverage_end='',scope_note='Computational graph root; not a discovered textual unit or human boundary.'))
    edges={}
    def edge(source,target,kind,ids,authority,dimension='',meaning='',original_relation='',position=''):
        require(kind in CLASSES,'unknown relation type')
        key=(source,target,kind,dimension)
        if key not in edges:
            edges[key]=dict(edge_id='E:'+sha(canonical(key).encode())[:20],source_node=source,target_node=target,
                edge_class=CLASSES[kind],relation_type=kind,dimension=dimension,semantic_meaning=meaning,
                original_relation=original_relation,membership_position=position,authorities=[],source_judgment_ids=[],source_evidence_ids=[])
        r=edges[key]
        r['source_judgment_ids']=sorted(set(r['source_judgment_ids'])|set(ids))
        r['authorities']=sorted(set(r['authorities'])|{authority})
        r['source_evidence_ids']=evidence_ids(r['source_judgment_ids'],s)
    for ident,x in records.items():
        if x['layer']=='HSA2-F':continue
        r=x['record']
        for p in h1.pairs([r]):
            target=p['related_judgment_id']
            if target:
                require(target in mapping,'missing exact related judgment '+target)
                require(records[target]['record']['reference_start']==p['related_reference'],'related reference/ID contradiction')
                target_node=mapping[target]
            else:
                binding=cfg['explicit_reference_targets'].get(ident)
                require(binding and binding['reference']==p['related_reference'],'unbound explicit human span target')
                target_node=binding['node_id']
            kind='PARALLEL_ENDING' if r['structural_function']=='PARALLEL_ENDING' and p['relation']=='PARALLEL_TO' else p['relation']
            edge(mapping[ident],target_node,kind,[ident],x['layer'],original_relation=p['relation'])
        if r['structural_function'] in ('NO_BOUNDARY','TRANSITION_COMPONENT'):
            edge(mapping[ident],mapping[ident],r['structural_function'],[ident],x['layer'])
    for g in cfg['groups']:
        for position,member in enumerate(g['members'],1):
            target=mapping.get(member,member)
            edge(target,g['node_id'],'GROUP_MEMBER_OF',g['source_judgment_ids'],g['group_origin'],position=position)
        if g['onset_judgment']:
            edge(mapping[g['onset_judgment']],g['node_id'],'CYCLE_ONSET_OF',[g['onset_judgment']], 'HSA2')
    intro=cfg['introduction']
    edge(mapping[intro['source']],intro['target'],'NARRATIVE_INTRODUCTION',intro['source_judgment_ids'],intro['authority'])
    for ident,x in records.items():
        if x['layer']!='HSA2-F':continue
        r=x['record']; target=cfg['final_target_judgments'][r['candidate_id']]
        edge(mapping[ident],mapping.get(target,target),r['selected_relation'],[ident],'HSA2-F',r['dimension'],r['semantic_meaning'])
    known=parents(list(edges.values()))
    for n in nodes:
        parent_ids=sorted(known.get(n['node_id'],set()))
        require(len(parent_ids)<=1,'multiple asserted direct parents require review: '+n['node_id'])
        n['direct_parent_ids']=parent_ids
        n['parentage_status']='NOT_APPLICABLE' if n['node_type']=='TECHNICAL_ROOT' else 'RESOLVED' if parent_ids else 'UNRESOLVED'
        if n['parentage_status']=='UNRESOLVED':
            edge(n['node_id'],'JOB_BOOK','TECHNICAL_ROOT_LINK',[],'TECHNICAL_ONLY')
    result=sorted(edges.values(),key=lambda r:r['edge_id'])
    require(all(r['source_node'] in {n['node_id'] for n in nodes} and r['target_node'] in {n['node_id'] for n in nodes} for r in result),'unknown node target')
    require(acyclic(result),'hierarchical cycle')
    return sorted(nodes,key=lambda n:n['node_id']),result


def parents(edges):
    result=defaultdict(set)
    for e in edges:
        if e['edge_class']!='HIERARCHY':continue
        if e['relation_type']=='CHILD_OF':result[e['source_node']].add(e['target_node'])
        elif e['relation_type']=='HIERARCHICALLY_ABOVE':result[e['target_node']].add(e['source_node'])
    return result


def acyclic(edges):
    pp=parents(edges)
    def visit(node,path):
        return node not in path and all(visit(p,path|{node}) for p in pp.get(node,()))
    return all(visit(n,set()) for n in pp)


def unresolved(nodes,edges,s):
    result=[]
    for n in nodes:
        if n['parentage_status']!='UNRESOLVED':continue
        related=[e for e in edges if e['edge_class']!='TECHNICAL' and n['node_id'] in (e['source_node'],e['target_node'])]
        events={json.loads(r['source_row']).get('participant_event_id') for r in s['links'] if r['judgment_id'] in n['source_judgment_ids']}
        frames=sorted({r['frame_id'] for r in s['enclosures'] if r['participant_event_id'] in events and r['frame_id']})
        result.append(dict(node_id=n['node_id'],reference=n['reference_start'],known_structural_function=n['structural_function'],
            direct_parent='UNRESOLVED',known_relation_ids=[e['edge_id'] for e in related],known_relations=[dict(edge_id=e['edge_id'],relation_type=e['relation_type'],source_node=e['source_node'],target_node=e['target_node']) for e in related],known_group_ids=sorted({e['target_node'] for e in related if e['source_node']==n['node_id'] and e['edge_class']=='MEMBERSHIP'}),
            existing_possible_frame_ids=frames,frame_authority='ACCEPTED_ANALYTICAL_FRAME_CONTEXT_NOT_PARENT',
            reason='No explicit CHILD_OF or HIERARCHICALLY_ABOVE assigns this node a direct parent. Group membership, continuation, introduction, closure and response are separate claims.',
            source_judgment_ids=n['source_judgment_ids'],source_evidence_ids=n['source_evidence_ids'],later_human_review_required=True))
    return result


def provenance(nodes,edges,s):
    records,_=maps(s)
    result=[]
    for kind,objects,key in [('NODE',nodes,'node_id'),('EDGE',edges,'edge_id')]:
        for obj in objects:
            for ident in obj['source_judgment_ids']:
                original=records[ident]
                result.append(dict(object_kind=kind,object_id=obj[key],judgment_id=ident,source_layer=original['layer'],
                    source_locator=deepcopy(original['locator']),source_record=deepcopy(original['record'])))
    return result


def build(s):
    nodes,edges=compile_scaffold(s)
    records,mapping=maps(s)
    m=dict(nodes=nodes,edges=edges,unresolved=unresolved(nodes,edges,s),provenance=provenance(nodes,edges,s),
        accounting=[dict(judgment_id=k,layer=v['layer'],scaffold_node_id=mapping[k],historical_record=deepcopy(v['record']),source_locator=deepcopy(v['locator'])) for k,v in sorted(records.items())],
        historical=deepcopy(s['historical']))
    m['negative']=negative_controls(m,s)
    m['report']=report(m,s)
    return m


def has(m,a,b,kind):
    return any(e['source_node']==a and e['target_node']==b and e['relation_type']==kind and e['edge_class']==CLASSES[kind] for e in m['edges'])


def negative_controls(m,s):
    nodes={n['node_id']:n for n in m['nodes']}
    checks={
        'NO_ZOPHAR_III':not any('ZOPHAR' in n.upper() for n in nodes),
        'NO_29_CHILD_27':not has(m,'H:HSA016','H:HSA015','CHILD_OF'),
        'NO_27_PARENT_29':not has(m,'H:HSA015','H:HSA016','HIERARCHICALLY_ABOVE'),
        'NO_28_BOUNDARY':nodes.get('H:HSA2-NO-28',{}).get('textual_boundary') is False,
        'NO_31_DIRECT_27':not has(m,'H:HSA017','H:HSA015','DIRECT_LOCAL_CLOSURE'),
        'NO_CLOSURE_COLLAPSE':has(m,'H:HSA017','H:HSA016','DIRECT_LOCAL_CLOSURE') and has(m,'H:HSA017','POST_DIALOGUE_JOB','TERMINATES_ENCLOSING_GROUP'),
        'NO_ELIHU_PEER_SUBORDINATION':all(not has(m,'H:'+i,'H:HSA020','CHILD_OF') for i in ('HSA021','HSA022','HSA023')),
        'NO_40_1_SAME_LEVEL':all(not has(m,'H:HSA026','H:'+i,'SAME_LEVEL_SIBLING') for i in ('HSA025','HSA028')),
        'NO_42_16_NEW_PARAGRAPH':nodes.get('H:HSA031',{}).get('structural_function')=='NO_BOUNDARY',
        'NO_42_10_12_BOUNDARIES':not any(n['reference_start'] in ('42:10','42:12') and n['textual_boundary'] for n in m['nodes']),
        'NO_37_24_PARENT_38_1':not has(m,'H:HSA025','H:HSA024','CHILD_OF') and not has(m,'H:HSA024','H:HSA025','HIERARCHICALLY_ABOVE'),
        'NO_31_40_PARENT_38_1':not has(m,'H:HSA025','H:HSA017','CHILD_OF') and not has(m,'H:HSA017','H:HSA025','HIERARCHICALLY_ABOVE'),
        'NO_HUMAN_ENDING_PROMOTED_TO_MR1':not any(e['relation_type']=='MR1_EXPLICIT_CLOSURE' for e in m['edges']) and m['historical']==s['historical'],
        'NO_HUMAN_REGISTRY_REWRITE':m['historical']==s['historical']}
    return [dict(control=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def report(m,s):
    nn={n['node_id']:n for n in m['nodes']}
    groups=[n for n in m['nodes'] if n['group_origin'] in ('HUMAN_GROUP','HUMAN_RELATION_DERIVED')]
    members=defaultdict(list)
    for e in m['edges']:
        if e['edge_class']=='MEMBERSHIP':members[e['target_node']].append((e['membership_position'],e['source_node']))
    def label(n):
        reference=n['reference_start']+('–'+n['reference_end'] if n['reference_end'] and n['reference_start']!=n['reference_end'] else '')
        return f'{n["node_id"]} | {reference or "no new textual onset"} | {n["structural_function"]}'+(' | '+n['human_speaker'] if n['human_speaker'] else '')+f' | direct parent: {n["parentage_status"]}'
    lines=['# R4.3 — Human-grounded whole-book partial scaffold','',f'Mode: **{s["mode"]}**','',
        'This is a partial compiler output, not a completed Job tree or new human adjudication.',
        '59 historical human records remain separate. Explicit record aliases combine only named restatements;',
        'they do not infer identity from reference, Hebrew text, speaker or marker similarity.',
        'Reference columns describe judgment loci, not automatically inferred speech-end coverage.', '',
        '## Scaffold display conventions','',
        '`[RESOLVED]` means an explicit hierarchical relation. `[GROUP]` and its indentation mean MEMBERSHIP ONLY.',
        '`[OVERLAY]` means a typed non-parent relation. `[UNRESOLVED]` does not acquire a parent from indentation.',
        '`[TECHNICAL]` JOB_BOOK connects unresolved nodes for graph storage, never HUMAN_CHILD_OF.', '',
        '```text','[TECHNICAL] JOB_BOOK — computational root, not a textual unit','```','',
        '## Reviewed group membership (not resolved direct parentage)','']
    for g in groups:
        lines += ['```text','[GROUP; NON-TEXTUAL; parent UNRESOLVED] '+g['node_id']]
        if g['node_id']=='ELIHU_SPEECH_SEQUENCE':
            lines += ['  [DESCRIPTIVE] introduced by H:HSA019 (32:2–5); introduction is not a peer speech onset or a forced parent']
        for _,ident in sorted(members[g['node_id']]):
            lines.append('  [MEMBERSHIP ONLY; '+nn[ident]['parentage_status']+'] '+label(nn[ident]))
        lines += ['```',g['scope_note'],'']
    lines += ['## Explicit resolved hierarchy only','','```text']
    for e in m['edges']:
        if e['edge_class']=='HIERARCHY':
            child,parent=(e['source_node'],e['target_node']) if e['relation_type']=='CHILD_OF' else (e['target_node'],e['source_node'])
            lines += [label(nn[parent]),'  [RESOLVED CHILD] '+label(nn[child])+' | source '+','.join(e['source_judgment_ids'])]
    lines += ['```','','## Other anchors and typed overlays','',
        'The two major YHWH onsets (38:1/40:6) and Job response onsets (40:3/42:1) retain their respective sibling relations.',
        '32:1 remains a transition component, not an Elihu onset or a child/target of 31:40.',
        '37:24 remains SPEECH_UNIT_END; no new direct closure target is assigned. Response/adjacency never assigns a parent.',
        '42:7 remains PARAGRAPH_ONSET and 42:16 continues within it. 42:10/42:12 are not promoted to boundaries.',
        '1:22/2:10 are human PARALLEL_ENDING, not MR1 explicit closures. 3:1 remains outside the cycle groups.', '',
        '| Class | Source → target | Relation | Source judgments |','| --- | --- | --- | --- |']
    for e in m['edges']:
        if e['edge_class'] not in ('HIERARCHY','TECHNICAL','MEMBERSHIP','HORIZONTAL'):
            lines.append('| '+' | '.join([e['edge_class'],e['source_node']+' → '+e['target_node'],e['relation_type']+(' ('+e['semantic_meaning']+')' if e['semantic_meaning'] else ''),', '.join(e['source_judgment_ids'])])+' |')
    lines += ['', 'The HSA2-F active closure edges coexist with all original HSA2 UNRESOLVED records under `history/`.',
        'No preceding-verse endings, missing speeches, response antecedents or extra participant identities are generated.', '',
        '## UNRESOLVED GLOBAL SEAMS','',
        'Every row below lacks an explicit direct parent. Known membership/continuation may constrain later review,',
        'but does not resolve that distinct question. All rows require later human review; there is no candidate ranking.',
        'Analytical candidate frames are context only, joined through exact accepted participant-event links.', '',
        '| Node | Reference | Known function | Known groups | Direct parent |',
        '| --- | --- | --- | --- | --- |']
    for r in m['unresolved']:
        lines.append('| '+' | '.join([r['node_id'],r['reference'],r['known_structural_function'],', '.join(r['known_group_ids']),'UNRESOLVED'])+' |')
    lines += ['', '## Counts and provenance','',
        f'Nodes: {len(m["nodes"])} including one technical root. Types: `{canonical(dict(Counter(n["node_type"] for n in m["nodes"])))}`.',
        f'Edges: {len(m["edges"])}. Classes: `{canonical(dict(Counter(e["edge_class"] for e in m["edges"])))}`.',
        f'Unresolved direct-parent cases: {len(m["unresolved"])}. No assertion of complete global parentage.',
        'All node/edge provenance is in 07; all 59 original rows and their mapping are in 10. Historical files,',
        'including complete human source/context links and nested manifests, remain byte-identical under history/.',
        'Cycle 1/2/3 retain 6/6/4 speech members. No Zophar III or missing-speech placeholder exists.',
        'Next stage: human review of the enumerated unresolved attachments; no automatic parent completion.', '']
    return '\n'.join(lines)


def gates(m,s):
    expected_nodes,expected_edges=compile_scaffold(s)
    records,mapping=maps(s)
    nodes={n['node_id']:n for n in m['nodes']}
    cfg=s['cfg']; checks={}
    def frozen(paths):
        selected=[r for r in s['frozen'] if r['path'] in paths]
        return len(selected)==len(paths) and all(r['actual']==r['expected']==cfg['frozen_files'][r['path']] for r in selected)
    def peers(ids):
        return all(has(m,mapping[a],mapping[b],'SAME_LEVEL_SIBLING') for a in ids for b in ids if a!=b)
    for layer,paths in [('HSA1',[h1.CSV,h1.MD]),('HSA2',[h2.CSV,h2.MD]),('HSA2_F',[final.CSV,final.MD])]:
        checks[layer+'_FROZEN']=frozen([p.relative_to(ROOT).as_posix() for p in paths])
    hist='hsa2_f/hsa2/03_closure_target_candidate_relations.csv'
    checks['HISTORICAL_UNRESOLVED_INTACT']=m['historical']==s['historical'] and all(r['selected_relation']=='UNRESOLVED' and r['review_status']=='UNREVIEWED' for r in table(m['historical'],hist))
    final_edges=[r for r in m['edges'] if 'HSA2-F' in r['authorities']]
    expected_final=[r for r in expected_edges if 'HSA2-F' in r['authorities']]
    checks['ACTIVE_FINAL_PRECEDENCE']=final_edges==expected_final and len(final_edges)==3
    checks['59_HUMAN_RECORDS_ACCOUNTED']=Counter(r['layer'] for r in m['accounting'])==Counter(cfg['regression']['human_counts']) and {r['judgment_id'] for r in m['accounting']}==set(records) and all(r['historical_record']==records[r['judgment_id']]['record'] and r['scaffold_node_id']==mapping[r['judgment_id']] for r in m['accounting'])
    checks['EVERY_NODE_PROVENANCE']=all(n['source_judgment_ids'] and all(i in records for i in n['source_judgment_ids']) for n in m['nodes'] if n['node_type']!='TECHNICAL_ROOT') and m['provenance']==provenance(m['nodes'],m['edges'],s)
    checks['EVERY_NONTECH_EDGE_PROVENANCE']=all(e['source_judgment_ids'] and all(i in records for i in e['source_judgment_ids']) for e in m['edges'] if e['edge_class']!='TECHNICAL')
    checks['DERIVED_GROUP_PROVENANCE']=all(n['derived_from_judgments']==n['source_judgment_ids'] and bool(n['derived_from_judgments']) for n in m['nodes'] if n['node_type'] in ('HUMAN_GROUP','DERIVED_SCAFFOLD_GROUP'))
    for group,count in cfg['regression']['cycle_counts'].items():
        members=[e['source_node'] for e in m['edges'] if e['edge_class']=='MEMBERSHIP' and e['target_node']==group]
        expected=[e['source_node'] for e in expected_edges if e['edge_class']=='MEMBERSHIP' and e['target_node']==group]
        checks[group+'_MEMBERS']=len(members)==count and members==expected and all(nodes.get(i,{}).get('node_type')=='SPEECH_UNIT' for i in members)
    checks['NO_ZOPHAR_III']=set(nodes)=={n['node_id'] for n in expected_nodes} and not any('ZOPHAR' in n.upper() for n in nodes)
    checks['CYCLE_ONSET_PEERS']=peers(['HSA2-CYCLE-1','HSA2-CYCLE-2','HSA2-CYCLE-3'])
    checks['27_29_PEERS']=peers(['HSA015','HSA016']) and not has(m,'H:HSA016','H:HSA015','CHILD_OF') and not has(m,'H:HSA015','H:HSA016','HIERARCHICALLY_ABOVE')
    checks['28_CONTINUATION']=has(m,mapping['HSA2-NO-28'],mapping['HSA015'],'CONTINUES_WITHIN') and nodes.get(mapping['HSA2-NO-28'],{}).get('structural_function')=='NO_BOUNDARY'
    checks['THREE_FINAL_CLOSURE_RELATIONS']=has(m,'H:HSA017','H:HSA016','DIRECT_LOCAL_CLOSURE') and has(m,'H:HSA017','H:HSA015','NO_DIRECT_RELATION') and has(m,'H:HSA017','POST_DIALOGUE_JOB','TERMINATES_ENCLOSING_GROUP') and not has(m,'H:HSA017','H:HSA015','DIRECT_LOCAL_CLOSURE')
    checks['LOCAL_HIGHER_SEPARATE']=len(final_edges)==3 and {e['edge_class'] for e in final_edges}=={'LOCAL_CLOSURE','NEGATIVE','HIGHER_TERMINATION'} and {e['dimension'] for e in final_edges}=={'DIRECT_CLOSURE_TARGET','HIGHER_ORDER_TERMINAL_EFFECT'}
    checks['ELIHU_FOUR_PEERS']=peers(['HSA020','HSA021','HSA022','HSA023']) and all(has(m,'H:'+i,'ELIHU_SPEECH_SEQUENCE','GROUP_MEMBER_OF') for i in ('HSA020','HSA021','HSA022','HSA023'))
    checks['40_1_CHILD_38_1']=has(m,'H:HSA026','H:HSA025','CHILD_OF') and nodes.get('H:HSA026',{}).get('direct_parent_ids')==['H:HSA025']
    checks['YHWH_PEERS']=peers(['HSA025','HSA028'])
    checks['JOB_RESPONSE_PEERS']=peers(['HSA027','HSA029'])
    checks['42_16_CONTINUATION']=has(m,'H:HSA031','H:HSA030','CONTINUES_WITHIN') and nodes.get('H:HSA031',{}).get('textual_boundary') is False
    actual_parents=[e for e in m['edges'] if e['edge_class']=='HIERARCHY']
    true_parents=[e for e in expected_edges if e['edge_class']=='HIERARCHY']
    checks['NO_RESPONSE_TO_PARENT']=actual_parents==true_parents and not any(e['relation_type']=='RESPONSE' and e['edge_class']=='HIERARCHY' for e in m['edges'])
    checks['NO_ADJACENCY_PARENT']=parents(m['edges'])==parents(expected_edges) and actual_parents==true_parents
    checks['UNRESOLVED_PARENTAGE_EXPLICIT']=m['unresolved']==unresolved(expected_nodes,expected_edges,s) and all(n['parentage_status']==next(x['parentage_status'] for x in expected_nodes if x['node_id']==n['node_id']) and n['direct_parent_ids']==next(x['direct_parent_ids'] for x in expected_nodes if x['node_id']==n['node_id']) for n in m['nodes'] if n['node_id'] in {x['node_id'] for x in expected_nodes})
    checks['NO_PARENT_RANKING']=all(not any(t in k.lower() for t in ('score','rank','confidence','best_parent')) for rows in (m['nodes'],m['edges'],m['unresolved']) for r in rows for k in r)
    mr_paths=[p for p in cfg['frozen_files'] if 'mr1' in p.lower()]
    checks['NO_NEW_MR1_RULE']=frozen(mr_paths) and not any(e['relation_type']=='MR1_EXPLICIT_CLOSURE' for e in m['edges'])
    checks['NO_HUMAN_MUTATION']=m['historical']==s['historical'] and all(r['historical_record']==records.get(r['judgment_id'],{}).get('record') for r in m['accounting'])
    checks['TECHNICAL_ROOT_ONLY']=nodes.get('JOB_BOOK',{}).get('node_type')=='TECHNICAL_ROOT' and nodes['JOB_BOOK']['textual_boundary'] is False and {e['source_node'] for e in m['edges'] if e['relation_type']=='TECHNICAL_ROOT_LINK'}=={r['node_id'] for r in m['unresolved']} and all(e['edge_class']=='TECHNICAL' and e['target_node']=='JOB_BOOK' for e in m['edges'] if e['relation_type']=='TECHNICAL_ROOT_LINK')
    checks['GROUPS_NOT_TEXTUAL']=all(n['textual_boundary'] is False and n['group_origin'] in ('HUMAN_GROUP','HUMAN_RELATION_DERIVED') for n in m['nodes'] if n['node_type'] in ('HUMAN_GROUP','DERIVED_SCAFFOLD_GROUP'))
    checks['ELIHU_INTRO_NOT_PEER_OR_PARENT']=has(m,'H:HSA019','ELIHU_SPEECH_SEQUENCE','NARRATIVE_INTRODUCTION') and nodes.get('H:HSA019',{}).get('structural_function')=='NARRATIVE_INTRODUCTION' and not any(e['edge_class'] in ('HIERARCHY','HORIZONTAL') and 'H:HSA019' in (e['source_node'],e['target_node']) for e in m['edges'])
    checks['NO_FICTIONAL_CLOSURE_SPANS']=all(n['coverage_start']==n['coverage_end']=='' for n in m['nodes']) and {e['edge_id'] for e in m['edges'] if e['edge_class'] in ('LOCAL_CLOSURE','HIGHER_TERMINATION')}=={e['edge_id'] for e in expected_edges if e['edge_class'] in ('LOCAL_CLOSURE','HIGHER_TERMINATION')}
    checks['SOURCE_LINKS_LOSSLESS']=m['historical']==s['historical'] and m['provenance']==provenance(m['nodes'],m['edges'],s)
    checks['EXACT_TYPED_RELATIONS']=m['edges']==expected_edges and all(e['edge_class']==CLASSES.get(e['relation_type']) for e in m['edges'])
    checks['ACYCLIC_HIERARCHY']=acyclic(m['edges'])
    checks['NEGATIVE_CONTROLS']=m['negative']==negative_controls(m,s) and all(r['status']=='PASS' for r in m['negative'])
    checks['FROZEN_CORES']=len(s['frozen'])==len(cfg['frozen_files']) and frozen(list(cfg['frozen_files']))
    checks['REPORT_NO_FALSE_PARENTAGE']=m['report']==report(m,s) and all(f'| {r["node_id"]} |' in m['report'] for r in m['unresolved'])
    checks['DETERMINISTIC_OUTPUT']=m==build(s)
    return [dict(gate=k,status='PASS' if ok else 'FAIL') for k,ok in checks.items()]


def serialize(m,s):
    gg=gates(m,s)
    require(all(r['status']=='PASS' for r in gg),canonical([r for r in gg if r['status']!='PASS']))
    files={'history/'+k:v for k,v in m['historical'].items()}
    for name,rows,fields in [
        ('01_whole_book_hierarchy_nodes.csv',m['nodes'],None),
        ('02_whole_book_hierarchy_edges.csv',m['edges'],None),
        ('03_unresolved_parentage.csv',m['unresolved'],None),
        ('05_group_membership.csv',[e for e in m['edges'] if e['edge_class']=='MEMBERSHIP'],None),
        ('06_overlay_relations.csv',[e for e in m['edges'] if e['edge_class'] not in ('MEMBERSHIP','HIERARCHY','TECHNICAL')],None),
        ('07_source_provenance.csv',m['provenance'],None),
        ('08_negative_controls.csv',m['negative'],None),
        ('10_human_judgment_accounting.csv',m['accounting'],None),
        ('11_accepted_frame_context.csv',s['frames'],['source_row','source_locator'])]:
        files[name]=h1.util.csv_bytes(rows,fields)
    files[REPORT]=m['report'].encode()
    meta=dict(version='R4.3',mode=s['mode'],status='PASS',gate_count=len(gg)+1,
        counts=dict(nodes=len(m['nodes']),node_types=dict(Counter(n['node_type'] for n in m['nodes'])),edges=len(m['edges']),
            edge_classes=dict(Counter(e['edge_class'] for e in m['edges'])),edge_types=dict(Counter(e['relation_type'] for e in m['edges'])),
            unresolved=len(m['unresolved']),human_judgments=dict(Counter(r['layer'] for r in m['accounting'])),provenance_links=len(m['provenance'])),
        source_receipts=s['inputs'],frozen_receipts=s['frozen'],code_sha256=sha(Path(__file__).read_bytes()),config_sha256=sha(CONFIG.read_bytes()),
        authority_precedence=['HSA2-F','HSA2','HSA1','ACCEPTED_ANALYTICAL_EVIDENCE'],claim='PARTIAL_SCAFFOLD_NOT_COMPLETE_GLOBAL_PARENTAGE')
    files['90_run_metadata.json']=h1.util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv',None)
        files['99_manifest_sha256.csv']=h1.util.csv_bytes([dict(file=n,sha256=sha(v)) for n,v in sorted(files.items())])
    seal();gg.append(h1.util.manifest_gate(files));files['09_gates.csv']=h1.util.csv_bytes(gg);seal()
    require(h1.util.manifest_ok(files),'output manifest')
    return files


def publish(files,out):
    out=Path(out).resolve();zp=out.with_name(out.name+'_results.zip');log=out.with_name(out.name+'_run.log')
    require(not any(p.exists() for p in (out,zp,log)),'output exists')
    require(h1.util.manifest_ok(files),'publication manifest')
    for n,b in files.items():
        path=out/n;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    with zipfile.ZipFile(zp,'w') as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    with zipfile.ZipFile(zp) as z:require(z.testzip() is None and {n:z.read(n) for n in z.namelist()}==files,'ZIP integrity')
    require({p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}==files,'disk integrity')
    meta=json.loads(files['90_run_metadata.json'])
    log.write_text(f'R4.3 PASS\nMode {meta["mode"]}\nGates {meta["gate_count"]} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n',encoding='utf-8')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--self-test',action='store_true');a=p.parse_args(argv)
    s=load(a.self_test);files=serialize(build(s),s)
    require(files==serialize(build(s),s),'deterministic serialization')
    require(frozen_receipts(s['cfg'])==s['frozen'],'frozen source changed during run')
    for r in s['inputs']:require(sha((ROOT/r['path']).read_bytes())==r['expected'],'input changed during run')
    publish(files,a.out);print('R4.3 PASS '+str(Path(a.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
