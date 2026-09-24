"""Frozen-input consolidation, physical freeze, controls, then blank review."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
import milal_mfr_common as cm
from milal_mfr01a_data import OUTPUTS,stream,table
from milal_mfr01a_provenance import SCOPES,baseline,extract,static_scan
from milal_mfr01a_gates import release_gates,final_gates

def regression(path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    with path.with_suffix('.log').open('w',encoding='utf8') as log:
        result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.discover(str(cm.ROOT/'tests')))
    receipt=dict(tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),seconds=round(time.monotonic()-start,3))
    cm.write(path,cm.js(receipt));print(json.dumps(receipt));cm.require(result.wasSuccessful() and not result.skipped,'full regression failed')

def execute(out,archive=None,self_test=False):
    out=Path(out).resolve();work=out.with_name(out.name+'_work')
    cm.require(not out.exists() and not work.exists() and not out.with_name(out.name+'_results.zip').exists(),'fresh output required')
    work.mkdir(parents=True);cfg=json.loads((cm.ROOT/'config/mfr_0_1a_job.json').read_bytes());base,receipts=baseline(cfg);issues=static_scan();cm.require(not issues,'static contamination: '+str(issues))
    if self_test:
        from milal_mfr01a_synthetic import make_archive
        archive=make_archive(work/'synthetic_upstream');expected=cm.sha(archive.read_bytes())
    else:archive=Path(archive or cm.ROOT/cfg['archive']['path']).resolve();expected=cfg['archive']['sha256']
    receipts.extend(extract(archive,expected,work));events=[];frozen={};metadata={};logs=[]
    try:
        for scope,prefix in SCOPES.items():
            command=[sys.executable,'-B','-X','utf8',str(cm.ROOT/'src/milal_mfr01a_blind.py'),'--input',str(work/'input'/scope),'--out',str(work/'consolidated'/scope),'--scope',scope,'--prefix',prefix]
            p=subprocess.run(command,cwd=cm.ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf8');logs.append(p.stdout)
            cm.require(p.returncode==0,p.stdout)
            d=work/'consolidated'/scope;frozen[scope]=cm.manifest(d,'consolidation_manifest.csv');cm.require(cm.verify(d,'consolidation_manifest.csv'),'freeze manifest failed')
            metadata[scope]=json.loads((d/'consolidation_metadata.json').read_bytes());events.append(scope+'_FREEZE')
            print(json.dumps(dict(frozen=scope,statistics=metadata[scope]['statistics'])),flush=True)
        if not self_test:
            actual=metadata['job']['statistics']['raw'];cm.require(all(actual[k]==v for k,v in cfg['expected_job'].items()),'Job frozen count mismatch')
        out.mkdir();shutil.copytree(work/'consolidated',out/'consolidated',copy_function=os.link)
        for p in (out/'consolidated/job').iterdir():
            if p.name in OUTPUTS.values():os.link(p,out/p.name)
        # Upstream archive is preserved byte-for-byte, but not read by children.
        shutil.copyfile(archive,out/'mfr01_frozen_input.zip')
        table(out/'01_mfr01a_input_integrity.csv',receipts)
        events.append('CONTROLS_LOADED')
        from milal_mfr01a_controls import validate
        controls,jobchecks,cc=validate(out,archive,self_test)
        table(out/'18_cross_corpus_consolidation_validation.csv',controls);table(out/'19_job_postconsolidation_controls.csv',jobchecks)
        from milal_mfr01a_review import packet
        human,fields=packet(out,out/'consolidated/job')
        stats=metadata['job']['statistics'];report='# Human-review evidence consolidation\n\n'+json.dumps(stats,ensure_ascii=False,indent=2)+'\n\n'
        report+='Raw family and relation rows remain unchanged in the frozen input archive. Default family review operates on exact occurrence-set bundles. Archive means reference, not invalidity. No target reduction percentage is used.\n\n'
        report+='Closure coverage is checked exactly as requested. MFR.0.1 may have constructed a source coverage endpoint mechanically at the next cessation; its presence is not independently verified closure strength. Coverage-linked rows are not demoted to achieve a reduction target.\n'
        cm.write(out/'20_human_review_reduction_report.md',report.encode('utf8'))
        cm.write(out/'23_method_compliance_report.md',b'# Method compliance\n\nConsolidation is not adjudication. Bundles retain distinct family claims. Every raw marker, family, membership, relation, coverage, nested and force identity has a crosswalk. Observation and signature bytes remain in the original upstream archive. No book boundary eligibility, scores, accepted relation, participant identity, parent or tree is introduced. All five scopes freeze before known loci are consulted. Original historical judgment members remain opaque, unchanged archive bytes.\n')
        cm.write(out/'24_next_scope.md',b'# Next scope\n\nMFR.0.2: Human Marker-Family and Relation Adjudication using consolidated cases. Hierarchy assembly and R4.4 implementation remain unauthorized by this stage.\n')
        checks={}
        for scope,m in metadata.items():
            for gate,passed in m['core_gates'].items():checks[scope+':'+gate]=passed
        manifests=[cm.verify(out/'consolidated'/s,'consolidation_manifest.csv') and cm.sha((out/'consolidated'/s/'consolidation_manifest.csv').read_bytes())==frozen[s] for s in SCOPES]
        evidence=dict(baseline=base,receipts=receipts,reads=[r for m in metadata.values() for r in m['input_code_receipts']],static_issues=issues,scopes=list(SCOPES),events=events,controls=cc,
            post=dict(cases=human,review_fields=fields,participant_arc='UNADJUDICATED'),manifests=manifests,consumer_files=[str(p) for p in (cm.ROOT/'src').glob('*r4_4*.py')]+[str(p) for p in (cm.ROOT/'scripts').glob('*r4_4*')])
        checks.update(release_gates(evidence));cm.require(all(checks.values()),'failed gates '+str([k for k,v in checks.items() if not v]))
        table(out/'25_gates.csv',[dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()])
        meta=dict(stage='MFR.0.1a',mode='SYNTHETIC' if self_test else 'FROZEN_MFR_0_1_REAL',baseline=cfg['baseline'],upstream_sha256=expected,events=events,consolidation_freezes=frozen,
            statistics={s:m['statistics'] for s,m in metadata.items()},control_checks=cc,review_cases=len(human),run_gates=len(checks),gate_definitions=len(metadata['job']['core_gates'])+len(release_gates(evidence)),
            participant_arc='UNADJUDICATED',readiness=['MARKER_EVIDENCE_CONSOLIDATED','READY_FOR_MFR_0_2_HUMAN_ADJUDICATION'],external_release_gates=['FULL_REGRESSION_PASS','SKIP_ZERO','DETERMINISTIC_RERUN'],
            code_sha256={p.relative_to(cm.ROOT).as_posix():cm.sha(p.read_bytes()) for p in sorted((cm.ROOT/'src').glob('milal_mfr01a_*.py'))})
        cm.write(out/'90_run_metadata.json',cm.js(meta));cm.manifest(out,'99_manifest_sha256.csv');cm.require(cm.verify(out,'99_manifest_sha256.csv'),'final manifest failed')
        zp=cm.deterministic_zip(out);print(json.dumps(dict(zip=str(zp),sha256=cm.sha(zp.read_bytes()),gates=len(checks),job=stats)),flush=True)
    finally:cm.write(work/'runner_utf8.log','\n'.join(logs).encode('utf8'))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--input');p.add_argument('--self-test',action='store_true');p.add_argument('--regression-only');a=p.parse_args()
    if a.regression_only:regression(a.regression_only)
    else:cm.require(a.out,'output required');execute(a.out,a.input,a.self_test)
