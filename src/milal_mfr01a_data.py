"""Exact frozen-table access and stable, structure-neutral serialization."""
import csv
import json
from pathlib import Path
from collections import defaultdict
from milal_mfr_common import require, sha, js, csv_bytes, rows, write

TABLES = {
    'observation': '03_job_surface_observation_inventory.csv',
    'signatures': '04_job_formal_signatures.csv',
    'markers': '05_job_marker_candidates.csv',
    'families': '06_job_marker_family_registry.csv',
    'membership': '07_job_marker_family_membership.csv',
    'force': '08_job_hierarchical_force_evidence.csv',
    'coverage': '09_job_coverage_candidates.csv',
    'nested': '10_job_nested_marker_evidence.csv',
    'relations': '11_job_marker_relation_candidates.csv',
}
OUTPUTS = {
    'audit': '02_raw_family_redundancy_audit.csv',
    'bundles': '03_marker_evidence_bundle_registry.csv',
    'membership': '04_marker_evidence_bundle_membership.csv',
    'lattice': '05_marker_family_lattice.csv',
    'expansion': '06_marker_expansion_relations.csv',
    'profiles': '07_marker_profiles.csv',
    'family_review': '08_family_review_universe.csv',
    'family_archive': '09_family_archive_reference.csv',
    'crosswalk': '10_raw_relation_case_crosswalk.csv',
    'cases': '11_relation_evidence_cases.csv',
    'closures': '12_closure_candidate_audit.csv',
    'closure_review': '13_closure_review_cases.csv',
    'closure_archive': '14_closure_archive.csv',
    'relation_review': '15_relation_review_universe.csv',
    'relation_archive': '16_relation_archive_reference.csv',
    'trace': '17_raw_to_consolidated_traceability.csv',
}

def stream(path):
    csv.field_size_limit(128 * 1024 * 1024)
    with Path(path).open(encoding='utf8', newline='') as f:
        for row in csv.DictReader(f):
            for k, v in row.items():
                if v and (v[0] in '[{' or v in ('true', 'false', 'null')):
                    try: row[k] = json.loads(v)
                    except ValueError: pass
            yield row

def table(path, records):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf8', newline='') as f:
        writer = None
        for r in records:
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=list(r), lineterminator='\n'); writer.writeheader()
            writer.writerow({k: js(v).decode().strip() if isinstance(v, (dict, list, bool)) or v is None else v for k, v in r.items()})
        if writer is None: f.write('empty\n')

def index(records, field):
    out = {}
    for r in records:
        require(field in r and str(r[field]) not in out, 'missing/duplicate identity: ' + field)
        out[str(r[field])] = r
    return out

def load(directory):
    directory = Path(directory)
    d = {k: list(stream(directory / n)) for k, n in TABLES.items() if k != 'signatures'}
    d['m'] = index(d['markers'], 'marker_id'); d['f'] = index(d['families'], 'family_id')
    d['o'] = index(d['observation'], 'clause_id'); d['h'] = index(d['force'], 'marker_id')
    d['c'] = index(d['coverage'], 'coverage_candidate_id'); d['n'] = index(d['nested'], 'nested_evidence_id')
    index(d['relations'], 'relation_candidate_id')
    require(set(d['m']) == set(d['h']), 'force/marker identity mismatch')
    d['signature_views'] = defaultdict(dict)
    clauses = {str(m['clause_id']) for m in d['markers']}
    signature_count = 0
    for r in stream(directory / TABLES['signatures']):
        signature_count += 1
        if r['object_kind'] == 'clause' and str(r['object_id']) in clauses:
            d['signature_views'][str(r['object_id'])][r['resolution']] = r
    d['signature_count'] = signature_count
    actual_membership = {(r['family_id'], r['marker_id']) for r in d['membership']}
    expected_membership = {(f['family_id'], mid) for f in d['families'] for mid in f['marker_ids']}
    require(actual_membership == expected_membership and len(actual_membership) == len(d['membership']), 'family membership not exact')
    marker_families = defaultdict(set)
    for fid, mid in actual_membership: marker_families[mid].add(fid)
    marker_keys = set(d['m'])
    for f in d['families']:
        require(len(set(f['marker_ids'])) == int(f['occurrence_count']) == len(f['marker_ids']), 'family count mismatch')
        require(set(f['marker_ids']) <= marker_keys, 'family marker missing')
    for m in d['markers']:
        require(str(m['clause_id']) in d['o'] and m['clause_atom_ids'], 'marker anchor missing')
        require(set(m['family_ids']) == marker_families[m['marker_id']], 'marker family identity mismatch')
    coverage_keys = set(d['c'])
    for r in d['relations']:
        require(r['source_marker_id'] in d['m'] and r['target_marker_id'] in d['m'], 'relation marker missing')
        require(set(r['coverage_relationship']) <= coverage_keys, 'coverage reference missing')
    d['by_coverage'] = defaultdict(list); d['by_nested'] = defaultdict(list); d['by_relation'] = defaultdict(list)
    for r in d['coverage']: d['by_coverage'][r['marker_id']].append(r)
    for r in d['nested']: d['by_nested'][r['marker_id']].append(r)
    for r in d['relations']:
        for mid in (r['source_marker_id'], r['target_marker_id']): d['by_relation'][mid].append(r['relation_candidate_id'])
    return d

def ref(c): return str(c['book']) + ' ' + str(c['chapter']) + ':' + str(c['verse'])

def features(m):
    return {'Time': int(m['extension_features']['time']), 'Loca': int(m['extension_features']['loca'])}

def summary_raw(d):
    return {**{k: len(d[k]) for k in TABLES if k != 'signatures'},
            'signatures': d['signature_count'], 'atoms': len({a for c in d['observation'] for a in c['clause_atom_ids']})}
