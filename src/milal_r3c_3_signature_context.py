"""R3c.3: source-traceable structural evidence; never decode opaque signatures."""
from __future__ import annotations

import argparse
import copy
import csv
import io
import json
from collections import Counter
from pathlib import Path, PurePosixPath
import re
import tempfile
import zipfile

import milal_r3c_2_compact_review as prior

REVIEW_FIELDS = prior.REVIEW_FIELDS
AVAILABLE = 'AVAILABLE_FROM_SOURCE'
DERIVED = 'DERIVABLE_FROM_EXPLICIT_SOURCE_FIELDS'
MISSING = 'NOT_AVAILABLE_FROM_SOURCE'
VERSION = 'R3c.3'
CONTROLS = ('CASE001', 'CASE007', 'CASE013', 'CASE019', 'CASE025')
# Discriminating column sets, not archive filenames. Ambiguity is an error.
ROLES = {
    'field_definitions': ('b2', ('field', 'definition')),
    'bundles': ('b2', ('bundle_id', 'geometry_sha256', 'representative_family_id')),
    'families': ('b2', ('bundle_id', 'family_id', 'level', 'signature_hash', 'is_representative')),
    'profiles': ('b2', ('bundle_id', 'profile_layer', 'profile_payload_json', 'profile_sha256')),
    'members': ('b3', ('bundle_id', 'lineage_id', 'parent_bundle_id', 'refinement_depth')),
    'edges': ('b3', ('lineage_id', 'parent_bundle_id', 'child_bundle_id', 'parent_family_id', 'child_family_id', 'child_signature_hash')),
    'events': ('b3', ('parent_bundle_id', 'parent_family_id', 'child_level', 'mapped_g6_singleton_review_item_id')),
    'items': ('b2', ('review_item_id', 'signature_G6', 'first_unique_level', 'left1_ref')),
    'links': ('b3', ('review_item_id', 'signature_G6', 'first_unique_level', 'parent_bundle_id_at_first_unique')),
}
BUNDLE_FIELDS = ('bundle_id', 'lineage_id', 'levels_present', 'lowest_level', 'highest_level',
                 'representative_family_id', 'member_family_count', 'member_family_ids',
                 'occurrence_count', 'refinement_depth', 'parent_bundle_id', 'geometry_sha256', 'representative_level')
SINGLE_FIELDS = ('first_unique_level', 'signature_G6', 'parent_bundle_id_at_first_unique',
                 'lineage_id', 'mapped_g6_singleton_review_item_id')
PROFILE_LAYERS = ('P0_POSITIONAL', 'P1_BHSA', 'P2_COARSE_FLANK', 'P3_LEXICAL_FLANK', 'FORENSIC_EXACT')


def read_archive(path):
    path = Path(path)
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as z:
        names = [i.filename for i in z.infolist() if not i.is_dir()]
        if len(names) != len(set(names)) or any(PurePosixPath(n).is_absolute() or '..' in PurePosixPath(n).parts or '\\' in n or ':' in n for n in names):
            raise ValueError('Unsafe or duplicate ZIP member paths')
        if z.testzip() is not None:
            raise ValueError('ZIP integrity failure')
        files = {n: z.read(n) for n in names}
    return {'name': path.name, 'sha256': prior.sha(blob), 'files': files}


def member(archive, basename):
    matches = [n for n in archive['files'] if PurePosixPath(n).name == basename]
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one {basename}: {matches}')
    return matches[0]


def rows(archive, basename):
    name = member(archive, basename)
    return prior.csv_read(archive['files'][name], name)[1]


def manifest_valid(archive):
    try:
        name = member(archive, '99_manifest_sha256.csv')
        prefix = name[:-len('99_manifest_sha256.csv')]
        table = rows(archive, '99_manifest_sha256.csv')
        names = [prefix + r['file'] for r in table]
        return len(names) == len(set(names)) and set(names) == set(archive['files']) - {name} and all(
            prior.sha(archive['files'][prefix + r['file']]) == r['sha256'] and
            str(len(archive['files'][prefix + r['file']])) == r['bytes'] for r in table)
    except (KeyError, ValueError):
        return False


def source_metadata(archive):
    return json.loads(archive['files'][member(archive, '90_run_metadata.json')].decode('utf-8-sig'))


def inventory(archives):
    result = []
    for role, archive in sorted(archives.items()):
        for name, data in sorted(archive['files'].items()):
            fields, table = prior.csv_read(data, name) if name.endswith('.csv') else ([], [])
            result.append({'archive_role': role, 'archive_sha256': archive['sha256'], 'member': name,
                           'sha256': prior.sha(data), 'bytes': len(data), 'columns': fields, 'row_count': len(table)})
    return result


def discover(archives):
    found = {}
    for role, (archive_key, columns) in ROLES.items():
        archive = archives[archive_key]
        matches = []
        for name, data in archive['files'].items():
            if name.endswith('.csv'):
                fields, table = prior.csv_read(data, name)
                if set(columns) <= set(fields):
                    matches.append((name, table))
        if len(matches) > 1:
            raise ValueError(f'Ambiguous source schema for {role}')
        found[role] = []
        if matches:
            name, table = matches[0]
            found[role] = [{'archive_role': archive_key, 'archive_sha256': archive['sha256'],
                            'member': name, 'data_row': i, 'row': r} for i, r in enumerate(table, 1)]
    if not found['bundles'] or not found['members']:
        raise ValueError('Required bundle identity/genealogy schema missing')
    for role in ('bundles', 'members'):
        ids = [r['row']['bundle_id'] for r in found[role]]
        if len(ids) != len(set(ids)) or not all(ids):
            raise ValueError(f'Duplicate/blank bundle identity in {role}')
    return found


def cell(records, field):
    evidence = [{**{k: r[k] for k in ('archive_role', 'archive_sha256', 'member', 'data_row')},
                 'column': field, 'value': r['row'][field]} for r in records if field in r['row'] and r['row'][field] != '']
    return {'status': AVAILABLE if evidence else MISSING, 'evidence': evidence}


def unavailable():
    return {'status': MISSING, 'evidence': []}


def bundle_definition(bid, tables):
    records = [r for role in ('bundles', 'members') for r in tables[role] if r['row']['bundle_id'] == bid]
    if not records:
        raise ValueError(f'Unresolved source bundle {bid}')
    fields = {f: cell(records, f) for f in BUNDLE_FIELDS}
    for field in BUNDLE_FIELDS:
        values = {e['value'] for e in fields[field]['evidence']}
        if len(values) > 1:
            raise ValueError(f'Conflicting source bundle field {bid}/{field}')
    families = [r for r in tables['families'] if r['row']['bundle_id'] == bid]
    profiles = [r for r in tables['profiles'] if r['row']['bundle_id'] == bid]
    for r in profiles:
        if not isinstance(json.loads(r['row']['profile_payload_json']), dict):
            raise ValueError('Profile payload must be a JSON object')
    fields['family_signature_hash'] = cell(families, 'signature_hash')
    fields['family_level_description'] = cell(families, 'level_description')
    definitions = [r for r in tables['field_definitions'] if r['row']['field'] in ('review_bundle', 'geometry_sha256', 'representative_family_id')]
    fields['bundle_equivalence_definition'] = cell(definitions, 'definition')
    # The inspected archive contract supplies hashes, not preimages. Context
    # profile payloads are distributions and never substituted for membership.
    fields['membership_signature_payload'] = unavailable()
    for layer in PROFILE_LAYERS:
        fields[layer] = cell([r for r in profiles if r['row']['profile_layer'] == layer], 'profile_payload_json')
    return {'bundle_id': bid, 'fields': fields, 'source_rows': records + families + profiles + definitions}


def value(definition, field):
    evidence = definition['fields'][field]['evidence']
    return evidence[0]['value'] if evidence else ''


def singleton_definition(uid, source1, tables):
    provenance = [r for r in rows(source1, '06_object_provenance.csv') if r['object_id'] == uid]
    records = []
    for r in provenance:
        raw = json.loads(r['source_row_json'])
        for role in ('events', 'items', 'links'):
            for candidate in tables[role]:
                if candidate['row'] == raw and candidate not in records:
                    records.append(candidate)
    if not records:
        raise ValueError(f'No explicit singleton provenance resolves: {uid}')
    parents = sorted({r['row'][f] for r in records for f in ('parent_bundle_id', 'parent_bundle_id_at_first_unique') if r['row'].get(f)})
    return {'unit_id': uid, 'fields': {f: cell(records, f) for f in SINGLE_FIELDS},
            'uniqueness_feature_payload': unavailable(), 'parent_bundle_ids': parents, 'source_rows': records}


def deltas(definitions, tables):
    result = []
    for bid, definition in sorted(definitions.items()):
        parent = value(definition, 'parent_bundle_id')
        if not parent or parent not in definitions:
            continue
        edges = [r for r in tables['edges'] if r['row']['parent_bundle_id'] == parent and r['row']['child_bundle_id'] == bid]
        comparisons = []
        for edge in edges:
            r = edge['row']
            for field, left, right in (('level', 'parent_level', 'child_level'), ('family_id', 'parent_family_id', 'child_family_id')):
                if left in r and right in r:
                    comparisons.append({'field': field, 'parent': r[left], 'child': r[right],
                                        'change': 'unchanged' if r[left] == r[right] else 'changed', 'source': edge})
            parent_family = [x for x in tables['families'] if x['row']['family_id'] == r['parent_family_id'] and x['row']['bundle_id'] == parent]
            child_family = [x for x in tables['families'] if x['row']['family_id'] == r['child_family_id'] and x['row']['bundle_id'] == bid]
            if len(parent_family) == len(child_family) == 1:
                a, b = parent_family[0]['row']['signature_hash'], child_family[0]['row']['signature_hash']
                if b != r['child_signature_hash']:
                    raise ValueError('Edge/family child signature mismatch')
                comparisons.append({'field': 'signature_hash', 'parent': a, 'child': b,
                                    'change': 'unchanged' if a == b else 'changed', 'source': [edge, *parent_family, *child_family]})
        result.append({'bundle_id': bid, 'parent_bundle_id': parent,
                       'status': DERIVED if comparisons else MISSING, 'comparisons': comparisons,
                       'feature_payload_delta': unavailable(), 'source_rows': edges})
    return result


def distribution(case, evidence):
    selected = [r for r in evidence if r['case_id'] == case['case_id']]
    chapters = Counter()
    for r in selected:
        match = re.search(r'(\d+):\d+$', r['ref_start'])
        if not match:
            raise ValueError(f'Unparseable explicit reference {r["ref_start"]}')
        chapters[match[1]] += 1
    contexts = Counter(r['context_id'] for r in selected)
    return {'case_id': case['case_id'], 'status': DERIVED, 'evidence_row_count': len(selected),
            'unique_context_count': len(contexts), 'unique_surface_count': len({r['surface_text'] for r in selected}),
            'start_chapter_distribution': dict(sorted(chapters.items())),
            'contexts_with_multiple_evidence_rows': {k: v for k, v in sorted(contexts.items()) if v > 1},
            'span_length_distribution': MISSING}


def derive(archives):
    source2, source1 = archives['c2'], archives['c1']
    tables = discover(archives)
    cases = rows(source2, '02_review_cases.csv')
    evidence = rows(source2, '03_compact_evidence_index.csv')
    boundary = rows(source2, '07_boundary_evidence_index.csv')
    target_ids = {r['unit_id'] for r in cases if r['unit_id']} | {r['unit_id'] for r in boundary}
    singletons = [singleton_definition(uid, source1, tables) for uid in sorted(target_ids) if uid.startswith(('G6:', 'EVENT:'))]
    bundle_ids = {uid.removeprefix('BUNDLE:') for uid in target_ids if uid.startswith('BUNDLE:')}
    bundle_ids.update(p for r in singletons for p in r['parent_bundle_ids'])
    definitions = {bid: bundle_definition(bid, tables) for bid in sorted(bundle_ids)}
    for definition in list(definitions.values()):
        parent = value(definition, 'parent_bundle_id')
        if parent and parent not in definitions:
            definitions[parent] = bundle_definition(parent, tables)
    delta = deltas(definitions, tables)
    panel = [{'case_id': c['case_id'], 'unit_ids': sorted({r['unit_id'] for r in boundary if r['case_id'] == c['case_id']})}
             for c in cases if c['case_type'] == 'BOUNDARY_CONTROL']
    # Every original member is referenced by exact bytes/hash; all original rows
    # remain in the required retained source archive, including overlays.
    references = [{'member': n, 'sha256': prior.sha(data), 'bytes': len(data), 'archive_sha256': source2['sha256']}
                  for n, data in sorted(source2['files'].items())]
    readiness = []
    for c in cases:
        ids = [c['unit_id']] if c['unit_id'] else next(p['unit_ids'] for p in panel if p['case_id'] == c['case_id'])
        parent_ids = {value(definitions[uid[7:]], 'parent_bundle_id') for uid in ids if uid.startswith('BUNDLE:')}
        parent_ids.update(p for s in singletons if s['unit_id'] in ids for p in s['parent_bundle_ids'])
        parent_ids.discard('')
        readiness.append({'case_id': c['case_id'], 'structural_definition_available': MISSING,
            'structural_metadata_available': AVAILABLE if ids else MISSING,
            'parent_definition_available': MISSING if parent_ids else 'NOT_APPLICABLE',
            'parent_metadata_available': AVAILABLE if parent_ids else 'NOT_APPLICABLE',
            'parent_child_delta_available': DERIVED if any(d['bundle_id'] in {u[7:] for u in ids if u.startswith('BUNDLE:')} and d['status'] == DERIVED for d in delta) else MISSING,
            'singleton_uniqueness_definition_available': MISSING if any(u.startswith(('G6:', 'EVENT:')) for u in ids) else 'NOT_APPLICABLE',
            'context_evidence_available': AVAILABLE if any(r['case_id'] == c['case_id'] for r in evidence + boundary) else MISSING})
    return {'cases': cases, 'bundles': list(definitions.values()), 'deltas': delta, 'singletons': singletons,
            'boundary': panel, 'distribution': [distribution(c, evidence + boundary) for c in cases],
            'readiness': readiness, 'references': references, 'inventory': inventory(archives)}


def render(model):
    lines = ['# MILAL R3c.3 — Structural Signature Context', '',
             'Source metadata and context distributions do not decode membership signature hashes.',
             'Full occurrences, contexts, raw relations and overlays remain in the verified R3c.2 ZIP.',
             'See 90_run_metadata.json for every source member hash and archive identity.', '']
    bundles = {r['bundle_id']: r for r in model['bundles']}
    singles = {r['unit_id']: r for r in model['singletons']}
    for case in model['cases']:
        cid = case['case_id']
        ids = [case['unit_id']] if case['unit_id'] else next(r['unit_ids'] for r in model['boundary'] if r['case_id'] == cid)
        lines += [f'## {cid}', '', '### Why this review unit exists', '',
                  'Membership feature values / exact uniqueness cause: NOT_AVAILABLE_FROM_SOURCE.',
                  'Hashes identify source signatures; they do not disclose the hashed feature values.', '']
        for uid in ids:
            lines += [f'#### {prior.text(uid)}']
            definition = bundles[uid[7:]] if uid.startswith('BUNDLE:') else singles[uid]
            for field, evidence in definition['fields'].items():
                if field in PROFILE_LAYERS:
                    lines.append(f'- Context distribution {field}: {evidence["status"]}; {len(evidence["evidence"])} raw profile rows in 03_bundle_definition_context.csv (not membership criteria).')
                    payloads = [json.loads(e['value']) for e in evidence['evidence']]
                    feature_values = {key: sorted({prior.canonical(p[key]) for p in payloads if key in p}) for key in sorted({k for p in payloads for k in p})}
                    lines.append('  - Explicit profile field/value sets: ' + prior.text(prior.canonical(feature_values)))
                else:
                    vals = sorted({e['value'] for e in evidence['evidence']})
                    lines.append(f'- {field}: {prior.text(" | ".join(vals)) if vals else evidence["status"]}')
            parents = [value(definition, 'parent_bundle_id')] if uid.startswith('BUNDLE:') else definition['parent_bundle_ids']
            for parent in filter(None, parents):
                pd = bundles[parent]
                lines += [f'- Parent {prior.text(parent)}: levels {prior.text(value(pd, "levels_present"))}; representative family {prior.text(value(pd, "representative_family_id"))}; complete source definition in 03_bundle_definition_context.csv.']
            for d in model['deltas']:
                if uid == 'BUNDLE:' + d['bundle_id']:
                    lines += [f'- Parent → child source-field delta: {d["status"]}; feature-payload delta: {MISSING}.']
                    for comparison in d['comparisons']:
                        lines.append(f'  - {comparison["field"]}: {prior.text(comparison["parent"])} → {prior.text(comparison["child"])} ({comparison["change"]}).')
        diagnostic = next(r for r in model['distribution'] if r['case_id'] == cid)
        lines += ['', '### Distribution diagnostics', prior.text(prior.canonical(diagnostic)), '',
                  '### Occurrence/context evidence',
                  f'Open case {cid} in the verified source ZIP: 09_review_packet_compact.md. All rows remain in its evidence/context/boundary indexes; no representative replaces this case.', '',
                  '### Human review']
        lines += [f'- {field}: {prior.text(case[field])}' for field in REVIEW_FIELDS]
        lines.append('')
    return '\n'.join(lines) + '\n'


def source_checks(archives):
    a, b = archives['c2'], archives['c1']
    meta = source_metadata(a)
    recorded = dict(meta['source_r3c1_metadata']['input_archives'])
    inv = rows(b, '01_source_schema_inventory.csv')
    def match(role, source_role):
        candidates = {r['input_zip_sha256'] for r in inv if r['source'] == source_role}
        selected = [r for r in inv if r['source'] == source_role]
        return candidates == {archives[role]['sha256']} and all(recorded.get(r['input_archive']) == r['input_zip_sha256'] for r in selected)
    return {'SOURCE_R3C2_MANIFEST_VALID': manifest_valid(a),
            'R3B2_SHA_MATCHES_RECORDED_SOURCE': match('b2', 'items'),
            'R3B3_SHA_MATCHES_RECORDED_SOURCE': match('b3', 'members'),
            'SOURCE_CHAIN_VALID': manifest_valid(b) and meta['source_r3c1_zip_sha256'] == b['sha256'] and source_metadata(b) == meta['source_r3c1_metadata'],
            'SOURCE_VERSIONS_AND_GATES_VALID': all(source_metadata(x).get('version') == version and source_metadata(x).get('exit_code') == 0 and not source_metadata(x).get('gate_failures') and
                len(rows(x, '11_gates.csv')) == source_metadata(x).get('gate_count') and all(r['status'] == 'PASS' for r in rows(x, '11_gates.csv')) for x, version in ((a, 'R3c.2'), (b, 'R3c.1')))}


def gates(model):
    actual = model
    expected = derive(model['archives'])
    checks = source_checks(model['archives'])
    equal = lambda key: actual[key] == expected[key]
    bundle_fields = lambda obj, names: [(r['bundle_id'], {k: r['fields'][k] for k in names}) for r in obj['bundles']]
    singleton_fields = lambda obj, field: [(r['unit_id'], r['fields'][field]) for r in obj['singletons']]
    checks.update({
        'REVIEW_CASE_SET_UNCHANGED': equal('cases'),
        'REVIEW_TARGET_IDS_UNCHANGED': [(r['case_id'], r['unit_id']) for r in actual['cases']] == [(r['case_id'], r['unit_id']) for r in expected['cases']],
        'ALL_R3C2_EVIDENCE_REFERENCES_PRESERVED': equal('references'),
        'BUNDLE_DEFINITION_ROWS_TRACE_TO_SOURCE': equal('bundles'),
        'REPRESENTATIVE_FAMILY_IDS_TRACE_TO_SOURCE': bundle_fields(actual, ['representative_family_id']) == bundle_fields(expected, ['representative_family_id']),
        'MEMBER_FAMILY_IDS_TRACE_TO_SOURCE': bundle_fields(actual, ['member_family_ids', 'member_family_count']) == bundle_fields(expected, ['member_family_ids', 'member_family_count']),
        'PARENT_DEFINITION_TRACE_TO_SOURCE': equal('bundles') and [(r['unit_id'], r['parent_bundle_ids']) for r in actual['singletons']] == [(r['unit_id'], r['parent_bundle_ids']) for r in expected['singletons']],
        'PARENT_CHILD_DELTA_USES_SOURCE_FIELDS_ONLY': equal('deltas'),
        'NO_INFERRED_SIGNATURE_WHEN_SOURCE_MISSING': bundle_fields(actual, ['membership_signature_payload']) == bundle_fields(expected, ['membership_signature_payload']) and [s['uniqueness_feature_payload'] for s in actual['singletons']] == [s['uniqueness_feature_payload'] for s in expected['singletons']],
        'SINGLETON_SIGNATURE_TRACE_TO_SOURCE': singleton_fields(actual, 'signature_G6') == singleton_fields(expected, 'signature_G6'),
        'SINGLETON_FIRST_UNIQUE_LEVEL_TRACE_TO_SOURCE': singleton_fields(actual, 'first_unique_level') == singleton_fields(expected, 'first_unique_level'),
        'S02135_PRESERVED': [s for s in actual['singletons'] if s['unit_id'] == 'G6:S02135'] == [s for s in expected['singletons'] if s['unit_id'] == 'G6:S02135'] and any(s['unit_id'] == 'G6:S02135' for s in actual['singletons']),
        'BOUNDARY_OBJECT_SET_PRESERVED': equal('boundary'),
        'EXTENSION_REMAINS_OVERLAY_ONLY': equal('references') and equal('bundles') and equal('singletons'),
        'REVIEW_FIELDS_UNCHANGED': [{f: r[f] for f in REVIEW_FIELDS} for r in actual['cases']] == [{f: r[f] for f in REVIEW_FIELDS} for r in expected['cases']],
        'SOURCE_UNAVAILABLE_VALUES_EXPLICIT': equal('readiness') and equal('bundles') and equal('singletons'),
        'FIVE_ACCEPTANCE_CONTROLS_PRESERVED': all(any(r['case_id'] == cid for r in actual['cases']) and f'## {cid}\n' in actual['packet'] for cid in CONTROLS),
        'DISTRIBUTION_USES_EXPLICIT_EVIDENCE': equal('distribution'),
        'SOURCE_INVENTORY_COMPLETE': equal('inventory'),
        'PACKET_MATCHES_SOURCE_ENRICHMENT': actual['packet'] == render(expected),
    })
    # Exact derived schema comparison catches newly injected interpretation fields,
    # while raw archived rows remain untouched and may contain historical columns.
    checks['NO_AUTOMATIC_FUNCTION_LABELS'] = all(equal(k) for k in expected) and set(actual) == set(expected) | {'archives', 'packet'} and actual['packet'] == render(expected)
    return [prior.check(name, [] if ok else ['Computed source comparison failed'], 'Recomputed from verified source bytes') for name, ok in checks.items()]


def build(archives):
    checks = source_checks(archives)
    if not all(checks.values()):
        raise ValueError(f'Source preflight failed: {[k for k,v in checks.items() if not v]}')
    model = derive(archives)
    model['archives'] = archives
    model['packet'] = render(model)
    return model


def write(model, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    checks = gates(model)
    outputs = [('01_source_signature_inventory.csv', 'inventory'), ('02_review_cases.csv', 'cases'),
               ('03_bundle_definition_context.csv', 'bundles'), ('04_parent_child_structural_delta.csv', 'deltas'),
               ('05_singleton_definition_context.csv', 'singletons'), ('06_distribution_diagnostics.csv', 'distribution'),
               ('07_boundary_definition_context.csv', 'boundary'), ('09_human_review_readiness.csv', 'readiness')]
    for name, key in outputs:
        prior.write_csv(out / name, model[key])
    prior.write_csv(out / '10_gates.csv', checks)
    (out / '08_review_packet_signature_enriched.md').write_text(model['packet'], encoding='utf-8', newline='\n')
    (out / '11_method_note.md').write_text('Evidence enrichment only. Opaque signature hashes are not feature payloads. Context profiles describe distributions, not membership criteria. Delta compares explicit family IDs, levels and hashes only. Missing feature payloads remain NOT_AVAILABLE_FROM_SOURCE. Counts describe evidence rows; singleton source spans are not deduplicated occurrences. Preserve all four input ZIPs for lossless reference resolution. No automatic judgment, resampling, population change, or R4.\n', encoding='utf-8')
    meta = {'version': VERSION, 'sources': {k: {'name': a['name'], 'sha256': a['sha256']} for k, a in model['archives'].items()},
            'r3c2_evidence_references': model['references'], 'case_count': len(model['cases']),
            'gate_count': len(checks), 'gate_failures': [r['gate_id'] for r in checks if r['status'] != 'PASS'],
            'packet_lines': len(model['packet'].splitlines()), 'packet_utf8_bytes': len(model['packet'].encode('utf-8'))}
    (out / '90_run_metadata.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    prior.write_manifest(out)
    return 2 if meta['gate_failures'] else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    for flag in ('r3c2-zip', 'r3c1-zip', 'r3b2-zip', 'r3b3-zip', 'output-dir'):
        parser.add_argument('--' + flag, type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test(args.output_dir)
    if any(getattr(args, f) is None for f in ('r3c2_zip', 'r3c1_zip', 'r3b2_zip', 'r3b3_zip', 'output_dir')):
        parser.error('Four input ZIPs and --output-dir are required; R3c.1 supplies the verified source inventory/provenance.')
    try:
        archives = {key: read_archive(path) for key, path in zip(('c2', 'c1', 'b2', 'b3'), (args.r3c2_zip, args.r3c1_zip, args.r3b2_zip, args.r3b3_zip))}
        return write(build(archives), args.output_dir)
    except (ValueError, KeyError, OSError, zipfile.BadZipFile) as error:
        print(f'ERROR: {error}')
        return 2


def synthetic_sources(root):
    """Archive fixture follows the inspected schemas, with explicit synthetic values."""
    import milal_r3c_1_review_units as first
    tables, config, provider = first.synthetic_fixture()
    for table in tables.values():
        for r in table.rows:
            for field in ('review_item_id', 'mapped_g6_singleton_review_item_id'):
                if r.get(field) == 'S00001':
                    r[field] = 'S02135'
    config['singleton_control']['review_item_id'] = 'S02135'
    root = Path(root)
    bundle_rows, families, profiles, edge_rows = [], [], [], []
    for r in tables['members'].rows:
        bid = r['bundle_id']
        r.update(representative_family_id='F' + bid, member_family_count='1', member_family_ids='F' + bid)
        bundle_rows.append({**r, 'geometry_sha256': prior.sha(bid.encode())})
        families.append({'bundle_id': bid, 'family_id': 'F' + bid, 'level': r['lowest_level'], 'level_description': 'SYNTH explicit level', 'signature_hash': prior.sha(bid.encode()), 'is_representative': '1'})
        for layer in PROFILE_LAYERS:
            payload = '{"synthetic_flag":1}'
            profiles.append({'bundle_id': bid, 'profile_layer': layer, 'profile_payload_json': payload, 'profile_sha256': prior.sha(payload.encode()), 'source_representative_family_id': 'F' + bid})
        if r['parent_bundle_id']:
            edge_rows.append({'lineage_id': r['lineage_id'], 'parent_bundle_id': r['parent_bundle_id'], 'child_bundle_id': bid,
                              'parent_family_id': 'F' + r['parent_bundle_id'], 'child_family_id': 'F' + bid,
                              'parent_level': 'G0', 'child_level': r['lowest_level'], 'child_signature_hash': prior.sha(bid.encode())})
    for r in tables['items'].rows:
        r.update(first_unique_level='G3', signature_G6=prior.sha(r['review_item_id'].encode()), left1_ref='SYNTH')
    for r in tables['links'].rows:
        r.update(first_unique_level='G3', signature_G6=prior.sha(r['review_item_id'].encode()))
    for r in tables['events'].rows:
        r.setdefault('parent_family_id', 'F' + r['parent_bundle_id'])
    b2_roles = {'occurrences', 'items'}
    paths = {}
    for key in ('b2', 'b3'):
        folder = root / key
        folder.mkdir()
        for role, table in tables.items():
            if (role in b2_roles) == (key == 'b2'):
                table.fields = sorted(set(table.fields) | {f for r in table.rows for f in r})
                prior.write_csv(folder / table.name, table.rows, table.fields)
        extras = [('definitions.csv', bundle_rows), ('families.csv', families), ('profiles.csv', profiles),
                  ('field_definitions.csv', [{'field': 'review_bundle', 'definition': 'SYNTH same explicit occurrence geometry'}])] if key == 'b2' else [('edges.csv', edge_rows)]
        for name, data in extras:
            prior.write_csv(folder / name, data)
        path = root / (key + '.zip')
        zip_folder(folder, path)
        paths[key] = path
        for role, table in tables.items():
            if (role in b2_roles) == (key == 'b2'):
                table.archive_name, table.zip_sha256 = path.name, prior.sha(path.read_bytes())
    first.write_outputs(first.build_model(tables, config, provider), root / 'c1')
    paths['c1'] = root / 'c1.zip'
    zip_folder(root / 'c1', paths['c1'])
    prior.write_outputs(prior.build_model(prior.read_source(paths['c1'])), root / 'c2')
    paths['c2'] = root / 'c2.zip'
    zip_folder(root / 'c2', paths['c2'])
    return paths


def zip_folder(folder, target):
    with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(Path(folder).iterdir()):
            if p.is_file():
                z.write(p, p.name)


def self_test(output=None):
    with tempfile.TemporaryDirectory(prefix='milal_r3c3_') as tmp:
        paths = synthetic_sources(Path(tmp))
        model = build({k: read_archive(p) for k, p in paths.items()})
        status = write(model, output or Path(tmp) / 'enriched')
        if status:
            raise ValueError('Synthetic gates failed')
        if output:
            # Retain exact source bytes outside the manifest tree for auditability.
            for key, path in paths.items():
                with Path(str(output) + '_' + key + '.zip').open('xb') as stream:
                    stream.write(path.read_bytes())
        print(f'SELF-TEST PASS: {len(gates(model))} gates; {len(model["cases"])} cases; {len(model["packet"].splitlines())} lines / {len(model["packet"].encode("utf-8"))} UTF-8 bytes')
        return 0


if __name__ == '__main__':
    raise SystemExit(main())
