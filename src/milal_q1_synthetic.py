"""Executable Q1 controls; synthetic source witnesses never replace real input."""
from pathlib import Path
from milal_q1_binding import qualify, witness, outcome, pivot, SourceIndex, QUALIFIED
from milal_mfr02r_data import table, rows


def match(rid='W-A01',relation='HYPOTACTIC'):
    return dict(rule_id=rid,relation=relation,required_feature_witnesses=[['explicit_subordinator']])


def native_witness(source='1',target='2'):
    return witness('SB01','DIRECT_BINDING',source,target,
        dict(native_edges=[dict(head_node=int(source),dependent_node=int(target),rela='Objc')]),['HYPOTACTIC'])


def configuration(source='1',target='2'):
    return witness('SB06','CONFIGURATION_BINDING',source,target,
        dict(source_nodes=[source,'3','4'],target_nodes=[target,'5','6'],
             repeated_configuration='SYNTHETIC_EXPLICIT_CONFIGURATION'),['PARATACTIC'],
        independent_correspondence_and_same_line=True)


def semantic_checks():
    a=match();p=match('W-P01','PARATACTIC');h=match('W-H01')
    direct=qualify('1','2',[a],[native_witness()])
    unrelated=qualify('100','2',[a],[])
    remote=qualify('1','100000',[a],[native_witness('1','100000')])
    para=qualify('1','2',[p],[configuration()])
    active=witness('SB04','DIRECT_BINDING','1','2',dict(native_context='SYNTHETIC_BOUND_PAIR',mentions=[11,22]),
                   ['HYPOTACTIC'],active_participant_context='CONTINUED')
    same=[outcome('1','2','HYPOTACTIC') for _ in range(100)]
    different=[outcome('1','3','HYPOTACTIC'),outcome('2','3','HYPOTACTIC')]
    cases={
        'S1':direct['qualification']=='QUALIFIED_DIRECT',
        'S2':unrelated['qualification'] in ('SEARCH_ONLY','EVIDENCE_ONLY'),
        'S3':remote['qualification']=='QUALIFIED_DIRECT',
        'S4':not qualify('1','2',[p],[])['qualified_paths'],
        'S5':para['qualification']=='QUALIFIED_CONFIGURATION',
        'S6':not qualify('1','2',[h],[])['qualified_paths'],
        'S7':qualify('1','2',[h],[active])['qualification']=='QUALIFIED_DIRECT',
        'S8':len({o['structural_outcome_group_id'] for o in same})==1,
        'S9':pivot('2',same,True)['status']=='VARIANT_MEMBER_NON_PIVOT',
        'S10':pivot('3',different,True)['status']=='VARIANT_DECISION_PIVOT',
        'S11':pivot('2',same,True)['outcome_count']==1,
        'S12':len({o['mother_if_hypotactic'] for o in different})==2,
        'S13':not qualify('1','2',[dict(a,corpus_analogue=True)],[])['qualified_paths'],
        'S14':not qualify('1','2',[dict(p,prosody=True)],[])['qualified_paths'],
    }
    original=[dict(candidate_id=str(i),source=i,target=101) for i in range(100)]
    copy=[dict(x) for x in original]
    qualified=[qualify(str(r['source']),'101',[a],[]) for r in original]
    cases['S15']=original==copy and len(qualified)==len(original)
    return dict(cases=cases,target_only_rejected=cases['S2'],same_type_only_rejected=cases['S4'],
        inactive_participant_rejected=cases['S6'],corpus_only_rejected=cases['S13'],
        prosody_only_rejected=cases['S14'],many_rules_one_outcome=cases['S8'] and cases['S11'],
        membership_only_nonpivot=cases['S9'] and not pivot('1',[],True)['review_required'],
        distinct_positive_pivot=cases['S10'],NO_DISTANCE_CUTOFF=cases['S3'],
        NO_TOP_N=len(qualify('1','2',[match('SYNTHETIC-'+str(i)) for i in range(100)],[native_witness()])['qualified_paths'])==100,
        NO_NUMERIC_SCORE=all(qualify('1','2',[dict(a,score=n)],[native_witness()])==direct for n in (-100,0,100)))


def self_test(out):
    from milal_q1_pipeline import run_blind, ROOT, write_json
    from milal_mfr02r_grammar import load_registry
    out=Path(out)
    if out.exists():raise ValueError('fresh synthetic directory required')
    source=source_fixture(out/'source')
    grammar=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
    a=run_blind(source,out/'a',grammar);b=run_blind(source,out/'b',grammar)
    equality={p.name:p.read_bytes() for p in (out/'a').iterdir()}=={p.name:p.read_bytes() for p in (out/'b').iterdir()}
    checks=semantic_checks()
    if not all(checks['cases'].values()) or not equality:raise ValueError('synthetic invariant failed')
    report=dict(mode='SYNTHETIC',checks=checks,bytes_equal=equality,metrics=a)
    write_json(out/'self_test.json',report)
    (out/'synthetic_review.md').write_text('# Q1 synthetic review\n\n'+
        '\n'.join(f'- {k}: {v}' for k,v in checks['cases'].items())+
        '\n\nSearch pairs remain available; assignments are candidates only.\n'+
        'A selected relation versus UNDECIDED is not a decision pivot.\n',encoding='utf8',newline='\n')
    return report


def source_fixture(directory):
    """A consistent generated source, including positive native dependencies."""
    import json
    from milal_mfr02r_synthetic import sample
    from milal_mfr02r_engine import run_engine
    from milal_mfr02r_grammar import load_registry
    from milal_mfr02r_data import manifest
    from milal_q1_pipeline import ROOT
    directory=Path(directory);job=directory/'blind/job'
    registry=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
    labels=json.loads((ROOT/'config/mfr_0_2r_evidence_labels.json').read_text())
    native=[dict(dependent_node=t,head_node=s,rela='Objc',status='SYNTHETIC_NATIVE_ANNOTATION',
                 source_feature_sha256='SYNTHETIC',relation_feature_sha256='SYNTHETIC') for s,t in ((1,2),(1,4),(2,4),(4,5))]
    run_engine(sample(),registry,native,job,label_definitions=labels,analysis_scope='SYNTHETIC',comparison_scope='SYNTHETIC')
    table(directory/'mfr02a_original_decisions.csv',[dict(decision_id='SYNTHETIC-'+str(i),source_clause_ids=[1],target_clause_ids=[4],researcher_decision='UNRESOLVED') for i in range(13)])
    manifest(directory)
    return directory
