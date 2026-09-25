"""Only post-freeze validation looks up known references."""
import zipfile
from milal_mfr01b_data import zip_rows, TABLES, OUTPUTS, ref
from milal_mfr01a_data import stream

def validate(out,raw,archive,synthetic=False):
    external=[];job=[];out=__import__('pathlib').Path(out)
    scopes={'pentateuch':'18_pentateuch_edsf_control_report.csv','prophets':'19_prophetic_superscription_control_report.csv','death':'20_death_resumption_control_report.csv','daniel_ezra':'21_daniel_ezra_control_report.csv'}
    with zipfile.ZipFile(raw) as rz,zipfile.ZipFile(archive) as az:
        for scope,name in scopes.items():
            controls=list(zip_rows(rz,name));roles={r['marker_id']:r for r in stream(out/'audit'/scope/OUTPUTS['roles'])}
            required={e['relation_candidate_id'] for c in controls for e in c['relation_evidence']}
            cross={r['raw_relation_candidate_id']:r for r in zip_rows(az,'consolidated/'+scope+'/10_raw_relation_case_crosswalk.csv') if r['raw_relation_candidate_id'] in required}
            for c in controls:
                mids=c['marker_ids'];pairs=c['relation_evidence'];markers=[roles[mid] for mid in mids if mid in roles]
                preserved=len(markers)==len(mids) and all(e['relation_candidate_id'] in cross and cross[e['relation_candidate_id']]['raw_labels']==e['labels'] for e in pairs)
                primary=any(m['primary_bearing'] for m in markers)
                signal_separation=all(not set(m['support_sources'])&set(m['formal_role_sources']) for m in markers)
                valid=preserved and signal_separation and (primary if scope=='pentateuch' else True)
                external.append(dict(scope=scope,book=c['book'],reference=c['reference'],marker_ids=mids,primary_marker_ids=[m['marker_id'] for m in markers if m['primary_bearing']],support_evidence={m['marker_id']:m['support_sources'] for m in markers},raw_relation_ids=[e['relation_candidate_id'] for e in pairs],candidate_labels=sorted({x for e in pairs for x in e['labels']}),valid=valid,status='PRESERVED' if mids else 'NONRECOVERY_PRESERVED',automatic_resolution=False))
        obs=list(zip_rows(rz,'blind/job/'+TABLES['observation']));markers=list(zip_rows(rz,'blind/job/'+TABLES['markers']));roles={r['marker_id']:r for r in stream(out/'audit/job'/OUTPUTS['roles'])};cess={r['marker_id']:r for r in stream(out/'audit/job'/OUTPUTS['cessations'])}
        configs=list(stream(out/'audit/job'/OUTPUTS['configurations']))
        targets=['31:40','32:1','4:9','7:9','11:20','17:5','19:27','1:6','1:7','1:8','1:9','1:10','1:11','1:12','1:13','1:14','1:15','1:16','1:17','1:18','1:19','2:1','2:2','2:3','27:1','29:1','38:1','40:1','40:6','42:7','42:16','37:24'] if not synthetic else ['8:8','8:21','8:23']
        for target in targets:
            found=[m for m in markers if str(m['chapter'])+':'+str(m['verse'])==target];mids={m['marker_id'] for m in found}
            job.append(dict(reference=target,marker_ids=sorted(mids),roles={mid:roles[mid]['role'] for mid in sorted(mids)},cessation_roles={mid:cess[mid]['role_candidate'] for mid in sorted(mids) if mid in cess},configuration_case_ids=[c['configuration_case_id'] for c in configs if mids&set(c['marker_ids'])],surfaces=[dict(clause_id=c['clause_id'],reference=ref(c),surface=c['surface_hebrew']) for c in obs if str(c['chapter'])+':'+str(c['verse'])==target],status='PRESERVED' if mids else 'POSTFREEZE_NONRECOVERY_PRESERVED'))
    byref={r['reference']:r for r in job}
    word,activity,contrast=('8:8','8:21',['8:23']) if synthetic else ('31:40','32:1',['4:9','7:9','11:20','17:5','19:27'])
    checks=dict(speech_word='DISCOURSE_CESSATION_FORM_CANDIDATE' in byref[word]['cessation_roles'].values(),speech_activity='SPEECH_ACTIVITY_CESSATION_CANDIDATE' in byref[activity]['cessation_roles'].values(),contrast=all('NON_DISCOURSE_CESSATION_USAGE_CANDIDATE' in byref[t]['cessation_roles'].values() for t in contrast),external=bool(external) and all(r['valid'] for r in external))
    return external,job,checks
