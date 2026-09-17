#!/usr/bin/env python3
"""MILAL R3c.0.2: human review cases over frozen R3b.3 navigation.

Standard library except Text-Fabric on real runs. No interpretation labels,
candidate reduction, or population review-time extrapolation.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import random
import re
import sys
import tempfile
import unicodedata
import zipfile

VERSION = "R3c.0.2"
REVIEW_FIELDS = (
    "review_status", "observable_behavior", "recurring_context", "exceptions",
    "sufficient_context", "additional_information_needed", "review_time_seconds",
    "reviewer_notes",
)
CASE_TYPES = ("HIGH_COMPLEXITY_CONTAINER", "LOW_COMPLEXITY_CONTAINER",
              "RANDOM_CONTAINER", "SINGLETON_ITEM", "BOUNDARY_CONTROL")
OVERLAY = "SEQUENCE_EXTENSION_OVERLAY_ONLY"
FORBIDDEN_FIELDS = {"researcher_function_label", "researcher_function_description",
                    "function_label", "rhetorical_function", "discourse_function",
                    "theological_function"}
SOURCE_FILES = {
    "members": ("r3b3", "02_lineage_bundle_members.csv"),
    "workspace": ("r3b3", "09_lineage_review_workspace.csv"),
    "events": ("r3b3", "05_lineage_singleton_refinement_events.csv"),
    "links": ("r3b3", "06_g6_singleton_lineage_links.csv"),
    "overlay": ("r3b3", "07_sequence_extension_lineage_overlay.csv"),
    "items": ("r3b2", "08_singleton_review_items.csv"),
    "occurrences": ("r3b2", "03_bundle_occurrences.csv"),
}
SCHEMAS = {
    "members": ("bundle_id", "lineage_id", "parent_bundle_id", "refinement_depth",
                "exemplar_ref_start", "exemplar_ref_end", "exemplar_surface_text"),
    "workspace": ("review_container_id", "review_container_class", "lineage_id",
                  "orphan_singleton_review_item_id", "bundle_count", "max_refinement_depth"),
    "events": ("lineage_id", "parent_bundle_id", "parent_level", "child_level", "sequence_length",
               "exemplar_ref_start", "exemplar_ref_end", "exemplar_surface_text",
               "exemplar_start_index_1based", "mapped_g6_singleton_review_item_id"),
    "links": ("review_item_id", "lineage_id", "parent_bundle_id_at_first_unique", "link_status",
              "ref_start", "ref_end", "surface_text", "atom_node", "atom_index_1based"),
    "items": ("review_item_id", "ref_start", "ref_end", "surface_text", "atom_node", "atom_index_1based"),
    "occurrences": ("bundle_id", "window_id", "ref_start", "ref_end", "surface_text"),
    "overlay": ("relation", "short_bundle_id", "long_bundle_id", "short_lineage_id",
                "long_lineage_id", "short_exemplar_ref_start", "long_exemplar_ref_start"),
}


class SchemaError(ValueError):
    pass


class InvariantError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def review_defaults():
    return {field: "UNREVIEWED" if field == "review_status" else "" for field in REVIEW_FIELDS}


def integer(value, label):
    if not re.fullmatch(r"\d+", str(value)):
        raise SchemaError(f"{label}: expected nonnegative integer, got {value!r}")
    return int(value)


def reference(value, book):
    match = re.fullmatch(r"(?:(.+?)\s+)?(\d+):(\d+)", value.strip())
    if not match or (match[1] and match[1] != book):
        raise SchemaError(f"Invalid reference for {book}: {value!r}")
    pair = (int(match[2]), int(match[3]))
    if min(pair) < 1:
        raise SchemaError(f"Invalid reference: {value!r}")
    return pair


def ref_text(pair):
    return f"{pair[0]}:{pair[1]}"


def span(start, end, book):
    a, b = reference(start, book), reference(end, book)
    if a > b:
        raise SchemaError(f"Reversed span: {start}..{end}")
    return a, b


def contains(start, end, target, book):
    a, b = span(start, end, book)
    return a <= reference(target, book) <= b


@dataclass
class Table:
    name: str
    fields: list
    rows: list
    zip_sha256: str = "SYNTHETIC"
    archive_name: str = "SYNTHETIC"

    def records(self, role):
        """Row numbers count CSV data records from 1, excluding the header.

        Content hashes are identifiers, never an evidence-folding criterion.
        Identical rows keep separate ordinals; their source records are retained.
        """
        seen = Counter()
        for number, raw in enumerate(self.rows, 1):
            key = digest(raw)
            seen[key] += 1
            yield {
                "source_id": f"{self.name}:{key}:{seen[key]}",
                "source_key": f"{key}:{seen[key]}", "source_file": self.name,
                "source_row": number, "input_zip_sha256": self.zip_sha256,
                "input_archive": self.archive_name, "role": role,
                "row": dict(raw),
            }


def load_inputs(r3b2_zip, r3b3_zip):
    tables = {}
    for archive_key, path in (("r3b2", Path(r3b2_zip)), ("r3b3", Path(r3b3_zip))):
        archive_hash = sha256_file(path)
        with zipfile.ZipFile(path) as archive:
            for key, (owner, filename) in SOURCE_FILES.items():
                if owner != archive_key:
                    continue
                matches = [n for n in archive.namelist() if PurePosixPath(n).name == filename]
                if len(matches) != 1:
                    raise SchemaError(f"{path.name}: expected exactly one {filename}; found {matches}")
                name = matches[0]
                with archive.open(name) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig", newline="") as stream:
                    reader = csv.DictReader(stream)
                    fields = reader.fieldnames or []
                    if len(fields) != len(set(fields)):
                        raise SchemaError(f"{name}: duplicate column names")
                    rows = list(reader)
                    if any(None in row or any(v is None for v in row.values()) for row in rows):
                        raise SchemaError(f"{name}: malformed CSV record")
                    tables[key] = Table(name, fields, rows, archive_hash, path.name)
    validate_schemas(tables)
    return tables


def validate_schemas(tables):
    for key, fields in SCHEMAS.items():
        if key not in tables:
            raise SchemaError(f"Missing source table: {key}")
        missing = set(fields) - set(tables[key].fields)
        if missing:
            raise SchemaError(f"{tables[key].name}: missing required columns {sorted(missing)}")
        for i, row in enumerate(tables[key].rows, 1):
            if any(field not in row for field in fields):
                raise SchemaError(f"{tables[key].name} row {i}: missing required values")


def unique_records(records, field, label):
    result = {}
    for record in records:
        key = record["row"][field].strip()
        if not key or key in result:
            raise InvariantError(f"{label}: blank/duplicate {field}={key!r}; record={canonical(record)}")
        result[key] = record
    return result


def ancestry_paths(members):
    paths = {}
    for bundle in sorted(members):
        chain, seen, current = [], set(), bundle
        while current:
            if current in seen:
                raise InvariantError(f"Genealogy cycle: {chain + [current]}")
            if current not in members:
                raise InvariantError(f"Missing parent {current}; path={chain}")
            seen.add(current)
            chain.append(current)
            row = members[current]["row"]
            if row["lineage_id"] != members[bundle]["row"]["lineage_id"]:
                raise InvariantError(f"Cross-lineage parent: {bundle} -> {current}")
            current = row["parent_bundle_id"]
        paths[bundle] = list(reversed(chain))
    return paths


class SpanContext:
    """Ordered verses and word-overlap structures, bounded to a configured book."""
    def __init__(self, book, verses, structures):
        self.book = book
        self.verses = verses
        self.positions = {v["ref"]: i for i, v in enumerate(verses)}
        self.structures = structures

    def context(self, start, end):
        a, b = span(start, end, self.book)
        start, end = ref_text(a), ref_text(b)
        result = {"book": self.book, "ref_start": start, "ref_end": end,
                  "resolution_status": "UNRESOLVED", "prev_ref": "", "prev_text": "",
                  "span_text": "", "next_ref": "", "next_text": "", "clauses": [], "sentences": []}
        if start not in self.positions or end not in self.positions:
            return result
        i, j = self.positions[start], self.positions[end]
        covered = self.verses[i:j + 1]
        words = set().union(*(v["words"] for v in covered))
        result["span_text"] = "\n".join(f"{v['ref']} :: {v['text']}" for v in covered)
        for prefix, index in (("prev", i - 1), ("next", j + 1)):
            if 0 <= index < len(self.verses):
                result[prefix + "_ref"] = self.verses[index]["ref"]
                result[prefix + "_text"] = self.verses[index]["text"]
        for kind in ("clauses", "sentences"):
            result[kind] = [{k: v for k, v in node.items() if k != "words"}
                            for node in self.structures[kind] if words.intersection(node["words"])]
        if covered and all(v["text"] for v in covered) and all(result[k] for k in ("clauses", "sentences")):
            result["resolution_status"] = "RESOLVED"
        return result


class TFContext(SpanContext):
    def __init__(self, tf_dir, book):
        tf_dir = Path(tf_dir).expanduser().resolve()
        for feature in ("otype.tf", "oslots.tf"):
            if not (tf_dir / feature).is_file():
                raise SchemaError(f"Missing BHSA feature: {tf_dir / feature}")
        from tf.fabric import Fabric
        api = Fabric(locations=str(tf_dir), modules=[""], silent="deep").load("g_word_utf8", silent="deep")
        if not api:
            raise InvariantError("BHSA Text-Fabric load failed")
        book_node = api.T.nodeFromSection((book,))
        if not book_node:
            raise InvariantError(f"BHSA book not found: {book}")

        def text(node):
            value = api.T.text(node, fmt="text-orig-full")
            if not value:
                value = " ".join(api.F.g_word_utf8.v(w) or "" for w in api.L.d(node, otype="word"))
            return " ".join(value.split())

        verses, book_words = [], set()
        for node in api.L.d(book_node, otype="verse"):
            section = api.T.sectionFromNode(node)
            words = set(api.L.d(node, otype="word"))
            book_words.update(words)
            verses.append({"ref": f"{section[1]}:{section[2]}", "text": text(node), "words": words})
        structures = {}
        for plural, kind in (("clauses", "clause"), ("sentences", "sentence")):
            # Ascend from every word: also finds structures crossing verse boundaries.
            nodes = {n for word in book_words for n in api.L.u(word, otype=kind)}
            structures[plural] = []
            for node in sorted(nodes):
                words = set(api.L.d(node, otype="word"))
                first, last = api.T.sectionFromNode(min(words)), api.T.sectionFromNode(max(words))
                structures[plural].append({"node_id": node, "words": words,
                    "ref_start": f"{first[0]} {first[1]}:{first[2]}",
                    "ref_end": f"{last[0]} {last[1]}:{last[2]}", "text": text(node)})
        super().__init__(book, verses, structures)


def source_span(record, book, exemplar=False):
    row = record["row"]
    prefix = "exemplar_" if exemplar else ""
    a, b = span(row[prefix + "ref_start"], row[prefix + "ref_end"], book)
    return {"ref_start": ref_text(a), "ref_end": ref_text(b),
            "surface_text": row[prefix + "surface_text"], "source_id": record["source_id"]}


def build_outcomes(tables, members, paths, orphan_ids, book):
    items = unique_records(tables["items"].records("g6_item"), "review_item_id", "G6 item")
    links = unique_records(tables["links"].records("g6_link"), "review_item_id", "G6 link")
    if set(items) != set(links):
        raise InvariantError(f"G6 item/link identity mismatch: {sorted(set(items) ^ set(links))}")
    outcomes = {}

    def branch(lineage, parent, record, transition):
        if parent not in members or members[parent]["row"]["lineage_id"] != lineage:
            raise InvariantError(f"Singleton parent/lineage conflict: {canonical(record)}")
        return {"lineage_id": lineage, "parent_bundle_id": parent, "transition": transition,
                "ancestry": paths[parent], "source_id": record["source_id"]}

    for item_id, item in sorted(items.items()):
        link = links[item_id]
        row = link["row"]
        if (not item["row"]["atom_node"] or item["row"]["atom_node"] != row["atom_node"] or
                item["row"]["atom_index_1based"] != row["atom_index_1based"]):
            raise InvariantError(f"G6 atom identity conflict: {canonical([item, link])}")
        lineage, parent = row["lineage_id"], row["parent_bundle_id_at_first_unique"]
        orphan = item_id in orphan_ids
        if orphan and (lineage or parent):
            raise InvariantError(f"Explicit orphan has parent/lineage: {canonical(link)}")
        if not orphan and (not lineage or not parent):
            raise InvariantError(f"Unclassified singleton parent: {canonical(link)}")
        branches = [] if orphan else [branch(lineage, parent, link, row.get("first_unique_level", ""))]
        spans = [source_span(r, book) for r in (item, link)]
        outcomes["G6:" + item_id] = {
            "object_id": "G6:" + item_id, "object_type": "SINGLETON_OUTCOME",
            "review_item_id": item_id, "outcome_kind": "G6_ONLY",
            "lineage_id": lineage, "link_status": "EXPLICIT_ORPHAN" if orphan else "LINKED",
            "surface_text": item["row"]["surface_text"], "branches": branches,
            "spans": spans, "sources": [item, link],
        }
    for event in tables["events"].records("refinement_event"):
        row = event["row"]
        mapped = row["mapped_g6_singleton_review_item_id"]
        b = branch(row["lineage_id"], row["parent_bundle_id"], event, row["parent_level"] + "→" + row["child_level"])
        s = source_span(event, book, True)
        if mapped:
            oid = "G6:" + mapped
            if oid not in outcomes:
                raise InvariantError(f"Mapped G6 missing: {mapped}; {canonical(event)}")
            outcome = outcomes[oid]
            if outcome["lineage_id"] != row["lineage_id"] or outcome["link_status"] == "EXPLICIT_ORPHAN":
                raise InvariantError(f"Mapped singleton lineage conflict: {canonical(outcome['sources'] + [event])}")
            if integer(row["sequence_length"], "mapped sequence_length") != 1:
                raise InvariantError(f"Mapped G6 sequence must be one atom: {canonical(event)}")
            if integer(row["exemplar_start_index_1based"], "event atom index") != integer(links[mapped]["row"]["atom_index_1based"], "G6 atom index"):
                raise InvariantError(f"Mapped atom identity conflict: {canonical([links[mapped], event])}")
            outcome["outcome_kind"] = "MAPPED"
            outcome["sources"].append(event)
            outcome["branches"].append(b)
            outcome["spans"].append(s)
        else:
            oid = "EVENT:" + event["source_key"]
            outcomes[oid] = {"object_id": oid, "object_type": "SINGLETON_OUTCOME", "review_item_id": "",
                "outcome_kind": "EVENT_ONLY", "lineage_id": row["lineage_id"], "link_status": "LINKED",
                "surface_text": s["surface_text"], "branches": [b], "spans": [s], "sources": [event]}
    for outcome in outcomes.values():
        spans = [span(s["ref_start"], s["ref_end"], book) for s in outcome["spans"]]
        if max(a for a, b in spans) > min(b for a, b in spans):
            raise InvariantError(f"Mapped provenance span conflict: {canonical(outcome['sources'])}")
        for key in ("sources", "branches", "spans"):
            outcome[key].sort(key=lambda r: r["source_id"])
    return dict(sorted(outcomes.items()))


def select_cases(containers, outcomes, config):
    if len(containers) < 18 or len(outcomes) < 6:
        raise InvariantError("Insufficient sampling population: need 18 containers and 6 singleton outcomes")
    seed = config["seed"]
    key = lambda r: (r["bundle_count"], r["singleton_outcome_count"], r["max_refinement_depth"], r["review_container_id"])
    high = sorted(containers, key=lambda r: (-r["bundle_count"], -r["singleton_outcome_count"],
                                            -r["max_refinement_depth"], r["review_container_id"]))[:6]
    used = {r["review_container_id"] for r in high}
    low = sorted([r for r in containers if r["review_container_id"] not in used], key=key)[:6]
    used.update(r["review_container_id"] for r in low)
    pool = sorted([r for r in containers if r["review_container_id"] not in used], key=lambda r: r["review_container_id"])
    sampled = random.Random(seed).sample(pool, 6)
    cases = []

    def add(kind, **data):
        cases.append({"case_id": f"CASE{len(cases) + 1:03d}", "case_type": kind,
                      "review_container_id": "", "lineage_id": "", "object_id": "",
                      "boundary_ref": "", "selection_reason": "", "seed": seed,
                      "bundle_count": "", "singleton_outcome_count": "", "max_refinement_depth": "",
                      **data, **review_defaults()})

    for kind, rows, reason in ((CASE_TYPES[0], high, "Descending structural lexicographic order"),
                               (CASE_TYPES[1], low, "Ascending structural order after HIGH exclusion"),
                               (CASE_TYPES[2], sampled, "Seeded sample after HIGH and LOW exclusion")):
        for row in rows:
            add(kind, **row, selection_reason=reason)
    singleton_ids = sorted(outcomes)
    control = config.get("singleton_control")
    chosen = []
    if control:
        oid = "G6:" + control["review_item_id"]
        if oid not in outcomes:
            raise InvariantError(f"Configured singleton regression control missing: {oid}")
        o = outcomes[oid]
        expected = span(control["ref_start"], control["ref_end"], config["book"])
        item_spans = [s for s in o["spans"] if s["source_id"] == next(p["source_id"] for p in o["sources"] if p["role"] == "g6_item")]
        if not any(span(s["ref_start"], s["ref_end"], config["book"]) == expected for s in item_spans):
            raise InvariantError(f"Singleton control span mismatch: {oid}")
        # Hebrew letters only; cantillation, punctuation and spacing are irrelevant to this optional regression.
        def letters(text):
            text = "".join(ch for ch in unicodedata.normalize("NFD", text) if not unicodedata.combining(ch))
            text = re.sub(r"\s+[פס]\s*$", "", text)  # BHSA trailing paragraph marker, not pattern words
            return "".join(ch for ch in text if "א" <= ch <= "ת")
        if control.get("surface_letters") and letters(control["surface_letters"]) != letters(o["surface_text"]):
            raise InvariantError(f"Singleton control surface mismatch: {oid}")
        if o["outcome_kind"] != "MAPPED" or not o["branches"]:
            raise InvariantError(f"Singleton control requires event/G6 provenance and ancestry: {oid}")
        chosen.append(oid)
    chosen.extend(random.Random(seed).sample([oid for oid in singleton_ids if oid not in chosen], 6 - len(chosen)))
    for oid in chosen:
        add(CASE_TYPES[3], object_id=oid, lineage_id=outcomes[oid]["lineage_id"],
            selection_reason="Configured regression control" if control and oid == "G6:" + control["review_item_id"] else "Seeded singleton-outcome sample")
    refs = config["boundary_refs"]
    if len(refs) != 6 or len(set(refs)) != 6:
        raise InvariantError("Pilot configuration requires six distinct boundary references")
    for ref in refs:
        add(CASE_TYPES[4], boundary_ref=ref, selection_reason="Configured full boundary panel")
    return cases


def build_model(tables, config, provider):
    validate_schemas(tables)
    config = dict(config)
    if not isinstance(config.get("book"), str) or not config["book"].strip():
        raise SchemaError("Pilot configuration requires a nonblank book")
    if type(config.get("seed")) is not int:
        raise SchemaError("Pilot configuration requires an integer seed")
    book = config["book"]
    config["boundary_refs"] = [ref_text(reference(r, book)) for r in config["boundary_refs"]]
    members = unique_records(tables["members"].records("bundle_membership"), "bundle_id", "membership")
    workspace_records = list(tables["workspace"].records("navigation_container"))
    workspace = unique_records(workspace_records, "review_container_id", "container")
    paths = ancestry_paths(members)
    lineages = defaultdict(list)
    for bundle, record in members.items():
        row = record["row"]
        if not row["lineage_id"]:
            raise InvariantError(f"Blank membership lineage: {canonical(record)}")
        if integer(row["refinement_depth"], "refinement_depth") != len(paths[bundle]) - 1:
            raise InvariantError(f"Source depth disagrees with ancestry: {canonical(record)}")
        lineages[row["lineage_id"]].append(bundle)
    for lineage, bundles in lineages.items():
        if len({paths[b][0] for b in bundles}) != 1:
            raise InvariantError(f"Lineage has multiple roots: {lineage}")
    orphan_ids = {r["row"]["orphan_singleton_review_item_id"] for r in workspace.values() if r["row"]["orphan_singleton_review_item_id"]}
    outcomes = build_outcomes(tables, members, paths, orphan_ids, book)
    containers = []
    seen_lineages, seen_orphans = set(), set()
    for cid, record in sorted(workspace.items()):
        row = record["row"]
        lineage, orphan = row["lineage_id"], row["orphan_singleton_review_item_id"]
        if bool(lineage) == bool(orphan):
            raise InvariantError(f"Container must identify lineage or explicit orphan: {canonical(record)}")
        if lineage and (lineage not in lineages or lineage in seen_lineages):
            raise InvariantError(f"Container lineage missing/duplicate: {canonical(record)}")
        if orphan and ("G6:" + orphan not in outcomes or orphan in seen_orphans):
            raise InvariantError(f"Container orphan missing/duplicate: {canonical(record)}")
        seen_lineages.add(lineage) if lineage else seen_orphans.add(orphan)
        bundles = lineages.get(lineage, [])
        count = len(bundles)
        if integer(row["bundle_count"], "bundle_count") != count:
            raise InvariantError(f"Container bundle count mismatch: {cid}")
        depth = max((len(paths[b]) - 1 for b in bundles), default=0)
        # Empty depth is meaningful only for explicit orphan containers with no genealogy.
        source_depth = 0 if orphan and row["max_refinement_depth"] == "" else integer(row["max_refinement_depth"], "max_refinement_depth")
        if depth != source_depth:
            raise InvariantError(f"Container depth mismatch: {cid}")
        oids = [oid for oid, o in outcomes.items() if (lineage and o["lineage_id"] == lineage) or (orphan and oid == "G6:" + orphan)]
        containers.append({"review_container_id": cid, "lineage_id": lineage,
                           "bundle_count": count, "singleton_outcome_count": len(oids),
                           "max_refinement_depth": depth})
    if set(lineages) != seen_lineages:
        raise InvariantError(f"Navigation containers omit lineages: {sorted(set(lineages) - seen_lineages)}")
    cases = select_cases(containers, outcomes, config)
    occurrences = list(tables["occurrences"].records("bundle_occurrence"))
    for record in occurrences:
        if record["row"]["bundle_id"] not in members:
            raise InvariantError(f"Occurrence membership missing: {canonical(record)}")
        source_span(record, book)
    model = {"config": config, "tables": tables, "members": members, "workspace": workspace,
             "ancestry": paths, "all_outcomes": outcomes, "cases": cases,
             "container_evidence": [], "boundary_evidence": [], "outcomes": [], "overlay": [],
             "provenance": [], "contexts": {}, "case_objects": defaultdict(set),
             "case_bundles": defaultdict(set), "case_outcomes": defaultdict(set),
             "expected_overlay": set(), "expected_boundary": set(),
             "population": {"row_count": len(workspace_records), "unique_id_count": len(workspace),
                            "blank_id_count": sum(not r["row"]["review_container_id"].strip() for r in workspace_records),
                            "duplicate_id_count": len(workspace_records) - len(workspace)}}
    provenance_seen = set()

    def provenance(oid, record):
        key = oid, record["source_id"]
        if key not in provenance_seen:
            provenance_seen.add(key)
            model["provenance"].append({"object_id": oid, **{k: v for k, v in record.items() if k != "row"},
                                        "source_row_json": record["row"]})

    def context(start, end):
        a, b = span(start, end, book)
        cid = f"{book}:{ref_text(a)}..{ref_text(b)}"
        if cid not in model["contexts"]:
            model["contexts"][cid] = {"context_id": cid, **provider.context(ref_text(a), ref_text(b))}
        return cid

    def repeated(case, record, occurrence=False, ancestry_only=False):
        row = record["row"]
        bundle = row["bundle_id"]
        member = members[bundle]
        s = source_span(record, book, not occurrence)
        oid = ("OCC:" + record["source_key"]) if occurrence else "BUNDLE:" + bundle
        result = {"case_id": case["case_id"], "object_id": oid,
            "object_type": "REPEATED_BUNDLE_OCCURRENCE" if occurrence else "REPEATED_BUNDLE",
            "review_container_id": case["review_container_id"], "bundle_id": bundle,
            "lineage_id": member["row"]["lineage_id"], "parent_bundle_id": member["row"]["parent_bundle_id"],
            "ancestry": paths[bundle], "evidence_role": "ANCESTRY" if ancestry_only else "CASE_EVIDENCE",
            **s, "context_id": context(s["ref_start"], s["ref_end"])}
        provenance(oid, record)
        provenance(oid, member)
        model["case_objects"][case["case_id"]].add(oid)
        return result

    used_outcomes = set()
    for case in cases:
        case_id = case["case_id"]
        selected_bundles, selected_outcomes = set(), set()
        target = model["container_evidence"]
        if case["case_type"] in CASE_TYPES[:3]:
            lineage = case["lineage_id"]
            selected_bundles.update(lineages.get(lineage, []))
            orphan = workspace[case["review_container_id"]]["row"]["orphan_singleton_review_item_id"]
            selected_outcomes.update(oid for oid, o in outcomes.items() if (lineage and o["lineage_id"] == lineage) or (orphan and oid == "G6:" + orphan))
            provenance(case_id, workspace[case["review_container_id"]])
        elif case["case_type"] == "SINGLETON_ITEM":
            selected_outcomes.add(case["object_id"])
        else:
            target = model["boundary_evidence"]
            case["context_id"] = context(case["boundary_ref"], case["boundary_ref"])
            for record in occurrences:
                row = record["row"]
                if contains(row["ref_start"], row["ref_end"], case["boundary_ref"], book):
                    evidence = repeated(case, record, True)
                    target.append(evidence)
                    model["expected_boundary"].add((case_id, evidence["object_id"]))
                    selected_bundles.add(row["bundle_id"])
            for oid, o in outcomes.items():
                if any(contains(s["ref_start"], s["ref_end"], case["boundary_ref"], book) for s in o["spans"]):
                    selected_outcomes.add(oid)
                    model["expected_boundary"].add((case_id, oid))
        if case["case_type"] in CASE_TYPES[:3]:
            for record in occurrences:
                if record["row"]["bundle_id"] in selected_bundles:
                    target.append(repeated(case, record, True))
        for oid in sorted(selected_outcomes):
            o = outcomes[oid]
            model["case_objects"][case_id].add(oid)
            model["case_outcomes"][case_id].add(oid)
            target.append({"case_id": case_id, "object_id": oid, "object_type": "SINGLETON_OUTCOME",
                           "lineage_id": o["lineage_id"], "evidence_role": "CASE_EVIDENCE"})
            for b in o["branches"]:
                selected_bundles.update(b["ancestry"])
            used_outcomes.add(oid)
        expanded = set(selected_bundles)
        for bundle in selected_bundles:
            expanded.update(paths[bundle])
        model["case_bundles"][case_id] = expanded
        for bundle in sorted(expanded):
            target.append(repeated(case, members[bundle], ancestry_only=case["case_type"] not in CASE_TYPES[:3]))

    for oid in sorted(used_outcomes):
        o = outcomes[oid]
        for s in o["spans"]:
            s["context_id"] = context(s["ref_start"], s["ref_end"])
        for record in o["sources"]:
            provenance(oid, record)
        model["outcomes"].append(o)

    # Only the explicitly documented R3b.3 exemplar-start schema is supported here.
    # Counts such as verified_subwindow_count are not occurrence-level locations.
    relations = list(tables["overlay"].records("sequence_extension"))
    for record in relations:
        row = record["row"]
        for side in ("short", "long"):
            bundle = row[side + "_bundle_id"]
            if bundle not in members or members[bundle]["row"]["lineage_id"] != row[side + "_lineage_id"]:
                raise InvariantError(f"Overlay endpoint membership conflict: {canonical(record)}")
        refs = [row[side + "_exemplar_ref_start"] for side in ("short", "long")]
        valid_refs = []
        for r in refs:
            if r:
                valid_refs.append(ref_text(reference(r, book)))
        coverage = "EXEMPLAR_ONLY" if len(valid_refs) == 2 else "UNRESOLVED"
        relation_id = "EXT:" + record["source_key"]
        for case in cases:
            cid = case["case_id"]
            if case["case_type"] == "BOUNDARY_CONTROL":
                # Unlocatable relations incident to the panel's evidence remain visible as unresolved.
                relevant = case["boundary_ref"] in valid_refs
                if coverage == "UNRESOLVED":
                    relevant |= bool({row["short_bundle_id"], row["long_bundle_id"]} & model["case_bundles"][cid])
            else:
                case_lineages = {members[b]["row"]["lineage_id"] for b in model["case_bundles"][cid]}
                relevant = bool(case_lineages & {row["short_lineage_id"], row["long_lineage_id"]})
            if relevant:
                model["overlay"].append({"case_id": cid, "relation_id": relation_id, "relation_layer": OVERLAY,
                    "coverage": coverage, "coverage_note": "Exemplar starts only; boundary extension coverage is not exhaustive.",
                    "relation": row["relation"], "short_bundle_id": row["short_bundle_id"],
                    "long_bundle_id": row["long_bundle_id"], "short_lineage_id": row["short_lineage_id"],
                    "long_lineage_id": row["long_lineage_id"], "short_exemplar_ref_start": refs[0],
                    "long_exemplar_ref_start": refs[1], "source_id": record["source_id"]})
                model["expected_overlay"].add((cid, relation_id))
                provenance(relation_id, record)
    for key in ("container_evidence", "boundary_evidence", "overlay", "provenance"):
        model[key].sort(key=lambda r: (r.get("case_id", ""), r.get("object_id", r.get("relation_id", "")), r.get("source_id", "")))
    return model


def build_gates(model):
    gates = []

    def add(name, problems, detail):
        problems = list(problems)
        gates.append({"gate_id": name, "status": "FAIL" if problems else "PASS",
                      "detail": detail, "violations": problems})

    core = model["container_evidence"] + model["boundary_evidence"] + model["outcomes"]
    members = model["members"]
    repeated = [r for r in core if r.get("object_type") in ("REPEATED_BUNDLE", "REPEATED_BUNDLE_OCCURRENCE")]
    add("CORE_LINEAGE_MATCHES_MEMBERSHIP",
        [r.get("object_id") for r in repeated if r.get("bundle_id") not in members or
         r.get("lineage_id") != members[r["bundle_id"]]["row"]["lineage_id"]],
        f"Checked {len(repeated)} repeated evidence rows against source membership")
    bad_parents = []
    for outcome in model["outcomes"]:
        if outcome["link_status"] == "EXPLICIT_ORPHAN":
            valid = not outcome["lineage_id"] and not outcome["branches"] and any(
                r["row"]["orphan_singleton_review_item_id"] == outcome["review_item_id"] for r in model["workspace"].values())
            if not valid:
                bad_parents.append(outcome["object_id"])
        elif not outcome["branches"]:
            bad_parents.append(outcome["object_id"])
        for branch in outcome["branches"]:
            p = branch["parent_bundle_id"]
            if (p not in members or members[p]["row"]["lineage_id"] != branch["lineage_id"]
                    or branch["lineage_id"] != outcome["lineage_id"]):
                bad_parents.append({"object_id": outcome["object_id"], "branch": branch})
    add("SINGLETON_PARENT_LINEAGE_MATCHES", bad_parents, "All emitted singleton branch parents checked; explicit orphans validated separately")
    add("NO_EXTENSION_OBJECT_IN_CORE",
        [r.get("object_id") for r in core if r.get("object_type") not in
         {"REPEATED_BUNDLE", "REPEATED_BUNDLE_OCCURRENCE", "SINGLETON_OUTCOME"} or r.get("relation_layer") == OVERLAY],
        f"Checked {len(core)} core objects/attachments")
    extension_fields = {"relation", "relation_id", "relation_layer", "short_bundle_id", "long_bundle_id"}
    violations = [r.get("object_id") for r in core + model["cases"] if extension_fields & set(r)]
    actual = {(r["case_id"], r["relation_id"]) for r in model["overlay"]}
    violations.extend(sorted(model["expected_overlay"] ^ actual))
    violations.extend(r["relation_id"] for r in model["overlay"] if r["relation_layer"] != OVERLAY or not r["relation"])
    if len(actual) != len(model["overlay"]):
        violations.append("Duplicate case/relation attachment")
    extension_ids = {p["object_id"] for p in model["provenance"] if p["role"] == "sequence_extension"}
    violations.extend(r.get("object_id") for r in core if r.get("object_id") in extension_ids)
    add("EXTENSION_RELATIONS_OVERLAY_ONLY", violations, "Compared emitted overlay relations with selected source relations and checked core field/provenance separation")
    population = model["population"]
    add("SOURCE_CONTAINER_IDS", [population] if population["blank_id_count"] or population["duplicate_id_count"] or
        population["row_count"] != population["unique_id_count"] else [], canonical(population))
    counts = Counter(c["case_type"] for c in model["cases"])
    add("FIVE_GROUPS_OF_SIX", [dict(counts)] if dict(counts) != dict.fromkeys(CASE_TYPES, 6) else [], "Exactly 30 cases")
    ids = [c["review_container_id"] for c in model["cases"] if c["case_type"] in CASE_TYPES[:3]]
    add("CONTAINER_STRATA_DISJOINT", ids if len(ids) != len(set(ids)) else [], "HIGH, LOW and RANDOM containers are disjoint")
    add("CANONICAL_REVIEW_DEFAULTS", [c["case_id"] for c in model["cases"] if
        {field: c.get(field) for field in REVIEW_FIELDS} != review_defaults()], "Checked every canonical review field")
    add("NO_FUNCTION_AUTOLABEL", [r.get("case_id", r.get("object_id")) for r in core + model["cases"] + model["overlay"]
        if any(r.get(field) for field in FORBIDDEN_FIELDS)], "No populated automatic function/rhetorical fields in generated review data")
    boundaries = [c for c in model["cases"] if c["case_type"] == "BOUNDARY_CONTROL"]
    add("BOUNDARY_CASES", [] if Counter(c["boundary_ref"] for c in boundaries) == Counter(model["config"]["boundary_refs"])
        else [c["boundary_ref"] for c in boundaries], "Every configured boundary is a panel-level review case")
    actual_boundary = {(r["case_id"], r["object_id"]) for r in model["boundary_evidence"] if r["evidence_role"] == "CASE_EVIDENCE"}
    add("BOUNDARY_ALL_OCCURRENCES_AND_OUTCOMES", sorted(model["expected_boundary"] ^ actual_boundary), "Occurrence identity and folded outcome sets compared")
    provenance_ids = {p["object_id"] for p in model["provenance"]}
    singletons = [c for c in model["cases"] if c["case_type"] == "SINGLETON_ITEM"]
    add("SINGLETON_CASE_PROVENANCE", [c["case_id"] for c in singletons if c["object_id"] not in provenance_ids or
        c["object_id"] not in {o["object_id"] for o in model["outcomes"]}], "Independent singleton cases resolve to outcomes and source snapshots")
    missing_provenance = []
    provenance_by_object = defaultdict(set)
    for p in model["provenance"]:
        provenance_by_object[p["object_id"]].add(p["source_id"])
    for o in model["outcomes"]:
        emitted = provenance_by_object[o["object_id"]]
        expected = {r["source_id"] for r in model["all_outcomes"][o["object_id"]]["sources"]}
        if emitted != expected:
            missing_provenance.append(o["object_id"])
    add("FOLDED_PROVENANCE_COMPLETE", missing_provenance, "All source rows for each folded outcome preserved")
    try:
        reconstructed = ancestry_paths(members)
        bad_paths = [b for b in reconstructed if reconstructed[b] != model["ancestry"].get(b)]
    except InvariantError as error:
        bad_paths = [str(error)]
    add("GENEALOGY_PARENTS_AND_CYCLES", bad_paths, "Source parent graph revalidated")
    add("SPAN_CONTEXT_RESOLVES", [k for k, c in model["contexts"].items() if c["resolution_status"] != "RESOLVED"],
        "Full spans, overlapping clauses and sentences resolve; synthetic runs are not BHSA validation")
    add("BOUNDARY_TF_CONTEXT", [c["case_id"] for c in boundaries if model["contexts"].get(c.get("context_id"), {}).get("resolution_status") != "RESOLVED"],
        "All six boundary contexts resolve in the active provider")
    # Preserve every member in container cases; no truncation or candidate-count target.
    problems = []
    for c in model["cases"]:
        if c["case_type"] not in CASE_TYPES[:3]:
            continue
        expected = {b for b, r in members.items() if r["row"]["lineage_id"] == c["lineage_id"]}
        actual = {r["bundle_id"] for r in model["container_evidence"] if r["case_id"] == c["case_id"] and r["object_type"] == "REPEATED_BUNDLE"}
        if expected != actual:
            problems.append(c["case_id"])
    add("CONTAINER_MEMBERS_COMPLETE", problems, "All selected navigation members preserved")
    return gates


def render_packet(model):
    """One outcome detail per case; branch links retain every source parent."""
    lines = [f"# MILAL {VERSION} — Human Review Case Pilot", "",
             "Purpose: reviewability and context sufficiency. Time is diagnostic only; no population time estimate.", "",
             f"Book: {model['config']['book']}; sampling seed: {model['config']['seed']}.", "",
             "Extension coverage: EXEMPLAR_ONLY or UNRESOLVED. Boundary extension coverage is not exhaustive.", ""]
    by_case = defaultdict(list)
    for row in model["container_evidence"] + model["boundary_evidence"]:
        by_case[row["case_id"]].append(row)
    provenance = defaultdict(list)
    for row in model["provenance"]:
        provenance[row["object_id"]].append(row)
    displayed_contexts = set()
    active_case = ""

    def context_block(context_id):
        anchor = f"context-{active_case.lower()}-{digest(context_id)[:12]}"
        if context_id in displayed_contexts:
            lines.append(f"- Context: [covering verses, neighbors and structures](#{anchor}) (`{context_id}`; already shown in this case).")
            return
        displayed_contexts.add(context_id)
        ctx = model["contexts"][context_id]
        lines.extend([f'<a id="{anchor}"></a>', "", f"- Context `{context_id}`: **{ctx['resolution_status']}**",
                      f"  - Previous {ctx['prev_ref'] or '[book start]'}: {ctx['prev_text']}",
                      "  - Complete covering verses:"])
        lines.extend("    - " + text for text in ctx["span_text"].splitlines())
        lines.append(f"  - Next {ctx['next_ref'] or '[book end]'}: {ctx['next_text']}")
        for kind in ("clauses", "sentences"):
            lines.append(f"  - Overlapping {kind}:")
            for node in ctx[kind]:
                lines.append(f"    - `{node['node_id']}` {node['ref_start']}–{node['ref_end']}: {node['text']}")

    def sources(oid):
        lines.append("- Provenance:")
        for p in provenance[oid]:
            lines.append(f"  - {p['role']}: `{p['input_archive']}` / `{p['source_file']}` data row {p['source_row']}; key `{p['source_key']}`")

    for case in model["cases"]:
        cid = case["case_id"]
        active_case = cid
        displayed_contexts.clear()
        lines.extend([f"## {cid} — {case['case_type']}", "",
                      f"- Selection: {case['selection_reason']}",
                      f"- Container: `{case['review_container_id'] or '-'}`; lineage: `{case['lineage_id'] or '-'}`",
                      f"- Target outcome: `{case['object_id'] or '-'}`; boundary: `{case['boundary_ref'] or '-'}`", ""])
        if case["case_type"] in CASE_TYPES[:3]:
            lines.append(f"Structural measures: bundles={case['bundle_count']}; singleton outcomes={case['singleton_outcome_count']}; max depth={case['max_refinement_depth']}.")
        if case["case_type"] == "BOUNDARY_CONTROL":
            lines.extend(["Is the currently available MILAL evidence sufficient to analyze this textual transition?", ""])
            context_block(case["context_id"])
        lines.extend(["", "### Refinement genealogy", ""])
        children = defaultdict(list)
        for bundle in sorted(model["case_bundles"][cid]):
            children[model["members"][bundle]["row"]["parent_bundle_id"]].append(bundle)
        attached = defaultdict(set)
        for oid in sorted(model["case_outcomes"][cid]):
            for branch in model["all_outcomes"][oid]["branches"]:
                attached[branch["parent_bundle_id"]].add(oid)
        stack = [(b, 0) for b in reversed(children[""])]
        while stack:
            bundle, depth = stack.pop()
            lines.append("  " * depth + f"- {bundle}")
            for oid in sorted(attached[bundle]):
                lines.append("  " * (depth + 1) + f"- SINGLETON_OUTCOME `{oid}` (branch link; one detail below)")
            stack.extend((b, depth + 1) for b in reversed(children[bundle]))
        if not children[""]:
            lines.append("- No repeated ancestor (explicit orphan).")
        lines.extend(["", "### Repeated evidence and occurrence contexts", ""])
        for row in by_case[cid]:
            if row["object_type"] == "SINGLETON_OUTCOME":
                continue
            lines.extend([f"#### {row['object_type']} `{row['object_id']}`", "",
                          f"- Bundle `{row['bundle_id']}`; {row['evidence_role']}; ancestry: {' → '.join(row['ancestry'])}",
                          f"- Exact source surface ({row['ref_start']}–{row['ref_end']}): {row['surface_text']}"])
            context_block(row["context_id"])
            sources(row["object_id"])
            lines.append("")
        lines.extend(["### Singleton outcomes", ""])
        for oid in sorted(model["case_outcomes"][cid]):
            o = model["all_outcomes"][oid]
            lines.extend([f"#### SINGLETON_OUTCOME `{oid}`", "",
                          f"- Kind: {o['outcome_kind']}; status: {o['link_status']}; lineage: `{o['lineage_id'] or '-'}`"])
            for branch in o["branches"]:
                lines.append(f"- Branch: {' → '.join(branch['ancestry'])}; transition {branch['transition']}; source `{branch['source_id']}`")
            seen_contexts = set()
            for s in o["spans"]:
                lines.append(f"- Source `{s['source_id']}` surface ({s['ref_start']}–{s['ref_end']}): {s['surface_text']}")
                if s["context_id"] not in seen_contexts:
                    context_block(s["context_id"])
                    seen_contexts.add(s["context_id"])
            sources(oid)
            lines.append("")
        lines.extend(["### Sequence-extension overlay — separate from genealogy", "",
                      "Exemplar starts are evidence of limited coverage, not an exhaustive occurrence/subwindow search.", ""])
        overlays = [r for r in model["overlay"] if r["case_id"] == cid]
        for r in overlays:
            lines.append(f"- `{r['relation_id']}`: {r['short_bundle_id']} → {r['long_bundle_id']}; {r['relation']}; **{r['coverage']}**; exemplar starts {r['short_exemplar_ref_start']} / {r['long_exemplar_ref_start']}")
            sources(r["relation_id"])
        if not overlays:
            lines.append("- No matches established from available exemplar evidence; this does not establish absence of extension relations.")
        lines.extend(["", "### Human review", ""])
        lines.extend(f"- {field}: {case[field]}" for field in REVIEW_FIELDS)
        lines.append("")
    return "\n".join(lines) + "\n"


METHOD_NOTE = """# MILAL R3c.0.2 method

R3b.3 is a frozen navigation layer. These 30 cases test human reviewability and
context sufficiency; they do not redefine lineages or optimize candidate counts.
No rhetorical, discourse, theological or function labels are assigned.
Review time is diagnostic only. Do not extrapolate population review hours.

HIGH uses (bundle count descending, distinct singleton outcome count descending,
maximum refinement depth descending, container ID ascending). LOW uses ascending
structural measures after HIGH exclusion. RANDOM samples six from the remaining
ID-sorted containers. A separate random generator with the same recorded seed
selects singleton outcomes after the configured singleton control. The five
groups contain six cases each. Singleton and boundary cases may reuse evidence
from a container case; the three container strata cannot overlap.

Only mapped_g6_singleton_review_item_id explicitly matching review_item_id folds
events into a canonical G6 outcome. No text/span/signature similarity folding is
performed. EVENT_ONLY and G6_ONLY outcomes survive. All event records, branches,
transitions, surfaces and spans remain in provenance snapshots. Compatible
overlapping spans are preserved separately; non-overlapping mapped spans,
conflicting lineage, atom identity or mapped sequence length fail explicitly.
Multiple parents within the same lineage are retained, not reduced to one.

Source provenance uses input ZIP SHA256, archive member path, one-based CSV data
row (excluding header), content-derived source key and role. Hashes identify
source records only; they never establish singleton equivalence. Duplicate
source records remain distinct. Only referenced rows are snapshotted; input ZIPs
and complete input tables are not copied into the result. SHA256 locates the
exact original input even if its human-readable name changes.

The supported extension input is R3b.3 07_sequence_extension_lineage_overlay.csv.
Its short/long exemplar starts establish EXEMPLAR_ONLY coverage, not occurrence
coverage. Missing starts produce UNRESOLVED. verified_subwindow_count is a count,
not location evidence. No OCCURRENCE_VERIFIED claim is made by this adapter.
Boundary extension coverage is not exhaustive. Unknown relation schemas require
an explicit new adapter and tests, never inferred columns.

Context uses complete verses from start through end (including cross-chapter
spans), the immediately preceding/following verse within the configured book,
and every clause/sentence sharing words with those complete verses. Structures
crossing a verse boundary are found by ascending from words. At book edges the
neighbor is blank; the context does not wrap into another book. Exact source
pattern surface remains separate from the covering verse context. No speaker or
macro labels are invented. TF loads BHSA g_word_utf8 and uses text-orig-full,
falling back to joined word text when empty. All selected spans must resolve.

Review fields are derived from REVIEW_FIELDS. Only status starts UNREVIEWED.
Branch references can point to the same outcome, whose detail appears once per
case. Repeated bundle identities and all relevant occurrences remain separate.
Container packets include all bundle occurrences; this may still be large.
Volume is measured as reviewability evidence, not reduced by truncation.

Synthetic tests do not establish empirical acceptance. Run with BHSA 2021 on
Termux and inspect the resulting ZIP and human-facing packet before acceptance.
"""


def write_csv(path, rows, fields=None):
    rows = list(rows)
    if fields is None:
        fields = sorted({k for row in rows for k in row})
    with Path(path).open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="raise")
        writer.writeheader()
        for row in rows:
            writer.writerow({k: canonical(v) if isinstance(v, (dict, list, tuple)) else v for k, v in row.items()})


def write_manifest(out):
    rows = [{"file": p.name, "bytes": p.stat().st_size, "sha256": sha256_file(p)}
            for p in sorted(out.iterdir()) if p.is_file() and p.name != "99_manifest_sha256.csv"]
    write_csv(out / "99_manifest_sha256.csv", rows, ["file", "bytes", "sha256"])


def write_outputs(model, out, metadata=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    inventory = [{"source": k, "source_file": t.name, "row_count": len(t.rows), "columns": t.fields,
                  "input_zip_sha256": t.zip_sha256, "input_archive": t.archive_name} for k, t in sorted(model["tables"].items())]
    write_csv(out / "01_source_schema_inventory.csv", inventory)
    base_fields = ["case_id", "case_type", "review_container_id", "lineage_id", "object_id", "boundary_ref",
                   "selection_reason", "seed", "bundle_count", "singleton_outcome_count", "max_refinement_depth", "context_id"]
    write_csv(out / "02_review_cases.csv", model["cases"], base_fields + list(REVIEW_FIELDS))
    evidence_fields = ["case_id", "object_id", "object_type", "review_container_id", "bundle_id", "lineage_id",
                       "parent_bundle_id", "ancestry", "evidence_role", "ref_start", "ref_end", "surface_text", "source_id", "context_id"]
    write_csv(out / "03_container_case_evidence.csv", model["container_evidence"], evidence_fields)
    outcome_rows = [{k: v for k, v in o.items() if k != "sources"} for o in model["outcomes"]]
    write_csv(out / "04_singleton_outcomes.csv", outcome_rows,
              ["object_id", "object_type", "review_item_id", "outcome_kind", "lineage_id", "link_status", "surface_text", "branches", "spans"])
    write_csv(out / "05_object_provenance.csv", model["provenance"])
    write_csv(out / "06_boundary_case_evidence.csv", model["boundary_evidence"], evidence_fields)
    write_csv(out / "07_sequence_extension_overlay.csv", model["overlay"],
              ["case_id", "relation_id", "relation_layer", "coverage", "coverage_note", "relation", "short_bundle_id",
               "long_bundle_id", "short_lineage_id", "long_lineage_id", "short_exemplar_ref_start", "long_exemplar_ref_start", "source_id"])
    write_csv(out / "08_span_context_inventory.csv", [model["contexts"][k] for k in sorted(model["contexts"])])
    (out / "09_review_packet.md").write_text(render_packet(model), encoding="utf-8")
    gates = build_gates(model)
    write_csv(out / "10_gates.csv", gates, ["gate_id", "status", "detail", "violations"])
    (out / "11_method_note.md").write_text(METHOD_NOTE, encoding="utf-8")
    meta = {"version": VERSION, "seed": model["config"]["seed"], "pilot_config": model["config"],
            "population": model["population"], "case_counts": dict(Counter(c["case_type"] for c in model["cases"])),
            "singleton_outcome_population": len(model["all_outcomes"]),
            "singleton_outcome_kinds": dict(Counter(o["outcome_kind"] for o in model["all_outcomes"].values())),
            "emitted_singleton_outcomes": len(model["outcomes"]), "context_count": len(model["contexts"]),
            "extension_coverage": dict(Counter(r["coverage"] for r in model["overlay"])),
            "boundary_extension_coverage_exhaustive": False,
            "input_archives": sorted({(t.archive_name, t.zip_sha256) for t in model["tables"].values()}),
            "empirical_acceptance": "PENDING_TERMUX_RESULT_AND_HUMAN_PACKET_INSPECTION",
            "gate_failures": [g["gate_id"] for g in gates if g["status"] == "FAIL"], **(metadata or {})}
    meta["exit_code"] = 2 if meta["gate_failures"] else 0
    (out / "90_run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_manifest(out)
    return 2 if meta["gate_failures"] else 0


def synthetic_fixture():
    """Small non-Job corpus with branching, multi-verse spans and explicit orphans."""
    book = "TestBook"
    refs = ["1:1", "1:2", "1:3", "2:1", "2:2", "2:3"]
    rows = {key: [] for key in SCHEMAS}
    for i in range(1, 25):
        lineage, cid = f"L{i:03d}", f"C{i:03d}"
        bundles = [f"B{i:03d}{chr(97 + j)}" for j in range(13 if i == 1 else 3)]
        ref = refs[(i - 1) % 6]
        for j, bundle in enumerate(bundles):
            end = "1:3" if i == 1 and j == 0 else ref
            rows["members"].append({"bundle_id": bundle, "lineage_id": lineage,
                "parent_bundle_id": bundles[0] if j else "", "refinement_depth": "1" if j else "0",
                "exemplar_ref_start": ref, "exemplar_ref_end": end, "exemplar_surface_text": f"SYNTH pattern {bundle}"})
            rows["occurrences"].append({"bundle_id": bundle, "window_id": f"W{bundle}",
                "ref_start": ref, "ref_end": end, "surface_text": f"SYNTH occurrence {bundle}"})
        rows["workspace"].append({"review_container_id": cid, "review_container_class": "REFINEMENT_LINEAGE",
            "lineage_id": lineage, "orphan_singleton_review_item_id": "", "bundle_count": str(len(bundles)), "max_refinement_depth": "1"})
        item = f"S{i:05d}"
        common = {"review_item_id": item, "ref_start": ref, "ref_end": ref,
                  "surface_text": f"SYNTH singleton {item}", "atom_node": str(100 + i), "atom_index_1based": str(i)}
        rows["items"].append(dict(common))
        rows["links"].append({**common, "lineage_id": lineage,
                              "parent_bundle_id_at_first_unique": bundles[1], "link_status": "LINKED"})
        rows["events"].append({"lineage_id": lineage, "parent_bundle_id": bundles[1],
            "parent_level": "P1", "child_level": "G6", "sequence_length": "1",
            "exemplar_start_index_1based": str(i),
            "exemplar_ref_start": ref, "exemplar_ref_end": ref, "exemplar_surface_text": common["surface_text"],
            "mapped_g6_singleton_review_item_id": item})
        if i == 1:
            rows["events"].append({**rows["events"][-1], "parent_bundle_id": bundles[2]})
        if i > 1:
            rows["overlay"].append({"relation": "EXTENDS", "short_bundle_id": "B001a", "long_bundle_id": bundles[0],
                "short_lineage_id": "L001", "long_lineage_id": lineage,
                "short_exemplar_ref_start": "1:1", "long_exemplar_ref_start": ref})
    common = {"review_item_id": "ORPHAN", "ref_start": "2:3", "ref_end": "2:3", "surface_text": "SYNTH orphan", "atom_node": "999", "atom_index_1based": "25"}
    rows["items"].append(dict(common))
    rows["links"].append({**common, "lineage_id": "", "parent_bundle_id_at_first_unique": "", "link_status": "NO_REPEATED_ANCESTOR_AT_G0"})
    rows["workspace"].append({"review_container_id": "ORPHAN", "review_container_class": "ORPHAN_SINGLETON_ROOT",
        "lineage_id": "", "orphan_singleton_review_item_id": "ORPHAN", "bundle_count": "0", "max_refinement_depth": ""})
    event_only = {"lineage_id": "L001", "parent_bundle_id": "B001c", "parent_level": "P2", "child_level": "P3",
                  "sequence_length": "2", "exemplar_ref_start": "1:1", "exemplar_ref_end": "1:3",
                  "exemplar_start_index_1based": "1",
                  "exemplar_surface_text": "SYNTH identical text distinct unlinked records", "mapped_g6_singleton_review_item_id": ""}
    rows["events"].extend([dict(event_only), dict(event_only)])
    tables = {key: Table(SOURCE_FILES[key][1], list(SCHEMAS[key]), value) for key, value in rows.items()}
    verses = [{"ref": ref, "text": "SYNTH verse " + ref, "words": {i}} for i, ref in enumerate(refs, 1)]
    structures = {kind: [{"node_id": f"{kind}-{i}", "words": {i}, "ref_start": ref, "ref_end": ref,
                          "text": f"SYNTH {kind} {ref}"} for i, ref in enumerate(refs, 1)] for kind in ("clauses", "sentences")}
    structures["sentences"].append({"node_id": "sentence-cross", "words": {3, 4}, "ref_start": "1:3", "ref_end": "2:1", "text": "SYNTH crossing sentence"})
    config = {"book": book, "seed": 20260917, "boundary_refs": refs,
              "singleton_control": {"review_item_id": "S00001", "ref_start": "1:1", "ref_end": "1:1"}}
    return tables, config, SpanContext(book, verses, structures)


def write_synthetic_archives(tables, root):
    paths = []
    for owner in ("r3b2", "r3b3"):
        path = root / (owner + ".zip")
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for key, table in tables.items():
                if SOURCE_FILES[key][0] == owner:
                    stream = io.StringIO(newline="")
                    writer = csv.DictWriter(stream, fieldnames=table.fields)
                    writer.writeheader()
                    writer.writerows(table.rows)
                    archive.writestr("synthetic/" + table.name, stream.getvalue().encode("utf-8-sig"))
        paths.append(path)
    return paths


def self_test(output_dir=None):
    import copy
    tables, config, provider = synthetic_fixture()
    with tempfile.TemporaryDirectory(prefix="milal_r3c002_") as tmp:
        root = Path(tmp)
        archives = write_synthetic_archives(tables, root)
        loaded = load_inputs(*archives)
        model = build_model(loaded, config, provider)
        assert all(g["status"] == "PASS" for g in build_gates(model))
        assert provider.context("1:1", "1:3")["next_ref"] == "2:1"
        assert provider.context("1:3", "2:1")["next_ref"] == "2:2"
        for table in loaded.values():
            table.rows.reverse()
        assert model["cases"] == build_model(loaded, config, provider)["cases"]
        for gate, mutate in (
            ("CORE_LINEAGE_MATCHES_MEMBERSHIP", lambda m: m["container_evidence"][0].update(lineage_id="BAD")),
            ("SINGLETON_PARENT_LINEAGE_MATCHES", lambda m: next(o for o in m["outcomes"] if o["branches"])["branches"][0].update(parent_bundle_id="BAD")),
            ("NO_EXTENSION_OBJECT_IN_CORE", lambda m: m["container_evidence"][0].update(object_type=OVERLAY)),
            ("EXTENSION_RELATIONS_OVERLAY_ONLY", lambda m: m["container_evidence"][0].update(relation="EXTENDS")),
        ):
            changed = copy.deepcopy(model)
            mutate(changed)
            assert next(g for g in build_gates(changed) if g["gate_id"] == gate)["status"] == "FAIL", gate
        for key, mutate in (
            ("workspace", lambda rows: rows[0].update(review_container_id="")),
            ("workspace", lambda rows: rows[0].update(review_container_id=rows[1]["review_container_id"])),
            ("members", lambda rows: rows[0].update(parent_bundle_id=rows[1]["bundle_id"])),
            ("members", lambda rows: rows[1].update(parent_bundle_id="MISSING")),
        ):
            fresh, c, p = synthetic_fixture()
            mutate(fresh[key].rows)
            try:
                build_model(fresh, c, p)
            except InvariantError:
                pass
            else:
                raise AssertionError(f"Negative fixture did not fail: {key}")
        out = Path(output_dir) if output_dir else root / "output"
        if out.exists() and any(out.iterdir()):
            raise InvariantError(f"Output directory must be empty: {out}")
        status = write_outputs(model, out, {"run_kind": "SYNTHETIC_SELF_TEST"})
        assert status == 0
        packet = (out / "09_review_packet.md").read_text(encoding="utf-8")
        assert "  - B001b" in packet and "sentence-cross" in packet
        assert packet.count("### Human review\n") == 30
        print(f"SELF-TEST PASS: 30 cases; {len(build_gates(model))} computed gates; negative invariants tested.")
        if output_dir:
            print(f"Synthetic packet retained: {out.resolve()}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="MILAL R3c.0.2 human review case pilot")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--r3b2-zip", type=Path, default=Path("job_r3b_2_results.zip"))
    parser.add_argument("--r3b3-zip", type=Path, default=Path("job_r3b_3_results.zip"))
    parser.add_argument("--tf-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--pilot-config", type=Path, default=Path(__file__).resolve().parents[1] / "config/r3c_0_2_job_pilot.json")
    parser.add_argument("--seed", type=int, help="Override pilot configuration seed")
    parser.add_argument("--expected-review-containers", type=int, help="Optional corpus regression assertion only")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test(args.output_dir)
    out = (args.output_dir or Path("milal_r3c_0_2_output")).expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        print(f"ERROR: output directory must be empty: {out}", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)
    meta = {"version": VERSION, "started_utc": datetime.now(timezone.utc).isoformat(), "run_kind": "REAL_BHSA",
            "tf_dir": str(args.tf_dir), "pilot_config_path": str(args.pilot_config),
            "empirical_acceptance": "PENDING_TERMUX_RESULT_AND_HUMAN_PACKET_INSPECTION"}
    try:
        config = json.loads(args.pilot_config.read_text(encoding="utf-8-sig"))
        if args.seed is not None:
            config["seed"] = args.seed
        meta["seed"] = config["seed"]
        meta["pilot_config_sha256"] = sha256_file(args.pilot_config)
        tables = load_inputs(args.r3b2_zip, args.r3b3_zip)
        meta["input_archives"] = sorted({(t.archive_name, t.zip_sha256) for t in tables.values()})
        if args.expected_review_containers is not None and len(tables["workspace"].rows) != args.expected_review_containers:
            raise InvariantError(f"Optional regression assertion: expected {args.expected_review_containers} containers, got {len(tables['workspace'].rows)}")
        if args.tf_dir is None:
            raise SchemaError("--tf-dir is required for a real run")
        provider = TFContext(args.tf_dir, config["book"])
        model = build_model(tables, config, provider)
        meta["finished_utc"] = datetime.now(timezone.utc).isoformat()
        status = write_outputs(model, out, meta)
    except Exception as error:
        status = 2
        message = f"{type(error).__name__}: {error}"
        meta.update(error=message, exit_code=status, finished_utc=datetime.now(timezone.utc).isoformat())
        (out / "00_FATAL_ERROR.txt").write_text(message + "\n", encoding="utf-8")
        write_csv(out / "10_gates.csv", [{"gate_id": "INPUT_OR_MODEL_VALIDATION", "status": "FAIL", "detail": message, "violations": [message]}])
        (out / "90_run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        write_manifest(out)
        print(message, file=sys.stderr)
    print(f"MILAL {VERSION}: {'PASS' if status == 0 else 'FAIL'}; output={out}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
