"""Minimal synthetic registries; no real artifacts required by regression tests."""
from copy import deepcopy
import milal_jin_io as io
from milal_jin_relation_layers import TABLES


def fixture(cfg):
    cfg=deepcopy(cfg);cfg['registry_prefix']='registry/'
    cfg['sources']={k:'source/'+k for k in cfg['sources']}
    refs=['1:13','1:6','3:1','3:2','40:1','38:1','28:1','27:1','42:16','42:7','2:11','32:1']
    nodes=[dict(node_id='S:'+ref,node_kind='TEXTUAL_NODE',reference=ref,structural_function='NO_BOUNDARY' if ref in ('28:1','42:16') else 'SPEECH_UNIT_ONSET',original_record=dict(source_evidence_ids=[],coverage_start='',coverage_end=''),accepted_annotations=[]) for ref in refs]
    nodes += [dict(node_id=k,node_kind=k,reference='',structural_function='',original_record={},accepted_annotations=[]) for k in ['COMPOSITION_GROUP','TRANSITION_ANCHOR','ROLE_ALIAS','SOURCE_EVIDENCE_ANCHOR','TECHNICAL_ROOT']]
    edges=[]
    def edge(typ,a,b,layer='TEXTUAL_HIERARCHY'):
        rid='SYN:'+str(len(edges));r=dict(relation_id=rid,relation_type=typ,source_node=a,target_node=b,source_ref='',target_ref='',source_stage='SYNTHETIC',source_status='ACCEPTED_SOURCE',layer=layer,original_record=dict(source_judgment_ids=[],source_evidence_ids=[]));edges.append(r);return rid
    edge('CHILD_OF','S:1:13','S:1:6');control=edge('CHILD_OF','S:40:1','S:38:1')
    edge('HIERARCHICALLY_ABOVE','S:3:1','S:3:2')
    for a,b in [('3:2','3:1'),('28:1','27:1'),('42:16','42:7')]:edge('CONTINUES_WITHIN','S:'+a,'S:'+b)
    edge('SAME_LEVEL_SIBLING','S:1:6','S:38:1','TEXTUAL_SAME_LEVEL')
    edge('GROUP_MEMBER_OF','S:2:11','COMPOSITION_GROUP','COMPOSITION_GROUPING')
    edge('POST_CLOSURE_TRANSITION','S:32:1','TRANSITION_ANCHOR','TRANSITION')
    edge('CONTRASTIVE_ANA_FRAME','S:32:1','S:38:1','OVERLAY_RESPONSIO')
    edge('NO_DIRECT_RELATION','S:2:11','S:32:1','NEGATIVE_CONSTRAINT')
    edge('TECHNICAL_ROOT_LINK','S:2:11','TECHNICAL_ROOT','TECHNICAL_NAVIGATION')
    f={'registry/01_hsa3_canonical_nodes.csv':io.csv_bytes(nodes)}
    layers=['TEXTUAL_HIERARCHY','TEXTUAL_SAME_LEVEL','COMPOSITION_GROUPING','TRANSITION','OVERLAY_RESPONSIO','NEGATIVE_CONSTRAINT','TECHNICAL_NAVIGATION']
    for name,layer in zip(TABLES,layers):f['registry/'+name]=io.csv_bytes([r for r in edges if r['layer']==layer])
    for k,p in cfg['sources'].items():f[p]=io.csv_bytes([],['judgment_id'])
    f[cfg['sources']['01_jin_human_batch1_decisions.csv']]=io.csv_bytes([dict(historical_relation_ids=[control],control='POSITIVE_MACRO_HYPOTAXIS_CONTROL',verbatim_researcher_decision='SYNTHETIC macro support; no strict claim')])
    f[cfg['sources']['20_neutral_to_canonical_crosswalk.csv']]=io.csv_bytes([dict(node_id='S:40:1',original_jin_record=dict(clause_anchors=['BHSA2021:clause:1'],clause_atom_anchors=['BHSA2021:clause_atom:2']))])
    f['08_explicit_hypotaxis_controls.csv']=io.csv_bytes([dict(pair_id='SYN:STRICT',evidence=dict(clause_evidence=dict(evidence_flags=dict(S_EXPLICIT_SUBORDINATION_MARKER=True))),human_accepted=False,macro_evidence=False)])
    f['16_focused_postblind_comparison.csv']=io.csv_bytes([],['batch_case_id'])
    f['90_run_metadata.json']=io.js(dict(stage='SYNTHETIC_JIN05'))
    io.seal(f);return f,cfg
