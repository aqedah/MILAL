"""Alternative coverage and lossless factored nested marker intervals."""
from bisect import bisect_left,bisect_right
from collections import defaultdict

def coverage(markers,obs,families,prefix):
    indices=[m['sequence_index'] for m in markers];family={r['family_id']:r for r in families}
    # Build indexes without a family x marker scan.
    member_indices=defaultdict(list)
    for m in markers:
        for f in m['family_ids']:member_indices[f].append(m['marker_index'])
    closures=[m['marker_index'] for m in markers if 'EXPLICIT_CESSATION' in m['discovery_sources']]
    breaks=[i for i in range(1,len(obs)) if obs[i]['domain']!=obs[i-1]['domain'] and obs[i]['domain'] not in (None,'','?') and obs[i-1]['domain'] not in (None,'','?')]
    rows=[];nested=[];familybits={f:1<<i for i,f in enumerate(family)};size=1
    while size<len(markers):size*=2
    tree=[0]*(size*2)
    for i,m in enumerate(markers):tree[size+i]=sum(familybits[f] for f in m['family_ids'])
    for i in range(size-1,0,-1):tree[i]=tree[i*2]|tree[i*2+1]
    def unique_count(a,b):
        value=0;a+=size;b+=size
        while a<b:
            if a&1:value|=tree[a];a+=1
            if b&1:b-=1;value|=tree[b]
            a//=2;b//=2
        return value.bit_count()
    wordprefix=[0]
    for c in obs:wordprefix.append(wordprefix[-1]+len(c['word_ids']))
    for m in markers:
        ends=defaultdict(list);mi=m['marker_index'];start=m['sequence_index']
        for f in m['family_ids']:
            typ=family[f]['family_type']
            if typ not in ('EXACT_FORM_FAMILY','CONSTRUCTION_FAMILY','ADJUNCT_EXPANSION_FAMILY'):continue
            ii=member_indices[f];pos=bisect_right(ii,mi)
            if pos<len(ii):ends[(max(start,indices[ii[pos]]-1),'NEXT_'+typ)].append(f)
        pos=bisect_right(closures,mi)
        if pos<len(closures):ends[(indices[closures[pos]],'EXPLICIT_CLOSURE')].append(markers[closures[pos]]['marker_id'])
        pos=bisect_right(breaks,start)
        if pos<len(breaks):ends[(breaks[pos]-1,'DOMAIN_CONFIGURATION_BREAK')]=[]
        ends[(len(obs)-1,'ANALYSIS_SCOPE_END')]=[]
        for (end,basis),evidence in sorted(ends.items()):
            ident=prefix+'C'+str(len(rows)+1).zfill(7);a=bisect_right(indices,start);b=bisect_right(indices,end)
            rows.append(dict(coverage_candidate_id=ident,marker_id=m['marker_id'],start_anchor=obs[start]['anchor'],candidate_end_anchor=obs[end]['clause_atom_ids'][-1],start_index=start,end_index=end,end_basis=basis,end_evidence=evidence,word_count=wordprefix[end+1]-wordprefix[start],clause_count=end-start+1,nested_marker_count=b-a,nested_family_count=unique_count(a,b),automatic_resolution=False,scope_external_status='OUTSIDE_SCOPE_NOT_TESTED',limitations='OBSERVED_INTERVAL_NOT_ACCEPTED_UNIT; SCOPE_END_NOT_TEXTUAL_END'))
            nested.append(dict(nested_evidence_id=prefix+'N'+str(len(nested)+1).zfill(7),coverage_candidate_id=ident,marker_id=m['marker_id'],nested_marker_index_start=a,nested_marker_index_end_exclusive=b,nested_marker_count=b-a,nested_family_count=unique_count(a,b),membership_basis='ALL_MARKER_ROWS_IN_HALF_OPEN_INDEX_RANGE_AND_THEIR_FAMILY_MEMBERSHIPS',relation_semantics='OBSERVED_SPAN_EVIDENCE_ONLY'))
    return rows,nested
