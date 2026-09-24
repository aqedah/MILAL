"""Inspectable linguistic candidate bundles, never accepted hierarchy relations."""
from __future__ import annotations
from milal_jin_io import require

UNKNOWN=(None,'','NA','unknown','?')
LABELS=('PARATAXIS_SUPPORTED','HYPOTAXIS_SUPPORTED','PARATAXIS_AND_HYPOTAXIS_SUPPORTED',
        'HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED','RELATION_CANDIDATE_INSUFFICIENT','NO_LINGUISTIC_SUPPORT')


def clean(values):return {v for v in values if v not in UNKNOWN}
def png(w,suffix=False):return tuple(w.get(('prs_' if suffix else '')+k) for k in ('ps','gn','nu'))
def png_equal(a,b):return all(v not in UNKNOWN for v in a+b) and a==b


def extract(clauses,rules):
    result=[]
    for i,c in enumerate(clauses):
        ww=c['words'];verbs=[w for w in ww if w['sp']=='verb'];byid={w['node']:w for w in ww}
        pp=[]
        for p in c['phrases']:
            positions=[c['word_nodes'].index(w)+1 for w in p['word_nodes']]
            pp.append(dict(**p,positions=positions,surface=''.join(byid[w]['g_word_utf8']+(byid[w].get('trailer_utf8') or '') for w in p['word_nodes']),lexemes=[byid[w]['lex'] for w in p['word_nodes']]))
        subject_ids={w for p in pp if p['function']=='Subj' for w in p['word_nodes']}
        subjects=[w for w in ww if w['node'] in subject_ids and w['sp'] in ('subs','nmpr','prps','prde')]
        names=[w for w in ww if w['sp']=='nmpr']
        lexemes=[w['lex'] for w in ww];relative=[w['node'] for w in ww if w['lex'] in rules['relative_markers']]
        ambiguous=[w['node'] for w in ww if w['lex'] in rules['conditional_causal_markers']]
        finite=[w for w in verbs if w['vt'] not in UNKNOWN+('infc','infa','ptca','ptcp')]
        infinitive=[w['node'] for w in verbs if w['vt'] in ('infc','infa')]
        participle=[w['node'] for w in verbs if w['vt'] in ('ptca','ptcp')]
        pronouns=[w for w in ww if w['sp'] in ('prps','prde')]
        suffix=[w for w in ww if w.get('prs_ps') not in UNKNOWN]
        context=clauses[i:i+rules['formula_context_clauses']]
        context_words=[w for n in context for w in n['words']]
        context_lex=[w['lex'] for w in context_words]
        families=[]
        for name,pattern in rules['formula_patterns'].items():
            # Ordered subsequence, anchored by its first lexeme inside this clause.
            if pattern[0] not in lexemes:continue
            cursor=0
            for value in context_lex:
                if value==pattern[cursor]:cursor+=1
                if cursor==len(pattern):families.append(name);break
        times=[p for p in pp if p['function']=='Time'];loca=[p for p in pp if p['function']=='Loca']
        wayhi=any(w['lex']=='HJH[' and w['vt']=='wayq' and png(w)==('p3','m','sg') for w in verbs)
        result.append(dict(**c,feature_id='JL:'+str(c['clause_id']),sequence_index=i,verbal=bool(verbs),
            verbal_words=verbs,finite_verbal_words=finite,explicit_subjects=subjects,proper_name_mentions=names,
            implicit_subject_morphology=[dict(word_id=w['node'],png=list(png(w)),identity='UNRESOLVED') for w in finite] if not subjects else [],
            pronouns=pronouns,suffixes=suffix,phrase_details=pp,
            constituent_order=[p['function'] for p in pp],phrase_function_signature=sorted(clean(p['function'] for p in pp)),
            subject_positions=[p['positions'] for p in pp if p['function']=='Subj'],predicate_positions=[p['positions'] for p in pp if p['function'] in ('Pred','PreS','PreO')],
            object_complement_adjunct=[p for p in pp if p['function'] in ('Objc','Cmpl','Adju')],
            temporal_phrases=times,locative_phrases=loca,conjunctions=[w for w in ww if w['sp']=='conj'],
            relative_marker_words=relative,ambiguous_causal_conditional_words=ambiguous,infinitive_words=infinitive,participle_words=participle,
            main_clause_compatible=bool((finite or not verbs) and not relative and not infinitive),
            lexemes=lexemes,content_lexemes=sorted(clean(w['lex'] for w in ww if w['sp'] in ('verb','subs','nmpr','adjv'))),
            subject_lexemes=sorted(clean(w['lex'] for w in subjects)),participant_surfaces=sorted(clean(w['lex'] for w in subjects+names)),
            formula_atoms=families,formula_context_clause_ids=[x['clause_id'] for x in context],
            formula_context_surface=''.join(x['surface'] for x in context),wayhi_temporal=wayhi and bool(times),
            evidence_policy='RAW_FEATURES_AND_EXPLICIT_RULE_DERIVATIONS; NO_RESOLVED_COREFERENCE'))
    return result


def evidence(pre,cur,rules):
    pv,cv=pre['verbal_words'],cur['verbal_words'];distance=cur['sequence_index']-pre['sequence_index']
    local=0<distance<=rules['local_dependency_clause_window']
    form=bool(pv and cv and any(a['lex']==b['lex'] and a['vs']==b['vs'] and a['vt']==b['vt'] and a['vt'] not in UNKNOWN for a in pv for b in cv))
    pngmatch=any(png_equal(png(a),png(b)) for a in pv for b in cv)
    subj=set(pre['subject_lexemes']) & set(cur['subject_lexemes'])
    participants=set(pre['participant_surfaces']) & set(cur['participant_surfaces'])
    reference_png=[png(w) for w in cur['pronouns']]+[png(w,True) for w in cur['suffixes']]
    ant_png=[('p3',w.get('gn'),w.get('nu')) for w in pre['explicit_subjects'] if w['sp'] in ('subs','nmpr')]
    pron=local and any(png_equal(a,b) for a in reference_png for b in ant_png)
    suffix=local and any(png_equal(png(w,True),a) for w in cur['suffixes'] for a in ant_png)
    relative=bool(local and cur['relative_marker_words'] and (pre['explicit_subjects'] or pre['proper_name_mentions']))
    inf=bool(local and cur['infinitive_words'] and pre['finite_verbal_words'] and (participants or pngmatch))
    causal=bool(local and cur['ambiguous_causal_conditional_words'] and (participants or subj or pngmatch))
    speech_embedding=bool(local and any(w['lex']=='>MR[' for w in pv) and pre['domain'] not in UNKNOWN and pre['domain']!=cur['domain'] and cur['domain']=='Q')
    background=bool(local and cur['temporal_phrases'] and participants and cur['finite_verbal_words'] and not any(w['vt']=='wayq' for w in cv))
    f=dict(F_CLAUSE_TYPE_SAME=pre['clause_type']==cur['clause_type'],F_CLAUSE_TYPE_DIFFERENT=pre['clause_type']!=cur['clause_type'],
        F_VERB_FORM_CORRESPONDENCE=form,F_PNG_CORRESPONDENCE=pngmatch,
        F_CONSTITUENT_ORDER_CORRESPONDENCE=bool(pre['constituent_order'] and pre['constituent_order']==cur['constituent_order']),
        F_PHRASE_FUNCTION_CORRESPONDENCE=bool(pre['phrase_function_signature'] and pre['phrase_function_signature']==cur['phrase_function_signature']),
        F_FORMULA_CORRESPONDENCE=bool(set(pre['formula_atoms']) & set(cur['formula_atoms'])),
        R_EXPLICIT_PARTICIPANT_RECURRENCE=bool(subj),R_PRONOMINAL_CONTINUITY=pron,R_SUFFIX_CONTINUITY=suffix,
        R_PARTICIPANT_SET_CONTINUITY=bool(participants),R_PARTICIPANT_SET_CHANGE=bool(pre['participant_surfaces'] and cur['participant_surfaces'] and set(pre['participant_surfaces'])!=set(cur['participant_surfaces'])),
        S_EXPLICIT_SUBORDINATION_MARKER=relative,S_RELATIVE_CONSTRUCTION=relative,S_INFINITIVE_DEPENDENCY=inf,
        S_CAUSAL_CONDITIONAL_PURPOSE_MARKER=causal,S_ANAPHORIC_DEPENDENCY=pron or suffix,S_BACKGROUND_DEPENDENCY_CANDIDATE=background,
        D_SAME_DOMAIN=pre['domain']==cur['domain'] and pre['domain'] not in UNKNOWN,
        D_DOMAIN_SHIFT=pre['domain']!=cur['domain'] and pre['domain'] not in UNKNOWN and cur['domain'] not in UNKNOWN,
        D_TEMPORAL_FRAME_CORRESPONDENCE=bool(pre['temporal_phrases'] and cur['temporal_phrases'] and set(x for p in pre['temporal_phrases'] for x in p['lexemes']) & set(x for p in cur['temporal_phrases'] for x in p['lexemes'])),
        D_LOCATIVE_FRAME_CORRESPONDENCE=bool(pre['locative_phrases'] and cur['locative_phrases'] and set(x for p in pre['locative_phrases'] for x in p['lexemes']) & set(x for p in cur['locative_phrases'] for x in p['lexemes'])),
        D_MAIN_LINE_CORRESPONDENCE_CANDIDATE=pre['main_clause_compatible'] and cur['main_clause_compatible'],D_EMBEDDED_LINE_CANDIDATE=speech_embedding,
        L_LEXEME_RECURRENCE=bool(set(pre['content_lexemes']) & set(cur['content_lexemes'])),L_KEY_FORMULA_RECURRENCE=bool(set(pre['formula_atoms']) & set(cur['formula_atoms'])))
    triggers=[k for k in ('F_CLAUSE_TYPE_SAME','F_VERB_FORM_CORRESPONDENCE','F_FORMULA_CORRESPONDENCE','R_EXPLICIT_PARTICIPANT_RECURRENCE','R_PARTICIPANT_SET_CONTINUITY','R_PRONOMINAL_CONTINUITY','R_SUFFIX_CONTINUITY','S_RELATIVE_CONSTRUCTION','S_INFINITIVE_DEPENDENCY','S_CAUSAL_CONDITIONAL_PURPOSE_MARKER','S_BACKGROUND_DEPENDENCY_CANDIDATE','D_EMBEDDED_LINE_CANDIDATE','D_TEMPORAL_FRAME_CORRESPONDENCE','D_LOCATIVE_FRAME_CORRESPONDENCE','L_LEXEME_RECURRENCE') if f[k]]
    if f['F_CONSTITUENT_ORDER_CORRESPONDENCE'] and f['F_PHRASE_FUNCTION_CORRESPONDENCE']:triggers.append('CONSTITUENT_CONFIGURATION')
    # Boolean bundles across morphology, configuration and reference/frame dimensions.
    formal=f['F_FORMULA_CORRESPONDENCE'] or (form and f['F_CONSTITUENT_ORDER_CORRESPONDENCE'] and f['F_PHRASE_FUNCTION_CORRESPONDENCE'])
    reference=bool(subj) or f['D_TEMPORAL_FRAME_CORRESPONDENCE'] or f['D_LOCATIVE_FRAME_CORRESPONDENCE']
    para=bool(f['D_MAIN_LINE_CORRESPONDENCE_CANDIDATE'] and f['D_SAME_DOMAIN'] and formal and pngmatch and reference and not relative and not inf and not speech_embedding and not causal)
    hypo=bool(relative or inf or causal or pron or suffix or background or speech_embedding)
    label='PARATAXIS_AND_HYPOTAXIS_SUPPORTED' if para and hypo else 'HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED' if relative else 'HYPOTAXIS_SUPPORTED' if hypo else 'PARATAXIS_SUPPORTED' if para else 'RELATION_CANDIDATE_INSUFFICIENT' if triggers else 'NO_LINGUISTIC_SUPPORT'
    bundles=[]
    if para:bundles.append('P1_MAIN_FORM_MORPH_REFERENCE_DOMAIN')
    for name,value in [('H1_RELATIVE_WITH_NOMINAL_ANTECEDENT',relative),('H2_INFINITIVE_SHARED_ARGUMENT',inf),('H3_POLYSEMOUS_MARKER_WITH_CONTEXT',causal),('H4_PRONOMINAL_MORPH_COMPATIBILITY',pron or suffix),('H5_TEMPORAL_BACKGROUND_WITH_RECURRENCE',background),('H6_SAY_VERB_TO_QUOTED_DOMAIN',speech_embedding)]:
        if value:bundles.append(name)
    return dict(eligible=bool(triggers),trigger_reason_codes=triggers,evidence_flags=f,rule_bundles=bundles,
        parataxis_supported=para,hypotaxis_supported=hypo,relation_hypothesis=label,
        relation_candidate_status='UNADJUDICATED',automatic_resolution=False,
        referential_limit='Morphological compatibility is a candidate, never participant identity resolution.')
