"""PROV1: read-only reconstruction of historical signatures, not an analytical stage.

The verified historical generator is fingerprinted, never imported or executed.
Its pure serialization/construction rules (lines 100-122, 502-523, 556-557,
638-639, 669, 768, 859-861) are transcribed here. No R1/BHSA loading.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import csv
import hashlib
import io
import json
from pathlib import Path

import milal_r3c_3_signature_context as frozen

csv.field_size_limit(64 * 1024 * 1024)

REVIEW_FIELDS = frozen.REVIEW_FIELDS
VERSION = 'PROV1'
NA = 'NOT_AVAILABLE_FROM_SOURCE'
LEVELS = tuple('G' + str(i) for i in range(7))
KEYS = ('G0_atom_type', 'G1_verbal_morphology', 'G2_constituent_shape',
        'G3_core_argument_realization', 'G4_verbal_lexemes',
        'G5_general_content_lexemes', 'G6_entity_identity_lexical_bundles')
DESCRIPTIONS = ('clause_atom type', '+ verbal morphology', '+ constituent shape',
                '+ core-argument realization', '+ verbal lexeme identity',
                '+ general content lexemes, excluding BHSA gentilics (ls=gntl)',
                '+ proper-name (pdp=nmpr) and BHSA gentilic (ls=gntl) lexical identity bundles')
MISSING = {'', 'NA', 'n/a', 'absent', '?', 'None', 'none', 'null'}
EXPECTED = {
    'generator': '125bbda9d0ffbb777d811e3f464a3a85f24526b060df67d564ef229d483b79cd',
    'r2': 'a1a6845101f3957756e7748ab78ba85c4c9f39cf7f8e1ba86aed4396fd2716a2',
    'b2': 'd7989468f82274baf6b3d3692529739e940f6950e3a24c5b38914a9a71c61095',
    'b3': '612d4f9f432b8aaac5a2266341c464b2ee654dd7d353cea688866b94355cd5af',
    'c3': '5f8239a692a516fd9722d94fb919321d399fad93c3583dd828ac1c1883576981',
}
# Required named columns: extra columns remain in source_row, never discarded.
SCHEMAS = {
    'atoms': ('r2', '01_atom_form_vectors.csv', ('atom_node', 'atom_index_1based', 'atom_typ', 'ref_start', 'ref_end') + KEYS[1:] + tuple('signature_' + l for l in LEVELS)),
    'windows': ('r2', '02_sequence_windows.csv', ('window_id', 'start_index_1based', 'sequence_length', 'atom_nodes') + tuple('signature_' + l for l in LEVELS)),
    'families': ('r2', '03_repeated_form_families.csv', ('family_id', 'level', 'sequence_length', 'occurrence_count', 'signature_hash', 'exemplar_window_id')),
    'occurrences': ('r2', '04_family_occurrences.csv', ('family_id', 'window_id', 'atom_nodes', 'start_index_1based', 'sequence_length')),
    'refinements': ('r2', '05_form_refinements.csv', ('parent_family_id', 'parent_level', 'child_level', 'sequence_length', 'refinement_group_index', 'child_status', 'child_family_id', 'child_signature_hash', 'occurrence_count', 'exemplar_window_id')),
    'singletons': ('r2', '07_single_atom_singletons.csv', ('atom_node', 'atom_index_1based', 'first_unique_level') + tuple('signature_' + l for l in LEVELS) + tuple('count_' + l for l in LEVELS)),
    'members': ('b2', '02_bundle_family_members.csv', ('family_id', 'bundle_id', 'signature_hash')),
    'bundle_occurrences': ('b2', '03_bundle_occurrences.csv', ('bundle_id', 'window_id', 'atom_nodes')),
    'items': ('b2', '08_singleton_review_items.csv', ('review_item_id', 'atom_node', 'signature_G6')),
    'lineages': ('b3', '02_lineage_bundle_members.csv', ('bundle_id', 'lineage_id', 'parent_bundle_id')),
    'events': ('b3', '05_lineage_singleton_refinement_events.csv', ('parent_family_id', 'child_level', 'child_signature_hash', 'exemplar_window_id', 'mapped_g6_singleton_review_item_id')),
    'singleton_links': ('b3', '06_g6_singleton_lineage_links.csv', ('review_item_id', 'atom_node', 'lineage_id', 'parent_family_id_at_first_unique')),
    'overlay': ('b3', '07_sequence_extension_lineage_overlay.csv', ('short_bundle_id', 'long_bundle_id')),
    'cases': ('c3', '02_review_cases.csv', ('case_id', 'unit_id', 'target_summaries') + tuple(REVIEW_FIELDS)),
    'boundary': ('c3', '07_boundary_definition_context.csv', ('case_id', 'unit_ids')),
    'definitions': ('c3', '05_singleton_definition_context.csv', ('unit_id', 'source_rows')),
}
FILES = dict(zip(('atoms', 'families', 'refinements', 'singletons', 'links', 'audit'), (
    '01_atom_signature_provenance.csv', '02_family_signature_provenance.csv',
    '03_refinement_feature_delta.csv', '04_singleton_signature_provenance.csv',
    '05_downstream_identity_links.csv', '06_hash_reconstruction_audit.csv')))


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def sha(blob):
    return hashlib.sha256(blob).hexdigest()


def sig(value):
    return sha(canonical_json(value).encode('utf-8'))


def norm(value):
    text = '' if value is None else str(value)
    return '∅' if text in MISSING else text


def tuples(value):
    return tuple(tuples(v) for v in value) if isinstance(value, list) else value


def reconstruct_atom(row):
    components = [(norm(row['atom_typ']),)]
    for key in KEYS[1:]:
        value = json.loads(row[key])
        if not isinstance(value, list):
            raise ValueError('Schema: component must be JSON array: ' + key)
        components.append(tuples(value))
    return [tuple(zip(KEYS[:k + 1], components[:k + 1])) for k in range(7)]


def unique(rows, key):
    result = {r[key]: r for r in rows}
    if len(result) != len(rows) or '' in result:
        raise ValueError('Schema: duplicate/blank ' + key)
    return result


def load(paths):
    # Hash all raw input bytes before parsing tables or deriving any evidence.
    blobs = {k: Path(p).read_bytes() for k, p in paths.items()}
    if set(blobs) != set(EXPECTED):
        raise ValueError('Five exact inputs required')
    for key, blob in blobs.items():
        if sha(blob) != EXPECTED[key]:
            raise ValueError('SHA256 mismatch: ' + key)
    archives = {k: frozen.read_archive(paths[k]) for k in ('r2', 'b2', 'b3', 'c3')}
    if not frozen.manifest_valid(archives['c3']):
        raise ValueError('R3c.3 manifest integrity failure')
    meta = frozen.source_metadata(archives['c3'])
    if meta['version'] != 'R3c.3' or meta.get('gate_failures') or any(
            meta['sources'][k]['sha256'] != EXPECTED[k] for k in ('b2', 'b3')):
        raise ValueError('R3c.3 source chain failure')
    tables, locators = {}, {}
    for key, (role, name, columns) in SCHEMAS.items():
        member = frozen.member(archives[role], name)
        data = archives[role]['files'][member]
        reader = csv.DictReader(io.StringIO(data.decode('utf-8-sig')))
        if len(reader.fieldnames or []) != len(set(reader.fieldnames or [])) or not set(columns) <= set(reader.fieldnames or []):
            raise ValueError('Schema: missing exact columns in ' + name)
        tables[key] = list(reader)
        locators[key] = {'archive_role': role, 'archive_sha256': EXPECTED[role],
                         'member': member, 'member_sha256': sha(data)}
    return {'tables': tables, 'locators': locators,
            'hashes': {k: sha(b) for k, b in blobs.items()}, 'expected_hashes': dict(EXPECTED),
            'mode': 'ACCEPTED_REAL', 'source_metadata': meta}


def evidence(source, table, index):
    return dict(source['locators'][table], data_row=index + 1,
                source_row=copy.deepcopy(source['tables'][table][index]))


def schema_ok(source):
    try:
        return all(source['tables'][key] and all(set(cols) <= set(r) for r in source['tables'][key])
                   for key, (_, _, cols) in SCHEMAS.items())
    except (KeyError, TypeError):
        return False


def derive(source):
    if not schema_ok(source):
        raise ValueError('Schema: missing required table/columns')
    t = source['tables']
    raw_atoms = unique(t['atoms'], 'atom_node')
    raw_families = unique(t['families'], 'family_id')
    windows = unique(t['windows'], 'window_id')
    unique(t['cases'], 'case_id')
    unique(t['singletons'], 'atom_node')
    ordered = sorted(t['atoms'], key=lambda r: int(r['atom_index_1based']))
    if [int(r['atom_index_1based']) for r in ordered] != list(range(1, len(ordered) + 1)):
        raise ValueError('Schema: atom order must be explicit and contiguous')
    atom_order = [r['atom_node'] for r in ordered]
    payloads = {a: reconstruct_atom(r) for a, r in raw_atoms.items()}
    hashes = {a: [sig(p) for p in ps] for a, ps in payloads.items()}
    counts = [Counter(v[k] for v in hashes.values()) for k in range(7)]
    atoms, families, deltas, singles, audit, links = [], [], [], [], [], []

    def record(kind, identity, level, preimage, historical):
        actual = sig(preimage)
        result = {'canonical_json_preimage': canonical_json(preimage),
                  'reconstructed_hash': actual, 'historical_hash': historical,
                  'hash_match': actual == historical}
        audit.append(dict(object_type=kind, object_id=identity, level=level, **result))
        return result

    def window_payload(wid, level):
        w = windows[wid]
        nodes = w['atom_nodes'].split('|')
        length, start = int(w['sequence_length']), int(w['start_index_1based']) - 1
        if nodes != atom_order[start:start + length] or len(nodes) != length:
            raise ValueError('Window geometry disagrees with explicit atom order: ' + wid)
        k = LEVELS.index(level)
        key = tuple(hashes[a][k] for a in nodes)
        positions = [{'sequence_position': i + 1, 'atom_node': a,
                      'added_component_key': KEYS[k], 'added_component': payloads[a][k][-1][1],
                      'cumulative_payload': payloads[a][k]} for i, a in enumerate(nodes)]
        return (level, length, key), positions

    for i, r in enumerate(t['atoms']):
        for k, level in enumerate(LEVELS):
            p = payloads[r['atom_node']][k]
            atoms.append(dict(atom_node=r['atom_node'], ref_start=r['ref_start'], ref_end=r['ref_end'],
                              level=level, level_description=DESCRIPTIONS[k], component_key=KEYS[k],
                              added_component=p[-1][1], cumulative_payload=p, source=evidence(source, 'atoms', i),
                              **record('ATOM', r['atom_node'], level, p, r['signature_' + level])))
    occ = defaultdict(list)
    for i, r in enumerate(t['occurrences']):
        if r['family_id'] not in raw_families:
            raise ValueError('Unknown occurrence family')
        occ[r['family_id']].append((i, r))
    members = defaultdict(list)
    for i, r in enumerate(t['members']):
        if r['family_id'] not in raw_families or r['signature_hash'] != raw_families[r['family_id']]['signature_hash']:
            raise ValueError('Downstream family identity/hash mismatch')
        members[r['family_id']].append(r['bundle_id'])
    for fid, bids in members.items():
        expected_occ = Counter((o['window_id'], o['atom_nodes']) for _, o in occ[fid])
        for bid in bids:
            actual_occ = Counter((o['window_id'], o['atom_nodes']) for o in t['bundle_occurrences'] if o['bundle_id'] == bid)
            if actual_occ != expected_occ:
                raise ValueError('Downstream bundle occurrence membership mismatch: ' + bid)
    for i, r in enumerate(t['families']):
        fid, level = r['family_id'], r['level']
        pre, positions = window_payload(r['exemplar_window_id'], level)
        occurrences = []
        for oi, o in occ[fid]:
            op, _ = window_payload(o['window_id'], level)
            if op != pre or o['atom_nodes'] != windows[o['window_id']]['atom_nodes']:
                raise ValueError('Occurrence membership mismatch: ' + fid)
            occurrences.append(evidence(source, 'occurrences', oi))
        if len(occurrences) != int(r['occurrence_count']) or not occurrences:
            raise ValueError('Occurrence count mismatch: ' + fid)
        families.append(dict(family_id=fid, level=level, sequence_length=r['sequence_length'],
                             occurrence_count=r['occurrence_count'], sequence_key=pre[2], positions=positions,
                             bundle_ids=members[fid] or [NA], occurrences=occurrences,
                             source=evidence(source, 'families', i),
                             **record('FAMILY', fid, level, pre, r['signature_hash'])))
    child_partition = defaultdict(Counter)
    for i, r in enumerate(t['refinements']):
        fid, child = r['parent_family_id'], r['child_level']
        parent = raw_families[fid]
        if LEVELS.index(child) != LEVELS.index(parent['level']) + 1 or r['parent_level'] != parent['level']:
            raise ValueError('Non-adjacent or changed genealogy')
        pre, positions = window_payload(r['exemplar_window_id'], child)
        matching = [o for _, o in occ[fid] if window_payload(o['window_id'], child)[0] == pre]
        if len(matching) != int(r['occurrence_count']) or not matching:
            raise ValueError('Refinement occurrence subset mismatch')
        child_partition[fid].update(o['window_id'] for o in matching)
        if r['child_family_id'] and raw_families[r['child_family_id']]['signature_hash'] != r['child_signature_hash']:
            raise ValueError('Child family hash mismatch')
        status = 'REPEATED_FAMILY' if len(matching) >= 2 else 'SINGLETON_REFINEMENT'
        if r['child_status'] != status or bool(r['child_family_id']) != (status == 'REPEATED_FAMILY'):
            raise ValueError('Changed refinement child identity/status')
        event_links = [evidence(source, 'events', j) for j, e in enumerate(t['events']) if all(
            e[k] == r[k] for k in ('parent_family_id', 'child_level', 'child_signature_hash', 'exemplar_window_id'))]
        deltas.append(dict(parent_family_id=fid, child_family_id=r['child_family_id'] or NA,
                           parent_bundle_ids=members[fid] or [NA], child_bundle_ids=members[r['child_family_id']] or [NA],
                           singleton_links=event_links or [NA], parent_level=r['parent_level'], child_level=child,
                           added_component_key=KEYS[LEVELS.index(child)], positions=positions,
                           parent_occurrence_count=parent['occurrence_count'], child_occurrence_count=r['occurrence_count'],
                           occurrence_window_ids=[o['window_id'] for o in matching],
                           source=evidence(source, 'refinements', i),
                           **record('REFINEMENT', str(i + 1), child, pre, r['child_signature_hash'])))
    for fid, f in raw_families.items():
        if f['level'] != 'G6' and child_partition[fid] != Counter(o['window_id'] for _, o in occ[fid]):
            raise ValueError('Refinements do not partition parent occurrences: ' + fid)
    if {r['atom_node'] for r in t['singletons']} != {a for a in hashes if counts[6][hashes[a][6]] == 1}:
        raise ValueError('Singleton population incomplete')
    for i, r in enumerate(t['singletons']):
        a = r['atom_node']
        cs = [counts[k][hashes[a][k]] for k in range(7)]
        first = next((LEVELS[k] for k, n in enumerate(cs) if n == 1), '')
        if cs[-1] != 1 or first != r['first_unique_level'] or cs != [int(r['count_' + l]) for l in LEVELS]:
            raise ValueError('Singleton count/first uniqueness mismatch')
        checks = [record('SINGLETON_ATOM', a, l, payloads[a][k], r['signature_' + l]) for k, l in enumerate(LEVELS)]
        item_ids = [it['review_item_id'] for it in t['items'] if it['atom_node'] == a]
        if any(it['signature_G6'] != r['signature_G6'] for it in t['items'] if it['atom_node'] == a):
            raise ValueError('Singleton downstream atom hash mismatch')
        singles.append(dict(atom_node=a, review_item_ids=item_ids or [NA], first_unique_level=first,
                            cumulative_counts=dict(zip(LEVELS, cs)), component_values=payloads[a][-1],
                            first_unique_payload=payloads[a][LEVELS.index(first)], G6_payload=payloads[a][-1],
                            atom_hashes=checks, source=evidence(source, 'singletons', i)))
    # Each source row remains independently addressable, including one-to-many links.
    for table in ('members', 'bundle_occurrences', 'lineages', 'events', 'items', 'singleton_links', 'overlay', 'cases', 'boundary', 'definitions'):
        for i, r in enumerate(t[table]):
            links.append(dict(link_type=table, layer='SEQUENCE_EXTENSION_OVERLAY_ONLY' if table == 'overlay' else 'EXPLICIT_SOURCE',
                              **{k: r.get(k) or NA for k in ('family_id', 'bundle_id', 'lineage_id', 'review_item_id', 'atom_node', 'case_id', 'unit_id')},
                              source=evidence(source, table, i)))
    # Direct review-unit mappings come from target_summaries, never ID prefix guessing.
    for i, c in enumerate(t['cases']):
        for s in json.loads(c['target_summaries']):
            links.append(dict(link_type='review_unit', layer='EXPLICIT_SOURCE', case_id=c['case_id'],
                              review_unit_id=s['unit_id'], family_id=s.get('family_id') or NA,
                              bundle_id=s.get('bundle_id') or NA, lineage_id=s.get('lineage_id') or NA,
                              review_item_id=s.get('review_item_id') or NA, summary=s,
                              source=evidence(source, 'cases', i)))
    # Explicit event source rows retained by R3c.3 provide event-only review-unit links.
    for i, d in enumerate(t['definitions']):
        for ref in json.loads(d['source_rows']):
            links.append(dict(link_type='review_unit_source', layer='EXPLICIT_SOURCE', review_unit_id=d['unit_id'],
                              source=evidence(source, 'definitions', i), upstream_source=ref))
    return {'validation_mode': source['mode'], 'atoms': atoms, 'families': families, 'refinements': deltas, 'singletons': singles,
            'links': links, 'audit': audit, 'cases': copy.deepcopy(t['cases']),
            'boundary': copy.deepcopy(t['boundary'])}


def pretty(value):
    return canonical_json(value)


def render_catalog(model):
    lines = ['# PROV1 — Signature provenance', '',
             'Validation mode: ' + model['validation_mode'] + '. Synthetic values are not historical dataset results.',
             'Structural feature values only. Human judgment remains in the unchanged source review forms.',
             'Each family lists the added component separately from its cumulative payload.', '']
    for f in model['families']:
        lines += [f"## {f['family_id']} / {f['level']} / length {f['sequence_length']}",
                  f"Historical hash: `{f['historical_hash']}`; reconstruction: {'MATCH' if f['hash_match'] else 'MISMATCH'}.",
                  f"Bundles: {pretty(f['bundle_ids'])}. Occurrences: {f['occurrence_count']}."]
        for p in f['positions']:
            lines += [f"Position {p['sequence_position']}: added `{p['added_component_key']}` = `{pretty(p['added_component'])}`",
                      f"Cumulative: `{pretty(p['cumulative_payload'])}`"]
        lines.append('')
    for s in model['singletons']:
        lines += [f"## Singleton {pretty(s['review_item_ids'])} / atom {s['atom_node']}",
                  f"First unique: {s['first_unique_level']}; counts: {pretty(s['cumulative_counts'])}",
                  f"First-unique atom payload: `{pretty(s['first_unique_payload'])}`",
                  f"G6 atom payload: `{pretty(s['G6_payload'])}`",
                  f"G6 atom hash: `{s['atom_hashes'][-1]['historical_hash']}`", '']
    return '\n'.join(lines) + '\n'


def render_cases(model):
    lines = ['# PROV1 — Five-case structural evidence', '',
             'Validation mode: ' + model['validation_mode'] + '. Synthetic values are not historical dataset results.', '']
    for cid in frozen.CONTROLS:
        cases = [c for c in model['cases'] if c['case_id'] == cid]
        lines += ['## ' + cid]
        if len(cases) != 1:
            lines += [NA, '']; continue
        c = cases[0]
        lines += [f"Source target: {c['unit_id'] or c.get('boundary_ref', NA)}"]
        summaries = json.loads(c['target_summaries'])
        units = [s['unit_id'] for s in summaries]
        lines += ['All participating units: ' + pretty(units)]
        lines += ['Explicit source identities: ' + pretty([
            {k: s.get(k) or NA for k in ('unit_id', 'bundle_id', 'lineage_id', 'review_item_id')}
            for s in summaries])]
        bids = {s.get('bundle_id') for s in summaries} - {None, ''}
        # Preserve ancestry by explicit parent bundle rows, without changing target units.
        parents = {l['source']['source_row']['bundle_id']: l['source']['source_row']['parent_bundle_id']
                   for l in model['links'] if l['link_type'] == 'lineages'}
        pending = list(bids)
        while pending:
            p = parents.get(pending.pop())
            if p and p not in bids:
                bids.add(p); pending.append(p)
        fs = [f for f in model['families'] if bids.intersection(f['bundle_ids'])]
        fids = {f['family_id'] for f in fs}
        for f in fs:
            lines += [f"### {f['family_id']} / {f['level']}", f"Hash `{f['historical_hash']}`: {'MATCH' if f['hash_match'] else 'MISMATCH'}"]
            for p in f['positions']:
                lines += [f"Position {p['sequence_position']} added {p['added_component_key']}: `{pretty(p['added_component'])}`",
                          f"Cumulative: `{pretty(p['cumulative_payload'])}`"]
        for d in model['refinements']:
            if d['parent_family_id'] in fids or d['child_family_id'] in fids:
                lines += [f"Refinement {d['parent_family_id']} → {d['child_family_id']} ({d['parent_level']} → {d['child_level']}):",
                          f"Added {d['added_component_key']}: `{pretty([p['added_component'] for p in d['positions']])}`",
                          f"Window/refinement hash `{d['historical_hash']}`: {'MATCH' if d['hash_match'] else 'MISMATCH'}"]
        itemids = {s.get('review_item_id') for s in summaries} - {None, ''}
        for s in model['singletons']:
            if itemids.intersection(s['review_item_ids']):
                lines += [f"### Singleton {pretty(s['review_item_ids'])}", f"Counts: {pretty(s['cumulative_counts'])}",
                          f"First unique {s['first_unique_level']} payload: `{pretty(s['first_unique_payload'])}`",
                          f"G6 atom payload: `{pretty(s['G6_payload'])}`",
                          f"G6 atom hash: `{s['atom_hashes'][-1]['historical_hash']}`"]
                for d in model['refinements']:
                    if any(isinstance(e, dict) and e['source_row']['mapped_g6_singleton_review_item_id'] in s['review_item_ids'] for e in d['singleton_links']):
                        lines += [f"Parent {d['parent_family_id']} / {pretty(d['parent_bundle_ids'])}; {d['parent_level']} → {d['child_level']}",
                                  f"Added component: `{pretty([p['added_component'] for p in d['positions']])}`",
                                  f"Separate window/refinement child hash: `{d['historical_hash']}`"]
        # Event-only units are never silently dropped from boundary presentation.
        for link in model['links']:
            if link['link_type'] == 'review_unit_source' and link['review_unit_id'] in units:
                row = link['upstream_source']['row']
                lines += [f"Explicit source for {link['review_unit_id']}: `{pretty(row)}`"]
                for d in model['refinements']:
                    dr = d['source']['source_row']
                    if all(row.get(k) == dr[k] for k in ('parent_family_id', 'child_level', 'child_signature_hash', 'exemplar_window_id')):
                        lines += [f"Event added component {d['added_component_key']}: `{pretty([p['added_component'] for p in d['positions']])}`",
                                  f"Cumulative per position: `{pretty([p['cumulative_payload'] for p in d['positions']])}`"]
        lines += ['Human judgment: unchanged source fields; no automatic assessment.', '']
    return '\n'.join(lines)


def build(source):
    if source['hashes'] != source['expected_hashes']:
        raise ValueError('Input SHA preflight failure')
    model = dict(source=source, **derive(source))
    model['catalog'] = render_catalog(model)
    model['five_cases'] = render_cases(model)
    return model


def gates(model):
    s = model['source']
    if not schema_ok(s):
        return [{'gate_id': 'SOURCE_SCHEMAS_VALID', 'status': 'FAIL'}]
    expected = derive(s)
    eq = lambda k: canonical_json(model[k]) == canonical_json(expected[k])
    matched = lambda kind: bool([r for r in model['audit'] if r['object_type'] == kind]) and all(
        r['reconstructed_hash'] == r['historical_hash'] and r['hash_match'] and
        sha(r['canonical_json_preimage'].encode('utf-8')) == r['reconstructed_hash']
        for r in model['audit'] if r['object_type'] == kind)
    def control(cid, bid):
        cases = [c for c in model['cases'] if c['case_id'] == cid]
        return len(cases) == 1 and any(x.get('bundle_id') == bid for x in json.loads(cases[0]['target_summaries'])) and (
            bool([f for f in model['families'] if bid in f['bundle_ids']]) and eq('families') and
            ('## ' + cid) in model['five_cases'] and model['five_cases'] == render_cases(model))
    boundary = [b for b in model['boundary'] if b['case_id'] == 'CASE025']
    checks = {
        'GENERATOR_SHA_EXACT': s['hashes']['generator'] == s['expected_hashes']['generator'],
        'R2_ARCHIVE_SHA_EXACT': s['hashes']['r2'] == s['expected_hashes']['r2'],
        'DOWNSTREAM_SHA_EXACT': all(s['hashes'][k] == s['expected_hashes'][k] for k in ('b2', 'b3', 'c3')),
        'SOURCE_SCHEMAS_VALID': schema_ok(s),
        'ATOM_HASHES_EXACT': eq('atoms') and matched('ATOM') and len(model['atoms']) == len(s['tables']['atoms']) * 7,
        'FAMILY_HASHES_EXACT': eq('families') and matched('FAMILY'),
        'REFINEMENT_HASHES_EXACT': eq('refinements') and matched('REFINEMENT'),
        'SINGLETON_HASHES_EXACT': eq('singletons') and matched('SINGLETON_ATOM'),
        'HISTORICAL_IDS_UNCHANGED': all([r[k] for r in model[table]] == [r[k] for r in expected[table]] for table, k in (('atoms', 'atom_node'), ('families', 'family_id'), ('singletons', 'atom_node'))) and eq('cases'),
        'OCCURRENCES_UNCHANGED': [f['occurrences'] for f in model['families']] == [f['occurrences'] for f in expected['families']] and eq('links'),
        'GENEALOGY_UNCHANGED': eq('refinements'),
        'JUDGMENTS_UNFILLED': eq('cases') and all(all(not c.get(f) or (f == 'review_status' and c[f] == 'UNREVIEWED') for f in REVIEW_FIELDS) for c in model['cases']),
        'NO_AUTOMATIC_LABELS': set(model) == {'source', *expected, 'catalog', 'five_cases'} and model['catalog'] == render_catalog(expected) and model['five_cases'] == render_cases(expected),
        'EXPLICIT_LOSSLESS_LINKS': eq('links'),
        'CASE001_PRESERVED': control('CASE001', 'RB00104'),
        'CASE007_PRESERVED': control('CASE007', 'RB00121'),
        'CASE013_PRESERVED': control('CASE013', 'RB00548') and all(any(d['parent_family_id'] == p and d['child_family_id'] == c for d in model['refinements']) for p, c in [('F001301', 'F001968'), ('F001968', 'F002481')]),
        'S02135_PRESERVED': any('S02135' in r['review_item_ids'] and r['first_unique_level'] == 'G3' for r in model['singletons']) and eq('singletons') and '## CASE019' in model['five_cases'],
        'CASE025_MULTIPLICITY': len(boundary) == 1 and len(json.loads(boundary[0]['unit_ids'])) > 1 and eq('boundary') and all(u in model['five_cases'] for u in json.loads(boundary[0]['unit_ids'])),
        'EXTENSION_OVERLAY_ONLY': [r for r in model['links'] if r['link_type'] == 'overlay'] == [r for r in expected['links'] if r['link_type'] == 'overlay'] and eq('refinements'),
        'AUDIT_COMPLETE': eq('audit'),
    }
    return [{'gate_id': k, 'status': 'PASS' if v else 'FAIL'} for k, v in checks.items()]


def csv_bytes(rows):
    fields = sorted({k for r in rows for k in r})
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator='\n')
    writer.writeheader()
    for r in rows:
        writer.writerow({k: canonical_json(v) if isinstance(v, (dict, list, tuple, bool)) else v for k, v in r.items()})
    return stream.getvalue().encode('utf-8')


def manifest_ok(files):
    try:
        rows = list(csv.DictReader(io.StringIO(files['99_manifest_sha256.csv'].decode('utf-8'))))
        return len(rows) == len(files) - 1 and {r['file'] for r in rows} == set(files) - {'99_manifest_sha256.csv'} and all(
            sha(files[r['file']]) == r['sha256'] and len(files[r['file']]) == int(r['bytes']) for r in rows)
    except (KeyError, ValueError):
        return False


def manifest_gate(files):
    return {'gate_id': 'OUTPUT_MANIFEST_INTEGRITY',
            'status': 'PASS' if manifest_ok(files) else 'FAIL'}


def add_manifest(files):
    files['99_manifest_sha256.csv'] = csv_bytes([
        {'file': n, 'sha256': sha(b), 'bytes': len(b)}
        for n, b in sorted(files.items()) if n != '99_manifest_sha256.csv'])


def serialize(model):
    checks = gates(model)
    if any(g['status'] != 'PASS' for g in checks):
        raise ValueError('Invariant gates failed: ' + pretty(checks))
    files = {name: csv_bytes(model[k]) for k, name in FILES.items()}
    files['07_human_readable_signature_catalog.md'] = model['catalog'].encode('utf-8')
    files['08_five_case_validation.md'] = model['five_cases'].encode('utf-8')
    files['10_method_note.md'] = (VERSION + ': non-analytical provenance sidecar. Atom cumulative named components are canonical JSON; '
        'window/family/refinement preimages contain level, length and ordered reconstructed atom hashes. '
        'UTF-8 SHA256, ensure_ascii=False, sort_keys=True, compact separators. '
        'No historical target hash is used as reconstruction input. Component JSON comes from R2.2. '
        'Human fields remain in unchanged source rows. Sequence extension is overlay only. '
        'Missing explicit mappings are NOT_AVAILABLE_FROM_SOURCE. All source locators use one-based data rows. '
        'Keep every source archive: raw relations and boundary evidence remain accessible through original '
        'source rows and the R3c.3 metadata evidence references. No R1/BHSA/R2.2 execution or analytical mutation.\n').encode('utf-8')
    meta = {'version': VERSION, 'mode': model['source']['mode'], 'input_sha256': model['source']['hashes'],
            'source_metadata': model['source']['source_metadata'],
            'counts': {k: len(model[k]) for k in FILES}, 'gate_count': len(checks) + 1,
            'sampling': 'NONE', 'generator_executed': False}
    files['90_run_metadata.json'] = (pretty(meta) + '\n').encode('utf-8')
    # Compute the manifest gate from real bytes, then seal its recorded result.
    files['09_gates.csv'] = csv_bytes(checks)
    add_manifest(files)
    result = manifest_gate(files)
    if result['status'] != 'PASS':
        raise ValueError('OUTPUT_MANIFEST_INTEGRITY')
    checks.append(result)
    files['09_gates.csv'] = csv_bytes(checks)
    add_manifest(files)
    if manifest_gate(files)['status'] != 'PASS':
        raise ValueError('OUTPUT_MANIFEST_INTEGRITY')
    return files


def write(model, output):
    files = serialize(model)
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    for name, blob in files.items():
        (out / name).write_bytes(blob)
    if not manifest_ok({p.name: p.read_bytes() for p in out.iterdir()}):
        raise ValueError('OUTPUT_MANIFEST_INTEGRITY after write')
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--output-dir')
    for key in EXPECTED:
        parser.add_argument('--' + key, type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        from milal_prov1_synthetic import synthetic_source
        model = build(synthetic_source())
        if args.output_dir:
            write(model, args.output_dir)
        else:
            serialize(model)
        print('PROV1 synthetic self-test: 22/22 gates PASS')
        return 0
    if not args.output_dir or any(getattr(args, k) is None for k in EXPECTED):
        parser.error('All five inputs and a fresh --output-dir are required')
    write(build(load({k: getattr(args, k) for k in EXPECTED})), args.output_dir)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
