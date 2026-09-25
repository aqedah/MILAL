"""Verified frozen archives and a minimal blind member projection."""
import ast
import encodings.cp437
import hashlib
import json
import os
import re
import subprocess
import zipfile
from pathlib import Path
import milal_mfr_common as cm
from milal_mfr01b_data import TABLES, ROLE_TABLES, FULL_TABLES, zip_rows, prepare, digest

SCOPES=('job','pentateuch','prophets','death','daniel_ezra')
PRIOR={'old_bundles':'03_marker_evidence_bundle_registry.csv','old_cases':'11_relation_evidence_cases.csv','old_crosswalk':'10_raw_relation_case_crosswalk.csv',
       'expansions':'06_marker_expansion_relations.csv','old_family_review':'08_family_review_universe.csv','old_relation_review':'15_relation_review_universe.csv'}
CORE_FILES=('data','roles','evidence','configuration','core')

def scan(code=None):
    code=code if code is not None else {k:(cm.ROOT/'src'/('milal_mfr01b_'+k+'.py')).read_text(encoding='utf8') for k in CORE_FILES}
    issues=[]
    for name,text in code.items():
        if re.search(r'\b\d{1,2}:\d{1,3}\b',text):issues.append(name+':REFERENCE')
        if any(x.lower() in text.lower() for x in ('prologue','dialogue cycle','testing scene','Elihu section','divine speech','epilogue','macro root','CHILD_OF','SAME_LEVEL_SIBLING')):issues.append(name+':STRUCTURAL_LABEL')
        for node in ast.walk(ast.parse(text)):
            if isinstance(node,(ast.Import,ast.ImportFrom)):
                names=[a.name for a in node.names] if isinstance(node,ast.Import) else [node.module or '']
                if any(n.startswith('milal_') and not (n.startswith('milal_mfr01b_') or n in ('milal_mfr_common','milal_mfr01a_data')) for n in names):issues.append(name+':IMPORT')
            if isinstance(node,(ast.If,ast.IfExp,ast.comprehension)):
                tests=[node.test] if hasattr(node,'test') else node.ifs
                if any(any(isinstance(x,ast.Constant) and x.value in ('book','chapter','verse') for x in ast.walk(t)) for t in tests):issues.append(name+':REFERENCE_FILTER')
    return issues

def baseline(cfg):
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=cm.ROOT).decode().strip()
    ok=subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],head],cwd=cm.ROOT).returncode==0
    cm.require(ok,'baseline ancestry mismatch')
    receipts=[dict(path=p,expected_sha256=h,actual_sha256=digest(cm.ROOT/p)) for p,h in cfg['frozen_files'].items()]
    cm.require(all(r['actual_sha256']==r['expected_sha256'] for r in receipts),'frozen repository changed')
    return receipts

def verify_zip(path,expected):
    cm.require(digest(path)==expected,'ZIP SHA256 mismatch '+str(path))
    with zipfile.ZipFile(path) as z:
        names=z.namelist();cm.require(len(names)==len(set(names)) and z.testzip() is None,'ZIP CRC or duplicate names')
        manifest=list(zip_rows(z,'99_manifest_sha256.csv'));cm.require({r['path'] for r in manifest}==set(names)-{'99_manifest_sha256.csv'},'manifest universe')
        for r in manifest:
            h=hashlib.sha256()
            with z.open(r['path']) as f:
                while chunk:=f.read(1024*1024):h.update(chunk)
            cm.require(h.hexdigest()==r['sha256'],'member SHA256 '+r['path'])
    return dict(archive_sha256=expected,members=len(names),manifest_verified=True,crc_verified=True)

def project(archive,raw,work):
    dest=Path(work)/'blind_input.zip';receipts=[]
    with zipfile.ZipFile(archive) as a,zipfile.ZipFile(raw) as r,zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for scope in SCOPES:
            items=[(r,'blind/'+scope+'/'+TABLES[k],scope+'/'+k+'.csv','MFR.0.1') for k in (FULL_TABLES if scope=='job' else ROLE_TABLES)]
            items += [(a,'consolidated/'+scope+'/'+name,scope+'/'+key+'.csv','MFR.0.1a') for key,name in PRIOR.items() if scope=='job' or key=='old_bundles']
            for src,name,target,layer in items:
                h=hashlib.sha256();info=zipfile.ZipInfo(target,(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
                with src.open(name) as f,z.open(info,'w',force_zip64=True) as out:
                    while chunk:=f.read(1024*1024):h.update(chunk);out.write(chunk)
                receipts.append(dict(projected_member=target,source_layer=layer,source_member=name,sha256=h.hexdigest()))
    cm.write(Path(work)/'blind_input_receipts.json',cm.js(receipts));return dest

def load(z,scope,trace):
    keys=list(FULL_TABLES if scope=='job' else ROLE_TABLES)+[k for k in PRIOR if scope=='job' or k=='old_bundles']
    d={}
    for k in keys:
        name=scope+'/'+k+'.csv';d[k]=list(zip_rows(z,name));trace.append(name)
    return prepare(d)

def guard(allowed,out):
    paths={str(Path(p).resolve()).casefold() for p in allowed};base=str(Path(out).resolve()).casefold()+os.sep;trace=[]
    def hook(event,args):
        if event=='import':
            name=args[0]
            if name.startswith('milal_'):cm.require(name.startswith('milal_mfr01b_') and not name.endswith(('_controls','_review','_synthetic')) or name in ('milal_mfr_common','milal_mfr01a_data'),'forbidden blind import')
        if event!='open' or isinstance(args[0],int):return
        p=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode,flags=args[1:3]
        writing=isinstance(mode,str) and any(c in mode for c in 'wax+') or isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT)
        if writing:cm.require(p.startswith(base),'blind write outside output')
        else:cm.require(p in paths,'blind read outside allowlist');trace.append(p)
    import sys
    cm.require(not any(n.startswith('milal_') and not (n.startswith('milal_mfr01b_') or n in ('milal_mfr_common','milal_mfr01a_data')) for n in sys.modules),'blind module leakage')
    sys.addaudithook(hook);return trace
