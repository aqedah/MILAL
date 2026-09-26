"""Verified inputs, blind execution, post-freeze review and deterministic release."""
import argparse
import json
from pathlib import Path
from milal_mfr02r_data import rows,table,digest,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_io import verify_archive
from milal_q1_runner import verified_input
from milal_q1_binding import identity,MECHANISMS
from milal_q12_pipeline import blind,write
from milal_q12_controls import controls,diagnostics
from milal_q12_validation import policy,assert_gates

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q12_job.json'


def reports(out,metrics,numbers,bosman):
    operational={'SB01','SB02','SB03','SB04','SB06','SB10','SB11'}
    table(out/'16_q12_mechanism_coverage.csv',[dict(mechanism_id=k,name=v,
        status='CONSTRAINT_ONLY' if k=='SB12' else 'OPERATIONAL_WITNESS_ADAPTER' if k in operational else 'DEFERRED_NO_POSITIVE_ADAPTER',
        observed_witnesses=metrics['mechanism_witness_counts'].get(k,0),
        qualified_witnesses=metrics['mechanism_qualified_witness_counts'].get(k,0),
        positive_binding_allowed=k!='SB12',
        limitation='EXPLICITLY_TYPED_REFERENCE_REQUIRED; PNG_LEXEME_UNIQUE_SEARCH_NOT_IDENTITY' if k in ('SB02','SB03','SB10') else
            'INDEPENDENT_NATIVE_BOUNDED_SURFACE_SUBSET' if k in ('SB06','SB11') else 'NO_NEW_CANONICAL_ASSIGNMENT') for k,v in MECHANISMS.items()])
    readiness='NEEDS_ADDITIONAL_SOURCE_REVIEW' if any(b['reference_identity_status']=='UNRESOLVED' for b in bosman) else 'READY_FOR_MFR_0_2R_H0_1'
    text=['# Q1.2 method report','',
        'Implementation schemas are GENERALIZED_FOR_MILAL. Existing scholarly adoption labels remain frozen.',
        'No newly accepted human relation or hierarchy is generated. H0.1 is not started.','',
        '## Job counts','',encode(metrics), '', '## Configuration contract','',
        'Observed profiles preserve speech formulas and time/location constituents. Data-derived families generalize lexical fillers and optional frame elaboration. ',
        'An independently bounded configuration plus corresponding position must also have an explicit nominal anchor in corresponding grammatical function, or a pair-specific temporal/locative frame witness. Whole phrases need not be identical.',
        'SAME_CONFIGURATION_FAMILY does not establish a relation or textual level. Bare speech formula alone cannot qualify binding. ',
        'All positive correspondences expose their mapped source units, anchor receipts and differences in 03. No numeric similarity threshold or control recovery target is used.',
        '', '## Reference and global constraints','',
        'UNIQUE_SURFACE_CANDIDATE remains unresolved. PnG and lexical recurrence are search evidence only. An exact native clause relation is not automatically an antecedent annotation.',
        'The new reference adapter requires explicit antecedent semantics; no such semantics are invented for the frozen BHSA input. Independently bounded unit membership is stored separately from conditional legacy graph reachability.',
        'SB12 only constrains positively qualified outcomes. ANY_SUBSET variants leave unselected outcomes UNDECIDED. Pivots require positively distinct assignments, not differences in provenance, component membership or nonselection.',
        '', '## External controls after blind freeze','']
    for n in numbers:text.append('- '+n['candidate_id']+' '+n['relation']+': '+n['final_qualification']+'; retained='+str(n['relation_retained'])+'.')
    for b in bosman:text.append('- '+b['source_unit_candidate_id']+': reference '+b['reference_identity_status']+'; independent observed members '+str(b['independent_surface_unit']['members'])+'.')
    text+=['','## Limits and readiness','',readiness,
        'Configuration extraction covers exact native subordinate/speech-complement continuations; additional independent unit-boundary adapters remain source-review work. ',
        'Different sequence lengths are retained as distinct families. Optional time/location elaboration is represented, but not every conceivable embedded/participant realization variant is operationalized. ',
        'Fixture results are evidence review, not a recall objective. All raw candidates, source observations and the 13 historical decisions remain traceable.']
    (out/'17_q12_method_report.md').write_text('\n\n'.join(text)+'\n',encoding='utf8',newline='\n')
    (out/'18_q12_next_scope.md').write_text('# Next scope\n\n'+readiness+'\n\nReview independent configuration correspondence and unresolved reference evidence. H0.1 requires separate authorization.\n',encoding='utf8',newline='\n')
    return readiness


def audit(out,config,frozen,inputs,tests,synth,metrics,configs,refs,positive,refbindings,global_result,controls_receipts,human,events):
    code='\n'.join((ROOT/'src'/f).read_text(encoding='utf8') for f in
        ('milal_q12_profiles.py','milal_q12_references.py','milal_q12_binding.py'))
    freeze=json.loads((out/'blind_freeze.json').read_text())
    pivots=list(rows(out/'12_q12_variant_pivots.csv'))
    def missing_anchor(c):
        anchors=c['pair_binding_witnesses']
        return not anchors or any(a['kind'] not in ('EXPLICIT_LEXICAL_ANCHOR_IN_CORRESPONDING_GRAMMATICAL_ROLE',
            'TEMPORAL_FRAME_CORRESPONDENCE','LOCATIVE_FRAME_CORRESPONDENCE') or not a['provenance'] for a in anchors)
    def composition_error(c):
        a=next(u for u in configs.configurations.values() if u['configuration_id']==c['configuration_A'])
        b=next(u for u in configs.configurations.values() if u['configuration_id']==c['configuration_B'])
        return not (c['same_configuration_family'] and c['position_mapping'] and c['structural_information_beyond_clause_type'] and
            c['pair_binding_witnesses'] and not set(a['members'])&set(b['members']))
    return dict(semantic=synth['checks'],policy=policy(code),baseline=frozen['baseline'],expected_baseline=config['baseline'],
        frozen_differences=frozen['differences'],q1_verified=inputs['q1']['crc_valid'] and inputs['q1']['manifest_valid'],
        q11_verified=inputs['q11']['crc_valid'] and inputs['q11']['manifest_valid'],
        source_verified=inputs['source']['crc_valid'] and inputs['source']['manifest_valid'],
        raw_count=metrics['counts']['raw'],expected_raw_count=1049504,raw_errors=metrics['raw_crosswalk_errors'],
        human_equal=all(r['original_decision_sha256']==identity(r['original_decision']) for r in human),human_count=len(human),expected_human_count=13,
        canonical_mothers=[r for r in pivots if r['canonical_mother']],canonical_hierarchies=[r for r in pivots if r['canonical_hierarchy']],
        profile_count=len(configs.profiles),source_clause_count=len(configs.rows),
        dependent_positives=sum(c['configuration_independence_status'] not in ('INDEPENDENT_SURFACE','INDEPENDENT_VALENCY') for c in positive),
        unanchored_positives=sum(missing_anchor(c) for c in positive),invalid_positive_composition=sum(composition_error(c) for c in positive),
        reference_count=len(refs.witnesses),
        png_only_resolved=sum(r['reference_status']=='EXACT_NATIVE' and 'EXACT_NATIVE_WORD_REFERENCE' not in r['antecedent_basis'] for r in refs.witnesses),
        lexeme_only_resolved=sum(r['referential_identity']!='UNRESOLVED' and not r['exact_antecedent_id'] for r in refs.witnesses),
        circular_reference_bindings=sum(r['mechanism']=='SB03' and (not r['unit_membership_basis'] or
            r['unit_membership_basis']['configuration_independence_status'] not in ('INDEPENDENT_SURFACE','INDEPENDENT_VALENCY')) for r in refbindings),
        sb12_input_ids=global_result['input_outcome_ids'],sb12_output_ids=global_result['output_outcome_ids'],sb12_positive=global_result['positive_binding'],
        family_assigned_levels=sum(p['textual_level']!='UNRESOLVED' for p in configs.profiles.values()),events=events,
        blind_files_equal=all(digest(out/k)==h for k,h in freeze['files'].items()),
        full_external_analyses=sum(r['full_book_analysis'] for r in controls_receipts.values()),
        generated_external_candidates=sum(r['generated_new_candidates'] for r in controls_receipts.values()),
        new_judgments=[r for r in human if r['new_human_judgment']],
        tests={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint_matches=tests['code_fingerprint']==code_fingerprint(),
        independent_equal=False,manifest_valid=verify_manifest(out),analysis_books=sorted({r['book'] for r in configs.rows.values()}),
        fixture_identities_equal=all(r['exact_clause_ids']==r['expected_clause_ids'] for r in controls_receipts.values()),
        analysis_scope='JOB',corpus_comparison_scope='HB_CORPUS',
        deferred_qualified=sum(bool(r['qualified_paths']) and r['deferred'] for r in rows(out/'10_q12_qualified_relation_universe.csv'))+
            sum(bool(r['q12']['qualified_paths']) and r['deferred'] for scope in controls_receipts
                for r in rows(out/(scope+'_postfreeze_pair_audit.csv'))))


def run(source,q1,q11,out,regression,synthetic):
    source,q1,q11,out=map(Path,(source,q1,q11,out));config=json.loads(CONFIG.read_text())
    frozen=frozen_check(config);tests=json.loads(Path(regression).read_text());synth=json.loads(Path(synthetic).read_text())
    if tests['code_fingerprint']!=code_fingerprint() or tests['test_scope']!='FULL_REGRESSION' or any(tests[k] for k in ('errors','failures','skipped')):
        raise ValueError('current full regression required')
    if synth['mode']!='SYNTHETIC' or synth['code_fingerprint']!=code_fingerprint() or not synth['passed']:raise ValueError('current synthetic required')
    out.mkdir(parents=True,exist_ok=False)
    print('Q1.2 verifying exact source / Q1 / Q1.1 archives',flush=True)
    inputs={label:verified_input(path,Path(str(path)+'_results.zip'),config[key]) for label,path,key in
        [('source',source,'source_zip_sha256'),('q1',q1,'q1_zip_sha256'),('q11',q11,'q11_zip_sha256')]}
    grammar=load_registry(ROOT/'config/clause_relation_grammar_v1.json');events=['BLIND_STARTED']
    metrics,configs,refs,positive,refbindings,global_result=blind(source,q1,out,grammar)
    events+=['BLIND_FROZEN','CONTROLS_STARTED']
    receipts,numbers,bosman=controls(source,q1,q11,out,grammar,config);events+=['CONTROLS_FINISHED']
    human=diagnostics(source,q1,out,configs,refs,metrics,config)
    readiness=reports(out,metrics,numbers,bosman)
    write(out/'source_receipts.json',dict(inputs=inputs,frozen=frozen,events=events))
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],code_fingerprint=code_fingerprint(),
        analysis_scope='JOB',corpus_comparison_scope='HB_CORPUS',control_fixture_scope='EXPLICIT_REFERENCES_ONLY',
        status='AWAITING_INDEPENDENT_COMPARISON',readiness=readiness,synthetic=synth,metrics=metrics))
    manifest(out)
    e=audit(out,config,frozen,inputs,tests,synth,metrics,configs,refs,positive,refbindings,global_result,receipts,human,events)
    write(out/'gate_evidence.json',e)
    table(out/'19_q12_gates.csv',assert_gates(e,pending=('DETERMINISTIC_RERUN',)))
    manifest(out);print('Q1.2 completed',out,flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if not all(verify_manifest(p) for p in (a,b)):raise ValueError('manifest invalid')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('independent outputs differ')
    for out in (a,b):
        meta=json.loads((out/'90_run_metadata.json').read_text())
        if meta['code_fingerprint']!=code_fingerprint():raise ValueError('fingerprint changed')
        e=json.loads((out/'gate_evidence.json').read_text());e['independent_equal']=True;e['manifest_valid']=verify_manifest(out)
        table(out/'19_q12_gates.csv',assert_gates(e));write(out/'gate_evidence.json',e)
        meta['status']='VALIDATED_NOT_HUMAN_ACCEPTED';write(out/'90_run_metadata.json',meta);manifest(out)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final manifests differ')
    archives=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),archives):pack(p,z)
    if digest(archives[0])!=digest(archives[1]):raise ValueError('archive bytes differ')
    receipt=dict(verify_archive(archives[0],digest(archives[0])),independent_equal=True,zip_paths=list(map(str,archives)))
    write(Path(str(a)+'_verification.json'),receipt);return receipt


def main():
    p=argparse.ArgumentParser()
    for n in ('source','q1','q11','out','regression','synthetic'):p.add_argument('--'+n)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2);a=p.parse_args()
    if a.self_test:
        from milal_q12_synthetic import self_test
        print(encode(self_test(a.out)))
    elif a.release:print(encode(release(*a.release)))
    else:run(a.source,a.q1,a.q11,a.out,a.regression,a.synthetic)


if __name__=='__main__':main()
