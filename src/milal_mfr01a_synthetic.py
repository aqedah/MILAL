"""Artificial frozen MFR snapshots; never imported by real consolidation."""
from copy import deepcopy
from pathlib import Path
from milal_mfr01a_data import TABLES,table
import milal_mfr_common as cm

def snapshot():
    from milal_mfr_selftest import model
    m=model();used={(r['source_marker_id'],r['target_marker_id']) for r in m['relations']}
    # A formal-only archived case exercises presentation, not new detection.
    for s in m['markers']:
        for t in m['markers']:
            if s['marker_id']>=t['marker_id'] or (s['marker_id'],t['marker_id']) in used:continue
            shared=set(s['family_ids'])&set(t['family_ids'])
            if any(f['family_id'] in shared and f['family_type'] in ('ADJUNCT_EXPANSION_FAMILY','MULTI_CLAUSE_CONFIGURATION_FAMILY') for f in m['families']):continue
            r=deepcopy(m['relations'][0]);r.update(relation_candidate_id='SYN_FORMAL_ARCHIVE',source_marker_id=s['marker_id'],target_marker_id=t['marker_id'],source_family_ids=s['family_ids'],target_family_ids=t['family_ids'],
                source_anchor=s['anchor'],target_anchor=t['anchor'],source_clause_id=s['clause_id'],target_clause_id=t['clause_id'],source_book=s['book'],target_book=t['book'],cross_book=s['book']!=t['book'],
                exact_form_correspondence=False,construction_correspondence=True,coverage_relationship=[],nested_relationship=False,closure_evidence=False,
                resumption_evidence=dict(lexical_participant=False,temporal_context_recurrence=False,death_temporal=False,shared_context_lexemes=[]),relation_candidates=['FORMAL_PARALLEL_CANDIDATE','FORMAL_CORRESPONDENCE_ONLY'])
            m['relations'].append(r);return m
    raise AssertionError('synthetic archive pair missing')

def make_archive(path):
    from milal_mfr_controls import control_report
    from milal_mfr01a_provenance import SCOPES
    path=Path(path);path.mkdir(parents=True);m=snapshot()
    for scope in SCOPES:
        d=path/'blind'/scope
        for key,name in TABLES.items():table(d/name,m[key])
    definitions={
      '18_pentateuch_edsf_control_report.csv':('pentateuch',[['Alpha','8:1',1],['Beta','8:14',1]]),
      '19_prophetic_superscription_control_report.csv':('prophets',[['Alpha','8:1'],['Beta','8:14']]),
      '20_death_resumption_control_report.csv':('death',[['Alpha','8:9'],['Beta','8:10']]),
      '21_daniel_ezra_control_report.csv':('daniel_ezra',[['Alpha','8:1'],['Beta','8:14']]),
      '28_job_postblind_locus_controls.csv':('job',[['Alpha','8:1'],['Alpha','8:8'],['Alpha','8:999']]),
    }
    for name,(scope,targets) in definitions.items():table(path/name,control_report(path/'blind'/scope,scope,targets,{'1':dict(time=1,loca=1)}))
    cm.manifest(path,'99_manifest_sha256.csv');return cm.deterministic_zip(path)
