"""Independent release verification against frozen identities and package bytes."""
import argparse
from collections import Counter
import io
import json
from pathlib import Path
import zipfile
import milal_mfr_common as cm
from milal_mfr01b_data import digest,zip_rows,OUTPUTS,HIERARCHY,ACCEPTABLE_CESSATION
from milal_mfr01b_gates import final_gates
from milal_mfr01a_data import stream

def verify(a,b,regression):
    a,b=Path(a),Path(b);receipt=json.loads(Path(regression).read_bytes());ha,hb=digest(a),digest(b);checks=final_gates(ha,hb,receipt);cm.require(all(checks.values()),'external release gates failed')
    out=a.with_name(a.name.removesuffix('_results.zip'));meta=json.loads((out/'90_run_metadata.json').read_bytes());cfg=json.loads((cm.ROOT/'config/mfr_0_1b_job.json').read_bytes())
    cm.require(cm.verify(out,'99_manifest_sha256.csv') and cm.verify(out/'audit','freeze_manifest.csv'),'manifest invalid')
    cm.require(digest(out/'audit/freeze_manifest.csv')==meta['freeze_sha256'],'freeze changed')
    with zipfile.ZipFile(a) as z:
        cm.require(z.testzip() is None,'ZIP CRC');cm.require(set(z.namelist())=={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()},'ZIP file universe')
        import hashlib
        for name in z.namelist():
            h=hashlib.sha256()
            with z.open(name) as f:
                while chunk:=f.read(1024*1024):h.update(chunk)
            cm.require(h.hexdigest()==digest(out/name),'ZIP file bytes '+name)
    cm.require(all(digest(cm.ROOT/p)==h for p,h in cfg['frozen_files'].items()),'frozen code changed')
    cm.require(all(digest(cm.ROOT/p)==h for p,h in meta['code_sha256'].items()),'executed code changed')
    cm.require(digest(cm.ROOT/'config/mfr_0_1b_role_rules.json')==meta['rules_sha256'],'executed rules changed')
    cm.require(digest(out/'mfr01a_frozen_input.zip')==meta['upstream_sha256'],'prior ZIP changed')
    counts={}
    with zipfile.ZipFile(out/'mfr01a_frozen_input.zip') as old:
        raw_bytes=old.read('mfr01_frozen_input.zip');cm.require(cm.sha(raw_bytes)==meta['raw_sha256'],'raw archive changed')
        with zipfile.ZipFile(io.BytesIO(raw_bytes)) as raw:
            for scope in meta['statistics']:
                markers={r['marker_id']:r for r in zip_rows(raw,'blind/'+scope+'/05_job_marker_candidates.csv')};families={r['family_id'] for r in zip_rows(raw,'blind/'+scope+'/06_job_marker_family_registry.csv')}
                roles=list(stream(out/'audit'/scope/OUTPUTS['roles']));bundles=list(stream(out/'audit'/scope/OUTPUTS['bundles']))
                cm.require({r['marker_id'] for r in roles}==set(markers) and len(roles)==len(markers),'marker loss')
                cm.require(all(r['anchor']==markers[r['marker_id']]['anchor'] and r['clause_atom_ids']==markers[r['marker_id']]['clause_atom_ids'] and r['raw_discovery_sources']==markers[r['marker_id']]['discovery_sources'] for r in roles),'source marker identity changed')
                prior={b['bundle_id']:b for b in zip_rows(old,'consolidated/'+scope+'/03_marker_evidence_bundle_registry.csv')}
                cm.require(Counter(f for b in bundles for f in b['raw_family_ids'])==Counter(families),'family ID loss')
                cm.require({b['bundle_id'] for b in bundles}==set(prior) and all(b['marker_ids']==prior[b['bundle_id']]['marker_ids'] and b['raw_family_ids']==prior[b['bundle_id']]['contributing_family_ids'] for b in bundles),'bundle rewritten')
                counts[scope]=dict(markers=len(markers),families=len(families),bundles=len(bundles))
            relations={r['relation_candidate_id']:r for r in zip_rows(raw,'blind/job/11_job_marker_relation_candidates.csv')};members=list(stream(out/OUTPUTS['membership']));cases={c['configuration_case_id']:c for c in stream(out/OUTPUTS['configurations'])}
            cm.require(Counter(m['raw_relation_id'] for m in members)==Counter(relations.keys()),'raw pair loss/duplication')
            for m in members:
                r=relations[m['raw_relation_id']];cm.require(m['raw_candidate_labels']==r['relation_candidates'] and m['source_marker_id']==r['source_marker_id'] and m['target_marker_id']==r['target_marker_id'] and m['raw_relation_id'] in cases[m['configuration_case_id']]['raw_pair_ids'],'pair identity/labels changed')
            hierarchy={rid for rid,r in relations.items() if set(r['relation_candidates'])&HIERARCHY};h=list(stream(out/OUTPUTS['h1']));cm.require({rid for c in h for rid in c['phase_pair_ids']}==hierarchy,'hierarchy pair loss')
            evidence={e['evidence_id']:e for e in stream(out/OUTPUTS['evidence'])};closures=list(stream(out/OUTPUTS['closures']))
            job_roles={r['marker_id']:r for r in stream(out/OUTPUTS['roles'])}
            cm.require({c['raw_relation_id'] for c in closures}=={rid for rid,r in relations.items() if 'CLOSURE_TARGET_CANDIDATE' in r['relation_candidates']},'closure loss')
            for e in evidence.values():
                if e['provenance_family']=='EVID_NESTED_FROM_COVERAGE':cm.require(e['dependency_root_ids']==evidence[e['parent_evidence_ids'][0]]['dependency_root_ids'] and not e['independent_link_usable'],'nested independence invention')
                cm.require(not e['independent_link_usable'] or not any(r.startswith('CESSATION:') for r in e['dependency_root_ids']),'dependent closure evidence')
            for c in closures:
                cm.require(c['source_primary_bearing']==job_roles[c['source_marker_id']]['primary_bearing'],'source role identity')
                cm.require(c['review_eligible']==(c['source_primary_bearing'] and c['target_role'] in ACCEPTABLE_CESSATION and bool(c['independent_evidence_ids'])),'closure eligibility')
                cm.require(all(evidence[i]['independent_link_usable'] for i in c['independent_evidence_ids']),'invented independent link')
    human=list(stream(out/'20_mfr_0_2a_review_cases.csv'));cm.require(all(all(r[k]=='' for k in meta['human_fields']) for r in human),'human prefill')
    cm.require(meta['events']==['ROLE_AND_RELATION_OUTPUTS_FROZEN','CONTROLS_LOADED'],'control chronology')
    cm.require(all(r['status']=='PASS' for r in stream(out/'24_gates.csv')),'run gates failed')
    result=dict(status='PASS',zip_sha256=ha,run_gates=meta['run_gates'],gate_definitions=meta['core_gate_definitions']+meta['release_gate_definitions']+3,release_gates=checks,regression=receipt,
        raw_relations=len(relations),raw_closures=len(closures),hierarchy_pairs=len(hierarchy),h1_cases=len(h),human_cases=len(human),frozen_file_count=len(cfg['frozen_files']),scopes=counts)
    cm.write(out.with_name(out.name+'_independent_verification.json'),cm.js(result));print(json.dumps(result));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('a');p.add_argument('b');p.add_argument('regression');x=p.parse_args();verify(x.a,x.b,x.regression)
