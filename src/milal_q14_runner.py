"""Q1.4 empirical execution and independent release over verified frozen inputs."""
import argparse
import json
import ast
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,physical_path,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_io import verify_archive
from milal_q1_runner import verified_input
from milal_q13_pipeline import write
from milal_q14_pipeline import blind
from milal_q14_controls import controls
from milal_q14_spans import INDEPENDENT
from milal_q14_validation import policy,assert_gates

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q14_job.json'


def audit(out,q12,q13,index,binder,metrics,compat,receipts,config,frozen,inputs,tests,synth,events):
    cs=list(binder.cache.values());positive=[c for c in cs if c['positive_source_binding']]
    blind_info=json.loads((out/'blind_metrics.json').read_text());freeze=json.loads((out/'blind_freeze.json').read_text())
    core='\n'.join((ROOT/'src'/n).read_text(encoding='utf8') for n in ('milal_q14_spans.py','milal_q14_binding.py'))
    assignments=list(rows(out/'q13_coherent_assignments.csv'));os=list(rows(out/'12_q14_structural_outcome_groups.csv'))
    components=json.loads((out/'q13_symbolic_components.json').read_text())
    q12_manifest={r['path']:r['sha256'] for r in rows(q12/'99_manifest_sha256.csv')}
    refnames=('06_q12_reference_witnesses.csv','07_q12_reference_candidate_antecedents.csv','08_q12_sb02_sb03_sb10_qualification.csv')
    return dict(semantic=synth['checks'],policy=policy(core),baseline=frozen['baseline'],expected_baseline=config['baseline'],baseline_verified=True,
        inputs_verified=all(r['crc_valid'] and r['manifest_valid'] for r in inputs.values()),frozen_differences=frozen['differences'],
        raw_count=metrics['raw'],expected_raw=config['expected_input']['raw'],raw_errors=blind_info['grammar_errors'],
        retained=metrics['retained_relations'],expected_baseline_relations=config['expected_input']['qualified'],baseline_outcomes_unchanged=blind_info['baseline_outcomes_unchanged'],
        human_equal=digest(physical_path(q13/'preserved_human_judgments.csv'))==digest(physical_path(out/'preserved_human_judgments.csv')),
        canonical_mothers=[a for a in assignments if a['canonical_mother']],canonical_hierarchies=[a for a in assignments if a['canonical_hierarchy']],
        invalid_spans=[s['span_id'] for s in index.spans.values() if len(s['clause_ids'])<2 or any(
            max(index.rows[a]['word_ids'])+1!=min(index.rows[b]['word_ids']) for a,b in zip(s['clause_ids'],s['clause_ids'][1:]))],
        dependent_positive=[c['correspondence_id'] for c in positive if not c['independent'] or any(index.spans[s]['construction_independence_status'] not in INDEPENDENT for s in (c['source_span'],c['target_span']))],
        traversal_has_no_fixed_upper_bound=all(n.upper is None for n in ast.walk(ast.parse((ROOT/'src/milal_q14_spans.py').read_text())) if isinstance(n,ast.Slice)),
        profile_coverage=set(index.composites)=={k for k,s in index.spans.items() if s['construction_independence_status'] in INDEPENDENT},
        family_derived=all(c['composite_family_id'] in index.families and c['span_id'] in index.families[c['composite_family_id']]['span_ids'] for c in index.composites.values()),
        families_merged=[c['correspondence_id'] for c in cs if c['families_merged'] or c['correspondence_kind']=='CROSS_FAMILY_CONFIGURATION_CORRESPONDENCE' and c['family_A']==c['family_B']],
        unresolved_positive_mapping=[c['correspondence_id'] for c in positive if not c['mapping_resolved']],unanchored_positive=[c['correspondence_id'] for c in positive if not c['pair_binding_chains']],
        bare_formula_positive=blind_info['formula']['positive_composite_bindings'],
        reference_unchanged=all(digest(physical_path(q12/f))==q12_manifest[physical_path(q12/f).name] for f in refnames),
        invented_relation_types=[o for o in os if o['relation_type'] not in ('HYPOTACTIC','PARATACTIC')],grammar_errors=blind_info['grammar_errors'],
        q13_complete=sorted(o['structural_outcome_group_id'] for o in os)==sorted(i for c in components for i in c['outcome_ids']) and len(assignments)==len(index.order),
        membership_observational=all(not {'accepted_mother','accepted_parent','final_textual_unit','final_hierarchy_level'}&set(r) for r in rows(out/'02_q14_surface_span_membership.csv')),
        blind_unchanged=all(digest(out/k)==h for k,h in freeze['files'].items()),events=events,
        external_fixture_only=not receipts['full_external_analysis'] and receipts['new_raw_candidates']==0,
        new_human_judgments=[r for r in rows(out/'17_q14_numbers_postfreeze_controls.csv') if r['human_acceptance']],
        tests={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint_matches=tests.get('code_fingerprint')==code_fingerprint(),
        independent_equal=False,manifest_valid=verify_manifest(out),zip_crc_valid=False)


def run(source,q11,q12,q13,out,synthetic,regression=None):
    source,q11,q12,q13,out=map(Path,(source,q11,q12,q13,out));config=json.loads(CONFIG.read_text());frozen=frozen_check(config)
    synth=json.loads(Path(synthetic).read_text())
    if synth['code_fingerprint']!=code_fingerprint() or not synth['passed']:raise ValueError('current synthetic validation required')
    tests=json.loads(Path(regression).read_text()) if regression else dict(test_scope='NOT_RUN',tests_run=0,failures=0,errors=0,skipped=0)
    if regression and (tests['code_fingerprint']!=code_fingerprint() or tests['test_scope']!='FULL_REGRESSION' or any(tests[k] for k in ('failures','errors','skipped'))):raise ValueError('current full regression required')
    inputs={}
    for label,path in [('source',source),('q11',q11),('q12',q12),('q13',q13)]:
        print('Q1.4 verify',label,flush=True);inputs[label]=verified_input(path,Path(str(path)+'_results.zip'),config[label+'_zip_sha256'])
    out.mkdir(parents=True,exist_ok=False);grammar=json.loads((ROOT/'config/clause_relation_grammar_v1.json').read_text())
    print('Q1.4 Job blind',flush=True);index,binder,metrics,compat=blind(source,q12,q13,out,grammar);events=['BLIND_FROZEN']
    print('Q1.4 blind frozen; post-freeze diagnostics',flush=True)
    diag,pairs,numbers,bosman,receipts=controls(source,q11,q12,out,index,binder,config,grammar);events.append('POSTFREEZE_CONTROLS_COMPLETED')
    formula=json.loads((out/'blind_metrics.json').read_text())['formula']
    readiness='Q1_4_OVERGENERALIZED' if formula['positive_composite_bindings'] else 'READY_FOR_MFR_0_2R_Q1_5' if metrics['positive_composite_bindings'] and metrics['cross_family_correspondences'] else 'NEEDS_COMPOSITE_BINDING_REVIEW'
    report=['# Q1.4 method report','GENERALIZED_FOR_MILAL: composite extension of existing SB06/SB11. Q1.3 remains unchanged.',
        'Independent native local attachments plus nonfinite, typed subordinate, or explicit speech continuation define nonexclusive surface construction spans. Prefix subconstructions remain observational; no final textual extent is chosen.',
        'Exact node membership, word adjacency and database-native status are required. NA/Coor alone is insufficient. No fixed span length, chapter boundary, inferred hierarchy or human judgment defines discovery.',
        'Cross-family mapping preserves family identity and unresolved alternatives. Pair-specific chains must add non-generic lexical/native or explicit frame evidence. Bare repeated speech formulas and speaker names alone cannot bind.',
        'Configuration witnesses still use SB06/SB11 and the frozen qualifier. They may qualify only already licensed PARATACTIC candidates; they do not establish a new subordinate attachment. Deferred clause-binding restrictions remain.',
        '```json\n'+json.dumps(metrics,indent=2)+'\n```','Formula control: '+encode(formula),
        'Numbers: '+encode([dict(pair=n['candidate_id'],relation=n['relation'],status=n['q14_status']) for n in numbers]),
        'Bosman: '+encode([dict(source=b['source_clause_id'],membership=b['independent_membership_available'],reference=b['reference_identity_status']) for b in bosman]),
        'Reference identity, human judgments, closure targets and canonical hierarchy remain unchanged. Unmapped configurations remain available for review; no similarity ranking is used.',readiness,
        'Readiness is conditional on all release gates. Q1.5 is not started. See 15 and job_diagnostic_data.json for all requested Job diagnostics.']
    (out/'20_q14_method_report.md').write_text('\n\n'.join(report)+'\n',encoding='utf8',newline='\n')
    (out/'21_q14_next_scope.md').write_text('# Next scope\n\n'+readiness+'\n\nQ1.5 requires separate authorization. No automatic reference identity resolution.\n',encoding='utf8',newline='\n')
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],code_fingerprint=code_fingerprint(),analysis_scope='JOB',
        status='AWAITING_VALIDATION',readiness=readiness,metrics=metrics,synthetic=synth,inputs=inputs,events=events,frozen=frozen))
    manifest(out);e=audit(out,q12,q13,index,binder,metrics,compat,receipts,config,frozen,inputs,tests,synth,events)
    pending=['DETERMINISTIC_RERUN','ZIP_CRC_VALID']+(['FULL_REGRESSION_PASS'] if not regression else [])
    write(out/'gate_evidence.json',e);table(out/'22_q14_gates.csv',assert_gates(e,pending));manifest(out)
    print(encode(metrics),flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if a.resolve()==b.resolve() or not all(verify_manifest(p) for p in (a,b)):raise ValueError('two valid independent outputs required')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('independent manifests differ')
    trial=Path(str(a)+'_crc_preflight.zip');pack(a,trial);trial_check=verify_archive(trial,digest(trial))
    for out in (a,b):
        meta=json.loads((out/'90_run_metadata.json').read_text())
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        e=json.loads((out/'gate_evidence.json').read_text());e.update(independent_equal=True,manifest_valid=verify_manifest(out),zip_crc_valid=trial_check['crc_valid'])
        table(out/'22_q14_gates.csv',assert_gates(e));write(out/'gate_evidence.json',e)
        meta['status']='VALIDATED_NOT_HUMAN_ACCEPTED';write(out/'90_run_metadata.json',meta);manifest(out)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final manifests differ')
    zs=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),zs):pack(p,z)
    if digest(zs[0])!=digest(zs[1]):raise ValueError('ZIP bytes differ')
    receipt=dict(zip_paths=list(map(str,zs)),zip_sha256=digest(zs[0]),zip_exists=[z.is_file() for z in zs],
        independent_equal=True,archives=[verify_archive(z,digest(z)) for z in zs])
    write(Path(str(a)+'_verification.json'),receipt);return receipt


def main():
    p=argparse.ArgumentParser()
    for k in ('source','q11','q12','q13','out','synthetic','regression'):p.add_argument('--'+k)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);a=p.parse_args()
    if a.self_test:
        from milal_q14_synthetic import self_test
        print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.source,a.q11,a.q12,a.q13,a.out,a.synthetic,a.regression)


if __name__=='__main__':main()
