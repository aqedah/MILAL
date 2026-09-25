"""Resolve a factorized reference set to exact antecedent nodes and path witnesses."""
import argparse
from pathlib import Path
from milal_mfr02r_data import rows, encode, verify_manifest
from milal_mfr02r_features import build_features
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_layers import expand_unit_reference
from milal_mfr_observation import observe


def resolve(directory, source, target, registry):
    directory = Path(directory)
    if not verify_manifest(directory):
        raise ValueError('query requires a complete verified scope')
    inventory = sorted(rows(directory / '02_clause_feature_inventory.csv'), key=lambda r: int(r['position']))
    raw, native = [], {}
    for r in inventory:
        raw.append(dict(clause_id=int(r['clause_id']), clause_atom_ids=r['clause_atom_ids'],
            atoms=r['CLAUSE']['atoms'], word_ids=r['word_ids'], words=r['WORD'], phrases=r['PHRASE'],
            book=r['book'], chapter=int(r['chapter']), verse=int(r['verse']), clause_type=r['clause_type'], domain=r['DOMAIN']['raw']))
        for edge in r['CLAUSE']['native_annotations']:
            key = (edge['dependent_node'], edge['head_node'], edge['rela'])
            native[key] = dict(dependent_node=key[0], head_node=key[1], rela=key[2])
    features = build_features(observe(raw), registry, native.values())
    edges = [dict(r, source=int(r['source']), target=int(r['target'])) for r in rows(directory / '12_provisional_relation_graph.csv') if r['relation'] in ('HYPOTACTIC', 'PARATACTIC')]
    units = {u['unit_id']: u for u in rows(directory / 'textual_unit_candidates.csv')}
    for record in rows(directory / 'participant_unit_reference_evidence.csv'):
        if int(record['source_clause_id']) != source:
            continue
        if 'target_clause_ids' not in record:
            if int(record['target_clause_id']) == target:
                yield record
        else:
            unit = units[record['source_unit_candidate_id']]
            unit['opening_clause'] = int(unit['opening_clause'])
            yield from expand_unit_reference(record, unit, features, edges, target)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('scope_directory'); p.add_argument('source_clause', type=int); p.add_argument('target_clause', type=int)
    args = p.parse_args()
    registry = load_registry(Path(__file__).resolve().parents[1] / 'config/clause_relation_grammar_v1.json')
    for result in resolve(args.scope_directory, args.source_clause, args.target_clause, registry):
        print(encode(result))
