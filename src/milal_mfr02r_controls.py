"""Post-freeze empirical controls. Never imported by the blind worker."""
import json
from pathlib import Path
from collections import defaultdict
from itertools import product
from milal_mfr02r_data import rows, table, digest, encode, verify_manifest
from milal_mfr02r_graph import validate_variant


def reference(inventory, book, chapter, verse):
    found = [r for r in inventory if r['book'] == book and int(r['chapter']) == chapter and int(r['verse']) == verse]
    if not found:
        raise ValueError('exact control reference unavailable: %s %s:%s' % (book, chapter, verse))
    return sorted(found, key=lambda r: int(r['position']))


def inspect_targets(directory, references):
    inventory = list(rows(directory / '02_clause_feature_inventory.csv'))
    target_ids = {int(r['clause_id']) for book, chapter, verse in references for r in reference(inventory, book, chapter, verse)}
    for row in rows(directory / '09_candidate_evidence_matrix.csv'):
        if int(row['target_clause_id']) in target_ids:
            yield row


def candidate_edge(lookup, source, target, relation):
    row = lookup.get((source, target))
    return dict(source=source, target=target, relation=relation, pair_id=row['pair_id'], rule_ids=row['rule_ids']) if row and relation in row['relations'] else None


def triple_variants(lookup, panels):
    """Every exact clause triple, with no representative-clause selection."""
    for a, b, c in product(*panels):
        options = [('ALL_PARALLEL', [candidate_edge(lookup, a, b, 'PARATACTIC'), candidate_edge(lookup, a, c, 'PARATACTIC')]),
                   ('EMBEDDED_MIDDLE', [candidate_edge(lookup, a, b, 'HYPOTACTIC'), candidate_edge(lookup, a, c, 'PARATACTIC')])]
        for name, edges in options:
            yield dict(variant=name, exact_clause_ids=[a,b,c], actual_edges=edges,
                representable=all(edges) and not validate_variant(edges), status='HYPOTHETICAL_NOT_SELECTED')


def crossbook_relation_count(records, books):
    return sum(bool(r['relations']) and books[int(r['source_clause_id'])] != books[int(r['target_clause_id'])] for r in records)


def execute(blind, config_path, out, tf_path, registry, native):
    blind, out = Path(blind), Path(out)
    if not (blind / 'blind_freeze.json').is_file():
        raise ValueError('controls before blind freeze')
    freeze = json.loads((blind / 'blind_freeze.json').read_text())
    for scope, expected in freeze['scope_manifests'].items():
        if digest(blind / scope / '99_manifest_sha256.csv') != expected or not verify_manifest(blind / scope):
            raise ValueError('blind freeze changed')
    if set(freeze['scope_manifests']) != {'job'}:
        raise ValueError('only Job may enter primary blind freeze')
    config = json.loads(Path(config_path).read_text(encoding='utf8'))
    if config['phase'] != 'POST_BLIND_FREEZE_ONLY':
        raise ValueError('invalid control phase')
    if config.get('context_policy') != 'ONE_PRECEDING_VERSE_WITHIN_BOOK':
        raise ValueError('control context policy must be explicit and minimal')
    out.mkdir(parents=True, exist_ok=False)
    from milal_mfr02r_scope import fixture_references, read_references, evaluate_fixture
    fixture_results, fixture_receipts = {}, {}
    for name, references in fixture_references(config).items():
        observations, receipt = read_references(tf_path, references, include_preceding_verse=True)
        fixture_receipts[name] = receipt
        fixture_results[name] = evaluate_fixture(observations, registry, native)
        table(out / (name + '_fixture_source_clauses.csv'), (
            dict(clause_id=r['clause_id'],clause_atom_ids=r['clause_atom_ids'],word_ids=r['word_ids'],
                 book=r['book'],chapter=r['chapter'],verse=r['verse'],surface_hebrew=r['surface_hebrew'],
                 selection_reason=receipt['selection_reasons'][r['clause_id']]) for r in observations))
        table(out / (name + '_fixture_relation_checks.csv'), fixture_results[name]['candidates'])
        table(out / (name + '_fixture_global_configuration_checks.csv'), [dict(
            control_fixture_scope='EXPLICIT_REFERENCES_ONLY', source_clause_ids=receipt['selected_clause_ids'],
            candidate_only=True, **fixture_results[name]['fixture_graph'])])
    inventories = {name:result['inventory'] for name,result in fixture_results.items()}
    inventories['job'] = list(rows(blind / 'job' / '02_clause_feature_inventory.csv'))
    pent = inventories['pentateuch']
    def panel(book, ref):
        return [int(r['clause_id']) for r in reference(pent, book, *ref)]
    lev = config['leviticus']; lev_targets = panel(lev['book'], lev['target'])
    lev_sources = [(ref, panel(lev['book'], ref)) for ref in lev['sources']]
    lev_chain = [panel(lev['book'], ref) for ref in lev['parallel_chain']]
    num = config['numbers']; num_panels = [panel(num['book'], ref) for ref in num['references']]
    pent_cfg = config['pentateuch']; root_panels = [panel(pent_cfg['book'], ref) for ref in pent_cfg['roots']]
    target_panels = [panel(pent_cfg['book'], ref) for ref in pent_cfg['targets']]
    other_ids = [cid for book, chapter, verse in pent_cfg['other'] for cid in panel(book, [chapter, verse])]
    same_panels = [panel(book, [chapter, verse]) for book, chapter, verse in config['same_pattern']]
    selected = set(lev_targets + other_ids + [cid for group in [*lev_chain, *num_panels, *root_panels, *target_panels, *same_panels] for cid in group])
    lookup, all_candidates = {}, defaultdict(list)
    for row in fixture_results['pentateuch']['candidates']:
        sid, tid = int(row['source_clause_id']), int(row['target_clause_id'])
        if tid in selected:
            lookup[sid, tid] = row
            all_candidates[tid].append(row)
    def edge(source, target, relation):
        return candidate_edge(lookup, source, target, relation)
    lev_rows = []
    for ref, source_ids in lev_sources:
        actual = [lookup[s,t] for s,t in product(source_ids, lev_targets) if (s,t) in lookup]
        lev_rows.append(dict(source_reference=ref, source_clause_ids=source_ids, target_clause_ids=lev_targets,
            actual_candidates=actual, status='PARTIALLY_RECOVERED' if actual else 'NOT_RECOVERED', selected_winner=''))
    table(out / '19_lev25_26_control.csv', lev_rows)
    table(out / 'lev_parallel_chain_control.csv', (dict(source_clause_id=s, target_clause_id=t,
        actual_candidate=lookup.get((s,t), {}), parallel_candidate=edge(s,t,'PARATACTIC'),
        status='POST_FREEZE_CHECK_NOT_PRELOADED_ANSWER', selected_winner='') for s,t in product(*lev_chain)))
    num_rows = list(triple_variants(lookup, num_panels))
    table(out / '20_num26_variant_control.csv', num_rows)
    pent_rows = []
    for ref, roots in zip(pent_cfg['roots'], root_panels):
        for root in roots:
            choices = [[e for t in targets if (e := edge(root, t, 'HYPOTACTIC'))] for targets in target_panels]
            variants = [list(v) for v in product(*choices) if not validate_variant(v)]
            pent_rows.append(dict(root_reference=ref, root_clause_id=root, target_clause_panels=target_panels,
                candidate_edges_per_panel=choices, actual_variants=variants, representable=bool(variants),
                other_reference_candidates={str(t): all_candidates[t] for t in other_ids}, winner=''))
    table(out / '21_pentateuch_variant_control.csv', pent_rows)
    same_rows = []
    for ref, target_ids in zip(config['same_pattern'], same_panels):
        options = {str(tid): all_candidates[tid] for tid in target_ids}
        both = [tid for tid in target_ids if {'HYPOTACTIC', 'PARATACTIC'} <= {relation for option in all_candidates[tid] for relation in option['relations']}]
        same_rows.append(dict(target_reference=ref, target_clause_ids=target_ids, candidate_pairs=options,
            differing_levels_representable=bool(both), exact_targets_with_both_relations=both,
            level_status='NO_CANONICAL_LEVEL', same_pattern_not_level_equivalence=True))
    table(out / '22_same_pattern_different_level_control.csv', same_rows)
    table(out / 'job_control_candidate_universe.csv', inspect_targets(blind / 'job', config['job']))
    isa_bindings = fixture_results['isaiah']['bindings']
    table(out / 'oosting_control_bindings.csv', isa_bindings)
    from milal_mfr02r_layers import unit_candidates, symbolic_unit_references
    lam = fixture_results['lamentations']
    lam_edges = [dict(edge_id=r['pair_id']+'-'+relation,source=r['source_clause_id'],target=r['target_clause_id'],relation=relation)
                 for r in lam['candidates'] for relation in r['relations']]
    units = unit_candidates(lam_edges,lam['features'],compact=True)
    table(out / 'bosman_control_unit_references.csv', symbolic_unit_references(units,lam['features']))
    books = {int(r['clause_id']):r['book'] for r in inventories['pentateuch']}
    crossbook = {'explicit_fixtures': crossbook_relation_count(fixture_results['pentateuch']['candidates'],books)}
    per_triple = defaultdict(set)
    for row in num_rows:
        if row['representable']:
            per_triple[tuple(row['exact_clause_ids'])].add(row['variant'])
    status = dict(leviticus_candidates_recovered=sum(bool(r['actual_candidates']) for r in lev_rows),
        numbers_variants_representable=max((len(v) for v in per_triple.values()), default=0),
        pentateuch_variants_representable=len({tuple(r['root_reference']) for r in pent_rows if r['representable']}),
        same_pattern_different_level=sum(r['differing_levels_representable'] for r in same_rows),
        crossbook_candidate_counts=crossbook, oosting_binding_controls=len(isa_bindings),
        control_scope_inputs=list(inventories), controls_used_in_blind=False, winner_selected=False,
        control_fixture_scope='EXPLICIT_REFERENCES_ONLY', fixture_scope_receipts=fixture_receipts,
        full_pentateuch_analysis=False, primary_analysis_scope='JOB')
    (out / 'control_summary.json').write_text(encode(status) + '\n', encoding='utf8')
    for name, title in [('bosman_method_control_report.md', 'BOSMAN_INTEGRATION'), ('oosting_control_report.md', 'OOSTING_INTEGRATION')]:
        (out / name).write_text('# ' + title + '\n\nComputed post-freeze evidence is in the adjacent control CSV files.\nNo source author conclusion is selected as an answer.\n\n```json\n' + json.dumps(status, indent=2) + '\n```\n', encoding='utf8')
    return status
