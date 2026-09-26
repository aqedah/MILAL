"""Synthetic pair binding and ambiguous reference cases, without corpus controls."""
import copy
from pathlib import Path
from milal_q12_pipeline import indexes,constraints,write
from milal_q12_binding import compare_configurations,pair_anchors
from milal_q12_profiles import compare_dimensions
from milal_q12_validation import policy,measurements,GATES
from milal_q1_binding import outcome
from milal_mfr02r_data import table,digest
from milal_mfr02r_pipeline import code_fingerprint

GRAMMAR={'lexicons':{'speech':['SAY['],'subordinators':['THAT'],'subordinate_rela':['Objc','Adju']}}


def clause(cid,word,position,subject='NAME/',head=None,typ='WayX',time=None,reference=False):
    words=[dict(node=word,lex='SAY[',sp='verb',vt='impf',vs='qal',ps='p3',gn='m',nu='sg')]
    phrases=[dict(node=cid*100,word_ids=[word],function='Pred',typ='VP')]
    if subject:
        words.append(dict(node=word+1,lex=subject,sp='nmpr',vt='NA',vs='NA',ps='p3',gn='m',nu='sg'))
        phrases.append(dict(node=cid*100+1,word_ids=[word+1],function='Subj',typ='NP'))
    if time:
        node=word+len(words);words.append(dict(node=node,lex=time,sp='subs',vt='NA',vs='NA',ps='p3',gn='m',nu='sg'))
        phrases.append(dict(node=cid*100+2,word_ids=[node],function='Time',typ='NP'))
    edges=[] if head is None else [dict(head_node=head,dependent_node=cid,rela='Objc',resolution='EXACT_NODE_MEMBERSHIP')]
    mentions=[dict(node=word,lex='HE',kind='PRONOUN',png=['p3','m','sg'],identity='UNRESOLVED')] if reference else []
    return dict(clause_id=cid,position=position,word_ids=[w['node'] for w in words],clause_atom_ids=[cid+10000],
        clause_type=typ,WORD=words,PHRASE=phrases,CLAUSE=dict(native_annotations=edges),
        REFERENCE=dict(mentions=mentions),PARTICIPANT=dict(mentions=[]),book='Iob',chapter=1,verse=position+1,surface_hebrew='SYNTHETIC')


def data():
    return [clause(1,10,0),clause(2,12,1,subject=None,head=1,typ='InfC'),
        clause(3,20,2,time='DAY/'),clause(4,23,3,subject=None,head=3,typ='InfC')]


def semantic_checks():
    cfg,refs,binder=indexes(data(),GRAMMAR)
    positive=compare_configurations(cfg,'1','3','1','3')
    embedded=binder.evaluate('2','4',[dict(rule_id='W-P01',relation='PARATACTIC')])
    same=indexes([clause(1,10,0),clause(2,20,1)],GRAMMAR)[2].evaluate('1','2',[dict(rule_id='W-P01',relation='PARATACTIC')])
    checks=dict(profile_fields=all(k in cfg.profiles['1'] for k in ('reference_morphology','direct_speech_markers','temporal_adjuncts','locative_adjuncts','pre_predicate_constituents')),
        N1=not same['qualified_paths'],N2=not same['qualified_paths'],N8=positive['positive_source_binding'],
        N9=positive['textual_level']=='UNRESOLVED' and all(p['textual_level']=='UNRESOLVED' for p in cfg.profiles.values()),
        S1=positive['positive_source_binding'],S2=positive['correspondence_dimensions']['TIME_CONFIGURATION']['status']=='CORRESPONDING_VARIANT',
        SB11=any(w['mechanism']=='SB11' for w in embedded['witnesses']) and bool(embedded['qualified_paths']))
    cfg.configurations['1']['configuration_independence_status']='DEPENDENT_ON_TESTED_RELATION'
    checks['N5']=not compare_configurations(cfg,'1','3','1','3')['positive_source_binding']
    no_anchor=data()
    for r in no_anchor:
        for w in r['WORD']:
            if w['sp']=='nmpr':w['lex']='N'+str(r['clause_id'])
    c,_,_=indexes(no_anchor,GRAMMAR)
    checks['N4']=not compare_configurations(c,'1','3','1','3')['positive_source_binding']
    # Presence of time on both endpoints is not a pair-specific frame witness.
    time_data=[clause(1,10,0,subject=None,time='DAY/'),clause(2,20,1,subject=None,time='NIGHT/')]
    c,_,_=indexes(time_data,GRAMMAR)
    checks['generic_frames']=not pair_anchors(c.profiles['1'],c.profiles['2'])
    base=[clause(1,10,0),clause(2,20,1,subject=None,reference=True)]
    c,r,b=indexes(base,GRAMMAR);rw=r.by_target['2'][0]
    checks['S3']=rw['reference_status']=='UNIQUE_SURFACE_CANDIDATE' and not r.bindings('1','2')
    checks['N3']=rw['referential_identity']=='UNRESOLVED'
    lexical=indexes([clause(1,10,0),clause(2,20,1)],GRAMMAR)[1]
    checks['N2'] &= all(w['referential_identity']=='UNRESOLVED' for w in lexical.witnesses) and not lexical.bindings('1','2')
    ambiguous=[clause(1,10,0),clause(2,20,1),clause(3,30,2,subject=None,reference=True)]
    c,r,_=indexes(ambiguous,GRAMMAR)
    checks['N10']=r.by_target['3'][0]['reference_status']=='MULTIPLE_PLAUSIBLE'
    unit=[clause(1,10,0,subject=None),clause(2,11,1,head=1),clause(3,30,2,subject=None,reference=True)]
    unit[-1]['CLAUSE']['native_annotations']=[dict(head_node=12,dependent_node=30,rela='Rela',
        resolution='EXACT_NODE_MEMBERSHIP',reference_semantics='EXPLICIT_ANTECEDENT')]
    c,r,_=indexes(unit,GRAMMAR)
    checks['S4']=any(w['mechanism']=='SB03' and w['unit_membership_basis']['members']==['1','2'] for w in r.bindings('1','3'))
    unit[-1]['CLAUSE']['native_annotations'][0].pop('reference_semantics')
    checks['native_attachment_not_coreference']=not indexes(unit,GRAMMAR)[1].bindings('1','3')
    os=[outcome('1','3','HYPOTACTIC'),outcome('2','3','HYPOTACTIC')]
    g=constraints(os,{'1':0,'2':1,'3':2})
    checks['S5']=bool(g['conflicts']) and g['input_outcome_ids']==g['output_outcome_ids']
    checks['N6']=not constraints([],{} )['output_outcome_ids'] and not g['positive_binding']
    checks['N7']=not policy("def bad(): return 'P443836-443840'")['no_id_exception']
    many=[clause(i+1,10+i*3,i,subject=None) for i in range(100)]
    c,r,b=indexes(many,GRAMMAR)
    checks['S6']=all(not b.evaluate(str(i),str(j),[dict(rule_id='W-P01',relation='PARATACTIC')])['qualified_paths']
        for i in range(1,101) for j in range(i+1,101))
    checks['speech_preserved']=bool(c.profiles['1']['direct_speech_markers'])
    return checks,positive,embedded


def evidence_fixture():
    checks,_,_=semantic_checks()
    return dict(semantic=checks,policy=policy('def safe(): return None'),baseline='base',expected_baseline='base',frozen_differences=[],
        q1_verified=True,q11_verified=True,source_verified=True,raw_count=4,expected_raw_count=4,raw_errors=0,
        human_equal=True,human_count=1,expected_human_count=1,canonical_mothers=[],canonical_hierarchies=[],
        profile_count=4,source_clause_count=4,dependent_positives=0,unanchored_positives=0,invalid_positive_composition=0,
        reference_count=1,png_only_resolved=0,lexeme_only_resolved=0,circular_reference_bindings=0,
        sb12_input_ids=['a'],sb12_output_ids=['a'],sb12_positive=False,family_assigned_levels=0,
        events=['BLIND_STARTED','BLIND_FROZEN','CONTROLS_STARTED','CONTROLS_FINISHED'],blind_files_equal=True,
        full_external_analyses=0,generated_external_candidates=0,new_judgments=[],
        tests=dict(test_scope='FULL_REGRESSION',tests_run=1,failures=0,errors=0,skipped=0),fingerprint_matches=True,
        independent_equal=True,manifest_valid=True,analysis_books=['Iob'],fixture_identities_equal=True,
        analysis_scope='JOB',corpus_comparison_scope='HB_CORPUS',deferred_qualified=0)


MUTATIONS=list(zip(GATES,[('baseline','wrong'),('q1_verified',False),('q11_verified',False),('raw_errors',1),
    ('human_equal',False),('canonical_mothers',['bad']),('canonical_hierarchies',['bad']),('profile_count',0),
    ('dependent_positives',1),('semantic.N8',False),('unanchored_positives',1),('policy.no_score',False),
    ('policy.no_feature_threshold',False),('invalid_positive_composition',1),('semantic.SB11',False),('reference_count',0),
    ('png_only_resolved',1),('lexeme_only_resolved',1),('circular_reference_bindings',1),('sb12_output_ids',['new']),
    ('sb12_positive',True),('family_assigned_levels',1),('events',[]),('policy.no_id_exception',False),
    ('full_external_analyses',1),('new_judgments',['bad']),('tests.failures',1),('tests.skipped',1),
    ('independent_equal',False),('manifest_valid',False),('analysis_books',['Numeri']),('fixture_identities_equal',False),
    ('analysis_scope','HB_CORPUS'),('deferred_qualified',1)]))


def self_test(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    checks,positive,embedded=semantic_checks();e=evidence_fixture()
    checks['all_positive_gates']=all(r['passed'] for r in measurements(e))
    for gate,(key,value) in MUTATIONS:
        bad=copy.deepcopy(e);parts=key.split('.');obj=bad
        for part in parts[:-1]:obj=obj[part]
        obj[parts[-1]]=value
        checks['negative_'+gate]=not next(r['passed'] for r in measurements(bad) if r['gate']==gate)
    for name in ('a.csv','b.csv'):table(out/name,[dict(opening=positive,embedded=embedded)])
    checks['deterministic']=digest(out/'a.csv')==digest(out/'b.csv')
    receipt=dict(mode='SYNTHETIC',passed=all(checks.values()),checks=checks,code_fingerprint=code_fingerprint())
    write(out/'receipt.json',receipt)
    (out/'review.md').write_text('# Q1.2 synthetic review\n\nNon-identical time adjunct profiles bind through explicit corresponding-role anchors. '
        'Embedded positions qualify separately through SB11. Bare repeated formulas and generic time flags do not bind. '
        'A unique antecedent search candidate remains unresolved; an explicitly typed reference plus independent unit membership tests SB03. '
        'Global competing mothers remain alternatives.\n',encoding='utf8')
    if not receipt['passed']:raise ValueError('synthetic failed: '+repr([k for k,v in checks.items() if not v]))
    return receipt
