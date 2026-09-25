"""Observed valency frames precede inter-clausal grammar; no emendation or merging."""
import hashlib
import unicodedata
from collections import defaultdict
from milal_mfr02r_data import encode

PROVENANCE = dict(source_author='OOSTING', source_work='WALLS_OF_ZION_AND_RUINS_OF_JERUSALEM',
                  source_section='1.2.3 / 1.2.4 / 1.3', source_page_if_verified=[39, 40, 41, 42, 43, 48],
                  adoption_status='GENERALIZED_FOR_MILAL')


def signature_hash(value):
    return hashlib.sha256(encode(value).encode('utf8')).hexdigest()


def construction(row):
    words = row['words']; wm = {w['node']: w for w in words}
    verbs = [w for w in words if w['sp'] == 'verb']
    nominal_nodes = {n for p in row['phrases'] if p['function'] in ('Pred', 'PreC') for n in p['word_ids']} if not verbs else set()
    predicate_words = verbs or [w for w in words if w['node'] in nominal_nodes]
    slots = []
    for phrase in row['phrases']:
        slots.append(dict(phrase_node=phrase['node'], function=phrase['function'], phrase_type=phrase['typ'],
            word_nodes=phrase['word_ids'], prepositions=[wm[n]['lex'] for n in phrase['word_ids'] if wm[n]['sp'] == 'prep']))
    core_slots = [{k: s[k] for k in ('function', 'phrase_type', 'prepositions')} for s in slots]
    predicates = [dict(word_node=w['node'], predicate_lexeme=w['lex'], stem=w.get('vs'),
        predicate_type='PARTICIPLE_VERBAL_POTENTIAL' if w.get('vt') in ('ptca', 'ptcp') else 'VERBAL',
        verbal_morphology={k: w.get(k) for k in ('vt', 'vs', 'ps', 'gn', 'nu')},
        argument_governance='NOT_INFERRED_FROM_CLAUSE_MEMBERSHIP') for w in verbs]
    if not verbs:
        predicates = [dict(word_node=w['node'], predicate_lexeme=w['lex'], stem='NOT_APPLICABLE',
            predicate_type='OBSERVED_NOMINAL_PREDICATE_EXPRESSION',
            source_phrase_nodes=[p['node'] for p in row['phrases'] if p['function'] in ('Pred', 'PreC') and w['node'] in p['word_ids']],
            argument_governance='NOT_INFERRED_FROM_CLAUSE_MEMBERSHIP') for w in predicate_words]
    valency = dict(predicate_lexeme=[w['lex'] for w in predicate_words], stem=[w.get('vs') if verbs else 'NOT_APPLICABLE' for w in predicate_words],
        predicate_observation='OBSERVED_VERBAL_FEATURE' if verbs else 'OBSERVED_NOMINAL_PREDICATE_PHRASE' if predicate_words else 'NOT_AVAILABLE',
        voice_if_available='NOT_SEPARATELY_ANNOTATED', predicate_type='VERBAL' if verbs else 'NOMINAL',
        argument_slots=core_slots, complement_types=[s for s in core_slots if s['function'] in ('Cmpl', 'PreC', 'Loca')],
        prepositions=[w['lex'] for w in words if w['sp'] == 'prep'], phrase_functions=[s['function'] for s in slots],
        participant_role_slots=[s for s in core_slots if s['function'] in ('Subj', 'Objc', 'Cmpl', 'PreO', 'PreS')],
        constituent_arrangement=[s['function'] for s in slots],
        modality='OBSERVED_REALIZATIONS; OBLIGATORY_VALENCY_NOT_INFERRED')
    exact = dict(clause_type=row['clause_type'], valency_signature=valency,
                 constituent_signature=[(w['lex'], w['sp']) for w in words],
                 phrase_function_sequence=[s['function'] for s in slots],
                 morphological_signature=[{k: w.get(k) for k in ('sp', 'vt', 'vs', 'ps', 'gn', 'nu', 'prs_ps', 'prs_gn', 'prs_nu')} for w in words])
    return dict(construction_id='CON-' + str(row['clause_id']), clause_id=int(row['clause_id']),
        book=row['book'], chapter=row['chapter'], verse=row['verse'],
        clause_atom_ids=row['clause_atom_ids'], raw_clause_atom_ids=row['clause_atom_ids'],
        resolved_clause_candidate_id='CON-' + str(row['clause_id']), clause_type=row['clause_type'], predicate=predicates,
        valency_signature=valency, valency_signature_id=signature_hash(valency),
        exact_construction_signature=exact, exact_construction_signature_id=signature_hash(exact),
        constituent_signature=exact['constituent_signature'], phrase_sequence=slots,
        morphology=exact['morphological_signature'], domain=row['domain'],
        participant_configuration=row['participant_surface_set'], participant_use_type='RELATION_EVIDENCE',
        time_configuration=row['temporal_phrase_structure'], location_configuration=row['locative_phrase_structure'],
        observed_status='OBSERVED_CONSTRUCTION', generalized_pattern='', generalization_relation='MAY_INSTANTIATE_NOT_ASSIGNED',
        analysis_form='TEXT_AS_ENCODED', missing_arguments='UNKNOWN_NOT_VERIFIED_NO_VALENCY_LEXICON',
        **PROVENANCE)


def internal_bindings(observations, constructions):
    atoms = sorted([(min(a['word_ids']), int(a['node']), row, a) for row in observations for a in row['atoms']], key=lambda r: (r[0], r[1]))
    positions = {a[1]: i for i, a in enumerate(atoms)}
    cm = {c['clause_id']: c for c in constructions}
    for row in observations:
        ordered = sorted(row['atoms'], key=lambda a: min(a['word_ids']))
        for index, first in enumerate(ordered):
            for last in ordered[index + 1:]:
                a, b = positions[first['node']], positions[last['node']]
                between = atoms[a + 1:b]
                first_words, last_words = set(first['word_ids']), set(last['word_ids'])
                first_functions = {p['function'] for p in row['phrases'] if first_words & set(p['word_ids'])}
                last_functions = {p['function'] for p in row['phrases'] if last_words & set(p['word_ids'])}
                reasons = ['OTHER_SYNTACTIC_BINDING']
                realized_split = bool(first_functions & {'Pred', 'PreS', 'PreO', 'PtcO', 'PtcS'} and last_functions & {'Objc', 'Cmpl', 'PreC', 'Loca'})
                nominal_split = not row['predicate_lexeme'] and bool(first_functions & {'Subj', 'Nega'} and last_functions & {'PreC', 'Cmpl'})
                if realized_split or nominal_split:
                    reasons.append('VALENCY_COMPLETION')
                if any(any(p['function'] == 'Voct' and set(p['word_ids']) & set(atom['word_ids']) for p in other['phrases']) for _, _, other, atom in between):
                    reasons.append('VOCATIVE_INTERRUPTION')
                if any(int(other['clause_id']) != int(row['clause_id']) for _, _, other, _ in between):
                    reasons.append('INSERTED_CLAUSE_INTERRUPTION')
                for function, reason in [('Objc', 'SPLIT_OBJECT'), ('Cmpl', 'SPLIT_COMPLEMENT'), ('PreC', 'SPLIT_PREDICATE_COMPLEMENT')]:
                    if function in last_functions:
                        reasons.append(reason)
                record = cm[int(row['clause_id'])]
                yield dict(binding_id='BIND-%s-%s' % (first['node'], last['node']),
                    clause_atom_a=first['node'], clause_atom_b=last['node'], intervening_atoms=[x[1] for x in between],
                    predicate_lexeme=record['valency_signature']['predicate_lexeme'], verbal_stem=record['valency_signature']['stem'],
                    valency_slots=record['valency_signature']['argument_slots'], realized_arguments=record['phrase_sequence'],
                    missing_arguments=record['missing_arguments'], binding_evidence=dict(reasons=reasons,
                        raw_clause_membership=int(row['clause_id']), first_atom_functions=sorted(first_functions), last_atom_functions=sorted(last_functions)),
                    corpus_analogues=record['valency_signature_id'], status='CLAUSE_INTERNAL_BINDING_CANDIDATE',
                    relation_status='RELATION_DEFERRED_PENDING_CLAUSE_BINDING', construction_id=record['construction_id'],
                    automatic_atom_merge=False, **PROVENANCE)


def atom_relation_status(atom_a, atom_b, bindings):
    if any({int(b['clause_atom_a']), int(b['clause_atom_b'])} == {int(atom_a), int(atom_b)} for b in bindings):
        return 'RELATION_DEFERRED_PENDING_CLAUSE_BINDING'
    return 'INTER_CLAUSAL_CANDIDATE_SEARCH_ALLOWED'


def corpus_index(constructions):
    indexes = dict(exact=defaultdict(list), valency=defaultdict(list), predicate=defaultdict(list))
    for c in constructions:
        occurrence = dict(construction_id=c['construction_id'], clause_id=c['clause_id'],
                          book=c.get('book', 'UNKNOWN_NOT_VERIFIED'), valency_signature_id=c['valency_signature_id'],
                          exact_construction_signature_id=c['exact_construction_signature_id'],
                          domain=c['domain'], clause_type=c['clause_type'])
        indexes['exact'][c['exact_construction_signature_id']].append(occurrence)
        # Missing predicates are not shared linguistic evidence. Exact complete
        # observed constructions can still be compared without inventing a head.
        if c['valency_signature']['predicate_lexeme']:
            indexes['valency'][c['valency_signature_id']].append(occurrence)
            key = encode([c['valency_signature']['predicate_lexeme'], c['valency_signature']['stem']])
            indexes['predicate'][key].append(occurrence)
    return indexes


def validate_comparison_index(constructions, indexes):
    identities = {}
    for signature, occurrences in indexes['exact'].items():
        for occurrence in occurrences:
            cid = int(occurrence['clause_id'])
            if cid in identities or occurrence['exact_construction_signature_id'] != signature:
                raise ValueError('comparison index contains inconsistent source identity')
            identities[cid] = occurrence
    for c in constructions:
        actual = identities.get(c['clause_id'])
        if actual is None or any(actual[k] != c[k] for k in ('exact_construction_signature_id','valency_signature_id')):
            raise ValueError('comparison index incompatible with current observed construction')


def analogues(constructions, indexes, analysis_scope, comparison_scope, symbolic=False):
    for c in constructions:
        exact_key = c['exact_construction_signature_id']; valency_key = c['valency_signature_id']
        predicate_key = encode([c['valency_signature']['predicate_lexeme'], c['valency_signature']['stem']])
        # All exact, close and partial occurrences are retained, not a preferred match.
        exact = [r for r in indexes['exact'].get(exact_key, ()) if r['clause_id'] != c['clause_id']]
        close = [r for r in indexes['valency'].get(valency_key, ()) if r['exact_construction_signature_id'] != exact_key]
        partial = [r for r in indexes['predicate'].get(predicate_key, ()) if r['valency_signature_id'] != valency_key]
        yield dict(construction_id=c['construction_id'], analysis_scope=analysis_scope, corpus_comparison_scope=comparison_scope,
            exact_analogues=dict(index='exact', key=exact_key, exclude_clause_id=c['clause_id']) if symbolic else exact,
            close_analogues=dict(index='valency', key=valency_key, exclude_exact_key=exact_key) if symbolic else close,
            partial_analogues=dict(index='predicate', key=predicate_key, exclude_valency_key=valency_key) if symbolic else partial,
            analogue_status='EXACT_ANALOGUE' if exact else 'CLOSE_ANALOGUE' if close else 'PARTIAL_ANALOGUE' if partial else 'NO_ANALOGUE_FOUND',
            regularity_status='CORPUS_REGULARITY_SUPPORTED' if exact or close else 'NO_CORPUS_SUPPORT_FOUND',
            counterexample_candidates=dict(index='predicate', key=predicate_key, exclude_valency_key=valency_key) if symbolic else partial,
            structural_behavior='NOT_INFERRED_FROM_SIGNATURE',
            comparison_semantics='EXACT=FULL_OBSERVED_SIGNATURE; CLOSE=SAME_VALENCY; PARTIAL=SAME_PREDICATE_AND_STEM',
            outside_comparison_scope='OUTSIDE_SCOPE_NOT_TESTED', accepted_relation='', **PROVENANCE)


def recursive_patterns(observations):
    for row in observations:
        predicates = [w for w in row['words'] if w['sp'] == 'verb']
        main = [w for w in predicates if any(w['node'] in p['word_ids'] and p['function'] in ('Pred', 'PreO', 'PreS') for p in row['phrases'])]
        for inner in predicates:
            if inner.get('vt') not in ('ptca', 'ptcp', 'infc', 'infa'):
                continue
            for outer in main:
                if inner['node'] == outer['node']:
                    continue
                containing = [p for p in row['phrases'] if inner['node'] in p['word_ids']]
                yield dict(clause_id=row['clause_id'], outer_valency_predicate_node=outer['node'], inner_valency_predicate_node=inner['node'],
                    relation='OUTER_VALENCY_CONTAINS_INNER_VALENCY_CANDIDATE',
                    inner_verbal_potential='PARTICIPLE_VERBAL_POTENTIAL' if inner['vt'] in ('ptca', 'ptcp') else 'INFINITIVAL_VERBAL_POTENTIAL',
                    containing_phrases=containing, argument_governance='UNRESOLVED',
                    accepted_containment=False, **PROVENANCE)


def behavior_variation(constructions, behaviors):
    groups = defaultdict(list)
    for c in constructions:
        groups[c['exact_construction_signature_id']].append(c['clause_id'])
    for signature, ids in sorted(groups.items()):
        found = {cid: sorted(behaviors.get(cid, ())) for cid in ids}
        if len({tuple(value) for value in found.values()}) > 1:
            yield dict(exact_construction_signature_id=signature, occurrences=found,
                       status='CORPUS_BEHAVIOR_VARIATION', hierarchy_generalization=False, **PROVENANCE)


def participant_use(observation, interpretation=None):
    """Attach a later, explicitly sourced interpretation without replacing evidence."""
    result = dict(observation)
    if interpretation is None:
        result['participant_use_type'] = 'RELATION_EVIDENCE'
        return result
    if not all(interpretation.get(k) for k in ('hierarchy_freeze_sha256', 'reviewer', 'source_sha256', 'interpretation')):
        raise ValueError('post-hierarchy participant interpretation lacks provenance')
    result['participant_use_type'] = 'BOTH' if observation.get('participant_use_type') == 'RELATION_EVIDENCE' else 'DISCOURSE_INTERPRETATION'
    result['post_hierarchy_interpretation'] = dict(interpretation)
    return result


def tradition_evidence(row, qere=None, plausible_analyses=(), assessment='NOT_DECISIVE', text_status='TEXT_AS_ENCODED'):
    allowed = ('SUPPORTS_ANALYSIS_A', 'SUPPORTS_ANALYSIS_B', 'COMPATIBLE_WITH_BOTH', 'CONFLICTS_WITH_CURRENT_ANALYSIS', 'NOT_DECISIVE', 'NOT_AVAILABLE')
    if assessment not in allowed or text_status not in ('TEXT_AS_ENCODED', 'TEXT_CRITICAL_ISSUE_FLAGGED', 'ALTERNATIVE_READING_AVAILABLE'):
        raise ValueError('invalid tradition evidence status')
    variants = []
    for word in row['words']:
        encoded = word.get('g_word_utf8') or ''
        reading = (qere or {}).get(word['node'], '')
        variants.append(dict(word_node=word['node'], ketiv_form=encoded, qere_form=reading,
            analysis_form=encoded, tradition_variant_present=bool(reading),
            accents=[dict(character=c, unicode_name=unicodedata.name(c, 'UNKNOWN')) for c in encoded if '\u0591' <= c <= '\u05af']))
    return dict(clause_id=row['clause_id'], textual_tradition=variants, analysis_text_status=text_status,
        evidence_type='MASORETIC_TRADITION_EVIDENCE', assessment=assessment,
        display_as_tiebreaker=len(plausible_analyses) > 1, plausible_analyses=list(plausible_analyses),
        evidence_stage='SECONDARY_AFTER_LINGUISTIC_ANALYSIS', automatic_boundary=False, automatic_emendation=False,
        source_author='OOSTING', source_work=PROVENANCE['source_work'], source_section='1.3.5 / 1.3.6',
        source_page_if_verified=[61, 62, 63, 64], adoption_status='GENERALIZED_FOR_MILAL')
