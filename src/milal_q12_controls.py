"""Post-freeze selectors; never imported by configuration/binding extraction."""
import json
from collections import defaultdict
from milal_mfr02r_data import rows,table,digest,encode
from milal_q12_pipeline import indexes,constraints,write
from milal_q1_binding import outcome,identity

SCOPES=('pentateuch','qohelet','lamentations','isaiah')


def controls(source,q1,q11,out,grammar,config):
    freeze=json.loads((out/'blind_freeze.json').read_text())
    if any(digest(out/k)!=h for k,h in freeze['files'].items()):raise ValueError('blind freeze modified')
    registry={r['rule_id']:r for r in grammar['rules']}
    old_numbers={(r['candidate_id'],r['relation']):r for r in rows(q11/'02_q1_1_numbers_missing_control_audit.csv')}
    numbers=[];bosman=[];receipts={};coverage=[]
    old_q1={(r['scope'],r['candidate_id']):r for r in rows(q1/'16_q1_control_fixture_validation.csv')}
    deferred={str(r['binding_evidence']['raw_clause_membership'])
        for r in rows(source/'controls/oosting_control_bindings.csv')}
    for scope in SCOPES:
        inventory=list(rows(q11/(scope+'_source_evidence.csv')))
        original_nodes=list(rows(source/'controls'/(scope+'_fixture_source_clauses.csv')))
        actual={str(r['clause_id']) for r in inventory};expected={str(r['clause_id']) for r in original_nodes}
        if actual!=expected:raise ValueError('fixture identity changed')
        configs,refs,binder=indexes(inventory,grammar);pairs=[];os=[]
        for row in rows(source/'controls'/(scope+'_fixture_relation_checks.csv')):
            sid,tid=str(row['source_clause_id']),str(row['target_clause_id']);pair=row['pair_id']
            matches=[dict(rule_id=rid,relation=registry[rid]['candidate_relation']) for rid in row['rule_ids']
                if registry[rid]['candidate_relation'] in row['relations']]
            result=binder.evaluate(sid,tid,matches,deferred=tid in deferred)
            record=dict(scope=scope,candidate_id=pair,source_id=sid,target_id=tid,original=row,
                q1=old_q1[scope,pair],q12=result,deferred=tid in deferred);pairs.append(record)
            os.extend(outcome(sid,tid,rel) for rel in result['qualified_relations'])
            for relation in row['relations']:
                if [pair,relation] in config['numbers_controls']:
                    numbers.append(dict(candidate_id=pair,relation=relation,source_id=sid,target_id=tid,
                        original_status=old_q1[scope,pair],q11_failed_conditions=old_numbers[pair,relation]['failed_requirement'],
                        q12_source_profile=configs.profiles[sid],q12_target_profile=configs.profiles[tid],
                        configuration_correspondence=result['correspondences'],reference_witnesses=refs.by_target[tid],
                        sb06_sb11_effect=[w for w in result['witnesses'] if w['mechanism'] in ('SB06','SB11')],
                        final_qualification=result['qualification'],relation_retained=relation in result['qualified_relations'],
                        qualified_paths=[p for p in result['qualified_paths'] if p['relation']==relation],
                        human_acceptance='',no_control_specific_rule=True))
        global_result=constraints(os,configs.positions)
        table(out/(scope+'_postfreeze_pair_audit.csv'),pairs)
        table(out/(scope+'_postfreeze_profiles.csv'),configs.profiles.values())
        table(out/(scope+'_postfreeze_units.csv'),configs.configurations.values())
        table(out/(scope+'_postfreeze_references.csv'),refs.witnesses)
        write(out/(scope+'_postfreeze_constraints.json'),global_result)
        coverage.append(dict(scope=scope,clause_count=len(actual),pair_count=len(pairs),
            q1_qualified=sum(bool(p['q1']['qualified_relations']) for p in pairs),
            q12_qualified=sum(bool(p['q12']['qualified_relations']) for p in pairs),qualified_outcomes=len(os)))
        if scope=='pentateuch':
            for n in numbers:n['sb12_effect']=dict(constraint_file=scope+'_postfreeze_constraints.json',positive_binding=False,
                relevant_conflicts=[c for c in global_result['conflicts'] if c['target_clause_id']==n['target_id']])
        if scope=='lamentations':
            for old in rows(q11/'03_q1_1_bosman_unit_reference_audit.csv'):
                sid=str(old['source_clause_id']);targets=list(map(str,old['target_clause_ids']))
                units=configs.configurations[sid]
                bosman.append(dict(source_clause_id=sid,source_unit_candidate_id=old['source_unit_candidate_id'],
                    target_clause_ids=old['target_clause_ids'],frozen_conditional_evidence=old,
                    independent_surface_unit=units,
                    reference_witnesses=[r for t in targets for r in refs.by_target[t]],
                    candidate_antecedents=[a for a in refs.antecedents if a['reference_witness_id'] in
                        {r['reference_witness_id'] for t in targets for r in refs.by_target[t]}],
                    reference_bindings=[r for t in targets for r in refs.bindings(sid,t)],
                    reference_identity_status='UNRESOLVED' if not any(refs.bindings(sid,t) for t in targets) else 'EXACT_NATIVE',
                    human_acceptance='',conditional_graph_used_as_proof=False))
        receipts[scope]=dict(exact_clause_ids=sorted(actual,key=int),expected_clause_ids=sorted(expected,key=int),
            q11_source_sha256=digest(q11/(scope+'_source_evidence.csv')),full_book_analysis=False,
            original_pair_count=len(pairs),generated_new_candidates=0)
    table(out/'13_q12_numbers_postfreeze_controls.csv',numbers)
    table(out/'14_q12_bosman_postfreeze_controls.csv',bosman)
    table(out/'external_fixture_coverage.csv',coverage)
    write(out/'control_receipts.json',receipts)
    return receipts,numbers,bosman


def diagnostics(source,q1,out,configs,refs,metrics,config):
    wanted={tuple(x) for x in config['job_diagnostics']}
    selected={k:r for k,r in configs.rows.items() if (int(r['chapter']),int(r['verse'])) in wanted}
    by_target=defaultdict(list)
    for r in rows(out/'raw_qualification_crosswalk.csv'):
        if r['target_id'] in selected:by_target[r['target_id']].append(r)
    table(out/'job_special_raw_candidates.csv',(r for t in selected for r in by_target[t]))
    text=['# Q1.2 Job post-freeze diagnostics','',
        'Every selected target and raw pair is preserved in job_special_raw_candidates.csv. ',
        'Source IDs resolve through 01 and configuration_units.csv; 03 records all original-relation configuration comparisons.',
        'Reference candidate IDs resolve through 06–07. SB12 conflicts remain conditional, with no canonical hierarchy.','']
    outcomes=list(rows(out/'11_q12_structural_outcome_groups.csv'))
    for tid,r in selected.items():
        text += [f"## Job {r['chapter']}:{r['verse']} — clause {tid}",
            'Source: '+r['surface_hebrew'],
            'Counts: '+encode(metrics['target_counts'].get(tid,{})),
            'Observed profile: '+encode(configs.profiles[tid]),
            'Reference witnesses: '+encode(refs.by_target[tid]),
            'Outcomes: '+encode([o for o in outcomes if o['target']==tid]),'']
    (out/'15_q12_job_special_diagnostics.md').write_text('\n\n'.join(text)+'\n',encoding='utf8',newline='\n')
    old=list(rows(source/'mfr02a_original_decisions.csv'))
    frozen=list(rows(q1/'14_q1_mfr02a_13_case_reaudit.csv'))
    if old!=[r['original_decision'] for r in frozen]:raise ValueError('historical human decisions changed')
    human=[dict(original_decision=r,original_decision_sha256=identity(r),new_human_judgment='') for r in old]
    table(out/'preserved_human_judgments.csv',human)
    return human
