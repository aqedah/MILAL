"""Phase B: open human/native sources only after validating the blind freeze."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_jin_io as io

ROOT=Path(__file__).resolve().parents[1]
HISTORY='history/r4_4_contract_jin_0_1/'
COMPARISONS=('LINGUISTIC_SUPPORT_FOUND','LINGUISTIC_SUPPORT_WITH_COMPETING_ALTERNATIVE','PARTIAL_LINGUISTIC_SUPPORT',
              'LINGUISTIC_EVIDENCE_INSUFFICIENT','HUMAN_RELATION_NOT_RECOVERED','BLIND_CANDIDATE_CONFLICTS_WITH_HUMAN_RELATION','HUMAN_RELATION_OUTSIDE_CURRENT_AUDIT_SCOPE')
PLACEMENTS=('JP1_ROOT_REVIEW_REQUIRED','JP2_HYPOTACTIC_DAUGHTER_ALREADY_MOTHERED_BY_HUMAN','JP3_HYPOTACTIC_DAUGHTER_CANDIDATE',
            'JP4_PARATACTIC_PLACEMENT_CANDIDATE','JP5_PARATAXIS_AND_HYPOTAXIS_COMPETE','JP6_TRANSITION_PLACEMENT_REVIEW','JP7_INSUFFICIENT_LINGUISTIC_EVIDENCE')
LAYERS=('02_hsa3_textual_hierarchy_edges.csv','03_hsa3_textual_same_level_edges.csv','05_hsa3_composition_relations.csv','06_hsa3_transition_relations.csv','07_hsa3_overlay_relations.csv','08_hsa3_negative_constraints.csv','18_technical_navigation_relations.csv')


def unique_member(files,suffix):
    names=[n for n in files if n.endswith('/'+suffix) or n==suffix];io.require(len(names)==1,'unique source member '+suffix);return names[0]


def neutral_targets(history):
    """Preparation projection is also reproduced post-blind for exact crosswalk QA."""
    nn=io.rows(history['02_single_mother_applicability_nodes.csv']);out=[];links=[]
    selected=[n for n in nn if n['actual_textual_node'] is True]
    def key(n):return tuple(map(int,n['reference'].split(':')))+(n['node_id'],)
    for i,n in enumerate(sorted(selected,key=key),1):
        chapter,verse=map(int,n['reference'].split(':'));ident=f'JT{i:04d}'
        out.append(dict(audit_target_id=ident,book='Job',chapter=chapter,verse=verse))
        links.append(dict(audit_target_id=ident,node_id=n['node_id'],reference=n['reference'],original_jin_record=deepcopy(n)))
    return out,links


def historical_sources(history):
    member=unique_member(history,'01_hsa3_canonical_nodes.csv');nodes=io.rows(history[member]);relations=[]
    for suffix in LAYERS:
        name=unique_member(history,suffix)
        for i,r in enumerate(io.rows(history[name]),1):relations.append(dict(record=r,member=HISTORY+name,data_row=i,member_sha256=io.sha(history[name])))
    return nodes,relations


def compare(blind,history):
    nodes,rr=historical_sources(history);_,links=neutral_targets(history);byid={n['node_id']:n for n in nodes}
    jt={r['node_id']:r['audit_target_id'] for r in links};targets={r['audit_target_id']:r for r in io.rows(blind['01_blind_target_inventory.csv'])}
    pair_rows=io.rows(blind['03_blind_candidate_pairs.csv']);hy={r['pair_id']:r for r in io.rows(blind['04_blind_relation_hypotheses.csv'])}
    bypair=defaultdict(list)
    for p in pair_rows:bypair[(int(p['preceding_clause_id']),int(p['later_clause_id']))].append(p)
    def resolve(ident):
        if ident in jt:return jt[ident],'EXACT_CANONICAL_NODE'
        n=byid.get(ident,{})
        canonical=n.get('canonical_textual_node')
        return (jt[canonical],'EXPLICIT_ROLE_ALIAS_TO_LOCUS') if canonical in jt else ('','NO_NEUTRAL_TARGET')
    result=[]
    for item in rr:
        r=item['record'];left,lmode=resolve(r['source_node']);right,rmode=resolve(r['target_node']);typ=r['relation_type']
        expectation='PARATAXIS' if typ=='SAME_LEVEL_SIBLING' else 'HYPOTAXIS' if typ in ('CHILD_OF','HIERARCHICALLY_ABOVE') else 'OUTSIDE_SCOPE'
        matches=[]
        if left and right and expectation!='OUTSIDE_SCOPE':
            aa=targets[left]['clause_id'];bb=targets[right]['clause_id']
            for one in aa:
                for two in bb:
                    if typ=='CHILD_OF':keys=[(two,one)]
                    elif typ=='HIERARCHICALLY_ABOVE':keys=[(one,two)]
                    else:keys=[(one,two),(two,one)]
                    for key in keys:matches.extend(bypair.get(key,[]))
        matches={p['pair_id']:p for p in matches};hh=[hy[k] for k in matches]
        expected=any(h['parataxis_supported'] if expectation=='PARATAXIS' else h['hypotaxis_supported'] for h in hh)
        opposite=any(h['hypotaxis_supported'] if expectation=='PARATAXIS' else h['parataxis_supported'] for h in hh)
        partial=any(p['evidence_flags']['F_VERB_FORM_CORRESPONDENCE'] and (p['evidence_flags']['F_PNG_CORRESPONDENCE'] or p['evidence_flags']['R_EXPLICIT_PARTICIPANT_RECURRENCE']) for p in matches.values())
        status=COMPARISONS[6] if expectation=='OUTSIDE_SCOPE' or not left or not right else COMPARISONS[1] if expected and opposite else COMPARISONS[0] if expected else COMPARISONS[5] if opposite else COMPARISONS[2] if partial else COMPARISONS[3] if matches else COMPARISONS[4]
        result.append(dict(human_relation_id=r['relation_id'],human_source_stage=r['source_stage'],source_node=r['source_node'],target_node=r['target_node'],
            source_ref=byid.get(r['source_node'],{}).get('reference',r['source_ref']),target_ref=byid.get(r['target_node'],{}).get('reference',r['target_ref']),
            historical_relation_type=typ,comparison_family=expectation,neutral_source_target_id=left,neutral_target_target_id=right,
            endpoint_projection=[lmode,rmode],blind_candidate_found=bool(matches),blind_candidate_ids=sorted(matches),
            blind_relation_hypothesis=sorted({h['relation_hypothesis'] for h in hh}),blind_evidence_ids=sorted({p['evidence_id'] for p in matches.values()}),
            competing_candidates=sorted(h['pair_id'] for h in hh if h['hypotaxis_supported'] if expectation=='PARATAXIS') if expectation=='PARATAXIS' else sorted(h['pair_id'] for h in hh if h['parataxis_supported']),
            comparison_status=status,projection_scope='CLAUSE_EVIDENCE_VS_MACRO_JUDGMENT; NOT_AUTOMATIC_MACRO_RELATION',
            historical_source=item,original_human_record=deepcopy(r)))
    return result,links


def native_comparison(blind,native):
    pairs=io.rows(blind['03_blind_candidate_pairs.csv']);hyp={r['pair_id']:r for r in io.rows(blind['04_blind_relation_hypotheses.csv'])};out=[]
    for p in pairs:
        child=int(p['later_clause_id']);preceding=int(p['preceding_clause_id']);child_nodes=[child]+p['later_clause_atom_ids'];prior_nodes={preceding,*p['preceding_clause_atom_ids']}
        facts=[dict(node_id=n,**{f:native.get(f,{}).get(n) for f in io.NATIVE_FEATURES}) for n in child_nodes]
        linked=[f for f in facts if set(f['mother'] or []) & prior_nodes]
        para=any(f['rela']=='Coor' for f in linked)
        hypo=any(f['rela'] in ('Subj','Objc','Cmpl','Adju','Attr') for f in linked)
        h=hyp[p['pair_id']]
        if para or hypo:status='BHSA_NATIVE_AGREES' if (para and h['parataxis_supported']) or (hypo and h['hypotaxis_supported']) else 'BHSA_NATIVE_DIFFERS' if h['parataxis_supported'] or h['hypotaxis_supported'] else 'BHSA_NATIVE_NOT_COMPARABLE'
        elif not any(f['mother'] or f['rela'] not in (None,'','NA') or f['code'] is not None for f in facts):status='BHSA_NATIVE_NO_DATA'
        else:status='BHSA_NATIVE_NOT_COMPARABLE'
        out.append(dict(pair_id=p['pair_id'],comparison_status=status,native_facts=facts,
            method='EXACT_MOTHER_ENDPOINT_AND_DOCUMENTED_RELA_ONLY; TAB_PARGR_CODE_REPORTED_NOT_DECODED',blind_overwritten=False))
    return out


def placement(blind,cross,links):
    pairs=io.rows(blind['03_blind_candidate_pairs.csv']);hyp={r['pair_id']:r for r in io.rows(blind['04_blind_relation_hypotheses.csv'])};features=io.rows(blind['02_blind_linguistic_features.csv']);out=[]
    inventory=io.rows(blind['01_blind_target_inventory.csv']);link={r['audit_target_id']:r for r in links};byclause={int(r['clause_id']):r for r in features}
    for t in inventory:
        pp=[p for p in pairs if p['audit_target_id']==t['audit_target_id'] and p['target_role']=='TARGET_IS_LATER_CLAUSE'];hh=[hyp[p['pair_id']] for p in pp]
        para=any(h['parataxis_supported'] for h in hh);hypo=any(h['hypotaxis_supported'] for h in hh)
        node=link[t['audit_target_id']]['node_id']
        human=[r for r in cross if r['comparison_family']=='HYPOTAXIS' and ((r['historical_relation_type']=='CHILD_OF' and r['source_node']==node) or (r['historical_relation_type']=='HIERARCHICALLY_ABOVE' and r['target_node']==node))]
        already=any(r['comparison_status'] in COMPARISONS[:2] for r in human)
        # A proposal is not a placement decision; neither root nor mother is selected.
        first=min(int(byclause[n]['sequence_index']) for n in t['clause_id'])==0
        transition=any(set(byclause[n]['lexemes']) & {'TMM[','KLH[','CBT['} for n in t['clause_id']) and any(p['evidence_flags']['D_DOMAIN_SHIFT'] for p in pp)
        cat=PLACEMENTS[0] if first and not pp else PLACEMENTS[4] if para and hypo else PLACEMENTS[1] if hypo and already else PLACEMENTS[2] if hypo else PLACEMENTS[3] if para else PLACEMENTS[5] if transition else PLACEMENTS[6]
        out.append(dict(audit_target_id=t['audit_target_id'],canonical_node_id=node,reference=f"{t['chapter']}:{t['verse']}",placement_proposal=cat,
            parataxis_candidate_ids=[h['pair_id'] for h in hh if h['parataxis_supported']],hypotaxis_candidate_ids=[h['pair_id'] for h in hh if h['hypotaxis_supported']],
            prior_direct_mother_comparison_ids=[r['human_relation_id'] for r in human],proposal_status='UNREVIEWED',selected_mother='',selected_root=False,
            basis='BLIND_CANDIDATES_FIRST; JP2_ONLY_IS_POSTBLIND_HUMAN_COMPARISON_LABEL',historical_jin_record=link[t['audit_target_id']]['original_jin_record']))
    return out


def review_cases(blind):
    # Import the canonical review definition only in Phase B, after freeze.
    from milal_r3c_0_2_reviewability import REVIEW_FIELDS
    extra=('relation_decision','selected_mother_if_hypotactic','paratactic_peer_if_applicable','evidence_sufficient')
    hyp={r['pair_id']:r for r in io.rows(blind['04_blind_relation_hypotheses.csv'])};cases={}
    for p in io.rows(blind['03_blind_candidate_pairs.csv']):
        key=(int(p['preceding_clause_id']),int(p['later_clause_id']))
        r=cases.setdefault(key,dict(relation_case_id='JRC:'+str(key[0])+':'+str(key[1]),preceding_clause_id=key[0],later_clause_id=key[1],
            source_refs=[p['preceding_ref'],p['later_ref']],blind_pair_ids=[],audit_target_ids=[],blind_hypotheses=[],
            **{f:'UNREVIEWED' if f=='review_status' else '' for f in (*REVIEW_FIELDS,*extra)}))
        r['blind_pair_ids'].append(p['pair_id']);r['audit_target_ids'].append(p['audit_target_id']);r['blind_hypotheses'].append(hyp[p['pair_id']]['relation_hypothesis'])
    for r in cases.values():
        for key in ('blind_pair_ids','audit_target_ids','blind_hypotheses'):r[key]=sorted(set(r[key]))
    return [cases[k] for k in sorted(cases)]


def summary(m):
    cc=m['crosswalk'];pp=m['placements']
    return dict(blind=m['phase_a_meta']['summary'],human_paratactic_relations=sum(r['comparison_family']=='PARATAXIS' for r in cc),
        human_hypotactic_relations=sum(r['comparison_family']=='HYPOTAXIS' for r in cc),comparison={k:sum(r['comparison_status']==k for r in cc) for k in COMPARISONS},
        placement={k:sum(r['placement_proposal']==k for r in pp) for k in PLACEMENTS},native=dict(Counter(r['comparison_status'] for r in m['native_comparison'])),
        relation_review_cases=len(m['review_cases']),new_human_judgment_count=len(m['new_human_judgments']),new_accepted_structural_relation_count=len(m['new_relations']),new_parent_edge_count=len(m['new_parent_edges']))


def reports(m):
    blind=m['blind'];ff={int(r['clause_id']):r for r in io.rows(blind['02_blind_linguistic_features.csv'])};pairs={p['pair_id']:p for p in io.rows(blind['03_blind_candidate_pairs.csv'])}
    hyp={p['pair_id']:p for p in io.rows(blind['04_blind_relation_hypotheses.csv'])};native={p['pair_id']:p for p in m['native_comparison']}
    lines=['# Independent linguistic audit — researcher review','','No prior researcher relation was a discovery feature. All candidates remain UNADJUDICATED.',
        'Clause evidence does not automatically establish a macro-unit relation. Historical judgments are unchanged.','',
        'Readiness: BLOCKED_PENDING_BLIND_RELATION_HUMAN_REVIEW','', '```json',json.dumps(summary(m),ensure_ascii=False,indent=2),'```','',
        '## Revised questions — every answer blank / UNREVIEWED','']
    questions=['Does blind evidence support historical paratactic judgments?','Does blind evidence support historical hypotactic judgments?',
        'Should cases with differing blind evidence and historical judgment be reopened?',
        'Adopt paratactic and hypotactic placement as two basic textual-hierarchy relation types?',
        'Apply exactly-one-mother only to hypotactic daughters?',
        'Keep clause-to-macro projection subject to separate human adjudication?',
        'Leave root selection to a separate audit?']
    for i,q in enumerate(questions,1):lines += [f'RQ{i}. {q}','Review status: UNREVIEWED','Researcher answer:','']
    lines += ['## Historical relation comparisons','', 'All candidate IDs and raw features remain in CSV; no ranked winner is shown.','']
    for r in m['crosswalk']:
        if r['comparison_family']=='OUTSIDE_SCOPE':continue
        lines += ['### '+r['human_relation_id'],f"Historical: {r['source_ref']} → {r['target_ref']} / {r['historical_relation_type']} ({r['human_source_stage']})",'Comparison fact: '+r['comparison_status'],'Projection: '+r['projection_scope'],'']
        for ident in r['blind_candidate_ids']:
            p=pairs[ident];h=hyp[ident];left=ff[int(p['preceding_clause_id'])];right=ff[int(p['later_clause_id'])]
            lines += [f"- {ident}: {h['relation_hypothesis']}",f"  - Raw: {left['surface']} / {right['surface']}",
                f"  - Clause/atoms: {left['clause_id']} {left['clause_atom_ids']} / {right['clause_id']} {right['clause_atom_ids']}",
                '  - Observed/derived flags: '+json.dumps({k:v for k,v in p['evidence_flags'].items() if v},ensure_ascii=False),
                '  - P/H bundles: '+json.dumps(h['rule_bundles']),
                '  - Native post-blind: '+native[ident]['comparison_status']]
        lines += ['Competing candidate IDs: '+json.dumps(r['competing_candidates']),
            'review_status: UNREVIEWED','relation_decision:','selected_mother_if_hypotactic:','paratactic_peer_if_applicable:','evidence_sufficient:','additional_information_needed:','reviewer_notes:','']
    lines += ['## All neutral target projections','']
    target_inventory={r['audit_target_id']:r for r in io.rows(blind['01_blind_target_inventory.csv'])}
    for p in m['placements']:
        t=target_inventory[p['audit_target_id']]
        lines += [f"### {p['audit_target_id']} / {p['canonical_node_id']} / {p['reference']}",p['placement_proposal']+' — UNREVIEWED',
            'Raw target Hebrew: '+''.join(ff[c]['surface'] for c in t['clause_id']),
            'Clauses / atoms: '+json.dumps([t['clause_id'],t['clause_atom_id']]),
            'Historical necessity (comparison only): '+p['historical_jin_record']['historical_necessity'],
            'Historical function (comparison only): '+p['historical_jin_record']['structural_function'],
            'Parataxis candidates: '+json.dumps(p['parataxis_candidate_ids']),
            'Hypotaxis candidates: '+json.dumps(p['hypotaxis_candidate_ids']),
            'No mother assigned. Complete evidence/native comparisons are keyed by these IDs in 03/04/12.', '']
    lines += ['## Complete relation case list','',f"{len(m['review_cases'])} distinct ordered clause-pair cases in 21_relation_review_cases.csv; all occurrences retained by blind_pair_ids.",
        'All fields are UNREVIEWED/blank. This inventory is not an automatic KEEP/REVIEW directive or priority ranking.']
    scope=['# Next human adjudication scope','',f"Complete unranked eligible relation-case inventory: {len(m['review_cases'])} rows in 21_relation_review_cases.csv.",
        f"Historical comparisons: {sum(r['comparison_family']!='OUTSIDE_SCOPE' for r in m['crosswalk'])}; neutral textual-locus projections: {len(m['placements'])}.",
        'Review the evidence and competing arrangements before choosing any relation or hypotactic mother. No candidate has been selected by the audit.',
        'Root, macro projection and RQ1–RQ7 remain undecided. Participant arc UNADJUDICATED. R4.4 consumer NOT IMPLEMENTED.']
    return {'14_revised_contract_review_packet.md':('\n'.join(lines)+'\n').encode(),'16_next_human_adjudication_scope.md':('\n'.join(scope)+'\n').encode()}


def load(blind_path,archive_path,config_path,native_path=None,synthetic=False):
    # Order is intentional and tested: no config/human archive/native read precedes freeze verification.
    blind=io.read_dir(Path(blind_path));io.require(io.manifest_ok(blind,'07_blind_discovery_manifest.csv'),'blind output must be frozen before Phase B')
    frozen=io.sha(blind['07_blind_discovery_manifest.csv']);events=['BLIND_FREEZE_VERIFIED']
    cfg=json.loads(Path(config_path).read_bytes());data=Path(archive_path).read_bytes();events.append('HUMAN_ARCHIVE_OPENED')
    if not synthetic:io.require(io.sha(data)==cfg['archive']['sha256'],'JIN.0.1 archive SHA256')
    history=io.archive(data);io.require(io.manifest_ok(history),'JIN.0.1 manifest')
    meta=json.loads(blind['18_phase_a_metadata.json']);io.require(meta['human_source_count']==meta['native_hierarchy_source_count']==0,'blind source leakage')
    prepared,_=neutral_targets(history);inventory=io.rows(blind['01_blind_target_inventory.csv'])
    io.require([(t['audit_target_id'],t['book'],str(t['chapter']),str(t['verse'])) for t in prepared]==[(t['audit_target_id'],t['book'],t['chapter'],t['verse']) for t in inventory],'neutral inventory not exact projection')
    cross,links=compare(blind,history)
    features=io.rows(blind['02_blind_linguistic_features.csv']);nodes={int(c['clause_id']) for c in features}|{n for c in features for n in c['clause_atom_ids']}
    native={};native_sources=[]
    if native_path:
        events.append('NATIVE_HIERARCHY_OPENED_AFTER_BLIND_FREEZE')
        for name in io.NATIVE_FEATURES:
            native[name],receipt=io.read_tf(Path(native_path)/(name+'.tf'),keep=nodes);native_sources.append(receipt)
    else:io.require(synthetic,'real native feature path required')
    m=dict(blind=blind,historical=history,phase_a_meta=meta,freeze_sha256=frozen,events=events,
        crosswalk=cross,links=links,native=native,native_sources=native_sources,native_comparison=native_comparison(blind,native),
        placements=placement(blind,cross,links),review_cases=review_cases(blind),
        new_human_judgments=[],new_relations=[],new_parent_edges=[],participant_arc='UNADJUDICATED',consumer_implemented=False,
        phase_b_sources=[dict(source='JIN.0.1 ZIP',sha256=io.sha(data),path=str(Path(archive_path).resolve()))]+[dict(source=r['feature']+'.tf',sha256=r['sha256'],path=str((Path(native_path)/(r['feature']+'.tf')).resolve())) for r in native_sources])
    m['reports']=reports(m);return m,cfg


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--blind',required=True);p.add_argument('--archive',required=True);p.add_argument('--config',required=True)
    p.add_argument('--tf-data');p.add_argument('--synthetic',action='store_true');p.add_argument('--out',required=True);args=p.parse_args(argv)
    m,cfg=load(args.blind,args.archive,args.config,args.tf_data,args.synthetic)
    # Validation and final publication are imported only after blind freeze and comparison.
    from milal_jin_audit_pipeline import finalize
    files=finalize(m,cfg,args.synthetic);io.require(io.read_dir(Path(args.blind))==m['blind'],'Phase B mutated Phase A')
    zp=io.publish(files,args.out)
    print(json.dumps(dict(phase='B',loaded_source_files=m['phase_b_sources'],freeze_sha256=m['freeze_sha256'],zip_sha256=io.sha(zp.read_bytes()),summary=summary(m)),ensure_ascii=False))
    return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
