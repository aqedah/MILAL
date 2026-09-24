"""Preflight classification and static checks; never imported by blind discovery."""
from pathlib import Path
import ast
import json
import re
import subprocess
from collections import Counter
import milal_mfr_common as cm

BLIND_FILES=('milal_mfr_common.py','milal_mfr_observation.py','milal_mfr_signatures.py','milal_mfr_marker_discovery.py','milal_mfr_families.py','milal_mfr_force_evidence.py','milal_mfr_coverage.py','milal_mfr_relation_candidates.py','milal_mfr_blind.py')
LABELS=('CHILD_OF','SAME_LEVEL_SIBLING','JOB_NARRATIVE_ROOT','OPENING_NARRATIVE_COMPLEX','ELIHU_SPEECH_SEQUENCE','YHWH_JOB_RESPONSE_SEQUENCE','MACRO_TEXTUAL_HIERARCHY','STRICT_CLAUSE_HIERARCHY','prologue','epilogue','dialogue','cycle')

def classify(path):
    if path.startswith('BHSA2021/'):
        return 'OBSERVATION_SAFE',False,False,'Raw linguistic feature; hierarchy features excluded'
    if path=='src/milal_jin_io.py':
        tree=ast.parse((cm.ROOT/path).read_text(encoding='utf8'))
        deps=[n.module or '' for n in ast.walk(tree) if isinstance(n,ast.ImportFrom)]+[a.name for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names]
        if all(not d.startswith('milal_') for d in deps):return 'DERIVED_BLIND_SAFE',False,False,'Inspected serializer/raw feature reader; standard-library imports only; NOT reused by MFR'
    if path.startswith(('docs/','config/')) or path.endswith('.zip'):
        return 'POSTBLIND_ONLY',True,True,'Historical documentation/configuration/artifact; no blind reuse'
    return 'CONTAMINATED_OR_UNCLEAR',None,None,'Legacy executable/fixture/infrastructure dependency chain not certified for MFR; quarantined, not imported'

def audit(cfg,bhsa=None):
    result=[]
    for path,digest in sorted(cfg['frozen_files'].items()):
        cls,human,struct,reason=classify(path)
        result.append(dict(asset_path=path,asset_type=Path(path).suffix or 'TEXT',source_stage='PRE_MFR_BASELINE',dependency_summary=reason,human_dependency=human,structural_label_dependency=struct,reuse_class=cls,reason=reason,sha256=cm.sha((cm.ROOT/path).read_bytes()),expected_sha256=digest))
    result.append(dict(asset_path=cfg['archive']['path'],asset_type='ZIP',source_stage='JIN.0.9',dependency_summary='Historical complete package; loaded after every freeze',human_dependency=True,structural_label_dependency=True,reuse_class='POSTBLIND_ONLY',reason='Comparative provenance only',sha256=cm.sha((cm.ROOT/cfg['archive']['path']).read_bytes()),expected_sha256=cfg['archive']['sha256']))
    if bhsa:
        # Names are the new reader's fixed feature declaration, not old analytical code.
        from milal_mfr_observation import FEATURES
        for name in FEATURES:
            p=Path(bhsa)/(name+'.tf');cm.require(p.is_file(),'missing raw feature '+str(p))
            result.append(dict(asset_path=str(p),asset_type='TF',source_stage='BHSA2021',dependency_summary='Raw linguistic feature',human_dependency=False,structural_label_dependency=False,reuse_class='OBSERVATION_SAFE',reason='Explicit raw whitelist; no native hierarchy',sha256=cm.sha(p.read_bytes()),expected_sha256='LOCAL_RAW_SOURCE'))
    return result

def static_scan(code=None,rules=None):
    code=code or {n:(cm.ROOT/'src'/n).read_text(encoding='utf8') for n in BLIND_FILES};issues=[]
    for name,text in code.items():
        ast.parse(text)
        for value in re.findall(r'\b\d{1,2}:\d{1,3}\b',text):issues.append((name,'TARGET_REFERENCE',value))
        for label in LABELS:
            if label in text:issues.append((name,'STRUCTURAL_LABEL',label))
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
                for dep in names:
                    if dep.startswith('milal_') and dep+'.py' not in BLIND_FILES:issues.append((name,'FORBIDDEN_IMPORT',dep))
            if name=='milal_mfr_relation_candidates.py' and isinstance(node,(ast.If,ast.IfExp,ast.comprehension)):
                tests=[node.test] if hasattr(node,'test') else node.ifs
                for test in tests:
                    if any((isinstance(x,ast.Constant) and x.value in ('book','chapter','verse')) or (isinstance(x,ast.Attribute) and x.attr in ('book','chapter','verse')) for x in ast.walk(test)):issues.append((name,'METADATA_FILTER',ast.unparse(test)))
    ruletext=json.dumps(rules if rules is not None else json.loads((cm.ROOT/'config/mfr_0_1_blind_rules.json').read_bytes()))
    if re.search(r'\b\d{1,2}:\d{1,3}\b',ruletext) or any(s in ruletext for s in LABELS):issues.append(('RULES','CONTAMINATION',ruletext))
    return issues

def baseline(cfg):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cm.ROOT).decode().strip()
    ancestor=subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],head],cwd=cm.ROOT,capture_output=True).returncode==0
    cm.require(ancestor,'expected baseline not an ancestor')
    return dict(expected_baseline=cfg['baseline'],baseline_is_ancestor=ancestor,baseline_object=subprocess.check_output(['git','rev-parse',cfg['baseline']+'^{commit}'],cwd=cm.ROOT).decode().strip())

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--bhsa');p.add_argument('--out',required=True);a=p.parse_args();cfg=json.loads((cm.ROOT/'config/mfr_0_1_job.json').read_bytes())
    rr=audit(cfg,a.bhsa);issues=static_scan();cm.write(Path(a.out)/'01_existing_asset_provenance_audit.csv',cm.csv_bytes(rr));cm.write(Path(a.out)/'preflight.json',cm.js(dict(baseline=baseline(cfg),counts=dict(Counter(x['reuse_class'] for x in rr)),static_issues=issues)))
    cm.require(not issues,'static contamination '+str(issues));cm.require(all(r['sha256']==r['expected_sha256'] for r in rr if r['expected_sha256']!='LOCAL_RAW_SOURCE'),'frozen artifact changed');print('Provenance and static preflight PASS',len(rr))
