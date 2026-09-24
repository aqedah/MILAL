"""Neutral constructed raw clauses for tests; no historical relation labels."""
from copy import deepcopy


def clause(ident,chapter=1,verse=1,typ='XQtl',verb='>MR[',subject='PERSON/',tense='perf',relative=False,time=False):
    words=[];phrases=[]
    def add(lex,sp,function,**extra):
        n=ident*100+len(words)+1
        w=dict(node=n,lex=lex,lex_utf8=lex,g_word_utf8=lex,trailer_utf8=' ',sp=sp,pdp=sp,vt='NA',vs='NA',ps='NA',gn='m',nu='sg',prs_ps='NA',prs_gn='NA',prs_nu='NA',chapter=chapter,verse=verse)
        w.update(extra);words.append(w);phrases.append(dict(node=n+1000000,word_nodes=[n],function=function,typ='VP' if sp=='verb' else 'NP'))
    if relative:add('>CR','conj','Rela')
    if time:add('JWM/','subs','Time')
    add(verb,'verb','Pred',vt=tense,vs='qal',ps='p3')
    if subject:add(subject,'nmpr','Subj')
    return dict(clause_id=ident,clause_atom_ids=[ident+100000],chapter=chapter,verse=verse,reference=f'{chapter}:{verse}',
        word_start=words[0]['node'],word_end=words[-1]['node'],word_nodes=[w['node'] for w in words],surface=''.join(w['g_word_utf8']+' ' for w in words),
        clause_type=typ,domain='N',text_type='N',words=words,phrases=phrases)


def corpus(targets):
    return [clause(i+1,t['chapter'],t['verse'],typ='XQtl' if i%2 else 'WayX') for i,t in enumerate(targets)]


def controls():
    return {
        'S1':[clause(1),clause(2)],
        'S2':[clause(1),clause(2,relative=True)],
        'S3':[clause(1),clause(2,typ='WayX')],
        'S4':[clause(1),clause(2,typ='WayX',relative=True)],
        'S5':[clause(1),clause(2,relative=True)],
        'S6':[clause(1,time=True),clause(2,time=True)],
        'S7':[clause(1),clause(2),clause(3),clause(4,relative=True)],
        'S8':[clause(1),clause(2,verb='HLK[',tense='impf')],
        'S9':[clause(1,subject='A/'),clause(2,typ='WayX',verb='HLK[',subject='B/',tense='impf')],
        'S10':dict(composition_group='FORBIDDEN_CONSTRUCTED_GROUP')}
