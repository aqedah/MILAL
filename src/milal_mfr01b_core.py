"""Role/provenance overlays and phase dependencies; frozen rows never rewritten."""
from collections import Counter
from milal_mfr01b_roles import audit as role_audit
from milal_mfr01b_evidence import audit as evidence_audit
from milal_mfr01b_configuration import build as configurations

def build(d,rules):
    out=role_audit(d,rules)
    if 'relations' not in d:return out
    evidence,edges,closures=evidence_audit(d,out,rules);configs,members=configurations(d,closures)
    out.update(evidence=evidence,edges=edges,closures=closures,closure_review=[c for c in closures if c['review_eligible']],closure_archive=[c for c in closures if not c['review_eligible']],configurations=configs,membership=members)
    for kind,field in [('h1','hierarchy_pair_ids'),('r1','resumption_pair_ids'),('c1','closure_review_pair_ids')]:
        rows=[]
        for c in configs:
            if not c[field]:continue
            pairs=c[field];mids=sorted({d['r'][rid][side+'_marker_id'] for rid in pairs for side in ('source','target')})
            # Phase dependencies cover the full configuration's pair evidence.
            rows.append(dict(phase=kind.upper(),configuration_case_id=c['configuration_case_id'],phase_pair_ids=pairs,all_configuration_pair_ids=c['raw_pair_ids'],
                marker_ids=c['marker_ids'],bundle_ids=c['bundle_ids'],context_marker_ids=sorted(set(c['marker_ids'])-set(mids)),decision=''))
        out[kind]=rows
    active={c['configuration_case_id'] for kind in ('h1','r1','c1') for c in out[kind]};needed={b for kind in ('h1','r1','c1') for c in out[kind] for b in c['bundle_ids']}
    roles={r['marker_id']:r for r in out['roles']};expanded={e[k] for e in d['expansions'] for k in ('expansion_source_bundle','expansion_target_bundle')};fam=[]
    for b in out['bundles']:
        old=d['b'][b['bundle_id']];mids=b['marker_ids'];primary=b['primary_marker_ids'];cats=[]
        informative=any(f['family_type'] in ('EXACT_FORM_FAMILY','SLOT_NORMALIZED_FAMILY','MULTI_CLAUSE_CONFIGURATION_FAMILY') and int(f['occurrence_count'])>=2 for f in old['family_evidence'])
        if primary and len(mids)>=2 and informative:cats.append('FAM_A_PRIMARY_REPEATED')
        if len(mids)==1 and primary and set(roles[mids[0]]['formal_role_sources'])-{'REPEATED_CLAUSE_FORMULA','REPEATED_SEQUENCE_CONFIGURATION'}:cats.append('FAM_B_PRIMARY_SINGLETON_EXPLICIT')
        if primary and b['bundle_id'] in expanded:cats.append('FAM_C_EXPANSION_COMPLEX')
        if b['bundle_id'] in needed:cats.append('FAM_D_RELATION_DEPENDENCY')
        if b['bundle_role']=='SUPPORT_ONLY_BUNDLE':cats.append('FAM_E_SUPPORT_ONLY_REFERENCE')
        if not cats or not primary:cats.append('FAM_F_GENERIC_CONSTRUCTION_REFERENCE')
        default=bool(set(cats)&{'FAM_A_PRIMARY_REPEATED','FAM_B_PRIMARY_SINGLETON_EXPLICIT','FAM_C_EXPANSION_COMPLEX','FAM_D_RELATION_DEPENDENCY'})
        fam.append(dict(bundle_id=b['bundle_id'],marker_ids=mids,raw_family_ids=b['raw_family_ids'],categories=cats,default_review=default,standalone_formal_review=bool(primary and default),
            disposition='PHASE_DEPENDENCY_OR_FORMAL_REVIEW' if default else 'FORMAL_PATTERN_REFERENCE',accepted_family=''))
    out['family_review']=fam;references=[]
    for c in configs:
        if c['configuration_case_id'] not in active:references.append(dict(reference_id='CONFIG:'+c['configuration_case_id'],kind='RELATION_REFERENCE',marker_ids=c['marker_ids'],bundle_ids=c['bundle_ids'],raw_pair_ids=c['raw_pair_ids']))
    for b in fam:
        if not b['standalone_formal_review']:references.append(dict(reference_id='BUNDLE:'+b['bundle_id'],kind='FORMAL_OR_SUPPORT_REFERENCE',marker_ids=b['marker_ids'],bundle_ids=[b['bundle_id']],raw_pair_ids=[]))
    out['reference']=references
    return out

def statistics(d,o):
    roles=Counter(r['role'] for r in o['roles']);result=dict(markers=len(d['markers']),raw_families=len(d['families']),bundles=len(d['old_bundles']),marker_roles=dict(roles),
        primary_bearing=sum(r['primary_bearing'] for r in o['roles']),support_source_combinations=dict(Counter('+'.join(r['support_sources']) for r in o['roles'] if r['role']=='SUPPORT_SIGNAL_ONLY')),
        bundle_roles=dict(Counter(r['bundle_role'] for r in o['bundles'])),primary_bearing_bundles=sum(bool(r['primary_marker_ids']) for r in o['bundles']),
        cessation_roles=dict(Counter(r['role_candidate'] for r in o['cessations'])))
    if 'relations' not in d:return result
    result.update(raw_relations=len(d['relations']),raw_memberships=len(d['membership']),raw_coverage=len(d['coverage']),old_family_review=len(d['old_family_review']),old_relation_review=len(d['old_relation_review']),
        old_relation_bucket_combinations=dict(Counter('+'.join(d['old_case'][r['case_id']]['buckets']) for r in d['old_relation_review'])),
        closures=len(o['closures']),closure_review=len(o['closure_review']),closure_archive=len(o['closure_archive']),closure_statuses=dict(Counter(s for c in o['closures'] for s in c['statuses'])),
        hierarchy_pairs=sum(len(c['hierarchy_pair_ids']) for c in o['configurations']),hierarchy_configuration_cases=len(o['h1']),configuration_cases=len(o['configurations']),
        hierarchy_markers=len({m for c in o['h1'] for m in c['marker_ids']}),hierarchy_bundles=len({b for c in o['h1'] for b in c['bundle_ids']}),
        phases={k:len(o[k]) for k in ('h1','r1','c1','reference')},family_default=sum(r['default_review'] for r in o['family_review']),family_reference=sum(not r['default_review'] for r in o['family_review']),
        family_categories=dict(Counter(c for r in o['family_review'] for c in r['categories'])),
        raw_loss=len(set(d['m'])-{r['marker_id'] for r in o['roles']})+len(set(d['r'])-{r['raw_relation_id'] for r in o['membership']})+len(set(d['f'])-{f for b in o['bundles'] for f in b['raw_family_ids']}))
    return result
