"""Human-readable cases and marker pages; all adjudication fields stay blank."""
from pathlib import Path
import json
import zipfile
from collections import defaultdict
from milal_mfr01a_data import stream,OUTPUTS,table,write,rows

FAMILY_FIELDS=('bundle_validity','core_construction_decision','variant_relationship_decision','hierarchical_force_observation','additional_context_needed')
RELATION_FIELDS=('relation_decision','parataxis','hypotaxis','embedding','resumption','closure','insufficient','additional_context_needed')

def pretty(value):return json.dumps(value,ensure_ascii=False,indent=2)
def cell(v):return str(v).replace('|','\\|').replace('\n',' ')
def marker_link(mid):return '['+mid+'](review_markers/'+mid+'.md)'

def packet(out,source):
    # Canonical schema is imported only in this post-freeze renderer.
    from milal_r3c_0_2_reviewability import REVIEW_FIELDS
    out=Path(out);source=Path(source)
    bb={r['bundle_id']:r for r in stream(source/OUTPUTS['bundles'])};pp={r['marker_id']:r for r in stream(source/OUTPUTS['profiles'])}
    with zipfile.ZipFile(out/'mfr01_frozen_input.zip') as z:
        cov=rows(z.read('blind/job/09_job_coverage_candidates.csv'));nested=rows(z.read('blind/job/10_job_nested_marker_evidence.csv'))
        marker_order=sorted(rows(z.read('blind/job/05_job_marker_candidates.csv')),key=lambda m:int(m['marker_index']))
        observation=rows(z.read('blind/job/03_job_surface_observation_inventory.csv'))
    cov_by_id={c['coverage_candidate_id']:c for c in cov};nest_by_id={n['nested_evidence_id']:n for n in nested}
    def option(c):
        end=observation[int(c['end_index'])]
        return dict(c,endpoint_reference=str(end['book'])+' '+str(end['chapter'])+':'+str(end['verse']),endpoint_surface=end['surface_hebrew'])
    fr=list(stream(source/OUTPUTS['family_review']));rr=list(stream(source/OUTPUTS['relation_review']));wanted={r['case_id'] for r in rr}
    cases={r['case_id']:r for r in stream(source/OUTPUTS['cases']) if r['case_id'] in wanted}
    fields=tuple(dict.fromkeys((*REVIEW_FIELDS,*FAMILY_FIELDS,*RELATION_FIELDS)))
    human=[]
    for r in fr:human.append(dict(review_case_id='FAMILY:'+r['bundle_id'],case_kind='FAMILY_BUNDLE',evidence_case_id=r['bundle_id'],marker_ids=r['marker_ids'],**{k:'UNREVIEWED' if k=='review_status' else '' for k in fields}))
    for r in rr:
        c=cases[r['case_id']];human.append(dict(review_case_id='RELATION:'+c['case_id'],case_kind='RELATION_EVIDENCE',evidence_case_id=c['case_id'],marker_ids=[c['source_marker_id'],c['target_marker_id']],**{k:'UNREVIEWED' if k=='review_status' else '' for k in fields}))
    table(out/'21_mfr_0_2_human_review_cases.csv',human)
    for mid,p in pp.items():
        text='# '+mid+' — '+p['reference']+'\n\n'+p['surface']+'\n\n'
        for side in ('context_before','context_after'):
            text+='## '+side.replace('_',' ')+'\n\n'+'\n\n'.join(x['reference']+' — '+x['surface'] for x in p[side])+'\n\n'
        text+='## Coverage alternatives\n\n| Candidate | Endpoint | Basis | Clauses | Nested markers / families |\n| --- | --- | --- | --- | --- |\n'
        for cid in p['coverage_candidate_links']:
            c=option(cov_by_id[cid]);text+='| '+' | '.join(cell(c[k]) for k in ('coverage_candidate_id','endpoint_reference','end_basis','clause_count'))+' | '+str(c['nested_marker_count'])+' / '+str(c['nested_family_count'])+' |\n'
        text+='\n## Complete nested marker membership\n\n'
        for nid in p['nested_evidence_links']:
            n=nest_by_id[nid];members=marker_order[int(n['nested_marker_index_start']):int(n['nested_marker_index_end_exclusive'])]
            text+=nid+' ('+n['coverage_candidate_id']+'): '+', '.join('['+m['marker_id']+']('+m['marker_id']+'.md)' for m in members)+'\n\n'
        text+='## Multi-resolution evidence and original values\n\n```json\n'+pretty(p)+'\n```\n\n'
        text+='All coverage options, family IDs, original signature definitions and raw relation links remain explicit. No participant identity or textual level has been adjudicated.\n'
        write(out/'review_markers'/(mid+'.md'),text.encode('utf8'))
    lines=['# MFR.0.1a consolidated evidence review\n','Consolidation is not adjudication. Bundling preserves distinct linguistic claims. Category order is presentation only. No scores or accepted hierarchy.\n',
        'Read each marker link for Hebrew context, all seven signature views, force dimensions, coverage alternatives and nested/raw-relation links. The complete upstream ZIP and raw crosswalk are included. Archive is reference material, not rejected evidence.\n']
    ordered=sorted(fr,key=lambda r:('REPEATED_OCCURRENCE_BUNDLE' not in r['categories'],r['bundle_id']))
    lines.append('## Family bundles\n')
    for row in ordered:
        b=bb[row['bundle_id']];lines.extend(['### '+b['bundle_id']+'\n','Question: What linguistic construction/family does this multi-resolution evidence represent?\n',
            'Categories: '+', '.join(b['categories'])+'\n','Contributing family types: '+', '.join(b['contributing_family_types'])+'\n',
            '| Marker | Reference | Hebrew surface | Base construction | Adjunct variants |\n| --- | --- | --- | --- | --- |'])
        for mid in b['marker_ids']:
            p=pp[mid];lines.append('| '+' | '.join([marker_link(mid),cell(p['reference']),cell(p['surface']),cell(json.dumps(p['base_construction'],ensure_ascii=False)),cell(p['adjunct_variants'])])+' |')
        lines.append('\nContributing families and distinct construction definitions:\n')
        for f in b['family_evidence']:
            lines.append('- '+f['family_id']+' / '+f['family_type']+' / '+f['signature_resolution']+': `'+cell(json.dumps(f['construction_definition'],ensure_ascii=False))+'`')
        lines.append('\nExact/slot/construction differences and original values are in each marker panel; coverage options, context variants and relation links remain independent. Bundle equality does not establish equal textual level.\n')
        lines.append('UNREVIEWED — bundle validity / core construction / variant relationship / hierarchical force / additional context / notes: __________________\n')
    lines.append('## Relation evidence cases\n')
    # Overlapping semantic buckets are displayed together, never ranked.
    for r in sorted(cases.values(),key=lambda r:r['case_id']):
        s,t=pp[r['source_marker_id']],pp[r['target_marker_id']]
        presentation=dict(r,coverage_options=[option(cov_by_id[c]) for c in r['coverage_ids']],nested_intervals=[nest_by_id[n] for n in r['nested_evidence_ids']])
        lines.extend(['### '+r['case_id']+'\n','Buckets: '+', '.join(r['buckets'])+'\n',
            'Source '+marker_link(s['marker_id'])+' — '+s['reference']+' — '+s['surface']+'\n',
            'Target '+marker_link(t['marker_id'])+' — '+t['reference']+' — '+t['surface']+'\n',
            'Formal/context, bundle, coverage/nested, resumption, closure and competing evidence:\n\n```json\n'+pretty(presentation)+'\n```\n',
            'UNREVIEWED — relation decision / parataxis / hypotaxis / embedding / resumption / closure / insufficient / additional context / notes: __________________\n'])
    lines.extend(['## Reference appendices\n','[Archived family bundles](09_family_archive_reference.csv), [archived relations](16_relation_archive_reference.csv), [weak/insufficient closure pairs](14_closure_archive.csv), [all relation cases](11_relation_evidence_cases.csv), [raw traceability](17_raw_to_consolidated_traceability.csv). Every archived case remains machine-readable and linked to original evidence.\n'])
    write(out/'22_mfr_0_2_human_review_packet.md','\n'.join(lines).encode('utf8'))
    return human,fields
