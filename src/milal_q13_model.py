"""Orthogonal, symbolic assignments over existing qualified relation outcomes.

No source-binding extraction, corpus locations or historical judgments enter
this module. All explicit instances are feasibility witnesses, not selections.
"""
from collections import defaultdict
from itertools import combinations
from milal_q1_binding import identity
from milal_mfr02r_graph import validate_variant,Union

MOTHER='MOTHER_RELATION_DIMENSION'
PARALLEL='PARALLEL_RELATION_DIMENSION'
OVERLAY='NON_HIERARCHICAL_TYPED_RELATION_DIMENSION'


def dimension(row):
    typ=row['relation_type']
    if typ=='HYPOTACTIC':return MOTHER
    if typ=='PARATACTIC':return PARALLEL
    if typ=='EXCLUDED' and row.get('excluded_outcome_id') and row.get('constraint_provenance'):
        return 'EXPLICIT_CONSTRAINED_EXCLUSION'
    if row.get('non_hierarchical') is True and typ!='EXCLUDED':return OVERLAY
    raise ValueError('unknown relation dimension: '+typ)


def commitment(row):
    typ=row['relation_type'];s,t=row['source_or_peer'],row['target']
    if typ=='PARATACTIC':return (typ,*sorted((s,t)))
    if typ=='EXCLUDED':return (typ,row['excluded_outcome_id'])
    return (typ,s,t)


class AssignmentModel:
    def __init__(self,outcomes,targets=None,constraints=()):
        self.rows={r['structural_outcome_group_id']:dict(r) for r in outcomes}
        if len(self.rows)!=len(outcomes):raise ValueError('duplicate outcome ID')
        self.by_target=defaultdict(list)
        for oid,r in self.rows.items():
            for key in ('target','source_or_peer','relation_type','provenance_paths'):
                if key not in r:raise ValueError('missing outcome field '+key)
            if not isinstance(r['target'],str) or not isinstance(r['source_or_peer'],str):raise ValueError('source IDs must be exact strings')
            dimension(r)
            if r['relation_type']=='EXCLUDED' and r['excluded_outcome_id'] not in self.rows:raise ValueError('excluded outcome missing')
            self.by_target[r['target']].append(oid)
        self.targets=sorted(set(targets or ())|set(self.by_target))
        self.constraints=list(constraints);self.validation_cache={};self.search_calls=0
        for c in self.constraints:
            if c['kind']!='FORBIDDEN_COMBINATION' or not c['constraint_provenance'] or not c['independent']:
                raise ValueError('unverified global constraint')
            if len(set(c['outcome_ids']))<2 or not set(c['outcome_ids'])<=set(self.rows):raise ValueError('global constraint endpoints invalid')
        for oid in self.rows:
            if self.errors([oid]):raise ValueError('qualified outcome has no coherent singleton: '+oid)

    def errors(self,selected):
        key=tuple(sorted(set(selected)))
        if key in self.validation_cache:return self.validation_cache[key]
        if not set(key)<=set(self.rows):raise ValueError('unqualified relation in assignment')
        edges=[];errors=[]
        for oid in key:
            r=self.rows[oid]
            if dimension(r) in (MOTHER,PARALLEL):
                edges.append(dict(source=r['source_or_peer'],target=r['target'],relation=r['relation_type']))
            if r['relation_type']=='EXCLUDED' and r['excluded_outcome_id'] in key:
                errors.append('EXPLICIT_EXCLUSION_VS_POSITIVE_RELATION')
        errors+=validate_variant(edges)
        errors += ['GLOBAL_CONSTRAINT:'+c['constraint_id'] for c in self.constraints if set(c['outcome_ids'])<=set(key)]
        self.validation_cache[key]=sorted(set(errors));return self.validation_cache[key]

    def assignment(self,target,selected):
        selected=sorted(set(selected));errors=self.errors(selected)
        if errors:raise ValueError('incoherent assignment '+repr(errors))
        local=[i for i in selected if self.rows[i]['target']==target]
        mothers=defaultdict(list);peers=defaultdict(list);overlays=[];exclusions=[]
        for oid in local:
            r=self.rows[oid];d=dimension(r)
            if d==MOTHER:mothers[r['source_or_peer']].append(oid)
            elif d==PARALLEL:peers[r['source_or_peer']].append(oid)
            elif d==OVERLAY:overlays.append(oid)
            else:exclusions.append(oid)
        if len(mothers)>1:raise ValueError('mother slot violation')
        a=dict(target_id=target,mother_assignment=next((dict(source_id=s,outcome_ids=v) for s,v in sorted(mothers.items())),None),
            parallel_peer_assignments=[dict(peer_id=s,outcome_ids=v) for s,v in sorted(peers.items())],
            overlay_relations=overlays,explicit_exclusions=exclusions,
            unresolved_relations=sorted(set(self.by_target[target])-set(local)),
            selected_outcome_ids=selected,supporting_selected_context=sorted(set(selected)-set(local)),
            unselected_semantics='UNDECIDED',coherent=True,accepted=False,canonical_mother='',canonical_hierarchy='')
        a['assignment_id']='QA-'+identity(a);return a

    def minimal_conflict(self,selected):
        current=set(selected)
        if not self.errors(current):return None
        for oid in sorted(current):
            if self.errors(current-{oid}):current.remove(oid)
        return frozenset(current)

    def incompatible_witness(self,a,b):
        """Conflict-directed search for a minimal forbidden set containing both.

        Each branch removes an element of an irrelevant conflict core. This
        searches constraints, not the Cartesian product of UNDECIDED choices.
        Monotone structural constraints make core minimization and pruning exact.
        """
        if commitment(self.rows[a])==commitment(self.rows[b]):return None
        visited=set()
        def search(pool):
            pool=frozenset(pool)
            if pool in visited:return None
            visited.add(pool);self.search_calls+=1
            core=self.minimal_conflict(pool)
            if core is None:return None
            if {a,b}<=core:return core
            for other in sorted(core-{a,b}):
                found=search(pool-{other})
                if found is not None:return found
            return None
        if self.errors([a,b]):core=frozenset((a,b))
        else:core=search(self.rows)
        if core is None:return None
        context=sorted(core-{a,b});target=self.rows[a]['target']
        return dict(outcome_a=a,outcome_b=b,shared_positive_context=context,
            assignment_a=self.assignment(target,core-{b}),assignment_b=self.assignment(target,core-{a}),
            incompatible_union=sorted(core),violations=self.errors(core),
            constraint_provenance=self.provenance(core),
            proof='BOTH_ASSIGNMENTS_COHERENT; MINIMAL_UNION_INCOHERENT; BOTH_TARGET_COMMITMENTS_ESSENTIAL')

    def provenance(self,selected):
        result=[dict(source='FROZEN_STRUCTURAL_CONSTRAINT_VALIDATOR',constraint=x)
            for x in self.errors(selected) if not x.startswith('GLOBAL_CONSTRAINT:')]
        result += [dict(constraint_id=c['constraint_id'],source=c['constraint_provenance'])
            for c in self.constraints if set(c['outcome_ids'])<=set(selected)]
        return result

    def compatibility(self,a,b):
        ra,rb=self.rows[a],self.rows[b];da,db=dimension(ra),dimension(rb)
        same=commitment(ra)==commitment(rb);errors=self.errors([a,b]);proof=None
        if same:
            status='COMPATIBLE';category='CORROBORATED_RELATIONS';reason='SAME_STRUCTURAL_COMMITMENT_DIFFERENT_PROVENANCE'
        elif errors:
            status='MUTUALLY_EXCLUSIVE'
            if da==db==MOTHER and ra['target']==rb['target']:
                category='TRUE_MOTHER_COMPETITION';reason='DISTINCT_MOTHERS_CONSUME_THE_SAME_MOTHER_SLOT'
            elif (set((ra['source_or_peer'],ra['target']))==set((rb['source_or_peer'],rb['target'])) and
                  {da,db}=={MOTHER,PARALLEL}) or 'EXPLICIT_EXCLUSION_VS_POSITIVE_RELATION' in errors:
                category='TRUE_PAIR_RELATION_CONFLICT';reason='SAME_PAIR_STRICT_VS_EQUAL_OR_EXPLICIT_EXCLUSION'
            else:category='GLOBAL_STRUCTURAL_CONFLICT';reason='EXPLICIT_STRUCTURAL_CONSTRAINT_VIOLATION'
        elif da==db==PARALLEL:
            status='COMPATIBLE';category='ADDITIVE_PARALLEL_RELATIONS';reason='PARALLEL_PEERS_ADDITIVE'
        elif {da,db}=={MOTHER,PARALLEL}:
            status='CONDITIONALLY_COMPATIBLE';category='ORTHOGONAL_RELATIONS';reason='POTENTIALLY_COMPATIBLE_ORTHOGONAL_RELATIONS'
        else:
            status='COMPATIBLE';category='CORROBORATED_RELATIONS';reason='NON_HIERARCHICAL_TYPED_RELATIONS_DO_NOT_CONSUME_MOTHER_SLOT'
        if ra['target']==rb['target'] and not same:
            proof=self.incompatible_witness(a,b)
            if proof and proof['shared_positive_context']:
                status='CONDITIONALLY_COMPATIBLE';category='GLOBAL_STRUCTURAL_CONFLICT'
                reason='COEXIST_WITHOUT_CONTEXT; INCOMPATIBLE_UNDER_RECORDED_SHARED_POSITIVE_CONTEXT'
        return dict(target_id=ra['target'],relation_outcome_a=a,relation_outcome_b=b,dimension_a=da,dimension_b=db,
            compatibility_status=status,compatibility_reason=reason,classification=category,
            parallel_level_constraint='INCOMPATIBLE' if errors else 'UNRESOLVED' if PARALLEL in (da,db) else 'COMPATIBLE_CANDIDATE',
            level_status='PARALLEL_LEVEL_COMPATIBILITY_UNRESOLVED' if PARALLEL in (da,db) and not errors else '',
            level_compatibility_classification='UNRESOLVED_COMPATIBILITY' if PARALLEL in (da,db) and not errors else '',
            conditional_context_constraint='INCOMPATIBLE' if proof else '',
            constraint_provenance=self.provenance([a,b]),positive_incompatibility_witness=proof,
            human_review_required=proof is not None)

    def analyze(self):
        dimensions=[dict(outcome_id=oid,target_id=r['target'],source_or_peer=r['source_or_peer'],
            relation_type=r['relation_type'],dimension=dimension(r),mother_slot_consumed=dimension(r)==MOTHER,
            structural_commitment=commitment(r),q12_outcome_sha256=identity(r),original_outcome=r)
            for oid,r in sorted(self.rows.items())]
        matrix=[];assignments=[];peer_sets=[];mother_sets=[];pivots=[];orthogonal=[];components=[]
        pool_errors=self.errors(self.rows);sample_core=self.minimal_conflict(self.rows) if pool_errors else None
        nodes={n for r in self.rows.values() for n in (r['source_or_peer'],r['target'])};union=Union(nodes)
        for r in self.rows.values():union.join(r['source_or_peer'],r['target'])
        grouped=defaultdict(list)
        for oid,r in self.rows.items():grouped[union.find(r['target'])].append(oid)
        for _,ids in sorted(grouped.items()):
            components.append(dict(component_id='QC-'+identity(sorted(ids)),outcome_ids=sorted(ids),
                representation='SYMBOLIC_CONSTRAINT_COMPONENT',selection_semantics='ANY_SUBSET_SATISFYING_CONSTRAINTS; UNSELECTED_IS_UNDECIDED',
                laws=['ONE_HYPOTACTIC_MOTHER','MULTIPLE_PARALLEL_PEERS','STRICT_VS_EQUAL_LEVEL','ACYCLIC_AFTER_PARALLEL_CONTRACTION','EXPLICIT_GLOBAL_FORBIDDEN_COMBINATIONS'],
                accepted_variant='',positive_relations_created=0))
        for target in self.targets:
            ids=sorted(self.by_target[target]);local=[self.compatibility(a,b) for a,b in combinations(ids,2)];matrix+=local
            mothers=sorted({self.rows[i]['source_or_peer'] for i in ids if dimension(self.rows[i])==MOTHER})
            peers=sorted({self.rows[i]['source_or_peer'] for i in ids if dimension(self.rows[i])==PARALLEL})
            peer_ids=[i for i in ids if dimension(self.rows[i])==PARALLEL]
            can_combine=not self.errors(ids);combined=self.assignment(target,ids) if can_combine else None
            proofs=[r['positive_incompatibility_witness'] for r in local if r['positive_incompatibility_witness']]
            symbolic=dict(mother_options=[i for i in ids if dimension(self.rows[i])==MOTHER],
                parallel_options=peer_ids,overlay_options=[i for i in ids if dimension(self.rows[i])==OVERLAY],
                explicit_exclusion_options=[i for i in ids if self.rows[i]['relation_type']=='EXCLUDED'],
                mother_cardinality='ZERO_OR_ONE_DISTINCT_MOTHER',parallel_cardinality='ZERO_OR_MANY',
                unselected_semantics='UNDECIDED',requires_global_constraints=True)
            assignments.append(dict(target_id=target,symbolic_assignment=symbolic,coherent_combined_assignment=combined,
                combined_assignment_errors=self.errors(ids),conflict_assignment_witnesses=proofs,
                canonical_mother='',canonical_hierarchy='',human_accepted=''))
            peer_sets.append(dict(target_id=target,peer_ids=peers,outcome_ids=peer_ids,peer_pair_conflict=any(
                r['positive_incompatibility_witness'] for r in local if r['dimension_a']==r['dimension_b']==PARALLEL),
                all_peers_can_coexist_without_extra_context=not self.errors(peer_ids),
                parallel_level_constraint='UNRESOLVED' if peers else 'COMPATIBLE_CANDIDATE',
                level_compatibility_classification='UNRESOLVED_COMPATIBILITY' if peers else '',
                shared_mother_assigned=False,peer_count=len(peers),automatic_review_from_multiplicity=False))
            mother_sets.append(dict(target_id=target,mother_ids=mothers,outcome_ids=[i for i in ids if dimension(self.rows[i])==MOTHER],
                classification='Q13_MOTHER_COMPETITION' if len(mothers)>1 else 'NO_MOTHER_COMPETITION',chosen_mother=''))
            if mothers and peers:orthogonal.append(dict(target_id=target,mother_ids=mothers,peer_ids=peers,
                combined_assignment=combined,parallel_level_constraint='UNRESOLVED',conflict_proofs=proofs,
                classification='ORTHOGONAL_RELATIONS',accepted=''))
            pivots.append(dict(target_id=target,q13_status='VARIANT_DECISION_PIVOT' if proofs else 'NON_PIVOT',
                human_review_required=bool(proofs),conflict_categories=sorted({r['classification'] for r in local if r['positive_incompatibility_witness']}),
                positive_incompatibility_witnesses=proofs,reason='POSITIVELY_INCOMPATIBLE_COHERENT_ASSIGNMENTS' if proofs else
                    'NO_INCOMPATIBLE_POSITIVE_TARGET_COMMITMENTS; MULTIPLICITY_OR_UNDECIDED_IS_NOT_CONFLICT',
                canonical_mother='',canonical_hierarchy=''))
        # Unordered pair checking is global, without creating inverse edges.
        same_pair=[]
        for a,b in combinations(sorted(self.rows),2):
            ra,rb=self.rows[a],self.rows[b]
            if {dimension(ra),dimension(rb)}=={MOTHER,PARALLEL} and {ra['source_or_peer'],ra['target']}=={rb['source_or_peer'],rb['target']}:
                same_pair.append(dict(outcome_a=a,outcome_b=b,affected_targets=sorted({ra['target'],rb['target']}),
                    classification='Q13_SAME_PAIR_RELATION_CONFLICT',violations=self.errors([a,b]),constraint_provenance=self.provenance([a,b])))
        return dict(dimensions=dimensions,matrix=matrix,assignments=assignments,peer_sets=peer_sets,mother_sets=mother_sets,
            mother_competitions=[r for r in mother_sets if len(r['mother_ids'])>1],same_pair_conflicts=same_pair,
            additive=[r for r in peer_sets if r['peer_count']>1 and r['all_peers_can_coexist_without_extra_context']],orthogonal=orthogonal,pivots=pivots,components=components,
            global_audit=dict(whole_pool_coherent=not pool_errors,whole_pool_errors=pool_errors,
                one_minimal_global_conflict=sorted(sample_core) if sample_core else [],
                constraint_rows=self.constraints,source_outcome_ids=sorted(self.rows),output_outcome_ids=sorted(self.rows),
                positive_relations_created=0,cartesian_products_enumerated=0,conflict_directed_search_calls=self.search_calls))
