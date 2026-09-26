"""Blind additive qualification over the unchanged frozen candidate universe."""
from collections import Counter,defaultdict
from contextlib import ExitStack
from itertools import zip_longest
from pathlib import Path
from milal_mfr02r_data import rows,table,Table,digest,physical_path,encode
from milal_q1_binding import SourceIndex,identity,outcome,pivot,qualify
from milal_mfr02r_graph import analyze_graph
from milal_q12_profiles import ConfigurationIndex
from milal_q12_references import ReferenceIndex
from milal_q12_binding import BindingIndex


def write(path,value):
    Path(path).write_text(encode(value)+'\n',encoding='utf8',newline='\n')


def indexes(inventory,grammar):
    lex=grammar['lexicons'];configs=ConfigurationIndex(inventory,lex)
    refs=ReferenceIndex(configs)
    native=SourceIndex(inventory,lex['subordinate_rela'],lex['speech'])
    return configs,refs,BindingIndex(configs,refs,native)


def constraints(outcomes,positions):
    edges=[dict(edge_id=o['structural_outcome_group_id'],source=o['source_or_peer'],
                target=o['target'],relation=o['relation_type']) for o in outcomes]
    graph=analyze_graph(edges,positions)
    return dict(input_outcome_ids=sorted(e['edge_id'] for e in edges),
        output_outcome_ids=sorted(e['edge_id'] for e in edges),positive_binding=False,
        chosen_mother='',canonical_hierarchy='',**graph)


def blind(source,q1,out,grammar):
    job=source/'blind/job';inventory=list(rows(job/'02_clause_feature_inventory.csv'))
    if {r['book'] for r in inventory}!={'Iob'}:raise ValueError('primary scope must be Job')
    configs,refs,binder=indexes(inventory,grammar)
    table(out/'01_q12_configuration_profiles.csv',configs.profiles.values())
    table(out/'02_q12_configuration_families.csv',configs.families.values())
    table(out/'configuration_units.csv',configs.configurations.values())
    table(out/'06_q12_reference_witnesses.csv',refs.witnesses,['target_clause_id','target_reference_form','person','gender','number',
        'suffix_pronoun_type','explicit_lexical_form','candidate_antecedent_ids','antecedent_basis','candidate_count',
        'reference_status','referential_identity','exact_antecedent_id','provenance','reference_witness_id'])
    table(out/'07_q12_reference_candidate_antecedents.csv',refs.antecedents,['reference_witness_id','antecedent_id','clause_id',
        'word_node','phrase_node','grammatical_role','lex','png','antecedent_basis','native_reference_edges'])
    deferred={str(r['binding_evidence']['raw_clause_membership']) for r in rows(job/'clause_internal_binding_candidates.csv')}
    raw_hash=digest(physical_path(job/'09_candidate_evidence_matrix.csv'))
    counts=Counter();mechanisms=Counter();used_mechanisms=Counter();by_target=defaultdict(Counter)
    outcomes={};provenance=defaultdict(list);errors=0;positive_checks=[];reference_bindings=[]
    with ExitStack() as stack:
        def dest(name,fields):return stack.enter_context(Table(out/name,fields))
        pair_fields=['candidate_id','source_id','target_id','q1_qualification','qualification','qualified_relations',
            'qualified_paths','qualification_reason','disqualification_reason','correspondence_ids','reference_witness_ids','deferred']
        allpairs=dest('raw_qualification_crosswalk.csv',pair_fields+['raw_row_sha256','raw_table_sha256'])
        qualified=dest('10_q12_qualified_relation_universe.csv',pair_fields)
        correspond=dest('03_q12_configuration_correspondence.csv',['candidate_id','correspondence_id','record'])
        sb06=dest('04_q12_sb06_qualification.csv',['candidate_id','witness','qualified_paths'])
        sb11=dest('05_q12_sb11_parallel_configuration.csv',['candidate_id','witness','qualified_paths'])
        reft=dest('08_q12_sb02_sb03_sb10_qualification.csv',['candidate_id','witness','qualified_paths'])
        witnesses=dest('source_binding_witnesses.csv',['candidate_id','witness','qualified_paths'])
        streams=[rows(job/'09_candidate_evidence_matrix.csv'),rows(job/'08_relation_rule_matches.csv'),
            rows(q1/'03_q1_pair_qualification.csv'),rows(q1/'02_q1_source_binding_crosswalk.csv')]
        for raw,match,old,cross in zip_longest(*streams):
            if any(x is None for x in (raw,match,old,cross)):raise ValueError('raw streams differ')
            sid,tid=str(raw['candidate_clause_id']),str(raw['target_clause_id']);pair=raw['pair_id'];rh=identity(raw)
            if not (pair==match['pair_id']==old['candidate_id']==cross['candidate_id'] and
                    (sid,tid)==(cross['source_id'],cross['target_id'])==(old['source_id'],old['target_id']) and
                    rh==cross['raw_row_sha256'] and raw_hash==cross['raw_table_sha256']):
                raise ValueError('exact frozen raw crosswalk mismatch')
            result=binder.evaluate(sid,tid,match['matches'],tid in deferred) if match['matches'] else dict(
                **qualify(sid,tid,[],[],deferred=tid in deferred),witnesses=[],correspondences=[],reference_bindings=[])
            record=dict(candidate_id=pair,source_id=sid,target_id=tid,q1_qualification=old['relation_candidate_qualification'],
                **{k:result[k] for k in ('qualification','qualified_relations','qualified_paths','qualification_reason','disqualification_reason')},
                correspondence_ids=[c['correspondence_id'] for c in result['correspondences']],
                reference_witness_ids=[r['reference_witness']['reference_witness_id'] for r in result['reference_bindings']],deferred=tid in deferred)
            allpairs.write(dict(**record,raw_row_sha256=rh,raw_table_sha256=raw_hash))
            counts['raw']+=1;counts[result['qualification']]+=1;by_target[tid]['raw']+=1
            if old['qualified_relations']:counts['q1_qualified']+=1;by_target[tid]['q1_qualified']+=1
            if match['matches']:counts['original_relation_pairs']+=1
            if result['qualified_paths']:qualified.write(record);counts['qualified']+=1;by_target[tid]['qualified']+=1
            for c in result['correspondences']:
                correspond.write(dict(candidate_id=pair,correspondence_id=c['correspondence_id'],record=c))
                counts['correspondences']+=1
                if c['positive_source_binding']:positive_checks.append(c);counts['positive_configuration_witnesses']+=1
            for w in result['witnesses']:
                paths=[p for p in result['qualified_paths'] if p['witness_id']==w['witness_id']]
                row=dict(candidate_id=pair,witness=w,qualified_paths=paths);witnesses.write(row)
                mechanisms[w['mechanism']]+=1
                if paths:used_mechanisms[w['mechanism']]+=1
                if w['mechanism']=='SB06':sb06.write(row)
                elif w['mechanism']=='SB11':sb11.write(row)
                elif w['mechanism'] in ('SB02','SB03','SB10'):reft.write(row)
            reference_bindings.extend(result['reference_bindings'])
            for rel in result['qualified_relations']:
                o=outcome(sid,tid,rel);oid=o['structural_outcome_group_id'];outcomes[oid]=o
                provenance[oid].extend(dict(candidate_id=pair,**p) for p in result['qualified_paths'] if p['relation']==rel)
            if counts['raw']%100000==0:print('Q1.2 blind pairs',counts['raw'],flush=True)
    os=[dict(**o,provenance_paths=provenance[k]) for k,o in sorted(outcomes.items())]
    table(out/'11_q12_structural_outcome_groups.csv',os)
    global_result=constraints(os,configs.positions)
    table(out/'09_q12_sb12_global_constraints.csv',[dict(mechanism='SB12',constraint_result=global_result)])
    members={n for r in global_result['components'] for n in r['affected_clauses']}
    ots=defaultdict(list)
    for o in os:ots[o['target']].append(o)
    pivots=[pivot(t,ots[t],t in members) for t in configs.order]
    table(out/'12_q12_variant_pivots.csv',pivots)
    counts.update(profiles=len(configs.profiles),families=len(configs.families),configurations=len(configs.configurations),
        reference_witnesses=len(refs.witnesses),reference_antecedents=len(refs.antecedents),outcome_groups=len(os),
        variant_members=len(members),variant_pivots=sum(r['status']=='VARIANT_DECISION_PIVOT' for r in pivots))
    for n in (0,1,2):counts['targets_'+str(n)+('_plus' if n==2 else '')]=sum(len(ots[t])>=2 if n==2 else len(ots[t])==n for t in configs.order)
    metrics=dict(counts=dict(counts),mechanism_witness_counts=mechanisms,mechanism_qualified_witness_counts=used_mechanisms,
        reference_status_counts=Counter(r['reference_status'] for r in refs.witnesses),target_counts=by_target,
        analysis_scope='JOB',raw_hash=raw_hash,raw_crosswalk_errors=errors)
    write(out/'blind_metrics.json',metrics)
    write(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        controls_loaded=False,human_judgments_loaded=False,analysis_scope='JOB'))
    return metrics,configs,refs,positive_checks,reference_bindings,global_result
