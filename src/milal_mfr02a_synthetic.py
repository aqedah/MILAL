"""Small invented evidence fixtures; never a source of empirical judgments."""
import json
import subprocess
import sys
import zipfile
from pathlib import Path
import milal_mfr_common as cm
from milal_mfr02a_core import assemble, gates


def fixture():
    supplied=json.loads((cm.ROOT/'config/mfr_0_2a_human_decisions.json').read_bytes());h1=[];attachments={}
    for i,s in enumerate(supplied['decisions']):
        cid=s['configuration_case_id'];pairs=[f'SYN-P{i}-{j}' for j in range(2)];markers=[f'SYN-M{i}-0',f'SYN-M{i}-1'];bundles=[f'SYN-B{i}']
        c=dict(configuration_case_id=cid,raw_pair_ids=pairs,marker_ids=markers,bundle_ids=bundles,
            source_clause_ids=[f'SYN-C{i}-0'],target_clause_ids=[f'SYN-C{i}-1'],resumption_pair_ids=pairs,
            raw_candidate_labels=['RESUMPTION_CANDIDATE','COMPETING_RELATIONS'])
        e=[dict(evidence_id=pairs[0]+':FORM',provenance_family='EVID_DIRECT_FORMAL',independent_link_usable=True,cessation_derived=False,dependency_root_ids=['FORM:'+markers[0]]),
           dict(evidence_id=pairs[0]+':CESSATION',provenance_family='EVID_COVERAGE_CESSATION_DERIVED',independent_link_usable=False,cessation_derived=True,dependency_root_ids=['CESSATION:'+markers[1]])]
        attachments[cid]=dict(configuration=c,raw_relations=[dict(relation_candidate_id=r,relation_candidates=c['raw_candidate_labels']) for r in pairs],evidence_provenance=e,marker_roles=[],bundles=[],force=[],coverage=[],signatures=[])
        h1.append(dict(configuration_case_id=cid,all_configuration_pair_ids=pairs,phase_pair_ids=pairs,marker_ids=markers,bundle_ids=bundles,decision=''))
    return supplied,h1,attachments


def environment():
    return dict(BASELINE_COMMIT_VERIFIED=True,MFR_0_1_FROZEN_VERIFIED=True,MFR_0_1A_FROZEN_VERIFIED=True,MFR_0_1B_FROZEN_VERIFIED=True,
        events=['HUMAN_DECISIONS_FROZEN','HISTORICAL_LOADED'],freeze_valid=True,historical_read_guard_valid=True,
        historical_before={'synthetic-history':'frozen'},historical_after={'synthetic-history':'frozen'},new_consumers=[],authority_valid=True)


def selftest(out):
    out=Path(out).resolve();cm.require(not out.exists(),'Fresh synthetic output required');out.mkdir(parents=True)
    supplied,h1,attachments=fixture();projection=out/'synthetic_projection.zip'
    with zipfile.ZipFile(projection,'x') as z:
        z.writestr('13_h1_hierarchy_review_set.csv',cm.csv_bytes(h1))
        for cid,a in attachments.items():z.writestr('case_evidence/'+cid+'.json',cm.js(a))
    authority=out/'synthetic_supplied.json';cm.write(authority,cm.js(supplied))
    subprocess.run([sys.executable,'-B','-X','utf8',str(cm.ROOT/'src/milal_mfr02a_freeze.py'),str(projection),str(authority),str(out/'freeze')],check=True)
    from milal_mfr02a_pipeline import freeze_valid
    env=environment();env['freeze_valid']=freeze_valid(out/'freeze');env['historical_read_guard_valid']=json.loads((out/'freeze/15_freeze_read_receipt.json').read_bytes())['readset_valid']
    o=assemble(supplied,h1,attachments);gg=gates(o,supplied,h1,attachments,env);cm.require(all(gg.values()),str(gg))
    cm.write(out/'synthetic_gates.csv',cm.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in gg.items()]))
    report='# Synthetic human serialization check\n\nInvented evidence only; historical baseline flags are fixture preconditions.\n\n'
    report+='\n'.join(f"- {r['configuration_case_id']}: {r['researcher_decision']}; raw evidence memberships {len(r['underlying_raw_pair_ids'])}; constituent edges 0" for r in o['decisions'])
    cm.write(out/'synthetic_report.md',report.encode('utf8'));cm.manifest(out,'99_manifest_sha256.csv');cm.require(cm.verify(out,'99_manifest_sha256.csv'),'Synthetic manifest')
    print(json.dumps(dict(mode='SYNTHETIC',gates=len(gg),decisions=len(o['decisions']),accepted=len(o['accepted']))))
