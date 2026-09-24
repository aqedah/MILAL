"""Isolated focused discovery executable: one process and freeze per A/B/C."""
import argparse
import json
import os
from pathlib import Path
import sys
import milal_jin_io as io
import milal_jin_relation_rules as rr
import milal_jin_context_configuration as cc
from milal_jin_blind_linguistic_audit import neutral
from milal_jin_focused_common import Evidence
import milal_jin_job_1_13_mother_audit as audit_a
import milal_jin_speech_frame_audit as audit_b
import milal_jin_macro_parent_audit as audit_c

SAFE={'milal_jin_io','milal_jin_relation_rules','milal_jin_context_configuration','milal_jin_blind_linguistic_audit','milal_jin_focused_common','milal_jin_job_1_13_mother_audit','milal_jin_speech_frame_audit','milal_jin_macro_parent_audit','milal_jin_focused_blind'}
BUILD={'A':audit_a.build,'B':audit_b.build,'C':audit_c.build}


def guard(allowed,out):
    paths={str(Path(p).resolve()).casefold():v for p,v in allowed.items()};base=str(Path(out).resolve()).casefold();trace=[]
    io.require(not any(n.startswith('milal_') and n not in SAFE for n in sys.modules),'focused forbidden module preloaded')
    def hook(event,args):
        if event=='import':io.require(not args[0].startswith('milal_') or args[0] in SAFE,'focused forbidden import')
        if event!='open' or isinstance(args[0],int):return
        p=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode=args[1];flags=args[2]
        write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT))
        if write:io.require(p.startswith(base+os.sep),'focused write outside output')
        else:io.require(p in paths,'focused forbidden read');trace.append(dict(path=p,source_id=paths[p]))
    sys.addaudithook(hook);return trace


def main():
    p=argparse.ArgumentParser();p.add_argument('--audit',choices=list(BUILD),required=True);p.add_argument('--blind-input',required=True);p.add_argument('--rules',required=True);p.add_argument('--context-rules',required=True);p.add_argument('--tf-data');p.add_argument('--out',required=True);a=p.parse_args()
    inp=Path(a.blind_input);out=Path(a.out);allowed={inp/n:'FROZEN_BLIND/'+n for n in cc.FROZEN_NAMES}
    allowed.update({Path(a.rules):'NEUTRAL_FOCUSED_RULES',Path(a.context_rules):'NEUTRAL_CONTEXT_RULES'})
    for name in SAFE:allowed[Path(__file__).parent/(name+'.py')]='BLIND_CODE/'+name+'.py'
    if a.tf_data:allowed.update({Path(a.tf_data)/(n+'.tf'):'BHSA2021/'+n+'.tf' for n in io.RAW_FEATURES})
    trace=guard(allowed,out);blind={n:(inp/n).read_bytes() for n in cc.FROZEN_NAMES};io.require(io.manifest_ok(blind,'07_blind_discovery_manifest.csv'),'frozen blind manifest')
    for name in cc.FROZEN_NAMES[:5]:neutral(io.rows(blind[name]))
    rules=json.loads(Path(a.rules).read_bytes());context=json.loads(Path(a.context_rules).read_bytes());ling=json.loads(blind['19_blind_rule_config.json']);neutral(rules);neutral(context)
    old=json.loads(blind['18_phase_a_metadata.json']);io.require(old['human_source_count']==old['native_hierarchy_source_count']==0,'upstream blind source violation')
    features=io.rows(blind['02_blind_linguistic_features.csv']);receipts=[]
    if a.tf_data:
        raw,receipts=io.raw_corpus(a.tf_data,ling['bhsa_book_feature']);index={int(c['clause_id']):c for c in features}
        io.require({c['clause_id'] for c in raw}==set(index),'raw Job population differs')
        for c in raw:io.require(all(index[c['clause_id']][k]==v or (not isinstance(v,(list,dict,bool)) and str(index[c['clause_id']][k])==str(v)) for k,v in c.items()),'raw feature mismatch')
        io.require(receipts==old['feature_receipts'],'TF receipts changed')
    else:io.require(old['mode']=='SYNTHETIC','real blind stage requires raw BHSA')
    e=Evidence(features,io.rows(blind['01_blind_target_inventory.csv']),rules,context,ling);m=BUILD[a.audit](e,blind)
    sources=[dict(audit=a.audit,source_id=label,sha256=io.sha(path.read_bytes()),human_source=False,human_label_leakage=False,composition_source=False,native_hierarchy_source=False) for path,label in sorted(allowed.items(),key=lambda x:x[1])]
    io.require({r['source_id'] for r in sources}=={r['source_id'] for r in trace},'actual read receipt mismatch')
    files=m['files'];files.update(e.window_files());files['source_audit.csv']=io.csv_bytes(sources)
    files['metadata.json']=io.js(dict(audit=a.audit,status='FROZEN_BLIND_EVIDENCE',summary=m['summary'],rules=rules,raw_feature_receipts=receipts,source_counts={key:sum(r[key] for r in sources) for key in ('human_source','human_label_leakage','composition_source','native_hierarchy_source')},accepted_relations=[],new_human_judgments=[],new_parent_edges=[],selected_mothers=[]))
    io.seal(files,'blind_manifest.csv');io.publish(files,out,False)
    print(json.dumps(dict(audit=a.audit,freeze_sha256=io.sha(files['blind_manifest.csv']),sources=trace,summary=m['summary'])))

if __name__=='__main__':main()
