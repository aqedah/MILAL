"""Indexed set relations and adjunct differences, without hierarchy claims."""
from collections import defaultdict
from itertools import combinations
from milal_mfr01a_data import js, features

def lattice(d, bundles, by_marker):
    bb = {b['bundle_id']: b for b in bundles}; sets = {k:set(v['marker_ids']) for k,v in bb.items()}
    pairs = set()
    for bids in by_marker.values(): pairs.update(combinations(sorted(bids), 2))
    result = []
    for b in bundles:
        if len(b['contributing_family_ids']) > 1:
            result.append(dict(bundle_a=b['bundle_id'], bundle_b=b['bundle_id'], set_relation='SAME_OCCURRENCE_SET', shared_markers=b['marker_ids'],
                construction_relation=['EXACT_OCCURRENCE_SET_MULTIPLE_FAMILY_VIEWS'], adjunct_difference={}, status='EVIDENCE_ONLY'))
    for a,b in sorted(pairs):
        aa,zz=sets[a],sets[b]
        relation='STRICT_SUBSET' if aa < zz else 'STRICT_SUPERSET' if aa > zz else 'PARTIAL_OVERLAP'
        result.append(dict(bundle_a=a,bundle_b=b,set_relation=relation,shared_markers=sorted(aa&zz),construction_relation=['SHARED_MARKER_OCCURRENCE'],
            adjunct_difference=dict(source=sorted({js(features(d['m'][x])).decode().strip() for x in aa}),target=sorted({js(features(d['m'][x])).decode().strip() for x in zz})),status='EVIDENCE_ONLY'))
    return result

def expansions(d, by_marker):
    # The base-construction inverted index is linguistic, never reference-based.
    cores=defaultdict(lambda:defaultdict(set));definitions={}
    for mid,m in d['m'].items():
        if not m['base_construction']['predicates']: continue
        core=js(m['base_construction']).decode().strip();definitions[core]=m['base_construction']
        variant=js(features(m)).decode().strip()
        for bid in by_marker[mid]:cores[core][bid].add(variant)
    result=[]
    for core,groups in sorted(cores.items()):
        for a,b in combinations(sorted(groups),2):
            av,bv=groups[a],groups[b]
            if av==bv:continue
            result.append(dict(expansion_id='MEX'+str(len(result)+1).zfill(8),expansion_source_bundle=a,expansion_target_bundle=b,
                added_features=sorted(bv-av),removed_features=sorted(av-bv),shared_core=definitions[core],source_variants=sorted(av),target_variants=sorted(bv),
                status='EVIDENCE_ONLY',direction_semantics='DETERMINISTIC_ID_ORDER_NOT_HIERARCHY',limitations='RAW_TIME_LOCA_VARIANTS; NO_ELABORATION_LEVEL_RULE'))
    return result
