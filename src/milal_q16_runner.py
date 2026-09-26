"""Q1.6 verified audit execution and independent deterministic archives."""
import argparse,json,re
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,physical_path,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_io import verify_archive
from milal_mfr02r_pipeline import code_fingerprint
from milal_q1_runner import verified_input
from milal_q13_pipeline import write
from milal_q16_pipeline import blind
from milal_q16_controls import controls
from milal_q16_validation import gates
ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q16_job.json'
CORE=('milal_q16_evidence.py','milal_q16_sources.py','milal_q16_pipeline.py')


def evidence(a,views,result,cov,compat,metrics,out,source,q12,q14,q15,config,frozen,inputs,synth,tests,control):
    pre=json.loads((ROOT/'docs/MFR_0_2R_Q1_6_PREIMPLEMENTATION_AUDIT.json').read_text())
    oldmetrics=json.loads((q15/'blind_metrics.json').read_text())
    positive=[n for n in a.graph.nodes.values() if n['payload'].get('positive_binding')]
    outcomes=list(rows(out/'14_q16_qualified_relation_universe.csv'))
    core='\n'.join((ROOT/'src'/n).read_text(encoding='utf-8-sig') for n in CORE)
    unchanged=lambda path,h:digest(physical_path(path))==h
    no_ids=not re.search(r'\b[3-9]\d{5}\b',core)
    allpaths=[p for o in a.outcomes for p in o['provenance_paths']]
    grammar=json.loads((ROOT/'config/clause_relation_grammar_v1.json').read_text())
    # Validate frozen paths against their original Q1.2/Q1.4/Q1.5 qualification records.
    path_ok=all(any(p['witness_id']==q['witness_id'] and p['rule_id']==q['rule_id'] and p['relation']==q['relation'] for q in a.paths[o['structural_outcome_group_id']]) for o in a.outcomes for p in o['provenance_paths'])
    registry={r['mechanism']:r for r in cov}
    flags=dict(baseline_verified=pre['baseline']==config['baseline']==frozen['baseline'] and all(r['crc_valid'] and r['manifest_valid'] for r in inputs.values()),
      frozen_equal=not frozen['differences'],raw_equal=oldmetrics['counts']['raw']==config['expected_input']['raw'] and metrics['newly_qualified']==0,
      outcomes_equal=outcomes==a.outcomes and len(outcomes)==config['expected_input']['qualified'],
      references_equal=len(a.forms)==config['expected_input']['reference_witnesses'] and oldmetrics['counts']['original_global_candidates']==config['expected_input']['global_candidates'] and unchanged(q12/'06_q12_reference_witnesses.csv',digest(q15/'preserved_q12_reference_witnesses.csv')),
      spans_equal=len(a.spans)==config['expected_input']['spans'] and digest(q14/'01_q14_surface_construction_spans.csv')==digest(q15/'preserved_q14_surface_spans.csv'),
      human_equal=digest(q14/'preserved_human_judgments.csv')==digest(q15/'preserved_human_judgments.csv') and sum(1 for _ in rows(q15/'preserved_human_judgments.csv'))==config['expected_input']['human'],
      audit_first=not pre['q16_implementation_files_present'] and pre['stage']=='AUDIT_BEFORE_Q16_IMPLEMENTATION' and digest(ROOT/'docs/MFR_0_2R_Q1_6_PREIMPLEMENTATION_AUDIT.json')==config['preimplementation_audit_sha256'] and all(digest(ROOT/n)==h for n,h in pre['audited_source_hashes'].items()),
      aliases_blocked=not any(v['polarity']=='POSITIVE_BINDING' for vv in views.values() for v in vv) and not any(n['mechanism'] in views for n in positive),
      graph_complete=bool(positive) and all(a.graph.roots(n['node_id']) for n in positive) and all(p['witness_id'] in a.graph.nodes for p in allpaths),
      shared_once=len({r['raw_evidence_identity'] for r in result['groups']})==len(result['groups']) and all(r['independent_reason_count']==1 for r in result['groups']),
      ablation_complete=len(result['ablation'])==11 and all(r['baseline']==len(outcomes)==r['still_qualified']+r['lose_all_binding_support'] and not r['frozen_outputs_mutated'] for r in result['ablation']),
      no_valency_guess=synth['checks']['Q16-S1'] and synth['checks']['Q16-S2'] and all(not v['detail']['distinct_valency_path'] for v in views['SB05']),
      time_pair_required=synth['checks']['Q16-S3'] and synth['checks']['Q16-S4'] and registry['SB07']['positive_witness_count']==0,
      location_pair_required=synth['checks']['Q16-S5'] and synth['checks']['Q16-S6'] and registry['SB08']['positive_witness_count']==0,
      domain_positive=synth['checks']['Q16-S8'] and all(v['detail']['positive_continuity'] for v in views['SB09']),
      no_absence_domain=synth['checks']['Q16-S7'] and all(d['boundary_basis'] for d in a.domains.values()),
      domain_independent=synth['checks']['Q16-S10'] and all(not d['tested_relation_used_for_domain'] and d['independence_status']=='INDEPENDENT_SURFACE' for d in a.domains.values()),
      no_distance=not re.search(r'\b(nearest|distance_threshold|max_distance)\b',core),no_score=not re.search(r'\b(score|weight|ranking)\s*=',core),no_top_n=not re.search(r'\b(top_n|top_k)\b',core),
      grammar_retained=path_ok and metrics['newly_qualified']==0,
      q13_complete={o['structural_outcome_group_id'] for o in outcomes}=={oid for c in compat['components'] for oid in c['outcome_ids']},
      sb12_constraint=registry['SB12']['conceptual_status']=='CONSTRAINT_ONLY' and registry['SB12']['positive_witness_count']==0 and not any(n['mechanism']=='SB12' for n in positive),
      blind_unchanged=control['blind_unchanged'],no_job_ids=no_ids,no_numbers_ids=no_ids,no_bosman_ids=no_ids,
      no_canonical_mother=all(not x['canonical_mother'] for x in compat['assignments']),no_canonical_hierarchy=all(not x['canonical_hierarchy'] for x in compat['assignments']),
      no_new_human=metrics['newly_qualified']==0 and all(x['canonical_decision'] is None for x in rows(out/'19_q16_numbers_postfreeze_controls.csv')),
      regression_pass=tests.get('test_scope')=='FULL_REGRESSION' and tests.get('tests_run',0)>0 and not tests.get('failures',1) and not tests.get('errors',1) and tests.get('code_fingerprint')==code_fingerprint(),
      skip_zero=tests.get('skipped')==0,independent_equal=False,manifest_valid=verify_manifest(out),zip_crc_valid=False)
    native_actual={encode(e) for r in a.inventory for e in r['CLAUSE']['native_annotations']}
    flags['native_equal']=all(encode(n['payload']['value']) in native_actual for n in a.graph.nodes.values() if n['node_type']=='RAW' and n['payload']['kind']=='NATIVE_EDGE') and len(native_actual)>0
    for m in views:flags[m.lower()+'_audited']=bool(views[m]) and m in pre['findings'] and registry[m]['eligible']==len(views[m])
    return flags


def run(source,q11,q12,q14,q15,out,synthetic,regression=None):
    source,q11,q12,q14,q15,out=map(Path,(source,q11,q12,q14,q15,out))
    config=json.loads(CONFIG.read_text());frozen=frozen_check(config);synth=json.loads(Path(synthetic).read_text())
    if not synth['passed'] or synth['code_fingerprint']!=code_fingerprint():raise ValueError('current synthetic required')
    tests=json.loads(Path(regression).read_text()) if regression else dict(test_scope='NOT_RUN',tests_run=0,failures=0,errors=0,skipped=0)
    if regression and (tests.get('code_fingerprint')!=code_fingerprint() or tests.get('test_scope')!='FULL_REGRESSION' or any(tests[k] for k in ('failures','errors','skipped'))):raise ValueError('current full regression required')
    inputs={}
    for key,p in [('source',source),('q11',q11),('q12',q12),('q14',q14),('q15',q15)]:
        print('Q1.6 verify',key,flush=True);inputs[key]=verified_input(p,Path(str(p)+'_results.zip'),config[key+'_zip_sha256'])
    out.mkdir(parents=True,exist_ok=False)
    print('Q1.6 blind evidence audit',flush=True);a,views,result,cov,compat,metrics=blind(source,q12,q14,q15,out)
    print('Q1.6 freeze; post-freeze diagnostics',flush=True);receipt=controls(a,q15,out,config,result,views)
    readiness='NEEDS_SOURCE_BINDING_COVERAGE_REVIEW' if any(r['implementation_status'] in ('PARTIALLY_OPERATIONAL','NOT_YET_OPERATIONAL','UNRESOLVED') for r in cov) else 'READY_FOR_MFR_0_2R_H0_1'
    report=['# Q1.6 method report','Audit-first additive execution. All original qualified outcomes and provenance paths are preserved. No new relation extractor was justified by the preimplementation audit.',
      'Raw identities use exact BHSA source artifact hashes plus explicit node/edge observations. Derived paths retain frozen witness, visibility, span and domain IDs. Configuration dependencies include complete consumed clause profiles: shared context is conservatively shared provenance, not proof of independent causal sufficiency.',
      'Ablation removes raw facts consumed exclusively by one positive mechanism. Support-only views cannot rescue qualification. Shared facts remain. A recorded witness survives only when its complete recorded dependency closure survives; this is a conservative recorded-provenance ablation, not a minimal proof or counterfactual linguistic score. Derived dependencies (including SB04 depending on SB01) are transitively expanded.',
      'SB05 native government observations overlap SB01; deferred atom candidates remain unresolved. SB07/SB08 frame correspondence can be a shared configuration view without establishing temporal/locative dependency. SB09 reuses Q1.5 paths and domains; membership is never a new binding. SB10 lexical-anaphoric extraction still lacks an attested adapter. SB12 remains constraint only.',
      'The new supplemental dependency contract validates explicit attested synthetic paths. It is not a new empirical extractor. No Job path is fabricated to satisfy synthetic positives. Zero new relations is not completeness.',
      'Numbers/Bosman controls are exact post-freeze replays of verified Q1.5 fixtures because no new qualification adapter was introduced; no new external candidate universe is generated.',
      'Readiness withheld: material distinct valency/time/location/domain and lexical-anaphora contracts remain underspecified. Human methodological review must distinguish genuine unresolved evidence from missing extraction infrastructure.',
      '```json\n'+json.dumps(metrics,indent=2)+'\n```',readiness]
    (out/'22_q16_method_report.md').write_text('\n\n'.join(report)+'\n',encoding='utf8')
    (out/'23_q16_h0_1_readiness.md').write_text('# Readiness\n\n'+readiness+'\n\nDo not start H0.1. Review underspecified distinct dependency adapters and unresolved visibility gaps.\n',encoding='utf8')
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],status='AWAITING_VALIDATION',readiness=readiness,analysis_scope='JOB',control_fixture_scope='EXPLICIT_REFERENCES_ONLY',code_fingerprint=code_fingerprint(),metrics=metrics,inputs=inputs,frozen=frozen,synthetic=synth,tests={k:v for k,v in tests.items() if k!='passed_tests'}))
    manifest(out);ev=evidence(a,views,result,cov,compat,metrics,out,source,q12,q14,q15,config,frozen,inputs,synth,tests,receipt)
    pending=['DETERMINISTIC_RERUN','ZIP_CRC_VALID']+(['FULL_REGRESSION_PASS'] if not regression else [])
    write(out/'gate_evidence.json',ev);table(out/'24_q16_gates.csv',gates(ev,pending));manifest(out)
    print(encode(metrics),flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if a.resolve()==b.resolve() or not all(verify_manifest(p) for p in (a,b)):raise ValueError('independent valid outputs required')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('A/B manifest mismatch')
    trial=Path(str(a)+'_crc_preflight.zip');pack(a,trial);checked=verify_archive(trial,digest(trial))
    for p in (a,b):
        meta=json.loads((p/'90_run_metadata.json').read_text())
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        ev=json.loads((p/'gate_evidence.json').read_text());ev.update(independent_equal=True,manifest_valid=verify_manifest(p),zip_crc_valid=checked['crc_valid'])
        table(p/'24_q16_gates.csv',gates(ev));write(p/'gate_evidence.json',ev);meta['status']='VALIDATED_NOT_HUMAN_ACCEPTED';write(p/'90_run_metadata.json',meta);manifest(p)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final manifest mismatch')
    zs=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),zs):pack(p,z)
    if digest(zs[0])!=digest(zs[1]):raise ValueError('ZIP bytes differ')
    result=dict(zip_paths=list(map(str,zs)),zip_sha256=digest(zs[0]),zip_exists=[z.is_file() for z in zs],bytes_identical=zs[0].read_bytes()==zs[1].read_bytes(),archives=[verify_archive(z,digest(z)) for z in zs])
    write(Path(str(a)+'_verification.json'),result);return result


def main():
    p=argparse.ArgumentParser()
    for k in ('source','q11','q12','q14','q15','out','synthetic','regression'):p.add_argument('--'+k)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);args=p.parse_args()
    if args.self_test:
        from milal_q16_synthetic import self_test
        print(encode(self_test(args.out)))
    elif args.release:print(encode(release(*args.release)))
    else:run(args.source,args.q11,args.q12,args.q14,args.q15,args.out,args.synthetic,args.regression)
if __name__=='__main__':main()
