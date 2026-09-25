"""Scope correction: primary Job versus explicit controls and search-only corpus."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from test_mfr02r_grammar import ROOT, sample
from milal_mfr02r_scope import require_job_scope, read_references, fixture_references, evaluate_fixture
from milal_mfr02r_io import worker
from milal_mfr02r_grammar import load_registry


class ScopeTests(unittest.TestCase):
    def test_primary_scope_rejects_nonjob_and_full_book_configuration(self):
        config=json.loads((ROOT/'config/mfr_0_2r_job.json').read_text())
        require_job_scope(config)
        for key,value in [('scopes',['job','pentateuch']),('additional_raw_scopes',{'isaiah':'Jesaia'}),
                          ('primary_analysis_scope','HB_CORPUS'),('corpus_comparison_scope','JOB'),
                          ('control_fixture_scope','FULL_BOOK')]:
            altered=copy.deepcopy(config);altered[key]=value
            with self.assertRaises(ValueError): require_job_scope(altered)

    def test_worker_rejects_full_pentateuch_before_read_or_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            for scope in ('pentateuch','death','daniel_ezra','isaiah','HB_CORPUS'):
                with self.assertRaisesRegex(ValueError,'JOB only'):
                    worker('MISSING',scope,'MISSING','MISSING',Path(tmp)/scope)
                self.assertFalse((Path(tmp)/scope).exists())

    def test_fixture_has_explicit_references_not_chapter_expansion(self):
        config=json.loads((ROOT/'config/mfr_0_2r_controls.json').read_text())
        refs=fixture_references(config)
        self.assertIn(('Numeri',26,52),refs['pentateuch'])
        self.assertIn(('Deuteronomium',32,48),refs['pentateuch'])
        self.assertNotIn(('Leviticus',25,4),refs['pentateuch'])
        self.assertNotIn(('Genesis',1,1),refs['pentateuch'])
        self.assertTrue(all(len(r)==3 for group in refs.values() for r in group))

    def test_reference_reader_keeps_whole_clause_and_only_enclosed_context(self):
        from milal_mfr_observation import WORD_FEATURES
        types={**{w:'word' for w in range(1,7)},100:'book',101:'chapter',111:'verse',112:'verse',113:'verse',
            200:'clause',201:'clause',202:'clause',301:'clause_atom',302:'clause_atom',303:'clause_atom',304:'clause_atom',
            401:'phrase',402:'phrase',403:'phrase',404:'phrase'}
        slots={100:[1,2,3,4,5,6],101:[1,2,3,4,5,6],111:[1],112:[2,3,4],113:[5,6],200:[1,4],201:[2,3],202:[5,6],
            301:[1],302:[4],303:[2,3],304:[5,6],401:[1],402:[4],403:[2,3],404:[5,6]}
        values={k:{w:None for w in range(1,7)} for k in WORD_FEATURES}
        values.update(otype=types,oslots=slots,book={100:'Synthetic'},chapter={101:1},verse={111:1,112:2,113:3},
            typ={200:'WayX',201:'NmCl',202:'WayX',301:'WayX',302:'WayX',303:'NmCl',304:'WayX',401:'VP',402:'NP',403:'NP',404:'NP'},
            function={401:'Pred',402:'Objc',403:'Subj',404:'Subj'},domain={200:'N',201:'N',202:'N'})
        for w in range(1,7):
            for f in ('lex','lex_utf8','g_word_utf8'): values[f][w]='X'
            values['sp'][w]='verb' if w in (1,5) else 'subs'
            values['vt'][w]='impf' if w in (1,5) else None
            values['trailer_utf8'][w]=' '
        def read(path,keep=None):
            data=values[Path(path).stem]
            return {k:v for k,v in data.items() if keep is None or k in keep},{'feature':Path(path).name,'version':'2021','sha256':'SYNTHETIC'}
        with patch('milal_mfr_observation.read_feature',side_effect=read):
            observed,receipt=read_references('SYNTHETIC',[('Synthetic',1,1)])
            self.assertEqual({r['clause_id'] for r in observed},{200,201})
            self.assertEqual(observed[0]['word_ids'],[1,4])
            self.assertEqual(receipt['selection_reasons'][201],'ENCLOSED_INTERRUPTION_CONTEXT')
            contextual,context_receipt=read_references('SYNTHETIC',[('Synthetic',1,3)],include_preceding_verse=True)
            self.assertEqual({r['clause_id'] for r in contextual},{200,201,202})
            self.assertEqual(context_receipt['minimum_context_references'],[('Synthetic',1,2)])
            self.assertEqual(context_receipt['selection_reasons'][201],'MINIMUM_PRECEDING_VERSE_CONTEXT')
            with self.assertRaisesRegex(ValueError,'missing'):
                read_references('SYNTHETIC',[('Synthetic',1,99)])

    def test_fixture_evaluation_never_calls_primary_engine(self):
        registry=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
        with patch('milal_mfr02r_engine.run_engine',side_effect=AssertionError('primary engine forbidden')):
            result=evaluate_fixture(sample(),registry,[])
        self.assertTrue(result['candidates'])
        self.assertTrue(all(not r['accepted_mother'] for r in result['candidates']))
        self.assertTrue(all(r['context_status']=='EXPLICIT_FIXTURE_ONLY_NOT_FULL_PRECEDING_UNIVERSE' for r in result['candidates']))

    def test_fixture_candidates_are_json_serializable_like_primary_facts(self):
        from milal_mfr02r_data import encode
        from milal_mfr02r_synthetic import clause
        from milal_mfr_observation import observe
        registry=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
        observations=sample()+observe([clause(8,subject='UNSHARED/',complement='OTHER/')])
        for row in observations:
            for word in row['words']:
                for field in ('ps','gn','nu'): word[field]=None
        result=evaluate_fixture(observations,registry,[])
        encode(result['candidates'])
        self.assertTrue(all(type(v) is bool for r in result['candidates'] for v in r['facts'].values()))


if __name__=='__main__': unittest.main()
