"""Synthetic linkage mechanics only; human decisions come from the authored registry."""
from copy import deepcopy
import json

import milal_hsa1_registry as h


def source():
    rows = h.registry()
    cfg = json.loads(h.CONFIG.read_text(encoding='utf-8'))
    cfg['explicit_entry_event_id'] = 'SYNTHETIC:OVERT:1:14'
    catalog = {}
    for i, row in enumerate(rows, 1):
        ref = row['reference_start']
        key = 'SYNTHETIC:CONTROL:' + ref
        native = 'SYNTHETIC:NATIVE:' + ref
        def entry(key, kind, data, deps):
            return dict(evidence_id=key, source_layer='SYNTHETIC', evidence_kind=kind,
                atom_ids=[-i], source_locator={'fixture_id':key,'row_sha256':h.sha(h.canonical(data).encode())},
                source_row=data, dependencies=deps)
        catalog[native] = entry(native, 'NATIVE_CLAUSE_SNAPSHOT_NOT_A_BOUNDARY',
            {'fixture':'SYNTHETIC_NOT_BHSA','reference':ref}, [])
        catalog[key] = entry(key, 'EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION',
            {'ref':ref,'MR1_EXPLICIT_CLOSURE':'False','fixture':'SYNTHETIC_NOT_ACCEPTED_REAL'}, [native])
        if ref=='32:2':
            for extra_ref in ('32:3','32:4','32:5'):
                extra_key='SYNTHETIC:CONTROL:'+extra_ref
                catalog[extra_key]=entry(extra_key,'EXACT_REFERENCE_PANEL_NOT_HUMAN_CONCLUSION',
                    {'ref':extra_ref,'MR1_EXPLICIT_CLOSURE':'False','fixture':'SYNTHETIC'},[])
                catalog[key]['dependencies'].append(extra_key)
        if ref in ('1:16','1:17','1:18'):
            event = 'SYNTHETIC:ANONYMOUS:' + ref
            catalog[event] = entry(event, 'SOURCE_PHRASE_CANDIDATE_NOT_ENTITY_RESOLUTION',
                dict(anonymous_entry='True',identity_status='UNRESOLVED',participant_identity='UNRESOLVED',
                     first_appearance_in_book_if_exact='UNRESOLVED',named_role='',fixture='SYNTHETIC'), [])
            catalog[key]['dependencies'].append(event)
        if ref == '1:14':
            event=cfg['explicit_entry_event_id']
            catalog[event]=entry(event,'SOURCE_PHRASE_CANDIDATE_NOT_ENTITY_RESOLUTION',
                dict(participant_event_id=event,identity_status='EXPLICIT',anonymous_entry='False'),[])
            catalog[key]['dependencies'].append(event)
        if ref == '42:7':
            for suffix, data in [('wayhi',{'marker_family':'MR1_WAYHI_POSITIVE'}),
                                 ('csf',{'marker_family':'MR1_CSF','marker_subtype':'SIMPLE_AMR'}),
                                 ('hr1',{'human_case':'CASE030'})]:
                anchor='SYNTHETIC:ANCHOR:'+suffix
                catalog[anchor]=entry(anchor,'ACCEPTED_ANCHOR_OR_HUMAN_SCOPE',data,[])
                catalog[key]['dependencies'].append(anchor)
        if ref in ('31:40','32:1'):
            for kind, data in [('MR1_EXPLICIT_CLOSURE',{'fixture':'closure'}),
                               ('PRIOR_HUMAN_REVIEW_NOT_COMPUTATIONAL_JUDGMENT',{'case_id':'CASE025' if ref=='31:40' else 'CASE026'})]:
                dep='SYNTHETIC:'+kind+':'+ref
                catalog[dep]=entry(dep,kind,data,[]);catalog[key]['dependencies'].append(dep)
        row['source_evidence_ids'] = h.canonical([key])
        row['source_layers'] = h.canonical(['SYNTHETIC_LINKAGE_TEST_NOT_REAL_SOURCE'])
    receipts=[]
    for role, pin in cfg['archives'].items():
        pin.update(path='SYNTHETIC/'+role,sha256=h.sha(('SYNTHETIC:'+role).encode()))
        receipts.append(dict(role=role,path=pin['path'],sha256=pin['sha256'],expected=pin['sha256']))
    md = '# SYNTHETIC HSA1 linkage self-test — NOT empirical validation\n\n'
    md += 'Human decisions copied from the registry; all source pointers below are fictional test data.\n\n'
    md += h.markdown_table(rows) + '\n\n' + '\n'.join(cfg['principles']) + '\n'
    return dict(mode='SYNTHETIC_LINKAGE_ONLY',cfg=deepcopy(cfg),catalog=catalog,receipts=receipts), rows, md
