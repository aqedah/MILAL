"""Focused synthetic corpus and twelve independent semantic controls."""
from copy import deepcopy
import json
from pathlib import Path
import milal_jin_io as io
import milal_jin_relation_rules as rr
from milal_jin_synthetic import clause
from milal_jin_focused_common import Evidence,macro_hypothesis
from milal_jin_speech_frame_audit import event

REFS='1:5 1:6 1:13 1:14 1:16 1:17 1:18 1:22 2:1 2:9 2:10 2:11 3:1 3:2 4:1 6:1 8:1 9:1 11:1 11:4 12:1 15:1 16:1 18:1 19:1 20:1 21:1 22:1 23:1 25:1 26:1 27:1 28:1 29:1 31:40 32:1 32:2 32:6 34:1 35:1 36:1 37:24 38:1 40:1 40:3 40:6 42:1 42:7 42:16'.split()


def mouth(c):
    w=deepcopy(c['words'][-1]);w.update(node=c['word_end']+1,lex='PH/',sp='subs',pdp='subs',g_word_utf8='PH/',vt='NA',ps='NA');c['words'].append(w);c['word_nodes'].append(w['node']);c['word_end']=w['node'];c['phrases'].append(dict(node=w['node']+1000000,word_nodes=[w['node']],function='Objc',typ='NP'));c['surface']+='PH/ ';return c


def corpus():
    raw=[]
    for ref in sorted(set(REFS+['1:1','1:4','1:7','1:12','3:3','32:3']),key=lambda r:tuple(map(int,r.split(':')))):
        ch,v=map(int,ref.split(':'))
        for j in range(4 if ref in ('1:6','2:1') else 2):
            c=clause(len(raw)+1,ch,v,verb='HLK[',subject='PERSON/' if ref not in ('1:6','1:12','2:1') else 'OTHER/',relative=ref=='32:3' and j==0)
            if ref in ('1:6','2:1') and j==0:c=clause(len(raw)+1,ch,v,verb='HJH[',subject='OTHER/',typ='Way0',tense='wayq',time=True)
            if ref=='3:1' and j==0:c=mouth(clause(len(raw)+1,ch,v,verb='PTX[',subject='JOB/'))
            if ref=='3:1' and j==1:c=clause(len(raw)+1,ch,v,verb='QLL[',subject='JOB/')
            if ref=='3:2':c=clause(len(raw)+1,ch,v,verb='<NH[' if j==0 else '>MR[',subject='JOB/')
            if ref=='3:3':c['domain']='Q'
            raw.append(c)
    targets=[dict(audit_target_id='JT'+str(i+1).zfill(4),book='Job',chapter=int(r.split(':')[0]),verse=int(r.split(':')[1])) for i,r in enumerate(REFS)]
    a=[c['clause_id'] for c in raw if c['reference']=='32:2'];b=next(c['clause_id'] for c in raw if c['reference']=='32:3')
    return raw,targets,[[x,b] for x in a]


def controls(rules,ling,context):
    raw=[clause(i+1,1,i+1,verb='HLK[',subject=s) for i,s in enumerate(['A/','B/','A/'])]
    ff=rr.extract(raw,ling);targets=[dict(audit_target_id='JT'+str(i),clause_id=[c['clause_id']]) for i,c in enumerate(ff)]
    e=Evidence(ff,targets,rules,context,ling);res=e.resumption([ff[0]],[ff[2]],[ff[1]])
    form=mouth(clause(11,verb='PTX[',subject='JOB/'));csf=clause(12,verb='>MR[',subject='JOB/')
    ev=event(rr.extract([form],ling)[0],[],rules);cs=rr.extract([csf],ling)[0]
    relative=rr.extract([clause(20),clause(21,relative=True)],ling);local=rr.evidence(*relative,ling)
    # Same ordered following sequences vs distinct configurations.
    seq=[clause(i+1,verse=i+1,verb='HLK[',subject='A/') for i in range(8)]
    ee=Evidence(rr.extract(seq,ling),[],rules,context,ling);same=ee.ctx.compare(1,5)
    changed=deepcopy(seq)
    for i in (5,6,7):changed[i]=clause(i+1,verse=i+1,verb='DBR[',subject='B/',typ='NmCl',tense='impf')
    ec=Evidence(rr.extract(changed,ling),[],rules,context,ling);contrast=ec.ctx.compare(1,5)
    # Morphological reference compatibility is a hypothesis, not accepted identity.
    dep=[clause(30,verse=1,verb='HLK['),clause(31,verse=2,verb='HLK[')]
    dep[1]['words'][-1]['prs_ps']='p3';dep[1]['words'][-1]['prs_gn']='m';dep[1]['words'][-1]['prs_nu']='sg'
    dd=rr.extract(dep,ling);ed=Evidence(dd,[],rules,context,ling);p=ed.pair(dd[0],dd[1]);empty=ed.resumption([dd[0]],[dd[1]],[])
    positive=macro_hypothesis(p,empty,True,True);excluded=macro_hypothesis(p,empty,True,False)
    unrelated=rr.extract([clause(40,verb='HLK[',subject='A/'),clause(41,verb='DBR[',subject='B/',typ='NmCl',tense='impf')],ling);eu=Evidence(unrelated,[],rules,context,ling)
    zero=macro_hypothesis(eu.pair(*unrelated),eu.resumption([unrelated[0]],[unrelated[1]],[]),True,True)
    return dict(S1=res['candidate'],S2=contrast['configuration_status']=='CONFIGURATION_CONTRAST',S3=same['configuration_status']=='EXACT_CONFIGURATION_CORRESPONDENCE',S4=ev['frame_candidate'] and event(cs,[],rules)['formal_onset'],S5=ev['frame_candidate'] and not ev['formal_onset'],S6=event(cs,[],rules)['formal_onset'] and not event(cs,[],rules)['frame_candidate'],S7=local['hypotaxis_supported'] and local['evidence_flags']['S_EXPLICIT_SUBORDINATION_MARKER'],S8=not excluded['macro_mother_supported'],S9=positive['macro_mother_supported'],S10=len([h for h in [positive,deepcopy(positive)] if h['macro_mother_supported']])==2,S11=not zero['macro_mother_supported'],S12=res['candidate'] and not res['immediate_shared_participants'])
