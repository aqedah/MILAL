"""HSA3-ANA.0.3: freeze supplied human decisions; never adjudicate parentage."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_hsa3_ana_response_family_addendum as f

ROOT = f.ROOT
CONFIG = ROOT / 'config/hsa3_ana_0_3_job.json'
HISTORY = 'history/ana_0_2/'
PREP = f.HISTORY + 'history/hsa3_prep/'
R43 = f.HISTORY + f.R43
CANDIDATES = f.HISTORY + '04_post_31_40_relation_candidates.csv'
SEAMS = PREP + '03_global_seam_cases.csv'
ACCOUNTING = R43 + '10_human_judgment_accounting.csv'
UNRESOLVED = R43 + '03_unresolved_parentage.csv'
EDGES = R43 + '02_whole_book_hierarchy_edges.csv'
ADDENDUM = '06_ana_0_1_candidate_evidence_addendum.csv'
QUESTIONS = '16_unchanged_review_questions.csv'
REGISTRY = '08_hsa_adjudication_criteria_registry.csv'
REVIEW_FIELDS = f.a.prep.REVIEW_FIELDS
sha = f.sha
util = f.util
rows = f.a.prep.decode_rows
raw_rows = f.a.prep.r43.h1.read_csv


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-ANA.0.3 STOP: ' + message)


def nested_manifests(files):
    checks = []
    for name in sorted(files):
        if name.endswith('99_manifest_sha256.csv'):
            prefix = name[:-len('99_manifest_sha256.csv')]
            subset = {k[len(prefix):]: v for k, v in files.items() if k.startswith(prefix)}
            checks.append(dict(member=name, sha256=sha(files[name]), valid=util.manifest_ok(subset)))
    return checks


def baseline_audit(files, cfg, digest, synthetic=False):
    require(util.manifest_ok(files), 'baseline manifest')
    require(all(x['valid'] for x in nested_manifests(files)), 'nested manifest')
    if not synthetic:
        require(digest == cfg['archive']['sha256'] and len(files) == cfg['archive']['members'], 'baseline SHA/member count')
    meta = json.loads(files['90_run_metadata.json'])
    require(meta['version'] == 'HSA3-ANA.0.2' and meta['status'] == 'PASS', 'baseline stage/status')
    gg = rows(files['14_gates.csv'])
    require(bool(gg) and all(g['status'] == 'PASS' for g in gg) and len(gg) == meta['gate_count'], 'baseline gates')
    require(meta['counts']['new_human_judgments'] == meta['counts']['new_structural_relations'] == 0, 'baseline adjudication')
    candidates = rows(files[CANDIDATES])
    require([c['candidate_id'] for c in candidates] == ['ANA-C1', 'ANA-C2', 'ANA-C3', 'ANA-C4'], 'candidate identities')
    require(all(c['status'] == 'UNADJUDICATED' and c['automatic_resolution'] is False for c in candidates), 'candidate status')
    require(len(rows(files[ACCOUNTING])) == cfg['expected']['human'], 'frozen human count')
    require(len(rows(files[UNRESOLVED])) == cfg['expected']['unresolved'], 'unresolved count')
    cases = rows(files[SEAMS])
    require([c['case_id'] for c in cases] == ['SEAM_' + x for x in 'ABCDEFG'], 'A-G identities')
    require(all(c[k] == ('UNREVIEWED' if k == 'review_status' else '') for c in cases for k in REVIEW_FIELDS), 'A-G review fields')
    require(all(not c['candidate_parents'] and c['automatic_resolution'] is False for c in cases), 'A-G parentage')
    require(rows(files[REGISTRY]) == rows(util.csv_bytes(f.criteria.registry())), 'frozen criteria registry')
    require(all(q[k] == ('UNREVIEWED' if k == 'review_status' else '') for q in rows(files[QUESTIONS]) for k in REVIEW_FIELDS), 'historical Q1-Q5 fields')
    closure = {(e['target_node'], e['relation_type']) for e in rows(files[EDGES]) if e['source_node'] == 'H:HSA017'}
    require({('H:HSA016', 'DIRECT_LOCAL_CLOSURE'), ('H:HSA015', 'NO_DIRECT_RELATION'), ('POST_DIALOGUE_JOB', 'TERMINATES_ENCLOSING_GROUP')} <= closure, 'HSA2-F closure')
    return dict(sha256=digest, member_count=len(files), mode='SYNTHETIC_FIXTURE' if synthetic else 'VERIFIED_FROZEN_ARTIFACT', manifests=nested_manifests(files))


def load(self_test=False, archive=None):
    cfg = json.loads(CONFIG.read_bytes())
    frozen = f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['actual'] == r['expected'] for r in frozen), 'frozen source files changed')
    human_bytes = (ROOT / cfg['human_source']['path']).read_bytes()
    require(sha(human_bytes) == cfg['human_source']['sha256'], 'human decisions SHA')
    human = json.loads(human_bytes)
    request_bytes = (ROOT / human['source_path']).read_bytes()
    require(sha(request_bytes) == human['source_sha256'], 'researcher source SHA')
    if self_test:
        old = f.load(self_test=True)
        files = f.serialize(f.build(old), old)
        digest = sha(files['99_manifest_sha256.csv'])
    else:
        path = Path(archive) if archive else ROOT / cfg['archive']['path']
        data = path.read_bytes()
        digest = sha(data)
        require(digest == cfg['archive']['sha256'], 'baseline ZIP SHA')
        files = f.a.prep.r43.h1.src.archive(data, digest, mr1=True)['files']
    receipt = baseline_audit(files, cfg, digest, self_test)
    return dict(cfg=cfg, files=files, human=human, human_bytes=human_bytes, request_bytes=request_bytes,
                frozen=frozen, receipt=receipt, mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_ARTIFACT_HUMAN_FREEZE')


def locate(s, member, key, identity):
    table = raw_rows(s['files'][member])
    hits = [(i, r) for i, r in enumerate(table, 1) if r[key] == identity]
    require(len(hits) == 1, 'exact source identity missing/duplicate: ' + identity)
    i, r = hits[0]
    return dict(source_member=HISTORY + member, source_data_row=i, source_row_sha256=f.rowhash(r),
                source_member_sha256=sha(s['files'][member]), source_identity=identity,
                source_identity_field=key, source_artifact_sha256=s['receipt']['sha256'])


def evidence_index(s):
    index = {}
    for member in ('01_response_lexical_family_inventory.csv', '02_semantic_response_neighbor_inventory.csv', '03_response_context_reframing.csv'):
        for r in rows(s['files'][member]):
            ident = r['evidence_id']
            require(ident not in index, 'duplicate evidence identity: ' + ident)
            index[ident] = (member, 'evidence_id')
    for r in rows(s['files'][ACCOUNTING]):
        require(r['judgment_id'] not in index, 'duplicate judgment identity')
        index[r['judgment_id']] = (ACCOUNTING, 'judgment_id')
    return index


def decisions(s):
    originals = {r['candidate_id']: r for r in rows(s['files'][CANDIDATES])}
    addenda = {r['candidate_id']: r for r in rows(s['files'][ADDENDUM])}
    out = []
    for supplied in s['human']['decisions']:
        d = deepcopy(supplied)
        c = originals[d['original_candidate_id']]
        add = addenda[c['candidate_id']]
        evidence = c['occurrence_ids'] + c['positional_interval_occurrence_ids'] + add['direct_new_evidence_ids'] + add['contextual_new_evidence_ids'] + add['existing_verbal_evidence_ids']
        # Existing explicit judgment IDs: no surface/span identity inference.
        if d['review_question_id'] == 'ANA-Q2':
            evidence += ['HSA017', 'HSA018', 'HSA2-F-01', 'HSA2-F-02', 'HSA2-F-03']
        if d['review_question_id'] == 'ANA-Q5':
            evidence += ['HSA019', 'HSA020', 'HSA024']
        d.update(judgment_id='ANA-H' + d['review_question_id'].split('Q')[1], evidence_ids=sorted(set(evidence)),
                 original_candidate_type=c['candidate_type'], historical_candidate_record=deepcopy(c),
                 source_artifact_hashes=dict(ana_0_2=s['receipt']['sha256'], human_decisions=sha(s['human_bytes']), researcher_request=sha(s['request_bytes'])),
                 textual_hierarchy_relation=False, candidate_parent='',
                 source_authority='RESEARCHER_SUPPLIED_NOT_COMPUTATIONALLY_INFERRED')
        out.append(d)
    return out


def provenance(s, dd):
    index = evidence_index(s)
    out = []
    for d in dd:
        targets = [(CANDIDATES, 'candidate_id', d['original_candidate_id'], 'ORIGINAL_CANDIDATE'),
                   (ADDENDUM, 'candidate_id', d['original_candidate_id'], 'EVIDENCE_ADDENDUM'),
                   (QUESTIONS, 'question_id', d['review_question_id'], 'ORIGINAL_REVIEW_QUESTION')]
        for ident in d['evidence_ids']:
            require(ident in index, 'unresolved exact evidence ID: ' + ident)
            member, key = index[ident]
            targets.append((member, key, ident, 'CANDIDATE_EVIDENCE_ONLY' if d['status'] == 'UNRESOLVED' else 'HUMAN_JUDGMENT_EVIDENCE'))
        for member, key, ident, role in targets:
            out.append(dict(judgment_id=d['judgment_id'], review_question_id=d['review_question_id'], evidence_role=role, **locate(s, member, key, ident)))
    return out


def criteria_application(s, dd):
    registry = {r['evidence_code']: r for r in rows(s['files'][REGISTRY])}
    out = []
    for d in dd:
        for code in d['criteria_codes']:
            require(code in registry, 'unknown criterion: ' + code)
            out.append(dict(review_question_id=d['review_question_id'], criterion_code=code,
                            application_role='INSUFFICIENCY' if code.startswith('N-') else 'SUPPORTS_CANDIDACY_NOT_AUTOMATIC_SUFFICIENCY',
                            relation_dimension=d['relation_dimension'], registry_record=registry[code],
                            dimension_note='Supplied judgment dimensions are not additions to the frozen registry; codes document contributions/limits, not automatic admissibility or sufficiency.',
                            methodological_notes=d['methodological_notes'], evidence_ids=d['evidence_ids'],
                            **locate(s, REGISTRY, 'evidence_code', code)))
        out.append(dict(review_question_id=d['review_question_id'], criterion_code='', application_role='METHODOLOGICAL_NOTE_NO_NEW_REGISTRY_CODE',
                        relation_dimension=d['relation_dimension'], methodological_notes=d['methodological_notes'], evidence_ids=d['evidence_ids']))
    return out


def negative_application(s, dd):
    controls = {r['control']: r for r in rows(s['files']['12_negative_controls.csv'])}
    return [dict(review_question_id=d['review_question_id'], control=key, original_record=deepcopy(controls[key]),
                 application='RETAINED_INSUFFICIENCY_NOT_AUTOMATIC_RESOLUTION',
                 **locate(s, '12_negative_controls.csv', 'control', key)) for d in dd for key in d['negative_controls']]


def crosswalk(s, dd):
    return [dict(original_candidate_id=d['original_candidate_id'], original_candidate_type=d['original_candidate_type'],
                 review_question_id=d['review_question_id'], judgment_id=d['judgment_id'],
                 candidate_status_before=d['candidate_status_before'], human_decision=d['human_decision'],
                 candidate_status_after=d['candidate_status_after'], accepted_relation_created=d['accepted_relation_created'],
                 historical_record_unchanged=True, live_candidate=d['status'] == 'UNRESOLVED',
                 refined_relation_type=d['relation_type'] if d['original_candidate_type'] != d['relation_type'] else '',
                 **locate(s, CANDIDATES, 'candidate_id', d['original_candidate_id'])) for d in dd]


def dependencies(s, dd):
    by = {d['review_question_id']: d for d in dd}
    out = []
    for seam, questions in [('SEAM_D', ['ANA-Q2', 'ANA-Q4', 'ANA-Q5']), ('SEAM_E', ['ANA-Q4', 'ANA-Q5', 'ANA-Q3'])]:
        for q in questions:
            d = by[q]
            out.append(dict(case_id=seam, review_question_id=q, judgment_id=d['judgment_id'], original_candidate_id=d['original_candidate_id'],
                            dependency_status=d['status'], dependency_type='UNRESOLVED_CANDIDATE_EVIDENCE' if d['status'] == 'UNRESOLVED' else 'ACCEPTED_HUMAN_OVERLAY_EVIDENCE',
                            resolves_parentage=False, modifies_original_case=False, candidate_parent='', **locate(s, SEAMS, 'case_id', seam)))
    return out


def integrity(s, historical):
    out = []
    for i, r in enumerate(raw_rows(s['files'][ACCOUNTING]), 1):
        current = raw_rows(historical.get(ACCOUNTING, b''))
        actual = f.rowhash(current[i-1]) if len(current) >= i else 'MISSING'
        out.append(dict(kind='FROZEN_HUMAN_JUDGMENT', identity=r['judgment_id'], expected_row_sha256=f.rowhash(r), actual_row_sha256=actual,
                        status='PASS' if actual == f.rowhash(r) else 'FAIL', **locate(s, ACCOUNTING, 'judgment_id', r['judgment_id'])))
    for name in (UNRESOLVED, SEAMS, EDGES, CANDIDATES, REGISTRY, QUESTIONS):
        actual = sha(historical.get(name, b''))
        out.append(dict(kind='FROZEN_MEMBER', identity=HISTORY + name, expected_sha256=sha(s['files'][name]), actual_sha256=actual,
                        status='PASS' if actual == sha(s['files'][name]) else 'FAIL'))
    return out


def report(m, s):
    accepted = len(m['accepted'])
    deferred = sum(d['status'] == 'UNRESOLVED' for d in m['decisions'])
    lines = ['# HSA3-ANA.0.3 — Human Adjudication Freeze', '', s['mode'], '',
             f"Researcher-supplied decisions only. Accepted judgments: {accepted}; deferred decisions: {deferred}; accepted overlays: {accepted}; new textual hierarchy relations: {len(m['hierarchy'])}.",
             'Four original candidates and all historical artifacts remain intact. ANA-C2 is a live unresolved candidate.', '',
             'Q3: lexical/participant correspondence supports candidacy. No explicit causal/fulfillment marker or demonstrated interpretive necessity establishes the proposed link. Closure context 31:40 is metadata only.',
             'HSA3 A–G parentage is unchanged. R4.4 is not started.', '']
    for d in m['decisions']:
        lines += ['## ' + d['review_question_id'] + ' — ' + d['status'], '',
                  d['relation_type'] + ' | ' + d['relation_dimension'], '',
                  'Source: ' + (d['source_ref'] or 'not a directed endpoint') + '; target: ' + (d['target_ref'] or 'not a directed endpoint') + '; scope: ' + (d['scope_ref'] or 'not a scoped role'), '',
                  d['rationale'], '', 'Explicit exclusions: ' + '; '.join(d['limitations']), '',
                  'Methodological notes: ' + ' '.join(d['methodological_notes']), '',
                  'Evidence IDs: ' + ', '.join(d['evidence_ids']), '', 'Existing criteria: ' + ', '.join(d['criteria_codes']), '']
    lines += ['## Frozen closure and controls', '',
              '31:40 → 29:1 DIRECT_LOCAL_CLOSURE; → 27:1 NO_DIRECT_RELATION; → POST_DIALOGUE_JOB TERMINATES_ENCLOSING_GROUP.',
              '3:2 remains a formal-CSF negative control; 37:24 adjacency is insufficient.',
              '32:2–5 NARRATIVE_INTRODUCTION and 32:6–37:24 ELIHU_SPEECH_SEQUENCE remain distinct.', '',
              'Criteria assignments describe the supplied reasons; they are not computed scores or automatic sufficiency. Missing concepts are methodological notes, never invented registry codes.', '']
    return '\n'.join(lines)


def seam_packet(m, s):
    lines = ['# Next HSA3 seam review packet', '',
             'PREPARATION ONLY. No A–G parentage adjudication has begun. R4.4 remains unstarted.',
             'Q2/Q4/Q5 are accepted overlay judgments. Q3 remains UNRESOLVED/HUMAN_DEFERRED and cannot resolve SEAM_E.',
             'The original cases, unresolved rows and review fields are retained below and in the nested source files.', '']
    for case in rows(s['files'][SEAMS]):
        lines += ['## ' + case['case_id'] + ' — ' + case['title'], '', case['question'], '',
                  'Primary unresolved IDs: ' + ', '.join(case['primary_unresolved_rows']), '',
                  'Participating unresolved IDs: ' + ', '.join(case['participating_unresolved_rows']), '',
                  'Original case: [' + case['case_id'] + '](' + HISTORY + SEAMS + '). Exact dependency row/hash receipts are in [06](06_hsa3_dependency_update.csv).', '']
        deps = [r for r in m['dependencies'] if r['case_id'] == case['case_id']]
        if deps:
            lines += ['| Question | Status | Evidence use | Resolves parentage |', '| --- | --- | --- | --- |']
            lines += [f"| {r['review_question_id']} | {r['dependency_status']} | {r['dependency_type']} | false |" for r in deps]
        else:
            lines += ['No new ANA decision dependency.']
        lines += ['', 'Parent candidates: ' + f.canonical(case['candidate_parents']), '', '| Review field | Historical value |', '| --- | --- |']
        lines += [f'| {k} | {case[k]} |' for k in REVIEW_FIELDS]
        lines += ['']
    return '\n'.join(lines)


def derive(s):
    dd = decisions(s)
    m = dict(decisions=dd, accepted=[deepcopy(d) for d in dd if d['accepted_relation_created']],
             provenance=provenance(s, dd), criteria=criteria_application(s, dd), negative=negative_application(s, dd),
             crosswalk=crosswalk(s, dd), dependencies=dependencies(s, dd), historical=deepcopy(s['files']),
             receipt=deepcopy(s['receipt']), hierarchy=[], r44_started=False,
             registry=deepcopy(rows(s['files'][REGISTRY])))
    m['integrity'] = integrity(s, m['historical'])
    m['report'] = report(m, s)
    m['packet'] = seam_packet(m, s)
    return m


def payload_digest(m):
    data = {k: ({n: sha(v) for n, v in value.items()} if k == 'historical' else value) for k, value in m.items() if k != 'rerun_digest'}
    return f.rowhash(data)


def build(s):
    m = derive(s)
    m['rerun_digest'] = payload_digest(derive(s))
    return m


def gates(m, s):
    expected = decisions(s)
    by = {d['review_question_id']: d for d in m['decisions']}
    exp = {d['review_question_id']: d for d in expected}
    q3 = by.get('ANA-Q3', {})
    checks = {}
    checks['VERIFIED_BASELINE'] = m['receipt'] == s['receipt'] and m['historical'] == s['files'] and all(x['valid'] for x in nested_manifests(m['historical']))
    checks['FROZEN_SOURCE_FILES'] = len(s['frozen']) == len(s['cfg']['frozen_files']) and all(r['actual'] == r['expected'] == s['cfg']['frozen_files'][r['path']] for r in s['frozen'])
    checks['HUMAN_SOURCE_EXACT'] = sha(s['human_bytes']) == s['cfg']['human_source']['sha256'] and json.loads(s['human_bytes']) == s['human'] and sha(s['request_bytes']) == s['human']['source_sha256']
    for question in ('ANA-Q2', 'ANA-Q3', 'ANA-Q4', 'ANA-Q5'):
        checks[question.replace('-', '_') + '_EXACT_DECISION'] = by.get(question) == exp[question]
    counts = s['cfg']['expected']
    checks['THREE_ACCEPTED_ONE_DEFERRED'] = len(m['decisions']) == counts['candidates'] and sum(d['status'] == 'ACCEPTED' for d in m['decisions']) == counts['accepted'] and sum(d['decision_type'] == 'HUMAN_DEFERRED' for d in m['decisions']) == counts['deferred']
    checks['ACCEPTED_OVERLAYS_ONLY'] = m['accepted'] == [d for d in expected if d['accepted_relation_created']] and len(m['accepted']) == counts['overlay']
    checks['NO_TEXTUAL_HIERARCHY'] = len(m['hierarchy']) == counts['hierarchy'] and all(d.get('textual_hierarchy_relation') is False and not d.get('candidate_parent') for d in m['decisions'] + m['accepted'])
    checks['FOUR_CANDIDATES_PRESERVED'] = m['historical'].get(CANDIDATES) == s['files'][CANDIDATES] and len(m['crosswalk']) == counts['candidates'] and {r['original_candidate_id'] for r in m['crosswalk']} == {r['original_candidate_id'] for r in expected}
    checks['C2_LIVE_UNRESOLVED_NOT_ACCEPTED'] = any(r['original_candidate_id'] == 'ANA-C2' and r['live_candidate'] is True and r['candidate_status_after'] == 'UNRESOLVED' and r['accepted_relation_created'] is False for r in m['crosswalk']) and not any(d['original_candidate_id'] == 'ANA-C2' for d in m['accepted']) and q3.get('decision_type') == 'HUMAN_DEFERRED'
    checks['NO_CAUSAL_OR_FULFILLMENT_ASSERTION'] = all(d.get('causal_link_asserted') is False and d.get('fulfillment_asserted') is False for d in m['decisions'] + m['accepted']) and q3.get('closure_context_use') == 'CONTEXTUAL_METADATA_ONLY_NOT_CAUSAL_LINK' and m['report'] == report(m, s)
    checks['Q3_POSITIVE_AND_INSUFFICIENT_EVIDENCE'] = q3.get('evidence_ids') == exp['ANA-Q3']['evidence_ids'] and bool(q3.get('evidence_ids')) and q3.get('methodological_notes') == exp['ANA-Q3']['methodological_notes'] and q3.get('rationale') == exp['ANA-Q3']['rationale'] and q3.get('criteria_codes') == exp['ANA-Q3']['criteria_codes']
    for gate, member in [('FROZEN_59_UNCHANGED', ACCOUNTING), ('UNRESOLVED_57_UNCHANGED', UNRESOLVED), ('HSA3_AG_UNCHANGED', SEAMS), ('HSA2_F_CLOSURE_UNCHANGED', EDGES)]:
        checks[gate] = m['historical'].get(member) == s['files'][member]
    checks['REGISTRY_UNCHANGED_EXISTING_CODES_ONLY'] = m['registry'] == rows(s['files'][REGISTRY]) and all(code in {r['evidence_code'] for r in m['registry']} for d in m['decisions'] for code in d['criteria_codes'])
    checks['CRITERIA_APPLICATION_FAITHFUL'] = m['criteria'] == criteria_application(s, expected)
    checks['NEGATIVE_CONTROLS_RETAINED'] = m['negative'] == negative_application(s, expected) and all(r['original_record']['status'] == 'PASS' for r in m['negative'])
    checks['EXACT_ID_ROW_PROVENANCE'] = m['provenance'] == provenance(s, expected)
    checks['CANDIDATE_JUDGMENT_CROSSWALK'] = m['crosswalk'] == crosswalk(s, expected)
    checks['DEPENDENCIES_ONLY_NO_PARENTAGE'] = m['dependencies'] == dependencies(s, expected)
    checks['INTEGRITY_RECEIPTS_COMPUTED'] = m['integrity'] == integrity(s, m['historical']) and all(r['status'] == 'PASS' for r in m['integrity'])
    checks['NO_R4_4'] = m['r44_started'] is False
    checks['HUMAN_REPORT_FAITHFUL'] = m['report'] == report(dict(m, decisions=expected), s)
    checks['SEAM_PACKET_UNADJUDICATED'] = m['packet'] == seam_packet(dict(m, dependencies=dependencies(s, expected)), s)
    checks['DETERMINISTIC_RERUN'] = m['rerun_digest'] == payload_digest(m)
    return [dict(gate=k, status='PASS' if ok else 'FAIL') for k, ok in checks.items()]


def serialize(m, s):
    gg = gates(m, s)
    require(all(g['status'] == 'PASS' for g in gg), f.canonical([g for g in gg if g['status'] == 'FAIL']))
    files = {HISTORY + k: v for k, v in m['historical'].items()}
    for name, key in [('01_ana_human_adjudications.csv', 'decisions'), ('02_ana_human_relation_provenance.csv', 'provenance'),
                      ('03_ana_criteria_application.csv', 'criteria'), ('04_ana_negative_control_application.csv', 'negative'),
                      ('05_ana_candidate_to_judgment_crosswalk.csv', 'crosswalk'), ('06_hsa3_dependency_update.csv', 'dependencies'),
                      ('07_frozen_judgment_integrity.csv', 'integrity'), ('11_accepted_overlay_relations.csv', 'accepted')]:
        files[name] = util.csv_bytes(m[key])
    files['08_ana_0_3_adjudication_report.md'] = m['report'].encode('utf-8')
    files['09_next_hsa3_seam_review_packet.md'] = m['packet'].encode('utf-8')
    files['12_researcher_supplied_decisions.json'] = s['human_bytes']
    files['13_researcher_source.txt'] = s['request_bytes']
    meta = dict(version='HSA3-ANA.0.3', mode=s['mode'], status='PASS', gate_count=len(gg)+1,
                baseline_commit=s['cfg']['baseline_commit'], baseline_receipt=m['receipt'], frozen_receipts=s['frozen'],
                counts=dict(accepted_human_judgments=len(m['accepted']), deferred_human_decisions=sum(d['status'] == 'UNRESOLVED' for d in m['decisions']),
                            accepted_overlay_relations=len(m['accepted']), textual_hierarchy_relations=len(m['hierarchy']), historical_candidates=len(m['crosswalk']),
                            frozen_human=len(rows(s['files'][ACCOUNTING])), unresolved=len(rows(s['files'][UNRESOLVED])), seams=len(rows(s['files'][SEAMS]))),
                code_sha256=sha(Path(__file__).read_bytes()), config_sha256=sha(CONFIG.read_bytes()), human_decisions_sha256=sha(s['human_bytes']),
                researcher_source_sha256=sha(s['request_bytes']), rerun_payload_sha256=m['rerun_digest'],
                rerun_scope='TWO_INDEPENDENT_MODEL_BUILDS; independent-process ZIP comparison recorded in validation',
                bhsa_extraction_performed=False, r44_started=m['r44_started'],
                claim='RESEARCHER_SUPPLIED_OVERLAY_DECISIONS_ONLY; Q3 DEFERRED; NO A-G PARENTAGE ADJUDICATION')
    files['90_run_metadata.json'] = util.json_bytes(meta)
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
    parser.add_argument('--archive', help='Exact pinned ANA.0.2 ZIP, optional path override; SHA remains mandatory')
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args(argv)
    require(not (args.self_test and args.archive), '--archive cannot be combined with --self-test')
    s = load(args.self_test, args.archive)
    files = serialize(build(s), s)
    require(f.a.prep.r43.frozen_receipts(s['cfg']) == s['frozen'], 'frozen files changed during run')
    require((ROOT / s['cfg']['human_source']['path']).read_bytes() == s['human_bytes'], 'human input changed during run')
    require((ROOT / s['human']['source_path']).read_bytes() == s['request_bytes'], 'researcher source changed during run')
    if not args.self_test:
        require(sha((Path(args.archive) if args.archive else ROOT / s['cfg']['archive']['path']).read_bytes()) == s['receipt']['sha256'], 'archive changed during run')
    f.a.prep.publish(files, args.out)
    out = Path(args.out).resolve()
    zp = out.with_name(out.name + '_results.zip')
    out.with_name(out.name + '_run.log').write_text('HSA3-ANA.0.3 PASS\n' + s['mode'] + '\nZIP SHA256 ' + sha(zp.read_bytes()) + '\n', encoding='utf-8')
    print('HSA3-ANA.0.3 PASS ' + str(zp) + ' SHA256 ' + sha(zp.read_bytes()))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, KeyError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
