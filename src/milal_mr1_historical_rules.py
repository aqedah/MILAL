"""MR1 historical v5.2.5 marker-behavior subset.

Only the dependency closure of the four marker-table writers is transcribed.
No legacy loader, CLI, hierarchy, mother assignment, macro-unit composition,
convergence, or final-boundary engine is included. Speaker/participant values
are historical-comparison fields, not newly accepted discourse interpretations.
See config/mr1_job.json for source fingerprint, line locators and AST digests.
"""
from __future__ import annotations
import json
import re
import unicodedata
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

HEB_LETTERS = re.compile(r"[\u05D0-\u05EA]+")

FINAL_TO_MEDIAL = str.maketrans({"ך": "כ", "ם": "מ", "ן": "נ", "ף": "פ", "ץ": "צ"})

def norm_hebrew(s: Any) -> str:
    if s is None:
        return ""
    x = unicodedata.normalize("NFD", str(s))
    x = "".join(HEB_LETTERS.findall(x))
    return x.translate(FINAL_TO_MEDIAL)

def csv_join(values: Iterable[Any]) -> str:
    return "|".join(str(v) for v in values if v not in (None, "", []))

def ordered_unique(values: Iterable[Any]) -> List[Any]:
    out, seen = [], set()
    for v in values:
        if v not in seen:
            seen.add(v)
            out.append(v)
    return out

class BHSA:
    def f(self, name: str, node: int, default: Any = "") -> Any:
        try:
            feat = getattr(self.F, name)
            val = feat.v(node)
            return default if val is None else val
        except Exception:
            return default

    def down(self, node: int, otype: str) -> List[int]:
        try:
            return list(self.L.d(node, otype=otype))
        except Exception:
            return []

    def up(self, node: int, otype: str) -> List[int]:
        try:
            return list(self.L.u(node, otype=otype))
        except Exception:
            return []

    def otype(self, node: int) -> str:
        return str(self.f("otype", node, ""))

    def words(self, node: int) -> List[int]:
        return self.down(node, "word")

    def phrases(self, clause: int) -> List[int]:
        return self.down(clause, "phrase")

    def clause_atoms(self, clause: int) -> List[int]:
        return self.down(clause, "clause_atom")

    def verse_node(self, node: int) -> Optional[int]:
        if self.otype(node) == "verse":
            return node
        ups = self.up(node, "verse")
        return ups[0] if ups else None

    def section(self, node: int) -> Tuple[Any, ...]:
        try:
            return tuple(self.T.sectionFromNode(node))
        except Exception:
            return tuple()

    def ref(self, node: Optional[int]) -> str:
        if node is None:
            return ""
        sec = self.section(node)
        if len(sec) >= 3:
            return f"{sec[0]} {sec[1]}:{sec[2]}"
        if len(sec) == 2:
            return f"{sec[0]} {sec[1]}"
        return str(node)

    def cv(self, node: int) -> Tuple[int, int]:
        sec = self.section(node)
        if len(sec) >= 3:
            return int(sec[1]), int(sec[2])
        return (-1, -1)

    def lex(self, word: int) -> str:
        for feat in ("lex_utf8", "g_word_utf8"):
            nv = norm_hebrew(self.f(feat, word, ""))
            if nv:
                return nv
        return norm_hebrew(self.f("lex", word, ""))

    def surface(self, word: int) -> str:
        return str(self.f("g_word_utf8", word, ""))

    def text(self, node: int) -> str:
        return " ".join(self.surface(w) for w in self.words(node)).strip()

    def pos(self, word: int) -> str:
        return str(self.f("pdp", word, "") or self.f("sp", word, ""))

    def lexemes(self, node: int) -> List[str]:
        return [self.lex(w) for w in self.words(node) if self.lex(w)]

    def content_lexemes(self, node: int, content_pos: Set[str]) -> List[str]:
        return [self.lex(w) for w in self.words(node) if self.pos(w) in content_pos and self.lex(w)]

    def proper_names(self, node: int) -> List[str]:
        return [self.lex(w) for w in self.words(node) if self.pos(w) == "nmpr" and self.lex(w)]

    def phrase_functions(self, clause: int) -> List[str]:
        return [str(self.f("function", p, "")) for p in self.phrases(clause)]

    def phrase_of_word(self, word: int) -> Optional[int]:
        ups = self.up(word, "phrase")
        return ups[0] if ups else None

    def phrase_function_of_word(self, word: int) -> str:
        p = self.phrase_of_word(word)
        return str(self.f("function", p, "")) if p else ""

    def subject_names(self, clause: int) -> List[str]:
        out: List[str] = []
        for p in self.phrases(clause):
            if self.f("function", p, "") == "Subj":
                out.extend(self.proper_names(p))
        return out

    def subject_phrase(self, clause: int) -> Optional[int]:
        for p in self.phrases(clause):
            if self.f("function", p, "") == "Subj":
                return p
        return None

    def subject_label(self, clause: int) -> Tuple[str, str]:
        """Return (speaker label, source type) for explicit Subject phrases.

        Proper names are preferred. If none is present, a common-noun head-like
        lexical item is used so role speakers such as אשתו / מלאך are not lost.
        """
        p = self.subject_phrase(clause)
        if not p:
            return "", ""
        names = self.proper_names(p)
        if names:
            return names[0], "PROPER_NAME"
        # Prefer substantive/pronominal lexical material over articles/prepositions.
        for w in self.words(p):
            if self.pos(w) in {"subs", "prps"}:
                lx = self.lex(w)
                if lx:
                    return lx, "ROLE_OR_COMMON_NOUN"
        for w in self.words(p):
            lx = self.lex(w)
            if lx:
                return lx, "SUBJECT_PHRASE_LEXEME"
        return "", ""

    def proper_name_type(self, word: int) -> str:
        return str(self.f("nametype", word, ""))

    def vocative_names(self, clause: int) -> List[str]:
        out = []
        for p in self.phrases(clause):
            if self.f("function", p, "") == "Voct":
                out.extend(self.proper_names(p))
        return ordered_unique(out)

    def png(self, word: int, prefix: str = "") -> str:
        if prefix == "prs_":
            ps, gn, nu = self.f("prs_ps", word, ""), self.f("prs_gn", word, ""), self.f("prs_nu", word, "")
        else:
            ps, gn, nu = self.f("ps", word, ""), self.f("gn", word, ""), self.f("nu", word, "")
        if all(x in ("", "NA", "unknown") for x in (ps, gn, nu)):
            return ""
        return f"{ps}:{gn}:{nu}"

    def finite_verbs(self, clause: int) -> List[int]:
        out = []
        for w in self.words(clause):
            if self.pos(w) != "verb":
                continue
            vt = str(self.f("vt", w, ""))
            if vt not in {"", "NA", "infc", "infa", "ptca", "ptcp"}:
                out.append(w)
        return out

    def actor_png_profile(self, clause: int) -> str:
        # Prefer finite verbal inflection: especially useful in poetry where subjects are often implicit.
        for w in self.finite_verbs(clause):
            p = self.png(w)
            if p:
                return p
        # Fall back to explicit subject morphology.
        for pnode in self.phrases(clause):
            if self.f("function", pnode, "") == "Subj":
                for w in self.words(pnode):
                    p = self.png(w)
                    if p:
                        return p
        return ""

    def verb_forms(self, clause: int) -> Tuple[str, ...]:
        return tuple(str(self.f("vt", w, "")) for w in self.words(clause) if self.pos(w) == "verb" and self.f("vt", w, ""))

    def has_phrase_function(self, clause: int, fn: str) -> bool:
        return fn in self.phrase_functions(clause)

    def time_phrases(self, clause: int) -> List[int]:
        return [p for p in self.phrases(clause) if self.f("function", p, "") == "Time"]

    def locative_phrases(self, clause: int) -> List[int]:
        return [p for p in self.phrases(clause) if self.f("function", p, "") == "Loca"]

    def has_imperative(self, clause: int) -> bool:
        if any(self.f("vt", w, "") == "impv" for w in self.words(clause)):
            return True
        return "Im" in str(self.f("typ", clause, ""))

    def has_question(self, clause: int) -> bool:
        if self.has_phrase_function(clause, "Ques"):
            return True
        for w in self.words(clause):
            if self.pos(w) in {"prin", "inrg"} or self.f("ls", w, "") == "ques":
                return True
        return False

    def has_vocative(self, clause: int) -> bool:
        return self.has_phrase_function(clause, "Voct") or str(self.f("typ", clause, "")) == "Voct"

    def is_msyn(self, clause: int) -> bool:
        return str(self.f("typ", clause, "")) == "MSyn"

    def domain(self, clause: int) -> str:
        return str(self.f("domain", clause, ""))

    def is_way0(self, clause: int) -> bool:
        return str(self.f("typ", clause, "")) == "Way0"

    def is_wayx(self, clause: int) -> bool:
        return str(self.f("typ", clause, "")) == "WayX"

    def verse_distance(self, a: int, b: int) -> Optional[int]:
        va, vb = self.verse_node(a), self.verse_node(b)
        if va is None or vb is None:
            return None
        return abs(self.verse_pos[vb] - self.verse_pos[va])

class Analyzer:
    def __init__(self, b: BHSA, cfg: Dict[str, Any]):
        self.b = b
        self.cfg = cfg
        self.content_pos = set(cfg["content_pos"])
        self.discourse_markers = {norm_hebrew(x) for x in cfg["discourse_markers"]}
        self.subordinators = {norm_hebrew(x) for x in cfg["subordinator_lexemes"]}
        self.temporal_lexemes = {norm_hebrew(x) for x in cfg["temporal_construction_lexemes"]}
        self.temporal_allowed_pos = set(cfg["temporal_allowed_pos"])
        self.closure_patterns = [[norm_hebrew(x) for x in p] for p in cfg["closure_patterns"]]
        self.speech_anchors = {k: [norm_hebrew(x) for x in v] for k, v in cfg["speech_anchor_patterns"].items()}
        self._anonymous_speaker_counter = 0

        # Closure spans are independent of speech detection and can therefore be
        # available when speech level (top-level vs embedded/reported) is classified.
        self.closure_spans = self._detect_closure_spans()

        # All speech events are retained for audit, but only TOP_LEVEL_CSF events
        # control the outer speaker, top-level turn sequence, macro transitions,
        # and primary segment boundaries.
        self.speech_events = self._detect_csf_turns()
        self.csf_turns = [e for e in self.speech_events if e.get("speech_level") == "TOP_LEVEL_CSF"]
        self.speech_event_start_map = {e["start_clause"]: e for e in self.speech_events}
        self.embedded_speech_start_map = {e["start_clause"]: e for e in self.speech_events if e.get("speech_level") != "TOP_LEVEL_CSF"}
        self.csf_start_map = {t["start_clause"]: t for t in self.csf_turns}
        self.csf_content_map = {t["content_start_clause"]: t for t in self.csf_turns if t.get("content_start_clause")}
        self.turn_by_id = {int(t["turn_id"]): t for t in self.csf_turns}
        self._annotate_turn_sequence()
        self.speaker_by_clause = self._propagate_speaker()
        self.turn_id_by_clause = self._propagate_turn_id()
        self.participant_rows, self.participant_clause_sets = self._build_participant_tables()
        self.participant_set_map = {r["clause_node"]: set(filter(None, str(r.get("entity_participant_set", "")).split("|"))) for r in self.participant_clause_sets}
        self.actor_png_map = {c: self.b.actor_png_profile(c) for c in self.b.clauses}

    @staticmethod
    def contains_ordered(lexs: Sequence[str], pattern: Sequence[str]) -> bool:
        if not pattern:
            return False
        j = 0
        for x in lexs:
            if x == pattern[j]:
                j += 1
                if j == len(pattern):
                    return True
        return False

    def clause_index(self, c: int) -> int:
        return self.b.clause_pos[c]

    def is_narrator_clause(self, c: int) -> bool:
        return self.b.domain(c) == "N"

    def is_discourse_marker(self, c: int) -> bool:
        return bool(set(self.b.lexemes(c)) & self.discourse_markers)

    def temporal_construction(self, c: int) -> Tuple[bool, str]:
        if self.b.time_phrases(c):
            return True, "TIME_FUNCTION"
        words = self.b.words(c)
        if not words:
            return False, ""
        for w in words[:3]:
            lx = self.b.lex(w)
            pos = self.b.pos(w)
            if lx not in self.temporal_lexemes:
                continue
            if pos == "adjv" or pos not in self.temporal_allowed_pos:
                continue
            has_event_verb = any(self.b.pos(x) == "verb" and self.b.f("vt", x, "") not in {"", "NA"} for x in words)
            if has_event_verb:
                return True, f"TEMPORAL_CONSTRUCTION:{lx}"
        return False, ""

    def place_marker(self, c: int) -> Tuple[bool, str]:
        locs = self.b.locative_phrases(c)
        if locs:
            return True, "LOCA_FUNCTION"
        return False, ""

    def _anchor_type(self, c: int, window: List[int]) -> str:
        first = self.b.lexemes(c)
        all_lex = [lx for x in window for lx in self.b.lexemes(x)]
        if all(x in first for x in self.speech_anchors["OPEN_MOUTH"]):
            return "OPEN_MOUTH"
        if self.contains_ordered(all_lex, self.speech_anchors["TAKE_MASHAL"]):
            return "TAKE_MASHAL"
        if self.speech_anchors["ANSWER"][0] in first:
            return "ANSWER"
        if self.speech_anchors["ADD_SPEECH"][0] in first:
            return "ADD_SPEECH"
        return ""

    def _formula_expansion(
        self,
        nodes: List[int],
        speaker: str,
        subject_names: List[str],
        family: str = "",
    ) -> Dict[str, Any]:
        """
        Describe expansion of a Character Speech Formula.

        v5.1:
        - speech-formula lexemes are never interpreted as addressees;
        - proper-name addressees remain valid in Objc/Cmpl/Voct;
        - common-noun / role addressees remain possible when they are not part
          of the active CSF formula;
        - addressee inference is auditable.

        This fixes Job 27:1 / 29:1, where משל belongs to TAKE_MASHAL and must
        not be classified as an addressee.
        """
        addressees: List[str] = []
        addressee_evidence: List[str] = []
        rejected_formula_addressee_lexemes: List[str] = []
        adjunct_details: List[str] = []

        family_head = str(
            family
        ).split("+", 1)[0]

        formula_lexemes: Set[str] = {
            norm_hebrew("אמר")
        }

        if family_head in self.speech_anchors:
            formula_lexemes.update(
                norm_hebrew(x)
                for x in self.speech_anchors[
                    family_head
                ]
            )

        for c in nodes:
            for p in self.b.phrases(c):
                fn = str(
                    self.b.f(
                        "function",
                        p,
                        "",
                    )
                )
                pnames = self.b.proper_names(
                    p
                )

                if fn in {
                    "Objc",
                    "Cmpl",
                    "Voct",
                }:
                    if pnames:
                        for n in pnames:
                            if n == speaker:
                                continue
                            addressees.append(n)
                            addressee_evidence.append(
                                f"{fn}:PROPER_NAME:{n}"
                            )
                    else:
                        for w in self.b.words(p):
                            if self.b.pos(w) not in {
                                "subs",
                                "prps",
                            }:
                                continue

                            lx = self.b.lex(w)
                            nlx = norm_hebrew(lx)

                            if not lx or lx == speaker:
                                continue

                            if nlx in formula_lexemes:
                                rejected_formula_addressee_lexemes.append(
                                    lx
                                )
                                continue

                            addressees.append(lx)
                            addressee_evidence.append(
                                f"{fn}:COMMON_OR_ROLE:{lx}"
                            )
                            break

                    if fn in {
                        "Objc",
                        "Voct",
                    }:
                        continue

                if (
                    fn
                    and fn
                    not in {
                        "Pred",
                        "PreC",
                        "Subj",
                        "Conj",
                        "Objc",
                        "Voct",
                        "Cmpl",
                    }
                ):
                    adjunct_details.append(
                        f"{fn}:{self.b.text(p)}"
                    )

                elif (
                    fn == "Cmpl"
                    and not pnames
                ):
                    has_person_like = any(
                        self.b.pos(w)
                        in {
                            "subs",
                            "prps",
                        }
                        and norm_hebrew(
                            self.b.lex(w)
                        )
                        not in formula_lexemes
                        for w in self.b.words(p)
                    )

                    if not has_person_like:
                        adjunct_details.append(
                            f"{fn}:{self.b.text(p)}"
                        )

        addressees = ordered_unique(
            addressees
        )
        addressee_evidence = ordered_unique(
            addressee_evidence
        )
        rejected_formula_addressee_lexemes = ordered_unique(
            rejected_formula_addressee_lexemes
        )

        speaker_identification_expanded = (
            len(subject_names) > 1
        )

        expanded = bool(
            addressees
            or adjunct_details
            or speaker_identification_expanded
        )

        # v5.1 scope profile: explicit speaker/addressee belongs to the core
        # speech formula.  Adjuncts or expanded speaker-identification are
        # treated as scope-expanding material.  This is deliberately distinct
        # from `csf_profile`, whose EXPANDED value also includes addressees.
        scope_evidence: List[str] = []
        if adjunct_details:
            scope_evidence.extend(
                f"ADJUNCT:{x}"
                for x in adjunct_details
            )
        if speaker_identification_expanded:
            scope_evidence.append(
                "SPEAKER_IDENTIFICATION"
            )
        csf_scope_profile = (
            "SCOPE_EXPANDED"
            if scope_evidence
            else "CORE"
        )

        components: List[str] = []

        if speaker_identification_expanded:
            components.append(
                "SPEAKER_IDENTIFICATION"
            )

        if addressees:
            components.append(
                "EXPLICIT_ADDRESSEE"
            )

        if adjunct_details:
            components.append(
                "ADJUNCT"
            )

        return {
            "named_addressees": addressees,
            "addressee_evidence": (
                addressee_evidence
            ),
            "rejected_formula_addressee_lexemes": (
                rejected_formula_addressee_lexemes
            ),
            "adjunct_details": (
                adjunct_details
            ),
            "speaker_identification_expanded": (
                speaker_identification_expanded
            ),
            "csf_profile": (
                "EXPANDED"
                if expanded
                else "BASIC"
            ),
            "csf_scope_profile": csf_scope_profile,
            "csf_scope_evidence": ordered_unique(
                scope_evidence
            ),
            "csf_expansion_components": (
                components
            ),
        }

    def _new_anonymous_speaker(self, base: str = "ANON_SPEAKER") -> str:
        self._anonymous_speaker_counter += 1
        clean = norm_hebrew(base) or "ANON_SPEAKER"
        return f"{clean}_{self._anonymous_speaker_counter}"

    def _subject_demonstrative_label(self, clause: int) -> str:
        p = self.b.subject_phrase(clause)
        if not p:
            return ""
        for w in self.b.words(p):
            lx = self.b.lex(w)
            if self.b.pos(w) in {"prde", "prin"} or lx in {norm_hebrew("זה"), norm_hebrew("זאת"), norm_hebrew("אלה")}:
                return lx or "ANON"
        return ""

    def _recent_matching_named_entity(self, current_clause: int, actor_png: str, exclude: Set[str]) -> str:
        """Conservatively resolve an omitted 3rd-person speaker from recent explicit names.

        Only proper names with matching gender/number are considered. The result is used
        only when exactly one candidate survives, preventing silent over-resolution.
        """
        if not actor_png:
            return ""
        parts = actor_png.split(":")
        if len(parts) != 3:
            return ""
        _, gn, nu = parts
        i = self.clause_index(current_clause)
        max_back = int(self.cfg.get("implicit_speaker_entity_lookback_clauses", 12))
        for j in range(i - 1, max(-1, i - max_back - 1), -1):
            c = self.b.clauses[j]
            local_candidates: List[str] = []
            for w in self.b.words(c):
                if self.b.pos(w) != "nmpr":
                    continue
                name = self.b.lex(w)
                if not name or name in exclude:
                    continue
                nt = self.b.proper_name_type(w)
                if nt in {"loca", "topo", "geog"}:
                    continue
                wgn, wnu = str(self.b.f("gn", w, "")), str(self.b.f("nu", w, ""))
                if gn not in {"", "unknown", "NA"} and wgn not in {"", "unknown", "NA", gn}:
                    continue
                if nu not in {"", "unknown", "NA"} and wnu not in {"", "unknown", "NA", nu}:
                    continue
                local_candidates.append(name)
            uniq = ordered_unique(local_candidates)
            if len(uniq) == 1:
                return uniq[0]
            if len(uniq) > 1:
                return ""
        return ""

    def _implicit_speaker_from_context(
        self,
        clauses: List[int],
        i: int,
        current_clause: int,
        outer_speaker: str = "",
        outer_addressees: Optional[List[str]] = None,
    ) -> Tuple[str, str, Optional[int]]:
        """Resolve an omitted speech subject without allowing an embedded quote to
        overwrite the outer speaker. Person is used before distant name matching.
        """
        outer_addressees = outer_addressees or []
        actor = self.b.actor_png_profile(current_clause)

        # First person in an ongoing top-level speech is normally self-quotation.
        if actor.startswith("p1:") and outer_speaker:
            return outer_speaker, "IMPLICIT_SELF_QUOTE_P1", None

        # Second person normally quotes/reports the addressee's words. Do not search
        # for a distant proper name and silently convert this into a new top-level speaker.
        if actor.startswith("p2:"):
            if len(outer_addressees) == 1:
                return outer_addressees[0], "IMPLICIT_ADDRESSEE_QUOTE_P2", None
            return self._new_anonymous_speaker("ADDRESSEE_QUOTE"), "IMPLICIT_ADDRESSEE_QUOTE_P2", None

        max_back = int(self.cfg.get("csf_implicit_speaker_lookback_clauses", 2))
        for d in range(1, max_back + 1):
            j = i - d
            if j < 0:
                break
            p = clauses[j]
            if self.b.domain(p) == "Q":
                break
            label, source_type = self.b.subject_label(p)
            if label:
                if source_type == "PROPER_NAME":
                    return label, "IMPLICIT_FROM_PREVIOUS_NARRATOR_SUBJECT", p
                return self._new_anonymous_speaker(label), "IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT", p
            demo = self._subject_demonstrative_label(p)
            if demo:
                return self._new_anonymous_speaker(demo), "IMPLICIT_ANONYMOUS_FROM_PREVIOUS_SUBJECT", p

        # Name matching is permitted only for omitted third-person subjects.
        if actor.startswith("p3:"):
            exclude = {outer_speaker} if outer_speaker else set()
            resolved = self._recent_matching_named_entity(current_clause, actor, exclude)
            if resolved:
                return resolved, "IMPLICIT_RECENT_MATCHING_NAME", None

        if actor:
            return self._new_anonymous_speaker("IMPLICIT_SPEAKER"), "IMPLICIT_UNRESOLVED_BY_PNG", None
        return "", "", None

    def _speech_reset_evidence(self, clause: int) -> List[str]:
        """Strong frame evidence that can lift a SIMPLE_AMR event to top-level.

        This is deliberately conservative. It uses only non-Q material immediately
        around the formula plus explicit closure, Wayhi, time or place reset.
        """
        i = self.clause_index(clause)
        back = int(self.cfg.get("macro_cluster_back_clauses", 4))
        nodes = self.b.clauses[max(0, i - back):i + 1]
        ev: List[str] = []
        if self.recent_closures(clause):
            ev.append("EXPLICIT_CLOSURE")
        for c in nodes:
            if self.b.domain(c) == "Q":
                continue
            if self.wayhi_profile(c)["is_wayhi"]:
                ev.append("WAYHI_META")
            if self.temporal_construction(c)[0]:
                ev.append("TIME_RESET")
            if self.place_marker(c)[0]:
                ev.append("PLACE_RESET")
        return ordered_unique(ev)

    def _reported_speech_candidate(
        self,
        formula_clause: int,
        content_start_clause: Optional[int],
    ) -> Tuple[bool, str]:
        """
        Conservative reported/indirect-speech detection.
        """
        comps = {
            norm_hebrew(x)
            for x in self.cfg.get("reported_speech_complementizers", ["כי", "אשר"])
        }

        formula_lex = self.b.lexemes(formula_clause)
        for lx in formula_lex[-3:]:
            if lx in comps:
                return True, f"COMPLEMENTIZER_IN_FORMULA:{lx}"

        if content_start_clause:
            content_lex = self.b.lexemes(content_start_clause)
            if content_lex and content_lex[0] in comps:
                return True, f"COMPLEMENTIZER_AT_CONTENT_START:{content_lex[0]}"

        return False, ""

    def _preposed_report_complementizer(self, formula_clause: int) -> Tuple[bool, str]:
        """
        Detect a complementizer (e.g. כי / אשר) that precedes אמר inside the
        narrator formula clause itself.  This marks narrative reported
        speech/thought rather than a new top-level dialogue turn.

        Example target: Job 1:5 כי אמר איוב.
        """
        comps = {
            norm_hebrew(x)
            for x in self.cfg.get("reported_speech_complementizers", ["כי", "אשר"])
        }
        amr = norm_hebrew("אמר")
        lexs = self.b.lexemes(formula_clause)
        if amr not in lexs:
            return False, ""
        amr_i = lexs.index(amr)
        for lx in lexs[:amr_i]:
            if lx in comps:
                return True, lx
        return False, ""

    def _detect_csf_turns(self) -> List[Dict[str, Any]]:
        """Detect every speech event, then classify its speech level.

        TOP_LEVEL_CSF changes the outer speaker. EMBEDDED_CSF and REPORTED_SPEECH
        remain inside the current outer/top-level speech and never replace it.
        """
        clauses = self.b.clauses
        lookahead = int(self.cfg["speech_formula_lookahead_clauses"])
        amr = norm_hebrew("אמר")
        events: List[Dict[str, Any]] = []
        current_outer_speaker = ""
        current_outer_addressees: List[str] = []
        top_level_turn_id = 0

        for i, c in enumerate(clauses):
            if not self.is_narrator_clause(c):
                continue
            lexs = self.b.lexemes(c)
            formula_nodes: List[int] = []
            family = ""
            end_i = -1

            if amr in lexs:
                if any(e.get("formula_end_clause") == c and e.get("start_clause") != c for e in events):
                    continue
                formula_nodes = [c]
                family = "SIMPLE_AMR"
                end_i = i
            else:
                window = clauses[i:min(len(clauses), i + lookahead + 1)]
                anchor = self._anchor_type(c, window)
                if not anchor:
                    continue
                for j in range(i + 1, min(len(clauses), i + lookahead + 1)):
                    if amr in self.b.lexemes(clauses[j]):
                        end_i = j
                        break
                if end_i < 0:
                    continue
                formula_nodes = clauses[i:end_i + 1]
                family = f"{anchor}+AMR"

            speaker, speaker_source_type = self.b.subject_label(c)
            implicit_context_clause: Optional[int] = None
            if not speaker and family == "SIMPLE_AMR":
                speaker, speaker_source_type, implicit_context_clause = self._implicit_speaker_from_context(
                    clauses, i, c, current_outer_speaker, current_outer_addressees
                )
            if not speaker:
                continue

            subject_names = self.b.subject_names(c)
            exp = self._formula_expansion(
                formula_nodes,
                speaker,
                subject_names,
                family=family,
            )
            actor = self.b.actor_png_profile(c)
            reset_evidence = self._speech_reset_evidence(c)

            # Speech-level classification (v5.1).
            #
            # Priority:
            # 1) anchored CSF formula
            # 2) narrative reported speech/thought (preposed כי/אשר + אמר)
            # 3) explicit narrator speaker
            # 4) speaker supplied by preceding narrator frame
            # 5) resolved implicit named speaker introducing new Q-content
            # 6) direct reply by previous top-level interlocutor
            # 7) hard narrator reset
            # 8) otherwise embedded/reported speech inside current outer speech
            #
            # TIME_RESET alone never changes the top-level speaker.
            content_start_clause = clauses[end_i + 1] if end_i + 1 < len(clauses) else None
            reported_candidate, reported_reason = self._reported_speech_candidate(
                clauses[end_i], content_start_clause
            )
            preposed_report, preposed_report_lexeme = self._preposed_report_complementizer(
                clauses[end_i]
            )

            top_reason = ""
            previous_clause_is_q = bool(i > 0 and self.b.domain(clauses[i - 1]) == "Q")
            hard_reset = any(
                x in {"EXPLICIT_CLOSURE", "WAYHI_META"}
                for x in reset_evidence
            )

            probe = clauses[end_i + 1:min(len(clauses), end_i + 4)]
            following_q_content = bool(
                (content_start_clause and self.b.domain(content_start_clause) == "Q")
                or any(self.b.domain(x) == "Q" for x in probe)
            )

            top_level_speakers_so_far = [
                e.get("speaker", "")
                for e in events
                if e.get("speech_level") == "TOP_LEVEL_CSF" and e.get("speaker")
            ]
            previous_top_level_speaker = (
                top_level_speakers_so_far[-2]
                if len(top_level_speakers_so_far) >= 2
                else ""
            )
            direct_reply_to_current_outer = bool(
                current_outer_speaker
                and previous_clause_is_q
                and previous_top_level_speaker
                and speaker == previous_top_level_speaker
                and speaker != current_outer_speaker
            )

            resolved_implicit_new_turn = bool(
                speaker_source_type == "IMPLICIT_RECENT_MATCHING_NAME"
                and current_outer_speaker
                and speaker != current_outer_speaker
                and following_q_content
            )

            if family != "SIMPLE_AMR":
                speech_level = "TOP_LEVEL_CSF"
                top_reason = "ANCHORED_CSF_FORMULA"

            elif preposed_report:
                # Narrative reported speech/thought does not create a new outer turn.
                # Example: Job 1:5 כי אמר איוב.
                speech_level = "REPORTED_SPEECH"
                reported_reason = (
                    reported_reason
                    or f"PREPOSED_NARRATIVE_COMPLEMENTIZER:{preposed_report_lexeme}"
                )
                top_reason = "NARRATIVE_REPORTED_SPEECH"

            elif speaker_source_type in {
                "PROPER_NAME",
                "ROLE_OR_COMMON_NOUN",
                "SUBJECT_PHRASE_LEXEME",
            }:
                speech_level = "TOP_LEVEL_CSF"
                top_reason = "EXPLICIT_NARRATOR_SUBJECT"

            elif speaker_source_type in {
                "IMPLICIT_FROM_PREVIOUS_NARRATOR_SUBJECT",
                "IMPLICIT_ROLE_FROM_PREVIOUS_SUBJECT",
                "IMPLICIT_ANONYMOUS_FROM_PREVIOUS_SUBJECT",
            }:
                speech_level = "TOP_LEVEL_CSF"
                top_reason = "PRECEDING_NARRATOR_PARTICIPANT"

            elif resolved_implicit_new_turn:
                # Narrator-side omitted subject resolved to a concrete named
                # participant, different from the current outer speaker, with
                # direct Q-content following.  Examples: Job 1:21; 2:10.
                speech_level = "TOP_LEVEL_CSF"
                top_reason = "RESOLVED_IMPLICIT_NAMED_SPEAKER_WITH_Q_CONTENT"

            elif direct_reply_to_current_outer:
                speech_level = "TOP_LEVEL_CSF"
                top_reason = "DIRECT_REPLY_BY_PREVIOUS_TOP_LEVEL_SPEAKER"

            elif hard_reset and current_outer_speaker:
                speech_level = "TOP_LEVEL_CSF"
                top_reason = "HARD_NARRATIVE_RESET:" + "+".join(reset_evidence)

            elif current_outer_speaker:
                if reported_candidate:
                    speech_level = "REPORTED_SPEECH"
                    top_reason = "REPORTED_SPEECH_INSIDE_OUTER_SPEECH"
                else:
                    speech_level = "EMBEDDED_CSF"
                    top_reason = "SIMPLE_AMR_WITHOUT_TOP_LEVEL_RESET"

            else:
                if reported_candidate:
                    speech_level = "REPORTED_SPEECH"
                    top_reason = "REPORTED_SPEECH_WITHOUT_OUTER_SPEAKER"
                elif following_q_content:
                    speech_level = "TOP_LEVEL_CSF"
                    top_reason = "INITIAL_SIMPLE_AMR_WITH_Q_CONTENT"
                else:
                    speech_level = "REPORTED_SPEECH"
                    top_reason = "SIMPLE_AMR_WITHOUT_Q_CONTENT"

            if speech_level == "TOP_LEVEL_CSF":
                top_level_turn_id += 1
                outer_speaker = ""
                embedded_speaker = ""
                speech_depth = 1
                current_outer_speaker = speaker
                current_outer_addressees = list(exp["named_addressees"])
                assigned_top_turn = top_level_turn_id
            else:
                outer_speaker = current_outer_speaker
                embedded_speaker = speaker
                speech_depth = 2 if current_outer_speaker else 1
                assigned_top_turn = top_level_turn_id

            signature_parts = [family, "SPEAKER"]
            if speaker_source_type.startswith("IMPLICIT"):
                signature_parts.append("IMPLICIT_SPEAKER")
            signature_parts.extend(exp["csf_expansion_components"])
            events.append({
                "event_id": len(events) + 1,
                "turn_id": assigned_top_turn if speech_level == "TOP_LEVEL_CSF" else "",
                "top_level_turn_id": assigned_top_turn,
                "start_clause": c,
                "formula_end_clause": clauses[end_i],
                "content_start_clause": content_start_clause,
                "ref": self.b.ref(c),
                "speaker": speaker,
                "speaker_source_type": speaker_source_type,
                "outer_speaker": outer_speaker,
                "embedded_speaker": embedded_speaker,
                "speech_level": speech_level,
                "speech_depth": speech_depth,
                "reported_speech_reason": reported_reason,
                "speech_level_reason": top_reason,
                "reset_evidence": reset_evidence,
                "implicit_context_clause": implicit_context_clause,
                "implicit_context_ref": self.b.ref(implicit_context_clause),
                "speaker_subject_names": subject_names,
                "csf_family": family,
                "csf_profile": exp["csf_profile"],
                "csf_scope_profile": exp.get(
                    "csf_scope_profile",
                    "CORE",
                ),
                "csf_scope_evidence": exp.get(
                    "csf_scope_evidence",
                    [],
                ),
                "csf_signature": "+".join(signature_parts),
                "named_addressees": exp["named_addressees"],
                "addressee_evidence": exp.get(
                    "addressee_evidence",
                    [],
                ),
                "rejected_formula_addressee_lexemes": exp.get(
                    "rejected_formula_addressee_lexemes",
                    [],
                ),
                "adjunct_details": exp["adjunct_details"],
                "speaker_identification_expanded": exp["speaker_identification_expanded"],
                "formula_clause_count": len(formula_nodes),
                "formula_word_count": sum(len(self.b.words(x)) for x in formula_nodes),
                "content_domain_profile": csv_join(self.b.domain(x) for x in clauses[end_i + 1:min(len(clauses), end_i + 4)]),
                "formula_text": " || ".join(self.b.text(x) for x in formula_nodes),
            })

        unique: List[Dict[str, Any]] = []
        seen = set()
        for e in events:
            key = (e["start_clause"], e["speaker"], e["csf_family"], e["speech_level"])
            if key not in seen:
                seen.add(key)
                unique.append(e)
        unique.sort(key=lambda x: self.clause_index(x["start_clause"]))
        for i, e in enumerate(unique, start=1):
            e["event_id"] = i
        return unique

    def _annotate_turn_sequence(self) -> None:
        windows = list(self.cfg["speaker_regime_windows"])
        seen_speakers: Set[str] = set()
        min_span = int(self.cfg.get("speaker_regime_min_span_clauses", 8))
        recur_window = int(self.cfg.get("speaker_regime_following_turns", 2))
        for i, t in enumerate(self.csf_turns):
            prev = self.csf_turns[i - 1] if i else None
            t["previous_speaker"] = prev["speaker"] if prev else ""
            t["speaker_change"] = bool(prev and prev["speaker"] != t["speaker"])
            t["speaker_novelty"] = t["speaker"] not in seen_speakers
            seen_speakers.add(t["speaker"])
            prev_add = set(prev["named_addressees"]) if prev else set()
            cur_add = set(t["named_addressees"])
            t["previous_named_addressees"] = sorted(prev_add)
            t["addressee_shift"] = bool(prev and cur_add and cur_add != prev_add)

            tests: Dict[int, Optional[bool]] = {}
            for w in windows:
                if i < w:
                    tests[w] = None
                else:
                    prev_speakers = {x["speaker"] for x in self.csf_turns[i-w:i]}
                    tests[w] = t["speaker"] not in prev_speakers
            eligible = [x for x in tests.values() if x is not None]
            t["speaker_long_absence"] = bool(eligible) and all(eligible)
            t["speaker_regime_tests_passed"] = bool(eligible) and all(eligible)
            t["regime_tests"] = tests

            next_start_i = self.clause_index(self.csf_turns[i + 1]["start_clause"]) if i + 1 < len(self.csf_turns) else len(self.b.clauses)
            start_i = self.clause_index(t["start_clause"])
            content_i = self.clause_index(t["content_start_clause"]) if t.get("content_start_clause") in self.b.clause_pos else start_i
            t["turn_span_clauses"] = max(1, next_start_i - start_i)
            content_span = 0
            for ci in range(content_i, min(next_start_i, len(self.b.clauses))):
                cc = self.b.clauses[ci]
                if self.b.domain(cc) != "Q":
                    break
                content_span += 1
            t["content_span_clauses"] = content_span
            following = self.csf_turns[i + 1:min(len(self.csf_turns), i + 1 + recur_window)]
            t["speaker_recurs_soon"] = any(x["speaker"] == t["speaker"] for x in following)
            t["speaker_persistent"] = bool(t["content_span_clauses"] >= min_span or t["speaker_recurs_soon"])
            persistence = []
            if t["content_span_clauses"] >= min_span:
                persistence.append(f"LONG_CONTENT_SPAN:{t['content_span_clauses']}")
            if t["speaker_recurs_soon"]:
                persistence.append("SPEAKER_RECURS_SOON")
            t["speaker_persistence_evidence"] = persistence

    def _propagate_speaker(self) -> Dict[int, str]:
        out: Dict[int, str] = {}
        current = ""
        ti = 0
        for c in self.b.clauses:
            while ti < len(self.csf_turns) and self.clause_index(c) >= self.clause_index(self.csf_turns[ti]["start_clause"]):
                current = self.csf_turns[ti]["speaker"]
                ti += 1
            out[c] = current
        return out

    def _propagate_turn_id(self) -> Dict[int, int]:
        out: Dict[int, int] = {}
        current = 0
        ti = 0
        for c in self.b.clauses:
            while ti < len(self.csf_turns) and self.clause_index(c) >= self.clause_index(self.csf_turns[ti]["start_clause"]):
                current = int(self.csf_turns[ti]["turn_id"])
                ti += 1
            out[c] = current
        return out

    def csf_rows(self) -> List[Dict[str, Any]]:
        rows = []
        top_by_start = {t["start_clause"]: t for t in self.csf_turns}
        for e in self.speech_events:
            t = top_by_start.get(e["start_clause"]) if e.get("speech_level") == "TOP_LEVEL_CSF" else None
            rows.append({
                "event_id": e["event_id"],
                "top_level_turn_id": e.get("top_level_turn_id", ""),
                "ref": e["ref"],
                "speech_level": e.get("speech_level", ""),
                "speech_depth": e.get("speech_depth", ""),
                "speech_level_reason": e.get("speech_level_reason", ""),
                "reported_speech_reason": e.get("reported_speech_reason", ""),
                "speaker_canonical": e["speaker"],
                "outer_speaker": e.get("outer_speaker", ""),
                "embedded_speaker": e.get("embedded_speaker", ""),
                "speaker_source_type": e.get("speaker_source_type", ""),
                "implicit_context_ref": e.get("implicit_context_ref", ""),
                "speaker_subject_names": csv_join(e["speaker_subject_names"]),
                "csf_family": e["csf_family"],
                "csf_profile": e["csf_profile"],
                "csf_scope_profile": e.get(
                    "csf_scope_profile",
                    "CORE",
                ),
                "csf_scope_evidence": csv_join(
                    e.get(
                        "csf_scope_evidence",
                        [],
                    )
                ),
                "csf_signature": e["csf_signature"],
                "named_addressees": csv_join(e["named_addressees"]),
                "addressee_evidence": csv_join(
                    e.get(
                        "addressee_evidence",
                        [],
                    )
                ),
                "rejected_formula_addressee_lexemes": csv_join(
                    e.get(
                        "rejected_formula_addressee_lexemes",
                        [],
                    )
                ),
                "adjunct_details": csv_join(e["adjunct_details"]),
                "speaker_identification_expanded": e["speaker_identification_expanded"],
                "formula_end_ref": self.b.ref(e["formula_end_clause"]),
                "content_start_ref": self.b.ref(e["content_start_clause"]),
                "content_domain_profile": e.get("content_domain_profile", ""),
                "reset_evidence": csv_join(e.get("reset_evidence", [])),
                "previous_speaker": t.get("previous_speaker", "") if t else e.get("outer_speaker", ""),
                "speaker_change": t.get("speaker_change", False) if t else False,
                "speaker_novelty": t.get("speaker_novelty", False) if t else False,
                "speaker_long_absence": t.get("speaker_long_absence", False) if t else False,
                "speaker_regime_tests_passed": t.get("speaker_regime_tests_passed", False) if t else False,
                "speaker_persistent": t.get("speaker_persistent", False) if t else False,
                "speaker_persistence_evidence": csv_join(t.get("speaker_persistence_evidence", [])) if t else "",
                "turn_span_clauses": t.get("turn_span_clauses", "") if t else "",
                "content_span_clauses": t.get("content_span_clauses", "") if t else "",
                "addressee_shift": t.get("addressee_shift", False) if t else False,
                "regime_tests": json.dumps(t.get("regime_tests", {}), ensure_ascii=False) if t else "",
                "formula_text": e["formula_text"],
            })
        return rows

    def _detect_closure_spans(self) -> List[Dict[str, Any]]:
        spans = []
        width_max = int(self.cfg["closure_lookahead_clauses"])
        cs = self.b.clauses
        for i, c in enumerate(cs):
            for pat in self.closure_patterns:
                for width in range(1, width_max + 1):
                    nodes = cs[i:min(len(cs), i + width)]
                    lexs = [lx for x in nodes for lx in self.b.lexemes(x)]
                    if self.contains_ordered(lexs, pat):
                        spans.append({
                            "start_clause": c,
                            "end_clause": nodes[-1],
                            "start_ref": self.b.ref(c),
                            "end_ref": self.b.ref(nodes[-1]),
                            "pattern": "+".join(pat),
                            "width_clauses": len(nodes),
                            "text": " || ".join(self.b.text(x) for x in nodes),
                        })
                        break

        # If the same closure pattern reaches the same end clause from overlapping starts,
        # keep the shortest textual span. This removes duplicate detections such as 31:40.
        best: Dict[Tuple[int, str], Dict[str, Any]] = {}
        for r in spans:
            key = (int(r["end_clause"]), str(r["pattern"]))
            cur = best.get(key)
            if cur is None or int(r["width_clauses"]) < int(cur["width_clauses"]):
                best[key] = r
            elif cur is not None and int(r["width_clauses"]) == int(cur["width_clauses"]):
                if self.clause_index(int(r["start_clause"])) > self.clause_index(int(cur["start_clause"])):
                    best[key] = r
        out = list(best.values())
        out.sort(key=lambda x: (self.clause_index(x["start_clause"]), self.clause_index(x["end_clause"])))
        return out

    def recent_closures(self, c: int) -> List[Dict[str, Any]]:
        max_v = int(self.cfg["macro_closure_lookback_verses"])
        out = []
        for r in self.closure_spans:
            if self.clause_index(r["end_clause"]) >= self.clause_index(c):
                continue
            vd = self.b.verse_distance(r["end_clause"], c)
            if vd is not None and vd <= max_v:
                out.append(r)
        out.sort(key=lambda x: self.clause_index(x["end_clause"]), reverse=True)
        return out

    def wayhi_profile(self, c: int) -> Dict[str, Any]:
        is_way0 = self.b.is_way0(c)
        hyy = norm_hebrew("היה")
        wayhi_verbs = [w for w in self.b.finite_verbs(c) if self.b.lex(w) == hyy]
        is_wayhi = False
        for w in wayhi_verbs:
            ps = str(self.b.f("ps", w, ""))
            gn = str(self.b.f("gn", w, ""))
            nu = str(self.b.f("nu", w, ""))
            if ps == "p3" and gn == "m" and nu == "sg":
                is_wayhi = is_way0
                break
        frame_nodes: List[int] = []
        time_refs: List[str] = []
        place_refs: List[str] = []
        if is_wayhi:
            i = self.clause_index(c)
            for x in self.b.clauses[i:min(len(self.b.clauses), i + 1 + int(self.cfg["wayhi_frame_lookahead_clauses"]))]:
                if self.b.domain(x) == "Q":
                    continue
                tm, _ = self.temporal_construction(x)
                pm, _ = self.place_marker(x)
                if tm or pm:
                    frame_nodes.append(x)
                if tm:
                    time_refs.append(self.b.ref(x))
                if pm:
                    place_refs.append(self.b.ref(x))
        return {
            "is_way0": is_way0,
            "is_wayhi": is_wayhi,
            "wayhi_frame": bool(frame_nodes),
            "wayhi_time_refs": ordered_unique(time_refs),
            "wayhi_place_refs": ordered_unique(place_refs),
        }

    def wayhi_rows(self) -> List[Dict[str, Any]]:
        rows = []
        for c in self.b.clauses:
            p = self.wayhi_profile(c)
            if p["is_way0"]:
                rows.append({
                    "clause_node": c,
                    "ref": self.b.ref(c),
                    "clause_type": self.b.f("typ", c, ""),
                    "domain": self.b.domain(c),
                    "way0_generic": True,
                    "wayhi_meta": p["is_wayhi"],
                    "wayhi_frame": p["wayhi_frame"],
                    "wayhi_time_refs": csv_join(p["wayhi_time_refs"]),
                    "wayhi_place_refs": csv_join(p["wayhi_place_refs"]),
                    "actor_png": self.b.actor_png_profile(c),
                    "participant_set": csv_join(sorted(self.participant_set_map.get(c, set()))),
                    "text": self.b.text(c),
                })
        return rows

    def _is_numeric_subject_modifier(self, w: int) -> bool:
        """
        Exclude cardinal/ordinal modifiers from macro subject-head selection.

        BHSA `ls` is used when available.  A small lexical fallback covers the
        common Hebrew numerals in case the lexical-set feature is unavailable.
        """
        ls = str(self.b.f("ls", w, "")).lower()
        if ls in {
            "card",
            "cardinal",
            "ordn",
            "ordinal",
        }:
            return True

        lx = norm_hebrew(self.b.lex(w))
        numeric_lexemes = {
            norm_hebrew(x)
            for x in {
                "אחד",
                "שנים",
                "שני",
                "שתים",
                "שלש",
                "שלשה",
                "ארבע",
                "ארבעה",
                "חמש",
                "חמשה",
                "שש",
                "ששה",
                "שבע",
                "שבעה",
                "שמנה",
                "שמונה",
                "תשע",
                "תשעה",
                "עשר",
                "עשרה",
                "ראשון",
                "שני",
                "שלישי",
            }
        }
        return lx in numeric_lexemes

    def _subject_name_is_identification(
        self,
        words: Sequence[int],
        name_word: int,
        first_name_word: Optional[int],
    ) -> bool:
        """
        Detect patronymic / identification names inside a Subject phrase.

        Examples:
        - אליהוא בן ברכאל -> ברכאל is identification, not a coordinated subject.
        - proper names without patronymic markers remain eligible coordinated
          participants even if Hebrew conjunction is omitted.
        """
        if first_name_word is not None and name_word == first_name_word:
            return False

        try:
            pos = list(words).index(name_word)
        except ValueError:
            return False

        previous_words = list(words)[max(0, pos - 3):pos]
        previous_lexemes = {
            norm_hebrew(self.b.lex(w))
            for w in previous_words
            if self.b.lex(w)
        }

        identification_markers = {
            norm_hebrew(x)
            for x in {
                "בן",
                "בת",
                "אב",
                "אם",
                "משפחה",
                "משפחת",
                "בית",
            }
        }

        return bool(
            previous_lexemes
            & identification_markers
        )

    def _macro_subject_profile(self, c: int) -> Dict[str, Any]:
        """
        Surface-form Subject profile for whole-book macro analysis.

        v5.1 refinements
        ----------------
        1. numeral modifiers such as שלשת are not allowed to become the subject
           head; the following substantive head is preferred;
        2. when the Subject head is a proper name, all non-identification proper
           names in the same Subject phrase are retained as coordinated subjects,
           even where Hebrew omits a conjunction;
        3. patronymic names following בן/בת etc. remain identification names.
        """
        p = self.b.subject_phrase(c)

        if not p:
            return {
                "head_label": "",
                "head_source_type": "",
                "subject_phrase_text": "",
                "all_subject_names": [],
                "coordinated_subject_names": [],
                "identification_subject_names": [],
            }

        words = self.b.words(p)
        names = self.b.proper_names(p)

        first_entity_word = None

        # Prefer the first non-numeric substantive/proper/pronominal head.
        for w in words:
            pos = self.b.pos(w)
            if pos not in {
                "nmpr",
                "subs",
                "prps",
            }:
                continue

            if self._is_numeric_subject_modifier(w):
                continue

            first_entity_word = w
            break

        head_label = ""
        head_source_type = ""

        if first_entity_word is not None:
            pos = self.b.pos(
                first_entity_word
            )
            lx = self.b.lex(
                first_entity_word
            )

            if pos == "nmpr":
                head_label = lx
                head_source_type = (
                    "PROPER_NAME"
                )
            elif pos in {
                "subs",
                "prps",
            }:
                head_label = lx
                head_source_type = (
                    "ROLE_OR_COMMON_NOUN"
                )

        if not head_label:
            head_label, head_source_type = (
                self.b.subject_label(c)
            )

        name_words = [
            w for w in words
            if self.b.pos(w) == "nmpr"
            and self.b.lex(w)
        ]

        first_name_word = (
            name_words[0]
            if name_words else None
        )

        coordinated: List[str] = []
        identification: List[str] = []

        # If the syntactic head is a proper name, all later proper names are
        # examined as possible co-heads, not only those preceded by waw.
        if (
            head_source_type
            == "PROPER_NAME"
        ):
            for w in name_words:
                lx = self.b.lex(w)

                if self._subject_name_is_identification(
                    words,
                    w,
                    first_name_word,
                ):
                    identification.append(lx)
                    continue

                coordinated.append(lx)

        # If the head is common-noun material, proper names in the phrase are
        # references/identifiers, not automatically coordinated co-heads.
        # This preserves רעי איוב: head=רע, Job remains a referenced participant
        # but is not treated as the subject head.
        return {
            "head_label": head_label,
            "head_source_type": (
                head_source_type
            ),
            "subject_phrase_text": (
                self.b.text(p)
            ),
            "all_subject_names": (
                ordered_unique(names)
            ),
            "coordinated_subject_names": (
                ordered_unique(
                    coordinated
                )
            ),
            "identification_subject_names": (
                ordered_unique(
                    identification
                )
            ),
        }

    def _references_in_clause(self, c: int) -> List[Dict[str, Any]]:
        refs: List[Dict[str, Any]] = []
        speaker = self.speaker_by_clause.get(c, "")
        vocs = self.b.vocative_names(c)
        formula_addressees: List[str] = []
        event = self.speech_event_start_map.get(c)
        turn = self.csf_start_map.get(c)
        if event:
            formula_addressees = list(event["named_addressees"])
        else:
            tid = self.turn_id_by_clause.get(c, 0)
            if tid and tid in self.turn_by_id:
                formula_addressees = list(self.turn_by_id[tid]["named_addressees"])
        local_addressees = ordered_unique(vocs + formula_addressees)
        explicit_subject_names = self.b.subject_names(c)
        subject_phrase = self.b.subject_phrase(c)
        subject_name_words = [w for w in self.b.words(subject_phrase) if self.b.pos(w) == "nmpr"] if subject_phrase else []
        canonical_subject_word = subject_name_words[0] if subject_name_words else None
        macro_subject = self._macro_subject_profile(c)
        coordinated_subject_names = set(
            macro_subject["coordinated_subject_names"]
        )

        for w in self.b.words(c):
            if self.b.pos(w) != "nmpr":
                continue
            name = self.b.lex(w)
            fn = self.b.phrase_function_of_word(w)
            nt = self.b.proper_name_type(w)
            if nt in {"loca", "topo", "geog"}:
                ref_class = "NON_PARTICIPANT_PROPER_NAME"
            elif fn == "Subj" and name in coordinated_subject_names:
                ref_class = "ENTITY_PARTICIPANT"
            elif subject_phrase and w in subject_name_words[1:]:
                ref_class = "IDENTIFICATION_NAME"
            else:
                ref_class = "ENTITY_PARTICIPANT"
            role = "EXPLICIT_NAME"
            if fn == "Subj": role = "SUBJECT"
            elif fn == "Voct": role = "ADDRESSEE"
            elif fn in {"Objc", "Cmpl"}: role = "OBJECT_OR_COMPLEMENT"
            refs.append({"participant": name, "reference_form": "PROPER_NAME", "reference_class": ref_class,
                         "grammatical_role": role, "source_word": w, "png": self.b.png(w), "name_type": nt})

        # Speech-event speakers are textual participants. Embedded speakers are recorded
        # locally but do not replace the outer speaker used for top-level discourse.
        if c in self.speech_event_start_map:
            e = self.speech_event_start_map[c]
            st = str(e.get("speaker_source_type", ""))
            if st != "PROPER_NAME":
                named_implicit = st in {"IMPLICIT_FROM_PREVIOUS_NARRATOR_SUBJECT", "IMPLICIT_RECENT_MATCHING_NAME"} and not str(e["speaker"]).startswith(("ANON_", "IMPLICIT_", "ADDRESSEE_"))
                refs.append({"participant": e["speaker"],
                             "reference_form": "IMPLICIT_CSF_SPEAKER" if st.startswith("IMPLICIT") else "ROLE_OR_COMMON_NOUN",
                             "reference_class": "RESOLVED_PERSON_REFERENCE" if named_implicit else "ROLE_PARTICIPANT",
                             "grammatical_role": "EMBEDDED_SPEAKER" if e.get("speech_level") != "TOP_LEVEL_CSF" else "SPEAKER_SUBJECT",
                             "source_word": "", "png": "", "name_type": ""})

        for w in self.b.finite_verbs(c):
            ps, gn, nu = str(self.b.f("ps", w, "")), str(self.b.f("gn", w, "")), str(self.b.f("nu", w, ""))
            if ps in {"", "NA", "unknown"}: continue
            if ps == "p3" and explicit_subject_names:
                participant, ref_class = explicit_subject_names[0], "RESOLVED_PERSON_REFERENCE"
            elif ps == "p1" and speaker:
                participant, ref_class = speaker, "RESOLVED_PERSON_REFERENCE"
            elif ps == "p2" and len(local_addressees) == 1:
                participant, ref_class = local_addressees[0], "RESOLVED_PERSON_REFERENCE"
            else:
                participant = f"MORPH:{ps}:{gn}:{nu}"
                ref_class = "MORPHOLOGICAL_REFERENT"
            refs.append({"participant": participant, "reference_form": "VERBAL_INFLECTION", "reference_class": ref_class,
                         "grammatical_role": "VERBAL_SUBJECT", "source_word": w, "png": f"{ps}:{gn}:{nu}", "name_type": ""})

        for w in self.b.words(c):
            if self.b.pos(w) == "prps":
                ps, gn, nu = str(self.b.f("ps", w, "")), str(self.b.f("gn", w, "")), str(self.b.f("nu", w, ""))
                if ps not in {"", "NA", "unknown"}:
                    if ps == "p1" and speaker:
                        p, rc = speaker, "RESOLVED_PERSON_REFERENCE"
                    elif ps == "p2" and len(local_addressees) == 1:
                        p, rc = local_addressees[0], "RESOLVED_PERSON_REFERENCE"
                    else:
                        p, rc = f"MORPH:{ps}:{gn}:{nu}", "MORPHOLOGICAL_REFERENT"
                    refs.append({"participant": p, "reference_form": "INDEPENDENT_PRONOUN", "reference_class": rc,
                                 "grammatical_role": self.b.phrase_function_of_word(w) or "PRONOUN", "source_word": w,
                                 "png": f"{ps}:{gn}:{nu}", "name_type": ""})
            pps = str(self.b.f("prs_ps", w, ""))
            if pps not in {"", "NA", "unknown"}:
                pgn, pnu = str(self.b.f("prs_gn", w, "")), str(self.b.f("prs_nu", w, ""))
                if pps == "p1" and speaker:
                    p, rc = speaker, "RESOLVED_PERSON_REFERENCE"
                elif pps == "p2" and len(local_addressees) == 1:
                    p, rc = local_addressees[0], "RESOLVED_PERSON_REFERENCE"
                else:
                    p, rc = f"MORPH:{pps}:{pgn}:{pnu}", "MORPHOLOGICAL_REFERENT"
                refs.append({"participant": p, "reference_form": "PRONOMINAL_SUFFIX", "reference_class": rc,
                             "grammatical_role": "SUFFIX_REFERENCE", "source_word": w,
                             "png": f"{pps}:{pgn}:{pnu}", "name_type": ""})

        out, seen = [], set()
        for r in refs:
            key = (r["participant"], r["reference_form"], r["grammatical_role"], r["source_word"])
            if key not in seen:
                seen.add(key); out.append(r)
        return out

    def _build_participant_tables(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        all_rows: List[Dict[str, Any]] = []
        clause_sets: List[Dict[str, Any]] = []
        last_seen_clause: Dict[str, int] = {}
        previous_entity_set: Set[str] = set()
        previous_actor = ""
        cs = self.b.clauses
        return_window = int(self.cfg["participant_return_lookahead_clauses"])
        refs_by_clause = {c: self._references_in_clause(c) for c in cs}
        entity_classes = {"ENTITY_PARTICIPANT", "ROLE_PARTICIPANT", "RESOLVED_PERSON_REFERENCE"}

        for i, c in enumerate(cs):
            refs = refs_by_clause[c]
            entity_set = {r["participant"] for r in refs if r["participant"] and r.get("reference_class") in entity_classes}
            morph_set = {r["participant"] for r in refs if r.get("reference_class") == "MORPHOLOGICAL_REFERENT"}
            actor = self.b.actor_png_profile(c)
            actor_shift = bool(previous_actor and actor and actor != previous_actor)
            return_distance = ""
            if actor_shift:
                for d in range(1, return_window + 1):
                    if i + d >= len(cs): break
                    if self.b.actor_png_profile(cs[i+d]) == previous_actor:
                        return_distance = d; break

            for r in refs:
                p = r["participant"]
                if p not in last_seen_clause:
                    status, gap = "FIRST_TEXTUAL_OCCURRENCE", ""
                else:
                    gap_n = i - last_seen_clause[p]
                    status, gap = ("CONTINUED_ADJACENT" if gap_n == 1 else "RETURN_AFTER_GAP"), gap_n
                all_rows.append({
                    "clause_node": c, "ref": self.b.ref(c), "turn_id": self.turn_id_by_clause.get(c, 0),
                    "speaker": self.speaker_by_clause.get(c, ""), "participant": p,
                    "reference_form": r["reference_form"], "reference_class": r.get("reference_class", ""),
                    "grammatical_role": r["grammatical_role"], "png": r["png"], "name_type": r.get("name_type", ""),
                    "textual_status": status, "gap_clauses": gap, "source_word_node": r["source_word"], "text": self.b.text(c),
                })
                last_seen_clause[p] = i

            added = sorted(entity_set - previous_entity_set)
            dropped = sorted(previous_entity_set - entity_set)
            clause_sets.append({
                "clause_node": c, "ref": self.b.ref(c), "turn_id": self.turn_id_by_clause.get(c, 0),
                "speaker": self.speaker_by_clause.get(c, ""),
                "entity_participant_set": csv_join(sorted(entity_set)),
                "morphological_referent_set": csv_join(sorted(morph_set)),
                "set_added": csv_join(added), "set_dropped": csv_join(dropped),
                "participant_set_shift": bool(previous_entity_set and entity_set and entity_set != previous_entity_set),
                "actor_png": actor, "previous_actor_png": previous_actor, "actor_png_shift": actor_shift,
                "actor_returns_to_previous_within_clauses": return_distance, "text": self.b.text(c),
            })
            if entity_set: previous_entity_set = entity_set
            if actor: previous_actor = actor
        return all_rows, clause_sets

    def surface_clause_rows(self) -> List[Dict[str, Any]]:
        rows = []
        closure_starts = {r["start_clause"]: r for r in self.closure_spans}
        for c in self.b.clauses:
            tm, tms = self.temporal_construction(c)
            pm, pms = self.place_marker(c)
            wp = self.wayhi_profile(c)
            csf = self.csf_start_map.get(c)
            speech_event = self.speech_event_start_map.get(c)
            pset = self.participant_set_map.get(c, set())
            rows.append({
                "clause_node": c,
                "ref": self.b.ref(c),
                "chapter": self.b.cv(c)[0],
                "verse": self.b.cv(c)[1],
                "turn_id": self.turn_id_by_clause.get(c, 0),
                "speaker": self.speaker_by_clause.get(c, ""),
                "domain": self.b.domain(c),
                "clause_type": self.b.f("typ", c, ""),
                "kind": self.b.f("kind", c, ""),
                "msyn": self.b.is_msyn(c),
                "way0": self.b.is_way0(c),
                "wayx": self.b.is_wayx(c),
                "wayhi_meta": wp["is_wayhi"],
                "wayhi_frame": wp["wayhi_frame"],
                "time_marker": tm,
                "time_marker_source": tms,
                "place_marker": pm,
                "place_marker_source": pms,
                "actor_png": self.actor_png_map.get(c, ""),
                "participant_set": csv_join(sorted(pset)),
                "phrase_functions": csv_join(self.b.phrase_functions(c)),
                "verb_forms": csv_join(self.b.verb_forms(c)),
                "vocative": self.b.has_vocative(c),
                "imperative": self.b.has_imperative(c),
                "question": self.b.has_question(c),
                "discourse_marker": self.is_discourse_marker(c),
                "csf_open": bool(csf),
                "speech_event_open": bool(speech_event),
                "speech_level": speech_event.get("speech_level", "") if speech_event else "",
                "embedded_speaker": speech_event.get("embedded_speaker", "") if speech_event else "",
                "csf_family": speech_event["csf_family"] if speech_event else "",
                "csf_profile": speech_event["csf_profile"] if speech_event else "",
                "closure_start": c in closure_starts,
                "content_lexemes": csv_join(self.b.content_lexemes(c, self.content_pos)),
                "text": self.b.text(c),
            })
        return rows
