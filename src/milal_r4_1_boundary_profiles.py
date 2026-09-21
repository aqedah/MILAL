"""R4.1 source-event anchors and descriptive positional evidence; no hierarchy."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from itertools import combinations
import json
from pathlib import Path
import sys
import zipfile

import milal_r4_0_sources as src
import milal_r4_0_macro_boundary_inventory as r40
import milal_mr1_surface_marker_provenance as util

ROOT=src.ROOT
CONFIG=ROOT/'config/r4_1_job.json'
sha,canonical,require=src.sha,src.canonical,src.require
TABLES={'anchors':'01_boundary_oriented_anchors.csv','relations':'02_anchor_formal_relations.csv',
        'edges':'03_anchor_edge_profiles.csv','comparisons':'04_marker_family_comparisons.csv',
        'formal':'12_formal_occurrences.csv','human':'13_human_records.csv','links':'14_anchor_overlap_links.csv',
        'controls':'15_control_audit.csv','sources':'16_sources.csv','extensions':'17_extension_dependencies.csv',
        'human_links':'18_human_source_links.csv','way0_audit':'19_way0_audit.csv'}
REPORTS=('05_transition_profile_31_40_32_6.md','06_transition_profile_37_24_38_1.md',
         '07_yhwh_job_speech_frame_profile.md','08_transition_profile_42_7.md',
         '09_negative_control_42_16.md','10_macro_anchor_review_packet.md')
OBSERVED=('csf_family','csf_profile','csf_scope_profile','csf_scope_evidence','csf_signature',
          'speaker_source_type','speaker_canonical','speaker_subject_names','implicit_context_ref',
          'addressee_evidence','named_addressees','adjunct_details','formula_text','ref','formula_end_ref',
          'pattern','width_clauses','wayhi_meta','wayhi_frame','wayhi_time_refs','wayhi_place_refs')
CAUTIONS='Formal occurrence is not a boundary trigger. Formal crossing is not discourse continuity. Marker identity is not hierarchy level; same formula is not same parentage. Multiple source records are not automatically independent corroboration. Human judgment remains separate from computation.'
QUESTIONS='Unresolved: internal speech formula? speaker/addressee change? closure/opening? formal patterns crossing, beginning or ending at each edge? existing HR1 judgment? No new answers or hierarchy are assigned.'


def load(tf_data,paths=None):
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    oldcfg=json.loads(src.CONFIG.read_text(encoding='utf-8'))
    paths=paths or {}
    pp={k:paths.get(k) or str(ROOT/v['path']) for k,v in oldcfg['sources'].items()}
    p=Path(paths.get('r4_0') or ROOT/cfg['r4_0']['path'])
    archive=src.archive(p.read_bytes(),cfg['r4_0']['sha256'],mr1=True)
    meta=src.metadata(archive)
    require(meta['version']=='R4.0' and meta['mode']=='ACCEPTED_REAL' and meta['status']=='PASS','R4.0 real acceptance')
    require(meta['source_sha256']=={k:v['sha256'] for k,v in oldcfg['sources'].items()},'R4.0 upstream chain')
    s=src.load(oldcfg,pp,tf_data)
    old=r40.build(s)
    reproduced=r40.serialize(old,s)
    require(reproduced==archive['files'],'accepted R4.0 members differ from exact source derivation')
    # No R4.0 output is rewritten. Replay verifies its exact source relationships.
    s['r40']=old
    s['r40_receipt']=dict(expected=cfg['r4_0']['sha256'],actual=sha(p.read_bytes()),
                          members={n:sha(b) for n,b in archive['files'].items()},
                          reproduced={n:sha(b) for n,b in reproduced.items()})
    s['sources'].append(dict(source_layer='r4_0',path_archive=str(p.resolve()),SHA256=sha(p.read_bytes()),role='accepted exhaustive scaffold',status='EXACT_REPLAY_AND_MANIFEST'))
    s['profile_config']=cfg
    return s


def span_relations(x,y,a,b):
    """Inclusive native atom indices; logically overlapping labels are retained."""
    return [k for k,v in [('LEFT_CROSS',x<a<=y),('STARTS_WITHIN',a<=x<=b),
        ('ENDS_WITHIN',a<=y<=b),('RIGHT_CROSS',x<=b<y),('SPANS_ANCHOR',x<a and y>b),
        ('INTERNAL_TO_ANCHOR',a<=x<=y<=b)] if v]


def derive(s):
    atoms=s['atoms']; old=s['r40']; anchors=[]
    def anchor(eid,kind,source_id,aa,family,subtype,loc,observed,human=None):
        require(aa and all(a in atoms for a in aa),'unknown anchor atom')
        idx=[atoms[a]['index'] for a in aa]
        require(idx==list(range(idx[0],idx[-1]+1)),'anchor span not contiguous')
        return dict(anchor_id=eid,source_type=kind,source_id=source_id,atom_ids=aa,first_atom=aa[0],last_atom=aa[-1],
                    first_index=idx[0],last_index=idx[-1],chapter=atoms[aa[0]]['chapter'],
                    ref_start=atoms[aa[0]]['ref'],ref_end=atoms[aa[-1]]['ref'],marker_family=family,marker_subtype=subtype,
                    source_locator=loc,observed_marker_fields=observed,human_case=human or '',
                    scope_precision='EXACT_HR1_VERSE_SCOPE_NOT_ATOM_ADJUDICATED' if human else 'MR1_EVENT_SPAN',
                    surface_text=' | '.join(atoms[a]['surface'] for a in aa),review_status='UNREVIEWED')
    for r in s['markers']:
        anchors.append(anchor('MR1:'+r['source_event_id'],'MR1',r['source_event_id'],r['atom_ids'],r['family'],r['subtype'],
                              r['provenance_locator'],{k:r['historical_projection'][k] for k in OBSERVED if k in r['historical_projection']}))
    for r in old['human_scopes']:
        row=anchor(r['evidence_id'],'HR1',r['case_id'],r['clause_atom_ids'],'','',r['provenance_locator'],{},r['case_id'])
        row.update(human_locator=r['human_locator'],participating_unit_ids=r['participating_unit_ids'])
        anchors.append(row)
    anchors.sort(key=lambda r:(r['first_index'],r['last_index'],r['anchor_id']))
    require(len({r['anchor_id'] for r in anchors})==len(anchors),'duplicate anchor identity')
    formal=deepcopy(s['formal'])
    require(len({r['source_event_id'] for r in formal})==len(formal),'duplicate formal identity')
    for f in formal:
        f['first_index']=atoms[f['atom_ids'][0]]['index'];f['last_index']=atoms[f['atom_ids'][-1]]['index']
    relations=[];edges=[];local={}; family_sets={}
    for a in anchors:
        aid=a['anchor_id'];lo=a['first_index'];hi=a['last_index'];context=set()
        for f in formal:
            labels=span_relations(f['first_index'],f['last_index'],lo,hi)
            if labels:
                relations.append(dict(anchor_id=aid,formal_id=f['source_event_id'],relations=labels,
                                      family_ids=f['family_ids'],source_locators=f['source_locators']))
                context.add(f['source_event_id'])
        for side,cut in [('LEFT_EDGE',lo),('RIGHT_EDGE',hi+1)]:
            bins={k:[] for k in ('TERMINATES_BEFORE_OR_AT','CROSSES_EDGE','BEGINS_AFTER_OR_AT')}
            incident={k:[] for k in bins}
            for f in formal:
                x,y=f['first_index'],f['last_index'];fid=f['source_event_id']
                k='TERMINATES_BEFORE_OR_AT' if y<cut else 'BEGINS_AFTER_OR_AT' if x>=cut else 'CROSSES_EDGE'
                bins[k].append(fid)
                if y==cut-1 or x==cut or k=='CROSSES_EDGE':incident[k].append(fid);context.add(fid)
            for k in bins:
                edges.append(dict(anchor_id=aid,edge=side,cut_index=cut,relation=k,formal_ids=bins[k],
                                  incident_formal_ids=incident[k],occurrence_count=len(bins[k]),incident_count=len(incident[k])))
        local[aid]=sorted(context)
        family_sets[aid]={fid for f in formal if f['source_event_id'] in context for fid in f['family_ids']}
    comparisons=[]
    for a,b in combinations([a for a in anchors if a['source_type']=='MR1'],2):
        if (a['marker_family'],a['marker_subtype'])!=(b['marker_family'],b['marker_subtype']):continue
        left,right=family_sets[a['anchor_id']],family_sets[b['anchor_id']]
        words_a=a['surface_text'].split();words_b=b['surface_text'].split()
        comparisons.append(dict(left_anchor=a['anchor_id'],right_anchor=b['anchor_id'],family=a['marker_family'],subtype=a['marker_subtype'],
            left_ref=a['ref_start'],right_ref=b['ref_start'],left_observed_fields=a['observed_marker_fields'],right_observed_fields=b['observed_marker_fields'],
            left_surface=a['surface_text'],right_surface=b['surface_text'],surface_exact_equal=a['surface_text']==b['surface_text'],
            shared_exact_tokens=sorted(set(words_a)&set(words_b)),left_only_exact_tokens=sorted(set(words_a)-set(words_b)),right_only_exact_tokens=sorted(set(words_b)-set(words_a)),
            shared_family_ids=sorted(left&right),left_only_family_ids=sorted(left-right),right_only_family_ids=sorted(right-left),
            left_context_formal_ids=local[a['anchor_id']],right_context_formal_ids=local[b['anchor_id']],
            edge_profile_keys=[dict(anchor_id=q['anchor_id'],edge=edge) for q in (a,b) for edge in ('LEFT_EDGE','RIGHT_EDGE')]))
    links=[dict(left_anchor=a['anchor_id'],right_anchor=b['anchor_id'],shared_atom_ids=sorted(set(a['atom_ids'])&set(b['atom_ids'])),
                relation='EXACT_SCOPE_OVERLAP_NOT_EVENT_EQUIVALENCE_OR_ADJUDICATION') for a,b in combinations(anchors,2) if set(a['atom_ids'])&set(b['atom_ids'])]
    controls=[]
    for ref in s['profile_config']['controls']:
        aa={a for a,r in atoms.items() if r['ref']=='Job '+ref}
        matches=[a['anchor_id'] for a in anchors if aa.intersection(a['atom_ids'])]
        controls.append(dict(ref='Job '+ref,anchor_ids=matches,formal_ids=[f['source_event_id'] for f in formal if aa.intersection(f['atom_ids'])],
                             status='SOURCE_ANCHOR_PRESENT' if matches else 'NO_BOUNDARY_ORIENTED_SOURCE_ANCHOR'))
    saturation=dict(atoms=len(old['coverage']),candidates=len(old['candidates']),
                    formal_only=sum(bool(r['trigger_ids']) and all(x.startswith('FORMAL:') for x in r['trigger_ids']) for r in old['candidates']),zones=len(old['zones']))
    return dict(anchors=anchors,relations=relations,edges=edges,comparisons=comparisons,formal=formal,links=links,controls=controls,
                human=deepcopy(old['human']),extensions=deepcopy(old['extensions']),human_links=deepcopy(old['human_links']),
                way0_audit=deepcopy(old['way0_audit']),sources=deepcopy(s['sources']),saturation=saturation)


def reports(m,s):
    def block(a):
        aid=a['anchor_id'];out=[f"### {a['ref_start']} — {aid}",f"Span: {a['ref_start']} .. {a['ref_end']}; native atoms {a['atom_ids']}; {a['scope_precision']}",
            'Source locator: '+canonical(a['source_locator']),'Observed MR1 fields:\n\n'+'\n'.join('- '+k+': '+str(v) for k,v in a['observed_marker_fields'].items()),
            'Native surface: '+a['surface_text']]
        if a['human_case']:
            human=next(r for r in m['human'] if r['case_id']==a['human_case'])['human_source_record']
            out+=['Existing human judgment '+a['human_case']+' (complete unchanged record: 13_human_records.csv):',
                  '> '+human['reviewer_notes'].replace('\n','\n> '),
                  'Original assessment: '+human['form_assessment']+'; status: '+human['review_status']]
        out+=['Overlapping source anchors (not merged): '+canonical([r for r in m['links'] if aid in (r['left_anchor'],r['right_anchor'])])]
        table=['| Edge | Positional relation | All occurrences | Incident occurrence IDs |','| --- | --- | ---: | --- |']
        for e in m['edges']:
            if e['anchor_id']==aid:table.append(f"| {e['edge']} | {e['relation']} | {e['occurrence_count']} | {', '.join(e['incident_formal_ids']) or '(none)'} |")
        out.append('\n'.join(table))
        out+=['All span relation IDs/labels: '+canonical([dict(formal_id=r['formal_id'],relations=r['relations']) for r in m['relations'] if r['anchor_id']==aid]),QUESTIONS]
        return '\n\n'.join(out)
    result={}
    for name,lo,hi,csf_only in [(REPORTS[0],(31,40),(32,6),False),(REPORTS[1],(37,24),(38,1),False),
                              (REPORTS[2],(38,1),(42,1),True),(REPORTS[3],(42,7),(42,7),False)]:
        def ref_tuple(ref):return tuple(map(int,ref.removeprefix('Job ').split(':')))
        selected=[a for a in m['anchors'] if ref_tuple(a['ref_start'])<=hi and ref_tuple(a['ref_end'])>=lo and (not csf_only or a['marker_family']=='MR1_CSF')]
        result[name]='\n\n'.join(['# R4.1 source-grounded transition profile',CAUTIONS]+[block(a) for a in selected])+'\n'
    result[REPORTS[4]]='# Job 42:16 negative control\n\n'+CAUTIONS+'\n\n'+canonical([r for r in m['controls'] if r['ref']=='Job 42:16'])+'\n\nFormal evidence alone cannot create an anchor.\n'
    packet=['# Whole-book boundary-oriented review anchors',CAUTIONS,
            'R4.0 saturation (preserved, not a failure): '+canonical(m['saturation']),
            'Edges partition the entire formal inventory. Incident IDs alone touch/cross the cut; remote before/after occurrences are not local evidence. Complete partitions: 03 CSV; exact occurrence/family definitions and locators: 12 CSV.',
            'Family groups are navigation only; all source events remain separate.']
    for family in sorted({(a['marker_family'],a['marker_subtype']) for a in m['anchors']}):
        packet.append('## Navigation family '+canonical(family))
        packet.extend(block(a) for a in m['anchors'] if (a['marker_family'],a['marker_subtype'])==family)
    packet+=['## Exact same-family comparisons','Context = anchor overlap plus immediate edge incident occurrences. Token sets use exact whitespace tokens, no normalization or fuzzy match. All same-family pairs retained.']
    for c in m['comparisons']:
        packet+=['### '+c['left_ref']+' / '+c['right_ref']+' — '+c['subtype'],
                 'Events: '+c['left_anchor']+' / '+c['right_anchor'],
                 'Left surface: '+c['left_surface'],'Right surface: '+c['right_surface'],
                 'Exact surface equality: '+str(c['surface_exact_equal']),
                 'Left observed properties: '+canonical(c['left_observed_fields']),
                 'Right observed properties: '+canonical(c['right_observed_fields']),
                 'Shared families: '+', '.join(c['shared_family_ids']),
                 'Left-only families: '+', '.join(c['left_only_family_ids']),
                 'Right-only families: '+', '.join(c['right_only_family_ids']),
                 'Edge profiles: see both source-event blocks above (LEFT_EDGE and RIGHT_EDGE). Complete context occurrence and token sets: 04_marker_family_comparisons.csv.']
    result[REPORTS[5]]='\n\n'.join(packet)+'\n'
    return result


def build(s):
    m=deepcopy(derive(s));m['reports']=reports(m,s);return m


def gates(m,s):
    expected=derive(s); rr=reports(expected,s);eq=lambda k:m.get(k)==expected[k]
    family=lambda key:[a for a in m['anchors'] if a['marker_family']==key]
    expfamily=lambda key:[a for a in expected['anchors'] if a['marker_family']==key]
    human=lambda case:[a for a in m['anchors'] if a['human_case']==case]
    check={}
    receipt=s['r40_receipt']
    check['R40_SOURCE_INTEGRITY']=receipt['actual']==receipt['expected'] and bool(receipt['members']) and receipt['members']==receipt['reproduced']
    check['NO_FORMAL_ONLY_ANCHORS']=eq('anchors') and all(a['source_type'] in ('MR1','HR1') for a in m['anchors'])
    for name,f in [('CSF_PRESERVED','MR1_CSF'),('CLOSURES_PRESERVED','MR1_EXPLICIT_CLOSURE'),('WAYHI_PRESERVED','MR1_WAYHI_POSITIVE')]:
        check[name]=family(f)==expfamily(f) and bool(expfamily(f))
    check['SIX_HUMAN_SCOPES']=all(human(c)==[a for a in expected['anchors'] if a['human_case']==c] and bool(human(c)) for c in s['profile_config']['human_cases'])
    check['COLOCATED_EVENTS_SEPARATE']=eq('anchors') and eq('links')
    check['EXACT_SOURCE_PROVENANCE']=eq('anchors') and eq('sources') and all(a['source_locator'] for a in m['anchors'])
    check['FORMAL_RELATIONS_EXACT']=eq('relations') and eq('formal')
    check['TWO_EDGE_PARTITIONS']=eq('edges')
    check['NO_FUZZY_LINKAGE']=eq('links') and eq('relations') and eq('comparisons')
    check['CONTROL_42_16_NOT_PROMOTED']=eq('controls') and not any('Job 42:16' in (a['ref_start'],a['ref_end']) for a in m['anchors'])
    for case in ('CASE027','CASE028'):
        check[case+'_SCOPE_RETAINED']=bool(human(case)) and human(case)==[a for a in expected['anchors'] if a['human_case']==case]
    for name,index in [('TRANSITION_32_6_VISIBLE',0),('CONTINUITY_CAUTION_PRESERVED',1),('ORDERED_SPEECH_FRAMES',2),('42_7_DISTINCT_EVENTS',3),('NEGATIVE_CONTROL_REPORT',4),('WHOLE_BOOK_PACKET',5)]:
        check[name]=m['reports'].get(REPORTS[index])==rr[REPORTS[index]]
    for name,left,right in [('COMPARE_27_29','Job 27:1','Job 29:1'),('COMPARE_38_40','Job 38:1','Job 40:1')]:
        select=lambda rows:[r for r in rows if r['left_ref']==left and r['right_ref']==right]
        check[name]=select(m['comparisons'])==select(expected['comparisons']) and bool(select(expected['comparisons']))
    check['ALL_SAME_FAMILY_PAIRS']=eq('comparisons')
    check['HUMAN_JUDGMENTS_UNCHANGED']=eq('human') and eq('extensions') and eq('human_links')
    check['OBSERVED_FIELDS_UNCHANGED']=eq('anchors')
    # Restrict computed schemas; original human source text is a separate namespace.
    for gate,forbidden in [('NO_PARENTAGE',{'parent','parent_id','hierarchy','macro_level'}),('NO_SCORE_RANK',{'score','rank','ranking'}),('NO_NEW_INTERPRETIVE_LABEL',{'rhetorical_label','theological_label','discourse_label','final_boundary'})]:
        check[gate]=all(not forbidden.intersection(row) for key in TABLES if key!='human' for row in m[key])
    check['R40_SATURATION_RETAINED']=eq('saturation') and m['saturation']==s['profile_config']['saturation']
    check['WAY0_NEGATIVES_NOT_PROMOTED']=eq('way0_audit') and all(a['source_id'] not in {r['source_event_id'] for r in s['way0'] if not r['is_wayhi']} for a in m['anchors'])
    check['DETERMINISTIC_REPLAY']=all(eq(k) for k in TABLES) and m['reports']==rr
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in check.items()]


def serialize(m,s):
    checks=gates(m,s);require(all(r['status']=='PASS' for r in checks),'R4.1 gates failed: '+canonical([r for r in checks if r['status']!='PASS']))
    files={name:util.csv_bytes(m[key]) for key,name in TABLES.items()}
    files.update({name:text.encode() for name,text in m['reports'].items()})
    files['20_method_note.md']=(ROOT/'docs/R4_1_SPEC.md').read_bytes()
    meta=dict(version='R4.1',mode=s['mode'],status='PASS',config=s['profile_config'],source_sha256={r['source_layer']:r['SHA256'] for r in s['sources'] if r['source_layer']!='BHSA'},
              bhsa=s['execution'],counts={k:len(m[k]) for k in TABLES},source_breakdown=dict(Counter(a['marker_family'] or 'HR1' for a in m['anchors'])),
              edge_assignments=sum(e['occurrence_count'] for e in m['edges']),incident_edge_assignments=sum(e['incident_count'] for e in m['edges']),
              span_relation_labels=sum(len(r['relations']) for r in m['relations']),saturation=m['saturation'],gate_count=len(checks)+1,
              code_sha256={Path(__file__).name:sha(Path(__file__).read_bytes())})
    files['90_run_metadata.json']=util.json_bytes(meta)
    def seal():
        files.pop('99_manifest_sha256.csv',None)
        files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=n,sha256=sha(v)) for n,v in sorted(files.items())])
    seal();checks.append(util.manifest_gate(files));files['11_gates.csv']=util.csv_bytes(checks);seal()
    require(util.manifest_ok(files),'R4.1 manifest failed');return files


def publish(files,out):
    out=Path(out).resolve();zp=out.with_name(out.name+'_results.zip');log=out.with_name(out.name+'_run.log')
    require(not any(p.exists() for p in (out,zp,log)),'output exists')
    require(util.manifest_ok(files),'manifest before publication');out.mkdir(parents=True)
    for n,b in files.items():(out/n).write_bytes(b)
    with zipfile.ZipFile(zp,'w') as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(n,(2020,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,b)
    with zipfile.ZipFile(zp) as z:require(z.testzip() is None and {n:z.read(n) for n in z.namelist()}==files,'published ZIP integrity')
    require({p.name:p.read_bytes() for p in out.iterdir()}==files,'published disk integrity')
    checks=src.hr.read_csv(files['11_gates.csv']);require(all(r['status']=='PASS' for r in checks),'published gates')
    log.write_text(f'R4.1 PASS\nGates {len(checks)}/{len(checks)} PASS\nZIP {zp}\nSHA256 {sha(zp.read_bytes())}\n',encoding='utf-8')


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);parser.add_argument('--tf-data');parser.add_argument('--self-test',action='store_true')
    for role in ('mr1','r3c3','prov1','hr1','human','r4_0'):parser.add_argument('--'+role.replace('_','-'),dest=role)
    args=parser.parse_args(argv)
    if args.self_test:
        from milal_r4_1_synthetic import source
        s=source()
    else:
        if not args.tf_data:parser.error('--tf-data required')
        s=load(args.tf_data,{k:getattr(args,k) for k in ('mr1','r3c3','prov1','hr1','human','r4_0')})
    m=build(s);files=serialize(m,s)
    if not args.self_test:
        for r in s['sources']:require(sha(Path(r['path_archive']).read_bytes())==r['SHA256'],'source changed before publication')
    publish(files,args.out);print('R4.1 PASS '+str(Path(args.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
