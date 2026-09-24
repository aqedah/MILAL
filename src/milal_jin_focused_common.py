"""Neutral linguistic helpers for three independent focused blind processes."""
import json
from pathlib import Path
import milal_jin_io as io
import milal_jin_relation_rules as rr
import milal_jin_context_configuration as cc


def normalized(features):
    for c in features:
        for k in ('clause_id','sequence_index','word_start','word_end','chapter','verse'):c[k]=int(c[k])
    return sorted(features,key=lambda c:c['sequence_index'])


class Evidence:
    def __init__(self,features,targets,rules,context_rules,linguistic_rules):
        self.features=normalized(features);self.targets=targets;self.rules=rules;self.linguistic=linguistic_rules
        self.ctx=cc.Context(self.features,targets,context_rules);self.byid=self.ctx.byid
    def at_ref(self,ref):
        a,b=map(int,ref.split(':'));out=[c for c in self.features if any(w['chapter']==a and w['verse']==b for w in c['words'])]
        io.require(out,'reference absent: '+ref);return out
    def head(self,ref):return self.at_ref(ref)[0]
    def raw(self,c):
        return dict(clause_id=c['clause_id'],clause_atom_ids=c['clause_atom_ids'],reference=c['reference'],surface=c['surface'],signature=cc.signature(c),word_nodes=c['word_nodes'])
    def config(self,clauses):
        return dict(clause_ids=[c['clause_id'] for c in clauses],participants=sorted({p for c in clauses for p in c['participant_surfaces']}),subjects=[c['subject_lexemes'] for c in clauses],domains=[c['domain'] for c in clauses],verbs=[[w['lex'] for w in c['verbal_words']] for c in clauses],lexemes=sorted({l for c in clauses for l in c['content_lexemes']}))
    def resumption(self,earlier,target,immediate):
        a,b,c=map(self.config,(earlier,target,immediate))
        p=set(a['participants'])&set(b['participants']);im=set(c['participants'])&set(b['participants'])
        lex=set(a['lexemes'])&set(b['lexemes']);nonim=lex-set(c['lexemes'])
        # Surface argument recurrence only; never recovered identity or a hierarchy decision.
        return dict(earlier=a,target=b,immediate=c,shared_participant_surfaces=sorted(p),immediate_shared_participants=sorted(im),shared_content_lexemes=sorted(lex),earlier_only_recurrent_lexemes=sorted(nonim),
            participant_resumption=bool(p-im),lexical_configuration_resumption=bool(nonim and a['domains']==b['domains']),
            candidate=bool(p-im or (nonim and a['domains']==b['domains'])),identity='UNRESOLVED; SURFACE_RECURRENCE_ONLY')
    def pair(self,left,right):
        ev=rr.evidence(left,right,self.linguistic);cx=self.ctx.compare(left['clause_id'],right['clause_id'])
        return dict(preceding=self.raw(left),target=self.raw(right),clause_evidence=ev,context=cx,
            closure_onset_surface=dict(preceding_closure_lexemes=sorted(set(left['lexemes'])&set(self.rules['closure_lexemes'])),target_formula_atoms=right['formula_atoms']),
            limitations=['FORMAL_EVIDENCE_NOT_ACCEPTED_RELATION','MORPHOLOGICAL_COMPATIBILITY_NOT_COREFERENCE'],status='UNADJUDICATED',selected_mother='',automatic_resolution=False)
    def local_pair(self,a,b,pair_id):
        ev=rr.evidence(a,b,self.linguistic);cx=self.ctx.compare(a['clause_id'],b['clause_id'])
        p=dict(pair_id=pair_id,preceding_clause_id=a['clause_id'],later_clause_id=b['clause_id'])
        return self.ctx.scope(p,ev,cx)
    def window_files(self):
        return {'windows.csv':io.csv_bytes([r for rs in self.ctx.windows.values() for r in rs]),'signatures.csv':io.csv_bytes(list(self.ctx.signatures.values()))}


def macro_hypothesis(evidence,resumption,source_main,target_main):
    ev=evidence['clause_evidence'];f=ev['evidence_flags'];cx=evidence['context']['flags']
    independent_scope=bool(source_main and target_main and not f['S_RELATIVE_CONSTRUCTION'] and not f['S_INFINITIVE_DEPENDENCY'])
    hypo=bool(independent_scope and ev['hypotaxis_supported'] and f['R_EXPLICIT_PARTICIPANT_RECURRENCE'] and (f['S_ANAPHORIC_DEPENDENCY'] or f['D_EMBEDDED_LINE_CANDIDATE']) and cx['C_FOCAL_FORM_CORRESPONDENCE'] in ('MATCH','PARTIAL'))
    para=bool(independent_scope and ev['parataxis_supported'])
    labels=[]
    if hypo:labels.append('C_MACRO_HYPOTAXIS_CANDIDATE')
    if para:labels.append('C_MACRO_PARATAXIS_CANDIDATE')
    if resumption['candidate']:labels.append('C_RESUMPTIVE_PLACEMENT_CANDIDATE')
    if evidence['closure_onset_surface']['preceding_closure_lexemes'] and ev['eligible']:labels.append('C_TRANSITIONAL_PLACEMENT_CANDIDATE')
    if not hypo:labels.append('C_NO_MACRO_MOTHER_SUPPORT')
    if not (hypo or para or resumption['candidate']):labels.append('C_INSUFFICIENT_EVIDENCE')
    return dict(hypotheses=labels,retained=bool(ev['eligible'] or resumption['candidate']),macro_mother_supported=hypo,local_dependency_not_projected=not independent_scope,status='UNADJUDICATED',selected_mother='')


def table(rows,columns):
    def cell(v):return str(v).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(columns)+' |\n|'+ '|'.join('---' for _ in columns)+'|\n'+''.join('| '+' | '.join(cell(r.get(k,'')) for k in columns)+' |\n' for r in rows)
