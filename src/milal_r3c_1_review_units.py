#!/usr/bin/env python3
"""R3c.1: existing structural objects as review units; frozen R3c.0.2 helpers."""
from __future__ import annotations

import argparse
import copy
from collections import Counter, defaultdict
from datetime import datetime, timezone
import json
from pathlib import Path
import random
import re
import sys
import tempfile
import unicodedata

import milal_r3c_0_2_reviewability as base

VERSION = "R3c.1"
REVIEW_FIELDS = base.REVIEW_FIELDS
SchemaError, InvariantError = base.SchemaError, base.InvariantError
TFContext = base.TFContext
BUNDLE = "REPEATED_BUNDLE_UNIT"
SINGLETON = "SINGLETON_OUTCOME_UNIT"
CASE_TYPES = ("HIGH_OCCURRENCE_BUNDLE", "LOW_OCCURRENCE_BUNDLE", "RANDOM_BUNDLE",
              "SINGLETON_OUTCOME", "BOUNDARY_CONTROL")
MEMBER_FIELDS = ("occurrence_count", "sequence_length", "levels_present", "lowest_level", "highest_level")
CASE_FIELDS = ("case_id", "case_type", "unit_id", "unit_type", "boundary_ref", "context_id",
               "seed", "selection_reason") + REVIEW_FIELDS
EVIDENCE_FIELDS = ("case_id", "unit_id", "unit_type", "evidence_id", "bundle_id", "lineage_id",
                   "ref_start", "ref_end", "surface_text", "source_id", "context_id")
RELATION_FIELDS = ("case_id", "unit_id", "relation_kind", "related_unit_id", "lineage_id",
                   "ancestry", "transition", "source_id")
OVERLAY_FIELDS = ("case_id", "relation_id", "relation_layer", "coverage", "coverage_note", "relation",
                  "short_bundle_id", "long_bundle_id", "short_lineage_id", "long_lineage_id",
                  "short_exemplar_ref_start", "long_exemplar_ref_start", "source_id")


def validate_config(config):
    config = copy.deepcopy(config)
    if not isinstance(config.get("book"), str) or not config["book"].strip():
        raise SchemaError("Pilot configuration requires a nonblank book")
    if type(config.get("seed")) is not int:
        raise SchemaError("Pilot configuration requires an integer seed")
    refs = config.get("boundary_refs", [])
    config["boundary_refs"] = [base.ref_text(base.reference(r, config["book"])) for r in refs]
    if len(refs) != 6 or len(set(config["boundary_refs"])) != 6:
        raise SchemaError("Exactly six distinct boundary references required")
    if not config.get("singleton_control"):
        raise SchemaError("An explicit singleton_control is required (Job: S02135)")
    return config


def source_population(tables, config):
    """Validate source navigation without using the old container pilot/expansion."""
    base.validate_schemas(tables)
    for field in MEMBER_FIELDS:
        if field not in tables["members"].fields or any(field not in r for r in tables["members"].rows):
            raise SchemaError(f"members: missing required column/value {field}")
    members = base.unique_records(tables["members"].records("bundle_membership"), "bundle_id", "bundle")
    paths = base.ancestry_paths(members)
    workspace = base.unique_records(tables["workspace"].records("navigation_container"), "review_container_id", "container")
    lineages = defaultdict(list)
    for bid, record in members.items():
        r = record["row"]
        if not r["lineage_id"] or r["bundle_id"] != bid:
            raise InvariantError(f"Blank lineage or noncanonical bundle ID: {bid}")
        if base.integer(r["refinement_depth"], "refinement_depth") != len(paths[bid]) - 1:
            raise InvariantError(f"Source depth/parent mismatch: {bid}")
        if base.integer(r["sequence_length"], "sequence_length") < 1:
            raise InvariantError(f"Invalid sequence length: {bid}")
        if any(not r[f].strip() for f in ("levels_present", "lowest_level", "highest_level")):
            raise SchemaError(f"Missing source level information: {bid}")
        base.source_span(record, config["book"], True)
        lineages[r["lineage_id"]].append(bid)
    navigation, orphan_navigation = {}, {}
    for cid, record in sorted(workspace.items()):
        r = record["row"]
        lineage, orphan = r["lineage_id"], r["orphan_singleton_review_item_id"]
        if bool(lineage) == bool(orphan):
            raise InvariantError(f"Container must identify lineage or explicit orphan: {cid}")
        target, key = (navigation, lineage) if lineage else (orphan_navigation, orphan)
        if key in target or (lineage and lineage not in lineages):
            raise InvariantError(f"Missing/duplicate container lineage or orphan: {cid}")
        target[key] = cid
        bundles = lineages.get(lineage, [])
        depth = max((len(paths[b]) - 1 for b in bundles), default=0)
        source_depth = 0 if orphan and r["max_refinement_depth"] == "" else base.integer(r["max_refinement_depth"], "depth")
        if base.integer(r["bundle_count"], "bundle_count") != len(bundles) or source_depth != depth:
            raise InvariantError(f"Container count/depth mismatch: {cid}")
    if set(navigation) != set(lineages):
        raise InvariantError("Navigation omits source lineages")
    for lineage, bids in lineages.items():
        if len({paths[b][0] for b in bids}) != 1:
            raise InvariantError(f"Multiple roots: {lineage}")
    outcomes = base.build_outcomes(tables, members, paths, set(orphan_navigation), config["book"])
    if any("G6:" + oid not in outcomes for oid in orphan_navigation):
        raise InvariantError("Navigation orphan is missing its G6 outcome")
    occurrences = sorted(tables["occurrences"].records("bundle_occurrence"), key=lambda r: r["source_id"])
    by_bundle = defaultdict(list)
    for record in occurrences:
        bid = record["row"]["bundle_id"]
        if bid not in members:
            raise InvariantError(f"Occurrence belongs to unknown bundle: {bid}")
        base.source_span(record, config["book"])
        by_bundle[bid].append(record)
    children, event_counts = defaultdict(list), Counter()
    for bid, record in members.items():
        if record["row"]["parent_bundle_id"]:
            children[record["row"]["parent_bundle_id"]].append(bid)
    for row in tables["events"].rows:
        event_counts[row["parent_bundle_id"]] += 1
    population = []
    for bid, record in sorted(members.items()):
        r = record["row"]
        count = base.integer(r["occurrence_count"], "occurrence_count")
        if count < 1 or count != len(by_bundle[bid]):
            raise InvariantError(f"Source occurrence count mismatch: {bid}: declared={count}; rows={len(by_bundle[bid])}")
        population.append({"unit_id": "BUNDLE:" + bid, "unit_type": BUNDLE, "bundle_id": bid,
            "lineage_id": r["lineage_id"], "review_container_id": navigation[r["lineage_id"]],
            "parent_bundle_id": r["parent_bundle_id"], "ancestry": paths[bid],
            "refinement_depth": len(paths[bid]) - 1, "sequence_length": int(r["sequence_length"]),
            "occurrence_count": count, "direct_repeated_child_count": len(children[bid]),
            "direct_repeated_child_ids": sorted(children[bid]),
            "explicit_singleton_branch_count": event_counts[bid],
            **{f: r[f] for f in ("levels_present", "lowest_level", "highest_level",
                                "exemplar_ref_start", "exemplar_ref_end", "exemplar_surface_text")},
            "source_ids": [record["source_id"]]})
    for oid, outcome in outcomes.items():
        population.append({"unit_id": oid, "unit_type": SINGLETON,
            **{k: copy.deepcopy(v) for k, v in outcome.items() if k not in ("object_id", "object_type", "sources")},
            "review_container_id": navigation.get(outcome["lineage_id"], orphan_navigation.get(outcome["review_item_id"], "")),
            "source_ids": [r["source_id"] for r in outcome["sources"]]})
    return {"members": members, "paths": paths, "workspace": workspace, "outcomes": outcomes,
            "occurrences": occurrences, "by_bundle": by_bundle,
            "population": sorted(population, key=lambda r: r["unit_id"])}


def control_id(outcomes, config):
    control = config["singleton_control"]
    oid = "G6:" + control["review_item_id"]
    if oid not in outcomes:
        raise InvariantError(f"Singleton control missing: {oid}")
    o = outcomes[oid]
    expected = base.span(control["ref_start"], control["ref_end"], config["book"])
    item_ids = {r["source_id"] for r in o["sources"] if r["role"] == "g6_item"}
    if not any(s["source_id"] in item_ids and base.span(s["ref_start"], s["ref_end"], config["book"]) == expected for s in o["spans"]):
        raise InvariantError(f"Singleton control span mismatch: {oid}")
    # Same optional Hebrew control normalization as R3c.0.2; no identity inference.
    def letters(text):
        text = "".join(ch for ch in unicodedata.normalize("NFD", text) if not unicodedata.combining(ch))
        text = re.sub(r"\s+[פס]\s*$", "", text)
        return "".join(ch for ch in text if "א" <= ch <= "ת")
    if control.get("surface_letters") and letters(control["surface_letters"]) != letters(o["surface_text"]):
        raise InvariantError(f"Singleton control surface mismatch: {oid}")
    if o["outcome_kind"] != "MAPPED" or not o["branches"]:
        raise InvariantError(f"Singleton control requires mapped provenance/branches: {oid}")
    return oid


def select_cases(population, outcomes, config):
    bundles = [r for r in population if r["unit_type"] == BUNDLE]
    if len(bundles) < 18 or len(outcomes) < 6:
        raise InvariantError("Insufficient population: need 18 bundles and 6 singleton outcomes")
    measures = ("occurrence_count", "direct_repeated_child_count", "explicit_singleton_branch_count", "refinement_depth")
    high = sorted(bundles, key=lambda r: tuple(-r[k] for k in measures) + (r["bundle_id"],))[:6]
    used = {r["unit_id"] for r in high}
    low = sorted([r for r in bundles if r["unit_id"] not in used],
                 key=lambda r: tuple(r[k] for k in measures) + (r["bundle_id"],))[:6]
    used.update(r["unit_id"] for r in low)
    pool = sorted([r for r in bundles if r["unit_id"] not in used], key=lambda r: r["bundle_id"])
    sampled = random.Random(config["seed"]).sample(pool, 6)
    fixed = control_id(outcomes, config)
    singletons = [fixed] + random.Random(config["seed"]).sample([oid for oid in sorted(outcomes) if oid != fixed], 5)
    cases = []
    def add(kind, uid="", ref="", reason=""):
        cases.append({"case_id": f"CASE{len(cases) + 1:03d}", "case_type": kind, "unit_id": uid,
            "unit_type": BUNDLE if kind in CASE_TYPES[:3] else SINGLETON if kind == CASE_TYPES[3] else "",
            "boundary_ref": ref, "context_id": "", "seed": config["seed"],
            "selection_reason": reason, **base.review_defaults()})
    for kind, rows, reason in ((CASE_TYPES[0], high, "Descending lexicographic source measures"),
                               (CASE_TYPES[1], low, "Ascending lexicographic measures after HIGH exclusion"),
                               (CASE_TYPES[2], sampled, "Seeded sample of ID-sorted remaining bundles")):
        for r in rows:
            add(kind, r["unit_id"], reason=reason)
    for oid in singletons:
        add(CASE_TYPES[3], oid, reason="Fixed singleton control" if oid == fixed else "Separate seeded singleton sample")
    for ref in config["boundary_refs"]:
        add(CASE_TYPES[4], ref=ref, reason="Full boundary control panel; not a population unit")
    return cases


def context_id(book, start, end):
    a, b = base.span(start, end, book)
    return f"{book}:{base.ref_text(a)}..{base.ref_text(b)}"


def evidence_for(cases, source, config):
    targets, boundaries = [], []
    book = config["book"]
    def occurrence(case, record):
        r = record["row"]
        return {"case_id": case["case_id"], "unit_id": "BUNDLE:" + r["bundle_id"],
            "unit_type": BUNDLE, "evidence_id": "OCC:" + record["source_key"],
            "bundle_id": r["bundle_id"], "lineage_id": source["members"][r["bundle_id"]]["row"]["lineage_id"],
            **base.source_span(record, book), "context_id": context_id(book, r["ref_start"], r["ref_end"]) }
    def singleton(case, oid):
        o = source["outcomes"][oid]
        return [{"case_id": case["case_id"], "unit_id": oid, "unit_type": SINGLETON,
            "evidence_id": oid + ":SPAN:" + s["source_id"], "bundle_id": "", "lineage_id": o["lineage_id"],
            **s, "context_id": context_id(book, s["ref_start"], s["ref_end"])} for s in o["spans"]]
    for case in cases:
        if case["case_type"] in CASE_TYPES[:3]:
            targets.extend(occurrence(case, r) for r in source["by_bundle"].get(case["unit_id"].removeprefix("BUNDLE:"), []))
        elif case["case_type"] == CASE_TYPES[3]:
            if case["unit_id"] in source["outcomes"]:
                targets.extend(singleton(case, case["unit_id"]))
        elif case["case_type"] == CASE_TYPES[4]:
            ref = case["boundary_ref"]
            boundaries.extend(occurrence(case, r) for r in source["occurrences"]
                              if base.contains(r["row"]["ref_start"], r["row"]["ref_end"], ref, book))
            for oid, o in source["outcomes"].items():
                if any(base.contains(s["ref_start"], s["ref_end"], ref, book) for s in o["spans"]):
                    boundaries.extend(singleton(case, oid))
    return sorted(targets, key=base.canonical), sorted(boundaries, key=base.canonical)


def relations_for(cases, source, evidence):
    """Immediate neighbors and ancestor references only; no descendant expansion."""
    units = {r["unit_id"]: r for r in source["population"]}
    direct_branches = defaultdict(list)
    for oid, o in source["outcomes"].items():
        for branch in o["branches"]:
            direct_branches[branch["parent_bundle_id"]].append((oid, branch))
    targets = defaultdict(set)
    for row in evidence:
        targets[row["case_id"]].add(row["unit_id"])
    result = []
    for case in cases:
        if case["unit_id"]:
            targets[case["case_id"]].add(case["unit_id"])
        for uid in sorted(targets[case["case_id"]]):
            if uid not in units:
                continue
            unit = units[uid]
            def add(kind, related, sid, ancestry=None, transition=""):
                result.append({"case_id": case["case_id"], "unit_id": uid, "relation_kind": kind,
                    "related_unit_id": related, "lineage_id": unit["lineage_id"],
                    "ancestry": ancestry or [], "transition": transition, "source_id": sid})
            if unit["unit_type"] == BUNDLE:
                sid = unit["source_ids"][0]
                for ancestor in unit["ancestry"][:-1]:
                    add("ANCESTOR", "BUNDLE:" + ancestor, sid, unit["ancestry"])
                if unit["parent_bundle_id"]:
                    add("IMMEDIATE_PARENT", "BUNDLE:" + unit["parent_bundle_id"], sid)
                for child in unit["direct_repeated_child_ids"]:
                    add("DIRECT_REPEATED_CHILD", "BUNDLE:" + child, source["members"][child]["source_id"])
                for oid, branch in direct_branches[unit["bundle_id"]]:
                    add("EXPLICIT_SINGLETON_BRANCH", oid, branch["source_id"], branch["ancestry"], branch["transition"])
            else:
                for branch in source["outcomes"][uid]["branches"]:
                    add("EXPLICIT_PARENT_BRANCH", "BUNDLE:" + branch["parent_bundle_id"],
                        branch["source_id"], branch["ancestry"], branch["transition"])
    return sorted(result, key=base.canonical)


def overlays_for(cases, source, evidence, tables, config):
    incident = defaultdict(set)
    for row in evidence:
        if row["unit_type"] == BUNDLE:
            incident[row["case_id"]].add(row["bundle_id"])
        elif row["unit_id"] in source["outcomes"]:
            incident[row["case_id"]].update(b["parent_bundle_id"] for b in source["outcomes"][row["unit_id"]]["branches"])
    rows = []
    for record in tables["overlay"].records("sequence_extension"):
        r = record["row"]
        for side in ("short", "long"):
            bid = r[side + "_bundle_id"]
            if bid not in source["members"] or source["members"][bid]["row"]["lineage_id"] != r[side + "_lineage_id"]:
                raise InvariantError("Overlay endpoint membership conflict")
        if not r["relation"]:
            raise SchemaError("Blank sequence extension relation")
        refs = [base.ref_text(base.reference(r[s + "_exemplar_ref_start"], config["book"]))
                for s in ("short", "long") if r[s + "_exemplar_ref_start"]]
        coverage = "EXEMPLAR_ONLY" if len(refs) == 2 else "UNRESOLVED"
        endpoints = {r["short_bundle_id"], r["long_bundle_id"]}
        for case in cases:
            related = bool(endpoints & incident[case["case_id"]])
            if case["case_type"] == CASE_TYPES[4]:
                related = case["boundary_ref"] in refs or (coverage == "UNRESOLVED" and related)
            if related:
                rows.append({"case_id": case["case_id"], "relation_id": "EXT:" + record["source_key"],
                    "relation_layer": base.OVERLAY, "coverage": coverage,
                    "coverage_note": "Exemplar starts only; boundary extension coverage is not exhaustive.",
                    **{k: r[k] for k in base.SCHEMAS["overlay"]}, "source_id": record["source_id"]})
    return sorted(rows, key=base.canonical)


def provenance_for(source, evidence, overlay, tables):
    pairs = {}
    def add(oid, r):
        pairs[oid, r["source_id"]] = {"object_id": oid, **{k: v for k, v in r.items() if k != "row"}, "source_row_json": r["row"]}
    for bid, r in source["members"].items():
        add("BUNDLE:" + bid, r)
    for cid, r in source["workspace"].items():
        add("NAV:" + cid, r)
    for oid, o in source["outcomes"].items():
        for r in o["sources"]:
            add(oid, r)
    occurrence_records = {r["source_id"]: r for r in source["occurrences"]}
    for e in evidence:
        if e["source_id"] in occurrence_records:
            add(e["unit_id"], occurrence_records[e["source_id"]])
    overlay_records = {r["source_id"]: r for r in tables["overlay"].records("sequence_extension")}
    for r in overlay:
        if r["source_id"] in overlay_records:
            add(r["relation_id"], overlay_records[r["source_id"]])
    return [pairs[k] for k in sorted(pairs)]


def build_model(tables, config, provider):
    config = validate_config(config)
    if provider.book != config["book"]:
        raise InvariantError("Context provider book differs from configuration")
    source = source_population(tables, config)
    cases = select_cases(source["population"], source["outcomes"], config)
    targets, boundary = evidence_for(cases, source, config)
    relations = relations_for(cases, source, targets + boundary)
    overlays = overlays_for(cases, source, targets + boundary, tables, config)
    contexts = {}
    def attach(start, end):
        cid = context_id(config["book"], start, end)
        if cid not in contexts:
            contexts[cid] = {"context_id": cid, **provider.context(start, end)}
        return cid
    for row in targets + boundary:
        attach(row["ref_start"], row["ref_end"])
    for c in cases:
        if c["boundary_ref"]:
            c["context_id"] = attach(c["boundary_ref"], c["boundary_ref"])
    return {"tables": tables, "config": config, "population": copy.deepcopy(source["population"]),
            "cases": cases, "evidence": targets, "boundary": boundary, "relations": relations,
            "overlay": overlays, "contexts": contexts,
            "provenance": provenance_for(source, targets + boundary, overlays, tables)}


def row_bag(rows):
    return Counter(base.canonical(r) for r in rows)


def build_gates(model):
    """Reconstruct expectations from original source tables, not output counters."""
    gates = []
    def add(name, problems, detail):
        problems = list(problems)
        gates.append({"gate_id": name, "status": "FAIL" if problems else "PASS", "detail": detail, "violations": problems})
    def diff(name, expected, actual, detail):
        a, b = row_bag(expected), row_bag(actual)
        add(name, [] if a == b else [{"missing": sum((a - b).values()), "unexpected": sum((b - a).values())}], detail)
    try:
        source = source_population(model["tables"], model["config"])
    except (SchemaError, InvariantError) as error:
        add("SOURCE_NAVIGATION_AND_COUNTS_VALID", [str(error)], "Source schema, graph, navigation and declared occurrence counts")
        return gates
    add("SOURCE_NAVIGATION_AND_COUNTS_VALID", [], "Revalidated actual source schema, graph, navigation and occurrence counts")
    pop, cases = model["population"], model["cases"]
    expected_pop = {r["unit_id"]: r for r in source["population"]}
    actual_pop = {r.get("unit_id"): r for r in pop}
    ids = [r.get("unit_id") for r in pop]
    diff("REVIEW_UNIT_POPULATION_COMPLETE", [{"id": r["unit_id"], "type": r["unit_type"]} for r in source["population"]],
         [{"id": r.get("unit_id"), "type": r.get("unit_type")} for r in pop], "Every source bundle and canonical singleton exactly once")
    add("REVIEW_UNIT_IDS_UNIQUE", [v for v, n in Counter(ids).items() if not v or n != 1], "Nonblank unique review unit identifiers")
    add("NO_CONTAINER_AS_REVIEW_TARGET", [c["case_id"] for c in cases if
        (c["case_type"] == CASE_TYPES[4] and (c.get("unit_id") or c.get("unit_type"))) or
        (c["case_type"] != CASE_TYPES[4] and (c.get("unit_id") not in expected_pop or
         c.get("unit_type") != expected_pop.get(c.get("unit_id"), {}).get("unit_type")))],
        "Targets are source units; boundary panels have no population unit ID")
    repeated = [r for r in pop if r.get("unit_type") == BUNDLE]
    for name, field in (("REPEATED_UNIT_LINEAGE_MATCHES_SOURCE", "lineage_id"),
                        ("REPEATED_UNIT_PARENT_MATCHES_SOURCE", "parent_bundle_id")):
        add(name, [r["unit_id"] for r in repeated if r.get(field) != expected_pop.get(r["unit_id"], {}).get(field)], "Compared with frozen membership rows")
    diff("REPEATED_METADATA_COMPLETE", [r for r in source["population"] if r["unit_type"] == BUNDLE], repeated,
         "Source levels, counts, ancestry, exemplar and direct child measures preserved")
    expected_targets, expected_boundary = evidence_for(cases, source, model["config"])
    bad_counts = []
    for c in cases:
        if c["case_type"] in CASE_TYPES[:3]:
            rows = [r for r in model["evidence"] if r.get("case_id") == c["case_id"]]
            expected_count = expected_pop.get(c["unit_id"], {}).get("occurrence_count")
            if len(rows) != expected_count or any(r.get("unit_id") != c["unit_id"] for r in rows):
                bad_counts.append(c["case_id"])
    add("ALL_SELECTED_BUNDLE_OCCURRENCES_EMITTED", bad_counts, "Per-target emitted count equals declared and verified source count")
    diff("NO_TARGET_OCCURRENCE_TRUNCATION", [r for r in expected_targets if r["unit_type"] == BUNDLE],
         [r for r in model["evidence"] if r.get("unit_type") == BUNDLE], "Full occurrence identity/payload multisets; catches replacement and wrong bundle")
    diff("SELECTED_SINGLETON_SPANS_COMPLETE", [r for r in expected_targets if r["unit_type"] == SINGLETON],
         [r for r in model["evidence"] if r.get("unit_type") == SINGLETON], "Every selected singleton source span retained")
    required_contexts = {r["context_id"]: (r["ref_start"], r["ref_end"]) for r in expected_targets + expected_boundary}
    for c in cases:
        if c["case_type"] == CASE_TYPES[4]:
            required_contexts[context_id(model["config"]["book"], c["boundary_ref"], c["boundary_ref"])] = (c["boundary_ref"], c["boundary_ref"])
    add("ALL_SELECTED_CONTEXTS_RESOLVED", [cid for cid, (start, end) in required_contexts.items()
        if (ctx := model["contexts"].get(cid, {})).get("resolution_status") != "RESOLVED" or
        ctx.get("ref_start") != start or ctx.get("ref_end") != end or ctx.get("book") != model["config"]["book"] or
        not all(ctx.get(k) for k in ("span_text", "clauses", "sentences"))], "Every required target/boundary span has full resolved context")
    diff("SINGLETON_IDENTITY_FOLDING_VALID", [r for r in source["population"] if r["unit_type"] == SINGLETON],
         [r for r in pop if r.get("unit_type") == SINGLETON], "Recomputed exact R3c.0.2 identity folding, branches, surfaces and spans")
    parent_errors = []
    for r in pop:
        if r.get("unit_type") != SINGLETON:
            continue
        expected = expected_pop.get(r["unit_id"], {})
        if r.get("branches") != expected.get("branches") or r.get("lineage_id") != expected.get("lineage_id"):
            parent_errors.append(r["unit_id"])
    add("SINGLETON_PARENT_LINEAGE_MATCHES", parent_errors, "All explicit branch records and orphan identities match source")
    try:
        control = control_id(source["outcomes"], model["config"])
        valid = actual_pop.get(control) == expected_pop[control] and sum(c["case_type"] == CASE_TYPES[3] and c["unit_id"] == control for c in cases) == 1
        control_errors = [] if valid else [control]
    except (InvariantError, KeyError) as error:
        control_errors = [str(error)]
    add("S02135_REGRESSION_VALID", control_errors, "Configured fixed control (Job: S02135) is mapped and independently selected with original span/surface")
    boundary_errors = []
    if Counter(c["boundary_ref"] for c in cases if c["case_type"] == CASE_TYPES[4]) != Counter(model["config"]["boundary_refs"]):
        boundary_errors.append("Configured boundary panels missing or duplicated")
    if row_bag(model["boundary"]) != row_bag(expected_boundary):
        boundary_errors.append("Boundary evidence differs from all source matches/spans")
    for c in cases:
        if c["case_type"] == CASE_TYPES[4] and c.get("context_id") != context_id(model["config"]["book"], c["boundary_ref"], c["boundary_ref"]):
            boundary_errors.append(c["case_id"])
    add("BOUNDARY_CONTROLS_COMPLETE", boundary_errors, "Six full panels with every matching occurrence/outcome and panel context")
    core = pop + model["evidence"] + model["boundary"]
    add("NO_EXTENSION_OBJECT_IN_CORE", [r.get("unit_id") for r in core if r.get("unit_type") not in {BUNDLE, SINGLETON}
        or r.get("relation_layer") == base.OVERLAY or r.get("object_type") == base.OVERLAY], "Only the two existing object types in core")
    expected_overlay = overlays_for(cases, source, expected_targets + expected_boundary, model["tables"], model["config"])
    extension_fields = {"relation", "relation_id", "relation_layer", "short_bundle_id", "long_bundle_id"}
    contaminated = [r.get("unit_id", r.get("case_id")) for r in core + cases + model["relations"] if extension_fields & set(r)]
    if row_bag(model["overlay"]) != row_bag(expected_overlay):
        contaminated.append("Overlay source relations/coverage/attachments differ")
    extension_provenance = {p["object_id"] for p in model["provenance"] if p["role"] == "sequence_extension"}
    contaminated.extend(r.get("unit_id") for r in core if r.get("unit_id") in extension_provenance)
    add("EXTENSION_RELATIONS_OVERLAY_ONLY", contaminated, "Exact incident/exemplar source overlays, never occurrence-verified")
    add("REVIEW_FIELDS_BLANK_EXCEPT_STATUS", [c["case_id"] for c in cases if {f: c.get(f) for f in REVIEW_FIELDS} != base.review_defaults()] +
        [r.get("unit_id") for r in core + model["relations"] + model["overlay"] if any(f in r for f in REVIEW_FIELDS)],
        "Review forms exist only on cases and begin with canonical defaults")
    semantic = re.compile(r"function|rhetoric|discourse|theolog|speaker|macro|semantic", re.I)
    def semantic_keys(value):
        if isinstance(value, dict):
            return [k for k, v in value.items() if semantic.search(k)] + [k for v in value.values() for k in semantic_keys(v)]
        if isinstance(value, list):
            return [k for v in value for k in semantic_keys(v)]
        return []
    add("NO_AUTOMATIC_FUNCTION_LABELS", semantic_keys(core + cases + model["relations"] + model["overlay"] + list(model["contexts"].values())),
        "No semantic/function columns in generated review views; original provenance snapshots remain untouched")
    counts = Counter(c["case_type"] for c in cases)
    add("PILOT_CASE_COUNTS_VALID", [] if counts == Counter(dict.fromkeys(CASE_TYPES, 6)) and len({c["case_id"] for c in cases}) == 30 else [dict(counts)], "Five groups of six unique cases")
    bundle_ids = [c["unit_id"] for c in cases if c["case_type"] in CASE_TYPES[:3]]
    add("PILOT_SELECTIONS_DISJOINT_WHERE_REQUIRED", [] if len(bundle_ids) == len(set(bundle_ids)) else bundle_ids, "Three bundle strata are disjoint")
    try:
        expected_cases = select_cases(source["population"], source["outcomes"], model["config"])
        fields = ("case_id", "case_type", "unit_id", "unit_type", "boundary_ref", "seed", "selection_reason")
        diff("FIXED_SEED_SELECTION_REPRODUCIBLE", [{k: c[k] for k in fields} for c in expected_cases],
             [{k: c.get(k) for k in fields} for c in cases], "Recomputed lexicographic selection and separate seeded random draws")
    except InvariantError as error:
        add("FIXED_SEED_SELECTION_REPRODUCIBLE", [str(error)], "Recomputed selection")
    diff("RELATION_CONTEXT_COMPLETE", relations_for(cases, source, expected_targets + expected_boundary), model["relations"],
         "All ancestor/immediate repeated/direct singleton branch relations; no descendant target expansion")
    diff("PROVENANCE_COMPLETE", provenance_for(source, expected_targets + expected_boundary, expected_overlay, model["tables"]), model["provenance"],
         "All population source records and referenced occurrences/overlays retain exact source snapshots")
    return gates


def render_packet(model):
    units = {r["unit_id"]: r for r in model["population"]}
    lines = [f"# MILAL {VERSION} — Human Review Unit Decomposition", "",
        "Targets are existing bundles or canonical singleton outcomes. Containers and lineages are navigation metadata.",
        "Boundary panels are controls, not population objects. No descendant subtree is expanded as target evidence.",
        "Review time is diagnostic; no population time estimate.", "",
        f"Book: {model['config']['book']}; seed: {model['config']['seed']}.", ""]
    evidence = defaultdict(list)
    relations, overlays = defaultdict(list), defaultdict(list)
    for r in model["evidence"] + model["boundary"]:
        evidence[r["case_id"]].append(r)
    for r in model["relations"]:
        relations[r["case_id"]].append(r)
    for r in model["overlay"]:
        overlays[r["case_id"]].append(r)
    for case in model["cases"]:
        cid = case["case_id"]
        seen = set()
        def context(key):
            anchor = cid.lower() + "-" + base.digest(key)[:12]
            if key in seen:
                lines.append(f"- Context: [already displayed in this case](#{anchor}).")
                return
            seen.add(key)
            c = model["contexts"][key]
            lines.extend([f'<a id="{anchor}"></a>', "", f"- Context `{key}`: {c['resolution_status']}",
                f"- Previous {c['prev_ref'] or '[book start]'}: {c['prev_text']}", "- Complete verse span:", c["span_text"],
                f"- Next {c['next_ref'] or '[book end]'}: {c['next_text']}"])
            for kind in ("clauses", "sentences"):
                lines.append(f"- Overlapping {kind}:")
                lines.extend(f"  - `{n['node_id']}` {n['ref_start']}–{n['ref_end']}: {n['text']}" for n in c[kind])
        lines.extend([f"## {cid} — {case['case_type']}", "", f"- Selection: {case['selection_reason']}"])
        selected = sorted({r["unit_id"] for r in evidence[cid]})
        if case["unit_id"]:
            selected = [case["unit_id"]]
            lines.append(f"- Review target: `{case['unit_id']}` ({case['unit_type']})")
        else:
            lines.append(f"- Boundary control panel: {case['boundary_ref']}; all matching evidence below.")
            context(case["context_id"])
        for uid in selected:
            u = units[uid]
            lines.extend(["", f"### {u['unit_type']} `{uid}`", "",
                f"- Navigation container `{u['review_container_id']}`; lineage `{u['lineage_id'] or '-'}`",
                "- Provenance source IDs (full records in 06_object_provenance.csv): " + ", ".join(f"`{s}`" for s in u["source_ids"])])
            if u["unit_type"] == BUNDLE:
                lines.extend([f"- Occurrences: {u['occurrence_count']}; sequence length: {u['sequence_length']}; depth: {u['refinement_depth']}",
                    f"- Source levels: {u['levels_present']}; lowest: {u['lowest_level']}; highest: {u['highest_level']}",
                    f"- Exemplar {u['exemplar_ref_start']}–{u['exemplar_ref_end']}: {u['exemplar_surface_text']}",
                    "- Ancestry: " + " → ".join(u["ancestry"]),
                    f"- Direct repeated children: {u['direct_repeated_child_count']}; explicit refinement-event branches: {u['explicit_singleton_branch_count']}"])
                if u["parent_bundle_id"]:
                    p = units["BUNDLE:" + u["parent_bundle_id"]]
                    lines.append(f"- Immediate parent `{p['bundle_id']}`: lineage {p['lineage_id']}; levels {p['levels_present']}; sequence length {p['sequence_length']}; occurrences {p['occurrence_count']}")
                else:
                    lines.append("- Immediate parent: none (source root).")
            else:
                lines.append(f"- Kind: {u['outcome_kind']}; link status: {u['link_status']}")
            lines.extend(["", "#### Structural relation context", ""])
            for r in relations[cid]:
                if r["unit_id"] == uid:
                    parts = [f"- {r['relation_kind']}: `{r['related_unit_id']}`"]
                    if r['ancestry']:
                        parts.append("ancestry: " + " → ".join(r['ancestry']))
                    if r['transition']:
                        parts.append("transition: " + r['transition'])
                    parts.append(f"source `{r['source_id']}`")
                    lines.append("; ".join(parts))
            lines.extend(["", "#### Target evidence" if case["unit_id"] else "#### Boundary evidence", ""])
            for r in evidence[cid]:
                if r["unit_id"] == uid:
                    lines.extend([f"- Evidence `{r['evidence_id']}`; source `{r['source_id']}`",
                                  f"- Exact source surface ({r['ref_start']}–{r['ref_end']}): {r['surface_text']}"])
                    context(r["context_id"])
                    lines.append("")
        lines.extend(["### Sequence-extension overlay — separate", "",
            "EXEMPLAR_ONLY or UNRESOLVED. Exemplar evidence is not exhaustive occurrence/subwindow coverage.", ""])
        for r in overlays[cid]:
            lines.append(f"- `{r['relation_id']}`: {r['short_bundle_id']} → {r['long_bundle_id']}; {r['relation']}; {r['coverage']}; exemplar starts {r['short_exemplar_ref_start']} / {r['long_exemplar_ref_start']}; source `{r['source_id']}`")
        if not overlays[cid]:
            lines.append("- No matches established from available exemplar evidence; this does not establish absence of extension relations.")
        lines.extend(["", "### Human review", ""])
        lines.extend(f"- {f}: {case[f]}" for f in REVIEW_FIELDS)
        lines.append("")
    return "\n".join(lines) + "\n"


METHOD_NOTE = """# MILAL R3c.1 method note

One existing repeated bundle or exact R3c.0.2 canonical singleton outcome is one
review unit. No new semantic identity is introduced. Navigation IDs are frozen.
HIGH sorts occurrence count, direct repeated child count, explicit refinement
event branch count and depth descending, then bundle ID ascending. LOW uses
ascending measures after HIGH exclusion. RANDOM samples six from the remaining
ID-sorted pool. A separate Random instance with the same recorded config seed
selects five singleton outcomes after the fixed configured control.

Branch ranking counts source refinement-event records per immediate parent.
G6 link records do not double-count those events in the ranking; all explicit
event and link branches remain in the population, relations and provenance.
Only explicit mapped G6 IDs fold singleton identities. All original source
records, parents, surfaces and spans survive; equal texts never merge identities.

All selected target occurrences are emitted without truncation. Parent/ancestor
and direct child relations are context, not descendant target expansion.
Boundary panels include all matching occurrences and all spans of matching
singleton outcomes. They are not population units. All population units remain
inspectable, including unselected candidates. Population provenance includes all
membership/singleton records; occurrence snapshots cover selected/boundary evidence.
Raw provenance snapshots may contain historical source columns; generated review
views never assign or introduce semantic/function labels.

Span context reuses frozen R3c.0.2 complete-verse, neighbor and word-overlap
clause/sentence logic. Cross-chapter spans and nonwrapping book edges are kept.
Only evidence spans and boundary controls request context, not relation-only
neighbors or unselected population entries.

Extension overlays are incident to target bundles or explicit singleton parents.
Boundary overlays match exemplar starts, plus unresolved incident relations.
Coverage is EXEMPLAR_ONLY or UNRESOLVED; no OCCURRENCE_VERIFIED claim is made.
No exemplar match does not establish absence of an extension. Extension source
records are stored under EXT identifiers and never become core review units.

Only review_status is prefilled (UNREVIEWED). Review time is diagnostic; no
population hours are extrapolated. Synthetic validation is not R3c.1 empirical
acceptance. Windows is the next empirical environment; human inspection is
required before proceeding beyond this stage. No R4 analysis is performed.
"""


def write_outputs(model, out, metadata=None):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    inventory = [{"source": k, "source_file": t.name, "columns": t.fields, "row_count": len(t.rows),
                  "input_zip_sha256": t.zip_sha256, "input_archive": t.archive_name} for k, t in sorted(model["tables"].items())]
    gates = build_gates(model)
    for name, rows, fields in (
        ("01_source_schema_inventory.csv", inventory, None),
        ("02_review_cases.csv", model["cases"], CASE_FIELDS),
        ("03_review_unit_population.csv", model["population"], None),
        ("04_case_evidence.csv", model["evidence"], EVIDENCE_FIELDS),
        ("05_relation_context.csv", model["relations"], RELATION_FIELDS),
        ("06_object_provenance.csv", model["provenance"], None),
        ("07_boundary_case_evidence.csv", model["boundary"], EVIDENCE_FIELDS),
        ("08_sequence_extension_overlay.csv", model["overlay"], OVERLAY_FIELDS),
        ("09_span_context_inventory.csv", [model["contexts"][k] for k in sorted(model["contexts"])], None),
        ("11_gates.csv", gates, ("gate_id", "status", "detail", "violations")),
    ):
        base.write_csv(out / name, rows, fields)
    (out / "10_review_packet.md").write_text(render_packet(model), encoding="utf-8")
    (out / "12_method_note.md").write_text(METHOD_NOTE, encoding="utf-8")
    failures = [g["gate_id"] for g in gates if g["status"] != "PASS"]
    meta = {**(metadata or {}), "version": VERSION, "pilot_config": model["config"], "seed": model["config"]["seed"],
        "case_counts": dict(Counter(c["case_type"] for c in model["cases"])),
        "review_unit_population_counts": dict(Counter(r["unit_type"] for r in model["population"])),
        "navigation_container_count": len(model["tables"]["workspace"].rows),
        "singleton_outcome_kinds": dict(Counter(r["outcome_kind"] for r in model["population"] if r["unit_type"] == SINGLETON)),
        "input_archives": sorted({(t.archive_name, t.zip_sha256) for t in model["tables"].values()}),
        "context_count": len(model["contexts"]), "gate_count": len(gates), "gate_failures": failures,
        "boundary_extension_coverage_exhaustive": False,
        "empirical_acceptance": "PENDING_R3C_1_WINDOWS_RUN_AND_HUMAN_PACKET_INSPECTION", "exit_code": 2 if failures else 0}
    (out / "90_run_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base.write_manifest(out)
    return meta["exit_code"]


def synthetic_fixture():
    tables, config, provider = base.synthetic_fixture()
    # Extend only the synthetic source schema, never the frozen implementation.
    tables["members"].fields.extend(MEMBER_FIELDS)
    for i, row in enumerate(tables["members"].rows):
        count = 1 + i % 7
        row.update(occurrence_count=str(count), sequence_length="1", levels_present="G0 | G1",
                   lowest_level="G0", highest_level="G1")
        record = next(r for r in tables["occurrences"].rows if r["bundle_id"] == row["bundle_id"])
        for j in range(1, count):
            tables["occurrences"].rows.append({**record, "window_id": record["window_id"] + f"_{j}"})
    # Include an emitted crossing span as well as the original multi-verse span.
    tables["occurrences"].rows[2].update(ref_start="1:3", ref_end="2:1")
    return tables, config, provider


def self_test(output_dir=None):
    tables, config, provider = synthetic_fixture()
    with tempfile.TemporaryDirectory(prefix="milal_r3c1_") as tmp:
        root = Path(tmp)
        archives = base.write_synthetic_archives(tables, root)
        model = build_model(base.load_inputs(*archives), config, provider)
        gates = build_gates(model)
        assert all(g["status"] == "PASS" for g in gates), gates
        for table in tables.values():
            table.rows.reverse()
        assert model["cases"] == build_model(tables, config, provider)["cases"]
        for gate, mutate in (
            ("NO_TARGET_OCCURRENCE_TRUNCATION", lambda m: m["evidence"].remove(next(r for r in m["evidence"] if r["unit_type"] == BUNDLE))),
            ("REVIEW_UNIT_POPULATION_COMPLETE", lambda m: m["population"].pop(0)),
            ("EXTENSION_RELATIONS_OVERLAY_ONLY", lambda m: m["evidence"][0].update(relation="EXTENDS")),
            ("REVIEW_FIELDS_BLANK_EXCEPT_STATUS", lambda m: m["cases"][0].update(observable_behavior="automatic")),
        ):
            changed = copy.deepcopy(model)
            mutate(changed)
            assert next(g for g in build_gates(changed) if g["gate_id"] == gate)["status"] == "FAIL"
        out = Path(output_dir) if output_dir else root / "output"
        if out.exists() and any(out.iterdir()):
            raise InvariantError(f"Output directory must be empty: {out}")
        assert write_outputs(model, out, {"run_kind": "SYNTHETIC_SELF_TEST"}) == 0
        packet = (out / "10_review_packet.md").read_text(encoding="utf-8")
        assert packet.count("### Human review\n") == 30
        assert "sentence-cross" in packet and "EXEMPLAR_ONLY" in packet
        print(f"SELF-TEST PASS: 30 cases; {len(gates)} computed gates; 4 negative gate mutations; ZIP roundtrip and source-order reproducibility checked.")
        if output_dir:
            print(f"Synthetic packet retained: {out.resolve()}")
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="MILAL R3c.1 human review unit decomposition")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--r3b2-zip", type=Path)
    parser.add_argument("--r3b3-zip", type=Path)
    parser.add_argument("--tf-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--pilot-config", type=Path, default=Path(__file__).resolve().parents[1] / "config/r3c_1_job_pilot.json")
    parser.add_argument("--seed", type=int, help="Explicit override of configured seed")
    args = parser.parse_args(argv)
    if args.self_test:
        return self_test(args.output_dir)
    if args.output_dir is None:
        parser.error("--output-dir is required for a real run")
    out = args.output_dir.expanduser().resolve()
    if out.exists():
        print(f"ERROR: choose a fresh output directory: {out}", file=sys.stderr)
        return 2
    out.mkdir(parents=True)
    meta = {"version": VERSION, "run_kind": "REAL_BHSA", "started_utc": datetime.now(timezone.utc).isoformat(),
            "tf_dir": str(args.tf_dir), "pilot_config_path": str(args.pilot_config)}
    try:
        if any(v is None for v in (args.r3b2_zip, args.r3b3_zip, args.tf_dir)):
            raise SchemaError("--r3b2-zip, --r3b3-zip and --tf-dir are required")
        config = json.loads(args.pilot_config.read_text(encoding="utf-8-sig"))
        if args.seed is not None:
            config["seed"] = args.seed
        config = validate_config(config)
        meta.update(seed=config["seed"], pilot_config_sha256=base.sha256_file(args.pilot_config))
        tables = base.load_inputs(args.r3b2_zip, args.r3b3_zip)
        model = build_model(tables, config, TFContext(args.tf_dir, config["book"]))
        meta["finished_utc"] = datetime.now(timezone.utc).isoformat()
        status = write_outputs(model, out, meta)
    except Exception as error:
        status = 2
        message = f"{type(error).__name__}: {error}"
        meta.update(error=message, exit_code=2, finished_utc=datetime.now(timezone.utc).isoformat())
        (out / "00_FATAL_ERROR.txt").write_text(message + "\n", encoding="utf-8")
        base.write_csv(out / "11_gates.csv", [{"gate_id": "INPUT_OR_MODEL_VALIDATION", "status": "FAIL", "detail": message, "violations": [message]}])
        (out / "90_run_metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        base.write_manifest(out)
        print(message, file=sys.stderr)
    print(f"MILAL {VERSION}: {'PASS' if status == 0 else 'FAIL'}; output={out}")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
