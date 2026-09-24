"""Known loci are consulted only after all consolidation artifacts freeze."""
from pathlib import Path
import zipfile
from milal_mfr01a_data import stream,rows,OUTPUTS

def validate(out,archive,synthetic=False):
    out=Path(out);reports=[];job=[]
    files={'pentateuch':'18_pentateuch_edsf_control_report.csv','prophets':'19_prophetic_superscription_control_report.csv','death':'20_death_resumption_control_report.csv','daniel_ezra':'21_daniel_ezra_control_report.csv','job':'28_job_postblind_locus_controls.csv'}
    checks=dict(pentateuch_expected=0,pentateuch_valid=0,prophet_cross_formal=0,prophet_preserved=0,death_expected=0,death_preserved=0,daniel_expected=0,daniel_preserved=0,nonrecovery_raw_markers=[],nonrecovery_profiles=[],nonrecovery_checked=False)
    with zipfile.ZipFile(archive) as z:
        for scope,name in files.items():
            d=out/'consolidated'/scope;pp={r['marker_id']:r for r in stream(d/OUTPUTS['profiles'])};bb={r['bundle_id']:r for r in stream(d/OUTPUTS['bundles'])}
            cross={r['raw_relation_candidate_id']:r for r in stream(d/OUTPUTS['crosswalk'])}
            controls=rows(z.read(name));required_raw={p['relation_candidate_id'] for c in controls for p in c['relation_evidence']}
            caseids={cross[r]['case_id'] for r in required_raw if r in cross}
            cases={r['case_id']:r for r in stream(d/OUTPUTS['cases']) if r['case_id'] in caseids}
            seen=set()
            for c in controls:
                mids=c['marker_ids'];traceable=all(mid in pp and pp[mid]['all_bundle_ids'] and all(bid in bb for bid in pp[mid]['all_bundle_ids']) for mid in mids)
                variants=all(e['marker_id'] in pp and set(e['tags'])==set(pp[e['marker_id']]['discovery_sources']) for e in c['raw_evidence'])
                pairs=[]
                for raw in c['relation_evidence']:
                    rid=raw['relation_candidate_id'];case=cases.get(cross.get(rid,{}).get('case_id'))
                    okay=bool(case) and set(raw['labels'])<=set(case['raw_labels']) and case['cross_book']==raw['cross_book'] and case['automatic_resolution'] is False
                    pairs.append(dict(raw_relation_candidate_id=rid,case_id=case['case_id'] if case else None,labels=raw['labels'],preserved=okay))
                    if rid in seen:continue
                    seen.add(rid)
                    if scope=='prophets' and raw['cross_book'] and 'FORMAL_PARALLEL_CANDIDATE' in raw['labels']:
                        checks['prophet_cross_formal']+=1;checks['prophet_preserved']+=okay
                    if scope=='death' and raw['cross_book'] and 'TEMPORAL_RESUMPTION_CANDIDATE' in raw['labels']:
                        checks['death_expected']+=1;checks['death_preserved']+=okay
                    if scope=='daniel_ezra' and raw['cross_book']:
                        checks['daniel_expected']+=1;checks['daniel_preserved']+=okay
                if scope=='pentateuch':
                    checks['pentateuch_expected']+=1;checks['pentateuch_valid']+=bool(mids) and traceable and variants and all(p['preserved'] for p in pairs)
                row=dict(scope=scope,book=c['book'],reference=c['reference'],raw_marker_ids=mids,bundle_ids=sorted({b for mid in mids if mid in pp for b in pp[mid]['all_bundle_ids']}),
                    raw_status=c['status'],profile_links=[mid for mid in mids if mid in pp],raw_evidence=c['raw_evidence'],relation_cases=pairs,traceability_valid=traceable,variants_preserved=variants,
                    status='POSTBLIND_NONRECOVERY_PRESERVED' if not mids else 'CONSOLIDATED_EVIDENCE_PRESERVED' if traceable and variants and all(p['preserved'] for p in pairs) else 'FAILED',automatic_resolution=False)
                (job if scope=='job' else reports).append(row)
                if scope=='job' and ((not synthetic and c['reference']=='37:24') or (synthetic and not mids)):
                    checks['nonrecovery_checked']=True;checks['nonrecovery_raw_markers']=mids
                    checks['nonrecovery_profiles']=[mid for mid,p in pp.items() if p['reference']==c['book']+' '+c['reference']]
    return reports,job,checks
