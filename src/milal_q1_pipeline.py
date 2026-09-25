"""Additive, streaming source-binding qualification; frozen engine is not rerun."""
from collections import Counter, defaultdict
from contextlib import ExitStack
from itertools import zip_longest
from pathlib import Path
import json
import shutil

from milal_mfr02r_data import rows, table, Table, encode, digest, physical_path, manifest
from milal_q1_binding import SourceIndex, qualify, identity, outcome, pivot, rule_roles, QUALIFIED, STATUSES, MECHANISMS

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT/'config/mfr_0_2r_q1_job.json'


def write_json(path, data):
    Path(path).write_text(encode(data)+'\n', encoding='utf8', newline='\n')


def run_blind(source, out, grammar):
    source, out = Path(source), Path(out)
    out.mkdir(parents=True, exist_ok=False)
    job = source/'blind/job'
    inventory = list(rows(job/'02_clause_feature_inventory.csv'))
    index = SourceIndex(inventory, grammar['lexicons']['subordinate_rela'], grammar['lexicons']['speech'])
    registry = list(rows(job/'01_relation_grammar_registry.csv'))
    table(out/'01_q1_rule_execution_roles.csv', map(rule_roles, registry))
    by_rule = {r['rule_id']:r for r in registry}
    deferred = {str(r['binding_evidence']['raw_clause_membership']) for r in rows(job/'clause_internal_binding_candidates.csv')}
    members = set()
    for r in rows(job/'15_variant_components.csv'): members.update(map(str, r['affected_clauses']))
    upstream_hash = digest(physical_path(job/'09_candidate_evidence_matrix.csv'))
    outcomes, provenance = {}, defaultdict(list)
    by_target = defaultdict(list)
    counts = Counter({s:0 for s in STATUSES})
    rules_before, rules_after = Counter(), Counter()
    target_counts = defaultdict(Counter)
    active_context = defaultdict(list)
    fields = ['candidate_id','source_id','target_id','search_candidate_status','relation_candidate_qualification',
              'qualification_reason','disqualification_reason','qualified_relations','qualified_paths']
    audit_fields = ['candidate_id','rule_id','original_match','source_bound','qualified_witness_ids','reason']
    binding_fields = ['candidate_id','mechanism','binding_mode','source_id','target_id','evidence',
                      'allowed_relations','identity_status','dependent_on','witness_id',
                      'intervening_context_status','active_participant_context','independent_correspondence_and_same_line']
    streams = [rows(job/(name+'.csv')) for name in ('09_candidate_evidence_matrix', '08_relation_rule_matches')]
    with ExitStack() as stack:
        def output(name, fs): return stack.enter_context(Table(out/name, fs))
        q = output('03_q1_pair_qualification.csv', fields)
        cross = output('02_q1_source_binding_crosswalk.csv', ['candidate_id','source_id','target_id','raw_table_sha256','raw_row_sha256','witnesses'])
        bound = output('source_binding_witnesses.csv', binding_fields)
        walton = output('05_q1_walton_rule_audit.csv', audit_fields)
        jin = output('06_q1_jin_rule_audit.csv', audit_fields)
        qualified = output('07_q1_qualified_relation_universe.csv', fields)
        disqualified = output('08_q1_disqualified_relation_candidates.csv', fields)
        for raw, matchrow in zip_longest(*streams):
            if raw is None or matchrow is None or raw['pair_id'] != matchrow['pair_id']:
                raise ValueError('frozen pair/match streams disagree')
            pair, sid, tid = raw['pair_id'], str(raw['candidate_clause_id']), str(raw['target_clause_id'])
            matches = matchrow['matches']
            witnesses = index.bindings(sid, tid) if matches else []
            result = qualify(sid, tid, matches, witnesses, deferred=tid in deferred)
            record = dict(candidate_id=pair, source_id=sid, target_id=tid,
                search_candidate_status='SEARCH_CANDIDATE', relation_candidate_qualification=result['qualification'],
                **{k:result[k] for k in ('qualification_reason','disqualification_reason','qualified_relations','qualified_paths')})
            q.write(record)
            cross.write(dict(candidate_id=pair, source_id=sid, target_id=tid, raw_table_sha256=upstream_hash,
                raw_row_sha256=identity(raw), witnesses=[w['witness_id'] for w in witnesses]))
            for w in witnesses:
                bound.write(dict(candidate_id=pair, **{k:w.get(k,'') for k in binding_fields if k!='candidate_id'}))
                if w.get('active_participant_context'): active_context[tid].append(w)
            counts[result['qualification']] += 1
            target_counts[tid]['raw'] += 1
            if matches:
                target_counts[tid]['original_relations'] += 1
                counts['original_relations'] += 1
                (qualified if result['qualified_paths'] else disqualified).write(record)
            if result['qualified_paths']:
                counts['qualified'] += 1
                target_counts[tid]['qualified'] += 1
            for m in matches:
                rid = m['rule_id']; rules_before[rid] += 1
                paths = [p for p in result['qualified_paths'] if p['rule_id']==rid]
                if paths: rules_after[rid] += 1
                audit = dict(candidate_id=pair, rule_id=rid, original_match=m,
                    source_bound='YES' if paths else 'NO',
                    qualified_witness_ids=sorted({p['witness_id'] for p in paths}),
                    reason='VERIFIED_PAIR_WITNESS' if paths else result['disqualification_reason'] or 'NO_RULE_SPECIFIC_BINDING')
                (walton if rid.startswith('W-') else jin).write(audit)
            for relation in result['qualified_relations']:
                o = outcome(sid, tid, relation); oid=o['structural_outcome_group_id']
                outcomes[oid] = o
                provenance[oid].extend(dict(candidate_id=pair, **p) for p in result['qualified_paths'] if p['relation']==relation)
            if q.count % 100000 == 0: print('Q1 blind pairs',q.count,flush=True)
    for oid,o in outcomes.items(): by_target[o['target']].append(o)
    table(out/'09_q1_structural_outcomes.csv', [dict(**o, provenance_paths=provenance[oid]) for oid,o in sorted(outcomes.items())],
          ['structural_outcome_group_id','target','relation_type','source_or_peer','mother_if_hypotactic','parallel_peer_if_paratactic','textual_level_effect_candidate','variant_effect','provenance_paths'])
    table(out/'10_q1_structural_outcome_groups.csv', [dict(structural_outcome_group_id=oid,
        candidate_ids=sorted({p['candidate_id'] for p in provenance[oid]}),
        rule_ids=sorted({p['rule_id'] for p in provenance[oid]}), provenance_paths=provenance[oid]) for oid in sorted(outcomes)],
        ['structural_outcome_group_id','candidate_ids','rule_ids','provenance_paths'])
    pivots = [pivot(t,by_target[t],t in members) for t in index.ordered]
    table(out/'11_q1_variant_pivots.csv',pivots)
    for relation,name in [('HYPOTACTIC','12_q1_mother_competition.csv'),('PARATACTIC','13_q1_parallel_competition.csv')]:
        table(out/name, [dict(target_id=t, qualified_alternatives=sorted({o['source_or_peer'] for o in os if o['relation_type']==relation}),
            outcome_group_ids=sorted(o['structural_outcome_group_id'] for o in os if o['relation_type']==relation),
            competition=len({o['source_or_peer'] for o in os if o['relation_type']==relation})>1, accepted='') for t,os in sorted(by_target.items())],
            ['target_id','qualified_alternatives','outcome_group_ids','competition','accepted'])
    contexts=[]
    seen=set()
    for tid in index.ordered:
        r=index.rows[tid]
        lexical={m['lexical_key'] for m in r['PARTICIPANT']['mentions']}
        contexts.append(dict(target_id=tid,
            active_participant_status='CONTINUED' if active_context[tid] else 'HISTORICAL_RECURRENCE_ONLY' if lexical & seen else 'UNRESOLVED',
            source_bound_context_witnesses=active_context[tid], immediate_context_clause_ids=index.ordered[max(0,index.index[tid]-1):index.index[tid]],
            containing_unit_candidate_ids=[u for u in index.ordered if tid in index.units[u]['members'] and u!=tid],
            domain=r['DOMAIN'], unresolved_reference_chain=r['REFERENCE'],
            identity_status='UNRESOLVED', status_basis='SYNTACTICALLY_BOUND_EXPLICIT_MENTION_OR_UNRESOLVED; NO_LEXICAL_IDENTITY_INFERENCE'))
        seen |= lexical
    table(out/'04_q1_active_participant_context.csv',contexts)
    counts['raw']=sum(counts[s] for s in STATUSES)
    counts['outcome_groups']=len(outcomes)
    for n in (0,1,2): counts['targets_'+str(n)+('_plus' if n==2 else '')]=sum((len(by_target[t])>=2 if n==2 else len(by_target[t])==n) for t in index.ordered)
    counts['variant_members']=len(members)
    counts['variant_decision_pivots']=sum(r['status']=='VARIANT_DECISION_PIVOT' for r in pivots)
    counts['variant_member_non_pivots']=sum(r['status']=='VARIANT_MEMBER_NON_PIVOT' for r in pivots)
    for name,key in [('12_q1_mother_competition.csv','mother_competitions'),('13_q1_parallel_competition.csv','parallel_competitions')]:
        counts[key]=sum(r['competition'] is True for r in rows(out/name))
    metrics=dict(counts=counts, rules_before=rules_before, rules_after=rules_after, target_counts=target_counts,
        qualification_policy='NO_SCORE_NO_DISTANCE_CUTOFF_NO_TOP_N', analysis_scope='JOB',
        configuration_coverage='NATIVE_LINKED_REPEATED_CONFIGURATION_SUBSET; OTHER_CONFIGURATIONS_UNRESOLVED',
        unsupported_mechanisms=[k for k in MECHANISMS if k not in ('SB01','SB03','SB04','SB06')])
    write_json(out/'blind_metrics.json',metrics)
    write_json(out/'blind_freeze.json',dict(files={p.name:digest(p) for p in sorted(out.iterdir()) if p.is_file()},
        human_judgments_loaded=False, controls_loaded=False))
    return metrics


def post_freeze(source, h0, out):
    source,h0,out=map(Path,(source,h0,out))
    freeze=json.loads((out/'blind_freeze.json').read_text())
    if any(digest(out/k)!=v for k,v in freeze['files'].items()): raise ValueError('blind freeze changed')
    metrics=json.loads((out/'blind_metrics.json').read_text())
    inventory={str(r['clause_id']):r for r in rows(source/'blind/job/02_clause_feature_inventory.csv')}
    counts=metrics['target_counts']
    outcomes=defaultdict(list)
    for r in rows(out/'09_q1_structural_outcomes.csv'): outcomes[r['target']].append(r)
    pivots={r['target_id']:r for r in rows(out/'11_q1_variant_pivots.csv')}
    h0counts=Counter()
    for r in rows(h0/'01_h0_candidate_review_eligibility.csv'):
        if r['review_eligibility']=='RELATION_ELIGIBLE': h0counts[str(r['target_id'])]+=1
    metrics['h0_relation_eligible']=sum(h0counts.values())
    decisions=list(rows(source/'mfr02a_original_decisions.csv'))
    removed=defaultdict(Counter)
    for name in ('05_q1_walton_rule_audit.csv','06_q1_jin_rule_audit.csv'):
        for r in rows(out/name):
            if r['source_bound']=='NO': removed[r['candidate_id'].rsplit('-',1)[1]][r['rule_id']]+=1
    audits=[]
    for d in decisions:
        targets=list(map(str,d['target_clause_ids']))
        audits.append(dict(decision_id=d['decision_id'], original_decision=d,
            original_decision_sha256=identity(d),
            original_relation_candidates=sum(counts.get(t,{}).get('original_relations',0) for t in targets),
            h0_relation_eligible=sum(h0counts[t] for t in targets),
            q1_qualified_candidates=sum(counts.get(t,{}).get('qualified',0) for t in targets),
            qualified_structural_outcomes=[o for t in targets for o in outcomes[t]],
            pivot_status={t:pivots[t]['status'] for t in targets},
            removed_rule_paths={t:removed[t] for t in targets}, new_human_judgment=''))
    table(out/'14_q1_mfr02a_13_case_reaudit.csv',audits)
    diagnostics=['# Q1 post-freeze Job diagnostics', '',
        'All raw candidate identities are listed below. Full evidence remains in the exact frozen upstream table; Q1 never substitutes similarity for identity.', '']
    special={t for t,r in inventory.items() if (int(r['chapter']),int(r['verse'])) in ((29,1),(1,6),(1,13),(2,1))}
    grouped=defaultdict(list)
    for r in rows(out/'03_q1_pair_qualification.csv'):
        if r['target_id'] in special: grouped[r['target_id']].append(r)
    for t in sorted(special,key=int):
        r=inventory[t]
        diagnostics += [f"## Job {r['chapter']}:{r['verse']} clause {t}",r['surface_hebrew'],
            'Raw candidates: '+encode([q['candidate_id'] for q in grouped[t]]),
            'Counts: '+encode(counts.get(t,{})),
            'Qualified outcomes: '+encode(outcomes[t])]
        for q in grouped[t]:
            s=inventory[q['source_id']]
            if (int(s['chapter']),int(s['verse']))==(27,1):
                diagnostics += ['27:1 comparison: '+encode(dict(pair=q,
                    source_phrase_sequence=s['PHRASE'], target_phrase_sequence=r['PHRASE'],
                    source_participant=s['PARTICIPANT'],target_participant=r['PARTICIPANT'],
                    source_domain=s['DOMAIN'],target_domain=r['DOMAIN'],
                    interpretation='Exact witness details: source_binding_witnesses.csv. Domain or participant recurrence alone is not binding.'))]
    (out/'15_q1_job_special_diagnostics.md').write_text('\n\n'.join(diagnostics)+'\n',encoding='utf8',newline='\n')
    metrics['mfr02a_preserved']=len(audits)
    metrics['warnings']=[]
    if metrics['counts']['targets_2_plus'] > len(inventory)/2: metrics['warnings'].append('QUALIFICATION_STILL_NONSELECTIVE')
    write_json(out/'17_q1_reduction_metrics.json',metrics)
    return metrics
