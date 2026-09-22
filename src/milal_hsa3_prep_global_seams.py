"""Review-only triage of frozen R4.3 rows; no new structural assertions."""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import sys
import zipfile

import milal_r4_3_hierarchy_scaffold as r43
from milal_r3c_0_2_reviewability import REVIEW_FIELDS

ROOT, sha, canonical = r43.ROOT, r43.sha, r43.canonical
CONFIG = ROOT / 'config/hsa3_prep_job.json'
REPORT = '04_global_seam_review_packet.md'
CATEGORIES = ('TRUE_GLOBAL_SEAM', 'ROLE_ALIAS_OR_SAME_TEXTUAL_LOCUS',
              'KNOWN_CONTAINER_BUT_DIRECT_PARENT_UNRESOLVED', 'GROUP_PARENTAGE_UNRESOLVED',
              'LOCAL_RELATION_ALREADY_CONSTRAINS_STRUCTURE', 'TECHNICAL_OR_REPRESENTATIONAL_CASE')
SOURCE_TABLES = {'nodes':'01_whole_book_hierarchy_nodes.csv', 'edges':'02_whole_book_hierarchy_edges.csv',
                 'unresolved':'03_unresolved_parentage.csv', 'provenance':'07_source_provenance.csv',
                 'accounting':'10_human_judgment_accounting.csv', 'frames':'11_accepted_frame_context.csv'}


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-PREP STOP: '+message)


def decode_rows(data):
    rows = r43.h1.read_csv(data)
    for row in rows:
        for key, value in row.items():
            if value.startswith(('[', '{')):
                row[key] = json.loads(value)
            elif value in ('True', 'False'):
                row[key] = value == 'True'
    return rows


def load(self_test=False):
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    frozen = r43.frozen_receipts(cfg)
    require(all(x['actual']==x['expected'] for x in frozen), 'frozen file changed')
    if self_test:
        source = r43.load(True)
        files = r43.serialize(r43.build(source), source)
        receipts = []
    else:
        pin = cfg['archive']
        archive = r43.h1.src.archive((ROOT/pin['path']).read_bytes(), pin['sha256'], mr1=True)
        files = archive['files']
        meta = json.loads(files['90_run_metadata.json'])
        require(meta['version']=='R4.3' and meta['mode']=='ACCEPTED_REAL_SCAFFOLD' and meta['status']=='PASS', 'unaccepted R4.3')
        require(all(g['status']=='PASS' for g in decode_rows(files['09_gates.csv'])), 'R4.3 gate failure')
        # Verify the accepted upstream chain, without compiling or mutating R4.3.
        source = r43.load(False)
        require({k.removeprefix('history/'):v for k,v in files.items() if k.startswith('history/')}==source['historical'], 'R4.3 source bytes differ')
        receipts = deepcopy(source['inputs'])+[dict(role='r4_3',path=pin['path'],expected=pin['sha256'])]
    require(r43.h1.util.manifest_ok(files), 'R4.3 manifest')
    s = dict(cfg=cfg, files=files, frozen=frozen, receipts=receipts,
             mode='SYNTHETIC_REVIEW_ONLY' if self_test else 'ACCEPTED_REAL_REVIEW_ONLY')
    for key, name in SOURCE_TABLES.items():
        s[key] = decode_rows(files[name])
    s['links'] = []
    for name in ('history/hsa1/02_judgment_source_links.csv', 'history/hsa2_f/hsa2/02_hsa2_source_links.csv'):
        for i, row in enumerate(decode_rows(files[name]), 1):
            s['links'].append(dict(record=row, member=name, data_row=i))
    validate_source(s)
    return s


def validate_source(s):
    ids = [n['node_id'] for n in s['nodes']]
    require(len(ids)==len(set(ids)), 'duplicate node identity')
    require(all(e['source_node'] in ids and e['target_node'] in ids for e in s['edges']), 'dangling source edge')
    unresolved = [u['node_id'] for u in s['unresolved']]
    require(len(unresolved)==len(set(unresolved)), 'duplicate unresolved identity')
    require(set(unresolved)=={n['node_id'] for n in s['nodes'] if n['parentage_status']=='UNRESOLVED'}, 'unaccountable unresolved row')
    for key, rows in [('nodes',s['nodes']),('relations',s['edges']),('unresolved',s['unresolved']),('human_records',s['accounting'])]:
        require(len(rows)==s['cfg']['regression'][key], 'source regression '+key)


def reference(n):
    a,b = n['reference_start'],n['reference_end']
    return a+('–'+b if b and b!=a else '')


def role_audit(s):
    loci = defaultdict(list)
    for n in s['nodes']:
        if not n['group_origin'] and n['reference_start']:
            loci[(n['reference_start'],n['reference_end'])].append(n)
    authorized = {frozenset(pair) for pair in s['cfg']['role_pairs']}
    result = []
    for locus, nodes in sorted(loci.items()):
        if len(nodes)<2:
            continue
        shared = sorted(set.intersection(*(set(n['source_evidence_ids']) for n in nodes)))
        exact = frozenset(n['node_id'] for n in nodes) in authorized and bool(shared)
        result.append(dict(locus=reference(nodes[0]), node_ids=sorted(n['node_id'] for n in nodes),
            roles={n['node_id']:n['structural_function'] for n in nodes},
            judgments={n['node_id']:n['source_judgment_ids'] for n in nodes}, shared_source_evidence_ids=shared,
            audit_status='SAME_TEXTUAL_LOCUS_DIFFERENT_STRUCTURAL_ROLE' if exact else 'UNVERIFIED_SAME_REFERENCE_ONLY',
            identity_basis='EXPLICIT_RESEARCHER_PAIR_AND_SHARED_EXACT_EVIDENCE' if exact else 'NO_IDENTITY_INFERENCE',
            separate_parentage_review='DEFER_ROLE_REPRESENTATION_TO_SHARED_CASE' if exact else 'REQUIRES_SEPARATE_AUDIT',
            historical_records_merged=False))
    return result


def dependency_arcs(s):
    """Directions mean review dependence, never an inferred structural edge."""
    arcs = []
    for e in s['edges']:
        kind = e['relation_type']
        if kind in ('GROUP_MEMBER_OF','CONTINUES_WITHIN','CYCLE_ONSET_OF','TERMINATES_ENCLOSING_GROUP','CHILD_OF'):
            arcs.append(dict(node=e['source_node'], context=e['target_node'], edge_id=e['edge_id'], relation=kind))
        elif kind=='HIERARCHICALLY_ABOVE':
            arcs.append(dict(node=e['target_node'], context=e['source_node'], edge_id=e['edge_id'], relation=kind))
    return sorted(arcs, key=canonical)


def reachable(start, arcs):
    seen, paths = {start}, []
    todo = [start]
    while todo:
        node = todo.pop(0)
        for arc in arcs:
            if arc['node']==node:
                paths.append(arc)
                if arc['context'] not in seen:
                    seen.add(arc['context']); todo.append(arc['context'])
    return seen, sorted({a['edge_id']:a for a in paths}.values(), key=canonical)


def triage(s, aliases):
    nn = {n['node_id']:n for n in s['nodes']}
    alias_ids = {i for a in aliases if a['identity_basis']=='EXPLICIT_RESEARCHER_PAIR_AND_SHARED_EXACT_EVIDENCE' for i in a['node_ids']}
    arcs = dependency_arcs(s)
    rows = []
    for u in s['unresolved']:
        ident = u['node_id']; n = nn[ident]
        outgoing = [e for e in s['edges'] if e['source_node']==ident]
        groups = [e['target_node'] for e in outgoing if e['relation_type']=='GROUP_MEMBER_OF']
        local = [e for e in outgoing if e['relation_type'] in ('CONTINUES_WITHIN','DIRECT_LOCAL_CLOSURE','TERMINATES_ENCLOSING_GROUP')]
        if n['node_type'] in ('HUMAN_GROUP','DERIVED_SCAFFOLD_GROUP'):
            category = CATEGORIES[3]
        elif ident in alias_ids:
            category = CATEGORIES[1]
        elif groups:
            category = CATEGORIES[2]
        elif local:
            category = CATEGORIES[4]
        elif n['node_type']=='TECHNICAL_ROOT':
            category = CATEGORIES[5]
        else:
            category = CATEGORIES[0]
        contexts, path = reachable(ident, arcs)
        owners = sorted({s['cfg']['primary_scope_seeds'][i] for i in contexts if i in s['cfg']['primary_scope_seeds']})
        # Multiple possible display owners are not ranked; retain an explicit residual case.
        owner = owners[0] if len(owners)==1 else 'SEAM_EXTRA_'+ident.replace(':','_')
        needed = 'CASE_LEVEL_REVIEW_REQUIRED' if category in (CATEGORIES[0],CATEGORIES[3]) else 'DEFER_PENDING_CASE_REVIEW'
        rows.append(dict(unresolved_node_id=ident, reference=u['reference'], triage_category=category,
            controlling_case_id=owner, owner_basis='EXPLICIT_REVIEW_SCOPE_SEED_OR_TYPED_DEPENDENCY_PATH' if len(owners)==1 else 'NO_UNIQUE_REVIEW_SCOPE',
            already_known_container=groups, already_known_local_relation=[e['edge_id'] for e in local],
            known_structural_function=u['known_structural_function'], direct_parent='UNRESOLVED',
            dependency_path=path, dependency_context_nodes=sorted(contexts-{ident}),
            separate_human_decision_needed=needed,
            direct_parent_is_distinct_unanswered_question=True,
            separate_adjudication_adds_information='ONLY_IF_EXACT_PARENT_REPRESENTATION_REMAINS_NEEDED_AFTER_CASE_REVIEW',
            rationale='Review scheduling only. Existing '+category+' evidence can be reviewed together; no later decision is guaranteed to settle any member direct parent.',
            source_judgment_ids=u['source_judgment_ids'], source_evidence_ids=u['source_evidence_ids']))
    return rows


def cases(s, rows):
    nn = {n['node_id']:n for n in s['nodes']}
    arcs = dependency_arcs(s)
    result = []
    definitions = deepcopy(s['cfg']['seams'])
    known = {c['case_id'] for c in definitions}
    for row in rows:
        if row['controlling_case_id'] not in known:
            definitions.append(dict(case_id=row['controlling_case_id'], title='Additional source-derived unresolved review scope',
                seed_nodes=[row['unresolved_node_id']], question='No unique dependency scope was established. Audit this remaining structural attachment without choosing a parent.'))
            known.add(row['controlling_case_id'])
    for d in definitions:
        require(all(i in nn for i in d['seed_nodes']), 'unknown review seed')
        nodes = set(d['seed_nodes'])
        for ident in nn:
            if reachable(ident,arcs)[0] & nodes:
                nodes.add(ident)
        # Stable fixed point, independent of source row ordering.
        while True:
            expanded = nodes | {a['node'] for a in arcs if a['context'] in nodes}
            if expanded==nodes: break
            nodes=expanded
        related = [e for e in s['edges'] if e['edge_class']!='TECHNICAL' and (e['source_node'] in nodes or e['target_node'] in nodes)]
        primary = [r['unresolved_node_id'] for r in rows if r['controlling_case_id']==d['case_id']]
        covered = [r['unresolved_node_id'] for r in rows if r['unresolved_node_id'] in nodes]
        ids = sorted({i for n in nodes for i in nn[n]['source_judgment_ids']} | {i for e in related for i in e['source_judgment_ids']})
        result.append(dict(case_id=d['case_id'], panel_kind='OPEN_ATTACHMENT_REVIEW_CASE', title=d['title'],
            seed_nodes=d['seed_nodes'], involved_nodes=sorted(nodes), references={i:reference(nn[i]) for i in sorted(nodes)},
            source_judgment_ids=ids, relation_ids=[e['edge_id'] for e in related],
            positive_constraint_ids=[e['edge_id'] for e in related if e['edge_class']!='NEGATIVE'],
            negative_constraint_ids=[e['edge_id'] for e in related if e['edge_class']=='NEGATIVE'],
            primary_unresolved_rows=primary, participating_unresolved_rows=covered,
            primary_row_count=len(primary), participating_row_count=len(covered),
            question=d['question'], candidate_parents=[], valid_outcomes=['HUMAN_SUPPLIED_RELATION_WITH_SOURCE','UNRESOLVED','INSUFFICIENT_EVIDENCE'],
            redundant_decisions='Do not re-decide listed accepted relations or separately re-ask every member global attachment. Exact direct parentage may still require later representation review.',
            automatic_resolution=False, **{k:'UNREVIEWED' if k=='review_status' else '' for k in REVIEW_FIELDS}))
    return result


def group_audit(s, rows):
    by_id = {r['unresolved_node_id']:r for r in rows}
    result = []
    for n in s['nodes']:
        if n['node_type'] not in ('HUMAN_GROUP','DERIVED_SCAFFOLD_GROUP'): continue
        ident = n['node_id']
        members = [e['source_node'] for e in s['edges'] if e['relation_type']=='GROUP_MEMBER_OF' and e['target_node']==ident]
        dependents = [r['unresolved_node_id'] for r in rows if ident in r['dependency_context_nodes']]
        result.append(dict(group_id=ident, group_origin=n['group_origin'], textual_boundary=n['textual_boundary'],
            source_judgment_ids=n['source_judgment_ids'], members=sorted(members),
            known_relation_ids=[e['edge_id'] for e in s['edges'] if e['edge_class']!='TECHNICAL' and ident in (e['source_node'],e['target_node'])],
            controlling_case_id=by_id[ident]['controlling_case_id'], dependent_unresolved_rows=dependents,
            needs_own_global_parent='OPEN_REPRESENTATION_QUESTION_NOT_ASSUMED',
            could_reduce_repeated_review=bool(dependents), automatic_member_resolution=False))
    return result


def evidence_links(s, cc):
    result = []
    def add(case, kind, ident, member, row_index, raw_row):
        result.append(dict(case_id=case, evidence_kind=kind, evidence_id=ident, source_member=member,
            data_row=row_index, member_sha256=sha(s['files'][member]),
            row_sha256=sha(canonical(raw_row).encode()), source_row=raw_row))
    raw_cache = {name:r43.h1.read_csv(data) for name,data in s['files'].items() if name.endswith('.csv')}
    for c in cc:
        ids = set(c['source_judgment_ids']); nodes = set(c['involved_nodes'])
        for i,row in enumerate(raw_cache[SOURCE_TABLES['accounting']],1):
            if row['judgment_id'] in ids:
                add(c['case_id'],'HUMAN_JUDGMENT',row['judgment_id'],SOURCE_TABLES['accounting'],i,row)
        for i,row in enumerate(raw_cache[SOURCE_TABLES['edges']],1):
            if row['edge_id'] in c['relation_ids']:
                add(c['case_id'],'ACCEPTED_TYPED_RELATION',row['edge_id'],SOURCE_TABLES['edges'],i,row)
        for x in s['links']:
            if x['record']['judgment_id'] in ids:
                row = raw_cache[x['member']][x['data_row']-1]
                add(c['case_id'],'ACCEPTED_SOURCE_CONTEXT',row['evidence_id'],x['member'],x['data_row'],row)
        wanted_frames = {f for u in s['unresolved'] if u['node_id'] in nodes for f in u['existing_possible_frame_ids']}
        for i,frame in enumerate(s['frames'],1):
            if frame['source_row'].get('frame_id') in wanted_frames:
                add(c['case_id'],'ACCEPTED_FRAME_CONTEXT',frame['source_row']['frame_id'],SOURCE_TABLES['frames'],i,raw_cache[SOURCE_TABLES['frames']][i-1])
    return result


def build(s):
    aliases = role_audit(s)
    rows = triage(s,aliases)
    cc = cases(s,rows)
    memberships = {r['unresolved_node_id']:[c['case_id'] for c in cc if r['unresolved_node_id'] in c['participating_unresolved_rows']] for r in rows}
    crosswalk = [dict(unresolved_node_id=r['unresolved_node_id'], source_data_row=i,
        source_row_sha256=sha(canonical(r43.h1.read_csv(s['files'][SOURCE_TABLES['unresolved']])[i-1]).encode()),
        triage_category=r['triage_category'], controlling_case_id=r['controlling_case_id'], participating_case_ids=memberships[r['unresolved_node_id']],
        original_direct_parent='UNRESOLVED', triage_resolves_parent=False) for i,r in enumerate(rows,1)]
    m = dict(triage=rows, aliases=aliases, cases=cc, dependencies=deepcopy(rows), crosswalk=crosswalk,
        groups=group_audit(s,rows), evidence=evidence_links(s,cc),
        source_nodes=deepcopy(s['nodes']), source_edges=deepcopy(s['edges']), accounting=deepcopy(s['accounting']),
        historical=deepcopy(s['files']), new_structural_relations=[], candidate_method='NO_CANDIDATE_SELECTION',
        summary_panel=dict(case_id='SEAM_H', panel_kind='WHOLE_BOOK_SUMMARY_NOT_ADDITIONAL_INDEPENDENT_CASE',
                           involved_nodes=s['cfg']['summary_seeds'], depends_on=[c['case_id'] for c in cc], proposed_tree=False))
    m['negative'] = controls(m,s)
    m['report'] = report(m,s)
    # Review-model mutation must never alias accepted source/config records.
    return deepcopy(m)


def controls(m,s):
    same_edges = m['source_edges']==s['edges'] and not m['new_structural_relations']
    def frozen_fragment(fragment):
        selected=[x for x in s['frozen'] if fragment in x['path']]
        return bool(selected) and all(x['actual']==x['expected'] for x in selected)
    result = {'NO_HSA1_MUTATION':frozen_fragment('docs/HUMAN_STRUCTURAL_ADJUDICATION.csv'),
        'NO_HSA2_MUTATION':frozen_fragment('docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv'),
        'NO_HSA2_F_MUTATION':frozen_fragment('docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv'),
        'NO_R43_MUTATION':frozen_fragment('src/milal_r4_3_hierarchy_scaffold.py') and m['historical']==s['files'],
        'NO_NEW_MR1_RULE':frozen_fragment('src/milal_mr1_historical_rules.py'),
        'NO_NEW_CHILD_OF':same_edges, 'NO_NEW_HIERARCHICALLY_ABOVE':same_edges,
        'NO_NEW_PARENTAGE':same_edges, 'NO_NEW_DIRECT_CLOSURE':same_edges,
        'NO_NEAREST_OPENING':m['candidate_method']=='NO_CANDIDATE_SELECTION',
        'NO_ADJACENCY_OR_RESPONSE_PARENT':same_edges and m['candidate_method']=='NO_CANDIDATE_SELECTION',
        'NO_SYNTHETIC_ZOPHAR_III':not any('ZOPHAR' in n['node_id'].upper() for n in m['source_nodes']),
        'NO_CYCLE_MEMBER_REMOVED':m['source_nodes']==s['nodes'] and same_edges,
        'NO_ROLE_RECORD_DELETED':m['accounting']==s['accounting'],
        'NO_ROLE_DOUBLE_INDEPENDENT_REVIEW':m['aliases']==role_audit(s) and all(
            len({r['controlling_case_id'] for r in m['triage'] if r['unresolved_node_id'] in a['node_ids']})==1
            and a['audit_status']=='SAME_TEXTUAL_LOCUS_DIFFERENT_STRUCTURAL_ROLE' for a in m['aliases']),
        'NO_ELIHU_INTRO_PEER_REGRESSION':same_edges and not any(e['relation_type']=='SAME_LEVEL_SIBLING' and 'H:HSA019' in (e['source_node'],e['target_node']) for e in m['source_edges']),
        'NO_42_10_12_PROMOTION':not any(n['reference_start'] in ('42:10','42:12') and n['textual_boundary'] for n in m['source_nodes']),
        'NO_CANDIDATE_RANKING':all(c['candidate_parents']==[] and not any(t in key.lower() for t in ('score','rank','preferred_parent') for key in c) for c in m['cases']),
        'NO_HUMAN_DECISION_REOPENED':all(c['review_status']=='UNREVIEWED' and not c['candidate_parents'] and not c['automatic_resolution'] for c in m['cases']),
        'NO_HISTORICAL_MUTATION':m['historical']==s['files'],
        'NO_SILENT_UNRESOLVED_DELETION':Counter(r['unresolved_node_id'] for r in m['crosswalk'])==Counter(u['node_id'] for u in s['unresolved'])}
    return [dict(control=k,status='PASS' if v else 'FAIL') for k,v in result.items()]


def report(m,s):
    nn = {n['node_id']:n for n in s['nodes']}; ee = {e['edge_id']:e for e in s['edges']}
    accounting = {a['judgment_id']:a for a in s['accounting']}
    def cell(x): return str(x).replace('|','\\|').replace('\n',' ')
    lines = ['# HSA3-PREP — Global structural seam review packet','', 'Mode: '+s['mode'], '',
        'Review preparation only. No new parent, closure, boundary, human judgment or MR1 rule.',
        'All 57 unresolved direct-parent rows and all 59 historical human records remain intact.',
        'Membership, continuation, same-level roles, closure and technical root links remain different claims.', '',
        '## What compression establishes','',
        f'{len(m["triage"])} rows are scheduled into {len(m["cases"])} distinct open-attachment review cases plus SEAM_H summary.',
        'These are review scopes, NOT a proved number of independent atomic human decisions.',
        'Cases overlap. A primary controlling case is a presentation assignment, not a proposed parent or a promise that one judgment resolves its rows.',
        'Dependencies are exact existing typed relation paths. UNRESOLVED / INSUFFICIENT_EVIDENCE remain valid outcomes.', '',
        '| Review-only category | Rows |','| --- | ---: |']
    counts = Counter(r['triage_category'] for r in m['triage'])
    lines += [f'| {k} | {counts[k]} |' for k in CATEGORIES]
    lines += ['', '## Complete same-locus audit','', 'All 61 nodes were scanned; non-textual groups are not textual events. Reference equality alone never establishes identity.', '']
    for a in m['aliases']:
        lines += [f'### {a["locus"]}: {a["audit_status"]}', '',
                  'Roles: '+cell(canonical(a['roles'])), 'Judgment provenance: '+cell(canonical(a['judgments'])),
                  'Exact shared evidence: '+cell(', '.join(a['shared_source_evidence_ids'])),
                  'Keep both original records; do not request two independent textual parents merely from two role node IDs.', '']
    lines += ['## Local constraints and non-textual group dependencies','',
        'Exact direct parent is still a distinct representation question. Separate local adjudication is deferred until the enclosing review case establishes whether it would add information.', '',
        '| Node / locus | Existing outgoing constraint | Review case |', '| --- | --- | --- |']
    for row in m['triage']:
        if row['already_known_local_relation']:
            relations = [ee[i]['relation_type']+' → '+ee[i]['target_node'] for i in row['already_known_local_relation']]
            lines.append('| '+ ' | '.join([row['unresolved_node_id']+' / '+row['reference'], '; '.join(relations),row['controlling_case_id']])+' |')
    lines += ['', '**3:2 is already resolved, not a 58th unresolved row:** H:HSA014 has explicit parent H:HSA013 as well as CONTINUES_WITHIN. Its context is retained in A/B.', '']
    for g in m['groups']:
        lines += [f'### {g["group_id"]}', '',
            f'Origin: {g["group_origin"]}; textual_boundary=false. Parent representation remains open.',
            'Human sources: '+', '.join(g['source_judgment_ids']),
            'Explicit members: '+(', '.join(g['members']) or 'NONE; human scope target, not invented membership'),
            'Known relation IDs: '+', '.join(g['known_relation_ids']),
            'Potentially coordinated unresolved rows: '+(', '.join(g['dependent_unresolved_rows']) or 'NONE'),
            'Primary review: '+g['controlling_case_id']+'. This may avoid repeated item-level review, but does not automatically settle member parentage.', '']
    lines += ['## Open attachment cases','']
    for c in m['cases']:
        lines += [f'## {c["case_id"]} — {c["title"]}', '', c['question'], '',
            f'Primary unresolved rows: {c["primary_row_count"]}; participating rows (overlap allowed): {c["participating_row_count"]}.',
            'Primary IDs: '+(', '.join(c['primary_unresolved_rows']) or 'NONE: cross-case interface question; not a missing row'), '',
            '| Node | Exact judgment locus | Accepted function |', '| --- | --- | --- |']
        for ident in c['involved_nodes']:
            lines.append('| '+' | '.join([ident,reference(nn[ident]) or 'NON-TEXTUAL GROUP',nn[ident]['structural_function']])+' |')
        lines += ['', '### Existing human judgments — preserve, do not re-adjudicate','',
            '| Judgment | Function / relation | Linguistic basis and methodological note |', '| --- | --- | --- |']
        for ident in c['source_judgment_ids']:
            a = accounting[ident]['historical_record']
            lines.append('| '+' | '.join(map(cell,[ident, a.get('structural_function','')+' / '+a.get('hierarchy_relation',a.get('selected_relation','')),a.get('linguistic_basis','')+' '+a.get('methodological_note','')]))+' |')
        lines += ['', '### Accepted positive and negative constraints','',
            '| Edge ID | Source → target | Type / dimension | Human sources |', '| --- | --- | --- | --- |']
        for ident in c['relation_ids']:
            e=ee[ident]
            lines.append('| '+' | '.join(map(cell,[ident,e['source_node']+' → '+e['target_node'],e['relation_type']+' / '+e['dimension'],', '.join(e['source_judgment_ids'])]))+' |')
        links = [x for x in m['evidence'] if x['case_id']==c['case_id']]
        atoms, clauses, markers = set(),set(),set()
        for x in links:
            if x['evidence_kind']!='ACCEPTED_SOURCE_CONTEXT': continue
            raw=x['source_row']; atoms.update(json.loads(raw['atom_ids']))
            if x['evidence_id'].startswith('BHSA2021:clause:'): clauses.add(x['evidence_id'])
            if x['evidence_id'].startswith('MR1:'): markers.add(x['evidence_id'])
        frames = [x['evidence_id'] for x in links if x['evidence_kind']=='ACCEPTED_FRAME_CONTEXT']
        lines += ['', '### Exact source context','',
            'BHSA clause IDs: '+(', '.join(sorted(clauses)) or 'Not supplied for this panel'),
            'BHSA clause_atom IDs: '+(', '.join(map(str,sorted(atoms,key=str))) or 'Not supplied for this panel'),
            'Historical marker IDs: '+(', '.join(sorted(markers)) or 'None supplied; no marker inferred'),
            'Accepted frame context IDs: '+(', '.join(sorted(set(frames))) or 'NONE linked by the accepted unresolved registry'),
            'Frame context is not a parent candidate. The complete raw source rows, upstream locators, exact member/row hashes and every evidence occurrence are in [05_seam_evidence_links.csv](05_seam_evidence_links.csv).',
            c['redundant_decisions'], '', '### Researcher response (blank)','',
            'Allowed: source-supported human relation, UNRESOLVED, or INSUFFICIENT_EVIDENCE. No candidate is scored, ranked or preferred.', '',
            '| Field | Value |','| --- | --- |']
        lines += [f'| {key} | {c[key]} |' for key in REVIEW_FIELDS]
        lines += ['']
    lines += ['## SEAM_H — Whole-book attachment summary','',
        'Summary only; not an eighth independent case and not a proposed final tree. JOB_BOOK remains TECHNICAL_ROOT only.',
        'The opening/testing material, Job 3 initial speech, dialogue-cycle sequence, post-dialogue Job, Elihu introduction/sequence, YHWH–Job complex and final narrative remain separate known contexts.',
        'Summary node IDs: '+', '.join(m['summary_panel']['involved_nodes']),
        'Depends on: '+', '.join(m['summary_panel']['depends_on']), '',
        '## Lossless 57-row crosswalk','', '| Node | Primary review | All participating reviews | Category |', '| --- | --- | --- | --- |']
    for x in m['crosswalk']:
        lines.append('| '+' | '.join([x['unresolved_node_id'],x['controlling_case_id'],', '.join(x['participating_case_ids']),x['triage_category']])+' |')
    lines += ['', 'R4.4 hierarchy recompilation waits for completed researcher adjudication. No review field has been answered by this stage.', '']
    return '\n'.join(lines)


def gates(m,s):
    checks = {}
    def frozen_paths(paths):
        receipts={x['path']:x for x in s['frozen']}
        return bool(paths) and all(p in receipts and receipts[p]['actual']==receipts[p]['expected']==s['cfg']['frozen_files'][p] for p in paths)
    for layer,paths in [('HSA1',[r43.h1.CSV,r43.h1.MD]),('HSA2',[r43.h2.CSV,r43.h2.MD]),('HSA2_F',[r43.final.CSV,r43.final.MD])]:
        checks[layer+'_FROZEN']=frozen_paths([p.relative_to(ROOT).as_posix() for p in paths])
    checks['R43_FROZEN']=frozen_paths([p for p in s['cfg']['frozen_files'] if 'r4_3' in p.lower()]) and m['historical']==s['files']
    checks['ALL_FROZEN_CORES']=frozen_paths(list(s['cfg']['frozen_files']))
    checks['NO_NEW_MR1_RULE']=frozen_paths([p for p in s['cfg']['frozen_files'] if 'mr1' in p.lower()])
    checks['SOURCE_NODES_UNCHANGED']=m['source_nodes']==s['nodes']
    checks['SOURCE_RELATIONS_UNCHANGED']=m['source_edges']==s['edges']
    checks['NO_NEW_CHILD_OF']=not any(e.get('relation_type')=='CHILD_OF' for e in m['new_structural_relations'])
    checks['NO_NEW_HIERARCHICALLY_ABOVE']=not any(e.get('relation_type')=='HIERARCHICALLY_ABOVE' for e in m['new_structural_relations'])
    checks['NO_NEW_DIRECT_CLOSURE']=not any(e.get('relation_type')=='DIRECT_LOCAL_CLOSURE' for e in m['new_structural_relations'])
    checks['NO_STRUCTURAL_ASSERTIONS']=m['new_structural_relations']==[]
    checks['NO_HEURISTIC_SELECTION']=m['candidate_method']=='NO_CANDIDATE_SELECTION' and all(c['candidate_parents']==[] for c in m['cases'])
    checks['HUMAN_ACCOUNTING_INTACT']=m['accounting']==s['accounting']
    checks['ALL_UNRESOLVED_CROSSWALKED']=Counter(x['unresolved_node_id'] for x in m['crosswalk'])==Counter(u['node_id'] for u in s['unresolved'])
    expected_aliases=role_audit(s)
    expected_rows=triage(s,expected_aliases)
    expected_cases=cases(s,expected_rows)
    checks['COMPLETE_LOCUS_SCAN']=m['aliases']==expected_aliases
    checks['EXACT_ROLE_IDENTITY_ONLY']=all(a['identity_basis']=='EXPLICIT_RESEARCHER_PAIR_AND_SHARED_EXACT_EVIDENCE' and not a['historical_records_merged'] and a['shared_source_evidence_ids'] for a in m['aliases'])
    checks['TRIAGE_PARTITION']=m['triage']==expected_rows
    checks['TYPED_DEPENDENCY_INTEGRITY']=m['dependencies']==expected_rows
    checks['CASE_INVENTORY_FROM_DATA']=m['cases']==expected_cases
    expected_groups=group_audit(s,expected_rows)
    checks['GROUP_AUDIT_NO_PARENT_DECISION']=m['groups']==expected_groups
    checks['PRIMARY_COUNTS_PARTITION']=sum(c['primary_row_count'] for c in m['cases'])==len(s['unresolved']) and Counter(i for c in m['cases'] for i in c['primary_unresolved_rows'])==Counter(u['node_id'] for u in s['unresolved'])
    checks['CROSSWALK_DEPENDENCY_MATCH']=all(
        x['controlling_case_id']==next((r['controlling_case_id'] for r in expected_rows if r['unresolved_node_id']==x['unresolved_node_id']),None)
        and x['participating_case_ids']==[c['case_id'] for c in expected_cases if x['unresolved_node_id'] in c['participating_unresolved_rows']]
        and x['original_direct_parent']=='UNRESOLVED' and x['triage_resolves_parent'] is False
        and 1<=x['source_data_row']<=len(s['unresolved'])
        and x['unresolved_node_id']==s['unresolved'][x['source_data_row']-1]['node_id']
        and x['source_row_sha256']==sha(canonical(r43.h1.read_csv(s['files'][SOURCE_TABLES['unresolved']])[x['source_data_row']-1]).encode()) for x in m['crosswalk'])
    checks['SOURCE_EVIDENCE_LOSSLESS']=m['evidence']==evidence_links(s,expected_cases)
    checks['REVIEW_FIELDS_BLANK']=all(c.get(k)==('UNREVIEWED' if k=='review_status' else '') for c in m['cases'] for k in REVIEW_FIELDS)
    checks['NO_CANDIDATE_SCORING']=all(not any(term in key.lower() for term in ('score','rank','preferred_parent')) for collection in ('triage','cases','dependencies','groups') for row in m[collection] for key in row)
    checks['SUMMARY_NOT_TREE']=m['summary_panel']==dict(case_id='SEAM_H',panel_kind='WHOLE_BOOK_SUMMARY_NOT_ADDITIONAL_INDEPENDENT_CASE',involved_nodes=s['cfg']['summary_seeds'],depends_on=[c['case_id'] for c in expected_cases],proposed_tree=False)
    def subset(rows,kinds): return [e for e in rows if e['relation_type'] in kinds]
    checks['MEMBERS_AND_CYCLES_PRESERVED']=subset(m['source_edges'],{'GROUP_MEMBER_OF'})==subset(s['edges'],{'GROUP_MEMBER_OF'}) and not any('ZOPHAR' in n['node_id'].upper() for n in m['source_nodes'])
    checks['ELIHU_INTRO_NOT_PEER']=subset(m['source_edges'],{'NARRATIVE_INTRODUCTION'})==subset(s['edges'],{'NARRATIVE_INTRODUCTION'}) and not any(e['relation_type']=='SAME_LEVEL_SIBLING' and 'H:HSA019' in (e['source_node'],e['target_node']) for e in m['source_edges'])
    checks['NO_42_10_12_PROMOTION']=not any(n['reference_start'] in ('42:10','42:12') and n['textual_boundary'] for n in m['source_nodes'])
    checks['LOCAL_RELATIONS_NOT_PARENT']=subset(m['source_edges'],{'CONTINUES_WITHIN','DIRECT_LOCAL_CLOSURE','TERMINATES_ENCLOSING_GROUP','NO_DIRECT_RELATION'})==subset(s['edges'],{'CONTINUES_WITHIN','DIRECT_LOCAL_CLOSURE','TERMINATES_ENCLOSING_GROUP','NO_DIRECT_RELATION'}) and all(r['direct_parent']=='UNRESOLVED' for r in m['triage'])
    checks['NO_RESPONSE_ADJACENCY_PARENT']=subset(m['source_edges'],{'CHILD_OF','HIERARCHICALLY_ABOVE'})==subset(s['edges'],{'CHILD_OF','HIERARCHICALLY_ABOVE'}) and not m['new_structural_relations']
    checks['NEGATIVE_CONTROLS']=m['negative']==controls(m,s) and all(x['status']=='PASS' for x in m['negative'])
    checks['REPORT_FAITHFUL']=m['report']==report(m,s)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def serialize(m,s):
    gg=gates(m,s)
    require(all(x['status']=='PASS' for x in gg),canonical([x for x in gg if x['status']!='PASS']))
    files={'history/r4_3/'+k:v for k,v in m['historical'].items()}
    for name,key in [('01_unresolved_row_triage.csv','triage'),('02_same_textual_locus_role_audit.csv','aliases'),
        ('03_global_seam_cases.csv','cases'),('05_seam_evidence_links.csv','evidence'),
        ('06_parentage_dependency_map.csv','dependencies'),('07_negative_controls.csv','negative'),
        ('09_r4_3_unresolved_crosswalk.csv','crosswalk'),('10_non_textual_group_audit.csv','groups')]:
        files[name]=r43.h1.util.csv_bytes(m[key])
    files[REPORT]=m['report'].encode('utf-8')
    meta=dict(version='HSA3-PREP',mode=s['mode'],status='PASS',gate_count=len(gg)+1,
        baseline_commit=s['cfg']['baseline_commit'], code_sha256=sha(Path(__file__).read_bytes()),config_sha256=sha(CONFIG.read_bytes()),
        frozen_receipts=s['frozen'],source_receipts=s['receipts'],
        counts=dict(unresolved=len(m['triage']),triage={k:sum(x['triage_category']==k for x in m['triage']) for k in CATEGORIES},
            role_loci=len(m['aliases']),review_cases=len(m['cases']),summary_panels=1,
            primary_rows={c['case_id']:c['primary_row_count'] for c in m['cases']},
            participating_rows={c['case_id']:c['participating_row_count'] for c in m['cases']}, evidence_links=len(m['evidence'])),
        claim='REVIEW_SCOPE_COMPRESSION_NOT_PROOF_OF_ATOMIC_DECISION_COUNT',
        independent_atomic_human_decisions='NOT_DETERMINABLE_BEFORE_ADJUDICATION',summary_panel=m['summary_panel'])
    files['90_run_metadata.json']=r43.h1.util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv',None)
        files['99_manifest_sha256.csv']=r43.h1.util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(files.items())])
    seal();gg.append(r43.h1.util.manifest_gate(files));files['08_gates.csv']=r43.h1.util.csv_bytes(gg);seal()
    require(r43.h1.util.manifest_ok(files),'output manifest')
    return files


def publish(files,out):
    out=Path(out).resolve(); zp=out.with_name(out.name+'_results.zip');log=out.with_name(out.name+'_run.log')
    require(not any(p.exists() for p in (out,zp,log)),'output already exists')
    require(r43.h1.util.manifest_ok(files),'publication manifest')
    for name,data in files.items():
        target=out/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    with zipfile.ZipFile(zp,'w') as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    with zipfile.ZipFile(zp) as z:
        require(z.testzip() is None and {n:z.read(n) for n in z.namelist()}==files,'ZIP integrity')
    require({p.relative_to(out).as_posix():p.read_bytes() for p in out.rglob('*') if p.is_file()}==files,'disk integrity')
    meta=json.loads(files['90_run_metadata.json'])
    log.write_text(f'HSA3-PREP PASS\nMode {meta["mode"]}\nGates {meta["gate_count"]} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n',encoding='utf-8')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--self-test',action='store_true');a=p.parse_args(argv)
    s=load(a.self_test);m=build(s);files=serialize(m,s)
    require(files==serialize(build(s),s),'deterministic serialization')
    require(r43.frozen_receipts(s['cfg'])==s['frozen'],'frozen source changed during run')
    for receipt in s['receipts']:
        require(sha((ROOT/receipt['path']).read_bytes())==receipt['expected'],'input changed during run')
    publish(files,a.out);print('HSA3-PREP PASS '+str(Path(a.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
