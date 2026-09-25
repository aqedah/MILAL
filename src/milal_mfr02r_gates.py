"""Release gates consume measured audit facts and executable test receipts."""
import hashlib
import json
from pathlib import Path
from collections import Counter
from milal_mfr02r_data import rows, digest, encode, physical_path, verify_manifest
from milal_mfr02r_grammar import DIMENSIONS

ROOT = Path(__file__).resolve().parents[1]


def historical_preservation(originals, revalidated, review):
    expected = review.get('original_decision_hashes', {})
    actual = {r['decision_id']: hashlib.sha256(encode(r).encode()).hexdigest() for r in originals}
    original_map = {r['decision_id']:r for r in originals}
    return bool(expected) and actual == expected and {r['decision_id'] for r in revalidated} == set(expected) and len(originals) == len(expected) == len(revalidated) and all(
        r['original_decision'] == original_map.get(r['decision_id']) for r in revalidated)


def evaluate(facts):
    required = json.loads((ROOT / 'config/mfr_0_2r_required_gates.json').read_text())['gates']
    if set(facts) - set(required):
        raise ValueError('undeclared gate facts')
    return [dict(gate=name, passed=facts.get(name) is True, evidence=facts.get(name, 'NOT_EVALUATED')) for name in required]


def artifact_facts(job, registry, tests, config, receipts, control, review, out):
    job, out = Path(job), Path(out)
    inventory = list(rows(job / '02_clause_feature_inventory.csv'))
    rules = [r for r in registry['rules'] if r.get('enabled', True)]
    passed_tests = set(tests.get('passed_tests', []))
    def proof(name):
        return any(t.endswith('.' + name) for t in passed_tests)
    def exists(name):
        return physical_path(job / name).is_file()
    def record_nonempty(name):
        return next(rows(job / name), None) is not None
    by_id = {int(r['clause_id']): r for r in inventory}
    expected, actual = hashlib.sha256(), hashlib.sha256()
    count, invalid, canonical, same_hypo, different_para, rhetoric, para_count = 0, 0, 0, 0, 0, 0, 0
    for row in rows(job / '07_preceding_candidate_sets.csv'):
        target = int(row['target_clause_id'])
        for source in row['candidate_clause_ids']:
            expected.update(('%s:%s\n' % (source, target)).encode())
    for row in rows(job / '09_candidate_evidence_matrix.csv'):
        source, target = int(row['candidate_clause_id']), int(row['target_clause_id'])
        actual.update(('%s:%s\n' % (source, target)).encode()); count += 1
        invalid += source not in by_id or target not in by_id or int(by_id[source]['position']) >= int(by_id[target]['position'])
        rhetoric += row['RHETORICAL_SECONDARY']['status'] != 'NOT_LOADED' or row['SEMANTIC_CORRESPONDENCE']['status'] != 'NOT_LOADED'
        same_hypo += row['source_clause_type'] == row['target_clause_type'] and row['candidate_relations'] in ('HYPOTACTIC', 'MULTIPLE')
        different_para += row['source_clause_type'] != row['target_clause_type'] and row['candidate_relations'] in ('PARATACTIC', 'MULTIPLE')
        para_count += row['candidate_relations'] in ('PARATACTIC', 'MULTIPLE')
    relation_rows = rows(job / '10_relation_candidates.csv')
    canonical = sum(bool(r['accepted_mother'] or r['adjudicated_function']) for r in relation_rows)
    revalidated = list(rows(out / '18_mfr02a_revalidation.csv'))
    originals = list(rows(out / 'mfr02a_original_decisions.csv'))
    preserved = historical_preservation(originals, revalidated, review)
    human_rows = list(rows(out / '24_human_review_cases.csv'))
    from milal_mfr02r_review import REVIEW_FIELDS, EXTRA_REVIEW_FIELDS
    blanks = bool(human_rows) and all(not r[k] for r in human_rows for k in (*REVIEW_FIELDS, *EXTRA_REVIEW_FIELDS))
    frozen = bool(receipts) and all(r['expected_sha256'] == r['actual_sha256'] for r in receipts)
    source = '\n'.join((ROOT / 'src' / ('milal_mfr02r_' + name + '.py')).read_text(encoding='utf8') for name in ('engine', 'features', 'grammar', 'graph', 'layers', 'valency', 'revision'))
    no_scores = not any(name in source for name in ('relation_score', 'confidence_score', 'hierarchy_score', 'weighted_similarity', 'best_score'))
    count_family = Counter(r['rule_id'][3] for r in rules if r['source_author'] == 'JIN')
    facts = dict(BASELINE_COMMIT_VERIFIED=frozen and config['baseline'] == tests.get('baseline'),
        MFR_0_1_FROZEN=frozen, MFR_0_1A_FROZEN=frozen, MFR_0_1B_FROZEN=frozen, MFR_0_2A_FROZEN=frozen,
        RELATION_GRAMMAR_REGISTRY_CREATED=count_family == {'A': 4, 'B': 10, 'C': 4, 'D': 2, 'E': 4},
        EXPLICIT_SUBORDINATION_RULES_ACTIVE=proof('test_explicit_subordination_and_alternative_mothers'),
        MAIN_CLAUSE_HYPOTAXIS_RULES_ACTIVE=same_hypo > 0 and proof('test_same_type_hypotaxis_and_parataxis_compete'),
        MAIN_CLAUSE_PARATAXIS_RULES_ACTIVE=proof('test_all_parallel_and_embedded_variants') and para_count > 0,
        SAME_CLAUSE_TYPE_CAN_BE_HYPOTACTIC=same_hypo > 0,
        DIFFERENT_CLAUSE_TYPE_CAN_BE_PARATACTIC=different_para > 0 or proof('test_different_type_parataxis_context_required'),
        FULL_PRECEDING_CANDIDATE_SET_GENERATED=count > 0 and not invalid and expected.digest() == actual.digest(),
        NO_NEAREST_ONLY_HEURISTIC=proof('test_long_distance_and_book_boundary'),
        NO_PRIMARY_SUPPORT_EPISTEMIC_RANK='PRIMARY_FORMAL_MARKER' not in source and exists('09_candidate_evidence_matrix.csv'),
        NO_NUMERIC_RELATION_SCORE=no_scores,
        PROVISIONAL_RELATION_GRAPH_CREATED=record_nonempty('12_provisional_relation_graph.csv'),
        GLOBAL_COMPATIBILITY_CHECK_ACTIVE=proof('test_parallel_cycle_after_contraction') and exists('14_global_compatibility_matrix.csv'),
        MULTIPLE_VARIANTS_PRESERVED=proof('test_symbolic_preserves_every_option') and exists('15_variant_components.csv'),
        NO_AUTOMATIC_SINGLE_HIERARCHY=not canonical and proof('test_one_mother_only_in_selected_variant'),
        MFR02A_PROVISIONAL_STATUS_PRESERVED=preserved and all(r['provisional_status'] == 'PROVISIONAL_HUMAN_ADJUDICATION' for r in revalidated),
        MFR02A_NOT_SILENTLY_OVERWRITTEN=preserved and all(not r['revised_human_decision'] for r in revalidated),
        LEV25_26_CONTROL_EXECUTED='leviticus_candidates_recovered' in control,
        NUM26_VARIANT_CONTROL_EXECUTED=control.get('numbers_variants_representable') == 2,
        PENTATEUCH_VARIANT_CONTROL_EXECUTED=control.get('pentateuch_variants_representable') == 2,
        SAME_PATTERN_DIFFERENT_LEVEL_CONTROL_PASS=control.get('same_pattern_different_level') == 5,
        BOOK_BOUNDARY_NOT_HIERARCHY_FILTER=set(control.get('crossbook_candidate_counts', {})) == {'explicit_fixtures'} and all(n > 0 for n in control['crossbook_candidate_counts'].values()) and proof('test_long_distance_and_book_boundary'),
        RHETORIC_NOT_USED_IN_PASS1=not rhetoric and count > 0,
        NO_NEW_HUMAN_JUDGMENT=blanks and review['new_human_judgments'] == 0,
        NO_CANONICAL_NEW_MOTHER=not canonical and count > 0,
        NO_CANONICAL_WHOLE_TREE=count > 0 and not canonical and all(not r['accepted_variant'] for r in rows(job / '15_variant_components.csv')),
        R4_4_CONSUMER_ABSENT=not any('consumer' in p.name for p in (ROOT / 'src').glob('milal_mfr02r*.py')),
        FULL_REGRESSION_PASS=tests.get('tests_run', 0) >= 2152 and tests.get('failures') == tests.get('errors') == 0,
        SKIP_ZERO=tests.get('skipped') == 0 and tests.get('tests_run', 0) >= 2152,
        DETERMINISTIC_RERUN=False, MANIFEST_VALID=verify_manifest(job))
    for dim in ('TIME', 'LOCATION', 'PARTICIPANT', 'REFERENCE', 'DOMAIN'):
        facts[dim + '_FIRST_CLASS_EVIDENCE'] = bool(inventory) and all(dim in row and row[dim] is not None for row in inventory)
    walton = [r for r in rules if r['source_author'] == 'WALTON']
    facts.update(WALTON_SOURCE_PROVENANCE_COMPLETE=bool(walton) and all(all(r.get(k) for k in ('source_author', 'source_work', 'source_section', 'source_page', 'adoption_status')) for r in walton),
        PARTICIPANT_NEW_REINTRODUCED_CONTINUED_AVAILABLE=proof('test_participant_new_continued_reintroduced_absent'),
        TIME_PLACE_FIRST_CLASS_EVIDENCE=facts['TIME_FIRST_CLASS_EVIDENCE'] and facts['LOCATION_FIRST_CLASS_EVIDENCE'],
        SAME_TYPE_PARALLEL_NOT_HARD_RULE=proof('test_type_only_never_decides'),
        WALTON_PARTICIPANT_EXCEPTION_ACTIVE=proof('test_same_type_hypotaxis_and_parataxis_compete') and proof('test_walton_secondary_participant_negative'),
        SEMANTIC_CORRESPONDENCE_SECONDARY_ONLY=not rhetoric and proof('test_semantic_secondary_only'),
        NO_CORRESPONDENCE_NOT_AUTO_ROOT=record_nonempty('target_search_receipts.csv') and all(not r['canonical_level'] for r in rows(job / 'target_search_receipts.csv')),
        ITERATIVE_REVISION_HISTORY_SUPPORTED=proof('test_append_only_revision_and_tamper') and exists('relation_revision_history.csv'),
        LONG_DISTANCE_PARTICIPANT_REINTRODUCTION_SUPPORTED=proof('test_long_distance_and_book_boundary'),
        JIN_WALTON_CONFLICT_PRESERVED=proof('test_same_type_hypotaxis_and_parataxis_compete') and exists('jin_walton_rule_conflicts.csv'),
        NO_WALTON_CONCLUSION_HARDCODED=proof('test_static_control_reference_leakage'))
    bosman = list(rows(job / 'bosman_source_crosswalk.csv'))
    facts.update(BOSMAN_SOURCE_PROVENANCE_COMPLETE=bool(bosman) and all(r['source_author'] == 'BOSMAN' and all(r.get(k) for k in ('source_work', 'source_section', 'source_page_if_verified', 'adoption_status', 'source_pdf_sha256')) for r in bosman),
        MULTILAYER_EVIDENCE_ARCHITECTURE_ACTIVE=proof('test_synthetic_multilayer_outputs'),
        TEXTUAL_PARTICIPANT_POETIC_LAYERS_SEPARATE=proof('test_b_s3_reference_does_not_replace_mother') and proof('test_b_s4_poetic_and_syntax_edges_differ'),
        LARGER_UNIT_CONTEXT_AVAILABLE=exists('textual_unit_candidates.csv') and proof('test_b_s12_wider_context_is_source_linked'),
        HIDDEN_PARTICIPANT_REFERENCE_RECOVERABLE=proof('test_b_s1_hidden_reference'),
        PARTICIPANT_STRUCTURE_CAN_DIVERGE_FROM_SYNTAX=proof('test_b_s3_reference_does_not_replace_mother'),
        POETIC_STRUCTURE_CAN_DIVERGE_FROM_SYNTAX=proof('test_b_s4_poetic_and_syntax_edges_differ'),
        TEXTUAL_HIERARCHY_REMAINS_TREE_DIMENSION=proof('test_one_mother_only_in_selected_variant'),
        FULL_RELATION_MODEL_SUPPORTS_TYPED_GRAPH=proof('test_synthetic_multilayer_outputs'),
        PROGRAM_HUMAN_DECISION_MATRIX_PRESERVED=exists('program_human_decision_matrix.csv') and proof('test_b_s8_human_unproposed_acceptance'),
        REJECTED_CANDIDATES_PRESERVED=proof('test_b_s7_rejected_proposal_retained') and proof('test_b_s9_learning_keeps_both_rejection_states'),
        RULE_DISCOVERY_DATASET_CREATED=record_nonempty('relation_decision_learning_table.csv'),
        NO_BLACK_BOX_LEARNING=not any(name in source for name in ('sklearn', 'torch', 'tensorflow')) and record_nonempty('relation_decision_learning_table.csv'),
        NO_ACROSTIC_RULE_IMPORTED_TO_JOB=proof('test_b_s10_no_acrostic_rule'),
        NO_INVENTED_JOB_STROPHE=proof('test_b_s11_no_invented_poetic_boundary'),
        PROSODY_NOT_AUTOMATIC_BOUNDARY=proof('test_b_s5_boundary_not_hierarchy_break'),
        POETRY_AWARE_EXCEPTION_REPRESENTABLE=proof('test_poetry_exception_is_candidate_only'))
    construction_rows = list(rows(job / 'construction_inventory.csv'))
    facts.update(OOSTING_SOURCE_PROVENANCE_COMPLETE=bool(construction_rows) and all(r['source_author'] == 'OOSTING' and r['source_section'] for r in construction_rows),
        VALENCY_LAYER_ACTIVE=len(construction_rows) == len(inventory) > 0,
        CLAUSE_INTERNAL_BINDING_BEFORE_RELATION_GRAMMAR=proof('test_binding_precedes_grammar_in_engine'),
        RAW_CLAUSE_ATOM_NOT_ASSUMED_INDEPENDENT=proof('test_o_s10_raw_atom_not_independent'),
        VALENCY_BINDING_CAN_CROSS_INTERVENING_CLAUSES=proof('test_o_s2_inserted_clause_deferred'),
        EXACT_CONSTRUCTION_SIGNATURE_AVAILABLE=bool(construction_rows) and all(r['exact_construction_signature_id'] for r in construction_rows),
        OBSERVED_AND_GENERALIZED_PATTERNS_SEPARATE=bool(construction_rows) and all(r['observed_status'] == 'OBSERVED_CONSTRUCTION' and not r['generalized_pattern'] for r in construction_rows),
        CORPUS_ANALOGUE_SEARCH_ACTIVE=record_nonempty('corpus_analogue_evidence.csv') and proof('test_o_s4_crossbook_analogue'),
        CORPUS_SCOPE_SEPARATE_FROM_HIERARCHY_SCOPE=record_nonempty('corpus_analogue_evidence.csv') and all(r['analysis_scope'] != r['corpus_comparison_scope'] for r in rows(job / 'corpus_analogue_evidence.csv')),
        NO_CORPUS_ANALOGUE_AUTO_RELATION=proof('test_o_s5_analogue_not_hierarchy'),
        CORPUS_COUNTEREXAMPLES_PRESERVED=exists('corpus_behavior_variation.csv') and proof('test_o_s11_same_form_different_behavior'),
        MASORETIC_EVIDENCE_SECONDARY_ONLY=proof('test_o_s8_tiebreaker_needs_alternatives'),
        NO_ACCENT_AUTO_BOUNDARY=proof('test_o_s7_accent_conflict_secondary'),
        TEXT_AS_ENCODED_PRIMARY_PASS=bool(construction_rows) and all(r['analysis_form'] == 'TEXT_AS_ENCODED' for r in construction_rows),
        NO_AUTOMATIC_EMENDATION=proof('test_o_s12_no_emendation'),
        PARTICIPANT_DUAL_USE_PROVENANCE=proof('test_o_s9_participant_use_separate'),
        OOSTING_CONTROLS_EXECUTED='oosting_binding_controls' in control)
    from milal_mfr02r_scope import scope_facts
    receipt_path = out/'corpus_search/corpus_search_receipt.json'
    corpus_receipt = json.loads(receipt_path.read_text()) if receipt_path.is_file() else {}
    facts.update(scope_facts(out, control, corpus_receipt))
    return facts
