"""Selectors only after the Job freeze; existing external fixtures only."""
import json
from milal_mfr02r_data import rows,table,digest,encode
from milal_q13_pipeline import write
from milal_q14_controls import fixture_inventory
from milal_q12_profiles import ConfigurationIndex
from milal_q12_references import ReferenceIndex
from milal_q15_domains import Domains
from milal_q15_references import Visibility


def controls(source,q11,q12,q14,out,v,config,grammar):
    freeze=json.loads((out/'blind_freeze.json').read_text())
    if not all(digest(out/n)==h for n,h in freeze['files'].items()):raise ValueError('Job blind outputs changed')
    diagnostics=[];forms={f['reference_witness_id']:f for f in v.forms}
    for ch,vs in config['job_diagnostics']:
        ids={c for c,r in v.d.rows.items() if (int(r['chapter']),int(r['verse']))==(ch,vs)}
        rr=[dict(form=forms[r['reference_witness_id']],classification=r,
            visible_antecedents=[v.d.antecedents[a] for a in r['visible_antecedent_ids']],
            bindings=[b for b in v.bindings if b['reference_witness_id']==r['reference_witness_id']],
            paths=[p for p in v.paths if p['reference_witness_id']==r['reference_witness_id']])
            for r in v.reclassified if forms[r['reference_witness_id']]['target_clause_id'] in ids]
        diagnostics.append(dict(reference=f'{ch}:{vs}',clauses=[dict(clause_id=c,surface=v.d.rows[c]['surface_hebrew']) for c in sorted(ids)],references=rr))
    write(out/'job_reference_diagnostics.json',diagnostics)
    text=['# Job reference diagnostics after blind freeze','Visibility is observational; a unique visible candidate is not confirmed identity.']
    for entry in diagnostics:
        text += ['## '+entry['reference'],encode(entry['clauses'])]
        for r in entry['references']:
            f=r['form'];c=r['classification']
            text.append(encode(dict(clause=f['target_clause_id'],node=f['word_node'],form=f['raw_form'],type=f['reference_form_type'],
                global_count=c['global_candidate_count'],visible_count=c['visible_candidate_count'],bound_count=c['source_bound_candidate_count'],
                antecedents=[dict(id=a['antecedent_id'],clause=a['clause_id'],lexeme=a['lexeme'],role=a['grammatical_role']) for a in r['visible_antecedents']],
                status=c['reference_status'],identity=c['referential_identity_status'],paths=[p['path_type'] for p in r['paths']])))
    (out/'18_q15_job_special_diagnostics.md').write_text('\n\n'.join(text)+'\n',encoding='utf8',newline='\n')
    receipts=json.loads((q14/'control_receipts.json').read_text());external={}
    for label,scope in [('bosman','lamentations'),('numbers','pentateuch')]:
        wanted=set(receipts[label+'_clause_ids']);inventory=[r for r in fixture_inventory(source,q11,scope) if str(r['clause_id']) in wanted]
        if {str(r['clause_id']) for r in inventory}!=wanted:raise ValueError('exact fixture identities missing')
        spans=list(rows(q14/(label+'_01_q14_surface_construction_spans.csv')))
        # Numbers reference search is explicitly fixture-local, not a new book search.
        old=list(rows(q12/'lamentations_postfreeze_references.csv')) if label=='bosman' else ReferenceIndex(ConfigurationIndex(inventory,grammar['lexicons'])).witnesses
        ev=Visibility(Domains(inventory,spans,grammar['lexicons']),old);candidate_records=[];ev.process(candidate_records.append)
        external[label]=ev
        table(out/(label+'_reference_classification.csv'),ev.reclassified)
        table(out/(label+'_candidate_visibility.csv'),candidate_records)
        write(out/(label+'_reference_paths.json'),dict(domains=list(ev.d.domains.values()),paths=ev.paths,antecedents=list(ev.d.antecedents.values())))
    bosman=[];bv=external['bosman']
    for old in rows(q14/'18_q14_bosman_span_diagnostics.csv'):
        sid=old['source_clause_id'];targets=set(map(str,old['target_clause_ids']))
        source_spans=[s for s in bv.d.spans.values() if s['start_clause']==sid and s['construction_independence_status'].startswith('INDEPENDENT')]
        internal={a['antecedent_id']:a for a in bv.d.antecedents.values() if any(a['clause_id'] in s['clause_ids'] for s in source_spans)}
        target_forms=[f for f in bv.forms if f['target_clause_id'] in targets];originals={r['reference_witness_id']:r for r in bv.old};access=[]
        for f in target_forms:
            for aid in sorted(set(originals[f['reference_witness_id']]['candidate_antecedent_ids'])&set(internal)):
                ant=internal[aid];paths=bv.d.paths(ant['clause_id'],f['target_clause_id'])
                access.append(dict(source_clause=sid,source_span_ids=[s['span_id'] for s in source_spans if ant['clause_id'] in s['clause_ids']],
                    internal_antecedent=ant,target_reference=f,visibility_paths=paths,reference_bearing=f['reference_bearing'],
                    status='LEXICAL_RECURRENCE_ONLY' if not f['reference_bearing'] else 'INDEPENDENT_VISIBILITY_AVAILABLE' if paths else 'NO_INDEPENDENT_TARGET_VISIBILITY',
                    identity_status='UNRESOLVED',tested_relation_used_for_domain=False))
        bindings=[b for b in bv.bindings if b['mechanism']=='SB03' and b['source_id']==sid and b['target_id'] in targets]
        refs=[r for r in bv.reclassified if any(f['reference_witness_id']==r['reference_witness_id'] and f['target_clause_id'] in targets for f in bv.forms)]
        bosman.append(dict(source_clause_id=sid,target_clause_ids=sorted(targets),independent_membership_available=old['independent_membership_available'],
            independent_source_spans=source_spans,internal_antecedents=list(internal.values()),target_reference_forms=target_forms,internal_reference_access_audit=access,
            sb03_binding_candidates=bindings,reference_classifications=refs,status='UNIQUE_VISIBLE_BUT_IDENTITY_UNRESOLVED' if any(b['source_binding_candidate'] for b in bindings) else
            'MULTIPLE_VISIBLE' if bindings else 'NO_BINDING',reference_identity_status='UNRESOLVED',human_acceptance=''))
    table(out/'20_q15_bosman_postfreeze_controls.csv',bosman)
    nv=external['numbers'];raw={r['candidate_id']:r for r in rows(q12/'pentateuch_postfreeze_pair_audit.csv')};registry={r['rule_id']:r for r in grammar['rules']};nums=[]
    for pair,rel in config['numbers_controls']:
        prior=raw[pair];r=prior['original'];matches=[dict(rule_id=rid,relation=registry[rid]['candidate_relation']) for rid in r['rule_ids'] if registry[rid]['candidate_relation'] in r['relations']]
        result=nv.evaluate(prior['source_id'],prior['target_id'],matches,prior['deferred'])
        nums.append(dict(candidate_id=pair,relation=rel,reference_qualified=rel in result['qualified_relations'],
            status='REFERENCE_QUALIFIED' if rel in result['qualified_relations'] else 'EVIDENCE_ONLY',result=result,human_acceptance=''))
    table(out/'21_q15_numbers_postfreeze_controls.csv',nums)
    receipt=dict(numbers_clause_ids=external['numbers'].d.order,bosman_clause_ids=bv.d.order,external_scope='EXPLICIT_REFERENCES_ONLY',
        full_external_analysis=False,new_raw_candidates=0,blind_files_unchanged=all(digest(out/n)==h for n,h in freeze['files'].items()))
    write(out/'control_receipts.json',receipt)
    return receipt
