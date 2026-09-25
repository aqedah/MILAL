"""Additive H0 review sieve over an immutable MFR.0.2R result package."""
import argparse
from collections import Counter, defaultdict
from contextlib import ExitStack
import hashlib
import itertools
import json
from pathlib import Path
import statistics
import subprocess
import sys

from milal_mfr02r_data import rows, table, Table, encode, digest, manifest, verify_manifest, pack, physical_path
from milal_mfr02r_io import verify_archive
from milal_review_eligibility import classify, target_status, relation_types, CLASSES
from milal_relation_competition import sets, impacts
from milal_review_packet import write_target, historical_packet, blank_fields, HUMAN_FIELDS

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config/mfr_0_2r_h0_job.json'
PAIR_TABLE = 'blind/job/09_candidate_evidence_matrix.csv'


def hash_row(row):
    return hashlib.sha256(encode(row).encode('utf8')).hexdigest()


def load_config():
    return json.loads(CONFIG.read_text(encoding='utf8'))


def frozen_check(config):
    head = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    subprocess.run(['git','merge-base','--is-ancestor',config['baseline'],head], cwd=ROOT, check=True)
    mismatches = [p for p,h in config['frozen_files'].items() if digest(ROOT/p) != h]
    if mismatches:
        raise ValueError('frozen source modified: ' + repr(mismatches))
    return dict(baseline=config['baseline'], files=len(config['frozen_files']), differences=mismatches)


def source_context(source):
    job = Path(source)/'blind/job'
    inventory = {int(r['clause_id']):r for r in rows(job/'02_clause_feature_inventory.csv')}
    registry = {r['rule_id']:r for r in rows(job/'01_relation_grammar_registry.csv')}
    compatibility = {r['edge_id']:r for r in rows(job/'14_global_compatibility_matrix.csv')}
    components, target_components = defaultdict(list), defaultdict(list)
    for r in rows(job/'15_variant_components.csv'):
        for edge in r['alternative_edge_ids']:
            components[edge.rsplit('-',1)[0]].append(r['component_id'])
        for tid in r['affected_clauses']:
            target_components[int(tid)].append(r['component_id'])
    conflicts, conflict_rows = defaultdict(list), {}
    for r in rows(job/'13_global_relation_conflicts.csv'):
        conflict_rows[r['conflict_id']] = r
        for edge in r['edge_ids']:
            conflicts[edge.rsplit('-',1)[0]].append(r['conflict_id'])
    constructions = {int(r['clause_id']):r for r in rows(job/'construction_inventory.csv')}
    analogues = {r['construction_id']:r for r in rows(Path(source)/'corpus_search/01_job_hb_analogues.csv')}
    bindings = list(rows(job/'clause_internal_binding_candidates.csv'))
    deferred = list(rows(job/'clause_binding_revalidation.csv'))
    binding_targets = defaultdict(list)
    for r in bindings:
        tid = int(r['binding_evidence']['raw_clause_membership'])
        if tid not in inventory:
            raise ValueError('binding clause identity missing')
        binding_targets[tid].append(r['binding_id'])
    return dict(inventory=inventory, registry=registry, compatibility=compatibility, components=components,
                target_components=target_components, conflicts=conflicts, conflict_rows=conflict_rows,
                constructions=constructions, analogues=analogues, bindings=bindings, deferred=deferred, binding_targets=binding_targets)


def pair_context(row, poetic, ctx):
    pair = row['pair_id']; families = defaultdict(set)
    for rid in row['rule_ids_matched']:
        rule = ctx['registry'][rid]
        families[rule['source_author']].add(rule['candidate_relation'])
    different = len(families) > 1 and len(set().union(*families.values())) > 1
    return dict(source_family_conflict=different, conflict_ids=sorted(set(ctx['conflicts'].get(pair, []))),
                component_ids=sorted(set(ctx['components'].get(pair, []))),
                poetry_exception=poetic.get('exception_status',''), poetic_labels=poetic.get('labels',[]))


def current_summary(source, ctx):
    """No human or control data loaded. Pair contexts are exact existing edges."""
    result = defaultdict(lambda: dict(relation_ids=[], hyp=[], para=[]))
    for row in rows(Path(source)/'blind/job/10_relation_candidates.csv'):
        if row['relations']:
            r=result[int(row['target_clause_id'])]; r['relation_ids'].append(row['pair_id'])
            if 'HYPOTACTIC' in row['relations']: r['hyp'].append(row['pair_id'])
            if 'PARATACTIC' in row['relations']: r['para'].append(row['pair_id'])
    return result


def eligibility_pass(source, out, ctx, page_size):
    """Freeze current-evidence classifications before reading historical decisions."""
    source, out = Path(source), Path(out)
    summary = current_summary(source, ctx)
    source_sha = digest(physical_path(source/PAIR_TABLE))
    crossfields = ['candidate_id','target_id','source_candidate_id','existing_candidate_relation','existing_rule_ids',
        'existing_evidence','review_eligibility','review_reason_codes','relations','component_ids','conflict_ids','distance']
    target_rows, presentations, competitions, mothers, parallels, archives = [], [], [], [], [], []
    total = Counter(); seen_targets = set(); poetry_queue=[]
    poetry = iter(rows(source/'blind/job/poetic_prosodic_evidence.csv'))
    with ExitStack() as stack:
        cross = stack.enter_context(Table(out/'01_h0_candidate_review_eligibility.csv', crossfields))
        disagreement = stack.enter_context(Table(out/'06_h0_relation_disagreement_matrix.csv',
            ['candidate_id','JIN','WALTON','BOSMAN','OOSTING','MILAL_EXTENSION']))
        impact = stack.enter_context(Table(out/'07_h0_global_impact.csv',['candidate_id','global_impact','structural_flags']))
        for tid, group in itertools.groupby(rows(source/PAIR_TABLE), key=lambda r:int(r['target_clause_id'])):
            if tid in seen_targets: raise ValueError('source target groups not contiguous')
            seen_targets.add(tid); entries=[]; cards=[]; counts=Counter(); pair_ids=set()
            for original in group:
                p=next(poetry)
                if (int(p['source_clause_id']),int(p['target_clause_id'])) != (int(original['candidate_clause_id']),tid):
                    raise ValueError('poetry/source exact pair mismatch')
                pid=original['pair_id']
                if pid in pair_ids: raise ValueError('duplicate source candidate ID')
                pair_ids.add(pid)
                pc=pair_context(original,p,ctx); chosen=classify(original,pc)
                if len(summary[tid]['hyp'])>1 and 'HYPOTACTIC' in relation_types(original['candidate_relations']):
                    chosen['review_reason_codes']=sorted(set(chosen['review_reason_codes'])|{'MOTHER_COMPETITION'})
                ref=dict(table=PAIR_TABLE+'.gz' if physical_path(source/PAIR_TABLE).suffix=='.gz' else PAIR_TABLE,
                         table_sha256=source_sha, pair_id=pid, canonical_row_sha256=hash_row(original))
                r=dict(candidate_id=pid,target_id=tid,source_candidate_id=int(original['candidate_clause_id']),
                    existing_candidate_relation=original['candidate_relations'],existing_rule_ids=original['rule_ids_matched'],
                    existing_evidence=ref,**chosen,relations=relation_types(original['candidate_relations']),
                    component_ids=pc['component_ids'],conflict_ids=pc['conflict_ids'],distance=int(original['distance_clauses']))
                cross.write(r); counts[r['review_eligibility']]+=1; total[r['review_eligibility']]+=1
                contribution={family:[rid for rid in original['rule_ids_matched'] if ctx['registry'][rid]['source_author']==family]
                              for family in ('JIN','WALTON')}
                disagreement.write(dict(candidate_id=pid,**contribution,
                    BOSMAN=dict(table='blind/job/poetic_prosodic_evidence.csv.gz',pair_id=pid,labels=p['labels'],relation_claim='EVIDENCE_NOT_FORCED_GRAMMAR'),
                    OOSTING=dict(table='blind/job/construction_inventory.csv.gz',source=r['source_candidate_id'],target=tid,relation_claim='CONSTRUCTION_EVIDENCE'),
                    MILAL_EXTENSION=dict(table=ref['table'],pair_id=pid,schema='EXECUTABLE_EVIDENCE_SCHEMA_NOT_NEW_RELATION')))
                effects=impacts(r,len(summary[tid]['hyp']))
                # A dimension is flagged only where a matched rule actually cites it.
                cited={x for rid in original['rule_ids_matched'] for group in ctx['registry'][rid]['required_features'] for x in group if original['facts'].get(x)}
                flags=[]
                if len(summary[tid]['relation_ids'])>1:
                    for dimension,prefixes in [('TIME',('time_','temporal_')),('PARTICIPANT',('participant_','continued_secondary_participant')),('REFERENCE',('reference_','anaphoric_','antecedent_','embedded_reference'))]:
                        if any(x.startswith(prefixes) for x in cited): flags.append(dimension+'_STRUCTURAL_COMPETITION')
                impact.write(dict(candidate_id=pid,global_impact=effects,structural_flags=flags))
                if pc['poetry_exception']:
                    poetry_queue.append(dict(candidate_id=pid,target_id=tid,original_poetic_record=p,review_status='UNREVIEWED',resolution=''))
                entries.append(r)
                if r['review_eligibility'] in CLASSES[:2]:
                    sid=r['source_candidate_id']
                    detail={k:original.get(k,{}) for k in ('TIME','LOCATION','PARTICIPANT','REFERENCE','DOMAIN','LEXICAL')}
                    detail.update(FORM={k:original[k] for k in ('GRAPHEME','WORD','PHRASE','CLAUSE')},
                        SOURCE_TARGET_OBSERVATIONS={str(n):{k:ctx['inventory'][n][k] for k in ('TIME','LOCATION','PARTICIPANT','REFERENCE','DOMAIN','LEXICAL')} for n in (sid,tid)},
                        CONSTRUCTION_SIGNATURE={str(n):ctx['constructions'][n]['exact_construction_signature'] for n in (sid,tid)},
                        VALENCY={str(n):ctx['constructions'][n]['valency_signature'] for n in (sid,tid)},
                        CORPUS_ANALOGUE={str(n):ctx['analogues'][ctx['constructions'][n]['construction_id']] for n in (sid,tid)},
                        POETIC_PROSODIC=p)
                    cards.append(dict(r,source_contributions=contribution,detail=detail,global_impact=effects,
                        compatibility=[ctx['compatibility'][pid+'-'+suffix] for suffix in ('H','P') if pid+'-'+suffix in ctx['compatibility']]))
            cc={k:counts[k] for k in CLASSES}
            presentation=write_target(out,tid,ctx['inventory'],cards,cc,page_size);presentations.append(presentation)
            ts=target_status(entries,dict(binding_ids=ctx['binding_targets'].get(tid,[]),component_ids=ctx['target_components'].get(tid,[])))
            target_rows.append(dict(target_id=tid,**ts,class_counts=cc,raw_candidate_count=len(entries),
                relation_candidate_ids=[r['candidate_id'] for r in entries if r['review_eligibility']==CLASSES[0]],
                configuration_candidate_ids=[r['candidate_id'] for r in entries if r['review_eligibility']==CLASSES[1]],
                eligible_candidate_ids=[r['candidate_id'] for r in entries if r['review_eligibility'] in CLASSES[:2]],packet=presentation['packet']))
            c,m,pa=sets(tid,entries);competitions.append(c);mothers.append(m);parallels.append(pa)
            archives.append(dict(target_id=tid,evidence_only_count=counts['EVIDENCE_ONLY'],insufficient_count=counts['INSUFFICIENT'],lookup_table='01_h0_candidate_review_eligibility.csv'))
    if next(poetry,None) is not None: raise ValueError('unused poetry rows')
    for tid in ctx['inventory'].keys()-seen_targets:
        cc={k:0 for k in CLASSES};presentation=write_target(out,tid,ctx['inventory'],[],cc,page_size);presentations.append(presentation)
        ts=target_status([],dict(binding_ids=ctx['binding_targets'].get(tid,[]),component_ids=ctx['target_components'].get(tid,[])))
        target_rows.append(dict(target_id=tid,**ts,class_counts=cc,raw_candidate_count=0,relation_candidate_ids=[],configuration_candidate_ids=[],eligible_candidate_ids=[],packet=presentation['packet']))
        c,m,pa=sets(tid,[]);competitions.append(c);mothers.append(m);parallels.append(pa)
        archives.append(dict(target_id=tid,evidence_only_count=0,insufficient_count=0,lookup_table='01_h0_candidate_review_eligibility.csv'))
    for filename,records in [('03_h0_relation_competition_sets.csv',competitions),('04_h0_mother_candidate_sets.csv',mothers),
        ('05_h0_parallel_candidate_sets.csv',parallels),('09_h0_poetry_syntax_conflict_review.csv',poetry_queue),
        ('16_h0_archive_summary.csv',archives),('display_card_manifest.csv',presentations)]:
        table(out/filename,sorted(records,key=lambda r:(int(r.get('target_id',0)),r.get('candidate_id',''))))
    deferred_by_id={r['clause_binding_issue']:r for r in ctx['deferred']}
    table(out/'08_h0_valency_binding_review.csv', [dict(binding_id=r['binding_id'],target_id=r['binding_evidence']['raw_clause_membership'],
        raw_atoms=[r['clause_atom_a'],r['clause_atom_b']],original_binding=r,original_deferred=deferred_by_id[r['binding_id']],
        scope='ATOM_LEVEL_NOT_AUTOMATIC_CLAUSE_PAIR_PROMOTION',**blank_fields()) for r in ctx['bindings']])
    freeze={p.name:digest(p) for p in out.iterdir() if p.is_file()}
    (out/'eligibility_freeze.json').write_text(encode(freeze)+'\n',encoding='utf8')
    return sorted(target_rows,key=lambda r:r['target_id']), total


def fixture_checks(source):
    result=[]
    for scope in ('pentateuch','qohelet','lamentations','isaiah'):
        path=Path(source)/'controls'/(scope+'_fixture_relation_checks.csv')
        for r in rows(path):
            if not r['relations']: continue
            status='MULTIPLE' if len(r['relations'])>1 else r['relations'][0]
            eligibility=classify(dict(candidate_relations=status,facts=r['facts']),{})
            result.append(dict(scope=scope,pair_id=r['pair_id'],source_relations=r['relations'],**eligibility,
                preserved=eligibility['review_eligibility'] in CLASSES[:2],source_table='controls/'+path.name))
    return result


def metrics(targets,total,config):
    before=[r['raw_candidate_count'] for r in targets];after=[len(r['eligible_candidate_ids']) for r in targets]
    statuses=Counter(r['target_review_status'] for r in targets);tiers=Counter(r['review_tier'] for r in targets)
    required=statuses['TARGET_REVIEW_REQUIRED'];warn=[]
    if targets and required/len(targets)>=config['selectivity_warning_fraction']: warn.append('REVIEW_SIEVE_NOT_SELECTIVE')
    return dict(candidate_universe_total=sum(total.values()),eligibility_counts={k:total.get(k,0) for k in CLASSES},
        human_review_candidate_total=sum(after),candidate_reduction_percentage=100*(1-sum(after)/sum(before)) if sum(before) else 0,
        target_total=len(targets),target_status_counts=dict(statuses),tier_target_counts=dict(tiers),
        median_candidates_before=statistics.median(before),median_candidates_after=statistics.median(after),
        max_candidates_before=max(before,default=0),max_candidates_after=max(after,default=0),warnings=warn,
        diagnostic_warning_fraction=config['selectivity_warning_fraction'],numeric_pass_threshold=None)


def run(source,out,config=None,synthetic=False):
    config=config or load_config(); source=Path(source);out=Path(out)
    if out.exists(): raise ValueError('fresh output directory required')
    if not verify_manifest(source): raise ValueError('upstream manifest invalid')
    ctx=source_context(source)
    if not synthetic and any(r['book']!='Iob' for r in ctx['inventory'].values()): raise ValueError('primary scope is not Job')
    out.mkdir(parents=True)
    table(out/'upstream_manifest.csv',rows(source/'99_manifest_sha256.csv'))
    targets,total=eligibility_pass(source,out,ctx,config['display_cards_per_page'])
    freeze=json.loads((out/'eligibility_freeze.json').read_text())
    if any(digest(out/p)!=h for p,h in freeze.items()): raise ValueError('eligibility changed before historical display')
    # Only now read historical judgments, to mark explicit revalidation scope.
    old=list(rows(source/'mfr02a_original_decisions.csv'))
    lookup={r['target_id']:r for r in targets};tier1={int(t) for r in old for t in r['target_clause_ids']}
    direct=set(tier1)
    for conflict in ctx['conflict_rows'].values():
        edge_targets={int(e.rsplit('-',1)[0].split('-')[1]) for e in conflict['edge_ids']}
        if edge_targets&tier1: direct|=edge_targets
    for r in targets:
        if r['target_id'] in direct:
            r['review_tier']='TIER_1';r['target_review_status']='TARGET_REVIEW_REQUIRED'
            r['review_reason_codes']=sorted(set(r['review_reason_codes'])|{'MFR02A_REVALIDATION'})
    table(out/'02_h0_target_review_eligibility.csv',targets)
    special=historical_packet(out,old,lookup,ctx['inventory'])
    for tier,filename in [('TIER_1','12_h0_tier1_review_cases.csv'),('TIER_2','14_h0_tier2_review_cases.csv'),('TIER_3','15_h0_tier3_review_cases.csv')]:
        table(out/filename,[dict(r,**blank_fields()) for r in targets if r['review_tier']==tier])
    (out/'13_h0_tier1_review_packet.md').write_text('# Tier 1 — Immediate revalidation\n\n[13 configuration cases](11_h0_mfr02a_13_case_packet.md)\n\n'+
        '\n'.join('- [Target %s](%s)'%(r['target_id'],r['packet']) for r in targets if r['review_tier']=='TIER_1')+'\n',encoding='utf8')
    controls=fixture_checks(source);table(out/'18_h0_control_fixture_validation.csv',controls)
    checks=[]
    for chapter,verse in config['job_validation_refs']:
        for tid,inv in ctx['inventory'].items():
            if (int(inv['chapter']),int(inv['verse']))==(chapter,verse):
                checks.append(dict(reference=[chapter,verse],target_id=tid,**{k:lookup[tid][k] for k in ('class_counts','eligible_candidate_ids','packet')}))
    table(out/'job_postfreeze_validation.csv',checks)
    stats=metrics(targets,total,config)
    if any(not r['preserved'] for r in controls): stats['warnings'].append('REVIEW_SIEVE_OVERPRUNED')
    (out/'17_h0_review_reduction_metrics.json').write_text(encode(stats)+'\n',encoding='utf8')
    (out/'19_h0_method_report.md').write_text((ROOT/'docs/MFR_0_2R_H0_SPEC.md').read_text(encoding='utf8'),encoding='utf8')
    (out/'20_h0_next_scope.md').write_text('# Next scope\n\nMFR.0.2R-H, first the 13 provisional cases, requires explicit human authorization.\n\nWarnings: '+encode(stats['warnings'])+'\n',encoding='utf8')
    metadata=dict(stage='MFR.0.2R-H0',mode='SYNTHETIC' if synthetic else 'REAL',analysis_scope='JOB',
        source_manifest_sha256=digest(source/'99_manifest_sha256.csv'),source_archive_sha256=config['input_zip_sha256'],
        historical_decision_hashes={r['decision_id']:hash_row(r) for r in old},new_human_judgments=[],canonical_mothers=[],canonical_hierarchies=[],
        status='AWAITING_VALIDATION',warnings=stats['warnings'],eligibility_precedes_history=True)
    (out/'90_run_metadata.json').write_text(encode(metadata)+'\n',encoding='utf8');manifest(out)
    return stats
