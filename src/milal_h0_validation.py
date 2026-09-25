"""Computed H0 artifact gates and reproducible validation receipts."""
import ast
from collections import Counter
import itertools
import json
from pathlib import Path
from milal_mfr02r_data import rows, encode, digest, verify_manifest
from milal_mfr02r_h0 import hash_row, PAIR_TABLE, ROOT, load_config, source_context, pair_context, fixture_checks
from milal_review_eligibility import classify, CLASSES
from milal_review_packet import HUMAN_FIELDS

# Each equality compares a measured artifact/input fact, not a success switch.
GATE_FIELDS = {
 'BASELINE_COMMIT_VERIFIED':'baseline', 'MFR_0_2R_FROZEN':'frozen',
 'CANDIDATE_UNIVERSE_ROW_COUNT_UNCHANGED':'counts', 'NO_CANDIDATE_DELETED':'identity',
 'NO_NEW_RELATION_GRAMMAR':'grammar', 'NO_NEW_HUMAN_JUDGMENT':'human',
 'NO_CANONICAL_MOTHER':'mother', 'NO_CANONICAL_HIERARCHY':'hierarchy',
 'REVIEW_ELIGIBILITY_CLASSES_COMPLETE':'classes', 'RELATION_ELIGIBLE_IMPLEMENTED':'relation',
 'CONFIGURATION_ELIGIBLE_IMPLEMENTED':'configuration', 'EVIDENCE_ONLY_IMPLEMENTED':'evidence',
 'INSUFFICIENT_ARCHIVED_NOT_DELETED':'insufficient', 'TARGET_LEVEL_REVIEW_CLASSIFICATION_ACTIVE':'targets',
 'NO_NUMERIC_RANKING':'ranking', 'NO_DISTANCE_CUTOFF':'distance', 'NO_TOP_N_PRUNING':'display',
 'RELATION_COMPETITION_SET_CREATED':'competition', 'MOTHER_CANDIDATE_SET_CREATED':'mother_sets',
 'PARALLEL_CANDIDATE_SET_CREATED':'parallel_sets', 'GLOBAL_IMPACT_CLASSIFICATION_CREATED':'impact',
 'MFR02A_13_ALL_TIER1':'tier1', 'MFR02A_HUMAN_DECISIONS_UNCHANGED':'history',
 'VALENCY_REVIEW_QUEUE_CREATED':'binding', 'POETRY_SYNTAX_REVIEW_QUEUE_CREATED':'poetry',
 'HISTORICAL_JUDGMENT_NO_LEAKAGE':'isolation', 'PENTATEUCH_FULL_ANALYSIS_ABSENT':'scope',
 'CONTROL_FIXTURES_ONLY':'controls', 'HUMAN_PACKET_COMPACT':'compact',
 'RAW_TRACEABILITY_COMPLETE':'trace', 'FULL_REGRESSION_PASS':'regression',
 'SKIP_ZERO':'skips', 'DETERMINISTIC_RERUN':'determinism', 'MANIFEST_VALID':'manifest'}


def evaluate(measurements):
    return [dict(gate=gate,passed=measurements[field]['actual']==measurements[field]['expected'],evidence=measurements[field])
            for gate,field in GATE_FIELDS.items()]


def audit(source,out,config,receipts,determinism=False):
    source,out=Path(source),Path(out);m={}
    def check(name,actual,expected): m[name]=dict(actual=actual,expected=expected)
    ctx=source_context(source); metadata=json.loads((out/'90_run_metadata.json').read_text())
    targets={int(r['target_id']):r for r in rows(out/'02_h0_target_review_eligibility.csv')}
    eligible={tid:[] for tid in targets}; hyp={tid:[] for tid in targets};para={tid:[] for tid in targets}
    class_counts=Counter(); original_count=0;output_count=0;missing=0;trace_errors=0;wrong=Counter();all_ids=set();distance_errors=0
    poetry=iter(rows(source/'blind/job/poetic_prosodic_evidence.csv'))
    expected_poetry=[];required_by_pair=set();relation_counts=Counter()
    for original,r in itertools.zip_longest(rows(source/PAIR_TABLE),rows(out/'01_h0_candidate_review_eligibility.csv')):
        original_count+=original is not None;output_count+=r is not None
        if original is None or r is None: missing+=1;continue
        p=next(poetry);pc=pair_context(original,p,ctx)
        if pc['poetry_exception']:expected_poetry.append(original['pair_id'])
        expected=classify(original,pc)['review_eligibility'];actual=r['review_eligibility']
        original_tid=int(original['target_clause_id'])
        if expected==CLASSES[0]:relation_counts[original_tid]+=1
        if original['candidate_relations']=='MULTIPLE' or pc['source_family_conflict'] or pc['conflict_ids'] or pc['component_ids'] or pc['poetry_exception']:
            required_by_pair.add(original_tid)
        wrong[expected]+=actual!=expected
        class_counts[actual]+=1
        pid=r['candidate_id'];tid=int(r['target_id'])
        missing+=pid!=original['pair_id'] or pid in all_ids or int(r['source_candidate_id'])!=int(original['candidate_clause_id']) or tid!=int(original['target_clause_id'])
        all_ids.add(pid)
        trace_errors+=r['existing_evidence']['canonical_row_sha256']!=hash_row(original) or r['existing_rule_ids']!=original['rule_ids_matched'] or r['existing_candidate_relation']!=original['candidate_relations']
        distance_errors+=int(r['distance'])!=int(original['distance_clauses'])
        if actual in CLASSES[:2]:eligible[tid].append(pid)
        if 'HYPOTACTIC' in r['relations']:hyp[tid].append(pid)
        if 'PARATACTIC' in r['relations']:para[tid].append(pid)
    check('baseline',receipts['baseline']['baseline'],config['baseline'])
    check('frozen',receipts['baseline']['differences'],[])
    check('counts',output_count,original_count);check('identity',missing,0);check('trace',trace_errors,0)
    check('classes',sorted(set(class_counts)-set(CLASSES)),[])
    for field,cls in [('relation',CLASSES[0]),('configuration',CLASSES[1]),('evidence',CLASSES[2]),('insufficient',CLASSES[3])]:check(field,wrong[cls],0)
    check('distance',distance_errors,0)
    old=list(rows(source/'mfr02a_original_decisions.csv'))
    historical_targets={int(t) for r in old for t in r['target_clause_ids']};direct=set(historical_targets)
    for conflict in ctx['conflict_rows'].values():
        tids={int(e.rsplit('-',1)[0].split('-')[1]) for e in conflict['edge_ids']}
        if tids&historical_targets:direct|=tids
    required=required_by_pair|set(ctx['binding_targets'])|set(ctx['target_components'])|direct|{t for t,n in relation_counts.items() if n>1}
    expected_status={t:'TARGET_REVIEW_REQUIRED' if t in required else 'TARGET_REVIEW_OPTIONAL' if eligible[t] else 'TARGET_ARCHIVE_ONLY' for t in targets}
    expected_tier={t:'TIER_1' if t in direct else 'TIER_2' if t in required else 'TIER_3' if eligible[t] else '' for t in targets}
    target_errors=sum(sorted(r['eligible_candidate_ids'])!=sorted(eligible[tid]) or r['target_review_status']!=expected_status[tid] or r['review_tier']!=expected_tier[tid] for tid,r in targets.items())
    check('targets',[target_errors,sorted(targets)],[0,sorted(ctx['inventory'])])
    for field,file,key,expected in [('competition','03_h0_relation_competition_sets.csv','candidate_ids',eligible),
        ('mother_sets','04_h0_mother_candidate_sets.csv','mother_candidate_ids',hyp),('parallel_sets','05_h0_parallel_candidate_sets.csv','parallel_candidate_ids',para)]:
        actual={int(r['target_id']):r[key] for r in rows(out/file)}
        check(field,actual,expected)
    impacts=list(rows(out/'07_h0_global_impact.csv'));check('impact',[len(impacts),sum(not r['global_impact'] for r in impacts)],[original_count,0])
    # IDs can be streamed but these small sets are shared by the validation audit.
    check('ranking',[k for name in ('01_h0_candidate_review_eligibility.csv','02_h0_target_review_eligibility.csv','07_h0_global_impact.csv')
        for k in next(rows(out/name),{}) if k in ('review_score','priority_score','confidence_score','weighted_score','candidate_rank')],[])
    shown=list(rows(out/'display_card_manifest.csv'));check('display',{int(r['target_id']):r['candidate_ids'] for r in shown},eligible)
    pages=[out/p for r in shown for p in r['pages']]
    page_cards=[p.read_text(encoding='utf8').count('\n\n## P') for p in pages]
    check('compact',[sum(page_cards),sum(n>config['display_cards_per_page'] for n in page_cards)],[sum(map(len,eligible.values())),0])
    old=list(rows(source/'mfr02a_original_decisions.csv'));special=list(rows(out/'10_h0_mfr02a_13_case_packet.csv'))
    check('tier1',[r['case_id'] for r in special if r['review_tier']=='TIER_1' and all(targets[int(t)]['review_tier']=='TIER_1' for t in r['target_ids'])],[r['decision_id'] for r in old])
    check('history',{r['case_id']:hash_row(r['original_configuration']) for r in special},{r['decision_id']:hash_row(r) for r in old})
    human_errors=0
    for name in ('10_h0_mfr02a_13_case_packet.csv','12_h0_tier1_review_cases.csv','14_h0_tier2_review_cases.csv','15_h0_tier3_review_cases.csv','08_h0_valency_binding_review.csv'):
        human_errors+=sum(any(r.get(k) for k in HUMAN_FIELDS) for r in rows(out/name))
    check('human',[human_errors,metadata['new_human_judgments']],[0,[]])
    sets_rows=[r for name in ('03_h0_relation_competition_sets.csv','04_h0_mother_candidate_sets.csv','05_h0_parallel_candidate_sets.csv') for r in rows(out/name)]
    check('mother',[sum(bool(r['accepted_mother'] or r['accepted_parallel_peer']) for r in sets_rows),metadata['canonical_mothers']],[0,[]])
    check('hierarchy',metadata['canonical_hierarchies'],[])
    check('binding',[r['binding_id'] for r in rows(out/'08_h0_valency_binding_review.csv')],[r['binding_id'] for r in ctx['bindings']])
    check('poetry',[r['candidate_id'] for r in rows(out/'09_h0_poetry_syntax_conflict_review.csv')],expected_poetry)
    freeze=json.loads((out/'eligibility_freeze.json').read_text())
    check('isolation',[p for p,h in freeze.items() if digest(out/p)!=h],[])
    controls=list(rows(out/'18_h0_control_fixture_validation.csv'))
    check('controls',controls,fixture_checks(source))
    check('scope',[metadata['analysis_scope'],[p.name for p in out.iterdir() if p.name in ('blind','pentateuch','qohelet','lamentations','isaiah')]],['JOB',[]])
    imports=[]
    for filename in ('milal_review_eligibility.py','milal_relation_competition.py','milal_review_packet.py','milal_mfr02r_h0.py'):
        tree=ast.parse((ROOT/'src'/filename).read_text(encoding='utf8'))
        imports += [n.module for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module and any(x in n.module for x in ('grammar','engine','features','observation'))]
    check('grammar',imports,[])
    test=receipts['tests'];check('regression',[test['test_scope'],test['failures'],test['errors'],test['tests_run']>0],['FULL_REGRESSION',0,0,True])
    check('skips',test['skipped'],0);check('determinism',determinism,True);check('manifest',verify_manifest(out),True)
    return m
