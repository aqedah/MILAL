"""Control-blind, non-qualifying diagnostics over fixed Q1 source units.

Predicates decompose the frozen conjunction; they do not construct alternative
units or evaluate hypothetical relaxed qualification. No control identifiers,
book names, expected counts, scores or recovery thresholds belong here.
"""
from collections import Counter
from milal_mfr02r_data import encode

RESTRICTIONS = ('CONTIGUOUS_NATIVE_MULTICLAUSE', 'CORRESPONDING_LEXICAL_NP',
                'CORRESPONDING_GRAMMATICAL_POSITION', 'NON_SPEECH_PREDICATE',
                'IDENTICAL_FULL_SIGNATURE')


def competition_count(records):
    """Tables contain every target; only distinct positive alternatives compete."""
    count=0; seen=set()
    for row in records:
        if row['target_id'] in seen:raise ValueError('duplicate competition target')
        seen.add(row['target_id'])
        actual=len(set(row['qualified_alternatives']))>1
        if row['competition'] is not actual:raise ValueError('competition flag disagrees with alternatives')
        count+=actual
    return count


def restriction_vector(left, right):
    def mentions(unit, positional):
        offsets = {cid: i for i, cid in enumerate(unit['members'])}
        return {(offsets[m['clause_id']], m['function'], m['lex']) if positional else m['lex']
                for m in unit['explicit_np_witnesses']}
    return dict(zip(RESTRICTIONS, (
        len(left['members']) > 1 and len(right['members']) > 1,
        bool(mentions(left, False) & mentions(right, False)),
        bool(mentions(left, True) & mentions(right, True)),
        bool(left['nonformula_predicate_witnesses'] and right['nonformula_predicate_witnesses']),
        left['signature'] == right['signature'])))


def diagnose_pair(index, source, target):
    left, right = index.units[str(source)], index.units[str(target)]
    vector = restriction_vector(left, right)
    # This equality is checked on every empirical diagnostic pair, not assumed.
    original = bool(left['eligible'] and right['eligible'] and left['signature'] == right['signature'])
    if all(vector.values()) != original:
        raise ValueError('diagnostic decomposition differs from frozen SB06')
    return dict(restrictions=vector, failed_restrictions=[k for k, v in vector.items() if not v],
                frozen_sb06_conjunction=original,
                source_unit_members=left['members'], target_unit_members=right['members'])


def sensitivity(records, scope):
    counts = Counter(); n = 0; patterns = Counter()
    for record in records:
        n += 1
        failed = record['failed_restrictions']
        patterns[encode(failed)] += 1
        for key in RESTRICTIONS:
            counts[key, 'pass' if key not in failed else 'sole' if len(failed) == 1 else 'joint'] += 1
    return [dict(scope=scope, restriction=key, population=n,
                 passed=counts[key, 'pass'], excluded_solely=counts[key, 'sole'],
                 excluded_with_others=counts[key, 'joint'],
                 population_definition='ALL_FROZEN_ORIGINAL_RELATION_PAIRS; FIXED_Q1_UNITS',
                 interpretation='JOINT_PREDICATE_FAILURE_NOT_COUNTERFACTUAL_RELATION_RECOVERY',
                 failure_pattern_counts=dict(sorted(patterns.items()))) for key in RESTRICTIONS]


def binding_obstacles(index, source, target):
    source, target = str(source), str(target)
    direct = index.native(source, target)
    constituent = []
    for parent in index.parents[target]:
        edges = [e for e in index.native(parent, target)
                 if int(e['head_node']) in index.rows[parent]['word_ids']]
        constituent.append(dict(antecedent=parent, exact_word_edges=edges,
                                source_native_paths=index.dependency_paths(source, parent)))
    witnesses=index.bindings(source,target)
    return dict(direct_native_edges=direct, constituent_attempts=constituent,
                sb01_requirement_met=bool(direct),
                sb03_requirement_met=any(x['exact_word_edges'] and x['source_native_paths'] for x in constituent),
                sb04_active_context_requirement_met=any(w['mechanism']=='SB04' for w in witnesses),
                sb04_adjacent=index.index[target]==index.index[source]+1,
                sb04_requirement='NATIVE_EDGE_PLUS_ADJACENCY_PLUS_EXPLICIT_SECONDARY_PARTICIPANT_RECURRENCE',
                sb06=diagnose_pair(index, source, target),
                source_configuration=index.units[source], target_configuration=index.units[target])


def classify_nonretention(record, diagnostic):
    """Evidence review labels, never ground-truth correctness or new relations."""
    if record['qualified_relations']:
        return ['RETAINED']
    if not record['original_relations']:
        return ['A_NO_ORIGINAL_RELATION_TO_RETAIN']
    labels = ['B_UNRESOLVED_EVIDENCE']
    if 'PARATACTIC' in record['original_relations'] and diagnostic['sb06']['failed_restrictions']:
        labels += ['C_SB11_SB12_NOT_IMPLEMENTED', 'D_CONSERVATIVE_SB06_SUBSET']
    if 'HYPOTACTIC' in record['original_relations'] and not diagnostic['sb01_requirement_met'] and not diagnostic['sb03_requirement_met']:
        labels += ['C_OTHER_BINDING_ADAPTERS_UNAVAILABLE_NOT_PROVEN_APPLICABLE']
    return labels
