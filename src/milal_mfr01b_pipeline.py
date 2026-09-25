"""Verified frozen-input role audit, physical freeze, then controls and H1 packet."""
import argparse
import gc
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
import zipfile
import milal_mfr_common as cm
import milal_mfr01b_data as data
import milal_mfr01b_roles as roles
import milal_mfr01b_evidence as evidence
import milal_mfr01b_configuration as configuration
import milal_mfr01b_core as core
import milal_mfr01b_gates as gates
import milal_mfr01b_io as io

def blind(projected,rules_path,out):
    out=Path(out).resolve();cm.require(not out.exists(),'fresh blind output required');out.mkdir(parents=True)
    modules=[cm,data,roles,evidence,configuration,core,gates,io,sys.modules['milal_mfr01a_data']]
    code=[Path(m.__file__).resolve() for m in modules]+[Path(__file__).resolve()]
    allowed=[Path(projected).resolve(),Path(rules_path).resolve(),*code];reads=io.guard(allowed,out)
    rules=json.loads(Path(rules_path).read_bytes());stats={};checks={};trace=[]
    with zipfile.ZipFile(projected) as z:
        expected=set(z.namelist())
        for scope in io.SCOPES:
            d=io.load(z,scope,trace);o=core.build(d,rules);gg=gates.core_gates(d,o,rules);cm.require(all(gg.values()),'core gates '+str([k for k,v in gg.items() if not v]))
            for key,records in o.items():data.table(out/scope/data.OUTPUTS[key],records)
            stats[scope]=core.statistics(d,o);checks.update({scope+':'+k:v for k,v in gg.items()});del d,o;gc.collect()
    cm.require(set(trace)==expected and len(trace)==len(expected),'blind member readset incomplete')
    receipts={p.name:data.digest(p) for p in code}
    cm.write(out/'blind_metadata.json',cm.js(dict(statistics=stats,gates=checks,member_reads=trace,allowed_members=sorted(expected),code_sha256=receipts,readset_valid=set(reads)=={str(p).casefold() for p in allowed})))

def regression(path):
    path=Path(path);start=time.monotonic()
    with path.with_suffix('.log').open('w',encoding='utf8') as f:r=unittest.TextTestRunner(stream=f,verbosity=2).run(unittest.defaultTestLoader.discover(str(cm.ROOT/'tests')))
    result=dict(tests_run=r.testsRun,failures=len(r.failures),errors=len(r.errors),skipped=len(r.skipped),seconds=round(time.monotonic()-start,3))
    cm.write(path,cm.js(result));print(json.dumps(result));cm.require(r.wasSuccessful() and not r.skipped,'full regression failed')

def execute(out,archive=None,self_test=False):
    out=Path(out).resolve();work=out.with_name(out.name+'_work')
    cm.require(not out.exists() and not work.exists() and not out.with_name(out.name+'_results.zip').exists(),'fresh output required');work.mkdir(parents=True)
    cfg=json.loads((cm.ROOT/'config/mfr_0_1b_job.json').read_bytes());pins=io.baseline(cfg);issues=io.scan();cm.require(not issues,'static safeguards '+str(issues))
    if self_test:
        from milal_mfr01b_synthetic import package
        archive=package(work);expected=data.digest(archive)
    else:archive=Path(archive or cm.ROOT/cfg['archive']['path']).resolve();expected=cfg['archive']['sha256']
    a_receipt=io.verify_zip(archive,expected)
    raw=work/'mfr01_frozen_input.zip'
    with zipfile.ZipFile(archive) as z,raw.open('xb') as f:
        with z.open('mfr01_frozen_input.zip') as member:shutil.copyfileobj(member,f)
    rawhash=data.digest(raw) if self_test else cfg['embedded_raw_sha256'];r_receipt=io.verify_zip(raw,rawhash)
    projected=io.project(archive,raw,work)
    command=[sys.executable,'-B','-X','utf8',str(Path(__file__).resolve()),'--blind',str(projected),'--out',str(work/'audit')]
    p=subprocess.run(command,cwd=cm.ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf8');cm.write(work/'blind_runner.log',p.stdout.encode('utf8'));cm.require(p.returncode==0,p.stdout)
    freeze=cm.manifest(work/'audit','freeze_manifest.csv');cm.require(cm.verify(work/'audit','freeze_manifest.csv'),'freeze verification')
    meta=json.loads((work/'audit/blind_metadata.json').read_bytes());events=['ROLE_AND_RELATION_OUTPUTS_FROZEN']
    out.mkdir();shutil.copytree(work/'audit',out/'audit',copy_function=os.link)
    for f in (out/'audit/job').iterdir():os.link(f,out/f.name)
    shutil.copyfile(archive,out/'mfr01a_frozen_input.zip');shutil.copyfile(work/'blind_input_receipts.json',out/'input_projection_receipts.json')
    from milal_mfr01b_controls import validate
    events.append('CONTROLS_LOADED');external,job,control=validate(out,raw,archive,self_test)
    data.table(out/'17_cross_corpus_role_validation.csv',external);data.table(out/'18_job_postfreeze_validation.csv',job)
    from milal_mfr01b_review import packet
    with zipfile.ZipFile(projected) as z:d=io.load(z,'job',[])
    from milal_mfr01a_data import stream
    o={k:list(stream(out/'audit/job'/name)) for k,name in data.OUTPUTS.items()}
    human,fields=packet(out,d,o)
    env=dict(baseline=bool(pins),raw_integrity=r_receipt['manifest_verified'] and r_receipt['crc_verified'],consolidated_integrity=a_receipt['manifest_verified'] and a_receipt['crc_verified'],
        controls=control,static_issues=issues,readsets=[meta['readset_valid'],set(meta['member_reads'])==set(meta['allowed_members'])],events=events,human_rows=human,human_fields=fields,
        consumers=[str(p) for p in (cm.ROOT/'src').glob('*r4_4*.py')]+[str(p) for p in (cm.ROOT/'scripts').glob('*r4_4*')],participant_arc='UNADJUDICATED',manifests=[cm.verify(out/'audit','freeze_manifest.csv'),data.digest(out/'audit/freeze_manifest.csv')==freeze])
    checks=dict(meta['gates'],**gates.release_gates(env));cm.require(all(checks.values()),'release gates '+str([k for k,v in checks.items() if not v]));data.table(out/'24_gates.csv',[dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()])
    report='# Human review scope\n\n'+json.dumps(meta['statistics']['job'],ensure_ascii=False,indent=2)+'\n\nH1/R1/C1 are separate dependency-complete phases. Raw evidence is retained in the complete frozen input ZIP. The closure archive also contains non-discourse target candidates with independent evidence; archive is not rejection.\n'
    cm.write(out/'19_human_review_scope_report.md',report.encode('utf8'))
    cm.write(out/'22_method_compliance_report.md',b'# Method compliance\n\nJob: complete role, provenance and configuration audit. Other corpora: complete marker/bundle role overlays and unchanged frozen relation control checks. Five role outputs and Job relation outputs freeze before reference lookup. No new discovery, accepted relation, mother, root or hierarchy. Participant arc UNADJUDICATED. Computational root groups describe provenance, not statistical independence or strength scores.\n')
    cm.write(out/'23_next_scope.md',b'# Next scope\n\nMFR.0.2A: Hierarchy-Competing Configuration Adjudication. Then separate MFR.0.2B resumption and MFR.0.2C closure batches. No whole-book hierarchy assembly, root or literary labels. No feedback into discovery.\n')
    final=dict(stage='MFR.0.1b',mode='SYNTHETIC' if self_test else 'FROZEN_REAL',baseline=cfg['baseline'],upstream_sha256=expected,raw_sha256=rawhash,frozen_file_count=len(pins),archive_receipts=[a_receipt,r_receipt],
        freeze_sha256=freeze,events=events,statistics=meta['statistics'],controls=control,run_gates=len(checks),core_gate_definitions=len(gates.core_gates(d,o,json.loads((cm.ROOT/'config/mfr_0_1b_role_rules.json').read_bytes()))),release_gate_definitions=len(gates.release_gates(env)),
        code_sha256={p.relative_to(cm.ROOT).as_posix():data.digest(p) for p in sorted((cm.ROOT/'src').glob('milal_mfr01b_*.py'))},rules_sha256=data.digest(cm.ROOT/'config/mfr_0_1b_role_rules.json'),
        human_cases=len(human),human_fields=list(fields),participant_arc='UNADJUDICATED',readiness=['MARKER_ROLE_AND_EVIDENCE_INDEPENDENCE_ESTABLISHED','READY_FOR_MFR_0_2A_HIERARCHY_CONFIGURATION_ADJUDICATION'])
    cm.write(out/'90_run_metadata.json',cm.js(final));cm.manifest(out,'99_manifest_sha256.csv');cm.require(cm.verify(out,'99_manifest_sha256.csv'),'final manifest')
    z=cm.deterministic_zip(out);print(json.dumps(dict(zip=str(z),sha256=data.digest(z),gates=len(checks),statistics=meta['statistics']['job'])),flush=True);return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out');p.add_argument('--input');p.add_argument('--self-test',action='store_true');p.add_argument('--blind');p.add_argument('--regression-only');a=p.parse_args()
    if a.regression_only:regression(a.regression_only)
    elif a.blind:blind(a.blind,cm.ROOT/'config/mfr_0_1b_role_rules.json',a.out)
    else:cm.require(a.out,'output required');execute(a.out,a.input,a.self_test)
