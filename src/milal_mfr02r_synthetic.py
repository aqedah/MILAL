"""Small source-neutral synthetic observations; never imported by the blind worker."""
from milal_mfr_observation import observe

def clause(cid, typ='WayX', subject='A/', complement='B/', verb='>MR[', time=None, location=None,
           subordinate=False, domain='N', book='Synthetic', suffix=False):
    words, phrases = [], []
    def add(lex, sp, function, ps='p3', gn='m', nu='sg', vt=None):
        node = cid * 100 + len(words) + 1
        words.append(dict(node=node, lex=lex, lex_utf8=lex, g_word_utf8=lex, trailer_utf8=' ', sp=sp, pdp=sp,
                          ps=ps, gn=gn, nu=nu, vt=vt, vs='qal' if sp == 'verb' else None,
                          prs_ps='p3' if suffix else None, prs_gn='m' if suffix else None, prs_nu='sg' if suffix else None))
        phrases.append(dict(node=cid * 1000 + len(phrases), word_ids=[node], function=function, typ='VP' if sp == 'verb' else 'NP'))
    if subordinate:
        add('KJ', 'conj', 'Conj')
    if verb:
        add(verb, 'verb', 'Pred', vt='wayq' if typ.startswith('Way') else 'impf')
    if subject:
        add(subject, 'subs', 'Subj')
    if complement:
        add(complement, 'subs', 'Cmpl')
    if time:
        add(time, 'subs', 'Time')
    if location:
        add(location, 'subs', 'Loca')
    atom = cid * 10000
    return dict(book=book, chapter=1, verse=cid, clause_id=cid, clause_atom_ids=[atom],
                atoms=[dict(node=atom, word_ids=[w['node'] for w in words], typ=typ)],
                word_ids=[w['node'] for w in words], words=words, phrases=phrases, clause_type=typ, domain=domain)


def sample():
    return observe([clause(1, subject='A/', complement='B/', time='JWM/', location='X/'),
                    clause(2, subject='B/', complement='C/', time='CNH/', location='Y/'),
                    clause(3, subject='A/', complement='B/', time='JWM/', location='X/'),
                    clause(4, typ='NmCl', verb=None, subject='ZH', complement='B/'),
                    clause(5, typ='Ptcp', subordinate=True, subject='B/'),
                    clause(6, typ='Way0', verb='HJH[', subject=None, time='JWM/'),
                    clause(7, typ='Way0', verb='HJH[', subject=None, time='JWM/')])


