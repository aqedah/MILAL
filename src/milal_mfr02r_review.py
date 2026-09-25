"""Post-freeze comparison and blank target-centered human review, without new judgments."""
import hashlib
import json
import zipfile
from collections import defaultdict
from pathlib import Path
from milal_mfr02r_data import rows, table, zip_rows, encode, digest
from milal_r3c_0_2_reviewability import REVIEW_FIELDS

EXTRA_REVIEW_FIELDS = ('selected_candidate', 'selected_relation', 'HYPOTACTIC', 'PARATACTIC', 'FORMAL_ONLY',
                       'INSUFFICIENT', 'MULTIPLE_PLAUSIBLE', 'mother_if_hypotactic', 'alternative_retained', 'rationale', 'additional_context_needed')


def select_review_targets(receipts, inventory, affected, unit_targets, ambiguous):
    return {tid for tid, r in receipts.items() if int(r['hierarchy_candidate_count']) > 1 or
        tid in affected or tid in unit_targets or tid in ambiguous or inventory[tid]['frame_candidate']}


def revalidation_rows(previous, target_sets, pairs):
    for old in previous:
        sources = [int(x) for x in old['source_clause_ids']]
        targets = [int(x) for x in old['target_clause_ids']]
        evidence = [pairs[s, t] for s in sources for t in targets if (s, t) in pairs]
        competitors = sorted({s for t in targets for s in target_sets.get(t, ())} - set(sources))
        proposed = {r for row in evidence for r in row['relations']}
        current = old['researcher_decision']
        status = 'CURRENT_DECISION_NOT_YET_DECIDABLE'
        # A multi-clause human configuration is not equivalent to one onset edge.
        if len(sources) == len(targets) == 1:
            if current in proposed:
                status = 'CURRENT_DECISION_SUPPORTED_BUT_ALTERNATIVE_EXISTS' if competitors or len(proposed) > 1 else 'CURRENT_DECISION_STRONGLY_SUPPORTED'
            elif current == 'FORMAL_ONLY' and evidence and not proposed and all(r['status'] == 'FORMAL_ONLY' for r in evidence):
                status = 'FORMAL_ONLY_CONFIRMED'
            elif current == 'INSUFFICIENT' and evidence and not proposed and all(r['status'] == 'INSUFFICIENT' for r in evidence):
                status = 'INSUFFICIENT_CONFIRMED'
        yield dict(decision_id=old['decision_id'], current_human_decision=current, original_decision=old,
            original_row_sha256=hashlib.sha256(encode(old).encode()).hexdigest(),
            provisional_status='PROVISIONAL_HUMAN_ADJUDICATION',
            relation_status='PROVISIONAL_PARATACTIC_PENDING_CANDIDATE_SET_REVALIDATION' if current == 'PARATACTIC' else 'PROVISIONAL_HUMAN_ADJUDICATION',
            source_clause_ids=sources, target_clause_ids=targets,
            candidate_set_count={str(t): len(target_sets.get(t, ())) for t in targets}, new_competing_candidates=competitors,
            relation_rules_supporting_current_decision=[r for r in evidence if current in r['relations']],
            relation_rules_supporting_alternatives=[r for r in evidence if set(r['relations']) - {current}],
            global_configuration_effect='REFER_TO_COMPONENT_CONSTRAINTS; CONFIGURATION_NOT_IDENTICAL_TO_CONSTITUENT_EDGE',
            revalidation_status=status, revised_human_decision='', canonical_relation='')


def run_review(blind_job, controls, input_archive, out):
    blind_job, controls, out = Path(blind_job), Path(controls), Path(out)
    if not (controls / 'control_freeze.json').is_file():
        raise ValueError('human decisions loaded before control freeze')
    freeze = json.loads((controls / 'control_freeze.json').read_text())
    if any(digest(controls / r['path']) != r['sha256'] for r in freeze['files']):
        raise ValueError('control freeze changed')
    with zipfile.ZipFile(input_archive) as archive:
        old = list(zip_rows(archive, '01_mfr_0_2a_human_decisions.csv'))
    table(out / 'mfr02a_original_decisions.csv', old)
    targets = {int(r['target_clause_id']): r['candidate_clause_ids'] for r in rows(blind_job / '07_preceding_candidate_sets.csv')}
    needed = {(int(s), int(t)) for r in old for s in r['source_clause_ids'] for t in r['target_clause_ids']}
    pairs, ambiguous = {}, set()
    for r in rows(blind_job / '10_relation_candidates.csv'):
        key = (int(r['source_clause_id']), int(r['target_clause_id']))
        if key in needed:
            pairs[key] = r
        if len(r['relations']) > 1:
            ambiguous.add(key[1])
    revalidated = list(revalidation_rows(old, targets, pairs))
    table(out / '18_mfr02a_revalidation.csv', revalidated)
    inventory = {int(r['clause_id']): r for r in rows(blind_job / '02_clause_feature_inventory.csv')}
    affected = {int(t) for r in revalidated if r['new_competing_candidates'] for t in r['target_clause_ids']}
    receipts = {int(r['target_clause_id']): r for r in rows(blind_job / 'target_search_receipts.csv')}
    unit_targets = {int(t) for r in rows(blind_job / 'participant_unit_reference_evidence.csv') for t in r.get('target_clause_ids', [r.get('target_clause_id')])}
    selected = select_review_targets(receipts, inventory, affected, unit_targets, ambiguous)
    compatibility = {r['edge_id']: r for r in rows(blind_job / '14_global_compatibility_matrix.csv')}
    components = {eid:r['component_id'] for r in rows(blind_job / '15_variant_components.csv') for eid in r['alternative_edge_ids']}
    cases = []
    for tid in sorted(selected, key=lambda t: int(inventory[t]['position'])):
        cases.append(dict(case_id='REVIEW-' + str(tid), target_clause_id=tid, candidate_ids=targets[tid],
            larger_unit_candidate_selector=dict(table='blind/job/participant_unit_reference_evidence.csv', target_clause_id=tid, include='ALL_ROWS_WITH_TARGET_IN_TARGET_CLAUSE_IDS_OR_EXACT_TARGET_ID'),
            selection_reason='COMPETING_CANDIDATES_OR_UNRESOLVED_FRAME_OR_PROVISIONAL_H1',
            packet='review_packets/target_' + str(tid) + '.md',
            **{name: '' for name in REVIEW_FIELDS}, **{name: '' for name in EXTRA_REVIEW_FIELDS}))
    table(out / '24_human_review_cases.csv', cases)
    packet_dir = out / 'review_packets'; packet_dir.mkdir(parents=True, exist_ok=True)
    # One target at a time; all admitted candidates remain in source order.
    stream = None; current = None
    try:
        for row in rows(blind_job / '09_candidate_evidence_matrix.csv'):
            tid, sid = int(row['target_clause_id']), int(row['candidate_clause_id'])
            if tid not in selected:
                continue
            if tid != current:
                if stream:
                    stream.close()
                current = tid
                stream = (packet_dir / ('target_' + str(tid) + '.md')).open('w', encoding='utf8')
                target = inventory[tid]
                stream.write('# Target %s\n\n%s %s:%s · %s\n\n%s\n\n' % (tid, target['book'], target['chapter'], target['verse'], target['clause_type'], target['surface_hebrew']))
                neighbors = [v for v in inventory.values() if abs(int(v['position']) - int(target['position'])) <= 3]
                stream.write('Context (source clauses, not a paragraph):\n\n' + '\n'.join('- %s: %s' % (n['clause_id'], n['surface_hebrew']) for n in neighbors) + '\n\n')
                stream.write('Human fields: all blank in 24_human_review_cases.csv. No candidate is preselected.\n\n')
                stream.write('Full observed values: blind/job/02_clause_feature_inventory.csv, keyed by the exact source and target clause IDs and dimension name. Global effects: 13–15; unit references and poetic layer remain separate.\n\n')
                stream.write('Larger-unit cases: include every record whose target_clause_ids contains %s. Resolve witnesses with milal_mfr02r_query.py; no unit is selected as a mother.\n\n' % tid)
            source = inventory[sid]
            stream.write('## Candidate %s · %s\n\n%s\n\nDistance: %s clauses. Rules: %s. Relations: %s.\n\n' %
                (sid, source['clause_type'], source['surface_hebrew'], row['distance_clauses'], ', '.join(row['rule_ids_matched']), row['candidate_relations']))
            for dim in ('GRAPHEME', 'WORD', 'PHRASE', 'CLAUSE', 'TIME', 'LOCATION', 'PARTICIPANT', 'REFERENCE', 'DOMAIN', 'LEXICAL', 'SEMANTIC_CORRESPONDENCE'):
                stream.write('- %s: %s\n' % (dim, encode(row[dim])))
            stream.write('\nObserved source phrases: ' + encode(source['PHRASE']) + '\n\n')
            edge_ids = [row['pair_id'] + suffix for suffix in ('-H','-P') if row['pair_id'] + suffix in compatibility]
            effects = [dict(edge_id=eid, variant_component=components[eid],
                hard_conflicts=compatibility[eid]['conflicting_relations'],
                reassessment=compatibility[eid]['relations_requiring_reassignment'],
                level_effect=compatibility[eid]['embedding_effect'],
                parallel_effect=compatibility[eid]['parallel_chain_effect']) for eid in edge_ids]
            stream.write('Conditional global effects and exact conflict/variant IDs: ' + encode(effects) + '\n\n')
            stream.write('\nPair: `%s`; all variants remain conditional, no accepted mother.\n\n' % row['pair_id'])
    finally:
        if stream:
            stream.close()
    for case in cases:
        path = out / case['packet']
        if not path.exists():
            target = inventory[case['target_clause_id']]
            path.write_text('# Target %s\n\n%s\n\nNo preceding candidate admitted. NEW_HIGHER_LEVEL_CANDIDATE remains unadjudicated; no root or level is assigned.\n' %
                            (case['target_clause_id'], target['surface_hebrew']), encoding='utf8')
    (out / '25_human_review_packet.md').write_text('# MFR.0.2R-H target-centered review\n\n'
        'Read the source evidence and alternatives before filling the blank review CSV.\n'
        'Unreviewed candidates and any future rejected candidates remain preserved.\n\n' +
        '\n'.join('- [Target %s](%s)' % (c['target_clause_id'], c['packet']) for c in cases) + '\n', encoding='utf8')
    return dict(previous_decisions=len(old), provisional_decisions=len(revalidated),
                original_decision_hashes={r['decision_id']: hashlib.sha256(encode(r).encode()).hexdigest() for r in old},
                previous_paratactic=sum(r['current_human_decision'] == 'PARATACTIC' for r in revalidated),
                review_cases=len(cases), new_human_judgments=0,
                revalidation_statuses={status: sum(r['revalidation_status'] == status for r in revalidated) for status in sorted({r['revalidation_status'] for r in revalidated})})
