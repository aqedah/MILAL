"""Q1.6 audit-only Job pipeline. Frozen qualification is never rewritten."""
import json
from collections import Counter,defaultdict
from milal_mfr02r_data import rows,table,digest,physical_path
from milal_q1_binding import MECHANISMS,identity
from milal_q13_model import AssignmentModel
from milal_q13_pipeline import write
from milal_q16_sources import Adapter
from milal_q16_evidence import conflicts,empirical_status


def mechanism_views(a,source):
    views={m:[] for m in ('SB05','SB07','SB08','SB09')}
    constructions={str(r['clause_id']):r for r in rows(source/'blind/job/construction_inventory.csv')}
    def add(m,key,s,t,deps,detail,polarity='SUPPORT_ONLY'):
        r=a.view(m,key,s,t,deps,detail,polarity);views[m].append(r)
    for wid,w in a.records.items():
        if w['mechanism']=='SB01':
            edges=[e for e in w['evidence']['native_edges'] if e['rela'] in ('Objc','Cmpl','PreC','Subj')]
            if edges:add('SB05','VAL-'+wid,w['source_id'],w['target_id'],[wid],dict(predicate=constructions[w['source_id']]['predicate'],complement_clause_phrases=a.by_clause[w['target_id']]['PHRASE'],source_clause_atoms=a.by_clause[w['source_id']]['clause_atom_ids'],target_clause_atoms=a.by_clause[w['target_id']]['clause_atom_ids'],native_relations=edges,valency_path='EXACT_NATIVE_DEPENDENCY_ONLY',intervening_construction='NOT_NEWLY_RESOLVED',overlap_SB01=wid,overlap_Q14=[s['span_id'] for s in a.spans.values() if w['source_id'] in s['clause_ids'] and w['target_id'] in s['clause_ids']],distinct_valency_path=False))
        if w['mechanism'] in ('SB06','SB11'):
            ev=w['evidence'];frames=list(ev.get('pair_binding_witnesses',[]))+[c['witness'] for c in ev.get('pair_binding_chains',[]) if 'witness' in c]
            for f in frames:
                if f['kind'] not in ('TEMPORAL_FRAME_CORRESPONDENCE','LOCATIVE_FRAME_CORRESPONDENCE'):continue
                m='SB07' if f['kind'].startswith('TEMPORAL') else 'SB08'
                add(m,m+'-'+identity([wid,f]),w['source_id'],w['target_id'],[wid],dict(source_clause_or_span=ev.get('source_span',w['source_id']),target_clause=w['target_id'],source_expression=f['source_frame'],target_expression=f['target_frame'],dependency_type='FRAME_CORRESPONDENCE_NOT_REFERENTIAL_DEPENDENCY',surface_basis=f,frame_continuity_basis='NOT_ESTABLISHED',intervening_frame_status='UNRESOLVED',shared_existing_witness=wid,overlap_Q14='source_span' in ev,distinct_dependency=False))
    for b in rows(source/'blind/job/clause_internal_binding_candidates.csv'):
        c=str(b['binding_evidence']['raw_clause_membership'])
        add('SB05','VAL-'+b['binding_id'],c,c,a.clause_roots[c],dict(predicate=b['predicate_lexeme'],complement=b['realized_arguments'],source_atom=b['clause_atom_a'],target_atom=b['clause_atom_b'],native_relation='UNRESOLVED',valency_path=b['binding_evidence'],intervening_construction=b['intervening_atoms'],overlap_SB01='',overlap_Q14=[s['span_id'] for s in a.spans.values() if c in s['clause_ids']],frozen_candidate=b,distinct_valency_path=False),'UNRESOLVED')
    for c,r in a.by_clause.items():
        for p in r['PHRASE']:
            if p['function'] not in ('Time','Loca'):continue
            m='SB07' if p['function']=='Time' else 'SB08'
            add(m,m+'-PHRASE-'+str(p['node']),'',c,[a.phrases[int(p['node'])]],dict(source_clause_or_span='',target_clause=c,source_expression=None,target_expression=p,dependency_type='UNRESOLVED',surface_basis=p,frame_continuity_basis='NO_PAIR_SPECIFIC_DEPENDENCY_RECORDED',intervening_frame_status='UNRESOLVED',distinct_dependency=False),'UNRESOLVED')
    for did,d in a.domains.items():
        add('SB09','DOMAIN-'+did,d['opening_clause'],'',[did],dict(domain_id=did,domain_relation='DOMAIN_UNRESOLVED',member_clauses=d['member_clauses'],positive_continuity=d['boundary_basis'],independent_domain=True,membership_is_binding=False,overlap_Q15=True),'NEUTRAL')
    for pid,p in a.visibility.items():
        add('SB09','DOMAIN-'+pid,p['antecedent_clause'],p['target_clause'],[pid],dict(domain_ids=p['domain_ids'],domain_relation='DOMAIN_OVERLAP' if p['path_type']=='OVERLAPPING_SPAN_PATH' else 'DOMAIN_EMBEDDING' if p['path_type']=='EXPLICIT_SUBORDINATION_PATH' else 'DOMAIN_CONTINUATION',positive_continuity=p,path_type=p['path_type'],independent_domain=True,membership_is_binding=False,overlap_Q15=True,distinct_dependency=False))
    return views


def coverage(a,views,result):
    modules={'SB01':'milal_q1_binding','SB02':'milal_q15_references','SB03':'milal_q15_references','SB04':'milal_q1_binding','SB05':'milal_mfr02r_valency; milal_q16_pipeline','SB06':'milal_q12_configuration; milal_q14_binding','SB07':'milal_q12_configuration; milal_q14_binding; milal_q16_pipeline','SB08':'milal_q12_configuration; milal_q14_binding; milal_q16_pipeline','SB09':'milal_q15_domains; milal_q16_pipeline','SB10':'milal_q15_references','SB11':'milal_q14_binding','SB12':'milal_q13_model'}
    resultrows=[]
    for m,name in MECHANISMS.items():
        pp=[p for p in result['provenance'] if m in p['decisive_mechanism_set']];vv=views.get(m,[])
        count=Counter(v['polarity'] for v in vv)
        positive=sum(w['mechanism']==m for w in a.records.values())
        if m=='SB10':count.update(b['relation_status'] if b['relation_status']!='QUALIFIED' else 'POSITIVE_BINDING' for b in a.bindings if b['mechanism']==m)
        status='CONSTRAINT_ONLY' if m=='SB12' else 'PARTIALLY_OPERATIONAL' if m in ('SB05','SB07','SB08','SB09','SB10') else 'OPERATIONAL_DISTINCT'
        empirical='CONSTRAINT_ONLY' if m=='SB12' else empirical_status(positive,count['SUPPORT_ONLY'])
        limitation='Distinct attested dependency adapter remains underspecified; audit does not equate non-detection with empirical impossibility.' if m in views else 'Lexical recurrence is not attested lexical anaphora.' if m=='SB10' else 'No canonical assignment or referential identity is inferred.'
        abl=next((r for r in result['ablation'] if r['mechanism']==m),{})
        resultrows.append(dict(mechanism=m,definition=name,implementation_module=modules[m],raw_evidence_source='EXACT_FROZEN_BHSA_OBSERVATIONS_AND_WITNESS_IDS',conceptual_status='CONSTRAINT_ONLY' if m=='SB12' else 'CONCEPTUALLY_DISTINCT',implementation_status=status,empirical_job_status=empirical,operational_status='UNRESOLVED' if m=='SB12' else status,eligible=len(vv) if m in views else positive,positive_witness_count=positive,support_only=count['SUPPORT_ONLY'],counterevidence=count['COUNTEREVIDENCE'],neutral=count['NEUTRAL'],unresolved=count['UNRESOLVED'],qualified_relation_count=len(pp),unique_decisive_relation_count=abl.get('lose_all_binding_support',0),corroborative_relation_count=sum(m in p['corroborative_mechanism_set'] for p in result['provenance']),shared_evidence_relation_count=sum(m in p['corroborative_mechanism_set'] or (m in p['decisive_mechanism_set'] and bool(p['shared_evidence_groups'])) for p in result['provenance']),remaining_limitation=limitation))
    return resultrows


def visibility_gaps(a,q15):
    comp=defaultdict(list)
    for r in rows(q15/'07_q15_reference_compatibility.csv'):comp[r['reference_witness_id']].append(r)
    result=[]
    for r in rows(q15/'09_q15_reference_witness_reclassification.csv'):
        if int(r['global_candidate_count'])==0 or int(r['visible_candidate_count'])!=0:continue
        f=a.forms[r['reference_witness_id']];dd=[a.domains[d] for d in f['domain_ids']];cs=comp[r['reference_witness_id']]
        active=[d['domain_id'] for d in dd if len(d['member_clauses'])>1]
        role=[c for c in cs if c['dimensions'].get('GRAMMATICAL_ROLE')=='CONFLICT']
        why='REFERENCE_FORM_UNRESOLVED' if not f['reference_bearing'] else 'ROLE_CONFLICT' if cs and len(role)==len(cs) else 'DOMAIN_EXISTS_BUT_ANTECEDENT_OUTSIDE' if active and not cs else 'NO_INDEPENDENT_DOMAIN' if not active and not cs else 'DOMAIN_CONTINUITY_NOT_ESTABLISHED'
        result.append(dict(reference_witness_id=r['reference_witness_id'],target_clause=f['target_clause_id'],word_node=f['word_node'],global_candidates=int(r['global_candidate_count']),visible_candidates=0,reason=why,independent_nonlocal_domains=active,local_domains=[d['domain_id'] for d in dd if len(d['member_clauses'])==1],inspected_compatibilities=cs,interpretation='UNRESOLVED_UNDER_PERMITTED_SURFACE_EVIDENCE',material_coverage_limitation='No separately attested domain-continuity adapter; absence of route does not prove absence of referent.'))
    return result


def blind(source,q12,q14,q15,out):
    a=Adapter(source,q12,q14,q15)
    if {r['book'] for r in a.inventory}!={'Iob'}:raise ValueError('primary analysis scope violation')
    views=mechanism_views(a,source);result=a.graph.analyze(a.outcomes);cov=coverage(a,views,result)
    audit=AssignmentModel(a.outcomes,sorted(a.by_clause,key=lambda c:int(a.by_clause[c]['position']))).analyze()
    outputs={
     '01_q16_sb_mechanism_registry.csv':cov,'02_q16_evidence_dependency_graph.csv':result['graph'],'03_q16_shared_raw_evidence_groups.csv':result['groups'],
     '04_q16_sb05_valency_witnesses.csv':views['SB05'],'05_q16_sb07_temporal_witnesses.csv':views['SB07'],'06_q16_sb08_locative_witnesses.csv':views['SB08'],'07_q16_sb09_domain_witnesses.csv':views['SB09'],
     '08_q16_mechanism_overlap_matrix.csv':result['overlap'],'09_q16_mechanism_ablation.csv':result['ablation'],'10_q16_relation_mechanism_provenance.csv':result['provenance'],
     '11_q16_visibility_gap_audit.csv':visibility_gaps(a,q15),'12_q16_mechanism_support_conflicts.csv':conflicts(sum(views.values(),[])),
     '13_q16_relation_qualification_delta.csv':[dict(outcome_id=o['structural_outcome_group_id'],status='FROZEN_RETAINED',newly_qualified=False) for o in a.outcomes],
     '14_q16_qualified_relation_universe.csv':a.outcomes,'15_q16_q13_compatibility_reaudit.csv':audit['matrix'],'16_q16_true_decision_pivots.csv':audit['pivots'],'21_q16_mechanism_coverage_matrix.csv':cov}
    for name,rr in outputs.items():table(out/name,rr,fields=['candidate_id','status','witness_ids','resolution'] if name.startswith('12_') and not rr else None)
    write(out/'q13_coherent_assignments.json',audit['assignments']);write(out/'q13_global_audit.json',audit['global_audit']);write(out/'q13_symbolic_components.json',audit['components'])
    metrics=dict(baseline=len(a.outcomes),retained=len(a.outcomes),newly_qualified=0,total=len(a.outcomes),mother=sum(o['relation_type']=='HYPOTACTIC' for o in a.outcomes),parallel=sum(o['relation_type']=='PARATACTIC' for o in a.outcomes),overlay=sum(o['relation_type'] not in ('HYPOTACTIC','PARATACTIC') for o in a.outcomes),conflicts=sum(bool(r['positive_incompatibility_witness']) for r in audit['matrix']),true_pivots=sum(p['human_review_required'] for p in audit['pivots']),shared_raw_groups=len(result['groups']),duplicate_views_blocked=sum(v['polarity']=='SUPPORT_ONLY' and v['candidate_id'] in {'P'+p['source_id']+'-'+p['target_id'] for p in result['provenance']} for vv in views.values() for v in vv),independent_chain_pairs=sum(len(p['independent_chain_pairs']) for p in result['provenance']),recovered_positive_witnesses=len(a.records))
    write(out/'blind_metrics.json',metrics)
    write(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()}))
    return a,views,result,cov,audit,metrics
