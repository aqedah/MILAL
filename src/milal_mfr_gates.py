"""Computed release invariants and streaming artifact inspection."""
from pathlib import Path
from collections import Counter
import csv,json
import milal_mfr_common as cm

def scan(directory):
    d=Path(directory);meta=json.loads((d/'metadata.json').read_bytes());facts=dict(meta=meta,markers=0,repeated=0,singleton=0,relations=0,cross=0,auto=0,forbidden_fields=0,signature_resolutions=set(),family_types=set(),scope_bad=0,nested_nonempty=0,coverage_multi=0,coverage_by_marker=Counter(),label_counts=Counter(),unknown_scope=0)
    prohibited={'selected_relation','selected_mother','selected_root','root_id','parent_id','hierarchical_force_score','rank','best_marker','structural_function','relation_layer','accepted_relation'}
    csv.field_size_limit(128*1024*1024)
    for path in sorted(d.glob('*.csv')):
        if path.name=='02_blind_input_manifest.csv':continue
        with path.open(encoding='utf8',newline='') as f:
            reader=csv.DictReader(f);facts['forbidden_fields']+=len(set(reader.fieldnames or [])&prohibited)
            for r in reader:
                facts['auto']+=r.get('automatic_resolution','false')!='false'
                if 'scope_external_status' in r:facts['scope_bad']+=r['scope_external_status']!='OUTSIDE_SCOPE_NOT_TESTED';facts['unknown_scope']+=1
                if path.name.startswith('04_'):facts['signature_resolutions'].add(r['resolution'])
                if path.name.startswith('05_'):facts['markers']+=1;facts['repeated']+=int(r['repeat_count'])>=2;facts['singleton']+=bool(r['singleton_reason'])
                if path.name.startswith('06_'):facts['family_types'].add(r['family_type'])
                if path.name.startswith('09_'):facts['coverage_by_marker'][r['marker_id']]+=1
                if path.name.startswith('10_'):facts['nested_nonempty']+=int(r['nested_marker_count'])>0
                if path.name.startswith('11_'):
                    facts['relations']+=1;facts['cross']+=r['cross_book']=='true';facts['label_counts'].update(json.loads(r['relation_candidates']))
                    facts['scope_bad']+=r['same_book_required']!='false'
    facts['coverage_multi']=sum(n>1 for n in facts.pop('coverage_by_marker').values());facts['signature_resolutions']=sorted(facts['signature_resolutions']);facts['family_types']=sorted(facts['family_types']);facts['label_counts']=dict(facts['label_counts'])
    sources=cm.rows((d/'02_blind_input_manifest.csv').read_bytes());facts['sources']=sources
    facts['manifest_valid']=cm.verify(d,'12_job_blind_manifest.csv')
    return facts


def evaluate(e):
    phase=e['phases'];job=phase['job'];allp=list(phase.values());behavior=e['behavior'];audit=e['audit'];sequence=e['events'];post=e['post'];static=e['static'];controls=e['control_checks']
    def b(name):return behavior[name]
    def zero(key):return all(not r[key] for p in allp for r in p['sources'])
    result={
      'BASELINE_COMMIT_VERIFIED':e['baseline']['expected_baseline']==e['baseline']['baseline_object'],
      'HISTORICAL_GIT_HISTORY_PRESERVED':e['baseline']['baseline_is_ancestor'] and all(r['sha256']==r['expected_sha256'] for r in audit if r['expected_sha256']!='LOCAL_RAW_SOURCE'),
      'ASSET_PROVENANCE_AUDIT_COMPLETE':set(e['expected_assets'])=={r['asset_path'] for r in audit} and all(r['reuse_class'] in ('OBSERVATION_SAFE','DERIVED_BLIND_SAFE','POSTBLIND_ONLY','CONTAMINATED_OR_UNCLEAR') for r in audit),
      'BLIND_HUMAN_INPUT_COUNT_ZERO':zero('human_dependency'),
      'BLIND_STRUCTURAL_LABEL_INPUT_COUNT_ZERO':zero('structural_label_dependency'),
      'BLIND_TECHNICAL_ROOT_INPUT_ZERO':zero('technical_root_dependency'),
      'JOB_ALL_CLAUSES_OBSERVED':job['meta']['clause_count']==e['expected_clauses'] and job['meta']['counts']['observation']==e['expected_clauses'],
      'MULTI_RESOLUTION_SIGNATURES_PRESENT':set(job['signature_resolutions'])=={'SIG_EXACT','SIG_LEXICAL_SLOT','SIG_CONSTRUCTION','SIG_ADJUNCT','SIG_SEQUENCE_2','SIG_SEQUENCE_3','SIG_SEQUENCE_4'},
      'MARKER_DISCOVERY_GENERIC':not static and b('metadata_invariance'),
      'REPEATED_MARKERS_DISCOVERED':job['repeated']>0,
      'SINGLETON_EXPLICIT_MARKERS_PRESERVED':job['singleton']>0 and b('singleton'),
      'MARKER_FAMILIES_GENERATED':len(job['family_types'])==7 and job['meta']['counts']['membership']>=job['markers'],
      'FAMILY_NOT_EQUAL_HIERARCHY':all(p['auto']==0 for p in allp) and b('same_form'),
      'HIERARCHICAL_FORCE_EVIDENCE_PRESENT':job['meta']['counts']['force']==job['markers'] and job['markers']>0,
      'NO_HIERARCHICAL_FORCE_SCORE':all(p['forbidden_fields']==0 for p in allp),
      'COVERAGE_MULTIPLE_CANDIDATES_ALLOWED':job['coverage_multi']>0 and b('coverage_multiple'),
      'NO_COVERAGE_AUTOWINNER':all(p['auto']==0 for p in allp) and b('no_winner'),
      'NESTED_MARKER_EVIDENCE_PRESENT':job['nested_nonempty']>0,
      'RELATION_CANDIDATES_GENERATED':job['relations']>0 and job['relations']==job['meta']['counts']['relations'],
      'NO_RELATION_AUTO_ACCEPTED':all(p['auto']==0 for p in allp),
      'NO_BOOK_BOUNDARY_FILTER':not static and b('cross_book'),
      'NO_CHAPTER_BOUNDARY_FILTER':not static and b('metadata_invariance'),
      'NO_VERSE_BOUNDARY_FILTER':not static and b('metadata_invariance'),
      'SCOPE_BOUNDARY_NOT_EQUAL_TEXTUAL_BOUNDARY':all(p['scope_bad']==0 and p['unknown_scope']>0 for p in allp),
      'PENTATEUCH_CONTROL_BLIND':phase['pentateuch']['manifest_valid'] and 'pentateuch_FREEZE' in sequence,
      'PENTATEUCH_EDSF_POSTBLIND_LOOKUP_ONLY':sequence.index('pentateuch_FREEZE')<sequence.index('KNOWN_CONTROLS_LOADED'),
      'PROPHET_CONTROL_BLIND':phase['prophets']['manifest_valid'] and 'prophets_FREEZE' in sequence,
      'DEATH_RESUMPTION_CONTROL_BLIND':phase['death']['manifest_valid'] and 'death_FREEZE' in sequence,
      'DANIEL_EZRA_CONTROL_BLIND':phase['daniel_ezra']['manifest_valid'] and 'daniel_ezra_FREEZE' in sequence,
      'CONTROL_TARGET_REF_LEAKAGE_ZERO':not static and all(not any('controls' in r['source_id'].lower() for r in p['sources']) for p in allp),
      'CROSS_BOOK_FORMAL_RELATION_REPRESENTABLE':b('cross_formal'),
      'CROSS_BOOK_PARATAXIS_CANDIDATE_REPRESENTABLE':b('cross_parataxis'),
      'CROSS_BOOK_HYPOTAXIS_CANDIDATE_REPRESENTABLE':b('cross_hypotaxis'),
      'CROSS_BOOK_RESUMPTION_CANDIDATE_REPRESENTABLE':b('cross_resumption'),
      'SAME_FORM_NOT_AUTO_SAME_LEVEL':b('same_form'),
      'DIFFERENT_FORM_NOT_AUTO_DIFFERENT_LEVEL':b('different_form'),
      'JOB_BLIND_FROZEN_BEFORE_HISTORICAL_LOAD':sequence.index('job_FREEZE')<sequence.index('HISTORICAL_LOADED'),
      'CONTROL_BLIND_FROZEN_BEFORE_KNOWN_REF_LOAD':all(sequence.index(s+'_FREEZE')<sequence.index('KNOWN_CONTROLS_LOADED') for s in phase),
      'HISTORICAL_RELATIONS_POSTBLIND_ONLY':sequence.index('KNOWN_CONTROLS_LOADED')<sequence.index('HISTORICAL_LOADED') and post['historical_unchanged'],
      'NO_ROOT_GENERATED':all(p['forbidden_fields']==0 for p in allp) and not post['new_roots'],
      'NO_TREE_SYNTHESIS':all(p['forbidden_fields']==0 for p in allp) and not post['tree_edges'],
      'NO_STRICT_MACRO_PRECLASSIFICATION':not static and all(p['forbidden_fields']==0 for p in allp),
      'PLOT_LABELS_NOT_USED_IN_DISCOVERY':not static,
      'NO_NEW_HUMAN_JUDGMENT':post['review_blank'] and not post['new_judgments'],
      'NO_NEW_ACCEPTED_PARENT':not post['new_parents'],
      'NO_NEW_ACCEPTED_SIBLING':not post['new_siblings'],
      'R4_4_CONSUMER_NOT_IMPLEMENTED':not e['consumer_files'],
      'PARTICIPANT_ARC_UNTOUCHED':post['participant_arc']=='UNADJUDICATED',
      'MANIFEST_VALID':all(p['manifest_valid'] for p in allp) and e['final_manifest_valid'],
      'BLIND_READSET_AND_HASHES_VERIFIED':all(set(p['meta']['actual_source_reads'])=={r['source_id'] for r in p['sources']} and all(cm.sha(Path(r['actual_path']).read_bytes())==r['sha256'] for r in p['sources']) for p in allp),
      'HISTORICAL_RELATION_INVENTORY_PRESERVED':post['historical_count']==e['expected_historical_count'] and post['historical_unchanged'],
      'EDSF_GENERIC_OCCURRENCES_RECOVERED':controls['dsf_expected']>0 and controls['dsf_recovered']==controls['dsf_expected'],
      'PROPHET_CROSS_BOOK_FORMAL_CASE_RECOVERED':controls['prophet_cross_formal']>0,
      'DEATH_CROSS_BOOK_RESUMPTION_RECOVERED':controls['death_cross_resumption']>0 and controls['death_formula_recovered']==controls['death_formula_expected']>0 and controls['death_pairs_recovered']==controls['death_pairs_expected']>0,
      'DANIEL_EZRA_CROSS_BOOK_CASE_PRESERVED':controls['ketuvim_cross_formal']>0,
    }
    return result

def release_gates(a,b,receipt):
    return dict(DETERMINISTIC_RERUN=bool(a) and a==b,FULL_REGRESSION_PASS=receipt['tests_run']>=1860 and receipt['failures']==receipt['errors']==0,SKIP_ZERO=receipt['skipped']==0)
