"""Verify inputs, run H0 and validate independent results without rewriting upstream."""
import argparse
import json
from pathlib import Path
import zipfile
from milal_mfr02r_data import rows, table, encode, digest, manifest, verify_manifest, pack
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_h0 import run, load_config, frozen_check, verify_archive
from milal_h0_validation import audit, evaluate


def verified_source(source,archive,config):
    receipt=verify_archive(archive,config['input_zip_sha256'])
    with zipfile.ZipFile(archive) as z:
        if z.read('99_manifest_sha256.csv')!=(Path(source)/'99_manifest_sha256.csv').read_bytes():
            raise ValueError('extracted source differs from exact frozen ZIP manifest')
    if not verify_manifest(source):raise ValueError('extracted source manifest invalid')
    return receipt


def empirical(source,archive,out,regression):
    config=load_config();frozen=frozen_check(config)
    tests=json.loads(Path(regression).read_text())
    if tests.get('test_scope')!='FULL_REGRESSION' or tests['code_fingerprint']!=code_fingerprint() or any(tests[k] for k in ('failures','errors','skipped')) or tests['tests_run']<2403:
        raise ValueError('current full regression without failures/skips required')
    verified=verified_source(source,archive,config)
    run(source,out,config)
    receipts=dict(baseline=frozen,tests=tests,source=verified)
    # Keep the large passed-test ID list in the external receipt, not duplicated.
    receipts['tests']={k:v for k,v in tests.items() if k!='passed_tests'}
    out=Path(out)
    (out/'validation_receipts.json').write_text(encode(receipts)+'\n',encoding='utf8');manifest(out)
    measured=audit(source,out,config,receipts)
    gates=evaluate(measured);table(out/'21_h0_gates.csv',gates)
    metadata=json.loads((out/'90_run_metadata.json').read_text())
    metadata.update(code_fingerprint=code_fingerprint(),status='AWAITING_INDEPENDENT_RERUN')
    (out/'90_run_metadata.json').write_text(encode(metadata)+'\n',encoding='utf8');manifest(out)
    return dict(gates=len(gates),failed=[r['gate'] for r in gates if not r['passed']],metrics=json.loads((out/'17_h0_review_reduction_metrics.json').read_text()))


def release(a,b):
    a,b=Path(a),Path(b);config=load_config();frozen_check(config)
    if not all(verify_manifest(p) for p in (a,b)):raise ValueError('H0 manifest invalid')
    if list(rows(a/'99_manifest_sha256.csv'))!=list(rows(b/'99_manifest_sha256.csv')):raise ValueError('independent bytes differ')
    for out in (a,b):
        metadata=json.loads((out/'90_run_metadata.json').read_text())
        if metadata['mode']!='REAL' or metadata['stage']!='MFR.0.2R-H0' or metadata['code_fingerprint']!=code_fingerprint():raise ValueError('release stage/mode/fingerprint mismatch')
        gates=list(rows(out/'21_h0_gates.csv'))
        if len(gates)!=len(config['gates']) or {r['gate'] for r in gates}!=set(config['gates']):raise ValueError('gate universe incomplete')
        for r in gates:
            if r['gate']=='DETERMINISTIC_RERUN':r['passed']=True;r['evidence']=dict(actual=True,expected=True)
        if any(r['passed'] is not True for r in gates):raise ValueError('failed H0 gates')
        table(out/'21_h0_gates.csv',gates)
        metadata['status']='REVIEW_UNIVERSE_REDUCED_WITHOUT_DATA_LOSS'
        metadata['readiness']='REVIEW_SIEVE_SELECTIVITY_REQUIRES_HUMAN_REVIEW' if metadata['warnings'] else 'READY_FOR_MFR_0_2R_H'
        (out/'90_run_metadata.json').write_text(encode(metadata)+'\n',encoding='utf8');manifest(out)
    if list(rows(a/'99_manifest_sha256.csv'))!=list(rows(b/'99_manifest_sha256.csv')):raise ValueError('release bytes differ')
    za=Path(str(a)+'_results.zip');zb=Path(str(b)+'_results.zip');pack(a,za);pack(b,zb)
    if digest(za)!=digest(zb):raise ValueError('ZIP bytes differ')
    verified=verify_archive(za,digest(za))
    receipt=dict(**verified,zip_a=str(za),zip_b=str(zb),byte_identical=True,gates=len(config['gates']))
    Path(str(a)+'_verification.json').write_text(encode(receipt)+'\n',encoding='utf8')
    return receipt


def main():
    p=argparse.ArgumentParser();p.add_argument('--source');p.add_argument('--archive');p.add_argument('--out');p.add_argument('--regression-receipt')
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2)
    args=p.parse_args()
    if args.self_test:
        from milal_h0_synthetic import self_test
        result=self_test(args.out)
    elif args.release:result=release(*args.release)
    else:result=empirical(args.source,args.archive,args.out,args.regression_receipt)
    print(encode(result))


if __name__=='__main__':main()
