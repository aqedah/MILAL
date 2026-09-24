"""Contract proposal and compatibility test harness; NOT an R4.4 consumer."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import milal_hsa3_layer_0_2 as n

CONFIG = ROOT/'config/r4_4_contract_0_1_job.json'
HISTORY = 'history/hsa3_layer_0_2/'
sha, rows, util = n.sha, n.rows, n.util
MAPPING_STATUSES = ('LOSSLESS','LOSSLESS_WITH_EXTENSION','AMBIGUOUS_SCHEMA','INCOMPATIBLE','NOT_APPLICABLE')
SCHEMA_CLASSES = ('STILL_VALID_UNCHANGED','REUSABLE_WITH_EXTENSION','AMBIGUOUS_AFTER_HSA3','INCOMPATIBLE_WITH_LAYERED_MODEL','DEPRECATED_FOR_R4_4')
DOCUMENTS = {
 '07_r4_4_precedence_rules.md':'docs/R4_4_CONTRACT_0_1_PRECEDENCE.md',
 '08_r4_4_graph_invariants.md':'docs/R4_4_CONTRACT_0_1_INVARIANTS.md',
 '12_r4_4_input_contract_spec.md':'docs/R4_4_CONTRACT_0_1_SPEC.md',
 '16_repository_architecture_audit.md':'docs/R4_4_CONTRACT_0_1_ARCHITECTURE.md'}


def require(ok,message):
    if not ok: raise ValueError('R4.4-CONTRACT.0.1 STOP: '+message)


def load(self_test=False,archive=None):
    require(not (self_test and archive),'self-test cannot consume a real archive')
    cfg=json.loads(CONFIG.read_bytes());commit=n.l.d.baseline_receipt(cfg)
    pins=n.l.d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['actual']==r['expected'] for r in pins),'frozen source changed')
    request=(ROOT/cfg['source_request']['path']).read_bytes();proposal_bytes=(ROOT/cfg['proposal']['path']).read_bytes()
    require(sha(request)==cfg['source_request']['sha256'] and sha(proposal_bytes)==cfg['proposal']['sha256'],'authority/proposal hash')
    if self_test:
        old=n.load(True);files=n.serialize(n.build(old),old);digest=sha(files['99_manifest_sha256.csv'])
    else:
        data=(Path(archive) if archive else ROOT/cfg['archive']['path']).read_bytes();digest=sha(data)
        require(digest==cfg['archive']['sha256'],'upstream ZIP SHA256')
        files=n.l.d.h.f.a.prep.r43.h1.src.archive(data,digest,mr1=True)['files']
        require(len(files)==cfg['archive']['members'],'upstream member count')
    require(util.manifest_ok(files) and all(r['valid'] for r in n.l.d.h.nested_manifests(files)),'upstream manifests')
    meta=json.loads(files['90_run_metadata.json']);gg=rows(files['08_gates.csv'])
    require(meta['version']=='HSA3-LAYER.0.2' and meta['status']=='PASS' and not meta['r44_started'],'upstream stage')
    require(meta['mode']==('SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_NECESSITY_HUMAN_FREEZE'),'upstream mode')
    require(len(gg)==meta['gate_count'] and all(r['status']=='PASS' for r in gg),'upstream gates')
    for name,fields in cfg['r43_fields'].items():
        if name.endswith('.csv'):
            import csv,io
            actual=next(csv.reader(io.StringIO(files[cfg['r43_prefix']+name].decode('utf-8-sig'))))
            require(actual==fields,'R4.3 schema mismatch: '+name)
    return dict(cfg=cfg,commit=commit,pins=pins,request=request,proposal_bytes=proposal_bytes,
        proposal=json.loads(proposal_bytes),files=files,
        receipt=dict(sha256=digest,members=len(files),synthetic=self_test),
        documents={out:(ROOT/path).read_bytes() for out,path in DOCUMENTS.items()},
        mode='SYNTHETIC_CONTRACT_TEST_ONLY' if self_test else 'FROZEN_REAL_CONTRACT_DRY_RUN')


def source_records(s):
    result=[]
    for spec in s['cfg']['inputs']:
        member=spec['member'];data=s['files'][member]
        typed=[{'text':data.decode('utf-8')}] if spec['identity_field']=='DOCUMENT' else rows(data)
        raw=[{'text':data.decode('utf-8')}] if spec['identity_field']=='DOCUMENT' else n.l.d.h.raw_rows(data)
        seen=set()
        for i,(r,rr) in enumerate(zip(typed,raw),1):
            require(spec['identity_field']=='DOCUMENT' or spec['identity_field'] in r,'missing required source identity column: '+member)
            ident=member if spec['identity_field']=='DOCUMENT' else r[spec['identity_field']]
            require(ident and ident not in seen,'duplicate/empty exact source identity: '+member);seen.add(ident)
            receipt=dict(member=HISTORY+member,data_row=i,identity_field=spec['identity_field'],identity=ident,
                row_sha256=n.l.d.h.f.rowhash(rr),member_sha256=sha(data),artifact_sha256=s['receipt']['sha256'])
            result.append(dict(mapping_id='MAP:'+sha((member+'::'+str(ident)).encode())[:24],
                source_member=member,source_identity=ident,record_kind=spec['record_kind'],authority_role=spec['authority_role'],
                source_record=deepcopy(r),source_receipt=receipt))
    return result


def named_fields(value,names,path=''):
    """Retain all named source fields and paths; never flatten their scopes."""
    result={}
    if isinstance(value,dict):
        for key,item in value.items():
            p=path+'/'+key
            if key in names:result[p]=deepcopy(item)
            result.update(named_fields(item,names,p))
    elif isinstance(value,list):
        for i,item in enumerate(value):result.update(named_fields(item,names,path+'/'+str(i)))
    return result


def project(record,s,necessities):
    r=record['source_record'];kind=record['record_kind'];receipt=record['source_receipt']
    base=dict(original_record=deepcopy(r),provenance_ids=[deepcopy(receipt)],contract_status='CONTRACT_PROPOSAL')
    status='LOSSLESS';extension='';target='CONTRACT_STATE'
    if kind=='NODE':
        require(r['node_kind'] in s['proposal']['node_kinds'],'unmapped node kind')
        old=r['original_record'];human=necessities.get(r['node_id'])
        optional=dict(reference_start=old.get('reference_start',old.get('span_start')),
            reference_end=old.get('reference_end',old.get('span_end')),speaker=old.get('human_speaker'),
            participant_role=old.get('participant_role'),historical_parent_status=old.get('parentage_status'),
            direct_parent_ids=old.get('direct_parent_ids'),
            parentage_necessity_status=human['researcher_necessity_status'] if human else None,
            additional_parentage_review_required=human['additional_parentage_review_required'] if human else None,
            direct_parent_edge_resolved=human['direct_parent_edge_resolved'] if human else None)
        spans=deepcopy(r['accepted_annotations'])
        scope_fields={k:old[k] for k in ('reference_start','reference_end','span_start','span_end') if old.get(k)}
        if r['node_kind']=='COMPOSITION_GROUP' and scope_fields:
            spans.append(dict(source_kind='EXPLICIT_GROUP_SCOPE_FIELDS',source_fields=scope_fields,provenance_ids=[deepcopy(receipt)]))
        span_type=('SUPPLIED_GROUP_SCOPE' if scope_fields or spans else 'NO_SPAN_RECORDED') if r['node_kind']=='COMPOSITION_GROUP' else 'SOURCE_EVIDENCE_LOCUS' if r['node_kind']=='SOURCE_EVIDENCE_ANCHOR' else 'HISTORICAL_LOCUS'
        if r['node_kind']=='TECHNICAL_ROOT':span_type='NO_SPAN_RECORDED'
        base.update(node_id=r['node_id'],canonical_node_id=r['canonical_textual_node'] or r['node_id'],
            node_kind=r['node_kind'],textuality=s['proposal']['node_kinds'][r['node_kind']],anchor_ref=r['reference'],
            span_type=span_type,
            structural_function=r['structural_function'],source_stage=r['source_stage'],
            human_status=dict(source_authority=r['source_authority'],necessity_decision_id=human['decision_id'] if human else None),
            frozen_status=r['frozen_status'],technical_only=r['node_kind']=='TECHNICAL_ROOT',
            qualified_spans=spans,**optional,
            field_presence={k:'NOT_RECORDED' if v is None else 'SOURCE_RECORDED' for k,v in optional.items()})
        if human:
            base['necessity_source']=dict(decision_id=human['decision_id'],source_artifact_sha256=s['receipt']['sha256'],
                member=HISTORY+'01_parentage_necessity_human_decisions.csv',original_record=deepcopy(human))
        status='LOSSLESS_WITH_EXTENSION';extension='Typed textuality, qualified spans and separate historical/necessity axes.';target='CONTRACT_NODE'
    elif kind=='RELATION':
        # Use the authoritative file's layer and check the explicit stored layer.
        require(r['layer']==record['authority_role'],'relation layer/source member contradiction')
        if r['source_node'] and r['target_node']:form='NODE_IDS'
        elif r['source_ref'] and r['target_ref'] and not r['source_node'] and not r['target_node']:form='REFERENCE_PAIR'
        elif r['scope_ref'] and not any(r[k] for k in ('source_node','target_node','source_ref','target_ref')):form='REFERENCE_SCOPE'
        else:form='UNSUPPORTED';status='AMBIGUOUS_SCHEMA';extension='Unknown endpoint shape; explicit contract review required.'
        layer=r['layer'];old=r['original_record']
        base.update(relation_id=r['relation_id'],source_id=r['source_node'],target_id=r['target_node'],
            source_ref=r['source_ref'],target_ref=r['target_ref'],scope_ref=r['scope_ref'],endpoint_form=form,
            relation_layer=layer,relation_type=r['relation_type'],
            polarity='NEGATIVE' if layer=='NEGATIVE_CONSTRAINT' else 'TECHNICAL' if layer=='TECHNICAL_NAVIGATION' else 'POSITIVE',
            directionality=old.get('direction','STORED_SOURCE_TO_TARGET; NO_INVERSE_GENERATED'),
            status=r['source_status'],human_supplied=r['human_or_automatic']=='HUMAN_ACCEPTED_SOURCE',automatic_resolution=False,
            source_stage=r['source_stage'],original_dimension=r['original_dimension'],membership_position=r['membership_position'],
            graph_scope='TECHNICAL_NAVIGATION' if layer=='TECHNICAL_NAVIGATION' else 'ANALYTICAL_GRAPH',
            evidence_ids=named_fields(r,{'source_evidence_ids','evidence_ids','evidence_anchor_ids'}),
            limitations=named_fields(r,{'limitation','limitations','scope_note'}),
            historical_status=named_fields(r,{'original_status','candidate_status_before','historical_status'}))
        if form in ('REFERENCE_PAIR','REFERENCE_SCOPE'):
            status='LOSSLESS_WITH_EXTENSION';extension='Native reference/scope endpoint union; no fabricated node identity.'
        target='CONTRACT_RELATION'
    else:
        # State/group/crosswalk records remain separate envelopes, not graph edges.
        base.update(state_kind=kind,source_identity=record['source_identity'],state=deepcopy(r))
        if kind in ('QUESTION','NECESSITY','NECESSITY_FINAL','NECESSITY_CROSSWALK','FUTURE_SCOPE'):
            status='LOSSLESS_WITH_EXTENSION';extension='Independent historical, decision, necessity or future-scope state envelope.'
        if kind=='PRESENTATION_CONTEXT':status='NOT_APPLICABLE';extension='Reporting view preserved; not an additional analytical object.'
        if kind=='GROUP_VIEW':target='CONTRACT_NODE_GROUP_VIEW'
    return dict(**record,contract_target=target,contract_record=base,mapping_status=status,extension=extension,
                proposal_status='CONTRACT_PROPOSAL')


def mapping(s):
    records=source_records(s)
    necessity={r['source_record']['node_id']:r['source_record'] for r in records if r['record_kind']=='NECESSITY'}
    return [project(r,s,necessity) for r in records]


def values(obj,path):
    if not path:return [obj]
    if isinstance(obj,list):return [x for r in obj for x in values(r,path)]
    if not isinstance(obj,dict) or path[0] not in obj:return []
    return values(obj[path[0]],path[1:])


def fixture_catalog(mapped,s):
    result=[]
    for f in s['proposal']['fixtures']:
        assertions=[]
        for a in f['assertions']:
            hits=[r['mapping_id'] for r in mapped if r['record_kind']==a['record_kind'] and
                  all(any(x==v for x in values(r['contract_record'],k.split('.'))) for k,v in a['where'].items())]
            assertions.append(dict(requirement=a,mapping_ids=hits,status='PASS' if hits else 'FAIL'))
        result.append(dict(fixture_id=f['fixture_id'],status='PASS' if all(r['status']=='PASS' for r in assertions) else 'FAIL',
            assertions=assertions,proposal_status='CONTRACT_PROPOSAL',research_judgment_created=False))
    return result


def schema_audit(s):
    out=[];code='src/milal_r4_3_hierarchy_scaffold.py'
    for name,fields in s['cfg']['r43_fields'].items():
        for field in fields:
            cls='STILL_VALID_UNCHANGED';note='Preserve exact source field, type, identity and scope; never rewrite history.';line=387
            if field in ('parentage_status','later_human_review_required'):
                cls='AMBIGUOUS_AFTER_HSA3' if field=='parentage_status' else 'DEPRECATED_FOR_R4_4'
                note='Historical parent state is valid; use separate latest necessity decision for active review. The historical blanket review flag is not the current review queue.';line=203
            elif field=='direct_parent_ids':
                cls='REUSABLE_WITH_EXTENSION';note='Preserve explicit parent list, including empty. R4.3 checks at most one, not exactly one; broader cardinality is not approved by this audit.';line=176
            elif field in ('node_type','textual_boundary','reference_start','reference_end','coverage_start','coverage_end'):
                cls='REUSABLE_WITH_EXTENSION';note='Add explicit kind/textuality and qualified source spans. Locus/boundary flag is not full unit coverage or role identity.';line=106
            elif name=='06_overlay_relations.csv':
                cls='DEPRECATED_FOR_R4_4';note='Mixed non-hierarchy/non-membership/non-technical historical projection, not authoritative OVERLAY_RESPONSIO. Retain field via original edge and consume explicit HSA3 layer.';line=387
            elif field in ('edge_class','dimension','relation_type'):
                cls='REUSABLE_WITH_EXTENSION';note='Retain type and dimension; add explicit source layer. DESCRIPTIVE/HORIZONTAL and the filename hierarchy cannot stand for every analytical relation.';line=16
            elif field=='DOCUMENT':
                cls='DEPRECATED_FOR_R4_4';note='Historical human-readable partial scaffold remains evidence; not a machine contract or active all-rows-require-review instruction.';line=265
            elif name=='08_negative_controls.csv':
                cls='STILL_VALID_UNCHANGED';note='Computed QA outcome, not a human-adjudicated negative relation. Preserve as validation evidence only.';line=245
            elif name=='11_accepted_frame_context.csv':
                cls='REUSABLE_WITH_EXTENSION';note='Accepted audit context containing HUMAN_SUPPLIED_PAIR_NOT_DETECTED_MACRO_UNIT; never a discovered hierarchy or adjudicated participant arc.';line=41
            elif field in ('source_locator','source_record','historical_record'):
                cls='REUSABLE_WITH_EXTENSION';note='Keep exact nested record and locator, adding outer artifact/member receipts and later scoped addendum chain.';line=218
            out.append(dict(artifact=name,field=field,classification=cls,rationale=note,source_code=code,source_line=line,
                source_member=HISTORY+s['cfg']['r43_prefix']+name,source_sha256=sha(s['files'][s['cfg']['r43_prefix']+name]),
                proposal_status='CONTRACT_PROPOSAL'))
    return out


def hierarchy_acyclic(mapped):
    parents={}
    for item in mapped:
        r=item['contract_record']
        if item['record_kind']!='RELATION' or r['relation_layer']!='TEXTUAL_HIERARCHY':continue
        if r['relation_type']=='CHILD_OF':child,parent=r['source_id'],r['target_id']
        elif r['relation_type']=='HIERARCHICALLY_ABOVE':child,parent=r['target_id'],r['source_id']
        else:continue
        parents.setdefault(child,set()).add(parent)
    def visit(node,path):return node not in path and all(visit(p,path|{node}) for p in parents.get(node,()))
    return all(visit(x,set()) for x in parents)


def mapping_issues(mapped):
    return [dict(mapping_id=r['mapping_id'],source_member=r['source_member'],source_identity=r['source_identity'],
        mapping_status=r['mapping_status'],issue=r['extension']) for r in mapped if r['mapping_status'] in ('AMBIGUOUS_SCHEMA','INCOMPATIBLE')]


def counts(m):
    return dict(total_records=len(m['mapping']),mapping_statuses={x:sum(r['mapping_status']==x for r in m['mapping']) for x in MAPPING_STATUSES},
        record_kinds=dict(Counter(r['record_kind'] for r in m['mapping'])),schema_classifications=dict(Counter(r['classification'] for r in m['schema_audit'])),
        new_human_judgment_count=len(m['new_human_judgments']),new_structural_relation_count=len(m['new_structural_relations']),
        new_composition_relation_count=len(m['new_composition_relations']),new_overlay_relation_count=len(m['new_overlay_relations']),
        r44_analytical_implementation_count=len(m['consumer_implementations']))


def reports(m,s):
    readiness='BLOCKED_BY_SCHEMA_ISSUES' if mapping_issues(m['mapping']) else 'READY_FOR_HUMAN_CONTRACT_REVIEW'
    packet=['# R4.4 input contract — researcher review only','','CONTRACT_PROPOSAL. No question below has been decided by Codex.','',
            'Readiness: '+readiness,'','## Computed compatibility audit','', '```json',json.dumps(counts(m),ensure_ascii=False,indent=2),'```','',
            '## Questions requiring researcher approval','']
    for i,q in enumerate(s['proposal']['review_questions'],1):packet += ['Q'+str(i)+'. '+q,'','Researcher answer: ','Review status: UNREVIEWED','']
    packet += ['## Explicit extensions proposed','',
        'Keep existing TEXTUAL_NODE/TRANSITION_ANCHOR/SOURCE_EVIDENCE_ANCHOR kinds; do not recast every textual locus as a full unit.',
        'Retain COMPOSITION_GROUPING naming. Add native REFERENCE_PAIR and REFERENCE_SCOPE endpoints for ANA without fabricating node IDs.',
        'Separate historical parent, later necessity, frozen, candidate and human-deferred statuses. Keep source absence explicit, not one overloaded NULL.',
        'Preserve each raw record and source chain; presentation matrices and future scope notes are not new graph edges.',
        'R4.3 at-most-one-parent restriction is observed, not automatically generalized or newly approved. Any future multi-parent extension requires explicit contract review.',
        'Participant arc remains NEXT_RESEARCH_SCOPE / UNADJUDICATED. R4.4 analytical consumer and final output remain NOT STARTED.']
    result=deepcopy(s['documents']);result['13_r4_4_contract_review_packet.md']='\n'.join(packet).encode()
    # Required readiness artifact contains exactly one permitted token.
    result['14_r4_4_implementation_readiness.md']=(readiness+'\n').encode()
    return result


def derive(s):
    mm=mapping(s)
    m=dict(mapping=mm,schema_audit=schema_audit(s),fixtures=fixture_catalog(mm,s),issues=mapping_issues(mm),
        proposal=deepcopy(s['proposal']),historical=deepcopy(s['files']),commit=deepcopy(s['commit']),receipt=deepcopy(s['receipt']),
        new_human_judgments=[],new_structural_relations=[],new_composition_relations=[],new_overlay_relations=[],consumer_implementations=[])
    m['reports']=reports(m,s);return m


def digest(m):
    return n.l.d.h.f.rowhash({k:({a:sha(b) for a,b in v.items()} if k in ('historical','reports') else v) for k,v in m.items() if k!='rerun_digest'})


def build(s):
    m=derive(s);m['rerun_digest']=digest(derive(s));return m


def gates(m,s):
    expected=mapping(s);mapped=m['mapping'];check={};proposal=m['proposal']
    select=lambda kind:[r['contract_record'] for r in mapped if r['record_kind']==kind]
    nn=select('NODE');rr=select('RELATION');human=select('NECESSITY');questions=select('QUESTION')
    unchanged=lambda name:m['historical'].get(name)==s['files'][name]
    source_match=lambda kind:[r for r in mapped if r['record_kind']==kind]==[r for r in expected if r['record_kind']==kind]
    check['BASELINE_EXACT']=m['commit']==s['commit'] and m['commit']['verified_commit']==s['cfg']['baseline_commit'] and m['commit']['is_ancestor'] is True
    check['INPUT_VERIFIED']=m['receipt']==s['receipt'] and unchanged('90_run_metadata.json') and unchanged('08_gates.csv')
    check['SEAMS_FROZEN']=source_match('SEAM_STATUS') and len(select('SEAM_STATUS'))==s['cfg']['regression']['seams'] and all(r['state']['status']=='FROZEN' for r in select('SEAM_STATUS'))
    check['NECESSITY_57_FROZEN']=len(human)==s['cfg']['regression']['necessity_decisions'] and all(r['state']['human_status']=='FROZEN' for r in human) and source_match('NECESSITY')
    check['ACTIVE_QUESTIONS_ZERO']=bool(human) and all(r['state']['additional_parentage_review_required'] is False for r in human)
    check['HISTORICAL_PARENT_57']=sum(r['state']['question_kind']=='HISTORICAL_DIRECT_PARENT' and r['state']['status']=='UNRESOLVED' for r in questions)==s['cfg']['regression']['historical_parents'] and source_match('QUESTION')
    check['NO_PARENT_SYNTHESIS']=source_match('NODE') and source_match('RELATION') and all(r['state']['direct_parent_edge_resolved'] is False and r['state']['assigned_parent_ids']==[] for r in human)
    check['NO_NEW_HUMAN_JUDGMENT']=m['new_human_judgments']==[]
    check['NO_NEW_ANALYTICAL_RELATION']=m['new_structural_relations']==m['new_composition_relations']==m['new_overlay_relations']==[]
    check['PARTICIPANT_ARC_UNADJUDICATED']=source_match('FUTURE_SCOPE') and m['new_overlay_relations']==[] and proposal['future_overlay_extension']['actual_relations_created']==[]
    check['NO_R4_4_CONSUMER']=m['consumer_implementations']==[] and m['reports']['14_r4_4_implementation_readiness.md'] in (b'READY_FOR_HUMAN_CONTRACT_REVIEW\n',b'BLOCKED_BY_SCHEMA_ISSUES\n')
    check['NODE_TYPES_DISTINCT']=proposal['node_kinds']==s['proposal']['node_kinds'] and all(r['textuality']==proposal['node_kinds'].get(r['node_kind']) for r in nn)
    check['RELATION_LAYER_EXPLICIT']=all(r['relation_layer'] in proposal['relation_layers'] for r in rr) and 'relation_layer' in {r['field'] for r in proposal['fields']['relation']}
    for layer in s['proposal']['relation_layers']:
        check['LAYER_'+layer]=[r for r in mapped if r['record_kind']=='RELATION' and r['contract_record']['relation_layer']==layer]==[r for r in expected if r['record_kind']=='RELATION' and r['contract_record']['relation_layer']==layer]
    computed=fixture_catalog(mapped,s)
    for f in computed:check['FIXTURE_'+f['fixture_id']]=f['status']=='PASS' and f==next((x for x in m['fixtures'] if x['fixture_id']==f['fixture_id']),None)
    ids={r['state']['node_id'] for r in human}
    check['UNRESOLVED_AND_NOT_REQUIRED_COEXIST']=len(ids)==s['cfg']['regression']['historical_parents'] and all(r['historical_parent_status']=='UNRESOLVED' and r['parentage_necessity_status'] in ('DIRECT_PARENT_NOT_REQUIRED','CURRENT_LAYERED_RELATIONS_SUFFICIENT','DIRECT_TEXTUAL_PARENT_NOT_REQUIRED') and r['direct_parent_edge_resolved'] is False and r['direct_parent_ids']==[] and r['additional_parentage_review_required'] is False for r in nn if r['node_id'] in ids) and ids<={r['node_id'] for r in nn}
    peer={(r['source_id'],r['target_id']) for r in rr if r['relation_layer']=='TEXTUAL_SAME_LEVEL' and r['relation_type']=='SAME_LEVEL_SIBLING'}
    check['LAYER_SPECIFIC_CYCLE_POLICY']=hierarchy_acyclic(mapped) and bool(peer) and all((b,a) in peer for a,b in peer) and proposal['cycle_policy']==s['proposal']['cycle_policy']
    check['ROLE_ALIAS_NOT_DUPLICATE_UNIT']=source_match('ROLE_CROSSWALK') and all(r['node_kind']=='ROLE_ALIAS' and r['canonical_node_id']!=r['node_id'] for r in nn if r['original_record']['node_kind']=='ROLE_ALIAS')
    forbidden={r['node_id'] for r in nn if r['node_kind'] in ('COMPOSITION_GROUP','TECHNICAL_ROOT')}
    parents=[r['target_id'] if r['relation_type']=='CHILD_OF' else r['source_id'] for r in rr if r['relation_layer']=='TEXTUAL_HIERARCHY' and r['relation_type'] in ('CHILD_OF','HIERARCHICALLY_ABOVE')]
    check['GROUP_AND_ROOT_NOT_TEXTUAL_PARENTS']=not (set(parents)&forbidden) and all(not r['technical_only'] for r in nn if r['node_kind']=='COMPOSITION_GROUP')
    check['FUTURE_OVERLAY_APPEND_ONLY']=proposal['future_overlay_extension']==s['proposal']['future_overlay_extension'] and proposal['future_overlay_extension']['lower_layer_mutation_required'] is False and m['new_overlay_relations']==[]
    check['ALL_RECORDS_MAPPED']=len(mapped)==len(expected) and {r['mapping_id'] for r in mapped}=={r['mapping_id'] for r in expected} and len({r['mapping_id'] for r in mapped})==len(mapped)
    check['MAPPING_REPRODUCIBLE']=mapped==expected
    check['NO_DROPPED_PROVENANCE']=all(r['contract_record']['original_record']==r['source_record'] and r['contract_record']['provenance_ids']==[r['source_receipt']] for r in mapped) and [(r['source_record'],r['source_receipt']) for r in mapped]==[(r['source_record'],r['source_receipt']) for r in expected]
    check['MAPPING_ISSUES_REPORTED']=m['issues']==mapping_issues(mapped) and all(r['mapping_status'] in MAPPING_STATUSES for r in mapped)
    check['R43_ALL_FIELDS_AUDITED']=m['schema_audit']==schema_audit(s) and all(r['classification'] in SCHEMA_CLASSES for r in m['schema_audit'])
    check['CONTRACT_PROPOSAL_NOT_APPROVAL']=proposal==s['proposal'] and proposal['proposal_status']=='CONTRACT_PROPOSAL' and len(proposal['review_questions'])==7
    check['REPORTS_FAITHFUL']=m['reports']==reports(m,s)
    check['HISTORICAL_BYTES_UNCHANGED']=m['historical']==s['files']
    check['FROZEN_PINS']=len(s['pins'])==len(s['cfg']['frozen_files']) and all(r['actual']==r['expected']==s['cfg']['frozen_files'][r['path']] for r in s['pins'])
    check['REQUEST_AND_PROPOSAL_EXACT']=sha(s['request'])==s['cfg']['source_request']['sha256'] and sha(s['proposal_bytes'])==s['cfg']['proposal']['sha256'] and s['proposal']==json.loads(s['proposal_bytes'])
    check['DETERMINISTIC_PAYLOAD']=m['rerun_digest']==digest(m)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in check.items()]


def serialize(m,s):
    gg=gates(m,s);require(all(r['status']=='PASS' for r in gg),str([r for r in gg if r['status']!='PASS']))
    files={HISTORY+k:v for k,v in m['historical'].items()};files.update(m['reports'])
    files['01_r4_3_schema_audit.csv']=util.csv_bytes(m['schema_audit'])
    inventory=[]
    for r in s['cfg']['inputs']:
        inventory.append(dict(**r,source_artifact_sha256=s['receipt']['sha256'],member_sha256=sha(s['files'][r['member']]),
            record_count=sum(x['source_member']==r['member'] for x in m['mapping']),precedence='PRESERVE_HISTORY; APPLY_LATEST_EXPLICIT_SAME_QUESTION_AND_DIMENSION_ONLY'))
    files['02_hsa3_authoritative_inputs.csv']=util.csv_bytes(inventory)
    for i,kind in enumerate(('node','relation','status','provenance'),3):
        files[f'{i:02d}_r4_4_{kind}_contract_proposal.csv']=util.csv_bytes(m['proposal']['fields'][kind])
    files['09_r4_4_fixture_catalog.csv']=util.csv_bytes(m['fixtures'])
    files['10_r4_4_dry_run_mapping.csv']=util.csv_bytes(m['mapping'])
    files['11_r4_4_mapping_issues.csv']=util.csv_bytes(m['issues'],['mapping_id','source_member','source_identity','mapping_status','issue'])
    files['17_researcher_source.txt']=s['request'];files['18_contract_proposal.json']=s['proposal_bytes']
    files['90_run_metadata.json']=util.json_bytes(dict(version='R4.4-CONTRACT.0.1',status='PASS',mode=s['mode'],gate_count=len(gg)+1,
        contract_status='CONTRACT_PROPOSAL',counts=counts(m),baseline_commit=m['commit'],input_receipt=m['receipt'],frozen_receipts=s['pins'],
        config_sha256=sha(CONFIG.read_bytes()),audit_harness_sha256=sha(Path(__file__).read_bytes()),request_sha256=sha(s['request']),
        proposal_sha256=sha(s['proposal_bytes']),document_hashes={k:sha(v) for k,v in s['documents'].items()},
        rerun_payload_sha256=m['rerun_digest'],r44_consumer_implemented=False,
        release_checks='Full regression skip-zero and independent ZIP equality verified externally; stage exit is not human approval.'))
    n.l.f.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['15_gates.csv']=util.csv_bytes(gg);n.l.f.seal(files);require(util.manifest_ok(files),'output manifest');return files


def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--self-test',action='store_true');ap.add_argument('--archive');ap.add_argument('--out',required=True)
    args=ap.parse_args(argv);s=load(args.self_test,args.archive);files=serialize(build(s),s)
    require(n.l.d.h.f.a.prep.r43.frozen_receipts(s['cfg'])==s['pins'],'frozen files changed during audit')
    require(all((ROOT/p).read_bytes()==s['documents'][out] for out,p in DOCUMENTS.items()),'contract document changed during audit')
    if not args.self_test:require(sha((Path(args.archive) if args.archive else ROOT/s['cfg']['archive']['path']).read_bytes())==s['receipt']['sha256'],'archive changed during audit')
    n.l.d.h.f.a.prep.publish(files,args.out);out=Path(args.out).resolve();zp=out.with_name(out.name+'_results.zip')
    receipt='R4.4-CONTRACT.0.1 AUDIT PASS\n'+s['mode']+'\nZIP SHA256 '+sha(zp.read_bytes())+'\n'
    out.with_name(out.name+'_run.log').write_text(receipt,encoding='utf-8');print(receipt);return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
