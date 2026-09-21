"""Small independent source archives for HR1; never a substitute for real inputs."""
import io
import json
from pathlib import Path
import zipfile

import milal_hr1_adjudication_linkage as hr


def archive(files):
    files = dict(files)
    hr.prov.add_manifest(files)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as z:
        for name, blob in sorted(files.items()):
            info = zipfile.ZipInfo('synthetic/' + name, (2020, 1, 1, 0, 0, 0))
            z.writestr(info, blob)
    return buffer.getvalue()


def source_fixture():
    human = (Path(__file__).resolve().parents[1] / hr.HUMAN_PATH).read_bytes()
    cases, bundles, singles, boundaries, families, deltas, items = [], [], [], [], [], [], []
    summaries = {}
    for i, h in enumerate(hr.read_csv(human), 1):
        cid = h['case_id']
        targets = []
        numbers = [i] if i <= 24 else [1, 19, 21]
        for n in numbers:
            if n <= 18:
                targets.append(dict(unit_id=f'B{n}', unit_type='REPEATED_BUNDLE', bundle_id=f'B{n}', lineage_id=f'L{n}'))
            else:
                targets.append(dict(unit_id=f'U{n}', unit_type='SINGLETON_OUTCOME_UNIT',
                                    review_item_id='' if n in (21, 24) else f'S{n}', lineage_id=f'L{n}'))
        summaries[cid] = targets
        cases.append(dict(case_id=cid, case_type=h['case_type'], unit_id=targets[0]['unit_id'] if i <= 24 else '',
                          unit_type=targets[0]['unit_type'] if i <= 24 else '', boundary_ref='' if i <= 24 else f'SYNTHETIC:{i}',
                          target_summaries=hr.canonical(targets)))
        if i >= 25:
            boundaries.append(dict(case_id=cid, unit_ids=hr.canonical([s['unit_id'] for s in targets])))
    for i in range(1, 19):
        bundles.append(dict(bundle_id=f'B{i}', source_rows='[]'))
        families.append(dict(family_id=f'F{i}', bundle_ids=hr.canonical([f'B{i}']), positions='[]',
                             occurrences='[]', historical_hash=hr.sha(f'family{i}'.encode())))
    for i in range(19, 25):
        event = dict(parent_family_id=f'F{i}', child_level='G3', child_signature_hash=hr.sha(f'event{i}'.encode()), exemplar_window_id=f'W{i}')
        ref = dict(archive_role='b2', archive_sha256='synthetic', member='events.csv', data_row=i, row=event)
        singles.append(dict(unit_id=f'U{i}', source_rows=hr.canonical([ref])))
        deltas.append(dict(parent_family_id=f'F{i}', child_family_id=hr.NA, source=hr.canonical(dict(source_row=event)), historical_hash=event['child_signature_hash']))
        if i not in (21, 24):
            items.append(dict(atom_node=str(i), review_item_ids=hr.canonical([f'S{i}']), first_unique_level='G3', atom_hashes='[]'))
    cfiles = {name:hr.prov.csv_bytes(rows) for name, rows in [
        ('02_review_cases.csv',cases), ('03_bundle_definition_context.csv',bundles),
        ('05_singleton_definition_context.csv',singles), ('07_boundary_definition_context.csv',boundaries)]}
    cfiles['10_gates.csv'] = hr.prov.csv_bytes([dict(gate_id='SYNTHETIC_SOURCE',status='PASS')])
    cfiles['90_run_metadata.json'] = hr.canonical(dict(version='R3c.3',gate_count=1)).encode()
    cblob = archive(cfiles)
    cross = []
    for i, c in enumerate(cases, 1):
        for s in summaries[c['case_id']]:
            anchor = dict(archive_sha256=hr.sha(cblob), member='synthetic/02_review_cases.csv',
                          member_sha256=hr.sha(cfiles['02_review_cases.csv']), data_row=i, source_row=c)
            cross.append(dict(link_type='review_unit', layer='R3c.3', case_id=c['case_id'], review_unit_id=s['unit_id'], source=hr.canonical(anchor), summary=hr.canonical(s)))
    for s in singles:
        cross.append(dict(link_type='review_unit_source', layer='R3c.3', review_unit_id=s['unit_id'], source='{}', upstream_source=json.loads(s['source_rows'])[0]))
        cross[-1]['upstream_source'] = hr.canonical(cross[-1]['upstream_source'])
    for i in range(7, 12):
        cross.append(dict(link_type='overlay', layer='SEQUENCE_EXTENSION_OVERLAY_ONLY', source=hr.canonical(dict(source_row=dict(short_bundle_id=f'B{i}',long_bundle_id=f'B{i+1}',relation='EXTENDS_RIGHT')))))
    for i in range(1,19):
        cross.append(dict(link_type='members',layer='b2',source=hr.canonical(dict(source_row=dict(bundle_id=f'B{i}',family_id=f'F{i}')))))
    pfiles = {name:hr.prov.csv_bytes(rows) for name,rows in [
        ('02_family_signature_provenance.csv',families),('03_refinement_feature_delta.csv',deltas),
        ('04_singleton_signature_provenance.csv',items),('05_downstream_identity_links.csv',cross)]}
    pfiles['09_gates.csv'] = hr.prov.csv_bytes([dict(gate_id='SYNTHETIC_SOURCE',status='PASS')])
    pfiles['90_run_metadata.json'] = hr.canonical(dict(version='PROV1',gate_count=1,input_sha256=dict(c3=hr.sha(cblob)))).encode()
    blobs = dict(human=human,r3c3=cblob,prov1=archive(pfiles))
    return dict(blobs=blobs,expected_hashes={k:hr.sha(v) for k,v in blobs.items()},committed_human=human,
                source_commit='SYNTHETIC_FIXTURE',expected_commit='SYNTHETIC_FIXTURE',mode='SYNTHETIC')
