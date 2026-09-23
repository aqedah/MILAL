from copy import deepcopy
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import milal_hsa3_fg_prep as f


def hist(member):
    return lambda m,s:m['historical'].update({f.HISTORY+member:b'changed'})


def delete_edge(m,src,tgt,rel):
    name=f.HISTORY+f.EDGES
    rr=f.rows(m['historical'][name])
    m['historical'][name]=f.util.csv_bytes([r for r in rr if (r['source_node'],r['target_node'],r['relation_type'])!=(src,tgt,rel)])


def replace_lex(m,ref,old,new):
    for c in m['native']:
        for w in c['words']:
            if w['reference']==ref and w['lex']==old:w['lex']=new


def at(m,field,ref):
    return next(r for r in m[field] if r['reference']==ref)


MUTATIONS={
 'BASELINE_COMMIT_VERIFIED':lambda m,s:m['commit'].update(verified_commit='bad'),
 'ABC_FROZEN':hist('01_hsa3_abc_seam_adjudications.csv'),
 'DE_FROZEN':hist(f.prior.HISTORY+f.prior.DE),
 'FG_UNREVIEWED':lambda m,s:m['fg_review'][0].update(review_status='ACCEPTED'),
 'NO_R4_4':lambda m,s:m.update(r44_started=True),
 'NO_NEW_HUMAN_JUDGMENT':lambda m,s:m['human_judgments'].append({'status':'ACCEPTED'}),
 'NO_NEW_TEXTUAL_RELATION':lambda m,s:m['textual_relations'].append({'relation':'CHILD_OF'}),
 'NO_NEW_ACCEPTED_OVERLAY':lambda m,s:m['accepted_overlays'].append({'status':'ACCEPTED'}),
 'AFTER_THUS_DETECTED':lambda m,s:replace_lex(m,'3:1','>XR/','NOT_AFTER'),
 'AFTER_YHWH_SPEAKING_DETECTED':lambda m,s:replace_lex(m,'42:7','DBR[','NOT_SPEAK'),
 'AFTER_THIS_DETECTED':lambda m,s:replace_lex(m,'42:16','Z>T','NOT_THIS'),
 'JOB_42_16_LIVE_NOT_BE':lambda m,s:at(m,'g','42:16')['verbal_words'][0].update(lex='HJH['),
 'WAYHI_WAYCHI_DISTINCT':lambda m,s:at(m,'g','42:16')['lexical_wayhi_words'].append(999),
 'TEMPORAL_POSITION_DISTINCT':lambda m,s:at(m,'comparison','42:16')['DIFFERENCE'].update(after_first_verb=False),
 'WHOLE_BOOK_TEMPORAL_COVERAGE':lambda m,s:m['temporal'].pop(),
 'TEMPORAL_NOT_AUTO_BOUNDARY':lambda m,s:m['temporal'][0].update(structural_implication='NEW_BOUNDARY'),
 'REPEATED_SCENE_CONFIGURATION':lambda m,s:m['scenes'][0].update(sons_of_god=[]),
 'JOB_1_13_NOT_PROMOTED':lambda m,s:next(r for r in m['scenes'] if r['start_ref']=='1:13')['new_relation_ids'].append('SIBLING'),
 'TEST_SCENE_SIBLINGS_PRESERVED':lambda m,s:delete_edge(m,'H:HSA002','H:HSA009','SAME_LEVEL_SIBLING'),
 'JOB_27_ADD_FORMULA':lambda m,s:at(m,'formulas','27:1').update(take_proverb=[]),
 'JOB_36_ADD_FORMULA':lambda m,s:at(m,'formulas','36:1').update(formula_family='ANSWER'),
 'FORMAL_SHIFT_NOT_STRUCTURAL_EQUIVALENCE':lambda m,s:at(m,'formulas','36:1').update(structural_implication='NEW_GROUP_ONSET'),
 'YHWH_PEERS_PRESERVED':lambda m,s:delete_edge(m,'H:HSA025','H:HSA028','SAME_LEVEL_SIBLING'),
 'JOB_RESPONSE_PEERS_PRESERVED':lambda m,s:delete_edge(m,'H:HSA027','H:HSA029','SAME_LEVEL_SIBLING'),
 'INTERNAL_40_1_CHILD_PRESERVED':lambda m,s:delete_edge(m,'H:HSA026','H:HSA025','CHILD_OF'),
 'REPEATED_CHALLENGE_CAPTURED':lambda m,s:at(m,'f','40:7').update(repeated_challenge=[]),
 'F_CANDIDATES_UNADJUDICATED':lambda m,s:m['candidates'][0].update(status='ACCEPTED'),
 'JOB_42_7_PARAGRAPH_PRESERVED':lambda m,s:at(m,'g','42:7')['current_hsa'].update(nodes=[]),
 'JOB_42_10_NOT_PROMOTED':lambda m,s:at(m,'g','42:10')['current_hsa']['nodes'].append({'structural_function':'PARAGRAPH_ONSET'}),
 'JOB_42_12_NOT_PROMOTED':lambda m,s:at(m,'g','42:12')['current_hsa']['nodes'].append({'structural_function':'PARAGRAPH_ONSET'}),
 'JOB_42_16_NO_BOUNDARY_PRESERVED':lambda m,s:delete_edge(m,'H:HSA031','H:HSA030','CONTINUES_WITHIN'),
 'JOB_42_16_COUNTER_EVIDENCE_RETAINED':lambda m,s:at(m,'comparison','42:16')['counter_evidence_for_review'].update(temporal_expression=''),
 'FORMULA_LENGTH_NOT_HIERARCHY_BASIS':lambda m,s:m['negative'][0].update(prohibited_inference='length allowed'),
 'NARRATOR_NOT_HIERARCHY_BASIS':lambda m,s:m.update(spine_kind='COMPOSITION_GROUP'),
 'BHSA_MOTHER_CORROBORATION_ONLY':lambda m,s:m['evidence'][0].update(corroboration_use='MILAL_PARENT'),
 'FROZEN_ARTIFACTS_UNCHANGED':hist(f.NODES),
 'FROZEN_REPOSITORY_PINS':lambda m,s:s['frozen'][0].update(actual='bad'),
 'SOURCE_SNAPSHOT_EXACT':lambda m,s:m['execution'].update(tf_version='guessed'),
 'BHSA_VERSION_AND_COVERAGE':lambda m,s:m['execution'].update(bhsa_version='wrong'),
 'REQUEST_SOURCE_EXACT':lambda m,s:s.update(request=b'changed'),
 'CRITERIA_CANONICAL':lambda m,s:m['criteria'][0].update(evidence_code='GUESSED'),
 'PACKET_FAITHFUL':lambda m,s:m.update(packet='F/G resolved'),
 'INTEGRITY_RECEIPTS_COMPUTED':lambda m,s:m['integrity'][0].update(sha256='wrong'),
 'DETERMINISTIC_RERUN':lambda m,s:m.update(rerun_digest='wrong'),
}


class FGPrepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s=f.load(True);cls.m=f.build(cls.s);cls.files=f.serialize(cls.m,cls.s)

    def test_gate_negative_coverage(self):
        self.assertEqual(set(MUTATIONS),{g['gate'] for g in f.gates(self.m,self.s)})

    def test_all_gates_pass(self):
        self.assertTrue(all(g['status']=='PASS' for g in f.rows(self.files['12_gates.csv'])))

    def test_manifest_negative(self):
        ff=dict(self.files);ff['02_temporal_expression_inventory.csv']+=b'corrupt'
        self.assertFalse(f.util.manifest_ok(ff))

    def test_deterministic_independent_build(self):
        self.assertEqual(self.files,f.serialize(f.build(deepcopy(self.s)),deepcopy(self.s)))

    def test_three_temporal_positions(self):
        a,b,c=[at(self.m,'comparison',r)['DIFFERENCE'] for r in ('3:1','42:7','42:16')]
        self.assertEqual([a['phrase_function'],b['phrase_function'],c['phrase_function']],['Time','Conj','Time'])
        self.assertTrue(a['before_first_verb']);self.assertTrue(b['clause_initial']);self.assertTrue(c['after_first_verb'])

    def test_ambiguous_sense_not_forced(self):
        self.assertEqual(at(self.m,'temporal','19:26')['sense'],'UNRESOLVED_SENSE')
        self.assertEqual(at(self.m,'temporal','8:19')['sense'],'NON_TEMPORAL_OTHER_HOMONYM')

    def test_whole_book_not_selected_verse_filter(self):
        s=deepcopy(self.s);c=deepcopy(s['native'][0]);c['clause']=90000000;c['ref']='17:2';c['synthetic_anchor']=''
        c['words']=[deepcopy(s['native'][0]['words'][0])]
        c['words'][0].update(node=90000001,reference='17:2',lex='>XR/',phrase_ids=[90000002])
        c['phrases']=[dict(node=90000002,function='Time',type='NP',word_nodes=[90000001],surface='synthetic after')]
        s['native'].append(c);s['execution']['book_word_nodes'].append(90000001)
        f.validate(s)
        inv=f.inventory(s,f.evidence(s))
        self.assertTrue(any(r['reference']=='17:2' for r in inv))

    def test_missing_required_feature_fails(self):
        s=deepcopy(self.s);s['native'][0]['words'][0].pop('lex')
        with self.assertRaisesRegex(ValueError,'word schema'):f.validate(s)

    def test_duplicate_word_fails(self):
        s=deepcopy(self.s);s['native'][0]['words'][1]['node']=s['native'][0]['words'][0]['node']
        with self.assertRaisesRegex(ValueError,'coverage'):f.validate(s)

    def test_missing_whole_book_word_fails(self):
        s=deepcopy(self.s);s['execution']['book_word_nodes'].append(99999999)
        with self.assertRaisesRegex(ValueError,'coverage'):f.validate(s)

    def test_exact_word_pattern_does_not_accept_prefix(self):
        words=[dict(node=1,lex='XJH[',surface='ויחי')]
        self.assertFalse(f.matches(words,['HJH[']))

    def test_wayhi_flag_requires_exact_person_gender_number(self):
        for field,value in [('ps','p1'),('gn','f'),('nu','pl')]:
            s=deepcopy(self.s)
            c=next(c for c in s['native'] if c['ref']=='1:6')
            next(w for w in c['words'] if w['lex']=='HJH[')[field]=value
            self.assertFalse(next(e for e in f.evidence(s) if e['clause_node']==c['clause'])['lexical_wayhi_words'])

    def test_wayx_be_is_not_mr1_way0_positive(self):
        r=next(r for r in self.m['g'] if r['reference']=='42:12' and r['lexical_wayhi_words'])
        self.assertEqual(r['clause_type'],'WayX')
        self.assertFalse(any(int(x['start_clause'])==r['clause_node'] for x in f.rows(self.s['mr_files']['04_way0_wayhi_reproduction.csv'])))

    def test_candidates_are_not_accepted_objects(self):
        self.assertEqual(len(self.m['candidates']),3)
        for c in self.m['candidates']:
            self.assertFalse(c['automatic_resolution']);self.assertEqual(c['new_relation_ids'],[])
            for field in f.REVIEW_FIELDS:self.assertEqual(c[field],'UNREVIEWED' if field=='review_status' else '')

    def test_researcher_questions_exact(self):
        self.assertIn('Do the established peer pairs support two same-level YHWH–Job response complexes: 38:1–40:5 and 40:6–42:6?',self.m['packet'])
        self.assertIn('What relation connects the YHWH–Job speech complex ending at 42:6 with the final narrative beginning at 42:7?',self.m['packet'])

    def test_no_corroboration_in_discovery(self):
        s=deepcopy(self.s)
        for c in s['native']:
            c['corroboration']=[dict(node=c['clause'],mother=[12345],tab=99,pargr=99,rela='FAKE',code='FAKE')]
        ev=f.evidence(s)
        self.assertEqual(f.inventory(s,ev),self.m['temporal'])
        self.assertEqual(f.formula_audit(s,s['cfg']['formula_refs']),self.m['formulas'])

    def test_historical_members_byte_exact(self):
        for k,v in self.s['files'].items():self.assertEqual(self.files[f.HISTORY+k],v)
        for k,v in self.s['mr_files'].items():self.assertEqual(self.files['history/mr1/'+k],v)

    def test_new_counts_are_zero(self):
        cc=f.counts(self.m)
        for field in ('new_human_judgment_count','new_textual_relation_count','new_accepted_overlay_relation_count'):self.assertEqual(cc[field],0)

    def test_speaker_identity_not_inferred_inside_speech(self):
        r=at(self.m,'f','38:3')
        self.assertEqual(r['speaker_evidence']['identity_status'],'UNRESOLVED_IN_THIS_CLAUSE')

    def test_snapshot_hashes_resolve(self):
        cc={c['clause']:c for c in self.m['native']}
        for e in self.m['evidence']:self.assertEqual(e['source_record_sha256'],f.prior.d.h.f.rowhash(cc[e['clause_node']]))

    def test_criteria_source_links(self):
        for r in self.m['criteria']:
            link=r['source_link'];data=self.files[link['member']];raw=f.prior.d.h.raw_rows(data)[link['data_row']-1]
            self.assertEqual(f.sha(data),link['member_sha256']);self.assertEqual(f.prior.d.h.f.rowhash(raw),link['row_sha256'])


def negative(name,mutation):
    def run(self):
        m,s=deepcopy(self.m),deepcopy(self.s);mutation(m,s)
        gg={g['gate']:g['status'] for g in f.gates(m,s)}
        self.assertEqual(gg[name],'FAIL')
        with self.assertRaises(ValueError):f.serialize(m,s)
    return run


for name,mutation in MUTATIONS.items():setattr(FGPrepTests,'test_negative_'+name.lower(),negative(name,mutation))


if __name__=='__main__':unittest.main()
