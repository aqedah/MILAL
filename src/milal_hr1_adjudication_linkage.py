"""HR1: explicit linkage of committed human judgments to immutable review artifacts."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import subprocess
import zipfile

import milal_r3c_3_signature_context as frozen
import milal_prov1_signature_provenance as prov

csv.field_size_limit(64 * 1024 * 1024)
VERSION = 'HR1'
NA = 'NOT_AVAILABLE_FROM_SOURCE'
HUMAN_FIELDS = ('form_assessment',) + tuple(frozen.REVIEW_FIELDS)
COMMIT = 'a1e2b99b6fb70a56ccd4ba7230998bae69031dc0'
HUMAN_PATH = 'docs/HUMAN_REVIEW_PILOT_ADJUDICATION.csv'
EXPECTED = {
    'human': '4fb8c15a9ae530e778122f97c3ffcdcc78ded89f534535e4c7afe5cb2272abe3',
    'r3c3': '5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981',
    'prov1': '38c6703721e2f9cca590ab96d64d7a2860a3d075e059cabeb2abe9eb6708c482',
}
CASE_IDS = tuple(f'CASE{i:03d}' for i in range(1, 31))
SEQUENCE_CASES = tuple(f'CASE{i:03d}' for i in range(7, 13))
TABLES = {
    'cases': ('r3c3', '02_review_cases.csv', ('case_id', 'case_type', 'unit_id', 'unit_type', 'target_summaries', 'boundary_ref')),
    'bundles': ('r3c3', '03_bundle_definition_context.csv', ('bundle_id', 'source_rows')),
    'singles': ('r3c3', '05_singleton_definition_context.csv', ('unit_id', 'source_rows')),
    'boundary': ('r3c3', '07_boundary_definition_context.csv', ('case_id', 'unit_ids')),
    'families': ('prov1', '02_family_signature_provenance.csv', ('family_id', 'bundle_ids', 'positions', 'occurrences', 'historical_hash')),
    'deltas': ('prov1', '03_refinement_feature_delta.csv', ('parent_family_id', 'child_family_id', 'source', 'historical_hash')),
    'items': ('prov1', '04_singleton_signature_provenance.csv', ('atom_node', 'review_item_ids', 'first_unique_level', 'atom_hashes')),
    'crosswalk': ('prov1', '05_downstream_identity_links.csv', ('link_type', 'source', 'layer', 'case_id', 'review_unit_id')),
}
OUTPUTS = {
    'cases': '01_case_adjudication_links.csv',
    'evidence': '02_case_evidence_locators.csv',
    'provenance': '03_case_provenance_locators.csv',
    'extensions': '04_extension_dependency_links.csv',
    'boundary': '05_boundary_review_links.csv',
    'summary': '06_adjudication_summary.csv',
}


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def read_csv(blob, required=()):
    reader = csv.DictReader(io.StringIO(blob.decode('utf-8-sig'), newline=''))
    fields = reader.fieldnames or []
    if len(fields) != len(set(fields)) or not set(required) <= set(fields):
        raise ValueError('Missing/duplicate exact source columns')
    rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('Malformed source CSV row')
    return rows


def read_zip(blob):
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        if len(set(names)) != len(names) or any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n or ':' in n for n in names):
            raise ValueError('Unsafe/duplicate archive locator')
        if z.testzip() is not None:
            raise ValueError('Source ZIP CRC failure')
        archive = {'files': {n: z.read(n) for n in names}, 'sha256': sha(blob)}
    if not frozen.manifest_valid(archive):
        raise ValueError('Source manifest failure')
    return archive


def load(r3c3, prov1, adjudication, repo):
    paths = {'r3c3': Path(r3c3), 'prov1': Path(prov1), 'human': Path(adjudication)}
    blobs = {k: p.read_bytes() for k, p in paths.items()}
    if {k: sha(b) for k, b in blobs.items()} != EXPECTED:
        raise ValueError('Source SHA256 failure')
    committed = subprocess.run(['git', 'show', f'{COMMIT}:{HUMAN_PATH}'], cwd=repo,
                               check=True, capture_output=True).stdout
    if committed != blobs['human']:
        raise ValueError('Adjudication differs from committed human source')
    return {'blobs': blobs, 'expected_hashes': dict(EXPECTED), 'committed_human': committed,
            'source_commit': COMMIT, 'expected_commit': COMMIT, 'mode': 'ACCEPTED_REAL',
            'paths': {k: str(p.resolve()) for k, p in paths.items()}}


def parse(source):
    if {k: sha(b) for k, b in source['blobs'].items()} != source['expected_hashes']:
        raise ValueError('Source SHA256 failure')
    if source['committed_human'] != source['blobs']['human'] or source['source_commit'] != source['expected_commit']:
        raise ValueError('Adjudication source commit failure')
    human = read_csv(source['blobs']['human'], ('case_id', 'case_type') + HUMAN_FIELDS)
    archives = {k: read_zip(source['blobs'][k]) for k in ('r3c3', 'prov1')}
    meta = {k: frozen.source_metadata(a) for k, a in archives.items()}
    if meta['prov1'].get('input_sha256', {}).get('c3') != archives['r3c3']['sha256']:
        raise ValueError('PROV1 to R3c.3 source chain failure')
    if meta['r3c3'].get('version') != 'R3c.3' or meta['prov1'].get('version') != 'PROV1':
        raise ValueError('Unexpected source version')
    for role, name in [('r3c3', '10_gates.csv'), ('prov1', '09_gates.csv')]:
        gates = frozen.rows(archives[role], name)
        if not gates or any(r['status'] != 'PASS' for r in gates) or len(gates) != meta[role].get('gate_count'):
            raise ValueError('Accepted source gates inconsistent')
    tables, members = {}, {}
    for key, (role, name, columns) in TABLES.items():
        members[key] = frozen.member(archives[role], name)
        tables[key] = read_csv(archives[role]['files'][members[key]], columns)
    return human, archives, tables, members, meta


def single_index(rows, key):
    result = {}
    for i, row in enumerate(rows):
        if not row[key] or row[key] in result:
            raise ValueError('Ambiguous/blank identity: ' + key)
        result[row[key]] = (i, row)
    return result


def derive(source):
    human, archives, t, members, meta = parse(source)
    hi = single_index(human, 'case_id')
    ci = single_index(t['cases'], 'case_id')
    if tuple(hi) != CASE_IDS or set(ci) != set(CASE_IDS):
        raise ValueError('Unresolved case identity: require exact CASE001–030')
    bi = single_index(t['bundles'], 'bundle_id')
    si = single_index(t['singles'], 'unit_id')
    boundaries = single_index(t['boundary'], 'case_id')
    single_index(t['families'], 'family_id')
    single_index(t['items'], 'atom_node')
    # Archive bytes are immutable within this derivation. Fingerprint each member
    # once; recomputing a multi-megabyte table for every locator is quadratic.
    member_hashes = {key: sha(archives[TABLES[key][0]]['files'][name])
                     for key, name in members.items()}

    def locator(table, index):
        role = TABLES[table][0]
        name = members[table]
        return {'archive_role': role, 'archive_sha256': archives[role]['sha256'],
                'member': name, 'member_sha256': member_hashes[table],
                'data_row': index + 1, 'row_sha256': sha(canonical(t[table][index]).encode('utf-8'))}

    def human_locator(index):
        return {'source_commit': source['source_commit'], 'member': HUMAN_PATH,
                'file_sha256': sha(source['blobs']['human']), 'data_row': index + 1,
                'row_sha256': sha(canonical(human[index]).encode('utf-8'))}

    # Decode and index explicit foreign keys. No text/verse or ID-prefix matching.
    review = {}
    by_unit = defaultdict(list)
    overlays = []
    identity_rows = defaultdict(list)
    for i, r in enumerate(t['crosswalk']):
        if r['link_type'] == 'review_unit':
            key = (r['case_id'], r['review_unit_id'])
            if key in review:
                raise ValueError('Ambiguous PROV1 review-unit locator')
            review[key] = (i, r)
        elif r['link_type'] == 'review_unit_source':
            by_unit[r['review_unit_id']].append((i, r))
        elif r['link_type'] == 'overlay':
            overlays.append((i, r, json.loads(r['source'])['source_row']))
        elif r['link_type'] in ('lineages', 'members', 'singleton_links', 'items'):
            sr = json.loads(r['source'])['source_row']
            for field in ('bundle_id', 'review_item_id'):
                if sr.get(field): identity_rows[(field, sr[field])].append(i)
    fams = defaultdict(list)
    for i, f in enumerate(t['families']):
        for bid in json.loads(f['bundle_ids']):
            if bid != NA: fams[bid].append((i, f))
    items = {}
    for i, r in enumerate(t['items']):
        for rid in json.loads(r['review_item_ids']):
            if rid == NA: continue
            if rid in items: raise ValueError('Ambiguous singleton item locator')
            items[rid] = (i, r)
    event_key = ('parent_family_id', 'child_level', 'child_signature_hash', 'exemplar_window_id')
    deltas = {}
    for i, r in enumerate(t['deltas']):
        sr = json.loads(r['source'])['source_row']
        key = tuple(sr[k] for k in event_key)
        if key in deltas: raise ValueError('Ambiguous refinement provenance locator')
        deltas[key] = (i, r)
    cases, evidence, provenance, panels = [], [], [], []
    bundle_cases = defaultdict(set)
    used_review_keys = set()

    def add(target, cid, uid, role, loc):
        target.append({'case_id': cid, 'review_unit_id': uid, 'relationship': role,
                       'link_status': 'EXPLICIT_SOURCE', 'locator': loc})

    for cid, (human_i, h) in hi.items():
        case_i, c = ci[cid]
        if c['case_type'] != h['case_type']:
            raise ValueError('Case type differs from human source: ' + cid)
        summaries = json.loads(c['target_summaries'])
        if not summaries or len({s['unit_id'] for s in summaries}) != len(summaries):
            raise ValueError('Unresolved/ambiguous target summary: ' + cid)
        if c['unit_id']:
            if [s['unit_id'] for s in summaries] != [c['unit_id']]:
                raise ValueError('Case target identity mutation')
        else:
            if cid not in boundaries or set(json.loads(boundaries[cid][1]['unit_ids'])) != {s['unit_id'] for s in summaries}:
                raise ValueError('Boundary multiplicity mismatch')
            panel_i, panel = boundaries[cid]
            add(evidence, cid, NA, 'BOUNDARY_PANEL', locator('boundary', panel_i))
            panels.append({'case_id': cid, 'boundary_identity': {'case_id': cid, 'boundary_ref': c['boundary_ref']},
                           'participating_unit_ids': json.loads(panel['unit_ids']), 'locator': locator('boundary', panel_i),
                           'human_adjudication_locator': human_locator(human_i)})
        objects = []
        for summary in summaries:
            uid = summary['unit_id']
            key = (cid, uid)
            if key not in review: raise ValueError('Unresolved PROV1 case/unit link: ' + str(key))
            used_review_keys.add(key)
            pi, pr = review[key]
            if json.loads(pr['summary']) != summary:
                raise ValueError('PROV1 target summary identity mismatch')
            anchor = json.loads(pr['source'])
            if anchor['archive_sha256'] != archives['r3c3']['sha256'] or anchor['member'] != members['cases'] or int(anchor['data_row']) != case_i + 1 or anchor['source_row'] != c:
                raise ValueError('PROV1 source locator disagrees with R3c.3')
            add(evidence, cid, uid, 'CASE_TARGET_SUMMARY', dict(locator('cases', case_i), summary_index=summaries.index(summary)))
            add(provenance, cid, uid, 'REVIEW_UNIT_CROSSWALK', locator('crosswalk', pi))
            bid, rid = summary.get('bundle_id', ''), summary.get('review_item_id', '')
            obj = {'review_unit_id': uid, 'review_unit_type': summary.get('unit_type') or c['unit_type'] or NA,
                   'bundle_id': bid or NA, 'review_item_id': rid or NA, 'lineage_id': summary.get('lineage_id') or NA,
                   'family_ids': [], 'atom_node': NA, 'r3c3_summary': copy.deepcopy(summary)}
            if bid:
                if bid not in bi or not fams[bid]: raise ValueError('Unresolved bundle provenance: ' + bid)
                bundle_cases[bid].add(cid)
                add(evidence, cid, uid, 'BUNDLE_DEFINITION', locator('bundles', bi[bid][0]))
                for fi, f in fams[bid]:
                    obj['family_ids'].append(f['family_id'])
                    add(provenance, cid, uid, 'FAMILY_SIGNATURE', locator('families', fi))
                for xi in identity_rows[('bundle_id', bid)]:
                    add(provenance, cid, uid, 'EXPLICIT_IDENTITY_RELATION', locator('crosswalk', xi))
            else:
                if uid not in si: raise ValueError('Unresolved singleton review identity')
                add(evidence, cid, uid, 'SINGLETON_DEFINITION', locator('singles', si[uid][0]))
                if rid:
                    if rid not in items: raise ValueError('Unresolved G6 singleton provenance')
                    ii, item = items[rid]; obj['atom_node'] = item['atom_node']
                    add(provenance, cid, uid, 'SINGLETON_ATOM_PROVENANCE', locator('items', ii))
                    for xi in identity_rows[('review_item_id', rid)]:
                        add(provenance, cid, uid, 'EXPLICIT_IDENTITY_RELATION', locator('crosswalk', xi))
                refs = json.loads(si[uid][1]['source_rows'])
                matched_event = False
                for ref in refs:
                    sr = ref['row']
                    if set(event_key) <= set(sr):
                        k = tuple(sr[f] for f in event_key)
                        if k not in deltas: raise ValueError('Unresolved explicit refinement provenance')
                        di, delta = deltas[k]; matched_event = True
                        obj['family_ids'].append(delta['parent_family_id'])
                        add(provenance, cid, uid, 'SINGLETON_REFINEMENT_EVENT', locator('deltas', di))
                if not rid and not matched_event: raise ValueError('Unresolved event-only identity')
                if not by_unit[uid]: raise ValueError('Missing explicit review-unit source links')
                if {canonical(ref) for ref in refs} != {canonical(json.loads(xr['upstream_source'])) for _, xr in by_unit[uid]}:
                    raise ValueError('Incomplete explicit review-unit source links')
                for xi, xr in by_unit[uid]:
                    if json.loads(xr['upstream_source']) not in refs:
                        raise ValueError('Review-unit source not present in R3c.3')
                    add(provenance, cid, uid, 'REVIEW_UNIT_SOURCE', locator('crosswalk', xi))
            obj['family_ids'] = sorted(set(obj['family_ids'])) or [NA]
            objects.append(obj)
        cases.append(dict(copy.deepcopy(h), review_unit_id=c['unit_id'] or NA,
                          review_unit_type=c['unit_type'] or NA,
                          boundary_identity={'case_id': cid, 'boundary_ref': c['boundary_ref']} if not c['unit_id'] else NA,
                          target_objects=objects, human_adjudication_locator=human_locator(human_i),
                          r3c3_case_locator=locator('cases', case_i),
                          extension_dependency_cases=list(SEQUENCE_CASES) if cid in SEQUENCE_CASES else [],
                          extension_dependency_note=hi['CASE012'][1]['reviewer_notes'] if cid in SEQUENCE_CASES else ''))
    if used_review_keys != set(review):
        raise ValueError('PROV1 contains unmatched expected case/unit links')
    extensions = []
    for i, original, row in overlays:
        if original['layer'] != 'SEQUENCE_EXTENSION_OVERLAY_ONLY':
            raise ValueError('Extension source is not overlay-only')
        extensions.append({'layer': 'SEQUENCE_EXTENSION_OVERLAY_ONLY', 'source_relation': copy.deepcopy(row),
                           'short_case_ids': sorted(bundle_cases[row['short_bundle_id']]),
                           'long_case_ids': sorted(bundle_cases[row['long_bundle_id']]),
                           'locator': locator('crosswalk', i),
                           'independent_evidence_warning_source': human_locator(hi['CASE010'][0])})
    summary = []
    for field, labels in [('form_assessment', ('CLEAR', 'PARTIAL', 'INSUFFICIENT')), ('sufficient_context', ('YES', 'PARTIAL', 'NO'))]:
        counts = Counter(h[field] for h in human)
        summary += [{'human_field': field, 'human_value': label, 'case_count': counts[label],
                     'source': 'human researcher adjudication'} for label in labels]
    return {'cases': cases, 'evidence': evidence, 'provenance': provenance, 'extensions': extensions,
            'boundary': panels, 'summary': summary, 'source_metadata': meta,
            'mode': source['mode'], 'unresolved_links': [], 'ambiguous_links': []}


def render(model):
    lines = ['# HR1 — Human review pilot linkage', '', 'Mode: ' + model['mode'],
             'Human judgments are copied from the committed CSV, not generated by HR1.',
             'Locators refer to immutable source ZIPs; no historical output is written back.', '']
    for c in model['cases']:
        lines += ['## ' + c['case_id'], '', 'Case type: ' + c['case_type'],
                  'Explicit target identities: `' + canonical(c['target_objects']) + '`',
                  f"form_assessment: {c['form_assessment']}; sufficient_context: {c['sufficient_context']}; review_status: {c['review_status']}",
                  'review_time_seconds: blank (not measured)', '', 'Human researcher notes (verbatim):', '']
        lines += ['> ' + line for line in c['reviewer_notes'].split('\n')]
        lines += ['', 'Full human row and all remaining judgment fields: 01_case_adjudication_links.csv.',
                  'Evidence/provenance row locators: 02_case_evidence_locators.csv and 03_case_provenance_locators.csv.', '']
        if c['extension_dependency_cases']:
            lines += ['Human-authored dependency: CASE007–CASE012 are extended views of one repeated sequence, not six independent evidences.',
                      'Explicit sequence-extension relations remain overlay-only in 04_extension_dependency_links.csv; genealogy is unchanged.', '']
    return '\n'.join(lines) + '\n'


def acceptance(model):
    by = {c['case_id']: c for c in model['cases']}
    lines = ['# R3 human-review pilot — HR1 acceptance record', '', 'Mode: ' + model['mode'], '',
             'Question: Can a human researcher inspect MILAL review objects, recover their explicit linguistic basis, distinguish clear/partial/insufficient coherence, and avoid automatic overinterpretation?', '',
             'Technical conclusion: the recorded pilot supports readiness to close this human-review linkage step, provided all HR1 integrity gates pass. This is a bounded qualitative conclusion, not a score, universal validation of every family, or authorization to begin R4.', '',
             'The researcher distinguished reproducibility from recognizable form (CASE001/004/006/016), recognized extended sequences (CASE007–012), and retained uncertainty about the significance of singleton rarity (CASE021/022/024). These distinctions, rather than an invented numerical cutoff, support the conclusion.', '',
             '| Human field | Value | Cases |', '|---|---|---:|']
    lines += [f"| {r['human_field']} | {r['human_value']} | {r['case_count']} |" for r in model['summary']]
    lines += ['', 'Time was not measured. No automated score or new analytical label is assigned.',
              'Computational grouping, formal recognition and structural significance remain separate. Singleton uniqueness is not structural importance.',
              'CASE007–012 form one human-recognized extension series; do not count six independent structural evidences. Extension remains separate from refinement genealogy.', '']
    for cid in ('CASE001', 'CASE004', 'CASE006', 'CASE016', 'CASE010', 'CASE012', 'CASE021', 'CASE022', 'CASE024', 'CASE028', 'CASE029'):
        lines += ['## ' + cid + ' — recorded human qualification', '']
        lines += ['> ' + line for line in by[cid]['reviewer_notes'].split('\n')]
        lines += ['']
    lines += ['Boundary adjacency does not itself establish direct Elihu→YHWH discourse continuity. The recorded CASE029 judgment explicitly identifies Job as the addressee in `ויען יהוה את־איוב`.',
              'Final methodological closure remains the researcher’s decision. HR1 preserves the judgments and their source links; it does not revise them or begin R3c.4/R4.', '']
    return '\n'.join(lines)


def dependency_connected(model):
    graph = defaultdict(set)
    for r in model['extensions']:
        for a in r['short_case_ids']:
            for b in r['long_case_ids']:
                if a in SEQUENCE_CASES and b in SEQUENCE_CASES:
                    graph[a].add(b); graph[b].add(a)
    reached, queue = set(), [SEQUENCE_CASES[0]]
    while queue:
        n = queue.pop()
        if n not in reached:
            reached.add(n); queue.extend(graph[n] - reached)
    return set(SEQUENCE_CASES) <= reached


def gates(model):
    source = model['source']
    expected = derive(source)
    equal = lambda k: canonical(model[k]) == canonical(expected[k])
    human = read_csv(source['blobs']['human'])
    by = {r['case_id']: r for r in human}
    actual_by = {r['case_id']: r for r in model['cases']}
    def caution(cid):
        note = by[cid]['reviewer_notes']
        return cid in actual_by and actual_by[cid]['reviewer_notes'] == note and all(
            '> ' + line in model['report'] and '> ' + line in model['acceptance'] for line in note.split('\n'))
    checks = {
        'HUMAN_SOURCE_COMMIT_VERIFIED': source['blobs']['human'] == source['committed_human'] and source['source_commit'] == source['expected_commit'] and sha(source['blobs']['human']) == source['expected_hashes']['human'],
        'EXACTLY_30_ADJUDICATION_ROWS': len(model['cases']) == len(human) == 30,
        'CASE_IDS_COMPLETE_UNIQUE': Counter(c['case_id'] for c in model['cases']) == Counter(CASE_IDS),
        'ALL_R3C3_CASES_RESOLVED': equal('cases') and equal('evidence') and not model['unresolved_links'],
        'ALL_EXPLICIT_PROV1_LINKS_RESOLVED': equal('provenance') and not model['unresolved_links'],
        'NO_FUZZY_LINKAGE': equal('evidence') and equal('provenance') and not model['ambiguous_links'],
        'HUMAN_FIELDS_EQUIVALENT': all(c['case_id'] in by and all(c[f] == by[c['case_id']][f] for f in HUMAN_FIELDS) for c in model['cases']) and len(model['cases']) == len(human),
        'FORM_COUNTS_EXACT': Counter(c['form_assessment'] for c in model['cases']) == Counter({'CLEAR':21,'PARTIAL':5,'INSUFFICIENT':4}) and equal('summary'),
        'CONTEXT_COUNTS_EXACT': Counter(c['sufficient_context'] for c in model['cases']) == Counter({'YES':26,'PARTIAL':4}) and equal('summary'),
        'ALL_REVIEWED': len(model['cases']) == 30 and all(c['review_status'] == 'REVIEWED' for c in model['cases']),
        'TIME_UNMEASURED_BLANK': len(model['cases']) == 30 and all(c['review_time_seconds'] == '' for c in model['cases']),
        'EXTENSION_DEPENDENCY_PRESERVED': equal('extensions') and dependency_connected(model) and all(c['extension_dependency_cases'] == list(SEQUENCE_CASES) for c in model['cases'] if c['case_id'] in SEQUENCE_CASES),
        'CASE028_CONTINUITY_CAUTION': caution('CASE028'),
        'CASE029_JOB_ADDRESSEE_CAUTION': caution('CASE029'),
        'BOUNDARY_MULTIPLICITY_PRESERVED': equal('boundary'),
        'SINGLETON_IDENTITIES_PRESERVED': [c for c in model['cases'] if c['case_type'] == 'SINGLETON_OUTCOME'] == [c for c in expected['cases'] if c['case_type'] == 'SINGLETON_OUTCOME'],
        'HISTORICAL_HASHES_UNCHANGED': equal('evidence') and equal('provenance') and equal('source_metadata'),
        'HISTORICAL_IDS_UNCHANGED': equal('cases') and equal('boundary'),
        'MEMBERSHIP_GENEALOGY_UNCHANGED': equal('evidence') and equal('provenance') and equal('extensions'),
        'SOURCE_ZIP_INTEGRITY': all(sha(source['blobs'][k]) == source['expected_hashes'][k] and read_zip(source['blobs'][k]) for k in ('r3c3','prov1')),
        'REPORTS_TRACE_TO_HUMAN_SOURCE': model['report'] == render(expected) and model['acceptance'] == acceptance(expected),
    }
    return [{'gate_id': k, 'status': 'PASS' if v else 'FAIL'} for k, v in checks.items()]


def build(source):
    model = dict(source=source, **derive(source))
    model['report'] = render(model)
    model['acceptance'] = acceptance(model)
    return model


def serialize(model):
    checks = gates(model)
    if any(r['status'] != 'PASS' for r in checks):
        raise ValueError('HR1 gate failure: ' + canonical(checks))
    files = {name: prov.csv_bytes(model[key]) for key, name in OUTPUTS.items()}
    files['07_human_review_pilot_report.md'] = model['report'].encode('utf-8')
    files['08_r3_human_review_acceptance.md'] = model['acceptance'].encode('utf-8')
    meta = {'version': VERSION, 'mode': model['mode'], 'adjudication_commit': model['source']['source_commit'],
            'input_sha256': {k:sha(v) for k,v in model['source']['blobs'].items()},
            'source_metadata': model['source_metadata'], 'counts': {k:len(model[k]) for k in OUTPUTS},
            'gate_count': len(checks)+1, 'unresolved_links': len(model['unresolved_links']),
            'ambiguous_links': len(model['ambiguous_links']), 'human_judgment_source':'committed human CSV only',
            'fuzzy_linkage':False, 'analytical_outputs_modified':False}
    files['90_run_metadata.json'] = (canonical(meta)+'\n').encode('utf-8')
    files['09_gates.csv'] = prov.csv_bytes(checks)
    prov.add_manifest(files)
    final_gate = prov.manifest_gate(files)
    if final_gate['status'] != 'PASS': raise ValueError('Result manifest failure')
    checks.append(final_gate); files['09_gates.csv'] = prov.csv_bytes(checks); prov.add_manifest(files)
    if not prov.manifest_ok(files): raise ValueError('Result manifest failure')
    return files


def write(model, output):
    out = Path(output).resolve()
    target_zip = out.with_name(out.name+'_results.zip')
    log = out.with_name(out.name+'_run.log')
    if any(p.exists() for p in (out,target_zip,log)):
        raise FileExistsError('Fresh output directory, ZIP and log required')
    files = serialize(model)
    out.mkdir(parents=True, exist_ok=False)
    for name, blob in files.items(): (out/name).write_bytes(blob)
    with zipfile.ZipFile(target_zip,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for name,blob in sorted(files.items()):z.writestr(out.name+'/'+name,blob)
    verified = read_zip(target_zip.read_bytes())
    if {PurePosixPath(n).name:b for n,b in verified['files'].items()} != files:
        raise ValueError('Result ZIP bytes differ from intended output')
    if {p.name:p.read_bytes() for p in out.iterdir()} != files:
        raise ValueError('Result files changed while writing')
    for k,path in model['source'].get('paths',{}).items():
        if Path(path).read_bytes() != model['source']['blobs'][k]:
            raise ValueError('Historical source changed during execution')
    log.write_text(canonical({'version':VERSION,'exit_code':0,'gate_count':22,
                              'zip_sha256':sha(target_zip.read_bytes()),'zip_crc':'PASS','manifest':'PASS',
                              'metadata':json.loads(files['90_run_metadata.json'])})+'\n',encoding='utf-8')
    return target_zip, log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--r3c3-zip',type=Path)
    parser.add_argument('--prov1-zip',type=Path)
    parser.add_argument('--adjudication',type=Path,default=Path(__file__).resolve().parents[1]/HUMAN_PATH)
    parser.add_argument('--output-dir',type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        from milal_hr1_synthetic import source_fixture
        model = build(source_fixture())
        if args.output_dir: print(*write(model,args.output_dir),sep='\n')
        else: serialize(model)
        print('HR1 synthetic self-test: 22/22 gates PASS')
        return 0
    if not args.r3c3_zip or not args.prov1_zip or not args.output_dir:
        parser.error('Two frozen ZIPs and --output-dir required')
    source = load(args.r3c3_zip,args.prov1_zip,args.adjudication,Path(__file__).resolve().parents[1])
    print(*write(build(source),args.output_dir),sep='\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
