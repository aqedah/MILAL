import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from milal_review_eligibility import classify, target_status, relation_types
from milal_relation_competition import sets


def candidate(n,status='INSUFFICIENT',facts=None,context=None):
    return dict(candidate_id='P%s-200'%n,source_candidate_id=n,target_id=200,
        existing_candidate_relation=status,existing_rule_ids=[],relations=relation_types(status),
        component_ids=(context or {}).get('component_ids',[]),conflict_ids=(context or {}).get('conflict_ids',[]),
        **classify(dict(candidate_relations=status,facts=facts or {}),context or {}))


class EligibilityTests(unittest.TestCase):
    def test_s1_100_preserved_two_shown(self):
        data=[candidate(i) for i in range(95)]+[candidate(i,'FORMAL_ONLY') for i in range(95,98)]+[candidate(i,'HYPOTACTIC') for i in range(98,100)]
        self.assertEqual(len(data),100)
        self.assertEqual(len(sets(200,data)[0]['candidate_ids']),2)

    def test_s2_multi_rules_one_card(self):
        r=candidate(1,'MULTIPLE');r['existing_rule_ids']=['J1','J2','W1']
        self.assertEqual(sets(200,[r])[0]['candidate_ids'],['P1-200'])
        self.assertEqual(len(r['existing_rule_ids']),3)

    def test_s3_long_formal_evidence(self):
        r=candidate(1,'FORMAL_ONLY');r['distance']=100000
        self.assertEqual(r['review_eligibility'],'EVIDENCE_ONLY')
        self.assertEqual(target_status([r],{})['review_tier'],'')

    def test_s4_long_relation_survives(self):
        r=candidate(1,'HYPOTACTIC',{'participant_continuity':True});r['distance']=100000
        self.assertEqual(r['review_eligibility'],'RELATION_ELIGIBLE')

    def test_s5_multiple_mothers_required(self):
        self.assertEqual(target_status([candidate(1,'HYPOTACTIC'),candidate(2,'HYPOTACTIC')],{})['target_review_status'],'TARGET_REVIEW_REQUIRED')

    def test_s6_single_is_not_accepted(self):
        m=sets(200,[candidate(1,'HYPOTACTIC')])[1]
        self.assertEqual(m['status'],'SINGLE_HYPOTACTIC_CANDIDATE');self.assertEqual(m['accepted_mother'],'')

    def test_s7_hyp_para_competition(self):
        r=target_status([candidate(1,'HYPOTACTIC'),candidate(2,'PARATACTIC')],{})
        self.assertIn('HYPOTACTIC_PARATACTIC_COMPETITION',r['review_reason_codes'])

    def test_s8_variant_membership(self):
        self.assertEqual(candidate(1,context={'component_ids':['V1']})['review_eligibility'],'CONFIGURATION_ELIGIBLE')

    def test_s9_insufficient_retained(self):
        r=candidate(1);self.assertEqual(r['candidate_id'],'P1-200');self.assertEqual(r['review_eligibility'],'INSUFFICIENT')

    def test_s10_history_scope_only(self):
        r=candidate(1);status=target_status([r],{'revalidation_ids':['H1'],'tier1':True})
        self.assertEqual(status['review_tier'],'TIER_1');self.assertEqual(r['review_eligibility'],'INSUFFICIENT')

    def test_s11_history_cannot_promote(self):
        self.assertEqual(candidate(1,context={'historical_decision':'PARATACTIC'})['review_eligibility'],'INSUFFICIENT')

    def test_s12_deferred_relation(self):
        r=candidate(1,context={'deferred':True});self.assertIn('VALENCY_UNRESOLVED',r['review_reason_codes'])

    def test_s13_poetry_exception(self):
        r=candidate(1,context={'poetry_exception':'POETRY_AWARE_EXCEPTION_CANDIDATE'})
        self.assertEqual(r['review_eligibility'],'CONFIGURATION_ELIGIBLE')

    def test_s14_no_ranking(self):
        for field in candidate(1):self.assertFalse(field.endswith('_score') or field=='candidate_rank')

    def test_s15_complete_classes(self):
        data=[candidate(1),candidate(2,'FORMAL_ONLY'),candidate(3,'HYPOTACTIC'),candidate(4,context={'conflict_ids':['C1']})]
        self.assertEqual(len({r['review_eligibility'] for r in data}),4)

    def test_class_precedence_preserves_reasons(self):
        r=candidate(1,'HYPOTACTIC',context={'component_ids':['V1'],'conflict_ids':['C1']})
        self.assertEqual(r['review_eligibility'],'RELATION_ELIGIBLE');self.assertIn('GLOBAL_CONFLICT',r['review_reason_codes'])

    def test_binding_target_not_all_pair_promotion(self):
        r=candidate(1);self.assertEqual(target_status([r],{'binding_ids':['B1']})['target_review_status'],'TARGET_REVIEW_REQUIRED')
        self.assertEqual(r['review_eligibility'],'INSUFFICIENT')

    def test_evidence_dimensions_do_not_create_relation(self):
        for fact in ('time_continuity','location_continuity','participant_continuity','reference_continuity','lexical_continuity'):
            self.assertEqual(candidate(1,facts={fact:True})['review_eligibility'],'EVIDENCE_ONLY')
