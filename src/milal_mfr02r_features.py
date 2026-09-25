"""Node-preserving linguistic observations; referential identity stays unresolved."""
from collections import defaultdict


def valid(value):
    return value not in (None, '', 'NA', 'unknown')


def png(word, suffix=False):
    prefix = 'prs_' if suffix else ''
    values = tuple(word.get(prefix + k) for k in ('ps', 'gn', 'nu'))
    return values if all(valid(v) for v in values) else None


def build_features(observations, registry, native_edges=()):
    """Native dependency annotations are evidence, never accepted textual mothers."""
    features = []
    node_owner = defaultdict(set)
    lexicons = {k: set(v) for k, v in registry['lexicons'].items()}
    seen_participants, previous_participants = set(), set()
    required = {'clause_id', 'clause_atom_ids', 'words', 'phrases', 'atoms',
                'word_ids', 'clause_type', 'domain', 'surface_hebrew', 'book', 'chapter', 'verse'}
    for position, row in enumerate(observations):
        if required - row.keys():
            raise ValueError('required observation schema: ' + repr(sorted(required - row.keys())))
        words, phrases = row['words'], row['phrases']
        wm = {w['node']: w for w in words}
        if not words or set(wm) != set(row['word_ids']) or not row['clause_atom_ids']:
            raise ValueError('missing word/atom identity')
        for word in words:
            if not {'node', 'lex', 'sp', 'ps', 'gn', 'nu', 'vt'} <= word.keys():
                raise ValueError('required morphology schema')
        cid = int(row['clause_id'])
        for node in [cid, *row['clause_atom_ids'], *row['word_ids'], *(p['node'] for p in phrases)]:
            node_owner[int(node)].add(cid)
        def phrase_lex(functions):
            return {wm[n]['lex'] for p in phrases if p['function'] in functions for n in p['word_ids']
                    if wm[n]['sp'] not in ('prep', 'conj', 'art')}
        verbs = [w for w in words if w['sp'] == 'verb']
        subject_words = [wm[n] for p in phrases if p['function'] in ('Subj', 'PreS') for n in p['word_ids']]
        subjects = phrase_lex(('Subj', 'PreS'))
        objects = phrase_lex(('Objc', 'PreO'))
        complements = phrase_lex(('Cmpl', 'PreC', 'Adju', 'PrAd'))
        time_phrases = [p for p in phrases if p['function'] == 'Time']
        location_phrases = [p for p in phrases if p['function'] == 'Loca']
        references = []
        for w in words:
            if w['sp'] in ('prps', 'prde', 'prin') or w['lex'] in lexicons['deictic']:
                references.append(dict(kind='PRONOUN_OR_DEICTIC', node=w['node'], lex=w['lex'], png=png(w), identity='UNRESOLVED'))
            if png(w, True):
                references.append(dict(kind='PRONOMINAL_SUFFIX', node=w['node'], lex=w['lex'], png=png(w, True), identity='UNRESOLVED'))
        if not subjects:
            references.extend(dict(kind='IMPLICIT_SUBJECT', node=w['node'], lex=w['lex'], png=png(w), identity='UNRESOLVED') for w in verbs)
        temporal_words = [w for w in words if w['lex'] in lexicons['temporal'] | lexicons['relative_temporal']]
        wayhi = row['clause_type'] == 'Way0' and any(w['lex'] == 'HJH[' and png(w) == ('p3', 'm', 'sg') for w in verbs)
        types = {row['clause_type']}
        if wayhi and time_phrases:
            types.add('Wayhi+Time')
        time_tokens = phrase_lex(('Time',)) | {w['lex'] for w in temporal_words}
        loc_tokens = phrase_lex(('Loca',))
        content = {w['lex'] for w in words if w['sp'] not in ('prep', 'art', 'conj', 'nega')}
        # Exact lexical recurrence is not referential identity. Every mention keeps
        # its own source-node ID, even where the same lexeme has occurred before.
        participants = subjects | objects | complements
        participant_mentions = []
        for p in phrases:
            if p['function'] not in ('Subj', 'PreS', 'Objc', 'PreO', 'Cmpl', 'PreC', 'Adju', 'PrAd'):
                continue
            for n in p['word_ids']:
                w = wm[n]
                if w['lex'] not in participants:
                    continue
                status = 'CONTINUED' if w['lex'] in previous_participants else 'REINTRODUCED' if w['lex'] in seen_participants else 'NEW'
                reference_type = 'INDEPENDENT_PRONOUN' if w['sp'] == 'prps' else 'DEMONSTRATIVE' if w['sp'] == 'prde' else 'EXPLICIT_NP'
                participant_mentions.append(dict(participant_id='MENTION-' + str(n), participant_surface=w.get('g_word_utf8', ''),
                    participant_status=status, participant_reference_type=reference_type, participant_set_id='PART-' + str(cid),
                    lexical_key=w['lex'], status_basis='LEXICAL_SURFACE_RECURRENCE_NOT_REFERENTIAL_IDENTITY',
                    identity_status='UNRESOLVED', participant_use_type='RELATION_EVIDENCE', grammatical_role=p['function'], speaker='UNRESOLVED', addressee='UNRESOLVED', agent='UNRESOLVED', patient='UNRESOLVED'))
        for ref in references:
            if ref['kind'] in ('PRONOMINAL_SUFFIX', 'IMPLICIT_SUBJECT'):
                participant_mentions.append(dict(participant_id='MENTION-' + str(ref['node']) + '-' + ref['kind'], participant_surface=wm[ref['node']].get('g_word_utf8', ''),
                    participant_status='UNRESOLVED', participant_reference_type='PRONOMINAL_SUFFIX' if ref['kind'] == 'PRONOMINAL_SUFFIX' else 'INFLECTIONAL_AFFIX',
                    participant_set_id='PART-' + str(cid), lexical_key=ref['lex'], status_basis='IDENTITY_UNRESOLVED', identity_status='UNRESOLVED', participant_use_type='RELATION_EVIDENCE',
                    grammatical_role='IMPLICIT_SUBJECT' if ref['kind'] == 'IMPLICIT_SUBJECT' else 'SUFFIX', speaker='UNRESOLVED', addressee='UNRESOLVED', agent='UNRESOLVED', patient='UNRESOLVED'))
        absent = sorted(previous_participants - participants)
        seen_participants |= participants
        previous_participants = participants
        form = (tuple(w['sp'] for w in words), tuple((p['function'], p['typ']) for p in phrases))
        source_png = {p for w in subject_words + verbs if (p := png(w))}
        reference_png = {tuple(r['png']) for r in references if r['png']}
        feature = dict(clause_id=cid, position=position, clause_type=row['clause_type'], types=types,
                       row=row, subjects=subjects, objects=objects, complements=complements,
                       participants=participants, content=content, participant_mentions=participant_mentions,
                       absent_participant_lexemes=absent,
                       reintroduced={m['lexical_key'] for m in participant_mentions if m['participant_status'] == 'REINTRODUCED'},
                       time_tokens=time_tokens, location_tokens=loc_tokens,
                       time_phrases=time_phrases, temporal_words=temporal_words, location_phrases=location_phrases,
                       references=references, source_png=source_png, reference_png=reference_png,
                       predicate=tuple(w['lex'] for w in verbs), verbs=verbs, form=form,
                       domain=row['domain'], frame=bool(types & {'WayX', 'WXQt', 'Wayhi+Time'}),
                       native_preceding=[], native_raw=[], sequence_keys=[], narrative_anchors=[],
                       explicit_subordinator=any(w['lex'] in lexicons['subordinators'] for w in words),
                       infinitive_preposition=any(w['sp'] == 'prep' and w['lex'] in ('L', 'K', 'B') for w in words),
                       deictic=any(w['lex'] in lexicons['deictic'] for w in words),
                       speech=any(w['lex'] in lexicons['speech'] for w in verbs),
                       cessation=any(w['lex'] in lexicons['cessation'] for w in verbs) and bool(content & lexicons['speech_nouns']))
        features.append(feature)
    by_id = {f['clause_id']: f for f in features}
    if len(by_id) != len(features):
        raise ValueError('duplicate clause id')
    for edge in native_edges:
        targets = node_owner.get(int(edge['dependent_node']), set())
        sources = node_owner.get(int(edge['head_node']), set())
        for tid in sorted(targets):
            item = dict(edge, resolved_head_clause_ids=sorted(sources),
                        resolution='EXACT_NODE_MEMBERSHIP' if sources else 'OUTSIDE_PROJECTION',
                        textual_mother_status='NOT_ASSIGNED')
            by_id[tid]['native_raw'].append(item)
            for sid in sorted(sources):
                if by_id[sid]['position'] < by_id[tid]['position'] and edge['rela'] in lexicons['subordinate_rela']:
                    by_id[tid]['native_preceding'].append(sid)
    # Context signatures use source clause order, never a human segment boundary.
    for i, feature in enumerate(features):
        for length in registry['context_sequence_lengths']:
            if i + length <= len(features):
                signature = tuple((f['clause_type'], f['predicate'], f['form']) for f in features[i:i + length])
                feature['sequence_keys'].append(signature)
        if feature['clause_type'] == 'ZIm0':
            feature['narrative_anchors'] = [p['clause_id'] for p in features[:i]
                if p['clause_type'] == 'WayX' and p['speech'] and
                (p['clause_id'] in feature['native_preceding'] or
                 p['participants'] & feature['participants'] and p['domain'] != feature['domain'])]
    return features


def pair_facts(source, target):
    participant_shared = source['participants'] & target['participants']
    implicit_reference = source['source_png'] & target['reference_png']
    lexical_reference = participant_shared and bool(target['references'])
    reference = bool(implicit_reference or lexical_reference)
    native = source['clause_id'] in target['native_preceding']
    time_shared = source['time_tokens'] & target['time_tokens']
    location_shared = source['location_tokens'] & target['location_tokens']
    sequence = bool(set(source['sequence_keys']) & set(target['sequence_keys']))
    form = source['form'] == target['form']
    predicate = bool(source['predicate']) and source['predicate'] == target['predicate']
    domain_same = valid(source['domain']) and source['domain'] == target['domain']
    shared_functions = {p['function'] for p in source['row']['phrases']} & {p['function'] for p in target['row']['phrases']} - {'Pred', 'Conj'}
    high = sequence or form and predicate or predicate and bool(participant_shared) and bool(shared_functions)
    crossed_roles = bool(source['complements'] & target['subjects'] or source['subjects'] & target['complements'])
    time_contrast = bool(source['time_tokens'] and target['time_tokens'] and source['time_tokens'] != target['time_tokens'])
    location_contrast = bool(source['location_tokens'] and target['location_tokens'] and source['location_tokens'] != target['location_tokens'])
    participant_contrast = bool(source['participants'] and target['participants'] and source['participants'] != target['participants'])
    adjacent = target['position'] - source['position'] == 1
    # These predicates propose alternative readings; they do not resolve anaphora or a narrative line.
    interplay = crossed_roles and participant_contrast and (reference or domain_same)
    embedding = reference and (native or crossed_roles or adjacent and bool(source['subjects']))
    temporal = bool(time_shared or source['time_phrases'] and target['time_phrases'])
    frame_embedding = source['frame'] and target['frame'] and (reference or participant_shared) and (time_contrast or location_contrast or interplay)
    same_line = domain_same and bool(participant_shared or sequence or temporal and location_shared)
    return dict(native_subordinate=native, adjacent=adjacent,
                same_clause_type=source['clause_type'] == target['clause_type'],
                independent_correspondence=bool(participant_shared or reference or time_shared or location_shared or predicate or sequence),
                continued_secondary_participant=bool((source['objects'] | source['complements']) & target['participants']),
                subordination_continuation=bool(source['native_preceding'] and source['explicit_subordinator'] and target['explicit_subordinator']),
                source_finite=any(w.get('vt') in ('perf', 'impf', 'wayq', 'impv') for w in source['verbs']),
                infinitive_preposition=target['infinitive_preposition'], explicit_subordinator=target['explicit_subordinator'],
                reference_continuity=reference, participant_continuity=bool(participant_shared),
                speech_domain_entry=source['speech'] and valid(target['domain']) and source['domain'] != target['domain'] and (native or reference or bool(participant_shared)),
                nested_speech_entry=source['speech'] and bool(target['reference_png']) and (native or crossed_roles),
                prior_narrative_speech_anchor=bool(source['narrative_anchors']),
                embedded_reference=embedding, participant_interplay=interplay,
                frame_embedding=frame_embedding, nominal_background=bool(native or reference and participant_shared),
                anaphoric_summary=bool(target['deictic'] and (reference or participant_shared) or target['cessation'] and participant_shared),
                antecedent_embedding=embedding and any(w['sp'] == 'art' for w in target['row']['words']),
                anaphoric_embedding=source['deictic'] and target['deictic'] and embedding,
                high_correspondence=high, same_line=same_line, temporal_connection=temporal,
                sequence_correspondence=sequence, formal_correspondence=form,
                time_continuity=bool(time_shared), location_continuity=bool(location_shared),
                domain_continuity=domain_same, domain_contrast=bool(valid(source['domain']) and valid(target['domain']) and not domain_same),
                participant_contrast=participant_contrast, time_contrast=time_contrast, location_contrast=location_contrast,
                lexical_continuity=bool(source['content'] & target['content']))


INDEX_NAMES = ('CLAUSE_TYPE_INDEX', 'FORMAL_PATTERN_INDEX', 'PARTICIPANT_INDEX', 'REFERENCE_INDEX',
               'TIME_INDEX', 'LOCATION_INDEX', 'DOMAIN_INDEX', 'SEQUENCE_INDEX', 'FRAME_INDEX', 'LEXICAL_INDEX',
               'PARTICIPANT_REINTRODUCTION_INDEX', 'LEXICAL_REINTRODUCTION_INDEX')


def keys(feature):
    return dict(CLAUSE_TYPE_INDEX=feature['types'], FORMAL_PATTERN_INDEX=[feature['form']],
                PARTICIPANT_INDEX=feature['participants'], REFERENCE_INDEX=feature['source_png'],
                TIME_INDEX=feature['time_tokens'], LOCATION_INDEX=feature['location_tokens'],
                DOMAIN_INDEX=[feature['domain']], SEQUENCE_INDEX=feature['sequence_keys'],
                FRAME_INDEX=['FRAME'] if feature['frame'] else [], LEXICAL_INDEX=feature['content'],
                PARTICIPANT_REINTRODUCTION_INDEX=feature['participants'], LEXICAL_REINTRODUCTION_INDEX=feature['content'])


def preceding_sets(features):
    """Union of every independent evidence index, with no distance/book cutoff.

    Type/domain/frame indexes are recorded for inspection, but their generic
    labels alone cannot establish a plausible relation. Every lexical, formal,
    reference, participant, time, location, sequence or native match is retained.
    """
    indexes = {name: defaultdict(set) for name in INDEX_NAMES}
    for target in features:
        why = defaultdict(set)
        target_keys = keys(target)
        target_keys['REFERENCE_INDEX'] = target['reference_png']
        for name, values in target_keys.items():
            if name in ('CLAUSE_TYPE_INDEX', 'DOMAIN_INDEX', 'FRAME_INDEX'):
                continue
            for value in values:
                for cid in indexes[name].get(value, ()):
                    why[cid].add(name)
        for cid in target['native_preceding']:
            why[cid].add('EXPLICIT_DEPENDENCY')
        # Explicit subordinate constructions may depend on any preceding finite
        # main clause; contextual rules, not proximity, decide candidate relations.
        if target['explicit_subordinator'] or target['infinitive_preposition'] and target['clause_type'] == 'InfC':
            for values in indexes['CLAUSE_TYPE_INDEX'].values():
                for cid in values:
                    why[cid].add('SUBORDINATE_CANDIDATE_SEARCH')
        yield target, {cid: sorted(reasons) for cid, reasons in sorted(why.items())}
        for name, values in keys(target).items():
            for value in values:
                indexes[name][value].add(target['clause_id'])


def evidence_values(feature):
    row = feature['row']
    return dict(
        GRAPHEME=dict(function_words=[w for w in row['words'] if w['sp'] in ('prep', 'art', 'conj')],
                      suffixes=[r for r in feature['references'] if r['kind'] == 'PRONOMINAL_SUFFIX'],
                      prefix_status='MORPHOLOGICAL_FEATURES_ONLY_NO_SEGMENTATION_INFERRED'),
        WORD=row['words'], PHRASE=row['phrases'],
        CLAUSE=dict(clause_type=feature['clause_type'], atoms=row['atoms'], native_annotations=feature['native_raw']),
        TIME=dict(phrases=feature['time_phrases'], lexemes=feature['temporal_words'], time_phrase=feature['time_phrases'],
                  time_reference_type='EXPLICIT_PHRASE' if feature['time_phrases'] else 'LEXEME_ONLY' if feature['temporal_words'] else 'NOT_AVAILABLE',
                  temporal_continuity='PAIRWISE_MATRIX', temporal_change='PAIRWISE_MATRIX', temporal_succession='RELATIVE_LEXEMES_ONLY',
                  temporal_resumption='UNRESOLVED', temporal_frame_candidate='Wayhi+Time' in feature['types'], calendar_identity='UNRESOLVED'),
        LOCATION=dict(phrases=feature['location_phrases'], count=len(feature['location_phrases']),
                      geographic_topographic_identity='UNRESOLVED', location_phrase=feature['location_phrases'],
                      location_reference_type='EXPLICIT_PHRASE' if feature['location_phrases'] else 'NOT_AVAILABLE',
                      locative_continuity='PAIRWISE_MATRIX', locative_change='PAIRWISE_MATRIX',
                      single_or_multiple_locative='MULTIPLE' if len(feature['location_phrases']) > 1 else 'SINGLE' if feature['location_phrases'] else 'ABSENT',
                      location_frame_candidate=bool(feature['location_phrases']) and feature['frame']),
        PARTICIPANT=dict(subjects=sorted(feature['subjects']), objects=sorted(feature['objects']),
                         complements=sorted(feature['complements']), participants=sorted(feature['participants']),
                         mentions=feature['participant_mentions'], absent_from_current_clause_lexemes=feature['absent_participant_lexemes'],
                         absence_status='ABSENT_FROM_CLAUSE_NOT_PROVEN_DISCOURSE_EXIT',
                         semantic_roles='UNRESOLVED', referential_identity='UNRESOLVED'),
        REFERENCE=dict(mentions=feature['references'], anaphora='POTENTIAL_ONLY', cataphora='NOT_RESOLVED'),
        DOMAIN=dict(raw=feature['domain'], interpreted_embedding='UNRESOLVED'),
        LEXICAL=dict(lexemes=row['lexeme_sequence'], semantic_continuity='NOT_INFERRED'),
        RHETORICAL_SECONDARY='NOT_LOADED',
        GRAMMATICAL_CORRESPONDENCE=dict(words=row['words'], phrase_functions=[p['function'] for p in row['phrases']], clause_type=feature['clause_type']),
        TEXT_SYNTACTIC_CORRESPONDENCE=dict(participant_mentions=feature['participant_mentions'], time_phrase_ids=[p['node'] for p in feature['time_phrases']],
                                           location_phrase_ids=[p['node'] for p in feature['location_phrases']], domain=feature['domain']),
        LEXICAL_CORRESPONDENCE=dict(lexemes=row['lexeme_sequence']), SEMANTIC_CORRESPONDENCE=dict(status='NOT_LOADED', role='SECONDARY_CANDIDATE_EVIDENCE'))
