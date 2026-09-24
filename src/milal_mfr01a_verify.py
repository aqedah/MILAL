"""Independent release checks against original archive bytes and row identities."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import milal_mfr_common as cm
from milal_mfr01a_data import stream,OUTPUTS,rows
from milal_mfr01a_gates import final_gates

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()

def verify(a,b,receipt_path):
    a,b=Path(a),Path(b);receipt=json.loads(Path(receipt_path).read_bytes());ha,hb=digest(a),digest(b)
    release=final_gates(ha,hb,receipt);cm.require(all(release.values()),'external release gates failed')
    directory=a.with_name(a.name.removesuffix('_results.zip'));cm.require(cm.verify(directory,'99_manifest_sha256.csv'),'final manifest')
    with zipfile.ZipFile(a) as z:
        names=z.namelist();cm.require(z.testzip() is None and len(names)==len(set(names)),'ZIP integrity')
        cm.require(set(names)=={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()},'archive file set')
        for name in names:
            h=hashlib.sha256()
            with z.open(name) as f:
                while chunk:=f.read(1024*1024):h.update(chunk)
            cm.require(h.hexdigest()==digest(directory/name),'archive bytes: '+name)
    meta=json.loads((directory/'90_run_metadata.json').read_bytes());cfg=json.loads((cm.ROOT/'config/mfr_0_1a_job.json').read_bytes())
    cm.require(digest(directory/'mfr01_frozen_input.zip')==cfg['archive']['sha256'],'frozen upstream ZIP')
    cm.require(all(digest(cm.ROOT/p)==h for p,h in cfg['frozen_files'].items()),'frozen repository')
    cm.require(all(digest(cm.ROOT/p)==h for p,h in meta['code_sha256'].items()),'stage code changed since execution')
    scope_counts={}
    with zipfile.ZipFile(directory/'mfr01_frozen_input.zip') as z:
        for scope in meta['statistics']:
            d=directory/'consolidated'/scope;cm.require(cm.verify(d,'consolidation_manifest.csv'),'consolidation manifest')
            cm.require(digest(d/'consolidation_manifest.csv')==meta['consolidation_freezes'][scope],'freeze changed')
            audit=json.loads((d/'consolidation_metadata.json').read_bytes());cm.require(set(audit['actual_reads'])=={r['source_id'] for r in audit['input_code_receipts']},'readset mismatch')
            cm.require(all(not r['human_dependency'] and not r['structural_dependency'] for r in audit['input_code_receipts']),'input leakage')
            prefix='blind/'+scope+'/'
            rawf={r['family_id']:r for r in rows(z.read(prefix+'06_job_marker_family_registry.csv'))};rawm={r['marker_id'] for r in rows(z.read(prefix+'05_job_marker_candidates.csv'))}
            represented={};bids=set();membership=set()
            for row in stream(d/OUTPUTS['bundles']):
                cm.require(row['bundle_id'] not in bids,'duplicate bundle ID');bids.add(row['bundle_id'])
                for f in row['family_evidence']:
                    cm.require(f['family_id'] not in represented and f==rawf[f['family_id']],'family row changed/duplicated');represented[f['family_id']]=row['bundle_id']
                    cm.require(tuple(sorted(f['marker_ids']))==tuple(row['marker_ids']),'bundle not exact set')
                    membership.update((f['family_id'],mid) for mid in f['marker_ids'])
            cm.require(set(represented)==set(rawf),'family loss')
            original_membership={(r['family_id'],r['marker_id']) for r in rows(z.read(prefix+'07_job_marker_family_membership.csv'))};cm.require(membership==original_membership,'membership loss')
            profiles={r['marker_id'] for r in stream(d/OUTPUTS['profiles'])};cm.require(profiles==rawm,'marker loss')
            cross={r['raw_relation_candidate_id']:r for r in stream(d/OUTPUTS['crosswalk'])};seen=set();crossbook=0
            # Stream large raw relation tables directly from the ZIP.
            import csv,io
            with z.open(prefix+'11_job_marker_relation_candidates.csv') as f:
                for r in csv.DictReader(io.TextIOWrapper(f,encoding='utf8',newline='')):
                    rid=r['relation_candidate_id'];seen.add(rid);crossbook+=r['cross_book']=='true'
                    cm.require(rid in cross and cross[rid]['raw_labels']==json.loads(r['relation_candidates']) and cross[rid]['source_marker_id']==r['source_marker_id'] and cross[rid]['target_marker_id']==r['target_marker_id'],'raw relation lost or changed')
            cm.require(set(cross)==seen,'relation universe differs')
            caseids=set();represented_relations=set();newcross=0
            for r in stream(d/OUTPUTS['cases']):
                caseids.add(r['case_id']);represented_relations.update(r['raw_relation_ids']);newcross+=r['cross_book']
                cm.require(not r['automatic_resolution'] and all(x in bids for x in r['source_bundle_ids']+r['target_bundle_ids']),'case identity or decision')
            cm.require(represented_relations==seen and all(r['case_id'] in caseids for r in cross.values()),'case crosswalk loss')
            traces={}
            for r in stream(d/OUTPUTS['trace']):
                traces.setdefault(r['raw_kind'],set()).add(r['raw_id']);cm.require(set(r['bundle_ids'])<=bids and set(r['marker_profile_ids'])<=profiles and set(r['relation_case_ids'])<=caseids,'trace target missing')
            for kind,name,field in [('coverage','09_job_coverage_candidates.csv','coverage_candidate_id'),('nested','10_job_nested_marker_evidence.csv','nested_evidence_id')]:
                cm.require(traces[kind]=={r[field] for r in rows(z.read(prefix+name))},kind+' evidence loss')
            cm.require(traces['marker']==rawm and traces['family']==set(rawf) and traces['relation']==seen,'raw identity loss')
            scope_counts[scope]=dict(markers=len(rawm),families=len(rawf),bundles=len(bids),relations=len(seen),cases=len(caseids),cross_book_raw=crossbook,cross_book_cases=newcross)
    human=list(stream(directory/'21_mfr_0_2_human_review_cases.csv'));machine={'review_case_id','case_kind','evidence_case_id','marker_ids'}
    cm.require(all(all(v==('UNREVIEWED' if k=='review_status' else '') for k,v in r.items() if k not in machine) for r in human),'human fields filled')
    cm.require(all(r['status']=='PASS' for r in stream(directory/'25_gates.csv')),'run gates')
    events=meta['events'];cm.require(all(events.index(s+'_FREEZE')<events.index('CONTROLS_LOADED') for s in meta['statistics']),'control chronology')
    result=dict(status='PASS',zip_sha256=ha,zip_members=len(names),frozen_pins=len(cfg['frozen_files']),regression=receipt,release_gates=release,scopes=scope_counts,human_cases=len(human),run_gates=meta['run_gates'],gate_definitions=meta['gate_definitions'])
    dest=directory.with_name(directory.name+'_independent_verification.json');cm.write(dest,cm.js(result));print(json.dumps(result));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('a');p.add_argument('b');p.add_argument('regression');a=p.parse_args();verify(a.a,a.b,a.regression)
