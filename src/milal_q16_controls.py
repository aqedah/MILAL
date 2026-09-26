"""Q1.6 post-freeze diagnostics; corpus-specific selections live in configuration."""
import json
from milal_mfr02r_data import rows,table,digest
from milal_q13_pipeline import write


def controls(a,q15,out,config,result,views):
    freeze=json.loads((out/'blind_freeze.json').read_text())
    if not all(digest(out/n)==h for n,h in freeze['files'].items()):raise ValueError('blind files changed')
    refs=list(rows(q15/'09_q15_reference_witness_reclassification.csv'));byref={r['reference_witness_id']:r for r in refs}
    selected=[]
    targets={str(x) for x in config['diagnostic_targets']}
    for rid,f in a.forms.items():
        if str(f['target_clause_id']) not in targets:continue
        selected.append(dict(form=f,classification=byref[rid],domains=[a.domains[d] for d in f['domain_ids']],audit_status='CORRECTLY_UNRESOLVED' if int(byref[rid]['source_bound_candidate_count'])==0 else 'EXISTING_REFERENCE_SUPPORT',new_SB09_binding=False,judgment_scope='CURRENT_PERMITTED_EVIDENCE_CONTRACT; COMPLETENESS_UNRESOLVED'))
    write(out/'job_reference_diagnostics.json',selected)
    temporal=[v for v in views['SB07'] if v['source_id'] in targets or v['target_id'] in targets]
    storm=[]
    for c,r in a.by_clause.items():
        if c not in targets:continue
        for p in r['PHRASE']:
            if config['storm_lexeme'] in p['lexemes']:storm.append(dict(clause_id=c,phrase=p,native_function=p['function'],new_locative_binding=False,interpretation='EXISTING_CONFIGURATION_ONLY; LOCATIVE_IDENTITY_UNRESOLVED'))
    text=['# Q1.6 post-freeze Job diagnostics','All selections occurred after generic outputs were hashed. Diagnostic IDs are configuration, never detection rules.',
          'Zero visibility is correct under the implemented surface-domain contract; completeness of additional domain mechanisms remains underspecified. This does not identify an antecedent or prove none exists.',
          '## Reference cases','```json\n'+json.dumps(selected,ensure_ascii=False,indent=2)+'\n```','## Temporal analytical views','```json\n'+json.dumps(temporal,ensure_ascii=False,indent=2)+'\n```','## Storm native annotation','```json\n'+json.dumps(storm,ensure_ascii=False,indent=2)+'\n```']
    (out/'17_q16_job_special_diagnostics.md').write_text('\n\n'.join(text)+'\n',encoding='utf8')
    piv=[p for p in result['provenance'] if p['target_id']==str(config['pivot_target'])]
    detail=[]
    for p in piv:
        detail.append(dict(relation=p,raw_evidence={w:sorted(a.graph.roots(w)) for w in p['witness_ids']},supplemental_views=[v for vv in views.values() for v in vv if v['candidate_id']=='P'+p['source_id']+'-'+p['target_id']],ablation=[dict(mechanism=r['mechanism'],loses_binding=p['outcome_id'] in r['lost_outcome_ids'],alternative_retained=p['outcome_id'] in r['alternative_retained_outcome_ids']) for r in result['ablation']]))
    (out/'18_q16_job_37_20_pivot_audit.md').write_text('# Frozen mother alternatives\n\nNo ranking, canonical selection, or deletion. New mechanisms provide zero distinct bindings.\n\n```json\n'+json.dumps(detail,ensure_ascii=False,indent=2)+'\n```\n',encoding='utf8')
    receipts=[]
    for src,dst in [('21_q15_numbers_postfreeze_controls.csv','19_q16_numbers_postfreeze_controls.csv'),('20_q15_bosman_postfreeze_controls.csv','20_q16_bosman_postfreeze_controls.csv')]:
        rr=list(rows(q15/src))
        augmented=[dict(frozen_control=r,q15_source_sha256=digest(q15/src),q16_status='FROZEN_FIXTURE_REPLAY_NO_NEW_BINDING_ADAPTER',new_relations=[],canonical_decision=None) for r in rr]
        table(out/dst,augmented);receipts.append(dict(source=src,sha256=digest(q15/src),rows=len(rr),output=dst))
    receipt=dict(controls=receipts,blind_unchanged=all(digest(out/n)==h for n,h in freeze['files'].items()),fixture_scope=json.loads((q15/'control_receipts.json').read_text()),full_external_analysis=False,controls_mode='EXACT_FROZEN_REPLAY_AUDIT_ONLY')
    write(out/'control_receipts.json',receipt)
    return receipt
