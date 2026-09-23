"""HSA3-D/E: supplied seam decisions, existing-schema confirmation and constraints."""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import milal_hsa3_ana_human_freeze as h

ROOT = h.ROOT
CONFIG = ROOT / 'config/hsa3_de_job.json'
HISTORY = 'history/ana_0_3/'
EDGES = h.HISTORY + h.EDGES
NODES = h.HISTORY + h.R43 + '01_whole_book_hierarchy_nodes.csv'
UNRESOLVED = h.HISTORY + h.UNRESOLVED
SEAMS = h.HISTORY + h.SEAMS
ACCOUNTING = h.HISTORY + h.ACCOUNTING
REGISTRY = h.HISTORY + h.REGISTRY
ANA = '01_ana_human_adjudications.csv'
OVERLAYS = '11_accepted_overlay_relations.csv'
sha, rows, util = h.sha, h.rows, h.util
REVIEW_FIELDS = h.REVIEW_FIELDS


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-D/E STOP: ' + message)


def baseline_receipt(cfg):
    commit = cfg['baseline_commit']
    actual = subprocess.check_output(['git', 'rev-parse', commit + '^{commit}'], cwd=ROOT, text=True).strip()
    ancestor = subprocess.run(['git', 'merge-base', '--is-ancestor', commit, 'HEAD'], cwd=ROOT, capture_output=True).returncode == 0
    require(actual == commit and ancestor, 'baseline commit is not verified ancestry')
    return dict(expected_commit=commit, verified_commit=actual, is_ancestor=ancestor)


def audit(files, cfg, digest, synthetic=False):
    require(util.manifest_ok(files) and all(r['valid'] for r in h.nested_manifests(files)), 'input manifests')
    if not synthetic:
        require(digest == cfg['archive']['sha256'] and len(files) == cfg['archive']['members'], 'ANA.0.3 ZIP SHA/member count')
    meta = json.loads(files['90_run_metadata.json'])
    require(meta['version'] == 'HSA3-ANA.0.3' and meta['status'] == 'PASS' and meta['r44_started'] is False, 'ANA.0.3 stage/status')
    gg = rows(files['10_gates.csv'])
    require(len(gg) == meta['gate_count'] and all(g['status'] == 'PASS' for g in gg), 'ANA.0.3 gates')
    expected = json.loads((ROOT / 'config/hsa3_ana_0_3_human_decisions.json').read_bytes())['decisions']
    dd = rows(files[ANA])
    require(len(dd) == len(expected) and all(all(d[k] == value for k, value in e.items()) for d, e in zip(dd, expected)), 'ANA decisions changed')
    require(rows(files[OVERLAYS]) == [d for d in dd if d['accepted_relation_created']], 'ANA accepted overlays')
    require(len(rows(files[ACCOUNTING])) == cfg['expected']['human'] and len(rows(files[UNRESOLVED])) == cfg['expected']['unresolved'], 'frozen counts')
    require(all(r['direct_parent'] == 'UNRESOLVED' for r in rows(files[UNRESOLVED])), 'unexpected historical parentage schema')
    cases = rows(files[SEAMS])
    require([r['case_id'] for r in cases] == ['SEAM_' + x for x in 'ABCDEFG'], 'seam identities')
    require(all(r[k] == ('UNREVIEWED' if k == 'review_status' else '') for r in cases for k in REVIEW_FIELDS), 'historical review fields')
    return dict(sha256=digest, members=len(files), mode='SYNTHETIC_FIXTURE' if synthetic else 'VERIFIED_FROZEN_ARTIFACT', manifests=h.nested_manifests(files))


def load(self_test=False, archive=None):
    cfg = json.loads(CONFIG.read_bytes())
    commit = baseline_receipt(cfg)
    frozen = h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['expected'] == r['actual'] for r in frozen), 'frozen repository files changed')
    human_bytes = (ROOT / cfg['human_source']['path']).read_bytes()
    require(sha(human_bytes) == cfg['human_source']['sha256'], 'canonical human input SHA')
    human = json.loads(human_bytes)
    request = (ROOT / human['source_path']).read_bytes()
    require(sha(request) == human['source_sha256'], 'researcher request SHA')
    if self_test:
        prior = h.load(self_test=True)
        files = h.serialize(h.build(prior), prior)
        digest = sha(files['99_manifest_sha256.csv'])
    else:
        data = (Path(archive) if archive else ROOT / cfg['archive']['path']).read_bytes()
        digest = sha(data)
        require(digest == cfg['archive']['sha256'], 'ANA.0.3 ZIP SHA')
        files = h.f.a.prep.r43.h1.src.archive(data, digest, mr1=True)['files']
    receipt = audit(files, cfg, digest, self_test)
    return dict(cfg=cfg, commit=commit, frozen=frozen, human=human, human_bytes=human_bytes, request=request,
                files=files, receipt=receipt, mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_ARTIFACT_ADJUDICATION')


def locate(s, member, key, identity):
    rr = h.raw_rows(s['files'][member])
    hits = [(i, r) for i, r in enumerate(rr, 1) if r[key] == identity]
    require(len(hits) == 1, 'missing/duplicate exact identity: ' + identity)
    i, r = hits[0]
    return dict(source_member=HISTORY + member, source_data_row=i, source_identity_field=key, source_identity=identity,
                source_row_sha256=h.f.rowhash(r), source_member_sha256=sha(s['files'][member]), source_artifact_sha256=s['receipt']['sha256'])


def semantic_key(r):
    # Explicit schema aliases, not Hebrew/span/similarity matching.
    typ = 'NARRATIVE_INTRODUCTION' if r['relation_type'] == 'INTRODUCES_AND_ENCLOSES' else r['relation_type']
    return r['source_node'], r['target_node'], typ


def relation_actions(s):
    edges = rows(s['files'][EDGES])
    nodes = {r['node_id']: r for r in rows(s['files'][NODES])}
    out, done, confirmed = [], {}, set()
    def append(request):
        require(request['source_node'] in nodes and request['target_node'] in nodes, 'relation endpoint identity')
        key = semantic_key(request)
        matches = [r for r in edges if semantic_key(r) == key]
        require(len(matches) <= 1, 'ambiguous existing semantic relation: ' + str(key))
        action = deepcopy(request)
        action.update(action_id='HSA3-DE-A:' + request['request_id'], researcher_supplied=True,
                      automatic_resolution=False, causal_assertion=False, basis='EXPLICIT_RESEARCHER_DECISION',
                      evidence_node_ids=[request['source_node'], request['target_node']],
                      evidence_ids=sorted(set(nodes[request['source_node']]['source_evidence_ids'] + nodes[request['target_node']]['source_evidence_ids'])),
                      source_request_sha256=sha(s['request']), human_input_sha256=sha(s['human_bytes']))
        if key in done:
            action.update(action='NO_ACTION_DUPLICATE', canonical_relation_id=done[key], existing_relation_ids=[], existing_record={}, duplicate_of=done[key])
        elif matches:
            e = matches[0]
            action.update(action='CONFIRMED_EXISTING', canonical_relation_id=e['edge_id'], existing_relation_ids=[e['edge_id']], existing_record=deepcopy(e), duplicate_of='',
                          **locate(s, EDGES, 'edge_id', e['edge_id']))
            confirmed.add(e['edge_id'])
            done[key] = e['edge_id']
        else:
            ident = 'HSA3-DE-R:' + h.f.rowhash(dict(source=key[0], target=key[1], relation=key[2], dimension=request['dimension']))[:20]
            action.update(action='NEGATIVE_CONSTRAINT_CREATED' if request['polarity'] == 'NEGATIVE' else 'CREATED', canonical_relation_id=ident,
                          existing_relation_ids=[], existing_record={}, duplicate_of='')
            done[key] = ident
        action['assertion_scope'] = 'UNIT_COMPOSITION_NOT_VERSE_PARENTAGE' if key[2] == 'NARRATIVE_INTRODUCTION' else ('GROUP_TERMINAL_NOT_DIRECT_LOCAL_CLOSURE' if key[2] == 'TERMINATES_ENCLOSING_GROUP' else 'EXACT_DIMENSION_ONLY')
        if request['polarity'] == 'NEGATIVE':
            action['negative_authority'] = 'EXPLICIT_HUMAN_NEGATIVE_CONSTRAINT_NOT_AUTOMATIC_ABSENCE_OF_EVIDENCE'
            action['direction_note'] = 'Source is excluded as direct parent of target; not a CHILD_OF edge.' if key[2] == 'NO_DIRECT_PARENTAGE' else 'The source ending is not established as the direct response antecedent of target onset.'
        out.append(action)
    for request in s['human']['requests']:
        append(request)
    p = s['human']['preserve']
    onsets = set(p['onsets'])
    for e in edges:
        preserve = ((e['relation_type'] == 'TRANSITION_COMPONENT' and e['source_node'] == e['target_node'] == p['transition']) or
                    (e['relation_type'] == 'GROUP_MEMBER_OF' and e['source_node'] in onsets and e['target_node'] == p['group']) or
                    (e['relation_type'] == 'SAME_LEVEL_SIBLING' and e['source_node'] in onsets and e['target_node'] in onsets))
        if preserve and e['edge_id'] not in confirmed:
            append(dict(request_id='PRESERVE:' + e['edge_id'], seam_id='SEAM_D', source_node=e['source_node'], target_node=e['target_node'],
                        relation_type=e['relation_type'], dimension='COMPOSITION_GROUPING' if e['relation_type'] == 'GROUP_MEMBER_OF' else ('TRANSITION' if e['relation_type'] == 'TRANSITION_COMPONENT' else 'SAME_LEVEL_RELATION'),
                        polarity='POSITIVE', criteria_codes=(['E-PARTICIPANT-ALIGNMENT', 'E-EXPLICIT-CLOSURE', 'N-ADJACENCY-ONLY'] if e['relation_type'] == 'TRANSITION_COMPONENT' else ['E-FUNCTIONAL-EQUIVALENCE', 'E-DISTRIBUTIONAL-PATTERN', 'N-SPEAKER-ONLY', 'N-FORMULA-LENGTH-ONLY']),
                        authority='RESEARCHER_CONFIRMS_EXISTING', textual_parentage_created=False))
    return out


def adjudications(s, actions):
    out = []
    for d in s['human']['decisions']:
        row = deepcopy(d)
        row.update(action_ids=[a['action_id'] for a in actions if a['seam_id'] == d['seam_id']],
                   exact_textual_parent_assigned=False, new_composition_group_created=False, r44_started=False,
                   original_case=next(c for c in rows(s['files'][SEAMS]) if c['case_id'] == d['seam_id']),
                   source_request_sha256=sha(s['request']), human_input_sha256=sha(s['human_bytes']),
                   **locate(s, SEAMS, 'case_id', d['seam_id']))
        out.append(row)
    return out


def criteria(s, actions):
    registry = {r['evidence_code']: r for r in rows(s['files'][REGISTRY])}
    out = []
    for item in actions + s['human']['decisions']:
        ident = item.get('action_id', item.get('decision_id'))
        for code in item['criteria_codes']:
            require(code in registry, 'unknown criteria code: ' + code)
            out.append(dict(decision_or_action_id=ident, seam_id=item['seam_id'], evidence_code=code,
                            use='INSUFFICIENT_ALONE' if code.startswith('N-') else 'HUMAN_REASONING_CONTRIBUTION_NOT_AUTOMATIC_SUFFICIENCY',
                            registry_record=registry[code], **locate(s, REGISTRY, 'evidence_code', code)))
        out.append(dict(decision_or_action_id=ident, seam_id=item['seam_id'], evidence_code='', use='METHODOLOGICAL_NOTE',
                        note='Independently accepted unit functions and participant introduction/composition remain separate from verse parentage. Response semantics not established; overlay does not imply parentage. No formula-length rule or new registry code.'))
    return out


def resolution_crosswalk(s, actions):
    cases = rows(s['files'][SEAMS])
    direct = {n for a in actions for n in (a['source_node'], a['target_node'])}
    owners = {}
    for case in cases:
        for node in case['primary_unresolved_rows']:
            require(node not in owners, 'duplicate primary unresolved owner')
            owners[node] = case['case_id']
    out = []
    for old in rows(s['files'][UNRESOLVED]):
        require(old.get('direct_parent') == 'UNRESOLVED' and bool(old.get('reason')), 'schema: required historical direct_parent/reason')
        node = old['node_id']
        require(node in owners, 'missing primary unresolved owner')
        touched = node in direct
        applicable = [a['action_id'] for a in actions if node in (a['source_node'], a['target_node'])]
        # A negative exclusion, group membership or terminal effect cannot answer
        # the historical exact-direct-parent question. No such positive edge is supplied.
        direct_parent = [a for a in actions if a['action'] == 'CREATED' and a['relation_type'] == 'CHILD_OF' and a['source_node'] == node]
        require(not direct_parent, 'new exact parent is outside this seam authorization')
        out.append(dict(node_id=node, primary_seam=owners[node], historical_record=deepcopy(old),
                        status='REMAINS_UNRESOLVED' if touched else 'NOT_APPLICABLE_TO_THIS_SEAM_DECISION',
                        direct_parent_before=old['direct_parent'], direct_parent_after=old['direct_parent'], direct_parent_resolved=False,
                        affected_by_de=touched, action_ids=applicable, historical_input_modified=False,
                        reason='Accepted composition/terminal relations and negative exclusions do not assign an exact textual parent.' if touched else 'Outside the supplied D/E decision; original unresolved parentage retained.',
                        **locate(s, UNRESOLVED, 'node_id', node)))
    return out


def dependencies(s):
    out = []
    for prior in rows(s['files']['06_hsa3_dependency_update.csv']):
        q = prior['review_question_id']
        d = next(d for d in rows(s['files'][ANA]) if d['review_question_id'] == q)
        out.append(dict(seam_id=prior['case_id'], review_question_id=q, status=d['status'], decision_type=d['decision_type'],
                        role='UNRESOLVED_CANDIDATE_EVIDENCE_ONLY' if d['status'] == 'UNRESOLVED' else 'ACCEPTED_OVERLAY_RETAINED_NOT_PARENTAGE',
                        resolves_q3=False, creates_parentage=False, original_dependency=prior, **locate(s, ANA, 'review_question_id', q)))
    return out


def facts(s):
    nodes = {r['node_id']: r for r in rows(s['files'][NODES])}
    ids = s['human']['preserve']
    selected = [ids[k] for k in ('transition', 'intro', 'terminal', 'yhwh', 'group')] + ids['onsets'] + ['H:HSA026', 'H:HSA028']
    return [dict(node_id=n, original_record=nodes[n], **locate(s, NODES, 'node_id', n)) for n in selected]


def integrity(s, historical):
    return [dict(member=HISTORY + k, expected_sha256=sha(v), actual_sha256=sha(historical.get(k, b'')),
                 status='PASS' if historical.get(k) == v else 'FAIL') for k, v in sorted(s['files'].items())]


def counts(m):
    cc = Counter(a['action'] for a in m['actions'])
    xx = m['crosswalk']
    return dict(researcher_seam_decisions=len(m['adjudications']), new_positive_relations=cc['CREATED'],
                confirmed_existing_relations=cc['CONFIRMED_EXISTING'], new_negative_constraints=cc['NEGATIVE_CONSTRAINT_CREATED'],
                duplicate_skipped_relations=cc['NO_ACTION_DUPLICATE'], new_textual_parentage=sum(a['textual_parentage_created'] for a in m['actions']),
                resolved_by_de=sum(r['status'] in ('RESOLVED_BY_SEAM_D', 'RESOLVED_BY_SEAM_E') for r in xx),
                de_relevant_still_unresolved=sum(r['status'] == 'REMAINS_UNRESOLVED' for r in xx),
                not_applicable=sum(r['status'] == 'NOT_APPLICABLE_TO_THIS_SEAM_DECISION' for r in xx),
                all_still_unresolved=sum(not r['direct_parent_resolved'] for r in xx),
                remaining_seam_primary_rows=sum(r['primary_seam'] not in ('SEAM_D', 'SEAM_E') for r in xx))


def report(m, s):
    lines = ['# HSA3-D/E — Elihu Global Seam Human Adjudication', '', s['mode'], '',
             'SEAM_D and SEAM_E are FROZEN researcher decisions. This records existing evidence and supplied judgments; no new lexical analysis or R4.4.', '',
             '## Computed action accounting', '', h.f.canonical(counts(m)), '',
             'Confirmed-existing counts refer to existing canonical edge rows (including the historical directed sibling records), not newly invented human judgments.', '',
             '| Action | Source | Relation | Target | Disposition |', '| --- | --- | --- | --- | --- |']
    lines += [f"| {a['action_id']} | {a['source_node']} | {a['relation_type']} | {a['target_node']} | {a['action']} |" for a in m['actions']]
    lines += ['', '## Methodological interpretation', '',
              '32:1 remains an independent TRANSITION_COMPONENT. Its Q2 post-closure transition is separate from the composition of 32:2–37:24. It is not the textual parent of the introduction, sequence or 32:6.',
              'The existing HSA019 → ELIHU_SPEECH_SEQUENCE NARRATIVE_INTRODUCTION is confirmed with its exact existing edge ID. Unit-level introduction/composition does not create 32:6 CHILD_OF 32:2.',
              'The four Elihu onsets remain same-level peers and group members. No additional ELIHU_INTERVENTION_COMPLEX is needed; the existing group remains NON_TEXTUAL_GROUP.',
              '37:24 retains SPEECH_UNIT_END; its group-terminal relation is distinct from direct local closure or a textual parent. The supplied group scope is 32:6–37:24, preserved as human scope metadata, not rewritten into historical node coverage.',
              '37:24 → 38:1 has explicit human NO_DIRECT_PARENTAGE and NO_DIRECT_RESPONSE_ANTECEDENT constraints. They are dimension-specific judgments, not automatic deductions from missing evidence or a universal claim of no relationship.',
              'NO DIRECT HIERARCHICAL EDGE does not mean NO RHETORICAL/DISCOURSE RELATION. Q4 CONTRASTIVE_ANA_FRAME and Q5 ELIHU_RESPONSE_ROLE_INTERVENTION remain accepted and unchanged.',
              'TEXTUAL HIERARCHY, COMPOSITION/GROUPING, TRANSITION, OVERLAY/RESPONSIO and RESPONSE RELATION remain distinct. Adjacency, speaker succession, thematic continuity, nearest opening and formula length alone assign no parent.',
              '38:1/40:6 same-level major onsets and 40:1 CHILD_OF 38:1 remain accepted contextual/distributional judgments; no formula-length explanation replaces them.', '',
              '## Q3 and unresolved accounting', '',
              'Q3 remains UNRESOLVED / HUMAN_DEFERRED, with lexical/participant evidence as dependency only. No causal or fulfillment assertion is authorized. SEAM_E does not resolve Q3.',
              'Every historical unresolved row asks for an exact direct textual parent. Negative exclusions, introduction, grouping and termination do not answer that question. D/E seam decisions can be frozen while those parentage questions remain unresolved. All 57 source rows remain byte-identical.',
              'The crosswalk separates D/E-relevant unresolved rows from not-applicable rows. Primary seam ownership is preserved; the 38:1 node is shared E evidence but remains owned by unadjudicated SEAM_F.', '',
              '## Preserved history', '',
              '59 historical judgments and the three HSA2-F 31:40 relations remain intact. ANA-Q2/Q3/Q4/Q5 and all input artifacts are unchanged. Other seams A–C/F–G are unadjudicated.',
              'Canonical existing evidence codes only; missing functional-distinction/response/overlay concepts are notes, not registry mutations or automatic sufficiency.', '']
    return '\n'.join(lines)


def remaining_packet(m, s):
    edges = {r['edge_id']: r for r in rows(s['files'][EDGES])}
    lines = ['# HSA3 remaining seam review packet', '', 'SEAM_D: FROZEN. SEAM_E: FROZEN. Only A–C/F–G remain for new seam adjudication.',
             'D/E exact-direct-parent residual questions are not silently marked resolved. Q3 remains UNRESOLVED/HUMAN_DEFERRED. R4.4 has not started.', '']
    for c in m['remaining']:
        lines += ['## ' + c['case_id'] + ' — ' + c['title'], '', c['question'], '',
                  'Primary unresolved nodes: ' + ', '.join(c['primary_unresolved_rows']), '',
                  'Participating unresolved nodes: ' + ', '.join(c['participating_unresolved_rows']), '',
                  'Current evidence — exact source judgments: ' + ', '.join(c['source_judgment_ids']), '',
                  'Full case/evidence: [' + c['case_id'] + '](' + HISTORY + SEAMS + '); [historical edges](' + HISTORY + EDGES + '). All raw evidence IDs remain in these files.', '',
                  'Criteria dimensions for the open attachment question: PARENTAGE_CONTAINMENT; STRUCTURAL_FUNCTION; SAME_LEVEL_RELATION; CLOSURE_TARGET where applicable. No choice is prefilled.', '',
                  '| Accepted constraint | Source | Relation | Target |', '| --- | --- | --- | --- |']
        for label, key in [('POSITIVE', 'positive_constraint_ids'), ('NEGATIVE', 'negative_constraint_ids')]:
            for ident in c[key]:
                require(ident in edges, 'remaining constraint missing exact edge ' + ident)
                e = edges[ident]
                lines.append(f"| {label}: {ident} | {e['source_node']} | {e['relation_type']} | {e['target_node']} |")
        if not c['negative_constraint_ids']:
            lines += ['','No historical negative constraint listed for this case; this is not a new negative judgment.']
        shared = [a for a in m['negative'] if a['source_node'] in c['involved_nodes'] or a['target_node'] in c['involved_nodes']]
        if shared:
            lines += ['', 'Frozen D/E constraints involving a shared node (context only; no adjudication of this seam):']
            lines += [f"- {a['canonical_relation_id']}: {a['source_node']} → {a['target_node']} {a['relation_type']} ({a['dimension']})." for a in shared]
        lines += ['', '| Researcher field | Value |', '| --- | --- |']
        lines += [f'| {k} | {c[k]} |' for k in REVIEW_FIELDS]
        lines += ['']
    return '\n'.join(lines)


def derive(s):
    aa = relation_actions(s)
    m = dict(actions=aa, adjudications=adjudications(s, aa), criteria=criteria(s, aa), crosswalk=resolution_crosswalk(s, aa),
             negative=[deepcopy(a) for a in aa if a['polarity'] == 'NEGATIVE' and a['action'] != 'NO_ACTION_DUPLICATE'],
             positive=[deepcopy(a) for a in aa if a['action'] == 'CREATED'], dependencies=dependencies(s), facts=facts(s),
             remaining=[deepcopy(c) for c in rows(s['files'][SEAMS]) if c['case_id'] in s['cfg']['expected']['remaining_seams']],
             historical=deepcopy(s['files']), receipt=deepcopy(s['receipt']), commit=deepcopy(s['commit']),
             ana=deepcopy(rows(s['files'][ANA])), overlays=deepcopy(rows(s['files'][OVERLAYS])),
             scope=dict(group=s['human']['preserve']['group'], scope_ref=s['human']['preserve']['group_scope'], authority='RESEARCHER_SUPPLIED_NON_TEXTUAL_GROUP_SCOPE'),
             groups_created=[], r44_started=False, lexical_scans=[])
    m['integrity'] = integrity(s, m['historical'])
    m['report'] = report(m, s)
    m['packet'] = remaining_packet(m, s)
    return m


def digest(m):
    return h.f.rowhash({k: ({n: sha(v) for n, v in value.items()} if k == 'historical' else value) for k, value in m.items() if k != 'rerun_digest'})


def build(s):
    m = derive(s)
    m['rerun_digest'] = digest(derive(s))
    return m


def gates(m, s):
    aa = relation_actions(s)
    original_nodes = {r['node_id']: r for r in rows(s['files'][NODES])}
    current_facts = {r['node_id']: r['original_record'] for r in m['facts']}
    by = {r['seam_id']: r for r in m['adjudications']}
    expected_decisions = {r['seam_id']: r for r in adjudications(s, aa)}
    ana = {r['review_question_id']: r for r in m['ana']}
    orig_ana = {r['review_question_id']: r for r in rows(s['files'][ANA])}
    p = s['human']['preserve']
    def has(src, tgt, rel):
        return any(a['source_node'] == src and a['target_node'] == tgt and a['relation_type'] == rel and a['action'] != 'NO_ACTION_DUPLICATE' for a in m['actions'])
    def unchanged(member):
        return m['historical'].get(member) == s['files'][member]
    checks = {}
    checks['BASELINE_COMMIT_VERIFIED'] = m['commit'] == s['commit'] and m['commit']['verified_commit'] == s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    checks['ANA_0_3_FROZEN_VERIFIED'] = m['receipt'] == s['receipt'] and unchanged('90_run_metadata.json') and util.manifest_ok(m['historical'])
    checks['FROZEN_SOURCE_FILES'] = len(s['frozen']) == len(s['cfg']['frozen_files']) and all(r['actual'] == r['expected'] == s['cfg']['frozen_files'][r['path']] for r in s['frozen'])
    checks['RESEARCHER_SOURCE_EXACT'] = sha(s['human_bytes']) == s['cfg']['human_source']['sha256'] and json.loads(s['human_bytes']) == s['human'] and sha(s['request']) == s['human']['source_sha256']
    for seam in ('SEAM_D', 'SEAM_E'):
        checks[seam + '_RESEARCHER_DECISION_RECORDED'] = by.get(seam) == expected_decisions[seam]
    checks['JOB_32_1_REMAINS_TRANSITION'] = current_facts.get(p['transition']) == original_nodes[p['transition']] and original_nodes[p['transition']]['structural_function'] == 'TRANSITION_COMPONENT'
    checks['JOB_32_1_NOT_PARENT_OF_ELIHU'] = has(p['transition'], p['intro'], 'NO_DIRECT_PARENTAGE') and has(p['transition'], p['group'], 'NO_DIRECT_PARENTAGE') and not any(a['textual_parentage_created'] for a in m['actions'])
    checks['ELIHU_INTRO_RELATION_PRESENT'] = has(p['intro'], p['group'], 'NARRATIVE_INTRODUCTION') and current_facts.get(p['intro']) == original_nodes[p['intro']] and all(a['assertion_scope'] == 'UNIT_COMPOSITION_NOT_VERSE_PARENTAGE' for a in m['actions'] if a['relation_type'] == 'NARRATIVE_INTRODUCTION')
    sibling = lambda a: a['relation_type'] in ('SAME_LEVEL_SIBLING', 'GROUP_MEMBER_OF')
    checks['ELIHU_SPEECH_SIBLINGS_PRESERVED'] = [a for a in m['actions'] if sibling(a)] == [a for a in aa if sibling(a)] and unchanged(EDGES)
    checks['ELIHU_SEQUENCE_TERMINAL_37_24'] = has(p['terminal'], p['group'], 'TERMINATES_ENCLOSING_GROUP') and current_facts.get(p['terminal']) == original_nodes[p['terminal']] and original_nodes[p['terminal']]['structural_function'] == 'SPEECH_UNIT_END' and m['scope'] == dict(group=p['group'], scope_ref=p['group_scope'], authority='RESEARCHER_SUPPLIED_NON_TEXTUAL_GROUP_SCOPE')
    checks['NO_DIRECT_PARENTAGE_37_24_38_1'] = has(p['terminal'], p['yhwh'], 'NO_DIRECT_PARENTAGE')
    checks['NO_DIRECT_RESPONSE_ANTECEDENT_37_24_38_1'] = has(p['terminal'], p['yhwh'], 'NO_DIRECT_RESPONSE_ANTECEDENT')
    for q, name in [('ANA-Q2', 'ANA_Q2_PRESERVED'), ('ANA-Q3', 'ANA_Q3_STILL_UNRESOLVED'), ('ANA-Q4', 'ANA_Q4_PRESERVED'), ('ANA-Q5', 'ANA_Q5_PRESERVED')]:
        checks[name] = ana.get(q) == orig_ana[q]
    checks['OVERLAYS_NOT_DELETED_OR_PROMOTED'] = m['overlays'] == rows(s['files'][OVERLAYS]) and not any(a['textual_parentage_created'] for a in m['actions'])
    created = [a for a in m['actions'] if a['action'] in ('CREATED', 'NEGATIVE_CONSTRAINT_CREATED')]
    old_keys = {semantic_key(r) for r in rows(s['files'][EDGES])}
    checks['NO_DUPLICATE_RELATIONS'] = len({semantic_key(a) for a in created}) == len(created) and not any(semantic_key(a) in old_keys for a in created)
    checks['RELATION_ACTIONS_EXACT'] = m['actions'] == aa and m['positive'] == [a for a in aa if a['action'] == 'CREATED']
    checks['NEGATIVE_CONSTRAINTS_EXPLICIT'] = m['negative'] == [a for a in aa if a['polarity'] == 'NEGATIVE' and a['action'] != 'NO_ACTION_DUPLICATE']
    checks['NO_ADJACENCY_PARENTAGE'] = all(a['basis'] == 'EXPLICIT_RESEARCHER_DECISION' and not a['textual_parentage_created'] and a['relation_type'] not in ('CHILD_OF', 'HIERARCHICALLY_ABOVE', 'CONTINUES_WITHIN', 'RESPONSE_TO') for a in m['actions'])
    checks['NO_FORMULA_LENGTH_RULE'] = m['criteria'] == criteria(s, aa) and not any(a['basis'] == 'FORMULA_LENGTH' for a in m['actions'])
    checks['OTHER_SEAMS_UNCHANGED'] = set(by) == {'SEAM_D', 'SEAM_E'} and m['remaining'] == [c for c in rows(s['files'][SEAMS]) if c['case_id'] in s['cfg']['expected']['remaining_seams']] and unchanged(SEAMS)
    checks['HSA2_F_INTEGRITY'] = unchanged(EDGES) and unchanged(ACCOUNTING)
    checks['HISTORICAL_ARTIFACTS_UNCHANGED'] = m['historical'] == s['files']
    checks['UNRESOLVED_CROSSWALK_FAITHFUL'] = m['crosswalk'] == resolution_crosswalk(s, aa) and unchanged(UNRESOLVED)
    checks['DEPENDENCIES_Q3_NOT_RESOLVED'] = m['dependencies'] == dependencies(s)
    checks['NO_NEW_COMPOSITION_PARENT'] = m['groups_created'] == [] and current_facts.get(p['group']) == original_nodes[p['group']] and original_nodes[p['group']]['structural_function'] == 'NON_TEXTUAL_GROUP'
    checks['NO_CAUSAL_OR_FULFILLMENT'] = all(a['causal_assertion'] is False for a in m['actions']) and m['report'] == report(m, s)
    checks['SOURCE_FACTS_EXACT'] = m['facts'] == facts(s)
    checks['INTEGRITY_RECEIPTS_COMPUTED'] = m['integrity'] == integrity(s, m['historical']) and all(r['status'] == 'PASS' for r in m['integrity'])
    checks['NO_R4_4'] = m['r44_started'] is False and all(r['r44_started'] is False for r in m['adjudications'])
    checks['NO_NEW_LEXICAL_ANALYSIS'] = m['lexical_scans'] == []
    checks['REMAINING_PACKET_FAITHFUL'] = m['packet'] == remaining_packet(m, s)
    checks['DETERMINISTIC_RERUN'] = m['rerun_digest'] == digest(m)
    return [dict(gate=k, status='PASS' if value else 'FAIL') for k, value in checks.items()]


def serialize(m, s):
    gg = gates(m, s)
    require(all(g['status'] == 'PASS' for g in gg), h.f.canonical([g for g in gg if g['status'] == 'FAIL']))
    files = {HISTORY + k: v for k, v in m['historical'].items()}
    for name, key in [('01_hsa3_de_seam_adjudications.csv', 'adjudications'), ('02_hsa3_de_relation_actions.csv', 'actions'),
                      ('03_hsa3_de_criteria_application.csv', 'criteria'), ('04_hsa3_de_unresolved_crosswalk.csv', 'crosswalk'),
                      ('05_hsa3_de_negative_constraints.csv', 'negative'), ('06_hsa3_de_dependency_links.csv', 'dependencies'),
                      ('07_hsa3_de_frozen_integrity.csv', 'integrity'), ('11_hsa3_de_source_facts.csv', 'facts'),
                      ('12_hsa3_remaining_seam_cases.csv', 'remaining'), ('13_hsa3_de_created_positive_relations.csv', 'positive')]:
        files[name] = util.csv_bytes(m[key])
    files['08_hsa3_de_adjudication_report.md'] = m['report'].encode()
    files['09_hsa3_remaining_seams_review_packet.md'] = m['packet'].encode()
    files['14_researcher_decisions.json'] = s['human_bytes']
    files['15_researcher_source.txt'] = s['request']
    files['90_run_metadata.json'] = util.json_bytes(dict(version='HSA3-D/E', mode=s['mode'], status='PASS', gate_count=len(gg)+1,
        baseline_commit=m['commit'], baseline_receipt=m['receipt'], counts=counts(m), frozen_receipts=s['frozen'],
        config_sha256=sha(CONFIG.read_bytes()), code_sha256=sha(Path(__file__).read_bytes()), human_input_sha256=sha(s['human_bytes']),
        researcher_source_sha256=sha(s['request']), group_scope=m['scope'], rerun_payload_sha256=m['rerun_digest'],
        r44_started=m['r44_started'], lexical_scans=m['lexical_scans'], claim='RESEARCHER_SUPPLIED_D_E_ONLY; Q3 UNRESOLVED; NO TEXTUAL_PARENTAGE'))
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
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--out', required=True)
    p.add_argument('--archive')
    p.add_argument('--self-test', action='store_true')
    args = p.parse_args(argv)
    require(not (args.self_test and args.archive), 'self-test cannot use real archive')
    s = load(args.self_test, args.archive)
    files = serialize(build(s), s)
    require(h.f.a.prep.r43.frozen_receipts(s['cfg']) == s['frozen'], 'frozen sources changed during execution')
    require((ROOT / s['cfg']['human_source']['path']).read_bytes() == s['human_bytes'] and (ROOT / s['human']['source_path']).read_bytes() == s['request'], 'human source changed during execution')
    if not args.self_test:
        require(sha((Path(args.archive) if args.archive else ROOT / s['cfg']['archive']['path']).read_bytes()) == s['receipt']['sha256'], 'archive changed during execution')
    h.f.a.prep.publish(files, args.out)
    out = Path(args.out).resolve()
    zp = out.with_name(out.name + '_results.zip')
    out.with_name(out.name + '_run.log').write_text('HSA3-D/E PASS\n' + s['mode'] + '\nZIP SHA256 ' + sha(zp.read_bytes()) + '\n', encoding='utf-8')
    print('HSA3-D/E PASS ' + str(zp) + ' SHA256 ' + sha(zp.read_bytes()))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
