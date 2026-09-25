"""MFR.0.2A orchestration: verify, isolate, freeze, then compare history."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
import unittest
import zipfile
from pathlib import Path
import milal_mfr_common as cm
import milal_mfr02a_core as core
from milal_mfr01b_data import digest
from milal_mfr01b_io import baseline, verify_zip


def code_hashes():
    return {p.relative_to(cm.ROOT).as_posix(): digest(p) for p in sorted((cm.ROOT/'src').glob('milal_mfr02a_*.py'))}


def freeze_valid(out):
    out = Path(out)
    manifest = cm.rows((out/'14_human_decision_freeze.csv').read_bytes())
    return {r['path'] for r in manifest} == set(core.FREEZE_FILES) and len(manifest) == len(core.FREEZE_FILES) and all(digest(out/r['path']) == r['sha256'] for r in manifest)


def project(archive, dest):
    with zipfile.ZipFile(archive) as source, zipfile.ZipFile(dest, 'x', compression=zipfile.ZIP_DEFLATED) as target:
        h1 = cm.rows(source.read('13_h1_hierarchy_review_set.csv'))
        names = ['13_h1_hierarchy_review_set.csv', '14_r1_resumption_review_set.csv', '15_c1_closure_review_set.csv']
        names += ['case_evidence/' + h['configuration_case_id'] + '.json' for h in h1]
        for n in sorted(names):
            info = zipfile.ZipInfo(n, (2000, 1, 1, 0, 0, 0));info.compress_type=zipfile.ZIP_DEFLATED
            target.writestr(info, source.read(n))


def prepare(out, archive=None):
    out = Path(out).resolve()
    cm.require(not out.exists(), 'Append-only: fresh output path required')
    work = out.with_name(out.name + '_work');cm.require(not work.exists(), 'Fresh work path required');work.mkdir(parents=True)
    cfg = json.loads((cm.ROOT/'config/mfr_0_2a_job.json').read_bytes())
    pins = baseline(cfg)
    authority = cm.ROOT/'docs/MFR_0_2A_RESEARCHER_SOURCE.txt';human = cm.ROOT/'config/mfr_0_2a_human_decisions.json'
    cm.require(digest(authority) == cfg['authority_sha256'] and digest(human) == cfg['human_registry_sha256'], 'Researcher authority changed')
    archive = Path(archive or cm.ROOT/cfg['archive']['path']).resolve()
    receipt = verify_zip(archive, cfg['archive']['sha256'])
    # Embedded predecessors are exact frozen packages; verify both without reading historical outcomes.
    prior = work/'mfr01a.zip';raw = work/'mfr01.zip'
    with zipfile.ZipFile(archive) as z, prior.open('xb') as f:
        with z.open('mfr01a_frozen_input.zip') as src:shutil.copyfileobj(src, f)
    prior_cfg = json.loads((cm.ROOT/'config/mfr_0_1b_job.json').read_bytes())
    prior_receipt = verify_zip(prior, prior_cfg['archive']['sha256'])
    with zipfile.ZipFile(prior) as z, raw.open('xb') as f:
        with z.open('mfr01_frozen_input.zip') as src:shutil.copyfileobj(src, f)
    raw_receipt = verify_zip(raw, prior_cfg['embedded_raw_sha256'])
    projection = work/'h1_projection.zip';project(archive, projection)
    subprocess.run([sys.executable, '-B', '-X', 'utf8', str(cm.ROOT/'src/milal_mfr02a_freeze.py'), str(projection), str(human), str(out)], check=True, cwd=cm.ROOT)
    cm.require(freeze_valid(out), 'Decision freeze invalid')
    shutil.copyfile(projection, out/'h1_source_projection.zip')
    shutil.copyfile(archive, out/'mfr01b_frozen_input.zip')
    with zipfile.ZipFile(projection) as z:
        for n in z.namelist():
            if n.startswith('case_evidence/'):cm.write(out/'evidence'/Path(n).name, z.read(n))
    cm.write(out/'16_precomparison_receipt.json', cm.js(dict(baseline=cfg['baseline'], frozen_files=len(pins),
        authority_sha256=digest(authority), human_registry_sha256=digest(human), upstream_sha256=digest(archive),
        archive_receipts=[raw_receipt, prior_receipt, receipt], freeze_sha256=digest(out/'14_human_decision_freeze.csv'),
        phase='HUMAN_DECISIONS_FROZEN', freeze_code_sha256=code_hashes())))
    print(json.dumps(dict(status='HUMAN_DECISIONS_FROZEN', freeze_sha256=digest(out/'14_human_decision_freeze.csv'))), flush=True)
    return out


def regression(path):
    path = Path(path);start=time.monotonic();before=code_hashes()
    with path.with_suffix('.log').open('w',encoding='utf8') as f:
        result=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.discover(str(cm.ROOT/'tests')))
    receipt=dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),seconds=round(time.monotonic()-start,3),code_sha256=before)
    cm.require(code_hashes()==before,'Source changed during regression')
    cm.write(path,cm.js(receipt));print(json.dumps(receipt));cm.require(result.wasSuccessful() and not result.skipped,'Regression failed')


if __name__ == '__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--input');p.add_argument('--freeze-only',action='store_true');p.add_argument('--regression-only');p.add_argument('--self-test',action='store_true');p.add_argument('--complete-frozen',action='store_true');p.add_argument('--historical-config',default=str(cm.ROOT/'config/mfr_0_2a_historical_comparison.json'));a=p.parse_args()
    if a.regression_only:regression(a.regression_only)
    elif a.self_test:
        from milal_mfr02a_synthetic import selftest
        selftest(a.out)
    else:
        cm.require(a.out,'Output required')
        out=Path(a.out).resolve() if a.complete_frozen else prepare(a.out,a.input)
        if not a.freeze_only:
            from milal_mfr02a_finish import complete
            complete(out,a.historical_config)
