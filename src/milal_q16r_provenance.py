"""Additive typed provenance projection over the frozen Q1.6 graph.

Complete historical closure is preserved; semantic dependency is not raw identity.
"""
from collections import defaultdict
from itertools import combinations
from milal_mfr02r_data import rows
from milal_q1_binding import identity
from milal_q16r_roles import independence

class Projection:
    def __init__(self,q16,inventory):
        self.nodes={n['node_id']:n for n in rows(q16/'02_q16_evidence_dependency_graph.csv')}
        self.raw={(n['payload']['kind'],n['payload']['key']):n['node_id'] for n in self.nodes.values() if n['node_type']=='RAW'}
        self.inventory={str(r['clause_id']):r for r in inventory}
        self.bases={};self.unresolved=[]
        for key,n in self.nodes.items():
            if not n['mechanism']:continue
            self.active_raw=set(n['raw_evidence_nodes'])
            payload=n['payload'];w=payload.get('frozen_witness');core=set();analytic=[];inherited=set();complete=True
            pair=payload.get('candidate_id','');context_only=False;method=''
            if w:
                pair='P'+w['source_id']+'-'+w['target_id'];m=w['mechanism'];ev=w['evidence'];analytic=w['dependent_on']
                if m in ('SB01','SB02','SB03','SB04'):
                    core={d for d in n['dependencies'] if self.nodes[d]['node_type']=='RAW'}
                    method='EXPLICIT_NATIVE_OR_REFERENCE_OR_MENTION_INPUTS'
                elif m in ('SB06','SB11'):
                    method='RECORDED_PAIR_BINDING_ANCHORS_AND_NATIVE_PATTERN'
                    frames=ev.get('pair_binding_witnesses',[])+[c['witness'] for c in ev.get('pair_binding_chains',[]) if 'witness' in c]
                    for f in frames:
                        if 'source_frame' in f:
                            core |= self.frame(f['source_frame'])|self.frame(f['target_frame'])
                        elif f.get('lexeme') and f.get('grammatical_function'):
                            for mp in ev['position_mapping']:
                                core |= self.anchor(mp['source_clause_id'],f['grammatical_function'],f['lexeme'])|self.anchor(mp['target_clause_id'],f['grammatical_function'],f['lexeme'])
                    for a in ev.get('lexical_role_mapping',[])+ev.get('participant_role_mapping',[]):
                        mp=a['mapping'];core |= self.anchor(mp['source_clause_id'],a['grammatical_role'],a['lexeme'])|self.anchor(mp['target_clause_id'],a['grammatical_role'],a['lexeme'])
                    if ev.get('native_dependency_correspondence'):
                        core|={r for r in n['raw_evidence_nodes'] if self.nodes[r]['payload']['kind']=='NATIVE_EDGE'}
                    complete=bool(core)
                else:complete=False;method='UNMAPPED_FROZEN_WITNESS'
            else:
                m=n['mechanism'];d=payload['detail']
                if m in ('SB07','SB08'):
                    method='SURFACE_FRAME_VIEW'
                    for field in ('source_expression','target_expression'):
                        if d.get(field):core |= self.frame(d[field])
                    complete=bool(core)
                elif m=='SB05':
                    if d.get('overlap_SB01'):
                        parent=self.nodes[d['overlap_SB01']];core|={x for x in parent['raw_evidence_nodes'] if self.nodes[x]['payload']['kind']=='NATIVE_EDGE'}
                        method='EXACT_NATIVE_ALIAS'
                    else:context_only=True;method='PRE_RELATION_CONSTITUTION_CONTEXT'
                elif m=='SB09':context_only=True;method='DERIVED_VISIBILITY_CONTEXT'
                else:complete=False;method='UNMAPPED_VIEW'
            full=set(n['raw_evidence_nodes'])
            if not core<=full:raise ValueError('projection would invent raw input '+key)
            self.bases[key]=dict(id=key,mechanism=n['mechanism'],candidate_id=pair,core_raw=sorted(core),context_raw=sorted(full-core),full_raw=sorted(full),inherited_core_raw=[],analytical_dependencies=analytic,complete=complete,context_only=context_only,projection_method=method,historical_dependencies=n['dependencies'])
            if not complete:self.unresolved.append(key)
        def inherited(key,trail=()):
            if key in trail:raise ValueError('analytical dependency cycle')
            b=self.bases[key];rr=set(b['core_raw'])
            for other in b['analytical_dependencies']:rr|=inherited(other,trail+(key,))
            return rr
        for key,b in self.bases.items():
            b['inherited_core_raw']=sorted(set().union(*(inherited(k) for k in b['analytical_dependencies']))) if b['analytical_dependencies'] else []
    def frame(self,p):
        found=set()
        if p.get('node') is not None:
            key=('PHRASE',str(p['node']))
            if key not in self.raw:raise ValueError('missing exact frame phrase')
            if self.raw[key] in self.active_raw:found.add(self.raw[key])
        # A frozen phrase observation can already contain word IDs without separate
        # WORD dependencies. Project only raw identities actually recorded here.
        for w in p.get('word_ids',[]):
            raw=self.raw.get(('WORD',str(w)))
            if raw in self.active_raw:found.add(raw)
        return found
    def anchor(self,clause,role,lexeme):
        r=self.inventory[str(clause)];words={w['node']:w for w in r['WORD']};result=set()
        for p in r['PHRASE']:
            if (role=='PREDICATE' and p['function'] not in ('Pred','PreC','PreO','PreS','PtcO','PtcS')) or (role!='PREDICATE' and p['function']!=role):continue
            for node in p['word_ids']:
                if node in words and words[node]['lex']==lexeme:
                    result.add(self.raw[('WORD',str(node))]);result.add(self.raw[('PHRASE',str(p['node']))])
        return result
    def compare(self,q16):
        bypair=defaultdict(list);outcomes=defaultdict(set)
        for r in rows(q16/'10_q16_relation_mechanism_provenance.csv'):
            for a,b in combinations(sorted(r['witness_ids']),2):outcomes[(a,b)].add(r['outcome_id'])
        for b in self.bases.values():
            if b['candidate_id']:bypair[b['candidate_id']].append(b)
        result=[]
        for pair,bb in sorted(bypair.items()):
            for a,b in combinations(sorted(bb,key=lambda x:x['id']),2):
                r=independence(a,b)
                result.append(dict(comparison_id='EI-'+identity([a['id'],b['id']]),candidate_id=pair,witness_a=a['id'],witness_b=b['id'],mechanism_a=a['mechanism'],mechanism_b=b['mechanism'],qualified_outcome_ids=sorted(outcomes[(a['id'],b['id'])]),**r,historical_closure_overlap=sorted(set(a['full_raw'])&set(b['full_raw'])),new_relation=False))
        return result
    def shared(self,q16):
        rawusers=defaultdict(list)
        for b in self.bases.values():
            for r in b['full_raw']:
                rawusers[r].append(dict(witness_id=b['id'],mechanism=b['mechanism'],input_role='CORE_OBSERVATION' if r in b['core_raw'] else 'INHERITED_ANALYTICAL' if r in b['inherited_core_raw'] else 'CONTEXT'))
        return [dict(raw_evidence_identity=r['raw_evidence_identity'],frozen_shared_group=r,typed_consumers=rawusers[r['raw_evidence_identity']],raw_identity_unchanged=True,independent_votes_created=0) for r in rows(q16/'03_q16_shared_raw_evidence_groups.csv')]
