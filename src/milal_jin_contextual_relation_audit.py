"""C1 executable: isolated contextual consolidation of frozen blind evidence."""
import argparse
import json
import os
from pathlib import Path
import sys
import milal_jin_io as io
import milal_jin_context_configuration as context
from milal_jin_blind_linguistic_audit import neutral

SAFE={'milal_jin_io','milal_jin_relation_rules','milal_jin_blind_linguistic_audit',
      'milal_jin_context_configuration','milal_jin_contextual_relation_audit'}
TABLES={'01_context_supported_pair_inventory.csv':'supported','02_context_windows.csv':'windows',
 '03_context_signatures.csv':'signatures','04_context_correspondence.csv':'correspondence',
 '05_relation_scope_classification.csv':'scopes','06_contextual_relation_cases.csv':'cases',
 '07_contextual_case_membership.csv':'membership','08_insufficient_pair_archive.csv':'archive',
 '09_clause_internal_hypotaxis.csv':'clause_internal','10_contextual_macro_mother_candidates.csv':'macro_mothers',
 '30_context_auxiliary_membership.csv':'auxiliary','31_neutral_locus_inventory.csv':'targets'}


def install_guard(allowed,out):
    allowed={str(Path(p).resolve()).casefold():label for p,label in allowed.items()};base=str(Path(out).resolve()).casefold();trace=[]
    io.require(not any(n.startswith('milal_') and n not in SAFE for n in sys.modules),'C1 prohibited module preloaded')
    def audit(event,args):
        if event=='import':io.require(not args[0].startswith('milal_') or args[0] in SAFE,'C1 forbidden import')
        if event!='open' or isinstance(args[0],int):return
        path=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode=args[1];flags=args[2]
        writing=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT))
        if writing:io.require(path.startswith(base+os.sep),'C1 write outside output')
        else:
            io.require(path in allowed,'C1 forbidden read: '+path);trace.append(dict(path=path,source_id=allowed[path]))
    sys.addaudithook(audit);return trace


def serialize(m,blind,rules,sources,raw_receipts):
    empty_fields={'macro_mothers':list(m['scopes'][0])+['relation_family'] if m['scopes'] else ['pair_id','macro_projection_status','relation_family'],
                  'clause_internal':list(m['scopes'][0]) if m['scopes'] else ['pair_id','clause_internal_only'],
                  'auxiliary':['case_id','pair_id','evidence_id','context_id','reason','archive_status']}
    files={name:io.csv_bytes(m[key],empty_fields.get(key) if not m[key] else None) for name,key in TABLES.items()}
    files.update({'blind_input/'+name:data for name,data in blind.items()})
    mapping={r['pair_id']:[] for r in m['supported']+m['archive']}
    for r in m['membership']:mapping[r['pair_id']].append(r['case_id'])
    files['11_pairwise_to_contextual_crosswalk.csv']=io.csv_bytes([dict(pair_id=k,case_ids=sorted(set(v)),disposition='PRIMARY_CONTEXTUAL_CASE' if v else 'ARCHIVE_INSUFFICIENT_PAIR_EVIDENCE') for k,v in mapping.items()])
    files['13_context_blind_source_audit.csv']=io.csv_bytes(sources)
    files['29_c1_metadata.json']=io.js(dict(version='R4.4-CONTRACT.JIN.0.3-C1',status='FROZEN_CONTEXT_EVIDENCE',
        human_source_count=0,human_label_leakage_count=0,composition_source_count=0,native_hierarchy_source_count=0,
        sources=[r['source_id'] for r in sources],rules=rules,raw_feature_receipts=raw_receipts,
        counts={key:len(m[key]) for key in ('targets','supported','archive','windows','signatures','correspondence','scopes','cases','membership','auxiliary','macro_mothers','clause_internal')},
        input_blind_freeze_sha256=io.sha(blind['07_blind_discovery_manifest.csv']),
        accepted_parataxis=[],accepted_hypotaxis=[],new_human_judgments=[],new_parent_edges=[],participant_arc='UNADJUDICATED',consumer_implemented=False))
    io.seal(files,'14_context_blind_manifest.csv');io.require(io.manifest_ok(files,'14_context_blind_manifest.csv'),'C1 manifest')
    return files


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--blind-input',required=True);p.add_argument('--rules',required=True);p.add_argument('--tf-data');p.add_argument('--out',required=True);a=p.parse_args(argv)
    inp=Path(a.blind_input);out=Path(a.out);io.require(not out.exists(),'C1 output exists')
    allowed={inp/n:'JIN.0.2-PHASE-A/'+n for n in context.FROZEN_NAMES};allowed[Path(a.rules)]='NEUTRAL_CONTEXT_RULES'
    for name in sorted(SAFE):allowed[Path(__file__).parent/(name+'.py')]='C1_CODE/'+name+'.py'
    if a.tf_data:allowed.update({Path(a.tf_data)/(n+'.tf'):'BHSA2021/'+n+'.tf' for n in io.RAW_FEATURES})
    trace=install_guard(allowed,out);blind={n:(inp/n).read_bytes() for n in context.FROZEN_NAMES}
    io.require(io.manifest_ok(blind,'07_blind_discovery_manifest.csv'),'upstream blind manifest')
    for name in context.FROZEN_NAMES[:5]:neutral(io.rows(blind[name]))
    oldmeta=json.loads(blind['18_phase_a_metadata.json']);io.require(oldmeta['human_source_count']==oldmeta['native_hierarchy_source_count']==0,'upstream blind leakage')
    rules=json.loads(Path(a.rules).read_bytes());neutral(rules);receipts=[]
    if a.tf_data:
        raw,receipts=io.raw_corpus(a.tf_data,json.loads(blind['19_blind_rule_config.json'])['bhsa_book_feature'])
        features={int(c['clause_id']):c for c in io.rows(blind['02_blind_linguistic_features.csv'])}
        io.require({c['clause_id'] for c in raw}==set(features),'raw clause population')
        for c in raw:
            prior=features[c['clause_id']]
            io.require(all(prior[k]==v or (not isinstance(v,(list,dict,bool)) and str(prior[k])==str(v)) for k,v in c.items()),'raw BHSA differs from frozen features')
        io.require(receipts==oldmeta['feature_receipts'],'raw feature receipt changed')
    else:io.require(oldmeta['mode']=='SYNTHETIC','real C1 requires raw BHSA path')
    m=context.build(blind,rules)
    sources=[dict(source_id=label,sha256=io.sha(path.read_bytes()),human_source=False,composition_source=False,native_hierarchy_source=False) for path,label in sorted(allowed.items(),key=lambda x:x[1])]
    io.require({r['source_id'] for r in trace}=={r['source_id'] for r in sources},'C1 actual read registry')
    files=serialize(m,blind,rules,sources,receipts);io.publish(files,out,False)
    print(json.dumps(dict(phase='C1',loaded_source_files=sorted({r['path'] for r in trace}),freeze_sha256=io.sha(files['14_context_blind_manifest.csv']),counts=json.loads(files['29_c1_metadata.json'])['counts'])))
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as e:print(str(e),file=sys.stderr);sys.exit(2)
