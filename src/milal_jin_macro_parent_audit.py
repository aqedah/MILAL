"""C: all preceding neutral locus scans with strict local dependencies separated."""
import milal_jin_io as io
import milal_jin_relation_rules as rr
from milal_jin_focused_common import macro_hypothesis,table


def build(e,blind):
    out=[];excluded=[];targets=[];summaries={};reports={}
    oldpairs=io.rows(blind['03_blind_candidate_pairs.csv']);hyps={r['pair_id']:r for r in io.rows(blind['04_blind_relation_hypotheses.csv'])}
    for ref in e.rules['c_targets']:
        cur=e.head(ref);target=next(t for t in e.targets if int(t['chapter'])==cur['chapter'] and int(t['verse'])==cur['verse'])
        local=[]
        for p in oldpairs:
            h=hyps[p['pair_id']]
            if p['audit_target_id']!=target['audit_target_id'] or not h['hypotaxis_supported']:continue
            a,b=int(p['preceding_clause_id']),int(p['later_clause_id']);fresh=rr.evidence(e.byid[a],e.byid[b],e.linguistic)
            io.require(fresh['hypotaxis_supported'] and fresh['rule_bundles']==h['rule_bundles'],'frozen local hypothesis recomputation')
            scope=e.local_pair(e.byid[a],e.byid[b],p['pair_id'])
            local.append(dict(target_ref=ref,pair_id=p['pair_id'],source_pair=p,source_hypothesis=h,recomputed_evidence=fresh,scope=scope,excluded_from_macro=scope['clause_internal_only'] or not scope['aligned_locus_heads'],reason='LOCAL_DEPENDENCY_NOT_MACRO_TARGET_ANCHOR' if scope['clause_internal_only'] or not scope['aligned_locus_heads'] else 'SEPARATE_STRICT_PAIR_REVIEW_REQUIRED'))
        excluded.extend(local);scanned=[]
        near=e.features[max(0,cur['sequence_index']-3):cur['sequence_index']]
        for prior in e.targets:
            head=e.byid[e.ctx.head[prior['audit_target_id']]]
            if head['word_start']>=cur['word_start']:continue
            ev=e.pair(head,cur);r=e.resumption([e.byid[i] for i in prior['clause_id']],[e.byid[i] for i in target['clause_id']],near)
            h=macro_hypothesis(ev,r,head['main_clause_compatible'],cur['main_clause_compatible'])
            scanned.append(dict(candidate_id='FC:'+prior['audit_target_id']+':'+target['audit_target_id'],target_ref=ref,preceding_locus=prior['audit_target_id'],target_locus=target['audit_target_id'],preceding_ref=head['reference'],preceding_clause_id=head['clause_id'],target_clause_id=cur['clause_id'],scope='MACRO_ANCHOR_COMPARISON_NOT_ACCEPTED_RELATION',evidence=ev,resumption=r,**h))
        multiple=sum(r['macro_mother_supported'] for r in scanned)>1
        for r in scanned:
            if multiple and r['macro_mother_supported']:r['hypotheses'].append('C_MULTIPLE_MACRO_CANDIDATES')
        out.extend(scanned);targets.append(dict(reference=ref,neutral_locus=target['audit_target_id'],clause_ids=target['clause_id'],head_clause_id=cur['clause_id'],selected_mother='',status='UNADJUDICATED'))
        ss=dict(scanned=len(scanned),retained=sum(r['retained'] for r in scanned),macro_mother_candidates=sum(r['macro_mother_supported'] for r in scanned),strict_pairs=len(local),excluded_local_pairs=sum(r['excluded_from_macro'] for r in local),internal_pairs=sum(r['scope']['clause_internal_only'] for r in local),cross_locus_pairs=sum(r['scope']['cross_locus'] for r in local));summaries[ref]=ss
        report='# C — '+ref+' macro parent evidence\n\n'+str(ss)+'\n\n'+('NO_MACRO_MOTHER_FOUND' if not ss['macro_mother_candidates'] else 'UNADJUDICATED_MACRO_MOTHER_CANDIDATES')+'\n\n'
        report+=table([dict(Candidate=r['candidate_id'],Ref=r['preceding_ref'],Retained=r['retained'],Hypotheses=r['hypotheses'],Limitations=r['evidence']['limitations']) for r in scanned],['Candidate','Ref','Retained','Hypotheses','Limitations'])
        report+='\n## Strict local candidates and exclusions\n\n'+str(local)+'\n\nNo local subordinate clause is promoted to a macro target. All previous neutral loci were scanned without a nearest-locus choice.\n'
        reports[ref]=report
    return dict(files={'09_macro_parent_targets.csv':io.csv_bytes(targets),'10_macro_parent_candidate_inventory.csv':io.csv_bytes(out),'11_macro_parent_local_exclusions.csv':io.csv_bytes(excluded),'12_job_2_11_macro_parent_report.md':reports[e.rules['c_targets'][0]].encode(),'13_job_32_1_macro_parent_report.md':reports[e.rules['c_targets'][1]].encode()},summary=summaries)
