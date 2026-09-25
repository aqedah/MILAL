"""Source-qualified candidate grammar. No human outcomes or control references."""
import json
from pathlib import Path

DIMENSIONS = ('GRAPHEME', 'WORD', 'PHRASE', 'CLAUSE', 'TIME', 'LOCATION',
              'PARTICIPANT', 'REFERENCE', 'DOMAIN', 'LEXICAL', 'RHETORICAL_SECONDARY',
              'GRAMMATICAL_CORRESPONDENCE', 'TEXT_SYNTACTIC_CORRESPONDENCE',
              'LEXICAL_CORRESPONDENCE', 'SEMANTIC_CORRESPONDENCE')
SCHEMA_FIELDS = ('required_features', 'supporting_features', 'counterevidence_features',
                 'source_function_candidate', 'target_function_candidate')
_TYPE_CACHE = {}


def load_registry(path):
    _TYPE_CACHE.clear()
    registry = json.loads(Path(path).read_text(encoding='utf8'))
    rules = registry['rules']
    if len({r['rule_id'] for r in rules}) != len(rules):
        raise ValueError('duplicate rule identity')
    for r in rules:
        if r['adoption'] == 'DIRECTLY_ADOPTED':
            if r['source_reference']['jin_section'] == 'UNKNOWN_NOT_VERIFIED':
                raise ValueError('unverified directly adopted rule')
            if any(r['field_provenance'].get(k) != 'GENERALIZED_FOR_MILAL' for k in SCHEMA_FIELDS):
                raise ValueError('implementation/source conflation')
        elif r['source_author'] == 'WALTON':
            if not all(r.get(k) for k in ('source_work', 'source_section', 'source_page', 'adoption_status')):
                raise ValueError('Walton provenance incomplete')
        elif r.get('enabled', True):
            raise ValueError('unverified additional rule enabled')
        if not r['required_features'] or any(not group for group in r['required_features']):
            raise ValueError('type-only rule')
    return registry


def type_matches(patterns, feature, registry):
    return any(p == 'ANY' or p in feature['types'] or
               p == 'MAIN' and feature['clause_type'] not in registry['excluded_main_types']
               for p in patterns)


def match_rules(source, target, facts, registry):
    matches = []
    key = (id(registry), source['clause_type'], frozenset(source['types']), target['clause_type'], frozenset(target['types']))
    if key not in _TYPE_CACHE:
        _TYPE_CACHE[key] = (registry, [r for r in registry['rules'] if r.get('enabled', True)
            and type_matches(r['source_clause_type'], source, registry)
            and type_matches(r['target_clause_type'], target, registry)])
    for rule in _TYPE_CACHE[key][1]:
        witnesses = [group for group in rule['required_features'] if all(facts.get(k) for k in group)]
        if witnesses:
            matches.append(dict(rule_id=rule['rule_id'], relation=rule['candidate_relation'],
                                required_feature_witnesses=witnesses,
                                counterevidence=[k for k in rule['counterevidence_features'] if facts.get(k)],
                                source_function_candidate=rule['source_function_candidate'],
                                target_function_candidate=rule['target_function_candidate'],
                                source_author=rule['source_author'], source_section=rule['source_section'],
                                adoption_status=rule['adoption_status'],
                                adjudicated_function='', status='PROVISIONAL_RELATION_CANDIDATE'))
    return matches
