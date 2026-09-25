"""Conditional structural constraints, without selecting an accepted hierarchy."""
from collections import defaultdict
from itertools import product


class Union:
    def __init__(self, nodes):
        self.parent = {n: n for n in nodes}

    def find(self, node):
        while self.parent[node] != node:
            self.parent[node] = self.parent[self.parent[node]]
            node = self.parent[node]
        return node

    def join(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[max(a, b)] = min(a, b)


def validate_variant(edges):
    """Validate a hypothetical assignment; candidate pool itself is not rejected."""
    nodes = {n for e in edges for n in (e['source'], e['target'])}
    union = Union(nodes)
    mothers = defaultdict(set)
    for e in edges:
        if e['relation'] == 'PARATACTIC':
            union.join(e['source'], e['target'])
        elif e['relation'] == 'HYPOTACTIC':
            mothers[e['target']].add(e['source'])
        else:
            raise ValueError('auxiliary edge cannot assemble hierarchy')
    errors = []
    if any(len(m) > 1 for m in mothers.values()):
        errors.append('MULTIPLE_SELECTED_MOTHERS')
    graph = defaultdict(set)
    for target, sources in mothers.items():
        for source in sources:
            a, b = union.find(source), union.find(target)
            if a == b:
                errors.append('STRICT_AND_EQUAL_LEVEL_CONTRADICTION')
            graph[a].add(b)
    # Kahn's algorithm avoids recursion limits for long source texts.
    roots = {union.find(n) for n in nodes}
    incoming = {n: 0 for n in roots}
    for targets in graph.values():
        for target in targets:
            incoming[target] += 1
    queue = [n for n, degree in incoming.items() if not degree]
    visited = 0
    while queue:
        node = queue.pop(); visited += 1
        for target in graph[node]:
            incoming[target] -= 1
            if incoming[target] == 0:
                queue.append(target)
    if visited != len(roots):
        errors.append('CYCLE_AFTER_PARALLEL_CONTRACTION')
    return sorted(set(errors))


def analyze_graph(edges, positions, max_assignments=64):
    edge_map = {e['edge_id']: e for e in edges}
    if len(edge_map) != len(edges):
        raise ValueError('duplicate graph edge identity')
    nodes = {n for e in edges for n in (e['source'], e['target'])}
    union = Union(nodes)
    by_target, by_pair, touching = defaultdict(list), defaultdict(list), defaultdict(list)
    for e in edges:
        union.join(e['source'], e['target'])
        by_target[e['target']].append(e)
        by_pair[e['source'], e['target']].append(e)
        touching[e['source']].append(e['edge_id']); touching[e['target']].append(e['edge_id'])
    conflicts = []
    def conflict(kind, severity, options, target, explanation):
        conflicts.append(dict(conflict_id='GC%08d' % (len(conflicts) + 1), kind=kind,
                              severity=severity, edge_ids=sorted(options), target_clause_id=target,
                              activation='ONLY_IF_INCOMPATIBLE_EDGES_SELECTED_TOGETHER' if severity == 'HARD_CONFLICT' else 'CONDITIONAL_LEVEL_REASSESSMENT',
                              explanation=explanation, automatic_candidate_rejection=False))
    for target, options in sorted(by_target.items()):
        hypo = [e['edge_id'] for e in options if e['relation'] == 'HYPOTACTIC']
        para = [e['edge_id'] for e in options if e['relation'] == 'PARATACTIC']
        if len(hypo) > 1:
            conflict('AT_MOST_ONE_MOTHER', 'HARD_CONFLICT', hypo, target, 'Any two distinct selected mothers violate single mother; candidates remain.')
        if hypo and para:
            conflict('COMPETING_PARALLEL_CHAIN', 'SOFT_CONFLICT', hypo + para, target, 'Embedding may require a different placement of parallel peers.')
    for (source, target), options in sorted(by_pair.items()):
        if {e['relation'] for e in options} == {'HYPOTACTIC', 'PARATACTIC'}:
            conflict('STRICT_VS_EQUAL_LEVEL', 'HARD_CONFLICT', [e['edge_id'] for e in options], target,
                     'The same pair cannot be both strict hierarchical and equal-level in one assignment.')
    components = defaultdict(list)
    for e in edges:
        components[union.find(e['source'])].append(e)
    component_rows, variant_rows = [], []
    conflicts_by_edge = defaultdict(list)
    for c in conflicts:
        for eid in c['edge_ids']:
            conflicts_by_edge[eid].append(c)
    for number, (_, options) in enumerate(sorted(components.items()), 1):
        component_id = 'VC%06d' % number
        ids = sorted(e['edge_id'] for e in options)
        affected = sorted({n for e in options for n in (e['source'], e['target'])})
        symbolic = len(options) >= max_assignments.bit_length()
        local_conflicts = sorted({c['conflict_id'] for eid in ids for c in conflicts_by_edge[eid]})
        component_rows.append(dict(component_id=component_id,
            representation='SYMBOLIC_VARIANT_COMPONENT' if symbolic else 'MATERIALIZED_VARIANT_COMPONENT',
            affected_clauses=affected, alternative_edge_ids=ids, conflict_ids=local_conflicts,
            constraints=['AT_MOST_ONE_SELECTED_MOTHER_PER_DAUGHTER', 'PARATAXIS_EQUAL_LEVEL',
                         'HYPOTAXIS_STRICT_LEVEL', 'ACYCLIC_AFTER_PARALLEL_CONTRACTION'],
            assignment_semantics='ANY_SUBSET_SATISFYING_CONSTRAINTS; UNSELECTED_MEANS_UNDECIDED',
            affected_textual_levels='RELATIVE_ONLY_NOT_CANONICAL', accepted_variant=''))
        if not symbolic:
            for bits in product((False, True), repeat=len(options)):
                selected = [e for e, bit in zip(options, bits) if bit]
                if not validate_variant(selected):
                    variant_rows.append(dict(variant_id=component_id + '-V%06d' % (len(variant_rows) + 1),
                        component_id=component_id, selected_edge_ids=sorted(e['edge_id'] for e in selected),
                        status='HYPOTHETICAL_NOT_ADJUDICATED', human_accepted=False))
    compatibility = []
    for e in edges:
        related = conflicts_by_edge[e['edge_id']]
        peers = by_target[e['target']]
        compatibility.append(dict(edge_id=e['edge_id'],
            compatible_existing_relations='CONDITIONAL; EVALUATE_SYMBOLIC_COMPONENT_CONSTRAINTS',
            conflicting_relations=[c['conflict_id'] for c in related if c['severity'] == 'HARD_CONFLICT'],
            relations_requiring_reassignment=[c['conflict_id'] for c in related if c['severity'] == 'SOFT_CONFLICT'],
            parallel_chain_effect='EQUAL_LEVEL_CONSTRAINT' if e['relation'] == 'PARATACTIC' else 'REASSESS_PARALLEL_PEERS',
            embedding_effect='STRICT_LEVEL_CONSTRAINT' if e['relation'] == 'HYPOTACTIC' else 'NO_MOTHER_ASSIGNED',
            intervening_clause_effect=dict(source_position=positions[e['source']], target_position=positions[e['target']],
                                           status='PLACEMENT_NOT_INFERRED_FROM_SPAN'),
            candidate_mother_competition=dict(table='12_provisional_relation_graph.csv', target=e['target'], relation='HYPOTACTIC',
                                              selector='ALL_MATCHING_EDGES'),
            cycle_check='GLOBAL_PARALLEL_CONTRACTION_CONSTRAINT', chosen=False))
    return dict(conflicts=conflicts, compatibility=compatibility, components=component_rows, variants=variant_rows)
