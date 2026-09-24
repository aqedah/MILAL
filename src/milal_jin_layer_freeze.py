"""JIN.0.7: transcribe six authorized decisions, never migrate the graph."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import re
import subprocess
import milal_jin_io as io
from milal_jin_postcontext_comparison import review_fields

ROOT=Path(__file__).resolve().parents[1]
HISTORY='history/jin_0_6/'
INVENTORY='01_hierarchy_relation_inventory.csv'
LAYERS=('STRICT_CLAUSE_HIERARCHY','STRICT_CLAUSE_PARATAXIS','MACRO_TEXTUAL_HIERARCHY',
        'MACRO_TEXTUAL_PARATAXIS','COMPOSITION','TRANSITION','OVERLAY_RESPONSIO','NEGATIVE_CONSTRAINT','TECHNICAL_NAVIGATION')
CONTINUATION=('STRICT_SYNTACTIC_CONTINUATION','MACRO_TEXTUAL_CONTINUATION','NO_NEW_BOUNDARY')
QUESTIONS=(
 'Adopt LAYERED_TYPED_GRAPH as canonical overall representation, with STRICT_CLAUSE_HIERARCHY and MACRO_TEXTUAL_HIERARCHY as distinct analytical layers?',
 'Apply Jin single-mother invariant ONLY to units adjudicated as strict hypotactic daughters?',
 'Require every MACRO textual unit to have a mother, or allow macro paratactic/root/transition placements without mother?',
 'Preserve historical unresolved strict-parent questions independently from accepted macro hierarchy?',
 'Keep non-textual composition groups outside both strict and macro mother-daughter hierarchy?',
 'Keep technical navigation separate?',
 'Keep negative constraints first-class?',
 'Allow future overlays append-only?',
 'Validate cycles/invariants per relation-layer semantics?',
 'Should whole-Job textual root be defined separately for strict and macro hierarchy?')
INVARIANTS={
 'I1':'MACRO CHILD_OF does not entail STRICT MOTHER_OF.',
 'I2':'STRICT clause correspondence does not automatically entail MACRO relation.',
 'I3':'CLAUSE_ATOM anchor does not determine relation layer.',
 'I4':'MACRO SAME_LEVEL does not imply strict clause parataxis.',
 'I5':'NO_NEW_BOUNDARY does not imply mother-daughter relation.',
 'I6':'Historical relation label must be interpreted together with relation_layer.'}
WORDING='''MILAL distinguishes strict clause hierarchy from macro textual hierarchy.

Historical macro relations may remain valid even where strict syntactic motherhood is unproven.

Jin’s one-mother principle governs strict hypotactic daughterhood, not every macro containment relation.

Macro parataxis and strict clause parataxis are distinct analytical claims.

Relation type alone is insufficient; every active analytical relation must be interpreted together with its relation layer.

CONTINUES_WITHIN may encode macro continuation or no-new-boundary placement and therefore requires semantic subtype information.
'''


def config():return json.loads((ROOT/'config/r4_4_contract_jin_0_7_job.json').read_bytes())


def scope_ids(q,inv,cfg):
    if q in ('Q-D','Q-E'):
        typ='CONTINUES_WITHIN' if q=='Q-D' else 'SAME_LEVEL_SIBLING'
        return [r['relation_id'] for r in inv if r['relation_type']==typ]
    return next(r['historical_relation_ids'] for r in cfg['decisions'] if r['question_id']==q)


def source_link(files,path,index,record):
    return dict(member=path,data_row=index,member_sha256=io.sha(files[path]),row_sha256=io.sha(io.js(record)),record=record)


def authority(cfg,request):
    io.require(io.sha(request)==cfg['source_request']['sha256'],'exact researcher source')
    io.require([r['question_id'] for r in cfg['decisions']]==['Q-'+c for c in 'ABCDEF'],'six primary decisions')
    for r in cfg['decisions']:
        b=request[r['byte_start']:r['byte_end']]
        io.require(b.decode()==r['verbatim'] and io.sha(b)==r['excerpt_sha256'],'verbatim decision excerpt')
        io.require(r['human_decision']=='ACCEPTED' and r['question_id']+' = ACCEPTED' in r['verbatim'],'explicit researcher acceptance')


def contract():
    return dict(representation='LAYERED_TYPED_GRAPH',approval_scope='CONCEPTUAL_MODEL_AND_FUTURE_TYPING_RULES',
        mandatory_active_analytical_fields=['relation_type','relation_layer'],relation_layer_values=list(LAYERS),
        continuation_semantics=list(CONTINUATION),semantic_subtype_required_for_continuation=True,
        strict_continuation_requires_independent_evidence=True,strict_daughter_one_mother=True,
        macro_mother_requirement='OPEN_R3',whole_book_root_scope='OPEN_R10',
        macro_does_not_entail_strict=True,strict_does_not_entail_macro=True,
        anchor_does_not_determine_layer=True,macro_sibling_does_not_entail_strict_parataxis=True,
        no_boundary_is_not_mother=True,consumer_implemented=False,migration_executed=False,
        invariants=deepcopy(INVARIANTS),source_questions=['Q-'+c for c in 'ABCDEF'])


def primary(inv,cfg):
    byid={r['relation_id']:r for r in inv};out=[]
    descriptions={
      'Q-A':'1:13 is contained within the first testing frame opened at 1:6.',
      'Q-B':'3:1 opens the Job speech-event frame; 3:2 is the formal CSF within/continuing that macro speech event.',
      'Q-C':'40:1 is contained within the first YHWH speech/response complex opened at 38:1; storm formula, repeated challenge and wider distribution support macro containment.',
      'Q-D':'Distinguish independently supported strict continuation, macro continuation and no-new-boundary placement; seven listed cases remain provisional.',
      'Q-E':'The 98 historical SAME_LEVEL_SIBLING rows are macro textual parataxis, without establishing strict clause parataxis.',
      'Q-F':'Active analytical relations require separate mandatory relation_type and relation_layer fields; conceptual vocabulary approved without migration.'}
    for d in cfg['decisions']:
        q=d['question_id'];ids=scope_ids(q,inv,cfg)
        io.require(all(i in byid for i in ids),'exact approved relation identity absent')
        layers=['MACRO_TEXTUAL_HIERARCHY'] if q in ('Q-A','Q-B','Q-C') else ['STRICT_CLAUSE_HIERARCHY','MACRO_TEXTUAL_HIERARCHY'] if q=='Q-D' else ['STRICT_CLAUSE_PARATAXIS','MACRO_TEXTUAL_PARATAXIS'] if q=='Q-E' else list(LAYERS)
        out.append(dict(decision_id='JIN07:'+q,historical_relation_id=ids,
          historical_relation_type=sorted({byid[i]['relation_type'] for i in ids}),human_decision=d['human_decision'],
          approved_relation_layer=layers,approved_semantic_subtype=list(CONTINUATION) if q=='Q-D' else ['SPEECH_FRAME_CONTINUATION'] if q=='Q-B' else [],
          strict_status='UNRESOLVED_UNPROVEN' if q in ('Q-A','Q-B','Q-C') else 'NO_NEW_STRICT_ACCEPTANCE',
          macro_status='ACCEPTED' if q in ('Q-A','Q-B','Q-C','Q-E') else 'TYPING_RULE_ACCEPTED',
          source_judgment=q,rationale=descriptions[q],limitations='No historical rewrite, relation migration or new parent; clause-level candidates remain evidence.',
          supersedes_interpretation_only=True,rewrites_historical_record=False,
          version=cfg['stage'],source_recorded_date=cfg['version_date'],date_precision='DAY_NO_EVENT_TIME_INFERRED',
          decision_origin='EXPLICIT_RESEARCHER_TRANSCRIPTION',derived_from_human_rule=False,
          verbatim_researcher_decision=d['verbatim'],source_request_sha256=cfg['source_request']['sha256']))
    return out


def applications(files,inv,cfg):
    memberships={q:set(scope_ids(q,inv,cfg)) for q in ('Q-A','Q-B','Q-C','Q-D','Q-E')};out=[]
    for i,r in enumerate(inv,1):
        qs=[q for q,ids in memberships.items() if r['relation_id'] in ids]
        if not qs:continue
        typ=r['relation_type'];sub='MACRO_CONTAINMENT';status='ACCEPTED'
        if typ=='SAME_LEVEL_SIBLING':sub='MACRO_TEXTUAL_PARATAXIS'
        elif typ=='HIERARCHICALLY_ABOVE':sub='MACRO_SPEECH_EVENT_FRAME'
        elif typ=='CONTINUES_WITHIN':
            if 'Q-B' in qs:sub='SPEECH_FRAME_CONTINUATION'
            elif r['proposed_semantics']=='NO_NEW_BOUNDARY':sub='NO_NEW_BOUNDARY'
            else:sub='MACRO_TEXTUAL_CONTINUATION';status='PROVISIONAL_CURRENT_AUDIT'
        out.append(dict(application_id='JIN07:APPLY:'+r['relation_id'],decision_id=['JIN07:'+q for q in qs],
          historical_relation_id=r['relation_id'],historical_relation_type=typ,source_ref=r['source_ref'],target_ref=r['target_ref'],
          human_decision='DERIVED_TYPING_APPLICATION',approved_relation_layer='MACRO_TEXTUAL_PARATAXIS' if typ=='SAME_LEVEL_SIBLING' else 'MACRO_TEXTUAL_HIERARCHY',
          approved_semantic_subtype=sub,strict_status='UNRESOLVED_UNPROVEN',macro_status=status,
          source_judgment=qs,rationale='Exact-ID application of the explicit researcher decision; see primary source excerpts.',
          limitations='Typing is an append-only interpretation overlay, not an active graph migration or strict edge.',
          supersedes_interpretation_only=True,rewrites_historical_record=False,derived_from_human_rule=True,
          new_human_decision=False,new_relation=False,new_parent_edge=False,migrated=False,strict_relation_created=False,
          version=cfg['stage'],source_recorded_date=cfg['version_date'],historical_status=r['historical_status'],
          historical_review_status=r['latest_review_status'],historical_source=source_link(files,INVENTORY,i,r)))
    return out


def revised_questions():
    return [dict(question_id='R'+str(i),question=q,approval_scope='FUTURE_CONTRACT_OPERATIONALIZATION',**review_fields()) for i,q in enumerate(QUESTIONS,1)]


def question_crosswalk(files,cfg):
    p=cfg['question_source'];raw=files[p].decode();matches=re.findall(r'^Q([1-9]): (.+)$',raw,re.M)
    io.require([x[0] for x in matches]==list('123456789'),'historical Q1-Q9 exact question source')
    mapping={1:[1,2,3],2:[4],3:[5],4:[6],5:[7],6:[8],7:[9],8:[2,3],9:[10]}
    effects={1:'Q-F and approved core distinction require separate strict/macro scopes; canonical operational adoption remains R1.',
       2:'Q-A/B/C accept macro interpretations independently of unresolved strict motherhood; revise ambiguous parent terminology.',
       8:'Strict daughterhood and macro containment are distinct; scope must no longer be inferred from anchoring.'}
    return [dict(historical_question_id='Q'+n,historical_question=q.rstrip('\r'),historical_status='UNAPPROVED',
      source_member=p,source_sha256=io.sha(files[p]),effect_of_QA_QF=effects.get(int(n),'Layer-specific contract wording required; this historical question was not approved.'),
      still_open=True,revised_question_ids=['R'+str(k) for k in mapping[int(n)]],
      recommended_revised_wording=[QUESTIONS[k-1] for k in mapping[int(n)]],new_approval=False) for n,q in matches]


def build(files,cfg,request):
    authority(cfg,request)
    io.require(INVENTORY in files and '90_run_metadata.json' in files and io.manifest_ok(files),'JIN.0.6 files/manifest')
    inv=io.rows(files[INVENTORY]);io.require(len({r['relation_id'] for r in inv})==len(inv),'unique historical identities')
    counts=Counter(r['relation_type'] for r in inv)
    io.require(len(inv)==cfg['expected_registry_count'] and all(counts[k]==v for k,v in cfg['expected_counts'].items()),'baseline counts')
    io.require(all(r['proposal_status']=='UNREVIEWED' for r in inv),'JIN.0.6 audit proposals preserved')
    # The source metadata is checked, rather than silently substituting a new mother state.
    meta=json.loads(files['90_run_metadata.json'])
    io.require(meta['mother_search_results']=={'2:11':'NO_MACRO_MOTHER_FOUND','32:1':'NO_MACRO_MOTHER_FOUND'},'unresolved mother source state')
    io.require(meta['q1_q9']=={f'Q{i}':'UNAPPROVED' for i in range(1,10)} and meta['participant_arc']=='UNADJUDICATED','source open questions/participant')
    return dict(primary=primary(inv,cfg),applications=applications(files,inv,cfg),contract=contract(),
        questions=revised_questions(),question_crosswalk=question_crosswalk(files,cfg),
        strict_controls=io.rows(files['09_strict_clause_positive_controls.csv']),
        mother_status=deepcopy(meta['mother_search_results']),participant_arc=meta['participant_arc'],
        new_relations=[],new_parents=[],migrations=[],history=deepcopy(files))


def gates(m,expected):
    checks={};ds={r['source_judgment']:r for r in m['primary']};ed={r['source_judgment']:r for r in expected['primary']}
    checks['SIX_PRIMARY_HUMAN_DECISIONS']=len(m['primary'])==6 and ds.keys()==ed.keys() and all(not r['derived_from_human_rule'] for r in m['primary'])
    for q,name in [('Q-A','QA_MACRO_1_13_ACCEPTED'),('Q-B','QB_MACRO_SPEECH_FRAME_ACCEPTED'),('Q-C','QC_MACRO_40_1_ACCEPTED'),('Q-D','QD_CONTINUES_WITHIN_SPLIT_ACCEPTED'),('Q-E','QE_SAME_LEVEL_LAYER_SPLIT_ACCEPTED'),('Q-F','QF_TYPE_LAYER_SEPARATION_ACCEPTED')]:
        checks[name]=ds.get(q)==ed[q] and ds[q]['human_decision']=='ACCEPTED'
    aa=m['applications'];ea=expected['applications']
    for q,name in [('Q-A','QA_STRICT_1_13_UNRESOLVED'),('Q-B','QB_STRICT_3_1_2_UNRESOLVED'),('Q-C','QC_STRICT_40_1_UNPROVEN')]:
        r=[r for r in aa if q in r['source_judgment']];checks[name]=bool(r) and r==[r for r in ea if q in r['source_judgment']] and all(x['strict_status']=='UNRESOLVED_UNPROVEN' for x in r)
    checks['DERIVED_APPLICATIONS_COMPLETE']=aa==ea and all(r['derived_from_human_rule'] and not r['new_human_decision'] for r in aa)
    checks['CONTINUATION_APPLICATIONS_COMPLETE']=[r for r in aa if r['historical_relation_type']=='CONTINUES_WITHIN']==[r for r in ea if r['historical_relation_type']=='CONTINUES_WITHIN']
    checks['SAME_LEVEL_ROWS_UNCHANGED']=[r for r in aa if r['historical_relation_type']=='SAME_LEVEL_SIBLING']==[r for r in ea if r['historical_relation_type']=='SAME_LEVEL_SIBLING']
    checks['HISTORICAL_RELATIONS_UNCHANGED']=m['history']==expected['history'] and all(not r['rewrites_historical_record'] and r['historical_source'] in [e['historical_source'] for e in ea] for r in aa)
    checks['NO_RELATION_MIGRATION']=not m['migrations'] and not m['contract']['migration_executed'] and all(not r['migrated'] for r in aa)
    checks['NO_NEW_PARENT']=not m['new_parents'] and all(not r['new_parent_edge'] for r in aa)
    checks['NO_NEW_RELATION']=not m['new_relations'] and all(not r['new_relation'] for r in aa)
    for gate,key in [('MACRO_NOT_EQUAL_STRICT','macro_does_not_entail_strict'),('CLAUSE_ATOM_NOT_EQUAL_STRICT','anchor_does_not_determine_layer'),('MACRO_PARATAXIS_NOT_STRICT','macro_sibling_does_not_entail_strict_parataxis'),('STRICT_NOT_AUTOMATIC_MACRO','strict_does_not_entail_macro')]:
        checks[gate]=m['contract'][key] is True and all(not r['strict_relation_created'] for r in aa)
    nb=[r for r in aa if r['approved_semantic_subtype']=='NO_NEW_BOUNDARY']
    checks['NO_BOUNDARY_NOT_EQUAL_MOTHER']=m['contract']['no_boundary_is_not_mother'] and nb==[r for r in ea if r['approved_semantic_subtype']=='NO_NEW_BOUNDARY'] and all(not r['new_parent_edge'] for r in nb)
    for ref,tag in [('28:1','JOB_28_1'),('42:16','JOB_42_16')]:checks[tag+'_NO_NEW_BOUNDARY']=any(r['source_ref']==ref and r['approved_semantic_subtype']=='NO_NEW_BOUNDARY' for r in nb)
    checks['PROVISIONAL_CONTINUATIONS_NOT_PROMOTED']=[r for r in aa if r['macro_status']=='PROVISIONAL_CURRENT_AUDIT']==[r for r in ea if r['macro_status']=='PROVISIONAL_CURRENT_AUDIT']
    checks['TYPE_LAYER_VOCABULARY_FROZEN']=m['contract']==contract()
    for ref,tag in [('2:11','JOB_2_11'),('32:1','JOB_32_1')]:checks[tag+'_UNRESOLVED']=m['mother_status'].get(ref)=='NO_MACRO_MOTHER_FOUND' and not m['new_parents']
    checks['HISTORICAL_Q1_Q9_NOT_AUTO_APPROVED']=m['question_crosswalk']==expected['question_crosswalk']
    checks['REVISED_R1_R10_UNREVIEWED']=m['questions']==revised_questions()
    checks['STRICT_CONTROLS_NOT_PROMOTED']=m['strict_controls']==expected['strict_controls'] and bool(m['strict_controls']) and all(not r['human_accepted'] and not r['macro_evidence'] for r in m['strict_controls'])
    checks['NO_R4_4_CONSUMER']=not m['contract']['consumer_implemented']
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED'
    return checks


def render(m,cfg,request):
    f={HISTORY+k:v for k,v in m['history'].items()}
    f['01_relation_layer_human_decisions.csv']=io.csv_bytes(m['primary'])
    provenance=[dict(decision_id='JIN07:'+d['question_id'],source_request=cfg['source_request']['path'],source_sha256=io.sha(request),byte_start=d['byte_start'],byte_end=d['byte_end'],excerpt_sha256=d['excerpt_sha256'],version=cfg['stage'],source_recorded_date=cfg['version_date']) for d in cfg['decisions']]
    f['02_relation_layer_human_provenance.csv']=io.csv_bytes(provenance)
    f['03_relation_layer_historical_crosswalk.csv']=io.csv_bytes(m['applications'])
    for name,typ in [('04_continues_within_typing_decisions.csv','CONTINUES_WITHIN'),('05_same_level_typing_decisions.csv','SAME_LEVEL_SIBLING')]:f[name]=io.csv_bytes([r for r in m['applications'] if r['historical_relation_type']==typ])
    f['06_hierarchy_layer_contract_decision.md']=('# Approved conceptual contract — no migration\n\n'+WORDING+'\n```json\n'+io.js(m['contract']).decode()+'```\n\nSix primary decisions, '+str(len(m['applications']))+' derived interpretation applications. The latter are not new edges or new primary judgments.\n\nR1 reopens operational adoption, not the existence of the approved conceptual distinction. R2–R10 remain user-requested unanswered contract questions.\n').encode()
    f['07_relation_layer_invariants.md']=('# Approved invariants\n\n'+'\n\n'.join(k+'. '+v for k,v in m['contract']['invariants'].items())+'\n').encode()
    f['08_historical_contract_question_crosswalk.csv']=io.csv_bytes(m['question_crosswalk'])
    packet='# Revised R4.4 contract review — R1–R10 UNREVIEWED\n\nReadiness: READY_FOR_REVISED_R4_4_CONTRACT_REVIEW\n\n'+WORDING+'\n'
    for d in m['primary']:packet+=f"- {d['source_judgment']}: {d['human_decision']} — {d['rationale']}\n"
    packet+='\nPrimary researcher decisions: 6. Derived interpretation applications: '+str(len(m['applications']))+'. No registry migration.\n\n'
    packet+='2:11 / 32:1: NO_MACRO_MOTHER_FOUND. Q1–Q9 remain unapproved. Participant arc UNADJUDICATED; consumer absent. Seven continuation examples remain provisional; the typing rule is approved.\n\n'
    for r in m['questions']:packet+='## '+r['question_id']+'\n\n'+r['question']+'\n\nReview status: UNREVIEWED\nResearcher answer:\n\n'
    f['09_revised_contract_review_packet.md']=packet.encode()
    f['10_remaining_strict_macro_questions.csv']=io.csv_bytes(m['questions'])
    f['12_approved_conceptual_contract.json']=io.js(m['contract']);f['13_exact_researcher_source.txt']=request
    f['14_strict_controls_preserved.csv']=io.csv_bytes(m['strict_controls'])
    return f


def preflight(cfg,request,pins,baseline,archive_sha,consumer_files,synthetic=False):
    return dict(BASELINE_COMMIT_VERIFIED=baseline==cfg['baseline'],JIN_0_6_FROZEN_VERIFIED=pins==cfg['frozen_files'] and (synthetic or archive_sha==cfg['archive']['sha256']),EXACT_RESEARCHER_SOURCE=io.sha(request)==cfg['source_request']['sha256'],NO_CONSUMER_FILES=not consumer_files)


def execute(out,self_test=False):
    cfg=config();request=(ROOT/cfg['source_request']['path']).read_bytes()
    if self_test:
        from milal_jin_layer_freeze_fixture import fixture
        files,cfg=fixture(cfg);archive_sha=io.sha(io.js({k:io.sha(v) for k,v in files.items()}))
    else:
        data=(ROOT/cfg['archive']['path']).read_bytes();archive_sha=io.sha(data)
        io.require(archive_sha==cfg['archive']['sha256'],'pinned JIN.0.6 archive');files=io.archive(data)
    pins={p:io.sha((ROOT/p).read_bytes()) for p in cfg['frozen_files']}
    baseline=subprocess.check_output(['git','rev-parse',cfg['baseline']],cwd=ROOT,text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',baseline,'HEAD'],cwd=ROOT,check=True)
    checks=preflight(cfg,request,pins,baseline,archive_sha,list((ROOT/'src').glob('*r4_4*.py'))+list((ROOT/'scripts').glob('*r4_4*')),self_test)
    m=build(files,cfg,request);checks.update(gates(m,build(files,cfg,request)))
    io.require(all(checks.values()),'failed gates '+str([k for k,v in checks.items() if not v]))
    result=render(m,cfg,request)
    result['90_run_metadata.json']=io.js(dict(stage=cfg['stage'],mode='SYNTHETIC' if self_test else 'REAL_FROZEN_JIN_0_6',status='PASS',
        readiness='READY_FOR_REVISED_R4_4_CONTRACT_REVIEW',baseline=baseline,archive_sha256=archive_sha,pins=pins,
        primary_human_decision_count=len(m['primary']),derived_typing_application_count=len(m['applications']),
        new_relation_count=len(m['new_relations']),new_parent_edge_count=len(m['new_parents']),new_relation_migration_count=len(m['migrations']),
        mother_status=m['mother_status'],participant_arc=m['participant_arc'],historical_questions_approved=False,
        code_sha256=io.sha(Path(__file__).read_bytes()),external_release_gates=['DETERMINISTIC_RERUN','REGRESSION_PASS']))
    io.seal(result);checks['MANIFEST_VALID']=io.manifest_ok(result)
    result['11_gates.csv']=io.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]);io.seal(result)
    zp=io.publish(result,Path(out));print(json.dumps(dict(zip=str(zp),sha256=io.sha(zp.read_bytes()),gates=len(checks),primary_decisions=len(m['primary']),derived_applications=len(m['applications']))));return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True);p.add_argument('--self-test',action='store_true');a=p.parse_args();execute(a.out,a.self_test)
