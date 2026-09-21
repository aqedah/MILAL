"""Fabricated R4 inputs; contains no empirical occurrences or source substitutions."""
from copy import deepcopy
import json
import milal_r4_0_sources as src
import milal_hr1_adjudication_linkage as hr


def source():
    cfg=json.loads(src.CONFIG.read_text(encoding='utf-8'))
    cfg.update(scope=['Job 1:1','Job 42:17'],controls=['1:1','27:1','29:1','31:40','32:1','32:2','37:24','38:1','40:1','42:7','42:16','42:17'],zone_span_atoms=2)
    cfg['expected']=dict(clauses=12,atoms=13,multi_atom_clauses=1,csf=2,closure=1,way0=2,positive=1,negative=1,human=30)
    loc=lambda role,n:dict(archive_role=role,archive_sha256='a'*64,member='SYNTHETIC.csv',member_sha256='b'*64,data_row=n,row_sha256='c'*64)
    refs=[(1,1),(27,1),(29,1),(31,40),(32,1),(32,2),(37,24),(38,1),(40,1),(42,7),(42,16),(42,17)]
    atoms,clauses={},{}
    for i,(ch,v) in enumerate(refs):
        aa=[100+i*2,101+i*2] if i==0 else [100+i*2]
        clauses[500+i]=aa
        for a in aa:atoms[a]=dict(atom=a,clause=500+i,chapter=ch,verse=v,ref=f'Job {ch}:{v}',index=len(atoms),surface='SYNTHETIC')
    def marker(eid,family,aa,subtype):
        return dict(source_event_id=eid,family=family,atom_ids=aa,clause_ids=list(dict.fromkeys(atoms[a]['clause'] for a in aa)),
                    source_rule_id='SYNTHETIC_RULE',provenance_locator=loc('mr1',len(eid)),subtype=subtype,
                    surface_text='SYNTHETIC',historical_projection={})
    markers=[marker('csf:1','MR1_CSF',[100,101],'SIMPLE_AMR'),marker('csf:2','MR1_CSF',[114],'ANSWER+AMR'),
             marker('closure:1','MR1_EXPLICIT_CLOSURE',[106],'תממ+דבר'),marker('way0:1','MR1_WAYHI_POSITIVE',[118],'WAYHI_POSITIVE')]
    positive=deepcopy(markers[-1]);positive['is_wayhi']=True
    negative=marker('way0:2','WAY0_AUDIT',[120],'WAY0_NEGATIVE');negative['is_wayhi']=False
    human,cases=[],[]
    for i in range(1,31):
        cid=f'CASE{i:03}'
        row=dict(case_id=cid,case_type='SYNTHETIC',form_assessment='PARTIAL' if i==1 else 'INSUFFICIENT' if i==2 else 'CLEAR',
                 **{f:'' for f in hr.frozen.REVIEW_FIELDS})
        row.update(review_status='REVIEWED',sufficient_context='YES',reviewer_notes='SYNTHETIC '+cid)
        if cid=='CASE028':row['reviewer_notes']='Synthetic ending; adjacency is not direct discourse continuity.'
        if cid=='CASE029':row['reviewer_notes']='Synthetic beginning; Job is explicit addressee.'
        human.append(row)
        cases.append(dict(row,extension_dependency_cases=list(hr.SEQUENCE_CASES) if cid in hr.SEQUENCE_CASES else [],
                          extension_dependency_note='SYNTHETIC one dependent sequence' if cid in hr.SEQUENCE_CASES else '',human_adjudication_locator=loc('human',i)))
    boundaries=[]
    for i,ref in enumerate(['31:40','32:1','32:2','37:24','38:1','42:7'],25):
        cid=f'CASE{i:03}'
        boundaries.append(dict(case_id=cid,boundary_identity=dict(case_id=cid,boundary_ref=ref),participating_unit_ids=['SYNTHETIC_UNIT'],
                               locator=loc('r3c3',i),human_adjudication_locator=loc('human',i)))
    formal=[dict(source_event_id='RB1:W1',bundle_id='RB1',window_id='W1',family_ids=['F1'],atom_ids=[102,104],surface_text='SYNTHETIC',
                 provenance_locator=loc('prov1',1),source_locators=[loc('prov1',1),loc('prov1',2)])]
    extensions=[dict(layer='SEQUENCE_EXTENSION_OVERLAY_ONLY',short_case_ids=[hr.SEQUENCE_CASES[i]],long_case_ids=[hr.SEQUENCE_CASES[i+1]],
                     locator=loc('prov1',i+10),source_relation=dict(short_bundle_id='S'+str(i),long_bundle_id='S'+str(i+1)),independent_evidence_warning_source=loc('human',12)) for i in range(5)]
    cfg['sources']={k:dict(path='SYNTHETIC_'+k,sha256=src.sha(k.encode())) for k in ('mr1','r3c3','prov1','hr1','human')}
    return dict(config=cfg,mode='SYNTHETIC_NOT_EMPIRICAL',atoms=atoms,clauses=clauses,scope=cfg['scope'],
                execution=dict(bhsa_version='2021',tf_version='13.1.0',data_path='SYNTHETIC_API_NOT_LOADED'),
                mr_meta=dict(status='PASS',byte_comparison={k:dict(equal=True) for k in ('surface','csf','closure','way0')}),
                markers=markers,way0=[positive,negative],formal=formal,formal_family_occurrence_count=1,
                singleton_context=[dict(review_item_id='S1',atom=120,provenance_locator=loc('prov1',50),trigger_eligible=False,reason='UNIQUENESS_NOT_BOUNDARY_TRIGGER')],
                human=human,cases=cases,boundaries=boundaries,extensions=extensions,human_evidence=[],human_provenance=[],
                sources=[dict(source_layer=k,path_archive=v['path'],SHA256=v['sha256'],status='SYNTHETIC_FIXTURE',role=k) for k,v in cfg['sources'].items()],
                verified_hashes={k:v['sha256'] for k,v in cfg['sources'].items()},
                manifest_receipts={k:dict(actual={'SYNTHETIC.csv':'a'*64},expected={'SYNTHETIC.csv':'a'*64}) for k in ('mr1','r3c3','prov1','hr1')})
