"""Q1.6R verified audit runner; no relation generator is invoked."""
import argparse,ast,json,subprocess
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,physical_path,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_io import verify_archive
from milal_mfr02r_pipeline import code_fingerprint
from milal_q1_runner import verified_input
from milal_q13_pipeline import write
from milal_q16r_pipeline import audit
from milal_q16r_controls import diagnostics
from milal_q16r_validation import gates
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q16r_job.json'


def make_evidence(state,out,source,q15,q16,config,frozen,synth,tests,source_hash):
    old=list(rows(q16/'14_q16_qualified_relation_universe.csv'));new=list(rows(out/'preserved_qualified_relations.csv'))
    prev=json.loads((q15/'blind_metrics.json').read_text());processes=state['processes'];proj=state['projection']
    names=set()
    for p in (ROOT/'src').glob('milal_q16r_*.py'):
        names.update(n.id for n in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))) if isinstance(n,ast.Name))
    vals=[p['detail']['case'] for p in state['audits']['SB05'] if 'case' in p['detail']]
    return dict(baseline=config['baseline'],baseline_heads=config['verified_start_heads'],frozen_differences=frozen['differences'],
        input_hashes=json.loads((out/'frozen_input_hashes.json').read_text()),current_input_hashes={p.name:digest(p) for p in q16.iterdir() if p.is_file()},
        old_outcomes=old,new_outcomes=new,expected_relations=config['expected_input']['qualified'],raw_count=prev['counts']['raw'],expected_raw=config['expected_input']['raw'],raw_hash_before=source_hash,raw_hash_after=digest(physical_path(source/'blind/job/09_candidate_evidence_matrix.csv')),
        human_hash_before=prev['preserved_hashes']['preserved_human_judgments.csv'],human_hash_after=digest(q15/'preserved_human_judgments.csv'),human_count=sum(1 for _ in rows(q15/'preserved_human_judgments.csv')),expected_human=config['expected_input']['human'],
        registry=state['registry'],processes=processes,valency_cases=vals,expected_valency_cases=config['required_internal_valency_candidates'],semantic_checks=synth['checks'],
        native_annotation_changes=[p['process_id'] for p in processes if p['detail'].get('bhsa_rewritten')],
        independence_rows=state['comparisons'],forbidden_weighting_fields=sorted(names&{'score','weight','votes','confidence_total','ranking'}),
        new_positive_witnesses=[p['process_id'] for p in processes if p['distinct_positive_binding'] and p['process_id'] not in proj.nodes],new_relation_count=state['metrics']['newly_qualified'],
        assignments=state['compatibility']['assignments'],new_human_judgments=sum(bool(p['detail'].get('human_judgment')) for p in processes),regression={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint=code_fingerprint(),independent_equal=False,manifest_valid=verify_manifest(out),zip_crc_valid=False)


def run(source,q15,q16,out,synthetic,regression=None):
    source,q15,q16,out=map(Path,(source,q15,q16,out));config=json.loads(CONFIG.read_text());frozen=frozen_check(config)
    synth=json.loads(Path(synthetic).read_text());tests=json.loads(Path(regression).read_text()) if regression else dict(test_scope='NOT_RUN',tests_run=0,failures=0,errors=0,skipped=0)
    if not synth['passed'] or synth['code_fingerprint']!=code_fingerprint():raise ValueError('current synthetic required')
    if regression and (tests.get('code_fingerprint')!=code_fingerprint() or tests.get('test_scope')!='FULL_REGRESSION' or any(tests[k] for k in ('failures','errors','skipped'))):raise ValueError('current full regression required')
    inputs={}
    for k,p in [('source',source),('q15',q15),('q16',q16)]:
        print('Q1.6R verify',k,flush=True);inputs[k]=verified_input(p,Path(str(p)+'_results.zip'),config[k+'_zip_sha256'])
    for r in config['method_sources']:
        if digest(ROOT/r['file'])!=r['sha256']:raise ValueError('method source PDF hash mismatch')
    out.mkdir(parents=True,exist_ok=False);source_hash=digest(physical_path(source/'blind/job/09_candidate_evidence_matrix.csv'))
    print('Q1.6R Job ontology audit',flush=True);state=audit(source,q15,q16,out)
    print('Q1.6R audit frozen; diagnostics',flush=True);diagnostics(state,out,config)
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],status='AWAITING_VALIDATION',code_fingerprint=code_fingerprint(),readiness=state['metrics']['readiness'],metrics=state['metrics'],analysis_scope='JOB',new_relation_qualification_authorized=False,method_sources=config['method_sources'],inputs=inputs,frozen=frozen,synthetic=synth,tests={k:v for k,v in tests.items() if k!='passed_tests'}))
    manifest(out);e=make_evidence(state,out,source,q15,q16,config,frozen,synth,tests,source_hash)
    write(out/'gate_evidence.json',e);table(out/'18_q16r_gates.csv',gates(e,['DETERMINISTIC_RERUN','ZIP_CRC_VALID']+(['FULL_REGRESSION_PASS'] if not regression else [])));manifest(out)
    print(encode(state['metrics']),flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if a.resolve()==b.resolve() or not all(verify_manifest(p) for p in (a,b)):raise ValueError('independent valid outputs required')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('A/B manifests differ')
    trial=Path(str(a)+'_crc_preflight.zip');pack(a,trial);checked=verify_archive(trial,digest(trial))
    for p in (a,b):
        meta=json.loads((p/'90_run_metadata.json').read_text());e=json.loads((p/'gate_evidence.json').read_text())
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        e.update(independent_equal=True,manifest_valid=verify_manifest(p),zip_crc_valid=checked['crc_valid']);table(p/'18_q16r_gates.csv',gates(e));write(p/'gate_evidence.json',e);meta['status']='VALIDATED_METHOD_CONTRACT_NOT_HUMAN_HIERARCHY';write(p/'90_run_metadata.json',meta);manifest(p)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final manifest mismatch')
    zs=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),zs):pack(p,z)
    if zs[0].read_bytes()!=zs[1].read_bytes():raise ValueError('ZIP bytes differ')
    r=dict(zip_paths=list(map(str,zs)),zip_sha256=digest(zs[0]),zip_exists=[z.is_file() for z in zs],bytes_identical=True,archives=[verify_archive(z,digest(z)) for z in zs]);write(Path(str(a)+'_verification.json'),r);return r


def main():
    p=argparse.ArgumentParser()
    for k in ('source','q15','q16','out','synthetic','regression'):p.add_argument('--'+k)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);a=p.parse_args()
    if a.self_test:
        from milal_q16r_synthetic import self_test
        print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.source,a.q15,a.q16,a.out,a.synthetic,a.regression)
if __name__=='__main__':main()
