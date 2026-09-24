"""Isolated marker-first discovery executable with an exact source allowlist."""
import argparse
import csv
import json
import os
from pathlib import Path
import sys
from collections import Counter
import milal_mfr_common as cm
import milal_mfr_observation as ob
import milal_mfr_signatures as sg
import milal_mfr_marker_discovery as md
import milal_mfr_families as fm
import milal_mfr_force_evidence as hf
import milal_mfr_coverage as cv
import milal_mfr_relation_candidates as rc

MODULES=(cm,ob,sg,md,fm,hf,cv,rc)
NAMES={'observation':'03_job_surface_observation_inventory.csv','signatures':'04_job_formal_signatures.csv','markers':'05_job_marker_candidates.csv','families':'06_job_marker_family_registry.csv','membership':'07_job_marker_family_membership.csv','force':'08_job_hierarchical_force_evidence.csv','coverage':'09_job_coverage_candidates.csv','nested':'10_job_nested_marker_evidence.csv','relations':'11_job_marker_relation_candidates.csv'}


def guard(allowed,out):
    paths={str(Path(p).resolve()).casefold():v for p,v in allowed.items()};base=str(Path(out).resolve()).casefold()+os.sep;trace=[]
    safe={m.__name__ for m in MODULES}|{'milal_mfr_blind'}
    cm.require(not any(n.startswith('milal_') and n not in safe for n in sys.modules),'non-blind module preloaded')
    def hook(event,args):
        if event=='import':cm.require(not args[0].startswith('milal_') or args[0] in safe,'forbidden blind import')
        if event!='open' or isinstance(args[0],int):return
        path=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode=args[1];flags=args[2]
        write=(isinstance(mode,str) and any(x in mode for x in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT))
        if write:cm.require(path.startswith(base),'outside blind write boundary')
        else:cm.require(path in paths,'outside blind read allowlist: '+path);trace.append(paths[path])
    sys.addaudithook(hook);return trace


def build(obs,rules,prefix):
    sig,lookup=sg.signatures(obs);markers=md.discover(obs,lookup,rules,prefix);families,membership=fm.families(markers,obs,prefix+'F');coverage,nested=cv.coverage(markers,obs,families,prefix);force=hf.force(markers,obs,families,coverage,nested);pairs,index=rc.pair_universe(markers,obs,families,coverage)
    return dict(observation=obs,signatures=sig,markers=markers,families=families,membership=membership,force=force,coverage=coverage,nested=nested,pairs=pairs,index=index)


def main(argv=None):
    p=argparse.ArgumentParser();p.add_argument('--bhsa');p.add_argument('--synthetic');p.add_argument('--scope',required=True);p.add_argument('--rules',required=True);p.add_argument('--out',required=True);a=p.parse_args(argv)
    out=Path(a.out).resolve();cm.require(not out.exists(),'blind directory exists');out.mkdir(parents=True)
    code=[Path(__file__),*[Path(m.__file__) for m in MODULES]];allowed={f.resolve():'BLIND_CODE/'+f.name for f in code};allowed[Path(a.rules).resolve()]='NEUTRAL_RULES'
    if a.bhsa:allowed.update({(Path(a.bhsa)/(f+'.tf')).resolve():'BHSA2021/'+f+'.tf' for f in ob.FEATURES})
    else:allowed[Path(a.synthetic).resolve()]='SYNTHETIC_OBSERVATIONS'
    trace=guard(allowed,out);rules=json.loads(Path(a.rules).read_bytes());scope=rules['scopes'][a.scope]
    if a.bhsa:obs,receipts=ob.raw_corpus(a.bhsa,scope['books'])
    else:obs=ob.observe(json.loads(Path(a.synthetic).read_bytes()));receipts=[]
    m=build(obs,rules,scope['prefix']);counts={}
    for name in NAMES:
        if name=='relations':continue
        cm.write(out/NAMES[name],cm.csv_bytes(m[name]));counts[name]=len(m[name])
    cm.write(out/'pair_universe_index.json',cm.js(m['index']))
    count=0;labels=Counter();cross=0;all_false=True
    with (out/NAMES['relations']).open('w',encoding='utf8',newline='') as stream:
        writer=None
        for row in rc.relations(m['markers'],obs,m['force'],m['coverage'],m['pairs'],rules,scope['prefix']):
            if writer is None:writer=csv.DictWriter(stream,fieldnames=list(row),lineterminator='\n');writer.writeheader()
            writer.writerow({k:cm.js(v).decode().strip() if isinstance(v,(dict,list,bool)) or v is None else v for k,v in row.items()});count+=1;cross+=row['cross_book'];labels.update(row['relation_candidates']);all_false &= not row['automatic_resolution']
        if writer is None:stream.write('relation_candidate_id\n')
    counts['relations']=count
    sources=[dict(source_id=label,actual_path=str(path),sha256=cm.sha(path.read_bytes()),reuse_class='OBSERVATION_SAFE' if label.startswith(('BHSA','SYNTHETIC')) else 'DERIVED_BLIND_SAFE',human_dependency=False,structural_label_dependency=False,technical_root_dependency=False) for path,label in sorted(allowed.items(),key=lambda x:x[1])]
    cm.require(set(trace)==set(allowed.values()),'actual read inventory incomplete')
    cm.write(out/'02_blind_input_manifest.csv',cm.csv_bytes(sources))
    meta=dict(stage='MFR.0.1',scope=a.scope,mode='REAL_BHSA_2021' if a.bhsa else 'SYNTHETIC',counts=counts,clause_count=len(obs),clause_atom_count=len({x for c in obs for x in c['clause_atom_ids']}),label_counts=dict(labels),cross_book_candidate_count=cross,
        repeated_marker_count=sum(x['repeat_count']>=2 for x in m['markers']),singleton_explicit_count=sum(bool(x['singleton_reason']) for x in m['markers']),human_input_count=sum(x['human_dependency'] for x in sources),structural_label_input_count=sum(x['structural_label_dependency'] for x in sources),technical_root_input_count=sum(x['technical_root_dependency'] for x in sources),actual_source_reads=sorted(set(trace)),code_config_sha256={r['source_id']:r['sha256'] for r in sources if not r['source_id'].startswith('BHSA')},feature_receipts=receipts,automatic_resolution=not all_false,same_book_required=False,scope_external_status='OUTSIDE_SCOPE_NOT_TESTED')
    cm.write(out/'metadata.json',cm.js(meta))
    # A streaming read hook cannot subsequently read generated output: publish a
    # freeze in the coordinator, after this process has exited successfully.
    print(json.dumps(dict(scope=a.scope,counts=counts,cross_book=cross)))

if __name__=='__main__':main()
