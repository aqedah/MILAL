"""Record supplied human parentage-necessity decisions without changing parentage."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_hsa3_layer_0_1 as l

ROOT, sha, rows, util = l.ROOT, l.sha, l.rows, l.util
CONFIG = ROOT / 'config/hsa3_layer_0_2_job.json'
HISTORY = 'history/hsa3_layer_0_1/'
PROPOSALS = '10_parentage_necessity_audit.csv'
PARENTS = '09_hsa3_unresolved_deferred.csv'
NODES = '01_hsa3_canonical_nodes.csv'
SEAMS = '20_all_seams_preserved.csv'
SCOPE = '14_participant_arc_next_scope.md'
TABLES = {'01_parentage_necessity_human_decisions.csv':'decisions',
          '02_parentage_necessity_proposal_to_decision_crosswalk.csv':'crosswalk',
          '03_parentage_necessity_final_status.csv':'final'}


def require(ok, message):
    if not ok:
        raise ValueError('HSA3-LAYER.0.2 STOP: '+message)


def input_audit(files, cfg, digest, synthetic=False):
    require(util.manifest_ok(files) and all(r['valid'] for r in l.d.h.nested_manifests(files)), 'input manifests')
    require(synthetic or (digest == cfg['archive']['sha256'] and len(files) == cfg['archive']['members']), 'input SHA/count')
    meta = json.loads(files['90_run_metadata.json']); gg = rows(files['17_gates.csv'])
    require(meta['version'] == 'HSA3-LAYER.0.1' and meta['status'] == 'PASS' and meta['r44_started'] is False, 'input stage')
    require(meta['mode'] == ('SYNTHETIC_ONLY' if synthetic else 'FROZEN_REAL_LAYER_INTEGRATION'), 'input mode')
    require(len(gg) == meta['gate_count'] and all(r['status'] == 'PASS' for r in gg), 'input gates')
    pp = rows(files[PROPOSALS]); uu = [r for r in rows(files[PARENTS]) if r['question_kind'] == 'HISTORICAL_DIRECT_PARENT']
    require(dict(Counter(r['proposed_category'] for r in pp)) == cfg['regression']['proposal_categories'], 'proposal categories')
    require(len(pp) == len(uu) == len({r['node_id'] for r in pp}) == cfg['regression']['total'], 'unique proposal coverage')
    require({r['node_id'] for r in pp} == {r['node_id'] for r in uu}, 'historical identity coverage')
    require(all(r['direct_parent'] == 'UNRESOLVED' and r['proposal_status'] == 'UNREVIEWED' and
                r['proposal_kind'] == 'AUDIT_PROPOSAL' and r['human_judgment'] is False and
                r['direct_parent_resolved'] is False and
                all(r[k] == ('UNREVIEWED' if k == 'review_status' else '') for k in l.REVIEW_FIELDS) for r in pp), 'historical proposal states')
    require(all(r['status'] == r['original_record']['direct_parent'] == 'UNRESOLVED' for r in uu), 'historical unresolved states')
    by_id = {r['node_id']:r for r in uu}
    require(all(r['original_unresolved_record'] == by_id[r['node_id']]['original_record'] for r in pp), 'historical row identity')
    special = [r for r in pp if r['proposed_category'] == l.P7]
    require(len(special) == 1 and special[0]['node_id'] == cfg['regression']['special_node'] and
            special[0]['reference'] == cfg['regression']['special_reference'], 'P7 explicit human scope')
    ss = rows(files[SEAMS])
    require([r['seam_id'] for r in ss] == ['SEAM_'+x for x in 'ABCDEFG'] and all(r['status'] == 'FROZEN' for r in ss), 'seam states')
    return dict(sha256=digest, members=len(files), synthetic=synthetic, manifests=l.d.h.nested_manifests(files))


def load(self_test=False, archive=None):
    require(not (self_test and archive), 'synthetic cannot consume a real archive')
    cfg = json.loads(CONFIG.read_bytes()); commit = l.d.baseline_receipt(cfg)
    frozen = l.d.h.f.a.prep.r43.frozen_receipts(cfg)
    require(all(r['actual'] == r['expected'] for r in frozen), 'frozen repository pins')
    request = (ROOT/cfg['source_request']['path']).read_bytes()
    human_bytes = (ROOT/cfg['human_decisions']['path']).read_bytes()
    require(sha(request) == cfg['source_request']['sha256'], 'request hash')
    require(sha(human_bytes) == cfg['human_decisions']['sha256'], 'human authority hash')
    human = json.loads(human_bytes)
    require(human['version'] == cfg['version'] and human['authority'] == 'EXPLICIT_RESEARCHER_DECISION' and
            human['source_request_sha256'] == sha(request), 'human authority')
    require(set(human['category_decisions']) == set(cfg['regression']['proposal_categories']), 'human category scope')
    if self_test:
        ps = l.load(True); files = l.serialize(l.build(ps), ps); digest = sha(files['99_manifest_sha256.csv'])
    else:
        data = (Path(archive) if archive else ROOT/cfg['archive']['path']).read_bytes(); digest = sha(data)
        require(digest == cfg['archive']['sha256'], 'input ZIP hash')
        files = l.d.h.f.a.prep.r43.h1.src.archive(data, digest, mr1=True)['files']
    return dict(cfg=cfg, commit=commit, frozen=frozen, request=request, human_bytes=human_bytes, human=human,
                files=files, receipt=input_audit(files,cfg,digest,self_test),
                mode='SYNTHETIC_ONLY' if self_test else 'FROZEN_REAL_NECESSITY_HUMAN_FREEZE')


def source_link(s, ident):
    matches = [(i,r) for i,r in enumerate(l.d.h.raw_rows(s['files'][PROPOSALS]),1) if r['node_id'] == ident]
    require(len(matches) == 1, 'exact proposal identity '+ident)
    i,r = matches[0]
    # The upstream table has no proposal_id. This names its existing composite
    # identity, rather than claiming a historical ID field or matching by text.
    return dict(source_proposal_id='HSA3-LAYER.0.1::'+PROPOSALS+'::node_id='+ident,
                source_member=HISTORY+PROPOSALS, source_data_row=i, source_identity_field='node_id',
                source_identity=ident, source_row_sha256=l.d.h.f.rowhash(r),
                source_member_sha256=sha(s['files'][PROPOSALS]), source_artifact_sha256=s['receipt']['sha256'])


def decisions(s):
    result = []
    for p in rows(s['files'][PROPOSALS]):
        cat = p['proposed_category']; human = s['human']['category_decisions'][cat]
        require(human['researcher_decision'] == 'ACCEPT' and human['additional_parentage_review_required'] is False, 'unapproved necessity decision')
        result.append(dict(decision_id='LAYER02:NECESSITY:'+p['node_id'], node_id=p['node_id'], reference=p['reference'],
            proposal_category=cat, proposal_status=p['proposal_status'], proposal_kind=p['proposal_kind'],
            **deepcopy(human), necessity_human_status=human['researcher_necessity_status'],
            human_status='FROZEN', authority='EXPLICIT_RESEARCHER_DECISION',
            historical_direct_parent=p['direct_parent'], direct_parent_edge_resolved=False, assigned_parent_ids=[],
            criteria=dict(source_rule=p['necessity_rule'], existing_relation_ids=p['all_existing_relation_ids'],
                          scope='REPRESENTATION_NECESSITY_ONLY; NOT_EDGE_DISCOVERY',
                          human_decision_json_pointer='/category_decisions/'+cat),
            original_proposal=deepcopy(p), **source_link(s,p['node_id']),
            source_request_sha256=sha(s['request']), human_decisions_sha256=sha(s['human_bytes'])))
    return result


def crosswalk(dd):
    keys = ['decision_id','node_id','proposal_category','proposal_status','researcher_decision','researcher_necessity_status',
            'source_proposal_id','source_member','source_data_row','source_identity_field','source_identity',
            'source_row_sha256','source_member_sha256','source_artifact_sha256','source_request_sha256','human_decisions_sha256']
    return [{k:r[k] for k in keys} for r in dd]


def final_status(dd):
    keys = ['decision_id','node_id','reference','proposal_category','proposal_status','historical_direct_parent',
            'researcher_necessity_status','necessity_human_status','additional_parentage_review_required',
            'direct_parent_edge_resolved','assigned_parent_ids','human_status','source_proposal_id','source_artifact_sha256']
    return [{k:deepcopy(r[k]) for k in keys} for r in dd]


def counts(m):
    return dict(historical_unresolved_parent_rows=sum(r['question_kind'] == 'HISTORICAL_DIRECT_PARENT' and r['status'] == 'UNRESOLVED' for r in m['unresolved']),
        proposal_categories=dict(Counter(r['proposal_category'] for r in m['decisions'])),
        human_necessity_statuses=dict(Counter(r['researcher_necessity_status'] for r in m['decisions'])),
        PARENTAGE_NECESSITY_REVIEW_COMPLETED=sum(r['human_status'] == 'FROZEN' and r['researcher_decision'] == 'ACCEPT' for r in m['decisions']),
        active_future_direct_parent_questions=sum(r['additional_parentage_review_required'] is not False for r in m['decisions']),
        DIRECT_PARENT_EDGE_RESOLVED=sum(r['direct_parent_edge_resolved'] is not False or bool(r['assigned_parent_ids']) for r in m['decisions']),
        new_structural_relations=len(m['new_structural_relations']), new_composition_relations=len(m['new_composition_relations']))


def reports(m,s):
    ident = s['cfg']['regression']['special_node']; rr = [r for r in m['decisions'] if r['node_id'] == ident]
    r = rr[0] if len(rr) == 1 else {}; nn = [r for r in m['nodes'] if r['node_id'] == ident]
    special = '\n'.join(['# Job 2:11 — parentage necessity human record','',
        'Node: '+ident+'; historical direct parent: '+str(r.get('historical_direct_parent','MISSING')),
        'Human necessity: '+str(r.get('researcher_necessity_status','MISSING')),
        'Additional parentage review required: '+str(r.get('additional_parentage_review_required','MISSING')),
        'PARAGRAPH_ONSET and FRIENDS_ARRIVAL / PARTICIPANT_INTRODUCTION remain textual.',
        'NOT_WITHIN_SECOND_TESTING_SCENE and OPENING_NARRATIVE_COMPLEX membership are preserved.',
        'No new CHILD_OF relation or parent at 1:1, 2:1, 3:1 or any other node is assigned. This does not assert NO_PARENT.',
        '', '## Researcher rationale','',r.get('rationale','MISSING'),'',
        '## Existing source-grounded node and decision provenance','', '```json',
        json.dumps(dict(node=nn,proposal=source_link(s,ident)),ensure_ascii=False,indent=2),'```'])
    summary = '\n'.join(['# HSA3 layered completion — human necessity freeze','',
        'The original 57 R4.3 parent fields remain historically UNRESOLVED.',
        'After layered review, none of these 57 requires further direct textual-parent adjudication for the current MILAL representation.',
        '57 parentage-necessity questions reviewed is not 57 parentages resolved. No new parent edge is assigned.',
        'MILAL terminates this parentage review without constructing a complete one-parent tree.',
        'Job 2:11 remains a textual paragraph onset and participant-introduction unit, without requiring an exact direct textual parent.',
        'TEXTUAL_HIERARCHY, TEXTUAL_SAME_LEVEL, COMPOSITION_GROUPING, TRANSITION, OVERLAY_RESPONSIO, NEGATIVE_CONSTRAINT and UNRESOLVED/DEFERRED remain independent.',
        'NO DIRECT TEXTUAL PARENT ≠ STRUCTURAL INFORMATION MISSING.',
        'Historical direct_parent = UNRESOLVED does not entail mandatory future adjudication.',
        'A–G remain FROZEN. ANA-Q2/Q4/Q5 remain accepted; ANA-Q3 remains UNRESOLVED/HUMAN_DEFERRED.',
        'The upstream proposals retain UNREVIEWED and their original P2–P7 categories. Separate FROZEN human records carry the supplied necessity judgments.',
        'Historical later_human_review_required fields remain historical assertions, not the new active review queue.',
        '', '```json',json.dumps(counts(m),ensure_ascii=False,indent=2),'```','',
        '[Human decisions](01_parentage_necessity_human_decisions.csv); [exact crosswalk](02_parentage_necessity_proposal_to_decision_crosswalk.csv); [final necessity status](03_parentage_necessity_final_status.csv).',
        '[Unchanged layered matrix]('+HISTORY+'12_hsa3_complete_layered_matrix.csv); [historical proposals]('+HISTORY+PROPOSALS+').'])
    readiness = '\n'.join(['# R4.4 readiness update','',
        'PARENTAGE_NECESSITY_REVIEW_COMPLETE', 'R4_4_CONTRACT_REVIEW_STILL_REQUIRED', 'R4.4 implementation: NOT STARTED.',
        'A future, separately authorized contract must accept partial textual hierarchy, same-level textual relations, composition graph, transition graph, overlays, negative constraints, historical unresolved states and human direct-parent-not-required necessity status.',
        'Preserve exact identities, provenance, typed relations and technical navigation separately. No synthetic/default parent may be generated.',
        'This is readiness documentation, not an implemented or validated R4.4 consumer. Participant arc remains NEXT_RESEARCH_SCOPE / UNADJUDICATED.'])
    return {'04_job_2_11_parentage_necessity_record.md':special.encode(),
            '05_hsa3_layered_completion_summary.md':summary.encode(),
            '06_remaining_research_scope.md':s['files'][SCOPE], '07_r4_4_readiness_update.md':readiness.encode()}


def derive(s):
    dd = decisions(s)
    m = dict(decisions=dd,crosswalk=crosswalk(dd),final=final_status(dd),historical=deepcopy(s['files']),
             nodes=deepcopy(rows(s['files'][NODES])),unresolved=deepcopy(rows(s['files'][PARENTS])),
             commit=deepcopy(s['commit']),receipt=deepcopy(s['receipt']),
             new_structural_relations=[],new_composition_relations=[],participant_frames=[],r44_started=False)
    m['reports'] = reports(m,s)
    return m


def digest(m):
    return l.d.h.f.rowhash({k:({n:sha(b) for n,b in v.items()} if k in ('historical','reports') else v)
                          for k,v in m.items() if k != 'rerun_digest'})


def build(s):
    m = derive(s); m['rerun_digest'] = digest(derive(s)); return m


def gates(m,s):
    expected = decisions(s); cc = counts(m); cfg = s['cfg']; total = cfg['regression']['total']
    unchanged = lambda n: m['historical'].get(n) == s['files'][n]
    special = [r for r in m['decisions'] if r['node_id'] == cfg['regression']['special_node']]
    sr = special[0] if len(special) == 1 else {}
    check = {}
    check['BASELINE_COMMIT_EXACT'] = m['commit'] == s['commit'] and m['commit']['verified_commit'] == cfg['baseline_commit'] and m['commit']['is_ancestor'] is True
    check['UPSTREAM_VERIFIED'] = m['receipt'] == s['receipt'] and unchanged('90_run_metadata.json') and unchanged('17_gates.csv')
    check['HISTORICAL_57_PRESERVED'] = m['unresolved'] == rows(s['files'][PARENTS]) and unchanged(PARENTS) and unchanged(l.HISTORY+l.UNRESOLVED)
    check['PROPOSAL_CATEGORIES_PRESERVED'] = [(r['node_id'],r['proposal_category'],r['proposal_status'],r['original_proposal']) for r in m['decisions']] == [(r['node_id'],r['proposal_category'],r['proposal_status'],r['original_proposal']) for r in expected] and unchanged(PROPOSALS)
    for cat,n in cfg['regression']['proposal_categories'].items():
        check[cat[:2]+'_COUNT'] = cc['proposal_categories'].get(cat,0) == n
    check['JOB_2_11_IDENTITY'] = sr.get('reference') == cfg['regression']['special_reference'] and [r for r in m['nodes'] if r['node_id'] == cfg['regression']['special_node']] == [r for r in rows(s['files'][NODES]) if r['node_id'] == cfg['regression']['special_node']]
    check['JOB_2_11_HISTORICAL_UNRESOLVED'] = sr.get('historical_direct_parent') == 'UNRESOLVED'
    check['JOB_2_11_HUMAN_NECESSITY'] = sr.get('researcher_necessity_status') == 'DIRECT_TEXTUAL_PARENT_NOT_REQUIRED' and sr.get('additional_parentage_review_required') is False
    check['NO_JOB_2_11_PARENT'] = sr.get('assigned_parent_ids') == [] and sr.get('direct_parent_edge_resolved') is False and m['new_structural_relations'] == [] and unchanged('02_hsa3_textual_hierarchy_edges.csv')
    check['ALL_57_REVIEWED'] = cc['PARENTAGE_NECESSITY_REVIEW_COMPLETED'] == total and len(m['decisions']) == len({r['node_id'] for r in m['decisions']}) == total
    check['ACTIVE_FUTURE_QUESTIONS_ZERO'] = cc['active_future_direct_parent_questions'] == 0 and len(m['decisions']) == total
    check['HISTORICAL_UNRESOLVED_COUNT_57'] = cc['historical_unresolved_parent_rows'] == total
    check['NEW_PARENT_EDGES_ZERO'] = cc['DIRECT_PARENT_EDGE_RESOLVED'] == 0 and all(r['historical_direct_parent'] == 'UNRESOLVED' for r in m['decisions'])
    check['NO_TREE_OR_DEFAULT_PARENT_SYNTHESIS'] = m['nodes'] == rows(s['files'][NODES]) and all(r['assigned_parent_ids'] == [] for r in m['decisions']) and m['new_structural_relations'] == []
    check['NON_TEXTUAL_GROUPS_PRESERVED'] = unchanged('04_hsa3_composition_groups.csv') and [r for r in m['nodes'] if r['node_kind'] == 'COMPOSITION_GROUP'] == [r for r in rows(s['files'][NODES]) if r['node_kind'] == 'COMPOSITION_GROUP']
    check['ROLE_ALIASES_AND_CANONICAL_SPEECH_PRESERVED'] = unchanged('19_role_alias_crosswalk.csv') and m['nodes'] == rows(s['files'][NODES])
    check['LOCAL_RELATIONS_PRESERVED'] = unchanged('02_hsa3_textual_hierarchy_edges.csv') and unchanged('08_hsa3_negative_constraints.csv')
    check['CONTAINER_RELATIONS_PRESERVED'] = unchanged('05_hsa3_composition_relations.csv') and unchanged('03_hsa3_textual_same_level_edges.csv') and m['new_composition_relations'] == []
    check['GLOBAL_SEAMS_FROZEN'] = unchanged(SEAMS) and all(r['status'] == 'FROZEN' for r in rows(m['historical'][SEAMS]))
    check['ANA_PRESERVED_Q3_DEFERRED'] = unchanged('07_hsa3_overlay_relations.csv') and unchanged('06_hsa3_transition_relations.csv') and unchanged(l.HISTORY+l.ANA) and [r for r in m['unresolved'] if r['question_id'] == 'ANA-Q3'] == [r for r in rows(s['files'][PARENTS]) if r['question_id'] == 'ANA-Q3']
    check['PARTICIPANT_ARC_UNADJUDICATED'] = m['participant_frames'] == [] and m['reports']['06_remaining_research_scope.md'] == s['files'][SCOPE] and unchanged(SCOPE)
    check['NO_42_10_PROMOTION'] = m['nodes'] == rows(s['files'][NODES]) and m['new_structural_relations'] == []
    check['R4_4_NOT_STARTED'] = m['r44_started'] is False and m['reports']['07_r4_4_readiness_update.md'] == reports(m,s)['07_r4_4_readiness_update.md']
    check['ALL_HUMAN_DECISIONS_AUTHORIZED'] = m['decisions'] == expected
    check['CROSSWALK_EXACT'] = m['crosswalk'] == crosswalk(expected)
    check['FINAL_STATUS_EXACT'] = m['final'] == final_status(expected)
    check['HISTORICAL_ARTIFACTS_UNCHANGED'] = m['historical'] == s['files']
    check['ALL_RELATION_DIMENSIONS_PRESERVED'] = all(unchanged(n) for n in l.LAYERS) and not m['new_structural_relations'] and not m['new_composition_relations']
    check['REPORTS_FAITHFUL'] = m['reports'] == reports(m,s)
    check['FROZEN_REPOSITORY_PINS'] = len(s['frozen']) == len(cfg['frozen_files']) and all(r['actual'] == r['expected'] == cfg['frozen_files'][r['path']] for r in s['frozen'])
    check['RESEARCHER_AUTHORITY_EXACT'] = sha(s['request']) == cfg['source_request']['sha256'] and sha(s['human_bytes']) == cfg['human_decisions']['sha256'] and s['human'] == json.loads(s['human_bytes'])
    check['DETERMINISTIC_PAYLOAD'] = m['rerun_digest'] == digest(m)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in check.items()]


def serialize(m,s):
    gg = gates(m,s); require(all(r['status'] == 'PASS' for r in gg), str([r for r in gg if r['status'] != 'PASS']))
    files = {HISTORY+n:b for n,b in m['historical'].items()}
    for n,k in TABLES.items(): files[n] = util.csv_bytes(m[k])
    files.update(m['reports']); files['09_researcher_source.txt'] = s['request']; files['10_human_decisions.json'] = s['human_bytes']
    files['90_run_metadata.json'] = util.json_bytes(dict(version='HSA3-LAYER.0.2',status='PASS',mode=s['mode'],gate_count=len(gg)+1,
        counts=counts(m),baseline_commit=m['commit'],input_receipt=m['receipt'],frozen_receipts=s['frozen'],
        config_sha256=sha(CONFIG.read_bytes()),code_sha256=sha(Path(__file__).read_bytes()),
        request_sha256=sha(s['request']),human_decisions_sha256=sha(s['human_bytes']),rerun_payload_sha256=m['rerun_digest'],
        r44_started=False,claim='57_NECESSITY_REVIEWS; ZERO_NEW_PARENT_EDGES',
        release_checks='Full regression skip=0 and independent ZIP equality are externally verified in the validation report.'))
    l.f.seal(files); gg.append(dict(gate='MANIFEST_VALID',status='PASS' if util.manifest_ok(files) else 'FAIL'))
    files['08_gates.csv'] = util.csv_bytes(gg); l.f.seal(files)
    require(util.manifest_ok(files), 'output manifest'); return files


def release_gates(test_result, first_zip, second_zip):
    """External release checks: never claim a test-suite pass from a stage exit."""
    ok = test_result['tests_run'] > 0 and test_result['successful'] is True and all(test_result[k] == 0 for k in ('failures','errors','skipped'))
    return [dict(gate='FULL_REGRESSION_PASS_SKIP_ZERO',status='PASS' if ok else 'FAIL'),
            dict(gate='INDEPENDENT_ZIP_BYTE_IDENTICAL',status='PASS' if first_zip and first_zip == second_zip else 'FAIL')]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--self-test',action='store_true'); ap.add_argument('--archive'); ap.add_argument('--out',required=True)
    args = ap.parse_args(argv); s = load(args.self_test,args.archive); files = serialize(build(s),s)
    require(l.d.h.f.a.prep.r43.frozen_receipts(s['cfg']) == s['frozen'], 'frozen sources changed during run')
    require((ROOT/s['cfg']['source_request']['path']).read_bytes() == s['request'], 'request changed during run')
    require((ROOT/s['cfg']['human_decisions']['path']).read_bytes() == s['human_bytes'], 'human decisions changed during run')
    if not args.self_test:
        require(sha((Path(args.archive) if args.archive else ROOT/s['cfg']['archive']['path']).read_bytes()) == s['receipt']['sha256'], 'input changed during run')
    l.d.h.f.a.prep.publish(files,args.out); out = Path(args.out).resolve(); zp = out.with_name(out.name+'_results.zip')
    receipt = 'HSA3-LAYER.0.2 PASS\n'+s['mode']+'\nZIP SHA256 '+sha(zp.read_bytes())+'\n'
    out.with_name(out.name+'_run.log').write_text(receipt,encoding='utf-8'); print(receipt); return 0


if __name__ == '__main__':
    try: sys.exit(main())
    except (ValueError,KeyError,OSError) as exc: print(str(exc),file=sys.stderr); sys.exit(2)
