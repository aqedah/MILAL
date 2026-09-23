"""HSA3-ANA.0.1: surface constructions and unadjudicated response-frame hypotheses."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import zipfile

import milal_hsa3_prep_global_seams as prep
import milal_mr1_surface_marker_provenance as mr1

ROOT,sha,canonical = prep.ROOT,prep.sha,prep.canonical
CONFIG=ROOT/'config/hsa3_ana_job.json'
FEATURES=('lex','lex_utf8','lex0','gloss','root','g_word_utf8','sp','pdp','vt','vs','ps','gn','nu','prs_ps','prs_gn','prs_nu','st','nametype')
EXTRA_FEATURES=('gloss','lex0','mother','rela','code')
REPORTS=('07_job_31_40_postclosure_audit.md','08_ana_response_frame_review_packet.md')
CLASSES=('FORMULAIC_CSF','DIALOGUE_TURN_CSF','DIRECTED_ANA_CSF','RESPONSE_REQUEST',
         'ANSWERING_CESSATION','SELF_DECLARED_RESPONSE','NEGATED_OR_WITHHELD_RESPONSE',
         'OTHER_ANA','NON_ANSWER_HOMONYM','FIRST_PERSON_RESPONSE_PROSPECT','FIRST_PERSON_DIRECTED_RESPONSE')


def require(ok,message):
    if not ok:raise ValueError('HSA3-ANA.0.1 STOP: '+message)


def native_bhsa(path):
    """Reuse frozen version-checked loader; add lexical/syntactic evidence only."""
    cfg=json.loads(mr1.CONFIG.read_bytes())
    b,execution=mr1.load_bhsa(path,cfg)
    path=Path(path).resolve()
    for feature in EXTRA_FEATURES:
        fp=path/(feature+'.tf')
        require(fp.is_file(),'missing BHSA feature '+feature)
        header=fp.read_text(encoding='utf-8').split('\n\n',1)[0]
        require('@version=2021' in header.splitlines(),'BHSA feature version '+feature)
        execution['feature_versions'][feature]='2021'
    require(b.T.api.TF.load(' '.join(EXTRA_FEATURES),add=True,silent='deep'),'additional TF features')
    api=b.T.api.TF.api;b.F=api.F
    clauses=[]
    for c in b.clauses:
        words=[]
        for w in b.words(c):
            secw=b.section(w)
            words.append(dict(node=w,reference=f'{secw[1]}:{secw[2]}',surface=api.T.text((w,)),clause_atom_ids=list(api.L.u(w,otype='clause_atom')),
                phrase_ids=list(api.L.u(w,otype='phrase')),**{f:getattr(api.F,f).v(w) for f in FEATURES}))
        phrases=[dict(node=p,function=api.F.function.v(p),type=api.F.typ.v(p),word_nodes=list(api.L.d(p,otype='word')),
                      surface=api.T.text(api.L.d(p,otype='word'))) for p in api.L.d(c,otype='phrase')]
        sec=b.section(c)
        clauses.append(dict(clause=c,ref=f'{sec[1]}:{sec[2]}',chapter=sec[1],verse=sec[2],
            surface=api.T.text(b.words(c)),clause_atom_ids=b.down(c,'clause_atom'),words=words,phrases=phrases,
            type=api.F.typ.v(c),domain=api.F.domain.v(c),rela=api.F.rela.v(c),code=api.F.code.v(c),
            bhsa_mother_nodes=list(api.E.mother.f(c))))
    all_words=list(api.L.d(execution['book_node'],otype='word'))
    require(sorted(w['node'] for c in clauses for w in c['words'])==all_words,'whole-book word/clause coverage')
    for name,f in api.TF.features.items():
        if f.dataLoaded and (path/(name+'.tf')).is_file():
            execution['data_hashes'][str(path/(name+'.tf'))]=sha((path/(name+'.tf')).read_bytes())
    execution['book_word_nodes']=all_words
    return clauses,execution


def load(tf_data=None,self_test=False):
    cfg=json.loads(CONFIG.read_bytes())
    frozen=prep.r43.frozen_receipts(cfg)
    require(all(r['actual']==r['expected'] for r in frozen),'frozen baseline changed')
    prior=prep.load(self_test)
    if self_test:
        files=prep.serialize(prep.build(prior),prior)
        from milal_hsa3_ana_synthetic import fixture
        native,execution,csf=fixture(prior)
        inputs=[]
    else:
        require(tf_data is not None,'--tf-data required for actual BHSA audit')
        pin=cfg['archive'];a=prep.r43.h1.src.archive((ROOT/pin['path']).read_bytes(),pin['sha256'],mr1=True)
        files=a['files'];meta=json.loads(files['90_run_metadata.json'])
        require(meta['version']=='HSA3-PREP' and meta['mode']=='ACCEPTED_REAL_REVIEW_ONLY' and meta['status']=='PASS','unaccepted HSA3-PREP')
        require(all(g['status']=='PASS' for g in prep.decode_rows(files['08_gates.csv'])),'HSA3-PREP gates')
        require({k.removeprefix('history/r4_3/'):v for k,v in files.items() if k.startswith('history/r4_3/')}==prior['files'],'nested R4.3 mismatch')
        inputs=deepcopy(prior['receipts'])+[dict(role='hsa3_prep',path=pin['path'],expected=pin['sha256'])]
        mr_pin=json.loads(prep.r43.h1.CONFIG.read_bytes())['archives']['mr1']
        mr=prep.r43.h1.src.archive((ROOT/mr_pin['path']).read_bytes(),mr_pin['sha256'],mr1=True)
        csf=prep.decode_rows(mr['files']['02_csf_reproduction.csv'])
        native,execution=native_bhsa(tf_data)
    s=dict(cfg=cfg,prior=prior,files=files,frozen=frozen,inputs=inputs,native=native,execution=execution,csf=csf,
           mode='SYNTHETIC_AUDIT_ONLY' if self_test else 'REAL_BHSA_2021_AUDIT')
    validate_source(s)
    return s


def validate_source(s):
    ids=[c['clause'] for c in s['native']]
    require(len(ids)==len(set(ids)) and ids,'clause identity')
    words=[w['node'] for c in s['native'] for w in c['words']]
    require(len(words)==len(set(words)) and sorted(words)==s['execution']['book_word_nodes'],'whole-book coverage')
    for c in s['native']:
        require(all(k in c for k in ('type','domain','rela','code','bhsa_mother_nodes','phrases')),'missing clause schema')
        require(all(all(k in w for k in FEATURES+('node','reference','clause_atom_ids','phrase_ids','surface')) for w in c['words']),'missing word schema')


def by_id(s):return {c['clause']:c for c in s['native']}
def lexes(c):return {w['lex'] for w in c['words']}
def phrase_records(c,function):
    ww={w['node']:w for w in c['words']}
    return [dict(phrase=p['node'],function=p['function'],surface=p['surface'],words=[ww[w] for w in p['word_nodes']]) for p in c['phrases'] if p['function']==function]


def ancestors(c,cc):
    todo=[c['clause']];seen=set();out=[]
    while todo:
        ident=todo.pop(0)
        if ident in seen:continue
        seen.add(ident)
        for parent in cc[ident]['bhsa_mother_nodes']:
            # BHSA sometimes points to phrases: preserve raw edge, do not guess a clause.
            if parent in cc and parent not in seen:
                out.append(cc[parent]);todo.append(parent)
    return out


def formula(c,following,s):
    rules=s['cfg']['rules']
    verbs=[w for w in c['words'] if w['sp']=='verb']
    next_verbs=[w for w in following['words'] if w['sp']=='verb'] if following else []
    return bool(verbs and next_verbs and verbs[0]['lex']==s['cfg']['selection']['answer_lex'] and verbs[0]['vt']=='wayq'
                and next_verbs[0]['lex']==rules['say_lex'] and next_verbs[0]['vt']=='wayq' and phrase_records(c,'Subj'))


def csf_context(s,c):
    matches=[x for x in s['csf'] if int(x['start_clause'])==c['clause']]
    require(len(matches)<=1,'multiple exact MR1 starts')
    top=[x for x in s['csf'] if x['historical_projection']['speech_level']=='TOP_LEVEL_CSF']
    top=sorted(top,key=lambda x:int(x['start_clause']))
    before=[x for x in top if int(x['start_clause'])<c['clause']]
    after=[x for x in top if int(x['start_clause'])>c['clause']]
    def context(x):
        return dict(event_id=x['current_event_id'],clause=int(x['start_clause']),
                    speaker=x['historical_projection']['speaker_canonical'],
                    authority='HISTORICAL_MR1_ORDERED_CONTEXT_NOT_ANTECEDENT_OR_PARENT') if x else {}
    event=matches[0] if matches else None
    return event,context(before[-1] if before else None),context(after[0] if after else None)


def inventory(s):
    cc=by_id(s);out=[];cfg=s['cfg'];rules=cfg['rules']
    for index,c in enumerate(s['native']):
        for w in c['words']:
            if w['lex_utf8']!=cfg['selection']['lex_utf8']:continue
            require(w['lex'] in {cfg['selection']['answer_lex'],*cfg['selection']['nonanswer_lexemes']},'unreviewed ANA lexical identity '+str(w['lex']))
            answer=w['lex']==cfg['selection']['answer_lex']
            parents=ancestors(c,cc)
            direct=[cc[p] for p in c['bhsa_mother_nodes'] if p in cc]
            verse=[x for x in s['native'] if any(v['reference']==w['reference'] for v in x['words'])]
            verse_lex={v['lex'] for x in verse for v in x['words'] if v['reference']==w['reference']}
            next_clause=s['native'][index+1] if index+1<len(s['native']) else None
            formal=answer and formula(c,next_clause,s)
            event,previous,following=csf_context(s,c)
            subjects=phrase_records(c,'Subj');objects=phrase_records(c,'Objc');complements=phrase_records(c,'Cmpl')
            object_names=[v for p in objects for v in p['words'] if v['sp']=='nmpr']
            neg=[dict(clause=x['clause'],word=v['node'],lex=v['lex']) for x in [c]+parents for v in x['words'] if v['lex'] in rules['negative_lexemes']]
            cessation=[x for x in direct if rules['cease_lex'] in lexes(x)] if w['vt']=='infc' else []
            request=answer and w['vt']=='impf' and w['ps']=='p3' and w['prs_ps']=='p1' and bool(
                {v['lex'] for p in subjects for v in p['words']} & set(rules['request_subject_lexemes'])) and set(rules['wish_lexemes'])<=verse_lex
            emphasis=set(rules['self_emphasis_lexemes'])<=lexes(c)
            event_id='MR1:'+event['current_event_id'] if event else ''
            reviewed=[n for n in s['prior']['nodes'] if n['node_type']=='SPEECH_UNIT' and event_id and ({event_id,'R4.1:'+event_id}&set(n['source_evidence_ids']))]
            cycle_ids={e['source_node'] for e in s['prior']['edges'] if e['relation_type']=='GROUP_MEMBER_OF' and e['target_node'] in ('CYCLE_1','CYCLE_2','CYCLE_3')}
            dialogue=[n['node_id'] for n in reviewed if n['node_id'] in cycle_ids]
            if not answer:kind='NON_ANSWER_HOMONYM'
            elif formal and object_names:kind='DIRECTED_ANA_CSF'
            elif formal and dialogue:kind='DIALOGUE_TURN_CSF'
            elif formal:kind='FORMULAIC_CSF'
            elif cessation:kind='ANSWERING_CESSATION'
            elif neg:kind='NEGATED_OR_WITHHELD_RESPONSE'
            elif request:kind='RESPONSE_REQUEST'
            elif w['ps']=='p1' and w['vt']=='impf' and emphasis:kind='SELF_DECLARED_RESPONSE'
            elif w['ps']=='p1' and w['vt']=='impf' and w['prs_ps']=='p2':kind='FIRST_PERSON_DIRECTED_RESPONSE'
            elif w['ps']=='p1' and w['vt']=='impf':kind='FIRST_PERSON_RESPONSE_PROSPECT'
            else:kind='OTHER_ANA'
            contextual='PRECEDING_SPEECH_CONTEXT' if formal and dialogue else 'NOT_ESTABLISHED'
            control=w['reference']==cfg['controls']['formulaic_nonreply']
            if control:contextual='NOT_ESTABLISHED_FROZEN_FORMULAIC_CONTROL'
            out.append(dict(occurrence_id='ANA:W:'+str(w['node']),reference=w['reference'],word_node=w['node'],clause_node=c['clause'],
                clause_atom_ids=w['clause_atom_ids'],surface=w['surface'],clause_surface=c['surface'],
                lex=w['lex'],lex_utf8=w['lex_utf8'],lex0=w['lex0'],gloss=w['gloss'],root=w['root'],root_availability='PRESENT' if w['root'] else 'NOT_SUPPLIED_BY_BHSA',
                vs=w['vs'],vt=w['vt'],ps=w['ps'],gn=w['gn'],nu=w['nu'],clause_type=c['type'],domain=c['domain'],
                answer_lexeme=answer,construction_class=kind,formal_csf=formal,contextual_response=contextual,
                semantic_response_relation='NOT_AUTOMATICALLY_ESTABLISHED' if answer else 'NOT_APPLICABLE_NON_ANSWER_HOMONYM',
                preceding_speech_antecedent_explicit='NOT_ESTABLISHED',automatic_response_to=[],automatic_parent_ids=[],
                subject_evidence=subjects,governing_cessation_subjects=[dict(clause=x['clause'],subjects=phrase_records(x,'Subj')) for x in cessation],
                actor_identity='EXPLICIT_SUBJECT_SURFACE_ONLY' if subjects else ('EXPLICIT_CESSATION_GOVERNOR_SUBJECT' if cessation else 'UNRESOLVED'),
                explicit_objects=objects,explicit_complements=complements,explicit_target_names=[v['lex_utf8'] for v in object_names],
                pronominal_target=dict(ps=w['prs_ps'],gn=w['prs_gn'],nu=w['prs_nu'],referential_identity='UNRESOLVED'),
                previous_top_level_speaker=previous,following_top_level_speaker=following,
                speaker_context_note='Ordered accepted MR1 onsets only; never an assigned speaker, semantic antecedent or nearest-opening parent.',
                historical_csf_event=deepcopy(event) if event else {},
                formula_clause_ids=[c['clause'],next_clause['clause']] if formal else [],
                surrounding_formula=(c['surface']+next_clause['surface']) if formal else '',
                reviewed_dialogue_node_ids=dialogue,negation_evidence=neg,syntactic_ancestor_clause_ids=[x['clause'] for x in parents],
                bhsa_mother_nodes=c['bhsa_mother_nodes'],cessation_governor_ids=[x['clause'] for x in cessation],
                request_context_clause_ids=[x['clause'] for x in verse] if request else [],
                classification_basis='EXACT_LEXEME_AND_MORPHOSYNTAX_PLUS_SEPARATE_ACCEPTED_DIALOGUE_MEMBERSHIP',
                classification_limit='Construction evidence only; modality, coreference, discourse force and long-distance antecedent remain for human review.',
                source_word=deepcopy(w)))
    return out


def focus(s,occurrences):
    wanted=set(s['cfg']['focus_refs'])|{r['reference'] for r in occurrences if int(r['reference'].split(':')[0]) in s['cfg']['expanded_focus_chapters']}
    out=[]
    for ref in sorted(wanted,key=lambda x:tuple(map(int,x.split(':')))):
        clauses=[c for c in s['native'] if any(w['reference']==ref for w in c['words'])]
        require(clauses,'missing required focus '+ref)
        found=[r for r in occurrences if r['reference']==ref]
        out.append(dict(reference=ref,clause_ids=[c['clause'] for c in clauses],clause_atom_ids=sorted({a for c in clauses for a in c['clause_atom_ids']}),
            surface=''.join(w['surface'] for w in sorted([w for c in clauses for w in c['words'] if w['reference']==ref],key=lambda w:w['node'])),occurrence_ids=[r['occurrence_id'] for r in found],
            status='ANA_PRESENT' if found else 'NO_ANA',
            add_speech_control=not found and any(s['cfg']['rules']['add_lex'] in lexes(c) for c in clauses) and any(s['cfg']['rules']['say_lex'] in lexes(c) for c in clauses),
            lexical_evidence=[dict(clause=c['clause'],word=w['node'],lex=w['lex'],surface=w['surface'],gloss=w['gloss']) for c in clauses for w in c['words']],
            evidence_scope='COMPLETE_VERSE_CLAUSE_CONTEXT_NOT_INFERRED_UNIT_SPAN'))
    return out


def candidate_rows(s,occurrences,ff):
    by_ref={r['reference']:r for r in ff};out=[]
    for c in s['cfg']['candidates']:
        refs=list(dict.fromkeys([c['source'],c['closure_context'],c['target']]))
        relevant=[r for r in occurrences if r['reference'] in refs]
        interior=[r['occurrence_id'] for r in occurrences if min(by_ref[c['source']]['clause_ids'])<r['clause_node']<min(by_ref[c['target']]['clause_ids'])] if c['candidate_id']=='ANA-C4' else []
        out.append(dict(**c,status='UNADJUDICATED',automatic_resolution=False,candidate_parent='',
            relation_layer='HYPOTHESIS_OVERLAY_NOT_STRUCTURAL_EDGE',
            occurrence_ids=[r['occurrence_id'] for r in relevant],
            positional_interval_occurrence_ids=interior,interval_is_hierarchical_containment=False,
            clause_ids=sorted({n for ref in refs for n in by_ref[ref]['clause_ids']}),
            proposed_response_antecedent='UNADJUDICATED' if c['candidate_id']=='ANA-C2' else '',
            requested_responder_surface='שדי' if c['candidate_id']=='ANA-C2' else '',
            actual_responder_surface='יהוה' if c['candidate_id']=='ANA-C2' else '',
            responder_identity_equivalence='NOT_COMPUTATIONALLY_ASSERTED',
            adjacency_as_antecedent=False,new_human_judgment=False,
            limitation='Supplied research hypothesis, supported by separately listed surface evidence; neither lexical recurrence nor temporal ordering establishes the proposed relation.'))
    return out


def classes(rows):
    return [dict(construction_class=k,count=sum(r['construction_class']==k for r in rows),
        occurrence_ids=[r['occurrence_id'] for r in rows if r['construction_class']==k]) for k in CLASSES]


def questions():
    prompts=[('ANA-Q1','Frozen 3:2 formal/nonreply control; inspect accepted evidence, do not reopen its parentage.',[]),
        ('ANA-Q2','Does 31:40 to 32:1 warrant a source-supported post-closure relation?',['ANA-C1']),
        ('ANA-Q3','Does 31:35 to 38:1 warrant a long-distance response relation despite intervening speech and unresolved responder equivalence?',['ANA-C2']),
        ('ANA-Q4','Does the cessation/directed-answer contrast at 32:1 and 38:1 warrant a response-frame relation beyond lexical recurrence?',['ANA-C3']),
        ('ANA-Q5','What relation, if any, does Elihu have to that interval, considering his explicit response language and the 3:2 counterexample?',['ANA-C4'])]
    return [dict(question_id=i,question=q,candidate_ids=ids,
        allowed_outcomes=['FROZEN_CONTROL_NOT_REOPENED'] if i=='ANA-Q1' else ['HUMAN_SUPPLIED_RELATION_WITH_SOURCE','UNRESOLVED','INSUFFICIENT_EVIDENCE'],
        **{k:'UNREVIEWED' if k=='review_status' else '' for k in prep.REVIEW_FIELDS}) for i,q,ids in prompts]


def dependencies(s):
    cases=prep.decode_rows(s['files']['03_global_seam_cases.csv'])
    raw={r['case_id']:r for r in prep.r43.h1.read_csv(s['files']['03_global_seam_cases.csv'])}
    return [dict(case_id=c['case_id'],source_member='history/hsa3_prep/03_global_seam_cases.csv',
        source_row_sha256=sha(canonical(raw[c['case_id']]).encode()),source_review_status=c['review_status'],
        dependency_type='ADDITIONAL_SURFACE_EVIDENCE_PENDING_HUMAN_REVIEW',
        candidate_ids=[x['candidate_id'] for x in s['cfg']['candidates']],question_ids=['ANA-Q2','ANA-Q3','ANA-Q4','ANA-Q5'],
        modifies_original_case=False,resolves_parentage=False) for c in cases if c['case_id'] in ('SEAM_D','SEAM_E')]


def evidence(s,rows,ff):
    # Hash serialized CSV row dictionaries (strings), not Python-only type choices.
    def row_hash(row):return sha(canonical(prep.r43.h1.read_csv(prep.r43.h1.util.csv_bytes([row]))[0]).encode())
    selected={i for r in rows for i in [r['clause_node']]+r['formula_clause_ids']+r['syntactic_ancestor_clause_ids']}
    selected.update(i for f in ff for i in f['clause_ids'])
    out=[dict(evidence_id='BHSA2021:clause:'+str(c['clause']),kind='NATIVE_CLAUSE_SNAPSHOT',
        source_member='11_bhsa_native_clauses.csv',source_data_row=i,source_row_sha256=row_hash(c),
        reference=c['ref'],source_record=c) for i,c in enumerate(s['native'],1) if c['clause'] in selected]
    for i,c in enumerate(s['csf'],1):
        if any(r['historical_csf_event']==c for r in rows):out.append(dict(evidence_id='MR1:'+c['current_event_id'],kind='ACCEPTED_MR1_CSF_CONTEXT',
            source_member='13_accepted_mr1_csf_context.csv',source_data_row=i,source_row_sha256=row_hash(c),
            reference=c['historical_projection']['ref'],source_record=c))
    for i,c in enumerate(s['prior']['accounting'],1):
        out.append(dict(evidence_id='FROZEN_HUMAN_ROW:'+str(i),kind='FROZEN_HUMAN_ACCOUNTING',
            source_member='history/hsa3_prep/history/r4_3/10_human_judgment_accounting.csv',source_data_row=i,
            source_row_sha256=sha(canonical(prep.r43.h1.read_csv(s['files']['history/r4_3/10_human_judgment_accounting.csv'])[i-1]).encode()),reference='',source_record=c))
    for i,c in enumerate(s['prior']['edges'],1):
        if c['source_node'] in ('H:HSA017','H:HSA013','H:HSA014') or c['target_node'] in ('H:HSA013','H:HSA014'):
            out.append(dict(evidence_id=c['edge_id'],kind='FROZEN_STRUCTURAL_CONSTRAINT',
                source_member='history/hsa3_prep/history/r4_3/02_whole_book_hierarchy_edges.csv',source_data_row=i,
                source_row_sha256=sha(canonical(prep.r43.h1.read_csv(s['files']['history/r4_3/02_whole_book_hierarchy_edges.csv'])[i-1]).encode()),reference='',source_record=c))
    return out


def controls(m,s):
    def at(ref):return [r for r in m['inventory'] if r['reference']==ref]
    ff={x['reference']:x for x in m['focus']};out=[]
    checks={
        '3_2_FORMAL_NOT_SEMANTIC':bool(at('3:2')) and all(r['construction_class']=='FORMULAIC_CSF' and not r['automatic_response_to'] and r['contextual_response']=='NOT_ESTABLISHED_FROZEN_FORMULAIC_CONTROL' for r in at('3:2')),
        '31_35_REQUEST_NOT_ACTUAL_RESPONSE':bool(at('31:35')) and all(r['construction_class']=='RESPONSE_REQUEST' and r['request_context_clause_ids'] for r in at('31:35')),
        '32_1_CESSATION_EXPLICIT_JOB':bool(at('32:1')) and all(r['construction_class']=='ANSWERING_CESSATION' and 'איוב' in r['explicit_target_names'] and r['cessation_governor_ids'] for r in at('32:1')),
        '32_6_FORMAL_NO_PARENT':bool(at('32:6')) and all(r['formal_csf'] and not r['automatic_parent_ids'] and not r['automatic_response_to'] for r in at('32:6')),
        '36_1_NO_ANA_ADD_SPEECH':not at('36:1') and ff.get('36:1',{}).get('status')=='NO_ANA' and ff.get('36:1',{}).get('add_speech_control') is True,
        '38_1_DIRECTED_EXPLICIT_JOB':bool(at('38:1')) and all(r['construction_class']=='DIRECTED_ANA_CSF' and 'איוב' in r['explicit_target_names'] for r in at('38:1')),
        'NO_ADJACENCY_ANTECEDENT':all(not r['automatic_response_to'] and r['preceding_speech_antecedent_explicit']=='NOT_ESTABLISHED' for r in m['inventory']) and all(not c['adjacency_as_antecedent'] for c in m['candidates']),
        'HOMONYMS_RETAINED_NOT_ANSWER':all(r['construction_class']=='NON_ANSWER_HOMONYM' and not r['answer_lexeme'] for r in m['inventory'] if r['lex'] in s['cfg']['selection']['nonanswer_lexemes']),
    }
    for key,value in checks.items():out.append(dict(control=key,status='PASS' if value else 'FAIL',authority='REGRESSION_ONLY_NOT_DETECTION_RULE'))
    return out


def report(m,s,review=False):
    ff={f['reference']:f for f in m['focus']}
    lines=['# '+('ANA response-frame human review packet' if review else 'Job 31:40 post-closure surface audit'),'',
        'HSA3-ANA.0.1 — '+s['mode'], '',
        '**LEXICAL RECURRENCE ≠ SEMANTIC RESPONSE ≠ DISCOURSE RELATION ≠ HIERARCHICAL PARENTAGE.**', '',
        'This packet records construction evidence and four supplied research hypotheses. No automatic RESPONSE_TO, CHILD_OF, sibling, final boundary or new human judgment is created. R4.4 is not authorized.',
        'The entire 62-file accepted HSA3-PREP package is copied byte-for-byte under history/hsa3_prep (synthetic counterpart in self-test). All 57 unresolved rows, A–G reviews, 59 human judgments and HSA2-F closure decisions remain unchanged.', '',
        '## Inventory and provenance', '',
        f"Whole-book native scan: {len(s['execution']['book_word_nodes'])} words, {len(s['native'])} clauses. Hebrew lexeme ענה: {len(m['inventory'])} occurrences; answer lexeme: {sum(r['answer_lexeme'] for r in m['inventory'])}; distinct non-answer homonyms: {sum(not r['answer_lexeme'] for r in m['inventory'])}.",
        'BHSA raw lex, lex_utf8, lex0, gloss, stem, tense, person/gender/number and suffix features are retained. Root is NOT_SUPPLIED_BY_BHSA when absent; it is not reconstructed. The <NH=[ piel homonym (be lowly) remains visible and is not an answering event.',
        'Native clauses and every Job word are in 11/12; accepted MR1 context is in 13. Table 06 carries exact row IDs, canonical row hashes and complete source records. Metadata contains TF paths/versions/feature-file SHA256 and accepted artifact receipts. Original human source links remain in the complete nested histories.', '',
        '| Construction | Count |','| --- | ---: |']
    lines += [f"| {c['construction_class']} | {c['count']} |" for c in m['classes']]
    lines += ['', '## Classification limits','',
        'FORMULAIC_CSF requires answer-wayyiqtol with an explicit subject followed by an אמר-wayyiqtol clause. DIRECTED_ANA_CSF additionally has a proper-name object. DIALOGUE_TURN_CSF requires an exact MR1 event identity in an accepted cycle-member speech node; it records reviewed context, not a computed response antecedent. Previous/following top-level speakers are MR1 ordered context only.',
        'Negation uses explicit clause/mother-clause links, never a nearest-negative heuristic. It is reported as grammatical/contextual evidence, not a full semantic scope proof. ANSWERING_CESSATION uses an infinitive attached by BHSA mother to שבת. RESPONSE_REQUEST uses the attested wish context מי יתן, explicit שדי subject and first-person object suffix; impf alone does not prove jussive/request force.',
        'First-person forms with אף אני are SELF_DECLARED_RESPONSE; other first-person impf forms are prospective or pronominally directed subclasses. Conditional, interrogative and optative force is not resolved by this classification. OTHER_ANA retains all remaining answer forms without inventing discourse relations.', '',
        '## Fixed control: Job 3:2', '',
        'The formal ויען איוב ויאמר does not establish a preceding semantic reply. Job 2:13 records silence; 3:1 records Job opening his mouth. The accepted 3:1-above / 3:2-within relation remains frozen. ANA-Q1 displays this counterexample and does not reopen it.', '',
        '## Job 31:35–38:1 observations', '',
        '31:35 is a requested response (שדי יענני), not an actual response event or a morphology-only jussive. 31:40 is the accepted closure תמו דברי איוב, not a new ענה occurrence.',
        'HSA2-F remains: 31:40 → 29:1 DIRECT_LOCAL_CLOSURE; 31:40 → 27:1 NO_DIRECT_RELATION in DIRECT_CLOSURE_TARGET; 31:40 → POST_DIALOGUE_JOB TERMINATES_ENCLOSING_GROUP in HIGHER_ORDER_TERMINAL_EFFECT.',
        '32:1 explicitly describes the three men ceasing to answer Job: שבת governs מענות with explicit Job object. 38:1 has an explicit YHWH subject and Job object. Their contrast is observable; inclusio, long-distance response, parentage and שדי=יהוה identity are not computed.', '',
        '## Elihu: distinct evidence and limits', '',
        '32:6 is a formal speech introduction only. 32:11–17 supplies additional response-language: 32:12 עונה is syntactically linked through a participial clause to אין; 32:15–16 negate answering; 32:17 אף אני אענה is a first-person declaration (BHSA hif, retained without normalization). 32:20 has a first-person prospective answer form.',
        '32:14 uses אשיבנו (שוב), not ענה; it is preserved as response-role context. 33:12 אענך has explicit first-person verb and second-person suffix, without forced referential resolution. 33:13 has negated ענה but no local explicit subject: its third-person referent remains UNRESOLVED. 33:14 has אל with דבר and is NO_ANA.',
        '34:1 and 35:1 have formal CSFs. 36:1 is NO_ANA / ADD_SPEECH (יסף + אמר). Elihu’s response claims strengthen the reason to review the interval but neither make him a fourth friend nor establish him as the answer between the friends and YHWH. 37:24 adjacency does not establish the antecedent of 38:1.', '',
        '## Source panels (verse context, not inferred speech spans)', '']
    for f in m['focus']:
        lines += [f"### Job {f['reference']} — {f['status']}",'',f['surface'],'',
            'Clause IDs: '+', '.join(map(str,f['clause_ids']))+'; clause_atom IDs: '+', '.join(map(str,f['clause_atom_ids'])),
            'Occurrences: '+(', '.join(f['occurrence_ids']) or 'NONE; absence verified by whole-book scan'), '']
    lines += ['## All occurrences','', '| Reference | Word | Clause | Raw lex | Stem / tense | Construction |','| --- | ---: | ---: | --- | --- | --- |']
    lines += [f"| {r['reference']} | {r['word_node']} | {r['clause_node']} | {r['lex']} | {r['vs']} / {r['vt']} | {r['construction_class']} |" for r in m['inventory']]
    lines += ['', '## Hypothesis overlay only', '']
    for c in m['candidates']:
        lines += [f"- {c['candidate_id']}: {c['source']} → {c['target']}, {c['candidate_type']}; {c['status']}; automatic_resolution=false; no parent."]
    lines += ['', 'ANA-C2 keeps requested responder שדי and actual speaker יהוה separate. ANA-C4 records positional interval evidence only, never computed hierarchical containment. SEAM_D/E receive typed evidence dependencies; no A–G case is answered.', '']
    lines += ['## Frozen source constraints (not reopened)', '',
        '| Edge ID | Source node | Relation | Target node | Human source records |',
        '| --- | --- | --- | --- | --- |']
    lines += [f"| {x['source_record']['edge_id']} | {x['source_record']['source_node']} | {x['source_record']['relation_type']} | {x['source_record']['target_node']} | {', '.join(x['source_record']['source_judgment_ids'])} |" for x in m['evidence'] if x['kind']=='FROZEN_STRUCTURAL_CONSTRAINT']
    lines += ['', 'Each edge retains its exact original data-row locator and canonical hash in table 06. These rows are accepted constraints, not ANA candidate adjudications.', '']
    if review:
        lines += ['## Researcher worksheet — blank', '']
        for q in m['questions']:
            lines += ['### '+q['question_id'],'',q['question'],'','Allowed outcomes: '+', '.join(q['allowed_outcomes']),'','| Field | Value |','| --- | --- |']
            lines += [f'| {k} | {q[k]} |' for k in prep.REVIEW_FIELDS]
            lines += ['']
    return '\n'.join(lines)+'\n'


def build(s):
    ii=inventory(s);ff=focus(s,ii)
    m=dict(inventory=ii,focus=ff,classes=classes(ii),candidates=candidate_rows(s,ii,ff),questions=questions(),dependencies=dependencies(s),
        evidence=evidence(s,ii,ff),native=deepcopy(s['native']),historical=deepcopy(s['files']),
        nodes=deepcopy(s['prior']['nodes']),edges=deepcopy(s['prior']['edges']),accounting=deepcopy(s['prior']['accounting']),
        unresolved=deepcopy(s['prior']['unresolved']),new_human_judgments=[],new_structural_relations=[])
    m['negative']=controls(m,s);m['audit']=report(m,s);m['review']=report(m,s,True)
    return m


def gates(m,s):
    ii=m['inventory'];expected=inventory(s);checks={}
    checks['FROZEN_89_FILES']=len(s['frozen'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'].get(r['path']) for r in s['frozen'])
    checks['ACCEPTED_HISTORY_BYTE_IDENTICAL']=m['historical']==s['files']
    checks['SOURCE_NODES_EDGES_UNCHANGED']=m['nodes']==s['prior']['nodes'] and m['edges']==s['prior']['edges']
    checks['FROZEN_HUMAN_JUDGMENTS']=m['accounting']==s['prior']['accounting']
    checks['UNRESOLVED_57_UNCHANGED']=m['unresolved']==s['prior']['unresolved'] and len(m['unresolved'])==s['cfg']['regression']['unresolved']
    checks['NO_NEW_HUMAN_JUDGMENT']=m['new_human_judgments']==[]
    checks['NO_NEW_STRUCTURAL_RELATION']=m['new_structural_relations']==[]
    checks['NATIVE_SNAPSHOT_INTACT']=m['native']==s['native']
    checks['WHOLE_BOOK_ANA_COVERAGE']=Counter(r['word_node'] for r in ii)==Counter(w['node'] for c in s['native'] for w in c['words'] if w['lex_utf8']==s['cfg']['selection']['lex_utf8'])
    checks['OCCURRENCE_FIELDS_SOURCE_EXACT']=ii==expected
    checks['CONSTRUCTION_PARTITION']=m['classes']==classes(ii) and sum(c['count'] for c in m['classes'])==len(ii)
    checks['FOCUS_COMPLETE_SOURCE_EXACT']=m['focus']==focus(s,expected)
    checks['CANDIDATES_EXACT_FOUR']=m['candidates']==candidate_rows(s,expected,focus(s,expected))
    checks['NO_AUTOMATIC_CANDIDATE_RESOLUTION']=bool(m['candidates']) and all(c['status']=='UNADJUDICATED' and c['automatic_resolution'] is False and not c['candidate_parent'] and not c['new_human_judgment'] for c in m['candidates'])
    checks['RESPONDER_IDENTITY_UNASSERTED']=all(c['responder_identity_equivalence']=='NOT_COMPUTATIONALLY_ASSERTED' for c in m['candidates'])
    checks['NO_OCCURRENCE_PARENT_OR_RESPONSE']=all(not r['automatic_parent_ids'] and not r['automatic_response_to'] for r in ii)
    checks['REVIEW_QUESTIONS_BLANK']=m['questions']==questions()
    checks['SEAM_D_E_ADDENDUM_ONLY']=m['dependencies']==dependencies(s) and {x['case_id'] for x in m['dependencies']}=={'SEAM_D','SEAM_E'}
    checks['EXACT_EVIDENCE_LINKS']=m['evidence']==evidence(s,expected,focus(s,expected))
    checks['NEGATIVE_CONTROLS']=m['negative']==controls(m,s) and all(c['status']=='PASS' for c in m['negative'])
    for c in controls(m,s):checks[c['control']]=c['status']=='PASS'
    closure=[e for e in m['edges'] if e['source_node']=='H:HSA017' and e['relation_type'] in ('DIRECT_LOCAL_CLOSURE','NO_DIRECT_RELATION','TERMINATES_ENCLOSING_GROUP')]
    checks['THREE_CLOSURE_RELATIONS_PRESERVED']={(e['target_node'],e['relation_type'],e['dimension']) for e in closure}=={
        ('H:HSA016','DIRECT_LOCAL_CLOSURE','DIRECT_CLOSURE_TARGET'),('H:HSA015','NO_DIRECT_RELATION','DIRECT_CLOSURE_TARGET'),('POST_DIALOGUE_JOB','TERMINATES_ENCLOSING_GROUP','HIGHER_ORDER_TERMINAL_EFFECT')}
    checks['AUDIT_REPORT_FAITHFUL']=m['audit']==report(m,s)
    checks['REVIEW_PACKET_FAITHFUL']=m['review']==report(m,s,True)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def serialize(m,s):
    gg=gates(m,s);require(all(x['status']=='PASS' for x in gg),canonical([x for x in gg if x['status']!='PASS']))
    util=prep.r43.h1.util
    files={'history/hsa3_prep/'+k:v for k,v in m['historical'].items()}
    for name,key in [('01_ana_occurrence_inventory.csv','inventory'),('02_ana_focus_loci.csv','focus'),('03_ana_construction_classes.csv','classes'),
        ('04_post_31_40_relation_candidates.csv','candidates'),('05_ana_negative_controls.csv','negative'),('06_ana_evidence_links.csv','evidence'),
        ('09_hsa3_dependency_addendum.csv','dependencies'),('11_bhsa_native_clauses.csv','native'),('14_ana_review_questions.csv','questions')]:files[name]=util.csv_bytes(m[key])
    files['12_whole_book_word_scan.csv']=util.csv_bytes([dict(clause=c['clause'],**w) for c in m['native'] for w in c['words']])
    files['13_accepted_mr1_csf_context.csv']=util.csv_bytes(s['csf'])
    files[REPORTS[0]]=m['audit'].encode();files[REPORTS[1]]=m['review'].encode()
    metadata=dict(version='HSA3-ANA.0.1',mode=s['mode'],status='PASS',gate_count=len(gg)+1,baseline_commit=s['cfg']['baseline_commit'],
        code_sha256=sha(Path(__file__).read_bytes()),config_sha256=sha(CONFIG.read_bytes()),execution=s['execution'],frozen_receipts=s['frozen'],source_receipts=s['inputs'],
        counts=dict(occurrences=len(m['inventory']),answer_lexeme=sum(r['answer_lexeme'] for r in m['inventory']),constructions={c['construction_class']:c['count'] for c in m['classes']},
            candidates=len(m['candidates']),new_human_judgments=len(m['new_human_judgments']),new_structural_relations=len(m['new_structural_relations']),
            unresolved=len(m['unresolved']),historical_human_judgments=len(m['accounting']),native_clauses=len(m['native']),native_words=len(s['execution']['book_word_nodes'])),
        canonical_human_accounting_sha256=sha(canonical(m['accounting']).encode()),candidate_authority='UNADJUDICATED_RESEARCH_HYPOTHESES_ONLY')
    files['90_run_metadata.json']=util.json_bytes(metadata)
    def seal():
        files.pop('99_manifest_sha256.csv',None);files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(files.items())])
    seal();gg.append(util.manifest_gate(files));files['10_gates.csv']=util.csv_bytes(gg);seal()
    require(util.manifest_ok(files),'manifest');return files


def publish(files,out):
    # Reuse verified ZIP/disk writer; replace its stage-specific log only.
    prep.publish(files,out)
    out=Path(out).resolve();zp=out.with_name(out.name+'_results.zip');meta=json.loads(files['90_run_metadata.json'])
    out.with_name(out.name+'_run.log').write_text(f"HSA3-ANA.0.1 PASS\nMode {meta['mode']}\nGates {meta['gate_count']} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n",encoding='utf-8')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--self-test',action='store_true');a=p.parse_args(argv)
    s=load(a.tf_data,a.self_test);m=build(s);files=serialize(m,s)
    require(files==serialize(build(s),s),'deterministic serialization')
    require(prep.r43.frozen_receipts(s['cfg'])==s['frozen'],'frozen files changed during run')
    for r in s['inputs']:require(sha((ROOT/r['path']).read_bytes())==r['expected'],'input changed during run')
    for path,digest in s['execution']['data_hashes'].items():require(sha(Path(path).read_bytes())==digest,'BHSA feature changed during run')
    publish(files,a.out);print('HSA3-ANA.0.1 PASS '+str(Path(a.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError,KeyError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
