"""Candidate sets describe alternatives; they never accept a mother or peer."""
from milal_review_eligibility import CLASSES


def sets(target, candidates):
    eligible = [r for r in candidates if r['review_eligibility'] in CLASSES[:2]]
    mothers = [r['candidate_id'] for r in eligible if 'HYPOTACTIC' in r['relations']]
    parallels = [r['candidate_id'] for r in eligible if 'PARATACTIC' in r['relations']]
    components = sorted({x for r in eligible for x in r['component_ids']})
    conflicts = sorted({x for r in eligible for x in r['conflict_ids']})
    common = dict(target_id=target, accepted_mother='', accepted_parallel_peer='')
    competition = dict(common, competition_set_id='H0-CS-' + str(target), candidate_ids=[r['candidate_id'] for r in eligible],
        relation_types_present=sorted({x for r in eligible for x in r['relations']}),
        mother_candidate_count=len(mothers), parallel_candidate_count=len(parallels),
        multiple_candidate_count=sum(len(r['relations']) > 1 for r in eligible),
        variant_component_ids=components, global_conflict_count=len(conflicts))
    mother = dict(common, mother_candidate_ids=mothers, mother_candidate_count=len(mothers),
        status='NO_HYPOTACTIC_MOTHER_CANDIDATE' if not mothers else 'SINGLE_HYPOTACTIC_CANDIDATE' if len(mothers) == 1 else 'MOTHER_COMPETITION')
    parallel = dict(common, parallel_candidate_ids=parallels, parallel_candidate_count=len(parallels))
    return competition, mother, parallel


def impacts(candidate, mother_count):
    result = []
    if candidate['component_ids']:
        result.append('AFFECTS_VARIANT_COMPONENT')
    if candidate['conflict_ids']:
        result.append('AFFECTS_MULTIPLE_EXISTING_RELATIONS')
    if 'HYPOTACTIC' in candidate['relations']:
        result.append('AFFECTS_TEXTUAL_LEVEL')
        if mother_count > 1:
            result.append('AFFECTS_MOTHER_COMPETITION')
    if 'PARATACTIC' in candidate['relations']:
        result.append('AFFECTS_PARALLEL_CHAIN')
    return result or ['LOCAL_ONLY' if candidate['review_eligibility'] in CLASSES[:2] else 'NONE']
