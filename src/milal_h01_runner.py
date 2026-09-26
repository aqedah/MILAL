"""Verified-input H0.1 runner, synthetic receipt, independent release and gates."""
import argparse,ast,json
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,physical_path,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_io import verify_archive
from milal_mfr02r_pipeline import code_fingerprint
from milal_q1_runner import verified_input
from milal_q13_pipeline import write
from milal_h01_pipeline import audit
from milal_h01_controls import postfreeze
from milal_h01_validation import gates
from milal_h01_synthetic import cases,self_test
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_h01_job.json'


def ensure_code_unchanged(start_fingerprint):
    if code_fingerprint()!=start_fingerprint:raise ValueError('code/config/tests changed during H0.1 execution')


def evidence(state,out,source,q15,q16r,config,frozen,synth,tests,before,raw_hash):
    _,probes=cases();names=set();literals=set()
    for name in ('model','pipeline','evidence'):
        tree=ast.parse((ROOT/('src/milal_h01_'+name+'.py')).read_text(encoding='utf8'))
        names|={n.id for n in ast.walk(tree) if isinstance(n,ast.Name)}
        literals|={n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)}
    previous=json.loads((q15/'blind_metrics.json').read_text());receipt=json.loads((out/'postfreeze_receipt.json').read_text())
    return dict(baseline=config['baseline'],start_heads=config['verified_start_heads'],frozen_differences=frozen['differences'],input_hashes=before,current_hashes={p.name:digest(p) for p in q16r.iterdir() if p.is_file()},
      raw_count=previous['counts']['raw'],expected=config['expected_input'],raw_hash_before=raw_hash,raw_hash_after=digest(physical_path(source/'blind/job/09_candidate_evidence_matrix.csv')),
      outcomes=state['outcomes'],preserved_outcomes=list(rows(out/'preserved_qualified_relations.csv')),human_count=sum(1 for _ in rows(q15/'preserved_human_judgments.csv')),
      human_hash_before=previous['preserved_hashes']['preserved_human_judgments.csv'],human_hash_after=digest(q15/'preserved_human_judgments.csv'),target_ids=sorted(state['inventory']),
      result=state['result'],probes=probes,sb12=json.loads((q16r/'q13_compatibility_audit.json').read_text())['global_audit']['constraint_rows'],universe=state['universe'],
      role_catalog=[dict(process_id=k,primary_role=p['primary_role']) for k,p in state['catalog']['processes'].items()],packet_roles=json.loads((out/'role_display_contract.json').read_text())['roles'],
      policy_names=sorted(names),core_literals=sorted(literals),diagnostic_ids=config['diagnostic_ids'],new_human_judgments=state['metrics']['new_human_judgments'],cards=state['cards'],
      blind_access=json.loads((out/'blind_access_receipt.json').read_text()),blind_freeze_hashes=receipt['before'],postfreeze_hashes=receipt['after'],
      regression={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint=code_fingerprint(),independent_equal=False,manifest_valid=verify_manifest(out),crc_valid=False)


def run(source,q15,q16,q16r,h0,out,synthetic,regression=None):
    start_fingerprint=code_fingerprint()
    source,q15,q16,q16r,h0,out=map(Path,(source,q15,q16,q16r,h0,out));config=json.loads(CONFIG.read_text());frozen=frozen_check(config)
    synth=json.loads(Path(synthetic).read_text());tests=json.loads(Path(regression).read_text()) if regression else dict(test_scope='NOT_RUN',tests_run=0,failures=0,errors=0,skipped=0)
    if not synth['passed'] or synth['code_fingerprint']!=code_fingerprint():raise ValueError('current synthetic required')
    if regression and (tests.get('code_fingerprint')!=code_fingerprint() or tests.get('test_scope')!='FULL_REGRESSION' or any(tests[k] for k in ('failures','errors','skipped'))):raise ValueError('current full regression required')
    inputs={}
    for k,p in [('source',source),('q15',q15),('q16',q16),('q16r',q16r)]:
        print('H0.1 verify',k,flush=True);inputs[k]=verified_input(p,Path(str(p)+'_results.zip'),config[k+'_zip_sha256'])
    before={p.name:digest(p) for p in q16r.iterdir() if p.is_file()};raw_hash=digest(physical_path(source/'blind/job/09_candidate_evidence_matrix.csv'))
    out.mkdir(parents=True,exist_ok=False);print('H0.1 blind qualified-universe sieve',flush=True);state=audit(source,q16,q16r,out)
    print('H0.1 generic audit frozen; historical input and diagnostics now permitted',flush=True)
    inputs['h0_postfreeze']=verified_input(h0,Path(str(h0)+'_results.zip'),config['h0_zip_sha256']);ready=postfreeze(state,out,h0,config)
    ensure_code_unchanged(start_fingerprint)
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],status='AWAITING_VALIDATION',readiness=ready,code_fingerprint=start_fingerprint,
      metrics=state['metrics'],inputs=inputs,frozen=frozen,synthetic=synth,tests={k:v for k,v in tests.items() if k!='passed_tests'},analysis_scope='JOB',new_relation_qualification_authorized=False))
    manifest(out);e=evidence(state,out,source,q15,q16r,config,frozen,synth,tests,before,raw_hash);write(out/'gate_evidence.json',e)
    table(out/'19_h01_gates.csv',gates(e,['DETERMINISTIC_RERUN','ZIP_CRC_VALID']+(['FULL_REGRESSION_PASS'] if not regression else [])));manifest(out)
    ensure_code_unchanged(start_fingerprint);print(encode(state['metrics']),flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if a.resolve()==b.resolve() or not all(verify_manifest(p) for p in (a,b)):raise ValueError('independent valid outputs required')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('A/B manifests differ')
    trial=Path(str(a)+'_crc_preflight.zip');pack(a,trial);checked=verify_archive(trial,digest(trial))
    for p in (a,b):
        meta=json.loads((p/'90_run_metadata.json').read_text());e=json.loads((p/'gate_evidence.json').read_text())
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        e.update(independent_equal=True,manifest_valid=verify_manifest(p),crc_valid=checked['crc_valid']);table(p/'19_h01_gates.csv',gates(e));write(p/'gate_evidence.json',e)
        meta['status']='VALIDATED_REVIEW_UNIVERSE_NOT_HUMAN_ADJUDICATION';write(p/'90_run_metadata.json',meta);manifest(p)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final manifest mismatch')
    zs=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),zs):pack(p,z)
    if zs[0].read_bytes()!=zs[1].read_bytes():raise ValueError('ZIP bytes differ')
    r=dict(zip_paths=list(map(str,zs)),zip_sha256=digest(zs[0]),zip_exists=[z.is_file() for z in zs],bytes_identical=True,archives=[verify_archive(z,digest(z)) for z in zs]);write(Path(str(a)+'_verification.json'),r);return r


def main():
    p=argparse.ArgumentParser()
    for k in ('source','q15','q16','q16r','h0','out','synthetic','regression'):p.add_argument('--'+k)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);a=p.parse_args()
    if a.self_test:print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.source,a.q15,a.q16,a.q16r,a.h0,a.out,a.synthetic,a.regression)
if __name__=='__main__':main()
