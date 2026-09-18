"""Frozen-result presentation contracts: every gate has a failing mutation."""
import contextlib
import copy
import csv
import io
import json
from pathlib import Path
import random
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import milal_r3c_2_compact_review as m


def set_csv(source, key, rows, fields=None):
    if fields is None:
        fields, _ = m.csv_read(source["files"][m.FILES[key]], m.FILES[key])
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    source["files"][m.FILES[key]] = stream.getvalue().encode("utf-8-sig")


def remanifest(source):
    rows = [{"file": name, "bytes": len(data), "sha256": m.sha(data)}
            for name, data in sorted(source["files"].items()) if name != m.FILES["manifest"]]
    set_csv(source, "manifest", rows, ["file", "bytes", "sha256"])


def pack(source, path):
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in source["files"].items():
            archive.writestr(source["prefix"] + name, data)


class CompactReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="milal compact tests ")
        cls.root = Path(cls.temp.name)
        cls.zip = m.synthetic_source(cls.root)
        cls.source = m.read_source(cls.zip)
        cls.model = m.build_model(cls.source)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def gate_status(self, model, name):
        return next(g["status"] for g in m.build_gates(model) if g["gate_id"] == name)

    def test_all_gates_and_frozen_case_rows(self):
        gates = m.build_gates(self.model)
        self.assertEqual(len(gates), 23)
        self.assertTrue(all(g["status"] == "PASS" for g in gates), gates)
        self.assertEqual(self.model["cases"], m.source_rows(self.source, "cases"))
        self.assertEqual(len(self.model["cases"]), 30)
        import milal_r3c_0_2_reviewability as base
        self.assertIs(m.REVIEW_FIELDS, base.REVIEW_FIELDS)

    def test_negative_mutation_for_every_gate(self):
        def change_source_csv(x, key, mutate):
            rows = m.source_rows(x["source"], key)
            mutate(rows)
            set_csv(x["source"], key, rows)
        def wrong_version(x):
            meta = m.metadata(x["source"])
            meta["version"] = "R3c.0.2"
            x["source"]["files"][m.FILES["metadata"]] = json.dumps(meta).encode()
        def remove_control(x):
            x["evidence"] = [r for r in x["evidence"] if r["unit_id"] != "G6:S02135"]
        mutations = {
            "SOURCE_R3C1_MANIFEST_VALID": lambda x: x["source"]["files"].update({m.FILES["packet"]: b"tampered"}),
            "SOURCE_R3C1_GATES_ALL_PASS": lambda x: change_source_csv(x, "gates", lambda rows: rows[0].update(status="FAIL")),
            "SOURCE_R3C1_VERSION_VALID": wrong_version,
            "SOURCE_CASE_COUNT_VALID": lambda x: change_source_csv(x, "cases", lambda rows: rows.pop()),
            "SOURCE_CASE_SET_PRESERVED": lambda x: x["cases"][0].update(selection_reason="new sample"),
            "SOURCE_CASE_ORDER_PRESERVED": lambda x: x["cases"].reverse(),
            "REVIEW_TARGET_IDS_UNCHANGED": lambda x: x["cases"][0].update(unit_id=x["cases"][1]["unit_id"]),
            "ALL_EVIDENCE_IDS_PRESERVED": lambda x: x["evidence"].pop(),
            "NO_EVIDENCE_DUPLICATION_OR_LOSS": lambda x: x["evidence"].append(copy.deepcopy(x["evidence"][0])),
            "ALL_CONTEXT_REFERENCES_RESOLVE": lambda x: x["contexts"].pop(next(iter(x["contexts"]))),
            "CONTEXT_DETAIL_LOSSLESS": lambda x: next(iter(x["contexts"].values())).update(clauses="[]"),
            "RAW_RELATION_ROWS_PRESERVED": lambda x: x["raw_relations"].pop(),
            "COMPACT_RELATIONS_TRACE_TO_RAW": lambda x: x["compact_relations"][0].update(source_record_count=999),
            "BOUNDARY_EVIDENCE_PRESERVED": lambda x: x["boundary"].pop(),
            "EXTENSION_ROWS_PRESERVED": lambda x: x["overlay"].pop(),
            "EXTENSION_REMAINS_OVERLAY_ONLY": lambda x: x["evidence"][0].update(relation="EXTENDS"),
            "REVIEW_FIELDS_BLANK_EXCEPT_STATUS": lambda x: x["cases"][0].update(exceptions="automatic"),
            "NO_AUTOMATIC_FUNCTION_LABELS": lambda x: x["evidence"][0].update(function_label=""),
            "S02135_PRESERVED": remove_control,
            "PACKET_INDEX_COVERS_ALL_TARGET_EVIDENCE": lambda x: x.update(packet=x["packet"].replace("<!-- evidence:", "<!-- erased:", 1)),
            "PACKET_METRICS_MATCH_RENDERED_PACKET": lambda x: x["metrics"][0].update(packet_byte_count=1),
            "SOURCE_REFERENCES_RESOLVE": lambda x: x["raw_relations"][0].update(source_id="ABSENT"),
            "TARGET_SUMMARIES_PRESERVED": lambda x: x["summaries"][x["cases"][0]["case_id"]][0].update(occurrence_count="999"),
        }
        self.assertEqual(set(mutations), {g["gate_id"] for g in m.build_gates(self.model)})
        for name, mutate in mutations.items():
            with self.subTest(gate=name):
                model = copy.deepcopy(self.model)
                mutate(model)
                self.assertEqual(self.gate_status(model, name), "FAIL")

    def test_manifest_tampering_rejected_before_processing(self):
        for action in ("payload", "omitted", "size"):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as tmp:
                source = copy.deepcopy(self.source)
                if action == "payload":
                    source["files"][m.FILES["evidence"]] += b"tamper"
                else:
                    rows = m.source_rows(source, "manifest")
                    if action == "omitted":
                        rows.pop()
                    else:
                        rows[0]["bytes"] = "0"
                    set_csv(source, "manifest", rows)
                path = Path(tmp) / "tampered.zip"
                pack(source, path)
                with self.assertRaisesRegex(m.ValidationError, "MANIFEST"):
                    m.read_source(path)

    def test_failed_source_gate_rejected_even_with_valid_manifest(self):
        source = copy.deepcopy(self.source)
        rows = m.source_rows(source, "gates")
        rows[0]["status"] = "FAIL"
        set_csv(source, "gates", rows)
        remanifest(source)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "failed.zip"
            pack(source, path)
            with self.assertRaisesRegex(m.ValidationError, "GATES_ALL_PASS"):
                m.read_source(path)

    def test_wrong_version_and_case_count_rejected(self):
        for kind in ("version", "count"):
            source = copy.deepcopy(self.source)
            if kind == "version":
                meta = m.metadata(source)
                meta["version"] = "R3c.2"
                source["files"][m.FILES["metadata"]] = json.dumps(meta).encode()
            else:
                set_csv(source, "cases", m.source_rows(source, "cases")[:-1])
            remanifest(source)
            with self.subTest(kind=kind), self.assertRaises(m.ValidationError):
                m.build_model(source)

    def test_shared_context_display_keeps_every_occurrence(self):
        case = self.model["cases"][0]
        rows = [r for r in self.model["evidence"] if r["case_id"] == case["case_id"]]
        self.assertGreater(len(rows), len({r["context_id"] for r in rows}))
        section = dict(m.packet_sections(self.model["packet"]))[case["case_id"]]
        for context_id in {r["context_id"] for r in rows}:
            self.assertEqual(section.count(f"#### Context `{context_id}`"), 1)
        for r in rows:
            self.assertIn(f"Evidence `{m.text(r['evidence_id'])}`", section)
            self.assertIn(m.text(r["surface_text"]), section)
        self.assertNotIn("SYNTH sentences", section)

    def test_all_evidence_ids_trace_after_grouping(self):
        self.assertEqual(self.gate_status(self.model, "PACKET_INDEX_COVERS_ALL_TARGET_EVIDENCE"), "PASS")
        self.assertEqual(self.model["packet"].count("<!-- evidence:"), len(self.model["evidence"]) + len(self.model["boundary"]))

    def test_context_detail_json_and_unknown_fields_preserved(self):
        source = copy.deepcopy(self.source)
        fields, rows = m.csv_read(source["files"][m.FILES["contexts"]], "contexts")
        fields.append("source_note")
        for r in rows:
            r["source_note"] = "exact auxiliary context information"
        set_csv(source, "contexts", rows, fields)
        remanifest(source)
        model = m.build_model(source)
        self.assertEqual(m.row_bag(model["contexts"].values()), m.row_bag(rows))
        self.assertTrue(any(json.loads(c["sentences"]) for c in model["contexts"].values()))

    def test_compact_relations_keep_every_raw_record(self):
        rows = [r for r in self.model["compact_relations"] if r["source_record_count"] > 1]
        self.assertTrue(rows)
        raw = {r["raw_relation_id"]: r for r in self.model["raw_relations"]}
        for r in rows:
            self.assertEqual(len(r["raw_relation_ids"]), r["source_record_count"])
            self.assertTrue(all(k in raw for k in r["raw_relation_ids"]))
            self.assertEqual({raw[k]["related_unit_id"] for k in r["raw_relation_ids"]}, {r["related_unit_id"]})
        self.assertEqual(sum(r["source_record_count"] for r in self.model["compact_relations"]), len(raw))

    def test_duplicate_raw_relation_rows_are_not_deleted(self):
        source = copy.deepcopy(self.source)
        rows = m.source_rows(source, "relations")
        rows.append(dict(rows[0]))
        set_csv(source, "relations", rows)
        remanifest(source)
        model = m.build_model(source)
        self.assertEqual(len(model["raw_relations"]), len(rows))
        self.assertEqual(len({r["raw_relation_id"] for r in model["raw_relations"]}), len(rows))
        self.assertEqual(self.gate_status(model, "RAW_RELATION_ROWS_PRESERVED"), "PASS")

    def test_boundary_and_extension_payloads_and_coverage(self):
        for key in ("boundary", "overlay"):
            self.assertEqual(m.row_bag(m.source_rows(self.source, key)), m.row_bag(m.original_rows(self.source, key, self.model[key])))
        self.assertEqual({r["coverage"] for r in self.model["overlay"]}, {"EXEMPLAR_ONLY"})
        self.assertEqual(len([c for c in self.model["cases"] if c["case_type"] == "BOUNDARY_CONTROL"]), 6)
        self.assertNotIn("EXT:", self.model["packet"])

    def test_s02135_and_blank_fields(self):
        control = next(c for c in self.model["cases"] if c["unit_id"] == "G6:S02135")
        self.assertEqual(control["case_type"], "SINGLETON_OUTCOME")
        rows = [r for r in self.model["evidence"] if r["case_id"] == control["case_id"]]
        self.assertEqual(len(rows), 4)
        for case in self.model["cases"]:
            self.assertEqual([case[k] for k in m.REVIEW_FIELDS], ["UNREVIEWED"] + [""] * 7)

    def test_metrics_match_actual_utf8_sections(self):
        sections = dict(m.packet_sections(self.model["packet"]))
        for metric in self.model["metrics"]:
            block = sections[metric["case_id"]]
            self.assertEqual(metric["packet_line_count"], len(block.splitlines()))
            self.assertEqual(metric["packet_byte_count"], len(block.encode("utf-8")))
        self.assertLess(sum(r["packet_line_count"] for r in self.model["metrics"]), len(self.model["packet"].splitlines()))

    def test_source_row_order_does_not_change_packet(self):
        source = copy.deepcopy(self.source)
        for key in ("units", "evidence", "boundary", "relations", "provenance", "overlay", "contexts"):
            rows = m.source_rows(source, key)
            random.Random(71).shuffle(rows)
            set_csv(source, key, rows)
        remanifest(source)
        second = m.build_model(source)
        self.assertEqual(self.model["packet"], second["packet"])
        self.assertEqual(self.model["metrics"], second["metrics"])
        self.assertNotEqual(self.model["raw_relations"], second["raw_relations"])
        self.assertTrue(all(g["status"] == "PASS" for g in m.build_gates(second)))

    def test_case_order_is_preserved_not_sorted(self):
        source = copy.deepcopy(self.source)
        rows = list(reversed(m.source_rows(source, "cases")))
        set_csv(source, "cases", rows)
        remanifest(source)
        model = m.build_model(source)
        self.assertEqual([cid for cid, _ in m.packet_sections(model["packet"])], [r["case_id"] for r in rows])

    def test_cli_no_overwrite_manifest_and_packet_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "compact"
            args = ["--r3c1-zip", str(self.zip), "--output-dir", str(out)]
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(m.main(args), 0)
                manifest_bytes = (out / "99_manifest_sha256.csv").read_bytes()
                self.assertEqual(m.main(args), 2)
                self.assertEqual((out / "99_manifest_sha256.csv").read_bytes(), manifest_bytes)
            self.assertEqual(len(list(out.iterdir())), 14)
            self.assertEqual((out / "09_review_packet_compact.md").read_bytes(), self.model["packet"].encode("utf-8"))
            for r in m.csv_read(manifest_bytes, "manifest")[1]:
                payload = (out / r["file"]).read_bytes()
                self.assertEqual(m.sha(payload), r["sha256"])
                self.assertEqual(str(len(payload)), r["bytes"])
            meta = json.loads((out / "90_run_metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["source_r3c1_zip_sha256"], m.sha(self.zip.read_bytes()))
            self.assertFalse((out / "03_review_unit_population.csv").exists())

    def test_unsafe_or_ambiguous_archives_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("../99_manifest_sha256.csv", "/99_manifest_sha256.csv"):
                path = Path(tmp) / "bad.zip"
                with zipfile.ZipFile(path, "w") as archive:
                    archive.writestr(name, b"x")
                with self.subTest(name=name), self.assertRaises(m.ValidationError):
                    m.read_source(path)


if __name__ == "__main__":
    unittest.main()
