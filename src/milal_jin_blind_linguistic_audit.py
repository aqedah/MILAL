"""Phase A executable. Only neutral targets, raw linguistic TF features and rules."""
from __future__ import annotations
import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys

import milal_jin_io as io
import milal_jin_relation_rules as rules_module

TARGET_FIELDS={'audit_target_id','book','chapter','verse'}
FORBIDDEN={'relation_type','human_judgment','structural_function','same_level','child_of','cycle','seam','composition_group','accepted_relation','parent_id','necessity_status','mother','tab','pargr','rela','code'}
SAFE_MODULES={'milal_jin_io','milal_jin_relation_rules','milal_jin_blind_linguistic_audit'}


def neutral(value):
    if isinstance(value,dict):
        io.require(not (set(value)&FORBIDDEN),'forbidden discovery fields: '+str(set(value)&FORBIDDEN))
        for v in value.values():neutral(v)
    elif isinstance(value,list):
        for v in value:neutral(v)
    elif isinstance(value,str):
        io.require(not any(v in value for v in ('H:HSA','SAME_LEVEL_SIBLING','HIERARCHICALLY_ABOVE','POST_DIALOGUE_JOB','ELIHU_SPEECH_SEQUENCE','SEAM_A','CHILD_OF')),'human-semantic value in discovery')


def install_guard(allowed,out):
    """CPython audit hook enforces the file-read and MILAL-module allowlists."""
    paths={str(Path(p).resolve()).casefold():label for p,label in allowed.items()};out=str(Path(out).resolve()).casefold();trace=[]
    io.require(not any(k.startswith('milal_') and k not in SAFE_MODULES for k in sys.modules),'human-capable module preloaded')
    def hook(event,args):
        if event=='import':
            name=args[0];io.require(not name.startswith('milal_') or name in SAFE_MODULES,'prohibited MILAL import')
        if event!='open' or isinstance(args[0],int):return
        p=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode=args[1];flags=args[2]
        writing=(isinstance(mode,str) and any(k in mode for k in 'wax+')) or (isinstance(flags,int) and flags & (os.O_WRONLY|os.O_RDWR|os.O_CREAT))
        if writing:io.require(p.startswith(out+os.sep),'write outside Phase A output')
        else:
            io.require(p in paths,'read outside Phase A allowlist: '+p)
            trace.append(dict(path=p,source_id=paths[p]))
    sys.addaudithook(hook)
    return trace


def inventory(targets,clauses):
    neutral(targets);io.require(bool(targets) and bool(clauses),'empty blind target/corpus');out=[];seen=set()
    for t in targets:
        io.require(set(t)==TARGET_FIELDS and t['audit_target_id'].startswith('JT'),'neutral target schema')
        io.require(t['audit_target_id'] not in seen,'duplicate target ID');seen.add(t['audit_target_id'])
        hits=[c for c in clauses if any(w['chapter']==t['chapter'] and w['verse']==t['verse'] for w in c['words'])]
        io.require(hits,'target reference absent from raw book')
        out.append(dict(**t,clause_id=[c['clause_id'] for c in hits],clause_atom_id=sorted({a for c in hits for a in c['clause_atom_ids']}),
            anchor_start=min(c['word_start'] for c in hits),anchor_end=max(c['word_end'] for c in hits)))
    return out


def discover(targets,clauses,rules):
    neutral(clauses);neutral(rules)
    nn=inventory(targets,clauses);ff=rules_module.extract(clauses,rules);index={f['clause_id']:f for f in ff}
    pairs=[];hypotheses=[];mothers=[];scans=Counter();scanned=set()
    for target in nn:
        anchor_ids=set(target['clause_id'])
        for anchor in (index[i] for i in target['clause_id']):
            # Whole-book predecessors, plus a declared local forward syntactic window.
            options=[(pre,anchor,'TARGET_IS_LATER_CLAUSE') for pre in ff if pre['word_end']<anchor['word_start']]
            options += [(anchor,cur,'TARGET_IS_EARLIER_CONTEXT') for cur in ff[anchor['sequence_index']+1:anchor['sequence_index']+1+rules['local_dependency_clause_window']] if cur['word_start']>anchor['word_end'] and cur['clause_id'] not in anchor_ids]
            for pre,cur,role in options:
                key=(target['audit_target_id'],pre['clause_id'],cur['clause_id'])
                if key in scanned:continue
                scanned.add(key);scans[role]+=1
                ev=rules_module.evidence(pre,cur,rules);scans[ev['relation_hypothesis']]+=1
                if not ev['eligible']:continue
                ident='JP:'+':'.join(map(str,key));evidence_id='JE:'+':'.join(map(str,key))
                pairs.append(dict(pair_id=ident,evidence_id=evidence_id,audit_target_id=target['audit_target_id'],target_role=role,
                    preceding_clause_id=pre['clause_id'],later_clause_id=cur['clause_id'],preceding_ref=pre['reference'],later_ref=cur['reference'],
                    preceding_clause_atom_ids=pre['clause_atom_ids'],later_clause_atom_ids=cur['clause_atom_ids'],
                    feature_ids=[pre['feature_id'],cur['feature_id']],trigger_reason_codes=ev['trigger_reason_codes'],evidence_flags=ev['evidence_flags']))
                hypotheses.append(dict(pair_id=ident,evidence_id=evidence_id,relation_hypothesis=ev['relation_hypothesis'],
                    parataxis_supported=ev['parataxis_supported'],hypotaxis_supported=ev['hypotaxis_supported'],rule_bundles=ev['rule_bundles'],
                    relation_candidate_status=ev['relation_candidate_status'],automatic_resolution=False,referential_limit=ev['referential_limit']))
                if ev['hypotaxis_supported']:
                    mothers.append(dict(pair_id=ident,audit_target_id=target['audit_target_id'],daughter_clause_id=cur['clause_id'],mother_candidate_clause_id=pre['clause_id'],
                        target_role=role,evidence_id=evidence_id,relation_candidate_status='UNADJUDICATED',automatic_resolution=False))
    summary=dict(target_count=len(nn),raw_clause_count=len(ff),scanned_predecessor_pair_count=scans['TARGET_IS_LATER_CLAUSE'],
        scanned_forward_context_pair_count=scans['TARGET_IS_EARLIER_CONTEXT'],scanned_pair_count=len(scanned),eligible_pair_count=len(pairs),
        no_support_excluded_pair_count=scans['NO_LINGUISTIC_SUPPORT'],relation_hypotheses={k:scans[k] for k in rules_module.LABELS})
    return dict(targets=nn,features=ff,pairs=pairs,hypotheses=hypotheses,mothers=mothers,summary=summary)


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--targets',required=True);p.add_argument('--rules',required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--tf-data');g.add_argument('--synthetic-corpus')
    p.add_argument('--out',required=True);args=p.parse_args(argv)
    out=Path(args.out).resolve();io.require(not out.exists(),'Phase A output exists')
    allowed={Path(args.targets).resolve():'NEUTRAL_TARGETS',Path(args.rules).resolve():'LINGUISTIC_RULES'}
    codes=[Path(__file__),Path(io.__file__),Path(rules_module.__file__)]
    allowed.update({f.resolve():'DISCOVERY_CODE/'+f.name for f in codes})
    if args.tf_data:allowed.update({(Path(args.tf_data)/(f+'.tf')).resolve():'BHSA2021/'+f+'.tf' for f in io.RAW_FEATURES})
    else:allowed[Path(args.synthetic_corpus).resolve()]='SYNTHETIC_RAW_CORPUS'
    trace=install_guard(allowed,out)
    targets=json.loads(Path(args.targets).read_bytes());rules=json.loads(Path(args.rules).read_bytes())
    io.require(all(t['book']==rules['book'] for t in targets),'target book differs from configured corpus')
    if args.tf_data:clauses,tf_receipts=io.raw_corpus(args.tf_data,rules['bhsa_book_feature'])
    else:clauses=json.loads(Path(args.synthetic_corpus).read_bytes());tf_receipts=[]
    m=discover(targets,clauses,rules)
    code_hashes={f.name:io.sha(f.read_bytes()) for f in codes}
    source_rows=[dict(source_id=label,sha256=io.sha(path.read_bytes()),source_class='RAW_LINGUISTIC' if label.startswith('BHSA') else label,
                      human_source=False) for path,label in sorted(allowed.items(),key=lambda x:x[1])]
    actual=sorted({r['source_id'] for r in trace});io.require(actual==sorted(allowed.values()),'actual source-read inventory')
    meta=dict(version='R4.4-CONTRACT.JIN.0.2-PHASE-A',status='FROZEN_BLIND_CANDIDATES',mode='REAL_BHSA_2021' if args.tf_data else 'SYNTHETIC',
        summary=m['summary'],book=rules['book'],bhsa_book_feature=rules['bhsa_book_feature'],loaded_sources=actual,human_source_count=sum(r['human_source'] for r in source_rows),
        native_hierarchy_source_count=sum(Path(r['source_id']).stem in io.NATIVE_FEATURES for r in source_rows),
        source_access_policy='CPYTHON_AUDIT_HOOK_EXACT_READ_ALLOWLIST; MILAL_IMPORT_ALLOWLIST',
        code_sha256=code_hashes,feature_receipts=tf_receipts,rule_sha256=io.sha(Path(args.rules).read_bytes()))
    files={name:io.csv_bytes(m[key],fields) for name,key,fields in [
        ('01_blind_target_inventory.csv','targets',None),('02_blind_linguistic_features.csv','features',None),
        ('03_blind_candidate_pairs.csv','pairs',['pair_id','evidence_id','audit_target_id','target_role','preceding_clause_id','later_clause_id','preceding_ref','later_ref','preceding_clause_atom_ids','later_clause_atom_ids','feature_ids','trigger_reason_codes','evidence_flags']),
        ('04_blind_relation_hypotheses.csv','hypotheses',['pair_id','evidence_id','relation_hypothesis','parataxis_supported','hypotaxis_supported','rule_bundles','relation_candidate_status','automatic_resolution','referential_limit']),
        ('05_blind_hypotaxis_mother_candidates.csv','mothers',['pair_id','audit_target_id','daughter_clause_id','mother_candidate_clause_id','target_role','evidence_id','relation_candidate_status','automatic_resolution'])]}
    files['06_blind_discovery_source_audit.csv']=io.csv_bytes(source_rows);files['18_phase_a_metadata.json']=io.js(meta)
    files['19_blind_rule_config.json']=io.js(rules)
    io.seal(files,'07_blind_discovery_manifest.csv');io.require(io.manifest_ok(files,'07_blind_discovery_manifest.csv'),'blind freeze manifest')
    io.publish(files,out,zip_output=False)
    # Physical paths go to the execution log, not nondeterministic result members.
    print(json.dumps(dict(phase='A',loaded_source_files=sorted({r['path'] for r in trace}),human_source_count=0,freeze_sha256=io.sha(files['07_blind_discovery_manifest.csv']),summary=m['summary']),ensure_ascii=False))
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
