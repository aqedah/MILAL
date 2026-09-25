"""Post-freeze inspection of exact frozen control identities; no book expansion."""
from pathlib import Path
import json
from milal_mfr02r_data import rows, table, digest
from milal_mfr02r_scope import read_references
from milal_mfr_observation import read_feature
from milal_mfr02r_features import build_features, evidence_values
from milal_q1_binding import SourceIndex, qualify
from milal_q1_pipeline import write_json


def controls(source, out, tf_path, grammar):
    source,out,tf_path=map(Path,(source,out,tf_path))
    freeze=json.loads((out/'blind_freeze.json').read_text())
    if any(digest(out/k)!=v for k,v in freeze['files'].items()): raise ValueError('blind result changed')
    mothers,mh=read_feature(tf_path/'mother.tf')
    relations,rh=read_feature(tf_path/'rela.tf')
    native=[dict(dependent_node=n,head_node=h,rela=relations.get(n,'NA'),
        source_feature_sha256=mh['sha256'],relation_feature_sha256=rh['sha256'],
        status='DATABASE_EXISTING_RELATION') for n,heads in mothers.items() for h in heads]
    registry={r['rule_id']:r for r in grammar['rules']}
    deferred={str(r['binding_evidence']['raw_clause_membership']) for r in rows(source/'controls/oosting_control_bindings.csv')}
    known_num_edges={(e['pair_id'],e['relation']) for r in rows(source/'controls/20_num26_variant_control.csv')
                     for e in r['actual_edges'] if r['representable'] is True}
    result=[]; receipts={}
    for scope in ('pentateuch','qohelet','lamentations','isaiah'):
        frozen=list(rows(source/'controls'/(scope+'_fixture_source_clauses.csv')))
        refs=sorted({(r['book'],int(r['chapter']),int(r['verse'])) for r in frozen})
        observations,receipt=read_references(tf_path,refs,include_preceding_verse=False)
        ids={int(r['clause_id']) for r in frozen}
        # Complete-clause reading may see an intersecting clause in the same
        # verse; qualification uses only exact original fixture clause IDs.
        observations=[r for r in observations if int(r['clause_id']) in ids]
        if {int(r['clause_id']) for r in observations}!=ids: raise ValueError('fixture source identity missing')
        features=build_features(observations,grammar,native)
        inventory=[dict(clause_id=f['clause_id'],position=f['position'],
            clause_atom_ids=f['row']['clause_atom_ids'],word_ids=f['row']['word_ids'],
            clause_type=f['clause_type'],**evidence_values(f)) for f in features]
        index=SourceIndex(inventory,grammar['lexicons']['subordinate_rela'],grammar['lexicons']['speech'])
        for raw in rows(source/'controls'/(scope+'_fixture_relation_checks.csv')):
            sid,tid=str(raw['source_clause_id']),str(raw['target_clause_id'])
            matches=[dict(rule_id=rid,relation=registry[rid]['candidate_relation']) for rid in raw['rule_ids']]
            witnesses=index.bindings(sid,tid)
            q=qualify(sid,tid,matches,witnesses,deferred=tid in deferred)
            result.append(dict(scope=scope,candidate_id=raw['pair_id'],source_id=sid,target_id=tid,
                original_relations=raw['relations'],qualified_relations=q['qualified_relations'],
                qualification=q['qualification'],witnesses=witnesses,
                exact_fixture_identity=True,full_external_book_analysis=False,
                control_result='SOURCE_BOUND_CANDIDATE_RETAINED' if q['qualified_paths'] else
                'ORIGINAL_SEARCH_RELATION_NOT_SOURCE_BOUND; KNOWN_PLAUSIBILITY_REQUIRES_REVIEW'))
        receipts[scope]=dict(original_clause_ids=sorted(ids),selected_clause_ids=sorted(index.rows,key=int),
            source_csv_sha256=digest(source/'controls'/(scope+'_fixture_source_clauses.csv')),
            read_receipt=receipt,full_external_book_analysis=False)
        print('Q1 control fixture',scope,len(ids),flush=True)
    table(out/'16_q1_control_fixture_validation.csv',result)
    write_json(out/'control_source_receipts.json',receipts)
    # The legacy Bosman unit reference explicitly leaves identity unresolved;
    # no forced UNIT_MEDIATED edge is introduced to make this control pass.
    for name in ('bosman_control_unit_references.csv','oosting_control_bindings.csv'):
        table(out/('preserved_'+name),rows(source/'controls'/name))
    qualified_edges={(r['candidate_id'],relation) for r in result for relation in r['qualified_relations']}
    known_missing=sorted(known_num_edges-qualified_edges)
    return dict(fixture_pairs=len(result),retained=sum(bool(r['qualified_relations']) for r in result),
        unresolved_known_controls=bool(known_missing),
        known_num_variant_edges=len(known_num_edges),known_num_variant_edges_missing=known_missing,
        arbitrary_or_unresolved_search_paths_removed=sum(bool(r['original_relations']) and not r['qualified_relations'] for r in result),
        scopes={s:dict(original=sum(r['scope']==s for r in result),
            qualified=sum(r['scope']==s and bool(r['qualified_relations']) for r in result)) for s in receipts},
        larger_unit_identity_unresolved=any(r.get('reference_identity_status')=='UNRESOLVED'
            for r in rows(source/'controls/bosman_control_unit_references.csv')))
