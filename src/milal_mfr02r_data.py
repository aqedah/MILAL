"""Streaming, deterministic tables and hash manifests for large candidate universes."""
import csv
import gzip
import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

COMPACT_TABLES = False


def physical_path(path):
    path = Path(path)
    if not path.exists() and path.suffix == '.csv' and Path(str(path) + '.gz').exists():
        return Path(str(path) + '.gz')
    return path


def logical_stream(path):
    path = Path(path)
    return gzip.open(path, 'rb') if path.name.endswith('.csv.gz') else path.open('rb')


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


class Table:
    def __init__(self, path, fields):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.binary = None
        if COMPACT_TABLES:
            self.path = Path(str(self.path) + '.gz')
            self.binary = self.path.open('wb')
            self.file = io.TextIOWrapper(gzip.GzipFile(filename='', mode='wb', fileobj=self.binary, mtime=0, compresslevel=1), encoding='utf8', newline='')
        else:
            self.file = self.path.open('w', encoding='utf8', newline='')
        self.writer = csv.DictWriter(self.file, fields, lineterminator='\n')
        self.writer.writeheader()
        self.count = 0

    def write(self, row):
        self.writer.writerow({k: encode(v) if isinstance(v, (dict, list, tuple, bool)) or v is None else v for k, v in row.items()})
        self.count += 1

    def close(self):
        self.file.close()
        if self.binary:
            self.binary.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def table(path, rows, fields=None):
    it = iter(rows)
    first = next(it, None)
    with Table(path, fields or (list(first) if first is not None else ['empty'])) as out:
        if first is not None:
            out.write(first)
        for row in it:
            out.write(row)


def parse(stream):
    limit = sys.maxsize
    while True:
        try:
            csv.field_size_limit(limit)
            break
        except OverflowError:
            limit //= 10
    for row in csv.DictReader(stream):
        for key, value in row.items():
            if value and (value.startswith(('[', '{')) or value in ('true', 'false', 'null')):
                row[key] = json.loads(value)
        yield row


def rows(path):
    with logical_stream(physical_path(path)) as binary, io.TextIOWrapper(binary, encoding='utf8', newline='') as stream:
        yield from parse(stream)


def zip_rows(archive, member):
    with archive.open(member) as binary, io.TextIOWrapper(binary, encoding='utf8', newline='') as stream:
        yield from parse(stream)


def manifest(directory):
    directory = Path(directory)
    records = [dict(path=p.relative_to(directory).as_posix(), sha256=digest(p))
               for p in sorted(directory.rglob('*')) if p.is_file() and p != directory / '99_manifest_sha256.csv']
    # Keep physical-storage manifests uncompressed for independent inspection.
    previous = globals()['COMPACT_TABLES']; globals()['COMPACT_TABLES'] = False
    try:
        table(directory / '99_manifest_sha256.csv', records)
    finally:
        globals()['COMPACT_TABLES'] = previous
    return records


def verify_manifest(directory):
    directory = Path(directory)
    records = list(rows(directory / '99_manifest_sha256.csv'))
    actual = {p.relative_to(directory).as_posix() for p in directory.rglob('*') if p.is_file() and p != directory / '99_manifest_sha256.csv'}
    return actual == {r['path'] for r in records} and all(digest(directory / r['path']) == r['sha256'] for r in records)


def pack(directory, destination):
    """Preserve frozen bytes and manifest identities, including compressed tables."""
    directory = Path(directory)
    if not verify_manifest(directory):
        raise ValueError('manifest invalid')
    with zipfile.ZipFile(destination, 'x') as archive:
        for path in sorted(directory.rglob('*')):
            if not path.is_file():
                continue
            name = path.relative_to(directory).as_posix()
            info = zipfile.ZipInfo(name, (2000, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_STORED if name.endswith('.gz') else zipfile.ZIP_DEFLATED
            with path.open('rb') as stream, archive.open(info, 'w', force_zip64=True) as out:
                while chunk := stream.read(1024 * 1024):
                    out.write(chunk)
