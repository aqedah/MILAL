"""Several simultaneous resolutions; none is a privileged hierarchy."""
from milal_mfr_common import js,sha

def key(value):return sha(js(value))[:24]

def signatures(obs):
    rows=[];by_clause={}
    for i,c in enumerate(obs):
        variants=[('clause',c['clause_id'],set(c['word_ids']))]+[('clause_atom',a['node'],set(a['word_ids'])) for a in c['atoms']]
        for kind,node,ids in variants:
            ww=[w for w in c['words'] if w['node'] in ids];pp=[p for p in c['phrases'] if set(p['word_ids'])&ids]
            slot=[('PARTICIPANT' if w['sp']=='nmpr' else w['lex'],w['sp'],w.get('vt'),w.get('vs')) for w in ww]
            adjunct=[p['function'] for p in pp if p['function'] not in ('Pred','PreS','PreO','Subj','Objc','Cmpl','Conj')]
            values={'SIG_EXACT':dict(words=[[w.get(k) for k in ('lex','sp','vt','vs','ps','gn','nu')] for w in ww],order=[p['function'] for p in pp],type=c['clause_type']),
                'SIG_LEXICAL_SLOT':dict(words=slot,order=[p['function'] for p in pp]),
                'SIG_CONSTRUCTION':dict(type=c['clause_type'],verbal=[[w.get('vt'),w.get('vs')] for w in ww if w['sp']=='verb'],order=[p['function'] for p in pp],adjunct=adjunct),
                'SIG_ADJUNCT':dict(adjuncts=adjunct,time=sum(p['function']=='Time' for p in pp),loca=sum(p['function']=='Loca' for p in pp))}
            for size in (2,3,4):
                seq=obs[i:i+size]
                values['SIG_SEQUENCE_'+str(size)]=dict(complete=len(seq)==size,clauses=[dict(predicate=n['predicate_lexeme'],morph=n['verbal_conjugation'],order=n['constituent_order'],type=n['clause_type']) for n in seq])
            ss={name:key(value) for name,value in values.items()}
            if kind=='clause':by_clause[c['clause_id']]=ss
            for name,value in values.items():rows.append(dict(signature_id=f'{kind}:{node}:{name}',clause_id=c['clause_id'],clause_atom_ids=c['clause_atom_ids'],object_kind=kind,object_id=node,resolution=name,signature_hash=ss[name],definition=value,original_lexemes=[w['lex'] for w in ww],scope_limit='OUTSIDE_SCOPE_NOT_TESTED'))
    return rows,by_clause
