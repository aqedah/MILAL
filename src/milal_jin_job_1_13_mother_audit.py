"""A: preceding raw clause evidence and neutral anchor comparisons, no winner."""
from milal_jin_focused_common import table
import milal_jin_io as io


def build(e,blind):
    target=e.at_ref(e.rules['a_target']);head=target[0];start=e.head(e.rules['a_scan_start'])
    prior=[c for c in e.features if start['sequence_index']<=c['sequence_index']<head['sequence_index']]
    immediate=e.features[max(0,head['sequence_index']-3):head['sequence_index']]
    scans=[];resume=[]
    for c in prior:
        r=e.resumption([c],target,immediate);resume.append(dict(preceding_clause_id=c['clause_id'],reference=c['reference'],resumption=r))
        if not c['main_clause_compatible']:continue
        row=e.pair(c,head);ev=row['clause_evidence'];labels=[]
        if ev['parataxis_supported']:labels.append('A_PARATAXIS_SUPPORTED')
        if ev['hypotaxis_supported']:labels.append('A_HYPOTAXIS_SUPPORTED')
        if ev['parataxis_supported'] and ev['hypotaxis_supported']:labels.append('A_PARATAXIS_AND_HYPOTAXIS_SUPPORTED')
        if r['candidate']:labels.append('A_RESUMED_NARRATIVE_LINE_CANDIDATE')
        labels.append('A_MOTHER_CANDIDATE_SUPPORTED' if ev['hypotaxis_supported'] else 'A_MOTHER_CANDIDATE_INSUFFICIENT')
        if not (ev['hypotaxis_supported'] or ev['parataxis_supported'] or r['candidate']):labels.append('A_RELATION_INSUFFICIENT')
        row.update(candidate_id='FA:'+str(c['clause_id'])+':'+str(head['clause_id']),pool='A_STRICT_CLAUSE_MOTHER_CANDIDATES',main_clause_compatible=True,retained_mother_candidate=ev['hypotaxis_supported'],hypotheses=labels,resumption=r)
        scans.append(row)
    anchors=[]
    for ref in e.rules['a_anchors']:
        c=e.head(ref);anchors.append(dict(reference=ref,pool='A_MACRO_ANCHOR_COMPARISON',is_mother_relation=False,raw=e.raw(c),comparison=e.ctx.compare(c['clause_id'],head['clause_id'])))
    controls=[dict(references=refs,comparison=e.ctx.compare(e.head(refs[0])['clause_id'],e.head(refs[1])['clause_id'])) for refs in e.rules['a_controls']]
    earlier=[c for ref in e.rules['a_earlier_refs'] for c in e.at_ref(ref)];near=[c for ref in e.rules['a_immediate_refs'] for c in e.at_ref(ref)]
    special=e.resumption(earlier,target,near)
    display=[]
    for r in scans:
        f=r['clause_evidence']['evidence_flags'];display.append(dict(Candidate=str(r['preceding']['clause_id'])+' '+r['preceding']['reference'],Clause_type=r['preceding']['signature']['clause_type'],Formal=f['F_FORMULA_CORRESPONDENCE'],Participant_recurrence=f['R_PARTICIPANT_SET_CONTINUITY'],Participant_change=f['R_PARTICIPANT_SET_CHANGE'],Temporal=f['D_TEMPORAL_FRAME_CORRESPONDENCE'],Context=r['context']['configuration_status'],Resumption=r['resumption']['candidate'],Hypotaxis=r['clause_evidence']['hypotaxis_supported'],Parataxis=r['clause_evidence']['parataxis_supported'],Limitation='UNRESOLVED_IDENTITY; NO_WINNER',Status='UNADJUDICATED'))
    report='# A — preceding clause candidates, no mother selected\n\n'+table(display,list(display[0]) if display else ['Candidate'])
    report+='\n## Separate neutral anchors / three-way raw comparison\n\n'+str([r['reference'] for r in anchors])+'\n'
    for r in controls:report+='\n'+str(r['references'])+': '+str(r['comparison']['flags'])+'\n'
    report+='\n## Earlier configuration versus immediate context\n\n'+str(special)+'\n\nSurface recurrence does not establish a resumed semantic scene or a mother.\n'
    for ref in e.rules['a_earlier_refs']+e.rules['a_immediate_refs']+[e.rules['a_target']]:
        report+='\n'+ref+': '+' / '.join(str(c['clause_id'])+' '+c['surface'] for c in e.at_ref(ref))+'\n'
    return dict(files={'01_job_1_13_candidate_inventory.csv':io.csv_bytes(scans),'02_job_1_13_context_comparison.csv':io.csv_bytes(controls),'03_job_1_13_resumption_audit.csv':io.csv_bytes(resume),'04_job_1_13_blind_report.md':report.encode(),'a_macro_anchor_comparison.csv':io.csv_bytes(anchors),'a_special_resumption.json':io.js(special)},summary=dict(preceding_all=len(prior),scanned_main_compatible=len(scans),retained_mother_candidates=sum(r['retained_mother_candidate'] for r in scans),candidate_refs=[r['preceding']['reference'] for r in scans if r['retained_mother_candidate']],resumption_candidates=sum(r['resumption']['candidate'] for r in scans)))
