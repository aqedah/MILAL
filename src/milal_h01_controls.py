"""Read diagnostic selectors and historical H0 only after the generic audit freezes."""
import json
from milal_mfr02r_data import digest,encode
from milal_q13_pipeline import write

METHOD='''# H0.1 methodological report

Qualified relation, structural decision and human adjudication are distinct.
One unopposed candidate is QUALIFIED_NONCOMPETING_CANDIDATE, never accepted.
Multiple compatible peers or orthogonal mother/peer relations do not require choice.
UNSELECTED means UNDECIDED, not a negative structural commitment.

The frozen Q1.3 oracle enforces one mother, strict/equal-level compatibility,
acyclicity after parallel contraction, explicit exclusions and provenance-backed
SB12 forbidden combinations. H0.1 enumerates minimal forbidden sets using
conflict-directed deletion. A different minimal core must omit a member of the
current core; coherent pools terminate. This covers global cycles and higher-order
conditions without enumerating the Cartesian product of undecided relations.

Only relations joined by an actual minimal conflict form a decision component.
Every review item has coherent positive witness assignments whose union violates
a recorded hard constraint. Displayed assignments are feasibility proofs, not an
exhaustive list of all global hierarchies and not selected outcomes. The complete
symbolic constraints remain machine-readable. No shared-mother requirement is
added for parallel peers; unknown canonical levels do not force adjudication.
An affected GLOBAL_CONSTRAINT_DECISION target is not automatically a local true
pivot. A local true pivot additionally requires different positive commitments
for that same target inside a minimal forbidden set. A selected edge versus
omission alone never meets that test, even when a global cycle needs review.

Every qualified relation receives exactly one disposition. Every Job target gets
a status. A noncompeting qualified target with an evidence gap has primary status
EVIDENCE_GAP_NOT_STRUCTURAL_DECISION, while structural_status separately preserves
its single/compatible-set status. Targets without qualified relations remain
NO_QUALIFIED_RELATION even if gaps exist. Evidence gaps remain in a separate
lossless register and do not invent relations or exclusions.

Q1.6R roles separate pre-relation, primary, corroborative, visibility,
configuration, post-validation and global-constraint evidence. Raw IDs and shared
evidence warnings remain inspectable; no votes or weights are assigned.
Nondecision representatives use exact stable relation IDs for QA only, never as
human structural judgments. Historical H0 labels and human decisions are absent
from classification. Diagnostic controls and descriptive history follow the
generic hash freeze. Reduction is a scope change, not validated accuracy gain.

H0.2 may adjudicate only these review packets after explicit researcher approval.
H0.1 itself makes no human decision and does not start H0.2.
'''


def postfreeze(state,out,h0,config):
    freeze=json.loads((out/'blind_freeze.json').read_text());assert all(digest(out/n)==h for n,h in freeze['files'].items())
    selected={str(t['clause_id']) for t in state['inventory'].values() if [int(t['chapter']),int(t['verse'])]==config['diagnostic_reference']}
    diagnostics=[]
    for t in state['result']['targets']:
        if t['target'] not in selected:continue
        rel=[r for r in state['outcomes'] if r['target']==t['target']];ids={r['structural_outcome_group_id'] for r in rel}
        diagnostics.append(dict(target_status=t,qualified_mother_alternatives=[r for r in rel if r['relation_type']=='HYPOTACTIC'],
            evidence=[state['catalog']['provenance'][i] for i in sorted(ids)],
            components=[c for c in state['result']['components'] if t['target'] in c['targets']],
            ablation=[r for r in state['catalog']['ablation'] if any(ids&set(r.get(k,[])) for k in ('lost_outcome_ids','retained_outcome_ids','alternative_retained_outcome_ids','changed_outcome_ids'))],
            unresolved_gap_ids=[g['gap_id'] for g in state['gaps'] if g['target']==t['target']]))
    write(out/'postfreeze_diagnostic_evidence.json',diagnostics)
    text=['# Job post-freeze diagnostics','No mother or hierarchy is selected. Full ablation and evidence records are in postfreeze_diagnostic_evidence.json.']
    for d in diagnostics:
        t=d['target_status'];text+=['## '+t['target']+' — '+t['target_status'],
            'Qualified mothers: '+encode([dict(source=r['source_or_peer'],relation_id=r['structural_outcome_group_id']) for r in d['qualified_mother_alternatives']]),
            'Exact incompatibility: '+encode([c['positive_incompatibility_proofs'] for c in d['components']]),
            'Evidence and shared raw IDs: '+encode(d['evidence']), 'Unresolved: '+encode(d['unresolved_gap_ids'])]
    (out/'14_h01_job_postfreeze_diagnostics.md').write_text('\n\n'.join(text)+'\n',encoding='utf8',newline='\n')
    historical=json.loads((h0/'17_h0_review_reduction_metrics.json').read_text())
    comparison=dict(raw=historical['candidate_universe_total'],historical_relation_eligible=historical['eligibility_counts']['RELATION_ELIGIBLE'],
        historical_review_targets=historical['target_status_counts']['TARGET_REVIEW_REQUIRED'],current_qualified=len(state['outcomes']),current_human_review_items=len(state['cards']),
        historical_source_sha256=digest(h0/'17_h0_review_reduction_metrics.json'),historical_read_after_freeze=True)
    write(out/'historical_comparison.json',comparison)
    (out/'15_h01_historical_h0_comparison.md').write_text('# Historical comparison after freeze\n\n'+encode(comparison)+'\n\nSEARCH CANDIDATE → SOURCE-BOUND QUALIFIED RELATION → COMPATIBILITY → TRUE STRUCTURAL DECISION. Historical labels had no classification effect. Reduction is not a demonstrated accuracy improvement.\n',encoding='utf8',newline='\n')
    (out/'17_h01_method_report.md').write_text(METHOD,encoding='utf8',newline='\n')
    ready='READY_FOR_MFR_0_2R_H0_2' if len(state['result']['dispositions'])==len(state['outcomes']) else 'NEEDS_REVIEW_SIEVE_REPAIR'
    (out/'18_h01_next_scope.md').write_text('# Next scope\n\n'+ready+'\n\nH0.2 requires separate researcher authorization and must operate only on H0.1 review packets. No decisions made; H0.2 has not started.\n',encoding='utf8',newline='\n')
    after={n:digest(out/n) for n in freeze['files']}
    if after!=freeze['files']:raise ValueError('post-freeze mutation')
    write(out/'postfreeze_receipt.json',dict(before=freeze['files'],after=after,historical_read_after_freeze=True,diagnostic_read_after_freeze=True))
    return ready
