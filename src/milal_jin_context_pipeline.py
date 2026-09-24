"""Context audit preparation, validation and deterministic publication."""
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys
import milal_jin_io as io
import milal_jin_context_configuration as cc

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/r4_4_contract_jin_0_3_job.json'


def pins(cfg):return [dict(path=p,expected=h,actual=io.sha((ROOT/p).read_bytes())) for p,h in cfg['frozen_files'].items()]


def baseline(cfg):
    value=subprocess.check_output(['git','rev-parse',cfg['baseline_commit']+'^{commit}'],cwd=ROOT,text=True).strip()
    io.require(value==cfg['baseline_commit'] and subprocess.run(['git','merge-base','--is-ancestor',value,'HEAD'],cwd=ROOT).returncode==0,'baseline exact/ancestor')
    return value


def gates(m,cfg,synthetic=False):
    import milal_jin_postcontext_comparison as post
    from milal_jin_blind_linguistic_audit import neutral
    c=post.tables(m['c1']);meta=json.loads(m['c1']['29_c1_metadata.json']);checks={}
    src=io.rows(m['c1']['13_context_blind_source_audit.csv']);source_ok=all(r['source_id'].startswith(('JIN.0.2-PHASE-A/','BHSA2021/','C1_CODE/')) or r['source_id']=='NEUTRAL_CONTEXT_RULES' for r in src)
    leak=False
    try:
        for key in c:neutral(c[key])
    except ValueError:leak=True
    checks['BASELINE_EXACT']=m['baseline']==baseline(cfg)
    checks['FROZEN_SOURCE_PINS']=m['pins']==pins(cfg) and all(r['actual']==r['expected'] for r in m['pins'])
    checks['JIN_0_2_ARTIFACT_VERIFIED']=io.manifest_ok(m['history']) and (synthetic or m['archive_sha256']==cfg['archive']['sha256'])
    original_p={r['pair_id']:r for r in io.rows(m['history']['03_blind_candidate_pairs.csv'])}
    original_h={r['pair_id']:r for r in io.rows(m['history']['04_blind_relation_hypotheses.csv'])}
    checks['SUPPORTED_PAIR_COUNTS_PRESERVED']=Counter(r['source_hypothesis']['relation_hypothesis'] for r in c['supported'])==Counter(h['relation_hypothesis'] for h in original_h.values() if h['parataxis_supported'] or h['hypotaxis_supported'])
    if not synthetic:checks['SUPPORTED_PAIR_COUNTS_PRESERVED'] &= sum(r['source_hypothesis']['parataxis_supported'] for r in c['supported'])==cfg['regression']['parataxis'] and sum(r['source_hypothesis']['hypotaxis_supported'] for r in c['supported'])==cfg['regression']['hypotaxis']
    ins={k for k,h in original_h.items() if not h['parataxis_supported'] and not h['hypotaxis_supported']}
    supported=set(original_h)-ins
    checks['INSUFFICIENT_ARCHIVE_PRESERVED']={r['pair_id'] for r in c['archive']}==ins and all(r['archive_status']=='ARCHIVE_INSUFFICIENT_PAIR_EVIDENCE' and r['default_human_review'] is False for r in c['archive'])
    checks['ALL_PAIRS_LOSSLESS']=len(c['supported'])+len(c['archive'])==len(original_p) and all(r['source_pair']==original_p.get(r['pair_id']) and r['source_hypothesis']==original_h.get(r['pair_id']) for r in c['supported']+c['archive'])
    wins={r['bundle_id']:r for r in c['windows']};co={r['context_id']:r for r in c['correspondence']}
    checks['ALL_SUPPORTED_CONTEXT_BUNDLES']=all(f"JX:{r['source_pair']['preceding_clause_id']}:{r['source_pair']['later_clause_id']}" in co for r in c['supported']) and all(len(r['preceding_bundle_ids'])==len(r['later_bundle_ids'])==5 and all(k in wins for k in r['preceding_bundle_ids']+r['later_bundle_ids']) for r in co.values())
    mapped={r['pair_id'] for r in c['membership']};cases={r['case_id']:r for r in c['cases']}
    checks['SUPPORTED_MAPPING_COMPLETE']=mapped==supported and all(r['case_id'] in cases and r['pair_id'] in cases[r['case_id']]['member_pair_ids'] for r in c['membership'])
    checks['NO_SUPPORTED_PAIR_DROPPED']={p for r in c['cases'] for p in r['member_pair_ids']}==supported
    checks['PAIR_IDS_TRACEABLE']=all(r['member_pair_count']==str(len(r['member_pair_ids'])) and all(p in original_p for p in r['member_pair_ids']+r['auxiliary_pair_ids']) for r in c['cases'])
    disposition=io.rows(m['c1']['11_pairwise_to_contextual_crosswalk.csv'])
    checks['ALL_PAIR_DISPOSITIONS_TRACEABLE']=len(disposition)==len(original_p) and {r['pair_id'] for r in disposition}==set(original_p) and all(r['case_ids']==sorted({x['case_id'] for x in c['membership'] if x['pair_id']==r['pair_id']}) and r['disposition']==('ARCHIVE_INSUFFICIENT_PAIR_EVIDENCE' if r['pair_id'] in ins else 'PRIMARY_CONTEXTUAL_CASE') for r in disposition)
    checks['CANDIDATES_UNADJUDICATED']=all(r['status']=='UNADJUDICATED' and r['automatic_resolution'] is False for r in c['cases']+c['scopes'])
    old_count=len(io.rows(m['history']['21_relation_review_cases.csv']));default=[r for r in m['review'] if r['default_human_review']]
    checks['REVIEW_CASE_REDUCTION']=0<len(default)<old_count and len(c['cases'])<old_count
    features=io.rows(m['c1']['blind_input/02_blind_linguistic_features.csv']);ctx=cc.Context(features,c['targets'],meta['rules'])
    checks['CONTEXT_CORRESPONDENCE_COMPUTED']=all(r==io.rows(io.csv_bytes([ctx.compare(int(r['preceding_clause_id']),int(r['later_clause_id']))]))[0] for r in c['correspondence'])
    expected_scopes=[ctx.scope(r['source_pair'],r['source_hypothesis'],co[f"JX:{r['source_pair']['preceding_clause_id']}:{r['source_pair']['later_clause_id']}"]) for r in c['supported']]
    for t in c['targets']:
        for n in t['clause_id']:ctx.bundle(n)
    checks['SCOPE_CLASSIFICATION_COMPUTED']=c['scopes']==io.rows(io.csv_bytes(expected_scopes))
    checks['FIXED_ADAPTIVE_WINDOWS_PRESERVED']=c['windows']==io.rows(io.csv_bytes([w for n in sorted(ctx.windows) for w in ctx.windows[n]]))
    checks['ORDERED_SIGNATURES_COMPUTED']=c['signatures']==io.rows(io.csv_bytes([ctx.signatures[k] for k in sorted(ctx.signatures)]))
    control={tuple(r['references']):r for r in m['controls']}
    checks['CONTROL_CONTEXTS_GENERATED']=m['controls']==post.control_panels(m['c1'],cfg)
    checks['WAYHI_CONTRAST_CAPTURED']=synthetic or control[('1:6','1:13')]['context']['flags']['C_FOLLOWING_CONFIGURATION_DIVERGENCE']=='DIFFERENT'
    checks['WAYHI_REPEATED_CONFIGURATION_CAPTURED']=synthetic or control[('1:6','2:1')]['context']['configuration_status']=='EXACT_CONFIGURATION_CORRESPONDENCE'
    # Synthetic controls still test the actual categorical invariants, not unconditional PASS.
    if synthetic:
        checks['WAYHI_CONTRAST_CAPTURED']=m['synthetic_controls']['S2'] is True
        checks['WAYHI_REPEATED_CONFIGURATION_CAPTURED']=m['synthetic_controls']['S1'] is True
    checks['ALL_SYNTHETIC_CONTROLS']=len(m['synthetic_controls'])==12 and all(v is True for v in m['synthetic_controls'].values())
    for ref,gate,expected in [('2:11','JOB_2_11_SCOPE_CLASSIFIED',4),('32:1','JOB_32_1_SCOPE_CLASSIFIED',2)]:
        checks[gate]=m['special'][ref]==post.special(m['c1'],ref) and (synthetic or len(m['special'][ref])==expected)
    scopes={r['pair_id']:r for r in c['scopes']}
    checks['CLAUSE_INTERNAL_EXCLUDED_FROM_MACRO']=all(not r['clause_internal_only'] for r in c['macro_mothers']) and c['clause_internal']==[r for r in c['scopes'] if r['clause_internal_only']]
    expected_macro=[dict(**r,relation_family='HYPOTAXIS') for r in c['scopes'] if original_h[r['pair_id']]['hypotaxis_supported'] and not r['clause_internal_only'] and r['macro_projection_status'] in cc.PROJECTABLE]
    checks['MACRO_MOTHER_POOL_PROJECTABLE_ONLY']=c['macro_mothers']==expected_macro
    checks['NO_MOTHER_SELECTED']=all(r['selected_mother']=='' for r in c['cases']+c['scopes']+m['placements'])
    checks['NO_ACCEPTED_PARATAXIS']=meta['accepted_parataxis']==[] and all(r['adjudication_applied'] is False for r in c['cases'])
    checks['NO_ACCEPTED_HYPOTAXIS']=meta['accepted_hypotaxis']==[] and all(r['adjudication_applied'] is False for r in c['cases'])
    checks['NO_NEW_HUMAN_JUDGMENT_OR_PARENT']=meta['new_human_judgments']==meta['new_parent_edges']==[]
    checks['C1_HUMAN_SOURCE_COUNT_ZERO']=source_ok and meta['human_source_count']==0 and all(r['human_source'] is False for r in src)
    checks['C1_HUMAN_LABEL_LEAKAGE_ZERO']=not leak and meta['human_label_leakage_count']==0
    checks['C1_COMPOSITION_SOURCE_COUNT_ZERO']=source_ok and meta['composition_source_count']==0 and all(r['composition_source'] is False for r in src)
    checks['C1_NATIVE_HIERARCHY_SOURCE_COUNT_ZERO']=meta['native_hierarchy_source_count']==0 and all(r['native_hierarchy_source'] is False and Path(r['source_id']).stem not in io.NATIVE_FEATURES for r in src)
    checks['C1_FREEZE_BEFORE_HUMAN_LOAD']=m['events']==['C1_FREEZE_VERIFIED','HUMAN_JIN_0_2_ARCHIVE_OPENED_AFTER_FREEZE'] and m['freeze_sha256']==io.sha(m['c1']['14_context_blind_manifest.csv'])
    checks['C2_CANNOT_MUTATE_C1']=m['c1_after']==m['c1']
    expected=post.compare(m['c1'],m['history'])
    checks['SAME_LEVEL_POSTBLIND_ONLY']=checks['C1_FREEZE_BEFORE_HUMAN_LOAD'] and [r for r in m['comparisons'] if r['relation_family']=='PARATAXIS']==[r for r in expected if r['relation_family']=='PARATAXIS']
    checks['MOTHER_JUDGMENTS_POSTBLIND_ONLY']=checks['C1_FREEZE_BEFORE_HUMAN_LOAD'] and [r for r in m['comparisons'] if r['relation_family']=='HYPOTAXIS']==[r for r in expected if r['relation_family']=='HYPOTAXIS']
    checks['PAIRWISE_CONTEXT_BOTH_PRESERVED']=m['comparisons']==expected and all(r['historical_relation_unchanged'] is True for r in m['comparisons'])
    checks['REVIEW_UNIVERSE_COMPUTED']=m['review']==post.review_cases(m['c1'],m['comparisons'])
    checks['ARCHIVE_NOT_DEFAULT_REVIEW']=all(not (set(r['member_pair_ids'])<=ins) or r['case_origin']=='POSTFREEZE_HISTORICAL_COMPARISON' for r in default)
    checks['REVIEW_FIELDS_BLANK']=all(all(r[k]==v for k,v in post.review_fields().items()) for r in m['review'])
    checks['CONTEXTUAL_PLACEMENTS_APPEND_ONLY']=m['placements']==post.placements(m['c1'],m['history']) and all(r['automatic_supersession'] is False for r in m['placements'])
    def bad(value,tokens):
        if isinstance(value,dict):return any(any(t in k.lower() for t in tokens) or bad(v,tokens) for k,v in value.items())
        if isinstance(value,list):return any(bad(v,tokens) for v in value)
        return False
    checks['NO_NUMERIC_RELATION_SCORE']=not bad([c['cases'],c['scopes'],c['correspondence']],('score','weight'))
    checks['NO_CANDIDATE_RANKING']=not bad([c['cases'],m['review']],('rank','priority_score'))
    checks['NO_ARBITRARY_REVIEW_CAP']=not bad([cfg,meta['rules']],('max_cases','top_k','case_cap'))
    checks['PARTICIPANT_ARC_UNTOUCHED']=meta['participant_arc']=='UNADJUDICATED'
    checks['R4_4_CONSUMER_ABSENT']=meta['consumer_implemented'] is False and not list((ROOT/'src').glob('*r4_4*.py'))
    checks['HISTORICAL_ARTIFACTS_UNCHANGED']=io.manifest_ok(m['history']) and all(m['c1']['blind_input/'+n]==m['history'][n] for n in cc.FROZEN_NAMES)
    checks['C1_MANIFEST_VALID']=io.manifest_ok(m['c1'],'14_context_blind_manifest.csv')
    checks['REPORTS_FAITHFUL']=m['reports']==post.reports(m)
    checks['EXACT_REQUEST']=io.sha(m['request'])==cfg['source_request']['sha256']
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def enrich(m,cfg):
    from milal_jin_context_synthetic import controls
    m['baseline']=baseline(cfg);m['pins']=pins(cfg);m['synthetic_controls']=controls()
    m['request']=(ROOT/cfg['source_request']['path']).read_bytes();return m


def finalize(m,cfg,synthetic=False):
    import milal_jin_postcontext_comparison as post
    enrich(m,cfg);gg=gates(m,cfg,synthetic);io.require(all(r['status']=='PASS' for r in gg),str([r for r in gg if r['status']=='FAIL']))
    files=dict(m['c1']);files.update({post.HISTORY+k:v for k,v in m['history'].items()});files.update(m['reports'])
    for name,rows in [('12_contextual_placement_proposals.csv',m['placements']),('15_postcontext_human_comparison.csv',m['comparisons']),
        ('16_historical_same_level_context_audit.csv',[r for r in m['comparisons'] if r['relation_family']=='PARATAXIS']),
        ('17_historical_mother_context_audit.csv',[r for r in m['comparisons'] if r['relation_family']=='HYPOTAXIS']),
        ('18_relation_reopen_cases.csv',[r for r in m['review'] if r['review_bucket']=='REVIEW_A_CONFLICT_OR_REOPEN']),
        ('19_job_2_11_context_panel.csv',m['special']['2:11']),('21_job_32_1_context_panel.csv',m['special']['32:1']),
        ('24_contextual_human_review_cases.csv',[r for r in m['review'] if r['default_human_review']]),
        ('33_neutral_control_comparisons.csv',m['controls']),('36_clause_internal_case_appendix.csv',[r for r in m['review'] if not r['default_human_review']])]:files[name]=io.csv_bytes(rows)
    files['26_method_compliance_report.md']=(ROOT/'docs/R4_4_CONTRACT_JIN_0_3_SPEC.md').read_bytes()
    files['34_researcher_source.txt']=m['request'];files['35_synthetic_controls.json']=io.js(m['synthetic_controls'])
    files['90_run_metadata.json']=io.js(dict(version='R4.4-CONTRACT.JIN.0.3',status='PASS',mode='SYNTHETIC' if synthetic else 'REAL_BHSA_2021',
        readiness='READY_FOR_CONTEXTUAL_HUMAN_RELATION_REVIEW',summary=post.summary(m),baseline=m['baseline'],frozen_receipts=m['pins'],
        archive_sha256=m['archive_sha256'],c1_freeze_sha256=m['freeze_sha256'],events=m['events'],gate_count=len(gg)+1,
        phase_c1_human_source_count=0,phase_c1_human_label_leakage_count=0,phase_c1_native_source_count=0,
        implementation_sha256={p.name:io.sha(p.read_bytes()) for p in sorted((ROOT/'src').glob('milal_jin_*context*.py'))},
        external_release_gates=['FULL_REGRESSION_SKIP_ZERO','DETERMINISTIC_RERUN']))
    io.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if io.manifest_ok(files) else 'FAIL'));files['28_gates.csv']=io.csv_bytes(gg);io.seal(files);return files


def run(args,log):
    r=subprocess.run(args,cwd=ROOT,text=True,encoding='utf8',capture_output=True);log.extend([r.stdout,r.stderr]);io.require(r.returncode==0,r.stderr);return r


def synthetic_archive(work,log):
    # Fixture preparation is not C1. Historical helper imports never enter the C1 process.
    sys.path.insert(0,str(ROOT/'tests'));import r4_4_contract_jin_audit as previous
    from milal_jin_postblind_human_comparison import neutral_targets
    from milal_jin_synthetic import clause
    state=previous.load(True);history=previous.serialize(previous.build(state),state);zp=io.publish(history,work/'synthetic_jin01')
    targets,_=neutral_targets(history);raw=[]
    for i,t in enumerate(targets):
        for j in range(2):
            raw.append(clause(i*2+j+1,chapter=t['chapter'],verse=t['verse'],subject=['PERSON/','OTHER/','THIRD/'][i%3],verb='>MR[' if i%2 else 'HLK[',relative=(j==1 and i%4==0)))
    (work/'targets.json').write_bytes(io.js(targets));(work/'raw.json').write_bytes(io.js(raw))
    run([sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_blind_linguistic_audit.py'),'--targets',str(work/'targets.json'),'--rules',str(ROOT/'config/jin_blind_linguistic_rules.json'),'--synthetic-corpus',str(work/'raw.json'),'--out',str(work/'synthetic_a')],log)
    run([sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_postblind_human_comparison.py'),'--blind',str(work/'synthetic_a'),'--archive',str(zp),'--config',str(ROOT/'config/r4_4_contract_jin_0_2_job.json'),'--synthetic','--out',str(work/'synthetic_jin02')],log)
    return work/'synthetic_jin02_results.zip'


def execute(config=CONFIG,out=None,tf_data=None,self_test=False,archive=None):
    cfg=json.loads(Path(config).read_bytes());baseline(cfg);io.require(all(r['actual']==r['expected'] for r in pins(cfg)),'frozen pins')
    out=Path(out).resolve();work=out.with_name(out.name+'_work');io.require(not out.exists() and not work.exists(),'fresh output/work required');work.mkdir(parents=True)
    log=[];zp=synthetic_archive(work,log) if self_test else Path(archive) if archive else ROOT/cfg['archive']['path']
    data=zp.read_bytes();io.require(self_test or io.sha(data)==cfg['archive']['sha256'],'upstream ZIP hash');history=io.archive(data);io.require(io.manifest_ok(history),'upstream ZIP manifest')
    blind={n:history[n] for n in cc.FROZEN_NAMES};io.require(io.manifest_ok(blind,'07_blind_discovery_manifest.csv'),'blind subset manifest')
    inp=work/'blind_input';io.publish(blind,inp,False)
    args=[sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_contextual_relation_audit.py'),'--blind-input',str(inp),'--rules',str(ROOT/cfg['rules_path']),'--out',str(work/'c1')]
    if not self_test:io.require(tf_data,'real C1 requires --tf-data');args+=['--tf-data',str(Path(tf_data).resolve())]
    logpath=out.with_name(out.name+'_run.log')
    try:
        run(args,log);frozen=io.read_dir(work/'c1');io.require(io.manifest_ok(frozen,'14_context_blind_manifest.csv'),'C1 freeze before C2 launch')
        args=[sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_postcontext_comparison.py'),'--c1',str(work/'c1'),'--archive',str(zp),'--config',str(Path(config).resolve()),'--out',str(out)]
        if self_test:args+=['--synthetic']
        result=run(args,log);io.require(frozen==io.read_dir(work/'c1'),'C2 changed C1 bytes');print(result.stdout)
    finally:logpath.write_bytes(('\n'.join(log)+'\n').encode())
    return out


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default=str(CONFIG));p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--archive');p.add_argument('--self-test',action='store_true');a=p.parse_args(argv)
    io.require(not(a.self_test and (a.tf_data or a.archive)),'synthetic/real mix');execute(a.config,a.out,a.tf_data,a.self_test,a.archive)


if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError) as e:print(str(e),file=sys.stderr);sys.exit(2)
