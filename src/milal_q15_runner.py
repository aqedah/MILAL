"""Q1.5 execution over verified immutable packages; independent release."""
import argparse
import json
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,physical_path,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_io import verify_archive
from milal_q1_runner import verified_input
from milal_q13_pipeline import write
from milal_q15_pipeline import blind
from milal_q15_controls import controls
from milal_q15_validation import policy,assert_gates
from milal_q15_domains import form_type

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q15_job.json'


def audit(out,q12,q14,v,counts,compat,receipt,config,frozen,inputs,tests,synth):
    d=v.d;recs=v.reclassified;forms={f['reference_witness_id']:f for f in v.forms};positive=[b for b in v.bindings if b['source_binding_candidate']]
    freeze=json.loads((out/'blind_freeze.json').read_text());old=list(rows(q14/'12_q14_structural_outcome_groups.csv'))
    new={o['structural_outcome_group_id']:o for o in rows(out/'q15_structural_outcome_groups.csv')}
    lexical=[b for b in positive if not forms[b['reference_witness_id']]['reference_bearing']]
    ev=dict(semantic=synth['checks'],policy=policy('\n'.join((ROOT/'src'/n).read_text(encoding='utf8') for n in ('milal_q15_domains.py','milal_q15_references.py'))),
        baseline=frozen['baseline'],expected_baseline=config['baseline'],baseline_verified=True,inputs_verified=all(i['crc_valid'] and i['manifest_valid'] for i in inputs.values()),
        frozen_differences=frozen['differences'],raw=counts['raw'],expected_raw=config['expected_input']['raw'],
        grammar_errors=json.loads((out/'blind_metrics.json').read_text())['grammar_errors'],retained=counts['retained_relations'],expected_relations=config['expected_input']['qualified'],
        old_outcomes_equal=all(new[o['structural_outcome_group_id']]==o for o in old),
        spans_equal=digest(q14/'01_q14_surface_construction_spans.csv')==digest(out/'preserved_q14_surface_spans.csv') and counts['preserved_spans']==config['expected_input']['spans'],
        human_equal=digest(physical_path(q14/'preserved_human_judgments.csv'))==digest(physical_path(out/'preserved_human_judgments.csv')),
        form_types_correct=len(v.forms)==config['expected_input']['reference_witnesses'] and all(f['reference_form_type']==form_type(f['raw_form'],d.words[f['word_node']]) for f in v.forms),
        lexical_positive=lexical,domains_valid=bool(d.domains) and all(x['member_clauses'] and x['boundary_basis'] and set(x['member_clauses'])<=set(d.rows) for x in d.domains.values()),
        circular_domains=[x['domain_id'] for x in d.domains.values() if x['tested_relation_used_for_domain'] or x['independence_status']!='INDEPENDENT_SURFACE'],
        circular_bindings=[b['binding_id'] for b in positive if b['tested_relation_used_for_domain'] or not b['visibility']['visibility_path_ids']],
        overlap_supported=any(len(ids)>1 for ids in d.members.values()),
        global_equal=digest(q12/'06_q12_reference_witnesses.csv')==digest(out/'preserved_q12_reference_witnesses.csv') and
            digest(physical_path(q12/'07_q12_reference_candidate_antecedents.csv'))==digest(physical_path(out/'05_q15_global_reference_candidates.csv')) and
            v.global_count==sum(int(r['candidate_count']) for r in v.old),
        candidate_sets_separate=all(set(r['source_bound_antecedent_ids'])<=set(r['visible_antecedent_ids']) for r in recs) and v.classified_count==v.global_count+v.supplemental_count,
        png_confirmed=[r for r in recs if r['referential_identity_status']=='CONFIRMED_NATIVE' and r['reference_status']!='NATIVE_EXACT_REFERENCE'],
        unique_confirmed=[r for r in recs if r['reference_status']=='UNIQUE_VISIBLE_CANDIDATE' and r['referential_identity_status']!='PROVISIONAL_UNIQUE_VISIBLE'],
        sb02_present=(out/'10_q15_sb02_qualification.csv').is_file(),sb03_present=(out/'11_q15_sb03_qualification.csv').is_file(),
        sb10_evidence_only=all(not b['source_binding_candidate'] and not b['qualified_paths'] for b in v.bindings if b['mechanism']=='SB10'),
        sb10_lexical_positive=[b for b in lexical if b['mechanism']=='SB10'],relation_types_valid=all(o['relation_type'] in ('HYPOTACTIC','PARATACTIC') for o in new.values()),
        q13_complete=set(new)=={i for c in compat['components'] for i in c['outcome_ids']} and len(compat['assignments'])==len(d.order),
        canonical_coreference=[r for r in recs if r.get('canonical_entity')],canonical_mothers=[a for a in compat['assignments'] if a['canonical_mother']],
        canonical_hierarchies=[a for a in compat['assignments'] if a['canonical_hierarchy']],
        blind_unchanged=all(digest(out/n)==h for n,h in freeze['files'].items()),controls_after_freeze=receipt['blind_files_unchanged'],
        bosman_fixture_only=receipt['bosman_clause_ids']==json.loads((q14/'control_receipts.json').read_text())['bosman_clause_ids'] and not receipt['full_external_analysis'],
        numbers_fixture_only=receipt['numbers_clause_ids']==json.loads((q14/'control_receipts.json').read_text())['numbers_clause_ids'] and receipt['new_raw_candidates']==0,
        tests={k:x for k,x in tests.items() if k!='passed_tests'},fingerprint_matches=tests.get('code_fingerprint')==code_fingerprint(),
        independent_equal=False,manifest_valid=verify_manifest(out),zip_crc_valid=False)
    return ev


def run(source,q11,q12,q14,out,synthetic,regression=None):
    source,q11,q12,q14,out=map(Path,(source,q11,q12,q14,out));config=json.loads(CONFIG.read_text());frozen=frozen_check(config)
    synth=json.loads(Path(synthetic).read_text())
    if not synth['passed'] or synth['code_fingerprint']!=code_fingerprint():raise ValueError('current synthetic validation required')
    tests=json.loads(Path(regression).read_text()) if regression else dict(test_scope='NOT_RUN',tests_run=0,failures=0,errors=0,skipped=0)
    if regression and (tests['code_fingerprint']!=code_fingerprint() or tests['test_scope']!='FULL_REGRESSION' or any(tests[k] for k in ('failures','errors','skipped'))):raise ValueError('current full regression required')
    inputs={}
    for name,path in [('source',source),('q11',q11),('q12',q12),('q14',q14)]:
        print('Q1.5 verify',name,flush=True);inputs[name]=verified_input(path,Path(str(path)+'_results.zip'),config[name+'_zip_sha256'])
    out.mkdir(parents=True,exist_ok=False);grammar=json.loads((ROOT/'config/clause_relation_grammar_v1.json').read_text())
    print('Q1.5 Job blind',flush=True);v,counts,compat=blind(source,q12,q14,out,grammar)
    print('Q1.5 blind frozen; post-freeze controls',flush=True);receipt=controls(source,q11,q12,q14,out,v,config,grammar)
    metrics=v.metrics();readiness='READY_FOR_MFR_0_2R_Q1_6' if metrics['source_bound_candidates'] and metrics['visible_candidates']<metrics['global_candidates'] else 'NEEDS_REFERENCE_VISIBILITY_REVIEW'
    text=['# Q1.5 method report','GENERALIZED_FOR_MILAL: exact native/local clause and preserved composite span visibility; identity is a separate claim.',
        'Global Q1.2 candidates remain byte-preserved. Same-clause and other domain candidates absent from Q1.2 are separately labeled supplemental.',
        'Native typed dependencies define endpoint environments, not intervening textual units. Two overlapping composite spans may provide an exact shared-component path; no unrestricted graph closure is asserted.',
        'Ordinary lexical NPs are mentions. SB10 remains explicitly evidence-only without independently attested anaphoric grammar. Unknown participant or speech-role evidence is not invented.',
        'Unique grammatically supported visible candidates may supply provisional SB02/SB03 source binding. Multiple visible candidates remain support only, unless an exact native reference independently identifies a candidate. Identity is never confirmed by uniqueness.',
        'Existing HYPOTACTIC grammar licenses are still required, with frozen W-A/W-H/W-P and deferred restrictions. A reference binding is not a new relation-type license.',
        'No standalone temporal/locative or valency domain is inferred merely from frame presence. No speech extends beyond independently represented constructions. Coverage is conservative.',
        '```json\n'+json.dumps(dict(relations=counts,reference=metrics),indent=2)+'\n```',readiness,'Technical readiness is not human acceptance. Q1.6 has not started.']
    (out/'23_q15_method_report.md').write_text('\n\n'.join(text)+'\n',encoding='utf8',newline='\n')
    (out/'24_q15_next_scope.md').write_text('# Next scope\n\n'+readiness+'\n\nQ1.6 needs separate authorization.\n',encoding='utf8',newline='\n')
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],status='AWAITING_VALIDATION',readiness=readiness,code_fingerprint=code_fingerprint(),
        analysis_scope='JOB',control_fixture_scope='EXPLICIT_REFERENCES_ONLY',metrics=counts,reference_metrics=metrics,synthetic=synth,inputs=inputs,frozen=frozen))
    manifest(out);e=audit(out,q12,q14,v,counts,compat,receipt,config,frozen,inputs,tests,synth)
    pending=['DETERMINISTIC_RERUN','ZIP_CRC_VALID']+(['FULL_REGRESSION_PASS'] if not regression else [])
    write(out/'gate_evidence.json',e);table(out/'25_q15_gates.csv',assert_gates(e,pending));manifest(out)
    print(encode(dict(relations=counts,reference=metrics)),flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if a.resolve()==b.resolve() or not all(verify_manifest(p) for p in (a,b)):raise ValueError('two valid independent outputs required')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('independent manifests differ')
    trial=Path(str(a)+'_crc_preflight.zip');pack(a,trial);trial_check=verify_archive(trial,digest(trial))
    for out in (a,b):
        meta=json.loads((out/'90_run_metadata.json').read_text())
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        e=json.loads((out/'gate_evidence.json').read_text());e.update(independent_equal=True,manifest_valid=verify_manifest(out),zip_crc_valid=trial_check['crc_valid'])
        table(out/'25_q15_gates.csv',assert_gates(e));write(out/'gate_evidence.json',e)
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
    for k in ('source','q11','q12','q14','out','synthetic','regression'):p.add_argument('--'+k)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);a=p.parse_args()
    if a.self_test:
        from milal_q15_synthetic import self_test
        print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.source,a.q11,a.q12,a.q14,a.out,a.synthetic,a.regression)


if __name__=='__main__':main()
