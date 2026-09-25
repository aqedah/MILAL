"""Paged, complete presentation of eligible alternatives; no top-N selection."""
from pathlib import Path
import json
from milal_mfr02r_data import encode, table
from milal_r3c_0_2_reviewability import REVIEW_FIELDS

HUMAN_FIELDS = tuple(dict.fromkeys((*REVIEW_FIELDS, 'human_selected_candidate', 'human_selected_relation',
    'CONFIRM_CURRENT', 'REVISE_CURRENT', 'MULTIPLE_PLAUSIBLE', 'INSUFFICIENT', 'mother_if_hypotactic',
    'parallel_peer_if_paratactic', 'alternative_retained', 'rationale', 'additional_context_needed')))


def blank_fields():
    return {k: '' for k in HUMAN_FIELDS}


def evidence_summary(label, value):
    if isinstance(value,dict) and 'support' in value:
        return '%s; observed predicates: %s; counterevidence: %s.' % (
            value['support'], ', '.join(value.get('predicates',[])) or 'none', ', '.join(value.get('counterevidence',[])) or 'none')
    if label=='CONSTRUCTION_SIGNATURE':
        return '\n'.join('- Clause %s: %s; phrase sequence %s.'%(n,r['clause_type'],' → '.join(r['phrase_function_sequence'])) for n,r in value.items())
    if label=='VALENCY':
        return '\n'.join('- Clause %s: predicates %s; observed slots %s; obligatory arguments not inferred.'%(
            n,', '.join(r['predicate_lexeme']) or 'not available',', '.join(r['phrase_functions'])) for n,r in value.items())
    if label=='CORPUS_ANALOGUE':
        return '\n'.join('- Clause %s: %s; %s. Exact index selectors retained below.'%(n,r['analogue_status'],r['regularity_status']) for n,r in value.items())
    if label=='POETIC_PROSODIC':
        return '%s; %s; exception: %s. No syntactic override.'%(value['relation'],value['prosodic_status'],value['exception_status'] or 'none')
    if label=='FORM':
        return '\n'.join('- %s: %s.'%(k,r.get('support','NOT_AVAILABLE')) for k,r in value.items())
    if label=='SOURCE_TARGET_OBSERVATIONS':
        return '\n'.join('- Clause %s: time phrases %s; location phrases %s; participant surfaces %s; identity remains %s.'%(
            n,', '.join(p['surface'] for p in r['TIME']['phrases']) or 'none',
            ', '.join(p['surface'] for p in r['LOCATION']['phrases']) or 'none',
            ', '.join(p['participant_surface'] for p in r['PARTICIPANT']['mentions']) or 'none',
            r['PARTICIPANT']['referential_identity']) for n,r in value.items())
    return encode(value)


def write_target(out, target, inventory, cards, counts, page_size):
    directory = Path(out) / 'packets'; directory.mkdir(exist_ok=True)
    pages = []
    for start in range(0, len(cards), page_size):
        page = 'target_%s_%04d.md' % (target, start // page_size + 1)
        text = ['# Target %s — candidate details' % target,
                'All pages are equally reviewable. Source order is navigation only. No candidate is selected.']
        for card in cards[start:start + page_size]:
            source = inventory[int(card['source_candidate_id'])]
            text += ['## ' + card['candidate_id'], source['surface_hebrew'],
                     'Source %s → target %s; %s → %s; distance %s clauses.' % (
                         card['source_candidate_id'], target, source['clause_type'], inventory[target]['clause_type'], card['distance']),
                     'Why included: ' + ', '.join(card['review_reason_codes']),
                     'Existing relation: ' + card['existing_candidate_relation'],
                     'Matched rules: ' + encode(card['source_contributions']),
                     '### Evidence (observations, not new adjudication)']
            for label, value in card['detail'].items():
                text += ['**' + label + '**', evidence_summary(label,value),
                         '<details><summary>Exact source fields</summary>\n\n```json\n'+json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n```\n\n</details>']
            text += ['### What would change if selected?', encode(card['global_impact']),
                     'Conditional conflicts: ' + encode(card['conflict_ids']),
                     'Variant components: ' + encode(card['component_ids']),
                     'Compatibility: ' + encode(card['compatibility']),
                     'Raw provenance: ' + encode(card['existing_evidence']),
                     'Human conclusion: blank. Use the tier CSV; no automatic conclusion.']
        (directory / page).write_text('\n\n'.join(text) + '\n', encoding='utf8')
        pages.append('packets/' + page)
    summary = ['# Target %s' % target, inventory[target]['surface_hebrew'],
               '%s %s:%s · %s' % tuple(inventory[target][k] for k in ('book','chapter','verse','clause_type')),
               'Nearby source context (navigation, not an inferred unit):']
    ordered=sorted(inventory,key=lambda n:int(inventory[n]['position']))
    position=ordered.index(target)
    summary += ['%s: %s'%(n,inventory[n]['surface_hebrew']) for n in ordered[max(0,position-2):position+3]]
    summary += [
               'Archive summary: ' + encode(counts),
               'Eligible candidate pages (complete; no ranking or truncation):']
    summary += ['- [Page %d](%s)' % (i + 1, Path(p).name) for i, p in enumerate(pages)]
    summary += ['All source pairs remain in 01_h0_candidate_review_eligibility.csv and the immutable upstream tables.']
    name = 'packets/target_%s.md' % target
    (Path(out) / name).write_text('\n\n'.join(summary) + '\n', encoding='utf8')
    return dict(target_id=target, packet=name, pages=pages, candidate_ids=[r['candidate_id'] for r in cards],
                card_count=len(cards), largest_page=min(page_size, len(cards)))


def historical_packet(out, old, targets, inventory):
    result, markdown = [], ['# MFR.0.2A — 13 provisional configuration cases',
        'Historical decisions are displayed after current-evidence eligibility is frozen. No constituent edge is inferred from a configuration judgment.']
    for row in old:
        ids = [int(t) for t in row['target_clause_ids']]
        entry = dict(case_id=row['decision_id'], target_ids=ids,
                     current_provisional_decision=row['researcher_decision'], original_configuration=row,
                     candidate_ids=[c for t in ids for c in targets[t]['eligible_candidate_ids']],
                     new_relation_candidate_ids=[c for t in ids for c in targets[t]['relation_candidate_ids']],
                     new_configuration_candidate_ids=[c for t in ids for c in targets[t]['configuration_candidate_ids']],
                     excluded_evidence_only=sum(targets[t]['class_counts']['EVIDENCE_ONLY'] for t in ids),
                     excluded_insufficient=sum(targets[t]['class_counts']['INSUFFICIENT'] for t in ids),
                     review_tier='TIER_1', packets=[targets[t]['packet'] for t in ids], **blank_fields())
        result.append(entry)
        markdown += ['## ' + entry['case_id'], 'Current provisional decision: ' + entry['current_provisional_decision'],
                     'Original source configuration: ' + encode(row['source_clause_ids']),
                     '\n'.join('- Source %s: %s'%(s,inventory[int(s)]['surface_hebrew']) for s in row['source_clause_ids']),
                     'Original evidence: ' + encode({k:v for k,v in row.items() if k.startswith(('underlying_', 'independent_'))}),
                     'Original rationale (not a new H0 conclusion): ' + row.get('rationale', ''),
                     '### Targets and actual competing candidates']
        for tid in ids:
            t = targets[tid]
            markdown += ['**Target %s**: %s' % (tid, inventory[tid]['surface_hebrew']),
                         'Current eligible alternatives: %d; archived evidence-only %d; insufficient %d.' % (
                             len(t['eligible_candidate_ids']), t['class_counts']['EVIDENCE_ONLY'], t['class_counts']['INSUFFICIENT']),
                         '[Complete paged candidate cards](%s)' % t['packet']]
        markdown += ['Human fields remain blank. CONFIRM_CURRENT / REVISE_CURRENT / MULTIPLE_PLAUSIBLE / INSUFFICIENT are options, not assigned outcomes.']
    table(Path(out) / '10_h0_mfr02a_13_case_packet.csv', result)
    (Path(out) / '11_h0_mfr02a_13_case_packet.md').write_text('\n\n'.join(markdown) + '\n', encoding='utf8')
    return result
