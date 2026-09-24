"""Neutral ordered context evidence. No human relations or native hierarchy."""
from collections import defaultdict
from itertools import product
import milal_jin_io as io

INTERNAL='NOT_PROJECTABLE_CLAUSE_INTERNAL'
LOCAL='POSSIBLE_LOCAL_UNIT_PROJECTION'
CROSS='POSSIBLE_CROSS_LOCUS_PROJECTION'
MACRO='POSSIBLE_MACRO_PROJECTION'
INSUFFICIENT='INSUFFICIENT_FOR_PROJECTION'
PROJECTABLE={CROSS,MACRO}
FROZEN_NAMES=('01_blind_target_inventory.csv','02_blind_linguistic_features.csv','03_blind_candidate_pairs.csv',
              '04_blind_relation_hypotheses.csv','05_blind_hypotaxis_mother_candidates.csv','06_blind_discovery_source_audit.csv',
              '07_blind_discovery_manifest.csv','18_phase_a_metadata.json','19_blind_rule_config.json')


def categorical(left,right):
    """Position-sensitive categorical comparison; no similarity score."""
    if left is None or right is None or left==[] or right==[]:return 'NOT_AVAILABLE'
    if left==right:return 'MATCH'
    if isinstance(left,list) and isinstance(right,list):
        return 'PARTIAL' if any(a==b and a is not None for a,b in zip(left,right)) else 'DIFFERENT'
    return 'DIFFERENT'


def signature(c):
    verbs=[[w['lex'],w['vs'],w['vt'],w['ps'],w['gn'],w['nu']] for w in c['verbal_words']]
    explicit=c['subject_lexemes']
    subject=explicit or [['IMPLICIT_UNRESOLVED',*x['png']] for x in c['implicit_subject_morphology']]
    return dict(clause_type=c['clause_type'],verbs=verbs,subjects=subject,
        phrase_layout=c['constituent_order'],domain=None if c['domain'] in (None,'','?','NA') else c['domain'],
        formula_atoms=c['formula_atoms'],surface_clause_type=c['clause_type'],participants=c['participant_surfaces'],
        temporal=[p['lexemes'] for p in c['temporal_phrases']],locative=[p['lexemes'] for p in c['locative_phrases']],
        reference_markers=[dict(word_node=w['node'],ps=w['ps'],gn=w['gn'],nu=w['nu']) for w in c['pronouns']],
        suffix_markers=[dict(word_node=w['node'],ps=w['prs_ps'],gn=w['prs_gn'],nu=w['prs_nu']) for w in c['suffixes']])


CORE=('clause_type','verbs','subjects','phrase_layout','domain','formula_atoms','participants','temporal','locative')


def clause_comparison(a,b):
    if a is None or b is None:return 'NOT_AVAILABLE'
    sa,sb=signature(a),signature(b)
    aa=[sa[k] for k in CORE];bb=[sb[k] for k in CORE]
    # A missing/Unknown domain cannot make an otherwise matching configuration exact.
    if aa==bb and sa['domain'] is not None:return 'MATCH'
    core_form=sa['verbs']==sb['verbs'] and bool(sa['verbs'])
    same_layout=sa['clause_type']==sb['clause_type'] and sa['phrase_layout']==sb['phrase_layout']
    return 'PARTIAL' if core_form or same_layout else 'DIFFERENT'


class Context:
    def __init__(self,features,targets,rules):
        self.features=sorted(features,key=lambda c:int(c['sequence_index']));self.byid={int(c['clause_id']):c for c in features}
        self.pos={int(c['clause_id']):i for i,c in enumerate(self.features)};self.targets=targets;self.rules=rules
        self.members=defaultdict(list);self.head={};self.windows={};self.signatures={}
        for t in targets:
            ids=t['clause_id'];self.head[t['audit_target_id']]=min(ids,key=lambda n:self.pos[n])
            for n in ids:self.members[n].append(t['audit_target_id'])

    def at(self,node,offset):
        pos=self.pos[node]+offset
        return self.features[pos] if 0<=pos<len(self.features) else None

    def loci(self,node):
        # An unanchored clause remains its own source-qualified locus; never nearest-target inference.
        return sorted(self.members[node]) or ['JL'+str(node)]

    def locus_order(self,locus):
        node=self.head[locus] if locus in self.head else int(locus[2:])
        return (self.pos[node],locus)

    def bundle(self,node):
        if node in self.windows:return self.windows[node]
        c=self.byid[node];i=self.pos[node];radius=self.rules['fixed_radius'];n=len(self.features)
        fixed=self.features[max(0,i-radius):min(n,i+radius+1)]
        verses={(w['chapter'],w['verse']) for w in c['words']}
        same=[x for x in self.features if verses & {(w['chapter'],w['verse']) for w in x['words']}]
        lo=hi=i;domain=c['domain']
        if domain not in self.rules['unknown_domain']:
            while lo>0 and self.features[lo-1]['domain']==domain:lo-=1
            while hi+1<n and self.features[hi+1]['domain']==domain:hi+=1
        run=self.features[lo:hi+1]
        formula=[c]
        if c['formula_atoms']:
            for other in self.features[i+1:i+3]:
                formula.append(other)
                if any(w['lex']=='>MR[' for w in other['verbal_words']):break
        subject=[c];stop=None;base=set(c['participant_surfaces'])
        for other in self.features[i+1:]:
            current=set(other['participant_surfaces'])
            if current and current!=base:stop=int(other['clause_id']);break
            subject.append(other)
        next_formula=None
        for offset,other in enumerate(self.features[i+1:],1):
            if other['formula_atoms']:
                next_formula=dict(clause_id=int(other['clause_id']),reference=other['reference'],surface=other['surface'],formula_atoms=other['formula_atoms'],clause_distance=offset)
                break
        modes={'FIXED_MINUS3_PLUS3':fixed,'SAME_VERSE_COMPLETE':same,'RAW_DOMAIN_RUN':run,
               'FORMULA_CONTINUATION':formula,'UNTIL_EXPLICIT_PARTICIPANT_CHANGE':subject}
        out=[]
        for mode,clauses in modes.items():
            ident=f'JW:{node}:{mode}';ids=[int(x['clause_id']) for x in clauses]
            out.append(dict(bundle_id=ident,focal_clause_id=node,window_type=mode,clause_ids=ids,
                clause_atom_ids=sorted({a for x in clauses for a in x['clause_atom_ids']}),
                references=[x['reference'] for x in clauses],raw_domains=[x['domain'] for x in clauses],
                surface=''.join(x['surface'] for x in clauses),participant_change_stop_clause=stop if mode=='UNTIL_EXPLICIT_PARTICIPANT_CHANGE' else None,
                next_raw_formula=next_formula,
                raw_domain_boundary_crossings=[ids[k] for k in range(1,len(ids)) if clauses[k]['domain']!=clauses[k-1]['domain']],
                boundary_policy='BOOK_CLIPPED; UNKNOWN_DOMAIN_SINGLETON; NO_HUMAN_UNIT'))
            ss=[signature(x) for x in clauses]
            self.signatures[ident]=dict(bundle_id=ident,clause_ids=ids,ordered_clause_signatures=ss,
                adjacent_explicit_surface_recurrence=[bool(set(clauses[k-1]['participant_surfaces'])&set(clauses[k]['participant_surfaces'])) for k in range(1,len(clauses))],
                adjacent_participant_set_change=[clauses[k-1]['participant_surfaces']!=clauses[k]['participant_surfaces'] for k in range(1,len(clauses))],
                participant_identity='UNRESOLVED_WHERE_NOT_EXPLICIT; SURFACE_RECURRENCE_NOT_COREFERENCE')
        self.windows[node]=out;return out

    def compare(self,left,right):
        a,b=self.byid[left],self.byid[right];self.bundle(left);self.bundle(right)
        sa,sb=signature(a),signature(b)
        focal='MATCH' if (set(a['formula_atoms'])&set(b['formula_atoms']) and sa['verbs']==sb['verbs']) else clause_comparison(a,b)
        flags={'C_FOCAL_FORM_CORRESPONDENCE':focal}
        for side,sign in [('PRECEDING',-1),('FOLLOWING',1)]:
            for step in (1,2,3):flags[f'C_{side}_{step}_CORRESPONDENCE']=clause_comparison(self.at(left,sign*step),self.at(right,sign*step))
        seq_a=[signature(self.at(left,k)) if self.at(left,k) else None for k in range(-3,4)]
        seq_b=[signature(self.at(right,k)) if self.at(right,k) else None for k in range(-3,4)]
        for name,key in [('CLAUSE','clause_type'),('VERB','verbs'),('SUBJECT','subjects'),('FORMULA','formula_atoms'),('PARTICIPANT','participants'),('DOMAIN','domain')]:
            flags['C_'+name+'_SEQUENCE_CORRESPONDENCE']=categorical([x[key] if x else None for x in seq_a],[x[key] if x else None for x in seq_b])
        flags['C_TEMPORAL_LOCATIVE_SEQUENCE_CORRESPONDENCE']=categorical([[x['temporal'],x['locative']] if x else None for x in seq_a],[[x['temporal'],x['locative']] if x else None for x in seq_b])
        for side in ('PRECEDING','FOLLOWING'):
            status=[flags[f'C_{side}_{k}_CORRESPONDENCE'] for k in (1,2,3)]
            flags[f'C_{side}_CONFIGURATION_DIVERGENCE']='DIFFERENT' if any(x=='DIFFERENT' for x in status) else 'PARTIAL' if any(x=='PARTIAL' for x in status) else 'MATCH' if all(x=='MATCH' for x in status) else 'NOT_AVAILABLE'
        flags['C_PARTICIPANT_CONFIGURATION_DIVERGENCE']=flags['C_PARTICIPANT_SEQUENCE_CORRESPONDENCE']
        flags['C_DOMAIN_CONFIGURATION_DIVERGENCE']=flags['C_DOMAIN_SEQUENCE_CORRESPONDENCE']
        follow=[flags[f'C_FOLLOWING_{k}_CORRESPONDENCE'] for k in (1,2,3)]
        preceding=[flags[f'C_PRECEDING_{k}_CORRESPONDENCE'] for k in (1,2,3)]
        if focal=='MATCH' and all(x=='MATCH' for x in follow):label='EXACT_CONFIGURATION_CORRESPONDENCE'
        elif focal=='MATCH' and all(x=='DIFFERENT' for x in follow):label='CONFIGURATION_CONTRAST'
        elif any(x=='MATCH' for x in follow) or all(x=='MATCH' for x in preceding):label='PARTIAL_CONFIGURATION_CORRESPONDENCE'
        elif focal=='MATCH':label='FOCAL_ONLY_CORRESPONDENCE'
        else:label='NO_CONTEXTUAL_CORRESPONDENCE'
        return dict(context_id=f'JX:{left}:{right}',preceding_clause_id=left,later_clause_id=right,
            preceding_bundle_ids=[x['bundle_id'] for x in self.windows[left]],later_bundle_ids=[x['bundle_id'] for x in self.windows[right]],
            flags=flags,configuration_status=label,
            following_length_checks={str(k):'MATCH' if all(x=='MATCH' for x in follow[:k]) else 'PARTIAL' if any(x in ('MATCH','PARTIAL') for x in follow[:k]) else 'DIFFERENT' if all(x=='DIFFERENT' for x in follow[:k]) else 'NOT_AVAILABLE' for k in (1,2,3)},
            status='UNADJUDICATED',automatic_resolution=False)

    def scope(self,p,h,comparison):
        left,right=int(p['preceding_clause_id']),int(p['later_clause_id']);a,b=self.byid[left],self.byid[right]
        shared=set(self.members[left])&set(self.members[right]);distinct=bool(self.members[left] and self.members[right] and not shared)
        close=self.pos[right]-self.pos[left]<=self.rules['local_distance']
        sameverse=bool({(w['chapter'],w['verse']) for w in a['words']}&{(w['chapter'],w['verse']) for w in b['words']})
        heads=distinct and any(self.head[t]==left for t in self.members[left]) and any(self.head[t]==right for t in self.members[right])
        internal=bool(shared and close and h['hypotaxis_supported'])
        bundles=h['rule_bundles']
        dep='RELATIVE_DEPENDENCY' if any('H1_' in r for r in bundles) else 'INFINITIVE_DEPENDENCY' if any('H2_' in r for r in bundles) else 'FORMULA_INTERNAL' if close and a['formula_atoms'] and any(w['lex']=='>MR[' for w in b['verbal_words']) else 'SAME_VERSE_LOCAL_EMBEDDING' if sameverse else 'CROSS_VERSE_LOCAL_DEPENDENCY' if close else 'CROSS_LOCUS_CANDIDATE'
        if internal:scope='SCOPE_A_CLAUSE_INTERNAL';projection=INTERNAL
        elif (close and not heads) or shared:scope='SCOPE_B_LOCAL_LOCUS_RELATION';projection=LOCAL
        elif heads:
            repeated=comparison['flags']['C_FOCAL_FORM_CORRESPONDENCE']=='MATCH' and all(comparison['flags'][f'C_FOLLOWING_{k}_CORRESPONDENCE']=='MATCH' for k in (1,2))
            scope='SCOPE_D_MACRO_PROJECTION_CANDIDATE' if repeated else 'SCOPE_C_CROSS_LOCUS_RELATION';projection=MACRO if repeated else CROSS
        else:scope='SCOPE_E_EVIDENCE_ONLY_NOT_MACRO_PROJECTABLE';projection=INSUFFICIENT
        return dict(pair_id=p['pair_id'],preceding_clause_id=left,later_clause_id=right,earlier_neutral_loci=self.loci(left),later_neutral_loci=self.loci(right),
            clause_relation_scope=scope,macro_projection_status=projection,local_dependency_type=dep,clause_internal_only=internal,
            cross_locus=distinct,aligned_locus_heads=heads,same_verse=sameverse,context_id=comparison['context_id'],
            status='UNADJUDICATED',automatic_resolution=False,selected_mother='')


def case_type(family,scope,configs):
    contrast=any(x in ('CONFIGURATION_CONTRAST','FOCAL_ONLY_CORRESPONDENCE') for x in configs)
    if scope==INTERNAL:return 'CTX_CLAUSE_INTERNAL_HYPOTAXIS_ONLY'
    if family=='PARATAXIS' and contrast:return 'CTX_PARATAXIS_WITH_CONFIGURATION_CONTRAST'
    if family=='HYPOTAXIS' and scope in (LOCAL,INSUFFICIENT):return 'CTX_HYPOTAXIS_WITH_COMPETING_LOCAL_EXPLANATION'
    if scope==MACRO:return 'CTX_MACRO_PROJECTION_CANDIDATE'
    if scope==CROSS:return 'CTX_CROSS_LOCUS_'+family+'_CANDIDATE'
    return 'CTX_'+family+'_SUPPORTED'


def build(blind,rules):
    targets=io.rows(blind[FROZEN_NAMES[0]]);features=io.rows(blind[FROZEN_NAMES[1]])
    pairs=io.rows(blind[FROZEN_NAMES[2]]);hyp={r['pair_id']:r for r in io.rows(blind[FROZEN_NAMES[3]])}
    io.require({p['pair_id'] for p in pairs}==set(hyp) and len(pairs)==len(hyp),'pair identity')
    ctx=Context(features,targets,rules);supported=[];archive=[];comparisons={};scopes=[];cases={};mapping=[]
    for p in pairs:
        h=hyp[p['pair_id']]
        if h['parataxis_supported'] or h['hypotaxis_supported']:supported.append(dict(pair_id=p['pair_id'],source_pair=p,source_hypothesis=h))
        else:archive.append(dict(pair_id=p['pair_id'],archive_status='ARCHIVE_INSUFFICIENT_PAIR_EVIDENCE',default_human_review=False,source_pair=p,source_hypothesis=h))
    for row in supported:
        p,h=row['source_pair'],row['source_hypothesis'];a,b=int(p['preceding_clause_id']),int(p['later_clause_id'])
        comparison=ctx.compare(a,b);comparisons[comparison['context_id']]=comparison;s=ctx.scope(p,h,comparison);scopes.append(s)
        for family in ('PARATAXIS','HYPOTAXIS'):
            if not h[family.lower()+'_supported']:continue
            for left,right in product(s['earlier_neutral_loci'],s['later_neutral_loci']):
                if family=='PARATAXIS' and ctx.locus_order(left)>ctx.locus_order(right):left,right=right,left
                ident=f"JC:{left}:{right}:{family}:{s['macro_projection_status']}"
                case=cases.setdefault(ident,dict(case_id=ident,earlier_neutral_locus=left,later_neutral_locus=right,relation_family=family,
                    projection_scope=s['macro_projection_status'],member_pair_ids=[],member_evidence_ids=[],member_hypotheses=[],context_ids=[],
                    status='UNADJUDICATED',automatic_resolution=False,selected_mother='',adjudication_applied=False))
                for field,value in [('member_pair_ids',p['pair_id']),('member_evidence_ids',p['evidence_id']),('member_hypotheses',h['relation_hypothesis']),('context_ids',comparison['context_id'])]:case[field].append(value)
                mapping.append(dict(case_id=ident,pair_id=p['pair_id'],evidence_id=p['evidence_id'],member_role='PRIMARY_SUPPORTED',original_direction=[a,b]))
    # Context/contrast auxiliaries are archived, never independent default review cases.
    auxiliary=[]
    for row in archive:
        p=row['source_pair'];a,b=int(p['preceding_clause_id']),int(p['later_clause_id'])
        if ctx.members[a] and ctx.members[b]:
            co=ctx.compare(a,b);comparisons[co['context_id']]=co
        for case in cases.values():
            if case['earlier_neutral_locus'] not in ctx.loci(a) or case['later_neutral_locus'] not in ctx.loci(b):continue
            near=any(abs(ctx.pos[a]-ctx.pos[int(x.split(':')[1])])<=3 and abs(ctx.pos[b]-ctx.pos[int(x.split(':')[2])])<=3 for x in case['context_ids'])
            if near:
                co=ctx.compare(a,b);comparisons[co['context_id']]=co
                auxiliary.append(dict(case_id=case['case_id'],pair_id=p['pair_id'],evidence_id=p['evidence_id'],context_id=co['context_id'],reason='C_ADJACENT_CONTEXT_OF_SUPPORTED_PAIR',archive_status=row['archive_status']))
    for case in cases.values():
        for field in ('member_pair_ids','member_evidence_ids','member_hypotheses','context_ids'):case[field]=sorted(set(case[field]))
        case['member_pair_count']=len(case['member_pair_ids']);case['configuration_statuses']=sorted({comparisons[k]['configuration_status'] for k in case['context_ids']})
        case['candidate_type']=case_type(case['relation_family'],case['projection_scope'],case['configuration_statuses'])
        case['auxiliary_pair_ids']=sorted({r['pair_id'] for r in auxiliary if r['case_id']==case['case_id']})
        tiers=['TIER_1_PAIRWISE_ONLY','TIER_2_PAIRWISE_PLUS_LOCAL_CONTEXT']
        if 'EXACT_CONFIGURATION_CORRESPONDENCE' in case['configuration_statuses']:tiers.append('TIER_3_REPEATED_MULTI_CLAUSE_CONFIGURATION')
        if 'HYPOTAXIS_EXPLICIT_SUBORDINATION_SUPPORTED' in case['member_hypotheses']:tiers.append('TIER_4_EXPLICIT_SUBORDINATION')
        if case['projection_scope'] in PROJECTABLE:tiers.append('TIER_5_MACRO_PROJECTION_REQUIRES_HUMAN_JUDGMENT')
        case['evidence_tiers']=tiers
    # All neutral focal-head combinations make control lookup generic and pre-human.
    heads=sorted(set(ctx.head.values()),key=lambda n:ctx.pos[n])
    for i,a in enumerate(heads):
        for b in heads[i+1:]:
            co=ctx.compare(a,b);comparisons[co['context_id']]=co
    for t in targets:
        for n in t['clause_id']:ctx.bundle(n)
    case_list=sorted(cases.values(),key=lambda r:(ctx.locus_order(r['earlier_neutral_locus']),ctx.locus_order(r['later_neutral_locus']),r['relation_family'],r['case_id']))
    return dict(targets=targets,supported=supported,archive=archive,windows=[w for n in sorted(ctx.windows) for w in ctx.windows[n]],
        signatures=[ctx.signatures[k] for k in sorted(ctx.signatures)],correspondence=[comparisons[k] for k in sorted(comparisons)],
        scopes=scopes,cases=case_list,membership=mapping,auxiliary=auxiliary,
        macro_mothers=[dict(**r,relation_family='HYPOTAXIS') for r in scopes if hyp[r['pair_id']]['hypotaxis_supported'] and not r['clause_internal_only'] and r['macro_projection_status'] in PROJECTABLE],
        clause_internal=[r for r in scopes if r['clause_internal_only']])
