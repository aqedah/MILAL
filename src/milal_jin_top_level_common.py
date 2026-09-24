"""Raw-only utilities and process isolation for independent top-level audits."""
from __future__ import annotations
import argparse
from collections import defaultdict
import json
import os
from pathlib import Path
import sys
import milal_jin_io as io
import milal_jin_relation_rules as rr
from milal_jin_blind_linguistic_audit import neutral

BASE_SAFE={'milal_jin_io','milal_jin_relation_rules','milal_jin_blind_linguistic_audit','milal_jin_top_level_common'}
FORBIDDEN_VALUES=('H:HSA','CHILD_OF','SAME_LEVEL_SIBLING','OPENING_NARRATIVE_COMPLEX','JOB_FRIENDS_DISPUTE_COMPLEX','ELIHU_SPEECH_SEQUENCE','YHWH_JOB_RESPONSE_SEQUENCE','FINAL_NARRATIVE_COMPLEX','JOB_BOOK')
CONFIGURATIONS={
 'S':['S_CONFIG_ONE_UNIQUE_ROOT_CANDIDATE','S_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_CANDIDATES','S_CONFIG_ONE_ROOT_PLUS_TOP_LEVEL_PARATAXIS','S_CONFIG_OTHER_EXPLICIT','S_CONFIG_INSUFFICIENT'],
 'M':['M_CONFIG_ONE_UNIQUE_ROOT_CANDIDATE','M_CONFIG_MULTIPLE_TOP_LEVEL_PARATACTIC_UNITS','M_CONFIG_ONE_ROOT_PLUS_TOP_LEVEL_PARATAXIS','M_CONFIG_ONE_HIGHER_MACRO_FRAME','M_CONFIG_OTHER_EXPLICIT','M_CONFIG_INSUFFICIENT']}


def walk(value):
    yield value
    if isinstance(value,dict):
        for v in value.values():yield from walk(v)
    elif isinstance(value,list):
        for v in value:yield from walk(v)


def leakage(value):
    return sum(any(t in x for t in FORBIDDEN_VALUES) for x in walk(value) if isinstance(x,str))


def guard(allowed,out,safe):
    paths={str(Path(p).resolve()).casefold():label for p,label in allowed.items()}
    base=str(Path(out).resolve()).casefold();trace=[]
    io.require(not any(n.startswith('milal_') and n not in safe for n in sys.modules),'forbidden preloaded module')
    def hook(event,args):
        if event=='import':io.require(not args[0].startswith('milal_') or args[0] in safe,'forbidden top-level import')
        if event!='open' or isinstance(args[0],int):return
        p=str(Path(os.fsdecode(args[0])).resolve()).casefold();mode=args[1];flags=args[2]
        writing=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT))
        if writing:io.require(p.startswith(base+os.sep),'write outside isolated blind output')
        else:io.require(p in paths,'read outside top-level allowlist: '+p);trace.append(paths[p])
    sys.addaudithook(hook);return trace


def formal(c):
    return dict(clause_type=c['clause_type'],verbs=[[w['lex'],w['vs'],w['vt'],w['ps'],w['gn'],w['nu']] for w in c['verbal_words']],
        constituent_order=c['constituent_order'],domain=c['domain'],participants=c['participant_surfaces'],
        temporal=[p['lexemes'] for p in c['temporal_phrases']],locative=[p['lexemes'] for p in c['locative_phrases']])


def features(raw,ling):
    neutral(raw);neutral(ling);io.require(not leakage(raw),'human labels in raw input')
    # Canonical field order makes TF-read and serialized-rerun tables byte-identical.
    raw=json.loads(io.js(raw))
    required={'clause_id','clause_atom_ids','reference','words','phrases','word_nodes','word_start','word_end','clause_type','domain','surface'}
    io.require(bool(raw) and all(required<=set(c) for c in raw),'raw clause schema')
    io.require(len({c['clause_id'] for c in raw})==len(raw),'duplicate clause identity')
    return rr.extract(sorted(raw,key=lambda c:c['word_start']),ling)


def signals(ff,rules):
    """Generic raw observations, not accepted boundaries or historical units."""
    out=[];seen_subjects=set()
    for i,c in enumerate(ff):
        prev=ff[i-1] if i else None;nxt=ff[i+1] if i+1<len(ff) else None
        verbs={w['lex'] for w in c['verbal_words']};sub=set(c['subject_lexemes'])
        entering=bool(prev and prev['domain']!=c['domain'] and c['domain'] not in rr.UNKNOWN and prev['domain'] not in rr.UNKNOWN)
        after=bool(nxt and nxt['domain']!=c['domain'] and c['domain'] not in rr.UNKNOWN and nxt['domain'] not in rr.UNKNOWN)
        flags=dict(book_scope_initial=i==0,book_scope_terminal=i==len(ff)-1,domain_transition=entering,
            domain_transition_after=after,speech_formula=bool(verbs&set(rules['speech_verbs'])),
            repeated_formula_atom=bool(c['formula_atoms']),wayhi_time=c['wayhi_temporal'],
            wayx_frame=c['clause_type']=='WayX' and bool(c['temporal_phrases'] or c['locative_phrases'] or c['explicit_subjects']),
            temporal_frame=bool(c['temporal_phrases']),locative_frame=bool(c['locative_phrases']),
            explicit_participant_introduction=bool(sub-seen_subjects),
            explicit_subject_shift=bool(prev and sub and set(prev['subject_lexemes']) and sub!=set(prev['subject_lexemes'])),
            speech_addition=rules['add_verb'] in verbs and rules['proverb_lexeme'] in c['formula_context_surface'],
            closure_lexeme=bool(verbs&set(rules['closure_lexemes'])),terminal_lexeme=bool(verbs&set(rules['terminal_lexemes'])))
        # Lexemes, not display text, determine the ordered add/proverb construction.
        flags['speech_addition']=rules['add_verb'] in verbs and any(rules['proverb_lexeme'] in n['lexemes'] for n in ff[i:i+rules['context_clause_count']])
        seen_subjects|=sub;out.append(flags)
    return out


def families(ff,ids,rules,prefix):
    """Exact repeated formal sequences with participant evidence kept separately."""
    groups=defaultdict(list);length=rules['context_clause_count']
    for i in ids:
        seq=[]
        for c in ff[i:i+length]:
            seq.append(dict(verbs=[[w['lex'],w['vs'],w['vt']] for w in c['verbal_words']],layout=c['constituent_order'],domain=c['domain']))
        if seq and any(s['verbs'] for s in seq):groups[io.js(seq)].append(i)
    return [dict(family_id=prefix+str(n).zfill(4),signature=json.loads(key),member_clause_ids=[ff[i]['clause_id'] for i in members],member_indices=members,member_refs=[ff[i]['reference'] for i in members],status='UNADJUDICATED')
        for n,(key,members) in enumerate(sorted(((k,v) for k,v in groups.items() if len(v)>1),key=lambda kv:kv[1][0]),1)]


def candidate(c,ident,kinds,flags,peers,containers,coverage):
    return dict(candidate_id=ident,reference=c['reference'],clause_id=c['clause_id'],clause_atom_ids=c['clause_atom_ids'],
        candidate_kind=kinds,opening_features=[k for k,v in flags.items() if v],formal_family=[],
        participant_features=dict(surface=c['participant_surfaces'],morphology=c['implicit_subject_morphology'],identity='UNRESOLVED'),
        domain_features=c['domain'],temporal_features=c['temporal_phrases'],locative_features=c['locative_phrases'],
        hypotaxis_candidate_count=len(containers),parataxis_candidate_count=len(peers),possible_containing_candidates=containers,possible_peer_candidates=peers,
        coverage_evidence=coverage,closure_correspondence=[],status='UNADJUDICATED',automatic_resolution=False,selected_root=False,selected_mother='',
        limitations=['NO_SUPPORTED_MOTHER_IS_NOT_ROOT','SURFACE_PARTICIPANTS_NOT_RESOLVED_IDENTITIES','COVERAGE_NOT_RANKING'])


def freeze_main(audit,builder):
    p=argparse.ArgumentParser();p.add_argument('--linguistic-rules',required=True);p.add_argument('--rules',required=True)
    g=p.add_mutually_exclusive_group(required=True);g.add_argument('--tf-data');g.add_argument('--synthetic-corpus')
    p.add_argument('--out',required=True);a=p.parse_args();out=Path(a.out)
    module='milal_jin_'+('strict' if audit=='S' else 'macro')+'_top_level_audit';safe=BASE_SAFE|{module}
    allowed={Path(a.linguistic_rules):'NEUTRAL_LINGUISTIC_RULES',Path(a.rules):'NEUTRAL_TOP_LEVEL_RULES'}
    for name in safe:allowed[Path(__file__).parent/(name+'.py')]='BLIND_CODE/'+name+'.py'
    if a.tf_data:allowed.update({Path(a.tf_data)/(n+'.tf'):'BHSA2021/'+n+'.tf' for n in io.RAW_FEATURES})
    else:allowed[Path(a.synthetic_corpus)]='SYNTHETIC_RAW_CORPUS'
    trace=guard(allowed,out,safe);ling=json.loads(Path(a.linguistic_rules).read_bytes());rules=json.loads(Path(a.rules).read_bytes());neutral(rules)
    if a.tf_data:raw,receipts=io.raw_corpus(a.tf_data,ling['bhsa_book_feature'])
    else:raw=json.loads(Path(a.synthetic_corpus).read_bytes());receipts=[]
    model=builder(raw,ling,rules);files=model['files'];files['raw_inventory.json']=io.js(raw)
    sources=[]
    for path,label in sorted(allowed.items(),key=lambda kv:kv[1]):
        data=path.read_bytes();sources.append(dict(source_id=label,sha256=io.sha(data),source_class='RAW' if label.startswith('BHSA') or label=='SYNTHETIC_RAW_CORPUS' else 'NEUTRAL_CODE_OR_RULE',
            human_source=not(label.startswith(('BHSA2021/','BLIND_CODE/','NEUTRAL_')) or label=='SYNTHETIC_RAW_CORPUS'),native_hierarchy_source=path.stem in io.NATIVE_FEATURES))
    io.require(set(trace)=={r['source_id'] for r in sources},'actual read inventory mismatch')
    names=('06_strict_blind_source_audit.csv','07_strict_blind_manifest.csv') if audit=='S' else ('15_macro_blind_source_audit.csv','16_macro_blind_manifest.csv')
    files[names[0]]=io.csv_bytes(sources)
    files['metadata.json']=io.js(dict(audit=audit,mode='REAL_BHSA_2021' if a.tf_data else 'SYNTHETIC',summary=model['summary'],source_access_policy='EXACT_FILE_AND_MODULE_ALLOWLIST',
        loaded_sources=sorted(set(trace)),human_source_count=sum(r['human_source'] for r in sources),native_hierarchy_source_count=sum(r['native_hierarchy_source'] for r in sources),
        human_label_leakage=leakage(model['model']),raw_feature_receipts=receipts,linguistic_rules=ling,rules=rules,allowed_configurations=CONFIGURATIONS[audit],status='FROZEN_BLIND_CANDIDATES'))
    io.require(not leakage(model['model']),'blind output leakage');io.seal(files,names[1]);io.require(io.manifest_ok(files,names[1]),'blind manifest')
    io.publish(files,out,False);print(json.dumps(dict(audit=audit,freeze_sha256=io.sha(files[names[1]]),summary=model['summary'])))
