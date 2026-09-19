"""Small synthetic PROV1 sources. No historical files or generator execution."""
from collections import Counter, defaultdict
import hashlib
import json

import milal_prov1_signature_provenance as m


def synthetic_source():
    # Fixture encoder intentionally independent of production reconstruction.
    def encode(value):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
    def digest(value):
        return hashlib.sha256(encode(value).encode('utf-8')).hexdigest()
    atoms = []
    features = []
    # Repeated G0 target; four-position all-level repeat; G1->G2->G3 path;
    # two atoms equal through G2 and split at G3 (S02135 control).
    for i in range(2):
        features.append(['xYq0', [['impf', 'qal', 'p2', 'm', 'sg']], [['Pred', 'VP']], [], ['BW>['], [], []])
    for cycle in range(2):
        for j in range(4):
            features.append(['Q' + str(j), [], [['Pred', 'VP']], [], ['L' + str(j)], [], []])
    for shape in ['CP', 'CP', 'NP', 'NP']:
        features.append(['WxQ0', [['perf', 'qal', 'p1', 'unknown', 'sg']], [['Conj', shape]], [], ['CQV['], [], []])
    features += [
        ['ZQtX', [['perf', 'qal', 'p3', 'unknown', 'pl']], [['Pred', 'VP'], ['Subj', 'NP']],
         [['Subj', 'NP', [['subs', '∅', 'm', 'pl'], ['nmpr', '∅', 'm', 'sg']]]], ['TMM['], ['DBR/'], [['Subj', 'NP', [['nmpr', '∅', '>JWB/']]]]],
        ['ZQtX', [['perf', 'qal', 'p3', 'unknown', 'pl']], [['Pred', 'VP'], ['Subj', 'NP']],
         [['Subj', 'NP', [['subs', '∅', 'm', 'pl']]]], ['TMM['], ['DBR/'], []],
    ]
    ah = {}
    for i, values in enumerate(features, 1):
        a = str(1000 + i)
        row = {'atom_node': a, 'atom_index_1based': str(i), 'atom_typ': values[0],
               'ref_start': 'Job 31:40' if i == 15 else 'Job 1:1', 'ref_end': 'Job 31:40' if i == 15 else 'Job 1:1'}
        row.update({k: encode(v) for k, v in zip(m.KEYS[1:], values[1:])})
        parts = [[m.KEYS[0], [values[0]]]] + [[k, v] for k, v in zip(m.KEYS[1:], values[1:])]
        ah[a] = [digest(parts[:k + 1]) for k in range(7)]
        row.update({'signature_' + l: ah[a][k] for k, l in enumerate(m.LEVELS)})
        atoms.append(row)
    order = [r['atom_node'] for r in atoms]
    windows = []
    for length in range(1, 5):
        for start in range(len(order) - length + 1):
            nodes = order[start:start + length]
            row = {'window_id': f'W{start + 1:04d}L{length:02d}', 'atom_nodes': '|'.join(nodes),
                   'start_index_1based': str(start + 1), 'sequence_length': str(length)}
            row.update({'signature_' + l: digest([l, length, [ah[a][k] for a in nodes]]) for k, l in enumerate(m.LEVELS)})
            windows.append(row)
    families, occurrences = [], []
    # Complete length-one and length-four repeated groups at every level.
    groups = {}
    for k, l in enumerate(m.LEVELS):
        for length in (1, 4):
            grouped = defaultdict(list)
            for w in windows:
                if int(w['sequence_length']) == length:
                    grouped[w['signature_' + l]].append(w)
            for h, ws in grouped.items():
                if len(ws) < 2:
                    continue
                fid = 'X' + str(len(families) + 1).zfill(6)
                start = ws[0]['start_index_1based']
                if length == 1 and start == '1' and l == 'G0': fid = 'F000019'
                if length == 4 and start == '3': fid = ['F000980','F001704','F002216','F002550','F002771','F002937','F003104'][k]
                if length == 1 and start == '11' and l in ('G1','G2','G3'): fid = {'G1':'F001301','G2':'F001968','G3':'F002481'}[l]
                if length == 1 and start == '15' and l == 'G2': fid = 'F001969'
                r = {'family_id': fid, 'level': l, 'sequence_length': str(length), 'occurrence_count': str(len(ws)),
                     'signature_hash': h, 'exemplar_window_id': ws[0]['window_id']}
                families.append(r); groups[(l, length, h)] = (fid, ws)
                occurrences += [dict(w, family_id=fid) for w in ws]
    refinements = []
    for f in families:
        k = m.LEVELS.index(f['level'])
        if k == 6: continue
        l = m.LEVELS[k + 1]; length = int(f['sequence_length'])
        ws = groups[(f['level'], length, f['signature_hash'])][1]
        children = defaultdict(list)
        for w in ws: children[w['signature_' + l]].append(w)
        for idx, (h, childws) in enumerate(sorted(children.items()), 1):
            fid = groups.get((l, length, h), ('', []))[0]
            refinements.append({'parent_family_id': f['family_id'], 'parent_level': f['level'], 'child_level': l,
                                'sequence_length': str(length), 'refinement_group_index': str(idx),
                                'child_status': 'REPEATED_FAMILY' if fid else 'SINGLETON_REFINEMENT',
                                'child_family_id': fid, 'child_signature_hash': h, 'occurrence_count': str(len(childws)),
                                'exemplar_window_id': childws[0]['window_id']})
    counts = [Counter(v[k] for v in ah.values()) for k in range(7)]
    singletons = []
    for a in atoms:
        hs = ah[a['atom_node']]
        if counts[6][hs[6]] != 1: continue
        cs = [counts[k][hs[k]] for k in range(7)]
        singletons.append(dict(a, first_unique_level=m.LEVELS[next(k for k, n in enumerate(cs) if n == 1)],
                              **{'count_' + l: str(cs[k]) for k, l in enumerate(m.LEVELS)}))
    bid_by_fid = {}
    for i, f in enumerate(families):
        bid = 'RX' + str(i)
        if f['family_id'] == 'F000019': bid = 'RB00104'
        if f['family_id'] in ['F000980','F001704','F002216','F002550','F002771','F002937','F003104']: bid = 'RB00121'
        if f['family_id'] == 'F001301': bid = 'RB00549'
        if f['family_id'] in ['F001968','F002481']: bid = 'RB00548'
        if f['family_id'] == 'F001969': bid = 'RB01716'
        bid_by_fid[f['family_id']] = bid
    members = [dict(f, bundle_id=bid_by_fid[f['family_id']]) for f in families]
    boccs = []
    seen = set()
    for o in occurrences:
        bid = bid_by_fid[o['family_id']]
        if (bid, o['window_id']) not in seen:
            boccs.append(dict(o, bundle_id=bid)); seen.add((bid, o['window_id']))
    lineages = [{'bundle_id': b, 'lineage_id': 'RL_SYNTH', 'parent_bundle_id': 'RB00549' if b == 'RB00548' else ''} for b in sorted(set(bid_by_fid.values()))]
    items = [dict(s, review_item_id='S02135' if s['atom_node'] == '1015' else 'S_SYNTH_' + s['atom_node']) for s in singletons]
    events = []
    for r in refinements:
        if r['child_family_id']: continue
        w = next(w for w in windows if w['window_id'] == r['exemplar_window_id'])
        mapped = next((it['review_item_id'] for it in items if it['atom_node'] == w['atom_nodes']), '')
        events.append(dict(r, parent_bundle_id=bid_by_fid[r['parent_family_id']], mapped_g6_singleton_review_item_id=mapped))
    slinks = [dict(it, lineage_id='RL_SYNTH', parent_family_id_at_first_unique='F001969') for it in items]
    summaries = {}
    for cid, bid in [('CASE001','RB00104'),('CASE007','RB00121'),('CASE013','RB00548')]:
        summaries[cid] = [{'unit_id':'BUNDLE:' + bid, 'bundle_id':bid, 'lineage_id':'RL_SYNTH'}]
    summaries['CASE019'] = [{'unit_id':'G6:S02135', 'review_item_id':'S02135', 'lineage_id':'RL_SYNTH'}]
    summaries['CASE025'] = summaries['CASE001'] + summaries['CASE013'] + summaries['CASE019']
    cases = []
    for cid, ss in summaries.items():
        r = dict.fromkeys(m.REVIEW_FIELDS, '')
        r.update(case_id=cid, unit_id='' if cid == 'CASE025' else ss[0]['unit_id'],
                 target_summaries=encode(ss), boundary_ref='31:40' if cid == 'CASE025' else '', review_status='UNREVIEWED')
        cases.append(r)
    tables = dict(atoms=atoms, windows=windows, families=families, occurrences=occurrences,
                  refinements=refinements, singletons=singletons, members=members, bundle_occurrences=boccs,
                  items=items, lineages=lineages, events=events, singleton_links=slinks,
                  overlay=[{'short_bundle_id':'RB00104','long_bundle_id':'RB00121','relation':'SEQUENCE_EXTENSION'}],
                  cases=cases, boundary=[{'case_id':'CASE025','unit_ids':encode([s['unit_id'] for s in summaries['CASE025']])}],
                  definitions=[{'unit_id':'G6:S02135', 'source_rows':encode([{'row':items[0], 'member':'08_singleton_review_items.csv','data_row':1}])}])
    hashes = {k: hashlib.sha256(('synthetic:' + k).encode()).hexdigest() for k in m.EXPECTED}
    locators = {k: {'archive_role':role, 'archive_sha256':hashes[role], 'member':name,
                    'member_sha256':hashlib.sha256(encode(tables[k]).encode()).hexdigest()}
                for k, (role, name, _) in m.SCHEMAS.items()}
    return {'tables':tables, 'locators':locators, 'hashes':hashes, 'expected_hashes':dict(hashes),
            'mode':'SYNTHETIC', 'source_metadata':{'fixture':'PROV1 synthetic; not historical Job results'}}
