"""Audit a human-authored structural registry; never detect boundaries or infer parents."""
from __future__ import annotations

import argparse
from copy import deepcopy
import csv
import json
from pathlib import Path
import sys
import zipfile

import milal_r4_0_sources as src
import milal_mr1_surface_marker_provenance as util

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/hsa1_job.json'
CSV = ROOT / 'docs/HUMAN_STRUCTURAL_ADJUDICATION.csv'
MD = ROOT / 'docs/HUMAN_STRUCTURAL_ADJUDICATION.md'
FIELDS = ('judgment_id reference_start reference_end primary_anchor_atom_if_known '
          'judgment_type structural_function hierarchy_relation related_reference '
          'related_judgment_id_if_available linguistic_basis source_evidence_ids '
          'source_layers methodological_note review_status reviewer_notes').split()
FUNCTIONS = set(('INTERNAL_TRANSITION SPEECH_UNIT_ONSET SPEECH_UNIT_END PARALLEL_ENDING '
                 'NARRATIVE_INTRODUCTION SCENE_ONSET PARAGRAPH_ONSET TRANSITION_COMPONENT '
                 'INTERNAL_SPEECH_ONSET NO_BOUNDARY').split())
RELATIONS = set('SAME_LEVEL_SIBLING CHILD_OF HIERARCHICALLY_ABOVE CONTINUES_WITHIN PARALLEL_TO UNRESOLVED'.split())
sha, canonical = util.sha, util.canonical


def require(ok, message):
    if not ok:
        raise ValueError('HSA1 STOP: ' + message)


def read_csv(blob):
    csv.field_size_limit(16 * 1024 * 1024)
    return util.read_csv(blob)[0]


def jlist(value):
    result = json.loads(value)
    require(isinstance(result, list), 'expected JSON list')
    return result


def registry():
    rows = read_csv(CSV.read_bytes())
    require(rows and all(set(r) == set(FIELDS) for r in rows), 'registry schema')
    return rows


def registry_bytes(rows):
    """Match the repository's *.csv text eol=lf contract, including after checkout."""
    return util.csv_bytes(rows, FIELDS).replace(b'\r\n', b'\n')


def markdown_table(rows):
    """Exact human fields, including evidence IDs; used only to check the authored MD."""
    escape = lambda v: str(v).replace('|', '&#124;').replace('\n', '<br>')
    lines = []
    for r in rows:
        lines += ['### ' + r['judgment_id'] + ' — Job ' + r['reference_start'], '',
                  '| Field | Human-authored value |', '| --- | --- |']
        lines += ['| ' + k + ' | ' + escape(r[k]) + ' |' for k in FIELDS]
        lines += ['']
    return '\n'.join(lines)


def pairs(rows):
    """Serialize only directly supplied relations. No inverse/transitive completion."""
    result = []
    for row in rows:
        refs = jlist(row['related_reference'])
        ids = jlist(row['related_judgment_id_if_available'])
        require(len(refs) == len(ids), 'unaligned related references and IDs')
        require(row['hierarchy_relation'] != 'UNRESOLVED' or not refs, 'unresolved relation has targets')
        for ref, target in zip(refs, ids):
            result.append(dict(judgment_id=row['judgment_id'], reference=row['reference_start'],
                               relation=row['hierarchy_relation'], related_reference=ref,
                               related_judgment_id=target, authority='HUMAN_AUTHORED_DIRECT_RELATION'))
    return result


def load_sources():
    """Read hash-pinned accepted artifacts only; no analytical replay or BHSA reload."""
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    archives, receipts = {}, []
    for role, pin in cfg['archives'].items():
        path = ROOT / pin['path']
        blob = path.read_bytes()
        a = src.archive(blob, pin['sha256'], mr1=pin['simple_manifest'])
        gg = src.table(a, pin['gates'])
        require(gg and all(r['status'] == 'PASS' for r in gg), role + ' accepted gates')
        archives[role] = a
        receipts.append(dict(role=role, path=pin['path'], sha256=a['sha256'], expected=pin['sha256']))
    tables = {}

    def table(role, name):
        key = (role, name)
        if key not in tables:
            member = name if name in archives[role]['files'] else src.member(archives[role], name)
            tables[key] = read_csv(archives[role]['files'][member])
        return tables[key]

    def verify_locator(loc):
        role, name = loc['archive_role'], loc['member']
        a = archives[role]
        require(loc['archive_sha256'] == a['sha256'], 'locator archive pin')
        require(loc['member_sha256'] == a['member_hashes'][name], 'locator member hash')
        rr = table(role, name)
        i = int(loc['data_row']) - 1
        require(0 <= i < len(rr) and sha(canonical(rr[i]).encode()) == loc['row_sha256'], 'locator exact row hash')
        return rr[i]

    catalog = {}

    def add(key, role, name, number, row, kind, atoms, links=(), extra=None):
        require(key not in catalog, 'duplicate source ID ' + key)
        catalog[key] = dict(evidence_id=key, source_layer=role, evidence_kind=kind,
                            atom_ids=atoms, source_locator=src.locator(role, archives[role], name, number, row),
                            source_row=row, dependencies=list(links), **(extra or {}))

    native_name = '12_native_clause_evidence.csv'
    for i, row in enumerate(table('r4_2', native_name), 1):
        add('BHSA2021:clause:' + row['clause'], 'r4_2', native_name, i, row,
            'NATIVE_CLAUSE_SNAPSHOT_NOT_A_BOUNDARY', jlist(row['clause_atom_ids']))
    participant_name = '01_participant_transition_events.csv'
    for i, row in enumerate(table('r4_2', participant_name), 1):
        add('R4.2:' + row['participant_event_id'], 'r4_2', participant_name, i, row,
            'SOURCE_PHRASE_CANDIDATE_NOT_ENTITY_RESOLUTION', jlist(row['clause_atom_ids']),
            ['BHSA2021:clause:' + row['clause']])
    anchor_name = '01_boundary_oriented_anchors.csv'
    for i, row in enumerate(table('r4_1', anchor_name), 1):
        loc = json.loads(row['source_locator'])
        original = verify_locator(loc)
        direct_key = row['anchor_id']
        require(direct_key not in catalog, 'duplicate MR1/HR1 ID')
        catalog[direct_key] = dict(evidence_id=direct_key, source_layer=loc['archive_role'],
            evidence_kind=row['marker_family'] or 'HUMAN_REVIEW_SCOPE_NOT_MARKER',
            atom_ids=jlist(row['atom_ids']), source_locator=loc, source_row=original, dependencies=[])
        add('R4.1:' + direct_key, 'r4_1', anchor_name, i, row, 'ACCEPTED_ANCHOR_OR_HUMAN_SCOPE',
            jlist(row['atom_ids']), [direct_key])
    formal_name = '20_formal_occurrences.csv'
    for i, row in enumerate(table('r4_2', formal_name), 1):
        locs = jlist(row['source_locators'])
        for loc in locs:
            verify_locator(loc)
        add('FORMAL:' + row['source_event_id'], 'r4_2', formal_name, i, row,
            'FORMAL_CONTEXT_NOT_BOUNDARY_OR_HIERARCHY', jlist(row['atom_ids']),
            extra={'upstream_locators': locs})
    # Exact existing control IDs enumerate all source evidence. Never match Hebrew text.
    control_name = '16_control_evidence.csv'
    for i, row in enumerate(table('r4_2', control_name), 1):
        atoms = jlist(row['atom_ids'])
        links = ['BHSA2021:clause:' + str(r['clause']) for r in jlist(row['native_clauses'])]
        links += ['R4.2:' + k for k in jlist(row['event_ids'])]
        links += ['R4.1:' + k for k in jlist(row['marker_ids'])]
        links += ['FORMAL:' + k for k in jlist(row['formal_ids'])]
        for key in links:
            require(key in catalog and bool(set(catalog[key]['atom_ids']) & set(atoms)), 'control native identity linkage')
        add('R4.2:CONTROL:' + row['ref'], 'r4_2', control_name, i, row,
            'EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION', atoms, links)
    # Prior human case links retain every source dependency, including singleton and extension evidence.
    prior_links = table('r4_2', '23_prior_human_source_links.csv')
    for row in prior_links:
        loc = json.loads(row['locator'])
        verify_locator(loc)
        key = 'HR1:' + row['case_id']
        if key in catalog:
            catalog[key].setdefault('upstream_locators', []).append(loc)
    for i, row in enumerate(table('hr1', '01_case_adjudication_links.csv'), 1):
        key = 'HR1:' + row['case_id']
        if key in catalog:
            record = 'HR1:RECORD:' + row['case_id']
            verify_locator(json.loads(row['r3c3_case_locator']))
            add(record, 'hr1', '01_case_adjudication_links.csv', i, row,
                'PRIOR_HUMAN_REVIEW_NOT_COMPUTATIONAL_JUDGMENT', catalog[key]['atom_ids'])
            catalog[key]['dependencies'].append(record)
    for value in catalog.values():
        for dep in value['dependencies']:
            require(dep in catalog, 'missing dependency ' + dep)
    return dict(mode='ACCEPTED_REAL_AUDIT_ONLY', cfg=cfg, catalog=catalog, receipts=receipts)


def expand_links(rows, catalog):
    result = []
    for row in rows:
        roots = jlist(row['source_evidence_ids'])
        require(roots == ['NO_EXACT_MACHINE_LINK'] or 'NO_EXACT_MACHINE_LINK' not in roots,
                'mixed unresolved and exact source links')
        seen = set()

        def visit(key):
            if key in seen or key == 'NO_EXACT_MACHINE_LINK':
                return
            require(key in catalog, 'unresolved exact ID ' + key)
            seen.add(key)
            entry = catalog[key]
            result.append(dict(judgment_id=row['judgment_id'], evidence_id=key,
                relationship='EXPLICIT_REGISTRY_LINK' if key in roots else 'EXPLICIT_SOURCE_DEPENDENCY',
                link_status='EXACT_ID', source_layer=entry['source_layer'],
                evidence_kind=entry['evidence_kind'], atom_ids=deepcopy(entry['atom_ids']),
                source_locator=deepcopy(entry['source_locator']), upstream_locators=deepcopy(entry.get('upstream_locators', [])),
                source_row=deepcopy(entry['source_row'])))
            for dep in entry['dependencies']:
                visit(dep)

        for key in roots:
            visit(key)
    return result


def negative_controls(rows, links):
    by_ref = {r['reference_start']: r for r in rows}
    result = []
    for ref, constraint in (
        ('1:5', 'NOT_SAME_LEVEL_AS_1_6'), ('1:13', 'CHILD_NOT_SIBLING_OF_1_6'),
        ('1:14', 'FOUR_MESSENGERS_HUMAN_ONLY'), ('1:16', 'ANONYMOUS_IDENTITY_UNRESOLVED'),
        ('1:17', 'ANONYMOUS_IDENTITY_UNRESOLVED'), ('1:18', 'ANONYMOUS_IDENTITY_UNRESOLVED'),
        ('1:22', 'NOT_MR1_EXPLICIT_CLOSURE'), ('2:10', 'NOT_MR1_EXPLICIT_CLOSURE'),
        ('2:9', 'INTERNAL_NOT_PARALLEL_TESTING_UNIT'), ('2:11', 'NO_GLOBAL_PARENT_ASSIGNED'),
        ('3:1', 'NOT_MR1_EVENT'), ('27:1', 'NOT_MACRO_DOES_NOT_MEAN_SUBORDINATE'),
        ('29:1', 'NOT_MACRO_DOES_NOT_MEAN_SUBORDINATE'),
        ('34:1', 'NOT_CHILD_OF_32_6'), ('35:1', 'NOT_CHILD_OF_32_6'), ('36:1', 'NOT_CHILD_OF_32_6'),
        ('37:24', 'NO_DIRECT_ELIHU_TO_YHWH_CONTINUITY'), ('40:1', 'NOT_SIBLING_OF_38_1'),
        ('42:16', 'NO_NEW_BOUNDARY_FROM_CONTENT_ONLY')):
        r = by_ref[ref]
        selected = [x for x in links if x['judgment_id'] == r['judgment_id']]
        result.append(dict(judgment_id=r['judgment_id'], reference=ref, constraint=constraint,
                           authority='HUMAN_ADJUDICATION_WITH_SEPARATE_SOURCE_EVIDENCE',
                           structural_function=r['structural_function'], relation=r['hierarchy_relation'],
                           evidence_ids=[x['evidence_id'] for x in selected]))
    return result


def build(s, rows=None, markdown=None):
    rows = deepcopy(registry() if rows is None else rows)
    markdown = MD.read_text(encoding='utf-8') if markdown is None else markdown
    links = expand_links(rows, s['catalog'])
    return dict(judgments=rows, links=links, pairs=pairs(rows),
                negative=negative_controls(rows, links), markdown=markdown)


def gates(m, s):
    rows = m['judgments']; cfg = s['cfg']
    rr = {r['reference_start']: r for r in rows}
    byid = {r['judgment_id']: r for r in rows}
    def at(ref, function=None, relation=None, targets=None):
        r = rr.get(ref, {})
        return bool(r) and (function is None or r['structural_function'] == function) and (
            relation is None or r['hierarchy_relation'] == relation) and (
            targets is None or jlist(r['related_reference']) == targets)
    def siblings(refs):
        return all(at(ref, relation='SAME_LEVEL_SIBLING', targets=[x for x in refs if x != ref]) for ref in refs)
    def source_rows(ref, kind):
        r = rr.get(ref, {})
        return [x['source_row'] for x in m['links'] if x['judgment_id'] == r.get('judgment_id') and x['evidence_kind'] == kind]
    def no_closure(ref):
        controls = source_rows(ref, 'EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION')
        return bool(controls) and all(r['MR1_EXPLICIT_CLOSURE'] == 'False' for r in controls) and not source_rows(ref, 'MR1_EXPLICIT_CLOSURE')
    def anonymous():
        for ref in ('1:16', '1:17', '1:18'):
            events = source_rows(ref, 'SOURCE_PHRASE_CANDIDATE_NOT_ENTITY_RESOLUTION')
            entries = [r for r in events if r['anonymous_entry'] == 'True']
            if len(entries) != 1 or any(r[k] != 'UNRESOLVED' for r in entries for k in (
                    'identity_status', 'participant_identity', 'first_appearance_in_book_if_exact')) or any(r['named_role'] for r in entries):
                return False
        return True
    check = {}
    check['ALL_HUMAN_JUDGMENTS_PRESENT'] = len(rows) == len(cfg['expected_references']) == len(byid) and set(rr) == set(cfg['expected_references'])
    check['FRIENDS_2_11_PARAGRAPH'] = at('2:11', 'PARAGRAPH_ONSET', 'UNRESOLVED', [])
    check['WIFE_2_9_INTERNAL'] = at('2:9', 'INTERNAL_TRANSITION', 'CONTINUES_WITHIN', ['2:1–2:10'])
    check['SCENE_1_13_CHILD'] = at('1:13', 'SCENE_ONSET', 'CHILD_OF', ['1:6'])
    check['TESTING_UNITS_SAME_LEVEL'] = siblings(['1:6', '2:1'])
    check['JOB_27_29_SAME_LEVEL'] = siblings(['27:1', '29:1'])
    check['FOUR_ELIHU_SIBLINGS'] = siblings(['32:6', '34:1', '35:1', '36:1'])
    check['TWO_YHWH_SIBLINGS'] = siblings(['38:1', '40:6'])
    check['40_1_CHILD_OF_38_1'] = at('40:1', 'INTERNAL_SPEECH_ONSET', 'CHILD_OF', ['38:1'])
    check['TWO_JOB_RESPONSE_SIBLINGS'] = siblings(['40:3', '42:1'])
    check['42_7_PARAGRAPH'] = at('42:7', 'PARAGRAPH_ONSET', 'UNRESOLVED', [])
    check['42_16_NO_BOUNDARY'] = at('42:16', 'NO_BOUNDARY', 'CONTINUES_WITHIN', ['42:7'])
    check['ENDINGS_NOT_MR1_CLOSURE'] = all(no_closure(ref) for ref in ('1:22', '2:10')) and all(at(a, 'PARALLEL_ENDING', 'PARALLEL_TO', [b]) for a,b in [('1:22','2:10'),('2:10','1:22')])
    check['3_1_NOT_MR1'] = bool(source_rows('3:1', 'NATIVE_CLAUSE_SNAPSHOT_NOT_A_BOUNDARY')) and not any(x['source_layer']=='mr1' for x in m['links'] if x['judgment_id']==rr.get('3:1',{}).get('judgment_id'))
    check['ANONYMOUS_IDENTITIES_UNRESOLVED'] = anonymous()
    explicit_entries = source_rows('1:14', 'SOURCE_PHRASE_CANDIDATE_NOT_ENTITY_RESOLUTION')
    check['OVERT_1_14_ENTRY_RETAINED'] = any(r.get('participant_event_id')==cfg['explicit_entry_event_id'] and r.get('identity_status')=='EXPLICIT' and r.get('anonymous_entry')=='False' for r in explicit_entries)
    anchors42 = source_rows('42:7', 'ACCEPTED_ANCHOR_OR_HUMAN_SCOPE')
    check['42_7_THREE_SOURCE_EVENTS_SEPARATE'] = any(r.get('marker_family')=='MR1_WAYHI_POSITIVE' for r in anchors42) and any(r.get('marker_family')=='MR1_CSF' and r.get('marker_subtype')=='SIMPLE_AMR' for r in anchors42) and any(r.get('human_case')=='CASE030' for r in anchors42)
    check['CLOSURES_AND_HR1_PRESERVED'] = all(source_rows(ref,'MR1_EXPLICIT_CLOSURE') and any(r.get('case_id')==case for r in source_rows(ref,'PRIOR_HUMAN_REVIEW_NOT_COMPUTATIONAL_JUDGMENT')) for ref,case in [('31:40','CASE025'),('32:1','CASE026')])
    check['NO_AUTOMATIC_HIERARCHY'] = m['pairs'] == pairs(rows) and all(r['reference_start'] in cfg['expected_references'] for r in rows) and all(
        (r['structural_function'], r['hierarchy_relation'], jlist(r['related_reference'])) == tuple([v[0], v[1], v[2]]) for r in rows for v in [cfg['human_relation_assertions'].get(r['reference_start'], ['', '', []])])
    all_records = rows + m['pairs'] + m['links'] + m['negative']
    check['NO_SCORE_RANK'] = all(not any(any(word in key.lower() for word in ('score','rank','confidence','percentage')) for key in r) for r in all_records)
    check['NO_NEW_INTERPRETIVE_LABEL'] = all(r['structural_function'] in FUNCTIONS and r['hierarchy_relation'] in RELATIONS for r in rows) and all(not {'rhetorical_label','theological_label','discourse_label','semantic_label'}.intersection(r) for r in all_records)
    try:
        exact = expand_links(rows, s['catalog'])
        check['EXACT_SOURCE_LINKAGE_ONLY'] = m['links'] == exact
    except (ValueError, KeyError):
        check['EXACT_SOURCE_LINKAGE_ONLY'] = False
    check['HUMAN_SCHEMA_AND_TARGET_IDS'] = all(set(r)==set(FIELDS) and r['review_status']=='REVIEWED' and r['judgment_type']=='HUMAN_STRUCTURAL_ADJUDICATION' for r in rows) and all(
        not p['related_judgment_id'] or (p['related_judgment_id'] in byid and byid[p['related_judgment_id']]['reference_start']==p['related_reference']) for p in m['pairs'])
    check['REFERENCE_SPANS_AND_LINK_SCOPES'] = all(
        r['reference_end']==cfg['human_reference_scopes'].get(r['reference_start'], [''])[-1]
        and (jlist(r['source_evidence_ids'])==['NO_EXACT_MACHINE_LINK'] or
             sorted(x['ref'] for x in source_rows(r['reference_start'],'EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION'))==sorted(cfg['human_reference_scopes'][r['reference_start']]))
        for r in rows)
    check['MD_CSV_AGREE'] = markdown_table(rows) in m['markdown'] and all(p in m['markdown'] for p in cfg['principles'])
    check['DIRECT_3_1_ABOVE_3_2'] = at('3:1','PARAGRAPH_ONSET','HIERARCHICALLY_ABOVE',['3:2']) and at('3:2','SPEECH_UNIT_ONSET','CONTINUES_WITHIN',['3:1'])
    check['SOURCE_ARCHIVE_INTEGRITY'] = bool(s['receipts']) and all(r['sha256']==r['expected']==cfg['archives'].get(r['role'],{}).get('sha256') for r in s['receipts']) and len(s['receipts'])==len(cfg['archives']) and set(r['role'] for r in s['receipts'])==set(cfg['archives'])
    try:
        check['NEGATIVE_CONTROLS_RETAINED'] = m['negative'] == negative_controls(rows,m['links'])
        check['DETERMINISTIC_OUTPUT'] = m == build(s, rows, m['markdown'])
    except (ValueError, KeyError):
        check['NEGATIVE_CONTROLS_RETAINED'] = check['DETERMINISTIC_OUTPUT'] = False
    return [dict(gate=k, status='PASS' if v else 'FAIL') for k,v in check.items()]


def serialize(m, s):
    checks = gates(m, s)
    require(all(r['status']=='PASS' for r in checks), 'gates failed: ' + canonical([r for r in checks if r['status']!='PASS']))
    linked = {r['judgment_id'] for r in m['links']}
    counts = dict(judgments=len(m['judgments']), direct_relation_pairs=len(m['pairs']), source_links=len(m['links']),
                  source_linked_judgments=len(linked), human_only_judgments=len(m['judgments'])-len(linked), negative_controls=len(m['negative']))
    report = '\n'.join(['# HSA1 human structural adjudication audit', '', 'Mode: ' + s['mode'], '',
        'Human-authored judgments, not computational conclusions. Context links do not prove the human hierarchy.', '',
        *[f'- {k}: {v}' for k,v in counts.items()], '',
        'Relations are directed, explicitly authored pairs; reciprocal sibling/parallel pairs are counted twice.',
        'UNRESOLVED relations produce no pair. Supplied enclosing spans do not create new parent objects.', '',
        '3:1 has native evidence, no MR1 event. 1:22/2:10 are human parallel endings, not MR1 explicit closures.',
        'Anonymous entry events remain unresolved. Four messengers is a human control only.',
        '42:7 preserves Wayhi, SIMPLE_AMR and CASE030 separately. 42:16 remains a human NO_BOUNDARY control.',
        'Formal patterns and participant mentions are context, not automatic boundary confirmations.',
        'No unreviewed Job 3–26 hierarchy inferred. Review Job 3–26 before R4.3 whole-book parentage.', ''])
    files = {
        '01_structural_judgments.csv': registry_bytes(m['judgments']),
        '02_judgment_source_links.csv': util.csv_bytes(m['links']),
        '03_hierarchy_relation_pairs.csv': util.csv_bytes(m['pairs']),
        '04_negative_controls.csv': util.csv_bytes(m['negative']),
        '05_methodological_principles.md': ('# Human methodological principles\n\n' + '\n'.join(f'{i}. {p}' for i,p in enumerate(s['cfg']['principles'],1))+'\n').encode(),
        '06_structural_adjudication_report.md': report.encode(),
        '08_human_registry.md': m['markdown'].encode(),
        '90_run_metadata.json': util.json_bytes(dict(version='HSA1', mode=s['mode'], status='PASS', counts=counts,
            source_receipts=s['receipts'], registry_sha256=sha(registry_bytes(m['judgments'])),
            registry_markdown_sha256=sha(m['markdown'].encode()), config_sha256=sha(canonical(s['cfg']).encode()),
            code_sha256=sha(Path(__file__).read_bytes()), gate_count=len(checks)+1))}
    def seal():
        files.pop('99_manifest_sha256.csv', None)
        files['99_manifest_sha256.csv'] = util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(files.items())])
    seal(); checks.append(util.manifest_gate(files)); files['07_gates.csv']=util.csv_bytes(checks); seal()
    require(util.manifest_ok(files), 'manifest integrity')
    return files


def publish(files, out):
    out = Path(out).resolve(); zp=out.with_name(out.name+'_results.zip'); log=out.with_name(out.name+'_run.log')
    require(not any(p.exists() for p in (out,zp,log)), 'output exists')
    require(util.manifest_ok(files), 'output manifest')
    out.mkdir(parents=True)
    for name, blob in files.items():
        (out/name).write_bytes(blob)
    with zipfile.ZipFile(zp,'w') as z:
        for name, blob in sorted(files.items()):
            info=zipfile.ZipInfo(name,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,blob)
    with zipfile.ZipFile(zp) as z:
        require(z.testzip() is None and {n:z.read(n) for n in z.namelist()}==files,'ZIP integrity')
    require({p.name:p.read_bytes() for p in out.iterdir()}==files,'published file integrity')
    log.write_text(f'HSA1 PASS\nMode {json.loads(files["90_run_metadata.json"])["mode"]}\nGates {len(read_csv(files["07_gates.csv"]))} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n',encoding='utf-8')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args(argv)
    if args.self_test:
        from milal_hsa1_synthetic import source
        s, rows, md=source(); m=build(s,rows,md)
    else:
        s=load_sources(); m=build(s)
    files=serialize(m,s)
    require(files==serialize(build(s,m['judgments'],m['markdown']),s),'independent deterministic serialization')
    if not args.self_test:
        require(CSV.read_bytes()==files['01_structural_judgments.csv'] and MD.read_bytes()==files['08_human_registry.md'],'human source byte fidelity')
        for receipt in s['receipts']:
            require(sha((ROOT/receipt['path']).read_bytes())==receipt['expected'],'source changed before publication')
    publish(files,args.out)
    print('HSA1 PASS ' + str(Path(args.out).resolve()))
    return 0


if __name__=='__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc),file=sys.stderr);sys.exit(2)
