"""Independent release checks, outside the self-hashed result ZIP."""
import argparse
import json
import zipfile
from pathlib import Path
import milal_mfr_common as cm
import milal_mfr02a_core as core
from milal_mfr01b_data import digest
from milal_mfr01b_io import verify_zip,baseline
from milal_mfr02a_pipeline import freeze_valid,code_hashes


def verify(a,b,regression):
    a,b=Path(a),Path(b);ha,hb=digest(a),digest(b)
    ra,rb=verify_zip(a,ha),verify_zip(b,hb)
    receipt=json.loads(Path(regression).read_bytes())
    cfg=json.loads((cm.ROOT/'config/mfr_0_2a_job.json').read_bytes());pins=baseline(cfg)
    cm.require(receipt['code_sha256']==code_hashes(),'Regression source mismatch')
    checks=core.release_gates(receipt,ha==hb,ra['manifest_verified'] and rb['manifest_verified'])
    cm.require(all(checks.values()),str(checks))
    out=a.with_name(a.name.removesuffix('_results.zip'));cm.require(freeze_valid(out),'Freeze invalid')
    with zipfile.ZipFile(a) as z:
        for n in z.namelist():cm.require(cm.sha(z.read(n))==digest(out/n),'ZIP/local mismatch '+n)
        meta=json.loads(z.read('90_run_metadata.json'));cm.require(meta['code_sha256']==code_hashes(),'Executed source mismatch')
        upstream=z.read('mfr01b_frozen_input.zip');cm.require(cm.sha(upstream)==cfg['archive']['sha256'],'Upstream archive changed')
        del upstream
        with zipfile.ZipFile(cm.ROOT/cfg['archive']['path']) as old:
            h1=cm.rows(old.read('13_h1_hierarchy_review_set.csv'))
            attachments={h['configuration_case_id']:json.loads(old.read('case_evidence/'+h['configuration_case_id']+'.json')) for h in h1}
            for cid,attached in attachments.items():cm.require(z.read('evidence/'+cid+'.json')==old.read('case_evidence/'+cid+'.json'),'Evidence attachment modified')
            supplied=json.loads((cm.ROOT/'config/mfr_0_2a_human_decisions.json').read_bytes());expected=core.assemble(supplied,h1,attachments)
            for n,k in zip(core.FREEZE_FILES[:6],('decisions','provenance','crosswalk','calibration','deferred','accepted')):
                cm.require(z.read(n)==cm.csv_bytes(expected[k]),'Human/source serialization mismatch '+n)
            cm.require(json.loads(z.read(core.FREEZE_FILES[6]))==expected['representation'],'Representation changed')
            for n,prior,dim in [('08_mfr_0_2b_resumption_scope.csv','14_r1_resumption_review_set.csv','resumption'),('09_mfr_0_2c_closure_scope.csv','15_c1_closure_review_set.csv','closure')]:
                cm.require(z.read(n)==cm.csv_bytes(core.scope(cm.rows(old.read(prior)),expected['decisions'],dim)),'Deferred scope loss')
        cm.require(meta['events']==['HUMAN_DECISIONS_FROZEN','HISTORICAL_LOADED'],'Historical load chronology')
        cm.require(meta['freeze_sha256']==cm.sha(z.read('14_human_decision_freeze.csv')),'Freeze SHA mismatch')
        cm.require(all(r['status']=='PASS' for r in cm.rows(z.read('11_gates.csv'))),'Run gate failure')
        hcfg=json.loads((cm.ROOT/'config/mfr_0_2a_historical_comparison.json').read_bytes())
        cm.require(digest(cm.ROOT/hcfg['archive'])==hcfg['sha256'] and cm.sha(z.read('historical_source.csv'))==hcfg['member_sha256'],'Historical source changed')
        from milal_mfr02a_history import compare
        cm.require(z.read('06_mfr_0_2a_postfreeze_historical_comparison.csv')==cm.csv_bytes(compare(expected['decisions'],cm.rows(z.read('historical_source.csv')))),'Historical comparison altered')
    result=dict(status='PASS',zip_sha256=ha,regression=receipt,run_gates=meta['run_gates'],release_gates=checks,
        distinct_gate_definitions=meta['run_gates']+len(checks),frozen_files=len(pins),statistics=meta['statistics'])
    cm.write(out.with_name(out.name+'_independent_verification.json'),cm.js(result))
    cm.write(out.with_name(out.name+'_release_gates.csv'),cm.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]))
    print(json.dumps(result));return result


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('a');p.add_argument('b');p.add_argument('regression');x=p.parse_args();verify(x.a,x.b,x.regression)
