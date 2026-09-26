"""Decision-only sieve using the frozen Q1.3 feasibility oracle.

Minimal forbidden sets, not graph connectivity or omitted edges, connect decisions.
No corpus locations, historical reviews, discovery rules, or preferences enter here.
"""
from collections import Counter, defaultdict
from itertools import combinations
from milal_q13_model import AssignmentModel, commitment, dimension, MOTHER, PARALLEL
from milal_mfr02r_graph import Union
from milal_q1_binding import identity

STATUSES=('TRUE_DECISION_PIVOT','QUALIFIED_NONCOMPETING_CANDIDATE','QUALIFIED_COMPATIBLE_SET',
 'DEFERRED_COMPATIBILITY_UNRESOLVED','EVIDENCE_GAP_NOT_STRUCTURAL_DECISION',
 'NO_QUALIFIED_RELATION','EXPLICIT_NEGATIVE_CONFLICT','GLOBAL_CONSTRAINT_DECISION','UNRESOLVED_REVIEW_STATUS')
DISPOSITIONS=('PART_OF_TRUE_DECISION','NONCOMPETING_MOTHER_CANDIDATE','ADDITIVE_PARALLEL',
 'ORTHOGONAL_COMPATIBLE','COMPATIBILITY_DEFERRED','CORROBORATED_DUPLICATE_PATH','EXPLICIT_CONFLICT','OTHER_EXPLAINED_STATUS')
REVIEW_STATUSES={'TRUE_DECISION_PIVOT','GLOBAL_CONSTRAINT_DECISION','EXPLICIT_NEGATIVE_CONFLICT'}


def minimal_cores(model):
    """Enumerate all minimal monotone conflicts by conflict-directed deletion.

    A different minimal core must omit at least one member of the current core.
    Coherent pools terminate immediately; no Cartesian subset enumeration occurs.
    """
    pending=[frozenset(model.rows)];seen=set();cores=set()
    while pending:
        pool=pending.pop()
        if pool in seen:continue
        seen.add(pool);core=model.minimal_conflict(pool)
        if core is None:continue
        cores.add(core)
        pending.extend(pool-{oid} for oid in sorted(core))
    return sorted(cores,key=lambda c:tuple(sorted(c))),len(seen)


def core_types(model,core):
    rs=[model.rows[i] for i in core];kinds=set();errors=model.errors(core)
    for a,b in combinations(rs,2):
        if dimension(a)==dimension(b)==MOTHER and a['target']==b['target'] and a['source_or_peer']!=b['source_or_peer']:
            kinds.add('MOTHER_COMPETITION')
        if {dimension(a),dimension(b)}=={MOTHER,PARALLEL} and {a['source_or_peer'],a['target']}=={b['source_or_peer'],b['target']}:
            kinds.add('TRUE_PAIR_RELATION_CONFLICT')
    strict=[i for i in core if dimension(model.rows[i])==MOTHER]
    if 'CYCLE_AFTER_PARALLEL_CONTRACTION' in model.errors(strict):kinds.add('STRICT_MOTHER_CYCLE')
    if any(dimension(r)==PARALLEL for r in rs) and any(x in errors for x in ('STRICT_AND_EQUAL_LEVEL_CONTRADICTION','CYCLE_AFTER_PARALLEL_CONTRACTION')):
        kinds.add('PARALLEL_HIERARCHY_INCOMPATIBILITY_CANDIDATE')
    if any(x.startswith('GLOBAL_CONSTRAINT:') for x in errors):kinds.add('SB12_HARD_CONFLICT')
    if 'EXPLICIT_EXCLUSION_VS_POSITIVE_RELATION' in errors:kinds.add('EXPLICIT_NEGATIVE_CONFLICT')
    if not kinds:raise ValueError('NEEDS_COMPATIBILITY_MODEL_REVIEW: unclassified oracle conflict')
    return sorted(kinds)


def sieve(outcomes,targets,gaps=(),constraints=()):
    model=AssignmentModel(outcomes,targets,constraints);cores,searches=minimal_cores(model)
    cs=[];active={i for c in cores for i in c};union=Union(active)
    for core in cores:
        ids=sorted(core)
        if len(ids)<2:raise ValueError('NEEDS_COMPATIBILITY_MODEL_REVIEW: incoherent qualified singleton')
        for oid in ids[1:]:union.join(ids[0],oid)
        cs.append(dict(constraint_id='HC-'+identity(ids),relation_ids=ids,targets=sorted({model.rows[i]['target'] for i in ids}),
            constraint_types=core_types(model,core),violations=model.errors(core),provenance=model.provenance(core),
            minimal=all(not model.errors(core-{i}) for i in core),hard=True,activation='ONLY_IF_ALL_POSITIVE_COMMITMENTS_SELECTED'))
    groups=defaultdict(list)
    for oid in sorted(active):groups[union.find(oid)].append(oid)
    components=[];assignments=[];by_relation={}
    for ids in groups.values():
        cid='HD-'+identity(ids);cc=[c for c in cs if set(c['relation_ids'])<=set(ids)];tt=sorted({model.rows[i]['target'] for i in ids});aa={}
        for c in cc:
            for omitted in c['relation_ids']:
                selected=sorted(set(c['relation_ids'])-{omitted});aid='HA-'+identity([cid,selected])
                aa[aid]=dict(assignment_id=aid,component_id=cid,selected_relation_ids=selected,
                    target_assignments=[model.assignment(t,selected) for t in tt],
                    undecided_relations=sorted(set(ids)-set(selected)),unselected_semantics='UNDECIDED',
                    coherent=not model.errors(selected),purpose='FEASIBILITY_WITNESS_NOT_SELECTION')
        proofs=[]
        for a,b in combinations(sorted(aa),2):
            sa=set(aa[a]['selected_relation_ids']);sb=set(aa[b]['selected_relation_ids'])
            if sa-sb and sb-sa and model.errors(sa|sb):
                proofs.append(dict(assignment_a=a,assignment_b=b,positive_a_only=sorted(sa-sb),positive_b_only=sorted(sb-sa),
                    shared_positive_context=sorted(sa&sb),incompatible_union=sorted(sa|sb),violations=model.errors(sa|sb)))
        if not proofs:raise ValueError('NEEDS_COMPATIBILITY_MODEL_REVIEW: conflict lacks two coherent positive assignments')
        kinds=sorted({k for c in cc for k in c['constraint_types']})
        status='EXPLICIT_NEGATIVE_CONFLICT' if 'EXPLICIT_NEGATIVE_CONFLICT' in kinds else 'TRUE_DECISION_PIVOT' if any(k in kinds for k in ('MOTHER_COMPETITION','TRUE_PAIR_RELATION_CONFLICT')) else 'GLOBAL_CONSTRAINT_DECISION'
        components.append(dict(component_id=cid,targets=tt,relation_ids=ids,constraint_ids=[c['constraint_id'] for c in cc],constraint_types=kinds,
            coherent_positive_assignments=sorted(aa),positive_incompatibility_proofs=proofs,decision_required=True,decision_status=status,
            symbolic_semantics='ALL_SUBSETS_SATISFYING_RECORDED_HARD_CONSTRAINTS; UNSELECTED_IS_UNDECIDED',
            reason='COHERENT_POSITIVE_COMMITMENTS_WITH_INCOHERENT_UNION',human_accepted='',canonical_mother='',canonical_hierarchy=''))
        assignments+=list(aa.values())
        for oid in ids:by_relation[oid]=cid
    bycomponent={c['component_id']:c for c in components};gap_targets={g['target'] for g in gaps}
    targets_out=[];dispositions=[];matrix=[]
    for a,b in combinations(sorted(model.rows),2):
        # Full unordered qualified-pair audit; higher-order conditions remain explicit.
        cc=[c['constraint_id'] for c in cs if {a,b}<=set(c['relation_ids'])];errors=model.errors([a,b])
        matrix.append(dict(relation_a=a,relation_b=b,status='MUTUALLY_EXCLUSIVE' if errors else 'CONDITIONALLY_COMPATIBLE' if cc else 'COMPATIBLE_UNDER_CURRENT_HARD_CONTRACTS',
            pair_violations=errors,conditional_constraint_ids=cc,same_commitment=commitment(model.rows[a])==commitment(model.rows[b])))
    for target in model.targets:
        ids=sorted(model.by_target[target]);comps=sorted({by_relation[i] for i in ids if i in by_relation});unique={commitment(model.rows[i]) for i in ids}
        local_cores=[c for c in cs if len({commitment(model.rows[i]) for i in c['relation_ids'] if model.rows[i]['target']==target})>=2]
        target_pivot=bool(local_cores)
        structural='NO_QUALIFIED_RELATION' if not ids else 'QUALIFIED_NONCOMPETING_CANDIDATE' if len(unique)==1 else 'QUALIFIED_COMPATIBLE_SET'
        if comps:
            structural='EXPLICIT_NEGATIVE_CONFLICT' if target_pivot and any('EXPLICIT_NEGATIVE_CONFLICT' in c['constraint_types'] for c in local_cores) else 'TRUE_DECISION_PIVOT' if target_pivot else 'GLOBAL_CONSTRAINT_DECISION'
        status='EVIDENCE_GAP_NOT_STRUCTURAL_DECISION' if ids and not comps and target in gap_targets else structural
        targets_out.append(dict(target=target,target_status=status,structural_status=structural,qualified_relation_ids=ids,
            distinct_commitment_count=len(unique),decision_components=comps,evidence_gap_present=target in gap_targets,
            true_target_decision_pivot=target_pivot,human_review_required=bool(comps),human_accepted='',canonical_mother='',canonical_hierarchy=''))
        for oid in ids:
            r=model.rows[oid];others=[model.rows[i] for i in ids if i!=oid]
            if oid in by_relation:disp='EXPLICIT_CONFLICT' if bycomponent[by_relation[oid]]['decision_status']=='EXPLICIT_NEGATIVE_CONFLICT' else 'PART_OF_TRUE_DECISION'
            elif any(commitment(r)==commitment(o) for o in others):disp='CORROBORATED_DUPLICATE_PATH'
            elif dimension(r)==PARALLEL:disp='ADDITIVE_PARALLEL'
            elif dimension(r)==MOTHER:disp='ORTHOGONAL_COMPATIBLE' if any(dimension(o)==PARALLEL for o in others) else 'NONCOMPETING_MOTHER_CANDIDATE'
            else:disp='OTHER_EXPLAINED_STATUS'
            dispositions.append(dict(relation_id=oid,target=target,disposition=disp,target_status=status,structural_status=structural,
                decision_component=by_relation.get(oid,''),reason='PRESERVED_QUALIFIED_HYPOTHESIS_NOT_AUTOMATIC_ACCEPTANCE',original_relation=r))
    return dict(constraints=cs,components=components,assignments=assignments,targets=targets_out,dispositions=dispositions,matrix=matrix,
        search=dict(strategy='MONOTONE_MINIMAL_CONFLICT_DIRECTED_DELETION',pools_checked=searches,cartesian_products_enumerated=0),
        target_counts={k:sum(t['target_status']==k for t in targets_out) for k in STATUSES},
        disposition_counts={k:sum(d['disposition']==k for d in dispositions) for k in DISPOSITIONS})
