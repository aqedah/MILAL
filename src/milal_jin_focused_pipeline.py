"""Three blind focused audits, freezes, then isolated historical comparison."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import milal_jin_io as io
import milal_jin_context_configuration as cc
from milal_jin_focused_common import Evidence
from milal_jin_focused_blind import BUILD
import milal_jin_focused_postblind_comparison as post

ROOT=Path(__file__).resolve().parents[1];CONFIG=ROOT/'config/r4_4_contract_jin_0_5_job.json';HISTORY='history/jin_0_4/'


def run(args,logs):
    r=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf8');logs.extend([r.stdout,r.stderr]);io.require(r.returncode==0,r.stderr);return r


def execute(out,tf_data=None,self_test=False):
    cfg=json.loads(CONFIG.read_bytes());out=Path(out).resolve();work=out.with_name(out.name+'_work');io.require(not out.exists() and not work.exists(),'fresh paths required');work.mkdir(parents=True)
    subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],'HEAD'],cwd=ROOT,check=True,capture_output=True)
    io.require(all(io.sha((ROOT/k).read_bytes())==h for k,h in cfg['frozen_files'].items()),'frozen file pins');logs=[];rules=ROOT/cfg['blind_rules']
    try:
        if self_test:
            from milal_jin_focused_synthetic import corpus
            raw,targets,controls=corpus();(work/'raw.json').write_bytes(io.js(raw));(work/'targets.json').write_bytes(io.js(targets));rr=json.loads(rules.read_bytes());rr['explicit_control_nodes']=controls;(work/'rules.json').write_bytes(io.js(rr));rules=work/'rules.json'
            run([sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_blind_linguistic_audit.py'),'--targets',str(work/'targets.json'),'--rules',str(ROOT/'config/jin_blind_linguistic_rules.json'),'--synthetic-corpus',str(work/'raw.json'),'--out',str(work/'blind_input')],logs)
            source=io.read_dir(work/'blind_input');batch=json.loads((ROOT/'config/jin_human_batch1.json').read_bytes())['batch']
            history={cfg['blind_prefix']+k:v for k,v in source.items()};history['01_jin_human_batch1_decisions.csv']=io.csv_bytes(batch);history['90_run_metadata.json']=io.js(dict(mode='SYNTHETIC'));io.seal(history);archive=io.publish(history,work/'synthetic_jin04')
        else:
            archive=ROOT/cfg['archive']['path'];data=archive.read_bytes();io.require(io.sha(data)==cfg['archive']['sha256'],'upstream JIN.0.4 ZIP hash');history=io.archive(data);io.require(io.manifest_ok(history),'upstream manifest');source={n:history[cfg['blind_prefix']+n] for n in cc.FROZEN_NAMES};io.publish(source,work/'blind_input',False);io.require(tf_data,'real requires raw BHSA 2021')
        for name in ('A','B','C'):
            args=[sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_focused_blind.py'),'--audit',name,'--blind-input',str(work/'blind_input'),'--rules',str(rules),'--context-rules',str(ROOT/cfg['context_rules']),'--out',str(work/'blind'/name)]
            if not self_test:args+=['--tf-data',str(Path(tf_data).resolve())]
            run(args,logs);io.require(io.manifest_ok(io.read_dir(work/'blind'/name),'blind_manifest.csv'),'freeze '+name)
        frozen={n:io.read_dir(work/'blind'/n) for n in ('A','B','C')}
        args=[sys.executable,'-B','-X','utf8',str(ROOT/'src/milal_jin_focused_postblind_comparison.py'),'--blind-root',str(work/'blind'),'--archive',str(archive),'--config',str(CONFIG),'--out',str(out)]
        if self_test:args+=['--synthetic']
        result=run(args,logs);io.require(all(io.read_dir(work/'blind'/n)==frozen[n] for n in frozen),'postblind freeze mutation');print(result.stdout)
    finally:out.with_name(out.name+'_run.log').write_bytes(('\n'.join(logs)+'\n').encode())
    return out


def enrich(m,cfg):
    from milal_jin_focused_synthetic import controls
    subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],'HEAD'],cwd=ROOT,check=True,capture_output=True)
    m['baseline']=cfg['baseline'];m['pins']=[dict(path=k,expected=h,actual=io.sha((ROOT/k).read_bytes())) for k,h in sorted(cfg['frozen_files'].items())];m['request']=(ROOT/cfg['source_request']['path']).read_bytes()
    blind={n:m['history'][cfg['blind_prefix']+n] for n in cc.FROZEN_NAMES};m['expected']={};ling=json.loads(blind['19_blind_rule_config.json']);ctx=json.loads((ROOT/cfg['context_rules']).read_bytes())
    for name in ('A','B','C'):
        rules=json.loads(m['phases'][name]['metadata.json'])['rules'];e=Evidence(io.rows(blind['02_blind_linguistic_features.csv']),io.rows(blind['01_blind_target_inventory.csv']),rules,ctx,ling)
        m['expected'][name]=BUILD[name](e,blind)
    m['synthetic_controls']=controls(json.loads((ROOT/cfg['blind_rules']).read_bytes()),ling,ctx)
    m['comparisons']=post.comparison(m);m['reviews']=post.reviews(m);m['packet']=post.reports(m)
    m.update(new_human_judgments=[],accepted_relations=[],new_parent_edges=[],q1_q9_approved=False,participant_arc='UNADJUDICATED',consumer_implemented=False)
    return m


def walk(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from walk(v)
    elif isinstance(value,list):
        for v in value:yield from walk(v)


def gates(m,cfg,synthetic=False):
    checks={'BASELINE_COMMIT_VERIFIED':m['baseline']==cfg['baseline'],'FROZEN_REPOSITORY_PINS':all(r['actual']==r['expected'] for r in m['pins']),'JIN_0_4_FROZEN_PRESERVED':io.manifest_ok(m['history']) and (synthetic or m['archive_sha256']==cfg['archive']['sha256']),'EXACT_RESEARCHER_REQUEST':io.sha(m['request'])==cfg['source_request']['sha256']}
    for name in ('A','B','C'):
        f=m['phases'][name];meta=json.loads(f['metadata.json']);sources=io.rows(f['source_audit.csv'])
        checks['AUDIT_'+name+'_BLIND']=io.manifest_ok(f,'blind_manifest.csv') and f==m['original_phases'][name]
        for key,suffix in [('human_source','HUMAN_SOURCE_COUNT_ZERO'),('human_label_leakage','HUMAN_LABEL_LEAKAGE_ZERO'),('composition_source','COMPOSITION_INPUT_ZERO'),('native_hierarchy_source','NATIVE_INPUT_ZERO')]:checks[name+'_'+suffix]=bool(sources) and sum(r[key] for r in sources)==0 and meta['source_counts'][key]==0
        checks[name+'_EVIDENCE_RECOMPUTES']=all(f.get(k)==v for k,v in m['expected'][name]['files'].items())
    checks['BHSA_NATIVE_HIERARCHY_POSTBLIND_ONLY']=m['events']==['A_FREEZE_VERIFIED','B_FREEZE_VERIFIED','C_FREEZE_VERIFIED','HUMAN_ARCHIVE_OPENED_AFTER_ALL_FREEZES'] and all(checks[n+'_NATIVE_INPUT_ZERO'] for n in ('A','B','C'))
    a=io.rows(m['phases']['A']['01_job_1_13_candidate_inventory.csv']);b=io.rows(m['phases']['B']['06_job_speech_frame_candidates.csv']);c=io.rows(m['phases']['C']['10_macro_parent_candidate_inventory.csv']);local=io.rows(m['phases']['C']['11_macro_parent_local_exclusions.csv'])
    def no_mother(rows):return bool(rows) and all(r['selected_mother']=='' and r['status']=='UNADJUDICATED' for r in rows)
    checks['JOB_1_13_NO_MOTHER_AUTO_SELECTED']=no_mother(a)
    checks['JOB_1_13_THREE_WAY_CONTROL_PRESENT']=m['phases']['A']['02_job_1_13_context_comparison.csv']==m['expected']['A']['files']['02_job_1_13_context_comparison.csv']
    checks['JOB_1_13_RESUMPTION_AUDITED']=m['phases']['A']['03_job_1_13_resumption_audit.csv']==m['expected']['A']['files']['03_job_1_13_resumption_audit.csv'] and m['phases']['A']['a_special_resumption.json']==m['expected']['A']['files']['a_special_resumption.json']
    checks['JOB_3_1_2_GENERIC_SPEECH_FRAME_AUDIT']=m['phases']['B']['06_job_speech_frame_candidates.csv']==m['expected']['B']['files']['06_job_speech_frame_candidates.csv']
    checks['JOB_3_1_2_NO_RELATION_AUTO_SELECTED']=no_mother(b) and all(not r['automatic_resolution'] for r in b)
    checks['SPEECH_FRAME_WHOLE_JOB_INVENTORY_PRESENT']=m['phases']['B']['b_clause_event_inventory.csv']==m['expected']['B']['files']['b_clause_event_inventory.csv'] and m['phases']['B']['05_job_speech_transition_inventory.csv']==m['expected']['B']['files']['05_job_speech_transition_inventory.csv']
    controls=io.rows(m['phases']['B']['08_explicit_hypotaxis_controls.csv'])
    checks['EXPLICIT_HYPOTAXIS_CONTROL_PRESENT']=len(controls)==2 and all(r['evidence']['clause_evidence']['hypotaxis_supported'] and r['evidence']['clause_evidence']['evidence_flags']['S_EXPLICIT_SUBORDINATION_MARKER'] and not r['macro_evidence'] and not r['human_accepted'] for r in controls)
    for ref,tag in [('2:11','JOB_2_11'),('32:1','JOB_32_1')]:
        ss=[r for r in local if r['target_ref']==ref];cc=[r for r in c if r['target_ref']==ref];expected=io.rows(m['expected']['C']['files']['11_macro_parent_local_exclusions.csv'])
        checks[tag+'_LOCAL_HYPOTAXIS_EXCLUDED_FROM_MACRO']=ss==[r for r in expected if r['target_ref']==ref] and all(not r['scope']['clause_internal_only'] or r['excluded_from_macro'] for r in ss) and (synthetic or len(ss)==(4 if ref=='2:11' else 2))
        checks[tag+'_NO_MOTHER_AUTO_SELECTED']=no_mother(cc)
    checks['NO_NEAREST_PRECEDING_HEURISTIC']=m['phases']['C']['10_macro_parent_candidate_inventory.csv']==m['expected']['C']['files']['10_macro_parent_candidate_inventory.csv']
    checks['MULTIPLE_CANDIDATES_PRESERVED']=len(c)==len(io.rows(m['expected']['C']['files']['10_macro_parent_candidate_inventory.csv'])) and len(a)==len(io.rows(m['expected']['A']['files']['01_job_1_13_candidate_inventory.csv']))
    checks['NO_NUMERIC_RANKING']=not any(any(token in k.lower() for token in ('score','candidate_rank','best_candidate')) for r in walk(a+b+c) for k in r)
    checks['NO_NEW_HUMAN_JUDGMENT']=m['new_human_judgments']==[] and m['reviews']==post.reviews(m)
    checks['NO_NEW_ACCEPTED_RELATION']=m['accepted_relations']==[]
    checks['NO_NEW_PARENT_EDGE']=m['new_parent_edges']==[]
    checks['Q1_Q9_STILL_UNAPPROVED']=not m['q1_q9_approved']
    checks['PARTICIPANT_ARC_UNADJUDICATED']=m['participant_arc']=='UNADJUDICATED'
    checks['R4_4_CONSUMER_ABSENT']=not m['consumer_implemented'] and not list((ROOT/'src').glob('*r4_4*.py'))
    checks['HISTORICAL_ARTIFACTS_UNCHANGED']=io.manifest_ok(m['history'])
    checks['POSTBLIND_COMPARISON_ONLY']=m['comparisons']==post.comparison(m) and all(r['historical_relation_unchanged'] and not r['new_human_acceptance'] for r in m['comparisons'])
    checks['REVIEW_PACKET_FAITHFUL']=m['packet']==post.reports(m)
    checks['SYNTHETIC_S1_S12']=set(m['synthetic_controls'])=={'S'+str(i) for i in range(1,13)} and all(m['synthetic_controls'].values())
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def finalize(m,cfg,synthetic=False):
    enrich(m,cfg);gg=gates(m,cfg,synthetic);io.require(all(r['status']=='PASS' for r in gg),str([r for r in gg if r['status']=='FAIL']))
    files={};sources=[];freeze={};summary={}
    for name,f in m['phases'].items():
        files.update({'blind/'+name+'/'+k:v for k,v in f.items()});files.update({k:v for k,v in f.items() if k[:2].isdigit()});sources+=io.rows(f['source_audit.csv']);freeze[name]=io.sha(f['blind_manifest.csv']);summary[name]=json.loads(f['metadata.json'])['summary']
    files['14_focused_blind_source_audit.csv']=io.csv_bytes(sources);io.seal(files,'15_focused_blind_manifest.csv')
    files.update({HISTORY+k:v for k,v in m['history'].items()});files['16_focused_postblind_comparison.csv']=io.csv_bytes(m['comparisons']);files['17_focused_relation_review_cases.csv']=io.csv_bytes(m['reviews']);files['18_focused_relation_review_packet.md']=m['packet'].encode()
    files['19_method_compliance_report.md']=(ROOT/'docs/R4_4_CONTRACT_JIN_0_5_SPEC.md').read_bytes();files['20_next_adjudication_scope.md']=('# Next: researcher adjudication, not automatic hierarchy\n\n'+'\n\n'.join(r['researcher_question'] for r in m['reviews'])+'\n').encode()
    files['22_researcher_source.txt']=m['request'];files['23_synthetic_controls.json']=io.js(m['synthetic_controls'])
    native=[dict(member=k,sha256=io.sha(v),scope='HISTORICAL_POSTBLIND_VALIDATION_ONLY') for k,v in m['history'].items() if 'native' in k.lower()];files['24_postblind_native_provenance.csv']=io.csv_bytes(native,['member','sha256','scope'])
    files['90_run_metadata.json']=io.js(dict(stage=cfg['stage'],mode='SYNTHETIC' if synthetic else 'REAL_BHSA_2021',status='PASS',readiness='READY_FOR_FOCUSED_RELATION_HUMAN_ADJUDICATION',baseline=m['baseline'],archive_sha256=m['archive_sha256'],freezes=freeze,events=m['events'],summary=summary,pins=m['pins'],new_human_judgments=m['new_human_judgments'],accepted_relations=m['accepted_relations'],new_parent_edges=m['new_parent_edges'],participant_arc=m['participant_arc'],q1_q9_approved=m['q1_q9_approved'],consumer_implemented=m['consumer_implemented'],code_hashes={p.name:io.sha(p.read_bytes()) for p in sorted((ROOT/'src').glob('milal_jin_*audit.py')) if p.name in ('milal_jin_job_1_13_mother_audit.py','milal_jin_speech_frame_audit.py','milal_jin_macro_parent_audit.py')}|{p.name:io.sha(p.read_bytes()) for p in sorted((ROOT/'src').glob('milal_jin_focused_*.py'))},external_release_gates=['DETERMINISTIC_RERUN','FULL_REGRESSION_PASS']))
    io.seal(files);gg.append(dict(gate='MANIFEST_VALID',status='PASS' if io.manifest_ok(files) else 'FAIL'));files['21_gates.csv']=io.csv_bytes(gg);io.seal(files);return files


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--self-test',action='store_true');a=p.parse_args();io.require(not(a.self_test and a.tf_data),'synthetic/real mix');execute(a.out,a.tf_data,a.self_test)
