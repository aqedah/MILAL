"""Explicitly fabricated whole-book API fixture, not empirical evidence."""
from copy import deepcopy
import json
import milal_r4_0_synthetic as old
import milal_r4_0_macro_boundary_inventory as r40
import milal_r4_1_boundary_profiles as stage


def source():
    s=old.source()
    refs=[(1,1),(27,1),(29,1),(31,40),(32,1),(32,2),(32,6),(34,1),(35,1),(36,1),
          (37,24),(38,1),(40,1),(40,3),(40,6),(42,1),(42,7),(42,16),(42,17)]
    atoms={};clauses={};byref={}
    for i,(ch,v) in enumerate(refs):
        aa=[1000+i*3,1001+i*3] if (ch,v) in ((32,2),(38,1),(42,7)) else [1000+i*3]
        clauses[500+i]=aa;byref[ch,v]=aa
        for a in aa:atoms[a]=dict(atom=a,clause=500+i,chapter=ch,verse=v,ref=f'Job {ch}:{v}',index=len(atoms),surface=f'SYNTHETIC {a}')
    s['atoms']=atoms;s['clauses']=clauses
    template=deepcopy(s['markers'][0]);markers=[]
    for ref,subtype in [((27,1),'TAKE_MASHAL+AMR'),((29,1),'TAKE_MASHAL+AMR'),((32,6),'ANSWER+AMR'),
                       ((34,1),'ANSWER+AMR'),((35,1),'ANSWER+AMR'),((36,1),'ADD_SPEECH+AMR'),
                       ((38,1),'ANSWER+AMR'),((40,1),'ANSWER+AMR'),((40,3),'ANSWER+AMR'),((40,6),'ANSWER+AMR'),
                       ((42,1),'ANSWER+AMR'),((42,7),'SIMPLE_AMR'),((31,40),'CLOSE_A'),((32,1),'CLOSE_B'),((42,7),'WAYHI_POSITIVE')]:
        r=deepcopy(template);r['source_event_id']='SYNTHETIC:'+str(len(markers));r['atom_ids']=byref[ref]
        r['family']='MR1_EXPLICIT_CLOSURE' if subtype.startswith('CLOSE') else 'MR1_WAYHI_POSITIVE' if subtype=='WAYHI_POSITIVE' else 'MR1_CSF'
        r['subtype']=subtype;r['clause_ids']=[atoms[r['atom_ids'][0]]['clause']]
        r['historical_projection']=dict(csf_family=subtype,speaker_source_type='SYNTHETIC',speaker_canonical='SYNTHETIC',named_addressees='איוב' if ref==(38,1) else '')
        markers.append(r)
    s['markers']=markers
    positive=deepcopy(markers[-1]);positive['is_wayhi']=True
    negative=deepcopy(positive);negative.update(source_event_id='SYNTHETIC_NEGATIVE',atom_ids=byref[42,16],is_wayhi=False)
    s['way0']=[positive,negative]
    ordered=list(atoms);formal=[]
    for i in range(len(ordered)):
        for width in (1,2,4):
            if i+width>len(ordered):continue
            r=deepcopy(s['formal'][0]);r.update(source_event_id=f'SYNTHETIC_F{i}_{width}',atom_ids=ordered[i:i+width],family_ids=['F'+str(width)])
            formal.append(r)
    s['formal']=formal;s['formal_family_occurrence_count']=len(formal);s['singleton_context']=[]
    s['config']['expected'].update(clauses=len(clauses),atoms=len(atoms),multi_atom_clauses=3,csf=12,closure=2,positive=1)
    s['r40']=r40.build(s)
    cfg=json.loads(stage.CONFIG.read_text(encoding='utf-8'))
    cfg['saturation']=dict(atoms=len(atoms),candidates=len(s['r40']['candidates']),formal_only=sum(all(x.startswith('FORMAL:') for x in c['trigger_ids']) for c in s['r40']['candidates']),zones=len(s['r40']['zones']))
    cfg['r4_0']=dict(path='SYNTHETIC',sha256='a'*64);s['profile_config']=cfg
    s['r40_receipt']=dict(expected='a'*64,actual='a'*64,members={'SYNTHETIC':'b'*64},reproduced={'SYNTHETIC':'b'*64})
    return s
