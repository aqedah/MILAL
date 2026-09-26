"""Independent reference environments; no tested relation or textual hierarchy."""
from collections import defaultdict
from milal_q1_binding import identity
from milal_q12_profiles import profile, valid
from milal_q14_spans import INDEPENDENT


class Domains:
    def __init__(self, inventory, spans, lexicons):
        self.rows={str(r['clause_id']):r for r in inventory}
        self.order=sorted(self.rows,key=lambda c:int(self.rows[c]['position']))
        self.profiles={c:profile(self.rows[c],lexicons) for c in self.order}
        self.words={int(w['node']):w for r in inventory for w in r['WORD']}
        self.owners=defaultdict(set);self.domains={};self.members=defaultdict(set)
        self.spans={s['span_id']:s for s in spans};self.antecedents={}
        for c,r in self.rows.items():
            for node in [int(c),*r['word_ids'],*r['clause_atom_ids'],*(p['node'] for p in r['PHRASE'])]:self.owners[int(node)].add(c)
            self.add('LOCAL_NATIVE_CONSTRUCTION',[c],{'clause_id':c,'word_ids':r['word_ids'],'basis':'EXACT_CLAUSE_INTERNAL_GRAMMAR'})
        for s in self.spans.values():
            if s['construction_independence_status'] not in INDEPENDENT:continue
            self.add('COMPOSITE_SURFACE_SPAN',s['clause_ids'],{'span_id':s['span_id'],'boundary_witnesses':s['boundary_witnesses']})
        for c,r in self.rows.items():
            for e in r['CLAUSE']['native_annotations']:
                if e.get('status')!='DATABASE_EXISTING_RELATION' or e['resolution']!='EXACT_NODE_MEMBERSHIP':continue
                hs=self.owners[int(e['head_node'])];ds=self.owners[int(e['dependent_node'])]
                if len(hs)!=1 or ds!={c}:continue
                h=next(iter(hs))
                if h==c or self.rows[h]['book']!=r['book']:continue
                # Unspecified database sequence/coordination is not a domain.
                if e['rela'] not in lexicons['subordinate_rela'] and e.get('reference_semantics')!='EXPLICIT_ANTECEDENT':continue
                self.add('EXPLICIT_SUBORDINATION_DOMAIN' if e['rela'] in lexicons['subordinate_rela'] else 'LOCAL_NATIVE_CONSTRUCTION',
                    [h,c],{'native_annotation':e,'basis':'EXACT_NATIVE_ATTACHMENT_ENDPOINTS'})
        for c,r in self.rows.items():
            speech=bool(self.profiles[c]['direct_speech_markers'])
            for p in r['PHRASE']:
                for node in p['word_ids']:
                    w=self.words[int(node)]
                    if w['sp'] not in ('subs','nmpr','prps','prde'):continue
                    aid='ANT-'+str(node)
                    a=dict(antecedent_id=aid,word_node=int(node),clause_id=c,lexeme=w['lex'],grammatical_role=p['function'],
                        phrase_function=p['function'],phrase_node=p['node'],person=w.get('ps'),gender=w.get('gn'),number=w.get('nu'),
                        explicitness='EXPLICIT_LEXICAL_MENTION' if w['sp'] in ('subs','nmpr') else 'UNRESOLVED_PRONOMINAL_MENTION',nominal_status=w['sp'],
                        speech_role='SPEAKER_SURFACE_SUBJECT' if speech and p['function'] in ('Subj','PreS') and w['sp'] in ('subs','nmpr') else 'UNRESOLVED',
                        domain_ids=sorted(self.members[c]),span_ids=sorted(sid for sid,s in self.spans.items() if c in s['clause_ids']),
                        provenance={'word':w,'phrase':p},referential_identity='UNRESOLVED')
                    if aid in self.antecedents and self.antecedents[aid]!=a:raise ValueError('ambiguous antecedent role ownership')
                    self.antecedents[aid]=a

    def add(self,kind,members,evidence):
        if evidence.get('tested_relation_used_for_domain'):raise ValueError('circular domain')
        members=sorted(set(map(str,members)),key=lambda c:int(self.rows[c]['position']))
        d=dict(domain_type=kind,opening_clause=members[0],member_clauses=members,
            member_atoms=sorted({n for c in members for n in self.rows[c]['clause_atom_ids']}),boundary_basis=evidence,
            independence_status='INDEPENDENT_SURFACE',provenance='FROZEN_NATIVE_OBSERVATIONS',tested_relation_used_for_domain=False)
        d['domain_id']='RVD-'+identity(d);self.domains[d['domain_id']]=d
        for c in members:self.members[c].add(d['domain_id'])

    def paths(self,antecedent,target):
        a=str(antecedent);t=str(target);result=[]
        for did in sorted(self.members[a]&self.members[t]):
            d=self.domains[did]
            if d['tested_relation_used_for_domain']:raise ValueError('circular domain')
            result.append(dict(path_type='SAME_SURFACE_SPAN' if d['domain_type']=='COMPOSITE_SURFACE_SPAN' else
                'EXPLICIT_SUBORDINATION_PATH' if d['domain_type']=='EXPLICIT_SUBORDINATION_DOMAIN' else 'DIRECT_NATIVE_PATH',
                domain_ids=[did],antecedent_clause=a,target_clause=t,tested_relation_used_for_domain=False))
        # A shared observed component is an explicit two-domain overlap witness.
        # No reachability closure turns a whole connected book into one domain.
        for da in sorted(self.members[a]-self.members[t]):
            for dt in sorted(self.members[t]-self.members[a]):
                x,y=self.domains[da],self.domains[dt]
                if x['domain_type']!='COMPOSITE_SURFACE_SPAN' or y['domain_type']!='COMPOSITE_SURFACE_SPAN':continue
                overlap=sorted(set(x['member_clauses'])&set(y['member_clauses']))
                if overlap:result.append(dict(path_type='OVERLAPPING_SPAN_PATH',domain_ids=[da,dt],shared_clause_ids=overlap,
                    antecedent_clause=a,target_clause=t,tested_relation_used_for_domain=False))
        return result


def form_type(form,word):
    if form['kind']=='PRONOMINAL_SUFFIX':return 'PRONOMINAL_SUFFIX'
    if form['kind']=='IMPLICIT_SUBJECT':return 'IMPLICIT_SUBJECT_OR_ARGUMENT'
    if form['kind']=='PRONOUN_OR_DEICTIC':return 'DEICTIC_PRONOUN_OR_DETERMINER' if word['sp']=='prde' else 'INDEPENDENT_PRONOUN' if word['sp']=='prps' else 'INTERROGATIVE_PRONOUN_OR_FORM' if word['sp']=='prin' else 'UNRESOLVED'
    if form['kind']=='LEXICAL_NP':return 'EXPLICIT_PROPER_NAME_MENTION' if word['sp']=='nmpr' else 'EXPLICIT_COMMON_NP_MENTION'
    raise ValueError('unrecognized reference form '+form['kind'])


def compatibility(form,ant,paths,native=False):
    kind=form['reference_form_type'];png=form['raw_form'].get('png') or [None,None,None]
    dims={k:'NOT_APPLICABLE' for k in ('PERSON','GENDER','NUMBER','GRAMMATICAL_ROLE','EXPLICITNESS','SPEECH_ROLE','LEXICAL_ANCHOR','DOMAIN_VISIBILITY','NATIVE_REFERENCE_EVIDENCE','DEICTIC_COMPATIBILITY')}
    dims.update(EXPLICITNESS='MATCH' if ant['explicitness']=='EXPLICIT_LEXICAL_MENTION' else 'UNRESOLVED',DOMAIN_VISIBILITY='MATCH' if paths else 'CONFLICT',NATIVE_REFERENCE_EVIDENCE='MATCH' if native else 'UNRESOLVED')
    bearing=kind in ('PRONOMINAL_SUFFIX','INDEPENDENT_PRONOUN','DEICTIC_PRONOUN_OR_DETERMINER','IMPLICIT_SUBJECT_OR_ARGUMENT')
    if not bearing:
        dims['LEXICAL_ANCHOR']='MATCH' if form['raw_form']['lex']==ant['lexeme'] else 'CONFLICT'
        return dims,False,False
    for key,v,w in zip(('PERSON','GENDER','NUMBER'),png,(ant['person'],ant['gender'],ant['number'])):
        dims[key]='UNRESOLVED' if not valid(v) or not valid(w) else 'MATCH' if v==w else 'COMPATIBLE' if key=='GENDER' and 'c' in (v,w) else 'CONFLICT'
    if not valid(ant['person']) and png[0]=='p3':dims['PERSON']='COMPATIBLE'
    if png[0] in ('p1','p2'):
        expected='SPEAKER_SURFACE_SUBJECT' if png[0]=='p1' else 'ADDRESSEE_EXPLICIT_SURFACE'
        dims['SPEECH_ROLE']='MATCH' if ant['speech_role']==expected and paths else 'UNRESOLVED'
        dims['PERSON']='COMPATIBLE' if dims['SPEECH_ROLE']=='MATCH' else 'UNRESOLVED'
    if kind=='IMPLICIT_SUBJECT_OR_ARGUMENT':dims['GRAMMATICAL_ROLE']='COMPATIBLE' if ant['grammatical_role'] in ('Subj','PreS') else 'CONFLICT'
    if kind=='DEICTIC_PRONOUN_OR_DETERMINER':dims['DEICTIC_COMPATIBILITY']='COMPATIBLE' if all(dims[k] in ('MATCH','COMPATIBLE') for k in ('GENDER','NUMBER')) else 'UNRESOLVED'
    visible=bool(paths) and 'CONFLICT' not in dims.values()
    supported=visible and all(dims[k] in ('MATCH','COMPATIBLE') for k in ('PERSON','GENDER','NUMBER','EXPLICITNESS'))
    return dims,visible,supported
