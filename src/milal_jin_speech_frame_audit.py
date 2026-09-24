"""B: whole-book raw speech transitions and unadjudicated frame alternatives."""
import milal_jin_io as io
import milal_jin_relation_rules as rr
from milal_jin_focused_common import table


def event(c,following,rules):
    verbs={w['lex'] for w in c['verbal_words']};lex=set(c['lexemes']);future={w['lex'] for n in following for w in n['verbal_words']}
    open_mouth=rules['open_verb'] in verbs and rules['mouth'] in lex
    formal=bool('>MR[' in verbs or ('<NH[' in verbs and '>MR[' in future) or (rules['speech_add_verb'] in verbs and '>MR[' in future))
    speech=bool(verbs&set(rules['speech_verbs']) or open_mouth or (rules['speech_add_verb'] in verbs and '>MR[' in future))
    return dict(open_mouth=open_mouth,formal_onset=formal,speech_event=speech,frame_candidate=bool(speech and not formal),domain=c['domain'])


def build(e,blind):
    ff=e.features;n=e.rules['speech_near_clauses'];events=[event(c,ff[i+1:i+1+n],e.rules) for i,c in enumerate(ff)]
    transitions=[];candidates=[];covered=set()
    for i,c in enumerate(ff):
        if i and ff[i-1]['domain']=='N' and c['domain']=='Q':transitions.append(dict(transition_id='FT:'+str(c['clause_id']),transition_kind='NARRATIVE_TO_DIRECT_SPEECH',preceding=e.raw(ff[i-1]),target=e.raw(c),exact_adjacent=True))
        if not events[i]['frame_candidate']:continue
        near=[j for j in range(i+1,min(len(ff),i+1+n)) if events[j]['formal_onset']]
        if not near:
            candidates.append(dict(candidate_id='FB:'+str(c['clause_id'])+':NONE',frame=e.raw(c),onset=None,frame_event=events[i],onset_event=None,evidence=None,participant_surface_continuity=False,outgoing_speech_domain=False,comparable=False,hypotheses=['B_INSUFFICIENT_EVIDENCE'],status='UNADJUDICATED',selected_mother='',automatic_resolution=False));continue
        for j in near:
            cur=ff[j];covered.add(j);ev=e.pair(c,cur);same=bool(set(c['participant_surfaces'])&set(cur['participant_surfaces']))
            outgoing=any(x['domain']=='Q' for x in ff[j+1:j+1+n]);comparable=bool(same and outgoing and c['domain'] in ('N','?'))
            labels=['B_INSUFFICIENT_EVIDENCE']
            if same:labels=['B_CSF_CONTINUES_OPENED_SPEECH_EVENT','B_REDUNDANT_FORMAL_SPEECH_ONSET_CANDIDATE','B_MULTIPLE_INTERPRETATIONS_SUPPORTED']
            if ev['clause_evidence']['hypotaxis_supported']:labels.append('B_FRAME_TO_CSF_HYPOTAXIS_SUPPORTED')
            if ev['clause_evidence']['parataxis_supported']:labels.append('B_FRAME_TO_CSF_PARATAXIS_SUPPORTED')
            row=dict(candidate_id='FB:'+str(c['clause_id'])+':'+str(cur['clause_id']),frame=e.raw(c),onset=e.raw(cur),frame_event=events[i],onset_event=events[j],evidence=ev,participant_surface_continuity=same,outgoing_speech_domain=outgoing,comparable=comparable,hypotheses=labels,status='UNADJUDICATED',selected_mother='',automatic_resolution=False)
            candidates.append(row);transitions.append(dict(transition_id=row['candidate_id'],transition_kind='NARRATIVE_SPEECH_EVENT_TO_CSF' if c['domain']=='N' else 'SPEECH_EVENT_VERB_TO_FORMAL_ONSET',preceding=e.raw(c),target=e.raw(cur),exact_adjacent=j==i+1))
    for j,c in enumerate(ff):
        if events[j]['formal_onset'] and j not in covered:
            candidates.append(dict(candidate_id='FB:NONE:'+str(c['clause_id']),frame=None,onset=e.raw(c),frame_event=None,onset_event=events[j],evidence=None,participant_surface_continuity=False,outgoing_speech_domain=any(x['domain']=='Q' for x in ff[j+1:j+1+n]),comparable=False,hypotheses=['B_INDEPENDENT_SPEECH_ONSET_CANDIDATE','B_INSUFFICIENT_EVIDENCE'],status='UNADJUDICATED',selected_mother='',automatic_resolution=False))
    controls=[]
    for a,b in e.rules['explicit_control_nodes']:
        left,right=e.byid[a],e.byid[b];ev=e.pair(left,right)
        io.require(ev['clause_evidence']['evidence_flags']['S_EXPLICIT_SUBORDINATION_MARKER'] and ev['clause_evidence']['hypotaxis_supported'],'explicit subordinate control not recovered')
        controls.append(dict(pair_id='JP:JT0037:'+str(a)+':'+str(b),preceding_clause_id=a,later_clause_id=b,evidence=ev,scope='STRICT_CLAUSE_HYPOTAXIS_POSITIVE_CONTROL',macro_evidence=False,human_accepted=False,review_status='UNREVIEWED'))
    focus=[c for ref in e.rules['b_focus'] for c in e.at_ref(ref)];ids={c['clause_id'] for c in focus}
    focused=[r for r in candidates if (r['frame'] and r['frame']['clause_id'] in ids) or (r['onset'] and r['onset']['clause_id'] in ids)]
    comparable=[r for r in candidates if r['comparable'] and not (r['frame']['clause_id'] in ids or r['onset']['clause_id'] in ids)]
    report='# B — speech frame evidence, no relation selected\n\n## Exact source segmentation\n\n'
    for c in focus:report+=str(c['clause_id'])+' '+c['reference']+' domain='+c['domain']+' '+c['surface']+'\n\n'+str(e.raw(c)['signature'])+'\n\n'
    report+='## Focus sequence / participant / verb evidence\n\n'+str(focused)+'\n\n## Whole-Job comparable controls\n\n'
    report+=table([dict(ID=r['candidate_id'],Frame=r['frame']['reference'],Onset=r['onset']['reference'],Domain=r['frame']['signature']['domain'],Continuity=r['participant_surface_continuity']) for r in comparable],['ID','Frame','Onset','Domain','Continuity'])
    report+='\n'+('NO_COMPARABLE_JOB_CASE' if not comparable else 'COMPARABLE_JOB_CASES_PRESENT; HUMAN_SUFFICIENCY_UNDETERMINED')+'\n\n## Explicit clause controls\n\n'+str(controls)+'\n\nPartial speech-event similarity never proves governance or a macro mother. Raw Unknown domain remains Unknown.\n'
    return dict(files={'05_job_speech_transition_inventory.csv':io.csv_bytes(transitions),'06_job_speech_frame_candidates.csv':io.csv_bytes(candidates),'07_job_3_1_2_blind_report.md':report.encode(),'08_explicit_hypotaxis_controls.csv':io.csv_bytes(controls),'b_focus_candidates.csv':io.csv_bytes(focused),'b_comparable_cases.csv':io.csv_bytes(comparable),'b_clause_event_inventory.csv':io.csv_bytes([dict(clause_id=c['clause_id'],reference=c['reference'],event=ev) for c,ev in zip(ff,events)])},summary=dict(book_clause_count=len(ff),narrative_to_speech=sum(r['transition_kind']=='NARRATIVE_TO_DIRECT_SPEECH' for r in transitions),speech_transitions=len(transitions),frame_candidates=len(candidates),comparable_cases=len(comparable),focus_candidates=len(focused),explicit_controls=len(controls)))
