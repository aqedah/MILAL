"""MFR orchestration: provenance, five freezes, controls, then human history."""
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile
import milal_mfr_common as cm
import milal_mfr_provenance as pv
import milal_mfr_gates as gt

SCOPES=('job','pentateuch','prophets','death','daniel_ezra')
CONTROL_OUTPUTS={'pentateuch':'18_pentateuch_edsf_control_report.csv','prophets':'19_prophetic_superscription_control_report.csv','death':'20_death_resumption_control_report.csv','daniel_ezra':'21_daniel_ezra_control_report.csv'}

def run(command,log):
    result=subprocess.run(command,cwd=cm.ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf8',errors='replace');log.append(result.stdout);cm.require(result.returncode==0,result.stdout)

def execute(out,bhsa=None,self_test=False,regression=None):
    out=Path(out).resolve();work=out.with_name(out.name+'_work');cm.require(not out.exists() and not work.exists(),'fresh output paths required');work.mkdir(parents=True);logs=[]
    cfg=json.loads((cm.ROOT/'config/mfr_0_1_job.json').read_bytes());base=pv.baseline(cfg);audit=pv.audit(cfg,bhsa if not self_test else None);static=pv.static_scan();cm.require(not static,'static contamination');cm.require(all(r['sha256']==r['expected_sha256'] for r in audit if r['expected_sha256']!='LOCAL_RAW_SOURCE'),'frozen asset hash')
    if not self_test:
        cm.require(regression,'full-regression receipt required before empirical execution');receipt=json.loads(Path(regression).read_bytes());rg=gt.release_gates(b'a',b'a',receipt);cm.require(rg['FULL_REGRESSION_PASS'] and rg['SKIP_ZERO'],'full regression not clean')
    else:receipt=None
    from milal_mfr_selftest import behavior
    contract=behavior();cm.require(all(contract.values()),'method self-test')
    if self_test:
        from milal_mfr_synthetic import corpus
        cm.write(work/'synthetic.json',cm.js(corpus()))
    phases={};events=[];frozen={}
    try:
        for scope in SCOPES:
            phase=work/scope;command=[sys.executable,'-B','-X','utf8',str(cm.ROOT/'src/milal_mfr_blind.py'),'--rules',str(cm.ROOT/'config/mfr_0_1_blind_rules.json'),'--scope',scope,'--out',str(phase)]
            command+=['--synthetic',str(work/'synthetic.json')] if self_test else ['--bhsa',str(Path(bhsa).resolve())]
            run(command,logs)
            hashes={p.name:cm.sha(p.read_bytes()) for p in sorted(phase.iterdir()) if p.is_file()};cm.write(phase/'13_job_blind_hashes.json',cm.js(dict(scope=scope,files=hashes,code_config_sha256=json.loads((phase/'metadata.json').read_bytes())['code_config_sha256'])))
            frozen[scope]=cm.manifest(phase,'12_job_blind_manifest.csv');cm.require(cm.verify(phase,'12_job_blind_manifest.csv'),'freeze failed');events.append(scope+'_FREEZE');phases[scope]=gt.scan(phase)
            print(json.dumps(dict(frozen=scope,counts=phases[scope]['meta']['counts'])),flush=True)
        # Both historical labels and known references are unavailable to children.
        controls=json.loads((cm.ROOT/'config/mfr_0_1_controls.json').read_bytes());events.append('KNOWN_CONTROLS_LOADED')
        from milal_mfr_controls import control_report
        from milal_mfr_postblind import historical,review,early_marker_judgments,METHOD
        out.mkdir();cm.write(out/'01_existing_asset_provenance_audit.csv',cm.csv_bytes(audit));control_summary={};control_reports={}
        if self_test:
            for scope in CONTROL_OUTPUTS:
                controls[scope]=[['Alpha','8:1',1],['Beta','8:14',1]] if scope=='pentateuch' else [['Alpha','8:9'],['Beta','8:10']] if scope=='death' else [['Alpha','8:1'],['Beta','8:14']]
            controls['job']=['8:1','8:8','8:14']
            controls['death_formula_loci']=[['Beta','8:10']];controls['death_resumption_pairs']=[[['Alpha','8:9'],['Beta','8:10']]]
        for scope,name in CONTROL_OUTPUTS.items():
            report=control_report(work/scope,scope,controls[scope],controls['patterns']);control_reports[scope]=report;cm.write(out/name,cm.csv_bytes(report));control_summary[scope]=dict(Counter(r['status'] for r in report))
        job_targets=[['Alpha' if ref!='8:14' else 'Beta',ref] for ref in controls['job']] if self_test else [['Iob',ref] for ref in controls['job']]
        job_controls=control_report(work/'job','job',job_targets);cm.write(out/'28_job_postblind_locus_controls.csv',cm.csv_bytes(job_controls))
        events.append('HISTORICAL_LOADED')
        if self_test:
            archive=work/'synthetic_history.zip';hist=[dict(relation_id='SYN:H1',source_clause_id='101',target_clause_id='105',relation_type='HISTORICAL_CANDIDATE',provenance=[])]
            with zipfile.ZipFile(archive,'x') as z:z.writestr('history/01_hierarchy_relation_inventory.csv',cm.csv_bytes(hist))
        else:archive=cm.ROOT/cfg['archive']['path'];cm.require(cm.sha(archive.read_bytes())==cfg['archive']['sha256'],'historical archive SHA')
        history,comparison,upstream_count=historical(work/'job',archive,out)
        early=early_marker_judgments(work/'job',archive);cm.write(out/'29_hsa1_hsa2_marker_postblind_comparison.csv',cm.csv_bytes(early))
        cm.write(out/'16_historical_relation_marker_first_audit.csv',cm.csv_bytes(history));cm.write(out/'17_job_postblind_comparison.csv',cm.csv_bytes(comparison))
        cases,packet=review(work/'job',comparison);cm.write(out/'23_marker_family_human_review_cases.csv',cm.csv_bytes(cases));cm.write(out/'24_marker_family_human_review_packet.md',packet)
        cm.write(out/'22_cross_corpus_method_control_summary.md',('# Cross-corpus method controls\n\n'+json.dumps(control_summary,indent=2)+'\n\nAll lookup occurred after five independent freezes. Non-recovery and adjunct segmentation differences are preserved. No Jin hierarchy is imposed.\n').encode())
        cm.write(out/'25_methodological_reconstruction_report.md',('# MFR methodological reconstruction\n\n'+METHOD+'\nBook equality is a feature, never eligibility. No pre-adjudication one-mother constraint. All historical decisions remain original; unknown discovery chronology is PROVENANCE_UNCLEAR, never fabricated contamination or verified evidence-first status.\n').encode())
        cm.write(out/'26_next_scope.md','# Next scope\n\nMFR.0.2 — Human Marker-Family and Relation Adjudication. Only then MFR.0.3 — Adjudicated Relation to Text-Hierarchy Assembly. Plot/narrative/rhetoric integration follows hierarchy assembly.\n'.encode('utf8'))
        for scope in SCOPES:
            cm.require(cm.verify(work/scope,'12_job_blind_manifest.csv') and cm.sha((work/scope/'12_job_blind_manifest.csv').read_bytes())==frozen[scope],'blind output mutated')
            shutil.copytree(work/scope,out/'blind'/scope,copy_function=os.link)
        for path in (work/'job').iterdir():
            if path.name[:2].isdigit():os.link(path,out/path.name)
        manifestrows=[]
        for scope in SCOPES[1:]:
            for row in cm.rows((work/scope/'12_job_blind_manifest.csv').read_bytes()):manifestrows.append(dict(scope=scope,**row))
        cm.write(out/'14_control_blind_manifests.csv',cm.csv_bytes(manifestrows));cm.write(out/'15_control_blind_hashes.json',cm.js({s:frozen[s] for s in SCOPES[1:]}))
        machine_fields={'review_case_id','family_id','family_type','marker_ids'}
        post=dict(historical_count=len(history),historical_unchanged=all(r['historical_state_unchanged'] for r in history+comparison),review_blank=all(all(v==('UNREVIEWED' if k=='review_status' else '') for k,v in r.items() if k not in machine_fields) for r in cases),new_roots=[],tree_edges=[],new_judgments=[],new_parents=[],new_siblings=[],participant_arc='UNADJUDICATED')
        from milal_mfr_observation import FEATURES
        expected_assets=list(cfg['frozen_files'])+[cfg['archive']['path']]+([str(Path(bhsa)/(f+'.tf')) for f in FEATURES] if not self_test else [])
        def cross_cases(scope,label):return len({p['relation_candidate_id'] for r in control_reports[scope] for p in r['relation_evidence'] if p['cross_book'] and label in p['labels']})
        control_checks=dict(dsf_expected=len(control_reports['pentateuch']),dsf_recovered=sum(any('DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION' in e['tags'] for e in r['raw_evidence']) for r in control_reports['pentateuch']),prophet_cross_formal=cross_cases('prophets','FORMAL_PARALLEL_CANDIDATE'),death_cross_resumption=cross_cases('death','RESUMPTION_CANDIDATE'),ketuvim_cross_formal=cross_cases('daniel_ezra','FORMAL_PARALLEL_CANDIDATE'))
        death_index={(r['book'],r['reference']):r for r in control_reports['death']}
        control_checks['death_formula_expected']=len(controls['death_formula_loci']);control_checks['death_formula_recovered']=sum(any('AFTER_DEATH_TEMPORAL_CONSTRUCTION' in e['tags'] for e in death_index[tuple(locus)]['raw_evidence']) for locus in controls['death_formula_loci'])
        control_checks['death_pairs_expected']=len(controls['death_resumption_pairs']);control_checks['death_pairs_recovered']=0
        for source_locus,target_locus in controls['death_resumption_pairs']:
            source_case=death_index[tuple(source_locus)];target_case=death_index[tuple(target_locus)]
            control_checks['death_pairs_recovered']+=any(p['source_marker_id'] in source_case['marker_ids'] and p['target_marker_id'] in target_case['marker_ids'] and 'TEMPORAL_RESUMPTION_CANDIDATE' in p['labels'] for p in source_case['relation_evidence'])
        evidence=dict(phases=phases,behavior=contract,audit=audit,expected_assets=expected_assets,baseline=base,events=events,post=post,static=static,control_checks=control_checks,expected_clauses=20 if self_test else cfg['expected_job_clauses'],expected_historical_count=1 if self_test else 250,consumer_files=[str(p) for p in (cm.ROOT/'src').glob('*r4_4*.py')]+[str(p) for p in (cm.ROOT/'scripts').glob('*r4_4*')],final_manifest_valid=True)
        metadata=dict(stage='MFR.0.1',baseline=cfg['baseline'],mode='SYNTHETIC' if self_test else 'REAL_BHSA_2021',events=events,blind_manifest_sha256=frozen,summary={s:phases[s]['meta'] for s in SCOPES},provenance_counts=dict(Counter(r['reuse_class'] for r in audit)),historical_provenance_counts=dict(Counter(r['classification'] for r in history)),historical_comparison_counts=dict(Counter(r['status'] for r in comparison)),historical_relations=len(history),upstream_members_preserved=upstream_count,control_summary=control_summary,new_human_judgments=len(post['new_judgments']),new_accepted_relations=len(post['new_parents'])+len(post['new_siblings']),new_roots=len(post['new_roots']),participant_arc=post['participant_arc'],consumer_implemented=bool(evidence['consumer_files']),readiness=['MARKER_FIRST_BASELINE_ESTABLISHED','READY_FOR_MARKER_RELATION_HUMAN_REVIEW'],external_release_gates=['DETERMINISTIC_RERUN','FULL_REGRESSION_PASS','SKIP_ZERO'])
        metadata['control_checks']=control_checks;metadata['stage_code_sha256']={p.relative_to(cm.ROOT).as_posix():cm.sha(p.read_bytes()) for p in sorted((cm.ROOT/'src').glob('milal_mfr_*.py'))}
        cm.write(out/'90_run_metadata.json',cm.js(metadata));cm.manifest(out,'99_manifest_sha256.csv');evidence['final_manifest_valid']=cm.verify(out,'99_manifest_sha256.csv');checks=gt.evaluate(evidence);cm.require(all(checks.values()),'failed gates '+str([k for k,v in checks.items() if not v]))
        cm.write(out/'27_gates.csv',cm.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]));cm.manifest(out,'99_manifest_sha256.csv');cm.require(cm.verify(out,'99_manifest_sha256.csv'),'final manifest')
        zp=cm.deterministic_zip(out);print(json.dumps(dict(zip=str(zp),sha256=cm.sha(zp.read_bytes()),gates=len(checks),summary={s:phases[s]['meta']['counts'] for s in SCOPES})),flush=True)
    finally:cm.write(work/'runner_utf8.log','\n'.join(logs).encode('utf8'))
    return out

def regression(path):
    import unittest,time
    begin=time.monotonic();path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.with_suffix('.log').open('w',encoding='utf8') as stream:result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.discover(str(cm.ROOT/'tests')))
    receipt=dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),seconds=round(time.monotonic()-begin,3));cm.write(path,cm.js(receipt));print(json.dumps(receipt));cm.require(result.wasSuccessful() and not result.skipped,'full regression failed')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--bhsa');p.add_argument('--self-test',action='store_true');p.add_argument('--regression-receipt');p.add_argument('--regression-only');a=p.parse_args()
    if a.regression_only:regression(a.regression_only)
    else:
        cm.require(a.out,'output required');execute(a.out,a.bhsa,a.self_test,a.regression_receipt)
