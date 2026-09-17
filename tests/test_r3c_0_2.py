"""Contract tests for R3c.0.2; no BHSA installation required."""
import csv
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
BASELINE_FIXTURES = ROOT / "tests/fixtures/r3c_0_1"
sys.path.insert(0, str(ROOT / "src"))
import milal_r3c_0_2_reviewability as m


class PilotTests(unittest.TestCase):
    def setUp(self):
        self.tables, self.config, self.provider = m.synthetic_fixture()

    def build(self):
        return m.build_model(self.tables, self.config, self.provider)

    def test_thirty_cases_and_non_job_count(self):
        model = self.build()
        self.assertEqual(len(model["cases"]), 30)
        self.assertEqual(model["population"]["row_count"], 25)
        self.assertEqual(dict(m.Counter(c["case_type"] for c in model["cases"])),
                         dict.fromkeys(m.CASE_TYPES, 6))
        self.assertTrue(all(g["status"] == "PASS" for g in m.build_gates(model)))

    def test_branching_and_ancestry(self):
        model = self.build()
        self.assertEqual(model["ancestry"]["B001c"], ["B001a", "B001c"])
        packet = m.render_packet(model)
        self.assertIn("  - B001b", packet)
        self.assertIn("  - B001c", packet)
        self.assertIn("SINGLETON_OUTCOME", packet)

    def test_missing_parent(self):
        self.tables["members"].rows[1]["parent_bundle_id"] = "ABSENT"
        with self.assertRaisesRegex(m.InvariantError, "parent"):
            self.build()

    def test_cycle(self):
        self.tables["members"].rows[0]["parent_bundle_id"] = "B001b"
        with self.assertRaisesRegex(m.InvariantError, "cycle"):
            self.build()

    def test_explicit_folding_and_unmatched(self):
        model = self.build()
        outcomes = model["all_outcomes"]
        folded = outcomes["G6:S00001"]
        self.assertEqual(folded["outcome_kind"], "MAPPED")
        self.assertEqual(len([p for p in folded["sources"] if p["role"] == "refinement_event"]), 2)
        self.assertEqual({b["parent_bundle_id"] for b in folded["branches"]}, {"B001b", "B001c"})
        self.assertIn("EVENT_ONLY", {o["outcome_kind"] for o in outcomes.values()})
        self.assertEqual(outcomes["G6:ORPHAN"]["outcome_kind"], "G6_ONLY")
        self.assertEqual(outcomes["G6:ORPHAN"]["link_status"], "EXPLICIT_ORPHAN")

    def test_same_text_and_span_do_not_fold(self):
        model = self.build()
        events = [o for o in model["all_outcomes"].values() if o["outcome_kind"] == "EVENT_ONLY"]
        self.assertEqual(len(events), 2)
        self.assertNotEqual(events[0]["object_id"], events[1]["object_id"])
        self.assertEqual(events[0]["surface_text"], events[1]["surface_text"])

    def test_conflicting_lineage(self):
        self.tables["events"].rows[0]["lineage_id"] = "L002"
        with self.assertRaisesRegex(m.InvariantError, "lineage|parent"):
            self.build()

    def test_nonoverlapping_mapped_span(self):
        self.tables["events"].rows[0]["exemplar_ref_start"] = "2:1"
        self.tables["events"].rows[0]["exemplar_ref_end"] = "2:1"
        with self.assertRaisesRegex(m.InvariantError, "span"):
            self.build()

    def test_overlapping_different_spans_preserved(self):
        self.tables["events"].rows[0]["exemplar_ref_end"] = "1:2"
        outcome = self.build()["all_outcomes"]["G6:S00001"]
        self.assertIn("1:2", {s["ref_end"] for s in outcome["spans"]})

    def test_incompatible_sequence(self):
        self.tables["events"].rows[0]["sequence_length"] = "2"
        with self.assertRaisesRegex(m.InvariantError, "sequence"):
            self.build()

    def test_incompatible_atom_identity(self):
        self.tables["events"].rows[0]["exemplar_start_index_1based"] = "999"
        with self.assertRaisesRegex(m.InvariantError, "atom identity"):
            self.build()

    def test_g6_identities_with_identical_text_remain_separate(self):
        for key in ("items", "links"):
            self.tables[key].rows[1]["surface_text"] = self.tables[key].rows[0]["surface_text"]
            self.tables[key].rows[1]["ref_start"] = "1:1"
            self.tables[key].rows[1]["ref_end"] = "1:1"
        event = next(r for r in self.tables["events"].rows if r["mapped_g6_singleton_review_item_id"] == "S00002")
        event.update(exemplar_ref_start="1:1", exemplar_ref_end="1:1")
        outcomes = self.build()["all_outcomes"]
        self.assertEqual(outcomes["G6:S00001"]["surface_text"], outcomes["G6:S00002"]["surface_text"])
        self.assertNotEqual(outcomes["G6:S00001"]["object_id"], outcomes["G6:S00002"]["object_id"])

    def test_dangling_mapped_id(self):
        self.tables["events"].rows[0]["mapped_g6_singleton_review_item_id"] = "MISSING"
        with self.assertRaisesRegex(m.InvariantError, "MISSING"):
            self.build()

    def test_context_spans_cross_chapter_and_edges(self):
        ctx = self.provider.context("1:1", "1:3")
        self.assertEqual(ctx["next_ref"], "2:1")
        self.assertEqual(ctx["prev_ref"], "")
        self.assertIn("1:2", ctx["span_text"])
        self.assertEqual(self.provider.context("1:3", "2:1")["next_ref"], "2:2")
        self.assertEqual(self.provider.context("2:3", "2:3")["next_ref"], "")
        self.assertEqual(self.provider.context("8:1", "8:2")["resolution_status"], "UNRESOLVED")

    def test_overlapping_structure(self):
        ctx = self.provider.context("1:3", "2:1")
        self.assertIn("sentence-cross", {n["node_id"] for n in ctx["sentences"]})

    def test_boundary_occurrences_all_preserved(self):
        model = self.build()
        case = next(c for c in model["cases"] if c["case_type"] == "BOUNDARY_CONTROL" and c["boundary_ref"] == "1:2")
        rows = [r for r in model["boundary_evidence"] if r["case_id"] == case["case_id"] and r["object_type"] == "REPEATED_BUNDLE_OCCURRENCE"]
        expected = [r for r in self.tables["occurrences"].rows if m.contains(r["ref_start"], r["ref_end"], "1:2", self.config["book"])]
        self.assertEqual(len(rows), len(expected))
        self.assertGreater(len(rows), 1)

    def test_reproducibility_and_input_order(self):
        first = self.build()
        for t in self.tables.values():
            t.rows.reverse()
        second = self.build()
        self.assertEqual(first["cases"], second["cases"])
        self.assertEqual(set(first["all_outcomes"]), set(second["all_outcomes"]))

    def test_insufficient_population(self):
        self.tables["workspace"].rows = self.tables["workspace"].rows[:12]
        with self.assertRaises(m.InvariantError):
            self.build()

    def test_insufficient_singleton_population(self):
        model = self.build()
        containers = [c for c in model["cases"] if c["case_type"] in m.CASE_TYPES[:3]]
        with self.assertRaisesRegex(m.InvariantError, "Insufficient"):
            m.select_cases(containers, dict(list(model["all_outcomes"].items())[:5]), self.config)

    def test_exact_selection_order(self):
        model = self.build()
        cases = model["cases"]
        self.assertEqual([c["review_container_id"] for c in cases[:6]], [f"C{i:03d}" for i in range(1, 7)])
        self.assertEqual(cases[6]["review_container_id"], "ORPHAN")
        self.assertEqual(cases[18]["object_id"], "G6:S00001")

    def test_missing_required_singleton_control(self):
        self.config["singleton_control"]["review_item_id"] = "ABSENT"
        with self.assertRaisesRegex(m.InvariantError, "control missing"):
            self.build()

    def test_duplicate_g6_identity_fails(self):
        self.tables["links"].rows.append(dict(self.tables["links"].rows[0]))
        with self.assertRaisesRegex(m.InvariantError, "duplicate"):
            self.build()

    def test_blank_and_duplicate_containers(self):
        for value in ("", self.tables["workspace"].rows[1]["review_container_id"]):
            with self.subTest(value=value):
                self.tables["workspace"].rows[0]["review_container_id"] = value
                with self.assertRaisesRegex(m.InvariantError, "container"):
                    self.build()

    def test_schema_is_explicit(self):
        self.tables["members"].fields.remove("parent_bundle_id")
        with self.assertRaisesRegex(m.SchemaError, "parent_bundle_id"):
            self.build()

    def test_required_columns_match_actual_baseline_inventory(self):
        path = BASELINE_FIXTURES / "01_source_schema_inventory.csv"
        with path.open(encoding="utf-8-sig") as stream:
            inventory = {r["source"]: set(r["columns"].split(" | ")) for r in csv.DictReader(stream)}
        for key, (owner, filename) in m.SOURCE_FILES.items():
            self.assertLessEqual(set(m.SCHEMAS[key]), inventory[f"{owner}:{filename}"])

    def test_cli_success_failure_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            z2, z3 = m.write_synthetic_archives(self.tables, root)
            config = root / "config.json"
            config.write_text(json.dumps(self.config), encoding="utf-8")
            out = root / "run"
            args = ["--r3b2-zip", str(z2), "--r3b3-zip", str(z3), "--pilot-config", str(config),
                    "--tf-dir", str(root), "--output-dir", str(out)]
            with patch.object(m, "TFContext", return_value=self.provider), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(m.main(args), 0)
                before = m.sha256_file(out / "99_manifest_sha256.csv")
                self.assertEqual(m.main(args), 2)
                self.assertEqual(before, m.sha256_file(out / "99_manifest_sha256.csv"))
                args[-1] = str(root / "bad-count")
                self.assertEqual(m.main(args + ["--expected-review-containers", "1066"]), 2)
            failed = root / "bad-count"
            self.assertIn("Optional regression assertion", (failed / "00_FATAL_ERROR.txt").read_text(encoding="utf-8"))
            self.assertEqual(json.loads((failed / "90_run_metadata.json").read_text(encoding="utf-8"))["exit_code"], 2)

    def assert_gate_fails(self, model, gate):
        gates = {r["gate_id"]: r for r in m.build_gates(model)}
        self.assertEqual(gates[gate]["status"], "FAIL", gates[gate])

    def test_membership_gate_negative(self):
        model = self.build()
        model["container_evidence"][0]["lineage_id"] = "WRONG"
        self.assert_gate_fails(model, "CORE_LINEAGE_MATCHES_MEMBERSHIP")

    def test_singleton_parent_gate_negative(self):
        model = self.build()
        outcome = next(o for o in model["outcomes"] if o["branches"])
        outcome["branches"][0]["parent_bundle_id"] = "ABSENT"
        self.assert_gate_fails(model, "SINGLETON_PARENT_LINEAGE_MATCHES")

    def test_extension_object_gate_negative(self):
        model = self.build()
        model["container_evidence"][0]["object_type"] = m.OVERLAY
        self.assert_gate_fails(model, "NO_EXTENSION_OBJECT_IN_CORE")

    def test_extension_relation_gate_negative(self):
        model = self.build()
        model["container_evidence"][0]["relation"] = "EXTENDS"
        self.assert_gate_fails(model, "EXTENSION_RELATIONS_OVERLAY_ONLY")

    def test_missing_overlay_gate_negative(self):
        model = self.build()
        model["overlay"].pop()
        self.assert_gate_fails(model, "EXTENSION_RELATIONS_OVERLAY_ONLY")

    def test_blank_fields_and_no_autolabel(self):
        model = self.build()
        for row in model["cases"]:
            self.assertEqual({f: row[f] for f in m.REVIEW_FIELDS}, m.review_defaults())
        model["cases"][0]["exceptions"] = "autofilled"
        self.assert_gate_fails(model, "CANONICAL_REVIEW_DEFAULTS")
        model["boundary_evidence"][0]["rhetorical_function"] = "closure"
        self.assert_gate_fails(model, "NO_FUNCTION_AUTOLABEL")

    def test_coverage_not_overclaimed(self):
        model = self.build()
        self.assertEqual({r["coverage"] for r in model["overlay"]}, {"EXEMPLAR_ONLY"})
        self.assertIn("EXEMPLAR_ONLY", m.render_packet(model))

    def test_unresolved_coverage_visible(self):
        self.tables["overlay"].rows[0]["short_exemplar_ref_start"] = ""
        self.assertIn("UNRESOLVED", {r["coverage"] for r in self.build()["overlay"]})

    def test_packet_has_one_outcome_detail_per_case(self):
        model = self.build()
        packet = m.render_packet(model)
        for case in model["cases"]:
            part = packet.split(f"## {case['case_id']} —", 1)[1].split("\n## CASE", 1)[0]
            for oid in model["case_outcomes"][case["case_id"]]:
                self.assertEqual(part.count(f"#### SINGLETON_OUTCOME `{oid}`"), 1)
            for field, value in m.review_defaults().items():
                self.assertIn(f"- {field}: {value}\n", part)

    def test_context_gate_rejects_unresolved_span(self):
        model = self.build()
        next(iter(model["contexts"].values()))["resolution_status"] = "UNRESOLVED"
        self.assert_gate_fails(model, "SPAN_CONTEXT_RESOLVES")

    def test_output_roundtrip_provenance_and_manifest(self):
        model = self.build()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            m.write_outputs(model, out)
            def read(name):
                with (out / name).open(encoding="utf-8-sig", newline="") as stream:
                    return list(csv.DictReader(stream))
            cases = read("02_review_cases.csv")
            self.assertEqual(len(cases), 30)
            provenance = read("05_object_provenance.csv")
            self.assertTrue(all(json.loads(p["source_row_json"]) for p in provenance))
            manifest = read("99_manifest_sha256.csv")
            for row in manifest:
                self.assertEqual(m.sha256_file(out / row["file"]), row["sha256"])

    def test_optional_job_regression_from_checked_in_baseline(self):
        path = BASELINE_FIXTURES / "08_boundary_control_pattern_matches.csv"
        with path.open(encoding="utf-8-sig") as f:
            rows = [r for r in csv.DictReader(f) if r["review_item_id"] == "S02135"]
        self.assertEqual({r["object_type"] for r in rows}, {"G6_SINGLETON_REVIEW_ITEM", "SINGLETON_REFINEMENT_EVENT"})
        self.assertEqual({r["parent_bundle_id"] for r in rows}, {"RB01716"})
        self.assertEqual({r["lineage_id"] for r in rows}, {"RL00218"})

    def test_job_config_control_through_new_pipeline(self):
        # Real baseline control identity/surface in a synthetic genealogy. This is
        # an identity/rendering regression, not a reconstruction of real ancestry.
        path = BASELINE_FIXTURES / "08_boundary_control_pattern_matches.csv"
        with path.open(encoding="utf-8-sig") as stream:
            baseline = next(r for r in csv.DictReader(stream) if r["review_item_id"] == "S02135")
        config = json.loads((ROOT / "config/r3c_0_2_job_pilot.json").read_text(encoding="utf-8"))
        mapping = dict(zip(self.config["boundary_refs"], config["boundary_refs"]))
        for table in self.tables.values():
            for row in table.rows:
                for field, value in list(row.items()):
                    if "ref_start" in field or "ref_end" in field:
                        row[field] = mapping.get(value, value)
                    if value == "S00001":
                        row[field] = "S02135"
                if row.get("review_item_id") == "S02135" or row.get("mapped_g6_singleton_review_item_id") == "S02135":
                    for field in ("surface_text", "exemplar_surface_text"):
                        if field in row:
                            row[field] = baseline["surface_text"]
        verses = [{**v, "ref": mapping[v["ref"]]} for v in self.provider.verses]
        provider = m.SpanContext("Job", verses, self.provider.structures)
        model = m.build_model(self.tables, config, provider)
        control = next(c for c in model["cases"] if c["object_id"] == "G6:S02135")
        self.assertEqual(control["case_type"], "SINGLETON_ITEM")
        outcome = model["all_outcomes"][control["object_id"]]
        self.assertEqual({s["role"] for s in outcome["sources"]}, {"g6_item", "g6_link", "refinement_event"})
        self.assertTrue(all(b["ancestry"] for b in outcome["branches"]))
        self.assertIn("#### SINGLETON_OUTCOME `G6:S02135`", m.render_packet(model))


if __name__ == "__main__":
    unittest.main()
