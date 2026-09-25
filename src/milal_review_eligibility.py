"""Review eligibility only; consumes existing relations without evaluating grammar."""
CLASSES = ('RELATION_ELIGIBLE', 'CONFIGURATION_ELIGIBLE', 'EVIDENCE_ONLY', 'INSUFFICIENT')
RELATIONS = {'HYPOTACTIC', 'PARATACTIC', 'MULTIPLE'}
EVIDENCE_FACTS = {'formal_correspondence', 'lexical_continuity', 'time_continuity',
                  'temporal_connection', 'location_continuity', 'participant_continuity',
                  'reference_continuity', 'domain_continuity', 'sequence_correspondence'}


def classify(candidate, context):
    """Disjoint class, lossless overlapping reasons. History is not an input."""
    status = candidate['candidate_relations']
    reasons = set()
    if status in RELATIONS:
        reasons.add('EXISTING_' + status)
    if context.get('source_family_conflict'):
        reasons.add('SOURCE_FAMILY_CONFLICT')
    if context.get('deferred') or status in ('RELATION_DEFERRED_PENDING_CLAUSE_BINDING','RELATION_DEFERRED_PENDING_BINDING'):
        reasons.add('VALENCY_UNRESOLVED')
    relation = bool(reasons)
    if context.get('conflict_ids'):
        reasons.add('GLOBAL_CONFLICT')
    if context.get('component_ids'):
        reasons.add('VARIANT_COMPONENT')
    if context.get('configuration_ids'):
        reasons.add('CURRENT_CONFIGURATION_MEMBERSHIP')
    if context.get('poetry_exception'):
        reasons.add('POETRY_SYNTAX_CONFLICT')
    configuration = bool(reasons)
    evidence = status == 'FORMAL_ONLY' or any(candidate.get('facts', {}).get(k) for k in EVIDENCE_FACTS)
    evidence = evidence or bool(context.get('poetic_labels')) or bool(context.get('exact_pair_analogue'))
    eligibility = CLASSES[0] if relation else CLASSES[1] if configuration else CLASSES[2] if evidence else CLASSES[3]
    if eligibility == 'EVIDENCE_ONLY':
        reasons.add('CORRESPONDENCE_WITHOUT_RELATION_OR_CONFIGURATION')
    if eligibility == 'INSUFFICIENT':
        reasons.add('NO_ACTIVE_RELATION_OR_CONFIGURATION')
    return dict(review_eligibility=eligibility, review_reason_codes=sorted(reasons))


def target_status(candidates, context):
    eligible = [r for r in candidates if r['review_eligibility'] in CLASSES[:2]]
    relation = [r for r in eligible if r['review_eligibility'] == CLASSES[0]]
    kinds = {k for r in relation for k in r['relations']}
    reasons = set()
    if len(relation) > 1:
        reasons.add('MULTIPLE_RELATION_CANDIDATES')
    if {'HYPOTACTIC', 'PARATACTIC'} <= kinds:
        reasons.add('HYPOTACTIC_PARATACTIC_COMPETITION')
    for r in eligible:
        reasons.update(set(r['review_reason_codes']) & {'EXISTING_MULTIPLE', 'GLOBAL_CONFLICT', 'VARIANT_COMPONENT', 'SOURCE_FAMILY_CONFLICT', 'VALENCY_UNRESOLVED', 'POETRY_SYNTAX_CONFLICT'})
    if context.get('binding_ids'):
        reasons.add('VALENCY_UNRESOLVED')
    if context.get('component_ids'):
        reasons.add('VARIANT_COMPONENT')
    if context.get('revalidation_ids'):
        reasons.add('MFR02A_REVALIDATION')
    required = bool(reasons)
    status = 'TARGET_REVIEW_REQUIRED' if required else 'TARGET_REVIEW_OPTIONAL' if eligible else 'TARGET_ARCHIVE_ONLY'
    tier = 'TIER_1' if context.get('tier1') else 'TIER_2' if required else 'TIER_3' if eligible else ''
    return dict(target_review_status=status, review_tier=tier, review_reason_codes=sorted(reasons))


def relation_types(status):
    return ['HYPOTACTIC', 'PARATACTIC'] if status == 'MULTIPLE' else [status] if status in RELATIONS else []
