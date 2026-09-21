"""MR1 rules, exact linkage, package integrity, and a mutation per computed gate."""
from copy import deepcopy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import milal_mr1_surface_marker_provenance as m
import milal_mr1_historical_rules as h
from milal_mr1_synthetic import corpus, word, verb, self_test_bundle

CFG = json.loads(m.CONFIG.read_text(encoding="utf-8"))


def analyze(specs):
    return h.Analyzer(corpus(specs), CFG["rule_config"])


class TestMR1Rules(unittest.TestCase):
    def test_closure_single(self):
        rows = analyze([dict(words=[word("תמם"), word("דבר")])]).closure_spans
        self.assertEqual([(r["start_clause"], r["end_clause"], r["width_clauses"]) for r in rows], [(10000, 10000, 1)])

    def test_closure_two_clauses(self):
        rows = analyze([dict(words=[word("תמם")]), dict(words=[word("דבר")])]).closure_spans
        self.assertEqual([(r["start_clause"], r["end_clause"]) for r in rows], [(10000, 10001)])

    def test_closure_ordered_subsequence(self):
        self.assertEqual(len(analyze([dict(words=[word("תמם"), word("איוב"), word("דבר")])]).closure_spans), 1)

    def test_closure_wrong_order(self):
        self.assertEqual(analyze([dict(words=[word("דבר"), word("תמם")])]).closure_spans, [])

    def test_closure_shortest_and_width_boundary(self):
        rows = analyze([{}, dict(words=[word("תמם"), word("דבר")])]).closure_spans
        self.assertEqual([(r["start_clause"], r["end_clause"]) for r in rows], [(10001, 10001)])
        self.assertEqual(analyze([dict(words=[word("תמם")]), dict(words=[word("בית")]), dict(words=[word("דבר")])]).closure_spans, [])

    def test_csf_simple_amr(self):
        a = analyze([dict(words=[verb("אמר"), word("איוב", "nmpr", "Subj")])])
        self.assertEqual(a.speech_events[0]["csf_family"], "SIMPLE_AMR")
        self.assertEqual(a.speech_events[0]["speaker_source_type"], "PROPER_NAME")

    def test_csf_anchor_later_amr(self):
        a = analyze([dict(words=[verb("ענה"), word("איוב", "nmpr", "Subj")]), dict(words=[verb("אמר")])])
        self.assertEqual(len(a.speech_events), 1)
        self.assertEqual(a.speech_events[0]["csf_family"], "ANSWER+AMR")
        self.assertEqual(a.speech_events[0]["formula_end_clause"], 10001)

    def test_csf_other_anchor_families(self):
        for lexemes, family in [(["יסף"], "ADD_SPEECH"), (["נשא", "משל"], "TAKE_MASHAL"), (["פתח", "פה"], "OPEN_MOUTH")]:
            with self.subTest(family=family):
                a = analyze([dict(words=[word(x) for x in lexemes] + [word("איוב", "nmpr", "Subj")]), dict(words=[verb("אמר")])])
                self.assertEqual(a.speech_events[0]["csf_family"], family + "+AMR")

    def test_csf_domain_rejection(self):
        self.assertEqual(analyze([dict(domain="Q", words=[verb("אמר"), word("איוב", "nmpr", "Subj")])]).speech_events, [])

    def test_csf_empty_speaker_excluded(self):
        self.assertEqual(analyze([dict(words=[word("אמר")])]).speech_events, [])

    def test_csf_png_anonymous_is_historical_inclusion(self):
        # Historical "unresolved" with PNG can yield an anonymous speaker;
        # only an empty resolver result is excluded. Do not invent stricter filtering.
        a = analyze([dict(words=[verb("אמר")])])
        self.assertEqual(a.speech_events[0]["speaker_source_type"], "IMPLICIT_UNRESOLVED_BY_PNG")

    def test_csf_addressee_profile_not_scope(self):
        a = analyze([dict(words=[verb("אמר"), word("איוב", "nmpr", "Subj"), word("אליפז", "nmpr", "Cmpl")])])
        e = a.speech_events[0]
        self.assertEqual(e["named_addressees"], ["אליפז"])
        self.assertEqual(e["csf_profile"], "EXPANDED")
        self.assertEqual(e["csf_scope_profile"], "CORE")

    def test_csf_expanded_scope(self):
        a = analyze([dict(words=[verb("אמר"), word("איוב", "nmpr", "Subj"), word("יום", function="Time")])])
        self.assertEqual(a.speech_events[0]["csf_scope_profile"], "SCOPE_EXPANDED")

    def test_csf_lookahead_boundary(self):
        first = dict(words=[word("ענה"), word("איוב", "nmpr", "Subj")])
        for distance, expected in ((3, True), (4, False)):
            a = analyze([first] + [dict(words=[word("בית")])] * (distance - 1) + [dict(words=[verb("אמר")])])
            self.assertEqual(any(e["csf_family"] == "ANSWER+AMR" for e in a.speech_events), expected)

    def test_csf_implicit_lookback(self):
        a = analyze([dict(words=[word("איוב", "nmpr", "Subj")]), dict(words=[verb("אמר")])])
        self.assertEqual(a.speech_events[0]["speaker_source_type"], "IMPLICIT_FROM_PREVIOUS_NARRATOR_SUBJECT")

    def test_way0_positive_no_frame_still_positive(self):
        a = analyze([dict(typ="Way0", words=[verb("היה")])])
        self.assertTrue(a.wayhi_profile(10000)["is_wayhi"])
        self.assertFalse(a.wayhi_profile(10000)["wayhi_frame"])

    def test_wayx_not_wayhi(self):
        a = analyze([dict(typ="WayX", words=[verb("היה")])])
        self.assertFalse(a.wayhi_profile(10000)["is_wayhi"])
        self.assertEqual(a.wayhi_rows(), [])

    def test_wayhi_morphology(self):
        for feature, value in [("ps", "p1"), ("gn", "f"), ("nu", "pl"), ("vt", "infc"), ("vt", "ptca")]:
            with self.subTest(feature=feature, value=value):
                v = verb("היה"); v[feature] = value
                a = analyze([dict(typ="Way0", words=[v])])
                self.assertFalse(a.wayhi_profile(10000)["is_wayhi"])

    def test_wayhi_time_phrase(self):
        a = analyze([dict(typ="Way0", words=[verb("היה"), word("יום", function="Time")])])
        self.assertTrue(a.wayhi_profile(10000)["wayhi_frame"])

    def test_wayhi_location(self):
        a = analyze([dict(typ="Way0", words=[verb("היה"), word("בית", function="Loca")])])
        self.assertEqual(a.wayhi_profile(10000)["wayhi_place_refs"], ["Job 1:1"])

    def test_wayhi_q_excludes_frame_not_core(self):
        a = analyze([dict(typ="Way0", domain="Q", words=[verb("היה"), word("יום", function="Time")])])
        self.assertTrue(a.wayhi_profile(10000)["is_wayhi"])
        self.assertFalse(a.wayhi_profile(10000)["wayhi_frame"])

    def test_wayhi_lookahead_boundary(self):
        for distance, expected in ((3, True), (4, False)):
            a = analyze([dict(typ="Way0", words=[verb("היה")])] + [{}] * (distance - 1) + [dict(words=[word("יום", function="Time")])])
            self.assertEqual(a.wayhi_profile(10000)["wayhi_frame"], expected)

    def test_temporal_auxiliary_includes_nonfinite(self):
        for vt in ("perf", "infc", "infa", "ptca", "ptcp"):
            v = verb("הלך"); v["vt"] = vt
            a = analyze([dict(words=[word("אחר", "prep"), v])])
            self.assertTrue(a.temporal_construction(10000)[0], vt)

    def test_temporal_auxiliary_blank_na_rejected(self):
        for vt in ("", "NA"):
            v = verb("הלך"); v["vt"] = vt
            self.assertFalse(analyze([dict(words=[word("אחר", "prep"), v])]).temporal_construction(10000)[0])

    def test_temporal_first_three_allowed_pos(self):
        for words, expected in [([word("אחר", "adjv"), verb("הלך")], False), ([word("אחר", "prep"), word("בית")], False),
                                ([word("בית")] * 3 + [word("אחר", "prep"), verb("הלך")], False),
                                ([word("בית")] * 2 + [word("אחר", "prep"), verb("הלך")], True)]:
            self.assertEqual(analyze([dict(words=words)]).temporal_construction(10000)[0], expected)


class TestMR1Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle = self_test_bundle()

    def test_all_positive_gates(self):
        self.assertTrue(all(r["status"] == "PASS" for r in m.gates(self.bundle)))

    def test_fixture_independent_expected_properties(self):
        t = self.bundle["model"]["tables"]
        self.assertEqual({k: len(v) for k, v in t.items()}, dict(surface=5, csf=1, closure=1, way0=2))
        self.assertEqual(t["closure"][0]["pattern"], "תממ+דבר")
        self.assertEqual(t["closure"][0]["start_clause"], 10003)
        self.assertEqual(t["csf"][0]["named_addressees"], "אליפז")
        self.assertEqual(t["csf"][0]["csf_scope_profile"], "CORE")
        self.assertEqual([r["wayhi_meta"] for r in t["way0"]], [True, False])

    def test_mapping_single_multi_order(self):
        links = self.bundle["model"]["links"]
        self.assertEqual(links[0]["ordered_clause_atom_ids"], [30000, 30001])
        self.assertEqual(links[1]["ordered_clause_atom_ids"], [30002])
        self.assertEqual(len(links), 9)

    def test_exact_comparison(self):
        self.assertEqual({r["match_status"] for r in self.bundle["audit"]}, {"EXACT"})

    def test_fixture_historical_schema_bytes(self):
        for kind, rows in self.bundle["model"]["tables"].items():
            self.assertEqual(m.csv_bytes(rows), self.bundle["baseline"][kind], kind)

    def test_field_difference(self):
        rows = deepcopy(self.bundle["model"]["tables"]["surface"])
        rows[0]["text"] = "changed"
        audit = m.compare("surface", rows, self.bundle["baseline"]["surface"])
        self.assertEqual(audit[0]["match_status"], "FIELD_DIFFERENCE")
        self.assertEqual(audit[0]["differing_fields"], ["text"])

    def test_historical_current_only_no_fuzzy(self):
        rows = deepcopy(self.bundle["model"]["tables"]["surface"])
        rows[0]["clause_node"] = 99999  # Same text and reference must NOT rescue the ID.
        audit = m.compare("surface", rows, self.bundle["baseline"]["surface"])
        self.assertEqual(sum(r["match_status"] == "CURRENT_ONLY" for r in audit), 1)
        self.assertEqual(sum(r["match_status"] == "HISTORICAL_ONLY" for r in audit), 1)

    def test_duplicate_identity_stops(self):
        rows = deepcopy(self.bundle["model"]["tables"]["surface"])
        with self.assertRaisesRegex(ValueError, "AMBIGUOUS"):
            m.compare("surface", rows + [rows[0]], self.bundle["baseline"]["surface"])

    def test_schema_missing_stops(self):
        rows = deepcopy(self.bundle["model"]["tables"]["surface"])
        del rows[0]["domain"]
        with self.assertRaisesRegex(ValueError, "SCHEMA_ERROR"):
            m.compare("surface", rows, self.bundle["baseline"]["surface"])

    def test_csf_identity_checks_coordinates(self):
        rows = deepcopy(self.bundle["model"]["tables"]["csf"])
        rows[0]["formula_end_ref"] = "Job 99:99"
        row = m.compare("csf", rows, self.bundle["baseline"]["csf"])[0]
        self.assertFalse(row["identity_equal"])
        self.assertEqual(row["match_status"], "FIELD_DIFFERENCE")

    def test_exact_ast_negative(self):
        path = Path(h.__file__)
        original = path.read_text(encoding="utf-8-sig")
        before = m.ast_entries(original)
        after = m.ast_entries(original.replace('not in {"", "NA"} for x in words', 'not in {"", "NA", "ptca"} for x in words'))
        self.assertNotEqual(before["Analyzer.temporal_construction"], after["Analyzer.temporal_construction"])

    def test_manifest_mutation(self):
        files = m.render(self.bundle)
        self.assertEqual(m.manifest_gate(files)["status"], "PASS")
        files["02_csf_reproduction.csv"] += b"x"
        self.assertEqual(m.manifest_gate(files)["status"], "FAIL")

    def test_manifest_extra_and_missing_member(self):
        for change in ("extra", "missing"):
            files = m.render(self.bundle)
            if change == "extra":
                files["unlisted.txt"] = b"x"
            else:
                del files["02_csf_reproduction.csv"]
            self.assertFalse(m.manifest_ok(files))

    def test_byte_determinism_and_publish(self):
        first, second = m.render(self.bundle), m.render(self_test_bundle())
        self.assertEqual(first, second)
        with tempfile.TemporaryDirectory() as tmp:
            result, zipped, log = m.publish(first, Path(tmp) / "run")
            self.assertTrue(result)
            self.assertTrue(zipped.is_file() and log.is_file())
            with self.assertRaisesRegex(ValueError, "already exists"):
                m.publish(first, Path(tmp) / "run")


def mutate_gate(b, name):
    model, run = b["model"], b["execution"]
    if name == "BHSA_VERSION": run["bhsa_version"] = "2017"
    elif name == "TF_LOAD": run["tf_loaded"] = False
    elif name == "FULL_SCOPE": model["scope"][1] = "Job 1:4"
    elif name == "CLAUSE_COUNT": model["clauses"].pop()
    elif name == "ATOM_COUNT": model["atoms"].pop()
    elif name == "ATOM_MEMBERSHIP": model["links"][0]["clause_atom_count"] = 0
    elif name == "ATOM_ORDER": model["links"][0]["ordered_clause_atom_ids"].reverse()
    elif name == "SOURCE_FINGERPRINTS": b["source"]["hashes"]["source_script"] = "bad"
    elif name == "CSV_FINGERPRINTS": b["source"]["expected_hashes"][m.FILES["surface"]] = "bad"
    elif name in {"CLOSURE_PROVENANCE", "CSF_PROVENANCE", "WAYHI_PROVENANCE"}:
        b["rule_checks"][m.RULES[{"CLOSURE_PROVENANCE": "closure", "CSF_PROVENANCE": "csf", "WAYHI_PROVENANCE": "way0"}[name]]] = False
    elif name == "COMPLETE_RULE_PROVENANCE": b["extra_methods"].append("Analyzer.make_hierarchy")
    elif name == "TEMPORAL_AUXILIARY": b["rule_checks"]["Analyzer.temporal_construction"] = False
    elif name == "NO_FINITE_ONLY_AUXILIARY": b["source"]["source_ast"]["Analyzer.temporal_construction"] = "finite-only-mutation"
    elif name == "NO_WAYX_SHORTCUT": model["tables"]["way0"][0]["clause_type"] = "WayX"
    elif name == "NO_FUZZY_MATCHING": b["audit"][0]["join_key"] = ["different"]
    elif name == "DETERMINISTIC_RERUN": b["repeat"]["tables"]["surface"][0]["text"] = "different"
    elif name == "COMPARISON_PERFORMED": b["audit"] = [r for r in b["audit"] if r["kind"] != "closure"]
    elif name == "COUNTS": model["tables"]["csf"].pop()
    elif name == "IDENTITIES": b["audit"][0]["identity_equal"] = False
    elif name == "FIELD_EQUALITY": b["audit"][0]["match_status"] = "FIELD_DIFFERENCE"
    elif name == "UNMATCHED_ROWS": b["audit"][0]["match_status"] = "HISTORICAL_ONLY"
    elif name == "WAY0_AUDIT_COUNT": model["tables"]["way0"].pop()
    elif name == "WAYHI_POSITIVE_COUNT": model["tables"]["way0"][0]["wayhi_meta"] = False
    elif name == "WAYHI_NEGATIVE_COUNT": model["tables"]["way0"][1]["wayhi_meta"] = True
    elif name == "WAYHI_POSITIVE_IDENTITIES": model["tables"]["way0"][0]["ref"] = "Job 99:99"
    elif name == "ALL_WAY0_RESOLVE": next(r for r in b["audit"] if r["kind"] == "way0")["identity_equal"] = False
    elif name in {"NO_HIERARCHY", "NO_PARENTAGE", "NO_NEW_INTERPRETATION"}:
        model["records"]["surface"][0][{"NO_HIERARCHY": "hierarchy", "NO_PARENTAGE": "mother", "NO_NEW_INTERPRETATION": "rhetorical_label"}[name]] = "forbidden"
    elif name == "EVENT_PROVENANCE": model["records"]["surface"][0]["source_script_sha256"] = "bad"
    else: raise AssertionError("Missing negative mutation: " + name)


class TestMR1GateMutations(unittest.TestCase):
    pass


def gate_test(name):
    def test(self):
        bundle = self_test_bundle()
        mutate_gate(bundle, name)
        result = {r["gate"]: r["status"] for r in m.gates(bundle)}
        self.assertEqual(result[name], "FAIL", name)
    return test


for gate in m.gates(self_test_bundle()):
    setattr(TestMR1GateMutations, "test_negative_" + gate["gate"].lower(), gate_test(gate["gate"]))


if __name__ == "__main__":
    unittest.main()
