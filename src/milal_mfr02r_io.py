"""Verified inputs and restricted blind-worker projection."""
import hashlib
import json
import os
import subprocess
import sys
import zipfile
from pathlib import Path
from milal_mfr02r_data import digest, encode, zip_rows, table

ROOT = Path(__file__).resolve().parents[1]


def baseline(config):
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if subprocess.run(['git', 'merge-base', '--is-ancestor', config['baseline'], head], cwd=ROOT).returncode:
        raise ValueError('baseline ancestry mismatch')
    receipts = [dict(path=p, expected_sha256=h, actual_sha256=digest(ROOT / p)) for p, h in config['frozen_files'].items()]
    if any(r['expected_sha256'] != r['actual_sha256'] for r in receipts):
        raise ValueError('frozen repository file changed')
    return receipts


def verify_archive(path, expected):
    if digest(path) != expected:
        raise ValueError('input ZIP hash mismatch: ' + str(path))
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or archive.testzip() is not None:
            raise ValueError('ZIP duplicate member or CRC failure')
        records = list(zip_rows(archive, '99_manifest_sha256.csv'))
        if {r['path'] for r in records} != set(names) - {'99_manifest_sha256.csv'}:
            raise ValueError('ZIP manifest universe mismatch')
        for record in records:
            h = hashlib.sha256()
            with archive.open(record['path']) as source:
                while chunk := source.read(1024 * 1024):
                    h.update(chunk)
            if h.hexdigest() != record['sha256']:
                raise ValueError('ZIP member hash mismatch')
    return dict(sha256=expected, members=len(names), crc_valid=True, manifest_valid=True)


def project(config, tf_path, directory):
    from milal_mfr_observation import read_feature, raw_corpus
    from milal_mfr02r_data import rows
    from milal_mfr02r_valency import construction, corpus_index
    from milal_mfr02r_scope import require_job_scope
    require_job_scope(config)
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=False)
    (directory / 'source_location.json').write_text(encode(dict(tf_path=str(Path(tf_path).resolve())))+'\n', encoding='utf8')
    mothers, mh = read_feature(Path(tf_path) / 'mother.tf')
    relations, rh = read_feature(Path(tf_path) / 'rela.tf')
    qere, qh = read_feature(Path(tf_path) / 'qere_utf8.tf')
    (directory / 'qere.json').write_text(encode(qere) + '\n', encoding='utf8')
    archive_path = ROOT / config['archives'][0]['path']
    receipts = []
    with zipfile.ZipFile(archive_path) as archive:
        for scope in config['scopes']:
            member = 'blind/' + scope + '/03_job_surface_observation_inventory.csv'
            with archive.open(member) as source, (directory / (scope + '.csv')).open('xb') as dest:
                h = hashlib.sha256()
                while chunk := source.read(1024 * 1024):
                    h.update(chunk); dest.write(chunk)
            receipts.append(dict(scope=scope, source_archive_sha256=config['archives'][0]['sha256'], source_member=member, sha256=h.hexdigest()))
    # No accepted textual tree is imported. Native annotated object edges are
    # preserved as DATABASE_EXISTING_RELATION and only support candidate rules.
    table(directory / 'native_edges.csv', (dict(dependent_node=node, head_node=head, rela=relations.get(node, 'NA'),
        status='DATABASE_EXISTING_RELATION', source_feature_sha256=mh['sha256'], relation_feature_sha256=rh['sha256'])
        for node in sorted(mothers) for head in sorted(mothers[node])))
    receipts.append(dict(native_features=[mh, rh], tradition_features=[qh]))
    books, _ = read_feature(Path(tf_path) / 'book.tf')
    corpus, features = raw_corpus(tf_path, sorted(set(books.values())))
    # Search-only construction keys. No HB hierarchy, participant, marker or
    # valency inventory is emitted and the relation engine is never called here.
    index = corpus_index(construction(r) for r in corpus)
    (directory / 'comparison_index.json').write_text(encode(index) + '\n', encoding='utf8')
    receipt = dict(analysis_scope='JOB', corpus_comparison_scope='HB_CORPUS',
        unique_clauses=len(corpus), books=sorted(set(books.values())), hierarchy_generated=False,
        purpose='CORPUS_ANALOGUE_SEARCH_ONLY', features=features,
        comparison_index_sha256=digest(directory / 'comparison_index.json'))
    (directory / 'corpus_search_receipt.json').write_text(encode(receipt)+'\n', encoding='utf8')
    receipts.append(receipt)
    (directory / 'projection_receipts.json').write_text(encode(receipts) + '\n', encoding='utf8')
    return receipts


def install_read_guard(allowed, out):
    allowed = {str(Path(p).resolve()).casefold() for p in allowed}
    output = str(Path(out).resolve()).casefold()
    trace = []
    def hook(event, args):
        if event != 'open' or isinstance(args[0], int):
            return
        path = str(Path(os.fsdecode(args[0])).resolve()).casefold()
        mode, flags = args[1:3]
        writing = isinstance(mode, str) and any(c in mode for c in 'wax+') or isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)
        within_output = path.startswith(output + os.sep)
        if writing and not within_output:
            raise PermissionError('blind write outside output')
        if not writing and path not in allowed and not within_output:
            raise PermissionError('blind read outside projection allowlist: ' + path)
        if not writing and not within_output:
            trace.append(path)
    sys.addaudithook(hook)
    return trace


def worker(projection, scope, grammar_path, labels_path, out, max_assignments=64, long_distance=20):
    if scope != 'job':
        raise ValueError('primary relation worker accepts JOB only; use post-freeze fixtures')
    # All code imports complete before installing the deny-by-default file guard.
    from milal_mfr02r_data import rows, manifest
    from milal_mfr02r_grammar import load_registry
    from milal_mfr02r_engine import run_engine
    import milal_mfr02r_data as data
    data.COMPACT_TABLES = True
    observation_path = Path(projection) / (scope + '.csv')
    native_path = Path(projection) / 'native_edges.csv'
    comparison_path = Path(projection) / 'comparison_index.json'
    qere_path = Path(projection) / 'qere.json'
    registry = load_registry(grammar_path)
    labels = json.loads(Path(labels_path).read_text(encoding='utf8'))
    trace = install_read_guard([observation_path, native_path, comparison_path, qere_path], out)
    observations = list(rows(observation_path))
    native = [dict(r, dependent_node=int(r['dependent_node']), head_node=int(r['head_node'])) for r in rows(native_path)]
    comparison = json.loads(comparison_path.read_text(encoding='utf8'))
    qere = {int(k): v for k, v in json.loads(qere_path.read_text(encoding='utf8')).items()}
    result = run_engine(observations, registry, native, out, max_assignments, long_distance, labels,
                        comparison, 'JOB', 'HB_CORPUS', qere)
    (Path(out) / 'blind_access_receipt.json').write_text(encode(dict(scope=scope, input_files=sorted(set(Path(p).name for p in trace)),
        human_judgment_loaded=False, control_configuration_loaded=False, read_guard='DENY_BY_DEFAULT')) + '\n', encoding='utf8')
    manifest(out)
    return result
