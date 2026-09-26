"""Exact frozen-witness recovery and raw observation adapter for Q1.6."""
from collections import defaultdict
from milal_mfr02r_data import rows,digest,physical_path
from milal_q1_binding import witness,outcome
from milal_q16_evidence import EvidenceGraph


def recover(q12,q14,q15):
    records={}; paths=defaultdict(list)
    def add(w,pp):
        wid=w['witness_id']
        if wid in records and records[wid]!=w:raise ValueError('recovered witness collision')
        records[wid]=w
        for p in pp:
            if p['witness_id']!=wid:raise ValueError('exact witness reconstruction failed')
            oid=outcome(w['source_id'],w['target_id'],p['relation'])['structural_outcome_group_id']
            if p not in paths[oid]:paths[oid].append(p)
    for r in rows(q12/'source_binding_witnesses.csv'):add(r['witness'],r['qualified_paths'])
    spans={s['span_id']:s for s in rows(q14/'01_q14_surface_construction_spans.csv')}
    corr={c['correspondence_id']:c for c in rows(q14/'06_q14_composite_correspondence.csv') if c['positive_source_binding']}
    for r in rows(q14/'10_q14_relation_qualification_delta.csv'):
        found=set()
        for cid in r['correspondence_ids']:
            if cid not in corr:continue
            c=corr[cid];s,t=r['source_id'],r['target_id'];a,b=c['source_span'],c['target_span']
            if not any(m['source_clause_id']==s and m['target_clause_id']==t for m in c['position_mapping']):continue
            m='SB06' if spans[a]['start_clause']==s and spans[b]['start_clause']==t else 'SB11'
            w=witness(m,'CONFIGURATION_BINDING',s,t,c,['PARATACTIC'],independent_correspondence_and_same_line=True,
                intervening_context_status='COMPOSITE_POSITION_CANDIDATE_NOT_FINAL_LEVEL',source_anchor=dict(span_id=a,anchor_clause_id=s,anchor_basis='EXISTING_RAW_PAIR_COMPONENT'),target_anchor=dict(span_id=b,anchor_clause_id=t,anchor_basis='EXISTING_RAW_PAIR_COMPONENT'))
            pp=[p for p in r['qualified_paths'] if p['witness_id']==w['witness_id']]
            add(w,pp)
            if pp:found.add(w['witness_id'])
        if found!={p['witness_id'] for p in r['qualified_paths']}:raise ValueError('unresolved exact Q1.4 witness')
    bindings=[]
    for name in ('10_q15_sb02_qualification.csv','11_q15_sb03_qualification.csv','12_q15_sb10_qualification.csv'):
        for b in rows(q15/name):
            bindings.append(b)
            if not b['source_binding_candidate']:continue
            ev={k:v for k,v in b.items() if k not in ('qualified_paths','qualified_relation_types','relation_status')}
            w=witness(b['mechanism'],'UNIT_MEDIATED_BINDING' if b['mechanism']=='SB03' else 'DIRECT_BINDING',b['source_id'],b['target_id'],ev,['HYPOTACTIC'],intervening_context_status='INDEPENDENT_REFERENCE_VISIBILITY; IDENTITY_SEPARATE')
            add(w,b['qualified_paths'])
    outcomes=list(rows(q15/'q15_structural_outcome_groups.csv'))
    for o in outcomes:
        for p in o['provenance_paths']:
            if p['witness_id'] not in records:raise ValueError('frozen outcome witness missing')
            if not any(p['witness_id']==q['witness_id'] and p['rule_id']==q['rule_id'] for q in paths[o['structural_outcome_group_id']]):raise ValueError('frozen path not recovered')
    return records,paths,spans,bindings,outcomes

class Adapter:
    def __init__(self,source,q12,q14,q15):
        self.records,self.paths,self.spans,self.bindings,self.outcomes=recover(q12,q14,q15)
        self.inventory=list(rows(source/'blind/job/02_clause_feature_inventory.csv'))
        self.by_clause={str(r['clause_id']):r for r in self.inventory}
        self.domains={r['domain_id']:r for r in rows(q15/'02_q15_reference_visibility_domains.csv')}
        self.visibility={r['visibility_path_id']:r['path'] for r in rows(q15/'08_q15_reference_visibility_paths.csv')}
        self.ants={r['antecedent_id']:r for r in rows(q15/'04_q15_antecedent_inventory.csv')}
        self.forms={r['reference_witness_id']:r for r in rows(q15/'01_q15_reference_form_inventory.csv')}
        self.graph=EvidenceGraph();self.graph.paths=self.paths
        self.raw_source=dict(dataset='BHSA_2021',artifact='blind/job/02_clause_feature_inventory.csv',sha256=digest(physical_path(source/'blind/job/02_clause_feature_inventory.csv')))
        self.clause_roots={};self.words={};self.phrases={}
        for c,r in self.by_clause.items():
            ids=[]
            for w in r['WORD']:
                k=self.graph.raw('WORD',w['node'],w,self.raw_source);self.words[int(w['node'])]=k;ids.append(k)
            for p in r['PHRASE']:
                k=self.graph.raw('PHRASE',p['node'],p,self.raw_source);self.phrases[int(p['node'])]=k;ids.append(k)
            ids.append(self.graph.raw('CLAUSE_FEATURES',c,{k:v for k,v in r['CLAUSE'].items() if k!='native_annotations'},self.raw_source))
            self.clause_roots[c]=ids
        for did,d in self.domains.items():
            deps=self.boundary(d['boundary_basis'])
            if not deps:deps=sum((self.clause_roots[c] for c in d['member_clauses']),[])
            self.graph.derived(did,d,deps)
        for pid,p in self.visibility.items():self.graph.derived(pid,p,p['domain_ids'])
        for sid,s in self.spans.items():self.graph.derived(sid,s,self.boundary(s['boundary_witnesses']) or sum((self.clause_roots[c] for c in s['clause_ids']),[]))
        for wid,w in self.records.items():
            ev=w['evidence'];m=w['mechanism'];deps=list(w['dependent_on'])
            if m=='SB01':deps += [self.native(e) for e in ev['native_edges']]
            elif m in ('SB02','SB03'):
                deps += ev['visibility']['visibility_path_ids']
                deps += [self.words[int(ev['target_reference']['node'])],self.words[int(self.ants[ev['internal_antecedent']]['word_node'])],self.phrases[int(self.ants[ev['internal_antecedent']]['phrase_node'])]]
                if ev['source_span']:deps.append(ev['source_span'])
            elif m=='SB04':
                deps += [self.words[int(p['participant_id'].split('-')[-1])] for pair in ev['explicit_mention_pairs'] for p in pair]
            elif m in ('SB06','SB11'):
                for mapping in ev['position_mapping']:
                    deps+=self.clause_roots[str(mapping['source_clause_id'])]+self.clause_roots[str(mapping['target_clause_id'])]
                for key in ('source_span','target_span'):
                    if key in ev:deps.append(ev[key])
                # The complete consumed profile is conservative context provenance, not minimal causal evidence.
            else:raise ValueError('unsupported positive witness mechanism '+m)
            self.graph.derived(wid,dict(positive_binding=True,frozen_witness=w),deps,m)
        for wid in self.records:self.graph.roots(wid)
    def native(self,e):
        return self.graph.raw('NATIVE_EDGE',str(e['head_node'])+'>'+str(e['dependent_node']),e,self.raw_source)
    def boundary(self,obj):
        found=[]
        if isinstance(obj,dict):
            if 'dependent_node' in obj and 'head_node' in obj:return [self.native(obj)]
            for v in obj.values():found+=self.boundary(v)
        elif isinstance(obj,list):
            for v in obj:found+=self.boundary(v)
        return found
    def view(self,m,key,s,t,deps,detail,polarity='SUPPORT_ONLY'):
        pair='P'+str(s)+'-'+str(t) if s and t else ''
        self.graph.add_view(key,m,deps,dict(candidate_id=pair,detail=detail),polarity)
        return dict(witness_id=key,mechanism=m,source_id=str(s),target_id=str(t),candidate_id=pair,polarity=polarity,raw_evidence=sorted(self.graph.roots(key)),detail=detail,qualification_effect='NO_ADDITIONAL_BINDING',independence_status='SHARED_EXISTING_LAYER' if polarity=='SUPPORT_ONLY' else 'UNRESOLVED')
