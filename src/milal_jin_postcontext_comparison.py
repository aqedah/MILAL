"""C2: human comparisons after verification of the C1 freeze."""
import argparse
from collections import Counter
import json
from pathlib import Path
import sys
import milal_jin_io as io
import milal_jin_context_configuration as cc

HISTORY='history/r4_4_contract_jin_0_2/'
CP=('CP1_HYPOTAXIS_MACRO_CANDIDATE','CP2_PARATAXIS_MACRO_CANDIDATE','CP3_PARATAXIS_WITH_CONTEXT_CONTRAST',
    'CP4_CLAUSE_INTERNAL_ONLY','CP5_TRANSITIONAL_REVIEW','CP6_INSUFFICIENT_FOR_MACRO_PLACEMENT','CP7_COMPETING_CONTEXTUAL_CANDIDATES')


def tables(c1):
    from milal_jin_contextual_relation_audit import TABLES
    return {key:io.rows(c1[name]) for name,key in TABLES.items()}


def compare(c1,history):
    m=tables(c1);contexts={r['context_id']:r for r in m['correspondence']}
    pairs={p['pair_id']:p for p in io.rows(history['03_blind_candidate_pairs.csv'])};scopes={r['pair_id']:r for r in m['scopes']}
    out=[]
    for old in io.rows(history['08_postblind_human_relation_crosswalk.csv']):
        if old['comparison_family']=='OUTSIDE_SCOPE':continue
        ids=old['blind_candidate_ids'];cx=sorted({f"JX:{pairs[k]['preceding_clause_id']}:{pairs[k]['later_clause_id']}" for k in ids})
        io.require(all(k in contexts for k in cx),'historical exact pair context absent')
        configs=[contexts[k] for k in cx];labels=sorted({r['configuration_status'] for r in configs})
        divergence=any(r['flags']['C_FOCAL_FORM_CORRESPONDENCE']=='MATCH' and any(r['flags']['C_'+s+'_CONFIGURATION_DIVERGENCE']=='DIFFERENT' for s in ('PRECEDING','FOLLOWING')) for r in configs)
        prior=old['comparison_status']
        if prior=='BLIND_CANDIDATE_CONFLICTS_WITH_HUMAN_RELATION':status='PAIRWISE_CONFLICT_CONTEXT_SOFTENS_CONFLICT' if divergence else 'PAIRWISE_CONFLICT_CONTEXT_PRESERVES_CONFLICT'
        elif not configs:status='CONTEXT_NOT_RECOVERED'
        elif prior=='LINGUISTIC_SUPPORT_WITH_COMPETING_ALTERNATIVE':status='CONTEXT_SUPPORTS_WITH_ALTERNATIVE'
        elif prior=='LINGUISTIC_SUPPORT_FOUND' and 'EXACT_CONFIGURATION_CORRESPONDENCE' in labels:status='CONTEXT_SUPPORTS_HUMAN_RELATION'
        elif prior in ('LINGUISTIC_SUPPORT_FOUND','PARTIAL_LINGUISTIC_SUPPORT') and any(x!='NO_CONTEXTUAL_CORRESPONDENCE' for x in labels):status='CONTEXT_PARTIAL_SUPPORT'
        else:status='CONTEXT_INSUFFICIENT'
        family=old['comparison_family'];left=old['neutral_source_target_id'];right=old['neutral_target_target_id']
        # Normalize semantic mother direction explicitly; symmetric para ordering is presentation only.
        if old['historical_relation_type']=='CHILD_OF':left,right=right,left
        if family=='PARATAXIS':left,right=sorted((left,right))
        matches=[r['case_id'] for r in m['cases'] if r['earlier_neutral_locus']==left and r['later_neutral_locus']==right and r['relation_family']==family]
        out.append(dict(human_relation_id=old['human_relation_id'],relation_family=family,earlier_neutral_locus=left,later_neutral_locus=right,
            source_ref=old['source_ref'],target_ref=old['target_ref'],historical_relation_type=old['historical_relation_type'],
            pairwise_result=prior,context_result=labels,context_comparison_status=status,context_ids=cx,exact_pair_ids=ids,
            contextual_case_ids=matches,local_dependency_types=sorted({scopes[k]['local_dependency_type'] for k in ids if k in scopes}),
            macro_projection_statuses=sorted({scopes[k]['macro_projection_status'] for k in ids if k in scopes}),
            insufficient_resurfaced_pair_ids=[k for k in ids if k not in scopes],resurfacing_reason='A_EXACT_HISTORICAL_SOURCE_TARGET_PAIR',
            semantic_direction='MOTHER_CANDIDATE_TO_DAUGHTER' if family=='HYPOTAXIS' else 'CANONICAL_SYMMETRIC_LOCUS_ORDER',
            original_pairwise_human_crosswalk=old,historical_relation_unchanged=True,human_decision=''))
    return out


def review_fields():
    from milal_r3c_0_2_reviewability import REVIEW_FIELDS
    return {k:'UNREVIEWED' if k=='review_status' else '' for k in (*REVIEW_FIELDS,'relation_decision','selected_mother_if_hypotactic','paratactic_peer_if_applicable','macro_projection_decision','evidence_sufficient')}


def review_cases(c1,comparisons):
    m=tables(c1);cases={}
    ordering=cc.Context(io.rows(c1['blind_input/02_blind_linguistic_features.csv']),m['targets'],json.loads(c1['29_c1_metadata.json'])['rules'])
    for c in m['cases']:
        internal=c['projection_scope']==cc.INTERNAL
        bucket='REVIEW_C_CLAUSE_INTERNAL_CONFIRMATION' if internal else 'REVIEW_B_SUPPORTED_CROSS_LOCUS' if c['projection_scope'] in cc.PROJECTABLE and 'CONTRAST' not in c['candidate_type'] else 'REVIEW_A_CONFLICT_OR_REOPEN'
        cases[c['case_id']]=dict(review_case_id=c['case_id'],earlier_neutral_locus=c['earlier_neutral_locus'],later_neutral_locus=c['later_neutral_locus'],
            relation_family=c['relation_family'],projection_scope=c['projection_scope'],review_bucket=bucket,default_human_review=not internal,
            member_pair_ids=c['member_pair_ids'],auxiliary_pair_ids=c['auxiliary_pair_ids'],contextual_case_ids=[c['case_id']],human_relation_ids=[],
            context_ids=c['context_ids'],comparison_statuses=[],case_origin='BLIND_CONTEXTUAL_CASE',**review_fields())
    for row in comparisons:
        candidates=row['contextual_case_ids']
        if not candidates:candidates=[f"JH:{row['earlier_neutral_locus']}:{row['later_neutral_locus']}:{row['relation_family']}"]
        for ident in candidates:
            case=cases.setdefault(ident,dict(review_case_id=ident,earlier_neutral_locus=row['earlier_neutral_locus'],later_neutral_locus=row['later_neutral_locus'],
                relation_family=row['relation_family'],projection_scope='HISTORICAL_COMPARISON_REQUIRES_HUMAN_REVIEW',review_bucket='REVIEW_A_CONFLICT_OR_REOPEN',
                default_human_review=True,member_pair_ids=[],auxiliary_pair_ids=[],contextual_case_ids=[],human_relation_ids=[],context_ids=[],comparison_statuses=[],
                case_origin='POSTFREEZE_HISTORICAL_COMPARISON',**review_fields()))
            case['human_relation_ids'].append(row['human_relation_id']);case['context_ids']+=row['context_ids'];case['comparison_statuses'].append(row['context_comparison_status'])
            case['auxiliary_pair_ids']+=row['insufficient_resurfaced_pair_ids']
            case['member_pair_ids']+=row['exact_pair_ids']
            if row['pairwise_result'] not in ('LINGUISTIC_SUPPORT_FOUND',):case['review_bucket']='REVIEW_A_CONFLICT_OR_REOPEN';case['default_human_review']=True
    for c in cases.values():
        for k in ('member_pair_ids','auxiliary_pair_ids','contextual_case_ids','human_relation_ids','context_ids','comparison_statuses'):c[k]=sorted(set(c[k]))
    return sorted(cases.values(),key=lambda r:(ordering.locus_order(r['earlier_neutral_locus']),ordering.locus_order(r['later_neutral_locus']),r['relation_family'],r['review_case_id']))


def placements(c1,history):
    m=tables(c1);features={int(r['clause_id']):r for r in io.rows(c1['blind_input/02_blind_linguistic_features.csv'])}
    old={r['audit_target_id']:r for r in io.rows(history['13_textual_placement_proposals.csv'])};out=[]
    comparable={'JP3_HYPOTACTIC_DAUGHTER_CANDIDATE':CP[0],'JP4_PARATACTIC_PLACEMENT_CANDIDATE':CP[1],'JP5_PARATAXIS_AND_HYPOTAXIS_COMPETE':CP[6],'JP6_TRANSITION_PLACEMENT_REVIEW':CP[4],'JP7_INSUFFICIENT_LINGUISTIC_EVIDENCE':CP[5]}
    for t in m['targets']:
        ident=t['audit_target_id'];cases=[c for c in m['cases'] if ident in (c['earlier_neutral_locus'],c['later_neutral_locus'])]
        pp=[c for c in cases if c['relation_family']=='PARATAXIS' and c['projection_scope'] in cc.PROJECTABLE]
        hh=[c for c in cases if c['relation_family']=='HYPOTAXIS' and c['later_neutral_locus']==ident and c['projection_scope'] in cc.PROJECTABLE]
        contrast=any('CONTRAST' in c['candidate_type'] for c in pp)
        internal=bool(cases) and all(c['projection_scope']==cc.INTERNAL for c in cases)
        cessation=any(set(features[n]['lexemes'])&{'CBT[','TMM[','KLH['} for n in t['clause_id'])
        prop=CP[6] if pp and hh else CP[0] if hh else CP[2] if contrast else CP[1] if pp else CP[3] if internal else CP[4] if cessation else CP[5]
        previous=old[ident]
        out.append(dict(audit_target_id=ident,reference=t['chapter']+':'+t['verse'],contextual_proposal=prop,proposal_status='UNREVIEWED',
            parataxis_case_ids=[c['case_id'] for c in pp],hypotaxis_case_ids=[c['case_id'] for c in hh],all_contextual_case_ids=[c['case_id'] for c in cases],
            selected_mother='',historical_proposal_status='PAIRWISE_ONLY_PLACEMENT_PROPOSAL',original_pairwise_proposal=previous,
            comparison='CONTEXT_REFINEMENT_DIFFERENCE' if comparable.get(previous['placement_proposal'])!=prop else 'COMPATIBLE_PROPOSAL_FAMILY_DIFFERENT_SCOPE',automatic_supersession=False))
    return out


def control_panels(c1,cfg):
    m=tables(c1);features={int(r['clause_id']):r for r in io.rows(c1['blind_input/02_blind_linguistic_features.csv'])}
    target={r['chapter']+':'+r['verse']:r for r in m['targets']};contexts={r['context_id']:r for r in m['correspondence']};out=[]
    for refs in cfg['control_pairs']:
        a,b=[min(target[ref]['clause_id'],key=lambda n:int(features[n]['sequence_index'])) for ref in refs]
        out.append(dict(references=refs,earlier_focal_clause=a,later_focal_clause=b,context=contexts[f'JX:{a}:{b}'],
            raw_focal_surfaces=[features[a]['surface'],features[b]['surface']],human_decision=''))
    return out


def special(c1,ref):
    m=tables(c1);target=next(t for t in m['targets'] if t['chapter']+':'+t['verse']==ref)
    sources={r['pair_id']:r for r in m['supported']};windows={r['bundle_id']:r for r in m['windows']};contexts={r['context_id']:r for r in m['correspondence']};out=[]
    for scope in m['scopes']:
        source=sources[scope['pair_id']]
        if source['source_pair']['audit_target_id']!=target['audit_target_id'] or not source['source_hypothesis']['hypotaxis_supported']:continue
        co=contexts[scope['context_id']]
        out.append(dict(reference=ref,**scope,source_pair=source['source_pair'],source_hypothesis=source['source_hypothesis'],
            context=co,context_bundles=[windows[k] for k in co['preceding_bundle_ids']+co['later_bundle_ids']],macro_projectable=scope['macro_projection_status'] in cc.PROJECTABLE,**review_fields()))
    return out


def summary(m):
    c=tables(m['c1']);review=m['review'];default=[r for r in review if r['default_human_review']]
    old_count=len(io.rows(m['history']['21_relation_review_cases.csv']))
    return dict(c1=json.loads(m['c1']['29_c1_metadata.json'])['counts'],original_review_cases=old_count,final_human_review_cases=len(default),
        reduction_ratio=(old_count-len(default))/old_count,clause_internal_case_count=sum(r['projection_scope']==cc.INTERNAL for r in c['cases']),
        supported_cross_locus_case_count=sum(r['projection_scope'] in cc.PROJECTABLE for r in c['cases']),
        macro_projection_case_count=sum(r['projection_scope']==cc.MACRO for r in c['cases']),
        historical_conflict_reopen_case_count=sum(bool(r['human_relation_ids']) and r['review_bucket']=='REVIEW_A_CONFLICT_OR_REOPEN' for r in default),
        review_categories=dict(Counter(r['review_bucket'] for r in default)),comparison=dict(Counter(r['context_comparison_status'] for r in m['comparisons'])),
        placement=dict(Counter(r['contextual_proposal'] for r in m['placements'])),
        special={ref:dict(original_pairs=len(rows),clause_internal=sum(r['clause_internal_only'] for r in rows),cross_locus=sum(r['cross_locus'] for r in rows),macro_projectable=sum(r['macro_projectable'] for r in rows)) for ref,rows in m['special'].items()},
        new_human_judgment=0,new_accepted_parataxis=0,new_accepted_hypotaxis=0,new_parent_edge=0)


def context_text(c1,ids,lookup=None):
    if lookup is None:lookup=({x['context_id']:x for x in io.rows(c1['04_context_correspondence.csv'])},{x['bundle_id']:x for x in io.rows(c1['02_context_windows.csv'])})
    contexts,windows=lookup;lines=[]
    for ident in sorted(set(ids)):
        co=contexts[ident];lines += [f"- {ident}: {co['configuration_status']}",'  - Flags: '+json.dumps(co['flags'],ensure_ascii=False)]
        for key in (co['preceding_bundle_ids'][0],co['later_bundle_ids'][0]):
            w=windows[key];lines += [f"  - {key}; clauses {w['clause_ids']}; domains {w['raw_domains']}",'  - '+w['surface'],'  - Next raw formula (descriptive): '+json.dumps(w['next_raw_formula'],ensure_ascii=False)]
    return lines


def reports(m):
    c1=m['c1'];c=tables(c1);out={};s=summary(m)
    lookup=({x['context_id']:x for x in c['correspondence']},{x['bundle_id']:x for x in c['windows']})
    lines=['# Contextual relation review — UNREVIEWED','', 'Readiness: READY_FOR_CONTEXTUAL_HUMAN_RELATION_REVIEW',
        'Pairwise correspondence is evidence, not textual hierarchy. No mother or accepted relation is selected.','', '```json',json.dumps(s,indent=2),'```','',
        'Decisions remain blank. relation_decision: PARATACTIC / HYPOTACTIC / INSUFFICIENT_EVIDENCE / REQUIRES_ADDITIONAL_CONTEXT.',
        'macro_projection_decision: CLAUSE_ONLY / LOCAL_TEXTUAL / MACRO_TEXTUAL / NO_MACRO_PROJECTION / UNRESOLVED.','']
    for title,bucket in [('A — Methodological conflicts and reopened/context-refined cases','REVIEW_A_CONFLICT_OR_REOPEN'),('B — Supported cross-locus contextual cases','REVIEW_B_SUPPORTED_CROSS_LOCUS')]:
        lines += ['## '+title,'']
        for r in m['review']:
            if not r['default_human_review'] or r['review_bucket']!=bucket:continue
            lines += ['### '+r['review_case_id'],f"{r['earlier_neutral_locus']} / {r['later_neutral_locus']}; {r['relation_family']}; {r['projection_scope']}",
                'Primary/linked pair IDs: '+json.dumps(r['member_pair_ids']),'Auxiliary archived IDs: '+json.dumps(r['auxiliary_pair_ids']),
                'Historical comparison IDs: '+json.dumps(r['human_relation_ids']),'Context results: '+json.dumps(r['comparison_statuses'])]
            lines+=context_text(c1,r['context_ids'],lookup)
            lines+=['review_status: UNREVIEWED','relation_decision:','selected_mother_if_hypotactic:','paratactic_peer_if_applicable:','macro_projection_decision:','evidence_sufficient:','additional_information_needed:','reviewer_notes:','']
    lines+=['## C — Historical SAME_LEVEL grouped comparison','', '98 source judgments are linked without changing them; grouping uses neutral locus-pair identity.','']
    groups={}
    for r in m['comparisons']:
        if r['relation_family']=='PARATAXIS':groups.setdefault((r['earlier_neutral_locus'],r['later_neutral_locus']),[]).append(r)
    for key,rr in sorted(groups.items()):lines += [f"- {key}: "+json.dumps([dict(id=r['human_relation_id'],pairwise=r['pairwise_result'],context=r['context_comparison_status']) for r in rr])]
    lines+=['','## D — Job 2:11 / 32:1','See 19–22 CSV/Markdown panels. All source pairs, local scope and projection are shown. Human answers remain blank.',
        '','## E — Clause-internal summary only',f"{s['clause_internal_case_count']} contextual cases; appendix 36_clause_internal_case_appendix.csv. No automatic macro-mother promotion.",
        '','## F — Insufficient archive',f"{len(c['archive'])} records retained in 08. Archive-only rows do not enter the default review universe. Exact historical links or supported-context auxiliaries are separately identified."]
    out['25_contextual_human_review_packet.md']=('\n'.join(lines)+'\n').encode()
    for ref,prefix in [('2:11','20_job_2_11_context_panel.md'),('32:1','22_job_32_1_context_panel.md')]:
        text=['# Job '+ref+' — local versus macro hypothesis','', 'Human decision:','']
        for r in m['special'][ref]:
            text += [r['pair_id'],r['local_dependency_type'],r['clause_relation_scope'],r['macro_projection_status']]+context_text(c1,[r['context_id']],lookup)+['Human answer:','']
        out[prefix]=('\n'.join(text)+'\n').encode()
    text=['# Existing three mother cases — no acceptance/rejection','']
    for r in m['comparisons']:
        if r['relation_family']!='HYPOTAXIS':continue
        text += [f"## {r['source_ref']} → {r['target_ref']} / {r['historical_relation_type']}",
            'Semantic normalized direction: '+r['earlier_neutral_locus']+' → '+r['later_neutral_locus'],r['pairwise_result'],r['context_comparison_status'],
            'Local dependency types: '+json.dumps(r['local_dependency_types']),'Projection: '+json.dumps(r['macro_projection_statuses'])]+context_text(c1,r['context_ids'],lookup)+['review_status: UNREVIEWED','relation_decision:','selected_mother_if_hypotactic:','macro_projection_decision:','reviewer_notes:','']
    text+=['## 38:1 / 40:1 / 40:6 three-way raw panel','']
    for panel in m['controls']:
        if set(panel['references'])<={'38:1','40:1','40:6'}:text += [str(panel['references'])]+context_text(c1,[panel['context']['context_id']],lookup)
    out['23_existing_mother_cases_panel.md']=('\n'.join(text)+'\n').encode()
    out['27_next_adjudication_scope.md']=(f"# Next contextual adjudication\n\n{s['original_review_cases']} → {s['final_human_review_cases']} default locus-level review cases ({s['reduction_ratio']:.6%} reduction).\n\nComplete list: 24_contextual_human_review_cases.csv. A/B/C/D only require locus-level decisions; clause-internal confirmation stays in appendix 36 and insufficient evidence stays in archive 08. No numeric priority or cap. R4.4 consumer absent; participant arc UNADJUDICATED.\n").encode()
    return out


def load(c1_path,archive_path,config_path,synthetic=False):
    c1=io.read_dir(Path(c1_path));io.require({'01_context_supported_pair_inventory.csv','29_c1_metadata.json','13_context_blind_source_audit.csv'}<=set(c1) and io.manifest_ok(c1,'14_context_blind_manifest.csv'),'C1 freeze first')
    events=['C1_FREEZE_VERIFIED'];freeze=io.sha(c1['14_context_blind_manifest.csv'])
    cfg=json.loads(Path(config_path).read_bytes());data=Path(archive_path).read_bytes();events.append('HUMAN_JIN_0_2_ARCHIVE_OPENED_AFTER_FREEZE')
    if not synthetic:io.require(io.sha(data)==cfg['archive']['sha256'],'JIN.0.2 archive hash')
    history=io.archive(data);io.require(io.manifest_ok(history),'JIN.0.2 manifest')
    io.require(all(c1['blind_input/'+k]==history[k] for k in cc.FROZEN_NAMES),'C1 input differs from authoritative blind output')
    comparisons=compare(c1,history)
    m=dict(c1=c1,history=history,events=events,freeze_sha256=freeze,archive_sha256=io.sha(data),comparisons=comparisons,
        review=review_cases(c1,comparisons),placements=placements(c1,history),controls=control_panels(c1,cfg),
        special={ref:special(c1,ref) for ref in cfg['special_loci']},c1_after=io.read_dir(Path(c1_path)),
        human_sources=[dict(path=str(Path(archive_path).resolve()),sha256=io.sha(data)),dict(path=str(Path(config_path).resolve()),sha256=io.sha(Path(config_path).read_bytes()))])
    m['reports']=reports(m);return m,cfg


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--c1',required=True);p.add_argument('--archive',required=True);p.add_argument('--config',required=True);p.add_argument('--out',required=True);p.add_argument('--synthetic',action='store_true');a=p.parse_args(argv)
    m,cfg=load(a.c1,a.archive,a.config,a.synthetic)
    from milal_jin_context_pipeline import finalize
    files=finalize(m,cfg,a.synthetic);io.require(io.read_dir(Path(a.c1))==m['c1'],'C2 changed C1')
    zp=io.publish(files,a.out)
    print(json.dumps(dict(phase='C2',loaded_source_files=m['human_sources'],freeze_sha256=m['freeze_sha256'],zip_sha256=io.sha(zp.read_bytes()),summary=summary(m))))
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as e:print(str(e),file=sys.stderr);sys.exit(2)
