"""Release invariants are computed from source IDs, roots and output memberships."""
from collections import Counter, defaultdict
from milal_mfr01b_data import HIERARCHY, ACCEPTABLE_CESSATION
from milal_mfr01b_evidence import components

def all_dicts(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from all_dicts(v)
    elif isinstance(value,list):
        for v in value:yield from all_dicts(v)

def core_gates(d,o,rules):
    result={}
    def gate(name,fn):
        try:result[name]=bool(fn())
        except (KeyError,ValueError,TypeError,IndexError):result[name]=False
    roles={r['marker_id']:r for r in o['roles']};bundles={r['bundle_id']:r for r in o['bundles']};cess={r['marker_id']:r for r in o['cessations']}
    gate('MARKER_ROLE_AUDIT_COMPLETE',lambda:set(roles)==set(d['m']) and len(roles)==len(o['roles']) and all(roles[mid]['raw_discovery_sources']==m['discovery_sources'] and roles[mid]['anchor']==m['anchor'] and roles[mid]['clause_atom_ids']==m['clause_atom_ids'] for mid,m in d['m'].items()))
    gate('PRIMARY_FORMAL_VS_SUPPORT_SIGNAL_DISTINGUISHED',lambda:all(set(r['support_sources'])==set(d['m'][mid]['discovery_sources'])&set(rules['support_sources']) and not set(r['formal_role_sources'])&set(rules['support_sources']) and r['primary_bearing']==bool(r['formal_role_sources']) and (r['role']=='SUPPORT_SIGNAL_ONLY')==(not r['primary_trigger_sources']) for mid,r in roles.items()))
    gate('SUPPORT_ONLY_MARKERS_PRESERVED',lambda:all(mid in roles and roles[mid]['role']=='SUPPORT_SIGNAL_ONLY' and roles[mid]['force_context_usable'] for mid,m in d['m'].items() if set(m['discovery_sources'])<=set(rules['support_sources'])))
    gate('RAW_BUNDLE_FAMILY_IDS_PRESERVED',lambda:set(bundles)==set(d['b']) and all(b['marker_ids']==d['b'][bid]['marker_ids'] and b['raw_family_ids']==d['b'][bid]['contributing_family_ids'] for bid,b in bundles.items()))
    gate('CESSATION_ROLE_AUDIT_COMPLETE',lambda:set(cess)=={mid for mid,m in d['m'].items() if 'EXPLICIT_CESSATION' in m['discovery_sources']} and all(r['predicate_word_nodes'] and r['lexical_occurrence']=='CESSATION_LEXEME_OCCURRENCE' for r in cess.values()))
    gate('CESSATION_LEXEME_NOT_EQUAL_DISCOURSE_CESSATION',lambda:all((r['role_candidate']!='DISCOURSE_CESSATION_FORM_CANDIDATE' or bool(r['speech_arguments'])) and (r['role_candidate']!='SPEECH_ACTIVITY_CESSATION_CANDIDATE' or bool(r['speech_infinitive_candidates'])) and (not r['physical_temporal_arguments'] or r['speech_arguments'] or r['speech_infinitive_candidates'] or r['role_candidate']=='NON_DISCOURSE_CESSATION_USAGE_CANDIDATE') for r in cess.values()))
    if 'relations' in d:
        ev={e['evidence_id']:e for e in o['evidence']};byraw=defaultdict(list)
        for e in o['evidence']:byraw[e['raw_relation_id']].append(e)
        cl={c['raw_relation_id']:c for c in o['closures']};cfg={c['configuration_case_id']:c for c in o['configurations']}
        root_edges={(e['node_id'],e['parent_id']) for e in o['edges'] if e['edge_type']=='DEPENDENCY_ROOT'}
        gate('RELATION_PROVENANCE_COMPLETE',lambda:len(ev)==len(o['evidence']) and set(byraw)==set(d['r']) and all(e['dependency_root_ids'] and e['upstream_evidence_ids'] for e in ev.values()))
        gate('COVERAGE_CESSATION_DERIVATION_TRACKED',lambda:all(any(e['provenance_family']=='EVID_COVERAGE_CESSATION_DERIVED' and e['dependency_root_ids']==sorted('CESSATION:'+m for m in d['c'][cid]['end_evidence']) and not e['independent_link_usable'] for e in byraw[rid] if 'COVERAGE:'+cid in e['upstream_evidence_ids']) for rid,r in d['r'].items() for cid in r['coverage_relationship'] if d['c'][cid]['end_basis']=='EXPLICIT_CLOSURE'))
        gate('NESTED_FROM_COVERAGE_DERIVATION_TRACKED',lambda:all(len(e['parent_evidence_ids'])==1 and ev[e['parent_evidence_ids'][0]]['dependency_root_ids']==e['dependency_root_ids'] and not e['independent_link_usable'] for e in ev.values() if e['provenance_family']=='EVID_NESTED_FROM_COVERAGE'))
        gate('DEPENDENT_EVIDENCE_NOT_DOUBLE_COUNTED',lambda:all(c['independent_dependency_components']==components([ev[i] for i in c['independent_evidence_ids']]) and c['cessation_derived_chains']==components([e for e in byraw[rid] if e['cessation_derived']]) and all(not ev[i]['cessation_derived'] for i in c['independent_evidence_ids']) for rid,c in cl.items()))
        gate('RAW_963_CLOSURE_PAIRS_PRESERVED',lambda:set(cl)=={rid for rid,r in d['r'].items() if 'CLOSURE_TARGET_CANDIDATE' in r['relation_candidates']} and len(cl)==len(o['closures']))
        gate('CESSATION_DERIVED_ONLY_ARCHIVE_SUPPORTED',lambda:all(c['review_eligible']==(c['source_primary_bearing'] and c['target_role'] in ACCEPTABLE_CESSATION and bool(c['independent_evidence_ids'])) for c in cl.values()) and {c['raw_relation_id'] for c in o['closure_review']}=={rid for rid,c in cl.items() if c['review_eligible']} and {c['raw_relation_id'] for c in o['closure_archive']}=={rid for rid,c in cl.items() if not c['review_eligible']} and all(not c['review_eligible'] for c in cl.values() if 'CLOSURE_CESSATION_DERIVED_ONLY' in c['statuses']))
        gate('SUPPORT_NOT_STANDALONE_CLOSURE_SOURCE',lambda:all(c['source_primary_bearing']==roles[c['source_marker_id']]['primary_bearing'] and (not c['review_eligible'] or c['source_primary_bearing']) for c in cl.values()))
        gate('DEPENDENCY_GRAPH_VALID',lambda:all(e['node_id'] in ev and ((e['parent_id'] in ev[e['node_id']]['parent_evidence_ids']) if e['edge_type']=='DERIVED_FROM_EVIDENCE' else e['parent_id'] in ev[e['node_id']]['dependency_root_ids'] if e['edge_type']=='DEPENDENCY_ROOT' else e['parent_id'] in ev[e['node_id']]['upstream_evidence_ids']) for e in o['edges']) and root_edges=={(e['evidence_id'],root) for e in ev.values() for root in e['dependency_root_ids']} )
        gate('CONFIGURATION_LEVEL_CASES_CREATED',lambda:bool(cfg) and all(len(c['raw_pair_ids'])==1 or (c['sequence_witnesses'] and c['grouping_edges']) for c in cfg.values()) and all(c['marker_ids'] and set(c['bundle_ids'])=={b for m in c['marker_ids'] for b in d['by_marker'][m]} for c in cfg.values()))
        gate('RAW_PAIR_TRACEABILITY_COMPLETE',lambda:Counter(m['raw_relation_id'] for m in o['membership'])==Counter(d['r'].keys()) and all(m['configuration_case_id'] in cfg and m['raw_relation_id'] in cfg[m['configuration_case_id']]['raw_pair_ids'] and m['raw_candidate_labels']==d['r'][m['raw_relation_id']]['relation_candidates'] and m['source_marker_id']==d['r'][m['raw_relation_id']]['source_marker_id'] and m['target_marker_id']==d['r'][m['raw_relation_id']]['target_marker_id'] for m in o['membership']))
        hierarchy={rid for rid,r in d['r'].items() if set(r['relation_candidates'])&HIERARCHY}
        gate('HIERARCHY_32_RAW_PAIRS_PRESERVED',lambda:Counter(rid for c in cfg.values() for rid in c['hierarchy_pair_ids'])==Counter(hierarchy))
        gate('HIERARCHY_CONFIGURATION_CASES_GENERATED',lambda:bool(o['h1']) and {c['configuration_case_id'] for c in o['h1']}=={cid for cid,c in cfg.items() if c['hierarchy_pair_ids']} and {r for c in o['h1'] for r in c['phase_pair_ids']}==hierarchy)
        gate('PHASE_SPECIFIC_REVIEW_SETS_GENERATED',lambda:all(all(c['configuration_case_id'] in cfg and c['marker_ids']==cfg[c['configuration_case_id']]['marker_ids'] and c['bundle_ids']==cfg[c['configuration_case_id']]['bundle_ids'] and c['phase_pair_ids']==cfg[c['configuration_case_id']][field] and c['decision']=='' for c in o[k]) and {c['configuration_case_id'] for c in o[k]}=={cid for cid,c in cfg.items() if c[field]} for k,field in [('h1','hierarchy_pair_ids'),('r1','resumption_pair_ids'),('c1','closure_review_pair_ids')]))
        gate('NO_BOOK_BOUNDARY_FILTER',lambda:all(any(rid in c['raw_pair_ids'] and c['cross_book'] for c in cfg.values()) for rid,r in d['r'].items() if r['cross_book']))
        gate('SUPPORT_NOT_STANDALONE_FORMAL_REVIEW',lambda:all(not r['standalone_formal_review'] for r in o['family_review'] if bundles[r['bundle_id']]['bundle_role']=='SUPPORT_ONLY_BUNDLE'))
    obj=list(all_dicts(o))
    for name,fields in [('NO_HUMAN_JUDGMENT',{'human_judgment','human_acceptance'}),('NO_ACCEPTED_RELATION',{'accepted_relation','accepted_closure','accepted_family'}),('NO_PARENT',{'parent','mother','mother_if_hypotactic'}),('NO_HIERARCHY',{'hierarchy','tree','root','selected_relation','textual_level'})]:
        gate(name,lambda fields=fields:not any(any(r.get(k) not in (None,'',False,[]) for k in fields) for r in obj))
    gate('NO_NUMERIC_RANKING',lambda:not any(set(r)&{'score','rank','confidence_score','importance_score'} for r in obj))
    return result

def release_gates(e):
    c=e['controls']
    return dict(BASELINE_COMMIT_VERIFIED=e['baseline'],MFR_0_1_FROZEN_VERIFIED=e['raw_integrity'],MFR_0_1A_FROZEN_VERIFIED=e['consolidated_integrity'],
        JOB_31_40_POSTFREEZE_CONTROL_PRESENT=c['speech_word'],JOB_32_1_POSTFREEZE_CONTROL_PRESENT=c['speech_activity'],NONDISCOURSE_CESSATION_CONTROLS_PRESENT=c['contrast'],
        CROSS_CORPUS_CONTROLS_PRESERVED=c['external'],NO_REFERENCE_HARDCODING_IN_DISCOVERY=not e['static_issues'],
        BLIND_READSET_VALID=bool(e['readsets']) and all(e['readsets']),OUTPUTS_FROZEN_BEFORE_CONTROLS=e['events']==['ROLE_AND_RELATION_OUTPUTS_FROZEN','CONTROLS_LOADED'],
        HUMAN_FIELDS_BLANK=bool(e['human_rows']) and all(all(r[k]=='' for k in e['human_fields']) for r in e['human_rows']),
        R4_4_CONSUMER_ABSENT=not e['consumers'],PARTICIPANT_ARC_UNTOUCHED=e['participant_arc']=='UNADJUDICATED',MANIFEST_VALID=bool(e['manifests']) and all(e['manifests']))

def final_gates(a,b,receipt):
    return dict(DETERMINISTIC_RERUN=bool(a) and a==b,FULL_REGRESSION_PASS=receipt['tests_run']>=2026 and receipt['failures']==receipt['errors']==0,SKIP_ZERO=receipt['skipped']==0)
