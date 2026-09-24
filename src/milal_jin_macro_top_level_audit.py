"""M: independent raw macro evidence, no strict audit or human structure input."""
from collections import defaultdict
from itertools import combinations
import milal_jin_io as io
import milal_jin_top_level_common as common


def build(raw,ling,rules):
    ff=common.features(raw,ling);ss=common.signals(ff,rules);onsets=[];closures=[];markers=[]
    onsetkeys=('speech_formula','repeated_formula_atom','wayhi_time','wayx_frame','temporal_frame','locative_frame','explicit_participant_introduction','explicit_subject_shift','domain_transition','speech_addition')
    for i,(c,s) in enumerate(zip(ff,ss)):
        triggers=[k for k,v in s.items() if v]
        markers.append(dict(marker_id='MM'+str(i+1).zfill(4),clause_id=c['clause_id'],clause_atom_ids=c['clause_atom_ids'],reference=c['reference'],surface=c['surface'],raw_flags=s,formal=common.formal(c),status='AUDIT_OBSERVATION_ONLY'))
        if s['book_scope_initial'] or any(s[k] for k in onsetkeys):
            onsets.append(dict(onset_id='MO'+str(len(onsets)+1).zfill(4),clause_id=c['clause_id'],reference=c['reference'],index=i,triggers=triggers,status='M_ONSET_CANDIDATE',accepted_boundary=False))
        if s['closure_lexeme'] or s['domain_transition_after'] or s['terminal_lexeme'] or s['book_scope_terminal']:
            closures.append(dict(closure_id='MC'+str(len(closures)+1).zfill(4),clause_id=c['clause_id'],reference=c['reference'],index=i,triggers=triggers,status='M_CLOSURE_CANDIDATE' if s['closure_lexeme'] or s['domain_transition_after'] else 'M_HIGHER_TERMINAL_EFFECT_CANDIDATE' if s['terminal_lexeme'] else 'M_CLOSURE_INSUFFICIENT',accepted_boundary=False))
    families=common.families(ff,[r['index'] for r in onsets],rules,'MF');fam_by=defaultdict(list);peers=defaultdict(set);relations=[]
    for fam in families:
        for cid in fam['member_clause_ids']:fam_by[cid].append(fam['family_id'])
        for ai,bi in combinations(fam['member_indices'],2):
            a,b=ff[ai],ff[bi];peers[a['clause_id']].add(b['clause_id']);peers[b['clause_id']].add(a['clause_id'])
            relations.append(dict(relation_candidate_id=f'MR:P:{a["clause_id"]}:{b["clause_id"]}',source_clause_id=a['clause_id'],target_clause_id=b['clause_id'],candidate_kind='M_MACRO_PARATAXIS_POSSIBLE',
                evidence_bundle=dict(repeated_family=fam['family_id'],ordered_multi_clause_signature=fam['signature'],participant_surfaces=[a['participant_surfaces'],b['participant_surfaces']],formula_expansion=[len(a['word_nodes']),len(b['word_nodes'])]),
                status='UNADJUDICATED',selected_mother='',automatic_resolution=False,limitations='Repeated configuration may be local; correspondence does not establish a macro level.'))
    containers=defaultdict(list);cover={};window=rules['context_clause_count']
    for onset in onsets:
        i=onset['index'];a=ff[i];s=ss[i];cid=a['clause_id']
        later_equiv=[j for fam in families if cid in fam['member_clause_ids'] for j in fam['member_indices'] if j>i]
        end=min(later_equiv) if later_equiv else None
        cover[cid]=dict(candidate_coverage_start=a['word_start'],candidate_coverage_end_if_observable=ff[end]['word_start']-1 if end is not None else None,
            candidate_coverage_basis='UNTIL_NEXT_EXACT_REPEATED_FORMAL_SEQUENCE' if end is not None else 'NO_CLOSED_COVERAGE_OBSERVED',next_equivalent_clause_id=ff[end]['clause_id'] if end is not None else None)
        if end is None or not fam_by[cid] or not (s['temporal_frame'] or s['locative_frame'] or s['domain_transition']):continue
        outer=ff[i:i+window];outer_domains={c['domain'] for c in outer};outer_people={p for c in outer for p in c['participant_surfaces']}
        endings=[c for c in closures if i<c['index']<end]
        for inner in onsets:
            j=inner['index']
            if not i<j<end:continue
            b=ff[j];internal=ff[j:j+window];shared_people=outer_people&{p for c in internal for p in c['participant_surfaces']}
            shared_domains=outer_domains&{c['domain'] for c in internal}
            asym=bool((s['temporal_frame'] and not ss[j]['temporal_frame']) or (s['locative_frame'] and not ss[j]['locative_frame']) or (ss[j]['speech_formula'] and not s['speech_formula']))
            compatible=[r for r in endings if r['index']>=j]
            if not (shared_people and shared_domains and asym and compatible):continue
            containers[b['clause_id']].append(cid)
            relations.append(dict(relation_candidate_id=f'MR:C:{cid}:{b["clause_id"]}',source_clause_id=cid,target_clause_id=b['clause_id'],candidate_kind='M_MACRO_CONTAINMENT_POSSIBLE',
                evidence_bundle=dict(repeated_distribution=fam_by[cid],next_equivalent_onset=ff[end]['clause_id'],nested_onset=inner['onset_id'],internal_asymmetry=asym,
                    participant_surface_recurrence=sorted(shared_people),domain_containment=sorted(shared_domains),compatible_closure_ids=[r['closure_id'] for r in compatible]),
                status='UNADJUDICATED',selected_mother='',automatic_resolution=False,limitations='Distribution, nesting, asymmetry, recurrence and closure form a candidate bundle; no mother accepted.'))
    top=[];evidence=[]
    for onset in onsets:
        i=onset['index'];c=ff[i];s=ss[i];cid=c['clause_id']
        broad=bool(s['wayhi_time'] or (s['domain_transition'] and c['domain']=='N') or (c['domain']=='N' and (s['speech_formula'] or s['wayx_frame'] or s['temporal_frame'] or s['explicit_participant_introduction'])))
        repeated_broad=bool(fam_by[cid] and (broad or s['speech_addition']))
        retain=bool(s['book_scope_initial'] or broad or repeated_broad)
        onset['status']='M_ONSET_REPEATED_FAMILY_CANDIDATE' if fam_by[cid] else 'M_ONSET_CANDIDATE' if broad else 'M_LOCAL_ONLY_ONSET'
        evidence.append(dict(onset_id=onset['onset_id'],clause_id=cid,reference=c['reference'],broad_scope_bundle=broad,repeated_formal_families=fam_by[cid],retained_top_level=retain,
            possible_containers=containers[cid],reason='POSITIVE_FRAME_OR_REPEATED_CONFIGURATION' if retain else 'M_MACRO_PROJECTION_INSUFFICIENT',limitations='No-containing-candidate alone does not establish root.'))
        if not retain:continue
        kinds=[]
        if s['book_scope_initial']:kinds.append('M_SCOPE_INITIAL_CANDIDATE')
        if repeated_broad:kinds.append('M_TOP_PARATACTIC_CANDIDATE')
        if broad and not containers[cid]:kinds.append('M_TOP_UNCONTAINED_CANDIDATE')
        if containers[cid] or not broad:kinds.append('M_TOP_LEVEL_INSUFFICIENT')
        row=common.candidate(c,'MTC'+str(len(top)+1).zfill(4),kinds,s,sorted(peers[cid]),sorted(set(containers[cid])),cover[cid]);row['formal_family']=fam_by[cid];top.append(row)
    hypotheses=[];topids={r['clause_id'] for r in top}
    pairs=[r for r in relations if r['candidate_kind']=='M_MACRO_PARATAXIS_POSSIBLE' and r['source_clause_id'] in topids and r['target_clause_id'] in topids]
    if pairs:hypotheses.append(dict(configuration='M_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_UNITS',candidate_ids=[r['candidate_id'] for r in top if peers[r['clause_id']]&topids],evidence_ids=[r['relation_candidate_id'] for r in pairs],status='UNADJUDICATED',selected=False,limitations='Exact repeated configurations, not accepted peer levels.'))
    # Beginning/end are observations, not a hard-coded whole-book span or a root.
    first=ff[0];last=ff[-1];initial_run=[]
    for c in ff:
        if c['domain']!=first['domain']:break
        initial_run.append(c)
    terminal_run=[]
    for c in reversed(ff):
        if c['domain']!=last['domain']:break
        terminal_run.append(c)
    opening_people={p for c in initial_run for p in c['participant_surfaces']};closing_people={p for c in terminal_run for p in c['participant_surfaces']}
    opening_form={w['lex'] for c in initial_run for w in c['verbal_words']};closing_form={w['lex'] for c in terminal_run for w in c['verbal_words']}
    separate=bool(initial_run and terminal_run and initial_run[-1]['word_end']<terminal_run[-1]['word_start'])
    frame=dict(candidate_kind='WHOLE_BOOK_FRAME_CANDIDATE' if separate and first['domain']==last['domain']=='N' and opening_people&closing_people and opening_form&closing_form else 'M_RELATION_INSUFFICIENT',
        opening_clause_ids=[c['clause_id'] for c in initial_run],closing_clause_ids=[c['clause_id'] for c in reversed(terminal_run)],shared_participant_surfaces=sorted(opening_people&closing_people),shared_verbal_lexemes=sorted(opening_form&closing_form),
        raw_domain_recurrence=separate and first['domain']==last['domain'],span_created=False,root_selected=False,status='UNADJUDICATED',limitations='Separated raw domain runs and surface recurrence support a frame hypothesis, not an accepted whole-book span or a unique root.')
    if frame['candidate_kind']=='WHOLE_BOOK_FRAME_CANDIDATE':
        top[0]['candidate_kind'].append('M_HIGHER_FRAME_CANDIDATE');top[0]['closure_correspondence']=[frame]
        hypotheses.append(dict(configuration='M_CONFIG_ONE_HIGHER_MACRO_FRAME',candidate_ids=[top[0]['candidate_id']],evidence_ids=['M_FRAME_OBSERVATION'],status='UNADJUDICATED',selected=False,limitations=frame['limitations']))
    hypotheses.append(dict(configuration='M_CONFIG_INSUFFICIENT',candidate_ids=[r['candidate_id'] for r in top],evidence_ids=[],status='UNADJUDICATED',selected=False,limitations='No unique root established; broad coverage does not select a winner.'))
    model=dict(markers=markers,onsets=onsets,closures=closures,families=families,relations=relations,top=top,hypotheses=hypotheses,evidence=evidence,frame=frame)
    files={'08_macro_marker_inventory.csv':io.csv_bytes(markers),'09_macro_onset_candidates.csv':io.csv_bytes(onsets),'10_macro_closure_candidates.csv':io.csv_bytes(closures),
       '11_macro_relation_candidate_families.csv':io.csv_bytes(relations),'12_macro_top_level_candidates.csv':io.csv_bytes(top),'13_macro_top_level_configuration_hypotheses.csv':io.csv_bytes(hypotheses),
       '14_macro_candidate_evidence.csv':io.csv_bytes(evidence),'m_repeated_families.csv':io.csv_bytes(families),'m_frame_observation.json':io.js(frame),'m_model.json':io.js(model)}
    return dict(files=files,model=model,summary=dict(raw_clauses=len(ff),raw_marker_observations=sum(any(v for k,v in r['raw_flags'].items() if k not in ('book_scope_initial','book_scope_terminal')) for r in markers),onsets=len(onsets),closures=len(closures),repeated_families=len(families),relation_candidates=len(relations),top_level_candidates=len(top),configuration_hypotheses=[r['configuration'] for r in hypotheses]))


if __name__=='__main__':common.freeze_main('M',build)
