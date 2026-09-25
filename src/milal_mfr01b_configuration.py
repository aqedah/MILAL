"""Configuration review groups require explicit repeated-sequence witnesses."""
from collections import defaultdict
from itertools import combinations
from milal_mfr01b_data import require, HIERARCHY

def sequence_witnesses(d):
    covering=defaultdict(list);by_marker=d['m']
    for f in d['families']:
        if f['family_type']!='MULTI_CLAUSE_CONFIGURATION_FAMILY' or int(f['occurrence_count'])<2:continue
        res=f['signature_resolution'];require(res.startswith('SIG_SEQUENCE_'),'SCHEMA sequence resolution')
        length=int(res.rsplit('_',1)[1]);require(length>=2,'SCHEMA sequence length')
        for mid in f['marker_ids']:
            start=int(by_marker[mid]['sequence_index']);end=start+length-1
            if end>=len(d['observation']):continue
            for position in range(start,end+1):covering[position].append((f['family_id'],mid,start,end))
    result={}
    for r in d['relations']:
        s,t=d['m'][r['source_marker_id']],d['m'][r['target_marker_id']];found=[]
        for a in covering[int(s['sequence_index'])]:
            for b in covering[int(t['sequence_index'])]:
                if a[0]==b[0] and a[1]!=b[1] and a[2]<b[2]:
                    found.append(dict(family_id=a[0],source_occurrence_marker=a[1],target_occurrence_marker=b[1],source_start=a[2],source_end=a[3],target_start=b[2],target_end=b[3]))
        result[r['relation_candidate_id']]=sorted(found,key=lambda x:(x['family_id'],x['source_occurrence_marker'],x['target_occurrence_marker']))
    return result

def build(d,closures):
    rr=d['r'];witnesses=sequence_witnesses(d);parent={rid:rid for rid in rr};buckets=defaultdict(list)
    def find(x):
        while parent[x]!=x:parent[x]=parent[parent[x]];x=parent[x]
        return x
    def union(a,b):
        aa,bb=sorted((find(a),find(b)));parent[bb]=aa
    for rid,ws in witnesses.items():
        labels=set(rr[rid]['relation_candidates']);h=sorted(labels&HIERARCHY)
        if not h and 'RESUMPTION_CANDIDATE' not in labels:continue
        # Group by repeated occurrence pair; candidate labels are retained, never selected.
        for w in ws:buckets[(w['family_id'],w['source_occurrence_marker'],w['target_occurrence_marker'],bool(h))].append(rid)
    pair_edges=[]
    for key,ids in sorted(buckets.items()):
        for a,b in combinations(sorted(set(ids)),2):
            ra,rb=rr[a],rr[b]
            def adjacent(side):
                x,y=d['m'][ra[side+'_marker_id']],d['m'][rb[side+'_marker_id']]
                return abs(int(x['sequence_index'])-int(y['sequence_index']))<=1 or bool(set(x['clause_atom_ids'])&set(y['clause_atom_ids']))
            if adjacent('source') and adjacent('target'):
                union(a,b);pair_edges.append(dict(pair_a=a,pair_b=b,sequence_family=key[0],source_occurrence=key[1],target_occurrence=key[2]))
    groups=defaultdict(list)
    for rid in sorted(rr):groups[find(rid)].append(rid)
    closure={r['raw_relation_id']:r for r in closures};cases=[];membership=[]
    for number,ids in enumerate(sorted(groups.values(),key=lambda x:tuple(x)),1):
        cid='CFG'+str(number).zfill(6);raw=[rr[rid] for rid in ids]
        sources=sorted({r['source_marker_id'] for r in raw});targets=sorted({r['target_marker_id'] for r in raw});mids=sorted(set(sources+targets))
        ws={tuple(w.items()):w for rid in ids for w in witnesses[rid]};ws=sorted(ws.values(),key=lambda x:(x['family_id'],x['source_occurrence_marker'],x['target_occurrence_marker']))
        src_positions={int(d['m'][m]['sequence_index']) for m in sources};tar_positions={int(d['m'][m]['sequence_index']) for m in targets}
        for w in ws:src_positions.update(range(w['source_start'],w['source_end']+1));tar_positions.update(range(w['target_start'],w['target_end']+1))
        pair_markers=mids
        mids=sorted(set(mids)|{m['marker_id'] for m in d['markers'] if int(m['sequence_index']) in src_positions|tar_positions})
        h=[r['relation_candidate_id'] for r in raw if set(r['relation_candidates'])&HIERARCHY]
        res=[r['relation_candidate_id'] for r in raw if any(r['resumption_evidence'].get(k) is True for k in ('lexical_participant','temporal_context_recurrence','death_temporal')) and 'RESUMPTION_CANDIDATE' in r['relation_candidates']]
        cl=[rid for rid in ids if rid in closure and closure[rid]['review_eligible']]
        cases.append(dict(configuration_case_id=cid,raw_pair_ids=ids,prior_case_ids=sorted({d['old_cross'][rid]['case_id'] for rid in ids}),
            source_marker_ids=sources,target_marker_ids=targets,underlying_pair_marker_ids=pair_markers,marker_ids=mids,bundle_ids=sorted({b for m in mids for b in d['by_marker'][m]}),
            source_clause_ids=[d['observation'][i]['clause_id'] for i in sorted(src_positions)],target_clause_ids=[d['observation'][i]['clause_id'] for i in sorted(tar_positions)],
            source_span_indices=sorted(src_positions),target_span_indices=sorted(tar_positions),sequence_witnesses=ws,
            grouping_edges=[e for e in pair_edges if e['pair_a'] in ids and e['pair_b'] in ids],
            raw_candidate_labels=sorted({label for r in raw for label in r['relation_candidates']}),hierarchy_pair_ids=h,resumption_pair_ids=res,closure_review_pair_ids=cl,
            cross_book=any(r['cross_book'] for r in raw),automatic_resolution=False,limitations='CONNECTED_REVIEW_GROUP_NOT_ACCEPTED_UNIT; DISTINCT_RAW_CLAIMS_REMAIN_VISIBLE'))
        for rid in ids:membership.append(dict(configuration_case_id=cid,raw_relation_id=rid,prior_case_id=d['old_cross'][rid]['case_id'],source_marker_id=rr[rid]['source_marker_id'],target_marker_id=rr[rid]['target_marker_id'],raw_candidate_labels=rr[rid]['relation_candidates']))
    return cases,membership
