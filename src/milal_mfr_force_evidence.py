"""Independent evidence dimensions without aggregate score or placement."""
from collections import defaultdict

def force(markers,obs,families,coverage,nested):
    ff={f['family_id']:f for f in families};cov=defaultdict(list);nest=defaultdict(list)
    for r in coverage:cov[r['marker_id']].append(r)
    for r in nested:nest[r['marker_id']].append(r['nested_evidence_id'])
    positions={m['marker_id']:m['sequence_index'] for m in markers};out=[]
    for m in markers:
        i=m['sequence_index'];c=obs[i];before=obs[max(0,i-2):i];after=obs[i+1:i+3]
        out.append(dict(marker_id=m['marker_id'],HF_FORMAL_ELABORATION=dict(base=m['base_construction'],extension=m['extension_features'],adjuncts=m['added_adjuncts']),HF_RECURRENCE={f:ff[f]['occurrence_count'] for f in m['family_ids']},HF_DISTRIBUTION=dict(position=i,family_position_and_gap_records=m['family_ids'],lookup='FAMILY_REGISTRY.occurrence_positions/recurrence_gaps'),
            HF_CONTEXT_BEFORE=[dict(predicate=n['predicate_lexeme'],order=n['constituent_order'],domain=n['domain']) for n in before],HF_CONTEXT_AFTER=[dict(predicate=n['predicate_lexeme'],order=n['constituent_order'],domain=n['domain']) for n in after],
            HF_PARTICIPANT_CONFIGURATION=dict(surface=c['participant_surface_set'],before=before[-1]['participant_surface_set'] if before else [],after=after[0]['participant_surface_set'] if after else [],identity='UNRESOLVED'),
            HF_DOMAIN_CONFIGURATION=dict(current=c['domain'],before=before[-1]['domain'] if before else None,after=after[0]['domain'] if after else None),HF_TEMPORAL_CONFIGURATION=c['temporal_phrase_structure'],HF_LOCATIVE_CONFIGURATION=c['locative_phrase_structure'],
            HF_NESTED_MARKERS=nest[m['marker_id']],HF_CLOSURE_CORRESPONDENCE=[r['coverage_candidate_id'] for r in cov[m['marker_id']] if r['end_basis']=='EXPLICIT_CLOSURE'],HF_COVERAGE_CANDIDATES=[r['coverage_candidate_id'] for r in cov[m['marker_id']]],
            HF_RESUMPTION=dict(lexical_families=[f for f in m['family_ids'] if ff[f]['family_type']=='LEXICAL_RESUMPTION_FAMILY'],preceding_occurrences_preserved=True),HF_CROSS_FAMILY_RELATION=dict(overlapping_families=m['family_ids'],extension=m['extension_features']),automatic_resolution=False))
    return out
