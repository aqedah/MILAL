"""Isolated process: only nine frozen blind tables and clean consolidation code."""
import argparse
import json
import os
from pathlib import Path
import sys
import milal_mfr_common as cm
import milal_mfr01a_data as data
import milal_mfr01a_bundle as bundle
import milal_mfr01a_lattice as lattice
import milal_mfr01a_closure as closure
import milal_mfr01a_relation as relation
import milal_mfr01a_core as core
import milal_mfr01a_gates as gates

MODULES=(cm,data,bundle,lattice,closure,relation,core,gates)

def guard(allowed,out):
    paths={str(Path(p).resolve()).casefold():label for p,label in allowed.items()};base=str(Path(out).resolve()).casefold()+os.sep;trace=[]
    safe={m.__name__ for m in MODULES}|{'milal_mfr01a_blind'}
    cm.require(not any(n.startswith('milal_') and n not in safe for n in sys.modules),'non-consolidation module preloaded')
    def hook(event,args):
        if event=='import':cm.require(not args[0].startswith('milal_') or args[0] in safe,'forbidden consolidation import')
        if event!='open' or isinstance(args[0],int):return
        path=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode,flags=args[1],args[2]
        write=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT))
        if write:cm.require(path.startswith(base),'outside consolidation output boundary')
        else:cm.require(path in paths,'outside consolidation read allowlist: '+path);trace.append(paths[path])
    sys.addaudithook(hook);return trace

def main():
    p=argparse.ArgumentParser();p.add_argument('--input',required=True);p.add_argument('--out',required=True);p.add_argument('--scope',required=True);p.add_argument('--prefix',required=True);a=p.parse_args()
    out=Path(a.out).resolve();cm.require(not out.exists(),'fresh consolidation output required');out.mkdir(parents=True)
    allowed={(Path(a.input)/name).resolve():'FROZEN_BLIND/'+name for name in data.TABLES.values()}
    allowed.update({Path(m.__file__).resolve():'CONSOLIDATION_CODE/'+Path(m.__file__).name for m in MODULES});allowed[Path(__file__).resolve()]='CONSOLIDATION_CODE/'+Path(__file__).name
    trace=guard(allowed,out);d=data.load(a.input);o=core.build(d,a.prefix);checks=gates.core_gates(d,o)
    cm.require(all(checks.values()),'core gates failed: '+str([k for k,v in checks.items() if not v]))
    for key,name in data.OUTPUTS.items():data.table(out/name,o[key])
    receipts=[dict(source_id=label,sha256=cm.sha(path.read_bytes()),human_dependency=False,structural_dependency=False) for path,label in sorted(allowed.items(),key=lambda v:v[1])]
    cm.require(set(trace)=={r['source_id'] for r in receipts},'consolidation readset incomplete')
    meta=dict(scope=a.scope,stage='MFR.0.1a',statistics=core.statistics(d,o),core_gates=checks,actual_reads=sorted(set(trace)),input_code_receipts=receipts)
    cm.write(out/'consolidation_metadata.json',cm.js(meta));print(json.dumps(dict(scope=a.scope,statistics=meta['statistics'])),flush=True)

if __name__=='__main__':main()
