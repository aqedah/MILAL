"""JIN.0.8 authorized contract transcription; no graph migration or consumer."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import milal_jin_io as io
from milal_jin_layer_freeze import LAYERS, source_link
from milal_jin_postcontext_comparison import review_fields

ROOT = Path(__file__).resolve().parents[1]
HISTORY = 'history/jin_0_7/'
INVENTORY = 'history/jin_0_6/01_hierarchy_relation_inventory.csv'
APPLICATIONS = '03_relation_layer_historical_crosswalk.csv'
STATUS = 'REVISED_R4_4_CONTRACT_HUMAN_FROZEN'
READINESS = 'BLOCKED_PENDING_TOP_LEVEL_AND_REMAINING_HIERARCHY_AUDITS'
AXES = ['historical_status','adjudication_status','review_status','necessity_status',
        'strict_status','macro_status','frozen_status','supersession_status']
FIELDS = ['relation_id','source_id','target_id','relation_type','relation_layer','semantic_subtype',
          'polarity','directionality','adjudication_status','review_status','frozen_status',
          'strict_status','macro_status','human_supplied','derived_from_contract_decision',
          'automatic_resolution','evidence_ids','provenance_ids','historical_relation_id','limitations']
WORDING = '''MILAL is a layered typed graph overall, but hierarchy remains an explicitly typed analytical relation rather than a metaphor for all links.

Strict clause hierarchy and macro textual hierarchy are distinct.

Jin’s single-mother principle applies to strict hypotactic daughters.

By explicit methodological extension, a macro unit adjudicated as a macro hypotactic daughter likewise requires exactly one macro mother.

Paratactic units do not receive synthetic mothers merely to satisfy a tree representation.

Top-level/root cardinality is an empirical question for each hierarchy layer and is not pre-assumed.

Non-textual composition, transition, overlay, negative constraint and technical navigation do not substitute for textual mother-daughter relations.
'''
NEXT = '''# Next research scope

1. STRICT / MACRO TOP-LEVEL ROOT AUDIT, with separate evidence and outcomes.
2. Remaining strict-relation adjudication scope review, including the source-linked historical review backlog.
3. If needed, targeted strict mother audits.
4. Contract migration dry-run.
5. Only then consider R4.4 consumer implementation.

Participant arc remains UNADJUDICATED, separate future overlay research and not an implementation blocker unless later explicitly decided otherwise.
No audit, root selection, migration, parent synthesis or consumer is executed here.
'''


def config():
    return json.loads((ROOT/'config/r4_4_contract_jin_0_8_job.json').read_bytes())


def authority(cfg, request):
    io.require(io.sha(request)==cfg['source_request']['sha256'], 'exact researcher source')
    io.require([d['question_id'] for d in cfg['decisions']]==[f'R{i}' for i in range(1,11)], 'ten ordered decisions')
    for d in cfg['decisions']:
        b=request[d['byte_start']:d['byte_end']]
        io.require(b.decode()==d['approved_text'] and io.sha(b)==d['excerpt_sha256'], 'source excerpt')
        q=d['question_id'];qualification='QUALIFICATION' if q in ('R3','R8') else 'REWORDING' if q=='R10' else 'NONE'
        phrase='ACCEPTED with qualification' if qualification=='QUALIFICATION' else 'ACCEPTED with rewording' if qualification=='REWORDING' else 'ACCEPTED'
        io.require(d['decision']=='ACCEPTED' and d['qualification_type']==qualification and phrase in b.decode(), 'explicit approval/qualification')
    inv=[dict(invariant_id='CINV-R44-%03d'%int(n),approved_text=t) for n,t in re.findall(r'CINV-(\d\d)\r?\n([^\r\n]+)',request.decode())]
    io.require(cfg['invariants']==inv and len(inv)==20,'twenty source-grounded invariants')


def contract():
    return dict(representation='LAYERED_TYPED_GRAPH', relation_layers=list(LAYERS),
        minimum_fields=list(dict.fromkeys(FIELDS+AXES)), status_axes=AXES,
        strict_mother_rule=dict(placement='STRICT_HYPOTACTIC_DAUGHTER',requires_human_adjudication=True,direct_mother_count=1),
        macro_mother_rule=dict(placement='MACRO_HYPOTACTIC_DAUGHTER',requires_human_adjudication=True,direct_mother_count=1,authority='EXPLICIT_METHODOLOGICAL_EXTENSION_R3'),
        macro_placement_modes=['MACRO_HYPOTACTIC_DAUGHTER','MACRO_PARATACTIC_UNIT','MACRO_TOP_LEVEL','ROOT_CANDIDATE','MACRO_TRANSITIONAL_PLACEMENT','MACRO_PLACEMENT_UNRESOLVED'],
        synthetic_strict_mother=False,synthetic_macro_mother=False,composition_can_be_mother=False,
        technical_root_can_be_mother=False,macro_implies_strict=False,strict_implies_macro=False,
        negative_assertion_equals_absence=False,unresolved_strict_with_accepted_macro=True,
        lower_layer_revision_requires='EXPLICIT_VERSIONED_SUPERSEDING_HUMAN_ADJUDICATION',
        validation_by_layer={'STRICT_CLAUSE_HIERARCHY':'DIRECTED_CYCLE_INVALID; ADJUDICATED_DAUGHTER_EXACTLY_ONE_MOTHER',
          'MACRO_TEXTUAL_HIERARCHY':'DIRECTED_CYCLE_INVALID; ADJUDICATED_DAUGHTER_EXACTLY_ONE_MOTHER',
          'STRICT_CLAUSE_PARATAXIS':'RECIPROCAL_ALLOWED','MACRO_TEXTUAL_PARATAXIS':'RECIPROCAL_ALLOWED',
          'COMPOSITION':'SEPARATE_MEMBERSHIP_ORDER','TRANSITION':'NO_IMPLIED_MOTHER',
          'OVERLAY_RESPONSIO':'LONG_DISTANCE_CROSSINGS_ALLOWED','NEGATIVE_CONSTRAINT':'EXPLICIT_ASSERTION_NOT_ABSENCE',
          'TECHNICAL_NAVIGATION':'EXCLUDED_FROM_ANALYTICAL_HIERARCHY'},
        root_cardinality='EMPIRICAL_PER_HIERARCHY_LAYER',root_candidates_selected=[],
        consumer_implemented=False,migration_executed=False,contract_status=STATUS,implementation_readiness=READINESS)


def scope():
    common=['ONE_UNIQUE_ROOT','MULTIPLE_TOP_LEVEL_PARATACTIC_UNITS','ONE_ROOT_PLUS_TOP_LEVEL_PARATAXIS',
            'OTHER_EXPLICITLY_SUPPORTED_CONFIGURATION','INSUFFICIENT_EVIDENCE']
    return dict(strict=dict(audit='STRICT_TOP_LEVEL_ROOT_AUDIT',outcomes=common,
            evidence=['raw clause type','formal correspondence','clause-level parataxis/hypotaxis','participant/reference continuity','syntactic dependency','textual level','paragraph-opening patterns']),
        macro=dict(audit='MACRO_TOP_LEVEL_ROOT_AUDIT',outcomes=common+['ONE_HIGHER_MACRO_FRAME'],
            evidence=['major onset/closure markers','multi-clause repeated configuration','macro parataxis','macro containment','discourse/narrative frame','transition evidence','distribution across whole book']),
        forbidden=['nearest preceding heuristic','chapter boundary alone','technical root','composition group as mother','traditional outline alone'],
        assumptions=dict(job_1_1_is_root=False,job_book_is_analytical_root=False,tree_library_requires_one_root=False),
        limitation='Evidence plan only; no participant identity resolution or future audit executed.')


def unique_member(files, suffix):
    hits=[p for p in files if p.endswith('/'+suffix) or p==suffix]
    io.require(len(hits)==1,'unique historical source '+suffix)
    return hits[0]


def primary(cfg, crosswalk):
    out=[]
    for d in cfg['decisions']:
        q=d['question_id']
        out.append(dict(decision_id='JIN08:'+q,question_id=q,decision='ACCEPTED',decision_status='ACCEPTED',
            qualification_type=d['qualification_type'],approved_text=d['approved_text'],
            methodological_scope=d['approved_text'].splitlines()[0],affected_relation_layers=list(LAYERS),
            invariant_ids=d['invariant_ids'],historical_question_links=[r['historical_question_id'] for r in crosswalk if q in r['revised_question_ids']],
            researcher_supplied=True,source_stage='JIN_0_8',provenance=dict(source_sha256=cfg['source_request']['sha256'],byte_start=d['byte_start'],byte_end=d['byte_end'],excerpt_sha256=d['excerpt_sha256']),
            version=cfg['stage'],recorded_date=cfg['version_date'],timestamp_precision='DAY_NO_EVENT_TIME_INFERRED',rewrites_history=False))
    return out


def fixtures(files, inv, apps):
    definitions=[('F1',['1:13'],'macro accepted / strict unresolved'),('F2',['3:1','3:2'],'macro speech frame / strict unresolved'),
       ('F3',['40:1'],'macro accepted / strict unresolved'),('F4',['28:1'],'NO_NEW_BOUNDARY'),
       ('F5',['42:16'],'NO_NEW_BOUNDARY'),('F6',['1:6','2:1'],'macro parataxis, not strict'),
       ('F7',['37:24','38:1'],'negative constraints and separate overlay coexist; overlay is not a new direct 37:24→38:1 edge'),
       ('F8',['31:40'],'closure / composition / transition / negative dimensions coexist'),
       ('F9',['2:11'],'NO_MACRO_MOTHER_FOUND; composition and negative facts coexist'),
       ('F10',['32:1'],'NO_MACRO_MOTHER_FOUND; accepted transition preserved')]
    byid={r['historical_relation_id']:r for r in apps};out=[]
    for fid,refs,meaning in definitions:
        selected=[(i,r) for i,r in enumerate(inv,1) if r['source_ref'] in refs or r['target_ref'] in refs]
        io.require(bool(selected),'fixture source missing '+fid)
        types={r['relation_type'] for _,r in selected};layers={r['historical_layer'] for _,r in selected}
        typing=[byid[r['relation_id']] for _,r in selected if r['relation_id'] in byid]
        if fid in ('F1','F2','F3'):
            relevant=[r for r in typing if r['source_ref'] in refs and r['historical_relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE','CONTINUES_WITHIN')]
            io.require(len(relevant)==(2 if fid=='F2' else 1) and all(r['macro_status']=='ACCEPTED' and r['strict_status']=='UNRESOLVED_UNPROVEN' and r['approved_relation_layer']=='MACRO_TEXTUAL_HIERARCHY' for r in relevant),'macro/strict fixture split '+fid)
        if fid in ('F4','F5'):io.require(any(r['source_ref'] in refs and r['approved_semantic_subtype']=='NO_NEW_BOUNDARY' for r in typing),'no-boundary fixture '+fid)
        if fid=='F6':io.require(any(r['source_ref']=='1:6' and r['target_ref']=='2:1' and r['approved_relation_layer']=='MACRO_TEXTUAL_PARATAXIS' for r in typing),'macro parataxis fixture')
        if fid=='F7':io.require({'NEGATIVE_CONSTRAINT','OVERLAY_RESPONSIO'}<=layers,'negative/overlay coexistence')
        if fid=='F8':io.require({'DIRECT_LOCAL_CLOSURE','TERMINATES_ENCLOSING_GROUP','POST_CLOSURE_TRANSITION'}<=types,'closure dimensions')
        if fid=='F9':io.require('GROUP_MEMBER_OF' in types,'macro unresolved other facts')
        if fid=='F10':io.require('TRANSITION_COMPONENT' in types,'transition preserved')
        out.append(dict(fixture_id=fid,references=refs,contract_interpretation=meaning,
            historical_relation_ids=[r['relation_id'] for _,r in selected],
            historical_relation_types=sorted({r['relation_type'] for _,r in selected}),
            historical_layers=sorted({r['historical_layer'] for _,r in selected}),
            approved_typing=[deepcopy(byid[r['relation_id']]) for _,r in selected if r['relation_id'] in byid],
            source_records=[source_link(files,INVENTORY,i,r) for i,r in selected],
            new_strict_mother=False,new_macro_mother=False,layer_collapsed=False))
    return out


def open_questions(files, apps):
    out=[]
    def add(qid,kind,question,links):
        out.append(dict(question_id=qid,question_class=kind,question=question,source_records=links,
            disposition='SCOPE_REVIEW_REQUIRED_NOT_AN_ASSERTED_EDGE',**review_fields()))
    for ref in ('1:13','3:1/3:2','40:1'):
        rs=[r for r in apps if r['source_ref'] in (['3:1','3:2'] if '/' in ref else [ref])]
        add('STRICT:'+ref,'STRICT_RELATION_OPEN','Resolve strict clause dependency independently of accepted macro interpretation: '+ref,rs)
    for ref in ('2:11','32:1'):
        add('MACRO:'+ref,'MACRO_RELATION_OPEN','Determine macro placement without presuming daughterhood or assigning a mother: '+ref,[dict(member='90_run_metadata.json',sha256=io.sha(files['90_run_metadata.json']),field='mother_status',reference=ref)])
    for layer in ('STRICT','MACRO'):
        add('ROOT:'+layer,'TOP_LEVEL_ROOT_OPEN','Determine empirical top-level configuration: '+layer,[dict(source_decision='JIN08:R10')])
    for r in apps:
        if r['macro_status']=='PROVISIONAL_CURRENT_AUDIT':
            add('PROVISIONAL:'+r['historical_relation_id'],'MACRO_RELATION_OPEN','Review provisional macro continuation; typing approval is not individual acceptance.',[r])
    # Preserve every prior contextual case with exact subsequent batch judgments.
    # The scope question does not reopen the macro judgment or assert a strict edge.
    p=unique_member(files,'24_contextual_human_review_cases.csv');bp=unique_member(files,'01_jin_human_batch1_decisions.csv')
    batch=io.rows(files[bp])
    for i,r in enumerate(io.rows(files[p]),1):
        bid=r['review_case_id'];later=[source_link(files,bp,j,d) for j,d in enumerate(batch,1) if bid in d['contextual_review_case_ids']]
        add('SCOPE:'+bid,'STRICT_RELATION_OPEN','Review remaining strict applicability/scope of this historical candidate; retain later macro/control adjudications. No claim that a strict daughter exists.',[source_link(files,p,i,r)]+later)
    return out


def build(files,cfg,request):
    authority(cfg,request);io.require(io.manifest_ok(files),'JIN.0.7 manifest')
    inv=io.rows(files[INVENTORY]);apps=io.rows(files[APPLICATIONS]);oldq=io.rows(files['08_historical_contract_question_crosswalk.csv'])
    io.require(len(inv)==cfg['expected_registry_count'] and len({r['relation_id'] for r in inv})==len(inv),'historical registry identity/count')
    io.require(len(apps)==cfg['expected_applications'] and len({r['historical_relation_id'] for r in apps})==len(apps),'derived identity/count')
    byid={r['relation_id']:r for r in inv}
    for r in apps:
        io.require(r['historical_relation_id'] in byid,'missing historical relation identity')
        io.require(r['historical_source']['record']==byid[r['historical_relation_id']] and not r['migrated'] and not r['new_parent_edge'],'exact historical row link')
    io.require([r['historical_question_id'] for r in oldq]==[f'Q{i}' for i in range(1,10)],'historical questions')
    meta=json.loads(files['90_run_metadata.json'])
    io.require(meta['mother_status']=={'2:11':'NO_MACRO_MOTHER_FOUND','32:1':'NO_MACRO_MOTHER_FOUND'} and meta['participant_arc']=='UNADJUDICATED','upstream unresolved states')
    ds=primary(cfg,oldq);invs=[dict(**r,source_decisions=[d['decision_id'] for d in ds if r['invariant_id'] in d['invariant_ids']],derived_from_contract_decision=True,new_primary_human_decision=False,version=cfg['stage']) for r in cfg['invariants']]
    cw=[dict(historical_question_id=r['historical_question_id'],historical_question_text=r['historical_question'],historical_status=r['historical_status'],revised_contract_effect='SUPERSEDED_FOR_ACTIVE_REVIEW_BY_REVISED_R1_R10',covered_by_R1_R10=r['revised_question_ids'],still_open=False,notes='Contract question superseded only; empirical hierarchy questions remain open.',historical_source=deepcopy(r)) for r in oldq]
    derived=[dict(historical_relation_id=r['historical_relation_id'],derived_from_contract_decision=True,source_decisions=['JIN08:R1','JIN08:R4','JIN08:R9'],jin07_application=deepcopy(r),new_analytical_relation=False) for r in apps]
    aa={r['historical_relation_id']:r for r in apps};preview=[]
    for r in inv:
        a=aa.get(r['relation_id'])
        preview.append(dict(historical_relation_id=r['relation_id'],historical_relation_type=r['relation_type'],future_relation_layer=a['approved_relation_layer'] if a else 'UNRESOLVED_NOT_ADJUDICATED',future_semantic_subtype=a['approved_semantic_subtype'] if a else '',migration_needed='FUTURE_SCHEMA_REVIEW',human_decision_source=a['decision_id'] if a else [],migration_status='NOT_EXECUTED'))
    return dict(primary=ds,invariants=invs,contract=contract(),scope=scope(),crosswalk=cw,fixtures=fixtures(files,inv,apps),
        preview=preview,derived=derived,questions=open_questions(files,apps),history=deepcopy(files),mother_status=meta['mother_status'],
        participant_arc=meta['participant_arc'],new_relations=[],new_parents=[],new_composition=[],new_roots=[],new_participant=[],migrations=[])


def gates(m,e):
    checks={'TEN_PRIMARY_DECISIONS':len(m['primary'])==10 and len({r['question_id'] for r in m['primary']})==10}
    for i in range(1,11):
        key=f'R{i}_ACCEPTED'+('_WITH_QUALIFICATION' if i in (3,8) else '_WITH_REWORDING' if i==10 else '')
        checks[key]=[r for r in m['primary'] if r['question_id']==f'R{i}']==[r for r in e['primary'] if r['question_id']==f'R{i}'] and any(r['question_id']==f'R{i}' and r['decision']=='ACCEPTED' for r in m['primary'])
    for name,key in [('CONTRACT_INVARIANTS_FROZEN','invariants'),('HISTORICAL_Q1_Q9_CROSSWALK','crosswalk'),('ALL_FIXTURES_PRESERVED','fixtures'),('MIGRATION_PREVIEW_ONLY','preview'),('DERIVED_INTERPRETATIONS_PRESERVED','derived'),('OPEN_SCOPE_COMPLETE','questions')]:checks[name]=m[key]==e[key]
    c=m['contract'];ec=contract()
    for name,key in [('RELATION_LAYER_VOCABULARY_FROZEN','relation_layers'),('STRICT_SINGLE_MOTHER_SCOPE_CORRECT','strict_mother_rule'),('MACRO_SINGLE_MOTHER_SCOPE_CORRECT','macro_mother_rule'),('SCHEMA_STATUS_AXES_SEPARATE','minimum_fields'),('STATUS_AXES_FROZEN','status_axes'),('LAYER_SPECIFIC_VALIDATION','validation_by_layer'),('SUPERSEDING_ADJUDICATION_REQUIRED','lower_layer_revision_requires')]:checks[name]=c[key]==ec[key]
    checks['NO_SYNTHETIC_MACRO_PARENT']=not c['synthetic_macro_mother'] and not m['new_parents']
    checks['NO_SYNTHETIC_STRICT_PARENT']=not c['synthetic_strict_mother'] and not m['new_parents']
    checks['COMPOSITION_NOT_MOTHER']=not c['composition_can_be_mother']
    checks['TECHNICAL_ROOT_NOT_ANALYTICAL_ROOT']=not c['technical_root_can_be_mother'] and not m['scope']['assumptions']['job_book_is_analytical_root']
    checks['HISTORICAL_RELATIONS_UNCHANGED']=m['history']==e['history']
    checks['HISTORICAL_Q1_Q9_UNCHANGED']=all(m['history'].get(k)==v for k,v in e['history'].items() if 'question' in k or 'review_packet' in k)
    for fid,key in [('F1','JOB_1_13_MACRO_STRICT_SPLIT_PRESERVED'),('F2','JOB_3_1_2_MACRO_STRICT_SPLIT_PRESERVED'),('F3','JOB_40_1_MACRO_STRICT_SPLIT_PRESERVED'),('F4','JOB_28_1_NO_NEW_BOUNDARY'),('F5','JOB_42_16_NO_NEW_BOUNDARY'),('F6','SAME_LEVEL_MACRO_PARATAXIS'),('F7','NEGATIVE_OVERLAY_COEXISTENCE'),('F8','JOB_31_40_TYPED_DIMENSIONS')]:
        checks[key]=[r for r in m['fixtures'] if r['fixture_id']==fid]==[r for r in e['fixtures'] if r['fixture_id']==fid]
    for ref,key in [('2:11','JOB_2_11_UNRESOLVED'),('32:1','JOB_32_1_UNRESOLVED')]:checks[key]=m['mother_status'].get(ref)=='NO_MACRO_MOTHER_FOUND' and not m['new_parents']
    checks['NO_ROOT_SELECTED']=not m['new_roots'] and not c['root_candidates_selected'] and c['root_cardinality']=='EMPIRICAL_PER_HIERARCHY_LAYER'
    for layer in ('strict','macro'):checks[layer.upper()+'_TOP_LEVEL_AUDIT_SCOPED']=m['scope'][layer]==scope()[layer]
    checks['AUDIT_FORBIDDEN_HEURISTICS']=m['scope']==scope()
    checks['NO_RELATION_MIGRATION']=not m['migrations'] and not c['migration_executed'] and all(r['migration_status']=='NOT_EXECUTED' for r in m['preview'])
    for key,name in [('new_relations','NO_NEW_ANALYTICAL_RELATION'),('new_parents','NO_NEW_PARENT'),('new_composition','NO_NEW_COMPOSITION'),('new_participant','NO_NEW_PARTICIPANT')]:checks[name]=not m[key]
    checks['NO_R4_4_CONSUMER']=not c['consumer_implemented']
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED'
    checks['COMPLETE_CONTRACT_FROZEN']=c==ec
    return checks


def render(m,cfg,request):
    f={HISTORY+k:v for k,v in m['history'].items()}
    tables={'01_revised_contract_human_decisions.csv':m['primary'],
       '02_revised_contract_decision_provenance.csv':[dict(decision_id=d['decision_id'],**d['provenance']) for d in m['primary']],
       '03_contract_invariants.csv':m['invariants'],'04_relation_layer_vocabulary.csv':[dict(relation_layer=x,source_decision='JIN08:R1') for x in m['contract']['relation_layers']],
       '05_historical_q1_q9_crosswalk.csv':m['crosswalk'],'06_key_contract_fixtures.csv':m['fixtures'],
       '07_historical_relation_migration_preview.csv':m['preview'],'08_open_strict_macro_questions.csv':m['questions'],
       '14_derived_contract_interpretations.csv':m['derived']}
    f.update({k:io.csv_bytes(v) for k,v in tables.items()})
    f['09_top_level_root_audit_scope.md']=('# Separate empirical top-level audits\n\n```json\n'+io.js(m['scope']).decode()+'```\n').encode()
    spec='# Human-frozen revised contract\n\n'+WORDING+'\n```json\n'+io.js(m['contract']).decode()+'```\n\n'
    for d in m['primary']:spec+='## '+d['question_id']+' — '+d['qualification_type']+'\n\n'+d['approved_text']+'\n'
    spec+='\n## Versioned invariants\n\n'+'\n\n'.join(r['invariant_id']+': '+r['approved_text'] for r in m['invariants'])+'\n'
    f['10_revised_r4_4_contract_spec.md']=spec.encode()
    f['11_revised_contract_validation_report.md']=('# Contract freeze validation\n\n'+WORDING+f"\nPrimary decisions: {len(m['primary'])}; derived interpretation records: {len(m['derived'])}; invariants: {len(m['invariants'])}; fixtures: {len(m['fixtures'])}; open scope records: {len(m['questions'])}.\n\n"+
       'The scope records include historical candidate applicability questions, not newly established strict relations. Exact source rows and subsequent JIN.0.4 judgments remain attached. Prior JIN.0.1/JIN.0.2 candidate inventories remain lossless in history; JIN.0.3 supplies the consolidated human review cases.\n\n'+
       'Migration, new analytical relations, parents, composition, roots and participant overlays: 0. Seven provisional continuations remain provisional. Historical Q1–Q9 and JIN.0.7 R1–R10 blank review fields remain unchanged; only the new contract layer records acceptance.\n\n'+STATUS+' / '+READINESS+'\n\nSee 13_gates.csv for computed run checks. Full regression and independent rerun are external release checks, not claimed by this process alone.\n').encode()
    f['12_next_scope.md']=NEXT.encode();f['15_contract.json']=io.js(m['contract']);f['16_exact_researcher_source.txt']=request
    return f


def preflight(cfg,request,pins,baseline,archive_sha,consumer_files,synthetic=False):
    return dict(BASELINE_COMMIT_VERIFIED=baseline==cfg['baseline'],JIN_0_7_FROZEN_VERIFIED=pins==cfg['frozen_files'] and (synthetic or archive_sha==cfg['archive']['sha256']),EXACT_RESEARCHER_SOURCE=io.sha(request)==cfg['source_request']['sha256'],NO_CONSUMER_FILES=not consumer_files)


def execute(out,self_test=False):
    cfg=config();request=(ROOT/cfg['source_request']['path']).read_bytes()
    if self_test:
        from milal_jin_contract_freeze_fixture import fixture
        files,cfg=fixture(cfg);archive_sha=io.sha(io.js({k:io.sha(v) for k,v in files.items()}))
    else:
        b=(ROOT/cfg['archive']['path']).read_bytes();archive_sha=io.sha(b)
        io.require(archive_sha==cfg['archive']['sha256'],'pinned JIN.0.7 ZIP');files=io.archive(b)
    pins={p:io.sha((ROOT/p).read_bytes()) for p in cfg['frozen_files']}
    baseline=subprocess.check_output(['git','rev-parse',cfg['baseline']],cwd=ROOT,text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',baseline,'HEAD'],cwd=ROOT,check=True)
    checks=preflight(cfg,request,pins,baseline,archive_sha,list((ROOT/'src').glob('*r4_4*.py'))+list((ROOT/'scripts').glob('*r4_4*')),self_test)
    m=build(files,cfg,request);checks.update(gates(m,build(files,cfg,request)))
    io.require(all(checks.values()),'failed gates '+str([k for k,v in checks.items() if not v]))
    f=render(m,cfg,request)
    f['90_run_metadata.json']=io.js(dict(stage=cfg['stage'],mode='SYNTHETIC' if self_test else 'REAL_FROZEN_JIN_0_7',status='PASS',contract_status=STATUS,implementation_readiness=READINESS,
        baseline=baseline,archive_sha256=archive_sha,pins=pins,primary_decisions=len(m['primary']),derived_interpretations=len(m['derived']),invariants=len(m['invariants']),open_questions=len(m['questions']),
        new_relations=len(m['new_relations']),new_parents=len(m['new_parents']),new_composition=len(m['new_composition']),new_roots=len(m['new_roots']),new_participant=len(m['new_participant']),migrations=len(m['migrations']),
        participant_arc=m['participant_arc'],mother_status=m['mother_status'],code_sha256=io.sha(Path(__file__).read_bytes()),external_release_gates=['DETERMINISTIC_RERUN','REGRESSION_PASS']))
    io.seal(f);checks['MANIFEST_VALID']=io.manifest_ok(f)
    f['13_gates.csv']=io.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]);io.seal(f)
    zp=io.publish(f,Path(out));print(json.dumps(dict(zip=str(zp),sha256=io.sha(zp.read_bytes()),gates=len(checks),primary=len(m['primary']),derived=len(m['derived']),open_questions=len(m['questions']))));return f


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--self-test',action='store_true');a=p.parse_args();execute(a.out,a.self_test)
