"""Linguistic constructions and recurrence, without structural target loci."""
from collections import Counter
from milal_mfr_signatures import key

def nominal_heads(clause):
    """Surface heads of complementary PP/coordinate segments, not identities.

    A later noun inside a title/construct chain is not silently an addressee.
    """
    words={w['node']:w for w in clause['words']};heads=[]
    for phrase in clause['phrases']:
        if phrase['function'] not in ('Cmpl','Objc'):continue
        waiting=True
        for n in phrase['word_ids']:
            w=words[n]
            if w['sp'] in ('prep','conj'):waiting=True;continue
            if w['sp']=='art':continue
            if waiting:heads.append(w['lex']);waiting=False
    return heads

def adjacent_content(lexemes,first,seconds):
    values=[x for x in lexemes if x!='H']
    return any(a==first and b in seconds for a,b in zip(values,values[1:]))

def discover(obs,signatures,rules,prefix):
    freq=Counter(s['SIG_LEXICAL_SLOT'] for s in signatures.values());seqfreq=Counter(s['SIG_SEQUENCE_3'] for s in signatures.values());markers=[]
    for i,c in enumerate(obs):
        sig=signatures[c['clause_id']];window=obs[i:i+rules['construction_window']];lex=[x for n in window for x in n['lexeme_sequence']];here=c['lexeme_sequence'];verbs=c['predicate_lexeme'];prev=obs[i-1] if i else None
        temporal=c['temporal_phrase_structure'];loca=c['locative_phrase_structure'];speech=bool(set(verbs)&set(rules['speech_predicates']));cessation=bool(set(verbs)&set(rules['cessation_predicates']))
        subjects={x for n in window for x in n['subject_lexemes']};complements={x for n in window for p in n['phrases'] if p['function'] in ('Cmpl','Objc','Adju') for x in p['lexemes']}
        tags=[]
        if freq[sig['SIG_LEXICAL_SLOT']]>=2 and (verbs or any(w['sp'] in ('subs','nmpr') for w in c['words'])):tags.append('REPEATED_CLAUSE_FORMULA')
        if seqfreq[sig['SIG_SEQUENCE_3']]>=2 and verbs:tags.append('REPEATED_SEQUENCE_CONFIGURATION')
        if temporal:tags.append('TEMPORAL_FRAME')
        if loca:tags.append('LOCATIVE_FRAME')
        if speech:tags.extend(['SPEECH_PREDICATE_CONSTRUCTION','REPORTED_SPEECH_FORMULA'])
        if cessation:tags.append('EXPLICIT_CESSATION')
        if prev and c['subject_lexemes'] and prev['subject_lexemes'] and c['subject_lexemes']!=prev['subject_lexemes']:tags.append('EXPLICIT_SUBJECT_CONFIGURATION_SHIFT')
        if prev and speech and c['complement_surface'] and prev['complement_surface'] and c['complement_surface']!=prev['complement_surface']:tags.append('EXPLICIT_ADDRESSEE_COMPLEMENT_CONFIGURATION_SHIFT')
        if prev and c['domain'] not in (None,'','?','NA') and prev['domain'] not in (None,'','?','NA') and c['domain']!=prev['domain']:tags.append('DOMAIN_CONFIGURATION_CHANGE')
        if rules['add_predicate'] in verbs and rules['proverb_noun'] in lex and any(x in lex for x in rules['speech_predicates']):tags.append('ADD_PROVERB_SPEECH')
        if rules['open_predicate'] in verbs and rules['mouth_noun'] in lex:tags.append('OPEN_MOUTH_CONSTRUCTION')
        if rules['be_predicate'] in verbs and (temporal or any(x in here for x in rules['temporal_lexemes'])):tags.append('BE_TEMPORAL_CONSTRUCTION')
        explicit_speaker=rules['divine_name'] in c['subject_lexemes']
        call_then_speech=(rules['call_predicate'] in verbs and not c['subject_lexemes'] and i+1<len(obs) and rules['divine_name'] in obs[i+1]['subject_lexemes'] and bool(set(obs[i+1]['predicate_lexeme'])&set(rules['speech_predicates'])))
        if speech and rules['addressee_name'] in nominal_heads(c) and (explicit_speaker or call_then_speech):tags.append('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION')
        if set(here)&set(rules['revelation_nouns']) and (rules['relative_lexeme'] in lex or any(n['temporal_phrase_structure'] for n in window)):tags.append('REVELATION_HEADING_CONFIGURATION')
        if rules['death_predicate'] in verbs:tags.append('DEATH_CONSTRUCTION')
        if any(adjacent_content(p['lexemes'],rules['after_lexeme'],{rules['death_predicate'],rules['death_noun']}) for p in temporal):tags.append('AFTER_DEATH_TEMPORAL_CONSTRUCTION')
        if any(adjacent_content(p['lexemes'],rules['year_noun'],{rules['one_lexeme']}) for p in temporal):tags.append('YEAR_ONE_CONFIGURATION')
        if freq[sig['SIG_LEXICAL_SLOT']]>=2 and (temporal or loca):tags.append('FORMULA_ADJUNCT_EXPANSION')
        if not tags:continue
        explicit=[t for t in tags if not t.startswith('REPEATED_')];base=dict(predicates=verbs,morph=c['verbal_conjugation'],core_order=[f for f in c['constituent_order'] if f not in ('Time','Loca','Adju')])
        # Pure construction labels are observations, never assigned textual levels.
        markers.append(dict(marker_id=prefix+str(len(markers)+1).zfill(6),marker_index=len(markers),clause_id=c['clause_id'],clause_atom_ids=c['clause_atom_ids'],anchor=c['anchor'],book=c['book'],chapter=c['chapter'],verse=c['verse'],sequence_index=i,
            discovery_sources=tags,repeat_count=freq[sig['SIG_LEXICAL_SLOT']],singleton_reason='EXPLICIT_CONSTRUCTION_WITHOUT_SLOT_REPEAT' if freq[sig['SIG_LEXICAL_SLOT']]==1 and explicit else '',formal_explicitness=explicit,
            signatures=sig,base_construction=base,extension_features=dict(time=len(temporal),loca=len(loca),sequence_length=len(window)),added_adjuncts=[p['function'] for p in temporal+loca],removed_adjuncts=[],
            construction_context_clause_ids=[n['clause_id'] for n in window],context_lexemes=lex,context_named_surfaces=sorted({w['lex'] for n in window for w in n['words'] if w['sp']=='nmpr'}),context_content_lexemes=sorted({w['lex'] for n in window for w in n['words'] if w['sp'] in ('verb','subs','nmpr')}),context_subjects=sorted(subjects),context_complements=sorted(complements),
            family_ids=[],automatic_resolution=False,status='UNADJUDICATED'))
    return markers
