"""R4.0 strict accepted-source adapter. Never executes legacy marker/hierarchy code."""
from __future__ import annotations
import json
from pathlib import Path
import subprocess
import io
import zipfile
from pathlib import PurePosixPath
from collections import defaultdict

import milal_hr1_adjudication_linkage as hr
import milal_mr1_surface_marker_provenance as mr

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/r4_0_job.json'
sha, canonical = mr.sha, mr.canonical


def require(condition, message):
    if not condition:
        raise ValueError('R4.0 SOURCE STOP: ' + message)


def member(archive, basename):
    matches = [n for n in archive['files'] if Path(n).name == basename]
    require(len(matches) == 1, 'ambiguous/missing member ' + basename)
    return matches[0]


def table(archive, basename):
    return hr.read_csv(archive['files'][member(archive, basename)])


def metadata(archive):
    return json.loads(archive['files'][member(archive, '90_run_metadata.json')])


def locator(role, archive, name, number, row):
    return dict(archive_role=role, archive_sha256=archive['sha256'], member=member(archive, name),
                member_sha256=archive['member_hashes'][member(archive, name)], data_row=number,
                row_sha256=sha(canonical(row).encode()))


def archive(blob, expected, mr1=False):
    require(sha(blob) == expected, 'exact archive SHA256 mismatch')
    if mr1:
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            names=z.namelist()
            require(len(names)==len(set(names)) and all(not PurePosixPath(n).is_absolute() and '..' not in PurePosixPath(n).parts and '\\' not in n and ':' not in n for n in names),'unsafe/duplicate MR1 members')
            require(z.testzip() is None,'MR1 CRC failure')
            files={n:z.read(n) for n in names}
        require(mr.manifest_ok(files),'MR1 manifest failure')
        result=dict(files=files,sha256=sha(blob))
    else:
        result = hr.read_zip(blob)  # CRC, safe paths, unique names, exact member manifest.
    result['member_hashes'] = {n: sha(b) for n, b in result['files'].items()}
    return result


def atom_list(value):
    return [int(v) for v in value.split('|')]


def load(cfg, paths, tf_data):
    blobs = {k: Path(paths[k]).read_bytes() for k in cfg['sources']}
    for role, blob in blobs.items():
        require(sha(blob) == cfg['sources'][role]['sha256'], role + ' exact SHA256 mismatch')
    committed = subprocess.check_output(['git', 'show', cfg['human_commit'] + ':docs/HUMAN_REVIEW_PILOT_ADJUDICATION.csv'], cwd=ROOT)
    require(committed == blobs['human'], 'human record differs from committed bytes')
    archives = {k: archive(blobs[k], cfg['sources'][k]['sha256'], mr1=k=='mr1') for k in ('mr1','r3c3','prov1','hr1')}
    meta = {k: metadata(a) for k, a in archives.items()}
    for role, gatefile in [('mr1','09_gates.csv'),('r3c3','10_gates.csv'),('prov1','09_gates.csv'),('hr1','09_gates.csv')]:
        gg = table(archives[role], gatefile)
        require(bool(gg) and all(r['status'] == 'PASS' for r in gg), role + ' failed/absent gates')
        if role != 'mr1':
            require(len(gg) == meta[role]['gate_count'], role + ' gate count mismatch')
    require(meta['mr1']['status'] == 'PASS' and meta['mr1']['stage'] == 'MR1.0' and meta['mr1']['execution']['mode'] == 'REAL', 'MR1 not validated real')
    require(all(v['equal'] for v in meta['mr1']['byte_comparison'].values()), 'MR1 byte reproduction not exact')
    for kind, name in [('surface','20_historical_schema_surface.csv'),('csf','21_historical_schema_csf.csv'),('closure','22_historical_schema_closure.csv'),('way0','23_historical_schema_way0.csv')]:
        actual = sha(archives['mr1']['files'][member(archives['mr1'], name)])
        comparison = meta['mr1']['byte_comparison'][kind]
        require(actual == comparison['current_sha256'] == comparison['historical_sha256'], 'MR1 export SHA inconsistency')
    require(all(r['match_status']=='EXACT' and r['identity_equal']=='True' for r in table(archives['mr1'],'06_historical_reproduction_audit.csv')), 'MR1 field/identity mismatch')
    require(meta['prov1']['input_sha256']['c3'] == archives['r3c3']['sha256'], 'PROV1/R3c.3 chain mismatch')
    require(meta['hr1']['input_sha256'] == {k:sha(blobs[k]) for k in ('human','r3c3','prov1')}, 'HR1 chain mismatch')
    require(meta['hr1']['unresolved_links'] == meta['hr1']['ambiguous_links'] == 0, 'HR1 unresolved IDs')
    # Recompute only the frozen non-analytical HR1 linkage to verify all supplied
    # locators and case dependencies, not any frozen analytical classification.
    source = dict(blobs={k:blobs[k] for k in ('human','r3c3','prov1')},
                  expected_hashes=dict(hr.EXPECTED), committed_human=committed,
                  source_commit=cfg['human_commit'], expected_commit=hr.COMMIT, mode='ACCEPTED_REAL')
    derived = hr.derive(source)
    for key, name in hr.OUTPUTS.items():
        require(hr.read_csv(hr.prov.csv_bytes(derived[key])) == table(archives['hr1'],name), 'HR1 exact linkage differs: ' + key)
    mr_cfg = json.loads(mr.CONFIG.read_text(encoding='utf-8'))
    b, execution = mr.load_bhsa(tf_data, mr_cfg)  # API only; no MR1 extraction rerun.
    require(execution['bhsa_version']==cfg['bhsa_version'] and execution['tf_version']==cfg['tf_version'], 'BHSA/TF version mismatch')
    for name, expected in meta['mr1']['execution']['data_hashes'].items():
        local = Path(tf_data) / Path(name).name
        require(sha(local.read_bytes()) == expected, 'current BHSA differs from accepted MR1: ' + local.name)
    atom_index = {a:i for i,a in enumerate(b.atoms)}
    atoms, clauses = {}, {}
    for c in b.clauses:
        aa = b.clause_atoms(c)
        require(bool(aa), 'clause without native atoms')
        clauses[c] = aa
        for a in aa:
            require(a not in atoms, 'ambiguous clause membership')
            sec = b.section(a)
            atoms[a] = dict(atom=a, clause=c, chapter=int(sec[1]), verse=int(sec[2]),
                            ref=b.ref(a), index=atom_index[a], surface=b.text(a))
    require(set(atoms)==set(b.atoms), 'native atom inventory mismatch')
    s = dict(config=cfg, mode='ACCEPTED_REAL', atoms=atoms, clauses=clauses,
             scope=[b.ref(b.verses[0]), b.ref(b.verses[-1])], execution=execution,
             mr_meta=meta['mr1'], markers=[], way0=[], formal=[], singleton_context=[],
             human=hr.read_csv(blobs['human']), cases=derived['cases'], boundaries=derived['boundary'],
             extensions=derived['extensions'], human_evidence=derived['evidence'], human_provenance=derived['provenance'],
             sources=[], verified_hashes={k:sha(v) for k,v in blobs.items()})
    s['manifest_receipts']={}
    for role,a in archives.items():
        name=member(a,'99_manifest_sha256.csv');prefix=name[:-len('99_manifest_sha256.csv')]
        s['manifest_receipts'][role]=dict(actual={n:h for n,h in a['member_hashes'].items() if n!=name},
                                         expected={prefix+r['file']:r['sha256'] for r in table(a,'99_manifest_sha256.csv')})
    for role, path in paths.items():
        s['sources'].append(dict(source_layer=role, path_archive=str(Path(path).resolve()), SHA256=sha(blobs[role]),
                                 status='EXACT_PIN_AND_MANIFEST_VERIFIED' if role!='human' else 'COMMITTED_BYTES_VERIFIED',
                                 role={'mr1':'marker provenance','r3c3':'frozen review evidence','prov1':'R2/R3 explicit formal provenance','hr1':'human exact-case linkage','human':'human adjudication'}[role]))
    for path, digest in execution['data_hashes'].items():
        s['sources'].append(dict(source_layer='BHSA', path_archive=path, SHA256=digest,status='MATCHES_ACCEPTED_MR1',role='canonical textual source'))
    # Cross-check native clause/atom geometry with every MR1 surface membership.
    links = table(archives['mr1'],'05_clause_atom_marker_links.csv')
    native = {int(r['clause']):json.loads(r['ordered_clause_atom_ids']) for r in links if r['kind']=='surface'}
    require(native == clauses, 'MR1 clause/atom membership mismatch')
    surface = table(archives['mr1'],'01_surface_clause_reproduction.csv')
    require({int(r['start_clause']) for r in surface} == set(clauses), 'MR1 surface population mismatch')
    by_event = defaultdict(list)
    for r in links:
        by_event[r['current_event_id']].append(r)
    for kind, name in [('csf','02_csf_reproduction.csv'),('closure','03_explicit_closure_reproduction.csv'),('way0','04_way0_wayhi_reproduction.csv')]:
        for number,r in enumerate(table(archives['mr1'],name),1):
            aa, cc = json.loads(r['clause_atom_ids']), json.loads(r['clause_ids'])
            require(all(c in clauses for c in cc), 'MR1 unresolved clause ID')
            require(aa == list(dict.fromkeys(a for c in cc for a in clauses[c])), 'MR1 event membership mutation')
            ll = by_event[r['current_event_id']]
            require([int(x['clause']) for x in ll] == cc and all(json.loads(x['ordered_clause_atom_ids'])==clauses[int(x['clause'])] for x in ll), 'MR1 event links unresolved')
            h = json.loads(r['historical_projection'])
            event = dict(source_event_id=r['current_event_id'], atom_ids=aa, clause_ids=cc,
                         source_rule_id=r['rule_id'], provenance_locator=locator('mr1',archives['mr1'],name,number,r),
                         subtype=h.get('csf_family',h.get('pattern','WAYHI_POSITIVE')),
                         surface_text=h.get('formula_text',h.get('text','')), historical_projection=h)
            if kind == 'way0':
                require(r['is_wayhi'] in ('True','False'), 'invalid Wayhi classification')
                event['is_wayhi'] = r['is_wayhi']=='True'
                require(event['is_wayhi'] is h['wayhi_meta'], 'Wayhi semantics mutation')
                s['way0'].append(event)
                if not event['is_wayhi']: continue
            event['family']={'csf':'MR1_CSF','closure':'MR1_EXPLICIT_CLOSURE','way0':'MR1_WAYHI_POSITIVE'}[kind]
            s['markers'].append(event)
    # The seven PROV1 levels resolve to actual native atoms, never by text/ref similarity.
    signature_rows = table(archives['prov1'],'01_atom_signature_provenance.csv')
    atom_levels = set()
    for r in signature_rows:
        a = int(r['atom_node']);require(a in atoms,'PROV1 unknown native atom')
        old = json.loads(r['source'])['source_row']
        require(int(old['atom_index_1based'])==atoms[a]['index']+1 and r['ref_start']==atoms[a]['ref'], 'PROV1 native order/reference mismatch')
        key=(a,r['level']);require(key not in atom_levels,'duplicate atom/level');atom_levels.add(key)
        require(r['hash_match']=='true' and r['historical_hash']==r['reconstructed_hash'], 'PROV1 atom hash failure')
    require(atom_levels=={(a,'G'+str(level)) for a in atoms for level in range(7)},'PROV1 incomplete full-book scope')
    families = table(archives['prov1'],'02_family_signature_provenance.csv')
    bundles, occurrence, definitions = defaultdict(list), {}, {}
    for number,f in enumerate(families,1):
        require(f['hash_match']=='true' and f['historical_hash']==f['reconstructed_hash'],'formal family hash mismatch')
        ff=locator('prov1',archives['prov1'],'02_family_signature_provenance.csv',number,f)
        definitions[f['family_id']]=dict(family_id=f['family_id'],level=f['level'],sequence_length=int(f['sequence_length']),
                                         signature_hash=f['historical_hash'],sequence_key=json.loads(f['sequence_key']))
        for bid in json.loads(f['bundle_ids']): bundles[bid].append(f['family_id'])
        for index,o in enumerate(json.loads(f['occurrences'])):
            row=o['source_row'];key=(f['family_id'],row['window_id'])
            require(key not in occurrence,'ambiguous family/window ID')
            occurrence[key]=(row,dict(ff,occurrence_index=index),o)
    used=set()
    for number,r in enumerate(table(archives['prov1'],'05_downstream_identity_links.csv'),1):
        if r['link_type']=='items':
            require(int(r['atom_node']) in atoms,'unresolved singleton atom')
            s['singleton_context'].append(dict(review_item_id=r['review_item_id'],atom=int(r['atom_node']),
                                               provenance_locator=locator('prov1',archives['prov1'],'05_downstream_identity_links.csv',number,r),
                                               trigger_eligible=False,reason='UNIQUENESS_NOT_BOUNDARY_TRIGGER'))
        if r['link_type']!='bundle_occurrences': continue
        source_row=json.loads(r['source'])['source_row'];bid=source_row['bundle_id'];window=source_row['window_id']
        aa=atom_list(source_row['atom_nodes'])
        require(aa and all(a in atoms for a in aa),'unresolved formal atom')
        start=atoms[aa[0]]['index'];end=atoms[aa[-1]]['index']
        require([atoms[a]['index'] for a in aa]==list(range(start,end+1)),'formal window order mismatch')
        require(int(source_row['start_atom'])==aa[0] and int(source_row['end_atom'])==aa[-1],'formal endpoint mismatch')
        require(len(aa)==int(source_row['sequence_length']) and bundles[bid],'formal schema/member mismatch')
        loc=locator('prov1',archives['prov1'],'05_downstream_identity_links.csv',number,r)
        support=[loc];family_ids=sorted(bundles[bid])
        for fid in family_ids:
            key=(fid,window);require(key in occurrence,'unresolved explicit family/window')
            row, floc, upstream=occurrence[key]
            require(atom_list(row['atom_nodes'])==aa,'family/bundle explicit geometry mismatch')
            support.append(floc);used.add(key)
        s['formal'].append(dict(source_event_id=bid+':'+window, bundle_id=bid, window_id=window,family_ids=family_ids,
                               family_signature_definitions=[definitions[fid] for fid in family_ids],
                               atom_ids=aa,surface_text=source_row['surface_text'],provenance_locator=loc,source_locators=support))
    require(used==set(occurrence),'unpreserved formal occurrence provenance')
    s['formal_family_occurrence_count']=len(used)
    return s
