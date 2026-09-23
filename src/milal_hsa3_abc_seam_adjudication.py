"""HSA3-A/C: explicit researcher composition decisions over frozen evidence."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_hsa3_de_seam_adjudication as d

ROOT, sha, rows, util = d.ROOT, d.sha, d.rows, d.util
REVIEW_FIELDS = d.REVIEW_FIELDS
CONFIG = ROOT / 'config/hsa3_abc_job.json'
HISTORY = 'history/hsa3_de/'
EDGES, NODES, SEAMS, UNRESOLVED, ACCOUNTING, REGISTRY, ANA = (
    d.HISTORY + x for x in (d.EDGES, d.NODES, d.SEAMS, d.UNRESOLVED, d.ACCOUNTING, d.REGISTRY, d.ANA))
DE = '01_hsa3_de_seam_adjudications.csv'
OPENING, DISPUTE = 'OPENING_NARRATIVE_COMPLEX', 'JOB_FRIENDS_DISPUTE_COMPLEX'
ABC = ('SEAM_A', 'SEAM_B', 'SEAM_C')


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-A/C STOP: ' + message)


def audit(files, cfg, digest, synthetic=False):
    require(util.manifest_ok(files) and all(r['valid'] for r in d.h.nested_manifests(files)), 'input manifests')
    require(synthetic or (digest == cfg['archive']['sha256'] and len(files) == cfg['archive']['members']), 'D/E ZIP SHA/count')
    meta = json.loads(files['90_run_metadata.json'])
    require(meta['version'] == 'HSA3-D/E' and meta['status'] == 'PASS' and meta['r44_started'] is False, 'D/E stage/status')
    gg = rows(files['10_gates.csv'])
    require(len(gg) == meta['gate_count'] and all(g['status'] == 'PASS' for g in gg), 'D/E gates')
    decisions = rows(files[DE])
    require([r['seam_id'] for r in decisions] == ['SEAM_D', 'SEAM_E'] and all(r['status'] == 'FROZEN' for r in decisions), 'D/E frozen state')
    cases = rows(files[SEAMS])
    require([r['case_id'] for r in cases] == ['SEAM_' + x for x in 'ABCDEFG'], 'original seam identities')
    require(all(c[k] == ('UNREVIEWED' if k == 'review_status' else '') for c in cases for k in REVIEW_FIELDS), 'original review fields')
    require(all(r['direct_parent'] == 'UNRESOLVED' for r in rows(files[UNRESOLVED])), 'unresolved parent schema')
    return dict(sha256=digest, members=len(files), synthetic=synthetic, manifests=d.h.nested_manifests(files))


def load(self_test=False, archive=None):
    cfg = json.loads(CONFIG.read_bytes())
    commit = d.baseline_receipt(cfg)
    frozen = d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['expected'] == r['actual'] for r in frozen), 'frozen repository files')
    human_bytes = (ROOT / cfg['human_source']['path']).read_bytes()
    require(sha(human_bytes) == cfg['human_source']['sha256'], 'human decisions SHA')
    human = json.loads(human_bytes)
    request = (ROOT / human['source_path']).read_bytes()
    require(sha(request) == human['source_sha256'], 'researcher source SHA')
    if self_test:
        prior = d.load(self_test=True)
        files = d.serialize(d.build(prior), prior)
        digest = sha(files['99_manifest_sha256.csv'])
    else:
        data = (Path(archive) if archive else ROOT / cfg['archive']['path']).read_bytes()
        digest = sha(data)
        require(digest == cfg['archive']['sha256'], 'D/E archive SHA')
        files = d.h.f.a.prep.r43.h1.src.archive(data, digest, mr1=True)['files']
    receipt = audit(files, cfg, digest, self_test)
    return dict(cfg=cfg, commit=commit, frozen=frozen, human=human, human_bytes=human_bytes, request=request,
                files=files, receipt=receipt, mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_ARTIFACT_ADJUDICATION')


def locate(s, member, key, identity):
    found = [(i, r) for i, r in enumerate(d.h.raw_rows(s['files'][member]), 1) if r[key] == identity]
    require(len(found) == 1, 'missing/duplicate exact identity: ' + identity)
    i, r = found[0]
    return dict(source_member=HISTORY + member, source_data_row=i, source_identity_field=key, source_identity=identity,
                source_row_sha256=d.h.f.rowhash(r), source_member_sha256=sha(s['files'][member]), source_artifact_sha256=s['receipt']['sha256'])


def key(r):
    # A renamed dimension cannot manufacture a second copy of the same claim.
    return r['source_node'], r['target_node'], r['relation_type']


def group_records(s):
    nodes = {r['node_id']: r for r in rows(s['files'][NODES])}
    edges = rows(s['files'][EDGES])
    result = []
    for group in s['human']['groups']:
        g = deepcopy(group)
        # Exact membership identity audit, never location/text similarity.
        candidates = []
        for ident, node in nodes.items():
            mm = sorted((e for e in edges if e['target_node'] == ident and e['relation_type'] == 'GROUP_MEMBER_OF'), key=lambda e: int(e['membership_position']))
            if mm and [e['source_node'] for e in mm] == g['members']:
                require(node['structural_function'] == 'NON_TEXTUAL_GROUP', 'equivalent membership has incompatible group semantics')
                candidates.append(ident)
        require(len(candidates) <= 1, 'ambiguous equivalent composition group')
        if candidates:
            require(candidates[0] == g['group_id'], 'equivalent group requires explicit canonical-ID mapping')
        require(g['group_id'] not in nodes or candidates == [g['group_id']], 'group ID collision')
        require(all(x in nodes for x in g['members']), 'missing exact member identity')
        g.update(action='CONFIRMED_EXISTING' if candidates else 'CREATED', textual_parent=False,
                 authority='RESEARCHER_SUPPLIED_COMPOSITION', scope_authority='SUPPLIED_HUMAN_SPAN_NOT_COMPUTED_CLOSURE',
                 equivalent_existing_ids=candidates, source_request_sha256=s['human']['source_sha256'])
        result.append(g)
    return result


def crosswalk(s):
    cases = rows(s['files'][SEAMS])
    result = []
    for r in rows(s['files'][UNRESOLVED]):
        primary = [c['case_id'] for c in cases if r['node_id'] in c['primary_unresolved_rows']]
        participating = [c['case_id'] for c in cases if c['case_id'] in ABC and r['node_id'] in c['participating_unresolved_rows']]
        require(len(primary) == 1, 'unresolved ownership ambiguity')
        result.append(dict(node_id=r['node_id'], reference=r['reference'], primary_seam=primary[0], participating_abc_seams=participating,
            status='REMAINS_UNRESOLVED' if participating else 'NOT_APPLICABLE_TO_APPROVED_DECISION',
            direct_parent='UNRESOLVED', direct_parent_resolved=False, historical_record=r,
            reason='Composition and negative constraints assign no exact direct textual parent.', **locate(s, UNRESOLVED, 'node_id', r['node_id'])))
    return result


def actions(s, groups):
    edges = rows(s['files'][EDGES])
    cases = [c for c in rows(s['files'][SEAMS]) if c['case_id'] in ABC]
    result = []
    # Confirm each exact historical edge only once, even if multiple panels cite it.
    ids = set(e for c in cases for e in c['relation_ids'])
    for e in edges:
        if e['edge_id'] not in ids:
            continue
        result.append(dict(action_id='ABC:CONFIRM:' + e['edge_id'], action='CONFIRMED_EXISTING', object_kind='RELATION',
            canonical_relation_id=e['edge_id'], seam_ids=[c['case_id'] for c in cases if e['edge_id'] in c['relation_ids']],
            source_node=e['source_node'], target_node=e['target_node'], relation_type=e['relation_type'], dimension=e['dimension'],
            membership_position=e['membership_position'], textual_parentage_created=False, authority='PRESERVED_HUMAN_JUDGMENT',
            original_record=e, **locate(s, EDGES, 'edge_id', e['edge_id'])))
    requests = []
    for g in groups:
        for i, ident in enumerate(g['members'], 1):
            requests.append(dict(seam_id=g['seam_id'], source_node=ident, target_node=g['group_id'], relation_type='GROUP_MEMBER_OF',
                                 dimension='COMPOSITION_GROUPING', membership_position=i))
    requests += deepcopy(s['human']['negative_constraints'])
    seen = set()
    for r in requests:
        k = key(r)
        equivalent = [e for e in edges if (e['source_node'], e['target_node'], e['relation_type']) == k[:3]]
        require(len(equivalent) <= 1, 'ambiguous canonical relation')
        action = 'NO_ACTION_DUPLICATE' if k in seen else 'CONFIRMED_EXISTING' if equivalent else 'CREATED' if r['relation_type'] == 'GROUP_MEMBER_OF' else 'NEGATIVE_CONSTRAINT_CREATED'
        seen.add(k)
        ident = equivalent[0]['edge_id'] if equivalent else 'ABC:R:' + d.h.f.rowhash(k)[:20]
        result.append(dict(action_id='ABC:REQUEST:' + str(len(result) + 1), action=action, object_kind='RELATION',
            canonical_relation_id=ident, seam_ids=[r.pop('seam_id')], **r,
            textual_parentage_created=False, authority='EXPLICIT_RESEARCHER_DECISION',
            source_request_sha256=s['human']['source_sha256'], human_input_sha256=sha(s['human_bytes'])))
    for r in crosswalk(s):
        if r['status'] == 'REMAINS_UNRESOLVED':
            result.append(dict(action_id='ABC:UNRESOLVED:' + r['node_id'], action='UNRESOLVED_RETAINED', object_kind='PARENT_QUESTION',
                canonical_relation_id='', seam_ids=r['participating_abc_seams'], source_node=r['node_id'], target_node='',
                relation_type='UNRESOLVED', dimension='PARENTAGE_CONTAINMENT', textual_parentage_created=False,
                authority='NO_POSITIVE_PARENT_SUPPLIED'))
    return result


def criteria(s):
    registry = {r['evidence_code']: r for r in rows(s['files'][REGISTRY])}
    cases = {c['case_id']: c for c in rows(s['files'][SEAMS])}
    result = []
    for seam, codes in s['human']['criteria'].items():
        for code in codes:
            require(code in registry, 'unknown criteria code')
            result.append(dict(seam_id=seam, evidence_code=code, role='INSUFFICIENT_ALONE' if code.startswith('N-') else 'HUMAN_EVIDENCE_CROSSWALK',
                sole_basis_sufficient=False, original_registry_record=registry[code],
                source_judgment_ids=cases[seam]['source_judgment_ids'], source_relation_ids=cases[seam]['relation_ids'],
                methodological_note='Crosswalk of supplied rationale; no automatic inference or registry promotion. Composition ordering has no new evidence code.',
                **locate(s, REGISTRY, 'evidence_code', code)))
    return result


def integrity(s, historical):
    return [dict(member=HISTORY + name, expected_sha256=sha(data), actual_sha256=sha(historical.get(name, b'')),
                 status='PASS' if historical.get(name) == data else 'FAIL') for name, data in sorted(s['files'].items())]


def counts(m):
    cc = Counter(a['action'] for a in m['actions'])
    return dict(seam_decisions=len(m['adjudications']), new_groups=sum(g['action'] == 'CREATED' for g in m['groups']),
        new_positive_relations=cc['CREATED'], confirmed_existing_relations=cc['CONFIRMED_EXISTING'], new_negative_constraints=cc['NEGATIVE_CONSTRAINT_CREATED'],
        unresolved_retained=cc['UNRESOLVED_RETAINED'], duplicate_skipped=cc['NO_ACTION_DUPLICATE'],
        crosswalk=dict(Counter(r['status'] for r in m['crosswalk'])), resolved_by_A=sum(r['status'] == 'RESOLVED_BY_SEAM_A' for r in m['crosswalk']),
        resolved_by_B=sum(r['status'] == 'RESOLVED_BY_SEAM_B' for r in m['crosswalk']), resolved_by_C=sum(r['status'] == 'RESOLVED_BY_SEAM_C' for r in m['crosswalk']))


def packet(m, s):
    edges = {r['edge_id']: r for r in rows(s['files'][EDGES])}
    lines = ['# Remaining global seams: F/G', '', 'A/B/C are FROZEN by supplied decisions; D/E remain FROZEN. Frozen decisions do not resolve all parent questions.',
             '', 'F/G are UNREVIEWED. No R4.4. The 2:11–42:9 participant-frame hypothesis remains unadjudicated.', '']
    lines += ['## Preserved ANA context (not new F/G judgments)', '',
              '[Exact accepted/deferred records and evidence IDs](' + HISTORY + ANA + ').', '']
    for r in rows(s['files'][ANA]):
        lines.append(f"- {r['review_question_id']}: {r['status']}; {r['relation_type']} ({r['relation_dimension']}); target {r['target_ref'] or r['scope_ref']}. Limitations: {', '.join(r['limitations'])}.")
    lines += ['', 'These overlays and Q3 candidacy do not supply direct textual parentage.', '']
    for c in m['remaining']:
        lines += ['## ' + c['case_id'] + ' — ' + c['title'], '', c['question'], '',
                  'Participating nodes: ' + ', '.join(c['involved_nodes']), '',
                  'Source judgments: ' + ', '.join(c['source_judgment_ids']), '',
                  'Criteria dimensions: PARENTAGE_CONTAINMENT; STRUCTURAL_FUNCTION; SAME_LEVEL_RELATION; CLOSURE_TARGET where applicable.', '',
                  'Raw evidence and all source IDs: [' + c['case_id'] + '](' + HISTORY + SEAMS + '); [nodes](' + HISTORY + NODES + '); [edges](' + HISTORY + EDGES + ').', '',
                  'Canonical criteria registry: [dimensions and admissibility](' + HISTORY + REGISTRY + ').', '',
                  '| Accepted constraint | Source | Relation | Target |', '| --- | --- | --- | --- |']
        for label, field in [('POSITIVE', 'positive_constraint_ids'), ('NEGATIVE', 'negative_constraint_ids')]:
            for ident in c[field]:
                e = edges[ident]
                lines.append(f"| {label} {ident} | {e['source_node']} | {e['relation_type']} | {e['target_node']} |")
        lines += ['', 'Unresolved participating rows (unchanged parent questions):', '']
        for r in rows(s['files'][UNRESOLVED]):
            if r['node_id'] in c['participating_unresolved_rows']:
                lines.append(f"- {r['node_id']} ({r['reference']}): {r['direct_parent']}. {r['reason']}")
        lines += ['', 'Frozen D/E constraints involving shared nodes (context, not F/G adjudication):', '']
        for a in rows(s['files']['05_hsa3_de_negative_constraints.csv']):
            if a['source_node'] in c['involved_nodes'] or a['target_node'] in c['involved_nodes']:
                lines.append(f"- {a['canonical_relation_id']}: {a['source_node']} → {a['target_node']} {a['relation_type']} ({a['dimension']}).")
        lines += ['', '| Researcher field | Value |', '| --- | --- |']
        lines += [f'| {field} | {c[field]} |' for field in REVIEW_FIELDS]
        lines += ['']
    return '\n'.join(lines)


def report(m, s):
    return '\n'.join(['# HSA3-A/C human adjudication', '',
        *(r['seam_id'] + ': ' + r['decision'] for r in m['adjudications']), '',
        'A/B/C = FROZEN means the supplied decision is complete, not every parent question is resolved.',
        'Composition order is distinct from textual hierarchy. Neither new group is a CHILD_OF target, HIERARCHICALLY_ABOVE node or BHSA mother surrogate.',
        'Job 2:11 retains UNRESOLVED parentage; it is not attached to the dispute complex. The 2:11–42:9 hypothesis is unadjudicated.',
        'H:HSA013 is reused for INITIAL_JOB_SPEECH. Its historical PARAGRAPH_ONSET and SPEECH_UNIT_ONSET judgments are both preserved.',
        'No canonical sequential edge type exists; ordered GROUP_MEMBER_OF fields represent the supplied sequence.',
        'Group/member spans are researcher-supplied annotations, not newly detected boundaries or lexical results.',
        'Three cycles retain 6/6/4 members. No synthetic Zophar III or Cycle 4. POST_DIALOGUE_JOB is a separate component.',
        'D/E, ANA Q2/Q3/Q4/Q5 and HSA2-F remain unchanged. F/G are UNREVIEWED. No R4.4 or lexical scan.', '',
        'Computed counts:', '```json', json.dumps(counts(m), ensure_ascii=False, indent=2), '```', '',
        'Original artifacts are nested byte-for-byte under ' + HISTORY + '; source row links use exact IDs and SHA256.'])


def derive(s):
    groups = group_records(s)
    aa = actions(s, groups)
    decisions = [dict(**deepcopy(r), researcher_supplied=True, source_request_sha256=s['human']['source_sha256'],
                     exact_textual_parent_assigned=False, **locate(s, SEAMS, 'case_id', r['seam_id'])) for r in s['human']['decisions']]
    facts = [dict(node_id=n['node_id'], original_record=n, **locate(s, NODES, 'node_id', n['node_id'])) for n in rows(s['files'][NODES])]
    m = dict(groups=groups, actions=aa, adjudications=decisions, annotations=deepcopy(s['human']['annotations']),
        negative=[deepcopy(a) for a in aa if a['action'] == 'NEGATIVE_CONSTRAINT_CREATED'],
        criteria=criteria(s), crosswalk=crosswalk(s), historical=deepcopy(s['files']), facts=facts,
        remaining=[deepcopy(c) for c in rows(s['files'][SEAMS]) if c['case_id'] in ('SEAM_F', 'SEAM_G')],
        commit=deepcopy(s['commit']), receipt=deepcopy(s['receipt']), r44_started=False, lexical_scans=[], participant_frame_adjudications=[])
    m['integrity'] = integrity(s, m['historical'])
    m['report'], m['packet'] = report(m, s), packet(m, s)
    return m


def digest(m):
    return d.h.f.rowhash({k: ({n: sha(v) for n, v in value.items()} if k == 'historical' else value) for k, value in m.items() if k != 'rerun_digest'})


def build(s):
    m = derive(s)
    m['rerun_digest'] = digest(derive(s))
    return m


def gates(m, s):
    checks = {}
    unchanged = lambda name: m['historical'].get(name) == s['files'][name]
    original = {r['node_id']: r for r in rows(s['files'][NODES])}
    facts = {r['node_id']: r['original_record'] for r in m['facts']}
    gs = {g['group_id']: g for g in m['groups']}
    anns = {a['node_id']: a for a in m['annotations']}
    adjud = {r['seam_id']: r for r in m['adjudications']}
    new = [a for a in m['actions'] if a['action'] in ('CREATED', 'NEGATIVE_CONSTRAINT_CREATED')]
    has = lambda src, tgt, rel: any(a['source_node'] == src and a['target_node'] == tgt and a['relation_type'] == rel for a in m['actions'])
    no_parent = lambda ids: not any(a['action'] == 'CREATED' and a['relation_type'] in ('CHILD_OF', 'HIERARCHICALLY_ABOVE', 'CONTINUES_WITHIN') and (a['source_node'] in ids or a['target_node'] in ids) for a in m['actions'])
    checks['BASELINE_COMMIT_VERIFIED'] = m['commit'] == s['commit'] and m['commit']['verified_commit'] == s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    checks['PRIOR_DE_SEAMS_FROZEN'] = unchanged(DE) and all(r['status'] == 'FROZEN' for r in rows(s['files'][DE]))
    for seam in ABC:
        expected = next(r for r in s['human']['decisions'] if r['seam_id'] == seam)
        checks[seam + '_RESEARCHER_DECISION_RECORDED'] = seam in adjud and all(adjud[seam].get(k) == v for k, v in expected.items()) and adjud[seam]['researcher_supplied'] is True
    checks['FRIENDS_ARRIVAL_SEPARATE_FROM_TEST_2'] = anns.get('H:HSA012') == s['human']['annotations'][0] and has('H:HSA012', 'HUMAN_SCOPE_2_1_10', 'NOT_WITHIN_SECOND_TESTING_SCENE') and no_parent({'H:HSA012'})
    checks['FRIENDS_ARRIVAL_PARENT_UNRESOLVED'] = any(r['node_id'] == 'H:HSA012' and r['direct_parent'] == 'UNRESOLVED' and r['status'] == 'REMAINS_UNRESOLVED' and r['direct_parent_resolved'] is False for r in m['crosswalk']) and no_parent({'H:HSA012'})
    for ident, gate in [(OPENING, 'OPENING_NARRATIVE_GROUP_NON_TEXTUAL'), (DISPUTE, 'DISPUTE_COMPLEX_NON_TEXTUAL')]:
        checks[gate] = ident in gs and gs[ident]['node_type'] == 'NON_TEXTUAL_COMPOSITION_GROUP' and gs[ident]['textual_parent'] is False and no_parent({ident})
    checks['INITIAL_JOB_SPEECH_NOT_CYCLE1'] = anns.get('H:HSA013') == s['human']['annotations'][1] and has('H:HSA013', 'CYCLE_1', 'NOT_MEMBER_OF_CYCLE_1') and not has('H:HSA013', 'CYCLE_1', 'GROUP_MEMBER_OF') and no_parent({'H:HSA013', 'H:HSA2-C1-S1'})
    def members(group):
        return [a['source_node'] for a in sorted((a for a in m['actions'] if a['object_kind'] == 'RELATION' and a['target_node'] == group and a['relation_type'] == 'GROUP_MEMBER_OF'), key=lambda a: int(a['membership_position']))]
    cycles = [members('CYCLE_' + str(i)) for i in range(1, 4)]
    refs = [[facts.get(n, {}).get('reference_start') for n in cc] for cc in cycles]
    checks['CYCLE1_STARTS_4_1'] = bool(refs[0]) and refs[0][0] == '4:1'
    checks['THREE_CYCLE_PATTERN_PRESERVED'] = refs == s['human']['cycle_references'] and unchanged(EDGES)
    checks['NO_SYNTHETIC_ZOPHAR_III'] = cycles[2] == ['H:HSA2-C3-S' + str(i) for i in range(1, 5)] and set(facts) == set(original)
    checks['POST_DIALOGUE_JOB_DISTINCT_FROM_CYCLE3'] = all(has(a, b, 'NO_DIRECT_PARENTAGE') for a, b in [('POST_DIALOGUE_JOB', 'CYCLE_3'), ('CYCLE_3', 'POST_DIALOGUE_JOB'), ('DIALOGUE_CYCLE_SEQUENCE', 'POST_DIALOGUE_JOB'), ('POST_DIALOGUE_JOB', 'DIALOGUE_CYCLE_SEQUENCE')]) and no_parent({'POST_DIALOGUE_JOB', 'CYCLE_3', 'DIALOGUE_CYCLE_SEQUENCE'})
    checks['NO_CYCLE4_AT_27_1'] = facts.get('H:HSA015') == original['H:HSA015'] and not any(a['target_node'] == 'CYCLE_4' or (a['source_node'] == 'H:HSA015' and a['relation_type'] == 'CYCLE_ONSET_OF') for a in m['actions']) and 'CYCLE_4' not in gs and 'CYCLE_4' not in facts
    checks['DISPUTE_COMPLEX_PRESENT'] = DISPUTE in gs and (gs[DISPUTE]['span_start'], gs[DISPUTE]['span_end']) == ('3:1', '31:40')
    checks['DISPUTE_COMPLEX_ORDERED_MEMBERS_CORRECT'] = DISPUTE in gs and gs[DISPUTE]['members'] == ['H:HSA013', 'DIALOGUE_CYCLE_SEQUENCE', 'POST_DIALOGUE_JOB'] and members(DISPUTE) == gs[DISPUTE]['members']
    checks['JOB_2_11_NOT_ATTACHED_TO_DISPUTE_COMPLEX'] = DISPUTE in gs and 'H:HSA012' not in gs[DISPUTE]['members'] and not any(a['source_node'] == 'H:HSA012' and a['target_node'] == DISPUTE for a in m['actions'])
    checks['NO_2_11_42_9_FRAME_ADJUDICATION'] = m['participant_frame_adjudications'] == [] and m['groups'] == group_records(s)
    checks['HSA2_F_INTEGRITY'] = unchanged(EDGES) and unchanged(ACCOUNTING)
    checks['ANA_INTEGRITY'] = all(unchanged(n) for n in s['files'] if n.startswith(d.HISTORY))
    checks['DE_INTEGRITY'] = all(unchanged(n) for n in s['files'] if not n.startswith(d.HISTORY))
    checks['FG_UNCHANGED'] = m['remaining'] == [c for c in rows(s['files'][SEAMS]) if c['case_id'] in ('SEAM_F', 'SEAM_G')] and set(adjud) == set(ABC)
    oldkeys = {key(e) for e in rows(s['files'][EDGES])}
    checks['NO_DUPLICATE_RELATIONS'] = len({key(a) for a in new}) == len(new) and not any(key(a) in oldkeys for a in new)
    checks['NO_R4_4'] = m['r44_started'] is False
    checks['FROZEN_SOURCE_FILES'] = all(r['actual'] == r['expected'] == s['cfg']['frozen_files'][r['path']] for r in s['frozen']) and len(s['frozen']) == len(s['cfg']['frozen_files'])
    checks['RESEARCHER_SOURCE_EXACT'] = sha(s['human_bytes']) == s['cfg']['human_source']['sha256'] and json.loads(s['human_bytes']) == s['human'] and sha(s['request']) == s['human']['source_sha256']
    checks['SOURCE_FACTS_EXACT'] = m['facts'] == [dict(node_id=n['node_id'], original_record=n, **locate(s, NODES, 'node_id', n['node_id'])) for n in rows(s['files'][NODES])]
    checks['RELATION_ACTIONS_EXACT'] = m['actions'] == actions(s, group_records(s))
    checks['NEGATIVE_CONSTRAINTS_EXACT'] = m['negative'] == [a for a in actions(s, group_records(s)) if a['action'] == 'NEGATIVE_CONSTRAINT_CREATED']
    checks['CRITERIA_CANONICAL'] = m['criteria'] == criteria(s)
    checks['CROSSWALK_FAITHFUL'] = m['crosswalk'] == crosswalk(s) and unchanged(UNRESOLVED)
    checks['HISTORICAL_ARTIFACTS_UNCHANGED'] = m['historical'] == s['files'] and m['receipt'] == s['receipt']
    checks['INTEGRITY_RECEIPTS_COMPUTED'] = m['integrity'] == integrity(s, m['historical']) and all(r['status'] == 'PASS' for r in m['integrity'])
    checks['NO_NEW_LEXICAL_ANALYSIS'] = m['lexical_scans'] == []
    checks['REPORT_FAITHFUL'] = m['report'] == report(m, s)
    checks['REMAINING_PACKET_FAITHFUL'] = m['packet'] == packet(m, s)
    checks['DETERMINISTIC_RERUN'] = m['rerun_digest'] == digest(m)
    return [dict(gate=k, status='PASS' if v else 'FAIL') for k, v in checks.items()]


def serialize(m, s):
    gg = gates(m, s)
    require(all(g['status'] == 'PASS' for g in gg), str([g for g in gg if g['status'] == 'FAIL']))
    files = {HISTORY + k: v for k, v in m['historical'].items()}
    for name, field in [('01_hsa3_abc_seam_adjudications.csv', 'adjudications'), ('02_hsa3_abc_relation_actions.csv', 'actions'),
        ('03_hsa3_abc_composition_groups.csv', 'groups'), ('04_hsa3_abc_negative_constraints.csv', 'negative'),
        ('05_hsa3_abc_criteria_application.csv', 'criteria'), ('06_hsa3_abc_unresolved_crosswalk.csv', 'crosswalk'),
        ('07_hsa3_abc_frozen_integrity.csv', 'integrity'), ('11_hsa3_abc_source_facts.csv', 'facts'),
        ('12_hsa3_abc_unit_annotations.csv', 'annotations'), ('13_hsa3_fg_original_cases.csv', 'remaining')]:
        files[name] = util.csv_bytes(m[field])
    files['08_hsa3_abc_adjudication_report.md'] = m['report'].encode()
    files['09_hsa3_fg_remaining_review_packet.md'] = m['packet'].encode()
    files['14_researcher_decisions.json'], files['15_researcher_source.txt'] = s['human_bytes'], s['request']
    files['90_run_metadata.json'] = util.json_bytes(dict(version='HSA3-A/C', status='PASS', mode=s['mode'], gate_count=len(gg) + 1,
        counts=counts(m), baseline_commit=m['commit'], input_receipt=m['receipt'], frozen_receipts=s['frozen'],
        config_sha256=sha(CONFIG.read_bytes()), code_sha256=sha(Path(__file__).read_bytes()), human_input_sha256=sha(s['human_bytes']),
        researcher_source_sha256=sha(s['request']), rerun_payload_sha256=m['rerun_digest'], r44_started=False,
        lexical_scans=[], claim='SUPPLIED_A_B_C_ONLY; COMPOSITION_NOT_TEXTUAL_PARENTAGE; F_G_UNREVIEWED'))
    def seal():
        files.pop('99_manifest_sha256.csv', None)
        files['99_manifest_sha256.csv'] = util.csv_bytes([dict(file=k, sha256=sha(v)) for k, v in sorted(files.items())])
    seal()
    gg.append(dict(gate='MANIFEST_VALID', status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['10_gates.csv'] = util.csv_bytes(gg)
    seal()
    require(util.manifest_ok(files), 'output manifest')
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--archive')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args(argv)
    require(not (args.self_test and args.archive), 'self-test cannot use real archive')
    s = load(args.self_test, args.archive)
    files = serialize(build(s), s)
    require(d.h.f.a.prep.r43.frozen_receipts(s['cfg']) == s['frozen'], 'frozen sources changed during execution')
    require((ROOT / s['cfg']['human_source']['path']).read_bytes() == s['human_bytes'] and (ROOT / s['human']['source_path']).read_bytes() == s['request'], 'human source changed during execution')
    if not args.self_test:
        require(sha((Path(args.archive) if args.archive else ROOT / s['cfg']['archive']['path']).read_bytes()) == s['receipt']['sha256'], 'input archive changed')
    d.h.f.a.prep.publish(files, args.out)
    out = Path(args.out).resolve()
    zp = out.with_name(out.name + '_results.zip')
    receipt = 'HSA3-A/C PASS\n' + s['mode'] + '\nZIP SHA256 ' + sha(zp.read_bytes()) + '\n'
    out.with_name(out.name + '_run.log').write_text(receipt, encoding='utf-8')
    print(receipt)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
