"""Raw BHSA feature reader; no historical hierarchy dependencies."""
from pathlib import Path
import re
from collections import defaultdict
from milal_mfr_common import require,sha

WORD_FEATURES=('lex','lex_utf8','g_word_utf8','trailer_utf8','sp','pdp','vt','vs','ps','gn','nu','prs_ps','prs_gn','prs_nu')
FEATURES=('otype','oslots','book','chapter','verse','typ','function','domain',*WORD_FEATURES)


def numbers(spec):
    for part in spec.split(','):
        if '-' in part:
            a,b=map(int,part.split('-'));yield from range(a,b+1)
        else:yield int(part)


def read_feature(path,keep=None):
    data=Path(path).read_bytes();head,body=data.decode('utf8').lstrip('\ufeff').replace('\r\n','\n').split('\n\n',1)
    meta={line[1:].split('=',1)[0]:line.split('=',1)[1] if '=' in line else True for line in head.splitlines()}
    require(meta.get('version')=='2021','BHSA feature version must be 2021')
    require('edgeValues' not in meta,'unsupported valued edge');result={};prior=0
    for line in body.splitlines():
        parts=line.split('\t');nn=[prior+1] if len(parts)==1 else list(numbers(parts[0]));prior=nn[-1]
        nn=[n for n in nn if keep is None or n in keep]
        if not nn:continue
        value=parts[0] if len(parts)==1 else '\t'.join(parts[1:])
        if 'edge' in meta:value=list(numbers(value))
        elif meta.get('valueType')=='int':
            if value=='':continue
            value=int(value)
        else:value=re.sub(r'\\([\\nt])',lambda m:{'\\':'\\','n':'\n','t':'\t'}[m[1]],value)
        for n in nn:result[n]=value
    return result,dict(feature=Path(path).name,version=meta['version'],sha256=sha(data))


def raw_corpus(path,books):
    path=Path(path);receipts=[]
    def read(name,keep=None):
        require(name in FEATURES,'feature whitelist');value,receipt=read_feature(path/(name+'.tf'),keep);receipts.append(receipt);return value
    typ=read('otype');book=read('book');bn={n:v for n,v in book.items() if typ.get(n)=='book' and v in books}
    require(set(bn.values())==set(books),'configured books missing')
    # Only raw membership edges, never textual hierarchy relations.
    edges=read('oslots');ws={w for n in bn for w in edges[n]};book_of={w:b for n,b in bn.items() for w in edges[n]}
    edges={n:v for n,v in edges.items() if v and v[0] in ws and all(w in ws for w in v)};nodes=set(edges)|ws
    ff={f:read(f,ws if f in WORD_FEATURES else nodes) for f in FEATURES if f not in ('otype','book','oslots')}
    ch={w:ff['chapter'][n] for n,v in edges.items() if typ[n]=='chapter' for w in v};ve={w:ff['verse'][n] for n,v in edges.items() if typ[n]=='verse' for w in v}
    lookup={k:defaultdict(set) for k in ('phrase','clause_atom')}
    for n,v in edges.items():
        if typ[n] in lookup:
            for w in v:lookup[typ[n]][w].add(n)
    raw=[]
    for n,v in sorted(edges.items(),key=lambda x:(x[1][0],x[0])):
        if typ[n]!='clause':continue
        require(all(all(w in ff[k] for k in ('lex','sp','g_word_utf8')) for w in v),'required word schema')
        words=[dict(node=w,**{f:ff[f].get(w) for f in WORD_FEATURES}) for w in v]
        phrases=[dict(node=p,word_ids=[w for w in edges[p] if w in v],function=ff['function'].get(p),typ=ff['typ'].get(p)) for p in sorted({p for w in v for p in lookup['phrase'][w]},key=lambda x:edges[x][0])]
        atoms=[dict(node=a,word_ids=[w for w in edges[a] if w in v],typ=ff['typ'].get(a)) for a in sorted({a for w in v for a in lookup['clause_atom'][w]},key=lambda x:edges[x][0])]
        raw.append(dict(book=book_of[v[0]],chapter=ch[v[0]],verse=ve[v[0]],clause_id=n,clause_atom_ids=[a['node'] for a in atoms],atoms=atoms,word_ids=v,words=words,phrases=phrases,clause_type=ff['typ'].get(n),domain=ff['domain'].get(n)))
    allwords=[w for c in raw for w in c['word_ids']];require(len(allwords)==len(ws) and set(allwords)==ws,'complete scope word coverage')
    return observe(raw),receipts


def observe(raw):
    out=[]
    for i,c in enumerate(raw):
        require({'book','chapter','verse','clause_id','clause_atom_ids','word_ids','words','phrases','atoms','clause_type','domain'}==set(c),'raw schema: unknown derived fields prohibited')
        require(c['clause_atom_ids'] and c['word_ids'],'canonical anchor missing');words=c['words'];wmap={w['node']:w for w in words}
        def surface(ids):return ''.join((wmap[w].get('g_word_utf8') or '')+(wmap[w].get('trailer_utf8') or '') for w in ids)
        phrases=[dict(p,surface=surface(p['word_ids']),lexemes=[wmap[w]['lex'] for w in p['word_ids']]) for p in c['phrases']]
        def ps(funcs):return [p for p in phrases if p['function'] in funcs]
        subjects=ps(['Subj','PreS']);objects=ps(['Objc','PreO']);complements=ps(['Cmpl']);address=ps(['Cmpl','Adju'])
        verbs=[w for w in words if w['sp']=='verb'];participant=[w['lex'] for p in subjects+objects+complements for n in p['word_ids'] if (w:=wmap[n])['sp'] not in ('prep','art','conj')]
        out.append(dict(c,sequence_index=i,anchor=c['clause_atom_ids'][0],surface_hebrew=surface(c['word_ids']),phrases=phrases,
            predicate_lexeme=[w['lex'] for w in verbs],predicate_morphology=[{k:w.get(k) for k in ('node','vt','vs','ps','gn','nu')} for w in verbs],verbal_conjugation=[w.get('vt') for w in verbs],
            subject_surface=[p['surface'] for p in subjects],subject_lexemes=[wmap[n]['lex'] for p in subjects for n in p['word_ids']],object_surface=[p['surface'] for p in objects],complement_surface=[p['surface'] for p in complements],
            addressee_surface=[p['surface'] for p in address],addressee_limitation='COMPLEMENT_SURFACE_NOT_RESOLVED_ROLE',phrase_function_sequence=[p['function'] for p in phrases],phrase_type_sequence=[p['typ'] for p in phrases],constituent_order=[p['function'] for p in phrases],
            conjunction=[w['lex'] for w in words if w['sp']=='conj'],prepositions=[w['lex'] for w in words if w['sp']=='prep'],temporal_phrase_surface=[p['surface'] for p in ps(['Time'])],temporal_phrase_structure=ps(['Time']),
            locative_phrase_surface=[p['surface'] for p in ps(['Loca'])],locative_phrase_structure=ps(['Loca']),participant_surface_set=sorted(set(participant)),lexeme_sequence=[w['lex'] for w in words],pos_sequence=[w['sp'] for w in words],
            reported_speech_features=dict(raw_domain=c['domain'],predicate_lexemes=[w['lex'] for w in verbs],identity='UNRESOLVED')))
    require(len({c['clause_id'] for c in out})==len(out),'duplicate clause identity');return out
