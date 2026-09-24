"""Invariants computed from frozen rows, generated rows and release receipts."""
from collections import Counter
from milal_mfr01a_data import js

def objects(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from objects(v)
    elif isinstance(value,list):
        for v in value:yield from objects(v)

def core_gates(d,o):
    result={}
    def gate(name,fn):
        try:result[name]=bool(fn())
        except (KeyError,TypeError,ValueError,IndexError):result[name]=False
    bb={b['bundle_id']:b for b in o['bundles']};pp={p['marker_id']:p for p in o['profiles']};rr={r['case_id']:r for r in o['cases']}
    bundle_keys=set(bb);profile_keys=set(pp);case_keys=set(rr)
    family_review_keys={r['bundle_id'] for r in o['family_review']}
    rawr={r['relation_candidate_id']:r for r in d['relations']};rawf=d['f'];closed={r['relation_candidate_id'] for r in d['relations'] if 'CLOSURE_TARGET_CANDIDATE' in r['relation_candidates']}
    mapped={r['raw_relation_candidate_id']:r for r in o['crosswalk']}
    raw_ids={k:{r[field] for r in d[table]} for k,table,field in [('marker','markers','marker_id'),('family','families','family_id'),('relation','relations','relation_candidate_id'),('coverage','coverage','coverage_candidate_id'),('nested','nested','nested_evidence_id'),('force','force','marker_id')]}
    raw_ids['membership']={r['family_id']+'|'+r['marker_id'] for r in d['membership']}
    trace={k:{r['raw_id'] for r in o['trace'] if r['raw_kind']==k} for k in raw_ids}
    family_ids=[f for b in bb.values() for f in b['contributing_family_ids']]
    coverage={r['coverage_candidate_id'] for r in d['coverage']};nested={r['nested_evidence_id'] for r in d['nested']}
    gate('NO_RAW_MARKER_LOSS',lambda:set(pp)==set(d['m']) and len(pp)==len(o['profiles']) and all(str(p['anchor'])==str(d['m'][mid]['anchor']) and str(p['clause_id'])==str(d['m'][mid]['clause_id']) and p['clause_atom_ids']==d['m'][mid]['clause_atom_ids'] and p['discovery_sources']==d['m'][mid]['discovery_sources'] for mid,p in pp.items()))
    gate('NO_RAW_FAMILY_LOSS',lambda:Counter(family_ids)==Counter(rawf.keys()))
    gate('NO_RAW_RELATION_LOSS',lambda:set(mapped)==set(rawr) and len(mapped)==len(o['crosswalk']))
    gate('NO_COVERAGE_LOSS',lambda:trace['coverage']==coverage and {c for p in pp.values() for c in p['coverage_candidate_links']}==coverage)
    gate('NO_NESTED_EVIDENCE_LOSS',lambda:trace['nested']==nested and {n for p in pp.values() for n in p['nested_evidence_links']}==nested)
    gate('CANONICAL_OCCURRENCE_SET_BUNDLES_CREATED',lambda:{tuple(b['marker_ids']) for b in bb.values()}=={tuple(sorted(f['marker_ids'])) for f in rawf.values()} and all(b['marker_ids']==sorted(set(b['marker_ids'])) for b in bb.values()))
    gate('MULTI_RESOLUTION_DUPLICATES_CONSOLIDATED_FOR_REVIEW',lambda:len({tuple(b['marker_ids']) for b in bb.values()})==len(bb) and len(bb)<len(rawf))
    gate('RAW_FAMILY_IDS_PRESERVED',lambda:len(o['membership'])==len(rawf) and {r['family_id'] for r in o['membership']}==set(rawf) and all(js(f)==js(rawf[f['family_id']]) for b in bb.values() for f in b['family_evidence']))
    gate('RAW_RELATION_IDS_PRESERVED',lambda:all(mapped[k]['raw_labels']==rawr[k]['relation_candidates'] and k in rr[mapped[k]['case_id']]['raw_relation_ids'] for k in rawr))
    def lattice_valid(r):
        a=set(bb[r['bundle_a']]['marker_ids']);b=set(bb[r['bundle_b']]['marker_ids'])
        expected='SAME_OCCURRENCE_SET' if a==b else 'STRICT_SUBSET' if a<b else 'STRICT_SUPERSET' if a>b else 'PARTIAL_OVERLAP'
        return r['status']=='EVIDENCE_ONLY' and bool(a&b) and set(r['shared_markers'])==a&b and r['set_relation']==expected
    gate('FAMILY_LATTICE_PRESENT',lambda:bool(o['lattice']) and all(lattice_valid(r) for r in o['lattice']))
    gate('EXPANSION_RELATIONS_EVIDENCE_ONLY',lambda:all(r['status']=='EVIDENCE_ONLY' and r['expansion_source_bundle'] in bb and r['expansion_target_bundle'] in bb and (r['added_features'] or r['removed_features']) for r in o['expansion']))
    gate('SINGLETON_EXPLICIT_PRESERVED',lambda:all('SINGLETON_EXPLICIT_BUNDLE' in b['categories'] and b['bundle_id'] in family_review_keys for b in bb.values() if len(b['marker_ids'])==1 and d['m'][b['marker_ids'][0]]['formal_explicitness']))
    gate('SINGLETON_GENERIC_ARCHIVE_SUPPORTED',lambda:all(r['disposition']=='ARCHIVE_FOR_REFERENCE' and not r['inclusion_evidence'] and 'SINGLETON_GENERIC_BUNDLE' in r['categories'] for r in o['family_archive']) and {r['bundle_id'] for r in o['family_review']}|{r['bundle_id'] for r in o['family_archive']}==set(bb))
    gate('RELATION_CASES_CONSOLIDATED',lambda:len({(r['source_marker_id'],r['target_marker_id']) for r in rr.values()})==len(rr) and len(rr)==len({(r['source_marker_id'],r['target_marker_id']) for r in rawr.values()}))
    gate('FORMAL_ONLY_ARCHIVE_SUPPORTED',lambda:all(not r['default_review'] for r in rr.values() if set(r['raw_labels'])<={'FORMAL_PARALLEL_CANDIDATE','FORMAL_CORRESPONDENCE_ONLY'} and not r['expansion_comparison_family_ids'] and not r['sequence_comparison_family_ids']))
    gate('CLOSURE_MARKER_NOT_EQUAL_CLOSURE_TARGET',lambda:all(r['review_eligible']==any(s in r['closure_status'] for s in ('CLOSURE_STRUCTURALLY_LINKED','CLOSURE_FORMALLY_LINKED','CLOSURE_COVERAGE_LINKED')) for r in o['closures']))
    gate('CLOSURE_WEAK_PAIRS_PRESERVED',lambda:{r['raw_relation_candidate_id'] for r in o['closures']}==closed and {r['raw_relation_candidate_id'] for r in o['closure_review']}|{r['raw_relation_candidate_id'] for r in o['closure_archive']}==closed)
    gate('CLOSURE_REVIEW_LINK_EVIDENCE_REQUIRED',lambda:all(r['target_is_cessation'] and (r['coverage_end_ids'] or r['formal_family_ids'] or (r['onset_form_evidence'] and (r['participant_surface_continuity'] or r['domain_compatible'] or r['terminal_nested_evidence_ids']))) for r in o['closure_review']))
    allobj=list(objects(o))
    gate('NO_NUMERIC_RANKING',lambda:not any(set(r)&{'rank','score','importance_score','confidence_score','hierarchical_force_score'} for r in allobj))
    gate('NO_HIERARCHY_ADJUDICATION',lambda:not any(set(r)&{'selected_relation','selected_mother','selected_root','textual_level','accepted_closure','accepted_family'} for r in allobj) and all(r.get('automatic_resolution') is not True for r in allobj))
    gate('CROSS_BOOK_RELATIONS_PRESERVED',lambda:all(mapped[k]['case_id'] in rr and rr[mapped[k]['case_id']]['cross_book'] for k,r in rawr.items() if r['cross_book']))
    gate('HUMAN_REVIEW_UNIVERSE_REDUCED',lambda:len(o['family_review'])<len(d['families']) and len(o['relation_review'])<len(d['relations']))
    gate('HUMAN_REVIEW_CASES_TRACEABLE',lambda:all(trace[k]==v for k,v in raw_ids.items()) and all(set(r['bundle_ids'])<=bundle_keys and set(r['marker_profile_ids'])<=profile_keys and set(r['relation_case_ids'])<=case_keys for r in o['trace']) and all(p['force_evidence']==d['h'][mid] for mid,p in pp.items()))
    for name,fields in [('NO_HUMAN_JUDGMENT',{'human_judgment','human_decision'}),('NO_ACCEPTED_RELATION',{'accepted_relation','accepted_parataxis','accepted_hypotaxis'}),('NO_PARENT_EDGE',{'parent_id','mother_id','parent_edge'}),('NO_TREE_SYNTHESIS',{'root_id','tree_edges','hierarchy_assembly'})]:
        gate(name,lambda fields=fields:not any(set(r)&fields for r in allobj))
    return result

def release_gates(e):
    p=e['post'];controls=e['controls'];receipts=e['receipts'];events=e['events']
    return dict(
        BASELINE_COMMIT_VERIFIED=e['baseline']['expected']==e['baseline']['object'] and e['baseline']['ancestor'],
        MFR_0_1_FROZEN_VERIFIED=bool(receipts) and all(r['actual_sha256']==r['expected_sha256'] for r in receipts),
        CONSOLIDATION_HUMAN_INPUT_COUNT_ZERO=all(not r['human_dependency'] for r in e['reads']),
        CONSOLIDATION_STRUCTURAL_LABEL_INPUT_ZERO=all(not r['structural_dependency'] for r in e['reads']) and not e['static_issues'],
        CONSOLIDATION_FROZEN_BEFORE_CONTROL_LOOKUP=all(events.index(s+'_FREEZE')<events.index('CONTROLS_LOADED') for s in e['scopes']),
        PENTATEUCH_EDSF_CONSOLIDATION_VALID=controls['pentateuch_expected']>0 and controls['pentateuch_valid']==controls['pentateuch_expected'],
        PROPHET_CONTROL_CONSOLIDATION_VALID=controls['prophet_cross_formal']>0 and controls['prophet_cross_formal']==controls['prophet_preserved'],
        DEATH_RESUMPTION_CONSOLIDATION_VALID=controls['death_expected']>0 and controls['death_preserved']==controls['death_expected'],
        DANIEL_EZRA_CONSOLIDATION_VALID=controls['daniel_expected']>0 and controls['daniel_preserved']==controls['daniel_expected'],
        JOB_37_24_NONRECOVERY_PRESERVED=not controls['nonrecovery_raw_markers'] and not controls['nonrecovery_profiles'] and controls['nonrecovery_checked'],
        HUMAN_REVIEW_FIELDS_BLANK=bool(p['cases']) and all(all(v==('UNREVIEWED' if k=='review_status' else '') for k,v in r.items() if k in p['review_fields']) for r in p['cases']),
        R4_4_CONSUMER_ABSENT=not e['consumer_files'],PARTICIPANT_ARC_UNTOUCHED=p['participant_arc']=='UNADJUDICATED',
        MANIFEST_VALID=bool(e['manifests']) and all(e['manifests']),
    )

def final_gates(a,b,receipt):
    return dict(DETERMINISTIC_RERUN=bool(a) and a==b,FULL_REGRESSION_PASS=receipt['tests_run']>=1957 and receipt['failures']==receipt['errors']==0,SKIP_ZERO=receipt['skipped']==0)
