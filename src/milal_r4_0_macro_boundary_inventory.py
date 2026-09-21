"""R4.0 whole-book candidate inventory; no final boundary or hierarchy inference."""
from __future__ import annotations
import argparse
from collections import defaultdict, Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_r4_0_sources as src
import milal_mr1_surface_marker_provenance as util
import milal_hr1_adjudication_linkage as hr

VERSION='R4.0'
canonical,sha=util.canonical,util.sha
TABLES={'markers':'01_macro_marker_inventory.csv','candidates':'02_boundary_candidate_inventory.csv',
        'links':'03_candidate_evidence_links.csv','adjacent':'04_adjacent_marker_relations.csv',
        'controls':'05_control_anchor_audit.csv','zones':'06_transition_zone_candidates.csv',
        'sources':'09_evidence_source_inventory.csv','formal':'12_formal_occurrence_inventory.csv',
        'human':'13_human_adjudication_preserved.csv','human_scopes':'14_human_boundary_scopes.csv',
        'extensions':'15_extension_dependency_overlay.csv','singletons':'16_singleton_context_not_triggers.csv',
        'coverage':'17_whole_book_atom_coverage.csv','human_links':'18_human_source_links.csv',
        'way0_audit':'19_way0_source_audit.csv'}
CAUTIONS={
    'CASE028':'Adjacency does not establish direct Elihu-to-YHWH discourse continuity.',
    'CASE029':'Job is the explicit addressee; no inferred direct Elihu-to-YHWH continuity.'}


def unique(rows,key):
    index={}
    for r in rows:
        src.require(r[key] not in index,'duplicate explicit ID '+str(r[key]))
        index[r[key]]=r
    return index


def derive(s):
    atoms,cfg=s['atoms'],s['config']
    ordered=sorted(atoms,key=lambda a:atoms[a]['index'])
    byref=defaultdict(list)
    for a in ordered: byref[atoms[a]['ref'].removeprefix('Job ')].append(a)
    verse_order={ref:i for i,ref in enumerate(byref)}
    cases=unique(s['cases'],'case_id')
    markers,formal,scopes,triggers=[],[],[],[]
    def event(identifier,family,aa,subtype,text,rule,loc,source_id,extra=None):
        src.require(aa and all(a in atoms for a in aa),'unknown event atom')
        first=atoms[aa[0]]
        result=dict(marker_event_id=identifier,evidence_source=loc['archive_role'],source_event_id=source_id,
                    clause=list(dict.fromkeys(atoms[a]['clause'] for a in aa)),clause_atom_ids=aa,
                    first_clause_atom=aa[0],last_clause_atom=aa[-1],chapter=first['chapter'],verse=first['verse'],
                    marker_family=family,marker_subtype=subtype,surface_text=text,source_rule_id=rule,
                    provenance_locator=loc,human_review_link_if_any=[])
        if extra:result.update(extra)
        return result
    for r in s['markers']:
        eid='MR1:'+r['source_event_id']
        observation_keys=('csf_family','csf_profile','csf_scope_profile','csf_scope_evidence','named_addressees',
                          'addressee_evidence','adjunct_details','speaker_source_type','pattern','width_clauses',
                          'wayhi_meta','wayhi_frame','wayhi_time_refs','wayhi_place_refs')
        marker=event(eid,r['family'],r['atom_ids'],r['subtype'],r['surface_text'],r['source_rule_id'],r['provenance_locator'],r['source_event_id'],
                     dict(observation_role='SPEECH_FRAME_CANDIDATE' if r['family']=='MR1_CSF' else 'OBSERVED_MARKER_EVIDENCE',
                          source_observed_fields={k:r['historical_projection'][k] for k in observation_keys if k in r['historical_projection']}))
        markers.append(marker)
        anchor=r['atom_ids'][-1] if r['family']=='MR1_EXPLICIT_CLOSURE' else r['atom_ids'][0]
        triggers.append(dict(id=eid,family=r['family'],anchors=[anchor],locators=[r['provenance_locator']],
                             relation='MARKER_END' if r['family']=='MR1_EXPLICIT_CLOSURE' else 'MARKER_START',cases=[]))
    for r in s['formal']:
        eid='FORMAL:'+r['source_event_id']
        formal.append(event(eid,'R2_R3_FORMAL_OCCURRENCE',r['atom_ids'],'EXPLICIT_REPEATED_WINDOW',r['surface_text'],
                            'EXPLICIT_WINDOW_ENDPOINT_INVENTORY',r['provenance_locator'],r['source_event_id'],
                            dict(bundle_id=r['bundle_id'],window_id=r['window_id'],family_ids=r['family_ids'],
                                 family_signature_definitions=r.get('family_signature_definitions',[]),source_locators=r['source_locators'])))
        triggers.append(dict(id=eid,family='R2_R3_FORMAL_OCCURRENCE',anchors=list(dict.fromkeys([r['atom_ids'][0],r['atom_ids'][-1]])),
                             locators=r['source_locators'],relation='FORMAL_WINDOW_ENDPOINT_NOT_BOUNDARY_ASSERTION',cases=[]))
    for r in s['boundaries']:
        ident=r['boundary_identity'];cid=r['case_id'];ref=ident['boundary_ref']
        src.require(cid in cases and ident['case_id']==cid and ref in byref,'unresolved HR1 boundary identity')
        aa=byref[ref]
        scopes.append(dict(evidence_id='HR1:'+cid,case_id=cid,boundary_ref=ref,clause_atom_ids=aa,
                           scope_precision='VERSE_SCOPE_NOT_ATOM_ADJUDICATED',participating_unit_ids=r['participating_unit_ids'],
                           provenance_locator=r['locator'],human_locator=r['human_adjudication_locator'],
                           human_review_status=cases[cid]['review_status'],reviewer_notes=cases[cid]['reviewer_notes']))
        triggers.append(dict(id='HR1:'+cid,family='HR1_REVIEWED_BOUNDARY_SCOPE',anchors=aa,
                             locators=[r['locator'],r['human_adjudication_locator']],relation='EXACT_REVIEWED_VERSE_SCOPE_NOT_ATOM_DECISION',cases=[cid]))
    unique(markers+formal,'marker_event_id')
    unique(triggers,'id')
    at=defaultdict(list)
    for t in triggers:
        for a in t['anchors']: at[a].append(t)
    candidates,links=[],[]
    for a in sorted(at,key=lambda n:atoms[n]['index']):
        tt=sorted(at[a],key=lambda t:t['id']);human_ids=sorted({c for t in tt for c in t['cases']});cid=f'CAND:A{a}'
        candidates.append(dict(candidate_id=cid,anchor_clause_atom=a,chapter=atoms[a]['chapter'],verse=atoms[a]['verse'],
                               trigger_count=len(tt),trigger_types=sorted({t['family'] for t in tt}),trigger_ids=[t['id'] for t in tt],
                               human_review_status=[dict(case_id=c,review_status=cases[c]['review_status'],form_assessment=cases[c]['form_assessment'],
                                                         scope='EXACT_CASE_VERSE_ONLY') for c in human_ids],
                               candidate_only=True,notes='Positional source-trigger anchor; no final boundary or macro-level assertion.'))
        for t in tt:
            for loc in t['locators']:
                links.append(dict(candidate_id=cid,evidence_type=t['family'],evidence_id=t['id'],source_locator=loc,relation_to_anchor=t['relation']))
    adjacent=[]
    for left,right in zip(candidates,candidates[1:]):
        la,ra=left['anchor_clause_atom'],right['anchor_clause_atom']
        distance=atoms[ra]['index']-atoms[la]['index'];lr=atoms[la]['ref'].removeprefix('Job ');rr=atoms[ra]['ref'].removeprefix('Job ')
        adjacent.append(dict(left_id=left['candidate_id'],right_id=right['candidate_id'],
                             left_event_ids=left['trigger_ids'],right_event_ids=right['trigger_ids'],clause_atom_distance=distance,
                             verse_distance=verse_order[rr]-verse_order[lr],same_verse=lr==rr,directly_adjacent=distance==1))
    zones=[]
    # Fixed bounded forward windows, not transitive connected components.
    # Every eligible window retained; overlapping windows are intentional.
    for i,left in enumerate(candidates):
        aa=left['anchor_clause_atom'];window=[]
        for right in candidates[i:]:
            if atoms[right['anchor_clause_atom']]['index']-atoms[aa]['index']>cfg['zone_span_atoms']:break
            window.append(right)
        evidence_ids=sorted({eid for c in window for eid in c['trigger_ids']})
        if len(window)>=2 and len(evidence_ids)>=2:
            zones.append(dict(zone_id='ZONE:A'+str(aa),start_atom=aa,end_atom=window[-1]['anchor_clause_atom'],
                              candidate_ids=[c['candidate_id'] for c in window],evidence_ids=evidence_ids,
                              overlay_only=True,rule='BOUNDED_FORWARD_NATIVE_ATOM_WINDOW',span_limit=cfg['zone_span_atoms']))
    controls=[]
    for ref in cfg['controls']:
        aa=byref.get(ref,[]);aset=set(aa)
        mm=[r['marker_event_id'] for r in markers if aset.intersection(r['clause_atom_ids'])]
        ff=[r['marker_event_id'] for r in formal if aset.intersection(r['clause_atom_ids'])]
        hh=[r['case_id'] for r in scopes if r['boundary_ref']==ref]
        controls.append(dict(control_ref=ref,clause_atom_ids=aa,matching_MR1_marker_ids=mm,matching_R2_R3_evidence_ids=ff,
                             matching_HR1_cases=hh,source_status='MATCHING_SOURCE_EVIDENCE' if mm or ff or hh else 'NO_MATCHING_SOURCE_EVIDENCE',
                             notes='Control itself never creates an event or candidate. Human links here are exact boundary cases only.'))
    for r in markers:
        r['human_review_link_if_any']=[dict(case_id=h['case_id'],relation='COLOCATED_EXACT_CASE_SCOPE_NOT_EVENT_ADJUDICATION') for h in scopes if set(r['clause_atom_ids']).intersection(h['clause_atom_ids'])]
    human=[]
    for row in s['human']:
        c=cases[row['case_id']]
        human.append(dict(case_id=row['case_id'],human_source_record=row,extension_dependency_cases=c['extension_dependency_cases'],
                          extension_dependency_note=c['extension_dependency_note'],human_locator=c['human_adjudication_locator']))
    coverage=[dict(**atoms[a],candidate_ids=['CAND:A'+str(a)] if a in at else []) for a in ordered]
    return dict(markers=markers,formal=formal,candidates=candidates,links=links,adjacent=adjacent,zones=zones,controls=controls,
                human=human,human_scopes=scopes,extensions=deepcopy(s['extensions']),singletons=deepcopy(s['singleton_context']),
                coverage=coverage,sources=deepcopy(s['sources']),human_links=[dict(source_layer='HR1_R3c3',**r) for r in s['human_evidence']]+[dict(source_layer='HR1_PROV1',**r) for r in s['human_provenance']],
                way0_audit=[dict(source_event_id=r['source_event_id'],is_wayhi=r['is_wayhi'],provenance_locator=r['provenance_locator'],
                                promoted_marker_id='MR1:'+r['source_event_id'] if r['is_wayhi'] else '',retention_role='MR1_AUDIT_POPULATION') for r in s['way0']])


def focus_rows(m,s):
    start=tuple(s['config']['focus_start'])
    return [r for r in m['controls'] if tuple(map(int,r['control_ref'].split(':')))>=start]


def reports(m,s):
    notes={r['case_id']:r['human_source_record']['reviewer_notes'] for r in m['human']}
    common=['R4.0 is a source-trigger candidate inventory, not an accepted boundary segmentation or macro hierarchy.',
            'CSF is historical extraction behavior including speaker resolution: SPEECH_FRAME_CANDIDATE, no automatic macro importance.',
            'Way0 negatives remain in 19_way0_source_audit.csv and never trigger candidates.',
            'Formal repeated-window endpoints are review positions, not demonstrated boundary transitions; low-resolution patterns can make the inventory dense.',
            'Raw trigger multiplicity is not independent corroboration. Formal families may share provenance; MR1 and HR1 can describe the same occurrence.',
            'CASE007–012 remain one human-recognized extension sequence, not six independent evidences. See preserved dependency overlay.',
            'HR1 verse-scope judgments are never narrowed to an invented atom-level decision. Exact case notes apply only to that case.',
            'Adjacency does not establish direct Elihu-to-YHWH discourse continuity. Job is the explicit addressee at 38:1.',
            'Frozen R1.1/v6.42.12 remain historically unavailable. Legacy hierarchy, mother assignments, macro units and literary labels are not used.']
    chapter=defaultdict(Counter)
    for r in m['markers']:chapter[r['chapter']][r['marker_family']]+=1
    for r in m['candidates']:chapter[r['chapter']]['candidates']+=1
    whole=['# R4.0 whole-book macro scaffold','',s['mode'],'']+common+['','## Whole-book marker distribution and candidate distribution','','| Chapter | CSF | Closure | Wayhi-positive | Candidate anchors |','| --- | ---: | ---: | ---: | ---: |']
    for ch in sorted({a['chapter'] for a in s['atoms'].values()}):
        c=chapter[ch];whole.append(f"| {ch} | {c['MR1_CSF']} | {c['MR1_EXPLICIT_CLOSURE']} | {c['MR1_WAYHI_POSITIVE']} | {c['candidates']} |")
    whole+=['','## Evidence multiplicity','',f"{len(m['formal'])} complete formal occurrence records; {len(m['links'])} lossless candidate/source-locator links; {len(m['singletons'])} singleton contexts retained without rarity promotion.",
            'Trigger counts are descriptive multiplicity only; no score or rank. See complete machine-readable tables; no occurrence sampling.','','## Control audit','','| Reference | MR1 events | Formal occurrences | Exact HR1 cases | Status |','| --- | ---: | ---: | --- | --- |']
    for r in m['controls']:whole.append(f"| {r['control_ref']} | {len(r['matching_MR1_marker_ids'])} | {len(r['matching_R2_R3_evidence_ids'])} | {', '.join(r['matching_HR1_cases']) or 'none'} | {r['source_status']} |")
    whole+=['','## Candidate transition zones','',f"{len(m['zones'])} bounded forward windows, maximum native atom index distance {s['config']['zone_span_atoms']}. Every eligible overlapping window remains in 06_transition_zone_candidates.csv. No chain-merging or pruning.",
            'Zone identities only overlay existing candidate/event identities; they do not create structural units.','','## Unresolved questions','',
            'Marker presence, formal pattern occurrence and reviewed endings do not establish a hierarchy level. Dense formal coverage requires later methodological review, not automatic thinning. See the derived focus report.']
    focus=['# R4.0 focus: Job 27:1–42:17','', 'Derived after whole-book inventory; control references never generate evidence.','']+common
    byid={r['marker_event_id']:r for r in m['markers']}
    formal_by_id={r['marker_event_id']:r for r in m['formal']}
    for r in focus_rows(m,s):
        aa=set(r['clause_atom_ids']);focus+=['','## Job '+r['control_ref'],'',f"Atoms: {r['clause_atom_ids']}"]
        focus.append('Marker evidence: '+(canonical([dict(id=eid,family=byid[eid]['marker_family'],subtype=byid[eid]['marker_subtype'],surface=byid[eid]['surface_text'],source_observed_fields=byid[eid]['source_observed_fields']) for eid in r['matching_MR1_marker_ids']]) if r['matching_MR1_marker_ids'] else 'NO_MATCHING_SOURCE_EVIDENCE'))
        focus.append(f"Formal evidence: {len(r['matching_R2_R3_evidence_ids'])} complete occurrence IDs in control audit; details and all family locators in 12_formal_occurrence_inventory.csv.")
        focus+=['','| Bundle/window | Native atoms | Explicit family IDs | Source levels |','| --- | --- | --- | --- |']
        for eid in r['matching_R2_R3_evidence_ids']:
            f=formal_by_id[eid]
            focus.append(f"| {f['source_event_id']} | {f['clause_atom_ids']} | {', '.join(f['family_ids'])} | {', '.join(d['level'] for d in f['family_signature_definitions'])} |")
        focus.append('')
        focus.append('Human evidence: '+(', '.join(r['matching_HR1_cases']) or 'NO_MATCHING_SOURCE_EVIDENCE'))
        for cid in r['matching_HR1_cases']:
            focus+=['> '+line for line in notes[cid].split('\n')]
        index=[s['atoms'][a]['index'] for a in aa]
        nearby=[e['marker_event_id'] for e in m['markers'] if index and any(min(index)-s['config']['zone_span_atoms']<=s['atoms'][a]['index']<=max(index)+s['config']['zone_span_atoms'] for a in e['clause_atom_ids'])]
        focus.append('Nearby MR1 event IDs (positional window only): '+canonical(nearby))
        focus.append('Unresolved hierarchy question: no level, parent, continuity or macro-unit assignment follows from these records.')
    focus+=['','## Questions reserved for later review','',
            '- 27:1 / 29:1: compare marker form and full formal evidence; shared form does not establish equal macro status.',
            '- 31:40 / 32:1 / 32:2: one boundary or termination–transition–introduction? Preserve all three exact human cases.',
            '- 37:24 / 38:1: ending/start adjacency is observable; direct discourse continuity remains a separate question.',
            '- 38:1 / 40:1: speech-frame formal relation does not predetermine hierarchy level.',
            '- 42:7: check co-location of Wayhi, speech frame, formal evidence and exact human judgment without treating them as independent votes.',
            '- 42:16: report actual evidence only; a requested control is not a detector.']
    return '\n'.join(whole)+'\n','\n'.join(focus)+'\n'


def gates(m,s):
    expected=derive(s);cfg=s['config'];e=cfg['expected'];atoms=s['atoms'];checks={}
    equal=lambda key:m[key]==expected[key]
    families=Counter(r['marker_family'] for r in m['markers'])
    receipt=s['manifest_receipts']['mr1']
    checks['BHSA_2021_VERIFIED']=s['execution']['bhsa_version']==cfg['bhsa_version'] and s['execution']['tf_version']==cfg['tf_version']
    checks['MR1_MANIFEST_VERIFIED']=bool(receipt['actual']) and receipt['actual']==receipt['expected']
    checks['MR1_REPRODUCTION_ACCEPTED']=s['mr_meta']['status']=='PASS' and cfg['mr1_acceptance_role']=='R4_MARKER_PROVENANCE_ONLY' and all(v['equal'] for v in s['mr_meta']['byte_comparison'].values())
    checks['FULL_JOB_COVERAGE']=s['scope']==cfg['scope'] and equal('coverage')
    checks['NATIVE_SOURCE_COUNTS']=len(s['clauses'])==e['clauses'] and len(atoms)==e['atoms'] and sum(len(a)>1 for a in s['clauses'].values())==e['multi_atom_clauses']
    checks['ALL_MR1_MARKER_IDS_RESOLVE']=equal('markers')
    checks['ALL_CLAUSE_ATOM_LINKS_RESOLVE']=all(r['clause_atom_ids']==next(x['atom_ids'] for x in s['markers'] if x['source_event_id']==r['source_event_id']) and all(a in atoms for a in r['clause_atom_ids']) for r in m['markers']) and {a for aa in s['clauses'].values() for a in aa}==set(atoms)
    checks['WAY0_AUDIT_170']=len(m['way0_audit'])==len(s['way0'])==e['way0'] and equal('way0_audit')
    checks['ONLY_WAYHI_POSITIVES']=families['MR1_WAYHI_POSITIVE']==e['positive'] and {r['source_event_id'] for r in m['markers'] if r['marker_family']=='MR1_WAYHI_POSITIVE'}=={r['source_event_id'] for r in s['way0'] if r['is_wayhi']}
    negative={'MR1:'+r['source_event_id'] for r in s['way0'] if not r['is_wayhi']}
    checks['NEGATIVES_NOT_PROMOTED']=len(negative)==e['negative'] and not negative.intersection(eid for c in m['candidates'] for eid in c['trigger_ids'])
    checks['CSF_PRESERVED']=families['MR1_CSF']==e['csf'] and [r for r in m['markers'] if r['marker_family']=='MR1_CSF']==[r for r in expected['markers'] if r['marker_family']=='MR1_CSF']
    checks['CLOSURES_PRESERVED']=families['MR1_EXPLICIT_CLOSURE']==e['closure'] and [r for r in m['markers'] if r['marker_family']=='MR1_EXPLICIT_CLOSURE']==[r for r in expected['markers'] if r['marker_family']=='MR1_EXPLICIT_CLOSURE']
    known={r['marker_event_id'] for r in m['markers']+m['formal']}|{r['evidence_id'] for r in m['human_scopes']}
    checks['EVERY_CANDIDATE_TRIGGERED']=bool(m['candidates']) and all(c['trigger_count']==len(c['trigger_ids'])>0 and set(c['trigger_ids'])<=known for c in m['candidates']) and equal('candidates')
    changed=dict(s,config=dict(cfg,controls=[]));without=derive(changed)
    checks['CONTROLS_NOT_TRIGGERS']=m['candidates']==without['candidates'] and m['markers']==without['markers']
    checks['RARITY_NOT_TRIGGER']=not any('SINGLETON' in t or 'RARITY' in t for c in m['candidates'] for t in c['trigger_types']) and equal('singletons')
    checks['HUMAN_FIELDS_UNCHANGED']=[r['human_source_record'] for r in m['human']]==s['human'] and len(m['human'])==e['human']
    checks['SEQUENCE_DEPENDENCY_PRESERVED']=equal('extensions') and all(r['extension_dependency_cases']==list(hr.SEQUENCE_CASES) for r in m['human'] if r['case_id'] in hr.SEQUENCE_CASES) and equal('human')
    whole,focus=reports(expected,s)
    for cid,name in [('CASE028','CASE028_CONTINUITY_CAUTION'),('CASE029','CASE029_JOB_ADDRESSEE_CAUTION')]:
        original=next(r for r in s['human'] if r['case_id']==cid)['reviewer_notes']
        checks[name]=any(r['case_id']==cid and r['human_source_record']['reviewer_notes']==original for r in m['human']) and all('> '+line in m['focus_report'] for line in original.split('\n'))
    checks['ADJACENT_EVENTS_DISTINCT']=equal('adjacent') and len({r['marker_event_id'] for r in m['markers']})==len(s['markers'])
    checks['ZONES_OVERLAY_ONLY']=equal('zones') and all(r['overlay_only'] is True and set(r['candidate_ids'])<={c['candidate_id'] for c in m['candidates']} for r in m['zones'])
    # Human quotations and frozen locators are preserved in separate namespaces;
    # no prohibited derived field is allowed in an R4 inventory/edge/zone row.
    schema=set(k for key in ('markers','formal','candidates','links','adjacent','zones') for r in m[key] for k in r)
    checks['NO_SCORES_RANKINGS']=not schema.intersection({'score','rank','ranking','boundary_score','importance'})
    checks['NO_FINAL_BOUNDARY_LABEL']=all(r['candidate_only'] is True for r in m['candidates']) and not schema.intersection({'final_boundary','boundary_label','macro_level'})
    checks['NO_HIERARCHY_PARENTAGE']=not schema.intersection({'parent','parent_id','mother','parentage','hierarchy','macro_unit','continuity'})
    checks['NO_NEW_RHETORICAL_LABELS']=not schema.intersection({'rhetorical_label','theological_label','literary_label','discourse_label'})
    checks['FOCUS_FROM_WHOLE_BOOK']=m['focus_report']==focus and m['whole_report']==whole and equal('controls')
    checks['FINAL_VERSE_INCLUDED']=bool(m['coverage']) and m['coverage'][-1]['ref']==cfg['scope'][-1]
    checks['SOURCE_HASHES_PRESENT']=equal('sources') and all(len(r['SHA256'])==64 for r in m['sources']) and s['verified_hashes']=={k:v['sha256'] for k,v in cfg['sources'].items()}
    checks['NO_FUZZY_LINKAGE']=equal('links') and equal('formal') and equal('human_scopes') and equal('human_links')
    checks['DETERMINISTIC_RERUN']=all(equal(k) for k in TABLES)
    checks['FORMAL_OCCURRENCES_LOSSLESS']=equal('formal') and sum(len(r['family_ids']) for r in m['formal'])==s['formal_family_occurrence_count']
    checks['PARTIAL_INSUFFICIENT_RETAINED']=Counter(r['human_source_record']['form_assessment'] for r in m['human'])==Counter(r['form_assessment'] for r in s['human'])
    checks['UPSTREAM_MANIFESTS_VERIFIED']=all(r['actual'] and r['actual']==r['expected'] for r in s['manifest_receipts'].values())
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def build(s):
    m=deepcopy(derive(s));m['whole_report'],m['focus_report']=reports(m,s)
    return m


def serialize(m,s):
    checks=gates(m,s)
    src.require(all(r['status']=='PASS' for r in checks),'computed R4 gates failed: '+canonical([r for r in checks if r['status']!='PASS']))
    files={name:util.csv_bytes(m[key]) for key,name in TABLES.items()}
    files['07_whole_book_macro_scaffold.md']=m['whole_report'].encode()
    files['08_focus_zone_27_42.md']=m['focus_report'].encode()
    files['10_method_note.md']=(Path(__file__).resolve().parents[1]/'docs/R4_0_SPEC.md').read_bytes()
    meta=dict(version=VERSION,mode=s['mode'],status='PASS',counts={k:len(m[k]) for k in TABLES},
              source_sha256=s['verified_hashes'],bhsa=s['execution'],config=s['config'],
              source_code_sha256={p.name:sha(p.read_bytes()) for p in [Path(__file__),Path(src.__file__)]},
              scope=s['scope'],candidate_only=True,gate_count=len(checks)+1)
    files['90_run_metadata.json']=util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv',None)
        files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=n,sha256=sha(v)) for n,v in sorted(files.items())])
    seal();checks.append(util.manifest_gate(files));files['11_gates.csv']=util.csv_bytes(checks);seal()
    src.require(util.manifest_ok(files),'output manifest failed')
    return files


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True);parser.add_argument('--self-test',action='store_true')
    parser.add_argument('--tf-data')
    for role in ('mr1','r3c3','prov1','hr1','human'):parser.add_argument('--'+role)
    args=parser.parse_args(argv)
    if args.self_test:
        from milal_r4_0_synthetic import source
        s=source()
    else:
        if not args.tf_data:parser.error('--tf-data is required for real execution')
        cfg=json.loads(src.CONFIG.read_text(encoding='utf-8'))
        paths={k:getattr(args,k) or str(src.ROOT/v['path']) for k,v in cfg['sources'].items()}
        s=src.load(cfg,paths,args.tf_data)
    m=build(s);files=serialize(m,s)
    if not args.self_test:
        for r in s['sources']:src.require(sha(Path(r['path_archive']).read_bytes())==r['SHA256'],'source changed during execution')
    # MR1 writer is format-generic except its gate filename/log label; write a
    # local deterministic R4 package below without altering the frozen writer.
    publish(files,args.out)
    print('R4.0 PASS: '+str(Path(args.out).resolve()))
    return 0


def publish(files,out):
    import zipfile
    out=Path(out).resolve();zpath=out.with_name(out.name+'_results.zip');log=out.with_name(out.name+'_run.log')
    src.require(not any(p.exists() for p in (out,zpath,log)),'output already exists')
    src.require(util.manifest_ok(files),'manifest before write')
    out.mkdir(parents=True)
    for name,data in files.items():(out/name).write_bytes(data)
    src.require({p.name:p.read_bytes() for p in out.iterdir()}==files,'disk bytes differ')
    with zipfile.ZipFile(zpath,'w') as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,data)
    with zipfile.ZipFile(zpath) as z:src.require(z.testzip() is None and {n:z.read(n) for n in z.namelist()}==files,'output ZIP verification')
    rows=hr.read_csv(files['11_gates.csv']);src.require(all(r['status']=='PASS' for r in rows),'serialized gate failure')
    log.write_text(f'R4.0 PASS\nGates {len(rows)}/{len(rows)} PASS\nZIP {zpath}\nSHA256 {sha(zpath.read_bytes())}\n',encoding='utf-8')


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as exc:
        print(str(exc),file=sys.stderr);sys.exit(2)
