"""Additive composite binding over the exact frozen relation-candidate stream."""
import copy
import json
import shutil
from collections import Counter
from itertools import zip_longest
from pathlib import Path
from milal_mfr02r_data import rows,table,Table,digest,physical_path
from milal_q1_binding import outcome,identity
from milal_q13_model import AssignmentModel
from milal_q13_pipeline import write
from milal_q14_spans import SurfaceSpans,INDEPENDENT
from milal_q14_binding import CompositeBinding,bare_formula


def observations(index,out,prefix=''):
    table(out/(prefix+'01_q14_surface_construction_spans.csv'),index.spans.values(),fields=None if index.spans else ['span_id','clause_ids','construction_independence_status'])
    table(out/(prefix+'02_q14_surface_span_membership.csv'),index.membership_rows(),fields=['span_id','member_clause_id','member_clause_atom_id','membership_basis','independence_status','provenance'])
    table(out/(prefix+'03_q14_span_boundary_witnesses.csv'),[dict(span_id=s['span_id'],boundary_witnesses=s['boundary_witnesses'],independence_status=s['construction_independence_status']) for s in index.spans.values()],fields=['span_id','boundary_witnesses','independence_status'])
    table(out/(prefix+'04_q14_composite_surface_profiles.csv'),index.composites.values(),fields=None if index.composites else ['span_id','composite_profile_id'])
    table(out/(prefix+'05_q14_composite_configuration_families.csv'),index.families.values(),fields=None if index.families else ['composite_family_id','ordered_structural_template'])


def correspondence_outputs(binder,out):
    cs=sorted(binder.cache.values(),key=lambda c:c['correspondence_id'])
    table(out/'06_q14_composite_correspondence.csv',cs,fields=None if cs else ['correspondence_id','positive_source_binding'])
    cross=[c for c in cs if c['correspondence_kind']=='CROSS_FAMILY_CONFIGURATION_CORRESPONDENCE']
    table(out/'07_q14_cross_family_correspondence.csv',cross,fields=list(cs[0]) if cs else ['correspondence_id','family_A','family_B'])
    table(out/'08_q14_position_mappings.csv',(dict(correspondence_id=c['correspondence_id'],**m) for c in cs for m in c['position_mapping']),
        fields=['correspondence_id','source_span','target_span','source_position','target_position','source_clause_id','target_clause_id','source_component_profile','target_component_profile','mapping_basis','source_roles','target_roles'])
    table(out/'09_q14_composite_pair_binding_witnesses.csv',[dict(correspondence_id=c['correspondence_id'],source_span=c['source_span'],target_span=c['target_span'],
        pair_binding_chains=c['pair_binding_chains'],positive_source_binding=c['positive_source_binding']) for c in cs],
        fields=['correspondence_id','source_span','target_span','pair_binding_chains','positive_source_binding'])
    return cs,cross


def blind(source,q12,q13,out,grammar):
    inventory=list(rows(source/'blind/job/02_clause_feature_inventory.csv'))
    if {r['book'] for r in inventory}!={'Iob'}:raise ValueError('Job-only primary analysis required')
    # Only raw observation fields enter the construction adapter.
    index=SurfaceSpans(inventory,grammar['lexicons']);binder=CompositeBinding(index);observations(index,out)
    baseline=list(rows(q13/'preserved_q12_qualified_relations.csv'))
    old_outcomes=list(rows(q13/'preserved_q12_outcome_groups.csv'))
    universe={r['candidate_id']:copy.deepcopy(r) for r in baseline};outcomes={r['structural_outcome_group_id']:copy.deepcopy(r) for r in old_outcomes}
    initial_ids=set(outcomes);counts=Counter();mechanisms=Counter();grammar_errors=[]
    fields=['candidate_id','source_id','target_id','status','existing_qualified_relations','composite_qualified_relations',
        'new_relation_types','existing_grammar_matches','qualified_paths','correspondence_ids','deferred']
    raw_digest=digest(physical_path(source/'blind/job/09_candidate_evidence_matrix.csv'))
    with Table(out/'10_q14_relation_qualification_delta.csv',fields) as delta:
        for old,match in zip_longest(rows(q12/'raw_qualification_crosswalk.csv'),rows(source/'blind/job/08_relation_rule_matches.csv')):
            if old is None or match is None:raise ValueError('raw stream length changed')
            sid,tid=old['source_id'],old['target_id'];pair=old['candidate_id'];counts['raw']+=1
            if pair!=match['pair_id'] or (sid,tid)!=(str(match['source_clause_id']),str(match['target_clause_id'])) or old['raw_table_sha256']!=raw_digest:
                raise ValueError('exact raw pair provenance mismatch')
            if not index.memberships.get(sid) or not index.memberships.get(tid):continue
            result=binder.evaluate(sid,tid,match['matches'],deferred=old['deferred']);counts['evaluated_pairs']+=1;counts[result['status']]+=1
            before=universe.get(pair,{}).get('qualified_relations',[]);new=sorted(set(result['qualified_relations'])-set(before))
            delta.write(dict(candidate_id=pair,source_id=sid,target_id=tid,status=result['status'],existing_qualified_relations=before[:],
                composite_qualified_relations=result['qualified_relations'],new_relation_types=new,existing_grammar_matches=match['matches'],
                qualified_paths=result['qualified_paths'],correspondence_ids=result['correspondence_ids'],deferred=old['deferred']))
            if any(not any(m['rule_id']==p['rule_id'] and m['relation']==p['relation'] for m in match['matches']) for p in result['qualified_paths']):grammar_errors.append(pair)
            for w in result['witnesses']:
                if any(p['witness_id']==w['witness_id'] for p in result['qualified_paths']):mechanisms[w['mechanism']]+=1
            if not new:continue
            record=universe.setdefault(pair,{k:copy.deepcopy(v) for k,v in old.items() if k not in ('raw_row_sha256','raw_table_sha256')})
            record['qualified_relations']=sorted(set(record['qualified_relations'])|set(new))
            record['qualified_paths'] += [p for p in result['qualified_paths'] if p['relation'] in new]
            record['qualification']='QUALIFIED_CONFIGURATION' if record['qualification'] not in ('QUALIFIED_DIRECT','QUALIFIED_UNIT_MEDIATED') else record['qualification']
            record['qualification_reason']=sorted(set(record['qualification_reason'])|set(result['qualification_reason']))
            record['disqualification_reason']='';record['correspondence_ids']=sorted(set(record['correspondence_ids'])|set(result['correspondence_ids']))
            for rel in new:
                o=outcome(sid,tid,rel);o['provenance_paths']=[dict(candidate_id=pair,**p) for p in result['qualified_paths'] if p['relation']==rel]
                if o['structural_outcome_group_id'] in outcomes:raise ValueError('attempted frozen outcome overwrite')
                outcomes[o['structural_outcome_group_id']]=o
    cs,cross=correspondence_outputs(binder,out)
    table(out/'11_q14_qualified_relation_universe.csv',[universe[k] for k in sorted(universe)])
    os=[outcomes[k] for k in sorted(outcomes)];table(out/'12_q14_structural_outcome_groups.csv',os)
    model=AssignmentModel(os,index.order);reaudit=model.analyze()
    table(out/'13_q14_q13_compatibility_reaudit.csv',reaudit['matrix'],fields=None if reaudit['matrix'] else ['target_id','classification'])
    table(out/'14_q14_true_decision_pivots.csv',reaudit['pivots'])
    table(out/'q13_coherent_assignments.csv',reaudit['assignments']);write(out/'q13_global_audit.json',reaudit['global_audit'])
    write(out/'q13_symbolic_components.json',reaudit['components'])
    bare_ids={sid for sid,s in index.spans.items() if bare_formula(index,s)}
    bare_comparisons=[c for c in cs if c['source_span'] in bare_ids and c['target_span'] in bare_ids]
    formula=dict(bare_repeated_formula_spans=len(bare_ids),same_family_comparisons=sum(c['same_family'] for c in bare_comparisons),
        positive_composite_bindings=sum(c['positive_source_binding'] for c in bare_comparisons),
        blocked_generic_formula_only=sum(c['status']=='BLOCKED_GENERIC_FORMULA_ONLY' for c in bare_comparisons))
    table(out/'16_q14_dialogue_formula_negative_control.csv',[formula])
    table(out/'19_q14_mechanism_coverage.csv',[dict(mechanism=k,qualified_composite_witnesses=mechanisms[k],
        implementation='COMPOSITE_EXTENSION_OF_EXISTING_MECHANISM') for k in ('SB06','SB11')])
    preserved={}
    for name in ('preserved_q12_qualified_relations.csv','preserved_q12_outcome_groups.csv','preserved_q12_pivots.csv','preserved_human_judgments.csv'):
        p=physical_path(q13/name);dest=out/p.name;shutil.copyfile(p,dest);preserved[p.name]=digest(dest)
    counts.update(spans=len(index.spans),independent_spans=sum(s['construction_independence_status'] in INDEPENDENT for s in index.spans.values()),
        unresolved_spans=sum(s['construction_independence_status'] not in INDEPENDENT for s in index.spans.values()),overlapping_spans=sum(bool(s['overlapping_span_ids']) for s in index.spans.values()),
        composite_profiles=len(index.composites),composite_families=len(index.families),same_family_correspondences=sum(c['same_family'] for c in cs),
        cross_family_correspondences=len(cross),positive_composite_bindings=sum(c['positive_source_binding'] for c in cs),
        baseline_relations=len(initial_ids),retained_relations=len(initial_ids&set(outcomes)),newly_qualified=len(set(outcomes)-initial_ids),
        total_relations=len(os),qualified_pairs=len(universe),mother_relations=sum(o['relation_type']=='HYPOTACTIC' for o in os),
        parallel_relations=sum(o['relation_type']=='PARATACTIC' for o in os),overlay_relations=sum(o['relation_type'] not in ('HYPOTACTIC','PARATACTIC') for o in os),
        compatibility_conflicts=sum(bool(r['positive_incompatibility_witness']) for r in reaudit['matrix']),true_pivots=sum(p['human_review_required'] for p in reaudit['pivots']),
        human_judgments=sum(1 for _ in rows(q13/'preserved_human_judgments.csv')))
    write(out/'blind_metrics.json',dict(counts=counts,formula=formula,grammar_errors=grammar_errors,preserved_hashes=preserved,
        baseline_outcomes_unchanged=all(outcomes[o['structural_outcome_group_id']]==o for o in old_outcomes),raw_table_sha256=raw_digest,
        raw_crosswalk_sha256=digest(physical_path(q12/'raw_qualification_crosswalk.csv'))))
    write(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        events=['SURFACE_DISCOVERY','COMPOSITE_BINDING','Q13_COMPATIBILITY','BLIND_FROZEN'],control_ids_used=False,human_judgments_used=False))
    return index,binder,dict(counts),reaudit
