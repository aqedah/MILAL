"""Compositional configuration binding, separate from family membership."""
from milal_q1_binding import identity,witness,qualify
from milal_q12_profiles import compare_dimensions,nominal_anchors,INDEPENDENT


def frame_witness(left,right,kind):
    key='temporal_adjuncts' if kind=='TEMPORAL' else 'locative_adjuncts'
    result=[]
    for a in left[key]:
        for b in right[key]:
            shared=sorted({n['lex'] for n in a['nominals'] if n['sp'] in ('subs','nmpr')} &
                          {n['lex'] for n in b['nominals'] if n['sp'] in ('subs','nmpr')})
            if not shared or a['function']!=b['function']:continue
            result.append(dict(kind=kind+'_FRAME_CORRESPONDENCE',source_frame=a,target_frame=b,
                shared_structural_basis=dict(grammatical_function=a['function'],explicit_nominal_anchors=shared),
                formal_difference=dict(source_lexemes=a['lexemes'],target_lexemes=b['lexemes'],
                    source_phrase_type=a['typ'],target_phrase_type=b['typ']),
                provenance=[left['profile_id'],right['profile_id']],referential_frame_identity='UNRESOLVED'))
    return result


def pair_anchors(left,right):
    lexical=[dict(kind='EXPLICIT_LEXICAL_ANCHOR_IN_CORRESPONDING_GRAMMATICAL_ROLE',
        grammatical_function=function,lexeme=lex,provenance=[left['profile_id'],right['profile_id']],
        referential_identity='UNRESOLVED') for function,lex in sorted(nominal_anchors(left)&nominal_anchors(right))]
    return lexical+frame_witness(left,right,'TEMPORAL')+frame_witness(left,right,'LOCATIVE')


def compare_configurations(index,left_root,right_root,source,target):
    a,b=index.configurations[left_root],index.configurations[right_root]
    if source not in a['members'] or target not in b['members']:raise ValueError('position identity missing')
    same=a['family_id']==b['family_id']
    mapping=[dict(source_clause_id=x,target_clause_id=y,source_position=a['positions'][i],target_position=b['positions'][i])
             for i,(x,y) in enumerate(zip(a['members'],b['members']))] if same else []
    positional=any(m['source_clause_id']==source and m['target_clause_id']==target for m in mapping)
    independent=a['configuration_independence_status'] in INDEPENDENT and b['configuration_independence_status'] in INDEPENDENT
    # Overlapping configurations cannot cite the tested edge as their own unit.
    independent &= not (set(a['members'])&set(b['members']))
    anchors=[]
    for m in mapping:
        anchors.extend(pair_anchors(index.profiles[m['source_clause_id']],index.profiles[m['target_clause_id']]))
    # Structural content must exceed clause-type equality and an isolated word.
    structural=bool(len(a['members'])>1 and len(b['members'])>1 or
        any(index.profiles[n]['temporal_adjuncts'] or index.profiles[n]['locative_adjuncts'] or
            index.profiles[n]['subordinate_markers'] for n in a['members']) and
        any(index.profiles[n]['temporal_adjuncts'] or index.profiles[n]['locative_adjuncts'] or
            index.profiles[n]['subordinate_markers'] for n in b['members']))
    dimensions=compare_dimensions(index.profiles[source],index.profiles[target])
    dimensions['LOCAL_CLAUSE_SEQUENCE']=dict(status='EXACT' if same else 'DIFFERENT',
        source_observation=a['generalized_configuration_pattern'],target_observation=b['generalized_configuration_pattern'],
        shared_configuration_basis=a['family_id'] if same else '',
        difference='' if same else dict(source=a['family_id'],target=b['family_id']),
        provenance=[a['configuration_id'],b['configuration_id']])
    qualified=bool(same and independent and positional and structural and anchors)
    record=dict(source_id=source,target_id=target,configuration_A=a['configuration_id'],configuration_B=b['configuration_id'],
        family_id=a['family_id'] if same else '',same_configuration_family=same,
        configuration_independence_status='INDEPENDENT_SURFACE' if independent else 'DEPENDENT_ON_TESTED_RELATION',
        position_mapping=mapping,pair_binding_witnesses=anchors,correspondence_dimensions=dimensions,
        structural_information_beyond_clause_type=structural,
        matched_surface_features=[k for k,v in dimensions.items() if v['status'] in ('EXACT','CORRESPONDING_VARIANT')],
        nonmatched_surface_features=[k for k,v in dimensions.items() if v['status'] not in ('EXACT','CORRESPONDING_VARIANT','NOT_APPLICABLE')],
        positive_source_binding=qualified,status='QUALIFIED_CONFIGURATION_WITNESS' if qualified else 'SAME_CONFIGURATION_FAMILY' if same else 'DIFFERENT_CONFIGURATION',
        textual_level='UNRESOLVED',provenance='INDEPENDENT_PROFILES_AND_LOCAL_SOURCE_CONSTRUCTIONS')
    record['correspondence_id']='CC-'+identity(record)
    return record


class BindingIndex:
    def __init__(self,configurations,references,native):
        self.configurations=configurations;self.references=references;self.native=native

    def correspondences(self,source,target):
        result=[]
        for left,lp in self.configurations.memberships[source]:
            for right,rp in self.configurations.memberships[target]:
                if lp!=rp:continue
                a,b=self.configurations.configurations[left],self.configurations.configurations[right]
                if a['family_id']!=b['family_id']:continue
                result.append(compare_configurations(self.configurations,left,right,source,target))
        return result

    def evaluate(self,source,target,matches,deferred=False):
        source,target=str(source),str(target)
        # Q1's SB06 witness is replaced only in the new derived Q1.2 layer.
        ws=[w for w in self.native.bindings(source,target) if w['mechanism']!='SB06']
        correspondence=self.correspondences(source,target)
        for c in correspondence:
            if not c['positive_source_binding']:continue
            mechanism='SB06' if c['position_mapping'][0]['source_clause_id']==source and c['position_mapping'][0]['target_clause_id']==target else 'SB11'
            ws.append(witness(mechanism,'CONFIGURATION_BINDING',source,target,c,['PARATACTIC'],
                independent_correspondence_and_same_line=True,intervening_context_status='SOURCE_CONFIGURATION_POSITION_CANDIDATE; NOT_FINAL_LEVEL'))
        reference=self.references.bindings(source,target)
        for r in reference:ws.append(witness(r['mechanism'],'UNIT_MEDIATED_BINDING' if r['mechanism']=='SB03' else 'DIRECT_BINDING',
            source,target,r,['HYPOTACTIC'],intervening_context_status='INDEPENDENT_EXACT_REFERENCE'))
        result=qualify(source,target,matches,ws,deferred=deferred)
        if deferred:result['disqualification_reason']='RELATION_DEFERRED_PENDING_CLAUSE_BINDING'
        return dict(**result,witnesses=ws,correspondences=correspondence,reference_bindings=reference)
