"""Complete a verified human freeze; history cannot alter the decision registry."""
from collections import Counter
import json
import zipfile
import milal_mfr_common as cm
import milal_mfr02a_core as core
from milal_mfr01b_data import digest
from milal_mfr01b_io import baseline


def complete(out, historical_config):
    from pathlib import Path
    from milal_mfr02a_pipeline import freeze_valid,code_hashes
    out=Path(out).resolve();cm.require(freeze_valid(out),'Human freeze not verified')
    cm.require(not (out/'90_run_metadata.json').exists(),'Append-only: run already completed')
    cfg=json.loads((cm.ROOT/'config/mfr_0_2a_job.json').read_bytes());pins=baseline(cfg)
    pre=json.loads((out/'16_precomparison_receipt.json').read_bytes())
    cm.require(pre['freeze_sha256']==digest(out/'14_human_decision_freeze.csv'),'Freeze identity changed')
    events=['HUMAN_DECISIONS_FROZEN'];freeze_hash=pre['freeze_sha256']
    # Import and read historical outcomes only after the serialized decisions verify.
    from milal_mfr02a_history import load,compare
    hcfg=json.loads(Path(historical_config).read_bytes());historical,before=load(out,hcfg);events.append('HISTORICAL_LOADED')
    with zipfile.ZipFile(out/'h1_source_projection.zip') as z:
        h1=cm.rows(z.read('13_h1_hierarchy_review_set.csv'))
        attachments={h['configuration_case_id']:json.loads(z.read('case_evidence/'+h['configuration_case_id']+'.json')) for h in h1}
        r1=cm.rows(z.read('14_r1_resumption_review_set.csv'));c1=cm.rows(z.read('15_c1_closure_review_set.csv'))
    o={k:cm.rows((out/n).read_bytes()) for n,k in zip(core.FREEZE_FILES[:6],('decisions','provenance','crosswalk','calibration','deferred','accepted'))}
    o['representation']=json.loads((out/core.FREEZE_FILES[6]).read_bytes())
    supplied=json.loads((cm.ROOT/'config/mfr_0_2a_human_decisions.json').read_bytes())
    comparison=compare(o['decisions'],historical)
    cm.write(out/'06_mfr_0_2a_postfreeze_historical_comparison.csv',cm.csv_bytes(comparison))
    for name,rr,dimension in [('08_mfr_0_2b_resumption_scope.csv',r1,'resumption'),('09_mfr_0_2c_closure_scope.csv',c1,'closure')]:
        cm.write(out/name,cm.csv_bytes(core.scope(rr,o['decisions'],dimension)))
    after={hcfg['archive']:digest(cm.ROOT/hcfg['archive']),hcfg['member']:digest(out/'historical_source.csv')}
    tracked=set(cfg['frozen_files']);consumers=[p.relative_to(cm.ROOT).as_posix() for p in (cm.ROOT/'src').glob('*r4_4*') if p.relative_to(cm.ROOT).as_posix() not in tracked]
    env=dict(BASELINE_COMMIT_VERIFIED=bool(pins),
        MFR_0_1_FROZEN_VERIFIED=pre['archive_receipts'][0]['manifest_verified'],
        MFR_0_1A_FROZEN_VERIFIED=pre['archive_receipts'][1]['manifest_verified'],
        MFR_0_1B_FROZEN_VERIFIED=pre['archive_receipts'][2]['manifest_verified'],events=events,
        freeze_valid=freeze_valid(out) and digest(out/'14_human_decision_freeze.csv')==freeze_hash,
        historical_read_guard_valid=json.loads((out/'15_freeze_read_receipt.json').read_bytes())['readset_valid'],
        historical_before=before,historical_after=after,new_consumers=consumers,
        authority_valid=digest(cm.ROOT/'docs/MFR_0_2A_RESEARCHER_SOURCE.txt')==cfg['authority_sha256'] and digest(cm.ROOT/'config/mfr_0_2a_human_decisions.json')==cfg['human_registry_sha256'])
    gg=core.gates(o,supplied,h1,attachments,env);cm.require(all(gg.values()),str([k for k,v in gg.items() if not v]))
    cm.write(out/'11_gates.csv',cm.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in gg.items()]))
    stats=dict(decisions=len(o['decisions']),distribution=dict(Counter(r['researcher_decision'] for r in o['decisions'])),accepted_configuration_relations=len(o['accepted']),
        constituent_edges=len(o['representation']['constituent_edges']),mothers=len(o['representation']['mothers']),
        deferred_h1_resumption=sum(r['resumption_review_status']=='DEFERRED_TO_MFR_0_2B' for r in o['decisions']),
        deferred_h1_closure=sum(r['closure_review_status']=='DEFERRED_TO_MFR_0_2C' for r in o['decisions']),
        future_resumption_scope=len(r1),future_closure_scope=len(c1),calibrations=len(o['calibration']),
        historical_comparison=dict(Counter(r['status'] for r in comparison)),underlying_raw_pairs=len(o['crosswalk']))
    report='# MFR.0.2A human adjudication\n\nResearcher-supplied configuration decisions; constituent edges are not inferred.\n\n'
    report+='| Configuration | Decision | Raw pairs | Historical comparison |\n| --- | --- | --- | --- |\n'
    for r,h in zip(o['decisions'],comparison):report+=f"| {r['configuration_case_id']} | {r['researcher_decision']} | {len(r['underlying_raw_pair_ids'])} | {h['status']} |\n"
    report+='\nFORMAL_ONLY retains meaningful linguistic evidence; INSUFFICIENT is not NO_RELATION across all dimensions. Resumption and closure remain separately unreviewed. Historical comparison uses explicit clause identities and does not equate broader historical units with configurations.\n\n'
    report+='Statistics:\n\n```json\n'+json.dumps(stats,ensure_ascii=False,indent=2)+'\n```\n\n'
    report+='Human decisions were serialized and hashed before historical load. All original evidence remains in mfr01b_frozen_input.zip and exact case attachments.\n'
    cm.write(out/'07_mfr_0_2a_adjudication_report.md',report.encode('utf8'))
    cm.write(out/'10_next_scope.md',b'# Next scope\n\nMFR_H1_CONFIGURATION_ADJUDICATED\n\nREADY_FOR_MFR_0_2B_RESUMPTION_ADJUDICATION\n\nMFR.0.2B is the next researcher batch. MFR.0.2C follows separately. No tree, root, constituent expansion or R4.4 consumer.\n')
    meta=dict(stage='MFR.0.2A',baseline=cfg['baseline'],upstream_sha256=cfg['archive']['sha256'],authority_sha256=cfg['authority_sha256'],
        human_registry_sha256=cfg['human_registry_sha256'],freeze_sha256=freeze_hash,events=events,historical_sources=before,
        statistics=stats,run_gates=len(gg),release_gate_names=list(core.release_gates(dict(tests_run=0,errors=0,failures=0,skipped=0),False,False)),
        release_gate_status='REQUIRES_INDEPENDENT_A_B_AND_REGRESSION_VERIFIER',frozen_file_count=len(pins),code_sha256=code_hashes(),
        historical_config_sha256=digest(Path(historical_config)),readiness=['MFR_H1_CONFIGURATION_ADJUDICATED','READY_FOR_MFR_0_2B_RESUMPTION_ADJUDICATION'])
    cm.write(out/'90_run_metadata.json',cm.js(meta));cm.manifest(out,'99_manifest_sha256.csv');cm.require(cm.verify(out,'99_manifest_sha256.csv'),'Final manifest invalid')
    z=cm.deterministic_zip(out);print(json.dumps(dict(zip=str(z),sha256=digest(z),gates=len(gg),statistics=stats)),flush=True)
    return out
