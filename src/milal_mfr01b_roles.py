"""Surface-role candidates. A lexical cessation event is not a discourse verdict."""
from collections import Counter
from milal_mfr01b_data import require, ACCEPTABLE_CESSATION

def cessation(d,m,rules):
    c=d['o'][str(m['clause_id'])];i=int(m['sequence_index']);following=d['observation'][i+1:i+2]
    arguments=[p for p in c['phrases'] if p['function'] in ('Subj','Objc','Cmpl')]
    speech_arguments=[p for p in arguments if set(p['lexemes'])&set(rules['speech_argument_nouns'])]
    physical=[p for p in arguments if set(p['lexemes'])&set(rules['physical_temporal_argument_lexemes'])]
    speech_infinitives=[]
    for clause,kind in [(c,'SAME_CLAUSE'),*((n,'ADJACENT_PREPOSITIONAL_INFINITIVE_CANDIDATE') for n in following)]:
        verbs=[w for w in clause['words'] if w['sp']=='verb' and w['lex'] in rules['speech_predicates'] and w['vt'] in rules['infinitive_forms']]
        if kind!='SAME_CLAUSE' and (not clause['words'] or clause['words'][0]['lex'] not in rules['infinitive_introducers']):continue
        if verbs:speech_infinitives.append(dict(clause_id=clause['clause_id'],link_basis=kind,word_nodes=[w['node'] for w in verbs],words=verbs,phrases=clause['phrases']))
    label=('DISCOURSE_CESSATION_FORM_CANDIDATE' if speech_arguments else
           'SPEECH_ACTIVITY_CESSATION_CANDIDATE' if speech_infinitives else
           'NON_DISCOURSE_CESSATION_USAGE_CANDIDATE' if physical else 'CESSATION_ROLE_AMBIGUOUS')
    return dict(marker_id=m['marker_id'],anchor=m['anchor'],clause_id=m['clause_id'],clause_atom_ids=m['clause_atom_ids'],
        lexical_occurrence='CESSATION_LEXEME_OCCURRENCE',role_candidate=label,predicate_lexemes=c['predicate_lexeme'],predicate_morphology=c['predicate_morphology'],
        predicate_word_nodes=[w['node'] for w in c['words'] if w['lex'] in rules['cessation_predicates'] and w['sp']=='verb'],
        subject=[p for p in arguments if p['function']=='Subj'],object=[p for p in arguments if p['function']=='Objc'],complement=[p for p in arguments if p['function']=='Cmpl'],
        speech_arguments=speech_arguments,speech_infinitive_candidates=speech_infinitives,physical_temporal_arguments=physical,
        participant_configuration=c['participant_surface_set'],domain_before=d['observation'][i-1]['domain'] if i else None,domain_here=c['domain'],
        domain_after=following[0]['domain'] if following else None,surrounding_clause_ids=[n['clause_id'] for n in d['observation'][max(0,i-1):i+3]],
        human_acceptance='',limitations=rules['limitations'])

def audit(d,rules):
    prim=set(rules['primary_sources']);support=set(rules['support_sources']);counts=Counter(t for m in d['markers'] for t in m['discovery_sources'])
    require(not set(counts)-(prim|support),'SCHEMA untyped discovery source: '+str(sorted(set(counts)-(prim|support))))
    cess=[cessation(d,m,rules) for m in d['markers'] if 'EXPLICIT_CESSATION' in m['discovery_sources']];bycess={r['marker_id']:r for r in cess}
    roles=[]
    for m in d['markers']:
        tags=set(m['discovery_sources']);pp=tags&prim;ss=tags&support;effective=set(pp)
        cr=bycess.get(m['marker_id']);lexical_audit=bool(cr)
        # Keep the historical trigger; audit whether it independently bears a formal role.
        if cr and cr['role_candidate'] not in {'DISCOURSE_CESSATION_FORM_CANDIDATE','SPEECH_ACTIVITY_CESSATION_CANDIDATE'}:effective.discard('EXPLICIT_CESSATION')
        role=('COMPOSITE_MARKER_CANDIDATE' if effective and ss else 'PRIMARY_FORMAL_MARKER_CANDIDATE' if effective else
              'LEXICAL_EVENT_CANDIDATE_REQUIRES_ROLE_AUDIT' if pp else 'SUPPORT_SIGNAL_ONLY')
        roles.append(dict(marker_id=m['marker_id'],clause_id=m['clause_id'],clause_atom_ids=m['clause_atom_ids'],anchor=m['anchor'],raw_discovery_sources=m['discovery_sources'],
            primary_trigger_sources=sorted(pp),formal_role_sources=sorted(effective),support_sources=sorted(ss),role=role,primary_bearing=bool(effective),
            lexical_role_audit_required=lexical_audit,cessation_role=cr['role_candidate'] if cr else '',all_bundle_ids=sorted(d['by_marker'][m['marker_id']]),
            force_context_usable=True,participant_identity='UNRESOLVED',automatic_resolution=False))
    byrole={r['marker_id']:r for r in roles};bundles=[]
    for b in d['old_bundles']:
        mids=b['marker_ids'];pp=[m for m in mids if byrole[m]['primary_bearing']];ss=[m for m in mids if byrole[m]['role']=='SUPPORT_SIGNAL_ONLY'];lex=[m for m in mids if byrole[m]['role']=='LEXICAL_EVENT_CANDIDATE_REQUIRES_ROLE_AUDIT']
        typ='PRIMARY_BEARING_BUNDLE' if len(pp)==len(mids) else 'SUPPORT_ONLY_BUNDLE' if len(ss)==len(mids) else 'MIXED_ROLE_BUNDLE'
        bundles.append(dict(bundle_id=b['bundle_id'],marker_ids=mids,raw_family_ids=b['contributing_family_ids'],bundle_role=typ,primary_marker_ids=pp,support_only_marker_ids=ss,lexical_audit_marker_ids=lex,automatic_resolution=False))
    sources=[dict(discovery_source=t,source_role='PRIMARY_FORMAL_TRIGGER_CANDIDATE' if t in prim else 'SUPPORT_SIGNAL',occurrence_count=n,marker_ids=sorted(m['marker_id'] for m in d['markers'] if t in m['discovery_sources'])) for t,n in sorted(counts.items())]
    return dict(sources=sources,roles=roles,bundles=bundles,cessations=cess)
