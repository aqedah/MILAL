"""Blind candidate construction. Inputs are observations, grammar, native annotations."""
from collections import Counter, defaultdict
from pathlib import Path
from contextlib import ExitStack
from functools import lru_cache
from milal_mfr02r_data import Table, table, encode, manifest, digest, rows
from milal_mfr02r_features import build_features, preceding_sets, pair_facts, evidence_values
from milal_mfr02r_grammar import DIMENSIONS, match_rules
from milal_mfr02r_graph import analyze_graph
from milal_mfr02r_revision import RevisionHistory
from milal_mfr02r_layers import unit_candidates, unit_reference_evidence, labels_for, poetic_observation, decision_learning_row
from milal_mfr02r_layers import symbolic_unit_references
import milal_mfr02r_data as storage
from milal_mfr02r_valency import construction, internal_bindings, corpus_index, analogues, recursive_patterns, behavior_variation, tradition_evidence
from milal_mfr02r_valency import validate_comparison_index


DIMENSION_FACTS = dict(
    GRAPHEME=('explicit_subordinator', 'infinitive_preposition', 'reference_continuity'),
    WORD=('participant_continuity', 'reference_continuity', 'high_correspondence'),
    PHRASE=('formal_correspondence', 'high_correspondence'),
    CLAUSE=('native_subordinate', 'speech_domain_entry', 'nested_speech_entry'),
    TIME=('time_continuity', 'time_contrast', 'temporal_connection', 'frame_embedding'),
    LOCATION=('location_continuity', 'location_contrast', 'frame_embedding'),
    PARTICIPANT=('participant_continuity', 'participant_contrast', 'participant_interplay'),
    REFERENCE=('reference_continuity', 'embedded_reference', 'anaphoric_summary', 'anaphoric_embedding'),
    DOMAIN=('domain_continuity', 'domain_contrast', 'speech_domain_entry', 'nested_speech_entry'),
    LEXICAL=('lexical_continuity', 'sequence_correspondence', 'high_correspondence'),
    RHETORICAL_SECONDARY=(), GRAMMATICAL_CORRESPONDENCE=('same_clause_type', 'formal_correspondence'),
    TEXT_SYNTACTIC_CORRESPONDENCE=('participant_continuity', 'continued_secondary_participant', 'reference_continuity', 'time_contrast', 'location_contrast', 'domain_continuity'),
    LEXICAL_CORRESPONDENCE=('lexical_continuity', 'sequence_correspondence'), SEMANTIC_CORRESPONDENCE=())


@lru_cache(maxsize=8192)
def encoded_dimension(predicates, support, counterevidence):
    return encode(dict(predicates=list(predicates), support=support, counterevidence=list(counterevidence)))


@lru_cache(maxsize=65536)
def encoded_facts(items):
    return encode(dict(items))


def matrix_dimension(name, source, target, facts, matches, serialized=False):
    present = [k for k in DIMENSION_FACTS[name] if facts.get(k)]
    if name in ('RHETORICAL_SECONDARY', 'SEMANTIC_CORRESPONDENCE'):
        return dict(status='NOT_LOADED', support='NOT_AVAILABLE')
    relations = {m['relation'] for m in matches if any(set(group) & set(present) for group in m['required_feature_witnesses'])}
    direction = ('SUPPORTS_BOTH' if len(relations) > 1 else 'SUPPORTS_' + next(iter(relations)).replace('HYPOTACTIC', 'HYPOTAXIS').replace('PARATACTIC', 'PARATAXIS') if relations else
                 'COUNTEREVIDENCE' if any(k.endswith('_contrast') for k in present) else 'NEUTRAL')
    # The two clause IDs on the matrix row resolve the full observed values in
    # inventory[column=name]. Avoid copying the same word/phrase payload for
    # every pair, while preserving every observation and its exact identity.
    counter = [k for k in present if k.endswith('_contrast')]
    return encoded_dimension(tuple(present), direction, tuple(counter)) if serialized else dict(predicates=present, support=direction, counterevidence=counter)


def run_engine(observations, registry, native_edges, out, max_assignments=64, long_distance=20, label_definitions=None,
               comparison_index=None, analysis_scope='SYNTHETIC', comparison_scope='SYNTHETIC', qere=None):
    out = Path(out); out.mkdir(parents=True, exist_ok=False)
    constructions = [construction(r) for r in observations]
    bindings = list(internal_bindings(observations, constructions))
    table(out / 'construction_inventory.csv', constructions)
    table(out / 'clause_internal_binding_candidates.csv', bindings)
    table(out / 'resolved_clause_constructions.csv', (dict(raw_clause_atom_id=atom, resolved_clause_candidate_id=c['construction_id'],
        raw_clause_id=c['clause_id'], status='BHSA_CLAUSE_CONSTITUTION_PRESERVED', automatic_merge=False) for c in constructions for atom in c['clause_atom_ids']))
    table(out / 'valency_signatures.csv', (dict(construction_id=c['construction_id'], valency_signature_id=c['valency_signature_id'],
        valency_signature=c['valency_signature'], missing_arguments=c['missing_arguments']) for c in constructions))
    table(out / 'recursive_valency_patterns.csv', recursive_patterns(observations))
    comparison_index = comparison_index or corpus_index(constructions)
    validate_comparison_index(constructions, comparison_index)
    (out / 'corpus_analogue_index.json').write_text(encode(comparison_index) + '\n', encoding='utf8')
    table(out / 'corpus_analogue_evidence.csv', analogues(constructions, comparison_index, analysis_scope, comparison_scope, symbolic=True))
    table(out / 'clause_binding_revalidation.csv', (dict(original_candidate=[b['clause_atom_a'], b['clause_atom_b']],
        clause_binding_issue=b['binding_id'], valency_evidence=b['valency_slots'], corpus_analogue_evidence=b['corpus_analogues'],
        revalidation_status='RELATION_DEFERRED_PENDING_BINDING', replacement_construction=b['construction_id'],
        candidate_provenance='ATOM_LEVEL_HYPOTHESIS_NOT_PREVIOUS_ACCEPTED_RELATION') for b in bindings))
    features = build_features(observations, registry, native_edges)
    by_id = {f['clause_id']: f for f in features}
    table(out / '01_relation_grammar_registry.csv', registry['rules'], sorted({k for r in registry['rules'] for k in r}))
    inventory = []
    for f in features:
        row = f['row']
        inventory.append(dict(observation_id='OBS-' + str(f['clause_id']), clause_id=f['clause_id'],
            clause_atom_ids=row['clause_atom_ids'], word_ids=row['word_ids'], book=row['book'], chapter=row['chapter'], verse=row['verse'],
            position=f['position'], surface_hebrew=row['surface_hebrew'], clause_type=f['clause_type'],
            frame_candidate=f['frame'], functional_role_candidate=[], adjudicated_function='',
            temporal_progression_id='TIME-' + str(f['clause_id']), participant_configuration_id='PART-' + str(f['clause_id']),
            location_configuration_id='LOCA-' + str(f['clause_id']), domain_configuration_id='DOMAIN-' + str(f['clause_id']),
            **evidence_values(f)))
    table(out / '02_clause_feature_inventory.csv', inventory)
    for name, dimensions in [('03_time_evidence.csv', ['TIME']), ('04_location_evidence.csv', ['LOCATION']),
                             ('05_participant_reference_evidence.csv', ['PARTICIPANT', 'REFERENCE']), ('06_domain_evidence.csv', ['DOMAIN'])]:
        table(out / name, (dict(clause_id=r['clause_id'], clause_atom_ids=r['clause_atom_ids'],
            observation_id=r['observation_id'], **{d: r[d] for d in dimensions}, relation_engine_role='EVIDENCE_DIMENSION') for r in inventory))
    counts = Counter(clauses=len(features), clause_atoms=sum(len(f['row']['clause_atom_ids']) for f in features))
    edges, targets = [], []
    history_fields = ['history_id', 'pair_id', 'status', 'original_relation', 'new_evidence', 'trigger_clause', 'revised_relation', 'revision_reason', 'revision_scope', 'previous_sha256', 'generation_stage', 'engine_version', 'candidate_status', 'human_status', 'revision_event', 'evidence_added', 'evidence_removed', 'reason', 'history_sha256']
    history_table = Table(out / 'relation_revision_history.csv', history_fields)
    history = RevisionHistory(history_table.write)
    earlier_by_source = defaultdict(list)
    conflicts_between_sources = []
    graph_aux = {'formal_correspondence': 'FORMAL_CORRESPONDENCE', 'temporal_connection': 'TEMPORAL_RELATION',
                 'location_continuity': 'LOCATIVE_RELATION', 'participant_continuity': 'PARTICIPANT_RELATION',
                 'reference_continuity': 'REFERENCE_RELATION', 'domain_continuity': 'DOMAIN_RELATION', 'lexical_continuity': 'LEXICAL_RELATION'}
    with ExitStack() as stack:
        candidate_table = stack.enter_context(Table(out / '07_preceding_candidate_sets.csv', ['target_clause_id', 'target_clause_atom_ids', 'candidate_clause_ids', 'admission_evidence', 'outside_scope_status']))
        rule_table = stack.enter_context(Table(out / '08_relation_rule_matches.csv', ['pair_id', 'source_clause_id', 'target_clause_id', 'matches', 'nested_anchor_clause_ids']))
        matrix_table = stack.enter_context(Table(out / '09_candidate_evidence_matrix.csv', ['pair_id', 'target_clause_id', 'candidate_clause_id', 'distance_clauses', 'distance_words', 'rule_ids_matched', 'source_clause_type', 'target_clause_type', *DIMENSIONS, 'candidate_relations', 'facts']))
        relation_table = stack.enter_context(Table(out / '10_relation_candidates.csv', ['pair_id', 'source_clause_id', 'target_clause_id', 'relations', 'status', 'rule_ids', 'source_function_candidates', 'target_function_candidates', 'adjudicated_function', 'accepted_mother']))
        graph_table = stack.enter_context(Table(out / '12_provisional_relation_graph.csv', ['edge_id', 'source', 'target', 'relation', 'pair_id', 'rule_ids', 'status']))
        comparisons_table = stack.enter_context(Table(out / '11_candidate_comparison_cases.csv', ['case_id', 'target_clause_id', 'candidates', 'mother_candidate_count', 'mother_candidate_ids', 'winner', 'global_effect_reference']))
        for target, admitted in preceding_sets(features):
            tid = target['clause_id']
            candidate_table.write(dict(target_clause_id=tid, target_clause_atom_ids=target['row']['clause_atom_ids'],
                candidate_clause_ids=list(admitted), admission_evidence=admitted, outside_scope_status='OUTSIDE_SCOPE_NOT_TESTED'))
            candidates, mother_ids = [], []
            counts['targets_with_candidates' if admitted else 'targets_without_candidates'] += 1
            counts['targets_2plus' if len(admitted) > 1 else 'targets_one' if admitted else 'targets_zero'] += 1
            for sid in admitted:
                source = by_id[sid]
                if source['position'] >= target['position']:
                    raise ValueError('candidate is not preceding')
                pair_id = 'P%d-%d' % (sid, tid)
                facts = pair_facts(source, target)
                matches = match_rules(source, target, facts, registry)
                relations = sorted({m['relation'] for m in matches})
                status = 'MULTIPLE' if len(relations) > 1 else relations[0] if relations else 'FORMAL_ONLY' if facts['formal_correspondence'] else 'INSUFFICIENT'
                rule_ids = [m['rule_id'] for m in matches]
                if relations:
                    history.initialize(pair_id, relations, tid, rule_ids)
                    earlier_by_source[sid].append((pair_id, tid))
                jin = [m for m in matches if m['source_author'] == 'JIN']
                walton = [m for m in matches if m['source_author'] == 'WALTON']
                if jin and walton and {m['relation'] for m in jin} != {m['relation'] for m in walton}:
                    conflicts_between_sources.append(dict(pair_id=pair_id, status='MULTIPLE_RULE_SUPPORTED_RELATIONS',
                        jin_rule_ids=[m['rule_id'] for m in jin], walton_rule_ids=[m['rule_id'] for m in walton],
                        jin_supporting_evidence=[m['required_feature_witnesses'] for m in jin],
                        walton_supporting_evidence=[m['required_feature_witnesses'] for m in walton],
                        shared_evidence=pair_id, conflicting_evidence=sorted({m['relation'] for m in matches}), winner=''))
                distance = target['position'] - source['position']
                counts['candidate_pairs'] += 1; counts[status] += 1
                counts['long_distance'] += distance > long_distance
                counts['cross_book'] += source['row']['book'] != target['row']['book']
                matrix_table.write(dict(pair_id=pair_id, target_clause_id=tid, candidate_clause_id=sid,
                    distance_clauses=distance, distance_words=min(target['row']['word_ids']) - max(source['row']['word_ids']),
                    rule_ids_matched=rule_ids, source_clause_type=source['clause_type'], target_clause_type=target['clause_type'],
                    **{d: matrix_dimension(d, source, target, facts, matches, serialized=storage.COMPACT_TABLES) for d in DIMENSIONS}, candidate_relations=status,
                    facts=encoded_facts(tuple((k, bool(v)) for k, v in facts.items()))))
                rule_table.write(dict(pair_id=pair_id, source_clause_id=sid, target_clause_id=tid, matches=matches, nested_anchor_clause_ids=source['narrative_anchors']))
                relation_table.write(dict(pair_id=pair_id, source_clause_id=sid, target_clause_id=tid, relations=relations,
                    status=status, rule_ids=rule_ids, source_function_candidates=sorted({m['source_function_candidate'] for m in matches}),
                    target_function_candidates=sorted({m['target_function_candidate'] for m in matches}), adjudicated_function='', accepted_mother=''))
                for relation in relations:
                    edge = dict(edge_id=pair_id + '-' + relation[0], source=sid, target=tid, relation=relation, pair_id=pair_id,
                                rule_ids=[m['rule_id'] for m in matches if m['relation'] == relation], status='PROVISIONAL_NOT_ACCEPTED')
                    edges.append(edge); graph_table.write(edge); counts[relation + '_edges'] += 1
                    if relation == 'HYPOTACTIC':
                        mother_ids.append(sid)
                for fact, relation in graph_aux.items():
                    if facts[fact]:
                        graph_table.write(dict(edge_id=pair_id + '-' + relation, source=sid, target=tid, relation=relation,
                                               pair_id=pair_id, rule_ids=[], status='AUXILIARY_NOT_HIERARCHICAL'))
                candidates.append(dict(candidate_clause_id=sid, pair_id=pair_id, rule_ids=rule_ids, relations=relations,
                                       evidence_matrix_id=pair_id, distance_clauses=distance))
            targets.append(dict(target_clause_id=tid, candidate_count=len(admitted), mother_candidate_ids=sorted(set(mother_ids)),
                hierarchy_candidate_count=sum(bool(c['relations']) for c in candidates),
                no_candidate_status='' if admitted else 'NO_PLAUSIBLE_PRECEDING_CANDIDATE',
                level_proposal='' if admitted else 'NEW_HIGHER_LEVEL_CANDIDATE', canonical_level=''))
            if len(candidates) > 1:
                comparisons_table.write(dict(case_id='CC-' + str(tid), target_clause_id=tid, candidates=candidates,
                    mother_candidate_count=len(set(mother_ids)), mother_candidate_ids=sorted(set(mother_ids)), winner='',
                    global_effect_reference='14_global_compatibility_matrix.csv'))
    table(out / 'target_search_receipts.csv', targets)
    # One exact set selector per earlier relation preserves every later witness
    # without duplicating the quadratic cross product in a history log.
    for sid, previous in sorted(earlier_by_source.items()):
        for i, (pair_id, target_id) in enumerate(previous[:-1]):
            first_later_pair, first_later_target = previous[i + 1]
            history.reconsider(pair_id, [dict(graph_table='12_provisional_relation_graph.csv',
                source_clause_id=sid, target_position_greater_than=by_id[target_id]['position'],
                selector_semantics='ALL_LATER_HIERARCHICAL_CANDIDATE_EDGES_WITH_SAME_SOURCE',
                first_witness_pair_id=first_later_pair)], first_later_target)
    history_table.close()
    del history, earlier_by_source
    table(out / 'jin_walton_rule_conflicts.csv', conflicts_between_sources)
    graph = analyze_graph(edges, {f['clause_id']: f['position'] for f in features}, max_assignments)
    for name, key in [('13_global_relation_conflicts.csv', 'conflicts'), ('14_global_compatibility_matrix.csv', 'compatibility'),
                      ('15_variant_components.csv', 'components'), ('materialized_variants.csv', 'variants')]:
        table(out / name, graph[key])
    outgoing, peers, incoming = defaultdict(list), defaultdict(list), defaultdict(list)
    for edge in edges:
        if edge['relation'] == 'HYPOTACTIC':
            outgoing[edge['source']].append(edge['target']); incoming[edge['target']].append(edge['source'])
        else:
            peers[edge['source']].append(edge['target']); peers[edge['target']].append(edge['source'])
    behaviors = defaultdict(set)
    for edge in edges:
        behaviors[edge['target']].add(edge['relation'])
    table(out / 'corpus_behavior_variation.csv', behavior_variation(constructions, behaviors))
    table(out / 'masoretic_tradition_evidence.csv', (tradition_evidence(f['row'], qere, sorted(behaviors[f['clause_id']])) for f in features))
    table(out / '17_post_hierarchy_force_evidence.csv', (dict(clause_id=f['clause_id'],
        status='POST_HIERARCHY_FORCE_EVIDENCE', textual_level_candidate=dict(strictly_below=incoming[f['clause_id']], equal_level=peers[f['clause_id']]),
        coverage_candidate=dict(direct_embedded_clause_ids=outgoing[f['clause_id']], transitive_coverage='SYMBOLIC_COMPONENT_ASSIGNMENT_DEPENDENT'),
        contained_frames=[cid for cid in outgoing[f['clause_id']] if by_id[cid]['frame']],
        parallel_peers=peers[f['clause_id']], embedded_units=outgoing[f['clause_id']],
        opening_function_candidate='FRAME_CANDIDATE' if f['frame'] else '',
        closing_function_candidate='CESSATION_SYNTAX_CANDIDATE' if f['cessation'] else '',
        connecting_function_candidate='PARALLEL_CONNECTION_CANDIDATE' if peers[f['clause_id']] else '',
        canonical_level='', canonical_mother='') for f in features))
    counts.update(hard_conflicts=sum(c['severity'] == 'HARD_CONFLICT' for c in graph['conflicts']),
                  soft_conflicts=sum(c['severity'] == 'SOFT_CONFLICT' for c in graph['conflicts']),
                  components=len(graph['components']), materialized_variants=len(graph['variants']),
                  symbolic_components=sum(c['representation'] == 'SYMBOLIC_VARIANT_COMPONENT' for c in graph['components']))
    (out / 'blind_summary.json').write_text(encode(dict(counts)) + '\n', encoding='utf8')
    if label_definitions is not None:
        pass1 = manifest(out)
        (out / 'pass1_freeze.json').write_text(encode(dict(files=pass1, grammar_phase='LINGUISTIC_ONLY')) + '\n', encoding='utf8')
        units = unit_candidates(edges, features, compact=storage.COMPACT_TABLES)
        table(out / 'textual_unit_candidates.csv', units)
        unit_evidence = symbolic_unit_references(units, features) if storage.COMPACT_TABLES else unit_reference_evidence(units, features, edges)
        table(out / 'participant_unit_reference_evidence.csv', unit_evidence)
        table(out / 'bosman_source_crosswalk.csv', (dict(r, source_work=label_definitions['source_work'], source_pdf_sha256=label_definitions['source_pdf_sha256']) for r in label_definitions['labels']))
        rules_by_id = {r['rule_id']: r for r in registry['rules']}
        with ExitStack() as stack:
            poetic_table = stack.enter_context(Table(out / 'poetic_prosodic_evidence.csv', ['source_clause_id', 'target_clause_id', 'layer', 'relation', 'labels', 'observed_pattern_status', 'prosodic_status', 'poetic_boundary', 'boundary_status', 'exception_status', 'syntactic_override', 'canonical_boundary', 'source_author', 'source_work', 'source_section', 'source_page_if_verified', 'adoption_status']))
            layer_table = stack.enter_context(Table(out / 'relation_multilayer_edges.csv', ['source', 'target', 'relation', 'layer', 'provenance', 'status']))
            learning_fields = ['pair_id', 'target', 'candidate_source', 'candidate_relation', 'jin_rule_ids', 'walton_rule_ids', 'bosman_labels', 'milal_extension_labels', 'evidence_labels', 'program_proposed', 'global_conflict_reference', 'later_revision_history_reference', 'program_proposal_preserved', 'human_event', 'human_decision', 'human_rationale', 'competing_accepted_candidate', 'final_status', 'candidate_retained', 'model_training_performed']
            learning = stack.enter_context(Table(out / 'relation_decision_learning_table.csv', learning_fields))
            decision_matrix = stack.enter_context(Table(out / 'program_human_decision_matrix.csv', ['pair_id', 'program_proposed', 'human_decision', 'status']))
            source_conflicts = stack.enter_context(Table(out / 'multi_source_analytic_conflicts.csv', ['pair_id', 'status', 'jin_support', 'walton_support', 'bosman_support', 'shared_observations', 'conflicting_observations', 'affected_relation', 'affected_variant', 'winner']))
            layer_history_table = stack.enter_context(Table(out / 'relation_layer_revision_history.csv', history_fields))
            layer_history = RevisionHistory(layer_history_table.write)
            for edge in edges:
                layer_table.write(dict(source=edge['source'], target=edge['target'], relation=edge['relation'], layer='TEXTUAL_SYNTACTIC_LAYER', provenance=edge['edge_id'], status='ENGINE_PROPOSED_RELATION'))
            for matrix in rows(out / '09_candidate_evidence_matrix.csv'):
                sid, tid = int(matrix['candidate_clause_id']), int(matrix['target_clause_id'])
                source, target = by_id[sid], by_id[tid]
                facts = matrix['facts']
                labels = labels_for(facts, label_definitions, 2)
                poetic = poetic_observation(source, target, facts, label_definitions)
                poetic_table.write(poetic)
                if poetic['labels']:
                    layer_table.write(dict(source=sid, target=tid, relation='POETIC_PARALLELISM', layer='POETIC_PROSODIC_LAYER', provenance=matrix['pair_id'], status='FORMAL_CORRESPONDENCE_POETIC_INTERPRETATION_NOT_VERIFIED'))
                if facts['reference_continuity']:
                    layer_table.write(dict(source=sid, target=tid, relation='PARTICIPANT_REFERENCE', layer='PARTICIPANT_REFERENCE_LAYER', provenance=matrix['pair_id'], status='POTENTIAL_UNRESOLVED_REFERENCE'))
                proposed = matrix['candidate_relations'] in ('HYPOTACTIC', 'PARATACTIC', 'MULTIPLE')
                rule_ids = matrix['rule_ids_matched']
                result = decision_learning_row(dict(pair_id=matrix['pair_id'], target=tid, candidate_source=sid,
                    candidate_relation=matrix['candidate_relations'], jin_rule_ids=[r for r in rule_ids if rules_by_id[r]['source_author'] == 'JIN'],
                    walton_rule_ids=[r for r in rule_ids if rules_by_id[r]['source_author'] == 'WALTON'],
                    bosman_labels=[x['label_id'] for x in labels], milal_extension_labels=[], evidence_labels=labels,
                    program_proposed=proposed, global_conflict_reference=matrix['pair_id'], later_revision_history_reference=matrix['pair_id']))
                learning.write(result)
                decision_matrix.write(dict(pair_id=matrix['pair_id'], program_proposed=proposed, human_decision='', status=result['final_status']))
                if matrix['candidate_relations'] == 'MULTIPLE' or poetic['exception_status']:
                    source_conflicts.write(dict(pair_id=matrix['pair_id'], status='MULTI_SOURCE_ANALYTIC_CONFLICT',
                        jin_support=result['jin_rule_ids'], walton_support=result['walton_rule_ids'], bosman_support=poetic['labels'],
                        shared_observations=dict(source_clause_id=sid, target_clause_id=tid),
                        conflicting_observations=matrix['candidate_relations'], affected_relation=matrix['pair_id'],
                        affected_variant='15_variant_components.csv', winner=''))
            for row in rows(out / 'participant_unit_reference_evidence.csv'):
                if 'target_clause_ids' in row:
                    layer_table.write(dict(source=row['source_unit_candidate_id'], target=row['target_clause_ids'], relation='PARTICIPANT_REFERENCE',
                        layer='PARTICIPANT_REFERENCE_LAYER', provenance=row, status='EXACT_FACTORIZED_CONDITIONAL_REFERENCE_SET'))
                    pair_id = 'UNIT-SET-' + str(row['source_clause_id'])
                    trigger = row['target_clause_ids'][-1]
                    layer_history.initialize(pair_id, [], trigger, [])
                    layer_history.reconsider(pair_id, [row], trigger, ['UNIT_CONTEXT_REFERENCE_CANDIDATE'])
                    continue
                layer_table.write(dict(source=int(row['antecedent_clause_id']), target=int(row['target_clause_id']), relation='PARTICIPANT_REFERENCE',
                    layer='PARTICIPANT_REFERENCE_LAYER', provenance=row, status='CONDITIONAL_UNIT_REFERENCE_IDENTITY_UNRESOLVED'))
                pair_id = 'UNIT-%s-%s-%s' % (row['source_clause_id'], row['target_clause_id'], row['antecedent_clause_id'])
                layer_history.initialize(pair_id, [], int(row['target_clause_id']), [])
                layer_history.reconsider(pair_id, [row], int(row['target_clause_id']), ['UNIT_CONTEXT_REFERENCE_CANDIDATE'])
        if any(digest(out / r['path']) != r['sha256'] for r in pass1):
            raise ValueError('pass 2 mutated frozen pass 1')
    manifest(out)
    return dict(counts)
