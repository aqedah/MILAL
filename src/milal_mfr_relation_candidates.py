"""Indexed linguistic pairs. Corpus divisions are never eligibility filters."""
from collections import defaultdict
from itertools import combinations
from milal_mfr_signatures import key


def pair_universe(markers,obs,families,coverage):
    index=defaultdict(set)
    for m in markers:
        i=m['marker_index'];c=obs[m['sequence_index']];tags=m['discovery_sources']
        # Full lexical/slot correspondence is informative by itself. A broad
        # construction needs predicate or surrounding configuration agreement.
        for res in ('SIG_EXACT','SIG_LEXICAL_SLOT','SIG_SEQUENCE_3'):
            if c['predicate_lexeme'] or len(c['lexeme_sequence'])>=3:index[(res,m['signatures'][res])].add(i)
        if c['predicate_lexeme']:
            index[('PREDICATE_CONSTRUCTION',key(m['base_construction']))].add(i)
        for tag in ('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION','REVELATION_HEADING_CONFIGURATION','YEAR_ONE_CONFIGURATION','AFTER_DEATH_TEMPORAL_CONSTRUCTION'):
            if tag in tags:index[('CONSTRUCTION',tag)].add(i)
        if 'DEATH_CONSTRUCTION' in tags or 'AFTER_DEATH_TEMPORAL_CONSTRUCTION' in tags:
            for lex in set(m['context_lexemes']):
                if lex in set(c['subject_lexemes']) or any(lex==w['lex'] and w['sp']=='nmpr' for n in obs[m['sequence_index']:m['sequence_index']+4] for w in n['words']):index[('DEATH_PARTICIPANT',lex)].add(i)
        # Different predicates with the same repeated contextual configuration.
        nxt=obs[m['sequence_index']+1:m['sequence_index']+3]
        if len(nxt)==2 and all(n['predicate_lexeme'] for n in nxt):index[('PARALLEL_CONTEXT',key([(n['predicate_lexeme'],n['constituent_order']) for n in nxt]),key(c['constituent_order']))].add(i)
    pairs=set()
    for members in index.values():pairs.update(combinations(sorted(members),2))
    byclause={m['sequence_index']:m['marker_index'] for m in markers}
    marker_index={m['marker_id']:m['marker_index'] for m in markers}
    for r in coverage:
        if r['end_basis']=='EXPLICIT_CLOSURE' and r['end_index'] in byclause:
            a,b=marker_index[r['marker_id']],byclause[r['end_index']]
            if a!=b:pairs.add(tuple(sorted((a,b))))
    return sorted(pairs),[dict(index_type=k[0],index_signature=str(k[1:]),marker_indices=sorted(v),all_pairs_represented=True) for k,v in sorted(index.items(),key=lambda x:str(x[0])) if len(v)>1]


def relations(markers,obs,force,coverage,pairs,rules,prefix):
    cov=defaultdict(list)
    for r in coverage:cov[r['marker_id']].append(r)
    for count,(a,b) in enumerate(pairs,1):
        s,t=markers[a],markers[b];sc,tc=obs[s['sequence_index']],obs[t['sequence_index']];sf,tf=force[a],force[b]
        exact=s['signatures']['SIG_EXACT']==t['signatures']['SIG_EXACT'];construction=s['signatures']['SIG_CONSTRUCTION']==t['signatures']['SIG_CONSTRUCTION'];slot=s['signatures']['SIG_LEXICAL_SLOT']==t['signatures']['SIG_LEXICAL_SLOT']
        before=sf['HF_CONTEXT_BEFORE']==tf['HF_CONTEXT_BEFORE'] and bool(sf['HF_CONTEXT_BEFORE']);after=sf['HF_CONTEXT_AFTER']==tf['HF_CONTEXT_AFTER'] and bool(sf['HF_CONTEXT_AFTER'])
        participants=sorted(set(sc['participant_surface_set'])&set(tc['participant_surface_set']));sharedlex=sorted(set(s['context_lexemes'])&set(t['context_lexemes']))
        known_domain=sc['domain'] not in ('?',None,'','NA') and tc['domain'] not in ('?',None,'','NA');domain=known_domain and sc['domain']==tc['domain']
        containing=[r['coverage_candidate_id'] for r in cov[s['marker_id']] if r['end_index']>=t['sequence_index'] and r['end_basis']!='ANALYSIS_SCOPE_END']
        formal=exact or slot or construction or bool(set(s['family_ids'])&set(t['family_ids']));resumption=(bool(participants) and bool(set(sc['predicate_lexeme'])&set(tc['predicate_lexeme'])) and t['sequence_index']-s['sequence_index']>1)
        context_resumption=bool(set(s['context_named_surfaces'])&set(t['context_named_surfaces'])) and len(set(s['context_content_lexemes'])&set(t['context_content_lexemes']))>=2 and bool(sc['temporal_phrase_structure'] and tc['temporal_phrase_structure']) and t['sequence_index']-s['sequence_index']>1
        resumption=resumption or context_resumption
        death='DEATH_CONSTRUCTION' in s['discovery_sources'] and 'AFTER_DEATH_TEMPORAL_CONSTRUCTION' in t['discovery_sources'] and bool(set(s['context_subjects'])&set(t['context_lexemes']))
        parallel_context=before or after;subordinate=rules['relative_lexeme'] in tc['lexeme_sequence'] or any(v in ('infc','infa') for v in tc['verbal_conjugation'])
        closure='EXPLICIT_CESSATION' in t['discovery_sources'] and bool(containing)
        labels=[]
        if formal or parallel_context:labels.append('FORMAL_PARALLEL_CANDIDATE')
        if (slot or construction or parallel_context) and parallel_context and domain:labels.append('PARATAXIS_CANDIDATE')
        if (subordinate and (participants or formal) and (containing or parallel_context)) or (resumption and sc['temporal_phrase_structure'] and tc['temporal_phrase_structure'] and sc['lexeme_sequence']!=tc['lexeme_sequence']):labels.append('HYPOTAXIS_CANDIDATE')
        if containing and subordinate and participants:labels.append('EMBEDDING_CANDIDATE')
        if resumption or death:labels.append('RESUMPTION_CANDIDATE')
        if death:labels.append('TEMPORAL_RESUMPTION_CANDIDATE')
        if closure:labels.append('CLOSURE_TARGET_CANDIDATE')
        if closure and any(r['nested_family_count']>1 for r in cov[s['marker_id']] if r['end_basis']=='EXPLICIT_CLOSURE'):labels.append('HIGHER_ORDER_TERMINAL_EFFECT_CANDIDATE')
        if formal and not any(l in labels for l in ('PARATAXIS_CANDIDATE','HYPOTAXIS_CANDIDATE','RESUMPTION_CANDIDATE','CLOSURE_TARGET_CANDIDATE')):labels.append('FORMAL_CORRESPONDENCE_ONLY')
        if len(set(labels)&{'PARATAXIS_CANDIDATE','HYPOTAXIS_CANDIDATE','RESUMPTION_CANDIDATE','CLOSURE_TARGET_CANDIDATE'})>1:labels.append('COMPETING_RELATIONS')
        if not labels:labels=['INSUFFICIENT_EVIDENCE']
        yield dict(relation_candidate_id=prefix+'R'+str(count).zfill(8),source_marker_id=s['marker_id'],target_marker_id=t['marker_id'],source_family_ids=s['family_ids'],target_family_ids=t['family_ids'],source_anchor=s['anchor'],target_anchor=t['anchor'],source_clause_id=s['clause_id'],target_clause_id=t['clause_id'],source_book=s['book'],target_book=t['book'],cross_book=s['book']!=t['book'],same_book_required=False,
            exact_form_correspondence=exact,construction_correspondence=construction,adjunct_correspondence=s['signatures']['SIG_ADJUNCT']==t['signatures']['SIG_ADJUNCT'],context_before_correspondence=before,context_after_correspondence=after,participant_correspondence=participants,domain_correspondence=domain,temporal_correspondence=bool(sc['temporal_phrase_structure'] and tc['temporal_phrase_structure']),locative_correspondence=bool(sc['locative_phrase_structure'] and tc['locative_phrase_structure']),
            coverage_relationship=containing,nested_relationship=bool(containing),resumption_evidence=dict(lexical_participant=resumption,temporal_context_recurrence=context_resumption,death_temporal=death,shared_context_lexemes=sharedlex),closure_evidence=closure,competing_evidence=dict(different_predicates=sc['predicate_lexeme']!=tc['predicate_lexeme'],different_domains=sc['domain']!=tc['domain'],different_expansion=s['extension_features']!=t['extension_features'],distance=t['sequence_index']-s['sequence_index']),
            limitations='FORMAL_CORRESPONDENCE_NOT_PLACEMENT; PARTICIPANT_SURFACE_NOT_IDENTITY; CANDIDATE_DIRECTION_FOLLOWS_SOURCE_ORDER',relation_candidates=labels,automatic_resolution=False,status='UNADJUDICATED',scope_external_status='OUTSIDE_SCOPE_NOT_TESTED')
