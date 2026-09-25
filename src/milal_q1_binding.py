"""Q1 source witnesses. Search similarity never resolves referential identity.

All executable criteria here are GENERALIZED_FOR_MILAL, not new quotations
from Jin or Walton. Frozen native annotations retain DATABASE_EXISTING_RELATION.
"""
from collections import defaultdict
from hashlib import sha256
from milal_mfr02r_data import encode
from milal_mfr02r_graph import validate_variant

QUALIFIED = ('QUALIFIED_DIRECT', 'QUALIFIED_UNIT_MEDIATED', 'QUALIFIED_CONFIGURATION')
STATUSES = QUALIFIED + ('SEARCH_ONLY', 'EVIDENCE_ONLY', 'BLOCKED_BY_CONTEXT', 'UNRESOLVED')
MECHANISMS = dict(zip(('SB%02d' % i for i in range(1, 13)), (
    'DIRECT_SYNTACTIC_DEPENDENCY', 'EXPLICIT_REFERENCE_TO_SOURCE',
    'REFERENCE_TO_SOURCE_CONTAINING_UNIT', 'PARTICIPANT_CONTINUATION_FROM_ACTIVE_UNIT',
    'VALENCY_DEPENDENCY', 'FORMAL_CONFIGURATION_CORRESPONDENCE',
    'TEMPORAL_DEPENDENCY', 'LOCATIVE_FRAME_DEPENDENCY', 'DOMAIN_CONTINUATION_OR_EMBEDDING',
    'LEXICAL_ANAPHORIC_DEPENDENCY', 'ESTABLISHED_PARALLEL_CONFIGURATION',
    'GLOBAL_CONFIGURATION_CONSTRAINT')))


def identity(value):
    return sha256(encode(value).encode('utf8')).hexdigest()


def feature_kind(name):
    if name in ('explicit_subordinator', 'infinitive_preposition'):
        return 'TARGET_FEATURE'
    if name in ('source_finite', 'prior_narrative_speech_anchor'):
        return 'SOURCE_FEATURE'
    if name in ('same_line', 'subordination_continuation', 'sequence_correspondence'):
        return 'CONTEXT_FEATURE'
    return 'PAIR_FEATURE'


def rule_roles(rule):
    rid = rule['rule_id']
    roles = ['RELATION_CANDIDATE_RULE']
    if rid == 'W-P01': roles = ['EVIDENCE_RULE', 'RELATION_CANDIDATE_RULE']
    if rid == 'W-A01': roles = ['SEARCH_INDEX_RULE', 'RELATION_CANDIDATE_RULE']
    if rid.startswith('RG-M'): roles.append('CONFIGURATION_RULE')
    names = sorted({f for branch in rule['required_features'] for f in branch})
    return dict(rule_id=rid, execution_roles=roles,
        required_feature_roles={f: feature_kind(f) for f in names},
        supporting_feature_roles={f: 'PAIR_FEATURE' for f in rule['supporting_features']},
        original_definition=rule, implementation_schema_adoption='GENERALIZED_FOR_MILAL',
        qualification_policy='PAIR_WITNESS_REQUIRED; ORIGINAL_MATCH_IS_NOT_BINDING')


def witness(mechanism, mode, source, target, evidence, relations, **extra):
    record = dict(mechanism=mechanism, binding_mode=mode, source_id=str(source),
        target_id=str(target), evidence=evidence, allowed_relations=relations,
        identity_status='UNRESOLVED', dependent_on=[], **extra)
    record['witness_id'] = 'QW-' + identity(record)
    return record


def qualify(source, target, matches, witnesses, *, blocked=False, deferred=False):
    """Witnesses are produced by the exact-source adapter; no raw fact is promoted."""
    paths = []
    for match in matches:
        rid, relation = match['rule_id'], match['relation']
        for w in witnesses:
            if w['source_id'] != str(source) or w['target_id'] != str(target):
                raise ValueError('source-binding witness endpoint mismatch')
            if w['mechanism'] not in MECHANISMS or not w['evidence']:
                raise ValueError('unverifiable binding mechanism')
            if relation not in w['allowed_relations']: continue
            # A configuration correspondence does not establish a subordinate
            # attachment. W-H requires separately attested active context.
            if rid == 'W-A01' and w['mechanism'] not in ('SB01', 'SB02', 'SB03', 'SB05', 'SB10'):
                continue
            if rid == 'W-P01' and not w.get('independent_correspondence_and_same_line'):
                continue
            if rid == 'W-H01' and not w.get('active_participant_context'):
                continue
            paths.append(dict(rule_id=rid, relation=relation, witness_id=w['witness_id'],
                              binding_mode=w['binding_mode']))
    if blocked or deferred: paths = []
    modes = {p['binding_mode'] for p in paths}
    status = ('BLOCKED_BY_CONTEXT' if blocked else 'UNRESOLVED' if deferred else
        'QUALIFIED_DIRECT' if 'DIRECT_BINDING' in modes else
        'QUALIFIED_UNIT_MEDIATED' if 'UNIT_MEDIATED_BINDING' in modes else
        'QUALIFIED_CONFIGURATION' if 'CONFIGURATION_BINDING' in modes else
        'EVIDENCE_ONLY' if matches else 'SEARCH_ONLY')
    return dict(qualification=status, qualified_paths=paths,
        qualified_relations=sorted({p['relation'] for p in paths}),
        qualification_reason=sorted({p['witness_id'] for p in paths}),
        disqualification_reason='' if paths else 'BINDING_DEFERRED' if deferred else
        'CONTEXT_BLOCKS_RELATION' if blocked else 'NO_VERIFIED_SOURCE_TARGET_BINDING')


class SourceIndex:
    def __init__(self, inventory, subordinate_rela, speech_lexemes):
        self.rows = {str(r['clause_id']): r for r in inventory}
        self.ordered = sorted(self.rows, key=lambda k: int(self.rows[k]['position']))
        self.index = {cid:i for i,cid in enumerate(self.ordered)}
        self.subordinate_rela = set(subordinate_rela)
        self.speech = set(speech_lexemes)
        self.owners = defaultdict(set)
        for cid, r in self.rows.items():
            for node in [int(cid), *r['clause_atom_ids'], *r['word_ids'], *(p['node'] for p in r['PHRASE'])]:
                self.owners[int(node)].add(cid)
        self.units = {cid:self.native_configuration(cid) for cid in self.ordered}
        self.parents = {}
        for tid in self.ordered:
            self.parents[tid] = sorted({sid for e in self.rows[tid]['CLAUSE']['native_annotations']
                if e['rela'] in self.subordinate_rela and e['resolution']=='EXACT_NODE_MEMBERSHIP'
                for sid in self.owners.get(int(e['head_node']), ())
                if self.index[sid] < self.index[tid]})

    def dependency_paths(self, source, target):
        paths=[]; pending=[(target,[target])]
        while pending:
            node,reverse_path=pending.pop()
            if node==source:
                paths.append(list(reversed(reverse_path)));continue
            for parent in reversed(self.parents[node]):
                if self.index[parent] >= self.index[source]:pending.append((parent,reverse_path+[parent]))
        return sorted(paths)

    def native(self, source, target):
        result = []
        for e in self.rows[target]['CLAUSE']['native_annotations']:
            if (source in self.owners.get(int(e['head_node']), ()) and
                target in self.owners.get(int(e['dependent_node']), ()) and
                e['resolution'] == 'EXACT_NODE_MEMBERSHIP' and
                e['rela'] in self.subordinate_rela): result.append(e)
        return result

    def signature(self, cid):
        r = self.rows[cid]
        return (r['clause_type'], tuple((w['lex'], w['sp'], w['vt'], w['vs']) for w in r['WORD']),
                tuple((p['function'], p['typ']) for p in r['PHRASE']))

    def native_configuration(self, cid):
        """A contiguous root plus native-linked continuation, not a macro unit.

        NA annotations are allowed only as database sequence links here; they
        never supply SB01 or an accepted mother. Beyond a bare speech formula,
        correspondence needs a non-speech predicate and explicit lexical NP in
        the same grammatical position in the repeated multi-clause structure.
        """
        members = [cid]
        links = []
        for other in self.ordered[self.index[cid]+1:]:
            found = [e for e in self.rows[other]['CLAUSE']['native_annotations']
                     if cid in self.owners.get(int(e['head_node']), ()) and
                     other in self.owners.get(int(e['dependent_node']), ()) and
                     e['resolution'] == 'EXACT_NODE_MEMBERSHIP']
            if not found: break
            members.append(other); links.extend(found)
        root = self.rows[cid]
        np_nodes = [dict(clause_id=n,phrase_node=p['node'],function=p['function'],word_node=w['node'],lex=w['lex'])
            for n in members for p in self.rows[n]['PHRASE']
            if p['function'] in ('Subj','PreS','Objc','PreO','Cmpl','PreC','Time','Loca')
            for w in self.rows[n]['WORD'] if w['node'] in p['word_ids'] and w['sp'] in ('subs','nmpr')]
        nonformula = [dict(clause_id=n,word_node=w['node'],lex=w['lex'])
            for n in members for w in self.rows[n]['WORD'] if w['sp']=='verb' and w['lex'] not in self.speech]
        return dict(members=members, links=links, explicit_np_witnesses=np_nodes,
                    nonformula_predicate_witnesses=nonformula,
                    eligible=bool(len(members)>1 and np_nodes and nonformula),
                    signature=[self.signature(n) for n in members])

    def bindings(self, source, target):
        source, target = str(source), str(target)
        if self.index[source] >= self.index[target]: raise ValueError('not a preceding pair')
        result = []
        edges = self.native(source, target)
        if edges:
            result.append(witness('SB01', 'DIRECT_BINDING', source, target,
                dict(native_edges=edges, authority='DATABASE_EXISTING_RELATION_NOT_CANONICAL_MOTHER'),
                ['HYPOTACTIC'], intervening_context_status='REFERENCE_CROSSES_INTERVENING_MATERIAL'
                if self.index[target] != self.index[source]+1 else 'NO_STRUCTURAL_BREAK_DETECTED'))
            # Active participation is a pair-local context claim only. It does
            # not promote lexical matches to a referential identity.
            a, b = self.rows[source], self.rows[target]
            left = [m for m in a['PARTICIPANT']['mentions'] if m['grammatical_role'] in ('Objc','PreO','Cmpl','PreC') and m['participant_reference_type']=='EXPLICIT_NP']
            right = [m for m in b['PARTICIPANT']['mentions'] if m['participant_reference_type']=='EXPLICIT_NP']
            shared = [(x, y) for x in left for y in right if x['lexical_key']==y['lexical_key']]
            if shared and self.index[target] == self.index[source]+1:
                result.append(witness('SB04', 'DIRECT_BINDING', source, target,
                    dict(explicit_mention_pairs=shared, context='IMMEDIATE_SYNTACTICALLY_LINKED_PAIR',
                         dependency_witness=result[0]['witness_id']), ['HYPOTACTIC'],
                    active_participant_context='CONTINUED',
                    intervening_context_status='ACTIVE_DEPENDENCY_CONTINUES'))
                result[-1]['dependent_on']=[result[0]['witness_id']]
                result[-1]['witness_id']='QW-'+identity({k:v for k,v in result[-1].items() if k!='witness_id'})
        # A source-containing unit requires both an exact source dependency
        # path and an exact target-to-constituent edge. Conditional lexical/PnG
        # unit-reference matches in the frozen layer do not supply either.
        if not edges:
            for parent in self.parents[target]:
                reference_edges=[e for e in self.native(parent,target)
                    if int(e['head_node']) in self.rows[parent]['word_ids']]
                if not reference_edges: continue
                paths=self.dependency_paths(source,parent)
                if paths:
                    result.append(witness('SB03','UNIT_MEDIATED_BINDING',source,target,
                        dict(unit_opening_candidate=source,antecedent_clause=parent,
                             native_dependency_paths=paths,exact_constituent_reference=reference_edges,
                             unit_status='CONDITIONAL_NATIVE_DEPENDENCY_UNIT; NOT_FROZEN_MACRO_HIERARCHY'),
                        ['HYPOTACTIC'],intervening_context_status='REFERENCE_CROSSES_INTERVENING_MATERIAL'))
        a, b = self.units[source], self.units[target]
        if a['eligible'] and b['eligible'] and a['signature']==b['signature']:
            result.append(witness('SB06', 'CONFIGURATION_BINDING', source, target,
                dict(source_configuration=a, target_configuration=b,
                     participant_claim='EXPLICIT_NP_FORM_AND_POSITION; REFERENTIAL_IDENTITY_UNRESOLVED',
                     scope='CONFIGURATION_OPENING_CANDIDATE; NO_CONSTITUENT_SIBLING_INFERENCE'),
                ['PARATACTIC'], independent_correspondence_and_same_line=True,
                intervening_context_status='UNKNOWN'))
        return result


def outcome(source, target, relation):
    signature = dict(target=str(target), relation_type=relation, source_or_peer=str(source),
        mother_if_hypotactic=str(source) if relation=='HYPOTACTIC' else '',
        parallel_peer_if_paratactic=str(source) if relation=='PARATACTIC' else '',
        textual_level_effect_candidate='STRICTLY_BELOW' if relation=='HYPOTACTIC' else 'EQUAL_LEVEL',
        variant_effect='HYPOTHETICAL_ASSIGNMENT_ONLY')
    return dict(structural_outcome_group_id='QO-'+identity(signature), **signature)


def pivot(target, outcomes, member=False):
    """Two singleton assignments are coherent witnesses in the frozen ANY_SUBSET
    semantics. Empty/UNDECIDED versus assigned is never counted as a pivot.
    No component size, scoring or materialization limit enters this computation.
    """
    unique = {o['structural_outcome_group_id']:o for o in outcomes if o['target']==str(target)}
    variants = []
    for oid, o in sorted(unique.items()):
        edge = dict(source=o['source_or_peer'], target=o['target'], relation=o['relation_type'])
        if validate_variant([edge]): raise ValueError('incoherent qualified outcome')
        variants.append(dict(variant_id='QV-'+oid, selected_outcome_ids=[oid], coherent=True,
                             remainder='UNDECIDED', accepted=False))
    return dict(target_id=str(target), variant_member=member,
        status='VARIANT_DECISION_PIVOT' if len(unique)>1 else 'VARIANT_MEMBER_NON_PIVOT' if member else 'NOT_VARIANT_MEMBER',
        coherent_assignment_witnesses=variants, outcome_count=len(unique),
        review_required=len(unique)>1, canonical_mother='', canonical_hierarchy='')
