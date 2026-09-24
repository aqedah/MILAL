"""S: raw strict candidates, never human hierarchy or macro-audit input."""
from collections import Counter, defaultdict
import milal_jin_io as io
import milal_jin_relation_rules as rr
import milal_jin_top_level_common as common


def build(raw,ling,rules):
    ff=common.features(raw,ling);signals=common.signals(ff,rules)
    form_index=defaultdict(set);formula_index=defaultdict(set);relations=[];incoming=defaultdict(list);peers=defaultdict(list)
    for i,c in enumerate(ff):
        # All local predecessors are examined for explicit dependencies; none is preferred.
        # Global formal indices preserve every predecessor capable of satisfying P1.
        options=set(range(max(0,i-ling['local_dependency_clause_window']),i))
        for w in c['verbal_words']:options|=form_index[(w['lex'],w['vs'],w['vt'])]
        for family in c['formula_atoms']:options|=formula_index[family]
        for j in sorted(options):
            pre=ff[j];ev=rr.evidence(pre,c,ling)
            if not ev['eligible']:continue
            local=bool(ev['evidence_flags']['S_RELATIVE_CONSTRUCTION'] or ev['evidence_flags']['S_INFINITIVE_DEPENDENCY'])
            kind='STRICT_HYPOTAXIS_AND_PARATAXIS_COMPETE' if ev['hypotaxis_supported'] and ev['parataxis_supported'] else 'STRICT_LOCAL_DEPENDENCY' if local else 'STRICT_HYPOTAXIS_CANDIDATE' if ev['hypotaxis_supported'] else 'STRICT_PARATAXIS_CANDIDATE' if ev['parataxis_supported'] else 'STRICT_PLACEMENT_INSUFFICIENT'
            r=dict(candidate_relation_id=f'SR:{pre["clause_id"]}:{c["clause_id"]}',preceding_clause_id=pre['clause_id'],later_clause_id=c['clause_id'],
                preceding_ref=pre['reference'],later_ref=c['reference'],candidate_kind=kind,candidate_trigger=ev['trigger_reason_codes'],evidence_bundle=ev,
                explicit_local_dependency=local,clause_internal_dependency=bool(local and set(pre['clause_atom_ids'])&set(c['clause_atom_ids'])),
                status='UNADJUDICATED',automatic_resolution=False,selected_mother='',limitations='Local reference compatibility is not identity; possible dependency is not accepted daughterhood.')
            relations.append(r)
            if ev['hypotaxis_supported']:incoming[c['clause_id']].append(r)
            if ev['parataxis_supported']:peers[c['clause_id']].append(r);peers[pre['clause_id']].append(r)
        for w in c['verbal_words']:form_index[(w['lex'],w['vs'],w['vt'])].add(i)
        for family in c['formula_atoms']:formula_index[family].add(i)
    fam=common.families(ff,range(len(ff)),rules,'SF');fam_by=defaultdict(list)
    for f in fam:
        for cid in f['member_clause_ids']:fam_by[cid].append(f['family_id'])
    top=[];dispositions=[]
    for c,s in zip(ff,signals):
        cid=c['clause_id'];inc=incoming[cid];para=peers[cid]
        explicit=any(r['explicit_local_dependency'] for r in inc)
        frame=bool(s['domain_transition'] or (c['domain']=='N' and (s['speech_formula'] or s['wayhi_time'] or s['wayx_frame'] or s['explicit_participant_introduction'])) or (s['temporal_frame'] and c['main_clause_compatible']))
        high_para=bool(para and fam_by[cid] and (frame or c['domain']=='N'))
        retain=not explicit and bool(s['book_scope_initial'] or frame or high_para)
        kinds=[]
        if s['book_scope_initial']:kinds.append('S_SCOPE_INITIAL_CANDIDATE')
        if high_para:kinds.append('S_TOP_PARATACTIC_CANDIDATE')
        if frame and not inc:kinds.append('S_TOP_UNEMBEDDED_CANDIDATE')
        if not kinds or (inc and not high_para):kinds.append('S_TOP_LEVEL_INSUFFICIENT')
        dispositions.append(dict(clause_id=cid,reference=c['reference'],explicit_local_dependency_candidate=explicit,
            main_line_surface_frame=frame,retained_for_top_level_review=retain,candidate_kinds=kinds,
            hypotaxis_candidate_ids=[r['candidate_relation_id'] for r in inc],parataxis_candidate_ids=[r['candidate_relation_id'] for r in para],
            exclusion_reason='EXPLICIT_LOCAL_DEPENDENCY_CANDIDATE' if explicit else '' if retain else 'NO_POSITIVE_BROAD_FRAME_BUNDLE; NO_MOTHER_ALONE_IS_INSUFFICIENT',automatic_resolution=False))
        if retain:
            ps=[r['preceding_clause_id'] if r['later_clause_id']==cid else r['later_clause_id'] for r in para]
            cs=[r['preceding_clause_id'] for r in inc]
            deps=[r['later_clause_id'] for r in relations if r['preceding_clause_id']==cid and r['explicit_local_dependency']]
            row=common.candidate(c,'STC'+str(len(top)+1).zfill(4),kinds,s,sorted(set(ps)),sorted(set(cs)),
                dict(candidate_coverage_start=c['word_start'],candidate_coverage_end_if_observable=max([c['word_end']]+[x['word_end'] for x in ff if x['clause_id'] in deps]),candidate_coverage_basis='EXPLICIT_LOCAL_CANDIDATE_DEPENDENCIES_ONLY',covered_clause_ids=[cid]+deps))
            row['formal_family']=fam_by[cid];top.append(row)
    hypothesis=[];topids={r['clause_id'] for r in top}
    peer_pairs=[r for r in relations if r['evidence_bundle']['parataxis_supported'] and r['preceding_clause_id'] in topids and r['later_clause_id'] in topids]
    if peer_pairs:hypothesis.append(dict(configuration='S_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_CANDIDATES',candidate_ids=sorted({r['candidate_id'] for r in top if any(r['clause_id'] in (p['preceding_clause_id'],p['later_clause_id']) for p in peer_pairs)}),evidence_ids=[r['candidate_relation_id'] for r in peer_pairs],status='UNADJUDICATED',selected=False,limitations='Pairwise candidate parataxis is not an accepted whole-book top-level relation.'))
    # One candidate can govern all remaining clauses only as an explicit candidate hypothesis.
    for t in top:
        covered={r['later_clause_id'] for r in relations if r['preceding_clause_id']==t['clause_id'] and r['explicit_local_dependency']}
        if covered and covered|{t['clause_id']}=={c['clause_id'] for c in ff}:
            t['candidate_kind'].append('S_UNIQUE_ROOT_CANDIDATE_POSSIBLE')
            hypothesis.append(dict(configuration='S_CONFIG_ONE_UNIQUE_ROOT_CANDIDATE',candidate_ids=[t['candidate_id']],evidence_ids=[r['candidate_relation_id'] for r in relations if r['preceding_clause_id']==t['clause_id'] and r['explicit_local_dependency']],status='UNADJUDICATED',selected=False,limitations='Direct dependency candidates cover this scope; still requires human adjudication.'))
    hypothesis.append(dict(configuration='S_CONFIG_INSUFFICIENT',candidate_ids=[r['candidate_id'] for r in top],evidence_ids=[],status='UNADJUDICATED',selected=False,limitations='Unique root is not established; book-scope initial position and missing mothers do not entail root status.'))
    internal=[dict(clause_id=c['clause_id'],clause_atom_ids=c['clause_atom_ids'],reference=c['reference'],
        finite_word_nodes=[w['node'] for w in c['finite_verbal_words']],dependent_word_nodes=c['infinitive_words'],
        candidate_kind='STRICT_LOCAL_DEPENDENCY',scope='WITHIN_ONE_ACTUAL_CLAUSE',status='UNADJUDICATED',
        automatic_resolution=False,limitations='Finite and infinitive constituents within one clause; no clause-to-clause mother edge inferred.')
        for c in ff if c['finite_verbal_words'] and c['infinitive_words']]
    model=dict(inventory=ff,relations=relations,top=top,hypotheses=hypothesis,dispositions=dispositions,families=fam,internal=internal)
    files={'01_strict_clause_inventory.csv':io.csv_bytes(ff),'02_strict_relation_candidates.csv':io.csv_bytes(relations),
        '03_strict_top_level_candidates.csv':io.csv_bytes(top),'04_strict_top_level_configuration_hypotheses.csv':io.csv_bytes(hypothesis),
        '05_strict_candidate_evidence.csv':io.csv_bytes(dispositions),'s_formal_families.csv':io.csv_bytes(fam),'s_model.json':io.js(model),
        's_clause_internal_observations.csv':io.csv_bytes(internal,['clause_id','clause_atom_ids','reference','finite_word_nodes','dependent_word_nodes','candidate_kind','scope','status','automatic_resolution','limitations'])}
    return dict(files=files,model=model,summary=dict(total_clauses=len(ff),retained_relations=len(relations),explicit_local_hypotaxis=sum(r['explicit_local_dependency'] for r in relations),parataxis=sum(r['evidence_bundle']['parataxis_supported'] for r in relations),top_level_candidates=len(top),configuration_counts=dict(Counter(r['configuration'] for r in hypothesis))))


if __name__=='__main__':common.freeze_main('S',build)
