"""Whole-Job qualified-universe audit; diagnostic and historical inputs are absent."""
from collections import Counter,defaultdict
from milal_mfr02r_data import rows,table,digest,encode
from milal_q13_pipeline import write
from milal_q1_binding import identity
from milal_h01_model import sieve
from milal_h01_evidence import gap_register,load_catalog,packets,DISPLAY_ROLES,REVIEW_FIELDS


def nondecision_groups(result,catalog):
    grouped=defaultdict(list)
    for d in result['dispositions']:
        if d['decision_component']:continue
        r=d['original_relation'];p=catalog['provenance'][d['relation_id']];family=[]
        for wid in p['witness_ids']:
            ev=catalog['graph'][wid]['payload']['frozen_witness']['evidence']
            family += [(k,ev[k]) for k in sorted(ev) if k.startswith('family_') or 'signature' in k]
        key=encode(dict(relation_type=r['relation_type'],binding_modes=sorted({x['binding_mode'] for x in r['provenance_paths']}),
            primary_mechanisms=sorted({catalog['processes'][w]['mechanism_id'] for w in p['witness_ids'] if catalog['processes'][w]['primary_role']=='PRIMARY_SOURCE_BINDING'}),
            configuration_family_or_signature=sorted({encode(x) for x in family}),review_status=d['target_status']))
        grouped[key].append(d)
    groups=[];representatives=[]
    import json
    for key,ds in sorted(grouped.items()):
        ids=sorted(d['relation_id'] for d in ds);gid='HN-'+identity(key)
        groups.append(dict(group_id=gid,**json.loads(key),group_count=len(ids),relation_ids=ids,
            structural_status_types=sorted({d['structural_status'] for d in ds}),representative=ids[0],
            selection_provenance='LEXICOGRAPHIC_MINIMUM_EXACT_RELATION_ID; QA_ONLY; NO_RANDOM_OR_SCORING'))
        representatives.append(dict(group_id=gid,relation_id=ids[0],all_group_relation_ids=ids,qa_only=True,human_review_item=False))
    return groups,representatives


def render_packets(cards):
    text=['# H0.1 structural decision review packets','No alternatives are ranked or recommended. Qualified does not mean accepted. Unselected means UNDECIDED. Complete source evidence is retained in the CSV and packet_evidence_catalog.json.']
    for card in cards:
        text += ['## '+card['review_item_id'],'Targets: '+', '.join(card['target_ids'])]
        for t in card['targets']:text += [f"Job {t['chapter']}:{t['verse']} — clause {t['clause_id']} / atoms {encode(t['clause_atom_ids'])}",t['surface_hebrew']]
        text += ['Exact incompatibility: '+encode(card['global_constraints'])]
        for number,a in enumerate(card['alternatives'],1):
            text+=['### Alternative '+str(number)+' / '+a['assignment_id'],'Display order follows stable IDs only. '+a['meaning']]
            for r in a['relations']:
                text += [f"{r['relation']['source_or_peer']} → {r['relation']['target']}: {r['relation']['relation_type']} ({r['relation_id']})",
                    r['source']['surface_hebrew'],'Structural implication: '+r['structural_implication'],
                    'Grammar: '+', '.join(x['rule_id'] for x in r['grammar_rules']),
                    'Primary binding: '+', '.join(r['primary_source_binding'])]
                for role in DISPLAY_ROLES:text.append(role+': '+(', '.join(r['role_evidence_ids'][role]) or 'No recorded evidence in this role'))
                for tid,f in r['feature_evidence'].items():
                    text += ['Clause '+tid+' Time: '+encode(f['TIME'])+'; Location: '+encode(f['LOCATION']),
                        'Participant/reference: '+encode(f['PARTICIPANT'])+' / '+encode(f['REFERENCE']),
                        'Lexical FORM: '+encode([w['lex'] for w in f['WORD']])]
                text += ['Other-pair evidence is context only, not support for this alternative: '+encode(r['context_role_evidence_ids']),
                    'Exact native word/phrase records are also retained under feature_evidence in 12_h01_review_packets.csv.',
                    'Raw evidence IDs: '+encode(r['raw_evidence_ids']),
                    'Shared raw warnings (not independent votes): '+encode(r['shared_raw_warnings']),
                    'Unresolved evidence IDs: '+encode(r['unresolved_gap_ids'])]
        text+=['Review status: UNREVIEWED. All human judgment fields remain blank.']
    if not cards:text+=['No proven incompatible positive commitments require human review under the current contracts.']
    return '\n\n'.join(text)+'\n'


def audit(source,q16,q16r,out):
    inventory={str(r['clause_id']):r for r in rows(source/'blind/job/02_clause_feature_inventory.csv')}
    outcomes=list(rows(q16r/'preserved_qualified_relations.csv'));gaps=gap_register(q16r)
    prior=list(rows(q16r/'07_q16r_global_constraints.csv'))
    # The exact SB12 contract is in Q1.6R's preserved Q1.3 audit, not historical H0.
    import json
    q13=json.loads((q16r/'q13_compatibility_audit.json').read_text())
    constraints=q13['global_audit']['constraint_rows']
    result=sieve(outcomes,sorted(inventory),gaps,constraints);catalog=load_catalog(source,q16,q16r)
    for c in result['constraints']:
        catalog['processes'][c['constraint_id']]=dict(process_id=c['constraint_id'],mechanism_id='SB12',primary_role='GLOBAL_CONSTRAINT',detail=c,source_artifact='03_h01_structural_constraints.csv')
    cards,evidence=packets(result,inventory,outcomes,gaps,catalog)
    groups,reps=nondecision_groups(result,catalog)
    universe=[dict(review_item_id=c['review_item_id'],component_id=c['component_id'],target_ids=c['target_ids'],
        status=c['compatibility']['decision_status'],relation_ids=c['compatibility']['relation_ids'],packet_id=c['review_item_id'],review_status=c['review_status']) for c in cards]
    tables={'01_h01_relation_disposition.csv':result['dispositions'],'02_h01_target_status.csv':result['targets'],
      '03_h01_structural_constraints.csv':result['constraints'],'04_h01_relation_compatibility.csv':result['matrix'],
      '05_h01_decision_components.csv':result['components'],'06_h01_coherent_assignments.csv':result['assignments'],
      '07_h01_true_decision_pivots.csv':[t for t in result['targets'] if t['true_target_decision_pivot']],
      '08_h01_human_review_universe.csv':universe,'09_h01_evidence_gap_register.csv':gaps,
      '10_h01_nondecision_groups.csv':groups,'11_h01_nondecision_representatives.csv':reps,'12_h01_review_packets.csv':cards,
      'preserved_qualified_relations.csv':outcomes}
    empty_fields={
      '03_h01_structural_constraints.csv':['constraint_id','relation_ids','targets','constraint_types','violations','provenance','minimal','hard','activation'],
      '05_h01_decision_components.csv':['component_id','targets','relation_ids','constraint_types','coherent_positive_assignments','decision_required','reason'],
      '06_h01_coherent_assignments.csv':['assignment_id','component_id','selected_relation_ids','target_assignments','undecided_relations','unselected_semantics','coherent'],
      '07_h01_true_decision_pivots.csv':['target','target_status','structural_status','qualified_relation_ids','decision_components','human_review_required'],
      '08_h01_human_review_universe.csv':['review_item_id','component_id','target_ids','status','relation_ids','packet_id','review_status'],
      '12_h01_review_packets.csv':['review_item_id','component_id','target_ids','targets','alternatives','compatibility','global_constraints','unresolved_gap_ids',*REVIEW_FIELDS]}
    if result['targets']:empty_fields['07_h01_true_decision_pivots.csv']=list(result['targets'][0])
    for name,rr in tables.items():table(out/name,rr,empty_fields.get(name) if not rr else None)
    write(out/'role_display_contract.json',dict(roles=list(DISPLAY_ROLES),source='FROZEN_Q16R_ROLE_ONTOLOGY'))
    write(out/'packet_evidence_catalog.json',evidence)
    (out/'13_h01_review_packets.md').write_text(render_packets(cards),encoding='utf8',newline='\n')
    constraint_counts={k:sum(k in c['constraint_types'] for c in result['constraints']) for k in ('MOTHER_COMPETITION','TRUE_PAIR_RELATION_CONFLICT','STRICT_MOTHER_CYCLE','PARALLEL_HIERARCHY_INCOMPATIBILITY_CANDIDATE','SB12_HARD_CONFLICT','EXPLICIT_NEGATIVE_CONFLICT')}
    metrics=dict(qualified=len(outcomes),mother=sum(r['relation_type']=='HYPOTACTIC' for r in outcomes),parallel=sum(r['relation_type']=='PARATACTIC' for r in outcomes),
        targets=len(inventory),target_status=result['target_counts'],structural_status=dict(Counter(t['structural_status'] for t in result['targets'])),
        relation_disposition=result['disposition_counts'],constraints=constraint_counts,decision_components=len(result['components']),
        true_pivots=sum(t['true_target_decision_pivot'] for t in result['targets']),human_review_items=len(cards),
        evidence_gaps=len(gaps),gap_types=dict(Counter(g['gap_type'] for g in gaps)),nondecision_groups=len(groups),
        new_relations=0,deleted_relations=0,new_human_judgments=0,search=result['search'])
    write(out/'16_h01_metrics.json',metrics)
    write(out/'blind_access_receipt.json',dict(classification_inputs=['FROZEN_QUALIFIED_OUTCOMES','JOB_TARGET_INVENTORY','Q16R_EVIDENCE_GAPS','FROZEN_Q13_SB12_CONSTRAINTS'],
        historical_review_inputs=[],human_judgment_inputs=[],diagnostic_inputs=[],method='MINIMAL_CONFLICT_DIRECTED_SEARCH'))
    write(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()}))
    return dict(result=result,inventory=inventory,outcomes=outcomes,gaps=gaps,catalog=catalog,cards=cards,universe=universe,groups=groups,reps=reps,metrics=metrics,evidence=evidence)
