"""Postblind comparison: verify three freezes before opening human history."""
import argparse
import json
from pathlib import Path
import sys
import milal_jin_io as io
from milal_jin_postcontext_comparison import review_fields


def load(blind_root,archive,cfg,synthetic=False):
    root=Path(blind_root);phases={}
    for name in ('A','B','C'):
        files=io.read_dir(root/name);io.require('metadata.json' in files and 'source_audit.csv' in files and io.manifest_ok(files,'blind_manifest.csv'),'focused freeze invalid '+name);phases[name]=files
    # Opening human-capable archive occurs only after every separate freeze verifies.
    data=Path(archive).read_bytes();io.require(synthetic or io.sha(data)==cfg['archive']['sha256'],'JIN.0.4 ZIP hash')
    history=io.archive(data);io.require(io.manifest_ok(history),'JIN.0.4 manifest')
    return dict(phases=phases,original_phases={k:dict(v) for k,v in phases.items()},history=history,archive_sha256=io.sha(data),events=['A_FREEZE_VERIFIED','B_FREEZE_VERIFIED','C_FREEZE_VERIFIED','HUMAN_ARCHIVE_OPENED_AFTER_ALL_FREEZES'])


def comparison(m):
    a=io.rows(m['phases']['A']['01_job_1_13_candidate_inventory.csv']);b=io.rows(m['phases']['B']['b_focus_candidates.csv']);c=io.rows(m['phases']['C']['10_macro_parent_candidate_inventory.csv'])
    source=io.rows(m['history']['01_jin_human_batch1_decisions.csv']);out=[]
    for old in source:
        bid=old['batch_case_id']
        if bid not in ('B1','B2','B3','B4','B5'):continue
        relevant=[];status='FOCUSED_EVIDENCE_LEAVES_RELATION_UNRESOLVED'
        if bid=='B1':
            relevant=[r for r in io.rows(m['phases']['A']['02_job_1_13_context_comparison.csv']) if set(r['references'])==set(old['references'])]
            if relevant and relevant[0]['comparison']['configuration_status']=='EXACT_CONFIGURATION_CORRESPONDENCE':status='FOCUSED_EVIDENCE_SUPPORTS_HISTORICAL_RELATION'
        elif bid=='B2':
            relevant=[r for r in a if r['preceding']['reference']==old['references'][1]]
            if any(r['retained_mother_candidate'] for r in relevant):status='FOCUSED_EVIDENCE_PARTIALLY_SUPPORTS_HISTORICAL_RELATION'
            elif any(r['clause_evidence']['parataxis_supported'] for r in relevant):status='MULTIPLE_LINGUISTIC_RELATIONS_REMAIN_POSSIBLE'
            else:status='FOCUSED_EVIDENCE_DOES_NOT_RECOVER_RELATION'
        elif bid=='B3':
            relevant=b
            if any('B_FRAME_TO_CSF_HYPOTAXIS_SUPPORTED' in r['hypotheses'] for r in b):status='FOCUSED_EVIDENCE_PARTIALLY_SUPPORTS_HISTORICAL_RELATION'
            elif any('B_MULTIPLE_INTERPRETATIONS_SUPPORTED' in r['hypotheses'] for r in b):status='MULTIPLE_LINGUISTIC_RELATIONS_REMAIN_POSSIBLE'
            else:status='FOCUSED_EVIDENCE_DOES_NOT_RECOVER_RELATION'
        else:
            relevant=[r for r in c if r['target_ref']==old['references'][0] and r['retained']]
            if any(r['macro_mother_supported'] for r in relevant):status='MULTIPLE_LINGUISTIC_RELATIONS_REMAIN_POSSIBLE'
        out.append(dict(batch_case_id=bid,historical_record=old,comparison_status=status,focused_evidence=relevant,new_human_acceptance=False,historical_relation_unchanged=True))
    return out


def reviews(m):
    specs=[('A','1:13','Does linguistic evidence support 1:6 as mother, another preceding clause, or resumed/paratactic placement?'),('B','3:1-2','Does speech-event framing govern, continue, or merely precede CSF; are Job-internal controls adequate?'),('C','2:11','Does the locus have macro mother evidence; what further hierarchy/root rule is needed?'),('C','32:1','Does the locus have macro mother evidence; what further hierarchy/root rule is needed?')]
    out=[]
    for audit,ref,q in specs:
        fields=review_fields();fields.update(selected_mother='',paratactic_peer='')
        out.append(dict(review_case_id='JIN05:'+audit+':'+ref,audit=audit,reference=ref,researcher_question=q,**fields))
    return out


def reports(m):
    packet='# Focused relation human review\n\nNo mother or relation is accepted. Every decision field remains blank.\n'
    for audit,names in [('A',['04_job_1_13_blind_report.md']),('B',['07_job_3_1_2_blind_report.md']),('C',['12_job_2_11_macro_parent_report.md','13_job_32_1_macro_parent_report.md'])]:
        packet+='\n## SECTION '+audit+'\n\n'
        for name in names:packet+=m['phases'][audit][name].decode()+'\n'
        for r in m['reviews']:
            if r['audit']==audit:
                packet+='\n### '+r['reference']+'\n\n'+r['researcher_question']+'\n\n'
                for key in ('review_status','relation_decision','selected_mother','paratactic_peer','macro_projection_decision','evidence_sufficient','additional_information_needed','reviewer_notes'):packet+=key+': '+str(r[key])+'\n\n'
    return packet


def main():
    p=argparse.ArgumentParser();p.add_argument('--blind-root',required=True);p.add_argument('--archive',required=True);p.add_argument('--config',required=True);p.add_argument('--out',required=True);p.add_argument('--synthetic',action='store_true');a=p.parse_args()
    cfg=json.loads(Path(a.config).read_bytes());m=load(a.blind_root,a.archive,cfg,a.synthetic)
    import milal_jin_focused_pipeline as pipeline
    files=pipeline.finalize(m,cfg,a.synthetic);io.require(all(io.read_dir(Path(a.blind_root)/n)==f for n,f in m['original_phases'].items()),'postblind mutated freeze');zp=io.publish(files,a.out)
    print(json.dumps(dict(zip=str(zp),sha256=io.sha(zp.read_bytes()),summary=json.loads(files['90_run_metadata.json'])['summary'])))

if __name__=='__main__':main()
