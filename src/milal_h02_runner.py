"""Verified H0.1 consumption and deterministic H0.2 human-overlay release."""
import argparse
import json
import shutil
import subprocess
from pathlib import Path
from milal_mfr02r_data import rows, table, digest, manifest, verify_manifest, pack, encode, physical_path
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_io import verify_archive
from milal_q1_runner import verified_input
from milal_q13_pipeline import write
from milal_h02_overlay import build, write_outputs, FILES
from milal_h02_validation import gates, MUTATIONS
from milal_h02_synthetic import self_test

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'config/mfr_0_2r_h02_job.json'


def file_hashes(path):
    return {p.relative_to(path).as_posix():digest(p) for p in sorted(path.rglob('*')) if p.is_file()}


def authority(config):
    current = {name:digest(ROOT/name) for name in config['authority_files']}
    if current != config['authority_files']:
        raise ValueError('researcher authority/registry changed; explicit corrective version required')
    return list(rows(ROOT/config['registry'])), current


def current_receipts(synthetic, regression, fingerprint):
    synth = json.loads(Path(synthetic).read_text(encoding='utf8'))
    tests = json.loads(Path(regression).read_text(encoding='utf8'))
    if (synth.get('mode') != 'SYNTHETIC' or not synth.get('passed')
            or synth.get('code_fingerprint') != fingerprint
            or len(synth.get('cases',{})) != 12 or not all(synth['cases'].values())
            or set(synth.get('negative_mutations',{})) != set(MUTATIONS)
            or not all(synth['negative_mutations'].values())):
        raise ValueError('current complete synthetic receipt required')
    if (tests.get('test_scope') != 'FULL_REGRESSION' or tests.get('tests_run',0) < 3050
            or tests.get('code_fingerprint') != fingerprint
            or any(tests.get(k,1) for k in ('failures','errors','skipped'))):
        raise ValueError('current full regression with zero skips required')
    return synth, {k:v for k,v in tests.items() if k != 'passed_tests'}


def read_state(out):
    state = {k:list(rows(out/name)) for k,name in FILES.items()}
    scope = json.loads((out/'overlay_scope.json').read_text(encoding='utf8'))
    state.update(scope)
    return state


def run(h01, raw_source, historical_human, out, synthetic, regression):
    start = code_fingerprint(); config = json.loads(CONFIG.read_text(encoding='utf8'))
    frozen = frozen_check(config); registry, ah = authority(config)
    synth, tests = current_receipts(synthetic,regression,start)
    h01, out = Path(h01), Path(out)
    raw_source, historical_human = physical_path(raw_source), Path(historical_human)
    if h01.resolve() == out.resolve() or h01.resolve() in out.resolve().parents:
        raise ValueError('output must not modify source directory')
    print('H0.2 verify immutable H0.1 archive and extracted manifest',flush=True)
    verified = verified_input(h01,Path(str(h01)+'_results.zip'),config['h01_zip_sha256'])
    before = file_hashes(h01)
    source_evidence = json.loads((h01/'gate_evidence.json').read_text(encoding='utf8'))
    if any(g['status'] != 'PASS' for g in rows(h01/'19_h01_gates.csv')):
        raise ValueError('H0.1 not validated')
    raw_before, human_before = digest(raw_source), digest(historical_human)
    if raw_before != source_evidence['raw_hash_after'] or human_before != source_evidence['human_hash_after']:
        raise ValueError('raw/historical-human input differs from verified H0.1 receipt')
    outcomes = list(rows(h01/'preserved_qualified_relations.csv'))
    packets = list(rows(h01/'12_h01_review_packets.csv'))
    pivots = list(rows(h01/'07_h01_true_decision_pivots.csv'))
    historical = list(rows(historical_human))
    state = build(outcomes,packets,pivots,registry,historical)
    out.mkdir(parents=True,exist_ok=False)
    shutil.copytree(h01,out/'frozen_h01')
    shutil.copyfile(historical_human,out/'historical_human_source.csv')
    write_outputs(out,state)
    write(out/'overlay_scope.json',dict(new_relations=state['new_relations'],canonical_hierarchy=state['canonical_hierarchy']))
    # Gates measure deserialized output, not only the in-memory construction.
    state = read_state(out)
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    if head != config['baseline']:
        subprocess.run(['git','merge-base','--is-ancestor',config['baseline'],head],cwd=ROOT,check=True)
    evidence = dict(state=state,original_outcomes=outcomes,original_historical=historical,
        packets=packets,pivots=pivots,authority=registry,expected=config['expected'],
        baseline=config['baseline'],start_heads=config['verified_start_heads'],frozen_differences=frozen['differences'],
        input_before=before,input_after=file_hashes(h01),copied_input=file_hashes(out/'frozen_h01'),
        raw_count=source_evidence['raw_count'],raw_expected_hash=source_evidence['raw_hash_after'],
        raw_before=raw_before,raw_after=digest(raw_source),
        packet_before=before['12_h01_review_packets.csv'],packet_after=digest(h01/'12_h01_review_packets.csv'),
        packet_copy=digest(out/'frozen_h01/12_h01_review_packets.csv'),
        human_expected_hash=source_evidence['human_hash_after'],human_before=human_before,
        human_after=digest(historical_human),human_copy=digest(out/'historical_human_source.csv'),
        regression=tests,fingerprint=start,independent_equal=False,manifest_valid=True,crc_valid=False,
        authority_hashes=ah,current_authority_hashes=authority(config)[1],
        caution_report=(out/'08_h02_ki_function_caution.md').read_text(encoding='utf8'),
        method_report=(out/'10_h02_method_report.md').read_text(encoding='utf8'))
    if code_fingerprint() != start:
        raise ValueError('code changed during execution')
    write(out/'90_run_metadata.json',dict(stage=config['stage'],mode='REAL',baseline=config['baseline'],
        code_fingerprint=start,status='AWAITING_INDEPENDENT_RELEASE',readiness='READY_FOR_MFR_0_2R_H1_0',
        analysis_scope='JOB',frozen=frozen,h01_archive=verified,authority=ah,synthetic=synth,regression=tests,
        metrics=state['review'][0],historical_count_contract='UNCHANGED_LEGACY_ENTRIES_PLUS_ONE_NEW_PACKET'))
    manifest(out);evidence['manifest_valid']=verify_manifest(out)
    table(out/'12_h02_gates.csv',gates(evidence,['DETERMINISTIC_RERUN','ZIP_CRC_VALID']))
    write(out/'gate_evidence.json',evidence);manifest(out)
    print(encode(state['review'][0]),flush=True)


def release(a,b):
    config = json.loads(CONFIG.read_text(encoding='utf8'));frozen_check(config);authority(config)
    a,b = Path(a),Path(b)
    if a.resolve() == b.resolve() or not all(verify_manifest(p) for p in (a,b)):
        raise ValueError('independent valid outputs required')
    if (a/'99_manifest_sha256.csv').read_bytes() != (b/'99_manifest_sha256.csv').read_bytes():
        raise ValueError('independent A/B manifests differ')
    trial = Path(str(a)+'_crc_preflight.zip');pack(a,trial)
    checked = verify_archive(trial,digest(trial))
    for p in (a,b):
        e = json.loads((p/'gate_evidence.json').read_text(encoding='utf8'))
        meta = json.loads((p/'90_run_metadata.json').read_text(encoding='utf8'))
        if meta['code_fingerprint'] != code_fingerprint():
            raise ValueError('release fingerprint changed')
        e['state'] = read_state(p)
        e['copied_input'] = file_hashes(p/'frozen_h01')
        e['packet_copy'] = digest(p/'frozen_h01/12_h01_review_packets.csv')
        e['human_copy'] = digest(p/'historical_human_source.csv')
        e['current_authority_hashes'] = authority(config)[1]
        e['caution_report'] = (p/'08_h02_ki_function_caution.md').read_text(encoding='utf8')
        e['method_report'] = (p/'10_h02_method_report.md').read_text(encoding='utf8')
        e.update(independent_equal=True,manifest_valid=verify_manifest(p),crc_valid=checked['crc_valid'])
        table(p/'12_h02_gates.csv',gates(e));write(p/'gate_evidence.json',e)
        meta['status']='VALIDATED_APPEND_ONLY_HUMAN_LOCAL_ADJUDICATION';write(p/'90_run_metadata.json',meta);manifest(p)
    zs = [Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),zs):
        pack(p,z)
    if zs[0].read_bytes() != zs[1].read_bytes():
        raise ValueError('ZIP bytes differ')
    receipt = dict(zip_paths=list(map(str,zs)),zip_sha256=digest(zs[0]),zip_exists=[z.is_file() for z in zs],
                   bytes_identical=True,archives=[verify_archive(z,digest(z)) for z in zs])
    write(Path(str(a)+'_verification.json'),receipt)
    return receipt


def main():
    p=argparse.ArgumentParser()
    for name in ('h01','raw-source','historical-human','out','synthetic','regression'):
        p.add_argument('--'+name)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2)
    a=p.parse_args()
    if a.self_test:print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.h01,a.raw_source,a.historical_human,a.out,a.synthetic,a.regression)


if __name__ == '__main__':main()
