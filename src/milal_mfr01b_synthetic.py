"""Artificial input packages only; never imported for real execution."""
import json
from pathlib import Path
from copy import deepcopy
import shutil
import tempfile
import milal_mfr_common as cm

def model():
    from milal_mfr_synthetic import corpus
    from milal_mfr_selftest import model as original_model
    raw=corpus()
    for n,predicate,subject,inf in [(21,'CBT[','>JC/',False),(22,'<NH[','PN/',True),(23,'KLH[','<JN/',False),(24,'QTP[','XYZ/',False)]:
        c=deepcopy(raw[0]);c.update(book='Beta',chapter=8,verse=n,clause_id=100+n,clause_atom_ids=[200+n],domain='Q' if n==24 else 'N')
        words=[];phrases=[]
        for function,items in [('Pred',([('MN','prep')] if inf else [])+[(predicate,'verb')]),('Subj',[(subject,'subs')])]:
            ids=[]
            for lex,sp in items:
                w=deepcopy(raw[0]['words'][0]);w.update(node=3000+n*10+len(words),lex=lex,lex_utf8=lex,g_word_utf8=lex,sp=sp,pdp=sp,vt='infc' if inf and sp=='verb' else 'wayq' if sp=='verb' else 'NA');words.append(w);ids.append(w['node'])
            phrases.append(dict(node=9000+n*10+len(phrases),word_ids=ids,function=function,typ='VP' if function=='Pred' else 'NP'))
        c.update(words=words,phrases=phrases,word_ids=[w['node'] for w in words],atoms=[dict(node=200+n,word_ids=[w['node'] for w in words],typ='Way0')]);raw.append(c)
    m=original_model(raw)
    used={(r['source_marker_id'],r['target_marker_id']) for r in m['relations']}
    for s in m['markers']:
        for t in m['markers']:
            if s['marker_id']>=t['marker_id'] or (s['marker_id'],t['marker_id']) in used:continue
            if any(f['family_id'] in set(s['family_ids'])&set(t['family_ids']) and f['family_type'] in ('ADJUNCT_EXPANSION_FAMILY','MULTI_CLAUSE_CONFIGURATION_FAMILY') for f in m['families']):continue
            r=deepcopy(m['relations'][0]);r.update(relation_candidate_id='SYN_FORMAL_REFERENCE',source_marker_id=s['marker_id'],target_marker_id=t['marker_id'],source_family_ids=s['family_ids'],target_family_ids=t['family_ids'],source_anchor=s['anchor'],target_anchor=t['anchor'],source_clause_id=s['clause_id'],target_clause_id=t['clause_id'],source_book=s['book'],target_book=t['book'],cross_book=s['book']!=t['book'],coverage_relationship=[],nested_relationship=False,closure_evidence=False,resumption_evidence=dict(lexical_participant=False,temporal_context_recurrence=False,death_temporal=False,shared_context_lexemes=[]),relation_candidates=['FORMAL_CORRESPONDENCE_ONLY']);m['relations'].append(r);return m
    raise AssertionError('synthetic formal reference missing')

def dataset():
    from milal_mfr01a_data import TABLES,table,load
    from milal_mfr01a_core import build
    from milal_mfr01b_data import prepare
    m=model()
    with tempfile.TemporaryDirectory() as td:
        for k,n in TABLES.items():table(Path(td)/n,m[k])
        a=build(load(td))
    d=prepare(dict(m,old_bundles=a['bundles'],old_cases=a['cases'],old_crosswalk=a['crosswalk'],expansions=a['expansion'],old_family_review=a['family_review'],old_relation_review=a['relation_review']))
    return d,a

def package(work):
    from milal_mfr01a_data import TABLES,OUTPUTS,table
    from milal_mfr_controls import control_report
    from milal_mfr01b_io import SCOPES
    d,a=dataset();work=Path(work);raw=work/'synthetic_raw';prior=work/'synthetic_prior'
    for scope in SCOPES:
        for key,name in TABLES.items():table(raw/'blind'/scope/name,d[key])
        for key,name in OUTPUTS.items():table(prior/'consolidated'/scope/name,a[key])
    definitions={'18_pentateuch_edsf_control_report.csv':('pentateuch',[['Alpha','8:1',1],['Beta','8:14',1]]),
        '19_prophetic_superscription_control_report.csv':('prophets',[['Alpha','8:1'],['Beta','8:14']]),
        '20_death_resumption_control_report.csv':('death',[['Alpha','8:9'],['Beta','8:10']]),
        '21_daniel_ezra_control_report.csv':('daniel_ezra',[['Alpha','8:1'],['Beta','8:14']]),
        '28_job_postblind_locus_controls.csv':('job',[['Alpha','8:8'],['Beta','8:21'],['Beta','8:23']])}
    for name,(scope,targets) in definitions.items():table(raw/name,control_report(raw/'blind'/scope,scope,targets,{'1':dict(time=1,loca=1)}))
    cm.manifest(raw,'99_manifest_sha256.csv');rz=cm.deterministic_zip(raw);shutil.copyfile(rz,prior/'mfr01_frozen_input.zip')
    cm.manifest(prior,'99_manifest_sha256.csv');return cm.deterministic_zip(prior)
