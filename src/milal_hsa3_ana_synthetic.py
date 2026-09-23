"""Invented miniature corpus for ANA mechanics; never empirical BHSA evidence."""
import json
from milal_hsa3_ana_response_frame import CONFIG, FEATURES


def fixture(prior):
    cfg=json.loads(CONFIG.read_bytes());spec={};serial=10000000
    def word(lex,**kw):
        d={k:None for k in FEATURES};d.update(lex=lex,lex_utf8='ענה' if lex.startswith('<NH') else lex,
            lex0=lex,gloss='answer' if lex=='<NH[' else 'synthetic',sp='subs',pdp='subs',g_word_utf8=lex,
            vt='NA',vs='NA',ps='NA',gn='NA',nu='NA',prs_ps='NA',prs_gn='NA',prs_nu='NA');d.update(kw);return d
    def ana(**kw):return word('<NH[',sp='verb',pdp='verb',vt='impf',vs='qal',ps='p3',gn='m',nu='sg',**kw)
    def add(ref,words,roles=(),mother=None):spec.setdefault(ref,[]).append((words,roles,mother))
    def csf(ref,target=False):
        ww=[word('<NH[',sp='verb',vt='wayq',vs='qal',ps='p3'),word('JHWH/' if target else '>JWB/',sp='nmpr',lex_utf8='יהוה' if target else 'איוב')]
        roles=[('Subj',[1])]
        if target:ww.append(word('>JWB/',sp='nmpr',lex_utf8='איוב'));roles.append(('Objc',[2]))
        add(ref,ww,roles);add(ref,[word('>MR[',sp='verb',vt='wayq')])
    for ref in ('3:2','4:1','32:6','34:1','35:1','40:3','42:1'):csf(ref)
    for ref in ('38:1','40:1','40:6'):csf(ref,True)
    add('2:13',[word('>JN/'),word('DBR[',sp='verb',vt='ptca')])
    add('3:1',[word('PTX[',sp='verb'),word('>JWB/',sp='nmpr'),word('PH/')],[('Subj',[1]),('Objc',[2])])
    add('31:35',[word('MJ'),word('NTN[',sp='verb')])
    add('31:35',[word('CDJ/',sp='nmpr',lex_utf8='שדי'),ana(prs_ps='p1')],[('Subj',[0])])
    add('31:40',[word('TMM[',sp='verb'),word('DBR/'),word('>JWB/',sp='nmpr')])
    add('32:1',[word('CBT[',sp='verb'),word('CLC/'),word('>JC/')],[('Subj',[1,2])])
    add('32:1',[word('<NH[',sp='verb',vt='infc'),word('>JWB/',sp='nmpr',lex_utf8='איוב')],[('Objc',[1])],0)
    add('32:12',[word('>JN/')]);add('32:12',[word('JKX[',sp='verb')],mother=0)
    add('32:12',[word('<NH[',sp='verb',vt='ptca'),word('>MR/')],[('Objc',[1])],1)
    add('32:14',[word('L>'),word('CWB[',sp='verb')])
    for ref in ('32:15','32:16','33:13','40:5'):add(ref,[word('L>'),ana()])
    add('32:17',[word('>P'),word('>NJ'),word('<NH[',sp='verb',vt='impf',ps='p1',vs='hif')])
    add('32:20',[word('<NH[',sp='verb',vt='impf',ps='p1')])
    add('33:12',[word('<NH[',sp='verb',vt='impf',ps='p1',prs_ps='p2')])
    add('33:14',[word('DBR[',sp='verb'),word('>L/')],[('Subj',[1])])
    add('36:1',[word('JSP[',sp='verb'),word('>LJHW/',sp='nmpr')],[('Subj',[1])]);add('36:1',[word('>MR[',sp='verb')])
    for ref in ('30:11','37:23'):add(ref,[word('<NH=[',sp='verb',vs='piel',gloss='be lowly')])
    add('40:2',[ana()])
    for ref in cfg['focus_refs']:
        if ref not in spec:add(ref,[word('SYNTHETIC_CONTEXT')])
    native=[];events=[]
    cycle_ids={e['source_node'] for e in prior['edges'] if e['relation_type']=='GROUP_MEMBER_OF' and e['target_node']=='CYCLE_1'}
    evidence=[e.removeprefix('R4.1:') for n in prior['nodes'] if n['node_id'] in cycle_ids for e in n['source_evidence_ids'] if e.startswith(('MR1:','R4.1:MR1:'))]
    for ref in sorted(spec,key=lambda x:tuple(map(int,x.split(':')))):
        local=[]
        for wi,roles,mother in spec[ref]:
            serial+=100;cid=serial;ww=[];pp=[]
            for i,w in enumerate(wi):ww.append(dict(w,node=cid+i+1,reference=ref,surface=w['lex_utf8']+' ',clause_atom_ids=[cid+50],phrase_ids=[]))
            for j,(function,indexes) in enumerate(roles):
                pid=cid+60+j
                for i in indexes:ww[i]['phrase_ids'].append(pid)
                pp.append(dict(node=pid,function=function,type='NP',word_nodes=[ww[i]['node'] for i in indexes],surface=''.join(ww[i]['surface'] for i in indexes)))
            c=dict(clause=cid,ref=ref,chapter=int(ref.split(':')[0]),verse=int(ref.split(':')[1]),surface=''.join(w['surface'] for w in ww),
                clause_atom_ids=[cid+50],words=ww,phrases=pp,type='SYNTHETIC',domain='Q',rela='Adju' if mother is not None else 'NA',code=None,
                bhsa_mother_nodes=[local[mother]['clause']] if mother is not None else [])
            local.append(c);native.append(c)
        if local[0]['words'][0]['lex']=='<NH[' and local[0]['words'][0]['vt']=='wayq':
            eid=evidence[0].removeprefix('MR1:') if ref=='4:1' and evidence else 'SYNTHETIC:'+ref
            events.append(dict(current_event_id=eid,start_clause=local[0]['clause'],end_clause=local[-1]['clause'],historical_projection=dict(
                speech_level='TOP_LEVEL_CSF',speaker_canonical='SYNTHETIC_SPEAKER',ref='Job '+ref,csf_family='ANSWER+AMR')))
    execution=dict(dataset_version='SYNTHETIC',tf_version='SYNTHETIC',data_path='SYNTHETIC',data_hashes={},book_node=-1,
                   book_word_nodes=sorted(w['node'] for c in native for w in c['words']))
    return native,execution,events
