"""Occurrence-set presentation bundles retain every distinct family claim."""
from collections import defaultdict, Counter
from milal_mfr01a_data import js, sha, ref, features

TYPE_FIELDS = {
    'EXACT_FORM_FAMILY': 'exact_form_families', 'CONSTRUCTION_FAMILY': 'construction_families',
    'SLOT_NORMALIZED_FAMILY': 'slot_families', 'ADJUNCT_EXPANSION_FAMILY': 'adjunct_families',
    'MULTI_CLAUSE_CONFIGURATION_FAMILY': 'multi_clause_families',
    'PARTIAL_FORMAL_FAMILY': 'partial_families', 'LEXICAL_RESUMPTION_FAMILY': 'resumption_families',
}

def bundle(d, prefix='MEB'):
    groups = defaultdict(list)
    for f in d['families']: groups[tuple(sorted(f['marker_ids']))].append(f)
    bundles = []; membership = []; audit = []; by_marker = defaultdict(list)
    for i, (occurrences, families) in enumerate(sorted(groups.items()), 1):
        bid = prefix + str(i).zfill(6); families = sorted(families, key=lambda f: f['family_id'])
        types = sorted({f['family_type'] for f in families})
        explicit = {mid: d['m'][mid]['formal_explicitness'] for mid in occurrences if d['m'][mid]['formal_explicitness']}
        categories = ['REPEATED_OCCURRENCE_BUNDLE' if len(occurrences) > 1 else 'SINGLETON_EXPLICIT_BUNDLE' if explicit else 'SINGLETON_GENERIC_BUNDLE']
        categories.append('MULTI_RESOLUTION_BUNDLE' if len(types) > 1 else 'SINGLE_RESOLUTION_BUNDLE')
        bundles.append(dict(bundle_id=bid, canonical_occurrence_set=list(occurrences), marker_ids=list(occurrences), occurrence_count=len(occurrences),
            categories=categories, contributing_family_ids=[f['family_id'] for f in families], contributing_family_types=types,
            family_evidence=families, explicit_construction_evidence=explicit, automatic_resolution=False,
            limitations='BUNDLE_PRESENTS_DISTINCT_CLAIMS; OCCURRENCE_SET_EQUALITY_IS_NOT_LEVEL_EQUALITY'))
        for mid in occurrences: by_marker[mid].append(bid)
        for f in families:
            membership.append(dict(bundle_id=bid, family_id=f['family_id'], family_type=f['family_type'], marker_ids=f['marker_ids'], construction_definition=f['construction_definition'], signature_resolution=f['signature_resolution']))
            audit.append(dict(family_id=f['family_id'], family_type=f['family_type'], occurrence_count=int(f['occurrence_count']), canonical_occurrence_set=list(occurrences), bundle_id=bid, families_in_bundle=len(families), family_original_sha256=sha(js(f))))
    return bundles, membership, audit, by_marker

def profiles(d, by_marker):
    out = []
    for mid, m in sorted(d['m'].items()):
        c = d['o'][str(m['clause_id'])]; i = int(m['sequence_index'])
        fields = {v: sorted(f for f in m['family_ids'] if d['f'][f]['family_type'] == k) for k, v in TYPE_FIELDS.items()}
        out.append(dict(marker_id=mid, anchor=m['anchor'], clause_id=m['clause_id'], clause_atom_ids=m['clause_atom_ids'], reference=ref(c), surface=c['surface_hebrew'], discovery_sources=m['discovery_sources'],
            all_family_ids=sorted(m['family_ids']), all_bundle_ids=sorted(by_marker[mid]), **fields,
            repeat_evidence=dict(slot_repeat_count=int(m['repeat_count']), family_occurrences={f:int(d['f'][f]['occurrence_count']) for f in m['family_ids']}),
            explicit_construction_evidence=m['formal_explicitness'], base_construction=m['base_construction'], adjunct_variants=features(m),
            raw_signature_views=d['signature_views'][str(m['clause_id'])],
            context_before=[dict(clause_id=x['clause_id'], reference=ref(x), surface=x['surface_hebrew']) for x in d['observation'][max(0,i-2):i]],
            context_after=[dict(clause_id=x['clause_id'], reference=ref(x), surface=x['surface_hebrew']) for x in d['observation'][i+1:i+3]],
            force_evidence_link=mid, force_evidence=d['h'][mid], coverage_candidate_links=[r['coverage_candidate_id'] for r in d['by_coverage'][mid]],
            nested_evidence_links=[r['nested_evidence_id'] for r in d['by_nested'][mid]], relation_candidate_links=sorted(d['by_relation'][mid]),
            participant_identity='UNRESOLVED', automatic_resolution=False))
    return out

def review_universe(bundles, cases, expansions):
    relation_members = set()
    for r in cases:
        if set(r['raw_labels']) & {'PARATAXIS_CANDIDATE','HYPOTAXIS_CANDIDATE','EMBEDDING_CANDIDATE','RESUMPTION_CANDIDATE','TEMPORAL_RESUMPTION_CANDIDATE','CLOSURE_TARGET_CANDIDATE'}:
            relation_members.update((r['source_marker_id'], r['target_marker_id']))
    expanded = {r[k] for r in expansions for k in ('expansion_source_bundle','expansion_target_bundle')}
    review = []; archive = []
    for b in bundles:
        reasons = [c for c in b['categories'] if c in ('REPEATED_OCCURRENCE_BUNDLE','SINGLETON_EXPLICIT_BUNDLE')]
        if relation_members & set(b['marker_ids']): reasons.append('PARTICIPATES_IN_RAW_RELATION_CANDIDATE')
        if b['bundle_id'] in expanded: reasons.append('OBSERVED_EXPANSION_MEMBER')
        row = dict(bundle_id=b['bundle_id'], marker_ids=b['marker_ids'], raw_family_ids=b['contributing_family_ids'], categories=b['categories'], inclusion_evidence=reasons,
                   disposition='DEFAULT_REVIEW' if reasons else 'ARCHIVE_FOR_REFERENCE', automatic_resolution=False,
                   limitation='ARCHIVE_DOES_NOT_MEAN_INVALID; REVIEW_IS_NOT_ACCEPTANCE')
        (review if reasons else archive).append(row)
    return review, archive
