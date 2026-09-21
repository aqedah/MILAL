"""Surface participant-event audit; referential resolution and hierarchy are not inferred."""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

import milal_r4_1_boundary_profiles as previous
import milal_r4_0_sources as src
import milal_mr1_surface_marker_provenance as util

ROOT=src.ROOT
CONFIG=ROOT/'config/r4_2_job.json'
HUMAN=ROOT/'docs/R4_2_HUMAN_JUDGMENTS.json'
sha,canonical,require=src.sha,src.canonical,src.require
FEATURES=('lex','lex_utf8','sp','pdp','vt','vs','ps','gn','nu','prs_ps','prs_gn','prs_nu','st','nametype')
TABLES={'events':'01_participant_transition_events.csv','enclosures':'02_participant_enclosure_relations.csv',
        'endings':'03_parallel_ending_comparisons.csv','inventory':'07_whole_book_participant_transition_inventory.csv',
        'clauses':'12_native_clause_evidence.csv','anchors':'13_frame_endpoints.csv','frames':'14_human_candidate_frames.csv',
        'human':'15_researcher_judgments.csv','controls':'16_control_evidence.csv','correspondences':'17_ending_formal_correspondences.csv',
        'sources':'18_source_inventory.csv','historical_speakers':'19_historical_speaker_provenance.csv',
        'formal':'20_formal_occurrences.csv','old_human':'21_prior_human_records.csv','extensions':'22_extension_dependencies.csv',
        'human_links':'23_prior_human_source_links.csv','way0':'24_way0_audit.csv','formal_relations':'27_participant_formal_relations.csv'}
REPORTS=('04_job_1_3_participant_structure.md','05_wife_friends_comparison.md','06_friends_elihu_comparison.md','08_participant_transition_review_packet.md')
PRINCIPLES="An explicit participant-entry event may be preserved even when the participant's referential identity cannot be resolved from the permitted surface evidence. Event existence and participant identity are separate claims. Participant change is scene-transition evidence, not an automatic macro boundary. All recorded events are audit candidates, not automated scene or hierarchy decisions. Human hierarchy judgments are separate from computation."


def load(tf_data):
    cfg=json.loads(CONFIG.read_text(encoding='utf-8'))
    path=ROOT/cfg['r4_1']['path']; archive=src.archive(path.read_bytes(),cfg['r4_1']['sha256'],mr1=True)
    s=previous.load(tf_data)
    m=previous.build(s); files=previous.serialize(m,s)
    require(files==archive['files'],'R4.1 replay differs from accepted bytes')
    s['r41']=m;s['cfg42']=cfg;s['human42']=json.loads(HUMAN.read_text(encoding='utf-8'))
    s['receipt42']=dict(actual={n:sha(b) for n,b in archive['files'].items()},expected={n:sha(b) for n,b in files.items()},archive_sha=sha(path.read_bytes()))
    s['sources']+= [dict(source_layer='r4_1',path_archive=str(path),SHA256=sha(path.read_bytes()),role='accepted evidence profiles'),
                   dict(source_layer='r4_2_human',path_archive=str(HUMAN),SHA256=sha(HUMAN.read_bytes()),role='explicit researcher judgments')]
    b,execution=util.load_bhsa(tf_data,json.loads(util.CONFIG.read_text(encoding='utf-8')))
    require(execution==s['execution'],'BHSA execution changed during load')
    clauses=[]
    for c in b.clauses:
        phrases=[]
        for ph in b.down(c,'phrase'):
            ww=[dict(node=w,surface=b.text(w),**{k:b.f(k,w) for k in FEATURES}) for w in b.down(ph,'word')]
            phrases.append(dict(node=ph,function=b.f('function',ph),type=b.f('typ',ph),surface=b.text(ph),words=ww))
        aa=b.down(c,'clause_atom'); sec=b.section(c)
        clauses.append(dict(clause=c,clause_atom_ids=aa,chapter=sec[1],verse=sec[2],ref=b.ref(c),type=b.f('typ',c),domain=b.f('domain',c),
                            surface=b.text(c),phrases=phrases,atom_structure=[dict(atom=a,type=b.f('typ',a),word_nodes=b.down(a,'word')) for a in aa]))
    s['native_clauses']=clauses
    return s


def extraction(s):
    """No reference, human label, control coordinate or MR1 inferred speaker is used."""
    rules=s['cfg42']['rules'];events=[];inventory=[];previous_explicit={};seen_names={}
    for c in s['native_clauses']:
        verbs=[w for ph in c['phrases'] for w in ph['words'] if w['sp']=='verb']
        speech=any(w['lex_utf8'] in rules['speech_verbs'] for w in verbs)
        entry=any(w['lex_utf8'] in rules['entry_verbs'] for w in verbs)
        for ph in c['phrases']:
            words=ph['words']; names=[w for w in words if w['sp']=='nmpr']; nominal=[w for w in words if w['pdp'] in rules['nominal_pos']]
            deictic=[w for w in words if w['sp'] in rules['demonstrative_pos']]
            is_group=ph['function']=='Subj' and bool(nominal) and (any(w['nu']=='pl' for w in nominal) or any(w['lex_utf8'] in rules['numeral_lexemes'] for w in words))
            triggers=[]
            if names:triggers.append('OVERT_PROPER_NAME_MENTION')
            if ph['function']=='Subj' and nominal and (speech or entry):triggers.append('OVERT_NOMINAL_SPEECH_OR_ENTRY_SUBJECT')
            if is_group:triggers.append('OVERT_PLURAL_OR_NUMERAL_SUBJECT_GROUP')
            if ph['function']=='Subj' and deictic and entry:triggers.append('ANONYMOUS_DEICTIC_ENTRY')
            # Explicit addressee means an overt nominal argument in a speech clause;
            # source function is retained, not treated as a resolved semantic recipient.
            if speech and ph['function'] in rules['addressee_functions'] and nominal:triggers.append('OVERT_SPEECH_ARGUMENT')
            inventory.append(dict(clause=c['clause'],phrase=ph['node'],ref=c['ref'],function=ph['function'],surface=ph['surface'],
                                  word_nodes=[w['node'] for w in words],matched_rules=triggers,event_id='P:'+str(ph['node']) if triggers else '',
                                  audit_status='EVENT_CANDIDATE' if triggers else 'NO_PERMITTED_EXPLICIT_TRIGGER'))
            if not triggers:continue
            anonymous='ANONYMOUS_DEICTIC_ENTRY' in triggers and not nominal and not names
            key=canonical([(w['lex'],w['pdp'],w['prs_ps']) for w in words])
            role=ph['function']
            channel='SPEAKER' if speech and role=='Subj' else 'SPEECH_ARGUMENT:'+role if speech and role in rules['addressee_functions'] else 'SOURCE_FUNCTION:'+role
            prev=previous_explicit.get(channel)
            # These are changes of overt expressions in the same source function.
            # Different/same expressions are never entity inequality/equality.
            change=bool(prev and prev['expression_key']!=key)
            types=[]
            if is_group:types.append('EXPLICIT_NEW_PARTICIPANT_GROUP')
            if speech and role=='Subj' and nominal and change:types.append('EXPLICIT_SPEAKER_CHANGE')
            if speech and role in rules['addressee_functions'] and nominal and change:types.append('EXPLICIT_ADDRESSEE_CHANGE')
            if not anonymous and names and any(w['lex'] not in seen_names for w in names):types.append('EXPLICIT_NEW_PARTICIPANT')
            if not anonymous and entry and nominal:types.append('EXPLICIT_NEW_PARTICIPANT')
            if not types:types=['OTHER_EXPLICIT_SET_CHANGE']
            name_occurrences=[dict(word_node=w['node'],lexeme=w['lex'],surface=w['surface'],first_exact_lexeme_word=seen_names.get(w['lex'],w['node'])) for w in names]
            # Referential identity across occurrences is never assigned, including
            # homonymous proper names and possessors of suffixed common nouns.
            row=dict(participant_event_id='P:'+str(ph['node']),clause=c['clause'],clause_atom_ids=c['clause_atom_ids'],chapter=c['chapter'],verse=c['verse'],ref=c['ref'],
                     surface_text=c['surface'],event_type=types[0],event_types=sorted(set(types)),participant_surface=ph['surface'],participant_source_node=ph['node'],
                     participant_word_nodes=[w['node'] for w in words],identity_status='UNRESOLVED' if anonymous else 'EXPLICIT',
                     participant_identity='UNRESOLVED' if anonymous else 'OVERT_SOURCE_MENTION:'+str(ph['node']),
                     identity_scope='SOURCE_MENTION_ONLY_NOT_CROSS_OCCURRENCE_ENTITY',first_appearance_in_book_if_exact='UNRESOLVED',
                     exact_name_form_occurrences=name_occurrences,named_role='',matched_rules=triggers,source_function=role,
                     group_preserved=is_group,anonymous_entry=anonymous,previous_explicit_participant_context=deepcopy(prev) if prev else {},
                     source_provenance=dict(layer='BHSA2021',clause=c['clause'],phrase=ph['node'],word_nodes=[w['node'] for w in words],
                                            feature_hashes={Path(k).name:v for k,v in s['execution']['data_hashes'].items() if Path(k).stem in ('otype','oslots','lex','sp','pdp','function','nu','prs_ps')}),
                     human_review_status='UNREVIEWED',human_conclusion='',human_hierarchy_relation='')
            events.append(row)
            previous_explicit[channel]=dict(event_id=row['participant_event_id'],phrase=ph['node'],ref=c['ref'],expression_key=key,
                                         relation='PREVIOUS_OVERT_EXPRESSION_NOT_COREFERENCE')
            for w in names:seen_names.setdefault(w['lex'],w['node'])
    return events,inventory


def derive(s):
    events,inventory=extraction(s);atoms=s['atoms']; cfg=s['cfg42'];old=s['r41']
    byref={}
    for a,r in atoms.items():byref.setdefault(r['ref'].removeprefix('Job '),[]).append(a)
    anchors=[]
    for a in old['anchors']:
        if a['source_type']!='MR1':continue
        role='CLOSING' if a['marker_family']=='MR1_EXPLICIT_CLOSURE' else 'OPENING_CANDIDATE'
        anchors.append(dict(anchor_id=a['anchor_id'],role=role,atom_ids=a['atom_ids'],source_kind='MR1',source_locator=a['source_locator'],ref=a['ref_start']))
    for ref,role in [(r,'CLOSING') for r in cfg['ending_pair']]+[('3:1','OPENING_CANDIDATE')]:
        require(ref in byref,'human endpoint does not resolve')
        anchors.append(dict(anchor_id='HUMAN_ENDPOINT:'+ref,role=role,atom_ids=byref[ref],source_kind='HUMAN_REVIEWED_PARALLEL_ENDING_CANDIDATE' if role=='CLOSING' else 'HUMAN_REVIEWED_TRANSITION_CANDIDATE',
                            source_locator=dict(path='docs/R4_2_HUMAN_JUDGMENTS.json',role='HUMAN_ONLY'),ref='Job '+ref))
    for a in anchors:a.update(start=atoms[a['atom_ids'][0]]['index'],end=atoms[a['atom_ids'][-1]]['index'])
    frames=[]
    for start,end in cfg['candidate_frames']:
        opens=[a for a in anchors if a['ref']=='Job '+start and a['role']=='OPENING_CANDIDATE' and a['source_kind']=='MR1']
        # Endpoints explicitly supplied by human observation, not inferred pairing.
        closes=[a for a in anchors if a['anchor_id']=='HUMAN_ENDPOINT:'+end]
        require(opens and len(closes)==1,'unresolved supplied candidate frame')
        for a in opens:
            b=closes[0];frames.append(dict(frame_id='FRAME:'+a['anchor_id']+':'+b['anchor_id'],opening_anchor_id=a['anchor_id'],closing_anchor_id=b['anchor_id'],
                                         start=a['start'],end=b['end'],source='HUMAN_SUPPLIED_PAIR_NOT_DETECTED_MACRO_UNIT'))
    enclosures=[]
    for e in events:
        x=atoms[e['clause_atom_ids'][0]]['index'];y=atoms[e['clause_atom_ids'][-1]]['index']
        def nearest(role,preceding):
            pool=[a for a in anchors if a['role']==role and (a['end']<x if preceding else a['start']>y)]
            if not pool:return []
            target=(max(a['end'] for a in pool) if preceding else min(a['start'] for a in pool))
            return [a['anchor_id'] for a in pool if (a['end'] if preceding else a['start'])==target]
        po=nearest('OPENING_CANDIDATE',True);pc=nearest('CLOSING',True);fc=nearest('CLOSING',False);fo=nearest('OPENING_CANDIDATE',False)
        inside=[f for f in frames if f['start']<=x<=y<=f['end']]
        rel='INSIDE_MARKED_SPAN' if inside else 'BETWEEN_CLOSURE_AND_OPENING' if pc and fo else 'AFTER_CLOSURE' if pc else 'BEFORE_OPENING' if fo else 'UNRESOLVED'
        for frame in inside or [None]:
            enclosures.append(dict(participant_event_id=e['participant_event_id'],nearest_preceding_opening_anchor=po,nearest_preceding_closure_anchor=pc,
                nearest_following_closure_anchor=fc,nearest_following_opening_anchor=fo,inside_open_close_span=bool(frame),opening_anchor_id=frame['opening_anchor_id'] if frame else '',
                closing_anchor_id=frame['closing_anchor_id'] if frame else '',frame_id=frame['frame_id'] if frame else '',positional_relation=rel,
                source_only_notes='Positional containment in human-supplied candidate frame; not parentage. Nearest anchors are unpaired context and preserve ties.'))
    formal=old['formal'];controls=[];formal_relations=[];by_atom={}
    for f in formal:
        for a in f['atom_ids']:by_atom.setdefault(a,[]).append(f)
    for e in events:
        aa=e['clause_atom_ids'];near={f['source_event_id']:f for a in aa for f in by_atom.get(a,[])}
        for fid,f in sorted(near.items()):
            formal_relations.append(dict(participant_event_id=e['participant_event_id'],formal_id=fid,family_ids=f['family_ids'],
                positional_relations=previous.span_relations(atoms[f['atom_ids'][0]]['index'],atoms[f['atom_ids'][-1]]['index'],atoms[aa[0]]['index'],atoms[aa[-1]]['index']),
                source_locators=f['source_locators'],note='Relative to source clause span, not inferred participant scene extent.'))
    for ref in cfg['controls']:
        aa=byref.get(ref,[]);aset=set(aa)
        ff=[f for f in formal if aset.intersection(f['atom_ids'])]
        controls.append(dict(ref=ref,atom_ids=aa,event_ids=[e['participant_event_id'] for e in events if e['ref']=='Job '+ref],
            marker_ids=[a['anchor_id'] for a in old['anchors'] if a['source_type']=='MR1' and aset.intersection(a['atom_ids'])],
            formal_ids=[f['source_event_id'] for f in ff],family_ids=sorted({i for f in ff for i in f['family_ids']}),
            native_clauses=[c for c in s['native_clauses'] if c['ref']=='Job '+ref],
            human_judgment_ids=[h['id'] for h in s['human42']['judgments'] if ref in h['refs']],
            MR1_EXPLICIT_CLOSURE=any(a['marker_family']=='MR1_EXPLICIT_CLOSURE' and aset.intersection(a['atom_ids']) for a in old['anchors'])))
    left,right=[next(c for c in controls if c['ref']==r) for r in cfg['ending_pair']]
    l,r=set(left['family_ids']),set(right['family_ids']);shared=l&r
    levels={d['family_id']:d['level'] for f in formal for d in f.get('family_signature_definitions',[])}
    endings=[dict(left_ref=left['ref'],right_ref=right['ref'],shared_signature_levels=sorted({levels[f] for f in shared if f in levels}),shared_family_ids=sorted(shared),
        left_only_family_ids=sorted(l-r),right_only_family_ids=sorted(r-l),left_native_clauses=left['native_clauses'],right_native_clauses=right['native_clauses'],
        surface_relation='EXACT_SURFACES_AND_LEXEME_SETS_ONLY',shared_lexemes=sorted({w['lex'] for c in left['native_clauses'] for ph in c['phrases'] for w in ph['words']}&{w['lex'] for c in right['native_clauses'] for ph in c['phrases'] for w in ph['words']}),
        left_MR1_EXPLICIT_CLOSURE=left['MR1_EXPLICIT_CLOSURE'],right_MR1_EXPLICIT_CLOSURE=right['MR1_EXPLICIT_CLOSURE'],
        human_control_note='R42H12: HUMAN_REVIEWED_PARALLEL_ENDING_CANDIDATE; correspondence does not promote any MR1 closure.')]
    correspondences=[dict(formal_id=f['source_event_id'],atom_ids=f['atom_ids'],shared_control_families=sorted(shared&set(f['family_ids'])),
                          status='FORMAL_RECURRENCE_ONLY_NOT_AN_ENDING_DETECTION',source_locators=f['source_locators']) for f in formal if shared&set(f['family_ids'])]
    historical=[dict(event_id=r['source_event_id'],atom_ids=r['atom_ids'],historical_projection={k:r['historical_projection'].get(k,'') for k in ('speaker_canonical','speaker_source_type','implicit_context_ref')},
                     source_locator=r['provenance_locator'],identity_authority=False) for r in s['markers'] if r['family']=='MR1_CSF']
    return dict(events=events,inventory=inventory,enclosures=enclosures,endings=endings,clauses=deepcopy(s['native_clauses']),anchors=anchors,frames=frames,
                human=deepcopy(s['human42']['judgments']),controls=controls,correspondences=correspondences,sources=deepcopy(s['sources']),
                historical_speakers=historical,formal=deepcopy(formal),formal_relations=formal_relations,old_human=deepcopy(old['human']),extensions=deepcopy(old['extensions']),human_links=deepcopy(old['human_links']),way0=deepcopy(old['way0_audit']))


def reports(m,s):
    def section(ref):
        c=next(r for r in m['controls'] if r['ref']==ref)
        lines=['## Job '+ref,'Markers: '+canonical(c['marker_ids']),'Formal occurrences: '+canonical(c['formal_ids']),
               'MR1_EXPLICIT_CLOSURE = '+str(c['MR1_EXPLICIT_CLOSURE']).lower()]
        for native in c['native_clauses']:
            lines+=['Native clause '+str(native['clause'])+' / atoms '+canonical(native['clause_atom_ids'])+' / '+native['type']+': '+native['surface']]
            table=['| Phrase | Function/type | Exact surface | Word: lexeme [POS, tense, stem, person, gender, number] |',
                   '| --- | --- | --- | --- |']
            for ph in native['phrases']:
                detail='; '.join(str(w['node'])+': '+w['lex_utf8']+' ['+', '.join(str(w[k]) for k in ('sp','vt','vs','ps','gn','nu'))+']' for w in ph['words'])
                table.append('| '+str(ph['node'])+' | '+ph['function']+'/'+ph['type']+' | '+ph['surface'].replace('|','\\|')+' | '+detail.replace('|','\\|')+' |')
            lines.append('\n'.join(table))
        for e in m['events']:
            if e['participant_event_id'] not in c['event_ids']:continue
            lines+=['### '+e['participant_event_id']+' — '+e['participant_surface'],
                    'Source function/rules: '+e['source_function']+' / '+canonical(e['matched_rules']),
                    'Identity status: '+e['identity_status']+'; identity: '+e['participant_identity']+'; first appearance: '+e['first_appearance_in_book_if_exact'],
                    'Enclosure: '+canonical([r for r in m['enclosures'] if r['participant_event_id']==e['participant_event_id']]),
                    'Formal span relations (clause scope): '+canonical([dict(formal_id=r['formal_id'],relations=r['positional_relations']) for r in m['formal_relations'] if r['participant_event_id']==e['participant_event_id']])]
        lines+=['Existing human judgments (not extraction rules):']
        lines+=['> '+h['statement'] for h in m['human'] if h['id'] in c['human_judgment_ids']]
        lines+=['Human conclusion: [blank]; review status: UNREVIEWED; hierarchy relation: [blank].',
                'Unresolved: real participant-set change? scene transition? internal scene or new paragraph? what hierarchy, if any? No automatic answer.']
        return '\n\n'.join(lines)
    seq=['1:5','1:6','1:13','1:14','1:16','1:17','1:18','1:22','2:1','2:9','2:10','2:11','3:1','3:2']
    result={REPORTS[0]:'\n\n'.join(['# Job 1–3 participant audit',PRINCIPLES]+[section(r) for r in seq]),
            REPORTS[1]:'\n\n'.join(['# Wife / friends: parallel evidence, no automatic conclusion',PRINCIPLES]+[section(r) for r in ['2:1','2:9','2:10','2:11','3:1','3:2']]),
            REPORTS[2]:'\n\n'.join(['# Friends / Elihu: surrounding evidence',PRINCIPLES]+[section(r) for r in ['2:10','2:11','3:1','3:2','31:40','32:1','32:2','32:3','32:4','32:5','32:6']])}
    packet=['# Whole-book participant-transition review packet',PRINCIPLES,
            'Event inventory is uniform across the book; proper-name mentions, grammatical groups and overt speech arguments are candidates, not assumed human/animate actors. Exact source mention identity never merges referents. First appearance remains unresolved; name-form first word nodes are lexical facts only.',
            'Human hierarchy choices (blank, never auto-filled): SAME_LEVEL_SIBLING / CHILD / PARENT / CONTINUES_WITHIN / UNRESOLVED.',
            '## Source-event inventory']
    table=['| Event | Reference | Surface | Source rule | Identity |','| --- | --- | --- | --- | --- |']
    for e in m['events']:table.append('| '+ ' | '.join([e['participant_event_id'],e['ref'],e['participant_surface'].replace('|','\\|'),', '.join(e['matched_rules']),e['identity_status']])+' |')
    packet+=['\n'.join(table),'Full source coordinates/provenance and blank human fields: 01 CSV. All phrase inclusions/exclusions: 07 CSV. Full native features: 12 CSV. Enclosure links and supplied frames: 02/13/14 CSV.']
    packet+=['## Every source event: review context']
    for e in m['events']:
        eid=e['participant_event_id']
        packet+=['### Event '+eid+' — '+e['ref'],
                 'Source clause '+str(e['clause'])+' / atoms '+canonical(e['clause_atom_ids'])+': '+e['surface_text'],
                 'Overt expression: '+e['participant_surface']+'; source phrase '+str(e['participant_source_node'])+'; words '+canonical(e['participant_word_nodes']),
                 'Identity: '+e['identity_status']+' / '+e['participant_identity']+'; first appearance: '+e['first_appearance_in_book_if_exact'],
                 'Previous explicit expression, not coreference: '+canonical(e['previous_explicit_participant_context']),
                 'Enclosure positions: '+canonical([r for r in m['enclosures'] if r['participant_event_id']==eid]),
                 'Formal clause-span evidence: '+canonical([dict(formal_id=r['formal_id'],relations=r['positional_relations']) for r in m['formal_relations'] if r['participant_event_id']==eid]),
                 'Human conclusion: [blank]; review status: UNREVIEWED; hierarchy relation: [blank].']
    for ref in s['cfg42']['controls']:packet+=[section(ref)]
    packet+=['## Parallel ending audit',canonical([{k:v for k,v in e.items() if k not in ('left_native_clauses','right_native_clauses')} for e in m['endings']]),
             '3:1 surface transition remains separate from 3:2 MR1 CSF. No MR1 rule extension has been made. See native Time/Pred/Objc phrase evidence for אחרי כן / פתח איוב את פיהו.']
    result[REPORTS[3]]='\n\n'.join(packet)
    return {k:v+'\n' for k,v in result.items()}


def build(s):
    m=deepcopy(derive(s));m['reports']=reports(m,s);return m


def gates(m,s):
    expected=derive(s);eq=lambda k:m.get(k)==expected[k];cfg=s['cfg42'];checks={}
    receipt=s['receipt42'];checks['ACCEPTED_SOURCE_MANIFESTS']=bool(receipt['actual']) and receipt['actual']==receipt['expected'] and receipt['archive_sha']==cfg['r4_1']['sha256']
    checks['WHOLE_BOOK_SCOPE']=eq('inventory') and eq('clauses') and {c['clause'] for c in m['clauses']}==set(s['clauses'])
    checks['EXPLICIT_RULES_DOCUMENTED']=s['rules_receipt']==sha(canonical(cfg['rules']).encode())
    checks['NO_SEMANTIC_INVENTION']=eq('events') and all(not e['named_role'] for e in m['events'])
    controls=cfg['control_expectations']
    select=lambda rows,ref:[e for e in rows if e['ref']=='Job '+ref]
    for key,ref in [('EXPLICIT_MESSENGER',controls['explicit_entry']),('WIFE',controls['wife']),('FRIENDS_GROUP',controls['friends']),('ELIHU',controls['elihu'])]:
        current=select(m['events'],ref);truth=select(expected['events'],ref)
        checks[key+'_RESOLVED']=bool(current) and current==truth
    checks['ANONYMOUS_ENTRIES_RETAINED']=all(any(e['anonymous_entry'] for e in select(m['events'],ref)) and select(m['events'],ref)==select(expected['events'],ref) for ref in controls['anonymous_entries'])
    checks['UNRESOLVED_EVENT_NOT_DELETED']=eq('events') and sum(e['anonymous_entry'] for e in m['events'])==sum(e['anonymous_entry'] for e in expected['events'])
    checks['HISTORICAL_IMPLICIT_NOT_IDENTITY']=eq('historical_speakers') and eq('events') and all(not r['identity_authority'] for r in m['historical_speakers'])
    checks['NO_FORCED_MESSENGER_IDENTITIES']=all(e['participant_identity']=='UNRESOLVED' and e['named_role']=='' for e in m['events'] if e['anonymous_entry'])
    checks['FIRST_APPEARANCE_UNRESOLVED']=all(e['first_appearance_in_book_if_exact']=='UNRESOLVED' for e in m['events'])
    checks['HUMAN_CONTROL_SEPARATE']=eq('human') and eq('old_human') and eq('extensions') and eq('human_links')
    checks['UNIFORM_EXTRACTION_RULE']=eq('events') and eq('inventory')
    checks['SOURCE_ATOM_MAPPING']=eq('events') and all(e['clause_atom_ids']==s['clauses'][e['clause']] for e in m['events'])
    checks['ENCLOSURE_LINKS']=eq('enclosures') and eq('frames') and eq('anchors')
    checks['FORMAL_SPAN_RELATIONS']=eq('formal_relations') and eq('formal')
    checks['WIFE_ENCLOSED']=eq('enclosures') and any(r['inside_open_close_span'] and r['closing_anchor_id']=='HUMAN_ENDPOINT:2:10' for r in m['enclosures'] if r['participant_event_id'] in {e['participant_event_id'] for e in select(m['events'],controls['wife'])})
    checks['MESSENGERS_ENCLOSED']=eq('enclosures') and all(any(r['closing_anchor_id']=='HUMAN_ENDPOINT:1:22' for r in m['enclosures'] if r['participant_event_id'] in {e['participant_event_id'] for e in select(m['events'],ref)}) for ref in [controls['explicit_entry']]+controls['anonymous_entries'])
    checks['ENDING_COMPARISON_RETAINED']=eq('endings') and eq('correspondences')
    checks['MR1_CLOSURES_UNCHANGED']=eq('anchors') and eq('controls') and not any(r['left_MR1_EXPLICIT_CLOSURE'] or r['right_MR1_EXPLICIT_CLOSURE'] for r in m['endings'])
    checks['GAP_3_1_RETAINED']=eq('controls') and any(c['ref']==controls['gap'] and c['native_clauses'] and not c['marker_ids'] for c in m['controls'])
    checks['CSF_3_2_SEPARATE']=eq('controls') and any(c['ref']==controls['csf'] and c['marker_ids'] for c in m['controls'])
    checks['HUMAN_FIELDS_BLANK']=all(e['human_review_status']=='UNREVIEWED' and not e['human_hierarchy_relation'] and not e['human_conclusion'] for e in m['events'])
    for name,fields in [('NO_HIERARCHY',{'parent_id','parent','hierarchy_edge','macro_level'}),('NO_SCORE_RANK',{'score','rank','ranking'}),('NO_INTERPRETIVE_LABELS',{'rhetorical_label','theological_label','literary_role'})]:
        checks[name]=all(not fields.intersection(e) for e in m['events']+m['enclosures'])
    checks['REPORTS_SOURCE_GROUNDED']=m['reports']==reports(expected,s)
    checks['DETERMINISTIC_REPLAY']=all(eq(k) for k in TABLES)
    return [dict(gate=k,status='PASS' if v else 'FAIL') for k,v in checks.items()]


def serialize(m,s):
    gg=gates(m,s);require(all(g['status']=='PASS' for g in gg),'R4.2 gates failed: '+canonical([g for g in gg if g['status']!='PASS']))
    files={n:util.csv_bytes(m[k]) for k,n in TABLES.items()};files.update({n:v.encode() for n,v in m['reports'].items()})
    files['25_method_note.md']=(ROOT/'docs/R4_2_SPEC.md').read_bytes()
    files['26_human_judgments.json']=util.json_bytes(s['human42'])
    files['90_run_metadata.json']=util.json_bytes(dict(version='R4.2',mode=s['mode'],status='PASS',config=s['cfg42'],bhsa=s['execution'],
        counts={k:len(m[k]) for k in TABLES},event_type_counts=dict(Counter(e['event_type'] for e in m['events'])),identity_counts=dict(Counter(e['identity_status'] for e in m['events'])),
        enclosure_counts=dict(Counter(e['positional_relation'] for e in m['enclosures'])),gate_count=len(gg)+1,code_sha256=sha(Path(__file__).read_bytes())))
    def seal():
        files.pop('99_manifest_sha256.csv',None);files['99_manifest_sha256.csv']=util.csv_bytes([dict(file=n,sha256=sha(b)) for n,b in sorted(files.items())])
    seal();gg.append(util.manifest_gate(files));files['11_gates.csv']=util.csv_bytes(gg);seal();require(util.manifest_ok(files),'manifest failure');return files


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--out',required=True);parser.add_argument('--tf-data');parser.add_argument('--self-test',action='store_true');args=parser.parse_args(argv)
    if args.self_test:
        from milal_r4_2_synthetic import source
        s=source()
    else:
        if not args.tf_data:parser.error('--tf-data required')
        s=load(args.tf_data)
    s['rules_receipt']=sha(canonical(s['cfg42']['rules']).encode())
    files=serialize(build(s),s)
    if not args.self_test:
        for r in s['sources']:require(sha(Path(r['path_archive']).read_bytes())==r['SHA256'],'source changed')
    previous.publish(files,args.out)
    # The inherited format-generic publisher writes a version-specific log label.
    log=Path(args.out).resolve().with_name(Path(args.out).name+'_run.log');log.write_text(log.read_text(encoding='utf-8').replace('R4.1 PASS','R4.2 PASS'),encoding='utf-8')
    print('R4.2 PASS '+str(Path(args.out).resolve()));return 0


if __name__=='__main__':
    try:sys.exit(main())
    except (ValueError,OSError) as exc:print(str(exc),file=sys.stderr);sys.exit(2)
