"""Derived visibility, compatibility and provisional source binding; raw witnesses survive."""
from collections import defaultdict,Counter
from statistics import median
from milal_q1_binding import identity,witness,qualify
from milal_q15_domains import form_type,compatibility


class Visibility:
    def __init__(self,domains,witnesses):
        self.d=domains;self.old=witnesses;self.forms=[];self.reclassified=[];self.paths=[];self.compat=[]
        self.bindings=[];self.by_pair=defaultdict(list);self.by_reference={};self.path_cache={}
        self.ants_by_clause=defaultdict(list)
        for a in domains.antecedents.values():self.ants_by_clause[a['clause_id']].append(a)
        self.classified_count=0;self.global_count=0;self.supplemental_count=0

    def target_paths(self,target):
        if target not in self.path_cache:
            candidates=set()
            for did in self.d.members[target]:candidates.update(self.d.domains[did]['member_clauses'])
            for did in self.d.members[target]:
                d=self.d.domains[did]
                if d['domain_type']!='COMPOSITE_SURFACE_SPAN':continue
                for other in self.d.domains.values():
                    if other['domain_type']=='COMPOSITE_SURFACE_SPAN' and set(d['member_clauses'])&set(other['member_clauses']):candidates.update(other['member_clauses'])
            self.path_cache[target]={c:self.d.paths(c,target) for c in sorted(candidates)}
        return self.path_cache[target]

    def process(self,emit):
        for old in self.old:
            rid=old['reference_witness_id'];raw=old['target_reference_form'];tid=str(old['target_clause_id']);node=int(raw['node'])
            if node not in self.d.words:raise ValueError('reference word missing')
            kind=form_type(raw,self.d.words[node]);bearing=kind in ('PRONOMINAL_SUFFIX','INDEPENDENT_PRONOUN','DEICTIC_PRONOUN_OR_DETERMINER','IMPLICIT_SUBJECT_OR_ARGUMENT')
            lexical=kind in ('EXPLICIT_PROPER_NAME_MENTION','EXPLICIT_COMMON_NP_MENTION')
            form=dict(reference_witness_id=rid,target_clause_id=tid,word_node=node,reference_form_type=kind,raw_form=raw,
                reference_bearing=bearing,original_reference_status=old['reference_status'],global_candidate_count=int(old['candidate_count']),
                mention_status='LEXICAL_CONTINUITY_EVIDENCE' if not bearing and old['candidate_antecedent_ids'] else 'UNRESOLVED_MENTION_STATUS' if not bearing else 'NOT_APPLICABLE',
                domain_ids=sorted(self.d.members[tid]),provenance=old['provenance'])
            self.forms.append(form);paths=self.target_paths(tid)
            globals_=set(old['candidate_antecedent_ids'])
            if len(globals_)!=int(old['candidate_count']):raise ValueError('original candidate count mismatch')
            if not globals_<=set(self.d.antecedents):raise ValueError('original antecedent identity missing')
            local={a['antecedent_id'] for c in paths for a in self.ants_by_clause[c] if a['word_node']<node}
            all_ids=globals_|local;visible=[];supported=[];exact=[];evidence={}
            for aid in sorted(all_ids):
                a=self.d.antecedents[aid];ps=paths.get(a['clause_id'],[]) if aid in local else []
                native=[e for e in self.d.profiles[tid]['native_annotations'] if int(e['dependent_node'])==node and int(e['head_node'])==a['word_node']
                    and e.get('reference_semantics')=='EXPLICIT_ANTECEDENT' and e.get('status')=='DATABASE_EXISTING_RELATION' and e['resolution']=='EXACT_NODE_MEMBERSHIP']
                dims,vis,sup=compatibility(form,a,ps,bool(native));pids=[]
                if ps:
                    for p in ps:
                        record=dict(reference_witness_id=rid,antecedent_id=aid,**p)
                        record['visibility_path_id']='RVP-'+identity(record);self.paths.append(record);pids.append(record['visibility_path_id'])
                    self.compat.append(dict(reference_witness_id=rid,antecedent_id=aid,dimensions=dims,visible=vis,source_binding_supported=sup,native_reference_evidence=native))
                lexical=kind in ('EXPLICIT_PROPER_NAME_MENTION','EXPLICIT_COMMON_NP_MENTION')
                status='LEXICAL_EVIDENCE_ONLY' if lexical else 'UNRESOLVED' if not bearing else 'VISIBLE' if vis else 'BLOCKED_BY_ROLE' if ps and dims['GRAMMATICAL_ROLE']=='CONFLICT' else 'UNRESOLVED' if ps else 'OUTSIDE_ACTIVE_SURFACE_DOMAIN'
                emit(dict(reference_witness_id=rid,antecedent_id=aid,original_global_candidate=aid in globals_,supplemental_domain_candidate=aid not in globals_,
                    visibility_status=status,visibility_path_ids=pids,path_type='INDEPENDENT_DOMAIN_PATH' if pids else 'GLOBAL_SEARCH_ONLY',referential_identity='UNRESOLVED'))
                self.classified_count+=1;self.global_count+=aid in globals_;self.supplemental_count+=aid not in globals_
                if vis and bearing:visible.append(aid)
                if sup and bearing:supported.append(aid)
                if native and vis and bearing:exact.append(aid)
                if ps:evidence[aid]=dict(dimensions=dims,visibility_path_ids=pids,native_reference_evidence=native)
            bound=exact if len(exact)==1 else supported if len(visible)==1 and len(supported)==1 else []
            status=('LEXICAL_RECURRENCE_ONLY' if lexical and globals_ else 'UNRESOLVED' if not bearing else 'NATIVE_EXACT_REFERENCE' if len(exact)==1 else
                'MULTIPLE_VISIBLE_CANDIDATES' if len(visible)>1 else 'UNIQUE_VISIBLE_CANDIDATE' if bound else
                'VISIBLE_BUT_ROLE_AMBIGUOUS' if visible else 'OUTSIDE_DOMAIN_ONLY' if globals_ and not local else 'NO_VISIBLE_CANDIDATE')
            ident='CONFIRMED_NATIVE' if len(exact)==1 else 'PROVISIONAL_UNIQUE_VISIBLE' if bound else 'MULTIPLE_PLAUSIBLE' if len(visible)>1 else 'UNRESOLVED'
            rec=dict(reference_witness_id=rid,reference_form_type=kind,global_candidate_count=len(globals_),visible_candidate_count=len(visible),
                source_bound_candidate_count=len(bound),visible_antecedent_ids=visible,source_bound_antecedent_ids=bound,
                reference_status=status,referential_identity_status=ident,lexical_repetition_status='LEXICAL_REPETITION' if not bearing and globals_ else 'NOT_APPLICABLE',
                supplemental_domain_candidate_count=len(local-globals_))
            self.reclassified.append(rec);self.by_reference[rid]=rec
            # Ambiguous paths are represented as support; no rival is silently selected.
            for aid in visible:
                a=self.d.antecedents[aid];source=a['clause_id'];routes=[('SB02',source,None)]
                for sid in a['span_ids']:
                    span=self.d.spans[sid]
                    if span['construction_independence_status'].startswith('INDEPENDENT') and span['start_clause']!=source:
                        routes.append(('SB03',span['start_clause'],sid))
                for mechanism,source,span in routes:
                    if int(self.d.rows[source]['position'])>=int(self.d.rows[tid]['position']):continue
                    b=dict(mechanism=mechanism,source_id=source,target_id=tid,reference_witness_id=rid,source_span=span,
                        internal_antecedent=aid,antecedent_clause=a['clause_id'],target_reference=raw,visibility=evidence[aid],
                        competing_visible_antecedents=visible,source_binding_candidate=aid in bound,identity_status=ident,
                        tested_relation_used_for_domain=False,relation_status='SUPPORT_ONLY',qualified_relation_types=[],qualified_paths=[])
                    b['binding_id']='RB-'+identity(b);self.bindings.append(b);self.by_pair[(source,tid)].append(b)
            if bearing:
                for mechanism in ('SB02','SB03'):
                    if not any(b['reference_witness_id']==rid and b['mechanism']==mechanism for b in self.bindings):
                        self.bindings.append(dict(mechanism=mechanism,source_id='',target_id=tid,reference_witness_id=rid,source_span=None,
                            internal_antecedent='',antecedent_clause='',target_reference=raw,visibility={},competing_visible_antecedents=visible,
                            source_binding_candidate=False,identity_status=ident,tested_relation_used_for_domain=False,relation_status='UNRESOLVED',
                            qualified_relation_types=[],qualified_paths=[],binding_id=mechanism+'-'+rid))
            # SB10 lacks independently attested anaphoric grammar in this adapter.
            self.bindings.append(dict(mechanism='SB10',source_id='',target_id=tid,reference_witness_id=rid,source_span=None,
                internal_antecedent='',antecedent_clause='',target_reference=raw,visibility={},competing_visible_antecedents=visible,
                source_binding_candidate=False,identity_status='UNRESOLVED',tested_relation_used_for_domain=False,
                relation_status='SUPPORT_ONLY' if not bearing and globals_ else 'UNRESOLVED',qualified_relation_types=[],qualified_paths=[],binding_id='SB10-'+rid))

    def evaluate(self,source,target,matches,deferred=False):
        bs=self.by_pair.get((str(source),str(target)),[]);ws=[]
        for b in bs:
            if not b['source_binding_candidate']:continue
            if b['tested_relation_used_for_domain']:raise ValueError('circular reference binding')
            evidence={k:v for k,v in b.items() if k not in ('qualified_paths','qualified_relation_types','relation_status')}
            ws.append(witness(b['mechanism'],'UNIT_MEDIATED_BINDING' if b['mechanism']=='SB03' else 'DIRECT_BINDING',source,target,evidence,['HYPOTACTIC'],
                intervening_context_status='INDEPENDENT_REFERENCE_VISIBILITY; IDENTITY_SEPARATE'))
        result=qualify(source,target,matches,ws,deferred=deferred)
        for b in bs:
            matching=[w for w in ws if w['evidence']['binding_id']==b['binding_id']]
            pp=[p for p in result['qualified_paths'] if any(w['witness_id']==p['witness_id'] for w in matching)]
            b['qualified_paths']=pp;b['qualified_relation_types']=sorted({p['relation'] for p in pp})
            b['relation_status']='QUALIFIED' if pp else 'SUPPORT_ONLY'
        return dict(**result,witnesses=ws)

    def metrics(self):
        grouped=defaultdict(list)
        for r in self.reclassified:grouped[r['reference_form_type']].append(r)
        dist={k:{field:dict(total=sum(r[field] for r in rs),median=median(r[field] for r in rs),maximum=max(r[field] for r in rs))
            for field in ('global_candidate_count','visible_candidate_count','source_bound_candidate_count')} for k,rs in sorted(grouped.items())}
        return dict(reference_forms=dict(Counter(f['reference_form_type'] for f in self.forms)),domains=dict(Counter(d['domain_type'] for d in self.d.domains.values())),
            global_candidates=self.global_count,visible_candidates=sum(r['visible_candidate_count'] for r in self.reclassified),
            source_bound_candidates=sum(r['source_bound_candidate_count'] for r in self.reclassified),supplemental_domain_candidates=self.supplemental_count,
            candidate_distributions=dist,statuses=dict(Counter(r['reference_status'] for r in self.reclassified)),identity_statuses=dict(Counter(r['referential_identity_status'] for r in self.reclassified)),
            mechanisms={m:{status:sum(b['relation_status']==status for b in self.bindings if b['mechanism']==m) for status in ('QUALIFIED','SUPPORT_ONLY','UNRESOLVED')} for m in ('SB02','SB03','SB10')})
