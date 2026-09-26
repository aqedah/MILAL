"""Q1.6R process roles, not relation qualification or referent assignment."""
ROLES=('PRE_RELATION_STRUCTURE','PRIMARY_SOURCE_BINDING','CORROBORATIVE_RELATION_EVIDENCE','REFERENCE_VISIBILITY_CONTEXT','CONFIGURATION_CONTEXT','POST_RELATION_VALIDATION','GLOBAL_CONSTRAINT','HYBRID_WITH_EXPLICIT_SUBTYPES','UNRESOLVED_ROLE')
INDEPENDENCE=('SAME_RAW_EVIDENCE','DERIVED_FROM_SAME_RAW_EVIDENCE','SHARED_CONTEXT_ONLY','ANALYTICALLY_DEPENDENT','INDEPENDENT_RAW_EVIDENCE','UNRESOLVED_INDEPENDENCE')


def process_role(e):
    kind=e['process_kind']
    if kind=='ATOM_CONSTITUTION':
        if e.get('source_clause') and e['source_clause']==e.get('target_clause'):return 'PRE_RELATION_STRUCTURE'
        return 'PRIMARY_SOURCE_BINDING' if e.get('explicit_interclausal_governance') else 'UNRESOLVED_ROLE'
    if kind in ('NATIVE_DEPENDENCY','EXPLICIT_REFERENCE','QUALIFIED_CONFIGURATION'):
        return 'PRIMARY_SOURCE_BINDING' if e.get('verified_pair_path') else 'UNRESOLVED_ROLE'
    if kind=='PARTICIPANT_CONTINUATION':
        return 'CORROBORATIVE_RELATION_EVIDENCE' if e.get('dependent_on') else 'PRIMARY_SOURCE_BINDING' if e.get('verified_pair_path') else 'UNRESOLVED_ROLE'
    if kind in ('TIME_PARAMETER','LOCATION_PARAMETER'):return 'CONFIGURATION_CONTEXT'
    if kind in ('TEMPORAL_REFERENCE_FORM','LOCATIVE_REFERENCE_FORM','EXPLICIT_DEICTIC','MARKED_ANAPHORA','REFERENCE_FORM'):
        return 'REFERENCE_VISIBILITY_CONTEXT' # Dispatch to existing SB02/SB03, never duplicate.
    if kind in ('DERIVED_DOMAIN','EXPLICIT_NATIVE_DOMAIN'):return 'REFERENCE_VISIBILITY_CONTEXT'
    if kind in ('LEXICAL_REPETITION','LEXICAL_FORM_OBSERVATION','NATIVE_ALIAS','FRAME_CORRESPONDENCE'):return 'CORROBORATIVE_RELATION_EVIDENCE'
    if kind in ('LEXICAL_SEMANTICS','TEMPORAL_INTERPRETATION','GEOGRAPHICAL_INTERPRETATION'):return 'POST_RELATION_VALIDATION'
    if kind=='GLOBAL_COMPATIBILITY':return 'GLOBAL_CONSTRAINT'
    return 'UNRESOLVED_ROLE'


def valency_case(a,b,owner_a,owner_b,recorded_clause,explicit_interclausal=False):
    common=set(owner_a)&set(owner_b)
    exact=bool(recorded_clause) and common=={str(recorded_clause)} and set(owner_a)==set(owner_b)
    status='INTRA_CLAUSE_PRE_RELATION' if exact else 'INTER_CLAUSAL_GOVERNANCE_ATTESTED' if owner_a and owner_b and not common and explicit_interclausal else 'UNRESOLVED_OWNERSHIP_OR_GOVERNANCE'
    return dict(source_atom=str(a),target_atom=str(b),source_owners=sorted(owner_a),target_owners=sorted(owner_b),same_native_clause=exact,case_class=status,primary_role='PRE_RELATION_STRUCTURE' if exact else 'PRIMARY_SOURCE_BINDING' if explicit_interclausal and not common else 'UNRESOLVED_ROLE',new_relation=False)


def independence(a,b):
    ca,cb=set(a['core_raw']),set(b['core_raw']);fa,fb=set(a['full_raw']),set(b['full_raw'])
    direct=ca&cb; inherited=((ca|set(a['inherited_core_raw']))&(cb|set(b['inherited_core_raw'])))-direct
    analytic=a['id'] in b['analytical_dependencies'] or b['id'] in a['analytical_dependencies']
    if analytic:kind='ANALYTICALLY_DEPENDENT'
    elif direct:kind='SAME_RAW_EVIDENCE'
    elif inherited:kind='DERIVED_FROM_SAME_RAW_EVIDENCE'
    elif fa&fb and (a['complete'] and b['complete']):kind='SHARED_CONTEXT_ONLY'
    elif ca and cb and a['complete'] and b['complete']:kind='INDEPENDENT_RAW_EVIDENCE'
    else:kind='UNRESOLVED_INDEPENDENCE'
    return dict(independence_class=kind,same_direct_raw=sorted(direct),derived_same_raw=sorted(inherited),shared_context_or_cross_role_raw=sorted((fa&fb)-direct-inherited),analytical_dependency=analytic,independent_raw_basis=bool(ca and cb and not direct and not analytic and a['complete'] and b['complete']))


def readiness(registry,missing_primary,ambiguous_roles,integrity,compatibility):
    if missing_primary:return 'NEEDS_PRIMARY_BINDING_IMPLEMENTATION'
    if not integrity or not compatibility or ambiguous_roles or len(registry)!=12 or any(r['primary_methodological_role']=='UNRESOLVED_ROLE' for r in registry):return 'NEEDS_MECHANISM_ONTOLOGY_REVIEW'
    return 'READY_FOR_MFR_0_2R_H0_1'


def mechanism_overlaps(bases):
    """Exact shared core inputs and explicit analytical parent mechanisms."""
    result={b['mechanism']:set() for b in bases.values()};users={}
    for b in bases.values():
        for raw in set(b['core_raw'])|set(b['inherited_core_raw']):
            users.setdefault(raw,set()).add(b['mechanism'])
        for parent in b['analytical_dependencies']:
            other=bases[parent]['mechanism']
            if other!=b['mechanism']:
                result[b['mechanism']].add(other);result[other].add(b['mechanism'])
    for mechanisms in users.values():
        for m in mechanisms:result[m].update(mechanisms-{m})
    return result
