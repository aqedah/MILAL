"""Oriented marker-pair cases preserve all raw labels and overlapping buckets."""
from collections import defaultdict
from milal_mfr01a_closure import closure_link

HIERARCHY = {'PARATAXIS_CANDIDATE','HYPOTAXIS_CANDIDATE','EMBEDDING_CANDIDATE','COMPETING_RELATIONS'}
RESUMPTION = {'RESUMPTION_CANDIDATE','TEMPORAL_RESUMPTION_CANDIDATE'}
FORMAL = {'FORMAL_PARALLEL_CANDIDATE','FORMAL_CORRESPONDENCE_ONLY'}

def consolidate(d, by_marker, prefix='MRC'):
    groups=defaultdict(list)
    for r in d['relations']:groups[(r['source_marker_id'],r['target_marker_id'])].append(r)
    cases=[];crosswalk=[];closures=[];review=[];archive=[]
    for n,((source,target),raw) in enumerate(sorted(groups.items()),1):
        raw=sorted(raw,key=lambda r:r['relation_candidate_id']);cid=prefix+str(n).zfill(8)
        labels=sorted({label for r in raw for label in r['relation_candidates']});buckets=[];reasons=[]
        has_closure='CLOSURE_TARGET_CANDIDATE' in labels
        ce=closure_link(d,source,target) if has_closure else {}
        resumption=bool(set(labels)&RESUMPTION) and any(any(r['resumption_evidence'].get(k) is True for k in ('lexical_participant','temporal_context_recurrence','death_temporal')) for r in raw)
        if set(labels)&HIERARCHY:buckets.append('REL_A_HIERARCHY_COMPETING');reasons.append('RAW_HIERARCHY_POSSIBILITY')
        if set(labels)&RESUMPTION:buckets.append('REL_B_RESUMPTION')
        if resumption:reasons.append('RAW_RESUMPTION_EVIDENCE')
        if has_closure:
            buckets.append('REL_C_CLOSURE_REVIEW' if ce['review_eligible'] else 'REL_E_WEAK_CLOSURE_ARCHIVE')
            if ce['review_eligible']:reasons.append('LINGUISTIC_CLOSURE_LINK')
        formal_only=bool(set(labels)&FORMAL) and set(labels)<=FORMAL
        if formal_only:buckets.append('REL_D_FORMAL_CORRESPONDENCE')
        if 'INSUFFICIENT_EVIDENCE' in labels:buckets.append('REL_F_INSUFFICIENT')
        s,t=d['m'][source],d['m'][target]
        shared=set(s['family_ids'])&set(t['family_ids'])
        expansion=[f for f in sorted(shared) if d['f'][f]['family_type']=='ADJUNCT_EXPANSION_FAMILY' and s['extension_features']!=t['extension_features']]
        sequences=[f for f in sorted(shared) if d['f'][f]['family_type']=='MULTI_CLAUSE_CONFIGURATION_FAMILY' and int(d['f'][f]['occurrence_count'])>=2]
        if formal_only and (expansion or sequences):reasons.append('FORMAL_FORCE_COMPARISON_REQUIRED')
        rawids=[r['relation_candidate_id'] for r in raw]
        coverage=sorted({c for r in raw for c in r['coverage_relationship']})
        nested=sorted({r['nested_evidence_id'] for r in d['by_nested'][source] if r['coverage_candidate_id'] in coverage})
        fields=('exact_form_correspondence','construction_correspondence','adjunct_correspondence','context_before_correspondence','context_after_correspondence','participant_correspondence','domain_correspondence','temporal_correspondence','locative_correspondence')
        case=dict(case_id=cid,source_marker_id=source,target_marker_id=target,source_profile_id=source,target_profile_id=target,
            source_bundle_ids=sorted(by_marker[source]),target_bundle_ids=sorted(by_marker[target]),raw_relation_ids=rawids,raw_labels=labels,buckets=buckets,
            correspondence_evidence=[dict(raw_relation_id=r['relation_candidate_id'],**{k:r[k] for k in fields}) for r in raw],
            coverage_ids=coverage,nested_evidence_ids=nested,force_evidence_ids=[source,target],
            resumption_evidence=[r['resumption_evidence'] for r in raw],resumption_supported=resumption,closure_link=ce,
            expansion_comparison_family_ids=expansion,sequence_comparison_family_ids=sequences,competing_evidence=[r['competing_evidence'] for r in raw],
            default_review=bool(reasons),review_inclusion_evidence=reasons,cross_book=s['book']!=t['book'],automatic_resolution=False,
            limitations=[r['limitations'] for r in raw])
        cases.append(case)
        for r in raw:
            crosswalk.append(dict(raw_relation_candidate_id=r['relation_candidate_id'],case_id=cid,source_marker_id=source,target_marker_id=target,raw_labels=r['relation_candidates'],buckets=buckets))
            if 'CLOSURE_TARGET_CANDIDATE' in r['relation_candidates']:
                closures.append(dict(raw_relation_candidate_id=r['relation_candidate_id'],case_id=cid,source_marker_id=source,target_marker_id=target,**ce,automatic_resolution=False))
        disposition=dict(case_id=cid,raw_relation_ids=rawids,buckets=buckets,inclusion_evidence=reasons,disposition='DEFAULT_REVIEW' if reasons else 'ARCHIVE_FOR_REFERENCE',automatic_resolution=False)
        (review if reasons else archive).append(disposition)
    return cases,crosswalk,closures,review,archive
