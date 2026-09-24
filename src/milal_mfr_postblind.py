"""Historical comparison and blank human review after marker-first freezes."""
from pathlib import Path
from collections import defaultdict
import json,re,zipfile
import milal_mfr_common as cm
from milal_mfr_controls import read_table,relation_stream

METHOD='''Marker discovery precedes structural adjudication.

Book, chapter, and verse boundaries are metadata, not automatic text-hierarchy boundaries.

Scope boundaries define what was tested; they do not prove textual discontinuity.

Identical marker forms may have different hierarchical force.

Different marker forms may occupy the same textual level.

Marker family membership is evidence of correspondence, not proof of parataxis or hypotaxis.

Hierarchical force is evaluated through a bundle of formal expansion, distribution, coverage, contextual configuration, participant/domain, and closure evidence.

Coverage is evidence, not an automatic ranking rule.

Textual hierarchy is assembled only after marker-to-marker relations are human-adjudicated.

Plot and literary interpretation follow, rather than generate, the marker-based hierarchy.
'''

def ids(value):
    if not isinstance(value,list):value=[value]
    return [int(str(x).split(':')[-1]) for x in value if isinstance(x,int) or re.fullmatch(r'(?:BHSA2021:clause:)?\d+',str(x))]

def provenance_class(record):
    # Chronology must be explicit in the historical record; a current match cannot
    # retroactively prove that evidence preceded a past judgment.
    chain=record.get('marker_first_provenance',{})
    if chain.get('structure_assumed_before_marker_discovery') is True:return 'STRUCTURE_FIRST_CONTAMINATION'
    if chain.get('independent_blind_manifest_sha256') and chain.get('discovery_before_judgment') is True:
        return 'EVIDENCE_FIRST_VALID_REVIEW_PATH' if chain.get('relation_evidence_reviewed') is True else 'EVIDENCE_FIRST_BUT_NEEDS_READJUDICATION'
    return 'PROVENANCE_UNCLEAR'

def historical(directory,archive,out):
    out=Path(out);directory=Path(directory)
    with zipfile.ZipFile(archive) as z:
        cm.require(z.testzip() is None,'historical ZIP CRC');names=z.namelist();cm.require(len(names)==len(set(names)),'duplicate archive member')
        matches=[n for n in names if n.endswith('/01_hierarchy_relation_inventory.csv')];cm.require(len(matches)==1,'historical relation inventory identity');name=matches[0];data=z.read(name);records=cm.rows(data)
        # Exact entire upstream ZIP is copied as provenance; each relation embeds
        # its original record and member hash. No historical record is rewritten.
        manifest=[dict(path=n,sha256=cm.sha(z.read(n))) for n in names]
    cm.write(out/'history/upstream_member_hashes.csv',cm.csv_bytes(manifest));cm.write(out/'history/jin09_original_results.zip',Path(archive).read_bytes())
    markers=read_table(directory/'05_job_marker_candidates.csv');byclause=defaultdict(list)
    for m in markers:byclause[int(m['clause_id'])].append(m['marker_id'])
    wanted={tuple(sorted((a,b))) for r in records for a in ids(r.get('source_clause_id')) for b in ids(r.get('target_clause_id'))};pairrows=defaultdict(list)
    for r in relation_stream(directory/'11_job_marker_relation_candidates.csv'):
        k=tuple(sorted((int(r['source_clause_id']),int(r['target_clause_id']))))
        if k in wanted:pairrows[k].append(dict(relation_candidate_id=r['relation_candidate_id'],labels=r['relation_candidates'],source_clause_id=r['source_clause_id'],target_clause_id=r['target_clause_id']))
    audit=[];comparisons=[]
    for i,r in enumerate(records,1):
        source=ids(r.get('source_clause_id'));target=ids(r.get('target_clause_id'));rr=[p for a in source for b in target for p in pairrows[tuple(sorted((a,b)))]];cls=provenance_class(r)
        status='STRUCTURAL_JUDGMENT_PRECEDED_LINGUISTIC_EVIDENCE' if cls=='STRUCTURE_FIRST_CONTAMINATION' else 'MULTIPLE_RELATIONS_REMAIN' if any('COMPETING_RELATIONS' in p['labels'] for p in rr) else 'BLIND_EVIDENCE_PARTIALLY_SUPPORTS_HISTORICAL' if rr else 'HISTORICAL_RELATION_NOT_RECOVERED' if source and target else 'INSUFFICIENT'
        audit.append(dict(historical_relation_id=r['relation_id'],classification=cls,chronology_verified=cls!='PROVENANCE_UNCLEAR',next_action='REQUIRES_MARKER_FIRST_READJUDICATION' if cls!='EVIDENCE_FIRST_VALID_REVIEW_PATH' else 'REVIEW_PATH_VERIFIED',source_member=name,source_row=i,source_sha256=cm.sha(data),original_record=r,historical_state_unchanged=True,automatic_resolution=False,limitations='CURRENT_FORMAL_MATCH_DOES_NOT_PROVE_HISTORICAL_DISCOVERY_ORDER'))
        comparisons.append(dict(historical_relation_id=r['relation_id'],historical_relation_type=r.get('relation_type'),status=status,source_clause_ids=source,target_clause_ids=target,marker_ids=[m for c in source+target for m in byclause[c]],relation_candidates=rr,original_record=r,historical_state_unchanged=True,automatic_resolution=False))
    return audit,comparisons,len(manifest)

def review(directory,comparisons):
    from milal_r3c_0_2_reviewability import REVIEW_FIELDS
    d=Path(directory);families=read_table(d/'06_job_marker_family_registry.csv');markers=read_table(d/'05_job_marker_candidates.csv');mmap={m['marker_id']:m for m in markers};historical=defaultdict(list)
    for r in comparisons:
        for mid in r['marker_ids']:
            for fid in mmap[mid]['family_ids']:historical[fid].append(r['historical_relation_id'])
    fields=tuple(dict.fromkeys((*REVIEW_FIELDS,'family_validity','relation_decision','source_marker','target_marker','relation_type','coverage_decision','hierarchical_force_interpretation','additional_context_needed')))
    cases=[];packet=['# Marker-family review\n',METHOD,'\nEach family is correspondence evidence only. All decisions remain blank.\n']
    for f in families:
        cases.append(dict(review_case_id='REVIEW:'+f['family_id'],family_id=f['family_id'],family_type=f['family_type'],marker_ids=f['marker_ids'],**{k:'UNREVIEWED' if k=='review_status' else '' for k in fields}))
        packet.extend([f"\n## {f['family_id']} — {f['family_type']}\n",'Construction: `'+json.dumps(f['construction_definition'],ensure_ascii=False)+'`\n',f"Occurrences ({f['occurrence_count']}): "+', '.join(f['marker_ids'])+'\n',
            'Variants / adjunct configurations: '+json.dumps([dict(marker_id=x,features=mmap[x]['extension_features']) for x in f['marker_ids']],ensure_ascii=False)+'\n',
            'Context / force: 08, keyed by these marker IDs. Coverage: 09; nested intervals: 10; all relation candidates and competing evidence: 11. These complete tables are included in this package; no summary replaces them.\n',
            'Historical comparison (post-blind only): '+', '.join(sorted(set(historical[f['family_id']])))+'\n','UNREVIEWED — family validity / relation / coverage / hierarchical-force interpretation: __________________\n'])
    return cases,'\n'.join(packet).encode('utf8')

def early_marker_judgments(directory,archive):
    markers=read_table(Path(directory)/'05_job_marker_candidates.csv');result=[];seen=set()
    with zipfile.ZipFile(archive) as z:
        for name in sorted(z.namelist()):
            if not name.endswith(('/14_frozen_hsa1_human_judgments.csv','/01_hsa2_structural_judgments.csv')):continue
            data=z.read(name);digest=cm.sha(data)
            if digest in seen:continue
            seen.add(digest)
            for i,r in enumerate(cm.rows(data),1):
                anchor=r.get('primary_anchor_atom_if_known','');atoms=ids(anchor)
                evidence=r.get('source_evidence_ids',[])
                if isinstance(evidence,str):
                    try:evidence=json.loads(evidence)
                    except ValueError:evidence=[evidence]
                clauses=[int(x.rsplit(':',1)[1]) for x in evidence if re.fullmatch(r'BHSA2021:clause:\d+',x)]
                mm=[m for m in markers if set(m['clause_atom_ids'])&set(atoms) or int(m['clause_id']) in clauses]
                result.append(dict(historical_judgment_id=r['judgment_id'],source_member=name,source_row=i,source_sha256=digest,exact_atom_ids=atoms,exact_clause_ids=clauses,marker_ids=[m['marker_id'] for m in mm],status='BLIND_EVIDENCE_PARTIALLY_SUPPORTS_HISTORICAL' if mm else 'INSUFFICIENT',original_record=r,historical_state_unchanged=True,automatic_resolution=False,limitations='EXPLICIT_ATOM_OR_CLAUSE_ID_ONLY; FORMAL_MARKER_NOT_HUMAN_FUNCTION_CONFIRMATION'))
    return result
