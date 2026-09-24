"""Opaque release integrity and executable input quarantine."""
import ast
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zipfile
import milal_mfr_common as cm
from milal_mfr01a_data import TABLES

SCOPES={'job':'M','pentateuch':'P','prophets':'H','death':'D','daniel_ezra':'K'}
CORE_FILES=('data','bundle','lattice','closure','relation','core','blind')

def static_scan(code=None):
    code=code or {name:(cm.ROOT/'src'/('milal_mfr01a_'+name+'.py')).read_text(encoding='utf8') for name in CORE_FILES}
    issues=[]
    for name,text in code.items():
        tree=ast.parse(text)
        if re.search(r'\b\d{1,2}:\d{1,3}\b',text):issues.append((name,'TARGET_REFERENCE'))
        for label in ('CHILD_OF','SAME_LEVEL_SIBLING','JOB_NARRATIVE_ROOT','OPENING_NARRATIVE_COMPLEX','ELIHU_SPEECH_SEQUENCE'):
            if label in text:issues.append((name,'STRUCTURAL_LABEL'))
        for n in ast.walk(tree):
            if isinstance(n,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in n.names] if isinstance(n,ast.Import) else [n.module or '']
                if any(x.startswith('milal_') and not (x.startswith('milal_mfr01a_') or x=='milal_mfr_common') for x in names):issues.append((name,'FORBIDDEN_IMPORT'))
            if name in ('core','bundle','lattice','relation','closure') and isinstance(n,(ast.If,ast.IfExp,ast.comprehension)):
                tests=[n.test] if hasattr(n,'test') else n.ifs
                if any(any(isinstance(x,ast.Constant) and x.value in ('book','chapter','verse') for x in ast.walk(t)) for t in tests):issues.append((name,'METADATA_ELIGIBILITY_FILTER'))
    return issues

def baseline(cfg):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cm.ROOT).decode().strip()
    obj=subprocess.check_output(['git','rev-parse',cfg['baseline']+'^{commit}'],cwd=cm.ROOT).decode().strip()
    ancestor=subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],head],cwd=cm.ROOT).returncode==0
    cm.require(ancestor and obj==cfg['baseline'],'baseline ancestry mismatch')
    receipts=[dict(path=p,expected_sha256=h,actual_sha256=cm.sha((cm.ROOT/p).read_bytes())) for p,h in cfg['frozen_files'].items()]
    cm.require(all(r['expected_sha256']==r['actual_sha256'] for r in receipts),'frozen repository file changed')
    return dict(expected=cfg['baseline'],object=obj,ancestor=ancestor),receipts

def extract(archive,expected,work):
    archive=Path(archive);digest=cm.sha(archive.read_bytes());cm.require(digest==expected,'MFR.0.1 ZIP SHA256 mismatch')
    receipts=[dict(path='UPSTREAM_ZIP',expected_sha256=expected,actual_sha256=digest)]
    with zipfile.ZipFile(archive) as z:
        names=z.namelist();cm.require(z.testzip() is None and len(names)==len(set(names)),'ZIP integrity/duplicate member')
        manifest=cm.rows(z.read('99_manifest_sha256.csv'));cm.require({r['path'] for r in manifest}==set(names)-{'99_manifest_sha256.csv'},'upstream manifest universe')
        for r in manifest:
            digest=hashlib.sha256()
            with z.open(r['path']) as stream:
                while chunk:=stream.read(1024*1024):digest.update(chunk)
            actual=digest.hexdigest();cm.require(actual==r['sha256'],'upstream member hash: '+r['path'])
            receipts.append(dict(path='UPSTREAM/'+r['path'],expected_sha256=r['sha256'],actual_sha256=actual))
        # No historical CSV or known-control table is parsed here.
        for scope in SCOPES:
            for name in TABLES.values():
                cm.write(Path(work)/'input'/scope/name,z.read('blind/'+scope+'/'+name))
    return receipts
