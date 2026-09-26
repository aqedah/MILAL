"""Portable composite fixtures with no empirical control identifiers in logic."""
import copy
from pathlib import Path
from milal_q12_synthetic import clause,GRAMMAR
from milal_q14_spans import SurfaceSpans,INDEPENDENT
from milal_q14_binding import CompositeBinding,compare
from milal_q13_model import AssignmentModel
from milal_q13_validation import edge
from milal_mfr02r_data import table,digest,manifest,verify_manifest
from milal_mfr02r_pipeline import code_fingerprint
from milal_q13_pipeline import write


def construction(cid,word,pos):
    a=clause(cid,word,pos);a['WORD'][0]['lex']='DO['
    b=clause(cid+1,word+2,pos+1,subject='OBJECT/',head=cid,typ='InfC');b['WORD'][0].update(lex='LIFT[',vt='infc');b['PHRASE'][1]['function']='Objc'
    c=clause(cid+2,word+4,pos+2,subject=None,head=cid)
    for r in (b,c):
        for e in r['CLAUSE']['native_annotations']:e.update(rela='NA',status='DATABASE_EXISTING_RELATION',source_feature_sha256='synthetic-native',relation_feature_sha256='synthetic-rela')
    return [a,b,c]


def index(data):return SurfaceSpans(data,GRAMMAR['lexicons'])


def full_span(i,root):
    return next(s['span_id'] for s in i.spans.values() if s['start_clause']==str(root) and len(s['clause_ids'])==3)


def semantic_checks():
    data=construction(1,100,0)+construction(11,200,3);i=index(data);a,b=full_span(i,1),full_span(i,11)
    c=compare(i,a,b);binder=CompositeBinding(i);licensed=[dict(rule_id='W-P01',relation='PARATACTIC')]
    qualified=binder.evaluate('1','11',licensed)
    bad=copy.deepcopy(data);bad[1]['CLAUSE']['native_annotations'][0]['status']='PROVISIONAL_RELATION_UNDER_TEST'
    bi=index(bad);blocked=CompositeBinding(bi).evaluate('1','11',licensed)
    variant=copy.deepcopy(data);variant[3]['clause_type']='xQt0';variant[3]['WORD'][0]['vt']='perf'
    vi=index(variant);cross=compare(vi,full_span(vi,1),full_span(vi,11))
    many=[]
    for n in range(100):
        x=clause(1000+2*n,10000+10*n,2*n);y=clause(1001+2*n,10003+10*n,2*n+1,subject=None,head=1000+2*n)
        node=10002+10*n;x['word_ids'].append(node)
        x['WORD'].append(dict(node=node,lex='ADDRESSEE/',sp='nmpr',vt='NA',vs='NA',ps='p3',gn='m',nu='sg'))
        x['PHRASE'].append(dict(node=x['clause_id']*100+2,word_ids=[node],function='Objc',typ='NP'))
        y['CLAUSE']['native_annotations'][0].update(status='DATABASE_EXISTING_RELATION',rela='NA')
        many += [x,y]
    mi=index(many);mb=CompositeBinding(mi);formula_positives=0;formula_comparisons=0
    for n in range(100):
        for m in range(n+1,100):
            r=mb.evaluate(str(1000+2*n),str(1000+2*m),licensed)
            formula_positives+=bool(r['qualified_paths']);formula_comparisons+=1
    png=copy.deepcopy(data)
    for row in png:
        for w in row['WORD']:
            if w['sp']=='nmpr':w.update(sp='prps',lex='HE')
    pi=index(png);pc=compare(pi,full_span(pi,1),full_span(pi,11))
    m=AssignmentModel([edge('m','mother',target='t'),edge('p','peer',target='t',relation='PARATACTIC')])
    closure=clause(90,999,6,subject=None,head=1);closure['WORD'][0]['lex']='END[';closure['chapter']=31;closure['verse']=40
    closure['CLAUSE']['native_annotations'][0].update(status='DATABASE_EXISTING_RELATION',rela='NA')
    ci=index(data+[closure])
    checks=dict(S1=i.spans[a]['clause_ids']==['1','2','3'] and i.spans[a]['construction_independence_status'] in INDEPENDENT,
        S2=c['positive_source_binding'] and bool(qualified['qualified_paths']),S3=formula_comparisons==4950 and formula_positives==0,
        S4=blocked['status']=='BLOCKED_NONINDEPENDENT_SPAN' and not blocked['qualified_paths'],
        S5=cross['correspondence_kind']=='CROSS_FAMILY_CONFIGURATION_CORRESPONDENCE' and cross['family_A']!=cross['family_B'] and not cross['families_merged'],
        S6=not binder.evaluate('1','11',[])['qualified_paths'] and binder.evaluate('1','11',[])['status']=='BLOCKED_NO_EXISTING_RELATION_GRAMMAR',
        S7=any(p['lexeme']=='NAME/' and p['identity_basis']=='EXPLICIT_LEXICAL_FORM_NOT_COREFERENCE' for p in c['participant_role_mapping']),
        S8=not any(p['lexeme']=='HE' for p in pc['participant_role_mapping']) and pc['reference_identity']=='UNRESOLVED',
        S9=m.assignment('t',['m','p'])['coherent'] and not m.analyze()['pivots'][0]['human_review_required'],
        S10=not AssignmentModel([edge('a','p1',relation='PARATACTIC'),edge('b','p2',relation='PARATACTIC')]).analyze()['pivots'][0]['human_review_required'],
        S11=any(s['clause_ids']==['1','2'] for s in i.spans.values()) and bool(i.spans[a]['overlapping_span_ids']),
        S12=all('90' not in s['clause_ids'] for s in ci.spans.values()))
    return checks,i,c,cross,dict(comparisons=formula_comparisons,positive=formula_positives)


def self_test(out):
    from milal_q14_pipeline import observations
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    checks,i,c,cross,formula=semantic_checks()
    for name in ('a','b'):
        p=out/name;p.mkdir();observations(i,p);table(p/'comparisons.csv',[c,cross]);write(p/'formula.json',formula);manifest(p)
    checks['DETERMINISTIC']=digest(out/'a/99_manifest_sha256.csv')==digest(out/'b/99_manifest_sha256.csv') and verify_manifest(out/'a')
    receipt=dict(mode='SYNTHETIC',passed=all(checks.values()),checks=checks,code_fingerprint=code_fingerprint())
    write(out/'receipt.json',receipt)
    (out/'review.md').write_text('# Composite synthetic validation\n\nIndependent three-component constructions retain overlapping two-component spans. '
        'Exact and cross-family position mappings preserve distinct families. Non-generic native/lexical chains qualify existing licensed relations. '
        'The 100 bare speech formulas yield 4,950 comparisons and zero positive relations. PNG never supplies explicit identity; a remote closure does not set the onset span.\n',encoding='utf8')
    if not receipt['passed']:raise ValueError('synthetic failures '+repr([k for k,v in checks.items() if not v]))
    return receipt
