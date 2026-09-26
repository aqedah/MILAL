"""Independent, node-preserving surface profiles and bounded configurations.

No candidate edges, variant graph, human decisions or control identifiers enter
this module. Family membership describes construction form, never textual level.
"""
from collections import defaultdict
from milal_q1_binding import identity

DIMENSIONS = ('CLAUSE_TYPE','PREDICATE_MORPHOLOGY','CONSTITUENT_STRUCTURE',
    'PHRASE_ARRANGEMENT','SUBJECT_CONFIGURATION','COMPLEMENT_CONFIGURATION',
    'LOCATION_CONFIGURATION','TIME_CONFIGURATION','PARTICIPANT_CONFIGURATION',
    'REFERENCE_MORPHOLOGY','LEXICAL_ANCHOR','SPEECH_FORMULA','SUBORDINATION_PATTERN',
    'LOCAL_CLAUSE_SEQUENCE')
INDEPENDENT = ('INDEPENDENT_SURFACE','INDEPENDENT_VALENCY')
NP_FUNCTIONS = ('Subj','PreS','Objc','PreO','Cmpl','PreC')


def valid(value):
    return value not in (None,'','NA','unknown')


def profile(row, lexicons):
    for key in ('clause_id','clause_atom_ids','word_ids','clause_type','WORD','PHRASE','CLAUSE','REFERENCE'):
        if key not in row:raise ValueError('required profile source field: '+key)
    words=row['WORD'];phrases=row['PHRASE'];wm={w['node']:w for w in words}
    if set(wm)!=set(row['word_ids']) or not words:raise ValueError('word identity mismatch')
    verbs=[w for w in words if w['sp']=='verb']
    first_pred=min((w['node'] for w in verbs),default=None)
    def phrase_records(functions):
        return [dict(node=p['node'],function=p['function'],typ=p['typ'],word_ids=p['word_ids'],
            lexemes=[wm[n]['lex'] for n in p['word_ids']],
            nominals=[dict(node=n,lex=wm[n]['lex'],sp=wm[n]['sp'],
                ps=wm[n].get('ps'),gn=wm[n].get('gn'),nu=wm[n].get('nu'))
                for n in p['word_ids'] if wm[n]['sp'] in ('subs','nmpr','prps','prde')])
            for p in phrases if p['function'] in functions]
    speech=[dict(node=w['node'],lex=w['lex']) for w in verbs if w['lex'] in lexicons['speech']]
    lexical=[dict(node=w['node'],lex=w['lex'],sp=w['sp']) for w in words if w['sp'] not in ('prep','conj','art','nega')]
    result=dict(clause_id=str(row['clause_id']),clause_atom_ids=row['clause_atom_ids'],word_ids=row['word_ids'],
        clause_type=row['clause_type'],predicate_morphology=[dict(node=w['node'],lex=w['lex'],
            vt=w['vt'],vs=w['vs'],ps=w.get('ps'),gn=w.get('gn'),nu=w.get('nu')) for w in verbs],
        conjunction_syndesis=[dict(node=w['node'],lex=w['lex']) for w in words if w['sp']=='conj'],
        explicit_subject_presence=any(p['function'] in ('Subj','PreS') for p in phrases),
        subject_configuration=phrase_records(('Subj','PreS')),
        complement_structure=phrase_records(('Objc','PreO','Cmpl','PreC')),
        phrase_function_sequence=[p['function'] for p in phrases],phrase_type_sequence=[p['typ'] for p in phrases],
        pre_predicate_constituents=[dict(node=p['node'],function=p['function'],typ=p['typ']) for p in phrases
            if first_pred is not None and max(p['word_ids'])<first_pred],
        locative_adjuncts=phrase_records(('Loca',)),temporal_adjuncts=phrase_records(('Time',)),
        participant_grammatical_roles=phrase_records(NP_FUNCTIONS),
        speaker_addressee_structure=dict(speech_predicate_nodes=[s['node'] for s in speech],
            subject_phrase_nodes=[p['node'] for p in phrases if p['function'] in ('Subj','PreS')],
            complement_phrase_nodes=[p['node'] for p in phrases if p['function'] in ('Cmpl','PreC')],
            status='SURFACE_GRAMMATICAL_ROLES_ONLY; REFERENTIAL_IDENTITY_UNRESOLVED'),
        lexical_anchors=lexical,reference_morphology=row['REFERENCE']['mentions'],
        subordinate_markers=[dict(node=w['node'],lex=w['lex']) for w in words if w['lex'] in lexicons['subordinators']],
        direct_speech_markers=speech,native_annotations=row['CLAUSE']['native_annotations'],
        configuration_independence_status='INDEPENDENT_SURFACE',
        derivation_provenance=dict(source='FROZEN_BHSA_MILAL_OBSERVATION',source_row_sha256=identity(row)),
        referential_identity='UNRESOLVED',textual_level='UNRESOLVED')
    result['profile_id']='CP-'+identity(result)
    return result


def nominal_anchors(p):
    return {(r['function'],n['lex']) for r in p['participant_grammatical_roles']
            for n in r['nominals'] if n['sp'] in ('subs','nmpr')}


def core_shape(p, speech):
    """A compositional family key, not a complete signature or a score."""
    return dict(clause_type=p['clause_type'],
        predicates=[dict(predicate_class='SPEECH' if v['lex'] in speech else 'NON_SPEECH',
                         vt=v['vt'],vs=v['vs']) for v in p['predicate_morphology']],
        core_phrase_functions=[f for f in p['phrase_function_sequence'] if f not in ('Time','Loca')],
        subordinate_marker_lexemes=[m['lex'] for m in p['subordinate_markers']])


class ConfigurationIndex:
    def __init__(self, inventory, lexicons):
        self.rows={str(r['clause_id']):r for r in inventory}
        self.order=sorted(self.rows,key=lambda k:int(self.rows[k]['position']))
        self.positions={k:i for i,k in enumerate(self.order)}
        self.lexicons=lexicons
        self.profiles={k:profile(self.rows[k],lexicons) for k in self.order}
        self.owner=defaultdict(set)
        for k,r in self.rows.items():
            for node in [int(k),*r['clause_atom_ids'],*r['word_ids'],*(p['node'] for p in r['PHRASE'])]:self.owner[node].add(k)
        self.configurations={k:self.configuration(k) for k in self.order}
        self.memberships=defaultdict(list)
        for root,c in self.configurations.items():
            for offset,k in enumerate(c['members']):self.memberships[k].append((root,offset))
        self.families={}
        for c in self.configurations.values():
            family=self.families.setdefault(c['family_id'],dict(family_id=c['family_id'],
                family_definition=c['generalized_configuration_pattern'],required_surface_fields=['clause_type','predicate_morphology','core_phrase_functions','subordination_pattern'],
                optional_surface_fields=['temporal_adjuncts','locative_adjuncts','explicit_nominal_realization'],
                prohibited_confusions=['SAME_FAMILY_IS_NOT_SAME_LEVEL','BARE_SPEECH_REPETITION_IS_NOT_BINDING','PNG_IS_NOT_COREFERENCE'],
                derivation_provenance='DATA_DERIVED_CORE_SHAPES_FROM_INDEPENDENT_SURFACE_CONFIGURATIONS',
                configuration_ids=[]))
            family['configuration_ids'].append(c['configuration_id'])

    def configuration(self,root):
        members=[root];links=[]
        for target in self.order[self.positions[root]+1:]:
            previous=self.rows[members[-1]];r=self.rows[target]
            if max(previous['word_ids'])+1!=min(r['word_ids']):break
            exact=[e for e in r['CLAUSE']['native_annotations']
                if e['resolution']=='EXACT_NODE_MEMBERSHIP' and self.owner[int(e['head_node'])]&set(members)
                and target in self.owner[int(e['dependent_node'])]
                and (e['rela'] in self.lexicons['subordinate_rela'] or
                     r['clause_type']=='InfC' and self.profiles[target]['direct_speech_markers'])]
            if not exact:break
            members.append(target);links.extend(exact)
        observed=[self.profiles[k]['profile_id'] for k in members]
        generalized=[core_shape(self.profiles[k],self.lexicons['speech']) for k in members]
        positions=[dict(clause_id=k,offset=i,position='OPENING_POSITION' if i==0 else 'EMBEDDED_POSITION',
                        basis='OBSERVABLE_LOCAL_SEQUENCE_WITH_EXACT_NATIVE_SUBORDINATION_OR_SPEECH_COMPLEMENT') for i,k in enumerate(members)]
        record=dict(opening_clause_id=root,members=members,observed_configuration=observed,
            generalized_configuration_pattern=generalized,family_id='CF-'+identity(generalized),
            positions=positions,source_links=links,span_boundary='STOP_AT_WORD_GAP_OR_FIRST_UNBOUND_CONTINUATION',
            configuration_independence_status='INDEPENDENT_SURFACE',
            unit_membership_basis='EXACT_NATIVE_AND_SURFACE_ADJACENCY; NOT_PROVISIONAL_RELATION_REACHABILITY')
        record['configuration_id']='SC-'+identity(record)
        return record


def dimension_values(p):
    def structure(items):return [dict(function=r['function'],typ=r['typ'],lexemes=r['lexemes']) for r in items]
    return dict(CLAUSE_TYPE=p['clause_type'],PREDICATE_MORPHOLOGY=[{k:v for k,v in r.items() if k!='node'} for r in p['predicate_morphology']],
        CONSTITUENT_STRUCTURE=p['phrase_type_sequence'],PHRASE_ARRANGEMENT=p['phrase_function_sequence'],
        SUBJECT_CONFIGURATION=structure(p['subject_configuration']),COMPLEMENT_CONFIGURATION=structure(p['complement_structure']),
        LOCATION_CONFIGURATION=structure(p['locative_adjuncts']),TIME_CONFIGURATION=structure(p['temporal_adjuncts']),
        PARTICIPANT_CONFIGURATION=structure(p['participant_grammatical_roles']),
        REFERENCE_MORPHOLOGY=[{k:v for k,v in r.items() if k not in ('node','identity')} for r in p['reference_morphology']],
        LEXICAL_ANCHOR=[(r['sp'],r['lex']) for r in p['lexical_anchors']],SPEECH_FORMULA=[r['lex'] for r in p['direct_speech_markers']],
        SUBORDINATION_PATTERN=[r['lex'] for r in p['subordinate_markers']])


def compare_dimensions(a,b):
    left,right=dimension_values(a),dimension_values(b);result={}
    for key in left:
        x,y=left[key],right[key]
        status='NOT_APPLICABLE' if not x and not y else 'EXACT' if x==y else 'DIFFERENT'
        basis=''
        if x!=y and key in ('TIME_CONFIGURATION','LOCATION_CONFIGURATION'):
            status='CORRESPONDING_VARIANT';basis='OPTIONAL_OR_REPEATED_SURFACE_ADJUNCT_WITH_SAME_NAMED_PHRASE_FUNCTION'
        if x!=y and key=='PHRASE_ARRANGEMENT' and [v for v in x if v not in ('Time','Loca')]==[v for v in y if v not in ('Time','Loca')]:
            status='CORRESPONDING_VARIANT';basis='SAME_CORE_PHRASE_ORDER_WITH_EXPLICIT_TIME_LOCATION_DIFFERENCE'
        result[key]=dict(status=status,source_observation=x,target_observation=y,shared_configuration_basis=basis,
            difference='' if x==y else dict(source=x,target=y),provenance=[a['profile_id'],b['profile_id']])
    return result
