"""Known-reference lookup, imported only after five physical blind freezes."""
from collections import defaultdict
import csv,json
from pathlib import Path
import milal_mfr_common as cm

def read_table(path):return cm.rows(Path(path).read_bytes())

def relation_stream(path):
    csv.field_size_limit(128*1024*1024)
    with Path(path).open(encoding='utf8',newline='') as f:
        for r in csv.DictReader(f):
            for k in ('relation_candidates','resumption_evidence','source_family_ids','target_family_ids','competing_evidence'):
                if k in r:r[k]=json.loads(r[k])
            yield r

def control_report(directory,kind,targets,patterns=None):
    directory=Path(directory);markers=read_table(directory/'05_job_marker_candidates.csv');obs=read_table(directory/'03_job_surface_observation_inventory.csv');byclause={str(c['clause_id']):c for c in obs};wanted={}
    for t in targets:
        book,ref=t[:2];chapter,verse=ref.split(':');wanted[(book,chapter,verse)]=[m for m in markers if m['book']==book and str(m['chapter'])==chapter and str(m['verse'])==verse]
    mid={m['marker_id'] for vv in wanted.values() for m in vv};pairs=defaultdict(list)
    for r in relation_stream(directory/'11_job_marker_relation_candidates.csv'):
        if r['source_marker_id'] in mid and r['target_marker_id'] in mid:
            for k in (r['source_marker_id'],r['target_marker_id']):pairs[k].append(dict(relation_candidate_id=r['relation_candidate_id'],source_marker_id=r['source_marker_id'],target_marker_id=r['target_marker_id'],cross_book=r['cross_book']=='true',labels=r['relation_candidates'],competing_evidence=r['competing_evidence']))
    result=[]
    for target in targets:
        book,ref=target[:2];ch,ve=ref.split(':');mm=wanted[(book,ch,ve)];evidence=[]
        for m in mm:
            context=[byclause[str(x)] for x in m['construction_context_clause_ids']]
            evidence.append(dict(marker_id=m['marker_id'],clause_atom_ids=m['clause_atom_ids'],tags=m['discovery_sources'],family_ids=m['family_ids'],construction_clause_ids=m['construction_context_clause_ids'],surface=[c['surface_hebrew'] for c in context],time_phrases=[p for c in context for p in c['temporal_phrase_structure']],loca_phrases=[p for c in context for p in c['locative_phrase_structure']],raw_domain=[c['domain'] for c in context]))
        casepairs={p['relation_candidate_id']:p for m in mm for p in pairs[m['marker_id']]};pattern=target[2] if len(target)>2 else None
        status='RECOVERED_PARTIAL_CORRESPONDENCE' if mm else 'NOT_RECOVERED';expected=patterns.get(str(pattern)) if patterns and pattern else None
        if kind=='pentateuch':
            dsf=[e for e in evidence if 'DIVINE_SPEECH_ADDRESSEE_CONSTRUCTION' in e['tags']]
            exact=any(len(e['time_phrases'])==expected['time'] and len(e['loca_phrases'])==expected['loca'] for e in dsf)
            status='CONSISTENT_WITH_JIN_FORMAL_FAMILY' if exact else 'PARTIALLY_CONSISTENT' if dsf else 'NOT_RECOVERED'
        elif any('FORMAL_PARALLEL_CANDIDATE' in p['labels'] and p['cross_book'] for p in casepairs.values()):status='RECOVERED_STRONG_FORMAL_CORRESPONDENCE'
        result.append(dict(control_corpus=kind,book=book,reference=ref,status=status,marker_ids=[m['marker_id'] for m in mm],raw_evidence=evidence,relation_evidence=list(casepairs.values()),jin_pattern_postblind=pattern,expected_adjunct_pattern=expected,known_ref_loaded_after_freeze=True,automatic_resolution=False,limitations='POSTBLIND_FORMAL_COMPARISON_ONLY; ADJUNCT_PHRASE_COUNTS_NOT_HIERARCHY; NONRECOVERY_PRESERVED'))
    return result
