"""Small synthetic TF-shaped corpus; never a substitute for BHSA execution."""
from copy import deepcopy
import json
from types import SimpleNamespace

import milal_mr1_surface_marker_provenance as mr


def word(lexeme, pos="subs", function="Pred", **features):
    return dict(lex_utf8=lexeme, g_word_utf8=lexeme, lex=lexeme, pdp=pos, sp=pos,
                phrase_function=function, **features)


def verb(lexeme, **features):
    return word(lexeme, "verb", **dict(vt="perf", vs="qal", ps="p3", gn="m", nu="sg", **features))


def corpus(specs, rule_config=None):
    cfg = rule_config or json.loads(mr.CONFIG.read_text(encoding="utf-8"))["rule_config"]
    values, down, up, sections = {}, {}, {}, {}
    book = 1000000
    clauses, atoms, verses = [], [], []
    serial_word, serial_phrase, serial_atom = 1, 20000, 30000
    for i, spec in enumerate(specs):
        clause, verse = 10000 + i, 40000 + i
        sec = ["Job", 1, i + 1]
        clauses.append(clause)
        verses.append(verse)
        sections[clause] = sections[verse] = sec
        values[clause] = dict(otype="clause", domain=spec.get("domain", "N"), typ=spec.get("typ", "xYq0"), kind="Verbal")
        values[verse] = dict(otype="verse")
        ww, pp = [], []
        groups = {}
        for data in spec.get("words", [word("דבר")]):
            w = serial_word
            serial_word += 1
            ww.append(w)
            d = data.copy()
            fn = d.pop("phrase_function", "Pred")
            values[w] = dict(otype="word", **d)
            sections[w] = sec
            groups.setdefault(fn, []).append(w)
        for fn, pw in groups.items():
            p = serial_phrase
            serial_phrase += 1
            pp.append(p)
            values[p] = dict(otype="phrase", function=fn)
            sections[p] = sec
            down[p, "word"] = pw
            for w in pw:
                up[w, "phrase"] = [p]
        aa = []
        for j in range(spec.get("atoms", 1)):
            atom = serial_atom
            serial_atom += 1
            aa.append(atom)
            values[atom] = dict(otype="clause_atom")
            sections[atom] = sec
            down[atom, "word"] = ww[j::spec.get("atoms", 1)]
        atoms.extend(aa)
        down[clause, "word"], down[clause, "phrase"], down[clause, "clause_atom"] = ww, pp, aa
        down[verse, "clause"], down[verse, "clause_atom"], down[verse, "word"] = [clause], aa, ww
        for n in [clause] + aa + pp + ww:
            up[n, "verse"] = [verse]
            if n != clause:
                up[n, "clause"] = [clause]
    down[book, "clause"], down[book, "clause_atom"], down[book, "verse"] = clauses, atoms, verses
    feature_names = mr.FEATURES + ["otype"]
    features = SimpleNamespace(**{name: SimpleNamespace(v=lambda node, name=name: values[node].get(name)) for name in feature_names})
    api = SimpleNamespace(F=features, L=SimpleNamespace(d=lambda n, otype: tuple(down.get((n, otype), ())),
                                                       u=lambda n, otype: tuple(up.get((n, otype), ()))),
                          T=SimpleNamespace(sectionFromNode=lambda n: tuple(sections[n])))
    return mr.EvidenceBHSA(api, book, cfg)


def sample():
    return corpus([
        dict(typ="Way0", atoms=2, words=[verb("היה"), word("יום", function="Time")]),
        dict(words=[verb("אמר"), word("איוב", "nmpr", "Subj"), word("אליפז", "nmpr", "Cmpl")]),
        dict(domain="Q", words=[word("דבר")]),
        dict(words=[verb("תמם"), word("דבר")]),
        dict(typ="Way0", words=[verb("הלך")]),
    ])


def self_test_bundle():
    cfg = deepcopy(json.loads(mr.CONFIG.read_text(encoding="utf-8")))
    cfg.update(scope=["Job 1:1", "Job 1:5"], clause_count=5, clause_atom_count=6,
               historical_counts=dict(surface=5, csf=1, closure=1, way0=2),
               wayhi_positive_count=1, wayhi_negative_count=1, wayhi_positive_refs=["Job 1:1"],
               controls=["Job 1:1", "Job 1:2", "Job 1:4", "Job 1:5"])
    fixture = mr.ROOT / "tests/fixtures/mr1"
    baseline = {k: (fixture / f"{k}.csv").read_bytes() for k in mr.FILES}
    expected = {name: mr.sha(baseline[k]) for k, name in mr.FILES.items()}
    expected.update(source_script=cfg["source_script_sha256"], source_config=cfg["source_config_sha256"])
    source = dict(paths={}, hashes=expected.copy(), expected_hashes=expected, rule_config=cfg["rule_config"],
                  source_ast={r["identity"]: r["ast_sha256"] for r in cfg["methods"]},
                  metadata=dict(status="SYNTHETIC_FIXTURE_NOT_HISTORICAL_EVIDENCE"))
    execution = dict(mode="SYNTHETIC", bhsa_version="2021", feature_versions={"synthetic": "2021"}, tf_version="13.1.0", tf_loaded=True,
                     data_path="SYNTHETIC_API_NOT_ACTUAL_TEXT_FABRIC", data_hashes={})
    return mr.build(sample(), cfg, baseline, source, execution)
