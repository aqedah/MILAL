"""Q1 verified execution and deterministic release (no upstream engine rerun)."""
import argparse
import json
from pathlib import Path
import zipfile

from milal_mfr02r_data import rows, table, encode, digest, manifest, verify_manifest, pack
from milal_mfr02r_io import verify_archive
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_grammar import load_registry
from milal_q1_pipeline import ROOT, CONFIG, write_json, run_blind, post_freeze
from milal_q1_controls import controls
from milal_q1_validation import audit, evaluate, GATES
from milal_q1_synthetic import self_test, semantic_checks


def verified_input(source,archive,sha):
    source,archive=Path(source),Path(archive)
    receipt=verify_archive(archive,sha)
    with zipfile.ZipFile(archive) as z:
        if z.read('99_manifest_sha256.csv')!=(source/'99_manifest_sha256.csv').read_bytes():raise ValueError('ZIP/extracted manifest mismatch')
    if not verify_manifest(source):raise ValueError('extracted input invalid')
    return receipt


def empirical(source,archive,h0,h0_archive,out,tf_path,regression,synthetic_receipt):
    config=json.loads(CONFIG.read_text())
    frozen=frozen_check(config)
    tests=json.loads(Path(regression).read_text())
    if tests['code_fingerprint']!=code_fingerprint() or tests['test_scope']!='FULL_REGRESSION' or tests['tests_run']<2465 or any(tests[k] for k in ('failures','errors','skipped')):
        raise ValueError('current full regression with zero skipped required')
    synthetic=json.loads(Path(synthetic_receipt).read_text())
    if synthetic['mode']!='SYNTHETIC' or not synthetic['bytes_equal'] or not all(synthetic['checks']['cases'].values()):raise ValueError('synthetic validation required')
    print('Q1 verify frozen archives',flush=True)
    a=verified_input(source,archive,config['input_zip_sha256'])
    b=verified_input(h0,h0_archive,config['h0_zip_sha256'])
    grammar=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
    metrics=run_blind(source,out,grammar)
    print('Q1 blind result frozen; begin controls',flush=True)
    control=controls(source,out,tf_path,grammar)
    metrics=post_freeze(source,h0,out)
    metrics['controls']=control
    if control['unresolved_known_controls'] or control['larger_unit_identity_unresolved']:
        metrics['warnings'].append('QUALIFICATION_OVERRESTRICTIVE')
    # A verified derived subset is not a claim that every valid source-binding
    # mechanism has been resolved. Readiness remains withheld when controls need
    # methodological review; a successful exit is technical validation only.
    metrics['readiness']='QUALIFICATION_REQUIRES_METHODOLOGICAL_REVIEW' if metrics['warnings'] else 'READY_FOR_MFR_0_2R_H0_1'
    out=Path(out)
    write_json(out/'17_q1_reduction_metrics.json',metrics)
    receipts=dict(baseline=frozen,expected_baseline=config['baseline'],source=a,h0=b,
        tests={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint_matches=tests['code_fingerprint']==code_fingerprint(),
        synthetic=synthetic['checks'],independent_bytes_equal=False)
    write_json(out/'validation_receipts.json',receipts)
    report='''# Q1 method and limitations

The raw MFR.0.2R universe is immutable. Every pair has a source-table SHA256,
decoded-row SHA256, qualification and traceable witness list. Search admission
is never counted as proof of a structural connection.

Q1 currently instantiates SB01 exact native syntactic dependencies; SB03 exact
constituent reference through a source-containing native dependency path; SB04
an immediate syntactically linked explicit secondary-participant mention pair;
and SB06 a repeated native-linked multi-clause configuration. Other mechanisms
remain unavailable/unresolved, not proved absent. Native annotation NA is never
direct syntactic dependency. All referential participant identity stays unresolved.

The conservative SB06 implementation compares a root with contiguous explicitly
native-linked clauses. It requires an explicit lexical NP in a corresponding
grammatical position and a non-speech predicate beyond a bare speech formula,
with identical multi-clause lexical/morphological and phrase signatures. This is
a documented MILAL operational subset, not a universal definition or new scholarly rule. Other
configuration patterns remain in the search/evidence archive. Bare ANSWER+AMR
recurrence is not sufficient. This restriction may produce overrestrictive controls.

Jin/Walton definitions remain frozen. Each original match is separately audited.
Configuration evidence cannot license a subordinate W-A01 attachment. W-P01
requires a witnessed configuration, and W-H01 requires an active source-bound
context. Domain flags, lexical recurrence, PnG similarity, corpus analogy and
prosody alone cannot establish a source-bound hierarchy edge. Dependencies
among witnesses are explicit; they are not counted as independent votes.

Multiple provenance paths to an identical source/target/relation produce one
outcome. Two positively different coherent singleton assignments witness a pivot
under the frozen ANY_SUBSET constraints; the remainder is UNDECIDED, never
NO_RELATION. Global variation elsewhere does not create a target pivot.
No canonical hierarchy, mother or new human judgment is created.

Existing external references alone are inspected after blind qualification is
frozen. Legacy unit-reference controls with unresolved identity remain unresolved.
All 13 MFR.0.2A decisions are reproduced unchanged after that freeze.

Technical gates do not establish scholarly completeness or human acceptance.
Review overrestrictive controls and unsupported mechanisms before H0.1.
'''
    (out/'18_q1_method_report.md').write_text(report,encoding='utf8',newline='\n')
    (out/'19_q1_next_scope.md').write_text('# Next scope\n\n'+metrics['readiness']+'\n\n'+
        'Do not start H0.1 automatically. Review source-binding coverage and external controls first.\n',encoding='utf8',newline='\n')
    write_json(out/'90_run_metadata.json',dict(stage=config['stage'],mode='REAL',baseline=config['baseline'],
        code_fingerprint=code_fingerprint(),analysis_scope='JOB',control_fixture_scope='EXPLICIT_REFERENCES_ONLY',
        status='AWAITING_INDEPENDENT_RERUN',readiness=metrics['readiness'],warnings=metrics['warnings'],
        human_judgments_created=0,canonical_mother_count=0,canonical_hierarchy_count=0))
    manifest(out)
    print('Q1 recompute output invariants',flush=True)
    measures=audit(source,out,grammar,receipts,semantic_checks())
    write_json(out/'gate_measurements.json',measures)
    gates=evaluate(measures);table(out/'20_q1_gates.csv',gates);manifest(out)
    return dict(failed=[r['gate'] for r in gates if not r['passed']],metrics=metrics)


def release(a,b):
    a,b=Path(a),Path(b);config=json.loads(CONFIG.read_text());frozen_check(config)
    if not all(verify_manifest(p) for p in (a,b)):raise ValueError('manifest invalid')
    if list(rows(a/'99_manifest_sha256.csv'))!=list(rows(b/'99_manifest_sha256.csv')):raise ValueError('independent file bytes differ')
    for out in (a,b):
        m=json.loads((out/'90_run_metadata.json').read_text())
        if m['mode']!='REAL' or m['code_fingerprint']!=code_fingerprint():raise ValueError('release fingerprint or mode mismatch')
        measurements=json.loads((out/'gate_measurements.json').read_text())
        measurements['DETERMINISTIC_RERUN']['actual']=True
        gates=evaluate(measurements)
        if any(not r['passed'] for r in gates):raise ValueError('critical gates failed: '+repr([r['gate'] for r in gates if not r['passed']]))
        write_json(out/'gate_measurements.json',measurements)
        table(out/'20_q1_gates.csv',gates)
        m['status']='SOURCE_BOUND_RELATION_UNIVERSE_ESTABLISHED_WITH_COVERAGE_LIMITATIONS'
        write_json(out/'90_run_metadata.json',m)
        receipt=json.loads((out/'validation_receipts.json').read_text());receipt['independent_bytes_equal']=True
        write_json(out/'validation_receipts.json',receipt);manifest(out)
    if list(rows(a/'99_manifest_sha256.csv'))!=list(rows(b/'99_manifest_sha256.csv')):raise ValueError('final file bytes differ')
    za,zb=Path(str(a)+'_results.zip'),Path(str(b)+'_results.zip')
    pack(a,za);pack(b,zb)
    if digest(za)!=digest(zb):raise ValueError('ZIP bytes differ')
    verified=verify_archive(za,digest(za))
    receipt=dict(**verified,byte_identical=True,zip_a=str(za),zip_b=str(zb),gates=len(GATES))
    write_json(Path(str(a)+'_verification.json'),receipt)
    return receipt


def main():
    p=argparse.ArgumentParser()
    for arg in ('source','archive','h0','h0-archive','out','tf-path','regression-receipt','synthetic-receipt'):p.add_argument('--'+arg)
    p.add_argument('--self-test',action='store_true');p.add_argument('--release',nargs=2)
    args=p.parse_args()
    if args.self_test:result=self_test(args.out)
    elif args.release:result=release(*args.release)
    else:result=empirical(args.source,args.archive,args.h0,args.h0_archive,args.out,args.tf_path,args.regression_receipt,args.synthetic_receipt)
    print(encode(result))


if __name__=='__main__':main()
