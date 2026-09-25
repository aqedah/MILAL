"""Serialize supplied human decisions; never infer a decision from evidence."""
import copy
from collections import Counter
import milal_mfr_common as cm

DECISIONS = ('PARATACTIC', 'FORMAL_ONLY', 'INSUFFICIENT', 'HYPOTACTIC', 'EMBEDDING')
DECISION_FILE = '01_mfr_0_2a_human_decisions.csv'
FREEZE_FILES = (DECISION_FILE, '02_mfr_0_2a_decision_provenance.csv',
    '03_mfr_0_2a_configuration_crosswalk.csv', '04_mfr_0_2a_calibration_principles.csv',
    '05_mfr_0_2a_deferred_dimensions.csv', '12_accepted_configuration_relations.csv',
    '13_representation_inventory.json')


def keyed(rows, key):
    result = {r[key]: r for r in rows}
    cm.require(len(result) == len(rows), 'Duplicate identity: ' + key)
    return result


def assemble(supplied, h1, attachments, previous=()):
    """Append a new phase; earlier registry rows are neither replaced nor inferred."""
    source = keyed(supplied['decisions'], 'configuration_case_id')
    universe = keyed(h1, 'configuration_case_id')
    cm.require(set(source) == set(universe) == set(attachments), 'Exact H1 universe required')
    rows, provenance, crosswalk, deferred, accepted = [], [], [], [], []
    for cid in sorted(source):
        s, h, a = source[cid], universe[cid], attachments[cid]
        c = a['configuration']
        cm.require(c['configuration_case_id'] == cid, 'Attachment identity mismatch')
        cm.require(h['all_configuration_pair_ids'] == c['raw_pair_ids'], 'Pair membership mismatch')
        cm.require(set(c['raw_pair_ids']) == {r['relation_candidate_id'] for r in a['raw_relations']}, 'Raw pair loss')
        cm.require(h['marker_ids'] == c['marker_ids'] and h['bundle_ids'] == c['bundle_ids'], 'Dependency mismatch')
        decision = s['researcher_decision']
        cm.require(decision in DECISIONS, 'Unknown human decision')
        did = 'MFR02A-' + cid
        # Only formal/sequence observations are admitted for the accepted H1 rationale.
        # All other evidence remains unchanged in the case attachment.
        support = [e for e in a['evidence_provenance'] if decision == 'PARATACTIC'
                   and e['provenance_family'] in ('EVID_DIRECT_FORMAL', 'EVID_SEQUENCE_CONFIGURATION')
                   and e['independent_link_usable'] and not e['cessation_derived']
                   and not any(x.startswith('CESSATION:') for x in e['dependency_root_ids'])]
        cm.require(decision != 'PARATACTIC' or support, 'Accepted configuration lacks independent formal evidence')
        res = bool(c['resumption_pair_ids'])
        clo = any(e['cessation_derived'] or e['provenance_family'].startswith(('EVID_CESSATION', 'EVID_COVERAGE', 'EVID_NESTED')) for e in a['evidence_provenance'])
        row = dict(decision_id=did, phase='MFR_0_2A', decision_unit='CONFIGURATION_RELATION_CASE',
            configuration_case_id=cid, researcher_decision=decision,
            configuration_validity=s['configuration_validity'], formal_relationship=s['formal_relationship'],
            hierarchy_relation_decision=decision, mother_if_hypotactic='NONE',
            resumption_review_status='DEFERRED_TO_MFR_0_2B' if res else 'NO_H1_RESUMPTION_EVIDENCE',
            closure_review_status='DEFERRED_TO_MFR_0_2C' if clo else 'NO_H1_CLOSURE_EVIDENCE',
            RESUMPTIVE='UNREVIEWED_SEPARATE_DIMENSION', CLOSURE='UNREVIEWED_SEPARATE_DIMENSION',
            rationale=s['rationale'], limitations='CONFIGURATION_ONLY; NO_CONSTITUENT_EDGE_DERIVATION; OTHER_DIMENSIONS_UNADJUDICATED',
            underlying_raw_pair_ids=c['raw_pair_ids'], underlying_marker_ids=h['marker_ids'], underlying_bundle_ids=h['bundle_ids'],
            source_clause_ids=c['source_clause_ids'], target_clause_ids=c['target_clause_ids'],
            source_stage='MFR.0.1b', researcher_supplied=True, rewrites_history=False,
            independent_hierarchy_support_ids=[e['evidence_id'] for e in support])
        row.update({name: name == decision for name in DECISIONS})
        rows.append(row)
        provenance.append(dict(decision_id=did, configuration_case_id=cid, authority_sha256=supplied['authority_sha256'],
            source_section=s['source_section'], source_excerpt=s['source_excerpt'], excerpt_sha256=s['excerpt_sha256'],
            verbatim_formal_relationship=s['verbatim_formal_relationship'], inherited_rationale_from=s['inherited_rationale_from'],
            normalization='OBSERVABLE_TRANSITION_LABEL' if s['formal_relationship'] != s['verbatim_formal_relationship'] and not s['inherited_rationale_from'] else 'SUPPLIED_OR_EXPLICIT_RATIONALE_REFERENCE',
            evidence_attachment='evidence/' + cid + '.json', evidence_sha256=cm.sha(cm.js(a))))
        for rid in c['raw_pair_ids']:
            crosswalk.append(dict(decision_id=did, configuration_case_id=cid, raw_relation_id=rid,
                membership_role='EVIDENCE_MEMBERSHIP_ONLY', constituent_relation_created=False))
        deferred.append({k: row[k] for k in ('decision_id', 'configuration_case_id', 'resumption_review_status', 'closure_review_status', 'RESUMPTIVE', 'CLOSURE')})
        if decision == 'PARATACTIC':
            accepted.append(dict(relation_decision_id=did, configuration_case_id=cid,
                object_type='CONFIGURATION_RELATION_DECISION', relation='PARATACTIC',
                source_clause_ids=c['source_clause_ids'], target_clause_ids=c['target_clause_ids'],
                underlying_raw_pair_ids=c['raw_pair_ids'], constituent_edges_created=False))
    prior = list(previous)
    cm.require(not ({r['decision_id'] for r in prior} & {r['decision_id'] for r in rows}), 'Append-only duplicate decision')
    return dict(decisions=copy.deepcopy(prior) + rows, provenance=provenance, crosswalk=crosswalk,
        calibration=[dict(p, phase='MFR_0_2A', researcher_supplied=True, authority_sha256=supplied['authority_sha256']) for p in supplied['calibration_principles']],
        deferred=deferred, accepted=accepted,
        representation=dict(constituent_edges=[], mothers=[], trees=[], roots=[], consumers=[]))


def scope(rows, decisions, dimension):
    index = {r['configuration_case_id']: r for r in decisions}
    return [dict(r, future_phase='MFR_0_2B' if dimension == 'resumption' else 'MFR_0_2C',
        review_status='UNREVIEWED_SEPARATE_DIMENSION', human_decision='',
        h1_decision_id=index[r['configuration_case_id']]['decision_id'] if r['configuration_case_id'] in index else '',
        h1_does_not_adjudicate_this_dimension=True) for r in rows]


def gates(o, supplied, h1, attachments, env):
    rr = o['decisions']; by = keyed(rr, 'configuration_case_id'); counts = Counter(r['researcher_decision'] for r in rr)
    expected = {r['configuration_case_id']: r['researcher_decision'] for r in supplied['decisions']}
    g = {k: bool(env[k]) for k in ('BASELINE_COMMIT_VERIFIED', 'MFR_0_1_FROZEN_VERIFIED', 'MFR_0_1A_FROZEN_VERIFIED', 'MFR_0_1B_FROZEN_VERIFIED')}
    g['H1_CASE_COUNT_13'] = len(rr) == 13 and set(by) == set(expected) == {r['configuration_case_id'] for r in h1}
    for name, count in zip(DECISIONS, (5, 7, 1, 0, 0)):
        g[name + '_COUNT_' + str(count)] = counts[name] == count and all(r[name] == (r['researcher_decision'] == name) for r in rr)
    for cid, decision in sorted(expected.items()):
        g[cid + '_' + decision] = cid in by and by[cid]['hierarchy_relation_decision'] == by[cid]['researcher_decision'] == decision
    g['NO_CONSTITUENT_EDGE_AUTO_EXPANSION'] = not o['representation']['constituent_edges'] and len(o['accepted']) == counts['PARATACTIC'] and all(r['object_type'] == 'CONFIGURATION_RELATION_DECISION' and not r['constituent_edges_created'] for r in o['accepted']) and all(not r['constituent_relation_created'] for r in o['crosswalk'])
    g['NO_NEW_MOTHER'] = not o['representation']['mothers'] and all(r['mother_if_hypotactic'] == 'NONE' for r in rr)
    g['RESUMPTION_NOT_ADJUDICATED'] = all(r['RESUMPTIVE'] == 'UNREVIEWED_SEPARATE_DIMENSION' and r['resumption_review_status'] in ('DEFERRED_TO_MFR_0_2B', 'NO_H1_RESUMPTION_EVIDENCE') for r in rr)
    g['CLOSURE_NOT_ADJUDICATED'] = all(r['CLOSURE'] == 'UNREVIEWED_SEPARATE_DIMENSION' and r['closure_review_status'] in ('DEFERRED_TO_MFR_0_2C', 'NO_H1_CLOSURE_EVIDENCE') for r in rr)
    ev = {e['evidence_id']: e for a in attachments.values() for e in a['evidence_provenance']}
    g['CESSATION_DERIVED_EVIDENCE_NOT_USED_AS_INDEPENDENT_HIERARCHY_SUPPORT'] = all((r['researcher_decision'] != 'PARATACTIC' or r['independent_hierarchy_support_ids']) and all(e in ev and ev[e]['independent_link_usable'] and not ev[e]['cessation_derived'] and not any(x.startswith('CESSATION:') for x in ev[e]['dependency_root_ids']) for e in r['independent_hierarchy_support_ids']) for r in rr)
    g['HUMAN_DECISIONS_FROZEN_BEFORE_HISTORICAL_LOAD'] = env['events'] == ['HUMAN_DECISIONS_FROZEN', 'HISTORICAL_LOADED'] and env['freeze_valid'] and env['historical_read_guard_valid']
    g['HISTORICAL_RELATIONS_UNCHANGED'] = env['historical_before'] == env['historical_after'] and bool(env['historical_before'])
    for gate, key in [('NO_TREE_ASSEMBLY', 'trees'), ('NO_ROOT', 'roots'), ('NO_R4_4_CONSUMER', 'consumers')]:g[gate] = not o['representation'][key] and (key != 'consumers' or not env['new_consumers'])
    g['RAW_EVIDENCE_MEMBERSHIP_LOSSLESS'] = Counter((r['configuration_case_id'], r['raw_relation_id']) for r in o['crosswalk']) == Counter((h['configuration_case_id'], rid) for h in h1 for rid in h['all_configuration_pair_ids'])
    g['RESEARCHER_AUTHORITY_EXACT'] = env['authority_valid'] and all(r['researcher_supplied'] and not r['rewrites_history'] for r in rr)
    return g


def release_gates(regression, same_zip, valid_manifest):
    return dict(FULL_REGRESSION_PASS=regression['tests_run'] > 0 and regression['errors'] == regression['failures'] == 0,
        SKIP_ZERO=regression['skipped'] == 0, MANIFEST_VALID=bool(valid_manifest), DETERMINISTIC_RERUN=bool(same_zip))
