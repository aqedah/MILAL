"""Portable reference visibility probes, independent of empirical diagnostic IDs."""
import copy
from pathlib import Path
from milal_q12_synthetic import clause,GRAMMAR
from milal_q12_profiles import ConfigurationIndex
from milal_q12_references import ReferenceIndex
from milal_q15_domains import Domains
from milal_q15_references import Visibility
from milal_q1_binding import outcome
from milal_q13_model import AssignmentModel
from milal_mfr02r_data import table,manifest,digest
from milal_mfr02r_pipeline import code_fingerprint
from milal_q13_pipeline import write


def fixture(count=100,person='p3',two=False):
    data=[clause(1000+i,10000+10*i,i,subject='PERSON/') for i in range(count)]
    target=clause(2000,20000,count,subject=None,head=1000)
    for e in target['CLAUSE']['native_annotations']:e.update(status='DATABASE_EXISTING_RELATION')
    target['REFERENCE']['mentions']=[dict(node=20000,lex='SAY[',kind='IMPLICIT_SUBJECT',png=[person,'m','sg'],identity='UNRESOLVED')]
    if two:
        word=copy.deepcopy(data[0]['WORD'][1]);word['node']=10002
        data[0]['WORD'].append(word);data[0]['word_ids'].append(10002);data[0]['PHRASE'][1]['word_ids'].append(10002)
    return data+[target]


def run_fixture(data,spans=()):
    old=ReferenceIndex(ConfigurationIndex(data,GRAMMAR['lexicons'])).witnesses
    v=Visibility(Domains(data,spans,GRAMMAR['lexicons']),old);records=[];v.process(records.append)
    return v,records


def target_record(v,target='2000'):
    rid=next(f['reference_witness_id'] for f in v.forms if f['target_clause_id']==target and f['reference_bearing'])
    return v.by_reference[rid]


def hidden():
    a=clause(10,100,0,subject=None);b=clause(11,110,1,head=10);c=clause(12,120,2,subject=None,head=11)
    for r in (b,c):
        for e in r['CLAUSE']['native_annotations']:e['status']='DATABASE_EXISTING_RELATION'
    c['REFERENCE']['mentions']=[dict(node=120,lex='SAY[',kind='PRONOMINAL_SUFFIX',png=['p3','m','sg'],identity='UNRESOLVED')]
    span=dict(span_id='SS-toy',start_clause='10',clause_ids=['10','11'],construction_independence_status='INDEPENDENT_NATIVE_BINDING',boundary_witnesses={'native':b['CLAUSE']['native_annotations']})
    return run_fixture([a,b,c],[span])


def semantic_checks():
    v,records=run_fixture(fixture());r=target_record(v);multi,_=run_fixture(fixture(two=True));m=target_record(multi)
    hv,_=hidden();bs=[b for b in hv.bindings if b['mechanism']=='SB03' and b['source_id']=='10' and b['antecedent_clause']=='11']
    circular=False
    try:v.d.add('BAD',['1000','2000'],{'tested_relation_used_for_domain':True})
    except ValueError:circular=True
    far=fixture(2);far[1]['WORD'][1]['gn']='f';far[-1]['CLAUSE']['native_annotations'].append(dict(head_node=1001,dependent_node=2000,rela='Objc',resolution='EXACT_NODE_MEMBERSHIP',status='DATABASE_EXISTING_RELATION'))
    fv,_=run_fixture(far);fr=target_record(fv)
    speaker,_=run_fixture(fixture(2,person='p1'));sr=target_record(speaker)
    result=hv.evaluate('10','12',[dict(rule_id='RG-A01',relation='HYPOTACTIC')])
    o=outcome('10','12','HYPOTACTIC');o['provenance_paths']=result['qualified_paths']
    p=outcome('11','12','PARATACTIC');p['provenance_paths']=[{'synthetic':True}]
    model=AssignmentModel([o,p],['10','11','12']).analyze()
    checks=dict(S1=r['global_candidate_count']==100 and r['visible_candidate_count']==1 and r['referential_identity_status']=='PROVISIONAL_UNIQUE_VISIBLE',
        S2=m['reference_status']=='MULTIPLE_VISIBLE_CANDIDATES' and m['source_bound_candidate_count']==0,
        S3=any(x['reference_status']=='LEXICAL_RECURRENCE_ONLY' for x in v.reclassified) and not any(b['source_binding_candidate'] for b in v.bindings if b['mechanism']=='SB10'),
        S4=bool(bs) and bs[0]['source_binding_candidate'],S5=circular,
        S6=fr['visible_antecedent_ids']==['ANT-10001'],S7=r['global_candidate_count']==100 and len([x for x in records if x['reference_witness_id']==r['reference_witness_id'] and x['original_global_candidate']])==100,
        S8=sr['visible_candidate_count']==1 and sr['source_bound_candidate_count']==1,
        S9=all(x['referential_identity_status']=='UNRESOLVED' for x in v.reclassified if x['reference_form_type'].startswith('EXPLICIT_')),
        S10=bool(result['qualified_paths']) and not any(p['human_review_required'] for p in model['pivots']),
        S11=r['referential_identity_status']=='PROVISIONAL_UNIQUE_VISIBLE',S12=bool(bs) and bs[0]['internal_antecedent']=='ANT-111')
    return checks,v,records


def self_test(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);checks,v,records=semantic_checks()
    for name in ('a','b'):
        dest=out/name;dest.mkdir();_,vv,rr=semantic_checks()
        table(dest/'forms.csv',vv.forms);table(dest/'classification.csv',vv.reclassified);table(dest/'visibility.csv',rr);manifest(dest)
    checks['DETERMINISTIC']=digest(out/'a/99_manifest_sha256.csv')==digest(out/'b/99_manifest_sha256.csv')
    (out/'review.md').write_text('# Reference visibility synthetic review\n\n100 global matches remain recoverable; one independently visible candidate is provisional, not confirmed. Two visible matches remain ambiguous. Repeated names/NPs do not bind. The hidden antecedent is inside an independently sourced span, not necessarily its opening.\n',encoding='utf8')
    receipt=dict(mode='SYNTHETIC',checks=checks,passed=all(checks.values()),code_fingerprint=code_fingerprint());write(out/'receipt.json',receipt)
    if not receipt['passed']:raise ValueError('synthetic failed: '+repr(checks))
    return receipt
