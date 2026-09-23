"""Invented miniature FG corpus: exercises mechanics, never empirical evidence."""
import json
from milal_hsa3_fg_prep import ana, util, sha, refkey


def fixture(cfg, nodes):
    refs=set(sum((cfg[k] for k in ('spine_refs','f_refs','g_refs','formula_refs','way_refs')),[]))
    refs.update(('1:7','2:2','8:19','19:26'))
    specs={r:[] for r in refs}
    def add(ref, lex, roles=(),typ='WayX',domain='N', forms=None):
        specs[ref].append((lex,roles,typ,domain,forms or {}))
    for r in cfg['formula_refs']+['38:1','40:1','40:3','40:6','42:1']:
        subject='JHWH/' if r in ('38:1','40:1','40:6') else '>LJHW>/' if r in ('32:6','34:1','35:1','36:1') else '>JWB/'
        verb='JSP[' if r in ('27:1','29:1','36:1') else '<NH['
        lex=['W',verb,subject]; roles=[('Conj',[0]),('Pred',[1]),('Subj',[2])]
        if r in ('38:1','40:1','40:6'):
            lex+=['>T','>JWB/'];roles.append(('Objc',[3,4]))
        if r in ('38:1','40:6'):
            lex+=['MN','S<RH/'];roles.append(('Adju',[len(lex)-2,len(lex)-1]))
        add(r,lex,roles)
        if r in ('27:1','29:1'):add(r,['NF>[','MCL/'],[('Pred',[0]),('Objc',[1])],typ='InfC',forms={0:'infc'})
        add(r,['W','>MR['],[('Conj',[0]),('Pred',[1])],typ='Way0')
    for r in ('1:5','1:6','1:13','2:1'):
        add(r,['W','HJH[','H','JWM/'],[('Conj',[0]),('Pred',[1]),('Subj',[2,3])],typ='Way0')
    for r,nextref in [('1:6','1:7'),('2:1','2:2')]:
        add(r,['W','BW>[','BN/','H','>LHJM/'],[('Pred',[1]),('Subj',[2,3,4])])
        add(r,['L','JYB[','<L','JHWH/'],[('Pred',[1]),('Cmpl',[2,3])],typ='InfC',forms={1:'infc'})
        add(r,['W','BW>[','H','FVN/'],[('Pred',[1]),('Subj',[2,3])])
        add(nextref,['W','>MR[','JHWH/','>L','FVN/'],[('Pred',[1]),('Subj',[2]),('Cmpl',[3,4])])
    add('1:13',['W','BN/','BT/','>KL['],[('Subj',[1,2]),('Pred',[3])],typ='Ptcp',forms={3:'ptca'})
    add('3:1',['>XR/','KN','PTX[','>JWB/','PH/'],[('Time',[0,1]),('Pred',[2]),('Subj',[3]),('Objc',[4])],typ='xQtX',forms={2:'perf'})
    add('42:7',['W','HJH['],[('Conj',[0]),('Pred',[1])],typ='Way0')
    add('42:7',['>XR/','DBR[','JHWH/','>T','DBR/','>LH','>L','>JWB/'],[('Conj',[0]),('Pred',[1]),('Subj',[2]),('Objc',[3,4,5]),('Cmpl',[6,7])],typ='xQtX',forms={1:'perf'})
    add('42:16',['W','XJH[','>JWB/','>XR/','Z>T','CNH/'],[('Conj',[0]),('Pred',[1]),('Subj',[2]),('Time',[3,4]),('Time',[5])])
    for r,verb in [('42:10','CWB=['),('42:12','BRK[')]:
        add(r,['W','JHWH/',verb,'>T','>JWB/'],[('Conj',[0]),('Subj',[1]),('Pred',[2]),('Objc',[3,4])],typ='WXQt',forms={2:'perf'})
    add('42:12',['W','HJH[','L','CNH/'],[('Pred',[1]),('Cmpl',[2,3])])
    for r in ('38:3','40:7'):
        add(r,cfg['patterns']['challenge'],[('Pred',[0]),('Intj',[1]),('Adju',[2,3]),('Objc',[4])],typ='ZIm0',domain='Q',forms={0:'impv'})
    add('8:19',['>XR=/','YMX['],[('Subj',[0]),('Pred',[1])],domain='Q')
    add('19:26',['>XR/','<WR/','NQP['],[('Adju',[0,1]),('Pred',[2])],domain='Q')
    # IDs are intentionally borrowed only from explicit synthetic frozen-node
    # anchors so exact-identity linkage is tested. No empirical selection uses refs.
    anchors={}
    for n in nodes:
        raw=[int(x.split(':')[-1]) for x in n['source_evidence_ids'] if x.startswith('BHSA2021:clause:')]
        if raw and n['reference_start'] in refs:
            anchors.setdefault(n['reference_start'],min(raw))
    serial=10000000; native=[];used=set();csf=[];way=[]
    surfaces={'>XR/':'אחרי ', '>XR=/':'אחר ', 'KN':'כן ', 'Z>T':'זאת ', 'HJH[':'יהי ', 'XJH[':'יחי ',
        'W':'ו', 'PTX[':'פתח ', '>JWB/':'איוב ', 'JHWH/':'יהוה ', 'DBR[':'דבר ', 'JSP[':'יסף ',
        '>LJHW>/':'אליהוא ', 'NF>[':'שאת ', 'MCL/':'משלו ', '>ZR[':'אזר ', 'N>':'נא ', 'K':'כ', 'GBR/':'גבר ', 'XLY/':'חלציך '}
    for ref in sorted(refs,key=refkey):
        if not specs[ref]:add(ref,['>JWB/','DBR['],[('Subj',[0]),('Pred',[1])])
        for ordinal,(lex,roles,typ,domain,forms) in enumerate(specs[ref]):
            serial+=100;cid=anchors.get(ref,serial) if ordinal==0 else serial
            if cid in used:cid=serial
            used.add(cid);words=[];phrases=[]
            for i,l in enumerate(lex):
                w={k:None for k in ana.FEATURES};verb=l.endswith('[')
                sp='verb' if verb else 'nmpr' if l in ('>JWB/','JHWH/','>LJHW>/') else 'subs'
                w.update(node=serial+i+1,reference=ref,surface=surfaces.get(l,l+' '),lex=l,lex0=l,lex_utf8=surfaces.get(l,l).strip(),
                    sp=sp,pdp=sp,vt=forms.get(i,'wayq') if verb else 'NA',vs='qal' if verb else 'NA',ps='p3',gn='m',nu='sg',
                    clause_atom_ids=[serial+70],phrase_ids=[])
                words.append(w)
            for j,(function,ii) in enumerate(roles):
                p=serial+80+j
                for i in ii:words[i]['phrase_ids'].append(p)
                phrases.append(dict(node=p,function=function,type='SYNTHETIC',word_nodes=[words[i]['node'] for i in ii],surface=''.join(words[i]['surface'] for i in ii)))
            native.append(dict(clause=cid,ref=ref,words=words,phrases=phrases,surface=''.join(w['surface'] for w in words),clause_atom_ids=[serial+70],type=typ,domain=domain,txt=domain,synthetic_anchor='SYNTHETIC:NATIVE:'+ref if ordinal==0 else '',corroboration=[dict(node=cid,node_type='clause',mother=[],rela='NA',code=None,tab=None,pargr=None)]))
            if ordinal==0 and ref in cfg['formula_refs']+cfg['f_refs']:
                csf.append(dict(current_event_id='SYNTHETIC_CSF:'+ref,start_clause=cid,historical_projection=dict(csf_family='SYNTHETIC',speaker_canonical='SYNTHETIC_NOT_IDENTITY')))
            if typ=='Way0':way.append(dict(current_event_id='SYNTHETIC_WAY:'+str(cid),start_clause=cid,is_wayhi='HJH[' in lex,historical_projection=dict(clause_type=typ)))
    mf={'02_csf_reproduction.csv':util.csv_bytes(csf),'04_way0_wayhi_reproduction.csv':util.csv_bytes(way)}
    mf['99_manifest_sha256.csv']=util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(mf.items())])
    execution=dict(mode='SYNTHETIC',bhsa_version='SYNTHETIC',tf_version='SYNTHETIC',book_word_nodes=[w['node'] for c in native for w in c['words']],data_hashes={},feature_versions={})
    return native,execution,mf
