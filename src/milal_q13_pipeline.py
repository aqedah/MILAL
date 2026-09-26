"""Read frozen outcomes; publish compatibility without rerunning qualification."""
import json
import shutil
from collections import Counter
from itertools import combinations
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,physical_path,encode
from milal_q13_model import AssignmentModel,MOTHER,PARALLEL,OVERLAY

FILES={
 'dimensions':'01_q13_relation_dimensions.csv','matrix':'02_q13_relation_compatibility_matrix.csv',
 'peer_sets':'03_q13_parallel_peer_sets.csv','mother_sets':'04_q13_mother_candidate_sets.csv',
 'mother_competitions':'05_q13_mother_competitions.csv','same_pair_conflicts':'06_q13_same_pair_relation_conflicts.csv',
 'assignments':'07_q13_coherent_assignments.csv','additive':'08_q13_additive_parallel_relations.csv',
 'orthogonal':'09_q13_orthogonal_relation_sets.csv','pivots':'10_q13_true_decision_pivots.csv'}
PRESERVE={'10_q12_qualified_relation_universe.csv':'preserved_q12_qualified_relations.csv',
 '11_q12_structural_outcome_groups.csv':'preserved_q12_outcome_groups.csv',
 '12_q12_variant_pivots.csv':'preserved_q12_pivots.csv',
 'preserved_human_judgments.csv':'preserved_human_judgments.csv'}


def write(path,obj):
    path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8',newline='\n')


def sb12_constraints(result,outcomes):
    ids={r['structural_outcome_group_id'] for r in outcomes}
    if set(result['input_outcome_ids'])!=ids or set(result['output_outcome_ids'])!=ids or result['positive_binding']:
        raise ValueError('SB12 must only constrain existing outcomes')
    constraints=[]
    for c in result['conflicts']:
        if not set(c['edge_ids'])<=ids:raise ValueError('SB12 unknown endpoint')
        if c['severity']=='SOFT_CONFLICT':continue
        if c['severity']!='HARD_CONFLICT' or c['kind'] not in ('AT_MOST_ONE_MOTHER','STRICT_VS_EQUAL_LEVEL'):
            raise ValueError('unsupported SB12 hard constraint schema')
        for index,pair in enumerate(combinations(sorted(c['edge_ids']),2)):
            constraints.append(dict(kind='FORBIDDEN_COMBINATION',constraint_id=c['conflict_id']+':'+str(index),
                outcome_ids=list(pair),constraint_provenance=c,independent=True))
    return constraints


def verify_qualification(qualified,outcomes):
    expected={}
    for q in qualified:
        for rel in q['qualified_relations']:
            key=(q['source_id'],q['target_id'],rel)
            paths=[dict(p,candidate_id=q['candidate_id']) for p in q['qualified_paths'] if p['relation']==rel]
            expected.setdefault(key,[]).extend(paths)
    actual={}
    for o in outcomes:
        key=(o['source_or_peer'],o['target'],o['relation_type'])
        actual.setdefault(key,[]).extend(o['provenance_paths'])
    normalize=lambda x:{k:sorted(set(map(encode,v))) for k,v in x.items()}
    if normalize(expected)!=normalize(actual):raise ValueError('qualified evidence/outcome provenance mismatch')


def blind(source,out):
    source,out=Path(source),Path(out)
    qualified=list(rows(source/'10_q12_qualified_relation_universe.csv'))
    outcomes=list(rows(source/'11_q12_structural_outcome_groups.csv'))
    verify_qualification(qualified,outcomes)
    targets=[r['clause_id'] for r in rows(source/'01_q12_configuration_profiles.csv')]
    if len(targets)!=len(set(targets)):raise ValueError('duplicate source target')
    if not {n for r in outcomes for n in (r['target'],r['source_or_peer'])}<=set(targets):
        raise ValueError('outcome outside frozen Job source universe')
    sbrows=list(rows(source/'09_q12_sb12_global_constraints.csv'))
    if len(sbrows)!=1 or sbrows[0]['mechanism']!='SB12':raise ValueError('SB12 schema')
    sb=sbrows[0]['constraint_result']
    model=AssignmentModel(outcomes,targets,sb12_constraints(sb,outcomes));result=model.analyze()
    for key,name in FILES.items():
        empty_fields={
            'same_pair_conflicts':['outcome_a','outcome_b','affected_targets','classification','violations','constraint_provenance'],
            'mother_competitions':['target_id','mother_ids','outcome_ids','classification','chosen_mother'],
            'additive':['target_id','peer_ids','outcome_ids','peer_pair_conflict','all_peers_can_coexist_without_extra_context',
                'parallel_level_constraint','level_compatibility_classification','shared_mother_assigned','peer_count','automatic_review_from_multiplicity'],
            'orthogonal':['target_id','mother_ids','peer_ids','combined_assignment','parallel_level_constraint','conflict_proofs','classification','accepted']}
        fallback=empty_fields.get(key,['target_id','classification'])
        table(out/name,result[key],fields=None if result[key] else fallback)
    write(out/'symbolic_components.json',result['components'])
    write(out/'global_constraint_audit.json',dict(result['global_audit'],original_sb12=sb))
    # Actual observed count, without rewriting the million-row source table.
    raw_count=sum(1 for _ in rows(source/'raw_qualification_crosswalk.csv'))
    dims=Counter(r['dimension'] for r in result['dimensions'])
    true=[r for r in result['pivots'] if r['human_review_required']]
    counts=dict(raw=raw_count,qualified=len(qualified),outcomes=len(outcomes),targets=len(targets),
        mother_relations=dims[MOTHER],parallel_relations=dims[PARALLEL],overlay_relations=dims[OVERLAY],
        targets_with_multiple_qualified=sum(len(v)>1 for v in model.by_target.values()),
        targets_with_multiple_mothers=sum(len(r['mother_ids'])>1 for r in result['mother_sets']),
        targets_with_multiple_peers=sum(r['peer_count']>1 for r in result['peer_sets']),
        additive_parallel_sets=len(result['additive']),orthogonal_sets=len(result['orthogonal']),
        mother_competitions=len(result['mother_competitions']),same_pair_conflicts=len(result['same_pair_conflicts']),
        unresolved_level_compatibility=sum(r['parallel_level_constraint']=='UNRESOLVED' for r in result['peer_sets']),
        unresolved_multi_relation_sets=len({r['target_id'] for r in result['matrix'] if r['parallel_level_constraint']=='UNRESOLVED'}),
        true_mother_competition_targets=sum('TRUE_MOTHER_COMPETITION' in r['conflict_categories'] for r in true),
        true_pair_conflict_targets=sum('TRUE_PAIR_RELATION_CONFLICT' in r['conflict_categories'] for r in true),
        global_structural_conflict_targets=sum('GLOBAL_STRUCTURAL_CONFLICT' in r['conflict_categories'] for r in true),
        true_pivots=len(true),symbolic_components=len(result['components']))
    write(out/'blind_freeze.json',{p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()})
    return model,result,counts


def postfreeze(source,out,model,result,counts,config):
    old=[r for r in rows(source/'12_q12_variant_pivots.csv') if r['status']=='VARIANT_DECISION_PIVOT']
    if {r['target_id'] for r in old}!=set(config['previous_pivot_targets']):raise ValueError('previous pivot identities mismatch')
    indexed={r['target_id']:r for r in result['pivots']};assign={r['target_id']:r for r in result['assignments']}
    reaudit=[]
    for prior in old:
        target=prior['target_id'];pairs=[r for r in result['matrix'] if r['target_id']==target]
        reaudit.append(dict(target_id=target,prior_pivot=prior,prior_outcomes=[model.rows[i] for i in model.by_target[target]],
            relation_dimensions=sorted({r['dimension_a'] for r in pairs}|{r['dimension_b'] for r in pairs}),
            compatibility=pairs,combined_assignment=assign[target]['coherent_combined_assignment'],
            q13_status=indexed[target]['q13_status'],true_pivot=indexed[target]['human_review_required'],
            reason=indexed[target]['reason']))
    table(out/'11_q13_q12_seven_pivot_reaudit.csv',reaudit,fields=None if reaudit else ['target_id','q13_status'])
    diagnostics=[]
    for kind,d in config['diagnostics'].items():
        target=d['target'];desired=([(d['mother'],'HYPOTACTIC'),(d['peer'],'PARATACTIC')] if kind=='mother_parallel' else [(p,'PARATACTIC') for p in d['peers']])
        ids=[]
        for source_id,rel in desired:
            found=[i for i in model.by_target[target] if model.rows[i]['source_or_peer']==source_id and model.rows[i]['relation_type']==rel]
            if not found:raise ValueError('post-freeze diagnostic source identity missing')
            ids.extend(found)
        errors=model.errors(ids)
        diagnostics.append(dict(kind=kind,target_id=target,outcome_ids=sorted(ids),representable=not errors,
            assignment=None if errors else model.assignment(target,ids),violations=errors,human_accepted=False))
    (out/'12_q13_job_2_1_diagnostic.md').write_text('# Post-freeze Job 2:1 diagnostics\n\nFeasibility witnesses only; no human acceptance or shared-mother assignment.\n\n'+
        '\n\n'.join('## '+r['target_id']+'\n\n```json\n'+json.dumps(r,ensure_ascii=False,indent=2)+'\n```' for r in diagnostics)+'\n',encoding='utf8',newline='\n')
    preserved={}
    for src,dst in PRESERVE.items():
        original=physical_path(source/src);dest=out/(dst+'.gz' if original.suffix=='.gz' else dst)
        shutil.copyfile(original,dest);preserved[src]=dict(source_sha256=digest(original),output=dest.name,output_sha256=digest(dest))
    # Large original tables remain losslessly available in the mandatory verified upstream archive.
    receipt={r['path']:r['sha256'] for r in rows(source/'99_manifest_sha256.csv')}
    write(out/'source_preservation_receipt.json',dict(upstream_members=receipt,preserved=preserved,
        raw_storage='VERIFIED_FROZEN_UPSTREAM_ARCHIVE',input_zip_sha256=config.get('input_zip_sha256','SYNTHETIC')))
    counts.update(previous_pivots=len(old),human=sum(1 for _ in rows(source/'preserved_human_judgments.csv')))
    write(out/'13_q13_assignment_statistics.json',counts)
    write(out/'postfreeze_diagnostics.json',diagnostics)
    report=['# Q1.3 method report','GENERALIZED_FOR_MILAL: orthogonal compatibility over unchanged Q1.2 evidence.',
        'HYPOTACTIC consumes at most one distinct mother slot. Multiple PARATACTIC peers are additive; overlays consume no mother slot.',
        'UNSELECTED = UNDECIDED. A pivot requires two coherent assignments with positively incompatible commitments for this target. Global differences elsewhere are not target pivots.',
        'Global conflict proofs record a minimal incompatible union and common positive context. A conditionally incompatible pair may coexist when that context is undecided.',
        'Parallel equal-level constraints apply only within selected assignments. Final level/mother compatibility remains unresolved; no canonical level, shared mother or hierarchy is chosen.',
        'Existing SB12 soft competing-chain notices are retained, not promoted to prohibitions. Only explicit hard constraints and frozen structural laws restrict assignments.',
        'All source outcomes and provenance paths remain intact. Symbolic component domains represent all constrained subsets; no Cartesian enumeration of undecided selections is performed.',
        '```json\n'+json.dumps(counts,indent=2)+'\n```',
        '## Previous pivots']
    report += [r['target_id']+': '+r['q13_status']+'; '+', '.join(sorted({p['classification'] for p in r['compatibility']})) for r in reaudit]
    report+=['Q1.2 reference and unit-boundary limitations remain. No adapter change, new binding, new human judgment, corpus discovery or external fixture analysis was performed.',
        'READY_FOR_MFR_0_2R_Q1_4 is technical compatibility readiness, conditional on release gates. It is not human structural acceptance. Q1.4 requires separate authorization.']
    (out/'14_q13_method_report.md').write_text('\n\n'.join(report)+'\n',encoding='utf8',newline='\n')
    (out/'15_q13_next_scope.md').write_text('# Next scope\n\nREADY_FOR_MFR_0_2R_Q1_4, conditional on all release gates.\n\nDo not start Q1.4 automatically. Independent composite surface-unit and cross-family correspondence review remains.\n',encoding='utf8',newline='\n')
    return reaudit,diagnostics,preserved
