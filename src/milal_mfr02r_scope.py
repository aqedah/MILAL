"""Job-only execution boundaries and explicit post-freeze source fixtures."""
import json
from pathlib import Path
from collections import defaultdict
from milal_mfr02r_data import rows, table, encode, digest


def require_job_scope(config):
    if config.get('scopes') != ['job'] or config.get('additional_raw_scopes') or config.get('primary_analysis_scope') != 'JOB':
        raise ValueError('PRIMARY_ANALYSIS_SCOPE must be JOB only')
    if config.get('corpus_comparison_scope') != 'HB_CORPUS' or config.get('control_fixture_scope') != 'EXPLICIT_REFERENCES_ONLY':
        raise ValueError('corpus search and explicit control scope must be separate')


def fixture_references(config):
    lev, num, pent = (config[k] for k in ('leviticus', 'numbers', 'pentateuch'))
    refs = {(lev['book'], *r) for r in [lev['target'], *lev['sources'], *lev['parallel_chain']]}
    refs |= {(num['book'], *r) for r in num['references']}
    refs |= {(pent['book'], *r) for r in [*pent['roots'], *pent['targets']]}
    refs |= {tuple(r) for r in [*pent['other'], *config['same_pattern']]}
    return dict(pentateuch=sorted(refs), **{k: [tuple(r) for r in config[k]] for k in ('qohelet','lamentations','isaiah')})


def read_references(tf_path, references, include_preceding_verse=False):
    """Materialize only exact verses' whole clauses and enclosed interruptions.

    Raw BHSA indexing features are read to resolve exact node membership. No
    full-book observation, valency, participant or relation inventory is built.
    """
    from milal_mfr_observation import read_feature, WORD_FEATURES, FEATURES, observe
    receipts = []
    def read(name, keep=None):
        values, receipt = read_feature(Path(tf_path)/(name+'.tf'), keep)
        receipts.append(receipt); return values
    types, slots, books = read('otype'), read('oslots'), read('book')
    chapters, verses = read('chapter'), read('verse')
    book_of = {w:b for n,b in books.items() if types.get(n)=='book' for w in slots[n]}
    chapter_of = {w:chapters[n] for n in chapters if types.get(n)=='chapter' for w in slots[n]}
    verse_of = {w:verses[n] for n in verses if types.get(n)=='verse' for w in slots[n]}
    references = {tuple(r) for r in references}
    verse_nodes = {n for n in verses if types.get(n)=='verse' and (book_of[slots[n][0]],chapter_of[slots[n][0]],verses[n]) in references}
    found = {(book_of[slots[n][0]],chapter_of[slots[n][0]],verses[n]) for n in verse_nodes}
    if found != references:
        raise ValueError('exact fixture reference missing: '+repr(references-found))
    context_nodes=set()
    if include_preceding_verse:
        by_book=defaultdict(list)
        for n in verses:
            if types.get(n)=='verse': by_book[book_of[slots[n][0]]].append(n)
        preceding={}
        for group in by_book.values():
            ordered=sorted(group,key=lambda n:min(slots[n]))
            preceding.update({b:a for a,b in zip(ordered,ordered[1:])})
        context_nodes={preceding[n] for n in verse_nodes if n in preceding}-verse_nodes
    requested_words = {w for n in verse_nodes for w in slots[n]}
    selected = {n for n,v in slots.items() if types[n]=='clause' and requested_words.intersection(v)}
    context_words={w for n in context_nodes for w in slots[n]}
    context_clauses={n for n,v in slots.items() if types[n]=='clause' and context_words.intersection(v)}-selected
    explicit=set(selected); selected |= context_clauses
    spans = [(min(slots[n]),max(slots[n])) for n in selected]
    enclosed = {n for n,v in slots.items() if types[n]=='clause' and any(a<=min(v)<=max(v)<=b for a,b in spans)}
    reasons = {n:'EXPLICIT_VERSE_COMPLETE_CLAUSE' if n in explicit else 'MINIMUM_PRECEDING_VERSE_CONTEXT' if n in context_clauses
               else 'ENCLOSED_INTERRUPTION_CONTEXT' for n in selected|enclosed}
    selected |= enclosed
    words = {w for n in selected for w in slots[n]}
    retained = {n:v for n,v in slots.items() if types[n] in ('clause','clause_atom','phrase') and words.intersection(v)}
    nodes = set(retained)|words
    ff = {f:read(f,words if f in WORD_FEATURES else nodes) for f in FEATURES if f not in ('otype','oslots','book','chapter','verse')}
    lookup = {k:defaultdict(set) for k in ('phrase','clause_atom')}
    for n,v in retained.items():
        if types[n] in lookup:
            for w in v: lookup[types[n]][w].add(n)
    raw = []
    for n in sorted(selected,key=lambda n:(min(slots[n]),n)):
        ws = slots[n]
        def objects(kind):
            ids = {p for w in ws for p in lookup[kind][w]}
            return [dict(node=p,word_ids=[w for w in slots[p] if w in ws],typ=ff['typ'].get(p),
                         **({'function':ff['function'].get(p)} if kind=='phrase' else {})) for p in sorted(ids,key=lambda p:min(slots[p]))]
        atoms = objects('clause_atom')
        raw.append(dict(book=book_of[ws[0]],chapter=chapter_of[ws[0]],verse=verse_of[ws[0]],clause_id=n,
            clause_atom_ids=[a['node'] for a in atoms],atoms=atoms,word_ids=ws,
            words=[dict(node=w,**{f:ff[f].get(w) for f in WORD_FEATURES}) for w in ws],
            phrases=objects('phrase'),clause_type=ff['typ'].get(n),domain=ff['domain'].get(n)))
    observations = observe(raw)
    return observations, dict(requested_references=sorted(references), selected_clause_ids=sorted(selected),
        minimum_context_references=sorted((book_of[slots[n][0]],chapter_of[slots[n][0]],verses[n]) for n in context_nodes),
        context_policy='ONE_PRECEDING_VERSE_WITHIN_BOOK' if include_preceding_verse else 'COMPLETE_CLAUSES_ONLY',
        selection_reasons=reasons, feature_receipts=receipts, full_book_inventory_created=False)


def evaluate_fixture(observations, registry, native):
    """Ephemeral local evaluation; never a primary engine run or book inventory."""
    from milal_mfr02r_features import build_features, preceding_sets, pair_facts
    from milal_mfr02r_grammar import match_rules
    from milal_mfr02r_valency import construction, internal_bindings
    from milal_mfr02r_graph import analyze_graph
    features = build_features(observations, registry, native)
    by_id = {f['clause_id']:f for f in features}
    constructions = [construction(r) for r in observations]
    bindings = list(internal_bindings(observations, constructions))
    candidates = []
    for target, admitted in preceding_sets(features):
        for sid in admitted:
            source=by_id[sid]; facts=pair_facts(source,target)
            matches=match_rules(source,target,facts,registry)
            candidates.append(dict(pair_id='P%s-%s'%(sid,target['clause_id']),source_clause_id=sid,
                target_clause_id=target['clause_id'],relations=sorted({m['relation'] for m in matches}),
                rule_ids=[m['rule_id'] for m in matches],facts={k:bool(v) for k,v in facts.items()},
                context_status='EXPLICIT_FIXTURE_ONLY_NOT_FULL_PRECEDING_UNIVERSE',accepted_mother=''))
    inventory = [dict(clause_id=f['clause_id'],book=f['row']['book'],chapter=f['row']['chapter'],
                      verse=f['row']['verse'],position=f['position']) for f in features]
    edges=[dict(edge_id=r['pair_id']+'-'+relation,source=r['source_clause_id'],target=r['target_clause_id'],relation=relation)
           for r in candidates for relation in r['relations']]
    graph=analyze_graph(edges,{f['clause_id']:f['position'] for f in features})
    return dict(inventory=inventory,candidates=candidates,bindings=bindings,features=features,fixture_graph=graph)


def scope_facts(out, control, corpus_receipt):
    out=Path(out); blind=out/'blind'
    scopes={p.name for p in blind.iterdir() if p.is_dir()} if blind.exists() else set()
    primary=list(rows(blind/'job/02_clause_feature_inventory.csv')) if 'job' in scopes else []
    fixture=control.get('fixture_scope_receipts',{})
    valid_fixture=bool(fixture) and all(r.get('full_book_inventory_created') is False and r.get('requested_references') and
        set(map(str,r.get('selected_clause_ids',[])))==set(map(str,r.get('selection_reasons',{}))) and
        all(v in ('EXPLICIT_VERSE_COMPLETE_CLAUSE','MINIMUM_PRECEDING_VERSE_CONTEXT','ENCLOSED_INTERRUPTION_CONTEXT') for v in r['selection_reasons'].values()) for r in fixture.values())
    forbidden={'construction_inventory.csv','valency_signatures.csv','15_variant_components.csv','07_preceding_candidate_sets.csv'}
    nonjob=any(p.name.removesuffix('.gz') in forbidden and not p.is_relative_to(blind/'job') for p in out.rglob('*') if p.is_file())
    search_index=out/'corpus_search/hb_comparison_index.json'
    return dict(PRIMARY_ANALYSIS_SCOPE_JOB_ONLY=scopes=={'job'} and bool(primary) and all(r['book']=='Iob' for r in primary),
        PENTATEUCH_FULL_ANALYSIS_ABSENT=scopes=={'job'} and not nonjob,
        PENTATEUCH_CONTROLS_FIXTURE_ONLY=valid_fixture and 'pentateuch' in fixture and control.get('control_fixture_scope')=='EXPLICIT_REFERENCES_ONLY',
        CORPUS_SEARCH_NOT_CONFUSED_WITH_ANALYSIS_SCOPE=corpus_receipt.get('analysis_scope')=='JOB' and
            corpus_receipt.get('corpus_comparison_scope')=='HB_CORPUS' and corpus_receipt.get('hierarchy_generated') is False and
            corpus_receipt.get('unique_clauses',0)>0 and scopes=={'job'} and search_index.is_file() and
            digest(search_index)==corpus_receipt.get('comparison_index_sha256'))
