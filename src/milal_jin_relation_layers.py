"""JIN.0.6: source-linked relation typing proposals; no graph migration."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import milal_jin_io as io
from milal_jin_postcontext_comparison import review_fields

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/r4_4_contract_jin_0_6_job.json'
PRIMARY = ('CHILD_OF', 'HIERARCHICALLY_ABOVE', 'CONTINUES_WITHIN')
TABLES = ('02_hsa3_textual_hierarchy_edges.csv', '03_hsa3_textual_same_level_edges.csv',
          '05_hsa3_composition_relations.csv', '06_hsa3_transition_relations.csv',
          '07_hsa3_overlay_relations.csv', '08_hsa3_negative_constraints.csv',
          '18_technical_navigation_relations.csv')
NODE_TYPES = dict(TEXTUAL_NODE='MACRO_TEXTUAL_UNIT', COMPOSITION_GROUP='COMPOSITION_GROUP',
                  SOURCE_EVIDENCE_ANCHOR='EVIDENCE_ANCHOR', TRANSITION_ANCHOR='TRANSITION_ANCHOR',
                  ROLE_ALIAS='ROLE_ALIAS', TECHNICAL_ROOT='TECHNICAL')
LAYERS = ('STRICT_CLAUSE_HIERARCHY', 'MACRO_TEXTUAL_HIERARCHY', 'TEXTUAL_PARATAXIS',
          'MACRO_PARATAXIS', 'COMPOSITION', 'TRANSITION', 'OVERLAY_RESPONSIO',
          'NEGATIVE_CONSTRAINT', 'TECHNICAL_NAVIGATION')
QUESTIONS = (
    ('Q-A', 'Reinterpret 1:13→1:6 historical CHILD_OF as macro textual hierarchy?'),
    ('Q-B', 'Reinterpret 3:1/3:2 as a macro speech frame, leaving strict dependency unresolved?'),
    ('Q-C', 'Confirm 40:1→38:1 at macro level only, leaving strict mother unproven?'),
    ('Q-D', 'Separate CONTINUES_WITHIN strict, macro and no-new-boundary semantics?'),
    ('Q-E', 'Add strict versus macro parataxis layers to SAME_LEVEL_SIBLING?'),
    ('Q-F', 'Require separate relation_type and relation_layer fields in the future contract?'))
METHOD = '''# Relation typing methodology

Strict clause hierarchy and macro textual hierarchy are related but non-identical analytical layers.

A clause_atom anchor identifies textual location; it does not by itself determine whether a relation is strict syntactic hierarchy or macro textual hierarchy.

Historical relation labels such as CHILD_OF, HIERARCHICALLY_ABOVE, CONTINUES_WITHIN, and SAME_LEVEL_SIBLING may require an explicit relation_layer field to avoid semantic overloading.

Jin’s single-mother principle applies to a relation adjudicated as strict hypotactic daughterhood; it must not be inferred merely from a macro containment judgment.

Macro textual hierarchy may use clause-level linguistic evidence, but macro projection requires separate human adjudication.

All classifications are AUDIT_PROPOSAL / UNREVIEWED. No historical row is rewritten.
The latest lossless layered registry is inventoried once, preserving both stored orientations.
Clause anchors are source-recorded evidence sets, never computed unit extents. Unknown extent
and missing endpoint identity remain UNRESOLVED; reference matching never supplies identity.
Single-clause flags describe the unit only if explicit unit evidence establishes it.
Strict positive controls are separate linguistic controls, not accepted human macro edges.
An accepted macro judgment with unproven strict dependency is a normal, representable state.
RL5 is non-parent placement; its count is reported separately, not hidden in strict counts.
Non-hierarchy controls use RL6 with an explicit non-parent layer rather than invented hierarchy.
An overloaded label is flagged for review when it lacks an explicit strict/macro field or has
multiple source-grounded placement semantics. This is potential semantic overloading, not proof
that a strict usage exists. Q1–Q9 remain UNAPPROVED; participant arc UNADJUDICATED.
No mother search for 2:11 or 32:1; NO_MACRO_MOTHER_FOUND is preserved. No R4.4 consumer.
'''


def config():
    return json.loads(CONFIG.read_bytes())


def linked(files, path):
    return [dict(record=r, member=path, data_row=i, member_sha256=io.sha(files[path]),
                 row_sha256=io.sha(io.js(r))) for i, r in enumerate(io.rows(files[path]), 1)]


def source_model(files, cfg):
    io.require(bool(files) and '90_run_metadata.json' in files and io.manifest_ok(files), 'upstream manifest')
    p = cfg['registry_prefix']
    ns = linked(files, p+'01_hsa3_canonical_nodes.csv')
    edges = [r for name in TABLES for r in linked(files, p+name)]
    for x in edges:
        r=x['record']
        io.require(all(r.get(k) for k in ('relation_id','relation_type','layer','source_stage','source_status')),
                   'required relation column is absent or blank')
    io.require(len({r['record']['relation_id'] for r in edges}) == len(edges), 'duplicate relation identity')
    io.require(len({r['record']['node_id'] for r in ns}) == len(ns), 'duplicate node identity')
    sources = cfg['sources']
    judgments = {}
    for name in ('01_structural_judgments.csv', '01_hsa2_structural_judgments.csv'):
        for r in linked(files, sources[name]):
            ident = r['record']['judgment_id']
            io.require(ident not in judgments, 'duplicate human judgment identity')
            judgments[ident] = r
    anchors = {r['record']['node_id']: r for r in linked(files, sources['20_neutral_to_canonical_crosswalk.csv'])}
    latest = {r['record']['historical_relation_id']: r for r in linked(files, sources['03_jin_human_batch1_historical_crosswalk.csv'])}
    batch = linked(files, sources['01_jin_human_batch1_decisions.csv'])
    contextual = {r['record']['human_relation_id']:r for r in linked(files,sources['15_postcontext_human_comparison.csv'])}
    pair_inventory = {r['record']['pair_id']:r for r in linked(files,sources['01_context_supported_pair_inventory.csv'])}
    return dict(nodes=ns, edges=edges, judgments=judgments, anchors=anchors, latest=latest, batch=batch,
                contextual=contextual,pair_inventory=pair_inventory,
                strict=linked(files, '08_explicit_hypotaxis_controls.csv'),
                focused=linked(files, '16_focused_postblind_comparison.csv'))


def node_rows(s):
    result = []
    for link in s['nodes']:
        n = link['record']; o = n['original_record']; a = s['anchors'].get(n['node_id'])
        anchor = a['record']['original_jin_record'] if a else {}
        spans = [x['original_record'] for x in n.get('accepted_annotations', [])
                 if x['original_record'].get('span_start') and x['original_record'].get('span_end')]
        span = spans[0] if len(spans) == 1 else {}
        result.append(dict(node_id=n['node_id'], proposed_node_layer=NODE_TYPES.get(n['node_kind'], 'UNRESOLVED'),
            reference=n['reference'], structural_function=n['structural_function'],
            clause_ids=anchor.get('clause_anchors', []), clause_atom_ids=anchor.get('clause_atom_anchors', []),
            anchor_provenance=a or 'UNRESOLVED',
            span_start=span.get('span_start', o.get('coverage_start') or 'UNRESOLVED'),
            span_end=span.get('span_end', o.get('coverage_end') or 'UNRESOLVED'),
            is_single_clause='UNRESOLVED', is_single_clause_atom='UNRESOLVED',
            is_multi_clause_unit=True if span and span['span_start'] != span['span_end'] else 'UNRESOLVED',
            extent_limit='Anchor evidence count does not establish unit extent.',
            source_link=link, proposal_status='UNREVIEWED'))
    return result


def source_ids(value, keys):
    """Collect explicitly named source fields, never infer IDs from text."""
    out=set()
    if isinstance(value,dict):
        for key,item in value.items():
            if key in keys:
                for ident in item if isinstance(item,list) else [item]:
                    if isinstance(ident,str) and ident:out.add(ident)
            if isinstance(item,(dict,list)):out.update(source_ids(item,keys))
    elif isinstance(value,list):
        for item in value:out.update(source_ids(item,keys))
    return sorted(out)


def classify(r):
    """Typing of attested registry semantics, never new linguistic detection."""
    typ, layer = r['relation_type'], r['historical_layer']
    strict = r['strict_evidence_status'] == 'INDEPENDENT_LOCAL_DEPENDENCY'
    macro = r['macro_evidence_status'] != 'UNRESOLVED'
    if layer in ('COMPOSITION_GROUPING', 'TRANSITION', 'OVERLAY_RESPONSIO', 'NEGATIVE_CONSTRAINT', 'TECHNICAL_NAVIGATION'):
        return 'RL6_RELATION_LAYER_UNRESOLVED', {'COMPOSITION_GROUPING': 'COMPOSITION'}.get(layer, layer), 'NON_PARENT_CONTROL'
    if typ == 'CONTINUES_WITHIN':
        semantics = 'NO_NEW_BOUNDARY' if r['source_structural_function'] == 'NO_BOUNDARY' else 'MACRO_TEXTUAL_CONTINUATION'
        return 'RL5_NON_PARENT_HIERARCHICAL_PLACEMENT', 'MACRO_TEXTUAL_HIERARCHY', semantics
    if typ in ('SAME_LEVEL_SIBLING', 'PARALLEL_ENDING'):
        return ('RL3_STRICT_AND_MACRO_SUPPORTED' if strict and macro else
                'RL2_MACRO_TEXTUAL_HIERARCHY' if macro else 'RL6_RELATION_LAYER_UNRESOLVED'), 'MACRO_PARATAXIS' if macro else 'UNRESOLVED', 'PARATAXIS_NOT_MOTHERLESS_ERROR'
    if typ in PRIMARY:
        if strict and macro: return 'RL3_STRICT_AND_MACRO_SUPPORTED', 'UNRESOLVED', 'INDEPENDENT_BOTH_REQUIRES_HUMAN_REVIEW'
        if strict: return 'RL1_STRICT_CLAUSE_HIERARCHY', 'STRICT_CLAUSE_HIERARCHY', 'LOCAL_DEPENDENCY'
        if macro: return 'RL2_MACRO_TEXTUAL_HIERARCHY', 'MACRO_TEXTUAL_HIERARCHY', 'MACRO_SUPPORT_DOES_NOT_PROVE_STRICT_MOTHER'
    return 'RL6_RELATION_LAYER_UNRESOLVED', 'UNRESOLVED', 'NON_PARENT_CLOSURE_OR_UNRESOLVED'


def inventory(s, nodes):
    nm = {n['node_id']: n for n in nodes}; result = []
    for link in s['edges']:
        e = link['record']; o = e['original_record']; rid = e['relation_id']
        human_ids = source_ids(o, {'source_judgment_ids','judgment_id','action_id'})
        rationale = [s['judgments'][i] for i in human_ids if i in s['judgments']]
        decisions = [b for b in s['batch'] if rid in b['record']['historical_relation_ids']]
        latest = s['latest'].get(rid)
        contextual=s['contextual'].get(rid)
        pair_ids=contextual['record']['exact_pair_ids'] if contextual else []
        pairs=[s['pair_inventory'][ident] for ident in pair_ids if ident in s['pair_inventory']]
        r = dict(relation_id=rid, source_id=e['source_node'] or 'UNRESOLVED', target_id=e['target_node'] or 'UNRESOLVED',
            relation_type=e['relation_type'], relation_direction='STORED_SOURCE_TO_TARGET', source_stage=e['source_stage'],
            human_source_id=human_ids, historical_layer=e['layer'], historical_status=e['source_status'],
            latest_review_status=latest['record']['active_review_status'] if latest else 'NO_LATER_EXACT_ID_REVIEW',
            original_rationale=rationale or [dict(record=o, source_link=link)], evidence_ids=source_ids(o,{'source_evidence_ids','evidence_ids'}),
            historical_source=link, latest_review_source=latest or {}, batch_decisions=decisions,
            prior_context_audit=contextual or {}, exact_linguistic_pair_evidence=pairs,
            linguistic_evidence_scope='Candidate clause pairs are not identity-equivalent to the macro edge.',
            explicit_subordination_evidence=[], syntactic_dependency_evidence=[], reference_dependency_evidence=[],
            strict_evidence_status='UNPROVEN_FOR_THIS_MACRO_EDGE',
            macro_evidence_status='UNRESOLVED', multi_clause_configuration_evidence=[],
            macro_distribution_evidence=decisions, speech_frame_evidence=[], onset_closure_evidence=[],
            new_relation=False, new_parent_edge=False, new_human_judgment=False, migrated=False)
        for side in ('source', 'target'):
            n = nm.get(e[side+'_node'], {})
            r[side+'_ref'] = e[side+'_ref'] or n.get('reference') or 'UNRESOLVED'
            r[side+'_node_layer'] = n.get('proposed_node_layer', 'UNRESOLVED')
            r[side+'_clause_id'] = n.get('clause_ids', []) or 'UNRESOLVED'
            r[side+'_clause_atom_ids'] = n.get('clause_atom_ids', [])
            for k in ('span_start', 'span_end', 'is_single_clause', 'is_single_clause_atom', 'is_multi_clause_unit', 'structural_function'):
                r[side+'_'+k] = n.get(k, 'UNRESOLVED')
        if e['layer'] in ('TEXTUAL_HIERARCHY', 'TEXTUAL_SAME_LEVEL') and (
                rationale or decisions or any(r[k+'_node_layer'] == 'MACRO_TEXTUAL_UNIT' for k in ('source', 'target'))):
            r['macro_evidence_status'] = 'HISTORICAL_TEXTUAL_JUDGMENT_NOT_NEW_ACCEPTANCE'
        r['speech_frame_evidence'] = [x for x in rationale if 'SPEECH' in x['record'].get('structural_function', '')]
        r['onset_closure_evidence'] = [x for x in rationale if any(t in x['record'].get('structural_function', '') for t in ('ONSET', 'CLOSURE', 'NO_BOUNDARY'))]
        r['multi_clause_configuration_evidence'] = [x for x in s['focused'] if
            rid in x['record']['historical_record'].get('canonical_relation_ids', [])]
        # Preserve existing hypotheses as evidence without converting local support into
        # a strict typing decision about a differently scoped historical macro edge.
        for x in pairs:
            h=x['record'].get('source_hypothesis',{})
            flags=x['record'].get('source_pair',{}).get('evidence_flags',{})
            if flags.get('S_EXPLICIT_SUBORDINATION_MARKER'):r['explicit_subordination_evidence'].append(x)
            if h.get('hypotaxis_supported') or 'HYPOTAXIS' in h.get('relation_hypothesis',''):
                r['syntactic_dependency_evidence'].append(x)
            if flags.get('S_ANAPHORIC_DEPENDENCY'):r['reference_dependency_evidence'].append(x)
        proposal, layer, semantics = classify(r)
        r.update(proposal_category=proposal, proposed_relation_layer=layer, proposed_semantics=semantics,
                 proposal_kind='AUDIT_PROPOSAL', proposal_status='UNREVIEWED',
                 historical_strict_claim='NOT_EXPLICITLY_TYPED_IN_SOURCE',
                 label_overloading_review_required=e['relation_type'] in (*PRIMARY, 'SAME_LEVEL_SIBLING'))
        result.append(r)
    return result


def reviews():
    return [dict(case_id=k, question=q, **{f: 'UNREVIEWED' if f == 'review_status' else '' for f in review_fields()}) for k, q in QUESTIONS]


def summaries(inv):
    out = []
    for typ in sorted({r['relation_type'] for r in inv}):
        rr = [r for r in inv if r['relation_type'] == typ]; c = Counter(r['proposal_category'][:3] for r in rr)
        out.append(dict(relation_type=typ, number_of_occurrences=len(rr), strict_count=c['RL1'], macro_count=c['RL2'],
            mixed_count=c['RL3']+c['RL4'], unresolved_count=c['RL6'], non_parent_placement_count=c['RL5'],
            proposed_layers=sorted({r['proposed_relation_layer'] for r in rr}),
            source_semantics=sorted({r['proposed_semantics'] for r in rr}),
            potential_overloading=any(r['label_overloading_review_required'] for r in rr)))
    return out


def build(files, cfg):
    s = source_model(files, cfg); nodes = node_rows(s); inv = inventory(s, nodes)
    strict = [dict(control_id=r['record']['pair_id'], control_label='STRICT_HYPOTAXIS_POSITIVE_CONTROL',
        proposed_relation_layer='STRICT_CLAUSE_HIERARCHY', proposal_status='UNREVIEWED',
        human_accepted=False, macro_evidence=False, source_link=r) for r in s['strict']]
    return dict(nodes=nodes, inventory=inv, strict=strict, reviews=reviews(), summary=summaries(inv),
        new_relations=[], new_parents=[], human_judgments=[], migrations=[],
        q1_q9={f'Q{i}': 'UNAPPROVED' for i in range(1,10)}, participant_arc='UNADJUDICATED',
        mother_search_results={ref:'NO_MACRO_MOTHER_FOUND' for ref in ('2:11','32:1')})


def gates(m, expected):
    inv=m['inventory']; exp=expected['inventory']
    checks={}
    def eq(name, predicate):
        checks[name]=[r for r in inv if predicate(r)] == [r for r in exp if predicate(r)] and any(predicate(r) for r in exp)
    checks['HIERARCHY_RELATIONS_INVENTORIED'] = [(r['relation_id'],r['historical_source']) for r in inv] == [(r['relation_id'],r['historical_source']) for r in exp]
    checks['RELATION_LAYER_AUDIT_COMPLETE'] = inv == exp and bool(inv)
    checks['NODE_LAYER_CROSSWALK_COMPLETE'] = m['nodes'] == expected['nodes'] and bool(m['nodes'])
    for typ in (*PRIMARY,'SAME_LEVEL_SIBLING'):
        eq(typ+'_LAYER_AUDITED',lambda r,t=typ:r['relation_type']==t)
    checks['STRICT_CONTROL_PRESENT'] = m['strict']==expected['strict'] and bool(m['strict']) and all(
        r['source_link']['record']['evidence']['clause_evidence']['evidence_flags']['S_EXPLICIT_SUBORDINATION_MARKER'] and
        not r['human_accepted'] and not r['macro_evidence'] for r in m['strict'])
    eq('MACRO_CONTROL_PRESENT',lambda r:any(b['record']['control']=='POSITIVE_MACRO_HYPOTAXIS_CONTROL' for b in r['batch_decisions']))
    checks['CLAUSE_ATOM_ANCHOR_NOT_EQUAL_STRICT_HIERARCHY'] = m['nodes']==expected['nodes'] and all(
        n['proposed_node_layer']!='STRICT_CLAUSE_NODE' for n in m['nodes'] if n['source_link']['record']['node_kind']!='STRICT_CLAUSE_NODE')
    for ref,tag in [('1:13','JOB_1_13'),('3:1','JOB_3_1_2'),('40:1','JOB_40_1'),('28:1','JOB_28_1'),('42:16','JOB_42_16')]:
        eq(tag+'_LAYER_DISTINCTION_PRESENT',lambda r,ref=ref:r['source_ref']==ref and r['relation_type'] in PRIMARY)
    for ref,tag in [('2:11','JOB_2_11'),('32:1','JOB_32_1')]:
        checks[tag+'_NO_MOTHER_CREATED'] = m['mother_search_results'].get(ref)=='NO_MACRO_MOTHER_FOUND' and not m['new_parents'] and all(not r['new_parent_edge'] for r in inv if ref in (r['source_ref'],r['target_ref']))
    for layer,tag in [('COMPOSITION_GROUPING','COMPOSITION'),('TRANSITION','TRANSITION'),('OVERLAY_RESPONSIO','OVERLAY')]:
        eq(tag+'_NOT_STRICT_HIERARCHY',lambda r,layer=layer:r['historical_layer']==layer)
    checks['NO_HISTORICAL_REWRITE']=all(r['historical_source']==e['historical_source'] for r,e in zip(inv,exp)) and len(inv)==len(exp)
    for name,key,flag in [('NO_RELATION_MIGRATION','migrations','migrated'),('NO_NEW_RELATION','new_relations','new_relation'),('NO_NEW_PARENT','new_parents','new_parent_edge'),('NO_NEW_HUMAN_JUDGMENT','human_judgments','new_human_judgment')]:
        checks[name] = not m[key] and all(not r[flag] for r in inv)
    checks['Q1_Q9_UNAPPROVED']=m['q1_q9']==expected['q1_q9']
    checks['QA_QF_UNREVIEWED']=m['reviews']==reviews()
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED'
    checks['OVERLOADING_SUMMARY_RECONCILES']=m['summary']==summaries(inv)
    return checks


def render(m):
    inv=m['inventory']; out={}
    def csv(name,rr): out[name]=io.csv_bytes(rr)
    csv('01_hierarchy_relation_inventory.csv',inv)
    csv('02_relation_node_layer_crosswalk.csv',m['nodes'])
    columns=('relation_id','relation_type','source_ref','target_ref','strict_evidence_status','macro_evidence_status','proposal_category','proposed_relation_layer','proposed_semantics','proposal_kind','proposal_status')
    csv('03_relation_layer_classification_proposals.csv',[{k:r[k] for k in columns} for r in inv])
    for name,typ in [('04_child_of_semantics_audit.csv','CHILD_OF'),('05_hierarchically_above_semantics_audit.csv','HIERARCHICALLY_ABOVE'),('06_continues_within_semantics_audit.csv','CONTINUES_WITHIN'),('07_same_level_semantics_audit.csv','SAME_LEVEL_SIBLING')]:csv(name,[r for r in inv if r['relation_type']==typ])
    csv('08_relation_label_overloading_summary.csv',m['summary']);csv('09_strict_clause_positive_controls.csv',m['strict'])
    csv('10_macro_hierarchy_controls.csv',[r for r in inv if r['batch_decisions']])
    reports=[]
    for name,refs in [('11_key_case_1_13.md',('1:13',)),('12_key_case_3_1_2.md',('3:1','3:2')),('13_key_case_40_1.md',('40:1',))]:
        rr=[r for r in inv if r['source_ref'] in refs and r['relation_type'] in PRIMARY]
        text='# '+ ' / '.join(refs)+' — UNREVIEWED layer proposal\n\n'
        for r in rr:
            text+=f"## {r['relation_id']}\n\n{r['source_ref']} {r['relation_type']} {r['target_ref']}\n\nStrict: {r['strict_evidence_status']}. Macro: {r['macro_evidence_status']}.\n\nProposal: {r['proposal_category']} / {r['proposed_relation_layer']}. Latest: {r['latest_review_status']}.\n\n"
            for x in r['original_rationale']:
                o=x['record']; text+=str(o.get('linguistic_basis',o.get('semantic_meaning','')))+'\n\n'+str(o.get('methodological_note',''))+'\n\n'
            for b in r['batch_decisions']:text+=b['record']['verbatim_researcher_decision']+'\n\n'
            text+='Exact source rows, full evidence IDs and focused comparisons are retained in inventory 01. No strict mother restored or selected.\n\n'
        if '3_1' in name:text+='JIN.0.5: raw N→Q boundary is 3:2→3:3, not automatically 3:1→3:2. Speech framing does not resolve strict motherhood.\n'
        out[name]=text.encode();reports.append(text)
    contract=[]
    for typ in sorted({r['relation_type'] for r in inv}):
        rr=[r for r in inv if r['relation_type']==typ]
        future={'CHILD_OF':'MACRO_WITHIN','HIERARCHICALLY_ABOVE':'MACRO_CONTAINS','SAME_LEVEL_SIBLING':'MACRO_PARALLEL'}.get(typ,typ)
        contract.append(dict(relation_type=typ,proposed_relation_layers=sorted({r['proposed_relation_layer'] for r in rr}),
            recommendation='NEW_TYPED_RELATION_NEEDED' if typ=='CONTINUES_WITHIN' else 'REUSE_EXISTING_TYPE_WITH_LAYER_FIELD',
            proposed_future_type=future, strict_names_for_review=['STRICT_MOTHER_OF','STRICT_DAUGHTER_OF'] if typ in PRIMARY else [],
            proposal_status='UNREVIEWED',migrate=False))
    csv('14_relation_contract_split_proposal.csv',contract)
    cm={r['relation_type']:r for r in contract}
    csv('15_historical_to_future_relation_crosswalk.csv',[dict(historical_relation_id=r['relation_id'],historical_type=r['relation_type'],proposed_relation_layer=r['proposed_relation_layer'],proposed_future_type=cm[r['relation_type']]['proposed_future_type'],review_status='UNREVIEWED',migrated=False) for r in inv])
    csv('16_human_review_cases.csv',m['reviews'])
    packet='# JIN.0.6 relation-layer review — all proposals UNREVIEWED\n\n'
    packet+='Primary hierarchy-like rows: '+str(sum(r['relation_type'] in PRIMARY for r in inv))+'. Complete registry rows (including controls): '+str(len(inv))+'.\n\n'
    packet+='| Type | Total | Strict | Macro | Mixed | Unresolved | Non-parent placement |\n|---|---:|---:|---:|---:|---:|---:|\n'
    for r in m['summary']:packet+='| '+' | '.join(str(r[k]) for k in ('relation_type','number_of_occurrences','strict_count','macro_count','mixed_count','unresolved_count','non_parent_placement_count'))+' |\n'
    packet+='\n'+'\n\n'.join(k+': '+q+' **UNREVIEWED**' for k,q in QUESTIONS)+'\n\n'
    packet+='## CONTINUES_WITHIN comparison\n\n'
    for r in inv:
        if r['relation_type']=='CONTINUES_WITHIN':packet+=f"- {r['relation_id']}: {r['source_ref']} → {r['target_ref']}: {r['proposed_semantics']}; strict UNPROVEN.\n"
    packet+='\n## SAME_LEVEL fixtures\n\nAll stored orientations remain in 07; no motherless error or new mother.\n\n'
    for r in inv:
        if r['relation_type']=='SAME_LEVEL_SIBLING':packet+=f"- {r['relation_id']}: {r['source_ref']} → {r['target_ref']} — {r['proposed_relation_layer']}, UNREVIEWED.\n"
    packet+='\n'+'\n\n'.join(reports)+'\n\n2:11 and 32:1: NO_MACRO_MOTHER_FOUND preserved; no search. Strict controls in 09 are not human macro acceptance.\n'
    out['17_human_review_packet.md']=packet.encode();out['18_methodological_addendum.md']=METHOD.encode()
    out['19_next_scope.md']=('# Next: Q-A–Q-F human adjudication\n\nNo migration, parent selection or R4.4 consumer authorized by this audit.\n\n'+'\n\n'.join(k+': '+q for k,q in QUESTIONS)+'\n').encode()
    out['21_proposed_relation_layer_vocabulary.json']=io.js(LAYERS)
    return out


def execute(out, self_test=False):
    cfg=config()
    if self_test:
        from milal_jin_relation_layers_fixture import fixture
        files,cfg=fixture(cfg)
        archive_hash=io.sha(io.js({k:io.sha(v) for k,v in files.items()}))
    else:
        data=(ROOT/cfg['archive']['path']).read_bytes();archive_hash=io.sha(data)
        io.require(archive_hash==cfg['archive']['sha256'],'exact JIN.0.5 ZIP hash')
        files=io.archive(data)
    pins={k:io.sha((ROOT/k).read_bytes()) for k in cfg['frozen_files']}
    baseline=subprocess.check_output(['git','rev-parse',cfg['baseline']],cwd=ROOT,text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],'HEAD'],cwd=ROOT,check=True)
    request=(ROOT/cfg['source_request']['path']).read_bytes()
    checks=preflight_gates(baseline,pins,files,request,
        list((ROOT/'src').glob('*r4_4*.py'))+list((ROOT/'scripts').glob('*r4_4*')),cfg)
    m=build(files,cfg);checks.update(gates(m,build(files,cfg)))
    io.require(all(checks.values()),'failed gates '+str([k for k,v in checks.items() if not v]))
    result=render(m); result.update({'history/jin_0_5/'+k:v for k,v in files.items()})
    result['22_researcher_source.txt']=request
    result['90_run_metadata.json']=io.js(dict(stage=cfg['stage'],mode='SYNTHETIC' if self_test else 'REAL_FROZEN_SOURCE_AUDIT',
        status='PASS',readiness='READY_FOR_RELATION_LAYER_HUMAN_REVIEW',baseline=baseline,archive_sha256=archive_hash,
        frozen_pins=pins,summary=m['summary'],new_relations=m['new_relations'],new_parent_edges=m['new_parents'],
        new_human_judgments=m['human_judgments'],migrations=m['migrations'],q1_q9=m['q1_q9'],participant_arc=m['participant_arc'],
        mother_search_results=m['mother_search_results'],code_sha256=io.sha(Path(__file__).read_bytes()),
        external_release_gates=['DETERMINISTIC_RERUN','REGRESSION_PASS']))
    io.seal(result);checks['MANIFEST_VALID']=io.manifest_ok(result)
    result['20_gates.csv']=io.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]);io.seal(result)
    zp=io.publish(result,Path(out));print(json.dumps(dict(zip=str(zp),sha256=io.sha(zp.read_bytes()),gates=len(checks),summary=m['summary']),ensure_ascii=False))
    return result


def preflight_gates(baseline,pins,files,request,consumer_files,cfg):
    return dict(BASELINE_COMMIT_VERIFIED=baseline==cfg['baseline'],
        JIN_0_5_FROZEN_PRESERVED=pins==cfg['frozen_files'] and io.manifest_ok(files),
        EXACT_REQUEST_PRESERVED=io.sha(request)==cfg['source_request']['sha256'],
        R4_4_CONSUMER_ABSENT=not consumer_files)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--self-test',action='store_true');a=p.parse_args();execute(a.out,a.self_test)
