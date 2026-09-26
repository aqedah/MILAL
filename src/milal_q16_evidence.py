"""Q1.6 audit algebra. Recorded evidence dependencies are not independent votes."""
from collections import defaultdict
from itertools import combinations
from milal_q1_binding import identity, MECHANISMS

class EvidenceGraph:
    def __init__(self):
        self.nodes={};self.views={};self.paths=defaultdict(list)
    def raw(self,kind,key,value,source):
        payload=dict(kind=kind,source=source,key=str(key),value=value)
        rid='RAW-'+identity(payload)
        self.nodes[rid]=dict(node_id=rid,node_type='RAW',mechanism='',dependencies=[],payload=payload)
        return rid
    def derived(self,key,payload,dependencies,mechanism=''):
        deps=sorted(set(dependencies))
        if not deps:raise ValueError('derived evidence without raw provenance')
        node=dict(node_id=key,node_type='DERIVED',mechanism=mechanism,dependencies=deps,payload=payload)
        if key in self.nodes and self.nodes[key]!=node:raise ValueError('conflicting evidence identity')
        self.nodes[key]=node
        return key
    def roots(self,key,trail=()):
        if key in trail:raise ValueError('circular evidence dependency')
        n=self.nodes[key]
        if n['node_type']=='RAW':return {key}
        return set().union(*(self.roots(d,trail+(key,)) for d in n['dependencies']))
    def add_view(self,key,mechanism,deps,payload,polarity='SUPPORT_ONLY'):
        self.derived(key,payload,deps,mechanism)
        self.views[key]=dict(mechanism=mechanism,polarity=polarity)
    def analyze(self,outcomes):
        positive={k:n['mechanism'] for k,n in self.nodes.items() if n['payload'].get('positive_binding')}
        roots={k:self.roots(k) for k in self.nodes}
        owners=defaultdict(set);consumers=defaultdict(set);affected=defaultdict(set)
        for k,m in positive.items():
            for r in roots[k]:owners[r].add(m)
        for k,n in self.nodes.items():
            if n['mechanism']:
                for r in roots[k]:consumers[r].add(n['mechanism'])
        prov=[]
        for o in outcomes:
            oid=o['structural_outcome_group_id'];ws=sorted(set(p['witness_id'] for p in self.paths[oid]))
            if not ws:raise ValueError('qualified outcome lacks exact witness')
            if any(w not in positive for w in ws):raise ValueError('nonpositive qualification witness')
            ms=sorted({positive[w] for w in ws});shared=set()
            independent=[]
            for a,b in combinations(ws,2):
                overlap=roots[a]&roots[b]
                if overlap:shared|=overlap
                elif positive[a]!=positive[b]:independent.append([a,b])
            corroborative=sorted({v['mechanism'] for k,v in self.views.items() if any(roots[k]&roots[w] for w in ws) and self.nodes[k]['payload'].get('candidate_id')=='P'+o['source_or_peer']+'-'+o['target']})
            basis='SINGLE_MECHANISM' if len(ms)==1 else 'MULTI_MECHANISM_INDEPENDENT' if independent and not shared else 'MULTI_MECHANISM_SHARED_RAW_EVIDENCE'
            for w in ws:
                for r in roots[w]:affected[r].add(oid)
            prov.append(dict(outcome_id=oid,source_id=o['source_or_peer'],target_id=o['target'],relation_type=o['relation_type'],witness_ids=ws,
                qualification_basis=basis,decisive_mechanism_set=ms,corroborative_mechanism_set=corroborative,shared_evidence_groups=sorted(shared),independent_chain_pairs=independent))
        groups=[dict(raw_evidence_identity=r,mechanism_views=sorted(ms),positive_mechanism_owners=sorted(owners[r]),affected_relations=sorted(affected[r]),independent_reason_count=1) for r,ms in sorted(consumers.items()) if len(ms)>1]
        ablation=[]
        for m in list(MECHANISMS)[:-1]:
            removed={r for r,ms in owners.items() if ms=={m}};lost=[];changed=[];retained=[];unaffected=[];alternative=[];to_corroborative=[]
            for p in prov:
                ws=p['witness_ids'];survive=[w for w in ws if not roots[w]&removed]
                if not survive:lost.append(p['outcome_id'])
                else:
                    retained.append(p['outcome_id'])
                    if len(survive)!=len(ws):
                        changed.append(p['outcome_id'])
                        if p['qualification_basis']=='MULTI_MECHANISM_INDEPENDENT' and not any(positive[x]!=positive[y] and not roots[x]&roots[y] for x,y in combinations(survive,2)):to_corroborative.append(p['outcome_id'])
                    else:unaffected.append(p['outcome_id'])
                    if m in p['decisive_mechanism_set'] and any(positive[w]!=m for w in survive):alternative.append(p['outcome_id'])
            ablation.append(dict(mechanism=m,baseline=len(prov),still_qualified=len(retained),lose_all_binding_support=len(lost),support_paths_changed=len(changed),independent_to_corroborative=len(to_corroborative),unaffected=len(unaffected),unique_raw_facts_removed=len(removed),lost_outcome_ids=lost,changed_outcome_ids=changed,alternative_retained_outcome_ids=alternative,frozen_outputs_mutated=False))
        overlap=[dict(mechanism_a=a,mechanism_b=b,shared_raw_count=sum(a in ms and b in ms for ms in consumers.values()),shared_raw_ids=sorted(r for r,ms in consumers.items() if a in ms and b in ms)) for a,b in combinations(MECHANISMS,2)]
        graph=[dict(**n,raw_evidence_nodes=sorted(roots[k]),mechanism_views=sorted(set().union(*(consumers[r] for r in roots[k]))),affected_relations=sorted(set().union(*(affected[r] for r in roots[k])))) for k,n in sorted(self.nodes.items())]
        return dict(graph=graph,groups=groups,provenance=prov,ablation=ablation,overlap=overlap)


def dependency_contract(record):
    """Validation of supplied attested paths; not an extractor or a grammar license."""
    m=record['mechanism']
    if m not in ('SB05','SB07','SB08','SB09'):raise ValueError('unsupported supplemental path')
    if record.get('tested_relation_used_for_domain'):raise ValueError('circular domain')
    if record.get('duplicate_of'):return 'REDUNDANT_ALIAS_BLOCKED'
    if not (record.get('source_id') and record.get('target_id') and record.get('raw_evidence') and record.get('provenance') and record.get('independent')):return 'UNRESOLVED'
    required={'SB05':'grammatical_governance_path','SB07':'pair_specific_temporal_path','SB08':'pair_specific_locative_path','SB09':'positive_domain_continuity_path'}[m]
    if not record.get(required):return 'UNRESOLVED'
    if m=='SB05' and record.get('semantic_valency_guess'):return 'UNRESOLVED'
    if m=='SB09' and not record.get('independent_domain'):return 'UNRESOLVED'
    return 'POSITIVE_BINDING'


def conflicts(records):
    result=[]
    for a,b in combinations(records,2):
        if a['candidate_id']!=b['candidate_id'] or {a['polarity'],b['polarity']}!={'POSITIVE_BINDING','COUNTEREVIDENCE'}:continue
        if set(a['raw_evidence'])&set(b['raw_evidence']):continue
        result.append(dict(candidate_id=a['candidate_id'],status='MECHANISM_SUPPORT_CONFLICT',witness_ids=[a['witness_id'],b['witness_id']],resolution='UNRESOLVED'))
    return result


def empirical_status(positive_records, support_records):
    return "OPERATIONAL_DISTINCT" if positive_records else "OPERATIONAL_VIA_EXISTING_LAYER" if support_records else "NO_JOB_WITNESS"
