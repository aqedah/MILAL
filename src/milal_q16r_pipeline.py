"""Q1.6R read-only methodological classification of frozen evidence."""
import json
from collections import Counter,defaultdict
from milal_mfr02r_data import rows,table,digest,physical_path
from milal_q1_binding import MECHANISMS,identity
from milal_q13_model import AssignmentModel
from milal_q13_pipeline import write
from milal_q16r_roles import process_role,valency_case,readiness,mechanism_overlaps
from milal_q16r_provenance import Projection


def process(mid,kind,key,source,detail,**facts):
    ev=dict(process_kind=kind,**facts)
    return dict(process_id=key,mechanism_id=mid,process_kind=kind,primary_role=process_role(ev),source_artifact=source,detail=detail,role_basis=ev,distinct_positive_binding=False,new_relation=False)


def audit(source,q15,q16,out):
    inventory=list(rows(source/'blind/job/02_clause_feature_inventory.csv'));byclause={str(r['clause_id']):r for r in inventory};owners=defaultdict(set)
    for c,r in byclause.items():
        for atom in r['clause_atom_ids']:owners[str(atom)].add(c)
    forms={f['reference_witness_id']:f for f in rows(q15/'01_q15_reference_form_inventory.csv')}
    recs={r['reference_witness_id']:r for r in rows(q15/'09_q15_reference_witness_reclassification.csv')}
    domains={r['domain_id']:r for r in rows(q15/'02_q15_reference_visibility_domains.csv')}
    audits={m:[] for m in ('SB05','SB07','SB08','SB09','SB10')};ps=[]
    for r in rows(q16/'04_q16_sb05_valency_witnesses.csv'):
        d=r['detail'];b=d.get('frozen_candidate')
        if b:
            ev=b['binding_evidence'];case=valency_case(b['clause_atom_a'],b['clause_atom_b'],owners[str(b['clause_atom_a'])],owners[str(b['clause_atom_b'])],ev['raw_clause_membership'])
            if case['case_class']=='INTER_CLAUSAL_GOVERNANCE_ATTESTED':raise ValueError('STOP: unexpected explicit interclausal contract requires separate review')
            detail=dict(frozen_witness=r,case=case,native_constitution_already_represents_pair=case['same_native_clause'],valency_completion_flag='VALENCY_COMPLETION' in ev['reasons'],valency_governance='UNRESOLVED_NOT_PROVED_BY_MEMBERSHIP',bhsa_rewritten=False)
            p=process('SB05','ATOM_CONSTITUTION',r['witness_id'],'q16/04_q16_sb05_valency_witnesses.csv',detail,source_clause=next(iter(owners[str(b['clause_atom_a'])]),''),target_clause=next(iter(owners[str(b['clause_atom_b'])]),''))
        else:p=process('SB05','NATIVE_ALIAS',r['witness_id'],'q16/04_q16_sb05_valency_witnesses.csv',dict(frozen_witness=r,delegated_to=['SB01'],independent_SB05_binding=False))
        audits['SB05'].append(p);ps.append(p)
    for mid,num,param,role in [('SB07','05','TIME_PARAMETER','Time'),('SB08','06','LOCATION_PARAMETER','Loca')]:
        name=f'{num}_q16_{mid.lower()}_'+('temporal' if mid=='SB07' else 'locative')+'_witnesses.csv'
        for r in rows(q16/name):
            kind='FRAME_CORRESPONDENCE' if r['polarity']=='SUPPORT_ONLY' else param
            p=process(mid,kind,r['witness_id'],'q16/'+name,dict(frozen_witness=r,native_function=role,delegated_to=['SB06','SB11'] if kind=='FRAME_CORRESPONDENCE' else [],structural_signal=True,pair_specific_reference_binder=False))
            audits[mid].append(p);ps.append(p)
        for f in forms.values():
            c=str(f['target_clause_id']);node=int(f['word_node'])
            phrase=[p for p in byclause[c]['PHRASE'] if node in p['word_ids'] and p['function']==role]
            if not phrase or not f['reference_bearing']:continue
            kind='TEMPORAL_REFERENCE_FORM' if mid=='SB07' else 'LOCATIVE_REFERENCE_FORM'
            p=process(mid,kind,mid+'-'+f['reference_witness_id'],'q15/01_q15_reference_form_inventory.csv',dict(form=f,classification=recs[f['reference_witness_id']],native_phrases=phrase,delegated_to=['SB02','SB03'],explicit_surface_reference=f['reference_form_type']!='IMPLICIT_SUBJECT_OR_ARGUMENT',frame_referent_identity='UNRESOLVED',verified_frame_anaphora=False,qualification_duplicated=False))
            audits[mid].append(p);ps.append(p)
    for r in rows(q16/'07_q16_sb09_domain_witnesses.csv'):
        d=r['detail'];did=d.get('domain_id');native=did and domains[did]['domain_type']=='EXPLICIT_SUBORDINATION_DOMAIN'
        p=process('SB09','EXPLICIT_NATIVE_DOMAIN' if native else 'DERIVED_DOMAIN',r['witness_id'],'q16/07_q16_sb09_domain_witnesses.csv',dict(frozen_witness=r,delegated_to=['SB01'] if native else ['SB02','SB03','SB06','SB11'],distinct_explicit_domain_binding=False,domain_is_extra_independent_reason=False))
        audits['SB09'].append(p);ps.append(p)
    for rid,f in forms.items():
        rr=recs[rid];kind='LEXICAL_REPETITION' if rr['lexical_repetition_status']=='LEXICAL_REPETITION' else 'EXPLICIT_DEICTIC' if f['reference_form_type']=='DEICTIC_PRONOUN_OR_DETERMINER' else 'REFERENCE_FORM' if f['reference_bearing'] else 'LEXICAL_FORM_OBSERVATION'
        # Nonrepeated lexical mentions are retained with observed_repetition=False.
        p=process('SB10',kind,'LEX-'+rid,'q15/reference_inventory_and_reclassification',dict(form=f,classification=rr,observed_repetition=rr['lexical_repetition_status']=='LEXICAL_REPETITION',lexical_semantic_interpretation=False,marked_lexical_anaphora=False,delegated_to=['SB02','SB03'] if f['reference_bearing'] else [],referential_identity_created=False),verified_pair_path=f['reference_bearing'])
        audits['SB10'].append(p);ps.append(p)
    proj=Projection(q16,inventory)
    for n in proj.nodes.values():
        w=n['payload'].get('frozen_witness')
        if not w:continue
        m=w['mechanism'];kind={'SB01':'NATIVE_DEPENDENCY','SB02':'EXPLICIT_REFERENCE','SB03':'EXPLICIT_REFERENCE','SB04':'PARTICIPANT_CONTINUATION','SB06':'QUALIFIED_CONFIGURATION','SB11':'QUALIFIED_CONFIGURATION'}[m]
        p=process(m,kind,w['witness_id'],'q16/02_q16_evidence_dependency_graph.csv',dict(witness=w),verified_pair_path=True,dependent_on=w['dependent_on']);p['distinct_positive_binding']=p['primary_role']=='PRIMARY_SOURCE_BINDING';ps.append(p)
    contract=process('SB10','LEXICAL_SEMANTICS','CONTRACT-LEXICAL-SEMANTICS','researcher_contract_and_Walton_2.1.1.3',dict(empirical_cases=0,status='POST_RELATION_CONTRACT_ONLY',relation_generation_authorized=False))
    ps.append(contract)
    old=list(rows(q16/'14_q16_qualified_relation_universe.csv'));compat=AssignmentModel(old,sorted(byclause,key=lambda c:int(byclause[c]['position']))).analyze()
    ps.append(process('SB12','GLOBAL_COMPATIBILITY','CONTRACT-Q13','milal_q13_model',dict(outcome_ids=[o['structural_outcome_group_id'] for o in old],global_audit=compat['global_audit'],positive_binding=False)))
    overlaps=mechanism_overlaps(proj.bases)
    coverage={r['mechanism']:r for r in rows(q16/'21_q16_mechanism_coverage_matrix.csv')};registry=[]
    for mid,name in MECHANISMS.items():
        rr=[p for p in ps if p['mechanism_id']==mid];roles={p['primary_role'] for p in rr};own=[p for p in rr if not p['detail'].get('delegated_to')]
        ownroles={p['primary_role'] for p in own}
        if 'PRE_RELATION_STRUCTURE' in ownroles:primary='PRE_RELATION_STRUCTURE'
        elif 'GLOBAL_CONSTRAINT' in ownroles:primary='GLOBAL_CONSTRAINT'
        elif 'PRIMARY_SOURCE_BINDING' in ownroles:primary='PRIMARY_SOURCE_BINDING'
        elif 'POST_RELATION_VALIDATION' in ownroles and 'CORROBORATIVE_RELATION_EVIDENCE' in roles:primary='HYBRID_WITH_EXPLICIT_SUBTYPES'
        elif any(p['process_kind']=='DERIVED_DOMAIN' for p in rr):primary='REFERENCE_VISIBILITY_CONTEXT'
        elif 'CONFIGURATION_CONTEXT' in ownroles:primary='CONFIGURATION_CONTEXT'
        elif 'CORROBORATIVE_RELATION_EVIDENCE' in roles:primary='CORROBORATIVE_RELATION_EVIDENCE'
        else:primary='UNRESOLVED_ROLE'
        has_binding=any(p['distinct_positive_binding'] for p in rr)
        registry.append(dict(mechanism_id=mid,original_definition=name,current_implementation=coverage[mid]['implementation_module'],raw_evidence_source=sorted({p['source_artifact'] for p in rr}),primary_methodological_role=primary,secondary_roles=sorted(roles-{primary}),can_positive_bind_relation=has_binding,can_only_support=not has_binding and primary!='GLOBAL_CONSTRAINT',can_only_constrain=primary=='GLOBAL_CONSTRAINT',pre_relation_dependency=primary=='PRE_RELATION_STRUCTURE',post_relation_dependency='POST_RELATION_VALIDATION' in roles,overlap_with=sorted(overlaps.get(mid,set())|{m for p in rr for m in p['detail'].get('delegated_to',[])}),double_count_risk='DERIVED_CONTEXT_AND_DELEGATED_SUBTYPES_MUST_NOT_ADD_A_VOTE',current_Job_witness_status=coverage[mid],role_test_evidence_ids=[p['process_id'] for p in rr],remaining_gap='NO_DISTINCT_REQUIRED_PRIMARY_BINDER_DEMONSTRATED; UNRESOLVED_REFERENTS_REMAIN_EVIDENCE_LIMITATIONS',subtypes=sorted({p['process_kind'] for p in rr}),qualification_changes=0))
    comps=proj.compare(q16);shared=proj.shared(q16)
    frozen={n.name:digest(n) for n in q16.iterdir() if n.is_file()}
    missing_primary=[p['process_id'] for p in ps if p['detail'].get('case',{}).get('case_class')=='INTER_CLAUSAL_GOVERNANCE_ATTESTED']
    ambiguous=[p['process_id'] for p in ps if p['primary_role']=='UNRESOLVED_ROLE']+proj.unresolved
    intact=all(digest(q16/n)==h for n,h in frozen.items()) and len(forms)==len(recs)
    read=readiness(registry,missing_primary,ambiguous,intact,len({i for c in compat['components'] for i in c['outcome_ids']})==len(old))
    write(out/'readiness_evidence.json',dict(missing_distinct_primary=missing_primary,unresolved_process_or_projection=ambiguous,integrity=intact,classification_scope='FROZEN_JOB_EVIDENCE_AND_AUTHORIZED_FORMAL_CONTRACT'))
    tables={
      '01_q16r_mechanism_role_registry.csv':registry,
      '02_q16r_pre_relation_dependencies.csv':[dict(**p,pipeline_order=['RAW_WORDS_PHRASES','CLAUSE_ATOMS','VALENCY_CONSTITUTION_AUDIT','CLAUSE_CONSTRUCTION_REPRESENTATION','RELATION_CANDIDATES','SOURCE_BINDING']) for p in ps if p['primary_role']=='PRE_RELATION_STRUCTURE'],
      '03_q16r_primary_binding_mechanisms.csv':[r for r in registry if r['primary_methodological_role']=='PRIMARY_SOURCE_BINDING'],
      '04_q16r_corroborative_evidence_dimensions.csv':[p for p in ps if p['primary_role']=='CORROBORATIVE_RELATION_EVIDENCE'],
      '05_q16r_context_domain_mechanisms.csv':[r for r in registry if r['primary_methodological_role'] in ('REFERENCE_VISIBILITY_CONTEXT','CONFIGURATION_CONTEXT')],
      '06_q16r_post_relation_validation.csv':[p for p in ps if p['primary_role']=='POST_RELATION_VALIDATION'],
      '07_q16r_global_constraints.csv':[p for p in ps if p['primary_role']=='GLOBAL_CONSTRAINT'],
      '08_q16r_sb05_valency_role_audit.csv':audits['SB05'],'09_q16r_sb07_temporal_role_audit.csv':audits['SB07'],'10_q16r_sb08_locative_role_audit.csv':audits['SB08'],'11_q16r_sb09_domain_role_audit.csv':audits['SB09'],'12_q16r_sb10_lexical_role_audit.csv':audits['SB10'],
      '13_q16r_evidence_independence_reclassification.csv':comps,'14_q16r_shared_evidence_audit.csv':shared,'typed_evidence_inputs.csv':list(proj.bases.values())}
    for name,rr in tables.items():table(out/name,rr)
    table(out/'preserved_qualified_relations.csv',old);write(out/'q13_compatibility_audit.json',compat)
    gaps=[]
    for r in rows(q16/'11_q16_visibility_gap_audit.csv'):
        status='DOMAIN_CONTEXT_EXISTS_BUT_NOT_REFERENCE_BINDING' if r['independent_nonlocal_domains'] else 'CORRECTLY_NO_VISIBLE_PATH' if r['reason']=='NO_INDEPENDENT_DOMAIN' else 'UNRESOLVED'
        gaps.append(dict(reference_witness_id=r['reference_witness_id'],target_clause=r['target_clause'],ontology_status=status,frozen_gap=r,attempted_recovery=False))
    table(out/'visibility_zero_role_audit.csv',gaps)
    metrics=dict(baseline=len(old),retained=len(old),newly_qualified=0,total=len(old),mother=sum(o['relation_type']=='HYPOTACTIC' for o in old),parallel=sum(o['relation_type']=='PARATACTIC' for o in old),overlay=sum(o['relation_type'] not in ('HYPOTACTIC','PARATACTIC') for o in old),true_pivots=sum(p['human_review_required'] for p in compat['pivots']),sb05_cases=Counter(p['detail']['case']['case_class'] for p in audits['SB05'] if 'case' in p['detail']),sb05_valency_completion_flags=sum(p['detail'].get('valency_completion_flag',False) for p in audits['SB05']),process_counts={m:dict(Counter(p['process_kind'] for p in audits[m])) for m in audits},independence=dict(Counter(c['independence_class'] for c in comps)),qualified_independence=dict(Counter(c['independence_class'] for c in comps if c['qualified_outcome_ids'])),independence_pairs=len(comps),unresolved_projections=len(proj.unresolved),shared_groups=len(shared),readiness=read)
    write(out/'blind_metrics.json',metrics);write(out/'frozen_input_hashes.json',frozen)
    write(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()}))
    return dict(inventory=inventory,registry=registry,processes=ps,audits=audits,projection=proj,comparisons=comps,shared=shared,outcomes=old,compatibility=compat,forms=forms,reclassifications=recs,domains=domains,metrics=metrics,gaps=gaps)
