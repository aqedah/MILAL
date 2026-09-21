"""MR1 provenance/reproduction only. No R4 or authoritative hierarchy."""
from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import importlib.metadata
import io
import json
from pathlib import Path
import sys
import zipfile

import milal_mr1_historical_rules as historical

ROOT = Path(__file__).resolve().parents[1]
VERSION = "MR1.0"
CONFIG = ROOT / "config/mr1_job.json"
FEATURES = "lex lex_utf8 g_word_utf8 sp pdp vt vs ps gn nu prs_ps prs_gn prs_nu typ kind domain function ls st nametype root".split()
FILES = dict(surface="00_job_surface_clauses.csv", csf="01_job_csf_speech_turns.csv",
             closure="02_job_explicit_closures.csv", way0="03_job_way0_wayhi.csv")
OUTPUTS = dict(surface="01_surface_clause_reproduction.csv", csf="02_csf_reproduction.csv",
               closure="03_explicit_closure_reproduction.csv", way0="04_way0_wayhi_reproduction.csv")
KEYS = dict(surface=("clause_node",), csf=("event_id",), closure=("start_clause", "end_clause", "pattern"), way0=("clause_node",))
IDENTITY = dict(surface=("clause_node", "ref"), csf=("event_id", "ref", "formula_end_ref", "csf_family", "speech_level"),
                closure=("start_clause", "end_clause", "pattern", "start_ref", "end_ref"), way0=("clause_node", "ref"))
RULES = dict(surface="Analyzer.surface_clause_rows", csf="Analyzer._detect_csf_turns",
             closure="Analyzer._detect_closure_spans", way0="Analyzer.wayhi_profile")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")


def csv_bytes(rows, fields=None):
    fields = fields or list(dict.fromkeys(k for r in rows for k in r))
    out = io.StringIO(newline="")
    writer = csv.DictWriter(out, fieldnames=fields, extrasaction="raise", lineterminator="\r\n")
    writer.writeheader()
    writer.writerows({k: canonical(v) if isinstance(v, (dict, list, tuple)) else v for k, v in r.items()} for r in rows)
    return out.getvalue().encode("utf-8-sig")


def read_csv(data):
    reader = csv.DictReader(io.StringIO(data.decode("utf-8-sig"), newline=""))
    if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
        raise ValueError("SCHEMA_ERROR: empty/duplicate CSV header")
    rows = list(reader)
    if any(None in r or None in r.values() for r in rows):
        raise ValueError("SCHEMA_ERROR: ragged CSV")
    return rows, reader.fieldnames


def ast_entries(text):
    out = {}
    for node in ast.parse(text).body:
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, ast.FunctionDef):
                    out[node.name + "." + method.name] = sha(ast.dump(method, include_attributes=False).encode())
        elif isinstance(node, ast.FunctionDef):
            out[node.name] = sha(ast.dump(node, include_attributes=False).encode())
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    out[target.id] = sha(ast.dump(node, include_attributes=False).encode())
    return out


def rule_verification(cfg):
    actual = ast_entries(Path(historical.__file__).read_text(encoding="utf-8-sig"))
    expected = {r["identity"]: r["ast_sha256"] for r in cfg["methods"]}
    return {k: actual.get(k) == v for k, v in expected.items()}, sorted(set(actual) - set(expected))


class EvidenceBHSA(historical.BHSA):
    """Strict API adapter; preserve actual queried values and ordered relationships.

    No source fallback: missing features/nodes/API errors fail before publication.
    A None feature value retains the historical caller's default semantics.
    """
    def __init__(self, api, book, cfg):
        self.F, self.L, self.T, self.cfg = api.F, api.L, api.T, cfg
        self.evidence = {}
        self.clauses = list(self.L.d(book, otype="clause"))
        self.verses = list(self.L.d(book, otype="verse"))
        self.atoms = list(self.L.d(book, otype="clause_atom"))
        self.clause_pos = {n: i for i, n in enumerate(self.clauses)}
        self.verse_pos = {n: i for i, n in enumerate(self.verses)}
        if not self.clauses or not self.verses or not self.atoms:
            raise ValueError("SCHEMA_ERROR: empty corpus")

    def f(self, name, node, default=""):
        key = f"feature:{name}:{node}"
        if key not in self.evidence:
            self.evidence[key] = getattr(self.F, name).v(node)
        value = self.evidence[key]
        return default if value is None else value

    def down(self, node, otype):
        key = f"down:{otype}:{node}"
        if key not in self.evidence:
            self.evidence[key] = list(self.L.d(node, otype=otype))
        return list(self.evidence[key])

    def up(self, node, otype):
        key = f"up:{otype}:{node}"
        if key not in self.evidence:
            self.evidence[key] = list(self.L.u(node, otype=otype))
        return list(self.evidence[key])

    def section(self, node):
        key = f"section:{node}"
        if key not in self.evidence:
            self.evidence[key] = list(self.T.sectionFromNode(node))
        return tuple(self.evidence[key])


def load_bhsa(path, cfg):
    from tf.fabric import Fabric
    path = Path(path).resolve()
    required = FEATURES + ["otype", "oslots", "otext"]
    missing = [name for name in required if not (path / (name + ".tf")).is_file()]
    if missing:
        raise ValueError("SCHEMA_ERROR: missing TF files " + repr(missing))
    versions = {}
    for name in required:
        header = (path / (name + ".tf")).read_text(encoding="utf-8").split("\n\n", 1)[0]
        versions[name] = next((line.split("=", 1)[1] for line in header.splitlines() if line.startswith("@version=")), None)
    if any(v != cfg["bhsa_version"] for v in versions.values()):
        raise ValueError("BHSA feature version mismatch: " + repr(versions))
    tf_version = importlib.metadata.version("text-fabric")
    if tf_version != cfg["tf_version"]:
        raise ValueError("Text-Fabric version mismatch: " + tf_version)
    fabric = Fabric(locations=str(path), modules=[""], silent="deep")
    api = fabric.load(" ".join(FEATURES), silent="deep")
    if not api:
        raise ValueError("Text-Fabric load failed")
    book = api.T.nodeFromSection((cfg["book"],))
    if book is None:
        raise ValueError("Job book node unavailable")
    b = EvidenceBHSA(api, book, cfg["rule_config"])
    files = {str(path / (name + ".tf")): sha((path / (name + ".tf")).read_bytes()) for name in sorted(fabric.features)
             if (path / (name + ".tf")).is_file() and fabric.features[name].dataLoaded}
    # otext is configuration, not a dataLoaded feature.
    for name in required:
        files[str(path / (name + ".tf"))] = sha((path / (name + ".tf")).read_bytes())
    return b, dict(mode="REAL", bhsa_version=cfg["bhsa_version"], feature_versions=versions,
                   tf_version=tf_version, data_path=str(path), book_node=book, tf_loaded=bool(api), data_hashes=files)


def load_baseline(directory, source_script, source_config, cfg):
    directory, source_script, source_config = map(Path, (directory, source_script, source_config))
    paths = {name: directory / name for name in cfg["baseline_hashes"]}
    paths["source_script"] = source_script
    paths["source_config"] = source_config
    expected = dict(cfg["baseline_hashes"], source_script=cfg["source_script_sha256"], source_config=cfg["source_config_sha256"])
    actual = {name: sha(p.read_bytes()) for name, p in paths.items()}
    if actual != expected:
        raise ValueError("Historical source fingerprint mismatch: " + repr([k for k in expected if expected[k] != actual[k]]))
    historical_config = json.loads(source_config.read_text(encoding="utf-8-sig"))
    if any(historical_config.get(k) != v for k, v in cfg["rule_config"].items()):
        raise ValueError("Historical rule config contradiction")
    source_ast = ast_entries(source_script.read_text(encoding="utf-8-sig"))
    if any(source_ast.get(r["identity"]) != r["ast_sha256"] for r in cfg["methods"]):
        raise ValueError("Historical source method contradiction")
    data = {k: (directory / name).read_bytes() for k, name in FILES.items()}
    meta = json.loads(paths["90_run_metadata.json"].read_text(encoding="utf-8-sig"))
    if meta["pipeline_version"] != "5.2.5" or meta["effective_dataset_version"] != "2021":
        raise ValueError("Historical metadata version contradiction")
    return data, dict(paths={k: str(v.resolve()) for k, v in paths.items()}, hashes=actual, expected_hashes=expected,
                      metadata=meta, rule_config=cfg["rule_config"], source_ast={r["identity"]: source_ast[r["identity"]] for r in cfg["methods"]})


def identity(row, kind):
    try:
        key = tuple(str(row[k]) for k in KEYS[kind])
    except KeyError as exc:
        raise ValueError("SCHEMA_ERROR: missing identity " + str(exc)) from exc
    if any(not v for v in key):
        raise ValueError("SCHEMA_ERROR: empty identity")
    return key


def compare(kind, current, baseline):
    old, fields = read_csv(baseline)
    if any(set(row) != set(fields) for row in current):
        raise ValueError("SCHEMA_ERROR: incompatible historical projection fields")
    current, generated_fields = read_csv(csv_bytes(current, fields))
    if generated_fields != fields or any(set(r) != set(fields) for r in current):
        raise ValueError("SCHEMA_ERROR: incompatible historical projection")
    def index(rows):
        out = {}
        for number, row in enumerate(rows, 2):
            key = identity(row, kind)
            if key in out:
                raise ValueError("AMBIGUOUS historical/current identity: " + repr(key))
            out[key] = (number, row)
        return out
    left, right = index(old), index(current)
    audit = []
    for key in sorted(left.keys() | right.keys()):
        ln, l = left.get(key, ("", {}))
        rn, r = right.get(key, ("", {}))
        diff = [f for f in fields if l.get(f) != r.get(f)] if l and r else []
        status = "EXACT" if l and r and not diff else "FIELD_DIFFERENCE" if l and r else "HISTORICAL_ONLY" if l else "CURRENT_ONLY"
        audit.append(dict(kind=kind, historical_file=FILES[kind], historical_row=ln, current_row=rn,
                          join_key=list(key), historical_identity={f: l.get(f) for f in IDENTITY[kind]} if l else {},
                          current_identity={f: r.get(f) for f in IDENTITY[kind]} if r else {},
                          match_status=status, differing_fields=diff,
                          differences={f: {"historical": l[f], "current": r[f]} for f in diff},
                          identity_equal=bool(l and r and all(l[f] == r[f] for f in IDENTITY[kind]))))
    return audit


def extract(b, cfg):
    analyzer = historical.Analyzer(b, cfg["rule_config"])
    tables = dict(surface=analyzer.surface_clause_rows(), csf=analyzer.csf_rows(),
                  closure=analyzer.closure_spans, way0=analyzer.wayhi_rows())
    memberships = {c: b.clause_atoms(c) for c in b.clauses}
    records, links = {}, []
    methods = {r["identity"]: r for r in cfg["methods"]}
    for kind, rows in tables.items():
        records[kind] = []
        for ordinal, row in enumerate(rows, 1):
            if kind == "csf":
                event = analyzer.speech_events[ordinal - 1]
                start, end = event["start_clause"], event["formula_end_clause"]
            elif kind == "closure":
                start, end = row["start_clause"], row["end_clause"]
            else:
                start = end = row["clause_node"]
            clauses = b.clauses[b.clause_pos[start]:b.clause_pos[end] + 1]
            atoms = historical.ordered_unique(a for c in clauses for a in memberships[c])
            event_id = kind + ":" + canonical(list(identity(row, kind)))
            record = dict(current_event_id=event_id, start_clause=start, end_clause=end,
                          chapter=b.cv(start)[0], verse_start=b.cv(start)[1], verse_end=b.cv(end)[1],
                          clause_ids=clauses, clause_atom_ids=atoms, span_length=len(clauses),
                          historical_projection=row, rule_id=RULES[kind],
                          historical_rule_source=cfg["source_script_name"],
                          source_script_sha256=cfg["source_script_sha256"],
                          rule_source_lines=[methods[RULES[kind]]["start_line"], methods[RULES[kind]]["end_line"]],
                          extractor_version=VERSION, feature_evidence_file="10_current_feature_evidence.json",
                          feature_evidence_clause_keys=[f"down:word:{c}" for c in clauses])
            if kind == "way0":
                frame = b.clauses[b.clause_pos[start]:b.clause_pos[start] + 1 + cfg["rule_config"]["wayhi_frame_lookahead_clauses"]]
                record.update(is_wayhi=row["wayhi_meta"], typ=b.f("typ", start),
                              verb_features=[dict(word=w, lexeme=b.lex(w), **{f: b.f(f, w) for f in ("vt", "vs", "ps", "gn", "nu")}) for w in b.words(start) if b.pos(w) == "verb"],
                              framing_evidence=[dict(clause=c, domain=b.domain(c), excluded_q=b.domain(c) == "Q",
                                                     temporal=analyzer.temporal_construction(c), location=analyzer.place_marker(c)) for c in frame])
            if kind == "csf":
                record.update(historical_event_type=row["speech_level"], anchor_type=row["csf_family"],
                              speaker_resolution=row["speaker_source_type"], historical_scope=row["csf_scope_profile"], historical_profile=row["csf_profile"])
            if kind == "closure":
                record.update(matched_pattern=row["pattern"], surface=row["text"])
            records[kind].append(record)
            for c in clauses:
                aa = memberships[c]
                links.append(dict(current_event_id=event_id, kind=kind, clause=c, chapter=b.cv(c)[0], verse=b.cv(c)[1],
                                  clause_atom_count=len(aa), ordered_clause_atom_ids=aa,
                                  first_clause_atom=aa[0] if aa else None, last_clause_atom=aa[-1] if aa else None))
    # All feature accesses used by copied behavior are recorded, including lookbacks.
    # Explicit word/phrase features allow inspection without re-running the source.
    for c in b.clauses:
        for n in [c] + b.words(c) + b.phrases(c) + memberships[c]:
            for name in FEATURES + ["otype"]:
                b.f(name, n)
    return dict(tables=tables, records=records, links=links, clauses=b.clauses, atoms=b.atoms,
                memberships={str(c): a for c, a in memberships.items()},
                scope=[b.ref(b.verses[0]), b.ref(b.verses[-1])], evidence=b.evidence.copy())


def build(b, cfg, baseline, source, execution):
    model = extract(b, cfg)
    repeat = extract(b, cfg)
    audit = [r for kind in FILES for r in compare(kind, model["tables"][kind], baseline[kind])]
    for kind, rows in model["records"].items():
        by_row = {r["current_row"]: r for r in audit if r["kind"] == kind and r["current_row"]}
        for i, row in enumerate(rows, 2):
            item = by_row[i]
            row.update(historical_file=item["historical_file"], historical_row=item["historical_row"], match_status=item["match_status"])
    checked, extra = rule_verification(cfg)
    return dict(model=model, repeat=repeat, audit=audit, baseline=baseline, source=source, execution=execution,
                rule_checks=checked, extra_methods=extra, config=cfg)


def gates(bundle):
    m, cfg, run, source = (bundle[k] for k in ("model", "config", "execution", "source"))
    audit, tables = bundle["audit"], m["tables"]
    out = []
    def gate(name, passed, detail):
        out.append(dict(gate=name, status="PASS" if passed else "FAIL", detail=detail))
    gate("BHSA_VERSION", run.get("bhsa_version") == cfg["bhsa_version"] and all(v == cfg["bhsa_version"] for v in run["feature_versions"].values()), run.get("bhsa_version"))
    gate("TF_LOAD", run.get("tf_loaded") is True and run.get("tf_version") == cfg["tf_version"] and bool(m["evidence"]), run.get("tf_version"))
    gate("FULL_SCOPE", m["scope"] == cfg["scope"], m["scope"])
    gate("CLAUSE_COUNT", len(m["clauses"]) == cfg["clause_count"] and len(set(m["clauses"])) == len(m["clauses"]), len(m["clauses"]))
    gate("ATOM_COUNT", len(m["atoms"]) == cfg["clause_atom_count"] and len(set(m["atoms"])) == len(m["atoms"]), len(m["atoms"]))
    gate("ATOM_MEMBERSHIP", bool(m["links"]) and all(r["ordered_clause_atom_ids"] == m["memberships"].get(str(r["clause"])) and r["clause_atom_count"] == len(r["ordered_clause_atom_ids"]) > 0 for r in m["links"]), len(m["links"]))
    gate("ATOM_ORDER", all(r["ordered_clause_atom_ids"] == m["evidence"].get(f"down:clause_atom:{r['clause']}") and r["first_clause_atom"] == r["ordered_clause_atom_ids"][0] and r["last_clause_atom"] == r["ordered_clause_atom_ids"][-1] for r in m["links"] if r["ordered_clause_atom_ids"]), "explicit L.d order")
    gate("SOURCE_FINGERPRINTS", all(source["hashes"].get(k) == v for k, v in source["expected_hashes"].items() if k not in FILES.values()) and source["rule_config"] == cfg["rule_config"], "metadata/config/script")
    gate("CSV_FINGERPRINTS", all(sha(bundle["baseline"][k]) == source["expected_hashes"][f] for k, f in FILES.items()), "current local comparison fingerprints")
    checks = bundle["rule_checks"]
    for name, method in (("CLOSURE_PROVENANCE", RULES["closure"]), ("CSF_PROVENANCE", RULES["csf"]), ("WAYHI_PROVENANCE", RULES["way0"])):
        gate(name, checks.get(method) is True, method)
    gate("COMPLETE_RULE_PROVENANCE", bool(checks) and all(checks.values()) and not bundle["extra_methods"], len(checks))
    gate("TEMPORAL_AUXILIARY", checks.get("Analyzer.temporal_construction") is True, "historical first-three / allowed POS / nonempty vt")
    gate("NO_FINITE_ONLY_AUXILIARY", checks.get("Analyzer.temporal_construction") is True and source["source_ast"].get("Analyzer.temporal_construction") == next(r["ast_sha256"] for r in cfg["methods"] if r["identity"] == "Analyzer.temporal_construction"), "exact AST; no additional infinitive/participle exclusion")
    gate("NO_WAYX_SHORTCUT", all(r["clause_type"] == "Way0" and m["evidence"].get(f"feature:typ:{r['clause_node']}") == "Way0" for r in tables["way0"]) and checks.get("Analyzer.wayhi_profile") is True, "actual candidate typ")
    recomputed = [r for kind in FILES for r in compare(kind, tables[kind], bundle["baseline"][kind])]
    gate("NO_FUZZY_MATCHING", audit == recomputed, "explicit keys; all audit rows rederived")
    gate("DETERMINISTIC_RERUN", all(m[k] == bundle["repeat"][k] for k in ("tables", "links", "memberships", "evidence")), "independent Analyzer instances")
    gate("COMPARISON_PERFORMED", set(r["kind"] for r in audit) == set(FILES), len(audit))
    old = {k: read_csv(bundle["baseline"][k])[0] for k in FILES}
    gate("COUNTS", all(len(tables[k]) == len(old[k]) == cfg["historical_counts"][k] for k in FILES), {k: [len(old[k]), len(tables[k])] for k in FILES})
    gate("IDENTITIES", bool(audit) and all(r["identity_equal"] for r in audit), sum(r["identity_equal"] for r in audit))
    gate("FIELD_EQUALITY", bool(audit) and all(r["match_status"] == "EXACT" and not r["differing_fields"] for r in audit), sum(r["match_status"] == "EXACT" for r in audit))
    unmatched = [r for r in audit if r["match_status"] in ("CURRENT_ONLY", "HISTORICAL_ONLY")]
    gate("UNMATCHED_ROWS", not unmatched and len(audit) == sum(len(v) for v in old.values()), len(unmatched))
    positive = [r for r in tables["way0"] if r["wayhi_meta"]]
    hp = [r for r in old["way0"] if r["wayhi_meta"] == "True"]
    gate("WAY0_AUDIT_COUNT", len(tables["way0"]) == len(old["way0"]) == cfg["historical_counts"]["way0"], len(tables["way0"]))
    gate("WAYHI_POSITIVE_COUNT", len(positive) == len(hp) == cfg["wayhi_positive_count"], len(positive))
    gate("WAYHI_NEGATIVE_COUNT", sum(not r["wayhi_meta"] for r in tables["way0"]) == sum(r["wayhi_meta"] == "False" for r in old["way0"]) == cfg["wayhi_negative_count"], len(tables["way0"]) - len(positive))
    gate("WAYHI_POSITIVE_IDENTITIES", [r["ref"] for r in positive] == cfg["wayhi_positive_refs"] and [(str(r["clause_node"]), r["ref"]) for r in positive] == [(r["clause_node"], r["ref"]) for r in hp], [r["ref"] for r in positive])
    gate("ALL_WAY0_RESOLVE", len([r for r in audit if r["kind"] == "way0" and r["identity_equal"]]) == cfg["historical_counts"]["way0"], "exact clause node plus coordinate")
    flattened = [r for rows in m["records"].values() for r in rows] + m["links"]
    fields = set(k for r in flattened for k in r)
    for name, forbidden in (("NO_HIERARCHY", {"macro_unit", "hierarchy", "macro_hierarchy"}), ("NO_PARENTAGE", {"mother", "parent", "parent_id", "parentage"}), ("NO_NEW_INTERPRETATION", {"rhetorical_label", "theological_label", "literary_label", "discourse_label"})):
        gate(name, not fields.intersection(forbidden) and all(set(row) == set(old[k][0]) for k in FILES for row in tables[k]), "historical projection only; no new structure/labels")
    gate("EVENT_PROVENANCE", all(r["source_script_sha256"] == cfg["source_script_sha256"] and r["rule_id"] in checks and r["clause_atom_ids"] == historical.ordered_unique(a for c in r["clause_ids"] for a in m["memberships"][str(c)]) and all(key in m["evidence"] for key in r["feature_evidence_clause_keys"]) for rows in m["records"].values() for r in rows), "current nodes, actual feature snapshot, rule, historical row")
    return out


def manifest_ok(files):
    try:
        rows, _ = read_csv(files["99_manifest_sha256.csv"])
        actual = {name: sha(data) for name, data in files.items() if name != "99_manifest_sha256.csv"}
        expected = {r["file"]: r["sha256"] for r in rows}
        return len(rows) == len(expected) and actual == expected
    except (KeyError, ValueError):
        return False


def manifest_gate(files):
    return dict(gate="MANIFEST_INTEGRITY", status="PASS" if manifest_ok(files) else "FAIL",
                detail="serialized member SHA256 and exact member inventory")


def render(bundle):
    m, cfg = bundle["model"], bundle["config"]
    files = {OUTPUTS[k]: csv_bytes(rows) for k, rows in m["records"].items()}
    files["05_clause_atom_marker_links.csv"] = csv_bytes(m["links"])
    files["06_historical_reproduction_audit.csv"] = csv_bytes(bundle["audit"])
    files["10_current_feature_evidence.json"] = json_bytes(m["evidence"])
    checks = gates(bundle)
    byte_status = {}
    for i, k in enumerate(FILES, 20):
        data = csv_bytes(m["tables"][k])
        files[f"{i}_historical_schema_{k}.csv"] = data
        byte_status[k] = dict(equal=data == bundle["baseline"][k], current_sha256=sha(data), historical_sha256=sha(bundle["baseline"][k]))
    metadata = dict(stage=VERSION, execution=bundle["execution"], sources=bundle["source"],
                    fingerprint_semantics=cfg["fingerprint_semantics"], source_files={str(p.relative_to(ROOT)): sha(p.read_bytes()) for p in (Path(__file__), Path(historical.__file__), CONFIG)},
                    byte_comparison=byte_status, historical_identity_policy=KEYS,
                    csf_identity_limit="Historical CSV has ordinal event_id and coordinates, no clause IDs; join by event_id, independently check family/level/start/end coordinates. No inferred historical clause ID.",
                    status="PASS" if all(r["status"] == "PASS" for r in checks) else "FAIL", r4_status="ON_HOLD_PENDING_MR1_REVIEW")
    files["90_run_metadata.json"] = json_bytes(metadata)
    catalog = ["# MR1 rule provenance", "", "Historical source: " + bundle["source"]["paths"].get("source_script", "SYNTHETIC"),
               "Config: " + bundle["source"]["paths"].get("source_config", "SYNTHETIC"),
               "Metadata: " + bundle["source"]["paths"].get("90_run_metadata.json", "SYNTHETIC"), "",
               "Only marker-writer dependency closure is transcribed. Participant/speaker calculations are historical comparison dependencies; no macro hierarchy, mother assignment, composition or boundary engine is executed.",
               "Closure width 1..2 total clauses; ordered normalized lexemes; shortest span per end/pattern.",
               "CSF detection and historical speaker inclusion/classification remain distinct from acceptance. Historical classification fields are confined to comparison provenance.",
               "Wayhi core: Way0 + historical finite HYH + p3/m/sg. Framing is independent, current plus next three clauses; Q framing clauses skipped.",
               "The temporal-lexeme auxiliary condition checks for a verbal word with a non-empty/non-NA `vt` value according to the historical implementation; MR1 does not strengthen this into a newly imposed finite-only criterion.",
               "", "Rule configuration:", "```json", json.dumps(cfg["rule_config"], ensure_ascii=False, indent=2), "```", "", "| Source dependency | Original lines | AST SHA256 |", "| --- | --- | --- |"]
    catalog += [f"| {r['identity']} | {r['start_line']}–{r['end_line']} | {r['ast_sha256']} |" for r in cfg["methods"]]
    files["07_rule_provenance_catalog.md"] = ("\n".join(catalog) + "\n").encode()
    summary = ["# MR1 reproduction summary", "", "Mode: " + bundle["execution"]["mode"], "",
               "MR1 reconstructs and tests the reproducibility of historically attested v5.2.x surface-marker extraction behavior against the currently available BHSA 2021 dataset.",
               "Historical `03_job_way0_wayhi.csv` is an audit table of all Way0 candidates, not a table containing only positive Wayhi events.",
               "Source-data identity: current TF files fingerprinted; historical raw dataset hashes unavailable (UNKNOWN_NOT_VERIFIED). Same version alone does not prove historical dataset byte identity.",
               "Node/coordinate and occurrence identity: exact native node keys where historical CSV supplies them. CSF supplies ordinal event_id/coordinates only; no guessed historical clause IDs.",
               "Row/field equality: every historical field audited, including historical-only classification fields; no fuzzy remapping.",
               "Byte identity: separate UTF-8-BOM/CRLF historical-schema exports; comparison below.", "",
               "| Table | Historical | Current | Exact fields | Historical only | Current only | Bytes equal |", "| --- | ---: | ---: | ---: | ---: | ---: | --- |"]
    for k in FILES:
        aa = [r for r in bundle["audit"] if r["kind"] == k]
        summary.append(f"| {k} | {len(read_csv(bundle['baseline'][k])[0])} | {len(m['tables'][k])} | {sum(r['match_status']=='EXACT' for r in aa)} | {sum(r['match_status']=='HISTORICAL_ONLY' for r in aa)} | {sum(r['match_status']=='CURRENT_ONLY' for r in aa)} | {byte_status[k]['equal']} |")
    pos = [r for r in m["tables"]["way0"] if r["wayhi_meta"]]
    summary += ["", f"Way0 audit rows: {len(m['tables']['way0'])}; Wayhi-positive: {len(pos)}; Wayhi-negative: {len(m['tables']['way0'])-len(pos)}.",
                "Positive references: " + ", ".join(r["ref"] for r in pos),
                f"Clauses: {len(m['clauses'])}; distinct atoms: {len(m['atoms'])}; event-clause linkage rows: {len(m['links'])}; multi-atom clauses: {sum(len(a)>1 for a in m['memberships'].values())}.",
                "", "Frozen R1.1 and v6.42.12 remain unavailable. No recovered frozen registry or accepted macro structure is claimed. R4 remains on hold pending researcher review.", "", "## Control inspection (no forced detection)", ""]
    controls = []
    for row in m["tables"]["surface"]:
        if row["ref"] in cfg["controls"] or (int(row["chapter"]), int(row["verse"])) <= (3, 1):
            controls.append(row)
    files["11_control_spot_checks.csv"] = csv_bytes(controls)
    for ref in cfg["controls"]:
        rr = [r for r in m["tables"]["surface"] if r["ref"] == ref]
        summary.append(f"- {ref}: clauses {[r['clause_node'] for r in rr]}; CSF starts {sum(r['speech_event_open'] for r in rr)}; closures {sum(r['closure_start'] for r in rr)}; Wayhi {sum(r['wayhi_meta'] for r in rr)}.")
    files["08_reproduction_summary.md"] = ("\n".join(summary) + "\n").encode()
    # Compute the gate on serialized payload, then re-seal the final package and
    # verify again. The manifest excludes only itself, avoiding circular hashes.
    files["99_manifest_sha256.csv"] = csv_bytes([dict(file=name, sha256=sha(data)) for name, data in sorted(files.items())])
    checks.append(manifest_gate(files))
    del files["99_manifest_sha256.csv"]
    files["09_gates.csv"] = csv_bytes(checks)
    files["99_manifest_sha256.csv"] = csv_bytes([dict(file=name, sha256=sha(data)) for name, data in sorted(files.items())])
    if not manifest_ok(files):
        raise ValueError("MANIFEST_INTEGRITY failed")
    return files


def publish(files, output):
    output = Path(output).resolve()
    zipped = output.with_name(output.name + "_results.zip")
    log = output.with_name(output.name + "_run.log")
    if output.exists() or zipped.exists() or log.exists():
        raise ValueError("Output already exists; no overwrite")
    if not manifest_ok(files):
        raise ValueError("MANIFEST_INTEGRITY failed before write")
    output.mkdir(parents=True)
    for name, data in files.items():
        (output / name).write_bytes(data)
    disk = {p.name: p.read_bytes() for p in output.iterdir()}
    if disk != files or not manifest_ok(disk):
        raise ValueError("Published file verification failed")
    with zipfile.ZipFile(zipped, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name, data in sorted(files.items()):
            info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, data)
    with zipfile.ZipFile(zipped) as z:
        if z.testzip() or {n: z.read(n) for n in z.namelist()} != files:
            raise ValueError("ZIP verification failed")
    rows, _ = read_csv(files["09_gates.csv"])
    passed = all(r["status"] == "PASS" for r in rows)
    log.write_text(f"MR1 {'PASS' if passed else 'FAIL'}\nGates {sum(r['status']=='PASS' for r in rows)}/{len(rows)}\nZIP {zipped}\nSHA256 {sha(zipped.read_bytes())}\n", encoding="utf-8")
    return passed, zipped, log


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tf-data")
    parser.add_argument("--historical-dir")
    parser.add_argument("--historical-script")
    parser.add_argument("--historical-config")
    parser.add_argument("--out", required=True)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    if args.self_test:
        from milal_mr1_synthetic import self_test_bundle
        bundle = self_test_bundle()
    else:
        if not all((args.tf_data, args.historical_dir, args.historical_script, args.historical_config)):
            parser.error("Real execution requires all four explicit source paths")
        baseline, source = load_baseline(args.historical_dir, args.historical_script, args.historical_config, cfg)
        b, execution = load_bhsa(args.tf_data, cfg)
        bundle = build(b, cfg, baseline, source, execution)
    files = render(bundle)
    if not args.self_test:
        paths = {**{p: bundle["source"]["hashes"][k] for k, p in bundle["source"]["paths"].items()}, **bundle["execution"]["data_hashes"]}
        if any(sha(Path(p).read_bytes()) != digest for p, digest in paths.items()):
            raise ValueError("Input changed during execution")
    passed, zipped, log = publish(files, args.out)
    print(f"{'PASS' if passed else 'FAIL'}: {zipped}\nLog: {log}")
    return 0 if passed else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print(f"MR1 STOP: {exc}", file=sys.stderr)
        sys.exit(2)
