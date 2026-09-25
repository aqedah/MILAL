"""Independent read-only Q1 baseline reproduction and diagnostic release."""
import argparse
from collections import Counter,defaultdict
from itertools import zip_longest
import json
from pathlib import Path
import subprocess

from milal_mfr02r_data import rows,table,Table,digest,physical_path,manifest,verify_manifest,pack,encode
from milal_mfr02r_h0 import frozen_check
from milal_mfr02r_pipeline import code_fingerprint
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_io import verify_archive
from milal_q1_runner import verified_input
from milal_q1_binding import SourceIndex,identity,pivot
from milal_q11_diagnostic import diagnose_pair,sensitivity,RESTRICTIONS,competition_count
from milal_q11_controls import review,mechanism_matrix,SCOPES
from milal_q11_validation import code_policy,assert_gates,measurements

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/mfr_0_2r_q11_review.json'


def write(path,value):
    Path(path).write_text(encode(value)+'\n',encoding='utf8',newline='\n')


def blind(source,q1,out,grammar):
    job=source/'blind/job'
    inventory=list(rows(job/'02_clause_feature_inventory.csv'))
    if {r['book'] for r in inventory}!={'Iob'}: raise ValueError('primary scope not Job')
    index=SourceIndex(inventory,grammar['lexicons']['subordinate_rela'],grammar['lexicons']['speech'])
    table(out/'job_fixed_q1_units.csv',(dict(clause_id=k,**v) for k,v in index.units.items()))
    raw_sha=digest(physical_path(job/'09_candidate_evidence_matrix.csv'))
    counts=Counter(); errors=0; computed=[]
    with Table(out/'job_sb06_pair_diagnostics.csv',['candidate_id','restrictions','failed_restrictions',
            'frozen_sb06_conjunction','source_unit_members','target_unit_members']) as dest:
        streams=[rows(job/'09_candidate_evidence_matrix.csv'),rows(job/'08_relation_rule_matches.csv'),
                 rows(q1/'02_q1_source_binding_crosswalk.csv'),rows(q1/'03_q1_pair_qualification.csv')]
        for raw,match,cross,q in zip_longest(*streams):
            if any(x is None for x in (raw,match,cross,q)):raise ValueError('raw streams differ')
            counts['raw']+=1
            sid,tid=str(raw['candidate_clause_id']),str(raw['target_clause_id'])
            errors+=not (raw['pair_id']==match['pair_id']==cross['candidate_id']==q['candidate_id'] and
                cross['raw_row_sha256']==identity(raw) and cross['raw_table_sha256']==raw_sha and
                (cross['source_id'],cross['target_id'])==(sid,tid)==(q['source_id'],q['target_id']))
            counts[q['relation_candidate_qualification']]+=1
            if q['qualified_relations']:computed.append(q)
            if match['matches']:
                counts['original_relations']+=1
                dest.write(dict(candidate_id=raw['pair_id'],**diagnose_pair(index,sid,tid)))
    actual=list(rows(q1/'07_q1_qualified_relation_universe.csv'))
    outcomes=list(rows(q1/'09_q1_structural_outcomes.csv'))
    groups=list(rows(q1/'10_q1_structural_outcome_groups.csv'))
    by_target=defaultdict(list)
    for o in outcomes:by_target[o['target']].append(o)
    members={str(t) for r in rows(job/'15_variant_components.csv') for t in r['affected_clauses']}
    pivots=list(rows(q1/'11_q1_variant_pivots.csv'))
    for p in pivots:p['outcome_count']=int(p['outcome_count'])
    counts.update(qualified=len(actual),outcome_groups=len(groups),
        mother_competitions=competition_count(rows(q1/'12_q1_mother_competition.csv')),
        parallel_competitions=competition_count(rows(q1/'13_q1_parallel_competition.csv')))
    result=dict(counts=dict(counts,pivot_targets=sorted(r['target_id'] for r in pivots if r['status']=='VARIANT_DECISION_PIVOT')),
        raw_crosswalk_errors=errors,universe_equal=actual==computed,
        outcomes_equal=len(groups)==len(outcomes) and
            {r['structural_outcome_group_id'] for r in groups}=={r['structural_outcome_group_id'] for r in outcomes} and
            all(r['provenance_paths']==next(o['provenance_paths'] for o in outcomes if o['structural_outcome_group_id']==r['structural_outcome_group_id']) for r in groups),
        pivots_equal=pivots==[pivot(t,by_target[t],t in members) for t in index.ordered],
        canonical_mothers=[r for r in pivots if r['canonical_mother']],
        canonical_hierarchies=[r for r in pivots if r['canonical_hierarchy']])
    write(out/'blind_baseline_measurements.json',result)
    write(out/'blind_diagnostic_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        controls_loaded=False,human_judgments_loaded=False,scope='JOB',mode='DIAGNOSTIC_ONLY_NO_QUALIFICATION'))
    return result,sensitivity(rows(out/'job_sb06_pair_diagnostics.csv'),'job')


def reports(out,sensitivity_rows):
    controls=list(rows(out/'02_q1_1_numbers_missing_control_audit.csv'))
    for r in sensitivity_rows:
        r['known_control_failures']=[dict(candidate_id=n['candidate_id'],relation=n['relation']) for n in controls
            if r['scope']=='pentateuch' and r['restriction'] in n['binding_diagnostic']['sb06']['failed_restrictions']]
        r['condition_class']='DELIBERATELY_CONSERVATIVE_Q1_RESTRICTION'
        r['source_contract_support']='Q1 SPEC operational subset; researcher contract requires binding/correspondence, not universal token identity'
        r['structural_necessity']='INDEPENDENT_CONNECTION_NECESSARY; THIS_EXACT_OPERATIONAL_FORM_NOT_ESTABLISHED_AS_NECESSARY'
        if r['restriction']=='IDENTICAL_FULL_SIGNATURE':
            r['condition_class']='CONSERVATIVE_IMPLEMENTATION_CONVENIENCE'
        if r['restriction']=='CONTIGUOUS_NATIVE_MULTICLAUSE':
            r['source_contract_support']='Independent unit evidence required; contiguity/root-link-only extraction is Q1 subset, not general textual-unit definition'
    table(out/'05_q1_1_sb06_restriction_sensitivity.csv',sensitivity_rows)
    options='''# Q1.1 method options — not adjudication

1. **SB06 / SB11: independently anchored configuration correspondence.**
   Basis: Q1 researcher sections 5, 8–9 (repeated configurations and independently
   witnessed correspondence); Jin §3.2.9.4.1–.2 and Walton parallelism are recorded
   in the frozen grammar. Replace neither with a bare same-type test. A future
   version could represent correspondence positions separately from complete
   token equality, using independently witnessed constituent configurations.
   This could address the Numbers parallel alternatives, including subordinate
   corresponding positions, but does not guarantee their recovery. Overgeneration:
   repeated speech templates at different levels. Circularity: deriving the unit
   from the relation being tested. Changes Q1 semantics: yes, if authorized.
   Validation: blind Job run, non-identical correspondences, same-pattern/different-
   level negatives, dependency tests, fixture-only controls after freeze.

2. **SB02 / SB03 / SB10: reference and containing-unit evidence.**
   Basis: Q1 direct/indirect binding contract; Bosman §9.1 p204 as recorded in
   milal_mfr02r_layers.py. Require an independently supported target-to-antecedent
   reference and independently evidenced source-containing unit. Extend beyond
   the current target-to-word native-edge adapter only with such receipts. Could
   address both Bosman candidates and reference-supported hypotaxis; does not
   establish the missing Numbers hypotaxis from similarity. Overgeneration:
   ambiguous PnG/lexeme matches. Circularity: high if provisional reachability
   establishes its own edge. Changes Q1 semantics: yes. Validation: exact nodes,
   competing antecedents, unresolved identity retained, edge-under-test removal,
   independently bounded units, negative morphology-only and corpus-only cases.

3. **SB12: explicit global compatibility and independent positive constraints.**
   Basis: Jin global examples, frozen Num/Lev alternative controls and existing
   graph constraints; Q1 names GLOBAL_CONFIGURATION_CONSTRAINT but supplies no
   complete binding adapter. A future contract must distinguish compatibility
   (a necessary condition) from positive source binding. Could express Numbers
   and Lev competing configurations without choosing a winner. Overgeneration:
   every coherent graph incorrectly promoted to evidence. Circularity: high if
   selecting a hierarchy first supplies its proof. Changes Q1 semantics: yes for
   any new qualification. Validation: competing coherent assignments, no canonical
   hierarchy, compatibility-only negatives and post-freeze controls.

All three require a specified independent witness contract before implementation.
Registry names are not sufficient methodological authorization. No option is selected.
'''
    (out/'08_q1_1_method_options.md').write_text(options,encoding='utf8',newline='\n')
    numbers=list(rows(out/'02_q1_1_numbers_missing_control_audit.csv'))
    bosman=list(rows(out/'03_q1_1_bosman_unit_reference_audit.csv'))
    lines=['# Q1.1 methodological findings','',
        'Q1 remains frozen: 1,049,504 raw / 95,929 original / 185 qualified / 185 groups / 2 pivots.',
        'An absent qualified edge is not an adjudicated NO_RELATION. No new qualification was run.','',
        '## Five Numbers relation alternatives over four pairs','']
    for r in numbers:
        lines.append('- '+r['candidate_id']+' '+r['relation']+': '+r['failed_requirement']+
            '; original rules '+', '.join(x['rule_id'] for x in r['original_admitting_rules'])+'.')
    lines += ['','All are EVIDENCE_ONLY. Exact endpoint words/phrases/atoms, native edges, fixed units and original rule definitions are in 02 and fixture receipts.',
        'SB11/SB12 name configuration intents, not implemented independent witnesses. SB02/SB05/SB10 cannot be claimed applicable without additional reference/slot evidence.',
        '', '## Two Bosman references','']
    for r in bosman:
        lines.append('- '+r['source_unit_candidate_id']+' → '+str(r['target_clause_ids'])+
            ': antecedent candidates '+str([x['antecedent_clause_id'] for x in r['exact_expansion']])+
            '; node identity exact; referent and unit membership remain UNRESOLVED/assignment dependent.')
    lines += ['','Both source and target IDs resolve; the ambiguity concerns reference identity, antecedent interpretation and independently justified containing-unit membership/boundary. A provisional path cannot prove its own relation.',
        '', '## SB01–SB12','',
        'Four adapters exist: SB01/SB03/SB04/SB06. SB03 has zero Job witnesses; implemented does not mean empirically used. Eight remaining names are intent categories with missing operational prerequisites. See 04 for all counts and risks.',
        '', '## SB06 sensitivity','',
        'Population: every frozen original relation pair, separately for Job and each external fixture. Units are the unchanged Q1 contiguous root-linked units. Five predicates are measured on each pair without changing extraction. Sole failures pass the other four predicates; joint failures fail at least one other predicate. Full signature equality subsumes many lexical/position constraints, so zero sole failures does not show irrelevance.',
        'Contiguity is audited as availability of two existing multi-clause units. The audit does not create noncontiguous counterfactual units. Counts describe fixed-unit predicate failures, not recovered relations. NP presence is refined into common lexeme and common offset/function/lexeme; conjunction equivalence to frozen SB06 is checked on every pair.',
        'The scholarly/researcher contract requires independent binding and correspondence. It does not establish exact full-token identity, root-only native contiguity or the non-speech restriction as universal necessities. These are conservative Q1 implementation choices; weakening them requires an independent-witness specification, not a recall target.','']
    for r in sensitivity_rows:
        lines.append('- '+r['scope']+' '+r['restriction']+': sole '+str(r['excluded_solely'])+', joint '+str(r['excluded_with_others'])+', population '+str(r['population'])+'.')
    lines+=['','## Coverage interpretation','',
        '06 separates fixture pairs from relation alternatives. external_pair_coverage_details.csv preserves every original row and every Q1 witness. A means no original relation was available to retain, not a new human rejection. B unresolved evidence, C missing adapters, and D conservative implementation may overlap; none is automatically a false negative.',
        '', '## Readiness','', 'NEEDS_ADDITIONAL_SOURCE_REVIEW',
        'Specify independent configuration/reference witnesses and review the three options before a separately authorized Q1.2. H0.1 remains deferred.']
    (out/'09_q1_1_methodological_findings.md').write_text('\n'.join(lines)+'\n',encoding='utf8',newline='\n')
    (out/'10_q1_1_next_scope.md').write_text('# Next scope\n\nNEEDS_ADDITIONAL_SOURCE_REVIEW\n\nNo H0.1. No mechanism option or control adjudication has been selected.\n',encoding='utf8',newline='\n')


def run(source,q1,out,tf_path,regression,synthetic):
    source,q1,out,tf_path=map(Path,(source,q1,out,tf_path))
    config=json.loads(CONFIG.read_text()); frozen=frozen_check(config)
    tests=json.loads(Path(regression).read_text()); synth=json.loads(Path(synthetic).read_text())
    if tests['code_fingerprint']!=code_fingerprint() or tests['test_scope']!='FULL_REGRESSION' or any(tests[k] for k in ('errors','failures','skipped')):
        raise ValueError('current full regression required')
    if synth['mode']!='SYNTHETIC' or synth['code_fingerprint']!=code_fingerprint() or not synth['passed']:
        raise ValueError('current synthetic validation required')
    out.mkdir(parents=True,exist_ok=False)
    print('Q1.1 verifying exact Q1/source archives and extractions',flush=True)
    input_receipts={label:verified_input(path,Path(str(path)+'_results.zip'),config[key])
        for label,path,key in [('q1',q1,'q1_zip_sha256'),('source',source,'source_zip_sha256')]}
    grammar=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
    events=['BLIND_DIAGNOSTICS_STARTED']
    baseline,sens=blind(source,q1,out,grammar)
    events+=['BLIND_DIAGNOSTICS_FROZEN','CONTROLS_STARTED']
    extra,control_receipts=review(source,q1,out,tf_path,grammar,config);sens+=extra
    events+=['CONTROLS_FINISHED']
    history=list(rows(q1/'14_q1_mfr02a_13_case_reaudit.csv'))
    old_history=list(rows(source/'mfr02a_original_decisions.csv'))
    baseline['counts']['human_decisions']=len(history)
    metrics=json.loads((q1/'17_q1_reduction_metrics.json').read_text())
    reproduction=[dict(metric=k,actual=baseline['counts'].get(k,0),expected=v,match=baseline['counts'].get(k,0)==v) for k,v in config['expected'].items()]
    reproduction += [dict(metric='warning',actual=metrics['warnings'],expected=['QUALIFICATION_OVERRESTRICTIVE'],match=metrics['warnings']==['QUALIFICATION_OVERRESTRICTIVE']),
        dict(metric='readiness',actual=metrics['readiness'],expected='QUALIFICATION_REQUIRES_METHODOLOGICAL_REVIEW',match=metrics['readiness']=='QUALIFICATION_REQUIRES_METHODOLOGICAL_REVIEW')]
    if not all(r['match'] for r in reproduction):raise ValueError('baseline counts/status mismatch '+repr(reproduction))
    table(out/'01_q1_1_baseline_reproduction.csv',reproduction)
    matrix=mechanism_matrix(q1,out)
    reports(out,sens)
    policy=code_policy((ROOT/'src/milal_q11_diagnostic.py').read_text())
    policy['no_new_qualification'] &= code_policy((ROOT/'src/milal_q11_controls.py').read_text())['no_new_qualification']
    table(out/'07_q1_1_control_blinding_audit.csv',[dict(check=k,passed=v,
        evidence='AST of control-blind diagnostic module; controls are post-freeze selectors only') for k,v in policy.items()]+[
        dict(check='event_order',passed=events==['BLIND_DIAGNOSTICS_STARTED','BLIND_DIAGNOSTICS_FROZEN','CONTROLS_STARTED','CONTROLS_FINISHED'],evidence=events)])
    write(out/'source_receipts.json',dict(inputs=input_receipts,frozen=frozen,controls=control_receipts,
        q1_files=list(rows(q1/'99_manifest_sha256.csv')),source_files=list(rows(source/'99_manifest_sha256.csv')),
        events=events,diagnostic_code_sha256=digest(ROOT/'src/milal_q11_diagnostic.py')))
    n=list(rows(out/'02_q1_1_numbers_missing_control_audit.csv'));b=list(rows(out/'03_q1_1_bosman_unit_reference_audit.csv'))
    freeze=json.loads((out/'blind_diagnostic_freeze.json').read_text())
    counts=baseline['counts']; wc=Counter(r['mechanism'] for r in rows(q1/'source_binding_witnesses.csv'))
    evidence=dict(**baseline,expected=config['expected'],baseline=frozen['baseline'],expected_baseline=config['baseline'],
        frozen_differences=frozen['differences'],inputs_verified=all(r['crc_valid'] and r['manifest_valid'] for r in input_receipts.values()),
        human_equal=[r['original_decision'] for r in history]==old_history and all(r['original_decision_sha256']==identity(r['original_decision']) for r in history),
        new_judgments=[r for r in history if r['new_human_judgment']],
        new_relations=[r for r in n+b if r['authoritative_relation_created']],policy=policy,events=events,
        blind_files_equal=all(digest(out/k)==h for k,h in freeze['files'].items()),
        numbers_identities=[[r['candidate_id'],r['relation']] for r in n],expected_numbers=config['numbers_controls'],
        numbers_complete=all(r['original_admitting_rules'] and r['source_nodes']['WORD'] and r['target_nodes']['WORD'] and r['failed_requirement'] and not r['authoritative_relation_created'] for r in n),
        bosman_identities=[[r['source_clause_id'],r['source_unit_candidate_id'],r['target_clause_ids']] for r in b],expected_bosman=config['bosman_controls'],
        bosman_unresolved=all(r['reference_identity_status']=='UNRESOLVED' for r in b),
        bosman_expansion_verified=all(len(r['exact_expansion'])==int(r['frozen_record']['antecedent_target_pair_count']) for r in b),
        matrix_ids=[r['mechanism_id'] for r in matrix],matrix_counts_equal=all(r['q1_job_witness_count']==wc[r['mechanism_id']] for r in matrix),
        sensitivity_complete={(r['scope'],r['restriction']) for r in sens}=={(s,k) for s in ('job',*SCOPES) for k in RESTRICTIONS},
        sensitivity_arithmetic=all(r['passed']+r['excluded_solely']+r['excluded_with_others']==r['population'] for r in sens),
        decomposition_errors=0,tests={k:v for k,v in tests.items() if k!='passed_tests'},fingerprint_matches=tests['code_fingerprint']==code_fingerprint(),
        independent_equal=False,manifest_valid=False)
    write(out/'90_run_metadata.json',dict(stage=config['stage'],baseline=config['baseline'],code_fingerprint=code_fingerprint(),
        analysis_scope='JOB',control_scope='EXPLICIT_REFERENCES_ONLY',mode='DIAGNOSTIC_ONLY',readiness='NEEDS_ADDITIONAL_SOURCE_REVIEW',
        synthetic_receipt=synth,status='AWAITING_INDEPENDENT_COMPARISON'))
    manifest(out);evidence['manifest_valid']=verify_manifest(out)
    write(out/'gate_evidence.json',evidence)
    table(out/'11_q1_1_gates.csv',assert_gates(evidence,pending=('DETERMINISTIC_RERUN',)))
    manifest(out)
    print('Q1.1 diagnostic run complete',out,flush=True)


def release(a,b):
    a,b=Path(a),Path(b);frozen_check(json.loads(CONFIG.read_text()))
    if not all(verify_manifest(p) for p in (a,b)):raise ValueError('manifest invalid')
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('independent outputs differ')
    for out in (a,b):
        metadata=json.loads((out/'90_run_metadata.json').read_text())
        if metadata['code_fingerprint']!=code_fingerprint():raise ValueError('release fingerprint changed')
        e=json.loads((out/'gate_evidence.json').read_text());e['independent_equal']=True;e['manifest_valid']=verify_manifest(out)
        table(out/'11_q1_1_gates.csv',assert_gates(e));write(out/'gate_evidence.json',e)
        metadata['status']='DIAGNOSTIC_REVIEW_COMPLETE';write(out/'90_run_metadata.json',metadata);manifest(out)
    if (a/'99_manifest_sha256.csv').read_bytes()!=(b/'99_manifest_sha256.csv').read_bytes():raise ValueError('final bytes differ')
    archives=[Path(str(p)+'_results.zip') for p in (a,b)]
    for p,z in zip((a,b),archives):pack(p,z)
    if digest(archives[0])!=digest(archives[1]):raise ValueError('ZIP bytes differ')
    receipt=dict(verify_archive(archives[0],digest(archives[0])),independent_equal=True,zip_paths=list(map(str,archives)))
    write(Path(str(a)+'_verification.json'),receipt)
    return receipt


def main():
    p=argparse.ArgumentParser()
    for name in ('source','q1','out','tf-path','regression','synthetic'):p.add_argument('--'+name)
    p.add_argument('--release',nargs=2);p.add_argument('--self-test',action='store_true')
    a=p.parse_args()
    if a.release:print(encode(release(*a.release)))
    elif a.self_test:
        from milal_q11_synthetic import self_test
        print(encode(self_test(a.out)))
    else:run(a.source,a.q1,a.out,a.tf_path,a.regression,a.synthetic)


if __name__=='__main__':main()
