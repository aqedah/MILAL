"""Consolidation depends only on frozen blind evidence."""
from collections import defaultdict,Counter
from milal_mfr01a_bundle import bundle,profiles,review_universe
from milal_mfr01a_lattice import lattice,expansions
from milal_mfr01a_relation import consolidate
from milal_mfr01a_data import summary_raw

def build(d,prefix='M'):
    bb,bm,aa,by_marker=bundle(d,prefix+'EB')
    ll=lattice(d,bb,by_marker);ee=expansions(d,by_marker);pp=profiles(d,by_marker)
    rr,cross,closures,review,archive=consolidate(d,by_marker,prefix+'RC')
    fr,fa=review_universe(bb,rr,ee)
    case_by_raw={r['raw_relation_candidate_id']:r['case_id'] for r in cross}
    trace=[]
    def add(kind,ident,bids=None,mids=None,cids=None):
        trace.append(dict(raw_kind=kind,raw_id=ident,bundle_ids=sorted(set(bids or [])),marker_profile_ids=sorted(set(mids or [])),relation_case_ids=sorted(set(cids or []))))
    for b in bb:
        for fid in b['contributing_family_ids']:add('family',fid,[b['bundle_id']],b['marker_ids'])
    for mid,m in sorted(d['m'].items()):
        cases=sorted({case_by_raw[r] for r in d['by_relation'][mid]})
        add('marker',mid,by_marker[mid],[mid],cases);add('force',mid,by_marker[mid],[mid],cases)
    for r in d['membership']:add('membership',r['family_id']+'|'+r['marker_id'],by_marker[r['marker_id']],[r['marker_id']])
    for r in d['relations']:add('relation',r['relation_candidate_id'],by_marker[r['source_marker_id']]+by_marker[r['target_marker_id']],[r['source_marker_id'],r['target_marker_id']],[case_by_raw[r['relation_candidate_id']]])
    for kind,rows,field in [('coverage',d['coverage'],'coverage_candidate_id'),('nested',d['nested'],'nested_evidence_id')]:
        for r in rows:add(kind,r[field],by_marker[r['marker_id']],[r['marker_id']])
    out=dict(audit=aa,bundles=bb,membership=bm,lattice=ll,expansion=ee,profiles=pp,family_review=fr,family_archive=fa,crosswalk=cross,cases=rr,closures=closures,
        closure_review=[r for r in closures if r['review_eligible']],closure_archive=[r for r in closures if not r['review_eligible']],relation_review=review,relation_archive=archive,trace=trace)
    return out

def statistics(d,out):
    return dict(raw=summary_raw(d),outputs={k:len(v) for k,v in out.items()},
        family_types=dict(Counter(f['family_type'] for f in d['families'])),family_occurrence_distribution=dict(Counter(str(f['occurrence_count']) for f in d['families'])),
        family_singleton_count=sum(int(f['occurrence_count'])==1 for f in d['families']),family_repeated_count=sum(int(f['occurrence_count'])>=2 for f in d['families']),
        bundle_categories=dict(Counter(c for b in out['bundles'] for c in b['categories'])),families_per_bundle=dict(Counter(str(len(b['contributing_family_ids'])) for b in out['bundles'])),
        duplicate_set_bundle_count=sum(len(b['contributing_family_ids'])>1 for b in out['bundles']),families_in_multi_family_bundles=sum(len(b['contributing_family_ids']) for b in out['bundles'] if len(b['contributing_family_ids'])>1),
        relation_buckets=dict(Counter(b for r in out['cases'] for b in r['buckets'])),closure_status=dict(Counter(s for r in out['closures'] for s in r['closure_status'])),
        explicit_cessation_markers=sum('EXPLICIT_CESSATION' in m['discovery_sources'] for m in d['markers']),
        archived_formal_only=sum('REL_D_FORMAL_CORRESPONDENCE' in r['buckets'] for r in out['relation_archive']),
        archived_weak_closure=sum('REL_E_WEAK_CLOSURE_ARCHIVE' in r['buckets'] for r in out['relation_archive']),
        cross_book_raw=sum(bool(r['cross_book']) for r in d['relations']),cross_book_cases=sum(r['cross_book'] for r in out['cases']))
