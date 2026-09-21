"""Fabricated participant-source fixture; never used as empirical input."""
import json
from copy import deepcopy
import milal_r4_0_synthetic as old
import milal_r4_2_participant_audit as p


def source():
    s=old.source();cfg=json.loads(p.CONFIG.read_text(encoding='utf-8'));s['cfg42']=cfg
    refs=sorted(set(cfg['controls']+['1:1','42:17']),key=lambda r:tuple(map(int,r.split(':'))))
    atoms={};clauses={};native=[];byref={}
    def word(n,lex,sp,nu='sg'):
        return dict({k:'' for k in p.FEATURES},node=n,surface=lex,lex=lex,lex_utf8=lex,sp=sp,pdp=sp,nu=nu,vt='perf' if sp=='verb' else 'NA')
    for i,ref in enumerate(refs):
        ch,v=map(int,ref.split(':'));a=1000+i;c=2000+i;ph=3000+i*10;w=10000+i*20
        aa=[a];byref[ref]=aa;clauses[c]=aa;atoms[a]=dict(atom=a,clause=c,chapter=ch,verse=v,ref='Job '+ref,index=i,surface='SYNTHETIC '+ref)
        verb='אמר';subject=[word(w+2,'שם','nmpr')]
        if ref in ('1:14','1:16','1:17','1:18'):
            verb='בוא';subject=[word(w+2,'מלאך','subs')] if ref=='1:14' else [word(w+2,'זה','prde')]
        if ref=='2:9':subject=[word(w+2,'אשׁה','subs')];subject[0]['prs_ps']='p3'
        if ref=='2:11':verb='שׁמע';subject=[word(w+2,'שׁלשׁ','subs'),word(w+3,'רע','subs','pl'),word(w+4,'איוב','nmpr')]
        if ref=='32:2':verb='חרה';subject=[word(w+2,'אף','subs'),word(w+3,'אליהוא','nmpr')]
        if ref=='3:1':verb='פתח'
        if ref in ('1:22','2:10'):verb='חטא'
        phrases=[dict(node=ph,function='Pred',type='VP',surface=verb,words=[word(w,verb,'verb')]),dict(node=ph+1,function='Subj',type='NP',surface=' '.join(x['surface'] for x in subject),words=subject)]
        native.append(dict(clause=c,clause_atom_ids=aa,chapter=ch,verse=v,ref='Job '+ref,type='SYNTHETIC',domain='N',surface='SYNTHETIC '+ref,phrases=phrases,atom_structure=[dict(atom=a,type='SYNTHETIC',word_nodes=[z['node'] for pp in phrases for z in pp['words']])]))
    s.update(atoms=atoms,clauses=clauses,native_clauses=native,human42=json.loads(p.HUMAN.read_text(encoding='utf-8')))
    s['execution']['data_hashes']={'SYNTHETIC/otype.tf':'a'*64}
    anchors=[];s['markers']=[]
    loc=dict(archive_role='SYNTHETIC',archive_sha256='a'*64,member='SYNTHETIC.csv',data_row=1)
    for ref in ('1:6','1:13','2:1','3:2','31:40','32:1','32:6'):
        family='MR1_EXPLICIT_CLOSURE' if ref in ('31:40','32:1') else 'MR1_CSF'
        aid='MR1:SYNTHETIC:'+ref
        anchors.append(dict(anchor_id=aid,source_type='MR1',marker_family=family,atom_ids=byref[ref],source_locator=loc,ref_start='Job '+ref))
        s['markers'].append(dict(source_event_id=aid,family=family,atom_ids=byref[ref],historical_projection={},provenance_locator=loc))
    formal=[dict(source_event_id='SYNTHETIC:F:'+r,atom_ids=aa,family_ids=['F1'],family_signature_definitions=[dict(family_id='F1',level='G0')],source_locators=[loc]) for r,aa in byref.items()]
    s['r41']=dict(anchors=anchors,formal=formal,human=deepcopy(s['human']),extensions=deepcopy(s['extensions']),human_links=[],way0_audit=[])
    s['receipt42']=dict(actual={'SYNTHETIC':'a'*64},expected={'SYNTHETIC':'a'*64},archive_sha=cfg['r4_1']['sha256'])
    s['rules_receipt']=p.sha(p.canonical(cfg['rules']).encode())
    return s
