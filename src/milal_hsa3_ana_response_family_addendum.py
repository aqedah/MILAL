"""HSA3-ANA.0.2: frozen-input lexical/context addendum, no adjudication."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys
import unicodedata
import zipfile
import milal_hsa3_ana_response_frame as a
import milal_hsa_adjudication_criteria as criteria

ROOT=a.ROOT;CONFIG=ROOT/'config/hsa3_ana_0_2_job.json';sha=a.sha;canonical=a.canonical;util=a.prep.r43.h1.util
HISTORY='history/ana_0_1/';R43='history/hsa3_prep/history/r4_3/'
LAYERS=('CORE_VERBAL_ANA','CORE_ANA_LEXICAL_FAMILY','SEMANTIC_RESPONSE_NEIGHBOR','RESPONSE_CONTEXT_REFRAMING')
SENSES=('SEMANTIC_REPLY_SHWB','RETURN_RESTORE_SHWB','OTHER_SHWB','UNRESOLVED_SHWB')
NOMINAL_CLASSES=('CORE_ANA_NOMINAL_COGNATE','POSSIBLE_ANA_NOMINAL_COGNATE','NON_RESPONSE_SIMILAR_FORM')


def require(ok,message):
    if not ok:raise ValueError('HSA3-ANA.0.2 STOP: '+message)


def norm(text):return ''.join(c for c in unicodedata.normalize('NFD',text or '') if not unicodedata.combining(c))
def order(ref):return tuple(map(int,ref.split(':')))
def rowhash(row):return sha(canonical(row).encode())
def csvhash(row):return rowhash(a.prep.r43.h1.read_csv(util.csv_bytes([row]))[0])


def baseline_audit(files,cfg,actual_sha,synthetic=False):
    require(util.manifest_ok(files),'0.1 manifest mismatch')
    if not synthetic:require(actual_sha==cfg['archive']['sha256'] and len(files)==cfg['archive']['members'],'0.1 SHA or member count mismatch')
    meta=json.loads(files['90_run_metadata.json']);ii=a.prep.decode_rows(files['01_ana_occurrence_inventory.csv'])
    cc=a.prep.decode_rows(files['04_post_31_40_relation_candidates.csv']);qq=a.prep.decode_rows(files['14_ana_review_questions.csv'])
    require(meta['version']=='HSA3-ANA.0.1' and meta['status']=='PASS','0.1 metadata')
    require(all(g['status']=='PASS' for g in a.prep.decode_rows(files['10_gates.csv'])),'0.1 gate failure')
    require(len(cc)==4 and [c['candidate_id'] for c in cc]==['ANA-C1','ANA-C2','ANA-C3','ANA-C4'],'0.1 candidates')
    require(all(c['automatic_resolution'] is False and c['status']=='UNADJUDICATED' and c['new_human_judgment'] is False for c in cc),'0.1 adjudication changed')
    require([q['question_id'] for q in qq]==['ANA-Q'+str(i) for i in range(1,6)] and all(q[k]==('UNREVIEWED' if k=='review_status' else '') for q in qq for k in a.prep.REVIEW_FIELDS),'0.1 review fields changed')
    require(meta['counts']['new_human_judgments']==meta['counts']['new_structural_relations']==0,'0.1 new judgments')
    require(len(a.prep.decode_rows(files[R43+'03_unresolved_parentage.csv']))==cfg['expected']['unresolved'],'0.1 unresolved')
    require(len(a.prep.decode_rows(files[R43+'10_human_judgment_accounting.csv']))==cfg['expected']['human'],'0.1 human count')
    if not synthetic:require(len(ii)==cfg['expected']['verbal'] and sum(not x['answer_lexeme'] for x in ii)==cfg['expected']['homonyms'],'0.1 verbal inventory counts')
    ee=a.prep.decode_rows(files[R43+'02_whole_book_hierarchy_edges.csv'])
    expected={('H:HSA016','DIRECT_LOCAL_CLOSURE','DIRECT_CLOSURE_TARGET'),('H:HSA015','NO_DIRECT_RELATION','DIRECT_CLOSURE_TARGET'),('POST_DIALOGUE_JOB','TERMINATES_ENCLOSING_GROUP','HIGHER_ORDER_TERMINAL_EFFECT')}
    require(expected<={(e['target_node'],e['relation_type'],e['dimension']) for e in ee if e['source_node']=='H:HSA017'},'0.1 frozen closure relations')
    return dict(sha256=actual_sha,member_count=len(files),mode='SYNTHETIC_BASELINE_FIXTURE' if synthetic else 'VERIFIED_FROZEN_ARTIFACT',manifest_sha256=sha(files['99_manifest_sha256.csv']))


def load(tf_data=None,self_test=False):
    cfg=json.loads(CONFIG.read_bytes());frozen=a.prep.r43.frozen_receipts(cfg)
    require(all(r['expected']==r['actual'] for r in frozen),'frozen source changed')
    if self_test:
        # Existing synthetic 0.1 fixture only. Never rerun the empirical 0.1 stage.
        old=a.load(self_test=True);files=a.serialize(a.build(old),old)
        from milal_hsa3_ana_family_synthetic import extend
        native=extend(deepcopy(old['native']));execution=deepcopy(old['execution']);execution['book_word_nodes']=sorted(w['node'] for c in native for w in c['words'])
        digest=sha(files['99_manifest_sha256.csv'])
    else:
        pin=cfg['archive'];data=(ROOT/pin['path']).read_bytes();digest=sha(data)
        artifact=a.prep.r43.h1.src.archive(data,pin['sha256'],mr1=True);files=artifact['files']
        baseline_audit(files,cfg,digest)
        require(tf_data is not None,'--tf-data required')
        native,execution=a.native_bhsa(tf_data)
        require(util.csv_bytes(native)==files['11_bhsa_native_clauses.csv'],'native source differs from frozen 0.1 snapshot')
        require(execution['data_hashes']==json.loads(files['90_run_metadata.json'])['execution']['data_hashes'],'BHSA source hashes differ')
    receipt=baseline_audit(files,cfg,digest,self_test)
    s=dict(cfg=cfg,files=files,receipt=receipt,native=native,execution=execution,frozen=frozen,mode='SYNTHETIC_ONLY' if self_test else 'REAL_BHSA_2021_ADDENDUM')
    a.validate_source(s)
    s['verbal']=a.prep.decode_rows(files['01_ana_occurrence_inventory.csv']);s['candidates']=a.prep.decode_rows(files['04_post_31_40_relation_candidates.csv'])
    s['questions']=a.prep.decode_rows(files['14_ana_review_questions.csv']);s['accounting']=a.prep.decode_rows(files[R43+'10_human_judgment_accounting.csv'])
    return s


def all_words(s):return [(c,w) for c in s['native'] for w in c['words']]
def verse(s,ref):return [c for c in s['native'] if any(w['reference']==ref for w in c['words'])]
def phrase_words(c,functions):return [w for p in c['phrases'] if p['function'] in functions for w in c['words'] if w['node'] in p['word_nodes']]
def phrases(c,functions):return [p for p in c['phrases'] if p['function'] in functions]


def source_row(s,c,w,layer,category):
    local=verse(s,w['reference']);negative=[dict(word=x['node'],lex=x['lex'],clause=c['clause']) for x in c['words'] if x['lex'] in ('L>','>JN/','>L=')]
    vv=sorted(s['verbal'],key=lambda r:int(r['word_node']));before=[r for r in vv if int(r['word_node'])<w['node']];after=[r for r in vv if int(r['word_node'])>w['node']]
    return dict(evidence_id=layer+':W:'+str(w['node']),reference=w['reference'],word_node=w['node'],clause_node=c['clause'],clause_atom_ids=w['clause_atom_ids'],
        surface=w['surface'],lex=w['lex'],lex_utf8=w['lex_utf8'],lex0=w['lex0'],root=w['root'],root_availability='PRESENT_NOT_SENSE_PROOF' if w['root'] else 'ROOT_UNAVAILABLE',
        gloss=w['gloss'],sp=w['sp'],pdp=w['pdp'],vs=w['vs'],vt=w['vt'],response_layer=layer,category=category,
        phrase_functions=[p['function'] for p in c['phrases'] if w['node'] in p['word_nodes']],clause_surface=c['surface'],
        verse_surface=''.join(x['surface'] for x in sorted([x for v in local for x in v['words'] if x['reference']==w['reference']],key=lambda x:x['node'])),
        subject_evidence=phrases(c,('Subj',)),object_evidence=phrases(c,('Objc',)),complement_evidence=phrases(c,('Cmpl',)),
        participant_references=[dict(word=x['node'],ps=x['ps'],suffix_ps=x['prs_ps'],suffix_gn=x['prs_gn'],suffix_nu=x['prs_nu'],referential_identity='UNRESOLVED') for x in c['words'] if x['prs_ps'] not in ('NA',None,'') or x['sp']=='prps'],
        negation_evidence=negative,polarity='NEGATIVE_OR_ABSENCE' if negative else 'NO_EXPLICIT_LOCAL_NEGATION',
        bhsa_syntactic_context=dict(type=c['type'],domain=c['domain'],mother=c['bhsa_mother_nodes'],rela=c['rela'],code=c['code'],use='CORROBORATION_ONLY_NOT_MILAL_PARENT'),
        previous_verbal_ana=before[-1]['occurrence_id'] if before else '',following_verbal_ana=after[0]['occurrence_id'] if after else '',
        neighbor_note='Source order only, not semantic antecedent or parent.',source_member='15_native_clause_evidence.csv',source_data_row=s['native'].index(c)+1,
        source_row_sha256=csvhash(c),source_word=deepcopy(w),automatic_relation='',automatic_parent_ids=[])


def nominal(s):
    out=[];cfg=s['cfg']['selection']
    for c,w in all_words(s):
        if w['sp']=='verb' or not ('ענה' in norm(w['lex_utf8']) or w['root']==cfg['ana_root']):continue
        core=w['lex']==cfg['nominal_lex'] and w['lex0']==cfg['nominal_lex0'] and w['gloss']==cfg['nominal_gloss'] and w['sp'] in cfg['nominal_pos']
        possible=not core and w['root']==cfg['ana_root'] and w['gloss'] in ('answer','reply','response','<unknown>')
        kind='CORE_ANA_NOMINAL_COGNATE' if core else ('POSSIBLE_ANA_NOMINAL_COGNATE' if possible else 'NON_RESPONSE_SIMILAR_FORM')
        r=source_row(s,c,w,LAYERS[1],kind)
        r.update(family_membership='INCLUDED_BY_LEXICAL_MORPHOLOGICAL_EVIDENCE' if core else 'NOT_CONFIRMED',
            selection_basis='WHOLE_BOOK_NONVERBAL_SPELLING_OR_RECORDED_ROOT_SCREEN',
            classification_basis='Exact M<NH=/ + M<NH + answer gloss + nominal POS; local negative/existential context corroborates. Root unavailable is not reconstructed.' if core else 'Distinct lexical identity/gloss or root homonym; spelling/root screening is not a response-family assertion.',
            direct_root_derivation_asserted=False,counts_as_response_family=core)
        out.append(r)
    return out


def shwb(s):
    out=[];rules=s['cfg']['rules']
    for c,w in all_words(s):
        if w['sp']!='verb' or norm(w['lex_utf8'])!='שוב':continue
        require(w['lex'] in s['cfg']['selection']['shwb_lexemes'],'unrecognized SHWB lexical identity')
        obj={x['lex'] for x in phrase_words(c,('Objc',))};cmpl={x['lex'] for x in phrase_words(c,('Cmpl',))}
        vl={x['lex'] for cl in verse(s,w['reference']) for x in cl['words'] if x['reference']==w['reference']}
        basis=[];kind='UNRESOLVED_SHWB'
        if w['vs']=='hif' and (obj|cmpl)&set(rules['speech_lexemes']):kind='SEMANTIC_REPLY_SHWB';basis=['HIF_WITH_EXPLICIT_UTTERANCE_OBJECT_OR_COMPLEMENT']
        elif w['vs']=='hif' and w['vt']=='impv' and w['prs_ps']=='p1' and (vl&set(rules['speech_lexemes']) or set(rules['turn_preparation'])<=vl):kind='SEMANTIC_REPLY_SHWB';basis=['HIF_IMPERATIVE_FIRST_PERSON_OBJECT_WITH_SPEECH_OR_TURN_PREPARATION_CONTEXT']
        elif w['vs']=='hif' and w['ps']=='p1' and w['prs_ps'] in ('p2','p3') and 'MH' in obj:kind='SEMANTIC_REPLY_SHWB';basis=['HIF_FIRST_PERSON_PERSONAL_SUFFIX_INTERROGATIVE_WHAT_OBJECT']
        elif (cmpl&set(rules['spatial_lexemes'])) or (obj&set(rules['restored_objects'])):kind='RETURN_RESTORE_SHWB';basis=['EXPLICIT_RETURN_DESTINATION_SOURCE_OR_RESTORED_OBJECT']
        elif (obj|{x['lex'] for x in phrase_words(c,('Subj',))})&set(rules['other_objects']):kind='OTHER_SHWB';basis=['NON_REPLY_WRATH_BREATH_OR_SPIRIT_CONSTRUCTION']
        else:basis=['INSUFFICIENT_CONSTRUCTION_FOR_CONFIDENT_SENSE_ASSIGNMENT']
        r=source_row(s,c,w,LAYERS[2],kind)
        r.update(classification_basis=basis,semantic_classification_status='PROVISIONAL_CONSTRUCTION_READING_NOT_HUMAN_ADJUDICATION',counts_as_response_neighbor=kind=='SEMANTIC_REPLY_SHWB',
            stem_evidence=dict(vs=w['vs'],vt=w['vt']),pronominal_object_evidence=dict(ps=w['prs_ps'],gn=w['prs_gn'],nu=w['prs_nu'],referent='UNRESOLVED'),
            immediate_discourse_evidence=[dict(clause=cl['clause'],surface=cl['surface']) for cl in verse(s,w['reference'])],
            utterance_complement_word_ids=[x['node'] for x in phrase_words(c,('Cmpl',)) if x['lex'] in rules['speech_lexemes']],
            relation_to_job='PERSONAL_SUFFIX_TARGET_UNRESOLVED; Job-context evidence supplied separately, not computational coreference',
            friends_failure_relation='CONTEXTUAL_HYPOTHESIS_ONLY_NOT_RESPONSE_TO',
            limitation='Hiphil alone is insufficient. Contextual sense is provisional; no structural or RESPONSE_TO edge follows.')
        out.append(r)
    return out


def reframing(s):
    cfg=s['cfg']['reframing'];src=[r for r in s['verbal'] if r['reference']==cfg['source']]
    target=[(c,w) for c,w in all_words(s) if w['reference']==cfg['target'] and w['lex']==cfg['target_lex']]
    require(src and target,'reframing source/target missing')
    out=[]
    for c,w in target:
        r=source_row(s,c,w,LAYERS[3],'POSSIBLE_RESPONSE_REFRAMING')
        r.update(source_ref=cfg['source'],target_ref=cfg['target'],source_expression=' '.join(x['clause_surface'] for x in src),target_expression=c['surface'],
            source_ana_ids=[x['occurrence_id'] for x in src],relation_candidate='POSSIBLE_RESPONSE_REFRAMING',status='UNADJUDICATED',automatic_resolution=False,
            core_ana_lexeme=False,semantic_response_neighbor=False,response_context_reframing=True,
            linguistic_basis='Negative answer predicate followed by explicit אל + דבר. The contrast is available for review; source-subject coreference and rhetorical function are not established.',
            limitation='Local context candidate only; not an additional structural candidate, not a new discourse judgment.')
        out.append(r)
    return out


def verbal_rows(s):
    return [dict(evidence_id=r['occurrence_id'],reference=r['reference'],word_node=int(r['word_node']),clause_node=int(r['clause_node']),clause_atom_ids=r['clause_atom_ids'],
        surface=r['surface'],lex=r['lex'],lex_utf8=r['lex_utf8'],lex0=r['lex0'],root=r['root'],vs=r['vs'],vt=r['vt'],
        response_layer=LAYERS[0],category=r['construction_class'],answer_sense=r['answer_lexeme'],source_member=HISTORY+'01_ana_occurrence_inventory.csv',source_data_row=i,
        source_row_sha256=rowhash(a.prep.r43.h1.read_csv(s['files']['01_ana_occurrence_inventory.csv'])[i-1]),original_record=deepcopy(r),
        automatic_relation='',automatic_parent_ids=[]) for i,r in enumerate(s['verbal'],1)]


def cluster(s,family,neighbors,context):
    cfg=s['cfg']['cluster'];rows=[]
    relevant=[r for r in family if r['response_layer']==LAYERS[0] or r.get('counts_as_response_family')]+[r for r in neighbors if r['counts_as_response_neighbor']]+context
    for r in relevant:
        if not order(cfg['start'])<=order(r['reference'])<=order(cfg['end']):continue
        original=r.get('original_record',r)
        rows.append(dict(reference=r['reference'],word_node=r['word_node'],expression=original.get('clause_surface',r['surface']),lexeme=r['lex'],
            response_layer=r['response_layer'],polarity=r.get('polarity','NEGATIVE_OR_ABSENCE' if original.get('negation_evidence') else ('CESSATION' if r['category']=='ANSWERING_CESSATION' else 'NO_EXPLICIT_LOCAL_NEGATION')),
            actor=original.get('subject_evidence',[]),target=original.get('explicit_objects',original.get('object_evidence',[])),construction=r['category'],
            source_type='FROZEN_0_1' if r['response_layer']==LAYERS[0] else 'BHSA_2021_ADDENDUM',semantic_role='CONSTRUCTION_EVIDENCE_ONLY_REFERENTIAL_IDENTITIES_UNRESOLVED',
            automatic_relation='',evidence_ids=[r['evidence_id']]))
    return sorted(rows,key=lambda r:(order(r['reference']),r['word_node'],r['response_layer']))


def distribution(s,family,neighbors,context):
    scopes=[(str(i)+':1',str(i)+':999','CHAPTER_'+str(i)) for i in sorted({c['chapter'] for c in s['native']})]
    scopes.append((s['cfg']['cluster']['start'],s['cfg']['cluster']['end'],'JOB_32_1_TO_33_14'))
    rows=[]
    for lo,hi,name in scopes:
        def inside(r):return order(lo)<=order(r['reference'])<=order(hi)
        vv=[r for r in family if r['response_layer']==LAYERS[0] and inside(r)];nn=[r for r in family if r.get('counts_as_response_family') and inside(r)]
        ss=[r for r in neighbors if r['counts_as_response_neighbor'] and inside(r)];cx=[r for r in context if inside(r)]
        rows.append(dict(scope=name,start=lo,end=hi,CORE_VERBAL_ANA_COUNT=len(vv),ANSWER_SENSE_VERBAL_COUNT=sum(r['answer_sense'] for r in vv),
            NON_ANSWER_VERBAL_HOMONYM_COUNT=sum(not r['answer_sense'] for r in vv),CORE_ANA_FAMILY_COUNT=len(nn),SEMANTIC_RESPONSE_NEIGHBOR_COUNT=len(ss),
            RESPONSE_CONTEXT_REFRAMING_COUNT=len(cx),evidence_ids={LAYERS[0]:[r['evidence_id'] for r in vv],LAYERS[1]:[r['evidence_id'] for r in nn],LAYERS[2]:[r['evidence_id'] for r in ss],LAYERS[3]:[r['evidence_id'] for r in cx]},
            interpretation='SEPARATE_UNWEIGHTED_COUNTS_NOT_STRUCTURAL_STRENGTH'))
    return rows


def crosswalk(s,family,neighbors,context):
    focus={x['reference']:x for x in a.prep.decode_rows(s['files']['02_ana_focus_loci.csv'])};out=[]
    for r in family+neighbors+context:
        isverbal=r['response_layer']==LAYERS[0]
        out.append(dict(evidence_id=r['evidence_id'],reference=r['reference'],word_node=r['word_node'],response_layer=r['response_layer'],
            original_occurrence_id=r['evidence_id'] if isverbal else '',original_classification=r['category'] if isverbal else '',
            original_focus_status=focus.get(r['reference'],{}).get('status','NOT_IN_0_1_FOCUS'),
            verbal_status='VERBAL_ANA_SOURCE_RECORD' if isverbal else 'NO_VERBAL_ANA_AT_THIS_WORD',
            addendum_category=r['category'],original_rewritten=False,source_member=r['source_member'],source_data_row=r['source_data_row'],source_row_sha256=r['source_row_sha256']))
    return out


def candidate_addendum(s,family,neighbors,context):
    extra=[r for r in family if r.get('counts_as_response_family')]+[r for r in neighbors if r['counts_as_response_neighbor']]+context
    out=[]
    for c in s['candidates']:
        cid=c['candidate_id'];local=[r for r in extra if order('32:1')<=order(r['reference'])<=order('33:14')]
        selected=[] if cid=='ANA-C1' else local
        out.append(dict(candidate_id=cid,original_candidate_type=c['candidate_type'],original_candidate_record=deepcopy(c),
            original_member=HISTORY+'04_post_31_40_relation_candidates.csv',original_row_sha256=csvhash(c),
            direct_new_evidence_ids=[],contextual_new_evidence_ids=[r['evidence_id'] for r in selected],
            existing_verbal_evidence_ids=[r['occurrence_id'] for r in s['verbal'] if order('32:1')<=order(r['reference'])<=order('33:14') or r['reference']=='38:1'] if cid=='ANA-C4' else c['occurrence_ids'],
            evidential_role='NO_NEW_DIRECT_CLOSURE_EVIDENCE' if cid=='ANA-C1' else ('CONTEXT_NOT_DIRECT_LONG_DISTANCE_FULFILLMENT' if cid=='ANA-C2' else 'LOCAL_RESPONSE_FAILURE_AND_ROLE_LANGUAGE_FOR_REVIEW'),
            refinement_candidate_label='ELIHU_RESPONSE_ROLE_INTERVENTION' if cid=='ANA-C4' else '',refinement_status='UNADJUDICATED',automatic_resolution=False,
            alternatives=['POSITIONAL_ONLY','RESPONSE_ROLE_INTERVENTION'] if cid=='ANA-C4' else [],selected_alternative='',automatic_relation='',candidate_parent=''))
    return out


def human_crosswalk(s):
    rows=[];by={r['judgment_id']:r for r in s['accounting']}
    raw=a.prep.r43.h1.read_csv(s['files'][R43+'10_human_judgment_accounting.csv'])
    for ident in s['cfg']['judgment_ids']:
        require(ident in by,'missing frozen judgment '+ident);r=by[ident];h=r['historical_record']
        relation=h.get('selected_relation',h.get('hierarchy_relation',''));function=h.get('structural_function','')
        codes={'E-NEGATIVE-CONTROL'} if function=='NO_BOUNDARY' or relation in ('NO_DIRECT_RELATION','CONTINUES_WITHIN') else set()
        if h.get('ending_reference')=='31:40':codes|={'E-EXPLICIT-CLOSURE','E-ENCLOSING-SCOPE'}
        if relation in ('CHILD_OF','HIERARCHICALLY_ABOVE') or function=='SPEECH_UNIT_END':codes|={'E-ENCLOSING-SCOPE'}
        if relation=='SAME_LEVEL_SIBLING':codes|={'E-FORMULA-CORRESPONDENCE','E-FUNCTIONAL-EQUIVALENCE','E-DISTRIBUTIONAL-PATTERN'}
        if function in ('SPEECH_UNIT_ONSET','PARAGRAPH_ONSET','TRANSITION_COMPONENT','NARRATIVE_INTRODUCTION'):codes|={'E-EXPLICIT-ONSET'}
        if ident in ('HSA014','HSA024'):codes|={'E-NEGATIVE-CONTROL','N-ADJACENCY-ONLY'}
        if not codes:codes={'E-NEGATIVE-CONTROL'}
        index=s['accounting'].index(r)+1
        rows.append(dict(judgment_id=ident,original_record=deepcopy(h),original_source_locator=deepcopy(r['source_locator']),
            source_member=HISTORY+R43+'10_human_judgment_accounting.csv',source_data_row=index,source_row_sha256=rowhash(raw[index-1]),
            evidence_codes=sorted(codes),mapping_status='DRAFT_ILLUSTRATIVE_CROSSWALK_NOT_RECONSTRUCTED_HUMAN_REASONING',
            original_linguistic_basis=h.get('linguistic_basis',h.get('reasoning','')),original_methodological_note=h.get('methodological_note',''),
            adjudication_changed=False,new_human_judgment=False,limitation='Code associations illustrate the relation-specific protocol; only the quoted original record states the historical rationale.'))
    return rows


def dependencies(s,addendum):
    member='history/hsa3_prep/03_global_seam_cases.csv';cases=a.prep.r43.h1.read_csv(s['files'][member])
    return [dict(case_id=c['case_id'],source_member=HISTORY+member,source_row_sha256=rowhash(c),original_status=c['review_status'],
        dependency_type='LEXICAL_FAMILY_AND_CONTEXT_EVIDENCE_ADDENDUM_ONLY',candidate_ids=[r['candidate_id'] for r in addendum],question_ids=['ANA-Q2','ANA-Q3','ANA-Q4','ANA-Q5'],
        modifies_original_case=False,resolves_parentage=False) for c in cases if c['case_id'] in ('SEAM_D','SEAM_E')]


def panels(s):
    refs=set(s['cfg']['cluster']['required']+s['cfg']['cluster']['controls']+[s['cfg']['reframing']['negative_control']])
    return [dict(reference=ref,clause_ids=[c['clause'] for c in verse(s,ref)],
        surface=''.join(w['surface'] for w in sorted([w for c in verse(s,ref) for w in c['words'] if w['reference']==ref],key=lambda w:w['node'])),
        evidence_scope='LOCAL_CONTEXT_NOT_LEXICAL_MEMBERSHIP_OR_HIERARCHICAL_SCOPE') for ref in sorted(refs,key=order)]


def controls(m,s):
    out=[]
    def put(name,ok,ids):out.append(dict(control=name,status='PASS' if ok else 'FAIL',evidence_ids=ids,authority='NEGATIVE_CONTROL_NOT_NEW_ADJUDICATION'))
    v=[r for r in m['family'] if r['response_layer']==LAYERS[0] and r['reference']=='3:2']
    put('3_2_FORMAL_NOT_RESPONSE',bool(v) and all(r['category']=='FORMULAIC_CSF' and not r['original_record']['automatic_response_to'] for r in v),[r['evidence_id'] for r in v])
    non=[r for r in m['neighbors'] if r['category'] in ('RETURN_RESTORE_SHWB','OTHER_SHWB')]
    put('UNRELATED_SHWB_RETAINED',bool(non) and any(r['vs']=='hif' for r in non) and all(not r['counts_as_response_neighbor'] for r in non),[r['evidence_id'] for r in non])
    f={r['reference']:r for r in a.prep.decode_rows(m['historical']['02_ana_focus_loci.csv'])}
    put('36_1_ADD_SPEECH_NO_ANA',f.get('36:1',{}).get('status')=='NO_ANA' and f.get('36:1',{}).get('add_speech_control') is True,[])
    put('37_24_ADJACENCY_INSUFFICIENT',all(not r['original_candidate_record']['adjacency_as_antecedent'] and not r['automatic_relation'] for r in m['addendum']),[])
    put('RECURRENCE_NOT_HIERARCHY',all(not r.get('automatic_parent_ids') and not r.get('automatic_relation') for r in m['family']+m['neighbors']) and not m['new_structural_relations'],[])
    cc=[w for c in s['native'] for w in c['words'] if w['reference']==s['cfg']['reframing']['negative_control'] and w['lex']=='DBR[']
    put('DABAR_LOCAL_CONTROL_NOT_RESPONSE',bool(cc) and not any(r['word_node'] in {w['node'] for w in cc} for r in m['family']+m['neighbors']+m['context']),[str(w['node']) for w in cc])
    excluded=[r for r in m['family'] if r['category']=='NON_RESPONSE_SIMILAR_FORM']
    put('SAME_SPELLING_ROOT_NOT_COGNATE',bool(excluded) and all(not r['counts_as_response_family'] for r in excluded),[r['evidence_id'] for r in excluded])
    return out


def report(m,s):
    nominalrows=[r for r in m['family'] if r.get('counts_as_response_family')]
    lines=['# HSA3-ANA.0.2 response-family review addendum','',s['mode'],'',
        '0.1 is an immutable input. The original candidates and verbal classifications are not rewritten. This packet does not choose a hypothesis or build a hierarchy. R4.4 is not started.',
        'LEXICAL COGNATE ≠ SEMANTIC NEIGHBOR ≠ DISCOURSE FUNCTION ≠ HIERARCHICAL RELATION.','',
        f"Frozen verbal inventory: {len(s['verbal'])}; nominal answer-family occurrences: {len(nominalrows)}; whole-book SHWB candidates (distinct BHSA lexical identities retained): {len(m['neighbors'])}.",
        'Nominal answer-family positions: '+', '.join(r['reference'] for r in nominalrows)+'.',
        'SHWB construction readings: '+canonical(dict(Counter(r['category'] for r in m['neighbors'])))+'.','',
        '## Lexical limits','',
        'M<NH=/ has nominal POS, lex0 M<NH and gloss answer. Root is unavailable for these answer nouns; the addendum does not fabricate an etymological/root link. Inclusion is explicitly based on convergent lexical/morphological and local-context evidence. M<NH/ with gloss hiding place and root <WN is separate, despite the same lex_utf8 spelling. Other root/spelling screen hits remain visible as non-response or possible candidates.',
        'The whole-book SHWB scan uses normalized Hebrew lexeme identity and keeps CWB[ and CWB=[ separate. Hiphil alone is never reply. Explicit utterance object/complement, personal-suffix response request constructions, spatial source/destination and restored objects guide provisional sense descriptions. Unclear senses stay UNRESOLVED_SHWB; no classification creates RESPONSE_TO.',
        '32:14 has hif, a third-person object suffix, local negation and באמריכם with an utterance complement. The suffix referent remains unresolved computationally. The Job/friends-failure linkage is contextual evidence for human review, not asserted coreference.',
        '33:5 is also retained because the whole-book scan precedes focus selection.' if any(r['reference']=='33:5' for r in m['neighbors']) else 'This synthetic fixture represents a subset of real-data contexts.',
        '33:13 retains its frozen ANA word ID and unresolved subject. 33:14 has explicit אל with דבר. The local contrast is POSSIBLE_RESPONSE_REFRAMING, UNADJUDICATED; דבר is neither core ANA family nor a semantic-response-neighbor lexeme. This is one context-evidence candidate, not a fifth structural candidate.',
        '32:3 and 32:5 can simultaneously be NO_VERBAL_ANA and CORE_ANA_NOMINAL_COGNATE. Their original NO_ANA status is unchanged. 32:13 is local context only. 36:1 stays NO_ANA / ADD_SPEECH. Counts are separate distributional evidence, not weighted strength or a structural verdict.','',
        '## Job 32:1–33:14 response-language cluster','', '| Reference | Expression | Layer | Construction | Polarity |','| --- | --- | --- | --- | --- |']
    lines += ['| '+' | '.join(str(r[k]) for k in ('reference','expression','response_layer','construction','polarity'))+' |' for r in m['cluster']]
    lines += ['', '## Local and continuation controls','']
    for p in m['panels']:lines += ['### Job '+p['reference'],'',p['surface'],'','Clause nodes: '+', '.join(map(str,p['clause_ids'])),'']
    lines += ['## Frozen candidate evidence addendum','']
    for c in m['addendum']:lines += ['- '+c['candidate_id']+' '+c['original_candidate_type']+': '+c['evidential_role']+'; additional contextual IDs: '+(', '.join(c['contextual_new_evidence_ids']) or 'NONE')+'.']
    lines += ['', 'ANA-C4 keeps its original name. ELIHU_RESPONSE_ROLE_INTERVENTION is an additional UNADJUDICATED refinement label. POSITIONAL_ONLY and RESPONSE_ROLE_INTERVENTION remain alternatives; neither is selected.',
        'Q2: the added 32:3/5 answer-absence cluster is surrounding context, not a new direct closure target. Q3: no new direct proof of fulfillment or שדי=יהוה identity is supplied. Q4: nominal absence can be compared with cessation/answer onset. Q5: compare the interval position with explicit role language at 32:12/14–17/20 and 33:12–14, retaining the 3:2 counterexample.','',
        '## Criteria draft and frozen judgments','',
        f"Seven separate relation dimensions and {len(m['registry'])} evidence codes are in 08/09. There is no global weighting or priority ranking. The {len(m['human_crosswalk'])} frozen-judgment crosswalks are illustrative draft code associations, not retroactively invented researcher rationales. Original records, linguistic_basis, source locators and hashes remain visible.",
        'BHSA syntax corroborates linguistic observations; it never becomes MILAL parentage automatically. Theory-informed marker selection coexists with outcome-open adjudication.','',
        '## Unchanged Q1–Q5 worksheet','']
    for q in m['questions']:
        lines += ['### '+q['question_id'],'',q['question'],'','Allowed: '+', '.join(q['allowed_outcomes']),'','| Field | Value |','| --- | --- |']
        lines += [f'| {k} | {q[k]} |' for k in a.prep.REVIEW_FIELDS];lines+=['']
    return '\n'.join(lines)+'\n'


def derive(s):
    family=verbal_rows(s)+nominal(s);neighbors=shwb(s);context=reframing(s);add=candidate_addendum(s,family,neighbors,context)
    m=dict(family=family,neighbors=neighbors,context=context,cluster=cluster(s,family,neighbors,context),distribution=distribution(s,family,neighbors,context),
        addendum=add,crosswalk=crosswalk(s,family,neighbors,context),registry=criteria.registry(),human_crosswalk=human_crosswalk(s),questions=deepcopy(s['questions']),
        dependencies=dependencies(s,add),panels=panels(s),historical=deepcopy(s['files']),baseline_receipt=deepcopy(s['receipt']),
        new_human_judgments=[],new_structural_relations=[],native=deepcopy(s['native']))
    m['methodology']=criteria.document(m['registry']);m['negative']=controls(m,s);m['report']=report(m,s)
    return m


def payload_digest(m):
    return rowhash({k:({n:sha(v) for n,v in value.items()} if k=='historical' else value) for k,value in m.items() if k!='rerun_digest'})


def build(s):
    m=derive(s);m['rerun_digest']=payload_digest(derive(s));return m


def gates(m,s):
    checks={};verbal=[r for r in m['family'] if r['response_layer']==LAYERS[0]];nom=[r for r in m['family'] if r['response_layer']==LAYERS[1]]
    checks['BASELINE_0_1_ARTIFACT_VERIFIED']=m['baseline_receipt']==s['receipt'] and m['historical']==s['files'] and util.manifest_ok(m['historical'])
    checks['FROZEN_SOURCE_FILES']=len(s['frozen'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'][r['path']] for r in s['frozen'])
    checks['VERBAL_ANA_INVENTORY_FROZEN']=verbal==verbal_rows(s)
    checks['NOMINAL_MAANEH_DETECTED']=nom==nominal(s) and {'32:3','32:5'}<={r['reference'] for r in nom if r['category']=='CORE_ANA_NOMINAL_COGNATE'}
    checks['SHWB_WHOLE_BOOK_COVERAGE']=Counter(r['word_node'] for r in m['neighbors'])==Counter(w['node'] for c,w in all_words(s) if w['sp']=='verb' and norm(w['lex_utf8'])=='שוב')
    checks['SHWB_SEMANTIC_DISAMBIGUATION_PRESENT']=m['neighbors']==shwb(s) and len({r['category'] for r in m['neighbors']})>1 and any(r['category']=='SEMANTIC_REPLY_SHWB' and r['reference']=='32:14' for r in m['neighbors'])
    checks['DABAR_NOT_PROMOTED_TO_CORE_RESPONSE_LEXEME']=m['context']==reframing(s) and not any(r['lex']=='DBR[' for r in m['family']+m['neighbors'])
    checks['JOB_32_RESPONSE_CLUSTER_COMPLETE']=m['cluster']==cluster(s,m['family'],m['neighbors'],m['context']) and set(s['cfg']['cluster']['required'])<={r['reference'] for r in m['cluster']}
    checks['DISTRIBUTION_LAYERS_SEPARATE']=m['distribution']==distribution(s,m['family'],m['neighbors'],m['context'])
    checks['CANDIDATE_COUNT_UNCHANGED']=len(m['addendum'])==len(s['candidates'])==s['cfg']['expected']['candidates'] and [x['original_candidate_record'] for x in m['addendum']]==s['candidates']
    checks['CANDIDATE_EVIDENCE_ADDENDUM_EXACT']=m['addendum']==candidate_addendum(s,m['family'],m['neighbors'],m['context'])
    checks['NO_AUTOMATIC_REFINEMENT']=all(x['automatic_resolution'] is False and x['refinement_status']=='UNADJUDICATED' and not x['selected_alternative'] and not x['candidate_parent'] for x in m['addendum'])
    checks['REVIEW_STATUS_UNCHANGED']=m['questions']==s['questions'] and all(q[k]==('UNREVIEWED' if k=='review_status' else '') for q in m['questions'] for k in a.prep.REVIEW_FIELDS)
    checks['NO_NEW_HUMAN_JUDGMENT']=m['new_human_judgments']==[] and all(x['new_human_judgment'] is False for x in m['human_crosswalk'])
    checks['NO_NEW_STRUCTURAL_RELATION']=m['new_structural_relations']==[] and all(not x.get('automatic_relation') for x in m['family']+m['neighbors']+m['context']+m['cluster']+m['addendum'])
    human_files=[k for k in s['files'] if any(t in k for t in ('judgment','adjudication','closure_relations'))]
    checks['FROZEN_HSA_UNCHANGED']=bool(human_files) and all(m['historical'].get(k)==s['files'][k] for k in human_files)
    keys=[k for k in s['files'] if k.startswith('history/hsa3_prep/')]
    checks['HSA3_PREP_UNCHANGED']=bool(keys) and all(m['historical'].get(k)==s['files'][k] for k in keys)
    checks['CRITERIA_REGISTRY_DIMENSION_SPECIFIC']=m['registry']==criteria.registry() and {d for r in m['registry'] for d in r['evidence_dimension']}==set(criteria.DIMENSIONS)
    def unweighted(rows):return all(not any(x in k.lower() for x in ('weight','rank','score','priority')) for r in rows for k in r)
    checks['NO_GLOBAL_EVIDENCE_WEIGHTING']=unweighted(m['registry']) and unweighted(m['distribution']) and all(r['sole_basis_sufficient'] is False for r in m['registry'])
    checks['BHSA_MOTHER_NOT_AUTO_PARENT']=all(not r.get('automatic_parent_ids') for r in m['family']+m['neighbors']+m['context']) and not m['new_structural_relations']
    checks['NEGATIVE_CONTROLS_PRESENT']=m['negative']==controls(m,s) and all(r['status']=='PASS' for r in m['negative'])
    checks['EXACT_0_1_CROSSWALK']=m['crosswalk']==crosswalk(s,m['family'],m['neighbors'],m['context'])
    checks['FROZEN_JUDGMENT_CRITERIA_CROSSWALK']=m['human_crosswalk']==human_crosswalk(s)
    checks['SEAM_DEPENDENCY_ONLY']=m['dependencies']==dependencies(s,m['addendum'])
    checks['NATIVE_SOURCE_IDENTITY']=m['native']==s['native']
    checks['LOCAL_CONTINUATION_PANELS']=m['panels']==panels(s)
    checks['METHODOLOGY_DRAFT_FAITHFUL']=m['methodology']==criteria.document(m['registry'])
    checks['REVIEW_PACKET_FAITHFUL']=m['report']==report(m,s)
    checks['DETERMINISTIC_RERUN']=m['rerun_digest']==payload_digest(m)
    return [dict(gate=k,status='PASS' if ok else 'FAIL') for k,ok in checks.items()]


def serialize(m,s):
    gg=gates(m,s);require(all(g['status']=='PASS' for g in gg),canonical([g for g in gg if g['status']=='FAIL']))
    files={HISTORY+k:v for k,v in m['historical'].items()}
    for filename,key in [('01_response_lexical_family_inventory.csv','family'),('02_semantic_response_neighbor_inventory.csv','neighbors'),('03_response_context_reframing.csv','context'),
        ('04_job_32_response_cluster.csv','cluster'),('05_response_distribution.csv','distribution'),('06_ana_0_1_candidate_evidence_addendum.csv','addendum'),('07_ana_0_1_crosswalk.csv','crosswalk'),
        ('08_hsa_adjudication_criteria_registry.csv','registry'),('10_existing_judgment_criteria_crosswalk.csv','human_crosswalk'),('12_negative_controls.csv','negative'),
        ('13_hsa3_dependency_addendum.csv','dependencies'),('15_native_clause_evidence.csv','native'),('16_unchanged_review_questions.csv','questions'),('17_local_continuation_panels.csv','panels')]:files[filename]=util.csv_bytes(m[key])
    files['09_hsa_adjudication_criteria_registry.md']=m['methodology'].encode();files['11_ana_0_2_review_packet.md']=m['report'].encode()
    counts=dict(verbal=len(s['verbal']),verbal_nonanswer=sum(not r['answer_lexeme'] for r in s['verbal']),nominal_screen_candidates=sum(r['response_layer']==LAYERS[1] for r in m['family']),
        nominal_answer=sum(r.get('counts_as_response_family',False) for r in m['family']),nominal_positions=[r['reference'] for r in m['family'] if r.get('counts_as_response_family')],
        shwb=len(m['neighbors']),shwb_senses=dict(Counter(r['category'] for r in m['neighbors'])),shwb_lexemes=dict(Counter(r['lex'] for r in m['neighbors'])),cluster=len(m['cluster']),
        candidates=len(m['addendum']),context_evidence_candidates=len(m['context']),new_human_judgments=len(m['new_human_judgments']),new_structural_relations=len(m['new_structural_relations']),
        criteria_codes=len(m['registry']),criteria_dimensions=list(criteria.DIMENSIONS),judgment_crosswalks=len(m['human_crosswalk']),frozen_human=len(s['accounting']),unresolved=len(a.prep.decode_rows(s['files'][R43+'03_unresolved_parentage.csv'])))
    meta=dict(version='HSA3-ANA.0.2',mode=s['mode'],status='PASS',gate_count=len(gg)+1,baseline_commit=s['cfg']['baseline_commit'],baseline_receipt=m['baseline_receipt'],frozen_receipts=s['frozen'],execution=s['execution'],counts=counts,
        code_sha256={p:sha((ROOT/p).read_bytes()) for p in ['src/milal_hsa3_ana_response_family_addendum.py','src/milal_hsa_adjudication_criteria.py','src/milal_hsa3_ana_family_synthetic.py']},
        config_sha256=sha(CONFIG.read_bytes()),rerun_payload_sha256=m['rerun_digest'],rerun_gate_scope='TWO_INDEPENDENT_BUILDS; independent-process ZIP equality checked separately in validation',
        claim='TECHNICAL_EVIDENCE_ADDENDUM_AND_CRITERIA_DRAFT_NOT_HUMAN_ACCEPTANCE')
    files['90_run_metadata.json']=util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv',None);files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=k,sha256=sha(v)) for k,v in sorted(files.items())])
    seal();gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'));files['14_gates.csv']=util.csv_bytes(gg);seal()
    require(util.manifest_ok(files),'output manifest');return files


def publish(files,out):
    a.prep.publish(files,out)
    out=Path(out).resolve();zp=out.with_name(out.name+'_results.zip');meta=json.loads(files['90_run_metadata.json'])
    out.with_name(out.name+'_run.log').write_text(f"HSA3-ANA.0.2 PASS\nMode {meta['mode']}\nGates {meta['gate_count']} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n",encoding='utf-8')


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--self-test',action='store_true');args=p.parse_args(argv)
    s=load(args.tf_data,args.self_test);files=serialize(build(s),s)
    require(a.prep.r43.frozen_receipts(s['cfg'])==s['frozen'],'frozen sources changed during execution')
    if not args.self_test:require(sha((ROOT/s['cfg']['archive']['path']).read_bytes())==s['cfg']['archive']['sha256'],'0.1 archive changed during execution')
    for path,digest in s['execution']['data_hashes'].items():require(sha(Path(path).read_bytes())==digest,'BHSA source changed during execution')
    publish(files,args.out);print('HSA3-ANA.0.2 PASS '+str(Path(args.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
