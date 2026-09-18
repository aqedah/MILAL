#!/usr/bin/env python3
"""Lossless presentation of a verified frozen R3c.1 result; no BHSA execution."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
import csv
from datetime import datetime, timezone
import hashlib
import html
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import zipfile

from milal_r3c_0_2_reviewability import REVIEW_FIELDS

VERSION = "R3c.2"
BUNDLE = "REPEATED_BUNDLE_UNIT"
SINGLETON = "SINGLETON_OUTCOME_UNIT"
OVERLAY = "SEQUENCE_EXTENSION_OVERLAY_ONLY"
FILES = {
    "inventory": "01_source_schema_inventory.csv", "cases": "02_review_cases.csv",
    "units": "03_review_unit_population.csv", "evidence": "04_case_evidence.csv",
    "relations": "05_relation_context.csv", "provenance": "06_object_provenance.csv",
    "boundary": "07_boundary_case_evidence.csv", "overlay": "08_sequence_extension_overlay.csv",
    "contexts": "09_span_context_inventory.csv", "packet": "10_review_packet.md",
    "gates": "11_gates.csv", "method": "12_method_note.md",
    "metadata": "90_run_metadata.json", "manifest": "99_manifest_sha256.csv",
}
EVIDENCE_FIELDS = ("case_id", "unit_id", "unit_type", "evidence_id", "bundle_id", "lineage_id",
                   "ref_start", "ref_end", "surface_text", "source_id", "context_id")
RELATION_FIELDS = ("case_id", "unit_id", "relation_kind", "related_unit_id", "lineage_id",
                   "ancestry", "transition", "source_id")
CONTEXT_FIELDS = ("context_id", "book", "ref_start", "ref_end", "prev_ref", "prev_text", "span_text",
                  "next_ref", "next_text", "clauses", "sentences", "resolution_status")
BUNDLE_SUMMARY = ("unit_id", "unit_type", "bundle_id", "lineage_id", "review_container_id",
                  "parent_bundle_id", "ancestry", "refinement_depth", "sequence_length", "occurrence_count",
                  "direct_repeated_child_count", "explicit_singleton_branch_count",
                  "exemplar_ref_start", "exemplar_ref_end", "exemplar_surface_text")
SINGLETON_SUMMARY = ("unit_id", "unit_type", "review_item_id", "lineage_id", "review_container_id",
                     "outcome_kind", "link_status", "surface_text")


class ValidationError(ValueError):
    def __init__(self, message, gates=None):
        super().__init__(message)
        self.gates = gates or []


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha(data):
    return hashlib.sha256(data).hexdigest()


def row_bag(rows):
    return Counter(canonical(r) for r in rows)


def csv_read(data, name):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    fields = reader.fieldnames or []
    if not fields or len(set(fields)) != len(fields):
        raise ValidationError(f"Missing/duplicate CSV columns: {name}")
    rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValidationError(f"Malformed CSV row: {name}")
    return fields, rows


def source_rows(source, key):
    return csv_read(source["files"][FILES[key]], FILES[key])[1]


def metadata(source):
    return json.loads(source["files"][FILES["metadata"]].decode("utf-8-sig"))


def check(name, problems, detail):
    problems = list(problems)
    return {"gate_id": name, "status": "FAIL" if problems else "PASS", "detail": detail, "violations": problems}


def preflight_gates(source):
    """Recompute from the actual archived bytes, never cached PASS booleans."""
    problems = []
    try:
        manifest = source_rows(source, "manifest")
        names = [r["file"] for r in manifest]
        expected = set(source["files"]) - {FILES["manifest"]}
        if len(names) != len(set(names)) or set(names) != expected:
            problems.append("Manifest must enumerate every package file exactly once, excluding itself")
        for row in manifest:
            content = source["files"].get(row["file"])
            if content is None or sha(content) != row["sha256"] or str(len(content)) != row["bytes"]:
                problems.append(row["file"])
        missing = set(FILES.values()) - set(source["files"])
        problems.extend(sorted(missing))
    except (KeyError, ValueError, UnicodeError) as error:
        problems.append(str(error))
    gates = [check("SOURCE_R3C1_MANIFEST_VALID", problems, "Every ZIP member payload and byte size checked against complete source manifest")]
    try:
        rows = source_rows(source, "gates")
        ids = [r["gate_id"] for r in rows]
        issues = [r for r in rows if r.get("status") != "PASS"]
        if not ids or len(ids) != len(set(ids)) or any(not k for k in ids):
            issues.append("Empty/duplicate source gates")
        if metadata(source).get("gate_count") != len(rows):
            issues.append("Source metadata gate count differs from recorded gates")
    except (KeyError, ValueError, UnicodeError) as error:
        issues = [str(error)]
    gates.append(check("SOURCE_R3C1_GATES_ALL_PASS", issues, "All recorded source gates must be nonempty, unique and PASS"))
    try:
        meta = metadata(source)
        issues = [] if meta.get("version") == "R3c.1" and meta.get("exit_code") == 0 and not meta.get("gate_failures") else [meta.get("version"), meta.get("exit_code"), meta.get("gate_failures")]
    except (KeyError, ValueError, UnicodeError) as error:
        issues = [str(error)]
    gates.append(check("SOURCE_R3C1_VERSION_VALID", issues, "Source metadata identifies a successful R3c.1 result"))
    try:
        cases = source_rows(source, "cases")
        ids = [r["case_id"] for r in cases]
        issues = [] if len(cases) == 30 and len(set(ids)) == 30 and all(ids) else [f"rows={len(cases)}, unique={len(set(ids))}"]
    except (KeyError, ValueError, UnicodeError) as error:
        issues = [str(error)]
    gates.append(check("SOURCE_CASE_COUNT_VALID", issues, "Exactly 30 distinct source cases before derivation"))
    return gates


def read_source(path):
    path = Path(path)
    # Hash and parse the same byte stream to avoid archive identity races.
    blob = path.read_bytes()
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        info = [i for i in archive.infolist() if not i.is_dir()]
        names = [i.filename for i in info]
        if len(names) != len(set(names)):
            raise ValidationError("Duplicate ZIP member paths")
        for name in names:
            p = PurePosixPath(name)
            if p.is_absolute() or ".." in p.parts or "\\" in name or ":" in name:
                raise ValidationError(f"Unsafe/noncanonical ZIP member path: {name}")
        manifests = [n for n in names if PurePosixPath(n).name == FILES["manifest"]]
        if len(manifests) != 1:
            raise ValidationError("Expected exactly one source manifest")
        prefix = manifests[0][:-len(FILES["manifest"])]
        if any(not n.startswith(prefix) for n in names):
            raise ValidationError("ZIP contains files outside the result package")
        files = {n[len(prefix):]: archive.read(n) for n in names}
    source = {"zip_name": path.name, "zip_sha256": sha(blob), "prefix": prefix, "files": files}
    gates = preflight_gates(source)
    failed = [g["gate_id"] for g in gates if g["status"] != "PASS"]
    if failed:
        raise ValidationError("Source preflight failed: " + ", ".join(failed), gates)
    return source


def require_fields(source, key, required):
    fields, rows = csv_read(source["files"][FILES[key]], FILES[key])
    missing = set(required) - set(fields)
    if missing:
        raise ValidationError(f"{FILES[key]}: missing required columns {sorted(missing)}")
    return fields, rows


def unique(rows, field, label):
    ids = [r[field] for r in rows]
    if any(not v for v in ids) or len(ids) != len(set(ids)):
        raise ValidationError(f"Blank/duplicate {label}: {field}")
    return {r[field]: r for r in rows}


def located_rows(source, key, identity=None):
    """Retain each raw row, including duplicate relation records, with a locator."""
    result, seen = [], Counter()
    for number, row in enumerate(source_rows(source, key), 1):
        if {"r3c1_source_file", "r3c1_data_row", "raw_relation_id"} & set(row):
            raise ValidationError(f"Source row collides with derived locator columns: {FILES[key]}")
        r = {**row, "r3c1_source_file": source["prefix"] + FILES[key], "r3c1_data_row": number}
        if identity:
            fingerprint = sha(canonical(row).encode("utf-8"))
            seen[fingerprint] += 1
            r[identity] = f"RAWREL:{fingerprint}:{seen[fingerprint]}"
        result.append(r)
    return sorted(result, key=lambda r: (r.get("case_id", ""), canonical({k: v for k, v in r.items() if k != "r3c1_data_row"})))


def summaries_for(source, cases):
    units = unique(source_rows(source, "units"), "unit_id", "population")
    positions = {r["unit_id"]: i for i, r in enumerate(source_rows(source, "units"), 1)}
    panels = defaultdict(set)
    for r in source_rows(source, "boundary"):
        panels[r["case_id"]].add(r["unit_id"])
    result = {}
    for case in cases:
        ids = [case["unit_id"]] if case["unit_id"] else sorted(panels[case["case_id"]])
        summary = []
        for uid in ids:
            if uid not in units:
                raise ValidationError(f"Unknown source unit: {uid}")
            row = units[uid]
            fields = BUNDLE_SUMMARY if row["unit_type"] == BUNDLE else SINGLETON_SUMMARY
            if row["unit_type"] not in {BUNDLE, SINGLETON} or any(f not in row for f in fields):
                raise ValidationError(f"Unsupported/incomplete source unit: {uid}")
            summary.append({**{f: row[f] for f in fields},
                "r3c1_source_file": source["prefix"] + FILES["units"], "r3c1_data_row": positions[uid]})
        result[case["case_id"]] = summary
    return result


def compact_relations(raw):
    groups = defaultdict(list)
    for row in raw:
        # Relation grouping is scoped to one case and one target unit. Boundary
        # panels can contain multiple targets with the same related unit.
        groups[row["case_id"], row["unit_id"], row["relation_kind"], row["related_unit_id"]].append(row)
    result = []
    for (cid, uid, kind, related), rows in sorted(groups.items()):
        paths = sorted({r["ancestry"] for r in rows if r["ancestry"]})
        result.append({"case_id": cid, "unit_id": uid, "relation_kind": kind, "related_unit_id": related,
            "source_record_count": len(rows), "source_ids": sorted({r["source_id"] for r in rows}),
            "raw_relation_ids": sorted(r["raw_relation_id"] for r in rows),
            "transitions": sorted({r["transition"] for r in rows if r["transition"]}),
            "ancestry_paths": [json.loads(p) for p in paths]})
    return result


def build_model(source):
    gates = preflight_gates(source)
    if any(g["status"] != "PASS" for g in gates):
        raise ValidationError("Source preflight failed", gates)
    case_fields, cases = require_fields(source, "cases", ("case_id", "case_type", "unit_id", "unit_type", "boundary_ref", "context_id") + REVIEW_FIELDS)
    for key in ("evidence", "boundary"):
        require_fields(source, key, EVIDENCE_FIELDS)
    require_fields(source, "relations", RELATION_FIELDS)
    require_fields(source, "contexts", CONTEXT_FIELDS)
    require_fields(source, "overlay", ("case_id", "relation_id", "relation_layer", "coverage", "relation", "short_bundle_id", "long_bundle_id", "source_id"))
    require_fields(source, "provenance", ("object_id", "source_id", "source_row_json"))
    contexts = unique(source_rows(source, "contexts"), "context_id", "contexts")
    for context in contexts.values():
        for key in ("clauses", "sentences"):
            if not isinstance(json.loads(context[key]), list):
                raise ValidationError(f"{context['context_id']}: {key} must be a JSON list")
    model = {"source": source, "case_fields": case_fields, "cases": copy.deepcopy(cases),
        "summaries": summaries_for(source, cases), "evidence": located_rows(source, "evidence"),
        "boundary": located_rows(source, "boundary"), "raw_relations": located_rows(source, "relations", "raw_relation_id"),
        "overlay": located_rows(source, "overlay"), "contexts": contexts}
    model["compact_relations"] = compact_relations(model["raw_relations"])
    model["packet"] = render_packet(model)
    model["metrics"] = packet_metrics(model, model["packet"])
    return model


def text(value):
    # Prevent source surfaces from becoming Markdown headings, HTML or trace markers.
    s = html.escape(str(value), quote=False).replace("`", "&#96;")
    return s.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")


def evidence_marker(row):
    return canonical({k: row[k] for k in ("case_id", "unit_id", "evidence_id", "context_id")})


def render_packet(model):
    lines = [f"# MILAL {VERSION} — Lossless Compact Review Presentation", "",
        "Exact frozen R3c.1 cases and target identities. No sampling, truncation or interpretation labels.",
        "Full clause/sentence details: 04_context_detail_inventory.csv. Raw relations: 06_raw_relation_index.csv.",
        "Provenance and unselected population remain resolvable in the SHA256-identified source ZIP (90_run_metadata.json).",
        "Extension is overlay-only; exemplar coverage is not exhaustive. Review time is diagnostic only.", ""]
    by_case = defaultdict(list)
    for row in model["evidence"] + model["boundary"]:
        by_case[row["case_id"]].append(row)
    for case in model["cases"]:
        cid = case["case_id"]
        lines.extend([f"## {cid} — {case['case_type']}", "",
            f"- Review target: `{text(case['unit_id'])}`" if case["unit_id"] else f"- Full boundary control panel: {text(case['boundary_ref'])}",
            "", "### Target summary", ""])
        summaries = model["summaries"].get(cid, [])
        for u in summaries:
            lines.append(f"- **{text(u['unit_type'])} `{text(u['unit_id'])}`**; lineage `{text(u['lineage_id'])}`; navigation `{text(u['review_container_id'])}`.")
            if u["unit_type"] == BUNDLE:
                ancestry = json.loads(u["ancestry"])
                lines.extend([f"  - Parent `{text(u['parent_bundle_id'])}`; ancestry: {text(' → '.join(ancestry))}; depth {u['refinement_depth']}; sequence length {u['sequence_length']}.",
                    f"  - Occurrences {u['occurrence_count']}; direct repeated children {u['direct_repeated_child_count']}; explicit singleton branches {u['explicit_singleton_branch_count']}.",
                    f"  - Exemplar {text(u['exemplar_ref_start'])}–{text(u['exemplar_ref_end'])}: {text(u['exemplar_surface_text'])}"])
            else:
                lines.append(f"  - {text(u['outcome_kind'])}; {text(u['link_status'])}; exact source surface: {text(u['surface_text'])}")
        lines.extend(["", "### Compact structural relations", ""])
        for r in model["compact_relations"]:
            if r["case_id"] == cid:
                paths = " | ".join(" → ".join(path) for path in r["ancestry_paths"])
                lines.append(f"- `{text(r['unit_id'])}` — {r['relation_kind']} → `{text(r['related_unit_id'])}`; source records {r['source_record_count']}; transitions {text(' | '.join(r['transitions'])) or '—'}; paths {text(paths) or '—'}.")
        lines.extend(["", "### Compact occurrence/context index", ""])
        groups = defaultdict(list)
        for r in by_case[cid]:
            groups[r["context_id"]].append(r)
        if case["context_id"]:
            groups.setdefault(case["context_id"], [])
        for context_id, rows in sorted(groups.items()):
            c = model["contexts"].get(context_id)
            if c is None:
                lines.append(f"- Missing context `{text(context_id)}` (validation failure)")
                continue
            lines.extend([f"#### Context `{text(context_id)}`", "",
                f"- Span {text(c['ref_start'])}–{text(c['ref_end'])}; {text(c['resolution_status'])}; overlapping clauses {len(json.loads(c['clauses']))}; sentences {len(json.loads(c['sentences']))}."])
            for r in sorted(rows, key=lambda r: (r["unit_id"], r["evidence_id"], r["surface_text"])):
                lines.append(f"- Evidence `{text(r['evidence_id'])}` · unit `{text(r['unit_id'])}` · exact surface: {text(r['surface_text'])} <!-- evidence:{evidence_marker(r)} -->")
            lines.extend([f"- Previous {text(c['prev_ref']) or '[book start]'}: {text(c['prev_text'])}",
                f"- Complete span: {text(c['span_text'])}",
                f"- Next {text(c['next_ref']) or '[book end]'}: {text(c['next_text'])}", ""])
        overlays = [r for r in model["overlay"] if r["case_id"] == cid]
        coverage = dict(sorted(Counter(r["coverage"] for r in overlays).items()))
        # Direction is the literal source short-bundle -> long-bundle orientation,
        # not a new inference about the target's function.
        directions = dict(sorted(Counter(f"{r['short_bundle_id']} → {r['long_bundle_id']}" for r in overlays).items()))
        bundles = sorted({r[k] for r in overlays for k in ("short_bundle_id", "long_bundle_id")})
        lines.extend(["### Sequence-extension overlay summary", "",
            f"- Overlay rows: {len(overlays)}; coverage categories: {text(canonical(coverage))}.",
            f"- Relation-direction counts (short → long): {text(canonical(directions))}.",
            f"- Involved bundles: {text(', '.join(bundles)) or 'none established'}.",
            "- Every raw row is in 08_sequence_extension_overlay.csv; no exhaustive boundary-extension claim.",
            "", "### Human review", ""])
        lines.extend(f"- {field}: {case[field]}" for field in REVIEW_FIELDS)
        lines.append("")
    return "\n".join(lines) + "\n"


def packet_sections(packet):
    starts = list(re.finditer(r"^## (\S+) — [^\n]+\n", packet, re.M))
    return [(match[1], packet[match.start():starts[i + 1].start() if i + 1 < len(starts) else len(packet)])
            for i, match in enumerate(starts)]


def packet_metrics(model, packet):
    sections = dict(packet_sections(packet))
    result = []
    for case in model["cases"]:
        cid = case["case_id"]
        rows = [r for r in model["evidence"] + model["boundary"] if r["case_id"] == cid]
        ids = {r["context_id"] for r in rows}
        if case["context_id"]:
            ids.add(case["context_id"])
        block = sections.get(cid, "")
        result.append({"case_id": cid, "case_type": case["case_type"], "source_evidence_rows": len(rows),
            "unique_context_count": len(ids), "raw_relation_rows": sum(r["case_id"] == cid for r in model["raw_relations"]),
            "compact_relation_rows": sum(r["case_id"] == cid for r in model["compact_relations"]),
            "extension_rows": sum(r["case_id"] == cid for r in model["overlay"]),
            "packet_line_count": len(block.splitlines()), "packet_byte_count": len(block.encode("utf-8"))})
    return result


def original_rows(source, key, rows):
    fields, _ = csv_read(source["files"][FILES[key]], FILES[key])
    return [{f: r.get(f) for f in fields} for r in rows]


def provenance_problems(model):
    source = model["source"]
    units = unique(source_rows(source, "units"), "unit_id", "population")
    provenance = {(r["object_id"], r["source_id"]) for r in source_rows(source, "provenance")}
    cases = {r["case_id"]: r for r in model["cases"]}
    issues = []
    for r in model["evidence"] + model["boundary"]:
        if r["case_id"] not in cases or r["unit_id"] not in units or (r["unit_id"], r["source_id"]) not in provenance:
            issues.append(r["evidence_id"])
    for r in model["raw_relations"]:
        if r["case_id"] not in cases or any(r[k] not in units for k in ("unit_id", "related_unit_id")) or not any((r[k], r["source_id"]) in provenance for k in ("unit_id", "related_unit_id")):
            issues.append(r["raw_relation_id"])
    for r in model["overlay"]:
        if r["case_id"] not in cases or (r["relation_id"], r["source_id"]) not in provenance:
            issues.append(r["relation_id"])
    for case in model["cases"]:
        if case["unit_id"] and case["unit_id"] not in units:
            issues.append(case["case_id"])
    # Locators must recover the complete unmodified source row, not merely an ID.
    for key, rows in (("evidence", model["evidence"]), ("boundary", model["boundary"]),
                      ("relations", model["raw_relations"]), ("overlay", model["overlay"])):
        originals = source_rows(source, key)
        fields, _ = csv_read(source["files"][FILES[key]], FILES[key])
        for row in rows:
            index = row.get("r3c1_data_row", 0)
            if (not isinstance(index, int) or not 1 <= index <= len(originals) or
                    row.get("r3c1_source_file") != source["prefix"] + FILES[key] or
                    {f: row.get(f) for f in fields} != originals[index - 1]):
                issues.append(f"Invalid {key} source locator: {index}")
    return issues


def build_gates(model):
    source, cases = model["source"], model["cases"]
    gates = preflight_gates(source)
    def add(name, problems, detail):
        gates.append(check(name, problems, detail))
    def compare(name, expected, actual, detail):
        a, b = row_bag(expected), row_bag(actual)
        add(name, [] if a == b else [{"missing": sum((a - b).values()), "unexpected": sum((b - a).values())}], detail)
    expected_cases = source_rows(source, "cases")
    compare("SOURCE_CASE_SET_PRESERVED", expected_cases, cases, "Every source case row preserved, including selection/configuration fields")
    order = [r["case_id"] for r in expected_cases]
    actual_order = [r.get("case_id") for r in cases]
    add("SOURCE_CASE_ORDER_PRESERVED", [] if order == actual_order else [actual_order], "Source case order preserved verbatim")
    target_fields = ("case_id", "case_type", "unit_id", "unit_type", "boundary_ref")
    compare("REVIEW_TARGET_IDS_UNCHANGED", [{k: r[k] for k in target_fields} for r in expected_cases],
            [{k: r.get(k) for k in target_fields} for r in cases], "Same analytical targets and boundary panels; no resampling")
    expected_evidence = source_rows(source, "evidence")
    expected_ids = {(r["case_id"], r["evidence_id"]) for r in expected_evidence}
    actual_ids = {(r["case_id"], r["evidence_id"]) for r in model["evidence"]}
    add("ALL_EVIDENCE_IDS_PRESERVED", sorted(expected_ids ^ actual_ids), "Every source target evidence ID retained in its case")
    compare("NO_EVIDENCE_DUPLICATION_OR_LOSS", expected_evidence, original_rows(source, "evidence", model["evidence"]),
            "Complete target row multisets, not just ID sets or counts")
    requested = {r["context_id"] for r in model["evidence"] + model["boundary"]} | {c["context_id"] for c in cases if c["context_id"]}
    add("ALL_CONTEXT_REFERENCES_RESOLVE", [key for key in sorted(requested) if
        model["contexts"].get(key, {}).get("resolution_status") != "RESOLVED" or model["contexts"].get(key, {}).get("context_id") != key],
        "Every target and panel context ID resolves without BHSA recomputation")
    compare("CONTEXT_DETAIL_LOSSLESS", source_rows(source, "contexts"), list(model["contexts"].values()),
            "Every source context field and full clause/sentence JSON cell preserved exactly")
    compare("RAW_RELATION_ROWS_PRESERVED", source_rows(source, "relations"), original_rows(source, "relations", model["raw_relations"]),
            "Every raw structural relation retained, with multiplicity")
    compare("COMPACT_RELATIONS_TRACE_TO_RAW", compact_relations(model["raw_relations"]), model["compact_relations"],
            "Per-case/per-target kind+related-unit grouping retains raw row IDs, transitions and all paths")
    compare("BOUNDARY_EVIDENCE_PRESERVED", source_rows(source, "boundary"), original_rows(source, "boundary", model["boundary"]),
            "All six panels' raw evidence and object identities remain auditable")
    compare("EXTENSION_ROWS_PRESERVED", source_rows(source, "overlay"), original_rows(source, "overlay", model["overlay"]),
            "Every overlay record, endpoint, coverage and case attachment retained")
    core = cases + model["evidence"] + model["boundary"] + model["raw_relations"] + model["compact_relations"] + [u for rows in model["summaries"].values() for u in rows]
    extension_fields = {"relation", "relation_id", "relation_layer", "short_bundle_id", "long_bundle_id"}
    issues = [r.get("unit_id", r.get("case_id")) for r in core if extension_fields & set(r) or r.get("unit_type") == OVERLAY]
    issues.extend(r["relation_id"] for r in model["overlay"] if r["relation_layer"] != OVERLAY or r["coverage"] not in {"EXEMPLAR_ONLY", "UNRESOLVED"})
    add("EXTENSION_REMAINS_OVERLAY_ONLY", issues, "No extension records become core evidence or units; coverage never upgraded")
    defaults = {f: "UNREVIEWED" if f == "review_status" else "" for f in REVIEW_FIELDS}
    add("REVIEW_FIELDS_BLANK_EXCEPT_STATUS", [c["case_id"] for c in cases if {f: c.get(f) for f in REVIEW_FIELDS} != defaults] +
        [r.get("unit_id") for r in core[len(cases):] + model["overlay"] if set(REVIEW_FIELDS) & set(r)],
        "Canonical review forms exist only on cases and start with blank judgments")
    semantic = re.compile(r"function|rhetoric|discourse|theolog|semantic|speaker|macro", re.I)
    def forbidden(value):
        if isinstance(value, dict):
            return [k for k in value if semantic.search(k)] + [k for v in value.values() for k in forbidden(v)]
        if isinstance(value, list):
            return [k for v in value for k in forbidden(v)]
        return []
    add("NO_AUTOMATIC_FUNCTION_LABELS", forbidden(core + model["overlay"] + list(model["contexts"].values())),
        "No interpretation-label fields introduced in generated views")
    control = metadata(source)["pilot_config"]["singleton_control"]["review_item_id"]
    uid = "G6:" + control
    expected_control_cases = [r for r in expected_cases if r["unit_id"] == uid and r["case_type"] == "SINGLETON_OUTCOME"]
    actual_control_cases = [r for r in cases if r["unit_id"] == uid and r["case_type"] == "SINGLETON_OUTCOME"]
    expected_control_evidence = [r for r in expected_evidence if r["unit_id"] == uid]
    actual_control_evidence = [r for r in original_rows(source, "evidence", model["evidence"]) if r["unit_id"] == uid]
    valid_control = (len(expected_control_cases) == len(actual_control_cases) == 1 and bool(expected_control_evidence) and
                     row_bag(expected_control_evidence) == row_bag(actual_control_evidence))
    if metadata(source)["pilot_config"]["book"] == "Job":
        valid_control = valid_control and control == "S02135"
    add("S02135_PRESERVED", [] if valid_control else [uid], "Configured singleton control (Job: S02135) remains independently reviewable with every source span")
    expected_traces = [evidence_marker(r) for r in model["evidence"] + model["boundary"]]
    actual_traces, trace_issues = [], []
    for cid, section in packet_sections(model["packet"]):
        for line in section.splitlines():
            if "<!-- evidence:" not in line:
                continue
            match = re.search(r"<!-- evidence:(\{.*\}) -->$", line)
            try:
                r = json.loads(match[1]) if match else {}
                if (r.get("case_id") != cid or not line.startswith(f"- Evidence `{text(r['evidence_id'])}` · unit `{text(r['unit_id'])}`")):
                    trace_issues.append(line)
                actual_traces.append(canonical(r))
            except (KeyError, ValueError):
                trace_issues.append(line)
    if Counter(expected_traces) != Counter(actual_traces):
        trace_issues.append("Rendered evidence ID/case/unit/context multiset differs")
    # Comparing the actual packet with the deterministic renderer catches changed
    # surfaces, counts, summaries or context prose as well as missing trace entries.
    if model["packet"] != render_packet(model):
        trace_issues.append("Packet text differs from its complete evidence/context index")
    add("PACKET_INDEX_COVERS_ALL_TARGET_EVIDENCE", trace_issues, "Actual visible evidence IDs and context grouping checked in rendered packet")
    expected_metrics = packet_metrics(model, model["packet"])
    metric_issues = [] if model["metrics"] == expected_metrics else ["Metrics differ from actual case sections"]
    if [cid for cid, section in packet_sections(model["packet"])] != actual_order:
        metric_issues.append("Packet case order/set differs")
    add("PACKET_METRICS_MATCH_RENDERED_PACKET", metric_issues, "UTF-8 bytes and lines counted from exact LF-encoded case blocks; no length thresholds")
    add("SOURCE_REFERENCES_RESOLVE", provenance_problems(model), "Evidence/relations/overlays resolve to archived population/provenance and exact data-row locators")
    compare("TARGET_SUMMARIES_PRESERVED", [{"case_id": k, "summaries": v} for k, v in summaries_for(source, cases).items()],
            [{"case_id": k, "summaries": v} for k, v in model["summaries"].items()],
            "Only selected/panel unit summary projections copied, exactly matching source population")
    return gates


METHOD_NOTE = """# MILAL R3c.2 — Lossless Compact Review Presentation

This package derives presentation only from a verified frozen R3c.1 result ZIP.
It does not rerun BHSA, rebuild earlier analytical layers, resample, split units,
cluster by meaning, truncate, or remove evidence. Keep the identified source ZIP:
its SHA256, member paths and data-row locators resolve full population/provenance
without unnecessarily duplicating them here. Manifest verification establishes
integrity relative to that source manifest, not third-party authentication.

The exact 30 cases, order, target IDs, selection reasons, seed and review fields
are retained. Only review_status starts UNREVIEWED. No semantic/function labels
or total review-hour estimates are generated.

Every target evidence row appears in 03_compact_evidence_index.csv; every boundary
evidence row in 07_boundary_evidence_index.csv. Identity preservation compares
full row multisets scoped by case: the same evidence can legitimately occur in
multiple panels. Original CSV values are retained, with source member/data-row
locators added. No occurrence is dropped merely because contexts are shared.

Contexts are displayed once per case/context_id, across target units in boundary
panels. Every evidence ID, target unit and exact surface is listed under that
context. Full covering verses/neighbors remain inline; clause/sentence counts
replace repeated inventories. 04_context_detail_inventory.csv retains all source
context fields and complete JSON cells, keyed by context_id, without alteration.
HTML evidence comments provide a machine-checkable trace beside each visible ID.

Relation display grouping is scoped to case_id and target unit_id, then uses
relation_kind + related_unit_id. This prevents a boundary panel from merging
relations belonging to different analytical targets. Every raw row has its own
raw_relation_id and source locator in 06_raw_relation_index.csv. Display rows
retain all raw IDs, transitions, paths and source IDs; event/G6 provenance rows
can share one display row without losing either record.

Overlay records remain separate in 08_sequence_extension_overlay.csv. Main
packet summaries show row counts, original coverage categories, literal directed
endpoint-pair counts (short bundle -> long bundle), and involved bundles. These
counts are structural presentation diagnostics, not functional interpretation.
Coverage remains EXEMPLAR_ONLY or UNRESOLVED, never upgraded or exhaustive.

Case metrics count exact UTF-8 bytes and lines in each rendered case block,
including its heading and trailing blank line. The shared packet preamble is
excluded from per-case metrics and included in whole-packet metadata. No gate
uses packet length as an acceptance threshold or a semantic score.

Rendering sorts evidence contexts/IDs and relation keys deterministically, but
preserves source case order. Reordering other source rows changes archive hashes
and data-row locators as it must; it does not change human packet content.
The source ZIP hash is in metadata/inventory rather than repeated in packet prose.

Development acceptance is synthetic. Real R3c.1 ZIP processing and R4 work are
outside this task; a later authorized real-data presentation run needs inspection.
"""


def write_csv(path, rows, fields=None):
    rows = list(rows)
    fields = list(fields) if fields is not None else sorted({k for row in rows for k in row})
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n", extrasaction="raise")
    writer.writeheader()
    writer.writerows({k: canonical(v) if isinstance(v, (dict, list, tuple)) else v for k, v in r.items()} for r in rows)
    Path(path).write_bytes(stream.getvalue().encode("utf-8-sig"))


def write_manifest(out):
    rows = [{"file": p.name, "bytes": p.stat().st_size, "sha256": sha(p.read_bytes())}
            for p in sorted(out.iterdir()) if p.is_file() and p.name != "99_manifest_sha256.csv"]
    write_csv(out / "99_manifest_sha256.csv", rows, ("file", "bytes", "sha256"))


def write_outputs(model, out, *, create=True):
    out = Path(out)
    # Exclusive directory creation is part of the public no-overwrite contract.
    if create:
        out.mkdir(parents=True, exist_ok=False)
    source = model["source"]
    inventory = []
    for name, data in sorted(source["files"].items()):
        row_count, columns = "", []
        if name.endswith(".csv"):
            columns, rows = csv_read(data, name)
            row_count = len(rows)
        inventory.append({"source_zip": source["zip_name"], "source_zip_sha256": source["zip_sha256"],
            "source_file": source["prefix"] + name, "bytes": len(data), "sha256": sha(data),
            "row_count": row_count, "columns": columns})
    gates = build_gates(model)
    # Only small target summary projections are embedded once per case. No full
    # population or global provenance table is copied to the derived package.
    cases = [{**r, "target_summaries": model["summaries"][r["case_id"]]} for r in model["cases"]]
    for name, rows, fields in (
        ("01_source_r3c1_inventory.csv", inventory, None),
        ("02_review_cases.csv", cases, model["case_fields"] + ["target_summaries"]),
        ("03_compact_evidence_index.csv", model["evidence"], csv_read(source["files"][FILES["evidence"]], FILES["evidence"])[0] + ["r3c1_source_file", "r3c1_data_row"]),
        ("04_context_detail_inventory.csv", [model["contexts"][k] for k in sorted(model["contexts"])], None),
        ("05_compact_relation_index.csv", model["compact_relations"],
         ("case_id", "unit_id", "relation_kind", "related_unit_id", "source_record_count", "source_ids", "raw_relation_ids", "transitions", "ancestry_paths")),
        ("06_raw_relation_index.csv", model["raw_relations"], csv_read(source["files"][FILES["relations"]], FILES["relations"])[0] + ["r3c1_source_file", "r3c1_data_row", "raw_relation_id"]),
        ("07_boundary_evidence_index.csv", model["boundary"], csv_read(source["files"][FILES["boundary"]], FILES["boundary"])[0] + ["r3c1_source_file", "r3c1_data_row"]),
        ("08_sequence_extension_overlay.csv", model["overlay"], csv_read(source["files"][FILES["overlay"]], FILES["overlay"])[0] + ["r3c1_source_file", "r3c1_data_row"]),
        ("10_packet_metrics.csv", model["metrics"], None),
        ("11_gates.csv", gates, ("gate_id", "status", "detail", "violations")),
    ):
        write_csv(out / name, rows, fields)
    (out / "09_review_packet_compact.md").write_bytes(model["packet"].encode("utf-8"))
    (out / "12_method_note.md").write_bytes(METHOD_NOTE.encode("utf-8"))
    failures = [g["gate_id"] for g in gates if g["status"] != "PASS"]
    meta = {"version": VERSION, "source_r3c1_zip": source["zip_name"], "source_r3c1_zip_sha256": source["zip_sha256"],
        "source_r3c1_metadata": metadata(source), "created_utc": datetime.now(timezone.utc).isoformat(),
        "case_count": len(model["cases"]), "target_evidence_rows": len(model["evidence"]),
        "boundary_evidence_rows": len(model["boundary"]), "context_count": len(model["contexts"]),
        "raw_relation_rows": len(model["raw_relations"]), "compact_relation_rows": len(model["compact_relations"]),
        "extension_rows": len(model["overlay"]), "gate_count": len(gates), "gate_failures": failures,
        "packet_line_count": len(model["packet"].splitlines()), "packet_byte_count": len(model["packet"].encode("utf-8")),
        "acceptance_scope": "PRESENTATION_VALIDATION_ONLY; human inspection required", "exit_code": 2 if failures else 0}
    (out / "90_run_metadata.json").write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    write_manifest(out)
    return meta["exit_code"]


def synthetic_source(root):
    """Generate a source result through the frozen R3c.1 writer, only for tests."""
    import milal_r3c_1_review_units as prior
    tables, config, provider = prior.synthetic_fixture()
    # Exercise the literal S02135 ID in a clearly synthetic, non-Job corpus.
    for table in tables.values():
        for row in table.rows:
            for key in ("review_item_id", "mapped_g6_singleton_review_item_id"):
                if row.get(key) == "S00001":
                    row[key] = "S02135"
    config["singleton_control"]["review_item_id"] = "S02135"
    model = prior.build_model(tables, config, provider)
    folder = Path(root) / "r3c1_synthetic_source"
    if prior.write_outputs(model, folder, {"run_kind": "SYNTHETIC_SELF_TEST"}) != 0:
        raise ValidationError("Synthetic R3c.1 source failed validation")
    target = Path(root) / "r3c1_synthetic_source.zip"
    with zipfile.ZipFile(target, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(folder.iterdir()):
            archive.write(path, folder.name + "/" + path.name)
    return target


def self_test(output_dir=None):
    if output_dir and Path(output_dir).exists():
        raise ValidationError(f"Existing output preserved: {output_dir}")
    with tempfile.TemporaryDirectory(prefix="milal_r3c2_") as tmp:
        root = Path(tmp)
        source_zip = synthetic_source(root)
        if output_dir:
            # Retain the synthetic frozen archive outside the derived manifest tree,
            # so the retained demo's provenance locators remain usable after testing.
            retained = Path(str(output_dir) + "_source_r3c1.zip")
            retained.parent.mkdir(parents=True, exist_ok=True)
            with retained.open("xb") as stream:
                stream.write(source_zip.read_bytes())
            source_zip = retained
        model = build_model(read_source(source_zip))
        gates = build_gates(model)
        assert all(g["status"] == "PASS" for g in gates), gates
        assert any(r["source_record_count"] > 1 for r in model["compact_relations"])
        assert len(model["cases"]) == 30
        assert any(r["unit_id"] == "G6:S02135" for r in model["cases"])
        changed = copy.deepcopy(model)
        changed["evidence"].pop()
        assert next(g for g in build_gates(changed) if g["gate_id"] == "NO_EVIDENCE_DUPLICATION_OR_LOSS")["status"] == "FAIL"
        out = Path(output_dir) if output_dir else root / "compact"
        assert write_outputs(model, out) == 0
        print(f"SELF-TEST PASS: {len(gates)} computed gates; 30 frozen cases; {len(model['evidence'])} target evidence rows; {len(model['boundary'])} boundary rows.")
        print(f"Compact packet: {len(model['packet'].splitlines())} lines / {len(model['packet'].encode('utf-8'))} bytes.")
        if output_dir:
            print(f"Synthetic compact packet retained: {out.resolve()}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="MILAL R3c.2 presentation over a frozen R3c.1 result ZIP")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--r3c1-zip", type=Path)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test(args.output_dir)
    if args.r3c1_zip is None or args.output_dir is None:
        parser.error("--r3c1-zip and --output-dir are required")
    out = args.output_dir.expanduser().resolve()
    try:
        out.mkdir(parents=True, exist_ok=False)
    except OSError as error:
        print(f"ERROR: cannot exclusively create output (existing paths preserved): {out}: {error}", file=sys.stderr)
        return 2
    try:
        source = read_source(args.r3c1_zip)
        model = build_model(source)
        status = write_outputs(model, out, create=False)
    except (ValidationError, OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
        # Failure diagnostics are new outputs only, never updates to prior runs.
        message = f"{type(error).__name__}: {error}"
        (out / "00_FATAL_ERROR.txt").write_bytes((message + "\n").encode("utf-8"))
        gates = getattr(error, "gates", []) or [check("SOURCE_OR_PRESENTATION_VALIDATION", [message], "Explicit schema/integrity failure")]
        write_csv(out / "11_gates.csv", gates, ("gate_id", "status", "detail", "violations"))
        meta = {"version": VERSION, "source_r3c1_zip": str(args.r3c1_zip), "error": message, "exit_code": 2}
        if args.r3c1_zip.is_file():
            meta["source_r3c1_zip_sha256"] = sha(args.r3c1_zip.read_bytes())
        (out / "90_run_metadata.json").write_bytes((json.dumps(meta, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
        write_manifest(out)
        print(message, file=sys.stderr)
        return 2
    print(f"MILAL {VERSION}: {'PASS' if status == 0 else 'FAIL'}; output={out}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
