"""Small raw linguistic fixtures, with artificial corpus metadata."""
from copy import deepcopy

def corpus():
    result=[]
    patterns=[('>MR[','JHWH/',True,True),('DBR[','PN/',False,False),('HLK[','PN/',False,False),('JCB[','PN/',False,False),
              ('>MR[','JHWH/',True,False),('DBR[','PN/',False,False),('HLK[','PN/',False,False),('TMM[','DBR/',False,False),
              ('MWT[','MCH=/',False,False),('HJH[','MCH=/',True,False),('>MR[','JHWH/',False,True),('DBR[','PN/',False,False),
              ('HLK[','PN/',False,False),('>MR[','JHWH/',True,True),('DBR[','PN/',False,False),('HLK[','PN/',False,False),
              ('JCB[','PN/',False,False),('JSP[','PN/',False,False),('PTX[','PN/',False,False),('DBR[','PN/',True,False)]
    for i,(verb,subject,time,loca) in enumerate(patterns):
        n=i+1;words=[];phrases=[];base=1000+n*30
        def phrase(function,items,typ='NP'):
            ids=[]
            for lex,pos in items:
                wid=base+len(words);ids.append(wid);words.append(dict(node=wid,lex=lex,lex_utf8=lex,g_word_utf8=lex,trailer_utf8=' ',sp=pos,pdp=pos,vt='wayq' if pos=='verb' else None,vs='qal' if pos=='verb' else None,ps='p3' if pos=='verb' else None,gn='m',nu='sg',prs_ps=None,prs_gn=None,prs_nu=None))
            phrases.append(dict(node=5000+n*10+len(phrases),word_ids=ids,function=function,typ=typ))
        phrase('Pred',[(verb,'verb')],'VP');phrase('Subj',[(subject,'nmpr')]);
        if verb=='>MR[':phrase('Cmpl',[('>L','prep'),('MCH=/','nmpr')],'PP')
        if time:phrase('Time',[('B','prep'),('CNH/','subs'),('>XD/','adjv')],'PP')
        if loca:phrase('Loca',[('B','prep'),('MDBR/','subs')],'PP')
        if n==10:phrase('Time',[('>XR/','prep'),('MWT[','verb'),('MCH=/','nmpr')],'PP')
        if n in (4,17):phrase('Rela',[('>CR','conj')])
        if n==18:phrase('Objc',[('MCL/','subs')])
        if n==19:phrase('Objc',[('PH/','subs')])
        ids=[w['node'] for w in words];result.append(dict(book='Alpha' if n<10 else 'Beta',chapter=8,verse=n,clause_id=100+n,clause_atom_ids=[200+n],atoms=[dict(node=200+n,word_ids=ids,typ='Way0')],word_ids=ids,words=words,phrases=phrases,clause_type='Way0',domain='N'))
    return result
