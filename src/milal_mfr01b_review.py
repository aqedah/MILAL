"""Configuration-centered H1 presentation; no adjudication field is prefilled."""
from collections import defaultdict
from pathlib import Path
import json
from milal_mfr01b_data import table, write, js, ref

EXTRA_FIELDS=('configuration_validity','formal_relationship','PARATACTIC','HYPOTACTIC','EMBEDDING','RESUMPTIVE','FORMAL_ONLY','INSUFFICIENT','REQUIRES_MORE_CONTEXT','selected_relation','mother_if_hypotactic','coverage_interpretation')

def cell(v):return str(v).replace('|','\\|').replace('\n',' ')

def packet(out,d,o):
    from milal_r3c_0_2_reviewability import REVIEW_FIELDS
    out=Path(out);fields=tuple(dict.fromkeys((*REVIEW_FIELDS,*EXTRA_FIELDS)));cases={c['configuration_case_id']:c for c in o['configurations']};roles={r['marker_id']:r for r in o['roles']}
    markers_by_clause=defaultdict(list)
    for m in d['markers']:markers_by_clause[str(m['clause_id'])].append(m['marker_id'])
    evidence=defaultdict(list)
    for e in o['evidence']:evidence[e['raw_relation_id']].append(e)
    humans=[];lines=['# MFR.0.2A — Hierarchy-competing configuration review\n',
        'This packet is a human review phase, not a hierarchy. Every grouped pair remains a separate claim in its attachment. No relation, mother, coverage or participant identity is selected.\n',
        'A cessation target, its cessation-derived coverage and nested evidence share one dependency chain. Distinct display rows do not imply independent support.\n']
    for phase in o['h1']:
        c=cases[phase['configuration_case_id']];cid=c['configuration_case_id'];raw=[d['r'][rid] for rid in c['raw_pair_ids']];ev=[e for rid in c['raw_pair_ids'] for e in evidence[rid]]
        humans.append(dict(configuration_case_id=cid,underlying_raw_pair_ids=c['raw_pair_ids'],marker_ids=c['marker_ids'],bundle_ids=c['bundle_ids'],**{k:'' for k in fields}))
        attachment=dict(configuration=c,raw_relations=raw,evidence_provenance=ev,marker_roles=[roles[m] for m in c['marker_ids']],
            coverage=[d['c'][x] for x in sorted({x for r in raw for x in r['coverage_relationship']})],force=[d['h'][m] for m in c['marker_ids']],
            signatures={m:d['m'][m]['signatures'] for m in c['marker_ids']},bundles=[d['b'][b] for b in c['bundle_ids']])
        write(out/'case_evidence'/(cid+'.json'),js(attachment))
        lines += ['## '+cid+'\n','[Complete source evidence and pair crosswalk](case_evidence/'+cid+'.json)\n',
                  'Underlying raw pairs: '+', '.join(c['raw_pair_ids'])+'\n','Competing candidates: '+', '.join(c['raw_candidate_labels'])+'\n']
        for side in ('source','target'):
            positions=c[side+'_span_indices'];lines += ['### '+side.title()+' span\n','| Reference / clause | Hebrew surface | Marker / role | Participant surface | Domain | Adjuncts |','| --- | --- | --- | --- | --- | --- |']
            for i in positions:
                n=d['observation'][i];mids=markers_by_clause[str(n['clause_id'])]
                lines.append('| '+' | '.join(cell(x) for x in [ref(n)+' / '+str(n['clause_id']),n['surface_hebrew'],', '.join(m+': '+roles[m]['role'] for m in mids) or 'CONTEXT_CLAUSE',n['participant_surface_set'],n['domain'],[(p['function'],p['surface']) for p in n['phrases'] if p['function'] in ('Time','Loca')]])+' |')
            lines.append('\nContext before / after (context is not an accepted unit):\n')
            for i in list(range(max(0,min(positions)-2),min(positions)))+list(range(max(positions)+1,min(len(d['observation']),max(positions)+3))):
                n=d['observation'][i];lines.append('- '+ref(n)+' — '+n['surface_hebrew'])
        lines+=['\n### Configuration and formal correspondence\n']
        if c['sequence_witnesses']:
            for w in c['sequence_witnesses']:lines.append('- Sequence family '+w['family_id']+': '+w['source_occurrence_marker']+' ↔ '+w['target_occurrence_marker']+'; '+d['f'][w['family_id']]['signature_resolution'])
        else:lines.append('No shared repeated-sequence witness; this remains an individual pair review case.')
        lines.append('\n| Pair | Exact / construction | Context before / after | Resumption flags |\n| --- | --- | --- | --- |')
        for r in raw:lines.append('| '+' | '.join(cell(x) for x in [r['relation_candidate_id'],[r['exact_form_correspondence'],r['construction_correspondence']],[r['context_before_correspondence'],r['context_after_correspondence']],r['resumption_evidence']])+' |')
        lines.append('\nBundles (distinct construction definitions remain in the evidence attachment): '+', '.join(c['bundle_ids'])+'\n')
        lines.append('### Coverage and evidence dependency\n\n| Provenance family / facet | Dependency roots | Independent link usable |\n| --- | --- | --- |')
        seen=set()
        for e in ev:
            key=(e['provenance_family'],e['evidence_facet'],tuple(e['dependency_root_ids']),e['independent_link_usable'])
            if key in seen:continue
            seen.add(key);lines.append('| '+' | '.join(cell(x) for x in [key[0]+' '+key[1],', '.join(key[2]),key[3]])+' |')
        lines+=['\nLimitations: shared configuration groups evidence for reading; transitive grouping is not a validated textual unit. Surface participants remain unresolved. Domain equality is contextual compatibility, not a boundary judgment. All coverage endpoints remain alternatives.\n',
                '### Human fields — blank\n','| Field | Value |\n| --- | --- |']
        lines.extend('| '+field+' | |' for field in fields)
    lines+=['\n## Other phases and reference evidence\n',
        '[H1 dependencies](13_h1_hierarchy_review_set.csv), [R1 dependencies](14_r1_resumption_review_set.csv), [C1 dependencies](15_c1_closure_review_set.csv), [reference evidence](16_reference_evidence_set.csv).\n',
        'MFR.0.2B and MFR.0.2C are separate later adjudication batches. No discovery feedback or whole-book hierarchy assembly is authorized here.\n']
    table(out/'20_mfr_0_2a_review_cases.csv',humans);write(out/'21_mfr_0_2a_review_packet.md','\n'.join(lines).encode('utf8'))
    return humans,fields
