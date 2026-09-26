"""Q1.3 verified frozen input, independent rerun, and deterministic release."""
import argparse
import json
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,manifest,verify_manifest,pack,encode,physical_path
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_io import verify_archive
from milal_q1_runner import verified_input
from milal_q13_pipeline import blind,postfreeze,write
from milal_q13_model import dimension,MOTHER
from milal_q13_validation import core_policy,assert_gates

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q13_job.json'


def audit(source,out,model,result,counts,reaudit,preserved,config,frozen,inputs,tests,synth):
    assignments=[];proofs=[]
    for r in result['assignments']:
        if r['coherent_combined_assignment']:assignments.append(r['coherent_combined_assignment'])
        proofs+=r['conflict_assignment_witnesses']
    for p in proofs:assignments += [p['assignment_a'],p['assignment_b']]
    invalid=[]
    for p in proofs:
        a,b=set(p['assignment_a']['selected_outcome_ids']),set(p['assignment_b']['selected_outcome_ids'])
        union=a|b
        if (model.errors(a) or model.errors(b) or not model.errors(union) or
            a-b!={p['outcome_a']} or b-a!={p['outcome_b']} or
            model.rows[p['outcome_a']]['target']!=model.rows[p['outcome_b']]['target'] or
            model.errors(union-{p['outcome_a']}) or model.errors(union-{p['outcome_b']})):
            invalid.append(p)
    pivots={r['target_id']:r for r in result['pivots']}
    original_ids=set(model.rows);output_ids={r['outcome_id'] for r in result['dimensions']}
    upstream={r['path']:r['sha256'] for r in rows(source/'99_manifest_sha256.csv')}
    def equal_file(name):
        path=physical_path(source/name)
        return digest(path)==upstream[path.name]
    def preserved_equal(name):
        r=preserved[name]
        return r['source_sha256']==r['output_sha256']==digest(out/r['output'])==digest(physical_path(source/name))
    freeze=json.loads((out/'blind_freeze.json').read_text(encoding='utf8'))
    blind_equal=all(digest(out/k)==v for k,v in freeze.items())
    sb=json.loads((out/'global_constraint_audit.json').read_text(encoding='utf8'))['original_sb12']
    diagnostics=json.loads((out/'postfreeze_diagnostics.json').read_text(encoding='utf8'))
    diagnostic_checks={}
    for d in diagnostics:
        ids=d['outcome_ids'];errors=model.errors(ids)
        expected_assignment=None if errors else model.assignment(d['target_id'],ids)
        # An independent constraint may explain a failure to coexist. Mere multiplicity may not.
        diagnostic_checks[d['kind']]=(d['representable']==(not errors) and d['violations']==errors and
            d['assignment']==expected_assignment and not d['human_accepted'] and
            (not errors or bool(model.provenance(ids))))
    e=dict(semantic=synth['checks'],policy=core_policy((ROOT/'src/milal_q13_model.py').read_text(encoding='utf8')),
        baseline=frozen['baseline'],expected_baseline=config['baseline'],baseline_verified=frozen['baseline']==config['baseline'],
        frozen_differences=frozen['differences'],input_verified=inputs['crc_valid'] and inputs['manifest_valid'] and verify_manifest(source),
        qualified_equal=preserved_equal('10_q12_qualified_relation_universe.csv') and counts['qualified']==config['expected_input']['qualified'],
        outcomes_equal=preserved_equal('11_q12_structural_outcome_groups.csv') and original_ids==output_ids and
            counts['outcomes']==config['expected_input']['outcomes'] and blind_equal and
            all(r['original_outcome']==model.rows[r['outcome_id']] for r in result['dimensions']),
        raw_count=counts['raw'],expected_raw=config['expected_input']['raw'],
        dimension_errors=[r for r in result['dimensions'] if r['dimension']!=dimension(model.rows[r['outcome_id']]) or r['mother_slot_consumed']!=(r['dimension']==MOTHER)],
        mother_parallel_diagnostic=diagnostic_checks.get('mother_parallel',False),
        multiple_peers_diagnostic=diagnostic_checks.get('multiple_peers',False),
        incoherent_assignments=[a['assignment_id'] for a in assignments if model.errors(a['selected_outcome_ids'])],
        assignment_errors=[a['assignment_id'] for a in assignments if a!=model.assignment(a['target_id'],a['selected_outcome_ids'])],
        multiplicity_only_pivots=[r['target_id'] for r in result['pivots'] if r['human_review_required'] and not r['positive_incompatibility_witnesses']],
        unselected_errors=[a['assignment_id'] for a in assignments if a['unselected_semantics']!='UNDECIDED' or
            set(a['unresolved_relations'])!=set(model.by_target[a['target_id']])-set(a['selected_outcome_ids'])],
        symbolic_coverage=sorted(i for c in result['components'] for i in c['outcome_ids'])==sorted(original_ids) and
            len(result['assignments'])==len(model.targets) and all(c['representation']=='SYMBOLIC_CONSTRAINT_COMPONENT' for c in result['components']),
        new_positive_ids=sorted(output_ids-original_ids),sb12_positive=sb['positive_binding'],
        sb12_ids_equal=set(sb['input_outcome_ids'])==set(sb['output_outcome_ids'])==original_ids,
        human_equal=preserved_equal('preserved_human_judgments.csv'),human_count=counts['human'],expected_human=config['expected_input']['human'],
        canonical_mothers=[r for r in result['assignments']+result['pivots']+assignments if r['canonical_mother']],
        canonical_hierarchies=[r for r in result['assignments']+result['pivots']+assignments if r['canonical_hierarchy']],
        reaudit_targets=sorted(r['target_id'] for r in reaudit),expected_reaudit_targets=sorted(config['previous_pivot_targets']),
        reaudit_consistent=len(reaudit)==counts['previous_pivots']==config['expected_input']['previous_pivots'] and
            all(r['q13_status']==pivots[r['target_id']]['q13_status'] for r in reaudit),
        reference_equal=all(equal_file(f) for f in ('06_q12_reference_witnesses.csv','07_q12_reference_candidate_antecedents.csv','08_q12_sb02_sb03_sb10_qualification.csv')),
        unit_boundary_equal=all(equal_file(f) for f in ('configuration_units.csv','01_q12_configuration_profiles.csv')),
        tests={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint_matches=tests['code_fingerprint']==code_fingerprint(),
        independent_equal=False,manifest_valid=verify_manifest(out),invalid_pivot_proofs=invalid)
    return e


def run(source,out,regression,synthetic):
    source,out=Path(source),Path(out);config=json.loads(CONFIG.read_text(encoding='utf8'));frozen=frozen_check(config)
    tests=json.loads(Path(regression).read_text(encoding='utf8'));synth=json.loads(Path(synthetic).read_text(encoding='utf8'))
    if tests['code_fingerprint']!=code_fingerprint() or tests['test_scope']!='FULL_REGRESSION' or any(tests[k] for k in ('errors','failures','skipped')):
        raise ValueError('current full regression required')
    if synth['mode']!='SYNTHETIC' or synth['code_fingerprint']!=code_fingerprint() or not synth['passed'] or not all(synth['checks'].values()):
        raise ValueError('current synthetic validation required')
    print('Q1.3 verifying exact Q1.2 archive and extracted bytes',flush=True)
    inputs=verified_input(source,Path(str(source)+'_results.zip'),config['input_zip_sha256'])
    out.mkdir(parents=True,exist_ok=False)
    model,result,counts=blind(source,out)
    reaudit,diagnostics,preserved=postfreeze(source,out,model,result,counts,config)
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],mode='REAL',
        code_fingerprint=code_fingerprint(),input_zip_sha256=config['input_zip_sha256'],analysis_scope='JOB',
        status='AWAITING_INDEPENDENT_COMPARISON',readiness='READY_FOR_MFR_0_2R_Q1_4',synthetic=synth,
        events=['BLIND_STARTED','BLIND_FROZEN','POSTFREEZE_DIAGNOSTICS'],counts=counts))
    write(out/'source_receipts.json',dict(frozen=frozen,input=inputs))
    manifest(out)
    e=audit(source,out,model,result,counts,reaudit,preserved,config,frozen,inputs,tests,synth)
    write(out/'gate_evidence.json',e);table(out/'16_q13_gates.csv',assert_gates(e,allow_pending=True));manifest(out)
    print(encode(counts),flush=True)


def release(a,b):
    a,b=Path(a),Path(b)
    if a.resolve()==b.resolve():raise ValueError('independent run directories required')
    frozen_check(json.loads(CONFIG.read_text(encoding='utf8')))
    if not all(verify_manifest(p) for p in (a,b)):raise ValueError('manifest invalid')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('independent outputs differ')
    for out in (a,b):
        meta=json.loads((out/'90_run_metadata.json').read_text(encoding='utf8'))
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        e=json.loads((out/'gate_evidence.json').read_text(encoding='utf8'));e['independent_equal']=True;e['manifest_valid']=verify_manifest(out)
        table(out/'16_q13_gates.csv',assert_gates(e));write(out/'gate_evidence.json',e)
        meta['status']='VALIDATED_NOT_HUMAN_ACCEPTED';write(out/'90_run_metadata.json',meta);manifest(out)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final manifests differ')
    archives=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),archives):pack(p,z)
    if digest(archives[0])!=digest(archives[1]):raise ValueError('archive bytes differ')
    checks=[verify_archive(z,digest(z)) for z in archives]
    receipt=dict(independent_equal=True,archives=checks,zip_sha256=digest(archives[0]),zip_paths=list(map(str,archives)))
    write(Path(str(a)+'_verification.json'),receipt);return receipt


def main():
    p=argparse.ArgumentParser()
    for n in ('q12','out','regression','synthetic'):p.add_argument('--'+n)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);a=p.parse_args()
    if a.self_test:
        from milal_q13_synthetic import self_test
        print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.q12,a.out,a.regression,a.synthetic)


if __name__=='__main__':main()
