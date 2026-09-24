"""Deterministic, structure-neutral serialization for MFR."""
from pathlib import Path
import csv
import hashlib
import io
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def js(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))+'\n').encode('utf8')


def csv_bytes(rows, fields=None):
    rows=list(rows); fields=fields or (list(rows[0]) if rows else ['empty'])
    stream=io.StringIO(newline=''); writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n');writer.writeheader()
    for row in rows:
        writer.writerow({k:js(v).decode().strip() if isinstance(v,(dict,list,bool)) or v is None else v for k,v in row.items()})
    return stream.getvalue().encode('utf8')


def rows(data):
    csv.field_size_limit(128*1024*1024);out=[]
    for row in csv.DictReader(io.StringIO(data.decode('utf8').lstrip('\ufeff'))):
        for k,v in row.items():
            if v and (v[0] in '[{' or v in ('true','false','null')):
                try:row[k]=json.loads(v)
                except ValueError:pass
        out.append(row)
    return out


def write(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)


def manifest(directory, name):
    directory=Path(directory)
    rr=[dict(path=p.relative_to(directory).as_posix(),sha256=sha(p.read_bytes())) for p in sorted(directory.rglob('*')) if p.is_file() and p.name!=name]
    write(directory/name,csv_bytes(rr));return sha((directory/name).read_bytes())


def verify(directory,name):
    directory=Path(directory);rr=rows((directory/name).read_bytes())
    actual={p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file()}-{name}
    return len(rr)==len(actual) and {r['path'] for r in rr}==actual and all(sha((directory/r['path']).read_bytes())==r['sha256'] for r in rr)


def deterministic_zip(directory):
    directory=Path(directory);dest=directory.with_name(directory.name+'_results.zip');require(not dest.exists(),'ZIP exists')
    with zipfile.ZipFile(dest,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for path in sorted(directory.rglob('*')):
            if not path.is_file():continue
            info=zipfile.ZipInfo(path.relative_to(directory).as_posix(),(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o600<<16
            with path.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
                while chunk:=src.read(1024*1024):dst.write(chunk)
    return dest
