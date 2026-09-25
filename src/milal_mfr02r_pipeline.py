"""MFR.0.2R isolated blind execution, post-freeze comparisons and release verification."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import unittest
import zipfile
import shutil
from milal_mfr02r_data import table, rows, zip_rows, encode, digest, manifest, verify_manifest, pack
from milal_mfr02r_io import ROOT, baseline, verify_archive, project, worker


def code_fingerprint():
    h = hashlib.sha256()
    for folder, glob in [('src', '*.py'), ('tests', '*.py'), ('config', '*.json')]:
        for path in sorted((ROOT / folder).glob(glob)):
            h.update(path.relative_to(ROOT).as_posix().encode()); h.update(path.read_bytes())
    return h.hexdigest()


def regression(path, stage_only=False):
    initial_fingerprint = code_fingerprint()
    class Result(unittest.TextTestResult):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs); self.passed_tests = []
        def addSuccess(self, test):
            self.passed_tests.append(test.id()); super().addSuccess(test)
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_mfr02r*.py' if stage_only else 'test_*.py')
    with path.with_suffix('.log').open('w', encoding='utf8') as log:
        result = unittest.TextTestRunner(stream=log, verbosity=2, resultclass=Result).run(suite)
    config = json.loads((ROOT / 'config/mfr_0_2r_job.json').read_text())
    if code_fingerprint() != initial_fingerprint:
        raise ValueError('source files changed during regression; rerun required')
    receipt = dict(tests_run=result.testsRun, failures=len(result.failures), errors=len(result.errors), skipped=len(result.skipped),
                   passed_tests=sorted(result.passed_tests), baseline=config['baseline'], code_fingerprint=code_fingerprint(),
                   test_scope='STAGE' if stage_only else 'FULL_REGRESSION')
    path.write_text(encode(receipt) + '\n', encoding='utf8')
    if not result.wasSuccessful() or result.skipped:
        raise ValueError('tests failed or skipped; see ' + str(path.with_suffix('.log')))
    return receipt


def self_test(out):
    from milal_mfr02r_grammar import load_registry
    from milal_mfr02r_engine import run_engine
    from milal_mfr02r_synthetic import sample
    out = Path(out)
    registry = load_registry(ROOT / 'config/clause_relation_grammar_v1.json')
    labels = json.loads((ROOT / 'config/mfr_0_2r_evidence_labels.json').read_text())
    result = run_engine(sample(), registry, [], out, label_definitions=labels,
                        analysis_scope='SYNTHETIC_ANALYSIS', comparison_scope='SYNTHETIC_CORPUS')
    if not verify_manifest(out):
        raise ValueError('synthetic manifest invalid')
    return result


def legacy_crosswalk(config, out):
    with zipfile.ZipFile(ROOT / config['archives'][2]['path']) as archive:
        roles = {r['marker_id']: r for r in zip_rows(archive, 'audit/job/02_marker_role_registry.csv')}
    with zipfile.ZipFile(ROOT / config['archives'][0]['path']) as archive:
        records = []
        for old in zip_rows(archive, 'blind/job/08_job_hierarchical_force_evidence.csv'):
            role = roles[old['marker_id']]
            records.append(dict(marker_id=old['marker_id'], status='PRE_HIERARCHY_FORCE_EVIDENCE',
                legacy_role_label=role['role'], relation_engine_role='EVIDENCE_DIMENSION',
                original_force_record=old, original_role_record=role, automatic_hierarchy=False))
        table(Path(out) / '16_pre_hierarchy_force_crosswalk.csv', records)
        references = []
        for item in config['archives']:
            references.append(dict(source_stage=item['stage'], source_archive_sha256=item['sha256'],
                original_archive_path=item['path'], preservation='ORIGINAL_IMMUTABLE_ARTIFACT',
                marker_family_role='CANDIDATE_SEARCH_INDEX_AND_FORMAL_CORRESPONDENCE_EVIDENCE',
                coverage_role='PRE_HIERARCHY_COVERAGE_CANDIDATE', nested_role='SPAN_RELATION_EVIDENCE',
                no_record_deletion=True))
        table(Path(out) / 'frozen_evidence_crosswalk.csv', references)


def run(out, projection, regression_receipt, reuse_job=None):
    from milal_mfr02r_controls import execute
    from milal_mfr02r_review import run_review
    from milal_mfr02r_gates import artifact_facts, evaluate
    from milal_mfr02r_grammar import load_registry
    out, projection = Path(out), Path(projection)
    config_path = ROOT / 'config/mfr_0_2r_job.json'
    config = json.loads(config_path.read_text())
    from milal_mfr02r_scope import require_job_scope
    require_job_scope(config)
    tests = json.loads(Path(regression_receipt).read_text())
    if tests['code_fingerprint'] != code_fingerprint() or tests['failures'] or tests['errors'] or tests['skipped']:
        raise ValueError('regression receipt is stale or not passing')
    if tests['test_scope'] != 'FULL_REGRESSION' or tests['tests_run'] < 2152:
        raise ValueError('full previous regression required before empirical execution')
    receipts = baseline(config)
    if out.exists():
        raise ValueError('output directory already exists')
    out.mkdir(parents=True)
    table(out / 'frozen_file_receipts.csv', receipts)
    grammar_path = ROOT / 'config/clause_relation_grammar_v1.json'
    labels_path = ROOT / 'config/mfr_0_2r_evidence_labels.json'
    blind = out / 'blind'; blind.mkdir()
    registry = load_registry(grammar_path)
    if reuse_job:
        original = Path(reuse_job)
        if not verify_manifest(original) or digest(original/'99_manifest_sha256.csv') != config['reusable_job_manifest_sha256']:
            raise ValueError('reused Job manifest is not the verified independent Job result')
        original_inventory = list(rows(original/'02_clause_feature_inventory.csv'))
        if not original_inventory or any(r['book'] != 'Iob' for r in original_inventory):
            raise ValueError('reused primary observations are not Job only')
        shutil.copytree(original, blind/'job')
        if not verify_manifest(blind/'job'):
            raise ValueError('copied Job manifest invalid')
        producer = dict(mode='VERIFIED_JOB_REUSE_NO_RESTART', manifest_sha256=config['reusable_job_manifest_sha256'],
            producer_code_fingerprint=config['job_producer_code_fingerprint'])
    else:
        subprocess.run([sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--worker',
            '--projection',str(projection),'--scope','job','--out',str(blind/'job')],check=True)
        producer = dict(mode='JOB_ONLY_PRIMARY_RUN', producer_code_fingerprint=code_fingerprint())
    freeze = dict(scope_manifests={'job': digest(blind/'job/99_manifest_sha256.csv')})
    (blind / 'blind_freeze.json').write_text(encode(freeze) + '\n', encoding='utf8')
    controls = out / 'controls'
    native = [dict(r,dependent_node=int(r['dependent_node']),head_node=int(r['head_node'])) for r in rows(projection/'native_edges.csv')]
    tf_path = json.loads((projection/'source_location.json').read_text())['tf_path']
    control = execute(blind, ROOT / 'config/mfr_0_2r_controls.json', controls, tf_path, registry, native)
    control_files = manifest(controls)
    (controls / 'control_freeze.json').write_text(encode(dict(files=control_files)) + '\n', encoding='utf8')
    manifest(controls)
    from milal_mfr02r_valency import analogues, validate_comparison_index
    search = out/'corpus_search'; search.mkdir()
    index = json.loads((projection/'comparison_index.json').read_text())
    constructions = list(rows(blind/'job/construction_inventory.csv'))
    for item in constructions:
        item['clause_id'] = int(item['clause_id'])
    validate_comparison_index(constructions,index)
    table(search/'01_job_hb_analogues.csv',analogues(constructions,index,'JOB','HB_CORPUS',symbolic=True))
    shutil.copyfile(projection/'comparison_index.json',search/'hb_comparison_index.json')
    shutil.copyfile(projection/'corpus_search_receipt.json',search/'corpus_search_receipt.json')
    (out/'job_reuse_provenance.json').write_text(encode(producer)+'\n',encoding='utf8')
    review = run_review(blind / 'job', controls, ROOT / config['archives'][3]['path'], out)
    legacy_crosswalk(config, out)
    (out / '26_next_scope.md').write_text('# Next scope\n\nMFR.0.2R-H — Human Revalidation of Candidate-Set Relation Cases.\nNo automatic progression to resumption or closure adjudication.\n', encoding='utf8')
    methodology = ROOT / 'docs/CLAUSE_RELATION_GRAMMAR.md'
    (out / '23_relation_engine_method_report.md').write_bytes(methodology.read_bytes())
    registry = load_registry(grammar_path)
    facts = artifact_facts(blind / 'job', registry, tests, config, receipts, control, review, out)
    table(out / '27_gates.csv', evaluate(facts))
    metadata = dict(stage='MFR.0.2R', mode='REAL', baseline=config['baseline'], code_fingerprint=code_fingerprint(),
        source_documents=config['source_documents'], rule_registry_sha256=digest(grammar_path),
        evidence_labels_sha256=digest(labels_path), projection_receipts=json.loads((projection / 'projection_receipts.json').read_text()),
        archive_verification_receipts=json.loads((projection / 'verified_archives.json').read_text()),
        tests={k: tests[k] for k in ('tests_run', 'failures', 'errors', 'skipped', 'code_fingerprint')},
        controls=control, review=review, analysis_scope='JOB', corpus_comparison_scope=config['corpus_comparison_scope'],
        corpus_comparison_is_entire_HB=True, control_fixture_scope='EXPLICIT_REFERENCES_ONLY', job_producer=producer,
        canonical_mothers=[], canonical_trees=[],
        status='AWAITING_INDEPENDENT_DETERMINISTIC_RELEASE_CHECK', frozen_file_count=len(receipts))
    (out / '90_run_metadata.json').write_text(encode(metadata) + '\n', encoding='utf8')
    manifest(out)
    return metadata


def release(a, b):
    a, b = Path(a), Path(b)
    for directory in (a, b):
        if not verify_manifest(directory):
            raise ValueError('release manifest invalid')
    left = {r['path']: r['sha256'] for r in rows(a / '99_manifest_sha256.csv')}
    right = {r['path']: r['sha256'] for r in rows(b / '99_manifest_sha256.csv')}
    if left != right:
        raise ValueError('independent rerun bytes differ')
    for directory in (a, b):
        gate_rows = list(rows(directory / '27_gates.csv'))
        required = json.loads((ROOT / 'config/mfr_0_2r_required_gates.json').read_text())['gates']
        if len(gate_rows) != len(required) or {r.get('gate') for r in gate_rows} != set(required):
            raise ValueError('release gate universe incomplete or duplicated')
        metadata_path = directory / '90_run_metadata.json'
        metadata = json.loads(metadata_path.read_text())
        if metadata.get('stage') != 'MFR.0.2R' or metadata.get('mode') != 'REAL' or metadata.get('code_fingerprint') != code_fingerprint():
            raise ValueError('release stage, mode or code fingerprint mismatch')
        for row in gate_rows:
            if row['gate'] == 'DETERMINISTIC_RERUN':
                row.update(passed=True, evidence=True)
        if any(r.get('passed') is not True for r in gate_rows):
            raise ValueError('release gate failures: ' + ', '.join(r['gate'] for r in gate_rows if r.get('passed') is not True))
        table(directory / '27_gates.csv', gate_rows)
        metadata['status'] = 'CLAUSE_RELATION_GRAMMAR_ENGINE_ESTABLISHED'
        metadata['readiness'] = 'READY_FOR_CANDIDATE_SET_HUMAN_REVALIDATION'
        metadata_path.write_text(encode(metadata) + '\n', encoding='utf8')
        manifest(directory)
    if {r['path']: r['sha256'] for r in rows(a / '99_manifest_sha256.csv')} != {r['path']: r['sha256'] for r in rows(b / '99_manifest_sha256.csv')}:
        raise ValueError('release files differ')
    za, zb = Path(str(a) + '_results.zip'), Path(str(b) + '_results.zip')
    pack(a, za); pack(b, zb)
    if digest(za) != digest(zb):
        raise ValueError('independent ZIP bytes differ')
    verify_archive(za, digest(za))
    receipt = dict(zip_a=za.name, zip_b=zb.name, sha256=digest(za), byte_identical=True, manifest_verified=True,
                   gates=len(gate_rows), all_gates_passed=True)
    Path(str(a) + '_verification.json').write_text(encode(receipt) + '\n', encoding='utf8')
    return receipt


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--out'); p.add_argument('--projection'); p.add_argument('--tf-path'); p.add_argument('--scope')
    p.add_argument('--reuse-job'); p.add_argument('--regression-receipt'); p.add_argument('--regression-only'); p.add_argument('--stage-tests-only')
    p.add_argument('--worker', action='store_true'); p.add_argument('--prepare', action='store_true')
    p.add_argument('--self-test', action='store_true'); p.add_argument('--release', nargs=2)
    args = p.parse_args()
    if args.regression_only:
        result = regression(args.regression_only)
    elif args.stage_tests_only:
        result = regression(args.stage_tests_only, True)
    elif args.self_test:
        result = self_test(args.out)
    elif args.prepare:
        config = json.loads((ROOT / 'config/mfr_0_2r_job.json').read_text()); baseline(config)
        verified = [dict(stage=item['stage'], **verify_archive(ROOT / item['path'], item['sha256'])) for item in config['archives']]
        result = project(config, args.tf_path, args.projection)
        (Path(args.projection) / 'verified_archives.json').write_text(encode(verified) + '\n', encoding='utf8')
    elif args.worker:
        result = worker(args.projection, args.scope, ROOT / 'config/clause_relation_grammar_v1.json', ROOT / 'config/mfr_0_2r_evidence_labels.json', args.out)
    elif args.release:
        result = release(*args.release)
    else:
        result = run(args.out, args.projection, args.regression_receipt, args.reuse_job)
    displayed = {k:v for k,v in result.items() if k != 'passed_tests'} if isinstance(result, dict) else result
    print(encode(displayed), flush=True)


if __name__ == '__main__':
    main()
