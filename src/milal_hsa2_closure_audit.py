"""Append-only human adjudication and evidence audit; closure targets are never chosen."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import sys
import zipfile

import milal_hsa1_registry as h1

ROOT=h1.ROOT
CONFIG=ROOT/'config/hsa2_job.json'
CSV=ROOT/'docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2.csv'
MD=ROOT/'docs/HUMAN_STRUCTURAL_ADJUDICATION_HSA2.md'
FIELDS=h1.FIELDS+['human_speaker','human_group','higher_order_function','direct_closure_target','higher_order_terminal_effect']
sha,canonical,require=h1.sha,h1.canonical,h1.require


def registry_bytes(rows):
    return h1.util.csv_bytes(rows,FIELDS).replace(b'\r\n',b'\n')


def registry():
    rows=h1.read_csv(CSV.read_bytes())
    require(rows and all(set(r)==set(FIELDS) for r in rows),'HSA2 registry schema')
    return rows


def registry_markdown(rows):
    lines=[]
    for r in rows:
        lines += [f'### {r["judgment_id"]} — Job {r["reference_start"]} ({r["judgment_type"]})','',
                  '| Field | Human-authored value |','| --- | --- |']
        lines += ['| '+k+' | '+str(r[k]).replace('|','&#124;').replace('\n','<br>')+' |' for k in FIELDS]
        lines += ['']
    return '\n'.join(lines)


def frozen_receipts(cfg):
    return [dict(path=p,expected=digest,actual=sha((ROOT/p).read_bytes())) for p,digest in cfg['frozen_files'].items()]


def native_geometry(native,signature_rows):
    """Clause membership may be discontinuous; only explicit PROV1 native indexes order atoms."""
    atoms=[a for v in native for a in v['atom_ids']]
    require(len(atoms)==len(set(atoms)),'duplicate native atom membership')
    positions={}
    for row in signature_rows:
        atom=int(row['atom_node']);old=json.loads(row['source'])['source_row']
        require(int(old['atom_node'])==atom,'signature/native atom mismatch')
        index=int(old['atom_index_1based'])-1
        require(atom not in positions or positions[atom]==index,'conflicting native index')
        positions[atom]=index
    require(set(positions)==set(atoms) and set(positions.values())==set(range(len(atoms))),'native index inventory mismatch')
    return sorted(atoms,key=positions.__getitem__),positions


def load():
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    receipts=frozen_receipts(cfg)
    require(all(r['actual']==r['expected'] for r in receipts),'HSA1/frozen core changed')
    s=h1.load_sources()  # Read-only accepted archive adapter; HSA1 core is frozen.
    s.update(cfg2=cfg,frozen_receipts=receipts,prior=h1.registry())
    cat=s['catalog']
    native=[v for k,v in cat.items() if k.startswith('BHSA2021:clause:')]
    pin=s['cfg']['archives']['prov1']
    archive=h1.src.archive((ROOT/pin['path']).read_bytes(),pin['sha256'])
    name='01_atom_signature_provenance.csv';signature_rows=h1.src.table(archive,name)
    s['native_order'],s['atom_index']=native_geometry(native,signature_rows)
    s['canonical_atom_index']=deepcopy(s['atom_index'])
    atom_refs={a:v['source_row']['ref'].removeprefix('Job ') for v in native for a in v['atom_ids']}
    s['native_refs']=list(dict.fromkeys(atom_refs[a] for a in s['native_order']))
    for key,v in cat.items():
        if key.startswith('FORMAL:'):
            indexes=[s['atom_index'][a] for a in v['atom_ids']];r=v['source_row']
            require(min(indexes)==int(r['first_index']) and max(indexes)==int(r['last_index']),'formal native span mismatch')
    refs=set(cfg['review_references']+cfg['comparison_controls'])
    for ref in cfg['focus']:
        i=s['native_refs'].index(ref)
        refs.update(s['native_refs'][max(0,i-1):i+2])
    # Explicit native coordinates select panels, never participant/object identity.
    for ref in sorted(refs,key=lambda x:tuple(map(int,x.split(':')))):
        nn=[v for v in native if v['source_row']['ref']=='Job '+ref]
        require(nn,'missing exact native reference '+ref)
        atoms=sorted([a for v in nn for a in v['atom_ids']],key=s['atom_index'].__getitem__)
        deps=[v['evidence_id'] for v in nn]
        deps += [k for k,v in cat.items() if k.startswith(('R4.1:','R4.2:P:','FORMAL:')) and set(v['atom_ids'])&set(atoms)]
        key='HSA2:PANEL:'+ref
        cat[key]=dict(evidence_id=key,source_layer='HSA2_EXACT_NATIVE_JOIN',evidence_kind='NATIVE_REFERENCE_PANEL',
            atom_ids=atoms,source_locator={'native_clause_ids':[v['source_row']['clause'] for v in nn]},
            source_row={'ref':ref,'scope':'FULL_VERSE_CONTEXT_NOT_CLOSURE_TARGET'},dependencies=deps)
    needed={a for ref in refs for a in cat['HSA2:PANEL:'+ref]['atom_ids']}
    for i,row in enumerate(signature_rows,1):
        atom=int(row['atom_node'])
        if atom not in needed:continue
        require(row['hash_match']=='true' and row['historical_hash']==row['reconstructed_hash']==sha(row['canonical_json_preimage'].encode()),'PROV1 signature mismatch')
        key=f'PROV1:ATOM:{atom}:{row["level"]}'
        require(key not in cat,'duplicate atom signature')
        cat[key]=dict(evidence_id=key,source_layer='prov1',evidence_kind='ATOM_SIGNATURE_PROVENANCE',atom_ids=[atom],
            source_locator=h1.src.locator('prov1',archive,name,i,row),source_row=row,dependencies=[])
    for ref in refs:
        panel=cat['HSA2:PANEL:'+ref]
        for atom in panel['atom_ids']:
            for level in range(7):
                key=f'PROV1:ATOM:{atom}:G{level}'
                require(key in cat,'missing exact atom signature')
                panel['dependencies'].append(key)
    return s


def candidate_model_valid(rows):
    """Independent review dimensions allow local closure AND enclosing termination."""
    options={'DIRECT_CLOSURE_TARGET':{'DIRECT_LOCAL_CLOSURE','NO_DIRECT_RELATION','UNRESOLVED'},
             'HIGHER_ORDER_TERMINAL_EFFECT':{'TERMINATES_ENCLOSING_GROUP','NO_DIRECT_RELATION','UNRESOLVED'}}
    return bool(rows) and all(r['dimension'] in options and set(r['review_options'])==options[r['dimension']]
        and r['selected_relation'] in options[r['dimension']] for r in rows)


def candidates(cfg):
    result=[]
    for i,target in enumerate(cfg['closure_review_candidates'],1):
        dimension=target['dimension']
        result.append(dict(candidate_id=f'CT{i:02}',ending_reference='31:40',
            candidate_target_reference=target['reference'],target_scope=target['scope'],dimension=dimension,
            review_options=['DIRECT_LOCAL_CLOSURE','NO_DIRECT_RELATION','UNRESOLVED'] if dimension=='DIRECT_CLOSURE_TARGET' else ['TERMINATES_ENCLOSING_GROUP','NO_DIRECT_RELATION','UNRESOLVED'],
            selected_relation='UNRESOLVED',direct_closure_target='UNRESOLVED',higher_order_terminal_effect='UNRESOLVED',
            review_status='UNREVIEWED',authority='RESEARCHER_SUPPLIED_REVIEW_QUESTION_NOT_HIERARCHY_EDGE'))
    return result


def edge_labels(lo,hi,start,end):
    labels=[]
    if lo==start:labels.append('STARTS_AT_MARKER_START')
    if hi==end:labels.append('ENDS_AT_MARKER_END')
    if lo<start<=hi:labels.append('CROSSES_START_EDGE')
    if lo<=end<hi:labels.append('CROSSES_END_EDGE')
    if start<=lo and hi<=end:labels.append('WITHIN_MARKER_SPAN')
    return labels


def evidence(s):
    cat=s['catalog'];cfg=s['cfg2'];idx=s['atom_index']
    scopes=[];edges=[];lexical=[]
    for ref in cfg['focus']+cfg['comparison_controls']:
        panel=cat['HSA2:PANEL:'+ref]
        aa=[cat[k] for k in panel['dependencies'] if k.startswith('R4.1:MR1:')]
        # All co-located marker identities are distinct. No closest-opening selection.
        selected=aa+([panel] if ref in cfg['comparison_controls'] or not aa else [])
        for entry in selected:
            atoms=entry['atom_ids'];lo,hi=min(idx[a] for a in atoms),max(idx[a] for a in atoms)
            scope=dict(reference=ref,evidence_id=entry['evidence_id'],atom_ids=atoms,start_index=lo,end_index=hi,
                scope_type='EXACT_MR1_EVENT' if entry['evidence_id'].startswith('R4.1:MR1:') else 'FULL_VERSE_HUMAN_COMPARISON_NOT_MR1',
                source_row=entry['source_row'],source_locator=entry['source_locator'])
            scopes.append(scope)
            for key,v in cat.items():
                if not key.startswith('FORMAL:'):continue
                fi=[idx[a] for a in v['atom_ids']];labels=edge_labels(min(fi),max(fi),lo,hi)
                if labels:
                    edges.append(dict(reference=ref,scope_id=entry['evidence_id'],formal_id=key,
                        formal_atom_ids=v['atom_ids'],relations=labels,formal_source_row=v['source_row'],
                        source_locator=v['source_locator'],upstream_locators=v.get('upstream_locators',[])))
            if ref in cfg['focus']:
                words=[]
                for k in panel['dependencies']:
                    if not k.startswith('BHSA2021:clause:'):continue
                    native=cat[k]['source_row']
                    exact_words={w for a in h1.jlist(native['atom_structure']) if a['atom'] in atoms for w in a['word_nodes']}
                    words += [w for ph in h1.jlist(native['phrases']) for w in ph['words'] if w['node'] in exact_words]
                lexical.append(dict(reference=ref,scope_id=entry['evidence_id'],word_nodes=[w['node'] for w in words],
                    source_lexemes=[w['lex'] for w in words],source_lexemes_utf8=[w['lex_utf8'] for w in words],
                    mashal_present=any(w['lex'] in cfg['mashal_source_lexemes'] for w in words),
                    status='LEXICAL_PRESENCE_ONLY_NO_SEMANTIC_EQUIVALENCE_OR_TARGET_INFERENCE'))
    return scopes,edges,lexical


def audit_links(rows,s):
    links=h1.expand_links(rows,s['catalog'])
    refs=set(s['cfg2']['focus']+s['cfg2']['comparison_controls'])
    for ref in s['cfg2']['focus']:
        i=s['native_refs'].index(ref);refs.update(s['native_refs'][max(0,i-1):i+2])
    for ref in sorted(refs,key=lambda r:tuple(map(int,r.split(':')))):
        links += h1.expand_links([dict(judgment_id='AUDIT_CONTEXT:'+ref,source_evidence_ids=canonical(['HSA2:PANEL:'+ref]))],s['catalog'])
    lower=min(s['atom_index'][a] for a in s['catalog']['HSA2:PANEL:27:1']['atom_ids'])
    upper=max(s['atom_index'][a] for a in s['catalog']['HSA2:PANEL:31:40']['atom_ids'])
    for key,v in s['catalog'].items():
        if key.startswith('R4.1:MR1:') and any(lower<=s['atom_index'][a]<=upper for a in v['atom_ids']):
            links += h1.expand_links([dict(judgment_id='AUDIT_RANGE_MARKER:'+key,source_evidence_ids=canonical([key]))],s['catalog'])
    return links


def negative_controls(rows,cfg):
    return [dict(control=key,authority='HUMAN_CONTROL_NOT_MR1_RULE',expected=val)
            for key,val in cfg['negative_controls'].items()]


def report(m,s):
    cat=s['catalog'];cfg=s['cfg2']
    out=['# Job 27:1–31:40 closure-target audit','', 'Mode: '+s['mode'], '',
         '**31:40 direct closure target = UNRESOLVED. Higher-order terminal effect = UNRESOLVED.**','',
         'A marker may close the immediately active speech unit and simultaneously produce termination at one or more enclosing structural levels.', '',
         'Direct closure target and higher-order terminal effect are independent review dimensions. No nearest-opening, chapter, topic, longest-span or shortest-span preference is applied.', '',
         'The researcher accepts 27:1 and 29:1 as peers and 31:40 as a speech ending. The tables below are source evidence, not closure assignments.','']
    for ref in cfg['focus']:
        panel=cat['HSA2:PANEL:'+ref]
        out += [f'## Job {ref}','']
        for k in panel['dependencies']:
            if k.startswith('BHSA2021:clause:'):
                r=cat[k]['source_row'];out += [f'- Clause {r["clause"]}; atoms {r["clause_atom_ids"]}; type {r["type"]}: {r["surface"]}']
            elif k.startswith('R4.1:MR1:'):
                r=cat[k]['source_row'];out += [f'- MR1 / R4.1 ID `{k}`; {r["marker_family"]} / {r["marker_subtype"]}; atoms {r["atom_ids"]}; exact surface: {r["surface_text"]}']
        out += ['', '### Neighboring full verses','']
        i=s['native_refs'].index(ref)
        for neighbor in s['native_refs'][max(0,i-1):i+2]:
            for key in cat['HSA2:PANEL:'+neighbor]['dependencies']:
                if key.startswith('BHSA2021:clause:'):
                    r=cat[key]['source_row'];out += [f'- {neighbor}; clause {r["clause"]}; atoms {r["clause_atom_ids"]}: {r["surface"]}']
        out += ['', '### Exact marker lexical evidence','']
        for row in m['lexical']:
            if row['reference']==ref:
                out += [f'- `{row["scope_id"]}`: lexemes `{canonical(row["source_lexemes"])}`; Hebrew `{canonical(row["source_lexemes_utf8"])}`; source משל lexeme present: **{row["mashal_present"]}**.']
        out += ['', '### Atom signatures (G0–G6; full preimages in 13)','', '| Atom | Level | Exact historical/reconstructed SHA256 |','| --- | --- | --- |']
        for k in panel['dependencies']:
            if k.startswith('PROV1:ATOM:'):
                r=cat[k]['source_row'];out.append(f'| {r["atom_node"]} | {r["level"]} | `{r["historical_hash"]}` |')
        out += ['', '### All formal patterns at the exact marker edges','',
                'Relations refer to the explicit MR1 atom span, not the whole verse and not a chosen closure target.', '',
                '| Scope | Formal occurrence | Atoms | Families / levels | Edge relations |', '| --- | --- | --- | --- | --- |']
        for r in m['edges']:
            if r['reference']==ref:
                defs=h1.jlist(r['formal_source_row']['family_signature_definitions'])
                families=', '.join(d['family_id']+'/'+d['level'] for d in defs)
                out += [f'| `{r["scope_id"]}` | `{r["formal_id"]}` | {r["formal_atom_ids"]} | {families} | {", ".join(r["relations"])} |']
        out += ['']
    out += ['', '## 27:1 and 29:1 signature comparison','',
            'Same-position signatures are compared only across the two explicit three-atom opening formulas; identity of a formula does not assign a closure.', '',
            '| Opening atom position | Level | 27:1 hash | 29:1 hash | Exact equality |','| --- | --- | --- | --- | --- |']
    aa={ref:next(x['atom_ids'] for x in m['scopes'] if x['reference']==ref and x['scope_type']=='EXACT_MR1_EVENT') for ref in ('27:1','29:1')}
    require(len(aa['27:1'])==len(aa['29:1']),'opening spans differ: cannot align atom positions')
    for pos,(a,b) in enumerate(zip(aa['27:1'],aa['29:1']),1):
        for level in range(7):
            left=cat[f'PROV1:ATOM:{a}:G{level}']['source_row']['historical_hash']
            right=cat[f'PROV1:ATOM:{b}:G{level}']['source_row']['historical_hash']
            out += [f'| {pos} | G{level} | `{left}` | `{right}` | {left==right} |']
    out += ['', '## All MR1 events within the supplied 27:1–31:40 review span','',
            'This preserves internal expressions as source events; it does not classify each as a new unit.', '']
    lower=min(s['atom_index'][a] for a in cat['HSA2:PANEL:27:1']['atom_ids'])
    upper=max(s['atom_index'][a] for a in cat['HSA2:PANEL:31:40']['atom_ids'])
    for key,v in cat.items():
        if key.startswith('R4.1:MR1:') and any(lower<=s['atom_index'][a]<=upper for a in v['atom_ids']):
            r=v['source_row'];out += [f'- `{key}`; {r["ref_start"]}–{r["ref_end"]}; {r["marker_subtype"]}; {r["surface_text"]}']
    out += ['', '## Review options — no adjudication','',
            '| Candidate | Proposed scope | Dimension | Available options | Selected |','| --- | --- | --- | --- | --- |']
    for r in m['candidates']:
        out += [f'| {r["candidate_id"]} | {r["candidate_target_reference"]} ({r["target_scope"]}) | {r["dimension"]} | {", ".join(r["review_options"])} | {r["selected_relation"]} |']
    out += ['', 'A direct local relation to 29:1 and an enclosing-group terminal effect at 27:1–31:40 can coexist in this model. Neither is selected.', '',
            '## Comparative controls','',
            '1:6 ↔ 1:22 and 2:1 ↔ 2:10 are supplied human testing-unit controls. 1:22/2:10 remain non-MR1 endings. 36:1 → 37:24 is the supplied fourth-Elihu-speech comparison. 38:1 / 40:1 / 40:3 / 40:6 / 42:1 are structural comparison controls only; no new closure edges follow.', '',
            '| Reference | Source scopes | MR1 explicit closure | Formal edge rows |','| --- | --- | --- | --- |']
    for ref in cfg['comparison_controls']:
        scopes=[r for r in m['scopes'] if r['reference']==ref]
        closed=any(r['source_row'].get('marker_family')=='MR1_EXPLICIT_CLOSURE' for r in scopes)
        out += [f'| {ref} | '+', '.join('`'+r['evidence_id']+'`' for r in scopes)+f' | {closed} | {sum(r["reference"]==ref for r in m["edges"])} |']
    out += ['', 'Control surfaces, native IDs, complete patterns and signatures are retained in 02, 09, 10, 11 and 13. Human attribution is preserved separately in 14.', '',
            '## Descriptive finding and limitation','',
            '27:1 and 29:1 have the same TAKE_MASHAL+AMR opening formula. 31:40 has the explicit תממ+דבר ending; its marker does not repeat משל. This is lexical observation, not a claim of semantic equivalence or inequality.', '',
            'The shared openings support the already supplied parallel-onset judgment. Ending identity and formal recurrence do not encode which opening is its direct target. These data alone do not establish a preference between the two direct-target options. Relative proximity is not evidence used to choose. Direct target and higher-order effect both remain UNRESOLVED; researcher review is required before whole-book R4.3 parentage.', '']
    return '\n'.join(out)


def cycle_report(rows,cfg):
    out=['# Human-reviewed dialogue sequence','', 'This is an ordered human review summary, not a generated parentage graph.', '', '3:1 — Job independent initial speech; above the separate 3:2 CSF.','']
    for cycle in cfg['cycles']:
        out += ['## '+cycle['name']+(' — incomplete' if cycle['incomplete'] else ''),'']
        out += [f'- {ref} — {speaker}' for ref,speaker in zip(cycle['refs'],cycle['speakers'])]
        out += ['']
    out += ['', 'Cycles 1 and 2 repeat Eliphaz → Job → Bildad → Job → Zophar → Job (human judgment). Cycle 3 has four reviewed units; no corresponding third Zophar speech is supplied or generated.', '',
            '4:1 / 15:1 / 22:1 have separate same-level cycle-onset judgments. Their source formula remains ANSWER+AMR. 11:4 SIMPLE_AMR stays internal to 11:1.', '',
            '26:1 is the final Job onset within the incomplete third cycle; no closing edge after chapter 26 is created.', '',
            '## Post-dialogue Job speech group','',
            '27:1 and 29:1 are parallel SAME_LEVEL_SIBLING speech-unit onsets. 27:1 begins the human-recognized post-dialogue group. 28:1 is NO_BOUNDARY / CONTINUES_WITHIN 27:1; semantic distinctiveness is not a new MR1 negative rule.', '',
            '**31:40 is an accepted speech ending. DIRECT_CLOSURE_TARGET = UNRESOLVED. Higher-order terminal effect = UNRESOLVED.**', '']
    return '\n'.join(out)


def build(s,rows=None,markdown=None):
    rows=deepcopy(registry() if rows is None else rows)
    md=MD.read_text(encoding='utf-8') if markdown is None else markdown
    scopes,edges,lex=evidence(s)
    m=dict(judgments=rows,markdown=md,pairs=h1.pairs(rows),links=audit_links(rows,s),
           scopes=scopes,edges=edges,lexical=lex,candidates=candidates(s['cfg2']),negative=negative_controls(rows,s['cfg2']))
    m['audit']=report(m,s);m['cycles']=cycle_report(rows,s['cfg2'])
    m['summary']='\n'.join(['# HSA2 review summary','',f'Mode: {s["mode"]}', '',
        f'Human judgments: {len(rows)}; direct human relation pairs: {len(m["pairs"])}; exact source/context links: {len(m["links"])}.', '',
        'HSA1 is frozen. HSA2 appends new context and dialogue-cycle judgments through Job 31.',
        'Job 3–26 cycles are human-reviewed: 6 / 6 / 4 speech units. Third Zophar speech is not generated.',
        '27:1/29:1 are peers; 28:1 is no boundary; 31:40 ending accepted, direct target UNRESOLVED.',
        'Whole-book R4.3 parentage is blocked pending closure-target review. No candidate is a settled hierarchy edge.', ''])
    return m


def gates(m,s):
    cfg=s['cfg2'];rows=m['judgments'];byid={r['judgment_id']:r for r in rows}
    expected=cfg['human_assertions']
    def subset(ids):return all(i in byid and all(byid[i].get(k)==v for k,v in expected[i].items()) for i in ids)
    def check_ref(ref):return subset([i for i,v in expected.items() if v['reference_start']==ref])
    def anchors(ref):return [s['catalog'][k]['source_row'] for k in s['catalog']['HSA2:PANEL:'+ref]['dependencies'] if k.startswith('R4.1:MR1:')]
    def observed(ref):return [r['source_row'] for r in m['links'] if r['judgment_id'] in {i for i,v in byid.items() if v['reference_start']==ref} and r['evidence_kind']=='ACCEPTED_ANCHOR_OR_HUMAN_SCOPE']
    tests={}
    tests['ALL_HUMAN_JUDGMENTS']=set(byid)==set(expected) and len(rows)==len(expected) and subset(expected)
    tests['HSA1_AND_FROZEN_CORES_UNCHANGED']=s['frozen_receipts']==[dict(path=p,expected=d,actual=d) for p,d in cfg['frozen_files'].items()]
    for n,c in enumerate(cfg['cycles'],1):
        ids=c['judgment_ids'];tests[f'CYCLE_{n}_SPEECH_UNITS']=subset(ids) and [byid[i]['reference_start'] for i in ids if i in byid]==c['refs']
    tests['NO_SYNTHETIC_ZOPHAR_III']=set(byid)==set(expected) and not any(r['human_group']=='CYCLE_3' and r['human_speaker']=='Zophar' for r in rows)
    tests['CYCLE_ONSET_PEERS']=subset(cfg['cycle_onset_ids'])
    tests['INDIVIDUAL_SPEECH_PEERS']=all(subset(c['judgment_ids']) for c in cfg['cycles'])
    tests['26_1_THIRD_CYCLE']=check_ref('26:1') and any(r.get('marker_subtype')=='ANSWER+AMR' for r in observed('26:1'))
    tests['27_1_DISTINCT_FORMULA']=check_ref('27:1') and any(r.get('marker_subtype')=='TAKE_MASHAL+AMR' for r in observed('27:1'))
    tests['27_29_SAME_LEVEL']=check_ref('27:1') and check_ref('29:1')
    tests['28_1_NO_BOUNDARY']=check_ref('28:1') and not anchors('28:1')
    tests['31_40_ENDING_RETAINED']=check_ref('31:40') and any(r.get('marker_family')=='MR1_EXPLICIT_CLOSURE' for r in observed('31:40'))
    ending=[r for r in rows if r['reference_start']=='31:40']
    tests['DIRECT_TARGET_UNRESOLVED']=bool(ending) and all(r['direct_closure_target']=='UNRESOLVED' and r['higher_order_terminal_effect']=='UNRESOLVED' for r in ending) and all(r['selected_relation']==r['direct_closure_target']==r['higher_order_terminal_effect']=='UNRESOLVED' and r['review_status']=='UNREVIEWED' for r in m['candidates'])
    tests['NO_NEAREST_OPENING_CHOICE']=m['candidates']==candidates(cfg) and not any(r['reference']=='31:40' for r in m['pairs'])
    tests['LOCAL_AND_HIGHER_SEPARATE']=candidate_model_valid(m['candidates']) and {r['dimension'] for r in m['candidates']}=={'DIRECT_CLOSURE_TARGET','HIGHER_ORDER_TERMINAL_EFFECT'}
    tests['HUMAN_ENDINGS_NOT_MR1']=all(any(r['reference']==ref and r['scope_type']=='FULL_VERSE_HUMAN_COMPARISON_NOT_MR1' for r in m['scopes']) if not anchors(ref) else all(r['source_row'].get('marker_family')!='MR1_EXPLICIT_CLOSURE' for r in m['scopes'] if r['reference']==ref) for ref in ('1:22','2:10'))
    tests['MR1_RULES_UNCHANGED']=all(r['actual']==r['expected'] for r in s['frozen_receipts'] if 'mr1' in r['path']) and all(any(r.get('marker_subtype')=='ANSWER+AMR' for r in observed(ref)) for ref in ('4:1','15:1','22:1'))
    tests['NO_WHOLE_BOOK_HIERARCHY']=m['pairs']==h1.pairs(rows) and subset(expected) and set(byid)==set(expected)
    tests['NO_SCORE_RANK']=all(not any(any(t in k.lower() for t in ('score','rank','confidence','percentage')) for k in r) for key in ('judgments','pairs','candidates','links','scopes','edges','lexical','negative') for r in m[key])
    tests['EXACT_SOURCE_LINKS']=m['links']==audit_links(rows,s)
    tests['FORMAL_EDGES_EXACT']=m['scopes']==evidence(s)[0] and m['edges']==evidence(s)[1]
    tests['NATIVE_ATOM_ORDER_EXACT']=s['atom_index']==s['canonical_atom_index'] and s['native_order']==sorted(s['canonical_atom_index'],key=s['canonical_atom_index'].__getitem__)
    tests['LEXICAL_FACTS_ONLY']=m['lexical']==evidence(s)[2] and {r['reference']:r['mashal_present'] for r in m['lexical']}==cfg['lexical_expectation']
    tests['11_4_INTERNAL_PRESERVED']=check_ref('11:4') and any(r.get('marker_subtype')=='SIMPLE_AMR' for r in observed('11:4'))
    tests['HUMAN_MD_CSV_MATCH']=registry_markdown(rows) in m['markdown'] and all(set(r)==set(FIELDS) and r['review_status']=='REVIEWED' for r in rows)
    targets={r['judgment_id']:r for r in s['prior']};targets.update(byid)
    tests['DIRECT_TARGET_IDS_EXACT']=all(not r['related_judgment_id'] or r['related_judgment_id'] in targets and targets[r['related_judgment_id']]['reference_start']==r['related_reference'] for r in m['pairs'])
    tests['REPORTS_AND_CONTROLS_PRESERVED']=m['audit']==report(m,s) and m['cycles']==cycle_report(rows,cfg) and m['negative']==negative_controls(rows,cfg)
    tests['ACCEPTED_ARCHIVE_PINS']=len(s['receipts'])==len(s['cfg']['archives']) and all(r['sha256']==r['expected']==s['cfg']['archives'][r['role']]['sha256'] for r in s['receipts'])
    tests['DETERMINISTIC_OUTPUT']=m==build(s,rows,m['markdown'])
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in tests.items()]


def serialize(m,s):
    gg=gates(m,s);require(all(r['status']=='PASS' for r in gg),'HSA2 gates failed '+canonical([r for r in gg if r['status']!='PASS']))
    files={'01_hsa2_structural_judgments.csv':registry_bytes(m['judgments']),
        '02_hsa2_source_links.csv':h1.util.csv_bytes(m['links']),
        '03_closure_target_candidate_relations.csv':h1.util.csv_bytes(m['candidates']),
        '04_job_27_31_closure_target_audit.md':m['audit'].encode(),
        '05_dialogue_cycle_structure.md':m['cycles'].encode(),'06_job_3_31_review_summary.md':m['summary'].encode(),
        '07_negative_controls.csv':h1.util.csv_bytes(m['negative']),
        '09_formal_edge_relations.csv':h1.util.csv_bytes(m['edges']),
        '10_exact_marker_scopes.csv':h1.util.csv_bytes(m['scopes']),
        '11_marker_lexical_observations.csv':h1.util.csv_bytes(m['lexical']),
        '12_direct_human_relation_pairs.csv':h1.util.csv_bytes(m['pairs']),
        '13_atom_signature_provenance.csv':h1.util.csv_bytes([dict(evidence_id=k,**v['source_row'],locator=v['source_locator']) for k,v in s['catalog'].items() if k.startswith('PROV1:ATOM:')]),
        '14_frozen_hsa1_human_judgments.csv':h1.registry_bytes(s['prior']),
        '15_hsa2_human_registry.md':m['markdown'].encode()}
    meta=dict(version='HSA2',mode=s['mode'],status='PASS',counts={k:len(m[k]) for k in ('judgments','pairs','links','candidates','edges','scopes','lexical','negative')},
        gate_count=len(gg)+1,source_receipts=s['receipts'],frozen_receipts=s['frozen_receipts'],config_sha256=sha(canonical(s['cfg2']).encode()),
        registry_sha256=sha(files['01_hsa2_structural_judgments.csv']),code_sha256=sha(Path(__file__).read_bytes()))
    files['90_run_metadata.json']=h1.util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv',None);files['99_manifest_sha256.csv']=h1.util.csv_bytes([dict(file=n,sha256=sha(v)) for n,v in sorted(files.items())])
    seal();gg.append(h1.util.manifest_gate(files));files['08_gates.csv']=h1.util.csv_bytes(gg);seal()
    require(h1.util.manifest_ok(files),'HSA2 manifest');return files


def publish(files,out):
    out=Path(out).resolve();zp=out.with_name(out.name+'_results.zip');log=out.with_name(out.name+'_run.log')
    require(not any(p.exists() for p in (out,zp,log)),'output exists')
    require(h1.util.manifest_ok(files),'publication manifest');out.mkdir(parents=True)
    for n,b in files.items():(out/n).write_bytes(b)
    with zipfile.ZipFile(zp,'w') as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    with zipfile.ZipFile(zp) as z:require(z.testzip() is None and {n:z.read(n) for n in z.namelist()}==files,'ZIP integrity')
    require({p.name:p.read_bytes() for p in out.iterdir()}==files,'disk integrity')
    log.write_text(f'HSA2 PASS\nMode {json.loads(files["90_run_metadata.json"])["mode"]}\nGates {len(h1.read_csv(files["08_gates.csv"]))} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n',encoding='utf-8')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);parser.add_argument('--self-test',action='store_true');args=parser.parse_args(argv)
    if args.self_test:
        from milal_hsa2_synthetic import source
        s,rows,md=source();m=build(s,rows,md)
    else:s=load();m=build(s)
    files=serialize(m,s)
    require(files==serialize(build(s,m['judgments'],m['markdown']),s),'deterministic serialization')
    if not args.self_test:
        require(CSV.read_bytes()==files['01_hsa2_structural_judgments.csv'] and MD.read_bytes()==files['15_hsa2_human_registry.md'],'human byte fidelity')
        require(frozen_receipts(s['cfg2'])==s['frozen_receipts'],'frozen source changed')
        for r in s['receipts']:require(sha((ROOT/r['path']).read_bytes())==r['expected'],'input changed')
    publish(files,args.out);print('HSA2 PASS '+str(Path(args.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
