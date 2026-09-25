"""Larger-unit, reference and poetic observations remain separate typed layers."""
from collections import defaultdict, deque
from milal_mfr02r_features import pair_facts

LAYERS = ('TEXTUAL_SYNTACTIC_LAYER', 'PARTICIPANT_REFERENCE_LAYER', 'POETIC_PROSODIC_LAYER')
SOURCE_WORK = 'PROSODIC_INFLUENCE_ON_TEXT_SYNTAX_OF_LAMENTATIONS'


def labels_for(facts, definitions, phase):
    observed = dict(facts, lexical_and_formal_correspondence=bool(facts.get('lexical_continuity') and facts.get('formal_correspondence')))
    labels = []
    for definition in definitions['labels']:
        if definition['implementation_status'] == 'PASS2_ONLY' and phase != 2:
            continue
        pattern = definition['observable_pattern']
        if set(pattern) != {'all'}:
            raise ValueError('unsupported label query operator')
        if all(observed.get(k, False) for k in pattern['all']):
            labels.append(dict(label_id=definition['label_id'], category=definition['category'],
                source_author=definition['source_author'], source_work=definitions['source_work'], source_section=definition['source_section'],
                source_page_if_verified=definition['source_page_if_verified'],
                adoption_status=definition['adoption_status'], observed_predicates=pattern['all']))
    return labels


def unit_candidates(edges, features, compact=False):
    """Conditional reachability objects, not unions asserted as coherent paragraphs.

    Every path is represented by the complete induced edge graph. A member is
    present only when a selected coherent assignment contains a path to it.
    No span filling, literary segments or accepted database hierarchy is used.
    """
    outgoing = defaultdict(list)
    for edge in edges:
        if edge['relation'] == 'HYPOTACTIC':
            outgoing[edge['source']].append(edge)
    positions = {f['clause_id']: f['position'] for f in features}
    if compact:
        order = [f['clause_id'] for f in features]
        reach = {cid: 1 << positions[cid] for cid in order}
        for cid in reversed(order):
            for edge in outgoing[cid]:
                if positions[edge['target']] <= positions[cid]:
                    raise ValueError('unit reachability requires preceding-source DAG')
                reach[cid] |= reach[edge['target']]
        return [dict(unit_id='UC-' + str(cid), opening_clause=cid, closing_clause_candidate='',
            member_clauses=[], member_clause_selector=dict(inventory='02_clause_feature_inventory.csv',
                ordering='position', membership_bitset_hex=hex(reach[cid])),
            hierarchy_depth_candidate='ASSIGNMENT_DEPENDENT', parent_unit_candidate='',
            derivation_source='RELATION_COMPONENT_DERIVED',
            membership_semantics='CONDITIONAL_REACHABILITY_NOT_SIMULTANEOUS_MEMBERSHIP',
            conditional_edge_ids=dict(table='12_provisional_relation_graph.csv', relation='HYPOTACTIC',
                source_in_member_selector=True, selection='ALL_MATCHING_EDGES'),
            source_author='BOSMAN', source_work=SOURCE_WORK, source_section='9.1 / 13.3', source_page_if_verified=[204, 253],
            adoption_status='GENERALIZED_FOR_MILAL') for cid in sorted(outgoing) if outgoing[cid]]
    result = []
    for opening in sorted(outgoing):
        reached = {opening}; queue = deque([opening]); witness_edges = set()
        while queue:
            node = queue.popleft()
            for edge in outgoing[node]:
                witness_edges.add(edge['edge_id'])
                if edge['target'] not in reached:
                    reached.add(edge['target']); queue.append(edge['target'])
        result.append(dict(unit_id='UC-' + str(opening), opening_clause=opening,
            closing_clause_candidate='', member_clauses=sorted(reached),
            hierarchy_depth_candidate='ASSIGNMENT_DEPENDENT', parent_unit_candidate='',
            derivation_source='RELATION_COMPONENT_DERIVED',
            membership_semantics='CONDITIONAL_REACHABILITY_NOT_SIMULTANEOUS_MEMBERSHIP',
            conditional_edge_ids=sorted(witness_edges), source_author='BOSMAN', source_work=SOURCE_WORK, source_section='9.1 / 13.3',
            source_page_if_verified=[204, 253], adoption_status='GENERALIZED_FOR_MILAL'))
    return result


def unit_reference_evidence(units, features, edges, allowed_targets=None):
    by_id = {f['clause_id']: f for f in features}
    target_png, target_lex = defaultdict(set), defaultdict(set)
    for target in features:
        for value in target['reference_png']:
            target_png[value].add(target['clause_id'])
        for value in target['participants']:
            target_lex[value].add(target['clause_id'])
    outgoing = defaultdict(list)
    for edge in edges:
        if edge['relation'] == 'HYPOTACTIC':
            outgoing[edge['source']].append(edge)
    for unit in units:
        sid = unit['opening_clause']; source = by_id[sid]
        # A shortest path is a minimal witness, not a preferred hierarchy. The
        # full conditional unit edge set retains every other possible path.
        paths = {sid: []}; queue = deque([sid])
        while queue:
            current = queue.popleft()
            for edge in outgoing[current]:
                if edge['target'] not in paths:
                    paths[edge['target']] = paths[current] + [edge['edge_id']]
                    queue.append(edge['target'])
        for antecedent_id in unit['member_clauses']:
            if antecedent_id == sid:
                continue
            antecedent = by_id[antecedent_id]
            possible = set()
            for value in antecedent['source_png']:
                possible |= target_png[value]
            for value in antecedent['participants']:
                possible |= target_lex[value]
            if allowed_targets is not None:
                possible &= allowed_targets
            for tid in sorted(possible):
                target = by_id[tid]
                if target['position'] <= antecedent['position']:
                    continue
                direct = pair_facts(source, target)['reference_continuity'] or bool(source['participants'] & target['participants'])
                if direct:
                    continue  # Direct evidence is already losslessly recorded in the pair matrix.
                yield dict(source_clause_id=sid, target_clause_id=tid, source_unit_candidate_id=unit['unit_id'],
                    target_unit_candidate_id='UC-' + str(tid) if tid in outgoing else '',
                    direct_reference_match=bool(direct), unit_internal_reference_match=True,
                    antecedent_clause_id=antecedent_id, antecedent_unit_id=unit['unit_id'],
                    reference_depth=len(paths[antecedent_id]), reference_hidden_in_larger_unit=not bool(direct),
                    required_selected_path=paths[antecedent_id], all_alternative_paths_reference=unit['unit_id'],
                    reference_identity_status='UNRESOLVED', evidence_level='LARGER_UNIT_EVIDENCE',
                    candidate_status='UNIT_CONTEXT_REFERENCE_CANDIDATE', syntactic_mother='',
                    source_author='BOSMAN', source_work=SOURCE_WORK, source_section='9.1', source_page_if_verified=204, adoption_status='GENERALIZED_FOR_MILAL')


def symbolic_unit_references(units, features):
    """Exact factorization of unit/antecedent/target triples, without truncation."""
    by_png, by_lex = defaultdict(int), defaultdict(int)
    for f in features:
        bit = 1 << f['position']
        for value in f['source_png']:
            by_png[value] |= bit
        for value in f['participants']:
            by_lex[value] |= bit
    matches = []
    for target in features:
        bits = 0
        for value in target['reference_png']:
            bits |= by_png[value]
        for value in target['participants']:
            bits |= by_lex[value]
        matches.append(bits & ((1 << target['position']) - 1))
    position = {f['clause_id']: f['position'] for f in features}
    for unit in units:
        members = int(unit['member_clause_selector']['membership_bitset_hex'], 16)
        opening = 1 << position[unit['opening_clause']]
        targets = []; witnesses = 0
        for target, antecedents in zip(features, matches):
            if not (antecedents & opening) and members & antecedents:
                targets.append(target['clause_id']); witnesses += (members & antecedents).bit_count()
        if targets:
            yield dict(source_clause_id=unit['opening_clause'], source_unit_candidate_id=unit['unit_id'],
                target_clause_ids=targets, representation='EXACT_FACTORIZED_UNIT_REFERENCE_SET',
                target_count=len(targets), antecedent_target_pair_count=witnesses,
                antecedent_selector=dict(unit_id=unit['unit_id'], matching='SOURCE_PNG_INTERSECTS_TARGET_REFERENCE_PNG_OR_SHARED_PARTICIPANT_LEXEME',
                    ordering='ANTECEDENT_PRECEDES_TARGET', exclude_direct_opening_match=True),
                path_selector=dict(graph='12_provisional_relation_graph.csv', relation='HYPOTACTIC',
                    path='ALL_SELECTED_COHERENT_PATHS_FROM_OPENING_TO_ANTECEDENT'),
                reference_depth='RESOLVED_BY_PATH_QUERY; ASSIGNMENT_DEPENDENT',
                reference_identity_status='UNRESOLVED', reference_hidden_in_larger_unit=True,
                evidence_level='LARGER_UNIT_EVIDENCE', candidate_status='UNIT_CONTEXT_REFERENCE_CANDIDATE', syntactic_mother='',
                source_author='BOSMAN', source_work=SOURCE_WORK, source_section='9.1', source_page_if_verified=204, adoption_status='GENERALIZED_FOR_MILAL')


def expand_unit_reference(record, unit, features, edges, target_clause_id=None):
    """Resolve exact node identities and minimal path witnesses on demand."""
    bits = int(unit['member_clause_selector']['membership_bitset_hex'], 16)
    expanded = dict(unit, member_clauses=[f['clause_id'] for f in features if bits & (1 << f['position'])])
    targets = set(record['target_clause_ids'])
    if target_clause_id is not None:
        targets &= {target_clause_id}
    yield from unit_reference_evidence([expanded], features, edges, targets)


def context_query(source, target, features, units):
    positions = {f['clause_id']: f['position'] for f in features}
    a, b = positions[source], positions[target]
    return dict(previous_clause=features[b - 1]['clause_id'] if b else None,
                next_clause=features[b + 1]['clause_id'] if b + 1 < len(features) else None,
                source_containing_unit=[u['unit_id'] for u in units if source in u['member_clauses']],
                target_containing_unit=[u['unit_id'] for u in units if target in u['member_clauses']],
                intervening_clauses=[f['clause_id'] for f in features[a + 1:b]],
                preceding_frame_candidates=[f['clause_id'] for f in features[:b] if f['frame']],
                following_frame_candidates=[f['clause_id'] for f in features[b + 1:] if f['frame']],
                participant_occurrences_within_units='CONDITIONAL_MEMBERSHIP_AND_SOURCE_NODE_LOOKUP')


def poetic_observation(source, target, facts, definitions, annotations=None):
    labels = [r for r in labels_for(facts, definitions, 2) if r['category'] == 'POETIC_PROSODIC_LABELS']
    boundary = 'UNKNOWN_POETIC_BOUNDARY'; boundary_status = 'PROSODIC_NOT_AVAILABLE'
    if annotations is not None:
        if not annotations.get('verified_source_sha256'):
            raise ValueError('unverified poetic annotation')
        a = annotations['clause_units'].get(source['clause_id'])
        b = annotations['clause_units'].get(target['clause_id'])
        if a is not None and b is not None:
            boundary = 'WITHIN_SAME_POETIC_UNIT' if a == b else 'CROSSES_POETIC_UNIT_BOUNDARY'
            boundary_status = 'PROSODIC_SUPPORT' if a == b else 'PROSODIC_COUNTEREVIDENCE'
    return dict(source_clause_id=source['clause_id'], target_clause_id=target['clause_id'],
                layer='POETIC_PROSODIC_LAYER', relation='POETIC_STRUCTURAL_CORRESPONDENCE' if labels else 'NO_VERIFIED_POETIC_RELATION',
                labels=labels, observed_pattern_status='OBSERVED' if labels else 'NOT_AVAILABLE',
                prosodic_status='PROSODIC_NOT_VERIFIED' if labels else 'PROSODIC_NOT_AVAILABLE',
                poetic_boundary=boundary, boundary_status=boundary_status,
                exception_status='POETRY_AWARE_EXCEPTION_CANDIDATE' if labels and (facts.get('embedded_reference') or facts.get('participant_interplay')) else '',
                syntactic_override=False, canonical_boundary='', source_author='BOSMAN', source_work=SOURCE_WORK, source_section='12.1 / 13.2',
                source_page_if_verified=[246, 252], adoption_status='GENERALIZED_FOR_MILAL')


def program_human_state(proposed, human_decision):
    allowed = {'': 'UNDECIDED', 'ACCEPTED': 'ACCEPTED', 'REJECTED': 'REJECTED', 'ALTERNATIVE_RETAINED': 'ALTERNATIVE_RETAINED'}
    if human_decision not in allowed:
        raise ValueError('unrecognized explicit human decision')
    return 'PROGRAM_' + ('PROPOSED' if proposed else 'NOT_PROPOSED') + '_HUMAN_' + allowed[human_decision]


def decision_learning_row(candidate, human_event=None):
    event = human_event or {}
    if event and not all(event.get(k) for k in ('event_id', 'reviewer', 'rationale', 'source_sha256')):
        raise ValueError('human event lacks provenance')
    return dict(candidate, program_proposal_preserved=True, human_event=event,
                human_decision=event.get('decision', ''), human_rationale=event.get('rationale', ''),
                competing_accepted_candidate=event.get('competing_accepted_candidate', ''),
                final_status=program_human_state(candidate['program_proposed'], event.get('decision', '')),
                candidate_retained=True, model_training_performed=False)
