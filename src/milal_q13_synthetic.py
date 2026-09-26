"""Small portable frozen-output fixtures; no corpus data or control identities."""
import json
from pathlib import Path
from milal_mfr02r_data import table,manifest,verify_manifest,digest
from milal_mfr02r_pipeline import code_fingerprint
from milal_q13_pipeline import blind,postfreeze,write
from milal_q13_validation import edge,semantic_checks


def fixture(source):
    source.mkdir(parents=True,exist_ok=False)
    outcomes=[edge('m','mother'),edge('p','peer',relation='PARATACTIC'),edge('p2','peer2',relation='PARATACTIC'),
        edge('m1','a',target='comp'),edge('m2','b',target='comp')]
    qualified=[]
    for o in outcomes:
        oid=o['structural_outcome_group_id'];path=dict(relation=o['relation_type'],witness_id='w-'+oid,rule_id='synthetic',binding_mode='DIRECT_BINDING')
        o['provenance_paths']=[dict(path,candidate_id=oid)]
        qualified.append(dict(candidate_id=oid,source_id=o['source_or_peer'],target_id=o['target'],qualified_relations=[o['relation_type']],qualified_paths=[path]))
    table(source/'10_q12_qualified_relation_universe.csv',qualified)
    table(source/'11_q12_structural_outcome_groups.csv',outcomes)
    table(source/'01_q12_configuration_profiles.csv',[dict(clause_id=n) for n in sorted({n for o in outcomes for n in (o['source_or_peer'],o['target'])})])
    table(source/'09_q12_sb12_global_constraints.csv',[dict(mechanism='SB12',constraint_result=dict(
        input_outcome_ids=[o['structural_outcome_group_id'] for o in outcomes],output_outcome_ids=[o['structural_outcome_group_id'] for o in outcomes],positive_binding=False,conflicts=[]))])
    table(source/'12_q12_variant_pivots.csv',[dict(target_id=n,status='VARIANT_DECISION_PIVOT',outcome_count=sum(o['target']==n for o in outcomes)) for n in ('t','comp')])
    table(source/'preserved_human_judgments.csv',[dict(review_status='UNREVIEWED',reviewer_notes='')])
    table(source/'raw_qualification_crosswalk.csv',[dict(candidate_id=o['structural_outcome_group_id']) for o in outcomes])
    for f in ('06_q12_reference_witnesses.csv','07_q12_reference_candidate_antecedents.csv','08_q12_sb02_sb03_sb10_qualification.csv','configuration_units.csv'):
        table(source/f,[dict(source_id='synthetic',identity_status='UNRESOLVED')])
    manifest(source)
    return dict(previous_pivot_targets=['t','comp'],diagnostics={'mother_parallel':dict(target='t',mother='mother',peer='peer'),
        'multiple_peers':dict(target='t',peers=['peer','peer2'])},expected_input=dict(raw=5,qualified=5,outcomes=5,previous_pivots=2,human=1))


def self_test(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);source=out/'input';config=fixture(source)
    checks=semantic_checks();fingerprint=code_fingerprint()
    for name in ('a','b'):
        dest=out/name;dest.mkdir();model,result,counts=blind(source,dest)
        reaudit,diagnostics,preserved=postfreeze(source,dest,model,result,counts,config)
        manifest(dest)
    checks['PIPELINE']=counts['qualified']==counts['outcomes']==5 and counts['true_pivots']==1 and all(d['representable'] for d in diagnostics)
    checks['PRESERVATION']=all(r['source_sha256']==r['output_sha256'] for r in preserved.values()) and verify_manifest(source)
    checks['DETERMINISTIC']=digest(out/'a/99_manifest_sha256.csv')==digest(out/'b/99_manifest_sha256.csv') and verify_manifest(out/'a') and verify_manifest(out/'b')
    receipt=dict(mode='SYNTHETIC',checks=checks,passed=all(checks.values()),code_fingerprint=fingerprint)
    write(out/'receipt.json',receipt)
    if not receipt['passed']:raise ValueError('synthetic failures '+repr([k for k,v in checks.items() if not v]))
    return receipt
