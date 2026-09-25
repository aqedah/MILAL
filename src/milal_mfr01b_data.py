"""Frozen schemas only; no discovery, fuzzy matching or historical interpretation."""
import io
import csv
import json
import hashlib
from pathlib import Path
from collections import defaultdict
from milal_mfr_common import ROOT, require, js, sha, rows, write
from milal_mfr01a_data import TABLES, table, ref

OUTPUTS = {
    'sources':'01_marker_discovery_source_role_audit.csv',
    'roles':'02_marker_role_registry.csv', 'bundles':'03_bundle_role_registry.csv',
    'cessations':'04_cessation_lexical_role_audit.csv',
    'evidence':'05_relation_evidence_provenance.csv', 'edges':'06_relation_evidence_dependency_graph.csv',
    'closures':'07_closure_independence_audit.csv', 'closure_review':'08_closure_independent_review_cases.csv',
    'closure_archive':'09_closure_derived_only_archive.csv', 'family_review':'10_family_review_role_reclassification.csv',
    'configurations':'11_configuration_relation_cases.csv', 'membership':'12_configuration_case_membership.csv',
    'h1':'13_h1_hierarchy_review_set.csv', 'r1':'14_r1_resumption_review_set.csv',
    'c1':'15_c1_closure_review_set.csv', 'reference':'16_reference_evidence_set.csv',
}
ROLE_TABLES = ('observation','markers','families')
FULL_TABLES = (*ROLE_TABLES,'membership','force','coverage','nested','relations')
HIERARCHY = {'PARATAXIS_CANDIDATE','HYPOTAXIS_CANDIDATE','EMBEDDING_CANDIDATE','COMPETING_RELATIONS'}
ACCEPTABLE_CESSATION = {'DISCOURSE_CESSATION_FORM_CANDIDATE','SPEECH_ACTIVITY_CESSATION_CANDIDATE','CESSATION_ROLE_AMBIGUOUS'}

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        while chunk:=f.read(1024*1024):h.update(chunk)
    return h.hexdigest()

def zip_rows(z,name):
    csv.field_size_limit(128*1024*1024)
    with z.open(name) as f:
        for row in csv.DictReader(io.TextIOWrapper(f,encoding='utf8',newline='')):
            for k,v in row.items():
                if v and (v[0] in '[{' or v in ('true','false','null')):
                    try:row[k]=json.loads(v)
                    except ValueError:pass
            yield row

def keyed(records,key):
    result={}
    for r in records:
        require(key in r and str(r[key]) not in result,'SCHEMA missing/duplicate '+key)
        result[str(r[key])]=r
    return result

def prepare(d):
    d['m']=keyed(d['markers'],'marker_id');d['f']=keyed(d['families'],'family_id');d['o']=keyed(d['observation'],'clause_id')
    d['b']=keyed(d['old_bundles'],'bundle_id');d['by_marker']=defaultdict(list)
    for b in d['old_bundles']:
        for mid in b['marker_ids']:
            require(mid in d['m'],'SCHEMA bundle marker absent');d['by_marker'][mid].append(b['bundle_id'])
    require(set(d['by_marker'])==set(d['m']),'SCHEMA marker/bundle mismatch')
    for i,c in enumerate(d['observation']):
        require(int(c['sequence_index'])==i,'SCHEMA observation order')
        for field in ('words','phrases','predicate_lexeme','predicate_morphology','domain','participant_surface_set'):
            require(field in c,'SCHEMA missing observation '+field)
    for m in d['markers']:
        require(str(m['clause_id']) in d['o'] and m['clause_atom_ids'],'SCHEMA marker anchor')
        require(d['observation'][int(m['sequence_index'])]['clause_id']==m['clause_id'],'SCHEMA marker sequence identity')
    if 'relations' in d:
        d['r']=keyed(d['relations'],'relation_candidate_id');d['c']=keyed(d['coverage'],'coverage_candidate_id');d['n']=keyed(d['nested'],'nested_evidence_id')
        d['h']=keyed(d['force'],'marker_id');d['old_case']=keyed(d['old_cases'],'case_id')
        d['old_cross']=keyed(d['old_crosswalk'],'raw_relation_candidate_id')
        require(set(d['old_cross'])==set(d['r']),'SCHEMA frozen relation crosswalk mismatch')
        d['by_nested']=defaultdict(list)
        for n in d['nested']:
            require(n['coverage_candidate_id'] in d['c'],'SCHEMA nested coverage absent')
            d['by_nested'][n['coverage_candidate_id']].append(n)
        for r in d['relations']:
            require(r['source_marker_id'] in d['m'] and r['target_marker_id'] in d['m'],'SCHEMA relation endpoint')
            require(set(r['coverage_relationship'])<=set(d['c']),'SCHEMA relation coverage')
    return d

def panel(d,mid):
    m=d['m'][mid];i=int(m['sequence_index']);c=d['o'][str(m['clause_id'])]
    def short(n):return dict(clause_id=n['clause_id'],reference=ref(n),surface=n['surface_hebrew'],domain=n['domain'],participant_surface=n['participant_surface_set'])
    return dict(marker_id=mid,anchor=m['anchor'],clause_atom_ids=m['clause_atom_ids'],**short(c),
                before=[short(x) for x in d['observation'][max(0,i-2):i]],after=[short(x) for x in d['observation'][i+1:i+3]])
