"""Invented extensions to the existing synthetic baseline, never real BHSA."""
from copy import deepcopy
from milal_hsa3_ana_response_frame import FEATURES


def extend(native):
    def new_word(c,offset,lex,utf,gloss,**features):
        w={k:None for k in FEATURES};w.update(lex=lex,lex_utf8=utf,lex0=lex.rstrip('/[').replace('=',''),gloss=gloss,sp='subs',pdp='subs',vt='NA',vs='NA',ps='NA',gn='NA',nu='NA',prs_ps='NA',prs_gn='NA',prs_nu='NA');w.update(features)
        w.update(node=c['clause']+offset,reference=c['ref'],surface=utf+' ',clause_atom_ids=c['clause_atom_ids'],phrase_ids=[]);return w
    def phrase(c,function,ww):
        node=c['clause']+70+len(c['phrases'])
        for w in ww:w['phrase_ids'].append(node)
        c['phrases'].append(dict(node=node,function=function,type='NP',word_nodes=[w['node'] for w in ww],surface=''.join(w['surface'] for w in ww)))
    def ref(r):return next(c for c in native if c['ref']==r)
    for r in ('32:3','32:5'):
        c=ref(r);c['words']=[];c['phrases']=[]
        neg=new_word(c,1,'L>' if r=='32:3' else '>JN/','לא' if r=='32:3' else 'אין','not')
        noun=new_word(c,2,'M<NH=/','מענה','answer');c['words']=[neg,noun];phrase(c,'Objc' if r=='32:3' else 'Subj',[noun])
    c=ref('32:14');c['phrases']=[]
    w=next(w for w in c['words'] if w['lex']=='CWB[');w.update(lex_utf8='שׁוב',vs='hif',vt='impf',ps='p1',prs_ps='p3')
    utterance=new_word(c,20,'>MR/','אמר','word',prs_ps='p2');c['words'].append(utterance);phrase(c,'Cmpl',[utterance])
    c=ref('37:24');w=new_word(c,20,'M<NH/','מענה','hiding place',root='<WN');c['words'].append(w)
    c=ref('32:13');w=new_word(c,20,'<T/','עת','time',root='<NH');c['words'].append(w)
    c=deepcopy(native[0]);c.update(clause=9000000,ref='1:21',chapter=1,verse=21,clause_atom_ids=[9000050],words=[],phrases=[],bhsa_mother_nodes=[])
    w=new_word(c,1,'CWB[','שׁוב','return',sp='verb',vs='hif',vt='impf',ps='p2',prs_ps='p1');p=new_word(c,2,'<PR/','עפר','dust');c['words']=[w,p];phrase(c,'Cmpl',[p]);native.append(c)
    c=deepcopy(c);c.update(clause=9000100,ref='1:22',verse=22,clause_atom_ids=[9000150],words=[],phrases=[])
    c['words']=[new_word(c,1,'CWB[','שׁוב','return',sp='verb',vs='hif',vt='impf',ps='p3',prs_ps='p1')];native.append(c)
    for c in native:c['surface']=''.join(w['surface'] for w in c['words'])
    return sorted(native,key=lambda c:(tuple(map(int,c['ref'].split(':'))),c['clause']))
