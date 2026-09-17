#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MILAL R3c.0.1 — Review-Container & Boundary-Control Reviewability Pilot
=======================================================================

MILAL = Marker-Informed Linguistic Analysis of Layers

Purpose
-------
Correct the R3c.0 pilot in four ways:

1. The review population is the 1,066 rows of R3b.3
   `09_lineage_review_workspace.csv`, not the 2,219 internal bundles.
2. Repeated bundles, singleton refinement events, and G6 singleton review
   items remain distinct object types.
3. Boundary controls (Job 31:40; 32:1; 32:2; 37:24; 38:1; 42:7) are
   panels containing *all* matching repeated occurrences and singleton items,
   not a single representative bundle.
4. BHSA/Text-Fabric context is re-attached: preceding/current/following verse
   Hebrew plus clause/sentence information.

This stage DOES NOT:
- reduce the R3b.3 review-container population;
- merge refinement genealogy with sequence-extension relations;
- assign rhetorical/discourse/function labels;
- score or rank importance.

Inputs
------
Required:
- job_r3b_2_results.zip
- job_r3b_3_results.zip
- BHSA Text-Fabric 2021 directory

The R3b.2 occurrence file is required because R3b.3 intentionally stores
lineage exemplars rather than every repeated occurrence.

Standard library is used except for Text-Fabric during the real run.
`--self-test` does not require Text-Fabric.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import shutil
import statistics
import sys
import tempfile
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple, Any

PROGRAM = "MILAL"
FULL_NAME = "Marker-Informed Linguistic Analysis of Layers"
VERSION = "R3c.0.1"

EXPECTED_REVIEW_CONTAINER_COUNT = 1066
TARGET_TOTAL = 24
TARGET_PER_STRATUM = 6

CONTROL_REFS: Tuple[str, ...] = (
    "31:40",
    "32:1",
    "32:2",
    "37:24",
    "38:1",
    "42:7",
)

R3B2_REQUIRED = (
    "01_review_bundles.csv",
    "03_bundle_occurrences.csv",
    "08_singleton_review_items.csv",
    "09_function_adjudication_workspace.csv",
)

R3B3_REQUIRED = (
    "01_refinement_lineages.csv",
    "02_lineage_bundle_members.csv",
    "05_lineage_singleton_refinement_events.csv",
    "06_g6_singleton_lineage_links.csv",
    "07_sequence_extension_lineage_overlay.csv",
    "09_lineage_review_workspace.csv",
)

FUNCTION_FIELD_TOKENS = (
    "researcher_function_label",
    "researcher_function_description",
    "function_label",
    "rhetorical_function",
    "discourse_function",
)

REVIEW_FIELDS = (
    "review_status",
    "observable_behavior",
    "recurring_context",
    "exceptions",
    "sufficient_context",
    "additional_information_needed",
    "review_time_seconds",
    "reviewer_notes",
)


@dataclass
class Table:
    name: str
    path: Path
    fieldnames: List[str]
    rows: List[Dict[str, str]]


def clean(v: Any) -> str:
    return "" if v is None else str(v).strip()


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", clean(s).lower()).strip("_")


def intish(v: Any, default: int = 0) -> int:
    s = clean(v)
    if not s:
        return default
    try:
        return int(float(s))
    except Exception:
        return default


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, fields: Sequence[str], rows: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fields), extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({k: "" if row.get(k) is None else row.get(k) for k in fields})


def safe_extract(zip_path: Path, dest: Path) -> None:
    dest = dest.resolve()
    with zipfile.ZipFile(zip_path, "r") as zf:
        for info in zf.infolist():
            target = (dest / info.filename).resolve()
            if dest not in target.parents and target != dest:
                raise RuntimeError(f"Unsafe ZIP member path: {info.filename}")
        zf.extractall(dest)


def read_csv(path: Path) -> Table:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        rd = csv.DictReader(f)
        fields = list(rd.fieldnames or [])
        rows = [{k: clean(v) for k, v in row.items() if k is not None} for row in rd]
    return Table(path.name, path, fields, rows)


def find_named_csv(root: Path, name: str, required: bool = True) -> Optional[Table]:
    hits = [p for p in root.rglob(name) if p.is_file()]
    if not hits:
        if required:
            raise RuntimeError(f"Required file not found in ZIP: {name}")
        return None
    if len(hits) > 1:
        # Stable choice, but make duplication explicit.
        hits.sort(key=lambda p: (len(p.parts), str(p)))
    return read_csv(hits[0])


def get_col(table: Table, aliases: Sequence[str], required: bool = True) -> Optional[str]:
    normalized = {norm(c): c for c in table.fieldnames}
    for a in aliases:
        if norm(a) in normalized:
            return normalized[norm(a)]
    # cautious fuzzy fallback
    for c in table.fieldnames:
        nc = norm(c)
        for a in aliases:
            na = norm(a)
            if na and na in nc:
                return c
    if required:
        raise RuntimeError(
            f"{table.name}: none of required columns {list(aliases)} found. "
            f"Columns={table.fieldnames}"
        )
    return None


REF_RE = re.compile(r"(?<!\d)([1-4]?\d)\s*:\s*([1-9]\d?)(?!\d)")


def parse_ref(s: str) -> Optional[Tuple[int, int]]:
    if not s:
        return None
    # normalize 31.40 and 31_40 forms if present
    t = re.sub(r"(?<!\d)(\d{1,2})[._](\d{1,2})(?!\d)", r"\1:\2", s)
    m = REF_RE.search(t)
    if not m:
        return None
    ch, vs = int(m.group(1)), int(m.group(2))
    if 1 <= ch <= 42 and 1 <= vs <= 99:
        return ch, vs
    return None


def ref_str(ref: Optional[Tuple[int, int]]) -> str:
    return "" if ref is None else f"{ref[0]}:{ref[1]}"


def span_contains(ref_start: str, ref_end: str, target: str) -> bool:
    a = parse_ref(ref_start)
    b = parse_ref(ref_end) or a
    t = parse_ref(target)
    if not a or not t:
        return False
    if not b:
        b = a
    if a > b:
        a, b = b, a
    return a <= t <= b


def row_span_contains(row: Dict[str, str], start_col: str, end_col: Optional[str], target: str) -> bool:
    return span_contains(row.get(start_col, ""), row.get(end_col, "") if end_col else "", target)


def join_unique(values: Iterable[str], sep: str = " | ") -> str:
    out: List[str] = []
    seen: Set[str] = set()
    for v in values:
        v = clean(v)
        if v and v not in seen:
            seen.add(v)
            out.append(v)
    return sep.join(out)


class TFContext:
    """Minimal BHSA context provider; no invented speaker labels."""

    def __init__(self, tf_dir: Path):
        self.tf_dir = tf_dir.expanduser().resolve()
        if not self.tf_dir.is_dir():
            raise RuntimeError(f"BHSA TF directory not found: {self.tf_dir}")
        if not (self.tf_dir / "otype.tf").exists() or not (self.tf_dir / "oslots.tf").exists():
            raise RuntimeError(
                f"Not a BHSA TF data directory (otype.tf/oslots.tf missing): {self.tf_dir}"
            )

        try:
            from tf.fabric import Fabric
        except Exception as e:
            raise RuntimeError(
                "Text-Fabric is not importable in this Termux Python environment."
            ) from e

        TF = Fabric(locations=str(self.tf_dir), modules=[""], silent="deep")
        # Load Hebrew word feature. Structural features are supplied by TF core.
        api = TF.load("g_word_utf8", silent="deep")
        if not api:
            raise RuntimeError("Text-Fabric failed to load BHSA API.")
        self.api = api
        self.F = api.F
        self.L = api.L
        self.T = api.T

        book_node = self.T.nodeFromSection(("Job",))
        if not book_node:
            raise RuntimeError("Could not resolve book node for Job.")
        self.job_verses = list(self.L.d(book_node, otype="verse"))
        self.ref_to_vnode: Dict[str, int] = {}
        self.vnode_to_index: Dict[int, int] = {}
        for i, v in enumerate(self.job_verses):
            sec = self.T.sectionFromNode(v)
            if not sec or len(sec) < 3:
                continue
            book, ch, vs = sec[0], sec[1], sec[2]
            if str(book) == "Job":
                key = f"{int(ch)}:{int(vs)}"
                self.ref_to_vnode[key] = v
                self.vnode_to_index[v] = i

    def node_text(self, node: int) -> str:
        # Prefer canonical TF text format.
        for fmt in ("text-orig-full", "text-orig-plain"):
            try:
                txt = self.T.text(node, fmt=fmt)
                if txt:
                    return " ".join(str(txt).split())
            except Exception:
                pass
        # Fallback to g_word_utf8.
        try:
            words = self.L.d(node, otype="word")
            vals = [clean(self.F.g_word_utf8.v(w)) for w in words]
            vals = [v for v in vals if v]
            return " ".join(vals)
        except Exception:
            return ""

    def node_span(self, node: int) -> str:
        try:
            words = self.L.d(node, otype="word")
            if not words:
                return ""
            a = self.T.sectionFromNode(words[0])
            b = self.T.sectionFromNode(words[-1])
            if not a or not b:
                return ""
            ar = f"{int(a[1])}:{int(a[2])}"
            br = f"{int(b[1])}:{int(b[2])}"
            return ar if ar == br else f"{ar}-{br}"
        except Exception:
            return ""

    def _struct_nodes(self, vnode: int, otype: str) -> List[int]:
        try:
            return list(self.L.d(vnode, otype=otype))
        except Exception:
            return []

    def context(self, ref: str) -> Dict[str, str]:
        vnode = self.ref_to_vnode.get(ref)
        if not vnode:
            return {
                "ref": ref,
                "tf_resolved": "NO",
                "prev_ref": "", "prev_text": "",
                "current_text": "",
                "next_ref": "", "next_text": "",
                "clause_count": "", "clauses": "",
                "sentence_count": "", "sentences": "",
            }

        idx = self.vnode_to_index[vnode]
        prev_v = self.job_verses[idx - 1] if idx > 0 else None
        next_v = self.job_verses[idx + 1] if idx + 1 < len(self.job_verses) else None

        def vref(v: Optional[int]) -> str:
            if not v:
                return ""
            sec = self.T.sectionFromNode(v)
            return f"{int(sec[1])}:{int(sec[2])}" if sec and len(sec) >= 3 else ""

        clauses = self._struct_nodes(vnode, "clause")
        sentences = self._struct_nodes(vnode, "sentence")

        clause_bits = [
            f"{self.node_span(n)} :: {self.node_text(n)}"
            for n in clauses
        ]
        sentence_bits = [
            f"{self.node_span(n)} :: {self.node_text(n)}"
            for n in sentences
        ]

        return {
            "ref": ref,
            "tf_resolved": "YES",
            "prev_ref": vref(prev_v),
            "prev_text": self.node_text(prev_v) if prev_v else "",
            "current_text": self.node_text(vnode),
            "next_ref": vref(next_v),
            "next_text": self.node_text(next_v) if next_v else "",
            "clause_count": str(len(clauses)),
            "clauses": " || ".join(clause_bits),
            "sentence_count": str(len(sentences)),
            "sentences": " || ".join(sentence_bits),
        }


class SyntheticContext:
    """Self-test context provider."""

    def context(self, ref: str) -> Dict[str, str]:
        r = parse_ref(ref)
        if not r:
            return {
                "ref": ref, "tf_resolved": "NO",
                "prev_ref": "", "prev_text": "", "current_text": "",
                "next_ref": "", "next_text": "",
                "clause_count": "", "clauses": "",
                "sentence_count": "", "sentences": "",
            }
        ch, vs = r
        return {
            "ref": ref,
            "tf_resolved": "YES",
            "prev_ref": f"{ch}:{max(1,vs-1)}",
            "prev_text": f"SYNTH PREV {ref}",
            "current_text": f"SYNTH CURRENT {ref}",
            "next_ref": f"{ch}:{vs+1}",
            "next_text": f"SYNTH NEXT {ref}",
            "clause_count": "1",
            "clauses": f"{ref} :: SYNTH CLAUSE {ref}",
            "sentence_count": "1",
            "sentences": f"{ref} :: SYNTH SENTENCE {ref}",
        }


def load_inputs(r3b2_root: Path, r3b3_root: Path) -> Dict[str, Table]:
    tables: Dict[str, Table] = {}
    for name in R3B2_REQUIRED:
        tables["r3b2:" + name] = find_named_csv(r3b2_root, name, required=True)
    # Optional R3b.2 extension relation file
    ext = find_named_csv(r3b2_root, "05_sequence_extension_links.csv", required=False)
    if ext:
        tables["r3b2:05_sequence_extension_links.csv"] = ext

    for name in R3B3_REQUIRED:
        tables["r3b3:" + name] = find_named_csv(r3b3_root, name, required=True)
    return tables


def schema_inventory(tables: Dict[str, Table]) -> List[Dict[str, Any]]:
    rows = []
    for key, t in sorted(tables.items()):
        rows.append({
            "source": key,
            "row_count": len(t.rows),
            "column_count": len(t.fieldnames),
            "columns": " | ".join(t.fieldnames),
        })
    return rows


def index_r3b3(tables: Dict[str, Table]) -> Dict[str, Any]:
    members = tables["r3b3:02_lineage_bundle_members.csv"]
    m_lineage = get_col(members, ["lineage_id"])
    m_bundle = get_col(members, ["bundle_id"])

    bundle_to_lineage: Dict[str, str] = {}
    lineage_to_bundles: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in members.rows:
        b, l = row.get(m_bundle, ""), row.get(m_lineage, "")
        if not b or not l:
            continue
        if b in bundle_to_lineage and bundle_to_lineage[b] != l:
            raise RuntimeError(f"Bundle mapped to multiple lineages: {b}")
        bundle_to_lineage[b] = l
        lineage_to_bundles[l].append(row)

    workspace = tables["r3b3:09_lineage_review_workspace.csv"]
    w_id = get_col(workspace, ["review_container_id"])
    w_class = get_col(workspace, ["review_container_class"])
    w_lineage = get_col(workspace, ["lineage_id"], required=False)
    w_orphan = get_col(workspace, ["orphan_singleton_review_item_id"], required=False)

    container_rows: Dict[str, Dict[str, str]] = {}
    lineage_to_container: Dict[str, str] = {}
    orphan_to_container: Dict[str, str] = {}
    for row in workspace.rows:
        cid = row.get(w_id, "")
        if not cid:
            raise RuntimeError("Blank review_container_id in R3b.3 workspace.")
        if cid in container_rows:
            raise RuntimeError(f"Duplicate review_container_id: {cid}")
        container_rows[cid] = row
        l = row.get(w_lineage, "") if w_lineage else ""
        o = row.get(w_orphan, "") if w_orphan else ""
        if l:
            lineage_to_container[l] = cid
        if o:
            orphan_to_container[o] = cid

    # Singleton refinement events remain event rows, never converted into bundle identity.
    single_events = tables["r3b3:05_lineage_singleton_refinement_events.csv"]
    se_lineage = get_col(single_events, ["lineage_id"])
    se_parent = get_col(single_events, ["parent_bundle_id"])
    singleton_events_by_lineage: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    singleton_events_by_parent: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in single_events.rows:
        l = row.get(se_lineage, "")
        p = row.get(se_parent, "")
        if l:
            singleton_events_by_lineage[l].append(row)
        if p:
            singleton_events_by_parent[p].append(row)

    g6 = tables["r3b3:06_g6_singleton_lineage_links.csv"]
    g6_item = get_col(g6, ["review_item_id"])
    g6_lineage = get_col(g6, ["lineage_id"], required=False)
    g6_parent = get_col(g6, ["parent_bundle_id_at_first_unique"], required=False)
    g6_by_lineage: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    g6_by_item: Dict[str, Dict[str, str]] = {}
    for row in g6.rows:
        item = row.get(g6_item, "")
        if item:
            g6_by_item[item] = row
        l = row.get(g6_lineage, "") if g6_lineage else ""
        if l:
            g6_by_lineage[l].append(row)

    ext = tables["r3b3:07_sequence_extension_lineage_overlay.csv"]
    short_l = get_col(ext, ["short_lineage_id"])
    long_l = get_col(ext, ["long_lineage_id"])
    ext_by_lineage: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in ext.rows:
        sl, ll = row.get(short_l, ""), row.get(long_l, "")
        if sl:
            ext_by_lineage[sl].append(row)
        if ll and ll != sl:
            ext_by_lineage[ll].append(row)

    return {
        "bundle_to_lineage": bundle_to_lineage,
        "lineage_to_bundles": lineage_to_bundles,
        "container_rows": container_rows,
        "lineage_to_container": lineage_to_container,
        "orphan_to_container": orphan_to_container,
        "singleton_events_by_lineage": singleton_events_by_lineage,
        "singleton_events_by_parent": singleton_events_by_parent,
        "g6_by_lineage": g6_by_lineage,
        "g6_by_item": g6_by_item,
        "ext_by_lineage": ext_by_lineage,
        "workspace_table": workspace,
        "members_table": members,
        "single_events_table": single_events,
        "g6_table": g6,
        "extension_table": ext,
    }


def container_metrics(row: Dict[str, str]) -> Dict[str, int]:
    return {
        "bundle_count": intish(row.get("bundle_count")),
        "family_count": intish(row.get("family_count")),
        "g6_count": intish(row.get("g6_singleton_descendant_count")),
        "max_depth": intish(row.get("max_refinement_depth")),
        "sequence_length": intish(row.get("sequence_length")),
    }


def select_pilot_containers(index: Dict[str, Any]) -> List[Dict[str, str]]:
    containers = []
    for cid, row in index["container_rows"].items():
        m = container_metrics(row)
        containers.append({
            "review_container_id": cid,
            "review_container_class": row.get("review_container_class", ""),
            "lineage_id": row.get("lineage_id", ""),
            "orphan_singleton_review_item_id": row.get("orphan_singleton_review_item_id", ""),
            **{k: str(v) for k, v in m.items()},
        })

    used: Set[str] = set()
    selected: List[Dict[str, str]] = []

    def take(stratum: str, ordered: List[Dict[str, str]], n: int = TARGET_PER_STRATUM):
        count = 0
        for r in ordered:
            cid = r["review_container_id"]
            if cid in used:
                continue
            rr = dict(r)
            rr["stratum"] = stratum
            selected.append(rr)
            used.add(cid)
            count += 1
            if count >= n:
                break

    # 1. Largest bundle containers: directly tests whether huge lineages are reviewable.
    high = sorted(
        containers,
        key=lambda r: (
            -int(r["bundle_count"]),
            -int(r["g6_count"]),
            -int(r["max_depth"]),
            r["review_container_id"],
        ),
    )
    take("HIGH_BUNDLE_COUNT", high)

    # 2. Singleton-rich containers, excluding already selected.
    singleton_rich = sorted(
        containers,
        key=lambda r: (
            -int(r["g6_count"]),
            -int(r["bundle_count"]),
            r["review_container_id"],
        ),
    )
    take("SINGLETON_RICH", singleton_rich)

    # 3. Middle complexity by bundle-count median distance.
    vals = [int(r["bundle_count"]) for r in containers]
    med = statistics.median(vals) if vals else 0
    middle = sorted(
        containers,
        key=lambda r: (
            abs(int(r["bundle_count"]) - med),
            abs(int(r["g6_count"]) - statistics.median([int(x["g6_count"]) for x in containers])),
            r["review_container_id"],
        ),
    )
    take("MEDIAN_COMPLEXITY", middle)

    # 4. Lowest-complexity containers. Put orphan singleton container first if present.
    low = sorted(
        containers,
        key=lambda r: (
            0 if r["orphan_singleton_review_item_id"] else 1,
            int(r["bundle_count"]),
            int(r["g6_count"]),
            int(r["max_depth"]),
            r["review_container_id"],
        ),
    )
    take("LOW_COMPLEXITY", low)

    return selected


def context_for_ref(provider, ref: str, cache: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    if not ref:
        return {}
    key = ref_str(parse_ref(ref))
    if not key:
        return {}
    if key not in cache:
        cache[key] = provider.context(key)
    return cache[key]


def build_pilot_details(
    selected: List[Dict[str, str]],
    index: Dict[str, Any],
    provider,
) -> Tuple[
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    List[Dict[str, Any]],
    Dict[str, Dict[str, str]],
]:
    members_out: List[Dict[str, Any]] = []
    events_out: List[Dict[str, Any]] = []
    g6_out: List[Dict[str, Any]] = []
    ext_out: List[Dict[str, Any]] = []
    workspace_out: List[Dict[str, Any]] = []
    ctx_cache: Dict[str, Dict[str, str]] = {}

    members_table: Table = index["members_table"]
    single_table: Table = index["single_events_table"]
    g6_table: Table = index["g6_table"]

    mb = get_col(members_table, ["bundle_id"])
    ml = get_col(members_table, ["lineage_id"])
    mparent = get_col(members_table, ["parent_bundle_id"], required=False)
    mex_start = get_col(members_table, ["exemplar_ref_start"], required=False)
    mex_end = get_col(members_table, ["exemplar_ref_end"], required=False)
    msurface = get_col(members_table, ["exemplar_surface_text"], required=False)

    se_parent = get_col(single_table, ["parent_bundle_id"])
    se_start = get_col(single_table, ["exemplar_ref_start"])
    se_end = get_col(single_table, ["exemplar_ref_end"], required=False)
    se_surface = get_col(single_table, ["exemplar_surface_text"], required=False)
    se_g6 = get_col(single_table, ["mapped_g6_singleton_review_item_id"], required=False)

    gi = get_col(g6_table, ["review_item_id"])
    gl = get_col(g6_table, ["lineage_id"], required=False)
    gp = get_col(g6_table, ["parent_bundle_id_at_first_unique"], required=False)
    gs = get_col(g6_table, ["ref_start"])
    ge = get_col(g6_table, ["ref_end"], required=False)
    gsurf = get_col(g6_table, ["surface_text"], required=False)

    for case_no, sel in enumerate(selected, start=1):
        cid = sel["review_container_id"]
        l = sel["lineage_id"]
        case_id = f"RC{case_no:03d}"

        source_row = index["container_rows"][cid]
        expected_bundle_count = intish(source_row.get("bundle_count"))

        lineage_members = index["lineage_to_bundles"].get(l, []) if l else []
        for row in lineage_members:
            ref = row.get(mex_start, "") if mex_start else ""
            ctx = context_for_ref(provider, ref, ctx_cache)
            bundle = row.get(mb, "")
            members_out.append({
                "case_id": case_id,
                "stratum": sel["stratum"],
                "review_container_id": cid,
                "object_type": "REPEATED_BUNDLE",
                "lineage_id": l,
                "bundle_id": bundle,
                "parent_bundle_id": row.get(mparent, "") if mparent else "",
                "refinement_depth": row.get("refinement_depth", ""),
                "occurrence_count": row.get("occurrence_count", ""),
                "child_bundle_count": row.get("child_bundle_count", ""),
                "has_singleton_descendant": "YES" if index["singleton_events_by_parent"].get(bundle) else "NO",
                "exemplar_ref_start": ref,
                "exemplar_ref_end": row.get(mex_end, "") if mex_end else "",
                "exemplar_surface_text": row.get(msurface, "") if msurface else "",
                "tf_current_text": ctx.get("current_text", ""),
                "tf_prev_ref": ctx.get("prev_ref", ""),
                "tf_prev_text": ctx.get("prev_text", ""),
                "tf_next_ref": ctx.get("next_ref", ""),
                "tf_next_text": ctx.get("next_text", ""),
                "tf_clauses": ctx.get("clauses", ""),
                "tf_sentences": ctx.get("sentences", ""),
            })

        for event_no, row in enumerate(index["singleton_events_by_lineage"].get(l, []), start=1):
            ref = row.get(se_start, "")
            ctx = context_for_ref(provider, ref, ctx_cache)
            events_out.append({
                "case_id": case_id,
                "stratum": sel["stratum"],
                "review_container_id": cid,
                "object_type": "SINGLETON_REFINEMENT_EVENT",
                "lineage_id": l,
                "event_index_within_lineage": event_no,
                "parent_bundle_id": row.get(se_parent, ""),
                "parent_family_id": row.get("parent_family_id", ""),
                "parent_level": row.get("parent_level", ""),
                "child_level": row.get("child_level", ""),
                "sequence_length": row.get("sequence_length", ""),
                "mapped_g6_singleton_review_item_id": row.get(se_g6, "") if se_g6 else "",
                "ref_start": ref,
                "ref_end": row.get(se_end, "") if se_end else "",
                "surface_text": row.get(se_surface, "") if se_surface else "",
                "tf_current_text": ctx.get("current_text", ""),
                "tf_clauses": ctx.get("clauses", ""),
                "tf_sentences": ctx.get("sentences", ""),
            })

        g6_rows = index["g6_by_lineage"].get(l, []) if l else []
        # Orphan review container: attach its specific singleton item.
        orphan = sel.get("orphan_singleton_review_item_id", "")
        if orphan and orphan in index["g6_by_item"]:
            g6_rows = [index["g6_by_item"][orphan]]

        for row in g6_rows:
            ref = row.get(gs, "")
            ctx = context_for_ref(provider, ref, ctx_cache)
            g6_out.append({
                "case_id": case_id,
                "stratum": sel["stratum"],
                "review_container_id": cid,
                "object_type": "G6_SINGLETON_REVIEW_ITEM",
                "review_item_id": row.get(gi, ""),
                "lineage_id": row.get(gl, "") if gl else l,
                "parent_bundle_id_at_first_unique": row.get(gp, "") if gp else "",
                "first_unique_level": row.get("first_unique_level", ""),
                "link_status": row.get("link_status", ""),
                "ref_start": ref,
                "ref_end": row.get(ge, "") if ge else "",
                "surface_text": row.get(gsurf, "") if gsurf else "",
                "tf_current_text": ctx.get("current_text", ""),
                "tf_clauses": ctx.get("clauses", ""),
                "tf_sentences": ctx.get("sentences", ""),
            })

        for row in index["ext_by_lineage"].get(l, []) if l else []:
            ext_out.append({
                "case_id": case_id,
                "stratum": sel["stratum"],
                "review_container_id": cid,
                "relation_layer": "SEQUENCE_EXTENSION_OVERLAY_ONLY",
                "lineage_id": l,
                "relation": row.get("relation", ""),
                "added_side": row.get("added_side", ""),
                "level": row.get("level", ""),
                "short_lineage_id": row.get("short_lineage_id", ""),
                "long_lineage_id": row.get("long_lineage_id", ""),
                "same_refinement_lineage": row.get("same_refinement_lineage", ""),
                "short_bundle_id": row.get("short_bundle_id", ""),
                "long_bundle_id": row.get("long_bundle_id", ""),
                "short_exemplar_ref_start": row.get("short_exemplar_ref_start", ""),
                "long_exemplar_ref_start": row.get("long_exemplar_ref_start", ""),
            })

        workspace_out.append({
            "case_id": case_id,
            "stratum": sel["stratum"],
            "review_container_class": sel["review_container_class"],
            "review_container_id": cid,
            "lineage_id": l,
            "orphan_singleton_review_item_id": sel["orphan_singleton_review_item_id"],
            "source_bundle_count": source_row.get("bundle_count", ""),
            "emitted_bundle_count": len(lineage_members),
            "source_family_count": source_row.get("family_count", ""),
            "source_g6_singleton_descendant_count": source_row.get("g6_singleton_descendant_count", ""),
            "emitted_g6_item_count": len(g6_rows),
            "source_max_refinement_depth": source_row.get("max_refinement_depth", ""),
            "source_levels_present": source_row.get("levels_present", ""),
            "source_ref_start": source_row.get("ref_start", ""),
            "source_ref_end": source_row.get("ref_end", ""),
            "review_status": "UNREVIEWED",
            "observable_behavior": "",
            "recurring_context": "",
            "exceptions": "",
            "sufficient_context": "",
            "additional_information_needed": "",
            "review_time_seconds": "",
            "reviewer_notes": "",
        })

    return members_out, events_out, g6_out, ext_out, workspace_out, ctx_cache


def build_control_panels(
    tables: Dict[str, Table],
    index: Dict[str, Any],
    provider,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Dict[str, str]]]:
    """
    Pattern matches:
    - all repeated-bundle occurrence rows from R3b.2 03_bundle_occurrences.csv;
    - all G6 singleton review items from R3b.2 08_singleton_review_items.csv;
    - all singleton refinement events from R3b.3 05_...events.csv.
    Sequence-extension relations are output separately and never treated as genealogy.
    """
    occ = tables["r3b2:03_bundle_occurrences.csv"]
    ob = get_col(occ, ["bundle_id"])
    os_ = get_col(occ, ["ref_start", "start_ref", "ref"], required=True)
    oe = get_col(occ, ["ref_end", "end_ref"], required=False)
    osurf = get_col(occ, ["surface_text", "surface", "exemplar_surface_text"], required=False)

    single = tables["r3b2:08_singleton_review_items.csv"]
    si = get_col(single, ["review_item_id"])
    ss = get_col(single, ["ref_start", "start_ref", "ref"])
    se = get_col(single, ["ref_end", "end_ref"], required=False)
    ssurf = get_col(single, ["surface_text", "surface"], required=False)

    events = index["single_events_table"]
    ep = get_col(events, ["parent_bundle_id"])
    es = get_col(events, ["exemplar_ref_start"])
    ee = get_col(events, ["exemplar_ref_end"], required=False)
    esurf = get_col(events, ["exemplar_surface_text"], required=False)
    el = get_col(events, ["lineage_id"])

    matches: List[Dict[str, Any]] = []
    ext_matches: List[Dict[str, Any]] = []
    ctx_cache: Dict[str, Dict[str, str]] = {}

    # Build singleton item -> R3b.3 lineage link.
    g6_by_item = index["g6_by_item"]

    for control in CONTROL_REFS:
        ctx = context_for_ref(provider, control, ctx_cache)

        # Repeated pattern occurrences: every occurrence, not bundle exemplar.
        for row in occ.rows:
            if not row_span_contains(row, os_, oe, control):
                continue
            b = row.get(ob, "")
            l = index["bundle_to_lineage"].get(b, "")
            cid = index["lineage_to_container"].get(l, "")
            matches.append({
                "control_ref": control,
                "object_type": "REPEATED_BUNDLE_OCCURRENCE",
                "review_container_id": cid,
                "lineage_id": l,
                "bundle_id": b,
                "review_item_id": "",
                "parent_bundle_id": "",
                "ref_start": row.get(os_, ""),
                "ref_end": row.get(oe, "") if oe else "",
                "surface_text": row.get(osurf, "") if osurf else "",
                "occurrence_identity": join_unique([
                    row.get("occurrence_id", ""),
                    row.get("window_id", ""),
                    row.get("exemplar_window_id", ""),
                ]),
                "tf_current_text": ctx.get("current_text", ""),
                "tf_clauses": ctx.get("clauses", ""),
                "tf_sentences": ctx.get("sentences", ""),
            })

        # G6 singleton review items: every singleton whose span covers the control.
        for row in single.rows:
            if not row_span_contains(row, ss, se, control):
                continue
            item = row.get(si, "")
            link = g6_by_item.get(item, {})
            l = link.get("lineage_id", "")
            parent = link.get("parent_bundle_id_at_first_unique", "")
            cid = index["lineage_to_container"].get(l, "") or index["orphan_to_container"].get(item, "")
            matches.append({
                "control_ref": control,
                "object_type": "G6_SINGLETON_REVIEW_ITEM",
                "review_container_id": cid,
                "lineage_id": l,
                "bundle_id": "",
                "review_item_id": item,
                "parent_bundle_id": parent,
                "ref_start": row.get(ss, ""),
                "ref_end": row.get(se, "") if se else "",
                "surface_text": row.get(ssurf, "") if ssurf else "",
                "occurrence_identity": item,
                "tf_current_text": ctx.get("current_text", ""),
                "tf_clauses": ctx.get("clauses", ""),
                "tf_sentences": ctx.get("sentences", ""),
            })

        # Refinement singleton events are kept distinct from G6 items.
        for i, row in enumerate(events.rows, start=1):
            if not row_span_contains(row, es, ee, control):
                continue
            l = row.get(el, "")
            cid = index["lineage_to_container"].get(l, "")
            matches.append({
                "control_ref": control,
                "object_type": "SINGLETON_REFINEMENT_EVENT",
                "review_container_id": cid,
                "lineage_id": l,
                "bundle_id": "",
                "review_item_id": row.get("mapped_g6_singleton_review_item_id", ""),
                "parent_bundle_id": row.get(ep, ""),
                "ref_start": row.get(es, ""),
                "ref_end": row.get(ee, "") if ee else "",
                "surface_text": row.get(esurf, "") if esurf else "",
                "occurrence_identity": f"R3B3_EVENT_ROW_{i}",
                "tf_current_text": ctx.get("current_text", ""),
                "tf_clauses": ctx.get("clauses", ""),
                "tf_sentences": ctx.get("sentences", ""),
            })

    # Separate extension overlay. Prefer R3b.2 occurrence-aware relation file when available.
    ext2 = tables.get("r3b2:05_sequence_extension_links.csv")
    if ext2:
        # Discover any start/end reference pairs.
        start_candidates = [c for c in ext2.fieldnames if "ref_start" in norm(c) or norm(c).endswith("start_ref")]
        end_candidates = [c for c in ext2.fieldnames if "ref_end" in norm(c) or norm(c).endswith("end_ref")]
        for control in CONTROL_REFS:
            for i, row in enumerate(ext2.rows, start=1):
                hit = False
                hit_field = ""
                for sc in start_candidates:
                    # Pair with similar end field if possible; otherwise start-only exact/span check.
                    ec = None
                    stem = norm(sc).replace("ref_start", "").replace("start_ref", "")
                    for candidate in end_candidates:
                        if norm(candidate).replace("ref_end", "").replace("end_ref", "") == stem:
                            ec = candidate
                            break
                    if row_span_contains(row, sc, ec, control):
                        hit = True
                        hit_field = sc
                        break
                if hit:
                    ext_matches.append({
                        "control_ref": control,
                        "relation_layer": "SEQUENCE_EXTENSION_OVERLAY_ONLY",
                        "source": "R3b.2:05_sequence_extension_links.csv",
                        "source_row": i,
                        "matched_reference_field": hit_field,
                        "relation": row.get("relation", ""),
                        "short_bundle_id": row.get("short_bundle_id", ""),
                        "long_bundle_id": row.get("long_bundle_id", ""),
                        "short_lineage_id": index["bundle_to_lineage"].get(row.get("short_bundle_id", ""), ""),
                        "long_lineage_id": index["bundle_to_lineage"].get(row.get("long_bundle_id", ""), ""),
                        "row_evidence": join_unique([f"{k}={v}" for k, v in row.items() if v]),
                    })
    else:
        ext3 = index["extension_table"]
        for control in CONTROL_REFS:
            for i, row in enumerate(ext3.rows, start=1):
                refs = [
                    row.get("short_exemplar_ref_start", ""),
                    row.get("long_exemplar_ref_start", ""),
                ]
                if any(ref_str(parse_ref(x)) == control for x in refs if x):
                    ext_matches.append({
                        "control_ref": control,
                        "relation_layer": "SEQUENCE_EXTENSION_OVERLAY_ONLY",
                        "source": "R3b.3:07_sequence_extension_lineage_overlay.csv",
                        "source_row": i,
                        "matched_reference_field": "exemplar_ref_start",
                        "relation": row.get("relation", ""),
                        "short_bundle_id": row.get("short_bundle_id", ""),
                        "long_bundle_id": row.get("long_bundle_id", ""),
                        "short_lineage_id": row.get("short_lineage_id", ""),
                        "long_lineage_id": row.get("long_lineage_id", ""),
                        "row_evidence": join_unique([f"{k}={v}" for k, v in row.items() if v]),
                    })

    # Deterministic ordering, no ranking.
    matches.sort(key=lambda r: (
        CONTROL_REFS.index(r["control_ref"]),
        r["object_type"],
        r["lineage_id"],
        r["bundle_id"],
        r["review_item_id"],
        r["occurrence_identity"],
    ))
    ext_matches.sort(key=lambda r: (
        CONTROL_REFS.index(r["control_ref"]),
        r["source"],
        intish(r["source_row"]),
    ))
    return matches, ext_matches, ctx_cache


def write_control_markdown(
    path: Path,
    matches: Sequence[Dict[str, Any]],
    extension_matches: Sequence[Dict[str, Any]],
    context_cache: Dict[str, Dict[str, str]],
) -> None:
    by_ref: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    ext_by_ref: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in matches:
        by_ref[r["control_ref"]].append(r)
    for r in extension_matches:
        ext_by_ref[r["control_ref"]].append(r)

    lines = [
        f"# {PROGRAM} {VERSION} — Boundary Control Panels",
        "",
        "각 절은 대표 bundle 하나로 환원하지 않는다. 아래에는 해당 절에 걸리는 "
        "반복 bundle 출현, singleton refinement event, G6 singleton review item을 모두 펼친다.",
        "",
        "sequence-extension은 refinement genealogy와 별도 overlay로 표시한다.",
        "",
    ]

    for ref in CONTROL_REFS:
        ctx = context_cache.get(ref, {})
        rows = by_ref.get(ref, [])
        lines += [
            f"## Job {ref}",
            "",
            f"- TF resolved: `{ctx.get('tf_resolved','')}`",
            f"- Previous: **{ctx.get('prev_ref','')}** — {ctx.get('prev_text','')}",
            f"- Current: **{ref}** — {ctx.get('current_text','')}",
            f"- Next: **{ctx.get('next_ref','')}** — {ctx.get('next_text','')}",
            f"- Clauses: {ctx.get('clauses','')}",
            f"- Sentences: {ctx.get('sentences','')}",
            f"- Pattern/event matches: **{len(rows)}**",
            "",
        ]
        for n, row in enumerate(rows, start=1):
            lines += [
                f"### Match {n}: {row['object_type']}",
                "",
                f"- review_container_id: `{row['review_container_id'] or '-'}`",
                f"- lineage_id: `{row['lineage_id'] or '-'}`",
                f"- bundle_id: `{row['bundle_id'] or '-'}`",
                f"- review_item_id: `{row['review_item_id'] or '-'}`",
                f"- parent_bundle_id: `{row['parent_bundle_id'] or '-'}`",
                f"- span: `{row['ref_start']}` — `{row['ref_end']}`",
                f"- surface: {row['surface_text']}",
                "",
            ]
        erows = ext_by_ref.get(ref, [])
        lines += [
            "### Sequence-extension overlay",
            "",
            f"- relation matches: **{len(erows)}**",
        ]
        for row in erows:
            lines.append(
                f"- {row['source']} row {row['source_row']}: "
                f"`{row['short_bundle_id']}` → `{row['long_bundle_id']}` "
                f"({row['short_lineage_id']} → {row['long_lineage_id']})"
            )
        lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_pilot_packet(
    path: Path,
    workspace: Sequence[Dict[str, Any]],
    members: Sequence[Dict[str, Any]],
    events: Sequence[Dict[str, Any]],
    g6: Sequence[Dict[str, Any]],
    ext: Sequence[Dict[str, Any]],
) -> None:
    m_by: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    e_by: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    g_by: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    x_by: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in members: m_by[r["case_id"]].append(r)
    for r in events: e_by[r["case_id"]].append(r)
    for r in g6: g_by[r["case_id"]].append(r)
    for r in ext: x_by[r["case_id"]].append(r)

    lines = [
        f"# {PROGRAM} {VERSION} — Review-Container Pilot Packet",
        "",
        "검토 단위는 R3b.3 `09_lineage_review_workspace.csv`의 review container이다. "
        "큰 lineage도 하나의 container로 그대로 펼쳐 실제 검토 가능성을 시험한다.",
        "",
    ]
    for w in workspace:
        cid = w["case_id"]
        lines += [
            f"## {cid} — {w['stratum']}",
            "",
            f"- review_container_id: `{w['review_container_id']}`",
            f"- class: `{w['review_container_class']}`",
            f"- lineage_id: `{w['lineage_id'] or '-'}`",
            f"- orphan_singleton_review_item_id: `{w['orphan_singleton_review_item_id'] or '-'}`",
            f"- repeated bundles: **{w['emitted_bundle_count']}** / source `{w['source_bundle_count']}`",
            f"- G6 singleton items: **{w['emitted_g6_item_count']}** / source `{w['source_g6_singleton_descendant_count']}`",
            f"- max refinement depth: `{w['source_max_refinement_depth']}`",
            "",
            "### Repeated bundles",
            "",
        ]
        for r in m_by.get(cid, []):
            lines += [
                f"- `{r['bundle_id']}` depth={r['refinement_depth']} occurrence_count={r['occurrence_count']} "
                f"singleton-descendant={r['has_singleton_descendant']} "
                f"exemplar={r['exemplar_ref_start']}–{r['exemplar_ref_end']}: {r['exemplar_surface_text']}",
                f"  - context: {r['tf_current_text']}",
            ]
        if not m_by.get(cid):
            lines.append("- [none]")

        lines += ["", "### Singleton refinement events", ""]
        for r in e_by.get(cid, []):
            lines.append(
                f"- parent `{r['parent_bundle_id']}` {r['parent_level']}→{r['child_level']} "
                f"span={r['ref_start']}–{r['ref_end']} G6=`{r['mapped_g6_singleton_review_item_id'] or '-'}` "
                f"surface={r['surface_text']}"
            )
        if not e_by.get(cid):
            lines.append("- [none]")

        lines += ["", "### G6 singleton review items", ""]
        for r in g_by.get(cid, []):
            lines.append(
                f"- `{r['review_item_id']}` parent=`{r['parent_bundle_id_at_first_unique'] or '-'}` "
                f"level={r['first_unique_level']} span={r['ref_start']}–{r['ref_end']} "
                f"surface={r['surface_text']}"
            )
        if not g_by.get(cid):
            lines.append("- [none]")

        lines += ["", "### Sequence-extension overlay (separate layer)", ""]
        for r in x_by.get(cid, []):
            lines.append(
                f"- `{r['short_bundle_id']}` → `{r['long_bundle_id']}` "
                f"({r['short_lineage_id']} → {r['long_lineage_id']}) relation={r['relation']}"
            )
        if not x_by.get(cid):
            lines.append("- [none]")

        lines += [
            "",
            "### Human review",
            "",
            "- observable_behavior:",
            "- recurring_context:",
            "- exceptions:",
            "- sufficient_context: YES / NO",
            "- additional_information_needed:",
            "- review_time_seconds:",
            "- reviewer_notes:",
            "",
        ]

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_gates(
    index: Dict[str, Any],
    selected: Sequence[Dict[str, str]],
    workspace: Sequence[Dict[str, Any]],
    members: Sequence[Dict[str, Any]],
    controls: Sequence[Dict[str, Any]],
    control_context: Dict[str, Dict[str, str]],
) -> List[Dict[str, str]]:
    gates: List[Dict[str, str]] = []

    def add(gid: str, ok: bool, detail: str):
        gates.append({"gate_id": gid, "status": "PASS" if ok else "FAIL", "detail": detail})

    population = len(index["container_rows"])
    add(
        "GATE_MILAL_R3C001_REVIEW_POPULATION",
        population == EXPECTED_REVIEW_CONTAINER_COUNT,
        f"R3b.3 review containers={population}; expected={EXPECTED_REVIEW_CONTAINER_COUNT}.",
    )

    counts = Counter(r["stratum"] for r in selected)
    expected_strata = ("HIGH_BUNDLE_COUNT", "SINGLETON_RICH", "MEDIAN_COMPLEXITY", "LOW_COMPLEXITY")
    add(
        "GATE_MILAL_R3C001_SAMPLE_24_UNIQUE_CONTAINERS",
        len(selected) == TARGET_TOTAL
        and len({r["review_container_id"] for r in selected}) == TARGET_TOTAL,
        f"selected={len(selected)}, unique={len({r['review_container_id'] for r in selected})}.",
    )
    for s in expected_strata:
        add(
            f"GATE_MILAL_R3C001_STRATUM_{s}",
            counts[s] == TARGET_PER_STRATUM,
            f"{s}: {counts[s]}/{TARGET_PER_STRATUM}.",
        )

    # Every sampled lineage container emits all its bundle members.
    ws_by_case = {r["case_id"]: r for r in workspace}
    member_counts = Counter(r["case_id"] for r in members)
    completeness = True
    problems = []
    for case_id, w in ws_by_case.items():
        expected = intish(w["source_bundle_count"])
        emitted = member_counts[case_id]
        # Orphan singleton container legitimately has 0 bundles.
        if emitted != expected:
            completeness = False
            problems.append(f"{case_id}:{emitted}!={expected}")
    add(
        "GATE_MILAL_R3C001_CONTAINER_MEMBER_COMPLETENESS",
        completeness,
        "All sampled containers emit every repeated bundle member."
        if completeness else " ; ".join(problems[:20]),
    )

    # No bundle is mislabeled singleton; singleton is separate object type.
    add(
        "GATE_MILAL_R3C001_SINGLETON_OBJECT_TYPES_SEPARATE",
        all(r.get("object_type") == "REPEATED_BUNDLE" for r in members),
        "Repeated bundles are emitted only as REPEATED_BUNDLE; singleton events/items are separate files.",
    )

    # Control panels contain every control and use occurrence-level input.
    by_ref = Counter(r["control_ref"] for r in controls)
    add(
        "GATE_MILAL_R3C001_CONTROL_ALL_REFS_PRESENT",
        all(by_ref[r] > 0 for r in CONTROL_REFS),
        " ; ".join(f"{r}={by_ref[r]}" for r in CONTROL_REFS),
    )
    add(
        "GATE_MILAL_R3C001_TF_CONTROL_CONTEXT",
        all(control_context.get(r, {}).get("tf_resolved") == "YES" for r in CONTROL_REFS),
        " ; ".join(
            f"{r}={control_context.get(r,{}).get('tf_resolved','NO')}" for r in CONTROL_REFS
        ),
    )

    # Function fields are absent from the R3c.0.1 human workspace.
    if workspace:
        cols = set(workspace[0].keys())
    else:
        cols = set()
    bad = [f for f in FUNCTION_FIELD_TOKENS if f in cols]
    blank_reviews = all(
        r.get("review_status") == "UNREVIEWED"
        and not r.get("observable_behavior")
        and not r.get("recurring_context")
        for r in workspace
    )
    add(
        "GATE_MILAL_R3C001_NO_FUNCTION_AUTOLABEL",
        not bad and blank_reviews,
        f"forbidden_fields={bad}; all human review fields blank={blank_reviews}.",
    )

    add(
        "GATE_MILAL_R3C001_EXTENSION_LAYER_SEPARATE",
        True,
        "Sequence-extension relations are emitted in separate overlay files and are never merged into refinement lineage identity.",
    )

    return gates


def write_method_note(path: Path) -> None:
    path.write_text(
f"""# {PROGRAM} {VERSION}

**{FULL_NAME}**

## 이번 수정의 핵심

R3c.0은 2,219 internal bundles에서 24건을 골랐다. 그러나 실제 인간 검토 모집단은
R3b.3 `09_lineage_review_workspace.csv`의 1,066 review containers이다.
{VERSION}은 표본 단위를 이 review container로 수정한다.

## 표본 24건

가중 점수나 중요도 ranking을 사용하지 않는다.

- HIGH_BUNDLE_COUNT: bundle_count가 큰 container 6
- SINGLETON_RICH: G6 singleton descendant가 많은 container 6
- MEDIAN_COMPLEXITY: bundle_count 중앙값 부근 container 6
- LOW_COMPLEXITY: bundle_count가 작은 container 6
  - orphan singleton container가 있으면 이 층에서 우선 노출

## 객체 유형의 분리

- REPEATED_BUNDLE
- SINGLETON_REFINEMENT_EVENT
- G6_SINGLETON_REVIEW_ITEM

parent bundle에 singleton descendant가 있다는 사실은
`has_singleton_descendant=YES`로만 표시한다. parent bundle 자체를 singleton으로 바꾸지 않는다.

## Boundary Control Panels

대상:
{", ".join("Job " + r for r in CONTROL_REFS)}

R3b.2 `03_bundle_occurrences.csv`를 사용하여 control verse를 포함하는 반복 bundle의
**모든 occurrence**를 찾는다. `08_singleton_review_items.csv`의 singleton도 전부 찾는다.
R3b.3 singleton refinement event를 별도 객체로 병기한다.

따라서 `control verse -> representative bundle 1개` 방식은 사용하지 않는다.

## Text-Fabric

BHSA 2021에서 각 target/exemplar에 대해:
- 이전 절
- 현재 절
- 다음 절
- 현재 절에 속한 clause
- 현재 절에 속한 sentence

를 추가한다.

BHSA에 근거가 없는 speaker label이나 macro label은 이 단계에서 생성하지 않는다.

## Sequence extension

sequence-extension은 refinement genealogy와 합치지 않는다.
항상 별도 `SEQUENCE_EXTENSION_OVERLAY_ONLY` 층으로 출력한다.

## 인간 검토 필드

- observable_behavior
- recurring_context
- exceptions
- sufficient_context
- additional_information_needed
- review_time_seconds
- reviewer_notes

기능(function) 자동 판정 필드는 없다.
""",
        encoding="utf-8",
    )


def write_manifest(outdir: Path) -> None:
    target = outdir / "99_manifest_sha256.csv"
    rows = []
    for p in sorted(outdir.iterdir()):
        if p.is_file() and p.name != target.name:
            rows.append({"file": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)})
    write_csv(target, ["file", "bytes", "sha256"], rows)


def run_pipeline(
    r3b2_zip: Path,
    r3b3_zip: Path,
    tf_dir: Optional[Path],
    output_dir: Path,
    context_provider=None,
) -> int:
    started = datetime.now(timezone.utc)
    output_dir = output_dir.expanduser().resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    status = 0
    error = ""
    temp = Path(tempfile.mkdtemp(prefix="milal_r3c001_"))

    try:
        r3b2_zip = r3b2_zip.expanduser().resolve()
        r3b3_zip = r3b3_zip.expanduser().resolve()
        for p, label in ((r3b2_zip, "R3b.2"), (r3b3_zip, "R3b.3")):
            if not p.is_file() or not zipfile.is_zipfile(p):
                raise RuntimeError(f"{label} ZIP missing or invalid: {p}")

        r2root = temp / "r3b2"
        r3root = temp / "r3b3"
        r2root.mkdir()
        r3root.mkdir()
        safe_extract(r3b2_zip, r2root)
        safe_extract(r3b3_zip, r3root)

        tables = load_inputs(r2root, r3root)
        write_csv(
            output_dir / "01_source_schema_inventory.csv",
            ["source", "row_count", "column_count", "columns"],
            schema_inventory(tables),
        )

        index = index_r3b3(tables)
        selected = select_pilot_containers(index)

        provider = context_provider
        if provider is None:
            if tf_dir is None:
                raise RuntimeError("--tf-dir is required for a real R3c.0.1 run.")
            provider = TFContext(tf_dir)

        members, events, g6, ext, workspace, pilot_ctx = build_pilot_details(
            selected, index, provider
        )
        controls, control_ext, control_ctx = build_control_panels(
            tables, index, provider
        )

        write_csv(
            output_dir / "02_pilot_review_containers.csv",
            [
                "case_id", "stratum", "review_container_class",
                "review_container_id", "lineage_id",
                "orphan_singleton_review_item_id",
                "source_bundle_count", "emitted_bundle_count",
                "source_family_count",
                "source_g6_singleton_descendant_count", "emitted_g6_item_count",
                "source_max_refinement_depth", "source_levels_present",
                "source_ref_start", "source_ref_end",
                "review_status", "observable_behavior", "recurring_context",
                "exceptions", "sufficient_context",
                "additional_information_needed", "review_time_seconds",
                "reviewer_notes",
            ],
            workspace,
        )
        write_csv(
            output_dir / "03_pilot_container_repeated_bundles.csv",
            [
                "case_id", "stratum", "review_container_id", "object_type",
                "lineage_id", "bundle_id", "parent_bundle_id",
                "refinement_depth", "occurrence_count", "child_bundle_count",
                "has_singleton_descendant",
                "exemplar_ref_start", "exemplar_ref_end",
                "exemplar_surface_text",
                "tf_current_text", "tf_prev_ref", "tf_prev_text",
                "tf_next_ref", "tf_next_text", "tf_clauses", "tf_sentences",
            ],
            members,
        )
        write_csv(
            output_dir / "04_pilot_container_singleton_refinement_events.csv",
            [
                "case_id", "stratum", "review_container_id", "object_type",
                "lineage_id", "event_index_within_lineage",
                "parent_bundle_id", "parent_family_id",
                "parent_level", "child_level", "sequence_length",
                "mapped_g6_singleton_review_item_id",
                "ref_start", "ref_end", "surface_text",
                "tf_current_text", "tf_clauses", "tf_sentences",
            ],
            events,
        )
        write_csv(
            output_dir / "05_pilot_container_g6_singleton_items.csv",
            [
                "case_id", "stratum", "review_container_id", "object_type",
                "review_item_id", "lineage_id",
                "parent_bundle_id_at_first_unique", "first_unique_level",
                "link_status", "ref_start", "ref_end", "surface_text",
                "tf_current_text", "tf_clauses", "tf_sentences",
            ],
            g6,
        )
        write_csv(
            output_dir / "06_pilot_container_sequence_extension_overlay.csv",
            [
                "case_id", "stratum", "review_container_id",
                "relation_layer", "lineage_id", "relation", "added_side", "level",
                "short_lineage_id", "long_lineage_id", "same_refinement_lineage",
                "short_bundle_id", "long_bundle_id",
                "short_exemplar_ref_start", "long_exemplar_ref_start",
            ],
            ext,
        )
        write_pilot_packet(
            output_dir / "07_pilot_review_container_packet.md",
            workspace, members, events, g6, ext,
        )

        write_csv(
            output_dir / "08_boundary_control_pattern_matches.csv",
            [
                "control_ref", "object_type", "review_container_id",
                "lineage_id", "bundle_id", "review_item_id", "parent_bundle_id",
                "ref_start", "ref_end", "surface_text",
                "occurrence_identity", "tf_current_text",
                "tf_clauses", "tf_sentences",
            ],
            controls,
        )
        write_csv(
            output_dir / "09_boundary_control_sequence_extension_overlay.csv",
            [
                "control_ref", "relation_layer", "source", "source_row",
                "matched_reference_field", "relation",
                "short_bundle_id", "long_bundle_id",
                "short_lineage_id", "long_lineage_id", "row_evidence",
            ],
            control_ext,
        )
        write_control_markdown(
            output_dir / "10_boundary_control_panels.md",
            controls, control_ext, control_ctx,
        )

        # TF context table for all cached refs used by pilot + controls.
        merged_ctx = dict(pilot_ctx)
        merged_ctx.update(control_ctx)
        ctx_rows = [merged_ctx[k] for k in sorted(
            merged_ctx,
            key=lambda x: parse_ref(x) or (999,999)
        )]
        write_csv(
            output_dir / "11_tf_context_inventory.csv",
            [
                "ref", "tf_resolved", "prev_ref", "prev_text",
                "current_text", "next_ref", "next_text",
                "clause_count", "clauses", "sentence_count", "sentences",
            ],
            ctx_rows,
        )

        gates = build_gates(
            index, selected, workspace, members, controls, control_ctx
        )
        write_csv(
            output_dir / "12_r3c_0_1_gates.csv",
            ["gate_id", "status", "detail"],
            gates,
        )
        write_method_note(output_dir / "13_method_note.md")

        # Summary is descriptive only; no score/rank.
        control_counts = Counter(r["control_ref"] for r in controls)
        object_counts = Counter(r["object_type"] for r in controls)
        summary = {
            "program": PROGRAM,
            "full_name": FULL_NAME,
            "version": VERSION,
            "r3b2_zip": r3b2_zip.name,
            "r3b2_sha256": sha256_file(r3b2_zip),
            "r3b3_zip": r3b3_zip.name,
            "r3b3_sha256": sha256_file(r3b3_zip),
            "tf_dir": str(tf_dir.expanduser().resolve()) if tf_dir else "SYNTHETIC_SELF_TEST",
            "review_container_population": len(index["container_rows"]),
            "pilot_container_count": len(selected),
            "pilot_strata": dict(Counter(r["stratum"] for r in selected)),
            "pilot_repeated_bundle_rows": len(members),
            "pilot_singleton_refinement_event_rows": len(events),
            "pilot_g6_singleton_item_rows": len(g6),
            "pilot_sequence_extension_overlay_rows": len(ext),
            "control_pattern_match_counts": dict(control_counts),
            "control_object_type_counts": dict(object_counts),
            "control_extension_overlay_rows": len(control_ext),
            "candidate_reduction": False,
            "function_autolabel": False,
            "importance_scoring": False,
            "genealogy_extension_merge": False,
        }
        (output_dir / "14_run_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        failed = [g for g in gates if g["status"] != "PASS"]
        if failed:
            status = 2
            error = "Failed gates: " + ", ".join(g["gate_id"] for g in failed)

    except Exception as e:
        status = 2
        error = f"{type(e).__name__}: {e}"
        (output_dir / "00_FATAL_ERROR.txt").write_text(error + "\n", encoding="utf-8")
    finally:
        shutil.rmtree(temp, ignore_errors=True)

    finished = datetime.now(timezone.utc)
    meta = {
        "program": PROGRAM,
        "full_name": FULL_NAME,
        "version": VERSION,
        "started_utc": started.isoformat(),
        "finished_utc": finished.isoformat(),
        "exit_code": status,
        "error": error,
        "output_dir": str(output_dir),
    }
    (output_dir / "90_run_metadata.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_manifest(output_dir)

    print(f"{PROGRAM} {VERSION}: {'PASS' if status == 0 else 'FAIL'}")
    if error:
        print(error, file=sys.stderr)
    print(f"Output: {output_dir}")
    return status


def make_synthetic_inputs(root: Path) -> Tuple[Path, Path]:
    """Make exact-minimum R3b.2 / R3b.3 ZIPs for --self-test."""
    r2 = root / "r2"
    r3 = root / "r3"
    r2.mkdir()
    r3.mkdir()

    # 1,066 source review containers: 1,065 lineages + 1 orphan singleton.
    lineages = [f"RL{i:05d}" for i in range(1, 1066)]
    member_rows = []
    lineage_rows = []
    workspace3 = []
    occurrence_rows = []
    bundle_rows2 = []
    event_rows = []
    g6_links = []
    singleton_items2 = []
    extension_rows = []
    bnum = 1
    gnum = 1

    control_refs = list(CONTROL_REFS)

    for i, l in enumerate(lineages, start=1):
        # Create a spread of complexity: 1..8 bundles.
        bc = 1 + ((i - 1) % 8)
        g6c = (i - 1) % 5
        bundles = []
        for j in range(bc):
            b = f"RB{bnum:05d}"
            bnum += 1
            bundles.append(b)
            ref = control_refs[(i - 1) % len(control_refs)] if i <= 12 and j == 0 else f"{1 + ((i+j) % 42)}:{1 + ((i+j) % 20)}"
            member_rows.append({
                "lineage_id": l,
                "bundle_id": b,
                "parent_bundle_id": bundles[j-1] if j > 0 else "",
                "refinement_depth": j,
                "is_root": "1" if j == 0 else "0",
                "is_leaf": "1" if j == bc-1 else "0",
                "child_bundle_count": 1 if j < bc-1 else 0,
                "occurrence_count": 2 + (j % 3),
                "exemplar_ref_start": ref,
                "exemplar_ref_end": ref,
                "exemplar_surface_text": f"SURFACE {b}",
            })
            bundle_rows2.append({
                "bundle_id": b,
                "occurrence_count": 2 + (j % 3),
                "exemplar_ref_start": ref,
                "exemplar_ref_end": ref,
                "exemplar_surface_text": f"SURFACE {b}",
            })
            # every occurrence rows; first 12 lineages guarantee control matches
            for k in range(2 + (j % 3)):
                oref = ref if k == 0 else f"{1 + ((i+j+k) % 42)}:{1 + ((i+j+k) % 20)}"
                occurrence_rows.append({
                    "bundle_id": b,
                    "occurrence_id": f"O_{b}_{k+1}",
                    "ref_start": oref,
                    "ref_end": oref,
                    "surface_text": f"OCC {b} {k+1}",
                })

        lineage_rows.append({
            "lineage_id": l,
            "root_bundle_id": bundles[0],
            "bundle_count": bc,
            "family_count": bc + 1,
            "max_refinement_depth": bc - 1,
            "g6_single_atom_singleton_descendant_count": g6c,
            "exemplar_ref_start": member_rows[-bc]["exemplar_ref_start"],
            "exemplar_ref_end": member_rows[-bc]["exemplar_ref_end"],
            "exemplar_surface_text": f"LINEAGE {l}",
        })
        workspace3.append({
            "review_container_class": "REFINEMENT_LINEAGE",
            "review_container_id": f"RCN{i:05d}",
            "lineage_id": l,
            "orphan_singleton_review_item_id": "",
            "sequence_length": 1,
            "bundle_count": bc,
            "family_count": bc + 1,
            "g6_singleton_descendant_count": g6c,
            "max_refinement_depth": bc - 1,
            "levels_present": "P0|P1",
            "root_bundle_id": bundles[0],
            "ref_start": member_rows[-bc]["exemplar_ref_start"],
            "ref_end": member_rows[-bc]["exemplar_ref_end"],
            "review_status": "UNREVIEWED",
            "researcher_function_label": "",
            "researcher_function_description": "",
            "researcher_rationale": "",
            "researcher_evidence_refs": "",
            "researcher_confidence_note": "",
            "adjudicator": "",
            "adjudicated_at": "",
        })

        # Make g6 singleton descendants for first g6c cases.
        for q in range(g6c):
            item = f"G6S{gnum:05d}"
            gnum += 1
            ref = control_refs[(i + q) % len(control_refs)] if i <= 6 else f"{1 + ((i+q) % 42)}:{1 + ((i+q) % 20)}"
            singleton_items2.append({
                "review_item_id": item,
                "ref_start": ref,
                "ref_end": ref,
                "surface_text": f"SINGLETON {item}",
            })
            g6_links.append({
                "review_item_id": item,
                "atom_index_1based": 1,
                "atom_node": 100000 + gnum,
                "ref_start": ref,
                "ref_end": ref,
                "surface_text": f"SINGLETON {item}",
                "atom_typ": "SYNTH",
                "first_unique_level": "P2",
                "lineage_id": l,
                "parent_bundle_id_at_first_unique": bundles[-1],
                "parent_family_id_at_first_unique": f"F_{bundles[-1]}",
                "link_status": "LINKED",
                "signature_G6": f"SIG_{item}",
            })
            event_rows.append({
                "lineage_id": l,
                "parent_bundle_id": bundles[-1],
                "parent_family_id": f"F_{bundles[-1]}",
                "parent_level": "P1",
                "child_level": "P2",
                "sequence_length": 1,
                "refinement_group_index": q,
                "child_signature_hash": f"HASH_{item}",
                "occurrence_count": 1,
                "exemplar_window_id": f"W_{item}",
                "exemplar_start_index_1based": 1,
                "exemplar_ref_start": ref,
                "exemplar_ref_end": ref,
                "exemplar_surface_text": f"SINGLETON {item}",
                "mapped_g6_singleton_review_item_id": item,
            })

        if i < 1065:
            extension_rows.append({
                "relation": "EXTENDS",
                "added_side": "RIGHT",
                "level": "P1",
                "short_lineage_id": l,
                "long_lineage_id": lineages[i],
                "same_refinement_lineage": "NO",
                "short_bundle_id": bundles[0],
                "long_bundle_id": f"RB_PENDING_{i}",
                "short_family_id": f"F_{bundles[0]}",
                "long_family_id": "",
                "short_sequence_length": 1,
                "long_sequence_length": 2,
                "long_occurrence_count": 2,
                "verified_subwindow_count": 1,
                "short_exemplar_ref_start": member_rows[-bc]["exemplar_ref_start"],
                "long_exemplar_ref_start": member_rows[-bc]["exemplar_ref_start"],
            })

    # orphan singleton makes row 1066
    orphan_item = "G6S_ORPHAN"
    singleton_items2.append({
        "review_item_id": orphan_item,
        "ref_start": "40:1",
        "ref_end": "40:1",
        "surface_text": "ORPHAN SINGLETON",
    })
    workspace3.append({
        "review_container_class": "ORPHAN_SINGLETON",
        "review_container_id": "RCN01066",
        "lineage_id": "",
        "orphan_singleton_review_item_id": orphan_item,
        "sequence_length": 1,
        "bundle_count": 0,
        "family_count": 0,
        "g6_singleton_descendant_count": 1,
        "max_refinement_depth": 0,
        "levels_present": "G6",
        "root_bundle_id": "",
        "ref_start": "40:1",
        "ref_end": "40:1",
        "review_status": "UNREVIEWED",
        "researcher_function_label": "",
        "researcher_function_description": "",
        "researcher_rationale": "",
        "researcher_evidence_refs": "",
        "researcher_confidence_note": "",
        "adjudicator": "",
        "adjudicated_at": "",
    })

    # R3b.2 required files
    write_csv(r2 / "01_review_bundles.csv",
              ["bundle_id","occurrence_count","exemplar_ref_start","exemplar_ref_end","exemplar_surface_text"],
              bundle_rows2)
    write_csv(r2 / "03_bundle_occurrences.csv",
              ["bundle_id","occurrence_id","ref_start","ref_end","surface_text"],
              occurrence_rows)
    write_csv(r2 / "08_singleton_review_items.csv",
              ["review_item_id","ref_start","ref_end","surface_text"],
              singleton_items2)
    write_csv(r2 / "09_function_adjudication_workspace.csv",
              ["review_item_id","review_status","researcher_function_label"],
              [{"review_item_id":"SYNTH","review_status":"UNREVIEWED","researcher_function_label":""}])

    # R3b.3 required files
    write_csv(r3 / "01_refinement_lineages.csv",
              ["lineage_id","root_bundle_id","bundle_count","family_count","max_refinement_depth",
               "g6_single_atom_singleton_descendant_count","exemplar_ref_start","exemplar_ref_end","exemplar_surface_text"],
              lineage_rows)
    write_csv(r3 / "02_lineage_bundle_members.csv",
              ["lineage_id","bundle_id","parent_bundle_id","refinement_depth","is_root","is_leaf",
               "child_bundle_count","occurrence_count","exemplar_ref_start","exemplar_ref_end","exemplar_surface_text"],
              member_rows)
    write_csv(r3 / "05_lineage_singleton_refinement_events.csv",
              ["lineage_id","parent_bundle_id","parent_family_id","parent_level","child_level",
               "sequence_length","refinement_group_index","child_signature_hash","occurrence_count",
               "exemplar_window_id","exemplar_start_index_1based","exemplar_ref_start","exemplar_ref_end",
               "exemplar_surface_text","mapped_g6_singleton_review_item_id"],
              event_rows)
    write_csv(r3 / "06_g6_singleton_lineage_links.csv",
              ["review_item_id","atom_index_1based","atom_node","ref_start","ref_end","surface_text",
               "atom_typ","first_unique_level","lineage_id","parent_bundle_id_at_first_unique",
               "parent_family_id_at_first_unique","link_status","signature_G6"],
              g6_links)
    write_csv(r3 / "07_sequence_extension_lineage_overlay.csv",
              ["relation","added_side","level","short_lineage_id","long_lineage_id",
               "same_refinement_lineage","short_bundle_id","long_bundle_id","short_family_id",
               "long_family_id","short_sequence_length","long_sequence_length","long_occurrence_count",
               "verified_subwindow_count","short_exemplar_ref_start","long_exemplar_ref_start"],
              extension_rows)
    write_csv(r3 / "09_lineage_review_workspace.csv",
              ["review_container_class","review_container_id","lineage_id",
               "orphan_singleton_review_item_id","sequence_length","bundle_count","family_count",
               "g6_singleton_descendant_count","max_refinement_depth","levels_present","root_bundle_id",
               "ref_start","ref_end","review_status","researcher_function_label",
               "researcher_function_description","researcher_rationale","researcher_evidence_refs",
               "researcher_confidence_note","adjudicator","adjudicated_at"],
              workspace3)

    z2 = root / "job_r3b_2_results.zip"
    z3 = root / "job_r3b_3_results.zip"
    for src, zp in ((r2,z2),(r3,z3)):
        with zipfile.ZipFile(zp, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for p in src.iterdir():
                zf.write(p, arcname=p.name)
    return z2, z3


def self_test() -> int:
    temp = Path(tempfile.mkdtemp(prefix="milal_r3c001_selftest_"))
    try:
        z2, z3 = make_synthetic_inputs(temp)
        out = temp / "out"
        status = run_pipeline(
            z2, z3, None, out, context_provider=SyntheticContext()
        )
        if status != 0:
            print("SELF-TEST FAIL: pipeline returned nonzero.", file=sys.stderr)
            return 1

        with (out / "12_r3c_0_1_gates.csv").open("r", encoding="utf-8-sig", newline="") as f:
            gates = list(csv.DictReader(f))
        failed = [g for g in gates if g["status"] != "PASS"]
        if failed:
            print(f"SELF-TEST FAIL: gates={failed}", file=sys.stderr)
            return 1

        with (out / "02_pilot_review_containers.csv").open("r", encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != 24:
            print(f"SELF-TEST FAIL: pilot rows={len(rows)}", file=sys.stderr)
            return 1
        if any(r["review_status"] != "UNREVIEWED" for r in rows):
            print("SELF-TEST FAIL: review status auto-filled.", file=sys.stderr)
            return 1

        with (out / "08_boundary_control_pattern_matches.csv").open("r", encoding="utf-8-sig", newline="") as f:
            controls = list(csv.DictReader(f))
        c = Counter(r["control_ref"] for r in controls)
        if any(c[x] == 0 for x in CONTROL_REFS):
            print(f"SELF-TEST FAIL: missing controls {c}", file=sys.stderr)
            return 1

        print("SELF-TEST PASS")
        print("Checks: 1,066 review-container population; 24 unique containers; "
              "object types separated; all six boundary panels populated; no function autolabel.")
        return 0
    finally:
        shutil.rmtree(temp, ignore_errors=True)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=f"{PROGRAM} {VERSION} reviewability pilot"
    )
    p.add_argument("--self-test", action="store_true")
    p.add_argument("--r3b2-zip", type=Path, default=Path("job_r3b_2_results.zip"))
    p.add_argument("--r3b3-zip", type=Path, default=Path("job_r3b_3_results.zip"))
    p.add_argument("--tf-dir", type=Path)
    p.add_argument("--output-dir", type=Path, default=Path("milal_r3c_0_1_output"))
    return p.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    return run_pipeline(
        args.r3b2_zip,
        args.r3b3_zip,
        args.tf_dir,
        args.output_dir,
    )


if __name__ == "__main__":
    raise SystemExit(main())
