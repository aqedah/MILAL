"""Computational provenance families, with shared-root dependency components."""
from collections import defaultdict
from milal_mfr01b_data import require, ACCEPTABLE_CESSATION

def components(records):
    groups=[]
    for r in sorted(records,key=lambda r:r['evidence_id']):
        roots=set(r['dependency_root_ids']);ids={r['evidence_id']};remaining=[]
        for group in groups:
            if roots & group[0]:roots |= group[0];ids |= group[1]
            else:remaining.append(group)
        # Merging can join an earlier, initially disjoint component transitively.
        changed=True
        while changed:
            changed=False;rest=[]
            for group in remaining:
                if roots & group[0]:roots |= group[0];ids |= group[1];changed=True
                else:rest.append(group)
            remaining=rest
        groups=remaining+[(roots,ids)]
    return [dict(dependency_root_ids=sorted(roots),evidence_ids=sorted(ids)) for roots,ids in sorted(groups,key=lambda x:sorted(x[1]))]

def audit(d,role_output,rules):
    roles={r['marker_id']:r for r in role_output['roles']};cess={r['marker_id']:r for r in role_output['cessations']}
    evidence=[];edges=[];closures=[]
    for r in sorted(d['relations'],key=lambda x:x['relation_candidate_id']):
        rid=r['relation_candidate_id'];s,t=d['m'][r['source_marker_id']],d['m'][r['target_marker_id']];sid,tid=s['marker_id'],t['marker_id']
        records=[];shared=set(s['family_ids'])&set(t['family_ids'])
        def add(kind,token,upstream,roots,details,usable=False,facet='',parents=()):
            eid=rid+':'+token;rootids=sorted(set(roots));require(bool(rootids),'provenance root absent')
            row=dict(evidence_id=eid,raw_relation_id=rid,provenance_family=kind,evidence_facet=facet,upstream_evidence_ids=sorted(set(upstream)),
                dependency_root_ids=rootids,parent_evidence_ids=list(parents),cessation_derived=any(x.startswith('CESSATION:') for x in rootids),
                independent_link_usable=bool(usable) and not any(x.startswith('CESSATION:') for x in rootids),details=details)
            records.append(row)
            for p in parents:edges.append(dict(raw_relation_id=rid,node_id=eid,parent_id=p,edge_type='DERIVED_FROM_EVIDENCE'))
            for root in rootids:edges.append(dict(raw_relation_id=rid,node_id=eid,parent_id=root,edge_type='DEPENDENCY_ROOT'))
            for raw in row['upstream_evidence_ids']:edges.append(dict(raw_relation_id=rid,node_id=eid,parent_id=raw,edge_type='FROZEN_SOURCE'))
            return row
        target_identity=None
        if tid in cess:
            target_identity=add('EVID_CESSATION_TARGET_IDENTITY','TARGET',['MARKER:'+tid],['CESSATION:'+tid],dict(role=cess[tid]['role_candidate']))
        onset=set(roles[sid]['formal_role_sources'])&set(rules['onset_sources'])
        if onset:
            onset_roots=[]
            for tag,typ in [('REPEATED_CLAUSE_FORMULA','SLOT_NORMALIZED_FAMILY'),('REPEATED_SEQUENCE_CONFIGURATION','MULTI_CLAUSE_CONFIGURATION_FAMILY')]:
                if tag in onset:onset_roots+=['FAMILY:'+f for f in s['family_ids'] if d['f'][f]['family_type']==typ]
            if onset-{'REPEATED_CLAUSE_FORMULA','REPEATED_SEQUENCE_CONFIGURATION'}:onset_roots.append('FORM:'+sid)
            add('EVID_DIRECT_FORMAL','ONSET',['MARKER:'+sid,'OBS:'+str(s['clause_id'])],onset_roots,dict(triggers=sorted(onset)),True,'ONSET')
        formal_families=sorted(f for f in shared if d['f'][f]['family_type'] in ('EXACT_FORM_FAMILY','SLOT_NORMALIZED_FAMILY','CONSTRUCTION_FAMILY','ADJUNCT_EXPANSION_FAMILY','PARTIAL_FORMAL_FAMILY'))
        if formal_families or r['exact_form_correspondence'] or r['construction_correspondence']:
            predicates=bool(set(s['base_construction']['predicates'])&set(t['base_construction']['predicates']))
            specific=bool(r['exact_form_correspondence'] or s['signatures']['SIG_LEXICAL_SLOT']==t['signatures']['SIG_LEXICAL_SLOT'] or predicates)
            roots=['FAMILY:'+f for f in formal_families] or ['FORM:'+sid,'FORM:'+tid]
            add('EVID_DIRECT_FORMAL','FORMAL',['RELATION:'+rid,*('FAMILY:'+f for f in formal_families)],roots,
                dict(family_ids=formal_families,exact=r['exact_form_correspondence'],construction=r['construction_correspondence'],predicate_supported=predicates,generic_order_only=not specific),specific,'CORRESPONDENCE')
        sequence=sorted(f for f in shared if d['f'][f]['family_type']=='MULTI_CLAUSE_CONFIGURATION_FAMILY' and int(d['f'][f]['occurrence_count'])>=2)
        if sequence:add('EVID_SEQUENCE_CONFIGURATION','SEQUENCE',['FAMILY:'+f for f in sequence],['FAMILY:'+f for f in sequence],dict(family_ids=sequence),True)
        if r['context_before_correspondence'] or r['context_after_correspondence']:
            add('EVID_CONTEXTUAL','CONTEXT',['FORCE:'+sid,'FORCE:'+tid],['CONTEXT:'+sid,'CONTEXT:'+tid],dict(before=r['context_before_correspondence'],after=r['context_after_correspondence']),True)
        if r['participant_correspondence']:
            add('EVID_PARTICIPANT','PARTICIPANT',['OBS:'+str(s['clause_id']),'OBS:'+str(t['clause_id'])],['PARTICIPANT:'+sid,'PARTICIPANT:'+tid],dict(surface=r['participant_correspondence'],identity='UNRESOLVED'),True)
        if r['domain_correspondence']:
            add('EVID_DOMAIN','DOMAIN',['OBS:'+str(s['clause_id']),'OBS:'+str(t['clause_id'])],['DOMAIN:'+sid,'DOMAIN:'+tid],dict(source_domain=d['o'][str(s['clause_id'])]['domain'],target_domain=d['o'][str(t['clause_id'])]['domain']),True)
        flags=r['resumption_evidence'];roots=[]
        lexical_participant=bool(r['participant_correspondence']) and bool(set(s['base_construction']['predicates'])&set(t['base_construction']['predicates'])) and int(t['sequence_index'])-int(s['sequence_index'])>1
        if flags['lexical_participant'] and lexical_participant:roots+=['PARTICIPANT:'+sid,'PARTICIPANT:'+tid,'FORM:'+sid,'FORM:'+tid]
        if flags['temporal_context_recurrence']:roots+=['CONTEXT:'+sid,'CONTEXT:'+tid]
        if flags['death_temporal']:roots+=['DEATH_FORM:'+sid,'TEMPORAL_FORM:'+tid]
        require(not flags['lexical_participant'] or roots,'SCHEMA unexplained frozen resumption flag')
        if roots:add('EVID_RESUMPTION','RESUMPTION',['RELATION:'+rid,'MARKER:'+sid,'MARKER:'+tid],roots,flags,True)
        for cid in sorted(r['coverage_relationship']):
            c=d['c'][cid];basis=c['end_basis'];roots=[];parents=[]
            endpoint=int(c['end_index'])==int(t['sequence_index']) and str(c['candidate_end_anchor']) in {str(a) for a in t['clause_atom_ids']}
            if basis=='EXPLICIT_CLOSURE':
                require(bool(c['end_evidence']) and all(mid in cess for mid in c['end_evidence']),'SCHEMA cessation coverage target identity')
                roots=['CESSATION:'+mid for mid in c['end_evidence']];kind='EVID_COVERAGE_CESSATION_DERIVED'
                if tid in c['end_evidence']:parents=[target_identity['evidence_id']]
            elif basis.startswith('NEXT_'):
                require(bool(c['end_evidence']) and all(fid in d['f'] for fid in c['end_evidence']),'SCHEMA family coverage provenance')
                roots=['FAMILY:'+fid for fid in c['end_evidence']];kind='EVID_COVERAGE_INDEPENDENT'
            elif basis=='DOMAIN_CONFIGURATION_BREAK':
                ni=int(c['end_index'])+1;require(ni<len(d['observation']),'SCHEMA domain boundary outside input')
                roots=['DOMAIN_BOUNDARY:'+str(d['observation'][ni]['clause_id'])];kind='EVID_COVERAGE_INDEPENDENT'
            elif basis=='ANALYSIS_SCOPE_END':roots=['SCOPE_LIMIT'];kind='EVID_SCOPE_LIMIT'
            else:raise ValueError('SCHEMA unknown coverage end basis '+basis)
            ce=add(kind,'COVERAGE:'+cid,['COVERAGE:'+cid],roots,dict(end_basis=basis,end_evidence=c['end_evidence'],ends_at_target=endpoint,endpoint=c['candidate_end_anchor']),endpoint and kind=='EVID_COVERAGE_INDEPENDENT',parents=parents)
            for n in d['by_nested'][cid]:
                add('EVID_NESTED_FROM_COVERAGE','NESTED:'+n['nested_evidence_id'],['NESTED:'+n['nested_evidence_id'],'COVERAGE:'+cid],roots,
                    dict(coverage_candidate_id=cid,terminal_target=int(n['nested_marker_index_end_exclusive'])-1==int(t['marker_index'])),False,parents=[ce['evidence_id']])
        if not records:add('EVID_RAW_RELATION_REFERENCE','RAW',['RELATION:'+rid],['RELATION_RECORD:'+rid],dict(labels=r['relation_candidates']))
        evidence.extend(records)
        if 'CLOSURE_TARGET_CANDIDATE' not in r['relation_candidates']:continue
        independent=[e for e in records if e['independent_link_usable']];chains=components([e for e in records if e['cessation_derived']]);groups=components(independent)
        families=sorted({e['provenance_family'] for e in independent});statuses=[]
        if not independent:statuses.append('CLOSURE_CESSATION_DERIVED_ONLY')
        if any(e['evidence_facet']=='ONSET' for e in independent):statuses.append('CLOSURE_WITH_INDEPENDENT_ONSET_EVIDENCE')
        if any(e['evidence_facet']=='CORRESPONDENCE' for e in independent):statuses.append('CLOSURE_WITH_INDEPENDENT_FORMAL_EVIDENCE')
        for family,label in [('EVID_SEQUENCE_CONFIGURATION','SEQUENCE'),('EVID_CONTEXTUAL','CONTEXT'),('EVID_PARTICIPANT','CONTEXT'),('EVID_DOMAIN','CONTEXT'),('EVID_RESUMPTION','RESUMPTION'),('EVID_COVERAGE_INDEPENDENT','COVERAGE')]:
            if family in families:statuses.append('CLOSURE_WITH_INDEPENDENT_'+label+'_EVIDENCE')
        if len(groups)>1 and len(families)>1:statuses.append('CLOSURE_WITH_MULTIPLE_INDEPENDENT_EVIDENCE_FAMILIES')
        targetrole=cess[tid]['role_candidate']
        if targetrole=='CESSATION_ROLE_AMBIGUOUS':statuses.append('CLOSURE_ROLE_TARGET_AMBIGUOUS')
        source_primary=roles[sid]['primary_bearing']
        eligible=source_primary and targetrole in ACCEPTABLE_CESSATION and bool(independent)
        closures.append(dict(raw_relation_id=rid,prior_case_id=d['old_cross'][rid]['case_id'],source_marker_id=sid,target_marker_id=tid,target_role=targetrole,source_primary_bearing=source_primary,
            statuses=sorted(set(statuses)),evidence_ids=[e['evidence_id'] for e in records],independent_evidence_ids=[e['evidence_id'] for e in independent],
            independent_evidence_families=families,independent_dependency_components=groups,cessation_derived_chains=chains,
            chain_semantics='ONE_CESSATION_DERIVED_CHAIN_PER_SHARED_ROOT',review_eligible=eligible,
            archive_reasons=[] if eligible else (['SOURCE_SUPPORT_OR_LEXICAL_REFERENCE_ONLY'] if not source_primary else [])+(['TARGET_ROLE_REQUIRES_REFERENCE_ONLY'] if targetrole not in ACCEPTABLE_CESSATION else [])+(['NO_INDEPENDENT_LINK'] if not independent else []),
            accepted_closure='',limitations='REVIEW_ELIGIBILITY_ONLY; ENDPOINT_DOMAIN_OR_SURFACE_MATCH_NOT_CLOSURE_ACCEPTANCE'))
    return evidence,edges,closures
