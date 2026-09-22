"""Append supplied HSA2-F decisions; never select targets from textual geometry."""
from __future__ import annotations

import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import zipfile

import milal_hsa2_closure_audit as h2

h1 = h2.h1
ROOT = h2.ROOT
CONFIG = ROOT / 'config/hsa2_final_job.json'
CSV = ROOT / 'docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.csv'
MD = ROOT / 'docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2_FINAL.md'
FIELDS = ('judgment_id candidate_id ending_reference target_reference dimension '
          'selected_relation semantic_meaning original_status authority review_status '
          'supporting_judgment_ids decision_provenance reasoning').split()
sha, canonical = h2.sha, h2.canonical
REPORT = '04_job_27_31_closure_target_final_adjudication.md'


def require(ok, message):
    if not ok:
        raise ValueError('HSA2-F STOP: ' + message)


def table(files, name):
    return h1.read_csv(files[name])


def registry_bytes(rows):
    return h1.util.csv_bytes(rows, FIELDS).replace(b'\r\n', b'\n')


def markdown_table(rows):
    lines = []
    for row in rows:
        lines += ['### ' + row['judgment_id'], '', '| Field | Human-authored value |', '| --- | --- |']
        lines += ['| ' + k + ' | ' + str(row[k]).replace('|', '&#124;').replace('\n', '<br>') + ' |' for k in FIELDS]
        lines += ['']
    return '\n'.join(lines)


def receipts(cfg):
    return [dict(path=p, expected=d, actual=sha((ROOT / p).read_bytes())) for p, d in cfg['frozen_files'].items()]


def source(self_test=False):
    cfg = json.loads(CONFIG.read_text(encoding='utf-8'))
    frozen = receipts(cfg)
    require(all(r['actual'] == r['expected'] for r in frozen), 'frozen file changed')
    if self_test:
        from milal_hsa2_synthetic import source as synthetic
        old, rows, md = synthetic()
        files = h2.serialize(h2.build(old, rows, md), old)
        digest = sha(canonical({k: sha(v) for k, v in files.items()}).encode())
        inputs = []
    else:
        pin = cfg['hsa2_archive']
        archive = h1.src.archive((ROOT / pin['path']).read_bytes(), pin['sha256'], mr1=True)
        files, digest = archive['files'], archive['sha256']
        meta = json.loads(files['90_run_metadata.json'])
        gg = table(files, '08_gates.csv')
        require(meta['version'] == 'HSA2' and meta['status'] == 'PASS' and meta['mode'] == 'ACCEPTED_REAL_AUDIT_ONLY', 'unaccepted HSA2')
        require(len(gg) == meta['gate_count'] and all(r['status'] == 'PASS' for r in gg), 'HSA2 gates')
        require(files['01_hsa2_structural_judgments.csv'] == h2.CSV.read_bytes() and files['15_hsa2_human_registry.md'] == h2.MD.read_bytes(), 'HSA2 registry byte fidelity')
        require(files['14_frozen_hsa1_human_judgments.csv'] == h1.CSV.read_bytes(), 'HSA1 registry byte fidelity')
        old = h2.load()  # Frozen read-only exact-ID/accepted-archive adapter.
        require(h1.util.csv_bytes(h2.audit_links(h2.registry(), old)) == files['02_hsa2_source_links.csv'], 'exact source links differ')
        inputs = deepcopy(old['receipts']) + [dict(role='hsa2', path=pin['path'], sha256=digest, expected=digest)]
    return dict(mode='SYNTHETIC_AUDIT_ONLY' if self_test else 'ACCEPTED_REAL_AUDIT_ONLY',
                cfg=cfg, files=files, archive_sha256=digest, frozen=frozen, inputs=inputs)


def relations(rows):
    """Projection of human-authored fields only: no evidence, order or span input."""
    return [{k: r[k] for k in ('judgment_id', 'candidate_id', 'ending_reference', 'target_reference',
                               'dimension', 'selected_relation', 'semantic_meaning', 'authority', 'review_status')} for r in rows]


def decision_links(rows, s):
    result = []
    for r in rows:
        requests = [('03_closure_target_candidate_relations.csv', 'candidate_id', r['candidate_id'], 'RESOLVES_HISTORICAL_CANDIDATE')]
        requests += [('01_hsa2_structural_judgments.csv', 'judgment_id', ident, 'USES_PRIOR_HUMAN_JUDGMENT') for ident in json.loads(r['supporting_judgment_ids'])]
        for member, field, ident, relation in requests:
            matches = [(i, x) for i, x in enumerate(table(s['files'], member), 1) if x[field] == ident]
            require(len(matches) == 1, 'missing/ambiguous exact human ID ' + ident)
            number, original = matches[0]
            result.append(dict(judgment_id=r['judgment_id'], relationship=relation, target_id=ident,
                               archive_sha256=s['archive_sha256'], member=member,
                               member_sha256=sha(s['files'][member]), data_row=number,
                               row_sha256=sha(canonical(original).encode()), source_row=original))
    return result


def build(s):
    rows = h1.read_csv(CSV.read_bytes())
    require(rows and all(set(r) == set(FIELDS) for r in rows), 'final registry schema')
    model = dict(judgments=rows, relations=relations(rows), links=decision_links(rows, s),
                 historical=deepcopy(s['files']), markdown=MD.read_text(encoding='utf-8'))
    model['report'] = report(model, s)
    return model


def report(m, s):
    old = m['historical']
    lines = ['# Job 27–31 closure final adjudication — HSA2-F', '', '**Mode: ' + s['mode'] + '**', '',
             'Authority: researcher final review, 2026-09-22, recorded in the separate HSA2-F human registry.',
             'HSA2 archive SHA256: `' + s['archive_sha256'] + '`.', '',
             '## Exact evidence preserved from HSA2', '']
    scopes = table(old, '10_exact_marker_scopes.csv')
    links = table(old, '02_hsa2_source_links.csv')
    for ref in ('27:1', '29:1', '31:40'):
        scope = next(r for r in scopes if r['reference'] == ref and r['scope_type'] == 'EXACT_MR1_EVENT')
        r = json.loads(scope['source_row'])
        atoms = set(json.loads(scope['atom_ids']))
        clauses = sorted({json.loads(x['source_row'])['clause'] for x in links if x['evidence_id'].startswith('BHSA2021:clause:') and atoms.intersection(json.loads(x['atom_ids']))})
        lines += ['### Job ' + ref, '', r['surface_text'], '',
                  '- Evidence ID: `' + scope['evidence_id'] + '`',
                  '- Clause IDs: `' + canonical(clauses) + '`; atom IDs: `' + scope['atom_ids'] + '`',
                  '- Marker: `' + r['marker_family'] + ' / ' + r['marker_subtype'] + '`',
                  '- Exact locator: `' + scope['source_locator'] + '`', '']
    lines += ['The two openings have the same TAKE_MASHAL+AMR formula and matching corresponding atom/level signatures.',
              'The ending marker is its exact MR1 span, not the whole verse. Complete signatures, lexical facts,',
              'formal edges, context links and comparison controls remain unchanged under `hsa2/`.', '',
              '## Original history and final human resolution', '',
              'HSA2 evidence audit → UNRESOLVED → researcher human review → HSA2-F final adjudication.',
              'Original CT01/CT02/CT03 remain UNREVIEWED with UNRESOLVED selected fields in the copied historical table.',
              'Original HSA2-END-31 retains both UNRESOLVED closure fields and SPEECH_UNIT_END.', '',
              '| Candidate | Ending → target | Dimension | Final relation | Semantic meaning |',
              '| --- | --- | --- | --- | --- |']
    for r in m['relations']:
        lines.append('| ' + ' | '.join([r['candidate_id'], r['ending_reference'] + ' → ' + r['target_reference'], r['dimension'], r['selected_relation'], r['semantic_meaning']]) + ' |')
    lines += ['', 'NO_DIRECT_RELATION is restricted to the DIRECT_CLOSURE_TARGET dimension: it rejects a direct local',
              'target at 27:1, not every structural relation to the larger group. TERMINATES_ENCLOSING_GROUP is the',
              'existing vocabulary for the independent HIGHER_ORDER_TERMINAL_EFFECT. No parent/child edge is added.', '',
              '## Researcher reasoning; no automatic closure rule', '',
              'Marker evidence alone did not distinguish 27:1 from 29:1 as a direct target; HSA2 correctly left this unresolved.',
              'Prior human judgments establish 27:1 and 29:1 as SAME_LEVEL_SIBLING speech onsets. 29:1 is not a child',
              'or subordinate continuation of 27:1; 28:1 remains NO_BOUNDARY / CONTINUES_WITHIN 27:1.',
              'With that previously adjudicated hierarchy, the researcher identifies the locally active speech after',
              '29:1 as the speech opened at 29:1 and adjudicates 31:40 as its direct ending. The researcher also',
              'adjudicates termination of the 27:1–31:40 group. These are two separate claims.',
              'Adjacency alone was not used. No nearest-opening, chapter, shortest/longest-span, topic or commentary',
              'heuristic is implemented. This single human judgment is not generalized to other closures.', '',
              '## Provenance and unchanged scope', '',
              'The final CSV/Markdown record the supplied decision and reasoning; `02_final_decision_provenance.csv`',
              'links each final row to its original candidate and the exact prior human rows with member/row hashes.',
              f'Historical source/context links: {len(links)} unchanged. Added human-decision provenance links: {len(m["links"])}.',
              f'Historical directed relations: {len(table(old, "12_direct_human_relation_pairs.csv"))} unchanged; final typed relations: {len(m["relations"])} added.',
              'HSA1/HSA2 and frozen analytical cores remain unchanged. Dialogue cycles remain 6/6/4, no Zophar III.',
              'No whole-book hierarchy, automatic parent assignment or additional enclosure node is generated.', '']
    return '\n'.join(lines)


def gates(m, s):
    old = m['historical']
    rows = table(old, '01_hsa2_structural_judgments.csv')
    byid = {r['judgment_id']: r for r in rows}
    rr = m['relations']
    final = {r['candidate_id']: r for r in rr}
    candidates = table(old, '03_closure_target_candidate_relations.csv')
    pairs = table(old, '12_direct_human_relation_pairs.csv')
    cfg = s['cfg']
    check = {}
    def frozen(predicate):
        selected = [r for r in s['frozen'] if predicate(r['path'])]
        return bool(selected) and all(r['actual'] == r['expected'] == cfg['frozen_files'].get(r['path']) for r in selected)
    def decision(ident, target, dimension, relation):
        r = final.get(ident, {})
        return r.get('ending_reference') == '31:40' and r.get('target_reference') == target and r.get('dimension') == dimension and r.get('selected_relation') == relation
    def peer(source_id, target_id):
        r = byid[source_id]
        return r['hierarchy_relation'] == 'SAME_LEVEL_SIBLING' and target_id in json.loads(r['related_judgment_id_if_available'])
    check['HSA1_FROZEN'] = frozen(lambda p: 'hsa1' in p.lower() or p.endswith(('HUMAN_STRUCTURAL_ADJUDICATION.csv', 'HUMAN_STRUCTURAL_ADJUDICATION.md')))
    check['HSA2_HISTORY_TRACEABLE'] = old == s['files'] and len(candidates) == 3 and all(r['selected_relation'] == r['direct_closure_target'] == r['higher_order_terminal_effect'] == 'UNRESOLVED' and r['review_status'] == 'UNREVIEWED' for r in candidates) and byid['HSA2-END-31']['direct_closure_target'] == byid['HSA2-END-31']['higher_order_terminal_effect'] == 'UNRESOLVED'
    check['31_40_ENDING_RETAINED'] = byid['HSA2-END-31']['structural_function'] == 'SPEECH_UNIT_END' and any(r['reference'] == '31:40' and json.loads(r['source_row'])['marker_family'] == 'MR1_EXPLICIT_CLOSURE' for r in table(old, '10_exact_marker_scopes.csv'))
    check['DIRECT_LOCAL_29'] = decision('CT01', '29:1', 'DIRECT_CLOSURE_TARGET', 'DIRECT_LOCAL_CLOSURE')
    check['NO_DIRECT_LOCAL_27'] = decision('CT02', '27:1', 'DIRECT_CLOSURE_TARGET', 'NO_DIRECT_RELATION') and not any(r['target_reference'] == '27:1' and r['selected_relation'] == 'DIRECT_LOCAL_CLOSURE' for r in rr)
    check['HIGHER_GROUP_TERMINAL'] = decision('CT03', '27:1–31:40', 'HIGHER_ORDER_TERMINAL_EFFECT', 'TERMINATES_ENCLOSING_GROUP')
    check['LOCAL_HIGHER_INDEPENDENT'] = len(rr) == len(final) == 3 and final.get('CT01', {}).get('dimension') == 'DIRECT_CLOSURE_TARGET' and final.get('CT03', {}).get('dimension') == 'HIGHER_ORDER_TERMINAL_EFFECT' and final['CT01']['judgment_id'] != final['CT03']['judgment_id']
    check['27_29_PEERS'] = peer('HSA2-JOB-27', 'HSA2-JOB-29') and peer('HSA2-JOB-29', 'HSA2-JOB-27')
    check['29_NOT_CHILD_27'] = byid['HSA2-JOB-29']['hierarchy_relation'] not in ('CHILD_OF', 'CONTINUES_WITHIN') and not any(r['reference'] == '29:1' and r['related_reference'] == '27:1' and r['relation'] != 'SAME_LEVEL_SIBLING' for r in pairs)
    check['27_NOT_PARENT_29'] = byid['HSA2-JOB-27']['hierarchy_relation'] != 'HIERARCHICALLY_ABOVE' and not any(r['reference'] == '27:1' and r['related_reference'] == '29:1' and r['relation'] != 'SAME_LEVEL_SIBLING' for r in pairs)
    r28 = byid['HSA2-NO-28']
    check['28_NO_BOUNDARY_CONTINUES'] = r28['structural_function'] == 'NO_BOUNDARY' and r28['hierarchy_relation'] == 'CONTINUES_WITHIN' and json.loads(r28['related_reference']) == ['27:1']
    for i, count in enumerate(cfg['cycle_counts'], 1):
        cycle = [r for r in rows if r['human_group'] == f'CYCLE_{i}' and r['structural_function'] == 'SPEECH_UNIT_ONSET']
        check[f'CYCLE_{i}_COUNT'] = len(cycle) == count
    check['NO_ZOPHAR_III'] = not any(r['human_group'] == 'CYCLE_3' and r['human_speaker'] == 'Zophar' for r in rows)
    check['NO_NEAREST_OPENING_RULE'] = rr == relations(h1.read_csv(CSV.read_bytes())) and all(r['authority'] == 'RESEARCHER_FINAL_ADJUDICATION' for r in rr)
    check['MR1_UNCHANGED'] = frozen(lambda p: 'mr1' in p.lower())
    check['NO_WHOLE_BOOK_HIERARCHY'] = set(old) == set(s['files']) and pairs == table(s['files'], '12_direct_human_relation_pairs.csv') and rr == relations(m['judgments']) and len(rr) == 3
    check['NO_UNREVIEWED_PARENTAGE'] = all(r['review_status'] == 'REVIEWED' and r['selected_relation'] in ('DIRECT_LOCAL_CLOSURE', 'NO_DIRECT_RELATION', 'TERMINATES_ENCLOSING_GROUP') for r in rr) and pairs == table(s['files'], '12_direct_human_relation_pairs.csv')
    check['SOURCE_CONTEXT_LINKS_VALID'] = old['02_hsa2_source_links.csv'] == s['files']['02_hsa2_source_links.csv'] and m['links'] == decision_links(m['judgments'], s)
    check['ALL_FROZEN_FILES'] = len(s['frozen']) == len(cfg['frozen_files']) and frozen(lambda p: True)
    check['HUMAN_FILE_FIDELITY'] = registry_bytes(m['judgments']) == CSV.read_bytes() and markdown_table(m['judgments']) in m['markdown'] and m['markdown'] == MD.read_text(encoding='utf-8')
    check['CANDIDATE_ID_RESOLUTION'] = len(rr) == len(candidates) and {r['candidate_id'] for r in rr} == {r['candidate_id'] for r in candidates} and all(any(c['candidate_id'] == r['candidate_id'] and c['ending_reference'] == r['ending_reference'] and c['candidate_target_reference'] == r['target_reference'] and c['dimension'] == r['dimension'] and r['selected_relation'] in json.loads(c['review_options']) for c in candidates) for r in rr)
    check['REPORT_FIDELITY'] = m['report'] == report(m, s)
    check['DETERMINISTIC_OUTPUT'] = m == build(s)
    return [dict(gate=k, status='PASS' if v else 'FAIL') for k, v in check.items()]


def serialize(m, s):
    gg = gates(m, s)
    require(all(r['status'] == 'PASS' for r in gg), canonical([r for r in gg if r['status'] != 'PASS']))
    files = {'hsa2/' + n: b for n, b in m['historical'].items()}
    files.update({'01_final_human_adjudications.csv': registry_bytes(m['judgments']),
                  '02_final_decision_provenance.csv': h1.util.csv_bytes(m['links']),
                  '03_final_closure_relations.csv': h1.util.csv_bytes(m['relations']),
                  REPORT: m['report'].encode(), '05_final_human_adjudications.md': m['markdown'].encode()})
    meta = dict(version='HSA2-F', mode=s['mode'], status='PASS', gate_count=len(gg)+1,
                historical_archive_sha256=s['archive_sha256'], source_receipts=s['inputs'], frozen_receipts=s['frozen'],
                counts=dict(hsa1_judgments=len(table(m['historical'], '14_frozen_hsa1_human_judgments.csv')),
                            hsa2_judgments=len(table(m['historical'], '01_hsa2_structural_judgments.csv')),
                            final_judgments=len(m['judgments']), historical_relations=len(table(m['historical'], '12_direct_human_relation_pairs.csv')),
                            final_relations=len(m['relations']), historical_source_links=len(table(m['historical'], '02_hsa2_source_links.csv')),
                            final_human_provenance_links=len(m['links'])),
                code_sha256=sha(Path(__file__).read_bytes()), config_sha256=sha(CONFIG.read_bytes()),
                registry_sha256=sha(CSV.read_bytes()), registry_markdown_sha256=sha(MD.read_bytes()))
    files['90_run_metadata.json'] = h1.util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv', None)
        files['99_manifest_sha256.csv'] = h1.util.csv_bytes([dict(file=n, sha256=sha(b)) for n, b in sorted(files.items())])
    seal()
    gg.append(h1.util.manifest_gate(files))
    files['08_gates.csv'] = h1.util.csv_bytes(gg)
    seal()
    require(h1.util.manifest_ok(files), 'manifest')
    return files


def publish(files, out):
    out = Path(out).resolve()
    zp, log = out.with_name(out.name + '_results.zip'), out.with_name(out.name + '_run.log')
    require(not any(p.exists() for p in (out, zp, log)), 'output exists')
    require(h1.util.manifest_ok(files), 'publication manifest')
    for n, b in files.items():
        path = out / n
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b)
    with zipfile.ZipFile(zp, 'w') as z:
        for n, b in sorted(files.items()):
            info = zipfile.ZipInfo(n, (2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, b)
    with zipfile.ZipFile(zp) as z:
        require(z.testzip() is None and {n: z.read(n) for n in z.namelist()} == files, 'ZIP integrity')
    require({p.relative_to(out).as_posix(): p.read_bytes() for p in out.rglob('*') if p.is_file()} == files, 'disk integrity')
    meta = json.loads(files['90_run_metadata.json'])
    log.write_text(f'HSA2-F PASS\nMode {meta["mode"]}\nGates {meta["gate_count"]} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n', encoding='utf-8')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', required=True)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args(argv)
    s = source(args.self_test)
    files = serialize(build(s), s)
    require(files == serialize(build(s), s), 'deterministic serialization')
    require(files['01_final_human_adjudications.csv'] == CSV.read_bytes() and files['05_final_human_adjudications.md'] == MD.read_bytes(), 'final human byte fidelity')
    require(receipts(s['cfg']) == s['frozen'], 'frozen files changed during audit')
    for r in s['inputs']:
        require(sha((ROOT / r['path']).read_bytes()) == r['expected'], 'input changed during audit')
    publish(files, args.out)
    print('HSA2-F PASS ' + str(Path(args.out).resolve()))
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError, KeyError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(2)
