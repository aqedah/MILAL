"""Fictional HSA2 evidence for audit tests; not empirical BHSA data."""
import json
from copy import deepcopy
import milal_hsa2_closure_audit as h


def source():
    cfg=json.loads(h.CONFIG.read_text(encoding='utf-8'));rows=h.registry()
    refs=set(cfg['review_references']+cfg['comparison_controls']+['26:14','27:2','28:28','29:2','31:39','32:1'])
    refs=sorted(refs,key=lambda x:tuple(map(int,x.split(':'))))
    cat={};native_order=[]
    def add(key,kind,atoms,row,deps=()):
        cat[key]=dict(evidence_id=key,source_layer='SYNTHETIC',evidence_kind=kind,atom_ids=atoms,source_row=row,
            source_locator={'fixture':key,'row_sha256':h.sha(h.canonical(row).encode())},dependencies=list(deps))
    for i,ref in enumerate(refs,1):
        atoms=[-10000+i*10+j for j in range(3)];native_order+=atoms
        clause=str(-i);words=[];structure=[]
        for j,a in enumerate(atoms):
            lex=['JSP[','MCL/','>MR['][j] if ref in ('27:1','29:1') else ['TMM[','DBR/','>JWB/'][j]
            w=dict(node=a*10,lex=lex,lex_utf8='משל' if lex=='MCL/' else 'SYNTHETIC')
            words.append(w);structure.append(dict(atom=a,type='SYNTHETIC',word_nodes=[w['node']]))
        native='BHSA2021:clause:'+clause
        add(native,'NATIVE_CLAUSE_SNAPSHOT_NOT_A_BOUNDARY',atoms,dict(clause=clause,clause_atom_ids=h.canonical(atoms),
            ref='Job '+ref,type='SYNTHETIC',surface='[SYNTHETIC] '+ref,phrases=h.canonical([dict(words=words)]),atom_structure=h.canonical(structure)))
        deps=[native]
        subtype=''
        if ref in [r for c in cfg['cycles'] for r in c['refs']]+['38:1','40:1','40:3','40:6','42:1']:subtype='ANSWER+AMR'
        if ref in ('27:1','29:1'):subtype='TAKE_MASHAL+AMR'
        if ref in ('11:4','2:10'):subtype='SIMPLE_AMR'
        if ref=='36:1':subtype='ADD_SPEECH+AMR'
        if ref in ('1:6','2:1'):subtype='WAYHI_POSITIVE'
        if ref=='31:40':subtype='תממ+דבר'
        if subtype:
            key='R4.1:MR1:SYNTHETIC:'+ref
            aa=[atoms[-1]] if ref=='31:40' else atoms
            family='MR1_EXPLICIT_CLOSURE' if ref=='31:40' else 'MR1_WAYHI_POSITIVE' if subtype=='WAYHI_POSITIVE' else 'MR1_CSF'
            add(key,'ACCEPTED_ANCHOR_OR_HUMAN_SCOPE',aa,dict(anchor_id=key,marker_family=family,marker_subtype=subtype,
                atom_ids=h.canonical(aa),ref_start='Job '+ref,ref_end='Job '+ref,surface_text='[SYNTHETIC FORMULA] '+subtype))
            deps.append(key)
        for j,a in enumerate(atoms):
            for level in range(7):
                payload=h.canonical(['SYNTHETIC',j,level]);digest=h.sha(payload.encode());key=f'PROV1:ATOM:{a}:G{level}'
                add(key,'ATOM_SIGNATURE_PROVENANCE',[a],dict(atom_node=str(a),level='G'+str(level),historical_hash=digest,reconstructed_hash=digest,
                    canonical_json_preimage=payload,hash_match='true',source='SYNTHETIC_NOT_REAL'))
                deps.append(key)
        formal='FORMAL:SYNTHETIC:'+ref
        fr=dict(source_event_id=formal,family_ids='["SYNTHETIC_F"]',family_signature_definitions='[{"family_id":"SYNTHETIC_F","level":"G0"}]',atom_ids=h.canonical(atoms))
        add(formal,'FORMAL_CONTEXT_NOT_BOUNDARY_OR_HIERARCHY',atoms,fr);deps.append(formal)
        add('HSA2:PANEL:'+ref,'NATIVE_REFERENCE_PANEL',atoms,dict(ref=ref,scope='SYNTHETIC_FULL_VERSE'),deps)
    cfg1=json.loads(h.h1.CONFIG.read_text(encoding='utf-8'));receipts=[]
    for role,pin in cfg1['archives'].items():
        pin.update(path='SYNTHETIC/'+role,sha256=h.sha(('SYNTHETIC:'+role).encode()))
        receipts.append(dict(role=role,path=pin['path'],sha256=pin['sha256'],expected=pin['sha256']))
    for r in rows:
        r['source_evidence_ids']=h.canonical(['HSA2:PANEL:'+r['reference_start']]);r['source_layers']='["SYNTHETIC_NOT_REAL"]'
    s=dict(mode='SYNTHETIC_AUDIT_ONLY',cfg2=cfg,cfg=cfg1,catalog=cat,receipts=receipts,prior=h.h1.registry(),
        native_order=native_order,atom_index={a:i for i,a in enumerate(native_order)},canonical_atom_index={a:i for i,a in enumerate(native_order)},native_refs=refs,
        frozen_receipts=[dict(path=p,actual=d,expected=d) for p,d in cfg['frozen_files'].items()])
    md='# SYNTHETIC HSA2 — not empirical evidence\n\nHuman decisions copied; source rows and IDs are fictional.\n\n'+h.registry_markdown(rows)+'\n'
    return deepcopy(s),rows,md
