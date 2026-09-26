"""Post-audit selectors and source-grounded Q1.6R method notes."""
import json
from milal_mfr02r_data import digest,encode
from milal_q13_pipeline import write

METHOD='''# Q1.6R methodological contract

This is an additive methodological role layer; historical qualification remains authoritative for the frozen stage. No positive mechanism is manufactured from zero counts.

## Source grounding and adoption
Oosting, Walls of Zion and Ruins of Jerusalem, §§1.2.3–1.2.4, printed pp.39–43 (PDF pp.41–45), explains clause constitution and reconnection of interrupted atoms belonging to a single valency pattern. This supports pre-relation placement; it does not license automatic merging or semantic guessing. The existing MILAL internal_bindings function enumerates pairs inside an existing raw clause. Native ownership proves placement, not obligatory valency. The 39 candidate rows remain historically unresolved as valency claims.

Walton, Experimenting with Qohelet, §2.1.1.3, printed pp.16–18 (PDF pp.25–27), treats participant, time/place and lexical correspondence as linguistic parameters. Walton also uses semantic correspondence (§2.1.2.3, p.19). MILAL's restriction of semantic interpretation to downstream validation is the researcher's explicit methodological adaptation, not a claim that Walton prohibited semantic attachment. No distance preference, feature voting or level-zero rule is adopted.

These sources ground the distinctions; the executable ontology and typed provenance projection are GENERALIZED_FOR_MILAL. Source PDF hashes and sections are in run metadata. No hierarchy, participant identity or interpretive conclusion from the source books is imported.

## Pipeline and roles
Raw words/phrases → clause_atoms → valency constitution audit → clause/construction representation → relation candidate generation → source binding. This is a methodological dependency, not a rewrite of BHSA constitution.

Time and place are first-class structural signals. Parameter presence and configuration correspondence do not individually choose a mother or peer. Explicit forms inside Time/Loca phrases are routed to existing SB02/SB03 reference machinery. A possessive suffix in a time/place expression may refer to a participant, not to a preceding frame: phrase membership does not prove temporal/locative anaphora. Implicit subject morphology is separately marked as non-explicit.

Visibility domains may require larger surface units. Derived domains preserve native/composite/reference evidence but add no independent binding vote. Explicit native subordination is accounted for by SB01; visibility zero is classified, never repaired by invented scope.

Lexical FORM repetition is corroborative/configuration evidence. Explicit deictics and grammatical reference belong to SB02/SB03 and are not recounted as SB10. Lexical SEMANTICS is a downstream validation contract; no empirical semantic judgments are generated. SB10 therefore has explicit subtypes, rather than an obligation to generate its own positive relations.

## Refined independence
Frozen Q1.6 raw identities and full transitive closures remain byte-preserved upstream. Q1.6R adds core-observation versus context input roles. SB01 uses exact native edges; SB02/SB03 use explicit reference and antecedent observations while retaining visibility context. SB04 records explicit analytical dependence on its SB01 witness. Configuration core inputs are the recorded pair-binding anchors and native pattern evidence; unselected full-profile observations remain context. Temporal/locative views project their exact frame nodes, not every fact inherited through the complete configuration witness.

The six classes are SAME_RAW_EVIDENCE, DERIVED_FROM_SAME_RAW_EVIDENCE, SHARED_CONTEXT_ONLY, ANALYTICALLY_DEPENDENT, INDEPENDENT_RAW_EVIDENCE and UNRESOLVED_INDEPENDENCE. An analytical dependency is not raw identity. Shared context does not make distinct core observations the same raw fact. No weighting, voting or confidence total follows. Counts are unordered witness pairs within an exact candidate pair, with qualified-outcome comparisons separately identified; they are not directly comparable to the old count of fully disjoint chains. Unknown projections remain unresolved; no independence is loosened to force a count.

## Readiness scope
Readiness concerns the currently authorized formal contracts and frozen candidate universe, not exhaustive resolution of every possible linguistic reference. Zero positives in a pre-relation/context/validation process is not an unimplemented binder. A newly demonstrated distinct primary binder or a qualification-blocking bug requires a stop and separate authorization. Unresolved referential identities are not silently repaired. H0.1 never starts automatically.
'''


def diagnostics(state,out,config):
    freeze=json.loads((out/'blind_freeze.json').read_text());wanted={tuple(x) for x in config['diagnostic_verses']};inventory=state['inventory']
    selected=[r for r in inventory if (int(r['chapter']),int(r['verse'])) in wanted or all(x in {w['lex'] for w in r['WORD']} for x in config['narrative_formula_lexemes'])]
    entries=[]
    for r in selected:
        cid=str(r['clause_id']);refs=[dict(form=f,classification=state['reclassifications'][rid]) for rid,f in state['forms'].items() if f['target_clause_id']==cid]
        relevant=[p for p in state['processes'] if cid in {str(p['detail'].get('frozen_witness',{}).get('source_id','')),str(p['detail'].get('frozen_witness',{}).get('target_id','')),str(p['detail'].get('form',{}).get('target_clause_id','')),str(p['detail'].get('witness',{}).get('source_id','')),str(p['detail'].get('witness',{}).get('target_id',''))}]
        entries.append(dict(reference=str(r['chapter'])+':'+str(r['verse']),clause_id=cid,surface=r['surface_hebrew'],native_phrases=r['PHRASE'],role_evidence=[dict(process_id=p['process_id'],mechanism=p['mechanism_id'],role=p['primary_role'],kind=p['process_kind']) for p in relevant],references=refs,domains=[d for d in state['domains'].values() if cid in d['member_clauses']],qualified_relations=[o for o in state['outcomes'] if cid in (o['source_or_peer'],o['target'])],visibility_ontology=[g for g in state['gaps'] if g['target_clause']==cid]))
    write(out/'job_diagnostic_evidence.json',entries)
    lines=['# Q1.6R Job diagnostics after generic audit freeze','No hierarchy re-adjudication or antecedent recovery. Complete source records are in job_diagnostic_evidence.json.']
    for e in entries:
        lines+=['## '+e['reference']+' / '+e['clause_id'],e['surface'],'Native functions: '+', '.join(p['function'] for p in e['native_phrases']),
          'Evidence roles: '+encode(e['role_evidence']), 'References: '+encode([dict(node=x['form']['word_node'],form=x['form']['raw_form'],global_count=x['classification']['global_candidate_count'],visible=x['classification']['visible_candidate_count'],bound=x['classification']['source_bound_candidate_count']) for x in e['references']]),
          'Existing native/composite domains are context; qualified relation IDs retained: '+encode([o['structural_outcome_group_id'] for o in e['qualified_relations']]),'Visibility ontology: '+encode([g['ontology_status'] for g in e['visibility_ontology']])]
    (out/'15_q16r_job_special_diagnostics.md').write_text('\n\n'.join(lines)+'\n',encoding='utf8',newline='\n')
    (out/'16_q16r_methodological_contract.md').write_text(METHOD,encoding='utf8',newline='\n')
    (out/'17_q16r_h0_1_readiness.md').write_text('# Readiness\n\n'+state['metrics']['readiness']+'\n\nRoles classified from audited processes, not from a requirement for positive counts. Existing primary paths and Q1.3 semantics are preserved. No new mandatory distinct binding path was demonstrated by the reviewed frozen evidence. This is bounded contract readiness, not proof of complete referent resolution. H0.1 has not started.\n',encoding='utf8',newline='\n')
    unchanged=all(digest(out/n)==h for n,h in freeze['files'].items())
    if not unchanged:raise ValueError('post-audit diagnostic changed frozen audit')
    write(out/'post_audit_receipt.json',dict(blind_unchanged=unchanged,selected_references=sorted({e['reference'] for e in entries}),selected_clause_ids=[e['clause_id'] for e in entries],hierarchy_readjudicated=False))
    return unchanged
