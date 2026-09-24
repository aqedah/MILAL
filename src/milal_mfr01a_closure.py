"""Cessation occurrence and evidence for a source-target link are separate."""
ONSET_FORMS = {
    'SPEECH_PREDICATE_CONSTRUCTION', 'REPORTED_SPEECH_FORMULA',
    'OPEN_MOUTH_CONSTRUCTION', 'ADD_PROVERB_SPEECH', 'BE_TEMPORAL_CONSTRUCTION',
    'DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION', 'REVELATION_HEADING_CONFIGURATION',
    'AFTER_DEATH_TEMPORAL_CONSTRUCTION', 'YEAR_ONE_CONFIGURATION',
}
FORMAL_TYPES = {'EXACT_FORM_FAMILY','SLOT_NORMALIZED_FAMILY','MULTI_CLAUSE_CONFIGURATION_FAMILY'}

def closure_link(d, source, target):
    s,t=d['m'][source],d['m'][target];si,ti=int(s['sequence_index']),int(t['sequence_index'])
    cessation='EXPLICIT_CESSATION' in t['discovery_sources']
    onset=sorted(set(s['discovery_sources']) & ONSET_FORMS)
    ending=[c for c in d['by_coverage'][source] if int(c['end_index'])==ti and str(c['candidate_end_anchor']) in {str(x) for x in t['clause_atom_ids']}]
    ending_ids={c['coverage_candidate_id'] for c in ending}
    terminal=[n['nested_evidence_id'] for n in d['by_nested'][source] if n['coverage_candidate_id'] in ending_ids and int(n['nested_marker_index_end_exclusive'])-1==int(t['marker_index']) and int(n['nested_marker_count'])>0]
    formal=sorted(f for f in set(s['family_ids']) & set(t['family_ids']) if d['f'][f]['family_type'] in FORMAL_TYPES)
    span=d['observation'][si:ti+1] if si<ti else []
    named=[set(c['participant_surface_set']) for c in span if c['participant_surface_set']]
    participant=sorted(set.intersection(*named)) if len(named)>1 else []
    domains=[c['domain'] for c in span]
    compatible=bool(domains) and all(x not in (None,'','?','NA') for x in domains) and len(set(domains))==1
    links=[]
    for name,value in (('ONSET_FORM',onset),('COVERAGE_END',ending),('FORMAL_FAMILY',formal),('PARTICIPANT',participant),('DOMAIN',compatible),('NESTED_CONFIGURATION',terminal)):
        if value:links.append('CLOSURE_LINK_'+name)
    if not links:links=['CLOSURE_LINK_NONE']
    statuses=[]
    if cessation:
        if onset and (participant or compatible or terminal):statuses.append('CLOSURE_STRUCTURALLY_LINKED')
        if formal:statuses.append('CLOSURE_FORMALLY_LINKED')
        if ending:statuses.append('CLOSURE_COVERAGE_LINKED')
        if len(statuses)>1:statuses.append('CLOSURE_MULTIPLE_LINK_TYPES')
        if not statuses:statuses.append('CLOSURE_WEAK_PAIR_ONLY')
    else:statuses=['CLOSURE_LINK_INSUFFICIENT']
    eligible=any(x in statuses for x in ('CLOSURE_STRUCTURALLY_LINKED','CLOSURE_FORMALLY_LINKED','CLOSURE_COVERAGE_LINKED'))
    return dict(target_is_cessation=cessation,link_types=links,closure_status=statuses,review_eligible=eligible,
        onset_form_evidence=onset,coverage_end_ids=sorted(ending_ids),coverage_end_bases={c['coverage_candidate_id']:c['end_basis'] for c in ending},
        formal_family_ids=formal,participant_surface_continuity=participant,participant_identity='UNRESOLVED',domain_compatible=compatible,
        domain_values=sorted({str(x) for x in domains}),span_clause_ids=[c['clause_id'] for c in span],terminal_nested_evidence_ids=terminal,
        limitations='MFR_COVERAGE_CAN_BE_MECHANICALLY_CESSATION_DERIVED; LINK_IS_NOT_CLOSURE_ACCEPTANCE; SURFACE_CONTINUITY_NOT_IDENTITY')
