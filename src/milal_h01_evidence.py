"""Lossless gap register and role-aware packet source catalog."""
from collections import defaultdict
from milal_mfr02r_data import rows
from milal_q1_binding import identity
from milal_q16r_roles import ROLES
from milal_r3c_0_2_reviewability import REVIEW_FIELDS

DISPLAY_ROLES=tuple(r for r in ROLES if r not in ('HYBRID_WITH_EXPLICIT_SUBTYPES','UNRESOLVED_ROLE'))


def gap_register(q16r):
    gaps=[]
    def add(target,kind,mechanism,rid,original):
        gaps.append(dict(gap_id='HG-'+identity([target,kind,rid]),target=str(target),gap_type=kind,relevant_mechanism=mechanism,
            could_materially_change_current_decision='UNRESOLVED',status='NO_CURRENT_STRUCTURAL_DECISION_EFFECT',
            reason='GAP_SUPPLIES_NO_ADDITIONAL_QUALIFIED_STRUCTURAL_COMMITMENT',source_evidence_id=rid,source_record=original))
    for r in rows(q16r/'12_q16r_sb10_lexical_role_audit.csv'):
        d=r['detail'];f=d['form'];c=d['classification']
        if c['referential_identity_status']!='CONFIRMED':
            add(f['target_clause_id'],'REFERENCE_IDENTITY' if f['reference_bearing'] else 'LEXICAL_ANAPHORA','SB02/SB03' if f['reference_bearing'] else 'SB10',f['reference_witness_id'],r)
    for r in rows(q16r/'08_q16r_sb05_valency_role_audit.csv'):
        d=r['detail']
        if 'case' in d:
            owners=d['case']['source_owners']+d['case']['target_owners']
            for target in sorted(set(owners)):add(target,'VALENCY_GOVERNANCE_NOT_ESTABLISHED','SB05',r['process_id'],r)
    for n,m in [('09_q16r_sb07_temporal_role_audit.csv','SB07'),('10_q16r_sb08_locative_role_audit.csv','SB08')]:
        for r in rows(q16r/n):
            d=r['detail'];w=d.get('frozen_witness',{});target=w.get('target_id') or d.get('form',{}).get('target_clause_id')
            if target and (r['process_kind'] in ('TIME_PARAMETER','LOCATION_PARAMETER','TEMPORAL_REFERENCE_FORM','LOCATIVE_REFERENCE_FORM')):
                add(target,'TIME_INTERPRETATION' if m=='SB07' else 'LOCATION_INTERPRETATION',m,r['process_id'],r)
    for r in rows(q16r/'visibility_zero_role_audit.csv'):
        add(r['target_clause'],'DOMAIN_VISIBILITY','SB09',r['reference_witness_id'],r)
    if len({g['gap_id'] for g in gaps})!=len(gaps):raise ValueError('duplicate gap identity')
    return sorted(gaps,key=lambda g:g['gap_id'])


def load_catalog(source,q16,q16r):
    graph={r['node_id']:r for r in rows(q16/'02_q16_evidence_dependency_graph.csv')}
    registry={r['mechanism_id']:r for r in rows(q16r/'01_q16r_mechanism_role_registry.csv')}
    provenance={r['outcome_id']:r for r in rows(q16/'10_q16_relation_mechanism_provenance.csv')}
    processes={}
    for name in ('02_q16r_pre_relation_dependencies.csv','04_q16r_corroborative_evidence_dimensions.csv','09_q16r_sb07_temporal_role_audit.csv',
                 '10_q16r_sb08_locative_role_audit.csv','11_q16r_sb09_domain_role_audit.csv','12_q16r_sb10_lexical_role_audit.csv'):
        for r in rows(q16r/name):processes[r['process_id']]=r
    for n in graph.values():
        w=n['payload'].get('frozen_witness')
        if w:
            m=w['mechanism'];processes[w['witness_id']]=dict(process_id=w['witness_id'],mechanism_id=m,
                primary_role=registry[m]['primary_methodological_role'],detail=dict(witness=w),source_artifact='q16/02_q16_evidence_dependency_graph.csv')
    return dict(graph=graph,registry=registry,provenance=provenance,processes=processes,
        grammar={r['rule_id']:r for r in rows(source/'blind/job/01_relation_grammar_registry.csv')},
        ablation=list(rows(q16/'09_q16_mechanism_ablation.csv')),
        shared={r['raw_evidence_identity']:r for r in rows(q16r/'14_q16r_shared_evidence_audit.csv')})


def process_targets(p):
    d=p['detail'];w=d.get('frozen_witness',{}) or d.get('witness',{});f=d.get('form',{});case=d.get('case',{})
    return {str(x) for x in [w.get('source_id'),w.get('target_id'),f.get('target_clause_id'),*case.get('source_owners',[]),*case.get('target_owners',[]),*d.get('targets',[])] if x}


def partition_evidence(processes,pair_ids,endpoints):
    direct={};context={}
    for key,p in processes.items():
        if key not in pair_ids and not process_targets(p)&set(endpoints):continue
        d=p['detail'];w=d.get('frozen_witness',{}) or d.get('witness',{})
        pair_specific=bool(w.get('source_id') and w.get('target_id')) or p['primary_role'] in ('PRIMARY_SOURCE_BINDING','GLOBAL_CONSTRAINT')
        (context if pair_specific and key not in pair_ids else direct)[key]=p
    return direct,context


def packets(result,inventory,outcomes,gaps,catalog):
    byid={r['structural_outcome_group_id']:r for r in outcomes};aa={a['assignment_id']:a for a in result['assignments']};cards=[];used=set();raw_used=set()
    for component in result['components']:
        alternatives=[]
        for aid in component['coherent_positive_assignments']:
            assignment=aa[aid];relations=[]
            for oid in assignment['selected_relation_ids']:
                r=byid[oid];prov=catalog['provenance'][oid];ids=set(prov['witness_ids']);pair='P'+r['source_or_peer']+'-'+r['target']
                for key,n in catalog['graph'].items():
                    if n['mechanism'] and n['payload'].get('candidate_id')==pair:ids.add(key)
                ids.update(component['constraint_ids'])
                relevant,context=partition_evidence(catalog['processes'],ids,{r['source_or_peer'],r['target']})
                roles={role:sorted(k for k,p in relevant.items() if p['primary_role']==role) for role in DISPLAY_ROLES}
                used.update(relevant);used.update(context);raw=set().union(*(set(catalog['graph'][w]['raw_evidence_nodes']) for w in prov['witness_ids']));raw_used|=raw
                rules=sorted({p['rule_id'] for p in r['provenance_paths']})
                if any(rule not in catalog['grammar'] for rule in rules):raise ValueError('missing exact relation grammar rule')
                relations.append(dict(relation_id=oid,source=inventory[r['source_or_peer']],target=inventory[r['target']],relation=r,
                    structural_implication=r.get('textual_level_effect_candidate',r['relation_type']),grammar_rules=[catalog['grammar'][x] for x in rules],
                    role_evidence_ids=roles,context_role_evidence_ids={role:sorted(k for k,p in context.items() if p['primary_role']==role) for role in DISPLAY_ROLES},
                    context_warning='OTHER_PAIR_BINDINGS_ARE_CONTEXT_ONLY; NOT_SUPPORT_FOR_THIS_ALTERNATIVE',
                    primary_source_binding=sorted({catalog['processes'][w]['mechanism_id'] for w in prov['witness_ids'] if catalog['processes'][w]['primary_role']=='PRIMARY_SOURCE_BINDING'}),
                    qualification_provenance=prov,raw_evidence_ids=sorted(raw),shared_raw_warnings=sorted(raw&set(catalog['shared'])),
                    feature_evidence={t:{k:inventory[t][k] for k in ('TIME','LOCATION','PARTICIPANT','REFERENCE','WORD','PHRASE')} for t in (r['source_or_peer'],r['target'])},
                    unresolved_gap_ids=[g['gap_id'] for g in gaps if g['target'] in (r['source_or_peer'],r['target'])]))
            alternatives.append(dict(assignment_id=aid,assignment=assignment,relations=relations,meaning='COHERENT_POSITIVE_COMMITMENTS; OMITTED_RELATIONS_UNDECIDED'))
        cards.append(dict(review_item_id='HR-'+component['component_id'],component_id=component['component_id'],target_ids=component['targets'],
            targets=[inventory[t] for t in component['targets']],alternatives=alternatives,compatibility=component,
            global_constraints=[c for c in result['constraints'] if c['constraint_id'] in component['constraint_ids']],
            unresolved_gap_ids=[g['gap_id'] for g in gaps if g['target'] in component['targets']],
            **{f:'UNREVIEWED' if f=='review_status' else '' for f in REVIEW_FIELDS}))
    for key in used:
        if key in catalog['graph']:raw_used.update(catalog['graph'][key]['raw_evidence_nodes'])
    return cards,dict(processes={k:catalog['processes'][k] for k in sorted(used)},raw_evidence={k:catalog['graph'][k] for k in sorted(raw_used)},
        shared_raw={k:catalog['shared'][k] for k in sorted(raw_used&set(catalog['shared']))})
