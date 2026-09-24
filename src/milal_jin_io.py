"""Neutral serialization and raw TF readers; no human-registry imports."""
from __future__ import annotations
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import zipfile

csv.field_size_limit(64*1024*1024)


def require(ok,message):
    if not ok:raise ValueError('JIN.0.2 SCHEMA/AUDIT ERROR: '+message)


def sha(data):return hashlib.sha256(data).hexdigest()
def js(value):return (json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()


def csv_bytes(records,fields=None):
    fields=fields or (list(records[0]) if records else [])
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in records:
        writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':')) if isinstance(v,(dict,list,bool)) or v is None else v for k,v in row.items()})
    return stream.getvalue().encode('utf-8')


def rows(data):
    out=[]
    for r in csv.DictReader(io.StringIO(data.decode('utf-8').lstrip('\ufeff'))):
        item={}
        for k,v in r.items():
            if v in ('True','False'):v=v=='True'
            if isinstance(v,str) and v and (v[0] in '[{' or v in ('true','false','null')):
                try:v=json.loads(v)
                except ValueError:pass
            item[k]=v
        out.append(item)
    return out


def seal(files,name='99_manifest_sha256.csv'):
    files[name]=csv_bytes([dict(path=k,sha256=sha(v)) for k,v in sorted(files.items()) if k!=name])


def manifest_ok(files,name='99_manifest_sha256.csv'):
    try:
        rr=rows(files[name]);key='path' if rr and 'path' in rr[0] else 'file'
        return len(rr)==len(files)-1 and {r[key] for r in rr}==set(files)-{name} and all(sha(files[r[key]])==r['sha256'] for r in rr)
    except (KeyError,ValueError):return False


def read_dir(path):return {p.relative_to(path).as_posix():p.read_bytes() for p in sorted(Path(path).rglob('*')) if p.is_file()}


def publish(files,path,zip_output=True):
    path=Path(path);zp=path.with_name(path.name+'_results.zip')
    require(not path.exists() and (not zip_output or not zp.exists()),'output already exists')
    path.mkdir(parents=True)
    for name,data in sorted(files.items()):
        dest=path/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    if zip_output:
        with zipfile.ZipFile(zp,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
            for name,data in sorted(files.items()):
                info=zipfile.ZipInfo(name,(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o600<<16;z.writestr(info,data)
    return zp


def archive(data):
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names=z.namelist();require(len(names)==len(set(names)) and z.testzip() is None,'ZIP identity/CRC')
        require(all(not Path(k).is_absolute() and '..' not in Path(k).parts and '\\' not in k for k in names),'ZIP paths')
        return {k:z.read(k) for k in names}


def specs(value):
    result=[]
    for part in value.split(','):
        if '-' in part:
            start,end=map(int,part.split('-'));result.extend(range(start,end+1))
        else:result.append(int(part))
    return result


def read_tf(path,keep=None,slot_bounds=None):
    """TF documented implicit-node/range format, with explicit restricted feature calls."""
    data=Path(path).read_bytes();text=data.decode('utf-8').lstrip('\ufeff');header,body=text.split('\n\n',1) if '\n\n' in text else text.replace('\r\n','\n').split('\n\n',1)
    header=header.replace('\r','');body=body.replace('\r\n','\n')
    meta={line[1:].split('=',1)[0]:line.split('=',1)[1] if '=' in line else True for line in header.splitlines()}
    require(meta.get('version')=='2021' or meta.get('version')=='SYNTHETIC','TF version')
    edge='edge' in meta;require('edgeValues' not in meta,'valued edges not supported in this allowlist')
    result={};previous=0
    for line in body.splitlines():
        parts=line.split('\t')
        if len(parts)==1:nodes=[previous+1];value=parts[0]
        else:nodes=specs(parts[0]);value='\t'.join(parts[1:])
        previous=max(nodes)
        selected=[n for n in nodes if keep is None or n in keep]
        if not selected:continue
        if edge:
            if slot_bounds:
                ranges=[tuple(map(int,p.split('-'))) if '-' in p else (int(p),int(p)) for p in value.split(',')]
                if not any(a<=slot_bounds[1] and b>=slot_bounds[0] for a,b in ranges):continue
            value=specs(value)
        elif meta.get('valueType')=='int':
            if value=='':continue
            value=int(value)
        else:value=re.sub(r'\\([\\nt])',lambda m:{'\\':'\\','n':'\n','t':'\t'}[m[1]],value)
        for n in selected:result[n]=value
    return result,dict(feature=Path(path).stem,sha256=sha(data),version=meta['version'],bytes=len(data))


WORD_FEATURES=('lex','lex_utf8','g_word_utf8','trailer_utf8','sp','pdp','vt','vs','ps','gn','nu','prs_ps','prs_gn','prs_nu')
RAW_FEATURES=('otype','oslots','book','chapter','verse','typ','function','domain','txt',*WORD_FEATURES)
NATIVE_FEATURES=('mother','tab','pargr','rela','code')


def raw_corpus(path,book='Job'):
    """Read only the named linguistic TF files, never a directory feature scan."""
    path=Path(path);receipts={}
    def read(name,**kw):
        require(name in RAW_FEATURES,'feature not allowed in discovery: '+name)
        value,receipt=read_tf(path/(name+'.tf'),**kw);receipts[name]=receipt;return value
    books=read('book');hits=[n for n,b in books.items() if b==book]
    book_types=read('otype',keep=set(hits));hits=[n for n in hits if book_types.get(n)=='book']
    require(len(hits)==1,'book identity')
    slots=read('oslots',keep=set(hits))[hits[0]];wordset=set(slots)
    edges=read('oslots',slot_bounds=(min(slots),max(slots)))
    edges={n:ws for n,ws in edges.items() if set(ws)<=wordset}
    node_ids=set(edges)|wordset;types=read('otype',keep=node_ids)
    ff={name:read(name,keep=wordset if name in WORD_FEATURES else node_ids) for name in RAW_FEATURES if name not in ('book','oslots','otype')}
    chapter_of={w:ff['chapter'][n] for n,ws in edges.items() if types[n]=='chapter' for w in ws}
    verse_of={w:ff['verse'][n] for n,ws in edges.items() if types[n]=='verse' for w in ws}
    byword={kind:{} for kind in ('phrase','clause_atom')}
    for n,ws in edges.items():
        if types[n] in byword:
            for w in ws:byword[types[n]].setdefault(w,[]).append(n)
    result=[]
    for n,ws in sorted(edges.items(),key=lambda item:(min(item[1]),item[0])):
        if types[n]!='clause':continue
        words=[]
        for w in ws:
            require(all(w in ff[k] for k in ('lex','sp','g_word_utf8')),'required word feature')
            words.append(dict(node=w,**{k:ff[k].get(w) for k in WORD_FEATURES},chapter=chapter_of[w],verse=verse_of[w]))
        phrases=[]
        for pn in sorted({pn for w in ws for pn in byword['phrase'].get(w,[])},key=lambda p:min(edges[p])):
            pw=[w for w in edges[pn] if w in set(ws)]
            phrases.append(dict(node=pn,word_nodes=pw,function=ff['function'].get(pn),typ=ff['typ'].get(pn)))
        result.append(dict(clause_id=n,clause_atom_ids=sorted({an for w in ws for an in byword['clause_atom'].get(w,[])}),
            chapter=chapter_of[ws[0]],verse=verse_of[ws[0]],reference=str(chapter_of[ws[0]])+':'+str(verse_of[ws[0]]),
            word_start=min(ws),word_end=max(ws),word_nodes=ws,surface=''.join(w['g_word_utf8']+(w['trailer_utf8'] or '') for w in words),
            clause_type=ff['typ'].get(n),domain=ff['domain'].get(n),text_type=ff['txt'].get(n),words=words,phrases=phrases))
    observed=[w for c in result for w in c['word_nodes']]
    require(sorted(observed)==sorted(slots) and len(observed)==len(set(observed)),'whole-book clause word coverage')
    return result,sorted(receipts.values(),key=lambda r:r['feature'])
