"""Composite extension of SB06/SB11; relation grammar and reference remain separate."""
from collections import defaultdict
from milal_q1_binding import identity,witness,qualify
from milal_q12_profiles import core_shape,nominal_anchors
from milal_q12_binding import frame_witness
from milal_q14_spans import INDEPENDENT


def non_generic_nominals(index,p):
    # A proper participant name is participant evidence in any role, never
    # the extra non-generic lexical anchor required by the contract.
    return {(r['function'],n['lex']) for r in index.role_phrases[p['clause_id']] for n in r['nominals']
        if r['function'] not in ('Subj','PreS') and n['sp']=='subs' and n['lex'] not in index.lexicons.get('speech_nouns',[])}


def bare_formula(index,span):
    ps=[index.profiles[k] for k in span['clause_ids']]
    return bool(any(p['direct_speech_markers'] for p in ps) and all(
        all(v['lex'] in index.lexicons['speech'] for v in p['predicate_morphology']) and
        not p['temporal_adjuncts'] and not p['locative_adjuncts'] and not p['subordinate_markers'] and
        not non_generic_nominals(index,p) for p in ps))


def position_mapping(index,a,b):
    ca,cb=index.composites[a['span_id']],index.composites[b['span_id']]
    same=ca['composite_family_id']==cb['composite_family_id'];mapping=[]
    for i,x in enumerate(a['clause_ids']):
        for j,y in enumerate(b['clause_ids']):
            if same and i!=j:continue
            p,q=index.profiles[x],index.profiles[y];ra=set(index.roles(x,i));rb=set(index.roles(y,j))
            if not same:
                # Initial positions never match noninitial positions. Interior formal
                # roles retain all mappings; ambiguous alternatives are not ranked.
                if (i==0)!=(j==0):continue
                common=(ra&rb)-{'SURFACE_COMPONENT'}
                if not common:continue
            exact=core_shape(p,index.lexicons['speech'])==core_shape(q,index.lexicons['speech'])
            basis='EXACT_COMPONENT_CONFIGURATION' if exact else 'DIRECT_SPEECH_POSITION_CORRESPONDENCE' if p['direct_speech_markers'] and q['direct_speech_markers'] else 'DEPENDENCY_POSITION_CORRESPONDENCE'
            mapping.append(dict(source_span=a['span_id'],target_span=b['span_id'],source_position=i,target_position=j,
                source_clause_id=x,target_clause_id=y,source_component_profile=p['profile_id'],target_component_profile=q['profile_id'],
                mapping_basis=basis,source_roles=sorted(ra),target_roles=sorted(rb)))
    xs=[m['source_position'] for m in mapping];ys=[m['target_position'] for m in mapping]
    unambiguous=bool(mapping and len(xs)==len(set(xs)) and len(ys)==len(set(ys)) and ys==sorted(ys) and
        (0,0) in {(m['source_position'],m['target_position']) for m in mapping} and
        (len(a['clause_ids'])-1,len(b['clause_ids'])-1) in {(m['source_position'],m['target_position']) for m in mapping})
    for span,mapped in ((a,set(xs)),(b,set(ys))):
        if any(not set(index.roles(k,i))&{'DEPENDENT_INFINITIVE','EXPLICIT_SUBORDINATE_COMPONENT','TEMPORAL_FRAME_COMPONENT','LOCATIVE_FRAME_COMPONENT'}
            for i,k in enumerate(span['clause_ids']) if i not in mapped):unambiguous=False
    return mapping,unambiguous


def projected_dependencies(composite,mapped):
    links=defaultdict(list)
    for e in composite['internal_dependency_pattern']:links[e['source_position']].append(e['target_position'])
    result=[]
    for start in sorted(mapped):
        stack=[(start,[start])]
        while stack:
            current,path=stack.pop()
            for end in sorted(set(links[current])):
                if end in path:continue
                if end in mapped:result.append(dict(source_position=mapped[start],target_position=mapped[end],native_path=path+[end]))
                else:stack.append((end,path+[end]))
    return result


def compare(index,left,right):
    a,b=index.spans[left],index.spans[right]
    independent=a['construction_independence_status'] in INDEPENDENT and b['construction_independence_status'] in INDEPENDENT and not set(a['clause_ids'])&set(b['clause_ids'])
    ca,cb=index.composites.get(left),index.composites.get(right)
    mapping,unambiguous=position_mapping(index,a,b) if independent else ([],False)
    same=bool(ca and cb and ca['composite_family_id']==cb['composite_family_id']);chains=[];lexical=[];participants=[]
    for m in mapping:
        p,q=index.profiles[m['source_clause_id']],index.profiles[m['target_clause_id']]
        for kind in ('TEMPORAL','LOCATIVE'):
            for f in frame_witness(p,q,kind):chains.append(dict(kind=kind+'_FRAME_CHAIN',mapping=m,witness=f))
        for lex in sorted({v['lex'] for v in p['predicate_morphology']}&{v['lex'] for v in q['predicate_morphology']} - set(index.lexicons['speech'])):
            lexical.append(dict(grammatical_role='PREDICATE',lexeme=lex,mapping=m,identity_basis='EXPLICIT_LEXICAL_FORM'))
        for function,lex in sorted(nominal_anchors(p)&nominal_anchors(q)):
            record=dict(grammatical_role=function,lexeme=lex,mapping=m,identity_basis='EXPLICIT_LEXICAL_FORM_NOT_COREFERENCE')
            participants.append(record)
        for function,lex in sorted(non_generic_nominals(index,p)&non_generic_nominals(index,q)):
            lexical.append(dict(grammatical_role=function,lexeme=lex,mapping=m,identity_basis='EXPLICIT_COMMON_NOUN_IN_NATIVE_ROLE',
                source_role_evidence=[r for r in index.role_phrases[p['clause_id']] if r['function']==function],
                target_role_evidence=[r for r in index.role_phrases[q['clause_id']] if r['function']==function]))
    projected_a=projected_dependencies(ca,{m['source_position']:n for n,m in enumerate(mapping)}) if unambiguous else []
    projected_b=projected_dependencies(cb,{m['target_position']:n for n,m in enumerate(mapping)}) if unambiguous else []
    pattern=lambda p:sorted((r['source_position'],r['target_position']) for r in p)
    native_correspondence=bool(projected_a and pattern(projected_a)==pattern(projected_b))
    if native_correspondence and lexical:
        chains.append(dict(kind='NATIVE_DEPENDENCY_PATTERN_CHAIN',source_paths=projected_a,target_paths=projected_b,
            non_generic_lexical_anchors=lexical,provenance=[ca['composite_profile_id'],cb['composite_profile_id']]))
    if len({x['mapping']['source_position'] for x in lexical})>1:
        chains.append(dict(kind='COMPOSITE_LEXICAL_ROLE_CHAIN',anchors=lexical))
    # Mere participant recurrence in an otherwise bare formula never establishes binding.
    bare=bare_formula(index,a) and bare_formula(index,b)
    participant_positions=defaultdict(set)
    for p in participants:participant_positions[p['lexeme']].add(p['mapping']['source_position'])
    if not bare and native_correspondence and any(len(pos)>1 for pos in participant_positions.values()):
        chains.append(dict(kind='PARTICIPANT_ROLE_CHAIN',explicit_anchors=participants,identity_basis='EXPLICIT_SURFACE_ONLY'))
    positive=bool(independent and unambiguous and chains and not bare)
    record=dict(source_span=left,target_span=right,family_A=ca['composite_family_id'] if ca else '',family_B=cb['composite_family_id'] if cb else '',
        correspondence_kind='EXACT_COMPOSITE_CORRESPONDENCE' if same else 'CROSS_FAMILY_CONFIGURATION_CORRESPONDENCE' if unambiguous else 'UNRESOLVED',
        same_family=same,families_merged=False,independent=independent,position_mapping=mapping,mapping_resolved=unambiguous,
        native_dependency_correspondence=native_correspondence,source_native_paths=projected_a,target_native_paths=projected_b,
        lexical_role_mapping=lexical,participant_role_mapping=participants,pair_binding_chains=chains,
        generic_formula_only=bare,positive_source_binding=positive,
        status='BLOCKED_NONINDEPENDENT_SPAN' if not independent else 'UNRESOLVED' if not unambiguous else
            'BLOCKED_GENERIC_FORMULA_ONLY' if bare else 'COMPOSITE_SOURCE_BINDING' if positive else
            'SAME_COMPOSITE_CONFIGURATION_FAMILY' if same else 'CROSS_FAMILY_CONFIGURATION_CORRESPONDENCE',
        textual_level='UNRESOLVED',reference_identity='UNRESOLVED',provenance=[ca['composite_profile_id'] if ca else left,cb['composite_profile_id'] if cb else right])
    record['correspondence_id']='CCC-'+identity(record);return record


class CompositeBinding:
    def __init__(self,index):self.index=index;self.cache={}

    def evaluate(self,source,target,matches,deferred=False):
        source,target=str(source),str(target);cs=[];ws=[]
        for left in self.index.memberships[source]:
            for right in self.index.memberships[target]:
                if left==right:continue
                key=left,right
                if key not in self.cache:self.cache[key]=compare(self.index,left,right)
                c=self.cache[key]
                mapped=any(m['source_clause_id']==source and m['target_clause_id']==target for m in c['position_mapping'])
                if not mapped and c['independent']:continue
                cs.append(c)
                if not c['positive_source_binding'] or not mapped:continue
                mechanism='SB06' if self.index.spans[left]['start_clause']==source and self.index.spans[right]['start_clause']==target else 'SB11'
                ws.append(witness(mechanism,'CONFIGURATION_BINDING',source,target,c,['PARATACTIC'],
                    independent_correspondence_and_same_line=True,intervening_context_status='COMPOSITE_POSITION_CANDIDATE_NOT_FINAL_LEVEL',
                    source_anchor=dict(span_id=left,anchor_clause_id=source,anchor_basis='EXISTING_RAW_PAIR_COMPONENT'),
                    target_anchor=dict(span_id=right,anchor_clause_id=target,anchor_basis='EXISTING_RAW_PAIR_COMPONENT')))
        result=qualify(source,target,matches,ws,deferred=deferred)
        status=('COMPOSITE_QUALIFIED' if result['qualified_paths'] else 'UNRESOLVED' if deferred else
            'BLOCKED_NO_EXISTING_RELATION_GRAMMAR' if ws and not matches else
            'COMPOSITE_SUPPORT_ONLY' if ws else 'BLOCKED_GENERIC_FORMULA_ONLY' if any(c['generic_formula_only'] for c in cs) else
            'BLOCKED_NONINDEPENDENT_SPAN' if any(not c['independent'] for c in cs) else
            'SAME_COMPOSITE_FAMILY_ONLY' if any(c['same_family'] for c in cs) else
            'CROSS_FAMILY_SUPPORT_ONLY' if any(c['mapping_resolved'] for c in cs) else 'UNRESOLVED')
        return dict(status=status,**result,correspondence_ids=[c['correspondence_id'] for c in cs],witnesses=ws)
