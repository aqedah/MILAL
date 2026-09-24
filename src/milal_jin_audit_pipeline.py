"""Prepare neutral targets; execute isolated A then post-freeze B; no adjudication."""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import sys

import milal_jin_io as io

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/r4_4_contract_jin_0_2_job.json'
DOCS={'15_jin_method_compliance_report.md':'docs/R4_4_CONTRACT_JIN_0_2_SPEC.md'}


def release_gates(first,second,regression):
    """External release evidence; no self-attested deterministic/test PASS."""
    return [dict(gate='DETERMINISTIC_RERUN',status='PASS' if first==second and bool(first) else 'FAIL'),
        dict(gate='FULL_REGRESSION_SKIP_ZERO',status='PASS' if regression.get('tests_run',0)>0 and
             regression.get('failures')==0 and regression.get('errors')==0 and regression.get('skipped')==0 else 'FAIL')]


def baseline(cfg):
    commit=cfg['baseline_commit'];verified=subprocess.check_output(['git','rev-parse',commit+'^{commit}'],cwd=ROOT,text=True).strip()
    ok=subprocess.run(['git','merge-base','--is-ancestor',commit,'HEAD'],cwd=ROOT).returncode==0
    io.require(verified==commit and ok,'baseline ancestor')
    return dict(expected_commit=commit,verified_commit=verified,is_ancestor=ok)


def pins(cfg):return [dict(path=p,expected=h,actual=io.sha((ROOT/p).read_bytes())) for p,h in cfg['frozen_files'].items()]


def controls(rules):
    from milal_jin_relation_rules import extract,evidence
    from milal_jin_synthetic import controls as fixtures
    from milal_jin_blind_linguistic_audit import neutral
    out={}
    for key,cc in fixtures().items():
        if key=='S10':
            rejected=False
            try:neutral(cc)
            except ValueError:rejected=True
            out[key]=dict(composition_input_rejected=rejected)
        else:
            ff=extract(cc,rules);out[key]=dict(same_type=ff[0]['clause_type']==ff[-1]['clause_type'],hypotheses=[evidence(f,ff[-1],rules) for f in ff[:-1]])
    return out


def enrich(m,cfg):
    m['baseline']=baseline(cfg);m['pins']=pins(cfg);m['controls']=controls(json.loads(m['blind']['19_blind_rule_config.json']))
    m['documents']={k:(ROOT/p).read_bytes() for k,p in DOCS.items()}
    m['request']=(ROOT/cfg['source_request']['path']).read_bytes()
    return m


def gates(m,cfg):
    import milal_jin_postblind_human_comparison as b
    from milal_jin_blind_linguistic_audit import neutral
    from milal_jin_relation_rules import LABELS
    blind=m['blind'];meta=m['phase_a_meta'];sources=io.rows(blind['06_blind_discovery_source_audit.csv'])
    targets=io.rows(blind['01_blind_target_inventory.csv']);features=io.rows(blind['02_blind_linguistic_features.csv'])
    pairs=io.rows(blind['03_blind_candidate_pairs.csv']);hh=io.rows(blind['04_blind_relation_hypotheses.csv']);mm=io.rows(blind['05_blind_hypotaxis_mother_candidates.csv'])
    expected_cross,expected_links=b.compare(blind,m['historical']);expected_places=b.placement(blind,expected_cross,expected_links)
    checks={};allow={f'BHSA2021/{f}.tf' for f in io.RAW_FEATURES}|{'NEUTRAL_TARGETS','LINGUISTIC_RULES','SYNTHETIC_RAW_CORPUS'}|{'DISCOVERY_CODE/'+f for f in ('milal_jin_io.py','milal_jin_relation_rules.py','milal_jin_blind_linguistic_audit.py')}
    source_ok=all(s['source_id'] in allow and s['human_source'] is False for s in sources) and set(meta['loaded_sources'])=={s['source_id'] for s in sources}
    leakage=False
    try:neutral(features);neutral(targets)
    except ValueError:leakage=True
    checks['BLIND_PHASE_HUMAN_LABEL_LEAKAGE_ZERO']=not leakage
    checks['PHASE_A_HUMAN_SOURCE_COUNT_ZERO']=source_ok and meta['human_source_count']==0
    for key in ('NO_EXISTING_HUMAN_RELATION_USED_AS_DISCOVERY_FEATURE','NO_COMPOSITION_MEMBERSHIP_USED_AS_DISCOVERY_FEATURE','NO_CYCLE_MEMBERSHIP_USED_AS_DISCOVERY_FEATURE','NO_SEAM_DECISION_USED_AS_DISCOVERY_FEATURE','SAME_LEVEL_NOT_USED_AS_DISCOVERY_INPUT','CHILD_OF_NOT_USED_AS_DISCOVERY_INPUT'):
        checks[key]=source_ok and not leakage
    checks['NO_BHSA_NATIVE_MOTHER_USED_BEFORE_BLIND_FREEZE']=meta['native_hierarchy_source_count']==0 and not any(Path(s['source_id']).stem in io.NATIVE_FEATURES for s in sources)
    checks['BASELINE_COMMIT_VERIFIED']=m['baseline']==baseline(cfg)
    checks['JIN_0_1_FROZEN_PRESERVED']=io.manifest_ok(m['historical']) and len(m['pins'])==len(cfg['frozen_files']) and all(r['actual']==r['expected']==cfg['frozen_files'][r['path']] for r in m['pins'])
    prepared,_=b.neutral_targets(m['historical'])
    checks['BLIND_TARGET_SCHEMA_NEUTRAL']=len(targets)==len(prepared)==cfg['regression']['targets'] and all(set(t)=={'audit_target_id','book','chapter','verse','clause_id','clause_atom_id','anchor_start','anchor_end'} for t in targets) and not leakage
    checks['BLIND_DISCOVERY_COMPLETE_BEFORE_HUMAN_LOAD']=m['events'][:2]==['BLIND_FREEZE_VERIFIED','HUMAN_ARCHIVE_OPENED'] and io.manifest_ok(blind,'07_blind_discovery_manifest.csv') and m['freeze_sha256']==io.sha(blind['07_blind_discovery_manifest.csv'])
    c=m['controls'];expected_controls=controls(json.loads(blind['19_blind_rule_config.json']))
    def control_ok(key):
        if key=='S10':return c[key]['composition_input_rejected'] is True
        h=c[key]['hypotheses'];same=c[key]['same_type']
        if key in ('S1','S3'):return same==(key=='S1') and len(h)==1 and h[0]['parataxis_supported'] and not h[0]['hypotaxis_supported']
        if key in ('S2','S4','S5'):return (key=='S5' or same==(key=='S2')) and len(h)==1 and h[0]['hypotaxis_supported'] and not h[0]['parataxis_supported']
        if key=='S6':return len(h)==1 and h[0]['parataxis_supported'] and h[0]['hypotaxis_supported']
        if key=='S7':return len(h)>1 and all(x['hypotaxis_supported'] and x['automatic_resolution'] is False for x in h)
        return all(not x['parataxis_supported'] and not x['hypotaxis_supported'] for x in h)
    for gate,key in [('SAME_TYPE_PARATAXIS_CONTROL_PASS','S1'),('SAME_TYPE_HYPOTAXIS_CONTROL_PASS','S2'),('DIFFERENT_TYPE_PARATAXIS_CONTROL_PASS','S3'),('DIFFERENT_TYPE_HYPOTAXIS_CONTROL_PASS','S4'),('EXPLICIT_SUBORDINATE_CONTROL_PASS','S5'),('AMBIGUOUS_RELATION_PRESERVED','S6'),('MULTIPLE_MOTHER_CANDIDATES_PRESERVED','S7'),('SPEAKER_ALONE_INSUFFICIENT','S8'),('ADJACENCY_ALONE_INSUFFICIENT','S9'),('COMPOSITION_INPUT_REJECTED','S10')]:
        checks[gate]=c[key]==expected_controls[key] and control_ok(key)
    checks['NO_AUTOMATIC_WINNER']=all(h['automatic_resolution'] is False and h['relation_candidate_status']=='UNADJUDICATED' for h in hh+mm) and all(p['selected_mother']=='' for p in m['placements'])
    def forbidden(row):
        if isinstance(row,dict):return any(any(t in k.lower() for t in ('score','rank','weight')) or forbidden(v) for k,v in row.items())
        if isinstance(row,list):return any(forbidden(v) for v in row)
        return False
    checks['NO_WEIGHTED_SCORE']=not any(forbidden(r) for r in pairs+hh+mm+m['placements'])
    checks['ALL_ELIGIBLE_HYPOTAXIS_CANDIDATES_PRESERVED']={r['pair_id'] for r in mm}=={h['pair_id'] for h in hh if h['hypotaxis_supported']} and len(mm)==len({r['pair_id'] for r in mm})
    checks['CANDIDATE_UNIVERSE_ACCOUNTED']=meta['summary']['eligible_pair_count']==len(pairs)==len(hh) and meta['summary']['scanned_pair_count']==len(pairs)+meta['summary']['no_support_excluded_pair_count'] and all(p['trigger_reason_codes'] for p in pairs)
    checks['HYPOTHESIS_COUNTS_COMPUTED']=all(meta['summary']['relation_hypotheses'][k]==sum(h['relation_hypothesis']==k for h in hh) for k in LABELS if k!='NO_LINGUISTIC_SUPPORT') and all(h['relation_hypothesis'] in LABELS for h in hh)
    checks['EXISTING_PARENT_3_BLINDLY_BACK_AUDITED']=sum(r['comparison_family']=='HYPOTAXIS' for r in m['crosswalk'])==cfg['regression']['human_direct_mothers'] and [r for r in m['crosswalk'] if r['comparison_family']=='HYPOTAXIS']==[r for r in expected_cross if r['comparison_family']=='HYPOTAXIS']
    checks['EXISTING_SAME_LEVEL_BLINDLY_BACK_AUDITED']=sum(r['comparison_family']=='PARATAXIS' for r in m['crosswalk'])==cfg['regression']['human_same_level'] and [r for r in m['crosswalk'] if r['comparison_family']=='PARATAXIS']==[r for r in expected_cross if r['comparison_family']=='PARATAXIS']
    checks['HUMAN_COMPARISON_FACTS_ONLY']=m['crosswalk']==expected_cross and all(not any(k in r for k in ('directive','keep_for_now','automatic_review_decision')) for r in m['crosswalk'])
    checks['PLACEMENT_PROPOSALS_UNREVIEWED']=m['placements']==expected_places and all(r['proposal_status']=='UNREVIEWED' for r in m['placements'])
    for gate,ref in [('JOB_2_11_NO_MOTHER_ASSIGNED','2:11'),('JOB_32_1_NO_PARENT_ASSIGNED','32:1')]:
        hits=[r for r in m['placements'] if r['reference']==ref];checks[gate]=len(hits)==1 and hits[0]['selected_mother']=='' and not m['new_parent_edges']
    checks['ROOT_NOT_SELECTED']=all(r['selected_root'] is False for r in m['placements'])
    checks['BHSA_NATIVE_POSTBLIND_ONLY']=(not m['native_sources'] and meta['mode']=='SYNTHETIC' or m['events']==['BLIND_FREEZE_VERIFIED','HUMAN_ARCHIVE_OPENED','NATIVE_HIERARCHY_OPENED_AFTER_BLIND_FREEZE']) and all(r['blind_overwritten'] is False for r in m['native_comparison'])
    checks['NATIVE_COMPARISON_REPRODUCIBLE']=m['native_comparison']==b.native_comparison(blind,m['native'])
    checks['NO_NEW_ACCEPTED_RELATION']=m['new_relations']==[] and m['new_human_judgments']==[]
    checks['NO_NEW_PARENT_EDGE']=m['new_parent_edges']==[]
    old=m['historical']['11_revised_r4_4_contract_review_packet.md']
    checks['Q1_Q9_REMAIN_HISTORICAL_UNREVIEWED']=old.count(b'Review status: UNREVIEWED')==9 and io.manifest_ok(m['historical'])
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED'
    checks['R4_4_CONSUMER_NOT_IMPLEMENTED']=m['consumer_implemented'] is False and not list((ROOT/'src').glob('*r4_4*.py'))
    checks['HISTORICAL_ARTIFACTS_UNCHANGED']=io.manifest_ok(m['historical'])
    checks['ALL_REVIEW_CASES_RETAINED']=m['review_cases']==b.review_cases(blind)
    checks['BLANK_HUMAN_REVIEW_FIELDS']=all(r['review_status']=='UNREVIEWED' and all(r[k]=='' for k in ('relation_decision','selected_mother_if_hypotactic','paratactic_peer_if_applicable','evidence_sufficient','additional_information_needed','reviewer_notes')) for r in m['review_cases'])
    checks['REPORTS_FAITHFUL']=m['reports']==b.reports(m)
    checks['EXACT_RESEARCHER_REQUEST']=io.sha(m['request'])==cfg['source_request']['sha256']
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def finalize(m,cfg,synthetic=False):
    import milal_jin_postblind_human_comparison as b
    enrich(m,cfg);gg=gates(m,cfg);io.require(all(r['status']=='PASS' for r in gg),str([r for r in gg if r['status']!='PASS']))
    files=dict(m['blind']);files.update({b.HISTORY+k:v for k,v in m['historical'].items()});files.update(m['reports']);files.update(m['documents'])
    for name,records in [
        ('08_postblind_human_relation_crosswalk.csv',m['crosswalk']),
        ('09_parataxis_back_audit.csv',[r for r in m['crosswalk'] if r['comparison_family']=='PARATAXIS']),
        ('10_hypotaxis_back_audit.csv',[r for r in m['crosswalk'] if r['comparison_family']=='HYPOTAXIS']),
        ('11_relation_discrepancies.csv',[r for r in m['crosswalk'] if r['comparison_status'] not in (b.COMPARISONS[0],b.COMPARISONS[6])]),
        ('12_bhsa_native_postblind_validation.csv',m['native_comparison']),('13_textual_placement_proposals.csv',m['placements']),
        ('20_neutral_to_canonical_crosswalk.csv',m['links']),('21_relation_review_cases.csv',m['review_cases'])]:
        files[name]=io.csv_bytes(records)
    files['22_researcher_source.txt']=m['request'];files['23_synthetic_control_results.json']=io.js(m['controls'])
    files['24_phase_b_source_audit.json']=io.js([dict(source=r['source'],sha256=r['sha256']) for r in m['phase_b_sources']])
    files['90_run_metadata.json']=io.js(dict(version='R4.4-CONTRACT.JIN.0.2',status='PASS',mode='SYNTHETIC' if synthetic else 'REAL_BHSA_2021_BLIND_THEN_POSTBLIND',
        summary=b.summary(m),gate_count=len(gg)+1,baseline=m['baseline'],frozen_receipts=m['pins'],events=m['events'],
        blind_freeze_sha256=m['freeze_sha256'],phase_a_human_source_count=m['phase_a_meta']['human_source_count'],
        source_archive_sha256=m['phase_b_sources'][0]['sha256'],request_sha256=io.sha(m['request']),config_sha256=io.sha(io.js(cfg)),
        native_source_receipts=m['native_sources'],readiness='BLOCKED_PENDING_BLIND_RELATION_HUMAN_REVIEW',consumer_implemented=False,
        implementation_sha256={p.name:io.sha(p.read_bytes()) for p in sorted((ROOT/'src').glob('milal_jin_*.py'))},
        release_checks='Independent ZIP byte equality and full regression skip-zero are externally verified release gates.'))
    io.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if io.manifest_ok(files) else 'FAIL'));files['17_gates.csv']=io.csv_bytes(gg);io.seal(files)
    io.require(io.manifest_ok(files),'final manifest');return files


def execute(config=CONFIG,out=None,tf_data=None,self_test=False,archive=None):
    cfg=json.loads(Path(config).read_bytes());baseline(cfg);io.require(all(r['actual']==r['expected'] for r in pins(cfg)),'frozen source pins')
    out=Path(out).resolve();work=out.with_name(out.name+'_work');io.require(not out.exists() and not work.exists(),'fresh output/work required');work.mkdir(parents=True)
    if self_test:
        # Preparation may inspect historical target inventory, never run discovery with these modules loaded.
        sys.path.insert(0,str(ROOT/'tests'));import r4_4_contract_jin_audit as previous
        state=previous.load(True);history=previous.serialize(previous.build(state),state)
        archive_path=io.publish(history,work/'synthetic_upstream')
    else:
        archive_path=Path(archive) if archive else ROOT/cfg['archive']['path'];data=archive_path.read_bytes();io.require(io.sha(data)==cfg['archive']['sha256'],'JIN.0.1 archive SHA256');history=io.archive(data)
        io.require(len(history)==cfg['archive']['members'] and io.manifest_ok(history),'JIN.0.1 members/manifest')
    from milal_jin_postblind_human_comparison import neutral_targets
    targets,_=neutral_targets(history);target_path=work/'neutral_targets.json';target_path.write_bytes(io.js(targets))
    rule_path=ROOT/cfg['rules_path'];blind_path=work/'blind';args=[sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_blind_linguistic_audit.py'),'--targets',str(target_path),'--rules',str(rule_path),'--out',str(blind_path)]
    if self_test:
        from milal_jin_synthetic import corpus
        raw_path=work/'synthetic_raw.json';raw_path.write_bytes(io.js(corpus(targets)));args+=['--synthetic-corpus',str(raw_path)]
    else:
        io.require(tf_data,'real mode requires explicit --tf-data');args+=['--tf-data',str(Path(tf_data).resolve())]
    log=[json.dumps(dict(phase='PREPARATION_ONLY',human_source=str(archive_path.resolve()),purpose='STRIP_TO_NEUTRAL_TARGETS_ONLY; NOT_DISCOVERY'))]
    first=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');log += [first.stdout,first.stderr]
    out.with_name(out.name+'_run.log').write_text('\n'.join(log),encoding='utf-8')
    io.require(first.returncode==0,'Phase A failed: '+first.stderr)
    blind=io.read_dir(blind_path);io.require(io.manifest_ok(blind,'07_blind_discovery_manifest.csv'),'Phase A freeze before Phase B launch')
    args=[sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_postblind_human_comparison.py'),'--blind',str(blind_path),'--archive',str(archive_path),'--config',str(Path(config).resolve()),'--out',str(out)]
    args+=['--synthetic'] if self_test else ['--tf-data',str(Path(tf_data).resolve())]
    second=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');log += [second.stdout,second.stderr]
    out.with_name(out.name+'_run.log').write_text('\n'.join(log),encoding='utf-8');io.require(second.returncode==0,'Phase B failed: '+second.stderr)
    io.require(io.read_dir(blind_path)==blind,'Phase B changed blind files')
    print(second.stdout);return out


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--config',default=str(CONFIG));p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--self-test',action='store_true');p.add_argument('--archive');args=p.parse_args(argv)
    io.require(not(args.self_test and (args.tf_data or args.archive)),'synthetic/real arguments mixed')
    execute(args.config,args.out,args.tf_data,args.self_test,args.archive);return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,KeyError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
