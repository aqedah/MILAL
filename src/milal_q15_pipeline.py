"""Q1.5 streaming derived reference layer and frozen candidate qualification."""
import copy
import json
import shutil
from collections import Counter
from itertools import zip_longest
from statistics import median
from milal_mfr02r_data import rows,table,Table,digest,physical_path
from milal_q1_binding import outcome
from milal_q13_model import AssignmentModel
from milal_q13_pipeline import write
from milal_q15_domains import Domains
from milal_q15_references import Visibility

CANDIDATE_FIELDS=['reference_witness_id','antecedent_id','original_global_candidate','supplemental_domain_candidate','visibility_status','visibility_path_ids','path_type','referential_identity']


def emit_reference(v,out):
    table(out/'01_q15_reference_form_inventory.csv',v.forms)
    table(out/'02_q15_reference_visibility_domains.csv',v.d.domains.values())
    table(out/'03_q15_domain_membership.csv',(dict(domain_id=d['domain_id'],clause_id=c,independence_status=d['independence_status']) for d in v.d.domains.values() for c in d['member_clauses']))
    table(out/'04_q15_antecedent_inventory.csv',v.d.antecedents.values())
    table(out/'07_q15_reference_compatibility.csv',v.compat,fields=['reference_witness_id','antecedent_id','dimensions','visible','source_binding_supported','native_reference_evidence'])
    table(out/'08_q15_reference_visibility_paths.csv',(dict(visibility_path_id=p['visibility_path_id'],reference_witness_id=p['reference_witness_id'],antecedent_id=p['antecedent_id'],path=p) for p in v.paths),fields=['visibility_path_id','reference_witness_id','antecedent_id','path'])
    table(out/'09_q15_reference_witness_reclassification.csv',v.reclassified)
    for n,m in ((10,'SB02'),(11,'SB03'),(12,'SB10')):
        rr=[r for r in v.bindings if r['mechanism']==m]
        table(out/f'{n:02d}_q15_{m.lower()}_qualification.csv',rr,fields=list(v.bindings[0]) if v.bindings else ['binding_id','mechanism','relation_status'])
    write(out/'17_q15_candidate_reduction_metrics.json',v.metrics())
    expl=[]
    for threshold in (100,500,1000):
        rr=[r for r in v.reclassified if r['global_candidate_count']>threshold]
        selected={r['reference_witness_id'] for r in rr}
        expl.append(dict(original_candidate_count_greater_than=threshold,count_before=len(rr),median_visible=median(r['visible_candidate_count'] for r in rr) if rr else 0,
            maximum_visible=max((r['visible_candidate_count'] for r in rr),default=0),visibility_mechanisms=sorted({p['path_type'] for p in v.paths if p['reference_witness_id'] in selected}),
            witness_ids=sorted(selected),threshold_used_in_linguistic_logic=False))
    table(out/'19_q15_reference_explosion_diagnostic.csv',expl)
    table(out/'22_q15_mechanism_coverage.csv',[dict(mechanism=m,qualified=sum(b['relation_status']=='QUALIFIED' for b in v.bindings if b['mechanism']==m),
        support_only=sum(b['relation_status']=='SUPPORT_ONLY' for b in v.bindings if b['mechanism']==m),unresolved=sum(b['relation_status']=='UNRESOLVED' for b in v.bindings if b['mechanism']==m),
        policy='LEXICAL_RECURRENCE_EVIDENCE_ONLY; NO_ATTESTED_ANAPHORIC_ADAPTER' if m=='SB10' else 'UNIQUE_VISIBLE_PROVISIONAL_OR_EXACT_NATIVE; EXISTING_GRAMMAR_REQUIRED') for m in ('SB02','SB03','SB10')])


def blind(source,q12,q14,out,grammar):
    inventory=list(rows(source/'blind/job/02_clause_feature_inventory.csv'))
    if {r['book'] for r in inventory}!={'Iob'}:raise ValueError('Job-only primary analysis')
    spans=list(rows(q14/'01_q14_surface_construction_spans.csv'))
    oldrefs=list(rows(q12/'06_q12_reference_witnesses.csv'))
    d=Domains(inventory,spans,grammar['lexicons']);v=Visibility(d,oldrefs)
    with Table(out/'06_q15_visible_antecedent_candidates.csv',CANDIDATE_FIELDS) as candidates:v.process(candidates.write)
    original=list(rows(q14/'12_q14_structural_outcome_groups.csv'))
    os={o['structural_outcome_group_id']:copy.deepcopy(o) for o in original};initial=set(os)
    universe={r['candidate_id']:copy.deepcopy(r) for r in rows(q14/'11_q14_qualified_relation_universe.csv')}
    rawhash=digest(physical_path(source/'blind/job/09_candidate_evidence_matrix.csv'));counts=Counter();grammar_errors=[];seen_pairs=set()
    with Table(out/'13_q15_relation_qualification_delta.csv',['candidate_id','source_id','target_id','existing_qualified_relations','reference_qualified_relations','new_relation_types','qualified_paths','existing_grammar','deferred']) as delta:
        for old,match in zip_longest(rows(q12/'raw_qualification_crosswalk.csv'),rows(source/'blind/job/08_relation_rule_matches.csv')):
            if old is None or match is None:raise ValueError('raw candidate stream mismatch')
            sid,tid=old['source_id'],old['target_id'];pair=old['candidate_id'];counts['raw']+=1
            if pair!=match['pair_id'] or (sid,tid)!=(str(match['source_clause_id']),str(match['target_clause_id'])) or old['raw_table_sha256']!=rawhash:raise ValueError('raw candidate identity mismatch')
            if (sid,tid) not in v.by_pair:continue
            seen_pairs.add((sid,tid));result=v.evaluate(sid,tid,match['matches'],old['deferred']);counts['evaluated_pairs']+=1
            before=list(universe.get(pair,{}).get('qualified_relations',[]));new=sorted(set(result['qualified_relations'])-set(before))
            delta.write(dict(candidate_id=pair,source_id=sid,target_id=tid,existing_qualified_relations=before,reference_qualified_relations=result['qualified_relations'],
                new_relation_types=new,qualified_paths=result['qualified_paths'],existing_grammar=match['matches'],deferred=old['deferred']))
            if any(not any(p['rule_id']==m['rule_id'] and p['relation']==m['relation'] for m in match['matches']) for p in result['qualified_paths']):grammar_errors.append(pair)
            if not new:continue
            r=universe.setdefault(pair,{k:copy.deepcopy(val) for k,val in old.items() if k not in ('raw_row_sha256','raw_table_sha256')})
            r['qualified_relations']=sorted(set(r['qualified_relations'])|set(new));r['qualified_paths'] += [p for p in result['qualified_paths'] if p['relation'] in new]
            r['qualification']=result['qualification'];r['qualification_reason']=sorted(set(r['qualification_reason'])|set(result['qualification_reason']));r['disqualification_reason']=''
            for rel in new:
                o=outcome(sid,tid,rel);o['provenance_paths']=[dict(candidate_id=pair,**p) for p in result['qualified_paths'] if p['relation']==rel]
                if o['structural_outcome_group_id'] in os:raise ValueError('frozen outcome overwrite')
                os[o['structural_outcome_group_id']]=o
    for pair,bb in v.by_pair.items():
        if pair not in seen_pairs:
            for b in bb:b['relation_status']='SUPPORT_ONLY'
    table(out/'14_q15_qualified_relation_universe.csv',[universe[k] for k in sorted(universe)])
    outcomes=[os[k] for k in sorted(os)];table(out/'q15_structural_outcome_groups.csv',outcomes)
    audit=AssignmentModel(outcomes,d.order).analyze()
    table(out/'15_q15_q13_compatibility_reaudit.csv',audit['matrix'],fields=None if audit['matrix'] else ['target_id','classification'])
    table(out/'16_q15_true_decision_pivots.csv',audit['pivots']);table(out/'q13_coherent_assignments.csv',audit['assignments'])
    write(out/'q13_global_audit.json',audit['global_audit']);write(out/'q13_symbolic_components.json',audit['components'])
    emit_reference(v,out)
    preserved={}
    for src,name in [(q12/'06_q12_reference_witnesses.csv','preserved_q12_reference_witnesses.csv'),
        (q12/'07_q12_reference_candidate_antecedents.csv','05_q15_global_reference_candidates.csv'),
        (q14/'01_q14_surface_construction_spans.csv','preserved_q14_surface_spans.csv'),
        (q14/'11_q14_qualified_relation_universe.csv','preserved_q14_qualified_relations.csv'),
        (q14/'12_q14_structural_outcome_groups.csv','preserved_q14_outcomes.csv'),
        (q14/'preserved_human_judgments.csv','preserved_human_judgments.csv')]:
        physical=physical_path(src);dest=out/(name+('.gz' if physical.suffix=='.gz' else ''));shutil.copyfile(physical,dest);preserved[dest.name]=digest(dest)
    counts.update(baseline_relations=len(initial),retained_relations=len(initial&set(os)),newly_qualified=len(set(os)-initial),total_relations=len(os),
        mother_relations=sum(o['relation_type']=='HYPOTACTIC' for o in outcomes),parallel_relations=sum(o['relation_type']=='PARATACTIC' for o in outcomes),overlay_relations=sum(o['relation_type'] not in ('HYPOTACTIC','PARATACTIC') for o in outcomes),
        compatibility_conflicts=sum(bool(r['positive_incompatibility_witness']) for r in audit['matrix']),true_pivots=sum(p['human_review_required'] for p in audit['pivots']),
        reference_witnesses=len(v.forms),original_global_candidates=v.global_count,classified_candidates=v.classified_count,supplemental_candidates=v.supplemental_count,
        preserved_spans=len(spans),human_judgments=sum(1 for _ in rows(q14/'preserved_human_judgments.csv')))
    evidence=dict(counts=counts,grammar_errors=grammar_errors,preserved_hashes=preserved,raw_table_sha256=rawhash,
        baseline_outcomes_unchanged=all(os[o['structural_outcome_group_id']]==o for o in original),reference_metrics=v.metrics())
    write(out/'blind_metrics.json',evidence)
    write(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},events=['VISIBILITY','QUALIFICATION','Q13_COMPATIBILITY','BLIND_FROZEN']))
    return v,dict(counts),audit
