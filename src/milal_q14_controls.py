"""Post-freeze diagnostics only. Selectors never enter construction discovery."""
import json
from milal_mfr02r_data import rows,table,digest,encode
from milal_q13_pipeline import write
from milal_q14_spans import SurfaceSpans
from milal_q14_binding import CompositeBinding
from milal_q14_pipeline import observations


def fixture_inventory(source,q11,scope):
    """Q1.1 observations and MFR fixture locations join only by exact identities."""
    observations=list(rows(q11/(scope+'_source_evidence.csv')))
    locations={str(r['clause_id']):r for r in rows(source/'controls'/(scope+'_fixture_source_clauses.csv'))}
    if {str(r['clause_id']) for r in observations}!=set(locations):raise ValueError('fixture clause identity mismatch')
    result=[]
    for r in observations:
        loc=locations[str(r['clause_id'])]
        if r['word_ids']!=loc['word_ids'] or r['clause_atom_ids']!=loc['clause_atom_ids']:raise ValueError('fixture word/atom identity mismatch')
        result.append(dict(r,**{k:loc[k] for k in ('book','chapter','verse','surface_hebrew')}))
    return result


def controls(source,q11,q12,out,index,binder,config,grammar):
    freeze=json.loads((out/'blind_freeze.json').read_text(encoding='utf8'))
    if any(digest(out/k)!=v for k,v in freeze['files'].items()):raise ValueError('blind outputs changed')
    diagnostics=[];selected={}
    for chapter,verse in config['job_diagnostics']:
        ids=[k for k in index.order if (int(index.rows[k]['chapter']),int(index.rows[k]['verse']))==(chapter,verse)]
        selected[chapter,verse]=ids
        diagnostics.append(dict(reference=f'{chapter}:{verse}',clauses=[dict(clause_id=k,surface_hebrew=index.rows[k]['surface_hebrew'],profile=index.profiles[k]) for k in ids],
            spans=[dict(span=s,composite_profile=index.composites.get(s['span_id'])) for s in index.spans.values() if s['start_clause'] in ids]))
    pairs=[];deltas=list(rows(out/'10_q14_relation_qualification_delta.csv'))
    for left,right in config['diagnostic_pairs']:
        aa,bb=selected[tuple(left)],selected[tuple(right)];sa={s for k in aa for s in index.memberships[k]};sb={s for k in bb for s in index.memberships[k]}
        cs=[c for (a,b),c in binder.cache.items() if a in sa and b in sb]
        pairs.append(dict(source_reference=':'.join(map(str,left)),target_reference=':'.join(map(str,right)),
            correspondence=cs,qualification=[d for d in deltas if d['source_id'] in aa and d['target_id'] in bb]))
    write(out/'job_diagnostic_data.json',dict(locations=diagnostics,pairs=pairs))
    text=['# Job composite diagnostics after blind freeze','Surface construction extents are local and observational, not accepted textual units. The closure-target question is not evaluated.']
    for d in diagnostics:
        text+=['## '+d['reference'],'\n'.join(c['clause_id']+' — '+c['surface_hebrew'] for c in d['clauses']),
            'Observed spans: '+encode([dict(span_id=x['span']['span_id'],members=x['span']['clause_ids'],independence=x['span']['construction_independence_status']) for x in d['spans']])]
    for p in pairs:
        text+=['## '+p['source_reference']+' ↔ '+p['target_reference'],
            'Correspondence: '+encode([dict(id=c['correspondence_id'],kind=c['correspondence_kind'],mapping_resolved=c['mapping_resolved'],
                chains=[w['kind'] for w in c['pair_binding_chains']],positive=c['positive_source_binding']) for c in p['correspondence']]),
            'Existing grammar and qualifications: '+encode(p['qualification'])]
    (out/'15_q14_job_special_diagnostics.md').write_text('\n\n'.join(text)+'\n',encoding='utf8',newline='\n')
    all_fixture=fixture_inventory(source,q11,'pentateuch');byid={str(r['clause_id']):r for r in all_fixture}
    oldnums=list(rows(q12/'13_q12_numbers_postfreeze_controls.csv'))
    # Retain the existing contiguous fixture blocks around exact endpoints.
    # Chapter boundaries are neither construction boundaries nor retrieval cuts.
    wanted={n[k] for n in oldnums for k in ('source_id','target_id')};blocks=[];block=[]
    for r in sorted(all_fixture,key=lambda x:int(x['position'])):
        if block and (r['book']!=block[-1]['book'] or max(block[-1]['word_ids'])+1!=min(r['word_ids'])):
            blocks.append(block);block=[]
        block.append(r)
    if block:blocks.append(block)
    fixture=[r for block in blocks if any(str(r['clause_id']) in wanted for r in block) for r in block]
    ni=SurfaceSpans(fixture,grammar['lexicons']);nb=CompositeBinding(ni);observations(ni,out,'numbers_')
    rawpairs={r['candidate_id']:r for r in rows(q12/'pentateuch_postfreeze_pair_audit.csv')}
    registry={r['rule_id']:r for r in grammar['rules']};numbers=[]
    for pair,rel in config['numbers_controls']:
        original=rawpairs[pair];r=original['original']
        matches=[dict(rule_id=rid,relation=registry[rid]['candidate_relation']) for rid in r['rule_ids'] if registry[rid]['candidate_relation'] in r['relations']]
        result=nb.evaluate(original['source_id'],original['target_id'],matches,deferred=original['deferred'])
        status='COMPOSITE_QUALIFIED' if rel in result['qualified_relations'] else 'COMPOSITE_SUPPORT_ONLY' if result['witnesses'] else 'EVIDENCE_ONLY' if result['status']!='UNRESOLVED' else 'UNRESOLVED'
        numbers.append(dict(candidate_id=pair,relation=rel,q12_qualified=rel in original['q12']['qualified_relations'],
            q14_status=status,q14_qualified=rel in result['qualified_relations'],existing_grammar=matches,result=result,human_acceptance=''))
    table(out/'17_q14_numbers_postfreeze_controls.csv',numbers)
    table(out/'numbers_correspondence.csv',nb.cache.values(),fields=None if nb.cache else ['correspondence_id','positive_source_binding'])
    lam=fixture_inventory(source,q11,'lamentations');bi=SurfaceSpans(lam,grammar['lexicons']);observations(bi,out,'bosman_')
    bosman=[]
    for prior in rows(q12/'14_q12_bosman_postfreeze_controls.csv'):
        sid=prior['source_clause_id'];ids=bi.memberships[sid]
        bosman.append(dict(source_clause_id=sid,source_unit_candidate_id=prior['source_unit_candidate_id'],target_clause_ids=prior['target_clause_ids'],
            surface_span_ids=ids,surface_spans=[bi.spans[k] for k in ids],independent_membership_available=any(k in bi.composites for k in ids),
            reference_identity_status=prior['reference_identity_status'],frozen_reference_record=prior,new_reference_identity='',human_acceptance=''))
    table(out/'18_q14_bosman_span_diagnostics.csv',bosman)
    receipt=dict(numbers_clause_ids=ni.order,bosman_clause_ids=bi.order,full_external_analysis=False,new_raw_candidates=0,
        q12_reference_sha256=digest(q12/'14_q12_bosman_postfreeze_controls.csv'),blind_files_unchanged=all(digest(out/k)==v for k,v in freeze['files'].items()))
    write(out/'control_receipts.json',receipt)
    return diagnostics,pairs,numbers,bosman,receipt
