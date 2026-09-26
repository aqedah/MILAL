"""Independent local surface constructions; no relation graph enters discovery."""
from collections import defaultdict
from milal_q1_binding import identity
from milal_q12_profiles import profile,core_shape

INDEPENDENT={'INDEPENDENT_NATIVE_BINDING','INDEPENDENT_SURFACE_SEQUENCE','INDEPENDENT_VALENCY',
    'INDEPENDENT_EXPLICIT_MARKER','MULTIPLE_INDEPENDENT_WITNESSES'}


def finite(p):
    return any(v['vt'] not in ('infc','infa','ptca','ptcp','NA','',None) for v in p['predicate_morphology'])


class SurfaceSpans:
    def __init__(self,inventory,lexicons):
        self.lexicons=lexicons;self.rows={str(r['clause_id']):r for r in inventory}
        if len(self.rows)!=len(inventory):raise ValueError('duplicate source clause')
        self.order=sorted(self.rows,key=lambda k:int(self.rows[k]['position']))
        self.positions={k:i for i,k in enumerate(self.order)}
        self.profiles={k:profile(self.rows[k],lexicons) for k in self.order}
        # Q1.2 participant-role subsets remain frozen. Composite lexical-role
        # evidence also preserves native adjuncts and other observed functions.
        self.role_phrases={}
        for k,row in self.rows.items():
            wm={w['node']:w for w in row['WORD']}
            self.role_phrases[k]=[dict(node=p['node'],function=p['function'],typ=p['typ'],word_ids=p['word_ids'],
                lexemes=[wm[n]['lex'] for n in p['word_ids']],nominals=[dict(node=n,lex=wm[n]['lex'],sp=wm[n]['sp']) for n in p['word_ids'] if wm[n]['sp'] in ('subs','nmpr','prps','prde')],
                semantic_frame_type='UNRESOLVED_NATIVE_ADJUNCT' if p['function']=='Adju' else 'NATIVE_'+p['function']) for p in row['PHRASE']]
        self.owners=defaultdict(set)
        for k,r in self.rows.items():
            for n in [int(k),*r['clause_atom_ids'],*r['word_ids'],*(p['node'] for p in r['PHRASE'])]:self.owners[n].add(k)
        self.spans={};self.memberships=defaultdict(list);self.composites={};self.families={}
        for root in self.order:
            members=[root];links=[]
            for target in self.order[self.positions[root]+1:]:
                found=self.local_links(members,target)
                if not found:break
                independent=[x for x in found if x['independence_status'] in INDEPENDENT]
                if not independent:
                    self.add_span(members+[target],links+found,'DEPENDENT_ON_TESTED_RELATION' if any(x['independence_status']=='DEPENDENT_ON_TESTED_RELATION' for x in found) else 'UNRESOLVED')
                    break
                members.append(target);links+=independent
                self.add_span(members[:],links[:],'INDEPENDENT_NATIVE_BINDING')
        for span in self.spans.values():
            span['overlapping_span_ids']=sorted(s['span_id'] for s in self.spans.values() if s['span_id']!=span['span_id'] and set(s['clause_ids'])&set(span['clause_ids']))

    def local_links(self,members,target):
        previous=self.rows[members[-1]];row=self.rows[target];p=self.profiles[target]
        if previous['book']!=row['book'] or max(previous['word_ids'])+1!=min(row['word_ids']):return []
        found=[]
        for e in row['CLAUSE']['native_annotations']:
            heads=self.owners[int(e['head_node'])]&set(members)
            if target not in self.owners[int(e['dependent_node'])] or not heads:continue
            # NA/Coor is not itself subordination. A local nonfinite attachment or
            # explicit speech continuation must also be observable.
            nonfinite=p['clause_type'] in ('InfC','InfA') or any(v['vt'] in ('infc','infa') for v in p['predicate_morphology'])
            subordinate=e['rela'] in self.lexicons['subordinate_rela']
            speech=bool(p['direct_speech_markers']) and any(self.profiles[h]['direct_speech_markers'] or
                self.profiles[h]['clause_type'] in ('InfC','InfA') for h in members)
            if not (nonfinite or subordinate or speech):continue
            status=('DEPENDENT_ON_TESTED_RELATION' if e.get('status')!='DATABASE_EXISTING_RELATION' else
                'UNRESOLVED' if e['resolution']!='EXACT_NODE_MEMBERSHIP' or len(heads)!=1 else 'INDEPENDENT_NATIVE_BINDING')
            found.append(dict(source_clause_id=sorted(heads)[0] if len(heads)==1 else '',possible_head_ids=sorted(heads),
                target_clause_id=target,basis='NATIVE_NONFINITE_ATTACHMENT' if nonfinite else 'NATIVE_TYPED_SUBORDINATION' if subordinate else 'NATIVE_EXPLICIT_SPEECH_CONTINUATION',
                independence_status=status,native_annotation=e,source_profile_ids=[self.profiles[h]['profile_id'] for h in sorted(heads)]+[p['profile_id']]))
        return found

    def roles(self,k,index):
        p=self.profiles[k];roles=[]
        if index==0 and finite(p):roles.append('INITIAL_FINITE')
        if p['clause_type'] in ('InfC','InfA'):roles.append('DEPENDENT_INFINITIVE')
        if p['direct_speech_markers']:roles.append('INITIAL_SPEECH_PREDICATE' if index==0 else 'FOLLOWING_SPEECH_PREDICATE')
        if p['temporal_adjuncts']:roles.append('TEMPORAL_FRAME_COMPONENT')
        if p['locative_adjuncts']:roles.append('LOCATIVE_FRAME_COMPONENT')
        if p['subordinate_markers']:roles.append('EXPLICIT_SUBORDINATE_COMPONENT')
        return roles or ['SURFACE_COMPONENT']

    def add_span(self,members,links,status):
        sid='SS-'+identity(dict(members=members,links=links,status=status))
        if sid in self.spans:return
        positions=[dict(position='POSITION_'+str(i+1),offset=i,clause_id=k,component_profile_id=self.profiles[k]['profile_id'],
            formal_roles=self.roles(k,i)) for i,k in enumerate(members)]
        boundary=dict(start=dict(status='OBSERVED_LOCAL_COMPONENT_START',clause_id=members[0]),
            end=dict(status='LOCAL_ATTACHMENT_SUBCONSTRUCTION_COMPLETE',clause_id=members[-1]),
            extent_basis='CONTIGUOUS_WORDS_AND_RECORDED_LOCAL_ATTACHMENT; NOT_FINAL_TEXTUAL_EXTENT',internal_links=links)
        span=dict(span_id=sid,start_clause=members[0],end_clause=members[-1],clause_ids=members,
            clause_atom_ids=[a for k in members for a in self.rows[k]['clause_atom_ids']],
            boundary_start_status=boundary['start']['status'],boundary_end_status=boundary['end']['status'],boundary_witnesses=boundary,
            construction_independence_status=status,overlapping_span_ids=[],anchor_clause_candidates=[dict(span_id=sid,
                anchor_clause_id=k,anchor_basis='INITIAL_FINITE_COMPONENT' if i==0 and finite(self.profiles[k]) else
                'EXPLICIT_MARKER_COMPONENT' if self.profiles[k]['direct_speech_markers'] else 'NATIVE_HEAD_COMPONENT' if any(e['source_clause_id']==k for e in links) else 'UNRESOLVED') for i,k in enumerate(members)])
        self.spans[sid]=span
        for k in members:self.memberships[k].append(sid)
        if status not in INDEPENDENT:return
        pattern=[dict(source_position=members.index(e['source_clause_id']),target_position=members.index(e['target_clause_id']),
            native_relation=e['native_annotation']['rela'],basis=e['basis']) for e in links]
        shapes=[core_shape(self.profiles[k],self.lexicons['speech']) for k in members]
        template=dict(component_shapes=shapes,internal_dependency_pattern=pattern)
        fid='CCF-'+identity(template)
        cps=[self.profiles[k] for k in members]
        record=dict(span_id=sid,composite_family_id=fid,object_type='COMPOSITE_SURFACE_PROFILE',
            ordered_clause_types=[p['clause_type'] for p in cps],ordered_predicate_lexemes=[[v['lex'] for v in p['predicate_morphology']] for p in cps],
            ordered_verbal_forms=[[v['vt'] for v in p['predicate_morphology']] for p in cps],internal_dependency_pattern=pattern,
            phrase_function_patterns=[p['phrase_function_sequence'] for p in cps],explicit_subject_configuration=[p['subject_configuration'] for p in cps],
            complement_configuration=[p['complement_structure'] for p in cps],speech_predicate_configuration=[p['direct_speech_markers'] for p in cps],
            subordinate_construction=[p['subordinate_markers'] for p in cps],participant_grammatical_roles=[p['participant_grammatical_roles'] for p in cps],
            lexical_anchors_by_role=[self.role_phrases[k] for k in members],time_frame=[p['temporal_adjuncts'] for p in cps],
            adjunct_frame=[[r for r in self.role_phrases[k] if r['function']=='Adju'] for k in members],
            location_frame=[p['locative_adjuncts'] for p in cps],direct_speech_marking=[p['direct_speech_markers'] for p in cps],
            conjunction_syndesis=[p['conjunction_syndesis'] for p in cps],internal_position_structure=positions,
            component_profile_ids=[p['profile_id'] for p in cps],provenance=[p['derivation_provenance'] for p in cps])
        record['composite_profile_id']='CSP-'+identity(record);self.composites[sid]=record
        family=self.families.setdefault(fid,dict(composite_family_id=fid,component_count_or_structure=len(members),ordered_structural_template=template,
            required_fields=['component_shapes','internal_dependency_pattern'],variant_fields=['explicit_lexical_realization','time_frame','location_frame'],
            provenance='DATA_DERIVED_FROM_INDEPENDENT_SURFACE_PROFILES',span_ids=[]))
        family['span_ids'].append(sid)

    def membership_rows(self):
        for s in self.spans.values():
            for k in s['clause_ids']:
                for a in self.rows[k]['clause_atom_ids']:
                    yield dict(span_id=s['span_id'],member_clause_id=k,member_clause_atom_id=a,membership_basis='OBSERVED_LOCAL_CONSTRUCTION',
                        independence_status=s['construction_independence_status'],provenance=s['boundary_witnesses'])
