"""Explicit synthetic source package for H0; not an empirical input substitute."""
import json
from pathlib import Path
from milal_mfr02r_data import rows, table, manifest
from milal_mfr02r_synthetic import sample
from milal_mfr02r_engine import run_engine
from milal_mfr02r_grammar import load_registry
from milal_mfr02r_h0 import ROOT, run, load_config


def source_fixture(directory):
    directory=Path(directory);job=directory/'blind/job'
    registry=load_registry(ROOT/'config/clause_relation_grammar_v1.json')
    labels=json.loads((ROOT/'config/mfr_0_2r_evidence_labels.json').read_text())
    run_engine(sample(),registry,[],job,label_definitions=labels,analysis_scope='SYNTHETIC',comparison_scope='SYNTHETIC')
    table(directory/'corpus_search/01_job_hb_analogues.csv',rows(job/'corpus_analogue_evidence.csv'))
    table(directory/'mfr02a_original_decisions.csv',[dict(decision_id='SYNTHETIC-H1',source_clause_ids=[1],target_clause_ids=[7],researcher_decision='PARATACTIC',rationale='Synthetic human input only')])
    eligible=[r for r in rows(job/'10_relation_candidates.csv') if r['relations']]
    for scope in ('pentateuch','qohelet','lamentations','isaiah'):
        table(directory/'controls'/(scope+'_fixture_relation_checks.csv'),[dict(pair_id=r['pair_id'],relations=r['relations'],facts={}) for r in eligible])
    manifest(directory)
    return directory


def self_test(out):
    out=Path(out)
    if out.exists():raise ValueError('fresh self-test directory required')
    source=source_fixture(out/'source')
    config=load_config();config['job_validation_refs']=[];config['input_zip_sha256']='SYNTHETIC_NOT_UPSTREAM_ZIP'
    a=run(source,out/'a',config,synthetic=True);b=run(source,out/'b',config,synthetic=True)
    assert a==b
    assert list(rows(out/'a/99_manifest_sha256.csv'))==list(rows(out/'b/99_manifest_sha256.csv'))
    assert a['candidate_universe_total']==21
    return dict(mode='SYNTHETIC',metrics=a,independent_bytes_equal=True)
