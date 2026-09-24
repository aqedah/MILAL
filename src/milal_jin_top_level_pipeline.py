"""Run S, freeze S, run M, freeze M, then open historical sources."""
from __future__ import annotations
import argparse
from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import milal_jin_io as io

ROOT=Path(__file__).resolve().parents[1]
CONFIG=ROOT/'config/r4_4_contract_jin_0_9_job.json'
MANIFESTS={'S':'07_strict_blind_manifest.csv','M':'16_macro_blind_manifest.csv'}
HISTORY='history/jin_0_8/'


def verified_phases(paths):
    phases={role:io.read_dir(path) for role,path in paths.items()}
    io.require(set(phases)=={'S','M'},'two independent audits required')
    for role,f in phases.items():io.require(io.manifest_ok(f,MANIFESTS[role]),role+' physical freeze invalid')
    return phases


def run(command,logs):
    r=subprocess.run(command,cwd=ROOT,capture_output=True,text=True,encoding='utf8');logs.extend([r.stdout,r.stderr]);io.require(r.returncode==0,r.stderr);return r


def assemble(phases,history,cfg,archive_sha,events,synthetic=False):
    # Imported only after independently written S/M manifests have been verified.
    import milal_jin_strict_top_level_audit as strict
    import milal_jin_macro_top_level_audit as macro
    import milal_jin_top_level_postblind as post
    models={r:json.loads(phases[r][r.lower()+'_model.json']) for r in ('S','M')};expected={}
    for role,builder in [('S',strict.build),('M',macro.build)]:
        meta=json.loads(phases[role]['metadata.json']);expected[role]=builder(json.loads(phases[role]['raw_inventory.json']),meta['linguistic_rules'],meta['rules'])
    p=post.compare(models['S'],models['M'],history,cfg,synthetic)
    return dict(phases=phases,original_phases=deepcopy(phases),models=models,expected=expected,post=p,expected_post=deepcopy(p),
        history=history,archive_sha=archive_sha,events=events,baseline=cfg['baseline'],pins={k:io.sha((ROOT/k).read_bytes()) for k in cfg['frozen_files']},
        request=(ROOT/cfg['source_request']['path']).read_bytes(),synthetic=synthetic)


def gates(m,cfg):
    import milal_jin_top_level_common as common
    import milal_jin_top_level_postblind as post
    s=m['models']['S'];a=m['models']['M'];p=m['post'];ep=m['expected_post'];checks={}
    checks['BASELINE_EXACT']=m['baseline']==cfg['baseline']
    checks['JIN_0_8_FROZEN_CONTRACT_VERIFIED']=io.manifest_ok(m['history']) and (m['synthetic'] or m['archive_sha']==cfg['archive']['sha256']) and p['contract']['contract_status']=='REVISED_R4_4_CONTRACT_HUMAN_FROZEN'
    checks['FROZEN_REPOSITORY_PINS']=m['pins']==cfg['frozen_files']
    checks['EXACT_RESEARCHER_SOURCE']=io.sha(m['request'])==cfg['source_request']['sha256']
    checks['HISTORICAL_250_RELATIONS_UNCHANGED']=p['historical_relations']==ep['historical_relations'] and m['history']==ep['history']
    for role in ('S','M'):
        f=m['phases'][role];sources=io.rows(f['06_strict_blind_source_audit.csv' if role=='S' else '15_macro_blind_source_audit.csv']);meta=json.loads(f['metadata.json'])
        checks[role+'_HUMAN_SOURCE_COUNT_ZERO']=bool(sources) and sum(r['human_source'] for r in sources)==meta['human_source_count']==0
        checks[role+'_HUMAN_LABEL_LEAKAGE_ZERO']=meta['human_label_leakage']==common.leakage(m['models'][role])==0
        checks[role+'_NATIVE_HIERARCHY_INPUT_ZERO']=sum(r['native_hierarchy_source'] for r in sources)==meta['native_hierarchy_source_count']==0
        checks[role+'_SOURCE_READ_ALLOWLIST']=sorted(r['source_id'] for r in sources)==meta['loaded_sources'] and all(r['source_id'].startswith(('BHSA2021/','BLIND_CODE/','NEUTRAL_','SYNTHETIC_RAW_CORPUS')) for r in sources)
        checks[role+'_FROZEN_BEFORE_POSTBLIND']=io.manifest_ok(f,MANIFESTS[role]) and m['events'].index(role+'_FREEZE_VERIFIED')<m['events'].index('HUMAN_ARCHIVE_OPENED')
        checks[role+'_EVIDENCE_RECOMPUTES']=m['models'][role]==m['expected'][role]['model'] and all(f[k]==v for k,v in m['expected'][role]['files'].items())
        checks[role+'_CONFIGURATION_SCHEMA']=meta['allowed_configurations']==common.CONFIGURATIONS[role] and all(r['configuration'] in meta['allowed_configurations'] and r['status']=='UNADJUDICATED' and not r['selected'] for r in m['models'][role]['hypotheses'])
    checks['ALL_JOB_CLAUSES_INVENTORIED']=len(s['inventory'])==cfg['expected_clauses'] and len({r['clause_id'] for r in s['inventory']})==cfg['expected_clauses']
    checks['EXPLICIT_HYPOTAXIS_CONTROLS_RECOVERED']=all(any(r['preceding_clause_id']==x and r['later_clause_id']==y and r['explicit_local_dependency'] for r in s['relations']) for x,y in cfg['explicit_controls']) and bool(cfg['explicit_controls'])
    checks['PARATAXIS_POSSIBILITY_PRESERVED']=any(r['evidence_bundle']['parataxis_supported'] for r in s['relations']) and s['relations']==m['expected']['S']['model']['relations']
    checks['NO_ALL_CLAUSE_ONE_MOTHER']=all(r['selected_mother']=='' and not r['automatic_resolution'] for r in s['relations']) and all(not r['automatic_resolution'] for r in s['dispositions'])
    checks['SCOPE_INITIAL_NOT_ROOT']=bool(s['top']) and all(not r['selected_root'] for r in s['top']) and any('S_SCOPE_INITIAL_CANDIDATE' in r['candidate_kind'] for r in s['top'])
    checks['M_GENERIC_ONSET_DISCOVERY']=a['onsets']==m['expected']['M']['model']['onsets'] and bool(a['onsets'])
    checks['M_GENERIC_CLOSURE_DISCOVERY']=a['closures']==m['expected']['M']['model']['closures'] and bool(a['closures'])
    checks['M_REPEATED_FAMILIES_PRODUCED']=a['families']==m['expected']['M']['model']['families'] and bool(a['families'])
    checks['M_MULTIPLE_EVIDENCE_CONTAINMENT']=all({'repeated_distribution','next_equivalent_onset','nested_onset','internal_asymmetry','participant_surface_recurrence','domain_containment','compatible_closure_ids'}<=set(r['evidence_bundle']) and all(r['evidence_bundle'].values()) for r in a['relations'] if r['candidate_kind']=='M_MACRO_CONTAINMENT_POSSIBLE') and a['relations']==m['expected']['M']['model']['relations']
    checks['M_NO_LONGEST_COVERAGE_WINNER']=all(not r['selected_root'] and r['selected_mother']=='' for r in a['top']) and not a['frame']['root_selected'] and not a['frame']['span_created']
    checks['NO_NUMERIC_RANKING']=not any(any(t in k.lower() for t in ('score','rank','best_root','winner')) for obj in common.walk([s,a]) if isinstance(obj,dict) for k in obj)
    checks['NO_TECHNICAL_COMPOSITION_ROOT']=common.leakage([s['top'],a['top']])==0 and all(not r['root_candidate'] and not r['mother_candidate'] for r in p['groups'])
    checks['POSTBLIND_SOURCE_ORDER']=m['events']==['S_FREEZE_VERIFIED','M_FREEZE_VERIFIED','HUMAN_ARCHIVE_OPENED','POSTBLIND_COMPARISON']
    checks['BLIND_OUTPUTS_UNMUTATED']=m['phases']==m['original_phases']
    for key,name in [('strict','STRICT_POSTBLIND_COMPARISON'),('macro','MACRO_POSTBLIND_COMPARISON'),('groups','GROUPS_POSTBLIND_ONLY'),('cross','CROSS_LAYER_COMPARISON'),('impacts','OPEN_SCOPE_IMPACT_LOSSLESS')]:checks[name]=p[key]==ep[key] and bool(p[key])
    checks['SAME_ANCHOR_NOT_AUTO_UNIFIED']=all(not r['automatic_unification'] and not r['same_root_status_inferred'] for r in p['cross'])
    checks['ONLY_TWO_ROOT_SCOPES_DIRECT']=sorted(r['question_id'] for r in p['impacts'] if r['direct_review'])==['ROOT:MACRO','ROOT:STRICT']
    checks['REMAINING_SCOPES_NOT_RESOLVED']=len(p['impacts'])==cfg.get('expected_scope_count',220) and all(not r['resolved'] for r in p['impacts'])
    checks['HUMAN_REVIEW_FIELDS_BLANK']=p['questions']==ep['questions'] and len(p['questions'])==10 and all(r['review_status']=='UNREVIEWED' and all(r[k]==v for k,v in post.review_fields().items()) for r in p['questions'])
    for ref,name in [('2:11','JOB_2_11_UNCHANGED'),('32:1','JOB_32_1_UNCHANGED')]:checks[name]=p['mother_status'].get(ref)=='NO_MACRO_MOTHER_FOUND'
    for key,name in [('new_human_judgments','NO_NEW_HUMAN_JUDGMENT'),('new_parent_edges','NO_NEW_PARENT_EDGE'),('new_roots','NO_NEW_ROOT'),('new_macro_relations','NO_NEW_MACRO_RELATION'),('new_strict_relations','NO_NEW_STRICT_RELATION'),('migrations','NO_MIGRATION')]:checks[name]=not p[key]
    checks['PARTICIPANT_ARC_UNTOUCHED']=p['participant_arc']=='UNADJUDICATED'
    checks['R4_4_CONSUMER_ABSENT']=not p['consumer_implemented'] and not list((ROOT/'src').glob('*r4_4*.py')) and not list((ROOT/'scripts').glob('*r4_4*'))
    return checks


def execute(out,tf_data=None,self_test=False):
    out=Path(out).resolve();work=out.with_name(out.name+'_work');io.require(not out.exists() and not work.exists(),'fresh paths required');work.mkdir(parents=True);logs=[];events=[]
    # No historical archive/config/module is opened before both isolated freezes.
    if self_test:
        from milal_jin_top_level_synthetic import corpus
        raw=corpus();(work/'raw.json').write_bytes(io.js(raw))
    try:
        for role,script in [('S','strict'),('M','macro')]:
            command=[sys.executable,'-B','-X','utf8',str(ROOT/f'src/milal_jin_{script}_top_level_audit.py'),'--linguistic-rules',str(ROOT/'config/jin_blind_linguistic_rules.json'),'--rules',str(ROOT/'config/jin_top_level_rules.json'),'--out',str(work/role)]
            if self_test:command+=['--synthetic-corpus',str(work/'raw.json')]
            else:io.require(tf_data,'raw BHSA path required');command+=['--tf-data',str(Path(tf_data).resolve())]
            run(command,logs);f=io.read_dir(work/role);io.require(io.manifest_ok(f,MANIFESTS[role]),'physical freeze '+role);events.append(role+'_FREEZE_VERIFIED')
        phases=verified_phases({r:work/r for r in ('S','M')});cfg=json.loads(CONFIG.read_bytes())
        subprocess.run(['git','merge-base','--is-ancestor',cfg['baseline'],'HEAD'],cwd=ROOT,check=True,capture_output=True)
        if self_test:
            from milal_jin_top_level_synthetic import history_fixture
            history,cfg=history_fixture(cfg);archive_sha=io.sha(io.js({k:io.sha(v) for k,v in history.items()}))
        else:
            data=(ROOT/cfg['archive']['path']).read_bytes();archive_sha=io.sha(data);io.require(archive_sha==cfg['archive']['sha256'],'JIN.0.8 ZIP hash');history=io.archive(data)
        io.require(io.manifest_ok(history),'upstream manifest');events.append('HUMAN_ARCHIVE_OPENED');events.append('POSTBLIND_COMPARISON')
        m=assemble(phases,history,cfg,archive_sha,events,self_test);checks=gates(m,cfg);io.require(all(checks.values()),'failed gates '+str([k for k,v in checks.items() if not v]))
        import milal_jin_top_level_postblind as post
        files={HISTORY+k:v for k,v in history.items()}
        for role,f in phases.items():
            files.update({'blind/'+role+'/'+k:v for k,v in f.items()})
            files.update({k:v for k,v in f.items() if k[:2].isdigit()})
        files.update(post.render(m['post'],m['models']['S'],m['models']['M']))
        # Controls are observed after discovery; missing onsets are reported, never injected.
        macro=m['models']['M'];control_rows=[]
        for ref in cfg['macro_controls']:
            control_rows.append(dict(reference=ref,raw_observed=any(r['reference']==ref for r in macro['markers']),onset_ids=[r['onset_id'] for r in macro['onsets'] if r['reference']==ref],closure_ids=[r['closure_id'] for r in macro['closures'] if r['reference']==ref],top_ids=[r['candidate_id'] for r in macro['top'] if r['reference']==ref],discovery_seed=False))
        files['27_postblind_raw_locus_controls.csv']=io.csv_bytes(control_rows)
        files['90_run_metadata.json']=io.js(dict(stage=cfg['stage'],baseline=cfg['baseline'],mode='SYNTHETIC' if self_test else 'REAL_BHSA_2021',readiness='READY_FOR_TOP_LEVEL_HUMAN_ADJUDICATION',
            events=events,archive_sha256=archive_sha,blind_manifest_sha256={r:io.sha(phases[r][MANIFESTS[r]]) for r in phases},summary={r:json.loads(phases[r]['metadata.json'])['summary'] for r in phases},
            comparison_counts={k:dict(__import__('collections').Counter(r['status'] for r in m['post'][k])) for k in ('strict','macro','groups')},
            new_human_judgments=0,new_parent_edges=0,new_roots=0,new_macro_relations=0,new_strict_relations=0,relation_migration=0,
            mother_status=m['post']['mother_status'],participant_arc=m['post']['participant_arc'],consumer_implemented=m['post']['consumer_implemented'],frozen_pins=m['pins'],
            external_release_gates=['DETERMINISTIC_RERUN','REGRESSION_PASS'],code_sha256={p.name:io.sha(p.read_bytes()) for p in sorted((ROOT/'src').glob('milal_jin_*top_level*.py'))}))
        io.require(verified_phases({r:work/r for r in phases})==phases,'blind mutation after postblind')
        io.seal(files);checks['MANIFEST_VALID']=io.manifest_ok(files);files['26_gates.csv']=io.csv_bytes([dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]);io.seal(files)
        zp=io.publish(files,out);print(json.dumps(dict(zip=str(zp),sha256=io.sha(zp.read_bytes()),gates=len(checks),summary={r:json.loads(phases[r]['metadata.json'])['summary'] for r in phases})))
    finally:out.with_name(out.name+'_run.log').write_text('\n'.join(logs),encoding='utf8')
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--tf-data');p.add_argument('--self-test',action='store_true');a=p.parse_args();execute(a.out,a.tf_data,a.self_test)
