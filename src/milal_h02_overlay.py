"""Append explicit researcher dispositions; never infer an adjudication from evidence."""
from copy import deepcopy
from milal_mfr02r_data import table, encode

ACCEPT = 'ACCEPTED_AS_LOCAL_MOTHER'
REJECT = 'REJECTED_AS_DIRECT_MOTHER'
RATIONALE = 'LOCAL_CONDITIONAL_PROTASIS_APODOSIS_CONFIGURATION'
REQUIRED_OBSERVATIONS = {
    'LOCAL_CONDITIONAL_CONSTRUCTION', 'DIRECT_PRIMARY_BINDING',
    'LOCAL_STRUCTURAL_COMPLETION', 'TWO_COLON_ORGANIZATION',
}


def bind_registry(outcomes, packets, pivots, registry):
    """Exact IDs only. Surface strings are independent human/machine representations."""
    oi = {r['structural_outcome_group_id']: r for r in outcomes}
    pi = {p['review_item_id']: p for p in packets}
    if len(oi) != len(outcomes) or len(pi) != len(packets):
        raise ValueError('duplicate source identity')
    if len(registry) != 2 or len({r['candidate_relation_id'] for r in registry}) != 2:
        raise ValueError('one packet requires two distinct candidate dispositions')
    if len({r['judgment_id'] for r in registry}) != 1 or len({r['review_packet_id'] for r in registry}) != 1:
        raise ValueError('one human decision packet required')
    if {r['human_decision'] for r in registry} != {ACCEPT, REJECT}:
        raise ValueError('explicit accepted and rejected dispositions required')
    targets = {str(p['target']) for p in pivots}
    snapshots = []
    for r in registry:
        oid, pid = r['candidate_relation_id'], r['review_packet_id']
        if oid not in oi or pid not in pi:
            raise ValueError('unresolved exact relation/packet identity')
        o, p = oi[oid], pi[pid]
        if (o['target'], o['source_or_peer'], o['relation_type']) != (
            r['target_clause_id'], r['source_clause_id'], r['machine_relation_type']
        ) or r['target_clause_id'] not in targets:
            raise ValueError('source/target/relation/pivot identity mismatch')
        aa = [a for a in p['alternatives'] if a['assignment_id'] == r['alternative_id']]
        if len(aa) != 1 or aa[0]['assignment']['selected_relation_ids'] != [oid]:
            raise ValueError('exact coherent singleton alternative required')
        qq = [q for q in aa[0]['relations'] if q['relation_id'] == oid]
        if len(qq) != 1:
            raise ValueError('alternative relation missing or duplicated')
        q = qq[0]
        if r['machine_rule'] not in {g['rule_id'] for g in q['grammar_rules']}:
            raise ValueError('machine rule provenance mismatch')
        if sorted(q['primary_source_binding']) != sorted(r['machine_binding']):
            raise ValueError('primary binding provenance mismatch')
        if [int(x) for x in r['target_atom_ids']] != q['target']['clause_atom_ids']:
            raise ValueError('target atom mismatch')
        if (str(q['source']['clause_id']), str(q['target']['clause_id'])) != (r['source_clause_id'], r['target_clause_id']):
            raise ValueError('packet node mismatch')
        snapshots.append(dict(candidate_relation_id=oid, original_outcome=deepcopy(o),
                              original_alternative=deepcopy(aa[0])))
    packet = pi[registry[0]['review_packet_id']]
    packet_relations = {q['relation_id'] for a in packet['alternatives'] for q in a['relations']}
    if packet_relations != {r['candidate_relation_id'] for r in registry}:
        raise ValueError('all packet alternatives must be disposed explicitly')
    return snapshots


def rationale_valid(r):
    return (r['human_rationale_code'] == RATIONALE
            and REQUIRED_OBSERVATIONS <= set(r['rationale_observations'])
            and r['proximity_alone_sufficient'] is False
            and r['machine_rule_rationale_adopted'] is False
            and bool(r['human_rationale_text']))


def build(outcomes, packets, pivots, registry, historical):
    snapshots = bind_registry(outcomes, packets, pivots, registry)
    accepted = [deepcopy(r) for r in registry if r['human_decision'] == ACCEPT]
    rejected = [deepcopy(r) for r in registry if r['human_decision'] == REJECT]
    if not rationale_valid(accepted[0]):
        raise ValueError('explicit local construction rationale required; proximity alone insufficient')
    a, r = accepted[0], rejected[0]
    if (r['no_relation_all_layers'] is not False or a['lexical_semantics_status'] != 'UNRESOLVED_FOR_HIERARCHY_PURPOSES'
            or any(x['canonical_whole_book_status'] != 'NOT_CANONICAL' for x in registry)):
        raise ValueError('human adjudication scope exceeded')
    resolved = {a['target_clause_id']}
    overlay = [dict(target=p['target'], h01_status=p['target_status'],
                    h02_status='HUMAN_ADJUDICATED', selected_local_mother=a['source_clause_id'],
                    rejected_direct_mother=r['source_clause_id'], judgment_id=a['judgment_id'],
                    pivot_status_after_human_adjudication='RESOLVED_BY_HUMAN',
                    canonical_whole_book_status='NOT_CANONICAL')
               for p in pivots if str(p['target']) in resolved]
    status = []
    ri = {x['candidate_relation_id']: x for x in registry}
    for o in outcomes:
        rid = o['structural_outcome_group_id']; h = ri.get(rid)
        status.append(dict(relation_id=rid, source=o['source_or_peer'], target=o['target'],
                           machine_status='MACHINE_QUALIFIED', machine_relation_type=o['relation_type'],
                           h02_human_status=h['human_decision'] if h else 'NOT_ADJUDICATED_BY_H02',
                           human_accepted_by_h02=bool(h and h['human_decision'] == ACCEPT),
                           canonical_accepted=False, prior_human_registry='PRESERVED_SEPARATELY'))
    decision = dict(judgment_id=a['judgment_id'], review_packet_id=a['review_packet_id'],
                    target_clause_id=a['target_clause_id'], target_atom_ids=a['target_atom_ids'],
                    candidate_relation_ids=[x['candidate_relation_id'] for x in registry],
                    disposition_count=len(registry), status='HUMAN_ADJUDICATED',
                    researcher_authority=a['researcher_authority'], provenance=a['provenance'])
    review = dict(machine_true_pivots_before=len(pivots), human_adjudicated_pivots=len(overlay),
                  remaining_unadjudicated_true_pivots=len(pivots)-len(overlay),
                  new_human_decision_packets=1, new_candidate_dispositions=len(registry),
                  historical_human_registry_entries=len(historical),
                  combined_registry_decision_entries=len(historical)+1,
                  counting_contract='13_LEGACY_DECISION_ENTRIES_PLUS_ONE_H02_PACKET_NOT_TWO_DISPOSITIONS',
                  qualified_relations=len(outcomes), all_qualified_relations_accepted=False)
    return dict(decisions=[decision], dispositions=deepcopy(registry), accepted=accepted, rejected=rejected,
                overlay=overlay, status=status, review=[review], outcomes=deepcopy(outcomes),
                historical=deepcopy(historical), machine_provenance=snapshots,
                new_relations=[], canonical_hierarchy=[])


FILES = {
    'decisions':'01_h02_human_decision_packets.csv', 'dispositions':'02_h02_candidate_dispositions.csv',
    'accepted':'03_h02_human_accepted_relations.csv', 'rejected':'04_h02_human_rejected_direct_mothers.csv',
    'overlay':'05_h02_pivot_resolution_overlay.csv', 'status':'06_h02_machine_vs_human_status.csv',
    'review':'09_h02_post_adjudication_review_status.csv', 'outcomes':'preserved_qualified_relations.csv',
    'historical':'preserved_historical_human_judgments.csv', 'machine_provenance':'machine_provenance.csv',
}


def reports(state):
    a, r = state['accepted'][0], state['rejected'][0]
    report = '# H0.2 — explicit researcher adjudication\n\n'
    report += 'One human decision packet with two dispositions. The machine packet is unchanged.\n\n'
    for row in state['dispositions']:
        report += f"## {row['source_clause_id']} → {row['target_clause_id']}\n\n"
        report += '| Field | Human record |\n|---|---|\n'
        for key, value in row.items():
            report += '| '+key+' | '+(encode(value) if not isinstance(value,str) else value).replace('|','\\|')+' |\n'
        report += '\n'
    caution = ('# KI_FUNCTION_CAUTION\n\nכי is a formal surface feature. No universal semantic '
               'function is assigned. The researcher accepts the local אם ... כי construction; '
               'W-A01 remains frozen and its rationale is not automatically adopted.\n\n'
               'LEXICAL_SEMANTIC_INTERPRETATION: UNRESOLVED_FOR_HIERARCHY_PURPOSES. '
               'STRUCTURAL_MOTHER_DECISION: RESOLVED. H0.2 does not decide the lexical root '
               'or translation of יבלע and does not reopen other כי occurrences.\n')
    method = ('# H0.2 method audit\n\nThe human decision is transcribed from explicit researcher '
              'authority, not computed from proximity, scores or a new discovery rule. '
              'The edge is accepted through LOCAL_CONDITIONAL_PROTASIS_APODOSIS_CONFIGURATION; '
              'machine W-A01 and SB01/SB02 provenance remains separately preserved.\n\n'
              'If the source were merely nearer without the formal local construction, direct primary '
              'binding, structural completion and two-colon organization, proximity alone would be insufficient. '
              'The two-colon grouping is POST_RELATION_VALIDATION_CONTEXT and does not create a paratactic edge.\n\n'
              'Rejection concerns direct strict motherhood only; it does not assert NO_RELATION_IN_ALL_LAYERS. '
              'All machine candidates survive. Other relations are NOT_ADJUDICATED_BY_H02; any historical '
              'judgments remain in their original registry and are not overridden.\n\n'
              'Counting: 13 legacy decision entries + 1 H0.2 decision packet = 14 combined decision entries. '
              'Two candidate dispositions are not two independent human decisions. '
              'Historical registry rows are not relabeled as H0.2 packets.\n')
    next_scope = ('# Next scope\n\nREADY_FOR_MFR_0_2R_H1_0, subject to all release gates.\n\n'
                  'Do not start H1.0 automatically. A later authorized provisional assembly must keep '
                  'MACHINE_QUALIFIED, HUMAN_ACCEPTED, HUMAN_REJECTED, PROVISIONALLY_INSTANTIATED '
                  'and CANONICAL_ACCEPTED distinct. No canonical whole-book hierarchy is produced here.\n')
    return {'07_h02_job_37_20_adjudication.md':report, '08_h02_ki_function_caution.md':caution,
            '10_h02_method_report.md':method, '11_h02_next_scope.md':next_scope}


def write_outputs(out, state):
    for key, name in FILES.items():
        table(out/name, state[key])
    for name, text in reports(state).items():
        (out/name).write_text(text, encoding='utf8', newline='\n')
